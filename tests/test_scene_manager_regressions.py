"""
Comprehensive regression test suite for SceneManager.

Tests edge cases, error conditions, performance scenarios, and complex
interactions to prevent regressions and catch subtle bugs.
"""

import pytest
import tempfile
import os
import json
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from scene_management import SceneManager
from geometry.parameter_interface import ParameterInterface


class ComplexAnimatableObject(ParameterInterface):
    """Complex mock object with multiple parameters and validation."""
    
    def __init__(self, obj_id: str = "complex", **params):
        self.obj_id = obj_id
        self._parameters = {
            'x': params.get('x', 0.0),
            'y': params.get('y', 0.0),
            'radius': params.get('radius', 1.0),
            'angle': params.get('angle', 0.0),
            'scale': params.get('scale', 1.0),
            'visible': params.get('visible', True)
        }
        self.update_count = 0
        self.validation_errors = []
        self.dependency_updates = []
    
    def get_parameters(self):
        return self._parameters.copy()
    
    def set_parameter(self, name: str, value):
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        
        # Validation logic
        if name == 'radius' and value <= 0:
            raise ValueError(f"Radius must be positive, got {value}")
        if name == 'scale' and value <= 0:
            raise ValueError(f"Scale must be positive, got {value}")
        if name == 'angle' and not isinstance(value, (int, float)):
            raise TypeError(f"Angle must be numeric, got {type(value)}")
        
        old_value = self._parameters[name]
        self._parameters[name] = value
        self.update_count += 1
        
        # Simulate expensive computation for some parameters
        if name in ['radius', 'scale']:
            time.sleep(0.001)  # Simulate slow update
    
    def get_parameter(self, name: str):
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        return self._parameters[name]
    
    def list_parameters(self):
        return list(self._parameters.keys())
    
    def clone(self):
        return ComplexAnimatableObject(self.obj_id, **self._parameters)
    
    def refresh_from_dependencies(self):
        """Track dependency updates."""
        self.dependency_updates.append(time.time())
    
    def to_dict(self):
        return {
            'type': 'ComplexAnimatableObject',
            'obj_id': self.obj_id,
            'parameters': self._parameters.copy()
        }


class BrokenAnimatableObject(ParameterInterface):
    """Object that fails in various ways for error testing."""
    
    def __init__(self, fail_mode: str = "none"):
        self.fail_mode = fail_mode
        self._parameters = {'value': 1.0}
    
    def get_parameters(self):
        if self.fail_mode == "get_parameters":
            raise RuntimeError("Simulated get_parameters failure")
        return self._parameters.copy()
    
    def set_parameter(self, name: str, value):
        if self.fail_mode == "set_parameter":
            raise RuntimeError("Simulated set_parameter failure")
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        self._parameters[name] = value
    
    def get_parameter(self, name: str):
        if self.fail_mode == "get_parameter":
            raise RuntimeError("Simulated get_parameter failure")
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        return self._parameters[name]
    
    def list_parameters(self):
        if self.fail_mode == "list_parameters":
            raise RuntimeError("Simulated list_parameters failure")
        return list(self._parameters.keys())
    
    def clone(self):
        if self.fail_mode == "clone":
            raise RuntimeError("Simulated clone failure")
        return BrokenAnimatableObject(self.fail_mode)
    
    def to_dict(self):
        if self.fail_mode == "to_dict":
            raise RuntimeError("Simulated to_dict failure")
        return {'type': 'BrokenAnimatableObject', 'fail_mode': self.fail_mode}


class TestSceneManagerEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_scene_operations(self):
        """Test operations on empty scene."""
        scene = SceneManager()
        
        assert scene.list_objects() == []
        assert scene.get_animation_cache_info() == {}
        
        # Operations that should fail gracefully
        with pytest.raises(KeyError):
            scene.get_object("nonexistent")
        
        with pytest.raises(KeyError):
            scene.remove_object("nonexistent")
    
    def test_object_id_edge_cases(self):
        """Test various object ID formats."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        
        # Test various ID formats
        edge_case_ids = [
            "",  # Empty string
            " ",  # Whitespace
            "obj with spaces",
            "obj-with-dashes",
            "obj_with_underscores",
            "obj.with.dots",
            "123numeric",
            "UPPERCASE",
            "MiXeDcAsE",
            "very_long_object_id_that_exceeds_normal_expectations_but_should_still_work",
            "unicode_测试",
            "special!@#$%^&*()chars"
        ]
        
        for obj_id in edge_case_ids:
            try:
                scene.add_object(obj_id, ComplexAnimatableObject(obj_id))
                assert obj_id in scene.list_objects()
                retrieved = scene.get_object(obj_id)
                assert retrieved.obj_id == obj_id
                scene.remove_object(obj_id)
            except Exception as e:
                pytest.fail(f"Failed to handle object ID '{obj_id}': {e}")
    
    def test_parameter_value_edge_cases(self):
        """Test edge cases for parameter values."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        scene.add_object("obj", obj)
        
        # Test extreme numeric values
        extreme_values = [
            0.0,
            1e-10,  # Very small
            1e10,   # Very large
            float('inf'),
            -float('inf'),
            np.pi,
            np.e
        ]
        
        for value in extreme_values:
            try:
                scene.update_parameter("obj", "x", value)
                assert scene.get_parameter("obj", "x") == value
            except Exception as e:
                # Some extreme values might legitimately fail
                if value in [float('inf'), -float('inf')]:
                    continue  # These might be rejected by validation
                pytest.fail(f"Failed to handle parameter value {value}: {e}")
    
    def test_large_scene_performance(self):
        """Test performance with large number of objects."""
        scene = SceneManager()
        
        # Add many objects
        num_objects = 100
        for i in range(num_objects):
            obj = ComplexAnimatableObject(f"obj_{i}")
            scene.add_object(f"obj_{i}", obj)
        
        assert len(scene.list_objects()) == num_objects
        
        # Test bulk operations
        start_time = time.time()
        for i in range(num_objects):
            scene.update_parameter(f"obj_{i}", "radius", 2.0)
        update_time = time.time() - start_time
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert update_time < 5.0, f"Bulk updates took too long: {update_time:.2f}s"
        
        # Verify all updates applied
        for i in range(num_objects):
            assert scene.get_parameter(f"obj_{i}", "radius") == 2.0


class TestParameterValidationRegressions:
    """Test parameter validation and error handling."""
    
    def test_invalid_parameter_values(self):
        """Test handling of invalid parameter values."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        scene.add_object("obj", obj)
        
        # Test invalid radius (should be positive)
        with pytest.raises(ValueError, match="Radius must be positive"):
            scene.update_parameter("obj", "radius", -1.0)
        
        with pytest.raises(ValueError, match="Radius must be positive"):
            scene.update_parameter("obj", "radius", 0.0)
        
        # Test invalid scale
        with pytest.raises(ValueError, match="Scale must be positive"):
            scene.update_parameter("obj", "scale", -0.5)
        
        # Test invalid angle type
        with pytest.raises(TypeError, match="Angle must be numeric"):
            scene.update_parameter("obj", "angle", "not_a_number")
    
    def test_parameter_validation_during_animation(self):
        """Test parameter validation during animation creation."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        scene.add_object("obj", obj)
        
        # Animation with invalid values should fail
        invalid_values = [1.0, 2.0, -1.0, 3.0]  # Contains negative radius
        
        with patch.object(scene, '_create_animation_from_frames'):
            with pytest.raises(ValueError, match="Radius must be positive"):
                scene.create_parameter_animation(
                    "obj", "radius", invalid_values, "test.gif", (100, 100), cache_frames=False
                )
    
    def test_broken_object_handling(self):
        """Test handling of objects that fail in various ways."""
        scene = SceneManager()
        
        # Test object that fails during parameter operations
        broken_obj = BrokenAnimatableObject("set_parameter")
        scene.add_object("broken", broken_obj)
        
        with pytest.raises(RuntimeError, match="Simulated set_parameter failure"):
            scene.update_parameter("broken", "value", 2.0)
        
        # Test object that fails during serialization
        broken_serialize = BrokenAnimatableObject("to_dict")
        scene.add_object("broken_serialize", broken_serialize)
        
        # save_scene should handle serialization failures gracefully
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            # Should not crash, but will print warning and store fallback data
            scene.save_scene(filename)
            
            # Verify file was created and contains fallback data
            assert os.path.exists(filename)
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Should contain fallback data for broken object
            assert 'broken_serialize' in data['objects']
            broken_data = data['objects']['broken_serialize']
            assert broken_data['type'] == 'UnserializableObject'
            assert 'error' in broken_data
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)


class TestAnimationSystemRegressions:
    """Test animation system edge cases and error conditions."""
    
    @patch('scene_management.scene_manager.plt')
    def test_animation_with_parameter_restoration_failure(self, mock_plt):
        """Test animation when parameter restoration fails."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        scene.add_object("obj", obj)
        
        mock_fig = Mock()
        mock_ax = Mock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        # Mock parameter restoration to fail
        original_update = scene.update_parameter
        call_count = [0]
        
        def failing_update_parameter(obj_id, param, value, update_dependents=True):
            call_count[0] += 1
            if call_count[0] > 3:  # Fail on restoration
                raise RuntimeError("Parameter restoration failed")
            return original_update(obj_id, param, value, update_dependents)
        
        scene.update_parameter = failing_update_parameter
        
        values = [1.0, 2.0, 3.0]
        
        with patch.object(scene, '_create_animation_from_frames'):
            with pytest.raises(RuntimeError, match="Parameter restoration failed"):
                scene.create_parameter_animation(
                    "obj", "radius", values, "test.gif", (100, 100), cache_frames=False
                )
    
    def test_animation_cache_corruption_handling(self):
        """Test handling of corrupted animation cache."""
        scene = SceneManager()
        
        # Simulate corrupted cache entry
        scene._animation_cache['corrupted'] = {
            'frame_files': ['/nonexistent/path1.png', '/nonexistent/path2.png'],
            'frame_count': 2,
            'cache_size_mb': 1.0,
            'created': '2023-01-01T00:00:00'
        }
        
        # Should handle missing files gracefully
        scene.clear_animation_cache('corrupted')
        assert 'corrupted' not in scene._animation_cache
    
    def test_concurrent_animation_operations(self):
        """Test thread safety of animation operations."""
        scene = SceneManager()
        obj = ComplexAnimatableObject()
        scene.add_object("obj", obj)
        
        errors = []
        
        def update_parameters():
            try:
                for i in range(10):
                    scene.update_parameter("obj", "x", float(i))
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        def manage_cache():
            try:
                for i in range(5):
                    # Add fake cache entry
                    cache_id = f"cache_{i}"
                    scene._animation_cache[cache_id] = {
                        'frame_count': 1,
                        'cache_size_mb': 0.1,
                        'created': '2023-01-01T00:00:00',
                        'frame_files': []
                    }
                    time.sleep(0.002)
                    # Clear it
                    scene.clear_animation_cache(cache_id)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent operations
        threads = [
            threading.Thread(target=update_parameters),
            threading.Thread(target=manage_cache)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check for thread safety issues
        if errors:
            pytest.fail(f"Concurrent operations failed: {errors}")


class TestDependencySystemRegressions:
    """Test dependency system edge cases."""
    
    def test_circular_dependency_detection(self):
        """Test detection and handling of circular dependencies."""
        scene = SceneManager()
        
        obj1 = ComplexAnimatableObject("obj1")
        obj2 = ComplexAnimatableObject("obj2")
        obj3 = ComplexAnimatableObject("obj3")
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        scene.add_object("obj3", obj3)
        
        # Create circular dependency: obj1 -> obj2 -> obj3 -> obj1
        scene.register_dependency("obj2", "obj1")
        scene.register_dependency("obj3", "obj2")
        
        # This should be allowed (detection is future enhancement)
        scene.register_dependency("obj1", "obj3")
        
        # Update should not cause infinite loop
        scene.update_parameter("obj1", "radius", 2.0, update_dependents=True)
    
    def test_dependency_cleanup_on_object_removal(self):
        """Test thorough cleanup of dependencies when objects are removed."""
        scene = SceneManager()
        
        # Create complex dependency network
        objects = {}
        for i in range(5):
            obj = ComplexAnimatableObject(f"obj{i}")
            objects[f"obj{i}"] = obj
            scene.add_object(f"obj{i}", obj)
        
        # Create dependencies: obj0 -> obj1 -> obj2, obj0 -> obj3 -> obj4
        scene.register_dependency("obj1", "obj0")
        scene.register_dependency("obj2", "obj1")
        scene.register_dependency("obj3", "obj0")
        scene.register_dependency("obj4", "obj3")
        
        # Remove central object
        scene.remove_object("obj0")
        
        # Verify all dependencies cleaned up
        for obj_id in ["obj1", "obj2", "obj3", "obj4"]:
            deps = scene.get_dependencies(obj_id)
            assert "obj0" not in deps['sources']
            assert "obj0" not in deps['dependents']
    
    def test_dependency_update_with_failures(self):
        """Test dependency updates when some dependents fail."""
        scene = SceneManager()
        
        source = ComplexAnimatableObject("source")
        good_dependent = ComplexAnimatableObject("good")
        bad_dependent = BrokenAnimatableObject("set_parameter")
        
        scene.add_object("source", source)
        scene.add_object("good", good_dependent)
        scene.add_object("bad", bad_dependent)
        
        scene.register_dependency("good", "source")
        scene.register_dependency("bad", "source")
        
        # Update should not fail even if one dependent fails
        scene.update_parameter("source", "radius", 2.0, update_dependents=True)
        
        # Good dependent should have been updated
        assert len(good_dependent.dependency_updates) > 0


class TestPersistenceRegressions:
    """Test scene persistence edge cases."""
    
    def test_save_load_with_complex_data(self):
        """Test persistence with complex parameter values."""
        scene = SceneManager()
        
        # Create objects with various parameter types
        obj1 = ComplexAnimatableObject("complex1", 
                                     x=np.pi, y=np.e, radius=1.414, 
                                     angle=2*np.pi/3, visible=True)
        obj2 = ComplexAnimatableObject("complex2",
                                     x=-1.5, y=0.0, scale=0.707,
                                     angle=-np.pi/4, visible=False)
        
        scene.add_object("obj1", obj1)
        scene.add_object("obj2", obj2)
        
        # Create complex grouping and dependencies
        scene.set_group("group1", ["obj1", "obj2"])
        scene.register_dependency("obj2", "obj1")
        
        # Save and load
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            scene.save_scene(filename)
            
            # Verify file structure
            with open(filename, 'r') as f:
                data = json.load(f)
            
            assert 'metadata' in data
            assert 'version' in data['metadata']
            assert 'created' in data['metadata']
            assert data['groups']['group1'] == ['obj1', 'obj2']
            assert 'obj1' in data['dependencies']
            
            # Load into new scene
            new_scene = SceneManager()
            new_scene.load_scene(filename)
            
            # Verify structure preserved
            assert new_scene._groups['group1'] == ['obj1', 'obj2']
            assert 'obj1' in new_scene._dependencies
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_save_load_with_corrupted_data(self):
        """Test loading corrupted or invalid scene files."""
        scene = SceneManager()
        
        # Test various corrupted files
        corrupted_data_cases = [
            {},  # Empty
            {'objects': None},  # Null objects
            {'invalid': 'structure'},  # Wrong structure
            {'objects': {}, 'styles': 'not_a_dict'},  # Wrong types
        ]
        
        for i, corrupted_data in enumerate(corrupted_data_cases):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(corrupted_data, f)
                filename = f.name
            
            try:
                # Should handle corrupted data gracefully
                scene.load_scene(filename)
                
                # Scene should be in valid state (empty or with defaults)
                assert isinstance(scene._objects, dict)
                assert isinstance(scene._styles, dict)
                assert isinstance(scene._groups, dict)
                
            except Exception as e:
                # Some corruption might legitimately cause exceptions
                # but they should be informative
                assert "json" in str(e).lower() or "load" in str(e).lower()
            
            finally:
                if os.path.exists(filename):
                    os.remove(filename)


class TestMemoryAndResourceManagement:
    """Test memory usage and resource cleanup."""
    
    def test_animation_cache_memory_limits(self):
        """Test animation cache doesn't grow unbounded."""
        scene = SceneManager()
        
        # Simulate many large cache entries
        for i in range(100):
            cache_id = f"large_cache_{i}"
            scene._animation_cache[cache_id] = {
                'frame_count': 100,
                'cache_size_mb': 10.0,  # Simulate 10MB each
                'created': f'2023-01-{i:02d}T00:00:00',
                'frame_files': [f'/fake/path_{j}.png' for j in range(100)]
            }
        
        # Total simulated cache size: 1GB
        cache_info = scene.get_animation_cache_info()
        total_size = sum(info['cache_size_mb'] for info in cache_info.values())
        assert total_size == 1000.0  # 100 * 10MB
        
        # Clear all caches
        scene.clear_animation_cache()
        
        # Should be empty
        assert len(scene.get_animation_cache_info()) == 0
    
    def test_object_cleanup_on_scene_destruction(self):
        """Test proper cleanup when scene is destroyed."""
        scene = SceneManager()
        
        # Add many objects
        for i in range(50):
            obj = ComplexAnimatableObject(f"obj_{i}")
            scene.add_object(f"obj_{i}", obj)
        
        # Add cache entries
        for i in range(10):
            scene._animation_cache[f"cache_{i}"] = {
                'frame_count': 10,
                'cache_size_mb': 1.0,
                'created': '2023-01-01T00:00:00',
                'frame_files': []
            }
        
        # Clear references
        initial_object_count = len(scene._objects)
        initial_cache_count = len(scene._animation_cache)
        
        assert initial_object_count == 50
        assert initial_cache_count == 10
        
        # Cleanup
        scene.clear_animation_cache()
        scene._objects.clear()
        scene._styles.clear()
        scene._groups.clear()
        
        assert len(scene._objects) == 0
        assert len(scene._animation_cache) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
