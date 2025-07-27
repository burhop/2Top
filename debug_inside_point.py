#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve

def debug_inside_point():
    """Debug the inside point (0.5, 0.5) test case"""
    print("=== Debugging Inside Point Test Case ===")
    
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
    
    # Test point that should be inside circle but not on boundary
    test_x, test_y = 0.5, 0.5
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Expected: point should be inside circle but not on boundary, so should return False")
    
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
    
    # Check ray-casting result
    inside_region = composite_curve._point_in_polygon_scalar(test_x, test_y)
    print(f"Ray-casting algorithm result (inside region): {inside_region}")
    
    # Check composite curve
    print(f"Composite curve contains point: {composite_curve.contains(test_x, test_y)}")
    
    print(f"\n=== Analysis ===")
    print(f"Point ({test_x}, {test_y}) is inside the unit circle: {test_x**2 + test_y**2 < 1}")
    print(f"Point is in first quadrant: {test_x >= 0 and test_y >= 0}")
    print(f"Distance from origin: {np.sqrt(test_x**2 + test_y**2):.3f}")
    print(f"Circle evaluation: {circle.evaluate(test_x, test_y)}")
    
    print(f"\nFor a closed composite curve representing a circle boundary:")
    print(f"- Points INSIDE the circle should return False (not contained)")
    print(f"- Points ON the boundary should return True (contained)")
    print(f"- Points OUTSIDE the circle should return False (not contained)")

if __name__ == "__main__":
    debug_inside_point()
