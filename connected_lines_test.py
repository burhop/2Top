#!/usr/bin/env python3
"""
Test to create and plot 3 connected lines in the same window.
The lines will form a triangle shape with connected endpoints.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve

def test_connected_lines():
    """
    Create and plot 3 lines that connect at their endpoints to form a triangle.
    """
    print("Creating 3 connected lines forming a triangle...")
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot - single window
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.suptitle('Three Connected Lines (Triangle Shape)', fontsize=16)
    
    # Define test grid
    x_range = np.linspace(-4, 4, 300)
    y_range = np.linspace(-4, 4, 300)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Define triangle vertices that will connect
    vertex_A = (-2, -1)  # Bottom left
    vertex_B = (2, -1)   # Bottom right  
    vertex_C = (0, 2)    # Top
    
    print(f"Triangle vertices:")
    print(f"  A: {vertex_A}")
    print(f"  B: {vertex_B}")
    print(f"  C: {vertex_C}")
    
    # Line 1: From A to B (bottom edge)
    # Line equation: y = -1 (horizontal line)
    print("\\n1. Creating Line AB (bottom edge): y = -1")
    line1_expr = y + 1  # y + 1 = 0
    line1 = PolynomialCurve(line1_expr, (x, y))
    
    # Line 2: From B to C (right edge)
    # Line from (2, -1) to (0, 2)
    # Slope = (2 - (-1)) / (0 - 2) = 3 / (-2) = -3/2
    # y - (-1) = -3/2 * (x - 2)
    # y + 1 = -3/2 * x + 3
    # y = -3/2 * x + 2
    # 3/2 * x + y - 2 = 0
    # 3x + 2y - 4 = 0
    print("2. Creating Line BC (right edge): 3x + 2y - 4 = 0")
    line2_expr = 3*x + 2*y - 4
    line2 = PolynomialCurve(line2_expr, (x, y))
    
    # Line 3: From C to A (left edge)
    # Line from (0, 2) to (-2, -1)
    # Slope = (-1 - 2) / (-2 - 0) = -3 / -2 = 3/2
    # y - 2 = 3/2 * (x - 0)
    # y = 3/2 * x + 2
    # 2y = 3x + 4
    # 3x - 2y + 4 = 0
    print("3. Creating Line CA (left edge): 3x - 2y + 4 = 0")
    line3_expr = 3*x - 2*y + 4
    line3 = PolynomialCurve(line3_expr, (x, y))
    
    # Plot all three lines on the same axes
    lines = [
        (line1, "Line AB (y = -1)", "red"),
        (line2, "Line BC (3x + 2y = 4)", "blue"), 
        (line3, "Line CA (3x - 2y = -4)", "green")
    ]
    
    for i, (line, label, color) in enumerate(lines):
        print(f"\\nPlotting {label}...")
        
        # Evaluate the line
        Z = np.zeros_like(X)
        for row in range(X.shape[0]):
            for col in range(X.shape[1]):
                try:
                    Z[row, col] = line.evaluate(X[row, col], Y[row, col])
                except:
                    Z[row, col] = np.nan
        
        # Plot the zero level (the actual line)
        ax.contour(X, Y, Z, levels=[0], colors=color, linewidths=3, label=label)
        
        # Also show some level sets for context
        ax.contour(X, Y, Z, levels=[-2, -1, 1, 2], colors=color, alpha=0.2, linewidths=1)
    
    # Mark the vertices
    vertices = [vertex_A, vertex_B, vertex_C]
    vertex_labels = ['A', 'B', 'C']
    
    for (vx, vy), label in zip(vertices, vertex_labels):
        ax.plot(vx, vy, 'ko', markersize=10, markerfacecolor='yellow', markeredgecolor='black', markeredgewidth=2)
        ax.annotate(f'{label}({vx},{vy})', (vx, vy), xytext=(10, 10), textcoords='offset points', 
                   fontsize=12, fontweight='bold', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Set up the plot
    ax.set_title('Three Lines Forming Triangle\\n(Lines only, no filled area)', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.legend(loc='upper right')
    
    # Test that vertices lie on the correct lines
    print("\\n" + "="*50)
    print("VERIFICATION: Testing vertices on lines")
    print("="*50)
    
    # Test vertex A on lines 1 and 3
    print(f"\\nVertex A{vertex_A}:")
    val1_A = line1.evaluate(vertex_A[0], vertex_A[1])
    val3_A = line3.evaluate(vertex_A[0], vertex_A[1])
    print(f"  On Line AB: f = {val1_A:.10f} {'✓' if abs(val1_A) < 1e-10 else '✗'}")
    print(f"  On Line CA: f = {val3_A:.10f} {'✓' if abs(val3_A) < 1e-10 else '✗'}")
    
    # Test vertex B on lines 1 and 2
    print(f"\\nVertex B{vertex_B}:")
    val1_B = line1.evaluate(vertex_B[0], vertex_B[1])
    val2_B = line2.evaluate(vertex_B[0], vertex_B[1])
    print(f"  On Line AB: f = {val1_B:.10f} {'✓' if abs(val1_B) < 1e-10 else '✗'}")
    print(f"  On Line BC: f = {val2_B:.10f} {'✓' if abs(val2_B) < 1e-10 else '✗'}")
    
    # Test vertex C on lines 2 and 3
    print(f"\\nVertex C{vertex_C}:")
    val2_C = line2.evaluate(vertex_C[0], vertex_C[1])
    val3_C = line3.evaluate(vertex_C[0], vertex_C[1])
    print(f"  On Line BC: f = {val2_C:.10f} {'✓' if abs(val2_C) < 1e-10 else '✗'}")
    print(f"  On Line CA: f = {val3_C:.10f} {'✓' if abs(val3_C) < 1e-10 else '✗'}")
    
    plt.tight_layout()
    plt.show()
    
    print("\\n✓ Three connected lines plotted successfully!")
    print("  - Lines form a triangle shape")
    print("  - Endpoints connect at vertices")
    print("  - No area region created (lines only)")

if __name__ == "__main__":
    test_connected_lines()
