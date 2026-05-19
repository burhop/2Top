import os
import sys
import json
import sqlite3
import math
import random
import numpy as np
from scipy.optimize import fsolve
import multiprocessing as mp

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "curves.db")
TOTAL_GROUPS = int(os.environ.get("TOTAL_GROUPS", 100000))  # Default to 100,000 groups, but configurable
CURVES_PER_GROUP = 10
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 1000))


def init_db(db_path):
    """Initialize the SQLite database and create schemas."""
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable WAL mode for high write performance
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    # Table to store individual curves
    cursor.execute("""
    CREATE TABLE curves (
        id INTEGER PRIMARY KEY,
        group_id INTEGER,
        equation TEXT NOT NULL,
        type TEXT NOT NULL,
        scale REAL NOT NULL,
        bounds_xmin REAL,
        bounds_xmax REAL,
        bounds_ymin REAL,
        bounds_ymax REAL,
        endpoints TEXT, -- JSON list of [x, y]
        local_tolerance REAL NOT NULL
    );
    """)
    
    # Table to store sparse intersections between curves
    cursor.execute("""
    CREATE TABLE intersections (
        curve_a_id INTEGER,
        curve_b_id INTEGER,
        intersections TEXT, -- JSON list of [x, y] (up to 10 closest to origin)
        relation_type TEXT, -- 'TRANSVERSAL', 'TANGENT', 'COINCIDENT', 'NEAR_MISS'
        PRIMARY KEY (curve_a_id, curve_b_id),
        FOREIGN KEY(curve_a_id) REFERENCES curves(id),
        FOREIGN KEY(curve_b_id) REFERENCES curves(id)
    );
    """)
    
    # Add indexes for fast querying
    cursor.execute("CREATE INDEX idx_curves_group ON curves(group_id);")
    cursor.execute("CREATE INDEX idx_curves_type ON curves(type);")
    
    conn.commit()
    conn.close()

# ==================== Curve Generator classes ====================

def solve_quadratic(a, b, c):
    """Helper to solve quadratic equations analytically."""
    discriminant = b**2 - 4*a*c
    if discriminant < -1e-9:
        return []
    if abs(discriminant) < 1e-9:
        return [-b / (2*a)]
    sqrt_d = math.sqrt(discriminant)
    return [(-b - sqrt_d)/(2*a), (-b + sqrt_d)/(2*a)]

def intersect_circle_line_analytical(cx, cy, r, lx1, ly1, lx2, ly2):
    """Analytical intersection between circle and line segment."""
    dx = lx2 - lx1
    dy = ly2 - ly1
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        # Line is a point, check if on circle
        dist = math.sqrt((lx1 - cx)**2 + (ly1 - cy)**2)
        return [(lx1, ly1)] if abs(dist - r) < 1e-6 else []
    
    # Represent line as x = lx1 + t*dx, y = ly1 + t*dy
    # Substitute into circle equation: (lx1 + t*dx - cx)^2 + (ly1 + t*dy - cy)^2 = r^2
    # At^2 + Bt + C = 0
    a_coef = dx**2 + dy**2
    b_coef = 2 * (dx * (lx1 - cx) + dy * (ly1 - cy))
    c_coef = (lx1 - cx)**2 + (ly1 - cy)**2 - r**2
    
    t_vals = solve_quadratic(a_coef, b_coef, c_coef)
    points = []
    for t in t_vals:
        x = lx1 + t * dx
        y = ly1 + t * dy
        points.append((x, y))
    return points

def intersect_circle_circle_analytical(cx1, cy1, r1, cx2, cy2, r2):
    """Analytical intersection of two circles."""
    dx = cx2 - cx1
    dy = cy2 - cy1
    d = math.sqrt(dx**2 + dy**2)
    
    if d > r1 + r2 + 1e-7 or d < abs(r1 - r2) - 1e-7:
        return []  # No intersection
    
    if d < 1e-9:
        return []  # Concentric, no unique intersection (or infinite)
        
    # Standard circle-circle intersection formulas
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = math.sqrt(max(0.0, r1**2 - a**2))
    
    x2_temp = cx1 + a * dx / d
    y2_temp = cy1 + a * dy / d
    
    if h < 1e-7:
        # Tangent
        return [(x2_temp, y2_temp)]
        
    rx = -dy * (h / d)
    ry = dx * (h / d)
    
    return [
        (x2_temp + rx, y2_temp + ry),
        (x2_temp - rx, y2_temp - ry)
    ]

# ==================== Group Generation Function ====================

def generate_spatial_group(args):
    """
    Generate a co-located spatial group of 10 curves.
    Includes rich variety, scales, edge cases, endpoints, and exact intersections.
    """
    group_id, seed = args
    random.seed(seed)
    np.random.seed(seed)
    
    # Establish a local hotspot (center of group)
    gx = random.uniform(-10.0, 10.0)
    gy = random.uniform(-10.0, 10.0)
    scale = random.choice([0.1, 0.5, 1.0, 2.0, 5.0])
    tol = 1e-8 * scale
    
    curves = []
    
    # Determine Group Type for targeting edge cases
    # 0: Standard Mixed curves
    # 1: Semicircles & Radical stress-test (touching & near-touching endpoints)
    # 2: Tangent circles and line-curve touches
    # 3: Near-miss curves (non-intersecting close approaches)
    # 4: Transcendentals & Periodic curves
    # 5: High-degree Algebraic (Weierstrass/Folium/Lemniscate)
    group_type = group_id % 6
    
    if group_type == 0:
        # Standard Mixed curves (Conics, lines)
        for i in range(CURVES_PER_GROUP):
            ctype = random.choice(["line", "circle", "ellipse", "parabola"])
            if ctype == "line":
                angle = random.uniform(0, 2*math.pi)
                c = random.uniform(-2, 2) * scale
                a = math.cos(angle)
                b = math.sin(angle)
                offset = a * gx + b * gy + c
                equation = f"{a:.6f}*x + {b:.6f}*y - {offset:.6f}"
                curves.append({
                    "type": "line", "equation": equation, "endpoints": [], "scale": scale,
                    "eval": lambda x, y, a=a, b=b, offset=offset: a*x + b*y - offset,
                    "deriv": lambda x, y, a=a, b=b: (a, b)
                })
            elif ctype == "circle":
                cx = gx + random.uniform(-1, 1) * scale
                cy = gy + random.uniform(-1, 1) * scale
                r = random.uniform(0.5, 2.0) * scale
                equation = f"(x - {cx:.6f})**2 + (y - {cy:.6f})**2 - {r**2:.6f}"
                curves.append({
                    "type": "circle", "equation": equation, "endpoints": [], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, r=r: (x - cx)**2 + (y - cy)**2 - r**2,
                    "deriv": lambda x, y, cx=cx, cy=cy: (2*(x - cx), 2*(y - cy))
                })
            elif ctype == "ellipse":
                cx = gx + random.uniform(-0.5, 0.5) * scale
                cy = gy + random.uniform(-0.5, 0.5) * scale
                a_param = random.uniform(0.5, 2.0) * scale
                b_param = random.uniform(0.5, 2.0) * scale
                equation = f"(x - {cx:.6f})**2/{a_param**2:.6f} + (y - {cy:.6f})**2/{b_param**2:.6f} - 1"
                curves.append({
                    "type": "ellipse", "equation": equation, "endpoints": [], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, a=a_param, b=b_param: (x - cx)**2/a**2 + (y - cy)**2/b**2 - 1,
                    "deriv": lambda x, y, cx=cx, cy=cy, a=a_param, b=b_param: (2*(x - cx)/a**2, 2*(y - cy)/b**2)
                })
            else:  # Parabola
                cx = gx + random.uniform(-0.5, 0.5) * scale
                cy = gy + random.uniform(-0.5, 0.5) * scale
                a_param = random.uniform(-1.5, 1.5)
                if abs(a_param) < 0.1: a_param = 0.5
                equation = f"y - {cy:.6f} - {a_param:.6f}*(x - {cx:.6f})**2"
                curves.append({
                    "type": "parabola", "equation": equation, "endpoints": [], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, a=a_param: y - cy - a*(x - cx)**2,
                    "deriv": lambda x, y, cx=cx, cy=cy, a=a_param: (-2*a*(x - cx), 1.0)
                })
                
    elif group_type == 1:
        # Radicals & Semicircles (Endpoint stress-test)
        # We will generate touching and near-touching endpoints
        for i in range(CURVES_PER_GROUP):
            edge_type = i % 4
            if edge_type == 0:
                # Semicircle exactly touching at gx, gy
                # Semicircle 1: upper, endpoint at (gx, gy)
                r = random.uniform(0.5, 2.0) * scale
                cx = gx + r
                cy = gy
                equation = f"y - {cy:.6f} - sqrt({r**2:.6f} - (x - {cx:.6f})**2)"
                curves.append({
                    "type": "semicircle", "equation": equation,
                    "endpoints": [[gx, gy], [gx + 2*r, gy]], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, r=r: y - cy - math.sqrt(max(0, r**2 - (x - cx)**2)) if abs(x-cx) <= r else 1e3,
                    "deriv": lambda x, y, cx=cx, cy=cy, r=r: ( (x-cx)/math.sqrt(max(1e-9, r**2 - (x-cx)**2)), 1.0 )
                })
            elif edge_type == 1:
                # Semicircle 2: upper, starting exactly from (gx, gy) but going left
                r = random.uniform(0.5, 2.0) * scale
                cx = gx - r
                cy = gy
                equation = f"y - {cy:.6f} - sqrt({r**2:.6f} - (x - {cx:.6f})**2)"
                curves.append({
                    "type": "semicircle", "equation": equation,
                    "endpoints": [[gx - 2*r, gy], [gx, gy]], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, r=r: y - cy - math.sqrt(max(0, r**2 - (x - cx)**2)) if abs(x-cx) <= r else 1e3,
                    "deriv": lambda x, y, cx=cx, cy=cy, r=r: ( (x-cx)/math.sqrt(max(1e-9, r**2 - (x-cx)**2)), 1.0 )
                })
            elif edge_type == 2:
                # Near-touching semicircle (gap of epsilon)
                r = random.uniform(0.5, 2.0) * scale
                eps = random.choice([1e-7, 1e-5, 1e-4]) * scale
                cx = gx + r + eps
                cy = gy
                equation = f"y - {cy:.6f} - sqrt({r**2:.6f} - (x - {cx:.6f})**2)"
                curves.append({
                    "type": "semicircle", "equation": equation,
                    "endpoints": [[gx + eps, gy], [gx + eps + 2*r, gy]], "scale": scale,
                    "eval": lambda x, y, cx=cx, cy=cy, r=r: y - cy - math.sqrt(max(0, r**2 - (x - cx)**2)) if abs(x-cx) <= r else 1e3,
                    "deriv": lambda x, y, cx=cx, cy=cy, r=r: ( (x-cx)/math.sqrt(max(1e-9, r**2 - (x-cx)**2)), 1.0 )
                })
            else:
                # Radical line segment starting exactly at touching point
                k = random.uniform(0.5, 1.5)
                equation = f"y - {gy:.6f} - {k:.6f}*sqrt(x - {gx:.6f})"
                curves.append({
                    "type": "radical", "equation": equation,
                    "endpoints": [[gx, gy]], "scale": scale,
                    "eval": lambda x, y, cx=gx, cy=gy, k=k: y - cy - k*math.sqrt(max(0, x - cx)) if x >= cx else 1e3,
                    "deriv": lambda x, y, cx=gx, cy=gy, k=k: ( -k/(2*math.sqrt(max(1e-9, x - cx))), 1.0 )
                })
                
    elif group_type == 2:
        # Tangent circles and line-curve touches (degenerate intersections)
        # Circle 1 at gx, gy
        r1 = 1.0 * scale
        curves.append({
            "type": "circle", "equation": f"(x - {gx:.6f})**2 + (y - {gy:.6f})**2 - {r1**2:.6f}",
            "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=gx, cy=gy, r=r1: (x-cx)**2 + (y-cy)**2 - r**2,
            "deriv": lambda x, y, cx=gx, cy=gy: (2*(x-cx), 2*(y-cy))
        })
        
        # Circle 2 tangent externally to Circle 1 on the right
        r2 = 1.5 * scale
        cx2 = gx + r1 + r2
        curves.append({
            "type": "circle", "equation": f"(x - {cx2:.6f})**2 + (y - {gy:.6f})**2 - {r2**2:.6f}",
            "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=cx2, cy=gy, r=r2: (x-cx)**2 + (y-cy)**2 - r**2,
            "deriv": lambda x, y, cx=cx2, cy=gy: (2*(x-cx), 2*(y-cy))
        })
        
        # Line tangent to Circle 1 at the top: y = gy + r1
        ty = gy + r1
        curves.append({
            "type": "line", "equation": f"y - {ty:.6f}",
            "endpoints": [], "scale": scale,
            "eval": lambda x, y, ty=ty: y - ty,
            "deriv": lambda x, y: (0.0, 1.0)
        })
        
        # Circle 3 tangent internally to Circle 1
        r3 = 0.5 * scale
        cx3 = gx + (r1 - r3)
        curves.append({
            "type": "circle", "equation": f"(x - {cx3:.6f})**2 + (y - {gy:.6f})**2 - {r3**2:.6f}",
            "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=cx3, cy=gy, r=r3: (x-cx)**2 + (y-cy)**2 - r**2,
            "deriv": lambda x, y, cx=cx3, cy=gy: (2*(x-cx), 2*(y-cy))
        })
        
        # Add remaining standard shapes to fill up 10
        for i in range(6):
            cx = gx + random.uniform(-2, 2) * scale
            cy = gy + random.uniform(-2, 2) * scale
            r = random.uniform(0.3, 1.0) * scale
            curves.append({
                "type": "circle", "equation": f"(x - {cx:.6f})**2 + (y - {cy:.6f})**2 - {r**2:.6f}",
                "endpoints": [], "scale": scale,
                "eval": lambda x, y, cx=cx, cy=cy, r=r: (x-cx)**2 + (y-cy)**2 - r**2,
                "deriv": lambda x, y, cx=cx, cy=cy: (2*(x-cx), 2*(y-cy))
            })
            
    elif group_type == 3:
        # Near-miss curves (very close but do not intersect)
        # We will create circles with a tiny gap between them
        for i in range(CURVES_PER_GROUP // 2):
            gap = random.choice([1.5e-3, 3e-3, 6e-3]) * scale
            r1 = random.uniform(0.5, 1.5) * scale
            r2 = random.uniform(0.5, 1.5) * scale
            
            # Place two circles separated horizontally by r1 + r2 + gap
            # Circle A
            cx_a = gx - r1 - gap/2
            curves.append({
                "type": "circle", "equation": f"(x - {cx_a:.6f})**2 + (y - {gy:.6f})**2 - {r1**2:.6f}",
                "endpoints": [], "scale": scale,
                "eval": lambda x, y, cx=cx_a, cy=gy, r=r1: (x-cx)**2 + (y-cy)**2 - r**2,
                "deriv": lambda x, y, cx=cx_a, cy=gy: (2*(x-cx), 2*(y-cy))
            })
            
            # Circle B
            cx_b = gx + r2 + gap/2
            curves.append({
                "type": "circle", "equation": f"(x - {cx_b:.6f})**2 + (y - {gy:.6f})**2 - {r2**2:.6f}",
                "endpoints": [], "scale": scale,
                "eval": lambda x, y, cx=cx_b, cy=gy, r=r2: (x-cx)**2 + (y-cy)**2 - r**2,
                "deriv": lambda x, y, cx=cx_b, cy=gy: (2*(x-cx), 2*(y-cy))
            })
            
    elif group_type == 4:
        # Transcendentals & Periodic curves
        # 1. Periodic Radical curve: y^2 - A*sin(B*x + C) = 0
        a_param = random.uniform(0.5, 2.0) * scale
        b_param = random.uniform(0.5, 1.5)
        c_param = random.uniform(-1, 1)
        equation = f"y**2 - {a_param:.6f}*sin({b_param:.6f}*x + {c_param:.6f})"
        
        # Calculate infinite endpoints: where sin(B*x + C) = 0 => B*x + C = k*pi => x = (k*pi - C)/B
        # Find 10 closest to origin
        endpoints = []
        k_values = sorted(range(-10, 11), key=lambda k: abs((k*math.pi - c_param)/b_param))
        for k in k_values[:10]:
            x_val = (k * math.pi - c_param) / b_param
            endpoints.append([x_val, 0.0])
            
        curves.append({
            "type": "periodic_radical", "equation": equation, "endpoints": endpoints, "scale": scale,
            "eval": lambda x, y, a=a_param, b=b_param, c=c_param: y**2 - a*math.sin(b*x + c) if a*math.sin(b*x+c) >= -1e-9 else 1e3,
            "deriv": lambda x, y, a=a_param, b=b_param, c=c_param: (-a*b*math.cos(b*x + c), 2*y)
        })
        
        # 2. Arcsin curve: y - y0 - A*arcsin(B*(x - x0)) = 0
        cx = gx
        cy = gy
        a_arcsin = random.uniform(0.5, 1.5) * scale
        b_arcsin = random.uniform(0.5, 1.5) / scale
        equation = f"y - {cy:.6f} - {a_arcsin:.6f}*asin({b_arcsin:.6f}*(x - {cx:.6f}))"
        curves.append({
            "type": "arcsin", "equation": equation,
            "endpoints": [[cx - 1/b_arcsin, cy - a_arcsin*math.pi/2], [cx + 1/b_arcsin, cy + a_arcsin*math.pi/2]], "scale": scale,
            "eval": lambda x, y, cx=cx, cy=cy, a=a_arcsin, b=b_arcsin: y - cy - a*math.asin(max(-1.0, min(1.0, b*(x-cx)))) if abs(b*(x-cx)) <= 1.0 else 1e3,
            "deriv": lambda x, y, cx=cx, cy=cy, a=a_arcsin, b=b_arcsin: (-a*b/math.sqrt(max(1e-9, 1.0 - (b*(x-cx))**2)), 1.0)
        })
        
        # Add remaining standard shapes to make 10
        for i in range(8):
            ctype = random.choice(["line", "circle"])
            if ctype == "line":
                line_x = gx + random.uniform(-1, 1) * scale
                curves.append({
                    "type": "line", "equation": f"x - {line_x:.6f}", "endpoints": [], "scale": scale,
                    "eval": lambda x, y, target=line_x: x - target,
                    "deriv": lambda x, y: (1.0, 0.0)
                })
            else:
                cx_c = gx + random.uniform(-1, 1) * scale
                cy_c = gy + random.uniform(-1, 1) * scale
                r = random.uniform(0.5, 1.5) * scale
                curves.append({
                    "type": "circle", "equation": f"(x - {cx_c:.6f})**2 + (y - {cy_c:.6f})**2 - {r**2:.6f}", "endpoints": [], "scale": scale,
                    "eval": lambda x, y, cx=cx_c, cy=cy_c, r=r: (x-cx)**2 + (y-cy)**2 - r**2,
                    "deriv": lambda x, y, cx=cx_c, cy=cy_c: (2*(x-cx), 2*(y-cy))
                })
                
    else:
        # High-degree Algebraic (Weierstrass/Folium/Lemniscate)
        # 1. Lemniscate of Bernoulli
        a_lem = random.uniform(1.0, 3.0) * scale
        equation = f"((x - {gx:.6f})**2 + (y - {gy:.6f})**2)**2 - {2*a_lem**2:.6f}*((x - {gx:.6f})**2 - (y - {gy:.6f})**2)"
        curves.append({
            "type": "lemniscate", "equation": equation, "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=gx, cy=gy, a=a_lem: ((x-cx)**2 + (y-cy)**2)**2 - 2*a**2*((x-cx)**2 - (y-cy)**2),
            "deriv": lambda x, y, cx=gx, cy=gy, a=a_lem: (
                4*(x-cx)*((x-cx)**2 + (y-cy)**2) - 4*a**2*(x-cx),
                4*(y-cy)*((x-cx)**2 + (y-cy)**2) + 4*a**2*(y-cy)
            )
        })
        
        # 2. Weierstrass Cubic
        a_c = random.uniform(-1.0, 1.0)
        b_c = random.uniform(0.5, 2.0)
        equation = f"(y - {gy:.6f})**2 - (x - {gx:.6f})**3 - {a_c:.6f}*(x - {gx:.6f}) - {b_c:.6f}"
        curves.append({
            "type": "cubic", "equation": equation, "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=gx, cy=gy, a=a_c, b=b_c: (y-cy)**2 - (x-cx)**3 - a*(x-cx) - b,
            "deriv": lambda x, y, cx=gx, cy=gy, a=a_c: (-3*(x-cx)**2 - a, 2*(y-cy))
        })
        
        # 3. Folium of Descartes
        a_f = random.uniform(1.0, 2.0) * scale
        equation = f"(x - {gx:.6f})**3 + (y - {gy:.6f})**3 - {3*a_f:.6f}*(x - {gx:.6f})*(y - {gy:.6f})"
        curves.append({
            "type": "folium", "equation": equation, "endpoints": [], "scale": scale,
            "eval": lambda x, y, cx=gx, cy=gy, a=a_f: (x-cx)**3 + (y-cy)**3 - 3*a*(x-cx)*(y-cy),
            "deriv": lambda x, y, cx=gx, cy=gy, a=a_f: (
                3*(x-cx)**2 - 3*a*(y-cy),
                3*(y-cy)**2 - 3*a*(x-cx)
            )
        })
        
        # Add standard shapes to make 10
        for i in range(7):
            cx = gx + random.uniform(-1.5, 1.5) * scale
            cy = gy + random.uniform(-1.5, 1.5) * scale
            r = random.uniform(0.5, 1.5) * scale
            curves.append({
                "type": "circle", "equation": f"(x - {cx:.6f})**2 + (y - {cy:.6f})**2 - {r**2:.6f}", "endpoints": [], "scale": scale,
                "eval": lambda x, y, cx=cx, cy=cy, r=r: (x-cx)**2 + (y-cy)**2 - r**2,
                "deriv": lambda x, y, cx=cx, cy=cy: (2*(x-cx), 2*(y-cy))
            })
            
    # Write curve record definitions (prepare for insertion)
    curves_records = []
    for i, c in enumerate(curves):
        curve_id = group_id * CURVES_PER_GROUP + i + 1
        # Bounding box estimation based on shape types
        if c["type"] == "line":
            xmin, xmax, ymin, ymax = -100.0, 100.0, -100.0, 100.0
        elif c["type"] == "circle" or c["type"] == "semicircle":
            # Extract center and radius from equations using string splitting to be safe & robust
            # We can also store local values or fallback to wide bounds
            xmin, xmax, ymin, ymax = gx - 5*scale, gx + 5*scale, gy - 5*scale, gy + 5*scale
        else:
            xmin, xmax, ymin, ymax = gx - 10*scale, gx + 10*scale, gy - 10*scale, gy + 10*scale
            
        curves_records.append((
            curve_id, group_id, c["equation"], c["type"], scale,
            xmin, xmax, ymin, ymax, json.dumps(c["endpoints"]), tol
        ))
        c["id"] = curve_id
        
    # Solve intersections inside the group
    intersections_records = []
    
    for i in range(len(curves)):
        for j in range(i + 1, len(curves)):
            c1 = curves[i]
            c2 = curves[j]
            
            pts = []
            relation = "TRANSVERSAL"
            
            # Analytical fast path for Circle-Circle
            if c1["type"] == "circle" and c2["type"] == "circle":
                # Parse equations back or use stored params
                # To be absolutely sure, extract parameters from equation string
                try:
                    # "(x - 1.23)**2 + (y - 4.56)**2 - 9.0"
                    parts1 = c1["equation"].split(" - ")
                    cx1 = float(parts1[1].split(")")[0])
                    cy1 = float(parts1[2].split(")")[0])
                    r1 = math.sqrt(float(parts1[3]))
                    
                    parts2 = c2["equation"].split(" - ")
                    cx2 = float(parts2[1].split(")")[0])
                    cy2 = float(parts2[2].split(")")[0])
                    r2 = math.sqrt(float(parts2[3]))
                    
                    pts = intersect_circle_circle_analytical(cx1, cy1, r1, cx2, cy2, r2)
                    
                    # Determine relation type
                    d = math.sqrt((cx2-cx1)**2 + (cy2-cy1)**2)
                    if d < 1e-8 and abs(r1-r2) < 1e-8:
                        relation = "COINCIDENT"
                    elif abs(d - (r1+r2)) < 1e-6 or abs(d - abs(r1-r2)) < 1e-6:
                        relation = "TANGENT"
                except Exception:
                    pts = []
                    
            # Numerical fallback solver for everything else
            if not pts and relation != "COINCIDENT":
                # Solve using numerical solver on a localized grid
                # Sample grid to find starting points
                x_sample = np.linspace(gx - 5*scale, gx + 5*scale, 40)
                y_sample = np.linspace(gy - 5*scale, gy + 5*scale, 40)
                X, Y = np.meshgrid(x_sample, y_sample)
                
                # Vectorized evaluation to find candidates
                try:
                    Z1 = np.vectorize(c1["eval"])(X, Y)
                    Z2 = np.vectorize(c2["eval"])(X, Y)
                    
                    mask = (np.abs(Z1) < 0.2*scale) & (np.abs(Z2) < 0.2*scale)
                    candidates = np.column_stack([X[mask], Y[mask]])
                    
                    refined = []
                    for cand in candidates:
                        def system(p):
                            return [c1["eval"](p[0], p[1]), c2["eval"](p[0], p[1])]
                        
                        try:
                            sol, infodict, ier, mesg = fsolve(system, cand, full_output=True, xtol=tol)
                            if ier == 1:
                                # Verify the residual is actually small
                                residual = system(sol)
                                if math.sqrt(residual[0]**2 + residual[1]**2) < 1e-6 * scale:
                                    # Ensure it respects bounds / domains for radical/semicircle curves
                                    # Semicircle check:
                                    valid = True
                                    for c in [c1, c2]:
                                        if c["type"] == "semicircle":
                                            # Validate semicircle bounds
                                            # Equation contains the radius
                                            parts = c["equation"].split(" - ")
                                            cx = float(parts[1].split(")")[0])
                                            cy = float(parts[2].split(")")[0])
                                            r = math.sqrt(float(parts[3].split(" - ")[0].split("sqrt(")[1]))
                                            if abs(sol[0] - cx) > r + 1e-6:
                                                valid = False
                                        elif c["type"] == "radical":
                                            # Must be >= gx
                                            parts = c["equation"].split("x - ")
                                            gx_rad = float(parts[1].split(")")[0])
                                            if sol[0] < gx_rad - 1e-6:
                                                valid = False
                                                
                                    if valid:
                                        # Check duplicate
                                        if not any(math.sqrt((sol[0]-r[0])**2 + (sol[1]-r[1])**2) < 1e-4 * scale for r in refined):
                                            refined.append((float(sol[0]), float(sol[1])))
                        except Exception:
                            continue
                    
                    pts = refined
                except Exception:
                    pts = []
                    
            # Detect tangency vs transversal vs near misses numerically
            if len(pts) == 1 and relation != "COINCIDENT":
                # Check if it is a tangent touch or near miss
                # Evaluate gradient compatibility
                pt = pts[0]
                try:
                    g1x, g1y = c1["deriv"](pt[0], pt[1])
                    g2x, g2y = c2["deriv"](pt[0], pt[1])
                    
                    norm1 = math.sqrt(g1x**2 + g1y**2)
                    norm2 = math.sqrt(g2x**2 + g2y**2)
                    if norm1 > 1e-9 and norm2 > 1e-9:
                        # Angle between gradients is near 0 or pi
                        cos_theta = abs(g1x*g2x + g1y*g2y) / (norm1 * norm2)
                        if abs(cos_theta - 1.0) < 1e-3:
                            relation = "TANGENT"
                except Exception:
                    pass
            
            # Detect near-miss group specifically
            if not pts and group_type == 3:
                relation = "NEAR_MISS"
                
            # Restrict to 10 closest to origin
            pts = sorted(pts, key=lambda p: p[0]**2 + p[1]**2)[:10]
            
            if pts or relation != "TRANSVERSAL":
                # Sparse storage: only store non-empty intersections or edge cases
                intersections_records.append((
                    c1["id"], c2["id"], json.dumps(pts), relation
                ))
                
    return curves_records, intersections_records

# ==================== Multiprocessing Runner ====================

def writer_process(queue, db_path, total_groups):
    """Background writer to stream results to SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    written_groups = 0
    
    while True:
        data = queue.get()
        if data is None:
            break
            
        curves_records, intersections_records = data
        
        # Batch insert
        cursor.executemany("INSERT INTO curves VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", curves_records)
        if intersections_records:
            cursor.executemany("INSERT INTO intersections VALUES (?, ?, ?, ?);", intersections_records)
            
        written_groups += 1
        
        # Commit periodically
        if written_groups % BATCH_SIZE == 0:
            conn.commit()
            sys.stdout.write(f"\rProgress: {written_groups}/{total_groups} groups generated...")
            sys.stdout.flush()
            
    conn.commit()
    conn.close()
    print(f"\nSuccessfully committed {written_groups} groups to database.")

def main():
    print("Initializing SQLite database...")
    init_db(DB_PATH)
    
    num_cores = max(1, mp.cpu_count() - 1)
    print(f"Starting multiprocessing pool with {num_cores} workers...")
    
    manager = mp.Manager()
    queue = manager.Queue(maxsize=1000)
    
    # Start writer process
    writer = mp.Process(target=writer_process, args=(queue, DB_PATH, TOTAL_GROUPS))
    writer.start()
    
    # Create arguments for pool workers
    tasks = [(g_id, random.randint(0, 10000000)) for g_id in range(TOTAL_GROUPS)]
    
    # Process tasks in parallel using pool
    with mp.Pool(processes=num_cores) as pool:
        for result in pool.imap_unordered(generate_spatial_group, tasks, chunksize=50):
            queue.put(result)
            
    # Signal writer process to finish
    queue.put(None)
    writer.join()
    
    print("Database generation complete!")
    print(f"Saved database to: {DB_PATH}")

if __name__ == "__main__":
    main()
