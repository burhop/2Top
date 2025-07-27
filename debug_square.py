#!/usr/bin/env python3
"""
Debug script for square creation issues.
"""

from geometry import create_square_from_edges
import numpy as np

def debug_square():
    """Debug square creation and properties."""
    print("Creating square from edges (-1, -1) to (1, 1)...")
    
    try:
        square = create_square_from_edges((-1, -1), (1, 1))
        print(f"Square created successfully with {len(square.segments)} segments")
        
        # Test individual segments
        print("\nSegment details:")
        for i, seg in enumerate(square.segments):
            print(f"  Segment {i}: {seg.base_curve.expression}")
            print(f"    Mask function: {seg.mask}")
        
        # Test containment
        print("\nTesting containment:")
        test_points = [
            (0, 0, "center"),
            (0.5, 0.5, "inside"),
            (2, 0, "outside"),
            (-0.5, -0.5, "inside"),
            (1.5, 1.5, "outside")
        ]
        
        for x, y, desc in test_points:
            result = square.contains(x, y)
            print(f"  Point ({x}, {y}) [{desc}]: {result}")
        
        # Test is_closed
        print(f"\nIs closed: {square.is_closed()}")
        
        # Test individual segment evaluation
        print("\nSegment evaluations at (0, 0):")
        for i, seg in enumerate(square.segments):
            base_eval = seg.base_curve.evaluate(0, 0)
            mask_eval = seg.mask(0, 0)
            contains_eval = seg.contains(0, 0)
            print(f"  Segment {i}: base={base_eval}, mask={mask_eval}, contains={contains_eval}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_square()
