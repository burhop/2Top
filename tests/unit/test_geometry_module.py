"""
Unit tests for implicit curve functionality
"""

import sys
import os
import unittest
import math

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual geometry modules we want to test
from geometry.implicit_curve import ImplicitCurve
from geometry.base_field import BaseField
from geometry.field_strategy import FieldStrategy


class TestImplicitCurve(unittest.TestCase):
    """Test the implicit curve functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a simple implicit curve: x^2 + y^2 - 1 = 0 (circle)
        self.curve = ImplicitCurve(lambda x, y: x**2 + y**2 - 1, "Circle")

    def test_curve_initialization(self):
        """Test that the curve initializes correctly"""
        self.assertEqual(self.curve.name, "Circle")
        self.assertIsNotNone(self.curve.function)
        self.assertEqual(self.curve.function(0, 0), -1)  # Point inside circle
        self.assertEqual(self.curve.function(1, 0), 0)   # Point on circle

    def test_curve_evaluation(self):
        """Test curve evaluation at various points"""
        # Point on the circle
        self.assertEqual(self.curve.function(1, 0), 0)
        self.assertEqual(self.curve.function(0, 1), 0)
        self.assertEqual(self.curve.function(-1, 0), 0)
        self.assertEqual(self.curve.function(0, -1), 0)
        
        # Point inside the circle
        self.assertLess(self.curve.function(0.5, 0.5), 0)
        
        # Point outside the circle
        self.assertGreater(self.curve.function(2, 0), 0)

    def test_curve_is_valid_point(self):
        """Test checking if a point is on the curve"""
        # Points on the curve
        self.assertTrue(self.curve.is_valid_point(1, 0))
        self.assertTrue(self.curve.is_valid_point(0, 1))
        self.assertTrue(self.curve.is_valid_point(-1, 0))
        self.assertTrue(self.curve.is_valid_point(0, -1))
        
        # Points not on the curve
        self.assertFalse(self.curve.is_valid_point(0.5, 0.5))
        self.assertFalse(self.curve.is_valid_point(2, 0))

    def test_curve_properties(self):
        """Test curve properties"""
        self.assertEqual(self.curve.name, "Circle")
        self.assertEqual(self.curve.dimension, 2)  # 2D curve


class TestBaseField(unittest.TestCase):
    """Test the base field functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.field = BaseField(10)  # Create a field with modulus 10

    def test_field_initialization(self):
        """Test that the field initializes correctly"""
        self.assertEqual(self.field.modulus, 10)
        self.assertEqual(self.field.size, 10)

    def test_field_operations(self):
        """Test field arithmetic operations"""
        # Addition
        self.assertEqual(self.field.add(3, 7), 0)  # (3 + 7) % 10 = 0
        self.assertEqual(self.field.add(5, 5), 0)  # (5 + 5) % 10 = 0
        
        # Multiplication
        self.assertEqual(self.field.multiply(3, 7), 1)  # (3 * 7) % 10 = 1
        self.assertEqual(self.field.multiply(5, 6), 0)  # (5 * 6) % 10 = 0
        
        # Subtraction
        self.assertEqual(self.field.subtract(3, 7), 6)  # (3 - 7) % 10 = 6
        self.assertEqual(self.field.subtract(10, 3), 7)  # (10 - 3) % 10 = 7


class TestFieldStrategy(unittest.TestCase):
    """Test the field strategy functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.strategy = FieldStrategy()

    def test_strategy_initialization(self):
        """Test that the strategy initializes correctly"""
        self.assertIsNotNone(self.strategy)
        
    def test_strategy_methods_exist(self):
        """Test that required methods exist"""
        # These should be callable
        self.assertTrue(hasattr(self.strategy, 'apply'))
        self.assertTrue(hasattr(self.strategy, 'validate'))


if __name__ == "__main__":
    unittest.main()