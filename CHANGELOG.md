# Changelog

## 0.5.0 - 2026-10-11 (development)

- Add non-destructive two-source static union/smooth union using the existing RFunctionCurve/CurveField engine. Blend amount is dimensionless; no signed-distance or Euclidean-offset claim.
- Add a bounded deterministic contour sampler and matching browser evaluation/contours, cached committed previews and coarser gesture previews. Handle multiple components and omit open/degenerate fragments explicitly.
- Add source selectors, amount/operation controls, source guides and the Confluence study artistic demo; live base-shape edits update the result, and removing a blend retains its sources.
- Add shared create_blend/update_blend/delete_blend commands with revisions, atomic batches, persistence and undo/redo. Reject animated/nested/cyclic operands and unsafe source deletion.
- Export schema 3; migrate schema 1/2 with empty blends and preserve existing geometry/tracks. Keep legacy algorithms and older authored sample files intact.
- Add field/contour parity, geometry bridge, input/budget/migration, real MCP-client and actual desktop/phone browser workflows. Native WebMCP remains unverified.

## 0.4.0 - 2026-10-11 (development)

- Display the selected island's authored center path with labeled pose handles; drag one position without replacing its other shape values or easing.
- Retime a selected key across neighbors with sorted tracks; reject occupied times and out-of-range values without committing. Show matched/jumping/missing loop endpoints.
- Expose the same position/retiming operation as validated `edit_keyframe` through UI, MCP HTTP/stdio and the WebMCP adapter; preserve batches, revisions, retries, persistence and undo/redo.
- Retain schema 2 for unchanged 0.3.x recipe compatibility and the existing 0.2.x migration. Keep legacy geometry and authored sample files intact.
- Add edge-case, interpolation/parity, real MCP-client and desktop/phone pointer workflow coverage; document current-dev startup on Work17. Native WebMCP host execution remains unverified.

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
