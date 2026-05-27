#!/usr/bin/env python3
"""
Test composite curve intersections
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections


def test_composite_intersections():
    """Test intersections with composite curves"""

    print("🔧 COMPOSITE CURVE INTERSECTION TEST")
    print("=" * 50)

    x, y = sp.symbols("x y")

    # Test 1: Square vs Line
    print("\n📦 Test 1: Square vs Diagonal Line")
    print("-" * 40)

    square = create_square_from_edges((-1, -1), (1, 1))
    diagonal = PolynomialCurve(x - y, (x, y))  # y = x

    print("  Square: Composite curve from (-1,-1) to (1,1)")
    print("  Line: y = x")

    intersections = find_curve_intersections(
        square,
        diagonal,
        search_range=2.0,
        grid_resolution=400,
        tolerance=1e-8,
        detect_overlap=False,
    )

    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        val1 = square.evaluate(px, py)
        val2 = diagonal.evaluate(px, py)
        on_square = square.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))

        print(
            f"    {i + 1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}, on_square: {on_square}"
        )

    # Test 2: Circle quarters vs Line
    print("\n🔵 Test 2: Circle Quarters vs Vertical Line")
    print("-" * 40)

    circle = create_circle_from_quarters(center=(0, 0), radius=1.5)
    vertical = PolynomialCurve(x - 0.5, (x, y))  # x = 0.5

    print("  Circle: Composite circle with radius 1.5")
    print("  Line: x = 0.5")

    intersections = find_curve_intersections(
        circle,
        vertical,
        search_range=2.0,
        grid_resolution=400,
        tolerance=1e-8,
        detect_overlap=False,
    )

    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        val1 = circle.evaluate(px, py)
        val2 = vertical.evaluate(px, py)
        on_circle = circle.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))

        print(
            f"    {i + 1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}, on_circle: {on_circle}"
        )

    # Visualization
    print("\n🎨 Creating composite curve intersection visualization...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Composite Curve Intersections", fontsize=16, fontweight="bold")

    test_cases = [
        (square, diagonal, "Square ∩ Diagonal", intersections),
        (circle, vertical, "Circle Quarters ∩ Vertical", []),  # Will recalculate
    ]

    plot_range = 2
    resolution = 400
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)

    for idx, (curve1, curve2, title, intersections) in enumerate(test_cases):
        ax = axes[idx]

        # Recalculate intersections for plotting
        if not intersections:
            intersections = find_curve_intersections(
                curve1,
                curve2,
                search_range=plot_range,
                grid_resolution=300,
                tolerance=1e-8,
                detect_overlap=False,
            )

        try:
            # Plot curves
            Z1 = curve1.evaluate(X, Y)
            Z2 = curve2.evaluate(X, Y)

            ax.contour(X, Y, Z1, levels=[0], colors=["blue"], linewidths=2.5, alpha=0.8)
            ax.contour(X, Y, Z2, levels=[0], colors=["red"], linewidths=2.5, alpha=0.8)

            # Plot intersections
            for px, py in intersections:
                ax.plot(
                    px,
                    py,
                    "go",
                    markersize=10,
                    markeredgecolor="black",
                    markeredgewidth=2,
                    zorder=10,
                )
                ax.annotate(
                    f"({px:.2f}, {py:.2f})",
                    xy=(px, py),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
                )

            ax.set_xlim(-plot_range, plot_range)
            ax.set_ylim(-plot_range, plot_range)
            ax.set_aspect("equal")
            ax.grid(True, alpha=0.3)
            ax.set_title(f"{title}\n({len(intersections)} intersections)")

        except Exception as e:
            ax.text(
                0.5,
                0.5,
                f"Error: {title}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            print(f"Error plotting {title}: {e}")

    plt.tight_layout()
    plt.savefig("composite_curve_intersections.png", dpi=300, bbox_inches="tight")
    print("  📁 Visualization saved as: composite_curve_intersections.png")

    print("\n✅ Composite curve intersection testing complete!")


if __name__ == "__main__":
    test_composite_intersections()
