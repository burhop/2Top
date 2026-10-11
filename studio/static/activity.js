/** Server-observed routes are transport evidence, never authenticated identity. */
export function sourceLabel(entry) {
  return {manual_http:'UI / HTTP',mcp_protocol:'MCP protocol',tool_http:'WebMCP / HTTP bridge',internal:'Internal service'}[entry?.source?.entrypoint] || 'Unverified source';
}
export function sourceKind(entry) {
  return ['manual_http','mcp_protocol','tool_http','internal'].includes(entry?.source?.entrypoint) ? entry.source.entrypoint : 'unknown';
}
export function committedEntries(scene, filter='all') {
  return [...(scene.history?.entries || [])].reverse().filter(entry=>filter==='all'||sourceKind(entry)===filter);
}
