"""
Generate Gallery - Creates 100 test case scenes of increasing complexity,
saves them to JSON, renders them to PNG, and creates metadata.json.
"""

import sys
import os
import time
import json
from pathlib import Path
import numpy as np
import sympy as sp
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scene_management.scene_manager import SceneManager
from graphics_backend.graphics_interface import GraphicsBackendInterface
from geometry.conic_section import ConicSection
from geometry.implicit_curve import ImplicitCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.superellipse import Superellipse
from geometry.area_region import AreaRegion
from geometry.base_field import BaseField, CurveField, BlendedField
from geometry.field_strategy import SignedDistanceField, OccupancyField
from geometry.factories import (
    create_polygon_from_edges,
    create_square_from_edges,
    create_circle_from_quarters,
    create_L_shape,
    create_T_shape,
    create_triangle,
    create_house_shape,
    create_zigzag_pattern,
    create_staircase,
    create_figure_eight,
    create_circle_line_hybrid,
    create_ellipse_parabola_hybrid,
    create_multi_conic_flower,
    create_superellipse_circle_hybrid,
    create_spiral_approximation,
    create_heart_shape,
)

_x, _y = sp.symbols("x y")

# Output directories
GALLERY_DIR = Path(ROOT) / "tests" / "gallery"
SCENES_DIR = GALLERY_DIR / "scenes"
IMAGES_DIR = GALLERY_DIR / "images"

SCENES_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def _circle(cx=0, cy=0, r=1):
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _ellipse(cx=0, cy=0, a=2, b=1):
    return ConicSection((_x - cx) ** 2 / a**2 + (_y - cy) ** 2 / b**2 - 1, (_x, _y))


def _parabola(a=1):
    return ImplicitCurve(_y - a * _x**2, (_x, _y))


def _line(a=1, b=-1, c=0):
    return ImplicitCurve(a * _x + b * _y + c, (_x, _y))


def render_and_time(sm, scene_id, bounds=(-5, 5, -5, 5)):
    """Render a SceneManager scene, measure total time from start to end, and save image."""
    import colorsys

    def convert_color(color_str):
        if not isinstance(color_str, str):
            return color_str
        if color_str.startswith("hsl"):
            try:
                # parse hsl(h, s%, l%)
                parts = color_str.replace("hsl(", "").replace(")", "").split(",")
                h = float(parts[0].strip()) / 360.0
                s = float(parts[1].replace("%", "").strip()) / 100.0
                luminance = float(parts[2].replace("%", "").strip()) / 100.0
                r, g, b = colorsys.hls_to_rgb(h, luminance, s)
                return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            except Exception:
                pass
        return color_str

    start_time = time.perf_counter()

    # Save scene JSON
    scene_file_path = SCENES_DIR / f"{scene_id}.json"
    sm.save_scene(str(scene_file_path))

    # Render
    backend = GraphicsBackendInterface(sm)
    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)

    xmin, xmax, ymin, ymax = bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # Apply subtle viewport frame and background paper tone for scenes containing fields
    has_fields = any(
        isinstance(sm.get_object(obj_id), BaseField) for obj_id in sm.list_objects()
    )
    if has_fields:
        ax.set_facecolor("#fafafb")  # soft light warm paper tone background
        for spine in ax.spines.values():
            spine.set_color("#cccccc")
            spine.set_linewidth(1.5)
            spine.set_visible(True)
    else:
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_color("#e0e0e0")
            spine.set_linewidth(1.0)
            spine.set_visible(True)

    # 1. Filled regions
    region_data = backend.get_region_data(bounds=bounds, resolution=(60, 60))
    if region_data:
        rx = np.linspace(xmin, xmax, 60)
        ry = np.linspace(ymin, ymax, 60)
        RX, RY = np.meshgrid(rx, ry)
        for obj_id, data in region_data.items():
            if data.get("inside_mask") is not None:
                style = sm.get_style(obj_id) or {}
                fill_color = style.get("fill_color", style.get("color", "#1f77b4"))
                fill_color = convert_color(fill_color)
                fill_alpha = style.get("fill_alpha", 0.25)
                mask = np.array(data["inside_mask"], dtype=bool)
                ax.contourf(
                    RX,
                    RY,
                    mask.astype(float),
                    levels=[0.5, 1.5],
                    colors=[fill_color],
                    alpha=fill_alpha,
                )

    # 2. Curve paths
    curve_data = backend.get_curve_paths(bounds=bounds, resolution=150)
    for obj_id, data in curve_data.items():
        paths = data.get("paths", [])
        if not paths and data.get("points"):
            paths = [data["points"]]
        style = sm.get_style(obj_id) or {}
        color = style.get("color", "#1f77b4")
        color = convert_color(color)
        linewidth = style.get("linewidth", 2)
        alpha = style.get("alpha", 1.0)
        linestyle = style.get("linestyle", "-")
        for path in paths:
            if path and len(path) >= 2:
                pts = np.array(path)
                ax.plot(
                    pts[:, 0],
                    pts[:, 1],
                    color=color,
                    linewidth=linewidth,
                    alpha=alpha,
                    linestyle=linestyle,
                )

    # 3. Scalar fields
    try:
        field_data = backend.get_field_data(bounds=bounds, resolution=(100, 100))
        if field_data:
            fx = np.linspace(xmin, xmax, 100)
            fy = np.linspace(ymin, ymax, 100)
            FX, FY = np.meshgrid(fx, fy)
            for obj_id, data in field_data.items():
                if "error" in data or "data" not in data:
                    continue
                obj = sm.get_object(obj_id)
                if not isinstance(obj, BaseField):
                    continue

                style = sm.get_style(obj_id) or {}
                color = style.get("color", "#1f77b4")
                color = convert_color(color)
                fill_color = style.get("fill_color", color)
                fill_color = convert_color(fill_color)
                fill_alpha = style.get("fill_alpha", 0.3)

                Z = np.array(data["data"])

                if isinstance(obj, SignedDistanceField):
                    try:
                        # Signed Distance Field: Beautiful full-domain continuous gradient (diverging coolwarm colormap)
                        limit = max(abs(np.nanmin(Z)), abs(np.nanmax(Z)))
                        limit = min(max(limit, 1.0), 5.0)
                        levels = np.linspace(-limit, limit, 15)
                        ax.contourf(
                            FX,
                            FY,
                            Z,
                            levels=levels,
                            cmap="coolwarm",
                            alpha=0.35,
                            extend="both",
                        )
                        # Draw nested helper contour lines to make distance steps explicitly clear
                        ax.contour(
                            FX,
                            FY,
                            Z,
                            levels=[-2.0, -1.0, 1.0, 2.0],
                            colors=["#555555"],
                            linewidths=0.5,
                            linestyles="dashed",
                            alpha=0.4,
                        )
                        # Highlight zero level-set boundary
                        ax.contour(
                            FX, FY, Z, levels=[0.0], colors=[color], linewidths=2.5
                        )
                    except Exception:
                        pass
                elif isinstance(obj, OccupancyField):
                    try:
                        # Occupancy Field: Two contrasting flat colors covering the entire domain
                        # Outside region (below 0.5): soft light gray
                        ax.contourf(
                            FX,
                            FY,
                            Z,
                            levels=[-1e9, 0.5],
                            colors=["#eaeaea"],
                            alpha=0.25,
                        )
                        # Inside region (above 0.5): primary style color
                        ax.contourf(
                            FX,
                            FY,
                            Z,
                            levels=[0.5, 1e9],
                            colors=[fill_color],
                            alpha=fill_alpha,
                        )
                        # Boundary contour line - drawn as dashed to signal occupancy threshold
                        ax.contour(
                            FX,
                            FY,
                            Z,
                            levels=[0.5],
                            colors=[color],
                            linewidths=2.5,
                            linestyles="dashed",
                        )
                    except Exception:
                        pass
                elif isinstance(obj, CurveField):
                    try:
                        # Curve Field: Solid interior only (transparent outside)
                        ax.contourf(
                            FX,
                            FY,
                            Z,
                            levels=[-1e9, 0.0],
                            colors=[fill_color],
                            alpha=fill_alpha,
                        )
                        ax.contour(
                            FX, FY, Z, levels=[0.0], colors=[color], linewidths=2
                        )
                    except Exception:
                        pass
                elif isinstance(obj, BlendedField):
                    try:
                        # Blended Field: Continuous gradient showing the multi-shape blending/intersection profile
                        limit = max(abs(np.nanmin(Z)), abs(np.nanmax(Z)))
                        limit = min(max(limit, 1.0), 5.0)
                        levels = np.linspace(-limit, limit, 15)
                        ax.contourf(
                            FX,
                            FY,
                            Z,
                            levels=levels,
                            cmap="coolwarm",
                            alpha=0.35,
                            extend="both",
                        )
                        ax.contour(
                            FX, FY, Z, levels=[0.0], colors=[color], linewidths=2
                        )
                    except Exception:
                        pass
    except Exception as fe:
        print(f"       [Warning] Field rendering encountered error: {fe}")

    ax.set_title(f"{scene_id}", fontsize=10, color="#666")
    fig.tight_layout()

    # Save PNG
    image_file_path = IMAGES_DIR / f"{scene_id}.png"
    fig.savefig(str(image_file_path), dpi=100, bbox_inches="tight")
    plt.close(fig)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000.0
    return elapsed_ms, f"scenes/{scene_id}.json", f"images/{scene_id}.png"


def main():
    print("[Start] Starting generation of 100 test cases...")

    # Load existing metadata for resumability
    existing_meta = {}
    metadata_path = GALLERY_DIR / "metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                loaded = json.load(f)
                existing_meta = {item["id"]: item for item in loaded}
            print(
                f"[Start] Loaded {len(existing_meta)} existing scene metadata records for resumability."
            )
        except Exception as e:
            print(f"[Start] Could not load existing metadata: {e}")

    metadata = []

    # Loop over 100 cases
    for idx in range(1, 101):
        scene_id = f"scene_{idx:03d}"
        sm = SceneManager()

        # Determine complexity tier and details
        if idx <= 10:
            tier = 1
            tier_name = "Simple Curves"
            # 1. Circle
            if idx == 1:
                name = "Unit Circle"
                desc = "A standard unit circle centered at the origin."
                sm.add_object(
                    "circle", _circle(0, 0, 1), {"color": "#1f77b4", "linewidth": 2.5}
                )
            # 2. Ellipse
            elif idx == 2:
                name = "Ellipse (a=3, b=1)"
                desc = "An axis-aligned ellipse centered at the origin."
                sm.add_object(
                    "ellipse",
                    _ellipse(0, 0, 3, 1),
                    {"color": "#9467bd", "linewidth": 2.5},
                )
            # 3. Parabola
            elif idx == 3:
                name = "Upward Parabola"
                desc = "Standard upward-opening parabola y - x^2 = 0."
                sm.add_object(
                    "parabola", _parabola(1), {"color": "#ff7f0e", "linewidth": 2.5}
                )
            # 4. Diagonal Line
            elif idx == 4:
                name = "Diagonal Line"
                desc = "A straight diagonal line passing through the origin."
                sm.add_object(
                    "line", _line(1, -1, 0), {"color": "#2ca02c", "linewidth": 2.5}
                )
            # 5. Triangle
            elif idx == 5:
                name = "Standard Triangle"
                desc = "Triangle constructed from three connected line segments."
                sm.add_object(
                    "triangle",
                    create_triangle(),
                    {"color": "#d62728", "linewidth": 2.5},
                )
            # 6. Square
            elif idx == 6:
                name = "Square (2x2)"
                desc = "A 2x2 square boundary centered at the origin."
                sm.add_object(
                    "square",
                    create_square_from_edges((-1, -1), (1, 1)),
                    {"color": "#e377c2", "linewidth": 2.5},
                )
            # 7. L-shape
            elif idx == 7:
                name = "L-Shape Segment"
                desc = "L-shape constructed from two perpendicular segments."
                sm.add_object(
                    "l_shape", create_L_shape(), {"color": "#bcbd22", "linewidth": 2.5}
                )
            # 8. T-shape
            elif idx == 8:
                name = "T-Shape Segment"
                desc = (
                    "T-shape constructed from three connected perpendicular segments."
                )
                sm.add_object(
                    "t_shape", create_T_shape(), {"color": "#17becf", "linewidth": 2.5}
                )
            # 9. Zigzag
            elif idx == 9:
                name = "Zigzag Segment"
                desc = "Zigzag pattern connecting multiple vertices."
                sm.add_object(
                    "zigzag",
                    create_zigzag_pattern(),
                    {"color": "#8c564b", "linewidth": 2.5},
                )
            # 10. Staircase
            else:
                name = "Staircase Segment"
                desc = "Perpendicular staircase step pattern."
                sm.add_object(
                    "staircase",
                    create_staircase(),
                    {"color": "#7f7f7f", "linewidth": 2.5},
                )

        elif idx <= 25:
            tier = 2
            tier_name = "Dual Shapes & Hybrids"
            # 11. Figure Eight
            if idx == 11:
                name = "Figure Eight"
                desc = "Continuous closed figure-eight shape using circular arcs."
                sm.add_object(
                    "figure_eight",
                    create_figure_eight(),
                    {"color": "#1f77b4", "linewidth": 2.5},
                )
            # 12. D-Shape Hybrid
            elif idx == 12:
                name = "D-Shape Hybrid"
                desc = "D-shape combining a semicircle with a straight boundary."
                sm.add_object(
                    "d_shape",
                    create_circle_line_hybrid(),
                    {"color": "#2ca02c", "linewidth": 2.5},
                )
            # 13. Egg-Shape Hybrid
            elif idx == 13:
                name = "Egg-Shape Hybrid"
                desc = "Egg-like hybrid shape combining ellipse and parabola arcs."
                sm.add_object(
                    "egg_shape",
                    create_ellipse_parabola_hybrid(),
                    {"color": "#ff7f0e", "linewidth": 2.5},
                )
            # 14. Concentric Circles
            elif idx == 14:
                name = "Concentric Circles"
                desc = "Two concentric circles of radius 1 and 2."
                sm.add_object("circle1", _circle(0, 0, 1.0), {"color": "#1f77b4"})
                sm.add_object("circle2", _circle(0, 0, 2.0), {"color": "#aec7e8"})
            # 15. Intersecting Circles
            elif idx == 15:
                name = "Intersecting Circles"
                desc = "Two intersecting circles at x=-0.75 and x=0.75."
                sm.add_object("c1", _circle(-0.75, 0, 1.25), {"color": "#ff7f0e"})
                sm.add_object("c2", _circle(0.75, 0, 1.25), {"color": "#ffbb78"})
            # 16. Concentric Ellipses
            elif idx == 16:
                name = "Concentric Ellipses"
                desc = "Concentric ellipses with different semi-axes."
                sm.add_object("e1", _ellipse(0, 0, 2.0, 1.0), {"color": "#9467bd"})
                sm.add_object("e2", _ellipse(0, 0, 3.5, 1.75), {"color": "#c5b0d5"})
            # 17. Offset Squares
            elif idx == 17:
                name = "Offset Squares"
                desc = "Two squares offset from the origin."
                sm.add_object(
                    "sq1",
                    create_square_from_edges((-2, -2), (0, 0)),
                    {"color": "#d62728"},
                )
                sm.add_object(
                    "sq2",
                    create_square_from_edges((0, 0), (2, 2)),
                    {"color": "#ff9896"},
                )
            # 18. Parallel Lines
            elif idx == 18:
                name = "Parallel Lines"
                desc = "Two parallel diagonal lines."
                sm.add_object("line1", _line(1, -1, -1), {"color": "#2ca02c"})
                sm.add_object("line2", _line(1, -1, 1), {"color": "#98df8a"})
            # 19. Intersecting Circle & Line
            elif idx == 19:
                name = "Intersecting Circle & Line"
                desc = "A unit circle intersected by a vertical line at x=0.5."
                sm.add_object("circle", _circle(0, 0, 1.5), {"color": "#1f77b4"})
                sm.add_object("line", _line(1, 0, -0.75), {"color": "#d62728"})
            # 20. Circle & Ellipse Cross
            elif idx == 20:
                name = "Circle & Ellipse Cross"
                desc = "A circle and a stretched ellipse intersecting."
                sm.add_object("circle", _circle(0, 0, 1.5), {"color": "#17becf"})
                sm.add_object(
                    "ellipse", _ellipse(0, 0, 3.0, 0.75), {"color": "#bcbd22"}
                )
            # 21. Triangle inside Circle
            elif idx == 21:
                name = "Triangle inside Circle"
                desc = "A triangle centered inside a larger outer circle."
                sm.add_object("circle", _circle(0, 0, 2.5), {"color": "#1f77b4"})
                sm.add_object("triangle", create_triangle(), {"color": "#d62728"})
            # 22. Square inside Circle
            elif idx == 22:
                name = "Square inside Circle"
                desc = "A square nested inside an outer circle."
                sm.add_object("circle", _circle(0, 0, 2.2), {"color": "#e377c2"})
                sm.add_object(
                    "square",
                    create_square_from_edges((-1, -1), (1, 1)),
                    {"color": "#7f7f7f"},
                )
            # 23. Superellipse (n=3)
            elif idx == 23:
                name = "Superellipse (n=3)"
                desc = "A superellipse curve with parameter exponent n=3."
                sm.add_object(
                    "se",
                    Superellipse(2.0, 1.5, 3.0),
                    {"color": "#8c564b", "linewidth": 2.5},
                )
            # 24. Three Circles
            elif idx == 24:
                name = "Three Circles"
                desc = "Three circles forming a triangular alignment."
                sm.add_object("c1", _circle(0, 1.0, 1.0), {"color": "#1f77b4"})
                sm.add_object("c2", _circle(-1.0, -0.5, 1.0), {"color": "#2ca02c"})
                sm.add_object("c3", _circle(1.0, -0.5, 1.0), {"color": "#ff7f0e"})
            # 25. Double Parabola
            else:
                name = "Double Parabola"
                desc = "Two parabolas opening in opposite directions."
                sm.add_object("p1", _parabola(0.5), {"color": "#ff7f0e"})
                sm.add_object(
                    "p2",
                    ImplicitCurve(-_y - 0.5 * _x**2 + 2, (_x, _y)),
                    {"color": "#aec7e8"},
                )

        elif idx <= 40:
            tier = 3
            tier_name = "Composite & Spiral Shapes"
            # 26-29. Multi-Conic Flowers
            if idx == 26:
                name = "Flower (3 petals)"
                desc = "Multi-conic flower shape with 3 alternating petals."
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(3),
                    {"color": "#d62728", "linewidth": 2},
                )
            elif idx == 27:
                name = "Flower (4 petals)"
                desc = "Multi-conic flower shape with 4 alternating petals."
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(4),
                    {"color": "#9467bd", "linewidth": 2},
                )
            elif idx == 28:
                name = "Flower (5 petals)"
                desc = "Multi-conic flower shape with 5 alternating petals."
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(5),
                    {"color": "#e377c2", "linewidth": 2},
                )
            elif idx == 29:
                name = "Flower (6 petals)"
                desc = "Multi-conic flower shape with 6 alternating petals."
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(6),
                    {"color": "#17becf", "linewidth": 2},
                )
            # 30-32. Spiral Approximations
            elif idx == 30:
                name = "Spiral (1 turn)"
                desc = (
                    "Spiral approximation using quarter-circle segments (1 full turn)."
                )
                sm.add_object(
                    "spiral",
                    create_spiral_approximation(1),
                    {"color": "#bcbd22", "linewidth": 2},
                )
            elif idx == 31:
                name = "Spiral (2 turns)"
                desc = (
                    "Spiral approximation using quarter-circle segments (2 full turns)."
                )
                sm.add_object(
                    "spiral",
                    create_spiral_approximation(2),
                    {"color": "#bcbd22", "linewidth": 2},
                )
            elif idx == 32:
                name = "Spiral (3 turns)"
                desc = (
                    "Spiral approximation using quarter-circle segments (3 full turns)."
                )
                sm.add_object(
                    "spiral",
                    create_spiral_approximation(3),
                    {"color": "#bcbd22", "linewidth": 2},
                )
            # 33. Superellipse-Circle Hybrid
            elif idx == 33:
                name = "Superellipse-Circle Hybrid"
                desc = "Rounded square superellipse blended with circular arcs."
                sm.add_object(
                    "hybrid",
                    create_superellipse_circle_hybrid(),
                    {"color": "#ff7f0e", "linewidth": 2},
                )
            # 34. Heart Shape
            elif idx == 34:
                name = "Heart Shape"
                desc = "Beautiful heart shape using two circular lobes and a parabolic base."
                sm.add_object(
                    "heart",
                    create_heart_shape(),
                    {"color": "#d62728", "linewidth": 2.5},
                )
            # 35. House Shape
            elif idx == 35:
                name = "House Shape"
                desc = "Square base with a triangular roof, forming a continuous path."
                sm.add_object(
                    "house", create_house_shape(), {"color": "#8c564b", "linewidth": 2}
                )
            # 36. Nested Triangles
            elif idx == 36:
                name = "Nested Triangles"
                desc = "Three nested triangles of increasing sizes."
                for i in range(1, 4):
                    scale = i * 0.75
                    t = create_triangle()
                    sm.add_object(
                        f"tri_{i}", t, {"color": "#2ca02c", "linewidth": 1.5 * i}
                    )
            # 37. Overlapping Squares Grid
            elif idx == 37:
                name = "Overlapping Squares Grid"
                desc = "Four overlapping squares forming a window pane alignment."
                sm.add_object(
                    "sq1",
                    create_square_from_edges((-1.5, -1.5), (0.5, 0.5)),
                    {"color": "#aec7e8"},
                )
                sm.add_object(
                    "sq2",
                    create_square_from_edges((-0.5, -1.5), (1.5, 0.5)),
                    {"color": "#ffbb78"},
                )
                sm.add_object(
                    "sq3",
                    create_square_from_edges((-1.5, -0.5), (0.5, 1.5)),
                    {"color": "#98df8a"},
                )
                sm.add_object(
                    "sq4",
                    create_square_from_edges((-0.5, -0.5), (1.5, 1.5)),
                    {"color": "#ff9896"},
                )
            # 38. Spiral and Circle Nest
            elif idx == 38:
                name = "Spiral & Circle Nest"
                desc = "A 2-turn spiral centered within an outer bounding circle."
                sm.add_object(
                    "spiral", create_spiral_approximation(2), {"color": "#bcbd22"}
                )
                sm.add_object(
                    "circle", _circle(0, 0, 2.5), {"color": "#1f77b4", "linewidth": 2.5}
                )
            # 39. Multi-Intersecting Lines
            elif idx == 39:
                name = "Star Grid (4 Lines)"
                desc = "Four intersecting lines meeting at the origin."
                sm.add_object("l1", _line(1, 0, 0), {"color": "#ff7f0e"})
                sm.add_object("l2", _line(0, 1, 0), {"color": "#1f77b4"})
                sm.add_object("l3", _line(1, -1, 0), {"color": "#2ca02c"})
                sm.add_object("l4", _line(1, 1, 0), {"color": "#d62728"})
            # 40. Custom Hexagon
            else:
                name = "Polygon Hexagon"
                desc = "A regular-like convex hexagon constructed from polygonal edges."
                vertices = [
                    (1.5, 0),
                    (0.75, 1.3),
                    (-0.75, 1.3),
                    (-1.5, 0),
                    (-0.75, -1.3),
                    (0.75, -1.3),
                ]
                sm.add_object(
                    "hex",
                    create_polygon_from_edges(vertices),
                    {"color": "#17becf", "linewidth": 2.5},
                )

        elif idx <= 60:
            tier = 4
            tier_name = "Scalar Fields & Containment"
            # 41. Circle Region Field
            if idx == 41:
                name = "Circle Signed Distance Field"
                desc = "Signed distance field generated from a circular region."
                # Create AreaRegion
                c = create_circle_from_quarters((0, 0), 2.0)
                sm.add_object(
                    "circle_boundary", c, {"color": "#1f77b4", "linewidth": 1.5}
                )
                region = AreaRegion(c)
                sdf = SignedDistanceField(region, resolution=0.1)
                sm.add_object(
                    "circle_sdf", sdf, {"color": "#1f77b4", "fill_alpha": 0.3}
                )
            # 42. Rectangle Region Field
            elif idx == 42:
                name = "Rectangle Signed Distance Field"
                desc = "Signed distance field generated from a rectangular region."
                r = create_square_from_edges((-2, -1), (2, 1))
                sm.add_object(
                    "rect_boundary", r, {"color": "#d62728", "linewidth": 1.5}
                )
                region = AreaRegion(r)
                sdf = SignedDistanceField(region, resolution=0.1)
                sm.add_object(
                    "rect_sdf",
                    sdf,
                    {"color": "#d62728", "fill_alpha": 0.35, "fill_color": "salmon"},
                )
            # 43. Triangle Region Field
            elif idx == 43:
                name = "Triangle Signed Distance Field"
                desc = "Signed distance field generated from a triangular region."
                t = create_triangle()
                sm.add_object("tri_boundary", t, {"color": "#2ca02c", "linewidth": 1.5})
                region = AreaRegion(t)
                sdf = SignedDistanceField(region, resolution=0.1)
                sm.add_object(
                    "tri_sdf",
                    sdf,
                    {"color": "#2ca02c", "fill_alpha": 0.3, "fill_color": "lightgreen"},
                )
            # 44. Circle Occupancy Field
            elif idx == 44:
                name = "Circle Occupancy Field"
                desc = "Binary occupancy field generated from a circular region."
                c = create_circle_from_quarters((0, 0), 1.5)
                sm.add_object(
                    "circle_boundary",
                    c,
                    {"color": "#1f77b4", "linewidth": 1.5, "linestyle": "dashed"},
                )
                region = AreaRegion(c)
                occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
                sm.add_object(
                    "circle_occ",
                    occ,
                    {"color": "#1f77b4", "fill_color": "skyblue", "fill_alpha": 0.5},
                )
            # 45. Square Occupancy Field
            elif idx == 45:
                name = "Square Occupancy Field"
                desc = "Binary occupancy field generated from a square region."
                s = create_square_from_edges((-1.2, -1.2), (1.2, 1.2))
                sm.add_object(
                    "square_boundary",
                    s,
                    {"color": "#e377c2", "linewidth": 1.5, "linestyle": "dashed"},
                )
                region = AreaRegion(s)
                occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
                sm.add_object(
                    "square_occ",
                    occ,
                    {"color": "#e377c2", "fill_color": "plum", "fill_alpha": 0.5},
                )
            # 46. Triangle Occupancy Field
            elif idx == 46:
                name = "Triangle Occupancy Field"
                desc = "Binary occupancy field generated from a triangular region."
                t = create_triangle()
                sm.add_object(
                    "tri_boundary",
                    t,
                    {"color": "#2ca02c", "linewidth": 1.5, "linestyle": "dashed"},
                )
                region = AreaRegion(t)
                occ = OccupancyField(region, inside_value=1.0, outside_value=0.0)
                sm.add_object(
                    "tri_occ",
                    occ,
                    {"color": "#2ca02c", "fill_color": "lightgreen", "fill_alpha": 0.5},
                )
            # 47. CurveField (Circle)
            elif idx == 47:
                name = "Circle Curve Field"
                desc = "Scalar field wrapping a standard circle's implicit equation."
                c = create_circle_from_quarters((0, 0), 1.5)
                sm.add_object(
                    "circle_boundary", c, {"color": "#1f77b4", "linewidth": 1.5}
                )
                cf = CurveField(_circle(0, 0, 1.5))
                sm.add_object("circle_cf", cf, {"color": "#1f77b4"})
            # 48. CurveField (Ellipse)
            elif idx == 48:
                name = "Ellipse Curve Field"
                desc = "Scalar field wrapping an ellipse's implicit equation."
                ellipse_curve = TrimmedImplicitCurve(
                    _ellipse(0, 0, 2.5, 1.25), lambda px, py: True
                )
                sm.add_object(
                    "ellipse_boundary",
                    ellipse_curve,
                    {"color": "#9467bd", "linewidth": 1.5},
                )
                cf = CurveField(_ellipse(0, 0, 2.5, 1.25))
                sm.add_object("ellipse_cf", cf, {"color": "#9467bd"})
            # 49. CurveField (Parabola)
            elif idx == 49:
                name = "Parabola Curve Field"
                desc = "Scalar field wrapping an upward parabola."
                parabola_curve = TrimmedImplicitCurve(
                    _parabola(0.5), lambda px, py: True
                )
                sm.add_object(
                    "parabola_boundary",
                    parabola_curve,
                    {"color": "#ff7f0e", "linewidth": 1.5},
                )
                cf = CurveField(_parabola(0.5))
                sm.add_object("parabola_cf", cf, {"color": "#ff7f0e"})
            # 50. CurveField (Line)
            elif idx == 50:
                name = "Line Curve Field"
                desc = "Scalar field wrapping a diagonal line."
                line_curve = TrimmedImplicitCurve(_line(1, -1, 0), lambda px, py: True)
                sm.add_object(
                    "line_boundary", line_curve, {"color": "#2ca02c", "linewidth": 1.5}
                )
                cf = CurveField(_line(1, -1, 0))
                sm.add_object("line_cf", cf, {"color": "#2ca02c"})
            # 51. Simple Blended Field (Add)
            elif idx == 51:
                name = "Blended Field: Circle + Ellipse (Add)"
                desc = "Addition blend of a circular curve field and an elliptical curve field."
                c = create_circle_from_quarters((-1.0, 0), 1.2)
                ellipse_curve = TrimmedImplicitCurve(
                    _ellipse(1.0, 0, 1.5, 1.0), lambda px, py: True
                )
                sm.add_object(
                    "circle_boundary", c, {"color": "#1f77b4", "linewidth": 1.5}
                )
                sm.add_object(
                    "ellipse_boundary",
                    ellipse_curve,
                    {"color": "#1f77b4", "linewidth": 1.5},
                )
                cf1 = CurveField(_circle(-1.0, 0, 1.2))
                cf2 = CurveField(_ellipse(1.0, 0, 1.5, 1.0))
                blend = BlendedField([cf1, cf2], operation="add")
                sm.add_object("blend_add", blend, {"color": "#1f77b4"})
            # 52. Simple Blended Field (Subtract)
            elif idx == 52:
                name = "Blended Field: Ellipse - Circle (Subtract)"
                desc = (
                    "Subtraction blend of a circular curve field from an ellipse field."
                )
                ellipse_curve = TrimmedImplicitCurve(
                    _ellipse(0, 0, 2.5, 1.5), lambda px, py: True
                )
                c = create_circle_from_quarters((0, 0), 1.0)
                sm.add_object(
                    "ellipse_boundary",
                    ellipse_curve,
                    {"color": "#9467bd", "linewidth": 1.5},
                )
                sm.add_object(
                    "circle_boundary", c, {"color": "#9467bd", "linewidth": 1.5}
                )
                cf1 = CurveField(_ellipse(0, 0, 2.5, 1.5))
                cf2 = CurveField(_circle(0, 0, 1.0))
                blend = BlendedField([cf1, cf2], operation="subtract")
                sm.add_object("blend_sub", blend, {"color": "#9467bd"})
            # 53. Simple Blended Field (Multiply)
            elif idx == 53:
                name = "Blended Field: Two Circles (Multiply)"
                desc = "Multiplicative blend of two circular curve fields."
                c1 = create_circle_from_quarters((-0.8, 0), 1.2)
                c2 = create_circle_from_quarters((0.8, 0), 1.2)
                sm.add_object(
                    "circle1_boundary", c1, {"color": "#ff7f0e", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle2_boundary", c2, {"color": "#ff7f0e", "linewidth": 1.5}
                )
                cf1 = CurveField(_circle(-0.8, 0, 1.2))
                cf2 = CurveField(_circle(0.8, 0, 1.2))
                blend = BlendedField([cf1, cf2], operation="multiply")
                sm.add_object("blend_mul", blend, {"color": "#ff7f0e"})
            # 54. Simple Blended Field (Min)
            elif idx == 54:
                name = "Blended Field: Two Circles (Min/Union)"
                desc = "Minimum blend of two circular fields, representing shape union."
                c1 = create_circle_from_quarters((-0.8, 0), 1.2)
                c2 = create_circle_from_quarters((0.8, 0), 1.2)
                sm.add_object(
                    "circle1_boundary", c1, {"color": "#d62728", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle2_boundary", c2, {"color": "#d62728", "linewidth": 1.5}
                )
                cf1 = CurveField(_circle(-0.8, 0, 1.2))
                cf2 = CurveField(_circle(0.8, 0, 1.2))
                blend = BlendedField([cf1, cf2], operation="min")
                sm.add_object("blend_min", blend, {"color": "#d62728"})
            # 55. Simple Blended Field (Max)
            elif idx == 55:
                name = "Blended Field: Two Circles (Max/Intersection)"
                desc = "Maximum blend of two circular fields, representing shape intersection."
                c1 = create_circle_from_quarters((-0.8, 0), 1.2)
                c2 = create_circle_from_quarters((0.8, 0), 1.2)
                sm.add_object(
                    "circle1_boundary", c1, {"color": "#2ca02c", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle2_boundary", c2, {"color": "#2ca02c", "linewidth": 1.5}
                )
                cf1 = CurveField(_circle(-0.8, 0, 1.2))
                cf2 = CurveField(_circle(0.8, 0, 1.2))
                blend = BlendedField([cf1, cf2], operation="max")
                sm.add_object("blend_max", blend, {"color": "#2ca02c"})
            # 56. Simple Blended Field (Average)
            elif idx == 56:
                name = "Blended Field: Two Circles (Average)"
                desc = "Average blend of two circular fields."
                c1 = create_circle_from_quarters((-0.8, 0), 1.2)
                c2 = create_circle_from_quarters((0.8, 0), 1.2)
                sm.add_object(
                    "circle1_boundary", c1, {"color": "#e377c2", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle2_boundary", c2, {"color": "#e377c2", "linewidth": 1.5}
                )
                cf1 = CurveField(_circle(-0.8, 0, 1.2))
                cf2 = CurveField(_circle(0.8, 0, 1.2))
                blend = BlendedField([cf1, cf2], operation="average")
                sm.add_object("blend_avg", blend, {"color": "#e377c2"})
            # 57. Blended Signed Distance Fields (Min/Union)
            elif idx == 57:
                name = "Blended SDF: Square + Circle (Min)"
                desc = "Minimum blend of a square distance field and a circular distance field."
                s = create_square_from_edges((-1.5, -1.5), (0.5, 0.5))
                c = create_circle_from_quarters((0.5, 0.5), 1.25)
                sm.add_object(
                    "square_boundary", s, {"color": "#17becf", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle_boundary", c, {"color": "#17becf", "linewidth": 1.5}
                )
                sdf1 = SignedDistanceField(AreaRegion(s), resolution=0.1)
                sdf2 = SignedDistanceField(AreaRegion(c), resolution=0.1)
                blend = BlendedField([sdf1, sdf2], operation="min")
                sm.add_object(
                    "blend_sdf_min", blend, {"color": "#17becf", "fill_alpha": 0.3}
                )
            # 58. Blended Signed Distance Fields (Max/Intersection)
            elif idx == 58:
                name = "Blended SDF: Square & Circle (Max)"
                desc = "Maximum blend of a square distance field and a circular distance field."
                s = create_square_from_edges((-1.5, -1.5), (0.5, 0.5))
                c = create_circle_from_quarters((0.5, 0.5), 1.25)
                sm.add_object(
                    "square_boundary", s, {"color": "#bcbd22", "linewidth": 1.5}
                )
                sm.add_object(
                    "circle_boundary", c, {"color": "#bcbd22", "linewidth": 1.5}
                )
                sdf1 = SignedDistanceField(AreaRegion(s), resolution=0.1)
                sdf2 = SignedDistanceField(AreaRegion(c), resolution=0.1)
                blend = BlendedField([sdf1, sdf2], operation="max")
                sm.add_object(
                    "blend_sdf_max",
                    blend,
                    {"color": "#bcbd22", "fill_alpha": 0.3, "fill_color": "yellow"},
                )
            # 59. Blended Occupancy Fields (Max/Union)
            elif idx == 59:
                name = "Blended Occupancy: Two Circles (Max)"
                desc = (
                    "Maximum blend of two occupancy fields, representing binary union."
                )
                c1 = create_circle_from_quarters((-0.75, 0), 1.25)
                c2 = create_circle_from_quarters((0.75, 0), 1.25)
                sm.add_object(
                    "circle1_boundary",
                    c1,
                    {"color": "#1f77b4", "linewidth": 1.5, "linestyle": "dashed"},
                )
                sm.add_object(
                    "circle2_boundary",
                    c2,
                    {"color": "#1f77b4", "linewidth": 1.5, "linestyle": "dashed"},
                )
                occ1 = OccupancyField(AreaRegion(c1))
                occ2 = OccupancyField(AreaRegion(c2))
                blend = BlendedField([occ1, occ2], operation="max")
                sm.add_object(
                    "blend_occ_max",
                    blend,
                    {"color": "#1f77b4", "fill_color": "skyblue", "fill_alpha": 0.5},
                )
            # 60. Blended Occupancy Fields (Min/Intersection)
            else:
                name = "Blended Occupancy: Two Circles (Min)"
                desc = "Minimum blend of two occupancy fields, representing binary intersection."
                c1 = create_circle_from_quarters((-0.75, 0), 1.25)
                c2 = create_circle_from_quarters((0.75, 0), 1.25)
                sm.add_object(
                    "circle1_boundary",
                    c1,
                    {"color": "#2ca02c", "linewidth": 1.5, "linestyle": "dashed"},
                )
                sm.add_object(
                    "circle2_boundary",
                    c2,
                    {"color": "#2ca02c", "linewidth": 1.5, "linestyle": "dashed"},
                )
                occ1 = OccupancyField(AreaRegion(c1))
                occ2 = OccupancyField(AreaRegion(c2))
                blend = BlendedField([occ1, occ2], operation="min")
                sm.add_object(
                    "blend_occ_min",
                    blend,
                    {"color": "#2ca02c", "fill_color": "lightgreen", "fill_alpha": 0.5},
                )

        elif idx <= 80:
            tier = 5
            tier_name = "Deep Dependency Trees"
            # 61. Two level dependency chain
            if idx == 61:
                name = "Circle Dependency Chain (2 Levels)"
                desc = "Circle 2 depends on Circle 1's radius; Circle 3 depends on Circle 2."
                c1 = _circle(0, 0, 1.0)
                c2 = _circle(2.0, 0, 0.5)
                c3 = _circle(-2.0, 0, 0.25)
                sm.add_object("c1", c1, {"color": "#1f77b4"})
                sm.add_object("c2", c2, {"color": "#2ca02c"})
                sm.add_object("c3", c3, {"color": "#ff7f0e"})
                sm.register_dependency(
                    "c2",
                    "c1",
                    description="Radius binds to c1.radius * 0.5; offset along x-axis",
                )
                sm.register_dependency(
                    "c3",
                    "c2",
                    description="Radius binds to c2.radius * 0.5; offset along negative x-axis",
                )
            # 62. Deep dependency chain (4 Levels)
            elif idx == 62:
                name = "Deep Circle Dependency Chain (4 Levels)"
                desc = "A 4-tier deep chain of geometric object dependencies."
                c1 = _circle(0, 0, 1.0)
                c2 = _circle(1.5, 0, 0.75)
                c3 = _circle(2.5, 0, 0.5)
                c4 = _circle(3.2, 0, 0.3)
                sm.add_object("c1", c1, {"color": "#1f77b4"})
                sm.add_object("c2", c2, {"color": "#2ca02c"})
                sm.add_object("c3", c3, {"color": "#ff7f0e"})
                sm.add_object("c4", c4, {"color": "#d62728"})
                sm.register_dependency(
                    "c2", "c1", description="Radius scales to 0.75x parent radius"
                )
                sm.register_dependency(
                    "c3", "c2", description="Radius scales to 0.67x parent radius"
                )
                sm.register_dependency(
                    "c4", "c3", description="Radius scales to 0.6x parent radius"
                )
            # 63. Branching dependency tree
            elif idx == 63:
                name = "Branching Dependency Tree"
                desc = "Branching dependency tree with one root and three dependents."
                c1 = _circle(0, 0, 1.5)
                c2 = _circle(-2.0, 2.0, 0.5)
                c3 = _circle(2.0, 2.0, 0.5)
                c4 = _circle(0, -2.0, 0.5)
                sm.add_object("root", c1, {"color": "#1f77b4", "linewidth": 3})
                sm.add_object("dep1", c2, {"color": "#2ca02c"})
                sm.add_object("dep2", c3, {"color": "#ff7f0e"})
                sm.add_object("dep3", c4, {"color": "#d62728"})
                sm.register_dependency(
                    "dep1",
                    "root",
                    description="Center anchored at root.center + (-2.0, 2.0)",
                )
                sm.register_dependency(
                    "dep2",
                    "root",
                    description="Center anchored at root.center + (2.0, 2.0)",
                )
                sm.register_dependency(
                    "dep3",
                    "root",
                    description="Center anchored at root.center + (0.0, -2.0)",
                )
            # 64. Converging dependency tree
            elif idx == 64:
                name = "Converging Dependency Tree"
                desc = "Multiple independent source shapes converging onto a single dependent composite shape."
                c1 = _circle(-2.0, 0, 1.0)
                c2 = _circle(2.0, 0, 1.0)
                c3 = _circle(0, 0, 1.5)
                sm.add_object("src1", c1, {"color": "#1f77b4"})
                sm.add_object("src2", c2, {"color": "#2ca02c"})
                sm.add_object("dependent", c3, {"color": "#ff7f0e", "linewidth": 3})
                sm.register_dependency(
                    "dependent",
                    "src1",
                    description="Center anchored midway between src1 and src2 centers",
                )
                sm.register_dependency(
                    "dependent",
                    "src2",
                    description="Center anchored midway between src1 and src2 centers",
                )
            # 65. Composite Curve dependent on sub-curves
            elif idx == 65:
                name = "Composite Curve with Dependencies"
                desc = "A composite D-shape where the straight segment depends on the circular outer boundary."
                c = create_circle_from_quarters((0, 0), 1.5)
                line_seg = _line(1, 0, 0)
                sm.add_object("boundary", c, {"color": "#1f77b4"})
                sm.add_object("divider", line_seg, {"color": "#d62728"})
                sm.register_dependency(
                    "divider",
                    "boundary",
                    description="Divider endpoints snap to boundary intersection points",
                )
            # 66. Blended Field depending on wrapped curve fields
            elif idx == 66:
                name = "Blended Field Dependency Tree"
                desc = "A blended field depending explicitly on its child curve fields."
                cf1 = CurveField(_circle(-1.0, -1.0, 1.2))
                cf2 = CurveField(_circle(1.0, 1.0, 1.2))
                blend = BlendedField([cf1, cf2], operation="min")
                sm.add_object("cf1", cf1, {"color": "#aec7e8"})
                sm.add_object("cf2", cf2, {"color": "#ffbb78"})
                sm.add_object("blend", blend, {"color": "#d62728", "linewidth": 3})
                sm.register_dependency(
                    "blend",
                    "cf1",
                    description="Evaluates min(cf1, cf2) to construct the union blended region",
                )
                sm.register_dependency(
                    "blend",
                    "cf2",
                    description="Evaluates min(cf1, cf2) to construct the union blended region",
                )
            # 67-80. Increasingly complex blended geometric fields and groups
            elif idx <= 70:
                name = f"Hierarchical Blend Scene {idx - 66}"
                desc = f"Complex blended scalar field combining multiple curve types (Idx: {idx})."
                c1 = _circle(0, 0, 1.0 + (idx - 67) * 0.2)
                c2 = _ellipse(0, 0, 2.0, 1.0 + (idx - 67) * 0.1)
                c3 = _parabola(0.2)
                sm.add_object(
                    "c1",
                    c1,
                    {"color": "#7f7f7f", "linewidth": 1.0, "linestyle": "dashed"},
                )
                sm.add_object(
                    "c2",
                    c2,
                    {"color": "#7f7f7f", "linewidth": 1.0, "linestyle": "dashed"},
                )
                sm.add_object(
                    "c3",
                    c3,
                    {"color": "#7f7f7f", "linewidth": 1.0, "linestyle": "dashed"},
                )
                cf1 = CurveField(c1)
                cf2 = CurveField(c2)
                cf3 = CurveField(c3)
                blend = BlendedField([cf1, cf2, cf3], operation="min")
                sm.add_object(
                    "blend", blend, {"color": f"hsl({(idx - 67) * 30}, 70%, 50%)"}
                )
                sm.register_dependency(
                    "blend",
                    "c1",
                    description="Evaluates hierarchical min blend wrapping child curve c1",
                )
                sm.register_dependency(
                    "blend",
                    "c2",
                    description="Evaluates hierarchical min blend wrapping child curve c2",
                )
                sm.register_dependency(
                    "blend",
                    "c3",
                    description="Evaluates hierarchical min blend wrapping child curve c3",
                )
            else:
                name = f"Complex Dependent Scene {idx - 70}"
                desc = f"Deeply nested scene combining groups, dependencies, and composites (Idx: {idx})."
                c1 = _circle(-1.5, 0, 1.0)
                c2 = _circle(1.5, 0, 1.0)
                sm.add_object("c1", c1, {"color": "#1f77b4"})
                sm.add_object("c2", c2, {"color": "#2ca02c"})
                sm.set_group("sources", ["c1", "c2"])

                # Dependents
                for k in range(idx - 70):
                    c_dep = _circle(0, (k - 2) * 0.5, 0.5)
                    sm.add_object(f"dep_{k}", c_dep, {"color": "#ff7f0e"})
                    sm.register_dependency(
                        f"dep_{k}",
                        "c1",
                        description="Coordinates propagate from c1 (source circle)",
                    )
                    sm.register_dependency(
                        f"dep_{k}",
                        "c2",
                        description="Coordinates propagate from c2 (source circle)",
                    )

        else:
            tier = 6
            tier_name = "Extreme Complexity / Stress Tests"
            # 81-90. Highly complex flowers, spirals, and composite grids
            if idx <= 85:
                name = f"Dense Flower Stress Test (Petals={idx - 75})"
                desc = (
                    f"Maximum stress test using a giant flower with {idx - 75} petals."
                )
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(idx - 75),
                    {"color": "#e377c2", "linewidth": 1.5},
                )
            elif idx <= 90:
                turns = idx - 83  # 3 to 7 turns
                name = f"Dense Spiral Stress Test (Turns={turns})"
                desc = f"Maximum stress test using a dense spiral approximation with {turns} full turns."
                sm.add_object(
                    "spiral",
                    create_spiral_approximation(turns),
                    {"color": "#bcbd22", "linewidth": 1.5},
                )
            # 91-100. Ultimate composite blended scenes and huge stress limits
            elif idx == 91:
                name = "Blended Field Stress (5 Circles)"
                desc = "Blended field combining 5 distinct overlapping circle fields with minimum union."
                fields = [
                    CurveField(_circle(np.cos(a) * 1.5, np.sin(a) * 1.5, 1.2))
                    for a in np.linspace(0, 2 * np.pi, 5, endpoint=False)
                ]
                blend = BlendedField(fields, operation="min")
                sm.add_object(
                    "blend_stress", blend, {"color": "#1f77b4", "linewidth": 2.5}
                )
            elif idx == 92:
                name = "Blended Field Stress (5 Circles Max)"
                desc = "Blended field combining 5 distinct overlapping circle fields with maximum intersection."
                fields = [
                    CurveField(_circle(np.cos(a) * 1.0, np.sin(a) * 1.0, 1.5))
                    for a in np.linspace(0, 2 * np.pi, 5, endpoint=False)
                ]
                blend = BlendedField(fields, operation="max")
                sm.add_object(
                    "blend_stress", blend, {"color": "#2ca02c", "linewidth": 2.5}
                )
            elif idx == 93:
                name = "Superellipse Mesh Grid"
                desc = "A dense grid of 6 nested superellipses with varying parameters."
                for k in range(1, 7):
                    sm.add_object(
                        f"se_{k}",
                        Superellipse(k * 0.5, k * 0.35, 1.5 + k * 0.5),
                        {"color": f"hsl({k * 40}, 65%, 55%)", "linewidth": 1.5},
                    )
            elif idx == 94:
                name = "Triple Flower Blended Pattern"
                desc = "Three multi-conic flowers overlapping in a line alignment."
                sm.add_object("f1", create_multi_conic_flower(4), {"color": "#aec7e8"})
                sm.add_object("f2", create_multi_conic_flower(5), {"color": "#ffbb78"})
                sm.add_object("f3", create_multi_conic_flower(6), {"color": "#98df8a"})
                sm.register_dependency(
                    "f2",
                    "f1",
                    description="f2.center offset dynamically from f1.center along x-axis",
                )
                sm.register_dependency(
                    "f3",
                    "f2",
                    description="f3.center offset dynamically from f2.center along x-axis",
                )
            elif idx == 95:
                name = "Concentric Heart Ripple"
                desc = "Four nested heart shapes forming a beautiful ripple pattern."
                for k in range(1, 5):
                    h = create_heart_shape()
                    sm.add_object(
                        f"heart_{k}", h, {"color": "#d62728", "linewidth": 1.2 * k}
                    )
            elif idx == 96:
                name = "Occ SDF Hybrid Stress"
                desc = "A hybrid scene blending a circular occupancy field and a rectangular signed distance field."
                c = create_circle_from_quarters((0, 0), 1.8)
                sm.add_object(
                    "circle_boundary",
                    c,
                    {"color": "#1f77b4", "linewidth": 1.5, "linestyle": "dashed"},
                )
                occ = OccupancyField(AreaRegion(c))
                r = create_square_from_edges((-1.5, -1.5), (1.5, 1.5))
                sm.add_object(
                    "rect_boundary", r, {"color": "#d62728", "linewidth": 1.5}
                )
                sdf = SignedDistanceField(AreaRegion(r))
                sm.add_object("occ", occ, {"color": "#1f77b4", "fill_alpha": 0.4})
                sm.add_object("sdf", sdf, {"color": "#d62728", "fill_alpha": 0.25})
                sm.register_dependency(
                    "sdf",
                    "occ",
                    description="SDF computes distance boundary representation from Occupancy Field occ",
                )
            elif idx == 97:
                name = "Multi-Shape Starburst Grid"
                desc = "Giant combination of circle, square, triangle, L-shape, and T-shape together."
                sm.add_object("c", _circle(0, 0, 2.5), {"color": "#1f77b4"})
                sm.add_object(
                    "s",
                    create_square_from_edges((-1.8, -1.8), (1.8, 1.8)),
                    {"color": "#ff7f0e"},
                )
                sm.add_object("t", create_triangle(), {"color": "#2ca02c"})
                sm.add_object("l", create_L_shape(), {"color": "#d62728"})
                sm.add_object("t_shape", create_T_shape(), {"color": "#9467bd"})
            elif idx == 98:
                name = "Extreme Spiral Flower Blend"
                desc = "An ultimate blend of spiral approximation paths and a central conic flower."
                sm.add_object(
                    "spiral", create_spiral_approximation(4), {"color": "#bcbd22"}
                )
                sm.add_object(
                    "flower",
                    create_multi_conic_flower(8),
                    {"color": "#e377c2", "linewidth": 2},
                )
                sm.register_dependency(
                    "flower",
                    "spiral",
                    description="flower coordinate system scales dynamically based on spiral shell radius",
                )
            elif idx == 99:
                name = "Mega Dependency Web (10 Objects)"
                desc = "A massive dependency web containing a root object and 9 interdependent dependents."
                sm.add_object(
                    "root", _circle(0, 0, 2.0), {"color": "#1f77b4", "linewidth": 3}
                )
                for k in range(1, 10):
                    c = _circle(np.cos(k) * 1.5, np.sin(k) * 1.5, 0.3)
                    sm.add_object(f"dep_{k}", c, {"color": "#2ca02c"})
                    sm.register_dependency(
                        f"dep_{k}",
                        "root",
                        description=f"dep_{k} propagates root translation",
                    )
                    if k > 1:
                        sm.register_dependency(
                            f"dep_{k}",
                            f"dep_{k - 1}",
                            description=f"dep_{k} scales radius relative to preceding node dep_{k - 1}",
                        )
            else:
                name = "The Ultimate 2Top stress Scene"
                desc = "The final ultimate stress scene combining 10 nested squares, 10 concentric circles, and 4 intersecting lines."
                # 10 squares
                for k in range(1, 11):
                    sm.add_object(
                        f"sq_{k}",
                        create_square_from_edges(
                            (-k * 0.35, -k * 0.35), (k * 0.35, k * 0.35)
                        ),
                        {"color": "#aec7e8", "linewidth": 1},
                    )
                # 10 circles
                for k in range(1, 11):
                    sm.add_object(
                        f"c_{k}",
                        _circle(0, 0, k * 0.35),
                        {"color": "#ffbb78", "linewidth": 1},
                    )
                # Lines
                sm.add_object(
                    "l1", _line(1, -1, 0), {"color": "#d62728", "linewidth": 2}
                )
                sm.add_object(
                    "l2", _line(1, 1, 0), {"color": "#2ca02c", "linewidth": 2}
                )

        # Track statistics
        curves_count = 0
        fields_count = 0

        for obj in sm.list_objects():
            o = sm.get_object(obj)
            if isinstance(o, BaseField):
                fields_count += 1
            else:
                curves_count += 1

        # Calculate dependency depth
        dep_depth = 0
        if sm._dependencies:
            # simple calculation of max path length in dependency graph
            memo = {}

            def get_depth(node):
                if node in memo:
                    return memo[node]
                children = sm._dependencies.get(node, [])
                if not children:
                    return 0
                val = 1 + max(get_depth(c) for c in children)
                memo[node] = val
                return val

            dep_depth = max(get_depth(node) for node in sm._dependencies.keys())
        # Check for resumability
        scene_file_path = SCENES_DIR / f"{scene_id}.json"
        image_file_path = IMAGES_DIR / f"{scene_id}.png"
        if (
            scene_id in existing_meta
            and scene_file_path.exists()
            and image_file_path.exists()
        ):
            print(f"[{idx}/100] Skipping '{name}' (already generated & timed)")
            metadata.append(existing_meta[scene_id])
            continue

        print(f"[{idx}/100] Rendering '{name}' (Tier {tier}: {tier_name})...")
        try:
            elapsed, scene_file, image_file = render_and_time(sm, scene_id)
            print(f"       -> Saved to {image_file} in {elapsed:.1f}ms")

            # Read back the saved scene JSON to embed in metadata (CORS bypass for local files)
            scene_data = {}
            try:
                with open(SCENES_DIR / f"{scene_id}.json", "r") as sf:
                    scene_data = json.load(sf)
            except Exception as jse:
                print(f"       [Warning] Could not read scene JSON to embed: {jse}")

            metadata.append(
                {
                    "id": scene_id,
                    "name": name,
                    "description": desc,
                    "complexity_tier": tier,
                    "tier_name": tier_name,
                    "curves_count": curves_count,
                    "fields_count": fields_count,
                    "dependency_depth": dep_depth,
                    "total_time_ms": round(elapsed, 2),
                    "scene_file": scene_file,
                    "image_file": image_file,
                    "scene_data": scene_data,
                }
            )
        except Exception as e:
            print(f"[Error] Failed to render '{name}': {e}")
            import traceback

            traceback.print_exc()

    # Save metadata.json and metadata.js (CORS bypass for local files)
    metadata_path = GALLERY_DIR / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    metadata_js_path = GALLERY_DIR / "metadata.js"
    with open(metadata_js_path, "w") as f:
        f.write("window.SCENE_METADATA = " + json.dumps(metadata, indent=2) + ";\n")

    print(
        f"[Success] Successfully generated 100 test cases and saved metadata.json to {metadata_path}!"
    )


if __name__ == "__main__":
    main()
