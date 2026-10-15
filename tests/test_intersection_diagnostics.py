"""Analytic/Decimal checks for explicitly uncertified intersection evidence."""

from decimal import Decimal, localcontext
import json
import math

import numpy as np
import pytest
import sympy as sp

from geometry import ImplicitCurve, ProceduralCurve, TrimmedImplicitCurve
from geometry import diagnose_intersection_candidates as diagnose
from geometry.curve_intersections import find_curve_intersections


X, Y = sp.symbols("x y")


def curve(expression):
    return ImplicitCurve(expression, (X, Y))


def only(first, second, point, **kwargs):
    report = diagnose(first, second, [point], **kwargs)
    json.dumps(report, allow_nan=False)
    assert report["certified"] is False
    assert report["completeness"] == report["overlap"] == "not_assessed"
    item = report["candidate_reports"][0]
    assert item["position_status"] == "position_unverified"
    assert item["position_verified"] is False
    assert item["positional_error_bound"] is None
    assert item["isolated_root_status"] == "not_established"
    return item


@pytest.mark.parametrize(
    "first_scale,second_scale", [(1, 1), (1e-200, 1e200), (-1e200, -1e-200), (3, -7)]
)
@pytest.mark.parametrize("reverse", [False, True])
def test_transverse_linear_correction_uses_scaled_residual_and_jacobian(
    first_scale, second_scale, reverse
):
    first, second = (
        curve(sp.Float(first_scale) * (X - 1)),
        curve(sp.Float(second_scale) * (Y - 2)),
    )
    if reverse:
        first, second = second, first
    item = only(first, second, (1.1, 2.2))
    np.testing.assert_allclose(
        item["linearized_displacement"], [-0.1, -0.2], rtol=1e-10
    )
    assert item["normalized_jacobian_reciprocal_condition"] == pytest.approx(1)
    assert "linearized_displacement_exceeds_spatial_tolerance" in item["warnings"]


@pytest.mark.parametrize("scale", [1e-100, 1.0, -1e100])
@pytest.mark.parametrize("geometric_scale", [0.001, 1.0, 1000.0])
def test_x8_nonroot_has_tiny_residual_but_large_linear_step(scale, geometric_scale):
    first = curve(sp.Float(scale) * (Y / geometric_scale - (X / geometric_scale) ** 8))
    second = curve(sp.Float(-3 * scale) * Y / geometric_scale)
    point = (0.04 * geometric_scale, 0.0)
    item = only(
        first,
        second,
        point,
        derivative_scale=(geometric_scale, geometric_scale),
        position_tolerance=1e-6 * geometric_scale,
    )
    # Independent univariate Newton quotient x**8/(8*x**7) = x/8.
    np.testing.assert_allclose(
        item["linearized_displacement"],
        [-0.005 * geometric_scale, 0],
        rtol=1e-6,
        atol=1e-20,
    )
    assert item["linearized_displacement_norm"] > 0.004 * geometric_scale
    assert item["normalized_jacobian_reciprocal_condition"] < 1e-8
    assert "ill_conditioned_sampled_jacobian" in item["warnings"]


def test_exact_reproduced_x8_candidates_are_never_position_verified():
    first, second = curve(Y - X**8), curve(Y)
    points = find_curve_intersections(
        first, second, search_range=2, grid_resolution=50, tolerance=1e-8
    )
    assert len(points) == 4
    report = diagnose(first, second, points)
    assert [item["point"] for item in report["candidate_reports"]] == points
    with localcontext() as context:
        context.prec = 160
        for point, item in zip(points, report["candidate_reports"]):
            px, py = map(Decimal.from_float, point)
            # y=0 and x**8=0 imply the only analytic root is the origin.
            actual_error = (px * px + py * py).sqrt()
            assert abs(py - px**8) < Decimal("1e-8") and abs(py) < Decimal("1e-8")
            assert (
                not item["position_verified"] and item["positional_error_bound"] is None
            )
            if actual_error > Decimal("0.03"):
                assert item["linearized_displacement_norm"] > 0.004
                assert "ill_conditioned_sampled_jacobian" in item["warnings"]
                assert (
                    Decimal.from_float(item["linearized_displacement_norm"])
                    < actual_error
                )


@pytest.mark.parametrize("power", [2, 4, 8])
def test_true_flat_contact_is_retained_as_uncertain_with_no_zero_error_bound(power):
    item = only(curve(Y - X**power), curve(Y), (0.0, 0.0))
    assert item["point"] == (0.0, 0.0)
    assert item["local_model_status"] == "singular_or_derivative_unresolved"
    assert item["linearized_displacement"] is None
    assert item["linearized_displacement_norm"] is None


def test_transverse_exact_root_still_is_not_a_certificate():
    item = only(curve(X - 1), curve(Y - 2), (1.0, 2.0))
    assert item["linearized_displacement_norm"] == 0
    assert item["position_verified"] is False


def test_two_nearby_high_order_crossings_are_neither_rejected_nor_merged():
    height = sp.Rational(1, 25) ** 8
    points = [(-0.04, float(height)), (0.04, float(height))]
    report = diagnose(curve(Y - X**8), curve(Y - height), points)
    assert len(report["candidate_reports"]) == 2
    assert [item["point"] for item in report["candidate_reports"]] == points
    assert all(not item["position_verified"] for item in report["candidate_reports"])


def test_even_power_near_miss_does_not_get_a_position_claim():
    # y=-delta cannot meet y=x**8 for any real x, even if residual <1e-8.
    delta = sp.Rational(1, 10**12)
    item = only(curve(Y - X**8), curve(Y + delta), (0.0, -float(delta)))
    assert item["fields"][0]["residual"] == pytest.approx(-float(delta))
    assert item["linearized_displacement"] is None


@pytest.mark.parametrize("mask_kind", ["closed", "strict", "reject", "raises"])
def test_scalar_trim_callbacks_report_contains_exclusion_or_unavailable(mask_kind):
    def mask(x, y):
        assert isinstance(x, float) and isinstance(y, float)
        if mask_kind == "raises":
            raise RuntimeError("mask failure")
        return mask_kind == "closed" or (mask_kind == "strict" and x > 0)

    line = TrimmedImplicitCurve(curve(Y), mask, xmin=0, xmax=1, ymin=0, ymax=0)
    item = only(curve(Y - X**8), line, (0.0, 0.0), trim_tolerance=1e-8)
    expected = (
        "contains"
        if mask_kind == "closed"
        else "unavailable"
        if mask_kind == "raises"
        else "excluded"
    )
    assert item["fields"][1]["trim"] == expected
    assert item["point"] == (0.0, 0.0)


@pytest.mark.parametrize("kind", ["procedural", "public", "private"])
def test_active_evaluator_is_authoritative_and_symbolic_gradient_is_not_used(kind):
    def actual(x, y):
        return y - x**8

    first = ProceduralCurve(actual) if kind == "procedural" else curve(X)
    if kind == "public":
        first.evaluate = actual
    elif kind == "private":
        first.evaluate(1, 2)
        first._eval_func = actual

    def forbidden(*args):
        raise AssertionError("must probe actual field, not a stored derivative")

    first.gradient = forbidden
    item = only(first, curve(Y), (0.04, 0))
    assert item["linearized_displacement"][0] == pytest.approx(-0.005, rel=1e-6)


def test_scalar_only_evaluators_receive_float_probes_and_have_bounded_cost():
    class ScalarField:
        def __init__(self, axis):
            self.axis, self.calls = axis, 0

        def evaluate(self, x, y):
            assert isinstance(x, float) and isinstance(y, float)
            self.calls += 1
            return (x, y)[self.axis]

    first, second = ScalarField(0), ScalarField(1)
    item = only(first, second, (0.1, 0.2))
    assert first.calls == second.calls == 10
    assert all(field["scalar_evaluations"] == 10 for field in item["fields"])


@pytest.mark.parametrize("tolerance,expected", [(None, "contains"), (0.5, "excluded")])
def test_trim_default_is_not_replaced_and_explicit_tolerance_is_positional(
    tolerance, expected
):
    trimmed = TrimmedImplicitCurve(curve(Y), lambda x, y: True)
    trimmed.contains = lambda x, y, custom_tolerance=0.25: custom_tolerance == 0.25
    item = only(curve(X), trimmed, (0, 0), trim_tolerance=tolerance)
    assert item["fields"][1]["trim"] == expected


@pytest.mark.parametrize("value", [np.nan, "bad", 1, None, np.array([True, False])])
def test_invalid_trim_truthiness_is_not_affirmative_evidence(value):
    trimmed = TrimmedImplicitCurve(curve(Y), lambda x, y: True)
    trimmed.contains = lambda *args: value
    item = only(curve(X), trimmed, (0, 0))
    assert item["fields"][1]["trim"] == "unavailable"


@pytest.mark.parametrize(
    "value", [True, np.bool_(True), np.array(True), np.array([True])]
)
def test_actual_single_boolean_trim_outputs_are_supported(value):
    trimmed = TrimmedImplicitCurve(curve(Y), lambda x, y: True)
    trimmed.contains = lambda *args: value
    item = only(curve(X), trimmed, (0, 0))
    assert item["fields"][1]["trim"] == "contains"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), 1j, "1", [1, 2]])
def test_invalid_field_evidence_is_unavailable_and_json_safe(bad):
    class BadField:
        def evaluate(self, x, y):
            return bad

    item = only(BadField(), curve(Y), (0.0, 0.0))
    assert item["fields"][0]["residual"] is None
    assert item["normalized_jacobian_reciprocal_condition"] is None
    assert item["linearized_displacement"] is None


def test_evaluator_exception_becomes_unavailable_evidence():
    first = curve(X)
    first.evaluate = lambda x, y: math.log(-1)
    item = only(first, curve(Y), (0.0, 0.0))
    assert "field_1_residual_unavailable" in item["warnings"]


def test_maxfloat_coordinate_does_not_invent_finite_derivative_or_zero_error():
    with np.errstate(all="ignore"):
        item = only(curve(X), curve(Y), (np.finfo(float).max, 0))
    assert item["local_model_status"] == "unavailable"
    assert item["linearized_displacement_norm"] is None


def test_extreme_underflow_never_turns_flat_samples_into_position_verification():
    item = only(curve(sp.Float(1e-300) * X**8), curve(Y), (1e-20, 0))
    assert not item["position_verified"]
    assert item["linearized_displacement"] is None


def test_finite_sample_aliasing_does_not_gain_certification():
    step = np.finfo(float).eps ** 0.2
    first = ProceduralCurve(lambda x, y: 1e-20 * np.sin(2 * np.pi * x / step))
    item = only(first, curve(Y), (step / 4, 0))
    assert item["fields"][0]["residual"] != 0
    assert not item["position_verified"] and item["positional_error_bound"] is None


@pytest.mark.parametrize("value", [0, -1, np.inf, np.nan, True])
def test_invalid_position_tolerance_rejected_before_probes(value):
    with pytest.raises(ValueError):
        diagnose(curve(X), curve(Y), [(0, 0)], position_tolerance=value)


@pytest.mark.parametrize("value", [1, (1,), (0, 1), (-1, 1), (1, np.inf)])
def test_invalid_derivative_scale_rejected(value):
    with pytest.raises(ValueError):
        diagnose(curve(X), curve(Y), [(0, 0)], derivative_scale=value)


@pytest.mark.parametrize("point", [(1,), (1, 2, 3), (np.inf, 0), (1j, 0), ("1", "2")])
def test_invalid_candidate_rejected(point):
    with pytest.raises(ValueError):
        diagnose(curve(X), curve(Y), [point])


@pytest.mark.parametrize("tolerance", [-1, np.inf, np.nan])
def test_invalid_trim_tolerance_rejected(tolerance):
    with pytest.raises(ValueError):
        diagnose(curve(X), curve(Y), [(0, 0)], trim_tolerance=tolerance)


def test_empty_report_does_not_assert_disjointness_or_completeness():
    report = diagnose(curve(Y - X**8), curve(Y - X**8), [])
    assert report["candidate_reports"] == [] and not report["certified"]
    assert report["overlap"] == report["completeness"] == "not_assessed"


def test_coincident_samples_are_not_isolated_root_claims():
    first = curve(Y - X * X)
    item = only(first, first, (0, 0))
    assert item["isolated_root_status"] == "not_established"
    assert item["linearized_displacement"] is None
