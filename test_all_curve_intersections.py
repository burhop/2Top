#!/usr/bin/env python3
"""
Test intersections between all curve types
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.curve_intersections import find_curve_intersections

def test_all_curve_intersections():
    """Test intersections between different curve types"""
    
    print("🌟 COMPREHENSIVE CURVE INTERSECTION TESTING")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Define test curves of each type
    test_curves = [
        ("Circle", ConicSection(x**2 + y**2 - 1, (x, y))),
        ("Ellipse", ConicSection(x**2/4 + y**2 - 1, (x, y))),
        ("Line", PolynomialCurve(x + y, (x, y))),
        ("Parabola", PolynomialCurve(y - x**2, (x, y))),
        ("Hyperbola", PolynomialCurve(x**2 - y**2 - 1, (x, y))),
        ("Superellipse", Superellipse(a=1.2, b=1.0, n=4.0, variables=(x, y))),
        ("Cubic", PolynomialCurve(x**3 + y**3 - 1, (x, y))),
    ]
    
    print(f"Testing {len(test_curves)} curve types:")
    for name, curve in test_curves:
        print(f"  • {name}: {curve}")
    
    # Test all pairwise combinations
    print(f"\n🔍 Finding intersections for all pairs...")
    
    intersection_results = {}
    total_intersections = 0
    
    for i in range(len(test_curves)):
        for j in range(i + 1, len(test_curves)):
            name1, curve1 = test_curves[i]
            name2, curve2 = test_curves[j]
            
            pair_name = f"{name1} ∩ {name2}"
            print(f"\n  {pair_name}:")
            
            try:
                # Find intersections with appropriate settings
                intersections = find_curve_intersections(
                    curve1, curve2,
                    search_range=4.0,
                    grid_resolution=500,
                    tolerance=1e-8,
                    max_points=15
                )
                
                intersection_results[pair_name] = intersections
                total_intersections += len(intersections)
                
                if intersections:
                    print(f"    Found {len(intersections)} intersection(s):")
                    for k, (px, py) in enumerate(intersections):
                        # Verify intersection
                        val1 = curve1.evaluate(px, py)
                        val2 = curve2.evaluate(px, py)
                        error = max(abs(val1), abs(val2))
                        
                        print(f"      {k+1}. ({px:7.4f}, {py:7.4f}) - error: {error:.2e}")
                else:
                    print("    No intersections found")
                    
            except Exception as e:
                print(f"    Error: {e}")
                intersection_results[pair_name] = []
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  Total curve pairs tested: {len(intersection_results)}")
    print(f"  Total intersections found: {total_intersections}")
    print(f"  Average intersections per pair: {total_intersections/len(intersection_results):.1f}")
    
    # Show pairs with most intersections
    sorted_results = sorted(intersection_results.items(), 
                           key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n🏆 Pairs with most intersections:")
    for i, (pair_name, intersections) in enumerate(sorted_results[:5]):
        if intersections:
            print(f"  {i+1}. {pair_name}: {len(intersections)} intersections")
    
    # Create visualization
    print(f"\n🎨 Creating comprehensive visualization...")
    
    # Select interesting pairs for visualization
    interesting_pairs = [
        ("Circle", "Line"),
        ("Circle", "Ellipse"), 
        ("Parabola", "Line"),
        ("Circle", "Superellipse"),
        ("Hyperbola", "Line"),
        ("Cubic", "Line"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Intersection Tests: Various Curve Combinations', fontsize=16, fontweight='bold')
    
    plot_range = 3
    resolution = 400
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    for idx, (type1, type2) in enumerate(interesting_pairs):
        if idx >= 6:  # Only 6 subplots
            break
            
        ax = axes[idx // 3, idx % 3]
        
        # Find curves of these types
        curve1 = next((curve for name, curve in test_curves if name == type1), None)
        curve2 = next((curve for name, curve in test_curves if name == type2), None)
        
        if curve1 is None or curve2 is None:
            continue
        
        try:
            # Plot curves
            Z1 = curve1.evaluate(X, Y)
            Z2 = curve2.evaluate(X, Y)
            
            ax.contour(X, Y, Z1, levels=[0], colors=['blue'], linewidths=2.5)
            ax.contour(X, Y, Z2, levels=[0], colors=['red'], linewidths=2.5)
            
            # Plot intersections
            pair_key = f"{type1} ∩ {type2}"
            if pair_key in intersection_results:
                intersections = intersection_results[pair_key]
                for px, py in intersections:
                    ax.plot(px, py, 'go', markersize=8, markeredgecolor='black', 
                           markeredgewidth=1.5, zorder=10)
            
            ax.set_xlim(-plot_range, plot_range)
            ax.set_ylim(-plot_range, plot_range)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(f'{type1} ∩ {type2}\n({len(intersection_results.get(pair_key, []))} intersections)')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {type1} ∩ {type2}', 
                   ha='center', va='center', transform=ax.transAxes)
            print(f"Error plotting {type1} ∩ {type2}: {e}")
    
    plt.tight_layout()
    plt.savefig('all_curve_intersections.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: all_curve_intersections.png")
    
    # Detailed analysis of specific interesting cases
    print(f"\n🔬 DETAILED ANALYSIS:")
    
    interesting_cases = [
        ("Circle ∩ Line", "Should have exactly 2 intersections"),
        ("Circle ∩ Ellipse", "Can have 0, 2, or 4 intersections"),
        ("Parabola ∩ Line", "Typically 0, 1, or 2 intersections"),
        ("Circle ∩ Superellipse", "Complex intersection pattern"),
    ]
    
    for case_name, expected in interesting_cases:
        if case_name in intersection_results:
            found = len(intersection_results[case_name])
            print(f"  {case_name}: Found {found} - {expected}")
        else:
            print(f"  {case_name}: Not tested")
    
    print(f"\n🎯 Testing complete! Check the visualization for detailed results.")

if __name__ == "__main__":
    test_all_curve_intersections()