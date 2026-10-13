# Center alignment and even spacing — 0.9.0

Select island rows using desktop additive shortcuts or touch **Select multiple**.
**Center layout** previews placement before one reversible commit, translating
complete authored paths without changing shape or timing.

## Human-repeatable workflow

1. Select at least two islands. Blend records are excluded; select their retained
   island rows instead. Hidden islands stay hidden. Spacing needs at least three.
2. **Align vertical** uses mean center x; **Align horizontal** uses mean center y.
   Anchors are authored centers at the visible playhead.
3. **Space horizontally/vertically** sorts the chosen coordinate and places
   intermediate centers at equal intervals. The outer centers stay fixed and
   the other axis is unchanged.
4. Inspect **Preview** at the frozen, displayed time. Authoritative scene data and
   history are unchanged until **Apply layout**. **Cancel preview** or Escape
   keeps the original. An exact no-op shows a message without a UI transaction.
5. Apply, then Undo/Redo. Active playback pauses at the preview time in the same
   UI transaction; direct protocol layout preserves playback. Save JSON to retain
   the result. Schema 4 and older recipe migrations remain.

Each island receives one translation applied to its base and **all** authored
keys. Timing, easing, pose counts, rotations, radii, other shape fields, styles,
selection and order remain. No keys or group records are created. Existing
interpolation and procedural tide formulas stay unchanged.

Retained sources keep their IDs and blend references. Their dependent blends can
change shape, including unselected blends; the existing dependency note explains
this. Layout does not remove/clone dependencies or introduce animated/nested
operands. Whole-layer transforms still support blend-record selections.

This is **center spacing**, not equal shore gaps, bounding-box alignment or
collision avoidance. Different radii, tracks and tide can overlap. Alignment
holds at the chosen authored time; moving islands can diverge later. Data limits
remain authoritative; no exact topology or physical behavior is promised.

## Shared command and deterministic anchors

`layout_islands` is the 21st validated tool, available through UI/HTTP, real MCP
HTTP/stdio and the WebMCP adapter. Read actual IDs/revision from `get_scene`.

```json
{
  "ids": ["island_ember", "island_lagoon", "island_moon"],
  "mode": "space_x",
  "time": 4.5,
  "expected_revision": 0,
  "request_id": "layout-unique-attempt"
}
```

Replace example IDs/revision/request ID with actual scene values. The command
takes 2–16 unique existing **island** IDs and mode `align_x`, `align_y`, `space_x`
or `space_y`; spacing requires three or more. Time is finite within 0..12 and
defaults to **0**, independent of wall clock or selection order. The UI supplies
its captured time explicitly. Anchors use authored pose sampling, excluding
procedural tide drift and sampled shore bounds.

Alignment sums in stable ASCII ID order. Spacing sorts by coordinate with ASCII
ID tie-breaks, making endpoint ownership deterministic. Coincident centers
preserve exact values, including fractional coordinates. Each mode changes one
axis and preserves the other.

Existing whole-path translations validate every resulting base/key center before
persistence. One out-of-bounds key rejects **the entire layout**. No clamping,
partial movement or automatic retry occurs. Stale previews reconcile after a
revision conflict. Failed validation, reference resolution or persistence
preserves disk, revision, history and retry keys. Atomic `batch` children retain
normal schemas/preconditions and final scene validation.

Programmatic no-op layouts retain normal transaction behavior: successful calls
increment revision/history while changes contain empty update lists. Manual
preview detects an exact no-op and skips that transaction.

## Verification and next independent step

Tests cover all modes, fixed endpoints, complete tracks at explicit times,
hidden/source selections, rejected blend IDs, min/max counts, duplicates, ties,
reverse ordering, coincident/fractional centers, bounds, persistence/rollback,
replays/conflicts, Python/JavaScript parity and real HTTP/stdio MCP. Actual
desktop/phone Chromium covers preview/cancel/apply, undo/redo, exports, retained
sources, frozen playback and a real client edit conflicting with a held preview.
WebMCP forwarding remains explicitly mocked; native hosting is unverified.

Version 0.10.0 completes [multi-keyframe retiming](multi_key_retiming.md), previewing
a shared time shift with atomic collision/end-time rejection. Version 0.11.0 adds
[anchored timing](anchored_time_scaling.md). Next is combined authoring review and
polish, independent of external host verification.
