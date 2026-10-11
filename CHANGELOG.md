# Changelog

## 0.2.0 — 2026-10-11 (development)

- Add Tidal Atlas, a canvas-first kinetic-art studio with editable contour islands, palettes, presets, animation, selection, undo/redo and JSON/SVG/PNG interchange.
- Add one typed, bounded scene service shared by manual UI, MCP and browser WebMCP, including atomic batches, optimistic revisions, replay keys and durable local recipes.
- Add official MCP 2.3.0 HTTP/stdio transports and feature-detected document.modelContext integration.
- Add reusable kinetic fields/curves with existing geometry, SceneManager and graphics-backend interoperability.
- Add protocol, geometry and DOM regression coverage plus nine real Chromium acceptance tests in CI.
- Install studio extras in the inherited CI so the new tests can be collected; retain repository-wide lint and formatting gates, with a separate mechanical cleanup of ten inherited Markdown examples.
- Target dev for integration; preserve its performance commits and keep main unchanged.
- Known acceptance gap: actual Chromium CI and native WebMCP/model-host interoperability have not yet run. Local browser access was restricted; publication currently needs a writable GitHub connection.

## 0.1.0 — existing baseline

- Reusable implicit geometry engine, scene management, graphics extraction and diagnostic UI.
