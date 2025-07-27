# 2D Implicit Sketching Application UI Specification

This document outlines a comprehensive **client-side UI specification** for a 2D implicit sketching application. The UI supports creation, visualization, and editing of **geometric objects** (implicit curves, composite shapes, area regions) and **field objects** (scalar fields like distance or fill patterns) as defined in the system’s design documents. The interface is organized to facilitate intuitive interaction with implicit geometry while leveraging the backend capabilities (e.g. real-time math evaluation, scene management, MCP agent control).

## 1. Object Naming Strategy

Every newly created object – whether a curve, field, or region – is assigned a unique, evocative default name. These default names combine whimsical adjectives or descriptors with object type hints. For example: a new looped curve might be named **“WobbleLoop”**, a field could be **“FieldSprout”**, etc. This naming scheme makes objects easier to identify than generic IDs like “c1” or “f1”, while still being unique in the scene.

- **Automatic Unique Naming:** The UI maintains a registry of existing names and ensures each new name is unique. If the auto-generated name already exists, the system will subtly alter it (e.g. append a number or use an alternate descriptor) to produce a unique variant.

- **User Renaming:** Users can rename any object via the UI. This can be done by double-clicking the object’s name or choosing a **"Rename"** option from a context menu. The UI ensures name uniqueness with validation and suggestions.

- **Naming Format:** Curves, fields, and regions will have distinct naming conventions (e.g., curve names might include "Loop", "Wave", fields might include "Field", "Map", etc.) to improve clarity when communicating with AI or referencing in UI panels.

## 2. UI Layout and Components

### 2.1 Graphics Canvas
- **Pan and Zoom** centered around mouse position
- **Object Selection** with filters (select curves only, hide fields, etc.)
- **Right-Click Context Menu** with styled options for edit, delete, style, etc.
- **Interactive Handles** for offset preview and curve manipulation
- **Visual Annotations** for axis bounds, field values under cursor, etc.

### 2.2 Object Category Panels
- Stacked collapsible panels for:
  - Conic Curves
  - Polynomial/Custom Curves
  - Composite Curves
  - Area Regions
  - Field Objects
- Each item displays:
  - Visibility toggle
  - Color/style swatch
  - Editable name
  - Inline quick actions (edit, delete, style)

### 2.3 Contextual Menus
- **Object menu** (edit, delete, rename, show dependencies, duplicate, export)
- **Canvas menu** (add object, paste, reset view, show grid, frame all)

### 2.4 Global Controls
- Toolbar or top menu for:
  - Save/Load Scene
  - Export image/animation
  - Default style editor
  - Undo/Redo
  - Animation panel toggle
  - Help/docs access

### 2.5 AI Interaction Panel
- A dedicated **AI panel** is positioned on the **right side** of the window.
- Functions similarly to interfaces in tools like **Cursor** and **Windsurf**.
- Allows users to type natural language commands or requests.
- All AI commands are dispatched as **MCP commands** (e.g. `create_object`, `update_parameters`, `set_style`).
- Supports:
  - Asking the AI to create or modify geometry.
  - Requesting explanations or suggestions.
  - Running parameter sweeps or stylization via prompt.
- The panel is **collapsible** to preserve workspace. Users can toggle visibility with a button.
- The AI panel enhances productivity but mirrors functionality already available in the UI, so users can work via UI or AI seamlessly.

## 3. Editing and Styling

### 3.1 Object Inspector Panel
- Editable fields for name, equation, parameters
- Smart controls for parameter sliders with real-time updates
- Field source indication for derived fields
- Area boundary listing and editing

### 3.2 Style Tools
- Stroke color, width, dash pattern
- Fill color, pattern, image-based fill
- Field colormap, opacity, level-set contour values
- Save and reuse named style presets

### 3.3 Groups and Visibility
- Create and name groups of objects
- Apply group-wide style and visibility settings
- Ungroup or remove from group
- Category-based visibility toggles (e.g., hide all fields)

## 4. Special Interactions

### 4.1 Offset Mode
- Enable mode on selected curve
- Render live distance field with isocontour previews
- Drag-to-offset interaction (outward = positive, inward = negative)
- Option to save field or create curve at offset value

### 4.2 Annotation Overlays
- Axis bounds and grid
- Value under cursor for fields
- Dimension lines or bounding boxes
- On-canvas labels for parameters (e.g., "r = 5")

### 4.3 Image Fill Mapping
- Select image fill for region
- On-canvas draggable handles for position/scale/rotation
- Fill tiling controls and tiling preview

## 5. Animation and Export

### 5.1 Animation Panel
- Select object and parameter to animate
- Set range, frame count, easing
- Play/stop controls with scrubbing
- Manual frame stepping

### 5.2 Export Options
- Export current view as PNG/SVG
- Export animation to GIF/WebM
- Optional per-object export (e.g., curve as SVG, field as PNG)

## 6. Persistence and Interop

### 6.1 Save/Load Scene
- Save as `.json` or `.scene.py`
- Load restores all object definitions, groups, styles
- Autosave/restore from local storage (optional)

### 6.2 MCP Support
- Respond to `create_object`, `update_parameters`, `set_style`, etc.
- UI dispatcher for incoming MCP commands
- Optional command console for developers

## 7. Missing or Suggested API Extensions

- `get_dependencies(object_id)` for dependency highlighting and validation
- `list_fields_by_source(curve_id)` for automated field linking UI
- `get_default_styles()` to persist user style preferences
- Image asset embedding or linking in scene save files
- Parameter enumeration API: `list_parameters(object_id)` (if needed)
- UI hooks for snapping or guided placement using `get_intersections()`

---

This specification enables implementation of a modern, user-friendly UI for exploring implicit geometry and scalar fields with strong support for MCP integration and future extensibility.

