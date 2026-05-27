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
from typing import Tuple, Union, Any, Callable, List, Optional

from .implicit_curve import ImplicitCurve
from .precision import PrecisionPolicy, get_precision_policy


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

    def __init__(
        self,
        base_curve: ImplicitCurve,
        mask: Callable[[float, float], bool],
        variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        endpoints: Optional[List[Tuple[float, float]]] = None,
        precision_policy: Optional[PrecisionPolicy] = None,
    ):
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

        # Precision
        if precision_policy is not None:
            policy = precision_policy
        elif hasattr(base_curve, "precision_policy"):
            try:
                policy = base_curve.precision_policy()
            except AttributeError:
                policy = None
        else:
            policy = None
        self._segment_policy = policy or get_precision_policy()

        # Use variables from base curve if not specified
        if variables is None:
            variables = base_curve.variables

        # Initialize parent class with base curve's expression
        # Note: The expression is inherited but trimming affects contains(), not evaluate()
        # Handle cases where base_curve.expression is None (e.g., ProceduralCurve)
        if base_curve.expression is not None:
            super().__init__(
                base_curve.expression, variables, precision_policy=self._segment_policy
            )
        else:
            # Create a placeholder expression for curves without symbolic expressions
            x, y = variables
            placeholder_expr = x + y  # Simple placeholder
            super().__init__(
                placeholder_expr, variables, precision_policy=self._segment_policy
            )
            # Override the expression to match the base curve
            self.expression = base_curve.expression

    def contains(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
    ) -> Union[bool, np.ndarray]:
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
        tol = self._resolve_tolerance(tolerance)
        curve_values = self.base_curve.evaluate(x, y)
        on_curve = np.abs(curve_values) <= tol

        # Check mask condition
        if np.isscalar(x) and np.isscalar(y):
            # Scalar case
            mask_satisfied = self.mask(x, y)
            in_rect = True
            if (
                self._xmin is not None
                and self._xmax is not None
                and self._ymin is not None
                and self._ymax is not None
            ):
                eps = max(tol * 0.1, 1e-12)
                in_rect = (
                    (x >= (self._xmin - eps))
                    and (x <= (self._xmax + eps))
                    and (y >= (self._ymin - eps))
                    and (y <= (self._ymax + eps))
                )
            return bool(on_curve and mask_satisfied and in_rect)
        else:
            # Vectorized case
            x_array = np.asarray(x)
            y_array = np.asarray(y)

            # Fast-path: rectangular bounds explicitly provided
            if (
                self._xmin is not None
                and self._xmax is not None
                and self._ymin is not None
                and self._ymax is not None
            ):
                eps = max(tol * 0.1, 1e-12)
                in_rect = (
                    (x_array >= (self._xmin - eps))
                    & (x_array <= (self._xmax + eps))
                    & (y_array >= (self._ymin - eps))
                    & (y_array <= (self._ymax + eps))
                )
                candidates = on_curve & in_rect
                mask_vals = np.zeros_like(candidates, dtype=bool)
                if np.any(candidates):
                    flat_cand = candidates.ravel()
                    flat_x = x_array.ravel()
                    flat_y = y_array.ravel()
                    flat_mask = np.zeros_like(flat_cand, dtype=bool)
                    for i in np.where(flat_cand)[0]:
                        try:
                            flat_mask[i] = bool(
                                self.mask(float(flat_x[i]), float(flat_y[i]))
                            )
                        except Exception:
                            pass
                    mask_vals = flat_mask.reshape(candidates.shape)
                return candidates & mask_vals

            # General fallback: evaluate mask only on candidates where on_curve is True
            mask_results = np.zeros_like(on_curve, dtype=bool)
            if np.any(on_curve):
                flat_on = on_curve.ravel()
                flat_x = x_array.ravel()
                flat_y = y_array.ravel()
                flat_mask = np.zeros_like(flat_on, dtype=bool)
                for i in np.where(flat_on)[0]:
                    try:
                        flat_mask[i] = bool(
                            self.mask(float(flat_x[i]), float(flat_y[i]))
                        )
                    except Exception:
                        pass
                mask_results = flat_mask.reshape(on_curve.shape)
            return on_curve & mask_results

    def on_curve(
        self,
        x: Union[float, np.ndarray],
        y: Union[float, np.ndarray],
        tolerance: float = 1e-3,
    ) -> Union[bool, np.ndarray]:
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

    @property
    def is_curved(self) -> bool:
        """Return True if the base curve is curved."""
        if hasattr(self, "base_curve") and self.base_curve is not None:
            return getattr(self.base_curve, "is_curved", True)
        return True

    def get_endpoints(
        self, xmin: Optional[float] = None, xmax: Optional[float] = None
    ) -> List[Tuple[float, float]]:
        """
        Get the endpoints of the trimmed curve segment.

        Args:
            xmin: Optional lower limit to find crossings.
            xmax: Optional upper limit to find crossings.

        Returns:
            List of (x, y) tuples representing the endpoints of the curve segment.
            Returns empty list if no endpoints were explicitly provided.
        """
        if self.endpoints:
            return self.endpoints.copy()
        if hasattr(self.base_curve, "get_endpoints"):
            try:
                try:
                    return self.base_curve.get_endpoints(xmin=xmin, xmax=xmax)
                except TypeError:
                    return self.base_curve.get_endpoints()
            except Exception:
                pass
        return []

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
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

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
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

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return bounding box using explicit bounds if available, else derive from endpoints or base."""
        if (
            self._xmin is not None
            and self._xmax is not None
            and self._ymin is not None
            and self._ymax is not None
        ):
            return (self._xmin, self._xmax, self._ymin, self._ymax)
        if self.endpoints and len(self.endpoints) >= 2:
            xs = [p[0] for p in self.endpoints]
            ys = [p[1] for p in self.endpoints]
            return (min(xs), max(xs), min(ys), max(ys))
        return self.base_curve.bounding_box()

    def to_dict(self) -> dict:
        """
        Serialize TrimmedImplicitCurve to a dictionary.

        Note: The mask function cannot be serialized. The reconstructed curve
        will use a pass-through mask (accepts all points on the base curve).
        """
        d = {
            "type": "TrimmedImplicitCurve",
            "base_curve": self.base_curve.to_dict(),
            "variables": [str(var) for var in self.variables],
            "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
            "mask_description": (
                "Mask function cannot be serialized. "
                "Manual reconstruction required to restore original mask behavior."
            ),
        }
        if self._xmin is not None:
            d["xmin"] = self._xmin
        if self._xmax is not None:
            d["xmax"] = self._xmax
        if self._ymin is not None:
            d["ymin"] = self._ymin
        if self._ymax is not None:
            d["ymax"] = self._ymax
        if self.endpoints:
            d["endpoints"] = [list(ep) for ep in self.endpoints]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "TrimmedImplicitCurve":
        """
        Reconstruct TrimmedImplicitCurve from a dictionary.

        The mask is not serializable; the reconstructed curve uses a
        pass-through mask (all points on the base curve are accepted).
        Bounding-box bounds are used to approximate the original mask
        when they were stored.
        """
        from .implicit_curve import ImplicitCurve

        if data.get("type") != "TrimmedImplicitCurve":
            raise ValueError(
                f"Invalid type: expected 'TrimmedImplicitCurve', got {data.get('type')}"
            )
        base_curve = ImplicitCurve.from_dict(data["base_curve"])
        xmin = data.get("xmin")
        xmax = data.get("xmax")
        ymin = data.get("ymin")
        ymax = data.get("ymax")

        if (
            xmin is not None
            and xmax is not None
            and ymin is not None
            and ymax is not None
        ):
            def mask(px, py, _xmin=xmin, _xmax=xmax, _ymin=ymin, _ymax=ymax):
                return _xmin <= px <= _xmax and _ymin <= py <= _ymax
        else:
            def mask(px, py):
                return True

        endpoints_raw = data.get("endpoints")
        endpoints = [tuple(ep) for ep in endpoints_raw] if endpoints_raw else None

        var_names = data.get("variables")
        variables = tuple(sp.Symbol(v) for v in var_names) if var_names else None

        obj = cls(
            base_curve=base_curve,
            mask=mask,
            variables=variables,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            endpoints=endpoints,
        )
        obj._deserialization_warning = (
            "Mask function was not serialized. A placeholder pass-through mask is used."
        )
        return obj

    @classmethod
    def from_anchors(
        cls,
        base_curve: ImplicitCurve,
        start_anchor: Union[Tuple[float, float], Any],
        end_anchor: Union[Tuple[float, float], Any],
        positive_half_plane: Optional[bool] = None,
        tolerance: float = 1e-5,
        **kwargs: Any,
    ) -> "TrimmedImplicitCurve":
        """
        Create a TrimmedImplicitCurve representing the segment between two anchors.

        Args:
            base_curve: The underlying ImplicitCurve to be trimmed.
            start_anchor: The starting anchor, either a coordinate tuple/list or an Anchor object.
            end_anchor: The ending anchor, either a coordinate tuple/list or an Anchor object.
            positive_half_plane: Optional bool. If True, only includes points where the cross product
                                 (P - P1) x (P2 - P1) >= -tolerance. If False, only <= tolerance.
                                 If None, does not restrict by half-plane.
            tolerance: Tolerance for boundary checks.
            **kwargs: Additional arguments passed to TrimmedImplicitCurve constructor.
        """
        # Retrieve coordinates from either a tuple/list or an object with a coords attribute
        p1 = start_anchor.coords if hasattr(start_anchor, "coords") else start_anchor
        p2 = end_anchor.coords if hasattr(end_anchor, "coords") else end_anchor

        if not isinstance(p1, (tuple, list)) or len(p1) < 2:
            raise TypeError(
                "start_anchor must be a coordinate pair or have a coords attribute"
            )
        if not isinstance(p2, (tuple, list)) or len(p2) < 2:
            raise TypeError(
                "end_anchor must be a coordinate pair or have a coords attribute"
            )

        x1, y1 = float(p1[0]), float(p1[1])
        x2, y2 = float(p2[0]), float(p2[1])

        dx = x2 - x1
        dy = y2 - y1
        lensq = dx * dx + dy * dy

        if lensq < 1e-14:
            # Degenerate case: start and end are the same point
            def mask(px, py):
                return abs(px - x1) < tolerance and abs(py - y1) < tolerance
        else:

            def mask(px: float, py: float) -> bool:
                ux = px - x1
                uy = py - y1
                # Projection parameter t along the chord direction
                t = (ux * dx + uy * dy) / lensq
                if not (0.0 - tolerance <= t <= 1.0 + tolerance):
                    return False
                if positive_half_plane is not None:
                    # Cross product (P - P1) x (P2 - P1)
                    cross = ux * dy - uy * dx
                    if positive_half_plane:
                        if cross < -tolerance:
                            return False
                    else:
                        if cross > tolerance:
                            return False
                return True

        endpoints = [(x1, y1), (x2, y2)]

        return cls(base_curve=base_curve, mask=mask, endpoints=endpoints, **kwargs)

    def get_polyline_approximation(
        self,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: int = 100,
    ) -> List[Tuple[float, float]]:
        """
        Approximate the trimmed curve segment as a sequence of points.

        Args:
            resolution: The desired number of points along the segment.

        Returns:
            List of (x, y) coordinate tuples along the trimmed segment.
        """
        # 1. Try to use endpoints if available
        endpoints = self.get_endpoints()
        if endpoints and len(endpoints) == 2:
            p0, p1 = endpoints
            if hasattr(self, "base_curve") and self.base_curve is not None:
                from .conic_section import ConicSection

                if isinstance(self.base_curve, ConicSection):
                    try:
                        conic_type = self.base_curve.conic_type()
                        if conic_type in ("circle", "ellipse"):
                            coeffs = self.base_curve._extract_coefficients()
                            A, B, C, D, E, F = (
                                coeffs["A"],
                                coeffs["B"],
                                coeffs["C"],
                                coeffs["D"],
                                coeffs["E"],
                                coeffs["F"],
                            )

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
                                if constant > 0:
                                    trace = A + C
                                    det_matrix = A * C - (B / 2) ** 2
                                    disc = trace**2 - 4 * det_matrix
                                    if disc >= 0:
                                        lambda1 = (trace + np.sqrt(disc)) / 2
                                        lambda2 = (trace - np.sqrt(disc)) / 2
                                        if lambda1 > 0 and lambda2 > 0:
                                            a = np.sqrt(constant / lambda1)
                                            b = np.sqrt(constant / lambda2)

                                            theta = (
                                                0.5 * np.arctan2(B, A - C)
                                                if abs(B) > 1e-12
                                                else 0.0
                                            )
                                            cos_t = np.cos(theta)
                                            sin_t = np.sin(theta)

                                            # Determine axes swapping by evaluating canonical vs swapped points directly
                                            x_test_no_swap = center_x + a * cos_t
                                            y_test_no_swap = center_y + a * sin_t
                                            val_no_swap = abs(
                                                float(
                                                    self.evaluate(
                                                        x_test_no_swap, y_test_no_swap
                                                    )
                                                )
                                            )

                                            x_test_swap = center_x + b * cos_t
                                            y_test_swap = center_y + b * sin_t
                                            val_swap = abs(
                                                float(
                                                    self.evaluate(
                                                        x_test_swap, y_test_swap
                                                    )
                                                )
                                            )

                                            swap_axes = val_swap < val_no_swap

                                            a_eff = b if swap_axes else a
                                            b_eff = a if swap_axes else b

                                            # Project endpoints to get phi_0 and phi_1
                                            def get_phi(pt):
                                                px, py = pt
                                                xi = (px - center_x) * cos_t + (
                                                    py - center_y
                                                ) * sin_t
                                                eta = (
                                                    -(px - center_x) * sin_t
                                                    + (py - center_y) * cos_t
                                                )
                                                cos_phi = xi / max(a_eff, 1e-15)
                                                sin_phi = eta / max(b_eff, 1e-15)
                                                return np.arctan2(sin_phi, cos_phi)

                                            phi0 = get_phi(p0)
                                            phi1 = get_phi(p1)

                                            # 1. CCW path
                                            phi1_ccw = (
                                                phi1
                                                if phi1 >= phi0
                                                else phi1 + 2 * np.pi
                                            )
                                            phi_mid_ccw = (phi0 + phi1_ccw) / 2.0
                                            xi_mid_ccw = a_eff * np.cos(phi_mid_ccw)
                                            eta_mid_ccw = b_eff * np.sin(phi_mid_ccw)
                                            x_mid_ccw = (
                                                center_x
                                                + xi_mid_ccw * cos_t
                                                - eta_mid_ccw * sin_t
                                            )
                                            y_mid_ccw = (
                                                center_y
                                                + xi_mid_ccw * sin_t
                                                + eta_mid_ccw * cos_t
                                            )
                                            ccw_ok = self.mask(x_mid_ccw, y_mid_ccw)

                                            # 2. CW path
                                            phi1_cw = (
                                                phi1
                                                if phi1 <= phi0
                                                else phi1 - 2 * np.pi
                                            )
                                            phi_mid_cw = (phi0 + phi1_cw) / 2.0
                                            xi_mid_cw = a_eff * np.cos(phi_mid_cw)
                                            eta_mid_cw = b_eff * np.sin(phi_mid_cw)
                                            x_mid_cw = (
                                                center_x
                                                + xi_mid_cw * cos_t
                                                - eta_mid_cw * sin_t
                                            )
                                            y_mid_cw = (
                                                center_y
                                                + xi_mid_cw * sin_t
                                                + eta_mid_cw * cos_t
                                            )
                                            cw_ok = self.mask(x_mid_cw, y_mid_cw)

                                            # Choose best direction
                                            if ccw_ok and not cw_ok:
                                                phi_start, phi_end = phi0, phi1_ccw
                                            elif cw_ok and not ccw_ok:
                                                phi_start, phi_end = phi0, phi1_cw
                                            else:
                                                dist_ccw = abs(phi1_ccw - phi0)
                                                dist_cw = abs(phi1_cw - phi0)
                                                if dist_ccw <= dist_cw:
                                                    phi_start, phi_end = phi0, phi1_ccw
                                                else:
                                                    phi_start, phi_end = phi0, phi1_cw

                                            phi_vals = np.linspace(
                                                phi_start, phi_end, resolution
                                            )
                                            pts = []
                                            for phi in phi_vals:
                                                xc = a_eff * np.cos(phi)
                                                yc = b_eff * np.sin(phi)
                                                px = center_x + xc * cos_t - yc * sin_t
                                                py = center_y + xc * sin_t + yc * cos_t
                                                pts.append((float(px), float(py)))

                                            if len(pts) > 1:
                                                pts[0] = (float(p0[0]), float(p0[1]))
                                                pts[-1] = (float(p1[0]), float(p1[1]))
                                                return pts
                    except Exception:
                        pass

        if endpoints and len(endpoints) == 2:
            p0, p1 = endpoints
            is_curved = getattr(self, "is_curved", True)

            if is_curved:
                t_vals = np.linspace(0, 1, resolution)
                pts = []
                for t in t_vals:
                    xi = float(p0[0] + t * (p1[0] - p0[0]))
                    yi = float(p0[1] + t * (p1[1] - p0[1]))
                    if 0.0 < t < 1.0:
                        try:
                            # Apply up to 5 steps of Newton-Raphson to pull onto the curve
                            for _ in range(5):
                                val = float(self.evaluate(xi, yi))
                                if abs(val) < 1e-6:
                                    break
                                gx, gy = self.gradient(xi, yi)
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
                if len(pts) > 1:
                    return pts
            else:
                # Linear segment
                t_vals = np.linspace(0, 1, resolution)
                pts = []
                for t in t_vals:
                    xi = float(p0[0] + t * (p1[0] - p0[0]))
                    yi = float(p0[1] + t * (p1[1] - p0[1]))
                    pts.append((xi, yi))
                if len(pts) > 1:
                    return pts

        # 2. Check if it's an ellipse or circle (degree-2 conics with no/empty endpoints)
        if hasattr(self, "base_curve") and self.base_curve is not None:
            # Import to avoid circular dependencies
            from .conic_section import ConicSection

            if isinstance(self.base_curve, ConicSection):
                try:
                    conic_type = self.base_curve.conic_type()
                    if conic_type in ("circle", "ellipse"):
                        coeffs = self.base_curve._extract_coefficients()
                        A, B, C, D, E, F = (
                            coeffs["A"],
                            coeffs["B"],
                            coeffs["C"],
                            coeffs["D"],
                            coeffs["E"],
                            coeffs["F"],
                        )

                        # Find the center
                        det = 4 * A * C - B**2
                        if abs(det) > 1e-12:
                            center_x = (B * E - 2 * C * D) / det
                            center_y = (B * D - 2 * A * E) / det

                            # Complete constant term at center
                            constant = (
                                A * center_x**2
                                + B * center_x * center_y
                                + C * center_y**2
                                - F
                            )
                            if constant > 0:
                                # Find eigenvalues of [[A, B/2], [B/2, C]]
                                trace = A + C
                                det_matrix = A * C - (B / 2) ** 2
                                disc = trace**2 - 4 * det_matrix
                                if disc >= 0:
                                    lambda1 = (trace + np.sqrt(disc)) / 2
                                    lambda2 = (trace - np.sqrt(disc)) / 2
                                    if lambda1 > 0 and lambda2 > 0:
                                        a = np.sqrt(constant / lambda1)
                                        b = np.sqrt(constant / lambda2)

                                        # Angle of rotation
                                        theta = (
                                            0.5 * np.arctan2(B, A - C)
                                            if abs(B) > 1e-12
                                            else 0.0
                                        )

                                        # Sample points along the ellipse boundary
                                        phi_vals = np.linspace(
                                            0, 2 * np.pi, max(360, resolution * 4)
                                        )
                                        candidate_pts = []

                                        cos_t = np.cos(theta)
                                        sin_t = np.sin(theta)

                                        # Determine axes swapping by evaluating canonical vs swapped points directly
                                        x_test_no_swap = center_x + a * cos_t
                                        y_test_no_swap = center_y + a * sin_t
                                        val_no_swap = abs(
                                            float(
                                                self.evaluate(
                                                    x_test_no_swap, y_test_no_swap
                                                )
                                            )
                                        )

                                        x_test_swap = center_x + b * cos_t
                                        y_test_swap = center_y + b * sin_t
                                        val_swap = abs(
                                            float(
                                                self.evaluate(x_test_swap, y_test_swap)
                                            )
                                        )

                                        swap_axes = val_swap < val_no_swap

                                        for phi in phi_vals:
                                            cp = np.cos(phi)
                                            sp = np.sin(phi)
                                            if not swap_axes:
                                                xc = a * cp
                                                yc = b * sp
                                            else:
                                                xc = b * cp
                                                yc = a * sp

                                            px = center_x + xc * cos_t - yc * sin_t
                                            py = center_y + xc * sin_t + yc * cos_t

                                            if self.mask(px, py):
                                                candidate_pts.append((px, py))

                                        # If we have valid segments, return them
                                        if len(candidate_pts) > 1:
                                            # Downsample to desired resolution
                                            step = len(candidate_pts) / resolution
                                            downsampled = [
                                                candidate_pts[int(i * step)]
                                                for i in range(resolution)
                                            ]
                                            # If it was closed and wrapped around, ensure it's closed
                                            if (
                                                len(candidate_pts)
                                                >= max(360, resolution * 4) - 5
                                                and abs(
                                                    candidate_pts[0][0]
                                                    - candidate_pts[-1][0]
                                                )
                                                < 1e-3
                                            ):
                                                if downsampled[-1] != downsampled[0]:
                                                    downsampled.append(downsampled[0])
                                            return downsampled
                except Exception:
                    pass

        # 3. Ray casting general fallback
        try:
            bbox = self.bounding_box()
            xmin_b, xmax_b, ymin_b, ymax_b = bbox
            cx = (xmin_b + xmax_b) / 2.0
            cy = (ymin_b + ymax_b) / 2.0
            angles = np.linspace(0, 2 * np.pi, 72, endpoint=False)
            pts = []
            max_r = max(xmax_b - xmin_b, ymax_b - ymin_b) * 1.5
            for angle in angles:
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)
                r_samples = np.linspace(0, max_r, 50)
                try:
                    f_vals = [
                        float(self.evaluate(cx + r * cos_a, cy + r * sin_a))
                        for r in r_samples
                    ]
                    for i in range(len(r_samples) - 1):
                        if f_vals[i] * f_vals[i + 1] <= 0:
                            r0, r1 = r_samples[i], r_samples[i + 1]
                            for _ in range(8):
                                rm = (r0 + r1) / 2.0
                                fm = float(
                                    self.evaluate(cx + rm * cos_a, cy + rm * sin_a)
                                )
                                if abs(fm) < 1e-6:
                                    r0 = rm
                                    break
                                if f_vals[i] * fm <= 0:
                                    r1 = rm
                                else:
                                    r0 = rm
                            px = cx + r0 * cos_a
                            py = cy + r0 * sin_a
                            if self.mask(px, py):
                                pts.append((px, py))
                            break
                except Exception:
                    pass
            if len(pts) > 1:
                # Sort polar-sequentially
                pts.sort(key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))
                return pts
        except Exception:
            pass

        # 4. Ultimate fallback to a simple bounding-box based linear interpolation
        try:
            bbox = self.bounding_box()
            s_xmin, s_xmax, s_ymin, s_ymax = bbox
            t_vals = np.linspace(0, 1, resolution)
            pts = []
            for t in t_vals:
                xi = float(s_xmin + t * (s_xmax - s_xmin))
                yi = float(s_ymin + t * (s_ymax - s_ymin))
                if self.mask(xi, yi):
                    pts.append((xi, yi))
            if len(pts) > 1:
                return pts
        except Exception:
            pass

        return []

    def __str__(self) -> str:
        return f"TrimmedImplicitCurve({self.base_curve})"

    def __repr__(self) -> str:
        return f"TrimmedImplicitCurve(base_curve={self.base_curve!r})"

    def plot(
        self,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        resolution: int = 1000,
        ax=None,
        **kwargs,
    ):
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
        default_kwargs = {"levels": [0], "colors": "blue", "linewidths": 2}
        default_kwargs.update(kwargs)

        cs = ax.contour(X, Y, Z_masked, **default_kwargs)

        # DEBUG: Extract and print the discretized line segments
        print("    Contour discretization results:")
        print(f"    Contour set type: {type(cs)}")

        # Handle different matplotlib versions
        try:
            if hasattr(cs, "collections"):
                collections = cs.collections
            elif hasattr(cs, "allsegs"):
                # Older matplotlib versions
                print("    Using allsegs (older matplotlib)")
                collections = []
                for level_segs in cs.allsegs:
                    for seg in level_segs:
                        print(f"    Segment with {len(seg)} points")
                        if len(seg) > 0:
                            print(
                                f"      First point: ({seg[0][0]:.3f}, {seg[0][1]:.3f})"
                            )
                            print(
                                f"      Last point:  ({seg[-1][0]:.3f}, {seg[-1][1]:.3f})"
                            )
            else:
                print("    Unknown contour set format")
        except Exception as e:
            print(f"    Error extracting contour info: {e}")

        return cs
