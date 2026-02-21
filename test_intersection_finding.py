#!/usr/bin/env python3
"""
Test the intersection finding functionality
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_intersection_finding():
    """Test intersection finding with known cases"""
    
    print("🔍 TESTING INTERSECTION FINDING")
    print("=" * 40)
    
    x, y = sp.symbols('x y')
    
    # Test Case 1: Circle and Line (known intersections)
    print("\n1. Circle and Line Test:")
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    line = PolynomialCurve(x + y, (x, y))
    
    print(f"  Circle: {circle}")
    print(f"  Line: {line}")
    
    # Find intersections
    intersections = find_curve_intersections(circle, line)
    
    print(f"  Found {len(intersections)} intersections:")
    for i, (px, py) in enumerate(intersections):
        print(f"    {i+1}. ({px:.4f}, {py:.4f})")
        
        # Verify
        circle_val = circle.evaluate(px, py)
        line_val = line.evaluate(px, py)
        print(f"       Circle check: {circle_val:.6f}")
        print(f"       Line check: {line_val:.6f}")
    
    # Expected: (±1/√2, ∓1/√2)
    expected = [(1/np.sqrt(2), -1/np.sqrt(2)), (-1/np.sqrt(2), 1/np.sqrt(2))]
    print(f"  Expected: {[(f'{x:.4f}', f'{y:.4f}') for x, y in expected]}")
    
    # Test Case 2: Two Circles
    print("\n2. Two Circles Test:")
    circle1 = ConicSection(x**2 + y**2 - 1, (x, y))
    circle2 = ConicSection((x-1)**2 + y**2 - 1, (x, y))
    
    print(f"  Circle 1: centered at (0,0), radius 1")
    print(f"  Circle 2: centered at (1,0), radius 1")
    
    intersections2 = find_curve_intersections(circle1, circle2)
    
    print(f"  Found {len(intersections2)} intersections:")
    for i, (px, py) in enumerate(intersections2):
        print(f"    {i+1}. ({px:.4f}, {py:.4f})")
    
    # Expected: (0.5, ±√3/2)
    expected2 = [(0.5, np.sqrt(3)/2), (0.5, -np.sqrt(3)/2)]
    print(f"  Expected: {[(f'{x:.4f}', f'{y:.4f}') for x, y in expected2]}")
    
    # Test Case 3: Parabola and Line
    print("\n3. Parabola and Line Test:")
    parabola = PolynomialCurve(y - x**2, (x, y))
    line2 = PolynomialCurve(y - 1, (x, y))
    
    print(f"  Parabola: y = x²")
    print(f"  Line: y = 1")
    
    intersections3 = find_curve_intersections(parabola, line2)
    
    print(f"  Found {len(intersections3)} intersections:")
    for i, (px, py) in enumerate(intersections3):
        print(f"    {i+1}. ({px:.4f}, {py:.4f})")
    
    # Expected: (±1, 1)
    expected3 = [(1, 1), (-1, 1)]
    print(f"  Expected: {[(f'{x:.4f}', f'{y:.4f}') for x, y in expected3]}")
    
    # Visualization
    print("\n4. Creating Visualization...")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Intersection Finding Tests', fontsize=14, fontweight='bold')
    
    test_cases = [
        ("Circle ∩ Line", circle, line, intersections, expected),
        ("Circle ∩ Circle", circle1, circle2, intersections2, expected2),
        ("Parabola ∩ Line", parabola, line2, intersections3, expected3),
    ]
    
    plot_range = 2
    resolution = 300
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    for i, (title, curve1, curve2, found_intersections, expected_intersections) in enumerate(test_cases):
        ax = axes[i]
        
        # Plot curves
        try:
            Z1 = curve1.evaluate(X, Y)
            Z2 = curve2.evaluate(X, Y)
            
            ax.contour(X, Y, Z1, levels=[0], colors=['blue'], linewidths=2, label='Curve 1')
            ax.contour(X, Y, Z2, levels=[0], colors=['red'], linewidths=2, label='Curve 2')
            
            # Plot found intersections
            if found_intersections:
                for px, py in found_intersections:
                    ax.plot(px, py, 'go', markersize=10, label='Found' if px == found_intersections[0][0] else "")
            
            # Plot expected intersections
            if expected_intersections:
                for px, py in expected_intersections:
                    ax.plot(px, py, 'rx', markersize=12, markeredgewidth=3, 
                           label='Expected' if px == expected_intersections[0][0] else "")
            
            ax.set_xlim(-plot_range, plot_range)
            ax.set_ylim(-plot_range, plot_range)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(title)
            ax.legend()
            
        except Exception as e:
            print(f"Error plotting {title}: {e}")
    
    plt.tight_layout()
    plt.savefig('intersection_tests.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: intersection_tests.png")
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"  Test 1 (Circle ∩ Line): {len(intersections)} found, 2 expected")
    print(f"  Test 2 (Circle ∩ Circle): {len(intersections2)} found, 2 expected")
    print(f"  Test 3 (Parabola ∩ Line): {len(intersections3)} found, 2 expected")
    
    total_found = len(intersections) + len(intersections2) + len(intersections3)
    total_expected = 6
    
    print(f"\n  Overall: {total_found}/{total_expected} intersections found")
    
    if total_found >= total_expected * 0.8:  # Allow some tolerance
        print("  ✅ Intersection finding working well!")
    else:
        print("  ⚠️  Some intersections may be missed - consider tuning parameters")

if __name__ == "__main__":
    test_intersection_finding()