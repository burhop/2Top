"""Independent algebraic derivative/domain/shape and query-reuse contracts."""

import numpy as np
import pytest
import sympy as sp

from geometry.base_field import BlendedField, CurveField
from geometry.implicit_curve import ImplicitCurve
from geometry.procedural_curve import ProceduralCurve

x, y = sp.symbols("x y")


def field(expression):
    return CurveField(ImplicitCurve(sp.sympify(expression), (x, y)))


@pytest.mark.parametrize(
    "operation", ["add", "subtract", "multiply", "divide", "average"]
)
@pytest.mark.parametrize(
    "coordinates", [(1.2, 2.3), (np.array([[1.2], [2.0]]), np.array([2.0, 3.0, 4.0]))]
)
def test_symbolic_nary_oracle(operation, coordinates):
    expressions = [x + 2, y + 3, x + y + 5]
    expression = expressions[0]
    for other in expressions[1:]:
        expression = {
            "add": lambda: expression + other,
            "average": lambda: expression + other,
            "subtract": lambda: expression - other,
            "multiply": lambda: expression * other,
            "divide": lambda: expression / other,
        }[operation]()
    if operation == "average":
        expression /= 3
    blend = BlendedField([field(e) for e in expressions], operation)
    expected = [
        sp.lambdify((x, y), sp.diff(expression, v), "numpy")(*coordinates)
        for v in (x, y)
    ]
    np.testing.assert_allclose(
        blend.gradient(*coordinates),
        [
            np.broadcast_to(
                v,
                np.broadcast_shapes(np.shape(coordinates[0]), np.shape(coordinates[1])),
            )
            for v in expected
        ],
        rtol=2e-14,
        atol=1e-14,
    )


@pytest.mark.parametrize("scale", [1e-300, 1e-200, 1.0, 1e200, 1e300])
def test_quotient_rescaling(scale):
    blend = BlendedField(
        [field(sp.Float(scale) * x), field(sp.Float(scale) * y)], "divide"
    )
    np.testing.assert_allclose(blend.gradient(1.0, 2.0), (0.5, -0.25), rtol=2e-15)


@pytest.mark.parametrize(
    "a,b,db,expected",
    [
        (1e300, 1e200, 1e250, -1e150),
        (1e-300, 1e-200, 1e-250, -1e-150),
        (1e-300, 1e100, 1e300, -1e-200),
    ],
)
def test_quotient_extreme_intermediates(a, b, db, expected):
    numerator = field(sp.Float(a))
    denominator = field(sp.Float(b) + sp.Float(db) * y)
    np.testing.assert_allclose(
        BlendedField([numerator, denominator], "divide").gradient(0.0, 0.0),
        (0.0, expected),
        rtol=2e-15,
        atol=0,
    )


def test_translated_quotient_without_stencil():
    blend = BlendedField([field(x - sp.Integer(10) ** 12 + 2), field(y + 3)], "divide")
    assert blend.gradient(1e12, 1.0) == (0.25, -0.125)


@pytest.mark.parametrize("operation", ["min", "max"])
def test_winners_ties_and_shared_derivatives(operation):
    blend = BlendedField([field(x), field(-x)], operation)
    assert np.isnan(blend.gradient(0.0, 0.0)).all()
    expected = (-1.0, 0.0) if operation == "min" else (1.0, 0.0)
    assert blend.gradient(1.0, 0.0) == expected
    assert BlendedField([field(x * x), field(x * x + x**4)], operation).gradient(
        0.0, 0.0
    ) == (0.0, 0.0)
    assert np.isnan(
        BlendedField([field(x), field(y), field(-x)], operation).gradient(0.0, 0.0)
    ).all()


def test_inactive_undefined_gradient_and_mixed_winners():
    inner = BlendedField([field(x), field(-x)], "min")
    blend = BlendedField([inner, field(-1)], "min")
    assert blend.gradient(0.0, 0.0) == (0.0, 0.0)
    np.testing.assert_allclose(
        blend.gradient(np.array([-2.0, 0.0, 2.0]), 0.0),
        ([1.0, 0.0, -1.0], [0.0, 0.0, 0.0]),
    )
    invalid = field(x)
    invalid.gradient = lambda *_: (_ for _ in ()).throw(ValueError("inactive"))
    assert BlendedField([invalid, field(-1)], "min").gradient(0.0, 0.0) == (0.0, 0.0)


@pytest.mark.parametrize(
    "coordinates,shape,scalar",
    [
        ((1.0, 2.0), (), True),
        ((np.array(1.0), np.array(2.0)), (), False),
        (([[1.0], [2.0]], [1.0, 2.0, 3.0]), (2, 3), False),
        ((np.empty((0, 1)), np.empty((1, 3))), (0, 3), False),
    ],
)
@pytest.mark.parametrize(
    "operation", ["add", "subtract", "multiply", "divide", "min", "max", "average"]
)
def test_constant_shapes(operation, coordinates, shape, scalar):
    blend = BlendedField([field(2), field(3)], operation)
    for value in (blend.evaluate(*coordinates), *blend.gradient(*coordinates)):
        assert isinstance(value, float) if scalar else isinstance(value, np.ndarray)
        assert np.shape(value) == shape


def test_zero_division_domain_and_legacy_scalar_value():
    blend = BlendedField([field(1), field(x)], "divide")
    np.testing.assert_equal(blend.evaluate([0.0, 1.0], 0.0), [0.0, 1.0])
    gx, gy = blend.gradient([0.0, 1.0], 0.0)
    assert np.isnan([gx[0], gy[0]]).all()
    np.testing.assert_equal([gx[1], gy[1]], [-1.0, 0.0])
    multi = BlendedField([field(1), field(0), field(sp.nan)], "divide")
    assert multi.evaluate(0.0, 0.0) == 0.0
    assert np.isnan(multi.evaluate(np.array(0.0), np.array(0.0)))
    assert np.isnan(multi.gradient(0.0, 0.0)).all()
    with pytest.raises(ValueError):
        blend.level_set(0.0).normal(0.0, 0.0)


@pytest.mark.parametrize("expression", [sp.log(x), 1 / x, sp.sqrt(x)])
def test_invalid_child_domains(expression):
    blend = BlendedField([field(expression), field(y)], "add")
    assert np.isnan(blend.gradient(-1.0 if expression != 1 / x else 0.0, 1.0)).all()


def test_mutable_dag_reuse_and_no_output_aliasing():
    a, b = field(x + 1), field(y + 2)
    counts = {"value": 0, "gradient": 0}
    evaluate, gradient = a.evaluate, a.gradient

    def counted_value(*coords):
        counts["value"] += 1
        return evaluate(*coords)

    def counted_gradient(*coords):
        counts["gradient"] += 1
        return gradient(*coords)

    a.evaluate, a.gradient = counted_value, counted_gradient
    product = BlendedField([a, b], "multiply")
    root = BlendedField([product, product, a], "add")
    assert root.gradient(2.0, 3.0) == (11.0, 6.0)
    assert counts == {"value": 1, "gradient": 1}
    a.curve.expression = 2 * x
    assert root.gradient(2.0, 3.0) == (22.0, 8.0)
    root.operation = "subtract"
    assert root.gradient(2.0, 3.0) == (-2.0, 0.0)
    root.fields = [a, b]
    assert root.gradient(2.0, 3.0) == (2.0, -1.0)


@pytest.mark.parametrize("gradient", [False, True])
def test_cycle_guard(gradient):
    blend = BlendedField([field(x), field(y)])
    blend.fields[0] = blend
    with pytest.raises(ValueError, match="Cyclic"):
        (blend.gradient if gradient else blend.evaluate)(1.0, 2.0)


def test_contour_callback_override_normal_agrees():
    contour = BlendedField([field(x), field(y)]).level_set(0.0)
    contour._gradient_function = lambda x, y: (1.0, -1.0)
    np.testing.assert_allclose(contour.normal(0.0, 0.0), (2**-0.5, -(2**-0.5)))
    contour.gradient = lambda x, y: (-1.0, 1.0)
    np.testing.assert_allclose(contour.normal(0.0, 0.0), (-(2**-0.5), 2**-0.5))


def test_override_and_super_respected():
    class Shifted(BlendedField):
        def evaluate(self, x, y):
            return super().evaluate(x, y) + x

        def gradient(self, x, y):
            return (2.0, 1.0)

    child = Shifted([field(x), field(y)])
    parent = BlendedField([child, field(x)], "multiply")
    assert parent.evaluate(2.0, 3.0) == 14.0
    assert parent.gradient(2.0, 3.0) == (11.0, 2.0)


def test_shifted_level_reuses_live_analytic_gradient():
    a = field(x)
    blend = BlendedField([a, field(y)], "add")
    level = blend.level_set(4.0)
    assert level.evaluate(2.0, 3.0) == 1.0
    assert level.gradient(2.0, 3.0) == (1.0, 1.0)
    a.curve.expression = 2 * x
    assert level.gradient(2.0, 3.0) == (2.0, 1.0)
    assert level.to_dict()["type"] == "ProceduralCurve"
    blend.gradient = lambda x, y: (5.0, 1.0)
    assert level.gradient(2.0, 3.0) == (5.0, 1.0)
    assert BlendedField([CurveField(level), field(0)]).gradient(2.0, 3.0) == (5.0, 1.0)


def test_procedural_uncertainty_not_upgraded_to_analytic_normal():
    uncertain = CurveField(ProceduralCurve(lambda x, y: np.abs(x) + y, (x, y)))
    for blend in [
        BlendedField([uncertain, field(0)], "add"),
        BlendedField([uncertain, field(1)], "min"),
    ]:
        assert np.isnan(blend.gradient(0.0, 0.0)).all()
        with pytest.raises(ValueError):
            blend.level_set(0.0).normal(0.0, 0.0)
    inactive = BlendedField([uncertain, field(y - 1)], "min")
    assert inactive.level_set(0.0).normal(0.0, 0.0) == (0.0, 1.0)


def test_inputs_not_modified():
    xx, yy = np.array([1.0, 2.0]), np.array([3.0, 4.0])
    original = xx.copy(), yy.copy()
    blend = BlendedField([field(x), field(y)], "divide")
    result = blend.evaluate(xx, yy)
    result[:] = 99
    blend.gradient(xx, yy)
    np.testing.assert_equal((xx, yy), original)


@pytest.mark.parametrize("operation", ["add", "multiply"])
def test_valid_stationary_procedural_leaf(operation):
    stationary = CurveField(ProceduralCurve(lambda x, y: x * x + y * y, (x, y)))
    other = field(y) if operation == "add" else field(1)
    blend = BlendedField([stationary, other], operation)
    expected = (0.0, 1.0) if operation == "add" else (0.0, 0.0)
    np.testing.assert_allclose(blend.gradient(0.0, 0.0), expected, atol=1e-16)
    if operation == "add":
        assert blend.level_set(0.0).normal(0.0, 0.0) == (0.0, 1.0)


def test_shifted_and_nested_procedural_uncertainty():
    from geometry.level_set_curve import LevelSetCurve

    source = ProceduralCurve(lambda x, y: np.abs(x) + y, (x, y))
    shifted = CurveField(LevelSetCurve(LevelSetCurve(source, 1.0), -1.0))
    blend = BlendedField([shifted, field(0)])
    for contour in [
        blend.level_set(0.0),
        BlendedField([CurveField(blend.level_set(1.0)), field(1)]).level_set(0.0),
    ]:
        with pytest.raises(ValueError):
            contour.normal(0.0, 0.0)


@pytest.mark.parametrize(
    "coordinates,scalar", [((1.0, 2.0), True), ((np.array(1.0), np.array(2.0)), False)]
)
def test_value_only_override_fallback_shape(coordinates, scalar):
    class Shifted(BlendedField):
        def evaluate(self, x, y):
            return super().evaluate(x, y) + x

    blend = Shifted([field(x), field(y)])
    actual = blend.gradient(*coordinates)
    np.testing.assert_allclose(actual, (2.0, 1.0), rtol=1e-9)
    assert all(
        isinstance(v, float) if scalar else isinstance(v, np.ndarray) for v in actual
    )


def test_procedural_quantization_error_cannot_cancel_into_trusted_normal():
    quantized = CurveField(ProceduralCurve(lambda x, y: 1e16 + x, (x, y)))
    blend = BlendedField([quantized, field(sp.Rational(1, 100) * y)], "add")
    with pytest.raises(ValueError):
        blend.level_set(1e16).normal(0.0, 0.0)


@pytest.mark.parametrize("level", [float("nan"), float("inf"), sp.Integer(10) ** 400])
def test_invalid_level(level):
    with pytest.raises(ValueError):
        BlendedField([field(x), field(y)]).level_set(level)


@pytest.mark.parametrize("gradient", [False, True])
def test_generated_levelset_cycle(gradient):
    from geometry.level_set_curve import LevelSetCurve

    blend = BlendedField([field(x), field(y)])
    blend.fields[0] = CurveField(LevelSetCurve(blend.level_set(0.0), 1.0))
    with pytest.raises(ValueError, match="Cyclic"):
        (blend.gradient if gradient else blend.evaluate)(1.0, 2.0)
