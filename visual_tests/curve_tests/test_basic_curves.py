"""
Basic curve tests.

Visual tests for fundamental curve types: circles, ellipses, hyperbolas, 
parabolas, and simple polynomial curves.
"""

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from typing import List, Tuple
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from geometry import ConicSection, PolynomialCurve
from visual_tests.utils import PlotManager, CurveFactory, GridEvaluator


def test_basic_conic_sections():
    """
    Test and visualize basic conic sections: circle, ellipse, hyperbola, parabola.
    """
    print("="*60)
    print("Testing Basic Conic Sections")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 2, figsize=(12, 12), 
                                         suptitle='Basic Conic Sections')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Define the curves to test
    curves = [
        ("Circle", CurveFactory.create_circle((0, 0), 2), "x² + y² = 4"),
        ("Ellipse", CurveFactory.create_ellipse((0, 0), 2, 1), "x²/4 + y² = 1"),
        ("Hyperbola", CurveFactory.create_hyperbola((0, 0), 1, 1), "x² - y² = 1"),
        ("Parabola", CurveFactory.create_parabola((0, 0), 'up', 1), "y = x²")
    ]
    
    # Plot each curve
    for i, (name, curve, equation) in enumerate(curves):
        ax = axes[i // 2, i % 2]
        title = f"{name}\\n{equation}"
        
        print(f"Plotting {name}...")
        plot_manager.plot_curve_contour(ax, curve, X, Y, title=title, 
                                       color='blue', show_levels=True)
    
    plot_manager.save_or_show()
    print("✓ Basic conic sections test completed")


def test_polynomial_curves():
    """
    Test and visualize polynomial curves: lines, cubic curves, and complex polynomials.
    """
    print("="*60)
    print("Testing Polynomial Curves")
    print("="*60)
    
    # Initialize utilities
    plot_manager = PlotManager()
    grid_evaluator = GridEvaluator()
    
    # Set up the plot
    fig, axes = plot_manager.setup_figure(2, 3, figsize=(15, 10), 
                                         suptitle='Polynomial Curves')
    
    # Create test grid
    X, Y = grid_evaluator.create_grid()
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Define the curves to test
    curves = [
        ("Line", CurveFactory.create_line((-2, -1), (2, 1)), "2x + 3y - 1 = 0"),
        ("Intersecting Lines", PolynomialCurve((x-y)*(x+y-1), (x, y)), "(x-y)(x+y-1) = 0"),
        ("Cubic Curve", CurveFactory.create_cubic_curve(), "y² = x³ - x"),
        ("Quartic", PolynomialCurve(y**2 - x**4 + 2*x**2, (x, y)), "y² = x⁴ - 2x²"),
        ("Circle (Polynomial)", PolynomialCurve(x**2 + y**2 - 4, (x, y)), "x² + y² = 4"),
        ("Lemniscate", PolynomialCurve((x**2 + y**2)**2 - 2*(x**2 - y**2), (x, y)), 
         "(x²+y²)² = 2(x²-y²)")
    ]
    
    # Plot each curve
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, (name, curve, equation) in enumerate(curves):
        ax = axes[i // 3, i % 3]
        title = f"{name}\\n{equation}"
        color = colors[i % len(colors)]
        
        print(f"Plotting {name}...")
        plot_manager.plot_curve_contour(ax, curve, X, Y, title=title, 
                                       color=color, show_levels=True)
    
    plot_manager.save_or_show()
    print("✓ Polynomial curves test completed")


def test_curve_evaluation():
    """
    Test curve evaluation at specific points.
    """
    print("="*60)
    print("Testing Curve Evaluation at Specific Points")
    print("="*60)
    
    # Initialize utilities
    grid_evaluator = GridEvaluator()
    
    # Create test curves
    circle = CurveFactory.create_circle((0, 0), 2)
    line = CurveFactory.create_line((-1, -1), (1, 1))
    parabola = CurveFactory.create_parabola((0, 0), 'up', 1)
    
    # Define test points
    test_points = [
        (0, 0, "Origin"),
        (2, 0, "Right edge"),
        (0, 2, "Top edge"),
        (-2, 0, "Left edge"),
        (0, -2, "Bottom edge"),
        (1, 1, "Diagonal"),
        (-1, -1, "Opposite diagonal"),
        (3, 0, "Outside right"),
        (0, 3, "Outside top")
    ]
    
    # Test each curve
    curves = [
        ("Circle (radius 2)", circle),
        ("Diagonal Line", line),
        ("Upward Parabola", parabola)
    ]
    
    for curve_name, curve in curves:
        print(f"\\nTesting {curve_name}:")
        results = grid_evaluator.test_specific_points(curve, test_points, 'curve')
        grid_evaluator.print_test_results(results)
    
    print("\\n✓ Curve evaluation test completed")


def test_curve_properties():
    """
    Test and display properties of different curve types.
    """
    print("="*60)
    print("Testing Curve Properties")
    print("="*60)
    
    # Create test curves
    curves = [
        ("Circle", CurveFactory.create_circle((0, 0), 2)),
        ("Ellipse", CurveFactory.create_ellipse((0, 0), 3, 1.5)),
        ("Hyperbola", CurveFactory.create_hyperbola((0, 0), 1, 1)),
        ("Parabola", CurveFactory.create_parabola((0, 0), 'up', 0.5)),
        ("Line", CurveFactory.create_line((-2, -1), (2, 1)))
    ]
    
    for name, curve in curves:
        print(f"\\n{name}:")
        print(f"  Expression: {curve.expression}")
        print(f"  Variables: {curve.variables}")
        
        # Test bounding box if available
        try:
            bbox = curve.bounding_box()
            print(f"  Bounding box: {bbox}")
        except Exception as e:
            print(f"  Bounding box: Not available ({e})")
        
        # Test some basic properties
        try:
            # Test evaluation at origin
            val_origin = curve.evaluate(0, 0)
            print(f"  Value at origin: {val_origin:.6f}")
        except Exception as e:
            print(f"  Value at origin: Error ({e})")
    
    print("\\n✓ Curve properties test completed")


def run_all_basic_curve_tests():
    """
    Run all basic curve tests.
    """
    print("\\n" + "="*80)
    print("RUNNING ALL BASIC CURVE TESTS")
    print("="*80)
    
    try:
        test_basic_conic_sections()
        print()
        test_polynomial_curves()
        print()
        test_curve_evaluation()
        print()
        test_curve_properties()
        
        print("\\n" + "="*80)
        print("✓ ALL BASIC CURVE TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\\n✗ ERROR in basic curve tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_basic_curve_tests()
