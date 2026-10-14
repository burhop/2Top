"""Independent Euclidean rectangle/circle oracles and live-query regressions."""

import gc
import weakref

import numpy as np
import pytest
import sympy as sp

from geometry import AreaRegion, CompositeCurve, ConicSection, create_square_from_edges
from geometry.base_field import CurveField
from geometry.field_strategy import SignedDistanceField
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve


def region(bounds=(0.0, 0.0, 4.0, 4.0)):
    x0, y0, x1, y1 = bounds
    return AreaRegion(create_square_from_edges((x0, y0), (x1, y1)))


def rectangle_distance(x, y, bounds=(0.0, 0.0, 4.0, 4.0)):
    """Analytic axis-aligned box SDF, independent of the engine's segment loop."""
    x0, y0, x1, y1 = bounds
    dx = np.abs(np.asarray(x) - (x0 + x1) / 2) - (x1 - x0) / 2
    dy = np.abs(np.asarray(y) - (y0 + y1) / 2) - (y1 - y0) / 2
    return np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(
        np.maximum(dx, dy), 0
    )


@pytest.mark.parametrize(
    "point", [(1, 2), (-1, 2), (5, 2), (2, 5), (-1, -2), (0, 2), (4, 4), (2, 2)]
)
@pytest.mark.parametrize("kind", ["scalar", "zero_dim", "array"])
def test_analytic_rectangle_sign_and_magnitude(point, kind):
    x, y = point
    if kind == "zero_dim":
        x, y = np.array(x), np.array(y)
    elif kind == "array":
        x, y = np.array([x]), np.array([y])
    observed = SignedDistanceField(region()).evaluate(x, y)
    np.testing.assert_allclose(observed, rectangle_distance(x, y), atol=1e-14)
    assert (
        isinstance(observed, float) if kind == "scalar" else observed.shape == x.shape
    )


@pytest.mark.parametrize("shape", [(5,), (5, 5), (2, 3, 4)])
@pytest.mark.parametrize("copy", [False, True])
def test_unprobed_coordinate_edit_changes_sign(shape, copy):
    field = SignedDistanceField(region())
    x, y = np.ones(shape), np.full(shape, 2.0)
    original = field.evaluate(x, y)
    if copy:
        x, y = x.copy(), y.copy()
    x.flat[1] = -1
    actual = field.evaluate(x, y)
    np.testing.assert_allclose(actual, rectangle_distance(x, y), atol=1e-14)
    assert actual.flat[1] == 1
    assert original.flat[1] == -1


@pytest.mark.parametrize("delta", [5e-10, 5e-6])
def test_close_coordinates_are_not_cache_keys(delta):
    field = SignedDistanceField(region())
    x, y = np.ones((5, 5)), np.full((5, 5), 2.0)
    field.evaluate(x, y)
    new_x = x + delta
    np.testing.assert_allclose(
        field.evaluate(new_x, y), rectangle_distance(new_x, y), rtol=0, atol=1e-14
    )


def test_returned_buffer_cannot_poison_later_queries():
    field = SignedDistanceField(region())
    x, y = np.ones((5, 5)), np.full((5, 5), 2.0)
    result = field.evaluate(x, y)
    result[:] = 99
    np.testing.assert_array_equal(field.evaluate(x, y), -np.ones(x.shape))
    assert field._cache is field._cached_segments_ab is None
    field.clear_cache()
    assert field.evaluate(1, 2) == -1


@pytest.mark.parametrize("kind", ["scalar", "array"])
@pytest.mark.parametrize("edit", ["region", "outer", "segments", "endpoints"])
def test_live_geometry_after_warm_query(kind, edit):
    field = SignedDistanceField(region())
    x, y = (
        (3.0, 3.0) if kind == "scalar" else (np.full((5, 5), 3.0), np.full((5, 5), 3.0))
    )
    np.testing.assert_array_equal(field.evaluate(x, y), -1)
    bigger = region((0, 0, 8, 8))
    if edit == "region":
        field.region = bigger
    elif edit == "outer":
        field.region.outer_boundary = bigger.outer_boundary
    else:
        outer = field.region.outer_boundary
        if edit == "segments":
            outer.segments[:] = bigger.outer_boundary.segments
        else:
            for old, new in zip(outer.segments, bigger.outer_boundary.segments):
                old.endpoints[:] = new.get_endpoints()
        # Keep the factory's independently stored containment oracle coherent.
        outer._square_bounds = bigger.outer_boundary._square_bounds
    np.testing.assert_allclose(
        field.evaluate(x, y), rectangle_distance(x, y, (0, 0, 8, 8))
    )


@pytest.mark.parametrize("kind", ["scalar", "array"])
def test_insert_replace_and_remove_live_hole(kind):
    field = SignedDistanceField(region((0, 0, 6, 6)))
    x, y = (3.0, 3.0) if kind == "scalar" else (np.array([3.0]), np.array([3.0]))
    np.testing.assert_array_equal(field.evaluate(x, y), -3)
    field.region.holes.append(region((2, 2, 4, 4)).outer_boundary)
    np.testing.assert_array_equal(field.evaluate(x, y), 1)
    field.region.holes[0] = region((2.5, 2.5, 3.5, 3.5)).outer_boundary
    np.testing.assert_array_equal(field.evaluate(x, y), 0.5)
    field.region.holes.clear()
    np.testing.assert_array_equal(field.evaluate(x, y), -3)


def test_analytic_hole_distance_includes_nearest_hole_edges_and_corners():
    field = SignedDistanceField(region((0, 0, 6, 6)))
    field.region.holes.append(region((2, 2, 4, 4)).outer_boundary)
    x = np.array([1.8, 2.0, 3.0, 3.0, 4.2, 1.8, -1.0])
    y = np.array([3.0, 3.0, 3.0, 4.0, 3.0, 1.8, 3.0])
    # Box with one box hole: intersection of outer and hole-complement SDFs.
    expected = np.maximum(
        rectangle_distance(x, y, (0, 0, 6, 6)), -rectangle_distance(x, y, (2, 2, 4, 4))
    )
    np.testing.assert_allclose(field.evaluate(x, y), expected, atol=1e-14)


@pytest.mark.parametrize(
    "scale,offset", [(0.01, 0.0), (1.0, 0.0), (1e6, 0.0), (1.0, 1e6)]
)
def test_box_distance_uses_geometry_units(scale, offset):
    bounds = (offset, offset, offset + 4 * scale, offset + 4 * scale)
    x, y = offset + scale * np.array([-1.0, 1.0, 5.0]), offset + 2 * scale
    np.testing.assert_allclose(
        SignedDistanceField(region(bounds)).evaluate(x, y),
        rectangle_distance(x, y, bounds),
        atol=1e-10 * scale,
    )


@pytest.mark.parametrize("expression_scale", [0.1, 1.0, 10.0])
def test_circle_sampling_is_distance_approximation_not_implicit_value(expression_scale):
    x, y = sp.symbols("x y")
    curve = ConicSection(expression_scale * (x * x + y * y - 4), (x, y))
    field = SignedDistanceField(
        AreaRegion(CompositeCurve([TrimmedImplicitCurve(curve, lambda x, y: True)]))
    )
    xx, yy = np.array([0.0, 1.0, 3.0, -3.0]), np.array([0.0, 0.25, 0.5, 0.0])
    expected = np.hypot(xx, yy) - 2
    # Explicit analytic error budget for the existing sampled circle approximation.
    # The sampler is not assumed to produce uniform-angle or exact circle vertices.
    np.testing.assert_allclose(
        field.evaluate(xx, yy),
        expected,
        rtol=0,
        atol=0.01,
    )
    assert CurveField(curve).evaluate(3.0, 0.0) == pytest.approx(5 * expression_scale)
    assert field.evaluate(3.0, 0.0) == pytest.approx(1.0, abs=0.005)


@pytest.mark.parametrize("kind", ["scalar", "broadcast", "list", "zero_dim"])
def test_shape_and_gradient_paths(kind):
    field = SignedDistanceField(region())
    x, y = 5.0, 2.0
    if kind == "broadcast":
        x, y = np.array([[5.0], [6.0]]), np.array([1.0, 2.0, 3.0])
    elif kind == "list":
        x, y = [5.0, 6.0], [2.0, 2.0]
    elif kind == "zero_dim":
        x, y = np.array(5.0), np.array(2.0)
    result = field.evaluate(x, y)
    np.testing.assert_allclose(result, rectangle_distance(x, y), atol=1e-14)
    gx, gy = field.gradient(x, y)
    np.testing.assert_allclose(gx, np.ones(np.shape(result)), atol=1e-12)
    np.testing.assert_allclose(gy, np.zeros(np.shape(result)), atol=1e-12)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_invalid_input_cannot_reuse_a_warm_cache(bad):
    field = SignedDistanceField(region())
    x, y = np.ones((5, 5)), np.full((5, 5), 2.0)
    field.evaluate(x, y)
    x[0, 1] = bad
    actual = field.evaluate(x, y)
    assert np.isnan(actual[0, 1])
    np.testing.assert_array_equal(np.delete(actual.ravel(), 1), -1)
    assert np.isnan(field.evaluate(bad, 2.0))


def test_no_query_buffer_retention_and_empty_shapes():
    field = SignedDistanceField(region())
    references = []
    for _ in range(3):
        x, y = np.ones((97, 97)), np.full((97, 97), 2.0)
        result = field.evaluate(x, y)
        references.extend(weakref.ref(v) for v in (x, y, result))
        del x, y, result
    gc.collect()
    assert all(ref() is None for ref in references)
    assert field._cache is field._cached_segments_ab is None
    assert field.evaluate(np.empty((0, 3)), 2.0).shape == (0, 3)


def test_serialization_and_level_wrapper_remain_live():
    field = SignedDistanceField.from_dict(SignedDistanceField(region()).to_dict())
    level = field.level_set(1.0)
    assert level.evaluate(-1.0, 2.0) == 0.0
    field.region = region((-4, -4, 4, 4))
    assert level.evaluate(-1.0, 2.0) == -3.0


@pytest.mark.parametrize("edit", ["segments", "endpoints"])
def test_generic_native_polygon_sign_after_inplace_geometry_edit(edit):
    boundary = CompositeCurve(region().outer_boundary.segments)
    field = SignedDistanceField(AreaRegion(boundary))
    x, y = np.ones(5), np.full(5, 2.0)
    np.testing.assert_allclose(field.evaluate(x, y), -1)
    moved = region((10, 0, 14, 4)).outer_boundary
    if edit == "segments":
        boundary.segments[:] = moved.segments
    else:
        for old, new in zip(boundary.segments, moved.segments):
            old.endpoints[:] = new.get_endpoints()
            # Segment boundary tests depend on a separate curve expression.
            old.base_curve = new.base_curve
    # Both the generic polygon query and signed-distance query must read live edges.
    assert not boundary.contains(x, y, region_containment=True).any()
    expected = rectangle_distance(x, y, (10, 0, 14, 4))
    np.testing.assert_allclose(field.evaluate(x, y), expected)
    assert field.evaluate(1.0, 2.0) == 9
    assert boundary._cached_polygon_segments is None


def test_large_coordinate_gradient_is_not_collapsed_by_close_cache_match():
    field = SignedDistanceField(region())
    field.evaluate(np.array([1e6, 1e6]), np.array([2.0, 2.0]))
    gx, gy = field.gradient(np.array([1e6, 1e6]), np.array([2.0, 2.0]))
    np.testing.assert_allclose(gx, 1.0, atol=2e-8)
    np.testing.assert_array_equal(gy, 0.0)


def test_scalar_callbacks_keep_float_probe_arguments():
    field = SignedDistanceField(region())
    original = field.region.contains

    def scalar_contains(x, y):
        assert isinstance(x, float) and isinstance(y, float)
        return original(x, y)

    field.region.contains = scalar_contains
    assert field.evaluate(5.0, 2.0) == 1.0
    np.testing.assert_allclose(field.gradient(5.0, 2.0), (1.0, 0.0), atol=1e-12)


def test_unavailable_boundary_has_no_fabricated_unit_distance():
    field = SignedDistanceField(region())
    field.region.outer_boundary.segments.clear()
    field.region._curve_to_polygon = lambda boundary: []
    with pytest.raises(ValueError, match="no available segments"):
        field.evaluate(5.0, 2.0)


def test_polygon_segment_results_are_defensive_and_not_retained():
    boundary = CompositeCurve(region().outer_boundary.segments)
    first = boundary.get_polygon_segments()
    first[:] = []
    assert len(boundary.get_polygon_segments()) == 4
    assert boundary._cached_polygon_segments is None
