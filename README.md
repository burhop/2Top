# 2Top 0.30.0 · Tidal Atlas

A canvas-first kinetic-art studio backed by a reusable Python implicit-geometry engine. Shape living topographic islands by hand or through real MCP and browser WebMCP tools. Every edit uses the same validated, revision-checked scene service.

## Development status

Version **0.30.0** adds [native affine half-plane trims](docs/native_half_plane_trims.md). Public immutable `HalfPlaneMask(a,b,c,closed=True)` declares exact `a*x+b*y+c>=0`, or `>0` with an open boundary. The polynomial/line solver now proves the positive irrational contact inside `x+y>=0` on `y=x`; the equivalent opaque callback remains unresolved. Constant/degenerate predicates, negative scaling and boundary tangencies have explicit semantics. Outward float intervals plus exact rational fallback preserve predicate signs, and native serialization retains raw stored coefficients and boundary mode. Existing rectangle proofs and independent representative gates remain. Development targets **dev**.

See the [milestone roadmap](docs/ROADMAP.md), [CHANGELOG.md](CHANGELOG.md) for version history and [verification details](docs/studio_verification.md) for tested behavior and remaining browser-host limits.

The [performance and supported-complexity guide](docs/studio_performance.md)
retains the measured 0.7.2 baseline and a reproducible current-browser benchmark.

## Start the new studio

Use Python 3.11 or later in a checkout of the **dev** branch. The studio does not
require Node, Qt, development tools, an AI account or an API key.

Windows PowerShell (no activation or execution-policy change needed):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[studio]"
.\.venv\Scripts\python.exe -m studio.app
```

macOS/Linux:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[studio]"
.venv/bin/python -m studio.app
```

For the existing Work17 checkout, see [current-dev startup and demo steps](docs/work17_quickstart.md).

Open **http://127.0.0.1:8000**. No AI account or API key is needed to draw, animate, undo, or export. The app stays on loopback. Local artwork is saved to `.studio/scene.json`; use `--ephemeral` for a disposable session.

If another studio is already using port 8000, leave its session intact and start
with `--ephemeral --port 8768`, then open **http://127.0.0.1:8768/**. Read the
terminal error if startup fails; first startup can take several seconds.

- Shift/Ctrl/⌘-click layers or use **Select multiple** on touch; nudge, scale, rotate or drag the selection while preserving its complete motion paths
- Preview center alignment with two selected islands, or equal center spacing with three or more; Apply commits one reversible layout and Cancel keeps the original
- Choose **Try confluence** to merge two static islands; edit either source, switch union/smooth union, adjust amount, undo or remove the composition while retaining sources
- Show a selected island’s labeled motion path, drag individual positional keys and retime them across neighbors; occupied times are rejected atomically
- Capture up to 24 complete poses per island, choose linear/smooth interpolation, jump between keys, and undo/redo choreography edits
- Directly drag islands and adjust their scale, stretch, curl, palette and contour density; animated edits create/update a pose at the paused playhead
- Play, pause and scrub a smooth 12-second tide; save JSON recipes, SVG artwork or PNG images
- Select, duplicate, hide, delete, undo and redo complete operations
- Connect an MCP client to **http://127.0.0.1:8000/mcp/** or launch the stdio proxy with `python -m studio.mcp_server`
- In a supported top-level browser, `document.modelContext` registers the same 23 tools, including center layout, whole-path arrangement, choreography and static blend creation/update/removal. Unsupported browsers retain the complete manual app

Recipes export schema 4 with complete back-to-front `layer_order` and bounded static blends. Schema-1/2/3 recipes reopen in their original islands-then-blends order, preserving styles, fields, tracks and dependencies. The next save uses schema 4, which older studios cannot read; keep original recipes for exchange. See [composition layers](docs/composition_layers.md) and [static blending](docs/static_blending.md) for limits.

See [the studio guide](docs/tidal_atlas.md), [agent connection details and compatibility](docs/agent_protocols.md), and the app's self-contained `/api/docs` reference. The studio does not include an embedded language model or pretend that local presets are AI output.

## Studio checks

```bash
python -m pip install -e ".[studio,dev]"
python -m pytest tests/studio
python -m pytest tests/test_backend_numerics.py tests/test_procedural_derivatives.py
python -m pytest tests/test_sublevel_bounds.py
python -m pytest tests/test_native_half_plane_trims.py tests/test_native_rectangle_trims.py tests/test_polynomial_line_intersections.py tests/test_intersection_diagnostics.py tests/test_coordinate_broadcast.py tests/test_tangent_intersections.py tests/test_trimmed_intersections.py tests/test_field_gradient_diagnostics.py tests/test_distance_gradient_diagnostics.py tests/test_distance_gradient.py tests/test_distance_sign.py tests/test_distance_numerics.py
python benchmarks/distance_numerics.py --output distance-numerics.json
python -m pytest tests/test_distance_cache.py
python benchmarks/distance_cache.py --output distance.json
python -m pytest tests/test_occupancy_validity.py
python benchmarks/occupancy_validity.py --output occupancy.json
python -m pytest tests/test_field_algebra.py
python benchmarks/field_algebra.py --output algebra.json
python -m pytest tests/test_automatic_derivatives.py
python benchmarks/automatic_derivatives.py --output automatic.json
python benchmarks/sublevel_bounds.py --output bounds.json
python benchmarks/procedural_accuracy.py --output accuracy.json
python benchmarks/implicit_backend.py --output backend-timing.json
node tests/studio/webmcp_contract.mjs
# Optional DOM/canvas behavioral checks (Node 24.15+):
npm ci
npm run test:ui
# Actual Chromium acceptance (also configured in GitHub Actions):
npx --no-install playwright install chromium
npm run test:browser
python -m ruff check studio geometry/kinetic*.py geometry/choreography.py geometry/static_blend.py geometry/__init__.py geometry/base_field.py geometry/implicit_curve.py scene_management/scene_manager.py tests/studio
python -m ruff format --check studio geometry/kinetic*.py geometry/choreography.py geometry/static_blend.py geometry/__init__.py geometry/base_field.py geometry/implicit_curve.py scene_management/scene_manager.py tests/studio
```

The legacy geometry engine and diagnostic UI remain available below. The historical `MCPCommandHandler` is a legacy command dispatcher, not a standard MCP transport; the new standard server is `studio/mcp_server.py`.

---

## Reusable implicit geometry library

A complete, tested framework for planar implicit geometry: define curves by f(x, y) = 0, compose them via constructive operations, build piecewise boundaries and filled regions, and generate scalar fields (signed distance, occupancy).

Robust handling of vectorization, masks, NaN/∞, serialization, and headless plotting.

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `sympy`, `numpy`, `matplotlib`, `PySide6`, `ruff`, `black`.

## Development Tooling

Code style is enforced with [ruff](https://docs.astral.sh/ruff/) and [black](https://black.readthedocs.io/). Configuration lives in `pyproject.toml` (line length 88, Python 3.11 target).

```bash
ruff check .
black .
```

## Running Tests

```bash
pytest
```

Run only the fast geometry suite:

```bash
python tests/fast_geo_runner.py
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

## Interactive Web UI & Visualizer Studio

The library includes a complete, real-time Web UI visualizer studio on top of the geometry engine for interactive coordinate plotting, database inspections, and comparative math verifications.

### Running the Web UI Studio

Start the Flask-based web application:

```bash
python -m ui.app
```

Then visit **`http://localhost:5000`** in your browser.

**Key UI Features:**
- **Dynamic 2D Canvas**: Rich 2D graphics canvas with smooth drag panning, mouse-wheel cursor-centered zooming, coordinate axes ticks, grid snapping, and adaptive LOD.
- **Neon Dark-Mode Design**: Harmonious modern dark design with high-contrast neon accents, floating control panels, and custom-styled scrolling widgets.
- **Database Loader Controls**:
  - Enter a **Curve ID** to load and reconstruct any implicit or trimmed curve from `curves.db` directly onto the viewport.
  - Enter a **Group ID** to reconstruct entire spatial sets of overlapping equations, rendered with alternating high-contrast color palettes to clearly distinguish boundaries.
- **Mathematical Verification Panel**:
  - The **Verify Scene** button queries the backend to calculate numerical/analytical endpoints and intersection coordinates for all loaded database curves.
  - Compares active calculations against database ground-truth records using strict, adaptive scale-factored tolerances.
  - Opens a floating detailed report card tracking exact match/mismatch statuses, error diff logs, and intersection relations.
- **Visual Test Runner HUD**: Steps, plays, and auto-navigates predefined geometry test cases in sequence using dedicated transport playback controls.

### Continuous Test Runner

To watch python source file modifications and automatically stream test suite executions visually to the active Web UI canvas:

```bash
python tools/continuous_runner.py
```

### Advanced Mathematical Testing

We have expanded the precision test suite to verify complex algebraic edge cases and metamorphic properties:
- **Metamorphic Invariant Testing** (`tests/property/test_metamorphic_invariants.py`): Validates consistency of R-functions and conic intersections under rigid coordinate translations, rotations, and scaling.
- **Singularity Verification** (`tests/unit/test_singularities.py`): Asserts exact evaluations and robust domain clipping around cusps, self-intersections, and isolated singular coordinates.
- **Ground Truth Comparison** (`tests/unit/test_verify_geometry_against_dataset.py`): Programmatically reconstructs thousands of database records to verify intersection locations under strict tolerance boundaries.

For a deep-dive on the internal architectures of these visual and mathematical testing systems, see the **[Visualizer Studio Developer Guide](file:///d:/repos/2Top/docs/VISUALIZER_STUDIO.md)**.

## API Tips

- __Numerical stability__: `ImplicitCurve.evaluate()` preserves mathematically correct NaN/∞ when inputs are NaN/∞, and guards against numerical overflow.
- __Vectorization__: All evaluate/gradient methods accept scalars or numpy arrays; internal implementations use `ravel()`-based views where needed.
- __Bounding boxes__: Use `ConicSection.bounding_box()` for precise bounds; other types may provide conservative boxes.

## Test Infrastructure

The `tests/` package is organized into focused sub-packages:

| Package | Purpose |
|---|---|
| `tests/models/` | Data models: `TestCase`, `TestResult`, `ErrorMessage`, `Module` |
| `tests/utils/` | Utilities: `TestCaseManager`, `TestCaseExecutor`, `TestResultAnalyzer`, `ErrorMessageGenerator`, `ResultStorageManager`, `TestCaseFailureDetector`, `ModuleIdentifier` |
| `tests/unit/` | Unit tests for geometry modules and test-system utilities |
| `tests/factories/` | Reusable curve scenario factories (`curve_scenarios.py`) |
| `tests/helpers/` | Geometry fixture builders (`builders.py`) and precision helpers (`precision.py`) |
| `tests/golden/` | Golden digest files (`digests/`) and loader; regenerate via `python -m tests.utils.golden_cli <name> --write` |
| `tests/integration/` | Integration-level test stubs |
| `tests/property/` | Property-based / fuzz tests (`test_geometry_fuzz.py`) |
| `tests/contract/` | Contract test stubs |

Test results are persisted to `./test_results/` as JSON by `ResultStorageManager`.

## Roadmap Alignment

This repository implements Part I (Foundational Sprints) of the agile blueprint in `design_docs/agile_development_blueprint.md`, including Sprint 4 (R-functions), Sprint 5 (Trimmed/Composite), and Sprint 6 (AreaRegion). Wrapper functions (`union`, `intersect`, `difference`, `blend`) and utilities (`create_square_from_edges`, `create_circle_from_quarters`) are provided via `geometry/__init__.py`.

## License

See repository for licensing details.

### Composition layers (0.6.0)

Use **Try layered study** for Glasswater. Composition rows show front-to-back
order, visibility and source dependencies; arrow buttons reorder artwork, and
Layer appearance controls palette and group opacity. Sources remain editable
through their selected center handles even when hidden or consumed by a blend.
UI, MCP and WebMCP use the same reversible layer commands. See
[composition layers](docs/composition_layers.md) for schema-4 migration, source
semantics and compositing limits. Native WebMCP host execution is still unverified.

### Coauthor workflow (0.7.0)

Open **Client setup**, connect an already configured local client, discover the
23 tools and read `get_scene` before making an edit. Coauthor activity shows
committed routes and differences; refine a layer by hand and share Undo/Redo.
The shipped protocol helper and acceptance scripts do not establish live model
inference. [Coauthor guide](docs/coauthoring.md) explains setup, revision-safe
calls, provenance and the remaining native/model-host verification gap.
