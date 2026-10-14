"""Internal real-valued broadcasting helpers for reusable field evaluators."""

import numpy as np


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
