"""Warm complete contact/intersection calls, including non-tangent controls."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np
import sympy as sp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from geometry import ImplicitCurve, TrimmedImplicitCurve
    import geometry.curve_intersections as module

    x, y = sp.symbols("x y")

    def curve(expression):
        return ImplicitCurve(expression, (x, y))

    large = curve(x * x + y * y - 1000000)
    unit = curve(x * x + y * y - 1)
    cases = [
        ("large_circle_line", large, curve(y - 1000), 3000.0, 64, [(0.0, 1000.0)]),
        (
            "large_external_circles",
            large,
            curve((x - 2000) ** 2 + y * y - 1000000),
            3000.0,
            64,
            [(1000.0, 0.0)],
        ),
        (
            "large_oblique_circles",
            large,
            curve((x - 1200) ** 2 + (y - 1600) ** 2 - 1000000),
            3000.0,
            64,
            [(600.0, 800.0)],
        ),
        (
            "large_circle_line_default_grid",
            large,
            curve(y - 1000),
            3000.0,
            500,
            [(0.0, 1000.0)],
        ),
        (
            "scaled_unit_fields",
            curve((x * x + y * y - 1) / 10**12),
            curve((y - 1) / 10**12),
            3.0,
            64,
            [(0.0, 1.0)],
        ),
        (
            "near_crossing",
            large,
            curve(y - 999),
            3000.0,
            64,
            [(-float(sp.sqrt(1999)), 999.0), (float(sp.sqrt(1999)), 999.0)],
        ),
        ("near_disjoint", large, curve(y - 1001), 3000.0, 64, []),
        (
            "trimmed_endpoint",
            unit,
            TrimmedImplicitCurve(
                curve(y - 1),
                lambda x, y: 0 <= x <= 1,
                xmin=0.0,
                xmax=1.0,
                ymin=1.0,
                ymax=1.0,
                endpoints=[(0.0, 1.0), (1.0, 1.0)],
            ),
            3.0,
            64,
            [(0.0, 1.0)],
        ),
        (
            "thin_trim_crossing_control",
            curve(x - sp.Rational(1, 2)),
            TrimmedImplicitCurve(
                curve(y - sp.Rational(1, 4)),
                lambda x, y: 0 <= x <= 1,
                xmin=0.0,
                xmax=1.0,
                ymin=0.25,
                ymax=0.25,
                endpoints=[(0.0, 0.25), (1.0, 0.25)],
            ),
            2.0,
            100,
            [(0.5, 0.25)],
        ),
        (
            "parabola_tangent_control",
            curve(y - x * x),
            curve(y),
            2.0,
            100,
            [(0.0, 0.0)],
        ),
    ]
    previous_solver = module.fsolve
    counts = {}

    def counted_solver(function, *args, **kwargs):
        counts["solver_starts"] += 1

        def counted_system(point):
            counts["solver_system_calls"] += 1
            return function(point)

        return previous_solver(counted_system, *args, **kwargs)

    module.fsolve = counted_solver
    rows = []
    try:
        for name, a, b, search, resolution, reference in cases:

            def run():
                counts.update(solver_starts=0, solver_system_calls=0)
                return sorted(
                    module.find_curve_intersections(
                        a,
                        b,
                        search_range=search,
                        grid_resolution=resolution,
                        tolerance=1e-8,
                    )
                )

            run()
            samples = []
            for _ in range(5):
                start = time.perf_counter_ns()
                run()
                samples.append((time.perf_counter_ns() - start) / 1e6)
            points = run()
            error = (
                max(
                    (
                        min(float(np.hypot(px - rx, py - ry)) for rx, ry in reference)
                        for px, py in points
                    ),
                    default=None,
                )
                if reference
                else None
            )
            rows.append(
                dict(
                    workload=name,
                    median_ms=statistics.median(samples),
                    batches_ms=samples,
                    grid_resolution=resolution,
                    points=points,
                    analytic_reference=reference,
                    count_matches=len(points) == len(reference),
                    maximum_nearest_reference_error=error,
                    **counts,
                )
            )
    finally:
        module.fsolve = previous_solver
    data = dict(
        label=args.label,
        python=platform.python_version(),
        numpy=np.__version__,
        platform=platform.platform(),
        geometry_import=str(Path(module.__file__).resolve()),
        workloads=rows,
        limits="Five sequential warm complete calls include recognition, grid/clustering or native contact validation, final residual/trim/search checks and result creation. fsolve counters exclude identity/grid/final residual/tangent/trim work and callback internals. Native classification is exact only for supported stored coefficient models; public coordinates remain floats and callbacks stay authoritative. Timings on this shared workstation are not general speedup or FPS guarantees; non-tangent controls disclose added recognition costs.",
    )
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
