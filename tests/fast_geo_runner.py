"""Fast geometry regression harness for batched scenario execution.

This module is intentionally lightweight: it coordinates scenario generation,
execution, and basic verification while allowing parallelism in future iterations.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, List

from geometry import PrecisionPolicy

from tests.factories.curve_scenarios import CurveScenario, sample_scenarios


def run_scenarios(scenarios: Iterable[CurveScenario]) -> List[dict]:
    results = []
    for scenario in scenarios:
        start = time.perf_counter()
        descriptor = scenario.descriptor()
        try:
            if scenario.composite is not None:
                # Light-touch verification for now: evaluate a grid point
                scenario.composite.is_closed()
            status = "ok"
        except Exception as exc:  # pragma: no cover (placeholder until tests land)
            status = "error"
            descriptor["error"] = str(exc)
        elapsed = time.perf_counter() - start
        descriptor["status"] = status
        descriptor["elapsed_ms"] = elapsed * 1000.0
        results.append(descriptor)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fast geometry regression scenarios")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--policy-abs", type=float, default=None)
    parser.add_argument("--policy-rel", type=float, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    policy_kwargs = {}
    if args.policy_abs is not None:
        policy_kwargs["absolute"] = args.policy_abs
    if args.policy_rel is not None:
        policy_kwargs["relative"] = args.policy_rel
    policy = PrecisionPolicy(**policy_kwargs) if policy_kwargs else PrecisionPolicy()

    scenarios = sample_scenarios(args.seed, args.count, policy)
    results = run_scenarios(scenarios)

    if args.output:
        args.output.write_text(json.dumps(results, indent=2))
    else:
        print(json.dumps(results[:10], indent=2))
        if len(results) > 10:
            print(f"... {len(results) - 10} more results omitted")


if __name__ == "__main__":
    main()
