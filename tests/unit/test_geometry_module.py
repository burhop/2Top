"""
Unit tests for implicit curve functionality
"""

import sys
import os
import unittest
import sympy as sp
import numpy as np

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve


class TestImplicitCurve(unittest.TestCase):
    """Test the implicit curve functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a simple implicit curve: x^2 + y^2 - 1 = 0 (circle)
        x, y = sp.symbols('x y')
        expression = x**2 + y**2 - 1
        self.curve = ConicSection(expression, (x, y))

    def test_curve_initialization(self):
        """Test that the curve initializes correctly"""
        # Check that it's a ConicSection instance
        self.assertIsInstance(self.curve, ConicSection)
        self.assertIsInstance(self.curve, ImplicitCurve)

        # Test evaluation
        self.assertEqual(self.curve.evaluate(0, 0), -1)  # Point inside circle
        self.assertEqual(self.curve.evaluate(1, 0), 0)   # Point on circle

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

    def test_curve_is_valid_point(self):
        """Test checking if a point is on the curve"""
        # Points on the curve
        self.assertTrue(self.curve.on_curve(1, 0))
        self.assertTrue(self.curve.on_curve(0, 1))
        self.assertTrue(self.curve.on_curve(-1, 0))
        self.assertTrue(self.curve.on_curve(0, -1))

        # Points not on the curve
        self.assertFalse(self.curve.on_curve(0.5, 0.5))
        self.assertFalse(self.curve.on_curve(2, 0))

    def test_curve_properties(self):
        """Test curve properties"""
        # Test conic type
        self.assertEqual(self.curve.conic_type(), "circle")
        self.assertEqual(self.curve.degree(), 2)  # 2D curve


class TestConicSection(unittest.TestCase):
    """Test the conic section functionality specifically"""

    def setUp(self):
        """Set up test fixtures"""
        x, y = sp.symbols('x y')
        # Create a circle: x^2 + y^2 - 1 = 0
        self.circle = ConicSection(x**2 + y**2 - 1, (x, y))
        # Create an ellipse: x^2/4 + y^2/9 - 1 = 0
        self.ellipse = ConicSection(x**2/4 + y**2/9 - 1, (x, y))
        # Create a parabola: y - x^2 = 0
        self.parabola = ConicSection(y - x**2, (x, y))

    def test_conic_types(self):
        """Test conic type classification"""
        self.assertEqual(self.circle.conic_type(), "circle")
        self.assertEqual(self.ellipse.conic_type(), "ellipse")
        self.assertEqual(self.parabola.conic_type(), "parabola")

    def test_conic_evaluation(self):
        """Test conic evaluation"""
        # Circle tests
        self.assertEqual(self.circle.evaluate(1, 0), 0)
        self.assertEqual(self.circle.evaluate(0, 1), 0)
        self.assertLess(self.circle.evaluate(0.5, 0.5), 0)
        self.assertGreater(self.circle.evaluate(2, 0), 0)

        # Ellipse tests
        self.assertEqual(self.ellipse.evaluate(2, 0), 0)
        self.assertEqual(self.ellipse.evaluate(0, 3), 0)
        self.assertLess(self.ellipse.evaluate(1, 1), 0)
        self.assertGreater(self.ellipse.evaluate(3, 0), 0)

        # Parabola tests
        self.assertEqual(self.parabola.evaluate(0, 0), 0)
        self.assertEqual(self.parabola.evaluate(1, 1), 0)
        self.assertEqual(self.parabola.evaluate(2, 4), 0)


if __name__ == "__main__":
    unittest.main()