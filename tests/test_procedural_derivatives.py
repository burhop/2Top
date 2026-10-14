"""Analytic oracles and explicit uncertainty contracts for procedural fields."""

import math

import numpy as np
import pytest

from geometry.procedural_curve import ProceduralCurve


@pytest.mark.parametrize("coordinate", [0.0, 1.0, 1e9, 1e15])
def test_linear_derivatives_at_large_coordinates(coordinate):
    curve = ProceduralCurve(
        lambda x, y: x + y, derivative_scale=max(1.0, abs(coordinate))
    )
    np.testing.assert_allclose(
        curve.gradient(coordinate, 0), [1, 1], rtol=1e-10, atol=0
    )


@pytest.mark.parametrize("scale", [1e-12, 1e-9, 1.0, 1e9])
def test_local_scale_sine_accuracy(scale):
    curve = ProceduralCurve(
        lambda x, y: np.sin(x / scale) + y / scale, derivative_scale=scale
    )
    np.testing.assert_allclose(
        curve.gradient(0.3 * scale, 0.2 * scale),
        [np.cos(0.3) / scale, 1 / scale],
        rtol=2e-10,
        atol=0,
    )


@pytest.mark.parametrize("center", [1e9, 1e12])
def test_translated_sine_uses_actual_displacements(center):
    curve = ProceduralCurve(lambda x, y: np.sin(x - center) + y, derivative_scale=1)
    x = center + 0.3
    result = curve.gradient_diagnostics(x, 0.2)
    np.testing.assert_allclose(result["gradient"], [np.cos(x - center), 1], rtol=2e-10)
    for coarse, fine in result["steps"]:
        assert all(v > 0 for v in coarse + fine)


def test_large_quadratic_accuracy():
    curve = ProceduralCurve(lambda x, y: x * x + y * y)
    np.testing.assert_allclose(curve.gradient(1e9, 0), [2e9, 0], rtol=2e-10, atol=0)


@pytest.mark.parametrize("scale", [1e-200, 1, 1e200])
def test_cusp_and_smooth_normal_field_rescaling(scale):
    cusp = ProceduralCurve(lambda x, y: scale * (y * y - x**3))
    with pytest.raises(ValueError, match="Normal undefined"):
        cusp.normal(0, 0)
    linear = ProceduralCurve(lambda x, y: scale * (x + y))
    np.testing.assert_allclose(linear.normal(0, 0), [math.sqrt(0.5)] * 2, rtol=1e-10)


@pytest.mark.parametrize("scalar_only", [False, True])
def test_analytic_callback_and_numerical_broadcast_empty_and_immutable(scalar_only):
    sine = math.sin if scalar_only else np.sin
    cosine = math.cos if scalar_only else np.cos
    numerical = ProceduralCurve(lambda x, y: sine(x) + y)
    analytic = ProceduralCurve(
        lambda x, y: sine(x) + y, gradient_function=lambda x, y: (cosine(x), 1)
    )
    x, y = np.arange(3.0)[:, None], np.arange(4.0)[None, :]
    before = x.copy(), y.copy()
    for curve in (numerical, analytic):
        gx, gy = curve.gradient(x, y)
        for value, diagnostic in zip(
            (gx, gy), curve.gradient_diagnostics(x, y)["gradient"]
        ):
            np.testing.assert_array_equal(value, diagnostic)
        assert gx.shape == gy.shape == (3, 4)
        np.testing.assert_allclose(gx, np.broadcast_to(np.cos(x), (3, 4)), atol=1e-10)
        np.testing.assert_allclose(gy, 1, atol=1e-10)
        assert all(
            v.shape == (0, 3) for v in curve.gradient(np.empty((0, 1)), np.ones((1, 3)))
        )
        assert all(isinstance(v, float) for v in curve.gradient(0, 0))
        assert all(
            isinstance(v, np.ndarray) and v.shape == ()
            for v in curve.gradient(np.array(0.0), np.array(0.0))
        )
    np.testing.assert_array_equal(x, before[0])
    np.testing.assert_array_equal(y, before[1])
    diagnostics = analytic.gradient_diagnostics(0, 0)
    assert (
        diagnostics["method"] == "analytic"
        and diagnostics["error_estimate"] is None
        and diagnostics["steps"] is None
    )


def test_analytic_gradient_does_not_sample_neighbours():
    calls = []

    def function(x, y):
        calls.append((x, y))
        return x * x + y * y

    curve = ProceduralCurve(function, gradient_function=lambda x, y: (2 * x, 2 * y))
    assert curve.gradient(1e15, 0) == (2e15, 0)
    assert calls == []
    assert curve.normal(1e15, 0) == (1, 0)
    assert len(calls) == 1


@pytest.mark.parametrize(
    "callback",
    [
        lambda x, y: 1,
        lambda x, y: (1, 2, 3),
        lambda x, y: (1j, 0),
        lambda x, y: ("1", 0),
        lambda x, y: (np.ones(7), 0),
    ],
)
def test_malformed_analytic_result_is_not_silently_replaced(callback):
    curve = ProceduralCurve(lambda x, y: x + y, gradient_function=callback)
    with pytest.raises(ValueError):
        curve.gradient(np.ones(2), np.ones(2))


@pytest.mark.parametrize(
    "scale",
    [0, -1, float("nan"), float("inf"), True, [True, True], [1, 0], [1, 2, 3], "1", 1j],
)
def test_invalid_local_scale_rejected(scale):
    with pytest.raises(ValueError):
        ProceduralCurve(lambda x, y: x + y, derivative_scale=scale)


def test_anisotropic_scale_and_placeholder_serialization():
    curve = ProceduralCurve(
        lambda x, y: np.sin(x / 1e-9) + np.cos(y / 1e3),
        derivative_scale=[1e-9, 1e3],
        gradient_function=lambda x, y: (
            np.cos(x / 1e-9) / 1e-9,
            -np.sin(y / 1e3) / 1e3,
        ),
    )
    data = curve.to_dict()
    assert (
        data["derivative_scale"] == [1e-9, 1e3]
        and "analytic gradient" in data["_serialization_note"]
    )
    restored = ProceduralCurve.from_dict(data)
    with pytest.raises(NotImplementedError):
        restored.gradient(0, 0)


def test_collapsed_refinement_and_maximum_float_report_uncertainty():
    curve = ProceduralCurve(lambda x, y: x + y, derivative_scale=1)
    diagnostics = curve.gradient_diagnostics(1e15, 0)
    assert math.isinf(diagnostics["error_estimate"][0])
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(1e15, 0)
    with np.errstate(all="ignore"):
        diagnostics = curve.gradient_diagnostics(np.finfo(float).max, 0)
    assert not math.isfinite(diagnostics["gradient"][0]) and math.isinf(
        diagnostics["error_estimate"][0]
    )


def test_nonfinite_and_zero_analytic_normals_rejected():
    for gradient in [(0, 0), (float("nan"), 1), (float("inf"), 0)]:
        curve = ProceduralCurve(
            lambda x, y: x, gradient_function=lambda x, y, g=gradient: g
        )
        with pytest.raises(ValueError, match="Normal undefined"):
            curve.normal(0, 0)


def test_visible_cancellation_uncertainty_is_not_a_certified_bound():
    curve = ProceduralCurve(lambda x, y: 1e16 + x, derivative_scale=1)
    diagnostics = curve.gradient_diagnostics(0, 0)
    assert max(diagnostics["error_estimate"]) > 1
    with pytest.raises(ValueError, match="unresolved"):
        curve.normal(0, 0)


def test_default_scale_does_not_couple_an_unrelated_large_axis():
    curve = ProceduralCurve(lambda x, y: np.sin(x) + y / 1e15)
    np.testing.assert_allclose(curve.gradient(0, 1e15), [1, 1e-15], rtol=1e-10, atol=0)


def test_scalar_branching_analytic_callback_broadcasts():
    curve = ProceduralCurve(
        lambda x, y: np.abs(x) + y,
        gradient_function=lambda x, y: (1 if x >= 0 else -1, 1),
    )
    gx, gy = curve.gradient(np.array([-1.0, 1.0]), 0)
    np.testing.assert_array_equal(gx, [-1, 1])
    np.testing.assert_array_equal(gy, [1, 1])


def test_subnormal_output_quantization_is_visible_to_normal_guard():
    numerical = ProceduralCurve(lambda x, y: 1e-320 * (x + y))
    with pytest.raises(ValueError, match="unresolved"):
        numerical.normal(0, 0)
    analytic = ProceduralCurve(
        lambda x, y: 1e-320 * (x + y), gradient_function=lambda x, y: (1e-320, 1e-320)
    )
    np.testing.assert_allclose(analytic.normal(0, 0), [math.sqrt(0.5)] * 2, rtol=1e-14)
