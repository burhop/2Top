"""
Test suite for RFunctionCurve class - Sprint 4 Task GEO-S4-T1

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- Sharp union and intersection operations using min/max
- Smooth blending operations with alpha parameter
- Serialization of composite curves with child curve preservation
- Interface compliance with ImplicitCurve methods
"""

import pytest
import sympy as sp
import numpy as np
from geometry.rfunction_curve import RFunctionCurve
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse


class TestRFunctionCurveConstructor:
    """Test RFunctionCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that RFunctionCurve properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-2)**2 + y**2 - 1, variables=(x, y))
        
        union_curve = RFunctionCurve(circle1, circle2, operation="union")
        
        # Should be instance of both RFunctionCurve and ImplicitCurve
        assert isinstance(union_curve, RFunctionCurve)
        assert isinstance(union_curve, ImplicitCurve)
    
    def test_constructor_with_various_operations(self):
        """Test constructor with different operation types"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-2)**2 + y**2 - 1, variables=(x, y))
        
        # Test all supported operations
        operations = ["union", "intersection", "difference", "blend"]
        
        for op in operations:
            if op == "blend":
                curve = RFunctionCurve(circle1, circle2, operation=op, alpha=0.1)
                assert curve.alpha == 0.1
            else:
                curve = RFunctionCurve(circle1, circle2, operation=op)
                assert curve.alpha == 0.0  # Default for sharp operations
            
            assert curve.operation == op
            assert curve.curve1 == circle1
            assert curve.curve2 == circle2
    
    def test_constructor_with_different_curve_types(self):
        """Test constructor with different combinations of curve types"""
        x, y = sp.symbols('x y')
        
        # Different curve type combinations
        conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        combinations = [
            (conic, poly),
            (conic, superellipse),
            (poly, superellipse)
        ]
        
        for curve1, curve2 in combinations:
            union_curve = RFunctionCurve(curve1, curve2, operation="union")
            assert union_curve.curve1 == curve1
            assert union_curve.curve2 == curve2
    
    def test_constructor_parameter_validation(self):
        """Test constructor parameter validation"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-2)**2 + y**2 - 1, variables=(x, y))
        
        # Invalid operation type
        with pytest.raises(ValueError, match="Invalid operation"):
            RFunctionCurve(circle1, circle2, operation="invalid_op")
        
        # Invalid alpha for non-blend operations
        with pytest.raises(ValueError, match="alpha must be 0"):
            RFunctionCurve(circle1, circle2, operation="union", alpha=0.5)
        
        # Missing alpha for blend operation
        with pytest.raises(ValueError, match="alpha must be positive"):
            RFunctionCurve(circle1, circle2, operation="blend", alpha=0.0)
        
        # Non-ImplicitCurve inputs
        with pytest.raises(TypeError, match="must be ImplicitCurve"):
            RFunctionCurve("not a curve", circle2, operation="union")


class TestRFunctionCurveSharpOperations:
    """Test sharp union and intersection operations - Sprint 4 Task GEO-S4-T1"""
    
    def setup_method(self):
        """Set up test curves for sharp operations"""
        x, y = sp.symbols('x y')
        
        # Two overlapping circles
        self.circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))  # Centered at origin
        self.circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))  # Centered at (1,0)
        
        # Union and intersection curves
        self.union_curve = RFunctionCurve(self.circle1, self.circle2, operation="union")
        self.intersection_curve = RFunctionCurve(self.circle1, self.circle2, operation="intersection")
        self.difference_curve = RFunctionCurve(self.circle1, self.circle2, operation="difference")
    
    def test_sharp_union_evaluation(self):
        """Test sharp union operation using min(f1, f2)"""
        # Test points for union behavior
        test_cases = [
            # Point inside circle1 but outside circle2 - should be inside union
            (-0.5, 0.0, "inside"),
            # Point inside circle2 but outside circle1 - should be inside union  
            (1.5, 0.0, "inside"),
            # Point inside both circles (overlap) - should be inside union
            (0.5, 0.0, "inside"),
            # Point outside both circles - should be outside union
            (0.0, 2.0, "outside"),
            (2.0, 2.0, "outside")
        ]
        
        for x, y, expected in test_cases:
            union_val = self.union_curve.evaluate(x, y)
            circle1_val = self.circle1.evaluate(x, y)
            circle2_val = self.circle2.evaluate(x, y)
            
            # Union should be min(f1, f2)
            expected_val = min(circle1_val, circle2_val)
            assert abs(union_val - expected_val) < 1e-10
            
            # Check inside/outside behavior
            if expected == "inside":
                assert union_val < 0, f"Point ({x}, {y}) should be inside union"
            else:
                assert union_val > 0, f"Point ({x}, {y}) should be outside union"
    
    def test_sharp_intersection_evaluation(self):
        """Test sharp intersection operation using max(f1, f2)"""
        # Test points for intersection behavior
        test_cases = [
            # Point inside circle1 but outside circle2 - should be outside intersection
            (-0.5, 0.0, "outside"),
            # Point inside circle2 but outside circle1 - should be outside intersection
            (1.5, 0.0, "outside"),
            # Point inside both circles (overlap) - should be inside intersection
            (0.5, 0.0, "inside"),
            # Point outside both circles - should be outside intersection
            (0.0, 2.0, "outside"),
            (2.0, 2.0, "outside")
        ]
        
        for x, y, expected in test_cases:
            intersection_val = self.intersection_curve.evaluate(x, y)
            circle1_val = self.circle1.evaluate(x, y)
            circle2_val = self.circle2.evaluate(x, y)
            
            # Intersection should be max(f1, f2)
            expected_val = max(circle1_val, circle2_val)
            assert abs(intersection_val - expected_val) < 1e-10
            
            # Check inside/outside behavior
            if expected == "inside":
                assert intersection_val < 0, f"Point ({x}, {y}) should be inside intersection"
            else:
                assert intersection_val > 0, f"Point ({x}, {y}) should be outside intersection"
    
    def test_sharp_difference_evaluation(self):
        """Test sharp difference operation (A - B)"""
        # Test points for difference behavior
        test_cases = [
            # Point inside circle1 but outside circle2 - should be inside difference
            (-0.5, 0.0, "inside"),
            # Point inside circle2 but outside circle1 - should be outside difference
            (1.5, 0.0, "outside"),
            # Point inside both circles (overlap) - should be outside difference
            (0.5, 0.0, "outside"),
            # Point outside both circles - should be outside difference
            (0.0, 2.0, "outside")
        ]
        
        for x, y, expected in test_cases:
            difference_val = self.difference_curve.evaluate(x, y)
            circle1_val = self.circle1.evaluate(x, y)
            circle2_val = self.circle2.evaluate(x, y)
            
            # Difference should be max(f1, -f2)
            expected_val = max(circle1_val, -circle2_val)
            assert abs(difference_val - expected_val) < 1e-10
            
            # Check inside/outside behavior
            if expected == "inside":
                assert difference_val < 0, f"Point ({x}, {y}) should be inside difference"
            else:
                assert difference_val > 0, f"Point ({x}, {y}) should be outside difference"
    
    def test_vectorized_sharp_operations(self):
        """Test vectorized evaluation for sharp operations"""
        x_vals = np.array([-0.5, 0.5, 1.5, 0.0])
        y_vals = np.array([0.0, 0.0, 0.0, 2.0])
        
        # Test union
        union_results = self.union_curve.evaluate(x_vals, y_vals)
        circle1_results = self.circle1.evaluate(x_vals, y_vals)
        circle2_results = self.circle2.evaluate(x_vals, y_vals)
        
        expected_union = np.minimum(circle1_results, circle2_results)
        np.testing.assert_allclose(union_results, expected_union, rtol=1e-10)
        
        # Test intersection
        intersection_results = self.intersection_curve.evaluate(x_vals, y_vals)
        expected_intersection = np.maximum(circle1_results, circle2_results)
        np.testing.assert_allclose(intersection_results, expected_intersection, rtol=1e-10)


class TestRFunctionCurveSmoothBlending:
    """Test smooth blending operations - Sprint 4 Task GEO-S4-T3"""
    
    def setup_method(self):
        """Set up test curves for smooth blending"""
        x, y = sp.symbols('x y')
        
        # Two overlapping circles
        self.circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        
        # Smooth blend curves with different alpha values
        self.blend_small = RFunctionCurve(self.circle1, self.circle2, operation="blend", alpha=0.1)
        self.blend_medium = RFunctionCurve(self.circle1, self.circle2, operation="blend", alpha=0.5)
        self.blend_large = RFunctionCurve(self.circle1, self.circle2, operation="blend", alpha=1.0)
    
    def test_smooth_blend_evaluation(self):
        """Test smooth blend evaluation using quadratic approximation"""
        # Test points in blend region
        test_points = [
            (0.0, 0.0),   # Between circles
            (0.5, 0.0),   # In overlap region
            (0.25, 0.0),  # Blend transition area
            (0.75, 0.0)   # Blend transition area
        ]
        
        for x, y in test_points:
            f1 = self.circle1.evaluate(x, y)
            f2 = self.circle2.evaluate(x, y)
            
            # Test different alpha values
            for blend_curve in [self.blend_small, self.blend_medium, self.blend_large]:
                blend_val = blend_curve.evaluate(x, y)
                alpha = blend_curve.alpha
                
                # Smooth blend formula: (f1 + f2 - sqrt((f1-f2)^2 + alpha^2)) / 2
                expected_val = (f1 + f2 - np.sqrt((f1 - f2)**2 + alpha**2)) / 2
                assert abs(blend_val - expected_val) < 1e-10
    
    def test_smooth_blend_continuity(self):
        """Test that smooth blend produces continuous gradients"""
        # Test gradient continuity at blend boundaries
        test_points = [
            (0.25, 0.0),
            (0.5, 0.0),
            (0.75, 0.0)
        ]
        
        for x, y in test_points:
            # Get gradients for different alpha values
            grad_small = self.blend_small.gradient(x, y)
            grad_medium = self.blend_medium.gradient(x, y)
            grad_large = self.blend_large.gradient(x, y)
            
            # All gradients should be finite (no discontinuities)
            for grad in [grad_small, grad_medium, grad_large]:
                assert np.isfinite(grad[0])
                assert np.isfinite(grad[1])
                
                # Gradient magnitude should be reasonable
                grad_magnitude = np.sqrt(grad[0]**2 + grad[1]**2)
                assert grad_magnitude < 100  # Reasonable upper bound
    
    def test_smooth_blend_alpha_effect(self):
        """Test that alpha parameter affects blend smoothness"""
        test_point = (0.5, 0.0)  # Point in blend region
        
        # Get values for different alpha
        val_small = self.blend_small.evaluate(*test_point)
        val_medium = self.blend_medium.evaluate(*test_point)
        val_large = self.blend_large.evaluate(*test_point)
        
        # Larger alpha should create smoother transitions
        # Values should be different for different alpha values
        assert abs(val_small - val_medium) > 1e-6
        assert abs(val_medium - val_large) > 1e-6
    
    def test_smooth_blend_approaches_sharp_operations(self):
        """Test that smooth blend approaches sharp operations as alpha approaches 0"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        
        # Create blend with very small alpha
        tiny_alpha_blend = RFunctionCurve(circle1, circle2, operation="blend", alpha=1e-10)
        sharp_union = RFunctionCurve(circle1, circle2, operation="union")
        
        test_points = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
        
        for x, y in test_points:
            blend_val = tiny_alpha_blend.evaluate(x, y)
            union_val = sharp_union.evaluate(x, y)
            
            # Should be very close to sharp union
            assert abs(blend_val - union_val) < 1e-8


class TestRFunctionCurveGradient:
    """Test gradient computation for RFunctionCurve"""
    
    def setup_method(self):
        """Set up test curves for gradient testing"""
        x, y = sp.symbols('x y')
        self.circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        
        self.union_curve = RFunctionCurve(self.circle1, self.circle2, operation="union")
        self.blend_curve = RFunctionCurve(self.circle1, self.circle2, operation="blend", alpha=0.5)
    
    def test_gradient_computation(self):
        """Test gradient computation for RFunctionCurve"""
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        
        for x, y in test_points:
            # Test union gradient
            union_grad = self.union_curve.gradient(x, y)
            assert len(union_grad) == 2
            assert all(np.isfinite(g) for g in union_grad)
            
            # Test blend gradient
            blend_grad = self.blend_curve.gradient(x, y)
            assert len(blend_grad) == 2
            assert all(np.isfinite(g) for g in blend_grad)
    
    def test_gradient_vectorized(self):
        """Test vectorized gradient computation"""
        x_vals = np.array([0.0, 0.5, 1.0])
        y_vals = np.array([0.0, 0.5, 0.0])
        
        grad_x, grad_y = self.union_curve.gradient(x_vals, y_vals)
        
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x_vals.shape
        assert grad_y.shape == y_vals.shape
        assert all(np.isfinite(grad_x))
        assert all(np.isfinite(grad_y))


class TestRFunctionCurveInheritedMethods:
    """Test that RFunctionCurve properly inherits ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        
        self.union_curve = RFunctionCurve(circle1, circle2, operation="union")
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly"""
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        
        for x, y in test_points:
            try:
                nx, ny = self.union_curve.normal(x, y)
                
                # Normal should be unit length
                magnitude = np.sqrt(nx**2 + ny**2)
                assert abs(magnitude - 1.0) < 1e-10
                
            except (ValueError, ZeroDivisionError):
                # If gradient is zero, normal should raise error
                with pytest.raises((ValueError, ZeroDivisionError)):
                    self.union_curve.gradient(x, y)
    
    def test_variables_property_inherited(self):
        """Test that variables property works correctly"""
        assert len(self.union_curve.variables) == 2
        assert all(isinstance(var, sp.Symbol) for var in self.union_curve.variables)
    
    def test_plot_method_inherited(self):
        """Test that plot method is available"""
        assert hasattr(self.union_curve, 'plot')


class TestRFunctionCurveSerialization:
    """Test RFunctionCurve serialization - Sprint 4 Task GEO-S4-T6"""
    
    def setup_method(self):
        """Set up test curves for serialization testing"""
        x, y = sp.symbols('x y')
        
        # Create various child curve types
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # Create RFunctionCurves with different operations
        self.union_curve = RFunctionCurve(self.circle, self.ellipse, operation="union")
        self.intersection_curve = RFunctionCurve(self.circle, self.poly, operation="intersection")
        self.difference_curve = RFunctionCurve(self.poly, self.superellipse, operation="difference")
        self.blend_curve = RFunctionCurve(self.circle, self.ellipse, operation="blend", alpha=0.5)
    
    def test_serialization_round_trip_union(self):
        """Test serialization round-trip for union operation"""
        # Serialize and deserialize
        serialized = self.union_curve.to_dict()
        restored = RFunctionCurve.from_dict(serialized)
        
        # Test functional equivalence
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0), (-1.0, 0.0)]
        
        for x, y in test_points:
            original_val = self.union_curve.evaluate(x, y)
            restored_val = restored.evaluate(x, y)
            assert abs(original_val - restored_val) < 1e-10
        
        # Test properties
        assert restored.operation == self.union_curve.operation
        assert restored.alpha == self.union_curve.alpha
    
    def test_serialization_round_trip_blend(self):
        """Test serialization round-trip for blend operation"""
        # Serialize and deserialize
        serialized = self.blend_curve.to_dict()
        restored = RFunctionCurve.from_dict(serialized)
        
        # Test functional equivalence
        test_points = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (0.25, 0.25)]
        
        for x, y in test_points:
            original_val = self.blend_curve.evaluate(x, y)
            restored_val = restored.evaluate(x, y)
            assert abs(original_val - restored_val) < 1e-10
        
        # Test properties
        assert restored.operation == "blend"
        assert restored.alpha == 0.5


class TestRFunctionCurveSpecializedMethods:
    """Test RFunctionCurve specialized methods and properties"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        
        self.union_curve = RFunctionCurve(circle1, circle2, operation="union")
        self.blend_curve = RFunctionCurve(circle1, circle2, operation="blend", alpha=0.5)
    
    def test_property_access(self):
        """Test access to RFunctionCurve properties"""
        assert self.union_curve.operation == "union"
        assert self.union_curve.alpha == 0.0
        assert isinstance(self.union_curve.curve1, ImplicitCurve)
        assert isinstance(self.union_curve.curve2, ImplicitCurve)
        
        assert self.blend_curve.operation == "blend"
        assert self.blend_curve.alpha == 0.5
    
    def test_string_representations(self):
        """Test string representations"""
        union_str = str(self.union_curve)
        assert "union" in union_str.lower()
        
        union_repr = repr(self.union_curve)
        assert "RFunctionCurve" in union_repr
        assert "union" in union_repr
        
        blend_str = str(self.blend_curve)
        assert "blend" in blend_str.lower()
        assert "0.5" in blend_str


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
