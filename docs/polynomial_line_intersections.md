# Reliable native polynomial/line intersections

Version 0.28.0 provides an explicit, useful correctness subset of the general
intersection problem. It does not change the legacy numerical finder.

On Work17 the native x**8 case takes a median **2.68 ms** over five warm calls;
the seven recorded workloads range from about **2.24 to 9.27 ms**. These are
local measurements, not latency guarantees. [Raw reports and timings](polynomial_line_work17.json)
include the current four-candidate legacy reproduction and exact binary-float
distances to its analytic root. **89 new regression cases** cover analytic and
high-precision oracles; independent review additionally checked mixed degree-eight
multiplicities and oblique irrational-root enclosures.

```python
import sympy as sp
from geometry import ImplicitCurve, find_polynomial_line_intersections

x, y = sp.symbols("x y")
report = find_polynomial_line_intersections(
    ImplicitCurve(y - x**8, (x, y)), ImplicitCurve(y, (x, y))
)
assert report["points"] == [(0.0, 0.0)]
assert report["roots"][0]["multiplicity"] == 8
assert report["roots"][0]["position_bound_exact"] == "0"
```

Analytically, y=0 implies x**8=0: only the origin, with multiplicity eight.
The old finder at search_range=2, grid_resolution=50, tolerance=1e-8 returns
four candidates, three about 0.04 from the root despite residuals around 1e-12.
The new API returns the one exact origin. Setting x**8+delta=0 with positive
delta gives no real roots; x**8-delta=0 gives two. Independent analytic and
160-digit Decimal tests check these outcomes without deriving the oracle from
the implementation's root isolation. Run `python examples/polynomial_line_demo.py`
for a JSON report or `python benchmarks/polynomial_line_intersections.py --output
report.json` for the current legacy comparison and five warm isolation calls.

## Supported coefficient model

Both fields must use the unchanged native ImplicitCurve evaluator and native
expression/variables properties, optionally under default TrimmedImplicitCurve
evaluation wrappers. Either input must be a nonzero affine line. The other is
a polynomial of total degree at most eight with rational or stored binary Float
coefficients. Each object's variable order denotes its x/y input order; variable
names do not have to match. Native compiled kernels are checked against their
stored expression/variables snapshot. Replacement evaluators, procedural fields,
transcendentals, unknown symbols and unsupported structure return `unsupported`.
There is no numerical fallback or residual-based root existence test.

The larger line coefficient is eliminated, so the dependent-coordinate slope
has magnitude at most one. Exact rational substitution yields a univariate
polynomial, normalized for coefficient content. SymPy real-root intervals give
disjoint rational enclosures and each root's multiplicity. Their affine images
enclose x and y. All real roots are considered globally; there is no search box,
sampling grid or maximum point count. An identically zero restriction reports
`non_isolated_model`, since the whole line is a component; trims may select a
different set that this API does not enumerate. A nonzero constant has zero roots.

Input traversal is capped at 512 nodes, degree eight and 4,096-bit coefficient
numerators/denominators. Float precision and binary exponent sizes are checked
before rational conversion; elimination and integer normalization are checked
again. Parameter and mapped coordinate interval endpoints have the same bit cap.
Touching parameter intervals get at most 64 refinement passes with 16 steps per
interval/pass; an unresolved separation is explicitly unsupported. These are
resource guards, not a hard wall-clock limit on SymPy root isolation.

## Model position, float checks and acceptance

`model_scope="exact_stored_coefficients_untrimmed"` applies to every enclosure.
It describes the exact zero set of the captured coefficients, including exact
binary values of Float atoms, rather than all rounding behavior of the native
floating evaluator. `model_root_completeness=True` means all distinct real roots
of that isolated untrimmed model have records. It does not mean all records have
accepted float representatives or that the trimmed set is complete.

Each root has rational-string `coordinate_intervals`, multiplicity and a float
`point` when representable. `position_bound_exact` is the maximum exact distance
from that binary float point to every coordinate interval endpoint: an L-infinity
bound to its model root. The numeric `position_bound` rounds outward (or is None
on overflow). Acceptance compares exact rational values with the exact binary
value of `position_tolerance`, default 1e-8; a small field residual never supplies
this bound. Isolation uses one sixteenth of that tolerance for its parameter
interval width; unusually tight requests may still fail after float rounding.

Accepted representatives also require both actual public scalar evaluations to
be finite and within `residual_tolerance`, default 1e-8. Field scaling does not
alter model roots, but extreme scaling/cancellation can fail this separate float
gate. Every failure retains its model record and an explicit reason. Distinct
model roots that round to the same float pair all remain unaccepted, preserving
their separate intervals and multiplicities. They are never merged by distance.
Changing the captured model or replacing its evaluator during callbacks
invalidates every accepted point and clears the model completeness claim.

## Conservative arbitrary trim membership

Each nested trim wrapper's actual `contains` method is checked; the default
argument is preserved unless `trim_tolerance` is explicitly supplied. Only an
actual scalar bool is usable evidence. Callback exceptions and invalid truthy
values are unavailable. `representative_contains` describes these checks alone.
Callbacks must be stable during the call; the API cannot prove arbitrary code
or mutable hidden state follows a mathematical predicate.

A nearby float satisfying a mask does not prove the exact root satisfies it.
For example, float(sqrt(2)) lies above the exact root: x>=float(sqrt(2)) includes
that representative while excluding the root. Therefore a trimmed model root is
accepted only when its enclosure-to-float bound is exactly zero and every trim
check is true at that exact point. This handles the flat origin, dyadic endpoints
and exact tangencies. Nonbinary rational/irrational roots under arbitrary masks
remain `root_trim_membership="unverified"` and are omitted from `points`, even
when the representative is included. Their untrimmed model records are retained.
An exact point rejected by a mask is `exact_point_excluded`; an accepted one is
`exact_point_accepted`. `trimmed_root_completeness` remains false conservatively.

This API performs no scene edits, registry calls, deployment or default-policy
changes. The general numerical finder and supplied-candidate diagnostics retain
their contracts. General flat callback certification, arbitrary irrational-root
trim membership and higher-degree models remain future work.
