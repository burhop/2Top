"""Geometric SDF signs stay distinct from intentionally fuzzy region containment."""

import numpy as np
import pytest
import sympy as sp
from fractions import Fraction

from geometry import AreaRegion, CompositeCurve, ConicSection, create_square_from_edges
from geometry.field_strategy import SignedDistanceField
from geometry.factories import create_polygon_from_edges
from geometry.numeric import endpoint_polygon_inside
from geometry.precision import PrecisionPolicy
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from tests.test_distance_numerics import exact_distance


def square(low, high):
    return create_square_from_edges((low, low), (high, high))


@pytest.mark.parametrize(
    "scale,offset",
    [(1e-200, 0.0), (1e-6, 0.0), (1.0, 0.0), (1e200, 0.0), (1.0, 1e6), (1e185, 1e200)],
)
@pytest.mark.parametrize("kind", ["scalar", "array", "zero_dim"])
def test_native_outer_hole_signs_match_analytic_geometry(scale, offset, kind):
    outer = square(offset, offset + 6 * scale)
    hole = square(offset + 2 * scale, offset + 4 * scale)
    region = AreaRegion(outer, [hole])
    field = SignedDistanceField(region)
    # Simple points keep their intended geometric status after binary64 translation.
    points = [
        (offset + 3 * scale, offset + 3 * scale, 1),
        (offset + 1.5 * scale, offset + 3 * scale, -1),
        (offset + 2.5 * scale, offset + 1.5 * scale, -1),
        (offset - scale, offset + 3 * scale, 1),
    ]
    endpoints = [
        (a, b)
        for boundary in (outer, hole)
        for a, b in [segment.get_endpoints() for segment in boundary.segments]
    ]
    for x, y, sign in points:
        expected = sign * min(exact_distance(a, b, (x, y)) for a, b in endpoints)
        if kind == "array":
            x, y = np.array([x]), np.array([y])
        elif kind == "zero_dim":
            x, y = np.array(x), np.array(y)
        np.testing.assert_allclose(field.evaluate(x, y), expected, rtol=4e-15, atol=0.0)


@pytest.mark.parametrize("scale", [1e-200, 1e-6, 1.0, 1e200])
@pytest.mark.parametrize("hole", [False, True])
def test_exact_native_boundary_is_canonical_positive_zero(scale, hole):
    outer = square(0.0, 6 * scale)
    holes = [square(2 * scale, 4 * scale)] if hole else []
    field = SignedDistanceField(AreaRegion(outer, holes))
    boundary = holes[0] if hole else outer
    points = []
    for a, b in [segment.get_endpoints() for segment in boundary.segments]:
        points += [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)]
    x, y = np.array(points).T
    result = field.evaluate(x, y)
    np.testing.assert_array_equal(result, 0.0)
    assert not np.signbit(result).any()
    for point in points:
        value = field.evaluate(*point)
        assert value == 0.0 and not np.signbit(value)


@pytest.mark.parametrize("scale", [1e-200, 1e-6, 1.0, 1e200])
@pytest.mark.parametrize("boundary", ["outer", "hole"])
def test_representable_neighbors_have_correct_sign(scale, boundary):
    field = SignedDistanceField(
        AreaRegion(square(0.0, 6 * scale), [square(2 * scale, 4 * scale)])
    )
    edge = 0.0 if boundary == "outer" else 2 * scale
    left, right = np.nextafter(edge, -np.inf), np.nextafter(edge, np.inf)
    values = field.evaluate(np.array([left, right]), 3 * scale)
    expected_signs = [1, -1] if boundary == "outer" else [-1, 1]
    assert np.signbit(values).tolist() == [s < 0 for s in expected_signs]
    for x, sign in zip((left, right), expected_signs):
        assert np.signbit(field.evaluate(float(x), float(3 * scale))) == (sign < 0)


def test_default_and_explicit_containment_tolerances_are_preserved():
    region = AreaRegion(square(0.0, 6e-6), [square(2e-6, 4e-6)])
    policy = region.precision_policy()
    default = region.contains(1.5e-6, 3e-6)
    explicit = region.contains(1.5e-6, 3e-6, tolerance=0.0)
    assert default is False and explicit is True
    field = SignedDistanceField(region)
    assert field.evaluate(1.5e-6, 3e-6) == pytest.approx(-5e-7, rel=2e-15, abs=0.0)
    assert region.contains(1.5e-6, 3e-6) is default
    assert region.precision_policy() is policy
    # No hole: default outer dilation continues to accept a nearby exterior point.
    outer = AreaRegion(square(0.0, 4.0))
    assert outer.contains(-1e-5, 2.0) and not outer.contains(-1e-5, 2.0, tolerance=0.0)
    assert SignedDistanceField(outer).evaluate(-1e-5, 2.0) == 1e-5
    assert outer.contains(-1e-5, 2.0)


@pytest.mark.parametrize("distance", [1e-7, 1e-5, 1e-3])
def test_positive_scale_circle_sign_is_independent_of_field_units(distance):
    x, y = sp.symbols("x y")
    for factor in (1e-6, 1.0, 1e6):
        curve = ConicSection(factor * (x * x + y * y - 1), (x, y))
        field = SignedDistanceField(
            AreaRegion(CompositeCurve([TrimmedImplicitCurve(curve, lambda x, y: True)]))
        )
        assert field.evaluate(1 - distance, 0.0) < 0
        assert field.evaluate(1 + distance, 0.0) > 0
        # At the unsampled smooth boundary, magnitude is still a chord approximation.
        assert abs(field.evaluate(1.0, 0.0)) < 0.01


def test_public_precision_changes_do_not_expand_the_distance_sign_band():
    region = AreaRegion(square(0.0, 4.0))
    field = SignedDistanceField(region)
    before = field.evaluate(-1e-5, 2.0)
    region._precision_policy = PrecisionPolicy(absolute=10.0, distance_factor=10.0)
    assert region.contains(-1.0, 2.0)
    assert field.evaluate(-1e-5, 2.0) == before


def test_broadcast_nonfinite_and_live_holes_keep_sign_contract():
    region = AreaRegion(square(0.0, 6e-6))
    field = SignedDistanceField(region)
    x, y = np.array([[1.5e-6], [3e-6]]), np.array([3e-6, np.nan])
    before = field.evaluate(x, y)
    assert (before[:, 0] < 0).all() and np.isnan(before[:, 1]).all()
    region.holes.append(square(2e-6, 4e-6))
    after = field.evaluate(x, y)
    assert after[0, 0] < 0 and after[1, 0] > 0 and np.isnan(after[:, 1]).all()


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    "scale,offset", [(1e-6, 0.0), (1.0, 0.0), (1e6, 0.0), (1.0, 1e6)]
)
def test_concave_endpoint_geometry_ignores_trim_padding(reverse, scale, offset):
    points = [(0, 0), (4, 0), (4, 4), (2, 2), (0, 4)]
    points = [(offset + scale * x, offset + scale * y) for x, y in points]
    if reverse:
        points.reverse()
    field = SignedDistanceField(AreaRegion(create_polygon_from_edges(points)))
    for x, y, sign in [(1, 1, -1), (2, 3, 1), (5, 1, 1)]:
        x, y = offset + scale * x, offset + scale * y
        assert np.signbit(field.evaluate(x, y)) == (sign < 0)
        assert np.signbit(field.evaluate(np.array([x]), np.array([y]))[0]) == (sign < 0)


@pytest.mark.parametrize("kind", ["generic", "concave"])
def test_outside_endpoint_extension_is_positive_even_when_contains_accepts_it(kind):
    if kind == "generic":
        boundary = CompositeCurve(square(0.0, 4.0).segments)
        point = (4.000001, 0.0)
    else:
        boundary = create_polygon_from_edges([(0, 0), (4, 0), (4, 4), (2, 2), (0, 4)])
        point = (4 + 5e-13, 0.0)
    region = AreaRegion(boundary)
    assert region.contains(*point, tolerance=0.0)
    field = SignedDistanceField(region)
    assert field.evaluate(*point) > 0
    assert field.evaluate(np.array([point[0]]), point[1])[0] > 0
    assert region.contains(*point, tolerance=0.0)


@pytest.mark.parametrize("callback_kind", ["two_args", "tolerance", "uninspectable"])
def test_custom_contains_callbacks_keep_calling_convention(callback_kind):
    region = AreaRegion(square(0.0, 4.0))
    calls = []

    def two_args(x, y):
        calls.append((x, y))
        return False

    def tolerance(x, y, *, tolerance=None):
        assert tolerance == 0.0
        return two_args(x, y)

    class Uninspectable:
        @property
        def __signature__(self):
            raise ValueError("Unavailable signature")

        def __call__(self, x, y):
            return two_args(x, y)

    region.contains = {
        "two_args": two_args,
        "tolerance": tolerance,
        "uninspectable": Uninspectable(),
    }[callback_kind]
    field = SignedDistanceField(region)
    assert field.evaluate(2.0, 2.0) == 2.0
    assert all(isinstance(v, float) for v in calls[-1])
    assert field.evaluate(np.array([2.0]), 2.0)[0] == 2.0
    assert isinstance(calls[-1][0], np.ndarray)


def test_callback_internal_typeerror_propagates_without_retry():
    region = AreaRegion(square(0.0, 4.0))
    calls = []

    def contains(x, y, tolerance=None):
        calls.append(tolerance)
        raise TypeError("callback internal failure")

    region.contains = contains
    with pytest.raises(TypeError, match="callback internal failure"):
        SignedDistanceField(region).evaluate(2.0, 2.0)
    assert calls == [0.0]


def test_boundary_callback_is_authoritative():
    region = AreaRegion(square(0.0, 4.0))
    region.outer_boundary.contains = lambda x, y, **kwargs: False
    assert not region.contains(1.0, 2.0)
    assert SignedDistanceField(region).evaluate(1.0, 2.0) == 1.0


@pytest.mark.parametrize(
    "points,queries",
    [
        ([(0.0, -1e308), (10.0, 1e308), (10.0, -1e308)], [(1.0, 0.0), (9.0, 0.0)]),
        (
            [(0.0, 0.0), (1e308, 1e308), (1e308, 0.0)],
            [(5e-201, 1e-200), (2e-200, 1e-200)],
        ),
        (
            [(0.0, 0.0), (7.0, 11.0), (7.0, 0.0)],
            [(3.5, np.nextafter(5.5, -np.inf)), (3.5, np.nextafter(5.5, np.inf))],
        ),
        (
            [(1e200, 1e200), (1e200 + 1e185, 1e200 + 2e185), (1e200 + 2e185, 1e200)],
            [(1e200 + 1e185, 1e200 + 1e185)],
        ),
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_strict_ray_crossing_matches_exact_rational_oracle(points, queries, reverse):
    if reverse:
        points = points[::-1]
    edges = list(zip(points, points[1:] + points[:1]))
    expected = []
    for x, y in queries:
        qx, qy = Fraction(x), Fraction(y)
        inside = False
        for a, b in edges:
            ax, ay, bx, by = [Fraction(v) for v in (*a, *b)]
            if (ay <= qy < by) or (by <= qy < ay):
                inside ^= qx < ax + (qy - ay) * (bx - ax) / (by - ay)
        expected.append(inside)
        assert endpoint_polygon_inside(x, y, edges) == inside
    x, y = np.array(queries).T
    np.testing.assert_array_equal(endpoint_polygon_inside(x, y, edges), expected)


def test_endpoint_sign_requires_closed_valid_geometry():
    with pytest.raises(ValueError, match="closed"):
        endpoint_polygon_inside(0.0, 0.0, [[(0.0, 0.0), (1.0, 1.0)]])
    with pytest.raises(ValueError, match="finite"):
        endpoint_polygon_inside(0.0, 0.0, [[(0.0, 0.0), (np.inf, 1.0)]])


def test_multiple_holes_use_independent_strict_endpoint_membership():
    field = SignedDistanceField(
        AreaRegion(square(0.0, 10.0), [square(1.0, 3.0), square(6.0, 8.0)])
    )
    x = np.array([2.0, 7.0, 5.0, -1.0])
    y = np.array([2.0, 7.0, 5.0, 5.0])
    np.testing.assert_array_equal(
        np.signbit(field.evaluate(x, y)), [False, False, True, False]
    )
    for px, py, inside in zip(x, y, [False, False, True, False]):
        assert np.signbit(field.evaluate(float(px), float(py))) == inside
