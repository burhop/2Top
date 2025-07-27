#!/usr/bin/env python3

import sympy as sp
from geometry.composite_curve import create_square_from_edges

def test_square_evaluation():
    """Debug test for square evaluation."""
    
    # Create a square with corners (-1, -1) and (1, 1)
    square = create_square_from_edges(corner1=(-1, -1), corner2=(1, 1))
    
    print(f"Square has {len(square.segments)} segments")
    
    # Test point (1.0, 0.0) which should be on the right edge
    test_point = (1.0, 0.0)
    print(f"\nTesting point {test_point}:")
    
    # Evaluate each segment individually
    for i, segment in enumerate(square.segments):
        seg_value = segment.evaluate(test_point[0], test_point[1])
        print(f"Segment {i}: {seg_value}")
        print(f"  Base curve: {segment.base_curve}")
        print(f"  Contains point: {segment.contains(test_point[0], test_point[1])}")
    
    # Evaluate the composite curve
    composite_value = square.evaluate(test_point[0], test_point[1])
    print(f"\nComposite curve value: {composite_value}")
    
    # Test a few more points
    test_points = [
        (0.0, -1.0),  # Bottom edge
        (0.0, 1.0),   # Top edge  
        (-1.0, 0.0),  # Left edge
        (0.0, 0.0),   # Center (should be negative)
        (2.0, 0.0),   # Outside (should be positive)
    ]
    
    print(f"\nTesting additional points:")
    for point in test_points:
        value = square.evaluate(point[0], point[1])
        print(f"Point {point}: {value}")

if __name__ == "__main__":
    test_square_evaluation()
