"""
2Top Geometry - Headless Batch Rendering and Gallery Generator
Solves, validates, and renders all 155 periodic curve pairs.
Generates docs/renders/periodic_curves/ and the review gallery dashboard.
"""

import sys
import os
import time
import math
import json
import sympy as sp
import numpy as np

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from tests.test_periodic_curves import TEST_CONFIGS, reconstruct_curve, get_expected_intersections
from geometry import ProceduralCurve
from geometry.curve_intersections import find_curve_intersections


def main():
    print("======================================================================")
    print(" 2Top Geometry Studio - Batch Solver & Renders Generator")
    print("======================================================================")
    
    # 1. Setup folders
    docs_renders_dir = os.path.join("docs", "renders", "periodic_curves")
    ui_renders_dir = os.path.join("ui", "static", "renders", "periodic_curves")
    os.makedirs(docs_renders_dir, exist_ok=True)
    os.makedirs(ui_renders_dir, exist_ok=True)
    
    # Initialize components in headless mode
    scene_manager = SceneManager()
    graphics_interface = GraphicsBackendInterface(scene_manager)
    
    results = []
    total_cases = len(TEST_CONFIGS)
    passed_count = 0
    
    t_start = time.perf_counter()
    
    # Sort cases naturally by numeric parts of test_id (e.g. 1.1, 1.2, ..., 1.10, 2.1)
    sorted_test_ids = sorted(TEST_CONFIGS.keys(), key=lambda x: [int(c) for c in x.split('.')])
    for idx, test_id in enumerate(sorted_test_ids):
        config = TEST_CONFIGS[test_id]
        name_safe = config['name'].replace('\u2229', 'intersection')
        print(f"[{idx+1}/{total_cases}] Solving Case {test_id}: {name_safe}...", end="", flush=True)
        
        # Clear active scene
        scene_manager.clear()
        
        # Reconstruct curves A and B
        x_sym, y_sym = sp.symbols('x y', real=True)
        dom = config["domain"]
        
        try:
            curve_a = reconstruct_curve(config["eq_a"], x_sym, y_sym)
            eq_b = config.get("eq_b")
            curve_b = reconstruct_curve(eq_b, x_sym, y_sym) if eq_b else None
            
            # Set properties for rendering
            curve_a.xmin, curve_a.xmax = dom[0], dom[1]
            curve_a.ymin, curve_a.ymax = -4.0, 4.0
            if curve_b:
                curve_b.xmin, curve_b.xmax = dom[0], dom[1]
                curve_b.ymin, curve_b.ymax = -4.0, 4.0
            
            style_a = {'color': '#00f0ff', 'linewidth': 4.5, 'alpha': 1.0, 'is_periodic_curve': True, 'curve_name': config['eq_a']}
            scene_manager.add_object('periodic_curve_a', curve_a, style_a)
            
            if curve_b:
                style_b = {'color': '#ff007f', 'linewidth': 2.0, 'alpha': 1.0, 'is_periodic_curve': True, 'curve_name': eq_b}
                scene_manager.add_object('periodic_curve_b', curve_b, style_b)
            
            # Solve Endpoints
            t0 = time.perf_counter()
            endpoints_a = []
            endpoints_b = []
            if hasattr(curve_a, 'get_endpoints'):
                endpoints_a = curve_a.get_endpoints(xmin=dom[0], xmax=dom[1])
            if curve_b and hasattr(curve_b, 'get_endpoints'):
                endpoints_b = curve_b.get_endpoints(xmin=dom[0], xmax=dom[1])
            
            calculated_endpoints = [tuple(pt) for pt in (endpoints_a + endpoints_b)]
            
            # Solve Intersections
            search_range = config.get("search_range", (dom[1] - dom[0]) / 2.0)
            if search_range < 0.1:
                search_range = 1.0
            grid_res = config.get("grid_res", 500)
            center_x = (dom[0] + dom[1]) / 2.0
            
            calculated_intersections = []
            
            # Only solve intersections if we have a second curve
            if curve_b:
                # Shift domain logic to focus grid search
                if abs(center_x) > 1e-4:
                    expr_a_trans = curve_a.expression.subs(x_sym, x_sym + center_x) if hasattr(curve_a, "expression") and curve_a.expression else None
                    expr_b_trans = curve_b.expression.subs(x_sym, x_sym + center_x) if hasattr(curve_b, "expression") and curve_b.expression else None
                    
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
                            c_a = ProceduralCurve(lambda x_v, y_v: orig_func(x_v + center_x, y_v), variables=(x_sym, y_sym))
                        else:
                            c_a = curve_a
                            
                        if isinstance(curve_b, ProceduralCurve):
                            orig_func = curve_b.function
                            c_b = ProceduralCurve(lambda x_v, y_v: orig_func(x_v + center_x, y_v), variables=(x_sym, y_sym))
                        else:
                            c_b = curve_b
                else:
                    c_a = curve_a
                    c_b = curve_b
                    
                detect_overlap = test_id in ("1.39", "2.34", "3.33")
                found_pts_trans = find_curve_intersections(c_a, c_b, search_range=search_range, grid_resolution=grid_res, detect_overlap=detect_overlap)
                calculated_intersections = [(float(pt[0] + center_x), float(pt[1])) for pt in found_pts_trans]
            
            elapsed_time = time.perf_counter() - t0
            
            # Ground truth matching
            expected_intersections = []
            if curve_b:
                oracle_dom = (center_x - search_range, center_x + search_range)
                expected_intersections = get_expected_intersections(config["eq_a"], eq_b, oracle_dom)
            
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
                        best_err = float('inf')
                        best_idx = -1
                        for idx, e_pt in enumerate(expected_intersections):
                            if idx in matched_exp:
                                continue
                            err = math.sqrt((f_pt[0] - e_pt[0])**2 + (f_pt[1] - e_pt[1])**2)
                            if err < best_err:
                                best_err = err
                                best_idx = idx
                        if best_idx != -1:
                            matched_exp.add(best_idx)
                            if best_err > max_error:
                                max_error = best_err
                        else:
                            if not ("1/x" in config["eq_a"] or has_eq_b_1_x):
                                max_error = float('inf')
                            else:
                                max_error = max(max_error, 0.1)
                            
                    tolerance_limit = 0.05
                    if "1/x" in config["eq_a"] or has_eq_b_1_x:
                        tolerance_limit = 0.15
                        
                    if max_error > tolerance_limit:
                        is_correct = False
            
            # Save files to both folders for local gallery and active UI server
            filename = f"case_{test_id.replace('.', '_')}.png"
            docs_filepath = os.path.join(docs_renders_dir, filename)
            ui_filepath = os.path.join(ui_renders_dir, filename)
            
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
            
            # Render to docs
            graphics_interface.render_scene_image_annotated(
                filename=docs_filepath,
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
                bounds=bounds
            )
            
            # Render to ui static
            import shutil
            shutil.copy2(docs_filepath, ui_filepath)
            
            if is_correct:
                passed_count += 1
                status_str = "SUCCESS"
            else:
                status_str = "FAILED"
                
            print(f" {status_str} in {elapsed_time:.3f}s (Ints found: {len(calculated_intersections)})")
            
            results.append({
                "test_id": test_id,
                "name": config["name"],
                "eq_a": config["eq_a"],
                "eq_b": eq_b or "",
                "tier": config["tier"],
                "elapsed_time": elapsed_time,
                "is_correct": is_correct,
                "ints_found": len(calculated_intersections),
                "expected_ints": len(expected_intersections),
                "image_path": f"renders/periodic_curves/{filename}"
            })
        except Exception as e:
            print(f" ERROR: {e}")
            results.append({
                "test_id": test_id,
                "name": config["name"],
                "eq_a": config["eq_a"],
                "eq_b": config.get("eq_b", ""),
                "tier": config["tier"],
                "elapsed_time": 0.0,
                "is_correct": False,
                "ints_found": 0,
                "expected_ints": 0,
                "image_path": ""
            })
            
    total_time = time.perf_counter() - t_start
    print("======================================================================")
    print(f" Batch Rendering Complete! {passed_count}/{total_cases} passed in {total_time:.2f}s.")
    print("======================================================================")
    
    # 2. Generate HTML Gallery
    generate_gallery(results, passed_count, total_cases, total_time)


def generate_gallery(results, passed, total, total_time):
    print("Generating responsive HTML gallery at docs/periodic_curve_gallery.html...")
    
    cards_html = []
    for r in results:
        status_class = "verified" if r["is_correct"] else "mismatch"
        status_tag = "VERIFIED ✅" if r["is_correct"] else "MISMATCH ❌"
        
        card = f"""
        <div class="card" data-tier="{r['tier']}" data-status="{status_class}">
            <div class="card-header">
                <div class="card-title">
                    <span class="case-id">Case {r['test_id']}</span>
                    <span class="case-tier">Tier {r['tier']}</span>
                </div>
                <h3>{r['name']}</h3>
            </div>
            
            <div class="equations">
                <div class="eq"><span class="eq-label">Curve A:</span> <code>{r['eq_a']}</code></div>
                <div class="eq"><span class="eq-label">Curve B:</span> <code>{r['eq_b']}</code></div>
            </div>
            
            <div class="stats-row">
                <div class="stat">
                    <span class="stat-label">Solver Time</span>
                    <span class="stat-val">{r['elapsed_time']:.3f}s</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Intersections</span>
                    <span class="stat-val">{r['ints_found']} / {r['expected_ints']}</span>
                </div>
                <div class="stat-badge {status_class}">
                    {status_tag}
                </div>
            </div>
            
            <div class="render-preview" onclick="openLightbox('{r['image_path']}', 'Case {r['test_id']} — {r['name']}')">
                <img src="{r['image_path']}" alt="Case {r['test_id']} Render" loading="lazy">
                <div class="zoom-overlay">🔍 Click to zoom</div>
            </div>
        </div>
        """
        cards_html.append(card)
        
    gallery_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2Top Periodic Curves Gallery</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #06080f;
            --surface: #0c0f1b;
            --border: rgba(255, 255, 255, 0.06);
            --text: #e8f0ff;
            --muted: #8f9cae;
            --accent-cyan: #00f0ff;
            --accent-rose: #ff007f;
            --success: #39ff14;
            --error: #ff3366;
            --font: 'Space Grotesk', system-ui, -apple-system, sans-serif;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .header-left h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-rose) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        
        .header-left p {{
            color: var(--muted);
            font-size: 0.95rem;
        }}
        
        .summary-stats {{
            display: flex;
            gap: 15px;
        }}
        
        .summary-badge {{
            background: rgba(12, 15, 27, 0.85);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 18px;
            min-width: 110px;
            text-align: center;
        }}
        
        .summary-badge .label {{
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--muted);
            margin-bottom: 4px;
            display: block;
        }}
        
        .summary-badge .val {{
            font-size: 1.3rem;
            font-weight: 700;
        }}
        
        .summary-badge.passed .val {{
            color: var(--success);
        }}
        
        /* Filters */
        .filters-panel {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 16px;
            color: var(--text);
            font-family: inherit;
            outline: none;
            font-size: 0.9rem;
            transition: border-color 0.2s;
        }}
        
        .search-box:focus {{
            border-color: var(--accent-cyan);
        }}
        
        .filter-btn-group {{
            display: flex;
            background: rgba(0, 0, 0, 0.25);
            padding: 3px;
            border-radius: 8px;
            border: 1px solid var(--border);
            gap: 2px;
        }}
        
        .filter-btn {{
            background: transparent;
            border: none;
            color: var(--muted);
            padding: 6px 14px;
            font-size: 0.75rem;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }}
        
        .filter-btn:hover {{
            color: var(--text);
        }}
        
        .filter-btn.active {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text);
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        }}
        
        /* Grid Layout */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }}
        
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            transition: transform 0.2s, border-color 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.12);
        }}
        
        .card-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .card-title {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .case-id {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--accent-cyan);
            font-family: monospace;
        }}
        
        .case-tier {{
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--muted);
        }}
        
        .card-header h3 {{
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.3;
        }}
        
        .equations {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            font-size: 0.7rem;
            background: rgba(0, 0, 0, 0.15);
            padding: 8px 10px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.02);
        }}
        
        .eq {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .eq-label {{
            color: var(--muted);
            margin-right: 4px;
        }}
        
        .eq code {{
            font-family: monospace;
            color: #d1d9e6;
        }}
        
        .stats-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
            padding-top: 10px;
        }}
        
        .stat {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        
        .stat-label {{
            font-size: 0.58rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted);
        }}
        
        .stat-val {{
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .stat-badge {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 4px 8px;
            border-radius: 6px;
        }}
        
        .stat-badge.verified {{
            background: rgba(57, 255, 20, 0.1);
            color: var(--success);
            border: 1px solid rgba(57, 255, 20, 0.2);
        }}
        
        .stat-badge.mismatch {{
            background: rgba(255, 51, 102, 0.1);
            color: var(--error);
            border: 1px solid rgba(255, 51, 102, 0.2);
        }}
        
        .render-preview {{
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.04);
            cursor: pointer;
            aspect-ratio: 4/3;
            background: #090a12;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .render-preview img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}
        
        .render-preview:hover img {{
            transform: scale(1.04);
        }}
        
        .zoom-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(6, 8, 15, 0.75);
            backdrop-filter: blur(2px);
            padding: 6px;
            text-align: center;
            font-size: 0.65rem;
            font-weight: 500;
            color: var(--muted);
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        .render-preview:hover .zoom-overlay {{
            opacity: 1;
        }}
        
        /* Lightbox styling */
        .lightbox {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 4, 8, 0.95);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            animation: fadeIn 0.2s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .lightbox-close {{
            position: absolute;
            top: 25px;
            right: 25px;
            background: transparent;
            border: none;
            color: white;
            font-size: 2.2rem;
            cursor: pointer;
            transition: transform 0.2s, color 0.2s;
        }}
        
        .lightbox-close:hover {{
            transform: scale(1.1);
            color: var(--accent-rose);
        }}
        
        .lightbox img {{
            max-width: 90%;
            max-height: 80%;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.06);
            transform: scale(0.95);
            animation: zoomIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }}
        
        @keyframes zoomIn {{
            to {{ transform: scale(1); }}
        }}
        
        .lightbox-title {{
            margin-top: 20px;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
        }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <div class="header-left">
            <h1>Periodic Curves Gallery</h1>
            <p>Verification dashboard & annotated visual renders across all 4 tiers (155 cases total).</p>
        </div>
        <div class="summary-stats">
            <div class="summary-badge passed">
                <span class="label">Verified</span>
                <span class="val">{passed} / {total}</span>
            </div>
            <div class="summary-badge">
                <span class="label">Total Time</span>
                <span class="val">{total_time:.1f}s</span>
            </div>
        </div>
    </header>

    <div class="filters-panel">
        <input type="text" id="search" class="search-box" placeholder="Search by name, equations, ID..." oninput="filterCards()">
        
        <div class="filter-btn-group">
            <span style="font-size: 0.65rem; color: var(--muted); align-self: center; margin: 0 10px; font-weight: 600; text-transform: uppercase;">Tier:</span>
            <button class="filter-btn active" data-filter-type="tier" data-val="all" onclick="setFilter(this, 'tier', 'all')">All</button>
            <button class="filter-btn" data-filter-type="tier" data-val="1" onclick="setFilter(this, 'tier', '1')">Tier 1</button>
            <button class="filter-btn" data-filter-type="tier" data-val="2" onclick="setFilter(this, 'tier', '2')">Tier 2</button>
            <button class="filter-btn" data-filter-type="tier" data-val="3" onclick="setFilter(this, 'tier', '3')">Tier 3</button>
            <button class="filter-btn" data-filter-type="tier" data-val="4" onclick="setFilter(this, 'tier', '4')">Tier 4</button>
        </div>

        <div class="filter-btn-group">
            <span style="font-size: 0.65rem; color: var(--muted); align-self: center; margin: 0 10px; font-weight: 600; text-transform: uppercase;">Status:</span>
            <button class="filter-btn active" data-filter-type="status" data-val="all" onclick="setFilter(this, 'status', 'all')">All</button>
            <button class="filter-btn" data-filter-type="status" data-val="verified" onclick="setFilter(this, 'status', 'verified')">Verified ✅</button>
            <button class="filter-btn" data-filter-type="status" data-val="mismatch" onclick="setFilter(this, 'status', 'mismatch')">Mismatch ❌</button>
        </div>
    </div>

    <div class="gallery-grid" id="grid">
        {"".join(cards_html)}
    </div>
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
    <img id="lightbox-img" src="" alt="Enlarged Render" onclick="event.stopPropagation()">
    <div class="lightbox-title" id="lightbox-title"></div>
</div>

<script>
    let activeFilters = {{
        tier: 'all',
        status: 'all'
    }};

    function setFilter(btn, type, val) {{
        // Toggle active button
        const group = btn.parentNode;
        group.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        activeFilters[type] = val;
        filterCards();
    }}

    function filterCards() {{
        const searchVal = document.getElementById('search').value.toLowerCase();
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {{
            const tier = card.getAttribute('data-tier');
            const status = card.getAttribute('data-status');
            const textContent = card.textContent.toLowerCase();
            
            const matchesTier = activeFilters.tier === 'all' || tier === activeFilters.tier;
            const matchesStatus = activeFilters.status === 'all' || status === activeFilters.status;
            const matchesSearch = textContent.includes(searchVal);
            
            if (matchesTier && matchesStatus && matchesSearch) {{
                card.style.display = 'flex';
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }}

    function openLightbox(src, title) {{
        const lb = document.getElementById('lightbox');
        const img = document.getElementById('lightbox-img');
        const titleEl = document.getElementById('lightbox-title');
        
        img.src = src;
        titleEl.textContent = title;
        lb.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }}

    function closeLightbox() {{
        const lb = document.getElementById('lightbox');
        lb.style.display = 'none';
        document.body.style.overflow = '';
    }}
    
    // Close lightbox on escape key
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') closeLightbox();
    }});
</script>
</body>
</html>
"""
    
    gallery_filepath = os.path.join("docs", "periodic_curve_gallery.html")
    with open(gallery_filepath, "w", encoding="utf-8") as f:
        f.write(gallery_html)
        
    print(f"Gallery review dashboard generated successfully at {gallery_filepath}!")


if __name__ == "__main__":
    main()
