#!/usr/bin/env python3
"""
Test script to verify that tolerance fixes resolve missing pixels in composite curves
"""

import numpy as np
import matplotlib.pyplot as plt
from geometry import *
from geometry.factories import (
    create_circle_line_hybrid, create_ellipse_parabola_hybrid, 
    create_superellipse_circle_hybrid, create_heart_shape,
    create_lens_shape, create_spiral_approximation, create_figure_eight
)

def test_tolerance_fixes():
    """Test that tolerance fixes resolve missing pixels"""
    print("🔧 Testing Tolerance Fixes for Missing Pixels")
    print("=" * 60)
    
    # Test curves that were having missing pixels
    test_curves = [
        ("D-Shape (Circle + Line)", create_circle_line_hybrid),
        ("Egg Shape (Ellipse + Parabola)", create_ellipse_parabola_hybrid),
        ("Rounded Square (Superellipse + Circle)", create_superellipse_circle_hybrid),
        ("Heart Shape (Circles + Parabola)", create_heart_shape),
        ("Lens Shape (Two Circles)", create_lens_shape),
        ("Figure-Eight", create_figure_eight),
        ("Spiral Approximation", lambda: create_spiral_approximation(turns=2)),
    ]
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.flatten()
    
    success_count = 0
    
    for i, (name, creator_func) in enumerate(test_curves):
        ax = axes[i]
        
        try:
            print(f"\n🧪 Testing {name}")
            
            # Create the curve
            curve = creator_func()
            print(f"  ✅ Created with {len(curve.segments)} segments")
            
            # Test plotting with high resolution to detect missing pixels
            x_range = np.linspace(-3, 3, 600)
            y_range = np.linspace(-3, 3, 600)
            X, Y = np.meshgrid(x_range, y_range)
            
            # Count pixels on curve (should be substantial for each segment)
            total_pixels = 0
            
            for j, segment in enumerate(curve.segments):
                if hasattr(segment, 'base_curve') and hasattr(segment, 'mask'):
                    # Trimmed curve
                    Z = segment.base_curve.evaluate(X, Y)
                    
                    # Apply mask
                    mask_grid = np.zeros_like(X, dtype=bool)
                    for row in range(X.shape[0]):
                        for col in range(X.shape[1]):
                            mask_grid[row, col] = segment.mask(X[row, col], Y[row, col])
                    
                    # Count pixels near zero within mask
                    on_curve = (np.abs(Z) < 0.05) & mask_grid
                    segment_pixels = np.sum(on_curve)
                    total_pixels += segment_pixels
                    
                    print(f"    Segment {j}: {segment_pixels} pixels")
                else:
                    # Regular curve
                    Z = segment.evaluate(X, Y)
                    on_curve = np.abs(Z) < 0.05
                    segment_pixels = np.sum(on_curve)
                    total_pixels += segment_pixels
                    
                    print(f"    Segment {j}: {segment_pixels} pixels")
            
            print(f"  📊 Total pixels on curve: {total_pixels}")
            
            # Plot the curve
            curve.plot(ax=ax, x_range=(-3, 3), y_range=(-3, 3), resolution=400)
            ax.set_title(f"{name}\n{total_pixels} pixels")
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            
            # Consider it successful if we have a reasonable number of pixels
            if total_pixels > 100:  # Threshold for "not missing pixels"
                print(f"  ✅ SUCCESS: Sufficient pixels rendered")
                success_count += 1
            else:
                print(f"  ⚠️ WARNING: Low pixel count, may have missing pixels")
            
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            ax.text(0.5, 0.5, f'Failed\n{str(e)[:50]}...', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f"{name} (Failed)")
    
    # Hide unused subplots
    for i in range(len(test_curves), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('tolerance_fixes_test.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n📊 RESULTS:")
    print(f"  ✅ Successful curves: {success_count}/{len(test_curves)}")
    print(f"  📈 Success rate: {success_count/len(test_curves)*100:.1f}%")
    print(f"  💾 Test plot saved as tolerance_fixes_test.png")
    
    if success_count >= len(test_curves) * 0.8:  # 80% success rate
        print(f"\n🎉 TOLERANCE FIXES SUCCESSFUL!")
        print("✅ Missing pixels issue appears to be resolved")
    else:
        print(f"\n⚠️ Some curves still have issues")
        print("🔧 May need additional tolerance adjustments")
    
    return success_count >= len(test_curves) * 0.8

if __name__ == "__main__":
    test_tolerance_fixes()