"""Independent analytic and high precision oracles for exact-model isolation."""

from decimal import Decimal, localcontext
import math

import numpy as np
import pytest
import sympy as sp

from geometry import (
    ImplicitCurve,
    TrimmedImplicitCurve,
    find_polynomial_line_intersections as find,
)

x, y = sp.symbols("x y")


def curve(expression, variables=(x, y)):
    return ImplicitCurve(sp.sympify(expression), variables)


def rational(value):
    value = sp.Rational(value)
    return Decimal(int(value.p)) / Decimal(int(value.q))


def assert_encloses(record, expected):
    # Oracle values are analytic Decimal calculations, not SymPy roots/intervals.
    with localcontext() as context:
        context.prec = 160
        for interval, coordinate, actual in zip(
            record["coordinate_intervals"], expected, record["point"]
        ):
            lo, hi = map(rational, interval)
            assert lo <= coordinate <= hi
            assert abs(Decimal.from_float(actual) - coordinate) <= rational(
                record["position_bound_exact"]
            )


@pytest.mark.parametrize("degree", range(2, 9))
@pytest.mark.parametrize("scale", [sp.Rational(1, 10**100), -1, 10**100])
def test_flat_contact_exact_and_scaled(degree, scale):
    # Setting y=0 gives x**degree=0, exactly one root of stated multiplicity.
    report = find(curve(scale * (y - x**degree)), curve(-7 * y))
    assert report["status"] == "isolated_model"
    assert report["model_root_completeness"]
    assert report["points"] == [(0.0, 0.0)]
    assert len(report["roots"]) == 1
    root = report["roots"][0]
    assert root["multiplicity"] == degree
    assert root["position_bound_exact"] == "0"


@pytest.mark.parametrize("delta", [sp.Rational(1, 2**64), sp.Rational(1, 10**8)])
def test_near_miss_and_two_real_crossings(delta):
    assert find(curve(x**8 + delta), curve(y))["roots"] == []
    report = find(curve(x**8 - delta), curve(y))
    assert len(report["points"]) == 2
    with localcontext() as context:
        context.prec = 160
        root = rational(delta).sqrt().sqrt().sqrt()
        for record, expected in zip(report["roots"], [-root, root]):
            assert record["multiplicity"] == 1
            assert_encloses(record, (expected, Decimal(0)))


def test_irrational_roots_high_precision_oracle():
    report = find(curve(x**2 - 2), curve(y), position_tolerance=1e-14)
    assert len(report["points"]) == 2
    with localcontext() as context:
        context.prec = 160
        root = Decimal(2).sqrt()
        for record, expected in zip(report["roots"], [-root, root]):
            assert record["accepted"]
            assert_encloses(record, (expected, Decimal(0)))


@pytest.mark.parametrize("swap", [False, True])
@pytest.mark.parametrize(
    "polynomial,line,expected,multiplicity",
    [
        ((y - 3) - (x - 2) ** 8, y - 3, (2, 3), 8),
        ((x - 3) - (y - 2) ** 8, x - 3, (3, 2), 8),
        ((x - 1) ** 2 + (y - 2) ** 2 - 1, y - x, (1, 1), 1),
        (y - x**2, y - 2 * x + 1, (1, 1), 2),
        (2 * x + y - 4, x - y + 1, (1, 2), 1),
    ],
)
def test_affine_oracles_and_input_order(swap, polynomial, line, expected, multiplicity):
    inputs = [curve(polynomial), curve(line)]
    report = find(*reversed(inputs)) if swap else find(*inputs)
    root = next(r for r in report["roots"] if r["point"] == expected)
    assert root["accepted"]
    assert root["multiplicity"] == multiplicity


def test_variable_order_is_coordinate_order_not_symbol_name():
    u, v = sp.symbols("u v")
    report = find(curve(v - u**8, (u, v)), curve(x, (y, x)))
    assert report["points"] == [(0, 0)]
    assert report["roots"][0]["multiplicity"] == 8


def test_float_coefficients_mean_exact_binary_values():
    value = 0.1
    report = find(curve(x - sp.Float(value)), curve(y))
    assert report["points"] == [(value, 0)]
    assert report["roots"][0]["coordinate_intervals"][0] == [
        str(sp.Rational(value)),
        str(sp.Rational(value)),
    ]


@pytest.mark.parametrize("include", [False, True])
def test_exact_flat_root_trim_membership(include):
    trimmed = TrimmedImplicitCurve(curve(y - x**8), lambda a, b: include)
    report = find(trimmed, curve(y))
    assert report["points"] == ([(0, 0)] if include else [])
    assert report["roots"][0]["root_trim_membership"] == (
        "exact_point_accepted" if include else "exact_point_excluded"
    )
    assert report["model_root_completeness"]
    assert not report["trimmed_root_completeness"]


def test_nested_masks_are_all_honored():
    inner = TrimmedImplicitCurve(curve(y - x**8), lambda a, b: False)
    outer = TrimmedImplicitCurve(inner, lambda a, b: True)
    root = find(outer, curve(y))["roots"][0]
    assert not root["accepted"]
    assert root["representative_contains"] == [True, False]


def test_sqrt_two_threshold_does_not_certify_root_trim():
    # This float lies ABOVE the exact positive sqrt(2). The mask excludes the
    # true root even if it includes the representative. Never certify from it.
    threshold = math.sqrt(2)
    with localcontext() as context:
        context.prec = 160
        assert Decimal.from_float(threshold) > Decimal(2).sqrt()
    trimmed = TrimmedImplicitCurve(curve(x**2 - 2), lambda a, b: a >= threshold)
    report = find(trimmed, curve(y), position_tolerance=1e-14)
    assert report["points"] == []
    for root in report["roots"]:
        assert root["root_trim_membership"] == "unverified"
        assert "root_trim_membership_unverified" in root["reasons"]
    assert report["roots"][1]["representative_contains"] == [True]


def test_nonbinary_rational_trim_remains_unverified():
    trimmed = TrimmedImplicitCurve(curve(3 * x - 1), lambda a, b: True)
    report = find(trimmed, curve(y))
    assert report["points"] == []
    assert report["roots"][0]["root_trim_membership"] == "unverified"


@pytest.mark.parametrize("value", [None, 1, "yes", np.nan, np.array([True])])
def test_invalid_contains_is_not_truthy_acceptance(value):
    trimmed = TrimmedImplicitCurve(curve(x**8), lambda a, b: True)
    trimmed.contains = lambda *args: value
    root = find(trimmed, curve(y))["roots"][0]
    assert root["representative_contains"] == [None]
    assert not root["accepted"]


def test_contains_defaults_and_explicit_tolerance():
    trimmed = TrimmedImplicitCurve(curve(x**8), lambda a, b: True)
    calls = []

    def contains(a, b, tolerance="default"):
        calls.append(tolerance)
        return True

    trimmed.contains = contains
    assert find(trimmed, curve(y))["points"] == [(0, 0)]
    assert calls == ["default"]
    assert find(trimmed, curve(y), trim_tolerance=1e-5)["points"] == [(0, 0)]
    assert calls == ["default", 1e-5]


def test_mask_mutating_native_field_invalidates_all_points():
    base = curve(x**2 - 1)

    def mutate(a, b):
        base.expression = x**2 + 1
        return True

    report = find(TrimmedImplicitCurve(base, mutate), curve(y))
    assert report["status"] == "model_changed"
    assert report["points"] == []
    assert not report["model_root_completeness"]
    assert all(not root["accepted"] for root in report["roots"])


def test_float_collision_preserves_two_distinct_roots():
    report = find(curve((x - 1) ** 2 - sp.Rational(1, 2**120)), curve(y))
    assert report["model_root_completeness"]
    assert len(report["roots"]) == 2
    assert report["points"] == []
    assert report["roots"][0]["point"] == report["roots"][1]["point"] == (1, 0)
    assert all(
        "float_representative_collision" in root["reasons"] for root in report["roots"]
    )
    assert sp.Rational(report["roots"][0]["coordinate_intervals"][0][1]) < sp.Rational(
        report["roots"][1]["coordinate_intervals"][0][0]
    )


def test_tighter_than_float_accuracy_keeps_model_root():
    report = find(curve(3 * x - 1), curve(y), position_tolerance=1e-30)
    assert report["points"] == []
    assert len(report["roots"]) == 1
    assert report["model_root_completeness"]
    assert "requested_position_bound_not_met" in report["roots"][0]["reasons"]


def test_numeric_bound_rounds_outward_including_underflow():
    report = find(curve(x - sp.Rational(1, 2**1100)), curve(y))
    root = report["roots"][0]
    exact = sp.Rational(root["position_bound_exact"])
    assert exact > 0
    assert root["point"] == (0, 0)
    assert sp.Rational(root["position_bound"]) >= exact
    assert root["position_bound"] == math.nextafter(0, math.inf)
    root = find(curve(3 * x - 1), curve(y))["roots"][0]
    assert sp.Rational(root["position_bound"]) >= sp.Rational(
        root["position_bound_exact"]
    )


def test_close_roots_strictly_separated_from_exact_origin():
    report = find(curve(x * (x**2 - sp.Rational(1, 2**120))), curve(y))
    assert len(report["roots"]) == len(report["points"]) == 3
    for first, second in zip(report["roots"], report["roots"][1:]):
        assert sp.Rational(first["coordinate_intervals"][0][1]) < sp.Rational(
            second["coordinate_intervals"][0][0]
        )


def test_elimination_coefficient_growth_is_capped():
    report = find(curve(x**8 - 1), curve(x + sp.Rational(1, 2**1000) * y))
    assert report["status"] == "unsupported"
    assert report["reason"] == "elimination_coefficient_limit"


def test_finite_residual_acceptance_is_separate_from_position():
    report = find(curve(10**100 * (x**2 - 2)), curve(y))
    assert len(report["roots"]) == 2
    assert report["points"] == []
    assert all(
        "representative_residual_not_accepted" in root["reasons"]
        for root in report["roots"]
    )


@pytest.mark.parametrize("expression", [0, y, y * (x**2 + 1)])
def test_line_component_is_nonisolated_not_empty(expression):
    report = find(curve(expression), curve(y))
    assert report["status"] == "non_isolated_model"
    assert not report["model_root_completeness"]
    assert report["points"] == report["roots"] == []


@pytest.mark.parametrize("expression", [1, y - 1, x**2 + 1])
def test_no_real_roots_can_be_complete(expression):
    report = find(curve(expression), curve(y))
    assert report["status"] == "isolated_model"
    assert report["model_root_completeness"]
    assert report["roots"] == []


@pytest.mark.parametrize(
    "expression",
    [sp.sin(x), x**9, 1 / x, sp.sqrt(x), sp.pi * x],
)
def test_unsupported_structure_before_expansion_or_conversion(expression):
    report = find(curve(expression), curve(y))
    assert report["status"] == "unsupported"
    assert not report["model_root_completeness"]


def test_large_unevaluated_power_rejected_before_expansion():
    expression = sp.Pow(x + y + 1, 1000000, evaluate=False)
    assert find(curve(expression), curve(y))["status"] == "unsupported"


def test_huge_float_exponent_rejected_before_rational_conversion():
    # Construct the compact binary float directly; parsing a huge decimal string
    # would itself allocate an enormous integer before our API is called.
    huge = sp.Float._new((0, 1, 100000000, 1), 53)
    expression = sp.Mul(huge, x, evaluate=False)
    assert find(curve(expression), curve(y))["status"] == "unsupported"


def test_no_line_is_explicitly_unsupported():
    assert find(curve(x**2 + y**2 - 1), curve(x**2 - y))["status"] == "unsupported"


def test_active_replacement_kernel_is_not_bypassed():
    field = curve(x**8)
    field._eval_func = lambda a, b: a**8 + 1
    assert find(field, curve(y))["reason"] == "native_model_unavailable"


def test_replaced_public_evaluator_is_not_bypassed():
    field = curve(x**8)
    field.evaluate = lambda a, b: 0
    assert find(field, curve(y))["reason"] == "native_model_unavailable"


def test_native_lazy_and_compiled_kernels_supported():
    field = curve(x**8)
    assert find(field, curve(y))["points"] == [(0, 0)]
    assert field._eval_func is not None
    assert find(field, curve(y))["points"] == [(0, 0)]


@pytest.mark.parametrize(
    "name", ["position_tolerance", "residual_tolerance", "trim_tolerance"]
)
@pytest.mark.parametrize("value", [0, -1, np.inf, np.nan, True, "bad"])
def test_tolerances(name, value):
    with pytest.raises(ValueError):
        find(curve(x**8), curve(y), **{name: value})
