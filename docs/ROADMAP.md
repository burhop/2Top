# 2Top development roadmap

Development updates target dev with synchronized versions, README/changelog,
local checks and passing CI on the exact feature commit before integration.

## 0.3.0 — authored island choreography

This milestone adds complete pose keys, deterministic linear/smooth sampling,
direct editing at a frozen playhead, reversible shared commands, schema-2
save/reopen and the Orbit & bloom demo. It retains the reusable legacy geometry
engine and loads 0.2.x recipes without introducing tracks or changing base poses.
It does not complete the broader 2Top vision.

## Host verification — separate follow-up

Validate native WebMCP registration and actual agent execution in the intended
supported top-level browser/model host. Work17 Chromium lacks modelContext;
mocked adapter contracts and real MCP clients cannot establish this capability.
Record host/version and real shared-scene edits without changing security flags
or pretending the unsupported browser is connected.

## 0.4.0 - editable motion paths

This milestone shows labeled selected-island center paths. Positional handles
and key retiming use the same validated edit_keyframe command through UI/MCP/
WebMCP. Crossing keys are sorted; occupied times fail atomically. Seam indicators,
undo/redo, schema-2 persistence and desktop/phone pointer coverage remain shared.
0.3.x tracks reopen unchanged and 0.2.x retains its empty-track migration.
The path is an authored center guide; curved paths and tangent tools are future
work. See [Work17 quickstart](work17_quickstart.md) to try the demo.

## 0.5.0 - bounded geometry blending

This milestone exposes legacy union/smooth union for two static island sources,
bounded sampled previews, source-preserving editing, shared commands and schema-3
persistence. Python/browser field and contour parity and real browser workflows
cover the composition. Animated/nested operands remain unsupported; numeric
field levels are not Euclidean offsets. Native WebMCP remains a separate gap.

## 0.6.0 - controlled composition layers

The existing island/blend records gain bounded order, shared visibility and
palette/opacity controls. Group alpha applies once to complete artwork. Source
dependencies are explicit; hidden/consumed sources remain editable through their
selected guides and handles. Schema 4 preserves older drawing order and fields.
Glasswater demonstrates visible depth. This does not add nested/animated graphs.

## 0.7.0 - guided coauthor workflow

The activity view distinguishes observed UI/MCP/HTTP bridge routes from caller
notes and summarizes actual committed data changes. Setup uses real local launch
settings and tool schemas. The coding-agent walkthrough uses an actual MCP
protocol client, browser refinement and cross-client undo/redo. Protocol scripts
and saved artwork are accurately labeled; no separate live model-client inference
session or supported native WebMCP host was exercised.

## 0.7.1 - focused reliability review

Fix batch ordering/deletion completion and rollback, same-revision restart
history reconciliation, explicit blend-editor precedence and stale native tool
test expectations. Unicode rejection is regression-covered, not redundantly
sanitized. Preserve the live demo and LAN settings during this patch pass.

## 0.7.2 - evidence-led performance and first-run usability

Profile actual authored motion, eight layered islands and two static blends at
48 contours. Keep existing accuracy and sampling quality: cached interactions
are satisfactory on Work17, so document complexity and reproducible measurements.
Fix reproduced keyboard focus loss and zero-size canvas layout errors. Verify
clean editable/wheel startup outside the checkout without development packages,
and keep a packaging CI gate. Preserve the live user demo and pending LAN settings.

## 0.8.0 - multi-selection and whole-path arrangement

Compose multiple existing layers together: additive/touch selection, coherent
dragging, nudge, uniform scale and rotation. The shared command moves whole
authored paths and resolves retained blend sources once. Bounds, revisions,
undo/redo and schema-4 compatibility stay authoritative; no new group graph or
engine formula is introduced. [Authoring contract and walkthrough](group_authoring.md).

## Completed authoring follow-through

Version 0.9.0 completes alignment/spacing through authored-center anchors,
whole-path translations, explicit island/source selections and a preview flow.
[Center-layout contract](center_layout.md) records the bounds and limitations.

## 0.9.0 - center alignment and even spacing

Align island centers on either axis; distribute three or more with fixed outer
centers and deterministic ties. Shape/timing, schema 4 and blend references stay
intact. Desktop/touch previews freeze the displayed playhead and apply one
reversible transaction. Stale/invalid layouts reject atomically. Center placement
does not guarantee equal edge gaps or collision avoidance.

## 0.10.0 - multi-keyframe retiming

Version 0.10.0 completes multi-keyframe retiming with transient desktop/touch key
selection, a frozen preview and one shared time shift. The 22nd tool supports
multiple explicit island tracks atomically, rejecting any occupied/out-of-range
destination. Poses/easing remain attached; selected times vacate together.
[Retiming contract](multi_key_retiming.md).

## 0.11.0 - anchored time scaling

Version 0.11.0 completes anchored time scaling, reusing selection and timing
previews with atomic collision/range rejection. First/last selected pose, visible
playhead and custom anchors remain explicit at commit time.
[Scaling contract](anchored_time_scaling.md).

## 0.11.1 - integrated authoring reliability patch

The bounded review reproduced pose-selection loss during geometry edits and
cached-preview acceptance across equal-revision restarts. Phone section jumps,
bounded selection restoration, context guards and explicit reconnect/save-failure
handling address those flows. Regression evidence includes actual owned loopback
restarts and clearly labeled browser offline/transport simulation.
[Reliability contract](authoring_reliability.md).

## Independent authoring stopping point

The tested move/layout/capture/shift/scale/undo/import flow is coherent. Do not
extend it with unrelated features merely to continue development. Hands-on creator
feedback, actual phone/network checks and native model-host verification remain
distinct from these automated passes; follow up only on a concrete new defect.

## Most important remaining showcase gap

Exercise the guided workflow in the user's intended, already configured model
client with genuine natural-language tool choice and visible shared edits. Record
the actual client/session and manual refinement; protocol acceptance alone does
not prove that integration. Native WebMCP separately needs an available supported
top-level browser/model host. No extra geometry feature should substitute for
this connection evidence, and no new credentials, permissions or paid API usage
are implied by this roadmap.

## Subsequent geometry work

Version 0.20.0 separates strict native endpoint/hole distance signs from public
fuzzy containment and retains custom callback contracts. Guarded endpoint and
nearest-segment arithmetic reduce full sampled-curve costs while preserving the
0.19 robust fallback. [Independent oracles, measurements and limits](distance_sign_performance.md).
The next concrete geometry opportunity is the existing fixed-step SDF gradient's
validity at corners, medial axes and tiny features. Curved source/chord agreement,
constructor scale limits and native model-host verification remain separate.

Version 0.19.0 corrects short-edge and overflowed segment distances with scaled,
compensated projection and bounded precision fallbacks. [Oracles, costs and
limits](distance_numerics.md). Default containment tolerance still reverses the
sign near a tiny hole in a recorded case; distance sign/precision semantics are
the next concrete opportunity. Sampled curves and derivative uncertainty remain
separate contracts.

Version 0.18.0 repairs signed-distance query freshness and the generic polygon
containment dependency, includes nearest hole boundaries and retains no query
buffers. [Analytic cases, measured cost and limits](distance_cache.md). The next
reproduced gap is scale-stable segment projection: absolute short-edge thresholds
and squared-distance overflow remain. Curve sampling and derivative uncertainty
require their own contracts; generic implicit values are not distances.

Version 0.17.0 corrects occupancy derivative/boundary validity, discrete level-set
semantics and unsafe cross-query mask caching. [Contracts and cost](occupancy_validity.md).
Signed-distance cache/derivative validity and domain/noise contracts remain
independent opportunities; generic discontinuous plotting still assumes more
continuity than arbitrary user predicates can guarantee.

Version 0.16.0 supplies native analytic algebraic derivatives, query-local shared
graph reuse and derivative-preserving contours with known procedural uncertainty.
[Contracts and measured overhead](field_algebra.md). Domain-aware sampling,
distance/occupancy derivative diagnostics and wider proved bounds remain useful
independent increments. Cheap direct grids retain measurable validation overhead.

Version 0.15.0 adds bounded automatic procedural steps, tested one-sided/off-ladder
consistency, per-point diagnostics and explicit failure/cost measurements.
[Automatic derivative contracts](automatic_derivatives.md). Finite samples still
miss some smooth hidden features; known scales and analytic callbacks remain
important. Domain/noise contracts and general algebraic-field derivatives are
useful separate correctness increments.

Version 0.14.0 completes supported quadratic sublevel envelopes, recursive smooth
blend level propagation and stable CurveField level-set wrappers.
[Bounds contracts, measurements and limitations](sublevel_bounds.md). Higher-degree
and domain-bound envelopes, interval evaluation and general algebraic-field
derivatives remain separate useful increments.

Version 0.13.0 addresses procedural derivative accuracy with representable
stencils, explicit local scales, diagnostics and analytic callbacks.
[Contract and analytic measurements](procedural_derivatives.md). Zero-contour
boxes cannot infer generic blend growth; 0.14 supplies supported sublevel proofs.

Version 0.12.0 delivers a bounded reusable backend pass: broadcast evaluation,
scale-stable normal and smooth union numerics, finite sampling validation and
deterministic contour cycles. Saved timings measure extraction gains and stable
blend overhead. [Contracts, reproduction and remaining gaps](implicit_backend.md).

Introduce a bounded subset of reusable primitives and reversible composition
(union, difference, blend) into the artwork studio. First specify how those
operations interact with tracks, immutable snapshots and persistence. Local
shoreline pinning, freeform deformation and exact continuity constraints need
their own geometry contracts and numerical acceptance cases. Physical tide
simulation, remote deployment and release packaging are separate milestones.
