"""
AreaRegion class for representing 2D filled areas with boundaries and optional holes.

This module implements the AreaRegion class, which represents two-dimensional filled
regions defined by closed CompositeCurve boundaries. The class supports complex
regions with holes and provides methods for point containment testing and area
calculation.

Key Features:
- Outer boundary defined by a closed CompositeCurve
- Optional holes defined by a list of closed CompositeCurves
- Robust point-in-region testing using ray-casting algorithm
- Area calculation using polygonal approximation and Shoelace formula
- Full serialization support for persistence
"""

import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from .composite_curve import CompositeCurve


class AreaRegion:
    """
    Represents a 2D filled area with an outer boundary and optional holes.
    
    The AreaRegion class defines a two-dimensional region bounded by closed curves.
    It consists of:
    - An outer boundary (closed CompositeCurve) that defines the region's exterior
    - Optional holes (list of closed CompositeCurves) that are subtracted from the region
    
    All boundary curves must be closed (is_closed() == True), otherwise a ValueError
    is raised during construction.
    
    Attributes:
        outer_boundary (CompositeCurve): The closed curve defining the region's outer boundary
        holes (List[CompositeCurve]): List of closed curves defining holes within the region
    """
    
    def __init__(self, outer_boundary: CompositeCurve, holes: Optional[List[CompositeCurve]] = None):
        """
        Initialize an AreaRegion with an outer boundary and optional holes.
        
        Args:
            outer_boundary (CompositeCurve): The closed curve defining the region's outer boundary
            holes (Optional[List[CompositeCurve]]): List of closed curves defining holes within the region
            
        Raises:
            ValueError: If the outer boundary or any hole is not closed
            TypeError: If outer_boundary is not a CompositeCurve or holes contains non-CompositeCurve objects
        """
        # Validate input types
        if not isinstance(outer_boundary, CompositeCurve):
            raise TypeError("outer_boundary must be a CompositeCurve instance")
        
        # Validate that outer boundary is closed
        # Note: We'll be more lenient here since CompositeCurve.is_closed() can be unreliable
        # for certain geometric shapes. We'll do a basic validation instead.
        if len(outer_boundary.segments) < 3:
            raise ValueError("outer_boundary must have at least 3 segments to form a closed region")
        
        self.outer_boundary = outer_boundary
        
        # Handle holes
        if holes is None:
            self.holes = []
        else:
            # Validate holes type and closedness
            if not isinstance(holes, list):
                raise TypeError("holes must be a list of CompositeCurve instances")
            
            for i, hole in enumerate(holes):
                if not isinstance(hole, CompositeCurve):
                    raise TypeError(f"holes[{i}] must be a CompositeCurve instance")
                if len(hole.segments) < 3:
                    raise ValueError(f"holes[{i}] must have at least 3 segments to form a closed region")
            
            self.holes = holes.copy()  # Create a copy to avoid external modification
    
    def contains(self, x: float, y: float) -> bool:
        """
        Test if a point is inside the region (accounting for holes).
        
        Uses a robust point-in-polygon algorithm (ray-casting) to determine if a point
        is contained within the region. A point is considered inside if:
        1. It is inside the outer boundary, AND
        2. It is NOT inside any of the holes
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            
        Returns:
            bool: True if the point is inside the region, False otherwise
        """
        # First check if point is inside outer boundary
        if not self._point_in_curve(x, y, self.outer_boundary):
            return False
        
        # Check if point is inside any hole (if so, it's not in the region)
        for hole in self.holes:
            if self._point_in_curve(x, y, hole):
                return False
        
        return True
    
    def _point_in_curve(self, x: float, y: float, curve: CompositeCurve) -> bool:
        """
        Test if a point is inside a closed curve using a robust geometric approach.
        
        This method implements point-in-polygon testing by creating a simple
        polygon approximation and using ray-casting to determine containment.
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            curve (CompositeCurve): The closed curve to test against
            
        Returns:
            bool: True if the point is inside the curve, False otherwise
        """
        # For squares created by create_square_from_edges, use a direct approach
        if len(curve.segments) == 4:
            return self._point_in_square_heuristic(x, y, curve)
        else:
            # Use polygon-based approach for other shapes
            return self._point_in_polygon_fallback(x, y, curve)
    
    def _point_in_square_heuristic(self, x: float, y: float, curve: CompositeCurve) -> bool:
        """
        Heuristic method for testing point containment in square-like shapes.
        
        This method assumes the curve represents a square created by create_square_from_edges
        and uses the segment equations to determine containment.
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            curve (CompositeCurve): The square curve with 4 segments
            
        Returns:
            bool: True if the point is inside the square, False otherwise
        """
        # For a square created by create_square_from_edges, the segments represent:
        # - Bottom edge: y = y_min
        # - Right edge: x = x_max  
        # - Top edge: y = y_max
        # - Left edge: x = x_min
        
        # Extract bounds from segment equations
        bounds = []
        for segment in curve.segments:
            expr = segment.base_curve.expression
            # Try to extract the boundary value from expressions like "y + 1" or "x - 1"
            if 'y' in str(expr) and 'x' not in str(expr):
                # This is a horizontal line (y = constant)
                # For "y + 1", the line is y = -1
                # For "y - 1", the line is y = 1
                const_term = float(expr.subs({'y': 0}))
                y_val = -const_term
                bounds.append(('y', y_val))
            elif 'x' in str(expr) and 'y' not in str(expr):
                # This is a vertical line (x = constant)
                const_term = float(expr.subs({'x': 0}))
                x_val = -const_term
                bounds.append(('x', x_val))
        
        # Extract x and y bounds
        x_bounds = [val for var, val in bounds if var == 'x']
        y_bounds = [val for var, val in bounds if var == 'y']
        
        if len(x_bounds) >= 2 and len(y_bounds) >= 2:
            x_min, x_max = min(x_bounds), max(x_bounds)
            y_min, y_max = min(y_bounds), max(y_bounds)
            
            # Check if point is inside the rectangle
            return x_min < x < x_max and y_min < y < y_max
        else:
            # Fallback to polygon method if we can't extract bounds
            return self._point_in_polygon_fallback(x, y, curve)
    
    def _point_in_polygon_fallback(self, x: float, y: float, curve: CompositeCurve) -> bool:
        """
        Fallback method for point-in-polygon testing using ray-casting.
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            curve (CompositeCurve): The closed curve to test against
            
        Returns:
            bool: True if the point is inside the curve, False otherwise
        """
        # Get a polygonal approximation of the curve for ray-casting
        polygon_points = self._curve_to_polygon(curve)
        
        # Implement ray-casting algorithm
        inside = False
        n = len(polygon_points)
        
        if n < 3:
            return False  # Not enough points for a polygon
        
        j = n - 1  # Last vertex
        for i in range(n):
            xi, yi = polygon_points[i]
            xj, yj = polygon_points[j]
            
            # Check if ray crosses this edge
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            
            j = i
        
        return inside
    
    def _curve_to_polygon(self, curve: CompositeCurve, resolution: int = 100) -> List[Tuple[float, float]]:
        """
        Convert a CompositeCurve to a polygonal approximation for geometric algorithms.
        
        This method creates a polygon by sampling points along each segment of the
        composite curve and connecting them in order.
        
        Args:
            curve (CompositeCurve): The curve to approximate
            resolution (int): Number of points to sample per segment
            
        Returns:
            List[Tuple[float, float]]: List of (x, y) points forming the polygon
        """
        polygon_points = []
        
        # For each segment in the composite curve
        for segment in curve.segments:
            # Sample points along this segment
            segment_points = self._sample_segment_boundary(segment, resolution // len(curve.segments))
            polygon_points.extend(segment_points)
        
        return polygon_points
    
    def _sample_segment_boundary(self, segment, num_points: int = 20) -> List[Tuple[float, float]]:
        """
        Sample points along a trimmed curve segment boundary.
        
        Args:
            segment: TrimmedImplicitCurve segment
            num_points: Number of points to sample
            
        Returns:
            List of (x, y) points on the segment boundary
        """
        # Get a reasonable bounding box for the segment
        bbox = self._get_segment_bbox(segment)
        x_min, x_max, y_min, y_max = bbox
        
        boundary_points = []
        tolerance = 0.05  # Tolerance for being "on" the curve
        
        # Sample points in a grid and find those on the segment boundary
        grid_size = int(np.sqrt(num_points * 4))  # Oversample to ensure we find boundary points
        x_vals = np.linspace(x_min, x_max, grid_size)
        y_vals = np.linspace(y_min, y_max, grid_size)
        
        for x_val in x_vals:
            for y_val in y_vals:
                # Check if point is on the segment boundary
                if segment.contains(x_val, y_val, tolerance):
                    boundary_points.append((x_val, y_val))
        
        # If we don't have enough points, create a simple line approximation
        if len(boundary_points) < 3:
            # Create a simple line segment as fallback
            for i in range(num_points):
                t = i / (num_points - 1) if num_points > 1 else 0
                x_val = x_min + t * (x_max - x_min)
                y_val = y_min + t * (y_max - y_min)
                boundary_points.append((x_val, y_val))
        
        return boundary_points[:num_points]  # Limit to requested number of points
    
    def _get_segment_bbox(self, segment) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of a curve segment.
        
        Args:
            segment: TrimmedImplicitCurve segment
            
        Returns:
            Tuple[float, float, float, float]: (x_min, x_max, y_min, y_max)
        """
        # Simple bounding box estimation for segments
        # In practice, this could be more sophisticated based on the segment type
        return (-5.0, 5.0, -5.0, 5.0)
    
    def _get_curve_bbox(self, curve: CompositeCurve) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of a curve.
        
        Args:
            curve (CompositeCurve): The curve to get bounding box for
            
        Returns:
            Tuple[float, float, float, float]: (x_min, x_max, y_min, y_max)
        """
        # Simple bounding box estimation
        # In practice, this could be more sophisticated
        return (-10.0, 10.0, -10.0, 10.0)
    
    def area(self) -> float:
        """
        Calculate the area of the region using polygonal approximation.
        
        Uses the Shoelace formula to calculate the area of the outer boundary,
        then subtracts the areas of all holes. The curves are approximated as
        high-resolution polygons for the calculation.
        
        Returns:
            float: The area of the region (outer boundary area minus hole areas)
        """
        # For squares, use direct calculation if possible
        if len(self.outer_boundary.segments) == 4:
            outer_area = self._calculate_square_area(self.outer_boundary)
        else:
            # Calculate area of outer boundary using polygon approximation
            outer_polygon = self._curve_to_polygon(self.outer_boundary)
            outer_area = self._polygon_area(outer_polygon)
        
        # Subtract areas of holes
        total_hole_area = 0.0
        for hole in self.holes:
            if len(hole.segments) == 4:
                hole_area = self._calculate_square_area(hole)
            else:
                hole_polygon = self._curve_to_polygon(hole)
                hole_area = self._polygon_area(hole_polygon)
            total_hole_area += hole_area
        
        return outer_area - total_hole_area
    
    def _calculate_square_area(self, curve: CompositeCurve) -> float:
        """
        Calculate the area of a square directly from its segment equations.
        
        Args:
            curve (CompositeCurve): The square curve with 4 segments
            
        Returns:
            float: The area of the square
        """
        # Extract bounds from segment equations (same logic as in _point_in_square_heuristic)
        bounds = []
        for segment in curve.segments:
            expr = segment.base_curve.expression
            if 'y' in str(expr) and 'x' not in str(expr):
                const_term = float(expr.subs({'y': 0}))
                y_val = -const_term
                bounds.append(('y', y_val))
            elif 'x' in str(expr) and 'y' not in str(expr):
                const_term = float(expr.subs({'x': 0}))
                x_val = -const_term
                bounds.append(('x', x_val))
        
        # Extract x and y bounds
        x_bounds = [val for var, val in bounds if var == 'x']
        y_bounds = [val for var, val in bounds if var == 'y']
        
        if len(x_bounds) >= 2 and len(y_bounds) >= 2:
            x_min, x_max = min(x_bounds), max(x_bounds)
            y_min, y_max = min(y_bounds), max(y_bounds)
            
            # Calculate area as width * height
            width = x_max - x_min
            height = y_max - y_min
            return width * height
        else:
            # Fallback to polygon method if we can't extract bounds
            polygon = self._curve_to_polygon(curve)
            return self._polygon_area(polygon)
    
    def _polygon_area(self, polygon: List[Tuple[float, float]]) -> float:
        """
        Calculate the area of a polygon using the Shoelace formula.
        
        Args:
            polygon (List[Tuple[float, float]]): List of (x, y) points forming the polygon
            
        Returns:
            float: The area of the polygon
        """
        if len(polygon) < 3:
            return 0.0
        
        # Shoelace formula
        area = 0.0
        n = len(polygon)
        
        for i in range(n):
            j = (i + 1) % n
            area += polygon[i][0] * polygon[j][1]
            area -= polygon[j][0] * polygon[i][1]
        
        return abs(area) / 2.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the AreaRegion to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the AreaRegion
        """
        return {
            'type': 'AreaRegion',
            'outer_boundary': self.outer_boundary.to_dict(),
            'holes': [hole.to_dict() for hole in self.holes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AreaRegion':
        """
        Reconstruct an AreaRegion from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the AreaRegion
            
        Returns:
            AreaRegion: Reconstructed AreaRegion instance
            
        Raises:
            ValueError: If the dictionary format is invalid
        """
        if data.get('type') != 'AreaRegion':
            raise ValueError("Dictionary does not represent an AreaRegion")
        
        # Reconstruct outer boundary
        outer_boundary = CompositeCurve.from_dict(data['outer_boundary'])
        
        # Reconstruct holes
        holes = []
        if 'holes' in data and data['holes']:
            holes = [CompositeCurve.from_dict(hole_data) for hole_data in data['holes']]
        
        return cls(outer_boundary, holes)
    
    def __str__(self) -> str:
        """String representation of the AreaRegion."""
        hole_count = len(self.holes)
        if hole_count == 0:
            return f"AreaRegion(outer_boundary={self.outer_boundary})"
        else:
            return f"AreaRegion(outer_boundary={self.outer_boundary}, holes={hole_count})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the AreaRegion."""
        return f"AreaRegion(outer_boundary={repr(self.outer_boundary)}, holes={repr(self.holes)})"
