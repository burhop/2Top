"""Native exact contacts versus nearby numerical roots and callback authority."""

import copy
import pickle

import numpy as np
import pytest
import sympy as sp

from geometry import ConicSection, ImplicitCurve, TrimmedImplicitCurve
from geometry.curve_intersections import (
    _native_circle_or_line,
    _native_tangent_candidates,
    find_curve_intersections,
)
from geometry.level_set_curve import LevelSetCurve
from geometry.procedural_curve import ProceduralCurve

x, y = sp.symbols("x y")


def curve(expression, cls=ImplicitCurve):
    return cls(expression, (x, y))


def find(a, b, scale=1, **kwargs):
    return find_curve_intersections(
        a,
        b,
        search_range=3 * float(scale),
        grid_resolution=64,
        tolerance=1e-8,
        **kwargs,
    )


def pair(kind, r, cls=ImplicitCurve):
    a = x * x + y * y - r * r
    if kind == "line":
        b = y - r
        expected = (0.0, float(r))
    elif kind == "oblique_line":
        b = 3 * x + 4 * y - 5 * r
        expected = (float(3 * r / 5), float(4 * r / 5))
    elif kind == "external":
        b = (x - 2 * r) ** 2 + y * y - r * r
        expected = (float(r), 0.0)
    elif kind == "oblique_external":
        b = (x - 6 * r / 5) ** 2 + (y - 8 * r / 5) ** 2 - r * r
        expected = (float(3 * r / 5), float(4 * r / 5))
    else:
        a = x * x + y * y - 4 * r * r
        b = (x - r) ** 2 + y * y - r * r
        expected = (float(2 * r), 0.0)
    return curve(a, cls), curve(b, cls), expected


@pytest.mark.parametrize(
    "scale", [sp.Rational(1, 1000), sp.Integer(1), sp.Integer(1000)]
)
@pytest.mark.parametrize("cls", [ImplicitCurve, ConicSection])
@pytest.mark.parametrize(
    "kind", ["line", "oblique_line", "external", "oblique_external", "internal"]
)
@pytest.mark.parametrize("reverse", [False, True])
def test_one_isolated_contact_across_scales_and_curve_order(scale, cls, kind, reverse):
    a, b, expected = pair(kind, scale, cls)
    if reverse:
        a, b = b, a
    result = find(a, b, scale)
    assert len(result) == 1
    np.testing.assert_allclose(result, [expected], atol=1e-12 * float(scale), rtol=0)
    assert np.linalg.norm([a.evaluate(*result[0]), b.evaluate(*result[0])]) < 1e-8
    # Already-compiled native kernels remain eligible on later calls.
    assert find(a, b, scale) == result


@pytest.mark.parametrize(
    "weight", [sp.Rational(1, 10**12), sp.Integer(-7), sp.Rational(13, 4)]
)
@pytest.mark.parametrize("detect_overlap", [False, True])
def test_field_scaling_cannot_hide_or_duplicate_a_true_contact(weight, detect_overlap):
    a, b = curve(weight * (x * x + y * y - 1)), curve(-3 * weight * (y - 1))
    assert find(a, b, detect_overlap=detect_overlap) == [(0.0, 1.0)]


@pytest.mark.parametrize(
    "scale", [sp.Rational(1, 1000), sp.Integer(1), sp.Integer(1000)]
)
@pytest.mark.parametrize("kind", ["line", "circles"])
@pytest.mark.parametrize("direction", [-1, 1])
def test_near_tangent_crossings_stay_two_and_disjoint_cases_stay_empty(
    scale, kind, direction
):
    r = scale
    offset = sp.Rational(direction, 1000)
    a = curve(x * x + y * y - r * r)
    if kind == "line":
        h = r * (1 + offset)
        b = curve(y - h)
        expected = (
            []
            if direction > 0
            else [
                (-float(sp.sqrt(r * r - h * h)), float(h)),
                (float(sp.sqrt(r * r - h * h)), float(h)),
            ]
        )
    else:
        distance = 2 * r * (1 + offset)
        b = curve((x - distance) ** 2 + y * y - r * r)
        half = distance / 2
        height = sp.sqrt(r * r - half * half) if direction < 0 else 0
        expected = (
            []
            if direction > 0
            else [(float(half), -float(height)), (float(half), float(height))]
        )
    assert _native_tangent_candidates(a, b) is None
    tolerance = float(min(r * r, r)) * 1e-12
    result = find_curve_intersections(
        a, b, search_range=3 * float(r), grid_resolution=100, tolerance=tolerance
    )
    assert len(result) == len(expected)
    if expected:
        np.testing.assert_allclose(
            sorted(result), sorted(expected), atol=float(r) * 1e-7, rtol=0
        )
        assert np.linalg.norm(np.subtract(*result)) > 1e-5


@pytest.mark.parametrize("direction", [-np.inf, np.inf])
def test_nextafter_line_offset_is_not_classified_as_an_exact_tangent(direction):
    offset = np.nextafter(1.0, direction)
    assert (
        _native_tangent_candidates(
            curve(x * x + y * y - 1), curve(y - sp.Float(offset))
        )
        is None
    )


@pytest.mark.parametrize("detect_overlap", [False, True])
def test_coincident_native_circles_are_not_isolated_contacts(detect_overlap):
    a = curve(x * x + y * y - 1)
    b = curve(-7 * (x * x + y * y - 1))
    assert _native_tangent_candidates(a, b) == []
    assert find(a, b, detect_overlap=detect_overlap) == []
    assert (
        _native_tangent_candidates(a, curve(x * x + y * y - sp.Rational(1, 4))) is None
    )
    assert find(a, curve(x * x + y * y - sp.Rational(1, 4))) == []


@pytest.mark.parametrize(
    "mask,expected",
    [
        (lambda x, y: 0 <= x <= 1, [(0.0, 1.0)]),
        (lambda x, y: 0 < x <= 1, []),
        (lambda x, y: False, []),
    ],
)
def test_trim_endpoint_membership_is_applied_to_the_canonical_contact(mask, expected):
    a = curve(x * x + y * y - 1)
    b = TrimmedImplicitCurve(
        curve(y - 1),
        mask,
        xmin=0.0,
        xmax=1.0,
        ymin=1.0,
        ymax=1.0,
        endpoints=[(0.0, 1.0), (1.0, 1.0)],
    )
    assert find(a, b) == expected


def test_final_contains_override_remains_authoritative():
    a = curve(x * x + y * y - 1)
    b = TrimmedImplicitCurve(curve(y - 1), lambda x, y: True)
    b.contains = lambda x, y, tolerance: False
    assert find(a, b) == []


def test_raising_trim_callback_retains_iterative_failure_behavior():
    def reject(x, y):
        raise ValueError("trim callback failure")

    b = TrimmedImplicitCurve(curve(y - 1), reject)
    assert find(curve(x * x + y * y - 1), b) == []


@pytest.mark.parametrize("kind", ["public", "private", "trim"])
def test_replacement_evaluator_with_extra_roots_is_not_shortcut(kind):
    a = curve(x * x + y * y - 1)

    def actual(x, y):
        return x * (x - 1)

    if kind == "public":
        a.evaluate = actual
    elif kind == "private":
        a.evaluate(0.1, 0.2)
        a._eval_func = actual
    else:
        a = TrimmedImplicitCurve(a, lambda x, y: True)
        a.evaluate = actual
        a.contains = lambda x, y, tolerance: True
    b = curve(y - 1)
    assert _native_tangent_candidates(a, b) is None
    result = find(a, b)
    assert len(result) == 2
    np.testing.assert_allclose(
        sorted(result), [(0.0, 1.0), (1.0, 1.0)], atol=1e-7, rtol=0
    )


def test_compiled_expression_and_variables_mutations_refresh_provenance():
    a = curve(x * x + y * y - 1, ConicSection)
    a._extract_coefficients()
    a.evaluate(0.1, 0.2)
    a.expression = x * x + (y - 3) ** 2 - 1
    assert a._eval_func is a._native_eval_func is None
    assert a._native_eval_state is None
    assert find(a, curve(y - 4), scale=2) == [(0.0, 4.0)]
    a.variables = (y, x)
    assert a._eval_func is a._native_eval_func is None
    assert a._native_eval_state is None
    assert find(a, curve(x - 4), scale=2) == [(4.0, 0.0)]


def test_stale_private_expression_cache_does_not_prove_symbolic_authority():
    a = curve(x * x + y * y - 1)
    a.evaluate(0.1, 0.2)
    a._expression = (x - 1) ** 2 + y * y - 1
    assert _native_tangent_candidates(a, curve(y - 1)) is None
    result = find(a, curve(y - 1))
    np.testing.assert_allclose(result, [(0.0, 1.0)], atol=1e-7, rtol=0)


def test_copy_and_uncompiled_pickle_keep_kernel_contracts():
    a = curve(x * x + y * y - 1)
    restored = pickle.loads(pickle.dumps(a))
    assert find(restored, curve(y - 1)) == [(0.0, 1.0)]
    a.evaluate(0.1, 0.2)
    clone = copy.deepcopy(a)
    assert clone._eval_func is clone._native_eval_func
    a.expression = (x - 1) ** 2 + y * y - 1
    assert find(clone, curve(y - 1)) == [(0.0, 1.0)]
    assert find(a, curve(y - 1)) == [(1.0, 1.0)]


def test_procedural_and_level_set_wrappers_keep_the_numerical_route():
    assert (
        _native_tangent_candidates(
            ProceduralCurve(lambda x, y: x * x + y * y - 1), curve(y - 1)
        )
        is None
    )
    assert (
        _native_tangent_candidates(
            LevelSetCurve(curve(x * x + y * y - 1), 0.0), curve(y - 1)
        )
        is None
    )


@pytest.mark.parametrize(
    "expression",
    [(x + y) ** 100000, x**3 + y, sp.sin(x) + y, x * x + 2 * y * y - 1, x * x + y * y],
)
def test_unsupported_or_degenerate_fields_are_not_generalized(expression):
    assert _native_circle_or_line(curve(expression)) is None


def test_huge_degree_is_rejected_before_poly_expansion(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("expanded unsupported polynomial")

    monkeypatch.setattr(sp, "Poly", forbidden)
    assert _native_circle_or_line(curve((x + y) ** 100000)) is None


def test_float_factored_translation_preserves_the_stored_geometry():
    a = curve((x - sp.Float(0.1)) ** 2 + y * y - 1)
    assert find(a, curve(y - 1)) == [(0.1, 1.0)]


def test_numeric_residual_failure_falls_back_instead_of_asserting_a_contact(
    monkeypatch,
):
    import geometry.curve_intersections as module

    center = sp.Integer(10) ** 12
    a = curve((x - center) ** 2 + y * y - 1)
    b = curve(3 * (x - center) + 4 * y - 5)
    candidate = _native_tangent_candidates(a, b)[0]
    assert np.linalg.norm([a.evaluate(*candidate), b.evaluate(*candidate)]) > 1e-8
    calls = []
    previous = module._are_curves_identical_fast

    def record(*args):
        calls.append(1)
        return previous(*args)

    monkeypatch.setattr(module, "_are_curves_identical_fast", record)
    assert (
        find_curve_intersections(
            a, b, search_range=float(center) + 2, grid_resolution=64, tolerance=1e-8
        )
        == []
    )
    assert calls == [1]


def test_search_limit_max_points_and_registry_are_shared():
    a, b, point = pair("external", sp.Integer(1000))
    records = []
    assert find(a, b, 1000, registry_callback=lambda *args: records.append(args)) == [
        point
    ]
    assert records == [(*point, a, b)]
    assert find(a, b, 1000, max_points=0) == []
    assert find(a, b, 1000, max_points=1) == [point]
    assert find(a, b, 1) == []


def test_nonfinite_actual_evaluation_is_not_a_valid_failure_sentinel():
    radius = sp.Integer(10) ** 200
    a = curve(x * x + y * y - radius * radius)
    b = curve(y - radius)
    assert _native_tangent_candidates(a, b) == [(0.0, float(radius))]
    with np.errstate(over="ignore", invalid="ignore"):
        assert not np.isfinite(a.evaluate(0.0, float(radius)))
        assert (
            find_curve_intersections(
                a, b, search_range=2e200, grid_resolution=16, tolerance=1e7
            )
            == []
        )
