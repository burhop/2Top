"""Helper builders for reusable geometry fixtures."""

from __future__ import annotations

import math
import sympy as sp

from geometry import CompositeCurve
from geometry.polynomial_curve import PolynomialCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve


def make_line_segment(point_a, point_b) -> TrimmedImplicitCurve:
    """Create a trimmed line segment between two points."""

    x, y = sp.symbols("x y")
    ax, ay = point_a
    bx, by = point_b

    if abs(ax - bx) < 1e-12:
        line = PolynomialCurve(x - ax, variables=(x, y))
        mask = lambda px, py: min(ay, by) <= py <= max(ay, by)
    else:
        slope = (by - ay) / (bx - ax)
        intercept = ay - slope * ax
        line = PolynomialCurve(y - (slope * x + intercept), variables=(x, y))
        mask = lambda px, py: min(ax, bx) <= px <= max(ax, bx)
    return TrimmedImplicitCurve(line, mask, endpoints=[point_a, point_b])


def build_axis_aligned_rectangle(min_x: float, min_y: float, width: float, height: float, **kwargs) -> CompositeCurve:
    """Return a CompositeCurve for an axis-aligned rectangle."""

    max_x = min_x + width
    max_y = min_y + height
    points = [
        (min_x, min_y),
        (max_x, min_y),
        (max_x, max_y),
        (min_x, max_y),
    ]
    segments = [
        make_line_segment(points[i], points[(i + 1) % 4])
        for i in range(4)
    ]
    return CompositeCurve(segments, **kwargs)


def composite_perimeter(composite: CompositeCurve) -> float:
    total = 0.0
    for segment in composite.segments:
        endpoints = getattr(segment, "get_endpoints", lambda: [])()
        if len(endpoints) != 2:
            raise ValueError("Segment missing endpoints for perimeter computation")
        (x0, y0), (x1, y1) = endpoints
        total += math.hypot(x1 - x0, y1 - y0)
    return total
