"""
Test suite for BaseField hierarchy and scalar field classes.

This module tests the BaseField abstract class and its concrete implementations:
- CurveField (wrapping ImplicitCurve as scalar field)
- BlendedField (algebraic combinations of scalar fields)
- Serialization and deserialization
- Gradient computation and level set extraction
"""

import pytest
import numpy as np
import sympy as sp
from geometry import (
    BaseField, CurveField, BlendedField,
    ImplicitCurve, ConicSection, PolynomialCurve
)


class TestBaseField:
    """Test the abstract BaseField class."""
    
    def test_base_field_is_abstract(self):
        """Test that BaseField cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseField()


class TestCurveField:
    """Test the CurveField class."""
    
    @pytest.fixture
    def circle_curve(self):
        """Create a simple circle curve for testing."""
        x, y = sp.symbols('x y')
        expr = x**2 + y**2 - 1  # Unit circle
        return ImplicitCurve(expr, (x, y))
    
    @pytest.fixture
    def conic_curve(self):
        """Create a conic section curve for testing."""
        x, y = sp.symbols('x y')
        expr = x**2 + y**2 - 4  # Circle: x^2 + y^2 = 4
        return ConicSection(expr, (x, y))
    
    def test_init(self, circle_curve):
        """Test CurveField initialization."""
        field = CurveField(circle_curve)
        assert field.curve is circle_curve
    
    def test_init_invalid_curve(self):
        """Test CurveField initialization with invalid curve."""
        with pytest.raises(TypeError, match="curve must be an ImplicitCurve instance"):
            CurveField("not a curve")
        
        with pytest.raises(TypeError, match="curve must be an ImplicitCurve instance"):
            CurveField(None)
    
    def test_evaluate_scalar(self, circle_curve):
        """Test scalar evaluation of CurveField."""
        field = CurveField(circle_curve)
        
        # Test point inside circle (should be negative)
        result = field.evaluate(0.0, 0.0)
        assert isinstance(result, float)
        assert result < 0
        
        # Test point on circle (should be close to zero)
        result = field.evaluate(1.0, 0.0)
        assert isinstance(result, float)
        assert abs(result) < 1e-10
        
        # Test point outside circle (should be positive)
        result = field.evaluate(2.0, 0.0)
        assert isinstance(result, float)
        assert result > 0
    
    def test_evaluate_vectorized(self, circle_curve):
        """Test vectorized evaluation of CurveField."""
        field = CurveField(circle_curve)
        
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 0.0, 0.0])
        
        result = field.evaluate(x, y)
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        
        # Check signs: inside, on boundary, outside
        assert result[0] < 0
        assert abs(result[1]) < 1e-10
        assert result[2] > 0
    
    def test_gradient_scalar(self, circle_curve):
        """Test scalar gradient computation."""
        field = CurveField(circle_curve)
        
        grad_x, grad_y = field.gradient(1.0, 1.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)
        
        # For circle x^2 + y^2 - 1, gradient is (2x, 2y)
        expected_grad_x = 2.0
        expected_grad_y = 2.0
        assert abs(grad_x - expected_grad_x) < 1e-10
        assert abs(grad_y - expected_grad_y) < 1e-10
    
    def test_gradient_vectorized(self, circle_curve):
        """Test vectorized gradient computation."""
        field = CurveField(circle_curve)
        
        x = np.array([1.0, 0.0])
        y = np.array([0.0, 1.0])
        
        grad_x, grad_y = field.gradient(x, y)
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x.shape
        assert grad_y.shape == y.shape
        
        # Check expected gradients
        np.testing.assert_allclose(grad_x, [2.0, 0.0], atol=1e-10)
        np.testing.assert_allclose(grad_y, [0.0, 2.0], atol=1e-10)
    
    def test_level_set(self, circle_curve):
        """Test level set extraction."""
        field = CurveField(circle_curve)
        
        # Level set at 0 should be the original curve
        level_curve = field.level_set(0.0)
        assert hasattr(level_curve, 'evaluate')
        
        # Test that level curve evaluates correctly
        assert abs(level_curve.evaluate(1.0, 0.0)) < 1e-10
    
    def test_serialization(self, circle_curve):
        """Test CurveField serialization."""
        field = CurveField(circle_curve)
        data = field.to_dict()
        
        assert data['type'] == 'CurveField'
        assert 'curve' in data
        
        # Test round-trip
        reconstructed = CurveField.from_dict(data)
        assert isinstance(reconstructed, CurveField)
        
        # Test that reconstructed field behaves the same
        test_points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        for x, y in test_points:
            original_val = field.evaluate(x, y)
            reconstructed_val = reconstructed.evaluate(x, y)
            assert abs(original_val - reconstructed_val) < 1e-10
    
    def test_from_dict_invalid_type(self):
        """Test CurveField.from_dict with invalid type."""
        data = {'type': 'WrongType'}
        with pytest.raises(ValueError, match="does not represent a CurveField"):
            CurveField.from_dict(data)
    
    def test_with_different_curve_types(self, conic_curve):
        """Test CurveField with different curve types."""
        field = CurveField(conic_curve)
        
        # Test evaluation
        result = field.evaluate(0.0, 0.0)
        assert isinstance(result, float)
        
        # Test gradient
        grad_x, grad_y = field.gradient(1.0, 1.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)


class TestBlendedField:
    """Test the BlendedField class."""
    
    @pytest.fixture
    def field1(self):
        """Create first test field."""
        x, y = sp.symbols('x y')
        curve1 = ImplicitCurve(x**2 + y**2 - 1, (x, y))  # Unit circle
        return CurveField(curve1)
    
    @pytest.fixture
    def field2(self):
        """Create second test field."""
        x, y = sp.symbols('x y')
        curve2 = ImplicitCurve((x-2)**2 + y**2 - 1, (x, y))  # Circle at (2,0)
        return CurveField(curve2)
    
    def test_init_add(self, field1, field2):
        """Test BlendedField initialization with addition."""
        blended = BlendedField([field1, field2], 'add')
        assert blended.fields == [field1, field2]
        assert blended.operation == 'add'
    
    def test_init_invalid_operation(self, field1, field2):
        """Test BlendedField initialization with invalid operation."""
        with pytest.raises(ValueError, match="Unsupported operation"):
            BlendedField([field1, field2], 'invalid_op')
    
    def test_init_insufficient_fields(self, field1):
        """Test BlendedField initialization with insufficient fields."""
        with pytest.raises(ValueError, match="At least two fields are required"):
            BlendedField([field1], 'add')
        
        with pytest.raises(ValueError, match="At least two fields are required"):
            BlendedField([], 'add')
    
    def test_init_invalid_field_types(self, field1):
        """Test BlendedField initialization with invalid field types."""
        with pytest.raises(TypeError, match="All fields must be BaseField instances"):
            BlendedField([field1, "not a field"], 'add')
    
    def test_evaluate_add(self, field1, field2):
        """Test evaluation with addition operation."""
        blended = BlendedField([field1, field2], 'add')
        
        # Test at origin: should be sum of both field values
        result = blended.evaluate(0.0, 0.0)
        expected = field1.evaluate(0.0, 0.0) + field2.evaluate(0.0, 0.0)
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_subtract(self, field1, field2):
        """Test evaluation with subtraction operation."""
        blended = BlendedField([field1, field2], 'subtract')
        
        result = blended.evaluate(0.0, 0.0)
        expected = field1.evaluate(0.0, 0.0) - field2.evaluate(0.0, 0.0)
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_multiply(self, field1, field2):
        """Test evaluation with multiplication operation."""
        blended = BlendedField([field1, field2], 'multiply')
        
        result = blended.evaluate(0.0, 0.0)
        expected = field1.evaluate(0.0, 0.0) * field2.evaluate(0.0, 0.0)
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_divide(self, field1, field2):
        """Test evaluation with division operation."""
        blended = BlendedField([field1, field2], 'divide')
        
        # Test at a point where field2 is non-zero
        result = blended.evaluate(1.0, 1.0)
        val1 = field1.evaluate(1.0, 1.0)
        val2 = field2.evaluate(1.0, 1.0)
        expected = val1 / val2 if abs(val2) > 1e-10 else 0.0
        
        if abs(val2) > 1e-10:
            assert abs(result - expected) < 1e-10
        else:
            assert result == 0.0  # Division by zero handling
    
    def test_evaluate_min(self, field1, field2):
        """Test evaluation with minimum operation."""
        blended = BlendedField([field1, field2], 'min')
        
        result = blended.evaluate(0.0, 0.0)
        val1 = field1.evaluate(0.0, 0.0)
        val2 = field2.evaluate(0.0, 0.0)
        expected = min(val1, val2)
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_max(self, field1, field2):
        """Test evaluation with maximum operation."""
        blended = BlendedField([field1, field2], 'max')
        
        result = blended.evaluate(0.0, 0.0)
        val1 = field1.evaluate(0.0, 0.0)
        val2 = field2.evaluate(0.0, 0.0)
        expected = max(val1, val2)
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_average(self, field1, field2):
        """Test evaluation with average operation."""
        blended = BlendedField([field1, field2], 'average')
        
        result = blended.evaluate(0.0, 0.0)
        val1 = field1.evaluate(0.0, 0.0)
        val2 = field2.evaluate(0.0, 0.0)
        expected = (val1 + val2) / 2
        assert abs(result - expected) < 1e-10
    
    def test_evaluate_vectorized(self, field1, field2):
        """Test vectorized evaluation."""
        blended = BlendedField([field1, field2], 'add')
        
        x = np.array([0.0, 1.0])
        y = np.array([0.0, 0.0])
        
        result = blended.evaluate(x, y)
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        
        # Check individual values
        for i in range(len(x)):
            expected = field1.evaluate(x[i], y[i]) + field2.evaluate(x[i], y[i])
            assert abs(result[i] - expected) < 1e-10
    
    def test_gradient_analytical(self, field1, field2):
        """Test gradient computation for analytical operations."""
        blended = BlendedField([field1, field2], 'add')
        
        grad_x, grad_y = blended.gradient(1.0, 1.0)
        
        # For addition, gradient should be sum of individual gradients
        grad1_x, grad1_y = field1.gradient(1.0, 1.0)
        grad2_x, grad2_y = field2.gradient(1.0, 1.0)
        
        expected_grad_x = grad1_x + grad2_x
        expected_grad_y = grad1_y + grad2_y
        
        assert abs(grad_x - expected_grad_x) < 1e-10
        assert abs(grad_y - expected_grad_y) < 1e-10
    
    def test_gradient_numerical_fallback(self, field1, field2):
        """Test numerical gradient computation for non-analytical operations."""
        blended = BlendedField([field1, field2], 'min')
        
        grad_x, grad_y = blended.gradient(1.0, 1.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)
        # Values will be computed numerically, so just check they're finite
        assert np.isfinite(grad_x)
        assert np.isfinite(grad_y)
    
    def test_level_set(self, field1, field2):
        """Test level set extraction."""
        blended = BlendedField([field1, field2], 'add')
        
        level_curve = blended.level_set(0.0)
        assert hasattr(level_curve, 'evaluate')
    
    def test_serialization(self, field1, field2):
        """Test BlendedField serialization."""
        blended = BlendedField([field1, field2], 'multiply')
        data = blended.to_dict()
        
        assert data['type'] == 'BlendedField'
        assert data['operation'] == 'multiply'
        assert 'fields' in data
        assert len(data['fields']) == 2
        
        # Test round-trip
        reconstructed = BlendedField.from_dict(data)
        assert isinstance(reconstructed, BlendedField)
        assert reconstructed.operation == 'multiply'
        assert len(reconstructed.fields) == 2
        
        # Test that reconstructed field behaves the same
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            original_val = blended.evaluate(x, y)
            reconstructed_val = reconstructed.evaluate(x, y)
            assert abs(original_val - reconstructed_val) < 1e-10
    
    def test_from_dict_invalid_type(self):
        """Test BlendedField.from_dict with invalid type."""
        data = {'type': 'WrongType'}
        with pytest.raises(ValueError, match="does not represent a BlendedField"):
            BlendedField.from_dict(data)
    
    def test_multiple_fields(self, field1, field2):
        """Test BlendedField with more than two fields."""
        x, y = sp.symbols('x y')
        curve3 = ImplicitCurve(x**2 + (y-2)**2 - 1, (x, y))  # Circle at (0,2)
        field3 = CurveField(curve3)
        
        blended = BlendedField([field1, field2, field3], 'add')
        
        result = blended.evaluate(0.0, 0.0)
        expected = (field1.evaluate(0.0, 0.0) + 
                   field2.evaluate(0.0, 0.0) + 
                   field3.evaluate(0.0, 0.0))
        assert abs(result - expected) < 1e-10
    
    def test_nested_blended_fields(self, field1, field2):
        """Test nesting BlendedField instances."""
        # Create a blended field
        blended1 = BlendedField([field1, field2], 'add')
        
        # Create another field to blend with
        x, y = sp.symbols('x y')
        curve3 = ImplicitCurve(x**2 + (y-2)**2 - 1, (x, y))
        field3 = CurveField(curve3)
        
        # Nest the blended fields
        nested = BlendedField([blended1, field3], 'multiply')
        
        result = nested.evaluate(0.0, 0.0)
        val_blended1 = blended1.evaluate(0.0, 0.0)
        val_field3 = field3.evaluate(0.0, 0.0)
        expected = val_blended1 * val_field3
        
        assert abs(result - expected) < 1e-10


class TestFieldEdgeCases:
    """Test edge cases and error conditions for field classes."""
    
    def test_curve_field_with_complex_expression(self):
        """Test CurveField with complex mathematical expressions."""
        x, y = sp.symbols('x y')
        # Complex expression with trigonometric and exponential terms
        expr = sp.sin(x) * sp.cos(y) + sp.exp(-x**2 - y**2) - 0.5
        curve = ImplicitCurve(expr, (x, y))
        field = CurveField(curve)
        
        # Should handle evaluation without errors
        result = field.evaluate(0.0, 0.0)
        assert isinstance(result, float)
        assert np.isfinite(result)
        
        # Should handle gradient computation
        grad_x, grad_y = field.gradient(0.0, 0.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)
        assert np.isfinite(grad_x)
        assert np.isfinite(grad_y)
    
    def test_blended_field_division_by_zero(self):
        """Test BlendedField division operation with zero divisor."""
        x, y = sp.symbols('x y')
        
        # Create a field that evaluates to zero at origin
        curve1 = ImplicitCurve(x**2 + y**2, (x, y))  # Zero at origin
        field1 = CurveField(curve1)
        
        # Create another field
        curve2 = ImplicitCurve(x**2 + y**2 - 1, (x, y))
        field2 = CurveField(curve2)
        
        # Test division where divisor is zero
        blended = BlendedField([field2, field1], 'divide')  # field2 / field1
        
        result = blended.evaluate(0.0, 0.0)
        assert result == 0.0  # Should handle division by zero gracefully
    
    def test_field_evaluation_with_nan(self):
        """Test field evaluation with NaN inputs."""
        x, y = sp.symbols('x y')
        curve = ImplicitCurve(x**2 + y**2 - 1, (x, y))
        field = CurveField(curve)
        
        # Test with NaN - behavior may vary but should not crash
        try:
            result = field.evaluate(float('nan'), 0.0)
            # Result may be NaN or handled gracefully
        except (ValueError, RuntimeError):
            # It's acceptable for this to raise an exception
            pass
    
    def test_field_evaluation_with_infinity(self):
        """Test field evaluation with infinite inputs."""
        x, y = sp.symbols('x y')
        curve = ImplicitCurve(x**2 + y**2 - 1, (x, y))
        field = CurveField(curve)
        
        # Test with infinity
        result = field.evaluate(float('inf'), 0.0)
        assert result == float('inf')  # x^2 + 0^2 - 1 = inf


class TestFieldPerformance:
    """Test performance characteristics of field classes."""
    
    def test_vectorized_vs_scalar_performance(self):
        """Test that vectorized operations are equivalent to scalar loops."""
        x, y = sp.symbols('x y')
        curve = ImplicitCurve(x**2 + y**2 - 1, (x, y))
        field = CurveField(curve)
        
        # Create test data
        n_points = 50
        x_vals = np.random.uniform(-2, 2, n_points)
        y_vals = np.random.uniform(-2, 2, n_points)
        
        # Test vectorized evaluation
        result_vectorized = field.evaluate(x_vals, y_vals)
        
        # Test scalar evaluation
        result_scalar = np.array([field.evaluate(x_vals[i], y_vals[i]) 
                                 for i in range(n_points)])
        
        # Results should be equivalent
        np.testing.assert_allclose(result_vectorized, result_scalar, atol=1e-12)
    
    def test_blended_field_performance(self):
        """Test performance of blended field operations."""
        x, y = sp.symbols('x y')
        
        # Create multiple fields
        fields = []
        for i in range(5):
            expr = (x - i)**2 + y**2 - 1
            curve = ImplicitCurve(expr, (x, y))
            fields.append(CurveField(curve))
        
        # Create blended field
        blended = BlendedField(fields, 'add')
        
        # Test evaluation at multiple points
        test_points = [(0.0, 0.0), (1.0, 1.0), (-1.0, -1.0), (2.0, 0.0)]
        
        for x_val, y_val in test_points:
            result = blended.evaluate(x_val, y_val)
            assert isinstance(result, float)
            assert np.isfinite(result)


if __name__ == "__main__":
    pytest.main([__file__])
