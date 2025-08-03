#!/usr/bin/env python3
"""
Debug script to understand why triangle composite curves are not being detected as closed.
"""

import sys
import os
sys.path.append('.')

import sympy as sp
from geometry import ImplicitCurve, TrimmedImplicitCurve, CompositeCurve, AreaRegion

def create_simple_triangle():
    """Create a simple triangle and test if it's detected as closed."""
    print("Creating simple triangle...")
    
    x, y = sp.symbols('x y')
    vertices = [(-1, -1), (1, -1), (0, 1)]
    v1, v2, v3 = vertices
    
    print(f"Triangle vertices: {vertices}")
    
    # Create 3 line segments
    segments = []
    
    # Edge 1: v1 to v2
    x1, y1 = v1
    x2, y2 = v2
    edge1_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
    edge1_curve = ImplicitCurve(edge1_expr, (x, y))
    print(f"Edge 1 expression: {edge1_expr}")
    
    def edge1_mask(px, py):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            if dx == 0:
                return False
            t = (px - x1) / dx
        else:
            if dy == 0:
                return False
            t = (py - y1) / dy
        return 0 <= t <= 1
    
    edge1_segment = TrimmedImplicitCurve(edge1_curve, edge1_mask)
    segments.append(edge1_segment)
    
    # Edge 2: v2 to v3
    x1, y1 = v2
    x2, y2 = v3
    edge2_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
    edge2_curve = ImplicitCurve(edge2_expr, (x, y))
    print(f"Edge 2 expression: {edge2_expr}")
    
    def edge2_mask(px, py):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            if dx == 0:
                return False
            t = (px - x1) / dx
        else:
            if dy == 0:
                return False
            t = (py - y1) / dy
        return 0 <= t <= 1
    
    edge2_segment = TrimmedImplicitCurve(edge2_curve, edge2_mask)
    segments.append(edge2_segment)
    
    # Edge 3: v3 to v1
    x1, y1 = v3
    x2, y2 = v1
    edge3_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
    edge3_curve = ImplicitCurve(edge3_expr, (x, y))
    print(f"Edge 3 expression: {edge3_expr}")
    
    def edge3_mask(px, py):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            if dx == 0:
                return False
            t = (px - x1) / dx
        else:
            if dy == 0:
                return False
            t = (py - y1) / dy
        return 0 <= t <= 1
    
    edge3_segment = TrimmedImplicitCurve(edge3_curve, edge3_mask)
    segments.append(edge3_segment)
    
    # Create composite curve
    triangle_composite = CompositeCurve(segments, (x, y))
    print(f"Created composite curve with {len(triangle_composite.segments)} segments")
    
    # Test closure
    print("\nTesting closure...")
    is_closed = triangle_composite.is_closed()
    print(f"is_closed() result: {is_closed}")
    
    # Test explicit endpoints
    print("\nChecking explicit endpoints...")
    for i, segment in enumerate(triangle_composite.segments):
        print(f"Segment {i}:")
        if hasattr(segment, 'get_endpoints'):
            try:
                endpoints = segment.get_endpoints()
                print(f"  Endpoints: {endpoints}")
            except Exception as e:
                print(f"  Error getting endpoints: {e}")
        else:
            print(f"  No get_endpoints method")
    
    # Try to create AreaRegion
    print("\nTrying to create AreaRegion...")
    try:
        triangle_region = AreaRegion(triangle_composite)
        print("✅ AreaRegion created successfully!")
        return triangle_region
    except Exception as e:
        print(f"❌ AreaRegion creation failed: {e}")
        return None

def main():
    print("=" * 60)
    print("TRIANGLE CLOSURE DEBUG")
    print("=" * 60)
    
    triangle_region = create_simple_triangle()
    
    if triangle_region:
        print("\n✅ Triangle region creation successful!")
    else:
        print("\n❌ Triangle region creation failed!")

if __name__ == "__main__":
    main()
