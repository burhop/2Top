"""
Test suite for Sprint 5 Serialization - TrimmedImplicitCurve and CompositeCurve

Tests cover:
- TrimmedImplicitCurve to_dict/from_dict round-trip testing
- CompositeCurve to_dict/from_dict round-trip testing
- Serialization limitations and documented behavior
- Nested structure serialization
- Cross-class serialization compatibility
"""

import pytest
import sympy as sp
import numpy as np
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.composite_curve import CompositeCurve
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse


class TestTrimmedImplicitCurveSerialization:
    """Test TrimmedImplicitCurve serialization - Sprint 5 Task GEO-S5-T6"""
    
    def setup_method(self):
        """Set up test curves for serialization testing"""
        x, y = sp.symbols('x y')
        
        # Create various base curves
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # Create different mask functions
        self.right_half_mask = lambda x, y: x >= 0
        self.upper_half_mask = lambda x, y: y >= 0
        self.first_quadrant_mask = lambda x, y: x >= 0 and y >= 0
        
        # Create trimmed curves
        self.right_half_circle = TrimmedImplicitCurve(self.circle, self.right_half_mask)
        self.upper_half_ellipse = TrimmedImplicitCurve(self.ellipse, self.upper_half_mask)
        self.first_quad_poly = TrimmedImplicitCurve(self.poly, self.first_quadrant_mask)
    
    def test_to_dict_structure(self):
        """Test that to_dict produces correct structure"""
        serialized = self.right_half_circle.to_dict()
        
        assert serialized["type"] == "TrimmedImplicitCurve"
        assert "base_curve" in serialized
        assert "mask" in serialized
        assert "mask_description" in serialized
        assert "variables" in serialized
        
        # Base curve should be properly serialized
        assert serialized["base_curve"]["type"] == "ConicSection"
        
        # Mask should have placeholder
        assert serialized["mask"] == "<<FUNCTION_NOT_SERIALIZABLE>>"
        assert "cannot be serialized" in serialized["mask_description"]
    
    def test_serialization_round_trip_with_limitations(self):
        """Test serialization round-trip with documented limitations"""
        # Serialize
        serialized = self.right_half_circle.to_dict()
        
        # Deserialize
        restored = TrimmedImplicitCurve.from_dict(serialized)
        
        # Test that base curve is functionally equivalent
        test_points = [(0.0, 0.0), (1.0, 0.0), (-1.0, 0.0), (0.5, 0.5)]
        
        for x, y in test_points:
            orig_base_val = self.right_half_circle.base_curve.evaluate(x, y)
            rest_base_val = restored.base_curve.evaluate(x, y)
            assert abs(orig_base_val - rest_base_val) < 1e-10
        
        # Test that restored curve has placeholder mask
        assert hasattr(restored, '_deserialization_warning')
        assert "placeholder" in restored._deserialization_warning
        
        # Placeholder mask should always return True
        assert restored.mask(1.0, 0.0) == True
        assert restored.mask(-1.0, 0.0) == True
    
    def test_serialization_different_base_curves(self):
        """Test serialization with different base curve types"""
        curves = {
            "circle": self.right_half_circle,
            "ellipse": self.upper_half_ellipse,
            "polynomial": self.first_quad_poly
        }
        
        for name, curve in curves.items():
            # Serialize and deserialize
            serialized = curve.to_dict()
            restored = TrimmedImplicitCurve.from_dict(serialized)
            
            # Test base curve equivalence
            test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
            for x, y in test_points:
                orig_val = curve.base_curve.evaluate(x, y)
                rest_val = restored.base_curve.evaluate(x, y)
                assert abs(orig_val - rest_val) < 1e-10
            
            # Test that type is preserved
            assert type(restored.base_curve) == type(curve.base_curve)
    
    def test_serialization_preserves_variables(self):
        """Test that serialization preserves variable symbols"""
        serialized = self.right_half_circle.to_dict()
        restored = TrimmedImplicitCurve.from_dict(serialized)
        
        # Variables should be preserved
        assert len(restored.variables) == 2
        assert all(isinstance(var, sp.Symbol) for var in restored.variables)
        
        # Variable names should match
        orig_names = [str(var) for var in self.right_half_circle.variables]
        rest_names = [str(var) for var in restored.variables]
        assert orig_names == rest_names
    
    def test_serialization_mask_limitation_documentation(self):
        """Test that mask serialization limitations are properly documented"""
        serialized = self.right_half_circle.to_dict()
        
        # Should contain clear documentation about limitations
        assert "mask" in serialized
        assert "mask_description" in serialized
        assert serialized["mask"] == "<<FUNCTION_NOT_SERIALIZABLE>>"
        assert "Manual reconstruction required" in serialized["mask_description"]
        
        # Deserialized curve should have warning
        restored = TrimmedImplicitCurve.from_dict(serialized)
        assert hasattr(restored, '_deserialization_warning')
        assert "placeholder" in restored._deserialization_warning.lower()


class TestCompositeCurveSerialization:
    """Test CompositeCurve serialization - Sprint 5 Task GEO-S5-T6"""
    
    def setup_method(self):
        """Set up test curves for serialization testing"""
        x, y = sp.symbols('x y')
        
        # Create base circle
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create quarter-circle segments
        self.segments = [
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        # Create composite curves
        self.full_circle = CompositeCurve(self.segments)
        self.half_circle = CompositeCurve(self.segments[:2])  # First two quadrants
        
        # Create mixed base curve composite
        poly = PolynomialCurve(x + y - 1, variables=(x, y))
        mixed_segments = [
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(poly, lambda x, y: x >= 0 and x <= 1)
        ]
        self.mixed_composite = CompositeCurve(mixed_segments)
    
    def test_to_dict_structure(self):
        """Test that to_dict produces correct structure"""
        serialized = self.full_circle.to_dict()
        
        assert serialized["type"] == "CompositeCurve"
        assert "segments" in serialized
        assert "segment_count" in serialized
        assert "variables" in serialized
        
        # Should have correct number of segments
        assert serialized["segment_count"] == 4
        assert len(serialized["segments"]) == 4
        
        # Each segment should be properly serialized
        for segment_data in serialized["segments"]:
            assert segment_data["type"] == "TrimmedImplicitCurve"
            assert "base_curve" in segment_data
    
    def test_serialization_round_trip_full_circle(self):
        """Test serialization round-trip for full circle composite"""
        # Serialize and deserialize
        serialized = self.full_circle.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Test basic properties
        assert len(restored.segments) == len(self.full_circle.segments)
        assert restored.get_segment_count() == self.full_circle.get_segment_count()
        
        # Test functional equivalence for base curve evaluation
        test_points = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
        
        for x, y in test_points:
            orig_val = self.full_circle.evaluate(x, y)
            rest_val = restored.evaluate(x, y)
            assert abs(orig_val - rest_val) < 1e-10
        
        # Test that segment base curves are equivalent
        for i in range(len(self.full_circle.segments)):
            orig_segment = self.full_circle.segments[i]
            rest_segment = restored.segments[i]
            
            # Base curves should be functionally equivalent
            for x, y in test_points:
                orig_base_val = orig_segment.base_curve.evaluate(x, y)
                rest_base_val = rest_segment.base_curve.evaluate(x, y)
                assert abs(orig_base_val - rest_base_val) < 1e-10
    
    def test_serialization_round_trip_partial_circle(self):
        """Test serialization round-trip for partial circle composite"""
        # Serialize and deserialize
        serialized = self.half_circle.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Test basic properties
        assert len(restored.segments) == 2
        assert restored.get_segment_count() == 2
        
        # Test evaluation
        test_points = [(0.707, 0.707), (-0.707, 0.707)]
        
        for x, y in test_points:
            orig_val = self.half_circle.evaluate(x, y)
            rest_val = restored.evaluate(x, y)
            assert abs(orig_val - rest_val) < 1e-10
    
    def test_serialization_mixed_base_curves(self):
        """Test serialization with mixed base curve types"""
        # Serialize and deserialize
        serialized = self.mixed_composite.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Test that different base curve types are preserved
        assert len(restored.segments) == 2
        
        # First segment should have ConicSection base
        assert isinstance(restored.segments[0].base_curve, ConicSection)
        
        # Second segment should have PolynomialCurve base
        assert isinstance(restored.segments[1].base_curve, PolynomialCurve)
        
        # Test functional equivalence
        test_points = [(0.5, 0.5), (0.5, 0.5)]
        
        for x, y in test_points:
            orig_val = self.mixed_composite.evaluate(x, y)
            rest_val = restored.evaluate(x, y)
            assert abs(orig_val - rest_val) < 1e-10
    
    def test_serialization_preserves_segment_order(self):
        """Test that serialization preserves segment order"""
        serialized = self.full_circle.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Segments should be in the same order
        assert len(restored.segments) == len(self.full_circle.segments)
        
        for i in range(len(self.full_circle.segments)):
            orig_segment = self.full_circle.segments[i]
            rest_segment = restored.segments[i]
            
            # Base curves should be the same type
            assert type(orig_segment.base_curve) == type(rest_segment.base_curve)
    
    def test_serialization_preserves_variables(self):
        """Test that serialization preserves variable symbols"""
        serialized = self.full_circle.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Variables should be preserved
        assert len(restored.variables) == 2
        assert all(isinstance(var, sp.Symbol) for var in restored.variables)
        
        # Variable names should match
        orig_names = [str(var) for var in self.full_circle.variables]
        rest_names = [str(var) for var in restored.variables]
        assert orig_names == rest_names
    
    def test_serialization_mask_limitations_propagated(self):
        """Test that mask serialization limitations are propagated to segments"""
        serialized = self.full_circle.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # All segments should have placeholder masks
        for segment in restored.segments:
            assert hasattr(segment, '_deserialization_warning')
            assert segment.mask(1.0, 0.0) == True  # Placeholder always returns True
            assert segment.mask(-1.0, 0.0) == True


class TestNestedCompositeCurveSerialization:
    """Test serialization of nested composite structures"""
    
    def setup_method(self):
        """Set up nested composite curves"""
        x, y = sp.symbols('x y')
        
        # Create base curves
        circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        circle2 = ConicSection((x-2)**2 + y**2 - 1, variables=(x, y))
        
        # Create segments for each circle
        segments1 = [
            TrimmedImplicitCurve(circle1, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(circle1, lambda x, y: x <= 0 and y >= 0)
        ]
        
        segments2 = [
            TrimmedImplicitCurve(circle2, lambda x, y: x >= 2 and y >= 0),
            TrimmedImplicitCurve(circle2, lambda x, y: x <= 2 and y >= 0)
        ]
        
        # Create individual composite curves
        self.composite1 = CompositeCurve(segments1)
        self.composite2 = CompositeCurve(segments2)
        
        # Create combined segments list
        all_segments = segments1 + segments2
        self.combined_composite = CompositeCurve(all_segments)
    
    def test_complex_composite_serialization(self):
        """Test serialization of complex composite with multiple base curves"""
        # Serialize and deserialize
        serialized = self.combined_composite.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Test basic properties
        assert len(restored.segments) == 4
        assert restored.get_segment_count() == 4
        
        # Test that base curves are preserved
        for i in range(len(self.combined_composite.segments)):
            orig_segment = self.combined_composite.segments[i]
            rest_segment = restored.segments[i]
            
            # Base curves should be functionally equivalent
            test_points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
            for x, y in test_points:
                orig_val = orig_segment.base_curve.evaluate(x, y)
                rest_val = rest_segment.base_curve.evaluate(x, y)
                assert abs(orig_val - rest_val) < 1e-10


class TestSerializationErrorHandling:
    """Test error handling in serialization"""
    
    def test_invalid_trimmed_curve_data(self):
        """Test error handling for invalid TrimmedImplicitCurve data"""
        # Missing type
        with pytest.raises(ValueError, match="Invalid type"):
            TrimmedImplicitCurve.from_dict({"base_curve": {}, "mask": ""})
        
        # Wrong type
        with pytest.raises(ValueError, match="Invalid type"):
            TrimmedImplicitCurve.from_dict({"type": "WrongType", "base_curve": {}, "mask": ""})
        
        # Missing base_curve
        with pytest.raises(KeyError):
            TrimmedImplicitCurve.from_dict({"type": "TrimmedImplicitCurve", "mask": ""})
    
    def test_invalid_composite_curve_data(self):
        """Test error handling for invalid CompositeCurve data"""
        # Missing type
        with pytest.raises(ValueError, match="Invalid type"):
            CompositeCurve.from_dict({"segments": []})
        
        # Wrong type
        with pytest.raises(ValueError, match="Invalid type"):
            CompositeCurve.from_dict({"type": "WrongType", "segments": []})
        
        # Missing segments
        with pytest.raises(KeyError):
            CompositeCurve.from_dict({"type": "CompositeCurve"})


class TestSerializationCompatibility:
    """Test serialization compatibility across different curve types"""
    
    def setup_method(self):
        """Set up curves with different base types"""
        x, y = sp.symbols('x y')
        
        # Create different base curve types
        self.conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        self.poly = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
        self.superellipse = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
        
        # Create trimmed versions
        self.trimmed_conic = TrimmedImplicitCurve(self.conic, lambda x, y: x >= 0)
        self.trimmed_poly = TrimmedImplicitCurve(self.poly, lambda x, y: y >= 0)
        self.trimmed_super = TrimmedImplicitCurve(self.superellipse, lambda x, y: x >= 0 and y >= 0)
        
        # Create composite with mixed types
        self.mixed_composite = CompositeCurve([
            self.trimmed_conic,
            self.trimmed_poly,
            self.trimmed_super
        ])
    
    def test_mixed_type_composite_serialization(self):
        """Test serialization of composite with mixed base curve types"""
        # Serialize and deserialize
        serialized = self.mixed_composite.to_dict()
        restored = CompositeCurve.from_dict(serialized)
        
        # Test that all base curve types are preserved
        assert len(restored.segments) == 3
        assert isinstance(restored.segments[0].base_curve, ConicSection)
        assert isinstance(restored.segments[1].base_curve, PolynomialCurve)
        assert isinstance(restored.segments[2].base_curve, Superellipse)
        
        # Test functional equivalence
        test_points = [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0)]
        
        for x, y in test_points:
            orig_val = self.mixed_composite.evaluate(x, y)
            rest_val = restored.evaluate(x, y)
            assert abs(orig_val - rest_val) < 1e-10


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
