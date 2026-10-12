/** Pure mirror of studio/transforms.py; never clamp an authored group transform. */
import { PARAMETER_BOUNDS } from './geometry.js';

export function resolveIslands(scene, layerIds) {
  const layers=new Map([...scene.objects,...scene.blends].map(layer=>[layer.id,layer]));
  const targets=new Set();
  for(const id of layerIds) {
    const layer=layers.get(id);if(!layer)throw new Error(`Unknown layer: ${id}`);
    for(const target of layer.type==='island'?[id]:[layer.source_a,layer.source_b])targets.add(target);
  }
  const available=new Set(scene.objects.map(island=>island.id));
  for(const target of targets)if(!available.has(target))throw new Error(`Unknown island: ${target}`);
  return scene.objects.filter(island=>targets.has(island.id));
}
export function transformPose(pose,{dx=0,dy=0,scale=1,rotation=0,pivot}) {
  const result={...pose};
  if(scale===1&&rotation===0){result.x=pose.x+dx;result.y=pose.y+dy;}
  else {
    const angle=rotation*Math.PI/180,cosine=Math.cos(angle),sine=Math.sin(angle);
    const x=(pose.x-pivot.x)*scale,y=(pose.y-pivot.y)*scale;
    result.x=pivot.x+x*cosine-y*sine+dx;result.y=pivot.y+x*sine+y*cosine+dy;
  }
  result.radius=pose.radius*scale;result.rotation=pose.rotation+rotation;
  for(const name of ['x','y','radius','rotation']) {
    const [low,high]=PARAMETER_BOUNDS[name];
    if(!Number.isFinite(result[name])||result[name]<low||result[name]>high)throw new Error(`Whole-path transform exceeds ${name} limits (${low}..${high}); use a smaller change`);
  }
  return result;
}
export function transformedIslands(islands,options={}) {
  if(!islands.length)throw new Error('Choose at least one island or blend');
  const pivot=options.pivot||Object.fromEntries(['x','y'].map(name=>[name,islands.reduce((sum,island)=>sum+island.parameters[name],0)/islands.length]));
  return islands.map(island=>({...island,style:{...island.style},parameters:transformPose(island.parameters,{...options,pivot}),keyframes:island.keyframes.map(key=>({...key,parameters:transformPose(key.parameters,{...options,pivot})}))}));
}
