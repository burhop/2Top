#!/usr/bin/env python3
"""
Test overlapping curve intersections to understand the behavior
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_overlapping_curves():
    """Test what happens when curves overlap vs just intersect"""
    
    print("🔄 OVERLAPPING CURVE INTERSECTION ANALYSIS")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Test 1: Two identical circles (complete overlap)
    print("\n🔵 Test 1: Two Identical Circles (Complete Overlap)")
    print("-" * 50)
    
    circle1 = ConicSection(x**2 + y**2 - 1, (x, y))
    circle2 = ConicSection(x**2 + y**2 - 1, (x, y))  # Identical
    
    intersections = find_curve_intersections(circle1, circle2, search_range=2.0, tolerance=1e-8)
    print(f"  Circle 1: x² + y² = 1")
    print(f"  Circle 2: x² + y² = 1 (identical)")
    print(f"  Found {len(intersections)} intersection(s)")
    
    # Test 2: Quarter circle vs half circle (partial overlap)
    print("\n🌗 Test 2: Quarter Circle vs Half Circle (Partial Overlap)")
    print("-" * 50)
    
    # Quarter circle (first quadrant)
    quarter_mask = lambda x_val, y_val: (x_val >= 0) & (y_val >= 0)
    quarter_circle = TrimmedImplicitCurve(circle1, quarter_mask)
    
    # Half circle (right half)
    half_mask = lambda x_val, y_val: x_val >= 0
    half_circle = TrimmedImplicitCurve(circle1, half_mask)
    
    intersections = find_curve_intersections(quarter_circle, half_circle, search_range=2.0, tolerance=1e-8)
    print(f"  Quarter Circle: First quadrant of x² + y² = 1")
    print(f"  Half Circle: Right half of x² + y² = 1")
    print(f"  Found {len(intersections)} intersection(s)")
    for i, (px, py) in enumerate(intersections):
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f})")
    
    # Test 3: Two line segments that overlap
    print("\n📏 Test 3: Two Overlapping Line Segments")
    print("-" * 50)
    
    # Horizontal line y = 0
    line_base = PolynomialCurve(y, (x, y))
    
    # First segment: x from -1 to 1
    segment1_mask = lambda x_val, y_val: (-1 <= x_val <= 1)
    segment1 = TrimmedImplicitCurve(line_base, segment1_mask)
    
    # Second segment: x from 0 to 2 (overlaps from 0 to 1)
    segment2_mask = lambda x_val, y_val: (0 <= x_val <= 2)
    segment2 = TrimmedImplicitCurve(line_base, segment2_mask)
    
    intersections = find_curve_intersections(segment1, segment2, search_range=3.0, tolerance=1e-8)
    print(f"  Segment 1: y = 0, x ∈ [-1, 1]")
    print(f"  Segment 2: y = 0, x ∈ [0, 2]")
    print(f"  Expected: Overlap from x = 0 to x = 1")
    print(f"  Found {len(intersections)} intersection(s)")
    for i, (px, py) in enumerate(intersections):
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f})")
    
    # Test 4: Two circles that intersect at discrete points (normal case)
    print("\n⭕ Test 4: Two Circles with Discrete Intersections")
    print("-" * 50)
    
    circle_a = ConicSection(x**2 + y**2 - 1, (x, y))
    circle_b = ConicSection((x-1)**2 + y**2 - 1, (x, y))
    
    intersections = find_curve_intersections(circle_a, circle_b, search_range=2.0, tolerance=1e-8)
    print(f"  Circle A: x² + y² = 1")
    print(f"  Circle B: (x-1)² + y² = 1")
    print(f"  Expected: 2 discrete intersection points")
    print(f"  Found {len(intersections)} intersection(s)")
    for i, (px, py) in enumerate(intersections):
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f})")
    
    # Visualization
    print(f"\n🎨 Creating overlapping curves visualization...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.suptitle('Overlapping vs Intersecting Curves', fontsize=16, fontweight='bold')
    
    test_cases = [
        (circle1, circle2, "Identical Circles", []),
        (quarter_circle, half_circle, "Quarter ∩ Half Circle", []),
        (segment1, segment2, "Overlapping Line Segments", []),
        (circle_a, circle_b, "Two Intersecting Circles", [])
    ]
    
    plot_range = 2.5
    resolution = 400
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    for idx, (curve1, curve2, title, _) in enumerate(test_cases):
        ax = axes[idx // 2, idx % 2]
        
        # Recalculate intersections for this plot
        intersections = find_curve_intersections(curve1, curve2, search_range=plot_range, tolerance=1e-8)
        
        try:
            # Plot curves with special handling for trimmed curves
            if hasattr(curve1, 'base_curve'):
                Z1 = curve1.base_curve.evaluate(X, Y)
                if hasattr(curve1, '_xmin') and curve1._xmin is not None:
                    mask1 = ((X >= curve1._xmin) & (X <= curve1._xmax) & 
                            (Y >= curve1._ymin) & (Y <= curve1._ymax))
                else:
                    mask1 = np.ones_like(X, dtype=bool)
                    for i in range(X.shape[0]):
                        for j in range(X.shape[1]):
                            mask1[i, j] = curve1.mask(X[i, j], Y[i, j])
                Z1_masked = np.where(mask1, Z1, np.nan)
            else:
                Z1_masked = curve1.evaluate(X, Y)
            
            if hasattr(curve2, 'base_curve'):
                Z2 = curve2.base_curve.evaluate(X, Y)
                if hasattr(curve2, '_xmin') and curve2._xmin is not None:
                    mask2 = ((X >= curve2._xmin) & (X <= curve2._xmax) & 
                            (Y >= curve2._ymin) & (Y <= curve2._ymax))
                else:
                    mask2 = np.ones_like(X, dtype=bool)
                    for i in range(X.shape[0]):
                        for j in range(X.shape[1]):
                            mask2[i, j] = curve2.mask(X[i, j], Y[i, j])
                Z2_masked = np.where(mask2, Z2, np.nan)
            else:
                Z2_masked = curve2.evaluate(X, Y)
            
            ax.contour(X, Y, Z1_masked, levels=[0], colors=['blue'], linewidths=3, alpha=0.7)
            ax.contour(X, Y, Z2_masked, levels=[0], colors=['red'], linewidths=3, alpha=0.7)
            
            # Plot intersections
            for px, py in intersections:
                ax.plot(px, py, 'go', markersize=10, markeredgecolor='black', 
                       markeredgewidth=2, zorder=10)
                ax.annotate(f'({px:.2f}, {py:.2f})', xy=(px, py), xytext=(5, 5),
                           textcoords='offset points', fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
            
            ax.set_xlim(-plot_range, plot_range)
            ax.set_ylim(-plot_range, plot_range)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'{title}\n({len(intersections)} intersections)')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {title}', 
                   ha='center', va='center', transform=ax.transAxes)
            print(f"Error plotting {title}: {e}")
    
    plt.tight_layout()
    plt.savefig('overlapping_curves_analysis.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: overlapping_curves_analysis.png")
    
    # Analysis and recommendations
    print(f"\n📊 ANALYSIS & RECOMMENDATIONS:")
    print("-" * 40)
    print("For overlapping curves, we have several options:")
    print("1. 🎯 CURRENT BEHAVIOR: Find discrete points where curves meet")
    print("2. 🚫 NO INTERSECTIONS: Treat overlap as 'infinite intersections'")
    print("3. 📍 ENDPOINT DETECTION: Report endpoints of overlapping segments")
    print("4. 🔍 OVERLAP DETECTION: Detect and report overlapping regions")
    
    print(f"\n💡 RECOMMENDATION:")
    print("For most geometric applications, discrete intersection points are most useful.")
    print("Overlapping segments should be handled as a special case in higher-level logic.")
    print("Current behavior seems appropriate for intersection-based algorithms.")

if __name__ == "__main__":
    test_overlapping_curves()