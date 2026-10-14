# Composed field and level-set gradient diagnostics

Version 0.23.0 extends gradient_diagnostics(x, y) to CurveField, BlendedField and
LevelSetCurve using the existing algebra query and adaptive estimator.
SignedDistanceField.level_set() reuses the existing generated procedural contour
to preserve native geometric derivatives.

## Reproduced failures

Source-circle containment signs multiplied by sampled chord magnitudes can jump
at the true boundary. In 0.22, the source diagnostic rejected that gradient,
but a generated blend contour reported the fixed-step vector near (18756, 18756)
as analytic with no error estimate, accepting a fabricated diagonal normal.
The opt-in composed diagnostic now preserves unavailable source errors and
returns two NaNs; its cheap normal rejects unknown uncertainty. This does not
substitute an exact source-circle signed distance.

At a square corner, a native undefined distance gradient became (-0.5, -0.5)
in its old plain procedural level set. The reused wrapper now retains two NaNs
and rejects the normal. At a regular tiny-square point, it preserves the native
unit gradient and usable normal across scales.

## Query and compatibility contract

- Explicit diagnostics use existing add/subtract/product/quotient/average chain
  rules and active min/max winners. Exact ties with disagreeing gradients stay
  unavailable. Inactive numerical branches are not probed.
- Shared fields, generated contours and constant shifts share source diagnostics
  per query. No input/graph results are retained between calls; live edits remain
  visible. Cycle guards span generated and unary wrappers. Shared reuse assumes
  pure, pointwise callbacks.
- Diagnostic gradient has two NaNs if a source/component/error is unresolved,
  coordinates are nonfinite, or the composed/shifted value is nonfinite.
  Availability preserves Python scalar versus NumPy 0d/broadcast/empty shapes.
  Raw composed candidates can already contain masked child gradients; supplied
  source raw candidates remain available in sources.
- Sources retain method, status, derivative target, distance model, raw candidate,
  heuristic error and reported evaluation count when supplied. Aggregate
  field_evaluations is None: probe counts omit graph/shift value checks and
  unknown callback internals.
- Heuristic errors propagate with absolute chain-rule factors, without value
  uncertainty. They are not rigorous bounds. Native/symbolic/provided errors
  remain unclaimed; an all-unclaimed graph reports error_estimate=None.
  Known numerical contributions can coexist with unclaimed provided errors.
  Certified is always false. Finite availability is sampled consistency or
  supplied/native finite validity, not a universal source-curve certificate.
- Supplied gradients and diagnostic availability/errors remain authoritative.
  Custom value-only overrides are diagnosed against the actual callback.
  Root super delegation and nested overrides retain their contracts. Exceptions
  propagate without retry or per-point vectorization; scalar callbacks receive
  Python floats and arrays receive the full broadcast shape.
- Cheap gradient adds no new adaptive work. Native SDF contours now use their
  geometric gradient; numerical source gradients retain the cheap estimate.
  Generated normals reject unknown uncertainty instead of normalizing it.
  Explicit diagnostic queries do not mutate later cheap normal behavior.
  CurveField around ordinary ProceduralCurve retains its pre-existing diagnostic
  cost in algebra. Supplied gradients remain the caller's responsibility.
- Levels are finite representable f-level shifts in field units, not Euclidean
  offsets. Callback serialization keeps the existing unavailable-code placeholder.

The unchanged estimator makes at most 321 vector evaluations per distinct
numerical source, plus graph/shift value checks. Smooth axes can remain
unresolved: 2*x-3*y at decimal (0.3, 0.2) returns a correct raw candidate but
exhausts the y budget near a cancelling value, so availability stays false.
Finite probes cannot rule out hidden features, noise or aliasing. No new scale/
domain solver, persistent graph, cache or exact curved-distance engine is added.

## Evidence and complete-call costs

Analytic regressions cover all seven operations, shared wrappers, corners/medial
points at three scales, an exact annulus cusp, shape/domain masks, callback
authority, value-only overrides, super delegation, cycles and opt-in budgets.
Independent read-only review and full Work17/exact feature/dev CI results are
recorded with the milestone PR and handoff.

Sequential warm complete-call medians on Work17 Python 3.11.14/NumPy 2.4.6:

| Workload | 0.22 gradient ms | 0.23 gradient ms | 0.23 diagnostics ms | Affine callback calls | Available vectors |
|---|---:|---:|---:|---:|---:|
| native_tiny_contour | 27.395 | 0.708 | 0.970 | 0 | 1/1 |\n| callback_blend_scalar | 0.121 | 0.151 | 0.817 | 18 | 1/1 |\n| callback_shared_alias_64 | 0.198 | 0.267 | 1.138 | 18 | 64/64 |\n| sampled_jump_contour | 16.130 | 21.689 | 856.875 | 0 | 0/1 |\n| sampled_smooth_contour | 17.622 | 19.030 | 76.299 | 0 | 1/1 |

The counter covers the explicit affine callback only; zero does not mean no work.
Raw [0.22](field_diagnostics_0.22.0_work17.json) and
[0.23](field_diagnostics_0.23.0_work17.json) results include normal timings and
rejection messages, source probe counts and three measured batches. Normal
timings can measure rejection. Shared-workstation medians do not establish
speedups or FPS. The shared 64-point query diagnoses the affine source once,
with 17 vector probes plus one graph value call, while its cheap gradient uses
five callback calls. Expensive curved source diagnostics remain explicit.
No query arrays were retained in the weak-reference check.

Reproduce in separate processes with the same installed dependencies:

    python benchmarks/field_diagnostics.py --repository . --label current --output field-costs.json
    python -m pytest tests/test_field_gradient_diagnostics.py tests/test_field_algebra.py

Possible follow-ups include deliberate source-curve distance semantics, explicit
scale/domain policies and evidence-led numerical normal consumers. These remain
separate from the bounded studio preview and unverified native WebMCP host.
