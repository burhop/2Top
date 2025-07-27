# Graphics Backend Interface Design Document

## Overview

This document defines a neutral interface for a 2D graphics backend to support visualization of implicit curves and fields. The backend is intended to be used in a variety of rendering environments including ThreeJS in a web context or native applications (e.g. PyQt, OpenGL). The interface enables higher-level software to access all data needed to draw objects and fields without committing to any specific rendering library or transport mechanism.

Endpoints and transmission layers (e.g., Flask API routes or WebSocket handlers) will be addressed separately. The current goal is to create a clean, backend-neutral contract for querying geometry, field data, and drawing attributes.

## Core Concepts

- **Field**: A scalar function defined over a 2D region. May represent signed distance, potential, fill factor, etc.
- **Curve**: A 1D implicit object embedded in 2D space. Can be trimmed, composite, or standalone.
- **Renderable Object**: Any object (curve, field, annotation) that can be visualized.

## Primary Interface: `GraphicsBackendInterface`

### Interface Methods

#### `get_bounding_box()`

```python
def get_bounding_box() -> Tuple[Vec2, Vec2]:
```

**Purpose:** Defines the full drawing region in world coordinates.

**Returns:** `((min_x, min_y), (max_x, max_y))`

---

#### `get_curve_paths()`

```python
def get_curve_paths(resolution: int = 256, tolerance: float = 1e-3) -> List[Dict]:
```

**Purpose:** Returns drawable representations of implicit curves.

**Each dict includes:**

- `points`: `List[Vec2]` — Polyline approximation of the curve.
- `color`: `Color` — Stroke color (hex or RGBA).
- `line_width`: `float` — Optional.
- `label`: `str` — Optional name/ID.
- `style`: `Dict` — Optional style metadata.

---

#### `get_field_data()`

```python
def get_field_data(resolution: Tuple[int, int] = (256, 256), bounds: Optional[Tuple[Vec2, Vec2]] = None) -> Dict:
```

**Purpose:** Retrieves a scalar field (e.g., signed distance) sampled on a grid.

**Returns:**

- `extent`: `((x0, y0), (x1, y1))` — World-space bounds.
- `values`: `List[List[float]]` — 2D array of samples.
- `colormap`: `str` — e.g. 'viridis', 'plasma'.
- `opacity`: `float` — Transparency.
- `level_sets`: `List[float]` — Optional isovalues to be contoured.
- `render_mode`: `str` — Optional, e.g. 'heatmap', 'contours'.

---

#### `get_intersections()`

```python
def get_intersections() -> List[Dict]:
```

**Purpose:** Return locations where curves intersect (for highlighting or editing).

**Each dict includes:**

- `position`: `Vec2`
- `curve_ids`: `List[str]`
- `style`: `Dict` — Optional visual style.

---

#### `get_text_annotations()`

```python
def get_text_annotations() -> List[Dict]:
```

**Purpose:** Textual labels, debug output, or IDs.

**Each dict includes:**

- `text`: `str`
- `position`: `Vec2`
- `size`: `float`
- `color`: `Color`
- `align`: `str` — 'center', 'left', 'right'

---

#### `get_metadata()`

```python
def get_metadata() -> Dict[str, Any]:
```

**Purpose:** Passes general-purpose information to guide rendering.

**Keys may include:**

- `background_color`: `Color`
- `units`: `str` — 'mm', 'cm', etc.
- `zoom_hint`: `float`
- `default_line_width`: `float`
- `max_field_resolution`: `int`
- `default_curve_tolerance`: `float`
- `adaptive_sampling`: `bool`

---

## Dynamic and Interactive Use Cases

To support sliders, parameter drags, and real-time animation, the frontend should be able to update equations and parameters quickly, with minimal server involvement. We support this by allowing:

### Client-Side Evaluation

- Equations are passed as strings (e.g. `x^2 + y^2 - r^2`) and evaluated using `math.js` in the browser.
- Parameters (e.g. `{r: 2.0}`) are applied at runtime.
- Curve and field data are regenerated locally in response to UI updates.
- Curve extraction is performed by our own **marching squares implementation** in JavaScript.

### Expected Frontend Responsibilities

The frontend, implemented using ThreeJS, math.js, and our marching squares code, should:

- Parse and evaluate scalar field equations using math.js.
- Render curves as polyline paths extracted from fields using marching squares.
- Display fields as colored surfaces or contour lines using ThreeJS.
- Animate curves and fields by updating parameter bindings in real time.
- Use efficient grid sampling and bounding-box culling to optimize redraw performance.
- Handle user interactions such as parameter sliders, dragging, and toggling object visibility.
- Dispatch and receive structured messages via Model Context Protocol (MCP).

### Server-Side Responsibilities

The backend is still essential for managing object state, metadata, and complex or expensive computations.

### Required Backend Calls:

#### 1. `POST /object`

Create a new curve, field, or composite object.

#### 2. `PUT /object/:id`

Update equation, parameters, or style for an object.

#### 3. `GET /object/:id`

Retrieve the full state of an object (useful for reconnection or collaborative editing).

#### 4. `DELETE /object/:id`

Remove an object from the scene.

#### 5. `POST /intersections`

Compute intersections between two or more objects, returning points and related metadata.

#### 6. `POST /evaluate`

(Optional) Remote evaluation of an equation on a grid. Used for fallback or heavy math not suitable for client-side execution.

#### 7. `GET /scene/save` and `GET /scene/load`

Persist and reload complete scenes.

---

## AI Agent Support via Model Context Protocol (MCP)

To support an intelligent agent embedded in the frontend, the system must expose a well-typed, AI-readable interface based on the Model Context Protocol. The agent can issue JSON-formatted commands to inspect, create, or modify scene objects.

### Supported MCP Commands

| Command              | Description                                     |
| -------------------- | ----------------------------------------------- |
| `create_object`      | Add new object with type, equation, style       |
| `update_parameters`  | Modify equation parameters (e.g., radius)       |
| `set_style`          | Set visual attributes (e.g., color, line width) |
| `delete_object`      | Remove object from scene                        |
| `describe_object`    | Get full metadata for an object                 |
| `group_objects`      | Combine objects into composite or area group    |
| `set_field_strategy` | Assign field computation method                 |
| `set_view`           | Change viewport or zoom bounds                  |

### Example Command (MCP JSON)

```json
{
  "command": "update_parameters",
  "id": "curve_3",
  "parameters": {"r": 3.5}
}
```

### MCP Dispatch

Frontend should implement:

```js
function dispatchMCP(command: object): object;
```

This invokes the controller, updates internal state, and triggers re-rendering.

---

### WebSocket for Synchronization (Optional for Phase 2)

Once MCP is working in the frontend, a WebSocket channel may be added to:

- Notify the client of server-side changes to geometry or parameters.
- Broadcast delta messages when multiple agents or users modify the scene.

#### Example WebSocket Message

```json
{
  "event": "object_updated",
  "id": "curve_3",
  "object": {
    "equation": "x^2 + y^2 - r^2",
    "parameters": {"r": 3.5},
    "style": {"color": "#ff0000"}
  }
}
```

Clients should listen for these messages and update only the affected objects. This avoids needing to re-poll or reload the full scene.

---

## ThreeJS Compatibility Notes

To render fields and curves in ThreeJS, the following data will be consumed:

- **Curves** → Converted to `THREE.Line` or `THREE.LineSegments`.
- **Field data** → Interpreted as `THREE.PlaneGeometry` + texture (heatmap), or polygonal `THREE.Mesh` generated from marching squares.
- **Intersections** → `THREE.Points` or sphere meshes.
- **Text** → External overlay or WebGL-based text (e.g. troika-text).

All curve evaluation for animation or UI parameter adjustment is intended to happen client-side via `math.js`, with marching squares used to extract 0-level contours in real time. The server provides object registry, structure, and assistance with computationally expensive operations.

---

## Next Steps

- Define `Field` and `Curve` object types that implement this interface.
- Implement default renderers in Python (matplotlib) and JavaScript (ThreeJS).
- Build Flask endpoints that return this data in JSON form.
- Prototype viewer consuming this data and rendering with ThreeJS.
- Implement MCP command dispatcher.
- Add optional WebSocket channel for real-time update notifications.

---

> This interface is designed to support fast iteration, minimal latency, and easy integration with UI-based parameter editing, real-time animation, and AI-based control.

