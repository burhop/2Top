"""Analytic gradients, genuine singularities and legacy callback/source contracts."""

from decimal import Decimal, localcontext
from fractions import Fraction
import copy

import numpy as np
import pytest
import sympy as sp

from geometry import AreaRegion, CompositeCurve, ConicSection, create_square_from_edges
from geometry.factories import create_polygon_from_edges
from geometry.field_strategy import SignedDistanceField
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve


def square(low=0.0, high=4.0):
    return create_square_from_edges((low, low), (high, high))


def reverse(boundary):
    for segment in boundary.segments:
        segment.endpoints = list(reversed(segment.get_endpoints()))
    boundary.segments.reverse()
    return boundary


def assert_gradient(field, point, expected):
    np.testing.assert_allclose(
        field.gradient(*point), expected, rtol=8e-15, atol=0.0, equal_nan=True
    )
    x, y = point
    array = field.gradient(np.array([x]), np.array([y]))
    np.testing.assert_allclose(
        np.array(array)[:, 0], expected, rtol=8e-15, atol=0.0, equal_nan=True
    )


@pytest.mark.parametrize(
    "scale,offset",
    [(1e-200, 0.0), (1e-6, 0.0), (1.0, 0.0), (1e200, 0.0), (1.0, 1e6), (1e185, 1e200)],
)
@pytest.mark.parametrize("reversed", [False, True])
def test_smooth_square_gradient_is_geometric_across_scales_and_translations(
    scale, offset, reversed
):
    boundary = square(offset, offset + 4 * scale)
    field = SignedDistanceField(AreaRegion(reverse(boundary) if reversed else boundary))
    points = [
        ((2.0, 1.0), (0.0, -1.0)),
        ((2.0, 0.0), (0.0, -1.0)),
        ((2.0, -1.0), (0.0, -1.0)),
        ((3.0, 2.0), (1.0, 0.0)),
        ((1.0, 2.0), (-1.0, 0.0)),
        ((2.0, 3.0), (0.0, 1.0)),
    ]
    for (x, y), expected in points:
        assert_gradient(field, (offset + x * scale, offset + y * scale), expected)


@pytest.mark.parametrize("scale", [1e-200, 1e-6, 1.0, 1e200])
@pytest.mark.parametrize("reversed", [False, True])
def test_square_corners_and_medial_axes_are_undefined(scale, reversed):
    boundary = square(0.0, 4 * scale)
    field = SignedDistanceField(AreaRegion(reverse(boundary) if reversed else boundary))
    for x, y in [
        (0.0, 0.0),
        (4.0, 0.0),
        (4.0, 4.0),
        (0.0, 4.0),
        (1.0, 1.0),
        (2.0, 2.0),
        (3.0, 3.0),
    ]:
        assert_gradient(field, (x * scale, y * scale), (np.nan, np.nan))


@pytest.mark.parametrize("scale", [1e-200, 1.0, 1e200])
def test_representable_medial_neighbors_have_unique_gradients(scale):
    field = SignedDistanceField(AreaRegion(square(0.0, 4 * scale)))
    for x, expected in [
        (np.nextafter(2 * scale, -np.inf), (-1.0, 0.0)),
        (np.nextafter(2 * scale, np.inf), (1.0, 0.0)),
    ]:
        assert_gradient(field, (x, 2 * scale), expected)
    assert_gradient(field, (np.nextafter(scale, -np.inf), scale), (-1.0, 0.0))
    assert_gradient(field, (np.nextafter(scale, np.inf), scale), (0.0, -1.0))


@pytest.mark.parametrize("scale", [1e-200, 1e-6, 1.0, 1e200])
@pytest.mark.parametrize("reversed", [False, True])
def test_shared_exterior_vertex_and_projection_transition_are_differentiable(
    scale, reversed
):
    boundary = square(0.0, 4 * scale)
    field = SignedDistanceField(AreaRegion(reverse(boundary) if reversed else boundary))
    assert_gradient(field, (-scale, -scale), (-1 / np.sqrt(2), -1 / np.sqrt(2)))
    assert_gradient(field, (-scale, 0.0), (-1.0, 0.0))
    assert_gradient(field, (0.0, -scale), (0.0, -1.0))
    # The point at the corner is singular, but its immediate open-edge and
    # exterior neighbors have well-defined gradients even at subnormal spacing.
    neighbor = np.nextafter(0.0, 1.0)
    assert_gradient(field, (neighbor, 0.0), (0.0, -1.0))
    assert_gradient(field, (0.0, neighbor), (-1.0, 0.0))
    assert_gradient(field, (-neighbor, 0.0), (-1.0, 0.0))


@pytest.mark.parametrize("scale", [1e-200, 1e-6, 1.0, 1e200])
@pytest.mark.parametrize("reversed", [False, True])
def test_hole_normals_and_hole_medial_axes_follow_region_sign(scale, reversed):
    outer, hole = square(0.0, 6 * scale), square(2 * scale, 4 * scale)
    if reversed:
        reverse(outer)
        reverse(hole)
    field = SignedDistanceField(AreaRegion(outer, [hole]))
    for point, expected in [
        ((1.5, 3.0), (1.0, 0.0)),
        ((2.0, 3.0), (1.0, 0.0)),
        ((2.5, 3.0), (1.0, 0.0)),
        ((4.0, 3.0), (-1.0, 0.0)),
        ((3.0, 3.0), (np.nan, np.nan)),
        ((1.0, 3.0), (np.nan, np.nan)),
    ]:
        assert_gradient(field, tuple(v * scale for v in point), expected)


@pytest.mark.parametrize("reversed", [False, True])
def test_collinear_join_keeps_a_smooth_normal_and_duplicate_segments_do_not_create_ties(
    reversed,
):
    points = [(0.0, 0.0), (2.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
    if reversed:
        points.reverse()
    field = SignedDistanceField(AreaRegion(create_polygon_from_edges(points)))
    assert_gradient(field, (2.0, 0.0), (0.0, -1.0))
    assert_gradient(field, (2.0, -1.0), (0.0, -1.0))
    # A complete repeated traversal cancels odd/even interior membership;
    # duplicate distance features must not invent a conflicting nearest point.
    boundary = square()
    boundary.segments = boundary.segments + boundary.segments
    repeated = SignedDistanceField(AreaRegion(boundary))
    assert_gradient(repeated, (-1.0, -1.0), (-1 / np.sqrt(2), -1 / np.sqrt(2)))
    assert_gradient(repeated, (2.0, 0.0), (np.nan, np.nan))


def test_zero_length_incident_segment_does_not_hide_smooth_collinear_join():
    points = [(0.0, 0.0), (2.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
    boundary = create_polygon_from_edges(points)
    point_segment = copy.deepcopy(boundary.segments[1])
    point_segment.endpoints = [(2.0, 0.0), (2.0, 0.0)]
    boundary.segments.insert(1, point_segment)
    field = SignedDistanceField(AreaRegion(boundary))
    assert_gradient(field, (2.0, 0.0), (0.0, -1.0))
    assert_gradient(field, (2.0, -1.0), (0.0, -1.0))


def test_overlapping_and_coincident_hole_boundaries_use_actual_membership():
    first, second = square(2.0, 4.0), square(3.0, 5.0)
    field = SignedDistanceField(AreaRegion(square(0.0, 6.0), [first, second]))
    assert_gradient(field, (4.0, 3.5), (np.nan, np.nan))
    assert_gradient(field, (4.0, 3.0), (np.nan, np.nan))
    assert_gradient(field, (2.0, 3.0), (1.0, 0.0))
    coincident = SignedDistanceField(
        AreaRegion(square(0.0, 6.0), [square(2.0, 4.0), square(2.0, 4.0)])
    )
    assert_gradient(coincident, (2.0, 3.0), (1.0, 0.0))
    empty = SignedDistanceField(AreaRegion(square(), [square()]))
    assert_gradient(empty, (0.0, 2.0), (np.nan, np.nan))
    assert_gradient(empty, (2.0, 1.0), (0.0, 1.0))


def test_narrow_neighbor_boundary_limits_normal_probes():
    field = SignedDistanceField(
        AreaRegion(
            square(0.0, 4.0), [create_square_from_edges((1e-12, 1.0), (2.0, 3.0))]
        )
    )
    assert_gradient(field, (0.0, 2.0), (-1.0, 0.0))
    assert_gradient(field, (1e-12, 2.0), (1.0, 0.0))


def test_live_endpoints_and_holes_are_recomputed_without_retained_queries():
    region = AreaRegion(square(0.0, 6.0))
    field = SignedDistanceField(region)
    assert_gradient(field, (1.5, 3.0), (-1.0, 0.0))
    region.holes.append(square(2.0, 4.0))
    assert_gradient(field, (1.5, 3.0), (1.0, 0.0))
    boundary = region.outer_boundary
    for segment in boundary.segments:
        segment.endpoints = [(x + 10.0, y) for x, y in segment.get_endpoints()]
    region.holes.clear()
    assert_gradient(field, (1.5, 3.0), (-1.0, 0.0))


@pytest.mark.parametrize("form", ["scalar", "zero_dim", "list", "broadcast", "empty"])
def test_gradient_forms_and_nonfinite_mask_keep_fresh_results(form):
    field = SignedDistanceField(AreaRegion(square()))
    if form == "scalar":
        x, y = 2.0, -1.0
    elif form == "zero_dim":
        x, y = np.array(2.0), np.array(-1.0)
    elif form == "list":
        x, y = [2.0, np.nan], [-1.0, -1.0]
    elif form == "broadcast":
        x, y = np.array([[2.0], [np.nan]]), np.array([-1.0, 5.0])
    else:
        x, y = np.empty((0, 3)), np.empty((0, 1))
    gx, gy = field.gradient(x, y)
    shape = np.broadcast_shapes(np.shape(x), np.shape(y))
    assert np.shape(gx) == shape and np.shape(gy) == shape
    if form == "scalar":
        assert isinstance(gx, float) and isinstance(gy, float)
    if form == "zero_dim":
        assert isinstance(gx, np.ndarray) and isinstance(gy, np.ndarray)
    finite = np.isfinite(np.broadcast_to(x, shape))
    np.testing.assert_array_equal(np.isnan(gx), ~finite)
    if shape and np.prod(shape):
        gx[...] = 42.0
        assert not np.any(field.gradient(x, y)[0] == 42.0)


@pytest.mark.parametrize("kind", ["region_two_args", "region_tolerance", "boundary"])
def test_contains_callbacks_preserve_legacy_gradient_and_float_arguments(kind):
    region = AreaRegion(square())
    calls = []

    def contains(x, y, **kwargs):
        calls.append((x, y, kwargs))
        assert isinstance(x, float) and isinstance(y, float)
        return False

    if kind == "region_two_args":
        region.contains = lambda x, y: contains(x, y)
    elif kind == "region_tolerance":
        region.contains = contains
    else:
        region.outer_boundary.contains = contains
    field = SignedDistanceField(region)
    np.testing.assert_allclose(field.gradient(2.0, 1.0), (0.0, 1.0), atol=1e-12)
    assert len(calls) == 4
    if kind != "region_two_args":
        assert all(call[2]["tolerance"] == 0.0 for call in calls)


@pytest.mark.parametrize("subclass", [False, True])
def test_evaluate_overrides_remain_authoritative_for_derivatives(subclass):
    class CustomField(SignedDistanceField):
        def evaluate(self, x, y):
            return 3 * x - 4 * y + 7

    field = (CustomField if subclass else SignedDistanceField)(AreaRegion(square()))
    if not subclass:
        field.evaluate = lambda x, y: 3 * x - 4 * y + 7
    np.testing.assert_allclose(field.gradient(2.0, 1.0), (3.0, -4.0), atol=1e-12)


def test_callback_internal_error_is_not_retried_or_hidden():
    field = SignedDistanceField(AreaRegion(square()))

    def contains(x, y, tolerance=None):
        raise TypeError("gradient callback failure")

    field.region.contains = contains
    with pytest.raises(TypeError, match="gradient callback failure"):
        field.gradient(2.0, 1.0)


@pytest.mark.parametrize("resolution", [0.1, 0.001])
def test_sampled_circle_retains_documented_resolution_based_approximation(resolution):
    x, y = sp.symbols("x y")
    field = SignedDistanceField(
        AreaRegion(
            CompositeCurve(
                [
                    TrimmedImplicitCurve(
                        ConicSection(x * x + y * y - 1, (x, y)), lambda x, y: True
                    )
                ]
            )
        ),
        resolution,
    )
    px, py = 1.3, 0.2
    h = resolution / 10
    # This is the published fallback contract, not a certificate of the smooth
    # source derivative or a replacement of sampled chords by an exact circle.
    expected = (
        (field.evaluate(px + h, py) - field.evaluate(px - h, py)) / (2 * h),
        (field.evaluate(px, py + h) - field.evaluate(px, py - h)) / (2 * h),
    )
    np.testing.assert_array_equal(field.gradient(px, py), expected)


@pytest.mark.parametrize("scale", [1e-200, 1.0, 1e200])
def test_oblique_smooth_normals_use_analytic_three_four_five_geometry(scale):
    # A valid initial factory chain is edited to exact endpoint geometry, the
    # authoritative native SDF contract; unrelated implicit metadata is unused.
    boundary = square()
    points = [
        (0.0, 0.0),
        (3 * scale, 4 * scale),
        (7 * scale, scale),
        (4 * scale, -3 * scale),
    ]
    for i, segment in enumerate(boundary.segments):
        segment.endpoints = [points[i], points[(i + 1) % 4]]
    field = SignedDistanceField(AreaRegion(boundary))
    assert_gradient(field, (1.5 * scale, 2 * scale), (-0.8, 0.6))
    assert_gradient(
        field, (1.5 * scale - 0.08 * scale, 2 * scale + 0.06 * scale), (-0.8, 0.6)
    )


def test_finite_coordinates_with_unrepresentable_distance_have_defined_unit_direction():
    field = SignedDistanceField(
        AreaRegion(create_square_from_edges((-1e308, -1e308), (-5e307, -5e307)))
    )
    assert np.isinf(field.evaluate(1e308, 1e308))
    assert_gradient(field, (1e308, 1e308), (1 / np.sqrt(2), 1 / np.sqrt(2)))


def test_native_gradient_rejects_invalid_endpoint_geometry():
    field = SignedDistanceField(AreaRegion(square()))
    field.region.outer_boundary.segments[0].endpoints[0] = (np.nan, 0.0)
    with pytest.raises(ValueError, match="finite"):
        field.gradient(2.0, 1.0)


@pytest.mark.parametrize("exponent", [340, 358, 359, 400])
@pytest.mark.parametrize("reversed", [False, True])
def test_positive_geometric_distance_rounded_to_zero_keeps_its_defined_gradient(
    exponent, reversed
):
    huge, tiny = 2.0**exponent, 2.0**-exponent
    points = [(huge, huge), (tiny, 2 * tiny), (huge, -huge), (2 * huge, 0.0)]
    boundary = square()
    for i, segment in enumerate(boundary.segments):
        segment.endpoints = [points[i], points[(i + 1) % 4]]
    if reversed:
        reverse(boundary)
    field = SignedDistanceField(AreaRegion(boundary))
    point = (2 * tiny, 3 * tiny)
    # The exact determinant is tiny²>0, even when binary64 magnitude is zero.
    a, b = [tuple(Fraction(v) for v in p) for p in points[:2]]
    px, py = [Fraction(v) for v in point]
    determinant = (px - a[0]) * (b[1] - a[1]) - (py - a[1]) * (b[0] - a[0])
    assert determinant == Fraction(tiny) ** 2 > 0
    if exponent >= 359:
        assert field.evaluate(*point) == 0.0
    assert_gradient(field, point, (-1 / np.sqrt(2), 1 / np.sqrt(2)))


@pytest.mark.parametrize("length", [2.0, np.nextafter(2.0, 0.0)])
@pytest.mark.parametrize("reversed", [False, True])
def test_half_subnormal_unit_components_use_independent_high_precision_normal(
    length, reversed
):
    tiny = np.nextafter(0.0, 1.0)
    points = [(0.0, 0.0), (length, tiny), (length, 1.0), (0.0, 1.0)]
    boundary = square()
    for i, segment in enumerate(boundary.segments):
        segment.endpoints = [points[i], points[(i + 1) % 4]]
    if reversed:
        reverse(boundary)
    field = SignedDistanceField(AreaRegion(boundary))
    with localcontext() as context:
        context.prec = 1500
        dx, dy = Decimal.from_float(length), Decimal.from_float(tiny)
        norm = (dx * dx + dy * dy).sqrt()
        expected = float(dy / norm), float(-dx / norm)
    assert field.evaluate(length / 2, 0.0) == 0.0
    np.testing.assert_array_equal(field.gradient(length / 2, 0.0), expected)
    np.testing.assert_array_equal(
        np.array(field.gradient(np.array([length / 2]), 0.0))[:, 0], expected
    )


def test_self_crossing_boundary_and_backtracking_endpoint_are_undefined():
    boundary = square()
    points = [(0.0, 0.0), (4.0, 4.0), (0.0, 4.0), (4.0, 0.0)]
    for i, segment in enumerate(boundary.segments):
        segment.endpoints = [points[i], points[(i + 1) % 4]]
    assert_gradient(
        SignedDistanceField(AreaRegion(boundary)), (2.0, 2.0), (np.nan, np.nan)
    )
    spike = create_polygon_from_edges(
        [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0), (0.0, 0.0), (-1.0, 0.0)]
    )
    assert_gradient(
        SignedDistanceField(AreaRegion(spike)), (-1.0, 0.0), (np.nan, np.nan)
    )


def test_subnormal_square_keeps_unit_directions_and_resolves_exact_nearest_features():
    tiny = np.nextafter(0.0, 1.0)
    field = SignedDistanceField(AreaRegion(square(0.0, 4 * tiny)))
    for point, expected in [
        ((2 * tiny, tiny), (0.0, -1.0)),
        ((2 * tiny, 0.0), (0.0, -1.0)),
        ((2 * tiny, 2 * tiny), (np.nan, np.nan)),
        ((tiny, 2 * tiny), (-1.0, 0.0)),
        ((3 * tiny, 2 * tiny), (1.0, 0.0)),
        ((-tiny, -tiny), (-1 / np.sqrt(2), -1 / np.sqrt(2))),
    ]:
        assert_gradient(field, point, expected)


@pytest.mark.parametrize("reversed", [False, True])
def test_rounded_axis_distances_resolve_using_actual_coordinate_low_parts(reversed):
    boundary = square(-1.0, 3.0)
    if reversed:
        reverse(boundary)
    field = SignedDistanceField(AreaRegion(boundary))
    delta = 2.0**-100
    for point, expected in [
        ((-delta, 0.0), (-1.0, 0.0)),
        ((delta, 0.0), (0.0, -1.0)),
        ((-delta, -2 * delta), (0.0, -1.0)),
        ((delta, 2 * delta), (-1.0, 0.0)),
        ((-delta, -delta), (np.nan, np.nan)),
    ]:
        assert_gradient(field, point, expected)


@pytest.mark.parametrize("reversed", [False, True])
def test_rectilinear_concave_normals_and_conflicts_use_exact_side_limits(reversed):
    points = [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)]
    if reversed:
        points.reverse()
    field = SignedDistanceField(AreaRegion(create_polygon_from_edges(points)))
    for point, expected in [
        ((2.0, 3.0), (1.0, 0.0)),
        ((3.0, 2.0), (0.0, 1.0)),
        ((2.0, 2.0), (np.nan, np.nan)),
        ((3.0, 3.0), (np.nan, np.nan)),
        ((0.5, 3.0), (-1.0, 0.0)),
        ((3.0, 0.5), (0.0, -1.0)),
    ]:
        assert_gradient(field, point, expected)
