/** Numeric/source mirror of studio/layout.py; placement uses authored centers. */
import { sampleParameters } from './choreography.js';
import { transformedIslands } from './transforms.js';

export function layoutPlan(scene,ids,mode,time=0) {
  if(!['align_x','align_y','space_x','space_y'].includes(mode))throw new Error('Choose a supported center layout');
  if(ids.length<2||ids.length>16||new Set(ids).size!==ids.length)throw new Error('Choose 2..16 unique island IDs');
  if(mode.startsWith('space')&&ids.length<3)throw new Error('Even spacing needs at least three islands');
  const islands=new Map(scene.objects.map(island=>[island.id,island]));
  for(const id of ids)if(!islands.has(id)){
    if(scene.blends.some(blend=>blend.id===id))throw new Error('Center layout accepts islands only; select retained sources instead of a blend');
    throw new Error(`Unknown island: ${id}`);
  }
  const axis=mode.at(-1),anchors=new Map(ids.map(id=>{const o=islands.get(id);return [id,sampleParameters(o.parameters,o.keyframes,time)];})),targets=new Map();
  if(mode.startsWith('align')){
    const values=[...ids].sort().map(id=>anchors.get(id)[axis]);
    const mean=values.every(value=>value===values[0])?values[0]:values.reduce((sum,value)=>sum+value,0)/ids.length;
    for(const id of ids)targets.set(id,mean);
  } else {
    const ordered=[...ids].sort((a,b)=>anchors.get(a)[axis]-anchors.get(b)[axis]||(a<b?-1:a>b?1:0));
    const low=anchors.get(ordered[0])[axis],high=anchors.get(ordered.at(-1))[axis];
    ordered.forEach((id,i)=>targets.set(id,i===0?low:i===ordered.length-1?high:low+(high-low)*i/(ordered.length-1)));
  }
  return [...ids].sort().map(id=>({id,dx:axis==='x'?targets.get(id)-anchors.get(id).x:0,dy:axis==='y'?targets.get(id)-anchors.get(id).y:0}));
}
export function laidOutIslands(scene,ids,mode,time=0) {
  const islands=new Map(scene.objects.map(island=>[island.id,island]));
  return layoutPlan(scene,ids,mode,time).map(move=>transformedIslands([islands.get(move.id)],move)[0]);
}
