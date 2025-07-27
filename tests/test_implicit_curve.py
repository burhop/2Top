"""
Test suite for ImplicitCurve class - Sprint 1 Task GEO-S1-T2

Tests cover:
- Constructor validation with valid/invalid inputs
- Evaluate method with scalar and numpy array inputs
- Points inside, on, and outside known curves
"""

import pytest
import sympy as sp
import numpy as np
from geometry.implicit_curve import ImplicitCurve


class TestImplicitCurveConstructor:
    """Test ImplicitCurve constructor validation"""
    
    def test_constructor_with_valid_sympy_expr(self):
        """Test successful instantiation with valid sympy.Expr"""
        x, y = sp.symbols('x y')
        expr = x**2 + y**2 - 1  # Unit circle
        curve = ImplicitCurve(expr, variables=(x, y))
        
        assert curve.expression == expr
        assert curve.variables == (x, y)
    
    def test_constructor_with_default_variables(self):
        """Test constructor with default (x, y) variables"""
        x, y = sp.symbols('x y')
        expr = x**2 + y**2 - 1
        curve = ImplicitCurve(expr)
        
        # Should use default x, y symbols
        assert len(curve.variables) == 2
        assert str(curve.variables[0]) == 'x'
        assert str(curve.variables[1]) == 'y'
    
    def test_constructor_with_invalid_expression_type(self):
        """Test constructor fails with non-sympy expression"""
        with pytest.raises((TypeError, ValueError)):
            ImplicitCurve("x^2 + y^2 - 1")  # String instead of sympy expr
    
    def test_constructor_with_invalid_expression_none(self):
        """Test constructor fails with None expression"""
        with pytest.raises((TypeError, ValueError)):
            ImplicitCurve(None)
    
    def test_constructor_with_wrong_number_of_variables(self):
        """Test constructor fails with wrong number of variables"""
        x, y, z = sp.symbols('x y z')
        expr = x**2 + y**2 - 1
        
        with pytest.raises((TypeError, ValueError)):
            ImplicitCurve(expr, variables=(x, y, z))  # 3 variables for 2D curve


class TestImplicitCurveEvaluate:
    """Test ImplicitCurve evaluate method"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        
        # Unit circle: x^2 + y^2 - 1 = 0
        self.circle_expr = x**2 + y**2 - 1
        self.circle = ImplicitCurve(self.circle_expr, variables=(x, y))
        
        # Line: x + y - 1 = 0
        self.line_expr = x + y - 1
        self.line = ImplicitCurve(self.line_expr, variables=(x, y))
    
    def test_evaluate_scalar_input_on_curve(self):
        """Test evaluate with scalar inputs for points on the curve"""
        # Point (1, 0) is on unit circle
        result = self.circle.evaluate(1.0, 0.0)
        assert abs(result) < 1e-10  # Should be approximately zero
        
        # Point (0.5, 0.5) is on line x + y - 1 = 0
        result = self.line.evaluate(0.5, 0.5)
        assert abs(result) < 1e-10
    
    def test_evaluate_scalar_input_inside_curve(self):
        """Test evaluate with scalar inputs for points inside closed curve"""
        # Point (0, 0) is inside unit circle (should be negative)
        result = self.circle.evaluate(0.0, 0.0)
        assert result < 0
        
        # Point (0.5, 0) is inside unit circle
        result = self.circle.evaluate(0.5, 0.0)
        assert result < 0
    
    def test_evaluate_scalar_input_outside_curve(self):
        """Test evaluate with scalar inputs for points outside closed curve"""
        # Point (2, 0) is outside unit circle (should be positive)
        result = self.circle.evaluate(2.0, 0.0)
        assert result > 0
        
        # Point (1.5, 1.5) is outside unit circle
        result = self.circle.evaluate(1.5, 1.5)
        assert result > 0
    
    def test_evaluate_numpy_array_input(self):
        """Test evaluate with numpy array inputs"""
        # Test with 1D arrays
        x_vals = np.array([0.0, 1.0, 2.0])
        y_vals = np.array([0.0, 0.0, 0.0])
        
        results = self.circle.evaluate(x_vals, y_vals)
        
        # Should return numpy array
        assert isinstance(results, np.ndarray)
        assert len(results) == 3
        
        # Check individual results
        assert results[0] < 0  # (0,0) inside
        assert abs(results[1]) < 1e-10  # (1,0) on curve
        assert results[2] > 0  # (2,0) outside
    
    def test_evaluate_2d_numpy_array_input(self):
        """Test evaluate with 2D numpy array inputs (meshgrid style)"""
        x_vals = np.array([[0.0, 1.0], [0.0, 1.0]])
        y_vals = np.array([[0.0, 0.0], [1.0, 1.0]])
        
        results = self.circle.evaluate(x_vals, y_vals)
        
        # Should return 2D array with same shape
        assert isinstance(results, np.ndarray)
        assert results.shape == (2, 2)
        
        # Check specific points
        assert results[0, 0] < 0  # (0,0) inside
        assert abs(results[0, 1]) < 1e-10  # (1,0) on curve
        assert results[1, 0] < 0  # (0,1) inside
        assert results[1, 1] > 0  # (1,1) outside
    
    def test_evaluate_mixed_scalar_array_input(self):
        """Test evaluate with mixed scalar and array inputs"""
        x_val = 0.0  # scalar
        y_vals = np.array([0.0, 1.0, 2.0])  # array
        
        results = self.circle.evaluate(x_val, y_vals)
        
        assert isinstance(results, np.ndarray)
        assert len(results) == 3
        
        # All points are (0, y) for different y values
        assert results[0] < 0  # (0,0) inside
        assert abs(results[1]) < 1e-10  # (0,1) on curve
        assert results[2] > 0  # (0,2) outside
    
    def test_evaluate_performance_with_large_arrays(self):
        """Test evaluate performance with large numpy arrays"""
        # Create a large grid
        x_vals = np.linspace(-2, 2, 100)
        y_vals = np.linspace(-2, 2, 100)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        # This should complete without timeout and return correct shape
        results = self.circle.evaluate(X, Y)
        
        assert isinstance(results, np.ndarray)
        assert results.shape == (100, 100)
        
        # Check that center point is inside
        center_idx = 50
        assert results[center_idx, center_idx] < 0


class TestImplicitCurveGradient:
    """Test ImplicitCurve gradient method - Sprint 1 Task GEO-S1-T4"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        
        # Unit circle: x^2 + y^2 - 1 = 0
        # Gradient should be (2x, 2y)
        self.circle_expr = x**2 + y**2 - 1
        self.circle = ImplicitCurve(self.circle_expr, variables=(x, y))
        
        # Line: x + y - 1 = 0
        # Gradient should be (1, 1)
        self.line_expr = x + y - 1
        self.line = ImplicitCurve(self.line_expr, variables=(x, y))
        
        # Parabola: y - x^2 = 0
        # Gradient should be (-2x, 1)
        self.parabola_expr = y - x**2
        self.parabola = ImplicitCurve(self.parabola_expr, variables=(x, y))
    
    def test_gradient_circle_at_known_points(self):
        """Test gradient computation for circle at known points"""
        # At point (1, 0), gradient should be (2, 0)
        grad_x, grad_y = self.circle.gradient(1.0, 0.0)
        assert abs(grad_x - 2.0) < 1e-10
        assert abs(grad_y - 0.0) < 1e-10
        
        # At point (0, 1), gradient should be (0, 2)
        grad_x, grad_y = self.circle.gradient(0.0, 1.0)
        assert abs(grad_x - 0.0) < 1e-10
        assert abs(grad_y - 2.0) < 1e-10
        
        # At point (-1, 0), gradient should be (-2, 0)
        grad_x, grad_y = self.circle.gradient(-1.0, 0.0)
        assert abs(grad_x - (-2.0)) < 1e-10
        assert abs(grad_y - 0.0) < 1e-10
    
    def test_gradient_line_constant(self):
        """Test gradient computation for line (should be constant)"""
        # Line x + y - 1 = 0 has constant gradient (1, 1)
        test_points = [(0.0, 1.0), (1.0, 0.0), (0.5, 0.5), (2.0, -1.0)]
        
        for x, y in test_points:
            grad_x, grad_y = self.line.gradient(x, y)
            assert abs(grad_x - 1.0) < 1e-10
            assert abs(grad_y - 1.0) < 1e-10
    
    def test_gradient_parabola_variable(self):
        """Test gradient computation for parabola with variable gradient"""
        # Parabola y - x^2 = 0 has gradient (-2x, 1)
        
        # At x = 0, gradient should be (0, 1)
        grad_x, grad_y = self.parabola.gradient(0.0, 0.0)
        assert abs(grad_x - 0.0) < 1e-10
        assert abs(grad_y - 1.0) < 1e-10
        
        # At x = 1, gradient should be (-2, 1)
        grad_x, grad_y = self.parabola.gradient(1.0, 1.0)
        assert abs(grad_x - (-2.0)) < 1e-10
        assert abs(grad_y - 1.0) < 1e-10
        
        # At x = -2, gradient should be (4, 1)
        grad_x, grad_y = self.parabola.gradient(-2.0, 4.0)
        assert abs(grad_x - 4.0) < 1e-10
        assert abs(grad_y - 1.0) < 1e-10
    
    def test_gradient_returns_floats(self):
        """Test that gradient always returns float values"""
        grad_x, grad_y = self.circle.gradient(1.0, 0.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)
    
    def test_gradient_zero_at_origin_for_centered_curve(self):
        """Test gradient behavior at singular points"""
        # Create a curve with zero gradient at origin: x^2 + y^2 = 0
        x, y = sp.symbols('x y')
        point_curve = ImplicitCurve(x**2 + y**2, variables=(x, y))
        
        grad_x, grad_y = point_curve.gradient(0.0, 0.0)
        assert abs(grad_x) < 1e-10
        assert abs(grad_y) < 1e-10


class TestImplicitCurveNormal:
    """Test ImplicitCurve normal method - Sprint 1 Task GEO-S1-T4"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        
        # Unit circle: x^2 + y^2 - 1 = 0
        self.circle_expr = x**2 + y**2 - 1
        self.circle = ImplicitCurve(self.circle_expr, variables=(x, y))
        
        # Line: x + y - 1 = 0
        self.line_expr = x + y - 1
        self.line = ImplicitCurve(self.line_expr, variables=(x, y))
    
    def test_normal_is_unit_length(self):
        """Test that normal vector has unit length"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
        
        for x, y in test_points:
            nx, ny = self.circle.normal(x, y)
            magnitude = np.sqrt(nx**2 + ny**2)
            assert abs(magnitude - 1.0) < 1e-10
    
    def test_normal_direction_circle(self):
        """Test normal direction for circle (should point outward)"""
        # At point (1, 0), normal should be (1, 0) - pointing outward
        nx, ny = self.circle.normal(1.0, 0.0)
        assert abs(nx - 1.0) < 1e-10
        assert abs(ny - 0.0) < 1e-10
        
        # At point (0, 1), normal should be (0, 1) - pointing outward
        nx, ny = self.circle.normal(0.0, 1.0)
        assert abs(nx - 0.0) < 1e-10
        assert abs(ny - 1.0) < 1e-10
        
        # At point (-1, 0), normal should be (-1, 0) - pointing outward
        nx, ny = self.circle.normal(-1.0, 0.0)
        assert abs(nx - (-1.0)) < 1e-10
        assert abs(ny - 0.0) < 1e-10
    
    def test_normal_direction_line(self):
        """Test normal direction for line"""
        # Line x + y - 1 = 0 has gradient (1, 1), so normal is (1/√2, 1/√2)
        expected_component = 1.0 / np.sqrt(2.0)
        
        test_points = [(0.0, 1.0), (1.0, 0.0), (0.5, 0.5)]
        
        for x, y in test_points:
            nx, ny = self.line.normal(x, y)
            assert abs(nx - expected_component) < 1e-10
            assert abs(ny - expected_component) < 1e-10
    
    def test_normal_returns_floats(self):
        """Test that normal always returns float values"""
        nx, ny = self.circle.normal(1.0, 0.0)
        assert isinstance(nx, float)
        assert isinstance(ny, float)
    
    def test_normal_raises_error_for_zero_gradient(self):
        """Test that normal raises ValueError for zero gradient"""
        # Create a curve with zero gradient at origin
        x, y = sp.symbols('x y')
        point_curve = ImplicitCurve(x**2 + y**2, variables=(x, y))
        
        with pytest.raises(ValueError, match="Normal undefined.*zero gradient"):
            point_curve.normal(0.0, 0.0)
    
    def test_normal_consistent_with_gradient(self):
        """Test that normal is normalized gradient"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for x, y in test_points:
            # Get gradient and normal
            grad_x, grad_y = self.circle.gradient(x, y)
            nx, ny = self.circle.normal(x, y)
            
            # Normal should be normalized gradient
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            expected_nx = grad_x / grad_magnitude
            expected_ny = grad_y / grad_magnitude
            
            assert abs(nx - expected_nx) < 1e-10
            assert abs(ny - expected_ny) < 1e-10


class TestImplicitCurveSerialization:
    """Test ImplicitCurve serialization methods - Sprint 1 Task GEO-S1-T6"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        
        # Various test curves
        self.circle = ImplicitCurve(x**2 + y**2 - 1, variables=(x, y))
        self.line = ImplicitCurve(x + y - 1, variables=(x, y))
        self.parabola = ImplicitCurve(y - x**2, variables=(x, y))
        
        # Complex expression
        self.complex_curve = ImplicitCurve(x**3 + y**3 - 3*x*y, variables=(x, y))
    
    def test_to_dict_basic_structure(self):
        """Test that to_dict returns proper dictionary structure"""
        data = self.circle.to_dict()
        
        # Check required fields
        assert isinstance(data, dict)
        assert "type" in data
        assert "expression" in data
        assert "variables" in data
        
        # Check field values
        assert data["type"] == "ImplicitCurve"
        assert isinstance(data["expression"], str)
        assert isinstance(data["variables"], list)
        assert len(data["variables"]) == 2
    
    def test_to_dict_expression_serialization(self):
        """Test that expressions are properly serialized to strings"""
        data = self.circle.to_dict()
        
        # Expression should be serializable string
        assert "x**2 + y**2 - 1" in data["expression"] or "x^2 + y^2 - 1" in data["expression"]
        
        # Variables should be string representations
        assert data["variables"] == ["x", "y"]
    
    def test_from_dict_basic_reconstruction(self):
        """Test basic reconstruction from dictionary"""
        # Serialize and deserialize
        data = self.circle.to_dict()
        reconstructed = ImplicitCurve.from_dict(data)
        
        # Check that it's a valid ImplicitCurve
        assert isinstance(reconstructed, ImplicitCurve)
        assert len(reconstructed.variables) == 2
        assert str(reconstructed.variables[0]) == "x"
        assert str(reconstructed.variables[1]) == "y"
    
    def test_round_trip_functional_equivalence(self):
        """Test that round-trip preserves functional behavior"""
        test_curves = [self.circle, self.line, self.parabola, self.complex_curve]
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (-1.0, -1.0)]
        
        for curve in test_curves:
            # Serialize and deserialize
            data = curve.to_dict()
            reconstructed = ImplicitCurve.from_dict(data)
            
            # Test that evaluate gives same results
            for x, y in test_points:
                original_val = curve.evaluate(x, y)
                reconstructed_val = reconstructed.evaluate(x, y)
                assert abs(original_val - reconstructed_val) < 1e-10
    
    def test_round_trip_gradient_equivalence(self):
        """Test that round-trip preserves gradient computation"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        # Serialize and deserialize circle
        data = self.circle.to_dict()
        reconstructed = ImplicitCurve.from_dict(data)
        
        # Test that gradient gives same results
        for x, y in test_points:
            orig_grad = self.circle.gradient(x, y)
            recon_grad = reconstructed.gradient(x, y)
            
            assert abs(orig_grad[0] - recon_grad[0]) < 1e-10
            assert abs(orig_grad[1] - recon_grad[1]) < 1e-10
    
    def test_round_trip_normal_equivalence(self):
        """Test that round-trip preserves normal computation"""
        test_points = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]
        
        # Serialize and deserialize circle
        data = self.circle.to_dict()
        reconstructed = ImplicitCurve.from_dict(data)
        
        # Test that normal gives same results
        for x, y in test_points:
            orig_normal = self.circle.normal(x, y)
            recon_normal = reconstructed.normal(x, y)
            
            assert abs(orig_normal[0] - recon_normal[0]) < 1e-10
            assert abs(orig_normal[1] - recon_normal[1]) < 1e-10
    
    def test_from_dict_invalid_data_handling(self):
        """Test that from_dict handles invalid data appropriately"""
        # Test with non-dictionary
        with pytest.raises(ValueError, match="Data must be a dictionary"):
            ImplicitCurve.from_dict("not a dict")
        
        # Test with wrong type
        with pytest.raises(ValueError, match="Invalid type"):
            ImplicitCurve.from_dict({"type": "WrongType", "expression": "x + y"})
        
        # Test with missing expression
        with pytest.raises(ValueError, match="Missing required field: expression"):
            ImplicitCurve.from_dict({"type": "ImplicitCurve"})
        
        # Test with invalid expression
        with pytest.raises(ValueError, match="Failed to parse expression"):
            ImplicitCurve.from_dict({
                "type": "ImplicitCurve",
                "expression": "invalid_expression_syntax!!!"
            })
    
    def test_custom_variables_serialization(self):
        """Test serialization with custom variable names"""
        # Create curve with custom variables
        u, v = sp.symbols('u v')
        custom_curve = ImplicitCurve(u**2 + v**2 - 4, variables=(u, v))
        
        # Round-trip test
        data = custom_curve.to_dict()
        reconstructed = ImplicitCurve.from_dict(data)
        
        # Check variables are preserved
        assert str(reconstructed.variables[0]) == "u"
        assert str(reconstructed.variables[1]) == "v"
        
        # Check functional equivalence
        test_points = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.0)]
        for u_val, v_val in test_points:
            orig_val = custom_curve.evaluate(u_val, v_val)
            recon_val = reconstructed.evaluate(u_val, v_val)
            assert abs(orig_val - recon_val) < 1e-10
    
    def test_serialization_with_complex_expressions(self):
        """Test serialization with complex mathematical expressions"""
        x, y = sp.symbols('x y')
        
        # Complex expressions to test
        complex_expressions = [
            sp.sin(x) + sp.cos(y) - 1,
            sp.exp(x**2 + y**2) - 2,
            x**4 + y**4 - 2*x**2*y**2 - 1,
            sp.log(x**2 + y**2 + 1) - 1
        ]
        
        for expr in complex_expressions:
            curve = ImplicitCurve(expr, variables=(x, y))
            
            # Round-trip test
            data = curve.to_dict()
            reconstructed = ImplicitCurve.from_dict(data)
            
            # Test functional equivalence at a few points
            test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
            for x_val, y_val in test_points:
                try:
                    orig_val = curve.evaluate(x_val, y_val)
                    recon_val = reconstructed.evaluate(x_val, y_val)
                    assert abs(orig_val - recon_val) < 1e-10
                except (ValueError, OverflowError):
                    # Some complex expressions may have domain issues
                    # Just ensure both raise the same error
                    with pytest.raises((ValueError, OverflowError)):
                        reconstructed.evaluate(x_val, y_val)
