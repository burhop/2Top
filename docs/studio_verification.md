# Tidal Atlas development verification

Updated October 11, 2026 for version 0.2.1. Real browser acceptance has now executed on Work17. Native WebMCP/model-host interoperability remains a separate host-specific check.

## Implemented

- Canvas-first kinetic islands with named layers, direct movement, shape controls, palettes, three compositions and deterministic 12-second animation.
- Selection, timeline, undo/redo, JSON save/reopen and real SVG/PNG export.
- One authoritative command service with bounded schemas, stable IDs, revisions, atomic batches, retry keys and atomic file persistence.
- Official MCP 2.3.0 HTTP server and stdio adapter sharing the running studio.
- Feature-detected top-level document.modelContext tools; unsupported browsers retain the manual editor. Registration does not imply an AI connection.
- Reusable NumPy geometry and a parity-tested JavaScript mirror, with BaseField/ImplicitCurve, SceneManager and graphics-backend interoperability.

The tools edit kinetic island recipes. The UI does not expose the entire historical geometry library. No embedded model, arbitrary expression evaluation, physical simulation or exact G1/G2 construction is claimed.

## Real Chromium acceptance

All nine Playwright Chromium cases passed locally against an ephemeral loopback service. They exercise real canvas rendering, keyboard selection, duplicate/remove/undo, pointer drag and Escape cancellation, native range preview/commit with undo/redo, controls during a delayed real request, presets/palettes/playback, invalid import recovery and responsive layouts.

The interchange case uses a native file chooser, validates real JSON/SVG/PNG downloads, changes the scene, reopens the actual downloaded JSON and checks restored objects after page reload. PNG signature and 2000x1400 dimensions, SVG paths and titles, and shared-service state are asserted. Uncaught JavaScript, unexpected HTTP and browser console errors fail the suite.

The published 0.2.0 head passed Python/shared-scene CI but failed two Chromium cases: an ambiguous status locator and 29 pixels of horizontal canvas overflow at a 390-pixel viewport. Version 0.2.1 targets the notification precisely and gives the canvas/recipe workspace an explicit container width, preventing minimum-height/aspect-ratio sizing from enlarging it horizontally.

Desktop (1440x1100), phone (390x844) and tablet (820x1180) screenshots were visually inspected after the fix. The phone canvas fits its column and controls/footer remain visible; no unintended clipping or horizontal overflow was observed at these checked sizes. This does not establish usability at every viewport, assistive technology or browser engine.

Run `npm run test:browser`. Screenshots, downloads, videos, traces, layout diagnostics and the HTML report are saved in `test-results/browser/` and `playwright-report/`; CI uploads the same evidence. See [PR #4](https://github.com/burhop/2Top/pull/4) for the final exact commit and current CI results.

## Other required gates and historical evidence

Required development checks are the full `tests/` Python suite, JavaScript DOM/service checks, the explicitly mocked WebMCP contract check, repository-wide Ruff lint/formatting and real Chromium acceptance. Existing CI gates remain enabled. Dev integration requires passing local application checks and required CI for the final head; main remains unchanged.

The 0.2.0 handoff reported 1,157 Python tests passed, 27 skipped for unavailable curves.db data or opt-in visual baselines, and 41 inherited numeric/runtime warnings. These historical results do not substitute for checks on the current commit. The 119 studio tests cover geometry parity/legacy interoperability, persistence, rollback, concurrent/stale edits, retry keys, invalid data and real MCP HTTP/stdio clients. Earlier DOM/native-render counts and the mocked adapter check are distinct from real browser acceptance.

The handoff also checked a built wheel outside the source checkout. Its artwork PNG/GIF were canvas renders rather than browser screenshots; current Playwright screenshots provide separate real-browser evidence.

## Native WebMCP limitation

Actual local Chromium reports `nativeRegisterToolAvailable: false`, `supported: false`, `registered: 0` and `reason: browser-unsupported`. The page retains manual editing and MCP connection instructions. No modelContext interface or AI/model host was injected into browser tests.

The separate mocked contract check validates adapter behavior only. Neither it nor the real browser's unsupported path proves native WebMCP tool execution, model-host interoperability or a live AI session. Validate those separately in the intended supported top-level host. Real MCP HTTP/stdio clients remain a separate protocol check.

## Repository handling

The six prepared 0.2.0 commits were restored unchanged from a size/hash-verified downloaded bundle into an isolated Work17 checkout. Base: dev `8d5eccdb86c128732d0216377a8bde708f19e026`; recovered head: `460f6e6a367b68c561828b2d2d6238dfe98b7793`. Recovery publication and draft PR #4 preserved existing dev performance history, main/dev heads and unrelated work, without force pushing.

Version 0.2.1 adds bounded browser/layout fixes and synchronized package/API/README/changelog metadata. Local environments and browser artifacts remain untracked. No deployment, release, security-setting change or credential inspection is part of this development update.
