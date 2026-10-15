"""Analytic trim intersections, candidate halos and final domain authority."""

import numpy as np
import pytest
import sympy as sp

from geometry import ImplicitCurve, TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections, _trim_endpoint_seeds

x, y = sp.symbols("x y")


def implicit(expression):
    return ImplicitCurve(expression, (x, y))


def horizontal(*, endpoints=True, low=0.0, high=1.0, height=0.25, mask=None):
    return TrimmedImplicitCurve(
        implicit(y - sp.Rational(height)),
        mask if mask is not None else lambda a, b: low <= a <= high,
        xmin=low,
        xmax=high,
        ymin=height,
        ymax=height,
        endpoints=[(low, height), (high, height)] if endpoints else [],
    )


def intersections(a, b, **kwargs):
    return find_curve_intersections(
        a, b, search_range=2.0, grid_resolution=100, tolerance=1e-8, **kwargs
    )


def assert_points(actual, expected, atol=1e-7):
    assert len(actual) == len(expected)
    np.testing.assert_allclose(sorted(actual), sorted(expected), atol=atol, rtol=0)


@pytest.mark.parametrize("resolution", [32, 100, 101])
@pytest.mark.parametrize("position", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("reverse", [False, True])
def test_zero_height_trim_finds_interior_and_endpoints_without_endpoint_seeds(
    resolution, position, reverse
):
    a, b = horizontal(endpoints=False), implicit(x - sp.Rational(position))
    if reverse:
        a, b = b, a
    result = find_curve_intersections(
        a, b, search_range=2.0, grid_resolution=resolution, tolerance=1e-8
    )
    assert_points(result, [(position, 0.25)])


def test_two_zero_width_rectangles_cross_off_grid():
    a = horizontal(endpoints=False)
    b = TrimmedImplicitCurve(
        implicit(x - sp.Rational(1, 2)),
        lambda a, b: 0 <= b <= 1,
        xmin=0.5,
        xmax=0.5,
        ymin=0.0,
        ymax=1.0,
    )
    assert_points(intersections(a, b), [(0.5, 0.25)])


def test_short_diagonal_trim_smaller_than_a_grid_cell():
    a = TrimmedImplicitCurve(
        implicit(y - x + sp.Rational(1, 4)),
        lambda a, b: 0.4999 <= a <= 0.5001,
        xmin=0.4999,
        xmax=0.5001,
        ymin=0.2499,
        ymax=0.2501,
    )
    assert_points(intersections(a, implicit(x - sp.Rational(1, 2))), [(0.5, 0.25)])


@pytest.mark.parametrize("detect_overlap", [False, True])
def test_circle_crossings_with_thin_rectangle_are_refined_not_coarse_overlap(
    detect_overlap,
):
    a = horizontal(low=-1.5, high=1.5, height=0.75)
    b = implicit(x * x + y * y - sp.Rational(25, 16))
    result = intersections(a, b, detect_overlap=detect_overlap)
    assert_points(result, [(-1.0, 0.75), (1.0, 0.75)])
    for px, py in result:
        assert a.contains(px, py, 1e-7)
        assert abs(b.evaluate(px, py)) < 1e-8


@pytest.mark.parametrize("detect_overlap", [False, True])
def test_aligned_trim_preserves_unpadded_overlap_trigger(detect_overlap):
    height = float(np.linspace(-2.0, 2.0, 100)[56])
    a = horizontal(height=height)
    b = implicit(
        (x - sp.Rational(1, 2)) ** 2
        + (y - sp.Rational(height)) ** 2
        - sp.Rational(4, 25)
    )
    # The original exact trim has only13 coarse points: it never triggered the
    # >20 legacy overlap heuristic. The halo must not change that decision.
    assert_points(
        intersections(a, b, detect_overlap=detect_overlap),
        [(0.1, height), (0.9, height)],
    )


def test_parabola_crossings_are_distinct_and_trimmed():
    a = horizontal(low=-0.75, high=0.75)
    assert_points(intersections(a, implicit(y - x * x)), [(-0.5, 0.25), (0.5, 0.25)])


def test_shared_circle_endpoint_is_returned_once():
    a = horizontal(low=0.0, high=1.0, height=0.75)
    assert_points(
        intersections(a, implicit(x * x + y * y - sp.Rational(25, 16))), [(1.0, 0.75)]
    )


def test_narrow_circle_arc_keeps_only_allowed_branch():
    a = TrimmedImplicitCurve(
        implicit(x * x + y * y - 1),
        lambda a, b: 0.1 <= a <= 0.11 and b >= 0.0,
        xmin=0.1,
        xmax=0.11,
        ymin=0.99,
        ymax=1.0,
    )
    assert_points(
        intersections(a, implicit(x - sp.Rational(21, 200))),
        [(0.105, np.sqrt(1 - 0.105**2))],
    )


@pytest.mark.parametrize("position", [-0.01, 1.01])
def test_expanded_grid_candidates_cannot_expand_final_rectangle(position):
    assert (
        intersections(
            horizontal(mask=lambda a, b: True), implicit(x - sp.Rational(position))
        )
        == []
    )


@pytest.mark.parametrize("mask", [lambda a, b: False, lambda a, b: a < 0.5])
def test_final_callable_mask_remains_authoritative(mask):
    assert intersections(horizontal(mask=mask), implicit(x - sp.Rational(1, 2))) == []


def test_final_contains_override_remains_authoritative():
    segment = horizontal()
    segment.contains = lambda a, b, tolerance: False
    assert intersections(segment, implicit(x - sp.Rational(1, 2))) == []


def test_partial_rectangle_does_not_crash_or_invent_constraints():
    segment = TrimmedImplicitCurve(
        implicit(y - sp.Rational(1, 4)), lambda a, b: 0 <= a <= 1, xmin=0.0, xmax=1.0
    )
    assert_points(
        intersections(segment, implicit(x - sp.Rational(1, 2))), [(0.5, 0.25)]
    )
    assert intersections(segment, implicit(x - sp.Rational(3, 2))) == []


def test_explicit_endpoint_survives_an_empty_grid_candidate_set(monkeypatch):
    import geometry.curve_intersections as module

    radius = sp.Rational(1, 1024)
    endpoint = (float(sp.Rational(1, 2) + radius), 0.25)
    arc = TrimmedImplicitCurve(
        implicit(
            2**40
            * ((x - sp.Rational(1, 2)) ** 2 + (y - sp.Rational(1, 4)) ** 2 - radius**2)
        ),
        lambda a, b: a >= 0.5,
        xmin=0.5,
        xmax=endpoint[0],
        ymin=0.25,
        ymax=0.25,
        endpoints=[endpoint],
    )
    counts = []
    cluster = module._cluster_candidates_fast

    def count(points, **kwargs):
        counts.append(len(points))
        return cluster(points, **kwargs)

    monkeypatch.setattr(module, "_cluster_candidates_fast", count)
    result = intersections(arc, implicit(y - sp.Rational(1, 4)))
    assert counts == [0]
    assert_points(result, [endpoint], atol=1e-10)
    # No general tiny-feature completeness claim when explicit seeds are absent.
    arc.endpoints = []
    assert intersections(arc, implicit(y - sp.Rational(1, 4))) == []


def test_explicit_seed_does_not_bypass_final_validation_when_grid_is_empty(monkeypatch):
    import geometry.curve_intersections as module

    monkeypatch.setattr(
        module,
        "_apply_trimming_masks_fast",
        lambda mask, *args, **kwargs: np.zeros_like(mask),
    )
    a = horizontal(mask=lambda a, b: False)
    assert intersections(a, implicit(x - sp.Rational(1, 2))) == []


def test_endpoint_seeds_are_finite_in_range_unique_copies():
    a = horizontal()
    point = np.array([0.5, 0.25])
    a.endpoints = [
        point,
        point,
        [np.nan, 0.25],
        [np.inf, 0.25],
        [3.0, 0.25],
        [1.0],
        ["bad", 0.25],
        None,
    ]
    seeds = _trim_endpoint_seeds(a, implicit(x), 2.0)
    assert len(seeds) == 1
    np.testing.assert_array_equal(seeds[0], point)
    seeds[0][0] = 99.0
    assert point[0] == 0.5


def test_endpoint_candidates_do_not_escape_the_requested_search():
    a = horizontal(low=3.0, high=4.0)
    assert intersections(a, implicit(x - sp.Rational(7, 2))) == []


def test_registry_receives_one_accepted_original_pair():
    a, b = horizontal(), implicit(x - sp.Rational(1, 2))
    records = []
    result = intersections(a, b, registry_callback=lambda *args: records.append(args))
    assert_points(result, [(0.5, 0.25)])
    assert records == [(0.5, 0.25, a, b)]


def test_max_points_and_live_mask_changes_keep_existing_behavior():
    a = horizontal(low=-1.5, high=1.5, height=0.75)
    circle = implicit(x * x + y * y - sp.Rational(25, 16))
    assert len(intersections(a, circle, max_points=1)) == 1
    assert intersections(a, circle, max_points=0) == []
    a.mask = lambda a, b: False
    assert intersections(a, circle) == []


@pytest.mark.parametrize(
    "expression,other,expected",
    [
        (y - x * x, y - sp.Rational(1, 4), [(-0.5, 0.25), (0.5, 0.25)]),
        (x * x + y * y - 1, y - 1, [(0.0, 1.0)]),
        (y - x * x, y, [(0.0, 0.0)]),
    ],
)
def test_existing_untrimmed_crossings_and_tangencies_remain_numerical(
    expression, other, expected
):
    assert_points(intersections(implicit(expression), implicit(other)), expected)


def test_coincident_curve_return_contract_is_unchanged():
    assert intersections(horizontal(), horizontal()) == []
