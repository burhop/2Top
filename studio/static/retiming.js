/** Numeric mirror of studio/retiming.py; exact times, no rounding/wrapping. */
import { sampleParameters } from './choreography.js';

export function retimedIslands(scene,targets,delta) {
  if(typeof delta!=='number'||!Number.isFinite(delta)||delta < -12||delta > 12)throw new Error('Time shift must be finite within -12..12 seconds');
  return mappedIslands(scene,targets,time=>time+delta);
}
export function scaledTime(time,anchor,factor){return factor===1||time===anchor?time:anchor+(time-anchor)*factor;}
export function scaledIslands(scene,targets,anchor,factor){
  if(typeof anchor!=='number'||!Number.isFinite(anchor)||anchor<0||anchor>12)throw new Error('Anchor must be finite within 0..12 seconds');
  if(typeof factor!=='number'||!Number.isFinite(factor)||factor<.1||factor>4)throw new Error('Time scale factor must be finite within 0.1..4');
  return mappedIslands(scene,targets,time=>scaledTime(time,anchor,factor));
}
function mappedIslands(scene,targets,mapTime){
  if(!Array.isArray(targets)||targets.length<1||targets.length>16||new Set(targets.map(t=>t.id)).size!==targets.length)throw new Error('Choose 1..16 unique island tracks');
  const islands=new Map(scene.objects.map(o=>[o.id,o]));
  return targets.map(target=>{
    const island=islands.get(target.id);
    if(!island)throw new Error('Select an existing island track');
    const times=target.times;
    if(!Array.isArray(times)||times.length<1||times.length>24||new Set(times).size!==times.length||times.some(t=>typeof t!=='number'||!Number.isFinite(t)||t<0||t>12))throw new Error('Choose 1..24 unique exact source times');
    const selected=new Set(times),existing=new Set(island.keyframes.map(k=>k.time));
    if(times.some(t=>!existing.has(t)))throw new Error('No keyframe at one of the exact source times');
    const untouched=new Set([...existing].filter(t=>!selected.has(t))),mapping=new Map(times.map(t=>[t,mapTime(t)])),destinations=[...mapping.values()];
    if(destinations.some(t=>t<0||t>12))throw new Error('Every retimed key must stay within 0..12 seconds');
    if(new Set(destinations).size!==destinations.length||destinations.some(t=>untouched.has(t)))throw new Error('Retimed keys collide with another destination or an unselected pose');
    const changed=structuredClone(island);
    for(const key of changed.keyframes)if(selected.has(key.time))key.time=mapping.get(key.time);
    changed.keyframes.sort((a,b)=>a.time-b.time);
    sampleParameters(changed.parameters,changed.keyframes,0);
    return changed;
  });
}
