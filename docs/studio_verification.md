# Tidal Atlas development verification

Updated October 11, 2026 for version 0.5.0. Work17 executes the local application
checks below; CI verifies the exact feature commit before dev integration.

## Current milestone

Version 0.5.0 adds non-destructive static island union/smooth union, live source
editing, bounded cached contour previews, source guides and the Confluence study
demo. It reuses RFunctionCurve/CurveField plus the existing SceneManager/graphics
backend. Source geometry is retained and nested/animated operands are rejected.
Schema 3 migrates older recipes with empty blends and preserves existing tracks.

The manual UI, real MCP HTTP/stdio and WebMCP adapter share 18 validated tools,
revisions, atomic batches, retry keys, persistence and undo/redo. Source deletion
is guarded while referenced. See [static blending](static_blending.md) for field
semantics, reference rules, sampling budgets and degenerate-case behavior.

## Local verification

- Full Python suite: **1,209 passed, 27 skipped**. The skips require unavailable
  curves.db data or opt-in visual baselines. Numeric/runtime warnings remain
  visible rather than being suppressed.
- Studio subset: 171 cases, including 15 choreography and 17 motion-edit cases for interpolation,
  endpoint/loop semantics, Python/JavaScript parity, demo reproducibility,
  malformed input, sorted unique keys, limits, replay/stale revisions, rollback,
  persistence, legacy migration and real MCP HTTP/stdio pose edits.
- JavaScript DOM/service behavior: **35 checks passed**. This is distinct from
  native browser layout testing.
- Explicitly mocked WebMCP contract: passed, including forwarding choreography and static-composition tools. This does not establish native host support.
- Repository-wide Ruff lint and formatting: passed, **129 files formatted**.
- Actual Playwright Chromium acceptance: **16 cases passed**, with unexpected
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

Confluence separate/merged desktop and phone screenshots were visually reviewed.
Source guides, controls and checked phone width fit their layouts. This does not
establish exact topology, distance/offset correctness, every viewport/browser or
every assistive technology. Native WebMCP host execution remains separate.

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
passed before 0.4.0 started. [PR #6](https://github.com/burhop/2Top/pull/6) merged 0.4.0 at
`af00fb452d1c62eb1a297d5cdb3eb77d8ecde954`; its post-merge CI passed before
0.5.0 started on a new feature branch. Existing
history and unrelated work are preserved. Main, releases, deployment and
security/credential settings are outside these development updates.

The studio does not yet expose every historical primitive or composition command.
Exact continuity, physical simulation and native model-host interoperability are
not claimed. This milestone continues development rather than completing 2Top.
