import numpy as np
import sympy as sp

from geometry.composite_curve import (
    CompositeCurve,
    create_polygon_from_edges,
    create_square_from_edges,
)


def test_convex_polygon_metadata_and_halfspaces():
    # Triangle is convex
    pts = [(0.0, 0.0), (2.0, 0.0), (1.0, 1.5)]
    poly = create_polygon_from_edges(pts)

    # New convenience methods (fallback to attributes if absent)
    is_convex = poly.is_convex_polygon() if hasattr(poly, "is_convex_polygon") else getattr(poly, "_is_convex_polygon", False)
    edges = poly.halfspace_edges() if hasattr(poly, "halfspace_edges") else getattr(poly, "_convex_edges_abc", None)

    assert is_convex is True
    assert isinstance(edges, (list, tuple))
    assert len(edges) == 3
    for e in edges:
        assert isinstance(e, (list, tuple)) and len(e) == 3

    # Half-space intersection should contain a clear inside point
    assert poly.contains(1.0, 0.4, region_containment=True)
    # Boundary considered inside
    assert poly.contains(1.0, 0.0, region_containment=True)
    # Outside point
    assert not poly.contains(3.0, 3.0, region_containment=True)


def test_nonconvex_polygon_has_no_convex_metadata():
    # Simple concave quad (arrow)
    pts = [(0, 0), (2, 1), (0, 2), (0.5, 1)]
    poly = create_polygon_from_edges(pts)

    is_convex = poly.is_convex_polygon() if hasattr(poly, "is_convex_polygon") else getattr(poly, "_is_convex_polygon", False)
    edges = poly.halfspace_edges() if hasattr(poly, "halfspace_edges") else getattr(poly, "_convex_edges_abc", None)

    assert is_convex is False
    assert edges is None


def test_square_metadata_present_and_contains():
    x, y = sp.symbols("x y")
    sq = create_square_from_edges((-1.0, -1.0), (1.0, 1.0), (x, y))
    assert sq.is_closed()

    # Square fast-path containment
    assert sq.contains(0.0, 0.0, region_containment=True)
    assert sq.contains(1.0, 0.0, region_containment=True)
    assert not sq.contains(2.0, 2.0, region_containment=True)
