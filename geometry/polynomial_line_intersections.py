"""Opt-in root isolation for unchanged native polynomial/line coefficient models.

Enclosures certify the stored rational coefficient model, not arbitrary fields.
Float residuals and exact-root trim membership are separate acceptance gates.
"""

import math

import numpy as np
import sympy as sp

from .implicit_curve import ImplicitCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve

_DEGREE = 8
_BITS = 4096
_NODES = 512


def _small_rational(value):
    return (
        isinstance(value, sp.Rational)
        and int(value.p).bit_length() <= _BITS
        and int(value.q).bit_length() <= _BITS
    )


def _structure(expression, variables, budget):
    budget[0] -= 1
    if budget[0] < 0:
        return None
    if isinstance(expression, sp.Float):
        _, _, exponent, bits = expression._mpf_
        return (
            0 if expression._prec <= _BITS and abs(exponent) + bits <= _BITS else None
        )
    if isinstance(expression, sp.Rational):
        return 0 if _small_rational(expression) else None
    if expression in variables:
        return 1
    if expression.is_Add or expression.is_Mul:
        degrees = [_structure(arg, variables, budget) for arg in expression.args]
        if any(degree is None for degree in degrees):
            return None
        degree = max(degrees) if expression.is_Add else sum(degrees)
    elif (
        expression.is_Pow
        and isinstance(expression.exp, sp.Integer)
        and 0 <= expression.exp <= _DEGREE
    ):
        degree = _structure(expression.base, variables, budget)
        if degree is None:
            return None
        degree *= int(expression.exp)
    else:
        return None
    return degree if degree <= _DEGREE else None


def _capture(curve):
    wrappers, seen = [], set()
    while isinstance(curve, TrimmedImplicitCurve):
        if (
            id(curve) in seen
            or getattr(curve.evaluate, "__func__", None)
            is not TrimmedImplicitCurve.evaluate
        ):
            return None
        seen.add(id(curve))
        wrappers.append(curve)
        curve = curve.base_curve
    if (
        not isinstance(curve, ImplicitCurve)
        or getattr(curve.evaluate, "__func__", None) is not ImplicitCurve.evaluate
        or getattr(type(curve), "expression", None) is not ImplicitCurve.expression
        or getattr(type(curve), "variables", None) is not ImplicitCurve.variables
        or hasattr(curve, "base_curve")
        or hasattr(curve, "mask")
    ):
        return None
    expression, variables = curve.expression, curve.variables
    if (
        len(variables) != 2
        or not all(isinstance(v, sp.Symbol) for v in variables)
        or variables[0] == variables[1]
        or not isinstance(expression, sp.Expr)
    ):
        return None
    kernel = curve._eval_func
    if kernel is not None and (
        kernel is not getattr(curve, "_native_eval_func", None)
        or (expression, variables) != getattr(curve, "_native_eval_state", None)
    ):
        return None
    return curve, expression, variables, tuple(wrappers)


def _unchanged(curve, captured):
    current = _capture(curve)
    return (
        current is not None
        and current[0] is captured[0]
        and current[1:3] == captured[1:3]
        and len(current[3]) == len(captured[3])
        and all(a is b for a, b in zip(current[3], captured[3]))
    )


def _polynomial(captured, coordinates):
    _, expression, variables, _ = captured
    if _structure(expression, variables, [_NODES]) is None:
        return None
    exact = expression.xreplace(
        {value: sp.Rational(value) for value in expression.atoms(sp.Float)}
    )
    polynomial = sp.Poly(exact, *variables, domain=sp.QQ)
    if not all(_small_rational(c) for c in polynomial.coeffs()):
        return None
    return sp.Poly.from_dict(polynomial.as_dict(), coordinates, domain=sp.QQ)


def _positive(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be positive and finite")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be positive and finite") from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def _separate_intervals(polynomial, intervals):
    """SymPy intervals may touch at a rational separator that is not a root."""
    square_free = polynomial.sqf_part()
    for _ in range(64):
        if not all(
            _small_rational(value) for interval, _ in intervals for value in interval
        ):
            return None
        touching = set()
        for i in range(len(intervals) - 1):
            if intervals[i][0][1] >= intervals[i + 1][0][0]:
                touching.update((i, i + 1))
        if not touching:
            return intervals
        for i in touching:
            (lower, upper), multiplicity = intervals[i]
            if lower != upper:
                refined = square_free.refine_root(
                    lower, upper, eps=(upper - lower) / 4, steps=16, fast=True
                )
                intervals[i] = refined, multiplicity
    return None


def _residual(curve, point):
    try:
        value = np.asarray(curve.evaluate(*point))
        if value.shape != () or value.dtype.kind not in "iuf":
            return None
        value = float(value)
        return value if math.isfinite(value) else None
    except Exception:
        return None


def _contains(wrapper, point, tolerance):
    try:
        value = (
            wrapper.contains(*point)
            if tolerance is None
            else wrapper.contains(*point, tolerance)
        )
        return bool(value) if isinstance(value, (bool, np.bool_)) else None
    except Exception:
        return None


def find_polynomial_line_intersections(
    first,
    second,
    *,
    position_tolerance=1e-8,
    residual_tolerance=1e-8,
    trim_tolerance=None,
):
    """Isolate all real roots of a bounded native polynomial/line model.

    Either input must be a nonzero affine line; the other has degree <= 8.
    Float coefficients mean their exact stored binary values. Distinct model
    roots retain separate rational enclosures and multiplicities. Accepted
    float points meet an exact L-infinity enclosure bound and actual finite
    residual checks. Arbitrary trims accept only an exactly representable model
    root with true containment at every wrapper; other trim membership remains
    unverified. No legacy fallback, search window, scene mutation or registration.

    Structural/coefficient caps limit inputs, not wall-clock isolation time.
    Completeness concerns the captured untrimmed coefficient model only. A
    non-isolated model does not enumerate intersections selected by masks.
    """
    position_tolerance = _positive(position_tolerance, "position_tolerance")
    residual_tolerance = _positive(residual_tolerance, "residual_tolerance")
    if trim_tolerance is not None:
        trim_tolerance = _positive(trim_tolerance, "trim_tolerance")
    requested = sp.Rational(position_tolerance)
    report = {
        "status": "unsupported",
        "model_scope": "exact_stored_coefficients_untrimmed",
        "model_root_completeness": False,
        "trimmed_root_completeness": False,
        "position_metric": "L_infinity",
        "position_tolerance": position_tolerance,
        "points": [],
        "roots": [],
        "reason": None,
    }
    captures = [_capture(first), _capture(second)]
    if any(c is None for c in captures):
        report["reason"] = "native_model_unavailable"
        return report
    x, y, t = sp.Dummy("x"), sp.Dummy("y"), sp.Dummy("t")
    try:
        polynomials = [_polynomial(c, (x, y)) for c in captures]
        if any(p is None for p in polynomials):
            report["reason"] = "polynomial_limits_or_coefficients"
            return report
        line_index = next(
            (i for i, p in enumerate(polynomials) if p.total_degree() == 1),
            None,
        )
        if line_index is None:
            report["reason"] = "nonzero_affine_line_required"
            return report
        line = polynomials[line_index]
        a, b, c = [line.coeff_monomial(m) for m in (x, y, 1)]
        if abs(b) >= abs(a):
            coordinates = (t, -a / b * t - c / b)
            report["parameter_axis"] = "x"
        else:
            coordinates = (-b / a * t - c / a, t)
            report["parameter_axis"] = "y"
        restricted = sp.Poly(
            polynomials[1 - line_index]
            .as_expr()
            .subs({x: coordinates[0], y: coordinates[1]}, simultaneous=True),
            t,
            domain=sp.QQ,
        )
        if not all(_small_rational(v) for v in restricted.coeffs()):
            report["reason"] = "elimination_coefficient_limit"
            return report
        if restricted.is_zero:
            report.update(status="non_isolated_model", reason="line_component")
            return report
        restricted = restricted.clear_denoms()[1].primitive()[1]
        if not all(_small_rational(v) for v in restricted.coeffs()):
            report["reason"] = "normalized_coefficient_limit"
            return report
        intervals = restricted.intervals(eps=requested / 16)
        intervals = _separate_intervals(restricted, intervals)
        if intervals is None:
            report["reason"] = "root_enclosures_not_separated"
            return report
    except (TypeError, ValueError, OverflowError, sp.PolynomialError):
        report["reason"] = "polynomial_model_unavailable"
        return report
    report.update(status="isolated_model", model_root_completeness=True)
    wrappers = [wrapper for captured in captures for wrapper in captured[3]]
    for (lower, upper), multiplicity in intervals:
        bounds = [
            sorted((coordinate.subs(t, lower), coordinate.subs(t, upper)))
            for coordinate in coordinates
        ]
        if not all(_small_rational(value) for bound in bounds for value in bound):
            report.update(
                status="unsupported",
                model_root_completeness=False,
                roots=[],
                reason="coordinate_enclosure_limit",
            )
            return report
        record = {
            "multiplicity": multiplicity,
            "coordinate_intervals": [[str(v) for v in bound] for bound in bounds],
            "point": None,
            "position_bound": None,
            "position_bound_exact": None,
            "representative_residuals": [None, None],
            "representative_contains": [],
            "root_trim_membership": "unverified" if wrappers else "not_applicable",
            "accepted": False,
            "reasons": [],
        }
        report["roots"].append(record)
        try:
            point = tuple(float((lo + hi) / 2) for lo, hi in bounds)
            if not all(math.isfinite(v) for v in point):
                raise ValueError("nonfinite representative")
        except (ValueError, OverflowError):
            record["reasons"].append("float_representative_unavailable")
            continue
        record["point"] = point
        bound = max(
            abs(sp.Rational(value) - endpoint)
            for value, endpoints in zip(point, bounds)
            for endpoint in endpoints
        )
        record["position_bound_exact"] = str(bound)
        # Exact rational value above is authoritative, including underflow cases.
        try:
            approximate_bound = float(bound)
        except OverflowError:
            approximate_bound = math.inf
        if math.isfinite(approximate_bound) and sp.Rational(approximate_bound) < bound:
            approximate_bound = math.nextafter(approximate_bound, math.inf)
        record["position_bound"] = (
            approximate_bound if math.isfinite(approximate_bound) else None
        )
        if bound > requested:
            record["reasons"].append("requested_position_bound_not_met")
        record["representative_residuals"] = [
            _residual(curve, point) for curve in (first, second)
        ]
        if any(
            value is None or abs(value) > residual_tolerance
            for value in record["representative_residuals"]
        ):
            record["reasons"].append("representative_residual_not_accepted")
        checks = [_contains(wrapper, point, trim_tolerance) for wrapper in wrappers]
        record["representative_contains"] = checks
        if wrappers:
            if bound != 0 or any(value is None for value in checks):
                record["reasons"].append("root_trim_membership_unverified")
            elif all(checks):
                record["root_trim_membership"] = "exact_point_accepted"
            else:
                record["root_trim_membership"] = "exact_point_excluded"
                record["reasons"].append("exact_root_excluded_by_trim")
        record["accepted"] = not record["reasons"]
    # A callback can invalidate any captured model, including earlier records.
    if not all(_unchanged(curve, c) for curve, c in zip((first, second), captures)):
        report.update(status="model_changed", model_root_completeness=False)
        report["reason"] = "model_changed_during_validation"
        for record in report["roots"]:
            record["accepted"] = False
            record["reasons"].append("model_changed_during_validation")
    points = {}
    for record in report["roots"]:
        if record["point"] is not None:
            points.setdefault(record["point"], []).append(record)
    for records in points.values():
        if len(records) > 1:
            for record in records:
                record["accepted"] = False
                record["reasons"].append("float_representative_collision")
    report["points"] = [r["point"] for r in report["roots"] if r["accepted"]]
    return report
