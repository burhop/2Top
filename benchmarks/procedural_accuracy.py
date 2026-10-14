"""Reproducible derivative accuracy against analytic functions; no speed claims."""

import argparse
import json
from pathlib import Path
import platform
import sys
import time
import statistics

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    for coordinate in [0.0, 1.0, 1e9, 1e15]:
        yield (
            f"linear_at_{coordinate:g}",
            lambda x, y: x + y,
            coordinate,
            0.0,
            max(1.0, abs(coordinate)),
            (1.0, 1.0),
        )
    for scale in [1e-9, 1.0, 1e9]:
        yield (
            f"sine_scale_{scale:g}",
            lambda x, y, s=scale: np.sin(x / s) + y / s,
            0.3 * scale,
            0.2 * scale,
            scale,
            (np.cos(0.3) / scale, 1 / scale),
        )
    for center in [1e9, 1e12]:
        x = center + 0.3
        yield (
            f"translated_sine_{center:g}",
            lambda x, y, c=center: np.sin(x - c) + y,
            x,
            0.2,
            1.0,
            (np.cos(x - center), 1.0),
        )
    yield "large_quadratic", lambda x, y: x * x + y * y, 1e9, 0.0, None, (2e9, 0.0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-root", type=Path, default=ROOT)
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Use 0.12 constructor without local scale hints",
    )
    args = parser.parse_args()
    sys.path.insert(0, str(args.implementation_root.resolve()))
    from geometry.procedural_curve import ProceduralCurve

    results = []
    for name, function, x, y, scale, expected in fixtures():
        keywords = (
            {} if args.baseline or scale is None else dict(derivative_scale=scale)
        )
        curve = ProceduralCurve(function, **keywords)
        actual = np.asarray(curve.gradient(x, y))
        expected = np.asarray(expected)
        results.append(
            dict(
                name=name,
                point=[x, y],
                derivative_scale=scale,
                expected=expected.tolist(),
                actual=actual.tolist(),
                absolute_error=np.abs(actual - expected).tolist(),
                normalized_error=(
                    np.abs(actual - expected) / np.maximum(np.abs(expected), 1)
                ).tolist(),
            )
        )
    axis = np.linspace(-1, 1, 97)
    xx, yy = np.meshgrid(axis, axis)
    function = lambda x, y: np.sin(x) + y * y
    jobs = {"numerical_grid_97_squared": ProceduralCurve(function)}
    if not args.baseline:
        jobs["analytic_grid_97_squared"] = ProceduralCurve(
            function, gradient_function=lambda x, y: (np.cos(x), 2 * y)
        )
    timings = {}
    for name, curve in jobs.items():
        curve.gradient(xx, yy)
        samples = []
        for _ in range(5):
            start = time.perf_counter()
            curve.gradient(xx, yy)
            samples.append(time.perf_counter() - start)
        timings[name] = dict(
            median_seconds=statistics.median(samples), samples_seconds=samples
        )
    record = dict(
        python=sys.version,
        numpy=np.__version__,
        platform=platform.platform(),
        baseline_constructor=args.baseline,
        measurement="Deterministic analytic derivative fixtures, not a universal accuracy bound; local scale hints are explicit.",
        results=results,
        warm_timings=timings,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(
        json.dumps({r["name"]: max(r["normalized_error"]) for r in results}, indent=2)
    )


if __name__ == "__main__":
    main()
