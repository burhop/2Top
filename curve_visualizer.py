#!/usr/bin/env python3
"""
Basic UI for visualizing implicit curves on a canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sympy as sp
from geometry import *

class CurveVisualizerApp:
    """Main application for visualizing implicit curves"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("2Top Implicit Curve Visualizer")
        self.root.geometry("1200x800")
        
        # Current curves to display
        self.curves = []
        self.curve_colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray']
        
        # Setup UI
        self.setup_ui()
        
        # Add some default curves
        self.add_default_curves()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel for plot
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup controls
        self.setup_controls(control_frame)
        
        # Setup plot
        self.setup_plot(plot_frame)
        
    def setup_controls(self, parent):
        """Setup control panel"""
        
        # Title
        title_label = ttk.Label(parent, text="Curve Controls", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Curve list
        list_frame = ttk.LabelFrame(parent, text="Active Curves")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.curve_listbox = tk.Listbox(list_container, height=8)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.curve_listbox.yview)
        self.curve_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.curve_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Curve type selection
        type_frame = ttk.LabelFrame(parent, text="Add New Curve")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.curve_type = tk.StringVar(value="Circle")
        curve_types = ["Circle", "Ellipse", "Line", "Parabola", "Superellipse", "Union", "Intersection"]
        
        for curve_type in curve_types:
            ttk.Radiobutton(type_frame, text=curve_type, variable=self.curve_type, 
                           value=curve_type).pack(anchor=tk.W, padx=5)
        
        # Add curve button
        ttk.Button(type_frame, text="Add Curve", command=self.add_curve).pack(pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_curve).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Clear All", command=self.clear_curves).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Refresh Plot", command=self.update_plot).pack(fill=tk.X, pady=2)
        
        # Plot settings
        settings_frame = ttk.LabelFrame(parent, text="Plot Settings")
        settings_frame.pack(fill=tk.X)
        
        # Grid resolution
        ttk.Label(settings_frame, text="Grid Resolution:").pack(anchor=tk.W, padx=5)
        self.resolution = tk.IntVar(value=200)
        resolution_scale = ttk.Scale(settings_frame, from_=50, to=500, variable=self.resolution, 
                                   orient=tk.HORIZONTAL, command=self.on_resolution_change)
        resolution_scale.pack(fill=tk.X, padx=5, pady=2)
        
        self.resolution_label = ttk.Label(settings_frame, text="200")
        self.resolution_label.pack(anchor=tk.W, padx=5)
        
        # Plot range
        ttk.Label(settings_frame, text="Plot Range:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        range_frame = ttk.Frame(settings_frame)
        range_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(range_frame, text="±").pack(side=tk.LEFT)
        self.plot_range = tk.DoubleVar(value=3.0)
        range_entry = ttk.Entry(range_frame, textvariable=self.plot_range, width=8)
        range_entry.pack(side=tk.LEFT, padx=2)
        range_entry.bind('<Return>', lambda e: self.update_plot())
        
    def setup_plot(self, parent):
        """Setup matplotlib plot"""
        
        # Create figure
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Setup initial plot
        self.setup_plot_style()
        
    def setup_plot_style(self):
        """Setup plot styling"""
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Implicit Curves Visualization')
        
    def add_default_curves(self):
        """Add some default curves to demonstrate"""
        x, y = sp.symbols('x y')
        
        # Add a circle
        circle = ConicSection(x**2 + y**2 - 1, (x, y))
        self.curves.append(("Circle (unit)", circle))
        
        # Add an ellipse
        ellipse = ConicSection(x**2/4 + y**2 - 1, (x, y))
        self.curves.append(("Ellipse", ellipse))
        
        # Add a line
        line = PolynomialCurve(x + y, (x, y))
        self.curves.append(("Line (x+y=0)", line))
        
        self.update_curve_list()
        self.update_plot()
        
    def add_curve(self):
        """Add a new curve based on selection"""
        x, y = sp.symbols('x y')
        curve_type = self.curve_type.get()
        
        try:
            if curve_type == "Circle":
                # Random circle
                radius = np.random.uniform(0.5, 2.0)
                cx = np.random.uniform(-1, 1)
                cy = np.random.uniform(-1, 1)
                curve = ConicSection((x-cx)**2 + (y-cy)**2 - radius**2, (x, y))
                name = f"Circle (r={radius:.1f})"
                
            elif curve_type == "Ellipse":
                # Random ellipse
                a = np.random.uniform(0.5, 2.0)
                b = np.random.uniform(0.5, 2.0)
                curve = ConicSection(x**2/a**2 + y**2/b**2 - 1, (x, y))
                name = f"Ellipse (a={a:.1f}, b={b:.1f})"
                
            elif curve_type == "Line":
                # Random line
                slope = np.random.uniform(-2, 2)
                intercept = np.random.uniform(-1, 1)
                curve = PolynomialCurve(y - slope*x - intercept, (x, y))
                name = f"Line (y={slope:.1f}x+{intercept:.1f})"
                
            elif curve_type == "Parabola":
                # Random parabola
                a = np.random.uniform(0.2, 2.0)
                h = np.random.uniform(-1, 1)
                k = np.random.uniform(-1, 1)
                curve = PolynomialCurve(y - a*(x-h)**2 - k, (x, y))
                name = f"Parabola (a={a:.1f})"
                
            elif curve_type == "Superellipse":
                # Random superellipse
                a = np.random.uniform(0.8, 1.5)
                b = np.random.uniform(0.8, 1.5)
                n = np.random.choice([0.5, 1.5, 2.0, 4.0, 8.0])
                curve = Superellipse(a=a, b=b, n=n, variables=(x, y))
                name = f"Superellipse (n={n})"
                
            elif curve_type == "Union":
                if len(self.curves) >= 2:
                    # Union of last two curves
                    curve1 = self.curves[-1][1]
                    curve2 = self.curves[-2][1]
                    curve = union(curve1, curve2)
                    name = "Union of last 2"
                else:
                    messagebox.showwarning("Warning", "Need at least 2 curves for union")
                    return
                    
            elif curve_type == "Intersection":
                if len(self.curves) >= 2:
                    # Intersection of last two curves
                    curve1 = self.curves[-1][1]
                    curve2 = self.curves[-2][1]
                    curve = intersect(curve1, curve2)
                    name = "Intersection of last 2"
                else:
                    messagebox.showwarning("Warning", "Need at least 2 curves for intersection")
                    return
            
            # Add to list
            self.curves.append((name, curve))
            self.update_curve_list()
            self.update_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create curve: {str(e)}")
    
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
    
    def update_curve_list(self):
        """Update the curve listbox"""
        self.curve_listbox.delete(0, tk.END)
        for i, (name, curve) in enumerate(self.curves):
            color = self.curve_colors[i % len(self.curve_colors)]
            self.curve_listbox.insert(tk.END, f"{name} ({color})")
    
    def on_resolution_change(self, value):
        """Handle resolution slider change"""
        self.resolution_label.config(text=str(int(float(value))))
    
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
                self.ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=2)
                
                # Add filled contour for inside/outside visualization
                self.ax.contourf(X, Y, Z, levels=[-1000, 0, 1000], 
                               colors=[color, 'white'], alpha=0.1)
                
            except Exception as e:
                print(f"Error plotting {name}: {e}")
        
        # Set plot limits
        self.ax.set_xlim(-plot_range, plot_range)
        self.ax.set_ylim(-plot_range, plot_range)
        
        # Add legend
        if self.curves:
            legend_elements = []
            for i, (name, _) in enumerate(self.curves):
                color = self.curve_colors[i % len(self.curve_colors)]
                legend_elements.append(plt.Line2D([0], [0], color=color, lw=2, label=name))
            
            self.ax.legend(handles=legend_elements, loc='upper right', 
                          bbox_to_anchor=(1.0, 1.0), fontsize=8)
        
        self.canvas.draw()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CurveVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()