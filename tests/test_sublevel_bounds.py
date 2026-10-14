"""Independent analytic envelopes and counterexamples to heuristic rejection."""

from dataclasses import FrozenInstanceError
import math

import numpy as np
import pytest
import sympy as sp

from geometry import (
    ImplicitCurve,
    ConicSection,
    ProceduralCurve,
    CurveField,
    BlendedField,
    LevelSetCurve,
    SublevelBounds,
    blend,
    union,
    intersect,
    difference,
)
from geometry.curve_intersections import find_curve_intersections

x, y = sp.symbols("x y")


def circle(cx=0, cy=0, radius=1):
    return ConicSection((x - cx) ** 2 + (y - cy) ** 2 - radius**2, (x, y))


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_nested_identical_blend_encloses_analytic_contour(depth):
    curve = circle()
    for _ in range(depth):
        curve = blend(curve, curve, 2)
    radius = math.sqrt(1 + depth)
    box = curve.sublevel_bounds().box
    assert box[0] <= -radius and box[1] >= radius
    angles = np.arange(1024) * 2 * np.pi / 1024
    px, py = radius * np.cos(angles), radius * np.sin(angles)
    assert np.all((px >= box[0]) & (px <= box[1]) & (py >= box[2]) & (py <= box[3]))
    assert np.max(np.abs(curve.evaluate(px, py))) < 4e-15


@pytest.mark.parametrize("scale", [1e-200, 1.0, 1e200])
def test_field_scale_changes_blend_growth_not_distance(scale):
    curve = ImplicitCurve(sp.Float(scale) * (x * x + y * y - 1))
    result = blend(curve, curve, scale * 2).sublevel_bounds()
    assert result.kind == "bounded"
    assert result.box[1] >= math.sqrt(2)
    assert result.box[1] <= math.nextafter(math.sqrt(2), math.inf)


@pytest.mark.parametrize("center", [0.0, 1e9, 1e16])
def test_factored_float_translation_preserves_small_radius(center):
    curve = ImplicitCurve((x - sp.Float(center)) ** 2 + y * y - 1)
    box = curve.sublevel_bounds().box
    exact_center = sp.Rational(center)
    assert sp.Rational(box[0]) <= exact_center - 1
    assert sp.Rational(box[1]) >= exact_center + 1
    assert box[2:] == (-1.0, 1.0)


def test_rotated_ellipse_extents_are_checked_against_exact_rationals():
    # Q=[[2,1],[1,3]], det=5; center=(7,-4), rho=5.
    u, v = x - 7, y + 4
    box = ImplicitCurve(2 * u * u + 2 * u * v + 3 * v * v - 5).sublevel_bounds().box
    for low, high, center, squared in [(box[0], box[1], 7, 3), (box[2], box[3], -4, 2)]:
        assert sp.Rational(low) - center <= 0 <= sp.Rational(high) - center
        assert (sp.Rational(low) - center) ** 2 >= squared
        assert (sp.Rational(high) - center) ** 2 >= squared


def test_near_singular_positive_definite_quad_has_finite_enclosure():
    tiny = sp.Rational(1, 10**100)
    result = ImplicitCurve((x + y) ** 2 + tiny * y * y - 1).sublevel_bounds()
    assert result.kind == "bounded"
    assert all(math.isfinite(v) for v in result.box)
    assert sp.Rational(result.box[3]) ** 2 >= 1 / tiny


@pytest.mark.parametrize(
    "expression",
    [
        -x * x - y * y + 1,
        x * x - y * y,
        x * x,
        x + y,
        x**4 + y**4 - 1,
        sp.sin(x) + y,
        sp.sqrt(2) * x * x + y * y - 1,
        sp.Symbol("a") * x * x + y * y - 1,
    ],
)
def test_unbounded_or_unsupported_sublevels_remain_unknown(expression):
    assert ImplicitCurve(expression).sublevel_bounds().kind == "unknown"


def test_empty_point_whole_plane_are_distinct():
    curve = circle()
    assert curve.sublevel_bounds(-2).kind == "empty"
    assert curve.sublevel_bounds(-1).box == (0.0, 0.0, 0.0, 0.0)
    assert ImplicitCurve(sp.Integer(2)).sublevel_bounds(1).kind == "empty"
    assert ImplicitCurve(sp.Integer(2)).sublevel_bounds(2).kind == "unknown"
    assert intersect(circle(), circle(5)).sublevel_bounds().kind == "empty"
    assert intersect(circle(), circle(2)).sublevel_bounds().box == (1.0, 1.0, -1.0, 1.0)


def test_envelope_cache_uses_current_expression_and_result_is_immutable():
    curve = circle()
    first = curve.sublevel_bounds()
    assert curve.evaluate(0, 0) == -1
    assert curve.gradient(0, 0) == (0.0, 0.0)
    curve.expression = (x - 10) ** 2 + y * y - 1
    assert curve.evaluate(0, 0) == 99
    assert curve.gradient(0, 0) == (-20.0, 0.0)
    assert curve.sublevel_bounds().box == (9.0, 11.0, -1.0, 1.0)
    assert first.box == (-1.0, 1.0, -1.0, 1.0)
    curve.variables = (y, x)
    assert curve.evaluate(0, 10) == -1
    assert curve.gradient(0, 0) == (0.0, -20.0)
    assert curve.sublevel_bounds().box == (-1.0, 1.0, 9.0, 11.0)
    with pytest.raises(FrozenInstanceError):
        first.box = (0.0, 1.0, 0.0, 1.0)


@pytest.mark.parametrize(
    "level", [True, np.bool_(True), float("nan"), float("inf"), 1j, "0"]
)
def test_invalid_levels_rejected(level):
    with pytest.raises(ValueError):
        circle().sublevel_bounds(level)
    with pytest.raises(ValueError):
        CurveField(circle()).level_set(level)


def test_unrepresentable_enclosure_returns_unknown():
    assert (
        ImplicitCurve(x * x + y * y - sp.Integer(10) ** 1000).sublevel_bounds().kind
        == "unknown"
    )


def test_nested_blend_level_sum_does_not_overflow_float():
    curve = circle()
    for _ in range(6):
        curve = blend(curve, curve, 1e308)
    result = curve.sublevel_bounds()
    assert result.kind == "bounded"
    assert result.box[1] >= math.sqrt(3) * 1e154


def test_unknown_operand_composition_rules():
    known = circle()
    unknown = ProceduralCurve(lambda x, y: (x - 30) ** 2 + y * y - 1)
    assert union(known, unknown).sublevel_bounds().kind == "unknown"
    assert blend(known, unknown, 1).bounding_box() is None
    assert (
        intersect(known, unknown).sublevel_bounds().box == known.sublevel_bounds().box
    )
    assert (
        difference(known, unknown).sublevel_bounds().box == known.sublevel_bounds().box
    )
    assert difference(unknown, known).bounding_box() is None
    assert (
        union(known, ImplicitCurve(sp.Integer(2))).sublevel_bounds().box
        == known.sublevel_bounds().box
    )
    assert (
        BlendedField([CurveField(known), CurveField(unknown)], "add")
        .sublevel_bounds()
        .kind
        == "unknown"
    )


def test_custom_evaluator_cannot_certify_its_display_expression():
    class DifferentField(ImplicitCurve):
        def evaluate(self, x, y):
            return (x - 30) ** 2 + y * y - 1

    assert DifferentField(x * x + y * y - 1).sublevel_bounds().kind == "unknown"


def test_wrapper_subclasses_and_instance_overrides_cannot_borrow_envelopes():
    class DifferentField(CurveField):
        def evaluate(self, x, y):
            return (x - 30) ** 2 + y * y - 1

    class DifferentLevel(LevelSetCurve):
        def evaluate(self, x, y):
            return (x - 30) ** 2 + y * y - 1

    for curve in (DifferentField(circle()), DifferentLevel(circle(), 0)):
        assert curve.sublevel_bounds().kind == "unknown"
    curve = circle()
    curve.evaluate = lambda x, y: (x - 30) ** 2 + y * y - 1
    assert curve.sublevel_bounds().kind == "unknown"


def test_unknown_union_no_longer_rejects_remote_intersections():
    remote = ProceduralCurve(lambda x, y: (x - 3) ** 2 + y * y - 1)
    result = find_curve_intersections(
        union(circle(), remote), circle(3.5), grid_resolution=160, tolerance=1e-7
    )
    assert len(result) == 2
    result = sorted(result, key=lambda p: p[1])
    np.testing.assert_allclose(
        result, [(3.25, -math.sqrt(15) / 4), (3.25, math.sqrt(15) / 4)], atol=1e-7
    )


def test_shifted_procedural_preserves_callback_shape_gradient_and_cusp_guard():
    calls = []

    def field(x, y):
        calls.append(1)
        return x * x + y * y

    curve = ProceduralCurve(field, gradient_function=lambda x, y: (2 * x, 2 * y))
    shifted = CurveField(curve).level_set(2)
    assert isinstance(shifted, LevelSetCurve)
    assert shifted.gradient(3, 4) == (6.0, 8.0)
    assert not calls
    assert shifted.evaluate(0, 0) == -2
    xx = np.array([[1.0], [2.0]])
    yy = np.array([0.0, 1.0, 2.0])
    np.testing.assert_array_equal(shifted.evaluate(xx, yy), xx * xx + yy * yy - 2)
    assert shifted.evaluate(np.empty((0, 2)), np.empty((0, 2))).shape == (0, 2)
    assert isinstance(shifted.evaluate(np.array(0.0), np.array(0.0)), np.ndarray)
    assert shifted.normal(3, 4) == pytest.approx((0.6, 0.8))
    cusp = CurveField(ProceduralCurve(lambda x, y: x**3 + y**3)).level_set(1)
    with pytest.raises(ValueError, match="Normal undefined"):
        cusp.normal(0, 0)
    assert shifted.sublevel_bounds().kind == "unknown"


def test_shifted_stable_blend_preserves_extreme_evaluation_and_serialization():
    curve = blend(ImplicitCurve(x), ImplicitCurve(y), 1e200)
    shifted = CurveField(curve).level_set(0)
    restored = ImplicitCurve.from_dict(shifted.to_dict())
    for target in (shifted, restored):
        assert target.evaluate(1e200, -1e200) == curve.evaluate(1e200, -1e200)
        assert math.isfinite(target.evaluate(1e200, -1e200))
        assert target.gradient(1e200, -1e200) == curve.gradient(1e200, -1e200)


def test_shifted_nested_levels_bounds_and_symbolic_round_trip():
    curve = CurveField(CurveField(circle()).level_set(1)).level_set(2)
    assert curve.evaluate(0, 0) == -4
    assert curve.sublevel_bounds().box == (-2.0, 2.0, -2.0, 2.0)
    restored = ImplicitCurve.from_dict(curve.to_dict())
    assert restored.evaluate(3, 4) == 21
    assert restored.sublevel_bounds().box == curve.sublevel_bounds().box
    with pytest.raises(ValueError):
        LevelSetCurve.from_dict(
            dict(type="LevelSetCurve", curve=circle().to_dict(), level=0, extra=1)
        )


@pytest.mark.parametrize(
    "box", [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, math.inf), (0.0, 1.0, 0.0)]
)
def test_invalid_public_envelopes_rejected(box):
    with pytest.raises(ValueError):
        SublevelBounds("bounded", box)
