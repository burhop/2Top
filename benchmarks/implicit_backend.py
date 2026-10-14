"""Reproducible warm backend timings and numerical checks; no speed assertions."""

import argparse
import hashlib
import json
import platform
from pathlib import Path
import statistics
import sys
import time

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geometry.implicit_curve import ImplicitCurve
from geometry.rfunction_curve import RFunctionCurve
from geometry.static_blend import StaticBlendField, contours_from_grid
from geometry.kinetic import contour_levels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if not 3 <= args.repeats <= 20:
        parser.error("Use 3..20 timed repeats")
    x, y = sp.symbols("x y")
    resolution = 192
    axis = np.linspace(-1, 1, resolution + 1)
    xx, yy = np.meshgrid(axis, axis)
    values = ((xx / 0.72) ** 2 + (yy / 0.55) ** 2 - 1).ravel().tolist()
    demo = json.loads((ROOT / "examples/tidal_atlas_confluence.json").read_text())
    first, second = [o["parameters"] for o in demo["objects"]]
    blend = StaticBlendField(first, second, "smooth_union", 0.85)
    bounds = blend.bounds()
    bx, by = np.meshgrid(
        np.linspace(bounds[0], bounds[1], 129),
        np.linspace(bounds[2], bounds[3], 129),
    )
    blend_values = blend.evaluate(bx, by).ravel().tolist()
    symbolic = ImplicitCurve(sp.sin(x) * sp.cos(y) + x * x + y * y)
    left, right = ImplicitCurve(x, (x, y)), ImplicitCurve(y, (x, y))
    union = RFunctionCurve(left, right, "blend", 0.6)
    jobs = {
        "ellipse_grid_192_16_levels": lambda: contours_from_grid(
            values, [-1, 1, -1, 1], np.linspace(-0.8, 0, 16).tolist(), 192
        ),
        "static_blend_grid_128_12_levels": lambda: contours_from_grid(
            blend_values, bounds, (contour_levels(12) - 1).tolist(), 128
        ),
        "symbolic_field_193_squared": lambda: symbolic.evaluate(xx, yy),
        "smooth_blend_field_193_squared": lambda: union.evaluate(xx, yy),
    }
    results = {}
    for name, job in jobs.items():
        output = job()  # compilation and one warm-up outside timing
        samples = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            output = job()
            samples.append(time.perf_counter() - start)
        signature = (
            [
                dict(
                    paths=len(layer["paths"]),
                    vertices=sum(map(len, layer["paths"])),
                    omitted=layer["omitted"],
                )
                for layer in output
            ]
            if isinstance(output, list)
            else dict(
                shape=list(np.shape(output)), finite=bool(np.isfinite(output).all())
            )
        )
        results[name] = dict(
            median_seconds=statistics.median(samples),
            min_seconds=min(samples),
            max_seconds=max(samples),
            samples_seconds=samples,
            output=signature,
        )
    record = dict(
        python=sys.version,
        numpy=np.__version__,
        sympy=sp.__version__,
        platform=platform.platform(),
        implementation_root=str(ROOT),
        warm_repeats=args.repeats,
        measurement="Sequential warm wall-clock timings on this host; includes contour validation/selection/stitching, excludes field sampling for grid jobs. No memory/renderer/FPS guarantee.",
        results=results,
        fixture_sha256=hashlib.sha256(
            np.asarray(values, dtype="<f8").tobytes()
        ).hexdigest(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({k: v["median_seconds"] for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
