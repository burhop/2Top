# 2Top: 2D Implicit Geometry Library

A complete, tested framework for planar implicit geometry: define curves by f(x, y) = 0, compose them via constructive operations, build piecewise boundaries and filled regions, and generate scalar fields (signed distance, occupancy).

All tests pass: 449/449. Robust handling of vectorization, masks, NaN/∞, serialization, and headless plotting.

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

## Quickstart

```python
import sympy as sp
from geometry import (
    ConicSection, PolynomialCurve, Superellipse, ProceduralCurve,
    TrimmedImplicitCurve, CompositeCurve, AreaRegion,
    union, intersect, difference, blend,
    create_circle_from_quarters, create_square_from_edges,
    SignedDistanceStrategy, OccupancyFillStrategy,
)

x, y = sp.symbols('x y')

# 1) Core curves
circle = ConicSection(x**2 + y**2 - 1, (x, y))
line = PolynomialCurve(2*x + 3*y - 1, (x, y))
superellipse = Superellipse(a=1.2, b=0.8, n=3.5, variables=(x, y))
proc = ProceduralCurve(lambda X, Y: (X-0.5)**2 + (Y+0.25)**2 - 0.6, variables=(x, y))

val = circle.evaluate(0.5, 0.5)   # < 0 inside
gx, gy = circle.gradient(1.0, 0.0)

# 2) Constructive geometry (R-functions)
u = union(circle, proc)                 # sharp union: min(f1, f2)
i = intersect(circle, line)             # sharp intersection: max(f1, f2)
d = difference(circle, line)            # A \ B: max(fA, -fB)
b = blend(circle, proc, alpha=0.3)      # smooth blend

# 3) Piecewise curves and regions
square = create_square_from_edges((-1, -1), (1, 1))
assert square.is_closed()
region = AreaRegion(square)             # filled area

# 4) Fields
sdf = SignedDistanceStrategy(resolution=0.05).generate_field(region)
occ = OccupancyFillStrategy(1.0, 0.0).generate_field(region)

## Curve Catalog

- __ConicSection__: circles/ellipses/hyperbolas/parabolas. Accurate `bounding_box()` for bounded cases; ∞ for unbounded.
- __PolynomialCurve__: arbitrary polynomial degree with `degree()`.
- __Superellipse__: |x/a|^n + |y/b|^n - 1 = 0 with vectorized gradient.
- __ProceduralCurve__: user function for f(x, y). Numerical gradient fallback. Serialization stores a "custom" placeholder.
- __TrimmedImplicitCurve__: segment of a base curve under a boolean `mask(x, y)`.
- __CompositeCurve__: ordered `TrimmedImplicitCurve` segments. `is_closed()`, `contains()` (boundary/region modes), specialized square evaluation.
- __RFunctionCurve__: constructive ops: `union`, `intersect`, `difference`, `blend(alpha)`.

## Containment Semantics

- __Boundary checks__: use `on_curve(x, y, tol)` on curve types. For regions, use `region.outer_boundary.on_curve(...)` or a hole boundary’s `on_curve(...)`.
- __Region checks__: `AreaRegion.contains(x, y)` tests inside/outside (holes subtracted). For composite closed curves, use `CompositeCurve.contains(x, y, region_containment=True)`.
- __Sign convention__: f(x, y) < 0 inside, > 0 outside for closed curves.

## Constructive Geometry (Sprint 4)

```python
from geometry import ConicSection, union, intersect, blend

x, y = sp.symbols('x y')
c1 = ConicSection((x-0.5)**2 + y**2 - 0.7**2, (x, y))
c2 = ConicSection((x+0.2)**2 + (y-0.1)**2 - 0.6**2, (x, y))

u = union(c1, c2)             # inside if in either
it = intersect(c1, c2)        # inside only in overlap
bl = blend(c1, c2, 0.2)       # smooth transition across seam
```

## Piecewise Curves and Regions (Sprint 5–6)

```python
from geometry import create_circle_from_quarters, create_square_from_edges, AreaRegion

circle = create_circle_from_quarters(center=(0, 0), radius=2.0)
square = create_square_from_edges((-1, -1), (1, 1))

assert circle.is_closed() and square.is_closed()
region = AreaRegion(square)
inside = region.contains(0.25, 0.25)  # True
on_bdry = region.contains_boundary(1.0, 0.0)
```

Notes:
- `CompositeCurve.evaluate()` uses a pseudo-distance metric. Squares created by `create_square_from_edges` use a special max-distance evaluation to ensure correct edge values.
- For robust region containment, `AreaRegion` converts boundaries to polygons and uses ray casting, with fixes for tolerances and ordering.
- Metadata optimizations:
  - Squares are tagged with `_is_square` and store `_square_bounds` for fast and accurate area.
  - Polygons created via `create_polygon_from_edges` store `_polygon_vertices` to avoid sampling and ensure exact area.
  - Trimmed line segments may expose `get_endpoints()` for better polygonal sampling.

See `examples/area_region_quickstart.py` for a runnable demonstration of region vs boundary containment and area calculation.

## Fields and Strategies

```python
from geometry import SignedDistanceStrategy, OccupancyFillStrategy

sdf = SignedDistanceStrategy(resolution=0.05).generate_field(region)
occ = OccupancyFillStrategy(inside_value=1.0, outside_value=0.0).generate_field(region)
```

## Serialization

- All curve/region classes implement `to_dict()`/`from_dict()`.
- `ProceduralCurve` and some masks are non-serializable by nature; stored as descriptive placeholders (e.g., `"function": "custom"`).
- Backward compatibility for older trimmed masks is handled via placeholder masks.

## Plotting (Headless)

- Matplotlib is configured for non-interactive environments. Use `curve.plot(...)` or custom visual tests.
- Backend: `'Agg'` to avoid tkinter/Tcl issues.

## API Tips

- __Numerical stability__: `ImplicitCurve.evaluate()` preserves mathematically correct NaN/∞ when inputs are NaN/∞, and guards against numerical overflow.
- __Vectorization__: All evaluate/gradient methods accept scalars or numpy arrays; internal implementations use `ravel()`-based views where needed.
- __Bounding boxes__: Use `ConicSection.bounding_box()` for precise bounds; other types may provide conservative boxes.

## Roadmap Alignment

This repository implements Part I (Foundational Sprints) of the agile blueprint in `design_docs/agile_development_blueprint.md`, including Sprint 4 (R-functions), Sprint 5 (Trimmed/Composite), and Sprint 6 (AreaRegion). Wrapper functions (`union`, `intersect`, `difference`, `blend`) and utilities (`create_square_from_edges`, `create_circle_from_quarters`) are provided via `geometry/__init__.py`.

## License

See repository for licensing details.
