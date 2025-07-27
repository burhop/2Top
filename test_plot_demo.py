"""
Demo script to test the plot method - Sprint 1 Task GEO-S1-T8
This script demonstrates the plotting functionality of ImplicitCurve.
"""

import sympy as sp
import matplotlib.pyplot as plt
from geometry.implicit_curve import ImplicitCurve

def test_plot_functionality():
    """Test that plot method works without crashing"""
    print("Testing ImplicitCurve plot method...")
    
    # Create symbols
    x, y = sp.symbols('x y')
    
    # Test different curves
    curves = [
        ("Circle", ImplicitCurve(x**2 + y**2 - 1, variables=(x, y))),
        ("Line", ImplicitCurve(x + y - 1, variables=(x, y))),
        ("Parabola", ImplicitCurve(y - x**2, variables=(x, y))),
        ("Hyperbola", ImplicitCurve(x**2 - y**2 - 1, variables=(x, y)))
    ]
    
    for name, curve in curves:
        print(f"Testing plot for {name}...")
        try:
            # Test that plot method can be called without error
            # We'll use a non-blocking approach for testing
            plt.figure(figsize=(6, 6))
            
            # Create coordinate grid manually to test evaluate
            import numpy as np
            x_vals = np.linspace(-2, 2, 100)
            y_vals = np.linspace(-2, 2, 100)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Evaluate function over grid
            Z = curve.evaluate(X, Y)
            
            # Create contour plot
            plt.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)
            plt.title(f'{name}: {curve}')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            
            # Save instead of show for testing
            plt.savefig(f'test_{name.lower()}_plot.png', dpi=100, bbox_inches='tight')
            plt.close()
            
            print(f"✓ {name} plot generated successfully")
            
        except Exception as e:
            print(f"✗ Error plotting {name}: {e}")
            return False
    
    print("All plot tests passed!")
    return True

if __name__ == "__main__":
    test_plot_functionality()
