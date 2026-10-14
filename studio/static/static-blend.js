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
    evaluate: (x,y) => {
      const f=a(x,y),g=b(x,y);
      if (!alpha) return Math.min(f,g);
      let difference=f-g,effectiveAlpha=alpha;
      if (!Number.isFinite(difference)&&Number.isFinite(f)&&Number.isFinite(g)) {
        difference=.5*f-.5*g;effectiveAlpha=.5*alpha;
      }
      const scale=Math.max(Math.abs(difference),effectiveAlpha),d=difference/scale,h=effectiveAlpha/scale;
      return Math.min(f,g)-(.5*alpha)*(h/(Math.hypot(d,h)+Math.abs(d)));
    },
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
  if (!Number.isInteger(resolution)||resolution<1||resolution>192) throw new RangeError('Resolution must be 1..192');
  if (!Array.isArray(bounds)||bounds.length!==4||!bounds.every(v=>typeof v==='number'&&Number.isFinite(v))||bounds[0]>=bounds[1]||bounds[2]>=bounds[3]||!Number.isFinite(bounds[1]-bounds[0])||!Number.isFinite(bounds[3]-bounds[2])) throw new RangeError('Invalid finite sampling bounds');
  if (!Array.isArray(levels)||levels.length<1||levels.length>16||!levels.every(v=>typeof v==='number'&&Number.isFinite(v))) throw new RangeError('At most 16 finite contour levels');
  const n=resolution+1, layers=[];
  if (!(Array.isArray(values)||ArrayBuffer.isView(values))||values.length!==n*n) throw new RangeError('Sampled grid must have (resolution + 1)^2 values');
  if (!Array.from(values).every(v=>typeof v==='number'&&Number.isFinite(v))) throw new RangeError('The sampled field must be finite');
  for(const level of levels) {
    const points=new Map(),localPoints=new Map(),neighbors=new Map(),segments=[],unique=new Set();
    const crossing=(a,b)=>{
      if(a>b)[a,b]=[b,a];
      const numerator=level-values[a],denominator=values[b]-values[a],scale=Math.max(Math.abs(values[a]),Math.abs(values[b]),Math.abs(level));
      const f=Number.isFinite(numerator)&&Number.isFinite(denominator)?numerator/denominator:(level/scale-values[a]/scale)/(values[b]/scale-values[a]/scale);
      const key=f===0?`v${a}`:f===1?`v${b}`:`${a}:${b}`;
      if(!points.has(key)) {
        const gx=a%n+f*(b%n-a%n),gy=Math.floor(a/n)+f*(Math.floor(b/n)-Math.floor(a/n));
        points.set(key,[bounds[0]+gx/resolution*(bounds[1]-bounds[0]),bounds[2]+gy/resolution*(bounds[3]-bounds[2])]);
        const point=points.get(key);
        localPoints.set(key,[(point[0]-bounds[0])/(bounds[1]-bounds[0]),(point[1]-bounds[2])/(bounds[3]-bounds[2])]);
      }
      return key;
    };
    for(let row=0;row<resolution;row++)for(let col=0;col<resolution;col++) {
      const a=row*n+col;
      for(const tri of [[a,a+1,a+n+1],[a,a+n+1,a+n]]) {
        const inside=tri.map(v=>values[v]<level);
        if(inside.every(Boolean)||!inside.some(Boolean))continue;
        const keys=[[0,1],[1,2],[2,0]].filter(([i,j])=>inside[i]!==inside[j]).map(([i,j])=>crossing(tri[i],tri[j]));
        const identity=[...keys].sort().join('|');
        if(keys[0]===keys[1]||unique.has(identity))continue;
        unique.add(identity);
        const edge=segments.length;segments.push(keys);
        for(const key of keys){if(!neighbors.has(key))neighbors.set(key,[]);neighbors.get(key).push(edge);}
      }
    }
    const visited=new Set(),paths=[];let omitted=0;
    for(let edge=0;edge<segments.length;edge++) {
      if(visited.has(edge))continue;
      const start=segments[edge][0];let key=start,current=edge,closed=false;
      const component=new Set(),vertices=new Set(),pending=[edge];
      while(pending.length) {
        const candidate=pending.pop();if(component.has(candidate))continue;component.add(candidate);
        for(const vertex of segments[candidate]) {
          vertices.add(vertex);for(const next of neighbors.get(vertex))if(!component.has(next))pending.push(next);
        }
      }
      if([...vertices].some(v=>neighbors.get(v).length!==2)) {
        for(const candidate of component)visited.add(candidate);omitted++;continue;
      }
      const path=[points.get(start)],local=[localPoints.get(start)];
      while(!visited.has(current)) {
        visited.add(current);const[a,b]=segments[current];key=key===a?b:a;path.push(points.get(key));local.push(localPoints.get(key));
        if(key===start){closed=true;break;}
        const candidates=neighbors.get(key).filter(e=>!visited.has(e));if(!candidates.length)break;current=candidates[0];
      }
      const [ox,oy]=local[0];let area=0;
      for(let i=1;i<local.length;i++)area+=(local[i-1][0]-ox)*(local[i][1]-oy)-(local[i][0]-ox)*(local[i-1][1]-oy);
      const span=Math.max(...[0,1].map(axis=>Math.max(...local.map(p=>p[axis]))-Math.min(...local.map(p=>p[axis]))));
      const tolerance=32*Number.EPSILON*span**2*local.length;
      if(closed&&path.length>=4&&Math.abs(area)>tolerance)paths.push(path);else omitted++;
    }
    layers.push({level,paths,omitted});
  }
  return layers;
}
