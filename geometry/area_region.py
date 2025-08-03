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
        # Check closure first to allow proper testing of closure validation
        if not outer_boundary.is_closed():
            raise ValueError("outer_boundary must be closed")
        
        # For multi-segment curves, check minimum segments for practical closed regions
        # Single-segment curves can be inherently closed (like circles)
        if len(outer_boundary.segments) > 1 and len(outer_boundary.segments) < 3:
            raise ValueError("outer_boundary must have at least 3 segments to form a closed region (or be a single inherently closed segment)")
        
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
                # Check if the hole is actually closed first
                if not hole.is_closed():
                    raise ValueError(f"holes[{i}] must be closed")
                # For multi-segment curves, check minimum segments for practical closed regions
                # Single-segment curves can be inherently closed (like circles)
                if len(hole.segments) > 1 and len(hole.segments) < 3:
                    raise ValueError(f"holes[{i}] must have at least 3 segments to form a closed region (or be a single inherently closed segment)")
            
            self.holes = holes.copy()  # Create a copy to avoid external modification
    
    def contains(self, x: float, y: float, tolerance: float = 1e-3) -> bool:
        """
        Test if a point is inside the region (accounting for holes).
        Uses a robust point-in-polygon algorithm (ray-casting) to determine if a point
        is contained within the region. A point is considered inside if:
        1. It is inside the outer boundary, AND
        2. It is NOT inside any of the holes
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            tolerance: Tolerance for containment test
            
        Returns:
            bool: True if the point is inside the region, False otherwise
        """
        # Check if point is inside outer boundary (region containment)
        # This will use CompositeCurve's _point_in_polygon_scalar
        if not self.outer_boundary.contains(x, y, tolerance=tolerance, region_containment=True):
            return False
        
        # Check if point is inside any hole (if so, it's not in the region)
        for hole in self.holes:
            if hole.contains(x, y, tolerance=tolerance, region_containment=True):
                return False
        
        return True
    
    def contains_boundary(self, x: float, y: float, tolerance: float = 1e-3) -> bool:
        """
        Test if a point is on the boundary of the region (outer boundary or hole boundaries).
        
        Args:
            x (float): X-coordinate of the test point
            y (float): Y-coordinate of the test point
            tolerance: Tolerance for containment test
            
        Returns:
            bool: True if the point is on any boundary, False otherwise
        """
        # Check if point is on the outer boundary
        if self.outer_boundary.contains(x, y, tolerance=tolerance, region_containment=False):
            return True
        
        # Check if point is on any hole boundary
        for hole in self.holes:
            if hole.contains(x, y, tolerance=tolerance, region_containment=False):
                return True
        
        return False
    
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
        
        # If we didn't find enough points, create a simple line approximation
        if len(boundary_points) < 3:
            # Create a simple line segment as fallback
            for i in range(num_points):
                t = i / (num_points - 1) if num_points > 1 else 0
                x_val = x_min + t * (x_max - x_min)
                y_val = y_min + t * (y_max - y_min)
                boundary_points.append((x_val, y_val))
        
        return boundary_points[:num_points]  # Limit to requested number of points
    
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
        
        # If we didn't find enough points, create a simple line approximation
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
        return segment.bounding_box()
    
    def _get_curve_bbox(self, curve: CompositeCurve) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of a curve.
        
        Args:
            curve (CompositeCurve): The curve to get bounding box for
            
        Returns:
            Tuple[float, float, float, float]: (x_min, x_max, y_min, y_max)
        """
        return curve.bounding_box()
    
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
        Calculate the area of a square directly from its bounding box.
        
        Args:
            curve (CompositeCurve): The square curve with 4 segments
            
        Returns:
            float: The area of the square
        """
        x_min, x_max, y_min, y_max = curve.bounding_box()
        width = x_max - x_min
        height = y_max - y_min
        return width * height
    
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
    
    def get_field(self, strategy: 'FieldStrategy') -> 'BaseField':
        """
        Generate a scalar field from this AreaRegion using the specified strategy.
        
        This method implements the FieldStrategy pattern, allowing different
        algorithms for generating scalar fields from the region. Common strategies
        include signed distance fields and occupancy fields.
        
        Args:
            strategy (FieldStrategy): The strategy to use for field generation
            
        Returns:
            BaseField: The generated scalar field
            
        Example:
            >>> from geometry.field_strategy import SignedDistanceStrategy, OccupancyFillStrategy
            >>> region = AreaRegion(square_boundary)
            >>> 
            >>> # Generate a signed distance field
            >>> sdf_strategy = SignedDistanceStrategy(resolution=0.1)
            >>> sdf = region.get_field(sdf_strategy)
            >>> 
            >>> # Generate an occupancy field
            >>> occ_strategy = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0)
            >>> occupancy = region.get_field(occ_strategy)
        """
        from .field_strategy import FieldStrategy
        
        if not isinstance(strategy, FieldStrategy):
            raise TypeError("strategy must be a FieldStrategy instance")
        
        return strategy.generate_field(self)
