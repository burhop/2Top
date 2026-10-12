/** Reproducible real-browser profile; owns only its disposable loopback process. */
import { chromium } from '@playwright/test';
import { spawn, execFileSync } from 'node:child_process';
import { readFile, writeFile, mkdir, open } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = path.resolve(process.argv[2] || 'benchmark-results/studio');
const port = Number(process.env.STUDIO_BENCHMARK_PORT || 8766);
if (!Number.isInteger(port) || port < 1024 || port > 65535 || port === 8000) throw Error('Use a separate test port');
const origin = `http://127.0.0.1:${port}`;
await mkdir(output, { recursive: true });
try { await fetch(`${origin}/api/health`, {signal:AbortSignal.timeout(1000)}); throw Error('Benchmark port already occupied; will not reuse it'); }
catch (error) { if (error.message.includes('already occupied')) throw error; }
const log = await open(path.join(output, 'server.log'), 'w');
const server = spawn(process.env.STUDIO_PYTHON || 'python', ['-m', 'studio.app', '--ephemeral', '--port', String(port)], {
  cwd: process.env.STUDIO_BENCHMARK_CWD || root, stdio: ['ignore', log.fd, log.fd], windowsHide: true,
});
let browser;
const summary = { source: 'actual Chromium; instrumented requestAnimationFrame callbacks and real Canvas drawImage',
  platform: os.platform(), release: os.release(), cpu: os.cpus()[0]?.model, logicalCpus: os.cpus().length,
  viewport: { width: 1440, height: 1100 }, dpr: 1, port, modelInference: false, scenarios: [] };
const quantile = (values, q) => values.length ? [...values].sort((a,b)=>a-b)[Math.min(values.length-1, Math.floor(values.length*q))] : null;
const stats = frames => ({ renders: frames.length, medianMs: quantile(frames.map(f=>f.ms),.5), p95Ms: quantile(frames.map(f=>f.ms),.95), maxMs: frames.length ? Math.max(...frames.map(f=>f.ms)) : null });
try {
  for (let i=0;i<120;i++) {
    if (server.exitCode !== null) throw Error(`Owned studio exited: ${server.exitCode}`);
    try { const r=await fetch(`${origin}/api/health`); if(r.ok){summary.health=await r.json();break;} } catch {}
    await new Promise(resolve=>setTimeout(resolve,250));
  }
  if (!summary.health) throw Error('Owned studio failed to start');
  browser = await chromium.launch(); summary.browser = browser.version();
  const readRecipe = async name => JSON.parse(await readFile(path.join(root,'examples',name),'utf8'));
  const motion=await readRecipe('tidal_atlas_choreography.json');
  const layered=await readRecipe('tidal_atlas_recipe.json');
  layered.objects=Array.from({length:8},(_,i)=>{const o=structuredClone(layered.objects[i%3]);o.id=`bench_layer_${i}`;o.name=`Layer ${i+1}`;o.parameters.x=240+(i%4)*160;o.parameters.y=270+Math.floor(i/4)*190;o.parameters.radius=140;o.style.opacity=.7;return o;});
  const blend=await readRecipe('tidal_atlas_confluence.json');
  const second=structuredClone(blend.objects); second.forEach((o,i)=>{o.id=`bench_source_${i}`;o.parameters.y+=150;o.parameters.x+=100;});
  const extra=structuredClone(blend.blends[0]); extra.id='bench_blend_2';extra.name='Second confluence';extra.source_a=second[0].id;extra.source_b=second[1].id;
  blend.objects.push(...second);blend.blends.push(extra);
  for (const [name,recipe] of [['authored-motion',motion],['eight-layered-islands',layered],['two-static-blends',blend]]) {
    if(process.env.STUDIO_BENCHMARK_SCENARIO && process.env.STUDIO_BENCHMARK_SCENARIO !== name)continue;
    recipe.schema_version=4;recipe.blends ||= [];recipe.objects.forEach(o=>o.keyframes ||= []);
    recipe.layer_order=[...recipe.objects,...recipe.blends].map(o=>o.id);recipe.view.contours=48;recipe.animation.playing=false;
    const current=await (await fetch(`${origin}/api/scene`)).json();
    const reset=await fetch(`${origin}/api/command`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({op:'load_recipe',recipe,expected_revision:current.revision})});
    if(!reset.ok)throw Error(`${name} fixture: ${await reset.text()}`);
    const loaded=await reset.json();
    const select=await fetch(`${origin}/api/command`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({op:'select',ids:[recipe.objects[0].id],expected_revision:loaded.scene.revision})});
    if(!select.ok)throw Error('Benchmark selection failed');
    await writeFile(path.join(output,`${name}-recipe.json`),JSON.stringify(recipe,null,2));
    const context=await browser.newContext({viewport:summary.viewport,deviceScaleFactor:1});
    await context.addInitScript(()=>{
      window.__profile={frames:[],draws:0,errors:[],firstArtwork:null};
      const draw=CanvasRenderingContext2D.prototype.drawImage;
      CanvasRenderingContext2D.prototype.drawImage=function(...args){if(this.canvas.id==='art-canvas')window.__profile.draws++;return draw.apply(this,args);};
      const raf=window.requestAnimationFrame.bind(window);
      window.requestAnimationFrame=callback=>raf(now=>{const before=window.__profile.draws,start=performance.now();callback(now);if(window.__profile.draws>before){const frame={start,ms:performance.now()-start,draws:window.__profile.draws-before};window.__profile.frames.push(frame);window.__profile.firstArtwork ||= frame;}});
      window.addEventListener('error',event=>window.__profile.errors.push(event.message));
    });
    const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push({message:e.message,stack:e.stack}));
    const cdp=await context.newCDPSession(page);await cdp.send('Profiler.enable');await cdp.send('Profiler.start');
    await page.goto(origin);await page.waitForFunction(()=>window.__profile.firstArtwork && window.tidalStudio?.getScene());
    const initial=await page.evaluate(()=>({frame:window.__profile.firstArtwork,navigationToArtworkMs:window.__profile.firstArtwork.start,nativeWebMCP:Boolean(document.modelContext),state:window.tidalStudio.getScene()}));
    const row={name,islands:recipe.objects.length,blends:recipe.blends.length,contours:48,initial:{renderMs:initial.frame.ms,navigationToArtworkMs:initial.navigationToArtworkMs+initial.frame.ms},nativeWebMCP:initial.nativeWebMCP};
    await page.locator('#timeline-input').focus();await page.keyboard.press('ArrowRight');
    await page.waitForFunction(()=>document.querySelector('#save-status').textContent==='Scene synchronized');
    row.keyboardFocusAfterCommit=await page.evaluate(()=>document.activeElement.id || document.activeElement.tagName);
    await page.evaluate(()=>{window.__profile.frames=[];});
    const timeline=await page.locator('#timeline-input').boundingBox();
    await page.mouse.move(timeline.x+timeline.width*.05,timeline.y+timeline.height/2);await page.mouse.down();
    const scrubLatency=[];
    for(let i=0;i<30;i++) {
      const start=await page.evaluate(()=>performance.now());const count=await page.evaluate(()=>window.__profile.frames.length);
      await page.mouse.move(timeline.x+timeline.width*(.08+i*.025),timeline.y+timeline.height/2);await page.waitForFunction(n=>window.__profile.frames.length>n,count,{timeout:10000});
      scrubLatency.push(await page.evaluate(t=>performance.now()-t,start));
    }
    row.scrubbing={...stats(await page.evaluate(()=>window.__profile.frames)),eventToObservedPaintMedianMs:quantile(scrubLatency,.5),eventToObservedPaintP95Ms:quantile(scrubLatency,.95)};
    await page.mouse.up();await page.waitForFunction(()=>document.querySelector('#save-status').textContent==='Scene synchronized');
    // Native pointer movement on the explicitly selected source center; Escape cancels temporary edits.
    const state=await page.evaluate(()=>window.tidalStudio.getScene());const o=state.objects.find(o=>o.id===state.selection[0])||state.objects[0];
    const pose=await page.evaluate(id=>window.tidalStudio.getPose(id),o.id);
    const box=await page.locator('#art-canvas').boundingBox();const scale=Math.min(box.width/1000,box.height/700)*.97*state.view.zoom;
    const x=box.x+box.width/2+(pose.x-500+state.view.pan_x)*scale,y=box.y+box.height/2+(pose.y-350+state.view.pan_y)*scale;
    await page.keyboard.press('Escape');await page.mouse.move(x,y);await page.mouse.down();
    await page.evaluate(()=>{window.__profile.frames=[];});
    for(let i=1;i<=24;i++){await page.mouse.move(x+i*2,y+i);await page.evaluate(()=>new Promise(requestAnimationFrame));}
    row.dragging=stats(await page.evaluate(()=>window.__profile.frames));await page.keyboard.press('Escape');await page.mouse.up();
    await page.locator('#play-button').click();await page.waitForFunction(()=>window.tidalStudio.getScene().animation.playing);
    await page.evaluate(()=>{window.__profile.frames=[];});await page.waitForTimeout(2000);
    row.playback=stats(await page.evaluate(()=>window.__profile.frames));row.errors=errors;
    const profile=(await cdp.send('Profiler.stop')).profile;await writeFile(path.join(output,`${name}.cpuprofile`),JSON.stringify(profile));
    await page.locator('#play-button').click();
    await page.waitForFunction(()=>!window.tidalStudio.getScene().animation.playing && document.querySelector('#save-status').textContent==='Scene synchronized');
    await page.waitForFunction(()=>{const c=document.querySelector('#art-canvas');return c.width>0 && c.getContext('2d').getImageData(5,5,1,1).data[0]>0;});
    const artwork=await page.locator('#art-canvas').evaluate(c=>c.toDataURL('image/png').split(',')[1]);
    await writeFile(path.join(output,`${name}-canvas.png`),Buffer.from(artwork,'base64'));
    await page.screenshot({path:path.join(output,`${name}.png`),fullPage:true});
    summary.scenarios.push(row);console.log(JSON.stringify(row));await context.close();
  }
  await writeFile(path.join(output,'measurements.json'),JSON.stringify(summary,null,2));
} finally {
  if(browser)await browser.close();
  if(server.exitCode===null) {
    if(process.platform==='win32')execFileSync('taskkill',['/PID',String(server.pid),'/T','/F'],{windowsHide:true,stdio:'pipe'});
    else server.kill();
  }
  await log.close();
}
