#!/usr/bin/env python3
"""Debug script for TrimmedImplicitCurve contains method"""

import sympy as sp
import numpy as np
from geometry import ConicSection, TrimmedImplicitCurve

def debug_trimmed_curve_contains():
    """Debug the contains method for right half circle"""
    print("Debugging TrimmedImplicitCurve.contains() method...")
    
    # Set up the same test case as the failing test
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    right_half = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    
    # Test the problematic point
    test_x, test_y = 0.707, 0.707
    
    print(f"Testing point ({test_x}, {test_y})")
    
    # Check base curve evaluation
    curve_value = circle.evaluate(test_x, test_y)
    print(f"Curve evaluation: {curve_value}")
    print(f"Absolute value: {abs(curve_value)}")
    
    # Check mask condition
    mask_result = right_half.mask(test_x, test_y)
    print(f"Mask result: {mask_result}")
    
    # Test contains with default tolerance (should be 1e-6 now)
    contains_default = right_half.contains(test_x, test_y)
    print(f"Contains (default): {contains_default}")
    
    # Test contains with explicit tolerance
    contains_1e3 = right_half.contains(test_x, test_y, tolerance=1e-3)
    print(f"Contains (1e-3): {contains_1e3}")
    
    # Check what tolerance is needed
    needed_tolerance = abs(curve_value)
    print(f"Tolerance needed: {needed_tolerance}")
    
    # Test if the issue is with the tolerance comparison
    print(f"\nDebugging tolerance comparison:")
    print(f"abs(curve_value) = {abs(curve_value)}")
    print(f"1e-6 = {1e-6}")
    print(f"abs(curve_value) <= 1e-6: {abs(curve_value) <= 1e-6}")
    print(f"abs(curve_value) <= 1e-3: {abs(curve_value) <= 1e-3}")

if __name__ == "__main__":
    debug_trimmed_curve_contains()
