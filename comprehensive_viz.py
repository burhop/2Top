def test_comprehensive_visualization():
    """
    Comprehensive 4x4 grid visualization showing all curve types.
    """
    print("="*60)
    print("Comprehensive Visualization: All Curve Types")
    print("="*60)
    
    import numpy as np
    import matplotlib.pyplot as plt
    import sympy as sp
    from geometry import (
        ConicSection, PolynomialCurve, TrimmedImplicitCurve,
        CompositeCurve, create_circle_region, create_triangle_region,
        create_square_with_hole, create_complex_shape
    )
    
    # Create symbolic variables
    x, y = sp.symbols('x y')
    
    # Set up the plot with 4x4 grid
    fig, axes = plt.subplots(4, 4, figsize=(16, 16))
    fig.suptitle('Comprehensive Implicit Geometry Library Showcase', fontsize=18)
    
    # Define test grid (smaller for performance)
    x_range = np.linspace(-3, 3, 80)
    y_range = np.linspace(-3, 3, 80)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Helper function to plot curves
    def plot_curve(ax, curve, title, color='blue', show_levels=True):
        Z = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                try:
                    Z[i, j] = curve.evaluate(X[i, j], Y[i, j])
                except:
                    Z[i, j] = np.nan
        
        # Plot zero level (the actual curve)
        ax.contour(X, Y, Z, levels=[0], colors=color, linewidths=2)
        if show_levels:
            ax.contour(X, Y, Z, levels=[-1, -0.5, 0.5, 1], colors='gray', alpha=0.3, linewidths=0.5)
        
        ax.set_title(title, fontsize=9)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.tick_params(labelsize=8)
    
    # Helper function to plot area regions
    def plot_area(ax, region, title, color='lightblue'):
        inside_mask = np.zeros_like(X, dtype=bool)
        boundary_mask = np.zeros_like(X, dtype=bool)
        
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                try:
                    inside_mask[i, j] = region.contains(X[i, j], Y[i, j], region_containment=True)
                    boundary_mask[i, j] = region.contains(X[i, j], Y[i, j], region_containment=False)
                except:
                    inside_mask[i, j] = False
                    boundary_mask[i, j] = False
        
        # Plot filled area
        inside_points = np.where(inside_mask)
        if len(inside_points[0]) > 0:
            ax.scatter(X[inside_points], Y[inside_points], c=color, s=0.3, alpha=0.6)
        
        # Plot boundary
        boundary_points = np.where(boundary_mask)
        if len(boundary_points[0]) > 0:
            ax.scatter(X[boundary_points], Y[boundary_points], c='red', s=0.8, alpha=0.8)
        
        ax.set_title(title, fontsize=9)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.tick_params(labelsize=8)
    
    try:
        # Row 1: Basic Conics
        print("Row 1: Basic Conic Sections...")
        
        # (0,0) Circle
        circle_expr = x**2 + y**2 - 4
        circle_curve = ConicSection(circle_expr, (x, y))
        plot_curve(axes[0, 0], circle_curve, "Circle\nx² + y² = 4")
        
        # (0,1) Ellipse
        ellipse_expr = x**2/4 + y**2/2 - 1
        ellipse_curve = ConicSection(ellipse_expr, (x, y))
        plot_curve(axes[0, 1], ellipse_curve, "Ellipse\nx²/4 + y²/2 = 1")
        
        # (0,2) Hyperbola
        hyperbola_expr = x**2 - y**2 - 1
        hyperbola_curve = ConicSection(hyperbola_expr, (x, y))
        plot_curve(axes[0, 2], hyperbola_curve, "Hyperbola\nx² - y² = 1")
        
        # (0,3) Parabola
        parabola_expr = y - x**2
        parabola_curve = ConicSection(parabola_expr, (x, y))
        plot_curve(axes[0, 3], parabola_curve, "Parabola\ny = x²")
        
        # Row 2: Lines and Polynomials
        print("Row 2: Lines and Polynomial Curves...")
        
        # (1,0) Line
        line_expr = 2*x + 3*y - 1
        line_curve = PolynomialCurve(line_expr, (x, y))
        plot_curve(axes[1, 0], line_curve, "Line\n2x + 3y = 1", 'green')
        
        # (1,1) Intersecting Lines
        intersecting_expr = (x - y) * (x + y - 1)
        intersecting_curve = PolynomialCurve(intersecting_expr, (x, y))
        plot_curve(axes[1, 1], intersecting_curve, "Intersecting Lines\n(x-y)(x+y-1) = 0", 'purple')
        
        # (1,2) Cubic Curve
        cubic_expr = y**2 - x**3 + x
        cubic_curve = PolynomialCurve(cubic_expr, (x, y))
        plot_curve(axes[1, 2], cubic_curve, "Cubic Curve\ny² = x³ - x", 'orange')
        
        # (1,3) Four-leaf Rose
        rose_expr = (x**2 + y**2)**2 - 2*(x**2 - y**2)
        rose_curve = PolynomialCurve(rose_expr, (x, y))
        plot_curve(axes[1, 3], rose_curve, "Four-leaf Rose\n(x²+y²)² = 2(x²-y²)", 'magenta')
        
        # Row 3: Trimmed and Composite Curves
        print("Row 3: Trimmed and Composite Curves...")
        
        # (2,0) Trimmed Circle (upper half)
        circle_base = ConicSection(x**2 + y**2 - 1, (x, y))
        plot_curve(axes[2, 0], circle_base, "Trimmed Circle\n(Upper Half)", 'lightgray', False)
        angles = np.linspace(0, np.pi, 100)
        trim_x = np.cos(angles)
        trim_y = np.sin(angles)
        axes[2, 0].plot(trim_x, trim_y, 'b-', linewidth=3)
        
        # (2,1) Trimmed Circle (right half)
        plot_curve(axes[2, 1], circle_base, "Trimmed Circle\n(Right Half)", 'lightgray', False)
        angles = np.linspace(-np.pi/2, np.pi/2, 100)
        trim_x = np.cos(angles)
        trim_y = np.sin(angles)
        axes[2, 1].plot(trim_x, trim_y, 'r-', linewidth=3)
        
        # (2,2) Composite Curve (two quarters)
        circle_base_expr = x**2 + y**2 - 2.25
        circle_base_comp = ConicSection(circle_base_expr, (x, y))
        plot_curve(axes[2, 2], circle_base_comp, "Composite Curve\n(2 Quarters)", 'lightgray', False)
        
        # First quarter (upper right)
        angles1 = np.linspace(0, np.pi/2, 50)
        q1_x = 1.5 * np.cos(angles1)
        q1_y = 1.5 * np.sin(angles1)
        axes[2, 2].plot(q1_x, q1_y, 'r-', linewidth=3)
        
        # Third quarter (lower left)
        angles3 = np.linspace(np.pi, 3*np.pi/2, 50)
        q3_x = 1.5 * np.cos(angles3)
        q3_y = 1.5 * np.sin(angles3)
        axes[2, 2].plot(q3_x, q3_y, 'b-', linewidth=3)
        
        # (2,3) Composite Curve (three segments)
        plot_curve(axes[2, 3], circle_base_comp, "Composite Curve\n(3 Segments)", 'lightgray', False)
        
        # Three segments
        for i, color in enumerate(['red', 'green', 'blue']):
            start_angle = i * 2 * np.pi / 3
            end_angle = start_angle + np.pi / 3
            angles = np.linspace(start_angle, end_angle, 30)
            seg_x = 1.5 * np.cos(angles)
            seg_y = 1.5 * np.sin(angles)
            axes[2, 3].plot(seg_x, seg_y, color=color, linewidth=3)
        
        # Row 4: Area Regions
        print("Row 4: Area Regions...")
        
        # (3,0) Circle Area
        circle_region = create_circle_region(center=(0.0, 0.0), radius=2.0)
        plot_area(axes[3, 0], circle_region, "Circle Area\n(Filled Region)", 'lightblue')
        
        # (3,1) Triangle Area
        triangle_vertices = [(-2.0, -1.5), (2.0, -1.5), (0.0, 2.0)]
        triangle_region = create_triangle_region(triangle_vertices)
        plot_area(axes[3, 1], triangle_region, "Triangle Area\n(3 Line Segments)", 'lightgreen')
        
        # (3,2) Square with Hole
        square_with_hole = create_square_with_hole()
        plot_area(axes[3, 2], square_with_hole, "Square with Hole\n(Composite Region)", 'lightyellow')
        
        # (3,3) Complex Shape
        complex_shape = create_complex_shape()
        plot_area(axes[3, 3], complex_shape, "Complex Shape\n(Multiple Regions)", 'lightcoral')
        
        plt.tight_layout()
        plt.show()
        
        print("\n--- COMPREHENSIVE VISUALIZATION COMPLETED ---")
        
    except Exception as e:
        print(f"\nERROR: Comprehensive visualization failed with exception:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        plt.show()
        print("\n--- COMPREHENSIVE VISUALIZATION FAILED ---")

if __name__ == "__main__":
    test_comprehensive_visualization()
