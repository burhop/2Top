from __future__ import annotations

from typing import List, Tuple, Optional
import sympy as sp
import numpy as np

from .composite_curve import CompositeCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from .conic_section import ConicSection
from .polynomial_curve import PolynomialCurve


def create_polygon_from_edges(
    points: List[Tuple[float, float]],
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a polygonal CompositeCurve from an ordered list of vertices.

    - Builds line `PolynomialCurve` edges between consecutive points (closing the loop).
    - Each edge is wrapped in a `TrimmedImplicitCurve` with a mask restricting to the segment.
    - If the polygon is convex, attaches specialized max-based evaluation via `_convex_edges_abc`.
    - Stores `_polygon_vertices` for visualization and serialization.
    """
    if not points or len(points) < 3:
        raise ValueError("Polygon must have at least 3 vertices")

    # Normalize to floats
    pts: List[Tuple[float, float]] = [(float(p[0]), float(p[1])) for p in points]
    # If explicitly closed by repeating the first vertex at the end, drop the duplicate last
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    # Require at least three vertices overall and at least three unique vertices
    if len(pts) < 3 or len({(px, py) for (px, py) in pts}) < 3:
        raise ValueError("Polygon must have at least 3 unique vertices")
    for (px, py) in pts:
        if not (np.isfinite(px) and np.isfinite(py)):
            raise ValueError("Polygon vertices must be finite numbers")

    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    def edge_halfspace(p0: Tuple[float, float], p1: Tuple[float, float], outward_normal: Tuple[float, float]):
        (x0, y0), (x1, y1) = p0, p1
        a, b = outward_normal
        norm = (a * a + b * b) ** 0.5
        if norm == 0:
            # Degenerate edge, skip with huge c so it's inactive
            expr = x + y + 1e9
            return expr, (0.0, 0.0, 1e9)
        a /= norm
        b /= norm
        c = -(a * x0 + b * y0)
        expr = a * x + b * y + c
        return expr, (a, b, c)

    segments: List[TrimmedImplicitCurve] = []
    edges_abc: List[Tuple[float, float, float]] = []

    def signed_area(seq: List[Tuple[float, float]]):
        A = 0.0
        for i in range(len(seq)):
            x0, y0 = seq[i]
            x1, y1 = seq[(i + 1) % len(seq)]
            A += x0 * y1 - x1 * y0
        return 0.5 * A

    area = signed_area(pts)
    if abs(area) <= 1e-15:
        raise ValueError("Degenerate polygon: vertices are collinear or area is zero")
    ccw = area > 0

    def is_convex(seq: List[Tuple[float, float]], ccw_flag: bool) -> bool:
        n = len(seq)
        prev_sign = 0
        for i in range(n):
            x0, y0 = seq[i]
            x1, y1 = seq[(i + 1) % n]
            x2, y2 = seq[(i + 2) % n]
            dx1, dy1 = x1 - x0, y1 - y0
            dx2, dy2 = x2 - x1, y2 - y1
            cross = dx1 * dy2 - dy1 * dx2
            s = 1 if cross > 0 else (-1 if cross < 0 else 0)
            if s != 0:
                if prev_sign == 0:
                    prev_sign = s
                elif s != prev_sign:
                    return False
        return True

    is_convex_poly = is_convex(pts, ccw)

    for i in range(len(pts)):
        p0 = pts[i]
        p1 = pts[(i + 1) % len(pts)]
        x0, y0 = p0
        x1, y1 = p1
        dx = x1 - x0
        dy = y1 - y0
        if dx == 0 and dy == 0:
            raise ValueError("Degenerate polygon: zero-length edge detected")
        # Outward normal: for CCW polygon, outward is (dy, -dx); for CW: (-dy, dx)
        n_out = (dy, -dx) if ccw else (-dy, dx)

        # Build line half-space expression and coefficients
        expr, abc = edge_halfspace(p0, p1, n_out)

        base_line = PolynomialCurve(expr, variables)

        # Segment mask via parameter t projection
        denom = dx * dx + dy * dy if (dx != 0 or dy != 0) else 1.0
        def mask_fn(X, Y, x0=x0, y0=y0, dx=dx, dy=dy, denom=denom):
            t = ((X - x0) * dx + (Y - y0) * dy) / denom
            return (t >= -1e-9) and (t <= 1 + 1e-9)

        xmin, xmax = (x0, x1) if x0 <= x1 else (x1, x0)
        ymin, ymax = (y0, y1) if y0 <= y1 else (y1, y0)

        seg = TrimmedImplicitCurve(
            base_line,
            mask_fn,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            endpoints=[p0, p1],
        )
        segments.append(seg)
        a, b, c = abc
        edges_abc.append((float(a), float(b), float(c)))

    polygon_curve = CompositeCurve(segments, variables)

    if is_convex_poly:
        polygon_curve._is_convex_polygon = True
        polygon_curve._convex_edges_abc = edges_abc
    polygon_curve._polygon_vertices = [(float(px), float(py)) for (px, py) in pts]

    return polygon_curve


ess = Tuple[float, float]


def create_square_from_edges(
    corner1: ess = (0.0, 0.0),
    corner2: ess = (1.0, 1.0),
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a square from four edge segments defined by two opposite corners.
    Marks the resulting `CompositeCurve` with `_is_square` and `_square_bounds` metadata.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    x1, y1 = corner1
    x2, y2 = corner2
    xmin, xmax = (x1, x2) if x1 <= x2 else (x2, x1)
    ymin, ymax = (y1, y2) if y1 <= y2 else (y2, y1)

    # Lines: x = xmin, x = xmax, y = ymin, y = ymax
    right_line = PolynomialCurve(x - xmax, variables)
    top_line = PolynomialCurve(y - ymax, variables)
    left_line = PolynomialCurve(x - xmin, variables)
    bottom_line = PolynomialCurve(y - ymin, variables)

    eps = 1e-6
    segments = [
        # Right edge: x = xmax, y in [ymin, ymax]
        TrimmedImplicitCurve(right_line, lambda X, Y, xmax=xmax, ymin=ymin, ymax=ymax, e=eps: (Y >= ymin - e) and (Y <= ymax + e) and (abs(X - xmax) <= e)),
        # Top edge: y = ymax, x in [xmin, xmax]
        TrimmedImplicitCurve(top_line, lambda X, Y, ymax=ymax, xmin=xmin, xmax=xmax, e=eps: (X >= xmin - e) and (X <= xmax + e) and (abs(Y - ymax) <= e)),
        # Left edge: x = xmin, y in [ymin, ymax]
        TrimmedImplicitCurve(left_line, lambda X, Y, xmin=xmin, ymin=ymin, ymax=ymax, e=eps: (Y >= ymin - e) and (Y <= ymax + e) and (abs(X - xmin) <= e)),
        # Bottom edge: y = ymin, x in [xmin, xmax]
        TrimmedImplicitCurve(bottom_line, lambda X, Y, ymin=ymin, xmin=xmin, xmax=xmax, e=eps: (X >= xmin - e) and (X <= xmax + e) and (abs(Y - ymin) <= e)),
    ]

    square_curve = CompositeCurve(segments, variables)
    square_curve._is_square = True
    square_curve._square_bounds = (xmin, xmax, ymin, ymax)
    return square_curve


def create_circle_from_quarters(
    center: ess = (0.0, 0.0),
    radius: float = 1.0,
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a complete circle from four quarter-circle segments.

    This implementation lives here to avoid circular dependencies and keep
    construction logic isolated from core composite behavior.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    cx, cy = center
    circle_expr = (x - cx) ** 2 + (y - cy) ** 2 - radius ** 2
    circle = ConicSection(circle_expr, variables)

    segments = [
        TrimmedImplicitCurve(circle, lambda X, Y, cx=cx, cy=cy: (X >= cx) and (Y >= cy)),
        TrimmedImplicitCurve(circle, lambda X, Y, cx=cx, cy=cy: (X <= cx) and (Y >= cy)),
        TrimmedImplicitCurve(circle, lambda X, Y, cx=cx, cy=cy: (X <= cx) and (Y <= cy)),
        TrimmedImplicitCurve(circle, lambda X, Y, cx=cx, cy=cy: (X >= cx) and (Y <= cy)),
    ]

    return CompositeCurve(segments, variables)
