"""Static compositions reuse legacy RFunctionCurve, never signed distances."""

import math

import numpy as np

from .base_field import CurveField
from .kinetic import normalize_parameters
from .kinetic_field import KineticIslandField
from .procedural_curve import ProceduralCurve
from .rfunction_curve import RFunctionCurve


class _StaticBlendCurve(RFunctionCurve):
    def bounding_box(self):
        return tuple(self._sample_bounds)


class StaticBlendField(CurveField):
    """Detached two-island field. Amount is dimensionless legacy blend alpha."""

    def __init__(self, first, second, operation="smooth_union", amount=0.6):
        if operation not in {"union", "smooth_union"}:
            raise ValueError("Unsupported static blend operation")
        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not math.isfinite(amount)
            or not 0 <= amount <= 1
        ):
            raise ValueError("Blend amount must be finite within 0..1")
        self.first = normalize_parameters(first)
        self.second = normalize_parameters(second)
        self.blend_operation, self.amount = operation, float(amount)
        alpha = self.amount if operation == "smooth_union" else 0
        curve = _StaticBlendCurve(
            KineticIslandField(self.first, 0, 0).level_set(0),
            KineticIslandField(self.second, 0, 0).level_set(0),
            "blend" if alpha else "union",
            alpha,
        )
        curve._sample_bounds = self.bounds()
        super().__init__(curve)

    def bounds(self):
        # Profile <= 1.259; smooth min lowers min by at most alpha/2.
        # The conservative radius also covers rotations and area-preserving stretch.
        extents = []
        for p in (self.first, self.second):
            stretch = max(math.sqrt(p["elongation"]), 1 / math.sqrt(p["elongation"]))
            alpha = self.amount if self.blend_operation == "smooth_union" else 0
            extent = p["radius"] * stretch * (1.5 + alpha * 0.75)
            extents.append(
                (p["x"] - extent, p["x"] + extent, p["y"] - extent, p["y"] + extent)
            )
        return [
            min(b[0] for b in extents),
            max(b[1] for b in extents),
            min(b[2] for b in extents),
            max(b[3] for b in extents),
        ]

    def level_set(self, level=0):
        if (
            not isinstance(level, (int, float))
            or isinstance(level, bool)
            or not math.isfinite(level)
        ):
            raise ValueError("Level must be finite")
        if level == 0:
            return self.curve
        return ProceduralCurve(
            lambda x, y: self.evaluate(x, y) - level, self.curve.variables
        )

    def to_dict(self):
        return {
            "type": "StaticBlendField",
            "first": dict(self.first),
            "second": dict(self.second),
            "operation": self.blend_operation,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, data):
        if (
            not isinstance(data, dict)
            or set(data) != {"type", "first", "second", "operation", "amount"}
            or data["type"] != "StaticBlendField"
        ):
            raise ValueError("Invalid static blend envelope")
        return cls(data["first"], data["second"], data["operation"], data["amount"])


def sample_field_contours(field, bounds, levels, resolution=128):
    """Fixed-diagonal marching triangles with shared vertex keys and linear edges.

    Closed loops only; open/clipped/zero-area fragments are reported and omitted.
    This is an approximation, not exact topology/continuity or Euclidean offsets.
    """
    if type(resolution) is not int or not 24 <= resolution <= 192:
        raise ValueError("Resolution must be an integer within 24..192")
    if (
        len(bounds) != 4
        or not all(math.isfinite(v) for v in bounds)
        or bounds[0] >= bounds[1]
        or bounds[2] >= bounds[3]
    ):
        raise ValueError("Invalid sampling bounds")
    if not 1 <= len(levels) <= 16 or not all(math.isfinite(v) for v in levels):
        raise ValueError("At most 16 finite contour levels")
    n = resolution + 1
    xs = np.linspace(bounds[0], bounds[1], n)
    ys = np.linspace(bounds[2], bounds[3], n)
    xx, yy = np.meshgrid(xs, ys)
    values = np.asarray(field.evaluate(xx, yy)).reshape(-1)
    if len(values) != n * n or not np.isfinite(values).all():
        raise ValueError("The sampled field must be finite")
    return contours_from_grid(values.tolist(), bounds, levels, resolution)


def contours_from_grid(values, bounds, levels, resolution):
    n = resolution + 1
    layers = []
    for level in levels:
        points, neighbors, segments = {}, {}, []

        def crossing(a, b):
            a, b = min(a, b), max(a, b)
            fraction = (level - values[a]) / (values[b] - values[a])
            key = f"v{a}" if fraction == 0 else f"v{b}" if fraction == 1 else f"{a}:{b}"
            if key not in points:
                gx = a % n + fraction * (b % n - a % n)
                gy = a // n + fraction * (b // n - a // n)
                points[key] = [
                    bounds[0] + gx / resolution * (bounds[1] - bounds[0]),
                    bounds[2] + gy / resolution * (bounds[3] - bounds[2]),
                ]
            return key

        for row in range(resolution):
            for col in range(resolution):
                a = row * n + col
                for tri in ((a, a + 1, a + n + 1), (a, a + n + 1, a + n)):
                    inside = [values[v] < level for v in tri]
                    if all(inside) or not any(inside):
                        continue
                    keys = [
                        crossing(tri[i], tri[j])
                        for i, j in ((0, 1), (1, 2), (2, 0))
                        if inside[i] != inside[j]
                    ]
                    if keys[0] == keys[1]:
                        continue
                    edge = len(segments)
                    segments.append(keys)
                    for key in keys:
                        neighbors.setdefault(key, []).append(edge)
        visited, paths, omitted = set(), [], 0
        for edge, (start, _) in enumerate(segments):
            if edge in visited:
                continue
            key, path, closed = start, [points[start]], False
            while edge not in visited:
                visited.add(edge)
                a, b = segments[edge]
                key = b if key == a else a
                path.append(points[key])
                if key == start:
                    closed = True
                    break
                candidates = [e for e in neighbors[key] if e not in visited]
                if not candidates:
                    break
                edge = candidates[0]
            area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(path, path[1:]))
            if closed and len(path) >= 4 and abs(area) > 1e-10:
                paths.append(path)
            else:
                omitted += 1
        layers.append({"level": level, "paths": paths, "omitted": omitted})
    return layers
