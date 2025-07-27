# System Integration Guide: 2D Implicit Sketching System

## Purpose and Scope

The 2D Implicit Sketching System is an interactive design platform for
creating and manipulating shapes defined by implicit equations (curves)
and associated scalar fields. It combines a powerful **Python backend**
for geometric computations with a **web-based frontend UI** for
visualization and editing. The goal is to allow intuitive sketching of
implicit curves (like circles, splines, blends, etc.) and fields (like
distance or noise maps) with real-time feedback, while supporting
advanced operations such as boolean combinations, offsets, and dynamic
updates via an AI assistant. The system's scope spans **geometric object
modeling**, **rendering data generation**, **scene management and
persistence**, **user interface controls**, and an **AI agent protocol**
for high-level control. In essence, the system lets users or AI agents
create implicit geometry, manipulate it interactively, and visualize
results immediately.

## Architecture Overview

At a high level, the system is composed of five core components that
interoperate closely:

- **Implicit Geometry Module (Python)** -- The library of geometric
  primitives and operations for 2D implicit curves and regions.
- **Graphics Backend Interface (Python)** -- A neutral API for
  extracting renderable representations of geometry and fields (e.g.
  polyline paths, field grids) for any rendering engine.
- **Scene Manager (Python)** -- The central runtime that manages all
  objects in a scene, handles grouping, styling, serialization
  (save/load), and delegates rendering queries and AI commands.
- **User Interface (JavaScript/Web)** -- The client-side application
  (using ThreeJS, math.js, etc.) that displays the scene, provides
  editing tools (sliders, handles, menus), and sends/receives commands
  to the backend.
- **Model Context Protocol (MCP)** -- A structured JSON command protocol
  used by the UI's AI panel (or other agents) to create, modify, and
  query objects in the scene in a controlled, semantic way.

These components form a **client-server model**: the Scene Manager and
associated backend modules run on the server (or local Python
environment), while the UI runs in the browser. They communicate via
defined APIs and the MCP messaging system. The **implicit geometry
module** is used by the scene manager for all mathematical operations.
The **graphics interface** defines how the scene manager provides
geometry to the UI (or any renderer). The **UI** invokes backend
functionality through HTTP or WebSocket endpoints (e.g. creating an
object or saving a scene) and also performs client-side computations for
responsiveness. The **MCP** ensures that both user-initiated actions and
AI-driven commands use the same interface to the system's functionality,
making the system uniformly controllable by humans or AI.

Below, we detail each core module, their responsibilities, and how they
integrate with one another. We also note any missing APIs or extensions
needed to fulfill certain use cases (like interactive offset editing
from the UI). Throughout, we assume the reader has deep technical
familiarity with Python and web development, focusing on integration
points rather than basic implementations.

## Implicit Geometry Module

**Purpose:** The Implicit Geometry module provides the mathematical
foundation of the system. It defines classes for implicit curves and
regions, and implements operations on them. All curves are represented
by equations *f(x,y) = 0* internally, enabling exact or numerical
computation of geometric properties. This module allows creation of
primitive shapes (circles, conics, polynomial curves), composite curves,
and area regions, and supports operations like curve **intersection**,
**blending**, **offsetting**, and **boolean combinations** (union,
difference, etc.) on these shapes. For example, it provides functions
`intersect(curve1, curve2)` to find intersection points and
`blend(curve1, curve2)` to smoothly merge shapes. The module's
`offset(curve, distance)` function produces a new implicit curve offset
by a given distance (useful for creating parallel curves or
morphologies). Similarly, set operations like
union/intersection/difference return new implicit curves representing
those regions.

**Structure:** The module defines a class hierarchy where
`ImplicitCurve` is the base class, and specific curve types (conic
sections, superellipses, composite curves, etc.) subclass it. Each curve
class implements common methods such as `evaluate(x,y)` (compute the
implicit function's value), `gradient(x,y)` (for normals or curvature),
and `plot()` for simple visualization. It also includes specialized
classes: - **TrimmedImplicitCurve:** A curve with a restricted domain
(useful for open curve segments or partial loops) which still behaves
like a full implicit curve in operations. - **CompositeCurve:** A
sequence of curve segments joined end-to-end, which together behave as
one continuous curve (useful for complex piecewise shapes). -
**AreaRegion:** Represents a 2D region bounded by one or more closed
curves (outer boundary and optional holes) and supports operations like
point containment, area calculation, and conversion to fields. - **Field
Strategies and Fields:** Although primarily focused on curves, the
geometry module intersects with field generation. For instance, an
AreaRegion can produce a scalar field representation (e.g., a **signed
distance field**) of the shape via a strategy pattern (e.g.,
`SignedDistanceStrategy`) to support things like offset shading or
fills. Several field classes (e.g., `SignedDistanceField`, `NoiseField`,
`ImageField`) are defined to represent continuous scalar fields, which
the UI can visualize.

**Integration:** The Scene Manager uses this module to instantiate
objects for the scene. When an MCP command requests a new object (say a
circle or a blended curve), the scene manager will call the appropriate
constructor from this geometry module (e.g., `Circle(...)` or a boolean
combination function) to create it. Similarly, when the UI or AI
requests an operation like *offsetting a curve*, the backend will use
`implicit_geometry.offset()` to compute the new implicit curve and then
add it as a new object to the scene. The geometry objects are also
required to support **serialization**: the Scene Manager will call
`to_dict()` on each object for saving, and use class-specific
`from_dict()` to reconstruct objects on loading.

*Developer Note:* **Implementing Serialization:** Each geometric class
(including composite ones) must implement a `from_dict` that mirrors its
`to_dict` output. For example, a `CompositeCurve` should serialize its
list of segments (likely as a list of segment dictionaries).
Accordingly, `CompositeCurve.from_dict(data)` should read the list of
segment dicts from `data["segments"]`, call the appropriate
`ImplicitCurve.from_dict` for each (since segments could be
`TrimmedImplicitCurve` or other types), and then assemble and return a
new `CompositeCurve` instance. Ensuring all nested objects are
reconstructed is crucial for scene loading. The **Scene Manager** will
rely on these methods to handle JSON scene files, so developers must
implement them for all new object types.

**Missing APIs / Future Enhancements:** The implicit geometry module
covers most planned operations, but a few extensions are noted: -
*Interactive Offset Support:* The current `offset()` function returns a
final offset curve for a given distance, but the UI's "Offset Mode"
envisions a live preview where a user drags to adjust the offset
distance continuously. There is no explicit API yet for "live" offset
updates (the design assumes the frontend can handle this by sampling a
distance field). In the future, a method to directly produce a
**parametric offset field** or to evaluate offset curves at interactive
rates could be added. For example, an `ImplicitCurve.to_field()` that
returns a SignedDistanceField for the curve would allow the UI to render
isocontours for offsets on the fly. Currently, such functionality might
be achieved by creating an AreaRegion from a closed curve and using a
`SignedDistanceStrategy` to get a field, but a more direct API could
simplify UI integration. - *Enhanced Curve Constructors:* The system
might benefit from convenience methods (e.g., creating a circle by
center and radius directly, or a composite curve from a list of points).
These can be implemented as needed but are not strictly required by the
current design. - *Symbolic Manipulation:* While the module supports
symbolic curves (via sympy expressions), more APIs to simplify or
analyze expressions (beyond the provided `simplify()` or `substitute()`)
could be added if AI developers need deeper algebraic insight into
curves.

## Graphics Backend Interface

**Purpose:** The Graphics Backend Interface defines how geometric and
field data is extracted for visualization. It acts as a **contract
between the backend and any rendering frontends**. This interface
ensures the UI (or other renderers) can obtain all necessary drawing
primitives from the scene without knowing the details of the geometry
library. The design is backend-neutral: it could be implemented for a
ThreeJS web client, a Qt desktop app, or even a headless image renderer.
The interface provides methods to query drawable representations of the
scene's content.

**Core API Methods:** Key methods in the `GraphicsBackendInterface`
include: - `get_bounding_box()` -- Returns the overall scene extents in
world coordinates, as a pair of min and max points. -
`get_curve_paths(resolution=256, tolerance=1e-3)` -- Returns a list of
path definitions for each implicit curve in the scene. Each path is
typically a polyline approximation of the curve, given as a list of
points, along with styling info like stroke color, line width, and an
optional label. The `resolution` and `tolerance` parameters control the
fineness of the approximation (e.g., sampling density or simplification
tolerance). - `get_field_data(resolution=(256,256), bounds=None)` --
Samples the scalar field objects in the scene on a grid and returns the
values plus metadata. The result includes the world-space extent of the
sampling, the 2D array of values, a colormap name, opacity, and optional
contour level sets. This allows the UI to render heatmaps or contour
lines for fields. - `get_intersections()` -- Computes intersections
among curves (if any) and returns their coordinates and related curve
IDs. This helps the UI highlight intersection points (useful for
snapping or for user reference). - `get_text_annotations()` -- Returns
any textual labels or annotations (e.g., names of objects, debug info)
with positions and style. - `get_metadata()` -- Provides miscellaneous
scene-wide info and defaults, such as background color, unit system (for
display scales), default styling parameters, or hints for rendering
(e.g., a zoom level suggestion, max field resolution).

The **implementation** of this interface on the backend will typically
involve iterating over all objects in the Scene Manager's registry and
converting each to a drawable form. For example, `get_curve_paths()`
will go through each curve object (explicit or composite) and sample it
(possibly using marching squares or analytical points) to produce a
polyline. Style information might come from each object's stored style
(color, line width, etc.) as set via the scene manager.

**Integration:** In practice, the Scene Manager (or a related controller
class) will implement these interface methods. For instance, a
`SceneManager.get_curve_paths()` can gather all curves via its
`list_objects()` and for each object that is an `ImplicitCurve` or
`CompositeCurve`, retrieve or compute its points and style. This
decoupling means the UI does not call geometry functions directly;
instead it requests data through a consistent interface. The system is
designed so that the **frontend can either poll these methods via HTTP**
(e.g., a REST API endpoint corresponds to each method) **or compute
locally** if the data and expressions are available. In our design, to
minimize latency, the **web UI often performs these computations
client-side** using the same math definitions, as noted below in the UI
section. But the interface is still crucial for cases where the client
is not doing its own math, or for non-web renderers. It's also used when
saving out images or animations on the backend (e.g., a server-side
render to PNG would use `get_curve_paths` to feed into a drawing
library).

**Implementation Constraints (Renderer Developers):** If you are
implementing a new renderer or backend for this interface, adhere to the
following guidelines:

- *Accuracy vs Performance:* Respect the `resolution` and `tolerance`
  arguments. Do not hard-code sampling density; use these parameters to
  balance detail and performance. For example, a high resolution should
  produce more points in `get_curve_paths()` than a low one, and a
  smaller tolerance should yield less simplification.
- *Metadata:* Pay attention to values provided by `get_metadata()`. For
  instance, `max_field_resolution` may tell you not to sample fields at
  an arbitrarily high resolution to avoid slowdowns. Similarly, use
  `default_curve_tolerance` if provided for polyline generation to
  ensure consistent fidelity across renderers.
- *Statelessness:* The interface methods should be **pure functions of
  the current scene state** -- they shouldn't alter the scene or
  maintain global state between calls. A renderer should be able to call
  them in any order to retrieve data. When writing a renderer, treat the
  output as read-only snapshots of the scene.
- *Consistency:* Ensure that styling (colors, line widths, etc.) is
  applied consistently. Use the style dictionaries provided by the Scene
  Manager (`get_style(obj_id)`) or embedded in the objects. If a style
  key is missing, fall back to defaults (which might be provided in
  metadata or known in design).
- *Extensibility:* The interface is neutral; you can extend it if needed
  for a specific platform (for example, a method to get **default style
  presets** or markers). The UI specification suggested an extension
  like `get_default_styles()` to retrieve user-defined style preferences
  -- currently not in the interface, but it could be added if the client
  needs to load default colors or patterns. Coordinate any such changes
  with the team to keep the contract consistent.

**Missing APIs / Gaps:** The defined interface covers geometry and field
retrieval well. Some potential gaps and future needs include: - There is
currently no direct method to query **object dependencies or
relationships** (e.g., which field is derived from which curve). The UI
spec mentioned a possible `get_dependencies(object_id)`. Implementing
this might require the Scene Manager to track links (like a field that
was generated from a particular region). - No explicit call for
**snapping guidance** beyond `get_intersections()`. The UI can use
`get_intersections()` results for snap-to-point behavior, but if more
sophisticated guides (like perpendicular or tangent snaps) are needed,
the interface might need additional queries (not yet specified). -
**Default style queries** as mentioned above (`get_default_styles`) are
not implemented. For now, style defaults might be hard-coded on the
client or stored in a config file. If a shared style palette is desired
across sessions, an API extension could provide it.

## Scene Manager

**Purpose:** The Scene Manager is the **orchestrator** of the entire
application's backend. It maintains the registry of all objects (curves,
composite shapes, fields, regions) in the current scene, along with
their properties like styles and grouping. It provides high-level
operations such as saving/loading the scene, handling grouping and
styling changes, and interfacing with external commands. In effect, the
Scene Manager is the single source of truth for the scene's state. As a
controller, it enforces consistency (for example, ensuring unique object
IDs, managing deletion such that no references remain, etc.) and
mediates between the UI/AI requests and the lower-level geometry or
rendering logic.

**Core Responsibilities and API:** The Scene Manager's interface (likely
exposed as methods and also via MCP commands) includes: - **Object
Management:** `add_object(obj_id, obj, style=None)` to add a new object
to the scene under a given identifier, `remove_object(obj_id)` to delete
an object, `get_object(obj_id)` to retrieve the actual object, and
`list_objects()` to list all IDs. These allow the UI or AI to create and
manipulate objects in the scene. The objects can be of any supported
type (ImplicitCurve, CompositeCurve, AreaRegion, or Field). - **Grouping
and Styling:** `set_group(group_id, [obj_ids])` to define named groups
of objects, and `update_group_style(group_id, style)` to apply style
changes to all in the group. Individually, `set_style(obj_id, style)`
and `get_style(obj_id)` let you change or query the visual style of a
single object. Groups help in applying transformations or style changes
to multiple objects at once (e.g., treating a set of curves as one
logical shape). - **Persistence:** `save_scene(filename)` and
`load_scene(filename)` to save the entire scene to disk (in either a
JSON format or a Python script format). The JSON format is a nested
dictionary of object data and group definitions, whereas the `.scene.py`
format writes actual Python code to recreate the scene (for convenience
and versioning). The Scene Manager uses each object's `to_dict()` during
save, and expects corresponding `from_dict()` methods to rebuild objects
on load. - **Rendering Support:** The Scene Manager either implements or
works closely with the Graphics Backend Interface. For example, it might
have a `render_image(filename, resolution, bbox=None)` method to produce
an image snapshot (using an off-screen renderer or by delegating to
something like Matplotlib or PIL in Python). Similarly,
`render_animation(...)` can produce an animation by updating the scene
over frames using a provided callback. These high-level methods likely
utilize `get_curve_paths()` and related calls internally to gather
drawing data. - **MCP Command Handling:** A critical function is
`handle_mcp_command(command: Dict) -> Dict` which takes a JSON-like
command (from the UI or AI) and executes the appropriate scene
operation. The Scene Manager essentially acts as the **dispatch center**
for MCP -- for example, a command
`{"command": "create_object", "type": "Circle", ...}` would be processed
by creating a new circle via the geometry module and adding it via
`add_object`. The result (success or any requested data) is returned as
a JSON-ready dictionary. The mapping of MCP commands to SceneManager
methods is defined by the integration design. For instance,
`create_object` maps to `add_object()`, `delete_object` to
`remove_object()`, `describe_object` to `get_object()` (with
serialization), `update_parameters` to updating an object's parameters
(which might involve calling a method on the geometry object or
replacing it), `set_style` to `set_style()`, `group_objects` to
`set_group()`, and so on. (See **MCP section** below for more details.)

**Integration with Other Modules:** The Scene Manager sits at the
center: - It holds references to all geometry objects (instances of
classes from the Implicit Geometry module). When the UI needs to modify
a curve's equation or a field's parameter, the Scene Manager will locate
the object and apply the change (either by directly setting properties
or by creating a new object to replace it, depending on whether the
geometry objects are immutable). - It uses the Graphics Backend
Interface to serve rendering data. In some implementations, the Scene
Manager class itself might implement the interface methods
(`get_curve_paths`, etc.), since it knows about all objects and their
styles. Alternatively, it could compose with a separate
GraphicsInterface class, feeding it the list of objects. In either case,
those interface calls iterate over scene objects and use each object's
methods (like `evaluate` or specialized sampling routines) to generate
output. The Scene Manager must ensure that every object type in the
scene can respond to the needed queries (hence the requirement that all
objects implement `get_bounds()`, `to_dict()`, and `from_dict()`, and
presumably any other method needed for rendering like maybe a custom
`as_polyline()` for curves if implemented). - It communicates with the
**UI** and **AI** through the MCP and possibly direct API endpoints. For
example, a UI "Save" action might call
`sceneManager.save_scene("scene.json")` through a Flask route, whereas
an AI agent asking for object details would send an MCP
`describe_object` command and get the data from `get_object` in return.

**Missing APIs / Enhancements:** While the Scene Manager covers most
needed functionality, the UI specification and overall use cases suggest
some additional APIs that are not yet in place: - **Dependency
Queries:** As noted, there is no built-in way to ask the scene manager
"what does object X depend on?". For example, if object Y is a blend of
A and B, or a field derived from curve C, the UI might want to highlight
those relationships. A method like `get_dependencies(obj_id)` was
suggested. Implementing this would require tracking creation
relationships in the scene (which could be done by storing references or
IDs of source objects in composite objects or fields). AI developers
might consider maintaining a graph of object dependencies within Scene
Manager to support this. - **Query by Type or Attribute:** It might be
useful to have methods like `list_objects_by_type(type_name)` (e.g., all
"Field" objects) or searching by name/attribute. Currently, the UI
likely filters objects by type on the client side since it knows each
object's type from the registry. But adding a backend query could be
convenient. - **Field Listing by Source:** Another UI suggestion was
`list_fields_by_source(curve_id)`, meaning "give me all field objects
that were generated from a given curve or region". This again ties to
dependency tracking. Without an explicit API, an AI could still infer
this if the naming conventions or data of fields store a reference to
the source (for instance, a distance field might include the source
curve's ID in its data). A formal API would be cleaner. - **Bulk
Operations:** Currently, grouping is supported, but there's no
single-call duplicate or transform operation. For instance, a
"duplicate_object" command (to copy an object under a new ID) might be
useful. Similarly, applying a transformation (translate/rotate/scale) to
a curve might be a future extension; right now, the system doesn't
explicitly list transform operations (one would achieve it by altering
the equation or parameters). - **Offset as First-Class Operation:**
Interactive offsetting was mentioned as a UI feature. There isn't a
direct MCP command for offsetting a curve and adding the result. A
dedicated command like `offset_object` (with parameters specifying which
object and distance) could be introduced to streamline this use case.
Without it, the UI or AI would have to simulate it by computing the
offset via geometry module and then using `create_object`. Developers
should be prepared to implement such a command if needed, making use of
the geometry module's `offset()` and ensuring the new curve is
integrated into the scene. - **View/Camera control:** The MCP command
set includes `set_view`, but as noted in the design, this is not handled
by the backend (the front-end takes care of view
adjustments)[\[1\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=match%20at%20L964%20by%20SceneManager,end.%20Our%20strategy).
So the Scene Manager currently can ignore or pass through view-related
commands. If in the future we had multiple clients or a need to persist
the view state, an API to store and retrieve view parameters could be
added.

*Developer Notes:* - **Implementing Parameter Updates:** The
`update_parameters` MCP command implies changing an existing object's
defining equation or parameters (e.g., radius of a circle). There isn't
a fixed `SceneManager.update_object(obj_id, params)` method specified,
but the MCP handling will need to be coded. Likely, it should fetch the
object, apply the parameter changes (which might involve updating an
attribute or calling a method on the object), and then possibly
recompute any cached data or update bounding boxes. AI developers
implementing this should follow the patterns in similar systems: for
example, if the object is defined by a sympy expression with parameters,
substitute the new parameter values and update the object's expression.
Also consider validation -- e.g., if the parameter is invalid, raise an
error (the QA plan expects robust error handling for bad MCP input). -
**Serialization and Version Control:** The Scene Manager's save to
`.scene.py` (executable script) is a powerful feature for preserving
scenes in a human-readable/editable form. However, be cautious: loading
from a `.scene.py` means executing code, which is fine for trusted
content but could be a security risk if not handled properly. For
deployment, it might often be safer to use JSON. When implementing load,
ensure that only expected functions/classes are called (e.g., use a
restricted namespace if executing a `.scene.py`). In source control, you
would not commit arbitrary `.scene.py` files from users, but you might
include some curated example scenes or test scenes in this format for
convenience.

## User Interface Module

**Purpose:** The UI module is the client-facing part of the system -- a
rich, interactive application (expected to be web-based with
HTML5/JavaScript and WebGL) that allows users to visually engage with
the implicit geometry. It provides a canvas to display curves and
fields, and UI panels/controls to create new shapes, adjust parameters,
group objects, style them, and trigger specialized modes (like animation
or offset editing). The UI is also responsible for integrating the AI
assistant via the MCP command interface, giving users a natural language
or high-level command channel in addition to direct manipulation.

**Key Features & Components:** - **Graphics Canvas:** The central area
where curves and fields are drawn (using WebGL via ThreeJS, or an
SVG/canvas overlay). It supports pan/zoom, selection of objects, and
shows visual aids like grid lines or bounding boxes. Users can click or
drag objects; for example, dragging a point on a curve could be an
interaction to tweak the curve (if supported). - **Object Panels:** A
sidebar listing all objects categorized by type (Curves, Composite
Shapes, Regions, Fields, etc.). Each object entry can show a visibility
toggle, color swatch, name (editable), and quick action buttons (edit,
delete, style). This provides a high-level overview and management
interface for the scene. - **Context Menus and Tools:** Right-click
context menus on the canvas and on objects provide operations like
deleting, renaming, duplicating an object, exporting geometry, or
grouping. Global toolbar actions include Save/Load, Undo/Redo, an
Animation timeline toggle, and help/docs. - **AI Interaction Panel:** A
dedicated panel (e.g., on the right side) where the user can type
natural language or command queries to an AI agent. The UI sends these
requests as MCP commands (such as `create_object` or
`update_parameters`) to the backend, then interprets and reflects the
responses. This panel can be shown/hidden and is meant to augment the UI
by providing an alternative way to perform actions (e.g., "Make this
curve a bit wider"). - **Inspector and Editors:** When an object is
selected, an inspector panel shows its details -- for a curve, the
defining equation and parameters; for a field, perhaps the formula or
source object; for a composite or region, its components. Users can edit
numeric parameters via sliders (with immediate visual feedback), change
equations in a text field, or adjust styles with color pickers and
dropdowns. These controls are wired such that changes propagate to the
scene in real-time. - **Special Interaction Modes:** The UI supports
modes like **Offset Mode**, where selecting a curve and enabling offset
mode will display a live preview of offset curves. In this mode, the UI
might render a *distance field* shading around the curve and highlight a
particular offset contour (for example, an outline at a certain
distance). The user can drag an on-screen handle to change the offset
distance; as they do, the preview updates continuously. Finally, the
user can confirm to create a new curve at that offset distance or even
keep the distance field as a field object. This mode uses both the
geometry's capabilities (distance fields, offset curves) and the UI's
interactive rendering (likely utilizing the marching squares algorithm
client-side for smooth updates). - **Animation Panel:** Another mode
where users can pick an object and a parameter to animate over time
(e.g., oscillate a radius). The UI provides controls for frame count,
play/pause, etc., and likely uses the backend's `render_animation` or
does client-side frame capture to produce an output. This implies tight
sync between UI and backend for each frame if backend rendering is used,
or purely client-side animation if possible for speed. - **Persistence &
Import/Export:** The UI offers Save/Load which interacts with backend
(the UI might simply call the backend save API, or retrieve a scene
file). It might also allow exporting the canvas as an image (PNG/SVG) or
exporting specific objects (e.g., an implicit curve as an SVG path).
These features rely on either backend services (e.g. a `/scene/save`
endpoint that triggers `save_scene`) or on the client replicating the
scene data and using local conversion (the design leans on backend for
saving to ensure all data including any procedural aspects are
captured).

**Integration with Backend:** The UI communicates with the backend
primarily via the **Model Context Protocol (MCP)** and possibly some
REST endpoints. For instance: - When a user creates a new object using
the UI (say by clicking "Add Circle"), the UI will generate a unique
name (like \"BouncyCircle\" by its naming scheme) and then send a
command to the backend:
`{"command": "create_object", "type": "Circle", "id": "BouncyCircle", "parameters": {...}}`.
The Scene Manager will handle this (create the circle in geometry, add
to scene) and return a result (perhaps the full object data or a success
acknowledgment). The UI then adds the new object to its list and renders
it. In many cases, the UI might also optimistically render the object
immediately using client-side math (for speed) while waiting for
confirmation. - If a user changes a parameter via slider (e.g., radius =
5 to 6), the UI could *either* update the geometry immediately in the
browser (re-evaluate the curve's equation with the new parameter and
update the polyline mesh) *and* send an MCP `update_parameters` command
to the backend so the authoritative state is updated. The design
suggests that for real-time updates, the **evaluation is done
client-side** using math.js and marching squares, avoiding a round trip
for each slight change. The backend is updated at a lower frequency or
only when the user stops dragging, ensuring state consistency. - The UI
listens for **backend events** (likely via WebSocket). For example, if
an AI agent on the backend creates or modifies an object, the backend
can broadcast an event like
`{"event": "object_updated", "id": "...", "object": {...}}`. The UI's
MCP dispatcher will catch this and update the UI state (e.g., add the
new object to the list or refresh an object's display if parameters
changed). This ensures that AI-driven changes or multi-user
collaboration reflect on the UI without the user manually refreshing. -
The UI uses **graphics data** from the backend when needed. If the UI
were thin, it would call `get_curve_paths` and `get_field_data`
endpoints whenever it needs to draw. However, as noted, our design
pushes these calculations to the client when possible. The UI has a
built-in math engine (using math.js for expressions) and a **marching
squares** implementation in JS to extract contour lines for implicit
equations. This means the UI can recompute a curve's polyline very
quickly as a user drags a slider, without waiting for the server.
**Constraint:** The client must use the same implicit equation as the
backend to ensure consistency. The backend provides the equation string
and current parameters for each object (e.g., via `describe_object` or
initially when created), and the UI stores that. Then the UI can
evaluate f(x,y) on a grid to get the curve. The **rendering of fields**
(heatmaps or contour fills) is done similarly: the UI can sample the
field equation using the same logic. The backend's `get_field_data`
might only be called for large or precise exports, or if the field is
too complex to compute on the client (the design allows an optional
remote evaluation for heavy computations). - For **snapping** or other
advanced guides: The UI might call `get_intersections()` on the backend
to get all intersection points, then use that list to draw markers and
magnetically snap objects when they are dragged near those points.
Alternatively, the UI could compute intersections itself (since it can
sample the curves), but a precise backend calculation is likely more
reliable for this case. So snapping is a collaborative effort: the
backend identifies intersection coords, the UI enforces the snap
behavior in interactions.

**Missing APIs / UI Wish-List:** The UI spec enumerated some desired
backend extensions which the current API does not cover yet: -
`get_dependencies(object_id)` -- as discussed, to highlight what other
objects are related to a given one (for instance, if an AreaRegion's
boundary comes from certain curves, or a field is tied to a region). -
`list_fields_by_source(curve_id)` -- quickly find fields generated from
a particular curve, to help when a user deletes a curve (the UI could
warn that a field will be orphaned). - `get_default_styles()` -- to
retrieve the application's default styling (colors, line widths) or
user's saved style presets. Without this, the UI currently probably uses
a hard-coded default set, but an API would allow consistent defaults
across sessions or sharing defaults between users. - Image embedding in
scenes -- the spec mentions possibly embedding images in fill patterns.
If we allow fields that are image-based (`ImageField`), the scene save
format might need to include binary data or references. There is no API
yet to manage image assets; a future extension might allow uploading an
image and referencing it in a field or style. -
`list_parameters(object_id)` -- to query what adjustable parameters a
given object has. This can be useful for AI or UI to automatically
construct appropriate sliders or UI controls. Currently, the UI knows
parameters implicitly (e.g., a circle has "r"), but an introspective API
would make the UI more dynamic. The lack of this is not critical because
the UI is likely coded with knowledge of each object type's parameters
from the design. - No explicit API for **interactive offset
finalization** -- as noted, the UI can preview offset by itself, but
when the user decides to "save field" or "create curve at offset", the
UI must either compute and create it via an existing command. Likely it
would do: if creating an offset curve, call backend's `create_object`
with type perhaps "ImplicitCurve" or same type as original but new
equation (the equation could be something like original f(x,y) = d). It
might be tricky to generate that formula on the fly. Alternatively, if
the backend had an `offset_object` command (not currently present), the
UI could simply send that with a distance. This gap suggests a future
MCP command or SceneManager method to directly handle offset creation,
which would encapsulate the geometry.offset call and object creation. -
Minor: The UI also mentioned *UI hooks for snapping/guides using
intersections*, which is not an API but an internal UI feature --
however, to fully implement it, the UI needs timely intersection data.
As described, the backend provides `get_intersections()`, but the UI
might want this continuously as objects move. Right now, there's no push
mechanism for intersections (the UI would have to poll or recompute). An
improvement could be to have the backend push an update when new
intersections form, but that's complex to do in real-time. Instead, the
UI might just call `get_intersections()` whenever an object is dropped
or on demand.

**Developer Guidance (UI):** - The UI developers should follow a
**testable, modular design**. Keep the rendering logic separate from
state logic, so we can simulate state changes in tests (e.g., using Jest
for unit tests of name generation, parameter change handling, etc.). The
UI should treat the backend responses as authoritative and handle
partial failure gracefully (e.g., if a command fails, show an error). -
Use the naming conventions and uniqueness rules as specified (the UI
should enforce unique names on its side too). - Implement the MCP
dispatch and listener carefully. For outbound commands, format the JSON
exactly as expected by the backend (keys like `"command"`, `"id"`,
etc.). For inbound messages, update only the relevant parts of the UI
state to avoid full re-renders needlessly. For example, if an
`object_updated` event comes, update that object's data in the store and
redraw that object, rather than rebuilding the whole scene. - **Local
computations:** Follow the design decision to do quick math in the
browser. Use `math.js` to parse and evaluate expressions for fields and
curves. For generating curve geometry, use a marching squares or
adaptive sampling algorithm similar to what the backend would do. The UI
and backend should produce comparable results; test this by comparing a
backend-generated curve path with the UI's for the same object
occasionally. This ensures the logic stays in sync (differences in
precision or algorithm might occur; having the same tolerance settings
helps). - Manage performance by capping resolution where appropriate
(honor the `max_field_resolution` hint from backend metadata or
implement dynamic level-of-detail as the user zooms). - **UI Test
considerations:** Plan for integration tests where the UI is fed
simulated backend responses. For instance, after sending an MCP command
in a test, simulate the backend's reply and ensure the UI state updated
correctly (this can be done by calling the UI's MCP dispatcher function
in a test context with a fake response). This will catch issues in the
UI-backend interface contract.

In summary, the UI is a sophisticated client that mirrors much of the
system's functionality in a user-friendly way, relying on the backend
for heavy lifting and persistence, but taking on real-time interactive
tasks on its own. Ensuring a clear separation of concerns (the backend
is the authority on scene data and complex ops; the frontend is the
authority on user interaction and real-time feedback) will make the
system robust and responsive.

## Model Context Protocol (MCP)

**Purpose:** The Model Context Protocol is a JSON-based messaging schema
that allows external agents (particularly the AI assistant integrated
into the UI, but also potentially other automated scripts or network
clients) to interact with the scene in a high-level, semantic way.
Instead of calling low-level APIs or functions, an agent can send a
self-descriptive command (with a structure like
`{"command": "...", "id": "...", "parameters": { ... }}`) which the
Scene Manager will interpret and execute. MCP abstracts the operations
into a stable interface that does not require direct function calls,
making it suitable for communication over WebSockets or HTTP and for AI
to reason about possible actions.

**Supported Commands:** The core set of MCP commands and their meanings
(as defined in design) include: - `create_object` -- Create a new object
in the scene. The command typically includes a `"type"` (e.g.,
`"Circle"`, `"Blend"`, or `"Field"`), an optional `"id"` (if the agent
wants to name it; otherwise the backend may assign one or use the
UI-suggested name), and the defining parameters or equation for the
object. This maps to the Scene Manager's `add_object()` (after
constructing the object via geometry library). - `delete_object` --
Remove an object by ID, mapping to `remove_object()`. -
`describe_object` -- Query an object's details. This would result in the
object's data being returned (likely its type, current equation or
parameters, and perhaps style). It maps to `get_object()` and then the
object is serialized (using `to_dict()` internally). -
`update_parameters` -- Adjust an existing object's parameters or
equation. For instance, change the radius of a circle, or change the
polynomial coefficients of a curve. This doesn't directly map to a
single Scene Manager method (there isn't an explicit one), but the Scene
Manager's MCP handler will handle it by altering the object and possibly
returning a confirmation or updated object state. - `set_style` --
Update the style (color, line width, etc.) of an object, mapping to the
Scene Manager's `set_style()` method. - `group_objects` -- Create or
update a group with a list of object IDs. This likely calls
`set_group()` on the Scene Manager to form a composite or logical
grouping (and possibly could trigger creation of a CompositeCurve or
AreaRegion if grouping implies a new object -- the design is a bit
unclear if grouping is purely visual or also geometric). -
`set_field_strategy` -- Apply a field generation strategy to an
AreaRegion. For example, if you have a region (closed composite curve),
you could use this command to generate a Signed Distance Field for it by
specifying the strategy (the backend would then create the field object
or alter the region's internal field). - `set_view` -- Adjust the view
or camera. This command is noted, but since view is a frontend concept,
the backend does not handle it (it would respond with a no-op or error
if
received)[\[1\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=match%20at%20L964%20by%20SceneManager,end.%20Our%20strategy).
The UI would interpret this if an AI agent sent it (e.g., the AI might
say \"zoom out\", which the UI would then just enact locally).

This list covers the main expected commands. The system can be extended
with new commands as needed; for instance, if we add an `offset_object`
API, we would also define an MCP command for it (e.g.,
`{"command": "offset_object", "id": "curve1", "distance": 5.0}`) which
the Scene Manager would implement accordingly.

**MCP Execution Flow:** On the frontend, there is a function (or
WebSocket event handler) like `dispatchMCP(command: object): object`
that the UI or AI panel calls to send a command to the backend. This
will typically result in an HTTP request or WebSocket message to the
server, where the Scene Manager's `handle_mcp_command` processes it. The
Scene Manager should parse the JSON (or if already a Python dict, use it
directly) and **validate it** -- ensuring the required fields are
present and types are correct. The QA strategy emphasizes testing
malformed commands (missing fields, wrong types) to ensure robust error
handling. Using a schema or Pydantic model for commands could help catch
these errors early. After validation, the Scene Manager dispatches to
the appropriate internal method or logic: e.g., for `create_object`,
call geometry constructors and then `add_object`; for
`update_parameters`, update the object's state, etc. Once the action is
done, a result is formulated. The result could be simple (e.g.,
`{ "status": "ok" }`) or detailed (e.g., returning the new object's data
for a create, or the updated parameters for an update). The design
examples suggest returning at least confirmation, and in some cases data
-- for example, `describe_object` obviously returns the object data, and
`create_object` might return the new object's ID or full info.
Consistency in response format is important so the UI or agent knows how
to parse it.

After processing, the backend returns the response through the same
channel. If using HTTP, the response is the JSON; if using WebSocket, it
might be a specific response message correlated by an ID. In our
scenario, since the UI directly calls and gets a return (maybe over an
async call), it can just handle the response in a callback or promise.
Additionally, if the command caused a scene change visible to others
(e.g., another collaborator or just to keep UI in sync), the backend may
emit an event. For example, after a successful `update_parameters`, the
backend could broadcast `object_updated` with the new state. The
initiating UI might not strictly need that (it already knows it
updated), but if multiple agents or windows are open, such broadcast
ensures everyone stays in sync.

**Testing MCP:** From a development standpoint, treat the MCP layer as a
thin but crucial integration layer. The QA plan calls for treating MCP
tests as integration tests between the API layer and the Scene Manager's
core logic. Each command should be tested: sending in a well-formed
command and verifying that the correct Scene Manager methods were
invoked and the scene state changed appropriately (and the correct
response was returned). Also test error cases: unknown commands, missing
required data, or attempts to act on non-existent objects should result
in clear error messages (the design might specify an error response
format, e.g., `{ "error": "Unknown command" }` or an exception that gets
turned into an error reply).

**Extensibility:** As new features are added to the system, the MCP
should be extended to cover them so that the AI can use them. Keep the
command set **in sync with backend capabilities**. For example, if we
add `duplicate_object` functionality in Scene Manager, define an MCP
command `"duplicate_object"` mapping to it. The documentation for MCP
should be updated accordingly (perhaps auto-generated or manually
maintained in a table, similar to how it's outlined in design docs).

**Security Consideration:** MCP commands expose powerful capabilities.
If the system is deployed in a multi-user or networked scenario, ensure
that appropriate authentication or permission checks guard the use of
MCP (for instance, a malicious user shouldn't be able to connect via
WebSocket and delete all objects unless authorized). This is more of a
deployment detail, but worth noting as developers implement the
protocol.

In summary, MCP is the glue that allows the AI and UI to drive the Scene
Manager. Adhering to the specified command schemas and properly handling
each case in the Scene Manager will yield a robust and flexible control
layer for the system.

## Test-Driven Development and QA Strategy

The project adopts a **test-first development approach** -- writing test
cases for each module and feature before or alongside implementation.
This ensures that the intended behavior is clearly defined and verified
continuously. The QA strategy document outlines detailed test plans per
module (Geometry, Graphics Interface, Scene Manager, UI) as well as
integration testing for MCP and overall system workflows. Developers are
expected to write unit tests for all new code and maintain high
coverage.

**Unit Testing Each Module:** For each core module, there is a battery
of functional tests and edge-case tests: - *Geometry Module Tests:*
These tests cover the correctness of geometric computations. For
example, tests verify that the `intersect()` function finds the proper
intersection points of curves (including special cases like tangential
intersections), that `blend()` produces a valid combined curve, and that
`offset()` generates the expected offset curve. A test might create a
circle of radius 1, call `offset(circle, 0.5)`, and then check that the
result is approximately a circle of radius 1.5 (by evaluating the
implicit function at a known point). Other tests ensure boolean
operations (union, difference) produce correct inside/outside
classifications, and trimmed/composite curves behave consistently (e.g.,
composite curve evaluation matches the segments, closed composites
report as closed). Exception handling is also tested: e.g., calling
`curve_segment` with endpoints not on the curve should raise an error.
The design guidelines (fail fast on invalid input) are enforced by tests
expecting exceptions for bad inputs. We use **pytest** for Python tests,
with fixtures to set up common objects (like a set of test curves). The
geometry tests also include performance sanity checks (like offsetting a
complex shape does not take excessively long), though performance
profiling is secondary to correctness in automated tests. - *Graphics
Interface Tests:* Here we treat the interface as a black box given a
known scene setup. For example, after adding known objects to the scene,
`get_bounding_box()` should return the correct bounds encompassing all.
`get_curve_paths()` is tested to ensure it returns the correct number of
paths with plausible point data -- e.g., for a simple circle, we expect
points roughly on the circle and style info present. Tests vary
resolution and tolerance to ensure those parameters take effect (higher
resolution yields more points). `get_field_data()` is tested by
comparing a few sample values against direct field evaluations.
Intersections and annotations are similarly validated (ensuring an
intersection that is expected is present and correctly labeled). We also
test how the interface handles *empty or error conditions*, for instance
calling `get_field_data` when no field exists (should return an empty
result or sensible default without
crashing)[\[2\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=,and%20ensure%20it%E2%80%99s),
or asking for a curve path with an invalid resolution (should raise a
ValueError). - *Scene Manager Tests:* These focus on scene operations --
adding and removing objects (the object list should update, and trying
to remove a non-existent object should error), grouping logic (group
membership is correctly assigned, and removing an object also updates
its group). Persistence is tested by saving a scene, then loading it and
comparing that the objects reappear with same properties. The save
formats are validated: JSON output should contain all objects with the
required fields, and a `.scene.py` round-trip should recreate an
equivalent scene (tests might execute the saved `.scene.py` in a safe
context and compare). The Scene Manager's integration with geometry is
implicitly tested in these cases (since saving/loading calls
`to_dict`/`from_dict` of geometry objects -- tests ensure that, say, a
CompositeCurve saved and loaded still has the same number of segments,
etc.). We also test the **rendering helpers** (if any) like
`render_image` in a limited way (maybe check that an image file is
created and is not empty). If the rendering spawns threads or uses
callbacks (like the animate function in `render_animation`), we use
synchronous testing or mock the time progression to verify that the
expected number of frames is produced without manual delays. - *MCP
Command Tests:* These are treated as *integration tests* that span the
Scene Manager and other components. For each supported command, we
simulate sending the command (by calling
`sceneManager.handle_mcp_command` with a dict) and then verify the
outcome. For example, for `create_object`, we check that after the call,
`sceneManager.get_object(new_id)` returns a valid object of the
requested type. For `delete_object`, we ensure the object is actually
gone from the registry. For `update_parameters`, we might check that the
object's internal parameter changed (and possibly that an
`object_updated` event is queued for broadcast). Group operations, style
changes, and field strategy commands are similarly tested in sequence to
make sure they produce the expected scene state. Error handling is
crucial here: tests attempt unknown commands, missing fields, or invalid
values and expect a clear error response without blowing up the server.
The MCP tests confirm that the mapping table (commands to methods) is
correctly implemented and that the system's state changes are consistent
with a direct API call. - *UI and Integration Testing:* Testing the
actual UI in a browser is complex, but we do as much as possible in
automated fashion. We utilize **Jest** for front-end logic tests,
targeting functions like name generation, command dispatch formatting,
and state reducers. For instance, we test that the name generator
produces unique whimsical names and properly appends numbers when
needed. We simulate a parameter slider change by calling the responsible
function with a fake event and verify it results in either a local state
update or an MCP call being issued (e.g., check that `dispatchMCP` was
called with the correct JSON). We also test the UI's handling of
incoming events: feed it a fake `object_updated` WebSocket message and
ensure the UI updates that object's data in its store and refreshes the
view (this can be done with a controlled store in a test setting).
End-to-end testing in a real browser (with tools like Playwright or
Cypress) will be minimal but targeted: for example, start the backend
and a test UI, then simulate a user creating an object through the UI
and verify it appears on canvas. Most heavy logic, however, is validated
at the unit or integration level without needing a full GUI automation,
which keeps tests maintainable.

**System-Level Testing Considerations:** Beyond individual modules, we
consider scenarios that test the system as a whole: - **Full Workflow
Simulation:** A test might go through a sequence: create a curve, offset
it, group it, save the scene, load the scene, then delete an object.
This ensures that state transitions are consistent across multiple
operations and that persistence works in the middle of a session. After
the sequence, the final scene state is checked to ensure consistency
(e.g., no ghost references in groups after deletion). - **Concurrent
Modifications:** If the design ever allows multiple simultaneous agents
(or asynchronous operations), tests ensure thread safety or order of
execution. For now, we mostly run things synchronously, but e.g.,
sending a burst of 10 `create_object` commands rapidly via MCP should
result in 10 objects with unique IDs -- tests can simulate this by
calling `handle_mcp_command` in a loop and verifying all objects exist
with proper unique naming (especially if ID isn't provided and the
system auto-names). - **Performance and Load:** We include some
non-regression performance tests (not as strict pass/fail in CI, but to
monitor), such as creating a very complex composite curve or a large
field and measuring that queries like `get_curve_paths` or `save_scene`
complete within a reasonable time. If a test consistently exceeds a
threshold, it might indicate a performance bug (e.g., an inefficient
algorithm). - **Resource Cleanup:** Tests ensure that files created by
save (temporary files) are cleaned up, that deleting objects frees them
for garbage collection (no memory leaks), etc. In Python tests, using
pytest's `tmp_path` for file operations helps with
cleanup[\[3\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=match%20at%20L528%20files%20,actually%20writing%20files%20or%20using).

All tests are run in continuous integration for each commit, and any
failures prevent merging, enforcing quality. Writing tests first not
only clarifies the desired behavior but also creates a safety net for
future refactors. Developers should also write **regression tests** for
any bugs found: if an error is discovered (e.g., blending two specific
curves fails), a test reproducing that scenario is added to ensure it
stays fixed going forward.

In summary, a comprehensive QA strategy is in place. As an AI developer
contributing to this project, you should write tests for any new feature
you implement *before* writing the feature (when possible), and ensure
all existing tests remain green. Use the test plan document as guidance
for what kinds of edge cases to consider. Quality is paramount for this
system given its mathematical nature and interactive use -- we want no
surprises for end users or when the AI is controlling the system.

## Deployment and Source Control Guidelines

Bringing all parts of this system together requires careful organization
in source control and a clear deployment plan. Below are guidelines on
project structure, versioning, and deployment steps:

**Source Repository Structure:** - **Core Library (**`sketchlib/` **or
similar):** This directory contains the Python packages for the Implicit
Geometry module and the Scene Manager (and possibly the Graphics
Interface implementation). For example, `sketchlib/geometry/` could
house `implicit_curve.py`, `composite_curve.py`, etc., and
`sketchlib/scene/` could contain `scene_manager.py`,
`graphics_interface.py` (if the interface is implemented here), and
related classes (style, group management, etc.). Ensuring a logical
separation (geometry vs scene management) in the codebase will make it
easier for multiple developers to work without overlap. - **Frontend UI
(**`ui/` **or a separate repository):** The web client code
(HTML/JS/CSS). If using a framework, this might be structured as a React
or Vue project. It will have its own structure (e.g., `src/components/`,
`src/utils/` for math and MCP logic, etc.). The front-end should be in
version control either in the same repo (if tightly coupled) or a linked
repo. In our case, since this is an integrated guide, we presume a
single repo for simplicity, but clearly separate the front-end
directory. Include build configuration files (like `package.json`,
webpack config) in version control so the build can be reproduced. -
**Tests (**`tests/`**):** A top-level tests directory containing
subfolders for each module's tests (e.g., `tests/test_geometry.py`,
`tests/test_scene_manager.py`, `tests/test_mcp.py`, `tests_ui/` for
front-end logic tests, etc.). Organize tests mirroring the code
structure. All test files and any test resources (like example scene
files, sample images for fields, etc.) should be checked in to ensure
consistent test runs in CI. - **Documentation (**`docs/`**):** Design
documents (like the ones summarized here), usage guides, and API
references can reside here. Files such as `implicit_geometry_design.md`,
`scene_manager_interfaces.md`, etc., can be included for reference, and
a high-level README to help new developers understand the project. It's
useful to keep these in version control to track design changes and
rationales. - **Examples and Assets (**`examples/` **or**
`assets/`**):** Provide a folder with example scenes (both in JSON and
.scene.py format) that demonstrate various features. For instance, an
example scene JSON with a couple of objects pre-defined, or a .scene.py
that procedurally builds a more complex design. These can be used for
manual testing or demos. Also, if there are sample images (for image
fill fields) or default style configurations (like a JSON of default
styles), include them here. - **Git Ignore:** Configure `.gitignore` to
exclude files that should not be committed. This includes: - Temporary
or user-specific output, e.g., any `.scene.py` or `.json` files that are
saved by users during their sessions (unless intentionally added as
examples). For instance, you might ignore `*.scene.py` globally, but
commit specific ones in the examples folder. - Logs, cache, compiled
files (e.g., Python `.pyc` or front-end build artifacts like `dist/`
folder, if any). - Virtual environment directories or dependency
caches. - **Requirements and Config:** Check in `requirements.txt` or
`pyproject.toml` for Python dependencies, and similarly `package.json`
for npm dependencies. This ensures anyone setting up the project can
install the correct versions.

**Deployment Considerations:** - **Backend (Python) Deployment:** The
backend can be packaged as a Python application. If it's providing HTTP
endpoints (as suggested by the required calls like POST /object, etc. ),
it likely uses a web framework (Flask/FastAPI). Ensure the entry point
(e.g., `app.py` or `server.py`) is in the repo, configured to import the
Scene Manager and set up routes for MCP commands and data queries. For
deployment, containerizing the backend using Docker is recommended,
pinning to a specific Python version and including all library
dependencies. The container should expose whatever port the HTTP or
WebSocket server runs on. - **Frontend (Web UI) Deployment:** The UI can
be deployed as a set of static files if it's a single-page application
(just host the built `index.html` and JS bundle on a static server or
CDN). Alternatively, if using a framework with a dev server, ensure the
production build step is documented (e.g., `npm run build`). The built
artifacts should be deployed to a web server. If the backend and
frontend are served together (e.g., backend also serving the UI files),
ensure the integration (the Flask app might serve static files from the
`ui/build` directory). - **Configuration:** It's useful to have a
configuration file or environment variables for things like the default
resolution, allowed max field size, etc., which were mentioned in
metadata. This way, deployment can tweak these if needed (for instance,
lower the max resolution in a low-resource environment). Also, configure
the backend's URL for the frontend (in development it might be
localhost, in production, a stable domain). - **Security:** If deploying
publicly, secure the channels (use HTTPS for server, WSS for WebSocket).
The MCP and endpoints might need authentication (at least a simple
token) to prevent misuse. This is beyond the core functionality but
crucial for real-world deployment. - **Logging and Monitoring:** Ensure
the backend logs important events (like MCP commands received, errors,
etc.) to stdout or a file, and that this is accessible in deployment
(for debugging issues). On the UI, consider a debug mode that can be
toggled for additional console logging of MCP messages and state
changes, which is invaluable during development or troubleshooting with
users. - **Continuous Integration (CI):** Set up CI to run all tests on
each commit or pull request. This could use GitHub Actions, GitLab CI,
etc. The CI configuration (YAML files) should be in the repo. It will
likely have jobs to (1) set up Python environment and run pytest, (2)
set up Node environment and run front-end tests, and possibly (3) build
the front-end and ensure it succeeds. - **Version Control Practices:**
Use branches for feature development and pull requests for integration.
Given AI developers are involved, make sure to perform code reviews for
AI-generated code -- ensure it meets style and passes tests. Tag
releases (e.g., v1.0, v1.1) when stable. Since multiple modules are in
the same repo, increment version numbers in a coordinated way or use a
single version for the whole system.

**Handling** `.scene.py` **and** `.json` **Files:** These scene files
are outputs of the application when a user saves their work. They are
**not source code** per se, and should generally not be committed to the
main repository unless for specific reasons (like examples or regression
tests). Typically: - **User Scenes:** Are kept in user space (downloaded
via browser or stored on server storage) and not mixed with app code. If
the application has a cloud component, these might be stored in a
database or cloud storage. - **Example Scenes:** If we include some in
the repo, place them in a clearly marked directory (`examples/`). Ensure
they are small and illustrate key features. This also helps with
automated tests; e.g., you can have a test that loads an example scene
and asserts it loads without error. - **Procedural .scene.py vs JSON:**
The JSON format is safer for long-term compatibility (and easier to diff
in version control if we ever needed to). The `.scene.py` format is more
for convenience. We do not expect developers to hand-write .scene.py
files except for simple cases, and any .scene.py checked in should be
treated as code (review its content for security). In deployment, you
might disable `.scene.py` loading or restrict it, to avoid executing
arbitrary code. If not, ensure only trusted users can upload .scene.py
files to the server.

**Expectations for AI Developer Contributions:** - *Adherence to
Design:* AI developers implementing parts of this system (whether it's a
new geometry algorithm or a rendering optimization) must follow the
interface contracts and guidelines laid out in the design docs. Do not
introduce changes that break the specified APIs without discussion. For
example, if implementing the `CompositeCurve` class, ensure it conforms
to the `ImplicitCurve` interface so it can be used interchangeably, as
the design explicitly requires. - *Code Style and Quality:* Maintain
consistent naming (use `snake_case` for Python, `camelCase` or
appropriate convention for JS) as specified. Include docstrings or
comments referencing the design spec for any complex logic. Check for
edge cases and use exceptions to handle invalid input (never silently
ignore an error). The geometry module, for instance, should raise
`ValueError` for domain errors, as tests will expect that. - *Testing:*
Write unit tests for any new capability. If you implement a new MCP
command, add tests for it. If you fix a bug, add a regression test. The
goal is to keep the test suite comprehensive and up-to-date. All tests
should pass before code is merged -- our CI pipeline will enforce
this. - *Collaboration:* Document any new module or significant function
in the `docs/` if it's not self-evident. When in doubt, refer back to
these integration guidelines and the module design documents (which we
keep in the repo for reference). If an AI is generating code, ensure a
human developer reviews it for compliance and adds the necessary inline
comments, especially for tricky math or logic. - *Renderer
Implementation:* If tasked with writing a new renderer (say a fallback
Matplotlib renderer for offline use, or a custom ThreeJS scene
integration), keep in mind the **constraints mentioned earlier**:
respect the data provided, don't bake in shortcuts that assume a
particular environment (the idea is any renderer reading the output of
`GraphicsBackendInterface` should draw the same scene). Test the
renderer with a variety of scenes, including edge cases like extremely
small or large coordinates (check that scaling or precision doesn't
break). - *Performance Optimizations:* If you optimize something (say, a
faster intersection algorithm or a caching layer for curve
discretization), make sure it does not change the external behavior or
interface. Use the metadata flags (like `adaptive_sampling` in metadata)
to toggle such features if needed so that we can compare results with
and without the optimization easily.

**Deployment Workflow:** For production deployment, a possible workflow
is: 1. **Build front-end** (e.g., run `npm run build` to produce static
files). 2. **Package backend** (if using Docker, build the image
including copying the built UI files into a directory the backend can
serve). 3. **Run migrations or setup** if any (not likely for this
system unless we have a user database or similar). 4. **Launch** the
backend (ensuring it serves on configured host/port, and static UI files
are accessible). 5. **Monitoring:** Keep an eye on logs and set up
health checks (e.g., an endpoint that returns OK) to ensure the service
is running.

By following these guidelines, we ensure that the system is
maintainable, extensible, and stable in production. All team members,
including AI coders, should coordinate via the shared repository, using
feature branches and pull requests with reviews for any changes. The
combination of a strong test suite, clear module boundaries, and
adherence to the design contracts will enable rapid development while
minimizing integration issues as the 2D Implicit Sketching System
evolves.

[\[1\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=match%20at%20L964%20by%20SceneManager,end.%20Our%20strategy)
[\[2\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=,and%20ensure%20it%E2%80%99s)
[\[3\]](file://file-L5w4RLcZK6WV1mPoUKVKp9#:~:text=match%20at%20L528%20files%20,actually%20writing%20files%20or%20using)
QA and Testing Strategy for Implicit 2D Sketching System.docx

<file://file-L5w4RLcZK6WV1mPoUKVKp9>
