/** Cross-platform lifecycle regressions for the restart-test helper. */
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {spawn} from 'node:child_process';
import {setTimeout as delay} from 'node:timers/promises';
import {watchOwnedChild} from './disposable-studio.mjs';

// Model the actual Node signal-exit contract, including synchronous event delivery.
const child=new EventEmitter();Object.assign(child,{pid:12345,exitCode:null,signalCode:null});
const signals=[];child.kill=signal=>{signals.push(signal);child.signalCode=signal;child.emit('exit',null,signal);return true;};
const stop=watchOwnedChild(child);
await Promise.race([stop('linux'),delay(1000).then(()=>{throw new Error('Signal exit was missed');})]);
assert.equal(child.exitCode,null);assert.equal(child.signalCode,'SIGTERM');assert.deepEqual(signals,['SIGTERM']);
await stop('linux');assert.deepEqual(signals,['SIGTERM']);
console.log('PASS signal exit with null exitCode completes once without a second kill');

const already=new EventEmitter();Object.assign(already,{pid:12346,exitCode:null,signalCode:null});
let kills=0;already.kill=()=>{kills++;};const stopAlready=watchOwnedChild(already);
already.signalCode='SIGTERM';already.emit('exit',null,'SIGTERM');await stopAlready('linux');assert.equal(kills,0);
console.log('PASS a previously emitted signal exit does not wait or terminate again');

// Use a real newly owned Node process on the current OS, forcing the POSIX path.
const actual=spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{windowsHide:true,stdio:'ignore'});
const stopActual=watchOwnedChild(actual);await new Promise((resolve,reject)=>{actual.once('spawn',resolve);actual.once('error',reject);});
await stopActual('linux');assert.ok(actual.exitCode!==null||actual.signalCode!==null);await stopActual('linux');
console.log('PASS real owned child termination completes through the POSIX lifecycle path');

const win=new EventEmitter();Object.assign(win,{pid:12347,exitCode:null,signalCode:null});
const stopWin=watchOwnedChild(win);let calls=0;
await stopWin('win32',async(command,args,options)=>{calls++;assert.equal(command,'taskkill');assert.deepEqual(args,['/PID','12347','/T','/F']);assert.equal(options.windowsHide,true);win.exitCode=1;win.emit('exit',1,null);});
await stopWin('win32');assert.equal(calls,1);
console.log('PASS Windows stops only its owned process tree once');
console.log('4 disposable process lifecycle checks passed.');
