#!/usr/bin/env python3
"""
Test CompositeCurve continuity requirements
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *

def test_composite_continuity():
    """Test that CompositeCurve enforces continuity as documented"""
    
    print("🔗 COMPOSITE CURVE CONTINUITY TESTING")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Test 1: Valid continuous triangle
    print("\n✅ Test 1: Valid Continuous Triangle")
    print("-" * 40)
    
    try:
        # Triangle with properly connected segments
        # Vertices: (0, 1), (-1, -1), (1, -1)
        
        # Segment 1: Left edge from (-1, -1) to (0, 1)
        # Line: 2x - y + 1 = 0
        left_line = PolynomialCurve(2*x - y + 1, (x, y))
        left_mask = lambda x_val, y_val: (-1 <= x_val <= 0) and (-1 <= y_val <= 1)
        left_segment = TrimmedImplicitCurve(left_line, left_mask, 
                                          endpoints=[(-1, -1), (0, 1)])
        
        # Segment 2: Right edge from (0, 1) to (1, -1)  
        # Line: -2x - y + 1 = 0
        right_line = PolynomialCurve(-2*x - y + 1, (x, y))
        right_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-1 <= y_val <= 1)
        right_segment = TrimmedImplicitCurve(right_line, right_mask,
                                           endpoints=[(0, 1), (1, -1)])
        
        # Segment 3: Bottom edge from (1, -1) to (-1, -1)
        # Line: y + 1 = 0
        bottom_line = PolynomialCurve(y + 1, (x, y))
        bottom_mask = lambda x_val, y_val: (-1 <= x_val <= 1) and (-1.1 <= y_val <= -0.9)
        bottom_segment = TrimmedImplicitCurve(bottom_line, bottom_mask,
                                            endpoints=[(1, -1), (-1, -1)])
        
        triangle = CompositeCurve([left_segment, right_segment, bottom_segment])
        
        print(f"  Triangle created successfully")
        print(f"  Is closed: {triangle.is_closed()}")
        
        # Test connectivity
        for i, segment in enumerate(triangle.segments):
            endpoints = segment.get_endpoints()
            print(f"  Segment {i+1} endpoints: {endpoints}")
        
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 2: Invalid discontinuous segments (should fail or warn)
    print("\n❌ Test 2: Invalid Discontinuous Segments")
    print("-" * 40)
    
    try:
        # Create disconnected segments that shouldn't form a valid composite
        
        # Segment 1: Line at y = 0, x from -1 to 0
        seg1_line = PolynomialCurve(y, (x, y))
        seg1_mask = lambda x_val, y_val: (-1 <= x_val <= 0) and (-0.1 <= y_val <= 0.1)
        seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(-1, 0), (0, 0)])
        
        # Segment 2: Line at y = 1, x from 0.5 to 1.5 (GAP from segment 1!)
        seg2_line = PolynomialCurve(y - 1, (x, y))
        seg2_mask = lambda x_val, y_val: (0.5 <= x_val <= 1.5) and (0.9 <= y_val <= 1.1)
        seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(0.5, 1), (1.5, 1)])
        
        # This should either fail or issue a warning about discontinuity
        discontinuous = CompositeCurve([seg1, seg2])
        
        print(f"  Discontinuous curve created (this might be wrong!)")
        print(f"  Is closed: {discontinuous.is_closed()}")
        
        # Check if there's a gap
        seg1_end = seg1.get_endpoints()[1]  # (0, 0)
        seg2_start = seg2.get_endpoints()[0]  # (0.5, 1)
        gap_distance = np.sqrt((seg2_start[0] - seg1_end[0])**2 + (seg2_start[1] - seg1_end[1])**2)
        print(f"  Gap between segments: {gap_distance:.3f} (should be ~0 for continuity)")
        
    except Exception as e:
        print(f"  Good! CompositeCurve rejected discontinuous segments: {e}")
    
    # Test 3: Check existing composite shapes for continuity
    print("\n🔍 Test 3: Check Existing Composite Shapes")
    print("-" * 40)
    
    test_shapes = [
        ("Square", lambda: create_square_from_edges((-1, -1), (1, 1))),
        ("Circle Quarters", lambda: create_circle_from_quarters(center=(0, 0), radius=1.0)),
    ]
    
    for name, creator in test_shapes:
        try:
            shape = creator()
            print(f"\n  {name}:")
            print(f"    Segments: {len(shape.segments)}")
            print(f"    Is closed: {shape.is_closed()}")
            
            # Check endpoint connectivity
            gaps = []
            for i in range(len(shape.segments)):
                current_seg = shape.segments[i]
                next_seg = shape.segments[(i + 1) % len(shape.segments)]
                
                curr_endpoints = current_seg.get_endpoints()
                next_endpoints = next_seg.get_endpoints()
                
                if curr_endpoints and next_endpoints:
                    # Find minimum distance between any endpoint of current and any of next
                    min_gap = float('inf')
                    for curr_end in curr_endpoints:
                        for next_end in next_endpoints:
                            gap = np.sqrt((curr_end[0] - next_end[0])**2 + (curr_end[1] - next_end[1])**2)
                            min_gap = min(min_gap, gap)
                    gaps.append(min_gap)
                    print(f"    Gap {i}->{(i+1)%len(shape.segments)}: {min_gap:.6f}")
            
            max_gap = max(gaps) if gaps else float('inf')
            is_continuous = max_gap < 0.1  # Tolerance for continuity
            print(f"    Continuous: {is_continuous} (max gap: {max_gap:.6f})")
            
        except Exception as e:
            print(f"  ERROR testing {name}: {e}")
    
    # Visualization
    print(f"\n🎨 Creating continuity test visualization...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('CompositeCurve Continuity Testing', fontsize=16, fontweight='bold')
    
    # Plot the triangle (should be continuous)
    ax1 = axes[0]
    if 'triangle' in locals():
        X = np.linspace(-2, 2, 200)
        Y = np.linspace(-2, 2, 200)
        XX, YY = np.meshgrid(X, Y)
        
        colors = ['red', 'green', 'blue']
        for i, segment in enumerate(triangle.segments):
            Z_base = segment.base_curve.evaluate(XX, YY)
            
            # Apply mask
            mask_grid = np.zeros_like(XX, dtype=bool)
            for row in range(XX.shape[0]):
                for col in range(XX.shape[1]):
                    mask_grid[row, col] = segment.mask(XX[row, col], YY[row, col])
            
            Z_masked = np.where(mask_grid, Z_base, np.nan)
            ax1.contour(XX, YY, Z_masked, levels=[0], colors=[colors[i]], linewidths=3)
            
            # Mark endpoints
            endpoints = segment.get_endpoints()
            for ep in endpoints:
                ax1.plot(ep[0], ep[1], 'o', color=colors[i], markersize=8, markeredgecolor='black')
        
        ax1.set_title('Continuous Triangle\n(endpoints should connect)')
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-1.5, 1.5)
        ax1.set_ylim(-1.5, 1.5)
    
    # Plot a square for comparison
    ax2 = axes[1]
    try:
        square = create_square_from_edges((-1, -1), (1, 1))
        
        colors = ['red', 'green', 'blue', 'orange']
        for i, segment in enumerate(square.segments):
            Z_base = segment.base_curve.evaluate(XX, YY)
            
            # Apply mask (if segment has one)
            if hasattr(segment, 'mask'):
                mask_grid = np.zeros_like(XX, dtype=bool)
                for row in range(XX.shape[0]):
                    for col in range(XX.shape[1]):
                        mask_grid[row, col] = segment.mask(XX[row, col], YY[row, col])
                Z_masked = np.where(mask_grid, Z_base, np.nan)
            else:
                Z_masked = Z_base
            
            ax2.contour(XX, YY, Z_masked, levels=[0], colors=[colors[i % len(colors)]], linewidths=3)
        
        ax2.set_title('Square from Edges\n(should be continuous)')
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        
    except Exception as e:
        ax2.text(0.5, 0.5, f'Error plotting square: {e}', 
                ha='center', va='center', transform=ax2.transAxes)
    
    plt.tight_layout()
    plt.savefig('composite_continuity_test.png', dpi=300, bbox_inches='tight')
    print("  📁 Visualization saved as: composite_continuity_test.png")
    
    print(f"\n📋 SUMMARY:")
    print("CompositeCurve should enforce continuity but currently doesn't.")
    print("Need to:")
    print("1. Add continuity validation in CompositeCurve.__init__()")
    print("2. Fix existing composite shape creators to ensure continuity")
    print("3. Add proper endpoint management for TrimmedImplicitCurve")

if __name__ == "__main__":
    test_composite_continuity()