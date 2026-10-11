# Changelog

## 0.3.0 - 2026-10-11 (development)

- Author up to 24 complete poses per island for position, scale, stretch, rotation and curl; interpolate deterministically with linear or smooth easing.
- Capture, select, replace and delete pose keys; keyed drags/sliders freeze the playhead and commit one reversible action. Duplicate preserves and offsets choreography.
- Share validated `set_keyframe`/`delete_keyframe` commands across manual UI, real MCP HTTP/stdio and the browser adapter; retain revision checks, atomic batches, persistence and undo/redo.
- Add the Orbit & bloom creative demo and version-2 JSON interchange; migrate existing schema-1 recipes without changing base parameters or adding motion tracks.
- Add interpolation/parity, malformed-input, persistence, MCP and real-browser regression coverage. Native WebMCP host verification remains pending.

## 0.2.1 — 2026-10-11 (development)

- Keep the canvas and recipe workspace within their responsive column; fix the 29-pixel horizontal overflow reproduced at a 390-pixel phone viewport.
- Scope the invalid-JSON browser assertion to the error notification instead of matching unrelated range-control outputs.
- Reopen the actual downloaded JSON recipe after a new edit and verify the restored scene survives page reload.
- Pass all nine real Chromium acceptance cases locally; inspect desktop, phone and tablet screenshots and retain layout diagnostics in the browser report.
- Keep native WebMCP host interoperability separate: the tested Chromium build lacks document.modelContext and correctly retains the manual editor and MCP connection instructions.

## 0.2.0 — 2026-10-11 (development)

- Add Tidal Atlas, a canvas-first kinetic-art studio with editable contour islands, palettes, presets, animation, selection, undo/redo and JSON/SVG/PNG interchange.
- Add one typed, bounded scene service shared by manual UI, MCP and browser WebMCP, including atomic batches, optimistic revisions, replay keys and durable local recipes.
- Add official MCP 2.3.0 HTTP/stdio transports and feature-detected document.modelContext integration.
- Add reusable kinetic fields/curves with existing geometry, SceneManager and graphics-backend interoperability.
- Add protocol, geometry and DOM regression coverage plus nine real Chromium acceptance tests in CI.
- Install studio extras in the inherited CI so the new tests can be collected; retain repository-wide lint and formatting gates, with a separate mechanical cleanup of ten inherited Markdown examples.
- Target dev for integration; preserve its performance commits and keep main unchanged.
- Acceptance gap at the original handoff: Chromium had not run and publication was blocked. The recovery branch and PR #4 are now published; 0.2.1 addresses the browser failures. Native WebMCP/model-host interoperability remains a separate host-specific check.

## 0.1.0 — existing baseline

- Reusable implicit geometry engine, scene management, graphics extraction and diagnostic UI.
