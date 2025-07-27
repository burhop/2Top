#!/usr/bin/env python3
"""Debug script for tolerance handling test"""

import sympy as sp
import numpy as np
from geometry import ConicSection, TrimmedImplicitCurve

def debug_tolerance_handling():
    """Debug the tolerance handling test case"""
    print("Debugging tolerance handling test...")
    
    # Set up the same test case as the failing test
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    right_half = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    
    # Test the problematic point
    test_x, test_y = -1e-10, 1.0
    
    print(f"Testing point ({test_x}, {test_y})")
    
    # Check base curve evaluation
    curve_value = circle.evaluate(test_x, test_y)
    print(f"Curve evaluation: {curve_value}")
    print(f"Absolute value: {abs(curve_value)}")
    
    # Check mask condition
    mask_result = right_half.mask(test_x, test_y)
    print(f"Mask result (x >= 0): {mask_result}")
    print(f"x = {test_x}, x >= 0 = {test_x >= 0}")
    
    # Check contains result
    contains_result = right_half.contains(test_x, test_y)
    print(f"Contains result: {contains_result}")
    
    # The test expects this to be True, but logically it should be False
    # because x = -1e-10 < 0, so it's not in the right half
    print(f"\nAnalysis:")
    print(f"- Point is very close to (0, 1) which is on the unit circle")
    print(f"- But x = {test_x} < 0, so it should NOT be in right half (x >= 0)")
    print(f"- Test expects True, but logically should be False")
    
    # Test the corresponding positive point
    test_x_pos = 1e-10
    print(f"\nTesting positive counterpart ({test_x_pos}, {test_y})")
    curve_value_pos = circle.evaluate(test_x_pos, test_y)
    mask_result_pos = right_half.mask(test_x_pos, test_y)
    contains_result_pos = right_half.contains(test_x_pos, test_y)
    
    print(f"Curve evaluation: {curve_value_pos}")
    print(f"Mask result: {mask_result_pos}")
    print(f"Contains result: {contains_result_pos}")

if __name__ == "__main__":
    debug_tolerance_handling()
