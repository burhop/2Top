#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.composite_curve import create_square_from_edges
from geometry.area_region import AreaRegion

def debug_outer_boundary_detailed():
    """Debug the outer boundary containment in detail"""
    print("=== Debugging Outer Boundary Containment ===")
    
    # Recreate the test case
    outer = create_square_from_edges((-3, -3), (3, 3))
    original = AreaRegion(outer, [])  # No holes for simplicity
    
    # Test point
    test_x, test_y = 0, 0
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Square bounds: (-3, -3) to (3, 3)")
    
    # Test original
    print("\n=== Original Outer Boundary ===")
    original_outer = original.outer_boundary
    print(f"Is closed: {original_outer.is_closed()}")
    print(f"Number of segments: {len(original_outer.segments)}")
    
    # Test each segment
    for i, segment in enumerate(original_outer.segments):
        contains_result = segment.contains(test_x, test_y)
        mask_result = segment.mask(test_x, test_y)
        curve_value = segment.base_curve.evaluate(test_x, test_y)
        print(f"  Segment {i}: contains={contains_result}, mask={mask_result}, curve_eval={curve_value}")
    
    # Test region containment
    region_contains = original_outer.contains(test_x, test_y, region_containment=True)
    boundary_contains = original_outer.contains(test_x, test_y, region_containment=False)
    print(f"Region containment: {region_contains}")
    print(f"Boundary containment: {boundary_contains}")
    
    # Test serialization
    print("\n=== Serialization/Deserialization ===")
    data = original.to_dict()
    reconstructed = AreaRegion.from_dict(data)
    
    # Test reconstructed
    print("\n=== Reconstructed Outer Boundary ===")
    reconstructed_outer = reconstructed.outer_boundary
    print(f"Is closed: {reconstructed_outer.is_closed()}")
    print(f"Number of segments: {len(reconstructed_outer.segments)}")
    
    # Test each segment
    for i, segment in enumerate(reconstructed_outer.segments):
        contains_result = segment.contains(test_x, test_y)
        mask_result = segment.mask(test_x, test_y)
        curve_value = segment.base_curve.evaluate(test_x, test_y)
        print(f"  Segment {i}: contains={contains_result}, mask={mask_result}, curve_eval={curve_value}")
    
    # Test region containment
    region_contains = reconstructed_outer.contains(test_x, test_y, region_containment=True)
    boundary_contains = reconstructed_outer.contains(test_x, test_y, region_containment=False)
    print(f"Region containment: {region_contains}")
    print(f"Boundary containment: {boundary_contains}")
    
    # Test ray-casting directly
    print("\n=== Ray-casting Analysis ===")
    try:
        original_ray_result = original_outer._point_in_polygon_scalar(float(test_x), float(test_y))
        reconstructed_ray_result = reconstructed_outer._point_in_polygon_scalar(float(test_x), float(test_y))
        print(f"Original ray-casting result: {original_ray_result}")
        print(f"Reconstructed ray-casting result: {reconstructed_ray_result}")
    except Exception as e:
        print(f"Ray-casting error: {e}")
    
    # Compare mask functions
    print("\n=== Mask Function Comparison ===")
    for i in range(len(original_outer.segments)):
        orig_segment = original_outer.segments[i]
        recon_segment = reconstructed_outer.segments[i]
        
        print(f"Segment {i}:")
        print(f"  Original mask type: {type(orig_segment.mask)}")
        print(f"  Reconstructed mask type: {type(recon_segment.mask)}")
        
        # Test mask at several points
        test_points = [(0, 0), (1, 1), (-1, -1), (2, 2)]
        for px, py in test_points:
            orig_mask = orig_segment.mask(px, py)
            recon_mask = recon_segment.mask(px, py)
            if orig_mask != recon_mask:
                print(f"  DIFFERENCE at ({px}, {py}): orig={orig_mask}, recon={recon_mask}")

if __name__ == "__main__":
    debug_outer_boundary_detailed()
