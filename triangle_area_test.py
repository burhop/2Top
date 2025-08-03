#!/usr/bin/env python3
"""
Test to create a triangle area region using three trimmed lines.
This demonstrates creating an AreaRegion from a CompositeCurve of trimmed segments.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve, TrimmedImplicitCurve, CompositeCurve, AreaRegion

def test_triangle_area():
    """
    Create a triangle area region using three trimmed line segments.
    """
    print("Creating triangle area from three trimmed lines...")
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot - single window
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.suptitle('Triangle Area Region from Three Trimmed Lines', fontsize=16)
    
    # Define test grid
    x_range = np.linspace(-4, 4, 200)
    y_range = np.linspace(-4, 4, 200)
    X, Y = np.meshgrid(x_range, y_range)
    
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
    
    # Create improved trimming masks
    print("\\nCreating trimming masks...")
    
    # Mask for Line AB: segment from A to B
    def mask_AB(px, py):
        # Check if close to the line y = -1
        if abs(py + 1) > 0.1:  # More tolerant
            return False
        # Check if x is between A and B
        return vertex_A[0] <= px <= vertex_B[0]
    
    # Mask for Line BC: segment from B to C
    def mask_BC(px, py):
        # Check if close to the line 3x + 2y - 4 = 0
        if abs(3*px + 2*py - 4) > 0.1:  # More tolerant
            return False
        
        # Use bounding box approach - simpler and more robust
        min_x = min(vertex_B[0], vertex_C[0])
        max_x = max(vertex_B[0], vertex_C[0])
        min_y = min(vertex_B[1], vertex_C[1])
        max_y = max(vertex_B[1], vertex_C[1])
        
        return min_x <= px <= max_x and min_y <= py <= max_y
    
    # Mask for Line CA: segment from C to A
    def mask_CA(px, py):
        # Check if close to the line 3x - 2y + 4 = 0
        if abs(3*px - 2*py + 4) > 0.1:  # More tolerant
            return False
        
        # Use bounding box approach
        min_x = min(vertex_C[0], vertex_A[0])
        max_x = max(vertex_C[0], vertex_A[0])
        min_y = min(vertex_C[1], vertex_A[1])
        max_y = max(vertex_C[1], vertex_A[1])
        
        return min_x <= px <= max_x and min_y <= py <= max_y
    
    # Create trimmed curves
    print("\\nCreating trimmed curves...")
    
    trimmed_AB = TrimmedImplicitCurve(line1_base, mask_AB)
    trimmed_BC = TrimmedImplicitCurve(line2_base, mask_BC)
    trimmed_CA = TrimmedImplicitCurve(line3_base, mask_CA)
    
    # Create composite curve from the three trimmed segments
    print("\\nCreating composite curve...")
    
    segments = [trimmed_AB, trimmed_BC, trimmed_CA]
    triangle_boundary = CompositeCurve(segments, (x, y))
    
    # Check if the composite curve is closed
    is_closed = triangle_boundary.is_closed()
    print(f"Triangle boundary is_closed: {is_closed}")
    
    # Create the area region
    print("\\nCreating area region...")
    
    triangle_area = AreaRegion(triangle_boundary)
    
    # Test containment over the grid
    print("\\nTesting containment over grid...")
    
    inside_mask = np.zeros_like(X, dtype=bool)
    boundary_mask = np.zeros_like(X, dtype=bool)
    
    total_points = X.size
    processed = 0
    
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            try:
                px, py = X[i, j], Y[i, j]
                
                # Test if point is inside the region
                is_inside = triangle_area.contains(px, py, region_containment=True)
                inside_mask[i, j] = is_inside
                
                # Test if point is on the boundary
                is_boundary = triangle_area.contains(px, py, region_containment=False)
                boundary_mask[i, j] = is_boundary
                
            except Exception as e:
                inside_mask[i, j] = False
                boundary_mask[i, j] = False
            
            processed += 1
            if processed % 5000 == 0:
                print(f"  Processed {processed}/{total_points} points ({100*processed/total_points:.1f}%)")
    
    print(f"  Completed: {processed}/{total_points} points")
    
    # Plot the results
    print("\\nPlotting results...")
    
    # Plot filled area (inside points)
    inside_points = np.where(inside_mask)
    if len(inside_points[0]) > 0:
        ax.scatter(X[inside_points], Y[inside_points], 
                  c='lightblue', s=3, alpha=0.6, label=f'Inside Triangle ({len(inside_points[0])} points)')
    
    # Plot boundary points
    boundary_points = np.where(boundary_mask)
    if len(boundary_points[0]) > 0:
        ax.scatter(X[boundary_points], Y[boundary_points], 
                  c='red', s=8, alpha=0.8, label=f'Boundary ({len(boundary_points[0])} points)')
    
    # Plot the individual trimmed segments for reference
    segments_info = [
        (trimmed_AB, "Segment AB", "red", [(-2.5, -1), (2.5, -1)]),
        (trimmed_BC, "Segment BC", "blue", [(2, -1), (0, 2)]),
        (trimmed_CA, "Segment CA", "green", [(0, 2), (-2, -1)])
    ]
    
    for segment, label, color, endpoints in segments_info:
        # Draw line between endpoints for reference
        x_line = [endpoints[0][0], endpoints[1][0]]
        y_line = [endpoints[0][1], endpoints[1][1]]
        ax.plot(x_line, y_line, color=color, linewidth=3, alpha=0.7, linestyle='--', label=f'{label} (reference)')
    
    # Mark the vertices
    vertices = [vertex_A, vertex_B, vertex_C]
    vertex_labels = ['A', 'B', 'C']
    
    for (vx, vy), label in zip(vertices, vertex_labels):
        ax.plot(vx, vy, 'ko', markersize=12, markerfacecolor='yellow', markeredgecolor='black', markeredgewidth=3)
        ax.annotate(f'{label}({vx},{vy})', (vx, vy), xytext=(15, 15), textcoords='offset points', 
                   fontsize=12, fontweight='bold', 
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
    
    # Set up the plot
    ax.set_title('Triangle Area Region\\n(Blue = Inside, Red = Boundary, Dashed = Segment Reference)', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 4)
    ax.legend(loc='upper right', fontsize=10)
    
    # Test specific points
    print("\\n" + "="*60)
    print("VERIFICATION: Testing specific points")
    print("="*60)
    
    test_points = [
        (0, 0, "Center"),
        (-1, 0, "Left of center"),
        (1, 0, "Right of center"),
        (0, 1, "Above center"),
        (0, -0.5, "Below center"),
        (-2, -1, "Vertex A"),
        (2, -1, "Vertex B"),
        (0, 2, "Vertex C"),
        (-3, 0, "Outside left"),
        (3, 0, "Outside right"),
        (0, 3, "Outside top"),
        (0, -2, "Outside bottom")
    ]
    
    for px, py, description in test_points:
        try:
            is_inside = triangle_area.contains(px, py, region_containment=True)
            is_boundary = triangle_area.contains(px, py, region_containment=False)
            
            status = "INSIDE" if is_inside else ("BOUNDARY" if is_boundary else "OUTSIDE")
            print(f"  Point ({px:4.1f}, {py:4.1f}) [{description:15s}]: {status}")
            
        except Exception as e:
            print(f"  Point ({px:4.1f}, {py:4.1f}) [{description:15s}]: ERROR - {e}")
    
    # Calculate statistics
    total_grid_points = X.size
    inside_count = np.sum(inside_mask)
    boundary_count = np.sum(boundary_mask)
    outside_count = total_grid_points - inside_count - boundary_count
    
    print(f"\\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Total grid points: {total_grid_points}")
    print(f"Inside triangle:   {inside_count} ({100*inside_count/total_grid_points:.1f}%)")
    print(f"On boundary:       {boundary_count} ({100*boundary_count/total_grid_points:.1f}%)")
    print(f"Outside triangle:  {outside_count} ({100*outside_count/total_grid_points:.1f}%)")
    
    plt.tight_layout()
    plt.show()
    
    print("\\n✓ Triangle area region created successfully!")
    print("  - Three trimmed line segments form the boundary")
    print("  - CompositeCurve combines the segments")
    print("  - AreaRegion creates the filled triangle")
    print(f"  - Boundary is {'closed' if is_closed else 'not closed'}")

if __name__ == "__main__":
    test_triangle_area()
