"""Independent analytic/high-precision regressions for reusable field numerics."""

from decimal import Decimal, localcontext
import math

import numpy as np
import pytest
import sympy as sp

from geometry.implicit_curve import ImplicitCurve
from geometry.procedural_curve import ProceduralCurve
from geometry.rfunction_curve import RFunctionCurve
from geometry.static_blend import contours_from_grid, sample_field_contours


X, Y = sp.symbols("x y")


@pytest.mark.parametrize("expression", [sp.Integer(7), X, Y, X + Y])
def test_symbolic_evaluation_and_gradient_broadcast(expression):
    curve = ImplicitCurve(expression, (X, Y))
    x, y = np.arange(3.0)[:, None], np.arange(4.0)[None, :]
    expected = np.empty((3, 4))
    for i in range(3):
        for j in range(4):
            expected[i, j] = float(expression.subs({X: i, Y: j}))
    actual = curve.evaluate(x, y)
    assert actual.shape == expected.shape
    np.testing.assert_array_equal(actual, expected)
    gx, gy = curve.gradient(x, y)
    assert gx.shape == gy.shape == expected.shape
    np.testing.assert_array_equal(
        gx, np.full(expected.shape, float(sp.diff(expression, X)))
    )
    np.testing.assert_array_equal(
        gy, np.full(expected.shape, float(sp.diff(expression, Y)))
    )


@pytest.mark.parametrize(
    "function", [lambda x, y: 7, lambda x, y: x, lambda x, y: math.sin(x) + y]
)
def test_procedural_scalar_fallback_broadcast(function):
    curve = ProceduralCurve(function)
    x, y = np.arange(3.0)[:, None], np.arange(4.0)[None, :]
    expected = np.array(
        [[function(float(i), float(j)) for j in range(4)] for i in range(3)]
    )
    actual = curve.evaluate(x, y)
    assert actual.shape == expected.shape
    np.testing.assert_allclose(actual, expected)


@pytest.mark.parametrize("scale", [1e-300, 1e-20, 1, 1e200, 1e308])
def test_normal_direction_invariant_to_finite_field_scale(scale):
    normal = ImplicitCurve(sp.Float(scale) * (X + Y), (X, Y)).normal(0, 0)
    np.testing.assert_allclose(normal, [math.sqrt(0.5)] * 2, rtol=1e-14)


@pytest.mark.parametrize(
    "expression,point", [(X * X + Y * Y, (0, 0)), (sp.log(X), (-1, 0)), (1 / X, (0, 0))]
)
def test_normal_rejects_singular_or_nonfinite_gradient(expression, point):
    curve = ImplicitCurve(expression, (X, Y))
    with (
        np.errstate(all="ignore"),
        pytest.raises(ValueError, match="undefined|Undefined"),
    ):
        curve.normal(*point)


@pytest.mark.parametrize(
    "a,b,alpha",
    [
        (1e200, -1e200, 0.5),
        (1e308, 1e308, 1),
        (1e-200, 0, 1e-200),
        (1e308, -1e308, 1e308),
        (1, 1, 1e-200),
        (1e-200, 1e-200, 1e-200),
        (1, 0, 1e-8),
        (0, 1, 1e-8),
        (5e-324, 0, 5e-324),
    ],
)
def test_smooth_blend_against_decimal_oracle(a, b, alpha):
    curve = RFunctionCurve(
        ImplicitCurve(X, (X, Y)), ImplicitCurve(Y, (X, Y)), "blend", alpha
    )
    with localcontext() as context:
        context.prec = 650
        da, db, d_alpha = map(Decimal.from_float, [a, b, alpha])
        root = ((da - db) ** 2 + d_alpha**2).sqrt()
        expected = float((da + db - root) / 2)
        wx, wy = float((1 - (da - db) / root) / 2), float((1 + (da - db) / root) / 2)
    actual = curve.evaluate(a, b)
    assert actual == pytest.approx(expected, rel=2e-14, abs=0)
    np.testing.assert_allclose(curve.gradient(a, b), [wx, wy], rtol=2e-14, atol=0)


@pytest.mark.parametrize(
    "scale,center", [(1e-9, 0), (1e-6, 0), (1, 0), (1e9, 0), (1, 1e9)]
)
def test_grid_circle_scale_and_translation(scale, center):
    axis = np.linspace(-1, 1, 49)
    x, y = np.meshgrid(axis, axis)
    values = (x * x + y * y - 0.55**2).ravel().tolist()
    result = contours_from_grid(
        values,
        [center - scale, center + scale, center - scale, center + scale],
        [0],
        48,
    )[0]
    assert len(result["paths"]) == 1 and result["omitted"] == 0
    points = np.asarray(result["paths"][0])
    assert np.array_equal(points[0], points[-1])
    local = (points - center) / scale
    np.testing.assert_allclose(np.linalg.norm(local, axis=1), 0.55, atol=0.0015)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_direct_grid_rejects_nonfinite_values(bad):
    values = np.ones(625)
    values[300] = bad
    with pytest.raises(ValueError, match="finite"):
        contours_from_grid(values, [-1, 1, -1, 1], [0], 24)


def test_constant_field_sampling_accepts_broadcast_result():
    result = sample_field_contours(
        ImplicitCurve(sp.Integer(1), (X, Y)), [-1, 1, -1, 1], [0], 24
    )
    assert result == [dict(level=0, paths=[], omitted=0)]


@pytest.mark.parametrize(
    "curve", [ImplicitCurve(X + Y, (X, Y)), ProceduralCurve(lambda x, y: x + y)]
)
def test_real_coordinates_shape_empty_and_immutable(curve):
    assert isinstance(curve.evaluate(1, 2), float)
    zero_dimensional = curve.evaluate(np.array(1.0), np.array(2.0))
    assert isinstance(zero_dimensional, np.ndarray) and zero_dimensional.shape == ()
    assert curve.evaluate(np.empty((0, 1)), np.ones((1, 3))).shape == (0, 3)
    x, y = np.arange(3.0)[:, None], np.arange(4.0)[None, :]
    before_x, before_y = x.copy(), y.copy()
    gx, gy = curve.gradient(x, y)
    assert gx.shape == gy.shape == (3, 4)
    np.testing.assert_allclose(gx, 1, atol=1e-7)
    np.testing.assert_allclose(gy, 1, atol=1e-7)
    np.testing.assert_array_equal(x, before_x)
    np.testing.assert_array_equal(y, before_y)
    for bad in [1j, "2", [None]]:
        with pytest.raises(ValueError, match="real numeric"):
            curve.evaluate(bad, 0)
    with pytest.raises(ValueError):
        curve.evaluate(np.ones(2), np.ones(3))


@pytest.mark.parametrize("operation", ["union", "intersection", "difference", "blend"])
def test_constant_operand_composition_broadcasts_and_roundtrips(operation):
    curve = RFunctionCurve(
        ImplicitCurve(sp.Integer(1), (X, Y)),
        ImplicitCurve(Y, (X, Y)),
        operation,
        0.5 if operation == "blend" else 0,
    )
    y = np.array([-2.0, 0.0, 2.0])
    actual = curve.evaluate(0, y)
    np.testing.assert_allclose(actual, [curve.evaluate(0, float(v)) for v in y])
    gx, gy = curve.gradient(0, y)
    assert gx.shape == gy.shape == y.shape
    rebuilt = ImplicitCurve.from_dict(curve.to_dict())
    np.testing.assert_allclose(rebuilt.evaluate(0, y), actual)


@pytest.mark.parametrize(
    "alpha", [float("nan"), float("inf"), float("-inf"), True, 1j, "1"]
)
def test_blend_rejects_undefined_alpha(alpha):
    with pytest.raises(ValueError, match="positive.*finite"):
        RFunctionCurve(
            ImplicitCurve(X, (X, Y)), ImplicitCurve(Y, (X, Y)), "blend", alpha
        )


@pytest.mark.parametrize(
    "bounds,levels,resolution",
    [
        ([-1, 1, -1, 1], [], 24),
        ([-1, 1, -1, 1], [0] * 17, 24),
        ([-1, 1, -1, 1], [float("nan")], 24),
        ([0, 0, -1, 1], [0], 24),
        ([-1e308, 1e308, -1, 1], [0], 24),
        ([-1, 1, -1, 1], [0], True),
        ([-1, 1, -1, 1], [0], 193),
    ],
)
def test_direct_and_sampled_grid_validation_agree(bounds, levels, resolution):
    for call in [
        lambda: contours_from_grid(np.ones(625), bounds, levels, resolution),
        lambda: sample_field_contours(
            ImplicitCurve(X, (X, Y)), bounds, levels, resolution
        ),
    ]:
        with pytest.raises(ValueError):
            call()


def test_grid_shape_and_sampled_domain_failures_are_explicit():
    for values in [np.ones(624), np.ones((1, 625)), np.ones(625, dtype=complex)]:
        with pytest.raises(ValueError):
            contours_from_grid(values, [-1, 1, -1, 1], [0], 24)
    with np.errstate(all="ignore"), pytest.raises(ValueError, match="finite"):
        sample_field_contours(ImplicitCurve(1 / X, (X, Y)), [-1, 1, -1, 1], [0], 24)


@pytest.mark.parametrize("scale", [1e-9, 1, 1e9])
def test_annulus_retains_hole_and_deterministic_loops(scale):
    x, y = np.meshgrid(np.linspace(-1, 1, 49), np.linspace(-1, 1, 49))
    values = (x * x + y * y - 0.25**2) * (x * x + y * y - 0.7**2)
    before = values.copy()
    result = contours_from_grid(values, [-scale, scale, -scale, scale], [0], 48)
    assert len(result[0]["paths"]) == 2 and result[0]["omitted"] == 0
    radii = sorted(
        float(np.mean(np.linalg.norm(np.asarray(path) / scale, axis=1)))
        for path in result[0]["paths"]
    )
    np.testing.assert_allclose(radii, [0.25, 0.7], atol=0.004)
    assert result == contours_from_grid(values, [-scale, scale, -scale, scale], [0], 48)
    np.testing.assert_array_equal(values, before)


def test_exact_zero_vertices_and_shared_edges_are_not_guessed():
    # Two negative pockets touch at a single exact-level vertex (degree four).
    values = np.ones((5, 5))
    values[2, 2] = 0
    values[1, 1] = -1
    values[3, 3] = -1
    layer = contours_from_grid(values, [0, 4, 0, 4], [0], 4)[0]
    assert layer["paths"] == [] and layer["omitted"] == 1
    # A shared zero edge has one segment, not a false two-edge closed path.
    layer = contours_from_grid([0, -1, -1, 0], [0, 1, 0, 1], [0], 1)[0]
    assert layer["paths"] == [] and layer["omitted"] == 1
    assert contours_from_grid(np.zeros(9), [0, 1, 0, 1], [0], 2) == [
        dict(level=0, paths=[], omitted=0)
    ]


def test_extreme_finite_grid_edges_interpolate_without_overflow():
    values = np.full((5, 5), 1e308)
    values[2, 2] = -1e308
    layer = contours_from_grid(values, [-1, 1, -1, 1], [0], 4)[0]
    assert len(layer["paths"]) == 1 and layer["omitted"] == 0
    assert np.isfinite(layer["paths"]).all()


@pytest.mark.parametrize("alpha", [5e-324, 1.5e-323])
def test_subnormal_blend_value_rounds_after_subtraction(alpha):
    curve = RFunctionCurve(
        ImplicitCurve(X, (X, Y)), ImplicitCurve(Y, (X, Y)), "blend", alpha
    )
    with localcontext() as context:
        context.prec = 800
        expected = float(Decimal.from_float(5e-324) - Decimal.from_float(alpha) / 2)
    assert curve.evaluate(5e-324, 5e-324) == expected
    np.testing.assert_array_equal(
        curve.evaluate(np.array([5e-324]), np.array([5e-324])), [expected]
    )


def test_world_mapping_collapse_is_omitted():
    x, y = np.meshgrid(np.linspace(-1, 1, 25), np.linspace(-1, 1, 25))
    values = (x + 0.5) ** 2 + (y + 0.5) ** 2 - 0.2**2
    layer = contours_from_grid(values, [1e16, 1e16 + 2, 1e16, 1e16 + 2], [0], 24)[0]
    assert layer["paths"] == [] and layer["omitted"] == 1


@pytest.mark.parametrize("scale", [1e-200, 1, 1e200])
def test_procedural_normal_rejects_truncation_cusp_but_accepts_linear_scale(scale):
    cusp = ProceduralCurve(lambda x, y: scale * (y * y - x**3))
    with pytest.raises(ValueError, match="Normal undefined"):
        cusp.normal(0, 0)
    line = ProceduralCurve(lambda x, y: scale * (x + y))
    np.testing.assert_allclose(line.normal(0, 0), [math.sqrt(0.5)] * 2, rtol=1e-14)
