"""
Sprint 5 Expression Type Compatibility Tests

This test suite focuses on expression type compatibility issues identified
from demo script failures, particularly around:

1. SymPy expression type handling in CompositeCurve constructor
2. Mixed expression types in utility functions
3. Expression serialization/deserialization edge cases
4. Complex expression combinations
5. Type coercion and conversion issues
"""

import pytest
import sympy as sp
import numpy as np
from geometry import (
    ConicSection, PolynomialCurve, Superellipse, ProceduralCurve,
    TrimmedImplicitCurve, CompositeCurve,
    create_circle_from_quarters, create_square_from_edges
)


class TestExpressionTypeHandling:
    """Test expression type handling in CompositeCurve"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        self.x, self.y = x, y
        
        # Create curves with different expression types
        self.simple_poly = PolynomialCurve(x + y - 1, (x, y))
        self.complex_poly = PolynomialCurve(x**3 + y**3 - x*y - 1, (x, y))
        self.conic = ConicSection(x**2 + y**2 - 1, (x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # Create procedural with different function types
        self.proc_simple = ProceduralCurve(lambda x, y: x + y - 1, (x, y))
        self.proc_trig = ProceduralCurve(lambda x, y: np.sin(x) + np.cos(y), (x, y))
        self.proc_complex = ProceduralCurve(lambda x, y: np.exp(x) * np.log(abs(y) + 1), (x, y))
    
    def test_composite_with_different_expression_types(self):
        """Test CompositeCurve with different base expression types"""
        # Create segments with different base curve types
        segments = [
            TrimmedImplicitCurve(self.simple_poly, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.complex_poly, lambda x, y: x <= 0),
            TrimmedImplicitCurve(self.conic, lambda x, y: y >= 0),
            TrimmedImplicitCurve(self.superellipse, lambda x, y: y <= 0),
        ]
        
        # Should create successfully despite different expression types
        composite = CompositeCurve(segments)
        assert len(composite.segments) == 4
        
        # Should evaluate without errors
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        assert not np.isnan(result)
        assert not np.isinf(result)
    
    def test_composite_with_procedural_curves(self):
        """Test CompositeCurve with procedural curves that might cause expression issues"""
        segments = [
            TrimmedImplicitCurve(self.proc_simple, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.proc_trig, lambda x, y: x <= 0),
            TrimmedImplicitCurve(self.proc_complex, lambda x, y: y >= 0),
        ]
        
        # Should handle procedural curves without expression type issues
        composite = CompositeCurve(segments)
        assert len(composite.segments) == 3
        
        # Test evaluation at various points
        test_points = [(0.1, 0.1), (-0.1, 0.1), (0.1, -0.1), (-0.1, -0.1)]
        for x, y in test_points:
            result = composite.evaluate(x, y)
            assert isinstance(result, (int, float, np.number))
            # Should not be NaN (though might be large)
            assert not np.isnan(result)
    
    def test_expression_placeholder_handling(self):
        """Test that expression placeholder in CompositeCurve works correctly"""
        x, y = self.x, self.y
        
        # Create segments with very different expression complexities
        simple_segment = TrimmedImplicitCurve(
            PolynomialCurve(x - 1, (x, y)), 
            lambda x, y: True
        )
        
        complex_segment = TrimmedImplicitCurve(
            PolynomialCurve(x**5 + y**5 - x**3*y**2 - x*y**4 + x*y - 1, (x, y)),
            lambda x, y: True
        )
        
        # CompositeCurve should use first segment's expression as placeholder
        composite = CompositeCurve([simple_segment, complex_segment])
        
        # The placeholder expression should be from the first segment
        assert composite.expression == simple_segment.expression
        
        # But evaluation should use the actual composite logic
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))


class TestUtilityFunctionExpressionHandling:
    """Test expression handling in utility functions"""
    
    def test_create_circle_expression_types(self):
        """Test create_circle_from_quarters with different variable types"""
        # Test with default variables
        circle1 = create_circle_from_quarters()
        assert isinstance(circle1, CompositeCurve)
        
        # Test with custom variables
        u, v = sp.symbols('u v')
        circle2 = create_circle_from_quarters(variables=(u, v))
        assert isinstance(circle2, CompositeCurve)
        
        # Variables should be preserved
        assert circle2.variables == (u, v)
        
        # Should evaluate correctly
        result = circle2.evaluate(1.0, 0.0)
        assert isinstance(result, (int, float, np.number))
    
    def test_create_square_expression_types(self):
        """Test create_square_from_edges with different variable types"""
        # Test with default variables
        square1 = create_square_from_edges()
        assert isinstance(square1, CompositeCurve)
        
        # Test with custom variables
        s, t = sp.symbols('s t')
        square2 = create_square_from_edges(variables=(s, t))
        assert isinstance(square2, CompositeCurve)
        
        # Variables should be preserved
        assert square2.variables == (s, t)
        
        # Should evaluate correctly
        result = square2.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
    
    def test_utility_function_edge_coordinates(self):
        """Test utility functions with edge case coordinates"""
        # Very large coordinates
        circle_large = create_circle_from_quarters(center=(1e6, 1e6), radius=1e6)
        assert isinstance(circle_large, CompositeCurve)
        
        # Very small coordinates
        circle_small = create_circle_from_quarters(center=(1e-6, 1e-6), radius=1e-6)
        assert isinstance(circle_small, CompositeCurve)
        
        # Negative coordinates
        circle_neg = create_circle_from_quarters(center=(-100, -100), radius=50)
        assert isinstance(circle_neg, CompositeCurve)
        
        # All should evaluate without errors
        for circle in [circle_large, circle_small, circle_neg]:
            result = circle.evaluate(0.0, 0.0)
            assert isinstance(result, (int, float, np.number))
            assert not np.isnan(result)


class TestSerializationExpressionHandling:
    """Test serialization with complex expressions"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        
        # Create curves with increasingly complex expressions
        self.simple = PolynomialCurve(x + y - 1, (x, y))
        self.quadratic = PolynomialCurve(x**2 + y**2 - 1, (x, y))
        self.high_degree = PolynomialCurve(x**5 + y**5 - x**3*y**2 - 1, (x, y))
        
        # Create with special functions
        self.with_abs = PolynomialCurve(sp.Abs(x) + sp.Abs(y) - 1, (x, y))
        self.with_trig = PolynomialCurve(sp.sin(x) + sp.cos(y) - 1, (x, y))
    
    def test_complex_expression_serialization(self):
        """Test serialization of complex expressions in trimmed curves"""
        curves = [self.simple, self.quadratic, self.high_degree, self.with_abs]
        
        for base_curve in curves:
            trimmed = TrimmedImplicitCurve(base_curve, lambda x, y: x >= 0)
            
            # Should serialize without errors
            serialized = trimmed.to_dict()
            assert isinstance(serialized, dict)
            assert "base_curve" in serialized
            
            # Should deserialize without errors
            restored = TrimmedImplicitCurve.from_dict(serialized)
            assert isinstance(restored, TrimmedImplicitCurve)
            
            # Base curve should be functionally equivalent
            test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
            for x, y in test_points:
                orig_val = base_curve.evaluate(x, y)
                rest_val = restored.base_curve.evaluate(x, y)
                assert abs(orig_val - rest_val) < 1e-10
    
    def test_composite_complex_expression_serialization(self):
        """Test serialization of composite curves with complex expressions"""
        segments = [
            TrimmedImplicitCurve(self.simple, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.high_degree, lambda x, y: x <= 0),
            TrimmedImplicitCurve(self.with_abs, lambda x, y: y >= 0),
        ]
        
        composite = CompositeCurve(segments)
        
        # Should serialize complex composite
        serialized = composite.to_dict()
        assert isinstance(serialized, dict)
        assert len(serialized["segments"]) == 3
        
        # Should deserialize correctly
        restored = CompositeCurve.from_dict(serialized)
        assert isinstance(restored, CompositeCurve)
        assert len(restored.segments) == 3
        
        # Should maintain functional equivalence
        test_points = [(0.5, 0.5), (-0.5, 0.5), (0.5, -0.5)]
        for x, y in test_points:
            orig_val = composite.evaluate(x, y)
            rest_val = restored.evaluate(x, y)
            assert abs(orig_val - rest_val) < 1e-10


class TestMixedTypeOperations:
    """Test operations mixing different curve and expression types"""
    
    def setup_method(self):
        x, y = sp.symbols('x y')
        
        # Create diverse curve types
        self.conic = ConicSection(x**2 + y**2 - 1, (x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, (x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
        self.procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, (x, y))
    
    def test_mixed_type_composite_evaluation(self):
        """Test evaluation of composite with all curve types"""
        segments = [
            TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(self.poly, lambda x, y: x <= 0 and y >= 0),
            TrimmedImplicitCurve(self.superellipse, lambda x, y: x <= 0 and y <= 0),
            TrimmedImplicitCurve(self.procedural, lambda x, y: x >= 0 and y <= 0),
        ]
        
        composite = CompositeCurve(segments)
        
        # Test evaluation in each quadrant
        quadrant_points = [
            (0.5, 0.5),   # Q1 - Conic
            (-0.5, 0.5),  # Q2 - Polynomial
            (-0.5, -0.5), # Q3 - Superellipse
            (0.5, -0.5),  # Q4 - Procedural
        ]
        
        for x, y in quadrant_points:
            result = composite.evaluate(x, y)
            assert isinstance(result, (int, float, np.number))
            assert not np.isnan(result)
            assert not np.isinf(result)
            
            # Test gradient
            grad_x, grad_y = composite.gradient(x, y)
            assert isinstance(grad_x, (int, float, np.number))
            assert isinstance(grad_y, (int, float, np.number))
            assert not np.isnan(grad_x)
            assert not np.isnan(grad_y)
    
    def test_mixed_type_vectorized_operations(self):
        """Test vectorized operations on mixed type composites"""
        segments = [
            TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0),
            TrimmedImplicitCurve(self.poly, lambda x, y: x <= 0),
        ]
        
        composite = CompositeCurve(segments)
        
        # Test with various array sizes and types
        test_arrays = [
            (np.array([0.5]), np.array([0.5])),                    # Single element
            (np.array([0.5, -0.5]), np.array([0.5, 0.5])),        # Two elements
            (np.linspace(-1, 1, 10), np.linspace(-1, 1, 10)),      # Ten elements
            (np.random.uniform(-1, 1, 100), np.random.uniform(-1, 1, 100)),  # Large array
        ]
        
        for x_vals, y_vals in test_arrays:
            # Test evaluation
            results = composite.evaluate(x_vals, y_vals)
            assert isinstance(results, np.ndarray)
            assert results.shape == x_vals.shape
            assert not np.any(np.isnan(results))
            
            # Test containment
            contains = composite.contains(x_vals, y_vals)
            assert isinstance(contains, np.ndarray)
            assert contains.dtype == bool
            assert contains.shape == x_vals.shape
            
            # Test gradient
            grad_x, grad_y = composite.gradient(x_vals, y_vals)
            assert isinstance(grad_x, np.ndarray)
            assert isinstance(grad_y, np.ndarray)
            assert grad_x.shape == x_vals.shape
            assert grad_y.shape == y_vals.shape
            assert not np.any(np.isnan(grad_x))
            assert not np.any(np.isnan(grad_y))


class TestRobustnessUnderStress:
    """Test robustness under stress conditions"""
    
    def test_deeply_nested_operations(self):
        """Test deeply nested curve operations"""
        x, y = sp.symbols('x y')
        base = ConicSection(x**2 + y**2 - 1, (x, y))
        
        # Create deeply nested structure
        current = base
        for i in range(5):  # 5 levels of nesting
            trimmed = TrimmedImplicitCurve(current, lambda x, y, i=i: x >= -i*0.1)
            composite = CompositeCurve([trimmed])
            current = composite
        
        # Should still work
        result = current.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        assert not np.isnan(result)
    
    def test_extreme_parameter_values(self):
        """Test with extreme parameter values"""
        x, y = sp.symbols('x y')
        
        # Extreme superellipse parameters
        extreme_super = Superellipse(a=1e-6, b=1e6, n=100.0, variables=(x, y))
        trimmed = TrimmedImplicitCurve(extreme_super, lambda x, y: True)
        
        # Should handle extreme parameters
        result = trimmed.evaluate(1e-3, 1e-3)
        assert isinstance(result, (int, float, np.number))
        
        # Test with extreme coordinates
        result_extreme = trimmed.evaluate(1e10, 1e-10)
        assert isinstance(result_extreme, (int, float, np.number))
    
    def test_memory_intensive_operations(self):
        """Test memory-intensive operations"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        
        # Create many segments
        segments = []
        for i in range(50):
            mask = lambda x, y, i=i: x >= -1 + i*0.04  # Overlapping masks
            segments.append(TrimmedImplicitCurve(circle, mask))
        
        composite = CompositeCurve(segments)
        
        # Test with large arrays
        n = 1000
        x_vals = np.random.uniform(-2, 2, n)
        y_vals = np.random.uniform(-2, 2, n)
        
        # Should handle large composite with large arrays
        results = composite.evaluate(x_vals, y_vals)
        assert isinstance(results, np.ndarray)
        assert results.shape == (n,)
        assert not np.any(np.isnan(results))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
