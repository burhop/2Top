"""
Test suite for ConicSection class - Sprint 2 Task GEO-S2-T1

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- conic_type method for different conic types (circle, ellipse, parabola, hyperbola)
- degree method (should always return 2)
- Specialized serialization with type "ConicSection"
- All inherited ImplicitCurve interface methods
"""

import pytest
import sympy as sp
import numpy as np
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve


class TestConicSectionConstructor:
    """Test ConicSection constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that ConicSection properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        circle_expr = x**2 + y**2 - 1
        conic = ConicSection(circle_expr, variables=(x, y))
        
        # Should be instance of both ConicSection and ImplicitCurve
        assert isinstance(conic, ConicSection)
        assert isinstance(conic, ImplicitCurve)
    
    def test_constructor_with_degree_2_polynomial(self):
        """Test constructor with valid degree-2 polynomial"""
        x, y = sp.symbols('x y')
        
        # Various degree-2 expressions
        expressions = [
            x**2 + y**2 - 1,  # Circle
            x**2/4 + y**2/9 - 1,  # Ellipse
            y - x**2,  # Parabola
            x**2 - y**2 - 1,  # Hyperbola
            x**2 + 2*x*y + y**2 - 1  # Rotated conic
        ]
        
        for expr in expressions:
            conic = ConicSection(expr, variables=(x, y))
            assert conic.expression == expr
            assert conic.variables == (x, y)
    
    def test_constructor_with_non_degree_2_polynomial_warning(self):
        """Test constructor behavior with non-degree-2 expressions"""
        x, y = sp.symbols('x y')
        
        # These should still work (ConicSection can handle them) but might not be true conics
        linear_expr = x + y - 1  # Degree 1
        cubic_expr = x**3 + y**3 - 1  # Degree 3
        
        # Should not raise error but might give unexpected conic_type results
        linear_conic = ConicSection(linear_expr, variables=(x, y))
        cubic_conic = ConicSection(cubic_expr, variables=(x, y))
        
        assert linear_conic.expression == linear_expr
        assert cubic_conic.expression == cubic_expr


class TestConicSectionConicType:
    """Test ConicSection conic_type method - Sprint 2 Task GEO-S2-T1"""
    
    def setup_method(self):
        """Set up test conic sections"""
        x, y = sp.symbols('x y')
        
        # Standard conic sections
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2/9 - 1, variables=(x, y))
        self.parabola = ConicSection(y - x**2, variables=(x, y))
        self.hyperbola = ConicSection(x**2 - y**2 - 1, variables=(x, y))
        
        # Translated conics (not centered at origin)
        self.translated_circle = ConicSection(x**2 + 2*x + y**2 - 3, variables=(x, y))
        self.translated_ellipse = ConicSection((x-1)**2/4 + (y+2)**2/9 - 1, variables=(x, y))
        
        # Rotated conic (has xy term)
        self.rotated_conic = ConicSection(x**2 + 2*x*y + y**2 - 1, variables=(x, y))
        
        # Degenerate cases
        self.degenerate_point = ConicSection(x**2 + y**2, variables=(x, y))  # Point at origin
        self.degenerate_lines = ConicSection(x**2 - y**2, variables=(x, y))  # Two intersecting lines
    
    def test_conic_type_circle(self):
        """Test conic_type identification for circles"""
        assert self.circle.conic_type() == "circle"
        assert self.translated_circle.conic_type() == "circle"
    
    def test_conic_type_ellipse(self):
        """Test conic_type identification for ellipses"""
        assert self.ellipse.conic_type() == "ellipse"
        assert self.translated_ellipse.conic_type() == "ellipse"
    
    def test_conic_type_parabola(self):
        """Test conic_type identification for parabolas"""
        assert self.parabola.conic_type() == "parabola"
        
        # Additional parabola forms
        x, y = sp.symbols('x y')
        parabola_x = ConicSection(x - y**2, variables=(x, y))
        assert parabola_x.conic_type() == "parabola"
    
    def test_conic_type_hyperbola(self):
        """Test conic_type identification for hyperbolas"""
        assert self.hyperbola.conic_type() == "hyperbola"
        
        # Additional hyperbola forms
        x, y = sp.symbols('x y')
        hyperbola_alt = ConicSection(y**2 - x**2 - 1, variables=(x, y))
        assert hyperbola_alt.conic_type() == "hyperbola"
    
    def test_conic_type_degenerate_cases(self):
        """Test conic_type identification for degenerate cases"""
        # These might return "degenerate" or specific subtypes
        result_point = self.degenerate_point.conic_type()
        result_lines = self.degenerate_lines.conic_type()
        
        # Should return some form of degenerate classification
        assert result_point in ["degenerate", "point", "circle"]  # Point could be degenerate circle
        assert result_lines in ["degenerate", "hyperbola", "lines"]  # Lines could be degenerate hyperbola
    
    def test_conic_type_rotated_conic(self):
        """Test conic_type for rotated conics with xy terms"""
        # This has B²-4AC = 4-4 = 0, so it's a parabola
        assert self.rotated_conic.conic_type() == "parabola"
    
    def test_conic_type_returns_string(self):
        """Test that conic_type always returns a string"""
        test_conics = [self.circle, self.ellipse, self.parabola, self.hyperbola]
        
        for conic in test_conics:
            result = conic.conic_type()
            assert isinstance(result, str)
            assert len(result) > 0


class TestConicSectionDegree:
    """Test ConicSection degree method - Sprint 2 Task GEO-S2-T1"""
    
    def test_degree_always_returns_2(self):
        """Test that degree method consistently returns 2 for conic sections"""
        x, y = sp.symbols('x y')
        
        # Various conic expressions
        expressions = [
            x**2 + y**2 - 1,  # Circle
            x**2/4 + y**2/9 - 1,  # Ellipse
            y - x**2,  # Parabola
            x**2 - y**2 - 1,  # Hyperbola
            x**2 + 2*x*y + y**2 - 1,  # Rotated conic
            x**2 + 2*x + y**2 + 3*y - 5,  # Translated conic
        ]
        
        for expr in expressions:
            conic = ConicSection(expr, variables=(x, y))
            assert conic.degree() == 2
    
    def test_degree_returns_integer(self):
        """Test that degree method returns an integer"""
        x, y = sp.symbols('x y')
        conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        result = conic.degree()
        assert isinstance(result, int)
        assert result == 2


class TestConicSectionInheritedMethods:
    """Test that ConicSection properly inherits and works with ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test conic sections"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2/9 - 1, variables=(x, y))
    
    def test_evaluate_method_inherited(self):
        """Test that evaluate method works correctly"""
        # Circle tests
        assert self.circle.evaluate(0.0, 0.0) < 0  # Inside
        assert abs(self.circle.evaluate(1.0, 0.0)) < 1e-10  # On curve
        assert self.circle.evaluate(2.0, 0.0) > 0  # Outside
        
        # Ellipse tests
        assert self.ellipse.evaluate(0.0, 0.0) < 0  # Inside
        assert abs(self.ellipse.evaluate(2.0, 0.0)) < 1e-10  # On curve (a=2)
        assert abs(self.ellipse.evaluate(0.0, 3.0)) < 1e-10  # On curve (b=3)
    
    def test_gradient_method_inherited(self):
        """Test that gradient method works correctly"""
        # Circle gradient at (1,0) should be (2,0)
        grad_x, grad_y = self.circle.gradient(1.0, 0.0)
        assert abs(grad_x - 2.0) < 1e-10
        assert abs(grad_y - 0.0) < 1e-10
        
        # Ellipse gradient
        grad_x, grad_y = self.ellipse.gradient(2.0, 0.0)
        assert abs(grad_x - 1.0) < 1e-10  # d/dx(x²/4) at x=2 is 2*2/4 = 1
        assert abs(grad_y - 0.0) < 1e-10
    
    def test_normal_method_inherited(self):
        """Test that normal method works correctly"""
        # Circle normal at (1,0) should be (1,0)
        nx, ny = self.circle.normal(1.0, 0.0)
        assert abs(nx - 1.0) < 1e-10
        assert abs(ny - 0.0) < 1e-10
        
        # Normal should be unit length
        magnitude = np.sqrt(nx**2 + ny**2)
        assert abs(magnitude - 1.0) < 1e-10


class TestConicSectionSerialization:
    """Test ConicSection serialization with specialized type"""
    
    def setup_method(self):
        """Set up test conic sections"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2/9 - 1, variables=(x, y))
    
    def test_to_dict_has_conic_section_type(self):
        """Test that to_dict returns type 'ConicSection'"""
        data = self.circle.to_dict()
        
        assert isinstance(data, dict)
        assert data["type"] == "ConicSection"
        assert "expression" in data
        assert "variables" in data
    
    def test_from_dict_reconstruction(self):
        """Test that from_dict can reconstruct ConicSection"""
        # Serialize and deserialize
        data = self.circle.to_dict()
        reconstructed = ConicSection.from_dict(data)
        
        # Should be ConicSection instance
        assert isinstance(reconstructed, ConicSection)
        assert isinstance(reconstructed, ImplicitCurve)
        
        # Should have same conic type
        assert reconstructed.conic_type() == self.circle.conic_type()
        assert reconstructed.degree() == 2
    
    def test_serialization_round_trip_functional_equivalence(self):
        """Test that serialization preserves functional behavior"""
        test_conics = [self.circle, self.ellipse]
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
        
        for conic in test_conics:
            # Serialize and deserialize
            data = conic.to_dict()
            reconstructed = ConicSection.from_dict(data)
            
            # Test functional equivalence
            for x, y in test_points:
                orig_val = conic.evaluate(x, y)
                recon_val = reconstructed.evaluate(x, y)
                assert abs(orig_val - recon_val) < 1e-10
                
                # Test gradient equivalence
                orig_grad = conic.gradient(x, y)
                recon_grad = reconstructed.gradient(x, y)
                assert abs(orig_grad[0] - recon_grad[0]) < 1e-10
                assert abs(orig_grad[1] - recon_grad[1]) < 1e-10
    
    def test_from_dict_invalid_type_handling(self):
        """Test that from_dict handles invalid types appropriately"""
        # Test with wrong type
        with pytest.raises(ValueError, match="Invalid type"):
            ConicSection.from_dict({"type": "WrongType", "expression": "x**2 + y**2 - 1"})
        
        # Test with ImplicitCurve type (should work via base class)
        data = {"type": "ImplicitCurve", "expression": "x**2 + y**2 - 1", "variables": ["x", "y"]}
        reconstructed = ConicSection.from_dict(data)
        assert isinstance(reconstructed, ConicSection)


class TestConicSectionSpecializedMethods:
    """Test ConicSection specialized methods beyond basic interface"""
    
    def setup_method(self):
        """Set up test conic sections"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    
    def test_str_representation(self):
        """Test string representation"""
        str_repr = str(self.circle)
        assert "x**2 + y**2 - 1" in str_repr or "x^2 + y^2 - 1" in str_repr
        assert "= 0" in str_repr
    
    def test_repr_representation(self):
        """Test detailed representation"""
        repr_str = repr(self.circle)
        assert "ConicSection" in repr_str
        assert "x**2 + y**2 - 1" in repr_str or "x^2 + y^2 - 1" in repr_str
