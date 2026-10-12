# Arrange layers and whole motion paths — 0.8.0

Arrange a composition without moving its islands one at a time or re-authoring
their choreography. Selection uses the existing layer IDs. There is no new group
record, nesting or recipe version: schema 4 and older recipe migrations remain.

## Desktop and touch workflow

1. Select a layer, then Shift/Ctrl/⌘-click other layer rows or artwork to toggle
   membership. On touch, choose **Select multiple**, tap rows/artwork, then choose
   **Done selecting**. **Select visible** selects visible artwork, including
   blends; **Clear** deselects without deleting anything.
2. **Arrange selection** shows the layer count and distinct affected island count.
   A dashed position guide joins the selected centers. Drag any selected artwork
   layer to translate the complete group; Escape/pointer cancellation discards
   the preview. A selected blend can be dragged through its retained operands.
3. Use the four nudge buttons with **Nudge distance** in world units. A scale
   factor of **1.10** makes the selected shapes and center spacing 10% larger.
   **Group rotation** is degrees; positive angles turn clockwise on the canvas.
   Scale and rotation use the mean of the affected centers at the visible
   playhead. The UI sends that explicit pivot to the shared command.
4. One transform is one undo step. Undo/redo works across UI and client edits.
   A group drag during playback freezes/pauses the visible playhead in the same
   transaction. Button transforms and direct protocol calls preserve playback.
5. Export JSON to preserve the transformed fields/tracks/styles. Selection is
   process state and is not included in exported recipes, as before. PNG/SVG
   omit the position guide and selection handles.

**Whole paths** means every affected island's base pose and all its authored
keys transform together; key times, easing and pose counts stay unchanged.
No pose is implicitly inserted and there is no hidden rotation wrapping. This
keeps existing interpolation meaningful. Single-island dragging and **Shape &
field** retain their current-pose editing behavior. Select one layer to use its
individual appearance/shape controls; those controls are disabled for a mixed
selection rather than silently changing only the first item.

Hidden layers can be explicitly selected in the list and remain hidden. Selecting
a blend transforms its retained source islands. A source selected both directly
and through one or two blends transforms **once**. Because sources are shared,
other blends using an affected source can also change; the arrangement panel
states this dependency. Source IDs, blend records, amounts and ordering are
preserved. Transforming a blend does not introduce animated or nested operands.

## Shared command contract

The new `transform_layers` tool is available through the manual command API,
real MCP HTTP/stdio and WebMCP adapter. The current catalog contains **20 tools**.
Read `get_scene` for actual IDs and the current revision before an edit.

```json
{
  "ids": ["island_ember", "island_lagoon"],
  "dx": 10,
  "dy": -5,
  "scale": 1.1,
  "rotation": 15,
  "pivot": {"x": 500, "y": 350},
  "expected_revision": 0,
  "request_id": "arrange-unique-attempt"
}
```

Replace example IDs/revision/request ID with values for the actual scene. The
tool takes 1–18 unique explicit island/blend IDs. Defaults are dx/dy/rotation 0
and scale 1. Input scale is 0.1–4, rotation −360..360 degrees, dx −3000..3000
and dy −2100..2100. A supplied pivot must be within the existing center bounds.
If omitted or null, the deterministic pivot is the arithmetic mean of the
distinct affected **base** centers, independent of wall clock or selection order.
The UI's explicit visible-playhead pivot can therefore differ from this default.

For each base pose and key: scale center displacement about the pivot, rotate
that displacement, then translate; multiply radius by scale and add the angle
to authored rotation. Stretch, warp, phase/lobes, styles and all other fields
are unchanged. Existing procedural tide continues using its original engine
formulas; this command transforms authored poses, not a physical simulation or
the tide's internal world-oriented drift law.

Every resulting center, radius and authored rotation must satisfy the existing
pose limits (x −1000..2000, y −700..1400, radius 80..400, rotation −360..360).
An invalid base or even one invalid key rejects **the entire edit**. Values are
never clamped or wrapped. Invalid drag previews cannot partially commit. Stale
revisions clear/reconcile the preview and require a fresh read/reconsideration.
Retry IDs retain the existing exact-intent idempotency behavior. Failed validation,
reference resolution or persistence preserves disk, revision and undo/redo state.

The command can be a child of `batch`; child schemas/preconditions and final
scene validation remain authoritative. Every targeted source must exist when
the transform executes. No arbitrary geometry expressions or filesystem paths
are accepted.

## Verification and next authoring step

Tests cover complete tracks/easing, static contour affine correspondence,
Python/JavaScript math/source-resolution parity, all 18 supported layers, bounds,
retry/conflict rollback, persistence and real HTTP/stdio MCP with manual undo.
Actual desktop/phone Chromium covers selection, nudge/scale/rotate, coherent
pointer movement, cancellation, JSON export and stale/invalid rejection. The
WebMCP forwarding contract is explicitly mocked; native/model-host execution
remains a separate verification gap.

The next independent authoring step is **alignment and even spacing for selected
islands**, reusing atomic transforms after defining shared-operand and whole-path
placement rules. It does not depend on the external model-host session.
