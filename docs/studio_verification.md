# Tidal Atlas development verification

Updated October 14, 2026 for version 0.18.0. Work17 executes the local application
checks below; CI verifies the exact feature commit before dev integration.

## Current milestone

Version 0.18.0 repairs [signed-distance cache freshness](distance_cache.md),
nearest-hole magnitude and live generic polygon containment. Independent source
review approved the bounded correction. The final affected distance/field/
composite/region suite passed **175 tests**, including **66 new analytic/cache
cases**. Full Work17 and exact-commit CI results are recorded with the milestone
handoff and PR. All 59 JavaScript checks, mocked WebMCP, 154-file configured Ruff
and 45-file explicit CI targets passed. Dependency metadata diffs change only
the project version; all 58 dependency records remain unchanged, and both h11
artifact records match canonical release metadata. Warm sequential measurements
record repeated-query costs, generic straight-edge gains and no retained query
buffers. Curved sampling, separate source metadata, short-edge/overflow numerics
and native WebMCP remain explicit limits.

## Previous milestone

Version 0.17.0 corrects [occupancy boundary validity](occupancy_validity.md),
discrete level-set semantics and unsafe mask caching. Independent review approved
the final source. Work17's full run passed 1,731 tests with 27 skips and 43 warnings,
then found one additional legacy integration assertion expecting a curve at an
unattained binary level. That assertion now requires explicit rejection; the
final affected AreaRegion/occupancy/field suite passed **220 tests**, including
**73 new analytic/edge cases**. Exact-commit CI runs the complete final suite.
All 59 JavaScript checks, mocked WebMCP, 153-file configured repository Ruff and
41-file explicit CI targets passed. The runtime-only installed 0.17.0 wheel passed
occupancy geometry, outside-checkout startup/assets and the real 23-tool MCP
catalog. Existing legacy AreaRegion equality assertions remain outside the
configured lint targets. Validation costs and finite-sampling, topology-cache
and discontinuous-plot limits are recorded. Native WebMCP remains unverified.

## Previous milestone

Version 0.16.0 adds analytic algebraic derivatives, query-local graph reuse and
blended contours retaining known procedural uncertainty.
[Independent contracts and raw timings](field_algebra.md). Work17 full suite:
**1,658 passed, 27 skipped, 43 warnings**. After the final contour-override guard
and fixture were added, all **73 new analytic/regression cases** passed in the
final focused run. Exact-commit CI runs the complete final suite and real Chromium.
All 59 JavaScript checks, mocked WebMCP, 152-file repository Ruff and explicit
36-file CI lint/format targets passed. The runtime-only installed 0.16.0 wheel
passed packaged algebraic geometry, outside-checkout startup/assets and the real
23-tool MCP catalog. Independent review approved the final source. Direct cheap
grid derivatives retain measured overhead; contour gradients avoid repeated
finite-difference evaluation. Heuristic errors remain estimates, and native
WebMCP remains unverified.

## Previous milestones

Version 0.15.0 adds bounded automatic procedural steps and sampled-consistency
diagnostics while retaining explicit scales and analytic callbacks.
[Analytic fixtures, failure modes and measured cost](automatic_derivatives.md).
Final Work17 Python suite: **1,586 passed, 27 skipped, 43 warnings**, including
**36 new regression/analytic cases**; focused compatibility suite: **208 passed**.
All 59 JavaScript checks, mocked WebMCP, 150-file repository Ruff and explicit
32-file CI lint/format targets passed. The installed 0.15.0 wheel verifies outside-
checkout assets, geometry and the real 23-tool MCP catalog with runtime packages
only. Exact-commit CI includes real Chromium; native WebMCP remains unverified.
Independent review verified flat-axis normals, quantized/discontinuous rejection,
mask/metadata parity and the hard vector-probe budget. A smooth hidden-feature
counterexample still yields a wrong gradient/normal despite flat samples; finite
sampling is not an accuracy certificate. Default numerical cost increases on the
saved grid; explicit scales/callbacks retain their performance paths.

Version 0.14.0 adds supported quadratic sublevel envelopes, recursive smooth
blend bounds and numeric-kernel-preserving CurveField level sets.
[Contracts, counterexamples and measurements](sublevel_bounds.md). Independent
review covered custom wrapper evaluators, compiled expression/variable changes
and shifted procedural normal guards. Final Work17 Python suite: **1,550 passed,
27 skipped, 43 warnings**, including **39 new analytic/regression cases**.
All 59 JavaScript checks, mocked WebMCP, 148-file repository Ruff and explicit
29-file CI lint/format targets passed. The final installed 0.14.0 wheel passed
outside-checkout startup, packaged assets and the real 23-tool MCP catalog with
runtime dependencies only. Real Chromium acceptance runs in exact-commit CI;
native WebMCP remains unverified. Enclosures apply to the mathematical field,
and unsupported domains and finite sampling retain documented limits.

Version 0.13.0 adds representable procedural stencils, local scale hints,
uncertainty diagnostics and analytic gradient callbacks. Independent review
corrected cross-axis scale coupling, scalar branching callback fallback and
subnormal quantization reporting. [Contracts and raw measurements](procedural_derivatives.md).
Work17: full Python suite **1,511 passed, 27 skipped, 43 warnings**; final focused
derivative/singularity compatibility suite **138 passed**; 59 JavaScript checks,
mocked WebMCP contract and 145-file repository Ruff checks passed. Installed
0.13.0 wheel startup/assets/real 23-tool MCP smoke passed outside the checkout.
Actual Chromium acceptance runs in exact-commit CI; local UI code is unchanged.
Native WebMCP remains unverified. Prior milestones below retain their own counts.

Version 0.12.0 fixes reusable field/normal/blend numerics and deterministic sampled
contour extraction. Independent review found and covered subnormal subtraction
rounding and contours collapsing during world mapping. Baseline new tests
reproduced 24 failures out of 30; expanded independent-oracle and browser-parity
cases cover the final implementation. [Backend contracts and saved timings](implicit_backend.md).
Final local verification: **1,472 Python cases passed, 27 skipped, 43 warnings**;
**72 new numerical/parity cases**, 59 JavaScript checks, mocked WebMCP contract,
143-file Ruff lint/format and **57 real Chromium cases passed (4.7 minutes)**.
The installed 0.12.0 wheel passed outside-checkout startup, packaged assets,
geometry response and the real read-only 23-tool MCP catalog without dev packages.
The full-suite procedural cusp regression was fixed and rerun successfully.
Native WebMCP host support remains unverified. Exact-commit CI gates dev integration.
The detailed 0.11.1 results below are retained as historical evidence.

Version 0.11.1 is the bounded integrated reliability patch: phone section jumps,
known pose-selection restoration, guarded document/session edits and explicit
reconnect/save-confirmation behavior. Authoritative Recipe JSON remains confirmed
data during previews, and the phone export menu stays above sticky navigation.
[Reliability contract](authoring_reliability.md). No new art operation or schema
change is added; existing authoring capabilities below remain.

Version 0.11.0 adds anchored timing stretch/compression with first/last selected
pose, visible-playhead and custom anchors. Scaling and shifting share selection,
Preview/Apply/Cancel, source/destination lists and atomic destination validation.
One invalid track rejects all targets. Factor 1 and anchored keys stay exact;
complete poses/easing, base geometry and recipe schema 4 remain compatible.
The catalog contains 23 tools. The manual selector edits one island's track;
commands can target multiple explicit tracks. [Scaling contract](anchored_time_scaling.md),
[retiming](multi_key_retiming.md),
[center layout](center_layout.md) and [group transforms](group_authoring.md).
Existing geometry/parity, quality and clean-wheel checks remain. The
[0.7.2 performance baseline and reproduction guide](studio_performance.md) remain available.

The manual UI, real MCP HTTP/stdio and WebMCP adapter share 23 validated tools,
revisions, atomic batches, retry keys, persistence and undo/redo. Source deletion
is guarded while referenced. See [static blending](static_blending.md) for field
semantics, reference rules, sampling budgets and degenerate-case behavior.

## Local verification

- Full Python suite: **1,400 passed, 27 skipped**. The skips require unavailable
  curves.db data or opt-in visual baselines. Numeric/runtime warnings remain
  visible rather than being suppressed.
- Studio subset: **362 cases**, including context guards, anchored scaling, multi-key retiming, center layout, choreography, motion-edit and whole-path group cases for interpolation,
  endpoint/loop semantics, Python/JavaScript parity, demo reproducibility,
  malformed input, sorted unique keys, limits, replay/stale revisions, rollback,
  persistence, legacy migration and real MCP HTTP/stdio pose edits.
- JavaScript: **35 DOM/service, 10 real-raster/layer-policy, 10 authoring-state and four owned-process lifecycle checks passed**. This is distinct from
  native browser layout testing.
- Explicitly mocked WebMCP contract: passed, including forwarding choreography and static-composition tools. This does not establish native host support.
- Repository-wide Ruff lint and formatting: passed, **141 files already formatted**.
- Actual Playwright Chromium acceptance: **57 cases passed**, with unexpected
  console, page and HTTP failures rejected.
- Installed 0.11.1 wheel: outside-checkout startup, all packaged assets including
  `pose-selection.js` and the real read-only 23-tool MCP catalog passed. Only declared
  dependencies are installed; pytest/PySide6 are absent.

0.11.1 adds document/session guards, direct HTTP and official MCP coverage,
ten bounded selection-memory checks and nine actual browser workflows. Desktop
and phone cases exercise selection after geometry edits, known undo/redo, import
reset, section navigation, authoritative Recipe JSON during previews and native
focus. Newly owned loopback services exercise real persistence/restarts and stale
same-revision writes; browser routes/offline simulation exercise controlled stalls
and lost replies without claiming physical-device or deployed-network coverage.

The first full 57-case run exposed the phone navigation covering export choices
and an obsolete restart-preview expectation; it also exceeded the unchanged
12-minute suite limit while other verification competed for the machine. The
export stacking was fixed, restart assertions now require clearing stale gestures
without writing, and download waits are joined with their clicks. A separate
Recipe reproduction showed preview data in the authoritative pane; it now reads
the confirmed scene. Four affected workflows passed, followed by all 57 cases in
6.9 minutes with the original timeouts. Full Python checks passed before the last
UI-only fixes; final DOM/raster/state checks and the rebuilt wheel cover that final
UI source. The patch's 25-action walkthrough completed with empty diagnostics.
The integrated reliability pass has a bounded stopping point; hands-on creator
feedback and native WebMCP/model-host verification remain separate work.

The first exact-feature Linux CI run passed 55 browser cases but timed out in
both real restart cases. The test helper mistook a signal-terminated child with
null exitCode for a running process, then waited for an exit event already emitted.
Its exit listener is now bound before termination, signalCode also establishes
completion and repeated stops share one promise. A deterministic signal-exit
reproduction, four lifecycle checks (including a real owned child through the
POSIX path) and both unchanged restart assertions verify the correction. Browser
assertions and timeouts remain unchanged; final Linux CI is required before merge.

0.11.0 adds 38 scaling cases and two real HTTP/stdio MCP cases covering anchors,
compression/stretch, exact identities, simultaneous vacancy, multi-track atomicity,
factor/time limits, floating-point destination collapse, hidden tracks, persistence,
retry/conflict/batch rollback, direct playback preservation and numeric JS parity.
Seven additional desktop/touch browser workflows check all four anchors,
preview/cancellation/focus, Apply/undo/redo/JSON reopening, stale actual-MCP edits,
and the combined move/align/compress/shift workflow. A separate 25-action review
produces raw/annotated screenshots, a live HTML report, a trace and empty browser
diagnostics on a newly owned ephemeral service. Its stopped driver-lookup evidence
is preserved; the corrected named-combobox rerun completed, and both report
structures validated. This is scripted, human-repeatable evidence rather than
a creator study. Its prioritized integrated reliability review is covered by
0.11.1 above.

0.10.0 adds 33 retiming cases and two real HTTP/stdio MCP cases: simultaneous
vacated-time movement, multi-track rollback, bounds/collisions, destination float
collapse, maximum 16 tracks/24 keys, invalid targets, exact key lookup,
persistence, retries/stale revisions, atomic batches and shared undo/redo.
Python/JavaScript valid-result and invalid-preview parity is checked. Five new
actual desktop/touch browser workflows exercise selection, preview/cancellation,
Apply, undo/redo, JSON export, endpoints, frozen playback and a real client conflict.
Desktop/phone screenshots were visually reviewed; pose chips and retiming buttons
have 44px minimum touch targets. The final collision wording has six targeted
rechecks, and the final installed wheel is rebuilt/smoked after that wording change.
Native host/natural-language execution remains separate from these checks.

0.9.0 adds 28 layout cases, two real HTTP/stdio MCP cases and five actual browser
workflows. They verify center placement/fixed endpoints, complete tracks,
coincident fractional centers, deterministic ties, hidden/retained sources,
atomic bounds/persistence/revision failures, desktop/phone preview/cancel/apply,
undo/redo/export, captured playback time and a real client conflict. Desktop and
phone layout screenshots were visually reviewed. WebMCP forwarding is mocked;
native hosting and genuine natural-language coauthoring remain unverified.

0.7.2 adds desktop/phone native keyboard continuity (including focus deliberately
moved during a delayed save) and zero-size layout recovery. Measured baseline
failures are reproduced before the fixes. No tight shared-CI timing gate or
unmeasured quality reduction is introduced.

0.8.0 adds five actual browser workflows for desktop/phone grouping, complete
track transforms, shared retained sources and stale/out-of-bounds drag rejection.
Direct/service, HTTP, official HTTP/stdio MCP and Python/JavaScript parity cases
verify atomicity, exact static contour transforms, 18-layer support, persistence,
retry/conflict semantics and cross-client undo/redo. WebMCP registration and
forwarding coverage remains explicitly mocked; native hosting is unverified.

The three new real-browser cases exercise native capture/scrub/easing controls,
interpolated poses, keyed pointer movement, undo/redo, actual downloaded JSON
reopening and reload, malformed-track rejection, schema-1 import, demo playback,
track-aware duplication and a 390-pixel phone layout. The existing nine cases
retain selection, cancellation, pending-request behavior, presets, responsive
layout and actual JSON/SVG/PNG export coverage.

Two additional desktop/phone browser cases use actual canvas pointer handles,
cross-neighbor retiming, collisions, range controls, undo/redo, cancellation,
coincident 0s/12s endpoints, seam indicators and saved JSON reopening/reload.
The real MCP workflow loads authored tracks, edits position/time, observes the
same state through MCP and HTTP, retries safely, rejects a collision and sees a
manual undo. Motion-edit unit tests cover disk persistence and Python/JS parity.

Twenty new Python cases cover legacy field evaluation and full Python/JavaScript
contour parity, two components merging into one, bounds, finite grids, omitted
fragments, snapshots, migration, references/cycles, budgets, rollback, persistence,
safe source removal, the real legacy graphics bridge and an actual MCP workflow.
The two new real-browser cases cover creation, operation/amount changes, source
selection and pointer editing, undo/redo, source-preserving removal, showing
separate/merged artwork, responsive layouts, SVG export and saved JSON reopening.
The prior choreography and motion-path cases remain enabled.

Nineteen additional Python cases verify complete order, atomic rollback, style
bounds, unchanged geometry bounds/evaluation, hidden-source dependency guards,
undo/redo, disk/save migration and a real MCP ordering/style workflow. Two
additional actual desktop/phone browser cases check frontmost artwork selection,
native button/opacity keys, hidden-source pointer edits, alpha pixel values,
SVG order/group opacity and saved JSON reopening. Raster alpha checks permit one
8-bit rounding unit; this does not establish cross-browser pixel identity.

Four additional Python cases cover provenance spoofing boundaries, actual diff
summaries, no-op/replay/conflict history, cross-client undo references, bounded
history, persistence/restart and real MCP protocol calls. Two more actual browser
cases use the official MCP client alongside native manual controls, test stale
writes, escaped caller notes, truthful bridge hints, history filtering and actual
save/reopen on desktop and phone. These are scripted protocol acceptance, not a
separate model inference session. Coauthor UI screenshots were visually reviewed.

Glasswater front/behind desktop and phone screenshots were visually reviewed.
Confluence separate/merged desktop and phone screenshots were visually reviewed.
Source guides, controls and checked phone width fit their layouts. This does not
establish exact topology, distance/offset correctness, every viewport/browser or
every assistive technology. Native WebMCP host execution remains separate.

Run `npm run test:browser`. Raw screenshots, downloads, diagnostics, videos and
traces are in `test-results/browser/`; the clickable report is in
`playwright-report/`. CI uploads the same evidence for each browser run.
The milestone PR provides the exact commit and CI links.

## Reviewed reliability regressions

Twenty-four added Python cases cover geometry/blend reorder-deletion batches,
structured malformed-final-state rejection, disk/history/revision/retry-key
rollback, undo/redo, actual-record selection, persisted restart identity and
Unicode safety across direct, HTTP and real MCP boundaries. Pydantic already
rejects lone high/low surrogates; the SDK may reject them before sending. Valid
supplementary Unicode round-trips without extra sanitization.

Three added Chromium cases cover desktop/phone New pair/second-blend choices and
ordinary polling after a same-revision restart. The restart test delivers a
genuine newly initialized SceneService snapshot through a simulated HTTP route;
the actual user demo is never restarted. Active preview and playback are preserved,
Undo/Redo/activity reset, and a late retired-session snapshot is ignored. Native
supported-branch tool counts/names derive from the actual catalog; unsupported
Chromium does not establish native-host support.

## Native WebMCP limitation

Actual Work17 Chromium lacks `document.modelContext.registerTool` and correctly
reports unsupported with zero registered tools. Manual editing remains available.
No fake interface or model host is injected into real browser acceptance.
Mocked registration and real MCP clients test separate adapter/transport behavior;
neither proves native WebMCP execution or a live AI session. Validate that in the
intended supported top-level host as the [roadmap](ROADMAP.md) describes.

## Recovery and integration history

The six prepared 0.2.0 commits were restored unchanged from the size/hash-verified
downloaded bundle into an isolated Work17 checkout. Base:
`8d5eccdb86c128732d0216377a8bde708f19e026`; recovered head:
`460f6e6a367b68c561828b2d2d6238dfe98b7793`.

[PR #4](https://github.com/burhop/2Top/pull/4) integrated the tested 0.2.1 browser
fixes into dev at `260d853eac5070fe9d36c20b7d98dd7f39591f67`. Version 0.3.0
started from that dev head. [PR #5](https://github.com/burhop/2Top/pull/5) merged
0.3.0 at dev `21584c0ff85a7a9b838ff7e975c0ab9bd9b21e59`, whose post-merge CI
passed before 0.4.0 started. [PR #6](https://github.com/burhop/2Top/pull/6) merged 0.4.0 at
`af00fb452d1c62eb1a297d5cdb3eb77d8ecde954`; its post-merge CI passed before
0.5.0 started on a new feature branch. [PR #7](https://github.com/burhop/2Top/pull/7)
merged 0.5.0 at `4a07def243bcbeedbc19eb4832696d6875a0fde0`, whose post-merge CI
passed before 0.6.0 started. [PR #8](https://github.com/burhop/2Top/pull/8)
merged 0.6.0 at `87c24032573a5e2fe0da17724d6fc34b63ff117e`, whose post-merge CI
passed before 0.7.0 started. [PR #9](https://github.com/burhop/2Top/pull/9)
merged 0.7.0 at `bd8a0269991c72171af81ed77f2cb5849fd82ca8`, whose post-merge CI
passed before 0.7.1 started. Existing
history and unrelated work are preserved. Main, releases, deployment and
security/credential settings are outside these development updates.

The studio does not yet expose every historical primitive or composition command.
Exact continuity, physical simulation and native model-host interoperability are
not claimed. This milestone continues development rather than completing 2Top.
