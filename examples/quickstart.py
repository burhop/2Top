import sympy as sp
import numpy as np

from geometry import (
    ConicSection, PolynomialCurve, Superellipse, ProceduralCurve,
    TrimmedImplicitCurve, CompositeCurve, AreaRegion,
    union, intersect, difference, blend,
    create_circle_from_quarters, create_square_from_edges,
    SignedDistanceStrategy, OccupancyFillStrategy,
)
from geometry.composite_curve import create_polygon_from_edges


def main():
    x, y = sp.symbols('x y')

    # Core curves
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    line = PolynomialCurve(2*x + 3*y - 1, (x, y))
    sup = Superellipse(a=1.2, b=0.8, n=3.5, variables=(x, y))
    proc = ProceduralCurve(lambda X, Y: (X-0.5)**2 + (Y+0.25)**2 - 0.6, variables=(x, y))

    # Evaluate & gradient
    p = (0.5, 0.5)
    print("circle f(0.5,0.5)=", circle.evaluate(*p))
    print("circle grad(1,0)=", circle.gradient(1.0, 0.0))

    # R-functions
    u = union(circle, proc)
    it = intersect(circle, line)
    df = difference(circle, line)
    bl = blend(circle, proc, alpha=0.3)

    print("union at p:", u.evaluate(*p))
    print("intersect at p:", it.evaluate(*p))
    print("difference at p:", df.evaluate(*p))
    print("blend at p:", bl.evaluate(*p))

    # Piecewise curves and regions
    square = create_square_from_edges((-1, -1), (1, 1), (x, y))
    assert square.is_closed()
    region = AreaRegion(square)

    print("region.contains(0.25,0.25)=", region.contains(0.25, 0.25))
    print("region.contains_boundary(1.0,0.0)=", region.contains_boundary(1.0, 0.0))

    # Convex polygon (triangle) example
    pts = [(0.0, 0.0), (2.0, 0.0), (1.0, 1.0)]
    poly = create_polygon_from_edges(pts)
    print("poly.is_convex_polygon()=", poly.is_convex_polygon() if hasattr(poly, 'is_convex_polygon') else getattr(poly, '_is_convex_polygon', False))
    print("poly.contains(1.0,0.3, region)=", poly.contains(1.0, 0.3, region_containment=True))
    print("poly.contains(1.0,0.0, region)=", poly.contains(1.0, 0.0, region_containment=True))
    print("poly.contains(3.0,3.0, region)=", poly.contains(3.0, 3.0, region_containment=True))

    # Fields
    sdf = SignedDistanceStrategy(resolution=0.1).generate_field(region)
    occ = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0).generate_field(region)

    # Sample a small grid
    xs = np.linspace(-1.5, 1.5, 5)
    ys = np.linspace(-1.5, 1.5, 5)
    grid = np.array([[sdf.evaluate(xv, yv) for xv in xs] for yv in ys])
    print("Signed distance 5x5 sample:\n", grid)

    occ_grid = np.array([[occ.evaluate(xv, yv) for xv in xs] for yv in ys])
    print("Occupancy 5x5 sample:\n", occ_grid)


if __name__ == "__main__":
    main()
