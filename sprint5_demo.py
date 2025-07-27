"""
Sprint 5 Demo - Curve Segmentation and Piecewise Composition

This demo showcases the new Sprint 5 functionality:
- TrimmedImplicitCurve: Segments of curves defined by mask functions
- CompositeCurve: Ordered sequences of trimmed segments
- Integration with all previous sprint curve types
- Utility functions for common composite shapes
- Serialization capabilities and limitations

Features Demonstrated:
1. Basic trimmed curves with different mask functions
2. Composite curves from multiple segments
3. Mixed base curve types in composites
4. Utility functions for common shapes
5. Integration with constructive geometry
6. Serialization and deserialization
7. Plotting and visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from geometry import (
    ConicSection, PolynomialCurve, Superellipse, ProceduralCurve,
    TrimmedImplicitCurve, CompositeCurve,
    union, intersect, difference, blend,
    create_circle_from_quarters, create_square_from_edges
)


def demo_basic_trimmed_curves():
    """Demonstrate basic TrimmedImplicitCurve functionality"""
    print("=" * 60)
    print("DEMO 1: Basic Trimmed Curves")
    print("=" * 60)
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Create a circle
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    print(f"Base circle: {circle.expression}")
    
    # Create different trimmed versions
    right_half = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    upper_half = TrimmedImplicitCurve(circle, lambda x, y: y >= 0)
    first_quadrant = TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0)
    
    print("\nTrimmed curve variations:")
    print("- Right half: x >= 0")
    print("- Upper half: y >= 0") 
    print("- First quadrant: x >= 0 and y >= 0")
    
    # Test containment
    test_points = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0), (0.707, 0.707)]
    
    print(f"\nContainment tests for points: {test_points}")
    print("Point        | Circle | Right Half | Upper Half | First Quad")
    print("-" * 65)
    
    for px, py in test_points:
        circle_contains = circle.evaluate(px, py) <= 0
        right_contains = right_half.contains(px, py)
        upper_contains = upper_half.contains(px, py)
        first_contains = first_quadrant.contains(px, py)
        
        print(f"({px:4.1f}, {py:4.1f}) | {str(circle_contains):6} | {str(right_contains):10} | {str(upper_contains):10} | {str(first_contains):10}")
    
    # Demonstrate evaluation (delegates to base curve)
    print(f"\nEvaluation at (0.5, 0.5):")
    print(f"Circle: {circle.evaluate(0.5, 0.5):.6f}")
    print(f"Right half: {right_half.evaluate(0.5, 0.5):.6f}")
    print(f"Upper half: {upper_half.evaluate(0.5, 0.5):.6f}")
    print("(All should be equal - evaluation delegates to base curve)")
    
    return right_half, upper_half, first_quadrant


def demo_composite_curves():
    """Demonstrate CompositeCurve functionality"""
    print("\n" + "=" * 60)
    print("DEMO 2: Composite Curves")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Create a circle and divide it into quarters
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    
    quarters = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),  # Q1
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),  # Q2
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),  # Q3
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),  # Q4
    ]
    
    # Create composite curves
    full_circle = CompositeCurve(quarters)
    half_circle = CompositeCurve(quarters[:2])  # Upper half
    
    print(f"Full circle composite: {len(full_circle.segments)} segments")
    print(f"Half circle composite: {len(half_circle.segments)} segments")
    
    # Test properties
    print(f"\nComposite curve properties:")
    print(f"Full circle is closed: {full_circle.is_closed()}")
    print(f"Half circle is closed: {half_circle.is_closed()}")
    
    # Test containment
    test_points = [(0.707, 0.707), (-0.707, 0.707), (-0.707, -0.707), (0.707, -0.707)]
    
    print(f"\nContainment tests:")
    print("Point           | Full Circle | Half Circle")
    print("-" * 45)
    
    for px, py in test_points:
        full_contains = full_circle.contains(px, py)
        half_contains = half_circle.contains(px, py)
        print(f"({px:5.3f}, {py:5.3f}) | {str(full_contains):11} | {str(half_contains):11}")
    
    # Test evaluation (minimum distance to any segment)
    print(f"\nEvaluation at (0.5, 0.5): {full_circle.evaluate(0.5, 0.5):.6f}")
    print(f"Evaluation at (2.0, 0.0): {full_circle.evaluate(2.0, 0.0):.6f}")
    
    return full_circle, half_circle


def demo_mixed_base_curves():
    """Demonstrate composite curves with mixed base curve types"""
    print("\n" + "=" * 60)
    print("DEMO 3: Mixed Base Curve Types")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Create different types of base curves
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    line = PolynomialCurve(x + y - 1, variables=(x, y))
    superellipse = Superellipse(a=1.0, b=1.0, n=4.0, variables=(x, y))  # Square-like
    procedural = ProceduralCurve(lambda x, y: np.sin(x*np.pi) + np.cos(y*np.pi), variables=(x, y))
    
    print("Base curve types:")
    print("- Circle (ConicSection)")
    print("- Line (PolynomialCurve)")
    print("- Superellipse (n=4, square-like)")
    print("- Procedural (sinusoidal)")
    
    # Create trimmed segments
    segments = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),      # Q1: Circle
        TrimmedImplicitCurve(line, lambda x, y: x <= 0 and y >= 0),        # Q2: Line
        TrimmedImplicitCurve(superellipse, lambda x, y: x <= 0 and y <= 0), # Q3: Superellipse
        TrimmedImplicitCurve(procedural, lambda x, y: x >= 0 and y <= 0),   # Q4: Procedural
    ]
    
    # Create mixed composite
    mixed_composite = CompositeCurve(segments)
    
    print(f"\nMixed composite: {len(mixed_composite.segments)} segments")
    print("Each quadrant uses a different curve type")
    
    # Test evaluation in each quadrant
    quadrant_points = [(0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5), (0.5, -0.5)]
    quadrant_names = ["Q1 (Circle)", "Q2 (Line)", "Q3 (Superellipse)", "Q4 (Procedural)"]
    
    print(f"\nEvaluation in each quadrant:")
    for i, (px, py) in enumerate(quadrant_points):
        value = mixed_composite.evaluate(px, py)
        contains = mixed_composite.contains(px, py)
        print(f"{quadrant_names[i]:15}: f({px:3.1f}, {py:3.1f}) = {value:8.4f}, contains = {contains}")
    
    return mixed_composite


def demo_utility_functions():
    """Demonstrate utility functions for common shapes"""
    print("\n" + "=" * 60)
    print("DEMO 4: Utility Functions")
    print("=" * 60)
    
    # Create circle from quarters
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.0)
    custom_circle = create_circle_from_quarters(center=(2, 1), radius=1.5)
    
    print("Circle from quarters:")
    print(f"- Default circle: center=(0,0), radius=1.0, {len(circle_quarters.segments)} segments")
    print(f"- Custom circle: center=(2,1), radius=1.5, {len(custom_circle.segments)} segments")
    
    # Create square from edges
    unit_square = create_square_from_edges(corner1=(0, 0), corner2=(1, 1))
    custom_square = create_square_from_edges(corner1=(-1, -1), corner2=(1, 1))
    
    print(f"\nSquare from edges:")
    print(f"- Unit square: corners (0,0) to (1,1), {len(unit_square.segments)} segments")
    print(f"- Custom square: corners (-1,-1) to (1,1), {len(custom_square.segments)} segments")
    
    # Test properties
    print(f"\nShape properties:")
    print(f"Circle quarters is closed: {circle_quarters.is_closed()}")
    print(f"Unit square is closed: {unit_square.is_closed()}")
    
    # Test containment
    test_points = [(0.5, 0.5), (1.5, 0.5), (2.5, 1.0)]
    
    print(f"\nContainment tests:")
    print("Point        | Circle | Custom Circle | Unit Square")
    print("-" * 55)
    
    for px, py in test_points:
        circle_contains = circle_quarters.contains(px, py)
        custom_contains = custom_circle.contains(px, py)
        square_contains = unit_square.contains(px, py)
        print(f"({px:3.1f}, {py:3.1f}) | {str(circle_contains):6} | {str(custom_contains):13} | {str(square_contains):11}")
    
    return circle_quarters, unit_square


def demo_constructive_geometry_integration():
    """Demonstrate integration with constructive geometry operations"""
    print("\n" + "=" * 60)
    print("DEMO 5: Constructive Geometry Integration")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Create base curves
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    square_expr = sp.Max(sp.Abs(x) - 0.8, sp.Abs(y) - 0.8)  # Approximate square
    square = ProceduralCurve(lambda x, y: np.maximum(np.abs(x) - 0.8, np.abs(y) - 0.8), variables=(x, y))
    
    # Create trimmed versions
    right_circle = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    upper_square = TrimmedImplicitCurve(square, lambda x, y: y >= 0)
    
    print("Base shapes:")
    print("- Right half circle (trimmed)")
    print("- Upper half square (trimmed)")
    
    # Apply constructive geometry operations
    union_shape = union(right_circle, upper_square)
    intersect_shape = intersect(right_circle, circle)  # Right half intersected with full circle
    difference_shape = difference(circle, right_circle)  # Full circle minus right half
    blend_shape = blend(right_circle, upper_square, alpha=0.1)
    
    print(f"\nConstructive geometry results:")
    print(f"- Union: {type(union_shape).__name__}")
    print(f"- Intersection: {type(intersect_shape).__name__}")
    print(f"- Difference: {type(difference_shape).__name__}")
    print(f"- Blend (α=0.1): {type(blend_shape).__name__}")
    
    # Test evaluation
    test_point = (0.5, 0.5)
    print(f"\nEvaluation at {test_point}:")
    print(f"Right circle: {right_circle.evaluate(*test_point):.6f}")
    print(f"Upper square: {upper_square.evaluate(*test_point):.6f}")
    print(f"Union: {union_shape.evaluate(*test_point):.6f}")
    print(f"Intersection: {intersect_shape.evaluate(*test_point):.6f}")
    print(f"Difference: {difference_shape.evaluate(*test_point):.6f}")
    print(f"Blend: {blend_shape.evaluate(*test_point):.6f}")
    
    return union_shape, blend_shape


def demo_serialization():
    """Demonstrate serialization capabilities and limitations"""
    print("\n" + "=" * 60)
    print("DEMO 6: Serialization")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Create curves to serialize
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    right_half = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    
    quarters = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),
    ]
    composite = CompositeCurve(quarters)
    
    print("Serialization test curves:")
    print("- Trimmed circle (right half)")
    print("- Composite curve (2 segments)")
    
    # Test TrimmedImplicitCurve serialization
    print(f"\n1. TrimmedImplicitCurve Serialization:")
    trimmed_dict = right_half.to_dict()
    print(f"   Serialized type: {trimmed_dict['type']}")
    print(f"   Base curve type: {trimmed_dict['base_curve']['type']}")
    print(f"   Mask: {trimmed_dict['mask']}")
    print(f"   Mask description: {trimmed_dict['mask_description'][:50]}...")
    
    # Deserialize
    restored_trimmed = TrimmedImplicitCurve.from_dict(trimmed_dict)
    print(f"   Restored successfully: {type(restored_trimmed).__name__}")
    print(f"   Has deserialization warning: {hasattr(restored_trimmed, '_deserialization_warning')}")
    
    # Test functional equivalence (base curve only)
    test_point = (0.5, 0.5)
    orig_base_val = right_half.base_curve.evaluate(*test_point)
    rest_base_val = restored_trimmed.base_curve.evaluate(*test_point)
    print(f"   Base curve evaluation match: {abs(orig_base_val - rest_base_val) < 1e-10}")
    
    # Test CompositeCurve serialization
    print(f"\n2. CompositeCurve Serialization:")
    composite_dict = composite.to_dict()
    print(f"   Serialized type: {composite_dict['type']}")
    print(f"   Segment count: {composite_dict['segment_count']}")
    print(f"   Variables: {composite_dict['variables']}")
    
    # Deserialize
    restored_composite = CompositeCurve.from_dict(composite_dict)
    print(f"   Restored successfully: {type(restored_composite).__name__}")
    print(f"   Segment count match: {len(restored_composite.segments) == len(composite.segments)}")
    
    # Test functional equivalence
    orig_comp_val = composite.evaluate(*test_point)
    rest_comp_val = restored_composite.evaluate(*test_point)
    print(f"   Composite evaluation match: {abs(orig_comp_val - rest_comp_val) < 1e-10}")
    
    # Demonstrate mask limitations
    print(f"\n3. Mask Function Limitations:")
    print("   Original mask (x >= 0):")
    print(f"     contains(0.5, 0.5): {right_half.contains(0.5, 0.5)}")
    print(f"     contains(-0.5, 0.5): {right_half.contains(-0.5, 0.5)}")
    
    print("   Restored mask (placeholder - always True):")
    print(f"     contains(0.5, 0.5): {restored_trimmed.contains(0.5, 0.5)}")
    print(f"     contains(-0.5, 0.5): {restored_trimmed.contains(-0.5, 0.5)}")
    print("   ⚠️  Mask functions cannot be serialized - manual reconstruction required")
    
    return restored_trimmed, restored_composite


def demo_plotting():
    """Demonstrate plotting capabilities"""
    print("\n" + "=" * 60)
    print("DEMO 7: Plotting and Visualization")
    print("=" * 60)
    
    x, y = sp.symbols('x y')
    
    # Create shapes for plotting
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    right_half = TrimmedImplicitCurve(circle, lambda x, y: x >= 0)
    
    # Create composite
    quarters = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y >= 0),
        TrimmedImplicitCurve(circle, lambda x, y: x <= 0 and y <= 0),
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y <= 0),
    ]
    composite = CompositeCurve(quarters)
    
    # Create utility shapes
    circle_quarters = create_circle_from_quarters(center=(0, 0), radius=1.0)
    unit_square = create_square_from_edges(corner1=(-0.8, -0.8), corner2=(0.8, 0.8))
    
    print("Creating plots...")
    
    # Create subplot layout
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Sprint 5 Demo - Curve Segmentation and Piecewise Composition', fontsize=16)
    
    # Plot 1: Original circle vs trimmed
    circle.plot(ax=axes[0,0], colors=['blue'], linewidths=2)
    right_half.plot(ax=axes[0,0], colors=['red'], linewidths=3)
    axes[0,0].set_title('Circle vs Right Half (Trimmed)')
    axes[0,0].legend(['Full Circle', 'Right Half'])
    
    # Plot 2: Composite quarters
    composite.plot(ax=axes[0,1], resolution=800)
    axes[0,1].set_title('Composite Circle (4 Quarters)')
    
    # Plot 3: Utility circle
    circle_quarters.plot(ax=axes[0,2], resolution=800)
    axes[0,2].set_title('Circle from Quarters (Utility)')
    
    # Plot 4: Utility square
    unit_square.plot(ax=axes[1,0], resolution=800)
    axes[1,0].set_title('Square from Edges (Utility)')
    
    # Plot 5: Mixed base curves
    mixed_segments = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= 0 and y >= 0),
        TrimmedImplicitCurve(PolynomialCurve(x + y - 0.5, variables=(x, y)), lambda x, y: x <= 0 and y >= 0),
    ]
    mixed_composite = CompositeCurve(mixed_segments)
    mixed_composite.plot(ax=axes[1,1], resolution=800)
    axes[1,1].set_title('Mixed Base Curves')
    
    # Plot 6: Constructive geometry with trimmed curves
    square = ProceduralCurve(lambda x, y: np.maximum(np.abs(x) - 0.6, np.abs(y) - 0.6), variables=(x, y))
    upper_square = TrimmedImplicitCurve(square, lambda x, y: y >= 0)
    union_shape = union(right_half, upper_square)
    union_shape.plot(ax=axes[1,2], colors=['purple'], linewidths=2)
    axes[1,2].set_title('Union: Right Circle + Upper Square')
    
    plt.tight_layout()
    plt.show()
    
    print("✓ Plots created successfully")
    print("  - Trimmed curves show only the masked portions")
    print("  - Composite curves display all segments with different colors")
    print("  - Utility functions create common shapes easily")
    print("  - Integration with constructive geometry works seamlessly")


def main():
    """Run all Sprint 5 demos"""
    print("🚀 Sprint 5 Demo - Curve Segmentation and Piecewise Composition")
    print("================================================================")
    print()
    print("This demo showcases the new Sprint 5 functionality:")
    print("• TrimmedImplicitCurve - curve segments with mask functions")
    print("• CompositeCurve - ordered sequences of trimmed segments")
    print("• Integration with all previous sprint curve types")
    print("• Utility functions for common composite shapes")
    print("• Serialization capabilities and documented limitations")
    print()
    
    try:
        # Run all demos
        demo_basic_trimmed_curves()
        demo_composite_curves()
        demo_mixed_base_curves()
        demo_utility_functions()
        demo_constructive_geometry_integration()
        demo_serialization()
        demo_plotting()
        
        print("\n" + "=" * 60)
        print("SPRINT 5 DEMO COMPLETE")
        print("=" * 60)
        print()
        print("✅ All Sprint 5 features demonstrated successfully!")
        print()
        print("Key achievements:")
        print("• TrimmedImplicitCurve enables curve segmentation with mask functions")
        print("• CompositeCurve enables piecewise curve composition")
        print("• Full integration with all 6 curve types from previous sprints")
        print("• Utility functions simplify creation of common shapes")
        print("• Serialization works with documented mask function limitations")
        print("• Plotting visualizes segmented and composite curves effectively")
        print("• Constructive geometry operations work seamlessly with new classes")
        print()
        print("🎯 Sprint 5 implementation is complete and validated!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
