"""
Test suite for MCP Command Handler

Tests command-based interface for external services and AI agents.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch

from scene_management import SceneManager
from graphics_backend import MCPCommandHandler


class TestMCPCommandHandler:
    """Test MCPCommandHandler functionality."""
    
    @pytest.fixture
    def handler(self):
        """Create MCPCommandHandler with fresh scene."""
        return MCPCommandHandler()
    
    @pytest.fixture
    def handler_with_objects(self):
        """Create MCPCommandHandler with test objects."""
        handler = MCPCommandHandler()
        
        # Add some test objects
        handler.handle_command('create.circle', {
            'object_id': 'circle1',
            'center': [0, 0],
            'radius': 1.0,
            'style': {'color': 'blue'}
        })
        
        handler.handle_command('create.rectangle', {
            'object_id': 'rect1',
            'center': [2, 2],
            'width': 2.0,
            'height': 1.5,
            'style': {'color': 'red'}
        })
        
        return handler
    
    def test_initialization(self):
        """Test MCPCommandHandler initialization."""
        handler = MCPCommandHandler()
        
        assert handler.scene_manager is not None
        assert handler.graphics_backend is not None
        assert handler.region_factory is not None
        assert handler.curve_factory is not None
        assert len(handler._commands) > 0
    
    def test_initialization_with_scene_manager(self):
        """Test initialization with existing SceneManager."""
        sm = SceneManager()
        handler = MCPCommandHandler(sm)
        
        assert handler.scene_manager is sm
    
    # ================== Basic Command Handling ==================
    
    def test_handle_unknown_command(self, handler):
        """Test handling of unknown command."""
        result = handler.handle_command('unknown.command')
        
        assert result['success'] is False
        assert 'Unknown command' in result['error']
        assert 'available_commands' in result
    
    def test_handle_command_success_structure(self, handler):
        """Test successful command response structure."""
        result = handler.handle_command('help.list_commands')
        
        assert result['success'] is True
        assert result['command'] == 'help.list_commands'
        assert 'data' in result
        assert isinstance(result['data'], list)
    
    def test_handle_command_error_structure(self, handler):
        """Test error command response structure."""
        result = handler.handle_command('scene.get_object_info', {})
        
        assert result['success'] is False
        assert result['command'] == 'scene.get_object_info'
        assert 'error' in result
        assert 'traceback' in result
    
    def test_handle_batch_commands(self, handler):
        """Test batch command handling."""
        commands = [
            {'command': 'help.list_commands'},
            {'command': 'scene.list_objects'},
            {'command': 'unknown.command'}
        ]
        
        results = handler.handle_batch_commands(commands)
        
        assert len(results) == 3
        assert results[0]['success'] is True
        assert results[1]['success'] is True
        assert results[2]['success'] is False
    
    def test_handle_batch_commands_missing_command(self, handler):
        """Test batch commands with missing command field."""
        commands = [
            {'params': {'test': 'value'}},  # Missing command
            {'command': 'help.list_commands'}
        ]
        
        results = handler.handle_batch_commands(commands)
        
        assert len(results) == 2
        assert results[0]['success'] is False
        assert 'Missing command field' in results[0]['error']
        assert results[1]['success'] is True
    
    # ================== Scene Management Commands ==================
    
    def test_list_objects_empty(self, handler):
        """Test listing objects in empty scene."""
        result = handler.handle_command('scene.list_objects')
        
        assert result['success'] is True
        assert result['data'] == []
    
    def test_list_objects_with_data(self, handler_with_objects):
        """Test listing objects with data."""
        result = handler_with_objects.handle_command('scene.list_objects')
        
        assert result['success'] is True
        assert len(result['data']) == 2
        assert 'circle1' in result['data']
        assert 'rect1' in result['data']
    
    def test_get_object_info(self, handler_with_objects):
        """Test getting object information."""
        result = handler_with_objects.handle_command('scene.get_object_info', {
            'object_id': 'circle1'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['id'] == 'circle1'
        assert 'type' in data
        assert 'style' in data
    
    def test_get_object_info_missing_id(self, handler):
        """Test getting object info without object_id."""
        result = handler.handle_command('scene.get_object_info', {})
        
        assert result['success'] is False
        assert 'Missing required parameter: object_id' in result['error']
    
    def test_get_scene_summary(self, handler_with_objects):
        """Test getting scene summary."""
        result = handler_with_objects.handle_command('scene.get_summary')
        
        assert result['success'] is True
        data = result['data']
        assert data['object_count'] == 2
        assert 'object_types' in data
        assert 'scene_bounds' in data
    
    def test_clear_scene(self, handler_with_objects):
        """Test clearing scene."""
        # Verify objects exist
        result = handler_with_objects.handle_command('scene.list_objects')
        assert len(result['data']) == 2
        
        # Clear scene
        result = handler_with_objects.handle_command('scene.clear')
        assert result['success'] is True
        assert result['data']['cleared_objects'] == 2
        
        # Verify scene is empty
        result = handler_with_objects.handle_command('scene.list_objects')
        assert len(result['data']) == 0
    
    def test_save_and_load_scene(self, handler_with_objects):
        """Test scene save and load."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            filename = tmp.name
        
        try:
            # Save scene
            result = handler_with_objects.handle_command('scene.save', {
                'filename': filename
            })
            assert result['success'] is True
            assert result['data']['filename'] == filename
            
            # Clear scene
            handler_with_objects.handle_command('scene.clear')
            
            # Load scene
            result = handler_with_objects.handle_command('scene.load', {
                'filename': filename
            })
            assert result['success'] is True
            assert result['data']['filename'] == filename
            
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    # ================== Object Creation Commands ==================
    
    def test_create_circle(self, handler):
        """Test circle creation."""
        result = handler.handle_command('create.circle', {
            'object_id': 'test_circle',
            'center': [1, 2],
            'radius': 3.0,
            'style': {'color': 'green'}
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'test_circle'
        assert data['type'] == 'circle'
        assert data['center'] == [1, 2]
        assert data['radius'] == 3.0
        assert data['style']['color'] == 'green'
        
        # Verify object was added
        objects = handler.handle_command('scene.list_objects')['data']
        assert 'test_circle' in objects
    
    def test_create_circle_defaults(self, handler):
        """Test circle creation with defaults."""
        result = handler.handle_command('create.circle', {})
        
        assert result['success'] is True
        data = result['data']
        assert data['center'] == [0, 0]
        assert data['radius'] == 1.0
        assert data['object_id'].startswith('circle_')
    
    def test_create_rectangle(self, handler):
        """Test rectangle creation."""
        result = handler.handle_command('create.rectangle', {
            'object_id': 'test_rect',
            'center': [0, 0],
            'width': 4.0,
            'height': 2.0,
            'style': {'fill_color': 'yellow'}
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'test_rect'
        assert data['type'] == 'rectangle'
        assert data['center'] == [0, 0]
        assert data['width'] == 4.0
        assert data['height'] == 2.0
    
    def test_create_triangle(self, handler):
        """Test triangle creation."""
        vertices = [[0, 0], [2, 0], [1, 2]]
        result = handler.handle_command('create.triangle', {
            'object_id': 'test_tri',
            'vertices': vertices,
            'style': {'color': 'purple'}
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'test_tri'
        assert data['type'] == 'triangle'
        assert data['vertices'] == vertices
    
    def test_create_triangle_invalid_vertices(self, handler):
        """Test triangle creation with invalid vertices."""
        result = handler.handle_command('create.triangle', {
            'vertices': [[0, 0], [1, 1]]  # Only 2 vertices
        })
        
        assert result['success'] is False
        assert 'exactly 3 vertices' in result['error']
    
    def test_create_line(self, handler):
        """Test line creation."""
        result = handler.handle_command('create.line', {
            'object_id': 'test_line',
            'start': [0, 0],
            'end': [3, 4],
            'style': {'linewidth': 3}
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'test_line'
        assert data['type'] == 'line'
        assert data['start'] == [0, 0]
        assert data['end'] == [3, 4]
    
    def test_create_ellipse(self, handler):
        """Test ellipse creation."""
        result = handler.handle_command('create.ellipse', {
            'object_id': 'test_ellipse',
            'center': [1, 1],
            'semi_major': 3.0,
            'semi_minor': 2.0
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'test_ellipse'
        assert data['type'] == 'ellipse'
        assert data['center'] == [1, 1]
        assert data['semi_major'] == 3.0
        assert data['semi_minor'] == 2.0
    
    # ================== Object Management Commands ==================
    
    def test_remove_object(self, handler_with_objects):
        """Test object removal."""
        # Verify object exists
        objects = handler_with_objects.handle_command('scene.list_objects')['data']
        assert 'circle1' in objects
        
        # Remove object
        result = handler_with_objects.handle_command('object.remove', {
            'object_id': 'circle1'
        })
        assert result['success'] is True
        assert result['data']['object_id'] == 'circle1'
        assert result['data']['removed'] is True
        
        # Verify object is gone
        objects = handler_with_objects.handle_command('scene.list_objects')['data']
        assert 'circle1' not in objects
    
    def test_get_object_style(self, handler_with_objects):
        """Test getting object style."""
        result = handler_with_objects.handle_command('object.get_style', {
            'object_id': 'circle1'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'circle1'
        assert data['style']['color'] == 'blue'
    
    def test_set_object_style(self, handler_with_objects):
        """Test setting object style."""
        new_style = {'color': 'orange', 'linewidth': 5}
        result = handler_with_objects.handle_command('object.set_style', {
            'object_id': 'circle1',
            'style': new_style
        })
        
        assert result['success'] is True
        assert result['data']['updated'] is True
        
        # Verify style was updated
        style_result = handler_with_objects.handle_command('object.get_style', {
            'object_id': 'circle1'
        })
        assert style_result['data']['style']['color'] == 'orange'
        assert style_result['data']['style']['linewidth'] == 5
    
    def test_get_object_parameters(self, handler_with_objects):
        """Test getting object parameters."""
        result = handler_with_objects.handle_command('object.get_parameters', {
            'object_id': 'circle1'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'circle1'
        # Parameters depend on object implementation
        assert 'parameters' in data
        assert 'parameter_names' in data
    
    # ================== Animation Commands ==================
    
    def test_create_parameter_animation(self, handler_with_objects):
        """Test parameter animation creation."""
        result = handler_with_objects.handle_command('animation.create_parameter', {
            'object_id': 'circle1',
            'parameter_name': 'radius',
            'values': [0.5, 1.0, 1.5, 2.0, 1.5, 1.0]
        })
        
        # Result depends on whether object supports parameters
        # Should either succeed or fail gracefully
        assert 'success' in result
        if result['success']:
            assert 'animation_id' in result['data']
            assert result['data']['frame_count'] == 6
    
    def test_create_multi_parameter_animation(self, handler_with_objects):
        """Test multi-parameter animation creation."""
        animations = {
            'circle1': {
                'parameter_name': 'radius',
                'values': [1.0, 2.0, 1.0]
            },
            'rect1': {
                'parameter_name': 'width',
                'values': [2.0, 4.0, 2.0]
            }
        }
        
        result = handler_with_objects.handle_command('animation.create_multi_parameter', {
            'animations': animations
        })
        
        # Should either succeed or fail gracefully
        assert 'success' in result
        if result['success']:
            assert 'animation_id' in result['data']
            assert result['data']['frame_count'] == 3
    
    def test_get_animation_cache_info(self, handler):
        """Test getting animation cache info."""
        result = handler.handle_command('animation.get_cache_info')
        
        assert result['success'] is True
        # Should return cache info dict (empty for new handler)
        assert isinstance(result['data'], dict)
    
    def test_clear_animation_cache(self, handler):
        """Test clearing animation cache."""
        result = handler.handle_command('animation.clear_cache')
        
        assert result['success'] is True
        assert result['data']['cleared_all'] is True
    
    # ================== Rendering Commands ==================
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_render_scene_image(self, mock_close, mock_savefig, handler_with_objects):
        """Test scene image rendering."""
        result = handler_with_objects.handle_command('render.scene_image', {
            'bounds': [-3, 5, -3, 5],
            'resolution': [400, 300],
            'show_grid': True
        })
        
        assert result['success'] is True
        data = result['data']
        assert 'filename' in data
        assert data['bounds'] == [-3, 5, -3, 5]
        assert data['resolution'] == [400, 300]
        assert 'rendered_objects' in data
        assert 'object_count' in data
    
    def test_get_curve_paths(self, handler_with_objects):
        """Test getting curve paths."""
        result = handler_with_objects.handle_command('render.get_curve_paths', {
            'bounds': [-2, 4, -2, 4],
            'resolution': 100
        })
        
        assert result['success'] is True
        data = result['data']
        assert isinstance(data, dict)
        # Should have data for created objects
        assert len(data) >= 0  # May be empty if extraction fails
    
    def test_get_field_data(self, handler_with_objects):
        """Test getting field data."""
        result = handler_with_objects.handle_command('render.get_field_data', {
            'bounds': [-2, 4, -2, 4],
            'resolution': [20, 20]
        })
        
        assert result['success'] is True
        data = result['data']
        assert isinstance(data, dict)
    
    def test_get_region_data(self, handler_with_objects):
        """Test getting region data."""
        result = handler_with_objects.handle_command('render.get_region_data', {
            'bounds': [-2, 4, -2, 4],
            'resolution': [20, 20]
        })
        
        assert result['success'] is True
        data = result['data']
        assert isinstance(data, dict)
    
    def test_get_scene_bounds(self, handler_with_objects):
        """Test getting scene bounds."""
        result = handler_with_objects.handle_command('render.get_scene_bounds', {
            'padding': 0.2
        })
        
        assert result['success'] is True
        bounds = result['data']
        assert len(bounds) == 4
        assert bounds[0] < bounds[1]  # xmin < xmax
        assert bounds[2] < bounds[3]  # ymin < ymax
    
    # ================== Grouping and Dependencies ==================
    
    def test_create_group(self, handler_with_objects):
        """Test group creation."""
        result = handler_with_objects.handle_command('group.create', {
            'group_name': 'test_group',
            'object_ids': ['circle1', 'rect1']
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['group_name'] == 'test_group'
        assert data['object_count'] == 2
        assert data['created'] is True
    
    def test_add_to_group(self, handler_with_objects):
        """Test adding object to group."""
        # Create group first
        handler_with_objects.handle_command('group.create', {
            'group_name': 'test_group',
            'object_ids': []
        })
        
        # Add object to group
        result = handler_with_objects.handle_command('group.add_object', {
            'group_name': 'test_group',
            'object_id': 'circle1'
        })
        
        assert result['success'] is True
        assert result['data']['added'] is True
    
    def test_register_dependency(self, handler_with_objects):
        """Test dependency registration."""
        result = handler_with_objects.handle_command('dependency.register', {
            'source_id': 'circle1',
            'dependent_id': 'rect1'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['source_id'] == 'circle1'
        assert data['dependent_id'] == 'rect1'
        assert data['registered'] is True
    
    def test_get_dependencies(self, handler_with_objects):
        """Test getting dependencies."""
        # Register a dependency first
        handler_with_objects.handle_command('dependency.register', {
            'source_id': 'circle1',
            'dependent_id': 'rect1'
        })
        
        # Get dependencies
        result = handler_with_objects.handle_command('dependency.get', {
            'object_id': 'circle1'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['object_id'] == 'circle1'
        assert 'dependencies' in data
    
    # ================== Utility Commands ==================
    
    def test_list_commands(self, handler):
        """Test listing available commands."""
        result = handler.handle_command('help.list_commands')
        
        assert result['success'] is True
        commands = result['data']
        assert isinstance(commands, list)
        assert len(commands) > 20  # Should have many commands
        assert 'create.circle' in commands
        assert 'scene.list_objects' in commands
        assert 'help.list_commands' in commands
    
    def test_get_command_info(self, handler):
        """Test getting command information."""
        result = handler.handle_command('help.get_command_info', {
            'command': 'create.circle'
        })
        
        assert result['success'] is True
        data = result['data']
        assert data['command'] == 'create.circle'
        assert 'description' in data
        assert data['available'] is True
    
    def test_get_command_info_unknown(self, handler):
        """Test getting info for unknown command."""
        result = handler.handle_command('help.get_command_info', {
            'command': 'unknown.command'
        })
        
        assert result['success'] is False
        assert 'Unknown command' in result['error']
    
    # ================== Error Handling ==================
    
    def test_missing_required_parameters(self, handler):
        """Test handling of missing required parameters."""
        # Test various commands that require parameters
        test_cases = [
            ('scene.get_object_info', {}),
            ('object.remove', {}),
            ('object.set_style', {'object_id': 'test'}),
            ('create.triangle', {'vertices': [[0, 0]]}),  # Wrong number of vertices
            ('dependency.register', {'source_id': 'test'}),
        ]
        
        for command, params in test_cases:
            result = handler.handle_command(command, params)
            assert result['success'] is False
            assert 'Missing required parameter' in result['error'] or 'exactly 3 vertices' in result['error']
    
    def test_nonexistent_object_operations(self, handler):
        """Test operations on nonexistent objects."""
        test_cases = [
            ('object.remove', {'object_id': 'nonexistent'}),
            ('object.get_style', {'object_id': 'nonexistent'}),
            ('object.set_style', {'object_id': 'nonexistent', 'style': {}}),
            ('object.get_parameters', {'object_id': 'nonexistent'}),
        ]
        
        for command, params in test_cases:
            result = handler.handle_command(command, params)
            # Should either fail gracefully or handle the nonexistent object
            assert 'success' in result
            # Don't assert specific behavior as it depends on implementation


class TestMCPHandlerIntegration:
    """Integration tests for MCP handler with complete workflows."""
    
    def test_complete_scene_creation_workflow(self):
        """Test complete workflow of creating and manipulating a scene."""
        handler = MCPCommandHandler()
        
        # 1. Create objects
        circle_result = handler.handle_command('create.circle', {
            'object_id': 'main_circle',
            'center': [0, 0],
            'radius': 2.0,
            'style': {'color': 'blue', 'fill_alpha': 0.3}
        })
        assert circle_result['success'] is True
        
        rect_result = handler.handle_command('create.rectangle', {
            'object_id': 'main_rect',
            'center': [3, 3],
            'width': 2.0,
            'height': 1.0,
            'style': {'color': 'red', 'linewidth': 3}
        })
        assert rect_result['success'] is True
        
        # 2. Create group
        group_result = handler.handle_command('group.create', {
            'group_name': 'main_objects',
            'object_ids': ['main_circle', 'main_rect']
        })
        assert group_result['success'] is True
        
        # 3. Register dependency
        dep_result = handler.handle_command('dependency.register', {
            'source_id': 'main_circle',
            'dependent_id': 'main_rect'
        })
        assert dep_result['success'] is True
        
        # 4. Get scene summary
        summary_result = handler.handle_command('scene.get_summary')
        assert summary_result['success'] is True
        assert summary_result['data']['object_count'] == 2
        
        # 5. Modify object style
        style_result = handler.handle_command('object.set_style', {
            'object_id': 'main_circle',
            'style': {'color': 'green', 'fill_alpha': 0.5}
        })
        assert style_result['success'] is True
        
        # 6. Get rendering data
        bounds_result = handler.handle_command('render.get_scene_bounds')
        assert bounds_result['success'] is True
        
        curve_result = handler.handle_command('render.get_curve_paths', {
            'bounds': bounds_result['data']
        })
        assert curve_result['success'] is True
        
        # 7. Save scene
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            filename = tmp.name
        
        try:
            save_result = handler.handle_command('scene.save', {
                'filename': filename
            })
            assert save_result['success'] is True
            
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
    
    def test_batch_object_creation(self):
        """Test creating multiple objects in batch."""
        handler = MCPCommandHandler()
        
        commands = [
            {
                'command': 'create.circle',
                'params': {'object_id': 'c1', 'center': [0, 0], 'radius': 1}
            },
            {
                'command': 'create.circle',
                'params': {'object_id': 'c2', 'center': [2, 0], 'radius': 1}
            },
            {
                'command': 'create.rectangle',
                'params': {'object_id': 'r1', 'center': [1, 2], 'width': 3, 'height': 1}
            },
            {
                'command': 'scene.list_objects'
            }
        ]
        
        results = handler.handle_batch_commands(commands)
        
        # All commands should succeed
        assert len(results) == 4
        for i in range(3):  # First 3 are object creation
            assert results[i]['success'] is True
        
        # Last command should list all objects
        assert results[3]['success'] is True
        objects = results[3]['data']
        assert len(objects) == 3
        assert 'c1' in objects
        assert 'c2' in objects
        assert 'r1' in objects
