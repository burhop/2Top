#!/usr/bin/env python3
"""
Test the visualizer display to see if squares are actually being drawn
"""

import tkinter as tk
import matplotlib.pyplot as plt
from clean_curve_visualizer import CleanCurveVisualizerApp


def test_visualizer_display():
    """Test the visualizer display by creating it and saving the plot"""
    print("🔍 Testing Visualizer Display")

    # Create the visualizer
    root = tk.Tk()
    root.withdraw()  # Hide the window

    app = CleanCurveVisualizerApp(root)

    # Add some curves
    print("Adding curves...")
    app.add_square()  # Should add "Unit Square"
    app.add_square()  # Should add "Small Square"
    app.add_composite()  # Should add first composite (L-Shape)

    print(f"Total curves: {len(app.curves)}")
    for i, (name, curve) in enumerate(app.curves):
        print(f"  {i}: {name}")

    # Force an update of the plot
    print("Updating plot...")
    app.update_plot()

    # Save the current plot to a file
    print("Saving plot...")
    app.fig.savefig("visualizer_display_test.png", dpi=150, bbox_inches="tight")

    # Also create a manual plot to compare
    fig, ax = plt.subplots(figsize=(10, 8))

    colors = ["blue", "red", "green", "orange", "purple"]

    for i, (name, curve) in enumerate(app.curves):
        print(f"Manually plotting {name}...")
        try:
            color = colors[i % len(colors)]
            contour_sets = curve.plot(
                ax=ax, x_range=(-2, 2), y_range=(-2, 2), colors=[color]
            )
            print(f"  {name}: Success ({len(contour_sets)} contour sets)")
        except Exception as e:
            print(f"  {name}: Failed - {e}")

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title("Manual Plot of Visualizer Curves")
    ax.legend([f"{name}" for name, _ in app.curves])

    plt.savefig("manual_visualizer_curves.png", dpi=150, bbox_inches="tight")
    plt.close()

    root.destroy()

    print("✅ Visualizer display test completed")
    print("Check visualizer_display_test.png and manual_visualizer_curves.png")


def test_square_colors():
    """Test if squares are being drawn with invisible colors"""
    print("\n🔍 Testing Square Colors")

    from geometry.factories import create_square_from_edges

    square = create_square_from_edges((-1, -1), (1, 1))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Test different color schemes
    color_schemes = [
        {"colors": ["blue"], "linewidths": 2},
        {"colors": ["red"], "linewidths": 4},
        {"colors": ["black"], "linewidths": 1},
    ]

    titles = ["Blue (default)", "Red (thick)", "Black (thin)"]

    for i, (ax, colors, title) in enumerate(zip(axes, color_schemes, titles)):
        try:
            contour_sets = square.plot(
                ax=ax, x_range=(-2, 2), y_range=(-2, 2), **colors
            )
            print(f"  {title}: Success ({len(contour_sets)} contour sets)")
        except Exception as e:
            print(f"  {title}: Failed - {e}")

        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig("square_color_test.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("✅ Square color test completed - check square_color_test.png")


if __name__ == "__main__":
    print("🧪 TESTING VISUALIZER DISPLAY")
    print("=" * 50)

    test_visualizer_display()
    test_square_colors()
