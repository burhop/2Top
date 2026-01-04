"""
Unit tests for polynomial curve functionality
"""

import sys
import os
import unittest

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.polynomial_curve import PolynomialCurve


class TestPolynomialCurve(unittest.TestCase):
    """Test the polynomial curve functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a quadratic curve: y = x^2
        self.curve = PolynomialCurve([0, 0, 1], "Quadratic")  # Coefficients for x^2

    def test_polynomial_initialization(self):
        """Test that the polynomial curve initializes correctly"""
        self.assertEqual(self.curve.coefficients, [0, 0, 1])
        self.assertEqual(self.curve.name, "Quadratic")
        self.assertEqual(self.curve.degree, 2)

    def test_polynomial_evaluation(self):
        """Test polynomial evaluation at various points"""
        # Evaluate at x = 0
        self.assertEqual(self.curve.evaluate(0), 0)
        
        # Evaluate at x = 1
        self.assertEqual(self.curve.evaluate(1), 1)
        
        # Evaluate at x = 2
        self.assertEqual(self.curve.evaluate(2), 4)
        
        # Evaluate at x = -1
        self.assertEqual(self.curve.evaluate(-1), 1)

    def test_polynomial_derivative(self):
        """Test derivative calculation"""
        # Derivative of x^2 is 2x
        derivative = self.curve.derivative()
        self.assertEqual(derivative.coefficients, [0, 2])  # Coefficients for 2x
        self.assertEqual(derivative.degree, 1)

    def test_polynomial_integral(self):
        """Test integral calculation"""
        # Integral of x^2 is (1/3)x^3
        integral = self.curve.integral()
        self.assertEqual(integral.coefficients, [0, 0, 0, 1/3])  # Coefficients for (1/3)x^3
        self.assertEqual(integral.degree, 3)

    def test_polynomial_properties(self):
        """Test polynomial properties"""
        self.assertEqual(self.curve.name, "Quadratic")
        self.assertEqual(self.curve.degree, 2)
        self.assertEqual(self.curve.dimension, 1)  # 1D curve


if __name__ == "__main__":
    unittest.main()