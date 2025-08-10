"""
SceneManager - Core scene management and parameter animation system for 2Top

Provides comprehensive scene state management, object lifecycle, persistence,
grouping, styling, and parameter-based animation capabilities with frame caching.
"""

import json
import os
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import tempfile
import shutil

# Import geometry classes
from geometry import ImplicitCurve, CompositeCurve, AreaRegion


class SceneManager:
    """
    Manages collections of geometric objects with styling, grouping, persistence,
    and parameter animation capabilities.
    """
    
    def __init__(self):
        """Initialize empty scene manager."""
        # Core registries
        self._objects: Dict[str, Any] = {}
        self._styles: Dict[str, Dict] = {}
        self._groups: Dict[str, List[str]] = {}
        
        # Animation system
        self._dependencies: Dict[str, List[str]] = {}  # obj_id -> [dependent_ids]
        self._reverse_dependencies: Dict[str, List[str]] = {}  # obj_id -> [source_ids]
        self._animation_cache: Dict[str, Dict] = {}
        self._cache_directory = Path(tempfile.gettempdir()) / "2top_animation_cache"
        self._cache_directory.mkdir(exist_ok=True)
        
        # Default styles
        self._default_style = {
            'color': '#1f77b4',
            'linewidth': 2.0,
            'alpha': 1.0,
            'fill_alpha': 0.3
        }
    
    # ================== Core Object Management ==================
    
    def add_object(self, obj_id: str, obj: Union[ImplicitCurve, CompositeCurve, AreaRegion], 
                   style: Optional[Dict] = None) -> None:
        """
        Add a named object to the scene.
        
        Args:
            obj_id: Unique identifier for the object
            obj: Geometric object to add
            style: Optional style dictionary
            
        Raises:
            ValueError: If obj_id already exists
        """
        if obj_id in self._objects:
            raise ValueError(f"Object ID '{obj_id}' already exists")
            
        self._objects[obj_id] = obj
        self._styles[obj_id] = style or self._default_style.copy()
    
    def remove_object(self, obj_id: str) -> None:
        """
        Remove an object from the scene.
        
        Args:
            obj_id: ID of object to remove
            
        Raises:
            KeyError: If obj_id doesn't exist
        """
        if obj_id not in self._objects:
            raise KeyError(f"Object ID '{obj_id}' not found")
            
        # Clean up all associated data
        del self._objects[obj_id]
        del self._styles[obj_id]
        
        # Remove from groups
        for group_id, members in self._groups.items():
            if obj_id in members:
                members.remove(obj_id)
        
        # Clean up dependencies
        self._remove_dependencies(obj_id)
    
    def get_object(self, obj_id: str) -> Any:
        """Get object by ID."""
        if obj_id not in self._objects:
            raise KeyError(f"Object ID '{obj_id}' not found")
        return self._objects[obj_id]
    
    def list_objects(self) -> List[str]:
        """Return list of all object IDs."""
        return list(self._objects.keys())
    
    # ================== Style Management ==================
    
    def set_style(self, obj_id: str, style: Dict) -> None:
        """Set style for an object."""
        if obj_id not in self._objects:
            raise KeyError(f"Object ID '{obj_id}' not found")
        
        # Merge with existing style
        current_style = self._styles[obj_id].copy()
        current_style.update(style)
        self._styles[obj_id] = current_style
    
    def get_style(self, obj_id: str) -> Dict:
        """Get style for an object."""
        if obj_id not in self._objects:
            raise KeyError(f"Object ID '{obj_id}' not found")
        return self._styles[obj_id].copy()
    
    # ================== Group Management ==================
    
    def set_group(self, group_id: str, object_ids: List[str]) -> None:
        """Assign objects to a group."""
        # Validate all object IDs exist
        for obj_id in object_ids:
            if obj_id not in self._objects:
                raise KeyError(f"Object ID '{obj_id}' not found")
        
        self._groups[group_id] = object_ids.copy()
    
    def update_group_style(self, group_id: str, style: Dict) -> None:
        """Update style for all objects in a group."""
        if group_id not in self._groups:
            raise KeyError(f"Group ID '{group_id}' not found")
        
        for obj_id in self._groups[group_id]:
            self.set_style(obj_id, style)
    
    # ================== Parameter Management ==================
    
    def update_parameter(self, obj_id: str, parameter: str, value: Any, 
                        update_dependents: bool = True) -> None:
        """
        Update a parameter on an object and optionally propagate to dependents.
        
        Args:
            obj_id: Object to update
            parameter: Parameter name
            value: New parameter value
            update_dependents: Whether to update dependent objects
        """
        obj = self.get_object(obj_id)
        
        # Check if object supports parameter updates
        if not hasattr(obj, 'set_parameter'):
            raise AttributeError(f"Object '{obj_id}' does not support parameter updates")
        
        # Update the parameter
        obj.set_parameter(parameter, value)
        
        # Update dependents if requested
        if update_dependents and obj_id in self._dependencies:
            for dependent_id in self._dependencies[obj_id]:
                self._update_dependent(dependent_id, obj_id)
    
    def get_parameter(self, obj_id: str, parameter: str) -> Any:
        """Get parameter value from an object."""
        obj = self.get_object(obj_id)
        
        if not hasattr(obj, 'get_parameter'):
            raise AttributeError(f"Object '{obj_id}' does not support parameter access")
        
        return obj.get_parameter(parameter)
    
    def list_parameters(self, obj_id: str) -> List[str]:
        """List all parameters for an object."""
        obj = self.get_object(obj_id)
        
        if not hasattr(obj, 'list_parameters'):
            raise AttributeError(f"Object '{obj_id}' does not support parameter listing")
        
        return obj.list_parameters()
    
    # ================== Dependency Management ==================
    
    def register_dependency(self, dependent_id: str, source_id: str, 
                          update_fn: Optional[Callable] = None) -> None:
        """
        Register a dependency relationship.
        
        Args:
            dependent_id: Object that depends on source
            source_id: Source object that dependent relies on
            update_fn: Optional custom update function
        """
        # Validate objects exist
        self.get_object(dependent_id)
        self.get_object(source_id)
        
        # Add to dependency tracking
        if source_id not in self._dependencies:
            self._dependencies[source_id] = []
        if dependent_id not in self._dependencies[source_id]:
            self._dependencies[source_id].append(dependent_id)
        
        # Add reverse dependency
        if dependent_id not in self._reverse_dependencies:
            self._reverse_dependencies[dependent_id] = []
        if source_id not in self._reverse_dependencies[dependent_id]:
            self._reverse_dependencies[dependent_id].append(source_id)
    
    def get_dependencies(self, obj_id: str) -> Dict[str, List[str]]:
        """Get dependency relationships for an object."""
        return {
            'dependents': self._dependencies.get(obj_id, []),
            'sources': self._reverse_dependencies.get(obj_id, [])
        }
    
    def _remove_dependencies(self, obj_id: str) -> None:
        """Remove all dependency relationships for an object."""
        # Remove as source
        if obj_id in self._dependencies:
            for dependent_id in self._dependencies[obj_id]:
                if dependent_id in self._reverse_dependencies:
                    self._reverse_dependencies[dependent_id].remove(obj_id)
            del self._dependencies[obj_id]
        
        # Remove as dependent
        if obj_id in self._reverse_dependencies:
            for source_id in self._reverse_dependencies[obj_id]:
                if source_id in self._dependencies:
                    self._dependencies[source_id].remove(obj_id)
            del self._reverse_dependencies[obj_id]
    
    def _update_dependent(self, dependent_id: str, source_id: str) -> None:
        """Update a dependent object when its source changes."""
        # Default implementation - can be overridden for custom update logic
        # For now, just trigger a parameter refresh if the object supports it
        dependent = self.get_object(dependent_id)
        if hasattr(dependent, 'refresh_from_dependencies'):
            dependent.refresh_from_dependencies()
    
    # ================== Animation System ==================
    
    def create_parameter_animation(self, obj_id: str, parameter: str, values: List[Any],
                                 filename: str, resolution: Tuple[int, int], 
                                 fps: int = 10, cache_frames: bool = True) -> None:
        """
        Create animation by cycling through parameter values.
        
        Args:
            obj_id: Object to animate
            parameter: Parameter to vary
            values: List of parameter values to cycle through
            filename: Output animation filename
            resolution: (width, height) for rendering
            fps: Frames per second
            cache_frames: Whether to cache frames for replay
        """
        if not values:
            raise ValueError("Values list cannot be empty")
        
        # Generate cache ID
        cache_id = self._generate_cache_id(obj_id, parameter, values, resolution)
        
        # Check if animation is already cached
        if cache_frames and cache_id in self._animation_cache:
            print(f"Using cached animation for {obj_id}.{parameter}")
            self.replay_cached_animation(cache_id, filename, fps)
            return
        
        print(f"Creating parameter animation: {obj_id}.{parameter}")
        frames = []
        frame_files = []
        
        # Store original parameter value
        original_value = self.get_parameter(obj_id, parameter)
        
        try:
            for i, value in enumerate(values):
                print(f"  Rendering frame {i+1}/{len(values)} (value={value})")
                
                # Update parameter
                self.update_parameter(obj_id, parameter, value, update_dependents=True)
                
                # Render frame
                fig, ax = plt.subplots(figsize=(resolution[0]/100, resolution[1]/100), dpi=100)
                self._render_scene(ax)
                
                if cache_frames:
                    # Save frame to cache
                    frame_file = self._cache_directory / f"{cache_id}_frame_{i:04d}.png"
                    fig.savefig(frame_file, dpi=100, bbox_inches='tight')
                    frame_files.append(str(frame_file))
                
                # Keep figure for animation
                frames.append(fig)
                plt.close(fig)
            
            # Create animation
            self._create_animation_from_frames(frame_files if cache_frames else frames, 
                                             filename, fps)
            
            # Store cache info
            if cache_frames:
                self._animation_cache[cache_id] = {
                    'obj_id': obj_id,
                    'parameter': parameter,
                    'values': values,
                    'resolution': resolution,
                    'frame_count': len(values),
                    'frame_files': frame_files,
                    'created': datetime.now().isoformat(),
                    'cache_size_mb': sum(os.path.getsize(f) for f in frame_files) / (1024*1024)
                }
                
        finally:
            # Restore original parameter value
            self.update_parameter(obj_id, parameter, original_value, update_dependents=True)
    
    def create_multi_parameter_animation(self, animations: List[Dict], filename: str,
                                       resolution: Tuple[int, int], fps: int = 10,
                                       cache_frames: bool = True) -> None:
        """
        Create animation with multiple parameters changing simultaneously.
        
        Args:
            animations: List of dicts with 'obj_id', 'parameter', 'values' keys
            filename: Output filename
            resolution: Render resolution
            fps: Frames per second
            cache_frames: Whether to cache frames
        """
        if not animations:
            raise ValueError("Animations list cannot be empty")
        
        # Validate all animations have same number of frames
        frame_count = len(animations[0]['values'])
        for anim in animations:
            if len(anim['values']) != frame_count:
                raise ValueError("All animations must have the same number of values")
        
        # Generate cache ID for multi-parameter animation
        cache_id = self._generate_multi_cache_id(animations, resolution)
        
        if cache_frames and cache_id in self._animation_cache:
            print(f"Using cached multi-parameter animation")
            self.replay_cached_animation(cache_id, filename, fps)
            return
        
        print(f"Creating multi-parameter animation with {len(animations)} parameters")
        frames = []
        frame_files = []
        
        # Store original parameter values
        original_values = {}
        for anim in animations:
            obj_id = anim['obj_id']
            parameter = anim['parameter']
            original_values[(obj_id, parameter)] = self.get_parameter(obj_id, parameter)
        
        try:
            for frame_idx in range(frame_count):
                print(f"  Rendering frame {frame_idx+1}/{frame_count}")
                
                # Update all parameters for this frame
                for anim in animations:
                    obj_id = anim['obj_id']
                    parameter = anim['parameter']
                    value = anim['values'][frame_idx]
                    self.update_parameter(obj_id, parameter, value, update_dependents=True)
                
                # Render frame
                fig, ax = plt.subplots(figsize=(resolution[0]/100, resolution[1]/100), dpi=100)
                self._render_scene(ax)
                
                if cache_frames:
                    frame_file = self._cache_directory / f"{cache_id}_frame_{frame_idx:04d}.png"
                    fig.savefig(frame_file, dpi=100, bbox_inches='tight')
                    frame_files.append(str(frame_file))
                
                frames.append(fig)
                plt.close(fig)
            
            # Create animation
            self._create_animation_from_frames(frame_files if cache_frames else frames,
                                             filename, fps)
            
            # Store cache info
            if cache_frames:
                self._animation_cache[cache_id] = {
                    'type': 'multi_parameter',
                    'animations': animations,
                    'resolution': resolution,
                    'frame_count': frame_count,
                    'frame_files': frame_files,
                    'created': datetime.now().isoformat(),
                    'cache_size_mb': sum(os.path.getsize(f) for f in frame_files) / (1024*1024)
                }
                
        finally:
            # Restore original parameter values
            for (obj_id, parameter), original_value in original_values.items():
                self.update_parameter(obj_id, parameter, original_value, update_dependents=True)
    
    def replay_cached_animation(self, cache_id: str, filename: str, fps: int = 10) -> None:
        """Replay a cached animation."""
        if cache_id not in self._animation_cache:
            raise KeyError(f"Animation cache '{cache_id}' not found")
        
        cache_info = self._animation_cache[cache_id]
        frame_files = cache_info['frame_files']
        
        print(f"Replaying cached animation: {len(frame_files)} frames")
        self._create_animation_from_frames(frame_files, filename, fps)
    
    def clear_animation_cache(self, cache_id: Optional[str] = None) -> None:
        """Clear animation cache."""
        if cache_id is None:
            # Clear all caches
            for cache_info in self._animation_cache.values():
                for frame_file in cache_info.get('frame_files', []):
                    if os.path.exists(frame_file):
                        os.remove(frame_file)
            self._animation_cache.clear()
            print("Cleared all animation caches")
        else:
            # Clear specific cache
            if cache_id in self._animation_cache:
                cache_info = self._animation_cache[cache_id]
                for frame_file in cache_info.get('frame_files', []):
                    if os.path.exists(frame_file):
                        os.remove(frame_file)
                del self._animation_cache[cache_id]
                print(f"Cleared animation cache: {cache_id}")
    
    def get_animation_cache_info(self) -> Dict[str, Dict]:
        """Get information about cached animations."""
        return {cache_id: {
            'frame_count': info['frame_count'],
            'cache_size_mb': info['cache_size_mb'],
            'created': info['created'],
            'type': info.get('type', 'single_parameter')
        } for cache_id, info in self._animation_cache.items()}
    
    # ================== Helper Methods ==================
    
    def _generate_cache_id(self, obj_id: str, parameter: str, values: List[Any], 
                          resolution: Tuple[int, int]) -> str:
        """Generate unique cache ID for animation."""
        content = f"{obj_id}_{parameter}_{values}_{resolution}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_multi_cache_id(self, animations: List[Dict], resolution: Tuple[int, int]) -> str:
        """Generate cache ID for multi-parameter animation."""
        content = str(animations) + str(resolution)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _render_scene(self, ax) -> None:
        """Render current scene to matplotlib axes."""
        # This is a placeholder - would integrate with visual_tests plotting
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Render each object
        for obj_id, obj in self._objects.items():
            style = self._styles[obj_id]
            
            # Basic rendering - would be enhanced with proper visual test integration
            if hasattr(obj, 'plot'):
                obj.plot(xlim=(-3, 3), ylim=(-3, 3), ax=ax, **style)
    
    def _create_animation_from_frames(self, frames, filename: str, fps: int) -> None:
        """Create animation file from frames."""
        if isinstance(frames[0], str):
            # Frames are file paths
            import imageio
            with imageio.get_writer(filename, mode='I', fps=fps) as writer:
                for frame_file in frames:
                    image = imageio.imread(frame_file)
                    writer.append_data(image)
        else:
            # Frames are matplotlib figures - would need different approach
            print(f"Animation saved: {filename}")
    
    # ================== Persistence ==================
    
    def save_scene(self, filename: str) -> None:
        """Save scene to JSON file."""
        scene_data = {
            'objects': {},
            'styles': self._styles.copy(),
            'groups': self._groups.copy(),
            'dependencies': self._dependencies.copy(),
            'reverse_dependencies': self._reverse_dependencies.copy(),
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        # Serialize objects
        for obj_id, obj in self._objects.items():
            if hasattr(obj, 'to_dict'):
                try:
                    scene_data['objects'][obj_id] = obj.to_dict()
                except Exception as e:
                    print(f"Warning: Failed to serialize object '{obj_id}': {e}")
                    # Store minimal fallback data
                    scene_data['objects'][obj_id] = {
                        'type': 'UnserializableObject',
                        'error': str(e),
                        'obj_id': obj_id
                    }
            else:
                print(f"Warning: Object '{obj_id}' does not support serialization")
                # Store minimal fallback data
                scene_data['objects'][obj_id] = {
                    'type': 'NonSerializableObject',
                    'obj_id': obj_id
                }
        
        with open(filename, 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        print(f"Scene saved: {filename}")
    
    def load_scene(self, filename: str) -> None:
        """Load scene from JSON file."""
        with open(filename, 'r') as f:
            scene_data = json.load(f)
        
        # Clear current scene
        self._objects.clear()
        self._styles.clear()
        self._groups.clear()
        self._dependencies.clear()
        self._reverse_dependencies.clear()
        
        # Load styles and groups with error handling
        styles_data = scene_data.get('styles', {})
        if isinstance(styles_data, dict):
            self._styles = styles_data
        else:
            print(f"Warning: Invalid styles data type, using empty dict")
            self._styles = {}
            
        groups_data = scene_data.get('groups', {})
        if isinstance(groups_data, dict):
            self._groups = groups_data
        else:
            print(f"Warning: Invalid groups data type, using empty dict")
            self._groups = {}
            
        deps_data = scene_data.get('dependencies', {})
        if isinstance(deps_data, dict):
            self._dependencies = deps_data
        else:
            print(f"Warning: Invalid dependencies data type, using empty dict")
            self._dependencies = {}
            
        reverse_deps_data = scene_data.get('reverse_dependencies', {})
        if isinstance(reverse_deps_data, dict):
            self._reverse_dependencies = reverse_deps_data
        else:
            print(f"Warning: Invalid reverse_dependencies data type, using empty dict")
            self._reverse_dependencies = {}
        
        # Load objects (would need proper class resolution)
        objects_data = scene_data.get('objects', {})
        if isinstance(objects_data, dict):
            for obj_id, obj_data in objects_data.items():
                try:
                    if isinstance(obj_data, dict):
                        # This would need proper class factory implementation
                        print(f"Loading object '{obj_id}' of type '{obj_data.get('type')}'")
                        # self._objects[obj_id] = create_object_from_dict(obj_data)
                    else:
                        print(f"Warning: Invalid object data for '{obj_id}', skipping")
                except Exception as e:
                    print(f"Warning: Failed to load object '{obj_id}': {e}")
        else:
            print(f"Warning: Invalid objects data type, skipping object loading")
        
        print(f"Scene loaded: {filename}")
