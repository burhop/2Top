#!/usr/bin/env python3
"""
Visual correctness testing - generate data that can be plotted to verify curves
"""

import sympy as sp
import numpy as np
from geometry import *
import matplotlib.pyplot as plt

def test_visual_correctness():
    """Generate visual test data to verify curve correctness"""
    
    x, y = sp.symbols('x y')
    
    print("🎨 VISUAL CORRECTNESS TESTING")
    print("=" * 50)
    
    # Set up matplotlib for headless operation
    plt.switch_backend('Agg')
    
    # Create a grid for evaluation
    x_range = np.linspace(-3, 3, 200)
    y_range = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(x_range, y_range)
    
    # 1. Test Circle
    print("\n1. 🔵 Testing Circle Visualization")
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    
    # Evaluate on grid
    Z_circle = circle.evaluate(X, Y)
    
    # Check zero-level set (should be a circle)
    zero_level = np.abs(Z_circle) < 0.05  # Points near the curve
    
    # Find points on the zero level
    circle_points_x = X[zero_level]
    circle_points_y = Y[zero_level]
    
    # Verify they satisfy x² + y² ≈ 1
    radii = np.sqrt(circle_points_x**2 + circle_points_y**2)
    circle_error = np.abs(radii - 1.0)
    max_circle_error = np.max(circle_error)
    
    print(f"  Circle max error: {max_circle_error:.6f} (should be < 0.1)")
    print(f"  Circle points found: {len(circle_points_x)}")
    
    # 2. Test Ellipse
    print("\n2. 🥚 Testing Ellipse Visualization")
    ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
    
    Z_ellipse = ellipse.evaluate(X, Y)
    ellipse_level = np.abs(Z_ellipse) < 0.05
    
    ellipse_points_x = X[ellipse_level]
    ellipse_points_y = Y[ellipse_level]
    
    # Verify ellipse equation: x²/4 + y² ≈ 1
    ellipse_values = (ellipse_points_x**2)/4 + ellipse_points_y**2
    ellipse_error = np.abs(ellipse_values - 1.0)
    max_ellipse_error = np.max(ellipse_error) if len(ellipse_error) > 0 else 0
    
    print(f"  Ellipse max error: {max_ellipse_error:.6f}")
    print(f"  Ellipse points found: {len(ellipse_points_x)}")
    
    # 3. Test Line
    print("\n3. 📐 Testing Line Visualization")
    line = PolynomialCurve(x + y - 1, (x, y))
    
    Z_line = line.evaluate(X, Y)
    line_level = np.abs(Z_line) < 0.05
    
    line_points_x = X[line_level]
    line_points_y = Y[line_level]
    
    # Verify line equation: x + y ≈ 1
    line_values = line_points_x + line_points_y
    line_error = np.abs(line_values - 1.0)
    max_line_error = np.max(line_error) if len(line_error) > 0 else 0
    
    print(f"  Line max error: {max_line_error:.6f}")
    print(f"  Line points found: {len(line_points_x)}")
    
    # 4. Test Superellipse
    print("\n4. ⭐ Testing Superellipse Visualization")
    
    # Circle-like (n=2)
    super_circle = Superellipse(a=1.5, b=1.0, n=2.0, variables=(x, y))
    Z_super = super_circle.evaluate(X, Y)
    super_level = np.abs(Z_super) < 0.05
    
    super_points_x = X[super_level]
    super_points_y = Y[super_level]
    
    print(f"  Superellipse (circle) points found: {len(super_points_x)}")
    
    # Square-like (n=8)
    super_square = Superellipse(a=1.0, b=1.0, n=8.0, variables=(x, y))
    Z_square = super_square.evaluate(X, Y)
    square_level = np.abs(Z_square) < 0.05
    
    square_points_x = X[square_level]
    square_points_y = Y[square_level]
    
    print(f"  Superellipse (square) points found: {len(square_points_x)}")
    
    # 5. Test Constructive Geometry
    print("\n5. 🔗 Testing Constructive Geometry")
    
    c1 = ConicSection(x**2 + y**2 - 1, (x, y))
    c2 = ConicSection((x-1)**2 + y**2 - 1, (x, y))
    
    # Union
    union_curve = union(c1, c2)
    Z_union = union_curve.evaluate(X, Y)
    union_level = np.abs(Z_union) < 0.05
    union_points = np.sum(union_level)
    
    print(f"  Union boundary points: {union_points}")
    
    # Intersection
    intersect_curve = intersect(c1, c2)
    Z_intersect = intersect_curve.evaluate(X, Y)
    intersect_level = np.abs(Z_intersect) < 0.05
    intersect_points = np.sum(intersect_level)
    
    print(f"  Intersection boundary points: {intersect_points}")
    
    # 6. Test Sign Convention
    print("\n6. ➕➖ Testing Sign Convention")
    
    # Inside should be negative, outside positive
    inside_circle = circle.evaluate(0, 0)  # Center
    outside_circle = circle.evaluate(2, 2)  # Far outside
    on_circle = circle.evaluate(1, 0)  # On boundary
    
    print(f"  Circle inside (0,0): {inside_circle} (should be < 0)")
    print(f"  Circle outside (2,2): {outside_circle} (should be > 0)")
    print(f"  Circle on boundary (1,0): {on_circle} (should be ≈ 0)")
    
    sign_correct = inside_circle < 0 and outside_circle > 0 and abs(on_circle) < 1e-10
    print(f"  Sign convention correct: {sign_correct}")
    
    # 7. Test Gradient Direction
    print("\n7. 📈 Testing Gradient Direction")
    
    # Gradient should point outward from curve
    gx, gy = circle.gradient(1, 0)  # At (1,0) on circle
    
    # At (1,0), outward normal should be (1,0)
    # Gradient of x²+y²-1 is (2x, 2y) = (2,0) at (1,0)
    gradient_correct = abs(gx - 2) < 1e-10 and abs(gy - 0) < 1e-10
    print(f"  Circle gradient at (1,0): ({gx}, {gy})")
    print(f"  Gradient direction correct: {gradient_correct}")
    
    # 8. Test Composite Curves
    print("\n8. 🔗 Testing Composite Curves")
    
    # Create and test square
    square = create_square_from_edges((-1, -1), (1, 1))
    
    # Test corners
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    corner_values = [square.evaluate(cx, cy) for cx, cy in corners]    
    print(f"  Square corner values: {corner_values}")
    
    # All corners should be on boundary (≈ 0)
    corners_on_boundary = all(abs(val) < 1e-6 for val in corner_values)
    print(f"  All corners on boundary: {corners_on_boundary}")
    
    # Test inside/outside
    inside_square = square.evaluate(0, 0)
    outside_square = square.evaluate(2, 0)
    
    print(f"  Square inside (0,0): {inside_square} (should be < 0)")
    print(f"  Square outside (2,0): {outside_square} (should be > 0)")
    
    # 9. Generate Sample Plot Data
    print("\n9. 📊 Generating Sample Plot Data")
    
    # Create a simple visualization data file
    plot_data = {
        'x_range': x_range,
        'y_range': y_range,
        'circle_values': Z_circle,
        'ellipse_values': Z_ellipse,
        'line_values': Z_line,
        'union_values': Z_union,
    }
    
    # Save key points for verification
    verification_points = {
        'circle_on_curve': [(1, 0), (0, 1), (-1, 0), (0, -1)],
        'ellipse_on_curve': [(2, 0), (0, 1), (-2, 0), (0, -1)],
        'line_on_curve': [(0, 1), (1, 0), (0.5, 0.5)],
    }
    
    print("  Sample verification points:")
    for curve_name, points in verification_points.items():
        print(f"    {curve_name}: {points}")
    
    # 10. Consistency Checks
    print("\n10. 🔍 Consistency Checks")
    
    # Check that different representations give same results
    circle_conic = ConicSection(x**2 + y**2 - 1, (x, y))
    circle_poly = PolynomialCurve(x**2 + y**2 - 1, (x, y))
    
    test_points = [(0, 0), (1, 0), (0.5, 0.5)]
    
    for px, py in test_points:
        val_conic = circle_conic.evaluate(px, py)
        val_poly = circle_poly.evaluate(px, py)
        consistent = abs(val_conic - val_poly) < 1e-10
        
        print(f"  Point ({px},{py}): Conic={val_conic}, Poly={val_poly}, Consistent={consistent}")
    
    print("\n🎯 Visual correctness testing complete!")
    print("\nTo verify visually, you can plot the zero-level sets of the generated data.")
    print("The curves should match their mathematical definitions exactly.")

if __name__ == "__main__":
    test_visual_correctness()