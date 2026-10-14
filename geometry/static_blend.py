"""Static compositions reuse legacy RFunctionCurve, never signed distances."""

import math

import numpy as np

from .base_field import CurveField
from .kinetic import normalize_parameters
from .kinetic_field import KineticIslandField
from .procedural_curve import ProceduralCurve
from .rfunction_curve import RFunctionCurve
from .numeric import real_array


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


def _sampling_inputs(bounds, levels, resolution, minimum=1):
    if type(resolution) is not int or not minimum <= resolution <= 192:
        raise ValueError(f"Resolution must be an integer within {minimum}..192")
    bounds, levels = real_array(bounds), real_array(levels)
    if (
        bounds.shape != (4,)
        or not np.isfinite(bounds).all()
        or bounds[0] >= bounds[1]
        or bounds[2] >= bounds[3]
    ):
        raise ValueError("Invalid finite sampling bounds")
    with np.errstate(over="ignore"):
        extents = bounds[[1, 3]] - bounds[[0, 2]]
    if not np.isfinite(extents).all():
        raise ValueError("Sampling bounds must have finite extents")
    if levels.ndim != 1 or not 1 <= len(levels) <= 16 or not np.isfinite(levels).all():
        raise ValueError("At most 16 finite contour levels")
    return bounds, levels


def sample_field_contours(field, bounds, levels, resolution=128):
    """Fixed-diagonal marching triangles with shared vertex keys and linear edges.

    Closed loops only; open/clipped/zero-area fragments are reported and omitted.
    This is an approximation, not exact topology/continuity or Euclidean offsets.
    """
    bounds, levels = _sampling_inputs(bounds, levels, resolution, 24)
    n = resolution + 1
    xs = np.linspace(bounds[0], bounds[1], n)
    ys = np.linspace(bounds[2], bounds[3], n)
    xx, yy = np.meshgrid(xs, ys)
    values = np.broadcast_to(real_array(field.evaluate(xx, yy)), xx.shape)
    if not np.isfinite(values).all():
        raise ValueError("The sampled field must be finite")
    return contours_from_grid(values, bounds, levels, resolution)


def contours_from_grid(values, bounds, levels, resolution):
    """Extract deterministic closed cycles of the sampled triangulation.

    Accept a row-major flat grid or a square grid. Open, branched and numerically
    degenerate connected components count once in ``omitted``; exact-level
    vertices belong outside. This does not establish continuous-field topology.
    """
    bounds, levels = _sampling_inputs(bounds, levels, resolution)
    n = resolution + 1
    values = real_array(values)
    if values.shape not in {(n * n,), (n, n)}:
        raise ValueError("Sampled grid must have (resolution + 1)^2 values")
    if not np.isfinite(values).all():
        raise ValueError("The sampled field must be finite")
    values = values.reshape(-1)
    rows, cols = np.indices((resolution, resolution))
    starts = (rows * n + cols).ravel()
    triangles = np.stack(
        (
            np.stack((starts, starts + 1, starts + n + 1), axis=1),
            np.stack((starts, starts + n + 1, starts + n), axis=1),
        ),
        axis=1,
    ).reshape(-1, 3)
    triangle_values = values[triangles]
    layers = []
    for level in levels:
        points, local_points, neighbors, segments, unique = {}, {}, {}, [], set()

        def crossing(a, b):
            a, b = min(a, b), max(a, b)
            first, second = float(values[a]), float(values[b])
            numerator, denominator = float(level) - first, second - first
            if math.isfinite(numerator) and math.isfinite(denominator):
                fraction = numerator / denominator
            else:
                scale = max(abs(first), abs(second), abs(float(level)))
                fraction = (level / scale - first / scale) / (
                    second / scale - first / scale
                )
            key = f"v{a}" if fraction == 0 else f"v{b}" if fraction == 1 else f"{a}:{b}"
            if key not in points:
                gx = a % n + fraction * (b % n - a % n)
                gy = a // n + fraction * (b // n - a // n)
                points[key] = [
                    bounds[0] + gx / resolution * (bounds[1] - bounds[0]),
                    bounds[2] + gy / resolution * (bounds[3] - bounds[2]),
                ]
                # Measure representable output coordinates, so a loop that
                # collapses during world mapping is omitted too.
                local_points[key] = [
                    (points[key][0] - bounds[0]) / (bounds[1] - bounds[0]),
                    (points[key][1] - bounds[2]) / (bounds[3] - bounds[2]),
                ]
            return key

        inside_values = triangle_values < level
        candidates = np.flatnonzero(
            inside_values.any(axis=1) & ~inside_values.all(axis=1)
        )
        for index in candidates:
            tri, inside = triangles[index], inside_values[index]
            keys = [
                crossing(int(tri[i]), int(tri[j]))
                for i, j in ((0, 1), (1, 2), (2, 0))
                if inside[i] != inside[j]
            ]
            identity = tuple(sorted(keys))
            if keys[0] == keys[1] or identity in unique:
                continue
            unique.add(identity)
            edge = len(segments)
            segments.append(keys)
            for key in keys:
                neighbors.setdefault(key, []).append(edge)
        visited, paths, omitted = set(), [], 0
        for edge, (start, _) in enumerate(segments):
            if edge in visited:
                continue
            # Reject the whole ambiguous/open component, rather than guessing
            # which branches form a loop at a shared exact-level vertex.
            component, pending, vertices = set(), [edge], set()
            while pending:
                current = pending.pop()
                if current in component:
                    continue
                component.add(current)
                for vertex in segments[current]:
                    vertices.add(vertex)
                    pending.extend(e for e in neighbors[vertex] if e not in component)
            if any(len(neighbors[v]) != 2 for v in vertices):
                visited.update(component)
                omitted += 1
                continue
            key, path, local, closed = (
                start,
                [points[start]],
                [local_points[start]],
                False,
            )
            while edge not in visited:
                visited.add(edge)
                a, b = segments[edge]
                key = b if key == a else a
                path.append(points[key])
                local.append(local_points[key])
                if key == start:
                    closed = True
                    break
                candidates = [e for e in neighbors[key] if e not in visited]
                if not candidates:
                    break
                edge = candidates[0]
            ox, oy = local[0]
            area = math.fsum(
                (a[0] - ox) * (b[1] - oy) - (b[0] - ox) * (a[1] - oy)
                for a, b in zip(local, local[1:])
            )
            span = max(
                max(p[i] for p in local) - min(p[i] for p in local) for i in (0, 1)
            )
            tolerance = 32 * np.finfo(float).eps * span**2 * len(local)
            if closed and len(path) >= 4 and abs(area) > tolerance:
                paths.append(path)
            else:
                omitted += 1
        layers.append({"level": level, "paths": paths, "omitted": omitted})
    return layers
