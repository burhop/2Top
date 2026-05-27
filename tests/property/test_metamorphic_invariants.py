"""Property-based and metamorphic tests for planar implicit geometry.

Verifies mathematical invariants (translation, rotation, scaling, gradient orthogonality)
across all taxonomic families of implicit equations.
"""

from __future__ import annotations

import math
import pytest
import sympy as sp
import numpy as np
from typing import Tuple, List

from geometry import (
    ImplicitCurve,
)


def get_taxonomic_curves() -> List[
    Tuple[str, sp.Expr, Tuple[sp.Symbol, sp.Symbol], List[Tuple[float, float]]]
]:
    """Return a suite of taxonomic test curves representing diverse algebraic and transcendental families,
    along with stable test points for evaluation.
    """
    x, y = sp.symbols("x y")

    curves = [
        # 1. Algebraic: Degree 1 (Linear)
        ("horizontal_line", y - 1.5, (x, y), [(0.0, 1.5), (2.0, 1.5), (-1.0, 2.5)]),
        ("vertical_line", x + 0.5, (x, y), [(-0.5, 0.0), (-0.5, 3.0), (1.0, 1.0)]),
        (
            "diagonal_line",
            2 * x - y + 1,
            (x, y),
            [(0.0, 1.0), (1.0, 3.0), (-2.0, -3.0)],
        ),
        # 2. Algebraic: Degree 2 (Conics)
        ("circle", x**2 + y**2 - 4.0, (x, y), [(2.0, 0.0), (0.0, 2.0), (1.0, 1.0)]),
        (
            "ellipse",
            x**2 / 9.0 + y**2 / 4.0 - 1.0,
            (x, y),
            [(3.0, 0.0), (0.0, 2.0), (1.5, 1.0)],
        ),
        ("parabola", y - x**2, (x, y), [(0.0, 0.0), (1.0, 1.0), (-2.0, 4.0)]),
        (
            "hyperbola",
            x**2 - y**2 - 1.0,
            (x, y),
            [(1.0, 0.0), (2.0, math.sqrt(3.0)), (-1.0, 0.0)],
        ),
        # 3. Degenerate Conics (Intersection of lines, points)
        (
            "intersecting_lines",
            x**2 - y**2,
            (x, y),
            [(0.0, 0.0), (1.0, 1.0), (2.0, -2.0)],
        ),
        ("single_point", x**2 + y**2, (x, y), [(0.0, 0.0), (1.0, 1.0), (-0.5, 0.5)]),
        # 4. Algebraic: Degree 3 (Cubics)
        (
            "semicubical_parabola",
            y**2 - x**3,
            (x, y),
            [(0.0, 0.0), (1.0, 1.0), (4.0, 8.0)],
        ),
        (
            "folium_of_descartes",
            x**3 + y**3 - 3 * x * y,
            (x, y),
            [(0.0, 0.0), (1.5, 1.5), (2.0, 1.0)],
        ),
        # 5. Algebraic: Degree 4 (Quartics)
        (
            "lemniscate",
            (x**2 + y**2) ** 2 - 2 * (x**2 - y**2),
            (x, y),
            [(0.0, 0.0), (math.sqrt(2), 0.0)],
        ),
        (
            "cardioid",
            (x**2 + y**2 - x) ** 2 - (x**2 + y**2),
            (x, y),
            [(0.0, 0.0), (2.0, 0.0)],
        ),
        # 6. Transcendental
        (
            "periodic_wavy",
            sp.sin(x) - sp.cos(y),
            (x, y),
            [(0.0, math.pi / 2), (math.pi, math.pi / 2)],
        ),
        ("exponential_open", y - sp.exp(x), (x, y), [(0.0, 1.0), (1.0, math.e)]),
    ]
    return curves


@pytest.mark.parametrize("name, expr, vars_tuple, test_points", get_taxonomic_curves())
def test_translation_invariance(
    name: str,
    expr: sp.Expr,
    vars_tuple: Tuple[sp.Symbol, sp.Symbol],
    test_points: List[Tuple[float, float]],
):
    """Metamorphic Invariant: Translating curve f(x, y) by (dx, dy) yields f'(x, y) = f(x - dx, y - dy).
    Therefore, f'(x + dx, y + dy) == f(x, y).
    """
    x, y = vars_tuple
    dx, dy = 1.5, -2.5

    # Original curve
    original_curve = ImplicitCurve(expr, variables=(x, y))

    # Translated curve: substitute variables simultaneously
    translated_expr = expr.subs({x: x - dx, y: y - dy}, simultaneous=True)
    translated_curve = ImplicitCurve(translated_expr, variables=(x, y))

    for px, py in test_points:
        orig_val = original_curve.evaluate(px, py)
        trans_val = translated_curve.evaluate(px + dx, py + dy)

        # Values should be equivalent
        assert math.isclose(orig_val, trans_val, abs_tol=1e-9)

        # Gradients must also translate exactly: grad_f'(px + dx, py + dy) == grad_f(px, py)
        orig_gx, orig_gy = original_curve.gradient(px, py)
        trans_gx, trans_gy = translated_curve.gradient(px + dx, py + dy)
        assert math.isclose(orig_gx, trans_gx, abs_tol=1e-9)
        assert math.isclose(orig_gy, trans_gy, abs_tol=1e-9)


@pytest.mark.parametrize("name, expr, vars_tuple, test_points", get_taxonomic_curves())
def test_positive_scaling_invariance(
    name: str,
    expr: sp.Expr,
    vars_tuple: Tuple[sp.Symbol, sp.Symbol],
    test_points: List[Tuple[float, float]],
):
    """Metamorphic Invariant: Multiplying expression f(x, y) by k > 0 scales the gradient magnitude,
    but keeps the sign and unit normal direction identical.
    """
    x, y = vars_tuple
    k = 3.5

    original_curve = ImplicitCurve(expr, variables=(x, y))
    scaled_curve = ImplicitCurve(k * expr, variables=(x, y))

    for px, py in test_points:
        orig_val = original_curve.evaluate(px, py)
        scaled_val = scaled_curve.evaluate(px, py)

        # Value is scaled by k
        assert math.isclose(scaled_val, k * orig_val, abs_tol=1e-9)

        # Signs are preserved
        assert np.sign(orig_val) == np.sign(scaled_val) or (
            abs(orig_val) < 1e-12 and abs(scaled_val) < 1e-12
        )

        # Gradients are scaled by k
        orig_gx, orig_gy = original_curve.gradient(px, py)
        scaled_gx, scaled_gy = scaled_curve.gradient(px, py)
        assert math.isclose(scaled_gx, k * orig_gx, abs_tol=1e-9)
        assert math.isclose(scaled_gy, k * orig_gy, abs_tol=1e-9)

        # Unit normal directions must be identical (if defined)
        orig_mag = math.sqrt(orig_gx**2 + orig_gy**2)
        if orig_mag > 1e-9:
            orig_nx, orig_ny = original_curve.normal(px, py)
            scaled_nx, scaled_ny = scaled_curve.normal(px, py)
            assert math.isclose(orig_nx, scaled_nx, abs_tol=1e-9)
            assert math.isclose(orig_ny, scaled_ny, abs_tol=1e-9)


@pytest.mark.parametrize("name, expr, vars_tuple, test_points", get_taxonomic_curves())
def test_rotation_invariance(
    name: str,
    expr: sp.Expr,
    vars_tuple: Tuple[sp.Symbol, sp.Symbol],
    test_points: List[Tuple[float, float]],
):
    """Metamorphic Invariant: Rotating curve by angle theta and rotating the test points yields the same values."""
    x, y = vars_tuple
    theta = math.pi / 6  # 30 degrees
    cos_t, sin_t = math.cos(theta), math.sin(theta)

    original_curve = ImplicitCurve(expr, variables=(x, y))

    # Rotated coordinate substitution
    # For a point (px, py), rotated coordinate (rx, ry) is:
    # rx = px * cos_t - py * sin_t
    # ry = px * sin_t + py * cos_t
    # Rotated coordinate substitution with simultaneous=True
    rotated_expr = expr.subs(
        {x: x * cos_t + y * sin_t, y: -x * sin_t + y * cos_t}, simultaneous=True
    )
    rotated_curve = ImplicitCurve(rotated_expr, variables=(x, y))

    for px, py in test_points:
        orig_val = original_curve.evaluate(px, py)

        # Rotate test point
        rx = px * cos_t - py * sin_t
        ry = px * sin_t + py * cos_t

        rot_val = rotated_curve.evaluate(rx, ry)
        assert math.isclose(orig_val, rot_val, abs_tol=1e-9)


@pytest.mark.parametrize("name, expr, vars_tuple, test_points", get_taxonomic_curves())
def test_gradient_tangent_orthogonality(
    name: str,
    expr: sp.Expr,
    vars_tuple: Tuple[sp.Symbol, sp.Symbol],
    test_points: List[Tuple[float, float]],
):
    """Mathematical Invariant: At any smooth point, the gradient vector is perpendicular to the tangent of the level set.
    For small step h along tangent t, f(p + h * t) - f(p) should be o(h).
    """
    x, y = vars_tuple
    curve = ImplicitCurve(expr, variables=(x, y))

    for px, py in test_points:
        gx, gy = curve.gradient(px, py)
        mag = math.sqrt(gx**2 + gy**2)
        if mag < 1e-6:
            continue  # Vanishing gradient (singularity)

        # Tangent vector is (-gy, gx)
        tx, ty = -gy / mag, gx / mag

        # Numerical derivative along tangent: df/dt ≈ [f(p + h*t) - f(p - h*t)] / 2h
        h = 1e-5
        val_plus = curve.evaluate(px + h * tx, py + h * ty)
        val_minus = curve.evaluate(px - h * tx, py - h * ty)
        deriv_along_tangent = (val_plus - val_minus) / (2 * h)

        # Rate of change along tangent must be zero (within numeric tolerances)
        assert abs(deriv_along_tangent) < 1e-4
