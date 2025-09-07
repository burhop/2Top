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
                # Generate polyline approximation
                if hasattr(obj, 'get_polyline_approximation'):
                    # Use object's built-in approximation if available
                    points = obj.get_polyline_approximation(bounds, resolution)
                    closed = getattr(obj, 'is_closed', lambda: False)()
                else:
                    # Try contour extraction, with fallback to boundary sampling
                    points, closed = self._extract_curve_contour(obj, bounds, resolution)
                    
                    # If contour extraction failed, try boundary sampling for AreaRegion
                    if not points and hasattr(obj, 'outer_boundary'):
                        points, closed = self._sample_boundary_points(obj.outer_boundary, bounds, resolution)
                
                if points and len(points) > 1:
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
                points, _ = self._extract_curve_contour(obj, self.default_bounds, 50)
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
            return self.default_bounds
        
        # Calculate overall bounds
        all_bounds = np.array(all_bounds)
        xmin = np.min(all_bounds[:, 0])
        xmax = np.max(all_bounds[:, 1])
        ymin = np.min(all_bounds[:, 2])
        ymax = np.max(all_bounds[:, 3])
        
        # Add padding
        x_range = xmax - xmin
        y_range = ymax - ymin
        x_padding = x_range * padding
        y_padding = y_range * padding
        
        return (
            xmin - x_padding,
            xmax + x_padding,
            ymin - y_padding,
            ymax + y_padding
        )
    
    # ================== Helper Methods ==================
    
    def _extract_curve_contour(self, obj, bounds: Tuple[float, float, float, float], 
                              resolution: int) -> Tuple[List[List[float]], bool]:
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
            
            # Extract zero-level contour
            import matplotlib.pyplot as plt
            # Create figure without interfering with main rendering
            with plt.ioff():  # Turn off interactive mode
                fig, ax = plt.subplots()
                contours = ax.contour(X, Y, Z, levels=[0])
                # Clear figure without calling plt.close to avoid mock interference
                fig.clear()
                del fig, ax
            
            if contours.collections:
                # Get the longest contour path
                paths = contours.collections[0].get_paths()
                if paths:
                    longest_path = max(paths, key=lambda p: len(p.vertices))
                    points = longest_path.vertices.tolist()
                    closed = longest_path.codes is not None and longest_path.codes[-1] == 79  # CLOSEPOLY
                    return points, closed
            
        except Exception as e:
            print(f"Contour extraction failed: {e}")
        
        return [], False
    
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
