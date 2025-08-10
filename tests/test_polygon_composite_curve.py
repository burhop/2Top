import numpy as np
import sympy as sp
import pytest

from geometry.composite_curve import CompositeCurve, create_polygon_from_edges, create_square_from_edges


def test_convex_polygon_evaluation_triangle():
    # Equilateral-ish triangle
    pts = [(0.0, 0.0), (2.0, 0.0), (1.0, 1.7320508075688772)]
    poly = create_polygon_from_edges(pts)

    # Check convex flags present
    assert getattr(poly, "_is_convex_polygon", False)
    assert hasattr(poly, "_convex_edges_abc") and len(poly._convex_edges_abc) == 3

    # Inside point
    xi, yi = 1.0, 0.6
    val_inside = poly.evaluate(xi, yi)
    assert np.isscalar(val_inside)
    assert val_inside <= 1e-9  # inside should be <= 0

    # On-edge point (midpoint of base)
    xe, ye = 1.0, 0.0
    val_edge = poly.evaluate(xe, ye)
    assert abs(val_edge) <= 1e-6

    # Outside point
    xo, yo = 3.0, 3.0
    val_out = poly.evaluate(xo, yo)
    assert val_out > 0

    # Vectorized check
    X = np.array([xi, xe, xo])
    Y = np.array([yi, ye, yo])
    V = poly.evaluate(X, Y)
    assert V.shape == X.shape
    assert V[0] <= 0 and abs(V[1]) <= 1e-6 and V[2] > 0


def test_polygon_serialization_roundtrip():
    pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    poly = create_polygon_from_edges(pts)

    d = poly.to_dict()
    poly2 = CompositeCurve.from_dict(d)

    # Ensure flags and data preserved
    assert getattr(poly2, "_is_convex_polygon", False)
    assert hasattr(poly2, "_convex_edges_abc") and len(poly2._convex_edges_abc) == 4

    # Evaluate some points to ensure behavior preserved
    p_inside = (1.0, 1.0)
    p_edge = (0.0, 1.0)
    p_out = (3.0, 3.0)

    assert poly2.evaluate(*p_inside) <= 0
    assert abs(poly2.evaluate(*p_edge)) <= 1e-6
    assert poly2.evaluate(*p_out) > 0


def test_nonconvex_polygon_no_convex_flag():
    # Simple concave polygon (arrow shape)
    pts = [(0, 0), (2, 1), (0, 2), (0.5, 1)]
    poly = create_polygon_from_edges(pts)

    # Should not be marked as convex
    assert not getattr(poly, "_is_convex_polygon", False)

    # Evaluation falls back to min over segments; not a region SDF.
    # Just ensure evaluate runs vectorized and scalar without error.
    xs = np.array([0.5, 1.0, 3.0])
    ys = np.array([1.0, 1.0, 3.0])
    vals = poly.evaluate(xs, ys)
    assert vals.shape == xs.shape


def test_contains_region_triangle():
    pts = [(0.0, 0.0), (2.0, 0.0), (1.0, 1.0)]
    poly = create_polygon_from_edges(pts)
    assert poly.is_closed()

    # Inside, boundary, outside
    assert poly.contains(1.0, 0.3, region_containment=True)
    assert poly.contains(1.0, 0.0, region_containment=True)
    assert not poly.contains(3.0, 3.0, region_containment=True)
