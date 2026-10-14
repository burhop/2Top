"""Reproduce analytic contour containment and numeric level-set counterexamples."""

import argparse
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import sympy as sp


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--implementation-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.implementation_root.resolve()))
    from geometry import (
        ConicSection,
        RFunctionCurve,
        ImplicitCurve,
        ProceduralCurve,
        CurveField,
        union,
    )
    from geometry.curve_intersections import find_curve_intersections
    from studio import __version__

    x, y = sp.symbols("x y")
    circle = ConicSection(x * x + y * y - 1, (x, y))
    first = RFunctionCurve(circle, circle, "blend", 2)
    nested = RFunctionCurve(first, first, "blend", 2)
    axis = np.arange(1024) * 2 * np.pi / 1024
    results = {}
    for name, curve, radius in [
        ("identical_blend", first, np.sqrt(2)),
        ("nested_blend", nested, np.sqrt(3)),
    ]:
        points = np.column_stack((radius * np.cos(axis), radius * np.sin(axis)))
        box = curve.bounding_box()
        excess = np.maximum.reduce(
            (
                box[0] - points[:, 0],
                points[:, 0] - box[1],
                box[2] - points[:, 1],
                points[:, 1] - box[3],
                np.zeros(1024),
            )
        )
        started = time.perf_counter()
        for _ in range(100):
            curve.bounding_box()
        results[name] = dict(
            box=box,
            analytic_radius=float(radius),
            violations=int(np.sum(excess > 1e-14)),
            maximum_excess=float(np.max(excess)),
            warm_box_mean_ms=(time.perf_counter() - started) * 10,
        )
    for name, curve, point in [
        (
            "procedural_level",
            ProceduralCurve(lambda x, y: x * x + y * y - 1),
            (0.0, 0.0),
        ),
        (
            "extreme_blend_level",
            RFunctionCurve(
                ImplicitCurve(x, (x, y)), ImplicitCurve(y, (x, y)), "blend", 1e200
            ),
            (1e200, -1e200),
        ),
    ]:
        try:
            with np.errstate(all="ignore"):
                actual = float(CurveField(curve).level_set(0).evaluate(*point))
            results[name] = dict(
                actual=actual if math.isfinite(actual) else str(actual),
                expected=float(curve.evaluate(*point)),
                finite=math.isfinite(actual),
            )
        except Exception as error:
            results[name] = dict(error_type=type(error).__name__, error=str(error))
    remote = ProceduralCurve(lambda x, y: (x - 3) ** 2 + y * y - 1)
    other = ConicSection((x - 3.5) ** 2 + y * y - 1, (x, y))
    hits = find_curve_intersections(
        union(circle, remote), other, grid_resolution=160, tolerance=1e-7
    )
    results["remote_intersections"] = dict(
        actual=sorted(hits),
        expected=[[3.25, -math.sqrt(15) / 4], [3.25, math.sqrt(15) / 4]],
        search_range=5.0,
        grid_resolution=160,
        tolerance=1e-7,
    )
    record = dict(
        version=__version__,
        samples=1024,
        results=results,
        note="Analytic fixture checks; timings are local warm-cache means, not completeness or universal performance guarantees.",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, indent=2, allow_nan=False))


if __name__ == "__main__":
    run()
