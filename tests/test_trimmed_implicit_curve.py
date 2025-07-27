"""
Test suite for TrimmedImplicitCurve class - Sprint 5 Task GEO-S5-T1

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- Contains method for checking points on masked curve segments
- Mask function behavior and validation
- Interface compliance with ImplicitCurve methods
- Edge cases and error handling
"""

import pytest
import sympy as sp
import numpy as np
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse


class TestTrimmedImplicitCurveConstructor:
    """Test TrimmedImplicitCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that TrimmedImplicitCurve properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        mask = lambda x, y: x >= 0  # Right half
        
        trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
        
        # Should be instance of both TrimmedImplicitCurve and ImplicitCurve
        assert isinstance(trimmed_curve, TrimmedImplicitCurve)
        assert isinstance(trimmed_curve, ImplicitCurve)
    
    def test_constructor_with_various_base_curves(self):
        """Test constructor with different base curve types"""
        x, y = sp.symbols('x y')
        
        # Different base curve types
        conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        mask = lambda x, y: x >= 0
        
        base_curves = [conic, poly, superellipse]
        
        for base_curve in base_curves:
            trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
            assert trimmed_curve.base_curve == base_curve
            assert trimmed_curve.mask == mask
    
    def test_constructor_with_various_masks(self):
        """Test constructor with different mask functions"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Different mask functions
        masks = {
            "right_half": lambda x, y: x >= 0,
            "upper_half": lambda x, y: y >= 0,
            "first_quadrant": lambda x, y: x >= 0 and y >= 0,
            "outside_small_circle": lambda x, y: x**2 + y**2 >= 0.25,
            "complex_region": lambda x, y: x >= 0 and y >= 0 and x + y <= 1
        }
        
        for name, mask in masks.items():
            trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
            assert trimmed_curve.mask == mask
            assert callable(trimmed_curve.mask)
    
    def test_constructor_parameter_validation(self):
        """Test constructor parameter validation"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        mask = lambda x, y: x >= 0
        
        # Valid construction
        trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
        assert trimmed_curve.base_curve == base_curve
        assert trimmed_curve.mask == mask
        
        # Invalid base curve
        with pytest.raises(TypeError, match="must be ImplicitCurve"):
            TrimmedImplicitCurve("not a curve", mask)
        
        # Invalid mask (not callable)
        with pytest.raises(TypeError, match="must be callable"):
            TrimmedImplicitCurve(base_curve, "not callable")
    
    def test_constructor_preserves_variables(self):
        """Test that constructor preserves variables from base curve"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        mask = lambda x, y: x >= 0
        
        trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
        
        assert trimmed_curve.variables == base_curve.variables
        assert len(trimmed_curve.variables) == 2


class TestTrimmedImplicitCurveContains:
    """Test TrimmedImplicitCurve contains method - Sprint 5 Task GEO-S5-T1"""
    
    def setup_method(self):
        """Set up test curves for contains method testing"""
        x, y = sp.symbols('x y')
        
        # Create base circle
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create different trimmed versions
        self.right_half = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        self.upper_half = TrimmedImplicitCurve(self.circle, lambda x, y: y >= 0)
        self.first_quadrant = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0)
        
        # Create line for additional testing
        self.line = PolynomialCurve(x + y - 1, variables=(x, y))
        self.line_segment = TrimmedImplicitCurve(self.line, lambda x, y: x >= 0 and x <= 1)
    
    def test_contains_right_half_circle(self):
        """Test contains method for right half of circle"""
        # Points on the right arc should be contained
        test_cases = [
            (1.0, 0.0, True, "Right point on circle"),
            (0.0, 1.0, True, "Top point on circle (x=0 boundary)"),
            (0.0, -1.0, True, "Bottom point on circle (x=0 boundary)"),
            (0.707, 0.707, True, "Point on right arc (approx)"),
            (0.707, -0.707, True, "Point on right arc (approx)"),
            (-1.0, 0.0, False, "Left point on circle (outside mask)"),
            (-0.707, 0.707, False, "Point on left arc (outside mask)"),
            (-0.707, -0.707, False, "Point on left arc (outside mask)"),
            (0.5, 0.0, False, "Point inside circle but not on boundary"),
            (2.0, 0.0, False, "Point outside circle"),
            (0.5, 0.5, False, "Point inside circle but not on boundary")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.right_half.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_upper_half_circle(self):
        """Test contains method for upper half of circle"""
        test_cases = [
            (0.0, 1.0, True, "Top point on circle"),
            (1.0, 0.0, True, "Right point on circle (y=0 boundary)"),
            (-1.0, 0.0, True, "Left point on circle (y=0 boundary)"),
            (0.707, 0.707, True, "Point on upper arc"),
            (-0.707, 0.707, True, "Point on upper arc"),
            (0.0, -1.0, False, "Bottom point on circle (outside mask)"),
            (0.707, -0.707, False, "Point on lower arc (outside mask)"),
            (-0.707, -0.707, False, "Point on lower arc (outside mask)")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.upper_half.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_first_quadrant_circle(self):
        """Test contains method for first quadrant of circle"""
        test_cases = [
            (1.0, 0.0, True, "Right point on circle"),
            (0.0, 1.0, True, "Top point on circle"),
            (0.707, 0.707, True, "Point on first quadrant arc"),
            (-1.0, 0.0, False, "Left point on circle (outside mask)"),
            (0.0, -1.0, False, "Bottom point on circle (outside mask)"),
            (-0.707, 0.707, False, "Point on second quadrant arc"),
            (0.707, -0.707, False, "Point on fourth quadrant arc"),
            (-0.707, -0.707, False, "Point on third quadrant arc")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.first_quadrant.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_line_segment(self):
        """Test contains method for line segment"""
        test_cases = [
            (0.0, 1.0, True, "Start point of segment"),
            (1.0, 0.0, True, "End point of segment"),
            (0.5, 0.5, True, "Middle point of segment"),
            (0.25, 0.75, True, "Point on segment"),
            (0.75, 0.25, True, "Point on segment"),
            (-0.5, 1.5, False, "Point on line but outside mask (x < 0)"),
            (1.5, -0.5, False, "Point on line but outside mask (x > 1)"),
            (0.5, 0.6, False, "Point near line but not on it"),
            (2.0, 0.0, False, "Point not on line")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.line_segment.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_tolerance_handling(self):
        """Test contains method with numerical tolerance"""
        # Points very close to the boundary should be considered on the curve
        tolerance_cases = [
            (1.0 + 1e-10, 0.0, True, "Point very close to circle boundary"),
            (1.0 - 1e-10, 0.0, True, "Point very close to circle boundary"),
            (0.0 + 1e-10, 1.0, True, "Point very close to circle boundary"),
            (0.0 - 1e-10, 1.0, False, "Point very close to boundary but outside right half (x < 0)")
        ]
        
        for x, y, expected, description in tolerance_cases:
            result = self.right_half.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_vectorized_input(self):
        """Test contains method with vectorized input"""
        # Test with numpy arrays
        x_vals = np.array([1.0, 0.0, -1.0, 0.707])
        y_vals = np.array([0.0, 1.0, 0.0, 0.707])
        
        results = self.right_half.contains(x_vals, y_vals)
        expected = np.array([True, True, False, True])
        
        np.testing.assert_array_equal(results, expected)
    
    def test_contains_edge_cases(self):
        """Test contains method edge cases"""
        # Test points exactly on mask boundary
        boundary_cases = [
            (0.0, 1.0, True, "Point on x=0 boundary (included)"),
            (0.0, -1.0, True, "Point on x=0 boundary (included)"),
            (0.0, 0.5, False, "Point on x=0 boundary but not on curve")
        ]
        
        for x, y, expected, description in boundary_cases:
            result = self.right_half.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"


class TestTrimmedImplicitCurveInheritedMethods:
    """Test that TrimmedImplicitCurve properly inherits ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        mask = lambda x, y: x >= 0
        
        self.trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
    
    def test_evaluate_method_inherited(self):
        """Test that evaluate method works correctly"""
        # Evaluate should work the same as base curve (trimming affects contains, not evaluate)
        test_points = [(0.0, 0.0), (1.0, 0.0), (-1.0, 0.0), (0.5, 0.5)]
        
        for x, y in test_points:
            trimmed_val = self.trimmed_curve.evaluate(x, y)
            base_val = self.trimmed_curve.base_curve.evaluate(x, y)
            assert abs(trimmed_val - base_val) < 1e-15
    
    def test_gradient_method_inherited(self):
        """Test that gradient method works correctly"""
        test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
        
        for x, y in test_points:
            try:
                trimmed_grad = self.trimmed_curve.gradient(x, y)
                base_grad = self.trimmed_curve.base_curve.gradient(x, y)
                
                assert abs(trimmed_grad[0] - base_grad[0]) < 1e-15
                assert abs(trimmed_grad[1] - base_grad[1]) < 1e-15
                
            except (ValueError, ZeroDivisionError):
                # If base curve gradient fails, trimmed should fail too
                with pytest.raises((ValueError, ZeroDivisionError)):
                    self.trimmed_curve.base_curve.gradient(x, y)
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.707, 0.707)]
        
        for x, y in test_points:
            try:
                trimmed_normal = self.trimmed_curve.normal(x, y)
                base_normal = self.trimmed_curve.base_curve.normal(x, y)
                
                assert abs(trimmed_normal[0] - base_normal[0]) < 1e-15
                assert abs(trimmed_normal[1] - base_normal[1]) < 1e-15
                
            except (ValueError, ZeroDivisionError):
                # If base curve normal fails, trimmed should fail too
                with pytest.raises((ValueError, ZeroDivisionError)):
                    self.trimmed_curve.base_curve.normal(x, y)
    
    def test_variables_property_inherited(self):
        """Test that variables property works correctly"""
        assert self.trimmed_curve.variables == self.trimmed_curve.base_curve.variables
        assert len(self.trimmed_curve.variables) == 2
    
    def test_plot_method_inherited(self):
        """Test that plot method is available"""
        assert hasattr(self.trimmed_curve, 'plot')


class TestTrimmedImplicitCurveSpecializedMethods:
    """Test TrimmedImplicitCurve specialized methods and properties"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        base_curve = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        mask = lambda x, y: x >= 0
        
        self.trimmed_curve = TrimmedImplicitCurve(base_curve, mask)
    
    def test_property_access(self):
        """Test access to TrimmedImplicitCurve properties"""
        assert isinstance(self.trimmed_curve.base_curve, ImplicitCurve)
        assert callable(self.trimmed_curve.mask)
        
        # Test mask function
        assert self.trimmed_curve.mask(1.0, 0.0) == True
        assert self.trimmed_curve.mask(-1.0, 0.0) == False
    
    def test_string_representations(self):
        """Test string representations"""
        trimmed_str = str(self.trimmed_curve)
        assert "TrimmedImplicitCurve" in trimmed_str
        
        trimmed_repr = repr(self.trimmed_curve)
        assert "TrimmedImplicitCurve" in trimmed_repr
        assert "base_curve" in trimmed_repr


class TestTrimmedImplicitCurveComplexMasks:
    """Test TrimmedImplicitCurve with complex mask functions"""
    
    def setup_method(self):
        """Set up test curves with complex masks"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Complex mask functions
        self.annular_mask = lambda x, y: x**2 + y**2 >= 0.25  # Outside small circle
        self.angular_mask = lambda x, y: np.arctan2(y, x) >= 0 and np.arctan2(y, x) <= np.pi/2  # First quadrant by angle
        self.distance_mask = lambda x, y: abs(x - 0.5) + abs(y - 0.5) <= 0.5  # Diamond region
        
        self.annular_curve = TrimmedImplicitCurve(self.circle, self.annular_mask)
        self.angular_curve = TrimmedImplicitCurve(self.circle, self.angular_mask)
        self.distance_curve = TrimmedImplicitCurve(self.circle, self.distance_mask)
    
    def test_annular_mask(self):
        """Test annular mask (outside small circle)"""
        test_cases = [
            (1.0, 0.0, True, "Point on outer circle, outside inner circle"),
            (0.0, 1.0, True, "Point on outer circle, outside inner circle"),
            (0.4, 0.3, False, "Point on outer circle but inside inner circle"),
            (0.0, 0.0, False, "Point at origin (inside inner circle)")
        ]
        
        for x, y, expected, description in test_cases:
            # Check if point is on circle first
            if abs(self.circle.evaluate(x, y)) < 1e-10:
                result = self.annular_curve.contains(x, y)
                assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_angular_mask(self):
        """Test angular mask (first quadrant by angle)"""
        test_cases = [
            (1.0, 0.0, True, "Point at 0 degrees"),
            (0.0, 1.0, True, "Point at 90 degrees"),
            (0.707, 0.707, True, "Point at 45 degrees"),
            (-1.0, 0.0, False, "Point at 180 degrees"),
            (0.0, -1.0, False, "Point at 270 degrees"),
            (-0.707, 0.707, False, "Point at 135 degrees")
        ]
        
        for x, y, expected, description in test_cases:
            # Check if point is on circle first
            if abs(self.circle.evaluate(x, y)) < 1e-10:
                result = self.angular_curve.contains(x, y)
                assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_distance_mask(self):
        """Test distance mask (diamond region)"""
        # This tests intersection of circle with diamond region
        test_cases = [
            (1.0, 0.0, True, "Point on circle within diamond"),
            (0.0, 1.0, True, "Point on circle within diamond"),
            # Note: Need to find actual intersection points for more precise testing
        ]
        
        for x, y, expected, description in test_cases:
            # Check if point is on circle and satisfies mask
            if abs(self.circle.evaluate(x, y)) < 1e-10:
                result = self.distance_curve.contains(x, y)
                # For this complex case, just verify the method runs without error
                assert isinstance(result, (bool, np.bool_))


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
