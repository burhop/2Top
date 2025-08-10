"""
Model Context Protocol (MCP) Command Handler for 2Top Geometry Library

Provides a command-based interface for external services and AI agents
to interact with the 2Top geometry system through structured commands.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import tempfile
import traceback

from scene_management import SceneManager
from .graphics_interface import GraphicsBackendInterface
from visual_tests.utils.test_objects import RegionFactory, CurveFactory
from geometry import AreaRegion, CompositeCurve


class MCPCommandHandler:
    """
    Handles MCP (Model Context Protocol) commands for the 2Top geometry system.
    
    Provides a structured command interface that external services can use
    to create, modify, and query geometric objects and scenes.
    """
    
    def __init__(self, scene_manager: Optional[SceneManager] = None):
        """
        Initialize MCP command handler.
        
        Args:
            scene_manager: SceneManager instance, creates new one if None
        """
        self.scene_manager = scene_manager or SceneManager()
        self.graphics_backend = GraphicsBackendInterface(self.scene_manager)
        self.region_factory = RegionFactory()
        self.curve_factory = CurveFactory()
        
        # Command registry
        self._commands = {
            # Scene Management
            'scene.list_objects': self._cmd_list_objects,
            'scene.get_object_info': self._cmd_get_object_info,
            'scene.get_summary': self._cmd_get_scene_summary,
            'scene.clear': self._cmd_clear_scene,
            'scene.save': self._cmd_save_scene,
            'scene.load': self._cmd_load_scene,
            
            # Object Creation
            'create.circle': self._cmd_create_circle,
            'create.rectangle': self._cmd_create_rectangle,
            'create.triangle': self._cmd_create_triangle,
            'create.line': self._cmd_create_line,
            'create.ellipse': self._cmd_create_ellipse,
            
            # Object Management
            'object.remove': self._cmd_remove_object,
            'object.get_style': self._cmd_get_object_style,
            'object.set_style': self._cmd_set_object_style,
            'object.get_parameters': self._cmd_get_object_parameters,
            'object.set_parameter': self._cmd_set_object_parameter,
            
            # Grouping and Dependencies
            'group.create': self._cmd_create_group,
            'group.add_object': self._cmd_add_to_group,
            'group.remove_object': self._cmd_remove_from_group,
            'dependency.register': self._cmd_register_dependency,
            'dependency.get': self._cmd_get_dependencies,
            
            # Animation
            'animation.create_parameter': self._cmd_create_parameter_animation,
            'animation.create_multi_parameter': self._cmd_create_multi_parameter_animation,
            'animation.replay': self._cmd_replay_animation,
            'animation.clear_cache': self._cmd_clear_animation_cache,
            'animation.get_cache_info': self._cmd_get_animation_cache_info,
            
            # Rendering and Data Extraction
            'render.scene_image': self._cmd_render_scene_image,
            'render.get_curve_paths': self._cmd_get_curve_paths,
            'render.get_field_data': self._cmd_get_field_data,
            'render.get_region_data': self._cmd_get_region_data,
            'render.get_scene_bounds': self._cmd_get_scene_bounds,
            
            # Utility
            'help.list_commands': self._cmd_list_commands,
            'help.get_command_info': self._cmd_get_command_info,
        }
    
    def handle_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an MCP command and return structured response.
        
        Args:
            command: Command name (e.g., 'create.circle')
            params: Command parameters
            
        Returns:
            Dict with 'success', 'data', and optionally 'error' keys
        """
        if params is None:
            params = {}
        
        try:
            if command not in self._commands:
                return {
                    'success': False,
                    'error': f"Unknown command: {command}",
                    'available_commands': list(self._commands.keys())
                }
            
            # Execute command
            result = self._commands[command](params)
            
            return {
                'success': True,
                'command': command,
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'command': command,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def handle_batch_commands(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle multiple commands in batch.
        
        Args:
            commands: List of command dicts with 'command' and 'params' keys
            
        Returns:
            List of response dicts
        """
        results = []
        
        for cmd_data in commands:
            command = cmd_data.get('command')
            params = cmd_data.get('params', {})
            
            if not command:
                results.append({
                    'success': False,
                    'error': 'Missing command field'
                })
                continue
            
            result = self.handle_command(command, params)
            results.append(result)
        
        return results
    
    # ================== Scene Management Commands ==================
    
    def _cmd_list_objects(self, params: Dict[str, Any]) -> List[str]:
        """List all objects in the scene."""
        return self.scene_manager.list_objects()
    
    def _cmd_get_object_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about an object."""
        obj_id = params.get('object_id')
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        
        return self.graphics_backend.get_object_info(obj_id)
    
    def _cmd_get_scene_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive scene summary."""
        return self.graphics_backend.get_scene_summary()
    
    def _cmd_clear_scene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear all objects from the scene."""
        object_count = len(self.scene_manager.list_objects())
        
        for obj_id in list(self.scene_manager.list_objects()):
            self.scene_manager.remove_object(obj_id)
        
        return {'cleared_objects': object_count}
    
    def _cmd_save_scene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save scene to file."""
        filename = params.get('filename')
        if not filename:
            raise ValueError("Missing required parameter: filename")
        
        self.scene_manager.save_scene(filename)
        return {'filename': filename, 'saved': True}
    
    def _cmd_load_scene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load scene from file."""
        filename = params.get('filename')
        if not filename:
            raise ValueError("Missing required parameter: filename")
        
        self.scene_manager.load_scene(filename)
        return {
            'filename': filename,
            'loaded': True,
            'object_count': len(self.scene_manager.list_objects())
        }
    
    # ================== Object Creation Commands ==================
    
    def _cmd_create_circle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a circle object."""
        center = params.get('center', [0, 0])
        radius = params.get('radius', 1.0)
        obj_id = params.get('object_id', f'circle_{len(self.scene_manager.list_objects())}')
        
        circle = self.region_factory.create_circle_region(tuple(center), radius)
        self.scene_manager.add_object(obj_id, circle)
        
        # Apply style if provided
        style = params.get('style', {})
        if style:
            self.scene_manager.set_style(obj_id, style)
        
        return {
            'object_id': obj_id,
            'type': 'circle',
            'center': center,
            'radius': radius,
            'style': style
        }
    
    def _cmd_create_rectangle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rectangle object."""
        center = params.get('center', [0, 0])
        width = params.get('width', 2.0)
        height = params.get('height', 2.0)
        obj_id = params.get('object_id', f'rectangle_{len(self.scene_manager.list_objects())}')
        
        # Convert center/width/height to corner points for RegionFactory
        cx, cy = center
        half_width = width / 2.0
        half_height = height / 2.0
        corner1 = (cx - half_width, cy - half_height)
        corner2 = (cx + half_width, cy + half_height)
        
        rectangle = self.region_factory.create_rectangle_region(corner1, corner2)
        self.scene_manager.add_object(obj_id, rectangle)
        
        # Apply style if provided
        style = params.get('style', {})
        if style:
            self.scene_manager.set_style(obj_id, style)
        
        return {
            'object_id': obj_id,
            'type': 'rectangle',
            'center': center,
            'width': width,
            'height': height,
            'style': style
        }
    
    def _cmd_create_triangle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a triangle object."""
        vertices = params.get('vertices', [[0, 0], [1, 0], [0.5, 1]])
        obj_id = params.get('object_id', f'triangle_{len(self.scene_manager.list_objects())}')
        
        if len(vertices) != 3:
            raise ValueError("Triangle requires exactly 3 vertices")
        
        triangle = self.region_factory.create_triangle_region(vertices)
        self.scene_manager.add_object(obj_id, triangle)
        
        # Apply style if provided
        style = params.get('style', {})
        if style:
            self.scene_manager.set_style(obj_id, style)
        
        return {
            'object_id': obj_id,
            'type': 'triangle',
            'vertices': vertices,
            'style': style
        }
    
    def _cmd_create_line(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a line object."""
        # Support both parameter naming conventions
        if 'start' in params and 'end' in params:
            # Use start/end format
            point1 = params.get('start', [0, 0])
            point2 = params.get('end', [1, 1])
            use_start_end = True
        else:
            # Use point1/point2 format
            point1 = params.get('point1', [0, 0])
            point2 = params.get('point2', [1, 1])
            use_start_end = False
            
        obj_id = params.get('object_id', f'line_{len(self.scene_manager.list_objects())}')
        
        # Use correct method name from CurveFactory
        line = self.curve_factory.create_line(tuple(point1), tuple(point2))
        self.scene_manager.add_object(obj_id, line)
        
        # Apply style if provided
        style = params.get('style', {})
        if style:
            self.scene_manager.set_style(obj_id, style)
        
        # Return in the same format as input
        result = {
            'object_id': obj_id,
            'type': 'line',
            'style': style
        }
        
        if use_start_end:
            result['start'] = point1
            result['end'] = point2
        else:
            result['point1'] = point1
            result['point2'] = point2
            
        return result
    
    def _cmd_create_ellipse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an ellipse object."""
        center = params.get('center', [0, 0])
        a = params.get('semi_major', 2.0)
        b = params.get('semi_minor', 1.0)
        obj_id = params.get('object_id', f'ellipse_{len(self.scene_manager.list_objects())}')
        
        # Create ellipse using CurveFactory and try direct AreaRegion creation like circle
        ellipse_curve = self.curve_factory.create_ellipse(tuple(center), a, b)
        try:
            # First try direct creation from the implicit ellipse (preferred)
            ellipse = AreaRegion(ellipse_curve)
        except Exception:
            # Fallback: This shouldn't be needed for ellipse, but kept for robustness
            from geometry import TrimmedImplicitCurve
            import sympy as sp
            x, y = sp.symbols('x y')
            composite_curve = CompositeCurve([TrimmedImplicitCurve(ellipse_curve, lambda px, py: True)], (x, y))
            ellipse = AreaRegion(composite_curve)
        
        self.scene_manager.add_object(obj_id, ellipse)
        
        # Apply style if provided
        style = params.get('style', {})
        if style:
            self.scene_manager.set_style(obj_id, style)
        
        return {
            'object_id': obj_id,
            'type': 'ellipse',
            'center': center,
            'semi_major': a,
            'semi_minor': b,
            'style': style
        }
    
    # ================== Object Management Commands ==================
    
    def _cmd_remove_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove an object from the scene."""
        obj_id = params.get('object_id')
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        
        self.scene_manager.remove_object(obj_id)
        return {'object_id': obj_id, 'removed': True}
    
    def _cmd_get_object_style(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get object style."""
        obj_id = params.get('object_id')
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        
        style = self.scene_manager.get_style(obj_id)
        return {'object_id': obj_id, 'style': style}
    
    def _cmd_set_object_style(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set object style."""
        obj_id = params.get('object_id')
        style = params.get('style')
        
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        if not style:
            raise ValueError("Missing required parameter: style")
        
        self.scene_manager.set_style(obj_id, style)
        return {'object_id': obj_id, 'style': style, 'updated': True}
    
    def _cmd_get_object_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get object parameters."""
        obj_id = params.get('object_id')
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        
        obj = self.scene_manager.get_object(obj_id)
        
        if hasattr(obj, 'get_parameters'):
            parameters = obj.get_parameters()
            parameter_names = obj.list_parameters() if hasattr(obj, 'list_parameters') else []
            
            return {
                'object_id': obj_id,
                'parameters': parameters,
                'parameter_names': parameter_names
            }
        else:
            return {
                'object_id': obj_id,
                'parameters': {},
                'parameter_names': [],
                'message': 'Object does not support parameters'
            }
    
    def _cmd_set_object_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set object parameter."""
        obj_id = params.get('object_id')
        parameter_name = params.get('parameter_name')
        parameter_value = params.get('parameter_value')
        
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        if not parameter_name:
            raise ValueError("Missing required parameter: parameter_name")
        if parameter_value is None:
            raise ValueError("Missing required parameter: parameter_value")
        
        self.scene_manager.update_parameter(obj_id, parameter_name, parameter_value)
        
        return {
            'object_id': obj_id,
            'parameter_name': parameter_name,
            'parameter_value': parameter_value,
            'updated': True
        }
    
    # ================== Animation Commands ==================
    
    def _cmd_create_parameter_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create parameter animation."""
        obj_id = params.get('object_id')
        parameter_name = params.get('parameter_name')
        values = params.get('values')
        
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        if not parameter_name:
            raise ValueError("Missing required parameter: parameter_name")
        if not values:
            raise ValueError("Missing required parameter: values")
        
        animation_id = self.scene_manager.create_parameter_animation(
            obj_id, parameter_name, values
        )
        
        return {
            'animation_id': animation_id,
            'object_id': obj_id,
            'parameter_name': parameter_name,
            'frame_count': len(values)
        }
    
    def _cmd_create_multi_parameter_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create multi-parameter animation."""
        animations = params.get('animations')
        
        if not animations:
            raise ValueError("Missing required parameter: animations")
        
        animation_id = self.scene_manager.create_multi_parameter_animation(animations)
        
        return {
            'animation_id': animation_id,
            'animation_count': len(animations),
            'frame_count': len(next(iter(animations.values()))['values']) if animations else 0
        }
    
    def _cmd_replay_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Replay cached animation."""
        animation_id = params.get('animation_id')
        
        if not animation_id:
            raise ValueError("Missing required parameter: animation_id")
        
        result = self.scene_manager.replay_cached_animation(animation_id)
        
        return {
            'animation_id': animation_id,
            'replayed': result is not None,
            'frame_count': len(result) if result else 0
        }
    
    def _cmd_clear_animation_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear animation cache."""
        animation_id = params.get('animation_id')  # Optional - clears all if None
        
        if animation_id:
            self.scene_manager.clear_animation_cache(animation_id)
            return {'animation_id': animation_id, 'cleared': True}
        else:
            self.scene_manager.clear_animation_cache()
            return {'cleared_all': True}
    
    def _cmd_get_animation_cache_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get animation cache information."""
        return self.scene_manager.get_animation_cache_info()
    
    # ================== Rendering Commands ==================
    
    def _cmd_render_scene_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render scene to image file."""
        filename = params.get('filename')
        if not filename:
            # Generate temporary filename
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            filename = temp_file.name
            temp_file.close()
        
        bounds = params.get('bounds')
        resolution = params.get('resolution')
        show_grid = params.get('show_grid', True)
        show_axes = params.get('show_axes', True)
        
        result = self.graphics_backend.render_scene_image(
            filename, bounds, resolution, show_grid, show_axes
        )
        
        return result
    
    def _cmd_get_curve_paths(self, params: Dict[str, Any]) -> Dict[str, Dict]:
        """Get curve path data."""
        bounds = params.get('bounds')
        resolution = params.get('resolution', 200)
        
        return self.graphics_backend.get_curve_paths(bounds, resolution)
    
    def _cmd_get_field_data(self, params: Dict[str, Any]) -> Dict[str, Dict]:
        """Get field data."""
        bounds = params.get('bounds')
        resolution = params.get('resolution')
        
        return self.graphics_backend.get_field_data(bounds, resolution)
    
    def _cmd_get_region_data(self, params: Dict[str, Any]) -> Dict[str, Dict]:
        """Get region data."""
        bounds = params.get('bounds')
        resolution = params.get('resolution')
        
        return self.graphics_backend.get_region_data(bounds, resolution)
    
    def _cmd_get_scene_bounds(self, params: Dict[str, Any]) -> List[float]:
        """Get optimal scene bounds."""
        padding = params.get('padding', 0.1)
        bounds = self.graphics_backend.get_scene_bounds(padding)
        return list(bounds)
    
    # ================== Grouping and Dependencies ==================
    
    def _cmd_create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create object group."""
        group_name = params.get('group_name')
        object_ids = params.get('object_ids', [])
        
        if not group_name:
            raise ValueError("Missing required parameter: group_name")
        
        # Use SceneManager's set_group method
        self.scene_manager.set_group(group_name, object_ids)
        
        return {
            'group_name': group_name,
            'object_count': len(object_ids),
            'created': True
        }
    
    def _cmd_add_to_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add object to group."""
        group_name = params.get('group_name')
        object_id = params.get('object_id')
        
        if not group_name:
            raise ValueError("Missing required parameter: group_name")
        if not object_id:
            raise ValueError("Missing required parameter: object_id")
        
        # Get current group members and add new object
        current_members = self.scene_manager._groups.get(group_name, [])
        if object_id not in current_members:
            updated_members = current_members + [object_id]
            self.scene_manager.set_group(group_name, updated_members)
        
        return {
            'group_name': group_name,
            'object_id': object_id,
            'added': True
        }
    
    def _cmd_remove_from_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove object from group."""
        group_name = params.get('group_name')
        object_id = params.get('object_id')
        
        if not group_name:
            raise ValueError("Missing required parameter: group_name")
        if not object_id:
            raise ValueError("Missing required parameter: object_id")
        
        # Get current group members and remove object
        current_members = self.scene_manager._groups.get(group_name, [])
        if object_id in current_members:
            updated_members = [obj for obj in current_members if obj != object_id]
            self.scene_manager.set_group(group_name, updated_members)
        
        return {
            'group_name': group_name,
            'object_id': object_id,
            'removed': True
        }
    
    def _cmd_register_dependency(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register object dependency."""
        source_id = params.get('source_id')
        dependent_id = params.get('dependent_id')
        
        if not source_id:
            raise ValueError("Missing required parameter: source_id")
        if not dependent_id:
            raise ValueError("Missing required parameter: dependent_id")
        
        self.scene_manager.register_dependency(source_id, dependent_id)
        
        return {
            'source_id': source_id,
            'dependent_id': dependent_id,
            'registered': True
        }
    
    def _cmd_get_dependencies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get object dependencies."""
        obj_id = params.get('object_id')
        
        if not obj_id:
            raise ValueError("Missing required parameter: object_id")
        
        deps = self.scene_manager.get_dependencies(obj_id)
        
        return {
            'object_id': obj_id,
            'dependencies': deps
        }
    
    # ================== Utility Commands ==================
    
    def _cmd_list_commands(self, params: Dict[str, Any]) -> List[str]:
        """List all available commands."""
        return sorted(self._commands.keys())
    
    def _cmd_get_command_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific command."""
        command = params.get('command')
        
        if not command:
            raise ValueError("Missing required parameter: command")
        
        if command not in self._commands:
            raise ValueError(f"Unknown command: {command}")
        
        # Get command function and docstring
        cmd_func = self._commands[command]
        docstring = cmd_func.__doc__ or "No description available"
        
        return {
            'command': command,
            'description': docstring.strip(),
            'available': True
        }
