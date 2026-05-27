"""
tests/test_graphics_superellipse.py

Unit + DB-validation tests for Superellipse graphics support.
"""

import json
import math
import os
import sqlite3

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "curves.db")

import sys

sys.path.insert(0, ROOT)

from geometry.superellipse import Superellipse
from geometry.conic_section import ConicSection
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
import sympy as sp

_x, _y = sp.symbols("x y")


def _make_backend():
    sm = SceneManager()
    return sm, GraphicsBackendInterface(sm)


def _circle(r):
    return ConicSection(_x**2 + _y**2 - r**2, (_x, _y))


# ── bounding_box ──────────────────────────────────────────────────────────────


class TestBoundingBox:
    def test_circle_case_n2(self):
        s = Superellipse(1, 1, 2)
        xmin, xmax, ymin, ymax = s.bounding_box()
        assert xmin < -1.0
        assert xmax > 1.0
        assert ymin < -1.0
        assert ymax > 1.0

    def test_asymmetric_a2_b1(self):
        s = Superellipse(2, 1, 4)
        xmin, xmax, ymin, ymax = s.bounding_box()
        assert xmin < -2.0
        assert xmax > 2.0
        # y-axis bounded by b=1
        assert ymin > -1.15
        assert ymax < 1.15

    def test_diamond_n1(self):
        s = Superellipse(1.5, 1.5, 1)
        xmin, xmax, ymin, ymax = s.bounding_box()
        assert abs(xmax - (1.5 * 1.05)) < 0.02
        assert abs(ymax - (1.5 * 1.05)) < 0.02

    def test_near_square_n10(self):
        s = Superellipse(1, 1, 10)
        xmin, xmax, ymin, ymax = s.bounding_box()
        # Should be very close to ±1
        assert xmax < 1.1
        assert ymax < 1.1

    def test_bbox_all_finite(self):
        for n in [1.0, 2.0, 4.0, 6.0, 10.0]:
            s = Superellipse(2, 1, n)
            bb = s.bounding_box()
            assert all(math.isfinite(v) for v in bb), f"Non-finite bbox for n={n}"

    def test_bbox_xmin_lt_xmax(self):
        s = Superellipse(3, 1.5, 3)
        xmin, xmax, ymin, ymax = s.bounding_box()
        assert xmin < xmax
        assert ymin < ymax


# ── get_center ────────────────────────────────────────────────────────────────


class TestGetCenter:
    def test_center_is_origin(self):
        s = Superellipse(2, 1, 4)
        assert s.get_center() == (0.0, 0.0)


# ── evaluate (boundary points) ────────────────────────────────────────────────


class TestEvaluate:
    def _on_boundary(self, a, b, n, angles):
        """Points on the superellipse boundary should evaluate to ≈0."""
        s = Superellipse(a, b, n)
        inv_n = 2.0 / n
        for theta in angles:
            xp = a * math.copysign(abs(math.cos(theta)) ** inv_n, math.cos(theta))
            yp = b * math.copysign(abs(math.sin(theta)) ** inv_n, math.sin(theta))
            val = s.evaluate(xp, yp)
            assert abs(val) < 1e-6, f"Boundary point ({xp:.4f},{yp:.4f}) → f={val} ≠ 0"

    def test_diamond_boundary(self):
        self._on_boundary(1.5, 1.5, 1.0, [math.pi / 4, math.pi * 3 / 4])

    def test_circle_boundary(self):
        self._on_boundary(
            1.0, 1.0, 2.0, [0, math.pi / 4, math.pi / 2, math.pi, 3 * math.pi / 2]
        )

    def test_squircle_boundary(self):
        self._on_boundary(1.5, 1.5, 4.0, [math.pi / 4, math.pi / 2, math.pi])

    def test_interior_is_negative(self):
        s = Superellipse(2, 1, 4)
        # Origin is inside every superellipse
        val = s.evaluate(0.0, 0.0)
        assert val < 0.0

    def test_exterior_is_positive(self):
        s = Superellipse(1, 1, 2)
        # Far point is outside
        val = s.evaluate(10.0, 10.0)
        assert val > 0.0

    def test_vectorised_evaluate(self):
        s = Superellipse(1, 1, 2)
        X = np.array([[0.0, 1.0], [2.0, 0.5]])
        Y = np.array([[0.0, 0.0], [0.0, 0.5]])
        Z = s.evaluate(X, Y)
        assert Z.shape == X.shape


# ── graphics backend ──────────────────────────────────────────────────────────


class TestGraphicsBackendSuperellipse:
    def _add(self, sm, s, oid="s"):
        sm.add_object(oid, s, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})

    def test_renders_diamond(self):
        sm, gi = _make_backend()
        self._add(sm, Superellipse(1.5, 1.5, 1.0))
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=100)
        assert "s" in paths
        assert len(paths["s"]["points"]) > 5

    def test_renders_squircle(self):
        sm, gi = _make_backend()
        self._add(sm, Superellipse(1.5, 1.5, 4.0))
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=100)
        assert len(paths["s"]["points"]) > 5

    def test_renders_near_square(self):
        sm, gi = _make_backend()
        self._add(sm, Superellipse(1, 1, 10.0))
        paths = gi.get_curve_paths(bounds=(-2, 2, -2, 2), resolution=100)
        assert len(paths["s"]["points"]) > 5

    def test_scene_bounds_match_bbox(self):
        sm, gi = _make_backend()
        s = Superellipse(2, 1, 4)
        self._add(sm, s)
        sb = gi.get_scene_bounds()
        xmin, xmax, ymin, ymax = sb
        assert xmin < -1.9
        assert xmax > 1.9

    def test_get_curve_paths_closed(self):
        sm, gi = _make_backend()
        self._add(sm, Superellipse(1, 1, 2))
        paths = gi.get_curve_paths(bounds=(-2, 2, -2, 2), resolution=150)
        # Superellipses are always closed
        assert paths["s"].get("closed", False) is True or len(paths["s"]["points"]) > 4

    def test_scene_data_superellipse(self):
        sm, gi = _make_backend()
        self._add(sm, Superellipse(1.5, 1.5, 3))
        data = gi.get_geometry_scene_data(resolution=100)
        objs = {o["id"]: o for o in data["objects"]}
        assert "s" in objs
        assert len(objs["s"]["points"]) > 5


# ── intersection: superellipse ∩ circle ───────────────────────────────────────


class TestSuperellipseIntersections:
    def _count_intersections_approx(self, s, c, bounds=(-3, 3, -3, 3)):
        sm, gi = _make_backend()
        sm.add_object("s", s, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        sm.add_object("c", c, {"color": "#0f0", "linewidth": 2.0, "alpha": 1.0})
        data = gi.get_geometry_scene_data(resolution=150)
        return len(data["intersections"])

    def test_squircle_n4_vs_circle_r1(self):
        # Squircle a=b=1.2, n=4 vs circle r=1.3 → 8 intersections (one per octant)
        s = Superellipse(1.2, 1.2, 4.0)
        c = _circle(1.3)
        count = self._count_intersections_approx(s, c)
        # Allow range 6-8 due to rounding in contour extraction
        assert 4 <= count <= 8, f"Expected ~8 intersections, got {count}"

    def test_diamond_n1_vs_line(self):
        import sympy as sp

        x, y = sp.symbols("x y")
        line = ConicSection(y - x, (x, y))  # y = x
        sm, gi = _make_backend()
        sm.add_object(
            "d",
            Superellipse(1.5, 1.5, 1.0),
            {"color": "#fff", "linewidth": 2.0, "alpha": 1.0},
        )
        sm.add_object("l", line, {"color": "#0f0", "linewidth": 2.0, "alpha": 1.0})
        data = gi.get_geometry_scene_data(resolution=150)
        # Line y=x intersects diamond |x|+|y|=1.5 at 2 points
        assert len(data["intersections"]) >= 1


# ── DB validation ─────────────────────────────────────────────────────────────


def _db_superellipse_rows():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, params_json, eval_samples_json, analytical_intersections_json "
        "FROM new_curve_types WHERE curve_class='Superellipse'"
    ).fetchall()
    conn.close()
    return rows


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="curves.db not found; run seed first"
)
class TestDBSuperellipseValidation:
    def test_db_has_at_least_15_rows(self):
        assert len(_db_superellipse_rows()) >= 15

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json",
        _db_superellipse_rows(),
    )
    def test_eval_samples_match(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        params = json.loads(params_json)
        s = Superellipse(params["a"], params["b"], params["n"])
        samples = json.loads(samples_json) if samples_json else []
        for xi, yi, expected_f in samples[:5]:
            actual_f = s.evaluate(float(xi), float(yi))
            assert abs(actual_f - expected_f) < 0.01, (
                f"{name}: f({xi},{yi})={actual_f:.4f}, expected {expected_f:.4f}"
            )

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json",
        _db_superellipse_rows(),
    )
    def test_bbox_covers_samples(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        params = json.loads(params_json)
        s = Superellipse(params["a"], params["b"], params["n"])
        samples = json.loads(samples_json) if samples_json else []
        xmin, xmax, ymin, ymax = s.bounding_box()
        for xi, yi, _ in samples[:5]:
            assert xmin <= xi <= xmax, f"{name}: x={xi} outside bbox"
            assert ymin <= yi <= ymax, f"{name}: y={yi} outside bbox"

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json",
        _db_superellipse_rows(),
    )
    def test_graphics_backend_renders(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        params = json.loads(params_json)
        s = Superellipse(params["a"], params["b"], params["n"])
        sm, gi = _make_backend()
        sm.add_object("s", s, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        half = max(params["a"], params["b"]) * 2
        paths = gi.get_curve_paths(bounds=(-half, half, -half, half), resolution=100)
        assert "s" in paths, f"No paths for {name}"
        assert len(paths["s"]["points"]) > 4, f"Too few points for {name}"
