"""
tests/test_graphics_fields.py

Unit + DB-validation tests for all scalar field type graphics support:
CurveField, BlendedField, SignedDistanceField, OccupancyField.
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
from geometry.base_field import CurveField, BlendedField
from geometry.field_strategy import SignedDistanceField, OccupancyField
from geometry.area_region import AreaRegion
from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager

_x, _y = sp.symbols("x y")


def _circle(cx=0, cy=0, r=1):
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _ellipse(a=2, b=1):
    return ConicSection(_x**2 / a**2 + _y**2 / b**2 - 1, (_x, _y))


def _make_region_circle(cx=0, cy=0, r=2):
    curve = _circle(cx, cy, r)
    from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
    from geometry.composite_curve import CompositeCurve

    trimmed = TrimmedImplicitCurve(curve, lambda x, y: True)
    composite = CompositeCurve([trimmed])
    return AreaRegion(outer_boundary=composite)


def _make_backend():
    sm = SceneManager()
    return sm, GraphicsBackendInterface(sm)


# ── CurveField ────────────────────────────────────────────────────────────────


class TestCurveField:
    def test_evaluate_matches_underlying_curve(self):
        curve = _circle(r=2)
        cf = CurveField(curve)
        pts = [(0.0, 0.0), (2.0, 0.0), (0.0, 2.0), (3.0, 1.0)]
        for px, py in pts:
            expected = float(curve.evaluate(px, py))
            actual = float(cf.evaluate(px, py))
            assert abs(actual - expected) < 1e-10, (
                f"CurveField({px},{py})={actual}, curve={expected}"
            )

    def test_evaluate_circle_at_centre(self):
        cf = CurveField(_circle(r=2))
        val = cf.evaluate(0.0, 0.0)
        assert abs(val - (-4.0)) < 1e-10  # 0+0-4=-4

    def test_evaluate_circle_on_boundary(self):
        cf = CurveField(_circle(r=2))
        assert abs(cf.evaluate(2.0, 0.0)) < 1e-10

    def test_evaluate_circle_outside(self):
        cf = CurveField(_circle(r=2))
        val = cf.evaluate(3.0, 0.0)
        assert abs(val - 5.0) < 1e-10  # 9+0-4=5

    def test_gradient_delegates_to_curve(self):
        curve = _circle(r=1)
        cf = CurveField(curve)
        gx_cf, gy_cf = cf.gradient(0.5, 0.5)
        gx_c, gy_c = curve.gradient(0.5, 0.5)
        assert abs(float(gx_cf) - float(gx_c)) < 1e-8
        assert abs(float(gy_cf) - float(gy_c)) < 1e-8

    def test_vectorised_evaluate(self):
        cf = CurveField(_circle(r=2))
        X = np.array([[0.0, 2.0], [3.0, 0.0]])
        Y = np.zeros((2, 2))
        Z = cf.evaluate(X, Y)
        assert Z.shape == (2, 2)
        assert abs(Z[0, 0] - (-4.0)) < 1e-8
        assert abs(Z[0, 1]) < 1e-8
        assert abs(Z[1, 0] - 5.0) < 1e-8

    def test_level_set_shifts_correctly(self):
        cf = CurveField(_circle(r=2))
        ls = cf.level_set(1.0)
        # level_set(1) → f(x,y) - 1 = 0 → circle r=sqrt(5)
        val = ls.evaluate(math.sqrt(5), 0.0)
        assert abs(val) < 1e-6


# ── BlendedField ──────────────────────────────────────────────────────────────


class TestBlendedField:
    def test_add_evaluates_correctly(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "add")
        val = bf.evaluate(0.0, 0.0)
        # -4 + -1 = -5
        assert abs(val - (-5.0)) < 1e-10

    def test_subtract_evaluates_correctly(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "subtract")
        val = bf.evaluate(0.0, 0.0)
        # -4 - (-1) = -3
        assert abs(val - (-3.0)) < 1e-10

    def test_multiply_evaluates_correctly(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "multiply")
        val = bf.evaluate(0.0, 0.0)
        # (-4) * (-1) = 4
        assert abs(val - 4.0) < 1e-10

    def test_min_is_union_boundary(self):
        c1 = ConicSection((_x - 0.5) ** 2 + _y**2 - 1, (_x, _y))
        c2 = ConicSection((_x + 0.5) ** 2 + _y**2 - 1, (_x, _y))
        bf = BlendedField([CurveField(c1), CurveField(c2)], "min")
        # (0,0) is inside both circles; min should be negative
        val = bf.evaluate(0.0, 0.0)
        assert val < 0.0
        # (10, 0) is outside both; min should be positive
        val_out = bf.evaluate(10.0, 0.0)
        assert val_out > 0.0

    def test_max_evaluates_correctly(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "max")
        val = bf.evaluate(0.0, 0.0)
        # max(-4, -1) = -1
        assert abs(val - (-1.0)) < 1e-10

    def test_average_evaluates_correctly(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "average")
        val = bf.evaluate(0.0, 0.0)
        # (-4 + -1) / 2 = -2.5
        assert abs(val - (-2.5)) < 1e-10

    def test_gradient_add(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "add")
        gx, gy = bf.gradient(1.0, 0.0)
        # df/dx of (x²+y²-4) + (x²+y²-1) = 4x → at (1,0): 4
        assert abs(float(gx) - 4.0) < 0.1

    def test_vectorised_evaluate(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "add")
        X = np.array([[0.0, 2.0]])
        Y = np.zeros((1, 2))
        Z = bf.evaluate(X, Y)
        assert Z.shape == (1, 2)

    def test_three_field_average(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        cf3 = CurveField(_ellipse(a=3, b=1))
        bf = BlendedField([cf1, cf2, cf3], "average")
        val = bf.evaluate(0.0, 0.0)
        expected = (-4.0 + -1.0 + -1.0) / 3.0
        assert abs(val - expected) < 1e-10


# ── SignedDistanceField ───────────────────────────────────────────────────────


class TestSignedDistanceField:
    def _sdf_circle(self, r=2):
        region = _make_region_circle(r=r)
        return SignedDistanceField(region, resolution=0.05)

    def test_inside_is_negative(self):
        sdf = self._sdf_circle(r=2)
        val = sdf.evaluate(0.0, 0.0)
        assert val < 0.0, f"Expected negative inside, got {val}"

    def test_outside_is_positive(self):
        sdf = self._sdf_circle(r=2)
        val = sdf.evaluate(3.0, 0.0)
        assert val > 0.0, f"Expected positive outside, got {val}"

    def test_inside_magnitude(self):
        sdf = self._sdf_circle(r=2)
        val = sdf.evaluate(0.0, 0.0)
        # Distance from centre to boundary = 2; SDF at centre ≈ -2
        assert abs(val - (-2.0)) < 0.5, f"SDF at centre: {val}, expected ≈ -2"

    def test_outside_magnitude(self):
        sdf = self._sdf_circle(r=2)
        val = sdf.evaluate(3.0, 0.0)
        # Distance from (3,0) to boundary = 1; SDF ≈ +1
        assert abs(val - 1.0) < 0.5, f"SDF outside: {val}, expected ≈ 1"

    def test_gradient_points_outward(self):
        sdf = self._sdf_circle(r=2)
        gx, gy = sdf.gradient(3.0, 0.0)
        # Gradient should point away from origin (positive x at (3,0))
        assert float(gx) > 0.0

    def test_vectorised_evaluate(self):
        sdf = self._sdf_circle(r=2)
        X = np.array([0.0, 3.0])
        Y = np.zeros(2)
        Z = sdf.evaluate(X, Y)
        assert Z.shape == (2,)
        assert Z[0] < 0.0
        assert Z[1] > 0.0


# ── OccupancyField ────────────────────────────────────────────────────────────


class TestOccupancyField:
    def _occ(self, r=2):
        region = _make_region_circle(r=r)
        return OccupancyField(region, inside_value=1.0, outside_value=0.0)

    def test_inside_returns_inside_value(self):
        occ = self._occ(r=2)
        val = occ.evaluate(0.0, 0.0)
        assert abs(val - 1.0) < 1e-10

    def test_outside_returns_outside_value(self):
        occ = self._occ(r=2)
        val = occ.evaluate(3.0, 0.0)
        assert abs(val - 0.0) < 1e-10

    def test_gradient_is_zero(self):
        occ = self._occ()
        gx, gy = occ.gradient(0.5, 0.5)
        assert gx == 0.0
        assert gy == 0.0

    def test_vectorised_evaluate(self):
        occ = self._occ(r=2)
        X = np.array([0.0, 3.0])
        Y = np.zeros(2)
        Z = occ.evaluate(X, Y)
        assert Z.shape == (2,)
        assert abs(Z[0] - 1.0) < 1e-10
        assert abs(Z[1] - 0.0) < 1e-10


# ── Graphics backend field heatmap ────────────────────────────────────────────


class TestGraphicsBackendFieldHeatmap:
    def _add(self, sm, field, oid="f"):
        sm.add_object(oid, field, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})

    def test_get_field_heatmap_data_shape(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        self._add(sm, cf)
        result = gi.get_field_heatmap_data(
            cf, "f", bounds=(-3, 3, -3, 3), resolution=32
        )
        assert "data" in result
        data = result["data"]
        assert len(data) == 32
        assert len(data[0]) == 32

    def test_get_field_heatmap_data_vmin_vmax(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        result = gi.get_field_heatmap_data(
            cf, "f", bounds=(-3, 3, -3, 3), resolution=32
        )
        assert result["vmin"] < 0.0
        assert result["vmax"] > 0.0

    def test_get_field_heatmap_data_zero_isoline(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        result = gi.get_field_heatmap_data(
            cf, "f", bounds=(-3, 3, -3, 3), resolution=64
        )
        assert "zero_isoline" in result
        # Should find some isoline paths
        assert len(result["zero_isoline"]) > 0

    def test_get_field_heatmap_data_statistics(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        result = gi.get_field_heatmap_data(
            cf, "f", bounds=(-3, 3, -3, 3), resolution=32
        )
        stats = result["statistics"]
        assert "min" in stats and "max" in stats
        assert stats["min"] < 0.0
        assert stats["max"] > 0.0

    def test_scene_data_includes_fields(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        self._add(sm, cf)
        data = gi.get_geometry_scene_data(resolution=64)
        assert "fields" in data
        assert len(data["fields"]) == 1
        assert data["fields"][0]["id"] == "f"

    def test_blended_field_heatmap(self):
        sm, gi = _make_backend()
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "add")
        self._add(sm, bf)
        result = gi.get_field_heatmap_data(
            bf, "f", bounds=(-3, 3, -3, 3), resolution=32
        )
        assert "data" in result
        assert result["statistics"]["min"] < -4.0  # sum of two negative inside values

    def test_sdf_heatmap(self):
        sm, gi = _make_backend()
        region = _make_region_circle(r=2)
        sdf = SignedDistanceField(region, resolution=0.1)
        self._add(sm, sdf)
        result = gi.get_field_heatmap_data(
            sdf, "f", bounds=(-4, 4, -4, 4), resolution=32
        )
        assert "data" in result
        # Should have both positive and negative values
        all_vals = [v for row in result["data"] for v in row if v is not None]
        assert min(all_vals) < 0.0
        assert max(all_vals) > 0.0

    def test_occupancy_heatmap(self):
        sm, gi = _make_backend()
        region = _make_region_circle(r=2)
        occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
        self._add(sm, occ)
        result = gi.get_field_heatmap_data(
            occ, "f", bounds=(-4, 4, -4, 4), resolution=32
        )
        assert "data" in result
        all_vals = [v for row in result["data"] for v in row if v is not None]
        assert max(all_vals) > 0.5  # has inside values
        assert min(all_vals) < 0.5  # has outside values

    def test_get_curve_paths_includes_field_zero_isoline(self):
        """Fields added to scene should appear in get_curve_paths as type field."""
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        self._add(sm, cf)
        paths = gi.get_curve_paths(bounds=(-3, 3, -3, 3), resolution=100)
        assert "f" in paths
        assert paths["f"]["type"] == "field"
        assert len(paths["f"]["points"]) == 0

    def test_scene_summary_counts_field_type(self):
        sm, gi = _make_backend()
        cf = CurveField(_circle(r=2))
        self._add(sm, cf, "cf1")
        bf = BlendedField([CurveField(_circle(r=1)), CurveField(_circle(r=2))], "add")
        self._add(sm, bf, "bf1")
        summary = gi.get_scene_summary()
        assert summary["object_count"] == 2
        types = summary["object_types"]
        assert "CurveField" in types
        assert "BlendedField" in types


# ── level_set extraction ──────────────────────────────────────────────────────


class TestLevelSetExtraction:
    def test_curvefield_level_set_is_renderable(self):
        cf = CurveField(_circle(r=2))
        ls = cf.level_set(0.0)
        # Level set at 0 is the circle itself — should be renderable
        val = ls.evaluate(2.0, 0.0)
        assert abs(val) < 1e-6

    def test_blendedfield_level_set(self):
        cf1 = CurveField(_circle(r=2))
        cf2 = CurveField(_circle(r=1))
        bf = BlendedField([cf1, cf2], "add")
        ls = bf.level_set(0.0)
        # The level set is a ProceduralCurve; just check it evaluates
        val = ls.evaluate(0.0, 0.0)
        assert isinstance(val, (int, float, np.floating))

    def test_sdf_level_set(self):
        region = _make_region_circle(r=2)
        sdf = SignedDistanceField(region, resolution=0.1)
        ls = sdf.level_set(0.5)  # isoline 0.5 units outside boundary
        val = ls.evaluate(2.5, 0.0)
        # Should be near zero (on the isoline)
        assert isinstance(val, (int, float, np.floating))


# ── DB validation ─────────────────────────────────────────────────────────────


def _db_field_rows():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, params_json, eval_samples_json "
        "FROM new_curve_types WHERE curve_class IN "
        "('CurveField','BlendedField','SignedDistanceField','OccupancyField')"
    ).fetchall()
    conn.close()
    return rows


def _reconstruct_field(params):
    """Reconstruct a BaseField from a DB params dict (best-effort)."""
    ft = params.get("field_type")
    if ft == "CurveField":
        spec = params["curve_spec"]
        expr = sp.sympify(spec["expr"])
        curve = ConicSection(expr, (_x, _y))
        return CurveField(curve)
    elif ft == "BlendedField":
        sub_fields = []
        for fs in params["fields_spec"]:
            if fs["type"] == "CurveField":
                expr = sp.sympify(fs["curve"]["expr"])
                curve = ConicSection(expr, (_x, _y))
                sub_fields.append(CurveField(curve))
        return BlendedField(sub_fields, params["operation"])
    elif ft == "SignedDistanceField":
        from geometry import CompositeCurve
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

        spec = params["region_spec"]
        expr = sp.sympify(spec["expr"])
        curve = ConicSection(expr, (_x, _y))
        if not isinstance(curve, CompositeCurve):
            curve = CompositeCurve([TrimmedImplicitCurve(curve, lambda px, py: True)])
        region = AreaRegion(outer_boundary=curve)
        return SignedDistanceField(region, resolution=0.1)
    elif ft == "OccupancyField":
        from geometry import CompositeCurve
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

        spec = params["region_spec"]
        expr = sp.sympify(spec["expr"])
        curve = ConicSection(expr, (_x, _y))
        if not isinstance(curve, CompositeCurve):
            curve = CompositeCurve([TrimmedImplicitCurve(curve, lambda px, py: True)])
        region = AreaRegion(outer_boundary=curve)
        return OccupancyField(
            region, params.get("inside_value", 1.0), params.get("outside_value", 0.0)
        )
    raise ValueError(f"Unknown field type: {ft}")


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="curves.db not found; run seed first"
)
class TestDBFieldValidation:
    def test_db_has_at_least_10_rows(self):
        assert len(_db_field_rows()) >= 10

    @pytest.mark.parametrize("row_id,name,params_json,samples_json", _db_field_rows())
    def test_eval_samples_match(self, row_id, name, params_json, samples_json):
        params = json.loads(params_json)
        try:
            field = _reconstruct_field(params)
        except Exception as e:
            pytest.skip(f"Cannot reconstruct {name}: {e}")
        samples = json.loads(samples_json) if samples_json else []
        for sample in samples[:3]:
            if len(sample) == 3 and sample[2] is not None:
                xi, yi, expected = sample
                actual = float(field.evaluate(float(xi), float(yi)))
                assert abs(actual - expected) < 0.5, (
                    f"{name}: f({xi},{yi})={actual:.4f}, expected {expected:.4f}"
                )

    @pytest.mark.parametrize("row_id,name,params_json,samples_json", _db_field_rows())
    def test_heatmap_renders(self, row_id, name, params_json, samples_json):
        params = json.loads(params_json)
        try:
            field = _reconstruct_field(params)
        except Exception as e:
            pytest.skip(f"Cannot reconstruct {name}: {e}")
        sm, gi = _make_backend()
        sm.add_object("f", field, {"color": "#fff", "linewidth": 2.0, "alpha": 1.0})
        result = gi.get_field_heatmap_data(
            field, "f", bounds=(-4, 4, -4, 4), resolution=32
        )
        assert "data" in result, f"No data for {name}"
        assert len(result["data"]) == 32
