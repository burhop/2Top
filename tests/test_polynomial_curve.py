"""
Test suite for PolynomialCurve class - Sprint 2 Task GEO-S2-T3

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- degree method for various polynomial degrees
- Specialized serialization with type "PolynomialCurve"
- All inherited ImplicitCurve interface methods
"""

import pytest
import sympy as sp
import numpy as np
from geometry.polynomial_curve import PolynomialCurve
from geometry.implicit_curve import ImplicitCurve


class TestPolynomialCurveConstructor:
    """Test PolynomialCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that PolynomialCurve properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        poly_expr = x**3 + y**3 - 1
        poly_curve = PolynomialCurve(poly_expr, variables=(x, y))
        
        # Should be instance of both PolynomialCurve and ImplicitCurve
        assert isinstance(poly_curve, PolynomialCurve)
        assert isinstance(poly_curve, ImplicitCurve)
    
    def test_constructor_with_various_polynomial_degrees(self):
        """Test constructor with polynomials of different degrees"""
        x, y = sp.symbols('x y')
        
        # Various polynomial expressions
        expressions = [
            x + y - 1,  # Degree 1 (line)
            x**2 + y**2 - 1,  # Degree 2 (circle)
            x**3 + y**3 - 1,  # Degree 3 (cubic)
            x**4 + y**4 - 2*x**2*y**2 - 1,  # Degree 4 (quartic)
            x**5 + x**3*y**2 + y**5 - 1,  # Degree 5 (quintic)
        ]
        
        for expr in expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.expression == expr
            assert poly_curve.variables == (x, y)
    
    def test_constructor_with_non_polynomial_expression(self):
        """Test constructor behavior with non-polynomial expressions"""
        x, y = sp.symbols('x y')
        
        # These should still work but degree computation might be affected
        trig_expr = sp.sin(x) + sp.cos(y) - 1
        exp_expr = sp.exp(x**2 + y**2) - 2
        
        # Should not raise error
        trig_curve = PolynomialCurve(trig_expr, variables=(x, y))
        exp_curve = PolynomialCurve(exp_expr, variables=(x, y))
        
        assert trig_curve.expression == trig_expr
        assert exp_curve.expression == exp_expr


class TestPolynomialCurveDegree:
    """Test PolynomialCurve degree method - Sprint 2 Task GEO-S2-T3"""
    
    def test_degree_linear_polynomial(self):
        """Test degree computation for linear polynomials (degree 1)"""
        x, y = sp.symbols('x y')
        
        linear_expressions = [
            x + y - 1,
            2*x - 3*y + 5,
            x - 1,
            y + 2,
            3*x + 4*y
        ]
        
        for expr in linear_expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.degree() == 1
    
    def test_degree_quadratic_polynomial(self):
        """Test degree computation for quadratic polynomials (degree 2)"""
        x, y = sp.symbols('x y')
        
        quadratic_expressions = [
            x**2 + y**2 - 1,  # Circle
            x**2 - y**2 - 1,  # Hyperbola
            x**2 + 2*x*y + y**2 - 1,  # With xy term
            x**2 + 3*x + y**2 + 2*y - 5,  # With linear terms
            y - x**2  # Parabola
        ]
        
        for expr in quadratic_expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.degree() == 2
    
    def test_degree_cubic_polynomial(self):
        """Test degree computation for cubic polynomials (degree 3)"""
        x, y = sp.symbols('x y')
        
        cubic_expressions = [
            x**3 + y**3 - 1,
            x**3 + 3*x**2*y + 3*x*y**2 + y**3 - 1,  # (x+y)³ - 1
            x**3 - 3*x*y**2 + 2,  # Mixed terms
            y**3 + x**2 - 1  # Highest degree term is y³
        ]
        
        for expr in cubic_expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.degree() == 3
    
    def test_degree_quartic_polynomial(self):
        """Test degree computation for quartic polynomials (degree 4)"""
        x, y = sp.symbols('x y')
        
        quartic_expressions = [
            x**4 + y**4 - 1,
            x**4 + y**4 - 2*x**2*y**2 - 1,  # Lemniscate-like
            (x**2 + y**2)**2 - 2*(x**2 - y**2),  # Expanded form
            x**4 + 2*x**3*y + x**2*y**2 - 1
        ]
        
        for expr in quartic_expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.degree() == 4
    
    def test_degree_higher_degree_polynomial(self):
        """Test degree computation for higher degree polynomials"""
        x, y = sp.symbols('x y')
        
        # Degree 5
        quintic = x**5 + y**5 - 1
        poly_curve = PolynomialCurve(quintic, variables=(x, y))
        assert poly_curve.degree() == 5
        
        # Degree 6
        sextic = x**6 + y**6 + x**3*y**3 - 1
        poly_curve = PolynomialCurve(sextic, variables=(x, y))
        assert poly_curve.degree() == 6
    
    def test_degree_constant_polynomial(self):
        """Test degree computation for constant expressions"""
        x, y = sp.symbols('x y')
        
        # Constant (degree 0)
        constant = sp.sympify(5)
        poly_curve = PolynomialCurve(constant, variables=(x, y))
        assert poly_curve.degree() == 0
        
        # Another constant
        constant2 = sp.sympify(-3)
        poly_curve2 = PolynomialCurve(constant2, variables=(x, y))
        assert poly_curve2.degree() == 0
    
    def test_degree_mixed_terms_polynomial(self):
        """Test degree computation for polynomials with mixed terms"""
        x, y = sp.symbols('x y')
        
        # The degree should be the maximum sum of exponents in any term
        mixed_expressions = [
            x**2*y + x*y**2 - 1,  # Both terms are degree 3
            x**3 + x**2*y + x*y**2 + y**3 - 1,  # All terms degree 3
            x**4 + x**2*y**2 + y**4 - 1,  # All terms degree 4
            x**5 + x**3*y + x*y**3 + y**2 - 1  # Highest is x⁵ (degree 5)
        ]
        
        expected_degrees = [3, 3, 4, 5]
        
        for expr, expected_degree in zip(mixed_expressions, expected_degrees):
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            assert poly_curve.degree() == expected_degree
    
    def test_degree_returns_integer(self):
        """Test that degree method returns an integer"""
        x, y = sp.symbols('x y')
        poly_curve = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        
        result = poly_curve.degree()
        assert isinstance(result, int)
        assert result == 3
    
    def test_degree_non_polynomial_expressions(self):
        """Test degree behavior with non-polynomial expressions"""
        x, y = sp.symbols('x y')
        
        # These might return unexpected results or raise errors
        # The behavior depends on sympy's polynomial degree computation
        non_poly_expressions = [
            sp.sin(x) + sp.cos(y),
            sp.exp(x) + y,
            sp.log(x**2 + y**2 + 1)
        ]
        
        for expr in non_poly_expressions:
            poly_curve = PolynomialCurve(expr, variables=(x, y))
            # Should not crash, but degree might be undefined or raise error
            try:
                degree = poly_curve.degree()
                assert isinstance(degree, int) or degree is None
            except (ValueError, TypeError, AttributeError):
                # Expected for non-polynomial expressions
                pass


class TestPolynomialCurveInheritedMethods:
    """Test that PolynomialCurve properly inherits and works with ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test polynomial curves"""
        x, y = sp.symbols('x y')
        self.line = PolynomialCurve(x + y - 1, variables=(x, y))
        self.circle = PolynomialCurve(x**2 + y**2 - 1, variables=(x, y))
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    def test_evaluate_method_inherited(self):
        """Test that evaluate method works correctly"""
        # Line tests
        assert abs(self.line.evaluate(0.5, 0.5)) < 1e-10  # On line
        assert self.line.evaluate(0.0, 0.0) < 0  # Below line
        assert self.line.evaluate(1.0, 1.0) > 0  # Above line
        
        # Circle tests
        assert self.circle.evaluate(0.0, 0.0) < 0  # Inside
        assert abs(self.circle.evaluate(1.0, 0.0)) < 1e-10  # On curve
        assert self.circle.evaluate(2.0, 0.0) > 0  # Outside
        
        # Cubic tests
        assert self.cubic.evaluate(0.0, 0.0) < 0  # Inside
        assert abs(self.cubic.evaluate(1.0, 0.0)) < 1e-10  # On curve
    
    def test_gradient_method_inherited(self):
        """Test that gradient method works correctly"""
        # Line gradient should be constant (1, 1)
        grad_x, grad_y = self.line.gradient(0.0, 0.0)
        assert abs(grad_x - 1.0) < 1e-10
        assert abs(grad_y - 1.0) < 1e-10
        
        # Circle gradient at (1,0) should be (2,0)
        grad_x, grad_y = self.circle.gradient(1.0, 0.0)
        assert abs(grad_x - 2.0) < 1e-10
        assert abs(grad_y - 0.0) < 1e-10
        
        # Cubic gradient at (1,0) should be (3,0)
        grad_x, grad_y = self.cubic.gradient(1.0, 0.0)
        assert abs(grad_x - 3.0) < 1e-10
        assert abs(grad_y - 0.0) < 1e-10
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly"""
        # Line normal should be unit vector in direction (1,1)
        nx, ny = self.line.normal(0.0, 0.0)
        expected_component = 1.0 / np.sqrt(2.0)
        assert abs(nx - expected_component) < 1e-10
        assert abs(ny - expected_component) < 1e-10
        
        # Normal should be unit length
        magnitude = np.sqrt(nx**2 + ny**2)
        assert abs(magnitude - 1.0) < 1e-10


class TestPolynomialCurveSerialization:
    """Test PolynomialCurve serialization with specialized type"""
    
    def setup_method(self):
        """Set up test polynomial curves"""
        x, y = sp.symbols('x y')
        self.line = PolynomialCurve(x + y - 1, variables=(x, y))
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    def test_to_dict_has_polynomial_curve_type(self):
        """Test that to_dict returns type 'PolynomialCurve'"""
        data = self.line.to_dict()
        
        assert isinstance(data, dict)
        assert data["type"] == "PolynomialCurve"
        assert "expression" in data
        assert "variables" in data
    
    def test_to_dict_includes_degree_info(self):
        """Test that to_dict includes degree information"""
        data = self.cubic.to_dict()
        
        assert "degree" in data
        assert data["degree"] == 3
    
    def test_from_dict_reconstruction(self):
        """Test that from_dict can reconstruct PolynomialCurve"""
        # Serialize and deserialize
        data = self.line.to_dict()
        reconstructed = PolynomialCurve.from_dict(data)
        
        # Should be PolynomialCurve instance
        assert isinstance(reconstructed, PolynomialCurve)
        assert isinstance(reconstructed, ImplicitCurve)
        
        # Should have same degree
        assert reconstructed.degree() == self.line.degree()
    
    def test_serialization_round_trip_functional_equivalence(self):
        """Test that serialization preserves functional behavior"""
        test_curves = [self.line, self.cubic]
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for curve in test_curves:
            # Serialize and deserialize
            data = curve.to_dict()
            reconstructed = PolynomialCurve.from_dict(data)
            
            # Test functional equivalence
            for x, y in test_points:
                orig_val = curve.evaluate(x, y)
                recon_val = reconstructed.evaluate(x, y)
                assert abs(orig_val - recon_val) < 1e-10
                
                # Test gradient equivalence
                orig_grad = curve.gradient(x, y)
                recon_grad = reconstructed.gradient(x, y)
                assert abs(orig_grad[0] - recon_grad[0]) < 1e-10
                assert abs(orig_grad[1] - recon_grad[1]) < 1e-10
    
    def test_from_dict_invalid_type_handling(self):
        """Test that from_dict handles invalid types appropriately"""
        # Test with wrong type
        with pytest.raises(ValueError, match="Invalid type"):
            PolynomialCurve.from_dict({"type": "WrongType", "expression": "x**3 + y**3 - 1"})
        
        # Test with ImplicitCurve type (should work via base class)
        data = {"type": "ImplicitCurve", "expression": "x**3 + y**3 - 1", "variables": ["x", "y"]}
        reconstructed = PolynomialCurve.from_dict(data)
        assert isinstance(reconstructed, PolynomialCurve)


class TestPolynomialCurveSpecializedMethods:
    """Test PolynomialCurve specialized methods beyond basic interface"""
    
    def setup_method(self):
        """Set up test polynomial curves"""
        x, y = sp.symbols('x y')
        self.cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    def test_str_representation(self):
        """Test string representation"""
        str_repr = str(self.cubic)
        assert "x**3 + y**3 - 1" in str_repr or "x^3 + y^3 - 1" in str_repr
        assert "= 0" in str_repr
    
    def test_repr_representation(self):
        """Test detailed representation"""
        repr_str = repr(self.cubic)
        assert "PolynomialCurve" in repr_str
        assert "degree 3" in repr_str or "3" in repr_str
        assert "x**3 + y**3 - 1" in repr_str or "x^3 + y^3 - 1" in repr_str
