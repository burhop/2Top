"""
Test suite for ProceduralCurve class - Sprint 3 Task GEO-S3-T3

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- Evaluation using Python lambda functions and callables
- Numerical gradient computation using finite differences
- Serialization limitations and placeholder behavior
- Interface compliance with ImplicitCurve methods
"""

import pytest
import sympy as sp
import numpy as np
from geometry.procedural_curve import ProceduralCurve
from geometry.implicit_curve import ImplicitCurve


class TestProceduralCurveConstructor:
    """Test ProceduralCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that ProceduralCurve properly inherits from ImplicitCurve"""
        # Simple lambda function for a circle
        circle_func = lambda x, y: x**2 + y**2 - 1
        proc_curve = ProceduralCurve(circle_func)
        
        # Should be instance of both ProceduralCurve and ImplicitCurve
        assert isinstance(proc_curve, ProceduralCurve)
        assert isinstance(proc_curve, ImplicitCurve)
    
    def test_constructor_with_lambda_function(self):
        """Test constructor with lambda functions"""
        # Various lambda functions
        functions = [
            lambda x, y: x**2 + y**2 - 1,  # Circle
            lambda x, y: x + y - 1,        # Line
            lambda x, y: x**3 + y**3 - 1,  # Cubic
            lambda x, y: np.sin(x) + np.cos(y) - 1,  # Trigonometric
            lambda x, y: np.exp(x**2 + y**2) - 2     # Exponential
        ]
        
        for func in functions:
            proc_curve = ProceduralCurve(func)
            assert proc_curve.function == func
            assert callable(proc_curve.function)
    
    def test_constructor_with_regular_function(self):
        """Test constructor with regular Python functions"""
        def circle_function(x, y):
            return x**2 + y**2 - 1
        
        def complex_function(x, y):
            return np.sin(x**2) + np.cos(y**2) - 0.5
        
        functions = [circle_function, complex_function]
        
        for func in functions:
            proc_curve = ProceduralCurve(func)
            assert proc_curve.function == func
            assert callable(proc_curve.function)
    
    def test_constructor_with_custom_variables(self):
        """Test constructor with custom variable symbols"""
        u, v = sp.symbols('u v')
        circle_func = lambda x, y: x**2 + y**2 - 1
        
        proc_curve = ProceduralCurve(circle_func, variables=(u, v))
        assert proc_curve.variables == (u, v)
    
    def test_constructor_with_function_name(self):
        """Test constructor with optional function name/description"""
        circle_func = lambda x, y: x**2 + y**2 - 1
        
        proc_curve = ProceduralCurve(circle_func, name="Unit Circle")
        assert proc_curve.name == "Unit Circle"
        
        # Test default name
        proc_curve2 = ProceduralCurve(circle_func)
        assert proc_curve2.name == "custom"
    
    def test_constructor_validation(self):
        """Test constructor parameter validation"""
        # Non-callable should raise error
        with pytest.raises(ValueError, match="function must be callable"):
            ProceduralCurve("not a function")
        
        with pytest.raises(ValueError, match="function must be callable"):
            ProceduralCurve(123)
        
        with pytest.raises(ValueError, match="function must be callable"):
            ProceduralCurve(None)


class TestProceduralCurveEvaluation:
    """Test ProceduralCurve evaluation using stored functions"""
    
    def setup_method(self):
        """Set up test procedural curves"""
        # Circle function
        self.circle_func = lambda x, y: x**2 + y**2 - 1
        self.circle = ProceduralCurve(self.circle_func, name="Circle")
        
        # Line function
        self.line_func = lambda x, y: x + y - 1
        self.line = ProceduralCurve(self.line_func, name="Line")
        
        # Complex function
        self.complex_func = lambda x, y: np.sin(x) * np.cos(y) - 0.5
        self.complex = ProceduralCurve(self.complex_func, name="Trigonometric")
        
        # Function with numpy operations
        self.numpy_func = lambda x, y: np.exp(-(x**2 + y**2)) - 0.5
        self.numpy_curve = ProceduralCurve(self.numpy_func, name="Gaussian")
    
    def test_evaluate_scalar_inputs(self):
        """Test evaluation with scalar inputs"""
        # Circle tests
        assert abs(self.circle.evaluate(0.0, 0.0) - (-1.0)) < 1e-10  # Inside
        assert abs(self.circle.evaluate(1.0, 0.0) - 0.0) < 1e-10     # On curve
        assert abs(self.circle.evaluate(2.0, 0.0) - 3.0) < 1e-10     # Outside
        
        # Line tests
        assert abs(self.line.evaluate(0.5, 0.5) - 0.0) < 1e-10       # On line
        assert abs(self.line.evaluate(0.0, 0.0) - (-1.0)) < 1e-10    # Below line
        assert abs(self.line.evaluate(1.0, 1.0) - 1.0) < 1e-10       # Above line
        
        # Complex function tests
        complex_val = self.complex.evaluate(0.0, 0.0)
        expected = np.sin(0.0) * np.cos(0.0) - 0.5  # 0 * 1 - 0.5 = -0.5
        assert abs(complex_val - expected) < 1e-10
    
    def test_evaluate_vectorized_inputs(self):
        """Test evaluation with numpy array inputs"""
        x_vals = np.array([0.0, 1.0, 2.0, -1.0])
        y_vals = np.array([0.0, 0.0, 0.0, 0.0])
        
        # Circle evaluation
        circle_results = self.circle.evaluate(x_vals, y_vals)
        expected_circle = x_vals**2 + y_vals**2 - 1
        
        assert isinstance(circle_results, np.ndarray)
        assert len(circle_results) == len(x_vals)
        np.testing.assert_allclose(circle_results, expected_circle, rtol=1e-10)
        
        # Line evaluation
        line_results = self.line.evaluate(x_vals, y_vals)
        expected_line = x_vals + y_vals - 1
        
        np.testing.assert_allclose(line_results, expected_line, rtol=1e-10)
    
    def test_evaluate_mixed_array_shapes(self):
        """Test evaluation with different array shapes"""
        # 2D arrays
        x_grid = np.array([[0.0, 1.0], [2.0, -1.0]])
        y_grid = np.array([[0.0, 0.0], [0.0, 0.0]])
        
        results = self.circle.evaluate(x_grid, y_grid)
        expected = x_grid**2 + y_grid**2 - 1
        
        assert results.shape == x_grid.shape
        np.testing.assert_allclose(results, expected, rtol=1e-10)
    
    def test_evaluate_function_with_numpy_operations(self):
        """Test evaluation of functions that use numpy operations"""
        # Test gaussian-like function
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
        
        for x, y in test_points:
            result = self.numpy_curve.evaluate(x, y)
            expected = np.exp(-(x**2 + y**2)) - 0.5
            assert abs(result - expected) < 1e-10
    
    def test_evaluate_consistency_with_direct_call(self):
        """Test that evaluate gives same results as direct function call"""
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5), (-1.0, 1.0)]
        
        curves_and_funcs = [
            (self.circle, self.circle_func),
            (self.line, self.line_func),
            (self.complex, self.complex_func)
        ]
        
        for curve, func in curves_and_funcs:
            for x, y in test_points:
                curve_result = curve.evaluate(x, y)
                direct_result = func(x, y)
                assert abs(curve_result - direct_result) < 1e-10


class TestProceduralCurveGradient:
    """Test ProceduralCurve numerical gradient computation"""
    
    def setup_method(self):
        """Set up test procedural curves with known analytical gradients"""
        # Circle: f(x,y) = x² + y² - 1, ∇f = (2x, 2y)
        self.circle_func = lambda x, y: x**2 + y**2 - 1
        self.circle = ProceduralCurve(self.circle_func, name="Circle")
        
        # Line: f(x,y) = x + y - 1, ∇f = (1, 1)
        self.line_func = lambda x, y: x + y - 1
        self.line = ProceduralCurve(self.line_func, name="Line")
        
        # Quadratic: f(x,y) = x² + 2xy + y² - 1, ∇f = (2x + 2y, 2x + 2y)
        self.quad_func = lambda x, y: x**2 + 2*x*y + y**2 - 1
        self.quad = ProceduralCurve(self.quad_func, name="Quadratic")
    
    def test_gradient_scalar_inputs(self):
        """Test gradient computation with scalar inputs"""
        # Circle gradient at (1, 0) should be approximately (2, 0)
        grad_x, grad_y = self.circle.gradient(1.0, 0.0)
        assert abs(grad_x - 2.0) < 1e-6  # Numerical approximation tolerance
        assert abs(grad_y - 0.0) < 1e-6
        
        # Circle gradient at (0, 1) should be approximately (0, 2)
        grad_x, grad_y = self.circle.gradient(0.0, 1.0)
        assert abs(grad_x - 0.0) < 1e-6
        assert abs(grad_y - 2.0) < 1e-6
        
        # Line gradient should be approximately (1, 1) everywhere
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5), (-1.0, 1.0)]
        for x, y in test_points:
            grad_x, grad_y = self.line.gradient(x, y)
            assert abs(grad_x - 1.0) < 1e-6
            assert abs(grad_y - 1.0) < 1e-6
    
    def test_gradient_vectorized_inputs(self):
        """Test gradient computation with array inputs"""
        x_vals = np.array([1.0, 0.0, 0.5])
        y_vals = np.array([0.0, 1.0, 0.5])
        
        grad_x, grad_y = self.circle.gradient(x_vals, y_vals)
        
        # Should return arrays of same shape
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x_vals.shape
        assert grad_y.shape == y_vals.shape
        
        # Check individual values
        expected_grad_x = 2 * x_vals
        expected_grad_y = 2 * y_vals
        
        np.testing.assert_allclose(grad_x, expected_grad_x, rtol=1e-5)
        np.testing.assert_allclose(grad_y, expected_grad_y, rtol=1e-5)
    
    def test_gradient_accuracy_comparison(self):
        """Test gradient accuracy against analytical solutions"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (1.0, 1.0)]
        
        for x, y in test_points:
            # Circle: analytical gradient is (2x, 2y)
            grad_x, grad_y = self.circle.gradient(x, y)
            analytical_x, analytical_y = 2*x, 2*y
            
            assert abs(grad_x - analytical_x) < 1e-5
            assert abs(grad_y - analytical_y) < 1e-5
            
            # Quadratic: analytical gradient is (2x + 2y, 2x + 2y)
            grad_x, grad_y = self.quad.gradient(x, y)
            analytical_x = analytical_y = 2*x + 2*y
            
            assert abs(grad_x - analytical_x) < 1e-5
            assert abs(grad_y - analytical_y) < 1e-5
    
    def test_gradient_finite_difference_parameters(self):
        """Test that gradient uses appropriate finite difference step size"""
        # Test that gradient is reasonably accurate
        # This indirectly tests the finite difference implementation
        
        # For a smooth function, numerical gradient should be close to analytical
        test_point = (0.5, 0.3)
        grad_x, grad_y = self.circle.gradient(*test_point)
        
        # Analytical gradient for circle at (0.5, 0.3)
        expected_x = 2 * 0.5  # 1.0
        expected_y = 2 * 0.3  # 0.6
        
        # Should be accurate to at least 1e-5
        assert abs(grad_x - expected_x) < 1e-5
        assert abs(grad_y - expected_y) < 1e-5
    
    def test_gradient_with_complex_functions(self):
        """Test gradient computation for more complex functions"""
        # Trigonometric function
        trig_func = lambda x, y: np.sin(x) + np.cos(y)
        trig_curve = ProceduralCurve(trig_func, name="Trigonometric")
        
        # Test at a point where we know the analytical gradient
        x, y = 0.0, 0.0
        grad_x, grad_y = trig_curve.gradient(x, y)
        
        # Analytical: ∂/∂x[sin(x) + cos(y)] = cos(x) = cos(0) = 1
        # Analytical: ∂/∂y[sin(x) + cos(y)] = -sin(y) = -sin(0) = 0
        expected_x = np.cos(0.0)  # 1.0
        expected_y = -np.sin(0.0)  # 0.0
        
        assert abs(grad_x - expected_x) < 1e-5
        assert abs(grad_y - expected_y) < 1e-5


class TestProceduralCurveSerialization:
    """Test ProceduralCurve serialization limitations - Sprint 3 Task GEO-S3-T5"""
    
    def setup_method(self):
        """Set up test procedural curves"""
        self.circle_func = lambda x, y: x**2 + y**2 - 1
        self.circle = ProceduralCurve(self.circle_func, name="Circle")
        
        def named_function(x, y):
            return x + y - 1
        
        self.line = ProceduralCurve(named_function, name="Line")
    
    def test_to_dict_contains_placeholder(self):
        """Test that to_dict returns placeholder information, not function code"""
        data = self.circle.to_dict()
        
        assert isinstance(data, dict)
        assert data["type"] == "ProceduralCurve"
        assert "function" in data
        
        # Should contain placeholder, not actual function code
        assert data["function"] == "custom" or "placeholder" in data["function"].lower()
        
        # Should not contain actual function code or bytecode
        assert "lambda" not in str(data).lower()
        assert "bytecode" not in str(data).lower()
        assert "code" not in data["function"].lower()
        
        # Should contain name if provided
        if hasattr(self.circle, 'name'):
            assert "name" in data
            assert data["name"] == self.circle.name
    
    def test_to_dict_descriptive_information(self):
        """Test that to_dict includes descriptive information"""
        data = self.line.to_dict()
        
        # Should have descriptive fields
        assert "type" in data
        assert data["type"] == "ProceduralCurve"
        
        # Should indicate it's a custom function
        assert "function" in data
        assert isinstance(data["function"], str)
        
        # Should include variables information
        assert "variables" in data
        assert isinstance(data["variables"], list)
    
    def test_from_dict_creates_placeholder_object(self):
        """Test that from_dict creates a placeholder object with limited functionality"""
        # Serialize
        data = self.circle.to_dict()
        
        # Deserialize
        reconstructed = ProceduralCurve.from_dict(data)
        
        # Should be ProceduralCurve instance
        assert isinstance(reconstructed, ProceduralCurve)
        assert isinstance(reconstructed, ImplicitCurve)
        
        # Should have placeholder function that raises appropriate error
        with pytest.raises((NotImplementedError, ValueError), match="placeholder|serialized|cannot evaluate"):
            reconstructed.evaluate(0.0, 0.0)
    
    def test_serialization_round_trip_limitation(self):
        """Test that serialization round-trip has documented limitations"""
        # Original curve should work
        original_result = self.circle.evaluate(1.0, 0.0)
        assert abs(original_result - 0.0) < 1e-10
        
        # Serialize and deserialize
        data = self.circle.to_dict()
        reconstructed = ProceduralCurve.from_dict(data)
        
        # Reconstructed should not be functional
        with pytest.raises((NotImplementedError, ValueError)):
            reconstructed.evaluate(1.0, 0.0)
        
        # But should preserve metadata
        if hasattr(reconstructed, 'name'):
            assert reconstructed.name == self.circle.name
    
    def test_serialization_error_handling(self):
        """Test error handling in serialization methods"""
        # Test invalid data for from_dict
        invalid_data_cases = [
            {},  # Empty dict
            {"type": "WrongType"},  # Wrong type
            {"type": "ProceduralCurve"},  # Missing function field
            {"type": "ProceduralCurve", "function": 123},  # Invalid function field
        ]
        
        for invalid_data in invalid_data_cases:
            with pytest.raises(ValueError):
                ProceduralCurve.from_dict(invalid_data)
    
    def test_serialization_documentation_compliance(self):
        """Test that serialization behavior matches documented limitations"""
        data = self.circle.to_dict()
        
        # Should clearly indicate it's a ProceduralCurve
        assert data["type"] == "ProceduralCurve"
        
        # Should indicate function is custom/placeholder
        function_desc = data["function"]
        assert isinstance(function_desc, str)
        assert function_desc in ["custom", "placeholder"] or "custom" in function_desc.lower()
        
        # Should not attempt to serialize actual function
        assert not callable(data["function"])


class TestProceduralCurveInheritedMethods:
    """Test that ProceduralCurve properly inherits and works with ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test procedural curves"""
        self.circle_func = lambda x, y: x**2 + y**2 - 1
        self.circle = ProceduralCurve(self.circle_func, name="Circle")
        
        self.line_func = lambda x, y: x + y - 1
        self.line = ProceduralCurve(self.line_func, name="Line")
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly with numerical gradients"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for x, y in test_points:
            try:
                nx, ny = self.circle.normal(x, y)
                
                # Normal should be unit length
                magnitude = np.sqrt(nx**2 + ny**2)
                assert abs(magnitude - 1.0) < 1e-6  # Slightly relaxed for numerical gradient
                
                # Normal should be in same direction as gradient
                grad_x, grad_y = self.circle.gradient(x, y)
                grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                
                if grad_magnitude > 1e-10:  # Avoid division by zero
                    expected_nx = grad_x / grad_magnitude
                    expected_ny = grad_y / grad_magnitude
                    
                    assert abs(nx - expected_nx) < 1e-5
                    assert abs(ny - expected_ny) < 1e-5
                
            except (ValueError, ZeroDivisionError):
                # If gradient is zero, normal should also raise error
                with pytest.raises((ValueError, ZeroDivisionError)):
                    self.circle.gradient(x, y)
    
    def test_variables_property_inherited(self):
        """Test that variables property works correctly"""
        # Default variables
        assert len(self.circle.variables) == 2
        assert all(isinstance(var, sp.Symbol) for var in self.circle.variables)
        
        # Custom variables
        u, v = sp.symbols('u v')
        custom_curve = ProceduralCurve(self.circle_func, variables=(u, v))
        assert custom_curve.variables == (u, v)
    
    def test_expression_property_behavior(self):
        """Test behavior of expression property for procedural curves"""
        # ProceduralCurve should have some form of expression representation
        # This might be a placeholder or symbolic representation
        expr = self.circle.expression
        
        # Should be a sympy expression or None
        assert expr is None or isinstance(expr, sp.Basic)
    
    def test_plot_method_inherited(self):
        """Test that plot method is available"""
        # Just test that the method exists
        assert hasattr(self.circle, 'plot')
        
        # Test that it doesn't crash (might not display in test environment)
        try:
            self.circle.plot(xlim=(-2, 2), ylim=(-2, 2), resolution=20)
        except Exception as e:
            # Plot might fail in test environment, but shouldn't crash the class
            # Allow plot-related errors but not implementation errors
            error_msg = str(e).lower()
            allowed_errors = ["plot", "display", "matplotlib", "figure", "show"]
            assert any(allowed in error_msg for allowed in allowed_errors)


class TestProceduralCurveSpecializedMethods:
    """Test ProceduralCurve specialized methods and properties"""
    
    def setup_method(self):
        """Set up test procedural curves"""
        self.circle_func = lambda x, y: x**2 + y**2 - 1
        self.circle = ProceduralCurve(self.circle_func, name="Circle")
        
        def named_function(x, y):
            """A named function for testing"""
            return x + y - 1
        
        self.line = ProceduralCurve(named_function, name="Line")
    
    def test_function_property_access(self):
        """Test access to stored function"""
        assert self.circle.function == self.circle_func
        assert callable(self.circle.function)
        
        # Test that stored function works
        result = self.circle.function(1.0, 0.0)
        assert abs(result - 0.0) < 1e-10
    
    def test_name_property_access(self):
        """Test access to function name/description"""
        assert self.circle.name == "Circle"
        assert self.line.name == "Line"
        
        # Test default name
        unnamed_curve = ProceduralCurve(lambda x, y: x**2 + y**2 - 1)
        assert unnamed_curve.name == "custom"
    
    def test_string_representations(self):
        """Test string representations"""
        circle_str = str(self.circle)
        assert "procedural" in circle_str.lower() or "custom" in circle_str.lower()
        assert "Circle" in circle_str
        
        circle_repr = repr(self.circle)
        assert "ProceduralCurve" in circle_repr
        assert "Circle" in circle_repr
    
    def test_function_signature_validation(self):
        """Test that function signature is appropriate"""
        # Function should accept two arguments
        try:
            result = self.circle.function(1.0, 0.0)
            assert isinstance(result, (int, float, np.number))
        except TypeError:
            pytest.fail("Function should accept two numeric arguments")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
