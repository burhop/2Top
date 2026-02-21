"""
Unit tests for implicit curve functionality
"""

import sys
import os
import unittest
import sympy as sp

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.implicit_curve import ImplicitCurve


class TestImplicitCurve(unittest.TestCase):
    """Test the implicit curve functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a simple implicit curve: x^2 + y^2 - 1 = 0 (circle)
        x, y = sp.symbols('x y')
        expression = x**2 + y**2 - 1
        self.curve = ImplicitCurve(expression, (x, y))

    def test_curve_initialization(self):
        """Test that the curve initializes correctly"""
        self.assertEqual(str(self.curve), "x**2 + y**2 - 1 = 0")
        self.assertIsNotNone(self.curve.expression)
        self.assertEqual(self.curve.variables, (sp.Symbol('x'), sp.Symbol('y')))

    def test_curve_evaluation(self):
        """Test curve evaluation at various points"""
        # Point on the circle
        self.assertEqual(self.curve.evaluate(1, 0), 0)
        self.assertEqual(self.curve.evaluate(0, 1), 0)
        self.assertEqual(self.curve.evaluate(-1, 0), 0)
        self.assertEqual(self.curve.evaluate(0, -1), 0)
        
        # Point inside the circle
        self.assertLess(self.curve.evaluate(0.5, 0.5), 0)
        
        # Point outside the circle
        self.assertGreater(self.curve.evaluate(2, 0), 0)

    def test_curve_properties(self):
        """Test curve properties"""
        self.assertEqual(str(self.curve), "x**2 + y**2 - 1 = 0")


if __name__ == "__main__":
    unittest.main()