/** Numeric mirror of legacy RFunctionCurve + geometry/static_blend.py. */
import { createEvaluator, normalizeParameters, contourLevels } from './geometry.js';

export function createBlend(first, second, operation = 'smooth_union', amount = .6) {
  if (!['union', 'smooth_union'].includes(operation) || typeof amount !== 'number' || !Number.isFinite(amount) || amount < 0 || amount > 1) throw new TypeError('Invalid static blend');
  const parameters = [normalizeParameters(first), normalizeParameters(second)];
  const [a, b] = parameters.map(p => createEvaluator(p, 0, 0));
  const alpha = operation === 'smooth_union' ? amount : 0;
  const extents = parameters.map(p => {
    const extent = p.radius * Math.max(Math.sqrt(p.elongation), 1 / Math.sqrt(p.elongation)) * (1.5 + alpha * .75);
    return [p.x - extent, p.x + extent, p.y - extent, p.y + extent];
  });
  return {
    bounds: [Math.min(...extents.map(b=>b[0])), Math.max(...extents.map(b=>b[1])), Math.min(...extents.map(b=>b[2])), Math.max(...extents.map(b=>b[3]))],
    evaluate: (x,y) => { const f=a(x,y),g=b(x,y); return alpha ? (f+g-Math.sqrt((f-g)**2+alpha**2))/2 : Math.min(f,g); },
  };
}

export function blendContours(first, second, operation, amount, count = 16, resolution = 128) {
  if (!Number.isInteger(resolution) || resolution < 24 || resolution > 192) throw new RangeError('Resolution must be 24..192');
  const field = createBlend(first, second, operation, amount), n = resolution + 1;
  const levels = contourLevels(Math.min(16, count)).map(level=>level-1);
  const values = new Float64Array(n*n), bounds = field.bounds;
  for(let row=0;row<n;row++)for(let col=0;col<n;col++) values[row*n+col]=field.evaluate(bounds[0]+col/resolution*(bounds[1]-bounds[0]),bounds[2]+row/resolution*(bounds[3]-bounds[2]));
  return contoursFromGrid(values,bounds,levels,resolution);
}

export function contoursFromGrid(values,bounds,levels,resolution) {
  const n=resolution+1, layers=[];
  for(const level of levels) {
    const points=new Map(),neighbors=new Map(),segments=[];
    const crossing=(a,b)=>{
      if(a>b)[a,b]=[b,a];
      const f=(level-values[a])/(values[b]-values[a]);
      const key=f===0?`v${a}`:f===1?`v${b}`:`${a}:${b}`;
      if(!points.has(key)) {
        const gx=a%n+f*(b%n-a%n),gy=Math.floor(a/n)+f*(Math.floor(b/n)-Math.floor(a/n));
        points.set(key,[bounds[0]+gx/resolution*(bounds[1]-bounds[0]),bounds[2]+gy/resolution*(bounds[3]-bounds[2])]);
      }
      return key;
    };
    for(let row=0;row<resolution;row++)for(let col=0;col<resolution;col++) {
      const a=row*n+col;
      for(const tri of [[a,a+1,a+n+1],[a,a+n+1,a+n]]) {
        const inside=tri.map(v=>values[v]<level);
        if(inside.every(Boolean)||!inside.some(Boolean))continue;
        const keys=[[0,1],[1,2],[2,0]].filter(([i,j])=>inside[i]!==inside[j]).map(([i,j])=>crossing(tri[i],tri[j]));
        if(keys[0]===keys[1])continue;
        const edge=segments.length;segments.push(keys);
        for(const key of keys){if(!neighbors.has(key))neighbors.set(key,[]);neighbors.get(key).push(edge);}
      }
    }
    const visited=new Set(),paths=[];let omitted=0;
    for(let edge=0;edge<segments.length;edge++) {
      if(visited.has(edge))continue;
      const start=segments[edge][0];let key=start,current=edge,closed=false;
      const path=[points.get(start)];
      while(!visited.has(current)) {
        visited.add(current);const[a,b]=segments[current];key=key===a?b:a;path.push(points.get(key));
        if(key===start){closed=true;break;}
        const candidates=neighbors.get(key).filter(e=>!visited.has(e));if(!candidates.length)break;current=candidates[0];
      }
      let area=0;for(let i=1;i<path.length;i++)area+=path[i-1][0]*path[i][1]-path[i][0]*path[i-1][1];
      if(closed&&path.length>=4&&Math.abs(area)>1e-10)paths.push(path);else omitted++;
    }
    layers.push({level,paths,omitted});
  }
  return layers;
}
