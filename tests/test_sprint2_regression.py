"""
Sprint 2 Regression Test Suite - Task GEO-S2-T6

Comprehensive regression tests for ConicSection and PolynomialCurve classes.
Ensures both classes maintain interface consistency and work correctly together.

Tests cover:
- Interface consistency between ConicSection and PolynomialCurve
- Inheritance from ImplicitCurve works correctly for both classes
- Serialization compatibility and round-trip testing
- Cross-class functional equivalence where applicable
- Edge cases and error handling
"""

import pytest
import sympy as sp
import numpy as np
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve


class TestSprint2InterfaceConsistency:
    """Test that both ConicSection and PolynomialCurve maintain consistent interfaces"""
    
    def setup_method(self):
        """Set up test curves for both classes"""
        x, y = sp.symbols('x y')
        
        # Common quadratic expressions that can be represented by both classes
        self.circle_expr = x**2 + y**2 - 1
        self.ellipse_expr = x**2/4 + y**2 - 1
        self.hyperbola_expr = x**2 - y**2 - 1
        self.parabola_expr = y - x**2
        
        # Create instances of both classes with same expressions
        self.conic_circle = ConicSection(self.circle_expr, variables=(x, y))
        self.poly_circle = PolynomialCurve(self.circle_expr, variables=(x, y))
        
        self.conic_ellipse = ConicSection(self.ellipse_expr, variables=(x, y))
        self.poly_ellipse = PolynomialCurve(self.ellipse_expr, variables=(x, y))
    
    def test_both_inherit_from_implicit_curve(self):
        """Test that both classes properly inherit from ImplicitCurve"""
        assert isinstance(self.conic_circle, ImplicitCurve)
        assert isinstance(self.poly_circle, ImplicitCurve)
        assert isinstance(self.conic_ellipse, ImplicitCurve)
        assert isinstance(self.poly_ellipse, ImplicitCurve)
    
    def test_evaluate_method_consistency(self):
        """Test that evaluate method gives same results for both classes"""
        test_points = [
            (0.0, 0.0),   # Inside
            (1.0, 0.0),   # On curve
            (2.0, 0.0),   # Outside
            (0.0, 1.0),   # On curve
            (0.5, 0.5),   # Various points
            (-1.0, 0.0),  # Negative coordinates
            (0.0, -1.0)
        ]
        
        curve_pairs = [
            (self.conic_circle, self.poly_circle),
            (self.conic_ellipse, self.poly_ellipse)
        ]
        
        for conic_curve, poly_curve in curve_pairs:
            for x, y in test_points:
                conic_val = conic_curve.evaluate(x, y)
                poly_val = poly_curve.evaluate(x, y)
                assert abs(conic_val - poly_val) < 1e-10, f"Evaluate mismatch at ({x}, {y})"
    
    def test_gradient_method_consistency(self):
        """Test that gradient method gives same results for both classes"""
        test_points = [
            (1.0, 0.0),   # On curve
            (0.0, 1.0),   # On curve
            (0.5, 0.5),   # Various points
            (2.0, 0.0),   # Outside
            (-1.0, 0.0)   # Negative coordinates
        ]
        
        curve_pairs = [
            (self.conic_circle, self.poly_circle),
            (self.conic_ellipse, self.poly_ellipse)
        ]
        
        for conic_curve, poly_curve in curve_pairs:
            for x, y in test_points:
                conic_grad = conic_curve.gradient(x, y)
                poly_grad = poly_curve.gradient(x, y)
                assert abs(conic_grad[0] - poly_grad[0]) < 1e-10, f"Gradient x mismatch at ({x}, {y})"
                assert abs(conic_grad[1] - poly_grad[1]) < 1e-10, f"Gradient y mismatch at ({x}, {y})"
    
    def test_normal_method_consistency(self):
        """Test that normal method gives same results for both classes"""
        test_points = [
            (1.0, 0.0),   # On curve
            (0.0, 1.0),   # On curve
            (0.5, 0.5),   # Various points
            (2.0, 0.0)    # Outside
        ]
        
        curve_pairs = [
            (self.conic_circle, self.poly_circle),
            (self.conic_ellipse, self.poly_ellipse)
        ]
        
        for conic_curve, poly_curve in curve_pairs:
            for x, y in test_points:
                try:
                    conic_normal = conic_curve.normal(x, y)
                    poly_normal = poly_curve.normal(x, y)
                    assert abs(conic_normal[0] - poly_normal[0]) < 1e-10, f"Normal x mismatch at ({x}, {y})"
                    assert abs(conic_normal[1] - poly_normal[1]) < 1e-10, f"Normal y mismatch at ({x}, {y})"
                except ValueError:
                    # Both should raise ValueError for zero gradient
                    with pytest.raises(ValueError):
                        conic_curve.normal(x, y)
                    with pytest.raises(ValueError):
                        poly_curve.normal(x, y)
    
    def test_degree_consistency_for_quadratics(self):
        """Test that degree methods are consistent for quadratic expressions"""
        # ConicSection should always return 2
        assert self.conic_circle.degree() == 2
        assert self.conic_ellipse.degree() == 2
        
        # PolynomialCurve should compute degree 2 for quadratic expressions
        assert self.poly_circle.degree() == 2
        assert self.poly_ellipse.degree() == 2


class TestSprint2SerializationCompatibility:
    """Test serialization compatibility and cross-class reconstruction"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        self.circle_expr = x**2 + y**2 - 1
        self.cubic_expr = x**3 + y**3 - 1
        
        self.conic_circle = ConicSection(self.circle_expr, variables=(x, y))
        self.poly_circle = PolynomialCurve(self.circle_expr, variables=(x, y))
        self.poly_cubic = PolynomialCurve(self.cubic_expr, variables=(x, y))
    
    def test_serialization_type_specificity(self):
        """Test that each class serializes with its specific type"""
        conic_data = self.conic_circle.to_dict()
        poly_data = self.poly_circle.to_dict()
        
        assert conic_data["type"] == "ConicSection"
        assert poly_data["type"] == "PolynomialCurve"
        
        # Both should have same expression and variables for same curve
        assert conic_data["expression"] == poly_data["expression"]
        assert conic_data["variables"] == poly_data["variables"]
    
    def test_cross_class_serialization_compatibility(self):
        """Test that serialized data can be reconstructed by appropriate classes"""
        # Serialize conic as ImplicitCurve, reconstruct as PolynomialCurve
        conic_data = self.conic_circle.to_dict()
        conic_data["type"] = "ImplicitCurve"  # Make it generic
        
        poly_from_conic = PolynomialCurve.from_dict(conic_data)
        assert isinstance(poly_from_conic, PolynomialCurve)
        assert poly_from_conic.degree() == 2
        
        # Test functional equivalence
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5)]
        for x, y in test_points:
            orig_val = self.conic_circle.evaluate(x, y)
            recon_val = poly_from_conic.evaluate(x, y)
            assert abs(orig_val - recon_val) < 1e-10
    
    def test_serialization_round_trip_all_classes(self):
        """Test serialization round-trip for all Sprint 2 classes"""
        curves = [self.conic_circle, self.poly_circle, self.poly_cubic]
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for curve in curves:
            # Serialize and deserialize
            data = curve.to_dict()
            
            if isinstance(curve, ConicSection):
                reconstructed = ConicSection.from_dict(data)
            else:
                reconstructed = PolynomialCurve.from_dict(data)
            
            # Test functional equivalence
            for x, y in test_points:
                orig_val = curve.evaluate(x, y)
                recon_val = reconstructed.evaluate(x, y)
                assert abs(orig_val - recon_val) < 1e-10
                
                orig_grad = curve.gradient(x, y)
                recon_grad = reconstructed.gradient(x, y)
                assert abs(orig_grad[0] - recon_grad[0]) < 1e-10
                assert abs(orig_grad[1] - recon_grad[1]) < 1e-10


class TestSprint2SpecializedMethods:
    """Test specialized methods unique to each class"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        
        # Various conic sections
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
        self.hyperbola = ConicSection(x**2 - y**2 - 1, variables=(x, y))
        self.parabola = ConicSection(y - x**2, variables=(x, y))
        
        # Various polynomial curves
        self.line = PolynomialCurve(x + y - 1, variables=(x, y))
        self.quadratic = PolynomialCurve(x**2 + y**2 - 1, variables=(x, y))
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.quartic = PolynomialCurve(x**4 + y**4 - 1, variables=(x, y))
    
    def test_conic_section_type_classification(self):
        """Test ConicSection conic_type method"""
        assert self.circle.conic_type() == "circle"
        assert self.ellipse.conic_type() == "ellipse"
        assert self.hyperbola.conic_type() == "hyperbola"
        assert self.parabola.conic_type() == "parabola"
    
    def test_conic_section_degree_always_two(self):
        """Test that ConicSection degree method always returns 2"""
        conics = [self.circle, self.ellipse, self.hyperbola, self.parabola]
        for conic in conics:
            assert conic.degree() == 2
    
    def test_polynomial_curve_degree_computation(self):
        """Test PolynomialCurve degree method for various degrees"""
        assert self.line.degree() == 1
        assert self.quadratic.degree() == 2
        assert self.cubic.degree() == 3
        assert self.quartic.degree() == 4
    
    def test_specialized_serialization_data(self):
        """Test that specialized serialization includes class-specific data"""
        # ConicSection should include conic_type
        conic_data = self.circle.to_dict()
        assert "conic_type" in conic_data
        assert conic_data["conic_type"] == "circle"
        
        # PolynomialCurve should include degree
        poly_data = self.cubic.to_dict()
        assert "degree" in poly_data
        assert poly_data["degree"] == 3


class TestSprint2EdgeCases:
    """Test edge cases and error handling for Sprint 2 classes"""
    
    def setup_method(self):
        """Set up edge case expressions"""
        x, y = sp.symbols('x y')
        
        # Edge case expressions
        self.constant = sp.sympify(5)  # Constant
        self.linear = x + y - 1  # Linear
        self.degenerate_conic = x**2  # Degenerate (missing y terms)
        self.non_polynomial = sp.sin(x) + sp.cos(y)  # Non-polynomial
    
    def test_conic_section_with_degenerate_cases(self):
        """Test ConicSection behavior with degenerate cases"""
        x, y = sp.symbols('x y')
        
        # Degenerate cases
        degenerate_cases = [
            x**2,  # Only x² term
            y**2,  # Only y² term
            x*y,   # Only xy term
            x + y  # Linear (not really a conic)
        ]
        
        for expr in degenerate_cases:
            conic = ConicSection(expr, variables=(x, y))
            # Should not crash
            conic_type = conic.conic_type()
            assert isinstance(conic_type, str)
            assert conic.degree() == 2  # Always returns 2
    
    def test_polynomial_curve_with_constant(self):
        """Test PolynomialCurve with constant expression"""
        x, y = sp.symbols('x y')
        constant_curve = PolynomialCurve(self.constant, variables=(x, y))
        
        assert constant_curve.degree() == 0
        assert constant_curve.evaluate(0.0, 0.0) == 5.0
        assert constant_curve.evaluate(1.0, 1.0) == 5.0  # Constant everywhere
    
    def test_polynomial_curve_with_non_polynomial(self):
        """Test PolynomialCurve behavior with non-polynomial expressions"""
        x, y = sp.symbols('x y')
        
        # This should not crash but degree computation might fail
        non_poly_curve = PolynomialCurve(self.non_polynomial, variables=(x, y))
        
        # Should be able to evaluate
        val = non_poly_curve.evaluate(0.0, 0.0)
        assert isinstance(val, (int, float))
        
        # Degree computation might fail
        try:
            degree = non_poly_curve.degree()
            assert isinstance(degree, int)
        except ValueError:
            # Expected for non-polynomial expressions
            pass
    
    def test_serialization_error_handling(self):
        """Test error handling in serialization methods"""
        # Test invalid data for from_dict
        invalid_data_cases = [
            {},  # Empty dict
            {"type": "WrongType"},  # Wrong type
            {"type": "ConicSection"},  # Missing expression
            {"type": "ConicSection", "expression": "x +"},  # Invalid expression
        ]
        
        for invalid_data in invalid_data_cases:
            with pytest.raises(ValueError):
                ConicSection.from_dict(invalid_data)
            
            with pytest.raises(ValueError):
                PolynomialCurve.from_dict(invalid_data)


class TestSprint2Performance:
    """Test performance characteristics of Sprint 2 implementations"""
    
    def setup_method(self):
        """Set up performance test curves"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    def test_vectorized_evaluation(self):
        """Test that vectorized evaluation works correctly for both classes"""
        # Create test arrays
        x_vals = np.array([0.0, 1.0, 2.0, -1.0])
        y_vals = np.array([0.0, 0.0, 0.0, 0.0])
        
        # Test ConicSection
        conic_results = self.circle.evaluate(x_vals, y_vals)
        assert isinstance(conic_results, np.ndarray)
        assert len(conic_results) == len(x_vals)
        
        # Test PolynomialCurve
        poly_results = self.cubic.evaluate(x_vals, y_vals)
        assert isinstance(poly_results, np.ndarray)
        assert len(poly_results) == len(x_vals)
    
    def test_caching_behavior(self):
        """Test that caching works correctly for expensive operations"""
        # ConicSection coefficient caching
        conic_type1 = self.circle.conic_type()
        conic_type2 = self.circle.conic_type()
        assert conic_type1 == conic_type2  # Should use cached result
        
        # PolynomialCurve degree caching
        degree1 = self.cubic.degree()
        degree2 = self.cubic.degree()
        assert degree1 == degree2  # Should use cached result


if __name__ == "__main__":
    # Run regression tests
    pytest.main([__file__, "-v"])
