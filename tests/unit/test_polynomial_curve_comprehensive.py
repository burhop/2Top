"""
Unit tests for polynomial curve functionality - Comprehensive coverage
"""

import sys
import os
import unittest
import numpy as np
import sympy as sp

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.polynomial_curve import PolynomialCurve


class TestPolynomialCurve(unittest.TestCase):
    """Test the polynomial curve functionality comprehensively"""

    def test_quadratic_curve(self):
        """Test quadratic curve: x^2 + y^2 - 1 = 0"""
        x, y = sp.symbols('x y')
        expr = x**2 + y**2 - 1  # Unit circle
        curve = PolynomialCurve(expr, variables=(x, y))
        
        # Test curve properties
        self.assertEqual(curve.degree(), 2)
        self.assertEqual(curve.variables, (x, y))
        
        # Test evaluation
        self.assertEqual(curve.evaluate(0, 0), -1)  # Inside circle
        self.assertEqual(curve.evaluate(1, 0), 0)   # On circle
        self.assertEqual(curve.evaluate(2, 0), 3)   # Outside circle
        
        # Test gradient
        gx, gy = curve.gradient(1, 0)
        self.assertEqual(gx, 2)  # 2x at (1,0)
        self.assertEqual(gy, 0)  # 2y at (1,0)

    def test_linear_curve(self):
        """Test linear curve: 2x + 3y - 1 = 0"""
        x, y = sp.symbols('x y')
        expr = 2*x + 3*y - 1  # Line
        curve = PolynomialCurve(expr, variables=(x, y))
        
        # Test curve properties
        self.assertEqual(curve.degree(), 1)
        self.assertEqual(curve.variables, (x, y))
        
        # Test curve properties
        self.assertEqual(curve.degree(), 1)
        self.assertEqual(curve.variables, (x, y))
        
        # Test evaluation
        self.assertEqual(curve.evaluate(0, 0), -1)  # 2*0 + 3*0 - 1 = -1
        self.assertEqual(curve.evaluate(1, 0), 1)   # 2*1 + 3*0 - 1 = 1
        self.assertEqual(curve.evaluate(0, 1), 2)   # 2*0 + 3*1 - 1 = 2
        
        # Test gradient
        gx, gy = curve.gradient(0, 0)
        self.assertEqual(gx, 2)  # Coefficient of x
        self.assertEqual(gy, 3)  # Coefficient of y

    def test_cubic_curve(self):
        """Test cubic curve: x^3 + y^3 - 1 = 0"""
        x, y = sp.symbols('x y')
        expr = x**3 + y**3 - 1
        curve = PolynomialCurve(expr, variables=(x, y))
        
        # Test curve properties
        self.assertEqual(curve.degree(), 3)
        self.assertEqual(curve.variables, (x, y))
        
        # Test evaluation
        self.assertEqual(curve.evaluate(0, 0), -1)  # 0^3 + 0^3 - 1 = -1
        self.assertEqual(curve.evaluate(1, 0), 0)   # 1^3 + 0^3 - 1 = 0
        self.assertEqual(curve.evaluate(0, 1), 0)   # 0^3 + 1^3 - 1 = 0
        
        # Test gradient
        gx, gy = curve.gradient(1, 0)
        self.assertEqual(gx, 3)  # 3x^2 at (1,0)
        self.assertEqual(gy, 0)  # 3y^2 at (1,0)

    def test_constant_curve(self):
        """Test constant curve: 5 = 0"""
        x, y = sp.symbols('x y')
        expr = sp.sympify(5)  # Constant
        curve = PolynomialCurve(expr, variables=(x, y))
        
        # Test curve properties
        self.assertEqual(curve.degree(), 0)
        self.assertEqual(curve.variables, (x, y))
        
        # Test evaluation (constant everywhere)
        self.assertEqual(curve.evaluate(0, 0), 5)
        self.assertEqual(curve.evaluate(1, 1), 5)
        self.assertEqual(curve.evaluate(100, -50), 5)
        
        # Test gradient (should be zero everywhere)
        gx, gy = curve.gradient(0, 0)
        self.assertEqual(gx, 0)
        self.assertEqual(gy, 0)

    def test_polynomial_coefficients(self):
        """Test polynomial coefficient handling"""
        x, y = sp.symbols('x y')
        
        # Test mixed degree polynomial
        expr1 = 1 + 2*x + 3*y + x*y + x**2  # Mixed terms
        curve1 = PolynomialCurve(expr1, variables=(x, y))
        self.assertEqual(curve1.degree(), 2)
        
        # Test higher degree
        expr2 = x**4 + y**4 + x**2*y**2  # Degree 4
        curve2 = PolynomialCurve(expr2, variables=(x, y))
        self.assertEqual(curve2.degree(), 4)

    def test_polynomial_operations(self):
        """Test polynomial operations and evaluation"""
        x, y = sp.symbols('x y')
        
        # Create two simple polynomials
        f_expr = x + 1  # Line
        g_expr = y - 1  # Line
        
        f = PolynomialCurve(f_expr, variables=(x, y))
        g = PolynomialCurve(g_expr, variables=(x, y))
        
        # Test evaluation
        self.assertEqual(f.evaluate(0, 0), 1)   # 0 + 1 = 1
        self.assertEqual(f.evaluate(1, 0), 2)   # 1 + 1 = 2
        self.assertEqual(g.evaluate(0, 0), -1)  # 0 - 1 = -1
        self.assertEqual(g.evaluate(0, 1), 0)   # 1 - 1 = 0

    def test_polynomial_properties(self):
        """Test polynomial properties and methods"""
        x, y = sp.symbols('x y')
        expr = 2 - 3*x + x**2 + y**2  # Mixed quadratic
        curve = PolynomialCurve(expr, variables=(x, y))
        
        # Test degree
        self.assertEqual(curve.degree(), 2)
        
        # Test variables
        self.assertEqual(curve.variables, (x, y))
        
        # Test that it has required methods
        self.assertTrue(hasattr(curve, 'evaluate'))
        self.assertTrue(hasattr(curve, 'gradient'))
        self.assertTrue(hasattr(curve, 'degree'))
        self.assertTrue(hasattr(curve, 'variables'))


if __name__ == "__main__":
    unittest.main()