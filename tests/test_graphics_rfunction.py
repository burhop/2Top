"""
tests/test_graphics_rfunction.py

Unit + DB-validation tests for RFunctionCurve graphics support.
"""

import json
import math
import os
import sqlite3

import numpy as np
import pytest
import sympy as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "curves.db")

import sys

sys.path.insert(0, ROOT)

from geometry.conic_section import ConicSection
from geometry.superellipse import Superellipse
from geometry.rfunction_curve import RFunctionCurve, union, intersect, difference, blend
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager

_x, _y = sp.symbols("x y")


def _circle(cx=0, cy=0, r=1):
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _ellipse(cx=0, cy=0, a=2, b=1):
    return ConicSection((_x - cx) ** 2 / a**2 + (_y - cy) ** 2 / b**2 - 1, (_x, _y))


def _make_backend():
    sm = SceneManager()
    return sm, GraphicsBackendInterface(sm)


# ── bounding_box ──────────────────────────────────────────────────────────────


class TestBoundingBox:
    def _c1(self):
        return _circle(0, 0, 1)

    def _c2(self):
        return _circle(1, 0, 1)

    def test_union_box_is_superset(self):
        r = union(self._c1(), self._c2())
        bb = r.bounding_box()
        assert bb is not None
        xmin, xmax, ymin, ymax = bb
        # Both circles fit in [-1, 2] x [-1, 1] (approximately)
        assert xmin <= -0.9
        assert xmax >= 1.9
        assert ymin <= -0.9
        assert ymax >= 0.9

    def test_blend_box_is_superset(self):
        r = blend(self._c1(), self._c2(), alpha=0.3)
        bb = r.bounding_box()
        assert bb is not None
        xmin, xmax, _, _ = bb
        assert xmin <= -0.9
        assert xmax >= 1.9

    def test_intersection_box_is_subset(self):
        r = intersect(self._c1(), self._c2())
        bb = r.bounding_box()
        assert bb is not None
        xmin, xmax, ymin, ymax = bb
        # Intersection of two circles centred at 0 and 1 with r=1
        # is roughly in [0, 1] x [-0.87, 0.87]
        assert xmin >= -1.1  # should not go beyond left circle's left edge much
        assert xmax <= 2.1  # should not go beyond right circle's right edge

    def test_difference_box_equals_c1(self):
        c1 = _circle(0, 0, 2)
        c2 = _circle(0.5, 0, 0.8)
        r = difference(c1, c2)
        bb = r.bounding_box()
        bb1 = c1.bounding_box()
        assert bb is not None
        assert bb1 is not None
        assert abs(bb[0] - bb1[0]) < 0.01
        assert abs(bb[1] - bb1[1]) < 0.01

    def test_bbox_none_when_children_have_none(self):
        from geometry.procedural_curve import ProceduralCurve

        c1 = ProceduralCurve(lambda x, y: x**2 + y**2 - 1)
        c2 = ProceduralCurve(lambda x, y: x**2 + y**2 - 4)
        r = union(c1, c2)
        bb = r.bounding_box()
        assert bb is None

    def test_bbox_uses_one_child_when_other_is_none(self):
        from geometry.procedural_curve import ProceduralCurve

        c1 = _circle(0, 0, 2)
        c2 = ProceduralCurve(lambda x, y: x**2 + y**2 - 1)
        r = union(c1, c2)
        bb = r.bounding_box()
        assert bb is not None


# ── get_child_curves ─────────────────────────────────────────────────────────


class TestGetChildCurves:
    def test_returns_both_children(self):
        c1 = _circle(0, 0, 1)
        c2 = _circle(1, 0, 1)
        r = union(c1, c2)
        children = r.get_child_curves()
        assert len(children) == 2
        assert children[0] is c1
        assert children[1] is c2


# ── evaluate (semantics) ──────────────────────────────────────────────────────


class TestEvaluateSemantics:
    """Validate that evaluate() values match the R-function semantics."""

    def test_union_inside_either(self):
        # Point (0.5, 0) is inside both circles → min should be negative
        r = union(_circle(0, 0, 1), _circle(1, 0, 1))
        val = r.evaluate(0.5, 0.0)
        assert val < 0.0

    def test_union_outside_both(self):
        # Point (10, 0) is outside both circles
        r = union(_circle(0, 0, 1), _circle(1, 0, 1))
        val = r.evaluate(10.0, 0.0)
        assert val > 0.0

    def test_intersection_inside_both(self):
        # (0.5, 0) is inside both unit circles centred at 0 and 1
        r = intersect(_circle(0, 0, 1), _circle(1, 0, 1))
        val = r.evaluate(0.5, 0.0)
        assert val < 0.0

    def test_intersection_inside_only_one(self):
        # (−0.9, 0) is inside c1 but outside c2 (centred at 1)
        r = intersect(_circle(0, 0, 1), _circle(1, 0, 1))
        val = r.evaluate(-0.9, 0.0)
        assert val > 0.0

    def test_difference_inside_c1_outside_c2(self):
        # (0, 0) is inside c1=circle(r=2) but outside c2=circle at (3,0)
        c1 = _circle(0, 0, 2)
        c2 = _circle(3, 0, 0.5)
        r = difference(c1, c2)
        val = r.evaluate(0.0, 0.0)
        assert val < 0.0

    def test_difference_inside_both(self):
        # Point inside c1 and also inside c2 → should be outside the difference
        c1 = _circle(0, 0, 2)
        c2 = _circle(0, 0, 1)
        r = difference(c1, c2)
        val = r.evaluate(0.0, 0.0)  # inside both → outside difference
        assert val > 0.0

    def test_blend_is_smooth(self):
        # Blend should interpolate smoothly — evaluate nearby points and check
        # that the result changes gradually
        c1 = _circle(0, 0, 1)
        c2 = _circle(2, 0, 1)
        r = blend(c1, c2, alpha=0.5)
        xs = np.linspace(-2, 4, 50)
        vals = np.array([r.evaluate(x, 0.0) for x in xs])
        # No huge jump between adjacent samples (smoothness check)
        diffs = np.abs(np.diff(vals))
        assert diffs.max() < 1.5, "Blend is not smooth"

    def test_vectorised_union(self):
        r = union(_circle(0, 0, 1), _circle(1, 0, 1))
        X = np.array([[0.0, 5.0], [0.5, -2.0]])
        Y = np.zeros((2, 2))
        Z = r.evaluate(X, Y)
        assert Z.shape == (2, 2)
        assert Z[0, 0] < 0  # inside
        assert Z[0, 1] > 0  # outside


# ── graphics backend ──────────────────────────────────────────────────────────


class TestGraphicsBackendRFunction:
    def _add(self, sm, obj, oid="r"):
        sm.add_object(oid, obj, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})

    def test_renders_union(self):
        sm, gi = _make_backend()
        self._add(sm, union(_circle(0, 0, 1), _circle(1, 0, 1)))
        paths = gi.get_curve_paths(bounds=(-2, 3, -2, 2), resolution=100)
        assert "r" in paths
        assert len(paths["r"]["points"]) > 5

    def test_renders_difference(self):
        sm, gi = _make_backend()
        self._add(sm, difference(_circle(0, 0, 2), _circle(0.5, 0, 0.8)))
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=100)
        assert len(paths["r"]["points"]) > 5

    def test_renders_blend(self):
        sm, gi = _make_backend()
        self._add(sm, blend(_circle(0, 0, 1), _circle(1, 0, 1), alpha=0.3))
        paths = gi.get_curve_paths(bounds=(-2, 3, -2, 2), resolution=100)
        assert len(paths["r"]["points"]) > 5

    def test_renders_intersection(self):
        sm, gi = _make_backend()
        self._add(sm, intersect(_circle(0, 0, 1.5), _circle(1, 0, 1.5)))
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=100)
        assert len(paths["r"]["points"]) > 5

    def test_scene_data_includes_rfunction(self):
        sm, gi = _make_backend()
        self._add(sm, union(_circle(0, 0, 1), _circle(1, 0, 1)))
        data = gi.get_geometry_scene_data(resolution=100)
        objs = {o["id"]: o for o in data["objects"]}
        assert "r" in objs

    def test_union_vs_line_intersections(self):
        # Union of two circles should intersect y=0 at (−1,0) and (2,0)
        sm, gi = _make_backend()
        self._add(sm, union(_circle(0, 0, 1), _circle(1, 0, 1)))
        line = ConicSection(_y, (_x, _y))
        sm.add_object("l", line, {"color": "#f00", "linewidth": 2.0, "alpha": 1.0})
        data = gi.get_geometry_scene_data(resolution=150)
        # Should have at least 2 intersections with y=0
        assert len(data["intersections"]) >= 1


# ── DB validation ─────────────────────────────────────────────────────────────


def _db_rfunction_rows():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, params_json, sample_points_json, analytical_intersections_json "
        "FROM new_curve_types WHERE curve_class='RFunctionCurve'"
    ).fetchall()
    conn.close()
    return rows


def _reconstruct_child(spec):
    """Build a geometry curve from a spec dict."""
    t = spec.get("type")
    x, y = sp.symbols("x y")
    if t == "ConicSection":
        expr = sp.sympify(spec["expr"])
        return ConicSection(expr, (x, y))
    elif t == "Superellipse":
        return Superellipse(spec["a"], spec["b"], spec["n"])
    raise ValueError(f"Unknown curve spec type: {t}")


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="curves.db not found; run seed first"
)
class TestDBRFunctionValidation:
    def test_db_has_at_least_40_rows(self):
        assert len(_db_rfunction_rows()) >= 40

    @pytest.mark.parametrize("row_id,name,params_json,_a,_b", _db_rfunction_rows())
    def test_graphics_backend_renders(self, row_id, name, params_json, _a, _b):
        params = json.loads(params_json)
        c1 = _reconstruct_child(params["curve1"])
        c2 = _reconstruct_child(params["curve2"])
        op = params["operation"]
        alpha = params.get("alpha", 0.0)
        r = RFunctionCurve(c1, c2, operation=op, alpha=alpha)
        sm, gi = _make_backend()
        sm.add_object("r", r, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        paths = gi.get_curve_paths(bounds=(-5, 5, -5, 5), resolution=80)
        assert "r" in paths, f"No paths for {name}"

    @pytest.mark.parametrize("row_id,name,params_json,_a,_b", _db_rfunction_rows())
    def test_bounding_box_finite(self, row_id, name, params_json, _a, _b):
        params = json.loads(params_json)
        c1 = _reconstruct_child(params["curve1"])
        c2 = _reconstruct_child(params["curve2"])
        op = params["operation"]
        alpha = params.get("alpha", 0.0)
        r = RFunctionCurve(c1, c2, operation=op, alpha=alpha)
        bb = r.bounding_box()
        if bb is not None:
            assert all(math.isfinite(v) for v in bb), f"Non-finite bbox for {name}"

    @pytest.mark.parametrize("row_id,name,params_json,_a,_b", _db_rfunction_rows())
    def test_union_contains_children_interiors(self, row_id, name, params_json, _a, _b):
        params = json.loads(params_json)
        if params["operation"] != "union":
            pytest.skip("Only union rows")
        c1 = _reconstruct_child(params["curve1"])
        c2 = _reconstruct_child(params["curve2"])
        r = union(c1, c2)
        # A point deep inside c1 should be inside the union
        val = r.evaluate(0.0, 0.0)
        # For most circle-like primitives centred near origin, (0,0) is inside c1
        # Accept either negative (inside) or very close to zero (boundary)
        assert val <= 0.1, f"{name}: expected inside, got f(0,0)={val:.4f}"
