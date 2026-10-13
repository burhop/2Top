# Tidal Atlas agent protocols

## What is actually implemented

The manual interface, browser tools and MCP clients operate on one `SceneService`
inside the running local web app. They share object IDs, selection, revisions,
transactions, undo and redo. Neither adapter evaluates code, accepts an expression,
reads arbitrary files nor creates a hidden second scene.

The app does **not** include a language model, agent runtime or model API key.
Browser-tool registration makes the page available to a compatible external agent;
it does not mean an AI is connected. The normal editing interface works without
WebMCP. Presets and demonstrations are deterministic application actions.

There are two real MCP entry points, both implemented with the official Python
[`mcp` SDK](https://github.com/modelcontextprotocol/python-sdk), pinned to **2.3.0**:

- Streamable HTTP at `http://127.0.0.1:8000/mcp/`, mounted in the same process as
  the UI API, using the exact same service instance.
- An SDK stdio server that forwards tool discovery and execution to that running
  app's HTTP API. It cannot start an isolated scene. If the app is unavailable,
  discovery fails or tool execution returns `studio_unavailable`.

The legacy `graphics_backend/mcp_handler.py` remains a backward-compatible
application command handler. It is not the new standard MCP transport.

## Run locally

From the repository, with Python 3.11 or newer:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[studio,dev]'
python -m studio.app
```

Visit `http://127.0.0.1:8000/`. The app persists the recipe/revision at
`.studio/scene.json` by default; `--ephemeral` avoids disk persistence. Undo and
idempotency history are bounded and process-local. Run **one server worker**;
multiple independent workers would each have a different in-memory scene.

Use a Streamable HTTP-capable MCP host with the endpoint above. A generic stdio
host entry is:

```json
{
  "mcpServers": {
    "tidal-atlas": {
      "command": "/ABSOLUTE/PATH/2top-studio/.venv/bin/python",
      "args": [
        "-m", "studio.mcp_server",
        "--studio-url", "http://127.0.0.1:8000"
      ],
      "cwd": "/ABSOLUTE/PATH/2top-studio"
    }
  }
}
```

Host configuration formats differ. If your host does not support `cwd`, install
the package into the Python environment named by `command`; then `python -m`
resolves `studio` without a working-directory override. The CLI also accepts
`TIDAL_STUDIO_URL`. Only loopback HTTP origins are accepted by the stdio proxy.

No writes go to stdout outside the SDK stdio transport. Diagnostics use stderr.
No live host has been installed or connected on the user's behalf.

## Protocol compatibility verified

On 2026-10-11, the official SDK 2.3.0 `Client` successfully negotiated:

- **2026-07-28** with in-process, real loopback Streamable HTTP and real stdio
  subprocess connections. Modern discovery is handled entirely by the SDK.
- **2025-11-25** with the SDK client's legacy initialization mode in-process.

These are the versions tested here, not a claim about every host or earlier
protocol revision. The implementation uses SDK `Server`, `stdio_server` and
`Server.streamable_http_app`; there is no custom JSON-RPC transport or simulated
handshake. The current [official server guide](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server)
requires SDK 2.x. The environment initially supplied SDK 1.29.0, but the tested
project environment installs 2.3.0 from PyPI rather than relying on that older
package.

To mount in another trusted local app:

```python
from studio.mcp_server import create_mcp_http_app

mcp_app, mcp_lifespan = create_mcp_http_app(the_same_scene_service)
# Enter `async with mcp_lifespan():` in the parent's lifespan.
# Mount mcp_app at /mcp, producing /mcp/.
```

Mounted ASGI apps do not automatically receive lifespan startup. The parent app
must enter the returned lifespan factory, as `studio.app.create_app` does.

## Shared tools and schemas

`GET /api/tools` returns schemas generated from the exact Pydantic command models
used by `SceneService`. Both protocols consume these definitions rather than
maintaining separate copies. Additional properties are rejected. The MCP adapter
also validates arguments against those JSON Schemas before calling the service;
server-side command validation always remains authoritative.

Read tools:

- `get_scene`: complete scene, IDs, revision, selection and bounded history.
- `get_selection`: selected IDs and objects, document ID and current revision.

Mutation tools:

- `create_geometry`, `update_geometry`, `delete_geometry`
- `set_style`, `reorder_layers`, `set_view`, `select`
- `transform_layers`: atomic move/uniform-scale/rotate of explicit layers and all authored poses; [complete contract](group_authoring.md)
- `layout_islands`: center alignment/even spacing at an explicit authored time, translating complete island paths atomically; [complete contract](center_layout.md)
- `retime_keyframes`: one shared delta for explicit keys across multiple tracks, vacating selected times together and rejecting all targets on any collision/range failure; [complete contract](multi_key_retiming.md)
- `set_keyframe`, `delete_keyframe`, `edit_keyframe`
- `create_blend`, `update_blend`, `delete_blend`
- `batch`, `undo`, `redo`, `load_recipe`

Every mutation requires `expected_revision`, a nonnegative integer. An optional
`request_id` identifies one exact attempt. Use a fresh ID for a new command;
reuse the same ID **and same arguments** only when retrying an uncertain attempt.
The service returns the original transaction ID and the current scene for a
recognized replay, without applying the command again. Reusing the ID with
changed arguments is an error. Replay history holds the most recent 256 keys
and is lost on process restart; it is not a permanent deduplication ledger.

Example named-tool arguments, after reading revision 0:

```json
{
  "id": "island_ember",
  "parameters": {"radius": 190, "warp": 0.7},
  "expected_revision": 0,
  "request_id": "shape_001"
}
```

Call `update_geometry` with those arguments. Do not include `op` in named-tool
arguments. The manual `POST /api/command` route instead accepts an `op` alongside
the arguments. Batch child commands include `op`, omit revision metadata and are
restricted to thirteen small editing operations (including key insertion/removal). A batch is at most 32 commands
and commits as one revision/undo step, or makes no change on failure.

`set_keyframe` accepts `id` and `keyframe`, whose fields are `time` (0..12),
`parameters` (all six bounded pose values: x, y, radius, elongation, rotation,
warp), and `easing` (linear or smooth). It inserts or replaces the exact time;
the track is sorted and limited to 24 keys. `delete_keyframe` accepts `id` and
`time`; a missing key fails without a revision. The left key determines segment
easing. Rotation interpolates authored degrees, allowing deliberate long turns.
The server's geometry snapshots and browser rendering sample the same tracks.

`edit_keyframe` identifies an existing island key by `id` and exact source
`time`. Supply `new_time` (0..12), `position` (complete bounded x/y), or both.
All other pose values and easing remain unchanged. Retiming can cross neighbors;
tracks are sorted afterward. An occupied destination yields `keyframe_collision`,
an absent source yields `keyframe_not_found`; neither changes history/revision.
These edits can be batched with `set_view` for a shared paused playhead and one
undo step. Retry IDs and revision rules are the same as other mutations.

Version 0.6.0 exports schema 4 with complete layer order. Schemas 1/2/3 are
accepted by MCP schemas and migrate to islands-then-blends drawing order,
retaining styles, fields, tracks and dependencies. Unknown versions, incomplete
schema-4 orders, malformed poses and invalid references are rejected. Older
studios cannot read schema 4; retain originals for exchange. See
[composition layers](composition_layers.md) and [static blending](static_blending.md).

Recipes are versioned bounded data: at most 16 islands, finite numeric parameter
ranges, recognized palettes and explicit view/animation fields. `load_recipe`
replaces the artwork as one undoable transaction. Animation is an art-directed
visual effect, not a physical simulation.

Mutations return `{ok, scene, transaction_id, affected_ids, replayed}`. The scene
is the authoritative committed result. `get_scene` wraps the scene in an `ok`
result, while `/api/scene` returns the scene directly. MCP returns equivalent
JSON text and `structuredContent`; domain failures set `isError: true` and include
`{ok:false,error:{code,message,details}}` when supplied by the service.

On `revision_conflict`, read again and reconsider the intended edit; never
blindly substitute a new revision. Invalid input and failed atomic commands do
not advance the revision. All adapters avoid automatic mutation retries. A
network interruption can occur after a commit; a timeout is **not** proof that
the mutation failed. Reconcile with `get_scene` and the same `request_id`.

## Browser WebMCP

`studio/static/webmcp.js` uses the current imperative API:
`document.modelContext.registerTool`. It registers only in the actual top-level
application document, and only after feature detection. It does not patch in a
fake API, inspect `navigator.modelContext`, require a browser extension, or label
unsupported browsers as agent-connected.

The exported `registerWebMCP({onScene,onStatus})` is idempotent and is also called
at module startup. It fetches `/api/tools` and submits exact tool arguments to
`POST /api/tools/{name}`. Mutations use the caller's explicit revision and request
ID. Browser cancellation signals are forwarded to `fetch`; cancellation produces
no fabricated success and does not cause a retry. Status is exposed through
`window.tidalWebMCPStatus` and `tidal:webmcp-status`; committed scenes are emitted
through `tidal:scene` and the `onScene` callback. A broken presentation callback
cannot turn a committed transaction into a reported tool failure.

Registration status says only whether the browser supports the API and how many
tools were registered. Failed partial registrations are aborted. All normal UI
controls remain available in unsupported browsers. MCP and WebMCP annotations are
hints for hosts, not a substitute for permission or server validation.

The implementation follows [ChatGPT's site-tools guide](https://learn.chatgpt.com/docs/webmcp)
and the current [WebMCP specification](https://webmachinelearning.github.io/webmcp/).
[Chrome's guide](https://developer.chrome.com/docs/ai/webmcp), updated October 7,
2026, describes an origin trial starting in Chrome 149 and a local testing flag.
Support is still experimental and browser-dependent. This change does not enable
browser flags or enroll an origin. Native browser/agent interoperability must be
verified in a compatible browser; mocked registration tests alone do not prove it.

## Safety and scope

This is a single-user loopback studio with no account authentication. Do not bind
it to a public interface or expose it through a tunnel as a production service.
The app checks host/origin, the SDK retains DNS-rebinding protection, and the
stdio proxy rejects non-loopback origins and credential-bearing URLs. Mutation
bodies and tool inputs are bounded. Actor labels in history (`manual`, `mcp`,
`webmcp`) describe the entry point; they are not authenticated user identities.

Agents should seek the user's intended edits through their host's normal
permission flow. Tools cannot publish, send messages, install software, access
credentials, execute arbitrary code or select a persistence path. Model providers
and remote clients are not configured by this adapter.

## Repeatable verification

```sh
.venv/bin/python -m pytest tests/studio/test_mcp.py -q
node tests/studio/webmcp_contract.mjs
```

The Python tests use the official SDK client to discover and execute tools. They
verify exact shared schemas; modern and legacy negotiation; edits, selection and
manual undo on the same scene; stale revision and input errors; idempotent retry;
atomic batch rollback and undo/redo; unavailable-proxy behavior; and real HTTP and
stdio connections to the actual FastAPI app. The stdio integration starts a real
subprocess and compares its edit against both HTTP MCP and `/api/scene`.

The Node contract test deliberately mocks `document.modelContext`. It checks
unsupported-browser fallback, one-time registration, schema passthrough, command
routing, scene events, error propagation, cancellation and callback isolation.
It does not claim a native browser agent has executed the tools.

## Composition layer commands

`reorder_layers` takes every layer ID exactly once, back to front. `set_style`
accepts island or blend IDs; `select` and `get_selection` cover both. Creating
geometry appends a frontmost ID and deleting it removes that ID. Order and style
changes are atomic and reversible; source deletion guards are unchanged. Schema
1/2/3 migrates to islands-then-blends order. See [composition layers](composition_layers.md).

## Coauthor provenance in 0.7.0

History adds server-observed `source.entrypoint`, UTC commit time, actual
`changes`/`summary`, operation and related undo/redo transaction/revision. Legacy
`actor` and batch `label` are retained; caller hints and notes are not identity or
authority. Direct MCP is distinguished from the named HTTP bridge used by stdio
and WebMCP. Recipes remain schema 4 and do not import/export process history.
The explicit `studio.mcp_client` uses the real SDK; it is not a model host.
See the [coauthor guide](coauthoring.md) for setup and the exact evidence limits.

## Batch and session contract clarified in 0.7.1

Every child must satisfy its command schema and operation preconditions (for
example, referenced objects must exist and dependent blends must be removed
before deleting a source). Cross-record recipe invariants are checked on the
complete final candidate, before persistence. Thus a batch may reorder to the
final remaining IDs before deleting an omitted layer; standalone reorder still
requires every live ID exactly once. Deletion removes all references to its ID
from order. Unknown/duplicate/missing surviving IDs fail with structured validation,
leaving state, disk, history, revision and retry keys unchanged. Selection checks
actual records, never an unvalidated intermediate order list.

Snapshots include `session_id`, a process identity rather than authentication.
It changes on service initialization while document/revision/artwork may stay
the same. It is not a recipe field or persisted authority. The UI refreshes
history/undo on a new session, defers snapshot application during an active
gesture, and continues playback. Late snapshots from retired sessions are ignored.
