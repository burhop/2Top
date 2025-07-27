"""
Sprint 4 Regression Test Suite - RFunctionCurve and Constructive Geometry

This test suite ensures that the RFunctionCurve implementation maintains
interface consistency with existing curve classes and that all constructive
geometry operations work correctly across different curve type combinations.

Tests cover:
- Interface consistency across all curve types including RFunctionCurve
- Constructive geometry operations with mixed curve types
- Wrapper function behavior and equivalence
- Serialization consistency for composite curves
- Vectorized operations for all curve combinations
- Edge cases and error handling
"""

import pytest
import sympy as sp
import numpy as np
from geometry import (
    ImplicitCurve, ConicSection, PolynomialCurve, 
    Superellipse, ProceduralCurve, RFunctionCurve,
    union, intersect, difference, blend
)


class TestRFunctionCurveInterfaceConsistency:
    """Test that RFunctionCurve maintains interface consistency with other curve types"""
    
    def setup_method(self):
        """Set up various curve types for interface testing"""
        x, y = sp.symbols('x y')
        
        # Create base curves of different types
        self.conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        self.procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, variables=(x, y))
        
        # Create RFunctionCurves
        self.union_curve = union(self.conic, self.poly)
        self.blend_curve = blend(self.conic, self.superellipse, alpha=0.5)
        
        # All curve types for testing
        self.all_curves = [
            self.conic, self.poly, self.superellipse, 
            self.procedural, self.union_curve, self.blend_curve
        ]
    
    def test_all_curves_inherit_from_implicit_curve(self):
        """Test that all curves inherit from ImplicitCurve"""
        for curve in self.all_curves:
            assert isinstance(curve, ImplicitCurve)
    
    def test_all_curves_have_required_methods(self):
        """Test that all curves have required ImplicitCurve methods"""
        required_methods = ['evaluate', 'gradient', 'normal', 'to_dict', 'plot']
        
        for curve in self.all_curves:
            for method_name in required_methods:
                assert hasattr(curve, method_name)
                assert callable(getattr(curve, method_name))
    
    def test_all_curves_have_required_properties(self):
        """Test that all curves have required properties"""
        for curve in self.all_curves:
            assert hasattr(curve, 'variables')
            assert hasattr(curve, 'expression')
            assert len(curve.variables) == 2
    
    def test_evaluate_method_consistency(self):
        """Test that evaluate method works consistently across all curve types"""
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0), (-0.5, 0.3)]
        
        for curve in self.all_curves:
            for x, y in test_points:
                try:
                    result = curve.evaluate(x, y)
                    assert isinstance(result, (int, float, np.number))
                    assert np.isfinite(result)
                except Exception as e:
                    pytest.fail(f"evaluate failed for {type(curve).__name__} at ({x}, {y}): {e}")
    
    def test_gradient_method_consistency(self):
        """Test that gradient method works consistently across all curve types"""
        test_points = [(0.5, 0.5), (1.0, 0.0), (-0.5, 0.3)]
        
        for curve in self.all_curves:
            for x, y in test_points:
                try:
                    grad_x, grad_y = curve.gradient(x, y)
                    assert isinstance(grad_x, (int, float, np.number))
                    assert isinstance(grad_y, (int, float, np.number))
                    assert np.isfinite(grad_x)
                    assert np.isfinite(grad_y)
                except (ValueError, ZeroDivisionError):
                    # Acceptable for singular points
                    pass
                except Exception as e:
                    pytest.fail(f"gradient failed for {type(curve).__name__} at ({x}, {y}): {e}")
    
    def test_vectorized_evaluation_consistency(self):
        """Test vectorized evaluation across all curve types"""
        x_vals = np.array([0.0, 0.5, 1.0, -0.5])
        y_vals = np.array([0.0, 0.5, 0.0, 0.3])
        
        for curve in self.all_curves:
            try:
                results = curve.evaluate(x_vals, y_vals)
                assert isinstance(results, np.ndarray)
                assert results.shape == x_vals.shape
                assert all(np.isfinite(results))
            except Exception as e:
                pytest.fail(f"Vectorized evaluate failed for {type(curve).__name__}: {e}")
    
    def test_serialization_consistency(self):
        """Test that serialization works consistently across all curve types"""
        for curve in self.all_curves:
            try:
                # Serialize
                serialized = curve.to_dict()
                assert isinstance(serialized, dict)
                assert "type" in serialized
                
                # Deserialize (skip ProceduralCurve due to known limitations)
                if not isinstance(curve, ProceduralCurve):
                    restored = ImplicitCurve.from_dict(serialized)
                    assert isinstance(restored, ImplicitCurve)
                    
                    # Test functional equivalence at a few points
                    test_points = [(0.0, 0.0), (0.5, 0.5)]
                    for x, y in test_points:
                        orig_val = curve.evaluate(x, y)
                        rest_val = restored.evaluate(x, y)
                        assert abs(orig_val - rest_val) < 1e-10
                        
            except Exception as e:
                pytest.fail(f"Serialization failed for {type(curve).__name__}: {e}")


class TestConstructiveGeometryOperations:
    """Test constructive geometry operations with mixed curve types"""
    
    def setup_method(self):
        """Set up curves for constructive geometry testing"""
        x, y = sp.symbols('x y')
        
        # Create different curve types
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
        
        # Test curve combinations
        self.curve_pairs = [
            (self.circle, self.ellipse),
            (self.circle, self.cubic),
            (self.ellipse, self.superellipse),
            (self.cubic, self.superellipse)
        ]
    
    def test_union_operations_all_combinations(self):
        """Test union operations with all curve type combinations"""
        for curve1, curve2 in self.curve_pairs:
            union_curve = union(curve1, curve2)
            
            # Test basic properties
            assert isinstance(union_curve, RFunctionCurve)
            assert union_curve.operation == "union"
            assert union_curve.alpha == 0.0
            
            # Test evaluation
            test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
            for x, y in test_points:
                union_val = union_curve.evaluate(x, y)
                curve1_val = curve1.evaluate(x, y)
                curve2_val = curve2.evaluate(x, y)
                
                # Union should be min(f1, f2)
                expected_val = min(curve1_val, curve2_val)
                assert abs(union_val - expected_val) < 1e-10
    
    def test_intersection_operations_all_combinations(self):
        """Test intersection operations with all curve type combinations"""
        for curve1, curve2 in self.curve_pairs:
            intersection_curve = intersect(curve1, curve2)
            
            # Test basic properties
            assert isinstance(intersection_curve, RFunctionCurve)
            assert intersection_curve.operation == "intersection"
            assert intersection_curve.alpha == 0.0
            
            # Test evaluation
            test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
            for x, y in test_points:
                intersection_val = intersection_curve.evaluate(x, y)
                curve1_val = curve1.evaluate(x, y)
                curve2_val = curve2.evaluate(x, y)
                
                # Intersection should be max(f1, f2)
                expected_val = max(curve1_val, curve2_val)
                assert abs(intersection_val - expected_val) < 1e-10
    
    def test_difference_operations_all_combinations(self):
        """Test difference operations with all curve type combinations"""
        for curve1, curve2 in self.curve_pairs:
            difference_curve = difference(curve1, curve2)
            
            # Test basic properties
            assert isinstance(difference_curve, RFunctionCurve)
            assert difference_curve.operation == "difference"
            assert difference_curve.alpha == 0.0
            
            # Test evaluation
            test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
            for x, y in test_points:
                difference_val = difference_curve.evaluate(x, y)
                curve1_val = curve1.evaluate(x, y)
                curve2_val = curve2.evaluate(x, y)
                
                # Difference should be max(f1, -f2)
                expected_val = max(curve1_val, -curve2_val)
                assert abs(difference_val - expected_val) < 1e-10
    
    def test_blend_operations_all_combinations(self):
        """Test blend operations with all curve type combinations"""
        alpha_values = [0.1, 0.5, 1.0]
        
        for curve1, curve2 in self.curve_pairs:
            for alpha in alpha_values:
                blend_curve = blend(curve1, curve2, alpha)
                
                # Test basic properties
                assert isinstance(blend_curve, RFunctionCurve)
                assert blend_curve.operation == "blend"
                assert blend_curve.alpha == alpha
                
                # Test evaluation
                test_points = [(0.0, 0.0), (0.5, 0.5)]
                for x, y in test_points:
                    blend_val = blend_curve.evaluate(x, y)
                    curve1_val = curve1.evaluate(x, y)
                    curve2_val = curve2.evaluate(x, y)
                    
                    # Blend should use smooth approximation
                    diff = curve1_val - curve2_val
                    expected_val = (curve1_val + curve2_val - np.sqrt(diff**2 + alpha**2)) / 2
                    assert abs(blend_val - expected_val) < 1e-10


class TestWrapperFunctionEquivalence:
    """Test that wrapper functions produce equivalent results to direct RFunctionCurve construction"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        self.curve1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.curve2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
    
    def test_union_wrapper_equivalence(self):
        """Test that union wrapper produces same result as direct construction"""
        wrapper_union = union(self.curve1, self.curve2)
        direct_union = RFunctionCurve(self.curve1, self.curve2, operation="union")
        
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            wrapper_val = wrapper_union.evaluate(x, y)
            direct_val = direct_union.evaluate(x, y)
            assert abs(wrapper_val - direct_val) < 1e-15
    
    def test_intersect_wrapper_equivalence(self):
        """Test that intersect wrapper produces same result as direct construction"""
        wrapper_intersect = intersect(self.curve1, self.curve2)
        direct_intersect = RFunctionCurve(self.curve1, self.curve2, operation="intersection")
        
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            wrapper_val = wrapper_intersect.evaluate(x, y)
            direct_val = direct_intersect.evaluate(x, y)
            assert abs(wrapper_val - direct_val) < 1e-15
    
    def test_difference_wrapper_equivalence(self):
        """Test that difference wrapper produces same result as direct construction"""
        wrapper_diff = difference(self.curve1, self.curve2)
        direct_diff = RFunctionCurve(self.curve1, self.curve2, operation="difference")
        
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            wrapper_val = wrapper_diff.evaluate(x, y)
            direct_val = direct_diff.evaluate(x, y)
            assert abs(wrapper_val - direct_val) < 1e-15
    
    def test_blend_wrapper_equivalence(self):
        """Test that blend wrapper produces same result as direct construction"""
        alpha = 0.5
        wrapper_blend = blend(self.curve1, self.curve2, alpha)
        direct_blend = RFunctionCurve(self.curve1, self.curve2, operation="blend", alpha=alpha)
        
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            wrapper_val = wrapper_blend.evaluate(x, y)
            direct_val = direct_blend.evaluate(x, y)
            assert abs(wrapper_val - direct_val) < 1e-15


class TestNestedConstructiveOperations:
    """Test nested constructive geometry operations"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        self.circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        self.circle3 = ConicSection((x-0.5)**2 + (y-0.5)**2 - 0.25, variables=(x, y))
    
    def test_nested_union_intersection(self):
        """Test nested operations: (A ∪ B) ∩ C"""
        # Create nested structure
        union_ab = union(self.circle1, self.circle2)
        nested_result = intersect(union_ab, self.circle3)
        
        # Test that it's a valid RFunctionCurve
        assert isinstance(nested_result, RFunctionCurve)
        assert nested_result.operation == "intersection"
        assert isinstance(nested_result.curve1, RFunctionCurve)
        assert nested_result.curve1.operation == "union"
        
        # Test evaluation
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            result_val = nested_result.evaluate(x, y)
            assert np.isfinite(result_val)
    
    def test_nested_blend_operations(self):
        """Test nested blend operations"""
        # Create nested blend: blend(A, blend(B, C, α1), α2)
        inner_blend = blend(self.circle2, self.circle3, alpha=0.3)
        outer_blend = blend(self.circle1, inner_blend, alpha=0.5)
        
        # Test that it's a valid structure
        assert isinstance(outer_blend, RFunctionCurve)
        assert outer_blend.operation == "blend"
        assert outer_blend.alpha == 0.5
        assert isinstance(outer_blend.curve2, RFunctionCurve)
        assert outer_blend.curve2.operation == "blend"
        assert outer_blend.curve2.alpha == 0.3
        
        # Test evaluation
        test_points = [(0.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            result_val = outer_blend.evaluate(x, y)
            assert np.isfinite(result_val)
    
    def test_complex_nested_structure(self):
        """Test complex nested structure: (A ∪ B) - blend(C, D, α)"""
        x, y = sp.symbols('x y')
        circle4 = ConicSection((x+0.5)**2 + (y+0.5)**2 - 0.25, variables=(x, y))
        
        # Create complex structure
        union_part = union(self.circle1, self.circle2)
        blend_part = blend(self.circle3, circle4, alpha=0.4)
        complex_result = difference(union_part, blend_part)
        
        # Test structure
        assert isinstance(complex_result, RFunctionCurve)
        assert complex_result.operation == "difference"
        assert isinstance(complex_result.curve1, RFunctionCurve)
        assert isinstance(complex_result.curve2, RFunctionCurve)
        
        # Test evaluation
        test_points = [(0.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            result_val = complex_result.evaluate(x, y)
            assert np.isfinite(result_val)


class TestRFunctionCurveEdgeCases:
    """Test edge cases and error conditions for RFunctionCurve"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.line = PolynomialCurve(x + y - 1, variables=(x, y))
    
    def test_identical_curves_union(self):
        """Test union of identical curves"""
        union_curve = union(self.circle, self.circle)
        
        # Should behave like the original curve
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            union_val = union_curve.evaluate(x, y)
            circle_val = self.circle.evaluate(x, y)
            assert abs(union_val - circle_val) < 1e-15
    
    def test_very_small_alpha_blend(self):
        """Test blend with very small alpha (should approach sharp union)"""
        tiny_alpha = 1e-12
        blend_curve = blend(self.circle, self.line, alpha=tiny_alpha)
        union_curve = union(self.circle, self.line)
        
        test_points = [(0.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            blend_val = blend_curve.evaluate(x, y)
            union_val = union_curve.evaluate(x, y)
            assert abs(blend_val - union_val) < 1e-8
    
    def test_large_alpha_blend(self):
        """Test blend with large alpha"""
        large_alpha = 10.0
        blend_curve = blend(self.circle, self.line, alpha=large_alpha)
        
        # Should still produce finite results
        test_points = [(0.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            blend_val = blend_curve.evaluate(x, y)
            assert np.isfinite(blend_val)
    
    def test_gradient_at_blend_boundaries(self):
        """Test gradient computation at blend boundaries"""
        blend_curve = blend(self.circle, self.line, alpha=0.5)
        
        # Test gradient at various points
        test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
        for x, y in test_points:
            try:
                grad_x, grad_y = blend_curve.gradient(x, y)
                assert np.isfinite(grad_x)
                assert np.isfinite(grad_y)
            except (ValueError, ZeroDivisionError):
                # Acceptable for singular points
                pass


if __name__ == "__main__":
    # Run regression tests
    pytest.main([__file__, "-v"])
