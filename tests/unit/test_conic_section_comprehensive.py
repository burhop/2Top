"""
Unit tests for conic section functionality - Comprehensive coverage
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


class TestConicSection(unittest.TestCase):
    """Test the conic section functionality comprehensively"""

    def setUp(self):
        """Set up test fixtures"""
        x, y = sp.symbols('x y')

    def test_circle_conic(self):
        """Test circle conic section"""
        x, y = sp.symbols('x y')
        # Circle: x^2 + y^2 - 4 = 0 (radius 2)
        expression = x**2 + y**2 - 4
        circle = ConicSection(expression, (x, y))
        
        # Test conic type detection
        self.assertEqual(circle.conic_type(), "circle")
        
        # Test points on circle
        self.assertTrue(circle.on_curve(2, 0))
        self.assertTrue(circle.on_curve(0, 2))
        self.assertTrue(circle.on_curve(-2, 0))
        self.assertTrue(circle.on_curve(0, -2))
        
        # Test points inside circle
        self.assertFalse(circle.on_curve(1, 1))
        
        # Test points outside circle
        self.assertFalse(circle.on_curve(3, 0))
        
        # Test evaluation
        self.assertEqual(circle.evaluate(2, 0), 0)
        self.assertEqual(circle.evaluate(0, 2), 0)
        self.assertEqual(circle.evaluate(1, 1), -2)  # Inside circle

    def test_ellipse_conic(self):
        """Test ellipse conic section"""
        x, y = sp.symbols('x y')
        # Ellipse: (x/3)^2 + (y/2)^2 - 1 = 0 (a=3, b=2)
        expression = (x/3)**2 + (y/2)**2 - 1
        ellipse = ConicSection(expression, (x, y))
        
        # Test conic type detection
        self.assertEqual(ellipse.conic_type(), "ellipse")
        
        # Test points on ellipse
        self.assertTrue(ellipse.on_curve(3, 0))
        self.assertTrue(ellipse.on_curve(0, 2))
        self.assertTrue(ellipse.on_curve(-3, 0))
        self.assertTrue(ellipse.on_curve(0, -2))
        
        # Test points inside ellipse
        self.assertFalse(ellipse.on_curve(1, 1))
        
        # Test points outside ellipse
        self.assertFalse(ellipse.on_curve(4, 0))
        
        # Test evaluation
        self.assertEqual(ellipse.evaluate(3, 0), 0)
        self.assertEqual(ellipse.evaluate(0, 2), 0)
        self.assertEqual(ellipse.evaluate(1, 1), -0.6388888888888888)  # Inside ellipse

    def test_parabola_conic(self):
        """Test parabola conic section"""
        x, y = sp.symbols('x y')
        # Parabola: y - x^2 = 0 (opens upward)
        expression = y - x**2
        parabola = ConicSection(expression, (x, y))
        
        # Test conic type detection
        self.assertEqual(parabola.conic_type(), "parabola")
        
        # Test points on parabola
        self.assertTrue(parabola.on_curve(0, 0))
        self.assertTrue(parabola.on_curve(1, 1))
        self.assertTrue(parabola.on_curve(-1, 1))
        
        # Test points not on parabola
        self.assertFalse(parabola.on_curve(1, 0))
        self.assertFalse(parabola.on_curve(0, 1))
        
        # Test evaluation
        self.assertEqual(parabola.evaluate(0, 0), 0)
        self.assertEqual(parabola.evaluate(1, 1), 0)
        self.assertEqual(parabola.evaluate(2, 4), 0)

    def test_hyperbola_conic(self):
        """Test hyperbola conic section"""
        x, y = sp.symbols('x y')
        # Hyperbola: x^2 - y^2 - 1 = 0
        expression = x**2 - y**2 - 1
        hyperbola = ConicSection(expression, (x, y))
        
        # Test conic type detection
        self.assertEqual(hyperbola.conic_type(), "hyperbola")
        
        # Test points on hyperbola
        self.assertTrue(hyperbola.on_curve(1, 0))
        self.assertTrue(hyperbola.on_curve(-1, 0))
        
        # Test points not on hyperbola
        self.assertFalse(hyperbola.on_curve(0, 0))
        self.assertFalse(hyperbola.on_curve(0, 1))
        
        # Test evaluation
        self.assertEqual(hyperbola.evaluate(1, 0), 0)
        self.assertEqual(hyperbola.evaluate(-1, 0), 0)
        self.assertEqual(hyperbola.evaluate(0, 1), -2)  # Outside hyperbola

    def test_conic_coefficient_extraction(self):
        """Test coefficient extraction from conic expressions"""
        x, y = sp.symbols('x y')
        
        # Circle: x^2 + y^2 - 4 = 0
        expression = x**2 + y**2 - 4
        circle = ConicSection(expression, (x, y))
        
        coeffs = circle._extract_coefficients()
        self.assertEqual(coeffs['A'], 1.0)
        self.assertEqual(coeffs['B'], 0.0)
        self.assertEqual(coeffs['C'], 1.0)
        self.assertEqual(coeffs['D'], 0.0)
        self.assertEqual(coeffs['E'], 0.0)
        self.assertEqual(coeffs['F'], -4.0)

    def test_conic_degree(self):
        """Test conic degree method"""
        x, y = sp.symbols('x y')
        
        # Various conic sections
        expressions = [
            x**2 + y**2 - 4,      # Circle
            (x/3)**2 + (y/2)**2 - 1,  # Ellipse
            y - x**2,             # Parabola
            x**2 - y**2 - 1       # Hyperbola
        ]
        
        for expr in expressions:
            conic = ConicSection(expr, (x, y))
            self.assertEqual(conic.degree(), 2)

    def test_conic_types_from_equations(self):
        """Test that different conic equations are correctly classified"""
        x, y = sp.symbols('x y')
        
        # Circle: x^2 + y^2 = 4
        circle_expr = x**2 + y**2 - 4
        circle = ConicSection(circle_expr, (x, y))
        self.assertEqual(circle.conic_type(), "circle")
        
        # Ellipse: x^2/9 + y^2/4 = 1
        ellipse_expr = x**2/9 + y**2/4 - 1
        ellipse = ConicSection(ellipse_expr, (x, y))
        self.assertEqual(ellipse.conic_type(), "ellipse")
        
        # Parabola: y = x^2
        parabola_expr = y - x**2
        parabola = ConicSection(parabola_expr, (x, y))
        self.assertEqual(parabola.conic_type(), "parabola")
        
        # Hyperbola: x^2 - y^2 = 1
        hyperbola_expr = x**2 - y**2 - 1
        hyperbola = ConicSection(hyperbola_expr, (x, y))
        self.assertEqual(hyperbola.conic_type(), "hyperbola")

    def test_conic_bounding_box(self):
        """Test bounding box calculation for different conic types"""
        x, y = sp.symbols('x y')
        
        # Circle: x^2 + y^2 = 4
        circle_expr = x**2 + y**2 - 4
        circle = ConicSection(circle_expr, (x, y))
        bbox = circle.bounding_box()
        
        # Should be approximately [-2, 2, -2, 2]
        self.assertAlmostEqual(bbox[0], -2.0, places=1)
        self.assertAlmostEqual(bbox[1], 2.0, places=1)
        self.assertAlmostEqual(bbox[2], -2.0, places=1)
        self.assertAlmostEqual(bbox[3], 2.0, places=1)
        
        # Ellipse: x^2/9 + y^2/4 = 1
        ellipse_expr = x**2/9 + y**2/4 - 1
        ellipse = ConicSection(ellipse_expr, (x, y))
        bbox = ellipse.bounding_box()
        
        # Should be approximately [-3, 3, -2, 2]
        self.assertAlmostEqual(bbox[0], -3.0, places=1)
        self.assertAlmostEqual(bbox[1], 3.0, places=1)
        self.assertAlmostEqual(bbox[2], -2.0, places=1)
        self.assertAlmostEqual(bbox[3], 2.0, places=1)


if __name__ == "__main__":
    unittest.main()