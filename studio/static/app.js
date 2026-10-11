import { generateContours, LOOP_DURATION, PARAMETER_BOUNDS } from './geometry.js';
import { sampleParameters, POSE_FIELDS } from './choreography.js';
import { demoRecipe } from './demo.js';
import { blendContours } from './static-blend.js';
import { blendDemoRecipe } from './blend-demo.js';
import { allLayers, orderedLayers, visibleLayers, sourceBlends, compositeLayer } from './layers.js';
import { layeredDemoRecipe } from './layered-demo.js';
import {sourceLabel,sourceKind,committedEntries} from './activity.js';
let activityKey;
let dialogGeneration=0;

const $ = (id) => document.getElementById(id);
const WORLD = { width: 1000, height: 700 };
const DURATION = LOOP_DURATION;
const paletteColors = {
  ember: ['#f0a088', '#dd786d', '#f3bc89', '#a54e52'],
  lagoon: ['#8ed0c6', '#51a6a1', '#acd7b6', '#3f777b'],
  aurora: ['#d7ba75', '#ad8f55', '#e5c795', '#7e875f'],
  mono: ['#d9dfcf', '#98afa6', '#edf0d9', '#6c8981'],
};
const compositingBuffers = new WeakMap();
let layerFocus;
function layerBuffer(target) {
  if(!compositingBuffers.has(target))compositingBuffers.set(target,document.createElement('canvas'));
  const buffer=compositingBuffers.get(target);
  if(buffer.width!==target.canvas.width)buffer.width=target.canvas.width;
  if(buffer.height!==target.canvas.height)buffer.height=target.canvas.height;
  return buffer;
}
const presets = {
  demo: demoRecipe,
  midnight: {
    title: 'Midnight archipelago',
    objects: [
      island('island-coral', 'Coral island', 340, 365, 224, 1.15, -30, 3, .74, 0, 'ember'),
      island('island-lagoon', 'Lagoon island', 692, 344, 208, 1.13, 138, 4, .64, 2.2, 'lagoon'),
      island('island-drift', 'Golden drift', 686, 581, 84, 1.65, -18, 3, .41, 4.5, 'aurora'),
    ],
    view: { zoom: 1, pan_x: 0, pan_y: 0, grid: false, contours: 28 },
    animation: { playing: false, time: 0, speed: 1, motion: .45 },
  },
  atoll: {
    title: 'Coral atoll',
    objects: [
      island('atoll-coral', 'Terraced atoll', 490, 335, 287, 1.5, -14, 4, .84, 1.2, 'ember'),
      island('atoll-reef', 'Outer reef', 777, 470, 101, 1.3, -32, 3, .65, 2.5, 'aurora'),
      island('atoll-pearl', 'Lagoon pearl', 252, 489, 81, .87, 15, 3, .45, .8, 'lagoon'),
    ],
    view: { zoom: 1, pan_x: 0, pan_y: 0, grid: false, contours: 34 },
    animation: { playing: false, time: 0, speed: .75, motion: .6 },
  },
  ribbons: {
    title: 'Tidal ribbons',
    objects: [
      island('ribbon-north', 'Northern current', 400, 231, 177, 2.3, -25, 4, .85, .4, 'lagoon'),
      island('ribbon-south', 'Southern current', 612, 477, 173, 2.4, -27, 3, .8, 2.8, 'ember'),
      island('ribbon-drift', 'Quiet current', 206, 489, 89, 1.7, 35, 3, .55, 4.2, 'aurora'),
    ],
    view: { zoom: 1, pan_x: 0, pan_y: 0, grid: false, contours: 25 },
    animation: { playing: false, time: 0, speed: 1, motion: .72 },
  },
};

function island(id, name, x, y, radius, elongation, rotation, lobes, warp, phase, palette) {
  return { id, name, type: 'island', parameters: { x, y, radius, elongation, rotation, lobes, warp, phase }, style: { palette, opacity: 1, visible: true } };
}
const canvas = $('art-canvas');
const ctx = canvas.getContext('2d', { alpha: false });
let scene = null;
let preview = null;
let dragging = null;
let gesture = null;
let showHandles = true;
let editMotionPath = false;
let activeBlendId;
let sourceGuides = true;
const blendCache = new Map();
let activeTool = 'select';
let busy = 0;
let online = false;
let destroyed = false;
let lastFrame = 0;
let renderDirty = true;
let lastSceneClock = performance.now();
let renderedPaths = [];
let toastTimer;
let copyTimer;
let webmcpStatus = window.tidalWebMCPStatus || { supported: false, registered: 0 };
let size = { width: 1, height: 1, dpr: 1 };
let transform = { scale: 1, x: 0, y: 0 };
let commandQueue = Promise.resolve();

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (s) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
const clone = (value) => JSON.parse(JSON.stringify(value));
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
const current = () => preview || scene;
const selectedLayer = (state = current()) => allLayers(state).find(item => state?.selection?.includes(item.id));
const selected = (state = current()) => state?.objects.find((object) => state.selection?.includes(object.id));
function getTime(state = current()) {
  if (!state) return 0;
  if (!state.animation?.playing || state === preview) return state.animation?.time || 0;
  return ((state.animation.time || 0) + (performance.now() - lastSceneClock) / 1000 * (state.animation.speed || 1)) % DURATION;
}
function setConnected(connected, error = '') {
  online = connected;
  $('connection-dot').className = `connection-dot ${connected ? 'connected' : 'error'}`;
  $('connection-label').textContent = connected ? 'Scene service connected' : 'Scene service offline';
  $('save-status').className = `save-status ${connected ? 'ok' : 'error'}`;
  $('save-status').lastChild.textContent = connected ? (busy ? 'Applying change…' : 'Scene synchronized') : (error || 'Connection interrupted');
  const locked = busy > 0 || !scene;
  for (const id of ['play-button', 'speed-button', 'add-island-button', 'add-tool', 'preset-select', 'fit-button', 'timeline-input', 'contours-input', 'tide-input']) $(id).disabled = locked;
  for (const id of ['radius-input', 'stretch-input', 'organic-input', 'rotation-input', 'duplicate-button', 'remove-button']) $(id).disabled = locked || !selected();
  $('demo-button').disabled = locked;
  if (scene) { setBlendingLocks(current()); setLayerLocks(current()); }
  updateKeyframeControls(current(), getTime());
  $('undo-button').disabled = locked || !scene?.history?.can_undo;
  $('redo-button').disabled = locked || !scene?.history?.can_redo;
}
function toast(message, error = false) {
  $('toast').textContent = message;
  $('toast').classList.toggle('error', error);
  $('toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, error ? 6500 : 3200);
}
function acceptScene(next, force = false) {
  if (!next || !Array.isArray(next.objects)) throw new Error('The scene service returned an invalid scene.');
  if (scene && next.document_id === scene.document_id && next.revision < scene.revision) return;
  const changed = !scene || next.document_id !== scene.document_id || next.revision !== scene.revision;
  if (!changed && !force) return;
  scene = next;
  lastSceneClock = performance.now();
  if (!gesture && !dragging) preview = null;
  renderDirty = true;
  updateUI();
  $('canvas-loading').hidden = true;
  $('canvas-error').hidden = true;
  window.dispatchEvent(new CustomEvent('tidal:ui-scene', { detail: scene }));
}
async function refresh({ initial = false } = {}) {
  try {
    const response = await fetch('/api/scene', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Scene service responded ${response.status}.`);
    const next = await response.json();
    if (!gesture && !dragging && !busy) acceptScene(next);
    setConnected(true);
    return next;
  } catch (error) {
    setConnected(false);
    if (initial || !scene) {
      $('canvas-loading').hidden = true;
      $('canvas-error').hidden = false;
      $('canvas-error-message').textContent = `${error.message} Run the studio service, then try again.`;
    }
    return null;
  }
}
function command(op, args = {}, options = {}) {
  const task = async () => {
    if (!scene) throw new Error('Open the scene before making an edit.');
    // A separately requested transaction supersedes any uncommitted gesture.
    if (dragging) endDrag(true);
    if (gesture) cancelGesture();
    busy += 1;
    setConnected(online);
    try {
      const response = await fetch('/api/command', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...args, op, expected_revision: options.expectedRevision ?? scene.revision, request_id: crypto.randomUUID() }),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        const error = new Error(result.error?.message || `The edit could not be saved (${response.status}).`);
        error.code = result.error?.code;
        throw error;
      }
      preview = null;
      acceptScene(result.scene, true);
      setConnected(true);
      return result;
    } catch (error) {
      preview = null;
      renderDirty = true;
      updateUI();
      const fresh = await refresh();
      if (fresh) acceptScene(fresh, true);
      if (!options.quiet) toast(error.code === 'revision_conflict' ? 'The scene changed elsewhere. Your preview was cleared; try the edit again.' : error.message, true);
      throw error;
    } finally {
      busy -= 1;
      setConnected(online);
    }
  };
  const result = commandQueue.then(task, task);
  commandQueue = result.catch(() => {});
  return result;
}
function run(op, args = {}, options = {}) { return command(op, args, options).catch(() => null); }
window.tidalStudio = { getScene: () => scene ? clone(scene) : null, getPose: (id, time = getTime()) => { const object = scene?.objects.find(o => o.id === id); return object ? sampleParameters(object.parameters, object.keyframes || [], time) : null; }, command, refresh };
window.addEventListener('tidal:scene', (event) => { if (!gesture && !dragging) acceptScene(event.detail?.scene || event.detail); });
window.addEventListener('tidal:webmcp-status', (event) => { webmcpStatus = event.detail; updateAgentStatus(); });

function updateUI() {
  if (!scene) return;
  const state = current();
  const object = selected(state);
  updateBlending(state);
  $('revision-label').textContent = `REV ${String(scene.revision).padStart(3, '0')}`;
  $('undo-button').disabled = !scene.history?.can_undo;
  $('redo-button').disabled = !scene.history?.can_redo;
  $('island-count').textContent = allLayers(state).length;
  $('artwork-name').textContent = state.title || 'Untitled archipelago';
  $('artwork-description').textContent = `${visibleLayers(state).length} artwork layers · ${state.view?.contours || 24} contours · one living field`;
  $('selected-name').textContent = object?.name || 'Select an island';
  $('duplicate-button').disabled = !object;
  $('remove-button').disabled = !object || sourceBlends(state,object.id).length > 0;
  updateLayers(state);
  updatePoseControls(state, getTime(state));
  updateKeyframes(state);
  $('contours-input').value = state.view?.contours || 24;
  $('contours-output').textContent = state.view?.contours || 24;
  $('tide-input').value = state.animation?.motion ?? .45;
  $('tide-output').textContent = `${Math.round((state.animation?.motion ?? .45) * 100)}%`;
  $('speed-button').textContent = `${state.animation?.speed || 1}×`;
  const palettePatterns = { tidal: ['ember', 'lagoon', 'aurora'], ember: ['ember', 'aurora', 'ember'], glacier: ['lagoon', 'mono', 'lagoon'] };
  document.querySelectorAll('.palette-option').forEach((button) => {
    const pattern = palettePatterns[button.dataset.palette];
    const matches = state.objects.length > 0 && state.objects.every((item, index) => item.style.palette === pattern[index % pattern.length]);
    button.classList.toggle('selected', matches);
    button.setAttribute('aria-pressed', String(matches));
  });
  progress($('contours-input')); progress($('tide-input'));
  const matchingPreset = Object.keys(presets).find((key) => presets[key].title === state.title);
  if (matchingPreset) $('preset-select').value = matchingPreset;
  $('play-button').setAttribute('aria-label', state.animation?.playing ? 'Pause animation' : 'Play animation');
  $('play-button').innerHTML = state.animation?.playing ? '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M5 4h3v10H5zm5 0h3v10h-3z"/></svg>' : '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M6 3.5 14 9l-8 5.5z"/></svg>';
  $('motion-label').textContent = state.animation?.playing ? 'LIVE COMPOSITION' : 'COMPOSITION / PAUSED';
  $('recipe-code').textContent = JSON.stringify(recipe(state), null, 2);
  const entries = scene.history?.entries || [];
  $('action-list').innerHTML = entries.length ? [...entries].reverse().slice(0,4).map(entry=>`<li class="action-item"><span class="action-icon">${sourceKind(entry)==='mcp_protocol'?'✧':'↳'}</span><div class="action-text"><strong>${esc(entry.summary||'Committed edit')}</strong><span>${esc(sourceLabel(entry))} · revision ${esc(entry.revision)}</span></div><span class="action-time">#${entry.revision}</span></li>`).join('') : '<li class="empty-activity">Your edits and client calls appear here.</li>';
  updateActivity();
  updateAgentStatus();
  setConnected(online);
}
function setLayerLocks(state) {
  const locked=busy>0||Boolean(dragging||gesture), layer=selectedLayer(state), object=selected(state);
  $('layer-palette').disabled=locked||!layer;
  $('layer-opacity').disabled=busy>0||Boolean(dragging)||Boolean(gesture&&gesture.id!=='layer-opacity')||!layer;
  $('layer-demo-button').disabled=locked;
  $('remove-button').disabled=locked||!object||sourceBlends(state,object.id).length>0;
  document.querySelectorAll('[data-layer-action]').forEach(button=>{const index=state.layer_order.indexOf(button.dataset.id);button.disabled=locked||(button.dataset.layerAction==='forward'&&index===state.layer_order.length-1)||(button.dataset.layerAction==='backward'&&index===0);});
  if(!locked&&layerFocus) {
    const button=Array.from(document.querySelectorAll('[data-layer-action]')).find(b=>b.dataset.id===layerFocus.id&&b.dataset.layerAction===layerFocus.action);
    if(document.activeElement===document.body&&!button?.disabled)button?.focus({preventScroll:true});
    layerFocus=null;
  }
}
function updateLayers(state) {
  const layer=selectedLayer(state), focus=document.activeElement?.closest('[data-layer-action]');
  const focusId=focus?.dataset.id,focusAction=focus?.dataset.layerAction;
  $('layer-list').innerHTML=[...orderedLayers(state)].reverse().map(o=>{
    const sources=sourceBlends(state,o.id),consumed=sources.some(b=>b.style.visible),active=state.selection.includes(o.id);
    const note=o.parameters ? (sources.length ? `Source of ${sources.map(b=>b.name).join(', ')}${consumed?' · not drawn separately':''}`:'Island') : `Blend of ${state.objects.find(a=>a.id===o.source_a).name} + ${state.objects.find(a=>a.id===o.source_b).name}`;
    return `<div class="layer-entry${active?' selected':''}${!o.style.visible?' hidden-layer':''}"><div class="layer-row"><button class="layer-select" data-layer-action="select" data-id="${esc(o.id)}" aria-label="Select ${esc(o.name)}" aria-pressed="${active}"><span class="layer-swatch" style="color:${paletteColors[o.style.palette][0]}"></span><span class="layer-name">${esc(o.name)}</span><span class="layer-kind">${o.parameters?'ISLAND':'BLEND'}</span></button><button class="layer-eye" data-layer-action="visibility" data-id="${esc(o.id)}" data-visibility="${esc(o.id)}" aria-label="${o.style.visible?'Hide':'Show'} ${esc(o.name)}" aria-pressed="${o.style.visible}">${o.style.visible?'◉':'◌'}</button><button class="layer-move" data-layer-action="forward" data-id="${esc(o.id)}" aria-label="Bring ${esc(o.name)} forward">↑</button><button class="layer-move" data-layer-action="backward" data-id="${esc(o.id)}" aria-label="Send ${esc(o.name)} backward">↓</button></div><p class="layer-dependency">${esc(note)}</p></div>`;
  }).join('');
  if(focusId)Array.from(document.querySelectorAll('[data-layer-action]')).find(b=>b.dataset.id===focusId&&b.dataset.layerAction===focusAction)?.focus({preventScroll:true});
  $('layer-style-name').textContent=layer?.name||'Select a layer';
  if(gesture?.id!=='layer-opacity')$('layer-opacity').value=Math.round((layer?.style.opacity??1)*100);
  $('layer-opacity-output').textContent=`${$('layer-opacity').value}%`;progress($('layer-opacity'));
  $('layer-palette').value=layer?.style.palette||'ember';
  const sources=layer?.parameters?sourceBlends(state,layer.id):[];
  $('layer-status').textContent=!layer?'Top row is frontmost. Move a layer with its arrow buttons.':!layer.parameters?'Select Edit A/B below Island confluence to edit its retained sources.':sources.length?`Source of ${sources.map(b=>b.name).join(', ')}. ${!layer.style.visible?'Hidden artwork; ':sources.some(b=>b.style.visible)?'Not drawn separately; ':''}the dashed guide and center handle let you edit this source. Remove its blends before deleting it.`:!layer.style.visible?'Hidden layer. The selected center handle lets you edit it without showing its artwork.':'Use the canvas or Shape & field to edit this island.';
  setLayerLocks(state);
}
$('layer-palette').addEventListener('change',()=>{const layer=selectedLayer(scene);if(layer)run('set_style',{id:layer.id,style:{palette:$('layer-palette').value}});});
$('layer-opacity').addEventListener('input',()=>{
  const layer=selectedLayer(scene);if(!layer||busy||dragging||(gesture&&gesture.id!=='layer-opacity'))return;
  if(!gesture){gesture={id:'layer-opacity',revision:scene.revision,layerId:layer.id};preview=clone(scene);}
  allLayers(preview).find(o=>o.id===gesture.layerId).style.opacity=Number($('layer-opacity').value)/100;
  $('layer-opacity-output').textContent=`${$('layer-opacity').value}%`;progress($('layer-opacity'));renderDirty=true;
});
$('layer-opacity').addEventListener('change',()=>{if(gesture?.id!=='layer-opacity')return;const saved=gesture;gesture=null;run('set_style',{id:saved.layerId,style:{opacity:Number($('layer-opacity').value)/100}},{expectedRevision:saved.revision});});
$('layer-opacity').addEventListener('pointercancel',()=>cancelGesture());
function progress(input) { input.style.setProperty('--progress', `${(Number(input.value) - Number(input.min)) / (Number(input.max) - Number(input.min)) * 100}%`); }
function updateAgentStatus() {
  updateActivity();
  const registered = Number(webmcpStatus?.registered) || 0;
  $('agent-hint').textContent = registered > 0 ? `${registered} browser tools registered. Agent edits appear in this same scene.` : 'Connect an MCP client or a WebMCP-enabled browser to edit this canvas.';
}
function recipe(state = scene) {
  return { schema_version: 4, layer_order: clone(state.layer_order), title: state.title, objects: clone(state.objects), blends: clone(state.blends || []), view: clone(state.view), animation: { ...state.animation, time: getTime(state), playing: false } };
}

function updateBlending(state) {
  const blends = state.blends || [], staticObjects = state.objects.filter(o => !o.keyframes?.length);
  const selectedBlend=blends.find(b=>state.selection.includes(b.id));if(selectedBlend)activeBlendId=selectedBlend.id;
  if (activeBlendId === undefined || (activeBlendId && !blends.some(b => b.id === activeBlendId))) activeBlendId = blends[0]?.id || '';
  const blend = blends.find(b => b.id === activeBlendId), locked = busy > 0 || Boolean(gesture || dragging);
  $('blend-select').innerHTML = '<option value="">New pair</option>' + blends.map(b=>`<option value="${esc(b.id)}">${esc(b.name)}</option>`).join('');
  $('blend-select').value = activeBlendId;
  for (const [id, field, fallback] of [['blend-source-a','source_a',0],['blend-source-b','source_b',1]]) {
    const previous = $(id).value;
    $(id).innerHTML = staticObjects.map(o=>`<option value="${esc(o.id)}">${esc(o.name)}</option>`).join('');
    $(id).value = blend?.[field] || (staticObjects.some(o=>o.id===previous) ? previous : staticObjects[fallback]?.id || '');
    $(id).disabled = locked;
  }
  if (blend && gesture?.id !== 'blend-amount') { $('blend-operation').value = blend.operation; $('blend-amount-input').value = blend.amount; }
  $('blend-amount-output').textContent = Number($('blend-amount-input').value).toFixed(2);
  $('apply-blend').textContent = blend ? 'Apply blend' : 'Create blend';
  $('apply-blend').disabled = locked || staticObjects.length < 2 || (!blend && blends.length >= 2) || $('blend-source-a').value === $('blend-source-b').value;
  $('delete-blend').disabled = locked || !blend;
  $('show-blend').checked = blend?.style.visible ?? true; $('show-blend').disabled = locked || !blend;
  for (const id of ['blend-select','blend-operation','blend-amount-input','edit-source-a','edit-source-b']) $(id).disabled = locked || staticObjects.length < 2;
  $('blend-amount-input').disabled ||= $('blend-operation').value === 'union';
}
function setBlendingLocks(state) {
  const blends=state.blends||[],blend=blends.find(b=>b.id===activeBlendId),count=state.objects.filter(o=>!o.keyframes?.length).length;
  const locked=busy>0||Boolean(gesture||dragging),a=$('blend-source-a').value,b=$('blend-source-b').value;
  for(const id of ['blend-select','blend-source-a','blend-source-b','blend-operation','edit-source-a','edit-source-b'])$(id).disabled=locked||count<2;
  $('blend-amount-input').disabled=busy>0||Boolean(dragging)||Boolean(gesture&&gesture.id!=='blend-amount')||count<2||$('blend-operation').value==='union';
  $('apply-blend').disabled=locked||!a||!b||a===b||(!blend&&blends.length>=2);
  $('delete-blend').disabled=locked||!blend;$('show-blend').disabled=locked||!blend;
  $('blend-demo-button').disabled=locked;
}
function blendArgs() { return { source_a: $('blend-source-a').value, source_b: $('blend-source-b').value, operation: $('blend-operation').value, amount: Number($('blend-amount-input').value) }; }
$('blend-select').addEventListener('change', event => { activeBlendId = event.target.value; updateUI(); });
for (const id of ['blend-source-a','blend-source-b','blend-operation']) $(id).addEventListener('change', () => { $('apply-blend').disabled = busy > 0 || $('blend-source-a').value === $('blend-source-b').value || (!activeBlendId && (scene.blends || []).length >= 2); $('blend-amount-input').disabled = $('blend-operation').value === 'union'; });
$('apply-blend').addEventListener('click', () => {
  if (!scene || busy) return;
  const args = blendArgs();
  const target = activeBlendId;
  run(target ? 'update_blend' : 'create_blend', target ? {id:target,...args} : args).then(result=>{if(result){activeBlendId=target || result.scene.blends.at(-1).id;updateUI();}});
});
$('delete-blend').addEventListener('click', () => { if(activeBlendId)run('delete_blend',{id:activeBlendId}); });
$('show-blend').addEventListener('change', () => { if(activeBlendId)run('update_blend',{id:activeBlendId,style:{visible:$('show-blend').checked}}); });
$('source-guides').addEventListener('change', () => { sourceGuides=$('source-guides').checked;renderDirty=true; });
for(const [button,input] of [['edit-source-a','blend-source-a'],['edit-source-b','blend-source-b']]) $(button).addEventListener('click',()=>{if($(input).value)run('select',{ids:[$(input).value]});});
$('blend-amount-input').addEventListener('input', () => {
  $('blend-amount-output').textContent = Number($('blend-amount-input').value).toFixed(2);
  if (!activeBlendId || busy || dragging) return;
  if (!gesture) { gesture = {id:'blend-amount',revision:scene.revision,blendId:activeBlendId};preview=clone(scene); }
  preview.blends.find(b=>b.id===gesture.blendId).amount=Number($('blend-amount-input').value);renderDirty=true;
});
$('blend-amount-input').addEventListener('change',()=>{if(!gesture||gesture.id!=='blend-amount')return;const saved=gesture;gesture=null;run('update_blend',{id:saved.blendId,amount:Number($('blend-amount-input').value)},{expectedRevision:saved.revision});});
$('blend-amount-input').addEventListener('pointercancel',()=>cancelGesture());
$('blend-demo-button').addEventListener('click',()=>run('load_recipe',{recipe:clone(blendDemoRecipe)}).then(result=>{if(result){activeBlendId=result.scene.blends[0]?.id||'';updateUI();}}));

function linkedSources(state, visibleOnly = false) { return new Set((state.blends || []).filter(b=>!visibleOnly||b.style.visible).flatMap(b=>[b.source_a,b.source_b])); }
function artworkLayers(state, time, previewGrid = false) {
  const linked = linkedSources(state), consumed = linkedSources(state,true), byId = new Map(state.objects.map(o=>[o.id,o]));
  const layers = state.objects.filter(o=>o.style.visible!==false&&!consumed.has(o.id)).map(object=>({object,layers:generateContours(sampleParameters(object.parameters,object.keyframes||[],time),linked.has(object.id)?0:time,linked.has(object.id)?0:state.animation.motion,state.view.contours,180).map((path,i)=>({paths:[path],omitted:0,level:i}))}));
  for(const object of state.blends || []) {
    if(!object.style.visible)continue;
    const first=byId.get(object.source_a),second=byId.get(object.source_b),grid=previewGrid?64:128;
    const fingerprint=JSON.stringify([first.parameters,second.parameters,object.operation,object.amount,state.view.contours,grid]);
    if(!blendCache.has(fingerprint)) {
      if(blendCache.size>=6)blendCache.delete(blendCache.keys().next().value);
      blendCache.set(fingerprint,blendContours(first.parameters,second.parameters,object.operation,object.amount,state.view.contours,grid));
    }
    layers.push({object,layers:blendCache.get(fingerprint)});
  }
  const byLayer = new Map(layers.map(item=>[item.object.id,item]));
  return orderedLayers(state).filter(item=>byLayer.has(item.id)).map(item=>byLayer.get(item.id));
}
function pathFromLoops(loops) { const path=new Path2D();for(const points of loops){if(!points.length)continue;path.moveTo(...points[0]);for(let i=1;i<points.length;i++)path.lineTo(...points[i]);path.closePath();}return path; }

function authoredTime(state = scene) {
  const time = getTime(state), phase = time <= DURATION ? time : time % DURATION;
  return state.animation.playing ? Math.round(phase * 100) / 100 : phase;
}
function poseValues(parameters) { return Object.fromEntries(POSE_FIELDS.map(name => [name, parameters[name]])); }
function trackObject(state) {
  const object = selected(state);
  // A gesture suppresses preview keys so its edited pose can be drawn directly.
  return object ? scene.objects.find(o => o.id === object.id) : null;
}
function updatePoseControls(state, time) {
  const object = selected(state);
  const p = object ? sampleParameters(object.parameters, object.keyframes || [], time) : null;
  for (const [id, field, format] of [
    ['radius', 'radius', n => `${Math.round(n)} px`], ['stretch', 'elongation', n => `${n.toFixed(2)}×`],
    ['organic', 'warp', n => `${Math.round(n * 100)}%`], ['rotation', 'rotation', n => `${Math.round(n)}°`],
  ]) {
    $(id + '-input').disabled = busy > 0 || !object;
    if (p) $(id + '-input').value = p[field];
    $(id + '-output').textContent = p ? format(p[field]) : '—';
    progress($(id + '-input'));
  }
}
function updateKeyframeControls(state, time) {
  const object = state && scene ? trackObject(state) : null;
  const key = object?.keyframes?.find(k => Math.abs(k.time - time) < 1e-7);
  const locked = busy > 0 || !object || Boolean(gesture || dragging);
  $('capture-keyframe').disabled = locked || linkedSources(scene).has(object?.id) || (!key && object.keyframes.length >= 24);
  $('delete-keyframe').disabled = locked || !key || Boolean(state?.animation.playing);
  $('keyframe-easing').disabled = locked;
  $('motion-path-button').disabled = locked || !object?.keyframes?.length;
  $('motion-path-button').setAttribute('aria-pressed', String(editMotionPath));
  $('key-time-input').disabled = locked || !key || Boolean(state?.animation.playing);
  $('retime-keyframe').disabled = $('key-time-input').disabled;
  if (document.activeElement !== $('key-time-input')) $('key-time-input').value = key ? key.time : '';
  $('capture-keyframe').textContent = key ? 'Update pose' : 'Capture pose';
  document.querySelectorAll('[data-keyframe-time]').forEach(button => { button.disabled = busy > 0 || Boolean(gesture || dragging); button.setAttribute('aria-pressed', String(Math.abs(Number(button.dataset.keyframeTime) - time) < 1e-7)); });
}
function updateKeyframes(state) {
  const object = trackObject(state), time = authoredTime(state);
  const keys = object?.keyframes || [];
  $('keyframe-summary').textContent = object ? `${object.name} · ${keys.length}/24 poses · 12s loop` : 'Select an island to capture its poses.';
  $('keyframe-list').innerHTML = keys.length ? keys.map(key => `<button class="pose-key" data-keyframe-time="${key.time}" aria-label="Go to keyframe ${key.time.toFixed(2)} seconds" aria-pressed="false">${key.time.toFixed(2)}s <span>${key.easing === 'smooth' ? 'smooth' : 'linear'}</span></button>`).join('') : '<span class="empty-poses">No poses yet. Capture the first, then scrub to the next.</span>';
  const key = keys.find(k => Math.abs(k.time - time) < 1e-7);
  if (key) $('keyframe-easing').value = key.easing;
  const start = keys.find(k => k.time === 0), end = keys.find(k => k.time === DURATION);
  $('seam-status').textContent = !start || !end ? 'Loop seam: add 0s and 12s poses' : POSE_FIELDS.every(name => Math.abs(start.parameters[name] - end.parameters[name]) < 1e-7) ? 'Loop seam: matched' : 'Loop seam: pose jump';
  updateKeyframeControls(state, time);
}
function poseEditCommands(object, patch, time) {
  const commands = [];
  time = time <= DURATION ? time : time % DURATION;
  if (scene.animation.playing || scene.animation.time !== time) commands.push({ op: 'set_view', view: {}, animation: { playing: false, time } });
  if (object.keyframes?.length) {
    const existing = object.keyframes.find(k => Math.abs(k.time - time) < 1e-7);
    commands.push({ op: 'set_keyframe', id: object.id, keyframe: { time, parameters: poseValues({ ...sampleParameters(object.parameters, object.keyframes, time), ...patch }), easing: existing?.easing || $('keyframe-easing').value } });
  } else commands.push({ op: 'update_geometry', id: object.id, parameters: patch });
  return commands;
}
function capturePose() {
  const object = selected(scene); if (!object || busy || dragging || gesture) return;
  const time = authoredTime();
  run('batch', { label: 'Capture island pose', commands: [
    { op: 'set_view', view: {}, animation: { playing: false, time } },
    { op: 'set_keyframe', id: object.id, keyframe: { time, parameters: poseValues(sampleParameters(object.parameters, object.keyframes || [], time)), easing: $('keyframe-easing').value } },
  ] });
}
$('capture-keyframe').addEventListener('click', capturePose);
$('delete-keyframe').addEventListener('click', () => { const object = selected(scene); if (object && !busy) run('delete_keyframe', { id: object.id, time: authoredTime() }); });
$('keyframe-easing').addEventListener('change', () => { const object = selected(scene); if (object?.keyframes?.some(k => Math.abs(k.time - authoredTime()) < 1e-7)) capturePose(); });
$('keyframe-list').addEventListener('click', event => { const button = event.target.closest('[data-keyframe-time]'); if (button && !busy) run('set_view', { view: {}, animation: { playing: false, time: Number(button.dataset.keyframeTime) } }); });
$('motion-path-button').addEventListener('click', () => { editMotionPath = !editMotionPath; showHandles = true; $('handles-button').setAttribute('aria-pressed', 'true'); $('handles-button').classList.add('active'); updateUI(); renderDirty = true; });
$('retime-keyframe').addEventListener('click', () => {
  const object = selected(scene), input = $('key-time-input');
  if (!object || busy || !input.reportValidity() || input.value === '') return;
  const time = authoredTime(), new_time = Number(input.value);
  run('batch', { label: 'Retime island pose', commands: [
    { op: 'edit_keyframe', id: object.id, time, new_time },
    { op: 'set_view', view: {}, animation: { playing: false, time: new_time } },
  ] });
});
$('demo-button').addEventListener('click', () => run('load_recipe', { recipe: { ...clone(demoRecipe), animation: { ...demoRecipe.animation, playing: true } } }));

function resize() {
  const box = canvas.getBoundingClientRect();
  size = { width: box.width, height: box.height, dpr: Math.min(window.devicePixelRatio || 1, 2) };
  canvas.width = Math.round(size.width * size.dpr);
  canvas.height = Math.round(size.height * size.dpr);
  renderDirty = true;
}
new ResizeObserver(resize).observe($('canvas-stage'));
function computeTransform(width, height, state) {
  const scale = Math.min(width / WORLD.width, height / WORLD.height) * .97 * (state.view?.zoom || 1);
  return { scale, x: width / 2 - WORLD.width / 2 * scale + (state.view?.pan_x || 0) * scale, y: height / 2 - WORLD.height / 2 * scale + (state.view?.pan_y || 0) * scale };
}
function mix(hex, dark, fraction) {
  const rgb = [1, 3, 5].map((index) => Math.round(parseInt(hex.slice(index, index + 2), 16) * fraction + parseInt(dark.slice(index, index + 2), 16) * (1 - fraction)));
  return `rgb(${rgb.join(',')})`;
}
function ringColor(palette, i, count) {
  const colors = paletteColors[palette] || paletteColors.ember;
  if (i === 0) return mix(colors[0], '#122b2a', .45);
  const value = i / count;
  if (i % 6 === 0) return '#193432';
  if (i % 6 === 1) return mix(colors[2], '#142c2b', .88);
  const fraction = .35 + Math.sin(value * Math.PI) * .53;
  return mix(colors[i % 6 === 5 ? 3 : 0], '#112c2a', fraction);
}
function pathFromPoints(points) {
  const path = new Path2D();
  if (!points.length) return path;
  path.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i += 1) path.lineTo(points[i][0], points[i][1]);
  path.closePath();
  return path;
}
function render(target = ctx, width = size.width, height = size.height, dpr = size.dpr, state = current(), time = getTime(), handles = showHandles) {
  target.setTransform(dpr, 0, 0, dpr, 0, 0);
  const background = target.createRadialGradient(width * .49, height * .42, 1, width * .5, height * .5, width * .8);
  background.addColorStop(0, '#173734'); background.addColorStop(.7, '#102725'); background.addColorStop(1, '#0b1e1e');
  target.fillStyle = background; target.fillRect(0, 0, width, height);
  target.fillStyle = '#86b3a318';
  const gap = width < 600 ? 24 : 30;
  for (let x = 20; x < width; x += gap) for (let y = 20; y < height; y += gap) target.fillRect(x, y, .8, .8);
  if (!state) return;
  const trans = computeTransform(width, height, state);
  if (target === ctx) transform = trans;
  target.translate(trans.x, trans.y); target.scale(trans.scale, trans.scale);
  // Delicate survey marks give the field a sense of scale without obscuring the art.
  target.strokeStyle = '#87b6a511'; target.lineWidth = .7 / trans.scale;
  target.beginPath(); target.moveTo(55, 350); target.lineTo(945, 350); target.moveTo(500, 55); target.lineTo(500, 635); target.stroke();
  if (state.view?.grid) {
    target.strokeStyle = '#93b8a923'; target.beginPath();
    for (let x = 0; x <= 1000; x += 50) { target.moveTo(x, 0); target.lineTo(x, 700); }
    for (let y = 0; y <= 700; y += 50) { target.moveTo(0, y); target.lineTo(1000, y); }
    target.stroke();
  }
  const paths = [];
  const count = state.view?.contours || 24;
  const consumed = linkedSources(state,true);
  for (const {object,layers} of artworkLayers(state,time,Boolean(gesture||dragging))) {
    const buffer=layerBuffer(target);
    compositeLayer(target,buffer,object.style.opacity ?? 1,layerTarget=>{
      for(let i=0;i<layers.length;i++) {
        const path=pathFromLoops(layers[i].paths);
        if(i===0) { paths.push({id:object.id,path});layerTarget.save();layerTarget.shadowBlur=24;layerTarget.shadowColor='#021a18';layerTarget.shadowOffsetY=8;layerTarget.fillStyle='#102422';layerTarget.fill(path,'evenodd');layerTarget.restore(); }
        layerTarget.fillStyle=i===layers.length-1?'#102825':ringColor(object.style.palette,i,layers.length);layerTarget.fill(path,'evenodd');
        layerTarget.strokeStyle=i%6===1?'#fcdeb175':mix(paletteColors[object.style.palette]?.[1]||'#dca17d','#102722',.43);layerTarget.lineWidth=.55/trans.scale;layerTarget.stroke(path);
      }
    });
  }
  if(handles) {
    for(const object of state.objects.filter(o=>(sourceGuides&&consumed.has(o.id)) || (state.selection.includes(o.id)&&(!o.style.visible||consumed.has(o.id))))) {
      const linked=linkedSources(state).has(object.id);
      const path=pathFromPoints(generateContours(sampleParameters(object.parameters,object.keyframes||[],time),linked?0:time,linked?0:state.animation.motion,2,180)[0]);
      target.save();target.setLineDash([4/trans.scale,5/trans.scale]);target.strokeStyle=paletteColors[object.style.palette]?.[0]||'#d7ddc5';target.lineWidth=1.2/trans.scale;target.stroke(path);target.restore();
    }
  }
  if (target === ctx) renderedPaths = paths;
  if (handles && editMotionPath) {
    const object = selected(state);
    const keys = object?.style?.visible !== false ? object?.keyframes || [] : [];
    if (keys.length) {
      target.save(); target.lineWidth = 1.4 / trans.scale; target.strokeStyle = '#f4e9c6b8'; target.setLineDash([5 / trans.scale, 5 / trans.scale]);
      target.beginPath(); keys.forEach((key, i) => { const p = key.parameters; if (i) target.lineTo(p.x, p.y); else target.moveTo(p.x, p.y); }); target.stroke(); target.setLineDash([]);
      for (const key of keys) {
        const active = Math.abs(key.time - time) < 1e-7, p = key.parameters;
        target.fillStyle = active ? '#f4e9c6' : '#183d36'; target.strokeStyle = key.time === DURATION ? '#e9bc81' : '#e6eed7';
        target.beginPath(); target.arc(p.x, p.y, (key.time === DURATION ? 10 : 7) / trans.scale, 0, Math.PI * 2); target.fill(); target.stroke();
        target.font = `${11 / trans.scale}px Arial`; target.textAlign = 'left'; target.textBaseline = 'middle';
        const label = `${key.time.toFixed(2)}s`, lx = p.x + 14 / trans.scale, ly = p.y + (key.time === DURATION ? 16 : -16) / trans.scale;
        target.fillStyle = '#102725ed'; target.fillRect(lx - 3 / trans.scale, ly - 9 / trans.scale, target.measureText(label).width + 6 / trans.scale, 18 / trans.scale);
        target.fillStyle = '#f4e9c6'; target.fillText(label, lx, ly);
      }
      target.restore();
    }
  }
  if (handles) {
    for (const object of orderedLayers(state).filter(o=>o.type==='island')) {
      const explicit = state.selection?.includes(object.id);
      if ((!object.style.visible || consumed.has(object.id)) && !explicit) continue;
      const active = state.selection?.includes(object.id);
      const { x, y } = sampleParameters(object.parameters, object.keyframes || [], time);
      target.save(); target.translate(x, y);
      target.strokeStyle = active ? '#f0eed5' : '#c1d6bd7a'; target.fillStyle = '#13362c'; target.lineWidth = 1 / trans.scale;
      target.beginPath(); target.arc(0, 0, (active ? 5 : 3) / trans.scale, 0, Math.PI * 2); target.fill(); target.stroke();
      if (active) { target.globalAlpha = .5; target.beginPath(); target.arc(0, 0, 12 / trans.scale, 0, Math.PI * 2); target.stroke(); target.globalAlpha = .9; target.beginPath(); target.moveTo(-18 / trans.scale, 0); target.lineTo(-9 / trans.scale, 0); target.moveTo(9 / trans.scale, 0); target.lineTo(18 / trans.scale, 0); target.moveTo(0, -18 / trans.scale); target.lineTo(0, -9 / trans.scale); target.moveTo(0, 9 / trans.scale); target.lineTo(0, 18 / trans.scale); target.stroke(); }
      target.restore();
    }
  }
}
function animationFrame(now) {
  if (destroyed) return;
  const time = getTime();
  if ((renderDirty || current()?.animation?.playing) && now - lastFrame > 28 && !$('canvas-stage').hidden && !document.hidden) {
    render(); lastFrame = now; renderDirty = false;
  }
  if (scene && !gesture) {
    $('time-value').textContent = time.toFixed(2).padStart(5, '0');
    $('timeline-input').value = time; progress($('timeline-input'));
    if (scene.animation.playing && !dragging) { updatePoseControls(scene, time); updateKeyframeControls(scene, time); }
  }
  requestAnimationFrame(animationFrame);
}
requestAnimationFrame(animationFrame);

function worldPoint(event) {
  const box = canvas.getBoundingClientRect();
  return { x: (event.clientX - box.left - transform.x) / transform.scale, y: (event.clientY - box.top - transform.y) / transform.scale };
}
function hitObject(point) {
  const state = current();
  if (!state) return null;
  const explicit=selected(state);
  if(showHandles&&explicit&&(!explicit.style.visible||sourceBlends(state,explicit.id,true).length)) {
    const pose=sampleParameters(explicit.parameters,explicit.keyframes||[],getTime());
    if(Math.hypot(pose.x-point.x,pose.y-point.y)<22/transform.scale)return explicit;
  }
  for (const item of [...renderedPaths].reverse()) {
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); const hit = ctx.isPointInPath(item.path, point.x, point.y,'evenodd'); ctx.restore();
    if (hit) return allLayers(state).find(o=>o.id===item.id);
    const object=state.objects.find(o=>o.id===item.id);
    if(showHandles&&object){const pose=sampleParameters(object.parameters,object.keyframes||[],getTime());if(Math.hypot(pose.x-point.x,pose.y-point.y)<22/transform.scale)return object;}
  }
  return null;
}
function hitMotionKey(point) {
  if (!editMotionPath || !showHandles) return null;
  const object = selected(scene);
  if (!object || object.style?.visible === false) return null;
  return (object.keyframes || []).filter(key => Math.hypot(key.parameters.x - point.x, key.parameters.y - point.y) <= 18 / transform.scale)
    .sort((a, b) => Math.abs(a.time - authoredTime()) - Math.abs(b.time - authoredTime()))[0] || null;
}
canvas.addEventListener('pointerdown', (event) => {
  if (!scene || busy || event.button !== 0) return;
  const point = worldPoint(event);
  if (activeTool === 'add') { addIsland(point); setTool('select'); return; }
  const motionKey = hitMotionKey(point);
  if (motionKey) {
    const object = selected(scene);
    preview = clone(scene); preview.animation.time = motionKey.time; preview.animation.playing = false;
    dragging = { id: object.id, pointerId: event.pointerId, start: point, x: motionKey.parameters.x, y: motionKey.parameters.y, time: motionKey.time, pathKey: true, moved: false, revision: scene.revision };
    canvas.setPointerCapture(event.pointerId); canvas.classList.add('dragging');
    $('selection-hint').textContent = 'Move this pose only · Esc to cancel'; renderDirty = true; updateUI(); return;
  }
  const object = hitObject(point);
  if (!object) { if (scene.selection.length) run('select', { ids: [] }); return; }
  if(!object.parameters) { activeBlendId=object.id;run('select',{ids:[object.id]});return; }
  preview = clone(scene);
  preview.selection = [object.id];
  preview.animation.time = authoredTime(scene);
  preview.animation.playing = false;
  const pose = sampleParameters(object.parameters, object.keyframes || [], preview.animation.time);
  const previewObject = preview.objects.find(o => o.id === object.id);
  previewObject.parameters = pose; previewObject.keyframes = [];
  dragging = { id: object.id, pointerId: event.pointerId, start: point, x: pose.x, y: pose.y, time: preview.animation.time, moved: false, revision: scene.revision };
  canvas.setPointerCapture(event.pointerId); canvas.classList.add('dragging');
  $('selection-hint').textContent = 'Release to commit · Esc to cancel';
  renderDirty = true; updateUI();
});
canvas.addEventListener('pointermove', (event) => {
  if (!scene) return;
  const point = worldPoint(event);
  $('coordinate-label').textContent = `X ${String(Math.round(point.x)).padStart(3, '0')} / Y ${String(Math.round(point.y)).padStart(3, '0')}`;
  if (!dragging) { canvas.style.cursor = activeTool === 'add' ? 'crosshair' : hitMotionKey(point) || hitObject(point) ? 'grab' : 'default'; return; }
  const dx = point.x - dragging.start.x, dy = point.y - dragging.start.y;
  if (Math.abs(dx) + Math.abs(dy) > 2) dragging.moved = true;
  const object = preview.objects.find((o) => o.id === dragging.id);
  const pose = dragging.pathKey ? object.keyframes.find(key => key.time === dragging.time).parameters : object.parameters;
  pose.x = clamp(dragging.x + dx, ...(dragging.pathKey ? PARAMETER_BOUNDS.x : [-500, 1500])); pose.y = clamp(dragging.y + dy, ...(dragging.pathKey ? PARAMETER_BOUNDS.y : [-350, 1050]));
  renderDirty = true;
});
async function endDrag(cancel = false) {
  if (!dragging) return;
  const drag = dragging; const object = preview?.objects.find((o) => o.id === drag.id);
  dragging = null; canvas.classList.remove('dragging');
  if (canvas.hasPointerCapture(drag.pointerId)) canvas.releasePointerCapture(drag.pointerId);
  $('selection-hint').textContent = 'Drag an island to change the tide.';
  if (cancel) { preview = null; renderDirty = true; updateUI(); return; }
  const commands = [];
  if (!scene.selection.includes(drag.id)) commands.push({ op: 'select', ids: [drag.id] });
  if (drag.pathKey) {
    commands.push({ op: 'set_view', view: {}, animation: { playing: false, time: drag.time } });
    if (drag.moved && object) {
      const pose = object.keyframes.find(key => key.time === drag.time).parameters;
      commands.push({ op: 'edit_keyframe', id: drag.id, time: drag.time, position: { x: Number(pose.x.toFixed(2)), y: Number(pose.y.toFixed(2)) } });
    }
  } else if (drag.moved && object) commands.push(...poseEditCommands(scene.objects.find(o => o.id === drag.id), { x: Number(object.parameters.x.toFixed(2)), y: Number(object.parameters.y.toFixed(2)) }, drag.time));
  if (!commands.length) { preview = null; renderDirty = true; updateUI(); return; }
  await run('batch', { label: drag.pathKey ? 'Edit motion path pose' : drag.moved ? 'Moved island' : 'Selected island', commands }, { expectedRevision: drag.revision });
}
canvas.addEventListener('pointerup', () => endDrag());
canvas.addEventListener('pointercancel', () => endDrag(true));
canvas.addEventListener('lostpointercapture', () => { if (dragging) endDrag(true); });
canvas.addEventListener('pointerleave', () => { if (!dragging) $('coordinate-label').textContent = 'FIELD / 01'; });
function setTool(tool) { activeTool = tool; $('select-tool').classList.toggle('active', tool === 'select'); $('add-tool').classList.toggle('active', tool === 'add'); canvas.style.cursor = tool === 'add' ? 'crosshair' : 'grab'; $('selection-hint').textContent = tool === 'add' ? 'Click anywhere to place a new island.' : 'Drag an island to change the tide.'; }
async function addIsland(point = { x: 500 + Math.random() * 70, y: 350 + Math.random() * 60 }) {
  if (!scene) return;
  const result = await run('create_geometry', { name: `Island ${scene.objects.length + 1}`, parameters: { x: Math.round(point.x), y: Math.round(point.y), radius: 100, elongation: 1.2, rotation: -20, lobes: 3, warp: .6, phase: 0 }, style: { palette: ['ember', 'lagoon', 'aurora'][scene.objects.length % 3], opacity: 1, visible: true } });
  if (result) {
    toast('A new island, ready to shape.');
  }
}
$('select-tool').addEventListener('click', () => setTool('select'));
$('add-tool').addEventListener('click', () => setTool(activeTool === 'add' ? 'select' : 'add'));
$('add-island-button').addEventListener('click', () => addIsland());
$('handles-button').addEventListener('click', () => { showHandles = !showHandles; $('handles-button').setAttribute('aria-pressed', String(showHandles)); $('handles-button').classList.toggle('active', showHandles); renderDirty = true; });
$('layer-list').addEventListener('click', (event) => {
  const action=event.target.closest('[data-layer-action]');if(!action||busy||gesture||dragging)return;
  layerFocus={id:action.dataset.id,action:action.dataset.layerAction};
  const layer=allLayers(scene).find(o=>o.id===action.dataset.id);if(!layer)return;
  if(action.dataset.layerAction==='visibility')run('set_style',{id:layer.id,style:{visible:!layer.style.visible}});
  else if(action.dataset.layerAction==='select') {if(!layer.parameters)activeBlendId=layer.id;run('select',{ids:[layer.id]});}
  else {
    const order=[...scene.layer_order],from=order.indexOf(layer.id),to=from+(action.dataset.layerAction==='forward'?1:-1);
    if(to<0||to>=order.length)return;[order[from],order[to]]=[order[to],order[from]];run('reorder_layers',{order});
  }
});
$('duplicate-button').addEventListener('click', () => { const object = selected(scene); if (!object) return; const offset = p => ({ ...p, x: clamp(p.x + 35, ...PARAMETER_BOUNDS.x), y: clamp(p.y + 35, ...PARAMETER_BOUNDS.y) }); run('create_geometry', { name: `${[...object.name].slice(0, 75).join('')} copy`, parameters: offset(object.parameters), keyframes: (object.keyframes || []).map(key => ({ ...key, parameters: offset(key.parameters) })), style: { ...object.style } }); });
$('remove-button').addEventListener('click', () => { const object = selected(scene); if (object) run('delete_geometry', { id: object.id }); });
$('layer-demo-button').addEventListener('click',()=>run('load_recipe',{recipe:clone(layeredDemoRecipe)}).then(result=>{if(result){activeBlendId=result.scene.blends[0]?.id||'';updateUI();}}));
$('preset-select').addEventListener('change', (event) => { const chosen = presets[event.target.value]; if (chosen) run('load_recipe', { recipe: { schema_version: 3, ...clone(chosen) } }).then((result) => { if (result) toast(`${chosen.title} loaded. Undo restores your previous scene.`); }); });
$('palette-options').addEventListener('click', (event) => {
  const button = event.target.closest('[data-palette]'); if (!button || !scene) return;
  const styles = { tidal: ['ember', 'lagoon', 'aurora'], ember: ['ember', 'aurora', 'ember'], glacier: ['lagoon', 'mono', 'lagoon'] }[button.dataset.palette];
  run('batch', { label: `Applied ${button.dataset.palette} palette`, commands: scene.objects.map((o, i) => ({ op: 'set_style', id: o.id, style: { palette: styles[i % styles.length] } })) });
});

$('radius-input').min = 80; $('radius-input').max = 400; $('radius-input').step = 1;
function bindSlider(id, target, field, format) {
  const input = $(id + '-input');
  input.addEventListener('input', () => {
    if (!scene || busy) { updateUI(); return; }
    if (!gesture) {
      gesture = { id, revision: scene.revision, objectId: selected(scene)?.id, time: authoredTime(scene) };
      preview = clone(scene); preview.animation.time = gesture.time; preview.animation.playing = false;
      if (target === 'object') { const object = preview.objects.find(o => o.id === gesture.objectId); if (object) { object.parameters = sampleParameters(object.parameters, object.keyframes || [], gesture.time); object.keyframes = []; } }
    }
    const value = Number(input.value);
    if (target === 'object') { const object = preview.objects.find((o) => o.id === gesture.objectId); if (!object) return; object.parameters[field] = value; }
    else preview[target][field] = value;
    $(id + '-output').textContent = format(value); progress(input); updateKeyframeControls(preview, preview.animation.time); renderDirty = true;
  });
  input.addEventListener('change', () => {
    if (!gesture || gesture.id !== id) return;
    const saved = gesture; const value = Number(input.value); gesture = null;
    if (target === 'object') run('batch', { label: 'Shape island pose', commands: poseEditCommands(scene.objects.find(o => o.id === saved.objectId), { [field]: value }, saved.time) }, { expectedRevision: saved.revision });
    else if (target === 'animation') run('set_view', { view: {}, animation: { [field]: value } }, { expectedRevision: saved.revision });
    else run('set_view', { view: { [field]: value } }, { expectedRevision: saved.revision });
  });
  input.addEventListener('pointercancel', cancelGesture);
}
function cancelGesture() { gesture = null; preview = null; renderDirty = true; updateUI(); }
bindSlider('radius', 'object', 'radius', (n) => `${Math.round(n)} px`);
bindSlider('stretch', 'object', 'elongation', (n) => `${n.toFixed(2)}×`);
bindSlider('organic', 'object', 'warp', (n) => `${Math.round(n * 100)}%`);
bindSlider('rotation', 'object', 'rotation', (n) => `${Math.round(n)}°`);
bindSlider('contours', 'view', 'contours', (n) => String(n));
bindSlider('tide', 'animation', 'motion', (n) => `${Math.round(n * 100)}%`);
$('play-button').addEventListener('click', () => { if (scene) run('set_view', { view: {}, animation: { playing: !scene.animation.playing, time: getTime() } }); });
$('speed-button').addEventListener('click', () => { if (!scene) return; const speeds = [.5, .75, 1, 1.5, 2]; const index = speeds.indexOf(scene.animation.speed); run('set_view', { view: {}, animation: { speed: speeds[(index + 1) % speeds.length], time: getTime() } }); });
$('timeline-input').addEventListener('input', () => { if (!scene || busy) { updateUI(); return; } if (!gesture) { gesture = { id: 'timeline', revision: scene.revision }; preview = clone(scene); } preview.animation.time = Number($('timeline-input').value); preview.animation.playing = false; $('time-value').textContent = preview.animation.time.toFixed(2).padStart(5, '0'); progress($('timeline-input')); updatePoseControls(preview, preview.animation.time); updateKeyframeControls(preview, preview.animation.time); renderDirty = true; });
$('timeline-input').addEventListener('change', () => { if (!gesture || gesture.id !== 'timeline') return; const revision = gesture.revision; gesture = null; run('set_view', { view: {}, animation: { time: Number($('timeline-input').value), playing: false } }, { expectedRevision: revision }); });
$('timeline-input').addEventListener('pointercancel', cancelGesture);
$('undo-button').addEventListener('click', () => run('undo'));
$('redo-button').addEventListener('click', () => run('redo'));
$('fit-button').addEventListener('click', () => run('set_view', { view: { zoom: 1, pan_x: 0, pan_y: 0 } }));
$('retry-button').addEventListener('click', () => { $('canvas-loading').hidden = false; $('canvas-error').hidden = true; refresh({ initial: true }); });
function setView(view) { const isRecipe = view === 'recipe'; $('recipe-view').hidden = !isRecipe; $('canvas-stage').hidden = isRecipe; $('canvas-tab').classList.toggle('active', !isRecipe); $('recipe-tab').classList.toggle('active', isRecipe); if (!isRecipe) { resize(); renderDirty = true; } }
$('canvas-tab').addEventListener('click', () => setView('canvas'));
$('recipe-tab').addEventListener('click', () => setView('recipe'));
$('import-recipe').addEventListener('click', () => { if (scene && !busy) $('recipe-file').click(); });
$('recipe-file').addEventListener('change', async () => {
  const file = $('recipe-file').files?.[0];
  $('recipe-file').value = '';
  if (!file || !scene) return;
  const revision = scene.revision;
  try {
    if (file.size > 512000) throw new Error('Choose a scene recipe smaller than 512 KB.');
    const imported = JSON.parse(await file.text());
    const result = await run('load_recipe', { recipe: imported }, { expectedRevision: revision });
    if (result) toast('Recipe loaded. Undo restores your previous scene.');
  } catch (error) { toast(error instanceof SyntaxError ? 'That file is not valid JSON. Your scene was not changed.' : error.message, true); }
});
$('copy-recipe').addEventListener('click', async () => { if (!scene) return; try { await navigator.clipboard.writeText(JSON.stringify(recipe(), null, 2)); $('copy-recipe').textContent = 'Copied'; clearTimeout(copyTimer); copyTimer = setTimeout(() => { $('copy-recipe').textContent = 'Copy JSON'; }, 2000); } catch { toast('Clipboard unavailable. Export the JSON recipe instead.', true); } });

function download(blob, filename) { const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 30000); }
function exportSVG() {
  const state = scene, time = getTime();
  let body = '<defs><radialGradient id="field"><stop stop-color="#173734"/><stop offset="1" stop-color="#0b1e1e"/></radialGradient></defs><rect width="1000" height="700" fill="url(#field)"/>';
  const trans = computeTransform(1000, 700, state);
  body += `<g transform="translate(${trans.x} ${trans.y}) scale(${trans.scale})">`;
  for(const {object,layers} of artworkLayers(state,time)) {
    body += `<g id="${esc(object.id)}" opacity="${object.style.opacity ?? 1}"><title>${esc(object.name)}</title>`;
    layers.forEach((layer,i)=>{ const d=layer.paths.map(points=>points.map((point,index)=>`${index?'L':'M'}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(' ')+'Z').join(' '); body+=`<path d="${d}" fill-rule="evenodd" fill="${i===layers.length-1?'#102825':ringColor(object.style.palette,i,layers.length)}" stroke="${i%6===1?'#e6be91':'#24463e'}" stroke-width=".55"/>`; });
    body+='</g>';
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700" viewBox="0 0 1000 700"><title>${esc(state.title)}</title><desc>Created with 2Top Tidal Atlas. Scene revision ${state.revision}. Frame ${time.toFixed(2)} seconds.</desc>${body}</g></svg>`;
}
$('export-button').addEventListener('click', () => { const opened = !$('export-menu').hidden; $('export-menu').hidden = opened; $('export-button').setAttribute('aria-expanded', String(!opened)); });
$('export-menu').addEventListener('click', async (event) => {
  const type = event.target.closest('[data-export]')?.dataset.export;
  if (!type || !scene) return;
  $('export-menu').hidden = true; $('export-button').setAttribute('aria-expanded', 'false');
  const base = (scene.title || 'tidal-atlas').toLowerCase().replace(/[^a-z0-9]+/g, '-');
  try {
    if (type === 'json') download(new Blob([JSON.stringify(recipe(), null, 2)], { type: 'application/json' }), `${base}.json`);
    if (type === 'svg') download(new Blob([exportSVG()], { type: 'image/svg+xml' }), `${base}.svg`);
    if (type === 'png') {
      const output = document.createElement('canvas'); output.width = 2000; output.height = 1400;
      render(output.getContext('2d'), 1000, 700, 2, scene, getTime(), false);
      const blob = await new Promise((resolve) => output.toBlob(resolve, 'image/png'));
      if (!blob) throw new Error('Image encoding failed. Try the SVG export.');
      download(blob, `${base}.png`);
    }
    toast(`${type.toUpperCase()} exported.`);
  } catch (error) { toast(error.message, true); }
});
document.addEventListener('click', (event) => { if (!event.target.closest('.export-wrap')) { $('export-menu').hidden = true; $('export-button').setAttribute('aria-expanded', 'false'); } });

function showDialog(title, content) { dialogGeneration++; $('dialog-title').textContent = title; $('dialog-content').innerHTML = content; $('info-dialog').showModal(); }
$('close-dialog').addEventListener('click', () => $('info-dialog').close());
$('info-dialog').addEventListener('click', (event) => { if (event.target === $('info-dialog')) { const box = $('info-dialog').getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) $('info-dialog').close(); } });
async function coauthorSetup() {
  showDialog('Coauthor the same canvas.', '<p>Loading local client settings…</p>');
  const generation=dialogGeneration;
  try {
    const response=await fetch('/api/setup');if(!response.ok)throw Error('Local setup settings are unavailable.');const setup=await response.json();if(generation!==dialogGeneration||!$('info-dialog').open)return;
    const config=JSON.stringify(setup.stdio,null,2),native=webmcpStatus?.registered?`${webmcpStatus.registered} tools registered; model session unverified`:webmcpStatus?.supported?'API available; registration incomplete and session unverified':'API unavailable here; native session unverified';
    $('dialog-content').innerHTML=`<p>Your hands and client tools share one scene and undo history. No AI provider is configured or called by this page. This app does not include a model or verify a client's identity.</p><ol class="setup-steps"><li><strong>Save your starting point.</strong> Export a JSON recipe before a coauthoring session.</li><li><strong>Connect an already configured local MCP client.</strong> The client runs on this computer. HTTP endpoint: <code>${esc(setup.mcp_url)}</code> (${setup.mcp_enabled?'enabled':'disabled'}). Or copy these stdio launch settings into its matching fields; clients use different configuration formats.<pre id="stdio-settings">${esc(config)}</pre><button class="small-button" id="copy-client-settings">Copy launch settings</button></li><li><strong>Discover, read, then make one edit.</strong> Discover the catalog, call <code>get_scene</code>, and use its latest <code>expected_revision</code>. For a write, use a unique <code>request_id</code>. A conflict means read again and reconsider; don't silently retry. <a href="${esc(setup.catalog_url)}" target="_blank" rel="noopener">Exact tool schemas</a> · <a href="/api/docs" target="_blank" rel="noopener">Tool reference</a>.</li><li><strong>Try a small coauthor prompt.</strong><blockquote>Read get_scene. Find the selected layer and propose a palette or opacity adjustment. Use set_style or one batch with the current revision, then read the scene and explain the committed change.</blockquote>Ask your existing model client to do this. Running a JSON command or saved example is a protocol walkthrough, not proof of live model inference.</li><li><strong>Refine together.</strong> Watch Coauthor activity for the committed MCP edit. Adjust a manual control, then Undo and Redo. Export JSON to keep the result. History describes routes and committed differences; client notes don't establish identity.</li></ol><h3>Native WebMCP</h3><p>${esc(native)}. The HTTP bridge label records its server route, not proof of native browser execution. Use an already supported top-level browser/model host; verify its tools, then exercise a real shared edit. Work17's ordinary Chromium does not qualify as a supported model session.</p><p><a href="https://developer.chrome.com/docs/ai/webmcp" target="_blank" rel="noopener">Official Chrome WebMCP guidance</a> · <a href="https://webmachinelearning.github.io/webmcp/" target="_blank" rel="noopener">WebMCP API draft</a></p><h3>Read-only protocol check</h3><p>With the studio running, this discovers tools using the real MCP SDK without a model or a write:</p><pre>python -m studio.mcp_client --studio-url ${esc(location.origin)} --catalog</pre><p>Use <code>--tool get_scene</code> to inspect the current artwork. A mutation requires an explicit JSON arguments file via <code>--arguments</code>; this client never chooses a revision or retries a write for you.</p>`;
    $('copy-client-settings').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(config);toast('Client launch settings copied.');}catch{toast('Select the launch settings text and copy it manually.',true);}});
  } catch(error){if(generation===dialogGeneration&&$('info-dialog').open)$('dialog-content').textContent=error.message;}
}
$('connect-button').addEventListener('click',coauthorSetup);
$('coauthor-setup-button').addEventListener('click',coauthorSetup);
$('help-button').addEventListener('click', () => showDialog('Make a little room for wonder.', '<p>Choose an art direction, move an island, or play the tide. Each island is a family of nested implicit contours. Your edits and connected-agent edits share the same scene history.</p><ul class="shortcut-list"><li><span>Play / pause</span><kbd>Space</kbd></li><li><span>Undo</span><kbd>⌘ / Ctrl Z</kbd></li><li><span>Redo</span><kbd>⌘ / Ctrl Shift Z</kbd></li><li><span>Select & move</span><kbd>V</kbd></li><li><span>Place an island</span><kbd>A</kbd></li><li><span>Toggle handles</span><kbd>H</kbd></li><li><span>Cancel an edit</span><kbd>Esc</kbd></li><li><span>Remove selected island</span><kbd>Delete</kbd></li></ul><p>Drag the center or shoreline to move an island. Use Shape & field for scale, organic detail, rotation, contour density, and tide strength. Exports omit selection handles.</p>'));
$('activity-button').addEventListener('click',()=>{$('coauthor-panel').scrollIntoView({behavior:'smooth',block:'start'});$('activity-filter').focus({preventScroll:true});});
function updateActivity() {
  if(!scene)return;
  const filter=$('activity-filter').value,key=`${scene.document_id}:${scene.revision}:${filter}:${webmcpStatus?.registered||0}`;
  if(key===activityKey)return;activityKey=key;
  const opened=new Set([...$('coauthor-activity').querySelectorAll('details[open]')].map(item=>item.dataset.tx));
  const entries=committedEntries(scene,filter),all=scene.history.entries;
  $('coauthor-count').textContent=`${all.filter(e=>sourceKind(e)==='mcp_protocol').length} observed MCP commits · last ${all.length} entries`;
  $('coauthor-capability').textContent=webmcpStatus?.registered?`WebMCP: ${webmcpStatus.registered} registered tools; session unverified`:webmcpStatus?.supported?'WebMCP API available; registration incomplete':'Native WebMCP: API unavailable here';
  $('coauthor-activity').innerHTML=entries.map(entry=>{
    const note=entry.operation==='batch'?`<p>Client note: ${esc(entry.label)}</p>`:'';
    const related=entry.related?` · ${entry.operation==='undo'?'undo':'redo'} of revision ${entry.related.revision}`:'';
    const hint=entry.source?.caller_hint?`<p>Caller transport hint: ${esc(entry.source.caller_hint)} (unverified).</p>`:'';
    return `<li class="coauthor-entry" data-source="${sourceKind(entry)}" data-revision="${entry.revision}"><div class="coauthor-entry-top"><span class="source-badge">${esc(sourceLabel(entry))}</span><span>Revision ${entry.revision}${esc(related)}</span></div><strong>${esc(entry.summary||'Committed edit')}</strong><details data-tx="${esc(entry.transaction_id)}"${opened.has(entry.transaction_id)?' open':''}><summary>Details for revision ${entry.revision}</summary><p>Observed server route: ${esc(entry.source?.entrypoint||'unknown')}. Identity and model inference are unverified.</p>${hint}${note}<p>Transaction: <code>${esc(entry.transaction_id)}</code></p><time datetime="${esc(entry.committed_at||'')}">${esc(entry.committed_at||'Time unavailable')}</time><pre>${esc(JSON.stringify(entry.changes||{},null,2))}</pre></details></li>`;
  }).join('')||'<li class="empty-activity">No committed edits for this route in the retained history.</li>';
  $('coauthor-history-note').textContent=`${scene.history.session_commits||0} commits this process. Showing up to ${scene.history.entry_limit||30}; history resets after a server restart and is not included in exported recipes.`;
}
$('activity-filter').addEventListener('change',updateActivity);

document.addEventListener('keydown', (event) => {
  const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
  if (event.key === 'Escape') { if (dragging) endDrag(true); if (gesture) cancelGesture(); setTool('select'); $('export-menu').hidden = true; $('export-button').setAttribute('aria-expanded', 'false'); return; }
  if (typing || $('info-dialog').open || !scene) return;
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'z') { event.preventDefault(); run(event.shiftKey ? 'redo' : 'undo'); return; }
  if (event.key === ' ' && !document.activeElement?.closest('button,a')) { event.preventDefault(); $('play-button').click(); }
  if (event.key.toLowerCase() === 'v') setTool('select');
  if (event.key.toLowerCase() === 'a' && !event.ctrlKey && !event.metaKey) setTool('add');
  if (event.key.toLowerCase() === 'h') $('handles-button').click();
  if (event.key === 'Delete' || event.key === 'Backspace') { const object = selected(scene); if (object) { event.preventDefault(); run('delete_geometry', { id: object.id }); } }
});
window.addEventListener('beforeunload', () => { destroyed = true; });
setInterval(() => { if (!document.hidden && !gesture && !dragging && !busy) refresh(); }, 1300);
refresh({ initial: true });
