"""
Plotting utilities for visual tests.

Provides consistent plotting functionality across all visual tests,
including curve plotting, region visualization, and grid management.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from typing import Tuple, List, Optional, Any
import traceback

# Configure matplotlib for better display and headless safety
plt.ion()  # interactive mode if a GUI backend is available
try:
    plt.switch_backend('TkAgg')  # Prefer TkAgg on Windows if available
except Exception:
    # Keep current backend (often 'Agg' in headless CI); we'll auto-save in that case
    pass


class PlotManager:
    """
    Manages consistent plotting across all visual tests.
    
    Provides standardized methods for plotting curves, regions,
    and test grids with consistent styling and error handling.
    """
    
    def __init__(self, figsize: Tuple[float, float] = (12, 10)):
        """
        Initialize the plot manager.
        
        Args:
            figsize: Default figure size for plots
        """
        self.figsize = figsize
        self.default_xlim = (-3, 3)
        self.default_ylim = (-3, 3)
        self.default_grid_size = 100
        
    def setup_figure(self, rows: int = 1, cols: int = 1, 
                    figsize: Optional[Tuple[float, float]] = None,
                    suptitle: Optional[str] = None) -> Tuple[plt.Figure, Any]:
        """
        Set up a matplotlib figure with consistent styling.
        
        Args:
            rows: Number of subplot rows
            cols: Number of subplot columns
            figsize: Figure size override
            suptitle: Super title for the figure
            
        Returns:
            Tuple of (figure, axes)
        """
        if figsize is None:
            figsize = self.figsize
            
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        
        if suptitle:
            fig.suptitle(suptitle, fontsize=16)
            
        return fig, axes
    
    def create_test_grid(self, xlim: Tuple[float, float] = None,
                        ylim: Tuple[float, float] = None,
                        grid_size: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a uniform test grid for evaluation.
        
        Args:
            xlim: X-axis limits (min, max)
            ylim: Y-axis limits (min, max)
            grid_size: Number of points along each axis
            
        Returns:
            Tuple of (X, Y) coordinate meshgrids
        """
        if xlim is None:
            xlim = self.default_xlim
        if ylim is None:
            ylim = self.default_ylim
        if grid_size is None:
            grid_size = self.default_grid_size
            
        x_range = np.linspace(xlim[0], xlim[1], grid_size)
        y_range = np.linspace(ylim[0], ylim[1], grid_size)
        X, Y = np.meshgrid(x_range, y_range)
        
        return X, Y
    
    def plot_curve_contour(self, ax: plt.Axes, curve: Any, X: np.ndarray, Y: np.ndarray,
                          title: str = "", color: str = 'blue', 
                          show_levels: bool = True, linewidth: float = 2) -> None:
        """
        Plot a curve using contour lines.
        
        Args:
            ax: Matplotlib axes to plot on
            curve: Curve object with evaluate method
            X: X coordinate meshgrid
            Y: Y coordinate meshgrid
            title: Plot title
            color: Curve color
            show_levels: Whether to show additional level curves
            linewidth: Line width for the curve
        """
        try:
            # Evaluate curve over the grid (vectorized with safe fallback)
            try:
                Z = np.asarray(curve.evaluate(X, Y))
                if Z.shape != X.shape:
                    # Some implementations might return flat array; reshape or fallback
                    Z = Z.reshape(X.shape)
            except Exception:
                Z = np.zeros_like(X)
                for i in range(X.shape[0]):
                    for j in range(X.shape[1]):
                        try:
                            Z[i, j] = curve.evaluate(X[i, j], Y[i, j])
                        except Exception:
                            Z[i, j] = np.nan
            
            # Plot zero level (the actual curve)
            try:
                cs0 = ax.contour(X, Y, Z, levels=[0], colors=[color], linewidths=linewidth)
            except Exception as e:
                # If contouring fails (e.g., all-NaN), show a warning in-plot
                ax.text(0.5, 0.5, "No contour at level 0", transform=ax.transAxes,
                        ha='center', va='center', fontsize=10, color='orange')
            
            # Plot additional level curves if requested
            if show_levels:
                try:
                    ax.contour(X, Y, Z, levels=[-2, -1, -0.5, 0.5, 1, 2],
                              colors='gray', alpha=0.3, linewidths=0.5)
                except Exception:
                    # Ignore auxiliary levels if they fail
                    pass
            
            self._apply_standard_styling(ax, title)
            
        except Exception as e:
            print(f"Error plotting curve '{title}': {e}")
            ax.text(0.5, 0.5, f"Error: {str(e)}", transform=ax.transAxes,
                   ha='center', va='center', fontsize=10, color='red')
            self._apply_standard_styling(ax, f"{title} (ERROR)")
    
    def plot_region_filled(self, ax: Any, region: Any, X: np.ndarray, Y: np.ndarray,
                           title: str = '', fill_color: str = 'lightblue', 
                           boundary_color: str = 'red', point_size: float = 1.0) -> None:
        """
        Plot a filled region by testing containment over a grid.

        Parameters:
            ax: Matplotlib axes
            region: AreaRegion-like object with contains methods
            X, Y: Grid arrays
            title: Plot title
            fill_color: Fill color for interior points
            boundary_color: Color for boundary points
            point_size: Size of plotted points
        """
        try:
            # Prefer robust evaluator for containment to avoid vectorization pitfalls
            try:
                # Local import to avoid circular dependency
                from visual_tests.utils.grid_evaluation import GridEvaluator
                evaluator = GridEvaluator()
                inside_mask, boundary_mask = evaluator.evaluate_region_containment(
                    region, X, Y, test_boundary=True
                )
            except Exception:
                # Fallback to conservative per-point evaluation
                inside_mask = np.zeros_like(X, dtype=bool)
                boundary_mask = np.zeros_like(X, dtype=bool)
                for i in range(X.shape[0]):
                    for j in range(X.shape[1]):
                        try:
                            inside_mask[i, j] = region.contains(X[i, j], Y[i, j])
                        except Exception:
                            inside_mask[i, j] = False
                        try:
                            if hasattr(region, 'contains_boundary'):
                                boundary_mask[i, j] = region.contains_boundary(X[i, j], Y[i, j])
                            else:
                                boundary_mask[i, j] = region.contains(X[i, j], Y[i, j], region_containment=False)
                        except Exception:
                            boundary_mask[i, j] = False
            
            # Plot filled area
            inside_points = np.where(inside_mask)
            boundary_points = np.where(boundary_mask)

            if len(inside_points[0]) == 0 and len(boundary_points[0]) == 0:
                ax.text(0.5, 0.5, "No region points detected", transform=ax.transAxes,
                       ha='center', va='center', fontsize=10, color='orange')
            else:
                ax.scatter(X[inside_points], Y[inside_points], s=point_size, c=fill_color, label=f"Inside ({len(inside_points[0])} points)", edgecolors='none', alpha=0.6)
                if len(boundary_points[0]) > 0:
                    ax.scatter(X[boundary_points], Y[boundary_points], s=point_size*1.5, c=boundary_color, label=f"Boundary ({len(boundary_points[0])} points)", alpha=0.8)

            # Overlay explicit boundary contour from region's boundary curve, if available
            try:
                boundary_curve = getattr(region, 'outer_boundary', None) or getattr(region, 'boundary', None)
                if boundary_curve is not None and hasattr(boundary_curve, 'evaluate'):
                    try:
                        Zb = np.asarray(boundary_curve.evaluate(X, Y))
                        if Zb.shape != X.shape:
                            Zb = Zb.reshape(X.shape)
                        ax.contour(X, Y, Zb, levels=[0], colors=[boundary_color], linewidths=1.0)
                    except Exception:
                        # If composite, try to iterate components
                        for seg in getattr(boundary_curve, 'curves', []):
                            try:
                                Zs = np.asarray(seg.evaluate(X, Y))
                                if Zs.shape != X.shape:
                                    Zs = Zs.reshape(X.shape)
                                ax.contour(X, Y, Zs, levels=[0], colors=[boundary_color], linewidths=1.0)
                            except Exception:
                                continue
            except Exception:
                pass
            
            self._apply_standard_styling(ax, title)
            ax.legend(fontsize=8)
            
        except Exception as e:
            print(f"Error plotting region '{title}': {e}")
            ax.text(0.5, 0.5, f"Error: {str(e)}", transform=ax.transAxes,
                   ha='center', va='center', fontsize=10, color='red')
            self._apply_standard_styling(ax, f"{title} (ERROR)")
    
    def plot_test_points(self, ax: plt.Axes, X: np.ndarray, Y: np.ndarray, 
                        inside_mask: np.ndarray, title: str = "",
                        inside_color: str = 'red', outside_color: str = 'black',
                        point_size: float = 1) -> None:
        """
        Plot test points colored by containment status.
        
        Args:
            ax: Matplotlib axes to plot on
            X: X coordinate meshgrid
            Y: Y coordinate meshgrid
            inside_mask: Boolean mask indicating which points are inside
            title: Plot title
            inside_color: Color for inside points
            outside_color: Color for outside points
            point_size: Size of plotted points
        """
        try:
            # Plot inside points
            inside_points = np.where(inside_mask)
            if len(inside_points[0]) > 0:
                ax.scatter(X[inside_points], Y[inside_points], 
                          c=inside_color, s=point_size, alpha=0.7,
                          label=f'Inside ({len(inside_points[0])} points)')
            
            # Plot outside points
            outside_mask = ~inside_mask
            outside_points = np.where(outside_mask)
            if len(outside_points[0]) > 0:
                ax.scatter(X[outside_points], Y[outside_points], 
                          c=outside_color, s=point_size, alpha=0.3,
                          label=f'Outside ({len(outside_points[0])} points)')
            
            self._apply_standard_styling(ax, title)
            ax.legend(fontsize=8)
            
        except Exception as e:
            print(f"Error plotting test points '{title}': {e}")
            ax.text(0.5, 0.5, f"Error: {str(e)}", transform=ax.transAxes,
                   ha='center', va='center', fontsize=10, color='red')
            self._apply_standard_styling(ax, f"{title} (ERROR)")
    
    def _apply_standard_styling(self, ax: plt.Axes, title: str) -> None:
        """
        Apply consistent styling to an axes.
        
        Args:
            ax: Matplotlib axes to style
            title: Title for the axes
        """
        ax.set_title(title, fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(self.default_xlim)
        ax.set_ylim(self.default_ylim)
        ax.tick_params(labelsize=8)
    
    def save_or_show(self, filename: Optional[str] = None, dpi: int = 100) -> None:
        """
        Save plot to file or show it with improved display handling.
        
        Args:
            filename: If provided, save to this file. Otherwise show the plot.
            dpi: DPI for saved images
        """
        try:
            plt.tight_layout()

            # Detect headless/non-interactive backends
            backend = mpl.get_backend().lower()
            headless = 'agg' in backend or 'pdf' in backend or 'svg' in backend

            # Ensure output directory exists when saving
            out_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
            out_dir = os.path.abspath(out_dir)
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception:
                pass

            if filename is None and headless:
                # Auto-generate filename in output directory
                import time as _time
                filename = os.path.join(out_dir, f"visual_{int(_time.time())}.png")

            if filename:
                plt.savefig(filename, dpi=dpi, bbox_inches='tight')
                print(f"Plot saved to {filename}")
            else:
                # Non-blocking show for interactive backends
                plt.show(block=False)
                plt.draw()
                plt.pause(0.2)
                
        except Exception as e:
            print(f"Error saving/showing plot: {e}")
            # Try alternative display methods
            try:
                plt.draw()
                plt.pause(0.1)
            except:
                print("Unable to display plot - check matplotlib backend")
    
    def print_statistics(self, inside_mask: np.ndarray, boundary_mask: Optional[np.ndarray] = None) -> None:
        """
        Print statistics about point classification.
        
        Args:
            inside_mask: Boolean mask for inside points
            boundary_mask: Optional boolean mask for boundary points
        """
        total_points = inside_mask.size
        inside_count = np.sum(inside_mask)
        
        print(f"\n{'='*50}")
        print("POINT CLASSIFICATION STATISTICS")
        print(f"{'='*50}")
        print(f"Total grid points: {total_points}")
        print(f"Inside points:     {inside_count} ({100*inside_count/total_points:.1f}%)")
        
        if boundary_mask is not None:
            boundary_count = np.sum(boundary_mask)
            outside_count = total_points - inside_count - boundary_count
            print(f"Boundary points:   {boundary_count} ({100*boundary_count/total_points:.1f}%)")
            print(f"Outside points:    {outside_count} ({100*outside_count/total_points:.1f}%)")
        else:
            outside_count = total_points - inside_count
            print(f"Outside points:    {outside_count} ({100*outside_count/total_points:.1f}%)")
