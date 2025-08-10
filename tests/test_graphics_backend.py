"""
Test suite for Graphics Backend Interface

Tests data extraction, rendering services, and API functionality
for front-end integration.
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from scene_management import SceneManager
from graphics_backend import GraphicsBackendInterface
from visual_tests.utils.test_objects import RegionFactory


class TestGraphicsBackendInterface:
    """Test GraphicsBackendInterface functionality."""
    
    @pytest.fixture
    def scene_manager(self):
        """Create a SceneManager with test objects."""
        sm = SceneManager()
        factory = RegionFactory()
        
        # Add test objects
        circle = factory.create_circle_region((0, 0), 1.0)
        rectangle = factory.create_rectangle_region((1, 1.25), (3, 2.75))  # center (2,2), width 2.0, height 1.5
        triangle = factory.create_triangle_region([(0, 0), (1, 0), (0.5, 1)])
        
        sm.add_object('circle1', circle)
        sm.add_object('rect1', rectangle)
        sm.add_object('tri1', triangle)
        
        # Add styles
        sm.set_style('circle1', {'color': 'blue', 'linewidth': 2})
        sm.set_style('rect1', {'color': 'red', 'fill_alpha': 0.5})
        sm.set_style('tri1', {'color': 'green', 'linewidth': 1})
        
        return sm
    
    @pytest.fixture
    def graphics_backend(self, scene_manager):
        """Create GraphicsBackendInterface with test scene."""
        return GraphicsBackendInterface(scene_manager)
    
    def test_initialization(self, scene_manager):
        """Test GraphicsBackendInterface initialization."""
        backend = GraphicsBackendInterface(scene_manager)
        
        assert backend.scene_manager is scene_manager
        assert backend.default_resolution == (800, 600)
        assert backend.default_bounds == (-5, 5, -5, 5)
        assert backend.default_grid_resolution == 100
    
    def test_get_curve_paths_basic(self, graphics_backend):
        """Test basic curve path extraction."""
        curve_data = graphics_backend.get_curve_paths()
        
        # Should have data for all objects
        assert len(curve_data) == 3
        assert 'circle1' in curve_data
        assert 'rect1' in curve_data
        assert 'tri1' in curve_data
        
        # Check data structure
        for obj_id, data in curve_data.items():
            assert data['type'] == 'curve'
            assert 'points' in data
            assert 'closed' in data
            assert 'style' in data
            assert 'bounds' in data
            
            if data.get('points'):  # If extraction succeeded
                assert len(data['bounds']) == 4  # xmin, xmax, ymin, ymax
                assert isinstance(data['closed'], bool)
                assert 'point_count' in data
    
    def test_get_curve_paths_custom_bounds(self, graphics_backend):
        """Test curve path extraction with custom bounds."""
        bounds = (-2, 2, -2, 2)
        curve_data = graphics_backend.get_curve_paths(bounds=bounds, resolution=50)
        
        # Should still have data for objects within bounds
        assert len(curve_data) >= 1  # At least circle should be included
        
        # Check that bounds are respected
        for obj_id, data in curve_data.items():
            if data.get('points'):
                points = np.array(data['points'])
                if len(points) > 0:
                    # Points should be within or near the specified bounds
                    assert np.min(points[:, 0]) >= bounds[0] - 1  # Allow some tolerance
                    assert np.max(points[:, 0]) <= bounds[1] + 1
    
    def test_get_field_data_basic(self, graphics_backend):
        """Test basic field data extraction."""
        field_data = graphics_backend.get_field_data()
        
        # Should have data for all objects
        assert len(field_data) == 3
        
        # Check data structure
        for obj_id, data in field_data.items():
            assert data['type'] == 'field'
            assert 'bounds' in data
            assert 'resolution' in data
            assert 'style' in data
            assert 'statistics' in data
            
            if data.get('data') is not None:  # If evaluation succeeded
                assert isinstance(data['data'], list)  # JSON-serializable
                stats = data['statistics']
                assert 'min' in stats
                assert 'max' in stats
                assert 'mean' in stats
                assert 'std' in stats
                assert 'finite_count' in stats
                assert 'total_count' in stats
    
    def test_get_field_data_custom_resolution(self, graphics_backend):
        """Test field data extraction with custom resolution."""
        bounds = (-3, 3, -3, 3)
        resolution = (50, 40)
        
        field_data = graphics_backend.get_field_data(bounds=bounds, resolution=resolution)
        
        for obj_id, data in field_data.items():
            assert data['bounds'] == list(bounds)
            assert data['resolution'] == list(resolution)
            
            if data.get('data') is not None:
                # Check that data has correct shape
                data_array = np.array(data['data'])
                assert data_array.shape == (40, 50)  # height, width
    
    def test_get_region_data_basic(self, graphics_backend):
        """Test basic region data extraction."""
        region_data = graphics_backend.get_region_data()
        
        # Should have data for all objects
        assert len(region_data) == 3
        
        # Check data structure
        for obj_id, data in region_data.items():
            assert data['type'] == 'region'
            assert 'bounds' in data
            assert 'resolution' in data
            assert 'style' in data
            assert 'statistics' in data
            
            if data.get('inside_mask') is not None:  # If evaluation succeeded
                assert isinstance(data['inside_mask'], list)  # JSON-serializable
                assert isinstance(data['boundary_mask'], list)
                
                stats = data['statistics']
                assert 'inside_count' in stats
                assert 'boundary_count' in stats
                assert 'total_count' in stats
                assert 'inside_percentage' in stats
                assert 'boundary_percentage' in stats
                
                # Sanity check statistics
                assert stats['inside_count'] >= 0
                assert stats['boundary_count'] >= 0
                assert stats['total_count'] > 0
                assert 0 <= stats['inside_percentage'] <= 100
                assert 0 <= stats['boundary_percentage'] <= 100
    
    def test_get_region_data_circle_containment(self, graphics_backend):
        """Test that circle region data shows reasonable containment."""
        bounds = (-2, 2, -2, 2)
        resolution = (40, 40)
        
        region_data = graphics_backend.get_region_data(bounds=bounds, resolution=resolution)
        
        # Circle should have reasonable inside percentage
        if 'circle1' in region_data and region_data['circle1'].get('inside_mask'):
            stats = region_data['circle1']['statistics']
            # Circle with radius 1 in bounds (-2,2,-2,2) should have ~20% area
            # Allow wide tolerance for different approximation methods
            assert 10 <= stats['inside_percentage'] <= 40
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_render_scene_image_basic(self, mock_close, mock_savefig, graphics_backend):
        """Test basic scene image rendering."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            filename = tmp.name
        
        try:
            result = graphics_backend.render_scene_image(filename)
            
            # Check result structure
            assert result['filename'] == filename
            assert 'bounds' in result
            assert 'resolution' in result
            assert 'rendered_objects' in result
            assert 'object_count' in result
            
            # Should have attempted to render objects
            assert result['object_count'] >= 0
            
            # Should have called matplotlib functions
            mock_savefig.assert_called_once()
            mock_close.assert_called_once()
            
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_get_scene_bounds_basic(self, graphics_backend):
        """Test scene bounds calculation."""
        bounds = graphics_backend.get_scene_bounds()
        
        assert len(bounds) == 4
        xmin, xmax, ymin, ymax = bounds
        
        # Bounds should be reasonable
        assert xmin < xmax
        assert ymin < ymax
        
        # Should include all objects with some padding
        # Circle at (0,0) with radius 1, rectangle at (2,2), triangle around (0,0)-(1,1)
        assert xmin <= -1.5  # Circle extends to -1, with padding
        assert xmax >= 3.5   # Rectangle extends to 3, with padding
        assert ymin <= -1.5  # Circle extends to -1, with padding
        assert ymax >= 3.0   # Rectangle and triangle, with padding
    
    def test_get_scene_bounds_with_padding(self, graphics_backend):
        """Test scene bounds calculation with custom padding."""
        bounds_small = graphics_backend.get_scene_bounds(padding=0.05)
        bounds_large = graphics_backend.get_scene_bounds(padding=0.3)
        
        # Larger padding should give larger bounds
        assert bounds_large[0] < bounds_small[0]  # xmin smaller
        assert bounds_large[1] > bounds_small[1]  # xmax larger
        assert bounds_large[2] < bounds_small[2]  # ymin smaller
        assert bounds_large[3] > bounds_small[3]  # ymax larger
    
    def test_get_object_info_basic(self, graphics_backend):
        """Test object information extraction."""
        info = graphics_backend.get_object_info('circle1')
        
        assert info['id'] == 'circle1'
        assert 'type' in info
        assert 'style' in info
        
        # Should include style information
        assert info['style']['color'] == 'blue'
        assert info['style']['linewidth'] == 2
    
    def test_get_object_info_nonexistent(self, graphics_backend):
        """Test object information for nonexistent object."""
        info = graphics_backend.get_object_info('nonexistent')
        
        assert info['id'] == 'nonexistent'
        assert 'error' in info
    
    def test_get_scene_summary_basic(self, graphics_backend):
        """Test scene summary generation."""
        summary = graphics_backend.get_scene_summary()
        
        # Check basic structure
        assert 'object_count' in summary
        assert 'object_types' in summary
        assert 'group_count' in summary
        assert 'dependency_count' in summary
        assert 'animation_cache_count' in summary
        assert 'total_cache_size_mb' in summary
        assert 'scene_bounds' in summary
        assert 'objects' in summary
        
        # Check values
        assert summary['object_count'] == 3
        assert len(summary['objects']) == 3
        assert 'circle1' in summary['objects']
        assert 'rect1' in summary['objects']
        assert 'tri1' in summary['objects']
        
        # Should have object type counts
        assert summary['object_types']  # Should not be empty
    
    def test_error_handling_broken_object(self, scene_manager):
        """Test error handling with objects that fail evaluation."""
        # Create a mock object that raises exceptions
        broken_obj = Mock()
        broken_obj.evaluate.side_effect = Exception("Evaluation failed")
        broken_obj.contains.side_effect = Exception("Containment failed")
        
        scene_manager.add_object('broken', broken_obj)
        scene_manager.set_style('broken', {'color': 'black'})
        
        backend = GraphicsBackendInterface(scene_manager)
        
        # Should handle errors gracefully
        curve_data = backend.get_curve_paths()
        assert 'broken' in curve_data
        assert 'error' in curve_data['broken']
        
        field_data = backend.get_field_data()
        assert 'broken' in field_data
        assert 'error' in field_data['broken']
        
        region_data = backend.get_region_data()
        assert 'broken' in region_data
        assert 'error' in region_data['broken']
    
    def test_empty_scene(self):
        """Test behavior with empty scene."""
        empty_sm = SceneManager()
        backend = GraphicsBackendInterface(empty_sm)
        
        # Should handle empty scene gracefully
        curve_data = backend.get_curve_paths()
        assert curve_data == {}
        
        field_data = backend.get_field_data()
        assert field_data == {}
        
        region_data = backend.get_region_data()
        assert region_data == {}
        
        summary = backend.get_scene_summary()
        assert summary['object_count'] == 0
        assert summary['objects'] == []
        
        # Bounds should fall back to defaults
        bounds = backend.get_scene_bounds()
        assert bounds == backend.default_bounds


class TestGraphicsBackendIntegration:
    """Integration tests for GraphicsBackendInterface with real geometry objects."""
    
    def test_circle_data_extraction_integration(self):
        """Test complete data extraction pipeline for circle."""
        sm = SceneManager()
        factory = RegionFactory()
        
        # Create circle with known properties
        circle = factory.create_circle_region((1, 1), 2.0)
        sm.add_object('test_circle', circle)
        sm.set_style('test_circle', {
            'color': 'blue', 
            'fill_color': 'lightblue',
            'alpha': 0.7
        })
        
        backend = GraphicsBackendInterface(sm)
        
        # Test all data extraction methods
        bounds = (-2, 4, -2, 4)
        
        curve_data = backend.get_curve_paths(bounds=bounds)
        field_data = backend.get_field_data(bounds=bounds, resolution=(20, 20))
        region_data = backend.get_region_data(bounds=bounds, resolution=(20, 20))
        
        # Verify circle is detected in all methods
        assert 'test_circle' in curve_data
        assert 'test_circle' in field_data
        assert 'test_circle' in region_data
        
        # Verify reasonable data for circle
        if region_data['test_circle'].get('inside_mask'):
            stats = region_data['test_circle']['statistics']
            # Circle with radius 2 in 6x6 area should have reasonable coverage
            assert stats['inside_percentage'] > 10  # At least some inside points
            assert stats['inside_percentage'] < 90  # Not everything inside
    
    def test_performance_with_high_resolution(self):
        """Test performance with high resolution grids."""
        sm = SceneManager()
        factory = RegionFactory()
        
        # Add a few objects
        sm.add_object('c1', factory.create_circle_region((0, 0), 1))
        sm.add_object('r1', factory.create_rectangle_region((1, 1), (3, 3)))  # center (2,2), width 2, height 2
        
        backend = GraphicsBackendInterface(sm)
        
        # Test with moderately high resolution (not too high for CI)
        bounds = (-3, 5, -3, 5)
        resolution = (80, 80)
        
        # Should complete without timeout or memory issues
        field_data = backend.get_field_data(bounds=bounds, resolution=resolution)
        region_data = backend.get_region_data(bounds=bounds, resolution=resolution)
        
        # Verify data structure is correct
        for obj_id in ['c1', 'r1']:
            if obj_id in field_data and field_data[obj_id].get('data'):
                data_array = np.array(field_data[obj_id]['data'])
                assert data_array.shape == (80, 80)
            
            if obj_id in region_data and region_data[obj_id].get('inside_mask'):
                mask_array = np.array(region_data[obj_id]['inside_mask'])
                assert mask_array.shape == (80, 80)
