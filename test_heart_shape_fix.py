#!/usr/bin/env python3
"""
Test the heart shape tolerance fix
"""

import numpy as np
import matplotlib.pyplot as plt
from geometry.factories import create_heart_shape

def test_heart_shape():
    """Test the fixed heart shape"""
    print("💖 Testing Heart Shape Fix")
    
    try:
        # Create heart shape
        heart = create_heart_shape()
        print(f"✅ Heart created with {len(heart.segments)} segments")
        
        # Test plotting with high resolution
        fig, ax = plt.subplots(figsize=(10, 8))
        
        x_range = np.linspace(-2, 2, 600)
        y_range = np.linspace(-2, 2, 600)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Count pixels for each segment
        total_pixels = 0
        
        for i, segment in enumerate(heart.segments):
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
                
                print(f"  Segment {i}: {segment_pixels} pixels")
        
        print(f"📊 Total pixels on heart: {total_pixels}")
        
        # Plot the heart
        heart.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2), resolution=400)
        ax.set_title(f'Heart Shape (Fixed)\n{total_pixels} pixels total')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.savefig('heart_shape_fix_test.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        if total_pixels > 1000:  # Should have plenty of pixels
            print("✅ SUCCESS: Heart shape has sufficient pixels")
            return True
        else:
            print("⚠️ WARNING: Heart shape may still have missing pixels")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_heart_shape()
    if success:
        print("\n🎉 Heart shape fix successful!")
    else:
        print("\n💔 Heart shape still needs work")