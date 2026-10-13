/** Owned loopback instances for restart tests. Never attach to saved/user port 8000. */
import {spawn,execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {setTimeout as delay} from 'node:timers/promises';
import {writeFile} from 'node:fs/promises';
const run=promisify(execFile);
export async function startDisposableStudio(testInfo,{port=8770,storage}={}){
  if(port!==8770)throw new Error('Restart QA owns only port 8770');
  const origin=`http://127.0.0.1:${port}`;
  try{await fetch(origin+'/api/health',{signal:AbortSignal.timeout(1000)});throw new Error('Restart test port is occupied; refusing to reuse it');}catch(error){if(error.name!=='TypeError')throw error;}
  const args=['-m','studio.app','--port',String(port),...(storage?['--scene',storage]:['--ephemeral'])];
  const child=spawn(process.env.STUDIO_PYTHON||'python',args,{windowsHide:true});
  let log='',spawnError;child.stdout.on('data',data=>log+=data);child.stderr.on('data',data=>log+=data);child.on('error',error=>spawnError=error);
  const stop=async()=>{
    if(child.exitCode===null&&child.pid){if(process.platform==='win32')await run('taskkill',['/PID',String(child.pid),'/T','/F'],{windowsHide:true});else {child.kill('SIGTERM');await Promise.race([new Promise(resolve=>child.once('exit',resolve)),delay(8000)]);if(child.exitCode===null){child.kill('SIGKILL');await new Promise(resolve=>child.once('exit',resolve));}}}
    await writeFile(testInfo.outputPath(`owned-server-${child.pid}.log`),log);
  };
  try{
    for(let i=0;i<100;i++){
      if(spawnError)throw spawnError;if(child.exitCode!==null)throw new Error(`Owned service exited: ${log}`);
      try{const response=await fetch(origin+'/api/health');if(response.ok)return {origin,stop,pid:child.pid};}catch{}
      await delay(150);
    }
    throw new Error('Owned service did not become available');
  }catch(error){await stop();throw error;}
}
export async function disposableScene(origin){const response=await fetch(origin+'/api/scene');if(!response.ok)throw new Error('Cannot read owned scene');return response.json();}
