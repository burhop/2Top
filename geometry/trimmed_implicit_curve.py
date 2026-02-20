"""
TrimmedImplicitCurve - Curve Segmentation

This module implements the TrimmedImplicitCurve class for Sprint 5, enabling
the representation of segments of implicit curves defined by mask functions.

The TrimmedImplicitCurve wraps a base ImplicitCurve and applies a mask function
to define which portions of the curve are included in the segment.

Key Features:
- Wraps any ImplicitCurve as a base curve
- Applies callable mask function to define included regions
- contains() method checks both curve membership and mask satisfaction
- Full inheritance from ImplicitCurve interface
- Specialized plotting for masked portions only
- Serialization support with mask function limitations
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Union, Dict, Any, Callable, List
from .implicit_curve import ImplicitCurve


class TrimmedImplicitCurve(ImplicitCurve):
    """
    TrimmedImplicitCurve represents a segment of an implicit curve defined by a mask function.
    
    This class wraps a base ImplicitCurve and applies a mask function to determine
    which portions of the curve are included in the segment. The key method is
    contains(), which checks both that a point lies on the base curve and that
    it satisfies the mask condition.
    
    Attributes:
        base_curve (ImplicitCurve): The underlying curve being trimmed
        mask (Callable): Function that takes (x, y) and returns bool for inclusion
    """
    
    def __init__(self, base_curve: ImplicitCurve, mask: Callable[[float, float], bool], 
                 variables: Tuple[sp.Symbol, sp.Symbol] = None,
                 xmin: float = None, xmax: float = None, ymin: float = None, ymax: float = None,
                 endpoints: List[Tuple[float, float]] = None):
        """
        Initialize TrimmedImplicitCurve with base curve and mask function.
        
        Args:
            base_curve: ImplicitCurve to be trimmed
            mask: Callable that takes (x, y) and returns True if point should be included
            variables: Tuple of (x, y) symbols, defaults to base_curve.variables
            xmin, xmax, ymin, ymax: Optional explicit bounding box
            endpoints: Optional list of (x, y) tuples representing the curve segment endpoints
            
        Raises:
            TypeError: If base_curve is not ImplicitCurve or mask is not callable
        """
        # Validate input parameters
        if not isinstance(base_curve, ImplicitCurve):
            raise TypeError("base_curve must be ImplicitCurve instance")
        if not callable(mask):
            raise TypeError("mask must be callable")
        
        # Store base curve and mask
        self.base_curve = base_curve
        self.mask = mask
        self._xmin = xmin
        self._xmax = xmax
        self._ymin = ymin
        self._ymax = ymax
        
        # Store explicit endpoints if provided
        self.endpoints = endpoints if endpoints is not None else []
        
        
        # Use variables from base curve if not specified
        if variables is None:
            variables = base_curve.variables
        
        # Initialize parent class with base curve's expression
        # Note: The expression is inherited but trimming affects contains(), not evaluate()
        # Handle cases where base_curve.expression is None (e.g., ProceduralCurve)
        if base_curve.expression is not None:
            super().__init__(base_curve.expression, variables)
        else:
            # Create a placeholder expression for curves without symbolic expressions
            x, y = variables
            placeholder_expr = x + y  # Simple placeholder
            super().__init__(placeholder_expr, variables)
            # Override the expression to match the base curve
            self.expression = base_curve.expression
    
    def contains(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-3) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are contained in the trimmed curve segment.
        
        A point is contained if:
        1. It lies on the base curve boundary (abs(base_curve.evaluate(x, y)) <= tolerance)
        2. It satisfies the mask condition (mask(x, y) == True)
        
        Note: For trimmed curve segments (like line segments), we check if points
        are ON the curve boundary, not inside a region.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for curve membership test
            
        Returns:
            Boolean or array of booleans indicating containment
        """
        # Check if points are on the base curve boundary (f(x,y) ≈ 0)
        curve_values = self.base_curve.evaluate(x, y)
        on_curve = np.abs(curve_values) <= tolerance
        
        # Check mask condition
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case
            mask_satisfied = self.mask(x, y)
            return bool(on_curve and mask_satisfied)
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)

            # Fast-path: rectangular bounds explicitly provided
            if (self._xmin is not None and self._xmax is not None and
                self._ymin is not None and self._ymax is not None):
                eps = 1e-9
                in_rect = (
                    (x_array >= (self._xmin - eps)) & (x_array <= (self._xmax + eps)) &
                    (y_array >= (self._ymin - eps)) & (y_array <= (self._ymax + eps))
                )
                return on_curve & in_rect

            # General fallback: evaluate mask per-point
            mask_results = np.zeros_like(x_array, dtype=bool)
            flat_x = x_array.flatten()
            flat_y = y_array.flatten()
            for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
                mask_results.flat[i] = self.mask(xi, yi)
            mask_results = mask_results.reshape(x_array.shape)
            return on_curve & mask_results
    
    def on_curve(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-3) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are on the trimmed curve segment.
        
        A point is on the curve if:
        1. It lies on the base curve boundary (abs(base_curve.evaluate(x, y)) <= tolerance)
        2. It satisfies the mask condition (mask(x, y) == True)
        
        This is the same as the contains method for trimmed curves since they represent
        curve segments, not filled regions.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for curve membership test
            
        Returns:
            Boolean or array of booleans indicating if points are on the curve segment
        """
        return self.contains(x, y, tolerance)
    
    def get_endpoints(self) -> List[Tuple[float, float]]:
        """
        Get the endpoints of the trimmed curve segment.
        
        Returns:
            List of (x, y) tuples representing the endpoints of the curve segment.
            Returns empty list if no endpoints were explicitly provided.
        """
        return self.endpoints.copy() if self.endpoints else []
    
    def evaluate(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Evaluate the trimmed curve at given point(s).
        
        Note: This returns the same values as the base curve. Trimming affects
        contains() method, not the implicit function values.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            
        Returns:
            Function value(s) at the given point(s)
        """
        return self.base_curve.evaluate(x, y)
    
    def gradient(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """
        Compute gradient of the trimmed curve.
        
        Note: This returns the same gradients as the base curve. Trimming affects
        contains() method, not the gradient computation.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            
        Returns:
            Tuple of (grad_x, grad_y) components
        """
        return self.base_curve.gradient(x, y)
    
    def plot(self, x_range: Tuple[float, float] = (-2, 2), 
             y_range: Tuple[float, float] = (-2, 2), 
             resolution: int = 1000, ax=None, **kwargs):
        """
        Plot the trimmed curve segment.
        
        This method plots only the portion of the base curve that satisfies
        the mask condition, creating a visualization of the trimmed segment.
        
        Args:
            x_range: Range of x values for plotting
            y_range: Range of y values for plotting  
            resolution: Number of points along each axis
            ax: Matplotlib axes object (optional)
            **kwargs: Additional arguments passed to contour plotting
            
        Returns:
            Matplotlib contour set object
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        # Create coordinate grids
        x_vals = np.linspace(x_range[0], x_range[1], resolution)
        y_vals = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        # Evaluate base curve
        Z = self.base_curve.evaluate(X, Y)
        
        # Apply mask to hide regions outside the trimmed segment
        # ALWAYS apply the mask - don't try to optimize by skipping it
        mask_grid = np.zeros_like(X, dtype=bool)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                mask_grid[i, j] = self.mask(X[i, j], Y[i, j])
        
        # Set masked regions to NaN so they don't appear in contour
        Z_masked = np.where(mask_grid, Z, np.nan)
        
        # Plot the trimmed curve
        default_kwargs = {'levels': [0], 'colors': 'blue', 'linewidths': 2}
        default_kwargs.update(kwargs)
        
        cs = ax.contour(X, Y, Z_masked, **default_kwargs)
        
        # DEBUG: Extract and print the discretized line segments
        print(f"    Contour discretization results:")
        print(f"    Contour set type: {type(cs)}")
        
        # Handle different matplotlib versions
        try:
            if hasattr(cs, 'collections'):
                collections = cs.collections
            elif hasattr(cs, 'allsegs'):
                # Older matplotlib versions
                print(f"    Using allsegs (older matplotlib)")
                collections = []
                for level_segs in cs.allsegs:
                    for seg in level_segs:
                        print(f"    Segment with {len(seg)} points")
                        if len(seg) > 0:
                            print(f"      First point: ({seg[0][0]:.3f}, {seg[0][1]:.3f})")
                            print(f"      Last point:  ({seg[-1][0]:.3f}, {seg[-1][1]:.3f})")
            else:
                print(f"    Unknown contour set format")
        except Exception as e:
            print(f"    Error extracting contour info: {e}")
        
        return cs
