from __future__ import annotations

from typing import List, Tuple, Optional


class CompositePolygonMixin:
    """
    Mixin providing polygon-related helpers and metadata accessors for Composite-like curves.

    Assumes the host class may have the following optional attributes set when representing
    a convex polygon created by a factory (e.g., create_polygon_from_edges):
      - _is_convex_polygon: bool
      - _convex_edges_abc: Optional[List[Tuple[float, float, float]]]  # (a,b,c) per edge where a*x+b*y+c <= 0 is inside
      - _polygon_vertices: Optional[List[Tuple[float, float]]]
    """

    # Accessors --------------------------------------------------------------
    def is_convex_polygon(self) -> bool:
        return bool(getattr(self, "_is_convex_polygon", False))

    def halfspace_edges(self) -> Optional[List[Tuple[float, float, float]]]:
        return getattr(self, "_convex_edges_abc", None)

    def polygon_vertices(self) -> Optional[List[Tuple[float, float]]]:
        return getattr(self, "_polygon_vertices", None)

    def polygon_normals(self) -> Optional[List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
        """
        Returns a list of ((mx, my), (nx, ny)) where (mx, my) is the midpoint of an edge
        and (nx, ny) is an outward unit normal of that edge. Returns None if metadata is missing.
        """
        verts = getattr(self, "_polygon_vertices", None)
        edges = getattr(self, "_convex_edges_abc", None)
        if verts is None or edges is None or len(verts) < 2:
            return None
        n = len(verts)
        out = []
        for i in range(n):
            x0, y0 = verts[i]
            x1, y1 = verts[(i + 1) % n]
            mx, my = (0.5 * (x0 + x1), 0.5 * (y0 + y1))
            a, b, _c = edges[i]
            norm = (a * a + b * b) ** 0.5
            if norm == 0:
                nx, ny = 0.0, 0.0
            else:
                nx, ny = a / norm, b / norm
            out.append(((mx, my), (nx, ny)))
        return out
