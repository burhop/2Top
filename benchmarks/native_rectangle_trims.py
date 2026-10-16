"""Compare0.28opaque boxes with0.29declarative boxes; five warm calls per case."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    import math
    import numpy as np
    import sympy as sp
    import geometry
    from geometry import (
        ImplicitCurve,
        TrimmedImplicitCurve,
        find_polynomial_line_intersections,
    )

    x, y = sp.symbols("x y")
    native = getattr(geometry, "RectangleMask", None)

    def curve(expression):
        return ImplicitCurve(expression, (x, y))

    def box(base, bounds):
        if native is not None:
            mask = native(*bounds)
        else:
            a, b, c, d = map(sp.Rational, bounds)

            def mask(px, py):
                return (
                    a <= sp.Rational(float(px)) <= b
                    and c <= sp.Rational(float(py)) <= d
                )

        return TrimmedImplicitCurve(base, mask)

    line = curve(y)
    cases = [
        ("irrational_flat_contact", box(curve((x * x - 2) ** 4), (0, 2, -1, 1)), line),
        ("nonbinary_rational", box(curve(3 * x - 1), (0, 1, -1, 1)), line),
        ("exact_closed_endpoint", box(curve(x**8), (0, 1, 0, 0)), line),
        (
            "sqrt2_threshold_excluded",
            box(curve(x * x - 2), (math.sqrt(2), 2, -1, 1)),
            line,
        ),
        (
            "nonbinary_zero_width",
            box(curve(3 * x - 1), (sp.Rational(1, 3), sp.Rational(1, 3), 0, 0)),
            line,
        ),
        (
            "oblique_irrational",
            box(curve(x * x - 2), (0, 2, -3, 0)),
            curve(y + sp.Rational(3, 2) * x),
        ),
        (
            "nested_rectangles",
            box(box(curve(x * x - 2), (0, 2, -1, 1)), (1, 2, -1, 1)),
            line,
        ),
        (
            "opaque_callback",
            TrimmedImplicitCurve(curve(x * x - 2), lambda px, py: True),
            line,
        ),
        (
            "opaque_oblique_halfplane",
            TrimmedImplicitCurve(curve(x * x - 2), lambda px, py: px + py >= 0),
            curve(y - x),
        ),
    ]
    rows = []
    for name, a, b in cases:
        find_polynomial_line_intersections(a, b)
        samples = []
        for _ in range(5):
            start = time.perf_counter_ns()
            report = find_polynomial_line_intersections(a, b)
            samples.append((time.perf_counter_ns() - start) / 1e6)
        expected = (
            1
            if name
            in (
                "irrational_flat_contact",
                "nonbinary_rational",
                "oblique_irrational",
                "nested_rectangles",
            )
            and native is not None
            else (1 if name == "exact_closed_endpoint" else 0)
        )
        assert len(report["points"]) == expected, (name, report)
        rows.append(
            dict(
                workload=name,
                median_ms=statistics.median(samples),
                samples_ms=samples,
                report=report,
            )
        )
    array_cost = None
    if native is not None:
        mask = native(0, 2, -1, 1)
        values = np.linspace(-2, 2, 100000)
        samples = []
        for _ in range(5):
            start = time.perf_counter_ns()
            result = mask(values, 0)
            samples.append((time.perf_counter_ns() - start) / 1e6)
        assert int(result.sum()) == 50000
        array_cost = dict(
            coordinates=100000, median_ms=statistics.median(samples), samples_ms=samples
        )
    data = dict(
        label=args.label,
        python=platform.python_version(),
        platform=platform.platform(),
        geometry_import=geometry.__file__,
        native_rectangle=native is not None,
        workloads=rows,
        array_mask=array_cost,
        limits="Five warm calls on Work17. Baseline0.28uses opaque callbacks for the same boxes;0.29declares exact native predicates. These measurements compare that explicit API choice,not automatic certification of arbitrary callbacks. Float residual/position/contains gates remain. No universal latency guarantee; no browser or scene changes.",
    )
    args.output.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    for row in rows:
        print(
            json.dumps(
                dict(
                    workload=row["workload"],
                    median_ms=row["median_ms"],
                    accepted_points=len(row["report"]["points"]),
                )
            )
        )


if __name__ == "__main__":
    main()
