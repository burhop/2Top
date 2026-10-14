"""Independent analytic fixtures, failure modes, probe counts and warm timings."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np


def fixtures():
    yield "affine_flat_axis", lambda x, y: 1 + y, (0.0, 0.0), (0, 1)
    yield "nonlinear_flat_axis", lambda x, y: x**3, (1.0, 0.0), (3, 0)
    for center in [0.0, 1e9, 1e12]:
        point = center + 0.3
        yield (
            f"translated_sine_{center:g}",
            lambda x, y, c=center: np.sin(x - c) + y,
            (point, 0.2),
            (np.cos(point - center), 1),
        )
    for scale in [1e-18, 1e-12, 1e-9, 1e-6, 1.0, 1e9]:
        yield (
            f"sine_scale_{scale:g}",
            lambda x, y, s=scale: np.sin(x / s) + y / s,
            (0.3 * scale, 0.2 * scale),
            (np.cos(0.3) / scale, 1 / scale),
        )
    yield "anisotropic", lambda x, y: np.sin(x) + y / 1e15, (0.0, 1e15), (1, 1e-15)
    for offset in [1e9, 1e15, 1e16]:
        yield (
            f"output_offset_{offset:g}",
            lambda x, y, c=offset: c + x + y,
            (0.0, 0.0),
            (1, 1),
        )
    yield (
        "quantized_oscillation",
        lambda x, y: 1e9 + np.sin(x) + x + y,
        (0.0, 0.0),
        (2, 1),
    )
    yield "log_boundary", lambda x, y: np.log(x) + y, (1e-9, 0.2), (1e9, 1)
    yield "abs_cusp", lambda x, y: np.abs(x) + y, (0.0, 0.0), None
    yield "sign_jump", lambda x, y: np.sign(x) + y, (0.0, 0.0), None
    yield "cube_root", lambda x, y: np.cbrt(x) + y, (0.0, 0.0), None
    yield "differentiable_cusp", lambda x, y: x * np.abs(x) + y * y, (0.0, 0.0), (0, 0)
    yield "stationary", lambda x, y: x * x + y * y, (0.0, 0.0), (0, 0)
    yield "cubic", lambda x, y: x**3 + y**3, (0.0, 0.0), (0, 0)
    step = np.finfo(float).eps ** 0.2
    yield (
        "dyadic_alias",
        lambda x, y: np.sin(2 * np.pi * x / step) + y,
        (0.0, 0.0),
        (2 * np.pi / step, 1),
    )

    # This analytic-at-origin bump vanishes at every nonzero sampled neighbor.
    # It explicitly demonstrates that sampled consistency is not a certificate.
    def hidden_bump(x, y):
        u = x / 1e-100
        return np.where(np.abs(u) < 1, x * np.exp(1 - 1 / (1 - u * u)), 0.0) + y

    yield "hidden_bump_counterexample", hidden_bump, (0.0, 0.0), (1, 1)
    yield (
        "subnormal_linear",
        lambda x, y: 1e-320 * (x + y),
        (0.0, 0.0),
        (1e-320, 1e-320),
    )


def safe(value):
    if isinstance(value, np.ndarray):
        return safe(value.tolist())
    if isinstance(value, (tuple, list)):
        return [safe(v) for v in value]
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--implementation-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.implementation_root.resolve()))
    from geometry.procedural_curve import ProceduralCurve
    from studio import __version__

    rows = []
    with np.errstate(all="ignore"):
        for name, function, point, expected in fixtures():
            calls = [0]

            def counted(x, y):
                calls[0] += 1
                return function(x, y)

            curve = ProceduralCurve(counted)
            info = curve.gradient_diagnostics(*point)
            evaluations = calls[0]
            actual = np.asarray(info["gradient"])
            row = dict(
                name=name,
                point=point,
                expected=expected,
                gradient=actual,
                evaluate_calls=evaluations,
                method=info["method"],
                error_estimate=info["error_estimate"],
                steps=info["steps"],
            )
            for key in (
                "status",
                "selection",
                "candidates",
                "nominal_step",
                "field_evaluations",
                "max_candidates",
            ):
                if key in info:
                    row[key] = info[key]
            if expected is not None:
                row["absolute_error"] = np.abs(actual - expected)
                row["normalized_error"] = np.abs(actual - expected) / np.maximum(
                    np.abs(expected), 1
                )
            try:
                row["normal"] = curve.normal(*point)
                row["normal_accepted"] = True
            except ValueError as error:
                row["normal_accepted"] = False
                row["normal_error"] = str(error)
            rows.append(row)
    axis = np.linspace(-1, 1, 97)
    xx, yy = np.meshgrid(axis, axis)

    def function(x, y):
        return np.sin(x) + y * y

    jobs = dict(
        default=ProceduralCurve(function),
        explicit_scale=ProceduralCurve(function, derivative_scale=1),
        analytic=ProceduralCurve(
            function, gradient_function=lambda x, y: (np.cos(x), 2 * y)
        ),
    )
    timings = {}
    for name, curve in jobs.items():
        curve.gradient(xx, yy)
        samples = []
        for _ in range(7):
            started = time.perf_counter()
            curve.gradient(xx, yy)
            samples.append(time.perf_counter() - started)
        timings[name] = dict(
            median_seconds=statistics.median(samples), samples_seconds=samples
        )
    record = dict(
        version=__version__,
        python=sys.version,
        numpy=np.__version__,
        platform=platform.platform(),
        results=rows,
        warm_grid_97_squared=timings,
        note="Independent analytic fixture evidence and explicit finite-sampling counterexamples; error estimates and sampled consistency are not accuracy certificates.",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(safe(record), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    for row in rows:
        error = max(row["normalized_error"]) if "normalized_error" in row else None
        print(
            row["name"],
            "error",
            error,
            "status",
            row.get("status"),
            "calls",
            row["evaluate_calls"],
            "normal",
            row["normal_accepted"],
        )
    print("warm median ms", {k: v["median_seconds"] * 1000 for k, v in timings.items()})


if __name__ == "__main__":
    main()
