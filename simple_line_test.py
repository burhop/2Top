#!/usr/bin/env python3
"""
Simple test to create and plot 3 lines using the implicit geometry library.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import PolynomialCurve

def test_three_lines():
    """
    Create and plot 3 different lines.
    """
    print("Creating and plotting 3 lines...")
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Three Lines using PolynomialCurve', fontsize=16)
    
    # Define test grid
    x_range = np.linspace(-5, 5, 200)
    y_range = np.linspace(-5, 5, 200)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Line 1: Horizontal line y = 2
    print("1. Creating horizontal line: y = 2")
    line1_expr = y - 2  # y - 2 = 0
    line1 = PolynomialCurve(line1_expr, (x, y))
    
    # Evaluate and plot
    Z1 = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z1[i, j] = line1.evaluate(X[i, j], Y[i, j])
    
    axes[0].contour(X, Y, Z1, levels=[0], colors='red', linewidths=3)
    axes[0].set_title('Horizontal Line\ny = 2', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_aspect('equal')
    axes[0].set_xlim(-5, 5)
    axes[0].set_ylim(-5, 5)
    
    # Line 2: Vertical line x = -1
    print("2. Creating vertical line: x = -1")
    line2_expr = x + 1  # x + 1 = 0
    line2 = PolynomialCurve(line2_expr, (x, y))
    
    # Evaluate and plot
    Z2 = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z2[i, j] = line2.evaluate(X[i, j], Y[i, j])
    
    axes[1].contour(X, Y, Z2, levels=[0], colors='blue', linewidths=3)
    axes[1].set_title('Vertical Line\nx = -1', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_aspect('equal')
    axes[1].set_xlim(-5, 5)
    axes[1].set_ylim(-5, 5)
    
    # Line 3: Diagonal line y = x + 1
    print("3. Creating diagonal line: y = x + 1")
    line3_expr = y - x - 1  # y - x - 1 = 0
    line3 = PolynomialCurve(line3_expr, (x, y))
    
    # Evaluate and plot
    Z3 = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z3[i, j] = line3.evaluate(X[i, j], Y[i, j])
    
    axes[2].contour(X, Y, Z3, levels=[0], colors='green', linewidths=3)
    axes[2].set_title('Diagonal Line\ny = x + 1', fontsize=12)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_aspect('equal')
    axes[2].set_xlim(-5, 5)
    axes[2].set_ylim(-5, 5)
    
    # Test some points on each line
    print("\nTesting points on the lines:")
    
    # Test horizontal line y = 2
    test_points_h = [(0, 2), (3, 2), (-2, 2), (1, 3)]
    print("Horizontal line y = 2:")
    for px, py in test_points_h:
        val = line1.evaluate(px, py)
        on_line = abs(val) < 1e-10
        print(f"  Point ({px}, {py}): f = {val:.6f} {'✓ ON LINE' if on_line else '✗ off line'}")
    
    # Test vertical line x = -1
    test_points_v = [(-1, 0), (-1, 3), (-1, -2), (0, 1)]
    print("Vertical line x = -1:")
    for px, py in test_points_v:
        val = line2.evaluate(px, py)
        on_line = abs(val) < 1e-10
        print(f"  Point ({px}, {py}): f = {val:.6f} {'✓ ON LINE' if on_line else '✗ off line'}")
    
    # Test diagonal line y = x + 1
    test_points_d = [(0, 1), (1, 2), (-1, 0), (2, 4)]
    print("Diagonal line y = x + 1:")
    for px, py in test_points_d:
        val = line3.evaluate(px, py)
        on_line = abs(val) < 1e-10
        print(f"  Point ({px}, {py}): f = {val:.6f} {'✓ ON LINE' if on_line else '✗ off line'}")
    
    plt.tight_layout()
    plt.show()
    
    print("\n✓ Three lines plotted successfully!")

if __name__ == "__main__":
    test_three_lines()
