# 2Top API Reference

A concise reference to the core classes, functions, and semantics. See `README.md` for a narrative quickstart and examples.

## Modules
- `geometry/` package exposes all primary classes and helpers via `from geometry import *`.

## Core Concepts
- Implicit curve: f(x, y) = 0 defines the boundary. Sign convention: f < 0 inside, f > 0 outside (for closed curves).
- Region: A filled area bounded by a closed curve with optional holes.
- Field strategies: Convert regions to scalar fields (e.g., signed distance, occupancy).

## Curves

### ImplicitCurve
- Base class storing `expression: sympy.Expr` and `variables: (x, y)`.
- Methods:
  - `evaluate(x, y) -> float|ndarray`: vectorized. Preserves NaN/∞ when mathematically appropriate.
  - `gradient(x, y) -> (gx, gy)`: vectorized.
  - `normal(x, y) -> (nx, ny)`: unit outward normal; raises for zero gradient.
  - `on_curve(x, y, tolerance=1e-3) -> bool|ndarray`: subclasses override to check |f| <= tol.
  - `bounding_box() -> (xmin, xmax, ymin, ymax)`: generic placeholder; see subclasses.
  - `to_dict()/from_dict()`.

### ConicSection
- Second-degree polynomials (circles, ellipses, parabolas, hyperbolas).
- Highlights: precise `bounding_box()` for bounded conics; ∞ for unbounded types.

### PolynomialCurve
- Arbitrary-degree polynomial; `degree()` reports total degree.

### Superellipse
- |x/a|^n + |y/b|^n - 1 = 0. Vectorized gradient; careful handling near axes.

### ProceduralCurve
- Wraps a Python callable f(X, Y). Vectorized evaluate; finite-difference gradient.
- Serialization uses placeholders (e.g., `"function": "custom"`).

### TrimmedImplicitCurve
- A segment of a base curve gated by `mask(x, y) -> bool`.
- `contains(x, y, tolerance)` checks membership on base curve AND mask.
- `on_curve(...)` delegates to `contains(...)` for boundary testing.

### CompositeCurve
- Ordered list of `TrimmedImplicitCurve` segments.
- `is_closed(tol)`; `on_curve(...)` over segments.
- `contains(x, y, tolerance=1e-3, region_containment=False)`:
  - When closed and `region_containment=True`, tests inside region.
  - Convex polygons created by `create_polygon_from_edges()` use a fast, vectorized half-space intersection (O(m) in number of edges) and treat boundary as inside.
  - When `region_containment=False`, tests boundary membership.
- Evaluation uses a pseudo-distance metric; special square and convex polygon paths use max-of-half-spaces for robustness and performance.
 - Convenience:
   - `is_convex_polygon() -> bool`
   - `halfspace_edges() -> List[(a,b,c)] | None` coefficients for convex polygons

### RFunctionCurve (Constructive Geometry)
- Combines two curves: `union` (min), `intersect` (max), `difference` (max(f1, -f2)), `blend(alpha)` (smooth min approximation).
- Vectorized evaluate and gradient.
- `to_dict()/from_dict()` persist operation, alpha, and children.
- Helpers: `union(c1, c2)`, `intersect(c1, c2)`, `difference(c1, c2)`, `blend(c1, c2, alpha)`.

## Regions

### AreaRegion
- Defines a filled area with `outer_boundary: CompositeCurve` and optional `holes: List[CompositeCurve]`.
- Requires closed boundaries. Provides:
  - `contains(x, y, tolerance=1e-3) -> bool`: inside/outside (holes subtracted).
  - `contains_boundary(x, y, tolerance=1e-3) -> bool`: boundary membership.
  - `area() -> float`: polygonal approximation (Shoelace), hole subtraction.
  - `to_dict()/from_dict()`.

## Field Strategies

- `SignedDistanceStrategy(resolution)`: returns `SignedDistanceField` over an `AreaRegion`.
- `OccupancyFillStrategy(inside_value, outside_value)`: returns `OccupancyField`.
- Usage:
```python
sdf = SignedDistanceStrategy(resolution=0.05).generate_field(region)
occ = OccupancyFillStrategy(1.0, 0.0).generate_field(region)
```

## Utilities
- `create_circle_from_quarters(center, radius)` -> `CompositeCurve`.
- `create_square_from_edges(corner1, corner2)` -> `CompositeCurve` with special evaluation and square metadata.
- `create_polygon_from_edges(points)` -> `CompositeCurve` polygon; stores polygon vertices and convex metadata for half-space containment/evaluation when appropriate.

Validation rules for `create_polygon_from_edges(...)`:
- Requires at least 3 unique, finite vertices; ignores a closing duplicate if present `(points[0] == points[-1])`.
- Rejects consecutive duplicate vertices (zero-length edges).
- Rejects degenerate polygons with zero area (collinear vertices).

## Containment & Boundary Testing
- Boundary: `curve.on_curve(x, y, tol)`.
- Region interior: `AreaRegion.contains(x, y)`; for closed composite curves: `CompositeCurve.contains(x, y, region_containment=True)`.

### Metadata & Fast-Paths
- Squares are tagged with `_is_square` and store `_square_bounds` enabling accurate and fast area calculation and robust edge evaluation.
- Polygons created by `create_polygon_from_edges` store `_polygon_vertices` to avoid sampling for area and to preserve vertex order.
- `TrimmedImplicitCurve.contains()` uses a vectorized rectangular-bounds fast-path when `_xmin/_xmax/_ymin/_ymax` are provided; falls back to per-point mask otherwise.

## Serialization Notes
- All types implement `to_dict()/from_dict()`; some masks and procedural functions serialize as placeholders.
- Backward compatibility for trimmed masks uses safe defaults.

## Plotting (Headless)
- Contour-based plotting uses the `'Agg'` backend; safe in non-GUI environments.

## Error Handling & Numerics
- Evaluate preserves NaN/∞ when inputs are NaN/∞; guards numerical overflow.
- Vectorized paths rely on `ravel()`-based views for correctness and performance.
