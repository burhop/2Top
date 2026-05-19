"""
Graphics Backend Interface for 2Top Geometry Library

Provides structured, render-ready data extraction from SceneManager for
front-end applications, web interfaces, and visualization tools.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path
import json
import tempfile
from itertools import combinations
import matplotlib
# Use non-interactive backend to avoid Tkinter main-loop issues in tests/servers
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches

from scene_management import SceneManager
from visual_tests.utils.grid_evaluation import GridEvaluator


class GraphicsBackendInterface:
    """
    Main interface for extracting render-ready data from 2Top scenes.
    
    Provides methods to convert internal geometry representations into
    structured data that front-end applications can easily consume for
    visualization and interaction.
    """
    
    def __init__(self, scene_manager: SceneManager):
        """
        Initialize graphics backend with a scene manager.
        
        Args:
            scene_manager: SceneManager instance to extract data from
        """
        self.scene_manager = scene_manager
        self.grid_evaluator = GridEvaluator()
        
        # Default rendering settings
        self.default_resolution = (800, 600)
        self.default_bounds = (-5, 5, -5, 5)  # xmin, xmax, ymin, ymax
        self.default_grid_resolution = 100
        self._fallback_bounds = (-5.0, 5.0, -5.0, 5.0)
    
    # ================== Curve Data Extraction ==================
    
    def get_curve_paths(self, bounds: Optional[Tuple[float, float, float, float]] = None,
                       resolution: int = 200) -> Dict[str, Dict]:
        """
        Extract polyline approximations of all curves in the scene.
        
        Args:
            bounds: (xmin, xmax, ymin, ymax) for curve sampling
            resolution: Number of points to sample per curve
            
        Returns:
            Dict mapping object IDs to curve path data:
            {
                'obj_id': {
                    'type': 'curve',
                    'points': [[x1, y1], [x2, y2], ...],
                    'closed': bool,
                    'style': {color, linewidth, alpha, ...},
                    'bounds': [xmin, xmax, ymin, ymax]
                }
            }
        """
        if bounds is None:
            bounds = self.default_bounds
        
        xmin, xmax, ymin, ymax = bounds
        curve_data = {}
        
        for obj_id in self.scene_manager.list_objects():
            obj = self.scene_manager.get_object(obj_id)
            style = self.scene_manager.get_style(obj_id)
            
            try:
                # Use per-object local bounds so small objects aren't evaluated on a
                # huge global grid (which produces degenerate/line contours).
                obj_bounds = self._estimate_object_bounds(obj, bounds)

                paths = []
                # Generate polyline approximation
                if hasattr(obj, 'get_polyline_approximation'):
                    # Use object's built-in approximation if available
                    points = obj.get_polyline_approximation(obj_bounds, resolution)
                    closed = getattr(obj, 'is_closed', lambda: False)()
                    paths = [points] if points else []
                else:
                    # Try contour extraction, with fallback to boundary sampling
                    points, closed, paths = self._extract_curve_contour(obj, obj_bounds, resolution)
                    
                    # If contour extraction failed, try boundary sampling for AreaRegion
                    if not points and hasattr(obj, 'outer_boundary'):
                        points, closed = self._sample_boundary_points(obj.outer_boundary, obj_bounds, resolution)
                        paths = [points] if points else []
                
                if points and len(points) > 1:
                    # Snapping open curves to mathematically exact endpoints to avoid early-termination visual gaps
                    if hasattr(obj, 'get_endpoints') and not closed:
                        try:
                            endpoints = obj.get_endpoints()
                            if endpoints and len(endpoints) > 0:
                                o_xmin, o_xmax, o_ymin, o_ymax = obj_bounds
                                grid_spacing = max((o_xmax - o_xmin) / resolution, (o_ymax - o_ymin) / resolution)
                                snap_threshold = max(1.0, 3.0 * grid_spacing)
                                sq_threshold = snap_threshold ** 2
                                # Snap start and end of all paths in paths to their closest exact endpoints
                                for path in paths:
                                    if len(path) >= 2:
                                        # Snap start of the path
                                        p_start = path[0]
                                        best_ep_start = None
                                        min_d_start = float('inf')
                                        for ep in endpoints:
                                            d = (ep[0] - p_start[0])**2 + (ep[1] - p_start[1])**2
                                            if d < min_d_start:
                                                min_d_start = d
                                                best_ep_start = ep
                                        if min_d_start < sq_threshold and best_ep_start is not None:
                                            path[0] = [float(best_ep_start[0]), float(best_ep_start[1])]

                                        # Snap end of the path
                                        p_end = path[-1]
                                        best_ep_end = None
                                        min_d_end = float('inf')
                                        for ep in endpoints:
                                            d = (ep[0] - p_end[0])**2 + (ep[1] - p_end[1])**2
                                            if d < min_d_end:
                                                min_d_end = d
                                                best_ep_end = ep
                                        if min_d_end < sq_threshold and best_ep_end is not None:
                                            path[-1] = [float(best_ep_end[0]), float(best_ep_end[1])]

                                # Also snap the primary points list
                                if points and len(points) >= 2:
                                    # Snap start of points
                                    p_start = points[0]
                                    best_ep_start = None
                                    min_d_start = float('inf')
                                    for ep in endpoints:
                                        d = (ep[0] - p_start[0])**2 + (ep[1] - p_start[1])**2
                                        if d < min_d_start:
                                            min_d_start = d
                                            best_ep_start = ep
                                    if min_d_start < sq_threshold and best_ep_start is not None:
                                        points[0] = [float(best_ep_start[0]), float(best_ep_start[1])]

                                    # Snap end of points
                                    p_end = points[-1]
                                    best_ep_end = None
                                    min_d_end = float('inf')
                                    for ep in endpoints:
                                        d = (ep[0] - p_end[0])**2 + (ep[1] - p_end[1])**2
                                        if d < min_d_end:
                                            min_d_end = d
                                            best_ep_end = ep
                                    if min_d_end < sq_threshold and best_ep_end is not None:
                                        points[-1] = [float(best_ep_end[0]), float(best_ep_end[1])]
                        except Exception as snap_err:
                            print(f"Warning: Failed endpoint snapping for '{obj_id}': {snap_err}")
                    # Calculate actual bounds of the curve
                    points_array = np.array(points)
                    curve_bounds = [
                        float(np.min(points_array[:, 0])),  # xmin
                        float(np.max(points_array[:, 0])),  # xmax
                        float(np.min(points_array[:, 1])),  # ymin
                        float(np.max(points_array[:, 1]))   # ymax
                    ]
                    
                    curve_data[obj_id] = {
                        'type': 'curve',
                        'points': points,
                        'paths': paths if paths else ([points] if points else []),
                        'closed': closed,
                        'style': style,
                        'bounds': curve_bounds,
                        'point_count': len(points)
                    }
                    
            except Exception as e:
                print(f"Warning: Failed to extract curve data for '{obj_id}': {e}")
                # Provide fallback data
                curve_data[obj_id] = {
                    'type': 'curve',
                    'points': [],
                    'closed': False,
                    'style': style,
                    'bounds': list(bounds),
                    'error': str(e)
                }
        
        return curve_data
    
    def get_field_data(self, bounds: Optional[Tuple[float, float, float, float]] = None,
                      resolution: Tuple[int, int] = None) -> Dict[str, Dict]:
        """
        Extract sampled grid data for all scalar fields in the scene.
        
        Args:
            bounds: (xmin, xmax, ymin, ymax) for field sampling
            resolution: (width, height) grid resolution
            
        Returns:
            Dict mapping object IDs to field data:
            {
                'obj_id': {
                    'type': 'field',
                    'data': numpy array of shape (height, width),
                    'bounds': [xmin, xmax, ymin, ymax],
                    'resolution': [width, height],
                    'style': {colormap, vmin, vmax, ...},
                    'statistics': {min, max, mean, std}
                }
            }
        """
        if bounds is None:
            bounds = self.default_bounds
        if resolution is None:
            resolution = (self.default_grid_resolution, self.default_grid_resolution)
        
        xmin, xmax, ymin, ymax = bounds
        width, height = resolution
        
        # Create sampling grid
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        
        field_data = {}
        
        for obj_id in self.scene_manager.list_objects():
            obj = self.scene_manager.get_object(obj_id)
            style = self.scene_manager.get_style(obj_id)
            
            try:
                # Check if object can be evaluated as a field
                if hasattr(obj, 'evaluate'):
                    # Direct evaluation for curves
                    Z = obj.evaluate(X, Y)
                elif hasattr(obj, 'outer_boundary') and hasattr(obj.outer_boundary, 'evaluate'):
                    # For AreaRegion, use the outer_boundary curve
                    Z = obj.outer_boundary.evaluate(X, Y)
                else:
                    # Objects that can't be evaluated get an error entry
                    field_data[obj_id] = {
                        'type': 'field',
                        'bounds': list(bounds),
                        'resolution': list(resolution),
                        'style': style,
                        'error': f'Object type {type(obj).__name__} does not support field evaluation'
                    }
                    continue
                
                # Ensure Z is a proper numpy array
                if not isinstance(Z, np.ndarray):
                    Z = np.array(Z)
                
                # Handle shape issues for vectorized evaluation
                if Z.shape != X.shape:
                    if Z.ndim == 1 and Z.size == X.size:
                        # Reshape 1D array to match grid shape
                        Z = Z.reshape(X.shape)
                    elif Z.ndim == 1 and Z.size == resolution[0]:
                        # Handle case where evaluation returns only one dimension
                        # This can happen with some curve evaluation methods
                        # Create a broadcast-compatible result
                        Z_2d = np.zeros(X.shape)
                        for i in range(resolution[1]):
                            Z_2d[i, :] = Z
                        Z = Z_2d
                    elif Z.ndim == 1 and Z.size == resolution[1]:
                        # Handle case where evaluation returns only one dimension (other axis)
                        Z_2d = np.zeros(X.shape)
                        for j in range(resolution[0]):
                            Z_2d[:, j] = Z
                        Z = Z_2d
                    elif Z.size == X.size:
                        # Try to reshape if sizes match
                        Z = Z.reshape(X.shape)
                    else:
                        # Objects with unresolvable shape mismatch get an error entry
                        field_data[obj_id] = {
                            'type': 'field',
                            'bounds': list(bounds),
                            'resolution': list(resolution),
                            'style': style,
                            'error': f'Shape mismatch: expected {X.shape}, got {Z.shape}, sizes: {X.size} vs {Z.size}'
                        }
                        continue
                    
                # Calculate statistics
                finite_mask = np.isfinite(Z)
                if np.any(finite_mask):
                    finite_values = Z[finite_mask]
                    stats = {
                        'min': float(np.min(finite_values)),
                        'max': float(np.max(finite_values)),
                        'mean': float(np.mean(finite_values)),
                        'std': float(np.std(finite_values)),
                        'finite_count': int(np.sum(finite_mask)),
                        'total_count': int(Z.size)
                    }
                else:
                    stats = {
                        'min': 0.0, 'max': 0.0, 'mean': 0.0, 'std': 0.0,
                        'finite_count': 0, 'total_count': int(Z.size)
                    }
                
                field_data[obj_id] = {
                    'type': 'field',
                    'data': Z.tolist(),  # Convert to JSON-serializable format
                    'bounds': list(bounds),
                    'resolution': list(resolution),
                    'style': style,
                    'statistics': stats
                }
                    
            except Exception as e:
                print(f"Warning: Failed to extract field data for '{obj_id}': {e}")
                field_data[obj_id] = {
                    'type': 'field',
                    'data': None,
                    'bounds': list(bounds),
                    'resolution': list(resolution),
                    'style': style,
                    'error': str(e)
                }
        
        return field_data
    
    def get_region_data(self, bounds: Optional[Tuple[float, float, float, float]] = None,
                       resolution: Tuple[int, int] = None) -> Dict[str, Dict]:
        """
        Extract filled region data with inside/boundary masks.
        
        Args:
            bounds: (xmin, xmax, ymin, ymax) for region sampling
            resolution: (width, height) grid resolution
            
        Returns:
            Dict mapping object IDs to region data:
            {
                'obj_id': {
                    'type': 'region',
                    'inside_mask': boolean array of shape (height, width),
                    'boundary_mask': boolean array of shape (height, width),
                    'bounds': [xmin, xmax, ymin, ymax],
                    'resolution': [width, height],
                    'style': {fill_color, fill_alpha, edge_color, ...},
                    'statistics': {inside_count, boundary_count, total_count}
                }
            }
        """
        if bounds is None:
            bounds = self.default_bounds
        if resolution is None:
            resolution = (self.default_grid_resolution, self.default_grid_resolution)
        
        region_data = {}
        
        for obj_id in self.scene_manager.list_objects():
            obj = self.scene_manager.get_object(obj_id)
            style = self.scene_manager.get_style(obj_id)
            
            try:
                # Check if object supports region containment
                if hasattr(obj, 'contains'):
                    # Use GridEvaluator to compute masks
                    X, Y = self.grid_evaluator.create_grid(bounds, resolution[0])
                    inside_mask, boundary_mask = self.grid_evaluator.evaluate_region_containment(
                        obj, X, Y, test_boundary=True, handle_errors=True
                    )
                    
                    # Calculate statistics
                    inside_count = int(np.sum(inside_mask))
                    boundary_count = int(np.sum(boundary_mask))
                    total_count = int(inside_mask.size)
                    
                    stats = {
                        'inside_count': inside_count,
                        'boundary_count': boundary_count,
                        'total_count': total_count,
                        'inside_percentage': 100.0 * inside_count / total_count,
                        'boundary_percentage': 100.0 * boundary_count / total_count
                    }
                    
                    region_data[obj_id] = {
                        'type': 'region',
                        'inside_mask': inside_mask.tolist(),
                        'boundary_mask': boundary_mask.tolist(),
                        'bounds': list(bounds),
                        'resolution': list(resolution),
                        'style': style,
                        'statistics': stats
                    }
                    
            except Exception as e:
                print(f"Warning: Failed to extract region data for '{obj_id}': {e}")
                region_data[obj_id] = {
                    'type': 'region',
                    'inside_mask': None,
                    'boundary_mask': None,
                    'bounds': list(bounds),
                    'resolution': list(resolution),
                    'style': style,
                    'error': str(e)
                }
        
        return region_data
    
    # ================== Rendering Services ==================
    
    def render_scene_image(self, filename: str, 
                          bounds: Optional[Tuple[float, float, float, float]] = None,
                          resolution: Tuple[int, int] = None,
                          show_grid: bool = True,
                          show_axes: bool = True) -> Dict[str, Any]:
        """
        Render the entire scene to an image file.
        
        Args:
            filename: Output image filename
            bounds: Rendering bounds
            resolution: Image resolution (width, height)
            show_grid: Whether to show grid lines
            show_axes: Whether to show axis labels
            
        Returns:
            Dict with rendering information and statistics
        """
        if bounds is None:
            bounds = self.default_bounds
        if resolution is None:
            resolution = self.default_resolution
        
        # Create figure
        fig, ax = plt.subplots(figsize=(resolution[0]/100, resolution[1]/100), dpi=100)
        
        # Set up axes
        xmin, xmax, ymin, ymax = bounds
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect('equal')
        
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        if not show_axes:
            ax.set_xticks([])
            ax.set_yticks([])
        
        # Render objects
        rendered_objects = []
        
        # First pass: Render filled regions
        region_data = self.get_region_data(bounds, (100, 100))
        for obj_id, data in region_data.items():
            if data.get('inside_mask') is not None:
                try:
                    self.plot_manager.plot_region_filled(
                        self.scene_manager.get_object(obj_id),
                        bounds, (100, 100), ax=ax,
                        **data['style']
                    )
                    rendered_objects.append({'id': obj_id, 'type': 'region'})
                except Exception as e:
                    print(f"Warning: Failed to render region '{obj_id}': {e}")
        
        # Second pass: Render curve boundaries
        curve_data = self.get_curve_paths(bounds, 200)
        for obj_id, data in curve_data.items():
            if data.get('points'):
                try:
                    points = np.array(data['points'])
                    style = data['style']
                    
                    ax.plot(points[:, 0], points[:, 1], 
                           color=style.get('color', 'blue'),
                           linewidth=style.get('linewidth', 2),
                           alpha=style.get('alpha', 1.0),
                           label=obj_id)
                    
                    rendered_objects.append({'id': obj_id, 'type': 'curve'})
                except Exception as e:
                    print(f"Warning: Failed to render curve '{obj_id}': {e}")
        
        # Add legend if there are objects
        if rendered_objects:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Save image
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Return rendering info
        return {
            'filename': filename,
            'bounds': list(bounds),
            'resolution': list(resolution),
            'rendered_objects': rendered_objects,
            'object_count': len(rendered_objects)
        }
    
    def get_scene_bounds(self, padding: float = 0.2) -> Tuple[float, float, float, float]:
        """
        Calculate optimal bounds for the current scene.
        
        Args:
            padding: Fraction of range to add as padding
            
        Returns:
            (xmin, xmax, ymin, ymax) bounds
        """
        all_bounds = []
        
        # Get bounds from all objects using curve path extraction
        for obj_id in self.scene_manager.list_objects():
            obj = self.scene_manager.get_object(obj_id)
            
            try:
                # First check if the object has manually assigned attributes xmin, xmax, ymin, ymax (e.g. loaded from DB)
                if hasattr(obj, 'xmin') and hasattr(obj, 'xmax') and hasattr(obj, 'ymin') and hasattr(obj, 'ymax'):
                    if all(getattr(obj, name) is not None and np.isfinite(float(getattr(obj, name))) for name in ['xmin', 'xmax', 'ymin', 'ymax']):
                        o_xmin, o_xmax, o_ymin, o_ymax = float(obj.xmin), float(obj.xmax), float(obj.ymin), float(obj.ymax)
                        # Skip extremely large bounds (span >= 50) like infinite vertical/horizontal lines
                        # to allow scene auto-fitting to focus tightly on the active shapes
                        if abs(o_xmax - o_xmin) < 50.0 and abs(o_ymax - o_ymin) < 50.0:
                            all_bounds.append((o_xmin, o_xmax, o_ymin, o_ymax))
                        continue

                # First try the get_bounds method if available
                if hasattr(obj, 'get_bounds'):
                    bounds = obj.get_bounds()
                    if bounds and len(bounds) == 4 and all(np.isfinite(bounds)):
                        all_bounds.append(bounds)
                        continue
                
                # Fallback: extract curve paths and calculate bounds from points
                if hasattr(obj, 'outer_boundary'):
                    # For AreaRegion objects, sample the boundary
                    points, _ = self._sample_boundary_points(obj.outer_boundary, self.default_bounds, 50)
                    if points:
                        points_array = np.array(points)
                        obj_bounds = [
                            float(np.min(points_array[:, 0])),  # xmin
                            float(np.max(points_array[:, 0])),  # xmax
                            float(np.min(points_array[:, 1])),  # ymin
                            float(np.max(points_array[:, 1]))   # ymax
                        ]
                        all_bounds.append(obj_bounds)
                        continue
                
                # Try contour extraction as another fallback
                points, _, _ = self._extract_curve_contour(obj, self.default_bounds, 50)
                if points:
                    points_array = np.array(points)
                    obj_bounds = [
                        float(np.min(points_array[:, 0])),  # xmin
                        float(np.max(points_array[:, 0])),  # xmax
                        float(np.min(points_array[:, 1])),  # ymin
                        float(np.max(points_array[:, 1]))   # ymax
                    ]
                    all_bounds.append(obj_bounds)
                    
            except Exception as e:
                # For debugging: print what went wrong
                print(f"Warning: Could not calculate bounds for '{obj_id}': {e}")
                continue
        
        if not all_bounds:
            return self._fallback_bounds
        
        # Calculate overall bounds
        all_bounds = np.array(all_bounds)
        xmin = np.min(all_bounds[:, 0])
        xmax = np.max(all_bounds[:, 1])
        ymin = np.min(all_bounds[:, 2])
        ymax = np.max(all_bounds[:, 3])
        
        # Add padding and guard against zero or infinite ranges
        if not np.isfinite(xmin) or not np.isfinite(xmax) or not np.isfinite(ymin) or not np.isfinite(ymax):
            return self._fallback_bounds

        x_range = xmax - xmin
        y_range = ymax - ymin

        if x_range <= 0 or y_range <= 0:
            return self._fallback_bounds

        x_padding = x_range * padding
        y_padding = y_range * padding
        
        return (
            xmin - x_padding,
            xmax + x_padding,
            ymin - y_padding,
            ymax + y_padding
        )

    def get_geometry_scene_data(self, resolution: int = 400, bounds: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        """Return polyline data, bounds, and key-point annotations for the scene."""

        if bounds is None:
            bounds = self.get_scene_bounds(padding=0.0)
        sanitized_bounds = self._sanitize_bounds(bounds)
        curve_data = self.get_curve_paths(bounds=sanitized_bounds, resolution=resolution)

        objects: List[Dict[str, Any]] = []
        polyline_lookup: Dict[str, List[List[float]]] = {}

        for obj_id, data in curve_data.items():
            points = data.get('points') or []
            obj = self.scene_manager.get_object(obj_id)
            sanitized_object_bounds = self._sanitize_bounds(data.get('bounds'))
            cleaned_points = [
                [float(pt[0]), float(pt[1])] for pt in points if len(pt) == 2 and np.isfinite(pt[0]) and np.isfinite(pt[1])
            ]
            polyline_lookup[obj_id] = cleaned_points

            raw_paths = data.get('paths') or []
            cleaned_paths = []
            for path in raw_paths:
                cleaned_path = [
                    [float(pt[0]), float(pt[1])] for pt in path if len(pt) == 2 and np.isfinite(pt[0]) and np.isfinite(pt[1])
                ]
                if len(cleaned_path) >= 2:
                    cleaned_paths.append(cleaned_path)

            key_points = self._extract_endpoint_points(obj, cleaned_points)

            objects.append({
                'id': obj_id,
                'type': data.get('type', 'curve'),
                'closed': bool(data.get('closed', False)),
                'points': cleaned_points,
                'paths': cleaned_paths if cleaned_paths else ([cleaned_points] if cleaned_points else []),
                'bounds': sanitized_object_bounds,
                'style': data.get('style', {}),
                'key_points': key_points,
            })

        intersections = self._compute_polyline_intersections(polyline_lookup)

        return {
            'objects': objects,
            'intersections': intersections,
            'scene_bounds': list(sanitized_bounds),
        }
    
    # ================== Helper Methods ==================

    def _estimate_object_bounds(self, obj, scene_bounds: Tuple[float, float, float, float],
                                coarse: int = 40) -> Tuple[float, float, float, float]:
        """
        Estimate tight bounds for a single object by probing on a coarse grid,
        then add padding. Falls back to scene_bounds if nothing is found.
        """
        # First check if the object has manually assigned attributes xmin, xmax, ymin, ymax (e.g. loaded from DB)
        if hasattr(obj, 'xmin') and hasattr(obj, 'xmax') and hasattr(obj, 'ymin') and hasattr(obj, 'ymax'):
            if all(getattr(obj, name) is not None and np.isfinite(float(getattr(obj, name))) for name in ['xmin', 'xmax', 'ymin', 'ymax']):
                o_xmin, o_xmax, o_ymin, o_ymax = float(obj.xmin), float(obj.xmax), float(obj.ymin), float(obj.ymax)
                s_xmin, s_xmax, s_ymin, s_ymax = scene_bounds
                
                # Check if it is an infinite/very large line (span >= 50)
                is_infinite = (abs(o_xmax - o_xmin) >= 50.0) or (abs(o_ymax - o_ymin) >= 50.0)
                
                if is_infinite:
                    # Crop dynamically to the bounds of other non-infinite curves in the active scene
                    non_inf_bounds = []
                    for other_id in self.scene_manager.list_objects():
                        other_obj = self.scene_manager.get_object(other_id)
                        if hasattr(other_obj, 'xmin') and hasattr(other_obj, 'xmax') and hasattr(other_obj, 'ymin') and hasattr(other_obj, 'ymax'):
                            if all(getattr(other_obj, name) is not None and np.isfinite(float(getattr(other_obj, name))) for name in ['xmin', 'xmax', 'ymin', 'ymax']):
                                ox_min, ox_max, oy_min, oy_max = float(other_obj.xmin), float(other_obj.xmax), float(other_obj.ymin), float(other_obj.ymax)
                                if abs(ox_max - ox_min) < 50.0 and abs(oy_max - oy_min) < 50.0:
                                    non_inf_bounds.append((ox_min, ox_max, oy_min, oy_max))
                    
                    if non_inf_bounds:
                        non_inf_bounds = np.array(non_inf_bounds)
                        c_xmin = np.min(non_inf_bounds[:, 0])
                        c_xmax = np.max(non_inf_bounds[:, 1])
                        c_ymin = np.min(non_inf_bounds[:, 2])
                        c_ymax = np.max(non_inf_bounds[:, 3])
                        
                        # Add a 50% padding relative to active cluster size
                        pad_x = max((c_xmax - c_xmin) * 0.5, 2.0)
                        pad_y = max((c_ymax - c_ymin) * 0.5, 2.0)
                        
                        # Apply crop limits
                        o_xmin = max(o_xmin, c_xmin - pad_x)
                        o_xmax = min(o_xmax, c_xmax + pad_x)
                        o_ymin = max(o_ymin, c_ymin - pad_y)
                        o_ymax = min(o_ymax, c_ymax + pad_y)

                # Intersect manual bounds with viewport/scene bounds to increase LOD when zooming
                int_xmin = max(o_xmin, s_xmin)
                int_xmax = min(o_xmax, s_xmax)
                int_ymin = max(o_ymin, s_ymin)
                int_ymax = min(o_ymax, s_ymax)
                
                if int_xmin < int_xmax and int_ymin < int_ymax:
                    # Pad by 5% of viewport width/height to avoid edge clipping issues
                    pad_x = (int_xmax - int_xmin) * 0.05
                    pad_y = (int_ymax - int_ymin) * 0.05
                    return (
                        max(o_xmin, int_xmin - pad_x),
                        min(o_xmax, int_xmax + pad_x),
                        max(o_ymin, int_ymin - pad_y),
                        min(o_ymax, int_ymax + pad_y)
                    )
                else:
                    return (o_xmin, o_xmax, o_ymin, o_ymax)


        xmin, xmax, ymin, ymax = scene_bounds
        # Coarse probe to find where the object's implicit function changes sign
        try:
            x = np.linspace(xmin, xmax, coarse)
            y = np.linspace(ymin, ymax, coarse)
            X, Y = np.meshgrid(x, y)

            if hasattr(obj, 'evaluate'):
                Z = obj.evaluate(X, Y)
            elif hasattr(obj, 'outer_boundary') and hasattr(obj.outer_boundary, 'evaluate'):
                Z = obj.outer_boundary.evaluate(X, Y)
            else:
                return scene_bounds

            if not isinstance(Z, np.ndarray):
                Z = np.array(Z)
            if Z.shape != X.shape:
                return scene_bounds

            # Find grid cells near the zero contour (sign change or near-zero)
            near_zero = np.abs(Z) < (np.nanmax(np.abs(Z)) * 0.3 + 1e-9)
            if not np.any(near_zero):
                return scene_bounds

            rows, cols = np.where(near_zero)
            ox_min = float(X[rows, cols].min())
            ox_max = float(X[rows, cols].max())
            oy_min = float(Y[rows, cols].min())
            oy_max = float(Y[rows, cols].max())

            # Pad by 20% of the object's own span (minimum 0.5 units)
            px = max((ox_max - ox_min) * 0.25, 0.5)
            py = max((oy_max - oy_min) * 0.25, 0.5)
            return (ox_min - px, ox_max + px, oy_min - py, oy_max + py)

        except Exception:
            return scene_bounds

    def _extract_curve_contour(self, obj, bounds: Tuple[float, float, float, float], 
                               resolution: int) -> Tuple[List[List[float]], bool, List[List[List[float]]]]:
        """
        Extract curve contour using matplotlib contour detection.
        
        Args:
            obj: Geometry object to extract contour from
            bounds: Sampling bounds
            resolution: Grid resolution
            
        Returns:
            (points, closed) where points is list of [x, y] coordinates
        """
        xmin, xmax, ymin, ymax = bounds
        
        # Check if periodic radical (endpoints all on y = 0)
        endpoints = getattr(obj, 'endpoints', None)
        is_periodic_radical = False
        if endpoints and len(endpoints) > 0:
            if all(abs(ep[1]) < 1e-5 for ep in endpoints):
                is_periodic_radical = True
                
        if is_periodic_radical:
            # For periodic radical curves (y² = g(x)), compute the actual Y-extent
            # by evaluating f(x,0) along the x-axis. Since f(x,y) = y² - g(x),
            # we have g(x) = -f(x,0) and max|y| = √(max(g(x))).
            # This concentrates ALL grid points in the curve's actual y-range
            # instead of wasting them on the (often huge) database bounds.
            try:
                x_probe = np.linspace(xmin, xmax, 200)
                y_zero = np.zeros_like(x_probe)
                f_at_zero = obj.evaluate(x_probe, y_zero)
                if isinstance(f_at_zero, np.ndarray):
                    g_x = -f_at_zero
                    g_max = float(np.nanmax(g_x))
                    if g_max > 0:
                        actual_ymax = np.sqrt(g_max)
                        ymax_abs = actual_ymax * 1.15  # 15% padding
                    else:
                        ymax_abs = max(abs(ymin), abs(ymax))
                else:
                    ymax_abs = max(abs(ymin), abs(ymax))
            except Exception:
                ymax_abs = max(abs(ymin), abs(ymax))
            ymin = -ymax_abs
            ymax = ymax_abs
            
        # Force odd resolution to ensure y=0 is a grid line, maximizing horizontal symmetry
        resolution = resolution | 1
        
        # Create evaluation grid
        x = np.linspace(xmin, xmax, resolution)
        y = np.linspace(ymin, ymax, resolution)
        X, Y = np.meshgrid(x, y)
        
        try:
            # Handle different object types
            if hasattr(obj, 'evaluate'):
                # Direct evaluation for curves
                Z = obj.evaluate(X, Y)
            elif hasattr(obj, 'outer_boundary') and hasattr(obj.outer_boundary, 'evaluate'):
                # For AreaRegion, use the outer_boundary curve
                Z = obj.outer_boundary.evaluate(X, Y)
            else:
                # No evaluation method available
                return [], False

            # Ensure Z has the correct shape for contour plotting
            if not isinstance(Z, np.ndarray):
                Z = np.array(Z)
            
            # Handle different shapes that might be returned
            if Z.ndim == 1:
                # Reshape 1D array to 2D grid
                Z = Z.reshape(X.shape)
            elif Z.shape != X.shape:
                # If shapes don't match, skip contour extraction
                return [], False

            # Keep raw evaluated array to detect NaN limits
            Z_raw = Z.copy()
            
            # Replace infinity and NaN values with extreme finite limits to protect Matplotlib contour
            Z = np.where(np.isnan(Z), 1e100, Z)
            Z = np.where(np.isposinf(Z), 1e100, Z)
            Z = np.where(np.isneginf(Z), -1e100, Z)
                
            # Extract zero-level contour (unmasked to avoid suppression and boundary gaps)
            import matplotlib.pyplot as plt
            with plt.ioff():  # Turn off interactive mode
                fig, ax = plt.subplots()
                contours = ax.contour(X, Y, Z, levels=[0])
                fig.clear()
                del fig, ax
            
            raw_paths = []

            # Modern matplotlib contour path extraction
            if hasattr(contours, 'get_paths') and callable(contours.get_paths):
                for path in contours.get_paths():
                    raw_paths.append((path.vertices.tolist(), path.codes))

            if not raw_paths and hasattr(contours, 'collections') and contours.collections:
                for collection in contours.collections:
                    for path in collection.get_paths():
                        raw_paths.append((path.vertices.tolist(), path.codes))

            if not raw_paths and hasattr(contours, 'allsegs'):
                for level_segments in contours.allsegs:
                    for seg in level_segments:
                        if len(seg) >= 2:
                            raw_paths.append((seg.tolist(), None))

            # Post-filter paths with the TrimmedImplicitCurve mask and explicit bounds
            # to achieve smooth, gap-free termination at boundaries
            candidate_paths = []
            
            obj_xmin = getattr(obj, '_xmin', None)
            obj_xmax = getattr(obj, '_xmax', None)
            obj_ymin = getattr(obj, '_ymin', None)
            obj_ymax = getattr(obj, '_ymax', None)
            eps = 1e-9
            
            def in_bounds(px, py):
                if obj_xmin is not None and px < obj_xmin - eps:
                    return False
                if obj_xmax is not None and px > obj_xmax + eps:
                    return False
                if obj_ymin is not None and py < obj_ymin - eps:
                    return False
                if obj_ymax is not None and py > obj_ymax + eps:
                    return False
                return True

            has_mask = hasattr(obj, 'mask') and callable(obj.mask)

            for points_list, codes in raw_paths:
                mask_bools = []
                if has_mask:
                    try:
                        # Try vectorized mask check first
                        xs = [p[0] for p in points_list]
                        ys = [p[1] for p in points_list]
                        mask_bools = obj.mask(np.array(xs), np.array(ys))
                        if not isinstance(mask_bools, np.ndarray):
                            mask_bools = [bool(mask_bools)] * len(points_list)
                        else:
                            mask_bools = mask_bools.tolist()
                    except Exception:
                        mask_bools = []
                        for px, py in points_list:
                            try:
                                mask_bools.append(bool(obj.mask(px, py)))
                            except Exception:
                                mask_bools.append(True)
                else:
                    mask_bools = [True] * len(points_list)
                
                # Vectorized validation of points against original NaN/boundary artifacts
                try:
                    xs_eval = np.array([p[0] for p in points_list], dtype=float)
                    ys_eval = np.array([p[1] for p in points_list], dtype=float)
                    vals = obj.evaluate(xs_eval, ys_eval)
                    valid_mask = ~np.isnan(vals) & ~np.isinf(vals)
                    if np.any(np.isnan(Z_raw)):
                        valid_mask &= (np.abs(vals) <= 0.15)
                    valid_list = valid_mask.tolist()
                except Exception:
                    valid_list = [True] * len(points_list)
                
                # Split paths if mask splits them or a new subpath starts (MOVETO code)
                current_subpath = []
                for idx, (pt, mask_ok) in enumerate(zip(points_list, mask_bools)):
                    is_moveto = (codes is not None and idx < len(codes) and codes[idx] == 1)
                    if mask_ok and in_bounds(pt[0], pt[1]) and valid_list[idx] and not is_moveto:
                        current_subpath.append(pt)
                    else:
                        if len(current_subpath) >= 2:
                            candidate_paths.append((current_subpath, None))
                        current_subpath = []
                        if mask_ok and in_bounds(pt[0], pt[1]) and valid_list[idx]:
                            current_subpath.append(pt)
                if len(current_subpath) >= 2:
                    candidate_paths.append((current_subpath, None))

            all_paths = [item[0] for item in candidate_paths if len(item[0]) >= 2]

            # For curves like periodic_radical where endpoints are zero-crossings at y = 0,
            # split closed loops at y = 0 into open branches so they snap perfectly and symmetrically.
            endpoints = getattr(obj, 'endpoints', None)
            is_periodic_radical = False
            if endpoints and len(endpoints) > 0:
                if all(abs(ep[1]) < 1e-5 for ep in endpoints):
                    is_periodic_radical = True

            if is_periodic_radical:
                split_paths = []
                for path in all_paths:
                    if len(path) < 2:
                        continue
                    
                    is_path_closed = np.allclose(path[0], path[-1], atol=1e-6)
                    rotated_path = path
                    if is_path_closed:
                        # Find a sign change/zero crossing in Y to rotate path start/end to a crossing point
                        rotate_idx = -1
                        for i in range(len(path) - 1):
                            if path[i][1] * path[i+1][1] < 0 or abs(path[i][1]) < 1e-9:
                                rotate_idx = i
                                break
                        if rotate_idx != -1:
                            rotated_path = path[rotate_idx+1:-1] + path[0:rotate_idx+2]
                            
                    # Robust sign-state tracking splitter to partition cleanly at y = 0
                    def get_sign(val):
                        if val > 1e-9: return 1
                        if val < -1e-9: return -1
                        return 0
                        
                    current_sub = [rotated_path[0]]
                    current_sign = get_sign(rotated_path[0][1])
                    
                    for i in range(1, len(rotated_path)):
                        curr_pt = rotated_path[i]
                        curr_sign = get_sign(curr_pt[1])
                        
                        if curr_sign != 0 and current_sign != 0 and curr_sign != current_sign:
                            # Strict sign change
                            current_sub.append(curr_pt)
                            if len(current_sub) >= 2:
                                split_paths.append(current_sub)
                            current_sub = [curr_pt]
                            current_sign = curr_sign
                        elif curr_sign == 0:
                            # Hitting exactly 0!
                            current_sub.append(curr_pt)
                            if len(current_sub) >= 2:
                                split_paths.append(current_sub)
                            current_sub = [curr_pt]
                            current_sign = 0
                        else:
                            current_sub.append(curr_pt)
                            if current_sign == 0:
                                current_sign = curr_sign
                                
                    if len(current_sub) >= 2:
                        split_paths.append(current_sub)
                all_paths = split_paths

            if all_paths:
                points = max(all_paths, key=len)
                closed = False
                if not is_periodic_radical and candidate_paths:
                    # Retrieve the original codes/closed flag for non-periodic curves
                    orig_points, codes = max(candidate_paths, key=lambda item: len(item[0]))
                    if codes is not None and len(codes) > 0:
                        closed = codes[-1] == 79  # CLOSEPOLY
                    elif len(points) >= 2:
                        first = points[0]
                        last = points[-1]
                        closed = np.allclose(first, last, atol=1e-6)
                return points, closed, all_paths

        except Exception as e:
            print(f"Contour extraction failed: {e}")
        
        return [], False, []

    def _sanitize_bounds(self, bounds: Optional[Union[List[float], Tuple[float, float, float, float]]]) -> Tuple[float, float, float, float]:
        """Ensure bounds are finite; otherwise return fallback defaults."""

# ... (rest of the code remains the same)
        if bounds is None or len(bounds) != 4:
            return self._fallback_bounds
        xmin, xmax, ymin, ymax = bounds
        values = np.array([xmin, xmax, ymin, ymax], dtype=float)
        if not np.isfinite(values).all():
            return self._fallback_bounds
        if xmin == xmax or ymin == ymax:
            return self._fallback_bounds
        return float(xmin), float(xmax), float(ymin), float(ymax)

    def _extract_endpoint_points(self, obj, polyline: List[List[float]]) -> List[Dict[str, Any]]:
        """Return labeled key points (endpoints/intersections placeholders)."""

        key_points: List[Dict[str, Any]] = []
        label_seed = ord('A')

        if hasattr(obj, 'get_endpoints'):
            try:
                endpoints = obj.get_endpoints()
            except Exception:
                endpoints = []
            for idx, pt in enumerate(endpoints or []):
                if len(pt) != 2 or not np.isfinite(pt[0]) or not np.isfinite(pt[1]):
                    continue
                key_points.append({
                    'type': 'endpoint',
                    'label': chr(label_seed + idx),
                    'x': float(pt[0]),
                    'y': float(pt[1]),
                })

        # Fallback 1: If we have exactly 1 analytical endpoint and the curve is open (not closed),
        # append the polyline boundary extremity that is far from that analytical endpoint.
        closed_attr = getattr(obj, 'is_closed', False)
        closed = closed_attr() if callable(closed_attr) else bool(closed_attr)
        if not closed and len(key_points) == 1 and len(polyline) >= 2:
            existing_pt = (key_points[0]['x'], key_points[0]['y'])
            first = polyline[0]
            last = polyline[-1]
            # Calculate squared distance from analytical endpoint to first and last polyline points
            d_first = (first[0] - existing_pt[0])**2 + (first[1] - existing_pt[1])**2
            d_last = (last[0] - existing_pt[0])**2 + (last[1] - existing_pt[1])**2
            
            # Select the boundary point that is further away
            if d_first > d_last:
                if d_first > 1e-4:
                    key_points.append({
                        'type': 'endpoint',
                        'label': chr(label_seed + len(key_points)),
                        'x': float(first[0]),
                        'y': float(first[1])
                    })
            else:
                if d_last > 1e-4:
                    key_points.append({
                        'type': 'endpoint',
                        'label': chr(label_seed + len(key_points)),
                        'x': float(last[0]),
                        'y': float(last[1])
                    })

        # Fallback 2: use polyline start/end if we still have no key points
        if not key_points and len(polyline) >= 2:
            first = polyline[0]
            last = polyline[-1]
            key_points.append({'type': 'endpoint', 'label': 'A', 'x': first[0], 'y': first[1]})
            key_points.append({'type': 'endpoint', 'label': 'B', 'x': last[0], 'y': last[1]})

        return key_points

    def _compute_polyline_intersections(self, polyline_lookup: Dict[str, List[List[float]]]) -> List[Dict[str, Any]]:
        """Detect approximate intersections between polylines using segment checks."""

        # Subsample each polyline to at most 60 points for intersection detection
        MAX_SEGS = 60
        def _subsample(pts):
            if len(pts) <= MAX_SEGS + 1:
                return pts
            step = len(pts) / MAX_SEGS
            return [pts[int(i * step)] for i in range(MAX_SEGS)] + [pts[-1]]

        raw: List[Tuple[float, float]] = []

        for (id_a, pts_a), (id_b, pts_b) in combinations(polyline_lookup.items(), 2):
            segs_a = self._polyline_segments(_subsample(pts_a))
            segs_b = self._polyline_segments(_subsample(pts_b))
            for seg_a in segs_a:
                for seg_b in segs_b:
                    result = self._segment_intersection(seg_a, seg_b)
                    if result is not None:
                        raw.append(result)

        # Deduplicate: cluster points within tolerance, keep one per cluster
        TOL = 0.05
        kept: List[Tuple[float, float]] = []
        for pt in raw:
            if not any(abs(pt[0] - k[0]) < TOL and abs(pt[1] - k[1]) < TOL for k in kept):
                kept.append(pt)

        return [
            {'label': f'I{i + 1}', 'x': float(x), 'y': float(y)}
            for i, (x, y) in enumerate(kept)
        ]

    def _polyline_segments(self, points: List[List[float]]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        if len(points) < 2:
            return segments
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            if np.isfinite(p1[0]) and np.isfinite(p1[1]) and np.isfinite(p2[0]) and np.isfinite(p2[1]):
                segments.append(((p1[0], p1[1]), (p2[0], p2[1])))
        return segments

    def _segment_intersection(self, seg_a, seg_b) -> Optional[Tuple[float, float]]:
        (x1, y1), (x2, y2) = seg_a
        (x3, y3), (x4, y4) = seg_b

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-9:
            return None

        px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

        if self._point_on_segment(px, py, seg_a) and self._point_on_segment(px, py, seg_b):
            return float(px), float(py)
        return None

    def _point_on_segment(self, px: float, py: float, segment) -> bool:
        (x1, y1), (x2, y2) = segment
        if (min(x1, x2) - 1e-6) <= px <= (max(x1, x2) + 1e-6) and (min(y1, y2) - 1e-6) <= py <= (max(y1, y2) + 1e-6):
            # Check collinearity via cross product
            cross = (px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)
            return abs(cross) <= 1e-3
        return False
    
    def _sample_boundary_points(self, boundary_curve, bounds: Tuple[float, float, float, float], 
                               resolution: int) -> Tuple[List[List[float]], bool]:
        """
        Sample points along a boundary curve as fallback when contour extraction fails.
        
        Args:
            boundary_curve: The boundary curve to sample
            bounds: Sampling bounds
            resolution: Number of points to sample
            
        Returns:
            (points, closed) where points is list of [x, y] coordinates
        """
        try:
            xmin, xmax, ymin, ymax = bounds
            
            # First try specialized handling for known curve types
            if hasattr(boundary_curve, '_is_square') and boundary_curve._is_square:
                # Rectangle boundary
                bounds_rect = boundary_curve._square_bounds
                xmin_r, xmax_r, ymin_r, ymax_r = bounds_rect
                points = [
                    [xmin_r, ymin_r], [xmax_r, ymin_r], 
                    [xmax_r, ymax_r], [xmin_r, ymax_r], 
                    [xmin_r, ymin_r]  # Close the rectangle
                ]
                return points, True
            
            # For circles and other curves, use a more robust approach
            # Try parametric sampling if available
            if hasattr(boundary_curve, 'get_parametric_points'):
                try:
                    points = boundary_curve.get_parametric_points(resolution)
                    if points and len(points) > 2:
                        return points, True
                except Exception:
                    pass
            
            # Fallback: Use a finer grid to find boundary points
            grid_res = max(50, resolution // 2)  # Use finer grid
            x_vals = np.linspace(xmin, xmax, grid_res)
            y_vals = np.linspace(ymin, ymax, grid_res)
            
            points = []
            tolerance = 0.2  # More lenient tolerance
            
            # Sample boundary points by finding points close to zero level
            for x in x_vals:
                for y in y_vals:
                    try:
                        val = boundary_curve.evaluate(x, y)
                        if isinstance(val, (list, np.ndarray)):
                            val = val[0] if len(val) > 0 else float('inf')
                        if abs(val) < tolerance:  # Close to boundary
                            points.append([float(x), float(y)])
                    except:
                        continue
            
            # If we found some boundary points, return them
            if len(points) > 2:
                return points, True  # Assume closed for regions
            
            # Last resort: Create a rough bounding box approximation
            # This ensures we at least get some bounds for the object
            center_x = (xmin + xmax) / 2
            center_y = (ymin + ymax) / 2
            
            # Try to find a reasonable size by testing a few points
            test_points = [
                (center_x, center_y),
                (center_x + 1, center_y),
                (center_x - 1, center_y),
                (center_x, center_y + 1),
                (center_x, center_y - 1)
            ]
            
            valid_points = []
            for x, y in test_points:
                try:
                    val = boundary_curve.evaluate(x, y)
                    if isinstance(val, (list, np.ndarray)):
                        val = val[0] if len(val) > 0 else float('inf')
                    if abs(val) < 1.0:  # Very lenient
                        valid_points.append([float(x), float(y)])
                except:
                    continue
            
            if valid_points:
                return valid_points, False
            
        except Exception as e:
            print(f"Boundary sampling failed: {e}")
        
        return [], False
    
    def get_object_info(self, obj_id: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a specific object.
        
        Args:
            obj_id: Object identifier
            
        Returns:
            Dict with object information
        """
        try:
            obj = self.scene_manager.get_object(obj_id)
            style = self.scene_manager.get_style(obj_id)
            
            info = {
                'id': obj_id,
                'type': type(obj).__name__,
                'style': style
            }
            
            # Add parameter information if available
            if hasattr(obj, 'list_parameters'):
                try:
                    parameters = obj.get_parameters()
                    info['parameters'] = parameters
                    info['parameter_names'] = obj.list_parameters()
                except Exception:
                    pass
            
            # Add bounds if available
            if hasattr(obj, 'get_bounds'):
                try:
                    bounds = obj.get_bounds()
                    if bounds:
                        info['bounds'] = bounds
                except Exception:
                    pass
            
            # Add dependencies
            deps = self.scene_manager.get_dependencies(obj_id)
            if deps['dependents'] or deps['sources']:
                info['dependencies'] = deps
            
            return info
            
        except Exception as e:
            return {
                'id': obj_id,
                'error': str(e)
            }
    
    def get_scene_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the entire scene.
        
        Returns:
            Dict with scene statistics and information
        """
        objects = self.scene_manager.list_objects()
        
        # Count object types
        type_counts = {}
        for obj_id in objects:
            try:
                obj = self.scene_manager.get_object(obj_id)
                obj_type = type(obj).__name__
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            except Exception:
                continue
        
        # Get animation cache info
        cache_info = self.scene_manager.get_animation_cache_info()
        total_cache_size = sum(info['cache_size_mb'] for info in cache_info.values())
        
        # Calculate scene bounds
        scene_bounds = self.get_scene_bounds()
        
        return {
            'object_count': len(objects),
            'object_types': type_counts,
            'group_count': len(self.scene_manager._groups),
            'dependency_count': len(self.scene_manager._dependencies),
            'animation_cache_count': len(cache_info),
            'total_cache_size_mb': total_cache_size,
            'scene_bounds': scene_bounds,
            'objects': objects
        }
