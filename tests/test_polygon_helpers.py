import math
import sympy as sp

from geometry.composite_curve import create_polygon_from_edges, create_square_from_edges, CompositeCurve


def test_polygon_vertices_preserved_and_serialized():
    pts = [(0.0, 0.0), (2.0, 0.0), (1.0, 1.5)]
    poly = create_polygon_from_edges(pts)

    verts = poly.polygon_vertices() if hasattr(poly, "polygon_vertices") else None
    assert verts is not None
    assert len(verts) == len(pts)
    for (vx, vy), (px, py) in zip(verts, pts):
        assert abs(vx - px) < 1e-12
        assert abs(vy - py) < 1e-12

    data = poly.to_dict()
    poly2 = CompositeCurve.from_dict(data)
    verts2 = poly2.polygon_vertices() if hasattr(poly2, "polygon_vertices") else None
    assert verts2 is not None
    assert len(verts2) == len(pts)
    for (vx, vy), (px, py) in zip(verts2, pts):
        assert abs(vx - px) < 1e-12
        assert abs(vy - py) < 1e-12


def test_polygon_normals_square_unit_length_and_count():
    x, y = sp.symbols("x y")
    sq = create_square_from_edges((-1.0, -1.0), (1.0, 1.0), (x, y))

    normals = sq.polygon_normals() if hasattr(sq, "polygon_normals") else None
    # For the rectangle utility, vertices metadata may not be set; normals require that
    # So also create via polygon factory to ensure vertices are present
    if normals is None:
        pts = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
        sq = create_polygon_from_edges(pts)
        normals = sq.polygon_normals()

    assert normals is not None
    assert len(normals) == 4

    for (mx, my), (nx, ny) in normals:
        # Unit length
        l = math.hypot(nx, ny)
        assert abs(l - 1.0) < 1e-12
        # Midpoints should lie exactly on square edges (either x=+-1 with y in [-1,1] or y=+-1)
        on_vertical = (abs(mx - 1.0) < 1e-9 or abs(mx + 1.0) < 1e-9) and (-1.0 - 1e-9 <= my <= 1.0 + 1e-9)
        on_horizontal = (abs(my - 1.0) < 1e-9 or abs(my + 1.0) < 1e-9) and (-1.0 - 1e-9 <= mx <= 1.0 + 1e-9)
        assert on_vertical or on_horizontal
