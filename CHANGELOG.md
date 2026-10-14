# Changelog

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
