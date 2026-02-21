#!/usr/bin/env python3
"""
Comprehensive test suite for CompositeCurve functionality
"""

import pytest
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from geometry import *

class TestCompositeCurveBasics:
    """Test basic CompositeCurve functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.x, self.y = sp.symbols('x y')
        
        # Create simple line segments for testing
        self.line1 = PolynomialCurve(self.y, (self.x, self.y))  # y = 0
        self.line2 = PolynomialCurve(self.x - 1, (self.x, self.y))  # x = 1
        self.line3 = PolynomialCurve(self.y - 1, (self.x, self.y))  # y = 1
        self.line4 = PolynomialCurve(self.x, (self.x, self.y))  # x = 0
        
        # Create circle for testing
        self.circle = ConicSection(self.x**2 + self.y**2 - 1, (self.x, self.y))
    
    def test_constructor_basic(self):
        """Test basic constructor functionality"""
        # Create simple segments
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1)
        
        # Should work without continuity validation
        composite = CompositeCurve([seg1, seg2])
        
        assert len(composite.segments) == 2
        assert isinstance(composite, CompositeCurve)
        assert isinstance(composite, ImplicitCurve)
    
    def test_constructor_empty_segments(self):
        """Test constructor with empty segments list"""
        with pytest.raises(ValueError, match="at least one segment"):
            CompositeCurve([])
    
    def test_constructor_invalid_segments(self):
        """Test constructor with invalid segment types"""
        with pytest.raises(TypeError, match="must be TrimmedImplicitCurve"):
            CompositeCurve([self.line1])  # Not a TrimmedImplicitCurve
    
    def test_evaluate_method(self):
        """Test evaluate method works"""
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1)
        composite = CompositeCurve([seg1, seg2])
        
        # Should return minimum of segment evaluations
        result = composite.evaluate(0.5, 0.5)
        assert isinstance(result, (int, float))
        
        # Test vectorized evaluation
        X = np.array([0.5, 1.0])
        Y = np.array([0.5, 0.5])
        results = composite.evaluate(X, Y)
        assert isinstance(results, np.ndarray)
        assert len(results) == 2
    
    def test_contains_method(self):
        """Test contains method works"""
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        composite = CompositeCurve([seg1])
        
        # Point on the line segment
        assert composite.contains(0.5, 0.0, tolerance=0.1)
        
        # Point not on the line
        assert not composite.contains(0.5, 0.5, tolerance=0.1)
        
        # Test vectorized
        X = np.array([0.5, 0.5])
        Y = np.array([0.0, 0.5])
        results = composite.contains(X, Y, tolerance=0.1)
        assert isinstance(results, np.ndarray)
        assert results[0] == True  # On line
        assert results[1] == False  # Not on line
    
    def test_on_curve_method(self):
        """Test on_curve method works"""
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        composite = CompositeCurve([seg1])
        
        # Point on the curve
        assert composite.on_curve(0.5, 0.0, tolerance=0.1)
        
        # Point not on the curve
        assert not composite.on_curve(0.5, 0.5, tolerance=0.1)
    
    def test_bounding_box(self):
        """Test bounding box calculation"""
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1, 
                                   xmin=0, xmax=1, ymin=-0.1, ymax=0.1)
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1,
                                   xmin=0.9, xmax=1.1, ymin=0, ymax=1)
        composite = CompositeCurve([seg1, seg2])
        
        bbox = composite.bounding_box()
        assert len(bbox) == 4
        x_min, x_max, y_min, y_max = bbox
        assert x_min <= x_max
        assert y_min <= y_max


class TestCompositeCurveSquare:
    """Test CompositeCurve with square creation"""
    
    def test_create_square_basic(self):
        """Test creating a square using factory function"""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        assert isinstance(square, CompositeCurve)
        assert len(square.segments) == 4
        assert square.is_closed()
    
    def test_square_contains_points(self):
        """Test square contains method"""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        # Point inside square
        assert square.contains(0, 0, region_containment=True)
        
        # Point on boundary
        assert square.contains(1, 0, tolerance=0.1)
        
        # Point outside square
        assert not square.contains(2, 2, region_containment=True)
    
    def test_square_evaluate(self):
        """Test square evaluate method"""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        # Inside should be negative
        inside_val = square.evaluate(0, 0)
        assert inside_val <= 0
        
        # Outside should be positive
        outside_val = square.evaluate(2, 2)
        assert outside_val > 0


class TestCompositeCurveCircle:
    """Test CompositeCurve with circle creation"""
    
    def test_create_circle_quarters(self):
        """Test creating circle from quarters"""
        circle = create_circle_from_quarters(center=(0, 0), radius=1.0)
        
        assert isinstance(circle, CompositeCurve)
        assert len(circle.segments) == 4
        assert circle.is_closed()
    
    def test_circle_contains_points(self):
        """Test circle contains method"""
        circle = create_circle_from_quarters(center=(0, 0), radius=1.0)
        
        # Point inside circle
        assert circle.contains(0, 0, region_containment=True)
        
        # Point on boundary
        assert circle.contains(1, 0, tolerance=0.1)
        
        # Point outside circle
        assert not circle.contains(2, 0, region_containment=True)


class TestCompositeCurveContinuity:
    """Test CompositeCurve continuity validation"""
    
    def setup_method(self):
        """Set up test data"""
        self.x, self.y = sp.symbols('x y')
        self.line1 = PolynomialCurve(self.y, (self.x, self.y))
        self.line2 = PolynomialCurve(self.x - 1, (self.x, self.y))
    
    def test_continuity_validation_disabled_by_default(self):
        """Test that continuity validation is disabled by default"""
        # Create disconnected segments
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 2 <= y <= 3)  # Gap!
        
        # Should work with default settings (no validation)
        composite = CompositeCurve([seg1, seg2])
        assert len(composite.segments) == 2
    
    def test_continuity_validation_with_endpoints(self):
        """Test continuity validation when endpoints are provided"""
        # Create connected segments with endpoints
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1,
                                   endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1,
                                   endpoints=[(1, 0), (1, 1)])
        
        # Should work with validation enabled
        composite = CompositeCurve([seg1, seg2], validate_continuity=True)
        assert len(composite.segments) == 2
    
    def test_continuity_validation_fails_with_gap(self):
        """Test continuity validation fails with disconnected segments"""
        # Create disconnected segments with endpoints
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1,
                                   endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1,
                                   endpoints=[(2, 1), (2, 2)])  # Gap!
        
        # Should fail with validation enabled
        with pytest.raises(ValueError, match="Gap of .* exceeds tolerance"):
            CompositeCurve([seg1, seg2], validate_continuity=True)
    
    def test_continuity_validation_missing_endpoints(self):
        """Test continuity validation fails when endpoints missing"""
        # Create segments without endpoints
        seg1 = TrimmedImplicitCurve(self.line1, lambda x, y: 0 <= x <= 1)
        seg2 = TrimmedImplicitCurve(self.line2, lambda x, y: 0 <= y <= 1)
        
        # Should fail with validation enabled
        with pytest.raises(ValueError, match="missing endpoint information"):
            CompositeCurve([seg1, seg2], validate_continuity=True)


class TestCompositeCurveComplexShapes:
    """Test CompositeCurve with complex shapes"""
    
    def setup_method(self):
        """Set up test data"""
        self.x, self.y = sp.symbols('x y')
    
    def test_create_triangle(self):
        """Test creating a triangle"""
        # Create triangle with proper endpoints
        line1 = PolynomialCurve(self.y + 0.5, (self.x, self.y))  # Bottom edge
        line2 = PolynomialCurve(self.y + 1.5*self.x - 1, (self.x, self.y))  # Right edge
        line3 = PolynomialCurve(self.y - 1.5*self.x - 1, (self.x, self.y))  # Left edge
        
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: -1 <= x <= 1,
                                   endpoints=[(-1, -0.5), (1, -0.5)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: 0 <= x <= 1,
                                   endpoints=[(1, -0.5), (0, 1)])
        seg3 = TrimmedImplicitCurve(line3, lambda x, y: -1 <= x <= 0,
                                   endpoints=[(0, 1), (-1, -0.5)])
        
        triangle = CompositeCurve([seg1, seg2, seg3], validate_continuity=True)
        
        assert len(triangle.segments) == 3
        assert triangle.is_closed()
    
    def test_create_L_shape(self):
        """Test creating an L-shape"""
        line1 = PolynomialCurve(self.x + 0.5, (self.x, self.y))  # Vertical
        line2 = PolynomialCurve(self.y + 1, (self.x, self.y))    # Horizontal
        
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: -1 <= y <= 0,
                                   endpoints=[(-0.5, -1), (-0.5, 0)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: -0.5 <= x <= 0.5,
                                   endpoints=[(-0.5, -1), (0.5, -1)])
        
        l_shape = CompositeCurve([seg1, seg2], validate_continuity=True)
        
        assert len(l_shape.segments) == 2
        assert not l_shape.is_closed()  # L-shape is open


class TestCompositeCurvePlotting:
    """Test CompositeCurve plotting functionality"""
    
    def test_plot_method_exists(self):
        """Test that plot method exists and works"""
        x, y = sp.symbols('x y')
        line = PolynomialCurve(y, (x, y))
        seg = TrimmedImplicitCurve(line, lambda x, y: 0 <= x <= 1)
        composite = CompositeCurve([seg])
        
        # Should not raise an error
        fig, ax = plt.subplots()
        composite.plot(ax=ax)
        plt.close(fig)
    
    def test_plot_square(self):
        """Test plotting a square"""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        fig, ax = plt.subplots()
        square.plot(ax=ax)
        plt.close(fig)


class TestCompositeCurveSerializationAndUtilities:
    """Test CompositeCurve serialization and utility methods"""
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization"""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        # Serialize
        data = square.to_dict()
        assert isinstance(data, dict)
        assert data["type"] == "CompositeCurve"
        assert "segments" in data
        
        # Deserialize
        restored = CompositeCurve.from_dict(data)
        assert isinstance(restored, CompositeCurve)
        assert len(restored.segments) == len(square.segments)
    
    def test_segment_access_methods(self):
        """Test segment access and manipulation methods"""
        x, y = sp.symbols('x y')
        line = PolynomialCurve(y, (x, y))
        seg1 = TrimmedImplicitCurve(line, lambda x, y: 0 <= x <= 1)
        seg2 = TrimmedImplicitCurve(line, lambda x, y: 1 <= x <= 2)
        
        composite = CompositeCurve([seg1])
        
        # Test get_segment_count
        assert composite.get_segment_count() == 1
        
        # Test get_segment
        retrieved = composite.get_segment(0)
        assert retrieved == seg1
        
        # Test add_segment
        composite.add_segment(seg2)
        assert composite.get_segment_count() == 2
        
        # Test __len__
        assert len(composite) == 2
        
        # Test __getitem__
        assert composite[0] == seg1
        assert composite[1] == seg2
        
        # Test __iter__
        segments = list(composite)
        assert len(segments) == 2
    
    def test_string_representations(self):
        """Test string representation methods"""
        x, y = sp.symbols('x y')
        line = PolynomialCurve(y, (x, y))
        seg = TrimmedImplicitCurve(line, lambda x, y: 0 <= x <= 1)
        composite = CompositeCurve([seg])
        
        # Test __str__
        str_repr = str(composite)
        assert "CompositeCurve" in str_repr
        assert "1 segments" in str_repr
        
        # Test __repr__
        repr_str = repr(composite)
        assert "CompositeCurve" in repr_str


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🧪 RUNNING COMPREHENSIVE COMPOSITE CURVE TESTS")
    print("=" * 60)
    
    # Run pytest on this file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    if success:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")