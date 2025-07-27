"""
Sprint 3 Regression Test Suite - Task GEO-S3-T7

Comprehensive regression tests for Superellipse and ProceduralCurve classes.
Ensures both classes maintain interface consistency and work correctly together.

Tests cover:
- Interface consistency between all curve classes
- Inheritance from ImplicitCurve works correctly for both classes
- Serialization behavior and limitations
- Cross-class functional equivalence where applicable
- Edge cases and error handling for specialized curve types
"""

import pytest
import sympy as sp
import numpy as np
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse
from geometry.procedural_curve import ProceduralCurve


class TestSprint3InterfaceConsistency:
    """Test that all curve classes maintain consistent interfaces"""
    
    def setup_method(self):
        """Set up test curves for all classes"""
        x, y = sp.symbols('x y')
        
        # Common circle expression that can be represented by multiple classes
        circle_expr = x**2 + y**2 - 1
        
        # Create instances of all classes with equivalent circle representations
        self.conic_circle = ConicSection(circle_expr, variables=(x, y))
        self.poly_circle = PolynomialCurve(circle_expr, variables=(x, y))
        self.super_circle = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # ProceduralCurve with equivalent function
        circle_func = lambda x, y: x**2 + y**2 - 1
        self.proc_circle = ProceduralCurve(circle_func, name="Circle")
    
    def test_all_inherit_from_implicit_curve(self):
        """Test that all classes properly inherit from ImplicitCurve"""
        curves = [self.conic_circle, self.poly_circle, self.super_circle, self.proc_circle]
        
        for curve in curves:
            assert isinstance(curve, ImplicitCurve)
            assert hasattr(curve, 'evaluate')
            assert hasattr(curve, 'gradient')
            assert hasattr(curve, 'normal')
            assert hasattr(curve, 'to_dict')
    
    def test_evaluate_method_consistency(self):
        """Test that evaluate method gives consistent results across classes"""
        test_points = [
            (0.0, 0.0),   # Inside
            (1.0, 0.0),   # On curve
            (2.0, 0.0),   # Outside
            (0.0, 1.0),   # On curve
            (0.5, 0.5),   # Various points
            (-1.0, 0.0),  # Negative coordinates
            (0.0, -1.0)
        ]
        
        # All curves should give similar results for circle evaluation
        for x, y in test_points:
            conic_val = self.conic_circle.evaluate(x, y)
            poly_val = self.poly_circle.evaluate(x, y)
            super_val = self.super_circle.evaluate(x, y)
            proc_val = self.proc_circle.evaluate(x, y)
            
            # All should be close to each other (within numerical tolerance)
            assert abs(conic_val - poly_val) < 1e-10
            assert abs(conic_val - super_val) < 1e-10
            assert abs(conic_val - proc_val) < 1e-10
    
    def test_gradient_method_consistency(self):
        """Test that gradient method gives consistent results across classes"""
        test_points = [
            (1.0, 0.0),   # On curve
            (0.0, 1.0),   # On curve
            (0.5, 0.5),   # Various points
            (2.0, 0.0),   # Outside
            (-1.0, 0.0)   # Negative coordinates
        ]
        
        for x, y in test_points:
            conic_grad = self.conic_circle.gradient(x, y)
            poly_grad = self.poly_circle.gradient(x, y)
            super_grad = self.super_circle.gradient(x, y)
            proc_grad = self.proc_circle.gradient(x, y)
            
            # Symbolic gradients should match exactly
            assert abs(conic_grad[0] - poly_grad[0]) < 1e-10
            assert abs(conic_grad[1] - poly_grad[1]) < 1e-10
            
            # Superellipse should match (for n=2, it's the same as circle)
            assert abs(conic_grad[0] - super_grad[0]) < 1e-10
            assert abs(conic_grad[1] - super_grad[1]) < 1e-10
            
            # ProceduralCurve uses numerical gradient, so tolerance is higher
            assert abs(conic_grad[0] - proc_grad[0]) < 1e-5
            assert abs(conic_grad[1] - proc_grad[1]) < 1e-5


class TestSprint3SerializationBehavior:
    """Test serialization behavior across all Sprint 3 classes"""
    
    def setup_method(self):
        """Set up test curves"""
        self.super_circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.super_square = Superellipse(a=2.0, b=1.5, n=4.0)
        
        circle_func = lambda x, y: x**2 + y**2 - 1
        self.proc_circle = ProceduralCurve(circle_func, name="Circle")
        
        complex_func = lambda x, y: np.sin(x) + np.cos(y) - 1
        self.proc_complex = ProceduralCurve(complex_func, name="Trigonometric")
    
    def test_superellipse_serialization_completeness(self):
        """Test that Superellipse serialization is complete and functional"""
        curves = [self.super_circle, self.super_square]
        
        for curve in curves:
            # Serialize
            data = curve.to_dict()
            
            # Check structure
            assert data["type"] == "Superellipse"
            assert "a" in data
            assert "b" in data
            assert "n" in data
            assert "shape_type" in data
            
            # Deserialize
            reconstructed = Superellipse.from_dict(data)
            
            # Test functional equivalence
            test_points = [(0.0, 0.0), (0.5, 0.3), (1.0, 0.0)]
            for x, y in test_points:
                orig_val = curve.evaluate(x, y)
                recon_val = reconstructed.evaluate(x, y)
                assert abs(orig_val - recon_val) < 1e-10
    
    def test_procedural_curve_serialization_limitations(self):
        """Test that ProceduralCurve serialization has documented limitations"""
        curves = [self.proc_circle, self.proc_complex]
        
        for curve in curves:
            # Serialize
            data = curve.to_dict()
            
            # Check structure
            assert data["type"] == "ProceduralCurve"
            assert "function" in data
            assert "name" in data
            assert "_serialization_note" in data
            
            # Function should be placeholder string, not actual function
            assert isinstance(data["function"], str)
            assert not callable(data["function"])
            
            # Deserialize
            reconstructed = ProceduralCurve.from_dict(data)
            
            # Should be ProceduralCurve but not functional
            assert isinstance(reconstructed, ProceduralCurve)
            
            # Should raise error when trying to evaluate
            with pytest.raises(NotImplementedError):
                reconstructed.evaluate(0.0, 0.0)
    
    def test_cross_class_serialization_type_specificity(self):
        """Test that each class serializes with its specific type"""
        curves_and_types = [
            (self.super_circle, "Superellipse"),
            (self.proc_circle, "ProceduralCurve")
        ]
        
        for curve, expected_type in curves_and_types:
            data = curve.to_dict()
            assert data["type"] == expected_type


class TestSprint3SpecializedFeatures:
    """Test specialized features unique to Sprint 3 classes"""
    
    def setup_method(self):
        """Set up test curves with different characteristics"""
        # Various superellipse shapes
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.square = Superellipse(a=1.0, b=1.0, n=4.0)
        self.diamond = Superellipse(a=1.0, b=1.0, n=1.0)
        self.ellipse = Superellipse(a=2.0, b=1.0, n=2.0)
        
        # Various procedural curves
        self.proc_circle = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, name="Circle")
        self.proc_line = ProceduralCurve(lambda x, y: x + y - 1, name="Line")
        self.proc_trig = ProceduralCurve(lambda x, y: np.sin(x) + np.cos(y) - 1, name="Trigonometric")
    
    def test_superellipse_shape_classification(self):
        """Test Superellipse shape classification"""
        assert self.circle.shape_type() == "circle"
        assert self.square.shape_type() == "square-like"
        assert self.diamond.shape_type() == "diamond"
        assert self.ellipse.shape_type() == "ellipse"
    
    def test_superellipse_parameter_access(self):
        """Test access to Superellipse parameters"""
        assert self.circle.a == 1.0
        assert self.circle.b == 1.0
        assert self.circle.n == 2.0
        
        assert self.ellipse.a == 2.0
        assert self.ellipse.b == 1.0
        assert self.ellipse.n == 2.0
    
    def test_superellipse_gradient_handling(self):
        """Test Superellipse gradient computation with absolute values"""
        # Test at non-axis points (should be smooth)
        test_point = (0.5, 0.3)
        
        for superellipse in [self.circle, self.square, self.diamond]:
            grad_x, grad_y = superellipse.gradient(*test_point)
            
            # Gradient should be finite
            assert np.isfinite(grad_x)
            assert np.isfinite(grad_y)
            
            # Gradient should have reasonable magnitude
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            assert grad_magnitude > 0
            assert grad_magnitude < 100  # Reasonable upper bound
    
    def test_procedural_curve_function_access(self):
        """Test access to stored functions in ProceduralCurve"""
        assert callable(self.proc_circle.function)
        assert self.proc_circle.name == "Circle"
        
        # Test that stored function works
        result = self.proc_circle.function(1.0, 0.0)
        assert abs(result - 0.0) < 1e-10
    
    def test_procedural_curve_numerical_gradient_accuracy(self):
        """Test accuracy of numerical gradient computation"""
        # For simple polynomial functions, numerical gradient should be accurate
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for x, y in test_points:
            # Circle: analytical gradient is (2x, 2y)
            grad_x, grad_y = self.proc_circle.gradient(x, y)
            expected_x, expected_y = 2*x, 2*y
            
            assert abs(grad_x - expected_x) < 1e-5
            assert abs(grad_y - expected_y) < 1e-5
            
            # Line: analytical gradient is (1, 1)
            grad_x, grad_y = self.proc_line.gradient(x, y)
            assert abs(grad_x - 1.0) < 1e-5
            assert abs(grad_y - 1.0) < 1e-5


class TestSprint3EdgeCases:
    """Test edge cases and error handling for Sprint 3 classes"""
    
    def test_superellipse_parameter_validation(self):
        """Test Superellipse parameter validation"""
        # Valid parameters should work
        Superellipse(a=1.0, b=1.0, n=2.0)
        Superellipse(a=0.5, b=2.0, n=1.5)
        
        # Invalid parameters should raise errors
        with pytest.raises(ValueError):
            Superellipse(a=0.0, b=1.0, n=2.0)  # a must be positive
        
        with pytest.raises(ValueError):
            Superellipse(a=1.0, b=0.0, n=2.0)  # b must be positive
        
        with pytest.raises(ValueError):
            Superellipse(a=1.0, b=1.0, n=0.0)  # n must be positive
    
    def test_superellipse_extreme_parameters(self):
        """Test Superellipse with extreme parameter values"""
        # Very small n (close to 0)
        try:
            small_n = Superellipse(a=1.0, b=1.0, n=0.1)
            # Should not crash
            val = small_n.evaluate(0.5, 0.5)
            assert np.isfinite(val)
        except ValueError:
            # If implementation rejects very small n, that's acceptable
            pass
        
        # Very large n
        large_n = Superellipse(a=1.0, b=1.0, n=10.0)
        val = large_n.evaluate(0.5, 0.5)
        assert np.isfinite(val)
        assert large_n.shape_type() == "square-like"
    
    def test_procedural_curve_function_validation(self):
        """Test ProceduralCurve function validation"""
        # Valid functions should work
        ProceduralCurve(lambda x, y: x**2 + y**2 - 1)
        
        def valid_function(x, y):
            return x + y - 1
        
        ProceduralCurve(valid_function)
        
        # Invalid functions should raise errors
        with pytest.raises(ValueError):
            ProceduralCurve("not a function")
        
        with pytest.raises(ValueError):
            ProceduralCurve(123)
        
        with pytest.raises(ValueError):
            ProceduralCurve(None)
    
    def test_procedural_curve_function_errors(self):
        """Test ProceduralCurve behavior with functions that raise errors"""
        # Function that raises error for certain inputs
        def problematic_function(x, y):
            if x < 0:
                raise ValueError("x must be non-negative")
            return x**2 + y**2 - 1
        
        curve = ProceduralCurve(problematic_function, name="Problematic")
        
        # Should work for valid inputs
        result = curve.evaluate(1.0, 0.0)
        assert abs(result - 0.0) < 1e-10
        
        # Should propagate error for invalid inputs
        with pytest.raises(ValueError):
            curve.evaluate(-1.0, 0.0)


class TestSprint3VectorizedOperations:
    """Test vectorized operations for Sprint 3 classes"""
    
    def setup_method(self):
        """Set up test curves"""
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0)
        self.proc_curve = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, name="Circle")
    
    def test_superellipse_vectorized_evaluation(self):
        """Test vectorized evaluation for Superellipse"""
        x_vals = np.array([0.0, 1.0, 2.0, -1.0])
        y_vals = np.array([0.0, 0.0, 0.0, 0.0])
        
        results = self.superellipse.evaluate(x_vals, y_vals)
        
        assert isinstance(results, np.ndarray)
        assert results.shape == x_vals.shape
        
        # Check individual values
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            scalar_result = self.superellipse.evaluate(float(x), float(y))
            assert abs(results[i] - scalar_result) < 1e-10
    
    def test_superellipse_vectorized_gradient(self):
        """Test vectorized gradient for Superellipse"""
        x_vals = np.array([1.0, 0.0, 0.5])
        y_vals = np.array([0.0, 1.0, 0.5])
        
        grad_x, grad_y = self.superellipse.gradient(x_vals, y_vals)
        
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x_vals.shape
        assert grad_y.shape == y_vals.shape
        
        # Check individual values
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            scalar_grad = self.superellipse.gradient(float(x), float(y))
            assert abs(grad_x[i] - scalar_grad[0]) < 1e-10
            assert abs(grad_y[i] - scalar_grad[1]) < 1e-10
    
    def test_procedural_curve_vectorized_evaluation(self):
        """Test vectorized evaluation for ProceduralCurve"""
        x_vals = np.array([0.0, 1.0, 2.0, -1.0])
        y_vals = np.array([0.0, 0.0, 0.0, 0.0])
        
        results = self.proc_curve.evaluate(x_vals, y_vals)
        
        assert isinstance(results, np.ndarray)
        assert results.shape == x_vals.shape
        
        # Check individual values
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            scalar_result = self.proc_curve.evaluate(float(x), float(y))
            assert abs(results[i] - scalar_result) < 1e-10
    
    def test_procedural_curve_vectorized_gradient(self):
        """Test vectorized gradient for ProceduralCurve"""
        x_vals = np.array([1.0, 0.0, 0.5])
        y_vals = np.array([0.0, 1.0, 0.5])
        
        grad_x, grad_y = self.proc_curve.gradient(x_vals, y_vals)
        
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x_vals.shape
        assert grad_y.shape == y_vals.shape
        
        # Check individual values (with numerical tolerance)
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            scalar_grad = self.proc_curve.gradient(float(x), float(y))
            assert abs(grad_x[i] - scalar_grad[0]) < 1e-10
            assert abs(grad_y[i] - scalar_grad[1]) < 1e-10


if __name__ == "__main__":
    # Run regression tests
    pytest.main([__file__, "-v"])
