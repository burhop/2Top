#!/usr/bin/env python3

import sympy as sp
import numpy as np
from geometry.composite_curve import create_square_from_edges
from geometry.area_region import AreaRegion

def debug_area_region_serialization():
    """Debug the area region serialization test case"""
    print("=== Debugging Area Region Serialization Test Case ===")
    
    # Recreate the test case
    outer = create_square_from_edges((-3, -3), (3, 3))
    hole1 = create_square_from_edges((-2, -2), (-1, -1))
    hole2 = create_square_from_edges((1, 1), (2, 2))
    original = AreaRegion(outer, [hole1, hole2])
    
    # Test point that should be between holes
    test_x, test_y = 0, 0
    
    print(f"Test point: ({test_x}, {test_y})")
    print(f"Expected: point should be inside outer boundary but not in any hole")
    
    # Test original region
    original_contains = original.contains(test_x, test_y)
    print(f"Original region contains point: {original_contains}")
    
    # Test serialization
    print("\n=== Serialization ===")
    data = original.to_dict()
    print(f"Serialized data keys: {list(data.keys())}")
    print(f"Outer boundary type: {data['outer_boundary']['type']}")
    print(f"Number of holes: {len(data['holes'])}")
    
    # Test deserialization
    print("\n=== Deserialization ===")
    reconstructed = AreaRegion.from_dict(data)
    reconstructed_contains = reconstructed.contains(test_x, test_y)
    print(f"Reconstructed region contains point: {reconstructed_contains}")
    
    # Debug individual components
    print("\n=== Component Analysis ===")
    
    # Test outer boundary
    print("Outer boundary:")
    outer_original = original.outer_boundary.contains(test_x, test_y, region_containment=True)
    outer_reconstructed = reconstructed.outer_boundary.contains(test_x, test_y, region_containment=True)
    print(f"  Original outer contains point: {outer_original}")
    print(f"  Reconstructed outer contains point: {outer_reconstructed}")
    
    # Test holes
    print("Holes:")
    for i, (hole_orig, hole_recon) in enumerate(zip(original.holes, reconstructed.holes)):
        hole_orig_contains = hole_orig.contains(test_x, test_y, region_containment=True)
        hole_recon_contains = hole_recon.contains(test_x, test_y, region_containment=True)
        print(f"  Hole {i+1} original contains point: {hole_orig_contains}")
        print(f"  Hole {i+1} reconstructed contains point: {hole_recon_contains}")
    
    # Debug mask functions for first segment of outer boundary
    print("\n=== Mask Function Analysis ===")
    orig_segment = original.outer_boundary.segments[0]
    recon_segment = reconstructed.outer_boundary.segments[0]
    
    print(f"Original segment mask at ({test_x}, {test_y}): {orig_segment.mask(test_x, test_y)}")
    print(f"Reconstructed segment mask at ({test_x}, {test_y}): {recon_segment.mask(test_x, test_y)}")
    
    # Test curve evaluation
    curve_value_orig = orig_segment.base_curve.evaluate(test_x, test_y)
    curve_value_recon = recon_segment.base_curve.evaluate(test_x, test_y)
    print(f"Original curve evaluation: {curve_value_orig}")
    print(f"Reconstructed curve evaluation: {curve_value_recon}")

if __name__ == "__main__":
    debug_area_region_serialization()
