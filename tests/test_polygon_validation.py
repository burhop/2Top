import numpy as np
import pytest
import sympy as sp

from geometry.composite_curve import create_polygon_from_edges


def test_polygon_accepts_closed_first_last_duplicate():
    # Triangle with first==last should be accepted after normalization
    pts = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0), (0.0, 0.0)]
    poly = create_polygon_from_edges(pts)
    assert poly.is_closed()
    assert poly.contains(0.5, 0.2, region_containment=True)


def test_polygon_rejects_too_few_unique_vertices():
    # After removing duplicates, less than 3 unique vertices
    with pytest.raises(ValueError):
        create_polygon_from_edges([(0, 0), (1, 1), (1, 1)])


def test_polygon_rejects_non_finite():
    with pytest.raises(ValueError):
        create_polygon_from_edges([(0, 0), (1, np.inf), (1, 1)])
    with pytest.raises(ValueError):
        create_polygon_from_edges([(0, 0), (np.nan, 0), (1, 1)])


def test_polygon_rejects_collinear():
    # Points on a line => zero area
    with pytest.raises(ValueError):
        create_polygon_from_edges([(0, 0), (1, 1), (2, 2)])


def test_polygon_rejects_zero_length_edge():
    # Consecutive duplicate creates zero-length edge
    with pytest.raises(ValueError):
        create_polygon_from_edges([(0, 0), (1, 0), (1, 0), (0, 1)])
