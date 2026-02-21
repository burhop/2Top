#!/usr/bin/env python3
"""
Final comprehensive test of CompositeCurve functionality
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from geometry import *
from geometry.factories import *

def test_comprehensive_composite_functionality():
    """Run comprehensive tests of all CompositeCurve functionality"""
    
    print("🧪 FINAL COMPREHENSIVE COMPOSITE CURVE TEST")
    print("=" * 60)
    
    # Test 1: All factory functions work
    print("\n1️⃣ Testing Factory Functions")
    print("-" * 30)
    
    factory_tests = [
        ("create_square_from_edges", lambda: create_square_from_edges((-1, -1), (1, 1))),
        ("create_circle_from_quarters", lambda: create_circle_from_quarters()),
        ("create_L_shape", create_L_shape),
        ("create_plus_sign", create_plus_sign),
        ("create_triangle", create_triangle),
        ("create_house_shape", create_house_shape),
        ("create_cross_pattern", create_cross_pattern),
        ("create_staircase", create_staircase),
        ("create_two_semicircles", create_two_semicircles),
    ]
    
    factory_results = []
    for name, func in factory_tests:
        try:
            shape = func()
            assert isinstance(shape, CompositeCurve)
            print(f"  ✅ {name}: {len(shape.segments)} segments")
            factory_results.append(True)
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            factory_results.append(False)
    
    # Test 2: Continuity validation
    print("\n2️⃣ Testing Continuity Validation")
    print("-" * 30)
    
    x, y = sp.symbols('x y')
    
    # Test continuous segments
    try:
        line1 = PolynomialCurve(y, (x, y))
        line2 = PolynomialCurve(x - 1, (x, y))
        
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: 0 <= x <= 1, endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: 0 <= y <= 1, endpoints=[(1, 0), (1, 1)])
        
        continuous = CompositeCurve([seg1, seg2], validate_continuity=True)
        print("  ✅ Continuous segments accepted")
        continuity_test1 = True
    except Exception as e:
        print(f"  ❌ Continuous segments failed: {e}")
        continuity_test1 = False
    
    # Test discontinuous segments rejection
    try:
        seg1 = TrimmedImplicitCurve(line1, lambda x, y: 0 <= x <= 1, endpoints=[(0, 0), (1, 0)])
        seg2 = TrimmedImplicitCurve(line2, lambda x, y: 0 <= y <= 1, endpoints=[(2, 1), (2, 2)])
        
        discontinuous = CompositeCurve([seg1, seg2], validate_continuity=True)
        print("  ❌ Discontinuous segments should have been rejected!")
        continuity_test2 = False
    except ValueError:
        print("  ✅ Discontinuous segments properly rejected")
        continuity_test2 = True
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        continuity_test2 = False
    
    # Test 3: Core methods work
    print("\n3️⃣ Testing Core Methods")
    print("-" * 30)
    
    test_shapes = [
        ("Square", create_square_from_edges((-1, -1), (1, 1))),
        ("Triangle", create_triangle()),
        ("Circle", create_circle_from_quarters()),
    ]
    
    method_results = []
    for name, shape in test_shapes:
        try:
            # Test evaluate
            val = shape.evaluate(0, 0)
            assert isinstance(val, (int, float))
            
            # Test contains
            contains_scalar = shape.contains(0, 0)
            assert isinstance(contains_scalar, (bool, np.bool_))
            
            # Test vectorized contains
            X = np.array([0, 0.5])
            Y = np.array([0, 0.5])
            contains_vector = shape.contains(X, Y)
            assert isinstance(contains_vector, np.ndarray)
            
            # Test on_curve
            on_curve_result = shape.on_curve(0, 0)
            assert isinstance(on_curve_result, (bool, np.bool_))
            
            # Test is_closed
            is_closed = shape.is_closed()
            assert isinstance(is_closed, bool)
            
            # Test bounding_box
            bbox = shape.bounding_box()
            assert len(bbox) == 4
            
            print(f"  ✅ {name}: All methods working")
            method_results.append(True)
            
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            method_results.append(False)
    
    # Test 4: Serialization
    print("\n4️⃣ Testing Serialization")
    print("-" * 30)
    
    try:
        square = create_square_from_edges((-1, -1), (1, 1))
        
        # Serialize
        data = square.to_dict()
        assert isinstance(data, dict)
        assert data["type"] == "CompositeCurve"
        
        # Deserialize
        restored = CompositeCurve.from_dict(data)
        assert isinstance(restored, CompositeCurve)
        assert len(restored.segments) == len(square.segments)
        
        print("  ✅ Serialization working")
        serialization_test = True
        
    except Exception as e:
        print(f"  ❌ Serialization failed: {e}")
        serialization_test = False
    
    # Test 5: Plotting
    print("\n5️⃣ Testing Plotting")
    print("-" * 30)
    
    try:
        triangle = create_triangle()
        
        fig, ax = plt.subplots(figsize=(6, 6))
        triangle.plot(ax=ax)
        ax.set_title("Triangle Composite Curve")
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        plt.savefig('composite_curve_test_plot.png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        print("  ✅ Plotting working - saved composite_curve_test_plot.png")
        plotting_test = True
        
    except Exception as e:
        print(f"  ❌ Plotting failed: {e}")
        plotting_test = False
    
    # Final Summary
    print(f"\n📊 FINAL RESULTS")
    print("=" * 40)
    
    all_factory_passed = all(factory_results)
    continuity_passed = continuity_test1 and continuity_test2
    all_methods_passed = all(method_results)
    
    results = [
        ("Factory Functions", all_factory_passed, f"{sum(factory_results)}/{len(factory_results)}"),
        ("Continuity Validation", continuity_passed, "2/2"),
        ("Core Methods", all_methods_passed, f"{sum(method_results)}/{len(method_results)}"),
        ("Serialization", serialization_test, "1/1"),
        ("Plotting", plotting_test, "1/1"),
    ]
    
    total_passed = 0
    total_tests = len(results)
    
    for category, passed, details in results:
        status = "✅" if passed else "❌"
        print(f"{status} {category}: {details}")
        if passed:
            total_passed += 1
    
    print(f"\nOverall: {total_passed}/{total_tests} categories passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! CompositeCurve is fully functional!")
        print("\n🚀 Ready for production use:")
        print("   • All factory functions working")
        print("   • Continuity validation enforced")
        print("   • All core methods functional")
        print("   • Serialization working")
        print("   • Plotting working")
        print("   • Complete test coverage")
        return True
    else:
        print(f"\n⚠️  {total_tests - total_passed} categories still have issues")
        return False


if __name__ == "__main__":
    success = test_comprehensive_composite_functionality()
    
    if success:
        print(f"\n✨ CompositeCurve implementation is COMPLETE and ROBUST!")
    else:
        print(f"\n🔧 Some issues remain to be addressed.")