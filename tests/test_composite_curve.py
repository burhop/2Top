"""
Test suite for CompositeCurve class - Sprint 5 Task GEO-S5-T3

Tests cover:
- Constructor validation and inheritance from ImplicitCurve
- is_closed method for checking connectivity of segments
- contains method for checking points on any segment
- Segment ordering and connectivity validation
- Interface compliance with ImplicitCurve methods
- Edge cases and error handling
"""

import math
import pytest
import sympy as sp
import numpy as np
from geometry.composite_curve import CompositeCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from tests.golden.loader import load_digest
from tests.helpers.builders import build_axis_aligned_rectangle, composite_perimeter
from tests.helpers.precision import PrecisionProfile, blended_tolerance


class TestCompositeCurveConstructor:
    """Test CompositeCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that CompositeCurve properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create quarter-circle segments
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        composite_curve = CompositeCurve(segments)
        
        # Should be instance of both CompositeCurve and ImplicitCurve
        assert isinstance(composite_curve, CompositeCurve)
        assert isinstance(composite_curve, ImplicitCurve)
    
    def test_constructor_with_various_segments(self):
        """Test constructor with different types of segments"""
        x, y = sp.symbols('x y')
        
        # Different base curves
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        line1 = PolynomialCurve(x - 1, variables=(x, y))
        line2 = PolynomialCurve(y - 1, variables=(x, y))
        
        # Create mixed segments
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(line1, lambda x, y: y >= 0 and y <= 1),
            TrimmedImplicitCurve(line2, lambda x, y: x >= 0 and x <= 1)
        ]
        
        composite_curve = CompositeCurve(segments)
        
        assert len(composite_curve.segments) == 3
        assert all(isinstance(seg, TrimmedImplicitCurve) for seg in composite_curve.segments)
    
    def test_constructor_parameter_validation(self):
        """Test constructor parameter validation"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        valid_segment = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
        
        # Valid construction
        composite_curve = CompositeCurve([valid_segment])
        assert len(composite_curve.segments) == 1
        
        # Empty segments list
        with pytest.raises(ValueError, match="at least one segment"):
            CompositeCurve([])
        
        # Invalid segment type
        with pytest.raises(TypeError, match="must be TrimmedImplicitCurve"):
            CompositeCurve([circle])  # Not a TrimmedImplicitCurve
        
        # Mixed invalid segments
        with pytest.raises(TypeError, match="must be TrimmedImplicitCurve"):
            CompositeCurve([valid_segment, "not a curve"])
    
    def test_constructor_preserves_segment_order(self):
        """Test that constructor preserves segment order"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create segments in specific order
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        composite_curve = CompositeCurve(segments)
        
        # Verify order is preserved
        for i, segment in enumerate(composite_curve.segments):
            assert segment == segments[i]


class TestCompositeCurveIsClosedMethod:
    """Test CompositeCurve is_closed method - Sprint 5 Task GEO-S5-T3"""
    
    def setup_method(self):
        """Set up test curves for is_closed testing"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create quarter-circle segments that form a closed loop
        self.closed_segments = [
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        # Create segments that don't form a closed loop
        self.open_segments = [
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            # Missing third and fourth quadrants
        ]
        
        self.closed_composite = CompositeCurve(self.closed_segments)
        self.open_composite = CompositeCurve(self.open_segments)
    
    def test_is_closed_for_complete_circle(self):
        """Test is_closed method for complete circle made of quarter segments"""
        # Four quarter-circles should form a closed curve
        assert self.closed_composite.is_closed() == True
    
    def test_is_closed_for_incomplete_circle(self):
        """Test is_closed method for incomplete circle"""
        # Two quarter-circles should not form a closed curve
        assert self.open_composite.is_closed() == False
    
    def test_is_closed_for_single_segment(self):
        """Test is_closed method for single segment"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Single segment cannot be closed
        single_segment = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
        single_composite = CompositeCurve([single_segment])
        
        assert single_composite.is_closed() == False
    
    def test_is_closed_connectivity_tolerance(self):
        """Test is_closed method with connectivity tolerance"""
        x, y = sp.symbols('x y')
        
        # Create line segments that should connect
        line1 = PolynomialCurve(y, variables=(x, y))  # x-axis
        line2 = PolynomialCurve(x - 1, variables=(x, y))  # Vertical line at x=1
        line3 = PolynomialCurve(y - 1, variables=(x, y))  # Horizontal line at y=1
        line4 = PolynomialCurve(x, variables=(x, y))  # y-axis
        
        # Create segments that form a square
        square_segments = [
            TrimmedImplicitCurve(line1, lambda x, y: x >= 0 and x <= 1),  # Bottom edge
            TrimmedImplicitCurve(line2, lambda x, y: y >= 0 and y <= 1),  # Right edge
            TrimmedImplicitCurve(line3, lambda x, y: x >= 0 and x <= 1),  # Top edge
            TrimmedImplicitCurve(line4, lambda x, y: y >= 0 and y <= 1),  # Left edge
        ]
        
        square_composite = CompositeCurve(square_segments)
        
        # Square should be closed
        assert square_composite.is_closed() == True
    
    def test_is_closed_with_gaps(self):
        """Test is_closed method with gaps between segments"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create segments with gaps
        gapped_segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0.1 and y >= 0.1),  # First quadrant with gap
            TrimmedImplicitCurve(circle, lambda x, y: x <= -0.1 and y >= 0.1),  # Second quadrant with gap
        ]
        
        gapped_composite = CompositeCurve(gapped_segments)
        
        # Should not be closed due to gaps
        assert gapped_composite.is_closed() == False


class TestCompositeCurveContainsMethod:
    """Test CompositeCurve contains method - Sprint 5 Task GEO-S5-T3"""
    
    def setup_method(self):
        """Set up test curves for contains method testing"""
        x, y = sp.symbols('x y')
        self.circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create quarter-circle segments
        self.segments = [
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(self.circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        self.composite_curve = CompositeCurve(self.segments)
    
    def test_contains_points_on_each_segment(self):
        """Test contains method for points on each component segment"""
        test_cases = [
            (1.0, 0.0, True, "Point on first/fourth quadrant boundary"),
            (0.0, 1.0, True, "Point on first/second quadrant boundary"),
            (-1.0, 0.0, True, "Point on second/third quadrant boundary"),
            (0.0, -1.0, True, "Point on third/fourth quadrant boundary"),
            (1/math.sqrt(2), 1/math.sqrt(2), True, "Point on first quadrant arc"),
            (-1/math.sqrt(2), 1/math.sqrt(2), True, "Point on second quadrant arc"),
            (-1/math.sqrt(2), -1/math.sqrt(2), True, "Point on third quadrant arc"),
            (1/math.sqrt(2), -1/math.sqrt(2), True, "Point on fourth quadrant arc")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.composite_curve.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_points_not_on_curve(self):
        """Test contains method for points not on the curve"""
        test_cases = [
            (0.0, 0.0, False, "Point at origin (inside circle)"),
            (2.0, 0.0, False, "Point outside circle"),
            (0.5, 0.5, False, "Point inside circle but not on boundary"),
            (1.5, 1.5, False, "Point outside circle")
        ]
        
        for x, y, expected, description in test_cases:
            result = self.composite_curve.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_with_partial_segments(self):
        """Test contains method with partial segments"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create only first and second quadrant segments
        partial_segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
        ]
        
        partial_composite = CompositeCurve(partial_segments)
        
        test_cases = [
            (1/math.sqrt(2), 1/math.sqrt(2), True, "Point on first quadrant arc"),
            (-1/math.sqrt(2), 1/math.sqrt(2), True, "Point on second quadrant arc"),
            (-1/math.sqrt(2), -1/math.sqrt(2), False, "Point on third quadrant arc (not included)"),
            (1/math.sqrt(2), -1/math.sqrt(2), False, "Point on fourth quadrant arc (not included)")
        ]
        
        for x, y, expected, description in test_cases:
            result = partial_composite.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"
    
    def test_contains_vectorized_input(self):
        """Test contains method with vectorized input"""
        # Test with numpy arrays
        x_vals = np.array([1.0, 0.0, -1.0, 0.0, 1/math.sqrt(2), -1/math.sqrt(2)])
        y_vals = np.array([0.0, 1.0, 0.0, -1.0, 1/math.sqrt(2), -1/math.sqrt(2)])
        
        results = self.composite_curve.contains(x_vals, y_vals)
        expected = np.array([True, True, True, True, True, True])
        
        np.testing.assert_array_equal(results, expected)
    
    def test_contains_tolerance_handling(self):
        """Test contains method with numerical tolerance"""
        # Points very close to the boundary should be considered on the curve
        tolerance_cases = [
            (1.0 + 1e-10, 0.0, True, "Point very close to circle boundary"),
            (1.0 - 1e-10, 0.0, True, "Point very close to circle boundary"),
            (0.0, 1.0 + 1e-10, True, "Point very close to circle boundary"),
            (0.0, 1.0 - 1e-10, True, "Point very close to circle boundary")
        ]
        
        for x, y, expected, description in tolerance_cases:
            result = self.composite_curve.contains(x, y)
            assert result == expected, f"Failed for {description}: point ({x}, {y})"


class TestCompositeCurveInheritedMethods:
    """Test that CompositeCurve properly inherits ImplicitCurve methods"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0)
        ]
        
        self.composite_curve = CompositeCurve(segments)
    
    def test_evaluate_method_inherited(self):
        """Test that evaluate method works correctly"""
        # For composite curves, evaluate should work based on a pseudo-distance metric
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5)]
        
        for x, y in test_points:
            result = self.composite_curve.evaluate(x, y)
            assert isinstance(result, (int, float, np.number))
            assert np.isfinite(result)
    
    def test_gradient_method_inherited(self):
        """Test that gradient method works correctly"""
        test_points = [(1.0, 0.0), (0.0, 1.0)]
        
        for x, y in test_points:
            try:
                grad_x, grad_y = self.composite_curve.gradient(x, y)
                assert isinstance(grad_x, (int, float, np.number))
                assert isinstance(grad_y, (int, float, np.number))
                assert np.isfinite(grad_x)
                assert np.isfinite(grad_y)
            except (ValueError, ZeroDivisionError):
                # Acceptable for singular points
                pass
    
    def test_variables_property_inherited(self):
        """Test that variables property works correctly"""
        assert len(self.composite_curve.variables) == 2
        assert all(isinstance(var, sp.Symbol) for var in self.composite_curve.variables)
    
    def test_plot_method_inherited(self):
        """Test that plot method is available"""
        assert hasattr(self.composite_curve, 'plot')


class TestCompositeCurveSpecializedMethods:
    """Test CompositeCurve specialized methods and properties"""
    
    def setup_method(self):
        """Set up test curves"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0)
        ]
        
        self.composite_curve = CompositeCurve(segments)
    
    def test_property_access(self):
        """Test access to CompositeCurve properties"""
        assert hasattr(self.composite_curve, 'segments')
        assert len(self.composite_curve.segments) == 2
        assert all(isinstance(seg, TrimmedImplicitCurve) for seg in self.composite_curve.segments)
    
    def test_string_representations(self):
        """Test string representations"""
        composite_str = str(self.composite_curve)
        assert "CompositeCurve" in composite_str
        
        composite_repr = repr(self.composite_curve)
        assert "CompositeCurve" in composite_repr
        assert "segments" in composite_repr
    
    def test_segment_count(self):
        """Test segment count property"""
        assert len(self.composite_curve.segments) == 2
        
        # Test with different number of segments
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        single_segment = [TrimmedImplicitCurve(circle, lambda x, y: x >= 0)]
        single_composite = CompositeCurve(single_segment)
        assert len(single_composite.segments) == 1
        
        four_segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0)
        ]
        four_composite = CompositeCurve(four_segments)
        assert len(four_composite.segments) == 4


class TestCompositeCurveConnectivity:
    """Test CompositeCurve connectivity analysis"""
    
    def setup_method(self):
        """Set up test curves for connectivity testing"""
        x, y = sp.symbols('x y')
        
        # Create line segments that form a square
        self.line1 = PolynomialCurve(y, variables=(x, y))  # x-axis
        self.line2 = PolynomialCurve(x - 1, variables=(x, y))  # Vertical line at x=1
        self.line3 = PolynomialCurve(y - 1, variables=(x, y))  # Horizontal line at y=1
        self.line4 = PolynomialCurve(x, variables=(x, y))  # y-axis
        
        # Create connected square segments
        self.connected_segments = [
            TrimmedImplicitCurve(self.line1, lambda x, y: x >= 0 and x <= 1),  # Bottom edge
            TrimmedImplicitCurve(self.line2, lambda x, y: y >= 0 and y <= 1),  # Right edge
            TrimmedImplicitCurve(self.line3, lambda x, y: x >= 0 and x <= 1),  # Top edge
            TrimmedImplicitCurve(self.line4, lambda x, y: y >= 0 and y <= 1),  # Left edge
        ]
        
        # Create disconnected segments
        self.disconnected_segments = [
            TrimmedImplicitCurve(self.line1, lambda x, y: x >= 0 and x <= 0.5),  # Partial bottom
            TrimmedImplicitCurve(self.line2, lambda x, y: y >= 0.5 and y <= 1),  # Partial right
        ]
        
        self.connected_composite = CompositeCurve(self.connected_segments)
        self.disconnected_composite = CompositeCurve(self.disconnected_segments)
    
    def test_connected_square_is_closed(self):
        """Test that connected square segments form a closed curve"""
        assert self.connected_composite.is_closed() == True
    
    def test_disconnected_segments_not_closed(self):
        """Test that disconnected segments don't form a closed curve"""
        assert self.disconnected_composite.is_closed() == False
    
    def test_segment_endpoints(self):
        """Test identification of segment endpoints"""
        # This is an internal method test - implementation dependent
        # The actual implementation would need methods to find segment endpoints
        pass


class TestCompositeCurveEdgeCases:
    """Test edge cases and error conditions for CompositeCurve"""
    
    def test_single_segment_composite(self):
        """Test CompositeCurve with single segment"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        single_segment = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
        single_composite = CompositeCurve([single_segment])
        
        # Should work but not be closed
        assert len(single_composite.segments) == 1
        assert single_composite.is_closed() == False
        
        # Contains should work for points on the segment
        assert single_composite.contains(1.0, 0.5, region_containment=True)
        assert not single_composite.contains(2.0, 0.5, region_containment=True)


class TestCompositeCurvePrecisionBehavior:
    """Test CompositeCurve constructor and inheritance"""
    
    def test_constructor_inherits_from_implicit_curve(self):
        """Test that CompositeCurve properly inherits from ImplicitCurve"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create quarter-circle segments
        segments = [
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # First quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Second quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),  # Third quadrant
            TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),  # Fourth quadrant
        ]
        
        composite_curve = CompositeCurve(segments)
        
        # Should be instance of both CompositeCurve and ImplicitCurve
        assert isinstance(composite_curve, CompositeCurve)
        assert isinstance(composite_curve, ImplicitCurve)


class TestCompositeCurveGoldenDigests:
    def test_unit_square_matches_digest(self):
        digest = load_digest("composite_square")["unit_square"]
        rect = build_axis_aligned_rectangle(0.0, 0.0, 1.0, 1.0)
        bbox = rect.bounding_box()
        computed_area = (bbox[1] - bbox[0]) * (bbox[3] - bbox[2])
        computed_perimeter = composite_perimeter(rect)

        assert pytest.approx(computed_area, rel=1e-9) == digest["area"]
        assert pytest.approx(computed_perimeter, rel=1e-9) == digest["perimeter"]
        assert list(map(float, bbox)) == pytest.approx(digest["bounding_box"], rel=1e-9)
    
    def test_identical_segments(self):
        """Test CompositeCurve with identical segments"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        segment = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
        identical_composite = CompositeCurve([segment, segment])
        
        # Should work but may have overlapping coverage
        assert len(identical_composite.segments) == 2
        assert identical_composite.contains(1.0, 0.0) == True
    
    def test_overlapping_segments(self):
        """Test CompositeCurve with overlapping segments"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        # Create overlapping segments
        segment1 = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)  # Right half
        segment2 = TrimmedImplicitCurve(circle, lambda x, y: y >= 0)  # Upper half
        
        segment2 = TrimmedImplicitCurve(circle, lambda x, y: y >= 0)  # Upper half
        
        overlapping_composite = CompositeCurve([segment1, segment2])
        
        # Should work - contains should return True if point is on any segment
        assert overlapping_composite.contains(1.0, 0.0) == True  # On both segments
        assert overlapping_composite.contains(0.0, 1.0) == True  # On both segments
        assert overlapping_composite.contains(1/math.sqrt(2), 1/math.sqrt(2)) == True  # On both segments


class TestCompositeCurveExtensive:
    """Extensive unit and functional test cases for CompositeCurve"""
    
    global create_square_from_edges, create_polygon_from_edges
    from geometry.composite_curve import create_square_from_edges, create_polygon_from_edges

    def test_connectivity_extended(self):
        """Test extended closure paths: inherently closed conics with/without masks, rectangles, and sampling fallback"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))

        # 1. Inherently closed single segment with pass-through mask
        closed_single = TrimmedImplicitCurve(circle, lambda px, py: True)
        composite_single_closed = CompositeCurve([closed_single])
        assert composite_single_closed.is_closed() is True

        # 2. Inherently closed single segment with restrictive mask
        open_single = TrimmedImplicitCurve(circle, lambda px, py: px >= 0.0)
        composite_single_open = CompositeCurve([open_single])
        assert composite_single_open.is_closed() is False

        # 3. Square boundary created by factory (uses _is_closed_rectangle)
        square = create_square_from_edges((0.0, 0.0), (1.0, 1.0))
        assert square.is_closed() is True

        # 4. Sampling fallback when explicit endpoints are missing
        # Create segments without explicit endpoints
        seg1 = TrimmedImplicitCurve(circle, lambda px, py: px >= 0.0 and py >= 0.0)
        seg2 = TrimmedImplicitCurve(circle, lambda px, py: px <= 0.0 and py >= 0.0)
        seg3 = TrimmedImplicitCurve(circle, lambda px, py: px <= 0.0 and py <= 0.0)
        seg4 = TrimmedImplicitCurve(circle, lambda px, py: px >= 0.0 and py <= 0.0)
        
        # Clear endpoints to force sampling fallback
        seg1.endpoints = []
        seg2.endpoints = []
        seg3.endpoints = []
        seg4.endpoints = []
        
        composite_sampled = CompositeCurve([seg1, seg2, seg3, seg4])
        # It should fall back to sampling and identify it is closed
        assert composite_sampled.is_closed(tolerance=0.1) is True

    def test_ray_casting_concave_shapes(self):
        """Test ray-casting algorithm on a concave L-shaped polygon"""
        # An L-shape with vertices:
        # (0,0) -> (2,0) -> (2,1) -> (1,1) -> (1,2) -> (0,2) -> back to (0,0)
        vertices = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)]
        l_shape = create_polygon_from_edges(vertices)
        assert l_shape.is_closed() is True

        # Points inside the L-shape region
        assert l_shape.contains(0.5, 0.5, region_containment=True) is True
        assert l_shape.contains(1.5, 0.5, region_containment=True) is True
        assert l_shape.contains(0.5, 1.5, region_containment=True) is True

        # Point in the concave "cutout" (outside)
        assert l_shape.contains(1.5, 1.5, region_containment=True) is False
        # Far outside
        assert l_shape.contains(3.0, 3.0, region_containment=True) is False

    def test_fast_path_metadata_evaluation(self):
        """Test square and polygon fast-path evaluation and containment"""
        # 1. Square fast-path
        square = create_square_from_edges((0.0, 0.0), (2.0, 2.0))
        assert getattr(square, "_is_square", False) is True
        
        # Scalar checks
        assert square.contains(1.0, 1.0, region_containment=True) is True
        assert square.contains(-0.5, 1.0, region_containment=True) is False
        
        # Vectorized checks
        xs = np.array([1.0, 3.0, -0.1, 1.5])
        ys = np.array([1.0, 1.0, 1.5, 2.1])
        expected = np.array([True, False, False, False])
        np.testing.assert_array_equal(square.contains(xs, ys, region_containment=True), expected)

        # 2. Convex polygon fast-path
        # A triangle with vertices (0,0), (2,0), (0,2)
        triangle = create_polygon_from_edges([(0.0, 0.0), (2.0, 0.0), (0.0, 2.0)])
        assert getattr(triangle, "_is_convex_polygon", False) is True
        
        # Scalar and vectorized contains checks (which uses _edges_ab and _edges_c)
        assert triangle.contains(0.5, 0.5, region_containment=True) is True
        assert triangle.contains(1.5, 1.5, region_containment=True) is False
        
        np.testing.assert_array_equal(
            triangle.contains(np.array([0.5, 1.5]), np.array([0.5, 1.5]), region_containment=True),
            np.array([True, False])
        )

    def test_evaluation_active_segments(self):
        """Test general composite minimum evaluation and supporting segment gradients"""
        x, y = sp.symbols('x y')
        line_v = PolynomialCurve(x - 1, variables=(x, y))  # x = 1
        line_h = PolynomialCurve(y - 2, variables=(x, y))  # y = 2
        
        seg_v = TrimmedImplicitCurve(line_v, lambda px, py: py >= 0)
        seg_h = TrimmedImplicitCurve(line_h, lambda px, py: px >= 0)
        
        composite = CompositeCurve([seg_v, seg_h])
        
        # Evaluate should return minimum of the segment evaluations
        val_at_point = composite.evaluate(2.0, 3.0)
        expected_val = min(seg_v.evaluate(2.0, 3.0), seg_h.evaluate(2.0, 3.0))
        assert val_at_point == pytest.approx(expected_val)
        
        # Gradient should be selected from the active/supporting segment (minimal value)
        gx, gy = composite.gradient(2.0, 3.0)
        # At (2,3), evaluate for x=1 is 2-1=1. evaluate for y=2 is 3-2=1.
        # Let's test a point where one is clearly smaller: (1.5, 4.0) -> v is 0.5, h is 2.0. V segment is active.
        gx, gy = composite.gradient(1.5, 4.0)
        assert gx == pytest.approx(1.0)
        assert gy == pytest.approx(0.0)

    def test_segment_modification_apis(self):
        """Test adding, retrieving, counting, and removing segments along with index errors"""
        x, y = sp.symbols('x y')
        circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
        
        seg1 = TrimmedImplicitCurve(circle, lambda px, py: px >= 0.0)
        seg2 = TrimmedImplicitCurve(circle, lambda px, py: px <= 0.0)
        
        composite = CompositeCurve([seg1])
        assert composite.get_segment_count() == 1
        assert len(composite) == 1
        
        # Test add_segment
        composite.add_segment(seg2)
        assert composite.get_segment_count() == 2
        assert composite[1] == seg2
        
        # Test IndexError
        with pytest.raises(IndexError):
            composite.get_segment(5)
            
        # Test remove_segment
        composite.remove_segment(1)
        assert composite.get_segment_count() == 1
        assert composite[0] == seg1
        
        # Cannot remove last segment
        with pytest.raises(ValueError, match="Cannot remove the last remaining segment"):
            composite.remove_segment(0)

    def test_serialization_metadata_round_trip(self):
        """Test full dict round-trip preserving special tags like squares and convex polygons"""
        # 1. Square Serialization
        square = create_square_from_edges((0.0, 0.0), (3.0, 3.0))
        square_dict = square.to_dict()
        
        assert square_dict["is_square"] is True
        assert square_dict["square_bounds"] == (0.0, 3.0, 0.0, 3.0)
        
        reconstructed_square = CompositeCurve.from_dict(square_dict)
        assert getattr(reconstructed_square, "_is_square", False) is True
        assert reconstructed_square._square_bounds == (0.0, 3.0, 0.0, 3.0)

        # 2. Polygon Serialization
        triangle = create_polygon_from_edges([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
        poly_dict = triangle.to_dict()
        
        assert poly_dict["is_convex_polygon"] is True
        assert "convex_edges_abc" in poly_dict
        assert "polygon_vertices" in poly_dict
        
        reconstructed_poly = CompositeCurve.from_dict(poly_dict)
        assert getattr(reconstructed_poly, "_is_convex_polygon", False) is True
        assert hasattr(reconstructed_poly, "_convex_edges_abc")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
