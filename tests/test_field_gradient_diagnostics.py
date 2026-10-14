"""Analytic composition oracles, validity propagation and opt-in probe budgets."""

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
from geometry.base_field import BlendedField, CurveField
from geometry.field_strategy import SignedDistanceField
from geometry.implicit_curve import ImplicitCurve
from geometry.level_set_curve import LevelSetCurve
from geometry.procedural_curve import ProceduralCurve

x, y = sp.symbols("x y")


def symbolic(expression):
    return CurveField(ImplicitCurve(sp.sympify(expression), (x, y)))


def native(scale=1.0):
    return SignedDistanceField(
        AreaRegion(create_square_from_edges((0.0, 0.0), (4 * scale, 4 * scale)))
    )


def callback(function):
    field = native()
    field.evaluate = function
    return field


def assert_unavailable(result):
    assert not np.any(result["available"])
    assert np.isnan(result["gradient"]).all()
    assert not result["certified"]


@pytest.mark.parametrize("scale", [1e-6, 1.0, 1e6])
def test_native_contours_keep_unit_gradient_and_corner_medial_masks(scale):
    field = native(scale)
    contour = field.level_set(0.125 * scale)
    assert contour.evaluate(2 * scale, scale) == pytest.approx(
        field.evaluate(2 * scale, scale) - 0.125 * scale
    )
    assert contour.gradient(2 * scale, scale) == (0.0, -1.0)
    assert contour.normal(2 * scale, scale) == (0.0, -1.0)
    assert contour.gradient_diagnostics(2 * scale, scale)["gradient"] == (0.0, -1.0)
    for point in ((0.0, 0.0), (2 * scale, 2 * scale)):
        assert np.isnan(contour.gradient(*point)).all()
        assert_unavailable(contour.gradient_diagnostics(*point))
        with pytest.raises(ValueError):
            contour.normal(*point)
    assert contour.to_dict()["type"] == "ProceduralCurve"


def test_sampled_circle_composition_does_not_claim_analytic_or_trust_jump_normal():
    circle = SignedDistanceField(
        AreaRegion(
            CompositeCurve(
                [
                    TrimmedImplicitCurve(
                        ConicSection(x * x + y * y - 1, (x, y)), lambda x, y: True
                    )
                ]
            )
        ),
        1e-6,
    )
    a, b = np.array(circle._boundary_segments()[0])
    mid = (a + b) / 2
    point = mid / np.hypot(*mid)
    blend = BlendedField([circle, symbolic(0)], "add")
    contour = blend.level_set(0.0)
    # Cheap gradients preserve their legacy estimate and do not run opt-in probes.
    np.testing.assert_array_equal(contour.gradient(*point), circle.gradient(*point))
    with pytest.raises(ValueError, match="unresolved"):
        contour.normal(*point)
    result = contour.gradient_diagnostics(*point)
    assert_unavailable(result)
    assert result["method"] == "algebraic"
    assert np.isinf(result["error_estimate"]).all()
    assert result["sources"][0]["derivative_target"] == "evaluate"


@pytest.mark.parametrize(
    "operation", ["add", "subtract", "multiply", "divide", "average", "min", "max"]
)
def test_analytic_chain_rules_and_numeric_error_propagation(operation):
    a = callback(lambda x, y: 3 * x - 4 * y + 7)
    b = symbolic(x + 2 * y + 3)
    blend = BlendedField([a, b], operation)
    point = (0.3, 0.2)
    av, bv = 7.1, 3.7
    da, db = np.array([3.0, -4.0]), np.array([1.0, 2.0])
    expected = {
        "add": da + db,
        "subtract": da - db,
        "multiply": da * bv + av * db,
        "divide": da / bv - av * db / (bv * bv),
        "average": (da + db) / 2,
        "min": db,
        "max": da,
    }[operation]
    result = blend.gradient_diagnostics(*point)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], expected, rtol=3e-9, atol=1e-12)
    assert not result["certified"]
    if operation == "min":
        assert result["sources"] == [] and result["error_estimate"] is None
    else:
        source = a.gradient_diagnostics(*point)
        error = np.array(source["error_estimate"])
        factor = {
            "add": 1.0,
            "subtract": 1.0,
            "multiply": abs(bv),
            "divide": 1 / abs(bv),
            "average": 0.5,
            "max": 1.0,
        }[operation]
        np.testing.assert_allclose(result["error_estimate"], error * factor, rtol=2e-15)


def test_shared_callback_diagnosed_once_through_nested_contour_and_shifts():
    calls = []

    def function(a, b):
        calls.append((a, b))
        return 3 * a - 4 * b + 7

    field = callback(function)
    inner = BlendedField([field, symbolic(0)])
    alias = CurveField(LevelSetCurve(LevelSetCurve(inner.level_set(1.0), 2.0), -3.0))
    outer = BlendedField([alias, field], "add")
    result = outer.gradient_diagnostics(0.3, 0.2)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], (6.0, -8.0), rtol=1e-9)
    assert len(result["sources"]) == 1
    assert len(calls) == 1 + result["sources"][0]["field_evaluations"]


@pytest.mark.parametrize("operation", ["min", "max"])
def test_inactive_numerical_source_never_triggers_diagnostics(operation):
    field = callback(lambda x, y: 100.0 if operation == "min" else -100.0)

    def forbidden(*args):
        raise AssertionError("inactive diagnostics must not be called")

    field.gradient_diagnostics = forbidden
    blend = BlendedField([field, symbolic(y)], operation)
    assert blend.gradient_diagnostics(0.3, 0.2)["gradient"] == (0.0, 1.0)
    assert blend.level_set(0.0).normal(0.3, 0.2) == (0.0, 1.0)


def test_cheap_paths_add_no_adaptive_probes_and_opt_in_recovers_tiny_callback():
    calls = []
    field = callback(lambda a, b: calls.append((a, b)) or np.hypot(a, b) - 1e-6)
    blend = BlendedField([field, symbolic(0)])
    contour = blend.level_set(0.0)
    point = (1.6e-6, 1.2e-6)
    assert max(np.abs(contour.gradient(*point))) < 0.001
    assert len(calls) <= 6
    calls.clear()
    with pytest.raises(ValueError, match="unresolved"):
        contour.normal(*point)
    assert len(calls) <= 6
    calls.clear()
    result = contour.gradient_diagnostics(*point)
    assert result["available"]
    np.testing.assert_allclose(result["gradient"], (0.8, 0.6), rtol=3e-6)
    assert len(calls) <= 323


@pytest.mark.parametrize("wrapper", ["blend", "contour", "shift", "field"])
def test_exact_medial_cusp_uncertainty_survives_wrappers(wrapper):
    source = callback(lambda x, y: np.abs(np.hypot(x, y) - 0.75) - 0.25)
    blend = BlendedField([source, symbolic(0)])
    obj = {
        "blend": blend,
        "contour": blend.level_set(0.0),
        "shift": LevelSetCurve(blend.level_set(1.0), -1.0),
        "field": CurveField(LevelSetCurve(blend.level_set(1.0), -1.0)),
    }[wrapper]
    assert_unavailable(obj.gradient_diagnostics(0.75, 0.0))


@pytest.mark.parametrize("operation", ["min", "max"])
def test_distinct_active_tie_gradients_remain_unavailable(operation):
    blend = BlendedField([symbolic(x), symbolic(-x)], operation)
    assert_unavailable(blend.gradient_diagnostics(0.0, 0.2))
    with pytest.raises(ValueError):
        blend.level_set(0.0).normal(0.0, 0.2)
    assert blend.gradient_diagnostics(0.25, 0.2)["available"]


def test_identical_shared_tie_and_native_corner_remain_correct():
    field = native()
    blend = BlendedField([field, field], "min")
    assert blend.gradient_diagnostics(2.0, 1.0)["gradient"] == (0.0, -1.0)
    assert_unavailable(blend.gradient_diagnostics(0.0, 0.0))


@pytest.mark.parametrize("kind", ["scalar", "zero_dim", "broadcast", "empty"])
def test_shapes_and_scalar_arguments_through_composition_and_contour(kind):
    if kind == "scalar":
        a, b = 0.3, 0.2
    elif kind == "zero_dim":
        a, b = np.array(0.3), np.array(0.2)
    elif kind == "broadcast":
        a, b = np.array([[0.3], [0.4]]), np.array([0.1, 0.2, 0.3])
    else:
        a, b = np.empty((0, 1)), np.ones((1, 3))
    shape = np.broadcast_arrays(a, b)[0].shape

    def function(u, v):
        if kind == "scalar":
            assert type(u) is float and type(v) is float
        else:
            assert u.shape == v.shape == shape
        return 3 * u - 4 * v + 7

    blend = BlendedField([callback(function), symbolic(x)])
    result = blend.level_set(1.0).gradient_diagnostics(a, b)
    np.testing.assert_allclose(result["gradient"][0], np.full(shape, 4.0), rtol=1e-9)
    np.testing.assert_allclose(result["gradient"][1], np.full(shape, -4.0), rtol=1e-9)
    assert np.shape(result["available"]) == shape
    assert (
        isinstance(result["available"], bool)
        if kind == "scalar"
        else isinstance(result["available"], np.ndarray)
    )


@pytest.mark.parametrize(
    "kind",
    [
        "blend_gradient",
        "sdf_gradient",
        "contour_gradient",
        "contour_callback",
        "shift_gradient",
    ],
)
def test_provided_gradients_remain_authoritative_without_fabricated_error(kind):
    source = native()
    blend = BlendedField([source, symbolic(0)])
    contour = blend.level_set(0.0)
    shifted = LevelSetCurve(contour, 0.0)
    obj = {
        "blend_gradient": blend,
        "sdf_gradient": source,
        "contour_gradient": contour,
        "contour_callback": contour,
        "shift_gradient": shifted,
    }[kind]
    if kind == "contour_callback":
        obj._gradient_function = lambda x, y: (3.0, -4.0)
    else:
        obj.gradient = lambda x, y: (3.0, -4.0)
    result = obj.gradient_diagnostics(2.0, 1.0)
    assert result["gradient"] == (3.0, -4.0)
    assert result["error_estimate"] is None
    if hasattr(obj, "normal"):
        np.testing.assert_allclose(obj.normal(2.0, 1.0), (0.6, -0.8))


def test_root_gradient_override_and_super_delegation_do_not_recurse():
    class Override(BlendedField):
        def gradient(self, x, y):
            gx, gy = super().gradient(x, y)
            return gx + 1, gy - 1

    blend = Override([symbolic(x), symbolic(y)])
    assert blend.gradient_diagnostics(0.3, 0.2)["gradient"] == (2.0, 0.0)
    assert blend.level_set(0.0).normal(0.3, 0.2) == (1.0, 0.0)


@pytest.mark.parametrize("kind", ["blend", "curve_field", "contour", "shift"])
def test_value_only_override_is_diagnosed_without_trusting_stale_normal(kind):
    blend = BlendedField([symbolic(x), symbolic(y)])
    contour = blend.level_set(0.0)
    shifted = LevelSetCurve(contour, 0.0)
    field = CurveField(contour)
    obj = {"blend": blend, "curve_field": field, "contour": contour, "shift": shifted}[
        kind
    ]
    if kind == "contour":
        obj.function = lambda x, y: 2 * x - 3 * y
    else:
        obj.evaluate = lambda x, y: 2 * x - 3 * y
    # Binary-exact, non-cancelling value: estimator behavior at near-zero
    # callback values is a separate conservative budget limitation.
    result = obj.gradient_diagnostics(0.5, 0.25)
    np.testing.assert_allclose(result["gradient"], (2.0, -3.0), rtol=1e-8)
    if hasattr(obj, "normal"):
        with pytest.raises(ValueError, match="unresolved"):
            obj.normal(0.3, 0.2)


def test_near_zero_callback_value_keeps_estimator_uncertainty():
    blend = BlendedField([symbolic(x), symbolic(y)])
    blend.evaluate = lambda x, y: 2 * x - 3 * y
    result = blend.gradient_diagnostics(0.3, 0.2)
    assert_unavailable(result)
    np.testing.assert_allclose(result["raw_gradient"], (2.0, -3.0))
    assert "budget_exhausted" in result["status"]


@pytest.mark.parametrize("kind", ["shift", "curve_field"])
def test_procedural_unresolved_errors_are_not_lost_without_available_metadata(kind):
    curve = ProceduralCurve(lambda x, y: np.abs(x) + y, (x, y))
    result = curve.gradient_diagnostics(0.0, 0.25)
    assert not np.isfinite(result["error_estimate"][0])
    obj = LevelSetCurve(curve, 0.0) if kind == "shift" else CurveField(curve)
    assert_unavailable(obj.gradient_diagnostics(0.0, 0.25))


def test_custom_diagnostic_availability_is_authoritative_through_aliases():
    source = native()
    source.gradient_diagnostics = lambda x, y: dict(
        gradient=(1.0, 0.0),
        available=False,
        error_estimate=None,
        method="provided_unavailable",
    )
    obj = BlendedField(
        [CurveField(LevelSetCurve(source.level_set(0.0), 0.0)), symbolic(y)]
    )
    assert_unavailable(obj.gradient_diagnostics(2.0, 1.0))
    with pytest.raises(ValueError):
        obj.level_set(0.0).normal(2.0, 1.0)


@pytest.mark.parametrize("kind", ["symbolic", "generated", "shifted"])
def test_curve_field_custom_diagnostics_are_not_bypassed(kind):
    curve = ImplicitCurve(x, (x, y))
    if kind != "symbolic":
        curve = BlendedField([symbolic(x), symbolic(0)]).level_set(0.0)
    if kind == "shifted":
        curve = LevelSetCurve(curve, 0.0)
    field = CurveField(curve)
    field.gradient_diagnostics = lambda x, y: dict(
        gradient=(1.0, 0.0), available=False, error_estimate=None
    )
    blend = BlendedField([field, symbolic(y)])
    assert_unavailable(blend.gradient_diagnostics(0.5, 0.25))
    with pytest.raises(ValueError, match="unresolved"):
        blend.level_set(0.0).normal(0.5, 0.25)


def test_generated_contour_custom_diagnostics_do_not_authorize_cheap_normal():
    contour = native().level_set(0.0)
    contour.gradient_diagnostics = lambda x, y: dict(
        gradient=(0.0, -1.0), available=False, error_estimate=None
    )
    with pytest.raises(ValueError, match="unresolved"):
        contour.normal(2.0, 1.0)


@pytest.mark.parametrize("kind", ["symbolic", "generated"])
def test_root_curve_field_diagnostic_override_can_delegate_to_super(kind):
    class Override(CurveField):
        def gradient_diagnostics(self, x, y):
            return super().gradient_diagnostics(x, y)

    curve = (
        ImplicitCurve(x, (x, y))
        if kind == "symbolic"
        else BlendedField([symbolic(x), symbolic(0)]).level_set(0.0)
    )
    assert Override(curve).gradient_diagnostics(0.5, 0.25)["gradient"] == (1.0, 0.0)


@pytest.mark.parametrize("kind", ["direct", "contour", "nested"])
def test_cycle_guards_span_generated_field_contours(kind):
    blend = BlendedField([symbolic(x), symbolic(y)])
    blend.fields[0] = (
        blend
        if kind == "direct"
        else CurveField(
            blend.level_set(0.0)
            if kind == "contour"
            else LevelSetCurve(blend.level_set(0.0), 1.0)
        )
    )
    with pytest.raises(ValueError, match="Cyclic"):
        blend.gradient_diagnostics(0.3, 0.2)


def test_mutated_unary_wrapper_cycle_is_rejected_before_alias_unwrap():
    curve = LevelSetCurve(ImplicitCurve(x, (x, y)), 0.0)
    curve.curve = curve
    blend = BlendedField([CurveField(curve), symbolic(y)])
    with pytest.raises(ValueError, match="Cyclic"):
        blend.gradient_diagnostics(0.5, 0.25)


@pytest.mark.parametrize("exception", [TypeError, ValueError, RuntimeError])
def test_callback_failures_propagate_once_through_diagnostic_graph(exception):
    calls = []

    def function(x, y):
        calls.append((x, y))
        raise exception("graph callback error")

    contour = BlendedField([callback(function), symbolic(0)]).level_set(0.0)
    with pytest.raises(exception, match="graph callback error"):
        contour.gradient_diagnostics(0.3, 0.2)
    assert len(calls) == 1


def test_shifted_domain_overflow_does_not_expose_an_available_vector():
    curve = ProceduralCurve(
        lambda x, y: np.full(np.shape(x), -1e308),
        (x, y),
        gradient_function=lambda x, y: (1.0, 0.0),
    )
    shifted = LevelSetCurve(curve, 1e308)
    with np.errstate(over="ignore"):
        assert_unavailable(shifted.gradient_diagnostics(0.3, 0.2))
    with pytest.raises(ValueError):
        shifted.normal(0.3, 0.2)


def test_invalid_division_domain_is_not_available():
    blend = BlendedField([symbolic(x), symbolic(y)], "divide")
    assert_unavailable(blend.gradient_diagnostics(1.0, 0.0))
    assert blend.evaluate(1.0, 0.0) == 0.0


def test_nonfinite_inputs_and_live_mutations_have_fresh_results():
    source = native()
    blend = BlendedField([source, symbolic(0)])
    result = blend.gradient_diagnostics(np.array([2.0, np.nan, np.inf]), 1.0)
    np.testing.assert_array_equal(result["available"], [True, False, False])
    result["gradient"][0][0] = 99.0
    assert blend.gradient_diagnostics(2.0, 1.0)["gradient"] == (0.0, -1.0)
    blend.fields[1] = symbolic(y)
    assert blend.gradient_diagnostics(2.0, 1.0)["gradient"] == (0.0, 0.0)
    with pytest.raises(ValueError):
        blend.level_set(0.0).normal(2.0, 1.0)


@pytest.mark.parametrize("level", [np.nan, np.inf, sp.Integer(10) ** 400])
def test_sdf_contour_rejects_invalid_level(level):
    with pytest.raises(ValueError):
        native().level_set(level)
