"""A declarative bridge from kinetic islands to the existing geometry engine.

``KineticIslandField`` is a real :class:`BaseField`, and its level sets are
``ImplicitCurve`` instances usable by CurveField, RFunctionCurve, SceneManager,
and GraphicsBackendInterface. Recipes contain bounded numeric data only; they
never deserialize expressions or Python callbacks.

The underlying field is dimensionless, NOT a signed-distance function. Gradients
and polylines are numerical approximations, with no exact G1/G2 guarantee. The
radial field is not differentiable at the island's moving center.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Integral
from types import MappingProxyType

import numpy as np

from . import kinetic
from .base_field import BaseField
from .procedural_curve import ProceduralCurve

RECIPE_VERSION = 1
LEVEL_BOUNDS = (-16.0, 16.0)
_FIELD_KEYS = {"type", "version", "parameters", "time", "motion"}
_GRADIENT_RELATIVE_STEP = float(np.cbrt(np.finfo(float).eps))


def _validate_recipe(data: Mapping, recipe_type: str, *, curve: bool = False):
    keys = _FIELD_KEYS | {"level"} if curve else _FIELD_KEYS
    if not isinstance(data, Mapping) or set(data) != keys:
        raise ValueError("invalid kinetic geometry recipe envelope")
    version = data["version"]
    if (
        data["type"] != recipe_type
        or isinstance(version, (bool, np.bool_))
        or not isinstance(version, Integral)
        or version != RECIPE_VERSION
        or not isinstance(data["parameters"], Mapping)
    ):
        raise ValueError("unsupported kinetic geometry recipe")


def _validate_level(level: float) -> float:
    level = kinetic._finite_number(level, "level")
    if not LEVEL_BOUNDS[0] <= level <= LEVEL_BOUNDS[1]:
        raise ValueError(f"level must be within {LEVEL_BOUNDS}")
    return level


class KineticIslandField(BaseField):
    """Snapshot of an island's scalar field, compatible with ``BaseField``.

    Parameters follow :func:`kinetic.normalize_parameters`: finite numeric
    values are clamped to the shared bounds, and unknown keys are rejected.
    Time is reduced modulo the 12-second loop; motion is clamped to [0, 1].
    Public recipe properties are read-only and ``parameters`` returns a copy.
    Create another snapshot to change the recipe or animation time.
    """

    def __init__(
        self,
        parameters: Mapping | None = None,
        time: float = 0.0,
        motion: float = 0.45,
    ):
        self._parameters = MappingProxyType(kinetic.normalize_parameters(parameters))
        self._time = kinetic._finite_number(time, "time") % kinetic.LOOP_DURATION
        self._motion = min(1.0, max(0.0, kinetic._finite_number(motion, "motion")))

    @property
    def parameters(self) -> dict:
        return dict(self._parameters)

    @property
    def time(self) -> float:
        return self._time

    @property
    def motion(self) -> float:
        return self._motion

    def evaluate(self, x, y):
        """Evaluate the exact shared numerical formula on broadcast coordinates."""
        return kinetic.evaluate(x, y, self._parameters, self.time, self.motion)

    def gradient(self, x, y):
        """Return radius-scaled central finite differences in world units.

        The nominal step is ``radius * cbrt(machine_epsilon)``. It is increased
        when necessary to remain representable at large world coordinates.
        Actual sample spacing is used in the denominator. At the coordinate
        domain boundary a clipped, one-sided difference is used instead.
        At the radial center the result is only a symmetric numerical estimate,
        since a classical gradient need not exist there.
        """
        # Validate types, bounds, broadcast shape, and allocation size before
        # doing arithmetic; don't silently coerce strings or booleans here.
        self.evaluate(x, y)
        x, y = np.broadcast_arrays(
            np.asarray(x, dtype=float), np.asarray(y, dtype=float)
        )
        step = self._parameters["radius"] * _GRADIENT_RELATIVE_STEP
        hx = np.maximum(step, 8.0 * np.abs(np.spacing(x)))
        hy = np.maximum(step, 8.0 * np.abs(np.spacing(y)))
        xp = np.minimum(x + hx, kinetic.MAX_COORDINATE)
        xm = np.maximum(x - hx, -kinetic.MAX_COORDINATE)
        yp = np.minimum(y + hy, kinetic.MAX_COORDINATE)
        ym = np.maximum(y - hy, -kinetic.MAX_COORDINATE)
        gx = (self.evaluate(xp, y) - self.evaluate(xm, y)) / (xp - xm)
        gy = (self.evaluate(x, yp) - self.evaluate(x, ym)) / (yp - ym)
        if np.ndim(gx) == 0:
            return float(gx), float(gy)
        return gx, gy

    def level_set(self, level: float = 0.0) -> KineticIslandCurve:
        """Return the declarative curve ``self(x,y) - level == 0``.

        Levels must be finite and within [-16, 16]. Levels below -1 have no
        points; -1 is the center point; larger levels are closed contours.
        """
        return KineticIslandCurve(self._parameters, self.time, self.motion, level)

    def to_dict(self) -> dict:
        return {
            "type": "KineticIslandField",
            "version": RECIPE_VERSION,
            "parameters": self.parameters,
            "time": self.time,
            "motion": self.motion,
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> KineticIslandField:
        _validate_recipe(data, "KineticIslandField")
        return cls(data["parameters"], data["time"], data["motion"])


class KineticIslandCurve(ProceduralCurve):
    """A serializable kinetic level set implementing ``ImplicitCurve``.

    The callable required by ProceduralCurve is created internally from a
    validated numeric recipe. Both serialization methods are overridden, so
    no callback placeholder or executable expression enters persistence.
    """

    def __init__(
        self,
        parameters: Mapping | None = None,
        time: float = 0.0,
        motion: float = 0.45,
        level: float = 0.0,
    ):
        self._field = KineticIslandField(parameters, time, motion)
        self._level = _validate_level(level)
        super().__init__(self.evaluate, name="kinetic_island")

    @property
    def field(self) -> KineticIslandField:
        return self._field

    @property
    def parameters(self) -> dict:
        return self.field.parameters

    @property
    def time(self) -> float:
        return self.field.time

    @property
    def motion(self) -> float:
        return self.field.motion

    @property
    def level(self) -> float:
        return self._level

    def evaluate(self, x, y):
        return self.field.evaluate(x, y) - self.level

    def gradient(self, x, y):
        return self.field.gradient(x, y)

    def is_closed(self) -> bool:
        return self.level > -1.0

    def bounding_box(self):
        """Conservative analytic envelope, or None for an empty level set."""
        if self.level < -1.0:
            return None
        parameters = self.field._parameters
        state = kinetic._motion_state(parameters, self.time, self.motion)
        # The negative notch cannot increase the radial profile. The sum of
        # the other harmonic amplitudes is a conservative upper bound.
        profile_max = 1.0 + 0.052 + 0.085 * parameters["warp"]
        profile_max += 0.026 + 0.026 * parameters["warp"] + 0.07
        extent = (1.0 + self.level) * profile_max * state["scale"]
        c, s = math.cos(state["rotation"]), math.sin(state["rotation"])
        stretch = state["stretch"]
        width = extent * math.hypot(c * stretch, s / stretch)
        height = extent * math.hypot(s * stretch, c / stretch)
        return (
            state["x"] - width,
            state["x"] + width,
            state["y"] - height,
            state["y"] + height,
        )

    def get_polyline_approximation(self, bounds=None, resolution: int = 200):
        """Sample a complete closed contour using the shared numeric kernels.

        ``bounds`` is accepted for graphics-interface compatibility; it does
        not clip this closed path. The renderer may clip it to its viewport.
        Resolution uses the core's bounded 24..720 angular samples. The closing
        point exactly repeats the first. An empty level set returns [], and
        the degenerate level -1 returns only the center point.
        """
        resolution = kinetic._bounded_integer(
            resolution, "resolution", 24, kinetic.MAX_SAMPLES
        )
        if self.level < -1.0:
            return []
        parameters = self.field._parameters
        state = kinetic._motion_state(parameters, self.time, self.motion)
        if self.level == -1.0:
            return [[state["x"], state["y"]]]
        theta = np.arange(resolution, dtype=float) * kinetic.TAU / resolution
        rho = (1.0 + self.level) * kinetic._profile(theta, parameters, state)
        angle = theta + kinetic._twist(rho, parameters, state)
        local_x = rho * np.cos(angle) * state["stretch"] * state["scale"]
        local_y = rho * np.sin(angle) / state["stretch"] * state["scale"]
        c, s = math.cos(state["rotation"]), math.sin(state["rotation"])
        points = np.stack(
            (
                state["x"] + local_x * c - local_y * s,
                state["y"] + local_x * s + local_y * c,
            ),
            axis=-1,
        )
        return np.concatenate((points, points[:1]), axis=0).tolist()

    def to_dict(self) -> dict:
        return {
            **self.field.to_dict(),
            "type": "KineticIslandCurve",
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> KineticIslandCurve:
        _validate_recipe(data, "KineticIslandCurve", curve=True)
        return cls(data["parameters"], data["time"], data["motion"], data["level"])
