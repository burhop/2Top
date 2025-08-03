#!/usr/bin/env python3
"""
Debug test specifically for endpoint detection in trimmed curves.
"""

import numpy as np
import sympy as sp
from geometry import PolynomialCurve, TrimmedImplicitCurve

def debug_endpoint_detection():
    """
    Debug the endpoint detection for trimmed line segments.
    """
    print("="*60)
    print("DEBUGGING ENDPOINT DETECTION")
    print("="*60)
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Define triangle vertices (our expected endpoints)
    vertex_A = (-2, -1)  # Bottom left
    vertex_B = (2, -1)   # Bottom right  
    vertex_C = (0, 2)    # Top
    
    print(f"Expected endpoints:")
    print(f"  Segment AB: {vertex_A} to {vertex_B}")
    print(f"  Segment BC: {vertex_B} to {vertex_C}")
    print(f"  Segment CA: {vertex_C} to {vertex_A}")
    
    # Create base line AB: y + 1 = 0
    line_AB_expr = y + 1
    line_AB_base = PolynomialCurve(line_AB_expr, (x, y))
    
    # Create a simple mask for AB segment
    def mask_AB(px, py):
        # On the line y = -1 and between x = -2 and x = 2
        on_line = abs(py + 1) < 0.1
        in_range = -2.1 <= px <= 2.1  # Slightly wider to include endpoints
        return on_line and in_range
    
    # Create trimmed curve
    trimmed_AB = TrimmedImplicitCurve(line_AB_base, mask_AB)
    
    print("\\n" + "="*40)
    print("TESTING TRIMMED CURVE AB")
    print("="*40)
    
    # Test the trimmed curve at expected endpoints and some other points
    test_points = [
        (vertex_A, "Vertex A (expected endpoint)"),
        (vertex_B, "Vertex B (expected endpoint)"),
        ((-1, -1), "Midpoint of AB"),
        ((0, -1), "Center of AB"),
        ((1, -1), "Another point on AB"),
        ((-3, -1), "Outside AB (left)"),
        ((3, -1), "Outside AB (right)"),
        ((0, 0), "Off the line"),
    ]
    
    print("\\nTesting contains() method:")
    for (px, py), description in test_points:
        try:
            # Test base curve
            base_val = line_AB_base.evaluate(px, py)
            # Test mask
            mask_result = mask_AB(px, py)
            # Test trimmed curve contains
            contains_result = trimmed_AB.contains(px, py)
            
            print(f"  {description}:")
            print(f"    Point: ({px}, {py})")
            print(f"    Base curve f(x,y) = {base_val:.6f} {'(on line)' if abs(base_val) < 1e-6 else '(off line)'}")
            print(f"    Mask result: {mask_result}")
            print(f"    Trimmed contains: {contains_result}")
            print()
        except Exception as e:
            print(f"  {description}: ERROR - {e}")
    
    # Test the bounding box method
    print("\\nTesting bounding_box() method:")
    try:
        bbox = trimmed_AB.bounding_box()
        print(f"  Bounding box: {bbox}")
        print(f"  Expected roughly: (-2, 2, -1, -1)")
    except Exception as e:
        print(f"  Bounding box ERROR: {e}")
    
    # Manually test the _get_segment_endpoints logic
    print("\\n" + "="*40)
    print("MANUAL ENDPOINT DETECTION")
    print("="*40)
    
    print("\\nSampling points to find endpoints...")
    
    # Use the same logic as _get_segment_endpoints
    try:
        x_min, x_max, y_min, y_max = trimmed_AB.bounding_box()
        
        # Clamp infinite bounds
        if x_min == float('-inf'):
            x_min = -10
        if x_max == float('inf'):
            x_max = 10
        if y_min == float('-inf'):
            y_min = -10
        if y_max == float('inf'):
            y_max = 10
        
        print(f"Using bounding box: ({x_min}, {x_max}, {y_min}, {y_max})")
        
        # Sample points
        n_samples = 20
        x_vals = np.linspace(x_min, x_max, n_samples)
        y_vals = np.linspace(y_min, y_max, n_samples)
        
        points_on_segment = []
        tolerance = 1e-6
        
        print(f"\\nSampling {n_samples}x{n_samples} = {n_samples*n_samples} points...")
        
        for i, x_val in enumerate(x_vals):
            for j, y_val in enumerate(y_vals):
                try:
                    if trimmed_AB.contains(x_val, y_val, tolerance):
                        points_on_segment.append((x_val, y_val))
                        print(f"  Found point on segment: ({x_val:.3f}, {y_val:.3f})")
                except:
                    pass
        
        print(f"\\nTotal points found on segment: {len(points_on_segment)}")
        
        if len(points_on_segment) >= 2:
            # Find the two points that are farthest apart
            max_distance = 0
            endpoint1, endpoint2 = None, None
            
            for i, p1 in enumerate(points_on_segment):
                for j, p2 in enumerate(points_on_segment[i+1:], i+1):
                    distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                    if distance > max_distance:
                        max_distance = distance
                        endpoint1, endpoint2 = p1, p2
            
            print(f"\\nDetected endpoints:")
            print(f"  Endpoint 1: {endpoint1}")
            print(f"  Endpoint 2: {endpoint2}")
            print(f"  Distance: {max_distance:.6f}")
            print(f"\\nExpected endpoints:")
            print(f"  Vertex A: {vertex_A}")
            print(f"  Vertex B: {vertex_B}")
            print(f"  Expected distance: {np.sqrt((vertex_B[0] - vertex_A[0])**2 + (vertex_B[1] - vertex_A[1])**2):.6f}")
        else:
            print("\\nERROR: Not enough points found on segment to detect endpoints!")
            
    except Exception as e:
        print(f"\\nERROR in manual endpoint detection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\\n" + "="*60)
    print("ENDPOINT DEBUGGING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    debug_endpoint_detection()
