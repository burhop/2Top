"""
Field strategy classes for generating scalar fields from AreaRegion objects.

This module implements the FieldStrategy design pattern, which decouples the
algorithm for generating a field from the AreaRegion itself. This enables
pluggable field generation techniques and makes the system highly extensible.

Key Features:
- FieldStrategy abstract base class defining the interface
- SignedDistanceStrategy for generating signed distance fields
- OccupancyFillStrategy for generating binary occupancy fields
- Extensible design for adding new field generation algorithms
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Dict, Any, TYPE_CHECKING
from .base_field import BaseField

if TYPE_CHECKING:
    from .area_region import AreaRegion
    from .implicit_curve import ImplicitCurve


class FieldStrategy(ABC):
    """
    Abstract base class for field generation strategies.

    The FieldStrategy pattern allows different algorithms for generating
    scalar fields from AreaRegion objects. Each strategy implements a
    specific approach to field generation, such as signed distance fields
    or occupancy fields.

    This design enables:
    - Pluggable field generation algorithms
    - Easy extension with new field types
    - Separation of concerns between region representation and field generation
    - Consistent interface for all field generation methods
    """

    @abstractmethod
    def generate_field(self, region: "AreaRegion") -> BaseField:
        """
        Generate a scalar field from an AreaRegion.

        Args:
            region: The AreaRegion to generate a field from

        Returns:
            BaseField representing the generated scalar field
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the strategy to a dictionary.

        Returns:
            Dictionary representation of the strategy
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldStrategy":
        """
        Reconstruct a strategy from a dictionary.

        Args:
            data: Dictionary representation of the strategy

        Returns:
            Reconstructed FieldStrategy instance
        """
        pass


class SignedDistanceStrategy(FieldStrategy):
    """
    Strategy for generating signed distance fields from AreaRegion objects.

    A signed distance field represents the distance to the nearest boundary,
    with negative values inside the region and positive values outside.
    This is useful for:
    - Collision detection and physics simulations
    - Advanced rendering techniques (ray marching, etc.)
    - Morphological operations on shapes
    - Smooth blending and deformation

    The field value at any point (x, y) is:
    - Negative distance to boundary if point is inside the region
    - Positive distance to boundary if point is outside the region
    - Zero on the boundary itself

    Attributes:
        resolution (float): Sampling resolution for distance calculations
    """

    def __init__(self, resolution: float = 0.1):
        """
        Initialize the SignedDistanceStrategy.

        Args:
            resolution: Sampling resolution for distance calculations (smaller = more accurate)
        """
        if resolution <= 0:
            raise ValueError("resolution must be positive")

        self.resolution = resolution

    def generate_field(self, region: "AreaRegion") -> BaseField:
        """
        Generate a signed distance field from an AreaRegion.

        Args:
            region: The AreaRegion to generate a field from

        Returns:
            SignedDistanceField representing the signed distance to the region boundary
        """
        return SignedDistanceField(region, self.resolution)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the strategy to a dictionary.

        Returns:
            Dictionary representation of the strategy
        """
        return {"type": "SignedDistanceStrategy", "resolution": self.resolution}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignedDistanceStrategy":
        """
        Reconstruct a SignedDistanceStrategy from a dictionary.

        Args:
            data: Dictionary representation of the strategy

        Returns:
            Reconstructed SignedDistanceStrategy instance
        """
        if data.get("type") != "SignedDistanceStrategy":
            raise ValueError("Dictionary does not represent a SignedDistanceStrategy")

        resolution = data.get("resolution", 0.1)
        return cls(resolution)


class OccupancyFillStrategy(FieldStrategy):
    """
    Strategy for generating binary occupancy fields from AreaRegion objects.

    An occupancy field is a binary field that returns one value for points
    inside the region and another value for points outside. This is useful for:
    - Simple collision detection
    - Binary masks and selections
    - Volume calculations
    - Boolean operations on regions

    The field value at any point (x, y) is:
    - inside_value if the point is inside the region
    - outside_value if the point is outside the region

    Attributes:
        inside_value (float): Value to return for points inside the region
        outside_value (float): Value to return for points outside the region
    """

    def __init__(self, inside_value: float = 1.0, outside_value: float = 0.0):
        """
        Initialize the OccupancyFillStrategy.

        Args:
            inside_value: Value to return for points inside the region
            outside_value: Value to return for points outside the region
        """
        self.inside_value = inside_value
        self.outside_value = outside_value

    def generate_field(self, region: "AreaRegion") -> BaseField:
        """
        Generate an occupancy field from an AreaRegion.

        Args:
            region: The AreaRegion to generate a field from

        Returns:
            OccupancyField representing the binary occupancy of the region
        """
        return OccupancyField(region, self.inside_value, self.outside_value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the strategy to a dictionary.

        Returns:
            Dictionary representation of the strategy
        """
        return {
            "type": "OccupancyFillStrategy",
            "inside_value": self.inside_value,
            "outside_value": self.outside_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OccupancyFillStrategy":
        """
        Reconstruct an OccupancyFillStrategy from a dictionary.

        Args:
            data: Dictionary representation of the strategy

        Returns:
            Reconstructed OccupancyFillStrategy instance
        """
        if data.get("type") != "OccupancyFillStrategy":
            raise ValueError("Dictionary does not represent an OccupancyFillStrategy")

        inside_value = data.get("inside_value", 1.0)
        outside_value = data.get("outside_value", 0.0)
        return cls(inside_value, outside_value)


class SignedDistanceField(BaseField):
    """
    Scalar field representing signed distance to an AreaRegion boundary.

    This field computes the signed distance from any point to the nearest
    boundary of the region. The sign indicates whether the point is inside
    (negative) or outside (positive) the region.

    Attributes:
        region (AreaRegion): The region to compute distances to
        resolution (float): Sampling resolution for distance calculations
    """

    def __init__(self, region: "AreaRegion", resolution: float = 0.1):
        """
        Initialize a SignedDistanceField.

        Args:
            region: The AreaRegion to compute distances to
            resolution: Sampling resolution for distance calculations
        """
        self.region = region
        self.resolution = resolution
        self._cache = None
        self._cached_segments_ab = None

    def clear_cache(self) -> None:
        """Compatibility hook; distance queries retain no grids or sampled geometry."""
        self._cache = None
        self._cached_segments_ab = None

    def evaluate(self, x, y):
        """Read live coordinates and boundaries, returning fresh signed distances.

        Straight segments use Euclidean point-to-segment distance. Curved sources
        retain the existing sampling approximation. No identity, partial-grid,
        tolerance or persistent geometry cache can track arbitrary public edits.
        Nonfinite coordinates are unavailable (NaN); finite points still evaluate.
        """
        from .numeric import broadcast_coordinates, field_result

        xx, yy, scalar = broadcast_coordinates(x, y)
        finite = np.isfinite(xx) & np.isfinite(yy)
        result = np.full(xx.shape, np.nan)
        if np.any(finite):
            px, py = xx[finite], yy[finite]
            if scalar:
                result[finite] = self._compute_signed_distance(
                    float(px[0]), float(py[0])
                )
            else:
                result[finite] = self._evaluate_vectorized(px, py)
        return field_result(result, xx.shape, scalar)

    def _evaluate_vectorized(self, x_array, y_array):
        is_inside = self.region.contains(x_array, y_array)
        distance = self._compute_distance_to_boundary_vectorized(x_array, y_array)
        return np.where(is_inside, -distance, distance)

    def _boundary_segments(self):
        """Prepare only this query's live outer/hole line segments and samples."""
        segments_ab = []
        for boundary in [self.region.outer_boundary, *self.region.holes]:
            boundary_segments = []
            for segment in boundary.segments:
                is_curved = getattr(segment, "is_curved", True)
                if not is_curved and hasattr(segment, "get_endpoints"):
                    endpoints = segment.get_endpoints()
                    if endpoints and len(endpoints) == 2:
                        # Copy endpoint values into query-local immutable pairs.
                        boundary_segments.append(tuple(tuple(p) for p in endpoints))
                        continue
                points = self.region._sample_segment_boundary(segment, num_points=50)
                if points and len(points) >= 2:
                    boundary_segments.extend(zip(points[:-1], points[1:]))
            if not boundary_segments:
                points = self.region._curve_to_polygon(boundary)
                if points and len(points) >= 2:
                    boundary_segments.extend(zip(points[:-1], points[1:]))
                    if boundary.is_closed():
                        boundary_segments.append((points[-1], points[0]))
            if not boundary_segments:
                raise ValueError("Signed distance boundary has no available segments")
            segments_ab.extend(boundary_segments)
        return segments_ab

    def _compute_distance_to_boundary_vectorized(self, x_array, y_array):
        flat_shape = x_array.shape
        flat_x = x_array.ravel()
        flat_y = y_array.ravel()
        min_dists_sq = np.full(flat_x.size, np.inf)

        # Query-local preparation avoids stale endpoints/samples after region edits.
        for (xA, yA), (xB, yB) in self._boundary_segments():
            dx, dy = xB - xA, yB - yA
            length_sq = dx**2 + dy**2
            if length_sq < 1e-9:
                d2 = (flat_x - xA) ** 2 + (flat_y - yA) ** 2
            else:
                t = ((flat_x - xA) * dx + (flat_y - yA) * dy) / length_sq
                t = np.clip(t, 0.0, 1.0)
                d2 = (flat_x - (xA + t * dx)) ** 2 + (flat_y - (yA + t * dy)) ** 2
            min_dists_sq = np.minimum(min_dists_sq, d2)
        return np.sqrt(min_dists_sq).reshape(flat_shape)

    def _compute_signed_distance(self, x: float, y: float) -> float:
        """
        Compute the signed distance from a point to the region boundary.

        Args:
            x: x-coordinate
            y: y-coordinate

        Returns:
            Signed distance to the boundary
        """
        # Check if point is inside the region
        is_inside = self.region.contains(x, y)

        # Compute unsigned distance to boundary
        distance = self._compute_distance_to_boundary(x, y)

        # Apply sign based on containment
        return -distance if is_inside else distance

    def _compute_distance_to_boundary(self, x: float, y: float) -> float:
        """
        Compute the unsigned distance from a point to the region boundary.

        Args:
            x: x-coordinate
            y: y-coordinate

        Returns:
            Unsigned distance to the boundary
        """
        res = self._compute_distance_to_boundary_vectorized(
            np.array([x]), np.array([y])
        )
        return float(res[0])

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[tuple, tuple]:
        """
        Compute the gradient of the signed distance field.

        The gradient points in the direction of steepest increase in distance,
        which is the outward normal direction from the boundary.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Gradient vector(s) at the given coordinates
        """
        # Use numerical gradient for simplicity
        from .numeric import broadcast_coordinates, field_result

        x, y, scalar = broadcast_coordinates(x, y)
        if scalar:
            x, y = float(x), float(y)
        h = self.resolution / 10  # Use smaller step size than resolution

        grad_x = (self.evaluate(x + h, y) - self.evaluate(x - h, y)) / (2 * h)
        grad_y = (self.evaluate(x, y + h) - self.evaluate(x, y - h)) / (2 * h)

        return tuple(field_result(v, np.shape(x), scalar) for v in (grad_x, grad_y))

    def level_set(self, level: float) -> "ImplicitCurve":
        """
        Extract a level set from the signed distance field.

        Args:
            level: The level value to extract

        Returns:
            ImplicitCurve representing the level set
        """
        import sympy as sp
        from .procedural_curve import ProceduralCurve

        # Create a procedural curve that represents the level set
        x, y = sp.symbols("x y")

        def level_set_function(x_val, y_val):
            return self.evaluate(x_val, y_val) - level

        return ProceduralCurve(level_set_function, (x, y))

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the SignedDistanceField to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        return {
            "type": "SignedDistanceField",
            "region": self.region.to_dict(),
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignedDistanceField":
        """
        Reconstruct a SignedDistanceField from a dictionary.

        Args:
            data: Dictionary representation of the field

        Returns:
            Reconstructed SignedDistanceField instance
        """
        if data.get("type") != "SignedDistanceField":
            raise ValueError("Dictionary does not represent a SignedDistanceField")

        from .area_region import AreaRegion

        region = AreaRegion.from_dict(data["region"])
        resolution = data.get("resolution", 0.1)

        return cls(region, resolution)


class OccupancyField(BaseField):
    """
    Binary scalar field representing occupancy of an AreaRegion.

    This field returns one value for points inside the region and another
    value for points outside, creating a binary mask of the region.

    Attributes:
        region (AreaRegion): The region to test occupancy for
        inside_value (float): Value for points inside the region
        outside_value (float): Value for points outside the region
    """

    def __init__(
        self,
        region: "AreaRegion",
        inside_value: float = 1.0,
        outside_value: float = 0.0,
    ):
        """
        Initialize an OccupancyField.

        Args:
            region: The AreaRegion to test occupancy for
            inside_value: Value for points inside the region
            outside_value: Value for points outside the region
        """
        self.region = region
        self.inside_value = inside_value
        self.outside_value = outside_value
        self._cache = None
        self.inside_value, self.outside_value = self._validated_values()

    def _validated_values(self):
        """Validate live public values; do not cache mutable field configuration."""
        from .numeric import real_array

        values = [real_array(v) for v in (self.inside_value, self.outside_value)]
        if any(v.shape != () or not np.isfinite(v) for v in values):
            raise ValueError("Occupancy values must be finite real scalars")
        return tuple(float(v) for v in values)

    def clear_cache(self) -> None:
        """Retain the common cache API; occupancy queries always read live state."""
        self._cache = None

    @staticmethod
    def _predicate_mask(value, shape):
        value = np.asarray(value)
        if value.dtype.kind != "b":
            raise ValueError("Region predicates must return booleans")
        return np.broadcast_to(value, shape)

    def _domain_mask(self, x, y, scalar=False):
        """Conservatively reject nonfinite or unavailable boundary evaluations."""
        from .numeric import field_result
        from .area_region import AreaRegion

        if not isinstance(self.region, AreaRegion):
            raise TypeError("Occupancy region must be an AreaRegion")

        valid = np.ones(x.shape, dtype=bool)
        coordinates = (float(x[0]), float(y[0])) if scalar else (x, y)
        for boundary in [self.region.outer_boundary, *self.region.holes]:
            tolerance = boundary._resolve_distance_tolerance(None)
            if not boundary.segments or not boundary.is_closed(tolerance=tolerance):
                raise ValueError("Occupancy requires nonempty closed region boundaries")
            for segment in boundary.segments:
                with np.errstate(all="ignore"):
                    value = field_result(segment.evaluate(*coordinates), x.shape, False)
                valid &= np.isfinite(value)
        return valid

    def evaluate(self, x, y):
        """Return the legacy strict-interior mask; invalid domain points are NaN.

        No cross-query result cache is safe for public mutable coordinates,
        values, regions and callbacks. The algebraic query cache still reuses
        this field within one pointwise evaluation.
        """
        from .numeric import broadcast_coordinates, field_result

        inside_value, outside_value = self._validated_values()
        xx, yy, scalar = broadcast_coordinates(x, y)
        finite = np.isfinite(xx) & np.isfinite(yy)
        result = np.full(xx.shape, np.nan)
        if inside_value == outside_value:
            result[finite] = inside_value
        elif np.any(finite):
            px, py = xx[finite], yy[finite]
            domain = self._domain_mask(px, py, scalar)
            selected = np.full(px.shape, np.nan)
            if np.any(domain):
                dx, dy = px[domain], py[domain]
                shape = dx.shape
                coordinates = (float(dx[0]), float(dy[0])) if scalar else (dx, dy)
                inside = self._predicate_mask(
                    self.region.contains(*coordinates, tolerance=1e-8), shape
                )
                boundary = self._predicate_mask(
                    self.region.contains_boundary(*coordinates, tolerance=1e-8), shape
                )
                selected[domain] = np.where(
                    inside & ~boundary, inside_value, outside_value
                )
            result[finite] = selected
        return field_result(result, xx.shape, scalar)

    def gradient(self, x, y):
        """Zero on valid constant pieces; both components NaN near jumps.

        The 2e-8 guard conservatively includes the existing 1e-8 exclusion
        band's transition. Bounded representable-neighbor membership checks
        supplement trim/predicate mismatches; sampling is not a continuity proof.
        Predicate units do not define a distance offset.
        Equal finite output values define a constant field and need no boundary
        queries. Known invalid source domains remain explicit.
        """
        from .numeric import broadcast_coordinates, field_result

        inside_value, outside_value = self._validated_values()
        xx, yy, scalar = broadcast_coordinates(x, y)
        finite = np.isfinite(xx) & np.isfinite(yy)
        result = np.full(xx.shape, np.nan)
        if inside_value == outside_value:
            result[finite] = 0.0
        elif np.any(finite):
            px, py = xx[finite], yy[finite]
            domain = self._domain_mask(px, py, scalar)
            selected = np.full(px.shape, np.nan)
            if np.any(domain):
                dx, dy = px[domain], py[domain]
                coordinates = (float(dx[0]), float(dy[0])) if scalar else (dx, dy)
                inside = self._predicate_mask(
                    self.region.contains(*coordinates, tolerance=1e-8), dx.shape
                )
                boundary = self._predicate_mask(
                    self.region.contains_boundary(*coordinates, tolerance=2e-8),
                    dx.shape,
                )
                uncertain = np.array(boundary, copy=True)
                candidates = ~boundary
                if np.any(candidates):
                    cx, cy = dx[candidates], dy[candidates]
                    expected = np.where(inside[candidates], inside_value, outside_value)
                    changed = np.zeros(cx.shape, dtype=bool)
                    for axis in (0, 1):
                        for sign in (-1, 1):
                            base = cx if axis == 0 else cy
                            with np.errstate(all="ignore"):
                                neighbor = base + sign * 2e-8
                                neighbor = np.where(
                                    neighbor == base,
                                    np.nextafter(base, sign * np.inf),
                                    neighbor,
                                )
                            nx, ny = (neighbor, cy) if axis == 0 else (cx, neighbor)
                            coordinates = (
                                (float(nx[0]), float(ny[0])) if scalar else (nx, ny)
                            )
                            observed = np.asarray(self.evaluate(*coordinates))
                            changed |= ~np.isfinite(observed) | (observed != expected)
                    uncertain[candidates] |= changed
                selected[domain] = np.where(uncertain, np.nan, 0.0)
            result[finite] = selected
        return tuple(field_result(v, xx.shape, scalar) for v in (result, result.copy()))

    def level_set(self, level):
        """Reject binary-mask levels: empty sets or plateaus are not regular curves.

        Use the existing region outer boundary and holes for boundary geometry;
        choose SignedDistanceStrategy explicitly when a distance contour is needed.
        """
        from .bounds import rational_level
        import sympy as sp

        exact = rational_level(level)
        inside_value, outside_value = self._validated_values()
        if exact in (sp.Rational(inside_value), sp.Rational(outside_value)):
            raise ValueError(
                "Occupancy endpoint level is empty or a plateau, not a regular implicit curve"
            )
        raise ValueError("Occupancy level is empty, not an interpolated boundary curve")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the OccupancyField to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        inside_value, outside_value = self._validated_values()
        return {
            "type": "OccupancyField",
            "region": self.region.to_dict(),
            "inside_value": inside_value,
            "outside_value": outside_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OccupancyField":
        """
        Reconstruct an OccupancyField from a dictionary.

        Args:
            data: Dictionary representation of the field

        Returns:
            Reconstructed OccupancyField instance
        """
        if data.get("type") != "OccupancyField":
            raise ValueError("Dictionary does not represent an OccupancyField")

        from .area_region import AreaRegion

        region = AreaRegion.from_dict(data["region"])
        inside_value = data.get("inside_value", 1.0)
        outside_value = data.get("outside_value", 0.0)

        return cls(region, inside_value, outside_value)
