"""Quick test for arcsin intersection fix."""

import sqlite3
import json
import sys
import time
import warnings

sys.path.append(".")
from tools.compare_solutions_suite import (
    reconstruct_db_curve,
    translate_curve,
    match_points,
)
from geometry.curve_intersections import find_curve_intersections

conn = sqlite3.connect("curves.db")
cursor = conn.cursor()

test_cases = [
    (2202, 2203, "arcsin x line (RowID 439)"),
    (2202, 2204, "arcsin x circle (RowID 440)"),
    (2382, 2383, "arcsin x line (RowID 819)"),
    (2382, 2387, "arcsin x circle (RowID 823)"),
    (2442, 2443, "arcsin x line (RowID 951)"),
]

passed_all = 0
for c_a_id, c_b_id, desc in test_cases:
    cursor.execute(
        "SELECT id, group_id, equation, type, scale, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, endpoints, local_tolerance FROM curves WHERE id IN (?, ?)",
        (c_a_id, c_b_id),
    )
    rows = {r[0]: r for r in cursor.fetchall()}
    c_a = reconstruct_db_curve(rows[c_a_id])
    c_b = reconstruct_db_curve(rows[c_b_id])
    cursor.execute(
        "SELECT intersections FROM intersections WHERE (curve_a_id=? AND curve_b_id=?) OR (curve_a_id=? AND curve_b_id=?)",
        (c_a_id, c_b_id, c_b_id, c_a_id),
    )
    result = cursor.fetchone()
    expected_pts = json.loads(result[0]) if result else []
    if not expected_pts:
        x0 = (c_a.xmin + c_a.xmax) / 2
        y0 = (c_a.ymin + c_a.ymax) / 2
    else:
        x0 = sum(p[0] for p in expected_pts) / len(expected_pts)
        y0 = sum(p[1] for p in expected_pts) / len(expected_pts)
    ca_t = translate_curve(c_a, x0, y0)
    cb_t = translate_curve(c_b, x0, y0)
    ox_min = max(c_a.xmin, c_b.xmin)
    ox_max = min(c_a.xmax, c_b.xmax)
    oy_min = max(c_a.ymin, c_b.ymin)
    oy_max = min(c_a.ymax, c_b.ymax)
    max_scale = max(float(rows[c_a_id][4]), float(rows[c_b_id][4]))
    if ox_min < ox_max and oy_min < oy_max:
        bounded_range = max((ox_max - ox_min) / 2 * 1.2, (oy_max - oy_min) / 2 * 1.2)
        search_range = min(15.0 * max_scale, bounded_range)
    else:
        search_range = max(2.0 * max_scale, 0.5)
    search_range = max(search_range, 0.5)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t0 = time.perf_counter()
        pts = find_curve_intersections(
            ca_t,
            cb_t,
            search_range=search_range,
            grid_resolution=500,
            tolerance=1e-4 * max_scale,
        )
        elapsed = time.perf_counter() - t0
    found = [(p[0] + x0, p[1] + y0) for p in pts]
    passed = match_points(found, expected_pts)
    status = "PASS" if passed else "FAIL"
    if passed:
        passed_all += 1
    print(
        f"{status} {desc}: expected={len(expected_pts)}, found={len(found)}, t={elapsed:.3f}s"
    )

conn.close()
print(f"\nResult: {passed_all}/{len(test_cases)} passed")
