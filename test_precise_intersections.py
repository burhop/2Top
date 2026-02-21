#!/usr/bin/env python3
"""
Test precise intersection finding with better validation
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_precise_intersections():
    """Test intersection finding with precise validation"""
    
    print("🎯 PRECISE INTERSECTION TESTING")
    print("=" * 50)
    
    x, y = sp.symbols('x y')
    
    # Test Case: Parabola y = x² and Line y = 1
    print("\n📐 Parabola y = x² intersecting Line y = 1")
    
    parabola = PolynomialCurve(y - x**2, (x, y))
    line = PolynomialCurve(y - 1, (x, y))
    
    print(f"  Parabola expression: {parabola.expression}")
    print(f"  Line expression: {line.expression}")
    
    # Analytical solution: x² = 1 → x = ±1, y = 1
    analytical_solutions = [(-1, 1), (1, 1)]
    print(f"  Analytical solutions: {analytical_solutions}")
    
    # Verify analytical solutions
    print("\n  Verifying analytical solutions:")
    for i, (px, py) in enumerate(analytical_solutions):
        parabola_val = parabola.evaluate(px, py)
        line_val = line.evaluate(px, py)
        print(f"    Point {i+1} ({px}, {py}):")
        print(f"      Parabola: {parabola_val:.8f} (should be 0)")
        print(f"      Line: {line_val:.8f} (should be 0)")
        print(f"      Check y = x²: {py} = {px}² = {px**2} ✓")
    
    # Find intersections numerically
    print("\n  Finding intersections numerically:")
    found_intersections = find_curve_intersections(parabola, line, 
                                                  search_range=3.0, 
                                                  grid_resolution=400,
                                                  tolerance=1e-8)
    
    print(f"  Found {len(found_intersections)} intersections:")
    for i, (px, py) in enumerate(found_intersections):
        parabola_val = parabola.evaluate(px, py)
        line_val = line.evaluate(px, py)
        print(f"    Found {i+1} ({px:.6f}, {py:.6f}):")
        print(f"      Parabola: {parabola_val:.8f}")
        print(f"      Line: {line_val:.8f}")
        print(f"      Check y = x²: {py:.6f} vs {px**2:.6f} (diff: {abs(py - px**2):.8f})")
    
    # Compare with analytical
    print("\n  Comparison with analytical solutions:")
    for analytical in analytical_solutions:
        closest_found = None
        min_distance = float('inf')
        
        for found in found_intersections:
            distance = np.sqrt((found[0] - analytical[0])**2 + (found[1] - analytical[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest_found = found
        
        if closest_found:
            print(f"    Analytical {analytical} → Found {closest_found} (distance: {min_distance:.6f})")
        else:
            print(f"    Analytical {analytical} → No match found!")
    
    # Visual verification
    print("\n  Creating detailed visualization...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Parabola-Line Intersection Analysis', fontsize=14, fontweight='bold')
    
    # Plot 1: Overview
    plot_range = 3
    resolution = 500
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    Z_parabola = parabola.evaluate(X, Y)
    Z_line = line.evaluate(X, Y)
    
    ax1.contour(X, Y, Z_parabola, levels=[0], colors=['blue'], linewidths=2)
    ax1.contour(X, Y, Z_line, levels=[0], colors=['red'], linewidths=2)
    
    # Mark analytical solutions
    for px, py in analytical_solutions:
        ax1.plot(px, py, 'go', markersize=10, markeredgecolor='black', 
                markeredgewidth=2, label='Analytical' if px == analytical_solutions[0][0] else "")
    
    # Mark found solutions
    for px, py in found_intersections:
        ax1.plot(px, py, 'rx', markersize=12, markeredgewidth=3,
                label='Found' if px == found_intersections[0][0] else "")
    
    ax1.set_xlim(-plot_range, plot_range)
    ax1.set_ylim(-1, 5)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Full View')
    ax1.legend()
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    
    # Plot 2: Zoomed in on intersection region
    zoom_range = 2
    ax2.contour(X, Y, Z_parabola, levels=[0], colors=['blue'], linewidths=2, label='y = x²')
    ax2.contour(X, Y, Z_line, levels=[0], colors=['red'], linewidths=2, label='y = 1')
    
    # Mark solutions with annotations
    for i, (px, py) in enumerate(analytical_solutions):
        ax2.plot(px, py, 'go', markersize=12, markeredgecolor='black', markeredgewidth=2)
        ax2.annotate(f'Analytical\n({px}, {py})', xy=(px, py), xytext=(px, py+0.3),
                    ha='center', fontsize=9, 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))
    
    for i, (px, py) in enumerate(found_intersections):
        ax2.plot(px, py, 'rx', markersize=15, markeredgewidth=3)
        ax2.annotate(f'Found\n({px:.3f}, {py:.3f})', xy=(px, py), xytext=(px, py-0.4),
                    ha='center', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.8))
    
    ax2.set_xlim(-zoom_range, zoom_range)
    ax2.set_ylim(-0.5, 2.5)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Zoomed View')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    
    plt.tight_layout()
    plt.savefig('precise_intersection_test.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: precise_intersection_test.png")
    
    # Assessment
    print(f"\n📊 ASSESSMENT:")
    expected_count = len(analytical_solutions)
    found_count = len(found_intersections)
    
    print(f"  Expected intersections: {expected_count}")
    print(f"  Found intersections: {found_count}")
    
    if found_count == expected_count:
        # Check accuracy
        max_error = 0
        for analytical in analytical_solutions:
            closest_found = min(found_intersections, 
                               key=lambda p: np.sqrt((p[0] - analytical[0])**2 + (p[1] - analytical[1])**2))
            error = np.sqrt((closest_found[0] - analytical[0])**2 + (closest_found[1] - analytical[1])**2)
            max_error = max(max_error, error)
        
        print(f"  Maximum error: {max_error:.8f}")
        
        if max_error < 1e-4:
            print("  ✅ EXCELLENT: All intersections found with high accuracy!")
        elif max_error < 1e-2:
            print("  ✅ GOOD: All intersections found with reasonable accuracy")
        else:
            print("  ⚠️  FAIR: All intersections found but with some error")
    elif found_count > expected_count:
        print("  ⚠️  WARNING: More intersections found than expected (possible false positives)")
    else:
        print("  ❌ ERROR: Fewer intersections found than expected (missing intersections)")

if __name__ == "__main__":
    test_precise_intersections()