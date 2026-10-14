"""Representable central differences with a bounded Richardson estimate.

The reported error is an uncertainty heuristic, not a certified bound for an
arbitrary callback. Local scales must be supplied for unresolved small features.
"""

import numpy as np


def estimate_gradient(evaluate, x, y, scales=None, *, diagnostics=True):
    center = evaluate(x, y)
    derivatives, errors, steps = [], [], []
    for axis, coordinate in enumerate((x, y)):
        scale = np.maximum(1.0, np.abs(coordinate)) if scales is None else scales[axis]
        step = np.asarray(np.finfo(float).eps ** 0.2 * scale)
        step = np.broadcast_to(step, coordinate.shape)
        approximations, products, rounding = [], [], []
        actual_steps = []
        for factor in (1.0, 0.5):
            with np.errstate(over="ignore", invalid="ignore"):
                plus, minus = coordinate + factor * step, coordinate - factor * step
                plus = np.where(
                    plus == coordinate, np.nextafter(coordinate, np.inf), plus
                )
                minus = np.where(
                    minus == coordinate, np.nextafter(coordinate, -np.inf), minus
                )
                hp, hm = plus - coordinate, coordinate - minus
            fp = evaluate(plus, y) if axis == 0 else evaluate(x, plus)
            fm = evaluate(minus, y) if axis == 0 else evaluate(x, minus)
            with np.errstate(all="ignore"):
                span = hp + hm
                wp, wm = hm / span, hp / span
                approximation = wp * ((fp - center) / hp) + wm * ((center - fm) / hm)
                valid = np.isfinite(plus) & np.isfinite(minus) & (hp > 0) & (hm > 0)
                approximation = np.where(valid, approximation, np.nan)
                if diagnostics:
                    eps = np.finfo(float).eps
                    floor = np.nextafter(0.0, 1.0)
                    ep, em, ec = (
                        np.maximum(eps * np.abs(v), floor) for v in (fp, fm, center)
                    )
                    error = wp * ((ep + ec) / hp) + wm * ((em + ec) / hm)
                    error = np.where(valid, error, np.inf)
            approximations.append(approximation)
            # Keep the two factors separately; their product can underflow.
            products.append((hp, hm))
            if diagnostics:
                rounding.append(error)
                actual_steps.append((hp, hm))
        coarse, fine = approximations
        with np.errstate(all="ignore"):
            ratio = (products[0][0] / products[1][0]) * (
                products[0][1] / products[1][1]
            )
            correction = (fine - coarse) / (ratio - 1)
            extrapolated = fine + correction
            # A half-step can round to the same samples. Do not invent an order
            # estimate from two identical stencils; return its slope as uncertain.
            usable = (ratio > 1.5) & np.isfinite(extrapolated)
            value = np.where(usable, extrapolated, fine)
            if diagnostics:
                uncertainty = np.where(
                    usable, np.abs(correction) + rounding[0] + rounding[1], np.inf
                )
        derivatives.append(value)
        if diagnostics:
            errors.append(uncertainty)
            steps.append(actual_steps)
    return dict(
        gradient=tuple(derivatives),
        error_estimate=tuple(errors),
        steps=tuple(steps),
        method="central_richardson",
    )
