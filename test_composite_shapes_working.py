#!/usr/bin/env python3
"""
Test that composite shapes are working with the fixes
"""

import sys
import sympy as sp
from geometry import *
from geometry.factories import *

def test_all_composite_shapes():
    """Test all composite shape creators"""
    
    print("🏗️ TESTING ALL COMPOSITE SHAPES")
    print("=" * 50)
    
    shapes_to_test = [
        ("L-Shape", create_L_shape),
        ("Plus Sign", create_plus_sign),
        ("Triangle", create_triangle),
        ("House Shape", create_house_shape),
        ("Cross Pattern", create_cross_pattern),
        ("Staircase", create_staircase),
        ("Two Semicircles", create_two_semicircles),
        ("Square", lambda: create_square_from_edges((-1, -1), (1, 1))),
        ("Circle Quarters", lambda: create_circle_from_quarters(center=(0, 0), radius=1.0)),
    ]
    
    results = []
    
    for name, creator in shapes_to_test:
        print(f"\n🔧 Testing {name}...")
        try:
            shape = creator()
            
            # Basic tests
            assert isinstance(shape, CompositeCurve)
            assert len(shape.segments) > 0
            
            # Test basic methods
            bbox = shape.bounding_box()
            assert len(bbox) == 4
            
            # Test evaluation
            val = shape.evaluate(0, 0)
            assert isinstance(val, (int, float))
            
            # Test contains
            contains_result = shape.contains(0, 0)
            assert isinstance(contains_result, (bool, np.bool_))
            
            # Test is_closed
            is_closed = shape.is_closed()
            assert isinstance(is_closed, bool)
            
            print(f"  ✅ {name}: {len(shape.segments)} segments, closed={is_closed}")
            results.append((name, True, None))
            
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results.append((name, False, str(e)))
    
    # Summary
    print(f"\n📊 RESULTS SUMMARY:")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    for name, success, error in results:
        if success:
            print(f"✅ {name}")
            passed += 1
        else:
            print(f"❌ {name}: {error}")
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL COMPOSITE SHAPES WORKING!")
        return True
    else:
        print("⚠️  Some shapes still have issues")
        return False


def test_continuity_validation():
    """Test continuity validation is working"""
    
    print(f"\n🔗 TESTING CONTINUITY VALIDATION")
    print("=" * 40)
    
    x, y = sp.symbols('x y')
    
    # Test 1: Continuous segments (should work)
    print("Testing continuous segments...")
    try:
        line1 = PolynomialCurve(y, (x, y))
        line2 = PolynomialCurve(x - 1, (x, y))
        
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: 0 <= x <= 1, endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: 0 <= y <= 1, endpoints=[(1, 0), (1, 1)])
        
        composite = CompositeCurve([seg1, seg2], validate_continuity=True)
        print("  ✅ Continuous segments accepted")
        
    except Exception as e:
        print(f"  ❌ Continuous segments failed: {e}")
    
    # Test 2: Discontinuous segments (should fail)
    print("Testing discontinuous segments...")
    try:
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: 0 <= x <= 1, endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: 0 <= y <= 1, endpoints=[(2, 1), (2, 2)])  # Gap!
        
        composite = CompositeCurve([seg1, seg2], validate_continuity=True)
        print("  ❌ Discontinuous segments should have failed!")
        
    except ValueError as e:
        print(f"  ✅ Discontinuous segments properly rejected: {e}")
    except Exception as e:
        print(f"  ❓ Unexpected error: {e}")


if __name__ == "__main__":
    shapes_working = test_all_composite_shapes()
    test_continuity_validation()
    
    if shapes_working:
        print(f"\n🚀 COMPOSITE CURVES ARE READY!")
        print("You can now run clean_curve_visualizer.py to see them in action.")
    else:
        print(f"\n⚠️  Some issues remain to be fixed.")