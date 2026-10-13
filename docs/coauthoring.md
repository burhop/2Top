# Coauthor the same canvas — 0.7.0

The studio, standard MCP clients and the browser adapter edit one bounded scene,
with the same revisions, validation and undo history. **Client setup** shows the
running application's actual local endpoint and stdio launch settings. This app
includes no model connection. The provided protocol client and saved examples
are not a live natural-language model integration.

## A human-repeatable session

1. Export a JSON recipe to preserve your starting artwork. Keep the studio open.
2. Open **Client setup**. Use an already configured local MCP/model client on
   this computer. Enter the displayed Streamable HTTP endpoint, or map the
   displayed `command`, `args` and `cwd` into its stdio configuration fields.
   Different clients use different configuration formats. No configuration,
   credentials, permissions or browser flags are changed by the studio.
3. Discover the tools. Read `get_scene` and choose a small edit against its actual
   IDs/revision. `set_style` changes palette/opacity/visibility; `update_geometry`
   changes an island's parameters; `batch` groups edits into one undo step.
   Supply the current `expected_revision` and a fresh `request_id` for a write.
   If the scene changed, read it again and reconsider the edit; do not silently
   replace the revision or retry a different intent.
4. Watch **Coauthor activity** for the committed edit. A real HTTP MCP call is
   recorded as **MCP protocol**. Select the changed layer and adjust a manual
   control or drag its center. Undo the manual refinement; undo again as needed
   to reach the MCP edit, then redo from either client. Selection is itself an
   undoable command, so it may sit between the edits.
5. Export JSON to keep the final artwork. Reopening preserves fields, layer
   order, styles, tracks and dependencies. History is process-local and not
   included in a recipe; a browser reload retains it, a server restart resets it.

Suggested prompt for your existing model client:

> Read get_scene. Find the selected layer, propose a subtle palette or opacity
> change, and make it with set_style or one batch using the current revision.
> Read the scene again and explain the committed change. Preserve other layers.

The schema catalog at `/api/tools` and the tool reference at `/api/docs` are
generated from the same validated command models. Version 0.10.0 has 22 tools,
including atomic whole-path `transform_layers`; see [group authoring](group_authoring.md).
No geometry or recipe-schema changes are required for this milestone.

## Read-only protocol check, then an explicit call

The existing official MCP 2.x SDK is used by the helper. Start the studio first:

```powershell
.\.venv\Scripts\python.exe -m studio.mcp_client --studio-url http://127.0.0.1:8000 --catalog
.\.venv\Scripts\python.exe -m studio.mcp_client --studio-url http://127.0.0.1:8000 --tool get_scene
```

For a write, prepare a JSON arguments file using IDs and revision from that read,
then pass `--tool set_style --arguments your-edit.json`. The helper only sends
the explicit tool/arguments. It does not infer intent, choose a revision, retry a
mutation, call a model, or create a scene if the service is unreachable. Its URL
must be a loopback HTTP origin. Failure exits nonzero; inspect the structured
result before assuming a write happened.

The local stdio adapter continues forwarding to the same app. The server sees
its named HTTP bridge and records a caller hint, not a verified MCP/person/model
identity. Direct Streamable HTTP calls are observed at the actual MCP endpoint.
MCP standardizes these two transports; see the current official
[transport overview](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)
and [stdio binding](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio).

## What history proves

The server adds observed entry point, committed UTC time, transaction ID,
actual scene differences, a bounded summary and undo/redo target references.
The activity filter distinguishes:

- **UI / HTTP**: command endpoint. This route can also be used by scripts; it
  does not prove a human clicked a control.
- **MCP protocol**: the official MCP endpoint/SDK dispatcher observed a call.
  It does not prove model inference or the caller's identity.
- **WebMCP / HTTP bridge**: named-tool HTTP route used by the WebMCP adapter and
  stdio proxy. Any `X-Studio-Actor` value is an explicitly unverified caller hint.
  The route does not prove native browser execution.
- **Internal service**: direct trusted-code calls, including unit-test fixtures.

The legacy `actor`/`label` fields remain compatible, but the UI uses observed
routes and server-computed summaries. Batch labels appear only as client notes;
they are data, not identity or authority. Body fields cannot inject provenance.
Replayed writes do not add commits; failed validation/conflicts/persistence do
not add successful activity. The UI retains the most recent 30 entries, with
bounded internal event/history storage. Undo/redo records point to the original
transaction, even when invoked through another route.

## Native WebMCP remains separate

Use an already supported top-level browser/model host, confirm real tool
registration, then exercise an actual shared-scene edit. Registration alone is
not a model connection, and an ordinary Chromium mock is not host verification.
Work17 acceptance Chromium reports the API unavailable. No supported model host
is exposed to this worker; no native host session, flags, trial enrollment,
credentials, permission expansion or paid model calls were used.

Chrome currently documents WebMCP as a proposed standard with trial/local
development availability; consult [its official guide](https://developer.chrome.com/docs/ai/webmcp)
for the intended host's current requirements. The [WebMCP API draft](https://webmachinelearning.github.io/webmcp/)
documents `document.modelContext`. This milestone keeps the existing progressive
adapter and its unsupported-browser fallback; it does not enable experimental
browser settings or claim an untested natural-language session.

## Restart behavior in 0.7.1

Process session metadata invalidates snapshot and activity caches even if the
saved document ID and revision are unchanged. Ordinary idle polling clears old
history and disables unavailable Undo/Redo after a restart. Active gestures keep
their preview until they finish/cancel, then polling reconciles the new session.
Playback is not implicitly paused. This metadata does not authenticate a caller
or establish a model connection; recipes still exclude process history.
