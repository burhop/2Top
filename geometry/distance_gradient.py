"""Query-local geometric gradients for native straight SDF boundaries."""

from decimal import Decimal, localcontext
from fractions import Fraction

import numpy as np

from .numeric import (
    _difference_with_error,
    endpoint_polygon_inside,
    real_array,
    segment_distance,
)


def native_boundaries(region):
    """Return validated endpoint chains only for native containment methods."""
    from .area_region import AreaRegion
    from .composite_curve import CompositeCurve

    if getattr(region.contains, "__func__", None) is not AreaRegion.contains:
        return None
    boundaries = []
    for boundary in [region.outer_boundary, *region.holes]:
        if (
            getattr(boundary.contains, "__func__", None) is not CompositeCurve.contains
            or not boundary.segments
            or any(
                getattr(segment, "is_curved", True)
                or not hasattr(segment, "get_endpoints")
                for segment in boundary.segments
            )
        ):
            return None
        pairs = [segment.get_endpoints() for segment in boundary.segments]
        if any(pair is None or len(pair) != 2 for pair in pairs):
            return None
        edges = real_array(pairs)
        endpoint_polygon_inside([], [], edges)  # Same finite/exact closure contract.
        boundaries.append(edges)
    return boundaries


def _fraction_point(point):
    return tuple(Fraction.from_float(float(v)) for v in point)


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _subtract(a, b):
    return a[0] - b[0], a[1] - b[1]


def _projection(point, edge):
    a, b = edge
    direction, offset = _subtract(b, a), _subtract(point, a)
    norm = _dot(direction, direction)
    parameter = (
        min(Fraction(1), max(Fraction(0), _dot(offset, direction) / norm))
        if norm
        else Fraction(0)
    )
    residual = tuple(offset[i] - parameter * direction[i] for i in range(2))
    return _dot(residual, residual), residual, direction


def _unit_exact(vector):
    """Normalize exact residuals before float conversion; protect tiny units."""
    scale = max(abs(v) for v in vector)
    if not scale:
        return np.nan, np.nan
    ratios = tuple(v / scale for v in vector)
    floats = np.array([float(v) for v in ratios])
    if any(v and abs(f) < np.finfo(float).tiny for v, f in zip(ratios, floats)):
        # A rounded half-subnormal ratio can depend on a tiny norm correction.
        # Binary64 source coordinates bound this rare path; no universal
        # correct-rounding claim follows from the fixed 1600-digit guard.
        with localcontext() as context:
            context.prec = 1600
            a, b = [Decimal(v.numerator) / Decimal(v.denominator) for v in ratios]
            norm = (a * a + b * b).sqrt()
            return float(a / norm), float(b / norm)
    return tuple(floats / np.hypot(*floats))


def _ordinary(x, y, edge):
    lower, upper = 2.0**-200, 2.0**200
    values = np.abs(edge)
    edge_valid = np.all((values == 0) | ((values >= lower) & (values <= upper)))
    ax, ay = np.abs(x), np.abs(y)
    return (
        edge_valid
        & ((ax == 0) | ((ax >= lower) & (ax <= upper)))
        & ((ay == 0) | ((ay >= lower) & (ay <= upper)))
    )


def _endpoint_projection(x, y, edge, index):
    """Prove a shared endpoint is nearest using normal-arithmetic guards."""
    (ax, ay), (bx, by) = edge
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return np.ones(x.shape, dtype=bool)
    with np.errstate(all="ignore"):
        u, v = (x - edge[index, 0]) * dx, (y - edge[index, 1]) * dy
        dot = u + v
        guard = 64 * np.finfo(float).eps * (np.abs(u) + np.abs(v))
        admitted = dot < -guard if index == 0 else dot > guard
    return _ordinary(x, y, edge) & admitted


def _shared_projection(x, y, first, second):
    result = np.zeros(x.shape, dtype=bool)
    for i in range(2):
        for j in range(2):
            if np.array_equal(first[i], second[j]):
                result |= _endpoint_projection(x, y, first, i) & _endpoint_projection(
                    x, y, second, j
                )
    return result


def _axis_offsets(x, y, edge):
    """Exact high/low projected distance within the normal-arithmetic envelope."""
    (ax, ay), (bx, by) = edge
    if ax == bx and ay != by:
        projected = (min(ay, by) <= y) & (y <= max(ay, by))
        coordinate, fixed, axis = x, ax, 0
    elif ay == by and ax != bx:
        projected = (min(ax, bx) <= x) & (x <= max(ax, bx))
        coordinate, fixed, axis = y, ay, 1
    else:
        return None
    with np.errstate(all="ignore"):
        high, low = _difference_with_error(coordinate, fixed)
    return (
        projected & _ordinary(x, y, edge),
        np.abs(high),
        np.where(high < 0, -low, low),
        axis,
        fixed,
    )


def _axis_comparison(x, y, old, new):
    """Resolve projected axis ties exactly with representable TwoDiff lows."""
    first, second = _axis_offsets(x, y, old), _axis_offsets(x, y, new)
    if first is None or second is None:
        return np.zeros(x.shape, dtype=bool), None, False
    active = first[0] & second[0]
    # Normal subtraction is correctly rounded and monotonic. If high parts
    # differ their order is exact; if equal the exact TwoDiff lows decide it.
    smaller = (second[1] < first[1]) | (
        (second[1] == first[1]) & (second[2] < first[2])
    )
    equal = (second[1] == first[1]) & (second[2] == first[2])
    relation = np.where(smaller, -1, np.where(equal, 0, 1))
    return active, relation, first[3:] == second[3:]


def _axis_boundary_units(x, y, edge, boundaries):
    """Exact infinitesimal side membership for fully rectilinear chains.

    Positive/negative coordinate infinitesimals change endpoint equality into
    strict/non-strict comparisons. No rounded offset or tolerance is used.
    """
    vertical = edge[0, 0] == edge[1, 0] and edge[0, 1] != edge[1, 1]
    horizontal = edge[0, 1] == edge[1, 1] and edge[0, 0] != edge[1, 0]
    gx, gy = np.full(x.shape, np.nan), np.full(x.shape, np.nan)
    if not vertical and not horizontal:
        return gx, gy
    positive, negative, conflict = [np.zeros(x.shape, dtype=bool) for _ in range(3)]
    inside_plus, inside_minus = None, None
    for boundary_index, edges in enumerate(boundaries):
        plus, minus = np.zeros(x.shape, dtype=bool), np.zeros(x.shape, dtype=bool)
        for (ax, ay), (bx, by) in edges:
            if ax == bx and ay != by:
                low, high = min(ay, by), max(ay, by)
                incident = (x == ax) & (low <= y) & (y <= high)
                if vertical:
                    positive |= incident & (high > y)
                    negative |= incident & (low < y)
                    active = (low <= y) & (y < high)
                    plus ^= active & (x < ax)
                    minus ^= active & (x <= ax)
                else:
                    conflict |= incident
                    plus ^= (x < ax) & (low <= y) & (y < high)
                    minus ^= (x < ax) & (low < y) & (y <= high)
            elif ay == by and ax != bx:
                low, high = min(ax, bx), max(ax, bx)
                incident = (y == ay) & (low <= x) & (x <= high)
                if horizontal:
                    positive |= incident & (high > x)
                    negative |= incident & (low < x)
                else:
                    conflict |= incident
        if boundary_index == 0:
            inside_plus, inside_minus = plus, minus
        else:
            inside_plus &= ~plus
            inside_minus &= ~minus
    defined = positive & negative & ~conflict & (inside_plus != inside_minus)
    if vertical:
        gx[defined], gy[defined] = np.where(inside_plus[defined], -1.0, 1.0), 0.0
    else:
        gx[defined], gy[defined] = 0.0, np.where(inside_plus[defined], -1.0, 1.0)
    return gx, gy


def _segment_units(x, y, edge):
    """Unsigned unit gradients; exact boundary and uncertain projections defer."""
    gx, gy = np.full(x.shape, np.nan), np.full(x.shape, np.nan)
    boundary = np.zeros(x.shape, dtype=bool)
    (ax, ay), (bx, by) = edge
    if ay == by and ax != bx:
        axis = (min(ax, bx) <= x) & (x <= max(ax, bx))
        gx[axis] = 0.0
        gy[axis] = (y[axis] > ay).astype(float) - (y[axis] < ay).astype(float)
        boundary[axis] = y[axis] == ay
    elif ax == bx and ay != by:
        axis = (min(ay, by) <= y) & (y <= max(ay, by))
        gx[axis] = (x[axis] > ax).astype(float) - (x[axis] < ax).astype(float)
        gy[axis] = 0.0
        boundary[axis] = x[axis] == ax
    else:
        axis = np.zeros(x.shape, dtype=bool)
    if np.all(axis):
        return gx, gy, boundary
    with np.errstate(all="ignore"):
        dx, dy = bx - ax, by - ay
        wx, wy = x - ax, y - ay
        u, v = wx * dx, wy * dy
        dot, norm = u + v, dx * dx + dy * dy
        epsilon = 64 * np.finfo(float).eps
        guard_a, guard_b = (
            epsilon * (np.abs(u) + np.abs(v)),
            epsilon * (np.abs(u) + np.abs(v) + norm),
        )
        ordinary = _ordinary(x, y, edge)
        at_a, at_b = ordinary & (dot < -guard_a), ordinary & (dot - norm > guard_b)
        interior = ordinary & (dot > guard_a) & (norm - dot > guard_b)
        cross_a, cross_b = wx * dy, wy * dx
        determinant = cross_a - cross_b
        interior &= np.abs(determinant) > epsilon * (np.abs(cross_a) + np.abs(cross_b))
        at_a &= ~axis
        at_b &= ~axis
        interior &= ~axis
        length = np.hypot(dx, dy)
        gx[interior] = np.sign(determinant[interior]) * dy / length
        gy[interior] = -np.sign(determinant[interior]) * dx / length
        for mask, a, b in ((at_a, ax, ay), (at_b, bx, by)):
            rx, ry = x[mask] - a, y[mask] - b
            distance = np.hypot(rx, ry)
            gx[mask], gy[mask] = rx / distance, ry / distance
    exact_edge = tuple(_fraction_point(p) for p in edge)
    for index in np.flatnonzero(~(axis | at_a | at_b | interior)):
        squared, residual, _ = _projection(
            _fraction_point((x[index], y[index])), exact_edge
        )
        boundary[index] = squared == 0
        if squared:
            gx[index], gy[index] = _unit_exact(residual)
    return gx, gy, boundary


def _inside_exact(point, boundaries):
    def polygon(edges):
        x, y = point
        inside = False
        for (ax, ay), (bx, by) in edges:
            if (ay <= y < by) or (by <= y < ay):
                inside ^= x < ax + (y - ay) * (bx - ax) / (by - ay)
        return inside

    return polygon(boundaries[0]) and not any(
        polygon(edges) for edges in boundaries[1:]
    )


def _boundary_unit(point, direction, boundaries):
    """Exact local side probes, before other intersections, certify a normal."""
    if not any(direction):
        return np.nan, np.nan
    normal = direction[1], -direction[0]
    intersections = []
    negative_ray, positive_ray = False, False
    for edges in boundaries:
        for a, b in edges:
            delta, offset = _subtract(b, a), _subtract(point, a)
            norm = _dot(delta, delta)
            incident = (
                (_cross(offset, delta) == 0 and 0 <= _dot(offset, delta) <= norm)
                if norm
                else point == a
            )
            if incident:
                if norm and _cross(direction, delta):
                    return np.nan, np.nan
                for endpoint in (a, b):
                    side = _dot(_subtract(endpoint, point), direction)
                    negative_ray |= side < 0
                    positive_ray |= side > 0
            # Intersections with the complete normal line, including endpoint
            # hits and collinear overlaps, bound probes on both sides.
            determinant = _cross(normal, delta)
            from_point = _subtract(a, point)
            if determinant:
                parameter = _cross(from_point, delta) / determinant
                along_edge = _cross(from_point, normal) / determinant
                if 0 <= along_edge <= 1 and parameter:
                    intersections.append(abs(parameter))
            elif _cross(from_point, normal) == 0:
                coordinate = 0 if normal[0] else 1
                for endpoint in (a, b):
                    parameter = (endpoint[coordinate] - point[coordinate]) / normal[
                        coordinate
                    ]
                    if parameter:
                        intersections.append(abs(parameter))
    if not negative_ray or not positive_ray:
        return np.nan, np.nan
    step = min(intersections) / 2 if intersections else Fraction(1)
    plus = tuple(point[i] + step * normal[i] for i in range(2))
    minus = tuple(point[i] - step * normal[i] for i in range(2))
    inside_plus, inside_minus = (
        _inside_exact(plus, boundaries),
        _inside_exact(minus, boundaries),
    )
    if inside_plus == inside_minus:
        return np.nan, np.nan
    unit = _unit_exact(normal)
    return tuple(-v for v in unit) if inside_plus else unit


def geometric_gradient(x, y, boundaries, inside):
    """Nearest-feature derivative; exact ties distinguish one/many projections.

    All data, exact arithmetic and decisions live within this query. The normal
    floating path uses the existing magnitude kernel and 64eps comparison guard;
    close, zero-rounded and infinite distances use exact rational comparisons.
    """
    edges = np.concatenate(boundaries)
    size = x.size
    best = np.full(size, np.inf)
    indices = np.full(size, -1, dtype=int)
    conflict = np.zeros(size, dtype=bool)
    exact_boundaries = [
        [tuple(_fraction_point(p) for p in edge) for edge in chain]
        for chain in boundaries
    ]
    exact_edges = [edge for chain in exact_boundaries for edge in chain]
    seen = set()
    for candidate, edge in enumerate(edges):
        key = tuple(sorted(tuple(p) for p in edge))
        if key in seen:
            continue  # Membership and boundary probes still retain every edge.
        seen.add(key)
        distance = segment_distance(x, y, *edge)
        initial = indices < 0
        with np.errstate(all="ignore"):
            magnitude = np.maximum(distance, best)
            ulp = np.where(np.isfinite(magnitude), np.spacing(magnitude), 0.0)
            guard = np.maximum(64 * np.finfo(float).eps * magnitude, 4 * ulp)
            close = ~initial & ((distance == best) | (np.abs(distance - best) <= guard))
        better = initial | ((distance < best) & ~close)
        best[better], indices[better], conflict[better] = (
            distance[better],
            candidate,
            False,
        )
        for previous in np.unique(indices[close]):
            selected = np.flatnonzero(close & (indices == previous))
            handled, relation, same_projection = _axis_comparison(
                x[selected], y[selected], edges[previous], edge
            )
            if relation is not None:
                improved = selected[handled & (relation < 0)]
                best[improved], indices[improved], conflict[improved] = (
                    distance[improved],
                    candidate,
                    False,
                )
                if not same_projection:
                    conflict[selected[handled & (relation == 0)]] = True
            selected = selected[~handled]
            common = _shared_projection(x[selected], y[selected], edges[previous], edge)
            for index in selected[~common]:
                point = _fraction_point((x[index], y[index]))
                old_sq, old_residual, old_direction = _projection(
                    point, exact_edges[previous]
                )
                new_sq, new_residual, new_direction = _projection(
                    point, exact_edges[candidate]
                )
                if new_sq < old_sq:
                    best[index], indices[index], conflict[index] = (
                        distance[index],
                        candidate,
                        False,
                    )
                elif new_sq == old_sq:
                    if new_sq:
                        conflict[index] |= new_residual != old_residual
                    elif any(new_direction) and any(old_direction):
                        conflict[index] |= _cross(new_direction, old_direction) != 0
                    elif any(new_direction):
                        indices[index] = candidate
    gx, gy = np.full(size, np.nan), np.full(size, np.nan)
    sign = np.where(inside, -1.0, 1.0)
    rectilinear = np.all(
        (edges[:, 0, 0] == edges[:, 1, 0]) | (edges[:, 0, 1] == edges[:, 1, 1])
    )
    boundary_cache = {}
    for selected in np.unique(indices[~conflict]):
        mask = (indices == selected) & ~conflict
        sx, sy, boundary = _segment_units(x[mask], y[mask], edges[selected])
        gx[mask], gy[mask] = sign[mask] * sx, sign[mask] * sy
        boundary_indices = np.flatnonzero(mask)[boundary]
        if rectilinear:
            bx, by = _axis_boundary_units(
                x[boundary_indices], y[boundary_indices], edges[selected], boundaries
            )
            gx[boundary_indices], gy[boundary_indices] = bx, by
            continue
        for index in boundary_indices:
            point = _fraction_point((x[index], y[index]))
            if point not in boundary_cache:
                direction = _subtract(*reversed(exact_edges[selected]))
                boundary_cache[point] = _boundary_unit(
                    point, direction, exact_boundaries
                )
            gx[index], gy[index] = boundary_cache[point]
    return gx, gy
