"""Opt-in root isolation for unchanged native polynomial/line coefficient models.

Enclosures certify the stored rational coefficient model, not arbitrary fields.
Float residuals and exact-root trim membership are separate acceptance gates.
"""

import math

import numpy as np
import sympy as sp

from .implicit_curve import ImplicitCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from .rectangle_mask import RectangleMask, _is_native_rectangle

_DEGREE = 8
_BITS = 4096
_NODES = 512
_NATIVE_CONTAINS = TrimmedImplicitCurve.contains
_MISSING = object()


def _trim_state(wrapper):
    try:
        return _trim_state_values(wrapper)
    except Exception:
        return None


def _trim_state_values(wrapper):
    """Snapshot ordinary predicate edits, including mutable scalar bbox values."""
    contains = getattr(wrapper, "contains", None)
    mask = getattr(wrapper, "mask", None)
    box = []
    references = [mask, contains]
    for name in ("_xmin", "_xmax", "_ymin", "_ymax"):
        value = getattr(wrapper, name, _MISSING)
        references.append(value)
        if (
            isinstance(value, np.ndarray)
            and value.size <= 1
            and value.dtype.kind in "biuf"
        ):
            box.append((value.dtype.str, value.shape, value.tobytes()))
        else:
            box.append(id(value))
    try:
        rectangle = (
            (mask.bounds, mask._float_bounds, id(type(mask).__call__))
            if type(mask) is RectangleMask
            else None
        )
    except AttributeError:
        rectangle = None
    signature = (
        id(mask),
        id(getattr(contains, "__func__", contains)),
        id(getattr(contains, "__self__", None)),
        tuple(box),
        rectangle,
    )
    # Retain compared objects so replacement cannot reuse a freed object's id.
    return signature, references


def _same_trim_state(first, second):
    if first is None or second is None:
        return first is second
    return first[0] == second[0]


def _rectangle_domain(wrapper, coordinates, parameter):
    try:
        return _rectangle_domain_values(wrapper, coordinates, parameter)
    except Exception:
        return None


def _rectangle_domain_values(wrapper, coordinates, parameter):
    if (
        getattr(getattr(wrapper, "contains", None), "__func__", None)
        is not _NATIVE_CONTAINS
        or not _is_native_rectangle(getattr(wrapper, "mask", None))
        or any(
            getattr(wrapper, name, _MISSING) is not None
            for name in ("_xmin", "_xmax", "_ymin", "_ymax")
        )
    ):
        return None
    lower, upper = None, None
    for coordinate, lo, hi in zip(
        coordinates, wrapper.mask.bounds[::2], wrapper.mask.bounds[1::2]
    ):
        slope, intercept = coordinate.diff(parameter), coordinate.subs(parameter, 0)
        if slope == 0:
            if not lo <= intercept <= hi:
                return sp.Integer(1), sp.Integer(0)
            continue
        a, b = sorted(((lo - intercept) / slope, (hi - intercept) / slope))
        if not _small_rational(a) or not _small_rational(b):
            return None
        lower = a if lower is None else max(lower, a)
        upper = b if upper is None else min(upper, b)
    return lower, upper


def _compare_root(polynomial, interval, threshold):
    """Exact side of one isolated root relative to a rational threshold."""
    lower, upper = interval
    if not _small_rational(threshold):
        return None
    if lower == upper:
        return int(bool(lower > threshold)) - int(bool(lower < threshold))
    if threshold < lower:
        return 1
    if threshold > upper:
        return -1
    endpoint_roots = [v for v in (lower, upper) if polynomial.eval(v) == 0]
    if len(endpoint_roots) == 1:
        root = endpoint_roots[0]
        return int(bool(root > threshold)) - int(bool(root < threshold))
    if endpoint_roots:
        return None
    if polynomial.eval(threshold) == 0:
        return 0
    if threshold == lower:
        return 1
    if threshold == upper:
        return -1
    try:
        count = polynomial.count_roots(lower, threshold)
    except (TypeError, ValueError, OverflowError, sp.PolynomialError):
        return None
    return -1 if count == 1 else (1 if count == 0 else None)


def _rectangle_membership(polynomial, interval, domain):
    lower, upper = domain
    if lower > upper:
        return "excluded"
    left = _compare_root(polynomial, interval, lower)
    right = _compare_root(polynomial, interval, upper)
    if (left is not None and left < 0) or (right is not None and right > 0):
        return "excluded"
    return "included" if left is not None and right is not None else "unverified"


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
    try:
        current = _capture(curve)
    except Exception:
        return False
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
    residual checks. Native RectangleMask trims have exact model-root membership
    proofs. Arbitrary trims require exactly representable roots; unresolved trim
    membership remains unverified. Every accepted float also needs actual true
    containment at every wrapper. No legacy fallback or scene mutation.

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
    try:
        captures = [_capture(first), _capture(second)]
    except Exception:
        report["reason"] = "native_model_unavailable"
        return report
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
    trim_states = [_trim_state(wrapper) for wrapper in wrappers]
    domains = [_rectangle_domain(wrapper, coordinates, t) for wrapper in wrappers]
    square_free = (
        restricted.sqf_part() if any(domain is not None for domain in domains) else None
    )
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
            "root_trim_checks": [],
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
            for domain, actual, state in zip(domains, checks, trim_states):
                if state is None:
                    status, kind = "unverified", "callback"
                elif domain is not None:
                    status = _rectangle_membership(square_free, (lower, upper), domain)
                    kind = "native_rectangle"
                else:
                    status = (
                        "unverified"
                        if bound != 0 or actual is None
                        else ("included" if actual else "excluded")
                    )
                    kind = "callback"
                record["root_trim_checks"].append({"kind": kind, "status": status})
            statuses = [evidence["status"] for evidence in record["root_trim_checks"]]
            if "excluded" in statuses:
                record["root_trim_membership"] = (
                    "exact_point_excluded" if bound == 0 else "model_root_excluded"
                )
                record["reasons"].append(
                    "exact_root_excluded_by_trim"
                    if bound == 0
                    else "model_root_excluded_by_trim"
                )
            elif all(status == "included" for status in statuses):
                record["root_trim_membership"] = (
                    "exact_point_accepted" if bound == 0 else "model_root_included"
                )
            else:
                record["reasons"].append("root_trim_membership_unverified")
            if not all(value is True for value in checks):
                record["reasons"].append("representative_trim_not_accepted")
        record["accepted"] = not record["reasons"]
    # A callback can invalidate any captured model, including earlier records.
    if not all(_unchanged(curve, c) for curve, c in zip((first, second), captures)):
        report.update(status="model_changed", model_root_completeness=False)
        report["reason"] = "model_changed_during_validation"
        for record in report["roots"]:
            record["accepted"] = False
            record["root_trim_membership"] = "unverified"
            for evidence in record["root_trim_checks"]:
                evidence["status"] = "unverified"
            record["reasons"].append("model_changed_during_validation")
    if any(
        not _same_trim_state(_trim_state(wrapper), state)
        for wrapper, state in zip(wrappers, trim_states)
    ):
        if report["status"] != "model_changed":
            report.update(
                status="trim_changed", reason="trim_changed_during_validation"
            )
        for record in report["roots"]:
            record["accepted"] = False
            record["root_trim_membership"] = "unverified"
            for evidence in record["root_trim_checks"]:
                evidence["status"] = "unverified"
            record["reasons"].append("trim_changed_during_validation")
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
