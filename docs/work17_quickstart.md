# Try current dev on Work17

In PowerShell, use the isolated project checkout and its installed environment:

```powershell
Set-Location 'C:\Users\markb\Documents\Codex\2026-10-11\task\2Top-recovery-0.2.0'
git fetch origin dev
git switch dev
git merge --ff-only origin/dev
.\.venv\Scripts\python.exe -m studio.app --ephemeral --port 8000
```

Open **http://127.0.0.1:8000/** on Work17. The ephemeral session leaves existing
saved artwork untouched; export JSON to keep your edits. Stop the foreground
server with Ctrl+C. For normal local persistence, omit `--ephemeral`.

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
