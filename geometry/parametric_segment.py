#!/usr/bin/env python3
"""
Parametric curve segments for reliable composite curves
"""

import numpy as np
import sympy as sp
from typing import Tuple, Callable, Optional, List
from .implicit_curve import ImplicitCurve


class ParametricSegment(ImplicitCurve):
    """
    A curve segment defined by parametric equations with explicit parameter bounds.
    This is much more reliable than trimmed implicit curves with masks.
    """

    def __init__(
        self,
        x_func: Callable[[float], float],
        y_func: Callable[[float], float],
        t_start: float,
        t_end: float,
        variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
        name: str = "ParametricSegment",
        is_periodic: bool = False,
    ):
        """
        Create a parametric curve segment.

        Args:
            x_func: Function x(t) for x-coordinate
            y_func: Function y(t) for y-coordinate
            t_start: Start parameter value
            t_end: End parameter value
            variables: Symbolic variables (x, y)
            name: Name for debugging
            is_periodic: Hint that the parametric functions are periodic (informational only)
        """
        if variables is None:
            x, y = sp.symbols("x y")
            variables = (x, y)

        # Store parametric functions
        self.x_func = x_func
        self.y_func = y_func
        self.t_start = t_start
        self.t_end = t_end
        self.name = name
        self.is_periodic = is_periodic

        # Calculate exact endpoints
        self.start_point = (x_func(t_start), y_func(t_start))
        self.end_point = (x_func(t_end), y_func(t_end))
        self.endpoints = [self.start_point, self.end_point]

        # Create a dummy implicit expression (we'll override evaluate)
        super().__init__(variables[0] ** 2 + variables[1] ** 2, variables)

    def evaluate(self, x_vals, y_vals):
        """
        Evaluate by checking distance to parametric curve.
        This is more reliable than implicit evaluation.
        """
        # Save input shape to restore it later
        input_shape = np.asarray(x_vals).shape

        # Ensure we have flat arrays
        flat_x = np.asarray(x_vals).ravel()
        flat_y = np.asarray(y_vals).ravel()

        # Sample the parametric curve
        t_samples = np.linspace(self.t_start, self.t_end, 200)
        curve_x = np.array([self.x_func(t) for t in t_samples], dtype=float)
        curve_y = np.array([self.y_func(t) for t in t_samples], dtype=float)

        result = np.empty(flat_x.shape, dtype=float)

        # Chunk size to prevent memory spikes
        chunk_size = 50000
        for i in range(0, len(flat_x), chunk_size):
            end_idx = min(i + chunk_size, len(flat_x))
            x_chunk = flat_x[i:end_idx]
            y_chunk = flat_y[i:end_idx]

            # Using broadcasting: (chunk_size, 1) and (1, 200)
            dx = x_chunk[:, np.newaxis] - curve_x[np.newaxis, :]
            dy = y_chunk[:, np.newaxis] - curve_y[np.newaxis, :]

            # Squared distance
            dists_sq = dx**2 + dy**2
            min_dist = np.sqrt(np.min(dists_sq, axis=1))

            result[i:end_idx] = min_dist - 0.02  # Threshold for "on curve"

        return result.reshape(input_shape)

    @property
    def is_curved(self) -> bool:
        """Return True if this parametric segment is curved."""
        if hasattr(self, "name") and self.name is not None:
            if self.name.startswith("Line"):
                return False
        return True

    def contains(self, x_val, y_val, tolerance=0.1):
        """Check if point is on the curve segment"""
        val = self.evaluate(x_val, y_val)
        return abs(val) <= tolerance

    def mask(self, x: float, y: float) -> bool:
        """
        Check if the point lies on this parametric segment.
        This provides compatibility with TrimmedImplicitCurve mask interfaces.
        """
        return bool(self.contains(x, y, tolerance=0.1))

    def get_polyline_approximation(
        self,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: int = 300,
    ) -> List[List[float]]:
        """
        Return a polyline approximation by directly sampling the parametric equations.

        This is the preferred rendering path in the graphics backend — far faster and
        more accurate than contour extraction on a distance field.

        Args:
            bounds: Ignored for parametric curves (sampling is in parameter space);
                    included for interface compatibility.
            resolution: Number of t-samples.

        Returns:
            List of [x, y] pairs.
        """
        t_vals = np.linspace(self.t_start, self.t_end, resolution)
        x_vals = np.array([float(self.x_func(t)) for t in t_vals])
        y_vals = np.array([float(self.y_func(t)) for t in t_vals])
        # Filter out non-finite values
        finite = np.isfinite(x_vals) & np.isfinite(y_vals)
        return [[x, y] for x, y in zip(x_vals[finite], y_vals[finite])]

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Return tight (xmin, xmax, ymin, ymax) by sampling the parametric curve.

        Returns:
            (xmin, xmax, ymin, ymax) computed from 500 uniformly spaced t-samples.
        """
        pts = self.get_polyline_approximation(resolution=500)
        if not pts:
            return (-1.0, 1.0, -1.0, 1.0)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        pad_x = max((max(xs) - min(xs)) * 0.05, 0.05)
        pad_y = max((max(ys) - min(ys)) * 0.05, 0.05)
        return (min(xs) - pad_x, max(xs) + pad_x, min(ys) - pad_y, max(ys) + pad_y)

    def is_closed(self, tolerance: float = 1e-6) -> bool:
        """
        Return True if the start and end points are the same (within tolerance).

        Args:
            tolerance: Maximum distance between start and end to consider closed.

        Returns:
            True if the curve is closed.
        """
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        return (dx * dx + dy * dy) <= tolerance * tolerance

    def plot(self, ax, resolution=200, **kwargs):
        """Plot the parametric segment"""
        t_vals = np.linspace(self.t_start, self.t_end, resolution)
        x_vals = np.array([self.x_func(t) for t in t_vals])
        y_vals = np.array([self.y_func(t) for t in t_vals])

        ax.plot(x_vals, y_vals, **kwargs)

        # Mark endpoints
        ax.plot([self.start_point[0]], [self.start_point[1]], "go", markersize=4)
        ax.plot([self.end_point[0]], [self.end_point[1]], "ro", markersize=4)


def create_circle_arc(
    center: Tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> ParametricSegment:
    """Create a circular arc segment"""
    cx, cy = center

    def x_func(t):
        return cx + radius * np.cos(t)

    def y_func(t):
        return cy + radius * np.sin(t)

    return ParametricSegment(
        x_func,
        y_func,
        start_angle,
        end_angle,
        variables,
        f"CircleArc({start_angle:.2f},{end_angle:.2f})",
    )


def create_line_segment(
    start: Tuple[float, float],
    end: Tuple[float, float],
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> ParametricSegment:
    """Create a line segment"""
    x1, y1 = start
    x2, y2 = end

    def x_func(t):
        return x1 + t * (x2 - x1)

    def y_func(t):
        return y1 + t * (y2 - y1)

    return ParametricSegment(
        x_func, y_func, 0.0, 1.0, variables, f"Line({start},{end})"
    )


def create_parabola_segment(
    a: float,
    b: float,
    c: float,
    x_start: float,
    x_end: float,
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> ParametricSegment:
    """Create a parabola segment y = ax² + bx + c"""

    def x_func(t):
        return x_start + t * (x_end - x_start)

    def y_func(t):
        x = x_func(t)
        return a * x**2 + b * x + c

    return ParametricSegment(
        x_func, y_func, 0.0, 1.0, variables, f"Parabola({a},{b},{c})"
    )


def create_ellipse_arc(
    center: Tuple[float, float],
    a: float,
    b: float,  # Semi-major and semi-minor axes
    start_angle: float,
    end_angle: float,
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> ParametricSegment:
    """Create an ellipse arc segment"""
    cx, cy = center

    def x_func(t):
        return cx + a * np.cos(t)

    def y_func(t):
        return cy + b * np.sin(t)

    return ParametricSegment(
        x_func,
        y_func,
        start_angle,
        end_angle,
        variables,
        f"EllipseArc({start_angle:.2f},{end_angle:.2f})",
    )
