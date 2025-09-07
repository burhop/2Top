# 2Top PySide6 Desktop UI (examples/ui)

This directory contains a minimal PySide6 desktop app for interacting with the 2Top geometry system.

- Entry point: `examples/ui/qt_app.py`
- Features:
  - Left: list of creation buttons
  - Right: image render (matplotlib) + info panel
  - Reusable parameter dialog supporting string, float, int, and bool
  - Uses `SceneManager` for object management and styling

## Quick Start

1) Install dependencies (ensure you target the same Python used to run the app):

```
python -m pip install -r requirements.txt
```

2) Run the app:

```
python examples/ui/qt_app.py
```

If you see "No module named 'PySide6'": you're likely using a different interpreter than the one that installed packages. Install using the absolute Python path or the `py -3.10` launcher, e.g.:

```
"C:\\Users\\<you>\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" -m pip install PySide6>=6.5.0
```

## How Rendering Works

- The app renders the current scene to a temporary PNG using matplotlib (`Agg` backend) and displays it in the UI.
- Each object added to the scene is expected to expose a `plot(ax=..., xlim=..., ylim=..., **style)` method.
- Styles are stored per-object in `SceneManager` and passed to `plot`.

## Adding New Buttons and Dialogs

You can add new creation commands by registering a handler and optionally using the reusable parameter dialog. Edit `examples/ui/qt_app.py`:

1) Register a button in `TwoTopMainWindow._register_default_buttons()`:

```python
self.button_registry = {
    "Add Circle": self._add_circle,
    "Add Rectangle": self._add_rectangle,
    "Add MyObject": self._add_my_object,  # new
    "Clear Scene": self._clear_scene,
    "Scene Summary": self._scene_summary,
}
```

2) Implement a handler that uses `ParameterDialog` and constructs your object:

```python
from typing import Dict

# Schema spec for ParameterDialog
# - name: kwarg name for your constructor
# - label: user-facing label text
# - type: 'str' | 'float' | 'int' | 'bool'
# - default: initial value
# - min/max/step: optional (numeric types only)

def _add_my_object(self):
    schema = [
        {"name": "id",        "label": "ID",       "type": "str",   "default": "obj1"},
        {"name": "segments",  "label": "Segments", "type": "int",   "default": 32, "min": 3,   "max": 360, "step": 1},
        {"name": "scale",     "label": "Scale",    "type": "float", "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1},
        {"name": "filled",    "label": "Filled",   "type": "bool",  "default": False},
    ]
    dlg = ParameterDialog("Create MyObject", schema, self)
    if dlg.exec() == QDialog.Accepted:
        params: Dict[str, object] = dlg.values()
        obj_id = self._unique_id("myobj")
        obj = MyObjectConstructor(**params)  # Make sure names match your constructor
        self.scene.add_object(obj_id, obj, style={"color": "#2ca02c", "linewidth": 2.0, "alpha": 1.0})
        self._append_object_info(obj_id)
        self._render_and_display()
```

3) Ensure your constructor parameters match the schema `name` fields (they become kwargs).

4) If your object does not have `plot(...)`, you can:
- Implement a `plot` method in the object, or
- Adapt `render_scene_to_png` to use the graphics backend interface if available for that type.

## ParameterDialog Notes

The dialog lives in `qt_app.py` as `ParameterDialog` and supports:
- Types: `str`, `float`, `int`, `bool`
- Labels and defaults for all fields
- `min`, `max`, `step` for numeric types
- On OK, returns a dict mapping `name -> value`

Example schema for a circle (already used by the app):

```python
schema = [
    {"name": "center_x", "label": "Center X", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
    {"name": "center_y", "label": "Center Y", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
    {"name": "radius",   "label": "Radius",   "type": "float", "default": 1.0, "min": 0.1,  "max": 10.0, "step": 0.1},
]
```

## SceneManager Integration

- Objects are added via `self.scene.add_object(obj_id, obj, style=...)`.
- Styles are simple dicts: `{ "color": str, "linewidth": float, "alpha": float, ... }`.
- You can group, style, and persist scenes using the `SceneManager` API.

## Animation (Future Hook)

The `SceneManager` includes parameter-based animation features (single/multi-parameter) with caching and dependency tracking. You can extend this UI to:
- Create an animation definition from a selected object and parameter(s)
- Render frames using the existing frame cache
- Preview/playback or export GIF/MP4

Refer to `examples/parameter_animation_demo.py` and `scene_management/scene_manager.py` for the API.

## Troubleshooting

- PySide6 missing: install with the exact Python you use to run the app.
- No window appears in headless contexts; run from a desktop session.
- If render looks empty, check that objects implement `plot(...)` and that x/y limits are reasonable.
