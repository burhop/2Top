# Qt App Feature Plan (Local-only)

Order: Geometry → Regions → Fields → Operations. No MCP/HTTP; create objects via dialogs, render locally.

## Phase 1 — Geometry
- Buttons: Circle, Rectangle, Ellipse, Line, Polygon, Composite (from selection), Conic (A..F), Implicit Curve (f(x,y)=0)
- Dialogs (ParameterDialog):
  - Circle: center_x, center_y, radius
  - Rectangle: center_x, center_y, width, height
  - Ellipse: center_x, center_y, a, b
  - Line: x1, y1, x2, y2
  - Polygon: N points (CSV or simple point table), auto-close
  - Composite: select one or more existing curve objects (see Object Selector below)
  - Conic (general quadratic): A, B, C, D, E, F for equation `A*x^2 + B*x*y + C*y^2 + D*x + E*y + F = 0`;
    optional: preview bounds (x_min, x_max, y_min, y_max), resolution (e.g., 200)
  - Implicit Curve: expression string `f(x,y)=0` (e.g., `sin(x)+cos(y)-0.2`), variables fixed to `x,y` for MVP;
    required: preview bounds (x_min, x_max, y_min, y_max); optional resolution
- Plot classes: AnimatableCircle, AnimatableRectangle, AnimatableEllipse, AnimatableLine, AnimatablePolygon, AnimatableCompositeCurve, AnimatableConic, RenderableImplicitCurve
- Rendering: each implements `.plot(ax, xlim, ylim, **style)`; scene uses existing `render_scene_to_png()`
  - Conic/Implicit: evaluate grid on bounds and draw contour `f(x,y)=0` via `matplotlib.contour`; thin anti-aliased line

## Phase 2 — Regions
- Button: Create Region
- Dialog: choose outer boundary (closed polygon/composite) and optional holes (multi-select)
- Class: AnimatableRegion with outer polygon and hole polygons
- Validation: ≥ 3 vertices for polygons; soft bbox checks for holes inside outer
- Rendering: matplotlib Path/PathPatch to fill outer and punch holes

## Phase 3 — Fields
- Buttons: Curve Field, Region Field, Blend Fields
- Dialogs:
  - Strategy: SignedDistance or Occupancy
  - Params: grid resolution/step, inside/outside values for occupancy
  - Blend: pick two fields + weight/operation
- Class: RenderableField (stores 2D array + extent), `.plot()` via imshow/contour

## Phase 4 — Operations
- Buttons: Union, Intersect, Difference (regions)
- Dialog: pick A and B (regions)
- Implementation (MVP): if polygon boolean ops lib unavailable, defer; else produce new AnimatableRegion

## Shared Infrastructure
- Object registry: use existing SceneManager to store objects with IDs and styles
- Validation helpers: numeric parsing, polygon checks
- Rendering: keep `_render_and_display()` unchanged

## NEW Requirement — Object Selector
For any feature that requires existing objects as input (e.g., Composite curve from parts, Region from boundaries/holes, Field from a curve/region, Boolean ops):

- Provide an Object Selector UI element in dialogs:
  - Displays a searchable list/dropdown of existing objects by their IDs/names from `SceneManager.list_objects()`
  - Supports single-select or multi-select as required by the operation
  - Filters by compatible types (e.g., only curves for Composite; only closed polygons/composites for Region; only regions for union/intersect/difference; only fields for blend)
  - Shows brief metadata preview for selection: type, segment/point count (if applicable)
- On submit, resolve IDs to objects via `SceneManager.get_object()` and validate compatibility; show user-friendly errors if invalid

## Milestones
1) Geometry buttons + dialogs + plot classes (Ellipse, Line, Polygon, Composite)
2) Region creation with holes using Object Selector
3) Field generation (SDF/Occupancy) and field rendering
4) Region boolean ops (optional depending on availability)
