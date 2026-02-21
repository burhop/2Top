#!/usr/bin/env python3
"""
Test square creation specifically in the context of the visualizer
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.factories import create_square_from_edges

def test_square_in_visualizer_context():
    """Test square creation as it would be used in the visualizer"""
    print("🔍 Testing Square in Visualizer Context")
    
    # Test the exact same square creation as in the visualizer
    try:
        square = create_square_from_edges((-0.8, -0.8), (0.8, 0.8))
        print(f"✅ Square created with {len(square.segments)} segments")
        
        # Test the square's properties
        print(f"Square is closed: {square.is_closed()}")
        print(f"Square type: {type(square).__name__}")
        
        # Check if it has the special square metadata
        print(f"Has _is_square: {hasattr(square, '_is_square')}")
        if hasattr(square, '_is_square'):
            print(f"_is_square: {square._is_square}")
        if hasattr(square, '_square_bounds'):
            print(f"_square_bounds: {square._square_bounds}")
        
        # Test evaluation at key points
        test_points = [
            (0, 0),      # Center
            (0.8, 0),    # Right edge
            (0, 0.8),    # Top edge
            (-0.8, 0),   # Left edge
            (0, -0.8),   # Bottom edge
            (1, 1),      # Outside
        ]
        
        print("\nTesting square evaluation:")
        for px, py in test_points:
            val = square.evaluate(px, py)
            contains_boundary = square.contains(px, py, tolerance=0.1)
            contains_region = square.contains(px, py, tolerance=0.1, region_containment=True)
            print(f"  Point ({px:4.1f}, {py:4.1f}): eval={val:6.3f}, boundary={contains_boundary}, region={contains_region}")
        
        # Test plotting with the same parameters as the visualizer
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot the square using the same method as the visualizer
        contour_sets = square.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2), resolution=1000)
        
        # Mark test points
        for i, (px, py) in enumerate(test_points):
            contains_region = square.contains(px, py, tolerance=0.1, region_containment=True)
            color = 'green' if contains_region else 'red'
            marker = 'o' if contains_region else 'x'
            ax.plot(px, py, color=color, marker=marker, markersize=8)
            ax.annotate(f'P{i+1}', (px, py), xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('Square in Visualizer Context')
        
        plt.savefig('test_square_visualizer.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✅ Square visualizer test plot saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Square creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_square_segments_individually():
    """Test each square segment individually"""
    print("\n🔍 Testing Square Segments Individually")
    
    square = create_square_from_edges((-0.8, -0.8), (0.8, 0.8))
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()
    
    segment_names = ['Bottom', 'Right', 'Top', 'Left']
    
    for i, (segment, name) in enumerate(zip(square.segments, segment_names)):
        ax = axes[i]
        
        print(f"\nSegment {i} ({name}):")
        print(f"  Expression: {segment.expression}")
        print(f"  Endpoints: {getattr(segment, 'endpoints', 'Not set')}")
        
        # Test segment plotting
        try:
            cs = segment.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2))
            print(f"  Plotting: Success")
        except Exception as e:
            print(f"  Plotting: Failed - {e}")
        
        # Test a few points on this segment
        if i == 0:  # Bottom
            test_points = [(-0.8, -0.8), (0, -0.8), (0.8, -0.8)]
        elif i == 1:  # Right
            test_points = [(0.8, -0.8), (0.8, 0), (0.8, 0.8)]
        elif i == 2:  # Top
            test_points = [(0.8, 0.8), (0, 0.8), (-0.8, 0.8)]
        else:  # Left
            test_points = [(-0.8, 0.8), (-0.8, 0), (-0.8, -0.8)]
        
        for px, py in test_points:
            contains = segment.contains(px, py, tolerance=0.1)
            eval_val = segment.evaluate(px, py)
            mask_val = segment.mask(px, py)
            print(f"    Point ({px:4.1f}, {py:4.1f}): contains={contains}, eval={eval_val:6.3f}, mask={mask_val}")
            
            # Mark the point on the plot
            color = 'green' if contains else 'red'
            marker = 'o' if contains else 'x'
            ax.plot(px, py, color=color, marker=marker, markersize=8)
        
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'{name} Segment')
    
    plt.tight_layout()
    plt.savefig('test_square_segments.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("✅ Square segments test plot saved")

def test_square_composite_plotting():
    """Test the composite curve plotting method specifically"""
    print("\n🔍 Testing Square Composite Plotting Method")
    
    square = create_square_from_edges((-0.8, -0.8), (0.8, 0.8))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Manually call the composite curve plot method
    print("Calling square.plot()...")
    try:
        contour_sets = square.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2), resolution=1000)
        print(f"Plot returned {len(contour_sets) if contour_sets else 0} contour sets")
        
        if contour_sets:
            for i, cs in enumerate(contour_sets):
                print(f"  Contour set {i}: {type(cs)}")
        
    except Exception as e:
        print(f"Plotting failed: {e}")
        import traceback
        traceback.print_exc()
    
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('Square Composite Plotting Test')
    
    plt.savefig('test_square_composite_plot.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("✅ Square composite plotting test saved")

if __name__ == "__main__":
    print("🧪 TESTING SQUARE IN VISUALIZER CONTEXT")
    print("=" * 60)
    
    success = test_square_in_visualizer_context()
    test_square_segments_individually()
    test_square_composite_plotting()
    
    if success:
        print(f"\n✅ Square testing completed - check PNG files for results")
    else:
        print(f"\n❌ Square testing failed")