# Browser performance and clean first run

Version 0.7.2 uses measured rendering evidence to define a practical scope. It
retains the engine, Python/JavaScript parity, validation, contour density,
sampling resolution and layer appearance. No quality reduction or new geometry
feature was needed for this pass.

## Reproduce on your own computer

Install `.[studio]`, then the locked development-only Node dependencies with
`npm ci` and Chromium with `npx --no-install playwright install chromium`.
Node and Playwright are needed for profiling, not for running the studio.

```powershell
$env:STUDIO_PYTHON = (Resolve-Path '.\.venv\Scripts\python.exe').Path
npm run benchmark:studio -- .\benchmark-results\studio
```

On macOS/Linux, use `STUDIO_PYTHON="$PWD/.venv/bin/python" npm run benchmark:studio`.
The harness refuses an occupied port and owns only a new ephemeral loopback
service on **8766**. Set `STUDIO_BENCHMARK_PORT` to another unused test port;
8000 is rejected to protect existing demo sessions. It writes recipe fixtures,
CPU profiles, screenshots, server logs and `measurements.json`, then stops its
own server. It never calls a model or edits the user demo.

Measurements use actual Chromium at 1440×1100, DPR 1: initial Canvas submission,
native pointer scrubbing, direct island/source dragging and two seconds of
playback. The requestAnimationFrame callback timings include rendering and UI
work. They measure CPU submission, not GPU completion. Event-to-observed-frame
timings include Playwright/automation overhead. Navigation-to-artwork includes
the first completed render; it excludes Python installation/server startup.
The browser's sampling profiler and instrumentation add overhead. Repeat on
target hardware before treating these as a frame-rate promise.

## Work17 baseline and supported complexity

October 12, 2026; Windows, Intel i9-12900H, 20 logical CPUs, Chromium 156.0.8078.4.
All fixtures use **48 island contours**, a reasonably high supported setting.
Baseline 0.7.1 values below are milliseconds, rounded; cold draw failures are
reported separately and fixed in 0.7.2.

| Fixture | First successful render | Scrub median / p95 | Drag median / p95 | Playback median / p95 |
| --- | ---: | ---: | ---: | ---: |
| Three islands with authored motion | 22 | 13 / 15 | 13 / 17 | 13 / 16 |
| Eight overlapping translucent islands | 31 | 33 / 38 | 38 / 49 | 33 / 41 |
| Two static blends retaining four sources | 224 | 8 / 12 | 16 / 24 | 9 / 13 |

Patched 0.7.2, same fixtures and instrumentation:

| Fixture | First render / navigation to completed artwork | Scrub median / p95 | Drag median / p95 | Playback median / p95 |
| --- | ---: | ---: | ---: | ---: |
| Authored motion | 13 / 193 | 16 / 23 | 18 / 26 | 12 / 15 |
| Eight layers | 45 / 162 | 33 / 40 | 35 / 39 | 39 / 47 |
| Two blends | 210 / 329 | 9 / 12 | 17 / 32 | 11 / 21 |

All patched profiles retain timeline keyboard focus after saving and record zero
uncaught browser errors. Differences between runs reflect normal scheduling/JIT
variance; the patch makes no numeric performance-improvement claim. The eight-layer
playback submitted 41 frames in its final two-second window. It is slower than
the lighter scenes, and remains explicitly documented as heavier work.

Three moving islands and cached blends fit the studio's existing approximate
30 Hz render cadence on this desktop. Eight dense layers require more work and
play back below that cadence (46 submitted frames in a measured two-second
window). This is an acceptable heavier editing workload, not a guaranteed 30/60
fps target. Static compositions pay for grid sampling on first render and when
sources change; the existing geometry cache makes unrelated timeline changes
cheap. Motion and translucency are preserved throughout.

Validation supports **16 islands**, **two static blends**, **24 poses per
island**, and **8–64 island contours**. These are data limits, not performance
guarantees. The measured guide covers three authored islands, eight layers and
two blends; maximum combinations, DPR 2 and phone hardware were not benchmarked.
Blends retain the existing 16-level, 128-cell committed/64-cell gesture sampler;
their sources remain static. Users can intentionally choose fewer contours for
lighter interaction, but the application does not silently lower quality.

## Observed interaction fixes

Actual baseline Chromium lost range-control focus after each saved keyboard edit:
the save lock disabled the focused slider and left focus on the document body.
0.7.2 restores it after the save only if it remains enabled and the user has not
focused/clicked elsewhere. Desktop/phone regressions exercise two consecutive
native arrow-key edits and deliberately move focus during a delayed save.

A transient zero-size layout raised an uncaught `drawImage` error when a scene
arrived before usable canvas dimensions. Rendering now waits for nonzero
dimensions. ResizeObserver makes the canvas dirty when layout recovers; no
geometry, history or scene data changes are involved. A real-browser regression
collapses and restores layout without mocking Canvas or reducing validation.

The regular browser suite verifies these behaviors without tight wall-clock
thresholds. The reproducible benchmark supplies raw distributions rather than
an unstable shared-CI millisecond gate. Review broad, sustained regressions with
the same fixtures and environment before adding an optimization.

## Clean environment and wheel verification

A new Python 3.11 virtual environment installed only `.[studio]` using the
documented command. Startup from a temporary directory outside the checkout
served all static assets and geometry, discovered the real 19-tool MCP catalog,
and ran the installed `twotop-studio --version` entry point. Neither pytest nor
PySide6 was installed. The same checks passed after replacing the editable
package with an isolated-build wheel; the module resolved in site-packages.
Baseline installed-wheel startup was **3.4 seconds** on Work17, without claiming
an installation/download duration guarantee.

`benchmarks/installation-smoke.py --output <directory>` repeats these read-only
checks in the currently selected environment on separate port 8767. A dedicated
CI job builds a wheel, installs its declared studio extra into a fresh virtual
environment and runs the probe outside the checkout. Development dependencies
cannot satisfy missing runtime requirements in that gate.

Windows instructions use the virtual environment's explicit Python executable;
activation and execution-policy changes are unnecessary. The Work17 guide uses
port 8768 so the running 0.7.0 user demo on 8000 keeps its in-memory history.

## Remaining original-goal integration gap

Profiling Chromium reports `document.modelContext` unavailable in all three
actual scenes. Available tooling exposes no supported top-level browser/model
session or configured external MCP model-client session that can be exercised
without installing/configuring access or making separately charged model calls.
The real SDK catalog check is protocol coverage; the adapter's mock test remains
explicitly mocked.

Native verification requires an already supported top-level browser exposing
`document.modelContext`, successful registration of the actual catalog, and a
connected model host permitted to choose and invoke its tools. MCP verification
requires the user's already configured local model client supporting Streamable
HTTP at the running studio's `/mcp/` endpoint or the documented stdio proxy, an
existing model session with permitted use, and an actual natural-language edit
followed by visible manual refinement/shared undo. No credentials, host flags,
client access or paid inference were added here. LAN approval remains separate.
