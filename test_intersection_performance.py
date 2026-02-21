#!/usr/bin/env python3
"""
Test intersection finding performance
"""

import time
import numpy as np
import sympy as sp
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_intersection_performance():
    """Test performance of intersection finding"""
    
    print("⚡ INTERSECTION PERFORMANCE TEST")
    print("=" * 50)
    
    x, y = sp.symbols('x y')
    
    # Test cases with different complexity
    test_cases = [
        # Simple case: two circles
        (ConicSection(x**2 + y**2 - 1, (x, y)), 
         ConicSection((x-1)**2 + y**2 - 1, (x, y)),
         "Two Circles"),
        
        # Trimmed curves
        (TrimmedImplicitCurve(ConicSection(x**2 + y**2 - 1, (x, y)), lambda x, y: x >= 0),
         PolynomialCurve(y, (x, y)),
         "Trimmed Circle vs Line"),
        
        # Complex curves
        (PolynomialCurve(x**3 + y**3 - 1, (x, y)),
         ConicSection(x**2 + y**2 - 1, (x, y)),
         "Cubic vs Circle"),
    ]
    
    for curve1, curve2, name in test_cases:
        print(f"\n🔍 {name}")
        print("-" * 30)
        
        # Test without overlap detection (fast)
        start_time = time.time()
        intersections_fast = find_curve_intersections(
            curve1, curve2,
            search_range=3.0,
            grid_resolution=400,
            tolerance=1e-8,
            detect_overlap=False
        )
        fast_time = time.time() - start_time
        
        # Test with overlap detection (slower)
        start_time = time.time()
        intersections_slow = find_curve_intersections(
            curve1, curve2,
            search_range=3.0,
            grid_resolution=400,
            tolerance=1e-8,
            detect_overlap=True
        )
        slow_time = time.time() - start_time
        
        print(f"  Fast mode:  {len(intersections_fast)} intersections in {fast_time:.3f}s")
        print(f"  Slow mode:  {len(intersections_slow)} intersections in {slow_time:.3f}s")
        print(f"  Speedup:    {slow_time/fast_time:.1f}x faster")
        
        # Show intersection points
        if intersections_fast:
            print(f"  Points (fast): {intersections_fast[:3]}{'...' if len(intersections_fast) > 3 else ''}")
        if intersections_slow:
            print(f"  Points (slow): {intersections_slow[:3]}{'...' if len(intersections_slow) > 3 else ''}")
    
    print(f"\n✅ Performance test complete!")
    print(f"💡 Recommendation: Use detect_overlap=False for interactive applications")

if __name__ == "__main__":
    test_intersection_performance()