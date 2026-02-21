#!/usr/bin/env python3
"""
Test heart shape endpoint matching
"""

import numpy as np
from geometry.factories import create_heart_shape

def test_heart_endpoints():
    """Test heart shape endpoint calculations"""
    print("💖 Testing Heart Shape Endpoints")
    
    try:
        heart = create_heart_shape()
        print(f"Heart created with {len(heart.segments)} segments")
        
        # Check each segment's endpoints and curve evaluation
        for i, segment in enumerate(heart.segments):
            print(f"\nSegment {i}:")
            
            if hasattr(segment, 'base_curve'):
                print(f"  Base curve: {segment.base_curve.expression}")
            
            if hasattr(segment, 'endpoints') and segment.endpoints:
                start, end = segment.endpoints
                print(f"  Endpoints: {start} → {end}")
                
                # Check if endpoints are on the curve
                if hasattr(segment, 'base_curve'):
                    curve = segment.base_curve
                else:
                    curve = segment
                
                start_val = curve.evaluate(start[0], start[1])
                end_val = curve.evaluate(end[0], end[1])
                
                print(f"  Start evaluation: {start_val:.6f}")
                print(f"  End evaluation: {end_val:.6f}")
                
                if abs(start_val) < 0.1 and abs(end_val) < 0.1:
                    print(f"  ✅ Endpoints are on curve")
                else:
                    print(f"  ❌ Endpoints not on curve!")
        
        # Check continuity
        print(f"\nContinuity check:")
        for i in range(len(heart.segments) - 1):
            seg1 = heart.segments[i]
            seg2 = heart.segments[i + 1]
            
            if seg1.endpoints and seg2.endpoints:
                end1 = seg1.endpoints[1]
                start2 = seg2.endpoints[0]
                
                distance = np.sqrt((end1[0] - start2[0])**2 + (end1[1] - start2[1])**2)
                
                if distance < 1e-6:
                    print(f"  Seg {i}→{i+1}: ✅ Connected (distance: {distance:.2e})")
                else:
                    print(f"  Seg {i}→{i+1}: ❌ Gap! {end1} → {start2} (distance: {distance:.6f})")
        
        # Check closure
        if len(heart.segments) >= 2:
            first_start = heart.segments[0].endpoints[0]
            last_end = heart.segments[-1].endpoints[1]
            
            closure_distance = np.sqrt((first_start[0] - last_end[0])**2 + (first_start[1] - last_end[1])**2)
            
            if closure_distance < 1e-6:
                print(f"  Closure: ✅ Closed (distance: {closure_distance:.2e})")
            else:
                print(f"  Closure: ❌ Open! {last_end} → {first_start} (distance: {closure_distance:.6f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Heart test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_heart_endpoints()