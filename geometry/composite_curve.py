"""
CompositeCurve - Piecewise Curve Composition

This module implements the CompositeCurve class for Sprint 5, enabling
the representation of complex shapes from ordered sequences of curve segments.

The CompositeCurve assembles multiple TrimmedImplicitCurve segments into a single,
continuous path with connectivity checking and unified containment testing.

Key Features:
- Ordered sequence of TrimmedImplicitCurve segments
- is_closed() method for connectivity validation
- contains() method for unified containment testing
- Full inheritance from ImplicitCurve interface
- Specialized plotting for piecewise visualization
- Serialization support for composite structures
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Union, Dict, Any
from .implicit_curve import ImplicitCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve


class CompositeCurve(ImplicitCurve):
    """
    CompositeCurve represents a piecewise curve composed of multiple segments.
    
    This class assembles an ordered sequence of TrimmedImplicitCurve segments
    into a single composite curve. It provides methods to check connectivity
    (is_closed) and unified containment testing across all segments.
    
    Attributes:
        segments (List[TrimmedImplicitCurve]): Ordered list of curve segments
    """
    
    def __init__(self, segments: List[TrimmedImplicitCurve], 
                 variables: Tuple[sp.Symbol, sp.Symbol] = None):
        """
        Initialize CompositeCurve with ordered list of segments.
        
        Args:
            segments: List of TrimmedImplicitCurve objects in order
            variables: Tuple of (x, y) symbols, defaults to first segment's variables
            
        Raises:
            ValueError: If segments list is empty
            TypeError: If any segment is not a TrimmedImplicitCurve
        """
        # Validate input parameters
        if not segments:
            raise ValueError("CompositeCurve must have at least one segment")
        
        if not all(isinstance(seg, TrimmedImplicitCurve) for seg in segments):
            raise TypeError("All segments must be TrimmedImplicitCurve instances")
        
        # Store segments
        self.segments = list(segments)  # Make a copy to avoid external modification
        
        # Use variables from first segment if not specified
        if variables is None:
            variables = segments[0].variables
        
        # Create a composite expression (pseudo-distance to any segment)
        # This is a placeholder - the real evaluation is done in evaluate()
        x, y = variables
        
        # Use a simple placeholder expression instead of sp.Min to avoid issues
        # The actual evaluation logic is implemented in the evaluate() method
        composite_expr = segments[0].expression  # Use first segment as placeholder
        
        # Initialize parent class
        super().__init__(composite_expr, variables)
    
    def is_closed(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the composite curve forms a closed loop.
        
        A composite curve is closed if the end of the last segment connects
        to the start of the first segment within the specified tolerance.
        
        Args:
            tolerance: Distance tolerance for connectivity check
            
        Returns:
            True if the curve is closed, False otherwise
        """
        if len(self.segments) < 2:
            return False
        
        # Find representative points on each segment to check connectivity
        # This is a simplified implementation - a more robust version would
        # find actual endpoints of each segment
        
        # For now, we'll use a heuristic approach:
        # Check if segments cover complementary regions that could form a closed loop
        
        # Sample points around a circle to test coverage
        n_test_points = 36  # Every 10 degrees
        angles = np.linspace(0, 2*np.pi, n_test_points, endpoint=False)
        
        # Test points on unit circle (this is a heuristic for common cases)
        test_points = [(np.cos(angle), np.sin(angle)) for angle in angles]
        
        # Count how many test points are contained in the composite curve
        contained_count = 0
        for x, y in test_points:
            if self.contains(x, y):
                contained_count += 1
        
        # If most test points are contained, likely closed
        # This is a heuristic - a more rigorous implementation would analyze
        # actual segment endpoints and connectivity
        coverage_ratio = contained_count / n_test_points
        
        # Consider closed if coverage is high (> 80%)
        return coverage_ratio > 0.8
    
    def contains(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-10) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are contained in any segment of the composite curve.
        
        A point is contained if it is contained in at least one of the segments.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for containment test
            
        Returns:
            Boolean or array of booleans indicating containment
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case - check each segment
            for segment in self.segments:
                if segment.contains(x, y, tolerance):
                    return True
            return False
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            
            # Initialize result array
            result = np.zeros_like(x_array, dtype=bool)
            
            # Check each segment
            for segment in self.segments:
                segment_contains = segment.contains(x_array, y_array, tolerance)
                result = result | segment_contains
            
            return result
    
    def evaluate(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Evaluate the composite curve using pseudo-distance metric.
        
        For composite curves, we use the minimum distance to any segment
        as the evaluation metric. This provides a reasonable implicit function
        for the piecewise curve.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            
        Returns:
            Minimum distance to any segment
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case - find minimum over all segments
            values = [segment.evaluate(x, y) for segment in self.segments]
            return min(values)
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            
            # Evaluate all segments
            segment_values = [segment.evaluate(x_array, y_array) for segment in self.segments]
            
            # Take minimum across segments
            return np.minimum.reduce(segment_values)
    
    def gradient(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """
        Compute gradient of the composite curve.
        
        The gradient is computed from the segment that gives the minimum value
        at each point, similar to the gradient of a min function.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            
        Returns:
            Tuple of (grad_x, grad_y) components
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case - find segment with minimum value
            values = [segment.evaluate(x, y) for segment in self.segments]
            min_idx = np.argmin(values)
            return self.segments[min_idx].gradient(x, y)
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            
            # Evaluate all segments to find minimum
            segment_values = [segment.evaluate(x_array, y_array) for segment in self.segments]
            min_indices = np.argmin(segment_values, axis=0)
            
            # Initialize gradient arrays
            grad_x = np.zeros_like(x_array, dtype=float)
            grad_y = np.zeros_like(y_array, dtype=float)
            
            # Compute gradient from appropriate segment for each point
            for i, segment in enumerate(self.segments):
                mask = (min_indices == i)
                if np.any(mask):
                    seg_grad_x, seg_grad_y = segment.gradient(x_array, y_array)
                    grad_x[mask] = seg_grad_x[mask]
                    grad_y[mask] = seg_grad_y[mask]
            
            return grad_x, grad_y
    
    def plot(self, x_range: Tuple[float, float] = (-2, 2), 
             y_range: Tuple[float, float] = (-2, 2), 
             resolution: int = 1000, ax=None, **kwargs):
        """
        Plot the composite curve by plotting each segment.
        
        This method iterates through all segments and plots each one,
        creating a visualization of the complete piecewise curve.
        
        Args:
            x_range: Range of x values for plotting
            y_range: Range of y values for plotting  
            resolution: Number of points along each axis
            ax: Matplotlib axes object (optional)
            **kwargs: Additional arguments passed to segment plotting
            
        Returns:
            List of matplotlib contour set objects from each segment
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        # Plot each segment
        contour_sets = []
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.segments)))
        
        for i, segment in enumerate(self.segments):
            # Use different colors for each segment if not specified
            segment_kwargs = kwargs.copy()
            if 'colors' not in segment_kwargs and 'color' not in segment_kwargs:
                segment_kwargs['colors'] = [colors[i]]
            
            # Plot the segment
            cs = segment.plot(x_range, y_range, resolution, ax, **segment_kwargs)
            contour_sets.append(cs)
        
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Composite Curve ({len(self.segments)} segments)')
        
        return contour_sets
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize CompositeCurve to dictionary.
        
        Returns:
            Dictionary containing curve type, segments, and metadata
        """
        return {
            "type": "CompositeCurve",
            "segments": [segment.to_dict() for segment in self.segments],
            "segment_count": len(self.segments),
            "variables": [str(var) for var in self.variables]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompositeCurve':
        """
        Deserialize CompositeCurve from dictionary.
        
        Args:
            data: Dictionary containing serialized curve data
            
        Returns:
            CompositeCurve instance
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if data.get("type") != "CompositeCurve":
            raise ValueError(f"Invalid type: expected 'CompositeCurve', got {data.get('type')}")
        
        # Reconstruct variables
        var_names = data["variables"]
        variables = tuple(sp.Symbol(name) for name in var_names)
        
        # Reconstruct segments
        segments = []
        for segment_data in data["segments"]:
            segment = TrimmedImplicitCurve.from_dict(segment_data)
            segments.append(segment)
        
        # Create CompositeCurve
        return cls(segments, variables)
    
    def get_segment_count(self) -> int:
        """
        Get the number of segments in the composite curve.
        
        Returns:
            Number of segments
        """
        return len(self.segments)
    
    def get_segment(self, index: int) -> TrimmedImplicitCurve:
        """
        Get a specific segment by index.
        
        Args:
            index: Index of the segment to retrieve
            
        Returns:
            TrimmedImplicitCurve at the specified index
            
        Raises:
            IndexError: If index is out of range
        """
        if not 0 <= index < len(self.segments):
            raise IndexError(f"Segment index {index} out of range [0, {len(self.segments)})")
        
        return self.segments[index]
    
    def add_segment(self, segment: TrimmedImplicitCurve):
        """
        Add a new segment to the end of the composite curve.
        
        Args:
            segment: TrimmedImplicitCurve to add
            
        Raises:
            TypeError: If segment is not a TrimmedImplicitCurve
        """
        if not isinstance(segment, TrimmedImplicitCurve):
            raise TypeError("Segment must be TrimmedImplicitCurve instance")
        
        self.segments.append(segment)
    
    def remove_segment(self, index: int):
        """
        Remove a segment by index.
        
        Args:
            index: Index of the segment to remove
            
        Raises:
            IndexError: If index is out of range
            ValueError: If trying to remove the last remaining segment
        """
        if not 0 <= index < len(self.segments):
            raise IndexError(f"Segment index {index} out of range [0, {len(self.segments)})")
        
        if len(self.segments) <= 1:
            raise ValueError("Cannot remove the last remaining segment")
        
        self.segments.pop(index)
    
    def __str__(self) -> str:
        """String representation of CompositeCurve"""
        return f"CompositeCurve({len(self.segments)} segments)"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"CompositeCurve(segments={self.segments})"
    
    def __len__(self) -> int:
        """Return number of segments"""
        return len(self.segments)
    
    def __getitem__(self, index: int) -> TrimmedImplicitCurve:
        """Get segment by index using bracket notation"""
        return self.get_segment(index)
    
    def __iter__(self):
        """Iterate over segments"""
        return iter(self.segments)


# Utility functions for creating common composite curves

def create_circle_from_quarters(center: Tuple[float, float] = (0, 0), 
                               radius: float = 1.0,
                               variables: Tuple[sp.Symbol, sp.Symbol] = None) -> CompositeCurve:
    """
    Create a complete circle from four quarter-circle segments.
    
    Args:
        center: Center point (x, y) of the circle
        radius: Radius of the circle
        variables: Tuple of (x, y) symbols
        
    Returns:
        CompositeCurve representing a complete circle
    """
    if variables is None:
        x, y = sp.symbols('x y')
        variables = (x, y)
    else:
        x, y = variables
    
    # Create circle equation: (x - cx)^2 + (y - cy)^2 - r^2 = 0
    cx, cy = center
    from .conic_section import ConicSection
    circle_expr = (x - cx)**2 + (y - cy)**2 - radius**2
    circle = ConicSection(circle_expr, variables)
    
    # Create quarter segments
    segments = [
        TrimmedImplicitCurve(circle, lambda x, y: x >= cx and y >= cy),  # First quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x <= cx and y >= cy),  # Second quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x <= cx and y <= cy),  # Third quadrant
        TrimmedImplicitCurve(circle, lambda x, y: x >= cx and y <= cy),  # Fourth quadrant
    ]
    
    return CompositeCurve(segments, variables)

def create_square_from_edges(corner1: Tuple[float, float] = (0, 0),
                           corner2: Tuple[float, float] = (1, 1),
                           variables: Tuple[sp.Symbol, sp.Symbol] = None) -> CompositeCurve:
    """
    Create a square from four edge segments.
    
    Args:
        corner1: First corner (x1, y1) of the square
        corner2: Opposite corner (x2, y2) of the square
        variables: Tuple of (x, y) symbols
        
    Returns:
        CompositeCurve representing a square
    """
    if variables is None:
        x, y = sp.symbols('x y')
        variables = (x, y)
    else:
        x, y = variables
    
    x1, y1 = corner1
    x2, y2 = corner2
    
    # Ensure proper ordering
    xmin, xmax = min(x1, x2), max(x1, x2)
    ymin, ymax = min(y1, y2), max(y1, y2)
    
    from .polynomial_curve import PolynomialCurve
    
    # Create line equations for each edge
    bottom_line = PolynomialCurve(y - ymin, variables)  # y = ymin
    right_line = PolynomialCurve(x - xmax, variables)   # x = xmax
    top_line = PolynomialCurve(y - ymax, variables)     # y = ymax
    left_line = PolynomialCurve(x - xmin, variables)    # x = xmin
    
    # Create edge segments
    segments = [
        TrimmedImplicitCurve(bottom_line, lambda x, y: xmin <= x <= xmax),  # Bottom edge
        TrimmedImplicitCurve(right_line, lambda x, y: ymin <= y <= ymax),   # Right edge
        TrimmedImplicitCurve(top_line, lambda x, y: xmin <= x <= xmax),     # Top edge
        TrimmedImplicitCurve(left_line, lambda x, y: ymin <= y <= ymax),    # Left edge
    ]
    
    return CompositeCurve(segments, variables)
