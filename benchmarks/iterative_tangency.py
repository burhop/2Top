"""Complete numerical intersection costs and exact solver-trace evidence."""

import argparse
import hashlib
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
    from geometry import ImplicitCurve, ProceduralCurve, TrimmedImplicitCurve
    import geometry.curve_intersections as module

    x, y = sp.symbols("x y")

    def curve(expression):
        return ImplicitCurve(expression, (x, y))

    cases = [
        ("parabola_origin", curve(y - x * x), curve(y), 2.0, 100, [(0.0, 0.0)]),
        (
            "parabola_translated",
            curve(y - 1 - (x - 1) ** 2),
            curve(y - 1),
            3.0,
            64,
            [(1.0, 1.0)],
        ),
        (
            "procedural_parabola",
            ProceduralCurve(lambda x, y: y - x * x),
            curve(y),
            2.0,
            50,
            [(0.0, 0.0)],
        ),
        (
            "quartic_contact",
            curve(y - x**4),
            curve(y),
            2.0,
            50,
            [(0.0, 0.0)],
        ),
        (
            "near_two_crossings",
            curve(y - x * x),
            curve(y - sp.Rational(1, 1000)),
            2.0,
            64,
            [
                (-float(sp.sqrt(sp.Rational(1, 1000))), 0.001),
                (float(sp.sqrt(sp.Rational(1, 1000))), 0.001),
            ],
        ),
        (
            "near_disjoint",
            curve(y - x * x),
            curve(y + sp.Rational(1, 1000)),
            2.0,
            64,
            [],
        ),
        (
            "trimmed_contact",
            curve(y - (x - sp.Rational(1, 2)) ** 2),
            TrimmedImplicitCurve(
                curve(y),
                lambda x, y: 0 <= x <= 1,
                xmin=0.0,
                xmax=1.0,
                ymin=0.0,
                ymax=0.0,
                endpoints=[(0.0, 0.0), (1.0, 0.0)],
            ),
            2.0,
            64,
            [(0.5, 0.0)],
        ),
        (
            "recognized_circle_contact",
            curve(x * x + y * y - 1000000),
            curve(y - 1000),
            3000.0,
            64,
            [(0.0, 1000.0)],
        ),
        (
            "coincident_parabolas",
            curve(y - x * x),
            curve(y - x * x),
            2.0,
            64,
            [],
        ),
    ]
    original = module.fsolve
    tracing = False
    trace = None
    solves = []

    def counted(function, start, **kwargs):
        def system(point):
            value = function(point)
            if tracing:
                trace.update(np.asarray(point, dtype="<f8").tobytes())
                trace.update(np.asarray(value, dtype="<f8").tobytes())
            return value

        result = original(system if tracing else function, start, **kwargs)
        if tracing:
            solution, info, status, message = result
            solves.append(
                dict(
                    start=np.asarray(start).tolist(),
                    solution=solution.tolist(),
                    nfev=info["nfev"],
                    status=status,
                    message=message,
                )
            )
        return result

    module.fsolve = counted
    rows = []
    try:
        for name, a, b, search, resolution, reference in cases:

            def run():
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
                begin = time.perf_counter_ns()
                run()
                samples.append((time.perf_counter_ns() - begin) / 1e6)
            trace, solves = hashlib.sha256(), []
            tracing = True
            points = run()
            tracing = False
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
                    solver_starts=len(solves),
                    solver_system_calls=sum(row["nfev"] for row in solves),
                    solver_trace_sha256=trace.hexdigest(),
                    solves=solves,
                )
            )
    finally:
        module.fsolve = original
    data = dict(
        label=args.label,
        python=platform.python_version(),
        numpy=np.__version__,
        platform=platform.platform(),
        geometry_import=module.__file__,
        workloads=rows,
        limits="Five warm unprofiled complete calls, followed by a separate trace validation call. Trace hashes cover ordered fsolve input coordinates and returned field pairs; per-start status, nfev, solutions and seeds are also recorded. No start reduction, changed budgets, relaxed residuals or accuracy/completeness guarantee. Timing varies on a shared workstation.",
    )
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps({key: value for key, value in row.items() if key != "solves"}))


if __name__ == "__main__":
    main()
