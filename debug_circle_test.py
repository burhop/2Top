#!/usr/bin/env python3

import sympy as sp
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve
from geometry.area_region import AreaRegion
from geometry.composite_curve import create_square_from_edges

def test_circle_hole():
    """Debug test for circular hole detection."""
    
    # Create outer boundary (4x4 square)
    outer = create_square_from_edges((-2, -2), (2, 2))
    print(f"Outer boundary segments: {len(outer.segments)}")
    print(f"Outer boundary is_closed: {outer.is_closed()}")
    
    # Create circular hole (radius 1, centered at origin)
    x, y = sp.symbols('x y')
    circle_expr = x**2 + y**2 - 1
    circle = ConicSection(circle_expr)
    print(f"Circle conic type: {circle.conic_type()}")
    
    # Create a composite curve from the circle (as a single segment)
    circle_trimmed = TrimmedImplicitCurve(circle, lambda x, y: True)  # Full circle
    circle_composite = CompositeCurve([circle_trimmed])
    print(f"Circle composite segments: {len(circle_composite.segments)}")
    print(f"Circle composite is_closed: {circle_composite.is_closed()}")
    
    # Test the circle directly
    print(f"\nDirect circle tests:")
    print(f"Circle.evaluate(0, 0) = {circle.evaluate(0, 0)}")  # Should be -1 (inside)
    print(f"Circle.evaluate(1.5, 0) = {circle.evaluate(1.5, 0)}")  # Should be positive (outside)
    
    # Test the trimmed circle
    print(f"\nTrimmed circle tests:")
    print(f"TrimmedCircle.contains(0, 0) = {circle_trimmed.contains(0, 0)}")  # Should be True (inside)
    print(f"TrimmedCircle.contains(1.5, 0) = {circle_trimmed.contains(1.5, 0)}")  # Should be False (outside)
    
    # Test the composite circle
    print(f"\nComposite circle tests:")
    print(f"CompositeCircle.contains(0, 0) = {circle_composite.contains(0, 0)}")
    print(f"CompositeCircle.contains(1.5, 0) = {circle_composite.contains(1.5, 0)}")
    
    # Create the region and test
    region = AreaRegion(outer, [circle_composite])
    print(f"\nAreaRegion tests:")
    print(f"Region.contains(0, 0) = {region.contains(0, 0)}")  # Should be False (in hole)
    print(f"Region.contains(1.5, 0) = {region.contains(1.5, 0)}")  # Should be True (in region, not in hole)
    
    # Test the _point_in_curve method directly
    print(f"\nDirect _point_in_curve tests:")
    print(f"_point_in_curve(0, 0, circle_composite) = {region._point_in_curve(0, 0, circle_composite)}")
    print(f"_point_in_curve(1.5, 0, circle_composite) = {region._point_in_curve(1.5, 0, circle_composite)}")

if __name__ == "__main__":
    test_circle_hole()
