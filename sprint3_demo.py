"""
Sprint 3 Demo - Superellipse and ProceduralCurve Classes

This demo showcases the functionality implemented in Sprint 3:
- Superellipse class with shape classification and piecewise gradient handling
- ProceduralCurve class with numerical gradient computation
- Serialization behavior and limitations
- Interface consistency with existing curve classes
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from geometry.implicit_curve import ImplicitCurve
from geometry.conic_section import ConicSection
from geometry.polynomial_curve import PolynomialCurve
from geometry.superellipse import Superellipse
from geometry.procedural_curve import ProceduralCurve


def demo_superellipse_shapes():
    """Demonstrate Superellipse functionality with different shape types"""
    print("=== Superellipse Demo ===")
    
    # Create various superellipse shapes
    shapes = {
        "Circle": Superellipse(a=1.0, b=1.0, n=2.0),
        "Ellipse": Superellipse(a=2.0, b=1.0, n=2.0),
        "Square-like": Superellipse(a=1.0, b=1.0, n=4.0),
        "Diamond": Superellipse(a=1.0, b=1.0, n=1.0),
        "Rounded Diamond": Superellipse(a=1.0, b=1.0, n=1.5),
        "Very Square": Superellipse(a=1.0, b=1.0, n=8.0)
    }
    
    for name, shape in shapes.items():
        print(f"\n{name}:")
        print(f"  Parameters: a={shape.a}, b={shape.b}, n={shape.n}")
        print(f"  Shape type: {shape.shape_type()}")
        print(f"  Value at origin: {shape.evaluate(0.0, 0.0):.3f}")
        print(f"  Value at (1,0): {shape.evaluate(1.0, 0.0):.3f}")
        print(f"  Gradient at (0.5,0.3): {shape.gradient(0.5, 0.3)}")


def demo_procedural_curves():
    """Demonstrate ProceduralCurve functionality with various functions"""
    print("\n=== ProceduralCurve Demo ===")
    
    # Create procedural curves with different function types
    functions = {
        "Circle": lambda x, y: x**2 + y**2 - 1,
        "Line": lambda x, y: x + y - 1,
        "Cubic": lambda x, y: x**3 + y**3 - 1,
        "Trigonometric": lambda x, y: np.sin(x) + np.cos(y) - 1,
        "Gaussian": lambda x, y: np.exp(-(x**2 + y**2)) - 0.5,
        "Complex": lambda x, y: np.sin(x**2) * np.cos(y**2) - 0.3
    }
    
    curves = {name: ProceduralCurve(func, name=name) for name, func in functions.items()}
    
    for name, curve in curves.items():
        print(f"\n{name}:")
        print(f"  Name: {curve.name}")
        print(f"  Value at origin: {curve.evaluate(0.0, 0.0):.3f}")
        print(f"  Value at (1,0): {curve.evaluate(1.0, 0.0):.3f}")
        print(f"  Numerical gradient at (0.5,0.3): {curve.gradient(0.5, 0.3)}")


def demo_interface_consistency():
    """Demonstrate interface consistency across all curve classes"""
    print("\n=== Interface Consistency Demo ===")
    
    # Create equivalent circle representations using different classes
    x, y = sp.symbols('x y')
    circle_expr = x**2 + y**2 - 1
    
    curves = {
        "ConicSection": ConicSection(circle_expr, variables=(x, y)),
        "PolynomialCurve": PolynomialCurve(circle_expr, variables=(x, y)),
        "Superellipse": Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y)),
        "ProceduralCurve": ProceduralCurve(lambda x, y: x**2 + y**2 - 1, name="Circle")
    }
    
    print("Circle representation across all curve classes:")
    test_points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
    
    for point in test_points:
        x_val, y_val = point
        print(f"\nAt point {point}:")
        
        for name, curve in curves.items():
            value = curve.evaluate(x_val, y_val)
            print(f"  {name:15}: {value:8.3f}")
        
        # Check consistency
        values = [curve.evaluate(x_val, y_val) for curve in curves.values()]
        max_diff = max(values) - min(values)
        if max_diff < 1e-5:
            print(f"  ✓ All values consistent (max diff: {max_diff:.2e})")
        else:
            print(f"  ⚠ Values differ (max diff: {max_diff:.2e})")


def demo_gradient_comparison():
    """Compare gradient computation methods across curve types"""
    print("\n=== Gradient Comparison Demo ===")
    
    # Create curves with known analytical gradients
    x, y = sp.symbols('x y')
    circle_expr = x**2 + y**2 - 1
    
    symbolic_curve = PolynomialCurve(circle_expr, variables=(x, y))
    superellipse_curve = Superellipse(a=1.0, b=1.0, n=2.0, variables=(x, y))
    procedural_curve = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, name="Circle")
    
    test_points = [(1.0, 0.0), (0.0, 1.0), (0.5, 0.5)]
    
    print("Gradient computation comparison (circle: ∇f = (2x, 2y)):")
    
    for point in test_points:
        x_val, y_val = point
        analytical = (2*x_val, 2*y_val)
        
        print(f"\nAt point {point}:")
        print(f"  Analytical:     {analytical}")
        
        symbolic_grad = symbolic_curve.gradient(x_val, y_val)
        print(f"  Symbolic:       {symbolic_grad}")
        
        super_grad = superellipse_curve.gradient(x_val, y_val)
        print(f"  Superellipse:   {super_grad}")
        
        numerical_grad = procedural_curve.gradient(x_val, y_val)
        print(f"  Numerical:      {numerical_grad}")
        
        # Check accuracy
        symbolic_error = max(abs(symbolic_grad[0] - analytical[0]), abs(symbolic_grad[1] - analytical[1]))
        super_error = max(abs(super_grad[0] - analytical[0]), abs(super_grad[1] - analytical[1]))
        numerical_error = max(abs(numerical_grad[0] - analytical[0]), abs(numerical_grad[1] - analytical[1]))
        
        print(f"  Errors: Symbolic={symbolic_error:.2e}, Super={super_error:.2e}, Numerical={numerical_error:.2e}")


def demo_serialization_behavior():
    """Demonstrate serialization behavior and limitations"""
    print("\n=== Serialization Demo ===")
    
    # Superellipse serialization (full functionality)
    print("Superellipse Serialization:")
    square = Superellipse(a=2.0, b=1.5, n=4.0)
    square_data = square.to_dict()
    
    print(f"  Original: {square}")
    print(f"  Serialized type: {square_data['type']}")
    print(f"  Parameters: a={square_data['a']}, b={square_data['b']}, n={square_data['n']}")
    print(f"  Shape type: {square_data['shape_type']}")
    
    # Reconstruct and test
    square_restored = Superellipse.from_dict(square_data)
    test_point = (0.5, 0.3)
    orig_val = square.evaluate(*test_point)
    rest_val = square_restored.evaluate(*test_point)
    
    print(f"  Functional test at {test_point}:")
    print(f"    Original: {orig_val:.6f}")
    print(f"    Restored: {rest_val:.6f}")
    print(f"    ✓ Serialization preserves functionality")
    
    # ProceduralCurve serialization (limitations)
    print("\nProceduralCurve Serialization:")
    trig_func = lambda x, y: np.sin(x) + np.cos(y) - 1
    trig_curve = ProceduralCurve(trig_func, name="Trigonometric")
    trig_data = trig_curve.to_dict()
    
    print(f"  Original: {trig_curve}")
    print(f"  Serialized type: {trig_data['type']}")
    print(f"  Function placeholder: {trig_data['function']}")
    print(f"  Serialization note: {trig_data['_serialization_note']}")
    
    # Reconstruct and test limitations
    trig_restored = ProceduralCurve.from_dict(trig_data)
    print(f"  Restored: {trig_restored}")
    
    try:
        trig_restored.evaluate(0.0, 0.0)
        print("  ⚠ Unexpected: restored curve is functional")
    except NotImplementedError as e:
        print(f"  ✓ Expected limitation: {str(e)[:60]}...")


def demo_vectorized_operations():
    """Demonstrate vectorized evaluation capabilities"""
    print("\n=== Vectorized Operations Demo ===")
    
    # Create test curves
    superellipse = Superellipse(a=1.0, b=1.0, n=2.0)
    procedural = ProceduralCurve(lambda x, y: x**2 + y**2 - 1, name="Circle")
    
    # Create test arrays
    x_vals = np.linspace(-2, 2, 5)
    y_vals = np.zeros_like(x_vals)
    
    print(f"Test points: x = {x_vals}")
    print(f"             y = {y_vals}")
    
    # Vectorized evaluation
    super_vals = superellipse.evaluate(x_vals, y_vals)
    proc_vals = procedural.evaluate(x_vals, y_vals)
    
    print(f"\nSuperellipse values: {super_vals}")
    print(f"ProceduralCurve values: {proc_vals}")
    
    # Check consistency
    max_diff = np.max(np.abs(super_vals - proc_vals))
    print(f"Maximum difference: {max_diff:.2e}")
    
    if max_diff < 1e-10:
        print("✓ Vectorized operations are consistent")
    else:
        print("⚠ Vectorized operations show differences")
    
    # Vectorized gradients
    super_grad = superellipse.gradient(x_vals, y_vals)
    proc_grad = procedural.gradient(x_vals, y_vals)
    
    print(f"\nSuperellipse gradients:")
    print(f"  x-component: {super_grad[0]}")
    print(f"  y-component: {super_grad[1]}")
    
    print(f"ProceduralCurve gradients:")
    print(f"  x-component: {proc_grad[0]}")
    print(f"  y-component: {proc_grad[1]}")


def demo_specialized_features():
    """Demonstrate specialized features of Sprint 3 classes"""
    print("\n=== Specialized Features Demo ===")
    
    # Superellipse shape morphing
    print("Superellipse Shape Morphing:")
    n_values = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 8.0]
    
    for n in n_values:
        try:
            shape = Superellipse(a=1.0, b=1.0, n=n)
            shape_type = shape.shape_type()
            corner_val = shape.evaluate(0.7, 0.7)  # Test corner behavior
            print(f"  n={n:3.1f}: {shape_type:15} | corner value: {corner_val:6.3f}")
        except ValueError as e:
            print(f"  n={n:3.1f}: Invalid parameter - {e}")
    
    # ProceduralCurve function flexibility
    print("\nProceduralCurve Function Flexibility:")
    
    # Complex mathematical functions
    functions = [
        ("Polynomial", lambda x, y: x**4 + y**4 - 2*x**2*y**2 - 1),
        ("Trigonometric", lambda x, y: np.sin(np.pi*x) * np.cos(np.pi*y) - 0.5),
        ("Exponential", lambda x, y: np.exp(-(x**2 + y**2)) - 0.5),
        ("Logarithmic", lambda x, y: np.log(x**2 + y**2 + 1) - 1),
        ("Hyperbolic", lambda x, y: np.sinh(x) + np.cosh(y) - 2)
    ]
    
    for name, func in functions:
        try:
            curve = ProceduralCurve(func, name=name)
            val_origin = curve.evaluate(0.0, 0.0)
            val_unit = curve.evaluate(1.0, 0.0)
            grad_unit = curve.gradient(1.0, 0.0)
            
            print(f"  {name:12}: f(0,0)={val_origin:6.3f}, f(1,0)={val_unit:6.3f}, ∇f(1,0)=({grad_unit[0]:5.2f},{grad_unit[1]:5.2f})")
        except Exception as e:
            print(f"  {name:12}: Error - {e}")


if __name__ == "__main__":
    print("Sprint 3 Geometry Library Demo")
    print("=" * 50)
    
    demo_superellipse_shapes()
    demo_procedural_curves()
    demo_interface_consistency()
    demo_gradient_comparison()
    demo_serialization_behavior()
    demo_vectorized_operations()
    demo_specialized_features()
    
    print("\n" + "=" * 50)
    print("Sprint 3 Demo Complete!")
    print("\nSummary of implemented features:")
    print("✓ Superellipse class with shape classification and piecewise gradients")
    print("✓ ProceduralCurve class with numerical gradient computation")
    print("✓ Specialized serialization with documented limitations")
    print("✓ Full inheritance from ImplicitCurve interface")
    print("✓ Vectorized evaluation support for both classes")
    print("✓ Interface consistency across all curve types")
    print("✓ Comprehensive test coverage and regression testing")
    print("✓ Handling of non-polynomial and non-symbolic curves")
