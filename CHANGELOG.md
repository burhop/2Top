# Changelog

## 0.27.0

- Reproduce the four x**8/line residual-filtered candidates; an analytic/160-digit
  Decimal oracle shows three are about 0.04 from the only root despite 1e-12
  residuals. Preserve legacy acceptance and iteration budgets for compatibility.
- Add public diagnose_intersection_candidates with every supplied position
  explicitly unverified, no positional error bound and unassessed isolation,
  completeness and overlap. It performs no root search, filtering or registration.
- Report row-normalized sampled Jacobian conditioning, derivative-error evidence
  and linearized displacement separately from trim membership. Singular or
  uncertainty-dominated models have no displacement; none is a root certificate.
- Preserve active evaluators, callback defaults and actual boolean trim evidence;
  callback/nonfinite/unrepresentable evidence is reported unavailable.
- Add 72 regressions, JSON/PNG independent-oracle example, measured opt-in costs
  and exact parity across nine legacy solver traces. Synchronize versions,
  README, changelog and CI coverage; defer quadratic/line acceleration.


## 0.26.0

- Profile the general parabola/line tangency: 62 starts all exhaust the existing
  600-evaluation budget, totaling 37,324 field-system calls.
- Skip redundant NumPy broadcasting dispatch after both coordinate inputs pass
  existing real-number validation and already have equal shapes. Keep scalar/0d,
  dtype, aliasing, strides, writeability and unequal-shape behavior.
- Preserve all solver budgets, starts and final residual/mask checks. Nine
  workloads retain identical ordered solver traces and outputs. Paired Work17
  complete-call medians improve from 1.98 s to 1.47 s on the parabola control.
- Reject short-budget acceptance after a higher-order tangency counterexample;
  document existing accuracy limits and evidence-led next opportunities.
- Add 62 coordinate/analytic regressions and a parabola JSON/PNG demonstration;
  synchronize versions, README, documentation and CI lint/path coverage.


## 0.25.0

- Recover one isolated contact for native circle/line and circle/circle exact
  tangencies without merging distinct nearby crossings. Large-circle duplicate
  contacts and a strongly scaled unit-field miss reproduce the prior gap.
- Bound recognition to native low-degree rational/Float coefficients and
  unchanged evaluation kernels; custom callbacks and nonzero discriminants
  retain the existing numerical path. Coincident circles do not enumerate roots.
- Validate actual finite field residuals, final trims, search/point limits and
  registry callbacks. Independent review corrected nonfinite sentinel acceptance.
- Add 104 regression cases, a JSON/PNG contact/crossing demonstration and
  complete-call timing evidence. Preserve 0.24 thin-trim candidate recovery.
- Synchronize versions and documentation. No general symbolic solver, certified
  positional accuracy or guarantee to find all tangencies is introduced.


## 0.24.0

- Recover interior and endpoint crossings lost when exact trim rectangles
  discarded every coarse grid seed. Retain one actual linspace cell around the
  rectangle for candidate generation; final contains and residual checks remain.
- Append finite explicit trim endpoint seeds after clustering, including when
  there are no grid candidates. Endpoints remain untrusted solver starts.
- Skip incomplete rectangle exclusion filters consistently with trim membership.
  Preserve both original inputs and activation threshold for legacy overlap
  heuristics, keeping padded seeds in the refinement path.
- Add 43 analytic regressions, a reproducible segment/circle JSON/PNG example,
  independent review and complete-call costs. Results remain numerical; no
  completeness, exactness, new symbolic solver or general overlap guarantee.
- Synchronize project/studio/JavaScript versions and documentation. Scene formats,
  dependencies, main, deployment and security settings remain unchanged.


## 0.23.0

- Extend the established gradient_diagnostics protocol to CurveField,
  BlendedField and LevelSetCurve. Existing query-local algebra propagates
  availability and heuristic errors; repeated contours/shifts share source probes.
- Reuse the existing procedural contour for SignedDistanceField level sets,
  preserving native nearest-feature gradients and corner/medial uncertainty.
  Generated numerical contours no longer mislabel fixed-step gradients analytic.
- Keep new adaptive probes opt-in. Cheap normals reject unknown numerical
  derivatives; explicit diagnostics can return useful uncertified vectors.
- Preserve supplied gradients/diagnostic callbacks, live edits, scalar/0d/
  broadcast/empty shapes, finite-domain masks, cycle guards and super delegation.
  Level shifts remain field-unit shifts with existing serialization placeholders.
- Analytic regressions, independent review and complete-call measurements cover
  validity and costs. Curved-distance and native WebMCP host limits remain.


## 0.22.0

- SignedDistanceField exposes the established gradient_diagnostics protocol
  using the unchanged bounded adaptive estimator. Numerical diagnostics report
  raw candidates, heuristic uncertainty, per-axis status/steps and call counts;
  unresolved or nonfinite vectors return two NaNs.
- Diagnostic targets explicitly distinguish native endpoint geometry, provided
  gradients and evaluated sampled/custom fields. Source-sign/chord-magnitude
  jumps are rejected without substituting an exact curved signed distance.
  Sampled consistency remains uncertified and smooth axes can remain unresolved.
- Provided gradients and scalar/array field/containment callbacks remain
  authoritative. Native dispatch now also guards _evaluate_vectorized overrides.
- Legacy curved/callback gradient behavior and algebra/level-set normal paths
  retain their prior approximation; diagnostics are opt-in. Analytic circle,
  annulus and domain oracles, independent review and complete-call measurements
  document correctness, budgets and remaining costs.

## 0.21.0

- Native straight-boundary SDF gradients use nearest-feature geometry instead
  of a fixed central-difference step. Smooth interiors/exteriors and boundaries
  return unit normals across tiny and huge scales; genuine corners and different
  equally nearest projections return two NaNs. Shared vertex projections remain
  valid away from the boundary.
- Exact rational adjudication handles guarded ties, rounded-zero distances,
  overflowing magnitudes and uncertain projections. Exact rectilinear side
  limits and subtraction residual comparisons bound common-case costs.
- Captured live endpoint chains drive each query's sign and gradient without
  retaining query buffers. Curved/custom field and containment callbacks keep
  their previous finite-difference contract; existing procedural level-set
  normals remain numerical. No topology or universal-rounding claim is added.
- Analytic/high-precision regressions, independent review and complete-call
  baseline measurements document supported behavior and remaining overhead.

## 0.20.0

- Native straight endpoint boundaries use a strict SDF-only odd/even sign
  predicate, including holes, reversed edges and concave polygons. Exact
  rational crossings resolve guarded overflow, underflow and near-boundary cases.
- Exact zero distance returns canonical positive zero. Public region/trim
  containment tolerance is unchanged; custom callbacks keep their calling
  conventions and internal errors propagate without a retry.
- A bounded endpoint projection fast path avoids unnecessary compensated
  arithmetic on ordinary queries. Interior, uncertain and extreme queries keep
  the 0.19 robust kernel and all its rational/high-precision regressions.
- Full sampled-circle measurements compare both 0.18 and 0.19; remaining curved
  source, constructor, approximation and derivative limits stay explicit.

## 0.19.0

- Segment distances use clamping/hypot for axis-aligned edges and separately
  scaled, compensated projection for oblique edges. Remove the absolute short-
  edge cutoff and squared-distance overflow; only identical endpoints are points.
- Bounded high-precision fallback handles observed overflow, underflow, endpoint
  rounding and cancellation. Nonfinite endpoint geometry raises explicitly.
- Exact-rational/high-precision fixtures cover tested tiny/huge coordinates,
  translations, degeneracy, reversal, holes and scalar/broadcast paths.
- Ordinary and fallback-heavy measurements document added arithmetic costs;
  curved sampling, containment tolerances and derivative limits remain explicit.

## 0.18.0

- Removed borrowed-grid/result and sampled-boundary caches from signed distance.
  Live coordinates, regions, outer boundaries and holes are read on every query.
- Generic polygon containment reads live segments/endpoints; straight edges use
  endpoints directly. This closes the stale vector sign after coherent edits.
- Nearest hole boundaries contribute to distance magnitude; broadcast, scalar,
  invalid-coordinate and empty-result paths retain explicit contracts.
- Unavailable boundaries raise ValueError instead of fabricating unit distance.
  Curved sampling and legacy short-segment/overflow limitations remain explicit.
- Independent distance oracles, defensive-result/retention regressions and warm
  before/after measurements document correctness and repeated-query costs.

## 0.17.0

- Verify selected locked artifact URLs/hashes against canonical release metadata;
  preserve h11's existing 0.16.0 pin independently of the project version.
- Occupancy derivatives explicitly reject guarded jumps, observed membership
  transitions and known invalid boundary domains; valid constant pieces keep
  zero derivatives. Equal finite outputs remain constant without region queries.
- Direct binary occupancy level sets now reject empty/plateau sets instead of
  creating interpolated regular curves. Existing region boundaries remain the
  boundary-geometry API; finite strict-interior values and schema stay compatible.
- Removed unsafe cross-query occupancy caching. Mutated coordinates, results,
  live values and region replacements are read afresh. Broadcast shapes, scalar
  callbacks and live scalar JSON export retain their contracts.
- Independent analytic/edge fixtures, separate review and saved warm measurements
  document the added validation cost and finite-sampling/topology/rendering limits.

## 0.16.0

- Native algebraic fields reuse analytic child derivatives for quotient and
  min/max composition, preserving left folds and explicitly undefined winning
  ties/singular quotients. Binary exponent scaling handles tested extreme ratios.
- Query-local graph reuse avoids repeated shared-node callbacks while preserving
  mutable expressions, methods and operations; native cycles fail explicitly.
- Blended contours retain derivatives and propagate known procedural heuristic
  uncertainty, including stationary children and nested shifts. Serialization
  keeps the existing honest procedural placeholder.
- Independent symbolic/analytic regressions and reproducible warm measurements
  record corrected translated derivatives, fewer callbacks and the additional
  validity-check overhead on cheap direct grids.

## 0.15.0

- Default procedural gradients choose local representable steps and bounded
  refinement/expansion instead of requiring hints for the measured translated
  and small-feature fields. Existing explicit scales and analytic callbacks
  retain their paths and serialization contracts.
- Diagnostics expose per-point selection/status, actual steps and probe counts;
  off-ladder and shrinking one-sided checks reject tested alias/cusp failures.
  Unresolved estimates carry infinite uncertainty. Sampled-flat axes retain
  quantization uncertainty and regular affine normals without proving constancy.
- Independent analytic fixtures show successes, budget/precision failures and a
  smooth hidden-feature counterexample to any universal accuracy certificate.
  The simple grid costs about 4.35x the previous default; fixed hints/callbacks
  preserve performance options. The hard cap is 321 vector evaluations.

## 0.14.0

- Sublevel queries distinguish bounded, proved empty and unknown sets. Supported
  native quadratics use exact stored coefficients and checked outward endpoints;
  unsupported/custom/unbounded fields remain unknown.
- Smooth R-function bounds propagate alpha/2 through nested operands in field
  units. Unknown union operands no longer borrow a known child's box and discard
  remote intersections. Searches retain finite-domain limits.
- CurveField level sets retain stable numeric kernels, gradients, procedural
  normal guards and scalar/broadcast contracts through LevelSetCurve. Serialized
  wrappers preserve source types and honest callback placeholders.
- Expression/variable assignment invalidates native compiled kernels, keeping evaluation
  consistent with enclosure proofs. Independent analytic regressions and saved
  before/after measurements document fixes and mathematical/performance limits.

## 0.13.0

- Procedural gradients use actual representable coarse/fine stencils and
  nonuniform Richardson correction, replacing the universal fixed `1e-8` step.
- Keyword-only analytic gradient callbacks and scalar/pair local scale hints
  preserve scalar/broadcast APIs, scalar-only callback fallback and honest
  placeholder serialization.
- Diagnostics expose heuristic uncertainty and actual displacements; numerical
  normals reject unresolved sampling and output quantization. Analytic and
  subclass gradients retain finite/domain/zero-gradient validation.
- Independent analytic fixtures and regression cases cover translations, small
  scales, large field offsets, axis independence and subnormal uncertainty.
  Numerical gradients require nine field probes instead of four; no universal
  accuracy or performance guarantee is claimed.

## 0.12.0

- Reusable symbolic/procedural evaluators broadcast real coordinates, constant
  values and gradient components consistently, preserving scalar and array APIs.
- Normal directions remain stable under finite field rescaling; singular or
  nonfinite domains fail explicitly.
- Scaled rationalized smooth union avoids overflow, underflow and small-weight
  cancellation; independent high-precision tests cover extreme finite values.
- Contour extraction validates grids, vector-selects crossing triangles, retains
  tiny/translated cycles and deduplicates zero edges. Branched, clipped or world-
  collapsed components are counted and omitted deterministically in Python/JS.
- Reproducible before/after timings report extraction gains and blend overhead.
  Schema 4, 23 tools and dependencies remain compatible; arbitrary smooth-field
  bounds and fixed procedural derivative steps remain explicit limitations.

## 0.11.1

- Sticky phone Canvas/Layers/Timing jumps retain previews and reduce long-page
  navigation; Canvas also exits Recipe view.
- Export menus remain clickable above the phone bar. Authoritative Recipe view
  now uses confirmed scene data rather than an uncommitted preview.
- Pose selection survives same-time geometry edits and restores through known
  timing Undo/Redo with bounded local memory; import/context changes clear it.
  Native pose-chip focus returns after saves without stealing intervening focus.
- Optional document/session mutation guards reject cached edits across equal-
  revision restarts. Offline edits lock; reconnect reads and changed sessions clear
  stale previews. Bounded save confirmation and lost-reply reconciliation never
  automatically replay an ambiguous write.
- Regression QA preserves baseline failures and tests owned loopback restarts,
  browser offline simulation and integrated authoring. No new art operation,
  recipe/geometry/dependency change or deployment is introduced.

## 0.11.0

- Anchored timing stretch/compression with first/last selected pose, visible
  playhead and custom-time anchors. Scaling shares selection and the timing
  preview/Apply/Cancel path, including source/destination lists and focus return.
- The 23rd tool `scale_keyframes` scales explicit tracks around a required anchor,
  with exact identity/fixed-anchor behavior and atomic collision/range rejection.
  Poses, easing, base geometry, schema 4 and dependencies remain compatible.
- Desktop/touch combined authoring acceptance and an evidence-producing walkthrough
  cover move, align, compress, shift, undo/redo and export. The next step is
  integrated usability/reliability review and polish rather than more features.

## 0.10.0

- Multi-keyframe retiming with desktop/touch key selection, a shared time shift,
  Preview, Apply, Cancel/Escape and one undoable edit. Complete poses/easing stay
  attached; selected keys vacate together and may cross unselected keys.
- The 22nd shared `retime_keyframes` tool supports 1..16 explicit island tracks
  atomically, rejecting all targets on any collision, missing key or 0..12s range
  failure. Geometry, schema 4, dependencies and direct-protocol playback remain.
- Version, README, guides, roadmap and desktop/touch/protocol acceptance coverage
  updated; native WebMCP/model-host verification remains separate.

## 0.9.0 — center alignment and even spacing

- Add desktop/touch center-layout Preview, Apply and Cancel, preserving one atomic undo step.
- Align authored centers on either axis; space three or more evenly with fixed outer centers and stable ID tie-breaking.
- Translate complete base/pose tracks without changing shape, timing/easing, styles, selection or schema 4; preserve retained blend references and reject blend-record layout selections explicitly.
- Freeze the displayed preview playhead, pause only on UI apply when needed, and reject stale/out-of-bounds layouts without partial commits.
- Expose `layout_islands` through all validated adapters, bringing the catalog to 21 tools. Native/model-host verification remains separate.
- Cover numeric parity, selection edges, real protocol/manual undo, desktop/phone acceptance and clean packaging. Next independent coding step: multi-keyframe retiming.

## 0.8.0 — multi-selection and whole-path arrangement

- Add desktop additive selection and touch-friendly Select multiple/Select visible controls, with shared selection and clear group feedback.
- Move, uniformly scale and rotate selected islands/blends through atomic `transform_layers`; expand retained operands and transform shared sources once.
- Transform base poses and every authored key together, preserving times/easing, styles, layer order, selection and recipe schema 4; reject any out-of-bounds result without clamping or wrapping.
- Preview coherent group drags with Escape/cancellation and stale-revision rejection; retain existing single-island current-pose editing.
- Expose the validated command through real MCP HTTP/stdio and the WebMCP adapter, bringing the catalog to 20 tools. Native/model-host verification remains separate.
- Add numeric/source parity, persistence/rollback/protocol and actual desktop/phone browser coverage; document the next independent alignment/spacing step.

## 0.7.2 — measured first-run and interaction reliability

- Preserve slider keyboard focus after asynchronous saves, without stealing focus after another interaction.
- Skip drawing into a transient zero-size canvas and recover when layout supplies valid dimensions.
- Add real-browser profiling for authored motion, eight layered islands and two static blends at 48 contours; document measured complexity without reducing quality or changing geometry.
- Verify clean editable and packaged-wheel startup outside the checkout using only declared studio dependencies; add a clean-wheel CI gate.
- Correct quickstart version/schema guidance and use explicit virtual-environment Python commands; protect the existing Work17 demo with a separate test port.

## 0.7.1 — reviewed reliability fixes

- Complete reorder/delete batches against final-state invariants instead of raising list-removal errors; reject malformed final states atomically.
- Validate selection against actual layer records rather than transient order entries.
- Add process session metadata so same-revision service restarts refresh both undo controls and coauthor history; preserve active gestures and playback.
- Preserve explicit blend-editor choices until a new canvas/shared selection, including New pair and a second blend.
- Derive native browser tool expectations from the actual catalog; native-host support remains unverified.
- Add direct, HTTP, real MCP and browser regressions. Lone-surrogate Unicode was already safely rejected; preserve valid supplementary text without extra sanitization.

## 0.7.0 — guided coauthoring

- Add actual local client setup and an explicit official MCP protocol helper.
- Show committed activity by observed route, with server-computed changes and undo/redo references.
- Treat caller actor hints and batch notes as unverified data, preserving legacy fields.
- Keep schema 4, geometry-engine reuse, bounded commands, retries and persistence semantics.
- Exercise real MCP edits followed by browser refinement, conflicts and shared undo/redo.
- No included model, live natural-language host claim, native WebMCP verification, release or deployment.

## 0.6.0 — composition layers

- Add complete bounded layer ordering, visible front/back controls and dependencies.
- Expose per-island/blend visibility, palette and opacity through shared commands.
- Composite each complete layer once; preserve SVG group order/opacity and source fields.
- Select frontmost visible artwork; explain hidden/consumed source editing with explicit handles.
- Migrate older recipes to schema 4 without changing their original drawing order or geometry.
- Add the Glasswater layered study, real raster checks and desktop/phone acceptance coverage.
- Native WebMCP host execution remains unverified; no release or deployment is included.

## 0.5.0 - 2026-10-11 (development)

- Add non-destructive two-source static union/smooth union using the existing RFunctionCurve/CurveField engine. Blend amount is dimensionless; no signed-distance or Euclidean-offset claim.
- Add a bounded deterministic contour sampler and matching browser evaluation/contours, cached committed previews and coarser gesture previews. Handle multiple components and omit open/degenerate fragments explicitly.
- Add source selectors, amount/operation controls, source guides and the Confluence study artistic demo; live base-shape edits update the result, and removing a blend retains its sources.
- Add shared create_blend/update_blend/delete_blend commands with revisions, atomic batches, persistence and undo/redo. Reject animated/nested/cyclic operands and unsafe source deletion.
- Export schema 3; migrate schema 1/2 with empty blends and preserve existing geometry/tracks. Keep legacy algorithms and older authored sample files intact.
- Add field/contour parity, geometry bridge, input/budget/migration, real MCP-client and actual desktop/phone browser workflows. Native WebMCP remains unverified.

## 0.4.0 - 2026-10-11 (development)

- Display the selected island's authored center path with labeled pose handles; drag one position without replacing its other shape values or easing.
- Retime a selected key across neighbors with sorted tracks; reject occupied times and out-of-range values without committing. Show matched/jumping/missing loop endpoints.
- Expose the same position/retiming operation as validated `edit_keyframe` through UI, MCP HTTP/stdio and the WebMCP adapter; preserve batches, revisions, retries, persistence and undo/redo.
- Retain schema 2 for unchanged 0.3.x recipe compatibility and the existing 0.2.x migration. Keep legacy geometry and authored sample files intact.
- Add edge-case, interpolation/parity, real MCP-client and desktop/phone pointer workflow coverage; document current-dev startup on Work17. Native WebMCP host execution remains unverified.

## 0.3.0 - 2026-10-11 (development)

- Author up to 24 complete poses per island for position, scale, stretch, rotation and curl; interpolate deterministically with linear or smooth easing.
- Capture, select, replace and delete pose keys; keyed drags/sliders freeze the playhead and commit one reversible action. Duplicate preserves and offsets choreography.
- Share validated `set_keyframe`/`delete_keyframe` commands across manual UI, real MCP HTTP/stdio and the browser adapter; retain revision checks, atomic batches, persistence and undo/redo.
- Add the Orbit & bloom creative demo and version-2 JSON interchange; migrate existing schema-1 recipes without changing base parameters or adding motion tracks.
- Add interpolation/parity, malformed-input, persistence, MCP and real-browser regression coverage. Native WebMCP host verification remains pending.

## 0.2.1 — 2026-10-11 (development)

- Keep the canvas and recipe workspace within their responsive column; fix the 29-pixel horizontal overflow reproduced at a 390-pixel phone viewport.
- Scope the invalid-JSON browser assertion to the error notification instead of matching unrelated range-control outputs.
- Reopen the actual downloaded JSON recipe after a new edit and verify the restored scene survives page reload.
- Pass all nine real Chromium acceptance cases locally; inspect desktop, phone and tablet screenshots and retain layout diagnostics in the browser report.
- Keep native WebMCP host interoperability separate: the tested Chromium build lacks document.modelContext and correctly retains the manual editor and MCP connection instructions.

## 0.2.0 — 2026-10-11 (development)

- Add Tidal Atlas, a canvas-first kinetic-art studio with editable contour islands, palettes, presets, animation, selection, undo/redo and JSON/SVG/PNG interchange.
- Add one typed, bounded scene service shared by manual UI, MCP and browser WebMCP, including atomic batches, optimistic revisions, replay keys and durable local recipes.
- Add official MCP 2.3.0 HTTP/stdio transports and feature-detected document.modelContext integration.
- Add reusable kinetic fields/curves with existing geometry, SceneManager and graphics-backend interoperability.
- Add protocol, geometry and DOM regression coverage plus nine real Chromium acceptance tests in CI.
- Install studio extras in the inherited CI so the new tests can be collected; retain repository-wide lint and formatting gates, with a separate mechanical cleanup of ten inherited Markdown examples.
- Target dev for integration; preserve its performance commits and keep main unchanged.
- Acceptance gap at the original handoff: Chromium had not run and publication was blocked. The recovery branch and PR #4 are now published; 0.2.1 addresses the browser failures. Native WebMCP/model-host interoperability remains a separate host-specific check.

## 0.1.0 — existing baseline

- Reusable implicit geometry engine, scene management, graphics extraction and diagnostic UI.
