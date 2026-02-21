#!/usr/bin/env python3
"""
Test edge cases and potential issues with implicit curve evaluators
"""

import sympy as sp
import numpy as np
from geometry import *

def test_edge_cases():
    """Test edge cases that might reveal issues"""
    
    x, y = sp.symbols('x y')
    
    print("🚨 EDGE CASE TESTING FOR CURVE EVALUATORS")
    print("=" * 50)
    
    # 1. Numerical Stability Tests
    print("\n1. 🔢 Numerical Stability:")
    
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    
    # Very small numbers
    tiny_val = circle.evaluate(1e-15, 1e-15)
    print(f"  Circle at tiny coords: {tiny_val} (should be ≈ -1)")
    
    # Very large numbers
    large_val = circle.evaluate(1e6, 1e6)
    print(f"  Circle at large coords: {large_val} (should be ≈ 2e12)")
    
    # Near-zero on curve
    near_zero = circle.evaluate(1.0, 1e-15)
    print(f"  Circle near (1,0): {near_zero} (should be ≈ 0)")
    
    # 2. Superellipse Edge Cases
    print("\n2. ⭐ Superellipse Edge Cases:")
    
    # Very high n (approaching square)
    super_high_n = Superellipse(a=1.0, b=1.0, n=100.0, variables=(x, y))
    val_high_n = super_high_n.evaluate(0.9, 0.9)
    print(f"  Super-square (n=100) at (0.9,0.9): {val_high_n}")
    
    # Very low n (approaching diamond)
    super_low_n = Superellipse(a=1.0, b=1.0, n=0.5, variables=(x, y))
    val_low_n = super_low_n.evaluate(0.5, 0.5)
    print(f"  Super-diamond (n=0.5) at (0.5,0.5): {val_low_n}")
    
    # Different aspect ratios
    super_stretched = Superellipse(a=5.0, b=0.2, n=2.0, variables=(x, y))
    val_stretched = super_stretched.evaluate(2.5, 0.1)
    print(f"  Stretched superellipse at (2.5,0.1): {val_stretched}")
    
    # 3. Composite Curve Tests
    print("\n3. 🔗 Composite Curve Tests:")
    
    # Create a square
    square = create_square_from_edges((-1, -1), (1, 1))
    
    # Test closure
    print(f"  Square is closed: {square.is_closed()}")
    
    # Test evaluation at corners and edges
    corner_val = square.evaluate(1, 1)
    print(f"  Square at corner (1,1): {corner_val}")
    
    edge_val = square.evaluate(1, 0)
    print(f"  Square at edge (1,0): {edge_val}")
    
    inside_val = square.evaluate(0, 0)
    print(f"  Square at center (0,0): {inside_val}")
    
    # 4. Area Region Tests
    print("\n4. 🏠 Area Region Tests:")
    
    region = AreaRegion(square)
    
    # Test containment
    contains_center = region.contains(0, 0)
    contains_outside = region.contains(2, 2)
    contains_edge = region.contains(1, 0)
    
    print(f"  Region contains (0,0): {contains_center} (should be True)")
    print(f"  Region contains (2,2): {contains_outside} (should be False)")
    print(f"  Region contains (1,0): {contains_edge} (edge case)")
    
    # 5. Constructive Geometry Edge Cases
    print("\n5. 🔗 Constructive Geometry Edge Cases:")
    
    # Overlapping circles
    c1 = ConicSection(x**2 + y**2 - 1, (x, y))
    c2 = ConicSection((x-0.5)**2 + y**2 - 1, (x, y))
    
    union_overlap = union(c1, c2)
    intersect_overlap = intersect(c1, c2)
    
    # Test at overlap region
    overlap_point = (0.25, 0)
    union_val = union_overlap.evaluate(*overlap_point)
    intersect_val = intersect_overlap.evaluate(*overlap_point)
    
    print(f"  Union at overlap {overlap_point}: {union_val}")
    print(f"  Intersection at overlap {overlap_point}: {intersect_val}")
    
    # Blend with extreme alpha values
    blend_extreme = blend(c1, c2, alpha=0.99)
    blend_val = blend_extreme.evaluate(0, 0)
    print(f"  Blend (α=0.99) at (0,0): {blend_val}")
    
    # 6. Gradient Edge Cases
    print("\n6. 📈 Gradient Edge Cases:")
    
    # Gradient at singularities
    try:
        # Cusp-like curve: y² - x³ = 0
        cusp = PolynomialCurve(y**2 - x**3, (x, y))
        gx, gy = cusp.gradient(0, 0)  # Singularity at origin
        print(f"  Cusp gradient at (0,0): ({gx}, {gy})")
    except Exception as e:
        print(f"  Cusp gradient failed: {e}")
    
    # Very flat curve
    flat_curve = PolynomialCurve(y - 0.001*x**2, (x, y))
    gx, gy = flat_curve.gradient(10, 0.1)
    print(f"  Flat curve gradient: ({gx}, {gy})")
    
    # 7. Serialization Edge Cases
    print("\n7. 💾 Serialization Edge Cases:")
    
    # Complex expression
    complex_poly = PolynomialCurve(x**4 + y**4 - 2*x**2*y**2 + x*y - 1, (x, y))
    
    try:
        serialized = complex_poly.to_dict()
        reconstructed = PolynomialCurve.from_dict(serialized)
        
        # Test equivalence
        test_point = (0.5, 0.3)
        orig_val = complex_poly.evaluate(*test_point)
        recon_val = reconstructed.evaluate(*test_point)
        
        serialization_ok = abs(orig_val - recon_val) < 1e-10
        status = "✅" if serialization_ok else "❌"
        print(f"  {status} Complex polynomial serialization: {orig_val} vs {recon_val}")
        
    except Exception as e:
        print(f"  ❌ Serialization failed: {e}")
    
    # 8. Performance Edge Cases
    print("\n8. ⚡ Performance Edge Cases:")
    
    # Large array evaluation
    large_x = np.random.uniform(-2, 2, 10000)
    large_y = np.random.uniform(-2, 2, 10000)
    
    import time
    start_time = time.time()
    large_results = circle.evaluate(large_x, large_y)
    end_time = time.time()
    
    print(f"  Large array (10k points) evaluation: {end_time - start_time:.4f}s")
    print(f"  Results shape: {large_results.shape}")
    print(f"  Sample results: {large_results[:5]}")
    
    # 9. Special Values
    print("\n9. 🎯 Special Values:")
    
    # NaN handling
    try:
        nan_result = circle.evaluate(np.nan, 0)
        print(f"  Circle with NaN input: {nan_result}")
    except Exception as e:
        print(f"  NaN handling: {e}")
    
    # Infinity handling
    try:
        inf_result = circle.evaluate(np.inf, 0)
        print(f"  Circle with inf input: {inf_result}")
    except Exception as e:
        print(f"  Infinity handling: {e}")
    
    print("\n🎯 Edge case testing complete!")

if __name__ == "__main__":
    test_edge_cases()