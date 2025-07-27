#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.composite_curve import create_square_from_edges
from geometry.area_region import AreaRegion

def debug_ray_casting_intersections():
    """Debug the ray-casting intersection calculation in detail"""
    print("=== Debugging Ray-casting Intersections ===")
    
    # Recreate the test case
    outer = create_square_from_edges((-3, -3), (3, 3))
    original = AreaRegion(outer, [])  # No holes for simplicity
    
    # Test point
    test_x, test_y = 0, 0
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Square bounds: (-3, -3) to (3, 3)")
    print(f"Expected: ray from (0,0) to right should intersect right edge at (3,0)")
    
    # Test serialization
    data = original.to_dict()
    reconstructed = AreaRegion.from_dict(data)
    
    # Compare ray-casting for both
    original_outer = original.outer_boundary
    reconstructed_outer = reconstructed.outer_boundary
    
    print(f"\n=== Ray-casting Intersection Analysis ===")
    
    # Test each segment's intersection calculation
    for i, (orig_segment, recon_segment) in enumerate(zip(original_outer.segments, reconstructed_outer.segments)):
        print(f"\nSegment {i}:")
        
        # Get base curve info
        orig_curve = orig_segment.base_curve
        recon_curve = recon_segment.base_curve
        
        print(f"  Original curve: {orig_curve.expression}")
        print(f"  Reconstructed curve: {recon_curve.expression}")
        
        # Test intersection calculation manually
        orig_intersections = original_outer._find_ray_segment_intersections(test_x, test_y, orig_segment)
        recon_intersections = reconstructed_outer._find_ray_segment_intersections(test_x, test_y, recon_segment)
        
        print(f"  Original intersections: {orig_intersections}")
        print(f"  Reconstructed intersections: {recon_intersections}")
        
        # Debug the intersection calculation step by step
        if orig_intersections != recon_intersections:
            print(f"  DIFFERENCE FOUND! Debugging segment {i}...")
            
            # Manual calculation
            expr = orig_curve.expression
            x_var, y_var = orig_curve.variables
            
            # Substitute y = test_y
            expr_at_y = expr.subs(y_var, test_y)
            print(f"  Curve equation at y={test_y}: {expr_at_y}")
            
            # Solve for x
            x_solutions = sp.solve(expr_at_y, x_var)
            print(f"  X solutions: {x_solutions}")
            
            for x_sol in x_solutions:
                try:
                    x_val = float(x_sol)
                    print(f"    Solution x={x_val}")
                    
                    if x_val > test_x:
                        print(f"      x_val > ray_x: {x_val} > {test_x} = True")
                        
                        # Test contains for both segments
                        orig_contains = orig_segment.contains(x_val, test_y, tolerance=1e-3)
                        recon_contains = recon_segment.contains(x_val, test_y, tolerance=1e-3)
                        
                        print(f"      Original segment contains ({x_val}, {test_y}): {orig_contains}")
                        print(f"      Reconstructed segment contains ({x_val}, {test_y}): {recon_contains}")
                        
                        if orig_contains != recon_contains:
                            print(f"      CONTAINS DIFFERENCE!")
                            
                            # Debug contains method
                            orig_curve_val = orig_segment.base_curve.evaluate(x_val, test_y)
                            recon_curve_val = recon_segment.base_curve.evaluate(x_val, test_y)
                            orig_mask_val = orig_segment.mask(x_val, test_y)
                            recon_mask_val = recon_segment.mask(x_val, test_y)
                            
                            print(f"        Original: curve_val={orig_curve_val}, mask={orig_mask_val}")
                            print(f"        Reconstructed: curve_val={recon_curve_val}, mask={recon_mask_val}")
                    else:
                        print(f"      x_val <= ray_x: {x_val} <= {test_x} = False (skipped)")
                        
                except (ValueError, TypeError) as e:
                    print(f"    Solution {x_sol} is not numeric: {e}")
    
    # Final ray-casting results
    print(f"\n=== Final Results ===")
    orig_result = original_outer._ray_casting_algorithm(test_x, test_y)
    recon_result = reconstructed_outer._ray_casting_algorithm(test_x, test_y)
    print(f"Original ray-casting: {orig_result}")
    print(f"Reconstructed ray-casting: {recon_result}")

if __name__ == "__main__":
    debug_ray_casting_intersections()
