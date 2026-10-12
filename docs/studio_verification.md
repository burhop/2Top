# Tidal Atlas development verification

Updated October 12, 2026 for version 0.7.1. Work17 executes the local application
checks below; CI verifies the exact feature commit before dev integration.

## Current milestone

Version 0.7.1 fixes reviewed final-candidate order/deletion errors, stale
same-revision restart history and blend-editor selection precedence. Process
session metadata refreshes both snapshot acceptance and activity cache. Normal
gestures/playback, 19 tools, schema 4 and geometry-engine reuse are retained.

The manual UI, real MCP HTTP/stdio and WebMCP adapter share 19 validated tools,
revisions, atomic batches, retry keys, persistence and undo/redo. Source deletion
is guarded while referenced. See [static blending](static_blending.md) for field
semantics, reference rules, sampling budgets and degenerate-case behavior.

## Local verification

- Full Python suite: **1,256 passed, 27 skipped**. The skips require unavailable
  curves.db data or opt-in visual baselines. Numeric/runtime warnings remain
  visible rather than being suppressed.
- Studio subset: 218 cases, including 15 choreography and 17 motion-edit cases for interpolation,
  endpoint/loop semantics, Python/JavaScript parity, demo reproducibility,
  malformed input, sorted unique keys, limits, replay/stale revisions, rollback,
  persistence, legacy migration and real MCP HTTP/stdio pose edits.
- JavaScript: **35 DOM/service checks and 10 real-raster/layer-policy checks passed**. This is distinct from
  native browser layout testing.
- Explicitly mocked WebMCP contract: passed, including forwarding choreography and static-composition tools. This does not establish native host support.
- Repository-wide Ruff lint and formatting: passed, **133 files formatted**.
- Actual Playwright Chromium acceptance: **23 cases passed**, with unexpected
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

Twenty new Python cases cover legacy field evaluation and full Python/JavaScript
contour parity, two components merging into one, bounds, finite grids, omitted
fragments, snapshots, migration, references/cycles, budgets, rollback, persistence,
safe source removal, the real legacy graphics bridge and an actual MCP workflow.
The two new real-browser cases cover creation, operation/amount changes, source
selection and pointer editing, undo/redo, source-preserving removal, showing
separate/merged artwork, responsive layouts, SVG export and saved JSON reopening.
The prior choreography and motion-path cases remain enabled.

Nineteen additional Python cases verify complete order, atomic rollback, style
bounds, unchanged geometry bounds/evaluation, hidden-source dependency guards,
undo/redo, disk/save migration and a real MCP ordering/style workflow. Two
additional actual desktop/phone browser cases check frontmost artwork selection,
native button/opacity keys, hidden-source pointer edits, alpha pixel values,
SVG order/group opacity and saved JSON reopening. Raster alpha checks permit one
8-bit rounding unit; this does not establish cross-browser pixel identity.

Four additional Python cases cover provenance spoofing boundaries, actual diff
summaries, no-op/replay/conflict history, cross-client undo references, bounded
history, persistence/restart and real MCP protocol calls. Two more actual browser
cases use the official MCP client alongside native manual controls, test stale
writes, escaped caller notes, truthful bridge hints, history filtering and actual
save/reopen on desktop and phone. These are scripted protocol acceptance, not a
separate model inference session. Coauthor UI screenshots were visually reviewed.

Glasswater front/behind desktop and phone screenshots were visually reviewed.
Confluence separate/merged desktop and phone screenshots were visually reviewed.
Source guides, controls and checked phone width fit their layouts. This does not
establish exact topology, distance/offset correctness, every viewport/browser or
every assistive technology. Native WebMCP host execution remains separate.

Run `npm run test:browser`. Raw screenshots, downloads, diagnostics, videos and
traces are in `test-results/browser/`; the clickable report is in
`playwright-report/`. CI uploads the same evidence for each browser run.
The milestone PR provides the exact commit and CI links.

## Reviewed reliability regressions

Twenty-four added Python cases cover geometry/blend reorder-deletion batches,
structured malformed-final-state rejection, disk/history/revision/retry-key
rollback, undo/redo, actual-record selection, persisted restart identity and
Unicode safety across direct, HTTP and real MCP boundaries. Pydantic already
rejects lone high/low surrogates; the SDK may reject them before sending. Valid
supplementary Unicode round-trips without extra sanitization.

Three added Chromium cases cover desktop/phone New pair/second-blend choices and
ordinary polling after a same-revision restart. The restart test delivers a
genuine newly initialized SceneService snapshot through a simulated HTTP route;
the actual user demo is never restarted. Active preview and playback are preserved,
Undo/Redo/activity reset, and a late retired-session snapshot is ignored. Native
supported-branch tool counts/names derive from the actual catalog; unsupported
Chromium does not establish native-host support.

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
passed before 0.4.0 started. [PR #6](https://github.com/burhop/2Top/pull/6) merged 0.4.0 at
`af00fb452d1c62eb1a297d5cdb3eb77d8ecde954`; its post-merge CI passed before
0.5.0 started on a new feature branch. [PR #7](https://github.com/burhop/2Top/pull/7)
merged 0.5.0 at `4a07def243bcbeedbc19eb4832696d6875a0fde0`, whose post-merge CI
passed before 0.6.0 started. [PR #8](https://github.com/burhop/2Top/pull/8)
merged 0.6.0 at `87c24032573a5e2fe0da17724d6fc34b63ff117e`, whose post-merge CI
passed before 0.7.0 started. [PR #9](https://github.com/burhop/2Top/pull/9)
merged 0.7.0 at `bd8a0269991c72171af81ed77f2cb5849fd82ca8`, whose post-merge CI
passed before 0.7.1 started. Existing
history and unrelated work are preserved. Main, releases, deployment and
security/credential settings are outside these development updates.

The studio does not yet expose every historical primitive or composition command.
Exact continuity, physical simulation and native model-host interoperability are
not claimed. This milestone continues development rather than completing 2Top.
