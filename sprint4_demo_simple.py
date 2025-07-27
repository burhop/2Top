"""
Sprint 4 Demo - Simple Version - Constructive Geometry via R-Functions

This is a simplified demo that showcases the core functionality implemented in Sprint 4:
- RFunctionCurve class for constructive solid geometry operations
- Sharp operations: union, intersection, difference using min/max
- Smooth blending operations with configurable alpha parameter
- High-level wrapper functions for convenient curve construction
"""

import sympy as sp
import numpy as np
from geometry import (
    ConicSection, PolynomialCurve, Superellipse, RFunctionCurve,
    union, intersect, difference, blend
)


def demo_basic_operations():
    """Demonstrate basic constructive geometry operations"""
    print("=== Basic Operations Demo ===")
    
    # Create base curves
    x, y = sp.symbols('x y')
    circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))  # Circle at origin
    circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))  # Circle at (1,0)
    
    print("\nBase curves:")
    print(f"  Circle 1: {circle1.expression} = 0")
    print(f"  Circle 2: {circle2.expression} = 0")
    
    # Create operations using wrapper functions
    union_curve = union(circle1, circle2)
    intersection_curve = intersect(circle1, circle2)
    difference_curve = difference(circle1, circle2)
    blend_curve = blend(circle1, circle2, alpha=0.5)
    
    print(f"\nOperations created:")
    print(f"  Union: {union_curve}")
    print(f"  Intersection: {intersection_curve}")
    print(f"  Difference: {difference_curve}")
    print(f"  Blend (α=0.5): {blend_curve}")
    
    # Test evaluation at key points
    test_points = [
        (0.0, 0.0, "Origin"),
        (0.5, 0.0, "Overlap region"),
        (1.0, 0.0, "Between circles"),
        (-0.5, 0.0, "Inside circle1 only"),
        (1.5, 0.0, "Inside circle2 only")
    ]
    
    print(f"\nEvaluation results:")
    print(f"{'Point':<15} {'Union':<8} {'Intersect':<10} {'Difference':<10} {'Blend':<8}")
    print("-" * 60)
    
    for x_val, y_val, desc in test_points:
        union_val = union_curve.evaluate(x_val, y_val)
        intersect_val = intersection_curve.evaluate(x_val, y_val)
        diff_val = difference_curve.evaluate(x_val, y_val)
        blend_val = blend_curve.evaluate(x_val, y_val)
        
        print(f"({x_val:4.1f}, {y_val:4.1f}){'':<5} {union_val:7.3f}  {intersect_val:9.3f}  {diff_val:9.3f}  {blend_val:7.3f}  {desc}")


def demo_mixed_curve_types():
    """Demonstrate operations with different curve types"""
    print("\n=== Mixed Curve Types Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create different curve types
    conic = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    polynomial = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    superellipse = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))
    
    print(f"\nDifferent curve types:")
    print(f"  Conic: {conic.expression} = 0")
    print(f"  Polynomial: {polynomial.expression} = 0")
    print(f"  Superellipse: {superellipse}")
    
    # Create mixed operations
    mixed_union = union(conic, polynomial)
    mixed_intersect = intersect(conic, superellipse)
    mixed_blend = blend(polynomial, superellipse, alpha=0.3)
    
    print(f"\nMixed operations at (0.5, 0.5):")
    print(f"  Conic ∪ Polynomial: {mixed_union.evaluate(0.5, 0.5):.6f}")
    print(f"  Conic ∩ Superellipse: {mixed_intersect.evaluate(0.5, 0.5):.6f}")
    print(f"  Blend(Polynomial, Superellipse, α=0.3): {mixed_blend.evaluate(0.5, 0.5):.6f}")


def demo_serialization():
    """Demonstrate serialization of composite curves"""
    print("\n=== Serialization Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create base curves
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    ellipse = ConicSection(x**2/4 + y**2 - 1, variables=(x, y))
    
    # Create composite curve
    blend_curve = blend(circle, ellipse, alpha=0.5)
    
    print(f"Original curve: {blend_curve}")
    print(f"  Operation: {blend_curve.operation}")
    print(f"  Alpha: {blend_curve.alpha}")
    
    # Serialize
    serialized = blend_curve.to_dict()
    print(f"\nSerialized successfully: {serialized['type']}")
    
    # Deserialize
    restored = RFunctionCurve.from_dict(serialized)
    print(f"Restored curve: {restored}")
    
    # Test functional equivalence
    test_points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
    print(f"\nFunctional equivalence test:")
    
    all_match = True
    for x_val, y_val in test_points:
        orig_val = blend_curve.evaluate(x_val, y_val)
        rest_val = restored.evaluate(x_val, y_val)
        diff = abs(orig_val - rest_val)
        match = diff < 1e-10
        all_match = all_match and match
        print(f"  ({x_val:4.1f}, {y_val:4.1f}): original={orig_val:.6f}, restored={rest_val:.6f}, diff={diff:.2e}")
    
    if all_match:
        print("✓ Serialization round-trip successful!")
    else:
        print("✗ Serialization round-trip failed!")


def demo_nested_operations():
    """Demonstrate nested constructive operations"""
    print("\n=== Nested Operations Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create base shapes
    circle1 = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    circle2 = ConicSection((x-1)**2 + y**2 - 1, variables=(x, y))
    circle3 = ConicSection((x-0.5)**2 + (y-0.5)**2 - 0.25, variables=(x, y))
    
    print(f"Base shapes:")
    print(f"  Circle 1: centered at origin, radius 1")
    print(f"  Circle 2: centered at (1,0), radius 1")
    print(f"  Circle 3: centered at (0.5,0.5), radius 0.5")
    
    # Create nested operations
    # (Circle1 ∪ Circle2) ∩ Circle3
    union_12 = union(circle1, circle2)
    nested_1 = intersect(union_12, circle3)
    
    print(f"\nNested operation: (Circle1 ∪ Circle2) ∩ Circle3")
    print(f"  Type: {type(nested_1).__name__}")
    print(f"  Operation: {nested_1.operation}")
    print(f"  Child 1 type: {type(nested_1.curve1).__name__}")
    print(f"  Child 1 operation: {nested_1.curve1.operation}")
    
    # Circle1 - blend(Circle2, Circle3, α=0.5)
    blend_23 = blend(circle2, circle3, alpha=0.5)
    nested_2 = difference(circle1, blend_23)
    
    print(f"\nNested operation: Circle1 - blend(Circle2, Circle3, α=0.5)")
    print(f"  Type: {type(nested_2).__name__}")
    print(f"  Operation: {nested_2.operation}")
    print(f"  Child 2 type: {type(nested_2.curve2).__name__}")
    print(f"  Child 2 operation: {nested_2.curve2.operation}")
    print(f"  Child 2 alpha: {nested_2.curve2.alpha}")
    
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


def demo_interface_consistency():
    """Demonstrate interface consistency with other curve types"""
    print("\n=== Interface Consistency Demo ===")
    
    x, y = sp.symbols('x y')
    
    # Create different curve types including RFunctionCurve
    from geometry import ImplicitCurve
    
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
    required_methods = ['evaluate', 'gradient', 'normal', 'to_dict']
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
    print("Sprint 4 Geometry Library Demo - Simple Version")
    print("=" * 55)
    
    # Run all demo functions
    demo_basic_operations()
    demo_mixed_curve_types()
    demo_serialization()
    demo_nested_operations()
    demo_gradient_computation()
    demo_interface_consistency()
    
    print("\n" + "=" * 55)
    print("Sprint 4 Demo Complete!")
    print("\nSummary of implemented features:")
    print("✓ RFunctionCurve class with constructive geometry operations")
    print("✓ Sharp operations: union, intersection, difference using min/max")
    print("✓ Smooth blending with configurable alpha parameter")
    print("✓ High-level wrapper functions: union(), intersect(), difference(), blend()")
    print("✓ Serialization support for composite and nested curves")
    print("✓ Gradient computation for all operation types")
    print("✓ Full interface consistency with existing curve classes")
    print("✓ Support for nested and complex constructive operations")
    print("✓ Mixed curve type combinations (Conic + Polynomial + Superellipse)")


if __name__ == "__main__":
    main()
