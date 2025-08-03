"""
Basic demonstration of the geometry library.

Simple introduction to creating and visualizing curves and regions
using the visual testing utilities.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from visual_tests.utils import PlotManager, CurveFactory, RegionFactory, GridEvaluator


def demo_basic_curves():
    """
    Demonstrate basic curve creation and visualization.
    """
    print("="*50)
    print("BASIC CURVES DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(1, 3, figsize=(15, 5), 
                                         suptitle='Basic Curves Demo')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    print("Creating basic curves...")
    
    # Create curves
    circle = CurveFactory.create_circle((0, 0), 2)
    line = CurveFactory.create_line((-2, -1), (2, 1))
    parabola = CurveFactory.create_parabola((0, 0), 'up', 0.5)
    
    curves = [
        ("Circle", circle, "A circle with center (0,0) and radius 2"),
        ("Line", line, "A line from (-2,-1) to (2,1)"),
        ("Parabola", parabola, "An upward-opening parabola")
    ]
    
    # Plot each curve
    colors = ['blue', 'green', 'red']
    
    for i, (name, curve, description) in enumerate(curves):
        ax = axes[i]
        color = colors[i]
        
        print(f"  Plotting {name}: {description}")
        
        plot_manager.plot_curve_contour(ax, curve, X, Y, 
                                       title=f"{name}\\n{description}", 
                                       color=color, show_levels=True)
    
    plot_manager.save_or_show()
    print("✓ Basic curves demo completed")


def demo_basic_regions():
    """
    Demonstrate basic region creation and visualization.
    """
    print("="*50)
    print("BASIC REGIONS DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(1, 3, figsize=(15, 5), 
                                         suptitle='Basic Regions Demo')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    print("Creating basic regions...")
    
    # Create regions
    circle_region = RegionFactory.create_circle_region((0, 0), 2)
    triangle_region = RegionFactory.create_triangle_region([(-2, -1), (2, -1), (0, 2)])
    rectangle_region = RegionFactory.create_rectangle_region((-1.5, -1), (1.5, 1))
    
    regions = [
        ("Circle Region", circle_region, "lightblue", "A filled circular area"),
        ("Triangle Region", triangle_region, "lightgreen", "A filled triangular area"),
        ("Rectangle Region", rectangle_region, "lightyellow", "A filled rectangular area")
    ]
    
    # Plot each region
    for i, (name, region, color, description) in enumerate(regions):
        ax = axes[i]
        
        print(f"  Plotting {name}: {description}")
        
        plot_manager.plot_region_filled(ax, region, X, Y, 
                                       title=f"{name}\\n{description}", 
                                       fill_color=color, point_size=1)
    
    plot_manager.save_or_show()
    print("✓ Basic regions demo completed")


def demo_containment_testing():
    """
    Demonstrate containment testing with specific points.
    """
    print("="*50)
    print("CONTAINMENT TESTING DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator()
    
    print("Creating test objects...")
    
    # Create test objects
    circle = CurveFactory.create_circle((0, 0), 2)
    circle_region = RegionFactory.create_circle_region((0, 0), 2)
    
    # Define test points
    test_points = [
        (0, 0, "Center"),
        (1, 0, "Inside"),
        (2, 0, "On boundary"),
        (3, 0, "Outside"),
        (1.4, 1.4, "Near boundary")
    ]
    
    # Test curve evaluation
    print("\\nTesting curve evaluation:")
    curve_results = grid_evaluator.test_specific_points(circle, test_points, 'curve')
    grid_evaluator.print_test_results(curve_results)
    
    # Test region containment
    print("\\nTesting region containment:")
    region_results = grid_evaluator.test_specific_points(circle_region, test_points, 'region')
    grid_evaluator.print_test_results(region_results)
    
    print("✓ Containment testing demo completed")


def demo_grid_statistics():
    """
    Demonstrate grid-based statistical analysis.
    """
    print("="*50)
    print("GRID STATISTICS DEMONSTRATION")
    print("="*50)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator()
    
    print("Analyzing different region sizes...")
    
    # Create regions of different sizes
    regions = [
        ("Small Circle", RegionFactory.create_circle_region((0, 0), 1)),
        ("Medium Circle", RegionFactory.create_circle_region((0, 0), 2)),
        ("Large Circle", RegionFactory.create_circle_region((0, 0), 2.5)),
        ("Triangle", RegionFactory.create_triangle_region([(-2, -2), (2, -2), (0, 2)]))
    ]
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Analyze each region
    for name, region in regions:
        print(f"\\nAnalyzing {name}:")
        
        # Evaluate containment
        inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
            region, X, Y, test_boundary=True)
        
        # Get and print statistics
        stats = grid_evaluator.analyze_grid_statistics(inside_mask, boundary_mask)
        grid_evaluator.print_grid_statistics(stats)
    
    print("\\n✓ Grid statistics demo completed")


def run_basic_demo():
    """
    Run the complete basic demonstration.
    """
    print("\\n" + "="*70)
    print("GEOMETRY LIBRARY - BASIC DEMONSTRATION")
    print("="*70)
    print("This demo shows the fundamental capabilities of the geometry library")
    print("and visual testing utilities.")
    print()
    
    try:
        demo_basic_curves()
        print()
        demo_basic_regions()
        print()
        demo_containment_testing()
        print()
        demo_grid_statistics()
        
        print("\\n" + "="*70)
        print("✓ BASIC DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\\nNext steps:")
        print("- Try the advanced demo for more complex features")
        print("- Explore individual test modules for specific functionality")
        print("- Run the comprehensive showcase for a complete overview")
        
    except Exception as e:
        print(f"\\n✗ ERROR in basic demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_basic_demo()
