# Scene Manager Interface Specification (Markdown)

This document defines the **contract-level API** and interface requirements for a `SceneManager` and related components in a 2D implicit sketching system. These interfaces are designed to be implemented in Python and interoperate with the modules defined in `graphics_backend_interface.md` and `implicit_geometry_design.md`.

---

## Overview

The `SceneManager` is responsible for:
- Managing all geometric and field objects in a scene.
- Providing persistence (save/load).
- Supporting grouping, styling, and querying by region.
- Rendering and animation.
- Interfacing with the MCP agent protocol.

---

## 1. `SceneManager` Interface

### Methods

#### `__init__()`
Initializes the scene manager with empty object, style, and group registries.

#### `save_scene(filename: str) -> None`
Persist the scene to disk in `.json` or `.py` format.

#### `load_scene(filename: str) -> None`
Load a scene file from disk and restore all objects.

#### `add_object(obj_id: str, obj: Union[ImplicitCurve, CompositeCurve, AreaRegion, BaseField], style: Optional[Dict] = None) -> None`
Adds a named object to the scene.

#### `remove_object(obj_id: str) -> None`
Removes an object from the scene by ID.

#### `get_object(obj_id: str) -> Any`
Returns the object associated with the ID.

#### `list_objects() -> List[str]`
Returns a list of all object IDs currently in the scene.

#### `objects_in_bbox(bbox: Tuple[Tuple[float, float], Tuple[float, float]]) -> List[str]`
Returns all object IDs whose geometry intersects a bounding box.

#### `set_style(obj_id: str, style: Dict) -> None`
Sets a style dictionary for an object.

#### `get_style(obj_id: str) -> Dict`
Returns the style dictionary associated with an object.

#### `set_group(group_id: str, object_ids: List[str]) -> None`
Assigns a set of object IDs to a named group.

#### `update_group_style(group_id: str, style: Dict) -> None`
Updates the visual style of all objects in a group.

#### `render_image(filename: str, resolution: Tuple[int, int], bbox: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None) -> None`
Renders the current scene to an image file (e.g., `.png`).

#### `render_animation(filename: str, frames: int, animate_fn: Callable[[int], None], resolution: Tuple[int, int], cache_frames: bool = True) -> None`
Generates a GIF animation by rendering the scene over multiple frames. If cache_frames is True, saves individual frames for faster replay.

#### `create_parameter_animation(obj_id: str, parameter: str, values: List[Any], filename: str, resolution: Tuple[int, int], fps: int = 10, cache_frames: bool = True) -> None`
Creates an animation by cycling through parameter values for a specific object. Automatically handles downstream object updates and frame caching.

#### `create_multi_parameter_animation(animations: List[Dict], filename: str, resolution: Tuple[int, int], fps: int = 10, cache_frames: bool = True) -> None`
Creates complex animations with multiple objects and parameters changing simultaneously. Each animation dict contains: {'obj_id': str, 'parameter': str, 'values': List[Any]}.

#### `replay_cached_animation(cache_id: str, filename: str, fps: int = 10) -> None`
Replays a previously cached animation at specified frame rate without recalculating.

#### `clear_animation_cache(cache_id: Optional[str] = None) -> None`
Clears cached animation frames. If cache_id is None, clears all caches.

#### `get_animation_cache_info() -> Dict[str, Dict]`
Returns information about cached animations including frame counts, file sizes, and creation times.

#### `handle_mcp_command(command: Dict) -> Dict`
Dispatches a Model Context Protocol (MCP) command and returns the result.

#### `update_parameter(obj_id: str, parameter: str, value: Any, update_dependents: bool = True) -> None`
Updates a parameter on an object and optionally propagates changes to dependent objects.

#### `get_parameter(obj_id: str, parameter: str) -> Any`
Retrieves the current value of a parameter from an object.

#### `list_parameters(obj_id: str) -> List[str]`
Returns a list of all animatable parameters for an object.

#### `register_dependency(dependent_id: str, source_id: str, update_fn: Callable) -> None`
Registers a dependency relationship where changes to source_id trigger updates to dependent_id.

#### `get_dependencies(obj_id: str) -> Dict[str, List[str]]`
Returns dependency relationships for an object (both as source and dependent).

---

## 2. Required Methods on Geometry and Field Classes

To support bounding box queries, serialization, and parameter animation, the following methods must be implemented by all renderable objects.

### `get_bounds() -> Tuple[Tuple[float, float], Tuple[float, float]]`
Returns the axis-aligned bounding box for the object.

### `to_dict() -> Dict`
Returns a serializable representation of the object.

### `from_dict(data: Dict) -> Object`
Reconstructs an object from its dictionary form.

### `get_parameters() -> Dict[str, Any]`
Returns a dictionary of all animatable parameters and their current values.

### `set_parameter(name: str, value: Any) -> None`
Sets a specific parameter value and triggers any necessary internal updates.

### `get_parameter(name: str) -> Any`
Returns the current value of a specific parameter.

### `list_parameters() -> List[str]`
Returns a list of all parameter names that can be animated.

### `clone() -> Object`
Creates a deep copy of the object for frame caching purposes.

---

## 3. Serialization Format

### JSON Scene Format
```json
{
  "objects": {
    "c1": {"type": "CompositeCurve", "data": {...}, "style": {...}},
    "f1": {"type": "Field", "data": {...}, "style": {...}}
  },
  "groups": {
    "edges": ["c1", "c2"]
  }
}
```

### Python `.scene.py` Format
```python
from sketchlib import Circle, Field, SceneManager
scene = SceneManager()
scene.add_object("circle1", Circle(0, 0, 2), style={"color": "#0ff"})
scene.save("scene.json")
```

---

## 4. MCP Command Mapping

These commands map to `SceneManager` methods.

| MCP Command       | SceneManager Method         |
|------------------|-----------------------------|
| `create_object`  | `add_object()`              |
| `delete_object`  | `remove_object()`           |
| `describe_object`| `get_object()`              |
| `update_parameters` | applied to curve/field    |
| `set_style`      | `set_style()`               |
| `group_objects`  | `set_group()`               |
| `set_field_strategy` | set field on AreaRegion |
| `set_view`       | not handled by SceneManager |
| `animate_parameter` | `create_parameter_animation()` |
| `animate_multi_parameter` | `create_multi_parameter_animation()` |
| `update_parameter` | `update_parameter()` |
| `get_parameter` | `get_parameter()` |
| `cache_animation` | handled automatically |
| `replay_animation` | `replay_cached_animation()` |

---

## 5. Animation System Architecture

### Parameter Animation Workflow
1. **Parameter Discovery**: Use `list_parameters()` to identify animatable properties
2. **Value Generation**: Create parameter value sequences (linear, exponential, custom)
3. **Frame Generation**: For each value, update parameter and render frame
4. **Dependency Updates**: Automatically propagate changes to dependent objects
5. **Frame Caching**: Store rendered frames for fast replay
6. **Animation Export**: Compile frames into GIF/MP4 with specified FPS

### Caching Strategy
- **Frame Cache**: Store individual rendered frames as PNG files
- **Parameter Cache**: Store object states for each parameter value
- **Dependency Cache**: Cache computed dependent object updates
- **Smart Invalidation**: Only recompute frames when parameters actually change

### Performance Optimizations
- **Lazy Evaluation**: Only compute frames when needed
- **Parallel Rendering**: Render multiple frames simultaneously when possible
- **Memory Management**: Automatic cache cleanup based on size/age limits
- **Progressive Loading**: Stream animation playback while computing remaining frames

### Animation Types Supported
- **Single Parameter**: Animate one parameter of one object
- **Multi-Parameter**: Animate multiple parameters of one object
- **Multi-Object**: Animate parameters across multiple objects
- **Synchronized**: Keep multiple animations in sync
- **Composite**: Combine multiple animation sequences

---

## 6. WebSocket Update Format (Optional)

```json
{
  "event": "object_updated",
  "id": "curve_3",
  "object": {
    "equation": "x^2 + y^2 - r^2",
    "parameters": {"r": 3.5},
    "style": {"color": "#f00"}
  }
}
```

---

## 7. Compatibility and Integration

- Fully compatible with the `GraphicsBackendInterface` (`get_curve_paths`, `get_field_data`, etc.).
- Compatible with `ImplicitCurve`, `Field`, `CompositeCurve`, `AreaRegion` class hierarchies.
- Designed to be extensible with style dictionaries, animation callbacks, and AI-agent commands.

---

## 8. Next Steps for Implementation

- Implement `SceneManager` and supporting methods.
- Add `get_bounds()`, `to_dict()`, `from_dict()` to geometry and field classes.
- Build serialization logic.
- Add WebSocket hooks for real-time collaboration.
- Tie into MCP command dispatch and ThreeJS renderer integration.
- Implement parameter animation system with frame caching.
- Add dependency tracking for automatic object updates.
- Create animation export utilities (GIF, MP4, frame sequences).
- Build animation timeline UI components.
- Add performance monitoring and cache management tools.

---

This contract serves as the blueprint for implementing the runtime and persistence layer for implicit 2D sketch-based design tools.
