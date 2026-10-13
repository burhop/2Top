# Multi-keyframe retiming - 0.10.0

Shift a choreography phrase earlier or later while keeping its poses and easing
attached to the selected keys. Preview the new timing before one reversible edit.

## Manual workflow

1. Select one island with authored keys. Choose **Select poses** and tap key chips;
   desktop Shift/Ctrl/Command-click also enters selection mode. **Select all poses**
   chooses the whole track; **Clear poses** empties it. Selection itself writes no
   scene transaction. **Done selecting poses** returns chips to playhead browsing.
2. Enter **Time shift (seconds)**, positive for later or negative for earlier,
   in 0.01-second input steps. Choose **Preview shift**.
3. Shifted chips and the artwork show the candidate at the frozen visible
   playhead. Shared scene data/history stay unchanged. Playback and scrub controls
   are held during preview. **Cancel shift** or Escape restores the original;
   playback continues if it was running. A zero UI shift skips the transaction.
4. **Apply shift** saves one shared undoable edit. A playing UI session pauses at
   its captured time in that same transaction. A paused session keeps its playhead.
   Successful shifts retain the translated key selection. Undo/Redo restore the
   whole track and reset transient key selection when the track changes.
5. Export JSON to retain the result. Schema 4 and existing recipe migrations remain.

Key selection is local to the editor and one selected island, not a new scene
field. Switching island/document/session or observing a changed track clears it.
Hidden tracks can be selected in the layer list and stay hidden. Blend records
and static blend operands have no motion track to retime.

Selected keys vacate their source times simultaneously. A selected key can move
onto another selected key's old time when that key moves away. Keys can cross
unselected keys if every final destination is free; unselected keys stay fixed.
Their new neighbors can change interpolation. Easing stays attached to its key
and still controls the outgoing segment. Relative selected timing is translated
by the same delta; this is not time scaling or curve/geometry editing.

All destinations must remain within **0..12 seconds**. One out-of-range or occupied
destination rejects the entire operation, including other selected tracks. No
wrapping, clamping, rounding or partial movement occurs. Endpoint poses are not
automatically rematched for a seamless loop; the existing seam indicator remains.
Preview at the fixed playhead is not a second playback session.

## Shared command

`retime_keyframes` is the 22nd validated tool in UI/HTTP, real MCP HTTP/stdio and
the WebMCP adapter. Read actual IDs, exact key times and revision from `get_scene`:

```json
{
  "targets": [
    {"id": "island_ember", "times": [3, 6]},
    {"id": "island_lagoon", "times": [3]}
  ],
  "delta": 1.5,
  "expected_revision": 0,
  "request_id": "unique-retime-attempt"
}
```

Replace example IDs/revision/retry key with actual scene values. Targets contain
**1..16 unique existing island IDs**, each with **1..24 unique exact existing
source times**. Delta is required, finite within -12..12. No selected layer or wall
clock is inferred. Protocol callers can shift multiple tracks together; the
manual selector edits one island's track. Atomic `batch` supports the same child.

Collision checks use exact stored numeric times, consistent with `edit_keyframe`.
Normal floating-point arithmetic applies; near-equal times are not snapped and
source times should come from scene data rather than rounded display labels.
If distinct source times collapse to the same represented destination, reject
the operation. Missing keys/IDs return `keyframe_not_found`/`object_not_found`;
bounds return `keyframe_range`; occupied destinations return `keyframe_collision`.
Malformed models return `validation_error`. Revision and retry/persistence rules
remain shared; a stale preview reconciles rather than overwriting a client edit.

Each shifted key preserves all six pose values and its easing. Base geometry,
styles, layer order, layer selection, view and direct-protocol playback remain
unchanged. Successful protocol delta=0 calls retain normal revision/history
behavior. The UI previews use the same numeric policy as the Python service.

## Verification and next independent step

Tests cover simultaneous movement, multi-track atomicity, endpoints, occupied
times, crossing keys, maximum 16 tracks/24 keys, malformed targets, missing keys,
persistence failures, retries/conflicts, batches and shared undo/redo. Actual
desktop/touch Chromium checks selection, preview/cancel/Apply, held playback,
JSON export, bounds and a real MCP change conflicting with a held preview. Official
HTTP/stdio clients and Python/JavaScript parity are exercised. WebMCP forwarding
is explicitly mocked; native host and natural-language execution remain unverified.

Next high-value independent step: **scale selected key times around an explicit
anchor**, with a preview and the same atomic collision/range guards, to stretch
or compress a choreography phrase while keeping its poses/easing.
