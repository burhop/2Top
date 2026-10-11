# Static island blending in 0.5.0

Confluence composes two retained island fields using the existing
`RFunctionCurve` and `CurveField` engine. Union evaluates `min(f, g)`. Smooth
union evaluates `(f + g - sqrt((f - g)^2 + amount^2)) / 2`; amount 0 is union.
Amount is finite within 0..1, dimensionless, and ignored by Union. It is not a
Euclidean offset, physical radius or signed-distance blend. The island fields
remain dimensionless implicit functions, negative inside and zero on the shore.

## Editing and references

Schema 3 adds at most two blend records alongside at most sixteen source islands.
Each record references two distinct existing island IDs, with operation, amount,
name and style. Nested blend references are forbidden, so cycles are rejected.
Source pose tracks are forbidden while referenced; blends evaluate base shapes
at time 0 with procedural motion 0. Timeline/tide settings can still animate
unrelated islands, but do not animate these operands.

Sources retain their IDs, base parameters, styles and layer-list entries. A visible
blend replaces their separate filled artwork in the canvas/export view; source
guides and center handles help edit them. Hiding/removing the blend restores
separate source artwork according to source visibility. Source visibility does
not remove its field from a visible composition. Removing a blend never deletes
or modifies its sources. Source deletion is rejected while referenced; an atomic
batch can remove dependent blends before deleting a source.

The UI and adapters share `create_blend` (source_a/source_b, optional name,
operation, amount, style), `update_blend` (id plus changed fields), and
`delete_blend` (id). Normal revision/retry rules apply. Candidate-reference
validation occurs before persistence/commit, including after a batch. Updates
retain unspecified values. Undo/redo restores complete source/composition edits.

Schema-1/2 documents migrate with empty blends, preserving base parameters,
views, animation and existing tracks. Older persisted local scenes also migrate.
The next save uses schema 3, which older studios cannot read; preserve originals
when exchanging with them. Existing example files remain in their old schemas.
The new ready-to-open demo is `examples/tidal_atlas_confluence.json`.

## Approximation and budgets

`geometry/static_blend.py` adds reusable fixed-diagonal marching triangles over
an evaluated grid. `studio/static/static-blend.js` mirrors the engine's field
formula and this sampling algorithm. Python/JavaScript tests compare values,
bounds, complete closed loops and the demo's two-component-to-one transition.
The Python field exposes the existing BaseField/RFunctionCurve interfaces and
the real SceneManager/GraphicsBackend bridge; that backend may sample at a
different resolution from the browser.

Browser previews use 128 cells per grid dimension and up to 16 field levels;
active gestures use a 64-cell preview, followed by committed resampling. A six-entry
geometry cache prevents resampling unchanged static compositions during playback.
The reusable sampler accepts 24..192 cells and at most 16 levels. Levels are
implicit field values derived from the studio's normalized contour levels,
not distances or guaranteed equally spaced physical terraces.

Edges interpolate linearly on a fixed grid diagonal. Closed loops use even-odd
filling to preserve separate components/holes. Open, clipped or zero-area fragments
are omitted and counted. Conservative bounds enclose the supported outer shore;
exact-level vertices use shared vertex identities. Very small necks/features can
vanish or change connectivity at finite resolution, and a tie/saddle can remain
grid-dependent. No exact topology, G1/G2, manufacturing or offset guarantee is
made. Union has nonsmooth joins; smooth union also inherits the source fields'
regularity and can expand their zero-level region.

Native WebMCP execution remains unverified; mock registration is adapter coverage,
not a supported browser/model-host session.
