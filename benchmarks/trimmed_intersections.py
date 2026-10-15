"""Sequential complete intersection calls with observed grid/refinement work."""

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

    def implicit(expression):
        return ImplicitCurve(expression, (x, y))

    def horizontal(*, low=0.0, high=1.0, height=0.25, partial=False):
        return TrimmedImplicitCurve(
            implicit(y - sp.Rational(height)),
            lambda a, b: low <= a <= high,
            xmin=low,
            xmax=high,
            ymin=None if partial else height,
            ymax=None if partial else height,
            endpoints=[(low, height), (high, height)],
        )

    cases = [
        ("thin_interior_100", horizontal(), implicit(x - sp.Rational(1, 2)), 100),
        ("thin_interior_500", horizontal(), implicit(x - sp.Rational(1, 2)), 500),
        ("thin_endpoint_100", horizontal(), implicit(x - 1), 100),
        (
            "thin_circle_crossings_100",
            horizontal(low=-1.5, high=1.5, height=0.75),
            implicit(x * x + y * y - sp.Rational(25, 16)),
            100,
        ),
        (
            "thin_outside_root_100",
            horizontal(),
            implicit(x - sp.Rational(101, 100)),
            100,
        ),
        (
            "partial_rectangle_100",
            horizontal(partial=True),
            implicit(x - sp.Rational(1, 2)),
            100,
        ),
        (
            "untrimmed_circle_crossings_100",
            implicit(x * x + y * y - sp.Rational(25, 16)),
            implicit(y - sp.Rational(3, 4)),
            100,
        ),
        ("untrimmed_parabola_tangent_100", implicit(y - x * x), implicit(y), 100),
    ]
    cluster, solver = module._cluster_candidates_fast, module.fsolve
    counts = {}

    def counted_cluster(points, **kwargs):
        counts["grid_candidates"] = len(points)
        return cluster(points, **kwargs)

    def counted_solver(function, *args, **kwargs):
        counts["solver_starts"] += 1

        def counted_system(point):
            counts["solver_system_calls"] += 1
            return function(point)

        return solver(counted_system, *args, **kwargs)

    module._cluster_candidates_fast = counted_cluster
    module.fsolve = counted_solver
    rows = []
    try:
        for name, a, b, resolution in cases:

            def run():
                counts.update(grid_candidates=0, solver_starts=0, solver_system_calls=0)
                try:
                    result = module.find_curve_intersections(
                        a,
                        b,
                        search_range=2.0,
                        grid_resolution=resolution,
                        tolerance=1e-8,
                    )
                    return result, None
                except (TypeError, ValueError) as error:
                    return [], f"{type(error).__name__}: {error}"

            run()
            samples = []
            for _ in range(5):
                start = time.perf_counter_ns()
                run()
                samples.append((time.perf_counter_ns() - start) / 1e6)
            result, error = run()
            rows.append(
                dict(
                    workload=name,
                    median_ms=statistics.median(samples),
                    batches_ms=samples,
                    grid_resolution=resolution,
                    points=sorted(result),
                    rejection=error,
                    **counts,
                )
            )
    finally:
        module._cluster_candidates_fast, module.fsolve = cluster, solver
    data = dict(
        label=args.label,
        python=platform.python_version(),
        numpy=np.__version__,
        platform=platform.platform(),
        geometry_import=str(Path(module.__file__).resolve()),
        workloads=rows,
        limits="Five sequential warm complete calls include grid evaluations, candidate clustering, solver refinement and final checks. Counters instrument clustering input and fsolve system calls; they exclude final residual/tangent/trim/identity evaluations and callback internals. These shared-workstation timings are not FPS or speedup guarantees. Baseline empty/error results do less useful work. No exactness/completeness/overlap certificate is claimed.",
    )
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
