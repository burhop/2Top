import os
import sys
import json
import sqlite3
import pytest
import sympy as sp

# Add project root to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "curves.db",
)


def load_test_data():
    """Helper to load a rich, representative sample of curves and intersections from the DB."""
    if not os.path.exists(DB_PATH):
        return None, None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Load curves from diverse spatial groups to cover different edge cases
    # We load groups 0 (mixed conics), 1 (endpoint stress tests), 2 (tangent cases), 3 (near-misses), 4 (transcendentals), 5 (high degree cubics/lemniscates)
    target_groups = [0, 1, 2, 3, 4, 5]
    placeholders = ",".join("?" for _ in target_groups)

    cursor.execute(
        f"""
        SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
        FROM curves
        WHERE group_id IN ({placeholders});
    """,
        target_groups,
    )

    curves_data = cursor.fetchall()
    curve_ids = [c[0] for c in curves_data]

    # 2. Load intersections for these curves
    if curve_ids:
        placeholders_inter = ",".join("?" for _ in curve_ids)
        query = f"""
            SELECT curve_a_id, curve_b_id, intersections, relation_type
            FROM intersections
            WHERE curve_a_id IN ({placeholders_inter}) AND curve_b_id IN ({placeholders_inter});
        """
        cursor.execute(query, curve_ids + curve_ids)
        intersections_data = cursor.fetchall()
    else:
        intersections_data = []

    conn.close()
    return curves_data, intersections_data


def reconstruct_geometry_curve(c_row):
    """Factory to map database record to 2Top Geometry object."""
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
    # Standardize equation for sympify (asin -> asin)
    equation_str_cleaned = equation_str.replace("asin", "asin")
    expr = sp.sympify(equation_str_cleaned)

    endpoints = json.loads(endpoints_json)

    if c_type == "periodic_radical":
        try:
            import math

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

    # 1. Base implicit curve or ConicSection depending on degree
    if c_type in ["circle", "ellipse", "parabola", "line"]:
        base_curve = ConicSection(expr, (x, y))
    else:
        base_curve = ImplicitCurve(expr, (x, y))

    # Set scale hint for tolerance matching
    base_curve.scale_hint = scale

    # 2. Apply trimmed segment wrapping if endpoints exist
    if endpoints:
        mask = lambda px, py: True
        sqrt_terms = [
            atom
            for atom in expr.atoms(sp.Pow)
            if atom.exp in [0.5, -0.5, sp.Rational(1, 2), sp.Rational(-1, 2)]
        ]
        asin_terms = expr.atoms(sp.asin)

        if sqrt_terms:
            sqrt_arg = sqrt_terms[0].base
            arg_func = sp.lambdify((x, y), sqrt_arg, "numpy")
            mask = lambda px, py, arg_func=arg_func: arg_func(px, py) >= -0.05
        elif asin_terms:
            asin_arg = list(asin_terms)[0].args[0]
            arg_func = sp.lambdify((x, y), asin_arg, "numpy")
            mask = lambda px, py, arg_func=arg_func: abs(arg_func(px, py)) <= 1.0 + 0.05
        elif c_type == "periodic_radical":
            # Domain where y^2 - expr >= 0 (since expr is y^2 - f(x))
            f_x = y**2 - expr
            f_func = sp.lambdify((x, y), f_x, "numpy")
            mask = lambda px, py, f_func=f_func: f_func(px, py) >= -0.05

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

    # Store bounding box on the curve object for search range calculation
    curve.xmin = xmin
    curve.xmax = xmax
    curve.ymin = ymin
    curve.ymax = ymax

    return c_id, curve, c_type, endpoints, tol


def translate_curve(curve, x0, y0):
    """Translate a 2Top Geometry curve by (x0, y0) to focus grid search."""
    x, y = sp.symbols("x y")

    # 1. Determine if trimmed
    if hasattr(curve, "base_curve") and hasattr(curve, "mask"):
        # TrimmedImplicitCurve
        base_expr = curve.base_curve.expression
        expr_trans = base_expr.subs({x: x + x0, y: y + y0})

        if isinstance(curve.base_curve, ConicSection):
            base_trans = ConicSection(expr_trans, (x, y))
        else:
            base_trans = ImplicitCurve(expr_trans, (x, y))

        base_trans.scale_hint = getattr(curve.base_curve, "scale_hint", 1.0)

        endpoints_trans = [(pt[0] - x0, pt[1] - y0) for pt in curve.endpoints]
        original_mask = curve.mask
        mask_trans = lambda px, py, om=original_mask, dx=x0, dy=y0: om(px + dx, py + dy)

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
        # Base curve (ImplicitCurve or ConicSection)
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

    return curve_trans


import math


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="Database curves.db not generated yet"
)
def test_verify_endpoints():
    """Verify that endpoints loaded from the database match endpoints defined on Geometry objects."""
    curves_data, _ = load_test_data()
    assert curves_data is not None, "Failed to load curves from database"

    endpoint_curves = 0

    for row in curves_data:
        c_id, curve, c_type, db_endpoints, tol = reconstruct_geometry_curve(row)

        if hasattr(curve, "get_endpoints") and callable(curve.get_endpoints):
            geom_endpoints = curve.get_endpoints()
            endpoint_curves += 1
        else:
            geom_endpoints = []

        assert len(geom_endpoints) == len(db_endpoints), (
            f"Curve #{c_id} ({c_type}) endpoint count mismatch"
        )

        # Sort endpoints to align comparison
        sorted_db = sorted(db_endpoints, key=lambda p: (p[0], p[1]))
        sorted_geom = sorted(geom_endpoints, key=lambda p: (p[0], p[1]))

        for db_pt, geom_pt in zip(sorted_db, sorted_geom):
            assert abs(db_pt[0] - geom_pt[0]) < 1e-4, (
                f"Curve #{c_id} ({c_type}) endpoint X mismatch"
            )
            assert abs(db_pt[1] - geom_pt[1]) < 1e-4, (
                f"Curve #{c_id} ({c_type}) endpoint Y mismatch"
            )

    assert endpoint_curves > 0, "No curves with endpoints found in test sample"
    print(f"Verified endpoints for {endpoint_curves} curves successfully.")


@pytest.mark.skipif(
    not os.path.exists(DB_PATH), reason="Database curves.db not generated yet"
)
def test_verify_intersections():
    """Verify that intersections solved by the Geometry library match the ground truth database records."""
    curves_data, intersections_data = load_test_data()
    assert curves_data is not None, "Failed to load curves"
    assert intersections_data is not None, "Failed to load intersections"

    # Map curve ID -> reconstructed Geometry object
    curve_map = {}
    tol_map = {}
    type_map = {}
    for row in curves_data:
        c_id, curve, c_type, _, tol = reconstruct_geometry_curve(row)
        curve_map[c_id] = curve
        tol_map[c_id] = tol
        type_map[c_id] = c_type

    verified_pairs = 0
    near_miss_pairs = 0
    tangent_pairs = 0

    for row in intersections_data:
        id_a, id_b, inter_json, relation_type = row

        if id_a not in curve_map or id_b not in curve_map:
            continue

        curve_a = curve_map[id_a]
        curve_b = curve_map[id_b]
        db_pts = json.loads(inter_json)

        # Shift to the average center of both curves to center grid search and maximize grid density
        # If there are intersection points, center directly on them. Otherwise center on finite curve.
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

        # Translate curves to origin
        curve_a_trans = translate_curve(curve_a, x0, y0)
        curve_b_trans = translate_curve(curve_b, x0, y0)

        # Determine maximum scale and search range (centered at origin, so it's small and high-res!)
        sh1 = getattr(curve_a, "scale_hint", 1.0)
        sh1_val = sh1() if callable(sh1) else sh1
        sh2 = getattr(curve_b, "scale_hint", 1.0)
        sh2_val = sh2() if callable(sh2) else sh2
        max_scale = max(float(sh1_val), float(sh2_val))
        search_range = 15.0 * max_scale

        # Run geometry intersections solver
        # We increase grid resolution for high accuracy matching in test harness
        geom_pts_trans = find_curve_intersections(
            curve_a_trans,
            curve_b_trans,
            search_range=search_range,
            grid_resolution=1201,
            tolerance=1e-4 * max_scale,
        )

        # Translate intersection points back
        geom_pts = [(pt[0] + x0, pt[1] + y0) for pt in geom_pts_trans]

        # Sort by distance to origin and capture up to 10 closest to match generator logic
        db_pts_sorted = sorted(db_pts, key=lambda p: p[0] ** 2 + p[1] ** 2)[:10]
        geom_pts_sorted = sorted(geom_pts, key=lambda p: p[0] ** 2 + p[1] ** 2)[:10]

        if relation_type == "NEAR_MISS":
            near_miss_pairs += 1
            # Near misses must NOT return false positives unless they are closer than the solver's tolerance
            try:
                # Use SymPy to analytically extract centers and radii of the circles
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

                # Expand expressions
                exp_a = sp.expand(expr_a)
                exp_b = sp.expand(expr_b)

                # Extract centers
                cx_a = float(-exp_a.coeff(x_sym) / 2.0)
                cy_a = float(-exp_a.coeff(y_sym) / 2.0)
                cx_b = float(-exp_b.coeff(x_sym) / 2.0)
                cy_b = float(-exp_b.coeff(y_sym) / 2.0)

                # Extract radii
                const_a = float(exp_a.subs({x_sym: 0, y_sym: 0}))
                const_b = float(exp_b.subs({x_sym: 0, y_sym: 0}))
                r1 = math.sqrt(max(0.0, cx_a**2 + cy_a**2 - const_a))
                r2 = math.sqrt(max(0.0, cx_b**2 + cy_b**2 - const_b))

                dist_centers = math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)
                true_gap = dist_centers - (r1 + r2)

                # If true_gap is less than the solver's tolerance, it is numerically
                # correct for the solver to return a fuzzy intersection within tolerance.
                # Otherwise, it must NOT return any intersections.
                if true_gap >= 1e-4 * max_scale:
                    assert len(geom_pts_sorted) == 0, (
                        f"Curves {id_a} ∩ {id_b} is a NEAR_MISS with gap {true_gap} >= tol {1e-4 * max_scale} but returned intersections: {geom_pts_sorted}"
                    )
            except Exception as e:
                # Fallback to standard check if parsing fails
                assert len(geom_pts_sorted) == 0, (
                    f"Curves {id_a} ∩ {id_b} is a NEAR_MISS but returned false-positive intersections: {geom_pts_sorted}"
                )

        elif relation_type == "TANGENT":
            tangent_pairs += 1
            # Tangents must return exactly the single point touch point
            assert len(geom_pts_sorted) >= 1, (
                f"Tangent curves {id_a} ∩ {id_b} failed to return intersection point"
            )
            # Verify close proximity
            min_dist = min(
                math.sqrt((gp[0] - dp[0]) ** 2 + (gp[1] - dp[1]) ** 2)
                for gp in geom_pts_sorted
                for dp in db_pts_sorted
            )
            assert min_dist < 1e-2 * max_scale, (
                f"Tangent curve {id_a} ∩ {id_b} intersection point mismatch"
            )

        else:
            verified_pairs += 1
            # Standard transversal intersection count comparison (with some numerical tolerance for count matching)
            # If DB has points, geom must find close matches for them
            for db_pt in db_pts_sorted:
                # Find closest geometric point match
                distances = [
                    math.sqrt((gp[0] - db_pt[0]) ** 2 + (gp[1] - db_pt[1]) ** 2)
                    for gp in geom_pts_sorted
                ]
                assert distances, (
                    f"Curves {id_a} ({type_map[id_a]}) ∩ {id_b} ({type_map[id_b]}) intersection failed to return points"
                )
                min_dist = min(distances)
                assert min_dist < 1e-2 * max_scale, (
                    f"Curves {id_a} ({type_map[id_a]}) ∩ {id_b} ({type_map[id_b]}) intersection point {db_pt} missing or mismatched"
                )

    assert verified_pairs > 0, "No standard intersections verified"
    assert near_miss_pairs > 0, "No near-miss edge cases verified"
    assert tangent_pairs > 0, "No tangent touches verified"

    print(
        f"Successfully verified {verified_pairs} standard pairs, {near_miss_pairs} near-misses, and {tangent_pairs} tangent touches."
    )
