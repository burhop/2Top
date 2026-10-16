"""Independent Fraction/Decimal oracles for half-plane signs and root membership."""

from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import math

import numpy as np
import pytest
import sympy as sp

from geometry import HalfPlaneMask, ImplicitCurve, RectangleMask, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections as find

x, y = sp.symbols("x y")


def curve(expression):
    return ImplicitCurve(sp.sympify(expression), (x, y))


def trim(expression, coefficients, closed=True):
    return TrimmedImplicitCurve(
        curve(expression), HalfPlaneMask(*coefficients, closed=closed)
    )


def oracle(coefficients, px, py, closed):
    a, b, c = (Fraction(sp.Rational(v)) for v in coefficients)
    exact = a * Fraction.from_float(float(px)) + b * Fraction.from_float(float(py)) + c
    return exact >= 0 if closed else exact > 0


@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize(
    "coefficients,point",
    [
        ((1, 1, 0), (1, -1)),
        ((1, sp.Rational(1, 2**1100), 0), (0, 1)),
        ((2**2000, 1, 0), (0, 1)),
        ((1, -1, sp.Rational(1, 2**1100)), (1e308, 1e308)),
        ((1, -1, -sp.Rational(1, 2**1100)), (1e308, 1e308)),
        ((1, -1, 0), (1e308, 1e308)),
        ((math.nextafter(0, 1), 0, 0), (math.nextafter(0, 1), 0)),
        ((sp.Rational(1, 3), sp.Rational(-1, 10), sp.Rational(1, 7)), (0.1, 1 / 3)),
        ((1, 1, 0), (float.fromhex("0x1.fffffffffffffp+1023"),) * 2),
    ],
)
def test_exact_scalar_sign_extremes(coefficients, point, closed):
    mask = HalfPlaneMask(*coefficients, closed=closed)
    assert mask(*point) == oracle(coefficients, *point, closed)


@pytest.mark.parametrize("closed", [False, True])
def test_seeded_broadcast_array_signs_match_fraction_oracle(closed):
    rng = np.random.default_rng(3030)
    values = rng.normal(size=(12, 9))
    for coefficients in [
        (1, 1, 0),
        (3, -7, sp.Rational(1, 3)),
        (sp.Rational(1, 2**1100), 1, -1),
        (2**2000, -(2**2000), 1),
    ]:
        mask = HalfPlaneMask(*coefficients, closed=closed)
        other = values.copy()
        other[::2] = values[::2]
        expected = np.array(
            [
                oracle(coefficients, a, b, closed)
                for a, b in zip(values.flat, other.flat)
            ]
        ).reshape(values.shape)
        np.testing.assert_array_equal(mask(values, other), expected)
    mask = HalfPlaneMask(1, -2, 0, closed=closed)
    a, b = np.broadcast_arrays(values[:, 0, None], values[0])
    expected = np.array(
        [oracle((1, -2, 0), px, py, closed) for px, py in zip(a.flat, b.flat)]
    ).reshape(a.shape)
    np.testing.assert_array_equal(mask(values[:, 0, None], values[0]), expected)


@pytest.mark.parametrize("closed", [False, True])
def test_seeded_extreme_cancellation_signs_have_independent_fraction_oracles(closed):
    rng = np.random.default_rng(3031)
    for index in range(80):
        powers = rng.integers(-900, 901, size=2)
        a = sp.Rational(2) ** int(powers[0]) * (-1 if index % 2 else 1)
        b = sp.Rational(2) ** int(powers[1]) * (-1 if index % 3 else 1)
        px = math.ldexp(0.75, int(rng.integers(-500, 501)))
        py = math.ldexp(-0.625, int(rng.integers(-500, 501)))
        epsilon = sp.Rational((index % 3) - 1, 2**1100)
        c = -a * sp.Rational(px) - b * sp.Rational(py) + epsilon
        mask = HalfPlaneMask(a, b, c, closed=closed)
        assert mask(px, py) == oracle((a, b, c), px, py, closed)


@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("constant", [-1, 0, 1])
def test_degenerate_normal_all_or_empty(closed, constant):
    mask = HalfPlaneMask(0, 0, constant, closed=closed)
    expected = constant >= 0 if closed else constant > 0
    assert mask(1, -2) == expected
    np.testing.assert_array_equal(
        mask(np.array([0, np.inf, np.nan]), 0), [expected, False, False]
    )
    report = find(trim(x * x - 2, (0, 0, constant), closed), curve(y))
    assert len(report["points"]) == (2 if expected else 0)


@pytest.mark.parametrize(
    "value",
    [
        True,
        np.inf,
        -np.inf,
        np.nan,
        1j,
        "1/3",
        sp.sqrt(2),
        2**5000,
        sp.Rational(1, 2**5000),
    ],
)
def test_invalid_coefficients_rejected(value):
    with pytest.raises(ValueError):
        HalfPlaneMask(value, 1)


@pytest.mark.parametrize("value", [0, 1, "closed", None, np.nan])
def test_closed_requires_actual_boolean(value):
    with pytest.raises(ValueError):
        HalfPlaneMask(1, 1, closed=value)


def test_compact_huge_float_rejected_before_exact_conversion():
    value = sp.Float._new((0, 1, 100000000, 1), 53)
    with pytest.raises(ValueError):
        HalfPlaneMask(value, 1)


def test_native_mask_immutable_and_coefficients_retained():
    mask = HalfPlaneMask(Fraction(1, 3), 0.1, -7, closed=np.bool_(False))
    assert mask.coefficients == (sp.Rational(1, 3), sp.Rational(0.1), -7)
    with pytest.raises(FrozenInstanceError):
        mask.closed = True
    assert HalfPlaneMask.from_dict(json.loads(json.dumps(mask.to_dict()))) == mask


@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("scale", [sp.Rational(1, 10**100), 1, 10**100, -1])
def test_motivating_irrational_oblique_contact_and_scaling(closed, scale):
    report = find(trim((x * x - 2) ** 4, (scale, scale, 0), closed), curve(y - x))
    assert len(report["points"]) == 1
    root = next(r for r in report["roots"] if r["accepted"])
    assert root["multiplicity"] == 4
    assert root["point"][0] > 0 if scale > 0 else root["point"][0] < 0
    assert root["root_trim_membership"] == "model_root_included"
    assert root["root_trim_checks"] == [
        {"kind": "native_half_plane", "status": "included"}
    ]
    with localcontext() as context:
        context.prec = 160
        expected = Decimal(2).sqrt() * (1 if scale > 0 else -1)
        assert abs(Decimal.from_float(root["point"][0]) - expected) <= Decimal("1e-8")


@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("normal", [1, -1])
def test_flat_boundary_tangency_equality_is_not_fuzzy(closed, normal):
    report = find(trim(x**8, (normal, 0, 0), closed), curve(y))
    assert report["points"] == ([(0, 0)] if closed else [])
    root = report["roots"][0]
    assert root["multiplicity"] == 8
    assert root["root_trim_membership"] == (
        "exact_point_accepted" if closed else "exact_point_excluded"
    )


@pytest.mark.parametrize("closed", [False, True])
def test_half_plane_constant_on_oblique_line(closed):
    report = find(
        trim(x * x - 2, (1, 1, -sp.Rational(1, 3)), closed),
        curve(y + x - sp.Rational(1, 3)),
    )
    assert all(
        r["root_trim_membership"]
        == ("model_root_included" if closed else "model_root_excluded")
        for r in report["roots"]
    )
    # Exact roots lie on the boundary; rounded representatives may fail closed
    # containment, which remains an independent gate.
    assert len(report["points"]) == sum(
        closed and all(r["representative_contains"]) for r in report["roots"]
    )


@pytest.mark.parametrize("direction", [-1, 0, 1])
@pytest.mark.parametrize("normal", [1, -1])
def test_negative_slope_threshold_next_to_sqrt_two(direction, normal):
    threshold = math.sqrt(2)
    if direction:
        threshold = math.nextafter(threshold, math.inf if direction > 0 else -math.inf)
    report = find(
        trim(x * x - 2, (normal, 0, -normal * sp.Rational(threshold))),
        curve(y),
        position_tolerance=1e-14,
    )
    positive = report["roots"][1]
    with localcontext() as context:
        context.prec = 160
        included = normal * (Decimal(2).sqrt() - Decimal.from_float(threshold)) >= 0
    assert positive["root_trim_membership"] == (
        "model_root_included" if included else "model_root_excluded"
    )


def test_vertical_parameter_and_nested_rectangle_half_plane():
    base = trim(y * y - 2, (0, 1, 0))
    field = TrimmedImplicitCurve(base, RectangleMask(-1, 1, -2, 2))
    report = find(field, curve(x))
    assert report["parameter_axis"] == "y"
    assert len(report["points"]) == 1 and report["points"][0][1] > 0
    opaque = TrimmedImplicitCurve(field, lambda a, b: True)
    report = find(opaque, curve(x))
    assert report["points"] == []
    assert report["roots"][0]["root_trim_membership"] == "model_root_excluded"
    assert report["roots"][1]["root_trim_membership"] == "unverified"


def test_declared_half_plane_does_not_certify_opaque_callback():
    field = TrimmedImplicitCurve(curve(x * x - 2), lambda a, b: a + b >= 0)
    assert find(field, curve(y - x))["points"] == []


@pytest.mark.parametrize(
    "change", ["mask", "coefficient", "mode", "cache", "contains", "bbox", "delete"]
)
def test_half_plane_predicate_mutation_invalidates_all_proofs(change):
    inner = trim(x * x - 1, (1, 1, 0))

    def mutate(a, b):
        if change == "mask":
            inner.mask = HalfPlaneMask(-1, -1)
        elif change == "coefficient":
            object.__setattr__(inner.mask, "a", sp.Rational(-1))
        elif change == "mode":
            object.__setattr__(inner.mask, "closed", False)
        elif change == "cache":
            object.__setattr__(inner.mask, "_float_coefficients", ((0.0, 0.0),) * 3)
        elif change == "contains":
            inner.contains = lambda *args: False
        elif change == "bbox":
            inner._xmin = 2
        elif hasattr(inner.mask, "a"):
            object.__delattr__(inner.mask, "a")
        return True

    report = find(TrimmedImplicitCurve(inner, mutate), curve(y - x))
    assert report["status"] == "trim_changed"
    assert report["points"] == []
    assert all(r["root_trim_membership"] == "unverified" for r in report["roots"])


def test_native_roundtrip_nested_and_raw_scale_preserved():
    for scale in (sp.Rational(1, 10**100), -(10**100)):
        field = trim((x * x - 2) ** 4, (scale, scale, 0), False)
        field = TrimmedImplicitCurve(field, RectangleMask(-2, 2, -2, 2))
        data = json.loads(json.dumps(field.to_dict(), allow_nan=False))
        restored = ImplicitCurve.from_dict(data)
        assert restored.base_curve.mask.coefficients == (scale, scale, 0)
        assert restored.base_curve.mask.closed is False
        assert find(field, curve(y - x)) == find(restored, curve(y - x))


@pytest.mark.parametrize(
    "text", ["1/0", "sqrt(2)", "__import__('os')", "1+2", "1e10000", "9" * 2500]
)
def test_invalid_native_coefficient_data_never_falls_back(text):
    data = trim(x * x - 2, (1, 1, 0)).to_dict()
    data["native_mask"]["coefficients"][0] = text
    with pytest.raises(ValueError):
        TrimmedImplicitCurve.from_dict(data)


@pytest.mark.parametrize(
    "change",
    ["missing_payload", "missing_marker", "mismatch", "invalid_closed", "unknown_type"],
)
def test_native_half_plane_codec_schema_guard(change):
    data = trim(x * x - 2, (1, 1, 0)).to_dict()
    if change == "missing_payload":
        del data["native_mask"]
    elif change == "missing_marker":
        del data["mask"]
    elif change == "mismatch":
        data["mask"] = "RectangleMask"
    elif change == "invalid_closed":
        data["native_mask"]["closed"] = 1
    else:
        data["mask"] = data["native_mask"]["type"] = "UnknownMask"
    with pytest.raises(ValueError):
        TrimmedImplicitCurve.from_dict(data)


@pytest.mark.parametrize("method", ["contains", "evaluate", "base_evaluate", "kernel"])
def test_native_codec_rejects_method_authority_changes(method):
    field = trim(x * x - 2, (1, 1, 0))
    if method == "base_evaluate":
        field.base_curve.evaluate = lambda *args: False
    elif method == "kernel":
        field.base_curve._eval_func = lambda *args: False
    else:
        setattr(field, method, lambda *args: False)
    with pytest.raises(ValueError):
        field.to_dict()


def test_additional_bbox_and_subclass_remain_opaque():
    field = trim(x * x - 2, (1, 1, 0))
    field._xmin = 0
    assert find(field, curve(y - x))["points"] == []

    class OtherHalfPlane(HalfPlaneMask):
        def __call__(self, a, b):
            return True

    field = TrimmedImplicitCurve(curve(x * x - 2), OtherHalfPlane(1, 1))
    assert find(field, curve(y - x))["points"] == []


@pytest.mark.parametrize("closed", [False, True])
def test_nonfinite_coordinates_are_outside_nondegenerate_half_plane(closed):
    mask = HalfPlaneMask(1, -1, 1, closed=closed)
    np.testing.assert_array_equal(
        mask(np.array([np.inf, -np.inf, np.nan, 0]), 0), [False, False, False, True]
    )


def test_derived_threshold_resource_limit_remains_unverified():
    field = trim(x * x - 2, (sp.Rational(1, 2**3000), 0, 2**3000))
    report = find(field, curve(y))
    assert report["points"] == []
    assert all(r["root_trim_membership"] == "unverified" for r in report["roots"])
    assert all(r["root_trim_checks"][0]["kind"] == "callback" for r in report["roots"])


def test_anchor_factory_chord_is_the_next_native_predicate_opportunity():
    field = TrimmedImplicitCurve.from_anchors(
        curve(x * x - 2), (-2, -2), (2, 2), positive_half_plane=True, tolerance=0
    )
    report = find(field, curve(y - x))
    assert report["points"] == []
    assert all(r["representative_contains"] == [True] for r in report["roots"])
    assert all(r["root_trim_membership"] == "unverified" for r in report["roots"])
    native = trim(x * x - 2, (1, 1, 4))
    native = TrimmedImplicitCurve(native, HalfPlaneMask(-1, -1, 4))
    native = TrimmedImplicitCurve(native, HalfPlaneMask(-1, 1, 0))
    assert len(find(native, curve(y - x))["points"]) == 2
