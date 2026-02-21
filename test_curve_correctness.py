#!/usr/bin/env python3
"""
Systematic testing of implicit curve evaluators for correctness
"""

import sympy as sp
import numpy as np
from geometry import *

def test_curve_correctness():
    """Test each curve type for mathematical correctness"""
    
    x, y = sp.symbols('x y')
    
    print("🔍 IMPLICIT CURVE CORRECTNESS TESTING")
    print("=" * 50)
    
    # 1. ConicSection Tests
    print("\n1. 🔵 ConicSection Tests:")
    
    # Unit circle: x² + y² - 1 = 0
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    test_points = [
        ((0, 0), -1, "center (inside)"),
        ((1, 0), 0, "on circle"),
        ((0, 1), 0, "on circle"),
        ((2, 0), 3, "outside"),
        ((-1, 0), 0, "on circle"),
    ]
    
    for (px, py), expected, desc in test_points:
        result = circle.evaluate(px, py)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Circle at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # Ellipse: x²/4 + y² - 1 = 0
    ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
    ellipse_tests = [
        ((0, 0), -1, "center"),
        ((2, 0), 0, "on ellipse (x-axis)"),
        ((0, 1), 0, "on ellipse (y-axis)"),
        ((1, 0), -0.75, "inside"),
    ]
    
    for (px, py), expected, desc in ellipse_tests:
        result = ellipse.evaluate(px, py)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Ellipse at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # 2. PolynomialCurve Tests
    print("\n2. 📐 PolynomialCurve Tests:")
    
    # Line: x + y - 1 = 0
    line = PolynomialCurve(x + y - 1, (x, y))
    line_tests = [
        ((0, 0), -1, "below line"),
        ((1, 0), 0, "on line"),
        ((0, 1), 0, "on line"),
        ((1, 1), 1, "above line"),
        ((0.5, 0.5), 0, "on line"),
    ]
    
    for (px, py), expected, desc in line_tests:
        result = line.evaluate(px, py)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Line at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # Parabola: y - x² = 0
    parabola = PolynomialCurve(y - x**2, (x, y))
    parabola_tests = [
        ((0, 0), 0, "vertex"),
        ((1, 1), 0, "on parabola"),
        ((2, 4), 0, "on parabola"),
        ((1, 0), -1, "below parabola"),
        ((1, 2), 1, "above parabola"),
    ]
    
    for (px, py), expected, desc in parabola_tests:
        result = parabola.evaluate(px, py)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Parabola at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # 3. Superellipse Tests
    print("\n3. ⭐ Superellipse Tests:")
    
    # Circle-like (n=2): |x/a|² + |y/b|² = 1
    super_circle = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
    super_tests = [
        ((0, 0), -1, "center"),
        ((1, 0), 0, "on curve (x-axis)"),
        ((0, 1), 0, "on curve (y-axis)"),
        ((0.5, 0.5), None, "inside (calculate)"),  # Will calculate expected
    ]
    
    for (px, py), expected, desc in super_tests:
        result = super_circle.evaluate(px, py)
        if expected is None:
            # For superellipse: |x/a|^n + |y/b|^n - 1
            expected_calc = abs(px/1.0)**2.0 + abs(py/1.0)**2.0 - 1
            expected = expected_calc
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Superellipse at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # Square-like (n=∞ approximation with n=10)
    super_square = Superellipse(a=1.0, b=1.0, n=10.0, variables=(x, y))
    square_tests = [
        ((0, 0), None, "center"),
        ((0.5, 0.5), None, "inside"),
        ((1, 0), 0, "on boundary"),
    ]
    
    for (px, py), expected, desc in square_tests:
        result = super_square.evaluate(px, py)
        if expected is None:
            expected_calc = abs(px/1.0)**10.0 + abs(py/1.0)**10.0 - 1
            expected = expected_calc
        status = "✅" if abs(result - expected) < 1e-6 else "❌"  # Looser tolerance for high powers
        print(f"  {status} Super-square at ({px},{py}): {result:.6f} (expected {expected:.6f}) - {desc}")
    
    # 4. ProceduralCurve Tests
    print("\n4. 🔧 ProceduralCurve Tests:")
    
    # Custom circle function
    def circle_func(x_val, y_val):
        return x_val**2 + y_val**2 - 1
    
    proc_circle = ProceduralCurve(circle_func, variables=(x, y))
    proc_tests = [
        ((0, 0), -1, "center"),
        ((1, 0), 0, "on circle"),
        ((2, 0), 3, "outside"),
    ]
    
    for (px, py), expected, desc in proc_tests:
        result = proc_circle.evaluate(px, py)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Procedural at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # 5. RFunctionCurve Tests (Constructive Geometry)
    print("\n5. 🔗 RFunctionCurve Tests:")
    
    circle1 = ConicSection(x**2 + y**2 - 1, (x, y))
    circle2 = ConicSection((x-1)**2 + y**2 - 1, (x, y))
    
    # Union (min operation)
    union_curve = union(circle1, circle2)
    union_tests = [
        ((0, 0), -1, "inside both"),
        ((0.5, 0), None, "between circles"),  # Will calculate
        ((2, 0), 0, "on second circle"),
    ]
    
    for (px, py), expected, desc in union_tests:
        result = union_curve.evaluate(px, py)
        if expected is None:
            # Union is min of the two
            val1 = circle1.evaluate(px, py)
            val2 = circle2.evaluate(px, py)
            expected = min(val1, val2)
        status = "✅" if abs(result - expected) < 1e-10 else "❌"
        print(f"  {status} Union at ({px},{py}): {result} (expected {expected}) - {desc}")
    
    # 6. Vectorized Operations Test
    print("\n6. 📊 Vectorized Operations Test:")
    
    # Test with arrays
    x_vals = np.array([0, 1, 2])
    y_vals = np.array([0, 0, 0])
    
    circle_results = circle.evaluate(x_vals, y_vals)
    expected_results = np.array([-1, 0, 3])
    
    vectorized_ok = np.allclose(circle_results, expected_results)
    status = "✅" if vectorized_ok else "❌"
    print(f"  {status} Vectorized circle: {circle_results} (expected {expected_results})")
    
    # 7. Gradient Tests
    print("\n7. 📈 Gradient Tests:")
    
    # Circle gradient at (1, 0) should be (2, 0)
    gx, gy = circle.gradient(1, 0)
    grad_ok = abs(gx - 2) < 1e-10 and abs(gy - 0) < 1e-10
    status = "✅" if grad_ok else "❌"
    print(f"  {status} Circle gradient at (1,0): ({gx}, {gy}) (expected (2, 0))")
    
    # Line gradient should be constant (1, 1)
    gx, gy = line.gradient(0, 0)
    grad_ok = abs(gx - 1) < 1e-10 and abs(gy - 1) < 1e-10
    status = "✅" if grad_ok else "❌"
    print(f"  {status} Line gradient at (0,0): ({gx}, {gy}) (expected (1, 1))")
    
    print("\n🎯 Testing complete! Look for ❌ marks to identify issues.")

if __name__ == "__main__":
    test_curve_correctness()