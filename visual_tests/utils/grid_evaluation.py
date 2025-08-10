"""
Grid evaluation utilities for visual tests.

Provides functionality for creating test grids, evaluating curves and regions
over grids, and analyzing the results.
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Optional, Callable
import traceback


class GridEvaluator:
    """
    Handles grid-based evaluation of curves and regions.
    
    Provides methods for creating test grids, evaluating geometric objects
    over grids, and analyzing the results with proper error handling.
    """
    
    def __init__(self, default_grid_size: int = 100):
        """
        Initialize the grid evaluator.
        
        Args:
            default_grid_size: Default number of points along each axis
        """
        self.default_grid_size = default_grid_size
        self.default_bounds = (-3, 3, -3, 3)  # x_min, x_max, y_min, y_max
    
    def create_grid(self, bounds: Tuple[float, float, float, float] = None,
                   grid_size: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a uniform test grid.
        
        Args:
            bounds: Grid bounds (x_min, x_max, y_min, y_max)
            grid_size: Number of points along each axis
            
        Returns:
            Tuple of (X, Y) coordinate meshgrids
        """
        if bounds is None:
            bounds = self.default_bounds
        if grid_size is None:
            grid_size = self.default_grid_size
            
        x_min, x_max, y_min, y_max = bounds
        
        x_range = np.linspace(x_min, x_max, grid_size)
        y_range = np.linspace(y_min, y_max, grid_size)
        X, Y = np.meshgrid(x_range, y_range)
        
        return X, Y
    
    def evaluate_curve_over_grid(self, curve: Any, X: np.ndarray, Y: np.ndarray,
                               handle_errors: bool = True) -> np.ndarray:
        """
        Evaluate a curve over a grid of points.
        
        Args:
            curve: Curve object with evaluate method
            X: X coordinate meshgrid
            Y: Y coordinate meshgrid
            handle_errors: Whether to handle evaluation errors gracefully
            
        Returns:
            2D array of curve values
        """
        Z = np.zeros_like(X)
        error_count = 0
        
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                try:
                    Z[i, j] = curve.evaluate(X[i, j], Y[i, j])
                except Exception as e:
                    if handle_errors:
                        Z[i, j] = np.nan
                        error_count += 1
                    else:
                        raise e
        
        if error_count > 0 and handle_errors:
            total_points = X.size
            print(f"Warning: {error_count}/{total_points} points failed evaluation "
                  f"({100*error_count/total_points:.1f}%)")
        
        return Z
    
    def evaluate_region_containment(self, region: Any, X: np.ndarray, Y: np.ndarray,
                                   test_boundary: bool = False, handle_errors: bool = True) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Evaluate region containment over a grid with optimized chunked processing.
        
        Args:
            region: Region object with contains method
            X: X coordinate meshgrid
            Y: Y coordinate meshgrid
            test_boundary: Whether to also test boundary containment
            handle_errors: Whether to handle evaluation errors gracefully
            
        Returns:
            Tuple of (inside_mask, boundary_mask). boundary_mask is None if test_boundary is False.
        """
        inside_mask = np.zeros_like(X, dtype=bool)
        boundary_mask = np.zeros_like(X, dtype=bool) if test_boundary else None
        error_count = 0
        total_points = X.size
        
        # Process in chunks for better performance and progress reporting
        chunk_size = min(1000, total_points)  # Process up to 1000 points at a time
        num_chunks = (total_points + chunk_size - 1) // chunk_size
        
        # Flatten arrays for easier processing
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        inside_flat = np.zeros(total_points, dtype=bool)
        boundary_flat = np.zeros(total_points, dtype=bool) if test_boundary else None
        
        for chunk_idx in range(num_chunks):
            start_idx = chunk_idx * chunk_size
            end_idx = min(start_idx + chunk_size, total_points)

            # Progress reporting
            if num_chunks > 1:
                progress = (chunk_idx + 1) / num_chunks * 100
                print(f"    Progress: {progress:.1f}% ({end_idx}/{total_points} points)")

            # Process chunk for inside mask
            for i in range(start_idx, end_idx):
                try:
                    # AreaRegion.contains signature is (x, y, tolerance=...)
                    # Do not pass non-existent flags like region_containment
                    inside_flat[i] = region.contains(X_flat[i], Y_flat[i])
                except Exception:
                    if handle_errors:
                        inside_flat[i] = False
                        error_count += 1
                    else:
                        raise
        
        # Reshape inside mask
        inside_mask = inside_flat.reshape(X.shape)

        # Compute boundary mask using implicit boundary evaluation with tolerance
        if test_boundary:
            # Determine tolerance based on grid spacing
            try:
                dx = (np.max(X) - np.min(X)) / max(X.shape[1] - 1, 1)
                dy = (np.max(Y) - np.min(Y)) / max(Y.shape[0] - 1, 1)
                eps = 0.5 * max(dx, dy)
            except Exception:
                eps = 1e-2

            boundary_mask = np.zeros_like(X, dtype=bool)

            # Try to get a boundary curve to evaluate
            boundary_curve = getattr(region, 'outer_boundary', None) or getattr(region, 'boundary', None)

            if boundary_curve is not None and hasattr(boundary_curve, 'evaluate'):
                try:
                    Zb = np.asarray(boundary_curve.evaluate(X, Y))
                    if Zb.shape != X.shape:
                        Zb = Zb.reshape(X.shape)
                    boundary_mask = np.isfinite(Zb) & (np.abs(Zb) <= eps)
                except Exception:
                    # Fall back to per-point evaluation on segments if composite
                    curves = getattr(boundary_curve, 'curves', [])
                    if curves:
                        Z_accum = np.full_like(X, np.inf, dtype=float)
                        for seg in curves:
                            try:
                                Zs = np.asarray(seg.evaluate(X, Y))
                                if Zs.shape != X.shape:
                                    Zs = Zs.reshape(X.shape)
                                # accumulate min absolute value as proxy for distance to boundary
                                Z_accum = np.minimum(Z_accum, np.abs(Zs))
                            except Exception:
                                continue
                        boundary_mask = np.isfinite(Z_accum) & (Z_accum <= eps)
                    else:
                        # Last resort: use exact boundary containment (likely sparse)
                        for i in range(total_points):
                            try:
                                boundary_flat[i] = region.contains(X_flat[i], Y_flat[i], region_containment=False)
                            except Exception:
                                boundary_flat[i] = False
                        boundary_mask = boundary_flat.reshape(X.shape)
            else:
                # No explicit boundary available: resort to exact boundary containment
                for i in range(total_points):
                    try:
                        boundary_flat[i] = region.contains(X_flat[i], Y_flat[i], region_containment=False)
                    except Exception:
                        boundary_flat[i] = False
                boundary_mask = boundary_flat.reshape(X.shape)
        
        if error_count > 0 and handle_errors:
            print(f"Warning: {error_count}/{total_points} points failed containment test "
                  f"({100*error_count/total_points:.1f}%)")
        
        return inside_mask, boundary_mask
    
    def test_specific_points(self, obj: Any, test_points: List[Tuple[float, float, str]],
                           test_type: str = 'curve') -> Dict[str, Any]:
        """
        Test specific points on a curve or region.
        
        Args:
            obj: Curve or region object to test
            test_points: List of (x, y, description) tuples
            test_type: Either 'curve' or 'region'
            
        Returns:
            Dictionary with test results
        """
        results = {
            'points': [],
            'errors': [],
            'summary': {}
        }
        
        for px, py, description in test_points:
            try:
                if test_type == 'curve':
                    value = obj.evaluate(px, py)
                    on_curve = abs(value) < 0.01  # Tolerance for being on curve
                    
                    result = {
                        'point': (px, py),
                        'description': description,
                        'value': value,
                        'on_curve': on_curve,
                        'status': 'ON CURVE' if on_curve else 'OFF CURVE'
                    }
                    
                elif test_type == 'region':
                    is_inside = obj.contains(px, py, region_containment=True)
                    is_boundary = obj.contains(px, py, region_containment=False)
                    
                    if is_inside:
                        status = 'INSIDE'
                    elif is_boundary:
                        status = 'BOUNDARY'
                    else:
                        status = 'OUTSIDE'
                    
                    result = {
                        'point': (px, py),
                        'description': description,
                        'inside': is_inside,
                        'boundary': is_boundary,
                        'status': status
                    }
                    
                else:
                    raise ValueError(f"Invalid test_type: {test_type}")
                
                results['points'].append(result)
                
            except Exception as e:
                error_info = {
                    'point': (px, py),
                    'description': description,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                results['errors'].append(error_info)
        
        # Generate summary
        total_tests = len(test_points)
        successful_tests = len(results['points'])
        failed_tests = len(results['errors'])
        
        results['summary'] = {
            'total_tests': total_tests,
            'successful': successful_tests,
            'failed': failed_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0
        }
        
        return results
    
    def print_test_results(self, results: Dict[str, Any]) -> None:
        """
        Print formatted test results.
        
        Args:
            results: Results dictionary from test_specific_points
        """
        print(f"\n{'='*60}")
        print("SPECIFIC POINT TESTS")
        print(f"{'='*60}")
        
        # Print successful tests
        for result in results['points']:
            point_str = f"({result['point'][0]:4.1f}, {result['point'][1]:4.1f})"
            desc_str = f"[{result['description']:15s}]"
            
            if 'value' in result:  # Curve test
                print(f"  Point {point_str} {desc_str}: {result['status']} (value: {result['value']:.6f})")
            else:  # Region test
                print(f"  Point {point_str} {desc_str}: {result['status']}")
        
        # Print errors
        if results['errors']:
            print(f"\nERRORS:")
            for error in results['errors']:
                point_str = f"({error['point'][0]:4.1f}, {error['point'][1]:4.1f})"
                desc_str = f"[{error['description']:15s}]"
                print(f"  Point {point_str} {desc_str}: ERROR - {error['error']}")
        
        # Print summary
        summary = results['summary']
        print(f"\nSUMMARY:")
        print(f"  Total tests: {summary['total_tests']}")
        print(f"  Successful:  {summary['successful']}")
        print(f"  Failed:      {summary['failed']}")
        print(f"  Success rate: {summary['success_rate']:.1%}")
    
    def analyze_grid_statistics(self, inside_mask: np.ndarray, 
                              boundary_mask: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Analyze statistics from grid evaluation.
        
        Args:
            inside_mask: Boolean mask for inside points
            boundary_mask: Optional boolean mask for boundary points
            
        Returns:
            Dictionary with statistics
        """
        total_points = inside_mask.size
        inside_count = np.sum(inside_mask)
        
        stats = {
            'total_points': total_points,
            'inside_count': inside_count,
            'inside_percentage': 100 * inside_count / total_points,
        }
        
        if boundary_mask is not None:
            boundary_count = np.sum(boundary_mask)
            outside_count = total_points - inside_count - boundary_count
            
            stats.update({
                'boundary_count': boundary_count,
                'outside_count': outside_count,
                'boundary_percentage': 100 * boundary_count / total_points,
                'outside_percentage': 100 * outside_count / total_points
            })
        else:
            outside_count = total_points - inside_count
            stats.update({
                'outside_count': outside_count,
                'outside_percentage': 100 * outside_count / total_points
            })
        
        return stats
    
    def print_grid_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Print formatted grid statistics.
        
        Args:
            stats: Statistics dictionary from analyze_grid_statistics
        """
        print(f"\n{'='*50}")
        print("GRID EVALUATION STATISTICS")
        print(f"{'='*50}")
        print(f"Total grid points: {stats['total_points']}")
        print(f"Inside points:     {stats['inside_count']} ({stats['inside_percentage']:.1f}%)")
        
        if 'boundary_count' in stats:
            print(f"Boundary points:   {stats['boundary_count']} ({stats['boundary_percentage']:.1f}%)")
            print(f"Outside points:    {stats['outside_count']} ({stats['outside_percentage']:.1f}%)")
        else:
            print(f"Outside points:    {stats['outside_count']} ({stats['outside_percentage']:.1f}%)")
    
    def create_focused_grid(self, center: Tuple[float, float], 
                          size: float, grid_size: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a grid focused around a specific center point.
        
        Args:
            center: Center point (x, y)
            size: Size of the grid (half-width/height)
            grid_size: Number of points along each axis
            
        Returns:
            Tuple of (X, Y) coordinate meshgrids
        """
        if grid_size is None:
            grid_size = self.default_grid_size
            
        cx, cy = center
        bounds = (cx - size, cx + size, cy - size, cy + size)
        
        return self.create_grid(bounds, grid_size)
