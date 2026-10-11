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

## Most important showcase gap - a real connected coauthor

The studio has shared manual/MCP edits and protocol acceptance, but the artist
has not yet been shown a verified natural-language agent session that changes
this same canvas, followed by manual refinement and shared undo. Prioritize a
short guided connection workflow and repeatable collaborative art demonstration
using the intended actual MCP client/agent. Record the client, connection and
visible shared-scene actions, avoiding new credentials or security changes.
Native WebMCP separately requires an actual supported browser/model host;
unsupported Chromium and mocked registration cannot prove that connection.

## Subsequent geometry work

Introduce a bounded subset of reusable primitives and reversible composition
(union, difference, blend) into the artwork studio. First specify how those
operations interact with tracks, immutable snapshots and persistence. Local
shoreline pinning, freeform deformation and exact continuity constraints need
their own geometry contracts and numerical acceptance cases. Physical tide
simulation, remote deployment and release packaging are separate milestones.
