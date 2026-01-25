#!/usr/bin/env python3
"""
Analysis of curve intersection vs R-function operations
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *

def analyze_intersection_concepts():
    """Analyze the difference between curve intersections and R-function operations"""
    
    print("🔍 CURVE INTERSECTION ANALYSIS")
    print("=" * 50)
    
    x, y = sp.symbols('x y')
    
    # Create two simple curves that intersect
    circle = ConicSection(x**2 + y**2 - 1, (x, y))  # Unit circle
    line = PolynomialCurve(x + y, (x, y))  # Line y = -x
    
    print("Test curves:")
    print(f"  Circle: {circle}")
    print(f"  Line: {line}")
    
    # 1. Find actual intersection points analytically
    print("\n1. 📍 Analytical Intersection Points:")
    
    # Solve x² + y² = 1 and y = -x simultaneously
    # Substitute: x² + (-x)² = 1 → 2x² = 1 → x = ±1/√2
    intersection_points = [
        (1/np.sqrt(2), -1/np.sqrt(2)),
        (-1/np.sqrt(2), 1/np.sqrt(2))
    ]
    
    print("  Analytical solutions:")
    for i, (px, py) in enumerate(intersection_points):
        print(f"    Point {i+1}: ({px:.4f}, {py:.4f})")
        
        # Verify these points are on both curves
        circle_val = circle.evaluate(px, py)
        line_val = line.evaluate(px, py)
        print(f"      Circle value: {circle_val:.6f} (should be ≈ 0)")
        print(f"      Line value: {line_val:.6f} (should be ≈ 0)")
    
    # 2. What R-function "intersection" actually does
    print("\n2. 🔗 R-Function 'Intersection' (max operation):")
    
    rfunction_intersect = intersect(circle, line)
    print(f"  R-function result: {type(rfunction_intersect).__name__}")
    
    # Test points to understand what this represents
    test_points = [
        (0, 0),      # Origin (inside circle, on line)
        (0.5, -0.5), # Inside circle, on line
        (0.8, 0),    # Inside circle, off line
        (0, 0.8),    # Inside circle, off line
        (1.5, 0),    # Outside circle, off line
    ]
    
    print("  Testing R-function intersection at various points:")
    for px, py in test_points:
        circle_val = circle.evaluate(px, py)
        line_val = line.evaluate(px, py)
        rfunction_val = rfunction_intersect.evaluate(px, py)
        max_val = max(circle_val, line_val)
        
        print(f"    ({px:4.1f}, {py:4.1f}): circle={circle_val:6.2f}, line={line_val:6.2f}, "
              f"max={max_val:6.2f}, R-func={rfunction_val:6.2f}")
    
    print("\n  R-function intersection represents: points inside BOTH curves")
    print("  (i.e., the region where both f1 ≤ 0 AND f2 ≤ 0)")
    
    # 3. Numerical intersection finding
    print("\n3. 🎯 Numerical Intersection Finding:")
    
    def find_curve_intersections(curve1, curve2, search_range=3, resolution=1000):
        """Find intersection points numerically"""
        
        # Create a fine grid
        x_vals = np.linspace(-search_range, search_range, resolution)
        y_vals = np.linspace(-search_range, search_range, resolution)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        # Evaluate both curves
        Z1 = curve1.evaluate(X, Y)
        Z2 = curve2.evaluate(X, Y)
        
        # Find points where both curves are close to zero
        tolerance = 0.05
        mask1 = np.abs(Z1) < tolerance
        mask2 = np.abs(Z2) < tolerance
        intersection_mask = mask1 & mask2
        
        # Extract intersection points
        x_intersect = X[intersection_mask]
        y_intersect = Y[intersection_mask]
        
        return x_intersect, y_intersect
    
    x_intersect, y_intersect = find_curve_intersections(circle, line)
    
    print(f"  Found {len(x_intersect)} numerical intersection points:")
    
    # Cluster nearby points (they might be duplicated due to grid sampling)
    if len(x_intersect) > 0:
        from scipy.spatial.distance import pdist, squareform
        from scipy.cluster.hierarchy import fcluster, linkage
        
        if len(x_intersect) > 1:
            points = np.column_stack([x_intersect, y_intersect])
            distances = pdist(points)
            linkage_matrix = linkage(distances)
            clusters = fcluster(linkage_matrix, 0.1, criterion='distance')
            
            # Get cluster centers
            unique_clusters = np.unique(clusters)
            cluster_centers = []
            
            for cluster_id in unique_clusters:
                cluster_points = points[clusters == cluster_id]
                center = np.mean(cluster_points, axis=0)
                cluster_centers.append(center)
            
            for i, (cx, cy) in enumerate(cluster_centers):
                print(f"    Cluster {i+1}: ({cx:.4f}, {cy:.4f})")
        else:
            print(f"    Single point: ({x_intersect[0]:.4f}, {y_intersect[0]:.4f})")
    
    # 4. Visualization
    print("\n4. 🎨 Creating Visualization...")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Curve Intersections vs R-Function Operations', fontsize=14, fontweight='bold')
    
    # Plot parameters
    plot_range = 2
    resolution = 400
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Plot 1: Original curves with intersection points
    ax1 = axes[0]
    Z_circle = circle.evaluate(X, Y)
    Z_line = line.evaluate(X, Y)
    
    ax1.contour(X, Y, Z_circle, levels=[0], colors=['blue'], linewidths=2, label='Circle')
    ax1.contour(X, Y, Z_line, levels=[0], colors=['red'], linewidths=2, label='Line')
    
    # Mark analytical intersection points
    for px, py in intersection_points:
        ax1.plot(px, py, 'ko', markersize=8, label='Intersection' if px == intersection_points[0][0] else "")
    
    ax1.set_xlim(-plot_range, plot_range)
    ax1.set_ylim(-plot_range, plot_range)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Original Curves + Intersection Points')
    ax1.legend()
    
    # Plot 2: R-function intersection (region)
    ax2 = axes[1]
    Z_rfunction = rfunction_intersect.evaluate(X, Y)
    
    ax2.contour(X, Y, Z_rfunction, levels=[0], colors=['green'], linewidths=2)
    ax2.contourf(X, Y, Z_rfunction, levels=[-1000, 0, 1000], 
                colors=['lightgreen', 'white'], alpha=0.5)
    
    ax2.set_xlim(-plot_range, plot_range)
    ax2.set_ylim(-plot_range, plot_range)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('R-Function "Intersection"\n(Region inside both)')
    
    # Plot 3: Union for comparison
    ax3 = axes[2]
    union_curve = union(circle, line)
    Z_union = union_curve.evaluate(X, Y)
    
    ax3.contour(X, Y, Z_union, levels=[0], colors=['purple'], linewidths=2)
    ax3.contourf(X, Y, Z_union, levels=[-1000, 0, 1000], 
                colors=['plum', 'white'], alpha=0.5)
    
    ax3.set_xlim(-plot_range, plot_range)
    ax3.set_ylim(-plot_range, plot_range)
    ax3.set_aspect('equal')
    ax3.grid(True, alpha=0.3)
    ax3.set_title('R-Function Union\n(Region inside either)')
    
    plt.tight_layout()
    plt.savefig('intersection_analysis.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: intersection_analysis.png")
    
    # 5. Recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = [
        "🎯 Separate curve intersection from R-function operations",
        "📍 Add find_intersections() method to return discrete points",
        "🏷️  Rename current intersect() to region_intersection() or inside_both()",
        "🎨 Update visualizer to show intersection points as dots, not areas",
        "📚 Add clear documentation explaining the difference",
        "🔧 Consider adding curve-curve intersection solver",
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print(f"\n🎉 Analysis complete!")

if __name__ == "__main__":
    analyze_intersection_concepts()