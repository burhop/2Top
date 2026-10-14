"""Complete native/fallback gradients and bounded singularity-heavy workloads."""

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

    def square(low=0.0, high=4.0):
        return create_square_from_edges((low, low), (high, high))

    def region(kind):
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
        else:
            outer = square()
        return AreaRegion(outer, [square(1.0, 3.0)] if kind == "hole" else [])

    def timing(query, batches=5, repeats=1):
        query()
        samples = []
        for _ in range(batches):
            start = time.perf_counter_ns()
            for _ in range(repeats):
                query()
            samples.append((time.perf_counter_ns() - start) / repeats / 1e6)
        return {"median_ms": statistics.median(samples), "batches_ms": samples}

    def diagnostics(gradient):
        gx, gy = gradient
        valid = np.isfinite(gx) & np.isfinite(gy)
        norm = np.hypot(gx, gy)
        return {
            "unavailable_pairs": int((~valid).sum()),
            "only_one_unavailable_component": int(
                (np.isfinite(gx) ^ np.isfinite(gy)).sum()
            ),
            "finite_nonunit_at_1e_8": int((valid & (np.abs(norm - 1) > 1e-8)).sum()),
        }

    workloads = []
    for kind in ("rectangle", "hole", "circle"):
        for size in (97, 257):
            field = SignedDistanceField(region(kind))
            x, y = np.meshgrid(
                np.linspace(-1.0, 5.0, size), np.linspace(-1.0, 5.0, size)
            )
            gradient = field.gradient(x, y)
            workloads.append(
                {
                    "geometry": kind,
                    "shape": [size, size],
                    "evaluate": timing(lambda: field.evaluate(x, y)),
                    "gradient": timing(lambda: field.gradient(x, y), 3),
                    "scalar_gradient": timing(lambda: field.gradient(-1.0, 2.0), 5, 10),
                    **diagnostics(gradient),
                }
            )
            references = [weakref.ref(value) for value in (x, y)]
            del x, y, gradient
            gc.collect()
            workloads[-1]["retains_queries"] = any(
                reference() is not None for reference in references
            )

    edges = []
    for kind, x, y, field in [
        (
            "exact_medial_ties_64",
            np.full(64, 2.0),
            np.full(64, 2.0),
            SignedDistanceField(AreaRegion(square())),
        ),
        (
            "near_medial_ties_64",
            np.tile([np.nextafter(2.0, -np.inf), np.nextafter(2.0, np.inf)], 32),
            np.full(64, 2.0),
            SignedDistanceField(AreaRegion(square())),
        ),
        (
            "boundary_normals_64",
            np.full(64, 2.0),
            np.zeros(64),
            SignedDistanceField(AreaRegion(square())),
        ),
        (
            "huge_smooth_64",
            np.full(64, 2e200),
            np.full(64, 1e200),
            SignedDistanceField(AreaRegion(square(0.0, 4e200))),
        ),
    ]:
        edges.append(
            {
                "workload": kind,
                **timing(lambda: field.gradient(x, y)),
                **diagnostics(field.gradient(x, y)),
            }
        )
    data = {
        "label": args.label,
        "repository": str(args.repository.resolve()),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "workloads": workloads,
        "edge_cases": edges,
        "limits": "Sequential warm full calls:five evaluation/edge batches,three grid-gradient batches,and five ten-call scalar batches. Same curved sampling/resolution; diagnostics are unit/mask counts,not derivative certificates. Baseline finite averages at singularities are misleading; exact-tie/boundary/scale guards have measurable costs. Shared-workstation wall-clock medians do not guarantee FPS or universal rounding.",
    }
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "label": args.label,
                "gradient_ms": [
                    (w["geometry"], w["shape"][0], w["gradient"]["median_ms"])
                    for w in workloads
                ],
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
