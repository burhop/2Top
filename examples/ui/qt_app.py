"""
2Top PySide6 Desktop App (MVP)

- Left: Extendable list of buttons to create implicit geometry/fields
- Right: Scene render view (image) and object info text window
- No web; runs locally:  python examples/ui/qt_app.py
"""

import os
import sys
import tempfile
import logging
import io
import contextlib
import traceback
from datetime import datetime
from typing import Callable, Dict

# Ensure repository root is on sys.path when running directly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import numpy as np
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QToolBar,
)

from scene_management import SceneManager
from ui.view_state import Viewport
from ui.rendering import render_scene_to_png
from ui.dialogs import ParameterDialog, ObjectSelectorDialog
from ui.actions import build_default_action_registry
from ui.menus import build_buttons_panel
from ui.widgets import ImageView


# --- Logging setup ---
LOG_PATH = os.path.join(tempfile.gettempdir(), "2top_ui.log")

def get_logger() -> logging.Logger:
    logger = logging.getLogger("2top_ui")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


# --- Simple animatable demo objects that support .plot() ---
# These mirror the approach in examples/parameter_animation_demo.py
class AnimatableCircle:
    def __init__(self, center_x=0.0, center_y=0.0, radius=1.0):
        self._parameters = {
            "center_x": float(center_x),
            "center_y": float(center_y),
            "radius": float(radius),
        }

    # Parameter interface used by SceneManager demos
    def list_parameters(self):
        return list(self._parameters.keys())

    def get_parameters(self):
        return self._parameters.copy()

    def get_parameter(self, name: str):
        return self._parameters[name]

    def set_parameter(self, name: str, value):
        self._parameters[name] = float(value)

    # Minimal plotting used by the viewer
    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        theta = np.linspace(0, 2*np.pi, 200)
        cx, cy, r = (
            self._parameters["center_x"],
            self._parameters["center_y"],
            self._parameters["radius"],
        )
        x = cx + r * np.cos(theta)
        y = cy + r * np.sin(theta)
        color = style.get("color", "#1f77b4")
        linewidth = style.get("linewidth", 2.0)
        alpha = style.get("alpha", 1.0)
        ax.plot(x, y, color=color, linewidth=linewidth, alpha=alpha, label=f"circle r={r:.2f}")
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

    def __repr__(self):
        p = self._parameters
        return f"AnimatableCircle(cx={p['center_x']}, cy={p['center_y']}, r={p['radius']})"

    # Axis-aligned bounding box
    def bounding_box(self):
        cx = self._parameters["center_x"]; cy = self._parameters["center_y"]; r = self._parameters["radius"]
        return (cx - r, cx + r, cy - r, cy + r)


class AnimatableRectangle:
    def __init__(self, center_x=0.0, center_y=0.0, width=2.0, height=1.5):
        self._parameters = {
            "center_x": float(center_x),
            "center_y": float(center_y),
            "width": float(width),
            "height": float(height),
        }

    def list_parameters(self):
        return list(self._parameters.keys())

    def get_parameters(self):
        return self._parameters.copy()

    def get_parameter(self, name: str):
        return self._parameters[name]

    def set_parameter(self, name: str, value):
        self._parameters[name] = float(value)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        cx = self._parameters["center_x"]
        cy = self._parameters["center_y"]
        w = self._parameters["width"]
        h = self._parameters["height"]
        x0 = cx - w/2.0
        y0 = cy - h/2.0
        color = style.get("color", "#d62728")
        linewidth = style.get("linewidth", 2.0)
        alpha = style.get("alpha", 1.0)
        rect = plt.Rectangle((x0, y0), w, h, fill=False, edgecolor=color, linewidth=linewidth, alpha=alpha,
                              label=f"rect {w:.2f}×{h:.2f}")
        ax.add_patch(rect)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

    def __repr__(self):
        p = self._parameters
        return f"AnimatableRectangle(cx={p['center_x']}, cy={p['center_y']}, w={p['width']}, h={p['height']})"

    def bounding_box(self):
        cx = self._parameters["center_x"]; cy = self._parameters["center_y"]
        w = self._parameters["width"]; h = self._parameters["height"]
        return (cx - w/2.0, cx + w/2.0, cy - h/2.0, cy + h/2.0)


# --- Additional curve classes ---

class AnimatableEllipse:
    def __init__(self, center_x=0.0, center_y=0.0, a=2.0, b=1.0, rotation_deg=0.0):
        self._parameters = {
            "center_x": float(center_x),
            "center_y": float(center_y),
            "a": float(a),
            "b": float(b),
            "rotation_deg": float(rotation_deg),
        }

    def list_parameters(self):
        return list(self._parameters.keys())

    def get_parameters(self):
        return self._parameters.copy()

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        p = self._parameters
        t = np.linspace(0, 2*np.pi, 400)
        x = p["a"] * np.cos(t)
        y = p["b"] * np.sin(t)
        th = np.deg2rad(p["rotation_deg"])
        xr = p["center_x"] + x * np.cos(th) - y * np.sin(th)
        yr = p["center_y"] + x * np.sin(th) + y * np.cos(th)
        ax.plot(xr, yr, color=style.get("color", "#9467bd"), linewidth=style.get("linewidth", 2.0), alpha=style.get("alpha", 1.0), label="ellipse")
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)

    def bounding_box(self):
        p = self._parameters
        a = p["a"]; b = p["b"]; th = np.deg2rad(p["rotation_deg"]) if abs(p["rotation_deg"]) > 1e-12 else 0.0
        # Closed form AABB for rotated ellipse
        wx = np.sqrt((a*np.cos(th))**2 + (b*np.sin(th))**2)
        wy = np.sqrt((a*np.sin(th))**2 + (b*np.cos(th))**2)
        cx = p["center_x"]; cy = p["center_y"]
        return (cx - wx, cx + wx, cy - wy, cy + wy)


class AnimatableLine:
    def __init__(self, x1=-1.0, y1=0.0, x2=1.0, y2=0.0):
        self._parameters = {"x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2)}

    def list_parameters(self):
        return list(self._parameters.keys())

    def get_parameters(self):
        return self._parameters.copy()

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        p = self._parameters
        ax.plot([p["x1"], p["x2"]], [p["y1"], p["y2"]], color=style.get("color", "#2ca02c"), linewidth=style.get("linewidth", 2.0), alpha=style.get("alpha", 1.0), label="line")
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)


class AnimatableCompositeCurve:
    def __init__(self, member_ids: list[str]):
        self.member_ids = list(member_ids)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        # Composite just draws members with slightly varied alpha
        # Scene and style are passed via outer call; we don't have scene here
        # so this class is used as a logical container; drawing is handled externally
        pass


class AnimatableConic:
    def __init__(self, A=1.0, B=0.0, C=1.0, D=0.0, E=0.0, F=-4.0, x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0, resolution=300):
        self._parameters = {"A": float(A), "B": float(B), "C": float(C), "D": float(D), "E": float(E), "F": float(F),
                            "x_min": float(x_min), "x_max": float(x_max), "y_min": float(y_min), "y_max": float(y_max),
                            "resolution": int(resolution)}

    def get_parameters(self):
        return self._parameters.copy()

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        p = self._parameters
        xs = np.linspace(p["x_min"], p["x_max"], p["resolution"])
        ys = np.linspace(p["y_min"], p["y_max"], p["resolution"])
        XX, YY = np.meshgrid(xs, ys)
        ZZ = (p["A"]*XX**2 + p["B"]*XX*YY + p["C"]*YY**2 + p["D"]*XX + p["E"]*YY + p["F"])
        ax.contour(
            XX,
            YY,
            ZZ,
            levels=[0.0],
            colors=[style.get("color", "#1f77b4")],
            linewidths=style.get("linewidth", 2.0),
            alpha=style.get("alpha", 1.0),
        )
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)


class RenderableImplicitCurve:
    def __init__(self, expression: str, x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0, resolution=300):
        self.expression = expression
        self.x_min = float(x_min); self.x_max = float(x_max)
        self.y_min = float(y_min); self.y_max = float(y_max)
        self.resolution = int(resolution)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        xs = np.linspace(self.x_min, self.x_max, self.resolution)
        ys = np.linspace(self.y_min, self.y_max, self.resolution)
        XX, YY = np.meshgrid(xs, ys)
        # Safe eval namespace
        ns = {"np": np, "x": XX, "y": YY}
        try:
            ZZ = eval(self.expression, {"__builtins": {}}, ns)
        except Exception:
            # Fallback to zeros to avoid crash
            ZZ = np.zeros_like(XX)
        ax.contour(
            XX,
            YY,
            ZZ,
            levels=[0.0],
            colors=[style.get("color", "#17becf")],
            linewidths=style.get("linewidth", 2.0),
            alpha=style.get("alpha", 1.0),
        )
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)


class AnimatableSuperellipse:
    def __init__(self, center_x=0.0, center_y=0.0, a=2.0, b=1.0, n=2.5):
        self._parameters = {"center_x": float(center_x), "center_y": float(center_y), "a": float(a), "b": float(b), "n": float(n)}

    def get_parameters(self):
        return self._parameters.copy()

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        p = self._parameters
        t = np.linspace(0, 2*np.pi, 600)
        cos_t = np.cos(t); sin_t = np.sin(t)
        x = p["center_x"] + p["a"] * np.sign(cos_t) * (np.abs(cos_t) ** (2.0/p["n"]))
        y = p["center_y"] + p["b"] * np.sign(sin_t) * (np.abs(sin_t) ** (2.0/p["n"]))
        ax.plot(x, y, color=style.get("color", "#8c564b"), linewidth=style.get("linewidth", 2.0), alpha=style.get("alpha", 1.0), label="superellipse")
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)

    def bounding_box(self):
        p = self._parameters
        return (p["center_x"] - p["a"], p["center_x"] + p["a"], p["center_y"] - p["b"], p["center_y"] + p["b"])


class AnimatableProcedural:
    def __init__(self, x_expr: str = "cos(t)", y_expr: str = "sin(t)", t_min: float = 0.0, t_max: float = 2*np.pi, samples: int = 400):
        self.x_expr = x_expr
        self.y_expr = y_expr
        self.t_min = float(t_min)
        self.t_max = float(t_max)
        self.samples = int(samples)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        t = np.linspace(self.t_min, self.t_max, self.samples)
        ns = {"np": np, "t": t}
        try:
            x = eval(self.x_expr, {"__builtins": {}}, ns)
            y = eval(self.y_expr, {"__builtins": {}}, ns)
        except Exception:
            x = np.zeros_like(t); y = np.zeros_like(t)
        ax.plot(x, y, color=style.get("color", "#e377c2"), linewidth=style.get("linewidth", 2.0), alpha=style.get("alpha", 1.0), label="procedural")
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)

    def bounding_box(self):
        # Sample to estimate bounds
        t = np.linspace(self.t_min, self.t_max, max(50, min(2000, self.samples)))
        ns = {"np": np, "t": t}
        try:
            x = eval(self.x_expr, {"__builtins": {}}, ns)
            y = eval(self.y_expr, {"__builtins": {}}, ns)
            x = np.asarray(x); y = np.asarray(y)
            if x.size == 0 or y.size == 0:
                return None
            return (float(np.nanmin(x)), float(np.nanmax(x)), float(np.nanmin(y)), float(np.nanmax(y)))
        except Exception:
            return None


# --- Additional implicit renderables ---
class RenderablePolynomialCurve:
    def __init__(self, expression: str, x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0, resolution=300):
        self.expression = expression
        self.x_min = float(x_min); self.x_max = float(x_max)
        self.y_min = float(y_min); self.y_max = float(y_max)
        self.resolution = int(resolution)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        xs = np.linspace(self.x_min, self.x_max, self.resolution)
        ys = np.linspace(self.y_min, self.y_max, self.resolution)
        XX, YY = np.meshgrid(xs, ys)
        ns = {"np": np, "x": XX, "y": YY}
        try:
            ZZ = eval(self.expression, {"__builtins": {}}, ns)
        except Exception:
            ZZ = np.zeros_like(XX)
        ax.contour(
            XX,
            YY,
            ZZ,
            levels=[0.0],
            colors=[style.get("color", "#bcbd22")],
            linewidths=style.get("linewidth", 2.0),
            alpha=style.get("alpha", 1.0),
        )
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)


class RenderableRFunctionCurve:
    def __init__(self, f_expr: str, g_expr: str, op: str = "union", x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0, resolution=300):
        self.f_expr = f_expr
        self.g_expr = g_expr
        self.op = op  # 'union' (min) or 'intersection' (max)
        self.x_min = float(x_min); self.x_max = float(x_max)
        self.y_min = float(y_min); self.y_max = float(y_max)
        self.resolution = int(resolution)

    def plot(self, xlim=(-5, 5), ylim=(-5, 5), ax=None, **style):
        if ax is None:
            fig, ax = plt.subplots()
        xs = np.linspace(self.x_min, self.x_max, self.resolution)
        ys = np.linspace(self.y_min, self.y_max, self.resolution)
        XX, YY = np.meshgrid(xs, ys)
        ns = {"np": np, "x": XX, "y": YY}
        try:
            F = eval(self.f_expr, {"__builtins": {}}, ns)
            G = eval(self.g_expr, {"__builtins": {}}, ns)
        except Exception:
            F = np.zeros_like(XX); G = np.zeros_like(XX)
        if self.op.lower() == "union":
            ZZ = np.minimum(F, G)
        else:  # intersection
            ZZ = np.maximum(F, G)
        ax.contour(
            XX,
            YY,
            ZZ,
            levels=[0.0],
            colors=[style.get("color", "#7f7f7f")],
            linewidths=style.get("linewidth", 2.0),
            alpha=style.get("alpha", 1.0),
        )
        ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal"); ax.grid(True, alpha=0.3)


# (render_scene_to_png moved to ui/rendering.py)
## Dialog classes moved to ui/dialogs.py


## ObjectSelector moved to ui/dialogs.py


# --- Main Window ---

class TwoTopMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2Top Interactive (PySide6)")
        self.resize(1100, 700)

        # Core state
        self.scene = SceneManager()
        self._id_counts: Dict[str, int] = {}
        # View state encapsulated in Viewport
        self.viewport = Viewport()
        # Cursor tracking for status bar (world coords)
        self._cursor_world: tuple[float, float] | None = None

        # Central layout
        central = QWidget()
        central_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # Build toolbar and status bar
        self._build_toolbar()
        self.statusBar().showMessage("Ready")

        # Right: splitter -> image on top, text below
        self.splitter = QSplitter(Qt.Vertical)

        # Image viewer inside a scroll area (interactive)
        self.image_view = ImageView(
            self.viewport,
            on_viewport_changed=self._render_and_display,
            on_mouse_move=self._on_mouse_move,
            parent=self,
        )
        self.image_view.setText("Render will appear here")
        self.image_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_scroll = QScrollArea()
        image_scroll.setWidgetResizable(True)
        image_scroll.setWidget(self.image_view)

        # Info text
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        self.splitter.addWidget(image_scroll)
        self.splitter.addWidget(self.info_text)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)

        # Register buttons and build left panel via helper
        self._register_default_buttons()
        self.buttons_panel = build_buttons_panel(self, self.button_registry)
        central_layout.addWidget(self.buttons_panel, 0)
        central_layout.addWidget(self.splitter, 1)

        # Initial render
        self._render_and_display()
        self._update_status()

    # ---- Button registry ----
    def _register_default_buttons(self):
        self.button_registry = build_default_action_registry(self)

    # ---- Toolbar/menu ----
    def _build_toolbar(self):
        tb = QToolBar("Main", self)
        self.addToolBar(tb)

        def add_action(text: str, handler, shortcut: str | None = None):
            act = QAction(text, self)
            act.triggered.connect(handler)  # type: ignore[arg-type]
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            tb.addAction(act)

        add_action("Zoom In", self._zoom_in, "Ctrl++")
        add_action("Zoom Out", self._zoom_out, "Ctrl+-")
        add_action("Zoom All", self._zoom_all, "Ctrl+0")
        tb.addSeparator()
        add_action("Pan Left", self._pan_left, "Shift+Left")
        add_action("Pan Right", self._pan_right, "Shift+Right")
        add_action("Pan Up", self._pan_up, "Shift+Up")
        add_action("Pan Down", self._pan_down, "Shift+Down")
        tb.addSeparator()
        add_action("Clear Scene", self._clear_scene, "Ctrl+Backspace")
        add_action("Scene Summary", self._scene_summary, "Ctrl+I")

    def _rebuild_buttons_ui(self):
        # Rebuild entire panel using helper (for future dynamic updates)
        parent_layout = self.centralWidget().layout()
        if isinstance(parent_layout, QHBoxLayout):
            # Remove existing panel widget
            parent_layout.removeWidget(self.buttons_panel)
            self.buttons_panel.setParent(None)
            # Build a fresh panel and insert
            self.buttons_panel = build_buttons_panel(self, self.button_registry)
            parent_layout.insertWidget(0, self.buttons_panel, 0)

    # ---- Handlers ----
    def _unique_id(self, base: str) -> str:
        n = self._id_counts.get(base, 0) + 1
        self._id_counts[base] = n
        return f"{base}{n}"

    def _add_circle(self):
        schema = [
            {"name": "center_x", "label": "Center X", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "center_y", "label": "Center Y", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "radius",   "label": "Radius",   "type": "float", "default": 1.0, "min": 0.1,  "max": 10.0, "step": 0.1},
        ]
        dlg = ParameterDialog("Create Circle", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("circle")
            circle = AnimatableCircle(**params)
            self.scene.add_object(obj_id, circle, style={"color": "#1f77b4", "linewidth": 2.5, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_polynomial(self):
        schema = [
            {"name": "expression", "label": "Polynomial f(x,y) =", "type": "str", "default": "y**2 - x**3 + x"},
            {"name": "x_min", "label": "x_min", "type": "float", "default": -5.0},
            {"name": "x_max", "label": "x_max", "type": "float", "default": 5.0},
            {"name": "y_min", "label": "y_min", "type": "float", "default": -5.0},
            {"name": "y_max", "label": "y_max", "type": "float", "default": 5.0},
            {"name": "resolution", "label": "Resolution", "type": "int", "default": 300, "min": 50, "max": 1000, "step": 50},
        ]
        dlg = ParameterDialog("Create Polynomial Curve", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("polycurve")
            obj = RenderablePolynomialCurve(
                expression=str(params["expression"]),
                x_min=float(params["x_min"]), x_max=float(params["x_max"]),
                y_min=float(params["y_min"]), y_max=float(params["y_max"]),
                resolution=int(params["resolution"]))
            self.scene.add_object(obj_id, obj, style={"color": "#bcbd22", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_rfunction(self):
        schema = [
            {"name": "f_expr", "label": "f(x,y) =", "type": "str", "default": "x**2 + y**2 - 1"},
            {"name": "g_expr", "label": "g(x,y) =", "type": "str", "default": "(x-0.5)**2 + y**2 - 1"},
            {"name": "op", "label": "Operation (union/intersection)", "type": "str", "default": "union"},
            {"name": "x_min", "label": "x_min", "type": "float", "default": -5.0},
            {"name": "x_max", "label": "x_max", "type": "float", "default": 5.0},
            {"name": "y_min", "label": "y_min", "type": "float", "default": -5.0},
            {"name": "y_max", "label": "y_max", "type": "float", "default": 5.0},
            {"name": "resolution", "label": "Resolution", "type": "int", "default": 300, "min": 50, "max": 1000, "step": 50},
        ]
        dlg = ParameterDialog("Create R-Function Curve", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            op = str(params.get("op", "union")).strip().lower()
            if op not in ("union", "intersection"):
                op = "union"
            obj_id = self._unique_id("rfunc")
            obj = RenderableRFunctionCurve(
                f_expr=str(params["f_expr"]), g_expr=str(params["g_expr"]), op=op,
                x_min=float(params["x_min"]), x_max=float(params["x_max"]),
                y_min=float(params["y_min"]), y_max=float(params["y_max"]),
                resolution=int(params["resolution"]))
            self.scene.add_object(obj_id, obj, style={"color": "#7f7f7f", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_ellipse(self):
        schema = [
            {"name": "center_x", "label": "Center X", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "center_y", "label": "Center Y", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "a", "label": "A (x radius)", "type": "float", "default": 2.0, "min": 0.1, "max": 20.0, "step": 0.1},
            {"name": "b", "label": "B (y radius)", "type": "float", "default": 1.0, "min": 0.1, "max": 20.0, "step": 0.1},
            {"name": "rotation_deg", "label": "Rotation (deg)", "type": "float", "default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0},
        ]
        dlg = ParameterDialog("Create Ellipse", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("ellipse")
            obj = AnimatableEllipse(**params)
            self.scene.add_object(obj_id, obj, style={"color": "#9467bd", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_line(self):
        schema = [
            {"name": "x1", "label": "x1", "type": "float", "default": -1.0},
            {"name": "y1", "label": "y1", "type": "float", "default": 0.0},
            {"name": "x2", "label": "x2", "type": "float", "default": 1.0},
            {"name": "y2", "label": "y2", "type": "float", "default": 0.0},
        ]
        dlg = ParameterDialog("Create Line", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("line")
            obj = AnimatableLine(**params)
            self.scene.add_object(obj_id, obj, style={"color": "#2ca02c", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_composite(self):
        # Select existing curve-like objects (exclude fields/regions)
        items: list[tuple[str, str]] = []
        for oid in self.scene.list_objects():
            o = self.scene.get_object(oid)
            if hasattr(o, "plot") and not isinstance(o, AnimatableCompositeCurve):
                items.append((oid, type(o).__name__))
        dlg = ObjectSelectorDialog("Select Curves for Composite", items, multi=True, parent=self)
        if dlg.exec() == QDialog.Accepted:
            sel = dlg.values()
            if len(sel) == 0:
                self.info_text.append("No objects selected for composite")
                return
            obj_id = self._unique_id("comp")
            comp = AnimatableCompositeCurve(sel)
            # Store minimal style; drawing uses member styles
            self.scene.add_object(obj_id, comp, style={"alpha": 1.0})
            self.info_text.append(f"Composite contains: {sel}")
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_conic(self):
        schema = [
            {"name": "A", "label": "A", "type": "float", "default": 1.0},
            {"name": "B", "label": "B", "type": "float", "default": 0.0},
            {"name": "C", "label": "C", "type": "float", "default": 1.0},
            {"name": "D", "label": "D", "type": "float", "default": 0.0},
            {"name": "E", "label": "E", "type": "float", "default": 0.0},
            {"name": "F", "label": "F", "type": "float", "default": -4.0},
            {"name": "x_min", "label": "x_min", "type": "float", "default": -5.0},
            {"name": "x_max", "label": "x_max", "type": "float", "default": 5.0},
            {"name": "y_min", "label": "y_min", "type": "float", "default": -5.0},
            {"name": "y_max", "label": "y_max", "type": "float", "default": 5.0},
            {"name": "resolution", "label": "Resolution", "type": "int", "default": 300, "min": 50, "max": 1000, "step": 50},
        ]
        dlg = ParameterDialog("Create Conic (A..F)", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("conic")
            obj = AnimatableConic(**params)  # type: ignore[arg-type]
            self.scene.add_object(obj_id, obj, style={"color": "#1f77b4", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_implicit(self):
        schema = [
            {"name": "expression", "label": "f(x,y) = 0", "type": "str", "default": "np.sin(x)+np.cos(y)-0.2"},
            {"name": "x_min", "label": "x_min", "type": "float", "default": -5.0},
            {"name": "x_max", "label": "x_max", "type": "float", "default": 5.0},
            {"name": "y_min", "label": "y_min", "type": "float", "default": -5.0},
            {"name": "y_max", "label": "y_max", "type": "float", "default": 5.0},
            {"name": "resolution", "label": "Resolution", "type": "int", "default": 300, "min": 50, "max": 1000, "step": 50},
        ]
        dlg = ParameterDialog("Create Implicit Curve", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("impl")
            obj = RenderableImplicitCurve(
                expression=str(params["expression"]),
                x_min=float(params["x_min"]), x_max=float(params["x_max"]),
                y_min=float(params["y_min"]), y_max=float(params["y_max"]),
                resolution=int(params["resolution"]))
            self.scene.add_object(obj_id, obj, style={"color": "#17becf", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_superellipse(self):
        schema = [
            {"name": "center_x", "label": "Center X", "type": "float", "default": 0.0},
            {"name": "center_y", "label": "Center Y", "type": "float", "default": 0.0},
            {"name": "a", "label": "A (x radius)", "type": "float", "default": 2.0},
            {"name": "b", "label": "B (y radius)", "type": "float", "default": 1.0},
            {"name": "n", "label": "Exponent n", "type": "float", "default": 2.5, "min": 0.2, "max": 20.0, "step": 0.1},
        ]
        dlg = ParameterDialog("Create Superellipse", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("superellipse")
            obj = AnimatableSuperellipse(**params)
            self.scene.add_object(obj_id, obj, style={"color": "#8c564b", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_procedural(self):
        schema = [
            {"name": "x_expr", "label": "x(t) =", "type": "str", "default": "np.cos(t)"},
            {"name": "y_expr", "label": "y(t) =", "type": "str", "default": "np.sin(t)"},
            {"name": "t_min", "label": "t min", "type": "float", "default": 0.0},
            {"name": "t_max", "label": "t max", "type": "float", "default": float(2*np.pi)},
            {"name": "samples", "label": "samples", "type": "int", "default": 400, "min": 50, "max": 5000, "step": 50},
        ]
        dlg = ParameterDialog("Create Procedural Curve", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("proc")
            obj = AnimatableProcedural(
                x_expr=str(params["x_expr"]), y_expr=str(params["y_expr"]),
                t_min=float(params["t_min"]), t_max=float(params["t_max"]), samples=int(params["samples"]))
            self.scene.add_object(obj_id, obj, style={"color": "#e377c2", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_trimmed_implicit(self):
        # Select an existing implicit-like curve to trim by new bounds
        items: list[tuple[str, str]] = []
        implicit_like = (RenderableImplicitCurve, AnimatableConic, AnimatableSuperellipse)
        for oid in self.scene.list_objects():
            o = self.scene.get_object(oid)
            if isinstance(o, implicit_like):
                items.append((oid, type(o).__name__))
        if not items:
            self.info_text.append("No implicit-like curves available to trim")
            return
        pick = ObjectSelectorDialog("Pick implicit curve to trim", items, multi=False, parent=self)
        if pick.exec() != QDialog.Accepted:
            return
        sel = pick.values()
        if not sel:
            return
        schema = [
            {"name": "x_min", "label": "x_min", "type": "float", "default": -2.0},
            {"name": "x_max", "label": "x_max", "type": "float", "default": 2.0},
            {"name": "y_min", "label": "y_min", "type": "float", "default": -2.0},
            {"name": "y_max", "label": "y_max", "type": "float", "default": 2.0},
            {"name": "resolution", "label": "Resolution", "type": "int", "default": 300, "min": 50, "max": 1000, "step": 50},
        ]
        dlg = ParameterDialog("Trim Implicit Curve (bounds)", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            base_id = sel[0]
            base = self.scene.get_object(base_id)
            obj_id = self._unique_id("trim")
            # Create a new implicit-like renderer that mirrors base but with new bounds
            if isinstance(base, AnimatableConic):
                p = base.get_parameters()
                obj = AnimatableConic(p["A"], p["B"], p["C"], p["D"], p["E"], p["F"],
                                      params["x_min"], params["x_max"], params["y_min"], params["y_max"], params["resolution"])  # type: ignore[arg-type]
                style = {"color": "#1f77b4", "linewidth": 2.0, "alpha": 0.9}
            elif isinstance(base, RenderableImplicitCurve):
                obj = RenderableImplicitCurve(base.expression, params["x_min"], params["x_max"], params["y_min"], params["y_max"], int(params["resolution"]))
                style = {"color": "#17becf", "linewidth": 2.0, "alpha": 0.9}
            elif isinstance(base, AnimatableSuperellipse):
                # Superellipse doesn't use bounds; emulate trimming by plotting within xlim/ylim via scene
                obj = base  # reuse (bounds controlled by viewer)
                style = {"color": "#8c564b", "linewidth": 2.0, "alpha": 0.9}
            else:
                return
            self.scene.add_object(obj_id, obj, style=style)
            self.info_text.append(f"Trimmed from {base_id}")
            self._append_object_info(obj_id)
            self._render_and_display()

    def _add_rectangle(self):
        schema = [
            {"name": "center_x", "label": "Center X", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "center_y", "label": "Center Y", "type": "float", "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.1},
            {"name": "width",    "label": "Width",    "type": "float", "default": 2.0, "min": 0.1,  "max": 10.0, "step": 0.1},
            {"name": "height",   "label": "Height",   "type": "float", "default": 1.2, "min": 0.1,  "max": 10.0, "step": 0.1},
        ]
        dlg = ParameterDialog("Create Rectangle", schema, self)
        if dlg.exec() == QDialog.Accepted:
            params = dlg.values()
            obj_id = self._unique_id("rect")
            rect = AnimatableRectangle(**params)
            self.scene.add_object(obj_id, rect, style={"color": "#d62728", "linewidth": 2.0, "alpha": 1.0})
            self._append_object_info(obj_id)
            self._render_and_display()

    def _clear_scene(self):
        for obj_id in self.scene.list_objects():
            # copy to avoid mutation during iteration
            pass
        for obj_id in list(self.scene.list_objects()):
            self.scene.remove_object(obj_id)
        self.info_text.append("\n-- Scene cleared --\n")
        # Reset view
        self.viewport.set_limits((-5.0, 5.0), (-5.0, 5.0))
        self._render_and_display()

    # ---- Zoom helpers ----
    def _apply_view(self, xmin: float, xmax: float, ymin: float, ymax: float, pad_ratio: float = 0.02):
        self.viewport.apply(xmin, xmax, ymin, ymax, pad_ratio=pad_ratio)
        self._render_and_display()

    def _zoom_in(self):
        # Zoom by 20% around center
        self.viewport.zoom_in(factor=0.8)
        self._render_and_display()
        self._update_status()

    def _zoom_out(self):
        # Zoom out by 25% around center
        self.viewport.zoom_out(factor=1/0.8)
        self._render_and_display()
        self._update_status()

    def _zoom_all(self):
        if not self.viewport.fit_to_scene(self.scene, pad_ratio=0.05):
            self.viewport.set_limits((-5.0, 5.0), (-5.0, 5.0))
        self._render_and_display()
        self._update_status()

    # ---- Pan helpers ----
    def _pan(self, frac_x: float, frac_y: float):
        # Shift view by given fraction of current width/height
        self.viewport.pan(frac_x=frac_x, frac_y=frac_y)
        self._render_and_display()
        self._update_status()

    def _pan_left(self):
        self._pan(frac_x=-0.2, frac_y=0.0)

    def _pan_right(self):
        self._pan(frac_x=0.2, frac_y=0.0)

    def _pan_up(self):
        self._pan(frac_x=0.0, frac_y=0.2)

    def _pan_down(self):
        self._pan(frac_x=0.0, frac_y=-0.2)

    def _scene_summary(self):
        objs = self.scene.list_objects()
        self.info_text.append(f"Scene has {len(objs)} objects: {objs}")

    # ---- Helpers ----
    def _append_object_info(self, obj_id: str):
        try:
            obj = self.scene.get_object(obj_id)
            style = self.scene.get_style(obj_id)
            lines = [
                f"Added: {obj_id}",
                f"  type: {type(obj).__name__}",
                f"  style: {style}",
            ]
            if hasattr(obj, "list_parameters") and hasattr(obj, "get_parameters"):
                lines.append(f"  parameters: {obj.get_parameters()}")
            self.info_text.append("\n".join(lines))
        except Exception as e:
            self.info_text.append(f"Error reading object info for {obj_id}: {e}")

    def _render_and_display(self):
        # Render scene to a temp file and display
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_path = tmp.name
            tmp.close()
            # Use external renderer with current viewport
            render_scene_to_png(self.scene, tmp_path, viewport=self.viewport)
            pix = QPixmap(tmp_path)
            if not pix.isNull():
                self.image_view.set_pixmap(pix)
            else:
                self.image_view.setText("Render failed (empty pixmap)")
            # Keep/remove temp file; removing saves disk clutter, but then pixmap owns data
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        except Exception as e:
            logger = get_logger()
            logger.error("Top-level render error:\n%s", traceback.format_exc())
            self.image_view.setText(f"Render error: {e}\nSee log: {LOG_PATH}")
        # Always refresh status bar after render attempt
        self._update_status()

    # ---- Status bar helpers ----
    def _on_mouse_move(self, x: float, y: float) -> None:
        self._cursor_world = (float(x), float(y))
        self._update_status()

    def _update_status(self) -> None:
        xmin, xmax = self.viewport.xlim
        ymin, ymax = self.viewport.ylim
        vp_text = f"x:[{xmin:.3f}, {xmax:.3f}] y:[{ymin:.3f}, {ymax:.3f}]"
        if self._cursor_world is not None:
            cx, cy = self._cursor_world
            cur_text = f"  |  cursor: ({cx:.3f}, {cy:.3f})"
        else:
            cur_text = ""
        self.statusBar().showMessage(f"viewport {vp_text}{cur_text}")


def main():
    app = QApplication(sys.argv)
    win = TwoTopMainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
