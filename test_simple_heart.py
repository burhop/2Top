#!/usr/bin/env python3
"""
Simple test of heart shape plotting
"""

import matplotlib.pyplot as plt
from geometry.factories import create_heart_shape


def test_simple_heart():
    """Test heart shape plotting directly"""
    print("💖 Testing Simple Heart Shape")

    # Create heart
    heart = create_heart_shape()
    print(f"Heart has {len(heart.segments)} segments")

    # Create plot
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    # Plot each segment individually
    for i, segment in enumerate(heart.segments):
        ax = axes[i]

        print(f"\nSegment {i}:")
        print(f"  Endpoints: {segment.endpoints}")

        # Plot using the segment's own plot method
        try:
            segment.plot(
                x_range=(-2, 2),
                y_range=(-2, 2),
                resolution=300,
                ax=ax,
                colors=["red"],
                linewidths=2,
            )
            ax.set_title(f"Segment {i} - Individual")
            print(f"  ✅ Segment {i} plotted successfully")
        except Exception as e:
            print(f"  ❌ Segment {i} failed: {e}")
            ax.text(
                0.5,
                0.5,
                f"Failed\n{str(e)[:30]}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )

        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

    # Plot composite using its own method
    ax = axes[3]
    try:
        heart.plot(x_range=(-2, 2), y_range=(-2, 2), resolution=300, ax=ax)
        ax.set_title("Composite Heart")
        print("  ✅ Composite heart plotted successfully")
    except Exception as e:
        print(f"  ❌ Composite heart failed: {e}")
        ax.text(
            0.5,
            0.5,
            f"Failed\n{str(e)[:30]}",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )

    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig("simple_heart_test.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("\n💾 Simple heart test saved as simple_heart_test.png")


if __name__ == "__main__":
    test_simple_heart()
