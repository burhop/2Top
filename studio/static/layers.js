/** Bounded layer policy; retained sources never become a second scene graph. */
export const allLayers = state => [...(state?.objects || []), ...(state?.blends || [])];
export function orderedLayers(state) {
  const items = allLayers(state), byId = new Map(items.map(item => [item.id, item]));
  return (state.layer_order || items.map(item => item.id)).map(id => byId.get(id));
}
export function sourceBlends(state, id, visibleOnly = false) {
  return (state.blends || []).filter(b => (!visibleOnly || b.style.visible) && [b.source_a, b.source_b].includes(id));
}
export function visibleLayers(state) {
  return orderedLayers(state).filter(item => item.style.visible && !sourceBlends(state, item.id, true).length);
}
export function compositeLayer(target, buffer, opacity, draw) {
  // Draw opaque internal terraces, then apply group alpha once over prior art.
  const context = buffer.getContext('2d');
  context.setTransform(1, 0, 0, 1, 0, 0); context.clearRect(0, 0, buffer.width, buffer.height);
  context.setTransform(target.getTransform());
  draw(context);
  target.save(); target.setTransform(1, 0, 0, 1, 0, 0);
  target.globalAlpha = opacity; target.drawImage(buffer, 0, 0); target.restore();
}
