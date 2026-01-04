"""
Unit tests for conic section functionality
"""

import sys
import os
import unittest

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.conic_section import ConicSection


class TestConicSection(unittest.TestCase):
    """Test the conic section functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create an ellipse: (x/2)^2 + (y/3)^2 = 1
        self.ellipse = ConicSection(
            a=2, b=3, center=(0, 0), rotation=0, 
            equation="(x/2)^2 + (y/3)^2 = 1"
        )

    def test_conic_initialization(self):
        """Test that the conic section initializes correctly"""
        self.assertEqual(self.ellipse.a, 2)
        self.assertEqual(self.ellipse.b, 3)
        self.assertEqual(self.ellipse.center, (0, 0))
        self.assertEqual(self.ellipse.rotation, 0)
        self.assertEqual(self.ellipse.equation, "(x/2)^2 + (y/3)^2 = 1")

    def test_conic_properties(self):
        """Test conic section properties"""
        # Test focal distance
        c = (self.ellipse.a**2 - self.ellipse.b**2)**0.5 if self.ellipse.a > self.ellipse.b else (self.ellipse.b**2 - self.ellipse.a**2)**0.5
        self.assertAlmostEqual(self.ellipse.focal_distance, c, places=10)
        
        # Test eccentricity
        if self.ellipse.a > self.ellipse.b:
            e = c / self.ellipse.a
        else:
            e = c / self.ellipse.b
        self.assertAlmostEqual(self.ellipse.eccentricity, e, places=10)

    def test_conic_points(self):
        """Test point evaluation on conic section"""
        # Point on the ellipse
        self.assertAlmostEqual(self.ellipse.evaluate(2, 0), 1.0, places=10)
        self.assertAlmostEqual(self.ellipse.evaluate(0, 3), 1.0, places=10)
        self.assertAlmostEqual(self.ellipse.evaluate(-2, 0), 1.0, places=10)
        self.assertAlmostEqual(self.ellipse.evaluate(0, -3), 1.0, places=10)
        
        # Point inside the ellipse
        self.assertLess(self.ellipse.evaluate(1, 1), 1.0)
        
        # Point outside the ellipse
        self.assertGreater(self.ellipse.evaluate(3, 0), 1.0)

    def test_conic_is_valid_point(self):
        """Test checking if a point is on the conic section"""
        # Points on the ellipse
        self.assertTrue(self.ellipse.is_valid_point(2, 0))
        self.assertTrue(self.ellipse.is_valid_point(0, 3))
        self.assertTrue(self.ellipse.is_valid_point(-2, 0))
        self.assertTrue(self.ellipse.is_valid_point(0, -3))
        
        # Points not on the ellipse
        self.assertFalse(self.ellipse.is_valid_point(1, 1))
        self.assertFalse(self.ellipse.is_valid_point(3, 0))


if __name__ == "__main__":
    unittest.main()