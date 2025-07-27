"""
Sprint 2 Demo - ConicSection and PolynomialCurve Classes

This demo showcases the functionality implemented in Sprint 2:
- ConicSection class with conic type classification
- PolynomialCurve class with degree computation
- Serialization and deserialization
- Interface consistency with ImplicitCurve
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve


def demo_conic_sections():
    """Demonstrate ConicSection functionality"""
    print("=== ConicSection Demo ===")
    x, y = sp.symbols('x y')
    
    # Create various conic sections
    conics = {
        "Circle": ConicSection(x**2 + y**2 - 1, variables=(x, y)),
        "Ellipse": ConicSection(x**2/4 + y**2 - 1, variables=(x, y)),
        "Hyperbola": ConicSection(x**2 - y**2 - 1, variables=(x, y)),
        "Parabola": ConicSection(y - x**2, variables=(x, y))
    }
    
    for name, conic in conics.items():
        print(f"\n{name}:")
        print(f"  Expression: {conic}")
        print(f"  Type: {conic.conic_type()}")
        print(f"  Degree: {conic.degree()}")
        print(f"  Value at origin: {conic.evaluate(0.0, 0.0):.3f}")
        print(f"  Gradient at (1,0): {conic.gradient(1.0, 0.0)}")


def demo_polynomial_curves():
    """Demonstrate PolynomialCurve functionality"""
    print("\n=== PolynomialCurve Demo ===")
    x, y = sp.symbols('x y')
    
    # Create polynomial curves of various degrees
    polynomials = {
        "Line": PolynomialCurve(x + y - 1, variables=(x, y)),
        "Circle": PolynomialCurve(x**2 + y**2 - 1, variables=(x, y)),
        "Cubic": PolynomialCurve(x**3 + y**3 - 1, variables=(x, y)),
        "Quartic": PolynomialCurve(x**4 + y**4 - 2*x**2*y**2 - 1, variables=(x, y)),
        "Mixed Terms": PolynomialCurve(x**3*y + x*y**3 - 1, variables=(x, y))
    }
    
    for name, poly in polynomials.items():
        print(f"\n{name}:")
        print(f"  Expression: {poly}")
        print(f"  Degree: {poly.degree()}")
        print(f"  Value at origin: {poly.evaluate(0.0, 0.0):.3f}")
        print(f"  Gradient at (1,0): {poly.gradient(1.0, 0.0)}")


def demo_interface_consistency():
    """Demonstrate interface consistency between classes"""
    print("\n=== Interface Consistency Demo ===")
    x, y = sp.symbols('x y')
    
    # Same expression represented by both classes
    expr = x**2 + y**2 - 1
    conic_circle = ConicSection(expr, variables=(x, y))
    poly_circle = PolynomialCurve(expr, variables=(x, y))
    
    print(f"Expression: {expr} = 0")
    print(f"ConicSection type: {conic_circle.conic_type()}")
    print(f"PolynomialCurve degree: {poly_circle.degree()}")
    
    # Test points
    test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    
    print("\nEvaluation consistency:")
    for x_val, y_val in test_points:
        conic_val = conic_circle.evaluate(x_val, y_val)
        poly_val = poly_circle.evaluate(x_val, y_val)
        print(f"  At ({x_val}, {y_val}): ConicSection={conic_val:.3f}, PolynomialCurve={poly_val:.3f}")
        assert abs(conic_val - poly_val) < 1e-10, "Values should be identical!"
    
    print("✓ All evaluations are consistent!")


def demo_serialization():
    """Demonstrate serialization functionality"""
    print("\n=== Serialization Demo ===")
    x, y = sp.symbols('x y')
    
    # Create test curves
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    # Serialize
    circle_data = circle.to_dict()
    cubic_data = cubic.to_dict()
    
    print("Serialized ConicSection:")
    print(f"  Type: {circle_data['type']}")
    print(f"  Conic Type: {circle_data['conic_type']}")
    print(f"  Expression: {circle_data['expression']}")
    
    print("\nSerialized PolynomialCurve:")
    print(f"  Type: {cubic_data['type']}")
    print(f"  Degree: {cubic_data['degree']}")
    print(f"  Expression: {cubic_data['expression']}")
    
    # Deserialize
    circle_restored = ConicSection.from_dict(circle_data)
    cubic_restored = PolynomialCurve.from_dict(cubic_data)
    
    # Test functional equivalence
    test_point = (0.5, 0.5)
    
    circle_orig = circle.evaluate(*test_point)
    circle_rest = circle_restored.evaluate(*test_point)
    
    cubic_orig = cubic.evaluate(*test_point)
    cubic_rest = cubic_restored.evaluate(*test_point)
    
    print(f"\nFunctional equivalence test at {test_point}:")
    print(f"  Circle: original={circle_orig:.6f}, restored={circle_rest:.6f}")
    print(f"  Cubic: original={cubic_orig:.6f}, restored={cubic_rest:.6f}")
    
    assert abs(circle_orig - circle_rest) < 1e-10, "Circle serialization failed!"
    assert abs(cubic_orig - cubic_rest) < 1e-10, "Cubic serialization failed!"
    
    print("✓ Serialization round-trip successful!")


def demo_vectorized_evaluation():
    """Demonstrate vectorized evaluation capabilities"""
    print("\n=== Vectorized Evaluation Demo ===")
    x, y = sp.symbols('x y')
    
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    # Create test arrays
    x_vals = np.linspace(-2, 2, 5)
    y_vals = np.zeros_like(x_vals)
    
    print(f"Test points: x = {x_vals}")
    print(f"             y = {y_vals}")
    
    # Vectorized evaluation
    circle_vals = circle.evaluate(x_vals, y_vals)
    cubic_vals = cubic.evaluate(x_vals, y_vals)
    
    print(f"\nCircle values: {circle_vals}")
    print(f"Cubic values:  {cubic_vals}")
    
    # Find zero crossings (approximate)
    circle_zeros = x_vals[np.abs(circle_vals) < 0.1]
    cubic_zeros = x_vals[np.abs(cubic_vals) < 0.1]
    
    print(f"\nApproximate zeros:")
    print(f"  Circle: x ≈ {circle_zeros}")
    print(f"  Cubic: x ≈ {cubic_zeros}")


def demo_inheritance():
    """Demonstrate inheritance from ImplicitCurve"""
    print("\n=== Inheritance Demo ===")
    x, y = sp.symbols('x y')
    
    circle = ConicSection(x**2 + y**2 - 1, variables=(x, y))
    cubic = PolynomialCurve(x**3 + y**3 - 1, variables=(x, y))
    
    curves = [circle, cubic]
    
    for i, curve in enumerate(curves, 1):
        curve_type = type(curve).__name__
        print(f"\nCurve {i} ({curve_type}):")
        print(f"  Is ImplicitCurve: {isinstance(curve, ImplicitCurve)}")
        print(f"  Has evaluate method: {hasattr(curve, 'evaluate')}")
        print(f"  Has gradient method: {hasattr(curve, 'gradient')}")
        print(f"  Has normal method: {hasattr(curve, 'normal')}")
        print(f"  Has plot method: {hasattr(curve, 'plot')}")
        print(f"  Has to_dict method: {hasattr(curve, 'to_dict')}")
        print(f"  Has from_dict method: {hasattr(curve, 'from_dict')}")
        
        # Test normal computation
        try:
            normal = curve.normal(1.0, 0.0)
            print(f"  Normal at (1,0): {normal}")
        except ValueError as e:
            print(f"  Normal computation: {e}")


if __name__ == "__main__":
    print("Sprint 2 Geometry Library Demo")
    print("=" * 50)
    
    demo_conic_sections()
    demo_polynomial_curves()
    demo_interface_consistency()
    demo_serialization()
    demo_vectorized_evaluation()
    demo_inheritance()
    
    print("\n" + "=" * 50)
    print("Sprint 2 Demo Complete!")
    print("\nSummary of implemented features:")
    print("✓ ConicSection class with conic type classification")
    print("✓ PolynomialCurve class with degree computation")
    print("✓ Specialized serialization for both classes")
    print("✓ Full inheritance from ImplicitCurve interface")
    print("✓ Vectorized evaluation support")
    print("✓ Comprehensive test coverage")
    print("✓ Interface consistency between classes")
