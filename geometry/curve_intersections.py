"""
Curve intersection utilities - finding discrete intersection points
"""

import numpy as np
import sympy as sp
from typing import List, Tuple, Union
from scipy.optimize import fsolve
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import fcluster, linkage


def find_curve_intersections(curve1, curve2, 
                           search_range: float = 5.0,
                           grid_resolution: int = 500,
                           tolerance: float = 1e-6,
                           max_points: int = 50,
                           detect_overlap: bool = False) -> List[Tuple[float, float]]:
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
        
    Returns:
        List of (x, y) intersection points
    """
    
    # Quick check for identical curves (only if detect_overlap is enabled)
    if detect_overlap and _are_curves_identical_fast(curve1, curve2, tolerance):
        return []  # Return empty for identical curves
    
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
    
    # Find points where both curves are close to zero
    coarse_tolerance = 0.05
    mask1 = np.abs(Z1) < coarse_tolerance
    mask2 = np.abs(Z2) < coarse_tolerance
    intersection_mask = mask1 & mask2
    
    # For trimmed curves, apply trimming masks efficiently
    intersection_mask = _apply_trimming_masks_fast(intersection_mask, X, Y, curve1, curve2)
    
    if not np.any(intersection_mask):
        return []
    
    # Extract candidate points
    x_candidates = X[intersection_mask]
    y_candidates = Y[intersection_mask]
    
    if len(x_candidates) == 0:
        return []
    
    # Simple overlap detection (only if enabled and many candidates)
    if detect_overlap and len(x_candidates) > 20:
        overlap_endpoints = _detect_overlap_endpoints_fast(x_candidates, y_candidates)
        if overlap_endpoints:
            return overlap_endpoints
    
    # Step 2: Cluster nearby points to avoid duplicates
    candidate_points = np.column_stack([x_candidates, y_candidates])
    starting_points = _cluster_candidates_fast(candidate_points)
    
    # Step 3: Refine intersections using numerical solver
    refined_intersections = []
    
    def intersection_system(point):
        """System of equations: both curves should be zero"""
        x_val, y_val = point
        try:
            f1 = curve1.evaluate(x_val, y_val)
            f2 = curve2.evaluate(x_val, y_val)
            return [f1, f2]
        except Exception:
            return [1e6, 1e6]  # Large values to indicate failure
    
    def is_valid_intersection(x_val, y_val, tolerance):
        """Check if intersection point is valid for both curves (respects trimming)"""
        # For trimmed curves, check if point satisfies the mask
        if hasattr(curve1, 'mask') and hasattr(curve1, 'base_curve'):
            # This is a TrimmedImplicitCurve
            if not curve1.contains(x_val, y_val, tolerance):
                return False
        
        if hasattr(curve2, 'mask') and hasattr(curve2, 'base_curve'):
            # This is a TrimmedImplicitCurve
            if not curve2.contains(x_val, y_val, tolerance):
                return False
        
        return True
    
    for start_point in starting_points[:max_points]:
        try:
            # Use numerical solver to refine the intersection
            solution = fsolve(intersection_system, start_point, xtol=tolerance)
            
            # Verify the solution
            residual = intersection_system(solution)
            if np.linalg.norm(residual) < tolerance:
                # Check if this point is valid for both curves (respects trimming)
                if is_valid_intersection(solution[0], solution[1], tolerance * 100):
                    # Check if this point is already in our list
                    is_duplicate = False
                    for existing_point in refined_intersections:
                        if np.linalg.norm(np.array(solution) - np.array(existing_point)) < tolerance * 100:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate and abs(solution[0]) < search_range and abs(solution[1]) < search_range:
                        refined_intersections.append((float(solution[0]), float(solution[1])))
                        
        except Exception:
            continue
    
    return refined_intersections[:max_points]


def _are_curves_identical_fast(curve1, curve2, tolerance: float) -> bool:
    """
    Fast check if two curves are identical by sampling a few points.
    """
    # Quick test with just a few points
    test_points = [(0, 0), (1, 0), (0, 1)]
    
    for x, y in test_points:
        try:
            val1 = curve1.evaluate(x, y)
            val2 = curve2.evaluate(x, y)
            if abs(val1 - val2) > tolerance:
                return False
        except Exception:
            return False
    
    return True


def _apply_trimming_masks_fast(intersection_mask, X, Y, curve1, curve2):
    """
    Fast application of trimming masks using vectorized operations when possible.
    """
    # Apply curve1's trimming mask
    if hasattr(curve1, 'mask') and hasattr(curve1, 'base_curve'):
        if hasattr(curve1, '_xmin') and curve1._xmin is not None:
            # Use explicit bounds (fast)
            eps = 1e-9
            trim_mask1 = (
                (X >= (curve1._xmin - eps)) & (X <= (curve1._xmax + eps)) &
                (Y >= (curve1._ymin - eps)) & (Y <= (curve1._ymax + eps))
            )
            intersection_mask = intersection_mask & trim_mask1
        else:
            # Skip expensive point-by-point evaluation for performance
            # Only apply mask to candidate points later
            pass
    
    # Apply curve2's trimming mask
    if hasattr(curve2, 'mask') and hasattr(curve2, 'base_curve'):
        if hasattr(curve2, '_xmin') and curve2._xmin is not None:
            # Use explicit bounds (fast)
            eps = 1e-9
            trim_mask2 = (
                (X >= (curve2._xmin - eps)) & (X <= (curve2._xmax + eps)) &
                (Y >= (curve2._ymin - eps)) & (Y <= (curve2._ymax + eps))
            )
            intersection_mask = intersection_mask & trim_mask2
        else:
            # Skip expensive point-by-point evaluation for performance
            pass
    
    return intersection_mask


def _cluster_candidates_fast(candidate_points):
    """
    Fast clustering of candidate points.
    """
    if len(candidate_points) <= 1:
        return candidate_points
    
    if len(candidate_points) <= 10:
        # For small numbers, just return all points
        return candidate_points
    
    # For larger numbers, use simple distance-based clustering
    try:
        distances = pdist(candidate_points)
        if len(distances) > 0 and np.max(distances) > 0:
            linkage_matrix = linkage(distances)
            clusters = fcluster(linkage_matrix, 0.1, criterion='distance')
            
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
    
    if best_pair and max_distance > 0.2:  # Only return if endpoints are reasonably far apart
        return [tuple(best_pair[0]), tuple(best_pair[1])]
    
    return []


def find_curve_self_intersections(curve, 
                                 search_range: float = 5.0,
                                 grid_resolution: int = 300) -> List[Tuple[float, float]]:
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
                    clusters = fcluster(linkage_matrix, 0.1, criterion='distance')
                    
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
        
        return [(float(x_curve[0]), float(y_curve[0]))] if len(singular_points) > 0 else []
        
    except Exception as e:
        print(f"Error finding self-intersections: {e}")
        return []


def analyze_curve_intersections(curves: List, 
                              search_range: float = 5.0,
                              show_progress: bool = True) -> dict:
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
        'pairwise_intersections': {},
        'self_intersections': {},
        'total_intersection_points': 0
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
            results['pairwise_intersections'][pair_key] = intersections
            results['total_intersection_points'] += len(intersections)
            
            if show_progress and intersections:
                print(f"  Found {len(intersections)} intersection(s)")
                for k, (x, y) in enumerate(intersections):
                    print(f"    Point {k+1}: ({x:.4f}, {y:.4f})")
    
    # Find self-intersections
    for name, curve in curves:
        if show_progress:
            print(f"Finding self-intersections: {name}")
        
        self_intersections = find_curve_self_intersections(curve, search_range)
        
        if self_intersections:
            results['self_intersections'][name] = self_intersections
            results['total_intersection_points'] += len(self_intersections)
            
            if show_progress:
                print(f"  Found {len(self_intersections)} self-intersection(s)")
                for k, (x, y) in enumerate(self_intersections):
                    print(f"    Point {k+1}: ({x:.4f}, {y:.4f})")
    
    return results