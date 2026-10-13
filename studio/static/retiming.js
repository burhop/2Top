/** Numeric mirror of studio/retiming.py; exact times, no rounding/wrapping. */
import { sampleParameters } from './choreography.js';

export function retimedIslands(scene,targets,delta) {
  if(!Array.isArray(targets)||targets.length<1||targets.length>16||new Set(targets.map(t=>t.id)).size!==targets.length)throw new Error('Choose 1..16 unique island tracks');
  if(typeof delta!=='number'||!Number.isFinite(delta)||delta < -12||delta > 12)throw new Error('Time shift must be finite within -12..12 seconds');
  const islands=new Map(scene.objects.map(o=>[o.id,o]));
  return targets.map(target=>{
    const island=islands.get(target.id);
    if(!island)throw new Error('Select an existing island track');
    const times=target.times;
    if(!Array.isArray(times)||times.length<1||times.length>24||new Set(times).size!==times.length||times.some(t=>typeof t!=='number'||!Number.isFinite(t)||t<0||t>12))throw new Error('Choose 1..24 unique exact source times');
    const selected=new Set(times),existing=new Set(island.keyframes.map(k=>k.time));
    if(times.some(t=>!existing.has(t)))throw new Error('No keyframe at one of the exact source times');
    const untouched=new Set([...existing].filter(t=>!selected.has(t))),destinations=times.map(t=>t+delta);
    if(destinations.some(t=>t<0||t>12))throw new Error('Every shifted key must stay within 0..12 seconds');
    if(new Set(destinations).size!==destinations.length||destinations.some(t=>untouched.has(t)))throw new Error('Shifted keys collide with another destination or an unselected pose');
    const changed=structuredClone(island);
    for(const key of changed.keyframes)if(selected.has(key.time))key.time+=delta;
    changed.keyframes.sort((a,b)=>a.time-b.time);
    sampleParameters(changed.parameters,changed.keyframes,0);
    return changed;
  });
}
