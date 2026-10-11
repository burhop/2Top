# Tidal Atlas: first studio slice

## What this version does

The new studio turns bounded, declarative implicit island fields into layered topographic artwork. Each island has a stable ID and an editable center, radius, stretch, rotation, lobe count, curl amount and phase. A deterministic 12-second motion recipe makes the fields breathe and drift. The underlying NumPy field and contour generator can be used without the editor.

The browser canvas renders the same recipe with a JavaScript mirror. Python/Node parity tests compare numerical outputs, including complete initial-scene recipes. Animation is art-directed, not a fluid or physical simulation. The field is dimensionless; it is not a Euclidean signed distance. Sampled contour polylines do not carry exact G1/G2 or manufacturing guarantees.

## Run locally

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -e ".[studio]"
python -m studio.app
```

Open http://127.0.0.1:8000. Alternatively, a reproducible uv install is `uv sync --locked --extra studio`, followed by `uv run --extra studio python -m studio.app`.

The service binds only to `127.0.0.1`. It is a local single-user prototype. It does not implement authentication, multi-tenant isolation, or remote deployment. Do not publish or reverse-proxy it onto the public internet. The legacy Flask diagnostic UI remains a separate application and is not mounted by the new server.

By default, validated edits are atomically written to `.studio/scene.json`. `--scene PATH` chooses a local file at startup; no agent tool can choose filesystem paths. `--ephemeral` disables disk persistence. The latest recipe and revision survive restart; selection, undo/redo history, action log and replay keys are process-local. Only one studio process should own a scene file.

## Manual walkthrough

1. Open the default two-island composition with a small golden satellite.
2. Select an island in the layer list or on the canvas. Drag the center or shore to move the whole island. Press Escape before releasing to discard the preview.
3. Change Scale, Organic detail, Rotation or Contour density. Slider movement previews locally; releasing commits one revision-checked action.
4. Play the tide, pause it, scrub the 12-second timeline, or change playback speed.
5. Switch among Midnight archipelago, Coral atoll and Tidal ribbons. Preset loading is one undoable transaction.
6. Add, duplicate, hide, remove, undo or redo. The last complete manual or agent transaction is the one that Undo reverses.
7. Export the current frame as PNG/SVG, or export the numeric recipe as JSON. Exports omit selection handles. The Recipe view exposes the editable document data.

Freeform shoreline deformation, local peninsula pinning, Boolean merging of these island layers, typography import, physical tide simulation and automatic language-model prompting are outside this first slice. The current direct edit moves a whole island. The existing broader geometry library remains available for future tools and other use cases.

## Co-edit with an agent

See [agent_protocols.md](agent_protocols.md) for exact client setup, tested protocol versions, tool schemas, error handling and WebMCP support caveats. Standard MCP and browser WebMCP both modify the same service as the mouse UI. An external model/client must be connected; the app makes no model API calls by itself.

Suggested host prompt:

> Read the Tidal Atlas scene and current selection. Keep the selected island's center where I placed it. Increase its warp slightly, give it a warmer palette, and add a small nearby golden island. Apply the change as one reversible batch against the revision you just read.

Tools require bounded numeric parameters and an explicit expected revision. Stale writes return a conflict without committing. A failed batch leaves every object unchanged. Repeating an identical request ID within the same process returns the original transaction ID without applying the edit twice. Reusing an ID for a different command is rejected.

Playhead sampling is shared by the server's monotonic clock while running. Browser playback extrapolates smoothly from that sampled phase; pause/scrub operations commit their chosen time through the same command API.

## Architecture and boundaries

- `geometry/kinetic.py`: reusable numeric field, contour sampler, recipe normalization
- `studio/service.py`: authoritative schema, state, transactions, history, persistence
- `studio/app.py`: loopback HTTP UI/API and mounted standard MCP endpoint
- `studio/mcp_server.py`: official SDK server; stdio proxy attaches to the running HTTP service
- `studio/static/geometry.js`: tested numeric mirror for low-latency canvas rendering
- `studio/static/app.js`: manual preview/commit interactions and canvas drawing
- `studio/static/webmcp.js`: feature-detected top-level browser tool registration

The service rejects extra fields, invalid IDs/references, non-finite values and over-budget scenes. Limits include 16 islands, 32 commands per batch, 64 displayed contours and a 512 KB request body. The standalone geometry sampler has its own finite grid/contour budgets. There are no executable expression or arbitrary file tools.

The base branch is main at `21e9b37df4e4cb72d16306b0be782ed190e8ae57`. Dev is three commits ahead and five behind. Its performance patch was reviewed, not blindly merged: bounds/resolution-only curve caching and classification caching lack reliable parameter-revision invalidation. This first slice avoids those stale-cache risks, uses a fast vectorized field, and leaves unrelated legacy behavior unchanged.

## Verification and known gap

Run `python -m pytest tests/studio`, `node tests/studio/webmcp_contract.mjs`, and the scoped Ruff commands in the README. New tests cover recipe/field parity, finite bounds, transactions, persistence failure, concurrent writes, stale revisions, duplicate retries, atomic rollback and real standard MCP clients.

The browser WebMCP contract test uses an explicitly mocked browser API. It does not prove native browser-agent interoperability. The exact end-to-end desktop model/host configuration still needs verification.

DOM interaction tests run the actual application JavaScript against the real Python scene service, with mocked DOM layout and canvas behavior. Optional native canvas rendering uses the same drawing code and creates an artwork preview, not a browser screenshot. Run `npm ci` then `npm run test:ui` with Node 24.15+; use `STUDIO_RENDER_PREVIEW=1` to also render the preview.

Actual cloud-browser UI verification was blocked in the build environment: loopback navigation returned `ERR_BLOCKED_BY_CLIENT`, and standalone Chromium could not create Unix sockets. No tunnel or public deployment was used to bypass the restriction. DOM/canvas tests and artwork renders are useful but do not replace browser layout/accessibility/performance verification. Before calling the UI release-ready, run it in an authorized local browser and check layout, pointer behavior, export downloads, repeated/interrupted gestures, and the intended WebMCP host.

A ready-to-open numeric recipe is included at `examples/tidal_atlas_recipe.json`. In the studio, choose Recipe → Load JSON. File selection cancellation or validation failure leaves the current scene unchanged.

## Reuse artwork in the existing geometry interfaces

`geometry.KineticIslandField` implements the existing `BaseField` interface. Its `level_set(0)` returns a real `ImplicitCurve`-compatible `KineticIslandCurve`. Both serialize bounded numeric recipes; no procedural callback is lost on reload. The curve can be wrapped in `CurveField`, composed through existing `BlendedField` / R-function operations, or added to an existing `SceneManager`.

`SceneService.get_geometry(id, time_value=...)` returns a detached field snapshot. `geometry_scene(time_value=...)` adapts one authoritative studio revision to the existing `SceneManager`, retaining stable object IDs. `geometry_paths(...)` uses the existing `GraphicsBackendInterface`; the read-only HTTP endpoint `/api/geometry?resolution=180&time=2` exposes those engine-derived shorelines. These adapters do not create a second writable scene.

This is a bounded integration seam. The current studio tool catalog edits kinetic-island recipes; it does not yet expose every legacy primitive, intersection operation, or historical SceneManager command. Browser color terraces use the parity-tested numeric mirror for responsive drawing, while Python consumers can use real geometry interfaces independently of the UI.

Run `python -m examples.tidal_atlas_engine` for a browser-free example that round-trips a kinetic curve through the existing `ImplicitCurve` dispatcher, extracts its shoreline through `GraphicsBackendInterface`, and composes it through `BlendedField`.
