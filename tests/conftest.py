"""
Shared pytest fixtures for the 2Top test suite.

Provides reusable SceneManager configurations, geometry objects,
GraphicsBackendInterface instances, and visual-testing utilities
that any test module under ``tests/`` can request by name.
"""

from __future__ import annotations

import sys

import os

import pytest
import sympy as sp

# Ensure the project root is on sys.path so that top-level packages
# (geometry, scene_management, graphics_backend, visual_tests) are importable
# even when pytest is invoked from an arbitrary working directory.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scene_management.scene_manager import SceneManager
from graphics_backend.graphics_interface import GraphicsBackendInterface
from visual_tests.utils.test_objects import RegionFactory, CurveFactory
from visual_tests.utils.baseline_manager import VisualBaselineManager
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve

# Canonical sympy symbols shared across fixtures
_x, _y = sp.symbols("x y")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scene_with(objects: dict, styles: dict | None = None) -> SceneManager:
    """Create a SceneManager and populate it with the given objects and styles.

    Parameters
    ----------
    objects : dict
        Mapping of ``{object_id: geometry_object}``.
    styles : dict or None
        Optional mapping of ``{object_id: style_dict}``.

    Returns
    -------
    SceneManager
    """
    sm = SceneManager()
    for obj_id, obj in objects.items():
        sm.add_object(obj_id, obj)
    if styles:
        for obj_id, style in styles.items():
            sm.set_style(obj_id, style)
    return sm


# ---------------------------------------------------------------------------
# Scene fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def circle_scene() -> SceneManager:
    """SceneManager containing a unit circle centred at the origin.

    Object ID: ``'circle'``
    Geometry : circle with centre (0, 0) and radius 1
    Style    : blue, linewidth 2
    """
    factory = RegionFactory()
    circle = factory.create_circle_region((0, 0), 1.0)
    return _make_scene_with(
        {"circle": circle},
        {"circle": {"color": "blue", "linewidth": 2}},
    )


@pytest.fixture
def ellipse_scene() -> SceneManager:
    """SceneManager containing an ellipse at the origin.

    Object ID: ``'ellipse'``
    Geometry : ellipse with semi-axes a=3, b=2
    Style    : purple, linewidth 2
    """
    factory = CurveFactory()
    ellipse = factory.create_ellipse((0, 0), a=3, b=2)
    return _make_scene_with(
        {"ellipse": ellipse},
        {"ellipse": {"color": "purple", "linewidth": 2}},
    )


@pytest.fixture
def rectangle_scene() -> SceneManager:
    """SceneManager containing a rectangle region.

    Object ID: ``'rectangle'``
    Geometry : rectangle with corners (-2, -1) and (2, 1)
    Style    : red, fill_alpha 0.3
    """
    factory = RegionFactory()
    rectangle = factory.create_rectangle_region((-2, -1), (2, 1))
    return _make_scene_with(
        {"rectangle": rectangle},
        {"rectangle": {"color": "red", "fill_alpha": 0.3}},
    )


@pytest.fixture
def triangle_scene() -> SceneManager:
    """SceneManager containing a triangle region.

    Object ID: ``'triangle'``
    Geometry : triangle with vertices (-2, -1.5), (2, -1.5), (0, 2)
    Style    : green, linewidth 1
    """
    factory = RegionFactory()
    triangle = factory.create_triangle_region([(-2, -1.5), (2, -1.5), (0, 2)])
    return _make_scene_with(
        {"triangle": triangle},
        {"triangle": {"color": "green", "linewidth": 1}},
    )


@pytest.fixture
def multi_object_scene() -> SceneManager:
    """SceneManager with the standard three-object scene (circle + rectangle + triangle).

    Object IDs : ``'circle'``, ``'rectangle'``, ``'triangle'``
    Circle     : centre (0, 0), radius 1, blue
    Rectangle  : corners (1, 1.25) – (3, 2.75), red
    Triangle   : vertices (0, 0), (1, 0), (0.5, 1), green
    """
    factory = RegionFactory()
    circle = factory.create_circle_region((0, 0), 1.0)
    rectangle = factory.create_rectangle_region((1, 1.25), (3, 2.75))
    triangle = factory.create_triangle_region([(0, 0), (1, 0), (0.5, 1)])
    return _make_scene_with(
        {"circle": circle, "rectangle": rectangle, "triangle": triangle},
        {
            "circle": {"color": "blue", "linewidth": 2},
            "rectangle": {"color": "red", "fill_alpha": 0.5},
            "triangle": {"color": "green", "linewidth": 1},
        },
    )


@pytest.fixture
def parabola_scene() -> SceneManager:
    """SceneManager with an open parabola curve  y − x² = 0.

    Object ID: ``'parabola'``
    Geometry : ``ImplicitCurve`` for the expression  y − x²
    Style    : orange, linewidth 2
    """
    parabola_expr = _y - _x**2
    parabola = ImplicitCurve(parabola_expr, (_x, _y))
    return _make_scene_with(
        {"parabola": parabola},
        {"parabola": {"color": "orange", "linewidth": 2}},
    )


@pytest.fixture
def two_curve_scene() -> SceneManager:
    """SceneManager with two intersecting curves: a unit circle and a diagonal line.

    Object IDs : ``'circle'``, ``'line'``
    Circle     : x² + y² − 1 = 0  (unit circle at origin)
    Line       : y − x = 0         (diagonal line through origin)
    """
    circle_expr = _x**2 + _y**2 - 1
    circle = ConicSection(circle_expr, (_x, _y))

    line_expr = _y - _x
    line = ImplicitCurve(line_expr, (_x, _y))

    return _make_scene_with(
        {"circle": circle, "line": line},
        {
            "circle": {"color": "blue", "linewidth": 2},
            "line": {"color": "red", "linewidth": 1},
        },
    )


# ---------------------------------------------------------------------------
# Backend / utility fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def graphics_backend(multi_object_scene) -> GraphicsBackendInterface:
    """A ``GraphicsBackendInterface`` wrapping the standard multi-object scene.

    Depends on the ``multi_object_scene`` fixture.
    """
    return GraphicsBackendInterface(multi_object_scene)


@pytest.fixture
def standard_bounds() -> tuple:
    """Standard viewing bounds used across many tests: ``(-5, 5, -5, 5)``."""
    return (-5, 5, -5, 5)


@pytest.fixture
def baseline_manager() -> VisualBaselineManager:
    """A ``VisualBaselineManager`` instance for visual regression testing.

    Reads configuration from the ``VISUAL_TEST_MODE``,
    ``VISUAL_DIFF_THRESHOLD``, ``VISUAL_OUTPUT_DIR``,
    ``VISUAL_BASELINE_DIR``, and ``VISUAL_DIFF_DIR`` environment variables
    (see ``visual_tests/utils/baseline_manager.py``).
    """
    return VisualBaselineManager()
