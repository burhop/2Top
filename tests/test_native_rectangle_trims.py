"""Independent rational/Decimal oracles for native rectangle root membership."""

from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import math

import numpy as np
import pytest
import sympy as sp

from geometry import ImplicitCurve, RectangleMask, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections as find
from geometry.polynomial_line_intersections import _compare_root

x, y = sp.symbols("x y")


def curve(expression):
    return ImplicitCurve(sp.sympify(expression), (x, y))


def trim(expression, bounds):
    return TrimmedImplicitCurve(curve(expression), RectangleMask(*bounds))


@pytest.mark.parametrize(
    "bound", [sp.Rational(1, 3), sp.Rational(1, 10), 0.1, 0, sp.Rational(1, 2**1100)]
)
def test_directed_scalar_and_array_masks_match_independent_fractions(bound):
    exact = Fraction(sp.Rational(bound))
    middle = float(bound)
    values = np.array(
        [math.nextafter(middle, -math.inf), middle, math.nextafter(middle, math.inf)]
    )
    lower = RectangleMask(bound, 1, -1, 1)
    upper = RectangleMask(-1, bound, -1, 1)
    expected_lower = [Fraction.from_float(float(value)) >= exact for value in values]
    expected_upper = [Fraction.from_float(float(value)) <= exact for value in values]
    np.testing.assert_array_equal(lower(values, 0), expected_lower)
    np.testing.assert_array_equal(upper(values, 0), expected_upper)
    assert [lower(float(value), 0) for value in values] == expected_lower
    assert [upper(float(value), 0) for value in values] == expected_upper


def test_rectangle_frozen_and_broadcast_finite_contract():
    mask = RectangleMask(-1, 1, -2, 2)
    with pytest.raises(FrozenInstanceError):
        mask.xmin = -2
    np.testing.assert_array_equal(
        mask(np.array([[0], [2]]), np.array([0, 3])), [[True, False], [False, False]]
    )
    assert not mask(np.inf, 0)
    assert not mask(0, np.nan)
    assert mask(1, 2)
    assert mask(-1, -2)


@pytest.mark.parametrize(
    "value",
    [True, np.inf, np.nan, 1j, "1/3", sp.sqrt(2), 2**5000, sp.Rational(1, 2**5000)],
)
def test_invalid_bound_rejected(value):
    with pytest.raises(ValueError):
        RectangleMask(value, 1, 0, 1)


def test_huge_float_exponent_rejected_before_conversion():
    huge = sp.Float._new((0, 1, 100000000, 1), 53)
    with pytest.raises(ValueError):
        RectangleMask(huge, huge, 0, 1)


@pytest.mark.parametrize("bounds", [(1, -1, 0, 1), (0, 1, 2, 1)])
def test_inverted_bounds_rejected(bounds):
    with pytest.raises(ValueError):
        RectangleMask(*bounds)


def test_irrational_flat_contact_and_excluded_partner():
    report = find(trim((x * x - 2) ** 4, (0, 2, -1, 1)), curve(y))
    assert len(report["points"]) == 1
    negative, positive = report["roots"]
    assert [root["multiplicity"] for root in report["roots"]] == [4, 4]
    assert negative["root_trim_membership"] == "model_root_excluded"
    assert positive["root_trim_membership"] == "model_root_included"
    assert positive["accepted"] and not negative["accepted"]
    with localcontext() as context:
        context.prec = 160
        exact = Decimal(2).sqrt()
        assert abs(Decimal.from_float(positive["point"][0]) - exact) <= Decimal(
            1
        ) / Decimal(10**8)
    assert positive["root_trim_checks"] == [
        {"kind": "native_rectangle", "status": "included"}
    ]
    assert report["model_root_completeness"]
    assert not report["trimmed_root_completeness"]


@pytest.mark.parametrize("direction", [-1, 0, 1])
@pytest.mark.parametrize("side", ["lower", "upper"])
def test_sqrt_two_rational_threshold_uses_root_side_not_float_membership(
    direction, side
):
    boundary = math.sqrt(2)
    if direction:
        boundary = math.nextafter(boundary, math.inf if direction > 0 else -math.inf)
    with localcontext() as context:
        context.prec = 160
        exact = Decimal(2).sqrt()
        rational_boundary = Decimal.from_float(boundary)
        included = (
            exact >= rational_boundary
            if side == "lower"
            else exact <= rational_boundary
        )
    bounds = (boundary, 2, -1, 1) if side == "lower" else (0, boundary, -1, 1)
    report = find(trim(x * x - 2, bounds), curve(y), position_tolerance=1e-14)
    positive = report["roots"][1]
    assert positive["root_trim_membership"] == (
        "model_root_included" if included else "model_root_excluded"
    )
    assert positive["accepted"] == (
        included and all(positive["representative_contains"])
    )


@pytest.mark.parametrize("slope", [sp.Rational(-3, 2), 0, sp.Rational(2, 3)])
@pytest.mark.parametrize("swap", [False, True])
def test_oblique_constant_coordinates_and_input_order(slope, swap):
    a = trim(x * x - 2, (0, 2, -3, 2))
    b = curve(y - slope * x)
    report = find(b, a) if swap else find(a, b)
    assert len(report["points"]) == 1
    assert (
        next(root for root in report["roots"] if root["point"][0] > 0)[
            "root_trim_membership"
        ]
        == "model_root_included"
    )


def test_constant_coordinate_outside_box_and_vertical_line():
    assert find(trim(x * x - 2, (0, 2, 1, 2)), curve(y))["points"] == []
    report = find(trim(y * y - 2, (-1, 1, 0, 2)), curve(x))
    assert len(report["points"]) == 1
    assert report["parameter_axis"] == "y"


def test_nonbinary_rational_root_in_box_is_useful():
    report = find(trim(3 * x - 1, (0, 1, -1, 1)), curve(y))
    assert report["points"] == [(1 / 3, 0)]
    assert report["roots"][0]["root_trim_membership"] == "model_root_included"


def test_zero_width_nonbinary_box_keeps_root_but_no_float_representative():
    report = find(
        trim(3 * x - 1, (sp.Rational(1, 3), sp.Rational(1, 3), 0, 0)), curve(y)
    )
    root = report["roots"][0]
    assert root["root_trim_membership"] == "model_root_included"
    assert root["representative_contains"] == [False]
    assert report["points"] == []
    assert "representative_trim_not_accepted" in root["reasons"]


@pytest.mark.parametrize("include", [False, True])
def test_exact_closed_endpoint_flat_contact(include):
    bounds = (0, 1, 0, 0) if include else (sp.Rational(1, 10), 1, 0, 0)
    report = find(trim(x**8, bounds), curve(y))
    assert report["points"] == ([(0, 0)] if include else [])
    assert report["roots"][0]["root_trim_membership"] == (
        "exact_point_accepted" if include else "exact_point_excluded"
    )


def test_narrow_rectangle_root_side_proof_does_not_need_float_separation():
    lo = sp.Rational(math.sqrt(2)) - sp.Rational(1, 10**100)
    report = find(trim(x * x - 2, (lo, 2, -1, 1)), curve(y))
    assert report["roots"][1]["root_trim_membership"] == "model_root_excluded"


def test_nested_rectangles_and_opaque_callback_uncertainty():
    inner = trim(x * x - 2, (0, 2, -1, 1))
    outer = TrimmedImplicitCurve(inner, lambda a, b: True)
    report = find(outer, curve(y))
    negative, positive = report["roots"]
    assert negative["root_trim_membership"] == "model_root_excluded"
    assert positive["root_trim_membership"] == "unverified"
    assert report["points"] == []
    outer = TrimmedImplicitCurve(inner, RectangleMask(1, 2, -1, 1))
    assert len(find(outer, curve(y))["points"]) == 1


def test_overridden_contains_or_mask_subclass_is_opaque():
    field = trim(x * x - 2, (0, 2, -1, 1))
    field.contains = lambda *args: True
    assert find(field, curve(y))["roots"][1]["root_trim_membership"] == "unverified"

    class CustomRectangle(RectangleMask):
        def __call__(self, a, b):
            return True

    field = TrimmedImplicitCurve(curve(x * x - 2), CustomRectangle(0, 2, -1, 1))
    assert find(field, curve(y))["points"] == []


def test_additional_bbox_constraint_is_conservatively_opaque():
    field = trim(x * x - 2, (0, 2, -1, 1))
    field._xmin = 0
    assert find(field, curve(y))["points"] == []


@pytest.mark.parametrize("change", ["mask", "contains", "bbox", "mutable_bbox"])
def test_observed_trim_mutation_invalidates_all_trim_proofs(change):
    inner = trim(x * x - 1, (-2, 2, -1, 1))
    if change == "mutable_bbox":
        inner._xmin = np.array(-2.0)

    def mutate(a, b):
        if change == "mask":
            inner.mask = RectangleMask(2, 3, -1, 1)
        elif change == "contains":
            inner.contains = lambda *args: False
        elif change == "bbox":
            inner._xmin = 2
        else:
            inner._xmin[()] = 2
        return True

    outer = TrimmedImplicitCurve(inner, mutate)
    report = find(outer, curve(y))
    assert report["status"] == "trim_changed"
    assert report["model_root_completeness"]
    assert report["points"] == []
    assert all(root["root_trim_membership"] == "unverified" for root in report["roots"])


@pytest.mark.parametrize("threshold", [sp.Rational(-3, 2), -1, 0, 1, sp.Rational(3, 2)])
def test_exact_root_compare_endpoint_and_neighboring_root_cases(threshold):
    threshold = sp.Rational(threshold)
    t = sp.Symbol("t")
    polynomial = sp.Poly((t - 1) * (t + 1), t)
    assert _compare_root(
        polynomial, (sp.Rational(1, 2), sp.Rational(3, 2)), threshold
    ) == (int(bool(1 > threshold)) - int(bool(1 < threshold)))


def test_serialization_exact_native_and_nested_roundtrip():
    field = trim((x * x - 2) ** 4, (sp.Rational(1, 3), 2, -1, 1))
    field = TrimmedImplicitCurve(field, RectangleMask(0, 2, -1, 1))
    data = json.loads(json.dumps(field.to_dict(), allow_nan=False))
    restored = ImplicitCurve.from_dict(data)
    assert isinstance(restored.mask, RectangleMask)
    assert isinstance(restored.base_curve.mask, RectangleMask)
    assert restored.base_curve.mask.bounds[0] == sp.Rational(1, 3)
    assert not hasattr(restored, "_deserialization_warning")
    before, after = find(field, curve(y)), find(restored, curve(y))
    assert before == after


@pytest.mark.parametrize(
    "text", ["1/0", "sqrt(2)", "__import__('os')", "1+2", "1e10000", "9" * 2500, "0/00"]
)
def test_invalid_serialized_native_bounds_never_fall_back(text):
    data = trim(x * x - 2, (0, 2, -1, 1)).to_dict()
    data["native_mask"]["bounds"][0] = text
    with pytest.raises(ValueError):
        TrimmedImplicitCurve.from_dict(data)


@pytest.mark.parametrize("method", ["contains", "evaluate"])
def test_native_serialization_rejects_overridden_trim_methods(method):
    field = trim(x * x - 2, (0, 2, -1, 1))
    setattr(field, method, lambda *args: False)
    with pytest.raises(ValueError, match="default trim methods"):
        field.to_dict()


@pytest.mark.parametrize("attribute", ["mask", "_xmin", "base_curve"])
def test_deleted_trim_attribute_reports_invalidation(attribute):
    inner = trim(x * x - 1, (-2, 2, -1, 1))

    def mutate(a, b):
        if hasattr(inner, attribute):
            delattr(inner, attribute)
        return True

    report = find(TrimmedImplicitCurve(inner, mutate), curve(y))
    assert report["status"] == (
        "model_changed" if attribute == "base_curve" else "trim_changed"
    )
    assert report["model_root_completeness"] == (attribute != "base_curve")
    assert report["points"] == []
    assert all(root["root_trim_membership"] == "unverified" for root in report["roots"])


@pytest.mark.parametrize("kind", ["public", "kernel"])
def test_native_curve_codec_rejects_opaque_base_evaluator(kind):
    field = trim(x * x - 2, (0, 2, -1, 1))
    if kind == "public":
        field.base_curve.evaluate = lambda *args: False
    else:
        field.base_curve._eval_func = lambda *args: False
    with pytest.raises(ValueError, match="native evaluators"):
        field.to_dict()


def test_singleton_array_bbox_mutation_cannot_keep_stale_point():
    inner = TrimmedImplicitCurve(
        curve(x * x - 1),
        RectangleMask(-2, 2, -1, 1),
        xmin=np.array([-2.0]),
        xmax=2.0,
        ymin=-1.0,
        ymax=1.0,
    )
    calls = 0

    def mutate(a, b):
        nonlocal calls
        calls += 1
        if calls == 2:
            inner._xmin[0] = 2.0
        return True

    report = find(TrimmedImplicitCurve(inner, mutate), curve(y))
    assert report["status"] == "trim_changed"
    assert report["points"] == []
    assert all(root["root_trim_membership"] == "unverified" for root in report["roots"])


def test_changed_native_float_cache_is_opaque_not_a_model_proof():
    mask = RectangleMask(0, 2, -1, 1)
    object.__setattr__(mask, "_float_bounds", (-2.0, 2.0, -1.0, 1.0))
    report = find(TrimmedImplicitCurve(curve(x * x - 2), mask), curve(y))
    assert report["points"] == []
    assert all(
        root["root_trim_checks"][0]["kind"] == "callback" for root in report["roots"]
    )
    with pytest.raises(ValueError):
        mask.to_dict()


@pytest.mark.parametrize(
    "change", ["missing_payload", "missing_marker", "mismatched_marker"]
)
def test_native_codec_marker_and_payload_must_agree(change):
    data = trim(x * x - 1, (0, 2, -1, 1)).to_dict()
    if change == "missing_payload":
        del data["native_mask"]
    elif change == "missing_marker":
        del data["mask"]
    else:
        data["mask"] = "<<FUNCTION_NOT_SERIALIZABLE>>"
    with pytest.raises(ValueError, match="must agree"):
        TrimmedImplicitCurve.from_dict(data)


def test_native_codec_cycle_rejected_before_recursive_serialization():
    field = trim(x * x - 1, (0, 2, -1, 1))
    field.base_curve = field
    with pytest.raises(ValueError, match="native evaluators"):
        field.to_dict()


def test_opaque_contains_property_failure_is_unverified_not_a_crash():
    class BrokenContains(TrimmedImplicitCurve):
        @property
        def contains(self):
            raise RuntimeError("opaque lookup unavailable")

    field = BrokenContains(curve(x * x - 1), RectangleMask(-2, 2, -1, 1))
    report = find(field, curve(y))
    assert report["points"] == []
    assert all(root["root_trim_membership"] == "unverified" for root in report["roots"])


def test_oblique_halfplane_callback_is_the_next_unresolved_predicate():
    field = TrimmedImplicitCurve(curve(x * x - 2), lambda a, b: a + b >= 0)
    report = find(field, curve(y - x))
    assert report["points"] == []
    positive = report["roots"][1]
    assert positive["representative_contains"] == [True]
    assert positive["root_trim_membership"] == "unverified"
