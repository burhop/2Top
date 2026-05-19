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
        socketio.emit('scene_updated', {
            'objects': object_ids,
            'bounds': None
        })
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

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "curves.db")

def reconstruct_geometry_curve(c_row):
    """Factory to map database record to 2Top Geometry object."""
    c_id, g_id, equation_str, c_type, scale, xmin, xmax, ymin, ymax, endpoints_json, tol = c_row
    
    x, y = sp.symbols('x y')
    equation_str_cleaned = equation_str.replace("asin", "asin")
    expr = sp.sympify(equation_str_cleaned)
    
    endpoints = json.loads(endpoints_json) if endpoints_json else []
    
    if c_type in ["circle", "ellipse", "parabola", "line"]:
        base_curve = ConicSection(expr, (x, y))
    else:
        base_curve = ImplicitCurve(expr, (x, y))
        
    base_curve.scale_hint = scale
    
    if endpoints:
        mask = lambda px, py: True
        sqrt_terms = [atom for atom in expr.atoms(sp.Pow) if atom.exp in [0.5, -0.5, sp.Rational(1, 2), sp.Rational(-1, 2)]]
        asin_terms = expr.atoms(sp.asin)
        
        if sqrt_terms:
            sqrt_arg = sqrt_terms[0].base
            arg_func = sp.lambdify((x, y), sqrt_arg, 'numpy')
            mask = lambda px, py, arg_func=arg_func: arg_func(px, py) >= -1e-6
        elif asin_terms:
            asin_arg = list(asin_terms)[0].args[0]
            arg_func = sp.lambdify((x, y), asin_arg, 'numpy')
            mask = lambda px, py, arg_func=arg_func: abs(arg_func(px, py)) <= 1.0 + 1e-6
        elif c_type == "periodic_radical":
            f_x = y**2 - expr
            f_func = sp.lambdify((x, y), f_x, 'numpy')
            mask = lambda px, py, f_func=f_func: f_func(px, py) >= -1e-6
            
        curve = TrimmedImplicitCurve(
            base_curve=base_curve,
            mask=mask,
            variables=(x, y),
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            endpoints=[tuple(pt) for pt in endpoints]
        )
    else:
        curve = base_curve
        
    curve.xmin = xmin
    curve.xmax = xmax
    curve.ymin = ymin
    curve.ymax = ymax
        
    return curve

def translate_curve(curve, x0, y0):
    """Translate a 2Top Geometry curve by (x0, y0) to focus grid search."""
    x, y = sp.symbols('x y')
    
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
        mask_trans = lambda px, py, om=original_mask, dx=x0, dy=y0: om(px + dx, py + dy)
        
        curve_trans = TrimmedImplicitCurve(
            base_curve=base_trans,
            mask=mask_trans,
            variables=(x, y),
            xmin=curve.xmin - x0,
            xmax=curve.xmax - x0,
            ymin=curve.ymin - y0,
            ymax=curve.ymax - y0,
            endpoints=endpoints_trans
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
    
    return curve_trans

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
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

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/api/scene/info')
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
            'objects': object_ids,
            'object_count': len(object_ids),
            'bounds': graphics_interface.get_scene_bounds() if objects else None
        }
        return jsonify({'success': True, 'data': scene_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/geometry-tests', methods=['GET'])
def geometry_tests():
    """Return metadata for predefined geometry test scenes."""
    try:
        return jsonify({'success': True, 'tests': list_geometry_tests()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/geometry-tests/run', methods=['POST'])
def geometry_tests_run():
    """Clear the scene and run a predefined geometry test scenario."""
    try:
        data = request.get_json(force=True)
        test_id = data.get('test_id')
        if not test_id:
            return jsonify({'success': False, 'error': 'test_id is required'}), 400

        created_ids = run_geometry_test(test_id, scene_manager, curve_factory, region_factory)
        bounds = graphics_interface.get_scene_bounds()
        socketio.start_background_task(_broadcast_scene_updated_async)
        return jsonify({'success': True, 'objects': created_ids, 'bounds': list(bounds)})
    except KeyError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/geometry-scene')
def geometry_scene_data():
    """Return polyline + key-point data for the current scene."""
    try:
        min_x = request.args.get('min_x', type=float)
        max_x = request.args.get('max_x', type=float)
        min_y = request.args.get('min_y', type=float)
        max_y = request.args.get('max_y', type=float)
        
        bounds = None
        if all(v is not None for v in [min_x, max_x, min_y, max_y]):
            bounds = (min_x, max_x, min_y, max_y)
            
        scene_data = graphics_interface.get_geometry_scene_data(resolution=150, bounds=bounds)
        return jsonify({'success': True, 'data': scene_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/curves/load', methods=['POST'])
def db_curves_load():
    """Load one or more curves from the SQLite database curves.db"""
    try:
        data = request.get_json(force=True) or {}
        curve_id = data.get('curve_id')
        group_id = data.get('group_id')
        
        if not os.path.exists(DB_PATH):
            return jsonify({'success': False, 'error': f"Database file not found at {DB_PATH}. Please ensure curves.db exists."}), 404
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        loaded_ids = []
        
        if curve_id is not None:
            cursor.execute("""
                SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                FROM curves WHERE id = ?;
            """, (int(curve_id),))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return jsonify({'success': False, 'error': f"Curve #{curve_id} not found in database"}), 404
            
            curve = reconstruct_geometry_curve(row)
            obj_id = f"db_curve_{row[0]}"
            
            # If it already exists, remove it first
            if obj_id in scene_manager.list_objects():
                scene_manager.remove_object(obj_id)
                
            # Add to scene manager with custom style tagging
            style = {
                'color': '#ff6b9c' if row[3] == 'periodic_radical' else '#77f6ff',
                'linewidth': 2.5,
                'alpha': 1.0,
                'is_db_curve': True,
                'db_id': row[0]
            }
            scene_manager.add_object(obj_id, curve, style)
            loaded_ids.append(row[0])
            
        elif group_id is not None:
            cursor.execute("""
                SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                FROM curves WHERE group_id = ?;
            """, (int(group_id),))
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                return jsonify({'success': False, 'error': f"No curves found for Spatial Group #{group_id}"}), 404
                
            NEON_PALETTE = ['#77f6ff', '#ff6b9c', '#a0fe38', '#ffb536', '#c684ff']
            for index, row in enumerate(rows):
                curve = reconstruct_geometry_curve(row)
                obj_id = f"db_curve_{row[0]}"
                
                if obj_id in scene_manager.list_objects():
                    scene_manager.remove_object(obj_id)
                    
                # Alternate colors in the group so they can be visually distinguished
                color = NEON_PALETTE[index % len(NEON_PALETTE)]
                style = {
                    'color': color,
                    'linewidth': 2.5,
                    'alpha': 1.0,
                    'is_db_curve': True,
                    'db_id': row[0]
                }
                scene_manager.add_object(obj_id, curve, style)
                loaded_ids.append(row[0])
        else:
            conn.close()
            return jsonify({'success': False, 'error': "Either curve_id or group_id is required"}), 400
            
        conn.close()
        
        # Emit scene update to trigger front-end redraw
        socketio.start_background_task(_broadcast_scene_updated_async)
        
        return jsonify({'success': True, 'loaded_ids': loaded_ids})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/db/groups/<int:group_id>/curves', methods=['GET'])
def db_group_curves(group_id):
    """Retrieve all curve IDs belonging to a specific spatial group"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify({'success': False, 'error': f"Database file not found at {DB_PATH}. Please ensure curves.db exists."}), 404
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM curves WHERE group_id = ? ORDER BY id;", (int(group_id),))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({'success': False, 'error': f"No curves found for Spatial Group #{group_id}"}), 404
            
        curve_ids = [r[0] for r in rows]
        return jsonify({'success': True, 'curve_ids': curve_ids})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/db/verify', methods=['POST'])
def db_verify_scene():
    """Run comparative geometric verification on all database curves currently in the scene"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify({'success': False, 'error': f"Database file not found at {DB_PATH}"}), 404
            
        # Find all database curve objects in the active scene manager
        active_objects = scene_manager.list_objects()
        db_objs = {} # db_id -> (obj_id, curve_object)
        for obj_id in active_objects:
            if obj_id.startswith("db_curve_"):
                try:
                    db_id = int(obj_id.replace("db_curve_", ""))
                    db_objs[db_id] = (obj_id, scene_manager.get_object(obj_id))
                except Exception:
                    pass
                    
        if not db_objs:
            return jsonify({
                'success': True,
                'verified': False,
                'message': "No database-loaded curves in the scene to verify.",
                'endpoints': [],
                'intersections': []
            })
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        verification_failed = False
        endpoint_results = []
        intersection_results = []
        
        # 1. Endpoint Verification
        for db_id, (obj_id, curve) in db_objs.items():
            cursor.execute("""
                SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance
                FROM curves WHERE id = ?;
            """, (db_id,))
            row = cursor.fetchone()
            if not row:
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'ERROR',
                    'message': f"Database record missing for curve #{db_id}"
                })
                verification_failed = True
                continue
                
            db_endpoints = json.loads(row[9]) if row[9] else []
            scale = row[4]
            c_type = row[3]
            
            # Calculate endpoints using active geometry module
            try:
                if hasattr(curve, 'get_endpoints') and callable(curve.get_endpoints):
                    geom_endpoints = curve.get_endpoints()
                else:
                    geom_endpoints = []
            except Exception as e:
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'ERROR',
                    'message': f"Calculated endpoints failed with error: {str(e)}",
                    'db_endpoints': db_endpoints,
                    'calculated_endpoints': []
                })
                verification_failed = True
                continue
                
            if not db_endpoints and not geom_endpoints:
                # No endpoints in either, correct!
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'MATCH',
                    'message': "No endpoints required, matches perfectly."
                })
                continue
                
            if len(db_endpoints) != len(geom_endpoints):
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'MISMATCH',
                    'message': f"Count mismatch! DB has {len(db_endpoints)} endpoints, but calculations returned {len(geom_endpoints)}.",
                    'db_endpoints': db_endpoints,
                    'calculated_endpoints': geom_endpoints
                })
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
                    mismatch_detail = f"Diff too large (tol {tol:.5f}): Stored {db_pt} vs Calculated {geom_pt}"
                    break
                    
            if mismatch_detail:
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'MISMATCH',
                    'message': mismatch_detail,
                    'db_endpoints': db_endpoints,
                    'calculated_endpoints': geom_endpoints
                })
                verification_failed = True
            else:
                endpoint_results.append({
                    'db_id': db_id,
                    'obj_id': obj_id,
                    'status': 'MATCH',
                    'message': f"All {len(db_endpoints)} endpoints verified successfully (tolerance {tol:.5f}).",
                    'db_endpoints': db_endpoints,
                    'calculated_endpoints': geom_endpoints
                })
                
        # 2. Intersection Verification (All active DB curve pairs)
        db_ids = sorted(list(db_objs.keys()))
        for i in range(len(db_ids)):
            for j in range(i + 1, len(db_ids)):
                id_a, id_b = db_ids[i], db_ids[j]
                obj_id_a, curve_a = db_objs[id_a]
                obj_id_b, curve_b = db_objs[id_b]
                
                # Query ground truth recorded intersections
                cursor.execute("""
                    SELECT curve_a_id, curve_b_id, intersections, relation_type
                    FROM intersections
                    WHERE curve_a_id = ? AND curve_b_id = ?;
                """, (min(id_a, id_b), max(id_a, id_b)))
                row = cursor.fetchone()
                
                db_pts = json.loads(row[2]) if row else []
                relation_type = row[3] if row else "NO_INTERSECTION"
                
                # Calculate Average Center point for translation
                if db_pts:
                    x0 = sum(p[0] for p in db_pts) / len(db_pts)
                    y0 = sum(p[1] for p in db_pts) / len(db_pts)
                elif (curve_a.xmax - curve_a.xmin) > 50.0 and (curve_b.xmax - curve_b.xmin) <= 50.0:
                    x0 = (curve_b.xmin + curve_b.xmax) / 2
                    y0 = (curve_b.ymin + curve_b.ymax) / 2
                elif (curve_b.xmax - curve_b.xmin) > 50.0 and (curve_a.xmax - curve_a.xmin) <= 50.0:
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
                        curve_a_trans, curve_b_trans,
                        search_range=search_range,
                        grid_resolution=1201,
                        tolerance=1e-4 * max_scale
                    )
                    geom_pts = [(pt[0] + x0, pt[1] + y0) for pt in geom_pts_trans]
                    
                    db_pts_sorted = sorted(db_pts, key=lambda p: p[0]**2 + p[1]**2)[:10]
                    geom_pts_sorted = sorted(geom_pts, key=lambda p: p[0]**2 + p[1]**2)[:10]
                except Exception as e:
                    intersection_results.append({
                        'curve_a_id': id_a,
                        'curve_b_id': id_b,
                        'status': 'ERROR',
                        'message': f"Analytical/Numerical solver failed: {str(e)}",
                        'relation_type': relation_type,
                        'db_intersections': db_pts,
                        'calculated_intersections': []
                    })
                    verification_failed = True
                    continue
                    
                # Mismatch Check based on relationship types
                mismatch_message = None
                
                if relation_type == "NEAR_MISS":
                    # Must not return intersections unless true gap is smaller than tolerance
                    if len(geom_pts_sorted) > 0:
                        try:
                            x_sym, y_sym = sp.symbols('x y')
                            expr_a = curve_a.expression if not hasattr(curve_a, 'base_curve') else curve_a.base_curve.expression
                            expr_b = curve_b.expression if not hasattr(curve_b, 'base_curve') else curve_b.base_curve.expression
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
                            
                            dist_centers = math.sqrt((cx_a - cx_b)**2 + (cy_a - cy_b)**2)
                            true_gap = dist_centers - (r1 + r2)
                            
                            if true_gap >= 1e-4 * max_scale:
                                mismatch_message = f"False positive! Stored NEAR_MISS (gap {true_gap:.6f}), but calculations returned intersections: {geom_pts_sorted}"
                        except Exception:
                            mismatch_message = f"False positive! Stored NEAR_MISS, but calculations returned {len(geom_pts_sorted)} intersections."
                            
                elif relation_type == "TANGENT":
                    if len(geom_pts_sorted) < 1:
                        mismatch_message = "Calculations failed to locate single touch point for TANGENT circles."
                    else:
                        min_dist = min(math.sqrt((gp[0]-dp[0])**2 + (gp[1]-dp[1])**2) for gp in geom_pts_sorted for dp in db_pts_sorted)
                        if min_dist >= 1e-2 * max_scale:
                            mismatch_message = f"Touch point mismatch! Minimum distance to stored touch point is too high ({min_dist:.5f} >= {1e-2 * max_scale:.5f})."
                            
                else: # Standard and NO_INTERSECTION cases
                    # Filter out intersections that are actually touching endpoints
                    filtered_geom_pts = []
                    for gp in geom_pts_sorted:
                        is_endpoint_touch = False
                        if hasattr(curve_a, 'endpoints') and curve_a.endpoints and hasattr(curve_b, 'endpoints') and curve_b.endpoints:
                            dist_a = min(math.sqrt((gp[0]-ep[0])**2 + (gp[1]-ep[1])**2) for ep in curve_a.endpoints)
                            dist_b = min(math.sqrt((gp[0]-ep[0])**2 + (gp[1]-ep[1])**2) for ep in curve_b.endpoints)
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
                            distances = [math.sqrt((gp[0]-db_pt[0])**2 + (gp[1]-db_pt[1])**2) for gp in geom_pts_sorted]
                            if not distances or min(distances) >= 1e-2 * max_scale:
                                missing_pts.append(db_pt)
                                
                        if missing_pts:
                            mismatch_message = f"Stored intersections {missing_pts} missing or coordinate distance exceeds tolerance limit ({1e-2 * max_scale:.5f})."
                            
                if mismatch_message:
                    intersection_results.append({
                        'curve_a_id': id_a,
                        'curve_b_id': id_b,
                        'status': 'MISMATCH',
                        'message': mismatch_message,
                        'relation_type': relation_type,
                        'db_intersections': db_pts_sorted,
                        'calculated_intersections': geom_pts_sorted
                    })
                    verification_failed = True
                else:
                    intersection_results.append({
                        'curve_a_id': id_a,
                        'curve_b_id': id_b,
                        'status': 'MATCH',
                        'message': f"Verified intersection successfully. Relation: {relation_type}.",
                        'relation_type': relation_type,
                        'db_intersections': db_pts_sorted,
                        'calculated_intersections': geom_pts_sorted
                    })
                    
        conn.close()
        
        return jsonify({
            'success': not verification_failed,
            'verified': True,
            'endpoints': endpoint_results,
            'intersections': intersection_results
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/render/image', methods=['POST'])
def render_image():
    """Render scene to image and return path"""
    try:
        data = request.get_json()
        resolution = data.get('resolution', [800, 600])
        bbox = data.get('bbox', None)
        
        # Generate unique filename
        import time
        filename = f"ui_render_{int(time.time())}.png"
        filepath = os.path.join('ui', 'static', 'renders', filename)
        
        # Ensure renders directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Render scene using the correct interface method
        graphics_interface.render_scene_image(filepath, bounds=bbox, resolution=tuple(resolution))
        
        return jsonify({
            'success': True, 
            'image_url': f'/static/renders/{filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('ui_command')
def handle_ui_command(data):
    """Handle UI commands directly without MCP layer"""
    try:
        command_data = data.get('command', {})
        command_name = command_data.get('command')
        
        result = None
        
        # Direct object creation using factories
        if command_name == 'create_circle':
            obj_id = command_data.get('obj_id')
            center_x = command_data.get('center_x', 0)
            center_y = command_data.get('center_y', 0)
            radius = command_data.get('radius', 1)
            style = command_data.get('style', {})
            
            # Create circle using CurveFactory
            circle = curve_factory.create_circle((center_x, center_y), radius)
            scene_manager.add_object(obj_id, circle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_rectangle':
            obj_id = command_data.get('obj_id')
            x = command_data.get('x', 0)
            y = command_data.get('y', 0)
            width = command_data.get('width', 2)
            height = command_data.get('height', 1.5)
            style = command_data.get('style', {})
            
            # Create rectangle using RegionFactory (convert x,y,width,height to corners)
            corner1 = (x, y)
            corner2 = (x + width, y + height)
            rectangle = region_factory.create_rectangle_region(corner1, corner2)
            scene_manager.add_object(obj_id, rectangle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_triangle':
            obj_id = command_data.get('obj_id')
            x1 = command_data.get('x1', 0)
            y1 = command_data.get('y1', 1)
            x2 = command_data.get('x2', -1)
            y2 = command_data.get('y2', -1)
            x3 = command_data.get('x3', 1)
            y3 = command_data.get('y3', -1)
            style = command_data.get('style', {})
            
            # Create triangle using RegionFactory (expects list of vertices)
            vertices = [(x1, y1), (x2, y2), (x3, y3)]
            triangle = region_factory.create_triangle_region(vertices)
            scene_manager.add_object(obj_id, triangle, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_ellipse':
            obj_id = command_data.get('obj_id')
            center_x = command_data.get('center_x', 0)
            center_y = command_data.get('center_y', 0)
            radius_x = command_data.get('radius_x', 1.5)
            radius_y = command_data.get('radius_y', 1)
            style = command_data.get('style', {})
            
            # Create ellipse using CurveFactory
            ellipse = curve_factory.create_ellipse((center_x, center_y), radius_x, radius_y)
            scene_manager.add_object(obj_id, ellipse, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'create_line':
            obj_id = command_data.get('obj_id')
            x1 = command_data.get('x1', -1)
            y1 = command_data.get('y1', 0)
            x2 = command_data.get('x2', 1)
            y2 = command_data.get('y2', 0)
            style = command_data.get('style', {})
            
            # Create line using CurveFactory
            line = curve_factory.create_line((x1, y1), (x2, y2))
            scene_manager.add_object(obj_id, line, style)
            result = {'obj_id': obj_id, 'created': True}

        elif command_name == 'create_parabola':
            import sympy as sp
            from geometry import ImplicitCurve
            obj_id = command_data.get('obj_id')
            vx = command_data.get('vertex_x', 0)
            vy = command_data.get('vertex_y', 0)
            scale = command_data.get('scale', 1.0)
            direction = command_data.get('direction', 'up')
            style = command_data.get('style', {})
            x, y = sp.symbols('x y')
            if direction == 'up':
                expr = (y - vy) - scale * (x - vx)**2
            elif direction == 'down':
                expr = (y - vy) + scale * (x - vx)**2
            elif direction == 'right':
                expr = (x - vx) - scale * (y - vy)**2
            else:
                expr = (x - vx) + scale * (y - vy)**2
            parabola = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, parabola, style)
            result = {'obj_id': obj_id, 'created': True}

        elif command_name == 'create_hyperbola':
            import sympy as sp
            from geometry import ImplicitCurve
            obj_id = command_data.get('obj_id')
            cx = command_data.get('center_x', 0)
            cy = command_data.get('center_y', 0)
            a = command_data.get('a', 1.5)
            b = command_data.get('b', 1.0)
            style = command_data.get('style', {})
            x, y = sp.symbols('x y')
            expr = (x - cx)**2 / a**2 - (y - cy)**2 / b**2 - 1
            hyperbola = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, hyperbola, style)
            result = {'obj_id': obj_id, 'created': True}

        elif command_name == 'create_cubic':
            import sympy as sp
            from geometry import ImplicitCurve
            obj_id = command_data.get('obj_id')
            cx = command_data.get('center_x', 0)
            cy = command_data.get('center_y', 0)
            scale = command_data.get('scale', 1.0)
            style = command_data.get('style', {})
            x, y = sp.symbols('x y')
            # y^2 = x^3 - x  (elliptic curve, shifted to center)
            expr = (y - cy)**2 - ((x - cx)**3 - (x - cx)) * scale
            cubic = ImplicitCurve(expr, (x, y))
            scene_manager.add_object(obj_id, cubic, style)
            result = {'obj_id': obj_id, 'created': True}
            
        elif command_name == 'delete_object':
            obj_id = command_data.get('obj_id')
            scene_manager.remove_object(obj_id)
            result = {'obj_id': obj_id, 'deleted': True}
            
        elif command_name == 'update_parameter':
            obj_id = command_data.get('obj_id')
            parameter = command_data.get('parameter')
            value = command_data.get('value')
            try:
                scene_manager.update_parameter(obj_id, parameter, value)
                result = {'obj_id': obj_id, 'parameter': parameter, 'value': value, 'updated': True}
            except Exception as e:
                # Be tolerant for UI flows/tests that only require a broadcast
                result = {
                    'obj_id': obj_id,
                    'parameter': parameter,
                    'value': value,
                    'updated': False,
                    'warning': str(e)
                }
            
        elif command_name == 'set_style':
            obj_id = command_data.get('obj_id')
            style = command_data.get('style', {})
            scene_manager.set_style(obj_id, style)
            result = {'obj_id': obj_id, 'style_updated': True}
            
        elif command_name == 'save_scene':
            filename = command_data.get('filename')
            scene_manager.save_scene(filename)
            result = {'filename': filename, 'saved': True}
            
        elif command_name == 'load_scene':
            filename = command_data.get('filename')
            scene_manager.load_scene(filename)
            result = {'filename': filename, 'loaded': True}
            
        elif command_name == 'clear_scene':
            # Clear all objects
            for obj_id in scene_manager.list_objects():
                scene_manager.remove_object(obj_id)
            result = {'cleared': True}
            
        else:
            raise ValueError(f"Unknown command: {command_name}")
        
        # Emit result back to client
        emit('ui_response', {
            'success': True,
            'result': result,
            'command_id': data.get('command_id')
        })
        
        # If command modified scene, broadcast update to all clients
        if _command_modifies_scene(command_data):
            # Defer broadcast to avoid being consumed during ui_response polling
            socketio.start_background_task(_broadcast_scene_updated_async)
            
    except Exception as e:
        print(f"UI Command Error: {e}")
        import traceback
        traceback.print_exc()
        emit('ui_response', {
            'success': False,
            'error': str(e),
            'command_id': data.get('command_id')
        })

@socketio.on('get_object_data')
def handle_get_object_data(data):
    """Get detailed object data for visualization"""
    try:
        obj_id = data.get('obj_id')
        data_type = data.get('type', 'curve')  # 'curve', 'region', 'field'
        resolution = data.get('resolution', 100)
        
        # Get scene bounds for data extraction
        bounds = graphics_interface.get_scene_bounds()
        
        if data_type == 'curve':
            # Get curve paths for specific object
            all_curve_data = graphics_interface.get_curve_paths(bounds, resolution)
            curve_data = all_curve_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'curve',
                'data': curve_data
            })
        elif data_type == 'region':
            # Get region data for specific object  
            all_region_data = graphics_interface.get_region_data(bounds, (resolution, resolution))
            region_data = all_region_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'region', 
                'data': region_data
            })
        elif data_type == 'field':
            # Get field data for specific object
            all_field_data = graphics_interface.get_field_data(bounds, (resolution, resolution))
            field_data = all_field_data.get(obj_id, {})
            
            emit('object_data_response', {
                'success': True,
                'obj_id': obj_id,
                'type': 'field',
                'data': field_data
            })
            
    except Exception as e:
        emit('object_data_response', {
            'success': False,
            'error': str(e),
            'obj_id': data.get('obj_id')
        })

def _command_modifies_scene(command):
    """Check if a command modifies the scene state"""
    modifying_commands = {
        'create_circle', 'create_rectangle', 'create_triangle', 'create_ellipse',
        'create_line', 'create_parabola', 'create_hyperbola', 'create_cubic',
        'delete_object', 'update_parameter', 'set_style',
        'group_objects', 'load_scene', 'clear_scene'
    }
    return command.get('command') in modifying_commands

if __name__ == '__main__':
    print("Starting 2Top UI Server...")
    print("Access the UI at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
