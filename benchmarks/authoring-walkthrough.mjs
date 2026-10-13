/** Evidence-producing human workflow. Owns a disposable loopback service; never port 8000. */
import {chromium,expect} from '@playwright/test';
import {mkdir,writeFile,appendFile,copyFile} from 'node:fs/promises';
import {createWriteStream} from 'node:fs';
import {spawn,execFileSync} from 'node:child_process';
import {resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';

const repository=resolve(fileURLToPath(new URL('..',import.meta.url)));
const timestamp=new Date().toISOString().replaceAll(':','-').replaceAll('.','-');
const root=resolve(process.argv[2]||join(repository,'..','artifacts','ui-walkthrough','combined-authoring-0.11.0',timestamp));
const origin='http://127.0.0.1:8769';
const python=process.env.STUDIO_PYTHON;if(!python)throw new Error('Set STUDIO_PYTHON to the project interpreter.');
for(const directory of ['playwright','screenshots/raw','screenshots/annotated','trace'])await mkdir(join(root,directory),{recursive:true});
await copyFile(fileURLToPath(import.meta.url),join(root,'playwright','authoring-walkthrough.mjs'));
await writeFile(join(root,'progress.md'),`# Combined authoring review — 0.11.0\n\nStarted ${new Date().toISOString()} (UTC). Work17 artist; disposable port 8769.\nNo browser action has run. The live port 8000 demo is excluded.\n`);
const diagnostics=[];let browser,context,page,server;
const scene=()=>page.evaluate(()=>window.tidalStudio.getScene());
const same=(a,b)=>expect(a).toEqual(b);
let arranged,compressed,shifted,selectionRevision;
const buttons=['#select-visible-button','[data-group-nudge="1,0"]','[data-layout-mode="align_y"]','#layout-apply','#layout-cancel','.layer-row.selected','#select-poses-button','[data-keyframe-time="3"]','[data-keyframe-time="6"]','#scale-anchor-mode','#time-scale-factor','#preview-time-scale','#retime-shift','#preview-retime','#apply-retime','#cancel-retime','#undo-button','#redo-button'];
const plans=[
  ['Open studio','Open the current disposable studio.', 'The canvas loads and the scene service connects.', async()=>{await page.goto(origin);await expect(page.locator('#canvas-loading')).toBeHidden();await expect(page.locator('#connection-label')).toHaveText('Scene service connected');},null],
  ['Play demo','Click Play demo.', 'Orbit & bloom loads with authored poses and playback.',async()=>page.getByRole('button',{name:'Play demo',exact:true}).click(),'#demo-button'],
  ['Pause animation','Click Pause animation.', 'Playback pauses without changing authored poses.',async()=>page.getByRole('button',{name:'Pause animation',exact:true}).click(),'#play-button'],
  ['Select visible','Click Select visible.', 'All three islands are selected; timing asks for one island.',async()=>{await page.getByRole('button',{name:'Select visible',exact:true}).click();await expect(page.locator('#retime-status')).toContainText('Select one island');},'#select-visible-button'],
  ['Move selection','Click Move selection right.', 'All selected complete paths move right together.',async()=>page.getByRole('button',{name:'Move selection right',exact:true}).click(),'[data-group-nudge="1,0"]'],
  ['Preview alignment','Click Align horizontal.', 'The horizontal center layout is previewed without a commit.',async()=>{await page.getByRole('button',{name:'Align horizontal',exact:true}).click();await expect(page.locator('#layout-status')).toContainText('preview');},'[data-layout-mode="align_y"]'],
  ['Apply alignment','Click Apply layout.', 'One reversible layout translates all complete paths.',async()=>{await page.getByRole('button',{name:'Apply layout',exact:true}).click();},'#layout-apply'],
  ['Choose island','Click Select Solstice.', 'One island is selected and its five pose chips are available.',async()=>{await page.getByRole('button',{name:'Select Solstice',exact:true}).click();await expect(page.locator('[data-keyframe-time]')).toHaveCount(5);arranged=(await scene()).objects;},'.layer-row'],
  ['Choose playhead','Click Go to keyframe 6.00 seconds.', 'The visible playhead pauses at 6 seconds.',async()=>{await page.getByRole('button',{name:'Go to keyframe 6.00 seconds',exact:true}).click();await expect(page.locator('#time-value')).toHaveText('06.00');},'[data-keyframe-time="6"]'],
  ['Select poses','Click Select poses.', 'Pose chips switch to local selection mode.',async()=>{selectionRevision=(await scene()).revision;await page.getByRole('button',{name:'Select poses',exact:true}).click();},'#select-poses-button'],
  ['Choose first pose','Click Select keyframe 3.00 seconds.', 'The 3-second pose is selected without a scene transaction.',async()=>{await page.getByRole('button',{name:'Select keyframe 3.00 seconds',exact:true}).click();expect((await scene()).revision).toBe(selectionRevision);},'[data-keyframe-time="3"]'],
  ['Choose second pose','Click Select keyframe 6.00 seconds.', 'Two poses are selected; the first-pose anchor resolves to 3 seconds.',async()=>{await page.getByRole('button',{name:'Select keyframe 6.00 seconds',exact:true}).click();await expect(page.locator('#scale-status')).toContainText('Anchor: 3s');},'[data-keyframe-time="6"]'],
  ['Set compression','Enter 0.5 in Time scale factor; keep Timing anchor set to First selected pose.', 'The factor is valid and no shared state changes.',async()=>{await page.getByLabel('Time scale factor',{exact:true}).fill('0.5');await expect(page.getByRole('combobox',{name:'Timing anchor',exact:true})).toHaveValue('first');},'#time-scale-factor'],
  ['Preview compression','Click Preview timing scale.', 'Preview lists 3s → 3s and 6s → 4.5s; shared artwork is unchanged.',async()=>{await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#timing-preview-list')).toContainText('6s → 4.5s');same((await scene()).objects,arranged);},'#preview-time-scale'],
  ['Cancel compression','Click Cancel timing scale.', 'The original timing returns and focus returns to Preview timing scale.',async()=>{await page.getByRole('button',{name:'Cancel timing scale',exact:true}).click();await expect(page.getByRole('button',{name:'Preview timing scale',exact:true})).toBeFocused();same((await scene()).objects,arranged);},'#cancel-retime'],
  ['Preview again','Click Preview timing scale again.', 'The same captured scaling is previewed.',async()=>{await page.getByRole('button',{name:'Preview timing scale',exact:true}).click();await expect(page.locator('#retime-status')).toContainText('0.5× around anchor 3s');},'#preview-time-scale'],
  ['Apply compression','Click Apply timing scale.', 'The 6-second pose becomes 4.5 seconds in one reversible edit.',async()=>{await page.getByRole('button',{name:'Apply timing scale',exact:true}).click();await expect.poll(async()=>(await scene()).objects[0].keyframes.map(k=>k.time)).toEqual([0,3,4.5,9,12]);compressed=(await scene()).objects;same(compressed[0].parameters,arranged[0].parameters);same(compressed.slice(1),arranged.slice(1));},'#apply-retime'],
  ['Preview shift','Click Preview shift with Time shift (seconds) set to 1.5.', 'The retained two-pose selection previews 3s → 4.5s and 4.5s → 6s.',async()=>{await page.getByRole('button',{name:'Preview shift',exact:true}).click();await expect(page.locator('#timing-preview-list')).toContainText('4.5s → 6s');},'#preview-retime'],
  ['Apply shift','Click Apply shift.', 'Only selected key times move; geometry and other tracks remain.',async()=>{await page.getByRole('button',{name:'Apply shift',exact:true}).click();await expect.poll(async()=>(await scene()).objects[0].keyframes.map(k=>k.time)).toEqual([0,4.5,6,9,12]);shifted=(await scene()).objects;same(shifted[0].parameters,arranged[0].parameters);},'#apply-retime'],
  ['Undo shift','Click Undo.', 'The compressed phrase returns in one undo.',async()=>{await page.getByRole('button',{name:'Undo',exact:true}).click();await expect.poll(async()=>(await scene()).objects).toEqual(compressed);},'#undo-button'],
  ['Undo compression','Click Undo again.', 'The arranged original five-key track returns.',async()=>{await page.getByRole('button',{name:'Undo',exact:true}).click();await expect.poll(async()=>(await scene()).objects).toEqual(arranged);},'#undo-button'],
  ['Redo compression','Click Redo.', 'The compressed phrase is restored.',async()=>{await page.getByRole('button',{name:'Redo',exact:true}).click();await expect.poll(async()=>(await scene()).objects).toEqual(compressed);},'#redo-button'],
  ['Redo shift','Click Redo again.', 'The shifted compressed phrase returns; key selection resets on track changes.',async()=>{await page.getByRole('button',{name:'Redo',exact:true}).click();await expect.poll(async()=>(await scene()).objects).toEqual(shifted);await expect(page.locator('#retime-status')).toContainText('Select poses');},'#redo-button'],
  ['Open export','Click Export.', 'JSON export is available.',async()=>{await page.getByRole('button',{name:/^Export/}).click();await expect(page.locator('[data-export="json"]')).toBeVisible();},'#export-button'],
  ['Save JSON','Click Scene recipe (JSON).', 'A schema-4 recipe downloads with the final artwork and tracks.',async()=>{const pending=page.waitForEvent('download');await page.locator('[data-export="json"]').click();const download=await pending;const file=join(root,'trace','authored-rhythm.json');await download.saveAs(file);const {readFile}=await import('node:fs/promises');const recipe=JSON.parse(await readFile(file,'utf8'));expect(recipe.schema_version).toBe(4);same(recipe.objects,shifted);},'[data-export="json"]'],
];
const status={title:'Combined authoring review — 0.11.0',summary:'Move and align complete paths, compress a phrase, shift it, undo/redo and save it.',overall:'pending',updated:new Date().toISOString(),manualSteps:plans.map(p=>({label:p[0],instruction:p[1]})),steps:plans.map((p,i)=>({id:String(i+1),state:'pending',label:p[0],summary:'Not reached.',purpose:p[2],action:p[1],controls:[],expected:p[2],actual:'Not reached.'}))};
const escape=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
async function report(){
  status.updated=new Date().toISOString();await writeFile(join(root,'status.json'),JSON.stringify(status,null,2));
  await writeFile(join(root,'report.html'),`<!doctype html><meta charset="utf-8"><title>${escape(status.title)}</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:16px;background:#f5f5f0;color:#17372f}.pass{border-left:8px solid #15803d}.blocked{border-left:8px solid #be123c}.pending{border-left:8px solid #64748b}article{background:white;padding:16px;margin:12px 0}.image-button{border:0;background:none;cursor:zoom-in}.image-button img{width:300px;max-width:100%}dialog img{max-width:95vw;max-height:85vh}dialog::backdrop{background:#000b}button{padding:10px}small{color:#53645b}</style><h1>${escape(status.title)}</h1><p>${escape(status.summary)} Overall: <strong>${status.overall}</strong>.</p><p>Disposable URL: ${origin}. Live port 8000 excluded. Updated ${status.updated} UTC.</p><h2>Manual repeat checklist</h2><ol>${status.manualSteps.map(s=>`<li>${escape(s.instruction)}</li>`).join('')}</ol>${status.steps.map(s=>`<article class="${s.state}"><h2>${s.id}. ${escape(s.label)} — ${s.state}</h2><p>${escape(s.summary)}</p><p>Expected: ${escape(s.expected)}<br>Actual: ${escape(s.actual)}</p>${s.raw?`<button class="image-button" data-image="${s.raw}"><img src="${s.raw}" alt="Raw screen ${s.id}"></button><button class="image-button" data-image="${s.annotated}"><img src="${s.annotated}" alt="Annotated controls ${s.id}"></button>`:''}${s.result?`<p><a href="${s.result}" target="_blank">Resulting screen</a></p>`:''}<small>${escape(s.controls.join(' · '))}</small></article>`).join('')}<dialog id="image-viewer"><button id="close-image">Close</button><p><img id="full-image"></p></dialog><script>const dialog=document.querySelector('#image-viewer');document.addEventListener('click',e=>{const b=e.target.closest('.image-button');if(b){document.querySelector('#full-image').src=b.dataset.image;dialog.showModal()}});document.querySelector('#close-image').onclick=()=>dialog.close();</script>`);
}
async function capture(index,suffix='before',primary){
  const stem=String(index+1).padStart(2,'0')+'-'+suffix;
  const raw=`screenshots/raw/${stem}.png`,annotated=`screenshots/annotated/${stem}.png`;
  await page.screenshot({path:join(root,raw),fullPage:true});
  const controls=await page.evaluate(selectors=>{
    const items=[];const seen=new Set();
    for(const selector of selectors)for(const element of document.querySelectorAll(selector)){
      const box=element.getBoundingClientRect();if(box.width&&box.height&&!seen.has(element)){seen.add(element);items.push({label:element.getAttribute('aria-label')||element.labels?.[0]?.textContent||element.textContent.trim()||selector,x:box.x+scrollX,y:box.y+scrollY});}
    }
    items.sort((a,b)=>a.y-b.y||a.x-b.x);
    const root=document.createElement('div');root.id='walkthrough-overlays';root.style='position:absolute;inset:0;pointer-events:none;z-index:2147483647';
    items.forEach((item,i)=>{const marker=document.createElement('span');marker.textContent=String(i+1);marker.style=`position:absolute;left:${item.x}px;top:${item.y}px;background:#b91c1c;color:white;padding:3px 7px;border-radius:4px;font:bold 13px system-ui`;root.append(marker);});
    const legend=document.createElement('div');legend.style='position:absolute;left:24px;top:64px;max-width:410px;background:#fffffff2;color:#172f28;padding:14px;border:2px solid #b91c1c;font:12px system-ui';legend.textContent=items.map((item,i)=>`${i+1}. ${item.label}`).join('\n');legend.style.whiteSpace='pre-line';root.append(legend);document.body.append(root);
    return items.map((item,i)=>`${i+1}. ${item.label}`);
  },[...(primary?[primary]:[]),...buttons]);
  await page.screenshot({path:join(root,annotated),fullPage:true});await page.locator('#walkthrough-overlays').evaluate(element=>element.remove());
  return {raw,annotated,controls};
}
await report();console.log(`ARTIFACT_ROOT ${root}`);
try{
  try{await fetch(origin+'/api/health',{signal:AbortSignal.timeout(1000)});throw new Error('Review port is occupied; refusing to reuse it.');}catch(error){if(error.name!=='TypeError')throw error;}
  const log=createWriteStream(join(root,'trace','server.log'));
  server=spawn(python,['-m','studio.app','--ephemeral','--port','8769'],{cwd:repository,windowsHide:true});server.stdout.pipe(log);server.stderr.pipe(log);
  let health;
  for(let i=0;i<80;i++){try{const response=await fetch(origin+'/api/health');if(response.ok){health=await response.json();break;}}catch{}await new Promise(r=>setTimeout(r,150));}
  if(health?.version!=='0.11.0')throw new Error('The isolated 0.11.0 service did not become available.');
  const branch=execFileSync('git',['branch','--show-current'],{cwd:repository,encoding:'utf8'}).trim();
  if(!['feat/anchored-time-scale-0.11.0','dev'].includes(branch))throw new Error('Unexpected review branch');
  await appendFile(join(root,'progress.md'),`\nEnvironment confirmed: ${branch}, application ${health.version}, newly owned ephemeral PID ${server.pid}, ${origin}.\n`);
  browser=await chromium.launch({headless:true});context=await browser.newContext({viewport:{width:1440,height:1100},acceptDownloads:true});await context.tracing.start({screenshots:true,snapshots:true,sources:true});page=await context.newPage();
  page.on('console',message=>{if(message.type()==='error'&&!/favicon/.test(message.location().url||''))diagnostics.push({kind:'console',message:message.text()});});page.on('pageerror',error=>diagnostics.push({kind:'pageerror',message:error.message}));page.on('response',response=>{if(response.status()>=400&&!response.url().endsWith('/favicon.ico'))diagnostics.push({kind:'http',status:response.status(),url:response.url()});});
  for(let i=0;i<plans.length;i++){
    const [label,action,expected,execute,primary]=plans[i],step=status.steps[i];
    try{
      const evidence=await capture(i,'before',primary);Object.assign(step,evidence);await report();
      const beforeRevision=i===0?null:(await scene()).revision;
      await execute();
      if([1,2,3,4,6,7,8].includes(i))await expect.poll(async()=>(await scene()).revision).toBeGreaterThan(beforeRevision);
      if(diagnostics.length)throw new Error(JSON.stringify(diagnostics));
      step.result=`screenshots/raw/${String(i+1).padStart(2,'0')}-result.png`;await page.screenshot({path:join(root,step.result),fullPage:true});
      step.state='pass';step.summary='Verified through the normal interface.';step.actual=expected;
      await appendFile(join(root,'progress.md'),`\n## ${i+1}. ${label} — PASS\n${new Date().toISOString()} UTC · ${page.url()}\nAction: ${action}\nControls: ${step.controls.join('; ')}\nExpected: ${expected}\nActual: ${step.actual}\nDiagnostics: ${JSON.stringify(diagnostics)}\nImages: ${step.raw}; ${step.annotated}; ${step.result}\n`);await report();console.log(`PASS ${i+1}/${plans.length} ${label}`);
    }catch(error){
      const evidence=await capture(i,'stopped',primary);Object.assign(step,evidence);step.state='blocked';step.summary=`Stopped at ${label}.`;step.actual=error.message;status.overall='blocked';status.summary=`Stopped at ${label}; later work remains unreached.`;
      await appendFile(join(root,'progress.md'),`\n## ${i+1}. ${label} — STOPPED\n${new Date().toISOString()} UTC · ${page.url()}\nControl/action: ${action}\nExpected: ${expected}\nActual: ${error.stack}\nDiagnostics: ${JSON.stringify(diagnostics)}\nImages: ${step.raw}; ${step.annotated}\nNo further actions run. Earlier actions may have changed only the disposable scene.\n`);await report();throw error;
    }
  }
  status.overall='pass';status.summary='The combined authoring journey completed with shared undo/redo and a matching schema-4 JSON export.';await report();
}catch(error){console.error(error.stack);process.exitCode=1;if(status.overall!=='blocked'){status.overall='blocked';status.summary=error.message;await report();}}
finally{
  await writeFile(join(root,'trace','browser-diagnostics.json'),JSON.stringify(diagnostics,null,2));
  if(context)await context.tracing.stop({path:join(root,'trace','trace.zip')});if(browser)await browser.close();
  if(server&&server.exitCode===null){if(process.platform==='win32')execFileSync('taskkill',['/PID',String(server.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});else server.kill('SIGTERM');}
}
