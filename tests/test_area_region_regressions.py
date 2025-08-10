import numpy as np
import sympy as sp
import pytest

from geometry import AreaRegion
from geometry.factories import create_polygon_from_edges, create_square_from_edges


def polygon_area(vertices):
    # Shoelace formula for expected area
    A = 0.0
    n = len(vertices)
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        A += x0 * y1 - x1 * y0
    return abs(0.5 * A)


def test_non_square_quadrilateral_does_not_use_square_fast_path():
    """
    A general 4-vertex polygon must not be treated as a square fast-path.
    Its area should match the polygon shoelace area.
    """
    # Define a simple rectangle that's not produced by the square factory
    # to ensure _is_square is not set (e.g., a 3x3 square translated/rotated would still be polygonal here).
    verts = [
        (-1.5, -1.0),
        ( 1.5, -1.0),
        ( 1.2,  1.3),
        (-1.8,  1.1),
    ]
    poly = create_polygon_from_edges(verts)
    region = AreaRegion(poly)

    expected = polygon_area(verts)
    area = region.area()

    assert pytest.approx(area, rel=1e-6, abs=1e-6) == expected


def test_square_uses_square_bounds_area_correct():
    """
    Squares built via create_square_from_edges() should have correct area via _square_bounds.
    """
    sq = create_square_from_edges((-2.0, -2.0), (1.0, 4.0))  # width=3, height=6 => area=18
    region = AreaRegion(sq)

    area = region.area()
    assert pytest.approx(area, rel=1e-12, abs=1e-12) == 18.0


def test_polygon_triangle_area_correct():
    """
    Sanity check: triangle area via polygon approximation matches shoelace.
    """
    tri = [(0.0, 0.0), (3.0, 0.0), (0.0, 2.0)]  # area = 3.0
    poly = create_polygon_from_edges(tri)
    region = AreaRegion(poly)

    assert pytest.approx(region.area(), rel=1e-12, abs=1e-12) == 3.0
