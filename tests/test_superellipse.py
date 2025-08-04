"""
Test suite for Superellipse class - Sprint 3 Task GEO-S3-T1

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- Superellipse shape evaluation (inside/outside points)
- Gradient computation with piecewise nature handling
- Different superellipse types (squarish n>2, diamond-like n<2)
- Specialized serialization and interface compliance
"""

import pytest
import sympy as sp
import numpy as np
from geometry.superellipse import Superellipse
from geometry.implicit_curve import ImplicitCurve


class TestSuperellipseConstructor:
    """Test Superellipse constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that Superellipse properly inherits from ImplicitCurve"""
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0)
        
        # Should be instance of both Superellipse and ImplicitCurve
        assert isinstance(superellipse, Superellipse)
        assert isinstance(superellipse, ImplicitCurve)
    
    def test_constructor_with_standard_parameters(self):
        """Test constructor with various parameter combinations"""
        # Standard circle (n=2, a=b=1)
        circle = Superellipse(a=1.0, b=1.0, n=2.0)
        assert circle.a == 1.0
        assert circle.b == 1.0
        assert circle.n == 2.0
        
        # Ellipse-like (n=2, different a,b)
        ellipse = Superellipse(a=2.0, b=1.0, n=2.0)
        assert ellipse.a == 2.0
        assert ellipse.b == 1.0
        assert ellipse.n == 2.0
        
        # Squarish superellipse (n>2)
        square = Superellipse(a=1.0, b=1.0, n=4.0)
        assert square.a == 1.0
        assert square.b == 1.0
        assert square.n == 4.0
        
        # Diamond-like superellipse (n<2)
        diamond = Superellipse(a=1.0, b=1.0, n=1.0)
        assert diamond.a == 1.0
        assert diamond.b == 1.0
        assert diamond.n == 1.0
    
    def test_constructor_with_custom_variables(self):
        """Test constructor with custom variable symbols"""
        u, v = sp.symbols('u v')
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(u, v))
        
        assert superellipse.variables == (u, v)
        # Expression should use u, v instead of x, y
        assert superellipse.expression.has(u)
        assert superellipse.expression.has(v)
    
    def test_constructor_parameter_validation(self):
        """Test constructor parameter validation"""
        # Positive parameters should work
        Superellipse(a=1.0, b=1.0, n=2.0)
        Superellipse(a=0.5, b=2.0, n=1.5)
        
        # Zero or negative parameters might be handled differently
        # (Implementation decision - could allow or raise error)
        try:
            Superellipse(a=0.0, b=1.0, n=2.0)
            Superellipse(a=1.0, b=0.0, n=2.0)
            Superellipse(a=1.0, b=1.0, n=0.0)
        except ValueError:
            # If implementation chooses to validate, that's acceptable
            pass
    
    def test_expression_generation(self):
        """Test that the superellipse expression is correctly generated"""
        x, y = sp.symbols('x y')
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # For n=2, a=b=1, should be similar to x² + y² - 1 = 0
        # But using absolute values: |x|^n + |y|^n - 1 = 0
        expr = superellipse.expression
        
        # Should contain absolute value terms
        assert expr.has(sp.Abs)
        assert expr.has(x)
        assert expr.has(y)


class TestSuperellipseEvaluation:
    """Test Superellipse evaluation for different shapes"""
    
    def setup_method(self):
        """Set up test superellipses"""
        # Standard circle (n=2)
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        
        # Squarish superellipse (n=4)
        self.square = Superellipse(a=1.0, b=1.0, n=4.0)
        
        # Diamond-like superellipse (n=1)
        self.diamond = Superellipse(a=1.0, b=1.0, n=1.0)
        
        # Elliptical superellipse
        self.ellipse = Superellipse(a=2.0, b=1.0, n=2.0)
    
    def test_evaluate_circle_like_superellipse(self):
        """Test evaluation for circle-like superellipse (n=2)"""
        # Origin should be inside (negative value)
        assert self.circle.evaluate(0.0, 0.0) < 0
        
        # Points on approximate boundary
        assert abs(self.circle.evaluate(1.0, 0.0)) < 0.1  # Near boundary
        assert abs(self.circle.evaluate(0.0, 1.0)) < 0.1  # Near boundary
        
        # Points clearly outside
        assert self.circle.evaluate(2.0, 0.0) > 0
        assert self.circle.evaluate(0.0, 2.0) > 0
        assert self.circle.evaluate(1.5, 1.5) > 0
        
        # Points clearly inside
        assert self.circle.evaluate(0.5, 0.0) < 0
        assert self.circle.evaluate(0.0, 0.5) < 0
        assert self.circle.evaluate(0.3, 0.3) < 0
    
    def test_evaluate_squarish_superellipse(self):
        """Test evaluation for squarish superellipse (n>2)"""
        # Origin should be inside
        assert self.square.evaluate(0.0, 0.0) < 0
        
        # Points that would be outside a circle but inside a square
        # For n=4: |0.9|^4 + |0.9|^4 = 1.3122 > 1, so (0.9,0.9) is outside
        assert self.square.evaluate(0.9, 0.9) > 0  # Outside - was incorrectly expecting inside
        # Use a point that's actually inside: |0.8|^4 + |0.8|^4 = 0.8192 < 1
        assert self.square.evaluate(0.8, 0.8) < 0  # Inside square, outside circle
        
        # Points clearly outside
        assert self.square.evaluate(1.5, 0.0) > 0
        assert self.square.evaluate(0.0, 1.5) > 0
        assert self.square.evaluate(1.2, 1.2) > 0
        
        # Corners should be closer to boundary than in circle
        corner_val = self.square.evaluate(0.8, 0.8)
        circle_val = self.circle.evaluate(0.8, 0.8)
        # Square should be "more inside" at corners
        assert corner_val < circle_val
    
    def test_evaluate_diamond_like_superellipse(self):
        """Test evaluation for diamond-like superellipse (n<2)"""
        # Origin should be inside
        assert self.diamond.evaluate(0.0, 0.0) < 0
        
        # Points on axes should be near boundary
        assert abs(self.diamond.evaluate(1.0, 0.0)) < 0.1
        assert abs(self.diamond.evaluate(0.0, 1.0)) < 0.1
        
        # Points clearly outside
        assert self.diamond.evaluate(1.5, 0.0) > 0
        assert self.diamond.evaluate(0.0, 1.5) > 0
        
        # Diamond shape: corners are "more outside" than circle
        corner_val = self.diamond.evaluate(0.5, 0.5)
        circle_val = self.circle.evaluate(0.5, 0.5)
        # Diamond should be "more outside" at corners
        assert corner_val > circle_val
    
    def test_evaluate_elliptical_superellipse(self):
        """Test evaluation for elliptical superellipse (different a, b)"""
        # Origin should be inside
        assert self.ellipse.evaluate(0.0, 0.0) < 0
        
        # Points on major axis (x-axis, a=2)
        assert abs(self.ellipse.evaluate(2.0, 0.0)) < 0.1  # Near boundary
        assert self.ellipse.evaluate(1.0, 0.0) < 0  # Inside
        assert self.ellipse.evaluate(3.0, 0.0) > 0  # Outside
        
        # Points on minor axis (y-axis, b=1)
        assert abs(self.ellipse.evaluate(0.0, 1.0)) < 0.1  # Near boundary
        assert self.ellipse.evaluate(0.0, 0.5) < 0  # Inside
        assert self.ellipse.evaluate(0.0, 1.5) > 0  # Outside
    
    def test_evaluate_vectorized(self):
        """Test vectorized evaluation with numpy arrays"""
        x_vals = np.array([0.0, 1.0, 2.0, -1.0, 0.5])
        y_vals = np.array([0.0, 0.0, 0.0, 0.0, 0.5])
        
        results = self.circle.evaluate(x_vals, y_vals)
        
        assert isinstance(results, np.ndarray)
        assert len(results) == len(x_vals)
        
        # Check individual results match scalar evaluation
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            scalar_result = self.circle.evaluate(float(x), float(y))
            assert abs(results[i] - scalar_result) < 1e-10


class TestSuperellipseGradient:
    """Test Superellipse gradient computation with piecewise handling"""
    
    def setup_method(self):
        """Set up test superellipses"""
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.square = Superellipse(a=1.0, b=1.0, n=4.0)
        self.diamond = Superellipse(a=1.0, b=1.0, n=1.0)
    
    def test_gradient_at_non_axis_points(self):
        """Test gradient computation at points away from axes (smooth regions)"""
        # Test point in first quadrant, away from axes
        test_point = (0.5, 0.3)
        
        for superellipse in [self.circle, self.square, self.diamond]:
            grad_x, grad_y = superellipse.gradient(*test_point)
            
            # Gradient should be finite
            assert np.isfinite(grad_x)
            assert np.isfinite(grad_y)
            
            # Gradient should point outward from origin for points inside
            if superellipse.evaluate(*test_point) < 0:
                # For points inside, gradient should point away from origin
                assert grad_x * test_point[0] >= 0  # Same sign or zero
                assert grad_y * test_point[1] >= 0  # Same sign or zero
    
    def test_gradient_symmetry(self):
        """Test gradient symmetry properties"""
        test_points = [
            (0.5, 0.3),
            (-0.5, 0.3),
            (0.5, -0.3),
            (-0.5, -0.3)
        ]
        
        for superellipse in [self.circle, self.square]:
            gradients = [superellipse.gradient(x, y) for x, y in test_points]
            
            # Check symmetry properties
            # grad(-x, y) should be (-grad_x, grad_y)
            assert abs(gradients[1][0] + gradients[0][0]) < 1e-10
            assert abs(gradients[1][1] - gradients[0][1]) < 1e-10
            
            # grad(x, -y) should be (grad_x, -grad_y)
            assert abs(gradients[2][0] - gradients[0][0]) < 1e-10
            assert abs(gradients[2][1] + gradients[0][1]) < 1e-10
    
    def test_gradient_near_axes(self):
        """Test gradient behavior near axes (potential non-smooth points)"""
        # Points very close to axes
        epsilon = 1e-6
        near_axis_points = [
            (1.0, epsilon),   # Near x-axis
            (epsilon, 1.0),   # Near y-axis
            (-1.0, epsilon),  # Near negative x-axis
            (epsilon, -1.0)   # Near negative y-axis
        ]
        
        for superellipse in [self.circle, self.square, self.diamond]:
            for x, y in near_axis_points:
                try:
                    grad_x, grad_y = superellipse.gradient(x, y)
                    
                    # Gradient should be finite (implementation should handle singularities)
                    assert np.isfinite(grad_x)
                    assert np.isfinite(grad_y)
                    
                except (ValueError, ZeroDivisionError):
                    # If implementation raises error at singular points, that's acceptable
                    pass
    
    def test_gradient_magnitude_scaling(self):
        """Test that gradient magnitude scales appropriately with parameters"""
        # Compare gradients for different superellipse parameters
        point = (0.5, 0.3)
        
        # Different exponents
        n2_grad = self.circle.gradient(*point)
        n4_grad = self.square.gradient(*point)
        
        # Both should be finite
        assert all(np.isfinite(g) for g in n2_grad)
        assert all(np.isfinite(g) for g in n4_grad)
        
        # Gradients should have reasonable magnitudes
        n2_mag = np.sqrt(n2_grad[0]**2 + n2_grad[1]**2)
        n4_mag = np.sqrt(n4_grad[0]**2 + n4_grad[1]**2)
        
        assert n2_mag > 0
        assert n4_mag > 0


class TestSuperellipseSpecializedMethods:
    """Test Superellipse specialized methods and properties"""
    
    def setup_method(self):
        """Set up test superellipses"""
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.square = Superellipse(a=1.0, b=1.0, n=4.0)
        self.diamond = Superellipse(a=1.0, b=1.0, n=1.0)
    
    def test_parameter_access(self):
        """Test access to superellipse parameters"""
        assert self.circle.a == 1.0
        assert self.circle.b == 1.0
        assert self.circle.n == 2.0
        
        assert self.square.n == 4.0
        assert self.diamond.n == 1.0
    
    def test_shape_classification(self):
        """Test classification of superellipse shapes"""
        # This could be a specialized method if implemented
        # For now, just test that we can distinguish based on n
        assert self.circle.n == 2.0  # Circle-like
        assert self.square.n > 2.0   # Square-like
        assert self.diamond.n < 2.0  # Diamond-like
    
    def test_string_representations(self):
        """Test string representations"""
        circle_str = str(self.circle)
        assert "superellipse" in circle_str.lower() or "abs" in circle_str.lower() or "|" in circle_str
        
        circle_repr = repr(self.circle)
        assert "Superellipse" in circle_repr
        assert "1.0" in circle_repr  # Should show parameters
        assert "2.0" in circle_repr


class TestSuperellipseSerialization:
    """Test Superellipse serialization"""
    
    def setup_method(self):
        """Set up test superellipses"""
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.square = Superellipse(a=2.0, b=1.5, n=4.0)
    
    def test_to_dict_structure(self):
        """Test that to_dict returns proper structure"""
        data = self.circle.to_dict()
        
        assert isinstance(data, dict)
        assert data["type"] == "Superellipse"
        assert "expression" in data
        assert "variables" in data
        assert "a" in data
        assert "b" in data
        assert "n" in data
        
        # Check parameter values
        assert data["a"] == 1.0
        assert data["b"] == 1.0
        assert data["n"] == 2.0
    
    def test_from_dict_reconstruction(self):
        """Test that from_dict can reconstruct Superellipse"""
        # Serialize and deserialize
        data = self.square.to_dict()
        reconstructed = Superellipse.from_dict(data)
        
        # Should be Superellipse instance
        assert isinstance(reconstructed, Superellipse)
        assert isinstance(reconstructed, ImplicitCurve)
        
        # Should have same parameters
        assert reconstructed.a == self.square.a
        assert reconstructed.b == self.square.b
        assert reconstructed.n == self.square.n
    
    def test_serialization_round_trip_functional_equivalence(self):
        """Test that serialization preserves functional behavior"""
        test_curves = [self.circle, self.square]
        test_points = [(0.0, 0.0), (0.5, 0.3), (1.0, 0.0), (0.0, 1.0)]
        
        for curve in test_curves:
            # Serialize and deserialize
            data = curve.to_dict()
            reconstructed = Superellipse.from_dict(data)
            
            # Test functional equivalence
            for x, y in test_points:
                orig_val = curve.evaluate(x, y)
                recon_val = reconstructed.evaluate(x, y)
                assert abs(orig_val - recon_val) < 1e-10
                
                # Test gradient equivalence (at non-singular points)
                try:
                    orig_grad = curve.gradient(x, y)
                    recon_grad = reconstructed.gradient(x, y)
                    assert abs(orig_grad[0] - recon_grad[0]) < 1e-10
                    assert abs(orig_grad[1] - recon_grad[1]) < 1e-10
                except (ValueError, ZeroDivisionError):
                    # Both should behave the same at singular points
                    with pytest.raises((ValueError, ZeroDivisionError)):
                        reconstructed.gradient(x, y)
    
    def test_from_dict_error_handling(self):
        """Test error handling in from_dict"""
        # Missing required fields
        with pytest.raises(ValueError):
            Superellipse.from_dict({"type": "Superellipse"})  # Missing parameters
        
        # Wrong type
        with pytest.raises(ValueError):
            Superellipse.from_dict({"type": "WrongType", "a": 1.0, "b": 1.0, "n": 2.0})
        
        # Invalid parameters
        with pytest.raises(ValueError):
            Superellipse.from_dict({
                "type": "Superellipse", 
                "a": "invalid", 
                "b": 1.0, 
                "n": 2.0,
                "expression": "Abs(x)**2 + Abs(y)**2 - 1",
                "variables": ["x", "y"]
            })


class TestSuperellipseInheritedMethods:
    """Test that Superellipse properly inherits and works with ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test superellipses"""
        self.circle = Superellipse(a=1.0, b=1.0, n=2.0)
        self.square = Superellipse(a=1.0, b=1.0, n=4.0)
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly"""
        test_point = (0.5, 0.3)
        
        for superellipse in [self.circle, self.square]:
            try:
                nx, ny = superellipse.normal(*test_point)
                
                # Normal should be unit length
                magnitude = np.sqrt(nx**2 + ny**2)
                assert abs(magnitude - 1.0) < 1e-10
                
                # Normal should be perpendicular to gradient
                grad_x, grad_y = superellipse.gradient(*test_point)
                # Normal should be in same direction as gradient (outward pointing)
                dot_product = nx * grad_x + ny * grad_y
                grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                assert abs(dot_product - grad_magnitude) < 1e-10
                
            except (ValueError, ZeroDivisionError):
                # If gradient is zero, normal should also raise error
                with pytest.raises((ValueError, ZeroDivisionError)):
                    superellipse.gradient(*test_point)
    
    def test_plot_method_inherited(self):
        """Test that plot method is available and doesn't crash"""
        # Just test that the method exists and can be called
        assert hasattr(self.circle, 'plot')
        
        # Test that it doesn't crash (might not display in test environment)
        try:
            self.circle.plot(xlim=(-2, 2), ylim=(-2, 2), resolution=50)
        except Exception as e:
            # Plot might fail in test environment, but shouldn't crash the class
            assert "plot" in str(e).lower() or "display" in str(e).lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
