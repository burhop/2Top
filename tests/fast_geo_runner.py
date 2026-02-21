"""Fast geometry regression harness for batched scenario execution.

This module is intentionally lightweight: it coordinates scenario generation,
execution, and basic verification while allowing parallelism in future iterations.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, List, Dict, Any

from geometry import PrecisionPolicy

from tests.factories.curve_scenarios import CurveScenario, sample_scenarios


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_scenarios(
    scenarios: Iterable[CurveScenario],
    failing_scenarios: List[Dict[str, Any]],
    max_failures: int,
) -> List[dict]:
    results = []
    for scenario in scenarios:
        start = time.perf_counter()
        descriptor = scenario.descriptor()
        descriptor["name"] = scenario.name
        try:
            if scenario.composite is not None:
                # Light-touch verification for now: evaluate representative checks
                descriptor["is_closed"] = bool(scenario.composite.is_closed())
            status = "ok"
        except Exception as exc:  # pragma: no cover (placeholder until tests land)
            status = "error"
            descriptor["error"] = str(exc)
            if len(failing_scenarios) < max_failures:
                failing_scenarios.append(descriptor.copy())
        elapsed = time.perf_counter() - start
        descriptor["status"] = status
        descriptor["elapsed_ms"] = elapsed * 1000.0
        results.append(descriptor)
    return results


def summarize_results(results: List[dict]) -> Dict[str, Any]:
    total = len(results)
    errors = sum(1 for r in results if r.get("status") != "ok")
    elapsed_ms = sum(r.get("elapsed_ms", 0.0) for r in results)
    return {
        "total": total,
        "errors": errors,
        "success": total - errors,
        "error_rate": errors / total if total else 0.0,
        "total_elapsed_ms": elapsed_ms,
    }


def write_artifacts(out_dir: Path, chunk_index: int, chunk_results: List[dict]) -> None:
    chunk_file = out_dir / f"chunk_{chunk_index:04d}.json"
    chunk_file.write_text(json.dumps(chunk_results, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fast geometry regression scenarios")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--policy-abs", type=float, default=None)
    parser.add_argument("--policy-rel", type=float, default=None)
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--max-failures", type=int, default=50)
    parser.add_argument("--output", type=Path, default=None, help="Directory for artifact output")
    args = parser.parse_args()

    policy_kwargs = {}
    if args.policy_abs is not None:
        policy_kwargs["absolute"] = args.policy_abs
    if args.policy_rel is not None:
        policy_kwargs["relative"] = args.policy_rel
    policy = PrecisionPolicy(**policy_kwargs) if policy_kwargs else PrecisionPolicy()

    output_dir = Path(args.output) if args.output else None
    if output_dir is not None:
        _ensure_dir(output_dir)

    chunk_size = max(1, args.chunk_size)
    remaining = args.count
    chunk_index = 0
    all_results: List[dict] = []
    failing_scenarios: List[Dict[str, Any]] = []

    while remaining > 0:
        batch_count = min(chunk_size, remaining)
        batch_seed = args.seed + chunk_index * 9973
        scenarios = sample_scenarios(batch_seed, batch_count, policy)
        chunk_results = run_scenarios(scenarios, failing_scenarios, args.max_failures)
        all_results.extend(chunk_results)
        if output_dir is not None:
            write_artifacts(output_dir, chunk_index, chunk_results)
        remaining -= batch_count
        chunk_index += 1

    summary = summarize_results(all_results)
    summary["chunks"] = chunk_index
    summary["timestamp"] = time.time()
    summary["max_failures"] = args.max_failures
    summary["failures_captured"] = len(failing_scenarios)
    summary_file = None

    if output_dir is not None:
        summary_file = output_dir / "summary.json"
        summary_file.write_text(json.dumps({
            "summary": summary,
            "failing_scenarios": failing_scenarios,
        }, indent=2))
        print(f"Summary written to {summary_file}")
    else:
        print(json.dumps(summary, indent=2))
        if failing_scenarios:
            print("Sample failing scenarios:")
            print(json.dumps(failing_scenarios[:5], indent=2))


if __name__ == "__main__":
    main()
