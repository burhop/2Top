#!/usr/bin/env python3
"""
Test multi-segment curve intersections
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_multi_segment_intersections():
    """Test intersections with multi-segment curves"""
    
    print("🔧 MULTI-SEGMENT CURVE INTERSECTION TESTING")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Test 1: Trimmed circle vs line
    print("\n📐 Test 1: Trimmed Circle vs Line")
    print("-" * 40)
    
    # Right half of unit circle
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    right_half_mask = lambda x_val, y_val: x_val >= 0
    trimmed_circle = TrimmedImplicitCurve(circle, right_half_mask)
    
    # Horizontal line through center
    line = PolynomialCurve(y, (x, y))
    
    print(f"  Trimmed Circle: Right half of x² + y² = 1")
    print(f"  Line: y = 0")
    
    intersections = find_curve_intersections(
        trimmed_circle, line,
        search_range=2.0,
        grid_resolution=400,
        tolerance=1e-8
    )
    
    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        # Verify intersection
        val1 = trimmed_circle.evaluate(px, py)
        val2 = line.evaluate(px, py)
        on_trimmed = trimmed_circle.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))
        
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}, on_trimmed: {on_trimmed}")
    
    # Test 2: Composite square vs line
    print("\n📦 Test 2: Composite Square vs Line")
    print("-" * 40)
    
    # Create square from edges
    square = create_square_from_edges((-1, -1), (1, 1))
    
    # Diagonal line
    diagonal = PolynomialCurve(x - y, (x, y))
    
    print(f"  Square: Composite curve from (-1,-1) to (1,1)")
    print(f"  Line: y = x")
    
    intersections = find_curve_intersections(
        square, diagonal,
        search_range=2.0,
        grid_resolution=400,
        tolerance=1e-8
    )
    
    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        val1 = square.evaluate(px, py)
        val2 = diagonal.evaluate(px, py)
        on_square = square.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))
        
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}, on_square: {on_square}")
    
    # Test 3: Two trimmed curves
    print("\n✂️ Test 3: Two Trimmed Curves")
    print("-" * 40)
    
    # Upper half of circle
    upper_mask = lambda x_val, y_val: y_val >= 0
    upper_circle = TrimmedImplicitCurve(circle, upper_mask)
    
    # Right half of ellipse
    ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
    right_ellipse = TrimmedImplicitCurve(ellipse, right_half_mask)
    
    print(f"  Upper Circle: Upper half of x² + y² = 1")
    print(f"  Right Ellipse: Right half of x²/4 + y² = 1")
    
    intersections = find_curve_intersections(
        upper_circle, right_ellipse,
        search_range=3.0,
        grid_resolution=500,
        tolerance=1e-8
    )
    
    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        val1 = upper_circle.evaluate(px, py)
        val2 = right_ellipse.evaluate(px, py)
        on_upper = upper_circle.contains(px, py, 1e-6)
        on_right = right_ellipse.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))
        
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}")
        print(f"        on_upper: {on_upper}, on_right: {on_right}")
    
    # Test 4: Circle quarters vs line
    print("\n🍕 Test 4: Circle Quarters vs Line")
    print("-" * 40)
    
    # Create circle from quarters
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.5)
    
    # Vertical line
    vertical = PolynomialCurve(x - 0.5, (x, y))
    
    print(f"  Circle Quarters: Composite circle with radius 1.5")
    print(f"  Line: x = 0.5")
    
    intersections = find_curve_intersections(
        circle_quarters, vertical,
        search_range=2.0,
        grid_resolution=400,
        tolerance=1e-8
    )
    
    print(f"  Found {len(intersections)} intersection(s):")
    for i, (px, py) in enumerate(intersections):
        val1 = circle_quarters.evaluate(px, py)
        val2 = vertical.evaluate(px, py)
        on_quarters = circle_quarters.contains(px, py, 1e-6)
        error = max(abs(val1), abs(val2))
        
        print(f"    {i+1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}, on_quarters: {on_quarters}")
    
    # Create comprehensive visualization
    print(f"\n🎨 Creating multi-segment intersection visualization...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.suptitle('Multi-Segment Curve Intersections', fontsize=16, fontweight='bold')
    
    test_cases = [
        (trimmed_circle, line, "Trimmed Circle ∩ Line", intersections),
        (square, diagonal, "Square ∩ Diagonal", []),  # Will recalculate
        (upper_circle, right_ellipse, "Upper Circle ∩ Right Ellipse", []),
        (circle_quarters, vertical, "Circle Quarters ∩ Vertical", [])
    ]
    
    plot_range = 2
    resolution = 400
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    for idx, (curve1, curve2, title, intersections) in enumerate(test_cases):
        ax = axes[idx // 2, idx % 2]
        
        # Recalculate intersections for plotting
        if not intersections:
            intersections = find_curve_intersections(
                curve1, curve2,
                search_range=plot_range,
                grid_resolution=300,
                tolerance=1e-8
            )
        
        try:
            # Plot curves
            Z1 = curve1.evaluate(X, Y)
            Z2 = curve2.evaluate(X, Y)
            
            ax.contour(X, Y, Z1, levels=[0], colors=['blue'], linewidths=2.5, alpha=0.8)
            ax.contour(X, Y, Z2, levels=[0], colors=['red'], linewidths=2.5, alpha=0.8)
            
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
    plt.savefig('multi_segment_intersections.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: multi_segment_intersections.png")
    
    print(f"\n✅ Multi-segment intersection testing complete!")

if __name__ == "__main__":
    test_multi_segment_intersections()