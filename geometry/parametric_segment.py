#!/usr/bin/env python3
"""
Parametric curve segments for reliable composite curves
"""

import numpy as np
import sympy as sp
from typing import Tuple, Callable, Optional
from .implicit_curve import ImplicitCurve

class ParametricSegment(ImplicitCurve):
    """
    A curve segment defined by parametric equations with explicit parameter bounds.
    This is much more reliable than trimmed implicit curves with masks.
    """
    
    def __init__(self, 
                 x_func: Callable[[float], float],
                 y_func: Callable[[float], float], 
                 t_start: float,
                 t_end: float,
                 variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
                 name: str = "ParametricSegment"):
        """
        Create a parametric curve segment.
        
        Args:
            x_func: Function x(t) for x-coordinate
            y_func: Function y(t) for y-coordinate  
            t_start: Start parameter value
            t_end: End parameter value
            variables: Symbolic variables (x, y)
            name: Name for debugging
        """
        if variables is None:
            x, y = sp.symbols('x y')
            variables = (x, y)
        
        # Store parametric functions
        self.x_func = x_func
        self.y_func = y_func
        self.t_start = t_start
        self.t_end = t_end
        self.name = name
        
        # Calculate exact endpoints
        self.start_point = (x_func(t_start), y_func(t_start))
        self.end_point = (x_func(t_end), y_func(t_end))
        self.endpoints = [self.start_point, self.end_point]
        
        # Create a dummy implicit expression (we'll override evaluate)
        super().__init__(variables[0]**2 + variables[1]**2, variables)
    
    def evaluate(self, x_vals, y_vals):
        """
        Evaluate by checking distance to parametric curve.
        This is more reliable than implicit evaluation.
        """
        x_vals = np.asarray(x_vals)
        y_vals = np.asarray(y_vals)
        
        # Sample the parametric curve
        t_samples = np.linspace(self.t_start, self.t_end, 200)
        curve_x = np.array([self.x_func(t) for t in t_samples])
        curve_y = np.array([self.y_func(t) for t in t_samples])
        
        # For each query point, find minimum distance to curve
        result = np.zeros_like(x_vals, dtype=float)
        
        x_flat = x_vals.flatten()
        y_flat = y_vals.flatten()
        
        for i, (qx, qy) in enumerate(zip(x_flat, y_flat)):
            # Distance to all curve points
            distances = np.sqrt((curve_x - qx)**2 + (curve_y - qy)**2)
            min_dist = np.min(distances)
            
            # Return signed distance (negative inside, positive outside)
            # For curve segments, we consider "inside" to be very close to the curve
            result.flat[i] = min_dist - 0.02  # Threshold for "on curve"
        
        return result.reshape(x_vals.shape)
    
    def contains(self, x_val, y_val, tolerance=0.1):
        """Check if point is on the curve segment"""
        val = self.evaluate(x_val, y_val)
        return abs(val) <= tolerance
    
    def plot(self, ax, resolution=200, **kwargs):
        """Plot the parametric segment"""
        t_vals = np.linspace(self.t_start, self.t_end, resolution)
        x_vals = np.array([self.x_func(t) for t in t_vals])
        y_vals = np.array([self.y_func(t) for t in t_vals])
        
        ax.plot(x_vals, y_vals, **kwargs)
        
        # Mark endpoints
        ax.plot([self.start_point[0]], [self.start_point[1]], 'go', markersize=4)
        ax.plot([self.end_point[0]], [self.end_point[1]], 'ro', markersize=4)


def create_circle_arc(center: Tuple[float, float], 
                     radius: float,
                     start_angle: float, 
                     end_angle: float,
                     variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None) -> ParametricSegment:
    """Create a circular arc segment"""
    cx, cy = center
    
    def x_func(t):
        return cx + radius * np.cos(t)
    
    def y_func(t):
        return cy + radius * np.sin(t)
    
    return ParametricSegment(x_func, y_func, start_angle, end_angle, variables, f"CircleArc({start_angle:.2f},{end_angle:.2f})")


def create_line_segment(start: Tuple[float, float],
                       end: Tuple[float, float],
                       variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None) -> ParametricSegment:
    """Create a line segment"""
    x1, y1 = start
    x2, y2 = end
    
    def x_func(t):
        return x1 + t * (x2 - x1)
    
    def y_func(t):
        return y1 + t * (y2 - y1)
    
    return ParametricSegment(x_func, y_func, 0.0, 1.0, variables, f"Line({start},{end})")


def create_parabola_segment(a: float, b: float, c: float,
                           x_start: float, x_end: float,
                           variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None) -> ParametricSegment:
    """Create a parabola segment y = ax² + bx + c"""
    
    def x_func(t):
        return x_start + t * (x_end - x_start)
    
    def y_func(t):
        x = x_func(t)
        return a * x**2 + b * x + c
    
    return ParametricSegment(x_func, y_func, 0.0, 1.0, variables, f"Parabola({a},{b},{c})")


def create_ellipse_arc(center: Tuple[float, float],
                      a: float, b: float,  # Semi-major and semi-minor axes
                      start_angle: float, end_angle: float,
                      variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None) -> ParametricSegment:
    """Create an ellipse arc segment"""
    cx, cy = center
    
    def x_func(t):
        return cx + a * np.cos(t)
    
    def y_func(t):
        return cy + b * np.sin(t)
    
    return ParametricSegment(x_func, y_func, start_angle, end_angle, variables, f"EllipseArc({start_angle:.2f},{end_angle:.2f})")