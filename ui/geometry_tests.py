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
import math
import numpy as np

from geometry import ImplicitCurve, ConicSection
from geometry.parametric_segment import ParametricSegment
from geometry.superellipse import Superellipse
from geometry.rfunction_curve import union, intersect, difference, blend
from geometry.procedural_curve import ProceduralCurve
from geometry import CurveField, BlendedField, SignedDistanceField, OccupancyField
from geometry.area_region import AreaRegion

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
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _ellipse(cx, cy, a, b):
    return ConicSection((_x - cx) ** 2 / a**2 + (_y - cy) ** 2 / b**2 - 1, (_x, _y))


def _line_implicit(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return ImplicitCurve(dy * (_x - x1) - dx * (_y - y1), (_x, _y))


def _parabola(vx, vy, scale=1.0, direction="up"):
    if direction == "up":
        expr = (_y - vy) - scale * (_x - vx) ** 2
    elif direction == "down":
        expr = (_y - vy) + scale * (_x - vx) ** 2
    elif direction == "right":
        expr = (_x - vx) - scale * (_y - vy) ** 2
    else:
        expr = (_x - vx) + scale * (_y - vy) ** 2
    return ImplicitCurve(expr, (_x, _y))


def _hyperbola(cx, cy, a, b):
    return ImplicitCurve((_x - cx) ** 2 / a**2 - (_y - cy) ** 2 / b**2 - 1, (_x, _y))


def _implicit(expr_str):
    return ImplicitCurve(sp.sympify(expr_str), (_x, _y))


# ── Batch 1: Circle family ────────────────────────────────────────────────────


def _b_circle_line_2pt(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2.8), C[0]),
        _add(sm, "l", _line_implicit(-4, 1.25, 3.5, -1.4), C[1]),
    ]


def _b_circle_line_tangent(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "l", _line_implicit(-3, 2, 3, 2), C[1]),
    ]


def _b_circle_line_miss(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-3, 2, 3, 2), C[1]),
    ]


def _b_circle_line_through_center(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2.5), C[0]),
        _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1]),
    ]


def _b_circle_line_vertical(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1]),
    ]


def _b_circle_line_vertical_tangent(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "l", _line_implicit(2, -3, 2, 3), C[1]),
    ]


def _b_two_circles_2pt(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-1, 0, 2), C[0]),
        _add(sm, "c2", _circle(1, 0, 2), C[1]),
    ]


def _b_two_circles_tangent_ext(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-2, 0, 2), C[0]),
        _add(sm, "c2", _circle(2, 0, 2), C[1]),
    ]


def _b_two_circles_tangent_int(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(0, 0, 3), C[0]),
        _add(sm, "c2", _circle(1, 0, 2), C[1]),
    ]


def _b_two_circles_concentric(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(0, 0, 3), C[0]),
        _add(sm, "c2", _circle(0, 0, 1.5), C[1]),
    ]


def _b_two_circles_miss(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-3, 0, 1), C[0]),
        _add(sm, "c2", _circle(3, 0, 1), C[1]),
    ]


def _b_three_circles(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(0, 0, 2), C[0]),
        _add(sm, "c2", _circle(2, 1, 1.5), C[1]),
        _add(sm, "c3", _circle(-2, 1, 1.5), C[2]),
    ]


def _b_circle_ellipse_2pt(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "e", _ellipse(1, 0, 3, 1.5), C[1]),
    ]


def _b_circle_ellipse_4pt(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "e", _ellipse(0, 0, 3, 1.2), C[2]),
    ]


def _b_circle_ellipse_tangent(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 1), C[0]),
        _add(sm, "e", _ellipse(0, 0, 2, 1), C[1]),
    ]


def _b_circle_parabola(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 1, 2), C[0]),
        _add(sm, "p", _parabola(0, -1, 0.4), C[1]),
    ]


def _b_circle_hyperbola(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2.5), C[0]),
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[1]),
    ]


def _b_circle_cubic(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 1.5), C[0]),
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
    ]


def _b_circle_tangent_to_line_at_origin(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 1, 1), C[0]),
        _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1]),
    ]


def _b_three_circles_common_chord(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-1, 0, 2), C[0]),
        _add(sm, "c2", _circle(1, 0, 2), C[1]),
        _add(sm, "l", _line_implicit(0, -3, 0, 3), C[5]),
    ]


def _b_circle_vs_circle_line(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-1, 0, 2), C[0]),
        _add(sm, "c2", _circle(1, 0, 2), C[1]),
        _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[5]),
    ]


def _b_unit_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 1), C[0])]


def _b_large_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 5), C[0])]


def _b_tiny_circle_alone(sm, cf, rf):
    return [_add(sm, "c", _circle(0, 0, 0.1), C[0])]


# ── Batch 2: Ellipse family ───────────────────────────────────────────────────


def _b_dual_ellipses(sm, cf, rf):
    return [
        _add(sm, "e1", _ellipse(-1.5, 0, 3.5, 1.25), C[0]),
        _add(sm, "e2", _ellipse(1.25, 0.6, 2.5, 1.75), C[2]),
    ]


def _b_ellipse_line_2pt(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-4, 0.5, 4, 0.5), C[1]),
    ]


def _b_ellipse_line_tangent(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-4, 1.5, 4, 1.5), C[1]),
    ]


def _b_ellipse_line_vertical(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 2, 1), C[0]),
        _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1]),
    ]


def _b_ellipse_diagonal_line(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 2.5, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-3, -2, 3, 2), C[1]),
    ]


def _b_ellipse_parabola(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 1.5, 2.5, 1.5), C[0]),
        _add(sm, "p", _parabola(0, 0, 0.3), C[2]),
    ]


def _b_ellipse_hyperbola(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 2), C[0]),
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[1]),
    ]


def _b_ellipse_cubic(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 2, 1.5), C[0]),
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
    ]


def _b_wide_ellipse_alone(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 4, 1), C[0])]


def _b_tall_ellipse_alone(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 1, 4), C[0])]


def _b_near_circle_ellipse(sm, cf, rf):
    return [_add(sm, "e", _ellipse(0, 0, 2.0, 1.95), C[0])]


def _b_three_ellipses(sm, cf, rf):
    return [
        _add(sm, "e1", _ellipse(-2, 0, 2, 1), C[0]),
        _add(sm, "e2", _ellipse(2, 0, 2, 1), C[1]),
        _add(sm, "e3", _ellipse(0, 0, 3, 0.8), C[2]),
    ]


# ── Batch 3: Parabola family ──────────────────────────────────────────────────


def _b_parabola_line_2pt(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.5), C[0]),
        _add(sm, "l", _line_implicit(-3, 1, 3, 1), C[1]),
    ]


def _b_parabola_line_tangent(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 1.0), C[0]),
        _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1]),
    ]


def _b_parabola_line_miss(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.5), C[0]),
        _add(sm, "l", _line_implicit(-3, -1, 3, -1), C[1]),
    ]


def _b_parabola_line_vertical(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.5), C[0]),
        _add(sm, "l", _line_implicit(1, -1, 1, 4), C[1]),
    ]


def _b_parabola_line_diagonal(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.5), C[0]),
        _add(sm, "l", _line_implicit(-3, -2, 3, 2), C[1]),
    ]


def _b_two_parabolas_same_axis(sm, cf, rf):
    return [
        _add(sm, "p1", _parabola(0, -1.5, 0.4, "up"), C[0]),
        _add(sm, "p2", _parabola(0, 1.25, 0.35, "down"), C[2]),
    ]


def _b_two_parabolas_cross(sm, cf, rf):
    return [
        _add(sm, "p1", _parabola(0, 0, 0.5, "up"), C[0]),
        _add(sm, "p2", _parabola(0, 0, 0.5, "right"), C[1]),
    ]


def _b_parabola_bundle(sm, cf, rf):
    return [
        _add(sm, "p1", _parabola(0, -1.5, 0.4, "up"), C[0]),
        _add(sm, "p2", _parabola(0, 1.25, 0.35, "down"), C[2]),
        _add(sm, "l", _line_implicit(-3.5, -2.5, 3.5, 2.5), C[1]),
    ]


def _b_parabola_offset_vertex(sm, cf, rf):
    return [
        _add(sm, "p1", _parabola(-2, 0, 0.5, "up"), C[0]),
        _add(sm, "p2", _parabola(2, 0, 0.5, "up"), C[1]),
    ]


def _b_parabola_horizontal(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.5, "right"), C[0]),
        _add(sm, "l", _line_implicit(1, -3, 1, 3), C[1]),
    ]


# ── Batch 4: Hyperbola family ─────────────────────────────────────────────────


def _b_hyperbola_line_2pt(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "l", _line_implicit(-4, 0.5, 4, 0.5), C[1]),
    ]


def _b_hyperbola_line_asymptote(sm, cf, rf):
    a, b = 1.5, 1.0
    return [
        _add(sm, "h", _hyperbola(0, 0, a, b), C[0]),
        _add(sm, "l", _line_implicit(-4, -4 * b / a, 4, 4 * b / a), C[1]),
    ]


def _b_hyperbola_line_vertical(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "l", _line_implicit(2, -4, 2, 4), C[1]),
    ]


def _b_hyperbola_circle(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "c", _circle(0, 0, 2.5), C[1]),
    ]


def _b_hyperbola_ellipse(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "e", _ellipse(0, 0, 3, 2), C[2]),
    ]


def _b_hyperbola_parabola(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "p", _parabola(0, -1, 0.4), C[1]),
    ]


def _b_two_hyperbolas_conjugate(sm, cf, rf):
    return [
        _add(sm, "h1", _hyperbola(0, 0, 1.5, 1), C[0]),
        _add(sm, "h2", ImplicitCurve(_y**2 / 1.0 - _x**2 / 2.25 - 1, (_x, _y)), C[1]),
    ]


def _b_hyperbola_alone(sm, cf, rf):
    return [_add(sm, "h", _hyperbola(0, 0, 2, 1.5), C[0])]


# ── Batch 5: Cubic & special curves ──────────────────────────────────────────


def _b_cubic_x_axis(sm, cf, rf):
    return [
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
        _add(sm, "l", _line_implicit(-2.5, 0, 2.5, 0), C[4]),
    ]


def _b_cubic_guides(sm, cf, rf):
    return [
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
        _add(sm, "lx", _line_implicit(-2.5, 0, 2.5, 0), C[4]),
        _add(sm, "ly", _line_implicit(0, -3, 0, 3), C[5]),
    ]


def _b_cubic_line_3pt(sm, cf, rf):
    return [
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
        _add(sm, "l", _line_implicit(-2, 0.5, 2, 0.5), C[4]),
    ]


def _b_folium_line(sm, cf, rf):
    return [
        _add(sm, "f", _implicit("x**3 + y**3 - 3*x*y"), C[3]),
        _add(sm, "l", _line_implicit(-2, -2, 2, 2), C[1]),
    ]


def _b_folium_circle(sm, cf, rf):
    return [
        _add(sm, "f", _implicit("x**3 + y**3 - 3*x*y"), C[3]),
        _add(sm, "c", _circle(1, 1, 1), C[0]),
    ]


def _b_lemniscate_circle(sm, cf, rf):
    return [
        _add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
        _add(sm, "c", _circle(0, 0, 1), C[0]),
    ]


def _b_lemniscate_line(sm, cf, rf):
    return [
        _add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
        _add(sm, "l", _line_implicit(-2, 0.5, 2, 0.5), C[1]),
    ]


def _b_lemniscate_ellipse(sm, cf, rf):
    return [
        _add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
        _add(sm, "e", _ellipse(0, 0, 1.5, 0.8), C[2]),
    ]


def _b_cassini_circle(sm, cf, rf):
    return [
        _add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
        _add(sm, "c", _circle(0, 0, 1.5), C[0]),
    ]


def _b_cassini_line(sm, cf, rf):
    return [
        _add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
        _add(sm, "l", _line_implicit(-3, 0.5, 3, 0.5), C[1]),
    ]


def _b_cardioid_circle(sm, cf, rf):
    return [
        _add(sm, "card", _implicit("(x**2+y**2-x)**2 - (x**2+y**2)"), C[1]),
        _add(sm, "c", _circle(0.5, 0, 0.5), C[0]),
    ]


def _b_cardioid_line(sm, cf, rf):
    return [
        _add(sm, "card", _implicit("(x**2+y**2-x)**2 - (x**2+y**2)"), C[1]),
        _add(sm, "l", _line_implicit(-2, 0.5, 2, 0.5), C[4]),
    ]


# ── Batch 6: Line combinations & degenerate ───────────────────────────────────


def _b_three_lines_concurrent(sm, cf, rf):
    return [
        _add(sm, "l1", _line_implicit(-3, -2, 3, 2), C[0]),
        _add(sm, "l2", _line_implicit(-3, 2, 3, -2), C[1]),
        _add(sm, "l3", _line_implicit(-3, 0, 3, 0), C[2]),
    ]


def _b_four_lines_grid(sm, cf, rf):
    return [
        _add(sm, "l1", _line_implicit(-3, -1, 3, -1), C[0]),
        _add(sm, "l2", _line_implicit(-3, 1, 3, 1), C[1]),
        _add(sm, "l3", _line_implicit(-1, -3, -1, 3), C[2]),
        _add(sm, "l4", _line_implicit(1, -3, 1, 3), C[3]),
    ]


def _b_parallel_lines(sm, cf, rf):
    return [
        _add(sm, "l1", _line_implicit(-3, -1, 3, -1), C[0]),
        _add(sm, "l2", _line_implicit(-3, 1, 3, 1), C[1]),
    ]


def _b_coincident_lines(sm, cf, rf):
    return [
        _add(sm, "l1", _line_implicit(-3, 0, 3, 0), C[0]),
        _add(sm, "l2", _line_implicit(-2, 0, 2, 0), C[1]),
    ]


def _b_star_of_lines(sm, cf, rf):
    import math

    ids = []
    for i in range(5):
        angle = math.pi * i / 5
        dx, dy = math.cos(angle) * 3, math.sin(angle) * 3
        ids.append(_add(sm, f"l{i}", _line_implicit(-dx, -dy, dx, dy), C[i % 6]))
    return ids


def _b_composite_quarters(sm, cf, rf):
    return [
        _add(
            sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]
        ),
        _add(sm, "l", _line_implicit(-4, 0, 4, 0), C[0]),
    ]


def _b_composite_quarters_diagonal(sm, cf, rf):
    return [
        _add(
            sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]
        ),
        _add(sm, "l", _line_implicit(-3, -3, 3, 3), C[1]),
    ]


def _b_composite_quarters_circle(sm, cf, rf):
    return [
        _add(
            sm, "qp", cf.create_composite_circle_quarters(center=(0, 0), radius=3), C[3]
        ),
        _add(sm, "c", _circle(0, 0, 2), C[0]),
    ]


# ── Batch 7: Mixed / stress tests ────────────────────────────────────────────


def _b_conic_zoo(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "e", _ellipse(0, 0, 3, 1.2), C[1]),
        _add(sm, "p", _parabola(0, -2, 0.3), C[2]),
        _add(sm, "h", _hyperbola(0, 0, 1.5, 1), C[4]),
    ]


def _b_circle_ellipse_parabola(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "e", _ellipse(0, 0, 3, 1.5), C[1]),
        _add(sm, "p", _parabola(0, -1, 0.4), C[2]),
    ]


def _b_two_circles_parabola(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-1.5, 0, 1.5), C[0]),
        _add(sm, "c2", _circle(1.5, 0, 1.5), C[1]),
        _add(sm, "p", _parabola(0, -2, 0.3), C[2]),
    ]


def _b_ellipse_two_lines(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 2.5, 1.5), C[0]),
        _add(sm, "l1", _line_implicit(-3, -1, 3, 1), C[1]),
        _add(sm, "l2", _line_implicit(-3, 1, 3, -1), C[2]),
    ]


def _b_parabola_two_circles(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.4), C[0]),
        _add(sm, "c1", _circle(-1.5, 1.5, 1), C[1]),
        _add(sm, "c2", _circle(1.5, 1.5, 1), C[2]),
    ]


def _b_hyperbola_two_lines(sm, cf, rf):
    a, b = 1.5, 1.0
    return [
        _add(sm, "h", _hyperbola(0, 0, a, b), C[0]),
        _add(sm, "l1", _line_implicit(-4, -4 * b / a, 4, 4 * b / a), C[5]),
        _add(sm, "l2", _line_implicit(-4, 4 * b / a, 4, -4 * b / a), C[4]),
    ]


def _b_cubic_circle_line(sm, cf, rf):
    return [
        _add(sm, "cu", _implicit("y**2 - x**3 + x"), C[1]),
        _add(sm, "c", _circle(0, 0, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-2, 0.5, 2, 0.5), C[4]),
    ]


def _b_near_tangent_circles(sm, cf, rf):
    return [
        _add(sm, "c1", _circle(-2.05, 0, 2), C[0]),
        _add(sm, "c2", _circle(2.05, 0, 2), C[1]),
    ]


def _b_near_tangent_circle_line(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "l", _line_implicit(-3, 1.99, 3, 1.99), C[1]),
    ]


def _b_near_tangent_ellipse_line(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 1.5), C[0]),
        _add(sm, "l", _line_implicit(-4, 1.49, 4, 1.49), C[1]),
    ]


def _b_very_flat_ellipse(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 0.2), C[0]),
        _add(sm, "l", _line_implicit(-4, 0.1, 4, 0.1), C[1]),
    ]


def _b_very_narrow_hyperbola(sm, cf, rf):
    return [
        _add(sm, "h", _hyperbola(0, 0, 0.2, 2), C[0]),
        _add(sm, "l", _line_implicit(-3, 0, 3, 0), C[1]),
    ]


def _b_steep_parabola(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 3.0), C[0]),
        _add(sm, "l", _line_implicit(-2, 1, 2, 1), C[1]),
    ]


def _b_shallow_parabola(sm, cf, rf):
    return [
        _add(sm, "p", _parabola(0, 0, 0.05), C[0]),
        _add(sm, "l", _line_implicit(-5, 1, 5, 1), C[1]),
    ]


def _b_offset_cubic(sm, cf, rf):
    return [
        _add(sm, "cu", _implicit("(y-1)**2 - (x-1)**3 + (x-1)"), C[1]),
        _add(sm, "c", _circle(1, 1, 1.5), C[0]),
    ]


def _b_circle_inside_ellipse(sm, cf, rf):
    return [
        _add(sm, "e", _ellipse(0, 0, 3, 2), C[0]),
        _add(sm, "c", _circle(0, 0, 1), C[1]),
    ]


def _b_ellipse_inside_circle(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 3), C[0]),
        _add(sm, "e", _ellipse(0, 0, 2, 1), C[1]),
    ]


def _b_four_conics(sm, cf, rf):
    return [
        _add(sm, "c", _circle(0, 0, 2), C[0]),
        _add(sm, "e", _ellipse(0, 0, 3, 1), C[1]),
        _add(sm, "p", _parabola(0, -2, 0.25), C[2]),
        _add(sm, "l", _line_implicit(-4, 0, 4, 0), C[5]),
    ]


def _b_lemniscate_parabola(sm, cf, rf):
    return [
        _add(sm, "lem", _implicit("(x**2+y**2)**2 - 2*(x**2-y**2)"), C[5]),
        _add(sm, "p", _parabola(0, 0, 0.5), C[1]),
    ]


def _b_cassini_parabola(sm, cf, rf):
    return [
        _add(sm, "cas", _implicit("((x-1)**2+y**2)*((x+1)**2+y**2) - 4"), C[2]),
        _add(sm, "p", _parabola(0, -1, 0.3), C[0]),
    ]


# ── Parametric Segment Builders ──────────────────────────────────────────────


def _b_parametric_circle_arc_line(sm, cf, rf):
    arc = ParametricSegment(
        lambda t: 2.0 * math.cos(t),
        lambda t: 2.0 * math.sin(t),
        0.0,
        math.pi / 2.0,
        name="ParamArc",
    )
    line = _line_implicit(-3, 1.0, 3, 1.0)
    return [_add(sm, "arc", arc, C[0]), _add(sm, "line", line, C[1])]


def _b_parametric_lissajous_circle(sm, cf, rf):
    liss = ParametricSegment(
        lambda t: 2.0 * math.sin(3.0 * t),
        lambda t: 2.0 * math.sin(2.0 * t),
        0.0,
        2.0 * math.pi,
        name="Lissajous32",
        is_periodic=True,
    )
    circ = _circle(0, 0, 0.7)
    return [_add(sm, "liss", liss, C[1]), _add(sm, "circ", circ, C[0])]


def _b_parametric_cycloid_line(sm, cf, rf):
    cycl = ParametricSegment(
        lambda t: (t - math.sin(t)) - math.pi,
        lambda t: (1.0 - math.cos(t)) - 1.0,
        0.0,
        2.0 * math.pi,
        name="Cycloid",
    )
    line = _line_implicit(-5, 0.0, 5, 0.0)
    return [_add(sm, "cycl", cycl, C[2]), _add(sm, "line", line, C[3])]


def _b_parametric_astroid_circle(sm, cf, rf):
    astr = ParametricSegment(
        lambda t: 2.0 * (math.cos(t) ** 3),
        lambda t: 2.0 * (math.sin(t) ** 3),
        0.0,
        2.0 * math.pi,
        name="Astroid",
        is_periodic=True,
    )
    circ = _circle(0, 0, 0.5)
    return [_add(sm, "astr", astr, C[4]), _add(sm, "circ", circ, C[5])]


def _b_parametric_rose_ellipse(sm, cf, rf):
    rose = ParametricSegment(
        lambda t: 2.0 * math.cos(3.0 * t) * math.cos(t),
        lambda t: 2.0 * math.cos(3.0 * t) * math.sin(t),
        0.0,
        math.pi,
        name="Rose3Petal",
        is_periodic=True,
    )
    ell = _ellipse(0, 0, 1.2, 0.8)
    return [_add(sm, "rose", rose, C[0]), _add(sm, "ell", ell, C[2])]


def _b_parametric_sine_arch_parabola(sm, cf, rf):
    arch = ParametricSegment(
        lambda t: t, lambda t: math.sin(t), 0.0, math.pi, name="SineArch"
    )
    par = _parabola(math.pi / 2, 0.5, scale=-0.5, direction="up")
    return [_add(sm, "arch", arch, C[3]), _add(sm, "par", par, C[1])]


def _b_parametric_two_arcs(sm, cf, rf):
    arc1 = ParametricSegment(
        lambda t: 2.0 * math.cos(t),
        lambda t: 2.0 * math.sin(t),
        0.0,
        math.pi,
        name="Arc1",
    )
    arc2 = ParametricSegment(
        lambda t: 1.0 + 1.5 * math.cos(t),
        lambda t: 1.5 * math.sin(t),
        math.pi / 2.0,
        3.0 * math.pi / 2.0,
        name="Arc2",
    )
    return [_add(sm, "arc1", arc1, C[0]), _add(sm, "arc2", arc2, C[4])]


def _b_parametric_figure_eight_line(sm, cf, rf):
    fig8 = ParametricSegment(
        lambda t: 2.0 * math.sin(t),
        lambda t: 2.0 * math.sin(2.0 * t),
        0.0,
        2.0 * math.pi,
        name="FigureEight",
        is_periodic=True,
    )
    line = _line_implicit(-3, 0.0, 3, 0.0)
    return [_add(sm, "fig8", fig8, C[1]), _add(sm, "line", line, C[5])]


# ── Superellipse Builders ────────────────────────────────────────────────────


def _b_superellipse_diamond_line(sm, cf, rf):
    se = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=1.0)
    line = _line_implicit(-3, 1.0, 3, -1.0)
    return [_add(sm, "se", se, C[2]), _add(sm, "line", line, C[0])]


def _b_superellipse_circle_n2(sm, cf, rf):
    se = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=2.0)
    circ = _circle(1.0, 1.0, 1.5)
    return [_add(sm, "se", se, C[3]), _add(sm, "circ", circ, C[1])]


def _b_superellipse_squircle_circle(sm, cf, rf):
    se = Superellipse(center_x=0.0, center_y=0.0, a=1.2, b=1.2, n=4.0)
    circ = _circle(0.0, 0.0, 1.3)
    return [_add(sm, "se", se, C[1]), _add(sm, "circ", circ, C[0])]


def _b_superellipse_near_square_parabola(sm, cf, rf):
    se = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=1.5, n=8.0)
    par = _parabola(0.0, -1.0, 0.5, "up")
    return [_add(sm, "se", se, C[4]), _add(sm, "par", par, C[2])]


def _b_superellipse_comparison(sm, cf, rf):
    se1 = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=1.0)
    se2 = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=2.0)
    se3 = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=4.0)
    return [
        _add(sm, "se1", se1, C[0]),
        _add(sm, "se2", se2, C[1]),
        _add(sm, "se3", se3, C[3]),
    ]


def _b_superellipse_intersection_pair(sm, cf, rf):
    se1 = Superellipse(center_x=-0.5, center_y=0.0, a=1.5, b=1.5, n=4.0)
    se2 = Superellipse(center_x=0.5, center_y=0.0, a=1.5, b=1.5, n=1.5)
    return [_add(sm, "se1", se1, C[4]), _add(sm, "se2", se2, C[5])]


# ── RFunctionCurve Builders ──────────────────────────────────────────────────


def _b_rfunction_union_circles(sm, cf, rf):
    c1 = _circle(-0.8, 0, 1.5)
    c2 = _circle(0.8, 0, 1.5)
    rf_union = union(c1, c2)
    return [_add(sm, "r_union", rf_union, C[3])]


def _b_rfunction_union_ellipse_circle(sm, cf, rf):
    el = _ellipse(-0.5, 0, 2.0, 1.2)
    ci = _circle(1.0, 0, 1.2)
    rf_union = union(el, ci)
    line = _line_implicit(-3, 0.5, 3, 0.5)
    return [_add(sm, "r_union", rf_union, C[0]), _add(sm, "line", line, C[1])]


def _b_rfunction_intersect_circles(sm, cf, rf):
    c1 = _circle(-0.8, 0, 1.5)
    c2 = _circle(0.8, 0, 1.5)
    rf_inter = intersect(c1, c2)
    return [_add(sm, "r_inter", rf_inter, C[1])]


def _b_rfunction_difference_pac_man(sm, cf, rf):
    c1 = _circle(0, 0, 2.0)
    c2 = _circle(1.2, 1.2, 1.0)
    rf_diff = difference(c1, c2)
    line = _line_implicit(-3, 0.5, 3, 0.5)
    return [_add(sm, "r_diff", rf_diff, C[2]), _add(sm, "line", line, C[4])]


def _b_rfunction_blend_circles(sm, cf, rf):
    c1 = _circle(-0.8, 0, 1.5)
    c2 = _circle(0.8, 0, 1.5)
    rf_blend = blend(c1, c2, 0.3)
    line = _line_implicit(-3, 0.5, 3, 0.5)
    return [_add(sm, "r_blend", rf_blend, C[0]), _add(sm, "line", line, C[5])]


def _b_rfunction_nested_union(sm, cf, rf):
    c1 = _circle(-1.0, -0.5, 1.2)
    c2 = _circle(1.0, -0.5, 1.2)
    c3 = _circle(0.0, 1.0, 1.2)
    u12 = union(c1, c2)
    rf_nest = union(u12, c3)
    return [_add(sm, "r_nest", rf_nest, C[4])]


def _b_rfunction_difference_vs_ellipse(sm, cf, rf):
    c1 = _circle(0, 0, 2.0)
    c2 = _circle(1.0, 0, 1.2)
    rf_diff = difference(c1, c2)
    ell = _ellipse(0, 0, 1.5, 0.8)
    return [_add(sm, "r_diff", rf_diff, C[2]), _add(sm, "ell", ell, C[3])]


def _b_rfunction_blend_alpha_compare(sm, cf, rf):
    c1 = _circle(-1.2, 0, 1.0)
    c2 = _circle(0.0, 0, 1.0)
    c3 = _circle(1.2, 0, 1.0)
    b12 = blend(c1, c2, 0.1)
    b23 = blend(b12, c3, 0.5)
    return [_add(sm, "r_blend", b23, C[0])]


# ── ProceduralCurve Builders ─────────────────────────────────────────────────


def _b_procedural_sin_line(sm, cf, rf):
    pc = ProceduralCurve(
        lambda x, y: np.sin(x) - y, name="sin(x) - y", is_periodic=True
    )
    pc.xmin, pc.xmax, pc.ymin, pc.ymax = -2.0 * math.pi, 2.0 * math.pi, -1.5, 1.5
    line = _line_implicit(-6, 0.5, 6, 0.5)
    return [_add(sm, "pc", pc, C[1]), _add(sm, "line", line, C[0])]


def _b_procedural_gaussian_line(sm, cf, rf):
    pc = ProceduralCurve(lambda x, y: np.exp(-(x**2)) - y, name="exp(-x**2) - y")
    pc.xmin, pc.xmax, pc.ymin, pc.ymax = -3.0, 3.0, 0.0, 1.1
    line = _line_implicit(-3, 0.5, 3, 0.5)
    return [_add(sm, "pc", pc, C[2]), _add(sm, "line", line, C[4])]


def _b_procedural_ripple_circle(sm, cf, rf):
    pc = ProceduralCurve(
        lambda x, y: x**2 + y**2 + np.sin(5.0 * x) - 1.0,
        name="x**2 + y**2 + sin(5*x) - 1",
    )
    pc.xmin, pc.xmax, pc.ymin, pc.ymax = -2.0, 2.0, -2.0, 2.0
    circ = _circle(0.0, 0.0, 1.5)
    return [_add(sm, "pc", pc, C[3]), _add(sm, "circ", circ, C[0])]


def _b_procedural_tanh_parabola(sm, cf, rf):
    pc = ProceduralCurve(lambda x, y: np.tanh(x) - y, name="tanh(x) - y")
    pc.xmin, pc.xmax, pc.ymin, pc.ymax = -3.0, 3.0, -1.5, 1.5
    par = _parabola(0.0, 0.0, 0.3, "up")
    return [_add(sm, "pc", pc, C[4]), _add(sm, "par", par, C[5])]


def _b_procedural_sin_xy_line(sm, cf, rf):
    pc = ProceduralCurve(lambda x, y: np.sin(x * y), name="sin(x*y)")
    pc.xmin, pc.xmax, pc.ymin, pc.ymax = -3.0, 3.0, -3.0, 3.0
    line = _line_implicit(-3, 1.0, 3, 1.0)
    return [_add(sm, "pc", pc, C[0]), _add(sm, "line", line, C[1])]


# ── Field Builders ───────────────────────────────────────────────────────────


def _b_field_curvefield_circle_heatmap(sm, cf, rf):
    cf_field = CurveField(_circle(0.0, 0.0, 2.0))
    return [_add(sm, "cf_field", cf_field, C[3])]


def _b_field_sdf_circle(sm, cf, rf):
    region = AreaRegion(outer_boundary=_circle(0.0, 0.0, 2.0))
    sdf = SignedDistanceField(region, resolution=0.1)
    return [_add(sm, "sdf", sdf, C[0])]


def _b_field_sdf_square(sm, cf, rf):
    square_curve = Superellipse(center_x=0.0, center_y=0.0, a=2.0, b=2.0, n=10.0)
    region = AreaRegion(outer_boundary=square_curve)
    sdf = SignedDistanceField(region, resolution=0.1)
    return [_add(sm, "sdf", sdf, C[1])]


def _b_field_occupancy_circle(sm, cf, rf):
    region = AreaRegion(outer_boundary=_circle(0.0, 0.0, 2.0))
    occ = OccupancyField(region, 1.0, 0.0)
    return [_add(sm, "occ", occ, C[2])]


def _b_field_blended_add(sm, cf, rf):
    f1 = CurveField(_circle(0.0, 0.0, 2.0))
    f2 = CurveField(_ellipse(0.0, 0.0, 3.0, 1.0))
    bf = BlendedField([f1, f2], "add")
    return [_add(sm, "bf", bf, C[4])]


def _b_field_blended_min_union(sm, cf, rf):
    f1 = CurveField(_circle(-0.5, 0.0, 1.0))
    f2 = CurveField(_circle(0.5, 0.0, 1.0))
    bf = BlendedField([f1, f2], "min")
    return [_add(sm, "bf", bf, C[5])]


def _T(tid, name, desc, tags, builder):
    return tid, GeometryTestDefinition(
        id=tid, name=name, description=desc, tags=tags, builder=builder
    )


GEOMETRY_TESTS: Dict[str, GeometryTestDefinition] = dict(
    [
        # ── Circle family ──────────────────────────────────────────────────────────
        _T(
            "circle_line_2pt",
            "Circle × Line (2pt)",
            "Circle cut by a slanted line at two points.",
            ("circle", "line", "intersection"),
            _b_circle_line_2pt,
        ),
        _T(
            "circle_line_tangent",
            "Circle × Line (tangent)",
            "Horizontal line tangent to top of circle.",
            ("circle", "line", "tangency"),
            _b_circle_line_tangent,
        ),
        _T(
            "circle_line_miss",
            "Circle × Line (miss)",
            "Line passes above circle — no intersection.",
            ("circle", "line", "degenerate"),
            _b_circle_line_miss,
        ),
        _T(
            "circle_line_center",
            "Circle × Line (diameter)",
            "Line passes through circle center.",
            ("circle", "line", "intersection"),
            _b_circle_line_through_center,
        ),
        _T(
            "circle_line_vertical",
            "Circle × Vertical Line",
            "Vertical chord through circle.",
            ("circle", "line", "intersection"),
            _b_circle_line_vertical,
        ),
        _T(
            "circle_line_vtangent",
            "Circle × Vertical Tangent",
            "Vertical line tangent to circle.",
            ("circle", "line", "tangency"),
            _b_circle_line_vertical_tangent,
        ),
        _T(
            "circle_tangent_origin",
            "Circle Tangent at Origin",
            "Circle tangent to x-axis at the origin.",
            ("circle", "line", "tangency"),
            _b_circle_tangent_to_line_at_origin,
        ),
        _T(
            "two_circles_2pt",
            "Two Circles (2pt)",
            "Two equal circles overlapping at two points.",
            ("circle", "intersection"),
            _b_two_circles_2pt,
        ),
        _T(
            "two_circles_tangent_ext",
            "Two Circles (ext tangent)",
            "Two circles touching externally at one point.",
            ("circle", "tangency"),
            _b_two_circles_tangent_ext,
        ),
        _T(
            "two_circles_tangent_int",
            "Two Circles (int tangent)",
            "Smaller circle internally tangent to larger.",
            ("circle", "tangency"),
            _b_two_circles_tangent_int,
        ),
        _T(
            "two_circles_concentric",
            "Concentric Circles",
            "Two circles sharing the same centre.",
            ("circle", "degenerate"),
            _b_two_circles_concentric,
        ),
        _T(
            "two_circles_miss",
            "Two Circles (miss)",
            "Two circles far apart — no intersection.",
            ("circle", "degenerate"),
            _b_two_circles_miss,
        ),
        _T(
            "three_circles",
            "Three Circles",
            "Three circles with pairwise intersections.",
            ("circle", "intersection"),
            _b_three_circles,
        ),
        _T(
            "three_circles_chord",
            "Three Circles + Chord",
            "Two intersecting circles with their radical axis.",
            ("circle", "line", "intersection"),
            _b_three_circles_common_chord,
        ),
        _T(
            "circle_vs_circle_line",
            "2 Circles + Line",
            "Two circles and a line through their intersection.",
            ("circle", "line", "intersection"),
            _b_circle_vs_circle_line,
        ),
        _T(
            "unit_circle",
            "Unit Circle",
            "Single unit circle — basic rendering check.",
            ("circle", "basics"),
            _b_unit_circle_alone,
        ),
        _T(
            "large_circle",
            "Large Circle (r=5)",
            "Large circle — tests viewport fitting.",
            ("circle", "basics"),
            _b_large_circle_alone,
        ),
        _T(
            "tiny_circle",
            "Tiny Circle (r=0.1)",
            "Very small circle — tests resolution at small scale.",
            ("circle", "basics", "degenerate"),
            _b_tiny_circle_alone,
        ),
        # ── Circle × conic ────────────────────────────────────────────────────────
        _T(
            "circle_ellipse_2pt",
            "Circle × Ellipse (2pt)",
            "Circle and ellipse intersecting at two points.",
            ("circle", "ellipse", "intersection"),
            _b_circle_ellipse_2pt,
        ),
        _T(
            "circle_ellipse_4pt",
            "Circle × Ellipse (4pt)",
            "Concentric circle and ellipse crossing at four points.",
            ("circle", "ellipse", "intersection"),
            _b_circle_ellipse_4pt,
        ),
        _T(
            "circle_ellipse_tangent",
            "Circle × Ellipse (tangent)",
            "Circle internally tangent to ellipse.",
            ("circle", "ellipse", "tangency"),
            _b_circle_ellipse_tangent,
        ),
        _T(
            "circle_parabola",
            "Circle × Parabola",
            "Circle intersecting an upward parabola.",
            ("circle", "parabola", "intersection"),
            _b_circle_parabola,
        ),
        _T(
            "circle_hyperbola",
            "Circle × Hyperbola",
            "Circle surrounding a hyperbola.",
            ("circle", "hyperbola", "intersection"),
            _b_circle_hyperbola,
        ),
        _T(
            "circle_cubic",
            "Circle × Cubic",
            "Circle crossing an elliptic cubic curve.",
            ("circle", "cubic", "intersection"),
            _b_circle_cubic,
        ),
        # ── Ellipse family ────────────────────────────────────────────────────────
        _T(
            "dual_ellipses",
            "Dual Ellipses",
            "Two offset ellipses with multiple intersection points.",
            ("ellipse", "intersection"),
            _b_dual_ellipses,
        ),
        _T(
            "ellipse_line_2pt",
            "Ellipse × Line (2pt)",
            "Horizontal line cutting ellipse at two points.",
            ("ellipse", "line", "intersection"),
            _b_ellipse_line_2pt,
        ),
        _T(
            "ellipse_line_tangent",
            "Ellipse × Line (tangent)",
            "Horizontal line tangent to top of ellipse.",
            ("ellipse", "line", "tangency"),
            _b_ellipse_line_tangent,
        ),
        _T(
            "ellipse_line_vertical",
            "Ellipse × Vertical Line",
            "Vertical chord through ellipse.",
            ("ellipse", "line", "intersection"),
            _b_ellipse_line_vertical,
        ),
        _T(
            "ellipse_line_diagonal",
            "Ellipse × Diagonal Line",
            "Diagonal line cutting ellipse.",
            ("ellipse", "line", "intersection"),
            _b_ellipse_diagonal_line,
        ),
        _T(
            "ellipse_parabola",
            "Ellipse × Parabola",
            "Ellipse and upward parabola intersecting.",
            ("ellipse", "parabola", "intersection"),
            _b_ellipse_parabola,
        ),
        _T(
            "ellipse_hyperbola",
            "Ellipse × Hyperbola",
            "Ellipse surrounding a hyperbola.",
            ("ellipse", "hyperbola", "intersection"),
            _b_ellipse_hyperbola,
        ),
        _T(
            "ellipse_cubic",
            "Ellipse × Cubic",
            "Ellipse crossing an elliptic cubic.",
            ("ellipse", "cubic", "intersection"),
            _b_ellipse_cubic,
        ),
        _T(
            "wide_ellipse",
            "Wide Ellipse (a=4,b=1)",
            "Very wide ellipse — aspect ratio stress test.",
            ("ellipse", "basics"),
            _b_wide_ellipse_alone,
        ),
        _T(
            "tall_ellipse",
            "Tall Ellipse (a=1,b=4)",
            "Very tall ellipse — aspect ratio stress test.",
            ("ellipse", "basics"),
            _b_tall_ellipse_alone,
        ),
        _T(
            "near_circle_ellipse",
            "Near-Circle Ellipse",
            "Ellipse with a≈b — nearly circular.",
            ("ellipse", "basics", "degenerate"),
            _b_near_circle_ellipse,
        ),
        _T(
            "three_ellipses",
            "Three Ellipses",
            "Three ellipses with overlapping regions.",
            ("ellipse", "intersection"),
            _b_three_ellipses,
        ),
        _T(
            "circle_inside_ellipse",
            "Circle Inside Ellipse",
            "Circle fully inside ellipse — no intersection.",
            ("circle", "ellipse", "degenerate"),
            _b_circle_inside_ellipse,
        ),
        _T(
            "ellipse_inside_circle",
            "Ellipse Inside Circle",
            "Ellipse fully inside circle — no intersection.",
            ("circle", "ellipse", "degenerate"),
            _b_ellipse_inside_circle,
        ),
        # ── Parabola family ───────────────────────────────────────────────────────
        _T(
            "parabola_line_2pt",
            "Parabola × Line (2pt)",
            "Horizontal line cutting parabola at two points.",
            ("parabola", "line", "intersection"),
            _b_parabola_line_2pt,
        ),
        _T(
            "parabola_line_tangent",
            "Parabola × Line (tangent)",
            "Horizontal line tangent to parabola vertex.",
            ("parabola", "line", "tangency"),
            _b_parabola_line_tangent,
        ),
        _T(
            "parabola_line_miss",
            "Parabola × Line (miss)",
            "Line below parabola — no intersection.",
            ("parabola", "line", "degenerate"),
            _b_parabola_line_miss,
        ),
        _T(
            "parabola_line_vertical",
            "Parabola × Vertical Line",
            "Vertical line crossing parabola once.",
            ("parabola", "line", "intersection"),
            _b_parabola_line_vertical,
        ),
        _T(
            "parabola_line_diagonal",
            "Parabola × Diagonal Line",
            "Diagonal secant through parabola.",
            ("parabola", "line", "intersection"),
            _b_parabola_line_diagonal,
        ),
        _T(
            "two_parabolas_axis",
            "Two Parabolas (same axis)",
            "Opposing parabolas on the same axis.",
            ("parabola", "intersection"),
            _b_two_parabolas_same_axis,
        ),
        _T(
            "two_parabolas_cross",
            "Two Parabolas (cross)",
            "Up-parabola and right-parabola crossing.",
            ("parabola", "intersection"),
            _b_two_parabolas_cross,
        ),
        _T(
            "parabola_bundle",
            "Parabola Bundle",
            "Two opposing parabolas and a diagonal line.",
            ("parabola", "line", "intersection"),
            _b_parabola_bundle,
        ),
        _T(
            "parabola_offset_vertex",
            "Two Parabolas (offset)",
            "Two upward parabolas with offset vertices.",
            ("parabola", "intersection"),
            _b_parabola_offset_vertex,
        ),
        _T(
            "parabola_horizontal",
            "Horizontal Parabola",
            "Right-opening parabola with vertical line.",
            ("parabola", "line", "intersection"),
            _b_parabola_horizontal,
        ),
        _T(
            "steep_parabola",
            "Steep Parabola (scale=3)",
            "Very steep parabola — tests narrow contour extraction.",
            ("parabola", "basics", "degenerate"),
            _b_steep_parabola,
        ),
        _T(
            "shallow_parabola",
            "Shallow Parabola (scale=0.05)",
            "Very shallow parabola — nearly flat.",
            ("parabola", "basics", "degenerate"),
            _b_shallow_parabola,
        ),
        # ── Hyperbola family ──────────────────────────────────────────────────────
        _T(
            "hyperbola_line_2pt",
            "Hyperbola × Line (2pt)",
            "Horizontal line cutting one branch of hyperbola.",
            ("hyperbola", "line", "intersection"),
            _b_hyperbola_line_2pt,
        ),
        _T(
            "hyperbola_line_asymptote",
            "Hyperbola × Asymptote",
            "Line along the asymptote direction.",
            ("hyperbola", "line", "degenerate"),
            _b_hyperbola_line_asymptote,
        ),
        _T(
            "hyperbola_line_vertical",
            "Hyperbola × Vertical Line",
            "Vertical line cutting one branch.",
            ("hyperbola", "line", "intersection"),
            _b_hyperbola_line_vertical,
        ),
        _T(
            "hyperbola_circle",
            "Hyperbola × Circle",
            "Circle surrounding both branches of hyperbola.",
            ("hyperbola", "circle", "intersection"),
            _b_hyperbola_circle,
        ),
        _T(
            "hyperbola_ellipse",
            "Hyperbola × Ellipse",
            "Ellipse enclosing a hyperbola.",
            ("hyperbola", "ellipse", "intersection"),
            _b_hyperbola_ellipse,
        ),
        _T(
            "hyperbola_parabola",
            "Hyperbola × Parabola",
            "Hyperbola and parabola crossing.",
            ("hyperbola", "parabola", "intersection"),
            _b_hyperbola_parabola,
        ),
        _T(
            "two_hyperbolas_conjugate",
            "Conjugate Hyperbolas",
            "A hyperbola and its conjugate.",
            ("hyperbola", "degenerate"),
            _b_two_hyperbolas_conjugate,
        ),
        _T(
            "hyperbola_alone",
            "Hyperbola Alone",
            "Single hyperbola — basic rendering check.",
            ("hyperbola", "basics"),
            _b_hyperbola_alone,
        ),
        _T(
            "very_narrow_hyperbola",
            "Narrow Hyperbola",
            "Hyperbola with very small a — nearly vertical branches.",
            ("hyperbola", "basics", "degenerate"),
            _b_very_narrow_hyperbola,
        ),
        # ── Cubic & special curves ────────────────────────────────────────────────
        _T(
            "cubic_x_axis",
            "Cubic × X-axis",
            "Elliptic cubic with x-axis guide.",
            ("cubic", "line", "intersection"),
            _b_cubic_x_axis,
        ),
        _T(
            "cubic_guides",
            "Cubic with Guides",
            "Cubic with orthogonal guide lines.",
            ("cubic", "line", "basics"),
            _b_cubic_guides,
        ),
        _T(
            "cubic_line_3pt",
            "Cubic × Line (3pt)",
            "Line cutting cubic at three real points.",
            ("cubic", "line", "intersection"),
            _b_cubic_line_3pt,
        ),
        _T(
            "cubic_circle",
            "Cubic × Circle",
            "Circle crossing an elliptic cubic.",
            ("cubic", "circle", "intersection"),
            _b_circle_cubic,
        ),
        _T(
            "cubic_ellipse",
            "Cubic × Ellipse",
            "Ellipse crossing an elliptic cubic.",
            ("cubic", "ellipse", "intersection"),
            _b_ellipse_cubic,
        ),
        _T(
            "cubic_parabola",
            "Cubic × Parabola",
            "Parabola crossing an elliptic cubic.",
            ("cubic", "parabola", "intersection"),
            _b_cubic_circle_line,
        ),
        _T(
            "folium_line",
            "Folium × Line",
            "Folium of Descartes with a diagonal line.",
            ("cubic", "line", "intersection"),
            _b_folium_line,
        ),
        _T(
            "folium_circle",
            "Folium × Circle",
            "Folium of Descartes with a circle.",
            ("cubic", "circle", "intersection"),
            _b_folium_circle,
        ),
        _T(
            "offset_cubic",
            "Offset Cubic",
            "Elliptic cubic shifted from origin.",
            ("cubic", "circle", "basics"),
            _b_offset_cubic,
        ),
        # ── Special / higher-degree curves ────────────────────────────────────────
        _T(
            "lemniscate_circle",
            "Lemniscate × Circle",
            "Lemniscate of Bernoulli with a circle.",
            ("special", "circle", "intersection"),
            _b_lemniscate_circle,
        ),
        _T(
            "lemniscate_line",
            "Lemniscate × Line",
            "Lemniscate with a horizontal secant.",
            ("special", "line", "intersection"),
            _b_lemniscate_line,
        ),
        _T(
            "lemniscate_ellipse",
            "Lemniscate × Ellipse",
            "Lemniscate with an ellipse.",
            ("special", "ellipse", "intersection"),
            _b_lemniscate_ellipse,
        ),
        _T(
            "lemniscate_parabola",
            "Lemniscate × Parabola",
            "Lemniscate with a parabola.",
            ("special", "parabola", "intersection"),
            _b_lemniscate_parabola,
        ),
        _T(
            "cassini_circle",
            "Cassini Oval × Circle",
            "Cassini oval with a circle.",
            ("special", "circle", "intersection"),
            _b_cassini_circle,
        ),
        _T(
            "cassini_line",
            "Cassini Oval × Line",
            "Cassini oval with a horizontal line.",
            ("special", "line", "intersection"),
            _b_cassini_line,
        ),
        _T(
            "cassini_parabola",
            "Cassini Oval × Parabola",
            "Cassini oval with a parabola.",
            ("special", "parabola", "intersection"),
            _b_cassini_parabola,
        ),
        _T(
            "cardioid_circle",
            "Cardioid × Circle",
            "Cardioid with an inscribed circle.",
            ("special", "circle", "intersection"),
            _b_cardioid_circle,
        ),
        _T(
            "cardioid_line",
            "Cardioid × Line",
            "Cardioid with a horizontal secant.",
            ("special", "line", "intersection"),
            _b_cardioid_line,
        ),
        # ── Line combinations & degenerate ────────────────────────────────────────
        _T(
            "three_lines_concurrent",
            "Three Concurrent Lines",
            "Three lines meeting at a single point.",
            ("line", "degenerate"),
            _b_three_lines_concurrent,
        ),
        _T(
            "four_lines_grid",
            "Four Lines (grid)",
            "Two horizontal and two vertical lines forming a grid.",
            ("line", "intersection"),
            _b_four_lines_grid,
        ),
        _T(
            "parallel_lines",
            "Parallel Lines",
            "Two parallel horizontal lines — no intersection.",
            ("line", "degenerate"),
            _b_parallel_lines,
        ),
        _T(
            "coincident_lines",
            "Coincident Lines",
            "Two segments on the same line — fully degenerate.",
            ("line", "degenerate"),
            _b_coincident_lines,
        ),
        _T(
            "star_of_lines",
            "Star of Lines",
            "Five lines through the origin forming a star.",
            ("line", "intersection"),
            _b_star_of_lines,
        ),
        # ── Composite curves ──────────────────────────────────────────────────────
        _T(
            "composite_quarters",
            "Composite Quarters",
            "Composite quarter-circles crossing a reference line.",
            ("composite", "circle", "intersection"),
            _b_composite_quarters,
        ),
        _T(
            "composite_quarters_diag",
            "Composite Quarters + Diag",
            "Composite quarter-circles with a diagonal line.",
            ("composite", "circle", "intersection"),
            _b_composite_quarters_diagonal,
        ),
        _T(
            "composite_quarters_circ",
            "Composite Quarters + Circle",
            "Composite quarter-circles with an inner circle.",
            ("composite", "circle", "intersection"),
            _b_composite_quarters_circle,
        ),
        # ── Near-tangent / stress ─────────────────────────────────────────────────
        _T(
            "near_tangent_circles",
            "Near-Tangent Circles",
            "Two circles almost touching externally.",
            ("circle", "tangency", "degenerate"),
            _b_near_tangent_circles,
        ),
        _T(
            "near_tangent_circle_line",
            "Near-Tangent Circle+Line",
            "Line almost tangent to circle (ε gap).",
            ("circle", "line", "degenerate"),
            _b_near_tangent_circle_line,
        ),
        _T(
            "near_tangent_ellipse_line",
            "Near-Tangent Ellipse+Line",
            "Line almost tangent to ellipse (ε gap).",
            ("ellipse", "line", "degenerate"),
            _b_near_tangent_ellipse_line,
        ),
        _T(
            "very_flat_ellipse",
            "Very Flat Ellipse",
            "Ellipse with b=0.2 — nearly a line segment.",
            ("ellipse", "line", "degenerate"),
            _b_very_flat_ellipse,
        ),
        # ── Mixed / multi-curve ───────────────────────────────────────────────────
        _T(
            "conic_zoo",
            "Conic Zoo",
            "Circle, ellipse, parabola and hyperbola together.",
            ("mixed", "intersection"),
            _b_conic_zoo,
        ),
        _T(
            "circle_ellipse_parabola",
            "Circle+Ellipse+Parabola",
            "Three conics with multiple intersections.",
            ("mixed", "intersection"),
            _b_circle_ellipse_parabola,
        ),
        _T(
            "two_circles_parabola",
            "2 Circles + Parabola",
            "Two circles and a parabola.",
            ("mixed", "intersection"),
            _b_two_circles_parabola,
        ),
        _T(
            "ellipse_two_lines",
            "Ellipse + 2 Lines",
            "Ellipse with two crossing secants.",
            ("ellipse", "line", "intersection"),
            _b_ellipse_two_lines,
        ),
        _T(
            "parabola_two_circles",
            "Parabola + 2 Circles",
            "Parabola with two circles above it.",
            ("parabola", "circle", "intersection"),
            _b_parabola_two_circles,
        ),
        _T(
            "hyperbola_two_lines",
            "Hyperbola + Asymptotes",
            "Hyperbola with both asymptote lines.",
            ("hyperbola", "line", "degenerate"),
            _b_hyperbola_two_lines,
        ),
        _T(
            "cubic_circle_line",
            "Cubic + Circle + Line",
            "Cubic, circle and horizontal line together.",
            ("cubic", "mixed", "intersection"),
            _b_cubic_circle_line,
        ),
        _T(
            "four_conics",
            "Four Conics",
            "Circle, ellipse, parabola and x-axis line.",
            ("mixed", "intersection"),
            _b_four_conics,
        ),
        # ── Parametric Segment family ────────────────────────────────────────────────
        _T(
            "parametric_circle_arc_line",
            "Parametric Circle Arc × Line",
            "Quarter circle arc intersected by horizontal line.",
            ("parametric", "line", "intersection"),
            _b_parametric_circle_arc_line,
        ),
        _T(
            "parametric_lissajous_circle",
            "Lissajous × Circle",
            "Lissajous (3:2) curve with a concentric circle.",
            ("parametric", "circle", "intersection"),
            _b_parametric_lissajous_circle,
        ),
        _T(
            "parametric_cycloid_line",
            "Cycloid × Line",
            "One arch of a cycloid cut by a line.",
            ("parametric", "line", "intersection"),
            _b_parametric_cycloid_line,
        ),
        _T(
            "parametric_astroid_circle",
            "Astroid × Circle",
            "Astroid curve with a concentric circle.",
            ("parametric", "circle", "intersection"),
            _b_parametric_astroid_circle,
        ),
        _T(
            "parametric_rose_ellipse",
            "Rose × Ellipse",
            "Three-petal rose curve intersected by an ellipse.",
            ("parametric", "ellipse", "intersection"),
            _b_parametric_rose_ellipse,
        ),
        _T(
            "parametric_sine_arch_parabola",
            "Sine Arch × Parabola",
            "Sine arch intersected by a parabola.",
            ("parametric", "parabola", "intersection"),
            _b_parametric_sine_arch_parabola,
        ),
        _T(
            "parametric_two_arcs",
            "Two Parametric Arcs",
            "Two intersecting circular parametric arcs.",
            ("parametric", "intersection"),
            _b_parametric_two_arcs,
        ),
        _T(
            "parametric_figure_eight_line",
            "Figure Eight × Line",
            "Figure-eight curve cut by x-axis.",
            ("parametric", "line", "intersection"),
            _b_parametric_figure_eight_line,
        ),
        # ── Superellipse family ──────────────────────────────────────────────────────
        _T(
            "superellipse_diamond_line",
            "Superellipse Diamond × Line",
            "Diamond-like superellipse (n=1) cut by diagonal line.",
            ("superellipse", "line", "intersection"),
            _b_superellipse_diamond_line,
        ),
        _T(
            "superellipse_circle_n2",
            "Superellipse Ellipse × Circle",
            "Ellipse-like superellipse (n=2) with offset circle.",
            ("superellipse", "circle", "intersection"),
            _b_superellipse_circle_n2,
        ),
        _T(
            "superellipse_squircle_circle",
            "Squircle × Circle",
            "Squircle (n=4) intersected by circle.",
            ("superellipse", "circle", "intersection"),
            _b_superellipse_squircle_circle,
        ),
        _T(
            "superellipse_near_square_parabola",
            "Near-Square × Parabola",
            "Near-square superellipse (n=8) with parabola.",
            ("superellipse", "parabola", "intersection"),
            _b_superellipse_near_square_parabola,
        ),
        _T(
            "superellipse_comparison",
            "Superellipse Comparison",
            "Three nested superellipses with different powers (n=1,2,4).",
            ("superellipse", "basics"),
            _b_superellipse_comparison,
        ),
        _T(
            "superellipse_intersection_pair",
            "Two Superellipses",
            "Two overlapping superellipses with different exponents.",
            ("superellipse", "intersection"),
            _b_superellipse_intersection_pair,
        ),
        # ── RFunctionCurve family ────────────────────────────────────────────────────
        _T(
            "rfunction_union_circles",
            "R-Function Union of Circles",
            "Union of two overlapping circles.",
            ("rfunction", "union"),
            _b_rfunction_union_circles,
        ),
        _T(
            "rfunction_union_ellipse_circle",
            "R-Function Union × Line",
            "Union of ellipse and circle cut by horizontal line.",
            ("rfunction", "union", "line"),
            _b_rfunction_union_ellipse_circle,
        ),
        _T(
            "rfunction_intersect_circles",
            "R-Function Intersection",
            "Intersection of two overlapping circles.",
            ("rfunction", "intersection"),
            _b_rfunction_intersect_circles,
        ),
        _T(
            "rfunction_difference_pac_man",
            "R-Function Pac-Man × Line",
            "Circle minus smaller offset circle, cut by line.",
            ("rfunction", "difference", "line"),
            _b_rfunction_difference_pac_man,
        ),
        _T(
            "rfunction_blend_circles",
            "R-Function Blend × Line",
            "Smooth R-function blend of two circles, cut by line.",
            ("rfunction", "blend", "line"),
            _b_rfunction_blend_circles,
        ),
        _T(
            "rfunction_nested_union",
            "R-Function Nested Union",
            "Nested R-function union of three circles.",
            ("rfunction", "union"),
            _b_rfunction_nested_union,
        ),
        _T(
            "rfunction_difference_vs_ellipse",
            "R-Function Diff × Ellipse",
            "Difference of circle and circle, intersected by ellipse.",
            ("rfunction", "difference", "ellipse"),
            _b_rfunction_difference_vs_ellipse,
        ),
        _T(
            "rfunction_blend_alpha_compare",
            "R-Function Blended Chain",
            "Chain of three blended circles showing different alpha.",
            ("rfunction", "blend"),
            _b_rfunction_blend_alpha_compare,
        ),
        # ── ProceduralCurve family ───────────────────────────────────────────────────
        _T(
            "procedural_sin_line",
            "Procedural Sine × Line",
            "Procedural sine curve cut by horizontal line.",
            ("procedural", "line", "intersection"),
            _b_procedural_sin_line,
        ),
        _T(
            "procedural_gaussian_line",
            "Procedural Gaussian × Line",
            "Procedural Gaussian curve cut by horizontal line.",
            ("procedural", "line", "intersection"),
            _b_procedural_gaussian_line,
        ),
        _T(
            "procedural_ripple_circle",
            "Procedural Ripple × Circle",
            "Concentric procedural ripple curve crossing a circle.",
            ("procedural", "circle", "intersection"),
            _b_procedural_ripple_circle,
        ),
        _T(
            "procedural_tanh_parabola",
            "Procedural Tanh × Parabola",
            "Procedural hyperbolic tangent curve crossing a parabola.",
            ("procedural", "parabola", "intersection"),
            _b_procedural_tanh_parabola,
        ),
        _T(
            "procedural_sin_xy_line",
            "Procedural sin(x*y) × Line",
            "Hyperbolic pattern generated by sin(x*y) cut by line.",
            ("procedural", "line", "intersection"),
            _b_procedural_sin_xy_line,
        ),
        # ── Field family ─────────────────────────────────────────────────────────────
        _T(
            "field_curvefield_circle_heatmap",
            "Curve Field Heatmap",
            "CurveField around a circle showing field value heatmap.",
            ("field", "basics"),
            _b_field_curvefield_circle_heatmap,
        ),
        _T(
            "field_sdf_circle",
            "SDF Circle",
            "Signed Distance Field of a circular region.",
            ("field", "sdf"),
            _b_field_sdf_circle,
        ),
        _T(
            "field_sdf_square",
            "SDF Square",
            "Signed Distance Field of a square region.",
            ("field", "sdf"),
            _b_field_sdf_square,
        ),
        _T(
            "field_occupancy_circle",
            "Occupancy Circle",
            "Occupancy Field (inside/outside indicator) of circular region.",
            ("field", "occupancy"),
            _b_field_occupancy_circle,
        ),
        _T(
            "field_blended_add",
            "Blended Field Add",
            "Sum of two curve fields.",
            ("field", "blended"),
            _b_field_blended_add,
        ),
        _T(
            "field_blended_min_union",
            "Blended Field Min Union",
            "Min of two curve fields (union of their interior).",
            ("field", "blended"),
            _b_field_blended_min_union,
        ),
    ]
)


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
