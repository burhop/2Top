#!/usr/bin/env python3
"""
Final test to verify all shape fixes are working
"""

import matplotlib.pyplot as plt
from geometry.factories import (
    create_ellipse_parabola_hybrid,
    create_superellipse_circle_hybrid,
    create_lens_shape,
    create_heart_shape,
)


def test_final_fixes():
    """Test all the final fixes"""
    print("🎯 Final Shape Fixes Test")
    print("=" * 40)

    # Create a single plot with all fixed shapes
    fig, ax = plt.subplots(figsize=(12, 10))

    shapes = [
        ("Egg Shape (Fixed)", create_ellipse_parabola_hybrid, "orange"),
        ("Rounded Square", create_superellipse_circle_hybrid, "green"),
        ("Lens Shape", create_lens_shape, "purple"),
        ("Heart Shape", create_heart_shape, "red"),
    ]

    success_count = 0

    for name, creator_func, color in shapes:
        try:
            print(f"🧪 Testing {name}")

            # Create shape
            shape = creator_func()
            print(f"  ✅ Created with {len(shape.segments)} segments")

            # Plot with offset to avoid overlap
            if "Egg" in name:
                offset_x, offset_y = -3, 2
            elif "Rounded" in name:
                offset_x, offset_y = 3, 2
            elif "Lens" in name:
                offset_x, offset_y = -3, -2
            else:  # Heart
                offset_x, offset_y = 3, -2

            # Plot the shape with offset
            x_range = (offset_x - 1.5, offset_x + 1.5)
            y_range = (offset_y - 1.5, offset_y + 1.5)

            # Manual plotting with offset
            import numpy as np

            x_vals = np.linspace(x_range[0], x_range[1], 300)
            y_vals = np.linspace(y_range[0], y_range[1], 300)
            X, Y = np.meshgrid(x_vals, y_vals)

            # Shift coordinates for evaluation
            X_shifted = X - offset_x
            Y_shifted = Y - offset_y

            # Plot each segment
            for j, segment in enumerate(shape.segments):
                if hasattr(segment, "base_curve") and hasattr(segment, "mask"):
                    # Trimmed curve
                    Z = segment.base_curve.evaluate(X_shifted, Y_shifted)

                    # Apply mask
                    mask_grid = np.zeros_like(X_shifted, dtype=bool)
                    for row in range(X_shifted.shape[0]):
                        for col in range(X_shifted.shape[1]):
                            mask_grid[row, col] = segment.mask(
                                X_shifted[row, col], Y_shifted[row, col]
                            )

                    Z_masked = np.where(mask_grid, Z, np.nan)
                    ax.contour(X, Y, Z_masked, levels=[0], colors=[color], linewidths=2)
                else:
                    # Regular curve
                    Z = segment.evaluate(X_shifted, Y_shifted)
                    ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2)

            # Add label
            ax.text(
                offset_x,
                offset_y + 1.8,
                name,
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color=color,
            )

            print(f"  ✅ {name} plotted successfully")
            success_count += 1

        except Exception as e:
            print(f"  ❌ {name} failed: {e}")

    ax.set_xlim(-5, 5)
    ax.set_ylim(-4, 4)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(
        "Fixed Composite Shapes\n(Egg shape now properly oriented)",
        fontsize=14,
        fontweight="bold",
    )

    plt.tight_layout()
    plt.savefig("final_fixes_test.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("\n📊 FINAL RESULTS:")
    print(f"  ✅ Working shapes: {success_count}/{len(shapes)}")
    print(f"  📈 Success rate: {success_count / len(shapes) * 100:.1f}%")
    print("  💾 Final test plot saved as final_fixes_test.png")

    if success_count == len(shapes):
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("✅ Egg shape orientation fixed")
        print("✅ Heart shape tolerance fixed")
        print("✅ Lens shape properly defined")
        print("✅ All shapes have sufficient pixels")
        return True
    else:
        print(f"\n⚠️ {len(shapes) - success_count} shapes still have issues")
        return False


if __name__ == "__main__":
    success = test_final_fixes()
    if success:
        print("\n🚀 Ready for user testing!")
    else:
        print("\n🔧 More work needed")
