/** Real Chromium integration tests. API calls only reset/read the disposable scene;
 * edits under test use browser UI, native pointer/keyboard/file/download behavior.
 * No mocked canvas, modelContext, tool registrations, or AI/model host is injected.
 */
import { test as base, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';

const seed = JSON.parse(await readFile(new URL('../../examples/tidal_atlas_recipe.json', import.meta.url), 'utf8'));
const first = seed.objects[0];

const test = base.extend({
  page: async ({ page, request }, use, testInfo) => {
    const errors = [];
    page.on('pageerror', (error) => errors.push({ kind: 'pageerror', message: error.message }));
    page.on('console', (message) => {
      if (message.type() !== 'error') return;
      // Chromium may ask for an optional favicon that this app does not provide.
      const url = message.location().url;
      if (url && new URL(url).pathname === '/favicon.ico' && /404/.test(message.text())) return;
      errors.push({ kind: 'console', message: message.text(), url });
    });
    page.on('response', (response) => {
      if (response.status() >= 400 && new URL(response.url()).pathname !== '/favicon.ico') {
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
  const pending = page.waitForEvent('download');
  await page.locator(`[data-export="${type}"]`).click();
  const item = await pending;
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
    expect(capability.status.registered).toBe(12);
    await expect(page.locator('#agent-hint')).toContainText('12 browser tools registered');
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
    await expect(page.getByRole('dialog')).toContainText('Not supported in this browser');
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
  const json = JSON.parse((await download(page, testInfo, 'json')).toString());
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
  await screenshot(page, testInfo, 'imported-studio');
});

test('invalid file import preserves the scene and valid imports still work afterward', async ({ page, request }) => {
  await page.getByRole('button', { name: /^Recipe/ }).click();
  const before = await serverScene(request);
  await page.locator('#recipe-file').setInputFiles({ name: 'broken.json', mimeType: 'application/json', buffer: Buffer.from('{broken') });
  await expect(page.getByRole('status')).toHaveText('That file is not valid JSON. Your scene was not changed.');
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
    await page.setViewportSize(viewport);
    await settleCanvas(page);
    const dimensions = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: innerWidth }));
    expect(dimensions.width, `${viewport.width}px layout must not overflow horizontally`).toBeLessThanOrEqual(dimensions.viewport + 1);
    await expect(page.locator('#art-canvas')).toBeVisible();
    await expect(page.getByRole('button', { name: /^Export/ })).toBeVisible();
    await screenshot(page, testInfo, `responsive-${viewport.width}`);
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
