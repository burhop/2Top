from __future__ import annotations

from typing import Callable, Dict


def build_default_action_registry(win) -> Dict[str, Callable[[], None]]:
    """Return the default label -> handler mapping for the main window.

    This centralizes command registration, so tests can import this
    function and verify the set of commands without constructing the UI.
    """
    return {
        # Geometry
        "Add Circle": win._add_circle,
        "Add Rectangle": win._add_rectangle,
        "Add Ellipse": win._add_ellipse,
        "Add Line": win._add_line,
        "Add Composite (from selection)": win._add_composite,
        "Add Conic (A..F)": win._add_conic,
        "Add Implicit Curve": win._add_implicit,
        "Add Polynomial Curve": win._add_polynomial,
        "Add R-Function Curve": win._add_rfunction,
        "Add Superellipse": win._add_superellipse,
        "Add Procedural Curve": win._add_procedural,
        "Add Trimmed Implicit": win._add_trimmed_implicit,
        # Utils
        "Zoom In": win._zoom_in,
        "Zoom Out": win._zoom_out,
        "Zoom All": win._zoom_all,
        "Pan Left": win._pan_left,
        "Pan Right": win._pan_right,
        "Pan Up": win._pan_up,
        "Pan Down": win._pan_down,
        "Clear Scene": win._clear_scene,
        "Scene Summary": win._scene_summary,
    }
