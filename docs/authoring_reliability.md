# Integrated authoring reliability - 0.11.1

This patch polishes the existing authoring flow rather than adding another art
operation. Phone navigation, local pose-selection continuity and reconnects now
have explicit behavior, with baseline failures and regression evidence.

## Navigation and selection

On a phone-sized layout, sticky **Canvas**, **Layers** and **Timing** links jump
between existing sections. **Canvas** also leaves Recipe view. Jumps are local,
read-only and retain a held preview; they do not move the camera or commit edits.
Targets account for the sticky navigation/connection notice, and links have 44px
minimum touch targets. Desktop layout retains the existing full workspace.
The export menu stays above the sticky bar. Recipe view shows the confirmed scene,
consistent with Copy JSON/JSON export; it does not present a preview as committed.

Pose selection survives geometry/appearance edits when the exact-time key set is
unchanged. Known timing Undo/Redo restores that track state's selected poses, so
compression and subsequent shifting can be revised without repeatedly selecting
chips. Native pose-chip keyboard focus survives saves, unless the user deliberately
focuses another control during the save.

Selection memory is local and bounded to 64 track states. Import, document/session
or selected-island changes clear it; unknown structural track edits clear it rather
than guessing key identity. Old evicted states restore no selection safely.
No persistent pose IDs or recipe/schema change is introduced. JSON exports contain
the artwork and timing, not this browser-local selection memory.

## Disconnect and reconnect behavior

Connection loss displays a notice and disables scene editing. The confirmed scene
and any held preview remain available; Cancel and read-only section navigation
still work. **Reconnect** performs a read rather than replaying a save. A heartbeat
also checks connectivity during held previews. Reconnecting to the same session
can retain the preview; a new document/session clears it and asks the user to
review the reconnected scene before editing.

Reads have a five-second deadline and save confirmation a ten-second deadline.
A stalled save releases controls after reconciliation instead of leaving the UI
indefinitely pending. A lost reply can mean the edit committed: refresh the scene
and inspect it before retrying. The app never automatically replays that write.
Undo/history remains process-local and resets on server restart; persisted artwork
and revision can survive that restart. The notice does not promise history recovery.

## Shared command context guards

All mutation schemas expose optional **expected_document_id** and
**expected_session_id**, alongside expected_revision and request_id. Read their
exact values from `get_scene`, then include them with an edit:

```json
{
  "view": {"contours": 30},
  "expected_revision": 3,
  "expected_document_id": "doc_actual_id",
  "expected_session_id": "session_actual_id",
  "request_id": "unique-attempt"
}
```

Replace example values with the actual scene. Document/session mismatches return
**document_conflict**/**session_conflict** (409) before retry replay or mutation.
This prevents a cached preview from being accepted merely because a restarted
server has the same revision. The manual UI captures these guards with queued
edits, gestures and asynchronous imports. Native/remote clients can use the same
validated fields. Legacy revision-only calls remain compatible; those callers
must opt into context guards to obtain restart protection.

The catalog remains 23 tools. Guards are transaction metadata, never geometry or
recipe data. Schema 4, geometry sources, dependencies, main, credentials and
loopback/LAN settings remain unchanged.

## Evidence and stopping point

Baseline browser checks reproduced selection loss after a nudge on desktop/phone
and a real restarted process accepting an old preview with equal document/revision.
The phone layout's long separation between canvas, layers and timing motivated
read-only section jumps. Corrected acceptance covers these flows, known Undo/Redo,
import reset, native focus, controlled save stalls and lost replies.

Reconnect QA includes actual stop/start of a newly owned loopback process on 8770
and browser offline simulation. The equal-revision race also replays a captured
old GET response while an unmodified POST reaches the new process. These tests
do not represent a physical phone, Wi-Fi/LAN outage or deployed network test.
Port 8000's live document/history is excluded. The previous 25-step walkthrough
is preserved; its patch rerun verifies the same integrated journey with restored
pose selection, raw/annotated screens and browser diagnostics.

The independent authoring flow has a coherent stopping point in these tested
scenarios. Remaining limits are explicit: one-track manual pose selection,
bounded local memory, process-local undo, and unverified actual phone/network and
native WebMCP/model-host operation. Do not invent another feature to extend the
milestone; obtain hands-on creator feedback or investigate a concrete new defect.
