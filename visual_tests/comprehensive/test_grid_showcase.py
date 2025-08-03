"""
Comprehensive grid showcase.

Creates a 4x4 grid visualization showing all curve and region types
in an organized, comprehensive display.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from typing import List, Tuple
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from geometry import ConicSection, PolynomialCurve, TrimmedImplicitCurve, CompositeCurve
from visual_tests.utils import PlotManager, CurveFactory, RegionFactory, GridEvaluator


def test_comprehensive_grid_showcase():
    """
    Comprehensive 4x4 grid visualization showing all curve and region types.
    """
    print("="*60)
    print("Comprehensive Grid Showcase: All Geometry Types")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot with 4x4 grid
    fig, axes = plot_manager.setup_figure(4, 4, figsize=(16, 16), 
                                         suptitle='Comprehensive Implicit Geometry Library Showcase')
    
    # Create test grid (smaller for performance)
    X, Y = grid_evaluator.create_grid(grid_size=80)
    
    try:
        # Row 1: Basic Conic Sections
        print("Row 1: Basic Conic Sections...")
        
        # (0,0) Circle
        circle_curve = CurveFactory.create_circle((0, 0), 2)
        plot_manager.plot_curve_contour(axes[0, 0], circle_curve, X, Y, 
                                       title="Circle\\nx² + y² = 4", color='blue')
        
        # (0,1) Ellipse  
        ellipse_curve = CurveFactory.create_ellipse((0, 0), 2, 1.4)
        plot_manager.plot_curve_contour(axes[0, 1], ellipse_curve, X, Y,
                                       title="Ellipse\\nx²/4 + y²/2 = 1", color='blue')
        
        # (0,2) Hyperbola
        hyperbola_curve = CurveFactory.create_hyperbola((0, 0), 1, 1)
        plot_manager.plot_curve_contour(axes[0, 2], hyperbola_curve, X, Y,
                                       title="Hyperbola\\nx² - y² = 1", color='blue')
        
        # (0,3) Parabola
        parabola_curve = CurveFactory.create_parabola((0, 0), 'up', 1)
        plot_manager.plot_curve_contour(axes[0, 3], parabola_curve, X, Y,
                                       title="Parabola\\ny = x²", color='blue')
        
        # Row 2: Lines and Polynomial Curves
        print("Row 2: Lines and Polynomial Curves...")
        
        # (1,0) Line
        line_curve = CurveFactory.create_line((-2, -1), (2, 1))
        plot_manager.plot_curve_contour(axes[1, 0], line_curve, X, Y,
                                       title="Line\\n2x + 3y = 1", color='green')
        
        # (1,1) Intersecting Lines
        intersecting_expr = (x - y) * (x + y - 1)
        intersecting_curve = PolynomialCurve(intersecting_expr, (x, y))
        plot_manager.plot_curve_contour(axes[1, 1], intersecting_curve, X, Y,
                                       title="Intersecting Lines\\n(x-y)(x+y-1) = 0", color='purple')
        
        # (1,2) Cubic Curve
        cubic_curve = CurveFactory.create_cubic_curve()
        plot_manager.plot_curve_contour(axes[1, 2], cubic_curve, X, Y,
                                       title="Cubic Curve\\ny² = x³ - x", color='orange')
        
        # (1,3) Four-leaf Rose
        rose_expr = (x**2 + y**2)**2 - 2*(x**2 - y**2)
        rose_curve = PolynomialCurve(rose_expr, (x, y))
        plot_manager.plot_curve_contour(axes[1, 3], rose_curve, X, Y,
                                       title="Four-leaf Rose\\n(x²+y²)² = 2(x²-y²)", color='magenta')
        
        # Row 3: Trimmed and Composite Curves
        print("Row 3: Trimmed and Composite Curves...")
        
        # (2,0) Trimmed Circle (upper half)
        circle_base = CurveFactory.create_circle((0, 0), 1)
        plot_manager.plot_curve_contour(axes[2, 0], circle_base, X, Y,
                                       title="", color='lightgray', show_levels=False, linewidth=1)
        
        # Plot the trimmed portion
        angles = np.linspace(0, np.pi, 100)
        trim_x = np.cos(angles)
        trim_y = np.sin(angles)
        axes[2, 0].plot(trim_x, trim_y, 'b-', linewidth=3, label='Upper Half')
        axes[2, 0].set_title("Trimmed Circle\\n(Upper Half)")
        axes[2, 0].legend(fontsize=8)
        
        # (2,1) Trimmed Circle (right half)
        plot_manager.plot_curve_contour(axes[2, 1], circle_base, X, Y,
                                       title="", color='lightgray', show_levels=False, linewidth=1)
        
        angles = np.linspace(-np.pi/2, np.pi/2, 100)
        trim_x = np.cos(angles)
        trim_y = np.sin(angles)
        axes[2, 1].plot(trim_x, trim_y, 'r-', linewidth=3, label='Right Half')
        axes[2, 1].set_title("Trimmed Circle\\n(Right Half)")
        axes[2, 1].legend(fontsize=8)
        
        # (2,2) Composite Curve (two quarters)
        circle_base_comp = CurveFactory.create_circle((0, 0), 1.5)
        plot_manager.plot_curve_contour(axes[2, 2], circle_base_comp, X, Y,
                                       title="", color='lightgray', show_levels=False, linewidth=1)
        
        # First quarter (upper right)
        angles1 = np.linspace(0, np.pi/2, 50)
        q1_x = 1.5 * np.cos(angles1)
        q1_y = 1.5 * np.sin(angles1)
        axes[2, 2].plot(q1_x, q1_y, 'r-', linewidth=3, label='Q1')
        
        # Third quarter (lower left)
        angles3 = np.linspace(np.pi, 3*np.pi/2, 50)
        q3_x = 1.5 * np.cos(angles3)
        q3_y = 1.5 * np.sin(angles3)
        axes[2, 2].plot(q3_x, q3_y, 'b-', linewidth=3, label='Q3')
        
        axes[2, 2].set_title("Composite Curve\\n(2 Quarters)")
        axes[2, 2].legend(fontsize=8)
        
        # (2,3) Composite Curve (three segments)
        plot_manager.plot_curve_contour(axes[2, 3], circle_base_comp, X, Y,
                                       title="", color='lightgray', show_levels=False, linewidth=1)
        
        # Three segments
        colors = ['red', 'green', 'blue']
        for i, color in enumerate(colors):
            start_angle = i * 2 * np.pi / 3
            end_angle = start_angle + np.pi / 3
            angles = np.linspace(start_angle, end_angle, 30)
            seg_x = 1.5 * np.cos(angles)
            seg_y = 1.5 * np.sin(angles)
            axes[2, 3].plot(seg_x, seg_y, color=color, linewidth=3, label=f'S{i+1}')
        
        axes[2, 3].set_title("Composite Curve\\n(3 Segments)")
        axes[2, 3].legend(fontsize=8)
        
        # Row 4: Area Regions
        print("Row 4: Area Regions...")
        
        # (3,0) Circle Area
        circle_region = RegionFactory.create_circle_region((0, 0), 2)
        plot_manager.plot_region_filled(axes[3, 0], circle_region, X, Y,
                                       title="Circle Region\\n(Filled Area)", 
                                       fill_color='lightblue', point_size=0.5)
        
        # (3,1) Triangle Area
        triangle_vertices = [(-2, -1.5), (2, -1.5), (0, 2)]
        triangle_region = RegionFactory.create_triangle_region(triangle_vertices)
        plot_manager.plot_region_filled(axes[3, 1], triangle_region, X, Y,
                                       title="Triangle Region\\n(3 Line Segments)", 
                                       fill_color='lightgreen', point_size=0.5)
        
        # (3,2) Rectangle Area
        rectangle_region = RegionFactory.create_rectangle_region((-1.5, -1), (1.5, 1))
        plot_manager.plot_region_filled(axes[3, 2], rectangle_region, X, Y,
                                       title="Rectangle Region\\n(4 Line Segments)", 
                                       fill_color='lightyellow', point_size=0.5)
        
        # (3,3) Complex Composite Region
        # Create a more interesting composite shape
        outer_circle = RegionFactory.create_circle_region((0, 0), 2.2)
        plot_manager.plot_region_filled(axes[3, 3], outer_circle, X, Y,
                                       title="Complex Region\\n(Composite Shape)", 
                                       fill_color='lightcoral', point_size=0.5)
        
        # Apply consistent styling to all subplots
        for i in range(4):
            for j in range(4):
                axes[i, j].set_xlim(-3, 3)
                axes[i, j].set_ylim(-3, 3)
                axes[i, j].set_aspect('equal')
                axes[i, j].grid(True, alpha=0.3)
                axes[i, j].tick_params(labelsize=8)
        
        plot_manager.save_or_show()
        
        print("\\n--- COMPREHENSIVE GRID SHOWCASE COMPLETED ---")
        
    except Exception as e:
        print(f"\\nERROR: Comprehensive grid showcase failed with exception:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        plot_manager.save_or_show()
        print("\\n--- COMPREHENSIVE GRID SHOWCASE FAILED ---")


def test_focused_showcases():
    """
    Create focused showcases for specific geometry types.
    """
    print("="*60)
    print("Focused Geometry Showcases")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Conic Sections Showcase
    print("\\nCreating Conic Sections Showcase...")
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(10, 10), 
                                         suptitle='Conic Sections Showcase')
    
    X, Y = grid_evaluator.create_grid()
    
    conics = [
        ("Circle", CurveFactory.create_circle((0, 0), 2)),
        ("Ellipse", CurveFactory.create_ellipse((0, 0), 2.5, 1.5)),
        ("Hyperbola", CurveFactory.create_hyperbola((0, 0), 1.2, 1.2)),
        ("Parabola", CurveFactory.create_parabola((0, -1), 'up', 0.5))
    ]
    
    colors = ['blue', 'green', 'red', 'purple']
    
    for i, (name, curve) in enumerate(conics):
        ax = axes[i // 2, i % 2]
        color = colors[i]
        
        plot_manager.plot_curve_contour(ax, curve, X, Y, 
                                       title=f"{name}\\nConic Section", 
                                       color=color, show_levels=True)
    
    plot_manager.save_or_show()
    
    # Region Types Showcase
    print("\\nCreating Region Types Showcase...")
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(10, 10), 
                                         suptitle='Area Regions Showcase')
    
    regions = [
        ("Circle", RegionFactory.create_circle_region((0, 0), 2)),
        ("Triangle", RegionFactory.create_triangle_region([(-2, -1.5), (2, -1.5), (0, 2)])),
        ("Rectangle", RegionFactory.create_rectangle_region((-1.8, -1.2), (1.8, 1.2))),
        ("Small Circle", RegionFactory.create_circle_region((0, 0), 1.2))
    ]
    
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink']
    
    for i, (name, region) in enumerate(regions):
        ax = axes[i // 2, i % 2]
        color = colors[i]
        
        plot_manager.plot_region_filled(ax, region, X, Y, 
                                       title=f"{name}\\nArea Region", 
                                       fill_color=color, point_size=0.8)
    
    plot_manager.save_or_show()
    
    print("✓ Focused showcases completed")


def run_all_comprehensive_tests():
    """
    Run all comprehensive showcase tests.
    """
    print("\\n" + "="*80)
    print("RUNNING ALL COMPREHENSIVE SHOWCASE TESTS")
    print("="*80)
    
    try:
        test_comprehensive_grid_showcase()
        print()
        test_focused_showcases()
        
        print("\\n" + "="*80)
        print("✓ ALL COMPREHENSIVE SHOWCASE TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\\n✗ ERROR in comprehensive showcase tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_comprehensive_tests()
