"""Exact rational projection and analytic region oracles for binary64 distances."""

from decimal import Decimal, localcontext
from fractions import Fraction

import numpy as np
import pytest

from geometry import AreaRegion, create_square_from_edges
from geometry.field_strategy import SignedDistanceField
from geometry.numeric import segment_distance
from geometry.precision import PrecisionPolicy


def exact_distance(start, end, point):
    """Exact rational residual projection, then an independent 1500-digit sqrt."""
    a, b, p = [
        tuple(Fraction.from_float(float(v)) for v in pair)
        for pair in (start, end, point)
    ]
    d, w = [b[i] - a[i] for i in range(2)], [p[i] - a[i] for i in range(2)]
    length_sq = sum(v * v for v in d)
    t = (
        min(
            Fraction(1),
            max(Fraction(0), sum(w[i] * d[i] for i in range(2)) / length_sq),
        )
        if length_sq
        else Fraction(0)
    )
    squared = sum((w[i] - t * d[i]) ** 2 for i in range(2))
    with localcontext() as context:
        context.prec = 1500
        return float((Decimal(squared.numerator) / Decimal(squared.denominator)).sqrt())


SUB = np.nextafter(0.0, 1.0)
MAX = np.finfo(float).max


@pytest.mark.parametrize("exponent", [-201, -200, -100, 0, 100, 199, 200, 201])
@pytest.mark.parametrize("offset", [0.0, 32.0])
@pytest.mark.parametrize("reverse", [False, True])
def test_guarded_endpoint_projection_matches_rational_oracle(exponent, offset, reverse):
    scale = 2.0**exponent
    start = (offset * scale, -offset * scale)
    end = ((offset + 3) * scale, (4 - offset) * scale)
    if reverse:
        start, end = end, start
    # Exterior endpoint regions, interior projection, cancellation and both
    # adjacent representable sides of the normal plane at each endpoint.
    points = [
        (offset - 2, -offset - 3),
        (offset + 5, 7 - offset),
        (offset + 1.5, 3 - offset),
    ]
    points = [(x * scale, y * scale) for x, y in points]
    for a in (start, end):
        points += [(np.nextafter(a[0], side), a[1]) for side in (-np.inf, np.inf)]
    expected = [exact_distance(start, end, p) for p in points]
    x, y = np.array(points).T
    np.testing.assert_allclose(
        segment_distance(x, y, start, end), expected, rtol=8e-15, atol=0.0
    )
    for point, value in zip(points, expected):
        assert float(segment_distance(*point, start, end)) == pytest.approx(
            value, rel=8e-15, abs=0.0
        )


@pytest.mark.parametrize(
    "scale", [2.0**-201, 2.0**-200, 1.0, 2.0**200, 2.0**201, 1e-200, 1e200]
)
@pytest.mark.parametrize("reverse", [False, True])
def test_box_pruned_minimum_matches_exact_rational_projection(scale, reverse):
    angles = np.linspace(0.0, 2 * np.pi, 12, endpoint=False)
    points = [
        (float(scale * (32 + 3 * np.cos(a))), float(scale * (-32 + 4 * np.sin(a))))
        for a in angles
    ]
    edges = list(zip(points, points[1:] + points[:1]))
    if reverse:
        edges = [(b, a) for a, b in reversed(edges)]
    queries = [
        (32 * scale, -32 * scale),
        (36 * scale, -31 * scale),
        (30 * scale, -30 * scale),
        points[0],
    ]
    queries += [
        (np.nextafter(points[0][0], -np.inf), points[0][1]),
        (np.nextafter(points[0][0], np.inf), points[0][1]),
    ]
    expected = [min(exact_distance(a, b, p) for a, b in edges) for p in queries]
    x, y = np.array(queries * 6).T
    field = SignedDistanceField.__new__(SignedDistanceField)
    field._boundary_segments = lambda: edges
    np.testing.assert_allclose(
        field._compute_distance_to_boundary_vectorized(x, y),
        expected * 6,
        rtol=8e-15,
        atol=0.0,
    )


def test_box_pruning_never_silently_omits_invalid_or_extreme_queries():
    field = SignedDistanceField.__new__(SignedDistanceField)
    edges = [((float(i), 0.0), (float(i + 1), 1.0)) for i in range(12)]
    field._boundary_segments = lambda: edges
    x, y = np.array([0.0, 1e200, np.nan, np.inf] * 8), np.ones(32)
    expected = np.minimum.reduce([segment_distance(x, y, a, b) for a, b in edges])
    np.testing.assert_allclose(
        field._compute_distance_to_boundary_vectorized(x, y),
        expected,
        rtol=8e-15,
        atol=0.0,
    )
    edges.append(((1000.0, 1000.0), (np.nan, 2000.0)))
    with pytest.raises(ValueError, match="finite"):
        field._compute_distance_to_boundary_vectorized(np.zeros(32), np.zeros(32))


CASES = [
    ((0.0, 0.0), (4e-6, 0.0), (2e-6, 1e-6)),
    ((0.0, 0.0), (4 * SUB, 0.0), (4 * SUB, 2 * SUB)),
    ((0.0, 0.0), (4 * SUB, 3 * SUB), (2 * SUB, 3 * SUB)),
    ((-1e308, 0.0), (1e308, 0.0), (0.0, 1.0)),
    ((-1e308, 0.0), (1e308, 0.0), (0.0, SUB)),
    ((-1e308, -1e308), (1e308, 1e308), (0.0, 1.0)),
    ((-1e200, -1e200), (1e200, 1e200), (0.0, 1e-200)),
    ((1.0, 0.0), (1e308, 0.0), (2.0, 1.0)),
    ((-1e308, 0.0), (1e308, 0.0), (np.nextafter(1e308, np.inf), 0.0)),
    ((0.0, 0.0), (1.0, 1.0), (1e200, 2.0)),
    ((MAX, 0.0), (MAX, 0.0), (-MAX, 0.0)),
    ((1e200, 1e200), (1e200, 1e200), (1e200, 0.0)),
    ((0.0, 0.0), (0.0, 0.0), (SUB, SUB)),
    ((0.0, 0.0), (1e308, 1e-308), (1e-308, 1e-308)),
    ((1e200, -1e200), (-1e200, 1e200), (1.0, 1.0)),
    ((1.0, 2.0), (4.0, 6.0), (2.5, 4.0)),
    ((0.0, 0.0), (1e308, 1e-14), (5e307, 0.0)),
    ((0.0, 0.0), (1e308, 1e-10), (5e307, 0.0)),
    ((0.0, 0.0), (1.0, 1e-310), (0.5, 0.0)),
    ((0.0, 0.0), (1e308, 1e308), (1e-200, 2e-200)),
    ((0.0, 0.0), (1e308, 1e-310), (5e307, 0.0)),
]


@pytest.mark.parametrize("start,end,point", CASES)
@pytest.mark.parametrize("reverse", [False, True])
def test_exact_extreme_and_degenerate_oracles(start, end, point, reverse):
    if reverse:
        start, end = end, start
    expected = exact_distance(start, end, point)
    observed = float(segment_distance(*point, start, end))
    assert not np.isnan(observed)
    if np.isinf(expected):
        assert np.isposinf(observed)
    elif expected == 0 or expected < np.finfo(float).tiny:
        assert observed == expected
    else:
        assert observed == pytest.approx(expected, rel=4e-15, abs=0.0)


@pytest.mark.parametrize(
    "scale", [1e-310, 1e-200, 1e-20, 1e-6, 1.0, 1e20, 1e150, 1e200, 1e307]
)
@pytest.mark.parametrize("point", [(-1.0, 2.0), (1.0, 2.0), (4.0, 2.0), (6.0, 7.0)])
def test_short_oblique_and_huge_segments(scale, point):
    start, end = (0.0, 0.0), (3 * scale, 4 * scale)
    point = tuple(v * scale for v in point)
    observed = float(segment_distance(*point, start, end))
    expected = exact_distance(start, end, point)
    assert observed == pytest.approx(expected, rel=5e-15, abs=0.0)


@pytest.mark.parametrize(
    "offset,step", [(1e12, 1.0), (1e200, 1e185), (-1e200, 1e185), (1e-200, 1e-215)]
)
def test_translated_actual_float_geometry(offset, step):
    start = (offset, offset)
    end = (offset + 3 * step, offset + 4 * step)
    point = (offset + step, offset + 2 * step)
    expected = exact_distance(start, end, point)
    assert float(segment_distance(*point, start, end)) == pytest.approx(
        expected, rel=8e-15, abs=0.0
    )


def test_seeded_mixed_exponent_oracle_and_batch_parity():
    random = np.random.default_rng(1900)
    for _ in range(40):
        values = np.ldexp(random.uniform(-1.0, 1.0, 6), random.integers(-1070, 1024, 6))
        start, end, point = values.reshape((3, 2))
        expected = exact_distance(start, end, point)
        observed = float(segment_distance(*point, start, end))
        if expected == 0 or expected < np.finfo(float).tiny or np.isinf(expected):
            assert observed == expected
        else:
            assert observed == pytest.approx(expected, rel=8e-15, abs=0.0)
        batched = segment_distance(np.array([point[0], point[0]]), point[1], start, end)
        np.testing.assert_array_equal(batched, np.array([observed, observed]))


@pytest.mark.parametrize("end", [(3.0, 4.0), (7.0, 11.0)])
@pytest.mark.parametrize("delta", [1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-13])
def test_near_line_distance_retains_small_residual(end, delta):
    point = (end[0] / 2, end[1] / 2 + delta)
    expected = exact_distance((0.0, 0.0), end, point)
    assert float(segment_distance(*point, (0.0, 0.0), end)) == pytest.approx(
        expected, rel=4e-15, abs=0.0
    )


@pytest.mark.parametrize("exponent", [300, 340, 350, 358, 359])
@pytest.mark.parametrize("reverse", [False, True])
def test_large_and_mixed_products_cancel_to_tiny_determinant(exponent, reverse):
    huge, small = np.ldexp(1.0, exponent), np.ldexp(1.0, -exponent)
    start, end, point = (huge, huge), (small, 2 * small), (2 * small, 3 * small)
    if reverse:
        start, end = end, start
    expected = exact_distance(start, end, point)
    observed = float(segment_distance(*point, start, end))
    if expected < np.finfo(float).tiny:
        assert observed == expected
    else:
        assert observed == pytest.approx(expected, rel=4e-15, abs=0.0)


@pytest.mark.parametrize("axis", [0, 1])
@pytest.mark.parametrize("scale", [SUB, 1e-200, 1e-6, 1.0, 1e200])
def test_zero_length_and_short_nonzero_are_distinct(axis, scale):
    end = [0.0, 0.0]
    end[axis] = 4 * scale
    point = [0.0, 0.0]
    point[axis] = 2 * scale
    point[1 - axis] = scale
    assert float(segment_distance(*point, (0.0, 0.0), end)) == scale
    expected = exact_distance((0.0, 0.0), (0.0, 0.0), point)
    assert float(segment_distance(*point, (0.0, 0.0), (0.0, 0.0))) == expected


@pytest.mark.parametrize(
    "bounds",
    [
        (0.0, 0.0, 4e-6, 4e-6),
        (0.0, 0.0, 4.0, 4.0),
        (0.0, 0.0, 4e200, 4e200),
        (1e200, 1e200, 2e200, 2e200),
    ],
)
@pytest.mark.parametrize("kind", ["scalar", "array", "zero_dim"])
def test_signed_rectangle_with_exact_edge_oracle(bounds, kind):
    x0, y0, x1, y1 = bounds
    field = SignedDistanceField(
        AreaRegion(create_square_from_edges((x0, y0), (x1, y1)))
    )
    point = (x0 + (x1 - x0) * 0.5, y0 + (y1 - y0) * 0.25)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    expected = -min(
        exact_distance(corners[i], corners[(i + 1) % 4], point) for i in range(4)
    )
    x, y = point
    if kind == "array":
        x, y = np.array([x]), np.array([y])
    elif kind == "zero_dim":
        x, y = np.array(x), np.array(y)
    np.testing.assert_allclose(field.evaluate(x, y), expected, rtol=4e-15, atol=0.0)


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e200])
def test_hole_sign_and_nearest_distance_at_scale(scale):
    outer = create_square_from_edges((0.0, 0.0), (6 * scale, 6 * scale))
    hole = create_square_from_edges((2 * scale, 2 * scale), (4 * scale, 4 * scale))
    # Isolate distance arithmetic from the separate default 1e-4 containment band.
    policy = PrecisionPolicy(absolute=0.0, relative=0.0, distance_factor=0.0)
    field = SignedDistanceField(AreaRegion(outer, [hole], precision_policy=policy))
    for point, sign in [((3 * scale, 3 * scale), 1), ((1.5 * scale, 3 * scale), -1)]:
        endpoints = [
            ((0.0, 0.0), (6 * scale, 0.0)),
            ((6 * scale, 0.0), (6 * scale, 6 * scale)),
            ((6 * scale, 6 * scale), (0.0, 6 * scale)),
            ((0.0, 6 * scale), (0.0, 0.0)),
            ((2 * scale, 2 * scale), (4 * scale, 2 * scale)),
            ((4 * scale, 2 * scale), (4 * scale, 4 * scale)),
            ((4 * scale, 4 * scale), (2 * scale, 4 * scale)),
            ((2 * scale, 4 * scale), (2 * scale, 2 * scale)),
        ]
        expected = sign * min(exact_distance(a, b, point) for a, b in endpoints)
        assert field.evaluate(*point) == pytest.approx(expected, rel=4e-15, abs=0.0)
        np.testing.assert_allclose(
            field.evaluate(np.array([point[0]]), point[1]),
            expected,
            rtol=4e-15,
            atol=0.0,
        )


@pytest.mark.parametrize("end", [(np.inf, 0.0), (np.nan, 0.0), (1j, 0.0)])
def test_invalid_endpoint_geometry_is_explicit(end):
    with pytest.raises(ValueError):
        segment_distance(1.0, 2.0, (0.0, 0.0), end)


def test_empty_broadcast_and_nonfinite_queries():
    assert segment_distance(np.empty((0, 3)), 0.0, (0.0, 0.0), (1.0, 1.0)).shape == (
        0,
        3,
    )
    observed = segment_distance(
        np.array([[0.0], [1.0]]), np.array([0.0, np.inf]), (0.0, 0.0), (1.0, 1.0)
    )
    assert observed.shape == (2, 2)
    assert np.isnan(observed[:, 1]).all()
    assert observed[0, 0] == 0.0


def test_invalid_boundary_segment_is_not_hidden_by_valid_neighbors():
    field = SignedDistanceField(
        AreaRegion(create_square_from_edges((0.0, 0.0), (4.0, 4.0)))
    )
    field.region.outer_boundary.segments[0].endpoints[0] = (np.nan, 0.0)
    with pytest.raises(ValueError, match="finite coordinate pairs"):
        field.evaluate(np.array([1.0, 2.0]), np.array([2.0, 2.0]))
