"""Unit tests for singularity and zero-gradient robustness in implicit curves.

Probes geometric cusps, nodes, acnodes, and degenerate cases to verify that
gradient evaluations vanish correctly, normal vectors raise appropriate errors,
and evaluations are numerically stable.
"""

from __future__ import annotations

import math
import pytest
import sympy as sp
import numpy as np

from geometry import (
    ImplicitCurve,
    ConicSection,
    PolynomialCurve,
    Superellipse,
    ProceduralCurve,
)


def test_cusp_singularity():
    """Verify behavior at the cusp of a semicubical parabola (y^2 - x^3 = 0) at (0,0)."""
    x, y = sp.symbols("x y")
    curve = ImplicitCurve(y**2 - x**3, variables=(x, y))

    # Cusp is at the origin (0, 0)
    # The gradient is ( -3x^2, 2y ) which vanishes at (0, 0)
    gx, gy = curve.gradient(0.0, 0.0)
    assert abs(gx) < 1e-12
    assert abs(gy) < 1e-12

    # Normal vector must raise ValueError indicating undefined normal due to zero gradient
    with pytest.raises(ValueError, match="Normal undefined.*zero gradient"):
        curve.normal(0.0, 0.0)


def test_node_singularity():
    """Verify behavior at the self-intersection node of intersecting lines (x^2 - y^2 = 0) at (0,0)."""
    x, y = sp.symbols("x y")
    curve = ConicSection(x**2 - y**2, variables=(x, y))

    # Intersection is at the origin (0, 0)
    # Gradient is (2x, -2y) which vanishes at (0, 0)
    gx, gy = curve.gradient(0.0, 0.0)
    assert abs(gx) < 1e-12
    assert abs(gy) < 1e-12

    with pytest.raises(ValueError, match="Normal undefined.*zero gradient"):
        curve.normal(0.0, 0.0)


def test_isolated_point_singularity_acnode():
    """Verify behavior at an isolated point singularity (acnode) for x^2 + y^2 = 0 at (0,0)."""
    x, y = sp.symbols("x y")
    curve = ConicSection(x**2 + y**2, variables=(x, y))

    # Acnode is at (0, 0)
    # Gradient is (2x, 2y) which vanishes at (0, 0)
    gx, gy = curve.gradient(0.0, 0.0)
    assert abs(gx) < 1e-12
    assert abs(gy) < 1e-12

    with pytest.raises(ValueError, match="Normal undefined.*zero gradient"):
        curve.normal(0.0, 0.0)


def test_high_order_vanishing_gradient():
    """Verify behavior for extremely flat/high-order curves like a squircle squashed boundary
    where gradients are very close to zero but not mathematically singular.
    """
    x, y = sp.symbols("x y")
    # Squircle of degree 8: x^8 + y^8 - 1 = 0
    curve = PolynomialCurve(x**8 + y**8 - 1, variables=(x, y))

    # At (0.1, 0.1), gradient elements are 8*x^7 and 8*y^7, which are ~8e-7 (tiny but non-zero)
    gx, gy = curve.gradient(0.1, 0.1)
    assert 0.0 < abs(gx) < 1e-6
    assert 0.0 < abs(gy) < 1e-6

    # Normal vector should still compute successfully despite the very small gradient magnitude
    nx, ny = curve.normal(0.1, 0.1)
    magnitude = np.sqrt(nx**2 + ny**2)
    assert math.isclose(magnitude, 1.0, abs_tol=1e-9)


def test_procedural_curve_singularity():
    """Verify that ProceduralCurve (which uses numerical gradients) behaves gracefully at singularities."""
    # Define a cusp curve numerically
    def cusp_func(x_val, y_val):
        return y_val**2 - x_val**3

    curve = ProceduralCurve(cusp_func)

    # Gradient at (0.0, 0.0) should be close to zero
    gx, gy = curve.gradient(0.0, 0.0)
    # Finite differences with step h=1e-5:
    # df/dx ≈ (0 - 0) / 2h = 0
    # df/dy ≈ (h^2 - h^2) / 2h = 0
    assert abs(gx) < 1e-4
    assert abs(gy) < 1e-4

    # Normal should fail gracefully at zero gradient
    with pytest.raises(ValueError, match="Normal undefined.*zero gradient"):
        curve.normal(0.0, 0.0)
