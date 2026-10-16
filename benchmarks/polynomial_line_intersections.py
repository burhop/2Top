"""Analytic x8 comparison and five warm exact-model isolation timings."""

import argparse
from decimal import Decimal, localcontext
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
    find_polynomial_line_intersections,
)
from geometry.curve_intersections import find_curve_intersections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    x, y = sp.symbols("x y")

    def curve(expression):
        return ImplicitCurve(sp.sympify(expression), (x, y))

    first, line = curve(y - x**8), curve(y)
    begin = time.perf_counter_ns()
    legacy = find_curve_intersections(
        first, line, search_range=2, grid_resolution=50, tolerance=1e-8
    )
    legacy_ms = (time.perf_counter_ns() - begin) / 1e6
    with localcontext() as context:
        context.prec = 160
        distances = [
            str(max(abs(Decimal.from_float(a)), abs(Decimal.from_float(b))))
            for a, b in legacy
        ]
    cases = [
        ("flat_x8", first, line, 1),
        ("scaled_flat_x8", curve(-(10**100) * (y - x**8)), line, 1),
        ("near_miss", curve(x**8 + sp.Rational(1, 10**12)), line, 0),
        ("two_crossings", curve(x**8 - sp.Rational(1, 2**64)), line, 2),
        ("irrational", curve(x**2 - 2), line, 2),
        ("exact_trim", TrimmedImplicitCurve(first, lambda a, b: a >= 0), line, 1),
        ("excluded_trim", TrimmedImplicitCurve(first, lambda a, b: False), line, 0),
    ]
    rows = []
    for name, a, b, expected in cases:
        find_polynomial_line_intersections(a, b)
        samples = []
        for _ in range(5):
            begin = time.perf_counter_ns()
            report = find_polynomial_line_intersections(a, b)
            samples.append((time.perf_counter_ns() - begin) / 1e6)
        assert len(report["points"]) == expected
        rows.append(
            dict(
                workload=name,
                median_ms=statistics.median(samples),
                samples_ms=samples,
                report=report,
            )
        )
    assert rows[0]["report"]["points"] == [(0, 0)]
    assert rows[0]["report"]["roots"][0]["multiplicity"] == 8
    data = dict(
        python=platform.python_version(),
        platform=platform.platform(),
        analytic_oracle="y=0 implies x**8=0; only (0,0), multiplicity8",
        legacy=dict(
            points=legacy, elapsed_ms=legacy_ms, exact_binary_Linf_errors=distances
        ),
        workloads=rows,
        limits="Opt-in unchanged native degree<=8 polynomial plus affine line only. Rational coefficient model enclosures, not general callback certification. Timings are five warm calls on Work17, not wall-clock bounds or cross-machine guarantees. Legacy x8 comparison is one current call; no legacy behavior changed.",
    )
    args.output.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "legacy_points": len(legacy),
                "isolated_points": rows[0]["report"]["points"],
                "median_ms": rows[0]["median_ms"],
            }
        )
    )


if __name__ == "__main__":
    main()
