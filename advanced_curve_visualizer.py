#!/usr/bin/env python3
"""
Advanced UI for visualizing implicit curves with interactive features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
from geometry import *
import json

class AdvancedCurveVisualizerApp:
    """Advanced application for visualizing implicit curves"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("2Top Advanced Curve Visualizer")
        self.root.geometry("1400x900")
        
        # Current curves and settings
        self.curves = []
        self.curve_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self.show_grid = tk.BooleanVar(value=True)
        self.show_filled = tk.BooleanVar(value=True)
        self.show_gradients = tk.BooleanVar(value=False)
        
        # Setup UI
        self.setup_ui()
        
        # Add demo curves
        self.add_demo_curves()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main visualization tab
        self.main_tab = ttk.Frame(notebook)
        notebook.add(self.main_tab, text="Curve Visualizer")
        
        # Gallery tab
        self.gallery_tab = ttk.Frame(notebook)
        notebook.add(self.gallery_tab, text="Curve Gallery")
        
        # Setup main tab
        self.setup_main_tab()
        
        # Setup gallery tab
        self.setup_gallery_tab()
        
    def setup_main_tab(self):
        """Setup main visualization tab"""
        
        # Create paned window
        paned = ttk.PanedWindow(self.main_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # Setup panels
        self.setup_control_panel(left_frame)
        self.setup_plot_panel(right_frame)
        
    def setup_control_panel(self, parent):
        """Setup control panel"""
        
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Curve Controls", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Active curves section
        self.setup_curve_list(scrollable_frame)
        
        # Add curve section
        self.setup_add_curve(scrollable_frame)
        
        # Custom expression section
        self.setup_custom_expression(scrollable_frame)
        
        # Plot settings section
        self.setup_plot_settings(scrollable_frame)
        
        # File operations
        self.setup_file_operations(scrollable_frame)
        
    def setup_curve_list(self, parent):
        """Setup curve list section"""
        
        list_frame = ttk.LabelFrame(parent, text="Active Curves")
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.X, padx=5, pady=5)
        
        self.curve_listbox = tk.Listbox(list_container, height=6)
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                      command=self.curve_listbox.yview)
        self.curve_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.curve_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Remove", command=self.remove_curve).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_curves).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Duplicate", command=self.duplicate_curve).pack(side=tk.LEFT, padx=2)
        
    def setup_add_curve(self, parent):
        """Setup add curve section"""
        
        add_frame = ttk.LabelFrame(parent, text="Quick Add Curves")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Predefined curves
        curves_data = [
            ("Circle", lambda: self.add_circle()),
            ("Ellipse", lambda: self.add_ellipse()),
            ("Line", lambda: self.add_line()),
            ("Parabola", lambda: self.add_parabola()),
            ("Hyperbola", lambda: self.add_hyperbola()),
            ("Superellipse", lambda: self.add_superellipse()),
        ]
        
        for i, (name, command) in enumerate(curves_data):
            row = i // 2
            col = i % 2
            ttk.Button(add_frame, text=name, command=command).grid(
                row=row, column=col, padx=2, pady=2, sticky="ew")
        
        add_frame.columnconfigure(0, weight=1)
        add_frame.columnconfigure(1, weight=1)
        
        # Constructive operations
        ops_frame = ttk.LabelFrame(parent, text="Constructive Operations")
        ops_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(ops_frame, text="Union", command=self.add_union).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(ops_frame, text="Intersect", command=self.add_intersection).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(ops_frame, text="Difference", command=self.add_difference).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(ops_frame, text="Blend", command=self.add_blend).pack(side=tk.LEFT, padx=2, pady=2)
        
    def setup_custom_expression(self, parent):
        """Setup custom expression section"""
        
        expr_frame = ttk.LabelFrame(parent, text="Custom Expression")
        expr_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(expr_frame, text="Enter f(x,y) = 0:").pack(anchor=tk.W, padx=5, pady=2)
        
        self.custom_expr = tk.StringVar(value="x**2 + y**2 - 1")
        expr_entry = ttk.Entry(expr_frame, textvariable=self.custom_expr)
        expr_entry.pack(fill=tk.X, padx=5, pady=2)
        expr_entry.bind('<Return>', lambda e: self.add_custom_curve())
        
        ttk.Button(expr_frame, text="Add Custom Curve", 
                  command=self.add_custom_curve).pack(pady=5)
        
        # Examples
        examples_frame = ttk.Frame(expr_frame)
        examples_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(examples_frame, text="Examples:", font=('Arial', 8)).pack(anchor=tk.W)
        
        examples = [
            "x**2 + y**2 - 1  (circle)",
            "x**2/4 + y**2 - 1  (ellipse)",
            "y - x**2  (parabola)",
            "x**2 - y**2 - 1  (hyperbola)",
            "x**3 + y**3 - 1  (cubic)",
        ]
        
        for example in examples:
            label = ttk.Label(examples_frame, text=example, font=('Arial', 7), 
                            foreground='gray')
            label.pack(anchor=tk.W)
            label.bind("<Button-1>", lambda e, ex=example.split('  ')[0]: 
                      self.custom_expr.set(ex))
        
    def setup_plot_settings(self, parent):
        """Setup plot settings section"""
        
        settings_frame = ttk.LabelFrame(parent, text="Plot Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Resolution
        ttk.Label(settings_frame, text="Resolution:").pack(anchor=tk.W, padx=5)
        self.resolution = tk.IntVar(value=300)
        resolution_scale = ttk.Scale(settings_frame, from_=100, to=1000, 
                                   variable=self.resolution, orient=tk.HORIZONTAL)
        resolution_scale.pack(fill=tk.X, padx=5, pady=2)
        
        # Range
        range_frame = ttk.Frame(settings_frame)
        range_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(range_frame, text="Range: ±").pack(side=tk.LEFT)
        self.plot_range = tk.DoubleVar(value=3.0)
        ttk.Entry(range_frame, textvariable=self.plot_range, width=8).pack(side=tk.LEFT)
        
        # Checkboxes
        ttk.Checkbutton(settings_frame, text="Show Grid", 
                       variable=self.show_grid).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text="Show Filled Regions", 
                       variable=self.show_filled).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text="Show Gradient Vectors", 
                       variable=self.show_gradients).pack(anchor=tk.W, padx=5, pady=2)
        
        # Update button
        ttk.Button(settings_frame, text="Update Plot", 
                  command=self.update_plot).pack(pady=5)
        
    def setup_file_operations(self, parent):
        """Setup file operations section"""
        
        file_frame = ttk.LabelFrame(parent, text="File Operations")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Save Plot", command=self.save_plot).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(file_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=2, pady=2)
        
    def setup_plot_panel(self, parent):
        """Setup plot panel"""
        
        # Create figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        
        # Pack widgets
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Setup plot style
        self.setup_plot_style()
        
    def setup_gallery_tab(self):
        """Setup gallery tab with predefined interesting curves"""
        
        gallery_frame = ttk.Frame(self.gallery_tab)
        gallery_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(gallery_frame, text="Curve Gallery", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 10))
        
        # Gallery items
        gallery_items = [
            ("Heart Curve", "((x**2 + y**2 - 1)**3) - (x**2 * y**3)", "A heart-shaped curve"),
            ("Lemniscate", "(x**2 + y**2)**2 - 2*(x**2 - y**2)", "Figure-eight curve"),
            ("Cardioid", "(x**2 + y**2 - 2*x)**2 - 4*(x**2 + y**2)", "Heart-like curve"),
            ("Astroid", "x**(2/3) + y**(2/3) - 1", "Four-pointed star"),
            ("Folium of Descartes", "x**3 + y**3 - 3*x*y", "Loop with asymptote"),
            ("Cassini Oval", "(x**2 + y**2)**2 - 2*(x**2 - y**2) - 1", "Oval-like curve"),
        ]
        
        # Create scrollable frame for gallery
        canvas = tk.Canvas(gallery_frame)
        scrollbar = ttk.Scrollbar(gallery_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for name, expr, desc in gallery_items:
            item_frame = ttk.LabelFrame(scrollable_frame, text=name)
            item_frame.pack(fill=tk.X, pady=5, padx=5)
            
            ttk.Label(item_frame, text=f"Expression: {expr}", 
                     font=('Courier', 9)).pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(item_frame, text=desc, 
                     font=('Arial', 9), foreground='gray').pack(anchor=tk.W, padx=5, pady=2)
            
            ttk.Button(item_frame, text="Add to Plot", 
                      command=lambda e=expr, n=name: self.add_gallery_curve(e, n)).pack(pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_plot_style(self):
        """Setup plot styling"""
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.set_title('Implicit Curves Visualization', fontsize=14, fontweight='bold')
        
    # Curve addition methods
    def add_circle(self):
        """Add a random circle"""
        x, y = sp.symbols('x y')
        radius = np.random.uniform(0.5, 2.0)
        cx = np.random.uniform(-1, 1)
        cy = np.random.uniform(-1, 1)
        curve = ConicSection((x-cx)**2 + (y-cy)**2 - radius**2, (x, y))
        name = f"Circle (r={radius:.1f}, center=({cx:.1f},{cy:.1f}))"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_ellipse(self):
        """Add a random ellipse"""
        x, y = sp.symbols('x y')
        a = np.random.uniform(0.8, 2.0)
        b = np.random.uniform(0.8, 2.0)
        curve = ConicSection(x**2/a**2 + y**2/b**2 - 1, (x, y))
        name = f"Ellipse (a={a:.1f}, b={b:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_line(self):
        """Add a random line"""
        x, y = sp.symbols('x y')
        slope = np.random.uniform(-2, 2)
        intercept = np.random.uniform(-1, 1)
        curve = PolynomialCurve(y - slope*x - intercept, (x, y))
        name = f"Line (slope={slope:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_parabola(self):
        """Add a random parabola"""
        x, y = sp.symbols('x y')
        a = np.random.uniform(0.2, 1.0)
        curve = PolynomialCurve(y - a*x**2, (x, y))
        name = f"Parabola (a={a:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_hyperbola(self):
        """Add a random hyperbola"""
        x, y = sp.symbols('x y')
        a = np.random.uniform(0.5, 1.5)
        b = np.random.uniform(0.5, 1.5)
        curve = ConicSection(x**2/a**2 - y**2/b**2 - 1, (x, y))
        name = f"Hyperbola (a={a:.1f}, b={b:.1f})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_superellipse(self):
        """Add a random superellipse"""
        x, y = sp.symbols('x y')
        a = np.random.uniform(0.8, 1.5)
        b = np.random.uniform(0.8, 1.5)
        n = np.random.choice([0.5, 1.5, 2.0, 4.0, 8.0])
        curve = Superellipse(a=a, b=b, n=n, variables=(x, y))
        name = f"Superellipse (n={n})"
        self.curves.append((name, curve))
        self.update_curve_list()
        self.update_plot()
        
    def add_custom_curve(self):
        """Add custom curve from expression"""
        try:
            x, y = sp.symbols('x y')
            expr_str = self.custom_expr.get()
            expr = sp.sympify(expr_str)
            curve = PolynomialCurve(expr, (x, y))
            name = f"Custom: {expr_str}"
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {str(e)}")
            
    def add_gallery_curve(self, expr_str, name):
        """Add curve from gallery"""
        try:
            x, y = sp.symbols('x y')
            expr = sp.sympify(expr_str)
            curve = PolynomialCurve(expr, (x, y))
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add {name}: {str(e)}")
    
    # Constructive operations
    def add_union(self):
        """Add union of selected curves"""
        if len(self.curves) >= 2:
            curve1 = self.curves[-1][1]
            curve2 = self.curves[-2][1]
            curve = union(curve1, curve2)
            name = f"Union of last 2 curves"
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        else:
            messagebox.showwarning("Warning", "Need at least 2 curves for union")
            
    def add_intersection(self):
        """Add intersection of selected curves"""
        if len(self.curves) >= 2:
            curve1 = self.curves[-1][1]
            curve2 = self.curves[-2][1]
            curve = intersect(curve1, curve2)
            name = f"Intersection of last 2 curves"
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        else:
            messagebox.showwarning("Warning", "Need at least 2 curves for intersection")
            
    def add_difference(self):
        """Add difference of selected curves"""
        if len(self.curves) >= 2:
            curve1 = self.curves[-1][1]
            curve2 = self.curves[-2][1]
            curve = difference(curve1, curve2)
            name = f"Difference of last 2 curves"
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        else:
            messagebox.showwarning("Warning", "Need at least 2 curves for difference")
            
    def add_blend(self):
        """Add blend of selected curves"""
        if len(self.curves) >= 2:
            curve1 = self.curves[-1][1]
            curve2 = self.curves[-2][1]
            alpha = 0.5  # Could make this configurable
            curve = blend(curve1, curve2, alpha=alpha)
            name = f"Blend of last 2 curves (α={alpha})"
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
        else:
            messagebox.showwarning("Warning", "Need at least 2 curves for blend")
    
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
        self.update_curve_list()
        self.update_plot()
        
    def duplicate_curve(self):
        """Duplicate selected curve"""
        selection = self.curve_listbox.curselection()
        if selection:
            index = selection[0]
            name, curve = self.curves[index]
            new_name = f"{name} (copy)"
            self.curves.append((new_name, curve))
            self.update_curve_list()
            self.update_plot()
    
    def update_curve_list(self):
        """Update the curve listbox"""
        self.curve_listbox.delete(0, tk.END)
        for i, (name, curve) in enumerate(self.curves):
            color = self.curve_colors[i % len(self.curve_colors)]
            self.curve_listbox.insert(tk.END, f"{name}")
    
    def update_plot(self):
        """Update the plot with current curves"""
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
        
        # Plot each curve
        for i, (name, curve) in enumerate(self.curves):
            try:
                # Evaluate curve on grid
                Z = curve.evaluate(X, Y)
                
                # Plot zero-level contour
                color = self.curve_colors[i % len(self.curve_colors)]
                
                # Main curve
                self.ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2.5)
                
                # Filled regions if enabled
                if self.show_filled.get():
                    self.ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                                   colors=[color, 'white'], alpha=0.15)
                
                # Gradient vectors if enabled
                if self.show_gradients.get() and i == 0:  # Only for first curve to avoid clutter
                    # Sample gradient at fewer points
                    step = max(1, resolution // 20)
                    X_grad = X[::step, ::step]
                    Y_grad = Y[::step, ::step]
                    
                    # Compute gradients
                    gx, gy = curve.gradient(X_grad, Y_grad)
                    
                    # Normalize for display
                    magnitude = np.sqrt(gx**2 + gy**2)
                    magnitude = np.where(magnitude == 0, 1, magnitude)
                    gx_norm = gx / magnitude
                    gy_norm = gy / magnitude
                    
                    # Plot arrows
                    self.ax.quiver(X_grad, Y_grad, gx_norm, gy_norm, 
                                  alpha=0.6, scale=20, color='red', width=0.002)
                
            except Exception as e:
                print(f"Error plotting {name}: {e}")
        
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
                                                label=name[:30] + "..." if len(name) > 30 else name))
            
            self.ax.legend(handles=legend_elements, loc='upper right', 
                          bbox_to_anchor=(1.0, 1.0), fontsize=8, 
                          framealpha=0.9)
        
        self.canvas.draw()
    
    def save_plot(self):
        """Save the current plot"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), 
                      ("SVG files", "*.svg"), ("All files", "*.*")]
        )
        if filename:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Plot saved to {filename}")
    
    def export_data(self):
        """Export curve data"""
        if not self.curves:
            messagebox.showwarning("Warning", "No curves to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                data = {
                    'curves': [],
                    'settings': {
                        'resolution': self.resolution.get(),
                        'plot_range': self.plot_range.get(),
                        'show_grid': self.show_grid.get(),
                        'show_filled': self.show_filled.get(),
                    }
                }
                
                for name, curve in self.curves:
                    curve_data = {
                        'name': name,
                        'type': type(curve).__name__,
                        'serialized': curve.to_dict()
                    }
                    data['curves'].append(curve_data)
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def add_demo_curves(self):
        """Add some demo curves"""
        x, y = sp.symbols('x y')
        
        # Add a few interesting curves
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        self.curves.append(("Unit Circle", circle))
        
        ellipse = ConicSection(x**2/4 + y**2/2.25 - 1, (x, y))
        self.curves.append(("Ellipse", ellipse))
        
        self.update_curve_list()
        self.update_plot()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = AdvancedCurveVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()