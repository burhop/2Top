#!/usr/bin/env python3
"""
Test curve plotting functionality without GUI
"""

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from geometry import *

def test_curve_plotting():
    """Test plotting various implicit curves"""
    
    print("🎨 Testing Curve Plotting")
    print("=" * 40)
    
    # Set up matplotlib
    plt.style.use('default')
    
    x, y = sp.symbols('x y')
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('2Top Implicit Curves Gallery', fontsize=16, fontweight='bold')
    
    # Plot parameters
    resolution = 400
    plot_range = 3.0
    x_range = np.linspace(-plot_range, plot_range, resolution)
    y_range = np.linspace(-plot_range, plot_range, resolution)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Test curves
    curves = [
        ("Circle", ConicSection(x**2 + y**2 - 1, (x, y))),
        ("Ellipse", ConicSection(x**2/4 + y**2 - 1, (x, y))),
        ("Parabola", PolynomialCurve(y - x**2, (x, y))),
        ("Hyperbola", ConicSection(x**2 - y**2 - 1, (x, y))),
        ("Superellipse", Superellipse(a=1.5, b=1.0, n=4.0, variables=(x, y))),
        ("Heart", PolynomialCurve(((x**2 + y**2 - 1)**3) - (x**2 * y**3), (x, y))),
    ]
    
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown']
    
    for i, ((name, curve), ax, color) in enumerate(zip(curves, axes.flat, colors)):
        print(f"  Plotting {name}...")
        
        try:
            # Evaluate curve
            Z = curve.evaluate(X, Y)
            
            # Plot zero-level contour
            contour = ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2)
            
            # Add filled regions
            ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                       colors=[color, 'white'], alpha=0.2)
            
            # Styling
            ax.set_xlim(-plot_range, plot_range)
            ax.set_ylim(-plot_range, plot_range)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(name, fontweight='bold')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            
            print(f"    ✅ {name} plotted successfully")
            
        except Exception as e:
            print(f"    ❌ Error plotting {name}: {e}")
            ax.text(0.5, 0.5, f"Error: {name}", ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "curve_gallery.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n📁 Gallery saved as: {output_file}")
    
    # Test constructive geometry
    print("\n🔗 Testing Constructive Geometry...")
    
    fig2, axes2 = plt.subplots(1, 4, figsize=(16, 4))
    fig2.suptitle('Constructive Geometry Operations', fontsize=14, fontweight='bold')
    
    # Base curves
    c1 = ConicSection(x**2 + y**2 - 1, (x, y))
    c2 = ConicSection((x-0.8)**2 + y**2 - 1, (x, y))
    
    # Operations
    operations = [
        ("Original Circles", [c1, c2]),
        ("Union", [union(c1, c2)]),
        ("Intersection", [intersect(c1, c2)]),
        ("Difference", [difference(c1, c2)]),
    ]
    
    op_colors = [['blue', 'red'], ['green'], ['purple'], ['orange']]
    
    for (op_name, curves_list), ax, colors_list in zip(operations, axes2, op_colors):
        print(f"  Plotting {op_name}...")
        
        try:
            for curve, color in zip(curves_list, colors_list):
                Z = curve.evaluate(X, Y)
                ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2)
                ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                           colors=[color, 'white'], alpha=0.15)
            
            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(-2.5, 2.5)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(op_name, fontweight='bold')
            
            print(f"    ✅ {op_name} plotted successfully")
            
        except Exception as e:
            print(f"    ❌ Error plotting {op_name}: {e}")
    
    plt.tight_layout()
    
    # Save constructive geometry plot
    output_file2 = "constructive_geometry.png"
    plt.savefig(output_file2, dpi=300, bbox_inches='tight')
    print(f"📁 Constructive geometry saved as: {output_file2}")
    
    # Test composite curves
    print("\n🔗 Testing Composite Curves...")
    
    fig3, axes3 = plt.subplots(1, 2, figsize=(10, 5))
    fig3.suptitle('Composite Curves', fontsize=14, fontweight='bold')
    
    # Square and circle from quarters
    square = create_square_from_edges((-1.5, -1.5), (1.5, 1.5))
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.2)
    
    composite_curves = [
        ("Square from Edges", square),
        ("Circle from Quarters", circle_quarters),
    ]
    
    for (comp_name, comp_curve), ax in zip(composite_curves, axes3):
        print(f"  Plotting {comp_name}...")
        
        try:
            Z = comp_curve.evaluate(X, Y)
            ax.contour(X, Y, Z, levels=[0], colors=['darkblue'], linewidths=2.5)
            ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                       colors=['lightblue', 'white'], alpha=0.3)
            
            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(-2.5, 2.5)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title(comp_name, fontweight='bold')
            
            print(f"    ✅ {comp_name} plotted successfully")
            
        except Exception as e:
            print(f"    ❌ Error plotting {comp_name}: {e}")
    
    plt.tight_layout()
    
    # Save composite curves plot
    output_file3 = "composite_curves.png"
    plt.savefig(output_file3, dpi=300, bbox_inches='tight')
    print(f"📁 Composite curves saved as: {output_file3}")
    
    print(f"\n🎉 All plots generated successfully!")
    print(f"Files created:")
    print(f"  - {output_file}")
    print(f"  - {output_file2}")
    print(f"  - {output_file3}")

if __name__ == "__main__":
    test_curve_plotting()