"""
Test suite for SceneManager parameter animation system.

Tests core scene management functionality including object lifecycle,
parameter animation, dependency tracking, and frame caching.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch

from scene_management import SceneManager
from geometry.parameter_interface import ParameterInterface, CircleParameters


class MockAnimatableObject(ParameterInterface):
    """Mock object for testing parameter animation."""
    
    def __init__(self, name: str = "test", radius: float = 1.0):
        self.name = name
        self._radius = radius
        self._parameters = {'radius': radius}
        self.parameter_change_count = 0
    
    def get_parameters(self):
        return self._parameters.copy()
    
    def set_parameter(self, name: str, value):
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        self._parameters[name] = value
        if name == 'radius':
            self._radius = value
        self.parameter_change_count += 1
    
    def get_parameter(self, name: str):
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        return self._parameters[name]
    
    def list_parameters(self):
        return list(self._parameters.keys())
    
    def clone(self):
        return MockAnimatableObject(self.name, self._radius)
    
    def to_dict(self):
        return {
            'type': 'MockAnimatableObject',
            'name': self.name,
            'radius': self._radius
        }


class TestSceneManagerBasics:
    """Test basic scene management functionality."""
    
    def test_scene_manager_initialization(self):
        """Test SceneManager initializes correctly."""
        scene = SceneManager()
        assert len(scene.list_objects()) == 0
        assert scene._cache_directory.exists()
    
    def test_add_object_success(self):
        """Test adding objects to scene."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1", 2.0)
        
        scene.add_object("obj1", obj)
        
        assert "obj1" in scene.list_objects()
        assert scene.get_object("obj1") is obj
    
    def test_add_object_duplicate_id_fails(self):
        """Test adding object with duplicate ID fails."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1")
        obj2 = MockAnimatableObject("circle2")
        
        scene.add_object("obj1", obj1)
        
        with pytest.raises(ValueError, match="Object ID 'obj1' already exists"):
            scene.add_object("obj1", obj2)
    
    def test_remove_object_success(self):
        """Test removing objects from scene."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj)
        scene.remove_object("obj1")
        
        assert "obj1" not in scene.list_objects()
        with pytest.raises(KeyError):
            scene.get_object("obj1")
    
    def test_remove_nonexistent_object_fails(self):
        """Test removing non-existent object fails."""
        scene = SceneManager()
        
        with pytest.raises(KeyError, match="Object ID 'nonexistent' not found"):
            scene.remove_object("nonexistent")
    
    def test_get_nonexistent_object_fails(self):
        """Test getting non-existent object fails."""
        scene = SceneManager()
        
        with pytest.raises(KeyError, match="Object ID 'nonexistent' not found"):
            scene.get_object("nonexistent")


class TestStyleManagement:
    """Test style management functionality."""
    
    def test_default_style_applied(self):
        """Test default style is applied to new objects."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj)
        style = scene.get_style("obj1")
        
        assert 'color' in style
        assert 'linewidth' in style
        assert 'alpha' in style
    
    def test_custom_style_on_add(self):
        """Test custom style can be set when adding object."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        custom_style = {'color': 'red', 'linewidth': 3.0}
        
        scene.add_object("obj1", obj, style=custom_style)
        style = scene.get_style("obj1")
        
        assert style['color'] == 'red'
        assert style['linewidth'] == 3.0
    
    def test_set_style_updates_existing(self):
        """Test setting style updates existing style."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj)
        original_style = scene.get_style("obj1")
        
        scene.set_style("obj1", {'color': 'blue'})
        updated_style = scene.get_style("obj1")
        
        assert updated_style['color'] == 'blue'
        # Other properties should be preserved
        assert updated_style['linewidth'] == original_style['linewidth']
    
    def test_style_operations_on_nonexistent_object_fail(self):
        """Test style operations on non-existent objects fail."""
        scene = SceneManager()
        
        with pytest.raises(KeyError):
            scene.get_style("nonexistent")
        
        with pytest.raises(KeyError):
            scene.set_style("nonexistent", {'color': 'red'})


class TestGroupManagement:
    """Test group management functionality."""
    
    def test_set_group_success(self):
        """Test setting group with valid objects."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1")
        obj2 = MockAnimatableObject("circle2")
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        
        scene.set_group("group1", ["obj1", "obj2"])
        
        # Group should be stored
        assert "group1" in scene._groups
        assert scene._groups["group1"] == ["obj1", "obj2"]
    
    def test_set_group_with_nonexistent_object_fails(self):
        """Test setting group with non-existent object fails."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj1)
        
        with pytest.raises(KeyError, match="Object ID 'nonexistent' not found"):
            scene.set_group("group1", ["obj1", "nonexistent"])
    
    def test_update_group_style(self):
        """Test updating style for all objects in group."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1")
        obj2 = MockAnimatableObject("circle2")
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        scene.set_group("group1", ["obj1", "obj2"])
        
        scene.update_group_style("group1", {'color': 'green'})
        
        assert scene.get_style("obj1")['color'] == 'green'
        assert scene.get_style("obj2")['color'] == 'green'
    
    def test_update_nonexistent_group_fails(self):
        """Test updating non-existent group fails."""
        scene = SceneManager()
        
        with pytest.raises(KeyError, match="Group ID 'nonexistent' not found"):
            scene.update_group_style("nonexistent", {'color': 'red'})


class TestParameterManagement:
    """Test parameter management functionality."""
    
    def test_update_parameter_success(self):
        """Test updating object parameter."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1", 1.0)
        
        scene.add_object("obj1", obj)
        scene.update_parameter("obj1", "radius", 2.5)
        
        assert scene.get_parameter("obj1", "radius") == 2.5
        assert obj.parameter_change_count == 1
    
    def test_get_parameter_success(self):
        """Test getting object parameter."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1", 1.5)
        
        scene.add_object("obj1", obj)
        
        assert scene.get_parameter("obj1", "radius") == 1.5
    
    def test_list_parameters_success(self):
        """Test listing object parameters."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj)
        params = scene.list_parameters("obj1")
        
        assert "radius" in params
    
    def test_parameter_operations_on_nonexistent_object_fail(self):
        """Test parameter operations on non-existent objects fail."""
        scene = SceneManager()
        
        with pytest.raises(KeyError):
            scene.update_parameter("nonexistent", "radius", 2.0)
        
        with pytest.raises(KeyError):
            scene.get_parameter("nonexistent", "radius")
        
        with pytest.raises(KeyError):
            scene.list_parameters("nonexistent")
    
    def test_parameter_operations_on_non_animatable_object_fail(self):
        """Test parameter operations on objects without parameter interface fail."""
        scene = SceneManager()
        obj = object()  # Regular object without parameter interface
        
        scene.add_object("obj1", obj)
        
        with pytest.raises(AttributeError):
            scene.update_parameter("obj1", "radius", 2.0)
        
        with pytest.raises(AttributeError):
            scene.get_parameter("obj1", "radius")
        
        with pytest.raises(AttributeError):
            scene.list_parameters("obj1")


class TestDependencyManagement:
    """Test dependency tracking functionality."""
    
    def test_register_dependency_success(self):
        """Test registering dependency relationship."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("source")
        obj2 = MockAnimatableObject("dependent")
        
        scene.add_object("source", obj1)
        scene.add_object("dependent", obj2)
        
        scene.register_dependency("dependent", "source")
        
        deps = scene.get_dependencies("source")
        assert "dependent" in deps['dependents']
        
        deps = scene.get_dependencies("dependent")
        assert "source" in deps['sources']
    
    def test_register_dependency_with_nonexistent_objects_fails(self):
        """Test registering dependency with non-existent objects fails."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("source")
        
        scene.add_object("source", obj1)
        
        with pytest.raises(KeyError):
            scene.register_dependency("nonexistent", "source")
        
        with pytest.raises(KeyError):
            scene.register_dependency("source", "nonexistent")
    
    def test_remove_object_cleans_dependencies(self):
        """Test removing object cleans up its dependencies."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("source")
        obj2 = MockAnimatableObject("dependent")
        
        scene.add_object("source", obj1)
        scene.add_object("dependent", obj2)
        scene.register_dependency("dependent", "source")
        
        scene.remove_object("source")
        
        deps = scene.get_dependencies("dependent")
        assert len(deps['sources']) == 0


class TestAnimationSystem:
    """Test parameter animation functionality."""
    
    @patch('scene_management.scene_manager.plt')
    def test_create_parameter_animation_basic(self, mock_plt):
        """Test creating basic parameter animation."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1", 1.0)
        
        scene.add_object("obj1", obj)
        
        # Mock matplotlib components
        mock_fig = Mock()
        mock_ax = Mock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        values = [1.0, 1.5, 2.0, 1.5, 1.0]
        
        with patch.object(scene, '_create_animation_from_frames') as mock_create:
            scene.create_parameter_animation(
                "obj1", "radius", values, "test.gif", (800, 600), cache_frames=False
            )
        
        # Should have called render for each value
        assert mock_plt.subplots.call_count == len(values)
        mock_create.assert_called_once()
        
        # Parameter should be restored to original value
        assert scene.get_parameter("obj1", "radius") == 1.0
    
    def test_create_parameter_animation_empty_values_fails(self):
        """Test creating animation with empty values list fails."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1")
        
        scene.add_object("obj1", obj)
        
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            scene.create_parameter_animation("obj1", "radius", [], "test.gif", (800, 600))
    
    @patch('scene_management.scene_manager.plt')
    def test_create_multi_parameter_animation_basic(self, mock_plt):
        """Test creating multi-parameter animation."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1", 1.0)
        obj2 = MockAnimatableObject("circle2", 2.0)
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        
        # Mock matplotlib
        mock_fig = Mock()
        mock_ax = Mock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        animations = [
            {'obj_id': 'obj1', 'parameter': 'radius', 'values': [1.0, 1.5, 2.0]},
            {'obj_id': 'obj2', 'parameter': 'radius', 'values': [2.0, 2.5, 3.0]}
        ]
        
        with patch.object(scene, '_create_animation_from_frames') as mock_create:
            scene.create_multi_parameter_animation(
                animations, "test.gif", (800, 600), cache_frames=False
            )
        
        # Should have rendered 3 frames
        assert mock_plt.subplots.call_count == 3
        mock_create.assert_called_once()
        
        # Parameters should be restored
        assert scene.get_parameter("obj1", "radius") == 1.0
        assert scene.get_parameter("obj2", "radius") == 2.0
    
    def test_create_multi_parameter_animation_mismatched_lengths_fails(self):
        """Test multi-parameter animation with mismatched value lengths fails."""
        scene = SceneManager()
        obj1 = MockAnimatableObject("circle1")
        obj2 = MockAnimatableObject("circle2")
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        
        animations = [
            {'obj_id': 'obj1', 'parameter': 'radius', 'values': [1.0, 1.5]},
            {'obj_id': 'obj2', 'parameter': 'radius', 'values': [2.0, 2.5, 3.0]}  # Different length
        ]
        
        with pytest.raises(ValueError, match="All animations must have the same number of values"):
            scene.create_multi_parameter_animation(animations, "test.gif", (800, 600))
    
    def test_animation_cache_management(self):
        """Test animation cache management."""
        scene = SceneManager()
        
        # Initially no cache
        assert len(scene.get_animation_cache_info()) == 0
        
        # Add mock cache entry
        scene._animation_cache['test_cache'] = {
            'frame_count': 5,
            'cache_size_mb': 1.5,
            'created': '2023-01-01T00:00:00',
            'frame_files': []
        }
        
        cache_info = scene.get_animation_cache_info()
        assert 'test_cache' in cache_info
        assert cache_info['test_cache']['frame_count'] == 5
        
        # Clear cache
        scene.clear_animation_cache()
        assert len(scene.get_animation_cache_info()) == 0


class TestPersistence:
    """Test scene persistence functionality."""
    
    def test_save_scene_basic(self):
        """Test basic scene saving."""
        scene = SceneManager()
        obj = MockAnimatableObject("circle1", 2.0)
        
        scene.add_object("obj1", obj, style={'color': 'red'})
        scene.set_group("group1", ["obj1"])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            scene.save_scene(filename)
            
            # Verify file was created and contains expected data
            assert os.path.exists(filename)
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            assert 'objects' in data
            assert 'styles' in data
            assert 'groups' in data
            assert data['groups']['group1'] == ['obj1']
            assert data['styles']['obj1']['color'] == 'red'
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_load_scene_basic(self):
        """Test basic scene loading."""
        scene = SceneManager()
        
        # Create test data
        test_data = {
            'objects': {},
            'styles': {'obj1': {'color': 'blue'}},
            'groups': {'group1': ['obj1']},
            'dependencies': {},
            'reverse_dependencies': {},
            'metadata': {'version': '1.0'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            filename = f.name
        
        try:
            scene.load_scene(filename)
            
            # Verify data was loaded
            assert scene._styles['obj1']['color'] == 'blue'
            assert scene._groups['group1'] == ['obj1']
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == '__main__':
    pytest.main([__file__])
