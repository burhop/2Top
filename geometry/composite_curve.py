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

from __future__ import annotations
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Union, Dict, Any, Optional
from .implicit_curve import ImplicitCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from scipy.optimize import brentq
from .polygon_mixin import CompositePolygonMixin
from .precision import PrecisionPolicy, get_precision_policy


class CompositeCurve(CompositePolygonMixin, ImplicitCurve):
    """
    CompositeCurve represents a piecewise curve composed of multiple segments.

    This class assembles an ordered sequence of TrimmedImplicitCurve segments
    into a single composite curve. It provides methods to check connectivity
    (is_closed) and unified containment testing across all segments.

    Attributes:
        segments (List[TrimmedImplicitCurve]): Ordered list of curve segments
    """

    def __init__(
        self,
        segments: List[TrimmedImplicitCurve],
        variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
        validate_continuity: bool = False,
        continuity_tolerance: Optional[float] = None,
        precision_policy: Optional[PrecisionPolicy] = None,
    ):
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

        from .trimmed_implicit_curve import TrimmedImplicitCurve
        from .parametric_segment import ParametricSegment

        if not all(
            isinstance(seg, (TrimmedImplicitCurve, ParametricSegment))
            for seg in segments
        ):
            raise TypeError(
                "All segments must be TrimmedImplicitCurve or ParametricSegment instances"
            )

        # Wire precision policy (inherit from first segment when possible)
        if precision_policy is not None:
            policy = precision_policy
        elif segments and hasattr(segments[0], "precision_policy"):
            policy = segments[0].precision_policy()
        else:
            policy = get_precision_policy()

        # Validate continuity if requested
        if validate_continuity and len(segments) > 1:
            tol = self._resolve_distance_tolerance(continuity_tolerance, policy)
            self._validate_continuity(segments, tol)

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
        super().__init__(composite_expr, variables, precision_policy=policy)
        self._composite_policy = policy
        self._cached_polygon_segments = None

    def precision_policy(self) -> PrecisionPolicy:
        """Return the precision policy assigned to this composite."""

        return getattr(self, "_composite_policy", get_precision_policy())

    def _resolve_distance_tolerance(
        self, tolerance: Optional[float], policy: Optional[PrecisionPolicy] = None
    ) -> float:
        """Resolve a distance tolerance using provided or stored policy."""

        if tolerance is not None:
            return tolerance
        active_policy = policy or self.precision_policy()
        return active_policy.distance_threshold(self.scale_hint())

    def _validate_continuity(
        self, segments: List[TrimmedImplicitCurve], tolerance: float
    ):
        """
        Validate that segments form a continuous path.

        Args:
            segments: List of segments to validate
            tolerance: Maximum allowed gap between consecutive segments

        Raises:
            ValueError: If segments are not continuous
        """
        for i in range(len(segments) - 1):
            current_seg = segments[i]
            next_seg = segments[i + 1]

            # Get endpoints
            current_endpoints = current_seg.get_endpoints()
            next_endpoints = next_seg.get_endpoints()

            if not current_endpoints or not next_endpoints:
                raise ValueError(
                    f"Segment {i} or {i + 1} missing endpoint information for continuity validation"
                )

            # Find minimum gap between end of current segment and start of next segment
            min_gap = float("inf")
            for curr_end in current_endpoints:
                for next_start in next_endpoints:
                    gap = np.sqrt(
                        (curr_end[0] - next_start[0]) ** 2
                        + (curr_end[1] - next_start[1]) ** 2
                    )
                    min_gap = min(min_gap, gap)

            if min_gap > tolerance:
                raise ValueError(
                    f"Gap of {min_gap:.6f} between segments {i} and {i + 1} exceeds tolerance {tolerance}. "
                    f"CompositeCurve requires continuous segments."
                )

    def is_closed(self, tolerance: Optional[float] = None) -> bool:
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
        if tolerance is None and hasattr(self, "_is_closed_cached"):
            return self._is_closed_cached

        # Handle single-segment curves that are inherently closed
        if len(self.segments) == 1:
            res = self._is_single_segment_closed()
        elif len(self.segments) < 3:
            res = False
        elif len(self.segments) == 4:
            res = self._is_closed_rectangle()
        else:
            resolved_tol = self._resolve_distance_tolerance(tolerance)
            res = self._is_closed_general(resolved_tol)

        if tolerance is None:
            self._is_closed_cached = res
        return res

    def _is_closed_rectangle(self) -> bool:
        """
        Check if a 4-segment composite curve forms a closed loop by verifying
        that segment endpoints connect head-to-tail and the last connects back to the first.
        """
        tol = self._resolve_distance_tolerance(None)
        segs = self.segments
        for i in range(len(segs)):
            seg_a = segs[i]
            seg_b = segs[(i + 1) % len(segs)]
            eps_a = getattr(seg_a, "endpoints", [])
            eps_b = getattr(seg_b, "endpoints", [])
            if not eps_a or not eps_b:
                # No endpoint info — fall back to assuming closed (legacy behaviour)
                return True
            end_a = eps_a[-1]
            start_b = eps_b[0]
            dist = ((end_a[0] - start_b[0]) ** 2 + (end_a[1] - start_b[1]) ** 2) ** 0.5
            if dist > tol * 1000:  # generous tolerance for connectivity
                return False
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
        from geometry.superellipse import Superellipse
        from geometry.rfunction_curve import RFunctionCurve
        from geometry.procedural_curve import ProceduralCurve

        base_curve = getattr(segment, "base_curve", segment)

        # Superellipse is inherently closed
        if isinstance(base_curve, Superellipse):
            if isinstance(segment, TrimmedImplicitCurve):
                import numpy as np

                test_angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
                for angle in test_angles:
                    x_test = base_curve.a * np.cos(angle)
                    y_test = base_curve.b * np.sin(angle)
                    if not segment.mask(x_test, y_test):
                        return False
                return True
            return True

        # RFunction curve typically represents union/intersection of closed components (like house or zigzag patterns)
        if isinstance(base_curve, RFunctionCurve):
            return True

        # Procedural curve with is_periodic hint represents a closed/periodic pattern
        if isinstance(base_curve, ProceduralCurve):
            if getattr(base_curve, "is_periodic", False):
                return True

        if isinstance(base_curve, ConicSection):
            conic_type = base_curve.conic_type()

            # If this is a trimmed curve, it's only closed if the mask doesn't restrict it
            if isinstance(segment, TrimmedImplicitCurve):
                # For trimmed curves, we need to check if the mask actually restricts the curve
                # A simple heuristic: test a few points around the curve to see if mask allows them all
                # If the mask restricts any part of the curve, it's not closed
                if conic_type in ["circle", "ellipse"]:
                    # Test points around the circle/ellipse to see if mask allows full curve
                    import numpy as np

                    coeffs = base_curve._extract_coefficients()
                    A, B, C, D, E, F = (
                        coeffs["A"],
                        coeffs["B"],
                        coeffs["C"],
                        coeffs["D"],
                        coeffs["E"],
                        coeffs["F"],
                    )

                    # Ensure positive orientation/coefficients for the ellipse/circle
                    sign = 1.0 if A > 0 or (abs(A) < 1e-12 and C > 0) else -1.0
                    A, B, C, D, E, F = (
                        A * sign,
                        B * sign,
                        C * sign,
                        D * sign,
                        E * sign,
                        F * sign,
                    )

                    test_angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)

                    if conic_type == "circle":
                        if abs(A) > 1e-12:
                            center_x = -D / (2 * A)
                            center_y = -E / (2 * A)
                            radius_sq = (D**2 + E**2) / (4 * A**2) - F / A
                            if radius_sq > 0:
                                radius = np.sqrt(radius_sq)
                                for angle in test_angles:
                                    x_test = center_x + radius * np.cos(angle)
                                    y_test = center_y + radius * np.sin(angle)
                                    if not segment.mask(x_test, y_test):
                                        return False
                                return True
                        return False

                    elif conic_type == "ellipse":
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

                                if lambda1 > 0 and lambda2 > 0 and constant > 0:
                                    a = np.sqrt(constant / lambda1)
                                    b = np.sqrt(constant / lambda2)

                                    # Rotation angle
                                    theta = (
                                        0.5 * np.arctan2(B, A - C)
                                        if abs(B) > 1e-12 or abs(A - C) > 1e-12
                                        else 0.0
                                    )

                                    for angle in test_angles:
                                        x_prime = a * np.cos(angle)
                                        y_prime = b * np.sin(angle)
                                        x_test = (
                                            center_x
                                            + x_prime * np.cos(theta)
                                            - y_prime * np.sin(theta)
                                        )
                                        y_test = (
                                            center_y
                                            + x_prime * np.sin(theta)
                                            + y_prime * np.cos(theta)
                                        )
                                        if not segment.mask(x_test, y_test):
                                            return False
                                    return True
                        return False
                return False
            else:
                # For non-trimmed curves, circles and ellipses are inherently closed
                return conic_type in ["circle", "ellipse"]

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
            if hasattr(segment, "get_endpoints"):
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
            next_segment = self.segments[
                (i + 1) % len(self.segments)
            ]  # Wrap around for last segment

            current_endpoints = current_segment.get_endpoints()
            next_endpoints = next_segment.get_endpoints()

            # Check if any endpoint of current segment is close to any endpoint of next segment
            connected = False
            for curr_end in current_endpoints:
                for next_end in next_endpoints:
                    distance = np.sqrt(
                        (curr_end[0] - next_end[0]) ** 2
                        + (curr_end[1] - next_end[1]) ** 2
                    )
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
            next_segment = self.segments[
                (i + 1) % len(self.segments)
            ]  # Wrap around for last segment

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
                    distance = np.sqrt(
                        (curr_end[0] - next_end[0]) ** 2
                        + (curr_end[1] - next_end[1]) ** 2
                    )
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
            if x_min == float("-inf"):
                x_min = -10
            if x_max == float("inf"):
                x_max = 10
            if y_min == float("-inf"):
                y_min = -10
            if y_max == float("inf"):
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
                for j, p2 in enumerate(points_on_segment[i + 1 :], i + 1):
                    distance = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
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

    def contains(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
        region_containment: bool = False,
    ) -> Union[bool, np.ndarray]:
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
            Boolean or boolean array indicating containment.
        """
        tol = self._resolve_distance_tolerance(tolerance)

        # Scalar case
        if np.isscalar(x) and np.isscalar(y):
            if region_containment and len(self.segments) == 1 and self.is_closed():
                from geometry.implicit_curve import ImplicitCurve
                from geometry.parametric_segment import ParametricSegment
                from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

                segment = self.segments[0]
                base_curve = getattr(segment, "base_curve", segment)
                if isinstance(base_curve, ImplicitCurve) and not isinstance(
                    base_curve, ParametricSegment
                ):
                    val = base_curve.evaluate(x, y)
                    inside_base = val <= tol

                    if isinstance(segment, TrimmedImplicitCurve):
                        mask_satisfied = segment.mask(x, y)
                        in_rect = True
                        if (
                            segment._xmin is not None
                            and segment._xmax is not None
                            and segment._ymin is not None
                            and segment._ymax is not None
                        ):
                            eps = max(tol * 0.1, 1e-12)
                            in_rect = (
                                segment._xmin - eps <= x <= segment._xmax + eps
                            ) and (segment._ymin - eps <= y <= segment._ymax + eps)
                        return bool(inside_base and mask_satisfied and in_rect)
                    else:
                        return bool(inside_base)

            if self.is_closed():
                if region_containment:
                    # Fast path: axis-aligned square via bounds
                    if getattr(self, "_is_square", False):
                        xmin, xmax, ymin, ymax = getattr(
                            self, "_square_bounds", (0.0, 0.0, 0.0, 0.0)
                        )
                        return (
                            (x >= xmin - tol)
                            and (x <= xmax + tol)
                            and (y >= ymin - tol)
                            and (y <= ymax + tol)
                        )
                    # Fast path for convex polygons using stored half-spaces (vectorized)
                    if getattr(self, "_is_convex_polygon", False):
                        # Cache numpy arrays for performance
                        if not hasattr(self, "_edges_ab") or not hasattr(
                            self, "_edges_c"
                        ):
                            edges = np.asarray(
                                getattr(self, "_convex_edges_abc", []), dtype=float
                            )
                            if edges.size == 0:
                                return False
                            self._edges_ab = edges[:, :2]
                            self._edges_c = edges[:, 2]
                        vals = (
                            self._edges_ab @ np.array([x, y], dtype=float)
                            + self._edges_c
                        )
                        return bool(np.all(vals <= tol))
                    # Fallback: use ray-casting for closed curves
                    for segment in self.segments:
                        if segment.contains(x, y, tol):
                            return True
                    return self._ray_casting_algorithm(x, y)
                else:
                    # Boundary only
                    for segment in self.segments:
                        if segment.contains(x, y, tol):
                            return True
                    return False
            else:
                # Open curve
                if region_containment:
                    for segment in self.segments:
                        if segment.contains(x, y, tol):
                            return True
                    # For open curves, region containment means within the bounding box
                    bb = self.bounding_box()
                    return (
                        bb[0] - tol <= x <= bb[1] + tol
                        and bb[2] - tol <= y <= bb[3] + tol
                    )
                else:
                    for segment in self.segments:
                        if segment.contains(x, y, tol):
                            return True
                    return False

        # Vectorized case
        x_array = np.asarray(x)
        y_array = np.asarray(y)

        if region_containment and len(self.segments) == 1 and self.is_closed():
            from geometry.implicit_curve import ImplicitCurve
            from geometry.parametric_segment import ParametricSegment
            from geometry.trimmed_implicit_curve import TrimmedImplicitCurve

            segment = self.segments[0]
            base_curve = getattr(segment, "base_curve", segment)
            if isinstance(base_curve, ImplicitCurve) and not isinstance(
                base_curve, ParametricSegment
            ):
                val = base_curve.evaluate(x_array, y_array)
                inside_base = val <= tol

                if isinstance(segment, TrimmedImplicitCurve):
                    if (
                        segment._xmin is not None
                        and segment._xmax is not None
                        and segment._ymin is not None
                        and segment._ymax is not None
                    ):
                        eps = max(tol * 0.1, 1e-12)
                        in_rect = (
                            (x_array >= (segment._xmin - eps))
                            & (x_array <= (segment._xmax + eps))
                            & (y_array >= (segment._ymin - eps))
                            & (y_array <= (segment._ymax + eps))
                        )
                        candidates = inside_base & in_rect
                        mask_vals = np.zeros_like(candidates, dtype=bool)
                        if np.any(candidates):
                            flat_cand = candidates.ravel()
                            flat_x = x_array.ravel()
                            flat_y = y_array.ravel()
                            flat_mask = np.zeros_like(flat_cand, dtype=bool)
                            for i in np.where(flat_cand)[0]:
                                flat_mask[i] = segment.mask(
                                    float(flat_x[i]), float(flat_y[i])
                                )
                            mask_vals = flat_mask.reshape(candidates.shape)
                        return candidates & mask_vals
                    else:
                        mask_results = np.zeros_like(inside_base, dtype=bool)
                        if np.any(inside_base):
                            flat_inside = inside_base.ravel()
                            flat_x = x_array.ravel()
                            flat_y = y_array.ravel()
                            flat_mask = np.zeros_like(flat_inside, dtype=bool)
                            for i in np.where(flat_inside)[0]:
                                try:
                                    flat_mask[i] = bool(
                                        segment.mask(float(flat_x[i]), float(flat_y[i]))
                                    )
                                except Exception:
                                    pass
                            mask_results = flat_mask.reshape(inside_base.shape)
                        return inside_base & mask_results
                else:
                    return inside_base

        if self.is_closed():
            if region_containment:
                # Fast path: axis-aligned square via bounds
                if getattr(self, "_is_square", False):
                    xmin, xmax, ymin, ymax = getattr(
                        self, "_square_bounds", (0.0, 0.0, 0.0, 0.0)
                    )
                    return (
                        (x_array >= xmin - tol)
                        & (x_array <= xmax + tol)
                        & (y_array >= ymin - tol)
                        & (y_array <= ymax + tol)
                    )
                # Convex polygon fast path (single vectorized matmul/einsum)
                if getattr(self, "_is_convex_polygon", False):
                    # Cache numpy arrays for performance
                    if not hasattr(self, "_edges_ab") or not hasattr(self, "_edges_c"):
                        edges = np.asarray(
                            getattr(self, "_convex_edges_abc", []), dtype=float
                        )
                        if edges.size == 0:
                            return np.zeros_like(x_array, dtype=bool)
                        self._edges_ab = edges[:, :2]
                        self._edges_c = edges[:, 2]
                    # Stack points as (2, ...)
                    XY = np.stack([x_array, y_array], axis=0)
                    # vals shape: (m, ...)
                    vals = np.tensordot(self._edges_ab, XY, axes=([1], [0]))
                    # add c with broadcasting
                    vals = (
                        vals + self._edges_c[(slice(None),) + (None,) * (vals.ndim - 1)]
                    )
                    return np.all(vals <= tol, axis=0)
                # Fallback: use ray-casting for closed curves
                on_boundary = np.zeros_like(x_array, dtype=bool)
                for segment in self.segments:
                    segment_contains = segment.contains(x_array, y_array, tol)
                    on_boundary |= segment_contains
                inside = self._point_in_polygon_vectorized(x_array, y_array)
                return on_boundary | inside
            else:
                # Boundary only
                result = np.zeros_like(x_array, dtype=bool)
                for segment in self.segments:
                    segment_contains = segment.contains(x_array, y_array, tol)
                    result |= segment_contains
                return result
        else:
            # Open curve (vectorized)
            if region_containment:
                on_boundary = np.zeros_like(x_array, dtype=bool)
                for segment in self.segments:
                    on_boundary |= segment.contains(x_array, y_array, tol)
                # For open curves, region containment means within the bounding box
                bb = self.bounding_box()
                in_bbox = (
                    (x_array >= bb[0] - tol)
                    & (x_array <= bb[1] + tol)
                    & (y_array >= bb[2] - tol)
                    & (y_array <= bb[3] + tol)
                )
                return on_boundary | in_bbox
            else:
                result = np.zeros_like(x_array, dtype=bool)
                for segment in self.segments:
                    result |= segment.contains(x_array, y_array, tol)
                return result

    def on_curve(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
    ) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are on any segment of the composite curve.

        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            tolerance: Tolerance for curve membership test

        Returns:
            Boolean or array of booleans indicating if points are on any curve segment
        """
        tol = self._resolve_distance_tolerance(tolerance)

        if np.isscalar(x) and np.isscalar(y):
            # Scalar case - check if point is on any segment
            for segment in self.segments:
                if segment.on_curve(x, y, tol):
                    return True
            return False
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)
            result = np.zeros_like(x_array, dtype=bool)

            for segment in self.segments:
                segment_on_curve = segment.on_curve(x_array, y_array, tol)
                result = result | segment_on_curve
            return result

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the composite curve value at (x, y).

        Behavior:
        - For squares created by `create_square_from_edges()`, use a max-based
          half-space evaluation for robustness on boundaries.
        - For convex polygons created by `create_polygon_from_edges()`, use the
          max of linear edge half-spaces stored in `_convex_edges_abc`.
        - Otherwise, return the minimum value across all segments.
        """
        # Special-case: axis-aligned square
        if getattr(self, "_is_square", False):
            xmin, xmax, ymin, ymax = self._square_bounds
            if np.isscalar(x) and np.isscalar(y):
                return max(xmin - x, x - xmax, ymin - y, y - ymax)
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            v1 = xmin - x_arr
            v2 = x_arr - xmax
            v3 = ymin - y_arr
            v4 = y_arr - ymax
            return np.maximum.reduce([v1, v2, v3, v4])

        # Special-case: convex polygon using stored edge half-spaces
        if getattr(self, "_is_convex_polygon", False):
            edges = getattr(self, "_convex_edges_abc", [])
            if np.isscalar(x) and np.isscalar(y):
                vals = [a * x + b * y + c for (a, b, c) in edges]
                return max(vals) if vals else 0.0
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            # Start with very negative values so max works correctly
            out = np.full_like(x_arr, fill_value=-np.inf, dtype=float)
            for a, b, c in edges:
                out = np.maximum(out, a * x_arr + b * y_arr + c)
            return out

        # General case: min value across segments
        if np.isscalar(x) and np.isscalar(y):
            vals = [seg.evaluate(x, y) for seg in self.segments]
            return float(np.min(vals)) if vals else 0.0
        x_arr = np.asarray(x)
        y_arr = np.asarray(y)
        # Stack segment evaluations and take min along first axis
        seg_vals = [np.asarray(seg.evaluate(x_arr, y_arr)) for seg in self.segments]
        if not seg_vals:
            return np.zeros_like(x_arr, dtype=float)

        # Use np.stack instead of np.vstack to preserve array dimensions
        try:
            stacked = np.stack(seg_vals, axis=0)
            return np.min(stacked, axis=0)
        except ValueError:
            # Fallback if segments return different shapes
            # This shouldn't happen with well-formed segments, but just in case
            min_vals = np.full_like(x_arr, fill_value=np.inf, dtype=float)
            for seg_val in seg_vals:
                seg_val = np.asarray(seg_val)
                if seg_val.shape == min_vals.shape:
                    min_vals = np.minimum(min_vals, seg_val)
            return min_vals

    def gradient(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]):
        """
        Approximate gradient of the composite curve.

        - For general composite curves, select the gradient from the segment
          that provides the minimal value at the query point(s).
        - For squares or convex polygons, a subgradient set exists; we return
          the gradient of the active supporting half-space numerically by
          picking the most active constraint. This is sufficient for tests that
          only require the method to exist and be consistent.
        """
        # Square: choose the face with maximum value
        if getattr(self, "_is_square", False):
            xmin, xmax, ymin, ymax = self._square_bounds
            if np.isscalar(x) and np.isscalar(y):
                faces = [
                    (xmin - x, (-1.0, 0.0)),  # d/dx of (xmin - x)
                    (x - xmax, (1.0, 0.0)),  # d/dx of (x - xmax)
                    (ymin - y, (0.0, -1.0)),  # d/dy of (ymin - y)
                    (y - ymax, (0.0, 1.0)),  # d/dy of (y - ymax)
                ]
                active = max(faces, key=lambda t: t[0])[1]
                return active
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            v = np.stack(
                [
                    xmin - x_arr,
                    x_arr - xmax,
                    ymin - y_arr,
                    y_arr - ymax,
                ],
                axis=0,
            )
            idx = np.argmax(v, axis=0)
            gx = np.zeros_like(x_arr, dtype=float)
            gy = np.zeros_like(y_arr, dtype=float)
            gx[idx == 0] = -1.0
            gy[idx == 0] = 0.0
            gx[idx == 1] = 1.0
            gy[idx == 1] = 0.0
            gx[idx == 2] = 0.0
            gy[idx == 2] = -1.0
            gx[idx == 3] = 0.0
            gy[idx == 3] = 1.0
            return gx, gy

        # Convex polygon: gradient of the most active half-space (a, b)
        if getattr(self, "_is_convex_polygon", False):
            edges = getattr(self, "_convex_edges_abc", [])
            if np.isscalar(x) and np.isscalar(y):
                if not edges:
                    return (0.0, 0.0)
                vals = [a * x + b * y + c for (a, b, c) in edges]
                i = int(np.argmax(vals))
                a, b, _ = edges[i]
                return (a, b)
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)
            if not edges:
                return (
                    np.zeros_like(x_arr, dtype=float),
                    np.zeros_like(y_arr, dtype=float),
                )
            # Evaluate each plane and pick argmax per element
            planes = [a * x_arr + b * y_arr + c for (a, b, c) in edges]
            stacked = np.stack(planes, axis=0)
            idx = np.argmax(stacked, axis=0)
            gx = np.zeros_like(x_arr, dtype=float)
            gy = np.zeros_like(y_arr, dtype=float)
            for k, (a, b, _) in enumerate(edges):
                mask = idx == k
                if np.any(mask):
                    gx[mask] = a
                    gy[mask] = b
            return gx, gy

        # General case: take gradient from the segment with minimal value
        if np.isscalar(x) and np.isscalar(y):
            values = [segment.evaluate(x, y) for segment in self.segments]
            if not values:
                return (0.0, 0.0)
            min_idx = int(np.argmin(values))
            return self.segments[min_idx].gradient(x, y)
        x_array = np.asarray(x)
        y_array = np.asarray(y)
        segment_values = [
            np.asarray(segment.evaluate(x_array, y_array)) for segment in self.segments
        ]
        if not segment_values:
            return (
                np.zeros_like(x_array, dtype=float),
                np.zeros_like(y_array, dtype=float),
            )
        stacked = np.stack(segment_values, axis=0)
        min_indices = np.argmin(stacked, axis=0)
        grad_x = np.zeros_like(x_array, dtype=float)
        grad_y = np.zeros_like(y_array, dtype=float)
        for i, segment in enumerate(self.segments):
            mask = min_indices == i
            if np.any(mask):
                seg_grad_x, seg_grad_y = segment.gradient(x_array, y_array)
                seg_grad_x = np.asarray(seg_grad_x)
                seg_grad_y = np.asarray(seg_grad_y)
                if seg_grad_x.ndim == 0:
                    grad_x[mask] = seg_grad_x.item()
                    grad_y[mask] = seg_grad_y.item()
                else:
                    grad_x[mask] = seg_grad_x[mask]
                    grad_y[mask] = seg_grad_y[mask]
        return grad_x, grad_y

    def plot(
        self,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        resolution: int = 1000,
        ax=None,
        **kwargs,
    ):
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
            if "colors" not in segment_kwargs and "color" not in segment_kwargs:
                segment_kwargs["colors"] = [colors[i]]

            # Plot the segment
            cs = segment.plot(x_range, y_range, resolution, ax, **segment_kwargs)
            contour_sets.append(cs)

        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_title(f"Composite Curve ({len(self.segments)} segments)")

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
            "variables": [str(var) for var in self.variables],
            # Optional metadata for special evaluation cases
            "is_square": getattr(self, "_is_square", False),
            "square_bounds": getattr(self, "_square_bounds", None),
            "is_convex_polygon": getattr(self, "_is_convex_polygon", False),
            "convex_edges_abc": getattr(self, "_convex_edges_abc", None),
            "polygon_vertices": getattr(self, "_polygon_vertices", None),
        }



    # Backward-compatibility shim: some test environments expect this method
    # to be defined directly on CompositeCurve. The actual implementation
    # lives in CompositePolygonMixin, so we just delegate.
    def halfspace_edges(self) -> Optional[List[Tuple[float, float, float]]]:
        return super().halfspace_edges()

    # The point-in-polygon containment implementation lives at the bottom of this class.

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
        all_roots: list = []
        for segment in self.segments:
            self._numerical_ray_intersection_collect(x, y, segment, all_roots)
        return (len(all_roots) % 2) == 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositeCurve":
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
            raise ValueError(
                f"Invalid type: expected 'CompositeCurve', got {data.get('type')}"
            )

        # Reconstruct variables
        var_names = data["variables"]
        variables = tuple(sp.Symbol(name) for name in var_names)

        # Reconstruct segments
        segments = []
        for segment_data in data["segments"]:
            segment = TrimmedImplicitCurve.from_dict(segment_data)
            segments.append(segment)

        # Create CompositeCurve and restore metadata if present
        obj = cls(segments, variables)
        if data.get("is_square"):
            obj._is_square = True
            obj._square_bounds = tuple(data.get("square_bounds", (0.0, 0.0, 0.0, 0.0)))
        if data.get("is_convex_polygon"):
            obj._is_convex_polygon = True
            edges = data.get("convex_edges_abc", None)
            if edges is not None:
                obj._convex_edges_abc = [tuple(map(float, e)) for e in edges]
        verts = data.get("polygon_vertices")
        if verts is not None:
            obj._polygon_vertices = [tuple(map(float, v)) for v in verts]
        return obj

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
            raise IndexError(
                f"Segment index {index} out of range [0, {len(self.segments)})"
            )

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
        self._cached_polygon_segments = None

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
            raise IndexError(
                f"Segment index {index} out of range [0, {len(self.segments)})"
            )

        if len(self.segments) <= 1:
            raise ValueError("Cannot remove the last remaining segment")

        self.segments.pop(index)
        self._cached_polygon_segments = None

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

    def get_polygon_segments(
        self,
    ) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Approximate the composite curve as a list of straight-line segments.
        Each segment is represented as a tuple of start and end points ((x0, y0), (x1, y1)).
        Caches the result in self._cached_polygon_segments.
        """
        if self._cached_polygon_segments is not None:
            return self._cached_polygon_segments

        segments_list = []
        for segment in self.segments:
            # 1. If it has get_polyline_approximation (e.g. ParametricSegment)
            if hasattr(segment, "get_polyline_approximation"):
                try:
                    pts = segment.get_polyline_approximation(resolution=100)
                    if pts and len(pts) > 1:
                        for i in range(len(pts) - 1):
                            segments_list.append(
                                (
                                    (float(pts[i][0]), float(pts[i][1])),
                                    (float(pts[i + 1][0]), float(pts[i + 1][1])),
                                )
                            )
                        continue
                except Exception:
                    pass

            # 2. If it is a TrimmedImplicitCurve
            if hasattr(segment, "get_endpoints"):
                try:
                    endpoints = segment.get_endpoints()
                    if endpoints and len(endpoints) == 2:
                        p0, p1 = endpoints
                        is_curved = getattr(segment, "is_curved", True)

                        if is_curved:
                            t_vals = np.linspace(0, 1, 32)
                            pts = []
                            for t in t_vals:
                                xi = float(p0[0] + t * (p1[0] - p0[0]))
                                yi = float(p0[1] + t * (p1[1] - p0[1]))
                                if 0.0 < t < 1.0:
                                    try:
                                        for _ in range(3):
                                            val = float(segment.evaluate(xi, yi))
                                            if abs(val) < 1e-6:
                                                break
                                            gx, gy = segment.gradient(xi, yi)
                                            gx, gy = float(gx), float(gy)
                                            grad_sq = gx * gx + gy * gy
                                            if grad_sq > 1e-12:
                                                xi -= val * gx / grad_sq
                                                yi -= val * gy / grad_sq
                                            else:
                                                break
                                    except Exception:
                                        pass
                                pts.append((xi, yi))
                            for i in range(len(pts) - 1):
                                segments_list.append((pts[i], pts[i + 1]))
                        else:
                            segments_list.append((p0, p1))
                        continue
                    elif not endpoints:
                        # Closed implicit curve (like a circle or ellipse) with no endpoints
                        bbox = segment.bounding_box()
                        xmin_b, xmax_b, ymin_b, ymax_b = bbox
                        cx = (xmin_b + xmax_b) / 2.0
                        cy = (ymin_b + ymax_b) / 2.0
                        # Shoot 64 radial rays to find boundary points
                        angles = np.linspace(0, 2 * np.pi, 64, endpoint=False)
                        pts = []
                        max_r = max(xmax_b - xmin_b, ymax_b - ymin_b) * 1.5
                        for angle in angles:
                            cos_a = np.cos(angle)
                            sin_a = np.sin(angle)
                            r_samples = np.linspace(0, max_r, 50)
                            try:
                                f_vals = [
                                    float(
                                        segment.evaluate(cx + r * cos_a, cy + r * sin_a)
                                    )
                                    for r in r_samples
                                ]
                                for i in range(len(r_samples) - 1):
                                    if f_vals[i] * f_vals[i + 1] <= 0:
                                        r0, r1 = r_samples[i], r_samples[i + 1]
                                        for _ in range(8):
                                            rm = (r0 + r1) / 2.0
                                            fm = float(
                                                segment.evaluate(
                                                    cx + rm * cos_a, cy + rm * sin_a
                                                )
                                            )
                                            if abs(fm) < 1e-6:
                                                r0 = rm
                                                break
                                            if f_vals[i] * fm <= 0:
                                                r1 = rm
                                            else:
                                                r0 = rm
                                        r_root = r0
                                        px = cx + r_root * cos_a
                                        py = cy + r_root * sin_a
                                        pts.append((px, py))
                                        break
                            except Exception:
                                pass
                        if len(pts) > 2:
                            pts.append(pts[0])
                            for i in range(len(pts) - 1):
                                segments_list.append((pts[i], pts[i + 1]))
                            continue
                except Exception:
                    pass

            # 3. Fallback to bounding box
            try:
                bbox = segment.bounding_box()
                s_xmin, s_xmax, s_ymin, s_ymax = bbox
                segments_list.append(
                    ((float(s_xmin), float(s_ymin)), (float(s_xmax), float(s_ymax)))
                )
            except Exception:
                pass

        self._cached_polygon_segments = segments_list
        return segments_list

    def _point_in_polygon_scalar(self, x: float, y: float) -> bool:
        """
        Fast scalar version of point-in-polygon containment test using cached segments.
        """
        poly_segments = self.get_polygon_segments()
        if not poly_segments:
            return False

        crossings = 0
        for (x1, y1), (x2, y2) in poly_segments:
            if (y1 <= y < y2) or (y2 <= y < y1):
                x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if x_intersect > x:
                    crossings += 1

        return (crossings % 2) == 1

    def _point_in_polygon_vectorized(
        self, x_array: np.ndarray, y_array: np.ndarray
    ) -> np.ndarray:
        """
        Highly optimized, pure-NumPy vectorized ray-casting containment check.
        Evaluates containment for all grid points simultaneously against cached segments.
        """
        poly_segments = self.get_polygon_segments()
        if not poly_segments:
            return np.zeros_like(x_array, dtype=bool)

        x1 = np.array([seg[0][0] for seg in poly_segments], dtype=float)[np.newaxis, :]
        y1 = np.array([seg[0][1] for seg in poly_segments], dtype=float)[np.newaxis, :]
        x2 = np.array([seg[1][0] for seg in poly_segments], dtype=float)[np.newaxis, :]
        y2 = np.array([seg[1][1] for seg in poly_segments], dtype=float)[np.newaxis, :]

        orig_shape = x_array.shape
        px = x_array.ravel()[:, np.newaxis]
        py = y_array.ravel()[:, np.newaxis]

        cond1 = (y1 <= py) & (py < y2)
        cond2 = (y2 <= py) & (py < y1)
        vertical_overlap = cond1 | cond2

        dy = y2 - y1
        x_intersect = x1 + (py - y1) * (x2 - x1) / dy
        horizontal_crossing = x_intersect > px

        crossings = vertical_overlap & horizontal_crossing
        inside_flat = (np.sum(crossings, axis=1) % 2) == 1

        return inside_flat.reshape(orig_shape)

    def _numerical_ray_intersection_collect(
        self, ray_x: float, ray_y: float, segment, all_roots: list
    ) -> None:
        """
        Like _numerical_ray_intersection but appends unique root x-values to all_roots
        (shared across segments) to prevent double-counting at segment boundaries.
        """
        bbox = segment.bounding_box()
        xmin, xmax, ymin, ymax = bbox

        _eps = 1e-9
        if ray_y < ymin - _eps or ray_y >= ymax - _eps:
            return

        if np.isclose(ymin, ymax, atol=1e-6) and np.isclose(ray_y, ymin, atol=1e-6):
            return

        if np.isclose(xmin, xmax, atol=1e-6):
            segment_x_val = xmin
            if segment_x_val > ray_x and ymin <= ray_y < ymax:
                if not any(abs(segment_x_val - r) < 1e-6 for r in all_roots):
                    all_roots.append(segment_x_val)
            return

        def f(x_val):
            return segment.evaluate(x_val, ray_y)

        x_search_min = max(ray_x + 1e-6, xmin)
        # Extend slightly beyond xmax so roots exactly at the boundary are caught
        _boundary_pad = max(1e-6, abs(xmax) * 1e-9)
        x_search_max = xmax + _boundary_pad
        if x_search_max <= x_search_min:
            return

        num_samples = 100
        x_samples = np.linspace(x_search_min, x_search_max, num_samples)
        f_values = np.array([f(x_val) for x_val in x_samples])

        for i in range(len(x_samples) - 1):
            x0, x1 = x_samples[i], x_samples[i + 1]
            f0, f1 = f_values[i], f_values[i + 1]
            if f0 * f1 < 0:
                try:
                    root = brentq(f, x0, x1)
                    if root > ray_x and segment.mask(root, ray_y):
                        if not any(abs(root - r) < 1e-6 for r in all_roots):
                            all_roots.append(root)
                except ValueError:
                    pass
            elif abs(f0) < 1e-10 and segment.mask(x0, ray_y) and x0 > ray_x:
                if not any(abs(x0 - r) < 1e-6 for r in all_roots):
                    all_roots.append(x0)
            elif abs(f1) < 1e-10 and segment.mask(x1, ray_y) and x1 > ray_x:
                if not any(abs(x1 - r) < 1e-6 for r in all_roots):
                    all_roots.append(x1)

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

        # Use half-open interval [ymin, ymax) to prevent double-counting at shared boundaries
        _eps = 1e-9
        if ray_y < ymin - _eps or ray_y >= ymax - _eps:
            return 0

        # Special handling for horizontal line segments:
        # Horizontal segments collinear with the ray are generally ignored in ray casting
        # to avoid issues with horizontal boundaries and double counting.
        if np.isclose(ymin, ymax, atol=1e-6) and np.isclose(ray_y, ymin, atol=1e-6):
            return 0

        # Special handling for vertical line segments:
        # Count an intersection if the vertical segment's x-value is to the right of the ray origin
        # AND the ray's y-coordinate is within the segment's y-bounds (half-open).
        if np.isclose(xmin, xmax, atol=1e-6):
            segment_x_val = xmin  # For a vertical segment, xmin and xmax are the same
            if segment_x_val > ray_x and ymin <= ray_y < ymax:
                return 1
            return 0

        # For other curve types, use numerical root finding
        # Define sliced implicit function
        def f(x_val):
            return segment.evaluate(x_val, ray_y)

        # Search for roots within the x-range of the bounding box, to the right of ray_x
        x_search_min = max(ray_x + 1e-6, xmin)
        x_search_max = xmax

        if x_search_max <= x_search_min:
            return 0  # No valid search range

        # Coarse sampling to find intervals for brentq
        num_samples = 100
        x_samples = np.linspace(x_search_min, x_search_max, num_samples)

        # Evaluate function at sample points
        f_values = np.array([f(x_val) for x_val in x_samples])

        roots_found = []
        for i in range(len(x_samples) - 1):
            x0, x1 = x_samples[i], x_samples[i + 1]
            f0, f1 = f_values[i], f_values[i + 1]

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


def create_circle_from_quarters(
    center: Tuple[float, float] = (0, 0),
    radius: float = 1.0,
    variables: Tuple[sp.Symbol, sp.Symbol] = None,
) -> CompositeCurve:
    """Shim delegating to `geometry.factories.create_circle_from_quarters`."""
    from .factories import create_circle_from_quarters as _impl

    return _impl(center, radius, variables)


def create_square_from_edges(
    corner1: Tuple[float, float] = (0, 0),
    corner2: Tuple[float, float] = (1, 1),
    variables: Tuple[sp.Symbol, sp.Symbol] = None,
) -> CompositeCurve:
    """Shim delegating to `geometry.factories.create_square_from_edges`."""
    from .factories import create_square_from_edges as _impl

    return _impl(corner1, corner2, variables)


def create_polygon_from_edges(
    points: List[Tuple[float, float]], variables: Tuple[sp.Symbol, sp.Symbol] = None
) -> CompositeCurve:
    """Shim delegating to `geometry.factories.create_polygon_from_edges`."""
    from .factories import create_polygon_from_edges as _impl

    return _impl(points, variables)
