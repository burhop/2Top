# Tidal Atlas first-version review

Verified October 11, 2026. This is a locally runnable first implementation, with a remaining native-browser acceptance gate.

## Implemented

- Canvas-first kinetic island artwork with named layers, direct movement, shape controls, palettes, three compositions and deterministic 12-second animation.
- Selection, timeline, undo/redo, JSON save/reopen, and real SVG/PNG export.
- One authoritative scene/command service: strict schemas, bounded inputs, stable IDs, monotonic revisions, atomic batches, retry keys, structured failures and atomic file persistence.
- Official MCP SDK 2.3.0 server over Streamable HTTP, plus a stdio adapter that attaches to the same running studio.
- Feature-detected top-level browser WebMCP using document.modelContext. Unsupported browsers retain the manual editor. Registration does not imply an AI connection.
- Reusable NumPy numeric geometry with a parity-tested JavaScript mirror, plus real BaseField/ImplicitCurve adapters, existing SceneManager save/load and GraphicsBackendInterface paths/grids.

The tools currently edit kinetic island recipes. The UI does not expose the entire historical geometry library. No embedded model, arbitrary expression evaluation, freeform shoreline pinning, physical simulation or exact G1/G2 construction is claimed.

## Checks run

The full repository `tests/` suite ran in a freshly installed environment using the updated uv lockfile, Python 3.12.14:

- 1,157 passed
- 27 skipped because the legacy curves.db dataset or opt-in visual baseline configuration was unavailable
- 41 legacy numeric/runtime warnings

The studio portion contains 119 tests. Coverage includes field/contour parity, scaled gradients, geometric roundtrip, old-interface composition, scene persistence, atomic rollback, failed disk writes, concurrent edits, stale revisions, exact request replay, invalid data and real MCP clients. Current protocol 2026-07-28 negotiated over both HTTP and stdio; legacy 2025-11-25 was also checked in-process.

36 JavaScript DOM/service/native-render checks passed against the real Python SceneService. They cover direct drag and Escape cancellation, preview/commit sliders, pending-command races, stale-write recovery, extreme valid inspector values, duplication at bounds, recipe import, export content, and actual 2000×1400 PNG encoding. The browser API contract test passed using an explicitly mocked WebMCP implementation.

Repository-wide Ruff lint and formatting both pass. A separate mechanical-formatting commit fixes ten inherited Markdown code-example files, with no production Python changes. The existing remote CI has not been rerun because no changes were pushed. The inherited workflow now installs the studio test dependencies; its repository-wide lint and formatting gates remain required. A new independent studio workflow runs scoped lint/format checks, the full test suite, WebMCP contract tests, DOM behavior tests and nine actual Chromium acceptance cases with downloadable screenshots/traces. Those Chromium cases were discovered successfully but have not yet executed.

A wheel was built and extracted outside the source checkout. Its imports, static UI assets and engine-backed /api/geometry endpoint passed an installation smoke test. The packaging now includes required visual_tests subpackages used by the existing graphics backend.

## Remaining acceptance gate

Actual browser layout, real pointer/accessibility behavior, browser download prompts, rendering performance and native WebMCP/model-host interoperability have not been verified. The build environment's cloud browser rejected loopback navigation with ERR_BLOCKED_BY_CLIENT, and standalone Chromium could not open required Unix sockets. No tunnel, public deployment or security bypass was used.

The accompanying PNG and 12-second GIF use the app's real canvas drawing code. They are artwork renders, not screenshots of a verified browser UI and not evidence of a live AI session.

Before treating this as release-ready, run `python -m studio.app` in an authorized local environment and test the browser UI and intended MCP/WebMCP host. Instructions are in the main README and docs/tidal_atlas.md.

## Repository handling

The initial review used main commit 21e9b37df4e4cb72d16306b0be782ed190e8ae57. Per the subsequent development instruction, the feature commits were rebased onto dev commit 8d5eccdb86c128732d0216377a8bde708f19e026 for version 0.2.0. Existing dev performance work and branch history are retained; main-only merge commits are not imported. The new studio creates detached immutable geometry snapshots, so its renderer does not reuse stale parameter-dependent legacy caches.

Local versioned feature commits exist. Publication is currently blocked: shell Git has no credentials and the connected integration returned HTTP403 Resource not accessible by integration when creating the feature ref. No remote branch or PR was created. No merge, deployment, or remote setting change occurred. A nine-case real Chromium suite and artifact-producing GitHub Actions job are ready, but cannot run remotely until publication is available.
