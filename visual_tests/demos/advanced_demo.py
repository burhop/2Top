"""
Advanced demonstration of the geometry library.

Showcases complex features including trimmed curves, composite curves,
and advanced region operations.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from geometry import TrimmedImplicitCurve, CompositeCurve
from visual_tests.utils import PlotManager, CurveFactory, RegionFactory, GridEvaluator


def demo_trimmed_curves():
    """
    Demonstrate trimmed curve creation and visualization.
    """
    print("="*50)
    print("TRIMMED CURVES DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(12, 12), 
                                         suptitle='Trimmed Curves Demo')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    print("Creating trimmed curves with different masks...")
    
    # Create base circle
    base_circle = CurveFactory.create_circle((0, 0), 2)
    
    # Define different trimming masks
    masks = [
        ("Upper Half", lambda px, py: py >= 0),
        ("Right Half", lambda px, py: px >= 0),
        ("First Quadrant", lambda px, py: px >= 0 and py >= 0),
        ("Ring Segment", lambda px, py: 1 <= px**2 + py**2 <= 4 and py >= 0)
    ]
    
    # Create and plot trimmed curves
    for i, (name, mask_func) in enumerate(masks):
        ax = axes[i // 2, i % 2]
        
        print(f"  Creating {name} trimmed curve...")
        
        # Plot base circle lightly
        plot_manager.plot_curve_contour(ax, base_circle, X, Y, 
                                       title="", color='lightgray', 
                                       show_levels=False, linewidth=1)
        
        # Create trimmed curve
        trimmed_curve = TrimmedImplicitCurve(base_circle, mask_func)
        
        # Sample and plot points that satisfy the mask
        angles = np.linspace(0, 2*np.pi, 200)
        mask_x, mask_y = [], []
        
        for angle in angles:
            px = 2 * np.cos(angle)
            py = 2 * np.sin(angle)
            
            try:
                if mask_func(px, py):
                    mask_x.append(px)
                    mask_y.append(py)
            except:
                pass
        
        if mask_x:
            ax.plot(mask_x, mask_y, 'b-', linewidth=3, label='Trimmed Curve')
        
        ax.set_title(f"{name}\\nTrimmed Circle")
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.legend()
    
    plot_manager.save_or_show()
    print("✓ Trimmed curves demo completed")


def demo_composite_curves():
    """
    Demonstrate composite curve creation from multiple segments.
    """
    print("="*50)
    print("COMPOSITE CURVES DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(1, 2, figsize=(12, 6), 
                                         suptitle='Composite Curves Demo')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    print("Creating composite curves from multiple segments...")
    
    # Demo 1: Circle quarters composite
    ax = axes[0]
    
    print("  Creating composite from circle quarters...")
    
    circle_base = CurveFactory.create_circle((0, 0), 1.5)
    
    # Plot base circle lightly
    plot_manager.plot_curve_contour(ax, circle_base, X, Y, 
                                   title="", color='lightgray', 
                                   show_levels=False, linewidth=1)
    
    # Create quarter segments
    quarter1_mask = lambda px, py: px >= 0 and py >= 0  # First quadrant
    quarter3_mask = lambda px, py: px <= 0 and py <= 0  # Third quadrant
    
    quarter1 = TrimmedImplicitCurve(circle_base, quarter1_mask)
    quarter3 = TrimmedImplicitCurve(circle_base, quarter3_mask)
    
    composite_quarters = CompositeCurve([quarter1, quarter3], (x, y))
    
    # Plot the quarters
    colors = ['red', 'blue']
    angle_ranges = [(0, np.pi/2), (np.pi, 3*np.pi/2)]
    
    for i, (start_angle, end_angle) in enumerate(angle_ranges):
        angles = np.linspace(start_angle, end_angle, 50)
        qx = 1.5 * np.cos(angles)
        qy = 1.5 * np.sin(angles)
        ax.plot(qx, qy, color=colors[i], linewidth=3, 
               label=f'Quarter {i+1}')
    
    ax.set_title("Composite Curve\\n(2 Circle Quarters)")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.legend()
    
    # Demo 2: Mixed curve types
    ax = axes[1]
    
    print("  Creating composite from mixed curve types...")
    
    # Create a line segment and a circle arc
    line_curve = CurveFactory.create_line((-2, -1), (0, 1))
    circle_curve = CurveFactory.create_circle((0, 0), 1)
    
    # Plot reference curves lightly
    plot_manager.plot_curve_contour(ax, line_curve, X, Y, 
                                   title="", color='lightgray', 
                                   show_levels=False, linewidth=1)
    plot_manager.plot_curve_contour(ax, circle_curve, X, Y, 
                                   title="", color='lightgray', 
                                   show_levels=False, linewidth=1)
    
    # Plot the actual segments
    ax.plot([-2, 0], [-1, 1], 'r-', linewidth=3, label='Line Segment')
    
    angles = np.linspace(0, np.pi/2, 50)
    arc_x = np.cos(angles)
    arc_y = np.sin(angles)
    ax.plot(arc_x, arc_y, 'b-', linewidth=3, label='Circle Arc')
    
    ax.set_title("Mixed Composite\\n(Line + Arc)")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.legend()
    
    plot_manager.save_or_show()
    print("✓ Composite curves demo completed")


def demo_complex_regions():
    """
    Demonstrate complex region creation and analysis.
    """
    print("="*50)
    print("COMPLEX REGIONS DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(1, 3, figsize=(15, 5), 
                                         suptitle='Complex Regions Demo')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    print("Creating complex regions...")
    
    # Create different complex regions
    regions = [
        ("Large Circle", RegionFactory.create_circle_region((0, 0), 2.5)),
        ("Complex Triangle", RegionFactory.create_triangle_region([(-2.5, -2), (2.5, -2), (0, 2.5)])),
        ("Wide Rectangle", RegionFactory.create_rectangle_region((-2.8, -1.2), (2.8, 1.2)))
    ]
    
    colors = ['lightblue', 'lightgreen', 'lightyellow']
    
    # Plot and analyze each region
    for i, (name, region) in enumerate(regions):
        ax = axes[i]
        color = colors[i]
        
        print(f"  Analyzing {name}...")
        
        # Plot the region
        plot_manager.plot_region_filled(ax, region, X, Y, 
                                       title=f"{name}\\nComplex Region", 
                                       fill_color=color, point_size=0.8)
        
        # Analyze statistics
        inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
            region, X, Y, test_boundary=True)
        
        stats = grid_evaluator.analyze_grid_statistics(inside_mask, boundary_mask)
        
        print(f"    Inside points: {stats['inside_count']} ({stats['inside_percentage']:.1f}%)")
        print(f"    Boundary points: {stats['boundary_count']} ({stats['boundary_percentage']:.1f}%)")
    
    plot_manager.save_or_show()
    print("✓ Complex regions demo completed")


def demo_advanced_analysis():
    """
    Demonstrate advanced analysis techniques.
    """
    print("="*50)
    print("ADVANCED ANALYSIS DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator()
    
    print("Performing advanced analysis on geometric objects...")
    
    # Create test objects
    circle = CurveFactory.create_circle((0, 0), 2)
    ellipse = CurveFactory.create_ellipse((0, 0), 2.5, 1.5)
    triangle_region = RegionFactory.create_triangle_region([(-2, -1.5), (2, -1.5), (0, 2)])
    
    # Advanced point testing
    print("\\nAdvanced curve evaluation:")
    
    # Test curves at strategic points
    strategic_points = [
        (0, 0, "Origin"),
        (2, 0, "Right boundary"),
        (0, 2, "Top boundary"),
        (1.414, 1.414, "Diagonal boundary"),
        (2.5, 0, "Outside right"),
        (0, 2.5, "Outside top")
    ]
    
    for curve_name, curve in [("Circle", circle), ("Ellipse", ellipse)]:
        print(f"\\n  Testing {curve_name}:")
        results = grid_evaluator.test_specific_points(curve, strategic_points, 'curve')
        
        # Print summary
        summary = results['summary']
        print(f"    Success rate: {summary['success_rate']:.1%}")
        print(f"    On-curve points: {sum(1 for r in results['points'] if r['on_curve'])}")
    
    # Advanced region analysis
    print("\\nAdvanced region analysis:")
    
    # Create focused grids for better resolution
    focused_X, focused_Y = grid_evaluator.create_focused_grid((0, 0), 3, 150)
    
    inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
        triangle_region, focused_X, focused_Y, test_boundary=True)
    
    stats = grid_evaluator.analyze_grid_statistics(inside_mask, boundary_mask)
    
    print(f"  High-resolution triangle analysis:")
    print(f"    Grid size: {focused_X.size} points")
    print(f"    Inside: {stats['inside_count']} points ({stats['inside_percentage']:.2f}%)")
    print(f"    Boundary: {stats['boundary_count']} points ({stats['boundary_percentage']:.2f}%)")
    print(f"    Boundary resolution: {stats['boundary_count']/stats['total_points']*100:.3f}%")
    
    print("✓ Advanced analysis demo completed")


def run_advanced_demo():
    """
    Run the complete advanced demonstration.
    """
    print("\\n" + "="*70)
    print("GEOMETRY LIBRARY - ADVANCED DEMONSTRATION")
    print("="*70)
    print("This demo showcases advanced features including trimmed curves,")
    print("composite curves, and sophisticated analysis techniques.")
    print()
    
    try:
        demo_trimmed_curves()
        print()
        demo_composite_curves()
        print()
        demo_complex_regions()
        print()
        demo_advanced_analysis()
        
        print("\\n" + "="*70)
        print("✓ ADVANCED DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\\nNext steps:")
        print("- Explore the comprehensive showcase for a complete overview")
        print("- Try individual test modules for specific functionality")
        print("- Create custom curves and regions using the factory classes")
        
    except Exception as e:
        print(f"\\n✗ ERROR in advanced demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_advanced_demo()
