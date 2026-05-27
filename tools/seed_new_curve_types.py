#!/usr/bin/env python3
"""
tools/seed_new_curve_types.py

Populates curves.db with entries for the five new geometry types:
  ParametricSegment, Superellipse, RFunctionCurve, ProceduralCurve, BaseField.

Run from the project root:
    $env:PYTHONPATH="."; uv run python tools/seed_new_curve_types.py

The script is idempotent: it recreates the `new_curve_types` table on each run
so tests always see a clean, canonical data set.
"""

import os
import sys
import json
import math
import sqlite3

import numpy as np

# ── project root on path ─────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "curves.db")

# ── helpers ───────────────────────────────────────────────────────────────────


def _sample_parametric(x_fn, y_fn, t_start, t_end, n=50):
    """Return n (x,y) samples of a parametric curve."""
    ts = np.linspace(t_start, t_end, n)
    return [
        [float(x_fn(t)), float(y_fn(t))]
        for t in ts
        if np.isfinite(x_fn(t)) and np.isfinite(y_fn(t))
    ]


def _sample_superellipse(a, b, n_exp, n=50):
    """Return n (x, y, f(x,y)) evaluation triples on a 5×10 grid."""
    rows = []
    for xi in np.linspace(-a * 0.9, a * 0.9, 5):
        for yi in np.linspace(-b * 0.9, b * 0.9, 10):
            fval = abs(xi / a) ** n_exp + abs(yi / b) ** n_exp - 1.0
            rows.append([float(xi), float(yi), float(fval)])
    return rows


def _circle_eval(r, x, y):
    return x**2 + y**2 - r**2


def _ellipse_eval(a, b, x, y):
    return (x / a) ** 2 + (y / b) ** 2 - 1.0


# ── parametric curve definitions ──────────────────────────────────────────────

PARAMETRIC_CURVES = [
    dict(
        name="circle_arc_q1",
        description="Quarter circle arc (Q1), r=1",
        x_expr="cos(t)",
        y_expr="sin(t)",
        t_start=0.0,
        t_end=math.pi / 2,
        x_fn=lambda t: math.cos(t),
        y_fn=lambda t: math.sin(t),
        paired_curve={"type": "line", "eq": "y - 0.5"},
        analytical_intersections=[[math.cos(math.asin(0.5)), 0.5]],
    ),
    dict(
        name="full_circle_r2",
        description="Full circle r=2 (parametric)",
        x_expr="2*cos(t)",
        y_expr="2*sin(t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: 2 * math.cos(t),
        y_fn=lambda t: 2 * math.sin(t),
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[[2.0, 0.0], [-2.0, 0.0]],
    ),
    dict(
        name="ellipse_arc_upper",
        description="Upper half of ellipse a=3,b=1",
        x_expr="3*cos(t)",
        y_expr="sin(t)",
        t_start=0.0,
        t_end=math.pi,
        x_fn=lambda t: 3 * math.cos(t),
        y_fn=lambda t: math.sin(t),
        paired_curve={"type": "line", "eq": "y - 0.5"},
        analytical_intersections=[
            [3 * math.cos(math.asin(0.5)), 0.5],
            [-3 * math.cos(math.asin(0.5)), 0.5],
        ],
    ),
    dict(
        name="lissajous_3_2",
        description="Lissajous 3:2, [0, 2pi]",
        x_expr="sin(3*t)",
        y_expr="sin(2*t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.sin(3 * t),
        y_fn=lambda t: math.sin(2 * t),
        paired_curve={"type": "circle", "eq": "x^2+y^2-0.25"},
        analytical_intersections=[],  # computed numerically during test
    ),
    dict(
        name="cycloid_one_arch",
        description="Cycloid (one arch)",
        x_expr="t - sin(t)",
        y_expr="1 - cos(t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: t - math.sin(t),
        y_fn=lambda t: 1 - math.cos(t),
        paired_curve={"type": "line", "eq": "y - 1"},
        # y=1 when cos(t)=0, i.e. t=pi/2 and 3pi/2
        analytical_intersections=[
            [math.pi / 2 - math.sin(math.pi / 2), 1.0],
            [3 * math.pi / 2 - math.sin(3 * math.pi / 2), 1.0],
        ],
    ),
    dict(
        name="astroid",
        description="Astroid (r=1)",
        x_expr="cos(t)**3",
        y_expr="sin(t)**3",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.cos(t) ** 3,
        y_fn=lambda t: math.sin(t) ** 3,
        paired_curve={"type": "circle", "eq": "x^2+y^2-0.25"},
        analytical_intersections=[],  # 8 intersections, computed in test
    ),
    dict(
        name="rose_3_petal",
        description="3-petal rose curve",
        x_expr="cos(3*t)*cos(t)",
        y_expr="cos(3*t)*sin(t)",
        t_start=0.0,
        t_end=math.pi,
        x_fn=lambda t: math.cos(3 * t) * math.cos(t),
        y_fn=lambda t: math.cos(3 * t) * math.sin(t),
        paired_curve={"type": "circle", "eq": "x^2+y^2-0.25"},
        analytical_intersections=[],
    ),
    dict(
        name="trefoil_knot",
        description="Trefoil-like plane curve",
        x_expr="sin(t) + 2*sin(2*t)",
        y_expr="cos(t) - 2*cos(2*t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.sin(t) + 2 * math.sin(2 * t),
        y_fn=lambda t: math.cos(t) - 2 * math.cos(2 * t),
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[],  # multiple, computed in test
    ),
    dict(
        name="archimedean_spiral",
        description="Archimedean spiral arc",
        x_expr="t*cos(t)",
        y_expr="t*sin(t)",
        t_start=0.0,
        t_end=3 * math.pi,
        x_fn=lambda t: t * math.cos(t),
        y_fn=lambda t: t * math.sin(t),
        paired_curve={"type": "line", "eq": "y - x"},
        analytical_intersections=[],
    ),
    dict(
        name="parabola_segment",
        description="Parabola y=t^2, t in [-2,2]",
        x_expr="t",
        y_expr="t**2",
        t_start=-2.0,
        t_end=2.0,
        x_fn=lambda t: t,
        y_fn=lambda t: t**2,
        paired_curve={"type": "line", "eq": "y - 1"},
        analytical_intersections=[[-1.0, 1.0], [1.0, 1.0]],
    ),
    dict(
        name="sine_arch",
        description="Sine arch, x in [0,pi]",
        x_expr="t",
        y_expr="sin(t)",
        t_start=0.0,
        t_end=math.pi,
        x_fn=lambda t: t,
        y_fn=lambda t: math.sin(t),
        paired_curve={"type": "line", "eq": "y - 0.5"},
        analytical_intersections=[
            [math.pi / 6, 0.5],
            [5 * math.pi / 6, 0.5],
        ],
    ),
    dict(
        name="hypotrochoid",
        description="Hypotrochoid (R=3,r=1,d=2)",
        x_expr="2*cos(t)+cos(2*t)",
        y_expr="2*sin(t)-sin(2*t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: 2 * math.cos(t) + math.cos(2 * t),
        y_fn=lambda t: 2 * math.sin(t) - math.sin(2 * t),
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[],
    ),
    dict(
        name="line_segment_diagonal",
        description="Line segment from (0,-1) to (1,1)",
        x_expr="t",
        y_expr="2*t - 1",
        t_start=0.0,
        t_end=1.0,
        x_fn=lambda t: t,
        y_fn=lambda t: 2 * t - 1,
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        # 2t-1=y, x=t → t²+(2t-1)²=1 → 5t²-4t=0 → t=0 or t=4/5
        analytical_intersections=[[0.0, -1.0], [0.8, 0.6]],
    ),
    dict(
        name="figure_eight",
        description="Figure-eight (lemniscate param)",
        x_expr="sin(t)",
        y_expr="sin(2*t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.sin(t),
        y_fn=lambda t: math.sin(2 * t),
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[[0.0, 0.0], [0.0, 0.0]],  # self-int at origin
    ),
    dict(
        name="ellipse_arc_lower",
        description="Lower half ellipse a=2,b=1",
        x_expr="2*cos(t)",
        y_expr="-sin(t)",
        t_start=math.pi,
        t_end=2 * math.pi,
        x_fn=lambda t: 2 * math.cos(t),
        y_fn=lambda t: -math.sin(t),
        paired_curve={"type": "circle", "eq": "x^2+y^2-2.25"},
        analytical_intersections=[],
    ),
    dict(
        name="cardioid_param",
        description="Cardioid (parametric)",
        x_expr="cos(t)*(1+cos(t))",
        y_expr="sin(t)*(1+cos(t))",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.cos(t) * (1 + math.cos(t)),
        y_fn=lambda t: math.sin(t) * (1 + math.cos(t)),
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[],
    ),
    dict(
        name="viviani_curve",
        description="Viviani curve (x=1+cos(t), y=sin(t))",
        x_expr="1+cos(t)",
        y_expr="sin(t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: 1 + math.cos(t),
        y_fn=lambda t: math.sin(t),
        paired_curve={"type": "line", "eq": "x - 1"},
        analytical_intersections=[[1.0, 0.0], [1.0, 0.0]],
    ),
    dict(
        name="folded_sine",
        description="Folded sine y=sin(t)+sin(2t), t in [-pi,pi]",
        x_expr="t",
        y_expr="sin(t)+sin(2*t)",
        t_start=-math.pi,
        t_end=math.pi,
        x_fn=lambda t: t,
        y_fn=lambda t: math.sin(t) + math.sin(2 * t),
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[[-math.pi, 0.0], [0.0, 0.0], [math.pi, 0.0]],
    ),
    dict(
        name="involute_circle",
        description="Involute of circle (r=1)",
        x_expr="cos(t)+t*sin(t)",
        y_expr="sin(t)-t*cos(t)",
        t_start=0.0,
        t_end=2 * math.pi,
        x_fn=lambda t: math.cos(t) + t * math.sin(t),
        y_fn=lambda t: math.sin(t) - t * math.cos(t),
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[[1.0, 0.0]],
    ),
    dict(
        name="cubic_bezier_approx",
        description="Cubic Bezier P0=(0,0) P1=(0.5,1) P2=(0.5,-1) P3=(1,0)",
        x_expr="3*0.5*t*(1-t)**2 + 3*0.5*t**2*(1-t) + t**3",
        y_expr="3*t*(1-t)**2 - 3*t**2*(1-t)",
        t_start=0.0,
        t_end=1.0,
        x_fn=lambda t: 3 * 0.5 * t * (1 - t) ** 2 + 3 * 0.5 * t**2 * (1 - t) + t**3,
        y_fn=lambda t: 3 * t * (1 - t) ** 2 - 3 * t**2 * (1 - t),
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[[0.0, 0.0], [1.0, 0.0]],
    ),
]

# ── superellipse definitions ───────────────────────────────────────────────────

SUPERELLIPSES = [
    dict(a=1.0, b=1.0, n=2.0, desc="Unit circle (n=2)"),
    dict(a=2.0, b=1.0, n=2.0, desc="Ellipse a=2,b=1 (n=2)"),
    dict(a=1.5, b=1.5, n=4.0, desc="Squircle r=1.5 (n=4)"),
    dict(a=1.5, b=1.5, n=1.0, desc="Diamond r=1.5 (n=1)"),
    dict(a=2.0, b=1.0, n=4.0, desc="Squished squircle a=2,b=1 (n=4)"),
    dict(a=1.0, b=2.0, n=4.0, desc="Tall squircle a=1,b=2 (n=4)"),
    dict(a=1.0, b=1.0, n=6.0, desc="Near-square r=1 (n=6)"),
    dict(a=3.0, b=1.0, n=2.0, desc="Wide ellipse a=3,b=1 (n=2)"),
    dict(a=1.5, b=1.5, n=3.0, desc="Rounded triangle a=b=1.5 (n=3)"),
    dict(a=2.0, b=2.0, n=1.0, desc="Large diamond a=b=2 (n=1)"),
    dict(a=1.0, b=1.0, n=1.5, desc="Rounded diamond r=1 (n=1.5)"),
    dict(a=2.0, b=1.0, n=6.0, desc="Wide near-square a=2,b=1 (n=6)"),
    dict(a=1.0, b=1.0, n=10.0, desc="Nearly square r=1 (n=10)"),
    dict(a=1.2, b=0.8, n=4.0, desc="Asymmetric squircle a=1.2,b=0.8 (n=4)"),
    dict(a=2.5, b=1.5, n=3.0, desc="Large rounded a=2.5,b=1.5 (n=3)"),
]


def _superellipse_intersects_circle(a, b, n_exp, r):
    """Numerically find intersections of |x/a|^n + |y/b|^n = 1 and x²+y²=r²."""
    # Sweep angle on superellipse boundary
    pts = []
    N = 2000
    ts = np.linspace(0, 2 * math.pi, N)
    # Parametrize superellipse: x = a*sign(cos)*|cos|^(2/n), y = b*sign(sin)*|sin|^(2/n)
    inv_n = 2.0 / n_exp
    xs = a * np.sign(np.cos(ts)) * np.abs(np.cos(ts)) ** inv_n
    ys = b * np.sign(np.sin(ts)) * np.abs(np.sin(ts)) ** inv_n
    dist = xs**2 + ys**2 - r**2
    for i in range(N - 1):
        if dist[i] * dist[i + 1] < 0:
            # Linear interpolation
            t_cross = ts[i] - dist[i] * (ts[i + 1] - ts[i]) / (dist[i + 1] - dist[i])
            xc = a * math.copysign(abs(math.cos(t_cross)) ** inv_n, math.cos(t_cross))
            yc = b * math.copysign(abs(math.sin(t_cross)) ** inv_n, math.sin(t_cross))
            pts.append([round(xc, 5), round(yc, 5)])
    return pts


# ── rfunction curve definitions ───────────────────────────────────────────────


def _build_rfunction_rows():
    rows = []
    import sympy as sp

    x, y = sp.symbols("x y")

    # Common child curves (defined as specs, not objects, for JSON storage)
    def circle_spec(cx, cy, r):
        return {"type": "ConicSection", "expr": f"(x-{cx})**2+(y-{cy})**2-{r**2}"}

    def superellipse_spec(a, b, n):
        return {"type": "Superellipse", "a": a, "b": b, "n": n}

    configs = [
        # UNION (10)
        (
            "union",
            circle_spec(0, 0, 1),
            circle_spec(1, 0, 1),
            0.0,
            "Union of two unit circles",
        ),
        (
            "union",
            circle_spec(0, 0, 2),
            circle_spec(1.5, 0, 1),
            0.0,
            "Union: large ∪ small",
        ),
        (
            "union",
            circle_spec(0, 0, 1.5),
            {"type": "ConicSection", "expr": "x**2/4+y**2-1"},
            0.0,
            "Union: circle ∪ ellipse",
        ),
        (
            "union",
            superellipse_spec(1, 1, 4),
            circle_spec(0, 0, 0.5),
            0.0,
            "Union: squircle ∪ small circle",
        ),
        (
            "union",
            circle_spec(-1, 0, 1),
            circle_spec(1, 0, 1),
            0.0,
            "Union: symmetric circles",
        ),
        (
            "union",
            circle_spec(0, 0, 1),
            {"type": "ConicSection", "expr": "x**2/2.25+y**2-1"},
            0.0,
            "Union: circle ∪ wide ellipse",
        ),
        (
            "union",
            superellipse_spec(1.5, 1.5, 4),
            superellipse_spec(1, 1, 2),
            0.0,
            "Union: squircle ∪ circle",
        ),
        (
            "union",
            circle_spec(0, 0, 2),
            superellipse_spec(2, 2, 6),
            0.0,
            "Union: circle ∪ near-square",
        ),
        (
            "union",
            circle_spec(0.5, 0, 1),
            circle_spec(-0.5, 0, 1),
            0.0,
            "Union: overlapping circles",
        ),
        (
            "union",
            superellipse_spec(2, 1, 3),
            circle_spec(0, 0, 1),
            0.0,
            "Union: tall superellipse ∪ unit circle",
        ),
        # INTERSECTION (10)
        (
            "intersection",
            circle_spec(0, 0, 2),
            superellipse_spec(1.5, 1.5, 10),
            0.0,
            "Intersect: circle ∩ near-square",
        ),
        (
            "intersection",
            circle_spec(0, 0, 1.5),
            {"type": "ConicSection", "expr": "x**2/4+y**2-1"},
            0.0,
            "Intersect: circle ∩ ellipse",
        ),
        (
            "intersection",
            circle_spec(-0.5, 0, 1.5),
            circle_spec(0.5, 0, 1.5),
            0.0,
            "Intersect: two circles",
        ),
        (
            "intersection",
            superellipse_spec(1.5, 1.5, 4),
            circle_spec(0, 0, 1.2),
            0.0,
            "Intersect: squircle ∩ circle",
        ),
        (
            "intersection",
            superellipse_spec(2, 1, 4),
            superellipse_spec(1, 2, 4),
            0.0,
            "Intersect: cross superellipses",
        ),
        (
            "intersection",
            circle_spec(0, 0, 2),
            circle_spec(1, 0, 2),
            0.0,
            "Intersect: overlapping circles",
        ),
        (
            "intersection",
            superellipse_spec(1, 1, 6),
            circle_spec(0, 0, 0.95),
            0.0,
            "Intersect: near-sq ∩ inner circle",
        ),
        (
            "intersection",
            circle_spec(0, 0, 1.5),
            superellipse_spec(1.5, 1.5, 3),
            0.0,
            "Intersect: circle ∩ rnd-triangle",
        ),
        (
            "intersection",
            superellipse_spec(2, 2, 1),
            circle_spec(0, 0, 1.5),
            0.0,
            "Intersect: diamond ∩ circle",
        ),
        (
            "intersection",
            circle_spec(0, 0, 3),
            {"type": "ConicSection", "expr": "x**2/4+y**2/9-1"},
            0.0,
            "Intersect: circle ∩ tall ellipse",
        ),
        # DIFFERENCE (10)
        (
            "difference",
            circle_spec(0, 0, 2),
            circle_spec(0.5, 0, 1),
            0.0,
            "Diff: pac-man",
        ),
        (
            "difference",
            circle_spec(0, 0, 1.5),
            circle_spec(0, 0, 0.8),
            0.0,
            "Diff: annulus",
        ),
        (
            "difference",
            superellipse_spec(1.5, 1.5, 4),
            circle_spec(0.3, 0, 0.7),
            0.0,
            "Diff: squircle minus circle",
        ),
        (
            "difference",
            circle_spec(0, 0, 2),
            {"type": "ConicSection", "expr": "x**2/4+y**2-1"},
            0.0,
            "Diff: circle minus ellipse",
        ),
        (
            "difference",
            circle_spec(0, 0, 2),
            superellipse_spec(1, 1, 6),
            0.0,
            "Diff: circle minus near-sq",
        ),
        (
            "difference",
            superellipse_spec(2, 1, 4),
            circle_spec(0, 0, 0.8),
            0.0,
            "Diff: wide sq minus circle",
        ),
        (
            "difference",
            circle_spec(-1, 0, 1.5),
            circle_spec(1, 0, 1.5),
            0.0,
            "Diff: left circle minus right",
        ),
        (
            "difference",
            circle_spec(0, 0, 2),
            circle_spec(-0.5, 0, 1.2),
            0.0,
            "Diff: asymmetric pac-man",
        ),
        (
            "difference",
            superellipse_spec(2, 2, 2),
            superellipse_spec(1, 1, 2),
            0.0,
            "Diff: ellipse minus inner",
        ),
        (
            "difference",
            circle_spec(0, 0, 2),
            superellipse_spec(1.5, 1.5, 3),
            0.0,
            "Diff: circle minus rounded tri",
        ),
        # BLEND (10)
        (
            "blend",
            circle_spec(0, 0, 1),
            circle_spec(1, 0, 1),
            0.2,
            "Blend alpha=0.2: two circles",
        ),
        (
            "blend",
            circle_spec(0, 0, 2),
            {"type": "ConicSection", "expr": "x**2/9+y**2-1"},
            0.5,
            "Blend alpha=0.5: circle+ellipse",
        ),
        (
            "blend",
            superellipse_spec(1, 1, 4),
            circle_spec(0, 0, 0.8),
            0.3,
            "Blend alpha=0.3: squircle+circle",
        ),
        (
            "blend",
            circle_spec(-0.5, 0, 1),
            circle_spec(0.5, 0, 1),
            0.4,
            "Blend alpha=0.4: overlapping",
        ),
        (
            "blend",
            circle_spec(0, 0, 1.5),
            superellipse_spec(1.5, 1.5, 3),
            0.25,
            "Blend alpha=0.25: circle+rnd",
        ),
        (
            "blend",
            superellipse_spec(2, 1, 4),
            circle_spec(0, 0, 1.5),
            0.5,
            "Blend alpha=0.5: wide sq+circle",
        ),
        (
            "blend",
            circle_spec(0, 0, 1),
            circle_spec(2, 0, 1),
            0.1,
            "Blend alpha=0.1: far circles",
        ),
        (
            "blend",
            circle_spec(0, 0, 2),
            circle_spec(0, 0, 1),
            0.3,
            "Blend alpha=0.3: concentric",
        ),
        (
            "blend",
            superellipse_spec(1.5, 1, 4),
            superellipse_spec(1, 1.5, 4),
            0.35,
            "Blend alpha=0.35: cross sq",
        ),
        (
            "blend",
            circle_spec(0, 0, 1.5),
            circle_spec(0, 1, 1.5),
            0.45,
            "Blend alpha=0.45: vert offset",
        ),
    ]

    for op, c1_spec, c2_spec, alpha, desc in configs:
        rows.append(
            dict(
                operation=op,
                alpha=alpha,
                curve1_spec=c1_spec,
                curve2_spec=c2_spec,
                description=desc,
            )
        )
    return rows


# ── procedural curve definitions ──────────────────────────────────────────────

PROCEDURAL_CURVES = [
    dict(
        name="sin_minus_y",
        function_desc="sin(x) - y",
        is_periodic=True,
        domain=[-2 * math.pi, 2 * math.pi, -1.5, 1.5],
        eval_samples=[
            [math.pi / 6, 0.5, 0.0],  # on curve
            [0.0, 0.0, 0.0],  # on curve
            [1.0, 0.5, math.sin(1.0) - 0.5],
        ],
        paired_curve={"type": "line", "eq": "y - 0.5"},
        # sin(x)=0.5 → x=pi/6 + 2k*pi or x=5pi/6 + 2k*pi in [-2pi,2pi]
        analytical_intersections=[
            [math.pi / 6, 0.5],
            [5 * math.pi / 6, 0.5],
            [math.pi / 6 - 2 * math.pi, 0.5],
            [5 * math.pi / 6 - 2 * math.pi, 0.5],
        ],
    ),
    dict(
        name="cos_minus_y",
        function_desc="cos(x) - y",
        is_periodic=True,
        domain=[-math.pi, math.pi, -1.5, 1.5],
        eval_samples=[
            [0.0, 1.0, 0.0],
            [math.pi / 3, 0.5, 0.0],
        ],
        paired_curve={"type": "line", "eq": "y - 0.5"},
        analytical_intersections=[
            [math.pi / 3, 0.5],
            [-math.pi / 3, 0.5],
        ],
    ),
    dict(
        name="gaussian_minus_y",
        function_desc="exp(-x**2) - y",
        is_periodic=False,
        domain=[-3.0, 3.0, 0.0, 1.1],
        eval_samples=[
            [0.0, 1.0, 0.0],
            [1.0, math.exp(-1.0), 0.0],
        ],
        paired_curve={"type": "line", "eq": "y - 0.5"},
        # exp(-x^2)=0.5 → x=±sqrt(ln2)
        analytical_intersections=[
            [math.sqrt(math.log(2)), 0.5],
            [-math.sqrt(math.log(2)), 0.5],
        ],
    ),
    dict(
        name="ripple_circle",
        function_desc="x**2 + y**2 + sin(5*x) - 1",
        is_periodic=True,
        domain=[-2.0, 2.0, -2.0, 2.0],
        eval_samples=[[0.0, 1.0, math.sin(0.0)]],
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[],
    ),
    dict(
        name="sin_x_times_y",
        function_desc="sin(x*y)",
        is_periodic=True,
        domain=[-3.0, 3.0, -3.0, 3.0],
        eval_samples=[
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        paired_curve={"type": "line", "eq": "x"},
        analytical_intersections=[],  # hyperbolic lattice
    ),
    dict(
        name="x_sin_y_minus_1",
        function_desc="x*sin(y) - 1",
        is_periodic=True,
        domain=[-4.0, 4.0, -4.0, 4.0],
        eval_samples=[
            [1.0 / math.sin(1.0), 1.0, 0.0],
        ],
        paired_curve={"type": "line", "eq": "y - 1"},
        analytical_intersections=[[1.0 / math.sin(1.0), 1.0]],
    ),
    dict(
        name="sin_x_plus_sin_y",
        function_desc="sin(x) + sin(y)",
        is_periodic=True,
        domain=[-math.pi, math.pi, -math.pi, math.pi],
        eval_samples=[
            [0.0, 0.0, 0.0],
            [math.pi / 2, -math.pi / 2, 0.0],
        ],
        paired_curve={"type": "line", "eq": "y"},
        analytical_intersections=[
            [0.0, 0.0],
            [math.pi, -math.pi],
            [-math.pi, math.pi],
        ],
    ),
    dict(
        name="tanh_minus_y",
        function_desc="tanh(x) - y",
        is_periodic=False,
        domain=[-3.0, 3.0, -1.5, 1.5],
        eval_samples=[
            [0.0, 0.0, 0.0],
        ],
        paired_curve={"type": "line", "eq": "y - 0.5"},
        # tanh(x)=0.5 → x=0.5*ln(3)
        analytical_intersections=[[0.5 * math.log(3), 0.5]],
    ),
    dict(
        name="cos_r_squared",
        function_desc="cos(x**2+y**2) - 0.5",
        is_periodic=True,
        domain=[-2.0, 2.0, -2.0, 2.0],
        eval_samples=[
            [math.sqrt(math.pi / 3), 0.0, 0.0],
        ],
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[],  # concentric rings
    ),
    dict(
        name="atan2_minus_1",
        function_desc="atan2(y, x) - 1",
        is_periodic=False,
        domain=[-2.0, 2.0, -2.0, 2.0],
        eval_samples=[
            [math.cos(1.0), math.sin(1.0), 0.0],
        ],
        paired_curve={"type": "circle", "eq": "x^2+y^2-1"},
        analytical_intersections=[[math.cos(1.0), math.sin(1.0)]],
    ),
]


# ── field definitions ─────────────────────────────────────────────────────────

FIELD_ENTRIES = [
    dict(
        name="curvefield_circle_r2",
        field_type="CurveField",
        curve_spec={"type": "ConicSection", "expr": "x**2+y**2-4"},
        description="CurveField wrapping circle r=2",
        eval_samples=[
            [0.0, 0.0, -4.0],  # inside: f=(0+0-4)=-4
            [2.0, 0.0, 0.0],  # on boundary
            [3.0, 0.0, 5.0],  # outside
        ],
        zero_isoline_desc="circle r=2",
    ),
    dict(
        name="curvefield_ellipse_a3b1",
        field_type="CurveField",
        curve_spec={"type": "ConicSection", "expr": "x**2/9+y**2-1"},
        description="CurveField wrapping ellipse a=3,b=1",
        eval_samples=[
            [0.0, 0.0, -1.0],
            [3.0, 0.0, 0.0],
            [0.0, 1.5, 1.25],
        ],
        zero_isoline_desc="ellipse a=3,b=1",
    ),
    dict(
        name="blendedfield_add_circles",
        field_type="BlendedField",
        operation="add",
        fields_spec=[
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-4"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-1"},
            },
        ],
        description="BlendedField add: circle(r=2) + circle(r=1)",
        eval_samples=[
            [0.0, 0.0, -5.0],  # -4 + -1
            [2.0, 0.0, 3.0],  # 0 + 3
        ],
        zero_isoline_desc="combined zero contour",
    ),
    dict(
        name="blendedfield_min_union",
        field_type="BlendedField",
        operation="min",
        fields_spec=[
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "(x-0.5)**2+y**2-1"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "(x+0.5)**2+y**2-1"},
            },
        ],
        description="BlendedField min: union boundary of two unit circles",
        eval_samples=[
            [0.0, 0.0, -0.75],  # inside both: (-0.5)^2-1 = -0.75
            [3.0, 0.0, 5.25],  # outside both: (2.5)^2-1 = 5.25
        ],
        zero_isoline_desc="union boundary",
    ),
    dict(
        name="blendedfield_multiply",
        field_type="BlendedField",
        operation="multiply",
        fields_spec=[
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-4"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2/9+y**2-1"},
            },
        ],
        description="BlendedField multiply: circle(r=2) × ellipse",
        eval_samples=[
            [0.0, 0.0, 4.0],  # (-4)*(-1)=4
        ],
        zero_isoline_desc="product zero contour",
    ),
    dict(
        name="sdf_circle_r2",
        field_type="SignedDistanceField",
        region_spec={"type": "circle", "expr": "x**2+y**2-4", "cx": 0, "cy": 0, "r": 2},
        description="SignedDistanceField of disk r=2",
        eval_samples=[
            [0.0, 0.0, -2.0],  # inside, at centre, dist=2 → SDF=-2
            [2.0, 0.0, 0.0],  # on boundary
            [3.0, 0.0, 1.0],  # outside, dist=1
        ],
        zero_isoline_desc="circle r=2",
    ),
    dict(
        name="sdf_ellipse_a3b1",
        field_type="SignedDistanceField",
        region_spec={"type": "ellipse", "expr": "x**2/9+y**2-1", "a": 3, "b": 1},
        description="SignedDistanceField of ellipse a=3,b=1",
        eval_samples=[
            [0.0, 0.0, None],  # negative (inside), exact value depends on impl
            [3.0, 0.0, 0.0],  # on boundary (approx)
        ],
        zero_isoline_desc="ellipse boundary",
    ),
    dict(
        name="occupancy_circle_r2",
        field_type="OccupancyField",
        region_spec={"type": "circle", "expr": "x**2+y**2-4", "cx": 0, "cy": 0, "r": 2},
        inside_value=1.0,
        outside_value=0.0,
        description="OccupancyField of disk r=2",
        eval_samples=[
            [0.0, 0.0, 1.0],  # inside
            [3.0, 0.0, 0.0],  # outside
            [2.0, 0.0, 0.0],  # on boundary → outside by containment
        ],
        zero_isoline_desc="N/A",
    ),
    dict(
        name="occupancy_ellipse_a2b1",
        field_type="OccupancyField",
        region_spec={"type": "ellipse", "expr": "x**2/4+y**2-1", "a": 2, "b": 1},
        inside_value=1.0,
        outside_value=0.0,
        description="OccupancyField of ellipse a=2,b=1",
        eval_samples=[
            [0.0, 0.0, 1.0],
            [3.0, 0.0, 0.0],
        ],
        zero_isoline_desc="N/A",
    ),
    dict(
        name="blendedfield_average",
        field_type="BlendedField",
        operation="average",
        fields_spec=[
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-4"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-1"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2/9+y**2-1"},
            },
        ],
        description="BlendedField average of 3 curve fields",
        eval_samples=[
            [0.0, 0.0, (-4.0 + -1.0 + -1.0) / 3],
        ],
        zero_isoline_desc="average zero contour",
    ),
    dict(
        name="blendedfield_subtract",
        field_type="BlendedField",
        operation="subtract",
        fields_spec=[
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-4"},
            },
            {
                "type": "CurveField",
                "curve": {"type": "ConicSection", "expr": "x**2+y**2-1"},
            },
        ],
        description="BlendedField subtract: circle(r=2) - circle(r=1)",
        eval_samples=[
            [0.0, 0.0, -3.0],  # -4-(-1)=-3
        ],
        zero_isoline_desc="difference zero contour",
    ),
]


# ── main ──────────────────────────────────────────────────────────────────────


def create_schema(cursor):
    cursor.execute("DROP TABLE IF EXISTS new_curve_types")
    cursor.execute("""
        CREATE TABLE new_curve_types (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            curve_class TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            description TEXT,
            params_json TEXT    NOT NULL,
            sample_points_json      TEXT,
            analytical_intersections_json TEXT,
            eval_samples_json       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)


def seed_parametric(cursor):
    for cfg in PARAMETRIC_CURVES:
        pts = _sample_parametric(cfg["x_fn"], cfg["y_fn"], cfg["t_start"], cfg["t_end"])
        params = {
            "x_expr": cfg["x_expr"],
            "y_expr": cfg["y_expr"],
            "t_start": cfg["t_start"],
            "t_end": cfg["t_end"],
            "paired_curve": cfg["paired_curve"],
        }
        cursor.execute(
            """
            INSERT INTO new_curve_types (curve_class, name, description, params_json,
                                        sample_points_json, analytical_intersections_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                "ParametricSegment",
                cfg["name"],
                cfg["description"],
                json.dumps(params),
                json.dumps(pts),
                json.dumps(cfg["analytical_intersections"]),
            ),
        )


def seed_superellipses(cursor):
    for cfg in SUPERELLIPSES:
        samples = _sample_superellipse(cfg["a"], cfg["b"], cfg["n"])
        # Compute analytical intersections with the unit circle r=1
        intersections = _superellipse_intersects_circle(
            cfg["a"], cfg["b"], cfg["n"], 1.0
        )
        params = {"a": cfg["a"], "b": cfg["b"], "n": cfg["n"]}
        cursor.execute(
            """
            INSERT INTO new_curve_types (curve_class, name, description, params_json,
                                        eval_samples_json, analytical_intersections_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                "Superellipse",
                f"superellipse_a{cfg['a']}_b{cfg['b']}_n{cfg['n']}",
                cfg["desc"],
                json.dumps(params),
                json.dumps(samples),
                json.dumps(intersections),
            ),
        )


def seed_rfunction(cursor):
    for row in _build_rfunction_rows():
        params = {
            "operation": row["operation"],
            "alpha": row["alpha"],
            "curve1": row["curve1_spec"],
            "curve2": row["curve2_spec"],
        }
        cursor.execute(
            """
            INSERT INTO new_curve_types (curve_class, name, description, params_json)
            VALUES (?, ?, ?, ?)
        """,
            (
                "RFunctionCurve",
                f"rfunction_{row['operation']}_{len([r for r in cursor.execute('SELECT id FROM new_curve_types WHERE curve_class=?', ('RFunctionCurve',)).fetchall()])}",
                row["description"],
                json.dumps(params),
            ),
        )


def seed_procedural(cursor):
    for cfg in PROCEDURAL_CURVES:
        params = {
            "function_desc": cfg["function_desc"],
            "is_periodic": cfg["is_periodic"],
            "domain": cfg["domain"],
            "paired_curve": cfg["paired_curve"],
        }
        cursor.execute(
            """
            INSERT INTO new_curve_types (curve_class, name, description, params_json,
                                        eval_samples_json, analytical_intersections_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                "ProceduralCurve",
                cfg["name"],
                cfg["function_desc"],
                json.dumps(params),
                json.dumps(cfg["eval_samples"]),
                json.dumps(cfg["analytical_intersections"]),
            ),
        )


def seed_fields(cursor):
    for cfg in FIELD_ENTRIES:
        params = {
            k: v
            for k, v in cfg.items()
            if k not in ("name", "description", "eval_samples")
        }
        cursor.execute(
            """
            INSERT INTO new_curve_types (curve_class, name, description, params_json,
                                        eval_samples_json)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                cfg["field_type"],
                cfg["name"],
                cfg["description"],
                json.dumps(params),
                json.dumps(cfg.get("eval_samples", [])),
            ),
        )


def main():
    print(f"Opening database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating schema …")
    create_schema(cursor)

    print(f"Seeding {len(PARAMETRIC_CURVES)} ParametricSegment rows …")
    seed_parametric(cursor)

    print(f"Seeding {len(SUPERELLIPSES)} Superellipse rows …")
    seed_superellipses(cursor)

    rfunc_rows = _build_rfunction_rows()
    print(f"Seeding {len(rfunc_rows)} RFunctionCurve rows …")
    seed_rfunction(cursor)

    print(f"Seeding {len(PROCEDURAL_CURVES)} ProceduralCurve rows …")
    seed_procedural(cursor)

    print(f"Seeding {len(FIELD_ENTRIES)} Field rows …")
    seed_fields(cursor)

    conn.commit()
    conn.close()

    # Report counts
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for cls in [
        "ParametricSegment",
        "Superellipse",
        "RFunctionCurve",
        "ProceduralCurve",
        "CurveField",
        "BlendedField",
        "SignedDistanceField",
        "OccupancyField",
    ]:
        count = c.execute(
            "SELECT COUNT(*) FROM new_curve_types WHERE curve_class=?", (cls,)
        ).fetchone()[0]
        print(f"  {cls}: {count} rows")
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
