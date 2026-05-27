"""
tests/test_graphics_parametric_segment.py

Unit + DB-validation tests for ParametricSegment graphics support.
"""

import json
import math
import os
import sqlite3

import numpy as np
import pytest

# ── project root ─────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "curves.db")

import sys

sys.path.insert(0, ROOT)

from geometry.parametric_segment import (
    ParametricSegment,
    create_line_segment,
    create_ellipse_arc,
    create_parabola_segment,
)
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_backend():
    sm = SceneManager()
    return sm, GraphicsBackendInterface(sm)


def _make_circle_arc(cx=0, cy=0, r=1, t0=0.0, t1=2 * math.pi):
    return ParametricSegment(
        lambda t: cx + r * math.cos(t),
        lambda t: cy + r * math.sin(t),
        t0,
        t1,
        name=f"CircleArc(r={r})",
    )


def _make_sine_arch():
    return ParametricSegment(
        lambda t: t,
        lambda t: math.sin(t),
        0.0,
        math.pi,
        name="SineArch",
    )


def _make_lissajous():
    return ParametricSegment(
        lambda t: math.sin(3 * t),
        lambda t: math.sin(2 * t),
        0.0,
        2 * math.pi,
        name="Lissajous32",
    )


# ── get_polyline_approximation ────────────────────────────────────────────────


class TestGetPolylineApproximation:
    def test_returns_list_of_2d_points(self):
        seg = _make_circle_arc(r=1, t1=math.pi / 2)
        pts = seg.get_polyline_approximation(resolution=100)
        assert isinstance(pts, list)
        assert len(pts) > 10
        assert all(len(p) == 2 for p in pts)

    def test_circle_arc_q1_start_end(self):
        seg = _make_circle_arc(r=2, t0=0.0, t1=math.pi / 2)
        pts = seg.get_polyline_approximation(resolution=200)
        # Start ≈ (2, 0), End ≈ (0, 2)
        assert abs(pts[0][0] - 2.0) < 0.01
        assert abs(pts[0][1] - 0.0) < 0.01
        assert abs(pts[-1][0] - 0.0) < 0.01
        assert abs(pts[-1][1] - 2.0) < 0.01

    def test_full_circle_returns_many_points(self):
        seg = _make_circle_arc(r=1)
        pts = seg.get_polyline_approximation(resolution=300)
        assert len(pts) == 300  # all finite for a circle

    def test_lissajous_x_range(self):
        seg = _make_lissajous()
        pts = seg.get_polyline_approximation(resolution=400)
        xs = [p[0] for p in pts]
        assert min(xs) < -0.9
        assert max(xs) > 0.9

    def test_sine_arch_y_range(self):
        seg = _make_sine_arch()
        pts = seg.get_polyline_approximation(resolution=200)
        ys = [p[1] for p in pts]
        assert min(ys) >= -0.01  # arch is above 0
        assert max(ys) > 0.99  # peak near 1

    def test_sine_arch_spot_check(self):
        seg = _make_sine_arch()
        pts = seg.get_polyline_approximation(resolution=1000)
        # At t=pi/2, x=pi/2, y=1 — find nearest sample
        target_x = math.pi / 2
        nearest = min(pts, key=lambda p: abs(p[0] - target_x))
        assert abs(nearest[1] - 1.0) < 0.01

    def test_resolution_parameter(self):
        seg = _make_circle_arc()
        pts50 = seg.get_polyline_approximation(resolution=50)
        pts300 = seg.get_polyline_approximation(resolution=300)
        assert len(pts300) > len(pts50)

    def test_bounds_param_ignored(self):
        # bounds parameter is accepted but ignored for parametric curves
        seg = _make_sine_arch()
        pts_no_bounds = seg.get_polyline_approximation(resolution=100)
        pts_with_bounds = seg.get_polyline_approximation(
            bounds=(-10, 10, -5, 5), resolution=100
        )
        assert len(pts_no_bounds) == len(pts_with_bounds)

    def test_line_segment_is_straight(self):
        seg = create_line_segment((0, 0), (1, 1))
        pts = seg.get_polyline_approximation(resolution=50)
        # All points should satisfy y ≈ x
        for p in pts:
            assert abs(p[1] - p[0]) < 1e-10

    def test_parabola_segment_y_positive(self):
        seg = create_parabola_segment(1, 0, 0, -2, 2)
        pts = seg.get_polyline_approximation(resolution=100)
        ys = [p[1] for p in pts]
        assert min(ys) >= -0.01  # y=x² is non-negative

    def test_ellipse_arc(self):
        seg = create_ellipse_arc((0, 0), 3, 1, 0, math.pi)
        pts = seg.get_polyline_approximation(resolution=200)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert max(xs) > 2.9
        assert min(xs) < -2.9
        assert all(y >= -0.01 for y in ys)  # upper half only


# ── bounding_box ──────────────────────────────────────────────────────────────


class TestBoundingBox:
    def test_full_circle_bbox(self):
        seg = _make_circle_arc(r=2)
        bb = seg.bounding_box()
        xmin, xmax, ymin, ymax = bb
        assert xmin < -2.0
        assert xmax > 2.0
        assert ymin < -2.0
        assert ymax > 2.0

    def test_q1_arc_bbox_nonneg(self):
        seg = _make_circle_arc(r=1, t0=0.0, t1=math.pi / 2)
        xmin, xmax, ymin, ymax = seg.bounding_box()
        assert xmin >= -0.1  # mostly in positive quadrant
        assert ymin >= -0.1

    def test_sine_arch_bbox_height(self):
        seg = _make_sine_arch()
        xmin, xmax, ymin, ymax = seg.bounding_box()
        assert ymax > 0.9
        assert ymin > -0.1  # arch is above zero

    def test_bbox_is_finite(self):
        seg = _make_lissajous()
        bb = seg.bounding_box()
        assert all(math.isfinite(v) for v in bb)

    def test_bbox_xmin_lt_xmax(self):
        seg = _make_circle_arc(r=1.5)
        xmin, xmax, ymin, ymax = seg.bounding_box()
        assert xmin < xmax
        assert ymin < ymax


# ── is_closed ─────────────────────────────────────────────────────────────────


class TestIsClosed:
    def test_full_circle_is_closed(self):
        seg = _make_circle_arc(r=1, t0=0.0, t1=2 * math.pi)
        assert seg.is_closed(tolerance=1e-4)

    def test_half_circle_not_closed(self):
        seg = _make_circle_arc(r=1, t0=0.0, t1=math.pi)
        assert not seg.is_closed(tolerance=1e-4)

    def test_lissajous_is_closed(self):
        seg = _make_lissajous()
        assert seg.is_closed(tolerance=1e-4)

    def test_line_segment_not_closed(self):
        seg = create_line_segment((0, 0), (1, 1))
        assert not seg.is_closed(tolerance=1e-4)


# ── is_periodic flag ─────────────────────────────────────────────────────────


class TestIsPeriodicFlag:
    def test_default_not_periodic(self):
        seg = _make_circle_arc()
        assert seg.is_periodic is False

    def test_set_periodic(self):
        seg = ParametricSegment(
            lambda t: math.sin(t),
            lambda t: math.cos(t),
            0.0,
            2 * math.pi,
            is_periodic=True,
        )
        assert seg.is_periodic is True


# ── graphics backend integration ──────────────────────────────────────────────


class TestGraphicsBackendParametric:
    def test_get_curve_paths_non_empty(self):
        sm, gi = _make_backend()
        seg = _make_circle_arc(r=2)
        sm.add_object("arc", seg, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=150)
        assert "arc" in paths
        pts = paths["arc"]["points"]
        assert len(pts) > 10

    def test_scene_bounds_finite(self):
        sm, gi = _make_backend()
        seg = _make_sine_arch()
        sm.add_object("sine", seg, {"color": "#f00", "linewidth": 2.0, "alpha": 1.0})
        bounds = gi.get_scene_bounds()
        assert all(math.isfinite(v) for v in bounds)

    def test_scene_bounds_contain_curve(self):
        sm, gi = _make_backend()
        seg = _make_circle_arc(r=3)
        sm.add_object("c", seg, {"color": "#0f0", "linewidth": 2.0, "alpha": 1.0})
        xmin, xmax, ymin, ymax = gi.get_scene_bounds()
        assert xmin < -2.9
        assert xmax > 2.9
        assert ymin < -2.9
        assert ymax > 2.9

    def test_lissajous_paths_present(self):
        sm, gi = _make_backend()
        seg = _make_lissajous()
        sm.add_object("liss", seg, {"color": "#00f", "linewidth": 2.0, "alpha": 1.0})
        data = gi.get_geometry_scene_data(resolution=100)
        objs = {o["id"]: o for o in data["objects"]}
        assert "liss" in objs
        assert len(objs["liss"]["points"]) > 10

    def test_multiple_parametric_in_scene(self):
        sm, gi = _make_backend()
        sm.add_object(
            "c",
            _make_circle_arc(r=2),
            {"color": "#fff", "linewidth": 2.0, "alpha": 1.0},
        )
        sm.add_object(
            "s", _make_sine_arch(), {"color": "#aaa", "linewidth": 2.0, "alpha": 1.0}
        )
        paths = gi.get_curve_paths(bounds=(-4, 4, -3, 3), resolution=150)
        assert len(paths) == 2


# ── DB validation ─────────────────────────────────────────────────────────────


@pytest.mark.skipif(not os.path.exists(DB_PATH), reason="curves.db not found")
def _db_parametric_rows():
    """Load all ParametricSegment rows from the DB."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, params_json, sample_points_json, analytical_intersections_json "
        "FROM new_curve_types WHERE curve_class='ParametricSegment'"
    ).fetchall()
    conn.close()
    return rows


_KNOWN_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "pi": math.pi,
    "exp": math.exp,
    "asin": math.asin,
    "acos": math.acos,
    "atan2": math.atan2,
    "log": math.log,
    "abs": abs,
}


def _build_segment_from_db(params):
    """Reconstruct a ParametricSegment from a DB params dict."""
    ns = {**_KNOWN_FUNCTIONS, "t": 0}
    x_fn = eval(f"lambda t: {params['x_expr']}", ns)
    y_fn = eval(f"lambda t: {params['y_expr']}", ns)
    return ParametricSegment(x_fn, y_fn, params["t_start"], params["t_end"])


@pytest.mark.skipif(
    not os.path.exists(DB_PATH),
    reason="curves.db not found; run seed_new_curve_types.py first",
)
class TestDBParametricValidation:
    def _rows(self):
        return _db_parametric_rows()

    def test_db_has_at_least_20_rows(self):
        assert len(self._rows()) >= 20

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,_",
        _db_parametric_rows() if os.path.exists(DB_PATH) else [],
    )
    def test_polyline_from_db(self, row_id, name, params_json, samples_json, _):
        params = json.loads(params_json)
        seg = _build_segment_from_db(params)
        pts = seg.get_polyline_approximation(resolution=200)
        assert len(pts) > 10, f"Too few points for {name}"

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json",
        _db_parametric_rows() if os.path.exists(DB_PATH) else [],
    )
    def test_sample_points_on_curve(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        """Verify that the stored sample points actually lie on the parametric curve."""
        params = json.loads(params_json)
        samples = json.loads(samples_json) if samples_json else []
        seg = _build_segment_from_db(params)
        # Check that every stored sample is close to the polyline
        polyline = np.array(seg.get_polyline_approximation(resolution=500))
        for px, py in samples[:5]:  # spot-check first 5
            dists = np.sqrt((polyline[:, 0] - px) ** 2 + (polyline[:, 1] - py) ** 2)
            assert dists.min() < 0.1, f"Sample ({px},{py}) too far from {name} polyline"

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json",
        _db_parametric_rows() if os.path.exists(DB_PATH) else [],
    )
    def test_bbox_covers_samples(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        """Bounding box must contain all sample points."""
        params = json.loads(params_json)
        samples = json.loads(samples_json) if samples_json else []
        if not samples:
            return
        seg = _build_segment_from_db(params)
        xmin, xmax, ymin, ymax = seg.bounding_box()
        for px, py in samples[:5]:
            assert xmin <= px <= xmax, f"{name}: x={px} outside bbox [{xmin},{xmax}]"
            assert ymin <= py <= ymax, f"{name}: y={py} outside bbox [{ymin},{ymax}]"
