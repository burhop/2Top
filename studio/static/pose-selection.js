/** Bounded local pose-selection memory. No recipe fields or persistent key IDs. */
export class PoseSelectionMemory {
  constructor(limit=64){this.limit=limit;this.cache=new Map();this.token='';}
  remember(state){
    if(!state.context||!state.signature)return;
    const key=state.context+'\n'+state.signature;this.cache.delete(key);this.cache.set(key,{times:[...state.times],selecting:state.selecting});
    while(this.cache.size>this.limit)this.cache.delete(this.cache.keys().next().value);
  }
  sync(scene,object,prior){
    const context=`${scene?.session_id}/${scene?.document_id}/${object?.id}`,signature=JSON.stringify(object?.keyframes||[]),timeSignature=JSON.stringify((object?.keyframes||[]).map(key=>key.time));
    const token=`${scene?.session_id}/${scene?.document_id}/${scene?.revision}`,operation=scene?.history?.entries?.at(-1)?.operation;
    const imported=token!==this.token&&operation==='load_recipe';this.token=token;
    if(prior.context!==context||imported){this.cache.clear();return {context,signature,timeSignature,times:[],selecting:false};}
    this.remember(prior);
    const available=new Set((object?.keyframes||[]).map(key=>key.time));
    if(prior.timeSignature===timeSignature)return {context,signature,timeSignature,times:prior.times.filter(time=>available.has(time)),selecting:prior.selecting};
    const restored=['undo','redo'].includes(operation)?this.cache.get(context+'\n'+signature):null;
    return {context,signature,timeSignature,times:restored?restored.times.filter(time=>available.has(time)):[],selecting:restored?.selecting||false};
  }
}
