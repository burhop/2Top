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
from typing import Tuple, Union, Dict, Any, Callable
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
                 variables: Tuple[sp.Symbol, sp.Symbol] = None):
        """
        Initialize TrimmedImplicitCurve with base curve and mask function.
        
        Args:
            base_curve: ImplicitCurve to be trimmed
            mask: Callable that takes (x, y) and returns True if point should be included
            variables: Tuple of (x, y) symbols, defaults to base_curve.variables
            
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
        
        # Use variables from base curve if not specified
        if variables is None:
            variables = base_curve.variables
        
        # Initialize parent class with base curve's expression
        # Note: The expression is inherited but trimming affects contains(), not evaluate()
        super().__init__(base_curve.expression, variables)
    
    def contains(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-10) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are contained in the trimmed curve segment.
        
        A point is contained if:
        1. It lies on the base curve (base_curve.evaluate(x, y) ≈ 0)
        2. It satisfies the mask condition (mask(x, y) == True)
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for curve membership test
            
        Returns:
            Boolean or array of booleans indicating containment
        """
        # Check if points are on the base curve
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
            
            # Apply mask to each point
            mask_results = np.zeros_like(x_array, dtype=bool)
            flat_x = x_array.flatten()
            flat_y = y_array.flatten()
            
            for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
                mask_results.flat[i] = self.mask(xi, yi)
            
            # Reshape to match input shape
            mask_results = mask_results.reshape(x_array.shape)
            
            return on_curve & mask_results
    
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
        
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Trimmed Curve: {self}')
        
        return cs
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize TrimmedImplicitCurve to dictionary.
        
        Note: The mask function cannot be serialized directly. This method
        stores a placeholder and documents the limitation.
        
        Returns:
            Dictionary containing curve type, base curve, and mask placeholder
        """
        return {
            "type": "TrimmedImplicitCurve",
            "base_curve": self.base_curve.to_dict(),
            "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
            "mask_description": "Mask function cannot be serialized. Manual reconstruction required.",
            "variables": [str(var) for var in self.variables]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrimmedImplicitCurve':
        """
        Deserialize TrimmedImplicitCurve from dictionary.
        
        Note: Since mask functions cannot be serialized, this method creates
        a placeholder that always returns True, effectively removing the trimming.
        
        Args:
            data: Dictionary containing serialized curve data
            
        Returns:
            TrimmedImplicitCurve instance with placeholder mask
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if data.get("type") != "TrimmedImplicitCurve":
            raise ValueError(f"Invalid type: expected 'TrimmedImplicitCurve', got {data.get('type')}")
        
        # Reconstruct variables
        var_names = data["variables"]
        variables = tuple(sp.Symbol(name) for name in var_names)
        
        # Reconstruct base curve
        base_curve = ImplicitCurve.from_dict(data["base_curve"])
        
        # Create placeholder mask that always returns True
        def placeholder_mask(x, y):
            """Placeholder mask function - always returns True"""
            return True
        
        # Create TrimmedImplicitCurve with placeholder mask
        trimmed_curve = cls(base_curve, placeholder_mask, variables)
        
        # Add warning attribute
        trimmed_curve._deserialization_warning = (
            "Mask function was not serialized. This curve uses a placeholder "
            "mask that always returns True, effectively removing trimming."
        )
        
        return trimmed_curve
    
    def __str__(self) -> str:
        """String representation of TrimmedImplicitCurve"""
        return f"TrimmedImplicitCurve(base={self.base_curve})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"TrimmedImplicitCurve(base_curve={repr(self.base_curve)}, "
                f"mask={self.mask})")


# Utility functions for common mask patterns

def right_half_mask(x: float, y: float) -> bool:
    """Mask for right half (x >= 0)"""
    return x >= 0

def left_half_mask(x: float, y: float) -> bool:
    """Mask for left half (x <= 0)"""
    return x <= 0

def upper_half_mask(x: float, y: float) -> bool:
    """Mask for upper half (y >= 0)"""
    return y >= 0

def lower_half_mask(x: float, y: float) -> bool:
    """Mask for lower half (y <= 0)"""
    return y <= 0

def first_quadrant_mask(x: float, y: float) -> bool:
    """Mask for first quadrant (x >= 0 and y >= 0)"""
    return x >= 0 and y >= 0

def second_quadrant_mask(x: float, y: float) -> bool:
    """Mask for second quadrant (x <= 0 and y >= 0)"""
    return x <= 0 and y >= 0

def third_quadrant_mask(x: float, y: float) -> bool:
    """Mask for third quadrant (x <= 0 and y <= 0)"""
    return x <= 0 and y <= 0

def fourth_quadrant_mask(x: float, y: float) -> bool:
    """Mask for fourth quadrant (x >= 0 and y <= 0)"""
    return x >= 0 and y <= 0

def angular_mask(start_angle: float, end_angle: float):
    """
    Create mask for angular segment.
    
    Args:
        start_angle: Start angle in radians
        end_angle: End angle in radians
        
    Returns:
        Mask function for the angular segment
    """
    def mask(x: float, y: float) -> bool:
        angle = np.arctan2(y, x)
        # Handle angle wrapping
        if start_angle <= end_angle:
            return start_angle <= angle <= end_angle
        else:
            return angle >= start_angle or angle <= end_angle
    return mask

def radial_mask(min_radius: float, max_radius: float):
    """
    Create mask for radial segment.
    
    Args:
        min_radius: Minimum radius (inclusive)
        max_radius: Maximum radius (inclusive)
        
    Returns:
        Mask function for the radial segment
    """
    def mask(x: float, y: float) -> bool:
        radius = np.sqrt(x**2 + y**2)
        return min_radius <= radius <= max_radius
    return mask
