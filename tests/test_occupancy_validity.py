"""Analytic binary-mask reference cases and explicit invalid geometry contracts."""

import numpy as np
import pytest
import sympy as sp

from geometry import (
    AreaRegion,
    CompositeCurve,
    ConicSection,
    OccupancyField,
    create_square_from_edges,
)
from geometry.base_field import BlendedField, CurveField
from geometry.implicit_curve import ImplicitCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

x, y = sp.symbols("x y")


def square(a=(0.0, 0.0), b=(4.0, 4.0), holes=None):
    return AreaRegion(create_square_from_edges(a, b), holes)


def coordinate(expression):
    return CurveField(ImplicitCurve(sp.sympify(expression), (x, y)))


@pytest.mark.parametrize(
    "point", [(0.0, 2.0), (4.0, 2.0), (2.0, 0.0), (2.0, 4.0), (0.0, 0.0), (4.0, 4.0)]
)
def test_square_jump_gradient_and_composed_normal(point):
    field = OccupancyField(square())
    assert field.evaluate(*point) == 0.0
    assert np.isnan(field.gradient(*point)).all()
    composed = BlendedField([field, coordinate(x + 2 * y)])
    with pytest.raises(ValueError, match="Normal undefined"):
        composed.level_set(0.0).normal(*point)


@pytest.mark.parametrize(
    "distance",
    [
        0.0,
        0.5e-8,
        1e-8,
        np.nextafter(1e-8, np.inf),
        1.5e-8,
        2e-8,
        -0.5e-8,
        -1e-8,
        -1.5e-8,
    ],
)
def test_guard_includes_legacy_tolerance_transition(distance):
    field = OccupancyField(square())
    assert np.isnan(field.gradient(distance, 2.0)).all()
    expected = 1.0 if distance > 1e-8 else 0.0
    assert field.evaluate(distance, 2.0) == expected


@pytest.mark.parametrize(
    "point,inside",
    [
        ((2.0, 2.0), True),
        ((-1.0, 2.0), False),
        ((5.0, 2.0), False),
        ((1e-6, 2.0), True),
    ],
)
def test_regular_piece_reference(point, inside):
    field = OccupancyField(square(), 7.0, -3.0)
    assert field.evaluate(*point) == (7.0 if inside else -3.0)
    assert field.gradient(*point) == (0.0, 0.0)
    assert BlendedField([field, coordinate(y)]).level_set(0.0).normal(*point) == (
        0.0,
        1.0,
    )


def test_hole_boundaries_and_constant_hole_interior():
    field = OccupancyField(
        square(
            (0.0, 0.0), (6.0, 6.0), [create_square_from_edges((2.0, 2.0), (4.0, 4.0))]
        )
    )
    for point in [(2.0, 3.0), (4.0, 3.0), (3.0, 2.0), (3.0, 4.0), (2.0, 2.0)]:
        assert np.isnan(field.gradient(*point)).all()
    assert field.evaluate(3.0, 3.0) == 0.0
    assert field.gradient(3.0, 3.0) == (0.0, 0.0)
    assert field.evaluate(1.0, 1.0) == 1.0
    assert field.gradient(1.0, 1.0) == (0.0, 0.0)


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e6])
def test_circle_field_unit_guard(scale):
    curve = ConicSection(sp.Float(scale) * (x * x + y * y - 1), (x, y))
    field = OccupancyField(
        AreaRegion(CompositeCurve([TrimmedImplicitCurve(curve, lambda x, y: True)]))
    )
    assert np.isnan(field.gradient(1.0, 0.0)).all()
    assert field.gradient(0.0, 0.0) == (0.0, 0.0)
    assert field.gradient(2.0, 0.0) == (0.0, 0.0)
    # Closed-form point inside the exclusion transition (field units).
    near = np.sqrt(1.0 - 1.5e-8 / scale)
    assert np.isnan(field.gradient(near, 0.0)).all()


@pytest.mark.parametrize("center,size", [(1e12, 4.0), (0.0, 1e-6), (0.0, 1e6)])
def test_translated_scaled_square(center, size):
    field = OccupancyField(square((center, center), (center + size, center + size)))
    assert np.isnan(field.gradient(center, center + size / 2)).all()
    assert field.evaluate(center + size / 2, center + size / 2) == 1.0
    assert field.gradient(center + size / 2, center + size / 2) == (0.0, 0.0)


@pytest.mark.parametrize(
    "coordinates,shape,scalar",
    [
        ((2.0, 2.0), (), True),
        ((np.array(2.0), np.array(2.0)), (), False),
        (([[0.0], [2.0]], [1.0, 2.0, 5.0]), (2, 3), False),
        ((np.empty((0, 1)), np.empty((1, 3))), (0, 3), False),
    ],
)
def test_broadcast_shapes_and_scalar_array_parity(coordinates, shape, scalar):
    field = OccupancyField(square())
    result = field.evaluate(*coordinates)
    gradient = field.gradient(*coordinates)
    for value in (result, *gradient):
        assert isinstance(value, float) if scalar else isinstance(value, np.ndarray)
        assert np.shape(value) == shape
    xx, yy = np.broadcast_arrays(*coordinates)
    for index in np.ndindex(shape):
        np.testing.assert_equal(
            result[index] if not scalar else result,
            field.evaluate(float(xx[index]), float(yy[index])),
        )
        np.testing.assert_equal(
            tuple(v[index] for v in gradient) if not scalar else gradient,
            field.gradient(float(xx[index]), float(yy[index])),
        )


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_coordinates_are_undefined(value):
    field = OccupancyField(square())
    for point in [(value, 2.0), (2.0, value)]:
        assert np.isnan(field.evaluate(*point))
        assert np.isnan(field.gradient(*point)).all()
    np.testing.assert_equal(field.evaluate([2.0, value], 2.0), [1.0, np.nan])
    np.testing.assert_equal(
        field.gradient([2.0, value], 2.0), ([0.0, np.nan], [0.0, np.nan])
    )


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, 1j, [1.0, 2.0], "1"])
def test_invalid_output_configuration(value):
    with pytest.raises(ValueError):
        OccupancyField(square(), inside_value=value)
    field = OccupancyField(square())
    field.outside_value = value
    with pytest.raises(ValueError):
        field.gradient(2.0, 2.0)


def test_equal_values_constant_despite_unavailable_boundary():
    region = square()

    def unavailable(*args, **kwargs):
        raise ValueError("boundary unavailable")

    region.contains = region.contains_boundary = unavailable
    field = OccupancyField(region, 3.0, 3.0)
    for point in [(0.0, 2.0), (2.0, 2.0), (-1.0, 2.0)]:
        assert field.evaluate(*point) == 3.0
        assert field.gradient(*point) == (0.0, 0.0)
    assert np.isnan(field.gradient(np.nan, 2.0)).all()


@pytest.mark.parametrize(
    "level,message",
    [(0.5, "empty"), (2.0, "empty"), (0.0, "plateau"), (1.0, "plateau")],
)
def test_discrete_level_sets_are_not_curves(level, message):
    with pytest.raises(ValueError, match=message):
        OccupancyField(square()).level_set(level)


@pytest.mark.parametrize("level", [np.nan, np.inf, 1j])
def test_level_domain_validation(level):
    with pytest.raises((ValueError, TypeError)):
        OccupancyField(square()).level_set(level)


def test_constant_level_plateau_and_empty():
    field = OccupancyField(square(), 2.0, 2.0)
    with pytest.raises(ValueError, match="plateau"):
        field.level_set(2.0)
    with pytest.raises(ValueError, match="empty"):
        field.level_set(0.0)


def test_fresh_mutable_coordinates_values_regions_and_results():
    field = OccupancyField(square())
    xx, yy = np.ones(5), np.full(5, 2.0)
    first = field.evaluate(xx, yy)
    first[0] = 99.0
    xx[1] = -1.0
    np.testing.assert_equal(field.evaluate(xx, yy), [1.0, 0.0, 1.0, 1.0, 1.0])
    other = xx.copy()
    other[3] = -1.0
    np.testing.assert_equal(field.evaluate(other, yy), [1.0, 0.0, 1.0, 0.0, 1.0])
    field.inside_value, field.outside_value = 3.0, -2.0
    np.testing.assert_equal(field.evaluate(xx, yy), [3.0, -2.0, 3.0, 3.0, 3.0])
    field.region.holes = [create_square_from_edges((0.5, 0.5), (1.5, 2.5))]
    np.testing.assert_equal(field.evaluate(xx, yy), [-2.0, -2.0, -2.0, -2.0, -2.0])
    field.region.holes = []
    np.testing.assert_equal(field.evaluate(xx, yy), [3.0, -2.0, 3.0, 3.0, 3.0])
    field.region.outer_boundary = square((10.0, 10.0), (14.0, 14.0)).outer_boundary
    np.testing.assert_equal(field.evaluate(xx, yy), [-2.0, -2.0, -2.0, -2.0, -2.0])
    field.region = square((10.0, 10.0), (14.0, 14.0))
    np.testing.assert_equal(field.evaluate(xx, yy), [-2.0, -2.0, -2.0, -2.0, -2.0])
    field.clear_cache()
    assert field._cache is None
    np.testing.assert_equal(yy, np.full(5, 2.0))


def test_mutable_native_expression_and_invalid_domain():
    source = ConicSection(x * x + y * y - 1, (x, y))
    field = OccupancyField(
        AreaRegion(CompositeCurve([TrimmedImplicitCurve(source, lambda x, y: True)]))
    )
    assert field.evaluate(2.0, 0.0) == 0.0
    source.expression = x * x + y * y - 9
    assert field.evaluate(2.0, 0.0) == 1.0
    source.evaluate = lambda x, y: np.nan + np.zeros_like(x)
    assert np.isnan(field.evaluate(2.0, 0.0))
    assert np.isnan(field.gradient(2.0, 0.0)).all()


def test_singular_source_zero_boundary_is_uncertain():
    source = ConicSection(x * x + y * y - 1, (x, y))
    field = OccupancyField(
        AreaRegion(CompositeCurve([TrimmedImplicitCurve(source, lambda x, y: True)]))
    )
    source.expression = sp.Integer(0)
    assert field.evaluate(2.0, 0.0) == 0.0
    assert np.isnan(field.gradient(2.0, 0.0)).all()


def test_mutated_open_region_rejected():
    region = square()
    field = OccupancyField(region)
    region.outer_boundary.segments = region.outer_boundary.segments[:2]
    with pytest.raises(ValueError, match="closed"):
        field.gradient(2.0, 2.0)


def test_unavailable_or_malformed_boundary_is_explicit():
    field = OccupancyField(square())
    field.region.contains_boundary = lambda *args, **kwargs: np.nan
    with pytest.raises(ValueError, match="booleans"):
        field.gradient(2.0, 2.0)

    def unavailable(*args, **kwargs):
        raise ValueError("boundary unavailable")

    field.region.contains_boundary = unavailable
    with pytest.raises(ValueError, match="unavailable"):
        field.gradient(2.0, 2.0)


def test_inactive_occupancy_jump_does_not_contaminate_strict_winner():
    field = OccupancyField(square())
    blend = BlendedField([field, coordinate(y - 10)], "min")
    assert blend.gradient(0.0, 2.0) == (0.0, 1.0)
    assert blend.level_set(0.0).normal(0.0, 2.0) == (0.0, 1.0)


def test_serialization_contract_retained():
    field = OccupancyField(square(), 4.0, -2.0)
    restored = OccupancyField.from_dict(field.to_dict())
    assert restored.to_dict() == field.to_dict()
    assert restored.evaluate(2.0, 2.0) == 4.0
    assert np.isnan(restored.gradient(0.0, 2.0)).all()


def test_scalar_only_predicates_and_source_callbacks_keep_float_arguments():
    field = OccupancyField(square())

    def wrap(callback):
        def scalar(x, y, **kwargs):
            assert np.isscalar(x) and np.isscalar(y)
            return callback(x, y, **kwargs)

        return scalar

    field.region.contains = wrap(field.region.contains)
    field.region.contains_boundary = wrap(field.region.contains_boundary)
    for segment in field.region.outer_boundary.segments:
        segment.evaluate = wrap(segment.evaluate)
    assert field.evaluate(2.0, 2.0) == 1.0
    assert field.gradient(2.0, 2.0) == (0.0, 0.0)
    assert np.isnan(field.gradient(0.0, 2.0)).all()


def test_unknown_containment_is_not_a_confident_gradient():
    field = OccupancyField(square())
    field.region.contains = lambda *args, **kwargs: np.nan
    for method in [field.evaluate, field.gradient]:
        with pytest.raises(ValueError, match="booleans"):
            method(2.0, 2.0)


def test_pointwise_invalid_source_domain_masks_only_affected_points():
    field = OccupancyField(square())
    field.region.outer_boundary.segments[0].evaluate = lambda x, y: np.sqrt(x)
    np.testing.assert_equal(field.evaluate([-1.0, 2.0], 2.0), [np.nan, 1.0])
    np.testing.assert_equal(
        field.gradient([-1.0, 2.0], 2.0), ([np.nan, 0.0], [np.nan, 0.0])
    )


@pytest.mark.parametrize("hole", [False, True])
@pytest.mark.parametrize(
    "point",
    [(-1e-8, 2.0), (np.nextafter(-1e-8, -np.inf), 2.0), (-1e-8, -1e-8), (1e-9, 2.0)],
)
def test_polygon_trim_tolerance_jumps(hole, point):
    from geometry.factories import create_polygon_from_edges

    polygon = create_polygon_from_edges(
        [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
    )
    region = (
        square((-2.0, -2.0), (6.0, 6.0), [polygon]) if hole else AreaRegion(polygon)
    )
    field = OccupancyField(region)
    assert np.isnan(field.gradient(*point)).all()
    with pytest.raises(ValueError, match="Normal undefined"):
        BlendedField([field, coordinate(y)]).level_set(0.0).normal(*point)


def test_concave_polygon_notch_and_regular_pieces():
    from geometry.factories import create_polygon_from_edges

    polygon = create_polygon_from_edges(
        [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)]
    )
    field = OccupancyField(AreaRegion(polygon))
    for point in [(2.0, 3.0), (3.0, 2.0), (2.0, 2.0)]:
        assert np.isnan(field.gradient(*point)).all()
    assert field.evaluate(1.0, 3.0) == 1.0
    assert field.evaluate(3.0, 3.0) == 0.0
    assert field.gradient(1.0, 3.0) == field.gradient(3.0, 3.0) == (0.0, 0.0)


def test_custom_containment_jump_is_sampled_uncertain():
    source = ConicSection(x * x + y * y - 1, (x, y))
    region = AreaRegion(
        CompositeCurve([TrimmedImplicitCurve(source, lambda x, y: True)])
    )
    original = region.contains
    region.contains = lambda x, y, **kwargs: (
        original(x, y, **kwargs) & (np.asarray(x) >= 0)
    )
    field = OccupancyField(region)
    assert field.evaluate(-1e-6, 0.0) == 0.0
    assert field.evaluate(1e-6, 0.0) == 1.0
    assert np.isnan(field.gradient(0.0, 0.0)).all()


def test_mutated_trim_mask_invalidates_closed_region():
    source = ConicSection(x * x + y * y - 1, (x, y))
    trimmed = TrimmedImplicitCurve(source, lambda x, y: True)
    field = OccupancyField(AreaRegion(CompositeCurve([trimmed])))
    trimmed.mask = lambda x, y: x >= 0
    with pytest.raises(ValueError, match="closed"):
        field.gradient(0.0, 0.0)


@pytest.mark.parametrize("value", [np.float32(3.0), np.array(3.0)])
def test_live_real_scalar_configuration_serializes(value):
    import json

    field = OccupancyField(square())
    field.inside_value = value
    payload = json.loads(json.dumps(field.to_dict()))
    assert payload["inside_value"] == 3.0
    assert OccupancyField.from_dict(payload).evaluate(2.0, 2.0) == 3.0
    field.inside_value = np.nan
    with pytest.raises(ValueError):
        field.to_dict()


@pytest.mark.parametrize("scale", [1e-300, 1e300])
def test_jump_validity_independent_of_finite_output_scale(scale):
    field = OccupancyField(square(), scale, 0.0)
    assert field.evaluate(2.0, 2.0) == scale
    assert field.gradient(2.0, 2.0) == (0.0, 0.0)
    assert np.isnan(field.gradient(0.0, 2.0)).all()
