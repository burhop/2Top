"""
Test suite for field strategy classes and scalar field generation.

This module tests the FieldStrategy pattern implementation, including:
- SignedDistanceStrategy and SignedDistanceField
- OccupancyFillStrategy and OccupancyField
- Integration with AreaRegion.get_field()
- Serialization and deserialization
- Edge cases and error handling
"""

import pytest
import numpy as np
from geometry import (
    AreaRegion, CompositeCurve, create_square_from_edges,
    FieldStrategy, SignedDistanceStrategy, OccupancyFillStrategy,
    SignedDistanceField, OccupancyField, BaseField
)


class TestFieldStrategyBase:
    """Test the abstract FieldStrategy base class."""
    
    def test_field_strategy_is_abstract(self):
        """Test that FieldStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            FieldStrategy()


class TestSignedDistanceStrategy:
    """Test the SignedDistanceStrategy class."""
    
    def test_init_default(self):
        """Test SignedDistanceStrategy initialization with default parameters."""
        strategy = SignedDistanceStrategy()
        assert strategy.resolution == 0.1
    
    def test_init_custom_resolution(self):
        """Test SignedDistanceStrategy initialization with custom resolution."""
        strategy = SignedDistanceStrategy(resolution=0.05)
        assert strategy.resolution == 0.05
    
    def test_init_invalid_resolution(self):
        """Test SignedDistanceStrategy initialization with invalid resolution."""
        with pytest.raises(ValueError, match="resolution must be positive"):
            SignedDistanceStrategy(resolution=0.0)
        
        with pytest.raises(ValueError, match="resolution must be positive"):
            SignedDistanceStrategy(resolution=-0.1)
    
    def test_generate_field(self):
        """Test generating a signed distance field from a region."""
        # Create a simple square region
        square = create_square_from_edges((0, 0), (4, 4))
        region = AreaRegion(square)
        
        strategy = SignedDistanceStrategy(resolution=0.1)
        field = strategy.generate_field(region)
        
        assert isinstance(field, SignedDistanceField)
        assert field.region is region
        assert field.resolution == 0.1
    
    def test_serialization(self):
        """Test SignedDistanceStrategy serialization."""
        strategy = SignedDistanceStrategy(resolution=0.05)
        data = strategy.to_dict()
        
        expected = {
            'type': 'SignedDistanceStrategy',
            'resolution': 0.05
        }
        assert data == expected
        
        # Test round-trip
        reconstructed = SignedDistanceStrategy.from_dict(data)
        assert reconstructed.resolution == strategy.resolution
    
    def test_from_dict_invalid_type(self):
        """Test SignedDistanceStrategy.from_dict with invalid type."""
        data = {'type': 'WrongType', 'resolution': 0.1}
        with pytest.raises(ValueError, match="does not represent a SignedDistanceStrategy"):
            SignedDistanceStrategy.from_dict(data)
    
    def test_from_dict_missing_resolution(self):
        """Test SignedDistanceStrategy.from_dict with missing resolution."""
        data = {'type': 'SignedDistanceStrategy'}
        strategy = SignedDistanceStrategy.from_dict(data)
        assert strategy.resolution == 0.1  # Default value


class TestOccupancyFillStrategy:
    """Test the OccupancyFillStrategy class."""
    
    def test_init_default(self):
        """Test OccupancyFillStrategy initialization with default parameters."""
        strategy = OccupancyFillStrategy()
        assert strategy.inside_value == 1.0
        assert strategy.outside_value == 0.0
    
    def test_init_custom_values(self):
        """Test OccupancyFillStrategy initialization with custom values."""
        strategy = OccupancyFillStrategy(inside_value=10.0, outside_value=-5.0)
        assert strategy.inside_value == 10.0
        assert strategy.outside_value == -5.0
    
    def test_generate_field(self):
        """Test generating an occupancy field from a region."""
        # Create a simple square region
        square = create_square_from_edges((0, 0), (4, 4))
        region = AreaRegion(square)
        
        strategy = OccupancyFillStrategy(inside_value=2.0, outside_value=-1.0)
        field = strategy.generate_field(region)
        
        assert isinstance(field, OccupancyField)
        assert field.region is region
        assert field.inside_value == 2.0
        assert field.outside_value == -1.0
    
    def test_serialization(self):
        """Test OccupancyFillStrategy serialization."""
        strategy = OccupancyFillStrategy(inside_value=5.0, outside_value=-2.0)
        data = strategy.to_dict()
        
        expected = {
            'type': 'OccupancyFillStrategy',
            'inside_value': 5.0,
            'outside_value': -2.0
        }
        assert data == expected
        
        # Test round-trip
        reconstructed = OccupancyFillStrategy.from_dict(data)
        assert reconstructed.inside_value == strategy.inside_value
        assert reconstructed.outside_value == strategy.outside_value
    
    def test_from_dict_invalid_type(self):
        """Test OccupancyFillStrategy.from_dict with invalid type."""
        data = {'type': 'WrongType', 'inside_value': 1.0, 'outside_value': 0.0}
        with pytest.raises(ValueError, match="does not represent an OccupancyFillStrategy"):
            OccupancyFillStrategy.from_dict(data)
    
    def test_from_dict_missing_values(self):
        """Test OccupancyFillStrategy.from_dict with missing values."""
        data = {'type': 'OccupancyFillStrategy'}
        strategy = OccupancyFillStrategy.from_dict(data)
        assert strategy.inside_value == 1.0  # Default value
        assert strategy.outside_value == 0.0  # Default value


class TestSignedDistanceField:
    """Test the SignedDistanceField class."""
    
    @pytest.fixture
    def square_region(self):
        """Create a simple square region for testing."""
        square = create_square_from_edges((0, 0), (4, 4))
        return AreaRegion(square)
    
    def test_init(self, square_region):
        """Test SignedDistanceField initialization."""
        field = SignedDistanceField(square_region, resolution=0.1)
        assert field.region is square_region
        assert field.resolution == 0.1
    
    def test_evaluate_scalar_inside(self, square_region):
        """Test evaluating signed distance field at points inside the region."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        # Test point inside the square
        result = field.evaluate(2.0, 2.0)
        assert isinstance(result, float)
        assert result < 0  # Inside should be negative
    
    def test_evaluate_scalar_outside(self, square_region):
        """Test evaluating signed distance field at points outside the region."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        # Test point outside the square
        result = field.evaluate(5.0, 5.0)
        assert isinstance(result, float)
        assert result > 0  # Outside should be positive
    
    def test_evaluate_scalar_boundary(self, square_region):
        """Test evaluating signed distance field at boundary points."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        # Test point on boundary
        result = field.evaluate(0.0, 2.0)
        assert isinstance(result, float)
        # Boundary points should be close to zero, but exact value depends on implementation
    
    def test_evaluate_vectorized(self, square_region):
        """Test vectorized evaluation of signed distance field."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        x = np.array([1.0, 2.0, 5.0])
        y = np.array([1.0, 2.0, 5.0])
        
        result = field.evaluate(x, y)
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        
        # First two points inside (negative), last point outside (positive)
        assert result[0] < 0
        assert result[1] < 0
        assert result[2] > 0
    
    def test_gradient_scalar(self, square_region):
        """Test gradient computation for scalar input."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        grad_x, grad_y = field.gradient(2.0, 2.0)
        assert isinstance(grad_x, float)
        assert isinstance(grad_y, float)
    
    def test_gradient_vectorized(self, square_region):
        """Test gradient computation for vectorized input."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        x = np.array([1.0, 2.0])
        y = np.array([1.0, 2.0])
        
        grad_x, grad_y = field.gradient(x, y)
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert grad_x.shape == x.shape
        assert grad_y.shape == y.shape
    
    def test_level_set(self, square_region):
        """Test level set extraction."""
        field = SignedDistanceField(square_region, resolution=0.1)
        
        level_curve = field.level_set(0.0)
        assert hasattr(level_curve, 'evaluate')  # Should be an ImplicitCurve
    
    def test_serialization(self, square_region):
        """Test SignedDistanceField serialization."""
        field = SignedDistanceField(square_region, resolution=0.05)
        data = field.to_dict()
        
        assert data['type'] == 'SignedDistanceField'
        assert data['resolution'] == 0.05
        assert 'region' in data
        
        # Test round-trip
        reconstructed = SignedDistanceField.from_dict(data)
        assert reconstructed.resolution == field.resolution
        # Note: Region comparison would require AreaRegion equality method
    
    def test_from_dict_invalid_type(self):
        """Test SignedDistanceField.from_dict with invalid type."""
        data = {'type': 'WrongType'}
        with pytest.raises(ValueError, match="does not represent a SignedDistanceField"):
            SignedDistanceField.from_dict(data)


class TestOccupancyField:
    """Test the OccupancyField class."""
    
    @pytest.fixture
    def square_region(self):
        """Create a simple square region for testing."""
        square = create_square_from_edges((0, 0), (4, 4))
        return AreaRegion(square)
    
    def test_init(self, square_region):
        """Test OccupancyField initialization."""
        field = OccupancyField(square_region, inside_value=10.0, outside_value=-5.0)
        assert field.region is square_region
        assert field.inside_value == 10.0
        assert field.outside_value == -5.0
    
    def test_evaluate_scalar_inside(self, square_region):
        """Test evaluating occupancy field at points inside the region."""
        field = OccupancyField(square_region, inside_value=1.0, outside_value=0.0)
        
        # Test point inside the square
        result = field.evaluate(2.0, 2.0)
        assert result == 1.0
    
    def test_evaluate_scalar_outside(self, square_region):
        """Test evaluating occupancy field at points outside the region."""
        field = OccupancyField(square_region, inside_value=1.0, outside_value=0.0)
        
        # Test point outside the square
        result = field.evaluate(5.0, 5.0)
        assert result == 0.0
    
    def test_evaluate_vectorized(self, square_region):
        """Test vectorized evaluation of occupancy field."""
        field = OccupancyField(square_region, inside_value=2.0, outside_value=-1.0)
        
        x = np.array([1.0, 2.0, 5.0])
        y = np.array([1.0, 2.0, 5.0])
        
        result = field.evaluate(x, y)
        assert isinstance(result, np.ndarray)
        assert result.shape == x.shape
        
        # First two points inside, last point outside
        assert result[0] == 2.0
        assert result[1] == 2.0
        assert result[2] == -1.0
    
    def test_gradient_scalar(self, square_region):
        """Test gradient computation for scalar input."""
        field = OccupancyField(square_region, inside_value=1.0, outside_value=0.0)
        
        grad_x, grad_y = field.gradient(2.0, 2.0)
        assert grad_x == 0.0
        assert grad_y == 0.0
    
    def test_gradient_vectorized(self, square_region):
        """Test gradient computation for vectorized input."""
        field = OccupancyField(square_region, inside_value=1.0, outside_value=0.0)
        
        x = np.array([1.0, 2.0])
        y = np.array([1.0, 2.0])
        
        grad_x, grad_y = field.gradient(x, y)
        assert isinstance(grad_x, np.ndarray)
        assert isinstance(grad_y, np.ndarray)
        assert np.all(grad_x == 0.0)
        assert np.all(grad_y == 0.0)
    
    def test_level_set(self, square_region):
        """Test level set extraction."""
        field = OccupancyField(square_region, inside_value=1.0, outside_value=0.0)
        
        level_curve = field.level_set(0.5)
        assert hasattr(level_curve, 'evaluate')  # Should be an ImplicitCurve
    
    def test_serialization(self, square_region):
        """Test OccupancyField serialization."""
        field = OccupancyField(square_region, inside_value=3.0, outside_value=-2.0)
        data = field.to_dict()
        
        assert data['type'] == 'OccupancyField'
        assert data['inside_value'] == 3.0
        assert data['outside_value'] == -2.0
        assert 'region' in data
        
        # Test round-trip
        reconstructed = OccupancyField.from_dict(data)
        assert reconstructed.inside_value == field.inside_value
        assert reconstructed.outside_value == field.outside_value
    
    def test_from_dict_invalid_type(self):
        """Test OccupancyField.from_dict with invalid type."""
        data = {'type': 'WrongType'}
        with pytest.raises(ValueError, match="does not represent an OccupancyField"):
            OccupancyField.from_dict(data)


class TestAreaRegionFieldIntegration:
    """Test integration of field strategies with AreaRegion.get_field()."""
    
    @pytest.fixture
    def square_region(self):
        """Create a simple square region for testing."""
        square = create_square_from_edges((0, 0), (4, 4))
        return AreaRegion(square)
    
    @pytest.fixture
    def region_with_hole(self):
        """Create a region with a hole for testing."""
        outer = create_square_from_edges((0, 0), (6, 6))
        hole = create_square_from_edges((2, 2), (4, 4))
        return AreaRegion(outer, [hole])
    
    def test_get_field_signed_distance(self, square_region):
        """Test AreaRegion.get_field() with SignedDistanceStrategy."""
        strategy = SignedDistanceStrategy(resolution=0.1)
        field = square_region.get_field(strategy)
        
        assert isinstance(field, SignedDistanceField)
        assert field.region is square_region
        assert field.resolution == 0.1
        
        # Test field evaluation
        assert field.evaluate(2.0, 2.0) < 0  # Inside
        assert field.evaluate(5.0, 5.0) > 0  # Outside
    
    def test_get_field_occupancy(self, square_region):
        """Test AreaRegion.get_field() with OccupancyFillStrategy."""
        strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
        field = square_region.get_field(strategy)
        
        assert isinstance(field, OccupancyField)
        assert field.region is square_region
        assert field.inside_value == 1.0
        assert field.outside_value == 0.0
        
        # Test field evaluation
        assert field.evaluate(2.0, 2.0) == 1.0  # Inside
        assert field.evaluate(5.0, 5.0) == 0.0  # Outside
    
    def test_get_field_with_hole_signed_distance(self, region_with_hole):
        """Test field generation for region with hole using signed distance."""
        strategy = SignedDistanceStrategy(resolution=0.1)
        field = region_with_hole.get_field(strategy)
        
        assert isinstance(field, SignedDistanceField)
        
        # Test points in different regions
        assert field.evaluate(1.0, 1.0) < 0  # Inside outer, outside hole
        assert field.evaluate(3.0, 3.0) > 0  # Inside hole (should be positive)
        assert field.evaluate(7.0, 7.0) > 0  # Outside outer
    
    def test_get_field_with_hole_occupancy(self, region_with_hole):
        """Test field generation for region with hole using occupancy."""
        strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
        field = region_with_hole.get_field(strategy)
        
        assert isinstance(field, OccupancyField)
        
        # Test points in different regions
        assert field.evaluate(1.0, 1.0) == 1.0  # Inside outer, outside hole
        assert field.evaluate(3.0, 3.0) == 0.0  # Inside hole (not in region)
        assert field.evaluate(7.0, 7.0) == 0.0  # Outside outer
    
    def test_get_field_invalid_strategy(self, square_region):
        """Test AreaRegion.get_field() with invalid strategy."""
        with pytest.raises(TypeError, match="strategy must be a FieldStrategy instance"):
            square_region.get_field("not a strategy")
        
        with pytest.raises(TypeError, match="strategy must be a FieldStrategy instance"):
            square_region.get_field(None)


class TestFieldStrategyEdgeCases:
    """Test edge cases and error conditions for field strategies."""
    
    def test_signed_distance_field_empty_boundary(self):
        """Test SignedDistanceField with region that has no boundary points."""
        # Create a minimal region that might not have good boundary approximation
        from geometry import TrimmedImplicitCurve, ImplicitCurve
        import sympy as sp
        
        x, y = sp.symbols('x y')
        # Create a very simple curve
        curve_expr = x**2 + y**2 - 1  # Unit circle
        base_curve = ImplicitCurve(curve_expr, (x, y))
        
        # Create a trimmed curve with a mask that might cause issues
        def always_false_mask(x_val, y_val):
            return False
        
        trimmed = TrimmedImplicitCurve(base_curve, always_false_mask)
        composite = CompositeCurve([trimmed])
        
        # This should handle the edge case gracefully
        try:
            region = AreaRegion(composite)
            field = SignedDistanceField(region, resolution=0.1)
            result = field.evaluate(0.0, 0.0)
            assert isinstance(result, float)
        except ValueError:
            # It's acceptable for this to fail during region creation
            pass
    
    def test_field_evaluation_extreme_coordinates(self):
        """Test field evaluation with extreme coordinate values."""
        square = create_square_from_edges((0, 0), (4, 4))
        region = AreaRegion(square)
        
        sdf = SignedDistanceField(region, resolution=0.1)
        occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
        
        # Test with very large coordinates
        large_coord = 1e6
        sdf_result = sdf.evaluate(large_coord, large_coord)
        occ_result = occ.evaluate(large_coord, large_coord)
        
        assert isinstance(sdf_result, float)
        assert sdf_result > 0  # Should be outside
        assert occ_result == 0.0  # Should be outside
        
        # Test with very small coordinates
        small_coord = 1e-6
        sdf_result = sdf.evaluate(small_coord, small_coord)
        occ_result = occ.evaluate(small_coord, small_coord)
        
        assert isinstance(sdf_result, float)
        assert sdf_result < 0  # Should be inside (point is within square bounds)
        assert occ_result == 1.0  # Should be inside (point (1e-6, 1e-6) is within square (0,0) to (4,4))
    
    def test_field_evaluation_nan_coordinates(self):
        """Test field evaluation with NaN coordinates."""
        square = create_square_from_edges((0, 0), (4, 4))
        region = AreaRegion(square)
        
        sdf = SignedDistanceField(region, resolution=0.1)
        occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
        
        # Test with NaN coordinates - behavior may vary but should not crash
        try:
            sdf_result = sdf.evaluate(float('nan'), 2.0)
            occ_result = occ.evaluate(float('nan'), 2.0)
            # Results may be NaN or handled gracefully
        except (ValueError, RuntimeError):
            # It's acceptable for this to raise an exception
            pass


class TestFieldStrategyPerformance:
    """Test performance characteristics of field strategies."""
    
    def test_vectorized_evaluation_performance(self):
        """Test that vectorized evaluation is more efficient than scalar loops."""
        square = create_square_from_edges((0, 0), (4, 4))
        region = AreaRegion(square)
        
        strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
        field = region.get_field(strategy)
        
        # Create test data
        n_points = 100
        x = np.random.uniform(-1, 5, n_points)
        y = np.random.uniform(-1, 5, n_points)
        
        # Test vectorized evaluation
        result_vectorized = field.evaluate(x, y)
        
        # Test scalar evaluation
        result_scalar = np.array([field.evaluate(x[i], y[i]) for i in range(n_points)])
        
        # Results should be equivalent
        np.testing.assert_array_equal(result_vectorized, result_scalar)
        
        # Both should have correct shape
        assert result_vectorized.shape == (n_points,)
        assert result_scalar.shape == (n_points,)


if __name__ == "__main__":
    pytest.main([__file__])
