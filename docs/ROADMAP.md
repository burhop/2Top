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

## Recommended 0.4.0 — editable motion paths

Show selected-island center paths and pose handles on the canvas. Allow moving
and retiming selected keys through the same revision-checked commands, with
clear seam indicators, undo/redo and JSON round trips. Test crossing/duplicate
times and phone interactions before adding more track types.

## Subsequent geometry work

Introduce a bounded subset of reusable primitives and reversible composition
(union, difference, blend) into the artwork studio. First specify how those
operations interact with tracks, immutable snapshots and persistence. Local
shoreline pinning, freeform deformation and exact continuity constraints need
their own geometry contracts and numerical acceptance cases. Physical tide
simulation, remote deployment and release packaging are separate milestones.
