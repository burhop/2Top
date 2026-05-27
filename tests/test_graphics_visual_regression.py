"""
Visual Regression Test Suite

Integrates the VisualBaselineManager into pytest for pixel-diff testing
of rendered scene images.

Usage:
    # Capture golden baselines (first run):
    VISUAL_TEST_MODE=baseline pytest tests/test_graphics_visual_regression.py -v

    # Compare against baselines (subsequent runs):
    VISUAL_TEST_MODE=compare pytest tests/test_graphics_visual_regression.py -v

    # Normal test runs skip these tests automatically.
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest
import numpy as np
import sympy as sp

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import RegionFactory, CurveFactory
from visual_tests.utils.baseline_manager import (
    get_baseline_manager,
)
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve

_x, _y = sp.symbols("x y")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def baseline_mgr():
    """Provide a VisualBaselineManager, skipping when not activated."""
    mgr = get_baseline_manager()
    if not mgr.is_active():
        pytest.skip("Visual tests require VISUAL_TEST_MODE=baseline or compare")
    return mgr


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _render_scene(sm, bounds=(-5, 5, -5, 5), resolution=(8, 6), dpi=120):
    """
    Render a SceneManager's contents onto a matplotlib figure and return it.

    Uses the GraphicsBackendInterface to extract curve paths and region data,
    then plots them with deterministic styling.
    """
    backend = GraphicsBackendInterface(sm)
    fig, ax = plt.subplots(figsize=resolution, dpi=dpi)

    xmin, xmax, ymin, ymax = bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # --- Render filled regions first (underneath curves) ---
    region_data = backend.get_region_data(bounds=bounds, resolution=(100, 100))
    if region_data:
        rx = np.linspace(xmin, xmax, 100)
        ry = np.linspace(ymin, ymax, 100)
        RX, RY = np.meshgrid(rx, ry)
        for obj_id, data in region_data.items():
            if data.get("inside_mask") is not None:
                style = sm.get_style(obj_id) or {}
                fill_color = style.get("fill_color", style.get("color", "blue"))
                fill_alpha = style.get("fill_alpha", 0.25)
                mask = np.array(data["inside_mask"], dtype=bool)
                ax.contourf(
                    RX,
                    RY,
                    mask.astype(float),
                    levels=[0.5, 1.5],
                    colors=[fill_color],
                    alpha=fill_alpha,
                )

    # --- Render curve boundaries ---
    curve_data = backend.get_curve_paths(bounds=bounds, resolution=300)
    for obj_id, data in curve_data.items():
        paths = data.get("paths", [])
        if not paths and data.get("points"):
            paths = [data["points"]]
        style = sm.get_style(obj_id) or {}
        color = style.get("color", "blue")
        linewidth = style.get("linewidth", 2)
        alpha = style.get("alpha", 1.0)
        for path in paths:
            if path and len(path) >= 2:
                pts = np.array(path)
                ax.plot(
                    pts[:, 0], pts[:, 1], color=color, linewidth=linewidth, alpha=alpha
                )

    ax.set_title("")  # deterministic – no title text variance
    fig.tight_layout()
    return fig


def _circle(cx=0, cy=0, r=1):
    """Convenience helper for creating a ConicSection circle."""
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestVisualRegression:
    """
    Visual regression tests.

    Each test builds a deterministic scene, renders it to a figure, and
    hands it to the VisualBaselineManager for capture or comparison.
    """

    # -- Single-shape tests ------------------------------------------------

    def test_unit_circle_render(self, baseline_mgr):
        """Render a unit circle centred at the origin."""
        sm = SceneManager()
        factory = RegionFactory()
        circle = factory.create_circle_region((0, 0), 1.0)
        sm.add_object("circle", circle)
        sm.set_style("circle", {"color": "blue", "linewidth": 2})

        fig = _render_scene(sm, bounds=(-3, 3, -3, 3))
        result = baseline_mgr.save_figure(fig, "test_unit_circle_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    def test_ellipse_render(self, baseline_mgr):
        """Render an ellipse with semi-axes (3, 2)."""
        sm = SceneManager()
        ellipse = CurveFactory.create_ellipse((0, 0), a=3, b=2)
        sm.add_object("ellipse", ellipse)
        sm.set_style("ellipse", {"color": "purple", "linewidth": 2})

        fig = _render_scene(sm, bounds=(-5, 5, -4, 4))
        result = baseline_mgr.save_figure(fig, "test_ellipse_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    def test_rectangle_region_render(self, baseline_mgr):
        """Render a filled rectangle region."""
        sm = SceneManager()
        factory = RegionFactory()
        rect = factory.create_rectangle_region((-2, -1), (2, 1))
        sm.add_object("rectangle", rect)
        sm.set_style(
            "rectangle",
            {
                "color": "red",
                "fill_color": "salmon",
                "fill_alpha": 0.35,
                "linewidth": 2,
            },
        )

        fig = _render_scene(sm, bounds=(-4, 4, -3, 3))
        result = baseline_mgr.save_figure(fig, "test_rectangle_region_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    def test_triangle_region_render(self, baseline_mgr):
        """Render a filled triangle region."""
        sm = SceneManager()
        factory = RegionFactory()
        triangle = factory.create_triangle_region([(-2, -1), (2, -1), (0, 2)])
        sm.add_object("triangle", triangle)
        sm.set_style(
            "triangle",
            {
                "color": "green",
                "fill_color": "lightgreen",
                "fill_alpha": 0.3,
                "linewidth": 2,
            },
        )

        fig = _render_scene(sm, bounds=(-4, 4, -3, 4))
        result = baseline_mgr.save_figure(fig, "test_triangle_region_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    # -- Composite scene ---------------------------------------------------

    def test_multi_object_scene_render(self, baseline_mgr):
        """Render a scene with a circle, rectangle, and triangle together."""
        sm = SceneManager()
        factory = RegionFactory()

        circle = factory.create_circle_region((0, 0), 1.5)
        sm.add_object("circle", circle)
        sm.set_style(
            "circle",
            {
                "color": "blue",
                "fill_color": "lightblue",
                "fill_alpha": 0.2,
                "linewidth": 2,
            },
        )

        rect = factory.create_rectangle_region((1, 0.5), (3, 2))
        sm.add_object("rectangle", rect)
        sm.set_style(
            "rectangle",
            {
                "color": "red",
                "fill_color": "lightyellow",
                "fill_alpha": 0.25,
                "linewidth": 2,
            },
        )

        tri = factory.create_triangle_region([(-3, -2), (0, -2), (-1.5, 1)])
        sm.add_object("triangle", tri)
        sm.set_style(
            "triangle",
            {
                "color": "green",
                "fill_color": "lightgreen",
                "fill_alpha": 0.25,
                "linewidth": 2,
            },
        )

        fig = _render_scene(sm, bounds=(-5, 5, -4, 4))
        result = baseline_mgr.save_figure(fig, "test_multi_object_scene_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    # -- Open curves -------------------------------------------------------

    def test_parabola_render(self, baseline_mgr):
        """Render an upward-opening parabola."""
        sm = SceneManager()
        parabola = CurveFactory.create_parabola(
            vertex=(0, -2), direction="up", scale=0.5
        )
        sm.add_object("parabola", parabola)
        sm.set_style("parabola", {"color": "darkorange", "linewidth": 2})

        fig = _render_scene(sm, bounds=(-5, 5, -4, 6))
        result = baseline_mgr.save_figure(fig, "test_parabola_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")

    # -- Intersecting curves -----------------------------------------------

    def test_two_intersecting_curves_render(self, baseline_mgr):
        """Render a circle and a line that intersect."""
        sm = SceneManager()

        # Unit circle
        circle = _circle(0, 0, 2)
        sm.add_object("circle", circle)
        sm.set_style("circle", {"color": "blue", "linewidth": 2})

        # Diagonal line: y = x  →  y - x = 0
        line = ImplicitCurve(_y - _x, (_x, _y))
        sm.add_object("line", line)
        sm.set_style("line", {"color": "red", "linewidth": 1.5})

        fig = _render_scene(sm, bounds=(-4, 4, -4, 4))
        result = baseline_mgr.save_figure(fig, "test_two_intersecting_curves_render")
        plt.close(fig)

        assert result.status in ("baseline_saved", "matched", "saved")
