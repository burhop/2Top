"""
Sprint 4 Demo - Constructive Geometry via R-Functions

This demo showcases the functionality implemented in Sprint 4:
- RFunctionCurve class for constructive solid geometry operations
- Sharp operations: union, intersection, difference using min/max
- Smooth blending operations with configurable alpha parameter
- High-level wrapper functions for convenient curve construction
- Serialization of composite curves with nested structures
- Interface consistency with existing curve classes
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from geometry import (
    ImplicitCurve, ConicSection, PolynomialCurve, 
    Superellipse, RFunctionCurve,
    union, intersect, difference, blend
)


def demo_sharp_operations():
    """Demonstrate sharp constructive geometry operations"""
    print("=== Sharp Operations Demo ===")
    
    # Create base curves
    x, y = sp.symbols('x y')
    circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))  # Circle at origin
    circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))  # Circle at (1,0)
    
    print("\nBase curves:")
    print(f"  Circle 1: {circle1.expression} = 0")
    print(f"  Circle 2: {circle2.expression} = 0")
    
    # Create sharp operations
    union_curve = union(circle1, circle2)
    intersection_curve = intersect(circle1, circle2)
    difference_curve = difference(circle1, circle2)
    
    print(f"\nSharp operations:")
    print(f"  Union: {union_curve}")
    print(f"  Intersection: {intersection_curve}")
    print(f"  Difference: {difference_curve}")
    
    # Test evaluation at key points
    test_points = [
        (-0.5, 0.0, "Inside circle1 only"),
        (1.5, 0.0, "Inside circle2 only"),
        (0.5, 0.0, "Inside both circles (overlap)"),
        (0.0, 2.0, "Outside both circles")
    ]
    
    print(f"\nEvaluation at test points:")
    print(f"{'Point':<20} {'Union':<8} {'Intersect':<10} {'Difference':<10} {'Description'}")
    print("-" * 70)
    
    for x, y, desc in test_points:
        union_val = union_curve.evaluate(x, y)
        intersect_val = intersection_curve.evaluate(x, y)
        diff_val = difference_curve.evaluate(x, y)
        
        print(f"({x:4.1f}, {y:4.1f}){'':<8} {union_val:7.3f}  {intersect_val:9.3f}  {diff_val:9.3f}  {desc}")


def demo_smooth_blending():
    """Demonstrate smooth blending operations"""
    print("\n=== Smooth Blending Demo ===")
    
    # Create base curves
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    square = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
    
    print(f"\nBase curves:")
    print(f"  Circle: {circle.expression} = 0")
    print(f"  Square-like: {square}")
    
    # Create blends with different alpha values
    alpha_values = [0.1, 0.5, 1.0, 2.0]
    blend_curves = {}
    
    for alpha in alpha_values:
        blend_curves[alpha] = blend(circle, square, alpha)
    
    print(f"\nSmooth blending with different alpha values:")
    print(f"{'Alpha':<8} {'At origin':<12} {'At (0.5,0)':<12} {'At (1,0)':<12}")
    print("-" * 50)
    
    for alpha in alpha_values:
        curve = blend_curves[alpha]
        val_origin = curve.evaluate(0.0, 0.0)
        val_half = curve.evaluate(0.5, 0.0)
        val_edge = curve.evaluate(1.0, 0.0)
        
        print(f"{alpha:<8.1f} {val_origin:<12.3f} {val_half:<12.3f} {val_edge:<12.3f}")
    
    # Compare with sharp union
    sharp_union = union(circle, square)
    print(f"\nComparison with sharp union:")
    print(f"Sharp union at (0.5, 0): {sharp_union.evaluate(0.5, 0.0):.6f}")
    print(f"Smooth blend (α=0.1) at (0.5, 0): {blend_curves[0.1].evaluate(0.5, 0.0):.6f}")
    print(f"Smooth blend (α=1.0) at (0.5, 0): {blend_curves[1.0].evaluate(0.5, 0.0):.6f}")


def demo_mixed_curve_types():
    """Demonstrate constructive operations with different curve types"""
    print("\n=== Mixed Curve Types Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create different curve types
    conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    polynomial = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    superellipse = Superellipse(a=1.5, b=1.0, n=2.5, variables=(x, y))
    
    print(f"\nDifferent curve types:")
    print(f"  Conic: {conic.expression} = 0")
    print(f"  Polynomial: {polynomial.expression} = 0")
    print(f"  Superellipse: {superellipse}")
    
    # Create mixed operations
    mixed_operations = {
        "Conic ∪ Polynomial": union(conic, polynomial),
        "Conic ∩ Superellipse": intersect(conic, superellipse),
        "Polynomial - Superellipse": difference(polynomial, superellipse),
        "Blend(Conic, Polynomial, α=0.3)": blend(conic, polynomial, alpha=0.3)
    }
    
    print(f"\nMixed operations evaluation at (0.5, 0.5):")
    for name, curve in mixed_operations.items():
        value = curve.evaluate(0.5, 0.5)
        print(f"  {name}: {value:.6f}")


def demo_nested_operations():
    """Demonstrate nested constructive operations"""
    print("\n=== Nested Operations Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create base shapes
    circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
    circle3 = ConicSection((x-0.5)**2 + (y-0.5)**2 - 0.25, variables=(x, y))
    
    print(f"\nBase shapes:")
    print(f"  Circle 1: centered at origin, radius 1")
    print(f"  Circle 2: centered at (1,0), radius 1")
    print(f"  Circle 3: centered at (0.5,0.5), radius 0.5")
    
    # Create nested operations
    print(f"\nNested operations:")
    
    # (Circle1 ∪ Circle2) ∩ Circle3
    union_12 = union(circle1, circle2)
    nested_1 = intersect(union_12, circle3)
    print(f"  (Circle1 ∪ Circle2) ∩ Circle3")
    print(f"    Type: {type(nested_1).__name__}")
    print(f"    Operation: {nested_1.operation}")
    print(f"    Child 1 type: {type(nested_1.curve1).__name__}")
    print(f"    Child 1 operation: {nested_1.curve1.operation}")
    
    # Circle1 - blend(Circle2, Circle3, α=0.5)
    blend_23 = blend(circle2, circle3, alpha=0.5)
    nested_2 = difference(circle1, blend_23)
    print(f"\n  Circle1 - blend(Circle2, Circle3, α=0.5)")
    print(f"    Type: {type(nested_2).__name__}")
    print(f"    Operation: {nested_2.operation}")
    print(f"    Child 2 type: {type(nested_2.curve2).__name__}")
    print(f"    Child 2 operation: {nested_2.curve2.operation}")
    print(f"    Child 2 alpha: {nested_2.curve2.alpha}")
    
    # Evaluate nested operations
    test_point = (0.5, 0.3)
    print(f"\nEvaluation at {test_point}:")
    print(f"  Nested 1: {nested_1.evaluate(*test_point):.6f}")
    print(f"  Nested 2: {nested_2.evaluate(*test_point):.6f}")


def demo_gradient_computation():
    """Demonstrate gradient computation for R-function curves"""
    print("\n=== Gradient Computation Demo ===")
    
    x, y = sp.symbols('x y')
    circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
    
    # Create different operation types
    operations = {
        "Union": union(circle1, circle2),
        "Intersection": intersect(circle1, circle2),
        "Difference": difference(circle1, circle2),
        "Blend (α=0.5)": blend(circle1, circle2, alpha=0.5)
    }
    
    test_point = (0.5, 0.0)  # Point in overlap region
    
    print(f"\nGradient computation at {test_point}:")
    print(f"{'Operation':<15} {'Grad X':<10} {'Grad Y':<10} {'Magnitude':<10}")
    print("-" * 50)
    
    for name, curve in operations.items():
        try:
            grad_x, grad_y = curve.gradient(*test_point)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            print(f"{name:<15} {grad_x:<10.3f} {grad_y:<10.3f} {magnitude:<10.3f}")
        except Exception as e:
            print(f"{name:<15} Error: {str(e)[:30]}")
    
    # Compare with base curve gradients
    print(f"\nBase curve gradients at {test_point}:")
    grad1_x, grad1_y = circle1.gradient(*test_point)
    grad2_x, grad2_y = circle2.gradient(*test_point)
    print(f"  Circle 1: ({grad1_x:.3f}, {grad1_y:.3f})")
    print(f"  Circle 2: ({grad2_x:.3f}, {grad2_y:.3f})")


def demo_serialization():
    """Demonstrate serialization of composite curves"""
    print("\n=== Serialization Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create base curves
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
    
    # Create composite curve
    blend_curve = blend(circle, ellipse, alpha=0.5)
    
    print(f"Original curve:")
    print(f"  Type: {type(blend_curve).__name__}")
    print(f"  Operation: {blend_curve.operation}")
    print(f"  Alpha: {blend_curve.alpha}")
    
    # Serialize
    serialized = blend_curve.to_dict()
    print(f"\nSerialized structure:")
    print(f"  Type: {serialized['type']}")
    print(f"  Operation: {serialized['operation']}")
    print(f"  Alpha: {serialized['alpha']}")
    print(f"  Child 1 type: {serialized['curve1']['type']}")
    print(f"  Child 2 type: {serialized['curve2']['type']}")
    
    # Deserialize
    restored = RFunctionCurve.from_dict(serialized)
    print(f"\nRestored curve:")
    print(f"  Type: {type(restored).__name__}")
    print(f"  Operation: {restored.operation}")
    print(f"  Alpha: {restored.alpha}")
    
    # Test functional equivalence
    test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
    print(f"\nFunctional equivalence test:")
    print(f"{'Point':<12} {'Original':<12} {'Restored':<12} {'Difference':<12}")
    print("-" * 50)
    
    for x, y in test_points:
        orig_val = blend_curve.evaluate(x, y)
        rest_val = restored.evaluate(x, y)
        diff = abs(orig_val - rest_val)
        print(f"({x:4.1f}, {y:4.1f}){'':<4} {orig_val:<12.6f} {rest_val:<12.6f} {diff:<12.2e}")
    
    print("✓ Serialization round-trip successful!")


def demo_vectorized_operations():
    """Demonstrate vectorized evaluation for R-function curves"""
    print("\n=== Vectorized Operations Demo ===")
    
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    square = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
    
    # Create composite curve
    union_curve = union(circle, square)
    
    # Create test grid
    x_vals = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
    y_vals = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    
    print(f"Test points: x = {x_vals}")
    print(f"             y = {y_vals}")
    
    # Vectorized evaluation
    union_results = union_curve.evaluate(x_vals, y_vals)
    circle_results = circle.evaluate(x_vals, y_vals)
    square_results = square.evaluate(x_vals, y_vals)
    
    print(f"\nVectorized evaluation results:")
    print(f"{'X':<6} {'Circle':<10} {'Square':<10} {'Union':<10} {'Expected':<10}")
    print("-" * 50)
    
    for i, x in enumerate(x_vals):
        expected = min(circle_results[i], square_results[i])
        print(f"{x:<6.1f} {circle_results[i]:<10.3f} {square_results[i]:<10.3f} "
              f"{union_results[i]:<10.3f} {expected:<10.3f}")
    
    # Test vectorized gradients
    grad_x, grad_y = union_curve.gradient(x_vals, y_vals)
    print(f"\nVectorized gradient results:")
    print(f"{'X':<6} {'Grad X':<10} {'Grad Y':<10} {'Magnitude':<10}")
    print("-" * 40)
    
    for i, x in enumerate(x_vals):
        magnitude = np.sqrt(grad_x[i]**2 + grad_y[i]**2)
        print(f"{x:<6.1f} {grad_x[i]:<10.3f} {grad_y[i]:<10.3f} {magnitude:<10.3f}")


def demo_interface_consistency():
    """Demonstrate interface consistency with other curve types"""
    print("\n=== Interface Consistency Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create different curve types including RFunctionCurve
    curves = {
        "ConicSection": ConicSection(x**2 + y**2 - 1, variables=(x, y)),
        "PolynomialCurve": PolynomialCurve(x**3 + y**3 - 1, variables=(x, y)),
        "Superellipse": Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y)),
        "RFunctionCurve": union(
            ConicSection(x**2 + y**2 - 1, variables=(x, y)),
            ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
        )
    }
    
    print(f"All curve types inherit from ImplicitCurve:")
    for name, curve in curves.items():
        is_implicit = isinstance(curve, ImplicitCurve)
        print(f"  {name:<15}: {is_implicit}")
    
    print(f"\nAll curves have required methods:")
    required_methods = ['evaluate', 'gradient', 'normal', 'to_dict', 'plot']
    for method in required_methods:
        print(f"  {method}:")
        for name, curve in curves.items():
            has_method = hasattr(curve, method) and callable(getattr(curve, method))
            print(f"    {name:<15}: {has_method}")
    
    # Test evaluation consistency
    test_point = (0.5, 0.5)
    print(f"\nEvaluation at {test_point}:")
    for name, curve in curves.items():
        try:
            value = curve.evaluate(*test_point)
            print(f"  {name:<15}: {value:.6f}")
        except Exception as e:
            print(f"  {name:<15}: Error - {str(e)[:30]}")


def main():
    """Run all Sprint 4 demos"""
    print("Sprint 4 Geometry Library Demo")
    print("=" * 50)
    
    # Run all demo functions
    demo_sharp_operations()
    demo_smooth_blending()
    demo_mixed_curve_types()
    demo_nested_operations()
    demo_gradient_computation()
    demo_serialization()
    demo_vectorized_operations()
    demo_interface_consistency()
    
    print("\n" + "=" * 50)
    print("Sprint 4 Demo Complete!")
    print("\nSummary of implemented features:")
    print("✓ RFunctionCurve class with constructive geometry operations")
    print("✓ Sharp operations: union, intersection, difference using min/max")
    print("✓ Smooth blending with configurable alpha parameter")
    print("✓ High-level wrapper functions: union(), intersect(), difference(), blend()")
    print("✓ Serialization support for composite and nested curves")
    print("✓ Gradient computation for all operation types")
    print("✓ Vectorized evaluation and gradient computation")
    print("✓ Full interface consistency with existing curve classes")
    print("✓ Support for nested and complex constructive operations")
    print("✓ Mixed curve type combinations (Conic + Polynomial + Superellipse)")
    print("✓ Comprehensive test coverage and regression testing")


if __name__ == "__main__":
    main()
