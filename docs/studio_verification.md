# Tidal Atlas development verification

Updated October 11, 2026 for version 0.4.0. Work17 executes the local application
checks below; CI verifies the exact feature commit before dev integration.

## Current milestone

Version 0.4.0 adds labeled selected-island motion paths, direct positional-key
handles, collision-safe retiming and loop seam indicators. Schema 2 is unchanged.

Island choreography adds up to 24 complete six-parameter poses per object,
deterministic linear/smooth interpolation, a frozen playhead for direct edits,
key selection/removal, track-aware duplication, shared undo/redo and schema-2
JSON persistence. Orbit & bloom demonstrates three independently authored loops.
Schema-1 recipes migrate with empty tracks and unchanged base parameters.

The manual UI, real MCP HTTP/stdio transports and feature-detected WebMCP adapter
use the same 15 validated tools and authoritative service. Revisions, atomic
batches, retry keys, bounded input and immutable legacy-engine snapshots remain
shared. The legacy geometry algorithms and existing 0.2.x example are preserved.

## Local verification

- Full Python suite: **1,189 passed, 27 skipped**. The skips require unavailable
  curves.db data or opt-in visual baselines. Numeric/runtime warnings remain
  visible rather than being suppressed.
- Studio subset: 151 cases, including 15 choreography and 17 motion-edit cases for interpolation,
  endpoint/loop semantics, Python/JavaScript parity, demo reproducibility,
  malformed input, sorted unique keys, limits, replay/stale revisions, rollback,
  persistence, legacy migration and real MCP HTTP/stdio pose edits.
- JavaScript DOM/service behavior: **35 checks passed**. This is distinct from
  native browser layout testing.
- Explicitly mocked WebMCP contract: passed, including forwarding the two new
  keyframe tools and existing-key editing. This does not establish native host support.
- Repository-wide Ruff lint and formatting: passed, **127 files formatted**.
- Actual Playwright Chromium acceptance: **14 cases passed**, with unexpected
  console, page and HTTP failures rejected.

The three new real-browser cases exercise native capture/scrub/easing controls,
interpolated poses, keyed pointer movement, undo/redo, actual downloaded JSON
reopening and reload, malformed-track rejection, schema-1 import, demo playback,
track-aware duplication and a 390-pixel phone layout. The existing nine cases
retain selection, cancellation, pending-request behavior, presets, responsive
layout and actual JSON/SVG/PNG export coverage.

Two additional desktop/phone browser cases use actual canvas pointer handles,
cross-neighbor retiming, collisions, range controls, undo/redo, cancellation,
coincident 0s/12s endpoints, seam indicators and saved JSON reopening/reload.
The real MCP workflow loads authored tracks, edits position/time, observes the
same state through MCP and HTTP, retries safely, rejects a collision and sees a
manual undo. Motion-edit unit tests cover disk persistence and Python/JS parity.

The Orbit & bloom motion-path desktop and phone screenshots were
visually reviewed. The compositions visibly change and controls fit their
columns; checked phone scroll width does not exceed its viewport. This does not
establish usability at every viewport, browser engine or assistive technology.

Run `npm run test:browser`. Raw screenshots, downloads, diagnostics, videos and
traces are in `test-results/browser/`; the clickable report is in
`playwright-report/`. CI uploads the same evidence for each browser run.
The milestone PR provides the exact commit and CI links.

## Native WebMCP limitation

Actual Work17 Chromium lacks `document.modelContext.registerTool` and correctly
reports unsupported with zero registered tools. Manual editing remains available.
No fake interface or model host is injected into real browser acceptance.
Mocked registration and real MCP clients test separate adapter/transport behavior;
neither proves native WebMCP execution or a live AI session. Validate that in the
intended supported top-level host as the [roadmap](ROADMAP.md) describes.

## Recovery and integration history

The six prepared 0.2.0 commits were restored unchanged from the size/hash-verified
downloaded bundle into an isolated Work17 checkout. Base:
`8d5eccdb86c128732d0216377a8bde708f19e026`; recovered head:
`460f6e6a367b68c561828b2d2d6238dfe98b7793`.

[PR #4](https://github.com/burhop/2Top/pull/4) integrated the tested 0.2.1 browser
fixes into dev at `260d853eac5070fe9d36c20b7d98dd7f39591f67`. Version 0.3.0
started from that dev head. [PR #5](https://github.com/burhop/2Top/pull/5) merged
0.3.0 at dev `21584c0ff85a7a9b838ff7e975c0ab9bd9b21e59`, whose post-merge CI
passed before 0.4.0 started. This milestone uses a new feature branch. Existing
history and unrelated work are preserved. Main, releases, deployment and
security/credential settings are outside these development updates.

The studio does not yet expose every historical primitive or composition command.
Exact continuity, physical simulation and native model-host interoperability are
not claimed. This milestone continues development rather than completing 2Top.
