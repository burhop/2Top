"""Bounded complete sampled-circle queries and robust-distance edge workloads."""

import argparse
import gc
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import weakref

import numpy as np
import sympy as sp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from geometry import (
        AreaRegion,
        CompositeCurve,
        ConicSection,
        create_square_from_edges,
    )
    from geometry.field_strategy import SignedDistanceField
    from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

    def make_region(kind):
        outer = create_square_from_edges((0.0, 0.0), (4.0, 4.0))
        if kind == "circle":
            x, y = sp.symbols("x y")
            outer = CompositeCurve(
                [
                    TrimmedImplicitCurve(
                        ConicSection((x - 2) ** 2 + (y - 2) ** 2 - 4, (x, y)),
                        lambda x, y: True,
                    )
                ]
            )
        holes = (
            [create_square_from_edges((1.0, 1.0), (3.0, 3.0))] if kind == "hole" else []
        )
        return AreaRegion(outer, holes)

    def timing(query, batches=5):
        query()
        samples = []
        for _ in range(batches):
            start = time.perf_counter_ns()
            query()
            samples.append((time.perf_counter_ns() - start) / 1e6)
        return {"median_ms": statistics.median(samples), "batches_ms": samples}

    workloads = []
    for kind in ("rectangle", "hole", "circle"):
        for size in (97, 257):
            field = SignedDistanceField(make_region(kind))
            x, y = np.meshgrid(
                np.linspace(-1.0, 5.0, size), np.linspace(-1.0, 5.0, size)
            )
            values = field.evaluate(x, y)
            workloads.append(
                {
                    "geometry": kind,
                    "shape": [size, size],
                    "boundary_segments": len(field._boundary_segments()),
                    "evaluate": timing(lambda: field.evaluate(x, y)),
                    "gradient": timing(lambda: field.gradient(x, y), 3),
                    "scalar": timing(lambda: field.evaluate(1.0, 2.0), 3),
                    "nonfinite_results": int((~np.isfinite(values)).sum()),
                }
            )
            reference_x, reference_y = weakref.ref(x), weakref.ref(y)
            del x, y, values
            gc.collect()
            workloads[-1]["retains_query_arrays"] = (
                reference_x() is not None or reference_y() is not None
            )

    edge_cases = []
    for label, a, b, x, y in [
        (
            "overflow_64",
            (-1e308, -1e308),
            (1e308, 1e308),
            np.linspace(-1.0, 1.0, 64),
            np.ones(64),
        ),
        ("collinear_64", (0.0, 0.0), (7.0, 11.0), np.full(64, 3.5), np.full(64, 5.5)),
        (
            "near_line_64",
            (0.0, 0.0),
            (7.0, 11.0),
            np.full(64, 3.5),
            5.5 + np.linspace(1e-13, 1e-8, 64),
        ),
        (
            "endpoint_257",
            (0.0, 0.0),
            (3.0, 4.0),
            np.full(257**2, -1.0),
            np.full(257**2, -2.0),
        ),
    ]:
        field = SignedDistanceField.__new__(SignedDistanceField)
        field._boundary_segments = lambda: [(a, b)]

        def query():
            return field._compute_distance_to_boundary_vectorized(x, y)

        with np.errstate(all="ignore"):
            values = query()
            edge_cases.append(
                {
                    "workload": label,
                    **timing(query),
                    "nonfinite_results": int((~np.isfinite(values)).sum()),
                }
            )

    data = {
        "label": args.label,
        "repository": str(args.repository.resolve()),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "workloads": workloads,
        "edge_cases": edge_cases,
        "limits": "Sequential warm complete calls; five evaluate/edge batches and three gradient/scalar batches, one call each. Same 50-point curved sampling across revisions. Wall-clock measurements include source sign, boundary preparation and reduction; no source-curve accuracy or application FPS claim. Baseline edge workloads may be incorrect.",
    }
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "label": args.label,
                "output": str(args.output),
                "circle_ms": [
                    w["evaluate"]["median_ms"]
                    for w in workloads
                    if w["geometry"] == "circle"
                ],
                "retained_queries": any(w["retains_query_arrays"] for w in workloads),
            }
        )
    )


if __name__ == "__main__":
    main()
