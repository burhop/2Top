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

from __future__ import annotations
import numpy as np
from typing import List, Optional, Dict, Any, Tuple, Union, TYPE_CHECKING
from .composite_curve import CompositeCurve
from .precision import PrecisionPolicy, get_precision_policy

if TYPE_CHECKING:
    from .field_strategy import FieldStrategy
    from .base_field import BaseField


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

    def __init__(
        self,
        outer_boundary: CompositeCurve,
        holes: Optional[List[CompositeCurve]] = None,
        precision_policy: Optional[PrecisionPolicy] = None,
    ):
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
            raise ValueError(
                "outer_boundary must have at least 3 segments to form a closed region (or be a single inherently closed segment)"
            )

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
                    raise ValueError(
                        f"holes[{i}] must have at least 3 segments to form a closed region (or be a single inherently closed segment)"
                    )

            self.holes = holes.copy()  # Create a copy to avoid external modification

        self._precision_policy = precision_policy or outer_boundary.precision_policy()

    def precision_policy(self) -> PrecisionPolicy:
        """Return the precision policy controlling tolerance decisions."""

        return self._precision_policy or get_precision_policy()

    def _resolve_tolerance(self, tolerance: Optional[float] = None) -> float:
        policy = self.precision_policy()
        if tolerance is not None:
            return tolerance
        return policy.distance_threshold(self.outer_boundary.scale_hint())

    def contains(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
    ) -> Union[bool, np.ndarray]:
        """
        Test if point(s) are inside the region (accounting for holes).
        Uses a robust point-in-polygon algorithm to determine if a point
        is contained within the region. A point is considered inside if:
        1. It is inside the outer boundary, AND
        2. It is NOT inside any of the holes

        Args:
            x: X-coordinate(s) of the test point
            y: Y-coordinate(s) of the test point
            tolerance: Tolerance for containment test

        Returns:
            bool or np.ndarray: True if the point is inside the region, False otherwise
        """
        tol = self._resolve_tolerance(tolerance)

        if np.isscalar(x) and np.isscalar(y):
            if not self.outer_boundary.contains(
                x, y, tolerance=tol, region_containment=True
            ):
                return False

            for hole in self.holes:
                if hole.contains(x, y, tolerance=tol, region_containment=True):
                    return False

            return True
        else:
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            inside = np.asarray(
                self.outer_boundary.contains(
                    x_arr, y_arr, tolerance=tol, region_containment=True
                ),
                dtype=bool,
            )

            for hole in self.holes:
                hole_inside = np.asarray(
                    hole.contains(x_arr, y_arr, tolerance=tol, region_containment=True),
                    dtype=bool,
                )
                inside = inside & ~hole_inside

            return inside

    def contains_boundary(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
    ) -> Union[bool, np.ndarray]:
        """
        Test if point(s) are on the boundary of the region (outer boundary or hole boundaries).

        Args:
            x: X-coordinate(s) of the test point
            y: Y-coordinate(s) of the test point
            tolerance: Tolerance for containment test

        Returns:
            bool or np.ndarray: True if the point is on any boundary, False otherwise
        """
        tol = self._resolve_tolerance(tolerance)

        if np.isscalar(x) and np.isscalar(y):
            if self.outer_boundary.on_curve(x, y, tolerance=tol):
                return True

            for hole in self.holes:
                if hole.contains(x, y, tolerance=tol):
                    return True

            return False
        else:
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            on_bound = np.asarray(
                self.outer_boundary.on_curve(x_arr, y_arr, tolerance=tol), dtype=bool
            )

            for hole in self.holes:
                on_bound = on_bound | np.asarray(
                    hole.contains(x_arr, y_arr, tolerance=tol), dtype=bool
                )

            return on_bound

    def _curve_to_polygon(
        self, curve: CompositeCurve, resolution: int = 100
    ) -> List[Tuple[float, float]]:
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
        # If this composite curve was created by polygon factory, use the exact
        # stored vertices for precise area/containment computations.
        if hasattr(curve, "_polygon_vertices") and curve._polygon_vertices:
            return list(curve._polygon_vertices)

        polygon_points = []

        # For each segment in the composite curve
        for segment in curve.segments:
            # Sample points along this segment
            segment_points = self._sample_segment_boundary(
                segment, resolution // len(curve.segments)
            )
            polygon_points.extend(segment_points)

        return polygon_points

    def _sample_segment_boundary(
        self, segment, num_points: int = 20
    ) -> List[Tuple[float, float]]:
        """
        Sample points along a trimmed curve segment boundary.

        Args:
            segment: TrimmedImplicitCurve segment
            num_points: Number of points to sample

        Returns:
            List of (x, y) points on the segment boundary
        """
        is_curved = getattr(segment, "is_curved", True)

        # If segment exposes explicit polyline approximation, use it
        if hasattr(segment, "get_polyline_approximation"):
            try:
                pts = segment.get_polyline_approximation(resolution=num_points)
                if pts and len(pts) > 1:
                    return [(float(p[0]), float(p[1])) for p in pts]
            except Exception:
                pass

        # If segment is not curved and exposes explicit endpoints (e.g., polygon edges), use them
        if not is_curved and hasattr(segment, "get_endpoints"):
            try:
                endpoints = segment.get_endpoints()
                if isinstance(endpoints, list) and len(endpoints) == 2:
                    (x0, y0), (x1, y1) = endpoints
                    if num_points <= 1:
                        return [(x0, y0)]
                    pts: List[Tuple[float, float]] = []
                    for i in range(num_points):
                        t = i / (num_points - 1)
                        xi = x0 + t * (x1 - x0)
                        yi = y0 + t * (y1 - y0)
                        pts.append((xi, yi))
                    return pts
            except Exception:
                # Fall back to generic sampling below on any error
                pass

        # Exact parametric sampling for circular and elliptical conics
        base_curve = segment
        if hasattr(segment, "base_curve"):
            base_curve = segment.base_curve

        is_conic = False
        conic_type = ""
        if hasattr(base_curve, "conic_type"):
            try:
                conic_type = base_curve.conic_type()
                if conic_type in ("circle", "ellipse"):
                    is_conic = True
            except Exception:
                pass

        if is_conic:
            try:
                coeffs = base_curve._extract_coefficients()
                A, B, C, D, E, F = (
                    coeffs["A"],
                    coeffs["B"],
                    coeffs["C"],
                    coeffs["D"],
                    coeffs["E"],
                    coeffs["F"],
                )

                if conic_type == "circle":
                    d_norm = D / A
                    e_norm = E / A
                    f_norm = F / A

                    center_x = -d_norm / 2
                    center_y = -e_norm / 2
                    radius_sq = (d_norm**2 + e_norm**2) / 4 - f_norm
                    radius = np.sqrt(radius_sq) if radius_sq > 0 else 0.0

                    semi_x = radius
                    semi_y = radius
                    angle = 0.0
                else:  # ellipse
                    if abs(B) < 1e-12:  # Axis-aligned ellipse
                        center_x = -D / (2 * A)
                        center_y = -E / (2 * C)

                        constant = A * center_x**2 + C * center_y**2 - F
                        if constant > 0:
                            semi_x = np.sqrt(constant / A)
                            semi_y = np.sqrt(constant / C)
                        else:
                            semi_x = 0.0
                            semi_y = 0.0
                        angle = 0.0
                    else:  # Rotated ellipse
                        det = 4 * A * C - B**2
                        if abs(det) > 1e-12:
                            center_x = (B * E - 2 * C * D) / det
                            center_y = (B * D - 2 * A * E) / det
                            constant = (
                                A * center_x**2
                                + B * center_x * center_y
                                + C * center_y**2
                                - F
                            )

                            trace = A + C
                            det_matrix = A * C - (B / 2) ** 2
                            discriminant = trace**2 - 4 * det_matrix
                            if discriminant >= 0:
                                lambda1 = (trace + np.sqrt(discriminant)) / 2
                                lambda2 = (trace - np.sqrt(discriminant)) / 2

                                semi_x = (
                                    np.sqrt(constant / lambda1)
                                    if lambda1 > 0 and constant > 0
                                    else 0.0
                                )
                                semi_y = (
                                    np.sqrt(constant / lambda2)
                                    if lambda2 > 0 and constant > 0
                                    else 0.0
                                )
                                angle = 0.5 * np.arctan2(B, A - C)
                            else:
                                semi_x = 0.0
                                semi_y = 0.0
                                angle = 0.0
                        else:
                            center_x = 0.0
                            center_y = 0.0
                            semi_x = 0.0
                            semi_y = 0.0
                            angle = 0.0

                if semi_x > 0 and semi_y > 0:
                    # Generate candidate points on the full circle/ellipse
                    thetas = np.linspace(0, 2 * np.pi, 1000)
                    x_unrot = semi_x * np.cos(thetas)
                    y_unrot = semi_y * np.sin(thetas)

                    if abs(angle) > 1e-12:
                        cos_a = np.cos(angle)
                        sin_a = np.sin(angle)
                        candidate_x = center_x + x_unrot * cos_a - y_unrot * sin_a
                        candidate_y = center_y + x_unrot * sin_a + y_unrot * cos_a
                    else:
                        candidate_x = center_x + x_unrot
                        candidate_y = center_y + y_unrot

                    # Filter candidate points that satisfy the segment's trim mask (vectorized for speed!)
                    candidate_x = np.asarray(candidate_x)
                    candidate_y = np.asarray(candidate_y)
                    mask = np.asarray(
                        segment.contains(candidate_x, candidate_y, tolerance=0.1),
                        dtype=bool,
                    )
                    valid_pts = [
                        (float(cx), float(cy))
                        for cx, cy in zip(candidate_x[mask], candidate_y[mask])
                    ]

                    if len(valid_pts) >= 2:
                        # Downsample to exactly the requested num_points
                        indices = np.linspace(
                            0, len(valid_pts) - 1, num_points, dtype=int
                        )
                        return [valid_pts[idx] for idx in indices]
            except Exception:
                # Fall back to generic sampling below on any error
                pass

        # Get a reasonable bounding box for the segment
        bbox = self._get_segment_bbox(segment)
        x_min, x_max, y_min, y_max = bbox

        boundary_points = []
        tolerance = 0.05  # Tolerance for being "on" the curve

        # Sample points in a grid and find those on the segment boundary in a vectorized way
        grid_size = int(
            np.sqrt(num_points * 4)
        )  # Oversample to ensure we find boundary points
        x_vals = np.linspace(x_min, x_max, grid_size)
        y_vals = np.linspace(y_min, y_max, grid_size)
        X_grid, Y_grid = np.meshgrid(x_vals, y_vals)

        try:
            contains_mask = np.asarray(
                segment.contains(X_grid, Y_grid, tolerance), dtype=bool
            )
            boundary_points = [
                (float(cx), float(cy))
                for cx, cy in zip(X_grid[contains_mask], Y_grid[contains_mask])
            ]
        except Exception:
            # Fallback to scalar loop on failure
            for x_val in x_vals:
                for y_val in y_vals:
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

    def _get_curve_bbox(
        self, curve: CompositeCurve
    ) -> Tuple[float, float, float, float]:
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
        # For explicitly marked squares, use direct calculation
        if getattr(self.outer_boundary, "_is_square", False):
            outer_area = self._calculate_square_area(self.outer_boundary)
        else:
            # Calculate area of outer boundary using polygon approximation
            outer_polygon = self._curve_to_polygon(self.outer_boundary)
            outer_area = self._polygon_area(outer_polygon)

        # Subtract areas of holes
        total_hole_area = 0.0
        for hole in self.holes:
            if getattr(hole, "_is_square", False):
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
        # Prefer explicit square bounds stored by factory to avoid
        # falling back to extremely large default bounding boxes
        # from generic implicit curves.
        if hasattr(curve, "_square_bounds") and curve._square_bounds is not None:
            x_min, x_max, y_min, y_max = curve._square_bounds
        else:
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
            "type": "AreaRegion",
            "outer_boundary": self.outer_boundary.to_dict(),
            "holes": [hole.to_dict() for hole in self.holes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AreaRegion":
        """
        Reconstruct an AreaRegion from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary representation of the AreaRegion

        Returns:
            AreaRegion: Reconstructed AreaRegion instance

        Raises:
            ValueError: If the dictionary format is invalid
        """
        if data.get("type") != "AreaRegion":
            raise ValueError("Dictionary does not represent an AreaRegion")

        # Reconstruct outer boundary
        outer_boundary = CompositeCurve.from_dict(data["outer_boundary"])

        # Reconstruct holes
        holes = []
        if "holes" in data and data["holes"]:
            holes = [CompositeCurve.from_dict(hole_data) for hole_data in data["holes"]]

        return cls(outer_boundary, holes)

    def __str__(self) -> str:
        """String representation of the AreaRegion."""
        hole_count = len(self.holes)
        if hole_count == 0:
            return f"AreaRegion(outer_boundary={self.outer_boundary})"
        else:
            return (
                f"AreaRegion(outer_boundary={self.outer_boundary}, holes={hole_count})"
            )

    def __repr__(self) -> str:
        """Detailed string representation of the AreaRegion."""
        return f"AreaRegion(outer_boundary={repr(self.outer_boundary)}, holes={repr(self.holes)})"

    def get_field(self, strategy: "FieldStrategy") -> "BaseField":
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
