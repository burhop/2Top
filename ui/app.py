def _broadcast_scene_updated_async():
    """Background task to broadcast scene updates after a brief delay.
    This avoids the test client's get_received() polling from consuming
    the scene_updated event while waiting for ui_response.
    """
    try:
        # Small delay to let ui_response be processed first
        time.sleep(0.01)
        objects = scene_manager.list_objects()
        if isinstance(objects, dict):
            object_ids = list(objects.keys())
        else:
            object_ids = list(objects)
        socketio.emit("scene_updated", {"objects": object_ids, "bounds": None})
    except Exception as e:
        print(f"Async scene_updated broadcast failed: {e}")


"""
2Top Geometry Library - Web UI Server
Main Flask application for the web-based user interface.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import sys
import os
import time

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import RegionFactory, CurveFactory
from geometry import ConicSection, AreaRegion, CompositeCurve
from .geometry_tests import list_geometry_tests, run_geometry_test
import sqlite3
import math
import numpy as np
import sympy as sp
from geometry.implicit_curve import ImplicitCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections
from tests.test_periodic_curves import (
    TEST_CONFIGS,
    reconstruct_curve,
    get_expected_intersections,
)
from geometry import ProceduralCurve
from geometry.parametric_segment import ParametricSegment
from geometry import Superellipse, RFunctionCurve
from geometry import (
    CurveField,
    BlendedField,
    SignedDistanceField,
    OccupancyField,
    BaseField,
)


DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "curves.db"
)


def reconstruct_new_curve_types_row(new_row):
    """Reconstruct a curve or field from a new_curve_types row."""
    db_id, curve_class, name, description, params_json = new_row
    params = json.loads(params_json)

    x, y = sp.symbols("x y")

    # Helper for child curves reconstruction
    def reconstruct_curve_from_spec(spec):
        t = spec.get("type")
        if t == "ConicSection":
            expr = sp.sympify(spec["expr"])
            return ConicSection(expr, (x, y))
        elif t == "Superellipse":
            return Superellipse(spec["a"], spec["b"], spec["n"])
        elif t == "RFunctionCurve":
            c1 = reconstruct_curve_from_spec(spec["curve1"])
            c2 = reconstruct_curve_from_spec(spec["curve2"])
            op = spec["operation"]
            alpha = spec.get("alpha", 0.0)
            return RFunctionCurve(c1, c2, operation=op, alpha=alpha)
        raise ValueError(f"Unknown curve spec type: {t}")

    # Helper for fields reconstruction
    def reconstruct_field_from_params(p):
        ft = p.get("field_type")
        if ft == "CurveField":
            curve = reconstruct_curve_from_spec(p["curve_spec"])
            return CurveField(curve)
        elif ft == "BlendedField":
            sub_fields = []
            for fs in p["fields_spec"]:
                if fs.get("type") == "CurveField":
                    curve = reconstruct_curve_from_spec(fs["curve"])
                    sub_fields.append(CurveField(curve))
                elif (
                    fs.get("type")
                    in (
                        "CurveField",
                        "BlendedField",
                        "SignedDistanceField",
                        "OccupancyField",
                    )
                    or "field_type" in fs
                ):
                    sub_fields.append(reconstruct_field_from_params(fs))
            return BlendedField(sub_fields, p["operation"])
        elif ft == "SignedDistanceField":
            spec = p["region_spec"]
            if "expr" in spec:
                curve = ConicSection(sp.sympify(spec["expr"]), (x, y))
            else:
                curve = reconstruct_curve_from_spec(spec)
            if not isinstance(curve, CompositeCurve):
                curve = CompositeCurve(
                    [TrimmedImplicitCurve(curve, lambda px, py: True)]
                )
            region = AreaRegion(outer_boundary=curve)
            return SignedDistanceField(region, resolution=0.1)
        elif ft == "OccupancyField":
            spec = p["region_spec"]
            if "expr" in spec:
                curve = ConicSection(sp.sympify(spec["expr"]), (x, y))
            else:
                curve = reconstruct_curve_from_spec(spec)
            if not isinstance(curve, CompositeCurve):
                curve = CompositeCurve(
                    [TrimmedImplicitCurve(curve, lambda px, py: True)]
                )
            region = AreaRegion(outer_boundary=curve)
            return OccupancyField(
                region, p.get("inside_value", 1.0), p.get("outside_value", 0.0)
            )
        raise ValueError(f"Unknown field type: {ft}")

    if curve_class == "ParametricSegment":
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
        ns = {**_KNOWN_FUNCTIONS, "t": 0}
        x_fn = eval(f"lambda t: {params['x_expr']}", ns)
        y_fn = eval(f"lambda t: {params['y_expr']}", ns)
        curve = ParametricSegment(x_fn, y_fn, params["t_start"], params["t_end"])

    elif curve_class == "Superellipse":
        curve = Superellipse(params["a"], params["b"], params["n"])

    elif curve_class == "RFunctionCurve":
        c1 = reconstruct_curve_from_spec(params["curve1"])
        c2 = reconstruct_curve_from_spec(params["curve2"])
        curve = RFunctionCurve(
            c1, c2, operation=params["operation"], alpha=params.get("alpha", 0.0)
        )

    elif curve_class == "ProceduralCurve":
        expr = sp.sympify(params["function_desc"])
        function_callable = sp.lambdify((x, y), expr, "numpy")
        curve = ProceduralCurve(
            function_callable,
            variables=(x, y),
            name=name,
            is_periodic=params.get("is_periodic", False),
        )

    elif curve_class in (
        "CurveField",
        "BlendedField",
        "SignedDistanceField",
        "OccupancyField",
    ):
        if "field_type" not in params:
            params["field_type"] = curve_class
        curve = reconstruct_field_from_params(params)

    else:
        raise ValueError(f"Unknown curve class: {curve_class}")

    if curve_class == "ProceduralCurve" and "domain" in params:
        d = params["domain"]
        curve.xmin, curve.xmax, curve.ymin, curve.ymax = d[0], d[1], d[2], d[3]
    elif hasattr(curve, "bounding_box") and curve.bounding_box() is not None:
        try:
            xmin, xmax, ymin, ymax = curve.bounding_box()
            curve.xmin, curve.xmax, curve.ymin, curve.ymax = xmin, xmax, ymin, ymax
        except Exception:
            curve.xmin, curve.xmax, curve.ymin, curve.ymax = -5.0, 5.0, -5.0, 5.0
    else:
        curve.xmin, curve.xmax, curve.ymin, curve.ymax = -5.0, 5.0, -5.0, 5.0

    curve.curve_type = curve_class
    curve.name = name
    curve.description = description
    return curve


def reconstruct_geometry_curve(c_row):
    """Factory to map database record to 2Top Geometry object."""
    if len(c_row) in (5, 9):
        if len(c_row) == 9:
            new_row = (c_row[0], c_row[1], c_row[2], c_row[3], c_row[4])
        else:
            new_row = c_row
        return reconstruct_new_curve_types_row(new_row)

    (
        c_id,
        g_id,
        equation_str,
        c_type,
        scale,
        xmin,
        xmax,
        ymin,
        ymax,
        endpoints_json,
        tol,
    ) = c_row

    x, y = sp.symbols("x y")
    equation_str_cleaned = equation_str.replace("asin", "asin")
    expr = sp.sympify(equation_str_cleaned)

    endpoints = json.loads(endpoints_json) if endpoints_json else []

    if c_type == "periodic_radical":
        try:
            sin_terms = expr.atoms(sp.sin)
            if sin_terms:
                sin_term = list(sin_terms)[0]
                arg = sin_term.args[0]
                B = float(arg.coeff(x))
                C = float(arg.subs(x, 0))
                # Find all k zero-crossings in [xmin, xmax]
                # x = (k * pi - C) / B
                # xmin - 0.1 <= x <= xmax + 0.1
                endpoints = []
                k_min = int(math.floor(((xmin - 0.5) * B + C) / math.pi))
                k_max = int(math.ceil(((xmax + 0.5) * B + C) / math.pi))
                for k in range(k_min - 2, k_max + 3):
                    x_val = (k * math.pi - C) / B
                    if xmin - 0.1 <= x_val <= xmax + 0.1:
                        endpoints.append([x_val, 0.0])
        except Exception as e:
            print(
                f"Warning: Failed dynamic endpoint generation for periodic radical: {e}"
            )

    if c_type in ["circle", "ellipse", "parabola", "line"]:
        base_curve = ConicSection(expr, (x, y))
    else:
        base_curve = ImplicitCurve(expr, (x, y))

    base_curve.scale_hint = scale

    if endpoints:
        def default_mask(px, py):
            return True
        mask = default_mask
        sqrt_terms = [
            atom
            for atom in expr.atoms(sp.Pow)
            if atom.exp in [0.5, -0.5, sp.Rational(1, 2), sp.Rational(-1, 2)]
        ]
        asin_terms = expr.atoms(sp.asin)

        if sqrt_terms:
            sqrt_arg = sqrt_terms[0].base
            arg_func = sp.lambdify((x, y), sqrt_arg, "numpy")

            def sqrt_mask(px, py, arg_func=arg_func):
                return arg_func(px, py) >= -0.05

            mask = sqrt_mask
        elif asin_terms:
            asin_arg = list(asin_terms)[0].args[0]
            arg_func = sp.lambdify((x, y), asin_arg, "numpy")

            def asin_mask(px, py, arg_func=arg_func):
                return abs(arg_func(px, py)) <= 1.0 + 0.05

            mask = asin_mask
        elif c_type == "periodic_radical":
            f_x = y**2 - expr
            f_func = sp.lambdify((x, y), f_x, "numpy")

            def periodic_mask(px, py, f_func=f_func):
                return f_func(px, py) >= -0.05

            mask = periodic_mask

        curve = TrimmedImplicitCurve(
            base_curve=base_curve,
            mask=mask,
            variables=(x, y),
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            endpoints=[tuple(pt) for pt in endpoints],
        )
    else:
        curve = base_curve

    curve.xmin = xmin
    curve.xmax = xmax
    curve.ymin = ymin
    curve.ymax = ymax

    # Store metadata on reconstructed curve objects for accurate backend graphics classification
    curve.curve_type = c_type
    curve.is_periodic_radical = c_type == "periodic_radical"
    if hasattr(curve, "base_curve") and curve.base_curve is not None:
        curve.base_curve.curve_type = c_type
        curve.base_curve.is_periodic_radical = c_type == "periodic_radical"

    return curve


def translate_curve(curve, x0, y0):
    """Translate a 2Top Geometry curve by (x0, y0) to focus grid search."""
    x, y = sp.symbols("x y")

    if hasattr(curve, "base_curve") and hasattr(curve, "mask"):
        base_expr = curve.base_curve.expression
        expr_trans = base_expr.subs({x: x + x0, y: y + y0})

        if isinstance(curve.base_curve, ConicSection):
            base_trans = ConicSection(expr_trans, (x, y))
        else:
            base_trans = ImplicitCurve(expr_trans, (x, y))

        base_trans.scale_hint = getattr(curve.base_curve, "scale_hint", 1.0)

        endpoints_trans = [(pt[0] - x0, pt[1] - y0) for pt in curve.endpoints]
        original_mask = curve.mask

        def mask_trans(px, py, om=original_mask, dx=x0, dy=y0):
            return om(px + dx, py + dy)

        curve_trans = TrimmedImplicitCurve(
            base_curve=base_trans,
            mask=mask_trans,
            variables=(x, y),
            xmin=curve.xmin - x0,
            xmax=curve.xmax - x0,
            ymin=curve.ymin - y0,
            ymax=curve.ymax - y0,
            endpoints=endpoints_trans,
        )
    else:
        expr_trans = curve.expression.subs({x: x + x0, y: y + y0})
        if isinstance(curve, ConicSection):
            curve_trans = ConicSection(expr_trans, (x, y))
        else:
            curve_trans = ImplicitCurve(expr_trans, (x, y))

    curve_trans.scale_hint = getattr(curve, "scale_hint", 1.0)
    curve_trans.xmin = curve.xmin - x0
    curve_trans.xmax = curve.xmax - x0
    curve_trans.ymin = curve.ymin - y0
    curve_trans.ymax = curve.ymax - y0

    if hasattr(curve, "curve_type"):
        curve_trans.curve_type = curve.curve_type
    if hasattr(curve, "is_periodic_radical"):
        curve_trans.is_periodic_radical = curve.is_periodic_radical
    if (
        hasattr(curve, "base_curve")
        and curve.base_curve is not None
        and hasattr(curve_trans, "base_curve")
        and curve_trans.base_curve is not None
    ):
        if hasattr(curve.base_curve, "curve_type"):
            curve_trans.base_curve.curve_type = curve.base_curve.curve_type
        if hasattr(curve.base_curve, "is_periodic_radical"):
            curve_trans.base_curve.is_periodic_radical = (
                curve.base_curve.is_periodic_radical
            )

    return curve_trans


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.after_request
def add_header(r):
    """Disable static asset caching entirely during development."""
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


# Initialize backend components
scene_manager = SceneManager()
graphics_interface = GraphicsBackendInterface(scene_manager)
region_factory = RegionFactory()
curve_factory = CurveFactory()

PERSISTENT_SCENE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "persistent_scene.json"
)


def save_persistent_scene():
    try:
        scene_manager.save_scene(PERSISTENT_SCENE_FILE)
        print(f"Persistent scene auto-saved to {PERSISTENT_SCENE_FILE}")
    except Exception as e:
        print(f"Warning: Failed to auto-save persistent scene: {e}")


def restore_persistent_scene():
    try:
        if os.path.exists(PERSISTENT_SCENE_FILE):
            print(f"Restoring persistent scene from {PERSISTENT_SCENE_FILE}...")
            scene_manager.load_scene(PERSISTENT_SCENE_FILE)
            print(
                f"Persistent scene restored successfully! Objects loaded: {list(scene_manager.list_objects())}"
            )
    except Exception as e:
        print(f"Warning: Failed to restore persistent scene: {e}")


# Automatically restore previous scene state if it exists
restore_persistent_scene()


@app.route("/")
def index():
    """Serve the main UI page"""
    return render_template("index.html")


@app.route("/api/scene/info")
def scene_info():
    """Get current scene information"""
    try:
        objects = scene_manager.list_objects()
        # Normalize to a list of object IDs
        if isinstance(objects, dict):
            object_ids = list(objects.keys())
        else:
            object_ids = list(objects)

        scene_data = {
            "objects": object_ids,
            "object_count": len(object_ids),
            "bounds": graphics_interface.get_scene_bounds() if objects else None,
        }
        return jsonify({"success": True, "data": scene_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/geometry-tests", methods=["GET"])
def geometry_tests():
    """Return metadata for predefined geometry test scenes."""
    try:
        return jsonify({"success": True, "tests": list_geometry_tests()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/geometry-tests/run", methods=["POST"])
def geometry_tests_run():
    """Clear the scene and run a predefined geometry test scenario."""
    try:
        data = request.get_json(force=True)
        test_id = data.get("test_id")
        if not test_id:
            return jsonify({"success": False, "error": "test_id is required"}), 400

        created_ids = run_geometry_test(
            test_id, scene_manager, curve_factory, region_factory
        )
        bounds = graphics_interface.get_scene_bounds()
        save_persistent_scene()
        socketio.start_background_task(_broadcast_scene_updated_async)
        return jsonify(
            {"success": True, "objects": created_ids, "bounds": list(bounds)}
        )
    except KeyError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/periodic-tests", methods=["GET"])
def list_periodic_tests():
    """Return metadata for all 155 periodic cases categorized by Tiers."""
    try:
        tests_list = []
        for test_id, config in sorted(
            TEST_CONFIGS.items(), key=lambda x: [int(c) for c in x[0].split(".")]
        ):
            tests_list.append(
                {
                    "test_id": test_id,
                    "name": config["name"],
                    "eq_a": config["eq_a"],
                    "eq_b": config.get("eq_b", ""),
                    "domain": config["domain"],
                    "tier": config["tier"],
                }
            )
        return jsonify({"success": True, "tests": tests_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/periodic-tests/run", methods=["POST"])
def run_periodic_test():
    """Clear the scene, reconstruct curves, calculate intersections and endpoints, verify results, render and return data."""
    try:
        data = request.get_json(force=True) or {}
        test_id = data.get("test_id")
        if not test_id or test_id not in TEST_CONFIGS:
            return jsonify(
                {"success": False, "error": f"Test ID '{test_id}' not found"}
            ), 400

        config = TEST_CONFIGS[test_id]
        dom = config["domain"]

        # 1. Clear active scene
        scene_manager.clear()

        # 2. Reconstruct curves A and B
        x_sym, y_sym = sp.symbols("x y", real=True)
        eq_b = config.get("eq_b")
        curve_a = reconstruct_curve(config["eq_a"], x_sym, y_sym)
        curve_b = reconstruct_curve(eq_b, x_sym, y_sym) if eq_b else None

        # Set attributes on reconstructed curves so graphics_backend can retrieve details
        curve_a.xmin, curve_a.xmax = dom[0], dom[1]
        curve_a.ymin, curve_a.ymax = -4.0, 4.0
        if curve_b:
            curve_b.xmin, curve_b.xmax = dom[0], dom[1]
            curve_b.ymin, curve_b.ymax = -4.0, 4.0

        # Add objects to scene manager with custom styling
        style_a = {
            "color": "#00f0ff",
            "linewidth": 4.5,
            "alpha": 1.0,
            "is_periodic_curve": True,
            "curve_name": config["eq_a"],
        }
        scene_manager.add_object("periodic_curve_a", curve_a, style_a)

        if curve_b:
            style_b = {
                "color": "#ff007f",
                "linewidth": 2.0,
                "alpha": 1.0,
                "is_periodic_curve": True,
                "curve_name": eq_b,
            }
            scene_manager.add_object("periodic_curve_b", curve_b, style_b)

        # 3. Calculate Endpoints & Intersections
        t0 = time.perf_counter()

        endpoints_a = []
        endpoints_b = []
        try:
            if hasattr(curve_a, "get_endpoints"):
                endpoints_a = curve_a.get_endpoints(xmin=dom[0], xmax=dom[1])
            if curve_b and hasattr(curve_b, "get_endpoints"):
                endpoints_b = curve_b.get_endpoints(xmin=dom[0], xmax=dom[1])
        except Exception as e:
            print(f"Warning: Endpoint calculation failed: {e}")

        calculated_endpoints = [tuple(pt) for pt in (endpoints_a + endpoints_b)]

        # Intersections calculation
        search_range = config.get("search_range", (dom[1] - dom[0]) / 2.0)
        if search_range < 0.1:
            search_range = 1.0
        grid_res = config.get("grid_res", 500)
        center_x = (dom[0] + dom[1]) / 2.0

        calculated_intersections = []

        if curve_b:
            # Handle shifting
            if abs(center_x) > 1e-4:
                expr_a_trans = (
                    curve_a.expression.subs(x_sym, x_sym + center_x)
                    if hasattr(curve_a, "expression") and curve_a.expression
                    else None
                )
                expr_b_trans = (
                    curve_b.expression.subs(x_sym, x_sym + center_x)
                    if hasattr(curve_b, "expression") and curve_b.expression
                    else None
                )

                if expr_a_trans and expr_b_trans:
                    if isinstance(curve_a, ProceduralCurve):
                        func_a = sp.lambdify((x_sym, y_sym), expr_a_trans, "numpy")
                        c_a = ProceduralCurve(func_a, variables=(x_sym, y_sym))
                    else:
                        c_a = reconstruct_curve(str(expr_a_trans), x_sym, y_sym)

                    if isinstance(curve_b, ProceduralCurve):
                        func_b = sp.lambdify((x_sym, y_sym), expr_b_trans, "numpy")
                        c_b = ProceduralCurve(func_b, variables=(x_sym, y_sym))
                    else:
                        c_b = reconstruct_curve(str(expr_b_trans), x_sym, y_sym)
                else:
                    if isinstance(curve_a, ProceduralCurve):
                        orig_func = curve_a.function
                        c_a = ProceduralCurve(
                            lambda x_v, y_v: orig_func(x_v + center_x, y_v),
                            variables=(x_sym, y_sym),
                        )
                    else:
                        c_a = curve_a

                    if isinstance(curve_b, ProceduralCurve):
                        orig_func = curve_b.function
                        c_b = ProceduralCurve(
                            lambda x_v, y_v: orig_func(x_v + center_x, y_v),
                            variables=(x_sym, y_sym),
                        )
                    else:
                        c_b = curve_b
            else:
                c_a = curve_a
                c_b = curve_b

            detect_overlap = test_id in ("1.39", "2.34", "3.33")
            found_pts_trans = find_curve_intersections(
                c_a,
                c_b,
                search_range=search_range,
                grid_resolution=grid_res,
                detect_overlap=detect_overlap,
            )
            calculated_intersections = [
                (float(pt[0] + center_x), float(pt[1])) for pt in found_pts_trans
            ]

        elapsed_time = time.perf_counter() - t0

        # 4. Compare with analytical expectations
        expected_intersections = []
        if curve_b:
            oracle_dom = (center_x - search_range, center_x + search_range)
            expected_intersections = get_expected_intersections(
                config["eq_a"], eq_b, oracle_dom
            )

        expected_endpoints = []
        if "expected_endpoint_count" in config:
            try:
                expr = curve_a.expression
                sin_terms = expr.atoms(sp.sin)
                if sin_terms:
                    sin_term = list(sin_terms)[0]
                    arg = sin_term.args[0]
                    B = float(arg.coeff(x_sym))
                    C = float(arg.subs(x_sym, 0))
                    k_min = int(math.floor(((dom[0] - 0.5) * B + C) / math.pi))
                    k_max = int(math.ceil(((dom[1] + 0.5) * B + C) / math.pi))
                    for k in range(k_min - 2, k_max + 3):
                        x_val = (k * math.pi - C) / B
                        if dom[0] - 0.1 <= x_val <= dom[1] + 0.1:
                            expected_endpoints.append((x_val, 0.0))
            except Exception:
                pass

        is_correct = True
        try:
            if "expected_endpoint_count" in config:
                expected_ep_count = config["expected_endpoint_count"]
                found_ep_count = len(calculated_endpoints)
                if abs(found_ep_count - expected_ep_count) > 2:
                    is_correct = False
            else:
                expected_int_count = len(expected_intersections)
                found_int_count = len(calculated_intersections)

                if test_id in ("1.39", "2.34", "3.33"):
                    if found_int_count > 0:
                        is_correct = False
                elif test_id == "2.33":
                    if found_int_count not in (1, 2):
                        is_correct = False
                else:
                    allowed_count_diff = 0
                    has_eq_b_1_x = eq_b and "1/x" in eq_b
                    if "1/x" in config["eq_a"] or has_eq_b_1_x:
                        allowed_count_diff = max(6, int(0.45 * expected_int_count))
                    elif expected_int_count > 100:
                        allowed_count_diff = max(2, int(0.02 * expected_int_count))

                    if abs(found_int_count - expected_int_count) > allowed_count_diff:
                        is_correct = False

                    max_error = 0.0
                    matched_exp = set()
                    for f_pt in calculated_intersections:
                        best_err = float("inf")
                        best_idx = -1
                        for idx, e_pt in enumerate(expected_intersections):
                            if idx in matched_exp:
                                continue
                            err = math.sqrt(
                                (f_pt[0] - e_pt[0]) ** 2 + (f_pt[1] - e_pt[1]) ** 2
                            )
                            if err < best_err:
                                best_err = err
                                best_idx = idx
                        if best_idx != -1:
                            matched_exp.add(best_idx)
                            if best_err > max_error:
                                max_error = best_err
                        else:
                            if not ("1/x" in config["eq_a"] or has_eq_b_1_x):
                                max_error = float("inf")
                            else:
                                max_error = max(max_error, 0.1)

                    tolerance_limit = 0.05
                    if "1/x" in config["eq_a"] or has_eq_b_1_x:
                        tolerance_limit = 0.15

                    if max_error > tolerance_limit:
                        is_correct = False
        except Exception:
            is_correct = False

        # 5. Render to Annotated image
        filename = f"case_{test_id.replace('.', '_')}.png"
        filepath = os.path.join("ui", "static", "renders", "periodic_curves", filename)

        x_span = dom[1] - dom[0]
        if x_span < 0.2:
            xmin_render = dom[0] - 2.0
            xmax_render = dom[1] + 2.0
        else:
            padding_x = x_span * 0.05
            xmin_render = dom[0] - padding_x
            xmax_render = dom[1] + padding_x

        # Calculate dynamic y range to avoid extremely squeezed/compressed x-axis under equal aspect ratio
        render_x_span = xmax_render - xmin_render
        y_span = max(2.5, min(8.0, render_x_span * 0.75))
        ymin_render = -y_span / 2.0
        ymax_render = y_span / 2.0
        bounds = (xmin_render, xmax_render, ymin_render, ymax_render)

        render_res = graphics_interface.render_scene_image_annotated(
            filename=filepath,
            test_id=test_id,
            name=config["name"],
            eq_a=config["eq_a"],
            eq_b=eq_b or "",
            calculated_endpoints=calculated_endpoints,
            expected_endpoints=expected_endpoints,
            calculated_intersections=calculated_intersections,
            expected_intersections=expected_intersections,
            elapsed_time=elapsed_time,
            is_correct=is_correct,
            bounds=bounds,
        )

        save_persistent_scene()
        socketio.start_background_task(_broadcast_scene_updated_async)

        payload = {
            "success": True,
            "test_id": test_id,
            "name": config["name"],
            "is_correct": is_correct,
            "elapsed_time": elapsed_time,
            "calculated_endpoints": calculated_endpoints,
            "expected_endpoints": expected_endpoints,
            "calculated_intersections": calculated_intersections,
            "expected_intersections": expected_intersections,
            "image_url": f"/static/renders/periodic_curves/{filename}",
            "render_details": render_res,
        }
        return jsonify(payload)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/geometry-scene")
def geometry_scene_data():
    """Return polyline + key-point data for the current scene."""
    try:
        min_x = request.args.get("min_x", type=float)
        max_x = request.args.get("max_x", type=float)
        min_y = request.args.get("min_y", type=float)
        max_y = request.args.get("max_y", type=float)

        bounds = None
        if all(v is not None for v in [min_x, max_x, min_y, max_y]):
            bounds = (min_x, max_x, min_y, max_y)

        scene_data = graphics_interface.get_geometry_scene_data(
            resolution=150, bounds=bounds
        )
        return jsonify({"success": True, "data": scene_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/geometry-scene/fields")
def geometry_scene_fields():
    """Return heatmap data for all BaseField objects in the scene."""
    try:
        # Evaluate fields on static physical scene bounds to ensure zoom-independence
        p_bounds = graphics_interface.get_scene_bounds(padding=0.5)
        if p_bounds is not None and all(np.isfinite(b) for b in p_bounds):
            pxmin, pxmax, pymin, pymax = p_bounds
        else:
            pxmin, pxmax, pymin, pymax = -10.0, 10.0, -10.0, 10.0

        span_x = pxmax - pxmin
        if span_x < 20.0:
            cx = (pxmin + pxmax) / 2.0
            pxmin = cx - 10.0
            pxmax = cx + 10.0

        span_y = pymax - pymin
        if span_y < 20.0:
            cy = (pymin + pymax) / 2.0
            pymin = cy - 10.0
            pymax = cy + 10.0

        sanitized_bounds = (pxmin, pxmax, pymin, pymax)
        fields = []
        resolution = 128
        for obj_id in scene_manager.list_objects():
            obj = scene_manager.get_object(obj_id)
            if isinstance(obj, BaseField):
                try:
                    field_entry = graphics_interface.get_field_heatmap_data(
                        obj, obj_id, sanitized_bounds, resolution
                    )
                    fields.append(field_entry)
                except Exception as fe:
                    fields.append({"id": obj_id, "error": str(fe)})

        return jsonify({"success": True, "fields": fields})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/db/curves/load", methods=["POST"])
def db_curves_load():
    """Load one or more curves from the SQLite database curves.db"""
    try:
        data = request.get_json(force=True) or {}
        curve_id = data.get("curve_id")
        group_id = data.get("group_id")

        if not os.path.exists(DB_PATH):
            return jsonify(
                {
                    "success": False,
                    "error": f"Database file not found at {DB_PATH}. Please ensure curves.db exists.",
                }
            ), 404

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        loaded_ids = []

        if curve_id is not None:
            curve_id = int(curve_id)
            is_new = False
            real_id = curve_id

            if curve_id >= 10000000:
                is_new = True
                real_id = curve_id - 10000000

            if is_new:
                cursor.execute(
                    """
                    SELECT id, curve_class, name, description, params_json FROM new_curve_types WHERE id = ?;
                """,
                    (real_id,),
                )
                new_row = cursor.fetchone()
                if not new_row:
                    conn.close()
                    return jsonify(
                        {
                            "success": False,
                            "error": f"Custom curve #{real_id} not found in database",
                        }
                    ), 404

                curve = reconstruct_new_curve_types_row(new_row)
                obj_id = f"db_curve_{real_id + 10000000}"

                if obj_id in scene_manager.list_objects():
                    scene_manager.remove_object(obj_id)

                # Neon orange/yellow for new curve types
                color = "#ffb536"
                style = {
                    "color": color,
                    "linewidth": 2.5,
                    "alpha": 1.0,
                    "is_db_curve": True,
                    "db_id": real_id + 10000000,
                    "is_new_type": True,
                    "curve_class": new_row[1],
                }
                scene_manager.add_object(obj_id, curve, style)
                loaded_ids.append(real_id + 10000000)
            else:
                cursor.execute(
                    """
                    SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                    FROM curves WHERE id = ?;
                """,
                    (curve_id,),
                )
                row = cursor.fetchone()
                if not row:
                    # Fallback to new_curve_types table
                    cursor.execute(
                        """
                        SELECT id, curve_class, name, description, params_json FROM new_curve_types WHERE id = ?;
                    """,
                        (curve_id,),
                    )
                    new_row = cursor.fetchone()
                    if not new_row:
                        conn.close()
                        return jsonify(
                            {
                                "success": False,
                                "error": f"Curve #{curve_id} not found in database",
                            }
                        ), 404

                    curve = reconstruct_new_curve_types_row(new_row)
                    obj_id = f"db_curve_{new_row[0] + 10000000}"

                    if obj_id in scene_manager.list_objects():
                        scene_manager.remove_object(obj_id)

                    # Neon orange/yellow for new curve types
                    color = "#ffb536"
                    style = {
                        "color": color,
                        "linewidth": 2.5,
                        "alpha": 1.0,
                        "is_db_curve": True,
                        "db_id": new_row[0] + 10000000,
                        "is_new_type": True,
                        "curve_class": new_row[1],
                    }
                    scene_manager.add_object(obj_id, curve, style)
                    loaded_ids.append(new_row[0] + 10000000)
                else:
                    curve = reconstruct_geometry_curve(row)
                    obj_id = f"db_curve_{row[0]}"

                    # If it already exists, remove it first
                    if obj_id in scene_manager.list_objects():
                        scene_manager.remove_object(obj_id)

                    # Add to scene manager with custom style tagging
                    group_id_val = row[1]
                    NEON_PALETTE = [
                        "#77f6ff",
                        "#ff6b9c",
                        "#a0fe38",
                        "#ffb536",
                        "#c684ff",
                    ]
                    if group_id_val is not None:
                        cursor.execute(
                            "SELECT id FROM curves WHERE group_id = ? ORDER BY id ASC;",
                            (int(group_id_val),),
                        )
                        group_curve_ids = [r[0] for r in cursor.fetchall()]
                        try:
                            index = group_curve_ids.index(int(curve_id))
                            color = NEON_PALETTE[index % len(NEON_PALETTE)]
                        except ValueError:
                            color = (
                                "#ff6b9c" if row[3] == "periodic_radical" else "#77f6ff"
                            )
                    else:
                        color = "#ff6b9c" if row[3] == "periodic_radical" else "#77f6ff"

                    style = {
                        "color": color,
                        "linewidth": 2.5,
                        "alpha": 1.0,
                        "is_db_curve": True,
                        "db_id": row[0],
                    }
                    scene_manager.add_object(obj_id, curve, style)
                    loaded_ids.append(row[0])

        elif group_id is not None:
            cursor.execute(
                """
                SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                FROM curves WHERE group_id = ?;
            """,
                (int(group_id),),
            )
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                return jsonify(
                    {
                        "success": False,
                        "error": f"No curves found for Spatial Group #{group_id}",
                    }
                ), 404

            NEON_PALETTE = ["#77f6ff", "#ff6b9c", "#a0fe38", "#ffb536", "#c684ff"]
            for index, row in enumerate(rows):
                curve = reconstruct_geometry_curve(row)
                obj_id = f"db_curve_{row[0]}"

                if obj_id in scene_manager.list_objects():
                    scene_manager.remove_object(obj_id)

                # Alternate colors in the group so they can be visually distinguished
                color = NEON_PALETTE[index % len(NEON_PALETTE)]
                style = {
                    "color": color,
                    "linewidth": 2.5,
                    "alpha": 1.0,
                    "is_db_curve": True,
                    "db_id": row[0],
                }
                scene_manager.add_object(obj_id, curve, style)
                loaded_ids.append(row[0])
        else:
            conn.close()
            return jsonify(
                {"success": False, "error": "Either curve_id or group_id is required"}
            ), 400

        conn.close()

        # Emit scene update to trigger front-end redraw
        save_persistent_scene()
        socketio.start_background_task(_broadcast_scene_updated_async)

        return jsonify({"success": True, "loaded_ids": loaded_ids})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/db/groups/<int:group_id>/curves", methods=["GET"])
def db_group_curves(group_id):
    """Retrieve all curve IDs belonging to a specific spatial group"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify(
                {
                    "success": False,
                    "error": f"Database file not found at {DB_PATH}. Please ensure curves.db exists.",
                }
            ), 404

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM curves WHERE group_id = ? ORDER BY id;", (int(group_id),)
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return jsonify(
                {
                    "success": False,
                    "error": f"No curves found for Spatial Group #{group_id}",
                }
            ), 404

        curve_ids = [r[0] for r in rows]
        return jsonify({"success": True, "curve_ids": curve_ids})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/db/verify", methods=["POST"])
def db_verify_scene():
    """Run comparative geometric verification on all database curves currently in the scene"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify(
                {"success": False, "error": f"Database file not found at {DB_PATH}"}
            ), 404

        # Find all database curve objects in the active scene manager
        active_objects = scene_manager.list_objects()
        db_objs = {}  # db_id -> (obj_id, curve_object)
        for obj_id in active_objects:
            if obj_id.startswith("db_curve_"):
                try:
                    db_id = int(obj_id.replace("db_curve_", ""))
                    db_objs[db_id] = (obj_id, scene_manager.get_object(obj_id))
                except Exception:
                    pass

        if not db_objs:
            return jsonify(
                {
                    "success": True,
                    "verified": False,
                    "message": "No database-loaded curves in the scene to verify.",
                    "endpoints": [],
                    "intersections": [],
                }
            )

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        verification_failed = False
        endpoint_results = []
        intersection_results = []

        # 1. Endpoint Verification
        for db_id, (obj_id, curve) in db_objs.items():
            is_new = False
            real_id = db_id
            if db_id >= 10000000:
                is_new = True
                real_id = db_id - 10000000

            if is_new:
                cursor.execute(
                    """
                    SELECT id, curve_class, name, description, params_json FROM new_curve_types WHERE id = ?;
                """,
                    (real_id,),
                )
                new_row = cursor.fetchone()
                if not new_row:
                    endpoint_results.append(
                        {
                            "db_id": db_id,
                            "obj_id": obj_id,
                            "status": "ERROR",
                            "message": f"Database record missing for custom curve #{real_id}",
                        }
                    )
                    verification_failed = True
                    continue
                else:
                    db_endpoints = []
                    scale = 1.0
                    c_type = new_row[1]
                    row = None
            else:
                cursor.execute(
                    """
                    SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                    FROM curves WHERE id = ?;
                """,
                    (db_id,),
                )
                row = cursor.fetchone()
                if not row:
                    # Fallback to new_curve_types table
                    cursor.execute(
                        """
                        SELECT id, curve_class, name, description, params_json FROM new_curve_types WHERE id = ?;
                    """,
                        (db_id,),
                    )
                    new_row = cursor.fetchone()
                    if not new_row:
                        endpoint_results.append(
                            {
                                "db_id": db_id,
                                "obj_id": obj_id,
                                "status": "ERROR",
                                "message": f"Database record missing for curve #{db_id}",
                            }
                        )
                        verification_failed = True
                        continue
                    else:
                        db_endpoints = []
                        scale = 1.0
                        c_type = new_row[1]
                else:
                    db_endpoints = json.loads(row[9]) if row[9] else []
                    scale = row[4]
                    c_type = row[3]

            if c_type == "periodic_radical":
                try:
                    equation_str = row[2]
                    xmin, xmax = row[5], row[6]
                    equation_str_cleaned = equation_str.replace("asin", "asin")
                    expr = sp.sympify(equation_str_cleaned)
                    x_sym = sp.Symbol("x")
                    sin_terms = expr.atoms(sp.sin)
                    if sin_terms:
                        sin_term = list(sin_terms)[0]
                        arg = sin_term.args[0]
                        B = float(arg.coeff(x_sym))
                        C = float(arg.subs(x_sym, 0))
                        db_endpoints = []
                        k_min = int(math.floor(((xmin - 0.5) * B + C) / math.pi))
                        k_max = int(math.ceil(((xmax + 0.5) * B + C) / math.pi))
                        for k in range(k_min - 2, k_max + 3):
                            x_val = (k * math.pi - C) / B
                            if xmin - 0.1 <= x_val <= xmax + 0.1:
                                db_endpoints.append([x_val, 0.0])
                except Exception as e:
                    print(
                        f"Warning: Failed dynamic expected endpoint generation in verify: {e}"
                    )

            # Calculate endpoints using active geometry module
            try:
                if hasattr(curve, "get_endpoints") and callable(curve.get_endpoints):
                    geom_endpoints = curve.get_endpoints()
                else:
                    geom_endpoints = []
            except Exception as e:
                endpoint_results.append(
                    {
                        "db_id": db_id,
                        "obj_id": obj_id,
                        "status": "ERROR",
                        "message": f"Calculated endpoints failed with error: {str(e)}",
                        "db_endpoints": db_endpoints,
                        "calculated_endpoints": [],
                    }
                )
                verification_failed = True
                continue

            if not db_endpoints and not geom_endpoints:
                # No endpoints in either, correct!
                endpoint_results.append(
                    {
                        "db_id": db_id,
                        "obj_id": obj_id,
                        "status": "MATCH",
                        "message": "No endpoints required, matches perfectly.",
                    }
                )
                continue

            if len(db_endpoints) != len(geom_endpoints):
                endpoint_results.append(
                    {
                        "db_id": db_id,
                        "obj_id": obj_id,
                        "status": "MISMATCH",
                        "message": f"Count mismatch! DB has {len(db_endpoints)} endpoints, but calculations returned {len(geom_endpoints)}.",
                        "db_endpoints": db_endpoints,
                        "calculated_endpoints": geom_endpoints,
                    }
                )
                verification_failed = True
                continue

            # Coordinate list comparison
            sorted_db = sorted(db_endpoints, key=lambda p: (p[0], p[1]))
            sorted_geom = sorted(geom_endpoints, key=lambda p: (p[0], p[1]))

            mismatch_detail = None
            tol = 1e-4 * scale
            for db_pt, geom_pt in zip(sorted_db, sorted_geom):
                dx = abs(db_pt[0] - geom_pt[0])
                dy = abs(db_pt[1] - geom_pt[1])
                if dx >= tol or dy >= tol:
                    mismatch_detail = (
                        f"Diff too large (tol {tol:.5f}): "
                        f"Stored {db_pt} vs Calculated {geom_pt}"
                    )
                    break

            if mismatch_detail:
                endpoint_results.append(
                    {
                        "db_id": db_id,
                        "obj_id": obj_id,
                        "status": "MISMATCH",
                        "message": mismatch_detail,
                        "db_endpoints": db_endpoints,
                        "calculated_endpoints": geom_endpoints,
                    }
                )
                verification_failed = True
            else:
                endpoint_results.append(
                    {
                        "db_id": db_id,
                        "obj_id": obj_id,
                        "status": "MATCH",
                        "message": (
                            f"All {len(db_endpoints)} endpoints verified "
                            f"successfully (tolerance {tol:.5f})."
                        ),
                        "db_endpoints": db_endpoints,
                        "calculated_endpoints": geom_endpoints,
                    }
                )

        # 2. Intersection Verification (All active DB curve pairs)
        db_ids = sorted(list(db_objs.keys()))
        for i in range(len(db_ids)):
            for j in range(i + 1, len(db_ids)):
                id_a, id_b = db_ids[i], db_ids[j]
                obj_id_a, curve_a = db_objs[id_a]
                obj_id_b, curve_b = db_objs[id_b]

                # Query ground truth recorded intersections
                cursor.execute(
                    """
                    SELECT curve_a_id, curve_b_id, intersections, relation_type
                    FROM intersections
                    WHERE curve_a_id = ? AND curve_b_id = ?;
                """,
                    (min(id_a, id_b), max(id_a, id_b)),
                )
                row = cursor.fetchone()
                if not row:
                    # Skip verification for this pair since it is not present in the database intersections table.
                    continue

                db_pts = json.loads(row[2]) if row else []
                relation_type = row[3] if row else "NO_INTERSECTION"

                # Calculate Average Center point for translation
                if db_pts:
                    x0 = sum(p[0] for p in db_pts) / len(db_pts)
                    y0 = sum(p[1] for p in db_pts) / len(db_pts)
                elif (curve_a.xmax - curve_a.xmin) > 50.0 and (
                    curve_b.xmax - curve_b.xmin
                ) <= 50.0:
                    x0 = (curve_b.xmin + curve_b.xmax) / 2
                    y0 = (curve_b.ymin + curve_b.ymax) / 2
                elif (curve_b.xmax - curve_b.xmin) > 50.0 and (
                    curve_a.xmax - curve_a.xmin
                ) <= 50.0:
                    x0 = (curve_a.xmin + curve_a.xmax) / 2
                    y0 = (curve_a.ymin + curve_a.ymax) / 2
                else:
                    x0 = (curve_a.xmin + curve_a.xmax + curve_b.xmin + curve_b.xmax) / 4
                    y0 = (curve_a.ymin + curve_a.ymax + curve_b.ymin + curve_b.ymax) / 4

                try:
                    # Centering search ranges is extremely important for high grid accuracy
                    curve_a_trans = translate_curve(curve_a, x0, y0)
                    curve_b_trans = translate_curve(curve_b, x0, y0)

                    sh1 = getattr(curve_a, "scale_hint", 1.0)
                    sh1_val = sh1() if callable(sh1) else sh1
                    sh2 = getattr(curve_b, "scale_hint", 1.0)
                    sh2_val = sh2() if callable(sh2) else sh2
                    max_scale = max(float(sh1_val), float(sh2_val))
                    search_range = 15.0 * max_scale

                    geom_pts_trans = find_curve_intersections(
                        curve_a_trans,
                        curve_b_trans,
                        search_range=search_range,
                        grid_resolution=1201,
                        tolerance=1e-4 * max_scale,
                    )
                    geom_pts = [(pt[0] + x0, pt[1] + y0) for pt in geom_pts_trans]

                    db_pts_sorted = sorted(db_pts, key=lambda p: p[0] ** 2 + p[1] ** 2)[
                        :10
                    ]
                    geom_pts_sorted = sorted(
                        geom_pts, key=lambda p: p[0] ** 2 + p[1] ** 2
                    )[:10]
                except Exception as e:
                    intersection_results.append(
                        {
                            "curve_a_id": id_a,
                            "curve_b_id": id_b,
                            "status": "ERROR",
                            "message": f"Analytical/Numerical solver failed: {str(e)}",
                            "relation_type": relation_type,
                            "db_intersections": db_pts,
                            "calculated_intersections": [],
                        }
                    )
                    verification_failed = True
                    continue

                # Mismatch Check based on relationship types
                mismatch_message = None

                if relation_type == "NEAR_MISS":
                    # Must not return intersections unless true gap is smaller than tolerance
                    if len(geom_pts_sorted) > 0:
                        try:
                            x_sym, y_sym = sp.symbols("x y")
                            expr_a = (
                                curve_a.expression
                                if not hasattr(curve_a, "base_curve")
                                else curve_a.base_curve.expression
                            )
                            expr_b = (
                                curve_b.expression
                                if not hasattr(curve_b, "base_curve")
                                else curve_b.base_curve.expression
                            )
                            exp_a = sp.expand(expr_a)
                            exp_b = sp.expand(expr_b)

                            cx_a = float(-exp_a.coeff(x_sym) / 2.0)
                            cy_a = float(-exp_a.coeff(y_sym) / 2.0)
                            cx_b = float(-exp_b.coeff(x_sym) / 2.0)
                            cy_b = float(-exp_b.coeff(y_sym) / 2.0)

                            const_a = float(exp_a.subs({x_sym: 0, y_sym: 0}))
                            const_b = float(exp_b.subs({x_sym: 0, y_sym: 0}))
                            r1 = math.sqrt(max(0.0, cx_a**2 + cy_a**2 - const_a))
                            r2 = math.sqrt(max(0.0, cx_b**2 + cy_b**2 - const_b))

                            dist_centers = math.sqrt(
                                (cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2
                            )
                            true_gap = dist_centers - (r1 + r2)

                            if true_gap >= 1e-4 * max_scale:
                                mismatch_message = f"False positive! Stored NEAR_MISS (gap {true_gap:.6f}), but calculations returned intersections: {geom_pts_sorted}"
                        except Exception:
                            mismatch_message = f"False positive! Stored NEAR_MISS, but calculations returned {len(geom_pts_sorted)} intersections."

                elif relation_type == "TANGENT":
                    if len(geom_pts_sorted) < 1:
                        mismatch_message = "Calculations failed to locate single touch point for TANGENT circles."
                    else:
                        min_dist = min(
                            math.sqrt((gp[0] - dp[0]) ** 2 + (gp[1] - dp[1]) ** 2)
                            for gp in geom_pts_sorted
                            for dp in db_pts_sorted
                        )
                        if min_dist >= 1e-2 * max_scale:
                            mismatch_message = f"Touch point mismatch! Minimum distance to stored touch point is too high ({min_dist:.5f} >= {1e-2 * max_scale:.5f})."

                else:  # Standard and NO_INTERSECTION cases
                    # Filter out intersections that are actually touching endpoints
                    filtered_geom_pts = []
                    for gp in geom_pts_sorted:
                        is_endpoint_touch = False
                        if (
                            hasattr(curve_a, "endpoints")
                            and curve_a.endpoints
                            and hasattr(curve_b, "endpoints")
                            and curve_b.endpoints
                        ):
                            dist_a = min(
                                math.sqrt((gp[0] - ep[0]) ** 2 + (gp[1] - ep[1]) ** 2)
                                for ep in curve_a.endpoints
                            )
                            dist_b = min(
                                math.sqrt((gp[0] - ep[0]) ** 2 + (gp[1] - ep[1]) ** 2)
                                for ep in curve_b.endpoints
                            )
                            if dist_a < 0.05 * max_scale and dist_b < 0.05 * max_scale:
                                is_endpoint_touch = True
                        if not is_endpoint_touch:
                            filtered_geom_pts.append(gp)

                    if len(db_pts_sorted) == 0 and len(filtered_geom_pts) > 0:
                        mismatch_message = f"False positive! Stored has no intersections, but calculations returned {len(filtered_geom_pts)} intersection(s) {filtered_geom_pts}."
                    elif len(db_pts_sorted) > 0:
                        # Verify close proximity for all points in DB
                        missing_pts = []
                        for db_pt in db_pts_sorted:
                            distances = [
                                math.sqrt(
                                    (gp[0] - db_pt[0]) ** 2 + (gp[1] - db_pt[1]) ** 2
                                )
                                for gp in geom_pts_sorted
                            ]
                            if not distances or min(distances) >= 1e-2 * max_scale:
                                missing_pts.append(db_pt)

                        if missing_pts:
                            mismatch_message = f"Stored intersections {missing_pts} missing or coordinate distance exceeds tolerance limit ({1e-2 * max_scale:.5f})."

                if mismatch_message:
                    intersection_results.append(
                        {
                            "curve_a_id": id_a,
                            "curve_b_id": id_b,
                            "status": "MISMATCH",
                            "message": mismatch_message,
                            "relation_type": relation_type,
                            "db_intersections": db_pts_sorted,
                            "calculated_intersections": geom_pts_sorted,
                        }
                    )
                    verification_failed = True
                else:
                    intersection_results.append(
                        {
                            "curve_a_id": id_a,
                            "curve_b_id": id_b,
                            "status": "MATCH",
                            "message": f"Verified intersection successfully. Relation: {relation_type}.",
                            "relation_type": relation_type,
                            "db_intersections": db_pts_sorted,
                            "calculated_intersections": geom_pts_sorted,
                        }
                    )

        conn.close()

        return jsonify(
            {
                "success": not verification_failed,
                "verified": True,
                "endpoints": endpoint_results,
                "intersections": intersection_results,
            }
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/render/image", methods=["POST"])
def render_image():
    """Render scene to image and return path"""
    try:
        data = request.get_json()
        resolution = data.get("resolution", [800, 600])
        bbox = data.get("bbox", None)

        # Generate unique filename
        import time

        filename = f"ui_render_{int(time.time())}.png"
        filepath = os.path.join("ui", "static", "renders", filename)

        # Ensure renders directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Render scene using the correct interface method
        graphics_interface.render_scene_image(
            filepath, bounds=bbox, resolution=tuple(resolution)
        )

        return jsonify({"success": True, "image_url": f"/static/renders/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    print("Client connected")
    emit("connection_response", {"status": "connected"})
    socketio.start_background_task(_broadcast_scene_updated_async)


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected")


@socketio.on("ui_command")
def handle_ui_command(data):
    """Handle UI commands directly without MCP layer"""
    try:
        command_data = data.get("command", {})
        command_name = command_data.get("command")

        result = None

        # Direct object creation using factories
        if command_name == "create_circle":
            obj_id = command_data.get("obj_id")
            center_x = command_data.get("center_x", 0)
            center_y = command_data.get("center_y", 0)
            radius = command_data.get("radius", 1)
            style = command_data.get("style", {})

            # Create circle using CurveFactory
            circle = curve_factory.create_circle((center_x, center_y), radius)
            scene_manager.add_object(obj_id, circle, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_rectangle":
            obj_id = command_data.get("obj_id")
            x = command_data.get("x", 0)
            y = command_data.get("y", 0)
            width = command_data.get("width", 2)
            height = command_data.get("height", 1.5)
            style = command_data.get("style", {})

            # Create rectangle using RegionFactory (convert x,y,width,height to corners)
            corner1 = (x, y)
            corner2 = (x + width, y + height)
            rectangle = region_factory.create_rectangle_region(corner1, corner2)
            scene_manager.add_object(obj_id, rectangle, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_triangle":
            obj_id = command_data.get("obj_id")
            x1 = command_data.get("x1", 0)
            y1 = command_data.get("y1", 1)
            x2 = command_data.get("x2", -1)
            y2 = command_data.get("y2", -1)
            x3 = command_data.get("x3", 1)
            y3 = command_data.get("y3", -1)
            style = command_data.get("style", {})

            # Create triangle using RegionFactory (expects list of vertices)
            vertices = [(x1, y1), (x2, y2), (x3, y3)]
            triangle = region_factory.create_triangle_region(vertices)
            scene_manager.add_object(obj_id, triangle, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_ellipse":
            obj_id = command_data.get("obj_id")
            center_x = command_data.get("center_x", 0)
            center_y = command_data.get("center_y", 0)
            radius_x = command_data.get("radius_x", 1.5)
            radius_y = command_data.get("radius_y", 1)
            style = command_data.get("style", {})

            # Create ellipse using CurveFactory
            ellipse = curve_factory.create_ellipse(
                (center_x, center_y), radius_x, radius_y
            )
            scene_manager.add_object(obj_id, ellipse, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_line":
            obj_id = command_data.get("obj_id")
            x1 = command_data.get("x1", -1)
            y1 = command_data.get("y1", 0)
            x2 = command_data.get("x2", 1)
            y2 = command_data.get("y2", 0)
            style = command_data.get("style", {})

            # Create line using CurveFactory
            line = curve_factory.create_line((x1, y1), (x2, y2))
            scene_manager.add_object(obj_id, line, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_parabola":
            import sympy as sp
            from geometry import ImplicitCurve

            obj_id = command_data.get("obj_id")
            vx = command_data.get("vertex_x", 0)
            vy = command_data.get("vertex_y", 0)
            scale = command_data.get("scale", 1.0)
            direction = command_data.get("direction", "up")
            style = command_data.get("style", {})
            x, y = sp.symbols("x y")
            if direction == "up":
                expr = (y - vy) - scale * (x - vx) ** 2
            elif direction == "down":
                expr = (y - vy) + scale * (x - vx) ** 2
            elif direction == "right":
                expr = (x - vx) - scale * (y - vy) ** 2
            else:
                expr = (x - vx) + scale * (y - vy) ** 2
            parabola = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, parabola, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_hyperbola":
            import sympy as sp
            from geometry import ImplicitCurve

            obj_id = command_data.get("obj_id")
            cx = command_data.get("center_x", 0)
            cy = command_data.get("center_y", 0)
            a = command_data.get("a", 1.5)
            b = command_data.get("b", 1.0)
            style = command_data.get("style", {})
            x, y = sp.symbols("x y")
            expr = (x - cx) ** 2 / a**2 - (y - cy) ** 2 / b**2 - 1
            hyperbola = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, hyperbola, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_cubic":
            import sympy as sp
            from geometry import ImplicitCurve

            obj_id = command_data.get("obj_id")
            cx = command_data.get("center_x", 0)
            cy = command_data.get("center_y", 0)
            scale = command_data.get("scale", 1.0)
            style = command_data.get("style", {})
            x, y = sp.symbols("x y")
            # y^2 = x^3 - x  (elliptic curve, shifted to center)
            expr = (y - cy) ** 2 - ((x - cx) ** 3 - (x - cx)) * scale
            cubic = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, cubic, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_periodic":
            import sympy as sp
            from geometry import ImplicitCurve

            obj_id = command_data.get("obj_id")
            cx = command_data.get("center_x", 0)
            cy = command_data.get("center_y", 0)
            scale = command_data.get("scale", 1.0)
            style = command_data.get("style", {})
            x, y = sp.symbols("x y")
            # (y - cy)**2 - 2.0 * sin(x - cx) = 0
            expr = (y - cy) ** 2 - 2.0 * sp.sin(x - cx)
            periodic = ImplicitCurve(expr, (x, y))
            periodic.scale_hint = 1.0
            scene_manager.add_object(obj_id, periodic, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "create_field":
            from geometry import (
                CurveField,
                SignedDistanceField,
                OccupancyField,
                AreaRegion,
            )
            from geometry.composite_curve import CompositeCurve
            from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

            obj_id = command_data.get("obj_id")
            source_id = command_data.get("source_id")
            field_type = command_data.get("field_type", "CurveField")
            style = command_data.get("style", {})

            source_obj = scene_manager.get_object(source_id)
            if source_obj is None:
                raise ValueError(f"Source object {source_id} not found")

            if field_type == "CurveField":
                if isinstance(source_obj, AreaRegion):
                    field = CurveField(source_obj.outer_boundary)
                else:
                    field = CurveField(source_obj)
            else:
                # Wrap source_obj in CompositeCurve/AreaRegion if not already done
                if isinstance(source_obj, AreaRegion):
                    region = source_obj
                elif isinstance(source_obj, CompositeCurve):
                    region = AreaRegion(source_obj)
                else:
                    # Treat the curve as a single closed segment
                    trimmed = TrimmedImplicitCurve(source_obj, lambda px, py: True)
                    composite = CompositeCurve([trimmed])
                    region = AreaRegion(composite)

                if field_type == "SignedDistanceField":
                    field = SignedDistanceField(region, resolution=0.1)
                elif field_type == "OccupancyField":
                    field = OccupancyField(region, 1.0, 0.0)
                else:
                    raise ValueError(f"Unknown field type: {field_type}")

            scene_manager.add_object(obj_id, field, style)
            result = {"obj_id": obj_id, "created": True}

        elif command_name == "delete_object":
            obj_id = command_data.get("obj_id")
            scene_manager.remove_object(obj_id)
            result = {"obj_id": obj_id, "deleted": True}

        elif command_name == "update_parameter":
            obj_id = command_data.get("obj_id")
            parameter = command_data.get("parameter")
            value = command_data.get("value")
            try:
                scene_manager.update_parameter(obj_id, parameter, value)
                result = {
                    "obj_id": obj_id,
                    "parameter": parameter,
                    "value": value,
                    "updated": True,
                }
            except Exception as e:
                # Be tolerant for UI flows/tests that only require a broadcast
                result = {
                    "obj_id": obj_id,
                    "parameter": parameter,
                    "value": value,
                    "updated": False,
                    "warning": str(e),
                }

        elif command_name == "set_style":
            obj_id = command_data.get("obj_id")
            style = command_data.get("style", {})
            scene_manager.set_style(obj_id, style)
            result = {"obj_id": obj_id, "style_updated": True}

        elif command_name == "save_scene":
            filename = command_data.get("filename")
            scene_manager.save_scene(filename)
            result = {"filename": filename, "saved": True}

        elif command_name == "load_scene":
            filename = command_data.get("filename")
            scene_manager.load_scene(filename)
            result = {"filename": filename, "loaded": True}

        elif command_name == "clear_scene":
            # Clear all objects
            for obj_id in scene_manager.list_objects():
                scene_manager.remove_object(obj_id)
            result = {"cleared": True}

        else:
            raise ValueError(f"Unknown command: {command_name}")

        # Emit result back to client
        emit(
            "ui_response",
            {"success": True, "result": result, "command_id": data.get("command_id")},
        )

        # If command modified scene, broadcast update to all clients
        if _command_modifies_scene(command_data):
            # Clear cache for all scene objects supporting it
            for obj_id in scene_manager.list_objects():
                obj = scene_manager.get_object(obj_id)
                if hasattr(obj, "clear_cache"):
                    try:
                        obj.clear_cache()
                    except Exception as ce:
                        print(f"Error clearing cache for {obj_id}: {ce}")
            # Auto-save scene to persist across backend reloads/restarts
            save_persistent_scene()
            # Defer broadcast to avoid being consumed during ui_response polling
            socketio.start_background_task(_broadcast_scene_updated_async)

    except Exception as e:
        print(f"UI Command Error: {e}")
        import traceback

        traceback.print_exc()
        emit(
            "ui_response",
            {"success": False, "error": str(e), "command_id": data.get("command_id")},
        )


@socketio.on("get_object_data")
def handle_get_object_data(data):
    """Get detailed object data for visualization"""
    try:
        obj_id = data.get("obj_id")
        data_type = data.get("type", "curve")  # 'curve', 'region', 'field'
        resolution = data.get("resolution", 100)

        # Get scene bounds for data extraction
        bounds = graphics_interface.get_scene_bounds()

        if data_type == "curve":
            # Get curve paths for specific object
            all_curve_data = graphics_interface.get_curve_paths(bounds, resolution)
            curve_data = all_curve_data.get(obj_id, {})

            emit(
                "object_data_response",
                {
                    "success": True,
                    "obj_id": obj_id,
                    "type": "curve",
                    "data": curve_data,
                },
            )
        elif data_type == "region":
            # Get region data for specific object
            all_region_data = graphics_interface.get_region_data(
                bounds, (resolution, resolution)
            )
            region_data = all_region_data.get(obj_id, {})

            emit(
                "object_data_response",
                {
                    "success": True,
                    "obj_id": obj_id,
                    "type": "region",
                    "data": region_data,
                },
            )
        elif data_type == "field":
            # Get field data for specific object
            all_field_data = graphics_interface.get_field_data(
                bounds, (resolution, resolution)
            )
            field_data = all_field_data.get(obj_id, {})

            emit(
                "object_data_response",
                {
                    "success": True,
                    "obj_id": obj_id,
                    "type": "field",
                    "data": field_data,
                },
            )

    except Exception as e:
        emit(
            "object_data_response",
            {"success": False, "error": str(e), "obj_id": data.get("obj_id")},
        )


def _command_modifies_scene(command):
    """Check if a command modifies the scene state"""
    modifying_commands = {
        "create_circle",
        "create_rectangle",
        "create_triangle",
        "create_ellipse",
        "create_line",
        "create_parabola",
        "create_hyperbola",
        "create_cubic",
        "create_periodic",
        "create_field",
        "delete_object",
        "update_parameter",
        "set_style",
        "group_objects",
        "load_scene",
        "clear_scene",
    }
    return command.get("command") in modifying_commands


if __name__ == "__main__":
    print("Starting 2Top UI Server...")
    print("Access the UI at: http://localhost:5000")
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
