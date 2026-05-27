"""
Graphics Backend Interface for 2Top Geometry Library

Provides structured, render-ready data extraction from SceneManager for
front-end applications, web interfaces, and visualization tools.
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Any, Optional, Union
from itertools import combinations
import matplotlib

# Use non-interactive backend to avoid Tkinter main-loop issues in tests/servers
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from scene_management import SceneManager
from visual_tests.utils.grid_evaluation import GridEvaluator
from visual_tests.utils import PlotManager

try:
    from geometry.base_field import BaseField
except ImportError:
    BaseField = None

_cached_fig = None
_cached_ax = None


def _get_cached_contour_axes():
    global _cached_fig, _cached_ax
    if _cached_fig is None:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as _plt

        _cached_fig, _cached_ax = _plt.subplots(figsize=(1, 1), dpi=10)
    else:
        _cached_ax.clear()
    return _cached_fig, _cached_ax


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
        self.plot_manager = PlotManager()

        # Default rendering settings
        self.default_resolution = (800, 600)
        self.default_bounds = (-5, 5, -5, 5)  # xmin, xmax, ymin, ymax
        self.default_grid_resolution = 100
        self._fallback_bounds = (-5.0, 5.0, -5.0, 5.0)

    # ================== Curve Data Extraction ==================

    def get_curve_paths(
        self,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: int = 200,
    ) -> Dict[str, Dict]:
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

            # Fields do not have physical line/contour paths or outlines to render
            if BaseField is not None and isinstance(obj, BaseField):
                curve_data[obj_id] = {
                    "type": "field",
                    "points": [],
                    "paths": [],
                    "closed": False,
                    "style": style or {},
                    "bounds": [0.0, 0.0, 0.0, 0.0],
                }
                continue

            try:
                # Use per-object local bounds so small objects aren't evaluated on a
                # huge global grid (which produces degenerate/line contours).
                obj_bounds = self._estimate_object_bounds(obj, bounds)

                paths = []
                # Generate polyline approximation
                if hasattr(obj, "get_polyline_approximation"):
                    # Use object's built-in approximation if available
                    points = obj.get_polyline_approximation(obj_bounds, resolution)
                    closed = getattr(obj, "is_closed", lambda: False)()
                    paths = [points] if points else []
                elif hasattr(obj, "outer_boundary") or hasattr(obj, "segments"):
                    # AreaRegion or CompositeCurve: sample boundary points directly for perfect sharp corners and speed!
                    boundary_curve = getattr(obj, "outer_boundary", obj)

                    if hasattr(boundary_curve, "segments"):
                        # Sample each segment individually to avoid spurious connecting lines
                        paths = []
                        points = []
                        num_segs = len(boundary_curve.segments)
                        pts_per_seg = max(5, resolution // num_segs)
                        for segment in boundary_curve.segments:
                            seg_pts = []
                            is_curved = getattr(segment, "is_curved", True)
                            if callable(is_curved):
                                is_curved = is_curved()
                            if is_curved and hasattr(
                                segment, "get_polyline_approximation"
                            ):
                                try:
                                    try:
                                        pts = segment.get_polyline_approximation(
                                            obj_bounds, pts_per_seg
                                        )
                                    except TypeError:
                                        pts = segment.get_polyline_approximation(
                                            resolution=pts_per_seg
                                        )
                                    if pts:
                                        seg_pts = [
                                            [float(p[0]), float(p[1])] for p in pts
                                        ]
                                except Exception:
                                    pass
                            if not seg_pts and hasattr(segment, "get_endpoints"):
                                try:
                                    endpoints = segment.get_endpoints()
                                    if endpoints and len(endpoints) == 2:
                                        (x0, y0), (x1, y1) = endpoints
                                        for t in np.linspace(0, 1, pts_per_seg):
                                            seg_pts.append(
                                                [
                                                    float(x0 + t * (x1 - x0)),
                                                    float(y0 + t * (y1 - y0)),
                                                ]
                                            )
                                except Exception:
                                    pass
                            if not seg_pts:
                                try:
                                    bbox = segment.bounding_box()
                                    s_xmin, s_xmax, s_ymin, s_ymax = bbox
                                    for t in np.linspace(0, 1, pts_per_seg):
                                        seg_pts.append(
                                            [
                                                float(s_xmin + t * (s_xmax - s_xmin)),
                                                float(s_ymin + t * (s_ymax - s_ymin)),
                                            ]
                                        )
                                except Exception:
                                    pass
                            if seg_pts:
                                paths.append(seg_pts)
                                points.extend(seg_pts)
                    else:
                        points, _ = self._sample_boundary_points(
                            boundary_curve, obj_bounds, resolution
                        )
                        paths = [points] if points else []

                    # Determine if it's closed
                    closed = False
                    if hasattr(obj, "is_closed"):
                        if callable(obj.is_closed):
                            closed = obj.is_closed()
                        else:
                            closed = bool(obj.is_closed)
                    elif hasattr(boundary_curve, "is_closed"):
                        if callable(boundary_curve.is_closed):
                            closed = boundary_curve.is_closed()
                        else:
                            closed = bool(boundary_curve.is_closed)
                    else:
                        closed = hasattr(
                            obj, "outer_boundary"
                        )  # AreaRegions are always closed
                else:
                    # Try contour extraction, with fallback to boundary sampling
                    points, closed, paths = self._extract_curve_contour(
                        obj, obj_bounds, resolution
                    )

                    # If contour extraction failed, try boundary sampling for AreaRegion
                    if not points and hasattr(obj, "outer_boundary"):
                        points, closed = self._sample_boundary_points(
                            obj.outer_boundary, obj_bounds, resolution
                        )
                        paths = [points] if points else []

                if points and len(points) > 1:
                    # Snapping open curves to mathematically exact endpoints to avoid early-termination visual gaps
                    if hasattr(obj, "get_endpoints") and not closed:
                        try:
                            endpoints = obj.get_endpoints(
                                xmin=obj_bounds[0], xmax=obj_bounds[1]
                            )
                            if endpoints and len(endpoints) > 0:
                                o_xmin, o_xmax, o_ymin, o_ymax = obj_bounds
                                grid_spacing = max(
                                    (o_xmax - o_xmin) / resolution,
                                    (o_ymax - o_ymin) / resolution,
                                )

                                is_periodic, cy_val, H_coeff = (
                                    self._is_periodic_radical(obj)
                                )
                                if is_periodic:
                                    snap_threshold = 3.0 * grid_spacing
                                else:
                                    # Extract scale_hint safely
                                    scale_hint = 1.0
                                    if (
                                        hasattr(obj, "scale_hint")
                                        and obj.scale_hint is not None
                                    ):
                                        sh = obj.scale_hint
                                        scale_hint = float(sh() if callable(sh) else sh)
                                    elif (
                                        hasattr(obj, "base_curve")
                                        and obj.base_curve is not None
                                        and hasattr(obj.base_curve, "scale_hint")
                                        and obj.base_curve.scale_hint is not None
                                    ):
                                        sh = obj.base_curve.scale_hint
                                        scale_hint = float(sh() if callable(sh) else sh)
                                    snap_threshold = max(
                                        0.1 * scale_hint, 3.0 * grid_spacing
                                    )

                                sq_threshold = snap_threshold**2
                                # Snap start and end of all paths in paths to their closest exact endpoints
                                snapped_indices = set()
                                for path in paths:
                                    if len(path) >= 2:
                                        # Snap start of the path
                                        p_start = path[0]
                                        best_ep_start = None
                                        min_d_start = float("inf")
                                        for ep in endpoints:
                                            d = (ep[0] - p_start[0]) ** 2 + (
                                                ep[1] - p_start[1]
                                            ) ** 2
                                            if d < min_d_start:
                                                min_d_start = d
                                                best_ep_start = ep
                                        if best_ep_start is not None:
                                            dx = abs(best_ep_start[0] - p_start[0])
                                            dy = abs(best_ep_start[1] - p_start[1])
                                            if (
                                                min_d_start < sq_threshold
                                                or dx < 1.5 * grid_spacing
                                                or dy < 1.5 * grid_spacing
                                            ):
                                                path[0] = [
                                                    float(best_ep_start[0]),
                                                    float(best_ep_start[1]),
                                                ]
                                                for idx, ep in enumerate(endpoints):
                                                    if ep is best_ep_start:
                                                        snapped_indices.add(idx)

                                        # Snap end of the path
                                        p_end = path[-1]
                                        best_ep_end = None
                                        min_d_end = float("inf")
                                        for ep in endpoints:
                                            d = (ep[0] - p_end[0]) ** 2 + (
                                                ep[1] - p_end[1]
                                            ) ** 2
                                            if d < min_d_end:
                                                min_d_end = d
                                                best_ep_end = ep
                                        if best_ep_end is not None:
                                            dx = abs(best_ep_end[0] - p_end[0])
                                            dy = abs(best_ep_end[1] - p_end[1])
                                            if (
                                                min_d_end < sq_threshold
                                                or dx < 1.5 * grid_spacing
                                                or dy < 1.5 * grid_spacing
                                            ):
                                                path[-1] = [
                                                    float(best_ep_end[0]),
                                                    float(best_ep_end[1]),
                                                ]
                                                for idx, ep in enumerate(endpoints):
                                                    if ep is best_ep_end:
                                                        snapped_indices.add(idx)

                                # Also snap the primary points list
                                if points and len(points) >= 2:
                                    # Snap start of points
                                    p_start = points[0]
                                    best_ep_start = None
                                    min_d_start = float("inf")
                                    for ep in endpoints:
                                        d = (ep[0] - p_start[0]) ** 2 + (
                                            ep[1] - p_start[1]
                                        ) ** 2
                                        if d < min_d_start:
                                            min_d_start = d
                                            best_ep_start = ep
                                    if best_ep_start is not None:
                                        dx = abs(best_ep_start[0] - p_start[0])
                                        dy = abs(best_ep_start[1] - p_start[1])
                                        if (
                                            min_d_start < sq_threshold
                                            or dx < 1.5 * grid_spacing
                                            or dy < 1.5 * grid_spacing
                                        ):
                                            points[0] = [
                                                float(best_ep_start[0]),
                                                float(best_ep_start[1]),
                                            ]
                                            for idx, ep in enumerate(endpoints):
                                                if ep is best_ep_start:
                                                    snapped_indices.add(idx)

                                    # Snap end of points
                                    p_end = points[-1]
                                    best_ep_end = None
                                    min_d_end = float("inf")
                                    for ep in endpoints:
                                        d = (ep[0] - p_end[0]) ** 2 + (
                                            ep[1] - p_end[1]
                                        ) ** 2
                                        if d < min_d_end:
                                            min_d_end = d
                                            best_ep_end = ep
                                    if best_ep_end is not None:
                                        dx = abs(best_ep_end[0] - p_end[0])
                                        dy = abs(best_ep_end[1] - p_end[1])
                                        if (
                                            min_d_end < sq_threshold
                                            or dx < 1.5 * grid_spacing
                                            or dy < 1.5 * grid_spacing
                                        ):
                                            points[-1] = [
                                                float(best_ep_end[0]),
                                                float(best_ep_end[1]),
                                            ]
                                            for idx, ep in enumerate(endpoints):
                                                if ep is best_ep_end:
                                                    snapped_indices.add(idx)

                                # Add micro-paths for unsnapped endpoints within bounds
                                for idx, ep in enumerate(endpoints):
                                    if idx not in snapped_indices:
                                        if (
                                            o_xmin - 1e-4 <= ep[0] <= o_xmax + 1e-4
                                        ) and (o_ymin - 1e-4 <= ep[1] <= o_ymax + 1e-4):
                                            delta = 1e-6
                                            micro_path = [
                                                [
                                                    float(ep[0]) - delta,
                                                    float(ep[1]) - delta,
                                                ],
                                                [
                                                    float(ep[0]) + delta,
                                                    float(ep[1]) + delta,
                                                ],
                                            ]
                                            paths.append(micro_path)
                        except Exception as snap_err:
                            print(
                                f"Warning: Failed endpoint snapping for '{obj_id}': {snap_err}"
                            )
                elif not points or len(points) <= 1:
                    # If points is empty or degenerate, but it has endpoints, initialize points and paths
                    if hasattr(obj, "get_endpoints") and not closed:
                        try:
                            endpoints = obj.get_endpoints(
                                xmin=obj_bounds[0], xmax=obj_bounds[1]
                            )
                            if endpoints and len(endpoints) > 0:
                                o_xmin, o_xmax, o_ymin, o_ymax = obj_bounds
                                for ep in endpoints:
                                    if (o_xmin - 1e-4 <= ep[0] <= o_xmax + 1e-4) and (
                                        o_ymin - 1e-4 <= ep[1] <= o_ymax + 1e-4
                                    ):
                                        delta = 1e-6
                                        micro_path = [
                                            [
                                                float(ep[0]) - delta,
                                                float(ep[1]) - delta,
                                            ],
                                            [
                                                float(ep[0]) + delta,
                                                float(ep[1]) + delta,
                                            ],
                                        ]
                                        paths.append(micro_path)
                                if paths:
                                    points = paths[0]
                        except Exception as ep_err:
                            pass

                # Calculate actual bounds of the curve
                if points and len(points) > 0:
                    points_array = np.array(points)
                    curve_bounds = [
                        float(np.min(points_array[:, 0])),  # xmin
                        float(np.max(points_array[:, 0])),  # xmax
                        float(np.min(points_array[:, 1])),  # ymin
                        float(np.max(points_array[:, 1])),  # ymax
                    ]
                else:
                    curve_bounds = list(bounds)

                curve_data[obj_id] = {
                    "type": "curve",
                    "points": points,
                    "paths": paths if paths else ([points] if points else []),
                    "closed": closed,
                    "style": style,
                    "bounds": curve_bounds,
                    "point_count": len(points),
                }

            except Exception as e:
                print(f"Warning: Failed to extract curve data for '{obj_id}': {e}")
                # Provide fallback data
                curve_data[obj_id] = {
                    "type": "curve",
                    "points": [],
                    "closed": False,
                    "style": style,
                    "bounds": list(bounds),
                    "error": str(e),
                }

        return curve_data

    def get_field_data(
        self,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: Tuple[int, int] = None,
    ) -> Dict[str, Dict]:
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
                if hasattr(obj, "evaluate"):
                    # Direct evaluation for curves
                    Z = obj.evaluate(X, Y)
                elif hasattr(obj, "outer_boundary") and hasattr(
                    obj.outer_boundary, "evaluate"
                ):
                    # For AreaRegion, use the outer_boundary curve
                    Z = obj.outer_boundary.evaluate(X, Y)
                else:
                    # Objects that can't be evaluated get an error entry
                    field_data[obj_id] = {
                        "type": "field",
                        "bounds": list(bounds),
                        "resolution": list(resolution),
                        "style": style,
                        "error": f"Object type {type(obj).__name__} does not support field evaluation",
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
                            "type": "field",
                            "bounds": list(bounds),
                            "resolution": list(resolution),
                            "style": style,
                            "error": f"Shape mismatch: expected {X.shape}, got {Z.shape}, sizes: {X.size} vs {Z.size}",
                        }
                        continue

                # Calculate statistics
                finite_mask = np.isfinite(Z)
                if np.any(finite_mask):
                    finite_values = Z[finite_mask]
                    stats = {
                        "min": float(np.min(finite_values)),
                        "max": float(np.max(finite_values)),
                        "mean": float(np.mean(finite_values)),
                        "std": float(np.std(finite_values)),
                        "finite_count": int(np.sum(finite_mask)),
                        "total_count": int(Z.size),
                    }
                else:
                    stats = {
                        "min": 0.0,
                        "max": 0.0,
                        "mean": 0.0,
                        "std": 0.0,
                        "finite_count": 0,
                        "total_count": int(Z.size),
                    }

                field_data[obj_id] = {
                    "type": "field",
                    "data": Z.tolist(),  # Convert to JSON-serializable format
                    "bounds": list(bounds),
                    "resolution": list(resolution),
                    "style": style,
                    "statistics": stats,
                }

            except Exception as e:
                print(f"Warning: Failed to extract field data for '{obj_id}': {e}")
                field_data[obj_id] = {
                    "type": "field",
                    "data": None,
                    "bounds": list(bounds),
                    "resolution": list(resolution),
                    "style": style,
                    "error": str(e),
                }

        return field_data

    def get_region_data(
        self,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: Tuple[int, int] = None,
    ) -> Dict[str, Dict]:
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
                if hasattr(obj, "contains"):
                    # Use GridEvaluator to compute masks
                    X, Y = self.grid_evaluator.create_grid(bounds, resolution[0])
                    inside_mask, boundary_mask = (
                        self.grid_evaluator.evaluate_region_containment(
                            obj, X, Y, test_boundary=True, handle_errors=True
                        )
                    )

                    # Calculate statistics
                    inside_count = int(np.sum(inside_mask))
                    boundary_count = int(np.sum(boundary_mask))
                    total_count = int(inside_mask.size)

                    stats = {
                        "inside_count": inside_count,
                        "boundary_count": boundary_count,
                        "total_count": total_count,
                        "inside_percentage": 100.0 * inside_count / total_count,
                        "boundary_percentage": 100.0 * boundary_count / total_count,
                    }

                    region_data[obj_id] = {
                        "type": "region",
                        "inside_mask": inside_mask.tolist(),
                        "boundary_mask": boundary_mask.tolist(),
                        "bounds": list(bounds),
                        "resolution": list(resolution),
                        "style": style,
                        "statistics": stats,
                    }

            except Exception as e:
                print(f"Warning: Failed to extract region data for '{obj_id}': {e}")
                region_data[obj_id] = {
                    "type": "region",
                    "inside_mask": None,
                    "boundary_mask": None,
                    "bounds": list(bounds),
                    "resolution": list(resolution),
                    "style": style,
                    "error": str(e),
                }

        return region_data

    # ================== Rendering Services ==================

    def render_scene_image(
        self,
        filename: str,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: Tuple[int, int] = None,
        show_grid: bool = True,
        show_axes: bool = True,
    ) -> Dict[str, Any]:
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
        fig, ax = plt.subplots(
            figsize=(resolution[0] / 100, resolution[1] / 100), dpi=100
        )

        # Set up axes
        xmin, xmax, ymin, ymax = bounds
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect("equal")

        if show_grid:
            ax.grid(True, alpha=0.3)

        if not show_axes:
            ax.set_xticks([])
            ax.set_yticks([])

        # Render objects
        rendered_objects = []

        # First pass: Render filled regions
        region_data = self.get_region_data(bounds, (100, 100))
        if region_data:
            xmin, xmax, ymin, ymax = bounds
            x = np.linspace(xmin, xmax, 100)
            y = np.linspace(ymin, ymax, 100)
            X, Y = np.meshgrid(x, y)
            for obj_id, data in region_data.items():
                if data.get("inside_mask") is not None:
                    try:
                        style = data.get("style", {})
                        kwargs = {}
                        if "color" in style:
                            kwargs["fill_color"] = style["color"]
                        elif "fill_color" in style:
                            kwargs["fill_color"] = style["fill_color"]
                        if "boundary_color" in style:
                            kwargs["boundary_color"] = style["boundary_color"]
                        if "point_size" in style:
                            kwargs["point_size"] = style["point_size"]

                        self.plot_manager.plot_region_filled(
                            ax,
                            self.scene_manager.get_object(obj_id),
                            X,
                            Y,
                            title=obj_id,
                            **kwargs,
                        )
                        rendered_objects.append({"id": obj_id, "type": "region"})
                    except Exception as e:
                        print(f"Warning: Failed to render region '{obj_id}': {e}")

        # Second pass: Render curve boundaries
        curve_data = self.get_curve_paths(bounds, 200)
        for obj_id, data in curve_data.items():
            if data.get("points"):
                try:
                    points = np.array(data["points"])
                    style = data["style"]

                    ax.plot(
                        points[:, 0],
                        points[:, 1],
                        color=style.get("color", "blue"),
                        linewidth=style.get("linewidth", 2),
                        alpha=style.get("alpha", 1.0),
                        label=obj_id,
                    )

                    rendered_objects.append({"id": obj_id, "type": "curve"})
                except Exception as e:
                    print(f"Warning: Failed to render curve '{obj_id}': {e}")

        # Add legend if there are objects
        if rendered_objects:
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Save image
        plt.tight_layout()
        plt.savefig(filename, dpi=100, bbox_inches="tight")
        plt.close(fig)

        # Return rendering info
        return {
            "filename": filename,
            "bounds": list(bounds),
            "resolution": list(resolution),
            "rendered_objects": rendered_objects,
            "object_count": len(rendered_objects),
        }

    def render_scene_image_annotated(
        self,
        filename: str,
        test_id: str,
        name: str,
        eq_a: str,
        eq_b: str,
        calculated_endpoints: List[Tuple[float, float]],
        expected_endpoints: List[Tuple[float, float]],
        calculated_intersections: List[Tuple[float, float]],
        expected_intersections: List[Tuple[float, float]],
        elapsed_time: float,
        is_correct: bool,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: Tuple[int, int] = (800, 600),
    ) -> Dict[str, Any]:
        """
        Render the scene to an image with correctness-colored overlays, keypoints, and a dark title card.
        """
        import math
        import os

        # Create figure with dark theme
        fig, ax = plt.subplots(
            figsize=(resolution[0] / 100, resolution[1] / 100), dpi=100
        )

        # Premium Dark Backgrounds
        fig.patch.set_facecolor("#0f111a")
        ax.set_facecolor("#0f111a")

        # Bounds setup
        if bounds is None:
            bounds = self.get_scene_bounds(padding=0.1)
        xmin, xmax, ymin, ymax = bounds
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect("equal")

        # Custom grid
        ax.grid(True, color="#1e2235", linestyle="--", linewidth=0.8, alpha=0.5)

        # Style spines
        for spine in ax.spines.values():
            spine.set_color("#1e2235")
            spine.set_linewidth(1.0)

        # Tick parameters
        ax.tick_params(colors="#8f9cae", which="both", labelsize=9)

        # Match Endpoints
        correct_endpoints = []
        incorrect_endpoints = []
        matched_expected_eps = set()
        tol_ep = 0.05

        for calc in calculated_endpoints:
            best_dist = float("inf")
            best_idx = -1
            for idx, exp in enumerate(expected_endpoints):
                if idx in matched_expected_eps:
                    continue
                dist = math.sqrt((calc[0] - exp[0]) ** 2 + (calc[1] - exp[1]) ** 2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            if best_idx != -1 and best_dist < tol_ep:
                correct_endpoints.append(calc)
                matched_expected_eps.add(best_idx)
            else:
                incorrect_endpoints.append(calc)

        missing_endpoints = [
            exp
            for idx, exp in enumerate(expected_endpoints)
            if idx not in matched_expected_eps
        ]

        # Match Intersections
        correct_intersections = []
        incorrect_intersections = []
        matched_expected_ints = set()
        tol_int = 0.15 if ("1/x" in eq_a or "1/x" in eq_b) else 0.05
        is_overlap = test_id in ("1.39", "2.34", "3.33")

        for calc in calculated_intersections:
            if is_overlap:
                incorrect_intersections.append(calc)
                continue
            best_dist = float("inf")
            best_idx = -1
            for idx, exp in enumerate(expected_intersections):
                if idx in matched_expected_ints:
                    continue
                dist = math.sqrt((calc[0] - exp[0]) ** 2 + (calc[1] - exp[1]) ** 2)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            if best_idx != -1 and best_dist < tol_int:
                correct_intersections.append(calc)
                matched_expected_ints.add(best_idx)
            else:
                incorrect_intersections.append(calc)

        missing_intersections = [
            exp
            for idx, exp in enumerate(expected_intersections)
            if idx not in matched_expected_ints
        ]

        # Render curves
        rendered_objects = []
        curve_data = self.get_curve_paths(bounds, 300)

        for obj_id, data in curve_data.items():
            if data.get("points"):
                try:
                    points = np.array(data["points"])
                    style = data["style"]

                    color = style.get("color", "#77f6ff")
                    if "curve_a" in obj_id:
                        color = "#00f0ff"  # Electric Cyan
                    elif "curve_b" in obj_id:
                        color = "#ff007f"  # Neon Rose
                    elif obj_id.endswith("a") or "db_curve_1" in obj_id:
                        color = "#00f0ff"
                    else:
                        color = "#ff007f"

                    linewidth = style.get("linewidth", style.get("lineWidth", 2.5))
                    zorder = 2
                    if (
                        "curve_a" in obj_id
                        or obj_id.endswith("a")
                        or "db_curve_1" in obj_id
                    ):
                        linewidth = 4.5
                        zorder = 2
                    elif (
                        "curve_b" in obj_id
                        or obj_id.endswith("b")
                        or "db_curve_2" in obj_id
                    ):
                        linewidth = 2.0
                        zorder = 3

                    ax.plot(
                        points[:, 0],
                        points[:, 1],
                        color=color,
                        linewidth=linewidth,
                        alpha=0.9,
                        zorder=zorder,
                    )
                    rendered_objects.append({"id": obj_id, "color": color})
                except Exception as e:
                    print(f"Warning: Failed to render periodic curve '{obj_id}': {e}")

        # Plot Endpoint Markers
        if correct_endpoints:
            pts = np.array(correct_endpoints)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                color="#39ff14",
                s=60,
                marker="o",
                edgecolors="#ffffff",
                linewidths=0.8,
                label="Correct Endpoint",
                zorder=5,
            )
        if incorrect_endpoints:
            pts = np.array(incorrect_endpoints)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                color="#ff3366",
                s=60,
                marker="o",
                edgecolors="#ffffff",
                linewidths=0.8,
                label="Incorrect Endpoint",
                zorder=5,
            )
        if missing_endpoints:
            pts = np.array(missing_endpoints)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                facecolors="none",
                edgecolors="#ff3366",
                s=70,
                marker="o",
                linestyle="--",
                linewidths=1.2,
                label="Missing Endpoint",
                zorder=4,
            )

        # Plot Intersection Markers
        if correct_intersections:
            pts = np.array(correct_intersections)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                color="#39ff14",
                s=80,
                marker="X",
                edgecolors="#ffffff",
                linewidths=0.5,
                label="Correct Intersection",
                zorder=6,
            )
        if incorrect_intersections:
            pts = np.array(incorrect_intersections)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                color="#ff3366",
                s=80,
                marker="X",
                edgecolors="#ffffff",
                linewidths=0.5,
                label="Incorrect Intersection",
                zorder=6,
            )
        if missing_intersections:
            pts = np.array(missing_intersections)
            ax.scatter(
                pts[:, 0],
                pts[:, 1],
                facecolors="none",
                edgecolors="#ff3366",
                s=90,
                marker="x",
                linestyle=":",
                linewidths=1.5,
                label="Missing Intersection",
                zorder=4,
            )

        # Title box / Status card overlay
        status_text = "VERIFIED ✅" if is_correct else "MISMATCH ❌"
        info_str = (
            f"CASE {test_id} — {name}\n"
            f"Curve A: {eq_a}\n"
            f"Curve B: {eq_b}\n"
            f"Status: {status_text} | Time: {elapsed_time:.3f}s"
        )

        ax.text(
            0.02,
            0.98,
            info_str,
            transform=ax.transAxes,
            color="#ffffff",
            fontsize=9,
            fontweight="medium",
            fontfamily="monospace",
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="#151828",
                edgecolor="#2c314c",
                alpha=0.9,
                linewidth=1.2,
            ),
        )

        # Save image
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        plt.tight_layout()
        fig.savefig(
            filename,
            dpi=100,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )
        plt.close(fig)

        return {
            "filename": filename,
            "bounds": list(bounds),
            "resolution": list(resolution),
            "rendered_objects": rendered_objects,
            "correct_endpoints_count": len(correct_endpoints),
            "incorrect_endpoints_count": len(incorrect_endpoints),
            "missing_endpoints_count": len(missing_endpoints),
            "correct_intersections_count": len(correct_intersections),
            "incorrect_intersections_count": len(incorrect_intersections),
            "missing_intersections_count": len(missing_intersections),
        }

    def get_scene_bounds(
        self, padding: float = 0.2
    ) -> Tuple[float, float, float, float]:
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
                if (
                    hasattr(obj, "xmin")
                    and hasattr(obj, "xmax")
                    and hasattr(obj, "ymin")
                    and hasattr(obj, "ymax")
                ):
                    if all(
                        getattr(obj, name) is not None
                        and np.isfinite(float(getattr(obj, name)))
                        for name in ["xmin", "xmax", "ymin", "ymax"]
                    ):
                        o_xmin, o_xmax, o_ymin, o_ymax = (
                            float(obj.xmin),
                            float(obj.xmax),
                            float(obj.ymin),
                            float(obj.ymax),
                        )
                        # Skip extremely large bounds (span >= 50) like infinite vertical/horizontal lines
                        # to allow scene auto-fitting to focus tightly on the active shapes
                        if abs(o_xmax - o_xmin) < 50.0 and abs(o_ymax - o_ymin) < 50.0:
                            all_bounds.append((o_xmin, o_xmax, o_ymin, o_ymax))
                        continue

                # First try the get_bounds method if available
                if hasattr(obj, "get_bounds"):
                    bounds = obj.get_bounds()
                    if bounds and len(bounds) == 4 and all(np.isfinite(bounds)):
                        all_bounds.append(bounds)
                        continue

                # Try the bounding_box method if available
                if hasattr(obj, "bounding_box"):
                    bounds = obj.bounding_box()
                    if (
                        bounds
                        and len(bounds) == 4
                        and all(np.isfinite(b) for b in bounds if b is not None)
                    ):
                        all_bounds.append(bounds)
                        continue

                # Fallback: extract curve paths and calculate bounds from points
                if hasattr(obj, "outer_boundary"):
                    # For AreaRegion objects, sample the boundary
                    points, _ = self._sample_boundary_points(
                        obj.outer_boundary, self.default_bounds, 50
                    )
                    if points:
                        points_array = np.array(points)
                        obj_bounds = [
                            float(np.min(points_array[:, 0])),  # xmin
                            float(np.max(points_array[:, 0])),  # xmax
                            float(np.min(points_array[:, 1])),  # ymin
                            float(np.max(points_array[:, 1])),  # ymax
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
                        float(np.max(points_array[:, 1])),  # ymax
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
        if (
            not np.isfinite(xmin)
            or not np.isfinite(xmax)
            or not np.isfinite(ymin)
            or not np.isfinite(ymax)
        ):
            return self._fallback_bounds

        x_range = xmax - xmin
        y_range = ymax - ymin

        if x_range < 0.2:
            mid_x = (xmin + xmax) / 2.0
            xmin, xmax = mid_x - 2.0, mid_x + 2.0
            x_range = 4.0
        if y_range < 0.2:
            mid_y = (ymin + ymax) / 2.0
            ymin, ymax = mid_y - 2.0, mid_y + 2.0
            y_range = 4.0

        if x_range <= 0 or y_range <= 0:
            return self._fallback_bounds

        x_padding = x_range * padding
        y_padding = y_range * padding

        return (xmin - x_padding, xmax + x_padding, ymin - y_padding, ymax + y_padding)

    def get_geometry_scene_data(
        self,
        resolution: int = 400,
        bounds: Optional[Tuple[float, float, float, float]] = None,
    ) -> Dict[str, Any]:
        """Return polyline data, bounds, and key-point annotations for the scene."""

        if bounds is None:
            bounds = self.get_scene_bounds(padding=0.0)
        sanitized_bounds = self._sanitize_bounds(bounds)
        curve_data = self.get_curve_paths(
            bounds=sanitized_bounds, resolution=resolution
        )

        objects: List[Dict[str, Any]] = []
        polyline_lookup: Dict[str, List[List[float]]] = {}

        for obj_id, data in curve_data.items():
            points = data.get("points") or []
            obj = self.scene_manager.get_object(obj_id)
            sanitized_object_bounds = self._sanitize_bounds(data.get("bounds"))
            cleaned_points = [
                [float(pt[0]), float(pt[1])]
                for pt in points
                if len(pt) == 2 and np.isfinite(pt[0]) and np.isfinite(pt[1])
            ]
            raw_paths = data.get("paths") or []
            cleaned_paths = []
            for path in raw_paths:
                cleaned_path = [
                    [float(pt[0]), float(pt[1])]
                    for pt in path
                    if len(pt) == 2 and np.isfinite(pt[0]) and np.isfinite(pt[1])
                ]
                if len(cleaned_path) >= 2:
                    cleaned_paths.append(cleaned_path)

            if BaseField is not None and isinstance(obj, BaseField):
                # Skip adding field boundary polylines to polyline_lookup
                # to prevent spawning thousands of segment intersection checks
                pass
            else:
                polyline_lookup[obj_id] = (
                    cleaned_paths
                    if cleaned_paths
                    else ([cleaned_points] if cleaned_points else [])
                )

            key_points = self._extract_endpoint_points(obj, cleaned_points)

            is_field = BaseField is not None and isinstance(obj, BaseField)
            objects.append(
                {
                    "id": obj_id,
                    "type": "field" if is_field else data.get("type", "curve"),
                    "closed": bool(data.get("closed", False)),
                    "points": cleaned_points,
                    "paths": cleaned_paths
                    if cleaned_paths
                    else ([cleaned_points] if cleaned_points else []),
                    "bounds": sanitized_object_bounds,
                    "style": data.get("style", {}),
                    "key_points": key_points,
                }
            )

        intersections = self._compute_polyline_intersections(polyline_lookup)

        # Collect field heatmap data for BaseField objects in the scene
        fields: List[Dict[str, Any]] = []
        if BaseField is not None:
            # Evaluate fields on a static physical scene bounding box with padding and minimum span 20
            # to make signed distance field completely zoom-independent and stable in physical coordinates.
            p_bounds = self.get_scene_bounds(padding=0.5)
            if p_bounds is not None and all(np.isfinite(b) for b in p_bounds):
                pxmin, pxmax, pymin, pymax = p_bounds
            else:
                pxmin, pxmax, pymin, pymax = -10.0, 10.0, -10.0, 10.0

            span_x = pxmax - pxmin
            if span_x < 20.0:
                cx = (pxmin + pxmax) / 2.0
                pxmin = cx - 10.0
                pxmax = cx + 10.0

            span_y = pymax - pymin
            if span_y < 20.0:
                cy = (pymin + pymax) / 2.0
                pymin = cy - 10.0
                pymax = cy + 10.0

            # Union with incoming viewport bounds to prevent clipping during zoom/pan
            if (
                bounds is not None
                and len(bounds) == 4
                and all(np.isfinite(b) for b in bounds)
            ):
                bxmin, bxmax, bymin, bymax = bounds
                pxmin = min(pxmin, bxmin)
                pxmax = max(pxmax, bxmax)
                pymin = min(pymin, bymin)
                pymax = max(pymax, bymax)

            field_bounds = (pxmin, pxmax, pymin, pymax)
            field_resolution = 128

            for obj_id in self.scene_manager.list_objects():
                obj = self.scene_manager.get_object(obj_id)
                if isinstance(obj, BaseField):
                    try:
                        field_entry = self.get_field_heatmap_data(
                            obj, obj_id, field_bounds, field_resolution
                        )
                        fields.append(field_entry)
                    except Exception as fe:
                        fields.append({"id": obj_id, "error": str(fe)})

        return {
            "objects": objects,
            "intersections": intersections,
            "fields": fields,
            "scene_bounds": list(sanitized_bounds),
        }

    # ================== Field Heatmap Rendering ==================

    def get_field_heatmap_data(
        self,
        field_obj,
        obj_id: str,
        bounds: Optional[Tuple[float, float, float, float]] = None,
        resolution: int = 128,
        colormap: str = "RdBu_r",
    ) -> Dict[str, Any]:
        """
        Evaluate a BaseField on a uniform grid and extract its zero-isoline.

        Args:
            field_obj: A BaseField instance (CurveField, BlendedField,
                       SignedDistanceField, OccupancyField).
            obj_id:    Scene object identifier.
            bounds:    (xmin, xmax, ymin, ymax).  Defaults to scene bounds.
            resolution: Number of grid points per axis.  Capped at 256.
            colormap:  Matplotlib colormap name for rendering hints.

        Returns:
            Dict with keys:
              id, bounds, resolution, colormap, vmin, vmax,
              data (row-major list of floats, NaN replaced by null),
              zero_isoline (list of [[x,y],...] paths),
              statistics, style.
        """
        if bounds is None:
            bounds = self._sanitize_bounds(self.get_scene_bounds())
        resolution = min(int(resolution), 256)

        xmin, xmax, ymin, ymax = bounds
        x = np.linspace(xmin, xmax, resolution)
        y = np.linspace(ymin, ymax, resolution)
        X, Y = np.meshgrid(x, y)

        try:
            Z = np.asarray(field_obj.evaluate(X, Y), dtype=float)
        except Exception as e:
            return {"id": obj_id, "error": f"evaluate failed: {e}"}

        if Z.shape != X.shape:
            try:
                Z = Z.reshape(X.shape)
            except Exception:
                return {
                    "id": obj_id,
                    "error": f"shape mismatch: {Z.shape} vs {X.shape}",
                }

        # Statistics (ignoring NaN/inf)
        finite = np.isfinite(Z)
        if np.any(finite):
            fv = Z[finite]
            vmin, vmax = float(fv.min()), float(fv.max())
            stats = {
                "min": vmin,
                "max": vmax,
                "mean": float(fv.mean()),
                "std": float(fv.std()),
                "finite_frac": float(finite.mean()),
            }
        else:
            vmin, vmax = -1.0, 1.0
            stats = {
                "min": vmin,
                "max": vmax,
                "mean": 0.0,
                "std": 0.0,
                "finite_frac": 0.0,
            }

        # Symmetric colour range centred on zero (for signed-distance / implicit fields)
        abs_max = max(abs(vmin), abs(vmax), 1e-9)

        # Serialise the grid (NaN/inf → None for JSON, fully vectorized in NumPy!)
        Z_none = np.where(np.isfinite(Z), Z, None)
        data_rows = Z_none.tolist()

        # Extract zero-isoline using cached matplotlib contour
        zero_isoline: List[List[List[float]]] = []
        try:
            fig, ax = _get_cached_contour_axes()
            cs = ax.contour(X, Y, Z, levels=[0.0])
            if hasattr(cs, "get_paths"):
                for path_obj in cs.get_paths():
                    for poly in path_obj.to_polygons():
                        path = [
                            [float(p[0]), float(p[1])]
                            for p in poly
                            if np.isfinite(p[0]) and np.isfinite(p[1])
                        ]
                        if len(path) >= 2:
                            zero_isoline.append(path)
            else:
                for coll in cs.collections:
                    for seg in coll.get_segments():
                        path = [
                            [float(p[0]), float(p[1])]
                            for p in seg
                            if np.isfinite(p[0]) and np.isfinite(p[1])
                        ]
                        if len(path) >= 2:
                            zero_isoline.append(path)
        except Exception:
            pass  # zero isoline is optional

        style = (
            self.scene_manager.get_style(obj_id)
            if obj_id in self.scene_manager.list_objects()
            else {}
        )

        return {
            "id": obj_id,
            "type": field_obj.__class__.__name__,
            "bounds": list(bounds),
            "resolution": resolution,
            "colormap": colormap,
            "vmin": -abs_max,
            "vmax": abs_max,
            "data": data_rows,
            "zero_isoline": zero_isoline,
            "statistics": stats,
            "style": style,
        }

    # ================== Helper Methods ==================

    def _is_periodic_radical(self, obj) -> Tuple[bool, float, float]:
        """
        Algebraically check if the object represents a periodic radical curve.
        Returns (is_periodic, cy_val, H_coeff).
        """
        # First check base curve if trimmed
        base = obj
        if hasattr(obj, "base_curve"):
            base = obj.base_curve

        # Fast path: honour the explicit is_periodic flag set on ProceduralCurve /
        # ParametricSegment instances so we avoid the fragile name-string heuristic.
        if getattr(obj, "is_periodic", False) or getattr(base, "is_periodic", False):
            endpoints = getattr(obj, "endpoints", None)
            if endpoints and len(endpoints) > 0:
                return True, float(endpoints[0][1]), 1.0
            return True, 0.0, 1.0

        # Check if explicitly marked as periodic radical via metadata properties
        is_marked = getattr(obj, "is_periodic_radical", False) or getattr(
            base, "is_periodic_radical", False
        )

        expr = getattr(base, "expression", None)
        if expr is None:
            if is_marked:
                endpoints = getattr(obj, "endpoints", None)
                if endpoints and len(endpoints) > 0:
                    return True, float(endpoints[0][1]), 1.0
                return True, 0.0, 1.0
            return False, 0.0, 1.0

        import sympy as sp

        vars_attr = getattr(base, "variables", None)
        if not vars_attr:
            free = expr.free_symbols
            x_sym = next((s for s in free if s.name == "x"), None)
            y_sym = next((s for s in free if s.name == "y"), None)
        else:
            x_sym, y_sym = vars_attr[0], vars_attr[1]

        if not x_sym or not y_sym:
            if is_marked:
                endpoints = getattr(obj, "endpoints", None)
                if endpoints and len(endpoints) > 0:
                    return True, float(endpoints[0][1]), 1.0
                return True, 0.0, 1.0
            return False, 0.0, 1.0

        # Check for trigonometric atoms
        has_trig = len(expr.atoms(sp.sin)) > 0 or len(expr.atoms(sp.cos)) > 0
        if not has_trig:
            if is_marked:
                endpoints = getattr(obj, "endpoints", None)
                if endpoints and len(endpoints) > 0:
                    return True, float(endpoints[0][1]), 1.0
                return True, 0.0, 1.0
            return False, 0.0, 1.0

        try:
            df_dy = sp.diff(expr, y_sym)
            df2_dy2 = sp.diff(expr, y_sym, 2)
            df3_dy3 = sp.diff(expr, y_sym, 3)
            df_dx_dy = sp.diff(expr, x_sym, y_sym)

            # Check if quadratic in y and no mixed term
            if df3_dy3 == 0 and df_dx_dy == 0 and df2_dy2 != 0:
                # It is quadratic in y: f(x, y) = H * (y - cy)^2 - g(x)
                E = df_dy.subs(y_sym, 0)
                D = df2_dy2
                cy_val = float(-E / D)
                H = float(D / 2.0)
                return True, cy_val, H
        except Exception:
            pass

        # Fallback to endpoints check only if explicitly marked or has >= 3 endpoints sharing the same Y
        endpoints = getattr(obj, "endpoints", None)
        if endpoints and len(endpoints) > 0:
            if is_marked or (
                len(endpoints) >= 3
                and all(abs(ep[1] - endpoints[0][1]) < 1e-5 for ep in endpoints)
            ):
                return True, float(endpoints[0][1]), 1.0

        return False, 0.0, 1.0

    def _estimate_object_bounds(
        self, obj, scene_bounds: Tuple[float, float, float, float], coarse: int = 40
    ) -> Tuple[float, float, float, float]:
        """
        Estimate tight bounds for a single object by probing on a coarse grid,
        then add padding. Falls back to scene_bounds if nothing is found.
        """
        # 0. Check if the object has a mathematically precise bounding box (e.g., ConicSection Circle/Ellipse)
        if hasattr(obj, "bounding_box"):
            try:
                bbox = obj.bounding_box()
                if bbox and all(np.isfinite(val) for val in bbox):
                    bx_min, bx_max, by_min, by_max = bbox
                    w = bx_max - bx_min
                    h = by_max - by_min
                    # Only use it if it's a tight, non-infinite, non-placeholder bounding box
                    if 0 < w < 50.0 and 0 < h < 50.0:
                        # Pad the tight mathematical bounds by 5% to avoid edge effects
                        pad_x = max(w * 0.05, 0.1)
                        pad_y = max(h * 0.05, 0.1)
                        return (
                            bx_min - pad_x,
                            bx_max + pad_x,
                            by_min - pad_y,
                            by_max + pad_y,
                        )
            except Exception as bbox_err:
                print(f"Warning: Failed mathematical bounding box check: {bbox_err}")

        # First check if the object has manually assigned attributes xmin, xmax, ymin, ymax (e.g. loaded from DB)
        if (
            hasattr(obj, "xmin")
            and hasattr(obj, "xmax")
            and hasattr(obj, "ymin")
            and hasattr(obj, "ymax")
        ):
            if all(
                getattr(obj, name) is not None
                and np.isfinite(float(getattr(obj, name)))
                for name in ["xmin", "xmax", "ymin", "ymax"]
            ):
                o_xmin, o_xmax, o_ymin, o_ymax = (
                    float(obj.xmin),
                    float(obj.xmax),
                    float(obj.ymin),
                    float(obj.ymax),
                )

                # Expand degenerate domains (spans < 0.2) to a stable default span (like 4.0 centered)
                if abs(o_xmax - o_xmin) < 0.2:
                    mid_x = (o_xmin + o_xmax) / 2.0
                    o_xmin, o_xmax = mid_x - 2.0, mid_x + 2.0
                if abs(o_ymax - o_ymin) < 0.2:
                    mid_y = (o_ymin + o_ymax) / 2.0
                    o_ymin, o_ymax = mid_y - 2.0, mid_y + 2.0

                s_xmin, s_xmax, s_ymin, s_ymax = scene_bounds

                # Check if it is an infinite/very large line (span >= 50)
                is_infinite = (abs(o_xmax - o_xmin) >= 50.0) or (
                    abs(o_ymax - o_ymin) >= 50.0
                )

                if is_infinite:
                    # Crop dynamically to the bounds of other non-infinite curves in the active scene
                    non_inf_bounds = []
                    for other_id in self.scene_manager.list_objects():
                        other_obj = self.scene_manager.get_object(other_id)
                        if (
                            hasattr(other_obj, "xmin")
                            and hasattr(other_obj, "xmax")
                            and hasattr(other_obj, "ymin")
                            and hasattr(other_obj, "ymax")
                        ):
                            if all(
                                getattr(other_obj, name) is not None
                                and np.isfinite(float(getattr(other_obj, name)))
                                for name in ["xmin", "xmax", "ymin", "ymax"]
                            ):
                                ox_min, ox_max, oy_min, oy_max = (
                                    float(other_obj.xmin),
                                    float(other_obj.xmax),
                                    float(other_obj.ymin),
                                    float(other_obj.ymax),
                                )
                                if (
                                    abs(ox_max - ox_min) < 50.0
                                    and abs(oy_max - oy_min) < 50.0
                                ):
                                    non_inf_bounds.append(
                                        (ox_min, ox_max, oy_min, oy_max)
                                    )

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
                        min(o_ymax, int_ymax + pad_y),
                    )
                else:
                    return (o_xmin, o_xmax, o_ymin, o_ymax)

        xmin, xmax, ymin, ymax = scene_bounds
        # Coarse probe to find where the object's implicit function changes sign
        try:
            x = np.linspace(xmin, xmax, coarse)
            y = np.linspace(ymin, ymax, coarse)
            X, Y = np.meshgrid(x, y)

            if hasattr(obj, "evaluate"):
                Z = obj.evaluate(X, Y)
            elif hasattr(obj, "outer_boundary") and hasattr(
                obj.outer_boundary, "evaluate"
            ):
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

    def _extract_curve_contour(
        self, obj, bounds: Tuple[float, float, float, float], resolution: int
    ) -> Tuple[List[List[float]], bool, List[List[List[float]]]]:
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

        # Check if periodic radical algebraically
        is_periodic_radical, cy_val, H_coeff = self._is_periodic_radical(obj)

        if is_periodic_radical:
            # For periodic radical curves (H*(y - cy_val)**2 = g(x)), compute the actual Y-extent
            # by evaluating f(x, cy_val) along the x-axis. Since f(x,y) = H*(y - cy_val)**2 - g(x),
            # we have g(x) = -f(x, cy_val) and max|y - cy_val| = √(max(g(x)) / H).
            # This concentrates ALL grid points in the curve's actual y-range
            # instead of wasting them on the (often huge) database bounds.
            try:
                x_probe = np.linspace(xmin, xmax, 200)
                y_probe = np.full_like(x_probe, cy_val)
                f_at_cy = obj.evaluate(x_probe, y_probe)
                if isinstance(f_at_cy, np.ndarray):
                    g_x = -f_at_cy / H_coeff
                    g_max = float(np.nanmax(g_x))
                    if g_max > 0:
                        actual_ymax = np.sqrt(g_max)
                        ymax_abs = actual_ymax * 1.15  # 15% padding
                    else:
                        ymax_abs = max(abs(ymin - cy_val), abs(ymax - cy_val))
                else:
                    ymax_abs = max(abs(ymin - cy_val), abs(ymax - cy_val))
            except Exception:
                ymax_abs = max(abs(ymin - cy_val), abs(ymax - cy_val))
            ymin = cy_val - ymax_abs
            ymax = cy_val + ymax_abs

        # Detect periodic frequency and scale resolution dynamically to avoid aliasing issues on high-frequency curves
        is_periodic = False
        max_freq = 1.0
        base = obj
        if hasattr(obj, "base_curve"):
            base = obj.base_curve

        expr = getattr(base, "expression", None)
        if expr is not None:
            try:
                import sympy as sp

                trig_atoms = expr.atoms(sp.sin) | expr.atoms(sp.cos)
                if trig_atoms:
                    is_periodic = True
                    for atom in trig_atoms:
                        arg = atom.args[0]
                        free = arg.free_symbols
                        x_sym = next((s for s in free if s.name == "x"), None)
                        if x_sym is not None:
                            coeff = float(arg.coeff(x_sym))
                            max_freq = max(max_freq, abs(coeff))
            except Exception:
                pass
        else:
            name = getattr(obj, "name", "") or getattr(base, "name", "") or ""
            if any(p in name.lower() for p in ("sin", "cos", "trig", "periodic")):
                is_periodic = True

        if is_periodic or is_periodic_radical:
            x_span = xmax - xmin
            periods = (x_span * max_freq) / (2.0 * math.pi)
            required_res = int(max(periods * 25, 800))
            resolution = min(required_res, 2000)

        # Force odd resolution to ensure y=cy_val is a grid line, maximizing horizontal symmetry
        resolution = resolution | 1

        # Create evaluation grid with a 2% boundary padding expansion
        # to ensure zero-crossings right at original boundaries are captured
        # (they will be strictly clipped back to original bounds in post-filtering)
        x_span = xmax - xmin
        y_span = ymax - ymin
        grid_xmin = xmin - x_span * 0.02
        grid_xmax = xmax + x_span * 0.02
        grid_ymin = ymin - y_span * 0.02
        grid_ymax = ymax + y_span * 0.02

        x = np.linspace(grid_xmin, grid_xmax, resolution)
        y = np.linspace(grid_ymin, grid_ymax, resolution)
        X, Y = np.meshgrid(x, y)

        try:
            # Handle different object types
            if hasattr(obj, "evaluate"):
                # Direct evaluation for curves
                Z = obj.evaluate(X, Y)
            elif hasattr(obj, "outer_boundary") and hasattr(
                obj.outer_boundary, "evaluate"
            ):
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
                plt.close(fig)

            raw_paths = []

            # Modern matplotlib contour path extraction
            if hasattr(contours, "get_paths") and callable(contours.get_paths):
                for path in contours.get_paths():
                    raw_paths.append((path.vertices.tolist(), path.codes))

            if (
                not raw_paths
                and hasattr(contours, "collections")
                and contours.collections
            ):
                for collection in contours.collections:
                    for path in collection.get_paths():
                        raw_paths.append((path.vertices.tolist(), path.codes))

            if not raw_paths and hasattr(contours, "allsegs"):
                for level_segments in contours.allsegs:
                    for seg in level_segments:
                        if len(seg) >= 2:
                            raw_paths.append((seg.tolist(), None))

            # Post-filter paths with the TrimmedImplicitCurve mask and explicit bounds
            # to achieve smooth, gap-free termination at boundaries
            candidate_paths = []

            obj_xmin = getattr(obj, "_xmin", None)
            obj_xmax = getattr(obj, "_xmax", None)
            obj_ymin = getattr(obj, "_ymin", None)
            obj_ymax = getattr(obj, "_ymax", None)

            # Expand degenerate clipping bounds to prevent empty polylines
            if (
                obj_xmin is not None
                and obj_xmax is not None
                and abs(obj_xmax - obj_xmin) < 0.2
            ):
                mid_x = (obj_xmin + obj_xmax) / 2.0
                obj_xmin, obj_xmax = mid_x - 2.0, mid_x + 2.0
            if (
                obj_ymin is not None
                and obj_ymax is not None
                and abs(obj_ymax - obj_ymin) < 0.2
            ):
                mid_y = (obj_ymin + obj_ymax) / 2.0
                obj_ymin, obj_ymax = mid_y - 2.0, mid_y + 2.0

            eps = 1e-9

            def in_bounds(px, py):
                # Crop to curve's explicit trimming bounds first
                if obj_xmin is not None and px < obj_xmin - eps:
                    return False
                if obj_xmax is not None and px > obj_xmax + eps:
                    return False
                if obj_ymin is not None and py < obj_ymin - eps:
                    return False
                if obj_ymax is not None and py > obj_ymax + eps:
                    return False
                # Also crop back to original evaluation domain boundaries (due to 2% grid padding)
                if (
                    px < xmin - eps
                    or px > xmax + eps
                    or py < ymin - eps
                    or py > ymax + eps
                ):
                    return False
                return True

            has_mask = hasattr(obj, "mask") and callable(obj.mask)

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
                        valid_mask &= np.abs(vals) <= 0.15
                    valid_list = valid_mask.tolist()
                except Exception:
                    valid_list = [True] * len(points_list)

                # Split paths if mask splits them or a new subpath starts (MOVETO code)
                current_subpath = []
                for idx, (pt, mask_ok) in enumerate(zip(points_list, mask_bools)):
                    is_moveto = (
                        codes is not None and idx < len(codes) and codes[idx] == 1
                    )
                    if (
                        mask_ok
                        and in_bounds(pt[0], pt[1])
                        and valid_list[idx]
                        and not is_moveto
                    ):
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

            # For curves like periodic_radical where endpoints are zero-crossings at y = cy_val,
            # split closed loops at y = cy_val into open branches so they snap perfectly and symmetrically.
            is_periodic_radical, cy_val, H_coeff = self._is_periodic_radical(obj)

            if is_periodic_radical:
                split_paths = []
                for path in all_paths:
                    if len(path) < 2:
                        continue

                    is_path_closed = np.allclose(path[0], path[-1], atol=1e-6)
                    rotated_path = path
                    if is_path_closed:
                        # Find a sign change/zero crossing in Y relative to cy_val to rotate path start/end to a crossing point
                        rotate_idx = -1
                        for i in range(len(path) - 1):
                            val_curr = path[i][1] - cy_val
                            val_next = path[i + 1][1] - cy_val
                            if val_curr * val_next < 0 or abs(val_curr) < 1e-9:
                                rotate_idx = i
                                break
                        if rotate_idx != -1:
                            rotated_path = (
                                path[rotate_idx + 1 : -1] + path[0 : rotate_idx + 2]
                            )

                    # Robust sign-state tracking splitter to partition cleanly at y = cy_val
                    def get_sign(val):
                        diff = val - cy_val
                        if diff > 1e-9:
                            return 1
                        if diff < -1e-9:
                            return -1
                        return 0

                    current_sub = [rotated_path[0]]
                    current_sign = get_sign(rotated_path[0][1])

                    for i in range(1, len(rotated_path)):
                        curr_pt = rotated_path[i]
                        curr_sign = get_sign(curr_pt[1])

                        if (
                            curr_sign != 0
                            and current_sign != 0
                            and curr_sign != current_sign
                        ):
                            # Strict sign change
                            current_sub.append(curr_pt)
                            if len(current_sub) >= 2:
                                split_paths.append(current_sub)
                            current_sub = [curr_pt]
                            current_sign = curr_sign
                        elif curr_sign == 0:
                            # Hitting exactly cy_val!
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
                    orig_points, codes = max(
                        candidate_paths, key=lambda item: len(item[0])
                    )
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

    def _sanitize_bounds(
        self, bounds: Optional[Union[List[float], Tuple[float, float, float, float]]]
    ) -> Tuple[float, float, float, float]:
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

    def _extract_endpoint_points(
        self, obj, polyline: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """Return labeled key points (endpoints/intersections placeholders)."""

        key_points: List[Dict[str, Any]] = []
        label_seed = ord("A")

        if hasattr(obj, "get_endpoints"):
            try:
                xmin_val = None
                xmax_val = None
                if polyline:
                    xs = [
                        pt[0] for pt in polyline if len(pt) == 2 and np.isfinite(pt[0])
                    ]
                    if xs:
                        xmin_val = min(xs)
                        xmax_val = max(xs)
                if xmin_val is None or xmax_val is None:
                    xmin_val = getattr(obj, "xmin", -10.0)
                    xmax_val = getattr(obj, "xmax", 10.0)

                endpoints = obj.get_endpoints(xmin=xmin_val, xmax=xmax_val)
            except Exception:
                endpoints = []
            for idx, pt in enumerate(endpoints or []):
                if len(pt) != 2 or not np.isfinite(pt[0]) or not np.isfinite(pt[1]):
                    continue
                key_points.append(
                    {
                        "type": "endpoint",
                        "label": chr(label_seed + idx),
                        "x": float(pt[0]),
                        "y": float(pt[1]),
                    }
                )

        # Fallback 1: If we have exactly 1 analytical endpoint and the curve is open (not closed),
        # append the polyline boundary extremity that is far from that analytical endpoint.
        closed_attr = getattr(obj, "is_closed", False)
        closed = closed_attr() if callable(closed_attr) else bool(closed_attr)
        if not closed and len(key_points) == 1 and len(polyline) >= 2:
            existing_pt = (key_points[0]["x"], key_points[0]["y"])
            first = polyline[0]
            last = polyline[-1]
            # Calculate squared distance from analytical endpoint to first and last polyline points
            d_first = (first[0] - existing_pt[0]) ** 2 + (
                first[1] - existing_pt[1]
            ) ** 2
            d_last = (last[0] - existing_pt[0]) ** 2 + (last[1] - existing_pt[1]) ** 2

            # Select the boundary point that is further away
            if d_first > d_last:
                if d_first > 1e-4:
                    key_points.append(
                        {
                            "type": "endpoint",
                            "label": chr(label_seed + len(key_points)),
                            "x": float(first[0]),
                            "y": float(first[1]),
                        }
                    )
            else:
                if d_last > 1e-4:
                    key_points.append(
                        {
                            "type": "endpoint",
                            "label": chr(label_seed + len(key_points)),
                            "x": float(last[0]),
                            "y": float(last[1]),
                        }
                    )

        # Fallback 2: use polyline start/end if we still have no key points
        if not key_points and len(polyline) >= 2:
            first = polyline[0]
            last = polyline[-1]
            key_points.append(
                {"type": "endpoint", "label": "A", "x": first[0], "y": first[1]}
            )
            key_points.append(
                {"type": "endpoint", "label": "B", "x": last[0], "y": last[1]}
            )

        return key_points

    def _compute_polyline_intersections(
        self, polyline_lookup: Dict[str, List[List[List[float]]]]
    ) -> List[Dict[str, Any]]:
        """Detect approximate intersections between polylines using segment checks."""

        def is_periodic_or_procedural(c) -> bool:
            if hasattr(c, "base_curve") and c.base_curve is not None:
                c = c.base_curve
            if self._is_periodic_radical(c)[0]:
                return True
            class_name = type(c).__name__
            if "Procedural" in class_name:
                return True
            if not hasattr(c, "expression") or c.expression is None:
                if any(
                    x in class_name
                    for x in [
                        "Line",
                        "Circle",
                        "ConicSection",
                        "Ellipse",
                        "Hyperbola",
                        "Parabola",
                        "PolynomialCurve",
                    ]
                ):
                    return False
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

        # Determine dynamic segment limits to balance performance and precision.
        # If any curve is periodic, we increase segment limit to preserve high-frequency features.
        has_periodic = False
        max_polyline_len = 0
        for obj_id in polyline_lookup.keys():
            try:
                style = self.scene_manager.get_style(obj_id)
                if style.get("is_periodic_curve"):
                    has_periodic = True
            except Exception:
                pass
            try:
                obj = self.scene_manager.get_object(obj_id)
                if self._is_periodic_radical(obj)[0]:
                    has_periodic = True
            except Exception:
                pass
            for path in polyline_lookup[obj_id]:
                max_polyline_len = max(max_polyline_len, len(path))

        # MAX_SEGS controls how many polyline segments are used in O(n*m) intersection computation.
        # Cap it to keep performance reasonable for interactive use.
        # Periodic curves need more segments than non-periodic to preserve high-frequency crossings.
        MAX_SEGS = 800 if has_periodic else 200

        def _subsample(pts):
            if len(pts) <= MAX_SEGS + 1:
                return pts
            step = len(pts) / MAX_SEGS
            return [pts[int(i * step)] for i in range(MAX_SEGS)] + [pts[-1]]

        raw: List[Tuple[float, float, float]] = []

        for (id_a, paths_a), (id_b, paths_b) in combinations(
            polyline_lookup.items(), 2
        ):
            obj_a = self.scene_manager.get_object(id_a)
            obj_b = self.scene_manager.get_object(id_b)
            has_eval = hasattr(obj_a, "evaluate") and hasattr(obj_b, "evaluate")
            is_periodic_a = is_periodic_or_procedural(obj_a)
            is_periodic_b = is_periodic_or_procedural(obj_b)

            # Global overlap check for the curve pair
            is_overlapping = False
            try:
                all_pts_a = []
                for p in paths_a:
                    all_pts_a.extend(p)
                all_pts_b = []
                for p in paths_b:
                    all_pts_b.extend(p)

                if len(all_pts_a) > 5 and len(all_pts_b) > 5:
                    check_pts_a = all_pts_a[:: max(1, len(all_pts_a) // 40)]
                    check_pts_b = all_pts_b[:: max(1, len(all_pts_b) // 40)]
                    if len(check_pts_a) > 2 and len(check_pts_b) > 2:
                        xs_a = [p[0] for p in all_pts_a]
                        ys_a = [p[1] for p in all_pts_a]
                        span_a = max(max(xs_a) - min(xs_a), max(ys_a) - min(ys_a))
                        xs_b = [p[0] for p in all_pts_b]
                        ys_b = [p[1] for p in all_pts_b]
                        span_b = max(max(xs_b) - min(xs_b), max(ys_b) - min(ys_b))

                        if not is_periodic_a and not is_periodic_b:
                            overlap_tol = 1e-5
                        else:
                            overlap_tol = min(0.1, 0.05 * min(span_a, span_b))
                        overlap_tol_sq = overlap_tol**2

                        close_count = 0
                        for pa in check_pts_a:
                            min_d_sq = min(
                                (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2
                                for pb in check_pts_b
                            )
                            if min_d_sq < overlap_tol_sq:
                                close_count += 1
                        ratio = close_count / len(check_pts_a)
                        if ratio > 0.90:
                            is_overlapping = True
            except Exception:
                pass

            if is_overlapping:
                continue

            for pts_a in paths_a:
                for pts_b in paths_b:
                    segs_a = self._polyline_segments(_subsample(pts_a))
                    segs_b = self._polyline_segments(_subsample(pts_b))
                    for seg_a in segs_a:
                        (a_p1, a_p2) = seg_a
                        a_xmin = min(a_p1[0], a_p2[0])
                        a_xmax = max(a_p1[0], a_p2[0])
                        a_ymin = min(a_p1[1], a_p2[1])
                        a_ymax = max(a_p1[1], a_p2[1])

                        for seg_b in segs_b:
                            (b_p1, b_p2) = seg_b
                            b_xmin = min(b_p1[0], b_p2[0])
                            b_xmax = max(b_p1[0], b_p2[0])
                            b_ymin = min(b_p1[1], b_p2[1])
                            b_ymax = max(b_p1[1], b_p2[1])

                            # Bounding box pre-filtering to prune non-overlapping segment pairs
                            if (
                                a_xmin <= b_xmax + 1e-9
                                and a_xmax >= b_xmin - 1e-9
                                and a_ymin <= b_ymax + 1e-9
                                and a_ymax >= b_ymin - 1e-9
                            ):
                                result = self._segment_intersection(seg_a, seg_b)
                                if result is not None:
                                    px, py = result
                                else:
                                    # Near miss check: if segment midpoints are close
                                    mid_a = (
                                        (a_p1[0] + a_p2[0]) / 2.0,
                                        (a_p1[1] + a_p2[1]) / 2.0,
                                    )
                                    mid_b = (
                                        (b_p1[0] + b_p2[0]) / 2.0,
                                        (b_p1[1] + b_p2[1]) / 2.0,
                                    )
                                    if (mid_a[0] - mid_b[0]) ** 2 + (
                                        mid_a[1] - mid_b[1]
                                    ) ** 2 < 0.0025:  # distance < 0.05
                                        px, py = mid_a[0], mid_a[1]
                                    else:
                                        continue

                                if has_eval:
                                    from scipy.optimize import fsolve

                                    def intersection_system(p):
                                        x_val, y_val = p[0], p[1]
                                        val_a = obj_a.evaluate(x_val, y_val)
                                        val_b = obj_b.evaluate(x_val, y_val)
                                        f_a = (
                                            float(val_a[0])
                                            if isinstance(val_a, np.ndarray)
                                            else float(val_a)
                                        )
                                        f_b = (
                                            float(val_b[0])
                                            if isinstance(val_b, np.ndarray)
                                            else float(val_b)
                                        )
                                        return [f_a, f_b]

                                    refined = False
                                    try:
                                        is_periodic_a = is_periodic_or_procedural(obj_a)
                                        is_periodic_b = is_periodic_or_procedural(obj_b)
                                        xtol_val = 1e-6

                                        sol, infodict, ier, mesg = fsolve(
                                            intersection_system,
                                            [px, py],
                                            xtol=xtol_val,
                                            full_output=True,
                                        )
                                        if ier in (1, 2, 3, 4, 5):
                                            sol_x, sol_y = float(sol[0]), float(sol[1])
                                            val_a = obj_a.evaluate(sol_x, sol_y)
                                            val_b = obj_b.evaluate(sol_x, sol_y)
                                            f_a = abs(
                                                float(val_a[0])
                                                if isinstance(val_a, np.ndarray)
                                                else float(val_a)
                                            )
                                            f_b = abs(
                                                float(val_b[0])
                                                if isinstance(val_b, np.ndarray)
                                                else float(val_b)
                                            )

                                            ok_a = True
                                            if hasattr(obj_a, "contains"):
                                                try:
                                                    ok_a = bool(
                                                        obj_a.contains(
                                                            sol_x, sol_y, tolerance=1e-2
                                                        )
                                                    )
                                                except Exception:
                                                    pass
                                            if (
                                                ok_a
                                                and hasattr(obj_a, "mask")
                                                and obj_a.mask is not None
                                            ):
                                                try:
                                                    ok_a = bool(
                                                        obj_a.mask(sol_x, sol_y)
                                                    )
                                                except Exception:
                                                    pass

                                            ok_b = True
                                            if hasattr(obj_b, "contains"):
                                                try:
                                                    ok_b = bool(
                                                        obj_b.contains(
                                                            sol_x, sol_y, tolerance=1e-2
                                                        )
                                                    )
                                                except Exception:
                                                    pass
                                            if (
                                                ok_b
                                                and hasattr(obj_b, "mask")
                                                and obj_b.mask is not None
                                            ):
                                                try:
                                                    ok_b = bool(
                                                        obj_b.mask(sol_x, sol_y)
                                                    )
                                                except Exception:
                                                    pass

                                            f_tol = (
                                                1.0e-5
                                                if (
                                                    not is_periodic_a
                                                    and not is_periodic_b
                                                )
                                                else 1e-2
                                            )

                                            dist_sq = (sol_x - px) ** 2 + (
                                                sol_y - py
                                            ) ** 2
                                            res_norm = math.sqrt(f_a**2 + f_b**2)
                                            if (
                                                res_norm < f_tol
                                                and ok_a
                                                and ok_b
                                                and dist_sq < 0.25
                                            ):
                                                px, py = sol_x, sol_y
                                                refined = True
                                                raw.append((px, py, res_norm))
                                    except Exception:
                                        pass

                                    if not refined:
                                        is_periodic_a = is_periodic_or_procedural(obj_a)
                                        is_periodic_b = is_periodic_or_procedural(obj_b)
                                        if not is_periodic_a and not is_periodic_b:
                                            # Reject false crossings arising from discrete chord near-misses
                                            continue

                                        # If refinement failed or is invalid, verify original approximate point
                                        ok_a = True
                                        if hasattr(obj_a, "contains"):
                                            try:
                                                ok_a = bool(
                                                    obj_a.contains(
                                                        px, py, tolerance=0.02
                                                    )
                                                )
                                            except Exception:
                                                pass
                                        if (
                                            ok_a
                                            and hasattr(obj_a, "mask")
                                            and obj_a.mask is not None
                                        ):
                                            try:
                                                ok_a = bool(obj_a.mask(px, py))
                                            except Exception:
                                                pass

                                        ok_b = True
                                        if hasattr(obj_b, "contains"):
                                            try:
                                                ok_b = bool(
                                                    obj_b.contains(
                                                        px, py, tolerance=0.02
                                                    )
                                                )
                                            except Exception:
                                                pass
                                        if (
                                            ok_b
                                            and hasattr(obj_b, "mask")
                                            and obj_b.mask is not None
                                        ):
                                            try:
                                                ok_b = bool(obj_b.mask(px, py))
                                            except Exception:
                                                pass

                                        if not (ok_a and ok_b):
                                            # Discard spurious point outside the trimmed domain
                                            continue

                                        try:
                                            val_a = obj_a.evaluate(px, py)
                                            val_b = obj_b.evaluate(px, py)
                                            f_a = abs(
                                                float(val_a[0])
                                                if isinstance(val_a, np.ndarray)
                                                else float(val_a)
                                            )
                                            f_b = abs(
                                                float(val_b[0])
                                                if isinstance(val_b, np.ndarray)
                                                else float(val_b)
                                            )
                                            res_norm = math.sqrt(f_a**2 + f_b**2)
                                        except Exception:
                                            res_norm = 1.0
                                        raw.append((px, py, res_norm))
                                else:
                                    raw.append((px, py, 1.0))

                    # Proximity tangent candidates check for near-touching / tangent curves
                    if True:
                        pts_a_sub = _subsample(pts_a)
                        pts_b_sub = _subsample(pts_b)

                        # Build a 2D spatial binning grid for pts_b_sub
                        grid = {}
                        bin_size = 0.15
                        for pt_b in pts_b_sub:
                            bx = int(math.floor(pt_b[0] / bin_size))
                            by = int(math.floor(pt_b[1] / bin_size))
                            key = (bx, by)
                            if key not in grid:
                                grid[key] = []
                            grid[key].append(pt_b)

                        proximity_seeds = []
                        for pt_a in pts_a_sub:
                            ax = int(math.floor(pt_a[0] / bin_size))
                            ay = int(math.floor(pt_a[1] / bin_size))

                            # Query only the cell containing pt_a and its 8 adjacent neighbors
                            for dx_cell in (-1, 0, 1):
                                for dy_cell in (-1, 0, 1):
                                    neighbor_key = (ax + dx_cell, ay + dy_cell)
                                    if neighbor_key in grid:
                                        for pt_b in grid[neighbor_key]:
                                            dx = pt_a[0] - pt_b[0]
                                            dy = pt_a[1] - pt_b[1]
                                            dist_sq = dx * dx + dy * dy
                                            if (
                                                dist_sq < 0.0225
                                            ):  # 0.15^2 = 0.0225 (corresponds to distance < 0.15)
                                                px, py = (
                                                    (pt_a[0] + pt_b[0]) / 2.0,
                                                    (pt_a[1] + pt_b[1]) / 2.0,
                                                )
                                                # Avoid running redundant fsolve calls on nearby seeds
                                                if any(
                                                    abs(px - sx) < 0.02
                                                    and abs(py - sy) < 0.02
                                                    for sx, sy in proximity_seeds
                                                ):
                                                    continue
                                                proximity_seeds.append((px, py))
                                                if has_eval:
                                                    from scipy.optimize import fsolve

                                                    def intersection_system(p):
                                                        x_val, y_val = p[0], p[1]
                                                        val_a = obj_a.evaluate(
                                                            x_val, y_val
                                                        )
                                                        val_b = obj_b.evaluate(
                                                            x_val, y_val
                                                        )
                                                        f_a = (
                                                            float(val_a[0])
                                                            if isinstance(
                                                                val_a, np.ndarray
                                                            )
                                                            else float(val_a)
                                                        )
                                                        f_b = (
                                                            float(val_b[0])
                                                            if isinstance(
                                                                val_b, np.ndarray
                                                            )
                                                            else float(val_b)
                                                        )
                                                        return [f_a, f_b]

                                                    try:
                                                        is_periodic_a = (
                                                            is_periodic_or_procedural(
                                                                obj_a
                                                            )
                                                        )
                                                        is_periodic_b = (
                                                            is_periodic_or_procedural(
                                                                obj_b
                                                            )
                                                        )
                                                        xtol_val = 1e-6

                                                        sol, infodict, ier, mesg = (
                                                            fsolve(
                                                                intersection_system,
                                                                [px, py],
                                                                xtol=xtol_val,
                                                                full_output=True,
                                                            )
                                                        )
                                                        if ier in (1, 2, 3, 4, 5):
                                                            sol_x, sol_y = (
                                                                float(sol[0]),
                                                                float(sol[1]),
                                                            )
                                                            val_a = obj_a.evaluate(
                                                                sol_x, sol_y
                                                            )
                                                            val_b = obj_b.evaluate(
                                                                sol_x, sol_y
                                                            )
                                                            f_a = abs(
                                                                float(val_a[0])
                                                                if isinstance(
                                                                    val_a, np.ndarray
                                                                )
                                                                else float(val_a)
                                                            )
                                                            f_b = abs(
                                                                float(val_b[0])
                                                                if isinstance(
                                                                    val_b, np.ndarray
                                                                )
                                                                else float(val_b)
                                                            )

                                                            ok_a = True
                                                            if hasattr(
                                                                obj_a, "contains"
                                                            ):
                                                                try:
                                                                    ok_a = bool(
                                                                        obj_a.contains(
                                                                            sol_x,
                                                                            sol_y,
                                                                            tolerance=1e-3,
                                                                        )
                                                                    )
                                                                except Exception:
                                                                    pass
                                                            if (
                                                                ok_a
                                                                and hasattr(
                                                                    obj_a, "mask"
                                                                )
                                                                and obj_a.mask
                                                                is not None
                                                            ):
                                                                try:
                                                                    ok_a = bool(
                                                                        obj_a.mask(
                                                                            sol_x, sol_y
                                                                        )
                                                                    )
                                                                except Exception:
                                                                    pass

                                                            ok_b = True
                                                            if hasattr(
                                                                obj_b, "contains"
                                                            ):
                                                                try:
                                                                    ok_b = bool(
                                                                        obj_b.contains(
                                                                            sol_x,
                                                                            sol_y,
                                                                            tolerance=1e-3,
                                                                        )
                                                                    )
                                                                except Exception:
                                                                    pass
                                                            if (
                                                                ok_b
                                                                and hasattr(
                                                                    obj_b, "mask"
                                                                )
                                                                and obj_b.mask
                                                                is not None
                                                            ):
                                                                try:
                                                                    ok_b = bool(
                                                                        obj_b.mask(
                                                                            sol_x, sol_y
                                                                        )
                                                                    )
                                                                except Exception:
                                                                    pass

                                                            d_sq = (sol_x - px) ** 2 + (
                                                                sol_y - py
                                                            ) ** 2

                                                            f_tol_prox = (
                                                                1e-6
                                                                if (
                                                                    not is_periodic_a
                                                                    and not is_periodic_b
                                                                )
                                                                else 1e-3
                                                            )
                                                            res_norm = math.sqrt(
                                                                f_a**2 + f_b**2
                                                            )
                                                            if (
                                                                res_norm < f_tol_prox
                                                                and ok_a
                                                                and ok_b
                                                                and d_sq < 0.25
                                                            ):
                                                                raw.append(
                                                                    (
                                                                        sol_x,
                                                                        sol_y,
                                                                        res_norm,
                                                                    )
                                                                )
                                                    except Exception:
                                                        pass

        # Define a robust tangency checking utility for the active curve combination
        def is_tangent_at(x_val, y_val, h=1e-5):
            for id_a, id_b in combinations(polyline_lookup.keys(), 2):
                try:
                    obj_a = self.scene_manager.get_object(id_a)
                    obj_b = self.scene_manager.get_object(id_b)
                    if hasattr(obj_a, "evaluate") and hasattr(obj_b, "evaluate"):
                        df1_dx = (
                            obj_a.evaluate(x_val + h, y_val)
                            - obj_a.evaluate(x_val - h, y_val)
                        ) / (2.0 * h)
                        df1_dy = (
                            obj_a.evaluate(x_val, y_val + h)
                            - obj_a.evaluate(x_val, y_val - h)
                        ) / (2.0 * h)
                        df2_dx = (
                            obj_b.evaluate(x_val + h, y_val)
                            - obj_b.evaluate(x_val - h, y_val)
                        ) / (2.0 * h)
                        df2_dy = (
                            obj_b.evaluate(x_val, y_val + h)
                            - obj_b.evaluate(x_val, y_val - h)
                        ) / (2.0 * h)

                        df1_dx = (
                            float(df1_dx[0])
                            if isinstance(df1_dx, np.ndarray)
                            else float(df1_dx)
                        )
                        df1_dy = (
                            float(df1_dy[0])
                            if isinstance(df1_dy, np.ndarray)
                            else float(df1_dy)
                        )
                        df2_dx = (
                            float(df2_dx[0])
                            if isinstance(df2_dx, np.ndarray)
                            else float(df2_dx)
                        )
                        df2_dy = (
                            float(df2_dy[0])
                            if isinstance(df2_dy, np.ndarray)
                            else float(df2_dy)
                        )

                        norm1 = math.sqrt(df1_dx**2 + df1_dy**2)
                        norm2 = math.sqrt(df2_dx**2 + df2_dy**2)

                        if norm1 < 1e-8 or norm2 < 1e-8:
                            return True

                        cross_prod = abs(df1_dx * df2_dy - df1_dy * df2_dx)
                        normalized_det = cross_prod / (norm1 * norm2)
                        if normalized_det < 0.001:
                            return True
                except Exception:
                    pass
            return False

        any_periodic = False
        for obj_id in polyline_lookup.keys():
            try:
                obj = self.scene_manager.get_object(obj_id)
                if is_periodic_or_procedural(obj):
                    any_periodic = True
                    break
            except Exception:
                pass

        # Deduplicate: cluster points within tolerance, keep one per cluster
        # Boost deduplication tolerance to 0.35 in flat tangent zones to avoid multiple spurious hits
        kept: List[Tuple[float, float, float]] = []
        for pt in raw:
            pt_x, pt_y, pt_res = pt
            is_dup = False
            for k in kept:
                k_x, k_y, k_res = k
                is_tangent = is_tangent_at(pt_x, pt_y) or is_tangent_at(k_x, k_y)
                if any_periodic:
                    local_tol = 0.15 if is_tangent else 0.002
                else:
                    # For non-periodic/algebraic/conic curves, match the analytical solver
                    if is_tangent:
                        # If both points are highly refined, reduce tolerance to avoid collapsing near-tangent points
                        if pt_res < 1e-4 and k_res < 1e-4:
                            local_tol = 0.0005
                        else:
                            local_tol = 0.005
                    else:
                        local_tol = 0.001

                if abs(pt_x - k_x) < local_tol and abs(pt_y - k_y) < local_tol:
                    is_dup = True
                    break
            if not is_dup:
                kept.append(pt)

        return [
            {"label": f"I{i + 1}", "x": float(x), "y": float(y)}
            for i, (x, y, _) in enumerate(kept)
        ]

    def _polyline_segments(
        self, points: List[List[float]]
    ) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        if len(points) < 2:
            return segments
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            if (
                np.isfinite(p1[0])
                and np.isfinite(p1[1])
                and np.isfinite(p2[0])
                and np.isfinite(p2[1])
            ):
                segments.append(((p1[0], p1[1]), (p2[0], p2[1])))
        return segments

    def _segment_intersection(self, seg_a, seg_b) -> Optional[Tuple[float, float]]:
        (x1, y1), (x2, y2) = seg_a
        (x3, y3), (x4, y4) = seg_b

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-9:
            return None

        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        if self._point_on_segment(px, py, seg_a) and self._point_on_segment(
            px, py, seg_b
        ):
            return float(px), float(py)
        return None

    def _point_on_segment(self, px: float, py: float, segment) -> bool:
        (x1, y1), (x2, y2) = segment
        if (min(x1, x2) - 1e-6) <= px <= (max(x1, x2) + 1e-6) and (
            min(y1, y2) - 1e-6
        ) <= py <= (max(y1, y2) + 1e-6):
            # Check collinearity via cross product
            cross = (px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)
            return abs(cross) <= 1e-3
        return False

    def _sample_boundary_points(
        self, boundary_curve, bounds: Tuple[float, float, float, float], resolution: int
    ) -> Tuple[List[List[float]], bool]:
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
            if hasattr(boundary_curve, "_is_square") and boundary_curve._is_square:
                # Rectangle boundary
                bounds_rect = boundary_curve._square_bounds
                xmin_r, xmax_r, ymin_r, ymax_r = bounds_rect
                points = [
                    [xmin_r, ymin_r],
                    [xmax_r, ymin_r],
                    [xmax_r, ymax_r],
                    [xmin_r, ymax_r],
                    [xmin_r, ymin_r],  # Close the rectangle
                ]
                return points, True

            # If the boundary is a composite curve (like a polygon), sample its segments in order
            if hasattr(boundary_curve, "segments"):
                points = []
                num_segs = len(boundary_curve.segments)
                pts_per_seg = max(5, resolution // num_segs)
                for segment in boundary_curve.segments:
                    seg_pts = []

                    # Try using segment's own polyline approximation first if available and curved
                    is_curved = getattr(segment, "is_curved", True)
                    if callable(is_curved):
                        is_curved = is_curved()

                    if is_curved and hasattr(segment, "get_polyline_approximation"):
                        try:
                            try:
                                pts = segment.get_polyline_approximation(
                                    bounds, pts_per_seg
                                )
                            except TypeError:
                                pts = segment.get_polyline_approximation(
                                    resolution=pts_per_seg
                                )
                            if pts:
                                seg_pts = [[float(p[0]), float(p[1])] for p in pts]
                        except Exception:
                            pass

                    # Fallback to linear endpoints if not curved or if polyline failed
                    if not seg_pts and hasattr(segment, "get_endpoints"):
                        try:
                            endpoints = segment.get_endpoints()
                            if endpoints and len(endpoints) == 2:
                                (x0, y0), (x1, y1) = endpoints
                                for t in np.linspace(0, 1, pts_per_seg):
                                    seg_pts.append(
                                        [
                                            float(x0 + t * (x1 - x0)),
                                            float(y0 + t * (y1 - y0)),
                                        ]
                                    )
                        except Exception:
                            pass

                    if not seg_pts:
                        # Fallback for this segment: use its bounding box
                        try:
                            bbox = segment.bounding_box()
                            s_xmin, s_xmax, s_ymin, s_ymax = bbox
                            # Simple line from min to max corner as fallback
                            for t in np.linspace(0, 1, pts_per_seg):
                                seg_pts.append(
                                    [
                                        float(s_xmin + t * (s_xmax - s_xmin)),
                                        float(s_ymin + t * (s_ymax - s_ymin)),
                                    ]
                                )
                        except Exception:
                            pass

                    points.extend(seg_pts)

                if len(points) > 2:
                    is_closed = False
                    if hasattr(boundary_curve, "is_closed"):
                        if callable(boundary_curve.is_closed):
                            is_closed = boundary_curve.is_closed()
                        else:
                            is_closed = bool(boundary_curve.is_closed)
                    else:
                        is_closed = True
                    return points, is_closed

            # For circles and other curves, use a more robust approach
            # Try parametric sampling if available
            if hasattr(boundary_curve, "get_parametric_points"):
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
                            val = val[0] if len(val) > 0 else float("inf")
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
                (center_x, center_y - 1),
            ]

            valid_points = []
            for x, y in test_points:
                try:
                    val = boundary_curve.evaluate(x, y)
                    if isinstance(val, (list, np.ndarray)):
                        val = val[0] if len(val) > 0 else float("inf")
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

            info = {"id": obj_id, "type": type(obj).__name__, "style": style}

            # Add parameter information if available
            if hasattr(obj, "list_parameters"):
                try:
                    parameters = obj.get_parameters()
                    info["parameters"] = parameters
                    info["parameter_names"] = obj.list_parameters()
                except Exception:
                    pass

            # Add bounds if available
            if hasattr(obj, "get_bounds"):
                try:
                    bounds = obj.get_bounds()
                    if bounds:
                        info["bounds"] = bounds
                except Exception:
                    pass

            # Add dependencies
            deps = self.scene_manager.get_dependencies(obj_id)
            if deps["dependents"] or deps["sources"]:
                info["dependencies"] = deps

            return info

        except Exception as e:
            return {"id": obj_id, "error": str(e)}

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
        total_cache_size = sum(info["cache_size_mb"] for info in cache_info.values())

        # Calculate scene bounds
        scene_bounds = self.get_scene_bounds()

        return {
            "object_count": len(objects),
            "object_types": type_counts,
            "group_count": len(self.scene_manager._groups),
            "dependency_count": len(self.scene_manager._dependencies),
            "animation_cache_count": len(cache_info),
            "total_cache_size_mb": total_cache_size,
            "scene_bounds": scene_bounds,
            "objects": objects,
        }
