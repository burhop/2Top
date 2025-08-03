#!/usr/bin/env python3
"""
Test to create 3 trimmed lines that form exact triangle edges.
Each line is trimmed to only show the segment between vertices.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve, TrimmedImplicitCurve

def test_trimmed_lines():
    """
    Create 3 lines and trim them to form exact triangle edge segments.
    """
    print("Creating 3 trimmed lines forming triangle edges...")
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot - single window
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.suptitle('Three Trimmed Lines (Triangle Edge Segments)', fontsize=16)
    
    # Define test grid
    x_range = np.linspace(-4, 4, 300)
    y_range = np.linspace(-4, 4, 300)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Define triangle vertices
    vertex_A = (-2, -1)  # Bottom left
    vertex_B = (2, -1)   # Bottom right  
    vertex_C = (0, 2)    # Top
    
    print(f"Triangle vertices:")
    print(f"  A: {vertex_A}")
    print(f"  B: {vertex_B}")
    print(f"  C: {vertex_C}")
    
    # Create the base lines (infinite lines)
    print("\\nCreating base lines...")
    
    # Line 1: y = -1 (horizontal line through A and B)
    line1_expr = y + 1
    line1_base = PolynomialCurve(line1_expr, (x, y))
    
    # Line 2: 3x + 2y - 4 = 0 (line through B and C)
    line2_expr = 3*x + 2*y - 4
    line2_base = PolynomialCurve(line2_expr, (x, y))
    
    # Line 3: 3x - 2y + 4 = 0 (line through C and A)
    line3_expr = 3*x - 2*y + 4
    line3_base = PolynomialCurve(line3_expr, (x, y))
    
    # Create trimming masks for each line segment
    print("\\nCreating trimming masks...")
    
    # Mask for Line AB: only between x = -2 and x = 2, y = -1
    def mask_AB(px, py):
        # On the line y = -1 and between x coordinates of A and B
        on_line = abs(py + 1) < 1e-6  # Close to y = -1
        in_x_range = -2 <= px <= 2    # Between A and B x-coordinates
        return on_line and in_x_range
    
    # Mask for Line BC: between vertices B(2,-1) and C(0,2)
    def mask_BC(px, py):
        # Check if point is on the line 3x + 2y - 4 = 0
        on_line = abs(3*px + 2*py - 4) < 1e-6
        
        # Check if point is between B and C using parameter t
        # Parametric form: P = B + t*(C - B) = (2,-1) + t*(-2,3)
        # So px = 2 - 2t, py = -1 + 3t
        # Solve for t: t = (2 - px)/2, and check if py = -1 + 3*t
        if abs(px - 2) < 1e-10:  # Avoid division by zero at x = 2
            t = 0
        else:
            t = (2 - px) / 2
        
        # Check if t is in [0,1] (between vertices) and point satisfies parametric equation
        in_range = 0 <= t <= 1
        expected_y = -1 + 3*t
        correct_y = abs(py - expected_y) < 1e-6
        
        return on_line and in_range and correct_y
    
    # Mask for Line CA: between vertices C(0,2) and A(-2,-1)  
    def mask_CA(px, py):
        # Check if point is on the line 3x - 2y + 4 = 0
        on_line = abs(3*px - 2*py + 4) < 1e-6
        
        # Check if point is between C and A using parameter t
        # Parametric form: P = C + t*(A - C) = (0,2) + t*(-2,-3)
        # So px = -2t, py = 2 - 3t
        # Solve for t: t = -px/2, and check if py = 2 - 3*t
        if abs(px) < 1e-10:  # At x = 0
            t = 0
        else:
            t = -px / 2
        
        # Check if t is in [0,1] (between vertices) and point satisfies parametric equation
        in_range = 0 <= t <= 1
        expected_y = 2 - 3*t
        correct_y = abs(py - expected_y) < 1e-6
        
        return on_line and in_range and correct_y
    
    # Create trimmed curves
    print("\\nCreating trimmed curves...")
    
    trimmed_AB = TrimmedImplicitCurve(line1_base, mask_AB)
    trimmed_BC = TrimmedImplicitCurve(line2_base, mask_BC)
    trimmed_CA = TrimmedImplicitCurve(line3_base, mask_CA)
    
    # Plot the full lines first (lightly)
    print("\\nPlotting full lines (light gray)...")
    
    lines_full = [
        (line1_base, "Full Line AB"),
        (line2_base, "Full Line BC"), 
        (line3_base, "Full Line CA")
    ]
    
    for line, label in lines_full:
        Z = np.zeros_like(X)
        for row in range(X.shape[0]):
            for col in range(X.shape[1]):
                try:
                    Z[row, col] = line.evaluate(X[row, col], Y[row, col])
                except:
                    Z[row, col] = np.nan
        
        ax.contour(X, Y, Z, levels=[0], colors='lightgray', linewidths=1, alpha=0.3)
    
    # Plot the trimmed segments (bold colors)
    print("\\nPlotting trimmed segments...")
    
    trimmed_lines = [
        (trimmed_AB, "Trimmed AB", "red"),
        (trimmed_BC, "Trimmed BC", "blue"), 
        (trimmed_CA, "Trimmed CA", "green")
    ]
    
    # For trimmed curves, we'll plot them by testing points and showing only those that pass the mask
    for trimmed_curve, label, color in trimmed_lines:
        print(f"  Plotting {label}...")
        
        # Test points on a finer grid around the expected segment
        if "AB" in label:
            # For AB segment, test points along y = -1
            x_test = np.linspace(-2.5, 2.5, 500)
            y_test = np.full_like(x_test, -1)
        elif "BC" in label:
            # For BC segment, test points along the line
            x_test = np.linspace(-0.5, 2.5, 500)
            y_test = (4 - 3*x_test) / 2  # Solve 3x + 2y = 4 for y
        else:  # CA
            # For CA segment, test points along the line
            x_test = np.linspace(-2.5, 0.5, 500)
            y_test = (3*x_test + 4) / 2  # Solve 3x - 2y = -4 for y
        
        # Filter points that pass the trimming mask
        valid_x = []
        valid_y = []
        
        for px, py in zip(x_test, y_test):
            try:
                # Check if point is on the trimmed curve
                if trimmed_curve.base_curve.evaluate(px, py) < 1e-6:  # On base line
                    if trimmed_curve.mask(px, py):  # Passes mask
                        valid_x.append(px)
                        valid_y.append(py)
            except:
                pass
        
        # Plot the valid points as a line
        if valid_x:
            ax.plot(valid_x, valid_y, color=color, linewidth=4, label=label, marker='o', markersize=2)
    
    # Mark the vertices
    vertices = [vertex_A, vertex_B, vertex_C]
    vertex_labels = ['A', 'B', 'C']
    
    for (vx, vy), label in zip(vertices, vertex_labels):
        ax.plot(vx, vy, 'ko', markersize=12, markerfacecolor='yellow', markeredgecolor='black', markeredgewidth=3)
        ax.annotate(f'{label}({vx},{vy})', (vx, vy), xytext=(15, 15), textcoords='offset points', 
                   fontsize=12, fontweight='bold', 
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))
    
    # Set up the plot
    ax.set_title('Trimmed Line Segments\\n(Gray = Full Lines, Colors = Trimmed Segments)', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 4)
    ax.legend(loc='upper right')
    
    # Test the trimmed curves
    print("\\n" + "="*60)
    print("VERIFICATION: Testing trimmed curves")
    print("="*60)
    
    # Test points on each trimmed segment
    test_points = {
        "AB": [(-1, -1), (0, -1), (1, -1), (-2, -1), (2, -1)],  # Points on AB segment
        "BC": [(1, 0.5), (0, 2), (2, -1)],  # Points on BC segment  
        "CA": [(-1, 3.5), (0, 2), (-2, -1)]  # Points on CA segment
    }
    
    curves = {"AB": trimmed_AB, "BC": trimmed_BC, "CA": trimmed_CA}
    
    for segment_name, points in test_points.items():
        print(f"\\nTrimmed segment {segment_name}:")
        curve = curves[segment_name]
        
        for px, py in points:
            try:
                on_base = abs(curve.base_curve.evaluate(px, py)) < 1e-6
                passes_mask = curve.mask(px, py)
                on_trimmed = on_base and passes_mask
                
                print(f"  Point ({px:4.1f}, {py:4.1f}): on_base={on_base}, passes_mask={passes_mask} → {'✓ ON SEGMENT' if on_trimmed else '✗ not on segment'}")
            except Exception as e:
                print(f"  Point ({px:4.1f}, {py:4.1f}): ERROR - {e}")
    
    plt.tight_layout()
    plt.show()
    
    print("\\n✓ Three trimmed line segments created successfully!")
    print("  - Each line is trimmed to show only the triangle edge")
    print("  - Full lines shown in light gray for reference")
    print("  - Trimmed segments shown in bold colors")

if __name__ == "__main__":
    test_trimmed_lines()
