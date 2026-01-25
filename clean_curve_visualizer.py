#!/usr/bin/env python3
"""
Clean curve visualizer with precise intersection display
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
from geometry import *
from geometry.curve_intersections import find_curve_intersections

class CleanCurveVisualizerApp:
    """Clean curve visualizer with precise intersection handling"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Clean Curve Visualizer - Precise Intersections")
        self.root.geometry("1200x800")
        
        # Current curves and intersections
        self.curves = []
        self.curve_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        self.intersection_data = []
        
        # Display settings
        self.show_curves = tk.BooleanVar(value=True)
        self.show_intersections = tk.BooleanVar(value=True)
        self.show_labels = tk.BooleanVar(value=True)
        self.detect_overlap = tk.BooleanVar(value=False)  # Disabled by default for performance
        
        # Setup UI
        self.setup_ui()
        
        # Start with empty canvas
        self.update_plot()
        
    def setup_ui(self):
        """Setup user interface"""
        
        # Main paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.Frame(paned)
        paned.add(control_frame, weight=1)
        
        # Plot panel
        plot_frame = ttk.Frame(paned)
        paned.add(plot_frame, weight=3)
        
        self.setup_controls(control_frame)
        self.setup_plot(plot_frame)
        
    def setup_controls(self, parent):
        """Setup control panel"""
        
        # Title
        ttk.Label(parent, text="Clean Curve Visualizer", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Curves section
        curves_frame = ttk.LabelFrame(parent, text="Curves")
        curves_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.curve_listbox = tk.Listbox(curves_frame, height=5)
        self.curve_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Add curve buttons
        add_frame1 = ttk.Frame(curves_frame)
        add_frame1.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(add_frame1, text="Circle", command=self.add_circle).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame1, text="Line", command=self.add_line).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame1, text="Ellipse", command=self.add_ellipse).pack(side=tk.LEFT, padx=1)
        
        add_frame2 = ttk.Frame(curves_frame)
        add_frame2.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(add_frame2, text="Parabola", command=self.add_parabola).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame2, text="Hyperbola", command=self.add_hyperbola).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame2, text="Superellipse", command=self.add_superellipse).pack(side=tk.LEFT, padx=1)
        
        add_frame3 = ttk.Frame(curves_frame)
        add_frame3.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(add_frame3, text="Trimmed", command=self.add_trimmed).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame3, text="Composite", command=self.add_composite).pack(side=tk.LEFT, padx=1)
        ttk.Button(add_frame3, text="Square", command=self.add_square).pack(side=tk.LEFT, padx=1)
        
        # Custom expression
        custom_frame = ttk.Frame(curves_frame)
        custom_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(custom_frame, text="Custom f(x,y)=0:", font=('Arial', 8)).pack(anchor=tk.W)
        self.custom_expr = tk.StringVar(value="x**3 + y**3 - 1")
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_expr, font=('Courier', 8))
        custom_entry.pack(fill=tk.X, pady=1)
        custom_entry.bind('<Return>', lambda e: self.add_custom())
        
        ttk.Button(custom_frame, text="Add Custom", command=self.add_custom).pack(pady=2)
        
        ttk.Button(curves_frame, text="Clear All", command=self.clear_all).pack(pady=5)
        
        # Intersections section
        intersect_frame = ttk.LabelFrame(parent, text="Intersections")
        intersect_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(intersect_frame, text="Find All Intersections", 
                  command=self.find_intersections).pack(pady=2)
        
        # Preset combinations
        preset_frame = ttk.Frame(intersect_frame)
        preset_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(preset_frame, text="Quick Tests:", font=('Arial', 8)).pack(anchor=tk.W)
        
        preset_buttons = ttk.Frame(preset_frame)
        preset_buttons.pack(fill=tk.X)
        
        ttk.Button(preset_buttons, text="Circle+Line", command=self.preset_circle_line).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_buttons, text="2 Circles", command=self.preset_two_circles).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_buttons, text="Multi-Segment", command=self.preset_multi_segment).pack(side=tk.LEFT, padx=1)
        
        self.intersect_listbox = tk.Listbox(intersect_frame, height=6)
        self.intersect_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Display options
        display_frame = ttk.LabelFrame(parent, text="Display")
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(display_frame, text="Show Curves", 
                       variable=self.show_curves, command=self.update_plot).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(display_frame, text="Show Intersections", 
                       variable=self.show_intersections, command=self.update_plot).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(display_frame, text="Show Labels", 
                       variable=self.show_labels, command=self.update_plot).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(display_frame, text="Detect Overlap (slower)", 
                       variable=self.detect_overlap).pack(anchor=tk.W, padx=5)
        
        # Plot settings
        settings_frame = ttk.LabelFrame(parent, text="Settings")
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="Range: ±").pack(anchor=tk.W, padx=5)
        self.plot_range = tk.DoubleVar(value=3.0)
        ttk.Entry(settings_frame, textvariable=self.plot_range, width=8).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Button(settings_frame, text="Update Plot", command=self.update_plot).pack(pady=5)
        
    def setup_plot(self, parent):
        """Setup plot panel"""
        
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Implicit Curves with Precise Intersections', fontweight='bold')
        
    def add_circle(self):
        """Add a circle"""
        x, y = sp.symbols('x y')
        
        # Variety of circles for interesting intersections
        circle_configs = [
            (0, 0, 1, "Unit Circle"),
            (1, 0, 1, "Circle (1,0)"),
            (0, 1, 0.8, "Circle (0,1)"),
            (-0.5, -0.5, 1.2, "Circle (-0.5,-0.5)"),
            (0, 0, 2, "Large Circle"),
        ]
        
        circle_count = len([c for c in self.curves if 'Circle' in c[0]])
        if circle_count < len(circle_configs):
            cx, cy, r, name = circle_configs[circle_count]
            curve = ConicSection((x-cx)**2 + (y-cy)**2 - r**2, (x, y))
        else:
            # Random circle
            cx = np.random.uniform(-1, 1)
            cy = np.random.uniform(-1, 1)
            r = np.random.uniform(0.5, 1.5)
            curve = ConicSection((x-cx)**2 + (y-cy)**2 - r**2, (x, y))
            name = f"Circle ({cx:.1f},{cy:.1f})"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_line(self):
        """Add a line"""
        x, y = sp.symbols('x y')
        
        # Variety of lines
        line_configs = [
            (x + y, "Line y=-x"),
            (y - 1, "Line y=1"),
            (x - 1, "Line x=1"),
            (y, "Line y=0"),
            (x, "Line x=0"),
            (x - y, "Line y=x"),
            (2*x + y - 1, "Line 2x+y=1"),
        ]
        
        line_count = len([c for c in self.curves if 'Line' in c[0]])
        if line_count < len(line_configs):
            expr, name = line_configs[line_count]
            curve = PolynomialCurve(expr, (x, y))
        else:
            # Random line
            slope = np.random.uniform(-2, 2)
            intercept = np.random.uniform(-1, 1)
            curve = PolynomialCurve(y - slope*x - intercept, (x, y))
            name = f"Line (m={slope:.1f})"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_ellipse(self):
        """Add an ellipse"""
        x, y = sp.symbols('x y')
        
        # Variety of ellipses
        ellipse_configs = [
            (2, 1, "Ellipse 2x1"),
            (1, 2, "Ellipse 1x2"),
            (3, 1.5, "Ellipse 3x1.5"),
            (1.5, 0.8, "Ellipse 1.5x0.8"),
        ]
        
        ellipse_count = len([c for c in self.curves if 'Ellipse' in c[0]])
        if ellipse_count < len(ellipse_configs):
            a, b, name = ellipse_configs[ellipse_count]
            curve = ConicSection(x**2/a**2 + y**2/b**2 - 1, (x, y))
        else:
            # Random ellipse
            a = np.random.uniform(1, 2.5)
            b = np.random.uniform(0.5, 2)
            curve = ConicSection(x**2/a**2 + y**2/b**2 - 1, (x, y))
            name = f"Ellipse {a:.1f}x{b:.1f}"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_parabola(self):
        """Add a parabola"""
        x, y = sp.symbols('x y')
        
        # Variety of parabolas
        parabola_configs = [
            (y - x**2, "Parabola y=x²"),
            (x - y**2, "Parabola x=y²"),
            (y - 0.5*x**2, "Parabola y=0.5x²"),
            (y + x**2 - 2, "Parabola y=-x²+2"),
            (x - 0.5*y**2 + 1, "Parabola x=0.5y²-1"),
        ]
        
        parabola_count = len([c for c in self.curves if 'Parabola' in c[0]])
        if parabola_count < len(parabola_configs):
            expr, name = parabola_configs[parabola_count]
            curve = PolynomialCurve(expr, (x, y))
        else:
            # Random parabola
            a = np.random.uniform(0.2, 1.5)
            curve = PolynomialCurve(y - a*x**2, (x, y))
            name = f"Parabola a={a:.1f}"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_hyperbola(self):
        """Add a hyperbola"""
        x, y = sp.symbols('x y')
        
        # Variety of hyperbolas
        hyperbola_configs = [
            (x**2 - y**2 - 1, "Hyperbola x²-y²=1"),
            (y**2 - x**2 - 1, "Hyperbola y²-x²=1"),
            (x**2/4 - y**2 - 1, "Hyperbola x²/4-y²=1"),
            (x*y - 1, "Hyperbola xy=1"),
        ]
        
        hyperbola_count = len([c for c in self.curves if 'Hyperbola' in c[0]])
        if hyperbola_count < len(hyperbola_configs):
            expr, name = hyperbola_configs[hyperbola_count]
            curve = PolynomialCurve(expr, (x, y))
        else:
            # Random hyperbola
            a = np.random.uniform(0.5, 2)
            b = np.random.uniform(0.5, 2)
            curve = ConicSection(x**2/a**2 - y**2/b**2 - 1, (x, y))
            name = f"Hyperbola {a:.1f},{b:.1f}"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_superellipse(self):
        """Add a superellipse"""
        x, y = sp.symbols('x y')
        
        # Variety of superellipses
        superellipse_configs = [
            (1, 1, 4, "Square-like (n=4)"),
            (1, 1, 0.5, "Diamond-like (n=0.5)"),
            (1.5, 1, 8, "Rounded rect (n=8)"),
            (1, 1.5, 3, "Rounded ellipse (n=3)"),
        ]
        
        super_count = len([c for c in self.curves if 'like' in c[0] or 'Rounded' in c[0]])
        if super_count < len(superellipse_configs):
            a, b, n, name = superellipse_configs[super_count]
            curve = Superellipse(a=a, b=b, n=n, variables=(x, y))
        else:
            # Random superellipse
            a = np.random.uniform(0.8, 1.5)
            b = np.random.uniform(0.8, 1.5)
            n = np.random.choice([0.5, 1.5, 2, 4, 8])
            curve = Superellipse(a=a, b=b, n=n, variables=(x, y))
            name = f"Superellipse n={n}"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_custom(self):
        """Add custom curve"""
        try:
            x, y = sp.symbols('x y')
            expr_str = self.custom_expr.get().strip()
            if not expr_str:
                return
                
            expr = sp.sympify(expr_str)
            curve = PolynomialCurve(expr, (x, y))
            name = f"Custom: {expr_str[:15]}..."
            
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {e}")
    
    def add_trimmed(self):
        """Add a trimmed implicit curve"""
        x, y = sp.symbols('x y')
        
        # Variety of trimmed curves
        trimmed_configs = [
            # Half circle (right half)
            (ConicSection(x**2 + y**2 - 1, (x, y)), 
             lambda x_val, y_val: x_val >= 0, 
             "Right Half Circle"),
            
            # Quarter circle (first quadrant)
            (ConicSection(x**2 + y**2 - 1, (x, y)), 
             lambda x_val, y_val: (x_val >= 0) & (y_val >= 0), 
             "Quarter Circle"),
            
            # Trimmed parabola (limited range)
            (PolynomialCurve(y - x**2, (x, y)), 
             lambda x_val, y_val: (x_val >= -1) & (x_val <= 1), 
             "Trimmed Parabola"),
            
            # Arc of ellipse (upper half)
            (ConicSection(x**2/4 + y**2 - 1, (x, y)), 
             lambda x_val, y_val: y_val >= 0, 
             "Upper Ellipse Arc"),
            
            # Trimmed line segment
            (PolynomialCurve(x + y, (x, y)), 
             lambda x_val, y_val: (x_val >= -1) & (x_val <= 1), 
             "Line Segment"),
        ]
        
        trimmed_count = len([c for c in self.curves if 'Half' in c[0] or 'Quarter' in c[0] or 'Trimmed' in c[0] or 'Arc' in c[0] or 'Segment' in c[0]])
        
        if trimmed_count < len(trimmed_configs):
            base_curve, mask_func, name = trimmed_configs[trimmed_count]
            curve = TrimmedImplicitCurve(base_curve, mask_func)
        else:
            # Random trimmed circle
            base_curve = ConicSection(x**2 + y**2 - 1, (x, y))
            angle_start = np.random.uniform(0, np.pi)
            angle_end = angle_start + np.random.uniform(np.pi/2, np.pi)
            
            def angle_mask(x_val, y_val):
                angles = np.arctan2(y_val, x_val)
                return (angles >= angle_start) & (angles <= angle_end)
            
            curve = TrimmedImplicitCurve(base_curve, angle_mask)
            name = f"Arc ({angle_start:.1f} to {angle_end:.1f})"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_composite(self):
        """Add a composite curve"""
        x, y = sp.symbols('x y')
        
        # Variety of composite curves
        composite_configs = [
            # Circle from quarters
            (lambda: create_circle_from_quarters(center=(0, 0), radius=1.0), 
             "Circle from Quarters"),
            
            # Different sized circle
            (lambda: create_circle_from_quarters(center=(0.5, 0), radius=1.2), 
             "Offset Circle Quarters"),
            
            # Custom composite: two semicircles
            (lambda: self._create_two_semicircles(), 
             "Two Semicircles"),
            
            # Custom composite: connected arcs
            (lambda: self._create_connected_arcs(), 
             "Connected Arcs"),
        ]
        
        composite_count = len([c for c in self.curves if 'Quarters' in c[0] or 'Semicircles' in c[0] or 'Arcs' in c[0]])
        
        if composite_count < len(composite_configs):
            creator_func, name = composite_configs[composite_count]
            try:
                curve = creator_func()
            except Exception as e:
                print(f"Error creating {name}: {e}")
                # Fallback to simple circle quarters
                curve = create_circle_from_quarters(center=(0, 0), radius=1.0)
                name = "Circle from Quarters (fallback)"
        else:
            # Default to circle quarters with random parameters
            cx = np.random.uniform(-0.5, 0.5)
            cy = np.random.uniform(-0.5, 0.5)
            r = np.random.uniform(0.8, 1.5)
            curve = create_circle_from_quarters(center=(cx, cy), radius=r)
            name = f"Random Circle Quarters"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_square(self):
        """Add a square (composite curve)"""
        # Variety of squares
        square_configs = [
            ((-1, -1), (1, 1), "Unit Square"),
            ((-0.5, -0.5), (0.5, 0.5), "Small Square"),
            ((0, 0), (2, 2), "Large Square"),
            ((-1.5, -0.5), (0.5, 1.5), "Rectangle"),
        ]
        
        square_count = len([c for c in self.curves if 'Square' in c[0] or 'Rectangle' in c[0]])
        
        if square_count < len(square_configs):
            (x1, y1), (x2, y2), name = square_configs[square_count]
            curve = create_square_from_edges((x1, y1), (x2, y2))
        else:
            # Random square
            size = np.random.uniform(0.5, 1.5)
            cx = np.random.uniform(-0.5, 0.5)
            cy = np.random.uniform(-0.5, 0.5)
            curve = create_square_from_edges((cx-size/2, cy-size/2), (cx+size/2, cy+size/2))
            name = f"Random Square"
        
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def _create_two_semicircles(self):
        """Create a composite of two semicircles"""
        x, y = sp.symbols('x y')
        
        # Upper semicircle
        upper_circle = ConicSection(x**2 + y**2 - 1, (x, y))
        upper_mask = lambda x_val, y_val: y_val >= 0
        upper_semi = TrimmedImplicitCurve(upper_circle, upper_mask)
        
        # Lower semicircle (shifted)
        lower_circle = ConicSection(x**2 + (y-0.5)**2 - 0.25, (x, y))
        lower_mask = lambda x_val, y_val: y_val <= 0.5
        lower_semi = TrimmedImplicitCurve(lower_circle, lower_mask)
        
        # Create composite
        composite = CompositeCurve([upper_semi, lower_semi])
        return composite
        
    def _create_connected_arcs(self):
        """Create connected arcs forming a complex shape"""
        x, y = sp.symbols('x y')
        
        # Arc 1: quarter circle
        arc1_base = ConicSection((x-0.5)**2 + y**2 - 0.25, (x, y))
        arc1_mask = lambda x_val, y_val: (x_val >= 0.25) & (y_val >= 0)
        arc1 = TrimmedImplicitCurve(arc1_base, arc1_mask)
        
        # Arc 2: another quarter circle
        arc2_base = ConicSection((x+0.5)**2 + y**2 - 0.25, (x, y))
        arc2_mask = lambda x_val, y_val: (x_val <= -0.25) & (y_val >= 0)
        arc2 = TrimmedImplicitCurve(arc2_base, arc2_mask)
        
        # Create composite
        composite = CompositeCurve([arc1, arc2])
        return composite
        
    def clear_all(self):
        """Clear all curves and intersections"""
        self.curves.clear()
        self.intersection_data.clear()
        self.update_curve_list()
        self.update_intersect_list()
        self.update_plot()
        
    def find_intersections(self):
        """Find all intersections with high precision"""
        if len(self.curves) < 2:
            messagebox.showwarning("Warning", "Need at least 2 curves")
            return
        
        self.intersection_data.clear()
        
        # Find pairwise intersections
        for i in range(len(self.curves)):
            for j in range(i + 1, len(self.curves)):
                name1, curve1 = self.curves[i]
                name2, curve2 = self.curves[j]
                
                # Use adaptive precision settings based on curve types
                curve1_type = type(curve1).__name__
                curve2_type = type(curve2).__name__
                
                # Adjust settings for different curve combinations
                if 'Superellipse' in curve1_type or 'Superellipse' in curve2_type:
                    grid_res = 800
                    tolerance = 1e-8
                elif 'Procedural' in curve1_type or 'Procedural' in curve2_type:
                    grid_res = 600
                    tolerance = 1e-8
                else:
                    grid_res = 600
                    tolerance = 1e-10
                
                intersections = find_curve_intersections(
                    curve1, curve2,
                    search_range=self.plot_range.get(),
                    grid_resolution=grid_res,
                    tolerance=tolerance,
                    max_points=20,
                    detect_overlap=self.detect_overlap.get()
                )
                
                for point in intersections:
                    # Verify the intersection is valid
                    val1 = curve1.evaluate(point[0], point[1])
                    val2 = curve2.evaluate(point[0], point[1])
                    
                    if abs(val1) < 1e-6 and abs(val2) < 1e-6:  # Both curves pass through point
                        self.intersection_data.append({
                            'point': point,
                            'curve1': name1,
                            'curve2': name2,
                            'error1': abs(val1),
                            'error2': abs(val2)
                        })
        
        self.update_intersect_list()
        self.update_plot()
        
        # Show summary
        if self.intersection_data:
            messagebox.showinfo("Results", f"Found {len(self.intersection_data)} precise intersections")
        else:
            messagebox.showinfo("Results", "No intersections found")
    
    def update_curve_list(self):
        """Update curve list"""
        self.curve_listbox.delete(0, tk.END)
        for i, (name, _) in enumerate(self.curves):
            color = self.curve_colors[i % len(self.curve_colors)]
            self.curve_listbox.insert(tk.END, f"{name}")
    
    def update_intersect_list(self):
        """Update intersection list"""
        self.intersect_listbox.delete(0, tk.END)
        for i, data in enumerate(self.intersection_data):
            point = data['point']
            curve1 = data['curve1']
            curve2 = data['curve2']
            error1 = data['error1']
            error2 = data['error2']
            
            # Format with error information
            error_info = f"(err: {max(error1, error2):.2e})" if max(error1, error2) > 1e-8 else ""
            
            self.intersect_listbox.insert(tk.END, 
                f"({point[0]:.4f}, {point[1]:.4f}) - {curve1[:10]} ∩ {curve2[:10]} {error_info}")
    
    def update_plot(self):
        """Update plot"""
        self.ax.clear()
        
        plot_range = self.plot_range.get()
        self.ax.set_xlim(-plot_range, plot_range)
        self.ax.set_ylim(-plot_range, plot_range)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Implicit Curves with Precise Intersections', fontweight='bold')
        
        if not self.curves:
            self.canvas.draw()
            return
        
        # Create evaluation grid
        resolution = 400
        x_range = np.linspace(-plot_range, plot_range, resolution)
        y_range = np.linspace(-plot_range, plot_range, resolution)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Plot curves
        if self.show_curves.get():
            legend_elements = []
            
            for i, (name, curve) in enumerate(self.curves):
                try:
                    color = self.curve_colors[i % len(self.curve_colors)]
                    
                    # Special handling for trimmed curves
                    if hasattr(curve, 'base_curve') and hasattr(curve, 'mask'):
                        # This is a TrimmedImplicitCurve - apply mask properly
                        Z = curve.base_curve.evaluate(X, Y)
                        
                        # Apply mask to hide regions outside the trimmed segment
                        mask_grid = np.zeros_like(X, dtype=bool)
                        
                        # Vectorized mask application for better performance
                        if hasattr(curve, '_xmin') and curve._xmin is not None:
                            # Use explicit bounds if available (much faster)
                            eps = 1e-9
                            mask_grid = (
                                (X >= (curve._xmin - eps)) & (X <= (curve._xmax + eps)) &
                                (Y >= (curve._ymin - eps)) & (Y <= (curve._ymax + eps))
                            )
                        else:
                            # Fall back to point-by-point mask evaluation
                            for row in range(X.shape[0]):
                                for col in range(X.shape[1]):
                                    mask_grid[row, col] = curve.mask(X[row, col], Y[row, col])
                        
                        # Set masked regions to NaN so they don't appear in contour
                        Z_masked = np.where(mask_grid, Z, np.nan)
                        
                        self.ax.contour(X, Y, Z_masked, levels=[0], colors=[color], linewidths=3)
                    else:
                        # Regular curve - plot normally
                        Z = curve.evaluate(X, Y)
                        self.ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=3)
                    
                    legend_elements.append(plt.Line2D([0], [0], color=color, lw=3, label=name))
                    
                except Exception as e:
                    print(f"Error plotting {name}: {e}")
            
            if legend_elements:
                self.ax.legend(handles=legend_elements, loc='upper right')
        
        # Plot intersections
        if self.show_intersections.get() and self.intersection_data:
            for i, data in enumerate(self.intersection_data):
                point = data['point']
                
                # Plot intersection point
                self.ax.plot(point[0], point[1], 'ro', markersize=10, 
                           markeredgecolor='black', markeredgewidth=2, zorder=10)
                
                # Add label if enabled
                if self.show_labels.get():
                    label = f"({point[0]:.3f}, {point[1]:.3f})"
                    self.ax.annotate(label, xy=point, xytext=(5, 5),
                                   textcoords='offset points', fontsize=9,
                                   bbox=dict(boxstyle='round,pad=0.3', 
                                           facecolor='yellow', alpha=0.8))
        
        self.canvas.draw()
    
    def preset_circle_line(self):
        """Preset: Circle intersecting line"""
        self.clear_all()
        x, y = sp.symbols('x y')
        
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        line = PolynomialCurve(x + y, (x, y))
        
        self.curves.append(("Unit Circle", circle))
        self.curves.append(("Line y=-x", line))
        
        self.update_curve_list()
        self.update_plot()
        self.find_intersections()
        
    def preset_two_circles(self):
        """Preset: Two intersecting circles"""
        self.clear_all()
        x, y = sp.symbols('x y')
        
        circle1 = ConicSection(x**2 + y**2 - 1, (x, y))
        circle2 = ConicSection((x-1)**2 + y**2 - 1, (x, y))
        
        self.curves.append(("Circle 1", circle1))
        self.curves.append(("Circle 2", circle2))
        
        self.update_curve_list()
        self.update_plot()
        self.find_intersections()
        
    def preset_parabola_line(self):
        """Preset: Parabola intersecting line"""
        self.clear_all()
        x, y = sp.symbols('x y')
        
        parabola = PolynomialCurve(y - x**2, (x, y))
        line = PolynomialCurve(y - 1, (x, y))
        
        self.curves.append(("Parabola y=x²", parabola))
        self.curves.append(("Line y=1", line))
        
        self.update_curve_list()
        self.update_plot()
        self.find_intersections()
    
    def preset_multi_segment(self):
        """Preset: Multi-segment curves with intersections"""
        self.clear_all()
        x, y = sp.symbols('x y')
        
        # Add a trimmed circle (half circle)
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        right_half_mask = lambda x_val, y_val: x_val >= 0
        trimmed_circle = TrimmedImplicitCurve(circle, right_half_mask)
        
        # Add a composite square
        square = create_square_from_edges((-0.5, -0.5), (0.5, 0.5))
        
        # Add a line that intersects both
        line = PolynomialCurve(y, (x, y))
        
        self.curves.append(("Right Half Circle", trimmed_circle))
        self.curves.append(("Square", square))
        self.curves.append(("Line y=0", line))
        
        self.update_curve_list()
        self.update_plot()
        self.find_intersections()
    
    def _create_two_semicircles(self):
        """Create a composite of two semicircles"""
        x, y = sp.symbols('x y')
        
        # Upper semicircle
        upper_circle = ConicSection(x**2 + y**2 - 1, (x, y))
        upper_mask = lambda x_val, y_val: y_val >= 0
        upper_semi = TrimmedImplicitCurve(upper_circle, upper_mask)
        
        # Lower semicircle (shifted)
        lower_circle = ConicSection(x**2 + (y-0.5)**2 - 0.25, (x, y))
        lower_mask = lambda x_val, y_val: y_val <= 0.5
        lower_semi = TrimmedImplicitCurve(lower_circle, lower_mask)
        
        # Create composite
        composite = CompositeCurve([upper_semi, lower_semi])
        return composite
        
    def _create_connected_arcs(self):
        """Create connected arcs forming a complex shape"""
        x, y = sp.symbols('x y')
        
        # Arc 1: quarter circle
        arc1_base = ConicSection((x-0.5)**2 + y**2 - 0.25, (x, y))
        arc1_mask = lambda x_val, y_val: (x_val >= 0.25) & (y_val >= 0)
        arc1 = TrimmedImplicitCurve(arc1_base, arc1_mask)
        
        # Arc 2: another quarter circle
        arc2_base = ConicSection((x+0.5)**2 + y**2 - 0.25, (x, y))
        arc2_mask = lambda x_val, y_val: (x_val <= -0.25) & (y_val >= 0)
        arc2 = TrimmedImplicitCurve(arc2_base, arc2_mask)
        
        # Create composite
        composite = CompositeCurve([arc1, arc2])
        return composite

def main():
    """Main function"""
    root = tk.Tk()
    app = CleanCurveVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()