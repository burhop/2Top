/** Browser WebMCP is a progressive enhancement of the existing command API.
 * The browser provides document.modelContext. We never fabricate it or imply
 * that registering tools connects an AI model.
 */
let registration;
const sceneListeners = new Set();
const statusListeners = new Set();
const approvedNames = new Set([
  "get_scene", "get_selection", "create_geometry", "update_geometry",
  "delete_geometry", "set_style", "reorder_layers", "set_view", "select", "batch", "undo",
  "redo", "load_recipe", "set_keyframe", "delete_keyframe", "edit_keyframe", "create_blend", "update_blend", "delete_blend",
]);

function notifyListener(listener, detail) {
  try { listener(detail); }
  catch (error) { console.warn("Studio observer failed after receiving an update:", error); }
}

function setStatus(detail) {
  window.tidalWebMCPStatus = Object.freeze({ ...detail });
  window.dispatchEvent(new CustomEvent("tidal:webmcp-status", { detail }));
  for (const listener of statusListeners) notifyListener(listener, detail);
  return detail;
}

function reportScene(scene) {
  if (!scene) return;
  window.dispatchEvent(new CustomEvent("tidal:scene", { detail: scene }));
  for (const listener of sceneListeners) notifyListener(listener, scene);
}

async function jsonRequest(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin", cache: "no-store", ...options,
  });
  let result;
  try { result = await response.json(); }
  catch { throw new Error(`Studio returned an unreadable response (${response.status}).`); }
  if (!response.ok || result?.ok === false || result?.error) {
    const error = new Error(result?.error?.message || `Studio request failed (${response.status}).`);
    error.details = result?.error || result;
    throw error;
  }
  return result;
}

/** Idempotent registration; callbacks may be attached before or after startup. */
export function registerWebMCP({ onScene, onStatus } = {}) {
  if (typeof onScene === "function") sceneListeners.add(onScene);
  if (typeof onStatus === "function") {
    statusListeners.add(onStatus);
    if (window.tidalWebMCPStatus) notifyListener(onStatus, window.tidalWebMCPStatus);
  }
  if (registration) return registration;
  registration = (async () => {
    const context = document.modelContext;
    if (window.top !== window.self) {
      return setStatus({ supported: false, registered: 0, error: null, reason: "top-level-required" });
    }
    if (typeof context?.registerTool !== "function") {
      return setStatus({ supported: false, registered: 0, error: null, reason: "browser-unsupported" });
    }
    const lifetime = new AbortController();
    let registered = 0;
    try {
      const catalog = await jsonRequest("/api/tools");
      const definitions = Array.isArray(catalog) ? catalog : catalog.tools;
      if (!Array.isArray(definitions)) throw new Error("Studio tool catalog is unavailable.");
      for (const definition of definitions) {
        if (!approvedNames.has(definition.name)) continue;
        await context.registerTool({
          name: definition.name,
          description: definition.description,
          inputSchema: definition.inputSchema,
          annotations: { readOnlyHint: Boolean(definition.annotations?.readOnlyHint) },
          execute: async (args = {}, options = {}) => {
            if (!args || typeof args !== "object" || Array.isArray(args)) {
              throw new Error("Tool arguments must be an object matching the input schema.");
            }
            // Never fill a missing revision or replay a failed mutation: the
            // caller must make its intent against the actual shared revision.
            const result = await jsonRequest(`/api/tools/${definition.name}`, {
              method: "POST",
              headers: { "Content-Type": "application/json", "X-Studio-Actor": "webmcp" },
              body: JSON.stringify(args),
              signal: options.signal,
            });
            reportScene(result.scene);
            return result;
          },
        }, { signal: lifetime.signal });
        registered += 1;
      }
      return setStatus({ supported: true, registered, error: null });
    } catch (error) {
      lifetime.abort(); // Roll back partial registrations per the current API.
      return setStatus({ supported: true, registered: 0, error: error.message || String(error) });
    }
  })();
  return registration;
}

// Imperative registration in the actual top-level application document.
registerWebMCP();
