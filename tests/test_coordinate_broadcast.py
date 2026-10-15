"""Coordinate contracts and analytic controls for cheaper numerical refinement."""

import numpy as np
import pytest
import sympy as sp

from geometry import ImplicitCurve, ProceduralCurve, TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections
from geometry.numeric import broadcast_coordinates, field_result


@pytest.mark.parametrize(
    "x,y",
    [
        (1.25, -0.0),
        (True, 2),
        (np.float32(0.25), np.int64(3)),
        (np.float16(0.5), np.float64(-2)),
        (np.array(1.0), np.array(2.0)),
        (np.array(True), np.array(2, dtype=np.int32)),
        (np.array(1.0), 2.0),
        ([1, 2, 3], [4, 5, 6]),
        (np.arange(6).reshape(2, 3), np.ones((2, 3), dtype=np.float32)),
        (np.empty((0, 3)), np.empty((0, 3))),
        (np.empty((0,)), 1.0),
        (np.array([0.0, -0.0, np.nan, np.inf, -np.inf]), np.zeros(5)),
        (np.arange(3.0)[:, None], np.arange(4.0)[None, :]),
        (np.arange(3.0), 2.0),
        (1.0, np.arange(3.0)),
    ],
)
def test_coordinate_values_shape_dtype_and_scalar_result(x, y):
    expected_x, expected_y = np.broadcast_arrays(
        np.asarray(x).astype(float), np.asarray(y).astype(float)
    )
    actual_x, actual_y, scalar = broadcast_coordinates(x, y)
    for actual, expected in ((actual_x, expected_x), (actual_y, expected_y)):
        assert actual.dtype == np.dtype(float)
        assert actual.shape == expected.shape
        np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(np.signbit(actual), np.signbit(expected))
    assert scalar is (np.isscalar(x) and np.isscalar(y))
    result = field_result(actual_x, actual_x.shape, scalar)
    assert isinstance(result, float) if scalar else isinstance(result, np.ndarray)
    np.testing.assert_array_equal(result, expected_x)


@pytest.mark.parametrize(
    "layout", ["contiguous", "strided", "reversed", "readonly", "empty"]
)
def test_equal_shape_float_arrays_retain_aliasing_strides_and_writeability(layout):
    first, second = np.arange(12.0), np.arange(12.0) + 10
    if layout == "strided":
        first, second = first[::2], second[::2]
    elif layout == "reversed":
        first, second = first[::-1], second[::-1]
    elif layout == "readonly":
        first.flags.writeable = second.flags.writeable = False
    elif layout == "empty":
        first, second = first[:0], second[:0]
    actual_x, actual_y, scalar = broadcast_coordinates(first, second)
    expected_x, expected_y = np.broadcast_arrays(first, second)
    assert not scalar
    for actual, expected in ((actual_x, expected_x), (actual_y, expected_y)):
        assert actual is expected
        assert actual.strides == expected.strides
        assert actual.flags.writeable == expected.flags.writeable


@pytest.mark.parametrize(
    "bad",
    [1j, np.array([1 + 0j]), "1", ["2"], np.array([1], dtype=object), None],
)
@pytest.mark.parametrize("side", [0, 1])
def test_invalid_real_coordinate_on_either_side_is_rejected(bad, side):
    inputs = [1.0, 2.0]
    inputs[side] = bad
    with pytest.raises(ValueError, match="real numeric"):
        broadcast_coordinates(*inputs)


def test_incompatible_shapes_still_raise():
    with pytest.raises(ValueError):
        broadcast_coordinates(np.ones(2), np.ones(3))


X, Y = sp.symbols("x y")


def curve(expression):
    return ImplicitCurve(expression, (X, Y))


def find(first, second, *, search=2.0, tolerance=1e-10, **kwargs):
    return find_curve_intersections(
        first,
        second,
        search_range=search,
        grid_resolution=40,
        tolerance=tolerance,
        **kwargs,
    )


@pytest.mark.parametrize("scale", [0.01, 1.0, 1000.0])
@pytest.mark.parametrize("order", [False, True])
@pytest.mark.parametrize("offset", [-0.001, 0.0, 0.001])
def test_analytic_parabola_line_contact_disjoint_and_two_crossings(
    scale, order, offset
):
    # Dimensionless fields separate geometric scale from field residual units.
    first = curve(Y / scale - (X / scale) ** 2)
    second = curve(Y / scale - sp.Float(offset))
    if order:
        first, second = second, first
    result = sorted(find(first, second, search=2 * scale))
    if offset < 0:
        assert result == []
    else:
        expected = (
            [(0.0, 0.0)]
            if offset == 0
            else [
                (-scale * np.sqrt(offset), scale * offset),
                (scale * np.sqrt(offset), scale * offset),
            ]
        )
        np.testing.assert_allclose(result, expected, rtol=0, atol=scale * 1e-7)
        assert all(
            abs(first.evaluate(*point)) < 1e-10 and abs(second.evaluate(*point)) < 1e-10
            for point in result
        )


@pytest.mark.parametrize("kind", ["native", "procedural", "replacement"])
def test_translated_parabola_and_active_callback_contact(kind):
    expression = Y - 1 - (X - sp.Rational(1, 2)) ** 2
    if kind == "native":
        first = curve(expression)
    elif kind == "procedural":
        first = ProceduralCurve(lambda x, y: y - 1 - (x - 0.5) ** 2)
    else:
        first = curve(X * X + Y * Y - 1)
        first.evaluate = lambda x, y: y - 1 - (x - 0.5) ** 2
    result = find(first, curve(Y - 1))
    np.testing.assert_allclose(result, [(0.5, 1.0)], atol=1e-7, rtol=0)


@pytest.mark.parametrize("mask_kind", ["closed", "strict", "reject", "raises"])
def test_contact_trim_endpoint_and_callback_authority(mask_kind):
    def mask(x, y):
        if mask_kind == "raises":
            raise ValueError("mask failure")
        if mask_kind == "reject":
            return False
        return x >= 0.5 if mask_kind == "closed" else x > 0.5

    line = TrimmedImplicitCurve(
        curve(Y - 1),
        mask,
        xmin=0.5,
        xmax=1.0,
        ymin=1.0,
        ymax=1.0,
        endpoints=[(0.5, 1.0), (1.0, 1.0)],
    )
    result = find(curve(Y - 1 - (X - sp.Rational(1, 2)) ** 2), line)
    if mask_kind == "closed":
        np.testing.assert_allclose(result, [(0.5, 1.0)], atol=1e-7, rtol=0)
    elif mask_kind in ("reject", "raises"):
        assert result == []
    else:
        assert all(px > 0.5 and abs(py - 1) < 1e-7 for px, py in result)


def test_quartic_contact_deduplicates_without_short_budget_acceptance():
    result = find(curve(Y - X**4), curve(Y))
    np.testing.assert_allclose(result, [(0.0, 0.0)], atol=1e-10, rtol=0)


@pytest.mark.parametrize("overlap", [False, True])
def test_coincidence_is_separate_from_isolated_contact(overlap):
    assert find(curve(Y - X * X), curve(Y - X * X), detect_overlap=overlap) == []


def test_recognized_circle_contact_and_registry_remain_intact():
    calls = []
    first, second = curve(X * X + Y * Y - 1000000), curve(Y - 1000)
    result = find(
        first, second, search=3000, registry_callback=lambda *args: calls.append(args)
    )
    assert result == [(0.0, 1000.0)]
    assert calls == [(0.0, 1000.0, first, second)]
