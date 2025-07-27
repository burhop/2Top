#!/usr/bin/env python3
"""
Debug script for signed distance field issues.
"""

from geometry import *
import numpy as np

def debug_signed_distance():
    print("=== Debugging Signed Distance Field ===")
    
    # Create a simple square region
    square = create_square_from_edges((0, 0), (4, 4))
    region = AreaRegion(square)
    
    print(f"Square region created with {len(square.segments)} segments")
    
    # Create signed distance field
    strategy = SignedDistanceStrategy(resolution=0.1)
    field = region.get_field(strategy)
    
    print(f"Field created with resolution: {field.resolution}")
    
    # Test point that should be outside
    test_x, test_y = 5.0, 5.0
    
    print(f"\nTesting point ({test_x}, {test_y})")
    
    # Check if point is inside region
    is_inside = region.contains(test_x, test_y)
    print(f"Point is inside region: {is_inside}")
    
    # Get boundary points
    boundary_points = field._get_boundary_points()
    print(f"Number of boundary points: {len(boundary_points)}")
    
    if boundary_points:
        print("First few boundary points:")
        for i, (bx, by) in enumerate(boundary_points[:5]):
            print(f"  Point {i}: ({bx}, {by})")
        
        # Calculate distance manually
        min_distance = float('inf')
        for bx, by in boundary_points:
            distance = np.sqrt((test_x - bx)**2 + (test_y - by)**2)
            min_distance = min(min_distance, distance)
        
        print(f"Manual minimum distance calculation: {min_distance}")
    else:
        print("No boundary points found!")
    
    # Test the field evaluation
    result = field.evaluate(test_x, test_y)
    print(f"Field evaluation result: {result}")
    print(f"Expected: positive value (> 0)")
    print(f"Test passes: {result > 0}")
    
    # Test a few more points
    print("\n=== Additional Test Points ===")
    test_points = [
        (2.0, 2.0),  # Inside
        (0.0, 2.0),  # On boundary
        (6.0, 6.0),  # Far outside
        (-1.0, -1.0)  # Outside on other side
    ]
    
    for px, py in test_points:
        inside = region.contains(px, py)
        value = field.evaluate(px, py)
        print(f"Point ({px}, {py}): inside={inside}, value={value}")

if __name__ == "__main__":
    debug_signed_distance()
