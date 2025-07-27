#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve

def debug_overlapping_segments():
    """Debug the overlapping segments test case"""
    print("=== Debugging Overlapping Segments Test Case ===")
    
    # Recreate the test case
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    
    # Create overlapping segments
    segment1 = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)  # Right half
    segment2 = TrimmedImplicitCurve(circle, lambda x, y: y >= 0)  # Upper half
    
    overlapping_composite = CompositeCurve([segment1, segment2])
    
    # Test point that should be on both segments
    test_x, test_y = 0.707, 0.707
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Expected: point should be on circle boundary in first quadrant")
    
    # Check if composite curve is closed
    print(f"Composite curve is_closed(): {overlapping_composite.is_closed()}")
    
    # Check individual segments
    print(f"Segment 1 (right half) contains point: {segment1.contains(test_x, test_y)}")
    print(f"Segment 2 (upper half) contains point: {segment2.contains(test_x, test_y)}")
    
    # Check composite curve
    print(f"Composite curve contains point: {overlapping_composite.contains(test_x, test_y)}")
    
    # Debug individual segment checks
    print("\n=== Individual Segment Debug ===")
    
    # Check if point is on circle boundary
    circle_value = circle.evaluate(test_x, test_y)
    print(f"Circle evaluation at test point: {circle_value}")
    print(f"Point is on circle boundary (|f| <= 1e-3): {abs(circle_value) <= 1e-3}")
    
    # Check mask conditions
    mask1_result = segment1.mask(test_x, test_y)
    mask2_result = segment2.mask(test_x, test_y)
    print(f"Segment 1 mask (x >= 0): {mask1_result}")
    print(f"Segment 2 mask (y >= 0): {mask2_result}")
    
    # Check segment contains with different tolerances
    print(f"Segment 1 contains (tol=1e-10): {segment1.contains(test_x, test_y, 1e-10)}")
    print(f"Segment 1 contains (tol=1e-3): {segment1.contains(test_x, test_y, 1e-3)}")
    print(f"Segment 2 contains (tol=1e-10): {segment2.contains(test_x, test_y, 1e-10)}")
    print(f"Segment 2 contains (tol=1e-3): {segment2.contains(test_x, test_y, 1e-3)}")

if __name__ == "__main__":
    debug_overlapping_segments()
