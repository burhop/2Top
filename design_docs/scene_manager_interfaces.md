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

#### `render_animation(filename: str, frames: int, animate_fn: Callable[[int], None], resolution: Tuple[int, int]) -> None`
Generates a GIF animation by rendering the scene over multiple frames.

#### `handle_mcp_command(command: Dict) -> Dict`
Dispatches a Model Context Protocol (MCP) command and returns the result.

---

## 2. Required Methods on Geometry and Field Classes

To support bounding box queries and serialization, the following methods must be implemented by all renderable objects.

### `get_bounds() -> Tuple[Tuple[float, float], Tuple[float, float]]`
Returns the axis-aligned bounding box for the object.

### `to_dict() -> Dict`
Returns a serializable representation of the object.

### `from_dict(data: Dict) -> Object`
Reconstructs an object from its dictionary form.

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

---

## 5. WebSocket Update Format (Optional)

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

## 6. Compatibility and Integration

- Fully compatible with the `GraphicsBackendInterface` (`get_curve_paths`, `get_field_data`, etc.).
- Compatible with `ImplicitCurve`, `Field`, `CompositeCurve`, `AreaRegion` class hierarchies.
- Designed to be extensible with style dictionaries, animation callbacks, and AI-agent commands.

---

## 7. Next Steps for Implementation

- Implement `SceneManager` and supporting methods.
- Add `get_bounds()`, `to_dict()`, `from_dict()` to geometry and field classes.
- Build serialization logic.
- Add WebSocket hooks for real-time collaboration.
- Tie into MCP command dispatch and ThreeJS renderer integration.

---

This contract serves as the blueprint for implementing the runtime and persistence layer for implicit 2D sketch-based design tools.
