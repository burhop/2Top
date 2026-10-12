# Composition layers in 0.6.0

The existing islands and static blends are the layers. Schema 4 adds one bounded
`layer_order` list containing every island and blend ID exactly once, back to
front. It introduces no parents, transforms, nested operators or general scene
graph. The Composition list displays the reverse order: its top row is frontmost.
Arrow buttons bring a layer forward or send it backward. Select a row to change
its palette or opacity, or use its visibility button. Native buttons support
Enter/Space; range controls support Home/End and arrow keys. Undo/redo restores
whole order/style edits. The Glasswater layered study shows a translucent veil,
a gold confluence and an underlying lagoon field.

## Shared editing and migration

`reorder_layers` accepts `order`, the complete back-to-front ID list. Missing,
unknown or repeated IDs fail before persistence. Existing `set_style` now accepts
island or blend IDs with palette, visible and/or opacity (0.05..1); omitted style
values remain unchanged. `select` supports both kinds and `get_selection` returns
their complete records. Shape/pose controls apply only to island selections;
blend selection activates its existing composition controls. All 19 tools share
revision guards, bounded retry keys, atomic batches and undo through UI/MCP/
WebMCP. Geometry creation appends a frontmost layer; deletion removes its ID.

Schema 1/2/3 recipes migrate to their original drawing order: islands in their
stored array order, followed by blends in their stored array order. Existing
styles, base fields, tracks and static dependencies remain unchanged. Old files
are not rewritten on import; the next save writes schema 4. Older studios cannot
read that schema, so retain original recipes for exchanging with them. Schema 4
requires an explicit complete order; it does not repair a malformed order.

## Visibility, selection and sources

A visible blend consumes its sources' separate filled artwork, regardless of
their layer order or source visibility. The source records keep their positions
so hiding/removing the blend restores their artwork according to each source's
visibility. Hidden source fields still contribute to the blend, and a source
cannot be deleted while any blend references it, including a hidden blend.
Remove dependent blends first, individually or in an atomic batch. Nested,
missing, cyclic and animated source references remain rejected.

Canvas artwork selection checks frontmost visible artwork first, with even-odd
hit testing for compound contours. Hidden and consumed source artwork is excluded.
For an explicit source edit, select its row or use Edit A/B. The selected source
shows a dashed guide and center handle even when its artwork is hidden or consumed;
the inspector explains its dependencies and blocks deletion. That explicit handle
is an editing overlay, not restored artwork. Source guides and selection handles
are omitted from exports. Turn handles off to remove editing overlays.

## Compositing and engine limits

Each complete layer is drawn opaquely into a reusable buffer, then composited once
over preceding artwork using its opacity. This prevents nested terraces from
accumulating alpha. SVG uses the same order and group opacity; canvas/PNG use the
same compositing code. Small raster rounding differences are expected. Shadows
belong to their layer; guides and selection handles are editing overlays.

Ordering/styles do not mutate source parameters, bounds, field evaluation or
static blend alpha. The existing RFunctionCurve/CurveField and SceneManager bridge
receive the same geometry in layer order with layer styling. Its contour-only
rendering is not a pixel-identical substitute for the studio's artistic terraces.
The finite-grid, dimensionless-field and non-exact-topology limits in
[static blending](static_blending.md) continue to apply. Native WebMCP host
execution remains a separate unverified capability.

## Reliability semantics in 0.7.1

A batch can set the order for its final surviving layers before deleting an
omitted island/blend. Final recipe invariants must still hold; malformed survivors
are rejected atomically. Each operation's normal preconditions remain in force.
Standalone order edits require the complete current layer list.

Blend composition is an explicit local editor choice: New pair or another blend
does not change canvas selection. A new canvas/shared selection of a blend
synchronizes the editor, but an existing unchanged selection does not overwrite
the user's dropdown choice. Creation selects the newly created editor record;
normal layer/canvas selection behavior remains shared and reversible.
