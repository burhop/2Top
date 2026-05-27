"""
tests/test_graphics_procedural.py

Unit + DB-validation tests for ProceduralCurve graphics support.
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

from geometry.procedural_curve import ProceduralCurve
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager


def _make_backend():
    sm = SceneManager()
    return sm, GraphicsBackendInterface(sm)


def _sin_curve():
    return ProceduralCurve(
        lambda x, y: math.sin(x) - y,
        name="sin(x)-y",
        is_periodic=True,
    )


def _gaussian_curve():
    return ProceduralCurve(
        lambda x, y: math.exp(-(x**2)) - y,
        name="gaussian",
        is_periodic=False,
    )


def _tanh_curve():
    return ProceduralCurve(
        lambda x, y: math.tanh(x) - y,
        name="tanh(x)-y",
        is_periodic=False,
    )


# ── evaluate ──────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_sin_curve_on_boundary(self):
        c = _sin_curve()
        # At (pi/6, 0.5): sin(pi/6) - 0.5 = 0
        val = c.evaluate(math.pi / 6, 0.5)
        assert abs(val) < 1e-6

    def test_sin_curve_scalar(self):
        c = _sin_curve()
        val = c.evaluate(0.0, 0.0)
        assert abs(val) < 1e-12  # sin(0)−0=0

    def test_gaussian_on_boundary(self):
        c = _gaussian_curve()
        # At (0, 1): exp(0) - 1 = 0
        val = c.evaluate(0.0, 1.0)
        assert abs(val) < 1e-12

    def test_tanh_on_boundary(self):
        c = _tanh_curve()
        val = c.evaluate(0.0, 0.0)
        assert abs(val) < 1e-12  # tanh(0)-0=0

    def test_vectorised_sin(self):
        c = ProceduralCurve(
            lambda x, y: np.sin(x) - y, name="vec_sin", is_periodic=True
        )
        X = np.array([[0.0, math.pi / 2], [math.pi, 0.0]])
        Y = np.array([[0.0, 1.0], [0.0, 0.0]])
        Z = c.evaluate(X, Y)
        assert Z.shape == (2, 2)
        assert abs(Z[0, 0]) < 1e-10  # sin(0)-0=0
        assert abs(Z[0, 1]) < 1e-10  # sin(pi/2)-1=0

    def test_outside_positive(self):
        c = _gaussian_curve()
        # At (0, 2): exp(0)-2=-1 < 0 (below the curve in output-space sense)
        # Actually: gaussian outputs f=exp(-x²)-y; at y=2, f=-1
        val = c.evaluate(0.0, 2.0)
        assert val < 0.0

    def test_inside_negative(self):
        c = _sin_curve()
        # At (0, 1): sin(0)-1 = -1
        val = c.evaluate(0.0, 1.0)
        assert abs(val - (-1.0)) < 1e-10


# ── gradient ──────────────────────────────────────────────────────────────────


class TestGradient:
    def test_sin_curve_gradient_scalar(self):
        # f(x,y)=sin(x)-y → df/dx=cos(x), df/dy=-1
        c = _sin_curve()
        gx, gy = c.gradient(math.pi / 4, 0.0)
        assert abs(gx - math.cos(math.pi / 4)) < 1e-4
        assert abs(gy - (-1.0)) < 1e-4

    def test_gaussian_gradient_at_origin(self):
        # f=exp(-x^2)-y → df/dx=-2x*exp(-x^2), df/dy=-1
        c = _gaussian_curve()
        gx, gy = c.gradient(0.0, 0.5)
        assert abs(gx - 0.0) < 1e-4
        assert abs(gy - (-1.0)) < 1e-4

    def test_gradient_vectorised(self):
        c = ProceduralCurve(
            lambda x, y: np.sin(x) - y, name="vec_sin", is_periodic=True
        )
        X = np.array([0.0, math.pi / 4])
        Y = np.array([0.0, 0.0])
        gx, gy = c.gradient(X, Y)
        assert abs(gx[0] - 1.0) < 1e-4  # cos(0)=1
        assert abs(gy[0] - (-1.0)) < 1e-4


# ── is_periodic ───────────────────────────────────────────────────────────────


class TestIsPeriodicAttribute:
    def test_default_not_periodic(self):
        c = ProceduralCurve(lambda x, y: x + y)
        assert c.is_periodic is False

    def test_set_periodic_true(self):
        c = ProceduralCurve(lambda x, y: math.sin(x) - y, is_periodic=True)
        assert c.is_periodic is True

    def test_is_periodic_affects_backend_detection(self):
        sm, gi = _make_backend()
        c = ProceduralCurve(
            lambda x, y: math.sin(x) - y, is_periodic=True, name="sin-y"
        )
        sm.add_object("pc", c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        # _is_periodic_radical should return True for is_periodic=True
        result, _, _ = gi._is_periodic_radical(c)
        assert result is True

    def test_not_periodic_does_not_trigger_detection(self):
        sm, gi = _make_backend()
        c = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, is_periodic=False)
        sm.add_object("pc", c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        result, _, _ = gi._is_periodic_radical(c)
        # Should NOT be detected as periodic since is_periodic=False and no trig in expr
        assert result is False


# ── bounding_box ──────────────────────────────────────────────────────────────


class TestBoundingBox:
    def test_returns_none(self):
        c = _sin_curve()
        assert c.bounding_box() is None

    def test_domain_attributes_used_by_backend(self):
        sm, gi = _make_backend()
        c = _sin_curve()
        c.xmin, c.xmax, c.ymin, c.ymax = -math.pi, math.pi, -1.5, 1.5
        sm.add_object("pc", c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        # Backend should use xmin/xmax/ymin/ymax attributes
        bounds = gi._estimate_object_bounds(c, (-10, 10, -10, 10))
        xmin, xmax, ymin, ymax = bounds
        assert xmin >= -math.pi - 1.0
        assert xmax <= math.pi + 1.0


# ── graphics backend integration ──────────────────────────────────────────────


class TestGraphicsBackendProcedural:
    def _add(self, sm, c, oid="pc"):
        sm.add_object(oid, c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        return oid

    def test_renders_sin_curve(self):
        sm, gi = _make_backend()
        c = ProceduralCurve(lambda x, y: np.sin(x) - y, name="sin", is_periodic=True)
        c.xmin, c.xmax, c.ymin, c.ymax = -2 * math.pi, 2 * math.pi, -1.5, 1.5
        self._add(sm, c)
        paths = gi.get_curve_paths(bounds=(-7, 7, -2, 2), resolution=150)
        assert "pc" in paths
        assert len(paths["pc"]["points"]) > 5

    def test_renders_gaussian(self):
        sm, gi = _make_backend()
        c = ProceduralCurve(lambda x, y: np.exp(-(x**2)) - y, name="gaussian")
        c.xmin, c.xmax, c.ymin, c.ymax = -3.0, 3.0, 0.0, 1.1
        self._add(sm, c)
        paths = gi.get_curve_paths(bounds=(-4, 4, -0.5, 1.5), resolution=150)
        assert len(paths["pc"]["points"]) > 5

    def test_scene_data_includes_procedural(self):
        sm, gi = _make_backend()
        c = ProceduralCurve(lambda x, y: np.tanh(x) - y, name="tanh")
        c.xmin, c.xmax, c.ymin, c.ymax = -3.0, 3.0, -1.5, 1.5
        self._add(sm, c)
        data = gi.get_geometry_scene_data(resolution=100)
        objs = {o["id"]: o for o in data["objects"]}
        assert "pc" in objs

    def test_sin_vs_line_intersections(self):

        x, y = sp.symbols("x y")
        from geometry.conic_section import ConicSection

        sm, gi = _make_backend()
        c = ProceduralCurve(
            lambda xv, yv: np.sin(xv) - yv, name="sin", is_periodic=True
        )
        c.xmin, c.xmax, c.ymin, c.ymax = -2 * math.pi, 2 * math.pi, -1.5, 1.5
        sm.add_object("sin", c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        line = ConicSection(y - 0.5, (x, y))
        sm.add_object("line", line, {"color": "#f00", "linewidth": 2.0, "alpha": 1.0})
        data = gi.get_geometry_scene_data(resolution=200)
        # sin(x)=0.5 has 4 solutions in [-2pi, 2pi]
        assert len(data["intersections"]) >= 2


# ── DB validation ─────────────────────────────────────────────────────────────


def _db_procedural_rows():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, params_json, eval_samples_json, analytical_intersections_json "
        "FROM new_curve_types WHERE curve_class='ProceduralCurve'"
    ).fetchall()
    conn.close()
    return rows


_KNOWN_FUNCS_NS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "tanh": np.tanh,
    "atan2": np.arctan2,
    "pi": math.pi,
    "abs": np.abs,
}


def _build_procedural(params):
    """Reconstruct a ProceduralCurve from a DB params dict."""
    desc = params["function_desc"]
    # Map common function descriptions to actual lambdas
    _func_map = {
        "sin(x) - y": lambda x, y: np.sin(x) - y,
        "cos(x) - y": lambda x, y: np.cos(x) - y,
        "exp(-x**2) - y": lambda x, y: np.exp(-(x**2)) - y,
        "x**2 + y**2 + sin(5*x) - 1": lambda x, y: x**2 + y**2 + np.sin(5 * x) - 1,
        "sin(x*y)": lambda x, y: np.sin(x * y),
        "x*sin(y) - 1": lambda x, y: x * np.sin(y) - 1,
        "sin(x) + sin(y)": lambda x, y: np.sin(x) + np.sin(y),
        "tanh(x) - y": lambda x, y: np.tanh(x) - y,
        "cos(x**2+y**2) - 0.5": lambda x, y: np.cos(x**2 + y**2) - 0.5,
        "atan2(y, x) - 1": lambda x, y: np.arctan2(y, x) - 1,
    }
    fn = _func_map.get(desc)
    if fn is None:
        raise ValueError(f"No function mapping for: {desc}")
    return ProceduralCurve(fn, name=desc, is_periodic=params.get("is_periodic", False))


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="curves.db not found; run seed first"
)
class TestDBProceduralValidation:
    def test_db_has_at_least_10_rows(self):
        assert len(_db_procedural_rows()) >= 10

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json", _db_procedural_rows()
    )
    def test_eval_samples_match(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        params = json.loads(params_json)
        try:
            c = _build_procedural(params)
        except ValueError:
            pytest.skip(f"No function mapping for {name}")
        samples = json.loads(samples_json) if samples_json else []
        for xi, yi, expected_f in samples[:3]:
            actual = float(c.evaluate(float(xi), float(yi)))
            assert abs(actual - expected_f) < 0.01, (
                f"{name}: f({xi},{yi})={actual:.6f}, expected {expected_f:.6f}"
            )

    @pytest.mark.parametrize(
        "row_id,name,params_json,samples_json,intersections_json", _db_procedural_rows()
    )
    def test_graphics_backend_renders(
        self, row_id, name, params_json, samples_json, intersections_json
    ):
        params = json.loads(params_json)
        try:
            c = _build_procedural(params)
        except ValueError:
            pytest.skip(f"No function mapping for {name}")
        dom = params.get("domain", [-3, 3, -3, 3])
        c.xmin, c.xmax, c.ymin, c.ymax = dom
        sm, gi = _make_backend()
        sm.add_object("pc", c, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        bounds = (dom[0] - 0.5, dom[1] + 0.5, dom[2] - 0.5, dom[3] + 0.5)
        paths = gi.get_curve_paths(bounds=bounds, resolution=80)
        assert "pc" in paths, f"No path entry for {name}"
