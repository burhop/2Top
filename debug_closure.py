#!/usr/bin/env python3
"""
Debug test to investigate why CompositeCurve.is_closed() isn't detecting closure.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve, TrimmedImplicitCurve, CompositeCurve

def debug_closure_detection():
    """
    Debug the closure detection for our triangle segments.
    """
    print("="*60)
    print("DEBUGGING CLOSURE DETECTION")
    print("="*60)
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Define triangle vertices
    vertex_A = (-2, -1)  # Bottom left
    vertex_B = (2, -1)   # Bottom right  
    vertex_C = (0, 2)    # Top
    
    print(f"Triangle vertices:")
    print(f"  A: {vertex_A}")
    print(f"  B: {vertex_B}")
    print(f"  C: {vertex_C}")
    
    # Create the base lines
    print("\\nCreating base lines...")
    
    # Line 1: y + 1 = 0 (horizontal line through A and B)
    line1_expr = y + 1
    line1_base = PolynomialCurve(line1_expr, (x, y))
    
    # Line 2: 3x + 2y - 4 = 0 (line through B and C)
    line2_expr = 3*x + 2*y - 4
    line2_base = PolynomialCurve(line2_expr, (x, y))
    
    # Line 3: 3x - 2y + 4 = 0 (line through C and A)
    line3_expr = 3*x - 2*y + 4
    line3_base = PolynomialCurve(line3_expr, (x, y))
    
    # Verify the lines pass through the correct vertices
    print("\\nVerifying lines pass through vertices:")
    
    lines = [(line1_base, "Line AB", [vertex_A, vertex_B]),
             (line2_base, "Line BC", [vertex_B, vertex_C]),
             (line3_base, "Line CA", [vertex_C, vertex_A])]
    
    for line, name, vertices in lines:
        print(f"\\n{name}:")
        for i, (vx, vy) in enumerate(vertices):
            val = line.evaluate(vx, vy)
            print(f"  Vertex {['A','B','C'][['A','B','C'].index(name.split()[1][0]) if len(name.split()[1]) > 0 else 0]}: ({vx}, {vy}) → f = {val:.10f} {'✓' if abs(val) < 1e-10 else '✗'}")
    
    # Create simple trimming masks (very permissive for debugging)
    print("\\nCreating permissive trimming masks...")
    
    def mask_AB(px, py):
        # Very permissive: just check if roughly on the line and in x range
        on_line = abs(py + 1) < 0.5  # Within 0.5 of y = -1
        in_range = -2.5 <= px <= 2.5  # Slightly wider than vertex range
        result = on_line and in_range
        return result
    
    def mask_BC(px, py):
        # Very permissive: check if roughly on line and in bounding box
        on_line = abs(3*px + 2*py - 4) < 0.5
        in_x_range = -0.5 <= px <= 2.5
        in_y_range = -1.5 <= py <= 2.5
        result = on_line and in_x_range and in_y_range
        return result
    
    def mask_CA(px, py):
        # Very permissive: check if roughly on line and in bounding box
        on_line = abs(3*px - 2*py + 4) < 0.5
        in_x_range = -2.5 <= px <= 0.5
        in_y_range = -1.5 <= py <= 2.5
        result = on_line and in_x_range and in_y_range
        return result
    
    # Test the masks at vertices
    print("\\nTesting masks at vertices:")
    
    masks = [("mask_AB", mask_AB), ("mask_BC", mask_BC), ("mask_CA", mask_CA)]
    vertices_test = [("A", vertex_A), ("B", vertex_B), ("C", vertex_C)]
    
    for mask_name, mask_func in masks:
        print(f"\\n{mask_name}:")
        for vertex_name, (vx, vy) in vertices_test:
            result = mask_func(vx, vy)
            print(f"  Vertex {vertex_name}({vx}, {vy}): {result} {'✓' if result else '✗'}")
    
    # Create trimmed curves
    print("\\nCreating trimmed curves...")
    
    trimmed_AB = TrimmedImplicitCurve(line1_base, mask_AB)
    trimmed_BC = TrimmedImplicitCurve(line2_base, mask_BC)
    trimmed_CA = TrimmedImplicitCurve(line3_base, mask_CA)
    
    # Test trimmed curves at vertices
    print("\\nTesting trimmed curves at vertices:")
    
    trimmed_curves = [("Trimmed AB", trimmed_AB), ("Trimmed BC", trimmed_BC), ("Trimmed CA", trimmed_CA)]
    
    for curve_name, curve in trimmed_curves:
        print(f"\\n{curve_name}:")
        for vertex_name, (vx, vy) in vertices_test:
            try:
                # Test base curve
                base_val = curve.base_curve.evaluate(vx, vy)
                # Test mask
                mask_result = curve.mask(vx, vy)
                # Test contains (should combine both)
                contains_result = curve.contains(vx, vy)
                
                print(f"  Vertex {vertex_name}({vx}, {vy}): base={base_val:.6f}, mask={mask_result}, contains={contains_result}")
            except Exception as e:
                print(f"  Vertex {vertex_name}({vx}, {vy}): ERROR - {e}")
    
    # Create composite curve
    print("\\nCreating composite curve...")
    
    segments = [trimmed_AB, trimmed_BC, trimmed_CA]
    triangle_boundary = CompositeCurve(segments, (x, y))
    
    print(f"Composite curve created with {len(triangle_boundary.segments)} segments")
    
    # Debug the is_closed method
    print("\\n" + "="*50)
    print("DEBUGGING is_closed() METHOD")
    print("="*50)
    
    # Check if CompositeCurve has the is_closed method
    if hasattr(triangle_boundary, 'is_closed'):
        print("\\nCalling is_closed()...")
        try:
            is_closed = triangle_boundary.is_closed()
            print(f"is_closed() returned: {is_closed}")
        except Exception as e:
            print(f"is_closed() failed with error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\\nERROR: CompositeCurve does not have is_closed() method!")
    
    # Let's manually check connectivity
    print("\\nManual connectivity check:")
    print("Expected connections:")
    print("  AB end should connect to BC start")
    print("  BC end should connect to CA start") 
    print("  CA end should connect to AB start")
    
    # The vertices should be the connection points
    connections = [
        ("AB→BC", vertex_B, "AB end connects to BC start"),
        ("BC→CA", vertex_C, "BC end connects to CA start"),
        ("CA→AB", vertex_A, "CA end connects to AB start")
    ]
    
    for connection_name, vertex, description in connections:
        vx, vy = vertex
        print(f"\\n{connection_name} at vertex ({vx}, {vy}):")
        print(f"  {description}")
        
        # Test if this vertex is on the relevant segments
        if "AB" in connection_name:
            ab_contains = trimmed_AB.contains(vx, vy)
            print(f"  Trimmed AB contains vertex: {ab_contains}")
        if "BC" in connection_name:
            bc_contains = trimmed_BC.contains(vx, vy)
            print(f"  Trimmed BC contains vertex: {bc_contains}")
        if "CA" in connection_name:
            ca_contains = trimmed_CA.contains(vx, vy)
            print(f"  Trimmed CA contains vertex: {ca_contains}")
    
    print("\\n" + "="*60)
    print("DEBUGGING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    debug_closure_detection()
