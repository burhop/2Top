#!/usr/bin/env python3
"""
Test to create a triangle area using explicit endpoints in TrimmedImplicitCurve.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve, TrimmedImplicitCurve, CompositeCurve, AreaRegion

def test_triangle_with_endpoints():
    """
    Create a triangle area using TrimmedImplicitCurve with explicit endpoints.
    """
    print("="*60)
    print("CREATING TRIANGLE WITH EXPLICIT ENDPOINTS")
    print("="*60)
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Define triangle vertices (these will be our explicit endpoints)
    vertex_A = (-2.0, -1.0)  # Bottom left
    vertex_B = (2.0, -1.0)   # Bottom right  
    vertex_C = (0.0, 2.0)    # Top
    
    print(f"Triangle vertices:")
    print(f"  A: {vertex_A}")
    print(f"  B: {vertex_B}")
    print(f"  C: {vertex_C}")
    
    # Create the base lines
    print("\\nCreating base lines...")
    
    # Line 1: y + 1 = 0 (horizontal line through A and B)
    line1_expr = y + 1
    line1_base = PolynomialCurve(line1_expr, (x, y))
    print(f"Line AB: {line1_expr} = 0")
    
    # Line 2: 3x + 2y - 4 = 0 (line through B and C)
    line2_expr = 3*x + 2*y - 4
    line2_base = PolynomialCurve(line2_expr, (x, y))
    print(f"Line BC: {line2_expr} = 0")
    
    # Line 3: 3x - 2y + 4 = 0 (line through C and A)
    line3_expr = 3*x - 2*y + 4
    line3_base = PolynomialCurve(line3_expr, (x, y))
    print(f"Line CA: {line3_expr} = 0")
    
    # Verify lines pass through correct vertices
    print("\\nVerifying lines pass through vertices:")
    lines_vertices = [
        (line1_base, "AB", [vertex_A, vertex_B]),
        (line2_base, "BC", [vertex_B, vertex_C]),
        (line3_base, "CA", [vertex_C, vertex_A])
    ]
    
    for line, name, vertices in lines_vertices:
        print(f"\\nLine {name}:")
        for i, vertex in enumerate(vertices):
            val = line.evaluate(vertex[0], vertex[1])
            vertex_name = ['A', 'B', 'C'][['A', 'B', 'C'].index(name[0]) + i] if i == 0 else ['A', 'B', 'C'][['A', 'B', 'C'].index(name[1])]
            print(f"  Vertex {vertex_name}{vertex}: f = {val:.10f} {'✓' if abs(val) < 1e-10 else '✗'}")
    
    # Create simple masks (very permissive)
    print("\\nCreating masks...")
    
    def mask_AB(px, py):
        # On line y = -1, between A and B
        return abs(py + 1) < 0.1 and vertex_A[0] <= px <= vertex_B[0]
    
    def mask_BC(px, py):
        # On line 3x + 2y - 4 = 0, in bounding box of B and C
        on_line = abs(3*px + 2*py - 4) < 0.1
        in_x_range = min(vertex_B[0], vertex_C[0]) <= px <= max(vertex_B[0], vertex_C[0])
        in_y_range = min(vertex_B[1], vertex_C[1]) <= py <= max(vertex_B[1], vertex_C[1])
        return on_line and in_x_range and in_y_range
    
    def mask_CA(px, py):
        # On line 3x - 2y + 4 = 0, in bounding box of C and A
        on_line = abs(3*px - 2*py + 4) < 0.1
        in_x_range = min(vertex_C[0], vertex_A[0]) <= px <= max(vertex_C[0], vertex_A[0])
        in_y_range = min(vertex_C[1], vertex_A[1]) <= py <= max(vertex_C[1], vertex_A[1])
        return on_line and in_x_range and in_y_range
    
    # Create trimmed curves WITH EXPLICIT ENDPOINTS
    print("\\nCreating trimmed curves with explicit endpoints...")
    
    # Segment AB: from A to B
    trimmed_AB = TrimmedImplicitCurve(
        line1_base, 
        mask_AB, 
        endpoints=[vertex_A, vertex_B]
    )
    print(f"Trimmed AB: endpoints {trimmed_AB.get_endpoints()}")
    
    # Segment BC: from B to C
    trimmed_BC = TrimmedImplicitCurve(
        line2_base, 
        mask_BC, 
        endpoints=[vertex_B, vertex_C]
    )
    print(f"Trimmed BC: endpoints {trimmed_BC.get_endpoints()}")
    
    # Segment CA: from C to A
    trimmed_CA = TrimmedImplicitCurve(
        line3_base, 
        mask_CA, 
        endpoints=[vertex_C, vertex_A]
    )
    print(f"Trimmed CA: endpoints {trimmed_CA.get_endpoints()}")
    
    # Create composite curve
    print("\\nCreating composite curve...")
    
    segments = [trimmed_AB, trimmed_BC, trimmed_CA]
    triangle_boundary = CompositeCurve(segments, (x, y))
    
    print(f"Composite curve created with {len(triangle_boundary.segments)} segments")
    
    # Test the new is_closed method
    print("\\n" + "="*50)
    print("TESTING NEW is_closed() METHOD")
    print("="*50)
    
    # Check if all segments have explicit endpoints
    print("\\nChecking for explicit endpoints:")
    for i, segment in enumerate(segments):
        endpoints = segment.get_endpoints()
        print(f"  Segment {i}: {endpoints}")
    
    # Test the is_closed method
    print("\\nTesting is_closed()...")
    try:
        is_closed = triangle_boundary.is_closed()
        print(f"is_closed() returned: {is_closed}")
        
        if is_closed:
            print("✓ SUCCESS: Triangle boundary detected as closed!")
        else:
            print("✗ FAILURE: Triangle boundary not detected as closed")
            
    except Exception as e:
        print(f"✗ ERROR in is_closed(): {e}")
        import traceback
        traceback.print_exc()
    
    # If closed, try to create the area region
    if is_closed:
        print("\\n" + "="*50)
        print("CREATING AREA REGION")
        print("="*50)
        
        try:
            triangle_area = AreaRegion(triangle_boundary)
            print("✓ SUCCESS: AreaRegion created successfully!")
            
            # Test some points
            test_points = [
                (0, 0, "Center"),
                (-1, 0, "Left of center"),
                (1, 0, "Right of center"),
                (0, 1, "Above center"),
                (-2, -1, "Vertex A"),
                (2, -1, "Vertex B"),
                (0, 2, "Vertex C"),
                (-3, 0, "Outside left"),
                (3, 0, "Outside right"),
                (0, 3, "Outside top")
            ]
            
            print("\\nTesting containment:")
            for px, py, description in test_points:
                try:
                    is_inside = triangle_area.contains(px, py, region_containment=True)
                    is_boundary = triangle_area.contains(px, py, region_containment=False)
                    
                    status = "INSIDE" if is_inside else ("BOUNDARY" if is_boundary else "OUTSIDE")
                    print(f"  Point ({px:4.1f}, {py:4.1f}) [{description:15s}]: {status}")
                    
                except Exception as e:
                    print(f"  Point ({px:4.1f}, {py:4.1f}) [{description:15s}]: ERROR - {e}")
            
        except Exception as e:
            print(f"✗ ERROR creating AreaRegion: {e}")
            import traceback
            traceback.print_exc()
    
    # Manual connectivity check
    print("\\n" + "="*50)
    print("MANUAL CONNECTIVITY VERIFICATION")
    print("="*50)
    
    print("\\nExpected connections:")
    print("  AB end (B) should connect to BC start (B)")
    print("  BC end (C) should connect to CA start (C)")
    print("  CA end (A) should connect to AB start (A)")
    
    connections = [
        ("AB→BC", vertex_B, trimmed_AB.get_endpoints(), trimmed_BC.get_endpoints()),
        ("BC→CA", vertex_C, trimmed_BC.get_endpoints(), trimmed_CA.get_endpoints()),
        ("CA→AB", vertex_A, trimmed_CA.get_endpoints(), trimmed_AB.get_endpoints())
    ]
    
    tolerance = 1e-6
    all_connected = True
    
    for connection_name, expected_vertex, current_endpoints, next_endpoints in connections:
        print(f"\\n{connection_name}:")
        print(f"  Expected connection at: {expected_vertex}")
        print(f"  Current segment endpoints: {current_endpoints}")
        print(f"  Next segment endpoints: {next_endpoints}")
        
        # Check if any endpoint of current matches any endpoint of next
        connected = False
        for curr_end in current_endpoints:
            for next_end in next_endpoints:
                distance = np.sqrt((curr_end[0] - next_end[0])**2 + (curr_end[1] - next_end[1])**2)
                if distance <= tolerance:
                    connected = True
                    print(f"  ✓ Connected: {curr_end} ↔ {next_end} (distance: {distance:.10f})")
                    break
            if connected:
                break
        
        if not connected:
            print(f"  ✗ NOT CONNECTED")
            all_connected = False
    
    print(f"\\nOverall connectivity: {'✓ ALL CONNECTED' if all_connected else '✗ NOT ALL CONNECTED'}")
    
    print("\\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_triangle_with_endpoints()
