#!/usr/bin/env python3
"""
Improved curve visualizer that properly handles intersections vs R-function operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
from geometry import *
from geometry.curve_intersections import find_curve_intersections, analyze_curve_intersections

class ImprovedCurveVisualizerApp:
    """Improved curve visualizer with proper intersection handling"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("2Top Improved Curve Visualizer")
        self.root.geometry("1400x900")
        
        # Current curves and settings
        self.curves = []
        self.curve_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Display options
        self.show_curves = tk.BooleanVar(value=True)
        self.show_intersections = tk.BooleanVar(value=True)
        self.show_regions = tk.BooleanVar(value=False)
        self.show_grid = tk.BooleanVar(value=True)
        
        # Current intersection points
        self.intersection_points = []
        
        # Setup UI
        self.setup_ui()
        
        # Add demo curves
        self.add_demo_curves()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Create main paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel for plot
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # Setup panels
        self.setup_control_panel(left_frame)
        self.setup_plot_panel(right_frame)
        
    def setup_control_panel(self, parent):
        """Setup control panel"""
        
        # Title
        title_label = ttk.Label(parent, text="Curve Visualizer", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Curve list section
        self.setup_curve_list(parent)
        
        # Add curves section
        self.setup_add_curves(parent)
        
        # Operations section
        self.setup_operations(parent)
        
        # Display options
        self.setup_display_options(parent)
        
        # Plot settings
        self.setup_plot_settings(parent)
        
    def setup_curve_list(self, parent):
        """Setup curve list section"""
        
        list_frame = ttk.LabelFrame(parent, text="Active Curves")
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Listbox
        self.curve_listbox = tk.Listbox(list_frame, height=6)
        self.curve_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Remove", command=self.remove_curve).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_curves).pack(side=tk.LEFT, padx=2)
        
    def setup_add_curves(self, parent):
        """Setup add curves section"""
        
        add_frame = ttk.LabelFrame(parent, text="Add Curves")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quick add buttons
        quick_frame = ttk.Frame(add_frame)
        quick_frame.pack(fill=tk.X, padx=5, pady=5)
        
        curves_data = [
            ("Circle", self.add_circle),
            ("Line", self.add_line),
            ("Ellipse", self.add_ellipse),
            ("Parabola", self.add_parabola),
        ]
        
        for i, (name, command) in enumerate(curves_data):
            row = i // 2
            col = i % 2
            ttk.Button(quick_frame, text=name, command=command).grid(
                row=row, column=col, padx=2, pady=2, sticky="ew")
        
        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)
        
        # Custom expression
        ttk.Label(add_frame, text="Custom f(x,y) = 0:").pack(anchor=tk.W, padx=5, pady=(10, 2))
        
        self.custom_expr = tk.StringVar(value="x**2 + y**2 - 4")
        expr_entry = ttk.Entry(add_frame, textvariable=self.custom_expr)
        expr_entry.pack(fill=tk.X, padx=5, pady=2)
        expr_entry.bind('<Return>', lambda e: self.add_custom_curve())
        
        ttk.Button(add_frame, text="Add Custom", 
                  command=self.add_custom_curve).pack(pady=5)
        
    def setup_operations(self, parent):
        """Setup operations section"""
        
        ops_frame = ttk.LabelFrame(parent, text="Curve Operations")
        ops_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Intersection analysis
        ttk.Button(ops_frame, text="Find All Intersections", 
                  command=self.find_all_intersections).pack(fill=tk.X, padx=5, pady=2)
        
        # R-function operations (clearly labeled)
        ttk.Label(ops_frame, text="R-Function Regions:", 
                 font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=5, pady=(10, 2))
        
        region_frame = ttk.Frame(ops_frame)
        region_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(region_frame, text="Union Region", 
                  command=self.add_union_region).pack(side=tk.LEFT, padx=2)
        ttk.Button(region_frame, text="Intersect Region", 
                  command=self.add_intersect_region).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(ops_frame, text="(Creates new curves representing combined regions)", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W, padx=5)
        
    def setup_display_options(self, parent):
        """Setup display options"""
        
        display_frame = ttk.LabelFrame(parent, text="Display Options")
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(display_frame, text="Show Curves", 
                       variable=self.show_curves, 
                       command=self.update_plot).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(display_frame, text="Show Intersection Points", 
                       variable=self.show_intersections,
                       command=self.update_plot).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(display_frame, text="Show Region Fills", 
                       variable=self.show_regions,
                       command=self.update_plot).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(display_frame, text="Show Grid", 
                       variable=self.show_grid,
                       command=self.update_plot).pack(anchor=tk.W, padx=5, pady=2)
        
    def setup_plot_settings(self, parent):
        """Setup plot settings"""
        
        settings_frame = ttk.LabelFrame(parent, text="Plot Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Resolution
        ttk.Label(settings_frame, text="Resolution:").pack(anchor=tk.W, padx=5)
        self.resolution = tk.IntVar(value=300)
        resolution_scale = ttk.Scale(settings_frame, from_=100, to=800, 
                                   variable=self.resolution, orient=tk.HORIZONTAL)
        resolution_scale.pack(fill=tk.X, padx=5, pady=2)
        
        # Range
        range_frame = ttk.Frame(settings_frame)
        range_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(range_frame, text="Range: ±").pack(side=tk.LEFT)
        self.plot_range = tk.DoubleVar(value=3.0)
        ttk.Entry(range_frame, textvariable=self.plot_range, width=8).pack(side=tk.LEFT)
        
        # Update button
        ttk.Button(settings_frame, text="Update Plot", 
                  command=self.update_plot).pack(pady=5)
        
    def setup_plot_panel(self, parent):
        """Setup plot panel"""
        
        # Create figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Setup plot style
        self.setup_plot_style()
        
    def setup_plot_style(self):
        """Setup plot styling"""
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.set_title('Implicit Curves with Intersection Points', fontsize=14, fontweight='bold')
        
    # Curve addition methods
    def add_circle(self):
        """Add a circle"""
        x, y = sp.symbols('x y')
        radius = np.random.uniform(0.8, 2.0)
        cx = np.random.uniform(-1, 1)
        cy = np.random.uniform(-1, 1)
        curve = ConicSection((x-cx)**2 + (y-cy)**2 - radius**2, (x, y))
        name = f"Circle (r={radius:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_line(self):
        """Add a line"""
        x, y = sp.symbols('x y')
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
        a = np.random.uniform(1.0, 2.5)
        b = np.random.uniform(0.5, 1.5)
        curve = ConicSection(x**2/a**2 + y**2/b**2 - 1, (x, y))
        name = f"Ellipse (a={a:.1f}, b={b:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_parabola(self):
        """Add a parabola"""
        x, y = sp.symbols('x y')
        a = np.random.uniform(0.2, 1.0)
        curve = PolynomialCurve(y - a*x**2, (x, y))
        name = f"Parabola (a={a:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_custom_curve(self):
        """Add custom curve"""
        try:
            x, y = sp.symbols('x y')
            expr_str = self.custom_expr.get()
            expr = sp.sympify(expr_str)
            curve = PolynomialCurve(expr, (x, y))
            name = f"Custom: {expr_str[:20]}..."
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {str(e)}")
    
    # Operations
    def find_all_intersections(self):
        """Find all intersection points between curves"""
        if len(self.curves) < 2:
            messagebox.showwarning("Warning", "Need at least 2 curves to find intersections")
            return
        
        self.intersection_points = []
        
        # Find pairwise intersections
        for i in range(len(self.curves)):
            for j in range(i + 1, len(self.curves)):
                name1, curve1 = self.curves[i]
                name2, curve2 = self.curves[j]
                
                intersections = find_curve_intersections(curve1, curve2, 
                                                       search_range=self.plot_range.get())
                
                for point in intersections:
                    self.intersection_points.append({
                        'point': point,
                        'curves': (name1, name2),
                        'type': 'intersection'
                    })
        
        # Update plot to show intersections
        self.update_plot()
        
        # Show results
        if self.intersection_points:
            result_msg = f"Found {len(self.intersection_points)} intersection points:\n\n"
            for i, data in enumerate(self.intersection_points):
                point = data['point']
                curves = data['curves']
                result_msg += f"{i+1}. ({point[0]:.4f}, {point[1]:.4f}) - {curves[0]} ∩ {curves[1]}\n"
            messagebox.showinfo("Intersection Results", result_msg)
        else:
            messagebox.showinfo("Intersection Results", "No intersections found")
    
    def add_union_region(self):
        """Add union region (R-function)"""
        if len(self.curves) < 2:
            messagebox.showwarning("Warning", "Need at least 2 curves for union region")
            return
        
        curve1 = self.curves[-1][1]
        curve2 = self.curves[-2][1]
        union_curve = union(curve1, curve2)
        name = f"Union Region ({len(self.curves)-1} ∪ {len(self.curves)})"
        self.curves.append((name, union_curve))
        self.update_curve_list()
        self.update_plot()
    
    def add_intersect_region(self):
        """Add intersection region (R-function)"""
        if len(self.curves) < 2:
            messagebox.showwarning("Warning", "Need at least 2 curves for intersection region")
            return
        
        curve1 = self.curves[-1][1]
        curve2 = self.curves[-2][1]
        intersect_curve = intersect(curve1, curve2)
        name = f"Intersect Region ({len(self.curves)-1} ∩ {len(self.curves)})"
        self.curves.append((name, intersect_curve))
        self.update_curve_list()
        self.update_plot()
    
    # Curve management
    def remove_curve(self):
        """Remove selected curve"""
        selection = self.curve_listbox.curselection()
        if selection:
            index = selection[0]
            del self.curves[index]
            self.update_curve_list()
            self.update_plot()
    
    def clear_curves(self):
        """Clear all curves"""
        self.curves.clear()
        self.intersection_points.clear()
        self.update_curve_list()
        self.update_plot()
    
    def update_curve_list(self):
        """Update curve listbox"""
        self.curve_listbox.delete(0, tk.END)
        for i, (name, curve) in enumerate(self.curves):
            self.curve_listbox.insert(tk.END, f"{i+1}. {name}")
    
    def update_plot(self):
        """Update the plot"""
        self.ax.clear()
        self.setup_plot_style()
        
        if not self.curves:
            self.canvas.draw()
            return
        
        # Get plot parameters
        resolution = self.resolution.get()
        plot_range = self.plot_range.get()
        
        # Create grid
        x_range = np.linspace(-plot_range, plot_range, resolution)
        y_range = np.linspace(-plot_range, plot_range, resolution)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Plot curves
        if self.show_curves.get():
            for i, (name, curve) in enumerate(self.curves):
                try:
                    Z = curve.evaluate(X, Y)
                    color = self.curve_colors[i % len(self.curve_colors)]
                    
                    # Plot curve boundary
                    self.ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2.5)
                    
                    # Plot filled regions if enabled
                    if self.show_regions.get():
                        self.ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                                       colors=[color, 'white'], alpha=0.2)
                    
                except Exception as e:
                    print(f"Error plotting {name}: {e}")
        
        # Plot intersection points
        if self.show_intersections.get() and self.intersection_points:
            for data in self.intersection_points:
                point = data['point']
                self.ax.plot(point[0], point[1], 'ko', markersize=8, 
                           markerfacecolor='red', markeredgecolor='black', 
                           markeredgewidth=2, zorder=10)
                
                # Add label
                self.ax.annotate(f'({point[0]:.2f}, {point[1]:.2f})', 
                               xy=point, xytext=(5, 5), 
                               textcoords='offset points', fontsize=8,
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Set plot limits and grid
        self.ax.set_xlim(-plot_range, plot_range)
        self.ax.set_ylim(-plot_range, plot_range)
        
        if self.show_grid.get():
            self.ax.grid(True, alpha=0.3)
        
        # Add legend
        if self.curves:
            legend_elements = []
            for i, (name, _) in enumerate(self.curves):
                color = self.curve_colors[i % len(self.curve_colors)]
                legend_elements.append(plt.Line2D([0], [0], color=color, lw=2.5, 
                                                label=name[:25] + "..." if len(name) > 25 else name))
            
            if self.intersection_points and self.show_intersections.get():
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                markerfacecolor='red', markeredgecolor='black',
                                                markersize=8, label='Intersections'))
            
            self.ax.legend(handles=legend_elements, loc='upper right', 
                          bbox_to_anchor=(1.0, 1.0), fontsize=9)
        
        self.canvas.draw()
    
    def add_demo_curves(self):
        """Add demo curves"""
        x, y = sp.symbols('x y')
        
        # Add intersecting curves
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        self.curves.append(("Unit Circle", circle))
        
        line = PolynomialCurve(x + y, (x, y))
        self.curves.append(("Line y=-x", line))
        
        self.update_curve_list()
        self.update_plot()

def main():
    """Main function"""
    root = tk.Tk()
    app = ImprovedCurveVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()