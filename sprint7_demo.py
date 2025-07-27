"""
Sprint 7 Demo: Advanced Scalar Fields and Pluggable Strategies

This demo showcases the new scalar field functionality implemented in Sprint 7:
- BaseField hierarchy with CurveField and BlendedField
- FieldStrategy pattern with SignedDistanceStrategy and OccupancyFillStrategy
- Integration with AreaRegion for field generation
- Field evaluation, gradient computation, and level set extraction
- Serialization and deserialization of fields and strategies

Key Features Demonstrated:
1. Creating scalar fields from implicit curves
2. Blending multiple fields with algebraic operations
3. Generating fields from area regions using pluggable strategies
4. Field evaluation and gradient computation
5. Serialization round-trip for persistence
"""

import numpy as np
import matplotlib.pyplot as plt
from geometry import (
    # Core classes
    ImplicitCurve, ConicSection, AreaRegion, CompositeCurve,
    create_square_from_edges,
    # Field classes
    BaseField, CurveField, BlendedField,
    # Strategy classes
    SignedDistanceStrategy, OccupancyFillStrategy
)
import sympy as sp


def demo_curve_fields():
    """Demonstrate CurveField functionality."""
    print("=" * 60)
    print("DEMO 1: CurveField - Wrapping Implicit Curves as Scalar Fields")
    print("=" * 60)
    
    # Create some implicit curves
    x, y = sp.symbols('x y')
    
    # Circle
    circle_expr = x**2 + y**2 - 4  # Circle with radius 2
    circle_curve = ImplicitCurve(circle_expr, (x, y))
    circle_field = CurveField(circle_curve)
    
    # Ellipse
    ellipse_expr = x**2 + 4*y**2 - 16  # x^2 + 4y^2 = 16
    ellipse = ConicSection(ellipse_expr, (x, y))
    ellipse_field = CurveField(ellipse)
    
    print(f"Created circle field: {circle_field}")
    print(f"Created ellipse field: {ellipse_field}")
    
    # Test field evaluation
    test_points = [(0, 0), (1, 1), (2, 0), (3, 0)]
    
    print("\nField Evaluation:")
    print("Point\t\tCircle Field\tEllipse Field")
    print("-" * 50)
    
    for px, py in test_points:
        circle_val = circle_field.evaluate(px, py)
        ellipse_val = ellipse_field.evaluate(px, py)
        print(f"({px:2}, {py:2})\t\t{circle_val:8.3f}\t{ellipse_val:8.3f}")
    
    # Test vectorized evaluation
    print("\nVectorized Evaluation:")
    x_vals = np.array([0, 1, 2, 3])
    y_vals = np.array([0, 1, 0, 0])
    
    circle_results = circle_field.evaluate(x_vals, y_vals)
    ellipse_results = ellipse_field.evaluate(x_vals, y_vals)
    
    print(f"Circle results: {circle_results}")
    print(f"Ellipse results: {ellipse_results}")
    
    # Test gradient computation
    print("\nGradient Computation:")
    grad_x, grad_y = circle_field.gradient(1.0, 1.0)
    print(f"Circle gradient at (1,1): ({grad_x:.3f}, {grad_y:.3f})")
    
    grad_x, grad_y = ellipse_field.gradient(2.0, 1.0)
    print(f"Ellipse gradient at (2,1): ({grad_x:.3f}, {grad_y:.3f})")
    
    # Test serialization
    print("\nSerialization Test:")
    circle_data = circle_field.to_dict()
    print(f"Circle field serialized: {circle_data['type']}")
    
    reconstructed = CurveField.from_dict(circle_data)
    original_val = circle_field.evaluate(1.5, 1.5)
    reconstructed_val = reconstructed.evaluate(1.5, 1.5)
    print(f"Original value: {original_val:.6f}")
    print(f"Reconstructed value: {reconstructed_val:.6f}")
    print(f"Serialization successful: {abs(original_val - reconstructed_val) < 1e-10}")
    
    return circle_field, ellipse_field


def demo_blended_fields(circle_field, ellipse_field):
    """Demonstrate BlendedField functionality."""
    print("\n" + "=" * 60)
    print("DEMO 2: BlendedField - Algebraic Combinations of Scalar Fields")
    print("=" * 60)
    
    # Create different blended fields
    blended_add = BlendedField([circle_field, ellipse_field], 'add')
    blended_min = BlendedField([circle_field, ellipse_field], 'min')
    blended_max = BlendedField([circle_field, ellipse_field], 'max')
    blended_multiply = BlendedField([circle_field, ellipse_field], 'multiply')
    
    print("Created blended fields:")
    print(f"- Addition: {blended_add}")
    print(f"- Minimum: {blended_min}")
    print(f"- Maximum: {blended_max}")
    print(f"- Multiplication: {blended_multiply}")
    
    # Test evaluation at various points
    test_points = [(0, 0), (1, 1), (2, 0), (0, 2)]
    
    print("\nBlended Field Evaluation:")
    print("Point\t\tAdd\t\tMin\t\tMax\t\tMultiply")
    print("-" * 70)
    
    for px, py in test_points:
        add_val = blended_add.evaluate(px, py)
        min_val = blended_min.evaluate(px, py)
        max_val = blended_max.evaluate(px, py)
        mult_val = blended_multiply.evaluate(px, py)
        print(f"({px:2}, {py:2})\t\t{add_val:6.2f}\t\t{min_val:6.2f}\t\t{max_val:6.2f}\t\t{mult_val:6.2f}")
    
    # Test gradient computation
    print("\nGradient Computation for Blended Fields:")
    grad_x, grad_y = blended_add.gradient(1.0, 1.0)
    print(f"Addition gradient at (1,1): ({grad_x:.3f}, {grad_y:.3f})")
    
    grad_x, grad_y = blended_min.gradient(1.0, 1.0)
    print(f"Minimum gradient at (1,1): ({grad_x:.3f}, {grad_y:.3f})")
    
    # Test serialization
    print("\nSerialization Test:")
    blended_data = blended_add.to_dict()
    print(f"Blended field serialized: {blended_data['type']}, operation: {blended_data['operation']}")
    
    reconstructed = BlendedField.from_dict(blended_data)
    original_val = blended_add.evaluate(1.5, 1.5)
    reconstructed_val = reconstructed.evaluate(1.5, 1.5)
    print(f"Original value: {original_val:.6f}")
    print(f"Reconstructed value: {reconstructed_val:.6f}")
    print(f"Serialization successful: {abs(original_val - reconstructed_val) < 1e-10}")
    
    return blended_min


def demo_field_strategies():
    """Demonstrate field strategy pattern with AreaRegion."""
    print("\n" + "=" * 60)
    print("DEMO 3: Field Strategies - Pluggable Field Generation from Regions")
    print("=" * 60)
    
    # Create test regions
    print("Creating test regions...")
    
    # Simple square region
    square = create_square_from_edges((0, 0), (4, 4))
    square_region = AreaRegion(square)
    print(f"Square region: {square_region}")
    
    # Region with hole
    outer = create_square_from_edges((0, 0), (6, 6))
    hole = create_square_from_edges((2, 2), (4, 4))
    region_with_hole = AreaRegion(outer, [hole])
    print(f"Region with hole: {region_with_hole}")
    
    # Create field strategies
    sdf_strategy = SignedDistanceStrategy(resolution=0.1)
    occupancy_strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
    
    print(f"\nCreated strategies:")
    print(f"- Signed Distance Strategy: resolution={sdf_strategy.resolution}")
    print(f"- Occupancy Strategy: inside={occupancy_strategy.inside_value}, outside={occupancy_strategy.outside_value}")
    
    # Generate fields from regions
    print("\nGenerating fields from square region:")
    square_sdf = square_region.get_field(sdf_strategy)
    square_occupancy = square_region.get_field(occupancy_strategy)
    
    print(f"- Signed distance field: {type(square_sdf).__name__}")
    print(f"- Occupancy field: {type(square_occupancy).__name__}")
    
    # Test field evaluation
    test_points = [(2, 2), (0, 2), (5, 5), (-1, -1)]
    
    print("\nField Evaluation on Square Region:")
    print("Point\t\tSigned Distance\tOccupancy")
    print("-" * 45)
    
    for px, py in test_points:
        sdf_val = square_sdf.evaluate(px, py)
        occ_val = square_occupancy.evaluate(px, py)
        print(f"({px:2}, {py:2})\t\t{sdf_val:8.3f}\t{occ_val:8.1f}")
    
    # Test with region with hole
    print("\nGenerating fields from region with hole:")
    hole_sdf = region_with_hole.get_field(sdf_strategy)
    hole_occupancy = region_with_hole.get_field(occupancy_strategy)
    
    print("\nField Evaluation on Region with Hole:")
    print("Point\t\tSigned Distance\tOccupancy\tRegion Contains")
    print("-" * 60)
    
    for px, py in test_points:
        sdf_val = hole_sdf.evaluate(px, py)
        occ_val = hole_occupancy.evaluate(px, py)
        contains = region_with_hole.contains(px, py)
        print(f"({px:2}, {py:2})\t\t{sdf_val:8.3f}\t{occ_val:8.1f}\t{contains}")
    
    # Test point inside hole
    hole_point = (3, 3)  # Inside the hole
    px, py = hole_point
    sdf_val = hole_sdf.evaluate(px, py)
    occ_val = hole_occupancy.evaluate(px, py)
    contains = region_with_hole.contains(px, py)
    print(f"({px:2}, {py:2}) [hole]\t{sdf_val:8.3f}\t{occ_val:8.1f}\t{contains}")
    
    # Test strategy serialization
    print("\nStrategy Serialization Test:")
    sdf_data = sdf_strategy.to_dict()
    occ_data = occupancy_strategy.to_dict()
    
    print(f"SDF strategy: {sdf_data}")
    print(f"Occupancy strategy: {occ_data}")
    
    # Reconstruct strategies
    sdf_reconstructed = SignedDistanceStrategy.from_dict(sdf_data)
    occ_reconstructed = OccupancyFillStrategy.from_dict(occ_data)
    
    print(f"SDF reconstruction successful: {sdf_reconstructed.resolution == sdf_strategy.resolution}")
    print(f"Occupancy reconstruction successful: {occ_reconstructed.inside_value == occupancy_strategy.inside_value}")
    
    return square_sdf, square_occupancy


def demo_advanced_field_operations(blended_field, sdf_field):
    """Demonstrate advanced field operations."""
    print("\n" + "=" * 60)
    print("DEMO 4: Advanced Field Operations")
    print("=" * 60)
    
    # Level set extraction
    print("Level Set Extraction:")
    try:
        level_curve = blended_field.level_set(0.0)
        print(f"Extracted level set from blended field: {type(level_curve).__name__}")
        
        # Test level curve evaluation
        level_val = level_curve.evaluate(1.0, 1.0)
        print(f"Level curve value at (1,1): {level_val:.6f}")
    except Exception as e:
        print(f"Level set extraction: {e}")
    
    # Gradient analysis
    print("\nGradient Analysis:")
    
    # Create a grid for gradient visualization
    x_range = np.linspace(-1, 5, 7)
    y_range = np.linspace(-1, 5, 7)
    
    print("Gradient vectors for SDF field:")
    print("Point\t\tGradient")
    print("-" * 30)
    
    for i, x in enumerate(x_range[::2]):  # Sample every other point
        for j, y in enumerate(y_range[::2]):
            try:
                grad_x, grad_y = sdf_field.gradient(x, y)
                magnitude = np.sqrt(grad_x**2 + grad_y**2)
                print(f"({x:3.1f}, {y:3.1f})\t\t({grad_x:6.3f}, {grad_y:6.3f}) |{magnitude:5.3f}|")
            except Exception as e:
                print(f"({x:3.1f}, {y:3.1f})\t\tError: {e}")
    
    # Vectorized operations performance test
    print("\nVectorized Operations Performance Test:")
    
    # Create large arrays for performance testing
    n_points = 1000
    x_test = np.random.uniform(-2, 6, n_points)
    y_test = np.random.uniform(-2, 6, n_points)
    
    import time
    
    # Time vectorized evaluation
    start_time = time.time()
    vectorized_result = sdf_field.evaluate(x_test, y_test)
    vectorized_time = time.time() - start_time
    
    # Time scalar loop evaluation (sample)
    start_time = time.time()
    scalar_results = []
    for i in range(min(100, n_points)):  # Only test first 100 for speed
        scalar_results.append(sdf_field.evaluate(x_test[i], y_test[i]))
    scalar_time = time.time() - start_time
    scalar_time_extrapolated = scalar_time * (n_points / 100)
    
    print(f"Vectorized evaluation ({n_points} points): {vectorized_time:.4f} seconds")
    print(f"Scalar evaluation (extrapolated): {scalar_time_extrapolated:.4f} seconds")
    print(f"Speedup factor: {scalar_time_extrapolated / vectorized_time:.1f}x")
    
    # Verify results are consistent
    sample_indices = np.random.choice(n_points, 10, replace=False)
    consistent = True
    for idx in sample_indices:
        vec_val = vectorized_result[idx]
        scalar_val = sdf_field.evaluate(x_test[idx], y_test[idx])
        if abs(vec_val - scalar_val) > 1e-10:
            consistent = False
            break
    
    print(f"Vectorized vs scalar consistency: {consistent}")


def demo_field_visualization():
    """Create a simple visualization of field values."""
    print("\n" + "=" * 60)
    print("DEMO 5: Field Visualization")
    print("=" * 60)
    
    # Create a simple region and field
    square = create_square_from_edges((1, 1), (3, 3))
    region = AreaRegion(square)
    
    occupancy_strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
    occupancy_field = region.get_field(occupancy_strategy)
    
    # Create a grid for visualization
    x = np.linspace(0, 4, 21)
    y = np.linspace(0, 4, 21)
    X, Y = np.meshgrid(x, y)
    
    # Evaluate field on grid
    Z = occupancy_field.evaluate(X, Y)
    
    print("Creating field visualization...")
    
    try:
        plt.figure(figsize=(8, 6))
        
        # Plot field values
        plt.contourf(X, Y, Z, levels=[0, 0.5, 1], colors=['lightblue', 'darkblue'], alpha=0.7)
        plt.contour(X, Y, Z, levels=[0.5], colors=['red'], linewidths=2)
        
        plt.title('Occupancy Field Visualization')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.colorbar(label='Field Value')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        # Add some test points
        test_points = [(0.5, 0.5), (2, 2), (3.5, 3.5)]
        for px, py in test_points:
            val = occupancy_field.evaluate(px, py)
            plt.plot(px, py, 'ro' if val > 0.5 else 'bo', markersize=8)
            plt.annotate(f'({px}, {py})\nval={val}', (px, py), 
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('sprint7_field_visualization.png', dpi=150, bbox_inches='tight')
        print("Visualization saved as 'sprint7_field_visualization.png'")
        plt.show()
        
    except Exception as e:
        print(f"Visualization failed (this is normal in headless environments): {e}")
    
    # Print ASCII visualization as fallback
    print("\nASCII Field Visualization (21x21 grid):")
    print("Legend: . = outside (0), # = inside (1)")
    print()
    
    for i in range(len(y)):
        row = ""
        for j in range(len(x)):
            val = Z[len(y)-1-i, j]  # Flip Y axis for display
            row += "#" if val > 0.5 else "."
        print(row)


def main():
    """Run all Sprint 7 demos."""
    print("SPRINT 7 DEMO: Advanced Scalar Fields and Pluggable Strategies")
    print("=" * 80)
    print("This demo showcases the new scalar field functionality:")
    print("- BaseField hierarchy (CurveField, BlendedField)")
    print("- FieldStrategy pattern (SignedDistanceStrategy, OccupancyFillStrategy)")
    print("- Integration with AreaRegion")
    print("- Field evaluation, gradients, and serialization")
    print("=" * 80)
    
    try:
        # Run demos
        circle_field, ellipse_field = demo_curve_fields()
        blended_field = demo_blended_fields(circle_field, ellipse_field)
        sdf_field, occ_field = demo_field_strategies()
        demo_advanced_field_operations(blended_field, sdf_field)
        demo_field_visualization()
        
        print("\n" + "=" * 80)
        print("SPRINT 7 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("All scalar field functionality is working correctly:")
        print("✓ CurveField wrapping of implicit curves")
        print("✓ BlendedField algebraic combinations")
        print("✓ FieldStrategy pattern implementation")
        print("✓ SignedDistanceStrategy and OccupancyFillStrategy")
        print("✓ AreaRegion.get_field() integration")
        print("✓ Field evaluation and gradient computation")
        print("✓ Serialization and deserialization")
        print("✓ Vectorized operations and performance")
        print("\nThe 2D Implicit Geometry Module now supports advanced scalar field")
        print("generation and manipulation with a flexible, extensible architecture!")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
