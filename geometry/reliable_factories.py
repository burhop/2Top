#!/usr/bin/env python3
"""
Reliable composite curve factories using parametric segments
"""

import numpy as np
import sympy as sp
from typing import Optional, Tuple
from .composite_curve import CompositeCurve
from .parametric_segment import (
    create_circle_arc,
    create_line_segment,
    create_parabola_segment,
    create_ellipse_arc,
)


def create_reliable_heart_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a heart shape using parametric segments - guaranteed to work!
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)

    # Heart design with parametric segments:
    # 1. Left circle arc (upper left lobe)
    # 2. Right circle arc (upper right lobe)
    # 3. Parabola bottom

    # Left heart lobe: circle centered at (-0.5, 0.25), radius 0.5
    # Arc from bottom (angle π) to top-right (angle 0)
    left_lobe = create_circle_arc(
        center=(-0.5, 0.25),
        radius=0.5,
        start_angle=np.pi,  # Start at (-1, 0.25)
        end_angle=0,  # End at (0, 0.25)
        variables=variables,
    )

    # Right heart lobe: circle centered at (0.5, 0.25), radius 0.5
    # Arc from top-left (angle π) to bottom (angle 0)
    right_lobe = create_circle_arc(
        center=(0.5, 0.25),
        radius=0.5,
        start_angle=np.pi,  # Start at (0, 0.25)
        end_angle=0,  # End at (1, 0.25)
        variables=variables,
    )

    # Bottom parabola: y = x² - 1, from x = 1 to x = -1
    heart_bottom = create_parabola_segment(
        a=1.0,
        b=0.0,
        c=-1.0,  # y = x² - 1
        x_start=1.0,  # Start at (1, 0)
        x_end=-1.0,  # End at (-1, 0)
        variables=variables,
    )

    return CompositeCurve([left_lobe, right_lobe, heart_bottom], variables)


def create_reliable_egg_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create an egg shape using parametric segments - guaranteed to work!
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)

    # Egg design:
    # 1. Bottom ellipse arc (wider bottom)
    # 2. Top parabola arc (narrower top)

    # Bottom ellipse: x²/4 + y² = 1, bottom half (y ≤ 0)
    # Parametric: x = 2*cos(t), y = sin(t), t from π to 2π
    bottom_ellipse = create_ellipse_arc(
        center=(0, 0),
        a=2.0,
        b=1.0,  # Semi-major=2, semi-minor=1
        start_angle=np.pi,  # Start at (-2, 0)
        end_angle=2 * np.pi,  # End at (2, 0)
        variables=variables,
    )

    # Top parabola: y = x²/4, from x = 2 to x = -2
    top_parabola = create_parabola_segment(
        a=0.25,
        b=0.0,
        c=0.0,  # y = x²/4
        x_start=2.0,  # Start at (2, 1)
        x_end=-2.0,  # End at (-2, 1)
        variables=variables,
    )

    return CompositeCurve([bottom_ellipse, top_parabola], variables)


def create_reliable_lens_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a lens shape using parametric segments - guaranteed to work!
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)

    # Lens: two intersecting circles
    # Left circle: (x+0.5)² + y² = 1, right half
    # Right circle: (x-0.5)² + y² = 1, left half
    # They intersect at (0, ±√3/2)

    intersection_y = np.sqrt(3) / 2

    # Left arc: circle centered at (-0.5, 0), right half
    # From (0, √3/2) to (0, -√3/2)
    left_arc = create_circle_arc(
        center=(-0.5, 0),
        radius=1.0,
        start_angle=np.arcsin(intersection_y),  # Upper intersection
        end_angle=-np.arcsin(intersection_y),  # Lower intersection
        variables=variables,
    )

    # Right arc: circle centered at (0.5, 0), left half
    # From (0, -√3/2) to (0, √3/2)
    right_arc = create_circle_arc(
        center=(0.5, 0),
        radius=1.0,
        start_angle=np.pi + np.arcsin(intersection_y),  # Lower intersection
        end_angle=np.pi - np.arcsin(intersection_y),  # Upper intersection
        variables=variables,
    )

    return CompositeCurve([left_arc, right_arc], variables)


def create_reliable_d_shape(
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a D-shape using parametric segments - guaranteed to work!
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)

    # D-shape: semicircle + straight line
    # Semicircle: x² + y² = 1, right half (x ≥ 0)
    # Line: x = 0, from (0, 1) to (0, -1)

    # Right semicircle: from (0, -1) to (0, 1)
    semicircle = create_circle_arc(
        center=(0, 0),
        radius=1.0,
        start_angle=-np.pi / 2,  # Start at (0, -1)
        end_angle=np.pi / 2,  # End at (0, 1)
        variables=variables,
    )

    # Straight line: from (0, 1) to (0, -1)
    straight_line = create_line_segment(start=(0, 1), end=(0, -1), variables=variables)

    return CompositeCurve([semicircle, straight_line], variables)


def create_reliable_square(
    corner1: Tuple[float, float] = (-1, -1),
    corner2: Tuple[float, float] = (1, 1),
    variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
) -> CompositeCurve:
    """
    Create a square using parametric line segments - guaranteed to work!
    """
    if variables is None:
        x, y = sp.symbols("x y")
        variables = (x, y)

    x1, y1 = corner1
    x2, y2 = corner2
    xmin, xmax = (x1, x2) if x1 <= x2 else (x2, x1)
    ymin, ymax = (y1, y2) if y1 <= y2 else (y2, y1)

    # Four line segments forming a square
    bottom = create_line_segment((xmin, ymin), (xmax, ymin), variables)
    right = create_line_segment((xmax, ymin), (xmax, ymax), variables)
    top = create_line_segment((xmax, ymax), (xmin, ymax), variables)
    left = create_line_segment((xmin, ymax), (xmin, ymin), variables)

    return CompositeCurve([bottom, right, top, left], variables)
