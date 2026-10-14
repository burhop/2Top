"""Analytic oracles, finite-sampling limits and compatibility of default steps."""

import math

import numpy as np
import pytest

from geometry import ProceduralCurve
from geometry.differentiation import estimate_gradient


@pytest.mark.parametrize("center", [1e9, 1e12])
def test_translated_sine_needs_no_local_hint(center):
    curve = ProceduralCurve(lambda x, y: np.sin(x - center) + y)
    point = center + 0.3
    result = curve.gradient_diagnostics(point, 0.2)
    np.testing.assert_allclose(
        result["gradient"], (np.cos(point - center), 1), rtol=2e-10
    )
    assert result["status"] == ("sample_consistent", "sample_consistent")
    assert result["selection"] == ("local", "local")
    assert result["field_evaluations"] == 17
    assert all(
        v > 0 and math.isfinite(v)
        for axis in result["steps"]
        for pair in axis
        for v in pair
    )


@pytest.mark.parametrize("scale", [1e-12, 1e-9, 1e-6, 1.0, 1e9])
def test_scale_selection_matches_analytic_local_sine(scale):
    curve = ProceduralCurve(lambda x, y: np.sin(x / scale) + y / scale)
    result = curve.gradient_diagnostics(0.3 * scale, 0.2 * scale)
    np.testing.assert_allclose(
        result["gradient"], (np.cos(0.3) / scale, 1 / scale), rtol=2e-9, atol=0
    )
    assert result["status"] == ("sample_consistent", "sample_consistent")
    assert 17 <= result["field_evaluations"] <= 321


def test_anisotropic_axis_does_not_supply_an_unrelated_scale():
    result = ProceduralCurve(lambda x, y: np.sin(x) + y / 1e15).gradient_diagnostics(
        0, 1e15
    )
    np.testing.assert_allclose(result["gradient"], (1, 1e-15), rtol=1e-10, atol=0)
    assert result["selection"] == ("local", "expanded")
    assert result["status"] == ("sample_consistent", "sample_consistent")


@pytest.mark.parametrize("scalar_only", [False, True])
def test_broadcast_empty_zero_dimensional_parity_and_immutable_inputs(scalar_only):
    sine = math.sin if scalar_only else np.sin
    cosine = math.cos if scalar_only else np.cos
    curve = ProceduralCurve(lambda x, y: sine(x) + y * y)
    xx = np.array([-0.3, 0.2])[:, None]
    yy = np.array([0.0, 0.1, 0.5])[None, :]
    copies = xx.copy(), yy.copy()
    gradient = curve.gradient(xx, yy)
    result = curve.gradient_diagnostics(xx, yy)
    for actual, diagnostic in zip(gradient, result["gradient"]):
        np.testing.assert_array_equal(actual, diagnostic)
    np.testing.assert_allclose(
        gradient[0], np.broadcast_to(np.vectorize(cosine)(xx), (2, 3)), rtol=2e-10
    )
    np.testing.assert_allclose(
        gradient[1], np.broadcast_to(2 * yy, (2, 3)), rtol=2e-10, atol=0
    )
    for key in ("status", "selection", "candidates", "nominal_step"):
        assert all(v.shape == (2, 3) for v in result[key])
    np.testing.assert_array_equal(xx, copies[0])
    np.testing.assert_array_equal(yy, copies[1])
    empty = curve.gradient_diagnostics(np.empty((0, 1)), np.ones((1, 3)))
    assert empty["field_evaluations"] == 1
    assert all(v.shape == (0, 3) for v in empty["gradient"] + empty["status"])
    zero = curve.gradient_diagnostics(np.array(0.3), np.array(0.2))
    assert all(
        isinstance(v, np.ndarray) and v.shape == ()
        for v in zero["gradient"] + zero["status"]
    )


def test_mixed_array_decisions_keep_regular_points_and_expose_nonsmooth_origin():
    curve = ProceduralCurve(lambda x, y: np.abs(x) + y)
    xx = np.array([-1.0, 0.0, 1.0])
    result = curve.gradient_diagnostics(xx, 0)
    for actual, diagnostic in zip(curve.gradient(xx, 0), result["gradient"]):
        np.testing.assert_array_equal(actual, diagnostic)
    np.testing.assert_allclose(result["gradient"][0][[0, 2]], [-1, 1], atol=1e-10)
    assert result["status"][0][1] == "budget_exhausted"
    assert np.isinf(result["error_estimate"][0][1])
    assert np.all(np.isfinite(result["error_estimate"][0][[0, 2]]))
    assert result["candidates"][0][1] == 20
    assert result["field_evaluations"] <= 321


@pytest.mark.parametrize(
    "function",
    [
        lambda x, y: np.abs(x) + y,
        lambda x, y: np.sign(x) + y,
        lambda x, y: np.cbrt(x) + y,
        lambda x, y: np.sqrt(np.abs(x)) + y,
        lambda x, y: x * np.abs(x) + y * y,
    ],
)
def test_nonconvergent_or_nonsmooth_directions_are_not_accepted(function):
    curve = ProceduralCurve(function)
    result = curve.gradient_diagnostics(0, 0)
    assert math.isinf(result["error_estimate"][0])
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(0, 0)


@pytest.mark.parametrize("scale", [1e-200, 1.0, 1e200])
def test_field_rescaling_retains_side_inconsistency_guard(scale):
    curve = ProceduralCurve(lambda x, y: scale * (np.abs(x) + y))
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(0, 0)
    smooth = ProceduralCurve(lambda x, y: scale * (x * x + y * y))
    np.testing.assert_allclose(smooth.normal(0, 1), (0, 1), atol=1e-10)


@pytest.mark.parametrize(
    "function", [lambda x, y: x * x + y * y, lambda x, y: x**3 + y**3]
)
def test_smooth_stationary_points_remain_zero_without_inventing_normals(function):
    curve = ProceduralCurve(function)
    result = curve.gradient_diagnostics(0, 0)
    np.testing.assert_allclose(result["gradient"], (0, 0), atol=1e-20)
    assert result["status"] == ("sampled_stationary", "sampled_stationary")
    with pytest.raises(ValueError, match="Normal undefined"):
        curve.normal(0, 0)


@pytest.mark.parametrize(
    "function,point,normal",
    [
        (lambda x, y: 1 + y, (0, 0), (0, 1)),
        (lambda x, y: x, (1, 0), (1, 0)),
        (lambda x, y: x**3, (1, 0), (1, 0)),
    ],
)
def test_flat_axes_retain_affine_and_regular_nonlinear_normals(function, point, normal):
    curve = ProceduralCurve(function)
    result = curve.gradient_diagnostics(*point)
    assert "flat_samples" in result["status"]
    assert all(math.isfinite(v) for v in result["error_estimate"])
    np.testing.assert_allclose(curve.normal(*point), normal, atol=1e-10)


@pytest.mark.parametrize("value", [0.0, 7.0, 1e16])
def test_flat_fields_do_not_acquire_an_accepted_normal(value):
    curve = ProceduralCurve(lambda x, y: value)
    result = curve.gradient_diagnostics(0, 0)
    assert result["status"] == ("flat_samples", "flat_samples")
    assert result["gradient"] == (0.0, 0.0)
    with pytest.raises(ValueError, match="Normal undefined"):
        curve.normal(0, 0)


def test_roundoff_expansion_stops_before_accepting_a_nonlocal_oscillatory_secant():
    curve = ProceduralCurve(lambda x, y: 1e9 + np.sin(x) + x + y)
    result = curve.gradient_diagnostics(0, 0)
    assert result["status"][0] == "roundoff_limited"
    assert math.isinf(result["error_estimate"][0])
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(0, 0)


def test_too_small_feature_remains_unresolved_with_explicit_escape_hatch():
    def function(x, y):
        return np.sin(x / 1e-18) + y / 1e-18

    curve = ProceduralCurve(function)
    result = curve.gradient_diagnostics(0.3e-18, 0.2e-18)
    assert result["status"][0] == "budget_exhausted"
    assert math.isinf(result["error_estimate"][0])
    explicit = ProceduralCurve(function, derivative_scale=1e-18)
    np.testing.assert_allclose(
        explicit.gradient(0.3e-18, 0.2e-18), (np.cos(0.3) / 1e-18, 1e18), rtol=2e-10
    )


def test_off_ladder_confirmation_breaks_a_dyadic_sine_alias():
    step = np.finfo(float).eps ** 0.2
    curve = ProceduralCurve(lambda x, y: np.sin(2 * np.pi * x / step) + y)
    result = curve.gradient_diagnostics(0, 0)
    np.testing.assert_allclose(result["gradient"], (2 * np.pi / step, 1), rtol=2e-10)
    assert result["candidates"][0] > 1


def test_hidden_bump_is_an_explicit_counterexample_to_any_accuracy_certificate():
    def function(x, y):
        u = x / 1e-100
        return np.where(np.abs(u) < 1, x * np.exp(1 - 1 / (1 - u * u)), 0.0) + y

    curve = ProceduralCurve(function)
    with np.errstate(all="ignore"):
        result = curve.gradient_diagnostics(0, 0)
    # Analytic derivative at the origin is (1,1). Every finite sampled neighbor
    # misses this bump; the API deliberately says flat samples, never certified.
    assert result["gradient"][0] == 0
    assert result["status"][0] == "flat_samples"
    np.testing.assert_allclose(
        ProceduralCurve(function, derivative_scale=1e-100).gradient(0, 0),
        (1, 1),
        rtol=2e-10,
    )


def test_numeric_probe_count_is_bounded_and_diagnostics_match_observed_calls():
    calls = []

    def function(x, y):
        calls.append(1)
        return np.abs(x) + y

    result = ProceduralCurve(function).gradient_diagnostics(
        np.array([-1.0, 0.0, 1.0]), 0
    )
    assert len(calls) == result["field_evaluations"] <= 321


def test_fixed_override_is_bit_identical_to_existing_estimator_and_uses_nine_probes():
    calls = []

    def function(x, y):
        calls.append(1)
        return np.sin(x) + y * y

    curve = ProceduralCurve(function, derivative_scale=(1.0, 2.0))
    actual = curve.gradient(0.3, 0.2)
    assert len(calls) == 9
    expected = estimate_gradient(
        curve.evaluate, np.array(0.3), np.array(0.2), (1.0, 2.0), diagnostics=False
    )
    np.testing.assert_array_equal(actual, expected["gradient"])
    assert curve.gradient_diagnostics(0.3, 0.2)["method"] == "central_richardson"


def test_callback_errors_propagate_and_bad_output_is_not_a_scale_candidate():
    def blocked(x, y):
        if x == 0 and y == 0:
            return 0.0
        raise RuntimeError("blocked neighbor")

    with pytest.raises(RuntimeError, match="blocked neighbor"):
        ProceduralCurve(blocked).gradient(0, 0)
    with pytest.raises(ValueError, match="real numeric"):
        ProceduralCurve(lambda x, y: "wrong").gradient(0, 0)


def test_numpy_domain_probes_refine_but_python_domain_exceptions_propagate():
    curve = ProceduralCurve(lambda x, y: np.log(x) + y)
    with np.errstate(all="ignore"):
        result = curve.gradient_diagnostics(1e-9, 0.2)
    np.testing.assert_allclose(result["gradient"], (1e9, 1), rtol=2e-9)
    assert result["status"] == ("sample_consistent", "sample_consistent")
    with pytest.raises(ValueError, match="math domain"):
        ProceduralCurve(lambda x, y: math.log(x) + y).gradient(1e-9, 0.2)


def test_nonfinite_inputs_and_subnormal_derivatives_remain_explicit():
    with np.errstate(all="ignore"):
        result = ProceduralCurve(lambda x, y: x + y).gradient_diagnostics(
            np.finfo(float).max, 0
        )
    assert result["status"][0] == "nonfinite"
    assert not math.isfinite(result["gradient"][0])
    curve = ProceduralCurve(lambda x, y: 1e-320 * (x + y))
    result = curve.gradient_diagnostics(0, 0)
    assert result["status"] == ("budget_exhausted", "budget_exhausted")
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(0, 0)
