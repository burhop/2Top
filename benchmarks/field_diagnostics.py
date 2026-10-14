"""Complete composed/wrapped field calls with explicit probe costs and validity."""

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
    from geometry.base_field import BlendedField, CurveField
    from geometry.field_strategy import SignedDistanceField
    from geometry.implicit_curve import ImplicitCurve
    from geometry.level_set_curve import LevelSetCurve

    x, y = sp.symbols("x y")

    def symbolic(expression):
        return CurveField(ImplicitCurve(sp.sympify(expression), (x, y)))

    def native(scale=1.0):
        return SignedDistanceField(
            AreaRegion(create_square_from_edges((0.0, 0.0), (4 * scale, 4 * scale)))
        )

    calls = [0]

    def affine(a, b):
        calls[0] += 1
        return 3 * a - 4 * b + 7

    callback = native()
    callback.evaluate = affine
    blend = BlendedField([callback, symbolic(0)])
    alias = CurveField(LevelSetCurve(blend.level_set(1.0), -1.0))
    shared = BlendedField([alias, callback])
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
    mid = (a + b) / 2
    boundary = mid / np.hypot(*mid)
    cases = [
        ("native_tiny_contour", native(1e-6).level_set(0.0), (2e-6, 1e-6)),
        ("callback_blend_scalar", blend, (0.3, 0.2)),
        (
            "callback_shared_alias_64",
            shared,
            (np.linspace(0.1, 0.5, 64), np.linspace(0.2, 0.4, 64)),
        ),
        (
            "sampled_jump_contour",
            BlendedField([circle, symbolic(0)]).level_set(0),
            tuple(boundary),
        ),
        (
            "sampled_smooth_contour",
            BlendedField([circle, symbolic(0)]).level_set(0),
            tuple(mid * 1.2),
        ),
    ]

    def run(query):
        try:
            result = query()
            return result, None
        except ValueError as error:
            return None, str(error)

    def timing(query):
        run(query)
        samples = []
        for _ in range(3):
            start = time.perf_counter_ns()
            run(query)
            samples.append((time.perf_counter_ns() - start) / 1e6)
        calls[0] = 0
        result, error = run(query)
        return dict(
            median_ms=statistics.median(samples),
            batches_ms=samples,
            callback_evaluations=calls[0],
            rejection=error,
        ), result

    rows = []
    for name, obj, point in cases:
        row = dict(workload=name)
        row["gradient"], _ = timing(lambda: obj.gradient(*point))
        if hasattr(obj, "normal"):
            row["normal"], _ = timing(lambda: obj.normal(*point))
        if callable(getattr(obj, "gradient_diagnostics", None)):
            row["diagnostics"], result = timing(
                lambda: obj.gradient_diagnostics(*point)
            )
            if result is not None:
                if "available" in result:
                    row["available_vectors"] = int(
                        np.count_nonzero(result["available"])
                    )
                row["query_points"] = int(np.broadcast_arrays(*point)[0].size)
                row["method"] = result["method"]
                row["field_evaluations"] = result.get("field_evaluations")
                row["sources"] = [
                    {
                        key: source[key]
                        for key in ("method", "field_evaluations", "derivative_target")
                        if key in source
                    }
                    for source in result.get("sources", [])
                ]
        rows.append(row)

    px, py = np.array([0.3, 0.4]), np.array([0.2, 0.1])
    references = weakref.ref(px), weakref.ref(py)
    if callable(getattr(shared, "gradient_diagnostics", None)):
        shared.gradient_diagnostics(px, py)
    else:
        shared.gradient(px, py)
    del px, py
    gc.collect()
    data = dict(
        label=args.label,
        python=platform.python_version(),
        numpy=np.__version__,
        platform=platform.platform(),
        workloads=rows,
        retains_queries=any(reference() is not None for reference in references),
        limits="Three sequential warm complete calls, including conservative rejection. Shared-workstation measurements are not speed/FPS guarantees. Only explicit diagnostics invoke new adaptive probes, bounded per distinct numerical leaf at321 vector evaluations plus graph/shift value checks. Supplied callback internal costs and universal accuracy remain unknown. Sampled consistency is uncertified; native endpoint geometry is not an exact curved-distance solver.",
    )
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
