"""
Composite curve tests.

Visual tests for trimmed curves and composite curves made from multiple segments.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from typing import List, Tuple, Callable
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from geometry import ConicSection, TrimmedImplicitCurve, CompositeCurve
from visual_tests.utils import PlotManager, CurveFactory, GridEvaluator


def test_trimmed_curves():
    """
    Test and visualize trimmed curves with different mask functions.
    """
    print("="*60)
    print("Testing Trimmed Curves")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 3, figsize=(15, 10), 
                                         suptitle='Trimmed Curves')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Create base circle
    base_circle = CurveFactory.create_circle((0, 0), 2)
    
    # Define different trimming masks
    masks = [
        ("Upper Half", lambda px, py: py >= 0),
        ("Right Half", lambda px, py: px >= 0),
        ("First Quadrant", lambda px, py: px >= 0 and py >= 0),
        ("Upper Right Arc", lambda px, py: px >= 0 and py >= 0 and px**2 + py**2 <= 4.5),
        ("Ring Segment", lambda px, py: 1 <= px**2 + py**2 <= 4 and py >= 0),
        ("Custom Shape", lambda px, py: abs(px) + abs(py) <= 2)
    ]
    
    # Plot each trimmed curve
    for i, (name, mask_func) in enumerate(masks):
        ax = axes[i // 3, i % 3]
        
        print(f"Creating trimmed curve: {name}...")
        
        # Create trimmed curve
        trimmed_curve = TrimmedImplicitCurve(base_circle, mask_func)
        
        # Plot the base circle lightly
        plot_manager.plot_curve_contour(ax, base_circle, X, Y, 
                                       title="", color='lightgray', 
                                       show_levels=False, linewidth=1)
        
        # Plot points that satisfy the mask
        mask_points_x = []
        mask_points_y = []
        
        # Sample points around the circle and check mask
        angles = np.linspace(0, 2*np.pi, 200)
        for angle in angles:
            px = 2 * np.cos(angle)
            py = 2 * np.sin(angle)
            
            try:
                if mask_func(px, py):
                    mask_points_x.append(px)
                    mask_points_y.append(py)
            except:
                pass
        
        if mask_points_x:
            ax.plot(mask_points_x, mask_points_y, 'b-', linewidth=3, 
                   label='Trimmed Curve')
        
        ax.set_title(f"{name}\\nTrimmed Circle", fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.legend(fontsize=8)
    
    plot_manager.save_or_show()
    print("✓ Trimmed curves test completed")


def test_composite_curves():
    """
    Test and visualize composite curves made from multiple segments.
    """
    print("="*60)
    print("Testing Composite Curves")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(12, 12), 
                                         suptitle='Composite Curves')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Test 1: Circle quarters
    print("Creating composite curve from circle quarters...")
    ax = axes[0, 0]
    
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
    angles_ranges = [(0, np.pi/2), (np.pi, 3*np.pi/2)]
    
    for i, (start_angle, end_angle) in enumerate(angles_ranges):
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
    
    # Test 2: Mixed curve types
    print("Creating composite curve from mixed types...")
    ax = axes[0, 1]
    
    # Create a line segment and a circle arc
    line_curve = CurveFactory.create_line((-2, -1), (0, 1))
    circle_curve = CurveFactory.create_circle((0, 0), 1)
    
    # Create masks
    line_mask = lambda px, py: -2 <= px <= 0 and abs(line_curve.evaluate(px, py)) < 0.1
    arc_mask = lambda px, py: px >= 0 and py >= 0 and abs(circle_curve.evaluate(px, py)) < 0.1
    
    line_segment = TrimmedImplicitCurve(line_curve, line_mask)
    arc_segment = TrimmedImplicitCurve(circle_curve, arc_mask)
    
    mixed_composite = CompositeCurve([line_segment, arc_segment], (x, y))
    
    # Plot the segments
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
    
    # Test 3: Multiple segments
    print("Creating composite curve with multiple segments...")
    ax = axes[1, 0]
    
    circle_base = CurveFactory.create_circle((0, 0), 1.2)
    
    # Plot base circle lightly
    plot_manager.plot_curve_contour(ax, circle_base, X, Y, 
                                   title="", color='lightgray', 
                                   show_levels=False, linewidth=1)
    
    # Create three segments
    segment_masks = [
        lambda px, py: 0 <= np.arctan2(py, px) <= np.pi/3,  # 0 to 60 degrees
        lambda px, py: 2*np.pi/3 <= np.arctan2(py, px) <= np.pi,  # 120 to 180 degrees
        lambda px, py: -np.pi <= np.arctan2(py, px) <= -2*np.pi/3  # -180 to -120 degrees
    ]
    
    segments = []
    colors = ['red', 'green', 'blue']
    angle_ranges = [(0, np.pi/3), (2*np.pi/3, np.pi), (-np.pi, -2*np.pi/3)]
    
    for i, (mask_func, (start_angle, end_angle)) in enumerate(zip(segment_masks, angle_ranges)):
        segment = TrimmedImplicitCurve(circle_base, mask_func)
        segments.append(segment)
        
        # Plot the segment
        angles = np.linspace(start_angle, end_angle, 30)
        seg_x = 1.2 * np.cos(angles)
        seg_y = 1.2 * np.sin(angles)
        ax.plot(seg_x, seg_y, color=colors[i], linewidth=3, 
               label=f'Segment {i+1}')
    
    multi_composite = CompositeCurve(segments, (x, y))
    
    ax.set_title("Multi-Segment Composite\\n(3 Circle Arcs)")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.legend()
    
    # Test 4: Complex shape
    print("Creating complex composite shape...")
    ax = axes[1, 1]
    
    # Create a more complex shape combining different curves
    # Square corners connected by curves
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        
        # Create line segment
        line = CurveFactory.create_line(start, end)
        ax.plot([start[0], end[0]], [start[1], end[1]], 
               color='purple', linewidth=3, alpha=0.7,
               label='Square Edges' if i == 0 else '')
    
    # Add circular arcs at corners
    corner_radius = 0.3
    for i, (cx, cy) in enumerate(corners):
        circle = CurveFactory.create_circle((cx, cy), corner_radius)
        angles = np.linspace(0, 2*np.pi, 100)
        corner_x = cx + corner_radius * np.cos(angles)
        corner_y = cy + corner_radius * np.sin(angles)
        ax.plot(corner_x, corner_y, color='orange', linewidth=2, alpha=0.7,
               label='Corner Circles' if i == 0 else '')
    
    ax.set_title("Complex Composite\\n(Square + Corner Circles)")
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.legend()
    
    plot_manager.save_or_show()
    print("✓ Composite curves test completed")


def test_composite_curve_properties():
    """
    Test properties of composite curves.
    """
    print("="*60)
    print("Testing Composite Curve Properties")
    print("="*60)
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Create a simple composite curve
    circle_base = CurveFactory.create_circle((0, 0), 2)
    
    # Create two quarter segments
    quarter1_mask = lambda px, py: px >= 0 and py >= 0
    quarter3_mask = lambda px, py: px <= 0 and py <= 0
    
    quarter1 = TrimmedImplicitCurve(circle_base, quarter1_mask)
    quarter3 = TrimmedImplicitCurve(circle_base, quarter3_mask)
    
    composite = CompositeCurve([quarter1, quarter3], (x, y))
    
    print(f"Composite curve created with {len(composite.segments)} segments")
    
    # Test closure
    try:
        is_closed = composite.is_closed()
        print(f"Is closed: {is_closed}")
    except Exception as e:
        print(f"Closure test failed: {e}")
    
    # Test segment properties
    for i, segment in enumerate(composite.segments):
        print(f"\\nSegment {i+1}:")
        print(f"  Type: {type(segment).__name__}")
        print(f"  Base curve: {type(segment.base_curve).__name__}")
        
        # Test some points on the segment
        test_points = [(1.4, 1.4), (-1.4, -1.4), (0, 2), (2, 0)]
        
        for px, py in test_points:
            try:
                on_segment = segment.contains(px, py)
                print(f"  Point ({px}, {py}) on segment: {on_segment}")
            except Exception as e:
                print(f"  Point ({px}, {py}) test failed: {e}")
    
    print("\\n✓ Composite curve properties test completed")


def run_all_composite_curve_tests():
    """
    Run all composite curve tests.
    """
    print("\\n" + "="*80)
    print("RUNNING ALL COMPOSITE CURVE TESTS")
    print("="*80)
    
    try:
        test_trimmed_curves()
        print()
        test_composite_curves()
        print()
        test_composite_curve_properties()
        
        print("\\n" + "="*80)
        print("✓ ALL COMPOSITE CURVE TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\\n✗ ERROR in composite curve tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_composite_curve_tests()
