"""
Curve intersection utilities - finding discrete intersection points
"""

import numpy as np
from typing import List, Tuple, Optional, Any, Callable
from scipy.optimize import fsolve
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import fcluster, linkage

from .precision import PrecisionPolicy, get_precision_policy


def _is_transcendental_or_procedural(c) -> bool:
    if c is None:
        return False
    if hasattr(c, "base_curve") and c.base_curve is not None:
        c = c.base_curve
    if not hasattr(c, "expression") or c.expression is None:
        return True
    if "Procedural" in type(c).__name__:
        return True
    try:
        import sympy as sp

        expr = c.expression
        if expr.has(
            sp.sin,
            sp.cos,
            sp.tan,
            sp.exp,
            sp.log,
            sp.asin,
            sp.acos,
            sp.atan,
            sp.sinh,
            sp.cosh,
            sp.tanh,
        ):
            return True
    except Exception:
        return True
    return False


def _quadratic_degree(expression, variables):
    """Reject unsupported/high-degree structure before polynomial expansion."""
    import sympy as sp

    if isinstance(expression, (sp.Rational, sp.Float)):
        return 0
    if expression in variables:
        return 1
    if expression.is_Add or expression.is_Mul:
        degrees = [_quadratic_degree(arg, variables) for arg in expression.args]
        if any(degree is None for degree in degrees):
            return None
        degree = max(degrees) if expression.is_Add else sum(degrees)
    elif expression.is_Pow and expression.exp in (0, 1, 2):
        base = _quadratic_degree(expression.base, variables)
        if base is None:
            return None
        degree = base * int(expression.exp)
    else:
        return None
    return degree if degree <= 2 else None


def _native_circle_or_line(curve):
    """Recognize only native kernels for stored rational/Float circle or line fields."""
    import sympy as sp
    from .implicit_curve import ImplicitCurve
    from .trimmed_implicit_curve import TrimmedImplicitCurve

    seen = set()
    while isinstance(curve, TrimmedImplicitCurve):
        if (
            id(curve) in seen
            or getattr(curve.evaluate, "__func__", None)
            is not TrimmedImplicitCurve.evaluate
        ):
            return None
        seen.add(id(curve))
        curve = curve.base_curve
    if (
        not isinstance(curve, ImplicitCurve)
        or getattr(curve.evaluate, "__func__", None) is not ImplicitCurve.evaluate
        or getattr(type(curve), "expression", None) is not ImplicitCurve.expression
        or getattr(type(curve), "variables", None) is not ImplicitCurve.variables
    ):
        return None
    expression, variables = curve.expression, curve.variables
    kernel = curve._eval_func
    if kernel is not None and (
        kernel is not getattr(curve, "_native_eval_func", None)
        or (expression, variables) != getattr(curve, "_native_eval_state", None)
    ):
        return None
    if (
        not isinstance(expression, sp.Expr)
        or sp.count_ops(expression) > 256
        or _quadratic_degree(expression, variables) is None
    ):
        return None
    try:
        exact = expression.xreplace(
            {v: sp.Rational(v) for v in expression.atoms(sp.Float)}
        )
        polynomial = sp.Poly(exact, *variables)
        if polynomial.total_degree() > 2 or any(
            not isinstance(c, sp.Rational) for c in polynomial.coeffs()
        ):
            return None
        coefficients = polynomial.as_dict()
        a, b, c, d, e, f = (
            coefficients.get(power, sp.Integer(0))
            for power in [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]
        )
        if a == b == c == 0 and (d != 0 or e != 0):
            return "line", (d, e, f)
        if a != 0 and a == c and b == 0:
            cx, cy = -d / (2 * a), -e / (2 * a)
            radius_squared = cx * cx + cy * cy - f / a
            if radius_squared > 0:
                return "circle", (cx, cy, radius_squared)
    except (TypeError, ValueError, OverflowError, sp.PolynomialError):
        pass
    return None


def _native_tangent_candidates(curve1, curve2):
    """One isolated exact native contact, [] for coincidence, None for fallback.

    The discriminant is exact for stored coefficients; returned float coordinates
    still need actual residual, final trim, search and limit validation.
    Nonzero discriminants never become contacts through a fuzzy tolerance.
    """
    first, second = _native_circle_or_line(curve1), _native_circle_or_line(curve2)
    if first is None or second is None:
        return None
    if first[0] != "circle":
        first, second = second, first
    if first[0] != "circle":
        return None
    cx, cy, radius_squared = first[1]
    if second[0] == "circle":
        ox, oy, other_radius_squared = second[1]
        if cx == ox and cy == oy:
            return [] if radius_squared == other_radius_squared else None
        # Subtract normalized circle equations to obtain their radical axis.
        d, e = 2 * (cx - ox), 2 * (cy - oy)
        f = (
            ox * ox
            + oy * oy
            - other_radius_squared
            - (cx * cx + cy * cy - radius_squared)
        )
    else:
        d, e, f = second[1]
    normal_squared = d * d + e * e
    offset = d * cx + e * cy + f
    if radius_squared * normal_squared - offset * offset != 0:
        return None
    try:
        point = (
            float(cx - d * offset / normal_squared),
            float(cy - e * offset / normal_squared),
        )
    except (TypeError, ValueError, OverflowError):
        return None
    return [point] if np.isfinite(point).all() else None


def find_curve_intersections(
    curve1,
    curve2,
    search_range: float = 5.0,
    grid_resolution: int = 500,
    tolerance: Optional[float] = None,
    max_points: int = 200,
    detect_overlap: bool = False,
    precision_policy: Optional[PrecisionPolicy] = None,
    registry_callback: Optional[Callable[[float, float, Any, Any], None]] = None,
) -> List[Tuple[float, float]]:
    """
    Find intersection points between two implicit curves.

    Args:
        curve1: First implicit curve
        curve2: Second implicit curve
        search_range: Range to search for intersections (±range)
        grid_resolution: Grid resolution for initial search
        tolerance: Tolerance for considering a point an intersection
        max_points: Maximum number of intersection points to return
        detect_overlap: If True, detect overlapping segments (slower)
        precision_policy: Optional precision policy to use for calculations

    Returns:
        With detect_overlap=False, approximate (x, y) points accepted by residual
        and final trim checks. Legacy overlap detection can return unrefined
        coarse approximations; its original candidate inputs are retained.
        Coarse grid seeds retain a one-cell trim halo; explicit trim endpoints
        also seed refinement. This is not a completeness or exactness guarantee.
    """

    policy = (
        precision_policy
        or getattr(curve1, "precision_policy", lambda: None)()
        or getattr(curve2, "precision_policy", lambda: None)()
        or get_precision_policy()
    )

    is_periodic_or_procedural = _is_transcendental_or_procedural(
        curve1
    ) or _is_transcendental_or_procedural(curve2)

    # Safe scale hint extraction (handles both float attributes and methods)
    sh1 = getattr(curve1, "scale_hint", 1.0)
    sh1_val = sh1() if callable(sh1) else sh1
    sh2 = getattr(curve2, "scale_hint", 1.0)
    sh2_val = sh2() if callable(sh2) else sh2
    max_scale = max(float(sh1_val), float(sh2_val))

    tol = tolerance if tolerance is not None else policy.distance_threshold(max_scale)
    grid_spacing = 2.0 * search_range / grid_resolution
    coarse_tolerance = max(
        0.06 * max_scale,
        2.5 * max_scale * grid_spacing,
        8 * policy.blended_tolerance(search_range),
    )

    def finite_residual(point):
        """Actual finite field values, separate from the solver's failure sentinel."""
        x_val, y_val = point
        try:
            f1 = curve1.evaluate(x_val, y_val)
            f2 = curve2.evaluate(x_val, y_val)
            v1 = float(f1[0]) if isinstance(f1, np.ndarray) else float(f1)
            v2 = float(f2[0]) if isinstance(f2, np.ndarray) else float(f2)
            if not np.isfinite(v1) or not np.isfinite(v2):
                return None
            return [v1, v2]
        except Exception:
            return None

    def intersection_system(point):
        residual = finite_residual(point)
        return residual if residual is not None else [1e6, 1e6]

    def is_valid_intersection(x_val, y_val, tolerance):
        """Check if intersection point is valid for both curves (respects trimming)"""
        # For trimmed curves, check if point satisfies the mask
        if hasattr(curve1, "mask") and hasattr(curve1, "base_curve"):
            # This is a TrimmedImplicitCurve
            if not curve1.contains(x_val, y_val, tolerance):
                return False

        if hasattr(curve2, "mask") and hasattr(curve2, "base_curve"):
            # This is a TrimmedImplicitCurve
            if not curve2.contains(x_val, y_val, tolerance):
                return False

        return True

    def notify(points):
        if registry_callback is not None:
            for x_val, y_val in points:
                try:
                    registry_callback(x_val, y_val, curve1, curve2)
                except Exception as e:
                    print(f"Error in registry callback: {e}")

    native = _native_tangent_candidates(curve1, curve2)
    if native is not None:
        if not native:
            return []  # Coincident native circles have no isolated tangent root.
        point = native[0]
        residual = finite_residual(point)
        if residual is not None and np.linalg.norm(residual) < tol:
            try:
                if (
                    max_points <= 0
                    or abs(point[0]) > search_range + 1e-3
                    or abs(point[1]) > search_range + 1e-3
                    or not is_valid_intersection(point[0], point[1], tol * 10)
                ):
                    return []
            except Exception:
                pass  # Retain the iterative path's handling of callback failures.
            else:
                notify(native)
                return native
        # Floating evaluation can disagree with the symbolic contact: retain the
        # existing solver instead of asserting that a numeric point is valid.

    # Quick check for identical curves
    if _are_curves_identical_fast(curve1, curve2, tol, search_range):
        return []  # Return empty for identical curves

    # Fast AABB overlap check to avoid expensive grid evaluation
    def _get_bbox(c):
        if hasattr(c, "sublevel_bounds"):
            try:
                result = c.sublevel_bounds(0)
                if result.kind == "bounded":
                    return result.box
            except Exception:
                pass
            # Unknown is not a license to use a heuristic display box as an
            # exclusion proof. A complete trim rectangle remains a constraint.
        elif hasattr(c, "bounding_box"):
            try:
                box = c.bounding_box()
                if box and len(box) == 4 and all(np.isfinite(v) for v in box):
                    return box
            except Exception:
                pass
        for candidate in (c, getattr(c, "base_curve", None)):
            box = tuple(
                getattr(candidate, key, None)
                for key in ("_xmin", "_xmax", "_ymin", "_ymax")
            )
            if (
                all(v is not None and np.isfinite(v) for v in box)
                and box[0] <= box[1]
                and box[2] <= box[3]
            ):
                return box
        return None

    bbox1 = _get_bbox(curve1)
    bbox2 = _get_bbox(curve2)
    if bbox1 and bbox2:
        x1_min, x1_max, y1_min, y1_max = bbox1
        x2_min, x2_max, y2_min, y2_max = bbox2
        pad = max(tol * 10, 0.5)
        if (
            x1_max + pad < x2_min
            or x2_max + pad < x1_min
            or y1_max + pad < y2_min
            or y2_max + pad < y1_min
        ):
            return []

    # Step 1: Coarse grid search to find approximate intersections
    x_vals = np.linspace(-search_range, search_range, grid_resolution)
    y_vals = np.linspace(-search_range, search_range, grid_resolution)
    X, Y = np.meshgrid(x_vals, y_vals)

    # Evaluate both curves on the grid
    try:
        Z1 = curve1.evaluate(X, Y)
        Z2 = curve2.evaluate(X, Y)
    except Exception as e:
        print(f"Error evaluating curves: {e}")
        return []

    # Find points where both curves are close to zero or cross zero (sign changes).
    # NaN values arise from out-of-domain evaluations (e.g. asin(x>1), sqrt(x<0)).
    # - For standard sign-change detection, operate on Z1 directly: NaN*anything=NaN,
    #   and NaN<=0 is False in NumPy, so NaN cells naturally self-exclude.
    # - For restricted-domain curves (arcsin, sqrt), intersections occur at the
    #   domain boundary. We detect this by marking finite cells adjacent to NaN cells.
    nan_mask1 = ~np.isfinite(Z1)
    nan_mask2 = ~np.isfinite(Z2)

    # Standard sign-change detection on original Z (NaN cells excluded naturally)
    sign_change_x1 = np.zeros_like(Z1, dtype=bool)
    sign_change_x1[:, :-1] |= Z1[:, :-1] * Z1[:, 1:] <= 0
    sign_change_x1[:, 1:] |= Z1[:, :-1] * Z1[:, 1:] <= 0

    sign_change_y1 = np.zeros_like(Z1, dtype=bool)
    sign_change_y1[:-1, :] |= Z1[:-1, :] * Z1[1:, :] <= 0
    sign_change_y1[1:, :] |= Z1[:-1, :] * Z1[1:, :] <= 0

    # Adjacent-to-NaN: finite cells neighboring a NaN cell are domain-boundary candidates
    near_nan_x1 = np.zeros_like(nan_mask1)
    near_nan_x1[:, :-1] |= nan_mask1[:, 1:]
    near_nan_x1[:, 1:] |= nan_mask1[:, :-1]
    near_nan_y1 = np.zeros_like(nan_mask1)
    near_nan_y1[:-1, :] |= nan_mask1[1:, :]
    near_nan_y1[1:, :] |= nan_mask1[:-1, :]

    mask1 = (
        (np.abs(Z1) < coarse_tolerance)
        | sign_change_x1
        | sign_change_y1
        | near_nan_x1
        | near_nan_y1
    ) & ~nan_mask1

    sign_change_x2 = np.zeros_like(Z2, dtype=bool)
    sign_change_x2[:, :-1] |= Z2[:, :-1] * Z2[:, 1:] <= 0
    sign_change_x2[:, 1:] |= Z2[:, :-1] * Z2[:, 1:] <= 0

    sign_change_y2 = np.zeros_like(Z2, dtype=bool)
    sign_change_y2[:-1, :] |= Z2[:-1, :] * Z2[1:, :] <= 0
    sign_change_y2[1:, :] |= Z2[:-1, :] * Z2[1:, :] <= 0

    near_nan_x2 = np.zeros_like(nan_mask2)
    near_nan_x2[:, :-1] |= nan_mask2[:, 1:]
    near_nan_x2[:, 1:] |= nan_mask2[:, :-1]
    near_nan_y2 = np.zeros_like(nan_mask2)
    near_nan_y2[:-1, :] |= nan_mask2[1:, :]
    near_nan_y2[1:, :] |= nan_mask2[:-1, :]

    mask2 = (
        (np.abs(Z2) < coarse_tolerance)
        | sign_change_x2
        | sign_change_y2
        | near_nan_x2
        | near_nan_y2
    ) & ~nan_mask2

    intersection_mask = mask1 & mask2

    # A grid seed need not lie on the final trim: an exact zero-width rectangle
    # usually contains no grid points. Retain the neighboring sampling cell.
    # linspace has N-1 intervals, unlike the legacy clustering scale above.
    trim_padding = (
        abs(2.0 * search_range / (grid_resolution - 1)) if grid_resolution > 1 else 0.0
    )
    intersection_mask = _apply_trimming_masks_fast(
        intersection_mask, X, Y, curve1, curve2, padding=trim_padding
    )
    endpoint_seeds = _trim_endpoint_seeds(curve1, curve2, search_range)

    if not np.any(intersection_mask) and not endpoint_seeds:
        return []

    # Extract candidate points
    x_candidates = X[intersection_mask]
    y_candidates = Y[intersection_mask]

    # Simple overlap detection (only if enabled and many candidates)
    if detect_overlap and len(x_candidates) > 20:
        # Preserve this legacy heuristic's original inputs: newly padded seeds
        # must pass numerical refinement, never become coarse overlap outputs.
        overlap_mask = _apply_trimming_masks_fast(
            intersection_mask, X, Y, curve1, curve2
        )
        if np.count_nonzero(overlap_mask) > 20:
            overlap_endpoints = _detect_overlap_endpoints_fast(
                X[overlap_mask], Y[overlap_mask]
            )
            if overlap_endpoints:
                return overlap_endpoints

    # Step 2: Cluster nearby points to avoid duplicates
    candidate_points = np.column_stack([x_candidates, y_candidates])
    starting_points = list(
        _cluster_candidates_fast(
            candidate_points,
            grid_spacing=grid_spacing,
            is_periodic=is_periodic_or_procedural,
        )
    )
    # Endpoints are user-supplied seeds, not accepted intersections. Append after
    # clustering so they are not averaged away or lost to grid subsampling.
    starting_points.extend(endpoint_seeds)

    # Step 3: Refine intersections using numerical solver
    refined_intersections = []

    def are_curves_tangent(x, y, h=1e-5):
        try:
            df1_dx = (curve1.evaluate(x + h, y) - curve1.evaluate(x - h, y)) / (2.0 * h)
            df1_dy = (curve1.evaluate(x, y + h) - curve1.evaluate(x, y - h)) / (2.0 * h)
            df2_dx = (curve2.evaluate(x + h, y) - curve2.evaluate(x - h, y)) / (2.0 * h)
            df2_dy = (curve2.evaluate(x, y + h) - curve2.evaluate(x, y - h)) / (2.0 * h)

            import math

            norm1 = math.sqrt(df1_dx**2 + df1_dy**2)
            norm2 = math.sqrt(df2_dx**2 + df2_dy**2)

            if norm1 < 1e-8 or norm2 < 1e-8:
                return True

            cross_prod = abs(df1_dx * df2_dy - df1_dy * df2_dx)
            normalized_det = cross_prod / (norm1 * norm2)
            return normalized_det < 0.0005
        except Exception:
            return False

    for start_point in starting_points:
        if len(refined_intersections) >= max_points:
            break
        try:
            # Clean up near-zero starting coordinates to prevent fsolve's relative-spacing step calculation from underflowing
            start_point_cleaned = np.where(
                np.abs(start_point) < 1e-13, 0.0, start_point
            )
            solution, info, ier, mesg = fsolve(
                intersection_system, start_point_cleaned, xtol=1e-10, full_output=True
            )
            residual = intersection_system(solution)
            res_norm = np.linalg.norm(residual)
            if ier == 1 or (ier in (2, 3, 4, 5) and res_norm < max(2.5e-5, tol)):
                if res_norm < tol:
                    # Check if this point is valid for both curves (respects trimming)
                    if is_valid_intersection(solution[0], solution[1], tol * 10):
                        # Check if this point is already in our list
                        is_duplicate = False
                        is_tangent = are_curves_tangent(solution[0], solution[1])

                        if is_tangent:
                            if is_periodic_or_procedural:
                                dup_tol = max(tol * 500, 0.05)
                            else:
                                dup_tol = max(tol * 0.1, 1e-5)
                        else:
                            dup_tol = max(tol * 0.1, 1e-5)

                        for existing_point in refined_intersections:
                            if (
                                np.linalg.norm(
                                    np.array(solution) - np.array(existing_point)
                                )
                                < dup_tol
                            ):
                                is_duplicate = True
                                break

                        if (
                            not is_duplicate
                            and abs(solution[0]) <= search_range + 1e-3
                            and abs(solution[1]) <= search_range + 1e-3
                        ):
                            refined_intersections.append(
                                (float(solution[0]), float(solution[1]))
                            )

        except Exception:
            continue

    notify(refined_intersections)

    return refined_intersections[:max_points]


def _are_curves_identical_fast(
    curve1, curve2, tolerance: float, search_range: float = 5.0
) -> bool:
    """
    Fast check if two curves are identical by sampling a few points.
    Returns True only if all test points give finite, close values on both curves.
    """
    # Quick test with just a few points and distributed sampling points.
    # Added irrational offsets to prevent sampling points from landing exactly on periodic zeros (e.g., multiples of pi)
    test_points = [
        (0.123, 0.456),
        (0.5 * search_range + 0.123, 0.2 * search_range + 0.456),
        (-0.3 * search_range + 0.123, -0.7 * search_range + 0.456),
        (0.8 * search_range + 0.123, -0.1 * search_range + 0.456),
        (-0.9 * search_range + 0.123, 0.6 * search_range + 0.456),
    ]

    finite_count = 0
    for x, y in test_points:
        try:
            val1 = curve1.evaluate(x, y)
            val2 = curve2.evaluate(x, y)
            v1 = float(val1[0]) if hasattr(val1, "__len__") else float(val1)
            v2 = float(val2[0]) if hasattr(val2, "__len__") else float(val2)
            # If either value is non-finite (NaN from domain restriction), skip this test point
            if not np.isfinite(v1) or not np.isfinite(v2):
                continue
            finite_count += 1
            if abs(v1 - v2) > tolerance:
                return False
        except Exception:
            return False

    # If we had no finite test points, we cannot conclude they are identical
    return finite_count >= 3


def _trim_endpoint_seeds(curve1, curve2, search_range):
    """Finite explicit trim coordinates; refinement/contains remain authoritative."""
    seeds = []
    for curve in (curve1, curve2):
        if not (hasattr(curve, "mask") and hasattr(curve, "base_curve")):
            continue
        endpoints = getattr(curve, "endpoints", None)
        if endpoints is None:
            continue
        for endpoint in endpoints:
            try:
                point = np.asarray(endpoint, dtype=float)
            except (TypeError, ValueError, OverflowError):
                continue
            if (
                point.shape == (2,)
                and np.isfinite(point).all()
                and np.all(np.abs(point) <= search_range + 1e-3)
                and not any(np.array_equal(point, other) for other in seeds)
            ):
                seeds.append(point.copy())
    return seeds


def _apply_trimming_masks_fast(intersection_mask, X, Y, curve1, curve2, *, padding=0.0):
    """
    Fast application of trimming masks using vectorized operations when possible.
    """
    # Partial rectangles are not exclusion proofs; contains also applies its
    # rectangle only when all four bounds exist. Arbitrary masks stay final-only.
    for curve in (curve1, curve2):
        if not (hasattr(curve, "mask") and hasattr(curve, "base_curve")):
            continue
        bounds = tuple(
            getattr(curve, key, None) for key in ("_xmin", "_xmax", "_ymin", "_ymax")
        )
        if not all(value is not None and np.isfinite(value) for value in bounds):
            continue
        xmin, xmax, ymin, ymax = bounds
        eps = max(1e-9, padding)
        intersection_mask = intersection_mask & (
            (X >= xmin - eps)
            & (X <= xmax + eps)
            & (Y >= ymin - eps)
            & (Y <= ymax + eps)
        )
    return intersection_mask


def _cluster_candidates_fast(
    candidate_points, grid_spacing: float = 0.02, is_periodic: bool = True
):
    """
    Fast clustering of candidate points.
    """
    if len(candidate_points) <= 1:
        return candidate_points

    if len(candidate_points) <= 10:
        # For small numbers, just return all points
        return candidate_points

    # Sub-sample candidate points if there are too many, to prevent O(N^2) pdist performance bottlenecks.
    # Use random sampling to avoid periodic aliasing/moire patterns that miss entire clusters.
    if len(candidate_points) > 1000:
        rng = np.random.default_rng(42)
        indices = rng.choice(len(candidate_points), 1000, replace=False)
        indices.sort()
        candidate_points = candidate_points[indices]

    # For larger numbers, use simple distance-based clustering
    try:
        distances = pdist(candidate_points)
        if len(distances) > 0 and np.max(distances) > 0:
            # Use average linkage and a robust adaptive threshold to prevent chaining of close intersections
            # while avoiding over-segmentation under high grid resolutions
            linkage_matrix = linkage(distances, method="average")
            threshold = max(1.1 * grid_spacing, 0.005) if is_periodic else 0.0005
            clusters = fcluster(
                linkage_matrix, max(1e-5, threshold), criterion="distance"
            )

            # Get cluster centers as starting points
            unique_clusters = np.unique(clusters)
            starting_points = []

            for cluster_id in unique_clusters:
                cluster_mask = clusters == cluster_id
                cluster_points = candidate_points[cluster_mask]
                center = np.mean(cluster_points, axis=0)
                starting_points.append(center)

            return starting_points
        else:
            return [candidate_points[0]]
    except Exception:
        # Fallback: use first few points
        return candidate_points[:5]


def _detect_overlap_endpoints_fast(x_candidates, y_candidates):
    """
    Fast overlap endpoint detection - simplified version.
    """
    points = np.column_stack([x_candidates, y_candidates])

    if len(points) < 10:  # Only detect overlap for many points
        return []

    # Simple approach: return the two points that are farthest apart
    max_distance = 0
    best_pair = None

    # Sample only a subset of points for performance
    sample_size = min(20, len(points))
    indices = np.random.choice(len(points), sample_size, replace=False)
    sample_points = points[indices]

    for i in range(len(sample_points)):
        for j in range(i + 1, len(sample_points)):
            distance = np.linalg.norm(sample_points[i] - sample_points[j])
            if distance > max_distance:
                max_distance = distance
                best_pair = (sample_points[i], sample_points[j])

    if (
        best_pair and max_distance > 0.2
    ):  # Only return if endpoints are reasonably far apart
        return [tuple(best_pair[0]), tuple(best_pair[1])]

    return []


def find_curve_self_intersections(
    curve, search_range: float = 5.0, grid_resolution: int = 300
) -> List[Tuple[float, float]]:
    """
    Find self-intersection points of a curve (e.g., figure-8 curves).

    Args:
        curve: Implicit curve to analyze
        search_range: Range to search for intersections
        grid_resolution: Grid resolution for search

    Returns:
        List of self-intersection points
    """

    # For self-intersections, we need to look for points where the gradient is zero
    # or where the curve has multiple branches passing through the same point

    x_vals = np.linspace(-search_range, search_range, grid_resolution)
    y_vals = np.linspace(-search_range, search_range, grid_resolution)
    X, Y = np.meshgrid(x_vals, y_vals)

    try:
        # Evaluate curve
        Z = curve.evaluate(X, Y)

        # Find points on the curve
        on_curve_mask = np.abs(Z) < 0.05

        if not np.any(on_curve_mask):
            return []

        # Get gradient at curve points
        x_curve = X[on_curve_mask]
        y_curve = Y[on_curve_mask]

        gradient_magnitudes = []
        for x_pt, y_pt in zip(x_curve, y_curve):
            try:
                gx, gy = curve.gradient(x_pt, y_pt)
                grad_mag = np.sqrt(gx**2 + gy**2)
                gradient_magnitudes.append(grad_mag)
            except Exception:
                gradient_magnitudes.append(1e6)

        gradient_magnitudes = np.array(gradient_magnitudes)

        # Find points where gradient is very small (potential singularities)
        singular_mask = gradient_magnitudes < 0.1

        if not np.any(singular_mask):
            return []

        singular_points = list(zip(x_curve[singular_mask], y_curve[singular_mask]))

        # Cluster nearby singular points
        if len(singular_points) > 1:
            try:
                distances = pdist(singular_points)
                if len(distances) > 0 and np.max(distances) > 0:
                    linkage_matrix = linkage(distances)
                    clusters = fcluster(linkage_matrix, 0.1, criterion="distance")

                    unique_clusters = np.unique(clusters)
                    clustered_points = []

                    for cluster_id in unique_clusters:
                        cluster_mask = clusters == cluster_id
                        cluster_points = np.array(singular_points)[cluster_mask]
                        center = np.mean(cluster_points, axis=0)
                        clustered_points.append((float(center[0]), float(center[1])))

                    return clustered_points
            except Exception:
                pass

        return (
            [(float(x_curve[0]), float(y_curve[0]))] if len(singular_points) > 0 else []
        )

    except Exception as e:
        print(f"Error finding self-intersections: {e}")
        return []


def analyze_curve_intersections(
    curves: List, search_range: float = 5.0, show_progress: bool = True
) -> dict:
    """
    Analyze all pairwise intersections between a list of curves.

    Args:
        curves: List of (name, curve) tuples
        search_range: Range to search for intersections
        show_progress: Whether to print progress

    Returns:
        Dictionary with intersection analysis results
    """

    results = {
        "pairwise_intersections": {},
        "self_intersections": {},
        "total_intersection_points": 0,
    }

    # Find pairwise intersections
    for i in range(len(curves)):
        for j in range(i + 1, len(curves)):
            name1, curve1 = curves[i]
            name2, curve2 = curves[j]

            if show_progress:
                print(f"Finding intersections: {name1} ∩ {name2}")

            intersections = find_curve_intersections(curve1, curve2, search_range)

            pair_key = f"{name1} ∩ {name2}"
            results["pairwise_intersections"][pair_key] = intersections
            results["total_intersection_points"] += len(intersections)

            if show_progress and intersections:
                print(f"  Found {len(intersections)} intersection(s)")
                for k, (x, y) in enumerate(intersections):
                    print(f"    Point {k + 1}: ({x:.4f}, {y:.4f})")

    # Find self-intersections
    for name, curve in curves:
        if show_progress:
            print(f"Finding self-intersections: {name}")

        self_intersections = find_curve_self_intersections(curve, search_range)

        if self_intersections:
            results["self_intersections"][name] = self_intersections
            results["total_intersection_points"] += len(self_intersections)

            if show_progress:
                print(f"  Found {len(self_intersections)} self-intersection(s)")
                for k, (x, y) in enumerate(self_intersections):
                    print(f"    Point {k + 1}: ({x:.4f}, {y:.4f})")

    return results
