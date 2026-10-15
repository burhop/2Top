"""Finite-sample intersection evidence, never a root-position certificate."""

import math

import numpy as np

from .differentiation import estimate_gradient
from .numeric import real_array


def _finite_scalar(value):
    array = real_array(value)
    if array.size != 1:
        raise ValueError("A scalar field probe must return one real value")
    result = float(array.reshape(-1)[0])
    if not math.isfinite(result):
        raise ValueError("A scalar field probe must be finite")
    return result


def _positive_scale(value, name):
    if np.asarray(value).dtype.kind == "b":
        raise ValueError(f"{name} must be positive and finite")
    result = _finite_scalar(value)
    if result <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def diagnose_intersection_candidates(
    curve1,
    curve2,
    candidates,
    *,
    position_tolerance=1e-6,
    derivative_scale=None,
    trim_tolerance=None,
):
    """Inspect supplied points without searching, verifying or filtering roots.

    Every result is position_unverified, including exact-looking transverse or
    flat contacts. The row-normalized Jacobian condition and linearized step are
    local finite-sample evidence, not positional errors or bounds. A singular or
    derivative-uncertainty-dominated model has no reported correction.

    position_tolerance is a user spatial comparison scale, not a field residual
    threshold. derivative_scale optionally sets two positive stencil scales; it
    does not change the coordinate metric. trim_tolerance is passed to existing
    contains callbacks (None uses their default). No points are discarded or
    registered. Supplied points may be overlap samples; isolation is unassessed.

    Each field uses at most one direct residual and nine scalar gradient probes
    per point, plus an optional contains call. Public evaluators stay active;
    exceptions/nonfinite outputs produce unavailable evidence. Probes assume
    stable deterministic fields and may invoke caller code with side effects.
    """
    position_tolerance = _positive_scale(position_tolerance, "position_tolerance")
    if derivative_scale is not None:
        scale = real_array(derivative_scale)
        if scale.shape != (2,) or not np.isfinite(scale).all() or np.any(scale <= 0):
            raise ValueError("derivative_scale must contain two positive finite values")
        derivative_scale = tuple(float(v) for v in scale)
    if trim_tolerance is not None:
        trim_tolerance = _finite_scalar(trim_tolerance)
        if trim_tolerance < 0:
            raise ValueError("trim_tolerance must be nonnegative and finite")

    points = []
    for candidate in candidates:
        point = real_array(candidate)
        if point.shape != (2,) or not np.isfinite(point).all():
            raise ValueError("Candidates must be finite real coordinate pairs")
        points.append(tuple(float(v) for v in point))

    reports = []
    for point in points:
        fields = []
        warnings = []
        unit_rows, error_rows, normalized_residuals = [], [], []
        for index, curve in enumerate((curve1, curve2)):
            evaluations = 0

            def evaluate(x, y):
                nonlocal evaluations
                evaluations += 1
                return _finite_scalar(curve.evaluate(float(x), float(y)))

            residual, gradient, error = None, None, None
            try:
                residual = evaluate(*point)
            except Exception:
                warnings.append(f"field_{index + 1}_residual_unavailable")
            try:
                evidence = estimate_gradient(
                    evaluate,
                    np.asarray(point[0]),
                    np.asarray(point[1]),
                    scales=derivative_scale,
                )
                gradient = tuple(_finite_scalar(v) for v in evidence["gradient"])
                error = tuple(_finite_scalar(v) for v in evidence["error_estimate"])
                if any(v < 0 for v in error):
                    raise ValueError("Invalid derivative uncertainty")
            except Exception:
                gradient, error = None, None
                warnings.append(f"field_{index + 1}_derivative_unavailable")

            trim = "not_applicable"
            try:
                if hasattr(curve, "mask") and hasattr(curve, "base_curve"):
                    contains = (
                        curve.contains(*point)
                        if trim_tolerance is None
                        else curve.contains(*point, trim_tolerance)
                    )
                    boolean = np.asarray(contains)
                    if boolean.dtype.kind != "b" or boolean.size != 1:
                        raise ValueError("Trim evidence must be one actual boolean")
                    trim = "contains" if bool(boolean.reshape(-1)[0]) else "excluded"
                    if trim == "excluded":
                        warnings.append(f"field_{index + 1}_trim_excluded")
            except Exception:
                trim = "unavailable"
                warnings.append(f"field_{index + 1}_trim_unavailable")
            fields.append(
                dict(
                    residual=residual,
                    gradient=gradient,
                    gradient_error_estimate=error,
                    scalar_evaluations=evaluations,
                    trim=trim,
                )
            )

            if gradient is not None and error is not None and residual is not None:
                maximum = max(abs(v) for v in gradient)
                if maximum > 0:
                    length = math.hypot(*(v / maximum for v in gradient))
                    unit = tuple((v / maximum) / length for v in gradient)
                    try:
                        scaled_error = tuple((v / maximum) / length for v in error)
                        scaled_residual = (residual / maximum) / length
                        if not all(
                            math.isfinite(v) for v in (*scaled_error, scaled_residual)
                        ):
                            raise ValueError("Unrepresentable normalized evidence")
                    except (ValueError, OverflowError, ZeroDivisionError):
                        warnings.append(f"field_{index + 1}_normalization_unavailable")
                    else:
                        unit_rows.append(unit)
                        error_rows.append(scaled_error)
                        normalized_residuals.append(scaled_residual)
                else:
                    warnings.append(f"field_{index + 1}_zero_sampled_gradient")

        rcond, correction, correction_norm = None, None, None
        model = "unavailable"
        if len(unit_rows) == 2:
            matrix = np.asarray(unit_rows)
            singular = np.linalg.svd(matrix, compute_uv=False)
            rcond = float(singular[-1] / singular[0])
            uncertainty = math.hypot(*(v for row in error_rows for v in row))
            if rcond <= math.sqrt(np.finfo(float).eps):
                warnings.append("ill_conditioned_sampled_jacobian")
            if singular[-1] == 0 or singular[-1] <= 8 * uncertainty:
                model = "singular_or_derivative_unresolved"
                warnings.append("linearized_displacement_unavailable")
            else:
                try:
                    step = np.linalg.solve(matrix, -np.asarray(normalized_residuals))
                    magnitude = math.hypot(*step)
                    if not np.isfinite(step).all() or not math.isfinite(magnitude):
                        raise ValueError("Unrepresentable linearized displacement")
                    correction, correction_norm = (
                        tuple(float(v) for v in step),
                        magnitude,
                    )
                    model = "finite_sample_linearization"
                    if magnitude > position_tolerance:
                        warnings.append(
                            "linearized_displacement_exceeds_spatial_tolerance"
                        )
                except (ValueError, np.linalg.LinAlgError):
                    model = "unavailable"
                    warnings.append("linearized_displacement_unavailable")
        reports.append(
            dict(
                point=point,
                position_status="position_unverified",
                position_verified=False,
                positional_error_bound=None,
                isolated_root_status="not_established",
                fields=fields,
                normalized_jacobian_reciprocal_condition=rcond,
                local_model_status=model,
                linearized_displacement=correction,
                linearized_displacement_norm=correction_norm,
                warnings=warnings,
            )
        )
    return dict(
        method="sampled_intersection_diagnostics",
        certified=False,
        completeness="not_assessed",
        overlap="not_assessed",
        position_tolerance=position_tolerance,
        derivative_scale=derivative_scale,
        trim_tolerance=trim_tolerance,
        candidate_reports=reports,
        limits="All supplied candidates remain position-unverified. Condition and derivative-error estimates are heuristic; linearized displacement is not a distance-to-root estimate or bound. Finite probes cannot certify arbitrary fields, isolation, completeness or overlap. No search, filtering, registration or solver-tolerance changes occur.",
    )
