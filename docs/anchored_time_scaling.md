# Anchored time scaling - 0.11.0

Stretch or compress a choreography phrase around a fixed time without changing
its poses. Scaling and shifting share pose selection, Preview/Apply/Cancel and
one global undo history. A source → destination list makes each preview explicit.

## Human-repeatable workflow

1. Select one island with authored keys. **Select poses** plus chip taps, desktop
   Shift/Ctrl/Command-click or **Select all poses** chooses keys. Layer selection
   and pose selection are distinct; timing controls explain when one island or
   captured poses are required.
2. Choose **Timing anchor**: **First selected pose**, **Last selected pose**,
   **Visible playhead** or **Custom time**. Custom **Anchor time (seconds)** is
   bounded to 0..12. The displayed selected span and resolved anchor describe
   the scope. First/last anchor refers to selected keys, not the complete track.
3. Enter **Time scale factor** within **0.1..4**: below 1 compresses the selected
   intervals; above 1 stretches them; 1 is identity. The UI uses 0.05 input steps.
4. **Preview timing scale** captures the anchor and visible authored playhead
   together. Shifted chips, artwork and a source/destination list show the
   candidate. Shared scene/history remain unchanged; anchor/transport controls
   are held. **Cancel timing scale** or Escape restores the original and returns
   focus to Preview timing scale when the preview owned focus.
5. **Apply timing scale** saves one reversible edit. Applying from playback pauses
   at the captured time in the same transaction. Cancel leaves playback running;
   direct protocol scaling preserves playback. Successful edits retain mapped
   key selection, so **Preview shift** can adjust the scaled phrase next.
6. Undo/Redo restores complete edits. Version 0.11.1 restores known timing selections; import/context changes or
   unknown structural edits clear them safely. Export/reopen JSON retains all poses,
   times and easing. Recipe schema 4 and old migrations remain compatible.

Example: selecting keys at 3s and 6s with first-pose anchor 3s and factor 0.5
moves the second to 4.5s while keeping 3s fixed. Last-pose anchor 6s moves the
first to 4.5s and keeps 6s fixed. Custom anchor 0s maps them to 1.5s and 3s;
selected source times vacate together, so the new 3s destination is available.

## Shared command and validation

The 23rd tool, `scale_keyframes`, accepts the same explicit track/key targets as
`retime_keyframes`. Read actual IDs, exact times and revision from `get_scene`:

```json
{
  "targets": [
    {"id": "island_ember", "times": [3, 6]},
    {"id": "island_lagoon", "times": [3, 6]}
  ],
  "anchor": 3,
  "factor": 0.5,
  "expected_revision": 0,
  "request_id": "unique-scale-attempt"
}
```

Replace example IDs/revision/retry key with current values. Both **anchor** and
**factor** are required, finite and bounded; no selection or wall clock is inferred.
For every selected source time `t`, the destination is
`anchor + (t - anchor) * factor`. One explicit anchor applies to all targeted
tracks. Factor 1 and keys exactly at the anchor preserve original times exactly,
including fractional coordinates. Positive factors preserve selected-key order.
This does not reverse playback or retime every island unless explicitly targeted.

Targets contain 1..16 unique existing island IDs and 1..24 unique exact existing
source times per island. The manual selector edits one track; protocol callers
can scale multiple tracks atomically. Existing blend records/static operands
have no motion track. Hidden tracks remain hidden. Base geometry, complete pose
values, easing, styles, order, layer selection and direct-protocol view/playback
remain unchanged. Scaling and shifting use one shared destination-validation
implementation in Python and its browser numeric mirror.

All selected source times vacate simultaneously. Any final time outside 0..12,
exact occupied unselected time, duplicate represented destination, missing key,
stale revision or persistence failure rejects the entire edit across all tracks.
No snapping, wrapping, clamping, rounding or partial movement occurs. Exact-time
checks match retiming; normal floating-point arithmetic applies. API callers use
exact scene times rather than rounded display labels. Atomic batches, retries
and shared undo/redo remain. Programmatic identity calls retain normal history;
manual identity/anchor-only previews skip transactions.

Crossing unselected keys changes interpolation neighbors; easing remains attached
and controls the outgoing segment. Endpoint poses are not automatically matched.
Selecting both 0s and 12s prevents stretching beyond the loop bounds; compression
can remove endpoint keys, with the existing seam hint reporting that condition.
Preview is fixed-time inspection rather than separate candidate playback.

## Combined authoring review

Actual desktop/touch acceptance combines whole-path movement and center alignment
with compression, subsequent shifting, global undo/redo and JSON reopening. A
repository-owned `benchmarks/authoring-walkthrough.mjs` separately creates raw and
annotated screenshots, an action log, trace, diagnostics and a live HTML report
for a human-repeatable 25-step journey. It owns only a disposable 8769 service,
refuses an occupied port and never attaches to port 8000. Run from the 0.11.0
feature/dev checkout with STUDIO_PYTHON pointing to the installed project Python.

Native WebMCP/model-host and natural-language execution remain unverified. The
next step is **combined authoring usability/reliability review and polish**,
including phone navigation, key-selection continuity, long sessions and reconnects,
rather than another standalone feature. Automated success does not replace a
creator's hands-on assessment or establish all-browser/device accessibility.

Version 0.11.1 completes the bounded [integrated reliability pass](authoring_reliability.md).
It defines the current navigation, selection, reconnect and save-confirmation behavior.
