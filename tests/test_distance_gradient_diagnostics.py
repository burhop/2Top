"""Analytic callback/domain oracles and distinct source/chord derivatives."""

import numpy as np
import pytest
import sympy as sp

from geometry import (
    AreaRegion,
    CompositeCurve,
    ConicSection,
    TrimmedImplicitCurve,
    create_square_from_edges,
)
from geometry.field_strategy import SignedDistanceField


def callback_field(function):
    field = SignedDistanceField(
        AreaRegion(create_square_from_edges((0.0, 0.0), (4.0, 4.0)))
    )
    field.evaluate = function
    return field


def sampled_circle():
    x, y = sp.symbols("x y")
    return SignedDistanceField(
        AreaRegion(
            CompositeCurve(
                [
                    TrimmedImplicitCurve(
                        ConicSection(x * x + y * y - 1, (x, y)), lambda x, y: True
                    )
                ]
            )
        ),
        resolution=1e-6,
    )


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e6])
def test_analytic_circle_callback_recovers_nonzero_unit_components(scale):
    field = callback_field(lambda x, y: np.hypot(x, y) - scale)
    point = (1.6 * scale, 1.2 * scale)
    result = field.gradient_diagnostics(*point)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], (0.8, 0.6), rtol=3e-6, atol=0)
    assert result["derivative_target"] == "evaluate"
    assert result["distance_model"] == "custom_evaluation"
    assert not result["certified"]
    assert 1 <= result["field_evaluations"] <= 321
    if scale == 1e-6:
        assert max(np.abs(field.gradient(*point))) < 0.001


def test_smooth_tiny_stationary_axis_can_remain_unresolved_honestly():
    result = callback_field(lambda x, y: np.hypot(x, y) - 1e-6).gradient_diagnostics(
        2e-6, 0.0
    )
    # x is recovered, but the finite sampling budget does not resolve y=0.
    assert result["raw_gradient"][0] == pytest.approx(1.0, rel=1e-10)
    assert not result["available"]
    assert all(np.isnan(v) for v in result["gradient"])
    assert result["status"][1] == "budget_exhausted"
    assert np.isinf(result["error_estimate"][1])


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e6])
def test_true_circle_medial_axis_is_not_a_zero_normal(scale):
    result = callback_field(lambda x, y: np.hypot(x, y) - scale).gradient_diagnostics(
        0.0, 0.0
    )
    assert not result["available"]
    assert all(np.isnan(v) for v in result["gradient"])
    assert all(np.isinf(v) for v in result["error_estimate"])
    assert result["field_evaluations"] <= 321


def test_annulus_medial_radius_is_unresolved_and_smooth_sides_are_radial():
    field = callback_field(lambda x, y: np.abs(np.hypot(x, y) - 0.7) - 0.3)
    for radius, sign in ((0.5, -1), (0.9, 1)):
        result = field.gradient_diagnostics(0.8 * radius, 0.6 * radius)
        assert result["available"]
        np.testing.assert_allclose(
            result["gradient"], (sign * 0.8, sign * 0.6), rtol=3e-6
        )
    result = field.gradient_diagnostics(0.8 * 0.7, 0.6 * 0.7)
    assert not result["available"]
    assert all(np.isnan(v) for v in result["gradient"])


def test_source_circle_boundary_sign_chord_jump_is_rejected():
    field = sampled_circle()
    a, b = np.array(field._boundary_segments()[0])
    midpoint = (a + b) / 2
    point = midpoint / np.hypot(*midpoint)
    # Analytic source circle is smooth here, but evaluate uses source sign
    # with a nonzero chord magnitude: its jump is not a curved SDF derivative.
    assert abs(field.evaluate(*point)) > 0.001
    assert min(np.abs(field.gradient(*point))) > 1000
    result = field.gradient_diagnostics(*point)
    assert not result["available"]
    assert all(np.isnan(v) for v in result["gradient"])
    assert result["derivative_target"] == "evaluate"
    assert result["distance_model"] == "boundary_magnitude_and_containment_sign"
    assert all(np.isinf(v) for v in result["error_estimate"])


def test_consistent_sampled_chord_normal_differs_from_source_circle_normal():
    field = sampled_circle()
    a, b = np.array(field._boundary_segments()[0])
    midpoint = (a + b) / 2
    normal = midpoint / np.hypot(*midpoint)
    tangent = np.array([-normal[1], normal[0]])
    point = midpoint + 0.2 * normal + 0.02 * tangent
    result = field.gradient_diagnostics(*point)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], normal, rtol=2e-6, atol=1e-9)
    source_normal = point / np.hypot(*point)
    assert np.linalg.norm(np.array(result["gradient"]) - source_normal) > 0.01
    assert not result["certified"]


@pytest.mark.parametrize("point", [(0.04, 0.09), (0.0, 0.09), (-0.04, 0.09)])
def test_callback_domain_and_infinite_boundary_derivative(point):
    def function(x, y):
        with np.errstate(invalid="ignore"):
            return np.sqrt(x) + np.sqrt(y)

    result = callback_field(function).gradient_diagnostics(*point)
    if point[0] > 0:
        assert result["available"]
        np.testing.assert_allclose(result["gradient"], (2.5, 5 / 3), rtol=3e-6)
    else:
        assert not result["available"]
        assert all(np.isnan(v) for v in result["gradient"])


@pytest.mark.parametrize("kind", ["scalar", "zero_dim", "broadcast", "empty"])
def test_callback_argument_shapes_and_result_shapes_are_preserved(kind):
    if kind == "scalar":
        x, y = 0.3, 0.2
    elif kind == "zero_dim":
        x, y = np.array(0.3), np.array(0.2)
    elif kind == "broadcast":
        x, y = np.array([[0.3], [0.4]]), np.array([0.1, 0.2, 0.3])
    else:
        x, y = np.empty((0, 1)), np.ones((1, 3))
    shape = np.broadcast_arrays(x, y)[0].shape
    calls = []

    def function(a, b):
        calls.append((a, b))
        if kind == "scalar":
            assert type(a) is float and type(b) is float
        else:
            assert a.shape == b.shape == shape
        return 3 * a - 4 * b + 7

    result = callback_field(function).gradient_diagnostics(x, y)
    assert calls
    assert len(calls) == result["field_evaluations"] <= 321
    assert np.shape(result["available"]) == shape
    assert all(np.shape(v) == shape for v in result["gradient"])
    np.testing.assert_allclose(result["gradient"][0], np.full(shape, 3), rtol=1e-9)
    np.testing.assert_allclose(result["gradient"][1], np.full(shape, -4), rtol=1e-9)
    if kind == "zero_dim":
        assert isinstance(result["status"][0], np.ndarray)
    if kind == "scalar":
        assert type(result["available"]) is bool


@pytest.mark.parametrize("exception", [TypeError, ValueError, RuntimeError])
def test_internal_callback_errors_propagate_once(exception):
    calls = []

    def function(x, y):
        calls.append((x, y))
        raise exception("authoritative diagnostic callback error")

    with pytest.raises(exception, match="authoritative diagnostic callback error"):
        callback_field(function).gradient_diagnostics(0.3, 0.2)
    assert len(calls) == 1


@pytest.mark.parametrize("subclass", [False, True])
def test_provided_gradient_is_authoritative_and_not_numerically_probed(subclass):
    class CustomField(SignedDistanceField):
        def gradient(self, x, y):
            return 3.0, -4.0

    field = callback_field(
        lambda x, y: (_ for _ in ()).throw(RuntimeError("must not evaluate"))
    )
    if subclass:
        field.__class__ = CustomField
    else:
        field.gradient = lambda x, y: (3.0, -4.0)
    result = field.gradient_diagnostics(0.3, 0.2)
    assert result["gradient"] == (3.0, -4.0)
    assert result["method"] == "provided_gradient"
    assert result["error_estimate"] is None
    assert result["field_evaluations"] is None


def test_vectorized_distance_override_is_authoritative_for_array_gradient():
    field = callback_field(lambda x, y: x + y)
    del field.evaluate
    field._evaluate_vectorized = lambda x, y: 3 * x - 4 * y
    xx, yy = np.array([0.3, 0.4]), np.array([0.2, 0.1])
    np.testing.assert_allclose(field.gradient(xx, yy), ([3, 3], [-4, -4]), atol=1e-12)
    result = field.gradient_diagnostics(xx, yy)
    assert result["distance_model"] == "custom_evaluation"
    np.testing.assert_allclose(result["gradient"], ([3, 3], [-4, -4]), atol=1e-9)


def test_native_diagnostics_preserve_geometric_corner_and_medial_masks():
    field = callback_field(lambda x, y: x + y)
    del field.evaluate
    result = field.gradient_diagnostics(
        np.array([2, 0, 2, np.nan]), np.array([1, 0, 2, 1])
    )
    np.testing.assert_array_equal(result["available"], [True, False, False, False])
    assert result["method"] == "nearest_feature"
    assert result["error_estimate"] is None
    assert result["field_evaluations"] == 0
    np.testing.assert_array_equal(result["gradient"][0], [0, np.nan, np.nan, np.nan])
    np.testing.assert_array_equal(result["gradient"][1], [-1, np.nan, np.nan, np.nan])


def test_callback_nonfinite_coordinates_have_no_available_vector():
    result = callback_field(lambda x, y: 3 * x - 4 * y).gradient_diagnostics(
        np.array([0.3, np.nan, np.inf]), 0.2
    )
    np.testing.assert_array_equal(result["available"], [True, False, False])
    assert result["status"][0][1] == result["status"][1][2] == "nonfinite_coordinate"
    assert np.isnan(result["gradient"][0][1:]).all()


def test_diagnostics_outputs_do_not_mutate_next_query_or_retain_geometry_cache():
    field = callback_field(lambda x, y: 3 * x - 4 * y)
    result = field.gradient_diagnostics(np.array([0.3]), 0.2)
    result["gradient"][0][0] = 99
    result["raw_gradient"][1][0] = 99
    next_result = field.gradient_diagnostics(np.array([0.3]), 0.2)
    np.testing.assert_allclose(next_result["gradient"], ([3], [-4]), rtol=1e-9)
    assert field._cache is None and field._cached_segments_ab is None


def test_constant_scalar_callback_output_broadcasts_without_false_accuracy_claim():
    result = callback_field(lambda x, y: 7.0).gradient_diagnostics(
        np.array([0.3, 0.4]), 0.2
    )
    assert result["available"].all()
    np.testing.assert_array_equal(result["gradient"], ([0, 0], [0, 0]))
    assert all(np.all(v == "flat_samples") for v in result["status"])
    assert not result["certified"]


def test_invalid_callback_shape_is_rejected():
    field = callback_field(lambda x, y: np.ones(2))
    with pytest.raises(ValueError):
        field.gradient_diagnostics(np.array([0.1, 0.2, 0.3]), 0.2)


@pytest.mark.parametrize("tolerance_keyword", [False, True])
def test_custom_containment_remains_authoritative_at_every_scalar_probe(
    tolerance_keyword,
):
    field = callback_field(lambda x, y: x + y)
    del field.evaluate
    calls = []

    def contains(x, y, **kwargs):
        assert type(x) is float and type(y) is float
        calls.append(kwargs)
        return False

    field.region.contains = (
        contains if tolerance_keyword else lambda x, y: contains(x, y)
    )
    result = field.gradient_diagnostics(2.0, 1.0)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], (0, 1), atol=1e-10)
    assert len(calls) == result["field_evaluations"]
    assert all(
        (call.get("tolerance") == 0.0) if tolerance_keyword else not call
        for call in calls
    )


def test_all_nonfinite_query_remains_bounded_and_explicitly_unavailable():
    result = callback_field(lambda x, y: 7.0).gradient_diagnostics(
        np.array([np.nan, np.inf]), np.nan
    )
    assert not result["available"].any()
    assert np.isnan(result["gradient"]).all()
    assert result["field_evaluations"] <= 321
    assert all(np.all(v == "nonfinite_coordinate") for v in result["status"])


def test_provided_gradient_super_delegation_preserves_native_policy():
    class CustomField(SignedDistanceField):
        def gradient(self, x, y):
            return super().gradient(x, y)

    field = CustomField(AreaRegion(create_square_from_edges((0.0, 0.0), (4.0, 4.0))))
    assert field.gradient_diagnostics(2.0, 1.0)["gradient"] == (0.0, -1.0)
    assert not field.gradient_diagnostics(2.0, 2.0)["available"]
