# Try current dev on Work17

In PowerShell, use the isolated project checkout and its installed environment:

```powershell
Set-Location 'C:\Users\markb\Documents\Codex\2026-10-11\task\2Top-recovery-0.2.0'
git fetch origin dev
git switch dev
git merge --ff-only origin/dev
.\.venv\Scripts\python.exe -m studio.app --ephemeral --port 8768
```

Open **http://127.0.0.1:8768/** on Work17. The current user demo stays on port
8000 in its fixed 0.7.0 worktree; leave it running to retain its session history.
This separate ephemeral session leaves existing
saved artwork untouched; export JSON to keep your edits. Stop the foreground
server with Ctrl+C. For normal local persistence, omit `--ephemeral`.

For static blending, choose **Try confluence**, then switch Operation between
Union and Smooth union and choose Apply blend. Adjust Blend amount; choose Edit
A/B to move a source. Remove blend restores both separate islands. Blends ignore
timeline/tide and accept static source islands only. Export JSON to keep the
composition. The current version exports schema 4 and reopens older recipes.

For choreography:

1. Choose **Play demo**, pause, and select **Solstice** in the Islands list.
2. Choose **Edit motion path**. Drag the labeled 3s handle to reshape its orbit.
3. Choose the 3s pose chip, enter **7.5** in Key time, then choose **Move key**.
   The key crosses 6s and retains its shape. Try 6s to see collision rejection.
4. Undo/redo, then play to see the changed route/timing. Match the 0s and 12s
   poses to keep a seamless loop; choose an endpoint chip before moving an
   overlapping endpoint handle.
5. Export JSON. Recipe → Load JSON reopens the complete track. PNG/SVG exports
   contain artwork without path guides.

The URL is local to Work17. The delivery verification record states whether a
server was actually started and checked; this guide alone does not imply that
one is running. Native WebMCP execution still requires a supported model host.

## Preview center layout in 0.9.0

Choose **Select visible** or select three island rows using **Select multiple**.
Under **Center layout**, choose **Space horizontally**, inspect the preview, then
**Cancel** or **Apply layout**. Undo/Redo restores the complete authored paths.
**Align vertical** aligns x centers; **Align horizontal** aligns y centers.
Spacing holds the outer centers fixed. Select island rows rather than blend rows.
The preview pauses at its displayed authored time; Apply preserves that time.
This arranges centers, not shore edges or collision-free gaps.
[Layout guide](center_layout.md). Keep the existing port 8000 demo intact.

## Arrange layers in 0.8.0

On the separate current-dev session at port 8768, choose **Select multiple**,
tap two layer rows, then **Done selecting**. Nudge right, set Group scale factor
to 1.10 and choose **Scale selection**, then rotate 15 degrees. Drag either
selected layer, cancel with Escape, or commit and Undo/Redo. Complete authored
paths move together. Select a blend plus a retained source to see sources move
once. [Authoring guide](group_authoring.md). Keep the existing port 8000 demo intact.

## Try 0.6.0 layers

Use **Try layered study** for Glasswater. The frontmost row appears first. Select
Glass veil, change its palette/opacity and use its arrow buttons to place it
behind Gold confluence. Hide a blend to reveal its sources, or select a source
row to edit its dashed center handle while retaining the blend. Export JSON
to preserve edits before restarting an ephemeral demo. [Layer guide](composition_layers.md).

## Coauthor in 0.7.0

Use **Client setup** for actual local MCP launch settings and the guided flow.
Discover tools, read the current revision, make a small client edit, then refine
it manually and use shared Undo/Redo. **Coauthor activity** shows observed routes,
server-computed changes and the target of undo/redo. Client notes are not verified
identity or inference. [Coauthor guide](coauthoring.md). History resets when the
server restarts; export JSON to retain artwork.
