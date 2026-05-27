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

    def _is_grid_cached(self, x: np.ndarray, y: np.ndarray) -> bool:
        if not hasattr(self, "_cache") or self._cache is None:
            return False
        cached_x, cached_y, cached_res = self._cache
        if x.shape != cached_x.shape or y.shape != cached_y.shape:
            return False
        if x is cached_x and y is cached_y:
            return True
        ndim = len(x.shape)
        if ndim == 2:
            h, w = x.shape
            if h < 2 or w < 2:
                return False
            corners = [(0, 0), (0, -1), (-1, 0), (-1, -1)]
            center = (h // 2, w // 2)
            indices = corners + [center]
        elif ndim == 1:
            n = len(x)
            if n < 2:
                return False
            indices = [(0,), (-1,), (n // 2,)]
        else:
            return False
        try:
            for idx in indices:
                if not np.isclose(x[idx], cached_x[idx], atol=1e-9) or not np.isclose(
                    y[idx], cached_y[idx], atol=1e-9
                ):
                    return False
            return True
        except Exception:
            return False

    def clear_cache(self) -> None:
        self._cache = None
        self._cached_segments_ab = None

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the signed distance field at given coordinates.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Signed distance value(s) to the region boundary
        """
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case
            return self._compute_signed_distance(x, y)

        x_array = np.asarray(x)
        y_array = np.asarray(y)

        # Check cache
        if self._is_grid_cached(x_array, y_array):
            return self._cache[2]

        # Handle NaN inputs by propagating them
        if np.isnan(x_array).any() or np.isnan(y_array).any():
            result = np.full_like(x_array, np.nan, dtype=float)
            # Only compute for non-NaN points
            valid_mask = ~np.isnan(x_array) & ~np.isnan(y_array)
            if np.any(valid_mask):
                valid_x = x_array[valid_mask]
                valid_y = y_array[valid_mask]
                valid_result = self._evaluate_vectorized(valid_x, valid_y)
                result[valid_mask] = valid_result
            return result

        result = self._evaluate_vectorized(x_array, y_array)
        self._cache = (x_array, y_array, result)
        return result

    def _evaluate_vectorized(
        self, x_array: np.ndarray, y_array: np.ndarray
    ) -> np.ndarray:
        # Check if points are inside the region
        is_inside = self.region.contains(x_array, y_array)

        # Compute distance to boundary
        distance = self._compute_distance_to_boundary_vectorized(x_array, y_array)

        # Return negative distance inside, positive distance outside
        return np.where(is_inside, -distance, distance)

    def _compute_distance_to_boundary_vectorized(
        self, x_array: np.ndarray, y_array: np.ndarray
    ) -> np.ndarray:
        flat_shape = x_array.shape
        flat_x = x_array.ravel()
        flat_y = y_array.ravel()
        pts_q = np.stack([flat_x, flat_y], axis=1)  # (M, 2)

        if not hasattr(self, "_cached_segments_ab") or self._cached_segments_ab is None:
            segments_ab = []

            if (
                hasattr(self.region, "outer_boundary")
                and self.region.outer_boundary is not None
            ):
                for segment in self.region.outer_boundary.segments:
                    has_linear = False
                    is_curved = getattr(segment, "is_curved", True)
                    if not is_curved and hasattr(segment, "get_endpoints"):
                        try:
                            endpoints = segment.get_endpoints()
                            if endpoints and len(endpoints) == 2:
                                segments_ab.append((endpoints[0], endpoints[1]))
                                has_linear = True
                        except Exception:
                            pass
                    if not has_linear:
                        try:
                            pts = self.region._sample_segment_boundary(
                                segment, num_points=50
                            )
                            if pts and len(pts) >= 2:
                                for k in range(len(pts) - 1):
                                    segments_ab.append((pts[k], pts[k + 1]))
                        except Exception:
                            pass

            # If no segments found, try standard _curve_to_polygon
            if len(segments_ab) == 0:
                try:
                    boundary_points = self.region._curve_to_polygon(
                        self.region.outer_boundary
                    )
                    if boundary_points and len(boundary_points) >= 2:
                        for k in range(len(boundary_points) - 1):
                            segments_ab.append(
                                (boundary_points[k], boundary_points[k + 1])
                            )
                        # If the outer boundary is closed, connect the last point to the first
                        try:
                            closed = False
                            if hasattr(self.region.outer_boundary, "is_closed"):
                                if callable(self.region.outer_boundary.is_closed):
                                    closed = self.region.outer_boundary.is_closed()
                                else:
                                    closed = bool(self.region.outer_boundary.is_closed)
                            if closed:
                                segments_ab.append(
                                    (boundary_points[-1], boundary_points[0])
                                )
                        except Exception:
                            pass
                except Exception:
                    pass

            self._cached_segments_ab = segments_ab
        else:
            segments_ab = self._cached_segments_ab

        if len(segments_ab) == 0:
            return np.ones_like(x_array, dtype=float)

        min_dists_sq = np.full(len(pts_q), float("inf"))

        # Exact vectorized distance to straight line segments
        for (xA, yA), (xB, yB) in segments_ab:
            dx = xB - xA
            dy = yB - yA
            L2 = dx**2 + dy**2
            if L2 < 1e-9:
                d2 = (pts_q[:, 0] - xA) ** 2 + (pts_q[:, 1] - yA) ** 2
                min_dists_sq = np.minimum(min_dists_sq, d2)
            else:
                t = ((pts_q[:, 0] - xA) * dx + (pts_q[:, 1] - yA) * dy) / L2
                t = np.clip(t, 0.0, 1.0)
                px = xA + t * dx
                py = yA + t * dy
                d2 = (pts_q[:, 0] - px) ** 2 + (pts_q[:, 1] - py) ** 2
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
        h = self.resolution / 10  # Use smaller step size than resolution

        grad_x = (self.evaluate(x + h, y) - self.evaluate(x - h, y)) / (2 * h)
        grad_y = (self.evaluate(x, y + h) - self.evaluate(x, y - h)) / (2 * h)

        return (grad_x, grad_y)

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

    def _is_grid_cached(self, x: np.ndarray, y: np.ndarray) -> bool:
        if not hasattr(self, "_cache") or self._cache is None:
            return False
        cached_x, cached_y, cached_res = self._cache
        if x.shape != cached_x.shape or y.shape != cached_y.shape:
            return False
        if x is cached_x and y is cached_y:
            return True
        ndim = len(x.shape)
        if ndim == 2:
            h, w = x.shape
            if h < 2 or w < 2:
                return False
            corners = [(0, 0), (0, -1), (-1, 0), (-1, -1)]
            center = (h // 2, w // 2)
            indices = corners + [center]
        elif ndim == 1:
            n = len(x)
            if n < 2:
                return False
            indices = [(0,), (-1,), (n // 2,)]
        else:
            return False
        try:
            for idx in indices:
                if not np.isclose(x[idx], cached_x[idx], atol=1e-9) or not np.isclose(
                    y[idx], cached_y[idx], atol=1e-9
                ):
                    return False
            return True
        except Exception:
            return False

    def clear_cache(self) -> None:
        self._cache = None

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the occupancy field at given coordinates.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Occupancy value(s) at the given coordinates
        """
        tol = 1e-8
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case
            is_inside = self.region.contains(
                x, y, tolerance=tol
            ) and not self.region.contains_boundary(x, y, tolerance=tol)
            return self.inside_value if is_inside else self.outside_value

        x_array = np.asarray(x)
        y_array = np.asarray(y)

        # Check cache
        if self._is_grid_cached(x_array, y_array):
            return self._cache[2]

        is_inside = self.region.contains(
            x_array, y_array, tolerance=tol
        ) & ~self.region.contains_boundary(x_array, y_array, tolerance=tol)
        result = np.where(is_inside, self.inside_value, self.outside_value)
        self._cache = (x_array, y_array, result)
        return result

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[tuple, tuple]:
        """
        Compute the gradient of the occupancy field.

        For a binary occupancy field, the gradient is zero everywhere except
        at the boundary, where it's undefined. We return zero gradients.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Zero gradient vector(s)
        """
        if np.isscalar(x) and np.isscalar(y):
            return (0.0, 0.0)
        else:
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            zeros_x = np.zeros_like(x_array, dtype=float)
            zeros_y = np.zeros_like(y_array, dtype=float)
            return (zeros_x, zeros_y)

    def level_set(self, level: float) -> "ImplicitCurve":
        """
        Extract a level set from the occupancy field.

        For an occupancy field, meaningful level sets are at the inside_value
        and outside_value boundaries.

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
        Serialize the OccupancyField to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        return {
            "type": "OccupancyField",
            "region": self.region.to_dict(),
            "inside_value": self.inside_value,
            "outside_value": self.outside_value,
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
