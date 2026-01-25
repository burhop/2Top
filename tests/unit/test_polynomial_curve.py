"""
Unit tests for polynomial curve functionality
"""

import sys
import os
import unittest
import sympy as sp

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.polynomial_curve import PolynomialCurve


class TestPolynomialCurve(unittest.TestCase):
    """Test the polynomial curve functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a quadratic curve: x^2 + y^2 - 1 = 0 (circle)
        x, y = sp.symbols('x y')
        self.curve = PolynomialCurve(x**2 + y**2 - 1, variables=(x, y))

    def test_polynomial_initialization(self):
        """Test that the polynomial curve initializes correctly"""
        x, y = sp.symbols('x y')
        self.assertEqual(self.curve.variables, (x, y))
        self.assertEqual(self.curve.degree(), 2)

    def test_polynomial_evaluation(self):
        """Test polynomial evaluation at various points"""
        # Evaluate at origin (should be -1 for unit circle)
        result = self.curve.evaluate(0, 0)
        self.assertEqual(result, -1)
        
        # Evaluate at point on circle (should be 0)
        result = self.curve.evaluate(1, 0)
        self.assertEqual(result, 0)
        
        # Evaluate at point outside circle (should be positive)
        result = self.curve.evaluate(2, 0)
        self.assertEqual(result, 3)

    def test_polynomial_derivative(self):
        """Test gradient calculation"""
        # Gradient of x^2 + y^2 - 1 is (2x, 2y)
        gx, gy = self.curve.gradient(1, 0)
        self.assertEqual(gx, 2)
        self.assertEqual(gy, 0)

    def test_polynomial_properties(self):
        """Test polynomial properties"""
        x, y = sp.symbols('x y')
        self.assertEqual(self.curve.variables, (x, y))
        self.assertEqual(self.curve.degree(), 2)
        
        # Test that it has required methods
        self.assertTrue(hasattr(self.curve, 'evaluate'))
        self.assertTrue(hasattr(self.curve, 'gradient'))
        self.assertTrue(hasattr(self.curve, 'degree'))
        self.assertTrue(hasattr(self.curve, 'on_curve'))


if __name__ == "__main__":
    unittest.main()