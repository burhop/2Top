/** Owned loopback instances for restart tests. Never attach to saved/user port 8000. */
import {spawn,execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {setTimeout as delay} from 'node:timers/promises';
import {writeFile} from 'node:fs/promises';
const run=promisify(execFile);
export function watchOwnedChild(child){
  // Bind before termination: signal exits have exitCode=null and signalCode set.
  const exited=new Promise(resolve=>child.once('exit',resolve));
  const finished=()=>child.exitCode!==null||child.signalCode!==null;
  let stopping;
  return (platform=process.platform,terminateTree=run)=>stopping??=(async()=>{
    if(!child.pid||finished())return;
    if(platform==='win32'){
      await terminateTree('taskkill',['/PID',String(child.pid),'/T','/F'],{windowsHide:true});
    }else{
      child.kill('SIGTERM');
      const timer=new AbortController();
      try{await Promise.race([exited,delay(8000,undefined,{signal:timer.signal})]);}finally{timer.abort();}
      if(!finished())child.kill('SIGKILL');
    }
    if(!finished())await exited;
  })();
}
export async function startDisposableStudio(testInfo,{port=8770,storage}={}){
  if(port!==8770)throw new Error('Restart QA owns only port 8770');
  const origin=`http://127.0.0.1:${port}`;
  try{await fetch(origin+'/api/health',{signal:AbortSignal.timeout(1000)});throw new Error('Restart test port is occupied; refusing to reuse it');}catch(error){if(error.name!=='TypeError')throw error;}
  const args=['-m','studio.app','--port',String(port),...(storage?['--scene',storage]:['--ephemeral'])];
  const child=spawn(process.env.STUDIO_PYTHON||'python',args,{windowsHide:true});
  const stopChild=watchOwnedChild(child);
  let log='',spawnError;child.stdout.on('data',data=>log+=data);child.stderr.on('data',data=>log+=data);child.on('error',error=>spawnError=error);
  const stop=async()=>{
    await stopChild();
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
