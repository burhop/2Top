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

## Next independent authoring work

Version 0.9.0 completes alignment/spacing through authored-center anchors,
whole-path translations, explicit island/source selections and a preview flow.
[Center-layout contract](center_layout.md) records the bounds and limitations.

## 0.9.0 - center alignment and even spacing

Align island centers on either axis; distribute three or more with fixed outer
centers and deterministic ties. Shape/timing, schema 4 and blend references stay
intact. Desktop/touch previews freeze the displayed playhead and apply one
reversible transaction. Stale/invalid layouts reject atomically. Center placement
does not guarantee equal edge gaps or collision avoidance.

## Next independent motion-authoring work

Version 0.10.0 completes multi-keyframe retiming with transient desktop/touch key
selection, a frozen preview and one shared time shift. The 22nd tool supports
multiple explicit island tracks atomically, rejecting any occupied/out-of-range
destination. Poses/easing remain attached; selected times vacate together.
[Retiming contract](multi_key_retiming.md).

## Next independent choreography work

Scale selected key times around an explicit anchor with Preview/Apply/Cancel and
the same atomic collision/range guards. This stretches or compresses a phrase's
rhythm while preserving poses/easing, independently of external host verification.

## Most important remaining showcase gap

Exercise the guided workflow in the user's intended, already configured model
client with genuine natural-language tool choice and visible shared edits. Record
the actual client/session and manual refinement; protocol acceptance alone does
not prove that integration. Native WebMCP separately needs an available supported
top-level browser/model host. No extra geometry feature should substitute for
this connection evidence, and no new credentials, permissions or paid API usage
are implied by this roadmap.

## Subsequent geometry work

Introduce a bounded subset of reusable primitives and reversible composition
(union, difference, blend) into the artwork studio. First specify how those
operations interact with tracks, immutable snapshots and persistence. Local
shoreline pinning, freeform deformation and exact continuity constraints need
their own geometry contracts and numerical acceptance cases. Physical tide
simulation, remote deployment and release packaging are separate milestones.
