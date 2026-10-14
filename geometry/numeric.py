"""Internal real-valued broadcasting helpers for reusable field evaluators."""

import numpy as np


def _difference_with_error(a, b):
    """TwoDiff: recover the low part of a finite binary64 subtraction."""
    difference = a - b
    virtual_b = a - difference
    virtual_a = difference + virtual_b
    return difference, (a - virtual_a) + (virtual_b - b)


def _product_error(a, b, product):
    """Dekker product residual for separately normalized finite operands."""
    splitter = 134217729.0
    split_a, split_b = splitter * a, splitter * b
    high_a, high_b = split_a - (split_a - a), split_b - (split_b - b)
    low_a, low_b = a - high_a, b - high_b
    return (
        (high_a * high_b - product) + high_a * low_b + low_a * high_b
    ) + low_a * low_b


def _precise_segment_distance(x, y, endpoints):
    """Rare overflow/cancellation path, 80 guard digits and a 1600-digit cap."""
    from decimal import Decimal, localcontext

    with localcontext() as context:
        ax, ay, bx, by = [Decimal.from_float(float(v)) for v in endpoints.ravel()]
        px, py = Decimal.from_float(float(x)), Decimal.from_float(float(y))
        exponents = [v.adjusted() for v in (ax, ay, bx, by, px, py) if v]
        spread = max(exponents) - min(exponents) if exponents else 0
        # Squared norm corrections can decide a half-subnormal rounding tie.
        context.prec = min(1600, 80 + 2 * spread)
        dx, dy = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        length_sq = dx * dx + dy * dy
        projection = wx * dx + wy * dy
        if length_sq == 0 or projection <= 0:
            value = (wx * wx + wy * wy).sqrt()
        elif projection >= length_sq:
            rx, ry = px - bx, py - by
            value = (rx * rx + ry * ry).sqrt()
        else:
            determinant = abs(wx * dy - wy * dx)
            value = determinant / length_sq.sqrt() if determinant else Decimal(0)
        return float(value)


def segment_distance(x, y, start, end):
    """Euclidean distance to a finite segment, with true point degeneracy.

    Binary scaling avoids squared lengths and overflowing projection ratios.
    Axis-aligned segments use clamping directly. A bounded Decimal fallback
    resolves overflowing differences, erased components and severe cancellation.
    Infinity means a distance outside binary64 range; invalid endpoints raise.
    """
    endpoints = real_array([start, end])
    if endpoints.shape != (2, 2) or not np.isfinite(endpoints).all():
        raise ValueError("Distance segment endpoints must be finite coordinate pairs")
    x, y = np.broadcast_arrays(real_array(x), real_array(y))
    shape = x.shape
    x, y = x.ravel(), y.ravel()
    valid = np.isfinite(x) & np.isfinite(y)
    result = np.full(x.shape, np.nan)
    if not np.any(valid):
        return result.reshape(shape)
    px, py = x[valid], y[valid]
    (ax, ay), (bx, by) = endpoints
    with np.errstate(all="ignore"):
        if ay == by:
            distance = np.hypot(px - np.clip(px, min(ax, bx), max(ax, bx)), py - ay)
        elif ax == bx:
            distance = np.hypot(px - ax, py - np.clip(py, min(ay, by), max(ay, by)))
        else:
            dx, error_dx = _difference_with_error(bx, ax)
            dy, error_dy = _difference_with_error(by, ay)
            wx, error_wx = _difference_with_error(px, ax)
            wy, error_wy = _difference_with_error(py, ay)
            if not np.isfinite([dx, dy]).all():
                distance = np.array(
                    [
                        _precise_segment_distance(qx, qy, endpoints)
                        for qx, qy in zip(px, py)
                    ]
                )
            else:
                exponent = np.frexp(max(abs(dx), abs(dy)))[1]
                ux, uy = np.ldexp(dx, -exponent), np.ldexp(dy, -exponent)
                low_dx, low_dy = (
                    np.ldexp(error_dx, -exponent),
                    np.ldexp(error_dy, -exponent),
                )
                query_exponent = np.frexp(np.maximum(np.abs(wx), np.abs(wy)))[1]
                sx, sy = np.ldexp(wx, -query_exponent), np.ldexp(wy, -query_exponent)
                low_wx, low_wy = (
                    np.ldexp(error_wx, -query_exponent),
                    np.ldexp(error_wy, -query_exponent),
                )
                dot_x, dot_y = sx * ux, sy * uy
                cross_x, cross_y = sx * uy, sy * ux
                dot = dot_x + dot_y
                cross, subtract_error = _difference_with_error(cross_x, cross_y)
                cross += (
                    _product_error(sx, uy, cross_x)
                    - _product_error(sy, ux, cross_y)
                    + subtract_error
                )
                # Retain coordinate/edge subtraction low parts in the determinant.
                cross += (
                    sx * low_dy
                    + low_wx * uy
                    + low_wx * low_dy
                    - sy * low_dx
                    - low_wy * ux
                    - low_wy * low_dx
                )
                t = np.ldexp(dot / (ux * ux + uy * uy), query_exponent - exponent)
                distance = np.where(
                    dot <= 0,
                    np.hypot(wx, wy),
                    np.where(
                        t >= 1,
                        np.hypot(px - bx, py - by),
                        np.ldexp(np.abs(cross) / np.hypot(ux, uy), query_exponent),
                    ),
                )
                epsilon = 64 * np.finfo(float).eps
                dot_scale = np.abs(dot_x) + np.abs(dot_y)
                cross_scale = np.abs(cross_x) + np.abs(cross_y)
                uncertain = (
                    ~np.isfinite(wx)
                    | ~np.isfinite(wy)
                    | np.isnan(distance)
                    | ((sx == 0) & (wx != 0))
                    | ((sy == 0) & (wy != 0))
                    | ((dot_scale > 0) & (np.abs(dot) <= epsilon * dot_scale))
                    | ((cross_scale > 0) & (np.abs(cross) <= epsilon * cross_scale))
                    # A rounded t=1 can erase a valid interior query near B.
                    | (np.isfinite(t) & (np.abs(t - 1) <= epsilon))
                    | (distance < np.finfo(float).tiny)
                    | ~np.isfinite(error_wx)
                    | ~np.isfinite(error_wy)
                    | ((low_wx == 0) & (error_wx != 0))
                    | ((low_wy == 0) & (error_wy != 0))
                )
                for left, right, product in (
                    (sx, ux, dot_x),
                    (sy, uy, dot_y),
                    (sx, uy, cross_x),
                    (sy, ux, cross_y),
                ):
                    uncertain |= (
                        (left != 0)
                        & (right != 0)
                        & (np.abs(product) < np.finfo(float).tiny)
                    )
                if (ux == 0 and dx != 0) or (uy == 0 and dy != 0):
                    uncertain[:] = True
                if (
                    not np.isfinite([error_dx, error_dy]).all()
                    or (low_dx == 0 and error_dx != 0)
                    or (low_dy == 0 and error_dy != 0)
                ):
                    uncertain[:] = True
                for index in np.flatnonzero(uncertain):
                    distance[index] = _precise_segment_distance(
                        px[index], py[index], endpoints
                    )
    result[valid] = distance
    return result.reshape(shape)


def real_array(value):
    array = np.asarray(value)
    if array.dtype.kind not in "biuf":
        raise ValueError("Field inputs and outputs must be real numeric values")
    return array.astype(float, copy=False)


def broadcast_coordinates(x, y):
    scalar = np.isscalar(x) and np.isscalar(y)
    x, y = np.broadcast_arrays(real_array(x), real_array(y))
    return x, y, scalar


def field_result(value, shape, scalar):
    result = real_array(value)
    if result.shape != shape:
        result = np.broadcast_to(result, shape).copy()
    return float(result) if scalar else result


def blend_terms(first, second, alpha, *, gradient=False):
    """Scaled half-difference and rationalized smooth-min correction.

    Avoid squared field magnitudes, overflowing sums/differences, and an
    absolute denominator floor. Undefined nonfinite operands propagate NaN.
    """
    first, second = np.asarray(first), np.asarray(second)
    with np.errstate(over="ignore", invalid="ignore"):
        difference = first - second
    # Only halve overflowing differences. Keeping finite differences intact
    # also preserves the gradient weights of subnormal operands and alpha.
    overflow = np.isinf(difference) & np.isfinite(first) & np.isfinite(second)
    if np.any(overflow):
        difference = np.where(overflow, 0.5 * first - 0.5 * second, difference)
        effective_alpha = np.where(overflow, 0.5 * alpha, alpha)
    else:
        effective_alpha = alpha
    scale = np.maximum(np.abs(difference), effective_alpha)
    d = difference / scale
    h = effective_alpha / scale
    root = np.hypot(d, h)
    factor = h / (root + np.abs(d))
    correction = (0.5 * alpha) * factor
    minimum = np.minimum(first, second)
    value = minimum - correction
    # Rescale subnormal subtraction and round once on return to float64.
    # Without this, half-alpha can round before an equally small field value.
    if alpha < np.finfo(float).tiny:
        subnormal = np.abs(minimum) < np.finfo(float).tiny
        if np.any(subnormal):
            value = np.array(value, copy=True)
            value[subnormal] = np.ldexp(
                np.ldexp(minimum[subnormal], 1022)
                - (0.5 * np.ldexp(alpha, 1022)) * factor[subnormal],
                -1022,
            )
    if not gradient:
        return value
    small_weight = (0.5 * h / root) * factor
    first_weight = np.where(d >= 0, small_weight, 1 - small_weight)
    second_weight = np.where(d >= 0, 1 - small_weight, small_weight)
    return value, first_weight, second_weight
