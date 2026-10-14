"""Measure complete old/current distance queries and bounded retained state."""

import argparse
import gc
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import tracemalloc
import weakref

import numpy as np
import sympy as sp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--label", default="current")
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
        if kind == "generic_rectangle":
            outer = CompositeCurve(outer.segments)
        elif kind == "circle":
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
            [create_square_from_edges((1.0, 1.0), (3.0, 3.0))]
            if kind == "hole"
            else None
        )
        return AreaRegion(outer, holes)

    def timing(query, repeats):
        query()
        batches = []
        for _ in range(5):
            start = time.perf_counter_ns()
            for _ in range(repeats):
                query()
            batches.append((time.perf_counter_ns() - start) / repeats / 1e6)
        return {"median_ms": statistics.median(batches), "batches_ms": batches}

    results = []
    for kind in ("rectangle", "generic_rectangle", "circle", "hole"):
        for size in (97, 257):
            xx, yy = np.meshgrid(
                np.linspace(-1.0, 5.0, size), np.linspace(-1.0, 5.0, size)
            )
            field = SignedDistanceField(make_region(kind))

            def edited():
                index = (size // 2) * size + 1
                xx.flat[index] = -1.0 if xx.flat[index] > 0 else 1.0
                return field.evaluate(xx, yy)

            def cold_result():
                field.clear_cache()
                return field.evaluate(xx, yy)

            results.append(
                {
                    "geometry": kind,
                    "shape": [size, size],
                    "repeated_same_grid": timing(lambda: field.evaluate(xx, yy), 5),
                    "copied_same_grid": timing(
                        lambda: field.evaluate(xx.copy(), yy.copy()), 5
                    ),
                    "inplace_edited_grid": timing(edited, 5),
                    "cleared_distance_cache": timing(cold_result, 5),
                    "gradient": timing(lambda: field.gradient(xx, yy), 2),
                    "scalar": timing(lambda: field.evaluate(1.0, 2.0), 10),
                }
            )

    field = SignedDistanceField(make_region("rectangle"))
    tracemalloc.start()
    refs = []
    for _ in range(10):
        memory_x, memory_y = np.meshgrid(
            np.linspace(-1.0, 5.0, 257), np.linspace(-1.0, 5.0, 257)
        )
        memory_result = field.evaluate(memory_x, memory_y)
        refs.extend(weakref.ref(a) for a in (memory_x, memory_y, memory_result))
        del memory_x, memory_y, memory_result
    gc.collect()
    retained, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metadata = {
        "label": args.label,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "workloads": results,
        "memory": {
            "retained_query_arrays": len({id(r()) for r in refs if r() is not None}),
            "python_traced_retained_bytes": retained,
            "python_traced_peak_bytes": peak,
        },
        "limits": "Warm timings include each full query, no compilation. Old cache-hit timings can be wrong. Tracemalloc excludes some native allocations; sampled curves are approximate. No speed/FPS or full-domain certificate.",
    }
    args.output.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "label": args.label,
                "memory": metadata["memory"],
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
