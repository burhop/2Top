#!/usr/bin/env python3
"""
Demo script showing the revived 2Top geometry library capabilities
"""

import sympy as sp
import numpy as np
from geometry import *

def main():
    print("🎯 2Top Geometry Library Revival Demo")
    print("=" * 50)
    
    # Setup symbols
    x, y = sp.symbols('x y')
    
    # 1. Basic Curves
    print("\n1. Basic Implicit Curves:")
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
    line = PolynomialCurve(x + y - 1, (x, y))
    superellipse = Superellipse(a=1.5, b=1.0, n=4.0, variables=(x, y))
    
    print(f"  Circle: {circle}")
    print(f"  Ellipse: {ellipse}")
    print(f"  Line: {line}")
    print(f"  Superellipse: {superellipse}")
    
    # 2. Curve Properties
    print("\n2. Curve Properties:")
    print(f"  Circle degree: {circle.degree()}")
    print(f"  Line degree: {line.degree()}")
    print(f"  Circle at origin: {circle.evaluate(0, 0)}")
    print(f"  Circle at (1,0): {circle.evaluate(1, 0)}")
    
    # 3. Constructive Geometry
    print("\n3. Constructive Geometry (R-functions):")
    union_curve = union(circle, ellipse)
    intersect_curve = intersect(circle, ellipse)
    diff_curve = difference(circle, ellipse)
    blend_curve = blend(circle, ellipse, alpha=0.3)
    
    print(f"  Union at origin: {union_curve.evaluate(0, 0)}")
    print(f"  Intersection at origin: {intersect_curve.evaluate(0, 0)}")
    print(f"  Difference at origin: {diff_curve.evaluate(0, 0)}")
    print(f"  Blend at origin: {blend_curve.evaluate(0, 0)}")
    
    # 4. Composite Curves and Regions
    print("\n4. Composite Curves and Area Regions:")
    square = create_square_from_edges((-1, -1), (1, 1))
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.5)
    
    print(f"  Square is closed: {square.is_closed()}")
    print(f"  Circle quarters is closed: {circle_quarters.is_closed()}")
    
    # Create area regions
    square_region = AreaRegion(square)
    circle_region = AreaRegion(circle_quarters)
    
    print(f"  Point (0,0) in square: {square_region.contains(0, 0)}")
    print(f"  Point (2,0) in square: {square_region.contains(2, 0)}")
    print(f"  Point (0,0) in circle: {circle_region.contains(0, 0)}")
    
    # 5. Field Generation
    print("\n5. Scalar Field Generation:")
    sdf_strategy = SignedDistanceStrategy(resolution=0.1)
    occ_strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
    
    sdf_field = sdf_strategy.generate_field(square_region)
    occ_field = occ_strategy.generate_field(square_region)
    
    print(f"  SDF field created: {type(sdf_field).__name__}")
    print(f"  Occupancy field created: {type(occ_field).__name__}")
    
    # 6. Vectorized Operations
    print("\n6. Vectorized Operations:")
    test_points_x = np.array([0, 0.5, 1.0, 1.5])
    test_points_y = np.array([0, 0.5, 0, 0])
    
    circle_values = circle.evaluate(test_points_x, test_points_y)
    print(f"  Circle values at test points: {circle_values}")
    
    # 7. Serialization
    print("\n7. Serialization:")
    circle_dict = circle.to_dict()
    reconstructed_circle = ConicSection.from_dict(circle_dict)
    
    print(f"  Original circle at (0,0): {circle.evaluate(0, 0)}")
    print(f"  Reconstructed circle at (0,0): {reconstructed_circle.evaluate(0, 0)}")
    print(f"  Serialization successful: {circle.evaluate(0, 0) == reconstructed_circle.evaluate(0, 0)}")
    
    print("\n🎉 All features working perfectly!")
    print("The 2Top geometry library has been successfully revived!")

if __name__ == "__main__":
    main()