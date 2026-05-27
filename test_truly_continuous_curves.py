#!/usr/bin/env python3
"""
Test that all composite curves are truly continuous (no discontinuous examples)
"""

import numpy as np
from geometry import *
from geometry.factories import *


def test_continuity_enforcement():
    """Test that all composite curves enforce true continuity"""

    print("🔗 TESTING TRUE CONTINUITY ENFORCEMENT")
    print("=" * 60)

    # Test all factory functions with continuity validation ENABLED
    continuous_shapes = [
        ("L-Shape", create_L_shape),
        ("T-Shape", create_T_shape),
        ("Triangle", create_triangle),
        ("House Shape", create_house_shape),
        ("Zigzag Pattern", create_zigzag_pattern),
        ("Staircase", create_staircase),
        ("Figure Eight", create_figure_eight),
        ("Square", lambda: create_square_from_edges((-1, -1), (1, 1))),
        (
            "Circle Quarters",
            lambda: create_circle_from_quarters(center=(0, 0), radius=1.0),
        ),
    ]

    print("Testing all shapes with continuity validation ENABLED...")

    all_continuous = True

    for name, creator in continuous_shapes:
        print(f"\n🔧 Testing {name}...")
        try:
            # Create with continuity validation enabled
            shape = creator()

            # Verify it's actually continuous by checking endpoints
            if len(shape.segments) > 1:
                gaps = []
                # For open curves, only check consecutive segments (not wraparound)
                # For closed curves, check all segments including wraparound
                is_closed = shape.is_closed()
                num_checks = (
                    len(shape.segments) if is_closed else len(shape.segments) - 1
                )

                for i in range(num_checks):
                    current_seg = shape.segments[i]
                    next_seg = shape.segments[(i + 1) % len(shape.segments)]

                    current_endpoints = current_seg.get_endpoints()
                    next_endpoints = next_seg.get_endpoints()

                    if current_endpoints and next_endpoints:
                        # Find minimum gap
                        min_gap = float("inf")
                        for curr_end in current_endpoints:
                            for next_end in next_endpoints:
                                gap = np.sqrt(
                                    (curr_end[0] - next_end[0]) ** 2
                                    + (curr_end[1] - next_end[1]) ** 2
                                )
                                min_gap = min(min_gap, gap)
                        gaps.append(min_gap)

                max_gap = max(gaps) if gaps else 0
                is_truly_continuous = max_gap < 1e-6

                if is_truly_continuous:
                    closed_status = "closed" if is_closed else "open"
                    print(
                        f"  ✅ {name}: {len(shape.segments)} segments, {closed_status}, max gap: {max_gap:.2e}"
                    )
                else:
                    print(
                        f"  ❌ {name}: {len(shape.segments)} segments, max gap: {max_gap:.2e} (TOO LARGE!)"
                    )
                    all_continuous = False
            else:
                print(f"  ✅ {name}: {len(shape.segments)} segment (single segment)")

        except Exception as e:
            print(f"  ❌ {name}: FAILED - {e}")
            all_continuous = False

    # Test that we properly reject discontinuous curves
    print("\n🚫 Testing rejection of discontinuous curves...")

    x, y = sp.symbols("x y")

    try:
        # Create two disconnected line segments
        line1 = PolynomialCurve(y, (x, y))
        line2 = PolynomialCurve(y - 1, (x, y))

        seg1 = TrimmedImplicitCurve(
            line1, lambda x, y: 0 <= x <= 1, endpoints=[(0, 0), (1, 0)]
        )
        seg2 = TrimmedImplicitCurve(
            line2, lambda x, y: 2 <= x <= 3, endpoints=[(2, 1), (3, 1)]
        )  # BIG GAP!

        # This should fail
        discontinuous = CompositeCurve([seg1, seg2], validate_continuity=True)
        print("  ❌ ERROR: Discontinuous curve was accepted! This should have failed.")
        all_continuous = False

    except ValueError as e:
        print(f"  ✅ Good! Discontinuous curve properly rejected: {e}")
    except Exception as e:
        print(f"  ❓ Unexpected error: {e}")
        all_continuous = False

    # Summary
    print("\n📊 CONTINUITY TEST RESULTS:")
    print("=" * 40)

    if all_continuous:
        print("🎉 ALL COMPOSITE CURVES ARE TRULY CONTINUOUS!")
        print("✅ No discontinuous examples remain")
        print("✅ All shapes pass continuity validation")
        print("✅ CompositeCurve properly enforces continuous paths")
        return True
    else:
        print("❌ Some curves are still discontinuous or have issues")
        print("⚠️  CompositeCurve implementation needs more work")
        return False


def test_specific_continuity_cases():
    """Test specific continuity cases that were problematic"""

    print("\n🎯 TESTING SPECIFIC CONTINUITY CASES")
    print("=" * 50)

    # Test the T-shape (should be continuous)
    print("Testing T-shape continuity...")
    try:
        t_shape = create_T_shape()

        # Check that the horizontal and vertical segments connect
        seg1_endpoints = t_shape.segments[0].get_endpoints()  # Horizontal
        seg2_endpoints = t_shape.segments[1].get_endpoints()  # Vertical

        print(f"  Horizontal endpoints: {seg1_endpoints}")
        print(f"  Vertical endpoints: {seg2_endpoints}")

        # They should share the point (0, 0.5)
        shared_point = None
        for h_end in seg1_endpoints:
            for v_end in seg2_endpoints:
                gap = np.sqrt((h_end[0] - v_end[0]) ** 2 + (h_end[1] - v_end[1]) ** 2)
                if gap < 1e-6:
                    shared_point = h_end
                    break

        if shared_point:
            print(f"  ✅ T-shape is continuous at {shared_point}")
        else:
            print("  ❌ T-shape segments don't connect properly")

    except Exception as e:
        print(f"  ❌ T-shape test failed: {e}")

    # Test the zigzag pattern (should be continuous)
    print("\nTesting zigzag pattern continuity...")
    try:
        zigzag = create_zigzag_pattern()

        seg1_endpoints = zigzag.segments[0].get_endpoints()  # First diagonal
        seg2_endpoints = zigzag.segments[1].get_endpoints()  # Second diagonal

        print(f"  First diagonal endpoints: {seg1_endpoints}")
        print(f"  Second diagonal endpoints: {seg2_endpoints}")

        # They should connect at (0, 0.5)
        connection_found = False
        for end1 in seg1_endpoints:
            for end2 in seg2_endpoints:
                gap = np.sqrt((end1[0] - end2[0]) ** 2 + (end1[1] - end2[1]) ** 2)
                if gap < 1e-6:
                    print(f"  ✅ Zigzag is continuous at {end1}")
                    connection_found = True
                    break

        if not connection_found:
            print("  ❌ Zigzag segments don't connect properly")

    except Exception as e:
        print(f"  ❌ Zigzag test failed: {e}")


if __name__ == "__main__":
    continuous = test_continuity_enforcement()
    test_specific_continuity_cases()

    if continuous:
        print("\n🚀 SUCCESS: All composite curves are truly continuous!")
        print(
            "CompositeCurve now properly represents 'continuous paths with connectivity checking'"
        )
    else:
        print("\n⚠️  ISSUES REMAIN: Some curves are still not properly continuous")
