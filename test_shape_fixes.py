#!/usr/bin/env python3
"""
Test the fixes for egg shape orientation and other shape issues
"""

import numpy as np
import matplotlib.pyplot as plt
from geometry.factories import (
    create_ellipse_parabola_hybrid,
    create_superellipse_circle_hybrid,
    create_lens_shape,
    create_heart_shape,
)


def test_shape_fixes():
    """Test all the shape fixes"""
    print("🔧 Testing Shape Fixes")
    print("=" * 50)

    # Test shapes that were having issues
    test_shapes = [
        ("Egg Shape (Fixed)", create_ellipse_parabola_hybrid),
        ("Rounded Square", create_superellipse_circle_hybrid),
        ("Lens Shape (Fixed)", create_lens_shape),
        ("Heart Shape (Fixed)", create_heart_shape),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()

    success_count = 0

    for i, (name, creator_func) in enumerate(test_shapes):
        ax = axes[i]

        try:
            print(f"\n🧪 Testing {name}")

            # Create the shape
            shape = creator_func()
            print(f"  ✅ Created with {len(shape.segments)} segments")

            # Test plotting with high resolution
            x_range = np.linspace(-3, 3, 400)
            y_range = np.linspace(-3, 3, 400)
            X, Y = np.meshgrid(x_range, y_range)

            # Count pixels on curve
            total_pixels = 0

            for j, segment in enumerate(shape.segments):
                if hasattr(segment, "base_curve") and hasattr(segment, "mask"):
                    # Trimmed curve
                    Z = segment.base_curve.evaluate(X, Y)

                    # Apply mask
                    mask_grid = np.zeros_like(X, dtype=bool)
                    for row in range(X.shape[0]):
                        for col in range(X.shape[1]):
                            mask_grid[row, col] = segment.mask(X[row, col], Y[row, col])

                    # Count pixels near zero within mask
                    on_curve = (np.abs(Z) < 0.05) & mask_grid
                    segment_pixels = np.sum(on_curve)
                    total_pixels += segment_pixels

                    print(f"    Segment {j}: {segment_pixels} pixels")
                else:
                    # Regular curve
                    Z = segment.evaluate(X, Y)
                    on_curve = np.abs(Z) < 0.05
                    segment_pixels = np.sum(on_curve)
                    total_pixels += segment_pixels

                    print(f"    Segment {j}: {segment_pixels} pixels")

            print(f"  📊 Total pixels: {total_pixels}")

            # Plot the shape
            shape.plot(ax=ax, x_range=(-3, 3), y_range=(-3, 3), resolution=300)
            ax.set_title(f"{name}\n{total_pixels} pixels")
            ax.grid(True, alpha=0.3)
            ax.set_aspect("equal")

            # Check for success
            if total_pixels > 500:  # Reasonable threshold
                print("  ✅ SUCCESS: Good pixel count")
                success_count += 1
            else:
                print("  ⚠️ WARNING: Low pixel count")

        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            ax.text(
                0.5,
                0.5,
                f"Failed\n{str(e)[:30]}...",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title(f"{name} (Failed)")

    plt.tight_layout()
    plt.savefig("shape_fixes_test.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("\n📊 RESULTS:")
    print(f"  ✅ Successful shapes: {success_count}/{len(test_shapes)}")
    print(f"  📈 Success rate: {success_count / len(test_shapes) * 100:.1f}%")
    print("  💾 Test plot saved as shape_fixes_test.png")

    if success_count >= len(test_shapes) * 0.75:  # 75% success rate
        print("\n🎉 SHAPE FIXES SUCCESSFUL!")
        print("✅ Most shape issues appear to be resolved")
    else:
        print("\n⚠️ Some shapes still have issues")
        print("🔧 May need additional fixes")

    return success_count >= len(test_shapes) * 0.75


def test_egg_orientation():
    """Specifically test that the egg shape is oriented correctly"""
    print("\n🥚 Testing Egg Shape Orientation")

    try:
        egg = create_ellipse_parabola_hybrid()

        # Test points to verify orientation
        # Should have ellipse at bottom (y <= 0) and parabola at top (y >= 0)

        # Test bottom point (should be on ellipse)
        bottom_val = egg.evaluate(0, -1)  # Bottom of ellipse
        print(f"  Bottom point (0, -1): {bottom_val:.6f}")

        # Test top point (should be on parabola)
        top_val = egg.evaluate(0, 0)  # On parabola y = x^2/4, at x=0, y=0
        print(f"  Top point (0, 0): {top_val:.6f}")

        # Test side points
        left_val = egg.evaluate(-2, 0)  # Should be on both curves (intersection)
        right_val = egg.evaluate(2, 0)  # Should be on both curves (intersection)
        print(f"  Left intersection (-2, 0): {left_val:.6f}")
        print(f"  Right intersection (2, 0): {right_val:.6f}")

        # Check if values are close to zero (on curve)
        if abs(bottom_val) < 0.1 and abs(top_val) < 0.1:
            print("  ✅ Egg orientation appears correct")
            return True
        else:
            print("  ⚠️ Egg orientation may still be wrong")
            return False

    except Exception as e:
        print(f"  ❌ Egg test failed: {e}")
        return False


if __name__ == "__main__":
    shape_success = test_shape_fixes()
    egg_success = test_egg_orientation()

    if shape_success and egg_success:
        print("\n🎉 ALL FIXES SUCCESSFUL!")
    else:
        print("\n🔧 Some issues remain")
