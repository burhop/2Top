#!/usr/bin/env python3
"""
Diagnose the real problem with composite curves
"""

import numpy as np
import matplotlib.pyplot as plt
from geometry.factories import create_heart_shape, create_ellipse_parabola_hybrid

def diagnose_plotting_issue():
    """Diagnose why shapes aren't plotting correctly"""
    print("🔍 DIAGNOSING REAL PLOTTING ISSUE")
    print("=" * 50)
    
    # Test the heart shape that should be working
    heart = create_heart_shape()
    
    print(f"Heart has {len(heart.segments)} segments")
    
    # Create a plotting grid
    x_range = np.linspace(-2, 2, 100)
    y_range = np.linspace(-2, 2, 100)
    X, Y = np.meshgrid(x_range, y_range)
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    # Test each segment individually
    for i, segment in enumerate(heart.segments):
        ax = axes[i]
        
        print(f"\nSegment {i}:")
        print(f"  Type: {type(segment).__name__}")
        
        if hasattr(segment, 'base_curve'):
            print(f"  Base curve: {segment.base_curve.expression}")
            
            # Evaluate base curve
            Z_base = segment.base_curve.evaluate(X, Y)
            ax.contour(X, Y, Z_base, levels=[0], colors=['blue'], linewidths=2)
            ax.set_title(f'Segment {i} - Base Curve')
            
            # Test mask at a few points
            print(f"  Testing mask:")
            test_points = [(-1, 0), (0, 0.25), (1, 0), (0, -1)]
            for px, py in test_points:
                mask_result = segment.mask(px, py)
                base_val = segment.base_curve.evaluate(px, py)
                print(f"    Point ({px}, {py}): mask={mask_result}, base_val={base_val:.3f}")
        
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    # Test the composite curve as a whole
    ax = axes[3]
    
    # Try to plot the composite
    try:
        heart.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2))
        ax.set_title('Composite Heart')
    except Exception as e:
        print(f"Composite plotting failed: {e}")
        ax.text(0.5, 0.5, f'Plot Failed\n{str(e)}', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Composite Failed')
    
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('diagnose_plotting.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n💾 Diagnostic plot saved as diagnose_plotting.png")

def test_mask_functions():
    """Test if mask functions are working correctly"""
    print("\n🎭 TESTING MASK FUNCTIONS")
    print("=" * 30)
    
    heart = create_heart_shape()
    
    # Test points that should be on each segment
    test_cases = [
        # Segment 0 (left circle): should include (-1, 0.25) and (0, 0.25)
        (0, [(-1, 0.25), (-0.5, 0.75), (0, 0.25)]),
        # Segment 1 (right circle): should include (0, 0.25) and (1, 0.25)  
        (1, [(0, 0.25), (0.5, 0.75), (1, 0.25)]),
        # Segment 2 (parabola): should include (1, 0), (0, -1), (-1, 0)
        (2, [(1, 0), (0, -1), (-1, 0)]),
    ]
    
    for seg_idx, test_points in test_cases:
        segment = heart.segments[seg_idx]
        print(f"\nSegment {seg_idx}:")
        
        for px, py in test_points:
            mask_result = segment.mask(px, py)
            
            if hasattr(segment, 'base_curve'):
                base_val = segment.base_curve.evaluate(px, py)
                segment_val = segment.evaluate(px, py)
                
                print(f"  Point ({px:4.1f}, {py:4.1f}): mask={mask_result:5}, base={base_val:6.3f}, segment={segment_val:6.3f}")
            else:
                segment_val = segment.evaluate(px, py)
                print(f"  Point ({px:4.1f}, {py:4.1f}): mask={mask_result:5}, segment={segment_val:6.3f}")

if __name__ == "__main__":
    diagnose_plotting_issue()
    test_mask_functions()