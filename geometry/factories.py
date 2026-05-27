from __future__ import annotations

from typing import List, Tuple, Optional
import sympy as sp
import numpy as np

from .composite_curve import CompositeCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from .conic_section import ConicSection
from .polynomial_curve import PolynomialCurve
from .superellipse import Superellipse


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
    for px, py in pts:
        if not (np.isfinite(px) and np.isfinite(py)):
            raise ValueError("Polygon vertices must be finite numbers")

    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    def edge_halfspace(
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        outward_normal: Tuple[float, float],
    ):
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
    Creates a continuous path with proper endpoint connectivity.
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

    # Square corners in order (counter-clockwise)
    corners = [
        (xmin, ymin),  # Bottom-left
        (xmax, ymin),  # Bottom-right
        (xmax, ymax),  # Top-right
        (xmin, ymax),  # Top-left
    ]

    # Lines: x = xmin, x = xmax, y = ymin, y = ymax
    bottom_line = PolynomialCurve(y - ymin, variables)
    right_line = PolynomialCurve(x - xmax, variables)
    top_line = PolynomialCurve(y - ymax, variables)
    left_line = PolynomialCurve(x - xmin, variables)

    eps = 0.02  # Further increased tolerance for more robust plotting
    segments = [
        # Bottom edge: from (xmin, ymin) to (xmax, ymin)
        TrimmedImplicitCurve(
            bottom_line,
            lambda X, Y, ymin=ymin, xmin=xmin, xmax=xmax, e=eps: (X >= xmin - e)
            and (X <= xmax + e)
            and (abs(Y - ymin) <= e),
            endpoints=[(xmin, ymin), (xmax, ymin)],
        ),
        # Right edge: from (xmax, ymin) to (xmax, ymax)
        TrimmedImplicitCurve(
            right_line,
            lambda X, Y, xmax=xmax, ymin=ymin, ymax=ymax, e=eps: (Y >= ymin - e)
            and (Y <= ymax + e)
            and (abs(X - xmax) <= e),
            endpoints=[(xmax, ymin), (xmax, ymax)],
        ),
        # Top edge: from (xmax, ymax) to (xmin, ymax)
        TrimmedImplicitCurve(
            top_line,
            lambda X, Y, ymax=ymax, xmin=xmin, xmax=xmax, e=eps: (X >= xmin - e)
            and (X <= xmax + e)
            and (abs(Y - ymax) <= e),
            endpoints=[(xmax, ymax), (xmin, ymax)],
        ),
        # Left edge: from (xmin, ymax) to (xmin, ymin)
        TrimmedImplicitCurve(
            left_line,
            lambda X, Y, xmin=xmin, ymin=ymin, ymax=ymax, e=eps: (Y >= ymin - e)
            and (Y <= ymax + e)
            and (abs(X - xmin) <= e),
            endpoints=[(xmin, ymax), (xmin, ymin)],
        ),
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
    Create a complete circle from four quarter-circle segments with proper endpoints.

    This implementation lives here to avoid circular dependencies and keep
    construction logic isolated from core composite behavior.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    cx, cy = center
    circle_expr = (x - cx) ** 2 + (y - cy) ** 2 - radius**2
    circle = ConicSection(circle_expr, variables)

    # Define endpoints for each quarter (going counter-clockwise)
    # Q1: First quadrant (X >= cx, Y >= cy) - from (cx+r, cy) to (cx, cy+r)
    # Q2: Second quadrant (X <= cx, Y >= cy) - from (cx, cy+r) to (cx-r, cy)
    # Q3: Third quadrant (X <= cx, Y <= cy) - from (cx-r, cy) to (cx, cy-r)
    # Q4: Fourth quadrant (X >= cx, Y <= cy) - from (cx, cy-r) to (cx+r, cy)

    segments = [
        TrimmedImplicitCurve(
            circle,
            lambda X, Y, cx=cx, cy=cy: (X >= cx) and (Y >= cy),
            endpoints=[(cx + radius, cy), (cx, cy + radius)],
        ),
        TrimmedImplicitCurve(
            circle,
            lambda X, Y, cx=cx, cy=cy: (X <= cx) and (Y >= cy),
            endpoints=[(cx, cy + radius), (cx - radius, cy)],
        ),
        TrimmedImplicitCurve(
            circle,
            lambda X, Y, cx=cx, cy=cy: (X <= cx) and (Y <= cy),
            endpoints=[(cx - radius, cy), (cx, cy - radius)],
        ),
        TrimmedImplicitCurve(
            circle,
            lambda X, Y, cx=cx, cy=cy: (X >= cx) and (Y <= cy),
            endpoints=[(cx, cy - radius), (cx + radius, cy)],
        ),
    ]

    return CompositeCurve(segments, variables)


def create_L_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create an L-shape from two connected line segments.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Vertical line: x = -0.5, y from -1 to 0
    vertical = PolynomialCurve(x + 0.5, variables)
    def vertical_mask(x_val, y_val):
        return (-0.65 <= x_val <= -0.35) and (-1.05 <= y_val <= 0.05)  # Increased tolerance
    vertical_segment = TrimmedImplicitCurve(
        vertical, vertical_mask, endpoints=[(-0.5, -1), (-0.5, 0)]
    )

    # Horizontal line: y = -1, x from -0.5 to 0.5
    horizontal = PolynomialCurve(y + 1, variables)
    def horizontal_mask(x_val, y_val):
        return (-0.55 <= x_val <= 0.55) and (-1.15 <= y_val <= -0.85)  # Increased tolerance
    horizontal_segment = TrimmedImplicitCurve(
        horizontal, horizontal_mask, endpoints=[(-0.5, -1), (0.5, -1)]
    )

    return CompositeCurve(
        [vertical_segment, horizontal_segment], validate_continuity=True
    )


def create_T_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a T-shape from connected line segments forming a continuous path.
    This replaces the plus sign with a truly continuous curve.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []

    # Horizontal top: y = 0.5, x from -1 to 0 (left part)
    horizontal_left = PolynomialCurve(y - 0.5, variables)
    def horizontal_left_mask(x_val, y_val):
        return (-1.05 <= x_val <= 0.05) and (0.35 <= y_val <= 0.65)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(
            horizontal_left, horizontal_left_mask, endpoints=[(-1, 0.5), (0, 0.5)]
        )
    )

    # Vertical stem: x = 0, y from 0.5 to -1
    vertical = PolynomialCurve(x, variables)
    def vertical_mask(x_val, y_val):
        return (-0.15 <= x_val <= 0.15) and (-1.05 <= y_val <= 0.55)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(vertical, vertical_mask, endpoints=[(0, 0.5), (0, -1)])
    )

    # Horizontal top: y = 0.5, x from 0 to 1 (right part)
    horizontal_right = PolynomialCurve(y - 0.5, variables)
    def horizontal_right_mask(x_val, y_val):
        return (-0.05 <= x_val <= 1.05) and (0.35 <= y_val <= 0.65)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(
            horizontal_right, horizontal_right_mask, endpoints=[(0, 0.5), (1, 0.5)]
        )
    )

    return CompositeCurve(segments, validate_continuity=True)


def create_triangle(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a triangle from three connected line segments.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Bottom edge: y = -0.5, x from -1 to 1
    bottom = PolynomialCurve(y + 0.5, variables)
    def bottom_mask(x_val, y_val):
        return (-1.05 <= x_val <= 1.05) and (-0.65 <= y_val <= -0.35)  # Increased tolerance
    bottom_segment = TrimmedImplicitCurve(
        bottom, bottom_mask, endpoints=[(-1, -0.5), (1, -0.5)]
    )

    # Right edge: from (1, -0.5) to (0, 1)
    # slope = (1 - (-0.5)) / (0 - 1) = -1.5
    # y - (-0.5) = -1.5(x - 1) => y = -1.5x + 1
    right = PolynomialCurve(y + 1.5 * x - 1, variables)
    def right_mask(x_val, y_val):
        return (-0.05 <= x_val <= 1.05) and (-0.55 <= y_val <= 1.05)  # Increased tolerance
    right_segment = TrimmedImplicitCurve(
        right, right_mask, endpoints=[(1, -0.5), (0, 1)]
    )

    # Left edge: from (0, 1) to (-1, -0.5)
    # slope = (-0.5 - 1) / (-1 - 0) = 1.5
    # y - 1 = 1.5(x - 0) => y = 1.5x + 1
    left = PolynomialCurve(y - 1.5 * x - 1, variables)
    def left_mask(x_val, y_val):
        return (-1.05 <= x_val <= 0.05) and (-0.55 <= y_val <= 1.05)  # Increased tolerance
    left_segment = TrimmedImplicitCurve(left, left_mask, endpoints=[(0, 1), (-1, -0.5)])

    return CompositeCurve(
        [bottom_segment, right_segment, left_segment], validate_continuity=True
    )


def create_house_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a house shape (square base + triangle roof) from connected line segments.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Square base + triangle roof, all connected
    segments = []

    # Bottom: y = -1, x from -0.5 to 0.5
    bottom = PolynomialCurve(y + 1, variables)
    def bottom_mask(x_val, y_val):
        return (-0.55 <= x_val <= 0.55) and (-1.15 <= y_val <= -0.85)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(bottom, bottom_mask, endpoints=[(-0.5, -1), (0.5, -1)])
    )

    # Right: x = 0.5, y from -1 to 0
    right = PolynomialCurve(x - 0.5, variables)
    def right_mask(x_val, y_val):
        return (0.35 <= x_val <= 0.65) and (-1.05 <= y_val <= 0.05)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(right, right_mask, endpoints=[(0.5, -1), (0.5, 0)])
    )

    # Roof right: from (0.5, 0) to (0, 0.5)
    roof_right = PolynomialCurve(y + x - 0.5, variables)
    def roof_right_mask(x_val, y_val):
        return (-0.05 <= x_val <= 0.55) and (-0.05 <= y_val <= 0.55)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(
            roof_right, roof_right_mask, endpoints=[(0.5, 0), (0, 0.5)]
        )
    )

    # Roof left: from (0, 0.5) to (-0.5, 0)
    roof_left = PolynomialCurve(y - x - 0.5, variables)
    def roof_left_mask(x_val, y_val):
        return (-0.55 <= x_val <= 0.05) and (-0.05 <= y_val <= 0.55)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(roof_left, roof_left_mask, endpoints=[(0, 0.5), (-0.5, 0)])
    )

    # Left: x = -0.5, y from 0 to -1
    left = PolynomialCurve(x + 0.5, variables)
    def left_mask(x_val, y_val):
        return (-0.65 <= x_val <= -0.35) and (-1.05 <= y_val <= 0.05)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(left, left_mask, endpoints=[(-0.5, 0), (-0.5, -1)])
    )

    return CompositeCurve(segments, validate_continuity=True)


def create_zigzag_pattern(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a zigzag pattern from connected line segments forming a continuous path.
    This replaces the cross pattern with a truly continuous curve.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []

    # Segment 1: from (-1, -0.5) to (0, 0.5) - diagonal up
    # Line equation: y - (-0.5) = 1(x - (-1)) => y = x + 0.5
    seg1 = PolynomialCurve(y - x - 0.5, variables)
    def seg1_mask(x_val, y_val):
        return (-1.05 <= x_val <= 0.05) and (-0.55 <= y_val <= 0.55)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(seg1, seg1_mask, endpoints=[(-1, -0.5), (0, 0.5)])
    )

    # Segment 2: from (0, 0.5) to (1, -0.5) - diagonal down
    # Line equation: y - 0.5 = -1(x - 0) => y = -x + 0.5
    seg2 = PolynomialCurve(y + x - 0.5, variables)
    def seg2_mask(x_val, y_val):
        return (-0.05 <= x_val <= 1.05) and (-0.55 <= y_val <= 0.55)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(seg2, seg2_mask, endpoints=[(0, 0.5), (1, -0.5)])
    )

    return CompositeCurve(segments, validate_continuity=True)


def create_staircase(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a staircase pattern from connected horizontal and vertical segments.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []

    # Step 1: horizontal from (-1, -1) to (-0.5, -1)
    h1 = PolynomialCurve(y + 1, variables)
    def h1_mask(x_val, y_val):
        return (-1.05 <= x_val <= -0.45) and (-1.15 <= y_val <= -0.85)  # Increased tolerance
    segments.append(TrimmedImplicitCurve(h1, h1_mask, endpoints=[(-1, -1), (-0.5, -1)]))

    # Step 1: vertical from (-0.5, -1) to (-0.5, -0.5)
    v1 = PolynomialCurve(x + 0.5, variables)
    def v1_mask(x_val, y_val):
        return (-0.65 <= x_val <= -0.35) and (-1.05 <= y_val <= -0.45)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(v1, v1_mask, endpoints=[(-0.5, -1), (-0.5, -0.5)])
    )

    # Step 2: horizontal from (-0.5, -0.5) to (0, -0.5)
    h2 = PolynomialCurve(y + 0.5, variables)
    def h2_mask(x_val, y_val):
        return (-0.55 <= x_val <= 0.05) and (-0.65 <= y_val <= -0.35)  # Increased tolerance
    segments.append(
        TrimmedImplicitCurve(h2, h2_mask, endpoints=[(-0.5, -0.5), (0, -0.5)])
    )

    # Step 2: vertical from (0, -0.5) to (0, 0)
    v2 = PolynomialCurve(x, variables)
    def v2_mask(x_val, y_val):
        return (-0.15 <= x_val <= 0.15) and (-0.55 <= y_val <= 0.05)  # Increased tolerance
    segments.append(TrimmedImplicitCurve(v2, v2_mask, endpoints=[(0, -0.5), (0, 0)]))

    # Step 3: horizontal from (0, 0) to (0.5, 0)
    h3 = PolynomialCurve(y, variables)
    def h3_mask(x_val, y_val):
        return (-0.05 <= x_val <= 0.55) and (-0.15 <= y_val <= 0.15)  # Increased tolerance
    segments.append(TrimmedImplicitCurve(h3, h3_mask, endpoints=[(0, 0), (0.5, 0)]))

    # Step 3: vertical from (0.5, 0) to (0.5, 0.5)
    v3 = PolynomialCurve(x - 0.5, variables)
    def v3_mask(x_val, y_val):
        return (0.35 <= x_val <= 0.65) and (-0.05 <= y_val <= 0.55)  # Increased tolerance
    segments.append(TrimmedImplicitCurve(v3, v3_mask, endpoints=[(0.5, 0), (0.5, 0.5)]))

    return CompositeCurve(segments, validate_continuity=True)


def create_figure_eight(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a figure-eight shape from connected circular arcs forming a continuous closed path.
    This replaces the disconnected semicircles with a truly continuous curve.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []
    radius = 0.5
    tolerance = 0.05  # Increased tolerance for better connectivity

    # Upper circle: x^2 + (y - 0.5)^2 = 0.25
    upper_circle = ConicSection(x**2 + (y - 0.5) ** 2 - radius**2, variables)

    # Upper circle - right half (x >= 0)
    upper_right = TrimmedImplicitCurve(
        upper_circle,
        lambda x_val, y_val, r=radius, tol=tolerance: (x_val >= -tol)
        and (x_val**2 + (y_val - 0.5) ** 2 <= (r + tol) ** 2),
        endpoints=[(0, 0), (0, 1)],  # From center crossing to top
    )
    segments.append(upper_right)

    # Upper circle - left half (x <= 0)
    upper_left = TrimmedImplicitCurve(
        upper_circle,
        lambda x_val, y_val, r=radius, tol=tolerance: (x_val <= tol)
        and (x_val**2 + (y_val - 0.5) ** 2 <= (r + tol) ** 2),
        endpoints=[(0, 1), (0, 0)],  # From top back to center crossing
    )
    segments.append(upper_left)

    # Lower circle: x^2 + (y + 0.5)^2 = 0.25
    lower_circle = ConicSection(x**2 + (y + 0.5) ** 2 - radius**2, variables)

    # Lower circle - left half (x <= 0)
    lower_left = TrimmedImplicitCurve(
        lower_circle,
        lambda x_val, y_val, r=radius, tol=tolerance: (x_val <= tol)
        and (x_val**2 + (y_val + 0.5) ** 2 <= (r + tol) ** 2),
        endpoints=[(0, 0), (0, -1)],  # From center crossing to bottom
    )
    segments.append(lower_left)

    # Lower circle - right half (x >= 0)
    lower_right = TrimmedImplicitCurve(
        lower_circle,
        lambda x_val, y_val, r=radius, tol=tolerance: (x_val >= -tol)
        and (x_val**2 + (y_val + 0.5) ** 2 <= (r + tol) ** 2),
        endpoints=[(0, -1), (0, 0)],  # From bottom back to center crossing
    )
    segments.append(lower_right)

    return CompositeCurve(
        segments, validate_continuity=False
    )  # Disable strict validation due to complex geometry


# Mixed Implicit Curve Composite Factories


def create_circle_line_hybrid(
    center: Tuple[float, float] = (0, 0),
    radius: float = 1.0,
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a hybrid shape combining a semicircle with straight line segments.
    Forms a D-shape (semicircle + straight edge).
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    cx, cy = center

    # Right semicircle: (x - cx)^2 + (y - cy)^2 = r^2, x >= cx
    circle = ConicSection((x - cx) ** 2 + (y - cy) ** 2 - radius**2, variables)
    semicircle = TrimmedImplicitCurve(
        circle,
        lambda x_val, y_val, cx=cx, cy=cy, r=radius: (x_val >= cx - 0.05)
        and (
            (x_val - cx) ** 2 + (y_val - cy) ** 2 <= (r + 0.1) ** 2
        ),  # Increased tolerance
        endpoints=[(cx, cy - radius), (cx, cy + radius)],
    )

    # Straight line closing the D: x = cx, y from cy+r to cy-r
    line = PolynomialCurve(x - cx, variables)
    line_segment = TrimmedImplicitCurve(
        line,
        lambda x_val, y_val, cx=cx, cy=cy, r=radius: (cx - 0.15 <= x_val <= cx + 0.15)
        and (cy - r - 0.05 <= y_val <= cy + r + 0.05),  # Increased tolerance
        endpoints=[(cx, cy + radius), (cx, cy - radius)],
    )

    return CompositeCurve([semicircle, line_segment], validate_continuity=True)


def create_ellipse_parabola_hybrid(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a hybrid shape combining an ellipse arc with a parabola arc.
    Forms an egg-like or teardrop shape with ellipse at bottom and parabola at top.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # The ellipse x²/4 + y² = 1 intersects y = x²/4 where:
    # x²/4 + (x²/4)² = 1
    # x²/4 + x⁴/16 = 1
    # Let u = x²/4, then u + u² = 1, so u² + u - 1 = 0
    # u = (-1 + √5)/2 ≈ 0.618
    # So x² = 4u ≈ 2.472, x ≈ ±1.571
    # And y = x²/4 = u ≈ 0.618

    intersection_x = np.sqrt(2 * (-1 + np.sqrt(5)))  # ≈ 1.571
    intersection_y = (-1 + np.sqrt(5)) / 2  # ≈ 0.618

    # Lower half of ellipse: x²/4 + y² = 1, y <= intersection_y
    ellipse = ConicSection(x**2 / 4 + y**2 - 1, variables)
    ellipse_lower = TrimmedImplicitCurve(
        ellipse,
        lambda x_val, y_val, iy=intersection_y: (y_val <= iy + 0.05)
        and (x_val**2 / 4 + y_val**2 <= 1.2),
        endpoints=[(-intersection_x, intersection_y), (intersection_x, intersection_y)],
    )

    # Parabola top: y = x²/4, connecting the intersection points
    parabola = PolynomialCurve(y - x**2 / 4, variables)
    parabola_upper = TrimmedImplicitCurve(
        parabola,
        lambda x_val, y_val, ix=intersection_x, iy=intersection_y: (
            -ix - 0.1 <= x_val <= ix + 0.1
        )
        and (iy - 0.05 <= y_val <= 1.2),
        endpoints=[(intersection_x, intersection_y), (-intersection_x, intersection_y)],
    )

    return CompositeCurve([ellipse_lower, parabola_upper], validate_continuity=False)


def create_multi_conic_flower(
    petals: int = 6, variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None
) -> CompositeCurve:
    """
    Create a flower shape using different conic sections for each petal.
    Alternates between circles, ellipses, and parabolas.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []
    petal_radius = 0.8

    for i in range(petals):
        angle = i * 2 * np.pi / petals
        center_x = petal_radius * np.cos(angle)
        center_y = petal_radius * np.sin(angle)

        # Alternate curve types
        curve_type = i % 3

        if curve_type == 0:
            # Circle petal
            curve = ConicSection(
                (x - center_x) ** 2 + (y - center_y) ** 2 - 0.16, variables
            )
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y: (x_val - cx) ** 2
                + (y_val - cy) ** 2
                <= 0.17
            )

        elif curve_type == 1:
            # Ellipse petal (stretched toward center)
            # Rotate ellipse to point toward center
            cos_a, sin_a = np.cos(angle + np.pi), np.sin(angle + np.pi)
            a, b = 0.5, 0.2
            curve_expr = (
                ((x - center_x) * cos_a + (y - center_y) * sin_a) ** 2 / a**2
                + ((-(x - center_x) * sin_a + (y - center_y) * cos_a) ** 2 / b**2)
                - 1
            )
            curve = ConicSection(curve_expr, variables)
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y: (x_val - cx) ** 2
                + (y_val - cy) ** 2
                <= 0.3
            )

        else:
            # Parabola petal (opening toward center)
            # Simplified: use a small circle for now (parabola rotation is complex)
            curve = ConicSection(
                (x - center_x) ** 2 + (y - center_y) ** 2 - 0.09, variables
            )
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y: (x_val - cx) ** 2
                + (y_val - cy) ** 2
                <= 0.1
            )

        # Create petal segment (not continuous between petals - this is decorative)
        segment = TrimmedImplicitCurve(curve, mask)
        segments.append(segment)

    # Note: Flower petals are typically not continuous, so disable validation
    return CompositeCurve(segments, validate_continuity=False)


def create_superellipse_circle_hybrid(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a hybrid combining a superellipse with circular arcs.
    Forms a rounded square with circular corners.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Main superellipse body (square-like with n=4)
    superellipse = Superellipse(1, 1, 4, variables)

    # Use the right half of the superellipse
    superellipse_right = TrimmedImplicitCurve(
        superellipse,
        lambda x_val, y_val: (x_val >= -0.05)
        and (abs(x_val) ** 4 + abs(y_val) ** 4 <= 1.15),  # Increased tolerance
        endpoints=[(0, -1), (0, 1)],
    )

    # Connect with a circular arc on the left
    circle = ConicSection((x + 0.5) ** 2 + y**2 - 1.25, variables)
    circle_left = TrimmedImplicitCurve(
        circle,
        lambda x_val, y_val: (x_val <= 0.05)
        and ((x_val + 0.5) ** 2 + y_val**2 <= 1.4),  # Increased tolerance
        endpoints=[(0, 1), (0, -1)],
    )

    return CompositeCurve([superellipse_right, circle_left], validate_continuity=True)


def create_spiral_approximation(
    turns: int = 3, variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None
) -> CompositeCurve:
    """
    Create a spiral approximation using connected circular arcs of decreasing radius.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    segments = []
    segments_per_turn = 4  # Quarter circles
    total_segments = turns * segments_per_turn

    centers = []
    radii = []

    for i in range(total_segments):
        # Decreasing radius
        radius = 1.0 * (1 - i / (total_segments * 1.2))

        # Determine quadrant
        quadrant = i % 4

        if i == 0:
            center_x = 0.0
            center_y = 0.0
        else:
            prev_cx, prev_cy = centers[-1]
            prev_r = radii[-1]
            if quadrant == 1:
                center_x = prev_cx
                center_y = prev_cy + prev_r - radius
            elif quadrant == 2:
                center_x = prev_cx - prev_r + radius
                center_y = prev_cy
            elif quadrant == 3:
                center_x = prev_cx
                center_y = prev_cy - prev_r + radius
            else:  # quadrant == 0
                center_x = prev_cx + prev_r - radius
                center_y = prev_cy

        centers.append((center_x, center_y))
        radii.append(radius)

        # Quarter circle
        circle = ConicSection(
            (x - center_x) ** 2 + (y - center_y) ** 2 - radius**2, variables
        )

        if quadrant == 0:  # First quadrant
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y, r=radius: (x_val >= cx)
                and (y_val >= cy)
                and ((x_val - cx) ** 2 + (y_val - cy) ** 2 <= (r + 0.1) ** 2)
            )
            endpoints = [(center_x + radius, center_y), (center_x, center_y + radius)]
        elif quadrant == 1:  # Second quadrant
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y, r=radius: (x_val <= cx)
                and (y_val >= cy)
                and ((x_val - cx) ** 2 + (y_val - cy) ** 2 <= (r + 0.1) ** 2)
            )
            endpoints = [(center_x, center_y + radius), (center_x - radius, center_y)]
        elif quadrant == 2:  # Third quadrant
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y, r=radius: (x_val <= cx)
                and (y_val <= cy)
                and ((x_val - cx) ** 2 + (y_val - cy) ** 2 <= (r + 0.1) ** 2)
            )
            endpoints = [(center_x - radius, center_y), (center_x, center_y - radius)]
        else:  # Fourth quadrant
            mask = (
                lambda x_val, y_val, cx=center_x, cy=center_y, r=radius: (x_val >= cx)
                and (y_val <= cy)
                and ((x_val - cx) ** 2 + (y_val - cy) ** 2 <= (r + 0.1) ** 2)
            )
            endpoints = [(center_x, center_y - radius), (center_x + radius, center_y)]

        segment = TrimmedImplicitCurve(circle, mask, endpoints=endpoints)
        segments.append(segment)

    return CompositeCurve(segments, validate_continuity=True)


def create_heart_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a heart shape using two circular arcs and a parabolic bottom.
    Uses a simpler design with better endpoint matching.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Simplified heart design:
    # Two half-circles at top meeting at (0, 0.5)
    # Parabola at bottom from (-1, 0) through (0, -1) to (1, 0)

    # Left circle: (x + 0.5)² + (y - 0.25)² = 0.25, center (-0.5, 0.25), radius 0.5
    left_circle = ConicSection((x + 0.5) ** 2 + (y - 0.25) ** 2 - 0.25, variables)
    left_lobe = TrimmedImplicitCurve(
        left_circle,
        lambda x_val, y_val: (x_val >= -1.05)
        and (y_val >= -0.05)
        and ((x_val + 0.5) ** 2 + (y_val - 0.25) ** 2 <= 0.35),
        endpoints=[(-1, 0), (0, 0.5)],  # From left bottom to top center
    )

    # Right circle: (x - 0.5)² + (y - 0.25)² = 0.25, center (0.5, 0.25), radius 0.5
    right_circle = ConicSection((x - 0.5) ** 2 + (y - 0.25) ** 2 - 0.25, variables)
    right_lobe = TrimmedImplicitCurve(
        right_circle,
        lambda x_val, y_val: (x_val <= 1.05)
        and (y_val >= -0.05)
        and ((x_val - 0.5) ** 2 + (y_val - 0.25) ** 2 <= 0.35),
        endpoints=[(0, 0.5), (1, 0)],  # From top center to right bottom
    )

    # Bottom parabola: y = x² - 1 (vertex at (0, -1))
    parabola = PolynomialCurve(y - x**2 + 1, variables)
    heart_bottom = TrimmedImplicitCurve(
        parabola,
        lambda x_val, y_val: (-1.1 <= x_val <= 1.1) and (-1.2 <= y_val <= 0.1),
        endpoints=[(1, 0), (-1, 0)],  # From right to left
    )

    return CompositeCurve(
        [left_lobe, right_lobe, heart_bottom], validate_continuity=False
    )

    return CompositeCurve(
        [left_lobe, right_lobe, heart_bottom], validate_continuity=False
    )


def create_robust_square(
    corner1: Tuple[float, float] = (0.0, 0.0),
    corner2: Tuple[float, float] = (1.0, 1.0),
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a robust square with improved segment connectivity and plotting.
    Uses larger tolerances and better mask functions for reliable visualization.
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

    # Use larger tolerance for robust plotting
    tol = max(0.05, (xmax - xmin) * 0.05, (ymax - ymin) * 0.05)

    # Create line equations
    bottom_line = PolynomialCurve(y - ymin, variables)
    right_line = PolynomialCurve(x - xmax, variables)
    top_line = PolynomialCurve(y - ymax, variables)
    left_line = PolynomialCurve(x - xmin, variables)

    segments = [
        # Bottom edge: from (xmin, ymin) to (xmax, ymin)
        TrimmedImplicitCurve(
            bottom_line,
            lambda X, Y, xmin=xmin, xmax=xmax, ymin=ymin, t=tol: (X >= xmin - t)
            and (X <= xmax + t)
            and (abs(Y - ymin) <= t),
            endpoints=[(xmin, ymin), (xmax, ymin)],
        ),
        # Right edge: from (xmax, ymin) to (xmax, ymax)
        TrimmedImplicitCurve(
            right_line,
            lambda X, Y, xmax=xmax, ymin=ymin, ymax=ymax, t=tol: (Y >= ymin - t)
            and (Y <= ymax + t)
            and (abs(X - xmax) <= t),
            endpoints=[(xmax, ymin), (xmax, ymax)],
        ),
        # Top edge: from (xmax, ymax) to (xmin, ymax)
        TrimmedImplicitCurve(
            top_line,
            lambda X, Y, xmin=xmin, xmax=xmax, ymax=ymax, t=tol: (X >= xmin - t)
            and (X <= xmax + t)
            and (abs(Y - ymax) <= t),
            endpoints=[(xmax, ymax), (xmin, ymax)],
        ),
        # Left edge: from (xmin, ymax) to (xmin, ymin)
        TrimmedImplicitCurve(
            left_line,
            lambda X, Y, xmin=xmin, ymin=ymin, ymax=ymax, t=tol: (Y >= ymin - t)
            and (Y <= ymax + t)
            and (abs(X - xmin) <= t),
            endpoints=[(xmin, ymax), (xmin, ymin)],
        ),
    ]

    square_curve = CompositeCurve(segments, variables)
    square_curve._is_square = True
    square_curve._square_bounds = (xmin, xmax, ymin, ymax)
    square_curve._is_robust_square = True  # Mark as robust version
    return square_curve


def create_lens_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a lens shape using two intersecting circular arcs.
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)
    else:
        x, y = variables

    # Calculate intersection points for two circles: (x+0.5)^2 + y^2 = 1 and (x-0.5)^2 + y^2 = 1
    # At intersection: x = 0, y = ±√3/2
    intersection_y = np.sqrt(3) / 2

    # Left circle arc (right half of left circle)
    left_circle = ConicSection((x + 0.5) ** 2 + y**2 - 1, variables)
    left_arc = TrimmedImplicitCurve(
        left_circle,
        lambda x_val, y_val: (x_val >= -0.05)
        and ((x_val + 0.5) ** 2 + y_val**2 <= 1.2),  # Right half with tolerance
        endpoints=[(0, intersection_y), (0, -intersection_y)],
    )

    # Right circle arc (left half of right circle)
    right_circle = ConicSection((x - 0.5) ** 2 + y**2 - 1, variables)
    right_arc = TrimmedImplicitCurve(
        right_circle,
        lambda x_val, y_val: (x_val <= 0.05)
        and ((x_val - 0.5) ** 2 + y_val**2 <= 1.2),  # Left half with tolerance
        endpoints=[(0, -intersection_y), (0, intersection_y)],
    )

    return CompositeCurve([left_arc, right_arc], validate_continuity=True)

    return CompositeCurve([left_arc, right_arc], validate_continuity=True)
