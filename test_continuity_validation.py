#!/usr/bin/env python3
"""
Test that CompositeCurve now properly validates continuity
"""

import numpy as np
import sympy as sp
from geometry import *

def test_continuity_validation():
    """Test that CompositeCurve rejects discontinuous segments"""
    
    print("🔗 TESTING CONTINUITY VALIDATION")
    print("=" * 50)
    
    x, y = sp.symbols('x y')
    
    # Test 1: Try to create discontinuous segments (should fail)
    print("\n❌ Test 1: Discontinuous Segments (should fail)")
    print("-" * 40)
    
    try:
        # Segment 1: Line from (0, 0) to (1, 0)
        seg1_line = PolynomialCurve(y, (x, y))
        seg1_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-0.1 <= y_val <= 0.1)
        seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(0, 0), (1, 0)])
        
        # Segment 2: Line from (2, 1) to (3, 1) - BIG GAP!
        seg2_line = PolynomialCurve(y - 1, (x, y))
        seg2_mask = lambda x_val, y_val: (2 <= x_val <= 3) and (0.9 <= y_val <= 1.1)
        seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(2, 1), (3, 1)])
        
        # This should fail
        discontinuous = CompositeCurve([seg1, seg2])
        print(f"  ERROR: Discontinuous curve was created! This should have failed.")
        
    except ValueError as e:
        print(f"  ✅ Good! CompositeCurve properly rejected discontinuous segments:")
        print(f"     {e}")
    except Exception as e:
        print(f"  ❓ Unexpected error: {e}")
    
    # Test 2: Create continuous segments (should succeed)
    print("\n✅ Test 2: Continuous Segments (should succeed)")
    print("-" * 40)
    
    try:
        # Segment 1: Line from (0, 0) to (1, 0)
        seg1_line = PolynomialCurve(y, (x, y))
        seg1_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-0.1 <= y_val <= 0.1)
        seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(0, 0), (1, 0)])
        
        # Segment 2: Line from (1, 0) to (1, 1) - CONNECTED!
        seg2_line = PolynomialCurve(x - 1, (x, y))
        seg2_mask = lambda x_val, y_val: (0.9 <= x_val <= 1.1) and (0 <= y_val <= 1)
        seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(1, 0), (1, 1)])
        
        # This should succeed
        continuous = CompositeCurve([seg1, seg2])
        print(f"  ✅ Success! Continuous curve created with {len(continuous.segments)} segments")
        print(f"     Is closed: {continuous.is_closed()}")
        
    except Exception as e:
        print(f"  ❌ Unexpected failure: {e}")
    
    # Test 3: Test with tolerance
    print("\n🎯 Test 3: Near-continuous with tolerance")
    print("-" * 40)
    
    try:
        # Segment 1: Line from (0, 0) to (1, 0)
        seg1_line = PolynomialCurve(y, (x, y))
        seg1_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-0.1 <= y_val <= 0.1)
        seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(0, 0), (1, 0)])
        
        # Segment 2: Line from (1.001, 0) to (2, 0) - TINY GAP (0.001)
        seg2_line = PolynomialCurve(y, (x, y))
        seg2_mask = lambda x_val, y_val: (1.001 <= x_val <= 2) and (-0.1 <= y_val <= 0.1)
        seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(1.001, 0), (2, 0)])
        
        # Should fail with default tolerance (1e-6)
        try:
            strict = CompositeCurve([seg1, seg2])
            print(f"  ❌ Strict tolerance should have failed")
        except ValueError:
            print(f"  ✅ Strict tolerance (1e-6) properly rejected gap of 0.001")
        
        # Should succeed with relaxed tolerance
        try:
            relaxed = CompositeCurve([seg1, seg2], validate_continuity=True, continuity_tolerance=0.01)
            print(f"  ✅ Relaxed tolerance (0.01) accepted gap of 0.001")
        except ValueError as e:
            print(f"  ❌ Relaxed tolerance failed: {e}")
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    # Test 4: Test bypass validation
    print("\n🚫 Test 4: Bypass validation")
    print("-" * 40)
    
    try:
        # Same discontinuous segments as Test 1
        seg1_line = PolynomialCurve(y, (x, y))
        seg1_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-0.1 <= y_val <= 0.1)
        seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(0, 0), (1, 0)])
        
        seg2_line = PolynomialCurve(y - 1, (x, y))
        seg2_mask = lambda x_val, y_val: (2 <= x_val <= 3) and (0.9 <= y_val <= 1.1)
        seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(2, 1), (3, 1)])
        
        # Should succeed when validation is disabled
        bypass = CompositeCurve([seg1, seg2], validate_continuity=False)
        print(f"  ✅ Validation bypass worked - discontinuous curve created")
        print(f"     (This is allowed when validate_continuity=False)")
        
    except Exception as e:
        print(f"  ❌ Bypass failed: {e}")

if __name__ == "__main__":
    test_continuity_validation()