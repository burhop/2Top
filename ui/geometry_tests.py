from __future__ import annotations

"""Predefined geometry scenarios for the Geometry Test Studio.

Tests are organised into categories:
  - basics        : simple single-curve sanity checks
  - intersection  : curve-curve intersection cases
  - tangency      : near-tangent / tangent cases (degenerate intersections)
  - degenerate    : mathematically tricky edge cases
  - composite     : multi-segment / composite curves
  - mixed         : combinations of different curve families
"""

import sympy as sp
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

from geometry import ImplicitCurve, ConicSection
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import CurveFactory, RegionFactory


@dataclass(frozen=True)
class GeometryTestDefinition:
    """Metadata + builder callback for a geometry test scene."""

    id: str
    name: str
    description: str
    tags: Sequence[str]
    builder: Callable[[SceneManager, CurveFactory, RegionFactory], List[str]]


# Palette tuned for high contrast on dark backgrounds
C = [
    "#46c2ff",  # 0 blue
    "#ff6b9c",  # 1 pink
    "#ffb347",  # 2 orange
    "#7bed8d",  # 3 green
    "#c792ea",  # 4 purple
    "#f9f871",  # 5 yellow
]

_x, _y = sp.symbols("x y")


def _add(sm, oid, obj, color, lw=2.5):
    sm.add_object(oid, obj, {"color": color, "linewidth": lw, "alpha": 1.0})
    return oid


def _circle(cx, cy, r):
    return ConicSection((_x - cx)**2 + (_y - cy)**2 - r**2, (_x, _y))


def _ellipse(cx, cy, a, b):
    return ConicSection((_x - cx)**2 / a**2 + (_y - cy)**2 / b**2 - 1, (_x, _y))


def _line_implicit(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return ImplicitCurve(dy * (_x - x1) - dx * (_y - y1), (_x, _y))


def _parabola(vx, vy, scale=1.0, direction="up"):
    if direction == "up":
        expr = (_y - vy) - scale * (_x - vx)**2
    elif direction == "down":
        expr = (_y - vy) + scale * (_x - vx)**2
    elif direction == "right":
        expr = (_x - vx) - scale * (_y - vy)**2
    else:
        expr = (_x - vx) + scale * (_y - vy)**2
    return ImplicitCurve(expr, (_x, _y))


def _hyperbola(cx, cy, a, b):
    return ImplicitCurve((_x - cx)**2 / a**2 - (_y - cy)**2 / b**2 - 1, (_x, _y))


def _implicit(expr_str):
    return ImplicitCurve(sp.sympify(expr_str), (_x, _y))


# ── Batch 1: Circle family ────────────────────────────────────────────────────

def _b_circle_line_2pt(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2.8), C[0]),
            _add(sm, "l", _line_implicit(-4, 1.25, 3.5, -1.4), C[1])]

def _b_circle_line_tangent(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "l", _line_implicit(-3, 2, 3, 2), C[1])]

def _b_circle_line_miss(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 1.5), C[0]),
            _add(sm, "l", _line_implicit(-3, 2, 3, 2), C[1])]

def _b_circle_line_through_center(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2.5), C[0]),
            _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1])]

def _b_circle_line_vertical(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1])]

def _b_circle_line_vertical_tangent(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "l", _line_implicit(2, -3, 2, 3), C[1])]

def _b_two_circles_2pt(sm, cf, rf):
    return [_add(sm, "c1", _circle(-1, 0, 2), C[0]),
            _add(sm, "c2", _circle(1, 0, 2), C[1])]

def _b_two_circles_tangent_ext(sm, cf, rf):
    return [_add(sm, "c1", _circle(-2, 0, 2), C[0]),
            _add(sm, "c2", _circle(2, 0, 2), C[1])]

def _b_two_circles_tangent_int(sm, cf, rf):
    return [_add(sm, "c1", _circle(0, 0, 3), C[0]),
            _add(sm, "c2", _circle(1, 0, 2), C[1])]

def _b_two_circles_concentric(sm, cf, rf):
    return [_add(sm, "c1", _circle(0, 0, 3), C[0]),
            _add(sm, "c2", _circle(0, 0, 1.5), C[1])]

def _b_two_circles_miss(sm, cf, rf):
    return [_add(sm, "c1", _circle(-3, 0, 1), C[0]),
            _add(sm, "c2", _circle(3, 0, 1), C[1])]

def _b_three_circles(sm, cf, rf):
    return [_add(sm, "c1", _circle(0, 0, 2), C[0]),
            _add(sm, "c2", _circle(2, 1, 1.5), C[1]),
            _add(sm, "c3", _circle(-2, 1, 1.5), C[2])]

def _b_circle_ellipse_2pt(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "e", _ellipse(1, 0, 3, 1.5), C[1])]

def _b_circle_ellipse_4pt(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "e", _ellipse(0, 0, 3, 1.2), C[2])]

def _b_circle_ellipse_tangent(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 1), C[0]),
            _add(sm, "e", _ellipse(0, 0, 2, 1), C[1])]

def _b_circle_parabola(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 1, 2), C[0]),
            _add(sm, "p", _parabola(0, -1, 0.4), C[1])]

def _b_circle_hyperbola(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2.5), C[0]),
            _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[1])]

def _b_circle_cubic(sm, cf, rf):
    return [_add(sm, "c",  _circle(0, 0, 1.5), C[0]),
            _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1])]

def _b_circle_tangent_to_line_at_origin(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 1, 1), C[0]),
            _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1])]

def _b_three_circles_common_chord(sm, cf, rf):
    return [_add(sm, "c1", _circle(-1, 0, 2), C[0]),
            _add(sm, "c2", _circle(1, 0, 2), C[1]),
            _add(sm, "l",  _line_implicit(0, -3, 0, 3), C[5])]

def _b_circle_vs_circle_line(sm, cf, rf):
    return [_add(sm, "c1", _circle(-1, 0, 2), C[0]),
            _add(sm, "c2", _circle(1, 0, 2), C[1]),
            _add(sm, "l",  _line_implicit(-3, 0, 3, 0), C[5])]

def _b_unit_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 1), C[0])]

def _b_large_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 5), C[0])]

def _b_tiny_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 0.1), C[0])]


# ── Batch 2: Ellipse family ───────────────────────────────────────────────────

def _b_dual_ellipses(sm, cf, rf):
    return [_add(sm, "e1", _ellipse(-1.5, 0, 3.5, 1.25), C[0]),
            _add(sm, "e2", _ellipse(1.25, 0.6, 2.5, 1.75), C[2])]

def _b_ellipse_line_2pt(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
            _add(sm, "l", _line_implicit(-4, 0.5, 4, 0.5), C[1])]

def _b_ellipse_line_tangent(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
            _add(sm, "l", _line_implicit(-4, 1.5, 4, 1.5), C[1])]

def _b_ellipse_line_vertical(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 2, 1), C[0]),
            _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1])]

def _b_ellipse_diagonal_line(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 2.5, 1.5), C[0]),
            _add(sm, "l", _line_implicit(-3, -2, 3, 2), C[1])]

def _b_ellipse_parabola(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 1.5, 2.5, 1.5), C[0]),
            _add(sm, "p", _parabola(0, 0, 0.3), C[2])]

def _b_ellipse_hyperbola(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 2), C[0]),
            _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[1])]

def _b_ellipse_cubic(sm, cf, rf):
    return [_add(sm, "e",  _ellipse(0, 0, 2, 1.5), C[0]),
            _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1])]

def _b_wide_ellipse_alone(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 4, 1), C[0])]

def _b_tall_ellipse_alone(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 1, 4), C[0])]

def _b_near_circle_ellipse(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 2.0, 1.95), C[0])]

def _b_three_ellipses(sm, cf, rf):
    return [_add(sm, "e1", _ellipse(-2, 0, 2, 1), C[0]),
            _add(sm, "e2", _ellipse(2, 0, 2, 1), C[1]),
            _add(sm, "e3", _ellipse(0, 0, 3, 0.8), C[2])]


# ── Batch 3: Parabola family ──────────────────────────────────────────────────

def _b_parabola_line_2pt(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.5), C[0]),
            _add(sm, "l", _line_implicit(-3, 1, 3, 1), C[1])]

def _b_parabola_line_tangent(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 1.0), C[0]),
            _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1])]

def _b_parabola_line_miss(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.5), C[0]),
            _add(sm, "l", _line_implicit(-3, -1, 3, -1), C[1])]

def _b_parabola_line_vertical(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.5), C[0]),
            _add(sm, "l", _line_implicit(1, -1, 1, 4), C[1])]

def _b_parabola_line_diagonal(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.5), C[0]),
            _add(sm, "l", _line_implicit(-3, -2, 3, 2), C[1])]

def _b_two_parabolas_same_axis(sm, cf, rf):
    return [_add(sm, "p1", _parabola(0, -1.5, 0.4, "up"), C[0]),
            _add(sm, "p2", _parabola(0, 1.25, 0.35, "down"), C[2])]

def _b_two_parabolas_cross(sm, cf, rf):
    return [_add(sm, "p1", _parabola(0, 0, 0.5, "up"), C[0]),
            _add(sm, "p2", _parabola(0, 0, 0.5, "right"), C[1])]

def _b_parabola_bundle(sm, cf, rf):
    return [_add(sm, "p1", _parabola(0, -1.5, 0.4, "up"), C[0]),
            _add(sm, "p2", _parabola(0, 1.25, 0.35, "down"), C[2]),
            _add(sm, "l",  _line_implicit(-3.5, -2.5, 3.5, 2.5), C[1])]

def _b_parabola_offset_vertex(sm, cf, rf):
    return [_add(sm, "p1", _parabola(-2, 0, 0.5, "up"), C[0]),
            _add(sm, "p2", _parabola(2, 0, 0.5, "up"), C[1])]

def _b_parabola_horizontal(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.5, "right"), C[0]),
            _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1])]


# ── Batch 4: Hyperbola family ─────────────────────────────────────────────────

def _b_hyperbola_line_2pt(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "l", _line_implicit(-4, 0.5, 4, 0.5), C[1])]

def _b_hyperbola_line_asymptote(sm, cf, rf):
    a, b = 1.5, 1.0
    return [_add(sm, "h", _hyperbola(0, 0, a, b), C[0]),
            _add(sm, "l", _line_implicit(-4, -4*b/a, 4, 4*b/a), C[1])]

def _b_hyperbola_line_vertical(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "l", _line_implicit(2, -4, 2, 4), C[1])]

def _b_hyperbola_circle(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "c", _circle(0, 0, 2.5), C[1])]

def _b_hyperbola_ellipse(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "e", _ellipse(0, 0, 3, 2), C[2])]

def _b_hyperbola_parabola(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "p", _parabola(0, -1, 0.4), C[1])]

def _b_two_hyperbolas_conjugate(sm, cf, rf):
    return [_add(sm, "h1", _hyperbola(0, 0, 1.5, 1), C[0]),
            _add(sm, "h2", ImplicitCurve(_y**2/1.0 - _x**2/2.25 - 1, (_x, _y)), C[1])]

def _b_hyperbola_alone(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 2, 1.5), C[0])]


# ── Batch 5: Cubic & special curves ──────────────────────────────────────────

def _b_cubic_x_axis(sm, cf, rf):
    return [_add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
            _add(sm, "l",  _line_implicit(-2.5, 0, 2.5, 0), C[4])]

def _b_cubic_guides(sm, cf, rf):
    return [_add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
            _add(sm, "lx", _line_implicit(-2.5, 0, 2.5, 0), C[4]),
            _add(sm, "ly", _line_implicit(0, -3, 0, 3), C[5])]

def _b_cubic_line_3pt(sm, cf, rf):
    return [_add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
            _add(sm, "l",  _line_implicit(-2, 0.5, 2, 0.5), C[4])]

def _b_folium_line(sm, cf, rf):
    return [_add(sm, "f", _implicit("x**3 + y**3 - 3*x*y"), C[3]),
            _add(sm, "l", _line_implicit(-2, -2, 2, 2), C[1])]

def _b_folium_circle(sm, cf, rf):
    return [_add(sm, "f", _implicit("x**3 + y**3 - 3*x*y"), C[3]),
            _add(sm, "c", _circle(1, 1, 1), C[0])]

def _b_lemniscate_circle(sm, cf, rf):
    return [_add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
            _add(sm, "c",   _circle(0, 0, 1), C[0])]

def _b_lemniscate_line(sm, cf, rf):
    return [_add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
            _add(sm, "l",   _line_implicit(-2, 0.5, 2, 0.5), C[1])]

def _b_lemniscate_ellipse(sm, cf, rf):
    return [_add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
            _add(sm, "e",   _ellipse(0, 0, 1.5, 0.8), C[2])]

def _b_cassini_circle(sm, cf, rf):
    return [_add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
            _add(sm, "c",   _circle(0, 0, 1.5), C[0])]

def _b_cassini_line(sm, cf, rf):
    return [_add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
            _add(sm, "l",   _line_implicit(-3, 0.5, 3, 0.5), C[1])]

def _b_cardioid_circle(sm, cf, rf):
    return [_add(sm, "card", _implicit("(x**2+y**2-x)**2 - (x**2+y**2)"), C[1]),
            _add(sm, "c",    _circle(0.5, 0, 0.5), C[0])]

def _b_cardioid_line(sm, cf, rf):
    return [_add(sm, "card", _implicit("(x**2+y**2-x)**2 - (x**2+y**2)"), C[1]),
            _add(sm, "l",    _line_implicit(-2, 0.5, 2, 0.5), C[4])]


# ── Batch 6: Line combinations & degenerate ───────────────────────────────────

def _b_three_lines_concurrent(sm, cf, rf):
    return [_add(sm, "l1", _line_implicit(-3, -2, 3, 2), C[0]),
            _add(sm, "l2", _line_implicit(-3, 2, 3, -2), C[1]),
            _add(sm, "l3", _line_implicit(-3, 0, 3, 0), C[2])]

def _b_four_lines_grid(sm, cf, rf):
    return [_add(sm, "l1", _line_implicit(-3, -1, 3, -1), C[0]),
            _add(sm, "l2", _line_implicit(-3, 1, 3, 1), C[1]),
            _add(sm, "l3", _line_implicit(-1, -3, -1, 3), C[2]),
            _add(sm, "l4", _line_implicit(1, -3, 1, 3), C[3])]

def _b_parallel_lines(sm, cf, rf):
    return [_add(sm, "l1", _line_implicit(-3, -1, 3, -1), C[0]),
            _add(sm, "l2", _line_implicit(-3, 1, 3, 1), C[1])]

def _b_coincident_lines(sm, cf, rf):
    return [_add(sm, "l1", _line_implicit(-3, 0, 3, 0), C[0]),
            _add(sm, "l2", _line_implicit(-2, 0, 2, 0), C[1])]

def _b_star_of_lines(sm, cf, rf):
    import math
    ids = []
    for i in range(5):
        angle = math.pi * i / 5
        dx, dy = math.cos(angle)*3, math.sin(angle)*3
        ids.append(_add(sm, f"l{i}", _line_implicit(-dx, -dy, dx, dy), C[i % 6]))
    return ids

def _b_composite_quarters(sm, cf, rf):
    return [_add(sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]),
            _add(sm, "l",  _line_implicit(-4, 0, 4, 0), C[0])]

def _b_composite_quarters_diagonal(sm, cf, rf):
    return [_add(sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]),
            _add(sm, "l",  _line_implicit(-3, -3, 3, 3), C[1])]

def _b_composite_quarters_circle(sm, cf, rf):
    return [_add(sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]),
            _add(sm, "c",  _circle(0, 0, 2), C[0])]


# ── Batch 7: Mixed / stress tests ────────────────────────────────────────────

def _b_conic_zoo(sm, cf, rf):
    return [_add(sm, "c",  _circle(0, 0, 2), C[0]),
            _add(sm, "e",  _ellipse(0, 0, 3, 1.2), C[1]),
            _add(sm, "p",  _parabola(0, -2, 0.3), C[2]),
            _add(sm, "h",  _hyperbola(0, 0, 1.5, 1), C[4])]

def _b_circle_ellipse_parabola(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "e", _ellipse(0, 0, 3, 1.5), C[1]),
            _add(sm, "p", _parabola(0, -1, 0.4), C[2])]

def _b_two_circles_parabola(sm, cf, rf):
    return [_add(sm, "c1", _circle(-1.5, 0, 1.5), C[0]),
            _add(sm, "c2", _circle(1.5, 0, 1.5), C[1]),
            _add(sm, "p",  _parabola(0, -2, 0.3), C[2])]

def _b_ellipse_two_lines(sm, cf, rf):
    return [_add(sm, "e",  _ellipse(0, 0, 2.5, 1.5), C[0]),
            _add(sm, "l1", _line_implicit(-3, -1, 3, 1), C[1]),
            _add(sm, "l2", _line_implicit(-3, 1, 3, -1), C[2])]

def _b_parabola_two_circles(sm, cf, rf):
    return [_add(sm, "p",  _parabola(0, 0, 0.4), C[0]),
            _add(sm, "c1", _circle(-1.5, 1.5, 1), C[1]),
            _add(sm, "c2", _circle(1.5, 1.5, 1), C[2])]

def _b_hyperbola_two_lines(sm, cf, rf):
    a, b = 1.5, 1.0
    return [_add(sm, "h",  _hyperbola(0, 0, a, b), C[0]),
            _add(sm, "l1", _line_implicit(-4, -4*b/a, 4, 4*b/a), C[5]),
            _add(sm, "l2", _line_implicit(-4, 4*b/a, 4, -4*b/a), C[4])]

def _b_cubic_circle_line(sm, cf, rf):
    return [_add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
            _add(sm, "c",  _circle(0, 0, 1.5), C[0]),
            _add(sm, "l",  _line_implicit(-2, 0.5, 2, 0.5), C[4])]

def _b_near_tangent_circles(sm, cf, rf):
    return [_add(sm, "c1", _circle(-2.05, 0, 2), C[0]),
            _add(sm, "c2", _circle(2.05, 0, 2), C[1])]

def _b_near_tangent_circle_line(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 2), C[0]),
            _add(sm, "l", _line_implicit(-3, 1.99, 3, 1.99), C[1])]

def _b_near_tangent_ellipse_line(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
            _add(sm, "l", _line_implicit(-4, 1.49, 4, 1.49), C[1])]

def _b_very_flat_ellipse(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 0.2), C[0]),
            _add(sm, "l", _line_implicit(-4, 0.1, 4, 0.1), C[1])]

def _b_very_narrow_hyperbola(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 0.2, 2), C[0]),
            _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1])]

def _b_steep_parabola(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 3.0), C[0]),
            _add(sm, "l", _line_implicit(-2, 1, 2, 1), C[1])]

def _b_shallow_parabola(sm, cf, rf):
    return [_add(sm, "p", _parabola(0, 0, 0.05), C[0]),
            _add(sm, "l", _line_implicit(-5, 1, 5, 1), C[1])]

def _b_offset_cubic(sm, cf, rf):
    return [_add(sm, "cu", _implicit("(y-1)**2 - (x-1)**3 + (x-1)"), C[1]),
            _add(sm, "c",  _circle(1, 1, 1.5), C[0])]

def _b_circle_inside_ellipse(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 3, 2), C[0]),
            _add(sm, "c", _circle(0, 0, 1), C[1])]

def _b_ellipse_inside_circle(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 3), C[0]),
            _add(sm, "e", _ellipse(0, 0, 2, 1), C[1])]

def _b_four_conics(sm, cf, rf):
    return [_add(sm, "c",  _circle(0, 0, 2), C[0]),
            _add(sm, "e",  _ellipse(0, 0, 3, 1), C[1]),
            _add(sm, "p",  _parabola(0, -2, 0.25), C[2]),
            _add(sm, "l",  _line_implicit(-4, 0, 4, 0), C[5])]

def _b_lemniscate_parabola(sm, cf, rf):
    return [_add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
            _add(sm, "p",   _parabola(0, 0, 0.5), C[1])]

def _b_cassini_parabola(sm, cf, rf):
    return [_add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
            _add(sm, "p",   _parabola(0, -1, 0.3), C[0])]


def _T(tid, name, desc, tags, builder):
    return tid, GeometryTestDefinition(id=tid, name=name, description=desc, tags=tags, builder=builder)


GEOMETRY_TESTS: Dict[str, GeometryTestDefinition] = dict([
    # ── Circle family ──────────────────────────────────────────────────────────
    _T("circle_line_2pt",          "Circle × Line (2pt)",          "Circle cut by a slanted line at two points.",                    ("circle","line","intersection"),    _b_circle_line_2pt),
    _T("circle_line_tangent",      "Circle × Line (tangent)",      "Horizontal line tangent to top of circle.",                      ("circle","line","tangency"),         _b_circle_line_tangent),
    _T("circle_line_miss",         "Circle × Line (miss)",         "Line passes above circle — no intersection.",                    ("circle","line","degenerate"),       _b_circle_line_miss),
    _T("circle_line_center",       "Circle × Line (diameter)",     "Line passes through circle center.",                             ("circle","line","intersection"),    _b_circle_line_through_center),
    _T("circle_line_vertical",     "Circle × Vertical Line",       "Vertical chord through circle.",                                 ("circle","line","intersection"),    _b_circle_line_vertical),
    _T("circle_line_vtangent",     "Circle × Vertical Tangent",    "Vertical line tangent to circle.",                               ("circle","line","tangency"),         _b_circle_line_vertical_tangent),
    _T("circle_tangent_origin",    "Circle Tangent at Origin",     "Circle tangent to x-axis at the origin.",                       ("circle","line","tangency"),         _b_circle_tangent_to_line_at_origin),
    _T("two_circles_2pt",          "Two Circles (2pt)",            "Two equal circles overlapping at two points.",                   ("circle","intersection"),           _b_two_circles_2pt),
    _T("two_circles_tangent_ext",  "Two Circles (ext tangent)",    "Two circles touching externally at one point.",                  ("circle","tangency"),                _b_two_circles_tangent_ext),
    _T("two_circles_tangent_int",  "Two Circles (int tangent)",    "Smaller circle internally tangent to larger.",                   ("circle","tangency"),                _b_two_circles_tangent_int),
    _T("two_circles_concentric",   "Concentric Circles",           "Two circles sharing the same centre.",                          ("circle","degenerate"),              _b_two_circles_concentric),
    _T("two_circles_miss",         "Two Circles (miss)",           "Two circles far apart — no intersection.",                      ("circle","degenerate"),              _b_two_circles_miss),
    _T("three_circles",            "Three Circles",                "Three circles with pairwise intersections.",                    ("circle","intersection"),           _b_three_circles),
    _T("three_circles_chord",      "Three Circles + Chord",        "Two intersecting circles with their radical axis.",             ("circle","line","intersection"),    _b_three_circles_common_chord),
    _T("circle_vs_circle_line",    "2 Circles + Line",             "Two circles and a line through their intersection.",            ("circle","line","intersection"),    _b_circle_vs_circle_line),
    _T("unit_circle",              "Unit Circle",                  "Single unit circle — basic rendering check.",                   ("circle","basics"),                  _b_unit_circle_alone),
    _T("large_circle",             "Large Circle (r=5)",           "Large circle — tests viewport fitting.",                        ("circle","basics"),                  _b_large_circle_alone),
    _T("tiny_circle",              "Tiny Circle (r=0.1)",          "Very small circle — tests resolution at small scale.",          ("circle","basics","degenerate"),     _b_tiny_circle_alone),
    # ── Circle × conic ────────────────────────────────────────────────────────
    _T("circle_ellipse_2pt",       "Circle × Ellipse (2pt)",       "Circle and ellipse intersecting at two points.",                ("circle","ellipse","intersection"),  _b_circle_ellipse_2pt),
    _T("circle_ellipse_4pt",       "Circle × Ellipse (4pt)",       "Concentric circle and ellipse crossing at four points.",       ("circle","ellipse","intersection"),  _b_circle_ellipse_4pt),
    _T("circle_ellipse_tangent",   "Circle × Ellipse (tangent)",   "Circle internally tangent to ellipse.",                        ("circle","ellipse","tangency"),       _b_circle_ellipse_tangent),
    _T("circle_parabola",          "Circle × Parabola",            "Circle intersecting an upward parabola.",                      ("circle","parabola","intersection"),  _b_circle_parabola),
    _T("circle_hyperbola",         "Circle × Hyperbola",           "Circle surrounding a hyperbola.",                              ("circle","hyperbola","intersection"), _b_circle_hyperbola),
    _T("circle_cubic",             "Circle × Cubic",               "Circle crossing an elliptic cubic curve.",                     ("circle","cubic","intersection"),     _b_circle_cubic),
    # ── Ellipse family ────────────────────────────────────────────────────────
    _T("dual_ellipses",            "Dual Ellipses",                "Two offset ellipses with multiple intersection points.",        ("ellipse","intersection"),           _b_dual_ellipses),
    _T("ellipse_line_2pt",         "Ellipse × Line (2pt)",         "Horizontal line cutting ellipse at two points.",               ("ellipse","line","intersection"),    _b_ellipse_line_2pt),
    _T("ellipse_line_tangent",     "Ellipse × Line (tangent)",     "Horizontal line tangent to top of ellipse.",                   ("ellipse","line","tangency"),         _b_ellipse_line_tangent),
    _T("ellipse_line_vertical",    "Ellipse × Vertical Line",      "Vertical chord through ellipse.",                              ("ellipse","line","intersection"),    _b_ellipse_line_vertical),
    _T("ellipse_line_diagonal",    "Ellipse × Diagonal Line",      "Diagonal line cutting ellipse.",                               ("ellipse","line","intersection"),    _b_ellipse_diagonal_line),
    _T("ellipse_parabola",         "Ellipse × Parabola",           "Ellipse and upward parabola intersecting.",                    ("ellipse","parabola","intersection"), _b_ellipse_parabola),
    _T("ellipse_hyperbola",        "Ellipse × Hyperbola",          "Ellipse surrounding a hyperbola.",                             ("ellipse","hyperbola","intersection"), _b_ellipse_hyperbola),
    _T("ellipse_cubic",            "Ellipse × Cubic",              "Ellipse crossing an elliptic cubic.",                          ("ellipse","cubic","intersection"),    _b_ellipse_cubic),
    _T("wide_ellipse",             "Wide Ellipse (a=4,b=1)",       "Very wide ellipse — aspect ratio stress test.",                 ("ellipse","basics"),                  _b_wide_ellipse_alone),
    _T("tall_ellipse",             "Tall Ellipse (a=1,b=4)",       "Very tall ellipse — aspect ratio stress test.",                 ("ellipse","basics"),                  _b_tall_ellipse_alone),
    _T("near_circle_ellipse",      "Near-Circle Ellipse",          "Ellipse with a≈b — nearly circular.",                         ("ellipse","basics","degenerate"),     _b_near_circle_ellipse),
    _T("three_ellipses",           "Three Ellipses",               "Three ellipses with overlapping regions.",                     ("ellipse","intersection"),           _b_three_ellipses),
    _T("circle_inside_ellipse",    "Circle Inside Ellipse",        "Circle fully inside ellipse — no intersection.",               ("circle","ellipse","degenerate"),     _b_circle_inside_ellipse),
    _T("ellipse_inside_circle",    "Ellipse Inside Circle",        "Ellipse fully inside circle — no intersection.",               ("circle","ellipse","degenerate"),     _b_ellipse_inside_circle),
    # ── Parabola family ───────────────────────────────────────────────────────
    _T("parabola_line_2pt",        "Parabola × Line (2pt)",        "Horizontal line cutting parabola at two points.",              ("parabola","line","intersection"),   _b_parabola_line_2pt),
    _T("parabola_line_tangent",    "Parabola × Line (tangent)",    "Horizontal line tangent to parabola vertex.",                  ("parabola","line","tangency"),        _b_parabola_line_tangent),
    _T("parabola_line_miss",       "Parabola × Line (miss)",       "Line below parabola — no intersection.",                       ("parabola","line","degenerate"),      _b_parabola_line_miss),
    _T("parabola_line_vertical",   "Parabola × Vertical Line",     "Vertical line crossing parabola once.",                        ("parabola","line","intersection"),   _b_parabola_line_vertical),
    _T("parabola_line_diagonal",   "Parabola × Diagonal Line",     "Diagonal secant through parabola.",                            ("parabola","line","intersection"),   _b_parabola_line_diagonal),
    _T("two_parabolas_axis",       "Two Parabolas (same axis)",    "Opposing parabolas on the same axis.",                         ("parabola","intersection"),          _b_two_parabolas_same_axis),
    _T("two_parabolas_cross",      "Two Parabolas (cross)",        "Up-parabola and right-parabola crossing.",                     ("parabola","intersection"),          _b_two_parabolas_cross),
    _T("parabola_bundle",          "Parabola Bundle",              "Two opposing parabolas and a diagonal line.",                  ("parabola","line","intersection"),   _b_parabola_bundle),
    _T("parabola_offset_vertex",   "Two Parabolas (offset)",       "Two upward parabolas with offset vertices.",                   ("parabola","intersection"),          _b_parabola_offset_vertex),
    _T("parabola_horizontal",      "Horizontal Parabola",          "Right-opening parabola with vertical line.",                   ("parabola","line","intersection"),   _b_parabola_horizontal),
    _T("steep_parabola",           "Steep Parabola (scale=3)",     "Very steep parabola — tests narrow contour extraction.",       ("parabola","basics","degenerate"),   _b_steep_parabola),
    _T("shallow_parabola",         "Shallow Parabola (scale=0.05)","Very shallow parabola — nearly flat.",                         ("parabola","basics","degenerate"),   _b_shallow_parabola),
    # ── Hyperbola family ──────────────────────────────────────────────────────
    _T("hyperbola_line_2pt",       "Hyperbola × Line (2pt)",       "Horizontal line cutting one branch of hyperbola.",             ("hyperbola","line","intersection"),  _b_hyperbola_line_2pt),
    _T("hyperbola_line_asymptote", "Hyperbola × Asymptote",        "Line along the asymptote direction.",                          ("hyperbola","line","degenerate"),    _b_hyperbola_line_asymptote),
    _T("hyperbola_line_vertical",  "Hyperbola × Vertical Line",    "Vertical line cutting one branch.",                            ("hyperbola","line","intersection"),  _b_hyperbola_line_vertical),
    _T("hyperbola_circle",         "Hyperbola × Circle",           "Circle surrounding both branches of hyperbola.",               ("hyperbola","circle","intersection"), _b_hyperbola_circle),
    _T("hyperbola_ellipse",        "Hyperbola × Ellipse",          "Ellipse enclosing a hyperbola.",                               ("hyperbola","ellipse","intersection"), _b_hyperbola_ellipse),
    _T("hyperbola_parabola",       "Hyperbola × Parabola",         "Hyperbola and parabola crossing.",                             ("hyperbola","parabola","intersection"), _b_hyperbola_parabola),
    _T("two_hyperbolas_conjugate", "Conjugate Hyperbolas",         "A hyperbola and its conjugate.",                               ("hyperbola","degenerate"),           _b_two_hyperbolas_conjugate),
    _T("hyperbola_alone",          "Hyperbola Alone",              "Single hyperbola — basic rendering check.",                    ("hyperbola","basics"),               _b_hyperbola_alone),
    _T("very_narrow_hyperbola",    "Narrow Hyperbola",             "Hyperbola with very small a — nearly vertical branches.",      ("hyperbola","basics","degenerate"),  _b_very_narrow_hyperbola),
    # ── Cubic & special curves ────────────────────────────────────────────────
    _T("cubic_x_axis",             "Cubic × X-axis",               "Elliptic cubic with x-axis guide.",                            ("cubic","line","intersection"),      _b_cubic_x_axis),
    _T("cubic_guides",             "Cubic with Guides",            "Cubic with orthogonal guide lines.",                           ("cubic","line","basics"),            _b_cubic_guides),
    _T("cubic_line_3pt",           "Cubic × Line (3pt)",           "Line cutting cubic at three real points.",                     ("cubic","line","intersection"),      _b_cubic_line_3pt),
    _T("cubic_circle",             "Cubic × Circle",               "Circle crossing an elliptic cubic.",                           ("cubic","circle","intersection"),    _b_circle_cubic),
    _T("cubic_ellipse",            "Cubic × Ellipse",              "Ellipse crossing an elliptic cubic.",                          ("cubic","ellipse","intersection"),   _b_ellipse_cubic),
    _T("cubic_parabola",           "Cubic × Parabola",             "Parabola crossing an elliptic cubic.",                         ("cubic","parabola","intersection"),  _b_cubic_circle_line),
    _T("folium_line",              "Folium × Line",                "Folium of Descartes with a diagonal line.",                    ("cubic","line","intersection"),      _b_folium_line),
    _T("folium_circle",            "Folium × Circle",              "Folium of Descartes with a circle.",                           ("cubic","circle","intersection"),    _b_folium_circle),
    _T("offset_cubic",             "Offset Cubic",                 "Elliptic cubic shifted from origin.",                          ("cubic","circle","basics"),          _b_offset_cubic),
    # ── Special / higher-degree curves ────────────────────────────────────────
    _T("lemniscate_circle",        "Lemniscate × Circle",          "Lemniscate of Bernoulli with a circle.",                       ("special","circle","intersection"),  _b_lemniscate_circle),
    _T("lemniscate_line",          "Lemniscate × Line",            "Lemniscate with a horizontal secant.",                         ("special","line","intersection"),    _b_lemniscate_line),
    _T("lemniscate_ellipse",       "Lemniscate × Ellipse",         "Lemniscate with an ellipse.",                                  ("special","ellipse","intersection"), _b_lemniscate_ellipse),
    _T("lemniscate_parabola",      "Lemniscate × Parabola",        "Lemniscate with a parabola.",                                  ("special","parabola","intersection"), _b_lemniscate_parabola),
    _T("cassini_circle",           "Cassini Oval × Circle",        "Cassini oval with a circle.",                                  ("special","circle","intersection"),  _b_cassini_circle),
    _T("cassini_line",             "Cassini Oval × Line",          "Cassini oval with a horizontal line.",                         ("special","line","intersection"),    _b_cassini_line),
    _T("cassini_parabola",         "Cassini Oval × Parabola",      "Cassini oval with a parabola.",                                ("special","parabola","intersection"), _b_cassini_parabola),
    _T("cardioid_circle",          "Cardioid × Circle",            "Cardioid with an inscribed circle.",                           ("special","circle","intersection"),  _b_cardioid_circle),
    _T("cardioid_line",            "Cardioid × Line",              "Cardioid with a horizontal secant.",                           ("special","line","intersection"),    _b_cardioid_line),
    # ── Line combinations & degenerate ────────────────────────────────────────
    _T("three_lines_concurrent",   "Three Concurrent Lines",       "Three lines meeting at a single point.",                       ("line","degenerate"),                _b_three_lines_concurrent),
    _T("four_lines_grid",          "Four Lines (grid)",            "Two horizontal and two vertical lines forming a grid.",        ("line","intersection"),              _b_four_lines_grid),
    _T("parallel_lines",           "Parallel Lines",               "Two parallel horizontal lines — no intersection.",             ("line","degenerate"),                _b_parallel_lines),
    _T("coincident_lines",         "Coincident Lines",             "Two segments on the same line — fully degenerate.",            ("line","degenerate"),                _b_coincident_lines),
    _T("star_of_lines",            "Star of Lines",                "Five lines through the origin forming a star.",                ("line","intersection"),              _b_star_of_lines),
    # ── Composite curves ──────────────────────────────────────────────────────
    _T("composite_quarters",       "Composite Quarters",           "Composite quarter-circles crossing a reference line.",         ("composite","circle","intersection"), _b_composite_quarters),
    _T("composite_quarters_diag",  "Composite Quarters + Diag",    "Composite quarter-circles with a diagonal line.",              ("composite","circle","intersection"), _b_composite_quarters_diagonal),
    _T("composite_quarters_circ",  "Composite Quarters + Circle",  "Composite quarter-circles with an inner circle.",              ("composite","circle","intersection"), _b_composite_quarters_circle),
    # ── Near-tangent / stress ─────────────────────────────────────────────────
    _T("near_tangent_circles",     "Near-Tangent Circles",         "Two circles almost touching externally.",                      ("circle","tangency","degenerate"),   _b_near_tangent_circles),
    _T("near_tangent_circle_line", "Near-Tangent Circle+Line",     "Line almost tangent to circle (ε gap).",                       ("circle","line","degenerate"),       _b_near_tangent_circle_line),
    _T("near_tangent_ellipse_line","Near-Tangent Ellipse+Line",    "Line almost tangent to ellipse (ε gap).",                      ("ellipse","line","degenerate"),      _b_near_tangent_ellipse_line),
    _T("very_flat_ellipse",        "Very Flat Ellipse",            "Ellipse with b=0.2 — nearly a line segment.",                  ("ellipse","line","degenerate"),      _b_very_flat_ellipse),
    # ── Mixed / multi-curve ───────────────────────────────────────────────────
    _T("conic_zoo",                "Conic Zoo",                    "Circle, ellipse, parabola and hyperbola together.",            ("mixed","intersection"),             _b_conic_zoo),
    _T("circle_ellipse_parabola",  "Circle+Ellipse+Parabola",      "Three conics with multiple intersections.",                    ("mixed","intersection"),             _b_circle_ellipse_parabola),
    _T("two_circles_parabola",     "2 Circles + Parabola",         "Two circles and a parabola.",                                  ("mixed","intersection"),             _b_two_circles_parabola),
    _T("ellipse_two_lines",        "Ellipse + 2 Lines",            "Ellipse with two crossing secants.",                           ("ellipse","line","intersection"),    _b_ellipse_two_lines),
    _T("parabola_two_circles",     "Parabola + 2 Circles",         "Parabola with two circles above it.",                          ("parabola","circle","intersection"), _b_parabola_two_circles),
    _T("hyperbola_two_lines",      "Hyperbola + Asymptotes",       "Hyperbola with both asymptote lines.",                         ("hyperbola","line","degenerate"),    _b_hyperbola_two_lines),
    _T("cubic_circle_line",        "Cubic + Circle + Line",        "Cubic, circle and horizontal line together.",                  ("cubic","mixed","intersection"),     _b_cubic_circle_line),
    _T("four_conics",              "Four Conics",                  "Circle, ellipse, parabola and x-axis line.",                   ("mixed","intersection"),             _b_four_conics),
])


def list_geometry_tests() -> List[Dict[str, str]]:
    """Return lightweight metadata for UI listings."""

    return [
        {
            "id": test.id,
            "name": test.name,
            "description": test.description,
            "tags": list(test.tags),
        }
        for test in GEOMETRY_TESTS.values()
    ]


def run_geometry_test(
    test_id: str,
    scene_manager: SceneManager,
    curve_factory: CurveFactory,
    region_factory: RegionFactory,
) -> List[str]:
    """Clear the scene and execute a test builder."""

    if test_id not in GEOMETRY_TESTS:
        raise KeyError(f"Unknown geometry test id '{test_id}'")

    # Clear scene before running new scenario
    for obj_id in list(scene_manager.list_objects()):
        scene_manager.remove_object(obj_id)

    definition = GEOMETRY_TESTS[test_id]
    return definition.builder(scene_manager, curve_factory, region_factory)
