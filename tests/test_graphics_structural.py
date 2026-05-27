"""
Structural / numerical test suite for the Graphics Backend curve-path pipeline.

Tests the DATA STRUCTURES returned by ``get_curve_paths()`` (and related
scene-bound helpers) – NOT pixel output.  This is the highest-ROI testing
strategy because it validates:
  * data integrity  (no NaN, no empty, correct dimensionality)
  * topology        (open vs. closed curves)
  * geometric bounds
  * point counts & resolution behaviour
  * on-curve accuracy
  * endpoint snapping
  * multi-object scenes
  * scene-level bounds
  * edge / degenerate cases
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest
import numpy as np
import sympy as sp

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import RegionFactory
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve

_x, _y = sp.symbols("x y")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_backend_with(*objects):
    """Build a (SceneManager, GraphicsBackendInterface) from (id, obj, style) tuples.

    Parameters
    ----------
    *objects : tuple
        Each element is ``(obj_id: str, obj, style: dict)``.

    Returns
    -------
    (SceneManager, GraphicsBackendInterface)
    """
    sm = SceneManager()
    for obj_id, obj, style in objects:
        sm.add_object(obj_id, obj)
        sm.set_style(obj_id, style)
    backend = GraphicsBackendInterface(sm)
    return sm, backend


def _circle(cx=0, cy=0, r=1):
    """Create a circle ConicSection centred at (cx, cy) with radius *r*."""
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _ellipse(cx=0, cy=0, a=3, b=2):
    """Create an axis-aligned ellipse ConicSection."""
    return ConicSection((_x - cx) ** 2 / a**2 + (_y - cy) ** 2 / b**2 - 1, (_x, _y))


def _parabola():
    """Create a standard upward parabola  y − x² = 0."""
    return ConicSection(_y - _x**2, (_x, _y))


def _line_vertical(x_val=1):
    """Create a vertical line  x − x_val = 0  as an ImplicitCurve."""
    return ImplicitCurve(_x - x_val, (_x, _y))


# Shared scene bounds used by many tests.
_DEFAULT_BOUNDS = (-5, 5, -5, 5)
_DEFAULT_RESOLUTION = 200


def _get_all_points(curve_data_entry):
    """Return an np.ndarray of shape (N, 2) from a curve data dict entry.

    Tries ``paths`` first (flattened), then ``points``.
    """
    paths = curve_data_entry.get("paths", [])
    if paths:
        flat = [pt for path in paths for pt in path]
        if flat:
            return np.array(flat)
    pts = curve_data_entry.get("points", [])
    if pts:
        return np.array(pts)
    return np.empty((0, 2))


# ====================================================================
# 1. Data Integrity
# ====================================================================


class TestCurvePathDataIntegrity:
    """Verify that extracted curve data contains finite, well-shaped points."""

    def test_no_nan_in_circle_points(self):
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["c"])
        assert pts.size > 0, "Circle should produce points"
        assert np.all(np.isfinite(pts)), "Circle points must all be finite"

    def test_no_nan_in_parabola_points(self):
        para = _parabola()
        _, backend = _make_backend_with(("p", para, {"color": "red"}))
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["p"])
        assert pts.size > 0, "Parabola should produce points"
        assert np.all(np.isfinite(pts)), "Parabola points must all be finite"

    def test_no_nan_in_ellipse_points(self):
        ell = _ellipse()
        _, backend = _make_backend_with(("e", ell, {"color": "green"}))
        data = backend.get_curve_paths(
            bounds=(-5, 5, -5, 5), resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["e"])
        assert pts.size > 0, "Ellipse should produce points"
        assert np.all(np.isfinite(pts)), "Ellipse points must all be finite"

    def test_no_empty_paths(self):
        """get_curve_paths should never return empty points for valid objects."""
        factory = RegionFactory()
        circle_region = factory.create_circle_region((0, 0), 1.0)
        _, backend = _make_backend_with(("cr", circle_region, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=(-3, 3, -3, 3), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["cr"]
        pts = _get_all_points(entry)
        assert len(pts) > 0, "Valid circle region must produce non-empty paths"

    def test_points_are_2d(self):
        """Every point must have exactly 2 coordinates."""
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["c"])
        assert pts.ndim == 2 and pts.shape[1] == 2, (
            f"Expected shape (N, 2), got {pts.shape}"
        )

    def test_all_objects_present_in_output(self):
        """Every scene object must appear in the output dict."""
        c = _circle()
        p = _parabola()
        e = _ellipse()
        _, backend = _make_backend_with(
            ("circ", c, {"color": "blue"}),
            ("para", p, {"color": "red"}),
            ("elli", e, {"color": "green"}),
        )
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        for key in ("circ", "para", "elli"):
            assert key in data, f"Object '{key}' missing from output"


# ====================================================================
# 2. Topology (open / closed)
# ====================================================================


class TestCurveTopology:
    """Check that the ``closed`` flag matches the expected topology."""

    def test_circle_is_closed(self):
        circle = _circle(r=2)
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=(-4, 4, -4, 4), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["c"]
        # Either the 'closed' flag is True OR the first/last points coincide
        pts = _get_all_points(entry)
        is_topologically_closed = entry.get("closed", False)
        if not is_topologically_closed and len(pts) >= 2:
            is_topologically_closed = np.allclose(pts[0], pts[-1], atol=0.15)
        assert is_topologically_closed, "Circle should be detected as closed"

    def test_parabola_is_open(self):
        para = _parabola()
        _, backend = _make_backend_with(("p", para, {"color": "red"}))
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        entry = data["p"]
        assert not entry.get("closed", False), "Parabola should be detected as open"

    def test_ellipse_is_closed(self):
        ell = _ellipse(a=2, b=1)
        _, backend = _make_backend_with(("e", ell, {"color": "green"}))
        data = backend.get_curve_paths(
            bounds=(-4, 4, -4, 4), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["e"]
        pts = _get_all_points(entry)
        is_closed = entry.get("closed", False)
        if not is_closed and len(pts) >= 2:
            is_closed = np.allclose(pts[0], pts[-1], atol=0.15)
        assert is_closed, "Ellipse should be closed"

    def test_line_is_open(self):
        line = _line_vertical(1)
        _, backend = _make_backend_with(("l", line, {"color": "gray"}))
        data = backend.get_curve_paths(
            bounds=_DEFAULT_BOUNDS, resolution=_DEFAULT_RESOLUTION
        )
        entry = data["l"]
        assert not entry.get("closed", False), "A vertical line should be open"

    def test_rectangle_region_is_closed(self):
        factory = RegionFactory()
        rect = factory.create_rectangle_region((0, 0), (2, 3))
        _, backend = _make_backend_with(("r", rect, {"color": "orange"}))
        data = backend.get_curve_paths(
            bounds=(-3, 5, -3, 6), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["r"]
        pts = _get_all_points(entry)
        is_closed = entry.get("closed", False)
        if not is_closed and len(pts) >= 2:
            is_closed = np.allclose(pts[0], pts[-1], atol=0.3)
        assert is_closed, "Rectangle boundary should be closed"

    def test_triangle_region_is_closed(self):
        factory = RegionFactory()
        tri = factory.create_triangle_region([(0, 0), (4, 0), (2, 3)])
        _, backend = _make_backend_with(("t", tri, {"color": "purple"}))
        data = backend.get_curve_paths(
            bounds=(-2, 6, -2, 5), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["t"]
        pts = _get_all_points(entry)
        is_closed = entry.get("closed", False)
        if not is_closed and len(pts) >= 2:
            is_closed = np.allclose(pts[0], pts[-1], atol=0.3)
        assert is_closed, "Triangle boundary should be closed"


# ====================================================================
# 3. Bounds
# ====================================================================


class TestCurveBounds:
    """Verify that reported curve bounds match geometric expectations."""

    def test_circle_bounds_match_radius(self):
        r = 2.0
        circle = _circle(cx=0, cy=0, r=r)
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=(-5, 5, -5, 5), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["c"]
        bnd = entry.get("bounds")
        assert bnd is not None and len(bnd) == 4
        tol = 0.3
        assert abs(bnd[0] - (-r)) < tol, f"xmin {bnd[0]} too far from {-r}"
        assert abs(bnd[1] - r) < tol, f"xmax {bnd[1]} too far from {r}"
        assert abs(bnd[2] - (-r)) < tol, f"ymin {bnd[2]} too far from {-r}"
        assert abs(bnd[3] - r) < tol, f"ymax {bnd[3]} too far from {r}"

    def test_ellipse_bounds_match_semi_axes(self):
        a, b = 3.0, 2.0
        ell = _ellipse(cx=0, cy=0, a=a, b=b)
        _, backend = _make_backend_with(("e", ell, {"color": "green"}))
        data = backend.get_curve_paths(
            bounds=(-5, 5, -5, 5), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["e"]
        bnd = entry.get("bounds")
        assert bnd is not None and len(bnd) == 4
        tol = 0.3
        assert abs(bnd[0] - (-a)) < tol, f"xmin {bnd[0]} too far from {-a}"
        assert abs(bnd[1] - a) < tol, f"xmax {bnd[1]} too far from {a}"
        assert abs(bnd[2] - (-b)) < tol, f"ymin {bnd[2]} too far from {-b}"
        assert abs(bnd[3] - b) < tol, f"ymax {bnd[3]} too far from {b}"

    def test_curve_bounds_within_scene_bounds(self):
        """Curve bounds should be within (or close to) the requested scene bounds."""
        circle = _circle(cx=0, cy=0, r=1)
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        scene_bounds = (-3, 3, -3, 3)
        data = backend.get_curve_paths(
            bounds=scene_bounds, resolution=_DEFAULT_RESOLUTION
        )
        entry = data["c"]
        bnd = entry.get("bounds")
        assert bnd is not None
        margin = 1.0  # contour can exceed requested bounds slightly
        assert bnd[0] >= scene_bounds[0] - margin
        assert bnd[1] <= scene_bounds[1] + margin
        assert bnd[2] >= scene_bounds[2] - margin
        assert bnd[3] <= scene_bounds[3] + margin


# ====================================================================
# 4. Point Count
# ====================================================================


class TestCurvePointCount:
    """Verify that enough points are generated and that resolution scaling works."""

    def test_circle_has_sufficient_points(self):
        circle = _circle(r=2)
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(bounds=(-4, 4, -4, 4), resolution=200)
        pts = _get_all_points(data["c"])
        assert len(pts) > 30, f"Expected >30 points for a circle, got {len(pts)}"

    def test_higher_resolution_gives_more_points(self):
        circle = _circle(r=2)
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data_low = backend.get_curve_paths(bounds=(-4, 4, -4, 4), resolution=100)
        data_high = backend.get_curve_paths(bounds=(-4, 4, -4, 4), resolution=400)
        pts_low = _get_all_points(data_low["c"])
        pts_high = _get_all_points(data_high["c"])
        assert len(pts_high) >= len(pts_low), (
            f"Higher resolution ({len(pts_high)}) should give >= points than lower ({len(pts_low)})"
        )


# ====================================================================
# 5. Points on Curve (algebraic accuracy)
# ====================================================================


class TestPointsOnCurve:
    """Every rendered point should approximately satisfy the implicit equation."""

    @staticmethod
    def _max_residual(expr, pts):
        """Evaluate the sympy expression at every point and return the max |f(x,y)|."""
        f = sp.lambdify((_x, _y), expr, modules="numpy")
        xs, ys = pts[:, 0], pts[:, 1]
        vals = np.abs(f(xs, ys))
        return float(np.nanmax(vals))

    def test_circle_points_satisfy_equation(self):
        r = 2
        expr = _x**2 + _y**2 - r**2
        circle = ConicSection(expr, (_x, _y))
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(
            bounds=(-4, 4, -4, 4), resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["c"])
        assert len(pts) > 0
        max_res = self._max_residual(expr, pts)
        assert max_res < 0.5, f"Max residual on circle: {max_res}"

    def test_ellipse_points_satisfy_equation(self):
        a, b = 3.0, 2.0
        expr = _x**2 / a**2 + _y**2 / b**2 - 1
        ell = ConicSection(expr, (_x, _y))
        _, backend = _make_backend_with(("e", ell, {"color": "green"}))
        data = backend.get_curve_paths(
            bounds=(-5, 5, -5, 5), resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["e"])
        assert len(pts) > 0
        max_res = self._max_residual(expr, pts)
        assert max_res < 0.5, f"Max residual on ellipse: {max_res}"

    def test_parabola_points_satisfy_equation(self):
        expr = _y - _x**2
        para = ConicSection(expr, (_x, _y))
        _, backend = _make_backend_with(("p", para, {"color": "red"}))
        data = backend.get_curve_paths(
            bounds=(-3, 3, -1, 9), resolution=_DEFAULT_RESOLUTION
        )
        pts = _get_all_points(data["p"])
        assert len(pts) > 0
        max_res = self._max_residual(expr, pts)
        assert max_res < 0.5, f"Max residual on parabola: {max_res}"


# ====================================================================
# 6. Endpoint Snapping
# ====================================================================


class TestEndpointSnapping:
    """For open curves with known endpoints, verify snapping is close."""

    def test_open_curve_endpoints_match_analytical(self):
        """A trimmed half-circle should have endpoints near (−r, 0) and (r, 0)."""
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

        r = 2.0
        base = _circle(cx=0, cy=0, r=r)
        # Keep upper half only
        upper_half = TrimmedImplicitCurve(
            base,
            lambda px, py: py >= 0,
            endpoints=[(-r, 0), (r, 0)],
        )
        _, backend = _make_backend_with(("h", upper_half, {"color": "purple"}))
        data = backend.get_curve_paths(
            bounds=(-4, 4, -4, 4), resolution=_DEFAULT_RESOLUTION
        )
        entry = data["h"]
        pts = _get_all_points(entry)
        if len(pts) < 2:
            pytest.skip("Half-circle produced too few points to test snapping")

        first, last = pts[0], pts[-1]
        # One end should be near (-r, 0) and the other near (r, 0)
        tol = 0.5
        endpoints_expected = [np.array([-r, 0.0]), np.array([r, 0.0])]
        actual_ends = [first, last]

        # Check that both expected endpoints are close to at least one actual end
        for exp in endpoints_expected:
            dists = [np.linalg.norm(act - exp) for act in actual_ends]
            assert min(dists) < tol, (
                f"Expected endpoint {exp} not found among actual ends {actual_ends} "
                f"(min dist = {min(dists):.4f})"
            )


# ====================================================================
# 7. Multi-Object Scene
# ====================================================================


class TestMultiObjectScene:
    """Verify correct behaviour when the scene has several heterogeneous objects."""

    @staticmethod
    def _build_three_object_scene():
        factory = RegionFactory()
        circle_region = factory.create_circle_region((0, 0), 1.0)
        rect_region = factory.create_rectangle_region((2, 2), (4, 4))
        tri_region = factory.create_triangle_region([(5, 0), (7, 0), (6, 2)])
        return _make_backend_with(
            ("circle", circle_region, {"color": "blue", "linewidth": 2}),
            ("rect", rect_region, {"color": "red", "linewidth": 1}),
            ("tri", tri_region, {"color": "green", "linewidth": 1}),
        )

    def test_three_objects_all_present(self):
        _, backend = self._build_three_object_scene()
        data = backend.get_curve_paths(
            bounds=(-3, 9, -3, 6), resolution=_DEFAULT_RESOLUTION
        )
        assert len(data) == 3, f"Expected 3 entries, got {len(data)}"
        for key in ("circle", "rect", "tri"):
            assert key in data

    def test_objects_have_style_data(self):
        _, backend = self._build_three_object_scene()
        data = backend.get_curve_paths(
            bounds=(-3, 9, -3, 6), resolution=_DEFAULT_RESOLUTION
        )
        for key in ("circle", "rect", "tri"):
            style = data[key].get("style")
            assert style is not None, f"Object '{key}' missing style"
            assert isinstance(style, dict), f"Style for '{key}' is not a dict"
            assert len(style) > 0, f"Style for '{key}' is empty"

    def test_objects_have_valid_bounds(self):
        _, backend = self._build_three_object_scene()
        data = backend.get_curve_paths(
            bounds=(-3, 9, -3, 6), resolution=_DEFAULT_RESOLUTION
        )
        for key in ("circle", "rect", "tri"):
            bnd = data[key].get("bounds")
            assert bnd is not None and len(bnd) == 4, f"Bad bounds for '{key}': {bnd}"
            assert all(np.isfinite(v) for v in bnd), (
                f"Bounds for '{key}' contain non-finite values"
            )


# ====================================================================
# 8. Scene Bounds
# ====================================================================


class TestSceneBounds:
    """Test the ``get_scene_bounds`` helper."""

    def test_scene_bounds_enclose_all_objects(self):
        factory = RegionFactory()
        c = factory.create_circle_region((0, 0), 1.0)
        r = factory.create_rectangle_region((3, 3), (5, 5))
        _, backend = _make_backend_with(
            ("c", c, {"color": "blue"}),
            ("r", r, {"color": "red"}),
        )
        scene_bnd = backend.get_scene_bounds(padding=0.2)
        # Per-object bounds from curve paths
        curve_data = backend.get_curve_paths(bounds=scene_bnd, resolution=100)
        for obj_id, entry in curve_data.items():
            obj_bnd = entry.get("bounds")
            if obj_bnd is None:
                continue
            # Object bounds should be inside scene bounds (with tolerance)
            margin = 1.0
            assert obj_bnd[0] >= scene_bnd[0] - margin, f"{obj_id} xmin out of scene"
            assert obj_bnd[1] <= scene_bnd[1] + margin, f"{obj_id} xmax out of scene"
            assert obj_bnd[2] >= scene_bnd[2] - margin, f"{obj_id} ymin out of scene"
            assert obj_bnd[3] <= scene_bnd[3] + margin, f"{obj_id} ymax out of scene"

    def test_scene_bounds_finite(self):
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        bnd = backend.get_scene_bounds()
        assert all(np.isfinite(v) for v in bnd), f"Scene bounds not finite: {bnd}"

    def test_scene_bounds_positive_range(self):
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        xmin, xmax, ymin, ymax = backend.get_scene_bounds()
        assert xmax > xmin, f"xmax ({xmax}) must be > xmin ({xmin})"
        assert ymax > ymin, f"ymax ({ymax}) must be > ymin ({ymin})"

    def test_empty_scene_returns_defaults(self):
        sm = SceneManager()
        backend = GraphicsBackendInterface(sm)
        bnd = backend.get_scene_bounds()
        # Should return fallback bounds, not crash
        assert len(bnd) == 4
        assert all(np.isfinite(v) for v in bnd)
        xmin, xmax, ymin, ymax = bnd
        assert xmax > xmin
        assert ymax > ymin


# ====================================================================
# 9. Edge Cases
# ====================================================================


class TestEdgeCases:
    """Degenerate / extreme inputs should not crash the pipeline."""

    def test_single_point_curve(self):
        """Degenerate curve x² + y² = 0 (only the origin) should not crash."""
        degenerate = ConicSection(_x**2 + _y**2, (_x, _y))
        _, backend = _make_backend_with(("d", degenerate, {"color": "black"}))
        # Just ensure no exception is raised
        data = backend.get_curve_paths(bounds=(-2, 2, -2, 2), resolution=50)
        assert "d" in data  # entry should exist even if empty

    def test_very_small_bounds(self):
        """Requesting very small bounds shouldn't crash."""
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(bounds=(-0.01, 0.01, -0.01, 0.01), resolution=50)
        assert "c" in data

    def test_very_large_bounds(self):
        """Requesting very large bounds shouldn't crash."""
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        data = backend.get_curve_paths(bounds=(-1000, 1000, -1000, 1000), resolution=50)
        assert "c" in data

    def test_zero_resolution_handled(self):
        """Resolution of 0 or 1 should not crash (or be handled gracefully)."""
        circle = _circle()
        _, backend = _make_backend_with(("c", circle, {"color": "blue"}))
        for res in (0, 1):
            try:
                data = backend.get_curve_paths(bounds=_DEFAULT_BOUNDS, resolution=res)
                # If it returns successfully, just verify the key exists
                assert "c" in data
            except (ValueError, ZeroDivisionError):
                # Acceptable: raising an explicit error for degenerate resolution
                pass
