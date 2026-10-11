/** DOM integration smoke test. Uses the real SceneService through an in-process
 * Python bridge by default (no network/server required); set STUDIO_TEST_URL to
 * exercise an already-running authorized HTTP service instead. Canvas API is
 * mocked, so this is behavioral verification, not visual/browser verification.
 * Install dependencies: npm install
 * Run from repo root: npm run test:ui
 * Optional: STUDIO_RENDER_PREVIEW=1 renders the exact canvas with @napi-rs/canvas.
 * STUDIO_NODE_DEPS can point to another directory containing node_modules.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { resolveObjectURL } from 'node:buffer';
let require = createRequire(path.join(process.cwd(), 'package.json'));
try { require.resolve('jsdom'); }
catch (error) {
  const fallback = process.env.STUDIO_NODE_DEPS || process.env.STUDIO_TEST_DEPS;
  if (!fallback) throw new Error('Install UI test dependencies with npm install, or set STUDIO_NODE_DEPS to a directory containing node_modules.');
  require = createRequire(path.join(path.resolve(fallback), 'package.json'));
}
const { JSDOM } = require('jsdom');
const nativeCanvas = (process.env.STUDIO_RENDER_PREVIEW || process.env.STUDIO_RENDER_ANIMATION) ? require('@napi-rs/canvas') : null;
const canvasBackings = new WeakMap();
const root = process.cwd();
const html = await fs.readFile(path.join(root, 'studio/static/index.html'), 'utf8');
const dom = new JSDOM(html, { url: process.env.STUDIO_TEST_URL || 'http://127.0.0.1:8000/', pretendToBeVisual: true });
const { window } = dom;
const nativeFetch = globalThis.fetch;
const nativeSetTimeout = globalThis.setTimeout;
const timeouts = new Set();
globalThis.setTimeout = (fn, ms, ...args) => { const handle = nativeSetTimeout(fn, ms, ...args); timeouts.add(handle); return handle; };
const intervals = new Set();
const rafs = [];
const downloads = [];
const requests = [];
const failures = [];
let failNext = false;
let holdNext = false;
let releaseHeld;
let bridge;
let serial = Promise.resolve();
let responseCallback;
if (!process.env.STUDIO_TEST_URL) {
  bridge = spawn(process.env.PYTHON || 'python', ['-u', '-c', `
import json, sys
from studio.service import SceneService, SceneError
service = SceneService()
for line in sys.stdin:
    req = json.loads(line)
    try:
        if req['path'] == '/api/scene': result = service.snapshot()
        elif req['path'] == '/api/command': result = service.execute(req['body'], actor='manual')
        elif req['path'] == '/api/tools': result = service.tool_definitions()
        else: raise ValueError('Unexpected test request path')
        response = {'status': 200, 'body': result}
    except SceneError as error:
        response = {'status': error.status, 'body': {'ok': False, 'error': error.as_dict(), 'revision': service.snapshot()['revision']}}
    print(json.dumps(response), flush=True)
`], { cwd: root, stdio: ['pipe', 'pipe', 'inherit'] });
  createInterface({ input: bridge.stdout }).on('line', (line) => { responseCallback?.(JSON.parse(line)); responseCallback = null; });
}
function callBridge(req) {
  const result = serial.then(() => new Promise((resolve) => { responseCallback = resolve; bridge.stdin.write(JSON.stringify(req) + '\n'); }));
  serial = result.catch(() => {}); return result;
}
globalThis.fetch = async (url, options = {}) => {
  const pathname = new URL(url, window.location.href).pathname;
  const body = options.body ? JSON.parse(options.body) : undefined;
  requests.push({ path: pathname, body });
  if (holdNext && pathname === '/api/command') { holdNext = false; await new Promise((resolve) => { releaseHeld = () => { releaseHeld = null; resolve(); }; }); }
  if (failNext && pathname === '/api/command') { failNext = false; return new Response(JSON.stringify({ ok: false, error: { code: 'storage_error', message: 'Test storage failure. No edit was committed.' } }), { status: 503, headers: { 'content-type': 'application/json' } }); }
  if (process.env.STUDIO_TEST_URL) return nativeFetch(new URL(pathname, process.env.STUDIO_TEST_URL), options);
  const result = await callBridge({ path: pathname, body });
  return new Response(JSON.stringify(result.body), { status: result.status, headers: { 'content-type': 'application/json' } });
};
const canvasContext = {
  createRadialGradient: () => ({ addColorStop() {} }),
  isPointInPath: () => false,
  getTransform:()=>({a:1,b:0,c:0,d:1,e:0,f:0}),
};
for (const name of ['setTransform', 'fillRect', 'clearRect', 'drawImage', 'translate', 'scale', 'beginPath', 'moveTo', 'lineTo', 'stroke', 'save', 'restore', 'fill', 'arc']) canvasContext[name] = () => {};
window.HTMLCanvasElement.prototype.getContext = function () {
  if (!nativeCanvas) return {...canvasContext,canvas:this};
  if (!canvasBackings.has(this)) canvasBackings.set(this, nativeCanvas.createCanvas(this.width, this.height));
  const context=canvasBackings.get(this).getContext('2d');
  if(!context.studioDrawImage){const original=context.drawImage.bind(context);context.drawImage=(image,...args)=>original(canvasBackings.get(image)||image,...args);context.studioDrawImage=true;}
  return context;
};
if (nativeCanvas) {
  for (const property of ['width', 'height']) {
    const descriptor = Object.getOwnPropertyDescriptor(window.HTMLCanvasElement.prototype, property);
    Object.defineProperty(window.HTMLCanvasElement.prototype, property, {
      get() { return descriptor.get.call(this); },
      set(value) { descriptor.set.call(this, value); if (canvasBackings.has(this)) canvasBackings.get(this)[property] = value; },
    });
  }
}
window.HTMLCanvasElement.prototype.getBoundingClientRect = () => ({ x: 0, y: 0, left: 0, top: 0, right: 960, bottom: 600, width: 960, height: 600 });
window.HTMLCanvasElement.prototype.setPointerCapture = function (id) { this.pointerId = id; };
window.HTMLCanvasElement.prototype.hasPointerCapture = function (id) { return this.pointerId === id; };
window.HTMLCanvasElement.prototype.releasePointerCapture = function () { this.pointerId = null; };
window.HTMLCanvasElement.prototype.toBlob = function (callback) { callback(new Blob([nativeCanvas ? canvasBackings.get(this).toBuffer('image/png') : 'png-test'], { type: 'image/png' })); };
window.HTMLAnchorElement.prototype.click = function () { downloads.push({ name: this.download, url: this.href }); };
window.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
window.HTMLDialogElement.prototype.close = function () { this.open = false; };
Object.defineProperty(window.document, 'hidden', { value: false });
Object.defineProperty(globalThis, 'navigator', { value: window.navigator, configurable: true });
Object.defineProperty(window.navigator, 'clipboard', { value: { writeText: async (text) => { window.copiedText = text; } } });
for (const key of ['window', 'document', 'location', 'CustomEvent']) globalThis[key] = window[key] || window;
globalThis.Path2D = nativeCanvas?.Path2D || class { moveTo() {} lineTo() {} closePath() {} };
globalThis.ResizeObserver = class { constructor(callback) { this.callback = callback; } observe() { this.callback(); } };
globalThis.requestAnimationFrame = (callback) => rafs.push(callback);
const nativeSetInterval = globalThis.setInterval;
globalThis.setInterval = (fn, ms) => { const handle = nativeSetInterval(fn, ms); intervals.add(handle); return handle; };
window.addEventListener('error', (event) => failures.push(event.error || event.message));
const $ = (id) => window.document.getElementById(id);
const sleep = (ms = 15) => new Promise((resolve) => setTimeout(resolve, ms));
async function waitFor(predicate, message) { const deadline = Date.now() + 6000; while (!predicate()) { if (Date.now() > deadline) throw new Error('Timed out: ' + message); await sleep(); } }
async function revisionAfter(action) { const before = window.tidalStudio.getScene().revision; action(); await waitFor(() => window.tidalStudio.getScene().revision > before, 'scene revision after action'); await sleep(); return window.tidalStudio.getScene(); }
function input(id, value) { const el = $(id); el.value = value; el.dispatchEvent(new window.Event('input', { bubbles: true })); }
function change(id) { $(id).dispatchEvent(new window.Event('change', { bubbles: true })); }
function key(key, props = {}) { window.document.dispatchEvent(new window.KeyboardEvent('keydown', { key, bubbles: true, ...props })); }
function pointer(type, x, y, props = {}) { const event = new window.MouseEvent(type, { clientX: x, clientY: y, button: 0, bubbles: true, ...props }); Object.defineProperty(event, 'pointerId', { value: 1 }); $('art-canvas').dispatchEvent(event); }
let renderClock = performance.now();
function frame() { renderClock = Math.max(renderClock + 40, performance.now() + 50); const callbacks = rafs.splice(0); for (const callback of callbacks) callback(renderClock); }
let checks = 0;
let initialRecipe;
function check(description, fn) { fn(); checks++; console.log('PASS ' + description); }
try {
  await import(pathToFileURL(path.join(root, 'studio/static/app.js')).href + '?smoke=' + Date.now());
  await waitFor(() => window.tidalStudio?.getScene(), 'initial scene load'); frame();
  const firstScene = window.tidalStudio.getScene();
  initialRecipe = Object.fromEntries(['schema_version', 'title', 'objects', 'view', 'animation'].map((key) => [key, firstScene[key]]));
  if (nativeCanvas) {
    await fs.mkdir(path.join(root, 'review_artifacts'), { recursive: true });
    await fs.writeFile(path.join(root, 'review_artifacts/tidal-atlas-canvas.png'), canvasBackings.get($('art-canvas')).toBuffer('image/png'));
    console.log('Saved exact canvas render (not a browser screenshot): review_artifacts/tidal-atlas-canvas.png');
  }
  check('initial scene is authoritative and connected', () => { assert.equal(window.tidalStudio.getScene().objects.length, 3); assert.equal($('canvas-loading').hidden, true); assert.match($('connection-label').textContent, /connected/); assert.equal($('undo-button').disabled, true); });
  let state = await revisionAfter(() => $('layer-list').querySelector(`[data-layer-action="select"][data-id="${window.tidalStudio.getScene().objects[0].id}"]`).click());
  check('layer selection enables exact object controls', () => { assert.equal(state.selection.length, 1); assert.equal($('radius-input').disabled, false); assert.equal(Number($('radius-input').value), state.objects[0].parameters.radius); });
  await window.tidalStudio.command('batch', { commands: [
    { op: 'update_geometry', id: state.objects[0].id, parameters: { rotation: 270 } },
    { op: 'set_view', view: { contours: 64 } },
  ] });
  check('inspector faithfully displays the full shared-schema rotation and contour ranges', () => { assert.equal(Number($('rotation-input').value), 270); assert.equal(Number($('contours-input').value), 64); });
  state = await revisionAfter(() => $('undo-button').click());
  const radius = state.objects[0].parameters.radius;
  const revision = state.revision;
  input('radius-input', radius + 10);
  check('slider preview does not mutate authoritative state', () => { assert.equal(window.tidalStudio.getScene().revision, revision); assert.equal(window.tidalStudio.getScene().objects[0].parameters.radius, radius); });
  state = await revisionAfter(() => change('radius-input'));
  check('slider release commits exact new radius', () => assert.equal(state.objects[0].parameters.radius, radius + 10));
  state = await revisionAfter(() => $('undo-button').click());
  check('undo restores geometry', () => assert.equal(state.objects[0].parameters.radius, radius));
  state = await revisionAfter(() => $('redo-button').click());
  check('redo restores the edit', () => assert.equal(state.objects[0].parameters.radius, radius + 10));
  holdNext = true;
  const pendingEdit = window.tidalStudio.command('set_view', { view: { grid: true } });
  await waitFor(() => releaseHeld, 'delayed command start');
  input('radius-input', radius + 25); input('timeline-input', 5); input('tide-input', .95);
  check('pending commands lock controls and reject overlapping gesture starts', () => { assert.equal($('radius-input').disabled, true); assert.equal($('timeline-input').disabled, true); assert.equal(window.tidalStudio.getScene().objects[0].parameters.radius, radius + 10); });
  releaseHeld(); await pendingEdit;
  input('radius-input', radius + 12);
  state = await revisionAfter(() => change('radius-input'));
  check('slider remains usable after interrupted async command', () => { assert.equal(state.objects[0].parameters.radius, radius + 12); assert.deepEqual(failures, []); });
  state = await revisionAfter(() => $('undo-button').click());
  const beforeCancel = state.revision;
  input('organic-input', .93); key('Escape'); change('organic-input'); await sleep(60);
  check('Escape cancels slider preview without a write', () => { assert.equal(window.tidalStudio.getScene().revision, beforeCancel); assert.notEqual(window.tidalStudio.getScene().objects[0].parameters.warp, .93); });
  frame();
  // center transform = min(960/1000,600/700)*.97, centered in canvas
  const object = window.tidalStudio.getScene().objects[0];
  const scale = 600 / 700 * .97, ox = 480 - 500 * scale, oy = 300 - 350 * scale;
  const sx = ox + object.parameters.x * scale, sy = oy + object.parameters.y * scale;
  pointer('pointerdown', sx, sy); pointer('pointermove', sx + 50, sy + 20); key('Escape'); pointer('pointerup', sx + 50, sy + 20); await sleep(50);
  check('Escape cancels a pointer drag', () => { assert.equal(window.tidalStudio.getScene().revision, beforeCancel); assert.equal($('art-canvas').classList.contains('dragging'), false); });
  pointer('pointerdown', sx, sy); pointer('pointermove', sx + 50, sy + 20);
  state = await revisionAfter(() => pointer('pointerup', sx + 50, sy + 20));
  check('one drag is one authoritative transaction', () => { assert.equal(state.revision, beforeCancel + 1); assert.ok(state.objects[0].parameters.x > object.parameters.x + 40); });
  const count = state.objects.length;
  state = await revisionAfter(() => $('duplicate-button').click());
  check('duplicate creates and selects one new island', () => { assert.equal(state.objects.length, count + 1); assert.equal(state.selection[0], state.objects.at(-1).id); });
  state = await revisionAfter(() => $('undo-button').click());
  check('one undo reverses the entire duplicate', () => assert.equal(state.objects.length, count));
  await window.tidalStudio.command('update_geometry', { id: state.selection[0], name: 'x'.repeat(80), parameters: { x: 2000, y: 1400 } });
  state = await revisionAfter(() => $('duplicate-button').click());
  check('duplicate accepts a maximum-length name and boundary coordinates', () => { const copied = state.objects.at(-1); assert.equal(copied.name.length, 80); assert.ok(copied.name.endsWith(' copy')); assert.equal(copied.parameters.x, 2000); assert.equal(copied.parameters.y, 1400); });
  await revisionAfter(() => $('undo-button').click());
  state = await revisionAfter(() => $('undo-button').click());
  state = await revisionAfter(() => $('add-island-button').click());
  check('add island validates and selects through command service', () => assert.equal(state.objects.length, count + 1));
  state = await revisionAfter(() => $('remove-button').click());
  check('remove selected island updates authoritative scene', () => assert.equal(state.objects.length, count));
  state = await revisionAfter(() => { $('preset-select').value = 'atoll'; change('preset-select'); });
  check('preset loads an undoable validated recipe', () => { assert.equal(state.title, 'Coral atoll'); assert.equal(state.view.contours, 34); });
  state = await revisionAfter(() => window.document.querySelector('[data-palette="glacier"]').click());
  check('palette is a single batch edit', () => { assert.equal(state.objects[0].style.palette, 'lagoon'); assert.equal(state.objects[1].style.palette, 'mono'); });
  const beforePlayRequests = requests.filter((r) => r.body).length;
  holdNext = true; $('play-button').click();
  await waitFor(() => releaseHeld, 'delayed play command');
  $('play-button').click(); $('play-button').click();
  const beforePlayRevision = window.tidalStudio.getScene().revision;
  releaseHeld();
  await waitFor(() => window.tidalStudio.getScene().revision > beforePlayRevision, 'play commits'); await sleep();
  state = window.tidalStudio.getScene();
  check('repeated clicks while pending do not enqueue duplicate play commands', () => assert.equal(requests.filter((r) => r.body).length, beforePlayRequests + 1));
  check('play persists animation state', () => assert.equal(state.animation.playing, true));
  await sleep(50);
  state = await revisionAfter(() => $('play-button').click());
  check('pause persists an advanced playhead', () => { assert.equal(state.animation.playing, false); assert.ok(state.animation.time > 0); });
  input('timeline-input', 8.25);
  state = await revisionAfter(() => change('timeline-input'));
  check('scrub commits exact paused playhead', () => { assert.equal(state.animation.time, 8.25); assert.equal(state.animation.playing, false); });
  const beforeFailure = state.revision; failNext = true;
  $('add-island-button').click(); await waitFor(() => !$('toast').hidden && /storage failure/.test($('toast').textContent), 'failed mutation message'); await sleep(40);
  check('failed mutation restores authoritative state and shows error', () => { assert.equal(window.tidalStudio.getScene().revision, beforeFailure); assert.equal($('toast').classList.contains('error'), true); });
  state = await revisionAfter(() => $('layer-list').querySelector(`[data-layer-action="select"][data-id="${window.tidalStudio.getScene().objects[0].id}"]`).click());
  const radiusBeforeConflict = state.objects[0].parameters.radius;
  input('radius-input', radiusBeforeConflict + 30);
  const externalResponse = await fetch('/api/command', { method: 'POST', body: JSON.stringify({ op: 'set_view', expected_revision: state.revision, request_id: crypto.randomUUID(), view: { grid: false } }) });
  const externalResult = await externalResponse.json();
  change('radius-input');
  await waitFor(() => /changed elsewhere/.test($('toast').textContent), 'stale gesture conflict notice'); await sleep();
  state = window.tidalStudio.getScene();
  check('stale gesture cannot overwrite concurrent edits and refreshes latest scene', () => { assert.equal(state.revision, externalResult.scene.revision); assert.equal(state.objects[0].parameters.radius, radiusBeforeConflict); assert.equal(state.view.grid, false); });
  $('recipe-tab').click();
  check('recipe view shows current authoritative recipe', () => { assert.equal($('recipe-view').hidden, false); assert.equal(JSON.parse($('recipe-code').textContent).title, state.title); });
  $('copy-recipe').click(); await sleep();
  check('copy recipe writes valid JSON to clipboard', () => assert.equal(JSON.parse(window.copiedText).schema_version, 4));
  const importRecipe = JSON.parse(window.copiedText); importRecipe.title = 'Imported field';
  Object.defineProperty($('recipe-file'), 'files', { configurable: true, value: [{ size: 2000, text: async () => JSON.stringify(importRecipe) }] });
  state = await revisionAfter(() => change('recipe-file'));
  check('JSON recipes can be loaded through the same undoable command service', () => assert.equal(state.title, 'Imported field'));
  const revisionBeforeInvalidImport = state.revision;
  Object.defineProperty($('recipe-file'), 'files', { configurable: true, value: [{ size: 20, text: async () => '{invalid json' }] });
  change('recipe-file');
  await waitFor(() => /not valid JSON/.test($('toast').textContent), 'invalid recipe notice');
  check('invalid recipe files leave the scene untouched', () => assert.equal(window.tidalStudio.getScene().revision, revisionBeforeInvalidImport));
  $('canvas-tab').click(); frame();
  $('connect-button').click();
  check('connect dialog is honest about browser support', () => { assert.equal($('info-dialog').open, true); assert.match($('dialog-content').textContent, /Not supported in this browser/); assert.match($('dialog-content').textContent, /--studio-url/); });
  $('close-dialog').click();
  check('dialog close restores workspace', () => assert.equal($('info-dialog').open, false));
  for (const format of ['json', 'svg', 'png']) { $('export-button').click(); window.document.querySelector(`[data-export="${format}"]`).click(); await sleep(35); }
  check('all three export formats produce downloads', () => assert.deepEqual(downloads.map((d) => d.name.split('.').at(-1)), ['json', 'svg', 'png']));
  const exportedJson = JSON.parse(await resolveObjectURL(downloads[0].url).text());
  const exportedSvg = new window.DOMParser().parseFromString(await resolveObjectURL(downloads[1].url).text(), 'image/svg+xml');
  check('exported recipe and vector artwork are parseable content', () => { assert.equal(exportedJson.schema_version, 4); assert.equal(exportedSvg.querySelector('parsererror'), null); assert.ok(exportedSvg.querySelectorAll('path').length > 50); });
  if (nativeCanvas) {
    const png = Buffer.from(await resolveObjectURL(downloads[2].url).arrayBuffer());
    check('native PNG export encodes a real 2000-by-1400 image', () => { assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a'); assert.equal(png.readUInt32BE(16), 2000); assert.equal(png.readUInt32BE(20), 1400); });
  }
  check('all persisted UI mutations use the authoritative command endpoint', () => { const mutations = requests.filter((r) => r.body); assert.ok(mutations.length >= 15); for (const r of mutations) { assert.equal(r.path, '/api/command'); assert.equal(typeof r.body.expected_revision, 'number'); assert.match(r.body.request_id, /^[a-f0-9-]+$/); } });
  check('no uncaught DOM errors occurred', () => assert.deepEqual(failures, []));
  if (nativeCanvas && process.env.STUDIO_RENDER_ANIMATION) {
    // Optional artifact-only pass after the assertions. These frames are exact
    // app canvas output from authoritative set_view commands, not screenshots.
    await window.tidalStudio.command('load_recipe', { recipe: initialRecipe });
    const framesDirectory = path.join(root, 'review_artifacts/tidal-atlas-frames');
    await fs.mkdir(framesDirectory, { recursive: true });
    for (let index = 0; index < 36; index++) {
      await window.tidalStudio.command('set_view', { view: {}, animation: { time: index / 3, playing: false } });
      frame();
      await fs.writeFile(path.join(framesDirectory, `frame-${String(index).padStart(3, '0')}.png`), canvasBackings.get($('art-canvas')).toBuffer('image/png'));
    }
    await window.tidalStudio.command('load_recipe', { recipe: initialRecipe });
    console.log('Saved 36 exact canvas frames over a 12-second loop: review_artifacts/tidal-atlas-frames/');
  }
  console.log(`\n${checks} frontend behavior checks passed. Native browser layout and interactions were not tested; this run verified DOM/service behavior.`);
} catch (error) { console.error(error); process.exitCode = 1; }
finally { window.dispatchEvent(new window.Event('beforeunload')); for (const handle of intervals) clearInterval(handle); globalThis.setInterval = nativeSetInterval; for (const handle of timeouts) clearTimeout(handle); globalThis.setTimeout = nativeSetTimeout; bridge?.kill(); window.close(); }
