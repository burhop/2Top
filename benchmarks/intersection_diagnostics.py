"""Bounded supplied-candidate diagnostic costs and legacy solver parity."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import (
    ImplicitCurve,
    TrimmedImplicitCurve,
    diagnose_intersection_candidates,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reproduction", type=Path, required=True)
    parser.add_argument("--solver-traces", type=Path, required=True)
    args = parser.parse_args()
    x, y = sp.symbols("x y")

    def curve(expression):
        return ImplicitCurve(expression, (x, y))

    points = [
        row["point"]
        for row in json.loads(args.reproduction.read_text(encoding="utf-8"))[
            "candidates"
        ]
    ]
    first, second = curve(y - x**8), curve(y)
    cases = [
        ("reproduced_x8_candidates", first, second, points),
        ("true_flat_origin", first, second, [(0.0, 0.0)]),
        ("transverse_offset", curve(x - 1), curve(y - 2), [(1.1, 2.2)]),
        (
            "two_flat_crossings",
            first,
            curve(y - sp.Rational(1, 25) ** 8),
            [
                (-0.04, float(sp.Rational(1, 25) ** 8)),
                (0.04, float(sp.Rational(1, 25) ** 8)),
            ],
        ),
        ("near_miss", first, curve(y + sp.Rational(1, 10**12)), [(0.0, -1e-12)]),
        (
            "trim_excluded",
            first,
            TrimmedImplicitCurve(second, lambda x, y: False),
            [(0.0, 0.0)],
        ),
        ("coincident_sample", first, first, [(0.0, 0.0)]),
    ]
    rows = []
    for name, a, b, candidates in cases:
        diagnose_intersection_candidates(a, b, candidates)
        samples = []
        for _ in range(5):
            begin = time.perf_counter_ns()
            report = diagnose_intersection_candidates(a, b, candidates)
            samples.append((time.perf_counter_ns() - begin) / 1e6)
        assert all(
            not item["position_verified"] and item["positional_error_bound"] is None
            for item in report["candidate_reports"]
        )
        rows.append(
            dict(
                workload=name,
                median_ms=statistics.median(samples),
                batches_ms=samples,
                diagnostic_scalar_evaluations=sum(
                    field["scalar_evaluations"]
                    for item in report["candidate_reports"]
                    for field in item["fields"]
                ),
                report=report,
            )
        )
    baseline = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "docs/iterative_tangency_0.26.0_work17.json"
        ).read_text(encoding="utf-8")
    )
    current = json.loads(args.solver_traces.read_text(encoding="utf-8"))
    matched = []
    for a, b in zip(baseline["workloads"], current["workloads"]):
        assert a["workload"] == b["workload"]
        for key in (
            "points",
            "solves",
            "solver_starts",
            "solver_system_calls",
            "solver_trace_sha256",
        ):
            assert a[key] == b[key], (a["workload"], key)
        matched.append(a["workload"])
    assert len(matched) == 9
    data = dict(
        python=platform.python_version(),
        platform=platform.platform(),
        workloads=rows,
        unchanged_solver_trace_workloads=matched,
        limits="Five warm complete diagnostic calls on supplied candidates, separate from root search. Ten direct scalar probes per field/candidate, plus optional contains internals. All reports remain position-unverified; timing/error estimates are not certificates. Nine complete legacy solver traces compare to recorded0.26data, not rerun baseline measurements.",
    )
    args.output.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    for row in rows:
        print(json.dumps({key: value for key, value in row.items() if key != "report"}))
    print(f"Exact legacy solver trace parity: {len(matched)} workloads")


if __name__ == "__main__":
    main()
