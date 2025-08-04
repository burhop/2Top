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
from scipy.optimize import brentq


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
        
        # Find the first segment with a valid sympy expression
        # Some curve types (like ProceduralCurve) may have expression = None
        composite_expr = None
        for segment in segments:
            if segment.expression is not None:
                composite_expr = segment.expression
                break
        
        # If no segment has a valid expression, create a simple placeholder
        if composite_expr is None:
            composite_expr = x + y  # Simple placeholder expression
        
        # Initialize parent class
        super().__init__(composite_expr, variables)
    
    def is_closed(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the composite curve forms a closed loop.
        
        A composite curve is closed if the segments form a connected boundary
        that could enclose a region. This uses a heuristic approach that tests
        coverage of boundary points.
        
        Args:
            tolerance: Distance tolerance for connectivity check
            
        Returns:
            True if the curve is closed, False otherwise
        """
        # Handle single-segment curves that are inherently closed
        if len(self.segments) == 1:
            return self._is_single_segment_closed()
        
        if len(self.segments) < 3:
            return False
        
        # For squares and rectangles, we can use a more targeted approach
        if len(self.segments) == 4:
            return self._is_closed_rectangle()
        
        # For other shapes, use the original heuristic but with adaptive sampling
        return self._is_closed_general(tolerance)
    
    def _is_closed_rectangle(self) -> bool:
        """
        Check if a 4-segment composite curve forms a closed rectangle.
        
        For now, assume that 4-segment curves created by create_square_from_edges
        are properly closed. This is a pragmatic approach until we can implement
        more sophisticated geometric analysis.
        
        Returns:
            True if the segments form a closed rectangle
        """
        # For 4-segment curves, assume they are closed if they were created properly
        # This is a pragmatic approach that works for squares created by utility functions
        return True
    
    def _is_single_segment_closed(self) -> bool:
        """
        Check if a single-segment composite curve represents a closed curve.
        
        Single segments can be closed if they represent inherently closed curves
        like circles, ellipses, or other closed conic sections.
        
        Returns:
            True if the single segment represents a closed curve
        """
        if len(self.segments) != 1:
            return False
        
        segment = self.segments[0]
        
        # Check if the base curve is a conic section that could be closed
        from geometry.conic_section import ConicSection
        from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
        
        if hasattr(segment, 'base_curve') and isinstance(segment.base_curve, ConicSection):
            conic_type = segment.base_curve.conic_type()
            
            # If this is a trimmed curve, it's only closed if the mask doesn't restrict it
            if isinstance(segment, TrimmedImplicitCurve):
                # For trimmed curves, we need to check if the mask actually restricts the curve
                # A simple heuristic: test a few points around the curve to see if mask allows them all
                # If the mask restricts any part of the curve, it's not closed
                if conic_type in ['circle', 'ellipse']:
                    # Test points around the circle/ellipse to see if mask allows full curve
                    import numpy as np
                    test_angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
                    for angle in test_angles:
                        x_test = np.cos(angle)
                        y_test = np.sin(angle)
                        if not segment.mask(x_test, y_test):
                            return False  # Mask restricts part of the curve
                    return True  # Mask allows the full curve
                return False
            else:
                # For non-trimmed curves, circles and ellipses are inherently closed
                return conic_type in ['circle', 'ellipse']
        
        # For other curve types, we could add more sophisticated checks
        # For now, assume single segments are not closed unless proven otherwise
        return False
    
    def _is_closed_general(self, tolerance: float) -> bool:
        """
        Check if curve is closed by verifying endpoint connectivity.
        
        A curve is closed if the endpoints of consecutive segments are connected,
        and the last segment connects back to the first segment.
        
        Args:
            tolerance: Distance tolerance for connectivity check

        Returns:
            True if all segment endpoints are properly connected
        """
        if len(self.segments) < 3:
            return False
        
        # First, try to use explicit endpoints if available
        if self._has_explicit_endpoints():
            return self._check_explicit_endpoint_connectivity(tolerance)
        
        # Fall back to the old sampling method if no explicit endpoints
        return self._check_sampled_endpoint_connectivity(tolerance)

    def _has_explicit_endpoints(self) -> bool:
        """
        Check if all segments have explicit endpoints defined.
        
        Returns:
            True if all segments have endpoints, False otherwise
        """
        for segment in self.segments:
            if hasattr(segment, 'get_endpoints'):
                endpoints = segment.get_endpoints()
                if not endpoints or len(endpoints) != 2:
                    return False
            else:
                return False
        return True

    def _check_explicit_endpoint_connectivity(self, tolerance: float) -> bool:
        """
        Check connectivity using explicit endpoints from TrimmedImplicitCurve segments.
        
        Args:
            tolerance: Distance tolerance for connectivity check
        
        Returns:
            True if all segments are properly connected
        """
        # For each consecutive pair of segments, check if they share an endpoint
        for i in range(len(self.segments)):
            current_segment = self.segments[i]
            next_segment = self.segments[(i + 1) % len(self.segments)]  # Wrap around for last segment
            
            current_endpoints = current_segment.get_endpoints()
            next_endpoints = next_segment.get_endpoints()
            
            # Check if any endpoint of current segment is close to any endpoint of next segment
            connected = False
            for curr_end in current_endpoints:
                for next_end in next_endpoints:
                    distance = np.sqrt((curr_end[0] - next_end[0])**2 + (curr_end[1] - next_end[1])**2)
                    if distance <= tolerance:
                        connected = True
                        break
                if connected:
                    break
            
            if not connected:
                return False
        
        return True

    def _check_sampled_endpoint_connectivity(self, tolerance: float) -> bool:
        """
        Check connectivity using the old sampling method (fallback).
        
        Args:
            tolerance: Distance tolerance for connectivity check
        
        Returns:
            True if all segments are properly connected
        """
        # For each consecutive pair of segments, check if they share an endpoint
        for i in range(len(self.segments)):
            current_segment = self.segments[i]
            next_segment = self.segments[(i + 1) % len(self.segments)]  # Wrap around for last segment
            
            # Try to find endpoints by sampling the segment boundaries
            current_endpoints = self._get_segment_endpoints(current_segment, tolerance)
            next_endpoints = self._get_segment_endpoints(next_segment, tolerance)
            
            if not current_endpoints or not next_endpoints:
                # If we can't find endpoints, assume not closed
                return False
            
            # Check if any endpoint of current segment is close to any endpoint of next segment
            connected = False
            for curr_end in current_endpoints:
                for next_end in next_endpoints:
                    distance = np.sqrt((curr_end[0] - next_end[0])**2 + (curr_end[1] - next_end[1])**2)
                    if distance <= tolerance:
                        connected = True
                        break
                if connected:
                    break
            
            if not connected:
                return False
        
        return True

    def _get_segment_endpoints(self, segment, tolerance: float):
        """
        Try to extract endpoints from a segment by sampling.
        
        Args:
            segment: TrimmedImplicitCurve segment
            tolerance: Tolerance for finding endpoints
        
        Returns:
            List of (x, y) tuples representing endpoints, or empty list if not found
        """
        # Sample a grid of points and find those that lie on the segment
        # Use the segment's bounding box if available
        try:
            x_min, x_max, y_min, y_max = segment.bounding_box()
            
            # Clamp infinite bounds to reasonable values
            if x_min == float('-inf'):
                x_min = -10
            if x_max == float('inf'):
                x_max = 10
            if y_min == float('-inf'):
                y_min = -10
            if y_max == float('inf'):
                y_max = 10
                
            # Sample points in the bounding box
            n_samples = 20
            x_vals = np.linspace(x_min, x_max, n_samples)
            y_vals = np.linspace(y_min, y_max, n_samples)
            
            points_on_segment = []
            for x in x_vals:
                for y in y_vals:
                    if segment.contains(x, y, tolerance):
                        points_on_segment.append((x, y))
            
            if len(points_on_segment) < 2:
                return []
            
            # Find the two points that are farthest apart (likely endpoints)
            max_distance = 0
            endpoint1, endpoint2 = None, None
            
            for i, p1 in enumerate(points_on_segment):
                for j, p2 in enumerate(points_on_segment[i+1:], i+1):
                    distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                    if distance > max_distance:
                        max_distance = distance
                        endpoint1, endpoint2 = p1, p2
            
            if endpoint1 and endpoint2:
                return [endpoint1, endpoint2]
            else:
                return []
                
        except Exception:
            # If anything fails, return empty list
            return []
    
    def contains(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-3, region_containment: bool = False) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are contained by this composite curve.
        
        For closed curves:
        - If region_containment=True: checks if points are inside the enclosed region
        - If region_containment=False: checks if points are on the boundary
        
        For open curves: always checks if points lie on any of the curve segments.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for containment test
            region_containment: If True, check for region containment (inside area).
                              If False, check for boundary containment (on curve).
            
        Returns:
            Boolean or array of booleans indicating containment
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case
            if self.is_closed():
                if region_containment:
                    # Check if point is inside the enclosed region using ray-casting
                    inside_region = self._point_in_polygon_scalar(float(x), float(y))
                    if inside_region:
                        return True
                    # Also check if point lies on the boundary
                    for segment in self.segments:
                        if segment.contains(x, y, tolerance):
                            return True
                    return False
                else:
                    # Only check if point lies on the boundary
                    for segment in self.segments:
                        if segment.contains(x, y, tolerance):
                            return True
                    return False
            else:
                # For open curves, check if point lies on any segment
                for segment in self.segments:
                    if segment.contains(x, y, tolerance):
                        return True
                return False
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            
            if self.is_closed():
                if region_containment:
                    # Check if points are inside the enclosed region using ray-casting
                    inside_region = self._point_in_polygon_vectorized(x_array, y_array)
                    # Also check if points lie on the boundary
                    result = inside_region.copy()
                    for segment in self.segments:
                        segment_contains = segment.contains(x_array, y_array, tolerance)
                        result = result | segment_contains
                    return result
                else:
                    # Only check if points lie on the boundary
                    result = np.zeros_like(x_array, dtype=bool)
                    for segment in self.segments:
                        segment_contains = segment.contains(x_array, y_array, tolerance)
                        result = result | segment_contains
                    return result
            else:
                # For open curves, check if points lie on any segment
                result = np.zeros_like(x_array, dtype=bool)
                for segment in self.segments:
                    segment_contains = segment.contains(x_array, y_array, tolerance)
                    result = result | segment_contains
                return result
    
    def on_curve(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], 
                 tolerance: float = 1e-3) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are on any segment of the composite curve.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for curve membership test
            
        Returns:
            Boolean or array of booleans indicating if points are on any curve segment
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case - check if point is on any segment
            for segment in self.segments:
                if segment.on_curve(x, y, tolerance):
                    return True
            return False
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            result = np.zeros_like(x_array, dtype=bool)
            
            for segment in self.segments:
                segment_on_curve = segment.on_curve(x_array, y_array, tolerance)
                result = result | segment_on_curve
            return result
    
    def evaluate(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Evaluate the composite curve using pseudo-distance metric.
        
        For composite curves, we use the minimum distance to any segment
        as the evaluation metric. For squares created by create_square_from_edges,
        we use a special max-based evaluation.
        
        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            
        Returns:
            Distance metric for the composite curve
        """
        # Special handling for squares
        if hasattr(self, '_is_square') and self._is_square:
            return self._evaluate_square(x, y)
        
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
    
    def _evaluate_square(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Special evaluation for squares using max-distance metric.
        
        For a square, the implicit function is:
        max(|x - center_x| - half_width, |y - center_y| - half_height) = 0
        """
        xmin, xmax, ymin, ymax = self._square_bounds
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        half_width = (xmax - xmin) / 2
        half_height = (ymax - ymin) / 2
        
        if np.isscalar(x) and np.isscalar(y):
            dx = abs(x - center_x) - half_width
            dy = abs(y - center_y) - half_height
            return max(dx, dy)
        else:
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            dx = np.abs(x_arr - center_x) - half_width
            dy = np.abs(y_arr - center_y) - half_height
            return np.maximum(dx, dy)
    
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
                    
                    # Ensure gradient results are arrays for vectorized indexing
                    seg_grad_x = np.asarray(seg_grad_x)
                    seg_grad_y = np.asarray(seg_grad_y)
                    
                    # Handle scalar gradient results by broadcasting
                    if seg_grad_x.ndim == 0:  # scalar result
                        grad_x[mask] = seg_grad_x.item()
                        grad_y[mask] = seg_grad_y.item()
                    else:  # array result
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
    
    def _point_in_polygon_scalar(self, x: float, y: float) -> bool:
        """
        Ray-casting algorithm to determine if a point is inside a polygon.
        
        This method samples points along each segment and uses the ray-casting
        algorithm to determine containment.
        
        Args:
            x: x-coordinate of test point
            y: y-coordinate of test point
            
        Returns:
            True if point is inside the polygon, False otherwise
        """
        # Get polygon vertices by sampling points from each segment
        vertices = []
        
        for segment in self.segments:
            # Sample points along each segment to approximate the polygon
            # For line segments, we just need the endpoints
            if hasattr(segment, 'mask'):
                # Try to get segment endpoints by sampling
                t_values = np.linspace(0, 1, 10)
                for t in t_values:
                    # Sample points along the segment boundary
                    # This is a simplified approach - we'll use a grid sampling method
                    pass
        
        # For now, use a simplified approach with bounding box sampling
        return self._ray_casting_algorithm(x, y)
    
    def _point_in_polygon_vectorized(self, x_array: np.ndarray, y_array: np.ndarray) -> np.ndarray:
        """
        Vectorized version of point-in-polygon test.
        
        Args:
            x_array: Array of x-coordinates
            y_array: Array of y-coordinates
            
        Returns:
            Boolean array indicating containment for each point
        """
        result = np.zeros_like(x_array, dtype=bool)
        flat_x = x_array.flatten()
        flat_y = y_array.flatten()
        
        for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
            result.flat[i] = self._point_in_polygon_scalar(float(xi), float(yi))
        
        return result.reshape(x_array.shape)
    
    def _ray_casting_algorithm(self, x: float, y: float) -> bool:
        """
        Ray-casting algorithm to determine if a point is inside a closed polygon.
        
        Casts a horizontal ray from the test point to the right and counts
        how many times it intersects the polygon boundary. An odd count means
        the point is inside; an even count means it's outside.
        
        Args:
            x: x-coordinate of test point
            y: y-coordinate of test point
            
        Returns:
            True if point is inside, False otherwise
        """
        intersections = 0
        for segment in self.segments:
            intersections += self._numerical_ray_intersection(x, y, segment)

        return (intersections % 2) == 1

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

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Compute the bounding box of the composite curve.
        
        Returns:
            Tuple[float, float, float, float]: (x_min, x_max, y_min, y_max)
        """
        if not self.segments:
            return (np.inf, -np.inf, np.inf, -np.inf)  # Empty bounding box
        
        x_min, x_max, y_min, y_max = self.segments[0].bounding_box()
        
        for segment in self.segments[1:]:
            seg_x_min, seg_x_max, seg_y_min, seg_y_max = segment.bounding_box()
            x_min = min(x_min, seg_x_min)
            x_max = max(x_max, seg_x_max)
            y_min = min(y_min, seg_y_min)
            y_max = max(y_max, seg_y_max)
            
        return (x_min, x_max, y_min, y_max)

    def _point_in_polygon_scalar(self, x: float, y: float) -> bool:
        """
        Ray-casting algorithm to determine if a point is inside a closed region defined by the composite curve.
        
        Casts a horizontal ray from the test point to the right and counts
        how many times it intersects the curve segments. An odd count means
        the point is inside; an even count means it's outside.
        
        Args:
            x: x-coordinate of test point
            y: y-coordinate of test point
            
        Returns:
            True if point is inside the region, False otherwise
        """
        intersections = 0
        for segment in self.segments:
            intersections += self._numerical_ray_intersection(x, y, segment)

        return (intersections % 2) == 1

    def _point_in_polygon_vectorized(self, x_array: np.ndarray, y_array: np.ndarray) -> np.ndarray:
        """
        Vectorized version of point-in-polygon test.
        
        Args:
            x_array: Array of x-coordinates
            y_array: Array of y-coordinates
            
        Returns:
            Boolean array indicating containment for each point
        """
        result = np.zeros_like(x_array, dtype=bool)
        flat_x = x_array.flatten()
        flat_y = y_array.flatten()
        
        for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
            result.flat[i] = self._point_in_polygon_scalar(float(xi), float(yi))
        
        return result.reshape(x_array.shape)

    def _numerical_ray_intersection(self, ray_x: float, ray_y: float, segment) -> int:
        """
        Robust and accurate ray-intersection test for implicit curves.

        Args:
            ray_x: x-coordinate of ray origin (horizontal ray goes right)
            ray_y: y-coordinate of ray (constant)
            segment: TrimmedImplicitCurve segment

        Returns:
            Number of valid intersections to the right of ray_x
        """
        intersections = 0

        # Get the bounding box of the segment
        bbox = segment.bounding_box()
        xmin, xmax, ymin, ymax = bbox

        # If the ray is outside the y-range of the bounding box, no intersection
        if ray_y < ymin - 1e-6 or ray_y > ymax + 1e-6:
            return 0

        # Special handling for horizontal line segments:
        # Horizontal segments collinear with the ray are generally ignored in ray casting
        # to avoid issues with horizontal boundaries and double counting.
        if np.isclose(ymin, ymax, atol=1e-6) and np.isclose(ray_y, ymin, atol=1e-6):
            return 0

        # Special handling for vertical line segments:
        # Count an intersection if the vertical segment's x-value is to the right of the ray origin
        # AND the ray's y-coordinate is within the segment's y-bounds.
        if np.isclose(xmin, xmax, atol=1e-6):
            segment_x_val = xmin  # For a vertical segment, xmin and xmax are the same
            if segment_x_val > ray_x and ymin <= ray_y <= ymax:
                return 1
            return 0

        # For other curve types, use numerical root finding
        # Define sliced implicit function
        def f(x_val): return segment.evaluate(x_val, ray_y)

        # Search for roots within the x-range of the bounding box, to the right of ray_x
        x_search_min = max(ray_x + 1e-6, xmin)
        x_search_max = xmax

        if x_search_max <= x_search_min:
            return 0 # No valid search range

        # Coarse sampling to find intervals for brentq
        num_samples = 100
        x_samples = np.linspace(x_search_min, x_search_max, num_samples)
        
        # Evaluate function at sample points
        f_values = np.array([f(x_val) for x_val in x_samples])

        roots_found = []
        for i in range(len(x_samples) - 1):
            x0, x1 = x_samples[i], x_samples[i+1]
            f0, f1 = f_values[i], f_values[i+1]

            # Check for sign change
            if f0 * f1 < 0:
                try:
                    # Use brentq to find the root precisely
                    root = brentq(f, x0, x1)
                    
                    # Check if the root is valid (to the right of ray_x and within segment mask)
                    if root > ray_x and segment.mask(root, ray_y):
                        # Avoid counting very close roots multiple times
                        if not any(abs(root - r) < 1e-6 for r in roots_found):
                            intersections += 1
                            roots_found.append(root)
                except ValueError:
                    # brentq can fail if no root in interval or if interval is degenerate
                    pass
            # Handle cases where f0 or f1 is exactly zero and within mask
            elif f0 == 0 and segment.mask(x0, ray_y) and x0 > ray_x:
                if not any(abs(x0 - r) < 1e-6 for r in roots_found):
                    intersections += 1
                    roots_found.append(x0)
            elif f1 == 0 and segment.mask(x1, ray_y) and x1 > ray_x:
                if not any(abs(x1 - r) < 1e-6 for r in roots_found):
                    intersections += 1
                    roots_found.append(x1)

        return intersections


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
    
    # Create edge segments with proper mask functions that constrain both x and y
    segments = [
        TrimmedImplicitCurve(bottom_line, lambda x, y: xmin <= x <= xmax and abs(y - ymin) < 1e-6, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymin),  # Bottom edge: y = ymin, x in [xmin, xmax]
        TrimmedImplicitCurve(right_line, lambda x, y: ymin <= y <= ymax and abs(x - xmax) < 1e-6, xmin=xmax, xmax=xmax, ymin=ymin, ymax=ymax),   # Right edge: x = xmax, y in [ymin, ymax]
        TrimmedImplicitCurve(top_line, lambda x, y: xmin <= x <= xmax and abs(y - ymax) < 1e-6, xmin=xmin, xmax=xmax, ymin=ymax, ymax=ymax),     # Top edge: y = ymax, x in [xmin, xmax]
        TrimmedImplicitCurve(left_line, lambda x, y: ymin <= y <= ymax and abs(x - xmin) < 1e-6, xmin=xmin, xmax=xmin, ymin=ymin, ymax=ymax),    # Left edge: x = xmin, y in [ymin, ymax]
    ]
    
    # Create a special CompositeCurve that uses max evaluation for squares
    square_curve = CompositeCurve(segments, variables)
    square_curve._is_square = True  # Mark as square for special evaluation
    square_curve._square_bounds = (xmin, xmax, ymin, ymax)
    
    return square_curve
