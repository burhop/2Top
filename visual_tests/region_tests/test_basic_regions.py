"""
Basic region tests.

Visual tests for fundamental area regions: circles, triangles, rectangles,
and basic containment testing.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from typing import List, Tuple
import sys
import os

# Configure matplotlib for better performance and display
plt.ion()  # Turn on interactive mode
try:
    plt.switch_backend('TkAgg')  # Use TkAgg backend for better Windows compatibility
except:
    pass  # Fall back to default backend

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from geometry import AreaRegion
from visual_tests.utils import PlotManager, RegionFactory, GridEvaluator


def test_basic_area_regions():
    """
    Test and visualize basic area regions: circle, triangle, rectangle.
    """
    print("="*60)
    print("Testing Basic Area Regions")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator(default_grid_size=60)  # Reduced grid size for performance
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(1, 3, figsize=(15, 5), 
                                         suptitle='Basic Area Regions')
    
    # Create test grid (smaller for better performance)
    X, Y = grid_evaluator.create_grid(grid_size=60)
    
    # Create test regions
    regions = [
        ("Circle", RegionFactory.create_circle_region((0, 0), 2)),
        ("Triangle", RegionFactory.create_triangle_region([(-2, -1.5), (2, -1.5), (0, 2)])),
        ("Rectangle", RegionFactory.create_rectangle_region((-1.5, -1), (1.5, 1)))
    ]
    
    colors = ['lightblue', 'lightgreen', 'lightyellow']
    
    # Plot each region
    for i, (name, region) in enumerate(regions):
        ax = axes[i]
        color = colors[i]
        
        print(f"Plotting {name} region...")
        plot_manager.plot_region_filled(ax, region, X, Y, 
                                       title=f"{name} Region", 
                                       fill_color=color, 
                                       boundary_color='red',
                                       point_size=2)  # Larger points for visibility
    
    plot_manager.save_or_show()
    print("✓ Basic area regions test completed")


def test_region_containment():
    """
    Test region containment with specific points.
    """
    print("="*60)
    print("Testing Region Containment")
    print("="*60)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator()
    
    # Create test regions
    circle_region = RegionFactory.create_circle_region((0, 0), 2)
    triangle_region = RegionFactory.create_triangle_region([(-2, -1), (2, -1), (0, 2)])
    
    # Define comprehensive test points
    test_points = [
        # Interior points
        (0, 0, "Center"),
        (1, 0, "Right interior"),
        (-1, 0, "Left interior"),
        (0, 1, "Top interior"),
        (0, -1, "Bottom interior"),
        
        # Boundary points (approximate)
        (2, 0, "Right boundary"),
        (-2, 0, "Left boundary"),
        (0, 2, "Top boundary"),
        (0, -2, "Bottom boundary"),
        
        # Exterior points
        (3, 0, "Right exterior"),
        (-3, 0, "Left exterior"),
        (0, 3, "Top exterior"),
        (0, -3, "Bottom exterior"),
        (2.5, 2.5, "Diagonal exterior")
    ]
    
    # Test each region
    regions = [
        ("Circle (radius 2)", circle_region),
        ("Triangle", triangle_region)
    ]
    
    for region_name, region in regions:
        print(f"\\nTesting {region_name}:")
        results = grid_evaluator.test_specific_points(region, test_points, 'region')
        grid_evaluator.print_test_results(results)
    
    print("\\n✓ Region containment test completed")


def test_region_statistics():
    """
    Test and analyze region statistics over grids.
    """
    print("="*60)
    print("Testing Region Statistics")
    print("="*60)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator(default_grid_size=50)  # Smaller grid for statistics
    
    # Create test regions with different sizes
    regions = [
        ("Small Circle", RegionFactory.create_circle_region((0, 0), 1)),
        ("Medium Circle", RegionFactory.create_circle_region((0, 0), 2)),
        ("Large Circle", RegionFactory.create_circle_region((0, 0), 2.5)),
        ("Triangle", RegionFactory.create_triangle_region([(-2, -2), (2, -2), (0, 2)])),
        ("Small Rectangle", RegionFactory.create_rectangle_region((-1, -1), (1, 1))),
        ("Large Rectangle", RegionFactory.create_rectangle_region((-2.5, -1.5), (2.5, 1.5)))
    ]
    
    # Test each region with smaller grid
    X, Y = grid_evaluator.create_grid(grid_size=50)
    
    for i, (name, region) in enumerate(regions):
        print(f"\nAnalyzing {name} ({i+1}/{len(regions)}):")
        
        # Evaluate containment with progress indication
        print(f"  Evaluating {X.size} grid points...")
        inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
            region, X, Y, test_boundary=True)
        
        # Analyze statistics
        stats = grid_evaluator.analyze_grid_statistics(inside_mask, boundary_mask)
        grid_evaluator.print_grid_statistics(stats)
        
        # Calculate theoretical area for comparison (where possible)
        if "Circle" in name:
            radius_str = name.split()[-1] if name.split()[-1].replace('.', '').isdigit() else "2"
            try:
                radius = float(radius_str)
                theoretical_area = np.pi * radius**2
                grid_area = (6**2) * stats['inside_count'] / stats['total_points']  # Grid covers 6x6 area
                print(f"  Theoretical area: {theoretical_area:.2f}")
                print(f"  Estimated area: {grid_area:.2f}")
                print(f"  Area ratio: {grid_area/theoretical_area:.2f}")
            except:
                pass
    
    print("\\n✓ Region statistics test completed")


def test_region_boundaries():
    """
    Test region boundary detection and visualization.
    """
    print("="*60)
    print("Testing Region Boundaries")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator(default_grid_size=80)  # Balanced resolution
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(12, 12), 
                                         suptitle='Region Boundary Detection')
    
    # Create focused grids with moderate resolution for performance
    regions_and_grids = [
        ("Circle", RegionFactory.create_circle_region((0, 0), 1.5), 
         grid_evaluator.create_focused_grid((0, 0), 2.5, 80)),
        ("Triangle", RegionFactory.create_triangle_region([(-1.5, -1), (1.5, -1), (0, 1.5)]), 
         grid_evaluator.create_focused_grid((0, 0), 2.5, 80)),
        ("Rectangle", RegionFactory.create_rectangle_region((-1, -0.8), (1, 0.8)), 
         grid_evaluator.create_focused_grid((0, 0), 2, 80)),
        ("Small Circle", RegionFactory.create_circle_region((0, 0), 0.8), 
         grid_evaluator.create_focused_grid((0, 0), 1.5, 80))
    ]
    
    # Plot each region with boundary emphasis
    for i, (name, region, (X, Y)) in enumerate(regions_and_grids):
        ax = axes[i // 2, i % 2]
        
        print(f"Analyzing boundaries for {name} ({i+1}/{len(regions_and_grids)})...")
        print(f"  Processing {X.size} points...")
        
        # Evaluate containment
        inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
            region, X, Y, test_boundary=True)
        
        # Plot with emphasis on boundaries
        inside_points = np.where(inside_mask)
        boundary_points = np.where(boundary_mask)
        
        if len(inside_points[0]) > 0:
            ax.scatter(X[inside_points], Y[inside_points], 
                      c='lightblue', s=0.5, alpha=0.4, label='Inside')
        
        if len(boundary_points[0]) > 0:
            ax.scatter(X[boundary_points], Y[boundary_points], 
                      c='red', s=2, alpha=0.9, label='Boundary')
        
        ax.set_title(f"{name}\\nBoundary Detection")
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        
        # Print boundary statistics
        boundary_count = len(boundary_points[0])
        total_points = X.size
        print(f"  Boundary points: {boundary_count}/{total_points} ({100*boundary_count/total_points:.2f}%)")
    
    plot_manager.save_or_show()
    print("✓ Region boundaries test completed")


def test_region_comparison():
    """
    Compare different regions side by side.
    """
    print("="*60)
    print("Testing Region Comparison")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator(default_grid_size=60)  # Moderate resolution
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 3, figsize=(15, 10), 
                                         suptitle='Region Comparison')
    
    # Create test grid with moderate resolution
    X, Y = grid_evaluator.create_grid(grid_size=60)
    
    # Create regions with similar "sizes" for comparison
    regions = [
        ("Circle r=1.5", RegionFactory.create_circle_region((0, 0), 1.5)),
        ("Square 2×2", RegionFactory.create_rectangle_region((-1, -1), (1, 1))),
        ("Triangle", RegionFactory.create_triangle_region([(-1.7, -1.2), (1.7, -1.2), (0, 1.8)])),
        ("Circle r=2", RegionFactory.create_circle_region((0, 0), 2)),
        ("Rectangle 3×2", RegionFactory.create_rectangle_region((-1.5, -1), (1.5, 1))),
        ("Tall Triangle", RegionFactory.create_triangle_region([(-1, -2), (1, -2), (0, 2)]))
    ]
    
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'lightpink', 'lightgray']
    
    # Plot each region and collect statistics
    region_stats = []
    
    for i, (name, region) in enumerate(regions):
        ax = axes[i // 3, i % 3]
        color = colors[i]
        
        print(f"Analyzing {name} ({i+1}/{len(regions)})...")
        
        # Evaluate containment
        inside_mask, boundary_mask = grid_evaluator.evaluate_region_containment(
            region, X, Y, test_boundary=True)
        
        # Plot region
        plot_manager.plot_region_filled(ax, region, X, Y, 
                                       title=name, 
                                       fill_color=color, 
                                       boundary_color='red',
                                       point_size=0.8)
        
        # Collect statistics
        stats = grid_evaluator.analyze_grid_statistics(inside_mask, boundary_mask)
        region_stats.append((name, stats))
    
    plot_manager.save_or_show()
    
    # Print comparison table
    print(f"\\n{'='*80}")
    print("REGION COMPARISON TABLE")
    print(f"{'='*80}")
    print(f"{'Region':<20} {'Inside%':<10} {'Boundary%':<12} {'Outside%':<10} {'Area Est.':<10}")
    print(f"{'-'*80}")
    
    for name, stats in region_stats:
        area_est = (6**2) * stats['inside_count'] / stats['total_points']  # Grid covers 6x6
        print(f"{name:<20} {stats['inside_percentage']:<10.1f} "
              f"{stats['boundary_percentage']:<12.1f} {stats['outside_percentage']:<10.1f} "
              f"{area_est:<10.2f}")
    
    print("\\n✓ Region comparison test completed")


def run_all_basic_region_tests():
    """
    Run all basic region tests.
    """
    print("\\n" + "="*80)
    print("RUNNING ALL BASIC REGION TESTS")
    print("="*80)
    
    try:
        test_basic_area_regions()
        print()
        test_region_containment()
        print()
        test_region_statistics()
        print()
        test_region_boundaries()
        print()
        test_region_comparison()
        
        print("\\n" + "="*80)
        print("✓ ALL BASIC REGION TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\\n✗ ERROR in basic region tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_basic_region_tests()
