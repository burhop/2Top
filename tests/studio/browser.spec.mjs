/** Real Chromium integration tests. API calls only reset/read the disposable scene;
 * edits under test use browser UI, native pointer/keyboard/file/download behavior.
 * No mocked canvas, modelContext, tool registrations, or AI/model host is injected.
 */
import { test as base, expect } from '@playwright/test';
import { readFile,writeFile } from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import { randomUUID } from 'node:crypto';
import {startDisposableStudio,disposableScene} from './disposable-studio.mjs';


const seed = JSON.parse(await readFile(new URL('../../examples/tidal_atlas_recipe.json', import.meta.url), 'utf8'));
const legacySeed = structuredClone(seed);
// Canonical expected state; schema-1 migration itself has explicit coverage below.
seed.schema_version = 4;
seed.layer_order = seed.objects.map(o=>o.id);
seed.blends = [];
seed.objects.forEach(object => { object.keyframes = []; });
const first = seed.objects[0];
const execFileAsync=promisify(execFile);
async function actualMcp(testInfo,tool,args={}) {
  const file=testInfo.outputPath(`mcp-${randomUUID()}.json`);await writeFile(file,JSON.stringify(args));
  const command=['-m','studio.mcp_client','--studio-url','http://127.0.0.1:8765','--tool',tool,'--arguments',file];
  let stdout;try {stdout=(await execFileAsync(process.env.STUDIO_PYTHON||'python',command,{timeout:15000})).stdout;}
  catch(error){if(!error.stdout)throw error;stdout=error.stdout;}
  const result=JSON.parse(stdout);
  await testInfo.attach('scripted-real-MCP-call',{body:JSON.stringify({tool,args,result,modelInference:false}),contentType:'application/json'});return result;
}

const test = base.extend({
  expectedHttpFailures: async ({}, use) => { await use(new Set()); },
  page: async ({ page, request, expectedHttpFailures }, use, testInfo) => {
    const errors = [];
    page.on('pageerror', (error) => errors.push({ kind: 'pageerror', message: error.message }));
    page.on('console', (message) => {
      if (message.type() !== 'error') return;
      // Chromium may ask for an optional favicon that this app does not provide.
      const url = message.location().url;
      if (url && new URL(url).pathname === '/favicon.ico' && /404/.test(message.text())) return;
      if (url && [...expectedHttpFailures].some(entry => entry.endsWith(' ' + new URL(url).pathname) && message.text().includes(entry.split(' ')[0]))) return;
      errors.push({ kind: 'console', message: message.text(), url });
    });
    page.on('response', (response) => {
      if (response.status() >= 400 && new URL(response.url()).pathname !== '/favicon.ico' && !expectedHttpFailures.has(`${response.status()} ${new URL(response.url()).pathname}`)) {
        errors.push({ kind: 'http', status: response.status(), url: response.url() });
      }
    });
    const before = await serverScene(request);
    const reset = await request.post('/api/command', {
      data: { op: 'load_recipe', recipe: seed, expected_revision: before.revision, request_id: randomUUID() },
    });
    expect(reset.ok(), await reset.text()).toBeTruthy();
    await page.goto('/');
    await expect(page.locator('#canvas-loading')).toBeHidden();
    await expect(page.locator('#canvas-error')).toBeHidden();
    await expect(page.locator('#connection-label')).toHaveText('Scene service connected');
    await expect(page.locator('.layer-row')).toHaveCount(seed.objects.length);
    await settleCanvas(page);
    await use(page);
    await testInfo.attach('browser-errors', { body: JSON.stringify(errors, null, 2), contentType: 'application/json' });
    expect(errors, 'No uncaught JavaScript, unexpected HTTP, or browser console errors').toEqual([]);
  },
});

async function serverScene(request) {
  const response = await request.get('/api/scene');
  expect(response.ok()).toBeTruthy();
  return response.json();
}
async function uiScene(page) {
  return page.evaluate(() => window.tidalStudio.getScene());
}
async function settleCanvas(page) {
  // Allow the app's throttled real requestAnimationFrame loop to paint, not a stub.
  await page.evaluate(async () => {
    for (let i = 0; i < 3; i += 1) await new Promise(requestAnimationFrame);
  });
}
async function edit(page, action) {
  const revision = (await uiScene(page)).revision;
  await action();
  await expect.poll(async () => (await uiScene(page)).revision).toBeGreaterThan(revision);
  await expect(page.locator('#save-status')).toHaveText('Scene synchronized');
  return uiScene(page);
}
async function selectFirst(page) {
  await edit(page, () => page.getByRole('button', { name: `Select ${first.name}`, exact: true }).click());
  await expect(page.getByRole('slider', { name: 'Island scale', exact: true })).toBeEnabled();
}
async function canvasPoint(page, object) {
  const box = await page.locator('#art-canvas').boundingBox();
  expect(box).not.toBeNull();
  const state = await uiScene(page);
  const scale = Math.min(box.width / 1000, box.height / 700) * .97 * state.view.zoom;
  return {
    x: box.x + box.width / 2 + (object.parameters.x - 500 + state.view.pan_x) * scale,
    y: box.y + box.height / 2 + (object.parameters.y - 350 + state.view.pan_y) * scale,
    scale,
  };
}
async function screenshot(page, testInfo, name) {
  const path = testInfo.outputPath(`${name}.png`);
  await page.screenshot({ path, fullPage: true, animations: 'disabled' });
  await testInfo.attach(name, { path, contentType: 'image/png' });
}
async function download(page, testInfo, type) {
  await page.getByRole('button', { name: /^Export/ }).click();
  const [item] = await Promise.all([
    page.waitForEvent('download'),
    page.locator(`[data-export="${type}"]`).click(),
  ]);
  expect(await item.failure()).toBeNull();
  expect(item.suggestedFilename()).toMatch(new RegExp(`\\.${type}$`));
  const path = testInfo.outputPath(item.suggestedFilename());
  await item.saveAs(path);
  await testInfo.attach(`export-${type}`, {
    path,
    contentType: { json: 'application/json', svg: 'image/svg+xml', png: 'image/png' }[type],
  });
  return readFile(path);
}

test('loads and paints the real canvas without claiming an AI connection', async ({ page }, testInfo) => {
  await expect(page).toHaveTitle('Tidal Atlas · 2Top Studio');
  await expect(page.getByRole('heading', { name: 'Tidal Atlas.' })).toBeVisible();
  const pixels = await page.locator('#art-canvas').evaluate((canvas) => {
    const { data } = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height);
    let artworkPixels = 0;
    for (let i = 0; i < data.length; i += 4 * 29) {
      if (data[i] > 70 || data[i + 1] > 90 || data[i + 2] > 90) artworkPixels += 1;
    }
    return { width: canvas.width, height: canvas.height, artworkPixels };
  });
  expect(pixels.width).toBeGreaterThan(600);
  expect(pixels.height).toBeGreaterThan(300);
  expect(pixels.artworkPixels).toBeGreaterThan(250);
  await expect.poll(() => page.evaluate(() => Boolean(window.tidalWebMCPStatus))).toBeTruthy();
  const capability = await page.evaluate(() => ({
    nativeRegisterToolAvailable: typeof document.modelContext?.registerTool === 'function',
    status: window.tidalWebMCPStatus,
  }));
  expect(capability.status.supported).toBe(capability.nativeRegisterToolAvailable);
  expect(capability.status.error).toBeNull();
  if (capability.nativeRegisterToolAvailable) {
    const catalog=await (await page.request.get('/api/tools')).json();
    expect(capability.status.registered).toBe(catalog.length);
    await expect(page.locator('#agent-hint')).toContainText(`${catalog.length} browser tools registered`);
    if(await page.evaluate(()=>typeof document.modelContext.getTools==='function')) {
      const names=await page.evaluate(async()=> (await document.modelContext.getTools()).map(tool=>tool.name).sort());
      expect(names).toEqual(catalog.map(tool=>tool.name).sort());
    }
  } else {
    expect(capability.status.registered).toBe(0);
    expect(capability.status.reason).toBe('browser-unsupported');
    await expect(page.locator('#agent-hint')).toContainText('Connect an MCP client');
  }
  await testInfo.attach('actual-browser-capability', { body: JSON.stringify(capability, null, 2), contentType: 'application/json' });
  await screenshot(page, testInfo, 'desktop-studio');
  await page.getByRole('button', { name: /^Connect/ }).click();
  await expect(page.getByRole('dialog')).toContainText('No AI provider is configured or called by this page.');
  if (!capability.nativeRegisterToolAvailable) {
    await expect(page.getByRole('dialog')).toContainText('API unavailable here');
  }
  await page.getByRole('button', { name: 'Close dialog', exact: true }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('keyboard layer selection, duplicate, remove, and undo use the shared scene', async ({ page, request }) => {
  const row = page.getByRole('button', { name: `Select ${first.name}`, exact: true });
  await row.focus();
  let scene = await edit(page, () => row.press('Enter'));
  expect(scene.selection).toEqual([first.id]);
  await expect(row).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#selected-name')).toHaveText(first.name);
  await expect(page.getByRole('slider', { name: 'Island scale', exact: true })).toHaveValue(String(first.parameters.radius));
  scene = await edit(page, () => page.getByRole('button', { name: 'Duplicate', exact: true }).click());
  expect(scene.objects).toHaveLength(4);
  const duplicate = scene.objects.find((object) => object.name === `${first.name} copy`);
  expect(duplicate).toBeDefined();
  expect(scene.selection).toEqual([duplicate.id]);
  scene = await edit(page, () => page.getByRole('button', { name: 'Remove', exact: true }).click());
  expect(scene.objects).toHaveLength(3);
  scene = await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
  expect(scene.objects).toHaveLength(4);
  expect((await serverScene(request)).objects).toEqual(scene.objects);
});

test('native pointer drag commits once and Escape cancels the next drag', async ({ page, request }) => {
  await selectFirst(page);
  await settleCanvas(page);
  const before = await uiScene(page);
  const start = await canvasPoint(page, before.objects[0]);
  await page.mouse.move(start.x, start.y);
  await page.mouse.down();
  await page.mouse.move(start.x + 45, start.y - 24, { steps: 6 });
  await expect(page.locator('#art-canvas')).toHaveClass('dragging');
  expect((await serverScene(request)).revision).toBe(before.revision);
  const moved = await edit(page, () => page.mouse.up());
  expect(moved.revision).toBe(before.revision + 1);
  expect(moved.objects[0].parameters.x).toBeCloseTo(first.parameters.x + 45 / start.scale, 1);
  expect(moved.objects[0].parameters.y).toBeCloseTo(first.parameters.y - 24 / start.scale, 1);
  expect((await serverScene(request)).objects[0].parameters).toEqual(moved.objects[0].parameters);

  const next = await canvasPoint(page, moved.objects[0]);
  const commands = [];
  page.on('request', (req) => { if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/command') commands.push(req); });
  await page.mouse.move(next.x, next.y);
  await page.mouse.down();
  await page.mouse.move(next.x + 55, next.y + 25, { steps: 5 });
  await page.keyboard.press('Escape');
  await page.mouse.up();
  await expect(page.locator('#art-canvas')).not.toHaveClass('dragging');
  await expect(page.locator('#selection-hint')).toHaveText('Drag an island to change the tide.');
  expect(commands).toHaveLength(0);
  expect((await serverScene(request)).revision).toBe(moved.revision);
  expect((await uiScene(page)).objects[0].parameters).toEqual(moved.objects[0].parameters);
});

test('a native range gesture previews, commits, and supports undo and redo', async ({ page, request }) => {
  await selectFirst(page);
  const slider = page.getByRole('slider', { name: 'Island scale', exact: true });
  await slider.scrollIntoViewIfNeeded();
  const before = await uiScene(page);
  const box = await slider.boundingBox();
  const fraction = (first.parameters.radius - 80) / (400 - 80);
  // Account for the native range thumb, then keep the pointer down during preview.
  const x = box.x + 7 + (box.width - 14) * fraction;
  await page.mouse.move(x, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(x + 25, box.y + box.height / 2, { steps: 5 });
  await expect(page.locator('#radius-output')).not.toHaveText(`${first.parameters.radius} px`);
  const previewRadius = Number(await slider.inputValue());
  expect(previewRadius).toBeGreaterThan(first.parameters.radius);
  expect((await serverScene(request)).revision).toBe(before.revision);
  expect((await uiScene(page)).objects[0].parameters.radius).toBe(first.parameters.radius);
  let scene = await edit(page, () => page.mouse.up());
  expect(scene.objects[0].parameters.radius).toBe(previewRadius);
  expect(scene.revision).toBe(before.revision + 1);
  scene = await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
  expect(scene.objects[0].parameters.radius).toBe(first.parameters.radius);
  scene = await edit(page, () => page.getByRole('button', { name: 'Redo', exact: true }).click());
  expect(scene.objects[0].parameters.radius).toBe(previewRadius);
  expect((await serverScene(request)).objects[0].parameters.radius).toBe(previewRadius);
});

test('pending edits lock controls and recover after the real request finishes', async ({ page, request }) => {
  await selectFirst(page);
  const before = await uiScene(page);
  let held = false;
  let release;
  const gate = new Promise((resolve) => { release = resolve; });
  // Delay transport only. The unmodified request still reaches the real service.
  const handler = async (route) => { held = true; await gate; await route.continue(); };
  await page.route('**/api/command', handler);
  try {
    await page.getByRole('slider', { name: 'Island scale', exact: true }).press('ArrowRight');
    await expect.poll(() => held).toBeTruthy();
    await expect(page.locator('#save-status')).toHaveText('Applying change…');
    for (const id of ['radius-input', 'timeline-input', 'tide-input', 'preset-select', 'undo-button']) {
      await expect(page.locator(`#${id}`)).toBeDisabled();
    }
    expect((await serverScene(request)).revision).toBe(before.revision);
  } finally {
    release();
  }
  await expect.poll(async () => (await uiScene(page)).revision).toBe(before.revision + 1);
  await expect(page.locator('#save-status')).toHaveText('Scene synchronized');
  await page.unroute('**/api/command', handler);
  await expect(page.getByRole('slider', { name: 'Island scale', exact: true })).toBeEnabled();
  const next = await edit(page, () => page.getByRole('slider', { name: 'Island scale', exact: true }).press('ArrowRight'));
  expect(next.objects[0].parameters.radius).toBe(first.parameters.radius + 2);
});

test('presets, palette, and playback update the same authoritative scene', async ({ page, request }) => {
  let scene = await edit(page, () => page.getByLabel('Starting point').selectOption('atoll'));
  expect(scene.title).toBe('Coral atoll');
  await expect(page.locator('#artwork-name')).toHaveText('Coral atoll');
  await expect(page.getByRole('button', { name: 'Select Terraced atoll', exact: true })).toBeVisible();
  scene = await edit(page, () => page.getByRole('button', { name: 'Glacier palette', exact: true }).click());
  expect(scene.objects.map((object) => object.style.palette)).toEqual(['lagoon', 'mono', 'lagoon']);
  await expect(page.getByRole('button', { name: 'Glacier palette', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await edit(page, () => page.getByRole('button', { name: 'Play animation', exact: true }).click());
  await expect.poll(async () => (await serverScene(request)).animation.time).toBeGreaterThan(.05);
  await expect(page.locator('#motion-label')).toHaveText('LIVE COMPOSITION');
  scene = await edit(page, () => page.getByRole('button', { name: 'Pause animation', exact: true }).click());
  expect(scene.animation.playing).toBe(false);
  await expect(page.locator('#motion-label')).toHaveText('COMPOSITION / PAUSED');
});

test('native file chooser imports a recipe and real JSON, SVG, PNG downloads are valid', async ({ page, request }, testInfo) => {
  const imported = structuredClone(seed);
  imported.title = 'Browser round trip';
  imported.objects[0].name = 'Imported island';
  imported.objects[0].parameters.radius = 240;
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const choosing = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Load JSON', exact: true }).click();
  const chooser = await choosing;
  const scene = await edit(page, () => chooser.setFiles({
    name: 'browser-round-trip.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(imported)),
  }));
  expect(scene.title).toBe(imported.title);
  expect(scene.objects).toEqual(imported.objects);
  await expect(page.locator('#recipe-code')).toContainText(imported.title);
  await page.getByRole('button', { name: 'Canvas', exact: true }).click();
  await settleCanvas(page);
  const savedRecipe = await download(page, testInfo, 'json');
  const json = JSON.parse(savedRecipe.toString());
  expect(json).toEqual(imported);
  const svg = (await download(page, testInfo, 'svg')).toString();
  expect(svg).toContain('<svg xmlns="http://www.w3.org/2000/svg"');
  expect(svg).toContain('<title>Browser round trip</title>');
  expect(svg).toContain('<title>Imported island</title>');
  expect(svg.match(/<path /g).length).toBe(imported.view.contours * imported.objects.length);
  const png = await download(page, testInfo, 'png');
  expect(png.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
  expect(png.readUInt32BE(16)).toBe(2000);
  expect(png.readUInt32BE(20)).toBe(1400);
  expect(png.length).toBeGreaterThan(20_000);
  expect((await serverScene(request)).revision).toBe(scene.revision);
  // Reopen the actual downloaded recipe after a new edit, not a fresh fixture.
  await edit(page, () => page.getByRole('button', { name: 'Select Imported island', exact: true }).click());
  const changed = await edit(page, () => page.getByRole('slider', { name: 'Island scale', exact: true }).press('ArrowRight'));
  expect(changed.objects[0].parameters.radius).toBe(241);
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const reopening = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Load JSON', exact: true }).click();
  const savedChooser = await reopening;
  const reopened = await edit(page, () => savedChooser.setFiles({
    name: 'saved-scene.json', mimeType: 'application/json', buffer: savedRecipe,
  }));
  expect(reopened.title).toBe(imported.title);
  expect(reopened.objects).toEqual(imported.objects);
  expect((await serverScene(request)).objects).toEqual(imported.objects);
  await page.reload();
  await expect(page.locator('#canvas-loading')).toBeHidden();
  await expect(page.locator('#artwork-name')).toHaveText(imported.title);
  expect((await uiScene(page)).objects).toEqual(imported.objects);
  await screenshot(page, testInfo, 'imported-studio');
});

test('invalid file import preserves the scene and valid imports still work afterward', async ({ page, request }) => {
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const before = await serverScene(request);
  await page.locator('#recipe-file').setInputFiles({ name: 'broken.json', mimeType: 'application/json', buffer: Buffer.from('{broken') });
  await expect(page.locator('#toast')).toHaveText('That file is not valid JSON. Your scene was not changed.');
  expect((await serverScene(request)).revision).toBe(before.revision);
  const imported = structuredClone(seed);
  imported.title = 'Recovered import';
  const scene = await edit(page, () => page.locator('#recipe-file').setInputFiles({
    name: 'fixed.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(imported)),
  }));
  expect(scene.title).toBe('Recovered import');
});

test('mobile and tablet layouts remain usable and capture actual browser screenshots', async ({ page }, testInfo) => {
  for (const viewport of [{ width: 390, height: 844 }, { width: 820, height: 1180 }]) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await settleCanvas(page);
    const dimensions = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: innerWidth }));
    await screenshot(page, testInfo, `responsive-${viewport.width}`);
    const overflow = await page.evaluate(() => [...document.querySelectorAll('body *')].filter((element) => {
      const bounds = element.getBoundingClientRect();
      return bounds.width > 0 && (bounds.right > innerWidth + 1 || bounds.left < -1);
    }).map((element) => ({ tag: element.tagName, id: element.id, className: element.className, width: element.getBoundingClientRect().width })));
    await testInfo.attach(`layout-${viewport.width}`, { body: JSON.stringify({ ...dimensions, overflow }, null, 2), contentType: 'application/json' });
    expect(dimensions.width, `${viewport.width}px layout must not overflow horizontally`).toBeLessThanOrEqual(dimensions.viewport + 1);
    await expect(page.locator('#art-canvas')).toBeVisible();
    await expect(page.getByRole('button', { name: /^Export/ })).toBeVisible();
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await selectFirst(page);
  await expect(page.locator('#selected-name')).toHaveText(first.name);
  const scene = await edit(page, () => page.getByRole('slider', { name: 'Island rotation', exact: true }).press('ArrowRight'));
  expect(scene.objects[0].parameters.rotation).toBe(first.parameters.rotation + 1);
  await page.getByRole('button', { name: 'Help and keyboard shortcuts', exact: true }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
});
// Key edits below use real buttons, keyboard range gestures and native pointers.
test('pose keys interpolate deterministically and pointer edits remain undoable', async ({ page, request }, testInfo) => {
  await selectFirst(page);
  let scene = await edit(page, () => page.getByRole('button', { name: 'Capture pose', exact: true }).click());
  expect(scene.objects[0].keyframes.map(key => key.time)).toEqual([0]);
  const timeline = page.getByRole('slider', { name: 'Animation playhead', exact: true });
  await edit(page, () => timeline.press('End'));
  scene = await edit(page, () => page.getByRole('slider', { name: 'Island scale', exact: true }).press('End'));
  expect(scene.animation.playing).toBe(false);
  expect(scene.objects[0].keyframes.map(key => key.time)).toEqual([0, 12]);
  expect(scene.objects[0].keyframes[1].parameters.radius).toBe(400);
  scene = await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
  expect(scene.objects[0].keyframes).toHaveLength(1);
  await edit(page, () => page.getByRole('button', { name: 'Redo', exact: true }).click());
  await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 0.00 seconds', exact: true }).click());
  await edit(page, () => page.getByLabel('Keyframe interpolation').selectOption('linear'));
  for (let i = 0; i < 5; i++) await edit(page, () => timeline.press('PageUp'));
  await expect(timeline).toHaveValue('6');
  const midpoint = await page.evaluate(id => window.tidalStudio.getPose(id, 6), first.id);
  expect(midpoint.radius).toBe(307.5);
  await expect(page.locator('#radius-output')).toHaveText('308 px');
  const start = await canvasPoint(page, { parameters: midpoint });
  await page.mouse.move(start.x, start.y); await page.mouse.down();
  await page.mouse.move(start.x + 40, start.y - 20, { steps: 5 });
  scene = await edit(page, () => page.mouse.up());
  expect(scene.objects[0].keyframes.map(key => key.time)).toEqual([0, 6, 12]);
  expect(scene.objects[0].parameters).toEqual(first.parameters);
  expect(scene.objects[0].keyframes[1].parameters.x).toBeCloseTo(midpoint.x + 40 / start.scale, 1);
  await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
  expect((await uiScene(page)).objects[0].keyframes).toHaveLength(2);
  await edit(page, () => page.getByRole('button', { name: 'Redo', exact: true }).click());
  const saved = await download(page, testInfo, 'json');
  expect(JSON.parse(saved).schema_version).toBe(4);
  await edit(page, () => page.getByRole('button', { name: 'Delete key', exact: true }).click());
  expect((await uiScene(page)).objects[0].keyframes).toHaveLength(2);
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const choosing = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Load JSON', exact: true }).click();
  const chooser = await choosing;
  scene = await edit(page, () => chooser.setFiles({ name: 'choreography.json', mimeType: 'application/json', buffer: saved }));
  expect(scene.objects[0].keyframes).toEqual(JSON.parse(saved).objects[0].keyframes);
  expect((await serverScene(request)).objects).toEqual(scene.objects);
  await page.reload(); await expect(page.locator('#canvas-loading')).toBeHidden();
  await selectFirst(page);
  await expect(page.getByRole('button', { name: 'Go to keyframe 6.00 seconds', exact: true })).toBeVisible();
  await screenshot(page, testInfo, 'keyframe-editor');
});

test('Orbit and bloom is reproducible, plays independent island poses and fits a phone', async ({ page, request }, testInfo) => {
  let scene = await edit(page, () => page.getByRole('button', { name: 'Play demo', exact: true }).click());
  expect(scene.title).toBe('Orbit & bloom');
  expect(scene.animation.playing).toBe(true);
  await edit(page, () => page.getByRole('button', { name: 'Pause animation', exact: true }).click());
  expect(scene.objects.every(object => object.keyframes.length === 5)).toBe(true);
  await selectFirst(page);
  await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 0.00 seconds', exact: true }).click());
  const initial = await page.locator('#art-canvas').evaluate(canvas => canvas.toDataURL());
  const pose0 = await page.evaluate(id => window.tidalStudio.getPose(id, 0), first.id);
  await screenshot(page, testInfo, 'choreography-desktop-0s');
  await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 6.00 seconds', exact: true }).click());
  await settleCanvas(page);
  const pose6 = await page.evaluate(id => window.tidalStudio.getPose(id, 6), first.id);
  expect(Math.abs(pose6.x - pose0.x)).toBeGreaterThan(300);
  expect(await page.locator('#art-canvas').evaluate(canvas => canvas.toDataURL())).not.toBe(initial);
  await screenshot(page, testInfo, 'choreography-desktop-6s');
  await edit(page, () => page.getByRole('button', { name: 'Play animation', exact: true }).click());
  await expect.poll(async () => (await serverScene(request)).animation.time).toBeGreaterThan(6.05);
  scene = await edit(page, () => page.getByRole('button', { name: 'Pause animation', exact: true }).click());
  expect(scene.animation.playing).toBe(false);
  await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 6.00 seconds', exact: true }).click());
  await page.setViewportSize({ width: 390, height: 844 }); await settleCanvas(page);
  const width = await page.evaluate(() => document.documentElement.scrollWidth);
  expect(width).toBeLessThanOrEqual(391);
  await expect(page.getByRole('button', { name: 'Update pose', exact: true })).toBeVisible();
  await screenshot(page, testInfo, 'choreography-phone');
  await edit(page, () => page.getByRole('button', { name: 'Duplicate', exact: true }).click());
  const duplicate = (await uiScene(page)).objects.at(-1);
  expect(duplicate.keyframes).toHaveLength(5);
  expect(duplicate.keyframes[2].parameters.x).toBe(pose6.x + 35);
});

test('malformed choreography is rejected and a legacy recipe still reopens', async ({ page, request, expectedHttpFailures }) => {
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const invalid = structuredClone(seed), before = await serverScene(request);
  const pose = Object.fromEntries(['x','y','radius','elongation','rotation','warp'].map(name => [name, first.parameters[name]]));
  invalid.objects[0].keyframes = [{ time: 0, parameters: pose, easing: 'smooth' }, { time: 0, parameters: pose, easing: 'smooth' }];
  expectedHttpFailures.add('400 /api/command');
  const rejected = page.waitForResponse(response => new URL(response.url()).pathname === '/api/command' && response.status() === 400);
  await page.locator('#recipe-file').setInputFiles({ name: 'duplicate-keys.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(invalid)) });
  expect((await (await rejected).json()).error.code).toBe('validation_error');
  await expect(page.locator('#toast')).toHaveText('Command validation failed');
  expect((await serverScene(request)).revision).toBe(before.revision);
  const scene = await edit(page, () => page.locator('#recipe-file').setInputFiles({ name: 'legacy-0.2.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(legacySeed)) }));
  expect(scene.schema_version).toBe(4);
  expect(scene.objects.every(object => object.keyframes.length === 0)).toBe(true);
  expect(scene.objects[0].parameters).toEqual(legacySeed.objects[0].parameters);
});

for (const viewport of [{ name: 'desktop', width: 1440, height: 1100 }, { name: 'phone', width: 390, height: 844 }]) {
  test(`motion path handles, retiming and saved poses work on ${viewport.name}`, async ({ page, request, expectedHttpFailures }, testInfo) => {
    await page.setViewportSize(viewport);
    await edit(page, () => page.getByRole('button', { name: 'Play demo', exact: true }).click());
    await edit(page, () => page.getByRole('button', { name: 'Pause animation', exact: true }).click());
    await selectFirst(page);
    await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 6.00 seconds', exact: true }).click());
    await page.getByRole('button', { name: 'Edit motion path', exact: true }).click();
    await settleCanvas(page);
    await expect(page.locator('#seam-status')).toHaveText('Loop seam: matched');
    const before = (await uiScene(page)).objects[0], key = before.keyframes[1];
    await page.locator('#art-canvas').scrollIntoViewIfNeeded(); await settleCanvas(page);
    const point = await canvasPoint(page, { parameters: key.parameters });
    let scene = await edit(page, async () => {
      await page.mouse.move(point.x, point.y); await page.mouse.down();
      await page.mouse.move(point.x + 28, point.y + 14, { steps: 5 }); await page.mouse.up();
    });
    let moved = scene.objects[0].keyframes[1];
    expect(moved.time).toBe(3); expect(moved.parameters.x).toBeCloseTo(key.parameters.x + 28 / point.scale, 1);
    expect(moved.parameters.radius).toBe(key.parameters.radius); expect(moved.easing).toBe(key.easing);
    expect(scene.objects[0].keyframes.filter(k => k.time !== 3)).toEqual(before.keyframes.filter(k => k.time !== 3));
    await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
    expect((await uiScene(page)).objects[0]).toEqual(before);
    await edit(page, () => page.getByRole('button', { name: 'Redo', exact: true }).click());
    expect((await uiScene(page)).objects[0].keyframes[1]).toEqual(moved);
    // Escape discards an actual captured-pointer preview without a transaction.
    const cancelPoint = await canvasPoint(page, { parameters: moved.parameters });
    const revision = (await uiScene(page)).revision;
    await page.mouse.move(cancelPoint.x, cancelPoint.y); await page.mouse.down();
    await page.mouse.move(cancelPoint.x + 20, cancelPoint.y + 15); await page.keyboard.press('Escape'); await page.mouse.up();
    expect((await serverScene(request)).revision).toBe(revision);
    await page.getByLabel('Selected key time').fill('7.5');
    scene = await edit(page, () => page.getByRole('button', { name: 'Move key', exact: true }).click());
    expect(scene.objects[0].keyframes.map(k => k.time)).toEqual([0, 6, 7.5, 9, 12]);
    expect(scene.objects[0].keyframes[2]).toEqual({ ...moved, time: 7.5 });
    expect(await page.evaluate(id => window.tidalStudio.getPose(id, 6.75).radius, first.id)).toBe(172.5);
    const retimed = structuredClone(scene.objects);
    await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
    expect((await uiScene(page)).objects[0].keyframes[1]).toEqual(moved);
    await expect(page.getByLabel('Selected key time')).toHaveValue('3');
    await edit(page, () => page.getByRole('button', { name: 'Redo', exact: true }).click());
    expect((await uiScene(page)).objects).toEqual(retimed);
    await expect(page.getByLabel('Selected key time')).toHaveValue('7.5');
    expectedHttpFailures.add('400 /api/command');
    await page.getByLabel('Selected key time').fill('6');
    await page.getByRole('button', { name: 'Move key', exact: true }).click();
    await expect(page.locator('#toast')).toContainText('already has a pose');
    expect((await serverScene(request)).objects).toEqual(retimed);
    // Range errors are rejected by the real number control before submission.
    await page.getByLabel('Selected key time').fill('12.01');
    await page.getByRole('button', { name: 'Move key', exact: true }).click();
    expect(await page.getByLabel('Selected key time').evaluate(input => input.validity.rangeOverflow)).toBe(true);
    expect((await serverScene(request)).objects).toEqual(retimed);
    await page.getByLabel('Selected key time').fill('7.5');
    await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 12.00 seconds', exact: true }).click());
    const endpoint = (await uiScene(page)).objects[0].keyframes.at(-1);
    await page.locator('#art-canvas').scrollIntoViewIfNeeded(); await settleCanvas(page);
    const endPoint = await canvasPoint(page, { parameters: endpoint.parameters });
    scene = await edit(page, async () => {
      await page.mouse.move(endPoint.x, endPoint.y); await page.mouse.down();
      await page.mouse.move(endPoint.x - 22, endPoint.y - 15, { steps: 4 }); await page.mouse.up();
    });
    expect(scene.objects[0].keyframes[0]).toEqual(before.keyframes[0]);
    expect(scene.objects[0].keyframes.at(-1).parameters.x).not.toBe(endpoint.parameters.x);
    await expect(page.locator('#seam-status')).toHaveText('Loop seam: pose jump');
    await edit(page, () => page.getByRole('button', { name: 'Undo', exact: true }).click());
    await expect(page.locator('#seam-status')).toHaveText('Loop seam: matched');
    await edit(page, () => page.getByRole('button', { name: 'Go to keyframe 7.50 seconds', exact: true }).click());
    await page.locator('#art-canvas').scrollIntoViewIfNeeded(); await settleCanvas(page);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width + 1);
    await expect(page.locator('#toast')).toBeHidden();
    await screenshot(page, testInfo, `motion-path-${viewport.name}`);
    const saved = JSON.parse((await download(page, testInfo, 'json')).toString('utf8'));
    expect(saved.schema_version).toBe(4); expect(saved.objects).toEqual(retimed);
    await edit(page, () => page.getByRole('button', { name: 'Delete key', exact: true }).click());
    await page.getByRole('button', { name: /^Recipe/ }).click();
    const chooser = page.waitForEvent('filechooser'); await page.getByRole('button', { name: 'Load JSON', exact: true }).click();
    await edit(page, async () => (await chooser).setFiles({ name: 'motion-path.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(saved)) }));
    await page.reload(); await expect(page.locator('#canvas-loading')).toBeHidden();
    expect((await serverScene(request)).objects).toEqual(retimed);
  });
}

async function blendPathCount(page) {
  return page.evaluate(async () => {
    const {blendContours} = await import('/static/static-blend.js');
    const state=window.tidalStudio.getScene(),blend=state.blends[0];
    const first=state.objects.find(o=>o.id===blend.source_a),second=state.objects.find(o=>o.id===blend.source_b);
    return blendContours(first.parameters,second.parameters,blend.operation,blend.amount,2,128)[0].paths.length;
  });
}
for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test(`static confluence merges two sources and preserves live editing on ${viewport.name}`, async ({page,request},testInfo)=>{
    await page.setViewportSize({width:viewport.width,height:viewport.height});
    let scene = await edit(page,()=>page.getByRole('button',{name:'Try confluence',exact:true}).click());
    expect(scene.title).toBe('Confluence study');expect(scene.schema_version).toBe(4);
    expect(scene.objects).toHaveLength(2);expect(scene.blends).toHaveLength(1);
    const original=structuredClone(scene.objects);
    expect(await blendPathCount(page)).toBe(1);
    await edit(page,()=>page.getByRole('button',{name:'Remove blend',exact:true}).click());
    expect((await uiScene(page)).objects).toEqual(original);
    await page.getByLabel('Blend operation').selectOption('union');
    scene = await edit(page,()=>page.getByRole('button',{name:'Create blend',exact:true}).click());
    expect(await blendPathCount(page)).toBe(2);expect(scene.objects).toEqual(original);
    await expect(page.getByRole('slider',{name:'Blend amount',exact:true})).toBeDisabled();
    await page.getByLabel('Blend operation').selectOption('smooth_union');
    await edit(page,()=>page.getByRole('button',{name:'Apply blend',exact:true}).click());
    expect(await blendPathCount(page)).toBe(1);
    await page.getByLabel('Blend source A').selectOption(original[1].id);
    await expect(page.getByRole('button',{name:'Apply blend',exact:true})).toBeDisabled();
    await page.getByLabel('Blend source A').selectOption(original[0].id);
    await page.getByRole('slider',{name:'Blend amount',exact:true}).focus();
    await edit(page,()=>page.keyboard.press('Home'));
    expect((await uiScene(page)).blends[0].amount).toBe(0);expect(await blendPathCount(page)).toBe(2);
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());
    expect(await blendPathCount(page)).toBe(1);
    await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());
    expect(await blendPathCount(page)).toBe(2);
    await page.getByRole('slider',{name:'Blend amount',exact:true}).focus();
    await edit(page,()=>page.keyboard.press('End'));
    expect((await uiScene(page)).blends[0].amount).toBe(1);
    await edit(page,()=>page.getByRole('button',{name:'Edit A',exact:true}).click());
    await expect(page.getByRole('button',{name:'Capture pose',exact:true})).toBeDisabled();
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
    const point=await canvasPoint(page,original[0]);
    scene=await edit(page,async()=>{await page.mouse.move(point.x,point.y);await page.mouse.down();await page.mouse.move(point.x+16,point.y+8,{steps:4});await page.mouse.up();});
    expect(scene.objects[0].parameters.x).not.toBe(original[0].parameters.x);
    expect(scene.objects[0].keyframes).toEqual([]);expect(scene.blends[0].source_a).toBe(original[0].id);
    const edited=structuredClone(scene.objects);
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect((await uiScene(page)).objects).toEqual(original);
    await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());expect((await uiScene(page)).objects).toEqual(edited);
    await edit(page,()=>page.getByLabel('Show blend',{exact:true}).uncheck());
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);await expect(page.locator('#toast')).toBeHidden();
    await screenshot(page,testInfo,`confluence-separate-${viewport.name}`);
    await edit(page,()=>page.getByLabel('Show blend',{exact:true}).check());
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width+1);
    await screenshot(page,testInfo,`confluence-merged-${viewport.name}`);
    const saved=JSON.parse((await download(page,testInfo,'json')).toString('utf8'));
    expect(saved.schema_version).toBe(4);expect(saved.objects).toEqual(edited);expect(saved.blends).toHaveLength(1);
    const svg=(await download(page,testInfo,'svg')).toString('utf8');expect(svg).toContain(`id="${saved.blends[0].id}"`);expect(svg).toContain('fill-rule="evenodd"');
    await edit(page,()=>page.getByRole('button',{name:'Remove blend',exact:true}).click());
    await page.getByRole('button',{name:/^Recipe/}).click();const chooser=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Load JSON',exact:true}).click();
    await edit(page,async()=> (await chooser).setFiles({name:'confluence.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))}));
    await page.reload();await expect(page.locator('#canvas-loading')).toBeHidden();
    const restored=await serverScene(request);expect(restored.objects).toEqual(saved.objects);expect(restored.blends).toEqual(saved.blends);
  });
}

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test(`layered study supports ordered selection, group alpha and hidden source edits on ${viewport.name}`,async({page,request},testInfo)=>{
    await page.setViewportSize({width:viewport.width,height:viewport.height});
    let scene=await edit(page,()=>page.getByRole('button',{name:'Try layered study',exact:true}).click());
    expect(scene.schema_version).toBe(4);expect(scene.layer_order).toEqual(['island_ember','island_lagoon','island_lowtide','blend_confluence','island_glass']);
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue('blend_confluence');
    const original=structuredClone(scene);
    // Actual Chromium raster API confirms alpha applies once to the entire layer.
    const pixel=await page.evaluate(async()=>{
      const {compositeLayer}=await import('/static/layers.js'),target=document.createElement('canvas'),buffer=document.createElement('canvas');
      target.width=buffer.width=4;target.height=buffer.height=4;const c=target.getContext('2d');c.fillStyle='blue';c.fillRect(0,0,4,4);
      compositeLayer(c,buffer,.5,layer=>{layer.fillStyle='red';layer.fillRect(0,0,4,4);layer.fillRect(0,0,4,4);});return [...c.getImageData(2,2,1,1).data];
    });expect(pixel[0]).toBeGreaterThanOrEqual(127);expect(pixel[0]).toBeLessThanOrEqual(129);expect(pixel[1]).toBe(0);expect(pixel[2]).toBeGreaterThanOrEqual(126);expect(pixel[2]).toBeLessThanOrEqual(128);expect(pixel[3]).toBe(255);
    await testInfo.attach('actual-group-alpha',{body:JSON.stringify({pixel,expected:[128,0,127,255],roundingTolerance:1}),contentType:'application/json'});
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
    const center=await canvasPoint(page,scene.objects.find(o=>o.id==='island_glass'));
    scene=await edit(page,()=>page.mouse.click(center.x,center.y));expect(scene.selection).toEqual(['island_glass']);
    await settleCanvas(page);await screenshot(page,testInfo,`glasswater-front-${viewport.name}`);
    await page.getByLabel('Layer palette',{exact:true}).selectOption('ember');
    await expect.poll(async()=>(await uiScene(page)).objects.find(o=>o.id==='island_glass').style.palette).toBe('ember');
    await page.getByRole('slider',{name:'Layer opacity',exact:true}).focus();scene=await edit(page,()=>page.keyboard.press('Home'));expect(scene.objects.at(-1).style.opacity).toBe(.05);
    await page.getByRole('slider',{name:'Layer opacity',exact:true}).focus();scene=await edit(page,()=>page.keyboard.press('End'));expect(scene.objects.at(-1).style.opacity).toBe(1);
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());
    await page.getByRole('button',{name:'Send Glass veil backward',exact:true}).focus();scene=await edit(page,()=>page.keyboard.press('Enter'));
    expect(scene.layer_order.at(-1)).toBe('blend_confluence');
    await expect(page.getByRole('button',{name:'Send Glass veil backward',exact:true})).toBeFocused();
    // With the veil behind the blend, the same artwork point selects the front blend.
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
    const reorderedCenter=await canvasPoint(page,scene.objects.find(o=>o.id==='island_glass'));
    scene=await edit(page,()=>page.mouse.click(reorderedCenter.x,reorderedCenter.y));expect(scene.selection).toEqual(['blend_confluence']);
    await expect(page.getByRole('slider',{name:'Island scale',exact:true})).toBeDisabled();
    await page.getByRole('button',{name:'Hide Gold confluence',exact:true}).focus();scene=await edit(page,()=>page.keyboard.press('Space'));
    expect(scene.blends[0].style.visible).toBe(false);
    scene=await edit(page,()=>page.getByRole('button',{name:'Show Gold confluence',exact:true}).click());expect(scene.blends[0].style.visible).toBe(true);
    await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());
    scene=await edit(page,()=>page.getByRole('button',{name:'Hide Solstice',exact:true}).click());expect(scene.objects[0].style.visible).toBe(false);
    await expect(page.locator('#layer-status')).toContainText('Hidden artwork');await expect(page.getByRole('button',{name:'Remove',exact:true})).toBeDisabled();
    await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
    const sourcePoint=await canvasPoint(page,scene.objects[0]);
    scene=await edit(page,async()=>{await page.mouse.move(sourcePoint.x,sourcePoint.y);await page.mouse.down();await page.mouse.move(sourcePoint.x+12,sourcePoint.y+6,{steps:3});await page.mouse.up();});
    expect(scene.objects[0].parameters.x).not.toBe(original.objects[0].parameters.x);expect(scene.objects[0].style.visible).toBe(false);expect(scene.blends[0].source_a).toBe('island_ember');
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect((await uiScene(page)).objects[0].parameters).toEqual(original.objects[0].parameters);
    await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());
    expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width+1);
    await expect(page.locator('#toast')).toBeHidden();await screenshot(page,testInfo,`glasswater-layers-${viewport.name}`);
    const saved=JSON.parse((await download(page,testInfo,'json')).toString('utf8'));
    const svg=(await download(page,testInfo,'svg')).toString('utf8');expect(svg.indexOf('id="island_glass"')).toBeLessThan(svg.indexOf('id="blend_confluence"'));expect(svg).toContain('opacity="0.42"');
    await edit(page,()=>page.getByRole('button',{name:'Remove blend',exact:true}).click());expect((await uiScene(page)).objects).toEqual(saved.objects);
    await page.getByRole('button',{name:/^Recipe/}).click();const chooser=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Load JSON',exact:true}).click();
    await edit(page,async()=> (await chooser).setFiles({name:'glasswater.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))}));
    await page.reload();await expect(page.locator('#canvas-loading')).toBeHidden();const restored=await serverScene(request);
    expect(restored.layer_order).toEqual(saved.layer_order);expect(restored.objects).toEqual(saved.objects);expect(restored.blends).toEqual(saved.blends);
  });
}

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test(`coauthor history shows real protocol edits and shared manual undo on ${viewport.name}`,async({page,request},testInfo)=>{
    await page.setViewportSize({width:viewport.width,height:viewport.height});
    await page.getByRole('button',{name:'Client setup',exact:true}).click();
    await expect(page.locator('#stdio-settings')).toContainText('studio.mcp_server');
    await expect(page.getByRole('dialog')).toContainText('not proof of live model inference');
    await expect(page.getByRole('dialog')).toContainText('expected_revision');
    await page.getByRole('button',{name:'Close dialog',exact:true}).click();
    const before=await serverScene(request),original=structuredClone(before.objects[0]);
    const authored=await actualMcp(testInfo,'batch',{expected_revision:before.revision,request_id:randomUUID(),label:'<b>Verified live agent</b>',commands:[{op:'update_geometry',id:first.id,parameters:{radius:240}},{op:'set_style',id:first.id,style:{palette:'mono',opacity:.7}}]});
    expect(authored.ok).toBe(true);const mcpRevision=authored.scene.revision;
    await expect.poll(async()=>(await uiScene(page)).revision).toBe(mcpRevision);
    const mcpRow=page.locator(`.coauthor-entry[data-revision="${mcpRevision}"]`);
    await expect(mcpRow.locator('.source-badge')).toHaveText('MCP protocol');await expect(mcpRow.locator('strong')).toHaveText('Updated 1 layer');
    await mcpRow.locator('summary').click();await expect(mcpRow).toContainText('Client note: <b>Verified live agent</b>');expect(await mcpRow.locator('b').count()).toBe(0);
    await selectFirst(page);await page.getByRole('slider',{name:'Island scale',exact:true}).focus();
    let scene=await edit(page,()=>page.keyboard.press('ArrowRight'));expect(scene.objects[0].parameters.radius).not.toBe(240);
    const stale=await actualMcp(testInfo,'set_style',{id:first.id,style:{opacity:.9},expected_revision:mcpRevision});expect(stale.error.code).toBe('revision_conflict');
    expect((await serverScene(request)).revision).toBe(scene.revision);
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect((await uiScene(page)).objects[0].parameters.radius).toBe(240);
    await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click()); // Undo selection.
    scene=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(scene.objects[0]).toEqual(original);
    const undoRow=page.locator(`.coauthor-entry[data-revision="${scene.revision}"]`);await expect(undoRow).toContainText(`undo of revision ${mcpRevision}`);await expect(undoRow.locator('.source-badge')).toHaveText('UI / HTTP');
    const redone=await actualMcp(testInfo,'redo',{expected_revision:scene.revision});expect(redone.ok).toBe(true);await expect.poll(async()=>(await uiScene(page)).revision).toBe(redone.scene.revision);
    expect((await uiScene(page)).objects[0].parameters.radius).toBe(240);
    const bridge=await request.post('/api/tools/set_style',{headers:{'X-Studio-Actor':'mcp'},data:{id:first.id,style:{opacity:.55},expected_revision:redone.scene.revision}});expect(bridge.ok()).toBe(true);
    scene=(await bridge.json()).scene;await expect.poll(async()=>(await uiScene(page)).revision).toBe(scene.revision);
    await page.getByLabel('Coauthor activity route',{exact:true}).selectOption('tool_http');
    const bridgeRow=page.locator(`.coauthor-entry[data-revision="${scene.revision}"]`);await expect(bridgeRow.locator('.source-badge')).toHaveText('WebMCP / HTTP bridge');await bridgeRow.locator('summary').click();await expect(bridgeRow).toContainText('Caller transport hint: mcp (unverified)');
    await page.getByLabel('Coauthor activity route',{exact:true}).selectOption('mcp_protocol');await expect(mcpRow).toBeVisible();await expect(page.locator('.coauthor-entry[data-source="tool_http"]')).toHaveCount(0);
    await page.getByLabel('Coauthor activity route',{exact:true}).selectOption('all');
    await page.locator('#coauthor-panel').scrollIntoViewIfNeeded();await expect(page.locator('#coauthor-panel')).toContainText('not who sent it');
    expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width+1);
    await expect(page.locator('#toast')).toBeHidden();await screenshot(page,testInfo,`coauthor-history-${viewport.name}`);
    const saved=JSON.parse((await download(page,testInfo,'json')).toString('utf8'));expect(saved.schema_version).toBe(4);expect(saved.history).toBeUndefined();
    await page.getByRole('button',{name:/^Recipe/}).click();const chooser=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Load JSON',exact:true}).click();
    await edit(page,async()=> (await chooser).setFiles({name:'coauthored.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))}));
    await page.reload();await expect(page.locator('#canvas-loading')).toBeHidden();scene=await serverScene(request);expect(scene.objects).toEqual(saved.objects);expect(scene.layer_order).toEqual(saved.layer_order);
    expect(scene.history.entries.at(-1).source.entrypoint).toBe('manual_http');await expect(page.locator('#coauthor-count')).toContainText('observed MCP commits');
  });
}

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test(`blend editor choice survives existing canvas selection on ${viewport.name}`,async({page,request})=>{
    await page.setViewportSize({width:viewport.width,height:viewport.height});
    let scene=await edit(page,()=>page.getByRole('button',{name:'Try confluence',exact:true}).click());
    const originalBlend=scene.blends[0];
    await edit(page,()=>page.locator(`[data-layer-action="select"][data-id="${originalBlend.id}"]`).click());
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(originalBlend.id);
    await page.getByLabel('Blend composition',{exact:true}).selectOption('');
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue('');
    await expect(page.getByRole('button',{name:'Create blend',exact:true})).toBeEnabled();
    scene=await edit(page,()=>page.getByRole('button',{name:'Create blend',exact:true}).click());
    const second=scene.blends[1];expect(scene.selection).toEqual([originalBlend.id]);
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(second.id);
    await page.getByLabel('Blend composition',{exact:true}).selectOption(originalBlend.id);
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(originalBlend.id);
    await page.getByLabel('Blend composition',{exact:true}).selectOption(second.id);
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(second.id);
    await page.evaluate(()=>window.tidalStudio.refresh({initial:true})); // Forced same snapshot must retain editor choice.
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(second.id);
    await edit(page,()=>page.locator(`[data-layer-action="select"][data-id="${originalBlend.id}"]`).click());
    await expect(page.getByLabel('Blend composition',{exact:true})).toHaveValue(originalBlend.id);
    const observed=await serverScene(request);expect(observed.blends).toHaveLength(2);expect(observed.selection).toEqual([originalBlend.id]);
  });
}

test('same-revision restarted snapshot clears a gesture and refreshes history without stopping playback',async({page,request},testInfo)=>{
  await selectFirst(page);
  await edit(page,()=>page.getByRole('button',{name:'Play animation',exact:true}).click());
  const before=await serverScene(request);
  expect(before.history.can_undo).toBe(true);
  const storage=testInfo.outputPath('restart-scene.json');
  const persisted=Object.fromEntries(['schema_version','title','objects','blends','layer_order','view','animation','document_id','revision','selection'].map(key=>[key,before[key]]));
  await writeFile(storage,JSON.stringify(persisted));
  const program='import json,sys; from studio.service import SceneService; print(json.dumps(SceneService(sys.argv[1]).snapshot()))';
  const restarted=JSON.parse((await execFileAsync(process.env.STUDIO_PYTHON||'python',['-c',program,storage],{timeout:15000})).stdout);
  expect(restarted.session_id).not.toBe(before.session_id);expect(restarted.document_id).toBe(before.document_id);expect(restarted.revision).toBe(before.revision);expect(restarted.objects).toEqual(before.objects);
  const slider=page.getByRole('slider',{name:'Layer opacity',exact:true});await slider.scrollIntoViewIfNeeded();const box=await slider.boundingBox();
  await page.mouse.move(box.x+box.width-4,box.y+box.height/2);await page.mouse.down();await page.mouse.move(box.x+box.width*.6,box.y+box.height/2,{steps:3});
  const preview=await slider.inputValue();expect(preview).not.toBe('100');
  let delivered=restarted;
  // Simulated network restart delivers a genuine new SceneService snapshot;
  // the owned Playwright server/user demo is never restarted by this test.
  await page.route('**/api/scene',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(delivered)}));
  await page.evaluate(()=>window.tidalStudio.refresh());
  await expect(slider).toHaveValue('100');await expect(slider).toBeDisabled();
  expect((await uiScene(page)).session_id).toBe(restarted.session_id);
  await expect(page.locator('#toast')).toContainText('session changed');
  expect((await serverScene(request)).objects).toEqual(before.objects);
  expect((await serverScene(request)).revision).toBe(before.revision);
  await expect(page.getByRole('button',{name:'Pause animation',exact:true})).toBeVisible();
  await page.keyboard.press('Escape');await page.mouse.up();
  // Playback and persisted artwork remain; process-local history is refreshed.
  await expect.poll(async()=>(await uiScene(page)).session_id).toBe(restarted.session_id);
  await expect(page.getByRole('button',{name:'Undo',exact:true})).toBeDisabled();await expect(page.getByRole('button',{name:'Redo',exact:true})).toBeDisabled();
  await expect(page.locator('#coauthor-count')).toContainText('0 observed MCP commits');
  await expect(page.locator('#coauthor-history-note')).toContainText('0 commits this process');await expect(page.locator('.coauthor-entry')).toHaveCount(0);
  expect((await uiScene(page)).session_id).toBe(restarted.session_id);expect((await uiScene(page)).objects).toEqual(before.objects);
  await expect(page.getByRole('button',{name:'Pause animation',exact:true})).toBeVisible();
  expect((await uiScene(page)).revision).toBe(before.revision);expect((await uiScene(page)).animation.playing).toBe(true);
  await screenshot(page,testInfo,'restart-history-reset');
  delivered=before;await page.evaluate(()=>window.tidalStudio.refresh());
  expect((await uiScene(page)).session_id).toBe(restarted.session_id);await expect(page.getByRole('button',{name:'Undo',exact:true})).toBeDisabled();
  await testInfo.attach('restart-snapshot-evidence',{body:JSON.stringify({before,restarted,delivery:'simulated HTTP delivery of actual restarted service snapshot'}),contentType:'application/json'});
});

for (const [name, viewport] of [['desktop', {width:1440,height:1100}], ['phone', {width:390,height:844}]]) {
  test.describe(`keyboard continuity ${name}`, () => {
    test.use({viewport});
    test('slider retains focus across committed keyboard edits', async ({page}) => {
      const slider=page.getByRole('slider',{name:'Animation playhead',exact:true});
      await slider.focus();
      const before=Number(await slider.inputValue());
      await edit(page,()=>page.keyboard.press('ArrowRight'));
      await expect(slider).toBeFocused();
      await edit(page,()=>page.keyboard.press('ArrowRight'));
      await expect(slider).toBeFocused();
      expect(Number(await slider.inputValue())).toBeCloseTo(before+.02,2);
      await selectFirst(page);
      const shape=page.getByRole('slider',{name:'Island scale',exact:true});
      await shape.focus();await edit(page,()=>page.keyboard.press('ArrowRight'));
      await expect(shape).toBeFocused();await edit(page,()=>page.keyboard.press('ArrowRight'));
      // Moving focus during a slower save must take precedence over restoration.
      await page.route('**/api/command',async route=>{await new Promise(resolve=>setTimeout(resolve,200));await route.continue();});
      await shape.focus();await page.keyboard.press('ArrowRight');await expect(shape).toBeDisabled();
      await page.locator('#canvas-tab').focus();
      await expect(page.locator('#save-status')).toHaveText('Scene synchronized');
      await expect(page.locator('#canvas-tab')).toBeFocused();await page.unroute('**/api/command');
    });
  });
}

test('zero-size layout recovers when the canvas becomes visible', async ({page},testInfo) => {
  const oldRevision=(await uiScene(page)).revision;
  await page.addStyleTag({content:'#canvas-stage { width:0!important; height:0!important; min-width:0!important; min-height:0!important; overflow:hidden!important; } #art-canvas { width:0!important; height:0!important; }'});
  await expect.poll(()=>page.locator('#art-canvas').evaluate(c=>c.width)).toBe(0);
  await page.evaluate(()=>window.tidalStudio.refresh({force:true}));
  await settleCanvas(page);
  await page.locator('style').last().evaluate(s=>s.remove());
  await expect.poll(()=>page.locator('#art-canvas').evaluate(c=>c.width)).toBeGreaterThan(0);
  await settleCanvas(page);expect((await uiScene(page)).revision).toBe(oldRevision);
  await screenshot(page,testInfo,'recovered-canvas-layout');
});

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test.describe(`group authoring ${viewport.name}`,()=>{
    test.use({viewport});
    test('multi-selection moves, scales, rotates, drags and exports one coherent group',async({page},testInfo)=>{
      const original=await uiScene(page),ids=original.objects.slice(0,2).map(o=>o.id);
      if(viewport.name==='desktop') {
        await edit(page,()=>page.getByRole('button',{name:`Select ${original.objects[0].name}`,exact:true}).click());
        await edit(page,()=>page.getByRole('button',{name:`Select ${original.objects[1].name}`,exact:true}).click({modifiers:['Shift']}));
      } else {
        await page.getByRole('button',{name:'Select multiple',exact:true}).click();
        for(const object of original.objects.slice(0,2))await edit(page,()=>page.getByRole('button',{name:`Select ${object.name}`,exact:true}).click());
        await page.getByRole('button',{name:'Done selecting',exact:true}).click();
      }
      await expect(page.locator('#selection-count')).toHaveText('2');
      await expect(page.getByRole('slider',{name:'Island scale',exact:true})).toBeDisabled();
      await expect(page.getByLabel('Layer palette',{exact:true})).toBeDisabled();
      const before=await uiScene(page);
      let scene=await edit(page,()=>page.getByRole('button',{name:'Move selection right',exact:true}).click());
      for(const id of ids)expect(scene.objects.find(o=>o.id===id).parameters.x).toBe(before.objects.find(o=>o.id===id).parameters.x+10);
      await expect(page.getByRole('button',{name:'Move selection right',exact:true})).toBeFocused();
      scene=await edit(page,()=>page.keyboard.press('Space'));
      for(const id of ids)expect(scene.objects.find(o=>o.id===id).parameters.x).toBe(before.objects.find(o=>o.id===id).parameters.x+20);
      expect(scene.objects[2]).toEqual(before.objects[2]);
      const moved=structuredClone(scene);
      await page.getByLabel('Group scale factor',{exact:true}).fill('1.10');
      scene=await edit(page,()=>page.getByRole('button',{name:'Scale selection',exact:true}).click());
      for(const id of ids)expect(scene.objects.find(o=>o.id===id).parameters.radius).toBeCloseTo(moved.objects.find(o=>o.id===id).parameters.radius*1.1,8);
      const scaled=structuredClone(scene);
      await page.getByLabel('Group rotation',{exact:true}).fill('15');
      scene=await edit(page,()=>page.getByRole('button',{name:'Rotate selection',exact:true}).click());
      for(const id of ids)expect(scene.objects.find(o=>o.id===id).parameters.rotation).toBeCloseTo(scaled.objects.find(o=>o.id===id).parameters.rotation+15,8);
      expect(scene.selection).toEqual(ids);
      await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
      const beforeDrag=structuredClone(scene),point=await canvasPoint(page,scene.objects[0]);
      await page.mouse.move(point.x,point.y);await page.mouse.down();await page.mouse.move(point.x+24,point.y+12,{steps:5});
      scene=await edit(page,()=>page.mouse.up());
      for(const id of ids){const a=beforeDrag.objects.find(o=>o.id===id).parameters,b=scene.objects.find(o=>o.id===id).parameters;expect(b.x-a.x).toBeCloseTo(24/point.scale,6);expect(b.y-a.y).toBeCloseTo(12/point.scale,6);}
      expect(scene.objects[2]).toEqual(before.objects[2]);
      const afterDrag=structuredClone(scene),cancelPoint=await canvasPoint(page,scene.objects[0]);
      await page.mouse.move(cancelPoint.x,cancelPoint.y);await page.mouse.down();await page.mouse.move(cancelPoint.x+20,cancelPoint.y+10,{steps:3});await page.keyboard.press('Escape');await page.mouse.up();
      expect((await uiScene(page)).revision).toBe(afterDrag.revision);expect((await uiScene(page)).objects).toEqual(afterDrag.objects);
      scene=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(scene.objects).toEqual(beforeDrag.objects);expect(scene.selection).toEqual(ids);
      scene=await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());expect(scene.objects).toEqual(afterDrag.objects);
      await page.getByLabel('Group scale factor',{exact:true}).fill('4');
      await page.getByRole('button',{name:'Scale selection',exact:true}).click();await expect(page.locator('#toast')).toContainText('use a smaller change');
      expect((await uiScene(page)).revision).toBe(scene.revision);expect((await uiScene(page)).objects).toEqual(scene.objects);
      await page.getByLabel('Group scale factor',{exact:true}).fill('1.10');
      const saved=await download(page,testInfo,'json');const recipe=JSON.parse(saved.toString('utf8'));expect(recipe.schema_version).toBe(4);expect(recipe.objects).toEqual(scene.objects);
      await settleCanvas(page);await screenshot(page,testInfo,`arranged-group-${viewport.name}`);
      await page.locator('.group-section').screenshot({path:testInfo.outputPath(`arrange-controls-${viewport.name}.png`)});
    });
  });
}

test('group arrangement moves every authored key without adding poses',async({page},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Play demo',exact:true}).click());
  await edit(page,()=>page.getByRole('button',{name:'Pause animation',exact:true}).click());
  const starting=await uiScene(page),names=starting.objects.slice(0,2).map(o=>o.name);
  await page.getByRole('button',{name:'Select multiple',exact:true}).click();
  for(const name of names)await edit(page,()=>page.getByRole('button',{name:`Select ${name}`,exact:true}).click());
  await page.getByRole('button',{name:'Done selecting',exact:true}).click();
  const before=await uiScene(page);
  const after=await edit(page,()=>page.getByRole('button',{name:'Move selection right',exact:true}).click());
  for(let i=0;i<2;i++){expect(after.objects[i].keyframes).toHaveLength(before.objects[i].keyframes.length);for(let k=0;k<before.objects[i].keyframes.length;k++){expect(after.objects[i].keyframes[k].parameters.x).toBe(before.objects[i].keyframes[k].parameters.x+10);expect(after.objects[i].keyframes[k].time).toBe(before.objects[i].keyframes[k].time);expect(after.objects[i].keyframes[k].easing).toBe(before.objects[i].keyframes[k].easing);}}
  expect(after.objects[2]).toEqual(before.objects[2]);
  expect((await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click())).objects).toEqual(before.objects);
  await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());await settleCanvas(page);
  await screenshot(page,testInfo,'whole-path-arrangement');
});

test('selected blend and its source move retained operands only once',async({page},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Try layered study',exact:true}).click());
  await page.getByRole('button',{name:'Select multiple',exact:true}).click();
  // Loading the study selects nothing. Blend plus its operand must deduplicate sources.
  for(const id of ['blend_confluence','island_ember','island_glass'])await edit(page,()=>page.locator(`[data-layer-action="select"][data-id="${id}"]`).click());
  await page.getByRole('button',{name:'Done selecting',exact:true}).click();
  const before=await uiScene(page);
  await expect(page.locator('#selection-summary')).toContainText('3 islands');
  const after=await edit(page,()=>page.getByRole('button',{name:'Move selection right',exact:true}).click());
  for(const id of ['island_ember','island_lagoon','island_glass'])expect(after.objects.find(o=>o.id===id).parameters.x).toBe(before.objects.find(o=>o.id===id).parameters.x+10);
  expect(after.objects.find(o=>o.id==='island_lowtide')).toEqual(before.objects.find(o=>o.id==='island_lowtide'));
  expect(after.blends).toEqual(before.blends);expect(after.layer_order).toEqual(before.layer_order);
  await settleCanvas(page);await screenshot(page,testInfo,'retained-source-group');
});

test('invalid and stale group drags cannot partially commit',async({page,expectedHttpFailures},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Select visible',exact:true}).click());
  const before=await uiScene(page);await page.locator('#art-canvas').scrollIntoViewIfNeeded();await settleCanvas(page);
  let point=await canvasPoint(page,before.objects[0]);
  await page.mouse.move(point.x,point.y);await page.mouse.down();await page.mouse.move(point.x+3000*point.scale,point.y,{steps:3});await page.mouse.up();
  await expect(page.locator('#toast')).toContainText('Nothing was saved');expect((await uiScene(page)).objects).toEqual(before.objects);expect((await uiScene(page)).revision).toBe(before.revision);
  point=await canvasPoint(page,before.objects[0]);await page.mouse.move(point.x,point.y);await page.mouse.down();await page.mouse.move(point.x+24,point.y+10,{steps:3});
  const changed=await actualMcp(testInfo,'transform_layers',{ids:before.selection,dx:-5,expected_revision:before.revision,request_id:`group-${randomUUID()}`});
  expect(changed.ok).toBeTruthy();expectedHttpFailures.add('409 /api/command');await page.mouse.up();
  await expect(page.locator('#toast')).toContainText('changed elsewhere');
  await expect.poll(async()=>(await uiScene(page)).revision).toBe(changed.scene.revision);
  expect((await uiScene(page)).objects).toEqual(changed.scene.objects);
  expect((await uiScene(page)).selection).toEqual(before.selection);
});

async function layoutStudy(page,request) {
  const recipe=structuredClone(seed);recipe.title='Quiet intervals — center study';
  recipe.objects.forEach((island,index)=>{island.parameters.x=[220,390,780][index];island.parameters.y=[310,440,340][index];island.parameters.radius=130;island.style.opacity=.95;});
  const state=await serverScene(request);
  const response=await request.post('/api/command',{data:{op:'load_recipe',recipe,expected_revision:state.revision}});expect(response.ok()).toBe(true);
  await page.evaluate(()=>window.tidalStudio.refresh({force:true}));
  await edit(page,()=>page.getByRole('button',{name:'Select visible',exact:true}).click());
  return uiScene(page);
}

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test.describe(`center layout ${viewport.name}`,()=>{
    test.use({viewport});
    test('center alignment and spacing preview, cancel, apply, undo and export',async({page,request},testInfo)=>{
      await expect(page.getByRole('button',{name:'Align horizontal',exact:true})).toBeDisabled();
      const before=await layoutStudy(page,request);
      await page.getByRole('button',{name:'Space horizontally',exact:true}).click();
      await expect(page.locator('#layout-status')).toContainText('preview at 0.00s');
      expect((await uiScene(page)).objects).toEqual(before.objects);expect((await serverScene(request)).revision).toBe(before.revision);
      await page.getByRole('button',{name:'Cancel preview',exact:true}).click();
      await expect(page.getByRole('button',{name:'Apply layout',exact:true})).toBeHidden();expect((await uiScene(page)).revision).toBe(before.revision);
      await page.getByRole('button',{name:'Space horizontally',exact:true}).click();await page.keyboard.press('Escape');
      expect((await uiScene(page)).objects).toEqual(before.objects);
      await page.getByRole('button',{name:'Space horizontally',exact:true}).click();
      let spaced=await edit(page,()=>page.getByRole('button',{name:'Apply layout',exact:true}).click());
      const xs=spaced.objects.map(object=>object.parameters.x).sort((a,b)=>a-b);expect(xs).toEqual([220,500,780]);
      for(let i=0;i<3;i++)expect(spaced.objects[i].parameters.y).toBe(before.objects[i].parameters.y);
      await page.getByRole('button',{name:'Space horizontally',exact:true}).click();await expect(page.locator('#toast')).toContainText('Nothing to apply');expect((await uiScene(page)).revision).toBe(spaced.revision);
      await page.getByRole('button',{name:'Align horizontal',exact:true}).click();
      const aligned=await edit(page,()=>page.getByRole('button',{name:'Apply layout',exact:true}).click());
      const mean=before.objects.reduce((sum,object)=>sum+object.parameters.y,0)/3;
      for(const object of aligned.objects)expect(object.parameters.y).toBeCloseTo(mean,8);
      expect((await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click())).objects).toEqual(spaced.objects);
      expect((await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click())).objects).toEqual(aligned.objects);
      const json=JSON.parse((await download(page,testInfo,'json')).toString());expect(json.schema_version).toBe(4);expect(json.objects).toEqual(aligned.objects);
      await settleCanvas(page);await screenshot(page,testInfo,`center-layout-${viewport.name}`);
      await page.locator('.layout-controls').screenshot({path:testInfo.outputPath(`layout-controls-${viewport.name}.png`)});
    });
  });
}

test('layout selection edges preserve hidden and retained-source state',async({page},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Try layered study',exact:true}).click());
  await edit(page,()=>page.locator('[data-layer-action="select"][data-id="blend_confluence"]').click());
  await expect(page.getByRole('button',{name:'Align horizontal',exact:true})).toBeDisabled();await expect(page.locator('#layout-status')).toContainText('island rows rather than blend');
  await page.getByRole('button',{name:'Select multiple',exact:true}).click();
  await edit(page,()=>page.locator('[data-layer-action="select"][data-id="blend_confluence"]').click());
  await edit(page,()=>page.locator('[data-layer-action="select"][data-id="island_ember"]').click());
  await edit(page,()=>page.locator('[data-layer-action="select"][data-id="island_lagoon"]').click());
  await page.getByRole('button',{name:'Done selecting',exact:true}).click();
  await expect(page.getByRole('button',{name:'Space horizontally',exact:true})).toBeDisabled();
  await edit(page,()=>page.locator('[data-layer-action="visibility"][data-id="island_ember"]').click());
  const before=await uiScene(page);
  await page.getByRole('button',{name:'Align vertical',exact:true}).click();
  const after=await edit(page,()=>page.getByRole('button',{name:'Apply layout',exact:true}).click());
  expect(after.blends).toEqual(before.blends);expect(after.objects[2]).toEqual(before.objects[2]);expect(after.layer_order).toEqual(before.layer_order);
  expect(after.objects[0].style.visible).toBe(before.objects[0].style.visible);expect(after.objects[1].style.visible).toBe(before.objects[1].style.visible);
  await settleCanvas(page);await screenshot(page,testInfo,'retained-source-layout');
});

test('layout at an authored playhead translates every key and pauses only on apply',async({page},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Play demo',exact:true}).click());
  await edit(page,()=>page.getByRole('button',{name:'Select visible',exact:true}).click());
  const before=await uiScene(page);
  await page.getByRole('button',{name:'Align horizontal',exact:true}).click();
  const freeze=await page.locator('#time-value').textContent();expect((await uiScene(page)).animation.playing).toBe(true);
  const after=await edit(page,()=>page.getByRole('button',{name:'Apply layout',exact:true}).click());expect(after.animation.playing).toBe(false);
  expect(after.animation.time).toBeCloseTo(Number(freeze),2);
  for(let i=0;i<3;i++){
    const dy=after.objects[i].parameters.y-before.objects[i].parameters.y;
    expect(after.objects[i].keyframes).toHaveLength(before.objects[i].keyframes.length);
    for(let k=0;k<before.objects[i].keyframes.length;k++){expect(after.objects[i].keyframes[k].parameters.y-before.objects[i].keyframes[k].parameters.y).toBeCloseTo(dy,8);expect(after.objects[i].keyframes[k].time).toBe(before.objects[i].keyframes[k].time);expect(after.objects[i].keyframes[k].easing).toBe(before.objects[i].keyframes[k].easing);}
  }
  await settleCanvas(page);await screenshot(page,testInfo,'whole-track-center-layout');
});

test('stale layout preview cannot overwrite a real client edit',async({page,request,expectedHttpFailures},testInfo)=>{
  const before=await layoutStudy(page,request);
  await page.getByRole('button',{name:'Align horizontal',exact:true}).click();
  const peer=await actualMcp(testInfo,'set_style',{id:before.objects[0].id,style:{opacity:.8},expected_revision:before.revision,request_id:`layout-peer-${randomUUID()}`});expect(peer.ok).toBe(true);
  expectedHttpFailures.add('409 /api/command');await page.getByRole('button',{name:'Apply layout',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('changed elsewhere');await expect.poll(async()=>(await uiScene(page)).revision).toBe(peer.scene.revision);
  expect((await uiScene(page)).objects).toEqual(peer.scene.objects);await expect(page.getByRole('button',{name:'Apply layout',exact:true})).toBeHidden();
});

async function retimeStudy(page,request,{playing=false,interior=false}={}) {
  const recipe=JSON.parse(await readFile(new URL('../../examples/tidal_atlas_choreography.json',import.meta.url),'utf8'));
  recipe.animation.playing=playing;recipe.animation.time=4;recipe.title='A later bloom — motion study';
  if(interior)for(const object of recipe.objects)object.keyframes.forEach((key,i)=>key.time=[1,3,6,9,11][i]);
  const before=await serverScene(request);
  const reset=await request.post('/api/command',{data:{op:'load_recipe',recipe,expected_revision:before.revision,request_id:randomUUID()}});expect(reset.ok()).toBeTruthy();
  await page.reload();await expect(page.locator('#canvas-loading')).toBeHidden();
  await edit(page,()=>page.getByRole('button',{name:`Select ${recipe.objects[0].name}`,exact:true}).click());
  return uiScene(page);
}
async function choosePoseKeys(page,times,{modifiers=false,touch=false}={}) {
  if(!modifiers)await page.getByRole('button',{name:'Select poses',exact:true}).click();
  for(const time of times){
    const label=`${modifiers&&time===times[0]?'Go to':'Select'} keyframe ${time.toFixed(2)} seconds`;
    const button=page.getByRole('button',{name:label,exact:true});
    if(touch)await button.tap();else await button.click(modifiers?{modifiers:['Shift']}:{});
  }
}
for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test.describe(`multi-key retiming ${viewport.name}`,()=>{
    test.use({viewport:{width:viewport.width,height:viewport.height},hasTouch:viewport.name==='phone'});
    test('selects poses, previews cancels applies undoes and saves a shared shift',async({page,request},testInfo)=>{
      const before=await retimeStudy(page,request);
      await choosePoseKeys(page,[3,6],{modifiers:viewport.name==='desktop',touch:viewport.name==='phone'});
      await expect(page.locator('#retime-status')).toContainText('2 poses selected');
      expect((await uiScene(page)).revision).toBe(before.revision);
      await page.getByLabel('Time shift (seconds)').fill('1.5');
      await page.getByRole('button',{name:'Preview shift',exact:true}).click();
      await expect(page.locator('#retime-status')).toContainText('2 poses preview +1.5s');
      await expect(page.getByRole('button',{name:'Select keyframe 4.50 seconds',exact:true})).toBeDisabled();
      await expect(page.getByRole('slider',{name:'Animation playhead',exact:true})).toBeDisabled();
      expect((await uiScene(page)).objects).toEqual(before.objects);expect((await serverScene(request)).revision).toBe(before.revision);
      await page.getByRole('button',{name:'Cancel shift',exact:true}).click();
      expect((await uiScene(page)).objects).toEqual(before.objects);
      await page.getByRole('button',{name:'Preview shift',exact:true}).click();await page.keyboard.press('Escape');
      await expect(page.getByRole('button',{name:'Apply shift',exact:true})).toBeHidden();
      await page.getByRole('button',{name:'Preview shift',exact:true}).click();
      const after=await edit(page,()=>page.getByRole('button',{name:'Apply shift',exact:true}).click());
      expect(after.revision).toBe(before.revision+1);expect(after.objects[0].keyframes.map(k=>k.time)).toEqual([0,4.5,7.5,9,12]);
      for(const time of [3,6])expect(after.objects[0].keyframes.find(k=>k.time===time+1.5)).toEqual({...before.objects[0].keyframes.find(k=>k.time===time),time:time+1.5});
      expect(after.objects[0].parameters).toEqual(before.objects[0].parameters);expect(after.objects.slice(1)).toEqual(before.objects.slice(1));
      await expect(page.locator('#retime-status')).toContainText('2 poses selected');
      const undone=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(undone.objects).toEqual(before.objects);
      const redone=await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());expect(redone.objects).toEqual(after.objects);
      const exported=JSON.parse(await download(page,testInfo,'json'));expect(exported.objects).toEqual(after.objects);expect(exported.schema_version).toBe(4);
      if(viewport.name==='phone'){expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);const box=await page.locator('[data-keyframe-time="4.5"]').boundingBox();expect(box.height).toBeGreaterThanOrEqual(44);}
      await settleCanvas(page);await screenshot(page,testInfo,`retimed-poses-${viewport.name}`);
      await page.locator('.retime-controls').screenshot({path:testInfo.outputPath(`retime-controls-${viewport.name}.png`)});
    });
  });
}
test('multi-key retiming rejects collisions ranges and zero shifts before committing',async({page,request},testInfo)=>{
  const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);
  await page.getByLabel('Time shift (seconds)').fill('3');await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('unselected pose');expect((await serverScene(request)).revision).toBe(before.revision);
  await page.getByRole('button',{name:'Select all poses',exact:true}).click();
  await page.getByLabel('Time shift (seconds)').fill('0.01');await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('0..12');
  await page.getByLabel('Time shift (seconds)').fill('-0.01');await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('0..12');
  await page.getByLabel('Time shift (seconds)').fill('0');await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('Zero shift');expect((await uiScene(page)).revision).toBe(before.revision);
  await page.getByRole('button',{name:'Clear poses',exact:true}).click();await expect(page.getByRole('button',{name:'Preview shift',exact:true})).toBeDisabled();
  const interior=await retimeStudy(page,request,{interior:true});await page.getByRole('button',{name:'Select all poses',exact:true}).click();
  await page.getByLabel('Time shift (seconds)').fill('1');await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  const endpoint=await edit(page,()=>page.getByRole('button',{name:'Apply shift',exact:true}).click());expect(endpoint.objects[0].keyframes.at(-1).time).toBe(12);expect(endpoint.objects[0].keyframes.length).toBe(interior.objects[0].keyframes.length);
  await edit(page,()=>page.getByRole('button',{name:`Select ${interior.objects[1].name}`,exact:true}).click());await expect(page.getByRole('button',{name:'Preview shift',exact:true})).toBeDisabled();
  await screenshot(page,testInfo,'retime-boundaries');
});
test('multi-key retiming captures playback time and pauses only when applied',async({page,request},testInfo)=>{
  const before=await retimeStudy(page,request,{playing:true});await choosePoseKeys(page,[3,6]);
  await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  const time=Number(await page.locator('#time-value').textContent());expect((await uiScene(page)).animation.playing).toBe(true);
  await page.getByRole('button',{name:'Cancel shift',exact:true}).click();expect((await uiScene(page)).animation.playing).toBe(true);
  await page.getByRole('button',{name:'Preview shift',exact:true}).click();const held=Number(await page.locator('#time-value').textContent());expect(held).toBeGreaterThanOrEqual(time);
  const after=await edit(page,()=>page.getByRole('button',{name:'Apply shift',exact:true}).click());expect(after.animation.playing).toBe(false);expect(after.animation.time).toBe(held);expect(after.revision).toBe(before.revision+1);
  const undo=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(undo.animation.playing).toBe(true);expect(undo.objects).toEqual(before.objects);
  await screenshot(page,testInfo,'retime-playing-preview');
});
test('stale multi-key preview cannot overwrite a real MCP retime and shares undo',async({page,request,expectedHttpFailures},testInfo)=>{
  const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview shift',exact:true}).click();
  const peer=await actualMcp(testInfo,'retime_keyframes',{targets:[{id:before.objects[1].id,times:[3,6]},{id:before.objects[2].id,times:[3]}],delta:1.5,expected_revision:before.revision,request_id:`retime-peer-${randomUUID()}`});expect(peer.ok).toBe(true);
  expectedHttpFailures.add('409 /api/command');await page.getByRole('button',{name:'Apply shift',exact:true}).click();
  await expect(page.locator('#toast')).toContainText('scene changed elsewhere');await expect.poll(async()=>(await uiScene(page)).revision).toBe(peer.scene.revision);
  expect((await uiScene(page)).objects).toEqual(peer.scene.objects);await expect(page.getByRole('button',{name:'Apply shift',exact:true})).toBeHidden();
  const undo=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(undo.objects).toEqual(before.objects);
  await screenshot(page,testInfo,'retime-client-conflict');
});

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]) {
  test.describe(`anchored scaling ${viewport.name}`,()=>{
    test.use({viewport:{width:viewport.width,height:viewport.height},hasTouch:viewport.name==='phone'});
    test('compresses selected poses with preview cancellation undo and JSON reopening',async({page,request},testInfo)=>{
      const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6],{modifiers:viewport.name==='desktop',touch:viewport.name==='phone'});
      await expect(page.locator('#scale-status')).toContainText('Anchor: 3s');
      await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();
      await expect(page.locator('#retime-status')).toContainText('0.5× around anchor 3s');
      await expect(page.locator('#timing-preview-list')).toContainText('6s → 4.5s');
      await expect(page.getByRole('combobox',{name:'Timing anchor',exact:true})).toBeDisabled();
      await expect(page.getByRole('button',{name:'Select keyframe 4.50 seconds',exact:true})).toBeDisabled();
      expect((await serverScene(request)).revision).toBe(before.revision);expect((await uiScene(page)).objects).toEqual(before.objects);
      await screenshot(page,testInfo,`timing-scale-preview-${viewport.name}`);
      await page.getByRole('button',{name:'Cancel timing scale',exact:true}).click();await expect(page.getByRole('button',{name:'Preview timing scale',exact:true})).toBeFocused();
      await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Preview timing scale',exact:true})).toBeFocused();
      await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();
      const after=await edit(page,()=>viewport.name==='phone'?page.getByRole('button',{name:'Apply timing scale',exact:true}).tap():page.getByRole('button',{name:'Apply timing scale',exact:true}).press('Enter'));
      expect(after.revision).toBe(before.revision+1);expect(after.objects[0].keyframes.map(k=>k.time)).toEqual([0,3,4.5,9,12]);
      expect(after.objects[0].keyframes.find(k=>k.time===4.5)).toEqual({...before.objects[0].keyframes.find(k=>k.time===6),time:4.5});expect(after.objects[0].parameters).toEqual(before.objects[0].parameters);expect(after.objects.slice(1)).toEqual(before.objects.slice(1));
      await expect(page.locator('#retime-status')).toContainText('2 poses selected');
      const undone=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(undone.objects).toEqual(before.objects);
      const redone=await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());expect(redone.objects).toEqual(after.objects);
      const saved=await download(page,testInfo,'json');expect(JSON.parse(saved).schema_version).toBe(4);
      await page.getByRole('button',{name:/^Recipe/}).click();const choosing=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Load JSON',exact:true}).click();const chooser=await choosing;
      const reopened=await edit(page,()=>chooser.setFiles({name:'scaled-rhythm.json',mimeType:'application/json',buffer:saved}));expect(reopened.objects).toEqual(after.objects);
      if(viewport.name==='phone'){expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);expect((await page.getByRole('combobox',{name:'Timing anchor',exact:true}).boundingBox()).height).toBeGreaterThanOrEqual(44);}
    });
    test('combined authoring scopes move align compress shift and shared undo coherently',async({page,request},testInfo)=>{
      const before=await retimeStudy(page,request);
      await edit(page,()=>page.getByRole('button',{name:'Select visible',exact:true}).click());await expect(page.locator('#retime-status')).toContainText('Select one island');
      await edit(page,()=>page.getByRole('button',{name:'Move selection right',exact:true}).click());
      await page.getByRole('button',{name:'Align horizontal',exact:true}).click();await page.getByRole('button',{name:'Cancel preview',exact:true}).click();
      await page.getByRole('button',{name:'Align horizontal',exact:true}).click();const arranged=await edit(page,()=>page.getByRole('button',{name:'Apply layout',exact:true}).click());
      await edit(page,()=>page.getByRole('button',{name:`Select ${before.objects[0].name}`,exact:true}).click());
      await page.getByRole('button',{name:'Edit motion path',exact:true}).click();await choosePoseKeys(page,[3,6],{touch:viewport.name==='phone'});
      await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const compressed=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());
      expect(compressed.objects[0].parameters).toEqual(arranged.objects[0].parameters);expect(compressed.objects.slice(1)).toEqual(arranged.objects.slice(1));
      await page.getByRole('button',{name:'Preview shift',exact:true}).click();const shifted=await edit(page,()=>page.getByRole('button',{name:'Apply shift',exact:true}).click());
      expect(shifted.objects[0].keyframes.map(k=>k.time)).toEqual([0,4.5,6,9,12]);
      expect((await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click())).objects).toEqual(compressed.objects);
      expect((await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click())).objects).toEqual(arranged.objects);
      await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());expect((await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click())).objects).toEqual(shifted.objects);
      await expect(page.locator('#retime-status')).toContainText('2 poses selected');
      if(viewport.name==='phone')expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);
      await settleCanvas(page);await screenshot(page,testInfo,`combined-authoring-${viewport.name}`);
    });
  });
}
test('anchored scaling offers all anchors and rejects collisions ranges and invalid input',async({page,request},testInfo)=>{
  const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);
  await page.getByLabel('Time scale factor',{exact:true}).fill('2');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#toast')).toContainText('unselected pose');
  expect((await serverScene(request)).revision).toBe(before.revision);
  await page.getByLabel('Time scale factor',{exact:true}).fill('1');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#toast')).toContainText('already match');
  await page.getByRole('combobox',{name:'Timing anchor',exact:true}).selectOption('last');await page.getByLabel('Time scale factor',{exact:true}).fill('0.5');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#timing-preview-list')).toContainText('3s → 4.5s');await page.getByRole('button',{name:'Cancel timing scale',exact:true}).click();
  await page.getByRole('combobox',{name:'Timing anchor',exact:true}).selectOption('playhead');await page.getByLabel('Time scale factor',{exact:true}).fill('2');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#timing-preview-list')).toContainText('6s → 8s');await page.keyboard.press('Escape');
  await page.getByRole('combobox',{name:'Timing anchor',exact:true}).selectOption('custom');await page.getByLabel('Anchor time (seconds)',{exact:true}).fill('0');await page.getByLabel('Time scale factor',{exact:true}).fill('0.5');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();
  const after=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());expect(after.objects[0].keyframes.map(k=>k.time)).toEqual([0,1.5,3,9,12]);
  await page.getByLabel('Anchor time (seconds)',{exact:true}).fill('12');await page.getByLabel('Time scale factor',{exact:true}).fill('2');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#toast')).toContainText('0..12');
  await page.getByLabel('Time scale factor',{exact:true}).fill('0');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();expect(await page.getByLabel('Time scale factor',{exact:true}).evaluate(input=>input.validity.valid)).toBe(false);expect((await uiScene(page)).revision).toBe(after.revision);
  await retimeStudy(page,request);await page.getByRole('button',{name:'Select all poses',exact:true}).click();await page.getByRole('combobox',{name:'Timing anchor',exact:true}).selectOption('custom');await page.getByLabel('Anchor time (seconds)',{exact:true}).fill('6');await page.getByLabel('Time scale factor',{exact:true}).fill('2');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#toast')).toContainText('0..12');
  await page.getByLabel('Time scale factor',{exact:true}).fill('0.5');await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const endpoints=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());expect(endpoints.objects[0].keyframes.map(k=>k.time)).toEqual([3,4.5,6,7.5,9]);await expect(page.locator('#seam-status')).toContainText('add 0s and 12s');await screenshot(page,testInfo,'scaling-anchor-boundaries');
});
test('anchored scaling freezes a visible-playhead anchor and pauses only on apply',async({page,request},testInfo)=>{
  const before=await retimeStudy(page,request,{playing:true});await choosePoseKeys(page,[3,6]);await page.getByRole('combobox',{name:'Timing anchor',exact:true}).selectOption('playhead');
  await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const held=Number(await page.locator('#time-value').textContent());await expect(page.locator('#scale-status')).toContainText(`Captured anchor: ${held}s`);expect((await uiScene(page)).animation.playing).toBe(true);
  await page.getByRole('button',{name:'Cancel timing scale',exact:true}).click();expect((await uiScene(page)).animation.playing).toBe(true);
  await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const anchor=Number(await page.locator('#time-value').textContent());const after=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());expect(after.animation.time).toBe(anchor);expect(after.animation.playing).toBe(false);expect(after.revision).toBe(before.revision+1);
  for(const time of [3,6]){const expected=anchor+(time-anchor)*.5;expect(after.objects[0].keyframes.find(k=>Math.abs(k.time-expected)<1e-9).parameters).toEqual(before.objects[0].keyframes.find(k=>k.time===time).parameters);}
  const undo=await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());expect(undo.objects).toEqual(before.objects);expect(undo.animation.playing).toBe(true);await screenshot(page,testInfo,'scaling-playhead-anchor');
});
test('stale anchored scaling cannot overwrite a real MCP scaling edit',async({page,request,expectedHttpFailures},testInfo)=>{
  const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();
  const peer=await actualMcp(testInfo,'scale_keyframes',{targets:[{id:before.objects[1].id,times:[3,6]},{id:before.objects[2].id,times:[3,6]}],anchor:3,factor:.5,expected_revision:before.revision,request_id:`scale-peer-${randomUUID()}`});expect(peer.ok).toBe(true);
  expectedHttpFailures.add('409 /api/command');await page.getByRole('button',{name:'Apply timing scale',exact:true}).click();await expect(page.locator('#toast')).toContainText('scene changed elsewhere');await expect.poll(async()=>(await uiScene(page)).revision).toBe(peer.scene.revision);expect((await uiScene(page)).objects).toEqual(peer.scene.objects);
  expect((await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click())).objects).toEqual(before.objects);await screenshot(page,testInfo,'scaling-client-conflict');
});

for(const viewport of [{name:'desktop',width:1440,height:1100},{name:'phone',width:390,height:844}]){
  test.describe(`authoring reliability ${viewport.name}`,()=>{
    test.use({viewport:{width:viewport.width,height:viewport.height},hasTouch:viewport.name==='phone'});
    test('pose selection survives geometry edits timing undo redo and clears on import',async({page,request},testInfo)=>{
      await retimeStudy(page,request);await choosePoseKeys(page,[3,6],{touch:viewport.name==='phone'});
      await edit(page,()=>page.getByRole('button',{name:'Move selection right',exact:true}).click());
      await expect(page.locator('#retime-status')).toContainText('2 poses selected');
      await expect(page.getByRole('button',{name:'Select keyframe 3.00 seconds',exact:true})).toHaveAttribute('aria-pressed','true');
      await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const scaled=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());
      await edit(page,()=>page.getByRole('button',{name:'Undo',exact:true}).click());await expect(page.getByRole('button',{name:'Select keyframe 6.00 seconds',exact:true})).toHaveAttribute('aria-pressed','true');
      await edit(page,()=>page.getByRole('button',{name:'Redo',exact:true}).click());await expect(page.getByRole('button',{name:'Select keyframe 4.50 seconds',exact:true})).toHaveAttribute('aria-pressed','true');
      const saved=await download(page,testInfo,'json');
      await page.getByRole('button',{name:/^Recipe/}).click();const choosing=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Load JSON',exact:true}).click();const chooser=await choosing;
      await edit(page,()=>chooser.setFiles({name:'reliability-import.json',mimeType:'application/json',buffer:saved}));
      expect((await uiScene(page)).objects).toEqual(scaled.objects);
      await edit(page,()=>page.getByRole('button',{name:`Select ${scaled.objects[0].name}`,exact:true}).click());await expect(page.getByRole('button',{name:'Preview timing scale',exact:true})).toBeDisabled();
      await screenshot(page,testInfo,`pose-continuity-${viewport.name}`);
    });
  });
}
test('phone authoring shortcuts keep a held preview while moving between canvas layers and timing',async({page,request},testInfo)=>{
  await page.setViewportSize({width:390,height:844});const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);
  await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();
  const navigation=page.getByRole('navigation',{name:'Authoring sections',exact:true});await expect(navigation).toBeVisible();
  await page.getByRole('button',{name:/^Recipe/}).click();await expect(page.locator('#canvas-stage')).toBeHidden();
  expect(JSON.parse(await page.locator('#recipe-code').textContent()).objects).toEqual(before.objects);
  for(const label of ['Canvas','Layers','Timing']){
    const link=navigation.getByRole('link',{name:label,exact:true});await link.click();expect((await link.boundingBox()).height).toBeGreaterThanOrEqual(44);
    if(label==='Canvas')await expect(page.locator('#canvas-stage')).toBeVisible();
    await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeVisible();expect((await serverScene(request)).revision).toBe(before.revision);
  }
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(391);await screenshot(page,testInfo,'phone-navigation-preview');
});
test('restart with the same document and revision rejects an old timing preview',async({page,expectedHttpFailures},testInfo)=>{
  test.setTimeout(60000);
  let owned=await startDisposableStudio(testInfo,{storage:testInfo.outputPath('restart-scene.json')}),staleMetadata=true;
  try{
    await page.goto(owned.origin);await expect(page.locator('#canvas-loading')).toBeHidden();
    await edit(page,()=>page.getByRole('button',{name:'Play demo',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Pause animation',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());
    await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const old=await uiScene(page);
    // Replay the actual captured GET response to hold a stale view during a real restart.
    // POSTs are unmodified and reach the new owned process.
    const handler=route=>staleMetadata?route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(old)}):route.continue();await page.route('**/api/scene',handler);
    await owned.stop();owned=await startDisposableStudio(testInfo,{storage:testInfo.outputPath('restart-scene.json')});
    const fresh=await disposableScene(owned.origin);expect(fresh.document_id).toBe(old.document_id);expect(fresh.revision).toBe(old.revision);expect(fresh.session_id).not.toBe(old.session_id);
    expectedHttpFailures.add('409 /api/command');
    const response=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/command'&&response.request().method()==='POST');await page.getByRole('button',{name:'Apply timing scale',exact:true}).click();const rejected=await response;
    expect(rejected.status()).toBe(409);expect((await rejected.json()).error.code).toBe('session_conflict');
    staleMetadata=false;await page.unroute('**/api/scene',handler);await expect.poll(async()=>(await uiScene(page)).session_id).toBe(fresh.session_id);
    expect((await disposableScene(owned.origin)).objects).toEqual(fresh.objects);expect((await disposableScene(owned.origin)).revision).toBe(fresh.revision);
    await expect(page.locator('#toast')).toContainText('session changed');await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeHidden();
    await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const recovered=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());expect(recovered.objects[0].keyframes.map(k=>k.time)).toEqual([0,3,4.5,9,12]);
    await screenshot(page,testInfo,'restart-recovery');
  }finally{expectedHttpFailures.add('net::ERR_CONNECTION_REFUSED /api/scene');await owned.stop();}
});

test('real loopback outage reconnects and clears a held preview when the session changes',async({page,expectedHttpFailures},testInfo)=>{
  test.setTimeout(60000);let owned=await startDisposableStudio(testInfo,{storage:testInfo.outputPath('outage-scene.json')});
  expectedHttpFailures.add('net::ERR_CONNECTION_REFUSED /api/scene');
  try{
    await page.goto(owned.origin);await expect(page.locator('#canvas-loading')).toBeHidden();
    await edit(page,()=>page.getByRole('button',{name:'Play demo',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Pause animation',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());
    await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();const before=await uiScene(page);
    await owned.stop();await expect(page.locator('#connection-notice')).toBeVisible();await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeDisabled();expect((await uiScene(page)).objects).toEqual(before.objects);
    owned=await startDisposableStudio(testInfo,{storage:testInfo.outputPath('outage-scene.json')});const fresh=await disposableScene(owned.origin);
    await expect.poll(async()=>(await uiScene(page)).session_id).toBe(fresh.session_id);await expect(page.locator('#connection-notice')).toBeHidden();await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeHidden();await expect(page.locator('#toast')).toContainText('session changed');
    expect((await uiScene(page)).objects).toEqual(before.objects);expect((await uiScene(page)).history.entries).toHaveLength(0);expect(fresh.revision).toBe(before.revision);
    await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());
    await screenshot(page,testInfo,'loopback-outage-recovered');
  }finally{await owned.stop();}
});
test('simulated browser offline retains a phone preview and resumes only after reconnection',async({page,request,expectedHttpFailures},testInfo)=>{
  await page.setViewportSize({width:390,height:844});const before=await retimeStudy(page,request);await choosePoseKeys(page,[3,6]);await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();let posts=0;
  page.on('request',request=>{if(request.method()==='POST'&&new URL(request.url()).pathname==='/api/command')posts++;});expectedHttpFailures.add('net::ERR_INTERNET_DISCONNECTED /api/scene');
  try{
    await page.context().setOffline(true);await expect(page.locator('#connection-notice')).toBeVisible();await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeDisabled();await expect(page.locator('#mobile-reconnect')).toBeVisible();
    await page.getByRole('navigation',{name:'Authoring sections',exact:true}).getByRole('link',{name:'Canvas',exact:true}).click();expect((await serverScene(request)).revision).toBe(before.revision);expect(posts).toBe(0);
    await page.context().setOffline(false);await expect(page.locator('#connection-notice')).toBeHidden();await expect(page.getByRole('button',{name:'Apply timing scale',exact:true})).toBeEnabled();expect(posts).toBe(0);
    await page.getByRole('navigation',{name:'Authoring sections',exact:true}).getByRole('link',{name:'Timing',exact:true}).click();await screenshot(page,testInfo,'phone-connected-preview');await page.screenshot({path:testInfo.outputPath('phone-authoring-preview-viewport.png'),fullPage:false});
    const after=await edit(page,()=>page.getByRole('button',{name:'Apply timing scale',exact:true}).click());expect(after.revision).toBe(before.revision+1);expect(posts).toBe(1);
  }finally{await page.context().setOffline(false);}
});
test('a timed out save releases editing without automatically replaying the request',async({page,request,expectedHttpFailures},testInfo)=>{
  await selectFirst(page);const before=await uiScene(page);let release,held=false;
  const gate=new Promise(resolve=>release=resolve);const handler=async route=>{held=true;await gate;try{await route.abort('failed');}catch(error){if(!/already handled/i.test(error.message))throw error;}};
  expectedHttpFailures.add('net::ERR_ABORTED /api/command');expectedHttpFailures.add('net::ERR_FAILED /api/command');await page.route('**/api/command',handler);
  try{
    await page.getByRole('slider',{name:'Island scale',exact:true}).press('ArrowRight');await expect.poll(()=>held).toBe(true);await expect(page.locator('#save-status')).toHaveText('Applying change…');
    await expect(page.locator('#toast')).toContainText('Save confirmation timed out',{timeout:16000});await expect(page.getByRole('slider',{name:'Island scale',exact:true})).toBeEnabled();expect((await serverScene(request)).revision).toBe(before.revision);
  }finally{release();await page.unroute('**/api/command',handler);}
  const recovered=await edit(page,()=>page.getByRole('slider',{name:'Island scale',exact:true}).press('ArrowRight'));expect(recovered.revision).toBe(before.revision+1);await screenshot(page,testInfo,'timed-save-recovered');
});
test('a lost save reply refreshes the committed scene once and does not duplicate the edit',async({page,request,expectedHttpFailures},testInfo)=>{
  await selectFirst(page);const before=await uiScene(page);let forwarded=0;
  const handler=async route=>{forwarded++;const response=await route.fetch();expect(response.ok()).toBe(true);await route.abort('failed');};expectedHttpFailures.add('net::ERR_FAILED /api/command');await page.route('**/api/command',handler);
  try{
    await page.getByRole('slider',{name:'Island scale',exact:true}).press('ArrowRight');await expect(page.locator('#toast')).toContainText('scene was refreshed');await expect.poll(async()=>(await uiScene(page)).revision).toBe(before.revision+1);
    expect((await serverScene(request)).objects[0].parameters.radius).toBe(before.objects[0].parameters.radius+1);expect(forwarded).toBe(1);await expect(page.locator('#connection-notice')).toBeHidden();await expect(page.getByRole('slider',{name:'Island scale',exact:true})).toBeEnabled();
    await page.waitForTimeout(1500);expect(forwarded).toBe(1);expect((await serverScene(request)).revision).toBe(before.revision+1);
  }finally{await page.unroute('**/api/command',handler);}
  await screenshot(page,testInfo,'lost-reply-confirmed-scene');
});
test('native pose chip focus survives saves and respects an intervening focus choice',async({page},testInfo)=>{
  await edit(page,()=>page.getByRole('button',{name:'Play demo',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Pause animation',exact:true}).click());await edit(page,()=>page.getByRole('button',{name:'Select Solstice',exact:true}).click());
  await edit(page,()=>page.getByRole('button',{name:'Go to keyframe 6.00 seconds',exact:true}).press('Enter'));await expect(page.getByRole('button',{name:'Go to keyframe 6.00 seconds',exact:true})).toBeFocused();
  let release,held=false;const gate=new Promise(resolve=>release=resolve);const handler=async route=>{held=true;await gate;await route.continue();};await page.route('**/api/command',handler);
  try{await page.getByRole('button',{name:'Go to keyframe 3.00 seconds',exact:true}).press('Enter');await expect.poll(()=>held).toBe(true);await page.getByRole('button',{name:'Client setup',exact:true}).focus();}finally{release();}
  await expect(page.locator('#save-status')).toHaveText('Scene synchronized');await expect(page.getByRole('button',{name:'Client setup',exact:true})).toBeFocused();await page.unroute('**/api/command',handler);await screenshot(page,testInfo,'pose-keyboard-continuity');
});
