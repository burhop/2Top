"""Complete opt-in diagnostics versus legacy gradient calls, never FPS claims."""

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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from geometry import (
        AreaRegion,
        CompositeCurve,
        ConicSection,
        TrimmedImplicitCurve,
        create_square_from_edges,
    )
    from geometry.field_strategy import SignedDistanceField

    def callback(function):
        field = SignedDistanceField(
            AreaRegion(create_square_from_edges((0.0, 0.0), (4.0, 4.0)))
        )
        field.evaluate = function
        return field

    x, y = sp.symbols("x y")
    circle = SignedDistanceField(
        AreaRegion(
            CompositeCurve(
                [
                    TrimmedImplicitCurve(
                        ConicSection(x * x + y * y - 1, (x, y)), lambda x, y: True
                    )
                ]
            )
        ),
        resolution=1e-6,
    )
    a, b = np.array(circle._boundary_segments()[0])
    midpoint = (a + b) / 2
    normal = midpoint / np.hypot(*midpoint)
    tangent = np.array([-normal[1], normal[0]])

    def timing(query, batches):
        query()
        samples = []
        for _ in range(batches):
            start = time.perf_counter_ns()
            query()
            samples.append((time.perf_counter_ns() - start) / 1e6)
        return dict(median_ms=statistics.median(samples), batches_ms=samples)

    grid_x, grid_y = np.meshgrid(np.linspace(-1.5, 1.5, 17), np.linspace(-1.5, 1.5, 17))
    cases = [
        ("sampled_source_boundary", circle, tuple(normal)),
        (
            "sampled_smooth_chord",
            circle,
            tuple(midpoint + 0.2 * normal + 0.02 * tangent),
        ),
        ("sampled_17x17", circle, (grid_x, grid_y)),
        (
            "tiny_circle_callback",
            callback(lambda x, y: np.hypot(x, y) - 1e-6),
            (1.6e-6, 1.2e-6),
        ),
        (
            "circle_medial_callback",
            callback(lambda x, y: np.hypot(x, y) - 1.0),
            (0.0, 0.0),
        ),
        (
            "affine_callback_64",
            callback(lambda x, y: 3 * x - 4 * y + 7),
            (np.linspace(0.1, 0.5, 64), np.linspace(0.2, 0.4, 64)),
        ),
        (
            "nonfinite_callback_64",
            callback(lambda x, y: 7.0),
            (np.full(64, np.nan), np.full(64, np.nan)),
        ),
    ]
    rows = []
    for name, field, point in cases:
        row = dict(
            workload=name, legacy_gradient=timing(lambda: field.gradient(*point), 5)
        )
        if hasattr(field, "gradient_diagnostics"):
            row["diagnostics"] = timing(lambda: field.gradient_diagnostics(*point), 3)
            result = field.gradient_diagnostics(*point)
            row["field_evaluations"] = result["field_evaluations"]
            row["available_vectors"] = int(np.count_nonzero(result["available"]))
            row["query_points"] = int(np.broadcast_arrays(*point)[0].size)
            row["status_counts"] = [
                dict(zip(*[v.tolist() for v in np.unique(status, return_counts=True)]))
                for status in result["status"]
            ]
        rows.append(row)
    px, py = np.array([0.3, 0.4]), np.array([0.2, 0.1])
    references = weakref.ref(px), weakref.ref(py)
    field = callback(lambda x, y: 3 * x - 4 * y)
    if hasattr(field, "gradient_diagnostics"):
        field.gradient_diagnostics(px, py)
    del px, py
    gc.collect()
    data = dict(
        label=args.label,
        python=platform.python_version(),
        numpy=np.__version__,
        platform=platform.platform(),
        workloads=rows,
        retains_queries=any(reference() is not None for reference in references),
        limits="Sequential warm complete calls:five legacy batches,three diagnostics batches. Numerical diagnostics are opt-in and bounded at321 vector evaluate calls, not per-point source-curve derivative certificates. Callbacks may perform unbounded internal work. Shared-workstation medians/ranges do not guarantee FPS or speedups; source-sign/sample-magnitude mismatch and smooth unresolved axes remain possible.",
    )
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            dict(
                label=args.label,
                medians=[
                    (
                        r["workload"],
                        r["legacy_gradient"]["median_ms"],
                        r.get("diagnostics", {}).get("median_ms"),
                    )
                    for r in rows
                ],
            )
        )
    )


if __name__ == "__main__":
    main()
