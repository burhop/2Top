"""Ten warm native half-plane controls versus the0.29opaque predicate baseline."""

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
    import numpy as np
    import sympy as sp
    import geometry
    from geometry import (
        ImplicitCurve,
        RectangleMask,
        TrimmedImplicitCurve,
        find_polynomial_line_intersections,
    )

    x, y = sp.symbols("x y")
    native = getattr(geometry, "HalfPlaneMask", None)

    def curve(expression):
        return ImplicitCurve(expression, (x, y))

    def plane(base, coefficients, closed=True):
        if native is not None:
            mask = native(*coefficients, closed=closed)
        else:
            a, b, c = map(sp.Rational, coefficients)

            def mask(px, py):
                value = a * sp.Rational(float(px)) + b * sp.Rational(float(py)) + c
                return bool(value >= 0 if closed else value > 0)

        return TrimmedImplicitCurve(base, mask)

    line = curve(y - x)
    root_curve = curve((x * x - 2) ** 4)
    cases = [
        ("oblique_irrational_contact", plane(root_curve, (1, 1, 0)), line, 1),
        ("closed_flat_boundary", plane(curve(x**8), (1, 0, 0)), curve(y), 1),
        ("open_flat_boundary", plane(curve(x**8), (1, 0, 0), False), curve(y), 0),
        (
            "negative_scaled_side",
            plane(root_curve, (-(10**100), -(10**100), 0)),
            line,
            1,
        ),
        (
            "constant_on_line_closed",
            plane(curve(x * x - 2), (1, 1, -sp.Rational(1, 3))),
            curve(y + x - sp.Rational(1, 3)),
            None,
        ),
        (
            "constant_on_line_open",
            plane(curve(x * x - 2), (1, 1, -sp.Rational(1, 3)), False),
            curve(y + x - sp.Rational(1, 3)),
            0,
        ),
        (
            "nested_rectangle",
            TrimmedImplicitCurve(
                plane(root_curve, (1, 1, 0)), RectangleMask(-2, 2, -2, 2)
            ),
            line,
            1,
        ),
        ("degenerate_all", plane(curve(x * x - 2), (0, 0, 1)), line, 2),
        (
            "opaque_callback",
            TrimmedImplicitCurve(root_curve, lambda px, py: px + py >= 0),
            line,
            0,
        ),
        (
            "anchor_factory_chord",
            TrimmedImplicitCurve.from_anchors(
                curve(x * x - 2),
                (-2, -2),
                (2, 2),
                positive_half_plane=True,
                tolerance=0,
            ),
            line,
            0,
        ),
    ]
    rows = []
    for name, a, b, expected in cases:
        find_polynomial_line_intersections(a, b)
        samples = []
        for _ in range(5):
            start = time.perf_counter_ns()
            report = find_polynomial_line_intersections(a, b)
            samples.append((time.perf_counter_ns() - start) / 1e6)
        count = (
            expected
            if native is not None
            else (1 if name == "closed_flat_boundary" else 0)
        )
        if count is not None:
            assert len(report["points"]) == count, (name, report)
        if native is not None and name == "constant_on_line_closed":
            assert all(
                r["root_trim_membership"] == "model_root_included"
                for r in report["roots"]
            )
        rows.append(
            dict(
                workload=name,
                median_ms=statistics.median(samples),
                samples_ms=samples,
                report=report,
            )
        )
    arrays = []
    if native is not None:
        mask = native(1, 1, 0)
        for name, size, boundary in [
            ("mixed_signs", 100000, False),
            ("exact_boundary", 1000, True),
        ]:
            values = np.linspace(-2, 2, size)
            other = -values if boundary else -values / 2
            samples = []
            for _ in range(5):
                start = time.perf_counter_ns()
                result = mask(values, other)
                samples.append((time.perf_counter_ns() - start) / 1e6)
            assert int(result.sum()) == (size if boundary else size // 2)
            arrays.append(
                dict(
                    workload=name,
                    coordinates=size,
                    median_ms=statistics.median(samples),
                    samples_ms=samples,
                    accepted=int(result.sum()),
                )
            )
    data = dict(
        label=args.label,
        python=platform.python_version(),
        platform=platform.platform(),
        geometry_import=geometry.__file__,
        native_half_plane=native is not None,
        workloads=rows,
        array_masks=arrays,
        limits="Five warm complete calls on shared Work17. Baseline uses exact-sign opaque callbacks for the same predicates; current uses declared native masks. This is an explicit API comparison,not automatic callback certification or a speedup claim. Boundary-heavy batches require exact fallback and can be slower. No universal latency or hard exact-arithmetic runtime bound. Actual float gates remain separate.",
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
