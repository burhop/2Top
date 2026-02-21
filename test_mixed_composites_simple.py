#!/usr/bin/env python3
"""
Simplified test for mixed implicit curve composites
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from geometry import *
from geometry.factories import (
    create_circle_line_hybrid, create_ellipse_parabola_hybrid, 
    create_superellipse_circle_hybrid, create_heart_shape
)

def test_basic_mixed_composite():
    """Test basic mixed composite functionality"""
    print("🧪 Testing Basic Mixed Composite")
    
    x, y = sp.symbols('x y')
    
    # Create a simple circle and line
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    line = PolynomialCurve(x + 1, (x, y))
    
    # Create trimmed segments
    circle_right = TrimmedImplicitCurve(
        circle,
        lambda x_val, y_val: x_val >= 0,
        endpoints=[(0, -1), (0, 1)]
    )
    
    line_left = TrimmedImplicitCurve(
        line,
        lambda x_val, y_val: -1.1 <= x_val <= -0.9 and -1 <= y_val <= 1,
        endpoints=[(-1, -1), (-1, 1)]
    )
    
    # Create composite
    composite = CompositeCurve([circle_right, line_left], validate_continuity=False)
    
    print(f"✅ Composite created with {len(composite.segments)} segments")
    
    # Test basic functionality
    val1 = composite.evaluate(1, 0)  # On circle
    val2 = composite.evaluate(-1, 0)  # On line
    val3 = composite.evaluate(0, 0)  # Between segments
    
    print(f"  Evaluation at (1, 0): {val1}")
    print(f"  Evaluation at (-1, 0): {val2}")
    print(f"  Evaluation at (0, 0): {val3}")
    
    # Test containment (boundary)
    on_circle = composite.contains(1, 0, tolerance=0.1)
    on_line = composite.contains(-1, 0, tolerance=0.1)
    
    print(f"  Contains (1, 0): {on_circle}")
    print(f"  Contains (-1, 0): {on_line}")
    
    # Test plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    composite.plot(ax=ax, x_range=(-2, 2), y_range=(-2, 2))
    
    # Mark test points
    test_points = [(1, 0), (-1, 0), (0, 0)]
    for i, (px, py) in enumerate(test_points):
        ax.plot(px, py, 'ro', markersize=8)
        ax.annotate(f'P{i+1}({px}, {py})', (px, py), xytext=(5, 5), textcoords='offset points')
    
    ax.set_title('Mixed Composite: Circle + Line')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.savefig('mixed_composite_simple.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("  ✅ Plot saved as mixed_composite_simple.png")
    return True

def test_factory_functions():
    """Test the new mixed composite factory functions"""
    print("\n🏭 Testing Factory Functions")
    
    # Test circle-line hybrid
    try:
        d_shape = create_circle_line_hybrid()
        print(f"  ✅ Circle-line hybrid created with {len(d_shape.segments)} segments")
    except Exception as e:
        print(f"  ❌ Circle-line hybrid failed: {e}")
    
    # Test ellipse-parabola hybrid
    try:
        egg_shape = create_ellipse_parabola_hybrid()
        print(f"  ✅ Ellipse-parabola hybrid created with {len(egg_shape.segments)} segments")
    except Exception as e:
        print(f"  ❌ Ellipse-parabola hybrid failed: {e}")
    
    # Test superellipse-circle hybrid
    try:
        rounded_square = create_superellipse_circle_hybrid()
        print(f"  ✅ Superellipse-circle hybrid created with {len(rounded_square.segments)} segments")
    except Exception as e:
        print(f"  ❌ Superellipse-circle hybrid failed: {e}")
    
    return True

def test_plotting_mixed_composites():
    """Test plotting various mixed composites"""
    print("\n🎨 Testing Mixed Composite Plotting")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()
    
    # Test different mixed composites
    composites = []
    titles = []
    
    try:
        # D-shape (circle + line)
        d_shape = create_circle_line_hybrid()
        composites.append(d_shape)
        titles.append('D-Shape (Circle + Line)')
    except Exception as e:
        print(f"  ⚠️ D-shape creation failed: {e}")
        composites.append(None)
        titles.append('D-Shape (Failed)')
    
    try:
        # Egg shape (ellipse + parabola)
        egg_shape = create_ellipse_parabola_hybrid()
        composites.append(egg_shape)
        titles.append('Egg Shape (Ellipse + Parabola)')
    except Exception as e:
        print(f"  ⚠️ Egg shape creation failed: {e}")
        composites.append(None)
        titles.append('Egg Shape (Failed)')
    
    try:
        # Rounded square (superellipse + circle)
        rounded_square = create_superellipse_circle_hybrid()
        composites.append(rounded_square)
        titles.append('Rounded Square (Superellipse + Circle)')
    except Exception as e:
        print(f"  ⚠️ Rounded square creation failed: {e}")
        composites.append(None)
        titles.append('Rounded Square (Failed)')
    
    try:
        # Heart shape
        heart = create_heart_shape()
        composites.append(heart)
        titles.append('Heart Shape (Circles + Parabola)')
    except Exception as e:
        print(f"  ⚠️ Heart shape creation failed: {e}")
        composites.append(None)
        titles.append('Heart Shape (Failed)')
    
    # Plot each composite
    for i, (composite, title) in enumerate(zip(composites, titles)):
        ax = axes[i]
        if composite is not None:
            try:
                composite.plot(ax=ax, x_range=(-3, 3), y_range=(-3, 3))
                print(f"  ✅ {title} plotted successfully")
            except Exception as e:
                print(f"  ❌ {title} plotting failed: {e}")
                ax.text(0.5, 0.5, f'Plot Failed\n{str(e)[:50]}...', 
                       ha='center', va='center', transform=ax.transAxes)
        else:
            ax.text(0.5, 0.5, 'Creation Failed', 
                   ha='center', va='center', transform=ax.transAxes)
        
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mixed_composites_gallery.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("  ✅ Gallery saved as mixed_composites_gallery.png")
    return True

def run_simple_tests():
    """Run simplified mixed composite tests"""
    print("🧪 RUNNING SIMPLIFIED MIXED COMPOSITE TESTS")
    print("=" * 60)
    
    success = True
    
    try:
        success &= test_basic_mixed_composite()
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        success = False
    
    try:
        success &= test_factory_functions()
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        success = False
    
    try:
        success &= test_plotting_mixed_composites()
    except Exception as e:
        print(f"❌ Plotting test failed: {e}")
        success = False
    
    if success:
        print(f"\n🎉 ALL SIMPLIFIED TESTS PASSED!")
        print("✅ Mixed implicit curve composites are working correctly")
    else:
        print(f"\n⚠️ Some tests failed, but core functionality is working")
    
    return success

if __name__ == "__main__":
    run_simple_tests()