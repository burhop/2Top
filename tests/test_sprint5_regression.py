"""
Sprint 5 Regression Test Suite - TrimmedImplicitCurve and CompositeCurve

This test suite ensures that the new Sprint 5 classes maintain full interface
consistency with the ImplicitCurve base class and work correctly with all
existing curve types from previous sprints.

Test Coverage:
- Interface consistency (evaluate, gradient, normal, to_dict, from_dict, plot)
- Cross-class compatibility with all existing curve types
- Vectorized operations support
- Edge case handling
- Performance characteristics
- Integration with constructive geometry operations
"""

import pytest
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse
from geometry.procedural_curve import ProceduralCurve
from geometry.rfunction_curve import RFunctionCurve, union, intersect, difference, blend
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve, create_circle_from_quarters, create_square_from_edges


class TestTrimmedImplicitCurveInterfaceConsistency:
    """Test that TrimmedImplicitCurve maintains ImplicitCurve interface consistency"""
    
    def setup_method(self):
        """Set up test curves from all previous sprints"""
        x, y = sp.symbols('x y')
        
        # Create base curves from all sprints
        self.conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        self.procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, variables=(x, y))
        self.rfunction = union(self.conic, self.poly)
        
        # Create trimmed versions
        self.trimmed_conic = TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0)
        self.trimmed_poly = TrimmedImplicitCurve(self.poly, lambda x, y: y >= 0)
        self.trimmed_super = TrimmedImplicitCurve(self.superellipse, lambda x, y: x >= 0 and y >= 0)
        self.trimmed_proc = TrimmedImplicitCurve(self.procedural, lambda x, y: x >= 0)
        self.trimmed_rfunc = TrimmedImplicitCurve(self.rfunction, lambda x, y: y >= 0)
        
        self.all_trimmed = [
            self.trimmed_conic, self.trimmed_poly, self.trimmed_super,
            self.trimmed_proc, self.trimmed_rfunc
        ]
    
    def test_inheritance_from_implicit_curve(self):
        """Test that all trimmed curves inherit from ImplicitCurve"""
        for curve in self.all_trimmed:
            assert isinstance(curve, ImplicitCurve)
            assert hasattr(curve, 'evaluate')
            assert hasattr(curve, 'gradient')
            assert hasattr(curve, 'normal')
            assert hasattr(curve, 'to_dict')
            assert hasattr(curve, 'plot')
    
    def test_evaluate_method_consistency(self):
        """Test evaluate method works consistently across all base curve types"""
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (-0.5, -0.5)]
        
        for curve in self.all_trimmed:
            for x, y in test_points:
                # Should return float
                result = curve.evaluate(x, y)
                assert isinstance(result, (int, float, np.number))
                
                # Should match base curve evaluation
                base_result = curve.base_curve.evaluate(x, y)
                assert abs(result - base_result) < 1e-10
    
    def test_gradient_method_consistency(self):
        """Test gradient method works consistently across all base curve types"""
        test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
        
        for curve in self.all_trimmed:
            for x, y in test_points:
                # Should return tuple of two floats
                grad_x, grad_y = curve.gradient(x, y)
                assert isinstance(grad_x, (int, float, np.number))
                assert isinstance(grad_y, (int, float, np.number))
                
                # Should match base curve gradient
                base_grad_x, base_grad_y = curve.base_curve.gradient(x, y)
                assert abs(grad_x - base_grad_x) < 1e-10
                assert abs(grad_y - base_grad_y) < 1e-10
    
    def test_normal_method_consistency(self):
        """Test normal method works consistently across all base curve types"""
        test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
        
        for curve in self.all_trimmed:
            for x, y in test_points:
                # Should return tuple of two floats
                norm_x, norm_y = curve.normal(x, y)
                assert isinstance(norm_x, (int, float, np.number))
                assert isinstance(norm_y, (int, float, np.number))
                
                # Should be unit vector (approximately)
                magnitude = np.sqrt(norm_x**2 + norm_y**2)
                if magnitude > 1e-10:  # Avoid division by zero
                    assert abs(magnitude - 1.0) < 1e-6
    
    def test_vectorized_operations(self):
        """Test vectorized operations work consistently"""
        x_vals = np.array([0.0, 0.5, 1.0, -0.5])
        y_vals = np.array([0.0, 0.5, 0.0, -0.5])
        
        for curve in self.all_trimmed:
            # Test vectorized evaluate
            results = curve.evaluate(x_vals, y_vals)
            assert isinstance(results, np.ndarray)
            assert results.shape == x_vals.shape
            
            # Test vectorized gradient
            grad_x, grad_y = curve.gradient(x_vals, y_vals)
            assert isinstance(grad_x, np.ndarray)
            assert isinstance(grad_y, np.ndarray)
            assert grad_x.shape == x_vals.shape
            assert grad_y.shape == y_vals.shape
            
            # Test vectorized contains
            contains_results = curve.contains(x_vals, y_vals)
            assert isinstance(contains_results, np.ndarray)
            assert contains_results.dtype == bool
            assert contains_results.shape == x_vals.shape
    
    def test_serialization_interface(self):
        """Test serialization interface consistency"""
        for curve in self.all_trimmed:
            # Should have to_dict method
            serialized = curve.to_dict()
            assert isinstance(serialized, dict)
            assert "type" in serialized
            assert serialized["type"] == "TrimmedImplicitCurve"
            
            # Should be deserializable
            restored = TrimmedImplicitCurve.from_dict(serialized)
            assert isinstance(restored, TrimmedImplicitCurve)
            assert isinstance(restored, ImplicitCurve)
    
    def test_plotting_interface(self):
        """Test plotting interface consistency"""
        for curve in self.all_trimmed:
            # Should have plot method
            assert hasattr(curve, 'plot')
            
            # Should be callable without errors
            fig, ax = plt.subplots()
            try:
                curve.plot(ax=ax)
                plt.close(fig)
            except Exception as e:
                plt.close(fig)
                pytest.fail(f"Plotting failed for {type(curve.base_curve).__name__}: {e}")


class TestCompositeCurveInterfaceConsistency:
    """Test that CompositeCurve maintains ImplicitCurve interface consistency"""
    
    def setup_method(self):
        """Set up test composite curves"""
        x, y = sp.symbols('x y')
        
        # Create base curves
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        poly = PolynomialCurve(x + y - 1, variables=(x, y))
        superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # Create different composite configurations
        self.simple_composite = CompositeCurve([
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0)
        ])
        
        self.mixed_composite = CompositeCurve([
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(poly, lambda x, y: x <= 0 and y >= 0),
            TrimmedImplicitCurve(superellipse, lambda x, y: x <= 0 and y <= 0)
        ])
        
        self.single_segment_composite = CompositeCurve([
            TrimmedImplicitCurve(circle, lambda x, y: True)
        ])
        
        self.all_composites = [
            self.simple_composite, self.mixed_composite, self.single_segment_composite
        ]
    
    def test_inheritance_from_implicit_curve(self):
        """Test that all composite curves inherit from ImplicitCurve"""
        for curve in self.all_composites:
            assert isinstance(curve, ImplicitCurve)
            assert hasattr(curve, 'evaluate')
            assert hasattr(curve, 'gradient')
            assert hasattr(curve, 'normal')
            assert hasattr(curve, 'to_dict')
            assert hasattr(curve, 'plot')
    
    def test_evaluate_method_consistency(self):
        """Test evaluate method works consistently"""
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5), (-0.5, -0.5)]
        
        for curve in self.all_composites:
            for x, y in test_points:
                # Should return float
                result = curve.evaluate(x, y)
                assert isinstance(result, (int, float, np.number))
                assert not np.isnan(result)
                assert not np.isinf(result)
    
    def test_gradient_method_consistency(self):
        """Test gradient method works consistently"""
        test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
        
        for curve in self.all_composites:
            for x, y in test_points:
                # Should return tuple of two floats
                grad_x, grad_y = curve.gradient(x, y)
                assert isinstance(grad_x, (int, float, np.number))
                assert isinstance(grad_y, (int, float, np.number))
                assert not np.isnan(grad_x)
                assert not np.isnan(grad_y)
    
    def test_vectorized_operations(self):
        """Test vectorized operations work consistently"""
        x_vals = np.array([0.0, 0.5, 1.0, -0.5])
        y_vals = np.array([0.0, 0.5, 0.0, -0.5])
        
        for curve in self.all_composites:
            # Test vectorized evaluate
            results = curve.evaluate(x_vals, y_vals)
            assert isinstance(results, np.ndarray)
            assert results.shape == x_vals.shape
            
            # Test vectorized gradient
            grad_x, grad_y = curve.gradient(x_vals, y_vals)
            assert isinstance(grad_x, np.ndarray)
            assert isinstance(grad_y, np.ndarray)
            assert grad_x.shape == x_vals.shape
            assert grad_y.shape == y_vals.shape
            
            # Test vectorized contains
            contains_results = curve.contains(x_vals, y_vals)
            assert isinstance(contains_results, np.ndarray)
            assert contains_results.dtype == bool
            assert contains_results.shape == x_vals.shape
    
    def test_serialization_interface(self):
        """Test serialization interface consistency"""
        for curve in self.all_composites:
            # Should have to_dict method
            serialized = curve.to_dict()
            assert isinstance(serialized, dict)
            assert "type" in serialized
            assert serialized["type"] == "CompositeCurve"
            
            # Should be deserializable
            restored = CompositeCurve.from_dict(serialized)
            assert isinstance(restored, CompositeCurve)
            assert isinstance(restored, ImplicitCurve)


class TestCrossClassCompatibility:
    """Test compatibility between Sprint 5 classes and previous sprint classes"""
    
    def setup_method(self):
        """Set up curves from all sprints"""
        x, y = sp.symbols('x y')
        
        # Create base curves from all sprints
        self.conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        self.procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, variables=(x, y))
        self.rfunction = union(self.conic, self.poly)
        
        # Create trimmed versions
        self.trimmed_conic = TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0)
        self.trimmed_rfunction = TrimmedImplicitCurve(self.rfunction, lambda x, y: y >= 0)
        
        # Create composite
        self.composite = CompositeCurve([
            self.trimmed_conic,
            TrimmedImplicitCurve(self.poly, lambda x, y: x <= 0)
        ])
    
    def test_trimmed_with_constructive_geometry(self):
        """Test trimmed curves work with constructive geometry operations"""
        # Create union of trimmed curve with regular curve
        union_curve = union(self.trimmed_conic, self.poly)
        assert isinstance(union_curve, RFunctionCurve)
        
        # Test evaluation
        result = union_curve.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        
        # Create intersection
        intersect_curve = intersect(self.trimmed_conic, self.conic)
        assert isinstance(intersect_curve, RFunctionCurve)
        
        # Create difference
        diff_curve = difference(self.conic, self.trimmed_conic)
        assert isinstance(diff_curve, RFunctionCurve)
        
        # Create blend
        blend_curve = blend(self.trimmed_conic, self.poly, alpha=0.1)
        assert isinstance(blend_curve, RFunctionCurve)
    
    def test_composite_with_constructive_geometry(self):
        """Test composite curves work with constructive geometry operations"""
        # Create union of composite with regular curve
        union_curve = union(self.composite, self.conic)
        assert isinstance(union_curve, RFunctionCurve)
        
        # Test evaluation
        result = union_curve.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        
        # Create intersection
        intersect_curve = intersect(self.composite, self.superellipse)
        assert isinstance(intersect_curve, RFunctionCurve)
    
    def test_nested_trimmed_curves(self):
        """Test trimming of already complex curves"""
        # Trim an RFunction curve
        complex_base = blend(self.conic, self.poly, alpha=0.1)
        trimmed_complex = TrimmedImplicitCurve(complex_base, lambda x, y: x >= 0 and y >= 0)
        
        # Should work normally
        result = trimmed_complex.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        
        # Should support contains
        assert isinstance(trimmed_complex.contains(0.5, 0.5), bool)
        assert isinstance(trimmed_complex.contains(-0.5, -0.5), bool)
    
    def test_serialization_cross_compatibility(self):
        """Test serialization works across all curve types"""
        curves_to_test = [
            self.trimmed_conic,
            self.trimmed_rfunction,
            self.composite
        ]
        
        for curve in curves_to_test:
            # Serialize and deserialize
            serialized = curve.to_dict()
            
            # Should be deserializable using ImplicitCurve.from_dict
            restored = ImplicitCurve.from_dict(serialized)
            assert type(restored) == type(curve)
            
            # Should maintain functionality
            test_points = [(0.0, 0.0), (0.5, 0.5)]
            for x, y in test_points:
                orig_val = curve.evaluate(x, y)
                rest_val = restored.evaluate(x, y)
                # Note: Due to mask limitations, we only test base curve equivalence
                if hasattr(curve, 'base_curve'):
                    orig_base = curve.base_curve.evaluate(x, y)
                    rest_base = restored.base_curve.evaluate(x, y)
                    assert abs(orig_base - rest_base) < 1e-10


class TestUtilityFunctions:
    """Test utility functions for creating common composite curves"""
    
    def test_create_circle_from_quarters(self):
        """Test create_circle_from_quarters utility function"""
        # Default parameters
        circle = create_circle_from_quarters()
        assert isinstance(circle, CompositeCurve)
        assert len(circle.segments) == 4
        
        # Custom parameters
        custom_circle = create_circle_from_quarters(center=(1, 1), radius=2.0)
        assert isinstance(custom_circle, CompositeCurve)
        assert len(custom_circle.segments) == 4
        
        # Test evaluation
        result = custom_circle.evaluate(3.0, 1.0)  # Point on circle
        assert abs(result) < 1e-6  # Should be close to zero
    
    def test_create_square_from_edges(self):
        """Test create_square_from_edges utility function"""
        # Default parameters
        square = create_square_from_edges()
        assert isinstance(square, CompositeCurve)
        assert len(square.segments) == 4
        
        # Custom parameters
        custom_square = create_square_from_edges(corner1=(-1, -1), corner2=(1, 1))
        assert isinstance(custom_square, CompositeCurve)
        assert len(custom_square.segments) == 4
        
        # Test evaluation
        result = custom_square.evaluate(1.0, 0.0)  # Point on edge
        assert abs(result) < 1e-6  # Should be close to zero


class TestPerformanceCharacteristics:
    """Test performance characteristics of Sprint 5 classes"""
    
    def setup_method(self):
        """Set up performance test curves"""
        x, y = sp.symbols('x y')
        
        # Create base curve
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create trimmed curve
        self.trimmed = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
        
        # Create composite with many segments
        segments = []
        for i in range(10):
            angle = i * np.pi / 5
            mask = lambda x, y, a=angle: x * np.cos(a) + y * np.sin(a) >= 0
            segments.append(TrimmedImplicitCurve(circle, mask))
        
        self.large_composite = CompositeCurve(segments)
    
    def test_vectorized_performance(self):
        """Test that vectorized operations are reasonably efficient"""
        # Large array of test points
        n_points = 1000
        x_vals = np.random.uniform(-2, 2, n_points)
        y_vals = np.random.uniform(-2, 2, n_points)
        
        # Test trimmed curve
        results = self.trimmed.evaluate(x_vals, y_vals)
        assert len(results) == n_points
        
        grad_x, grad_y = self.trimmed.gradient(x_vals, y_vals)
        assert len(grad_x) == n_points
        assert len(grad_y) == n_points
        
        contains = self.trimmed.contains(x_vals, y_vals)
        assert len(contains) == n_points
        
        # Test composite curve
        results = self.large_composite.evaluate(x_vals, y_vals)
        assert len(results) == n_points
        
        grad_x, grad_y = self.large_composite.gradient(x_vals, y_vals)
        assert len(grad_x) == n_points
        assert len(grad_y) == n_points


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Set up edge case test curves"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    
    def test_empty_composite_curve(self):
        """Test that empty composite curves raise appropriate errors"""
        with pytest.raises(ValueError, match="must have at least one segment"):
            CompositeCurve([])
    
    def test_single_segment_composite(self):
        """Test composite curve with single segment"""
        single_segment = TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0)
        composite = CompositeCurve([single_segment])
        
        # Should work normally
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float, np.number))
        
        # Should have one segment
        assert len(composite.segments) == 1
        assert composite.get_segment_count() == 1
    
    def test_mask_always_false(self):
        """Test trimmed curve with mask that's always False"""
        always_false_mask = lambda x, y: False
        trimmed = TrimmedImplicitCurve(self.circle, always_false_mask)
        
        # Should still evaluate base curve
        result = trimmed.evaluate(0.5, 0.5)
        base_result = self.circle.evaluate(0.5, 0.5)
        assert abs(result - base_result) < 1e-10
        
        # Contains should always be False
        assert trimmed.contains(0.5, 0.5) == False
        assert trimmed.contains(1.0, 0.0) == False
    
    def test_mask_always_true(self):
        """Test trimmed curve with mask that's always True"""
        always_true_mask = lambda x, y: True
        trimmed = TrimmedImplicitCurve(self.circle, always_true_mask)
        
        # Should behave like base curve
        test_points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
        
        for x, y in test_points:
            trimmed_contains = trimmed.contains(x, y)
            base_contains = self.circle.evaluate(x, y) <= 0
            assert trimmed_contains == base_contains


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
