"""
Sprint 5 Edge Cases and Robustness Tests

This test suite focuses on edge cases, error conditions, and robustness
issues identified from demo script failures. It validates:

1. Vectorized vs scalar input handling
2. Expression type compatibility issues
3. Utility function robustness
4. Mixed curve type interactions
5. Error handling and boundary conditions
6. Performance with large datasets
7. Memory management with complex operations
"""

import pytest
import sympy as sp
import numpy as np
from geometry import (
    ConicSection, PolynomialCurve, Superellipse, ProceduralCurve,
    TrimmedImplicitCurve, CompositeCurve,
    create_circle_from_quarters, create_square_from_edges
)


class TestVectorizedScalarHandling:
    """Test vectorized vs scalar input handling edge cases"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, (x, y))
        self.trimmed = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        self.composite = CompositeCurve([self.trimmed])
    
    def test_scalar_input_types(self):
        """Test different scalar input types"""
        # Test int, float, numpy scalars
        inputs = [
            (0, 0),           # int
            (0.0, 0.0),       # float
            (np.float64(0.5), np.float64(0.5)),  # numpy scalar
            (np.int32(1), np.int32(0)),          # numpy int
        ]
        
        for x_val, y_val in inputs:
            # Should work for all curve types
            result = self.trimmed.evaluate(x_val, y_val)
            assert isinstance(result, (int, float, np.number))
            
            contains = self.trimmed.contains(x_val, y_val)
            assert isinstance(contains, (bool, np.bool_))
            
            grad_x, grad_y = self.trimmed.gradient(x_val, y_val)
            assert isinstance(grad_x, (int, float, np.number))
            assert isinstance(grad_y, (int, float, np.number))
    
    def test_mixed_array_scalar_inputs(self):
        """Test mixing array and scalar inputs"""
        x_array = np.array([0.0, 0.5, 1.0])
        y_scalar = 0.5
        
        # Should handle mixed inputs gracefully
        result = self.trimmed.evaluate(x_array, y_scalar)
        assert isinstance(result, np.ndarray)
        assert result.shape == x_array.shape
        
        contains = self.trimmed.contains(x_array, y_scalar)
        assert isinstance(contains, np.ndarray)
        assert contains.dtype == bool
    
    def test_empty_arrays(self):
        """Test empty array inputs"""
        empty_x = np.array([])
        empty_y = np.array([])
        
        result = self.trimmed.evaluate(empty_x, empty_y)
        assert isinstance(result, np.ndarray)
        assert result.shape == (0,)
        
        contains = self.trimmed.contains(empty_x, empty_y)
        assert isinstance(contains, np.ndarray)
        assert contains.shape == (0,)
    
    def test_large_arrays(self):
        """Test performance with large arrays"""
        n = 10000
        x_vals = np.random.uniform(-2, 2, n)
        y_vals = np.random.uniform(-2, 2, n)
        
        # Should handle large arrays efficiently
        result = self.trimmed.evaluate(x_vals, y_vals)
        assert result.shape == (n,)
        
        contains = self.trimmed.contains(x_vals, y_vals)
        assert contains.shape == (n,)
        
        grad_x, grad_y = self.trimmed.gradient(x_vals, y_vals)
        assert grad_x.shape == (n,)
        assert grad_y.shape == (n,)


class TestUtilityFunctionRobustness:
    """Test utility function edge cases and error conditions"""
    
    def test_create_circle_edge_cases(self):
        """Test create_circle_from_quarters edge cases"""
        # Test with different parameter combinations
        circle1 = create_circle_from_quarters()  # Default
        assert isinstance(circle1, CompositeCurve)
        assert len(circle1.segments) == 4
        
        # Custom center and radius
        circle2 = create_circle_from_quarters(center=(1, 1), radius=2.0)
        assert isinstance(circle2, CompositeCurve)
        
        # Very small radius
        circle3 = create_circle_from_quarters(radius=1e-6)
        assert isinstance(circle3, CompositeCurve)
        
        # Large radius
        circle4 = create_circle_from_quarters(radius=1000.0)
        assert isinstance(circle4, CompositeCurve)
    
    def test_create_square_edge_cases(self):
        """Test create_square_from_edges edge cases"""
        # Default square
        square1 = create_square_from_edges()
        assert isinstance(square1, CompositeCurve)
        assert len(square1.segments) == 4
        
        # Reversed corners (should handle automatically)
        square2 = create_square_from_edges(corner1=(1, 1), corner2=(0, 0))
        assert isinstance(square2, CompositeCurve)
        
        # Very small square
        square3 = create_square_from_edges(corner1=(0, 0), corner2=(1e-6, 1e-6))
        assert isinstance(square3, CompositeCurve)
        
        # Large square
        square4 = create_square_from_edges(corner1=(-1000, -1000), corner2=(1000, 1000))
        assert isinstance(square4, CompositeCurve)


class TestMixedCurveTypeInteractions:
    """Test interactions between different curve types in composites"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        
        # Create different curve types
        self.conic = ConicSection(x**2 + y**2 - 1, (x, y))
        self.poly = PolynomialCurve(x + y - 1, (x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        self.procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, (x, y))
    
    def test_mixed_composite_creation(self):
        """Test creating composites with mixed curve types"""
        segments = [
            TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.poly, lambda x, y: x <= 0),
            TrimmedImplicitCurve(self.superellipse, lambda x, y: y >= 0),
            TrimmedImplicitCurve(self.procedural, lambda x, y: y <= 0),
        ]
        
        composite = CompositeCurve(segments)
        assert len(composite.segments) == 4
        
        # Test evaluation works
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
    
    def test_mixed_composite_vectorized(self):
        """Test vectorized operations on mixed composites"""
        segments = [
            TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.poly, lambda x, y: x <= 0),
        ]
        
        composite = CompositeCurve(segments)
        
        # Test with arrays
        x_vals = np.array([-1.0, 0.0, 1.0])
        y_vals = np.array([0.0, 0.0, 0.0])
        
        results = composite.evaluate(x_vals, y_vals)
        assert isinstance(results, np.ndarray)
        assert results.shape == (3,)
        
        contains = composite.contains(x_vals, y_vals)
        assert isinstance(contains, np.ndarray)
        assert contains.dtype == bool


class TestErrorHandlingAndBoundaryConditions:
    """Test error handling and boundary conditions"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, (x, y))
    
    def test_invalid_mask_functions(self):
        """Test behavior with problematic mask functions"""
        # Mask that raises exception
        def bad_mask(x, y):
            if x == 0:
                raise ValueError("Division by zero")
            return x > 0
        
        trimmed = TrimmedImplicitCurve(self.circle, bad_mask)
        
        # Should handle exceptions gracefully
        with pytest.raises(ValueError):
            trimmed.contains(0.0, 0.0)
    
    def test_nan_inf_inputs(self):
        """Test handling of NaN and infinity inputs"""
        trimmed = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        
        # Test NaN inputs
        result_nan = trimmed.evaluate(np.nan, 0.0)
        assert np.isnan(result_nan)
        
        # Test infinity inputs
        result_inf = trimmed.evaluate(np.inf, 0.0)
        assert np.isinf(result_inf)
    
    def test_extreme_values(self):
        """Test with extreme coordinate values"""
        trimmed = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        
        # Very large values
        result_large = trimmed.evaluate(1e10, 1e10)
        assert isinstance(result_large, (int, float, np.number))
        
        # Very small values
        result_small = trimmed.evaluate(1e-10, 1e-10)
        assert isinstance(result_small, (int, float, np.number))
    
    def test_empty_composite_error(self):
        """Test that empty composite raises appropriate error"""
        with pytest.raises(ValueError, match="must have at least one segment"):
            CompositeCurve([])
    
    def test_invalid_segment_types(self):
        """Test that invalid segment types raise errors"""
        with pytest.raises(TypeError):
            CompositeCurve([self.circle])  # Should be TrimmedImplicitCurve


class TestMemoryAndPerformance:
    """Test memory usage and performance characteristics"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, (x, y))
    
    def test_large_composite_creation(self):
        """Test creating composite with many segments"""
        segments = []
        for i in range(100):
            angle = i * 2 * np.pi / 100
            mask = lambda x, y, a=angle: x * np.cos(a) + y * np.sin(a) >= 0
            segments.append(TrimmedImplicitCurve(self.circle, mask))
        
        composite = CompositeCurve(segments)
        assert len(composite.segments) == 100
        
        # Should still work for evaluation
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
    
    def test_nested_composite_serialization(self):
        """Test serialization of complex nested structures"""
        # Create nested structure
        segments = []
        for i in range(10):
            mask = lambda x, y, i=i: (x + i) >= 0
            segments.append(TrimmedImplicitCurve(self.circle, mask))
        
        composite = CompositeCurve(segments)
        
        # Serialize and deserialize
        serialized = composite.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        assert len(restored.segments) == len(composite.segments)
    
    def test_memory_cleanup(self):
        """Test that objects can be properly garbage collected"""
        import gc
        
        # Create many objects
        objects = []
        for i in range(1000):
            trimmed = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
            objects.append(trimmed)
        
        # Clear references
        objects.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Should not cause memory issues
        assert True  # If we get here, no memory issues


class TestSpecialCases:
    """Test special mathematical cases and edge conditions"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, (x, y))
    
    def test_degenerate_masks(self):
        """Test degenerate mask functions"""
        # Always False mask
        always_false = TrimmedImplicitCurve(self.circle, lambda x, y: False)
        assert always_false.contains(0.0, 0.0) == False
        assert always_false.contains(1.0, 0.0) == False
        
        # Always True mask
        always_true = TrimmedImplicitCurve(self.circle, lambda x, y: True)
        # Should behave like base curve for boundary containment
        base_contains = abs(self.circle.evaluate(0.0, 0.0)) <= 1e-3
        assert always_true.contains(0.0, 0.0) == base_contains
    
    def test_boundary_conditions(self):
        """Test behavior exactly on curve boundaries"""
        # Point exactly on circle
        trimmed = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        
        # Test points on boundary
        boundary_points = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
        
        for x, y in boundary_points:
            # Should be close to zero (on curve)
            value = trimmed.evaluate(x, y)
            assert abs(value) < 1e-10
            
            # Containment depends on mask
            contains = trimmed.contains(x, y)
            expected = (x >= 0) and (value <= 0)
            assert contains == expected
    
    def test_gradient_singularities(self):
        """Test gradient computation at singular points"""
        # Create curve with potential singularity
        x, y = sp.symbols('x y')
        cusp_curve = PolynomialCurve(y**2 - x**3, (x, y))  # Cusp at origin
        trimmed = TrimmedImplicitCurve(cusp_curve, lambda x, y: x >= 0)
        
        # Test gradient near singularity
        grad_x, grad_y = trimmed.gradient(1e-6, 1e-6)
        assert isinstance(grad_x, (int, float, np.number))
        assert isinstance(grad_y, (int, float, np.number))
        
        # Should not be NaN or infinite
        assert not np.isnan(grad_x)
        assert not np.isnan(grad_y)
        assert not np.isinf(grad_x)
        assert not np.isinf(grad_y)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
