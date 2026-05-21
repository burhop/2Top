"""
Test suite for AreaRegion class.

This module contains comprehensive tests for the AreaRegion class, covering:
- Constructor validation and error handling
- Point containment testing with complex regions and holes
- Area calculation using polygonal approximation
- Serialization and deserialization round-trips
- Edge cases and boundary conditions
"""

import pytest
import numpy as np
from geometry import (
    AreaRegion, CompositeCurve, TrimmedImplicitCurve, 
    ConicSection, PolynomialCurve, create_square_from_edges
)
import sympy as sp


class TestAreaRegionConstructor:
    """Test AreaRegion constructor and validation."""
    
    def test_constructor_with_valid_closed_boundary(self):
        """Test constructor with a valid closed boundary."""
        # Create a simple closed square boundary
        square = create_square_from_edges((-1, -1), (1, 1))
        
        # Should construct successfully
        region = AreaRegion(square)
        assert region.outer_boundary == square
        assert region.holes == []
    
    def test_constructor_with_holes(self):
        """Test constructor with holes."""
        # Create outer boundary (square)
        outer = create_square_from_edges((-2, -2), (2, 2))
        
        # Create hole (smaller square)
        hole = create_square_from_edges((-1, -1), (1, 1))
        
        # Should construct successfully
        region = AreaRegion(outer, [hole])
        assert region.outer_boundary == outer
        assert len(region.holes) == 1
        assert region.holes[0] == hole
    
    def test_constructor_with_multiple_holes(self):
        """Test constructor with multiple holes."""
        # Create outer boundary (large square)
        outer = create_square_from_edges((-3, -3), (3, 3))
        
        # Create multiple holes
        hole1 = create_square_from_edges((-2, -2), (-1, -1))
        hole2 = create_square_from_edges((1, 1), (2, 2))
        
        region = AreaRegion(outer, [hole1, hole2])
        assert len(region.holes) == 2
        assert region.holes[0] == hole1
        assert region.holes[1] == hole2
    
    def test_constructor_validates_outer_boundary_type(self):
        """Test that constructor validates outer_boundary type."""
        with pytest.raises(TypeError, match="outer_boundary must be a CompositeCurve"):
            AreaRegion("not a curve")
    
    def test_constructor_validates_outer_boundary_closed(self):
        """Test that constructor validates outer boundary is closed."""
        # Create an open curve (this would need to be implemented based on actual curve creation)
        # For now, we'll create a mock that returns False for is_closed()
        
        # Create a simple curve and modify it to be open
        x, y = sp.symbols('x y')
        line = PolynomialCurve(x - 1)  # Vertical line
        
        # Create a composite with just one segment (which might not be closed)
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
        trimmed = TrimmedImplicitCurve(line, lambda x, y: -1 <= y <= 1)
        
        # Create a composite that's not closed
        open_composite = CompositeCurve([trimmed])
        
        # This should raise an error if the composite is not closed
        # Note: The actual behavior depends on the is_closed() implementation
        try:
            region = AreaRegion(open_composite)
            # If no error, check that the boundary was actually closed
            assert open_composite.is_closed(), "Test setup error: boundary should be closed or raise error"
        except ValueError as e:
            assert "must be closed" in str(e)
    
    def test_constructor_validates_holes_type(self):
        """Test that constructor validates holes type."""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        with pytest.raises(TypeError, match="holes must be a list"):
            AreaRegion(square, "not a list")
    
    def test_constructor_validates_hole_types(self):
        """Test that constructor validates individual hole types."""
        square = create_square_from_edges((-1, -1), (1, 1))
        
        with pytest.raises(TypeError, match="holes\\[0\\] must be a CompositeCurve"):
            AreaRegion(square, ["not a curve"])
    
    def test_constructor_validates_holes_closed(self):
        """Test that constructor validates holes are closed."""
        outer = create_square_from_edges((-2, -2), (2, 2))
        
        # Create an open curve for hole
        x, y = sp.symbols('x y')
        line = PolynomialCurve(x)
        trimmed = TrimmedImplicitCurve(line, lambda x, y: -1 <= y <= 1)
        open_hole = CompositeCurve([trimmed])
        
        try:
            region = AreaRegion(outer, [open_hole])
            # If no error, the hole was actually closed
            assert open_hole.is_closed(), "Test setup error: hole should be closed or raise error"
        except ValueError as e:
            assert "must be closed" in str(e)
    
    def test_constructor_copies_holes_list(self):
        """Test that constructor creates a copy of the holes list."""
        outer = create_square_from_edges((-2, -2), (2, 2))
        hole = create_square_from_edges((-1, -1), (1, 1))
        
        original_holes = [hole]
        region = AreaRegion(outer, original_holes)
        
        # Modify original list
        original_holes.append(hole)
        
        # Region should still have only one hole
        assert len(region.holes) == 1


class TestAreaRegionContains:
    """Test AreaRegion.contains method."""
    
    def test_contains_simple_square_no_holes(self):
        """Test contains method with a simple square region."""
        # Create a 2x2 square centered at origin
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        # Test points inside
        assert region.contains(0, 0) == True  # Center
        assert region.contains(0.5, 0.5) == True  # Inside
        assert region.contains(-0.5, -0.5) == True  # Inside
        
        # Test points outside
        assert region.contains(2, 0) == False  # Right of square
        assert region.contains(0, 2) == False  # Above square
        assert region.contains(-2, 0) == False  # Left of square
        assert region.contains(0, -2) == False  # Below square
        
        # Test points on boundary (behavior may vary based on implementation)
        # These tests are more about ensuring consistent behavior
        boundary_result_1 = region.contains(1, 0)  # Right edge
        boundary_result_2 = region.contains(0, 1)  # Top edge
        # Just ensure they return boolean values
        assert isinstance(boundary_result_1, bool)
        assert isinstance(boundary_result_2, bool)
    
    def test_contains_square_with_circular_hole(self):
        """Test contains method with a square region containing a circular hole."""
        # Create outer boundary (4x4 square)
        outer = create_square_from_edges((-2, -2), (2, 2))
        
        # Create circular hole (radius 1, centered at origin)
        x, y = sp.symbols('x y')
        circle_expr = x**2 + y**2 - 1
        circle = ConicSection(circle_expr)
        
        # Create a composite curve from the circle (as a single segment)
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
        circle_trimmed = TrimmedImplicitCurve(circle, lambda x, y: True)  # Full circle
        circle_composite = CompositeCurve([circle_trimmed])
        
        region = AreaRegion(outer, [circle_composite])
        
        # Test points inside square but outside hole
        assert region.contains(1.5, 0) == True  # Right side of square, outside hole
        assert region.contains(0, 1.5) == True  # Top side of square, outside hole
        assert region.contains(-1.5, 0) == True  # Left side of square, outside hole
        assert region.contains(0, -1.5) == True  # Bottom side of square, outside hole
        
        # Test points inside hole (should be False)
        assert region.contains(0, 0) == False  # Center of hole
        assert region.contains(0.5, 0) == False  # Inside hole
        assert region.contains(0, 0.5) == False  # Inside hole
        
        # Test points outside square (should be False)
        assert region.contains(3, 0) == False  # Outside square
        assert region.contains(0, 3) == False  # Outside square
    
    def test_contains_multiple_holes(self):
        """Test contains method with multiple holes."""
        # Create outer boundary (6x6 square)
        outer = create_square_from_edges((-3, -3), (3, 3))
        
        # Create two square holes
        hole1 = create_square_from_edges((-2, -2), (-1, -1))  # Bottom-left
        hole2 = create_square_from_edges((1, 1), (2, 2))      # Top-right
        
        region = AreaRegion(outer, [hole1, hole2])
        
        # Test points inside outer boundary but outside holes
        assert region.contains(0, 0) == True  # Center, between holes
        assert region.contains(2.5, 0) == True  # Right side, outside holes
        assert region.contains(-2.5, 0) == True  # Left side, outside holes
        
        # Test points inside holes (should be False)
        assert region.contains(-1.5, -1.5) == False  # Inside hole1
        assert region.contains(1.5, 1.5) == False    # Inside hole2
        
        # Test points outside outer boundary
        assert region.contains(4, 0) == False  # Outside outer boundary
        assert region.contains(0, 4) == False  # Outside outer boundary
    
    def test_contains_edge_cases(self):
        """Test contains method with edge cases."""
        # Create a simple square
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        # Test with various numeric types
        assert isinstance(region.contains(0.0, 0.0), bool)
        assert isinstance(region.contains(0, 0), bool)
        assert isinstance(region.contains(np.float64(0.0), np.float64(0.0)), bool)


class TestAreaRegionArea:
    """Test AreaRegion.area method."""
    
    def test_area_simple_square(self):
        """Test area calculation for a simple square."""
        # Create a 2x2 square (area should be 4)
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        area = region.area()
        
        # Allow for some numerical approximation error
        assert abs(area - 4.0) < 0.5, f"Expected area ~4.0, got {area}"
        assert area > 0, "Area should be positive"
    
    def test_area_square_with_hole(self):
        """Test area calculation for a square with a hole."""
        # Create outer boundary (4x4 square, area = 16)
        outer = create_square_from_edges((-2, -2), (2, 2))
        
        # Create hole (2x2 square, area = 4)
        hole = create_square_from_edges((-1, -1), (1, 1))
        
        region = AreaRegion(outer, [hole])
        area = region.area()
        
        # Expected area = 16 - 4 = 12
        # Allow for numerical approximation error
        assert abs(area - 12.0) < 1.0, f"Expected area ~12.0, got {area}"
        assert area > 0, "Area should be positive"
    
    def test_area_multiple_holes(self):
        """Test area calculation with multiple holes."""
        # Create outer boundary (6x6 square, area = 36)
        outer = create_square_from_edges((-3, -3), (3, 3))
        
        # Create two holes (each 1x1 square, area = 1 each)
        hole1 = create_square_from_edges((-2, -2), (-1, -1))
        hole2 = create_square_from_edges((1, 1), (2, 2))
        
        region = AreaRegion(outer, [hole1, hole2])
        area = region.area()
        
        # Expected area = 36 - 1 - 1 = 34
        # Allow for numerical approximation error
        assert abs(area - 34.0) < 2.0, f"Expected area ~34.0, got {area}"
        assert area > 0, "Area should be positive"
    
    def test_area_no_holes(self):
        """Test area calculation with no holes."""
        # Create a 3x3 square (area should be 9)
        square = create_square_from_edges((-1.5, -1.5), (1.5, 1.5))
        region = AreaRegion(square)
        
        area = region.area()
        
        # Allow for numerical approximation error
        assert abs(area - 9.0) < 1.0, f"Expected area ~9.0, got {area}"
        assert area > 0, "Area should be positive"


class TestAreaRegionSerialization:
    """Test AreaRegion serialization and deserialization."""
    
    def test_to_dict_simple_region(self):
        """Test serialization of a simple region."""
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        data = region.to_dict()
        
        assert data['type'] == 'AreaRegion'
        assert 'outer_boundary' in data
        assert 'holes' in data
        assert isinstance(data['outer_boundary'], dict)
        assert isinstance(data['holes'], list)
        assert len(data['holes']) == 0
    
    def test_to_dict_region_with_holes(self):
        """Test serialization of a region with holes."""
        outer = create_square_from_edges((-2, -2), (2, 2))
        hole = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(outer, [hole])
        
        data = region.to_dict()
        
        assert data['type'] == 'AreaRegion'
        assert len(data['holes']) == 1
        assert isinstance(data['holes'][0], dict)
    
    def test_from_dict_simple_region(self):
        """Test deserialization of a simple region."""
        # Create original region
        square = create_square_from_edges((-1, -1), (1, 1))
        original = AreaRegion(square)
        
        # Serialize and deserialize
        data = original.to_dict()
        reconstructed = AreaRegion.from_dict(data)
        
        # Test that reconstructed region behaves similarly
        assert isinstance(reconstructed, AreaRegion)
        assert len(reconstructed.holes) == 0
        
        # Test some containment points
        test_points = [(0, 0), (0.5, 0.5), (2, 0), (0, 2)]
        for x, y in test_points:
            assert original.contains(x, y) == reconstructed.contains(x, y)
    
    def test_from_dict_region_with_holes(self):
        """Test deserialization of a region with holes."""
        # Create original region
        outer = create_square_from_edges((-2, -2), (2, 2))
        hole = create_square_from_edges((-1, -1), (1, 1))
        original = AreaRegion(outer, [hole])
        
        # Serialize and deserialize
        data = original.to_dict()
        reconstructed = AreaRegion.from_dict(data)
        
        # Test structure
        assert isinstance(reconstructed, AreaRegion)
        assert len(reconstructed.holes) == 1
        
        # Test some containment points
        test_points = [(0, 0), (1.5, 0), (0, 1.5), (3, 0)]
        for x, y in test_points:
            assert original.contains(x, y) == reconstructed.contains(x, y)
    
    def test_from_dict_invalid_type(self):
        """Test deserialization with invalid type."""
        invalid_data = {'type': 'NotAnAreaRegion'}
        
        with pytest.raises(ValueError, match="does not represent an AreaRegion"):
            AreaRegion.from_dict(invalid_data)
    
    def test_serialization_round_trip(self):
        """Test complete serialization round-trip."""
        # Create a complex region
        outer = create_square_from_edges((-3, -3), (3, 3))
        hole1 = create_square_from_edges((-2, -2), (-1, -1))
        hole2 = create_square_from_edges((1, 1), (2, 2))
        original = AreaRegion(outer, [hole1, hole2])
        
        # Round-trip serialization
        data = original.to_dict()
        reconstructed = AreaRegion.from_dict(data)
        
        # Test that areas are approximately equal
        original_area = original.area()
        reconstructed_area = reconstructed.area()
        assert abs(original_area - reconstructed_area) < 0.1
        
        # Test containment for multiple points
        test_points = [
            (0, 0),      # Between holes
            (-1.5, -1.5), # Inside hole1
            (1.5, 1.5),   # Inside hole2
            (2.5, 0),     # Outside holes, inside outer
            (4, 0)        # Outside outer
        ]
        
        for x, y in test_points:
            assert original.contains(x, y) == reconstructed.contains(x, y)


class TestAreaRegionStringRepresentation:
    """Test AreaRegion string representations."""
    
    def test_str_no_holes(self):
        """Test string representation with no holes."""
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        str_repr = str(region)
        assert "AreaRegion" in str_repr
        assert "outer_boundary" in str_repr
    
    def test_str_with_holes(self):
        """Test string representation with holes."""
        outer = create_square_from_edges((-2, -2), (2, 2))
        hole = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(outer, [hole])
        
        str_repr = str(region)
        assert "AreaRegion" in str_repr
        assert "holes=1" in str_repr
    
    def test_repr(self):
        """Test detailed representation."""
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        repr_str = repr(region)
        assert "AreaRegion" in repr_str
        assert "outer_boundary" in repr_str
        assert "holes" in repr_str


class TestAreaRegionExtensive:
    """Extensive tests for AreaRegion covering boundary containment, polygonal Shoelace area, field strategy integration, and error validations."""

    def test_boundary_containment(self):
        """Test contains_boundary(x, y) under various scenarios."""
        # Create a simple 2x2 square centered at the origin
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)
        
        # Points exactly on the boundary
        assert region.contains_boundary(1.0, 0.0) is True   # Right edge
        assert region.contains_boundary(0.0, 1.0) is True   # Top edge
        assert region.contains_boundary(-1.0, 0.0) is True  # Left edge
        assert region.contains_boundary(0.0, -1.0) is True  # Bottom edge
        
        # Points inside the region (not on the boundary)
        assert region.contains_boundary(0.0, 0.0) is False
        assert region.contains_boundary(0.5, 0.5) is False
        
        # Points outside the region (not on the boundary)
        assert region.contains_boundary(2.0, 2.0) is False
        assert region.contains_boundary(-1.5, 0.0) is False

        # Test with custom tolerance
        # A point slightly off the boundary (0.005 away)
        assert region.contains_boundary(1.005, 0.0, tolerance=1e-5) is False
        assert region.contains_boundary(1.005, 0.0, tolerance=1e-2) is True

        # Now test with holes
        outer = create_square_from_edges((-3, -3), (3, 3))
        hole = create_square_from_edges((-1, -1), (1, 1))
        region_with_hole = AreaRegion(outer, [hole])

        # Point on outer boundary
        assert region_with_hole.contains_boundary(3.0, 0.0) is True
        # Point on hole boundary
        assert region_with_hole.contains_boundary(1.0, 0.0) is True
        # Point inside region (between outer and hole)
        assert region_with_hole.contains_boundary(2.0, 2.0) is False
        # Point inside hole
        assert region_with_hole.contains_boundary(0.0, 0.0) is False

    def test_polygonal_area_calculation(self):
        """Test area calculations with polygonal approximations, non-squares, and holes."""
        from geometry.composite_curve import create_polygon_from_edges

        # 1. Triangle area (polygonal calculation using precise vertices)
        # Vertices (0, 0), (2, 0), (0, 2) has area 0.5 * 2 * 2 = 2.0
        triangle = create_polygon_from_edges([(0.0, 0.0), (2.0, 0.0), (0.0, 2.0)])
        tri_region = AreaRegion(triangle)
        assert np.isclose(tri_region.area(), 2.0)

        # 2. Circle area (curves approximated using high-resolution regular polygon to bypass grid sampling limits)
        # Approximate circle using 64-sided regular polygon
        def make_polygon_circle(radius, center=(0.0, 0.0), num_sides=64):
            cx, cy = center
            theta = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
            vertices = [(cx + radius * np.cos(t), cy + radius * np.sin(t)) for t in theta]
            return create_polygon_from_edges(vertices)

        circle_composite = make_polygon_circle(3.0)
        circle_region = AreaRegion(circle_composite)
        
        # Approximate area should be extremely close to 9 * pi
        assert np.isclose(circle_region.area(), 9.0 * np.pi, rtol=0.05)

        # 3. Annular/Holes area subtraction
        # Circle radius 3 with circle radius 1 hole. Area = pi * (3^2 - 1^2) = 8 * pi = ~25.132
        circle_hole_composite = make_polygon_circle(1.0)
        
        annular_region = AreaRegion(circle_composite, [circle_hole_composite])
        assert np.isclose(annular_region.area(), 8.0 * np.pi, rtol=0.05)

        # Subtracting multiple different holes
        # Square (-3, -3) to (3, 3) area = 36
        # Subtract triangle hole of area 2.0 and square hole of area 1.0 (from 0 to 1, 0 to 1)
        outer_square = create_square_from_edges((-3, -3), (3, 3))
        hole_tri = create_polygon_from_edges([(1.0, 1.0), (3.0, 1.0), (1.0, 3.0)])  # Area = 2.0
        hole_sq = create_square_from_edges((-2, -2), (-1, -1)) # Area = 1.0
        
        multi_hole_region = AreaRegion(outer_square, [hole_tri, hole_sq])
        # Area = 36 - 2.0 - 1.0 = 33.0
        assert np.isclose(multi_hole_region.area(), 33.0)

    def test_field_strategy_integration(self):
        """Test generating scalar fields using field strategy design pattern."""
        from geometry import SignedDistanceStrategy, OccupancyFillStrategy, SignedDistanceField, OccupancyField

        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)

        # 1. Signed Distance Strategy
        sdf_strategy = SignedDistanceStrategy(resolution=0.1)
        assert sdf_strategy.resolution == 0.1

        strat_dict = sdf_strategy.to_dict()
        assert strat_dict['type'] == 'SignedDistanceStrategy'
        reconstructed_strategy = SignedDistanceStrategy.from_dict(strat_dict)
        assert reconstructed_strategy.resolution == 0.1

        with pytest.raises(ValueError, match="does not represent a SignedDistanceStrategy"):
            SignedDistanceStrategy.from_dict({'type': 'Wrong'})

        with pytest.raises(ValueError, match="resolution must be positive"):
            SignedDistanceStrategy(resolution=-0.5)

        sdf = region.get_field(sdf_strategy)
        assert isinstance(sdf, SignedDistanceField)
        assert sdf.resolution == 0.1

        # Inside scalar evaluation (negative distance to boundary)
        val_inside = sdf.evaluate(0.0, 0.0)
        assert val_inside < 0
        assert np.isclose(val_inside, -1.0, atol=1.5e-2)

        # Outside scalar evaluation (positive distance to boundary)
        val_outside = sdf.evaluate(2.0, 0.0)
        assert val_outside > 0
        assert np.isclose(val_outside, 1.0, atol=1.5e-2)

        # Vectorized evaluation
        x_arr = np.array([0.0, 2.0])
        y_arr = np.array([0.0, 0.0])
        results = sdf.evaluate(x_arr, y_arr)
        assert np.allclose(results, [-1.0, 1.0], atol=1.5e-2)

        # NaN propagation
        x_nan = np.array([0.0, np.nan, 2.0])
        y_nan = np.array([0.0, 0.0, np.nan])
        results_nan = sdf.evaluate(x_nan, y_nan)
        assert np.isnan(results_nan[1])
        assert np.isnan(results_nan[2])
        assert np.isclose(results_nan[0], -1.0, atol=1.5e-2)

        # Gradient evaluation
        grad_x, grad_y = sdf.gradient(2.0, 0.0)
        assert np.isclose(grad_x, 1.0, atol=2e-2)
        assert np.isclose(grad_y, 0.0, atol=2e-2)

        # Level set extraction
        lvl_set = sdf.level_set(0.0)
        from geometry.procedural_curve import ProceduralCurve
        assert isinstance(lvl_set, ProceduralCurve)
        val_lvl = lvl_set.evaluate(1.0, 0.0)
        assert np.isclose(val_lvl, 0.0, atol=0.15)

        # Serialization round-trip
        sdf_dict = sdf.to_dict()
        assert sdf_dict['type'] == 'SignedDistanceField'
        reconstructed_sdf = SignedDistanceField.from_dict(sdf_dict)
        assert isinstance(reconstructed_sdf, SignedDistanceField)
        assert reconstructed_sdf.resolution == 0.1
        assert np.isclose(reconstructed_sdf.evaluate(0.0, 0.0), -1.0, atol=1.5e-2)

        with pytest.raises(ValueError, match="does not represent a SignedDistanceField"):
            SignedDistanceField.from_dict({'type': 'Wrong'})

        # 2. Occupancy Fill Strategy
        occ_strategy = OccupancyFillStrategy(inside_value=5.0, outside_value=-1.0)
        assert occ_strategy.inside_value == 5.0
        assert occ_strategy.outside_value == -1.0

        occ_strat_dict = occ_strategy.to_dict()
        assert occ_strat_dict['type'] == 'OccupancyFillStrategy'
        reconstructed_occ_strat = OccupancyFillStrategy.from_dict(occ_strat_dict)
        assert reconstructed_occ_strat.inside_value == 5.0
        assert reconstructed_occ_strat.outside_value == -1.0

        with pytest.raises(ValueError, match="does not represent an OccupancyFillStrategy"):
            OccupancyFillStrategy.from_dict({'type': 'Wrong'})

        occ = region.get_field(occ_strategy)
        assert isinstance(occ, OccupancyField)
        assert occ.inside_value == 5.0
        assert occ.outside_value == -1.0

        # Scalar evaluation
        assert occ.evaluate(0.0, 0.0) == 5.0
        assert occ.evaluate(2.0, 0.0) == -1.0

        # Vectorized evaluation
        results_occ = occ.evaluate(x_arr, y_arr)
        assert np.allclose(results_occ, [5.0, -1.0])

        # Gradient (always returns zeros)
        assert occ.gradient(0.0, 0.0) == (0.0, 0.0)
        grad_x, grad_y = occ.gradient(x_arr, y_arr)
        assert np.allclose(grad_x, 0.0)
        assert np.allclose(grad_y, 0.0)

        # Level set
        occ_lvl_set = occ.level_set(2.0)
        assert isinstance(occ_lvl_set, ProceduralCurve)
        assert np.isclose(occ_lvl_set.evaluate(0.0, 0.0), 3.0)

        # Serialization round-trip
        occ_dict = occ.to_dict()
        assert occ_dict['type'] == 'OccupancyField'
        reconstructed_occ = OccupancyField.from_dict(occ_dict)
        assert isinstance(reconstructed_occ, OccupancyField)
        assert reconstructed_occ.inside_value == 5.0
        assert reconstructed_occ.outside_value == -1.0
        assert reconstructed_occ.evaluate(0.0, 0.0) == 5.0

        with pytest.raises(ValueError, match="does not represent an OccupancyField"):
            OccupancyField.from_dict({'type': 'Wrong'})

    def test_error_validations(self):
        """Test error conditions, invalid setups, and shape segment count limitations."""
        square = create_square_from_edges((-1, -1), (1, 1))
        region = AreaRegion(square)

        # Strategy mismatch
        with pytest.raises(TypeError, match="strategy must be a FieldStrategy instance"):
            region.get_field("not a strategy")

        # Closed 2-segment curve validation (should fail AreaRegion constructor)
        x, y = sp.symbols('x y')
        line1 = PolynomialCurve(y)
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: -1 <= x <= 1, endpoints=((-1.0, 0.0), (1.0, 0.0)))
        seg2 = TrimmedImplicitCurve(line1, lambda x, y: -1 <= x <= 1, endpoints=((1.0, 0.0), (-1.0, 0.0)))
        two_segment_composite = CompositeCurve([seg1, seg2])
        
        # Mock is_closed to return True so we can bypass the closure check and hit the segment count check
        two_segment_composite.is_closed = lambda *args, **kwargs: True

        with pytest.raises(ValueError, match="outer_boundary must have at least 3 segments to form a closed region"):
            AreaRegion(two_segment_composite)

        # Same for holes
        outer = create_square_from_edges((-3, -3), (3, 3))
        with pytest.raises(ValueError, match="holes\\[0\\] must have at least 3 segments to form a closed region"):
            AreaRegion(outer, [two_segment_composite])


if __name__ == "__main__":
    pytest.main([__file__])
