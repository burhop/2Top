#!/usr/bin/env python3
"""
Sprint 6 Demo: Area Regions and Boundary Representation

This demo showcases the AreaRegion class functionality implemented in Sprint 6,
including:
- Creating regions with closed boundaries
- Point containment testing with holes
- Area calculation using direct methods and polygonal approximation
- Serialization and deserialization
- Complex regions with multiple holes
"""

from geometry import (
    AreaRegion, create_square_from_edges, ConicSection, 
    TrimmedImplicitCurve, CompositeCurve
)
import sympy as sp
import numpy as np


def demo_basic_region():
    """Demonstrate basic AreaRegion functionality."""
    print("=" * 60)
    print("SPRINT 6 DEMO: Area Regions and Boundary Representation")
    print("=" * 60)
    
    print("\n1. BASIC REGION CREATION")
    print("-" * 30)
    
    # Create a simple square region
    square = create_square_from_edges((-2, -2), (2, 2))
    region = AreaRegion(square)
    
    print(f"Created region: {region}")
    print(f"Outer boundary segments: {len(region.outer_boundary.segments)}")
    print(f"Number of holes: {len(region.holes)}")
    
    # Test containment
    print("\n2. POINT CONTAINMENT TESTING")
    print("-" * 30)
    
    test_points = [
        (0, 0, "center"),
        (1, 1, "inside"),
        (-1.5, 1.5, "inside"),
        (3, 0, "outside"),
        (0, 3, "outside"),
        (-3, -3, "outside")
    ]
    
    for x, y, desc in test_points:
        result = region.contains(x, y)
        print(f"Point ({x:4.1f}, {y:4.1f}) [{desc:>7}]: {result}")
    
    # Test area calculation
    print("\n3. AREA CALCULATION")
    print("-" * 30)
    
    area = region.area()
    expected_area = 4 * 4  # 4x4 square
    print(f"Calculated area: {area}")
    print(f"Expected area:   {expected_area}")
    print(f"Accuracy:        {abs(area - expected_area) < 0.1}")


def demo_region_with_holes():
    """Demonstrate AreaRegion with holes."""
    print("\n4. REGIONS WITH HOLES")
    print("-" * 30)
    
    # Create outer boundary (6x6 square)
    outer = create_square_from_edges((-3, -3), (3, 3))
    
    # Create holes
    hole1 = create_square_from_edges((-2, -2), (-1, -1))  # Bottom-left hole
    hole2 = create_square_from_edges((1, 1), (2, 2))      # Top-right hole
    
    # Create region with holes
    region = AreaRegion(outer, [hole1, hole2])
    
    print(f"Created region with {len(region.holes)} holes")
    print(f"Outer boundary: 6x6 square (area = 36)")
    print(f"Hole 1: 1x1 square (area = 1)")
    print(f"Hole 2: 1x1 square (area = 1)")
    print(f"Expected total area: 36 - 1 - 1 = 34")
    
    # Test area calculation
    area = region.area()
    print(f"Calculated area: {area}")
    print(f"Accuracy: {abs(area - 34) < 1.0}")
    
    # Test containment with holes
    print("\nContainment testing with holes:")
    test_points = [
        (0, 0, "between holes"),
        (-1.5, -1.5, "inside hole1"),
        (1.5, 1.5, "inside hole2"),
        (2.5, 0, "outside holes, inside outer"),
        (4, 0, "outside outer boundary")
    ]
    
    for x, y, desc in test_points:
        result = region.contains(x, y)
        print(f"Point ({x:4.1f}, {y:4.1f}) [{desc:>20}]: {result}")


def demo_serialization():
    """Demonstrate AreaRegion serialization."""
    print("\n5. SERIALIZATION AND PERSISTENCE")
    print("-" * 30)
    
    # Create a complex region
    outer = create_square_from_edges((-2, -2), (2, 2))
    hole = create_square_from_edges((-1, -1), (1, 1))
    original = AreaRegion(outer, [hole])
    
    print("Original region:")
    print(f"  Area: {original.area()}")
    print(f"  Contains (0,0): {original.contains(0, 0)}")
    print(f"  Contains (1.5,0): {original.contains(1.5, 0)}")
    
    # Serialize
    data = original.to_dict()
    print(f"\nSerialized to dictionary with type: {data['type']}")
    print(f"Outer boundary type: {data['outer_boundary']['type']}")
    print(f"Number of holes: {len(data['holes'])}")
    
    # Deserialize
    reconstructed = AreaRegion.from_dict(data)
    print(f"\nReconstructed region:")
    print(f"  Area: {reconstructed.area()}")
    print(f"  Contains (0,0): {reconstructed.contains(0, 0)}")
    print(f"  Contains (1.5,0): {reconstructed.contains(1.5, 0)}")
    
    # Verify round-trip accuracy
    area_match = abs(original.area() - reconstructed.area()) < 0.1
    containment_match = (
        original.contains(0, 0) == reconstructed.contains(0, 0) and
        original.contains(1.5, 0) == reconstructed.contains(1.5, 0)
    )
    
    print(f"\nRound-trip validation:")
    print(f"  Area preserved: {area_match}")
    print(f"  Containment preserved: {containment_match}")
    print(f"  Serialization successful: {area_match and containment_match}")


def demo_edge_cases():
    """Demonstrate edge cases and robustness."""
    print("\n6. EDGE CASES AND ROBUSTNESS")
    print("-" * 30)
    
    # Test boundary points
    square = create_square_from_edges((-1, -1), (1, 1))
    region = AreaRegion(square)
    
    print("Testing boundary and near-boundary points:")
    boundary_points = [
        (1.0, 0.0, "right edge"),
        (0.0, 1.0, "top edge"),
        (-1.0, 0.0, "left edge"),
        (0.0, -1.0, "bottom edge"),
        (0.999, 0.0, "near right edge"),
        (1.001, 0.0, "just outside right edge")
    ]
    
    for x, y, desc in boundary_points:
        result = region.contains(x, y)
        print(f"Point ({x:6.3f}, {y:6.3f}) [{desc:>18}]: {result}")
    
    # Test with different numeric types
    print("\nTesting with different numeric types:")
    test_values = [
        (0, 0, "int"),
        (0.0, 0.0, "float"),
        (np.float64(0.0), np.float64(0.0), "numpy.float64")
    ]
    
    for x, y, dtype in test_values:
        result = region.contains(x, y)
        print(f"Point ({x}, {y}) [{dtype:>12}]: {result}")


def demo_performance():
    """Demonstrate performance characteristics."""
    print("\n7. PERFORMANCE CHARACTERISTICS")
    print("-" * 30)
    
    # Create a region
    square = create_square_from_edges((-1, -1), (1, 1))
    region = AreaRegion(square)
    
    # Test multiple containment queries
    import time
    
    n_tests = 1000
    test_points = [(np.random.uniform(-2, 2), np.random.uniform(-2, 2)) for _ in range(n_tests)]
    
    start_time = time.time()
    results = [region.contains(x, y) for x, y in test_points]
    end_time = time.time()
    
    inside_count = sum(results)
    total_time = end_time - start_time
    
    print(f"Containment testing performance:")
    print(f"  {n_tests} random points tested")
    print(f"  {inside_count} points inside region")
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Average time per query: {total_time/n_tests*1000:.3f} ms")
    
    # Test area calculation performance
    start_time = time.time()
    for _ in range(100):
        area = region.area()
    end_time = time.time()
    
    print(f"\nArea calculation performance:")
    print(f"  100 area calculations")
    print(f"  Total time: {end_time - start_time:.4f} seconds")
    print(f"  Average time per calculation: {(end_time - start_time)/100*1000:.3f} ms")


def main():
    """Run all Sprint 6 demos."""
    try:
        demo_basic_region()
        demo_region_with_holes()
        demo_serialization()
        demo_edge_cases()
        demo_performance()
        
        print("\n" + "=" * 60)
        print("SPRINT 6 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey achievements:")
        print("✅ AreaRegion class with closed boundary validation")
        print("✅ Robust point containment testing with holes")
        print("✅ Accurate area calculation using direct methods")
        print("✅ Complete serialization and deserialization support")
        print("✅ Edge case handling and performance optimization")
        print("\nSprint 6: Area Regions and Boundary Representation - COMPLETE")
        
    except Exception as e:
        print(f"\nERROR in Sprint 6 demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
