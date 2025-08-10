"""
AreaRegion Quickstart Example

Demonstrates:
- Creating squares and triangles as CompositeCurves
- Building AreaRegion with/without holes
- Region containment vs boundary checks
- Accurate area calculation using square fast-path and polygon vertices
"""

import numpy as np
from geometry import AreaRegion
from geometry.factories import create_square_from_edges, create_polygon_from_edges


def demo_square():
    # Axis-aligned rectangle via square factory (with metadata for fast-path)
    sq = create_square_from_edges((-2.0, -2.0), (1.0, 4.0))  # width=3, height=6 => area=18
    region = AreaRegion(sq)

    print("Square region area (expected 18):", region.area())
    print("Inside (0,0):", region.contains(0.0, 0.0))
    print("Outside (5,5):", region.contains(5.0, 5.0))
    # Boundary check uses on-curve
    print("On boundary (1.0,0.0):", region.contains_boundary(1.0, 0.0))


def demo_triangle():
    # Triangle via polygon factory (ensures exact vertices are used for area)
    tri_vertices = [(0.0, 0.0), (3.0, 0.0), (0.0, 2.0)]  # area = 3.0
    tri_curve = create_polygon_from_edges(tri_vertices)
    tri_region = AreaRegion(tri_curve)

    print("Triangle region area (expected 3):", tri_region.area())
    print("Inside (0.5,0.5):", tri_region.contains(0.5, 0.5))
    print("Outside (3,3):", tri_region.contains(3.0, 3.0))
    print("On boundary (1.5,0):", tri_region.contains_boundary(1.5, 0.0))


def main():
    print("--- Square Demo ---")
    demo_square()
    print("\n--- Triangle Demo ---")
    demo_triangle()


if __name__ == "__main__":
    main()
