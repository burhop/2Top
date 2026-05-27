#!/usr/bin/env python3
"""
Debug composite curve issues
"""

import numpy as np
import sympy as sp
from geometry import *


def test_composite_curve_debug():
    """Debug what's wrong with composite curves"""

    print("🔍 COMPOSITE CURVE DEBUG")
    print("=" * 40)

    x, y = sp.symbols("x y")

    # Test 1: Simple square
    print("\n📦 Test 1: Square from edges")
    try:
        square = create_square_from_edges((-1, -1), (1, 1))
        print(f"  Square created: {type(square)}")
        print(f"  Square segments: {len(square.segments)}")

        # Test evaluation
        test_points = [(0, 0), (1, 0), (0, 1)]
        for px, py in test_points:
            try:
                val = square.evaluate(px, py)
                print(f"  evaluate({px}, {py}) = {val} (type: {type(val)})")
            except Exception as e:
                print(f"  evaluate({px}, {py}) ERROR: {e}")

        # Test with arrays
        try:
            X = np.array([[0, 1], [0, 1]])
            Y = np.array([[0, 0], [1, 1]])
            Z = square.evaluate(X, Y)
            print(
                f"  Array evaluation shape: {Z.shape if hasattr(Z, 'shape') else type(Z)}"
            )
        except Exception as e:
            print(f"  Array evaluation ERROR: {e}")

    except Exception as e:
        print(f"  Square creation ERROR: {e}")

    # Test 2: Circle from quarters
    print("\n🔵 Test 2: Circle from quarters")
    try:
        circle = create_circle_from_quarters(center=(0, 0), radius=1.0)
        print(f"  Circle created: {type(circle)}")
        print(f"  Circle segments: {len(circle.segments)}")

        # Test evaluation
        test_points = [(0, 0), (1, 0), (0, 1)]
        for px, py in test_points:
            try:
                val = circle.evaluate(px, py)
                print(f"  evaluate({px}, {py}) = {val} (type: {type(val)})")
            except Exception as e:
                print(f"  evaluate({px}, {py}) ERROR: {e}")

        # Test with arrays
        try:
            X = np.array([[0, 1], [0, 1]])
            Y = np.array([[0, 0], [1, 1]])
            Z = circle.evaluate(X, Y)
            print(
                f"  Array evaluation shape: {Z.shape if hasattr(Z, 'shape') else type(Z)}"
            )
        except Exception as e:
            print(f"  Array evaluation ERROR: {e}")

    except Exception as e:
        print(f"  Circle creation ERROR: {e}")

    # Test 3: Manual composite curve
    print("\n🔧 Test 3: Manual composite curve")
    try:
        # Create simple trimmed segments manually
        line1 = PolynomialCurve(y, (x, y))  # y = 0
        mask1 = lambda x_val, y_val: (-1 <= x_val <= 1)
        segment1 = TrimmedImplicitCurve(line1, mask1)

        line2 = PolynomialCurve(x - 1, (x, y))  # x = 1
        mask2 = lambda x_val, y_val: (0 <= y_val <= 1)
        segment2 = TrimmedImplicitCurve(line2, mask2)

        composite = CompositeCurve([segment1, segment2])
        print(f"  Manual composite created: {type(composite)}")
        print(f"  Segments: {len(composite.segments)}")

        # Test evaluation
        val = composite.evaluate(0, 0)
        print(f"  evaluate(0, 0) = {val} (type: {type(val)})")

        # Test with arrays
        X = np.array([[0, 1], [0, 1]])
        Y = np.array([[0, 0], [1, 1]])
        Z = composite.evaluate(X, Y)
        print(
            f"  Array evaluation shape: {Z.shape if hasattr(Z, 'shape') else type(Z)}"
        )
        print(f"  Array evaluation values: {Z}")

    except Exception as e:
        print(f"  Manual composite ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_composite_curve_debug()
