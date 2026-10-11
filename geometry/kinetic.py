"""Declarative, deterministic kinetic islands for Tidal Atlas.

This module depends only on NumPy and the standard library. It does not depend
on an editor, renderer, procedural callbacks, or expression evaluation. The
same formulas and bounds live in ``studio/static/geometry.js``.

A positive, harmonic radial profile is transformed by a radius-dependent
angular twist, an area-preserving stretch, and a rigid transform. ``evaluate``
returns a dimensionless implicit field: zero at the outer shore, negative
inside, positive outside. It is NOT a Euclidean signed-distance function.
Contours are sampled polylines, not exact analytic curves. Their discretized
appearance and separation depend on the requested sampling resolution.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Real

import numpy as np

TAU = math.tau
LOOP_DURATION = 12.0
DEFAULT_PARAMETERS = {
    "x": 500.0,
    "y": 350.0,
    "radius": 230.0,
    "elongation": 1.2,
    "rotation": -24.0,
    "lobes": 3,
    "warp": 0.7,
    "phase": 0.4,
}
PARAMETER_BOUNDS = {
    "x": (-1000.0, 2000.0),
    "y": (-700.0, 1400.0),
    "radius": (80.0, 400.0),
    "elongation": (0.4, 2.5),
    "rotation": (-360.0, 360.0),
    "lobes": (2, 9),
    "warp": (0.0, 1.0),
    "phase": (0.0, TAU),
}
MAX_CONTOURS = 80
MAX_SAMPLES = 720
MAX_COORDINATE = 1e9
MAX_FIELD_SAMPLES = 4_000_000


def _finite_number(value: Real, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def normalize_parameters(parameters: Mapping | None = None) -> dict:
    """Return a fresh bounded numeric recipe, rejecting executable/unknown data.

    Missing values use defaults; finite out-of-range values are clamped.
    ``lobes`` uses half-up rounding so Python and JavaScript agree. Booleans,
    numeric strings, non-finite values, arrays, and unknown keys are rejected.
    """
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, Mapping):
        raise ValueError("parameters must be a plain numeric mapping")
    if set(parameters) - set(DEFAULT_PARAMETERS):
        raise ValueError("unknown island parameter")
    result = {}
    for name, default in DEFAULT_PARAMETERS.items():
        value = _finite_number(parameters.get(name, default), name)
        lower, upper = PARAMETER_BOUNDS[name]
        value = min(upper, max(lower, value))
        result[name] = int(math.floor(value + 0.5)) if name == "lobes" else value
    return result


def _bounded_integer(value: int, name: str, lower: int, upper: int) -> int:
    value = _finite_number(value, name)
    if not value.is_integer():
        raise ValueError(f"{name} must be an integer")
    return min(upper, max(lower, int(value)))


def _motion_state(parameters: Mapping, time: float, motion: float) -> dict:
    # Bounded phase reduction keeps trigonometry stable for long-lived sessions.
    # Integer harmonics share a smooth 12-second loop; negative time works too.
    time = _finite_number(time, "time")
    motion = min(1.0, max(0.0, _finite_number(motion, "motion")))
    t = (time % LOOP_DURATION) * TAU / LOOP_DURATION
    phase = parameters["phase"]
    breath = 1.0 + motion * (
        0.032 * math.sin(t + phase) + 0.012 * math.sin(3.0 * t + 0.7 * phase)
    )
    radius = parameters["radius"]
    return {
        "x": parameters["x"]
        + radius * 0.012 * motion * (math.sin(t + phase) - math.sin(phase)),
        "y": parameters["y"]
        + radius * 0.016 * motion * (math.cos(2.0 * t + phase) - math.cos(phase)),
        "scale": radius * breath,
        "stretch": math.sqrt(parameters["elongation"]),
        "rotation": parameters["rotation"] * math.pi / 180.0
        + 0.026 * motion * math.sin(t + phase),
        "phase": phase + 0.075 * motion * math.sin(t + 0.5 * phase),
        "twist_motion": 0.09 * motion * math.sin(2.0 * t + phase),
    }


def _profile(theta, parameters: Mapping, state: Mapping):
    warp, lobes, phase = parameters["warp"], parameters["lobes"], state["phase"]
    # Even the conservative sum-of-amplitudes lower bound is 0.101: no fold
    # or divide-by-zero is introduced by the radial profile itself.
    return (
        1.0
        + (0.052 + 0.085 * warp) * np.cos(lobes * theta + phase)
        + (0.026 + 0.026 * warp) * np.sin((lobes + 1) * theta - 0.7 * phase)
        + 0.07 * np.cos(theta - 0.6)
        - (0.15 + 0.49 * warp) * np.exp(3.6 * (np.cos(theta - 1.1 - 0.4 * phase) - 1.0))
    )


def _twist(rho, parameters: Mapping, state: Mapping):
    return parameters["warp"] * (2.35 / (1.0 + 2.7 * rho * rho) - 0.62) + state[
        "twist_motion"
    ] / (1.0 + rho * rho)


def contour_levels(count: int = 24) -> np.ndarray:
    """Return outer-to-inner normalized radii, ending at an ink-lagoon rim.

    The renderer chooses colors and can fill the last contour as a lagoon.
    The geometry deliberately has no palette or canvas dependency.
    """
    count = _bounded_integer(count, "count", 2, MAX_CONTOURS)
    return 1.0 - 0.82 * np.linspace(0.0, 1.0, count) ** 0.86


def generate_contours(
    parameters: Mapping | None = None,
    time: float = 0.0,
    motion: float = 0.45,
    count: int = 24,
    samples: int = 180,
) -> list[np.ndarray]:
    """Sample closed nested island contours as ``(samples + 1, 2)`` arrays.

    Rings are outermost first. The final point exactly repeats the first.
    Work is bounded: 2..80 rings and 24..720 samples per ring. Finite integers
    outside those ranges are clamped, while non-integers are rejected. No
    passed-in mapping is mutated. ``motion=0`` is independent of time.
    """
    parameters = normalize_parameters(parameters)
    state = _motion_state(parameters, time, motion)
    levels = contour_levels(count)
    samples = _bounded_integer(samples, "samples", 24, MAX_SAMPLES)
    theta = np.arange(samples, dtype=float) * TAU / samples
    rho = levels[:, None] * _profile(theta, parameters, state)[None, :]
    angle = theta[None, :] + _twist(rho, parameters, state)
    local_x = rho * np.cos(angle) * state["stretch"] * state["scale"]
    local_y = rho * np.sin(angle) / state["stretch"] * state["scale"]
    cosine, sine = math.cos(state["rotation"]), math.sin(state["rotation"])
    points = np.stack(
        (
            state["x"] + local_x * cosine - local_y * sine,
            state["y"] + local_x * sine + local_y * cosine,
        ),
        axis=-1,
    )
    return [np.concatenate((ring, ring[:1]), axis=0) for ring in points]


def evaluate(
    x,
    y,
    parameters: Mapping | None = None,
    time: float = 0.0,
    motion: float = 0.45,
):
    """Evaluate the dimensionless island field on scalar or broadcast arrays.

    Zero is the outer shoreline; generated ring ``i`` has field value
    ``contour_levels(count)[i] - 1``. Negative values are inside. Finite world
    coordinates must be within ±1e9 and broadcasts are limited to four million
    samples. These bounds prevent accidental extreme allocations/overflow.
    No exact-distance/continuity claim is made.
    """
    parameters = normalize_parameters(parameters)
    state = _motion_state(parameters, time, motion)
    try:
        x = np.asarray(x)
        y = np.asarray(y)
        if x.dtype.kind not in "iuf" or y.dtype.kind not in "iuf":
            raise ValueError("coordinates must be finite numbers")
        if math.prod(np.broadcast_shapes(x.shape, y.shape)) > MAX_FIELD_SAMPLES:
            raise ValueError("field sampling exceeds four million points")
        x, y = np.broadcast_arrays(x.astype(float), y.astype(float))
    except (TypeError, ValueError) as error:
        raise ValueError("coordinates must be broadcastable numeric arrays") from error
    if (
        np.any(~np.isfinite(x))
        or np.any(~np.isfinite(y))
        or np.any(np.abs(x) > MAX_COORDINATE)
        or np.any(np.abs(y) > MAX_COORDINATE)
    ):
        raise ValueError("coordinates must be finite and within ±1e9")
    dx, dy = x - state["x"], y - state["y"]
    cosine, sine = math.cos(state["rotation"]), math.sin(state["rotation"])
    local_x = (dx * cosine + dy * sine) / state["scale"] / state["stretch"]
    local_y = (-dx * sine + dy * cosine) / state["scale"] * state["stretch"]
    rho = np.hypot(local_x, local_y)
    theta = np.arctan2(local_y, local_x) - _twist(rho, parameters, state)
    field = rho / _profile(theta, parameters, state) - 1.0
    return float(field) if field.ndim == 0 else field


def to_recipe(parameters: Mapping | None = None) -> dict:
    """Serialize a standalone numeric island; no code is serialized."""
    return {
        "type": "tidal_island",
        "version": 1,
        "parameters": normalize_parameters(parameters),
    }


def from_recipe(recipe: Mapping) -> dict:
    """Validate a standalone island recipe and return its normalized parameters."""
    if not isinstance(recipe, Mapping) or set(recipe) != {
        "type",
        "version",
        "parameters",
    }:
        raise ValueError("invalid island recipe envelope")
    if (
        recipe["type"] != "tidal_island"
        or isinstance(recipe["version"], bool)
        or not isinstance(recipe["version"], Real)
        or recipe["version"] != 1
        or not isinstance(recipe["parameters"], Mapping)
    ):
        raise ValueError("unsupported island recipe")
    return normalize_parameters(recipe["parameters"])
