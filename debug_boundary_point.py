#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve

def debug_boundary_point():
    """Debug the boundary point (1.0, 0.0) test case"""
    print("=== Debugging Boundary Point Test Case ===")
    
    # Recreate the test case
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    
    # Create quarter-circle segments
    segments = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
    ]
    
    composite_curve = CompositeCurve(segments)
    
    # Test point that should be on boundary between first and fourth quadrants
    test_x, test_y = 1.0, 0.0
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Expected: point should be on circle boundary between first and fourth quadrants")
    
    # Check if composite curve is closed
    print(f"Composite curve is_closed(): {composite_curve.is_closed()}")
    
    # Check individual segments
    for i, segment in enumerate(segments):
        quadrant_name = ["First", "Second", "Third", "Fourth"][i]
        contains_result = segment.contains(test_x, test_y)
        print(f"Segment {i+1} ({quadrant_name} quadrant) contains point: {contains_result}")
        
        # Check mask condition for this segment
        mask_result = segment.mask(test_x, test_y)
        print(f"  Mask condition: {mask_result}")
        
        # Check if point is on circle boundary
        circle_value = circle.evaluate(test_x, test_y)
        print(f"  Circle evaluation: {circle_value}")
        print(f"  On boundary (|f| <= 1e-3): {abs(circle_value) <= 1e-3}")
    
    # Check composite curve
    print(f"Composite curve contains point: {composite_curve.contains(test_x, test_y)}")
    
    # Test with different tolerance
    print(f"Composite curve contains point (tol=1e-10): {composite_curve.contains(test_x, test_y, 1e-10)}")
    
    print("\n=== Mask Condition Details ===")
    print("First quadrant mask (x >= 0 and y >= 0):")
    print(f"  x >= 0: {test_x >= 0}")
    print(f"  y >= 0: {test_y >= 0}")
    print(f"  Combined: {test_x >= 0 and test_y >= 0}")
    
    print("Fourth quadrant mask (x >= 0 and y <= 0):")
    print(f"  x >= 0: {test_x >= 0}")
    print(f"  y <= 0: {test_y <= 0}")
    print(f"  Combined: {test_x >= 0 and test_y <= 0}")

if __name__ == "__main__":
    debug_boundary_point()
