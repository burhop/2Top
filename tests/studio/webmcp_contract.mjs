// Contract mock only: this does not assert native browser WebMCP support.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const source = fs.readFileSync('studio/static/webmcp.js', 'utf8');
const load = (suffix) => import('data:text/javascript;base64,' + Buffer.from(source + `\n// ${suffix}`).toString('base64'));
const events = [];
const warnings = [];
console.warn = (...args) => warnings.push(args);
globalThis.CustomEvent = class { constructor(name, options) { this.type = name; this.detail = options.detail; } };
globalThis.window = { dispatchEvent: (e) => events.push(e) };
window.top = window.self = window;
globalThis.document = {};
let fetched = 0;
globalThis.fetch = async () => { fetched++; throw Error('Should not fetch'); };
let adapter = await load('unsupported');
assert.deepEqual(await adapter.registerWebMCP(), {supported:false,registered:0,error:null,reason:'browser-unsupported'});
assert.equal(fetched, 0);
const registered = [];
const schema = {type:'object',properties:{expected_revision:{type:'integer'}},required:['expected_revision'],additionalProperties:false};
document.modelContext = { registerTool: async (tool) => registered.push(tool) };
let sent;
globalThis.fetch = async (path, options) => {
  if (path === '/api/tools') return {ok:true,json:async()=>['set_view','set_keyframe','delete_keyframe'].map(name=>({name,description:name,inputSchema:schema,annotations:{readOnlyHint:false}}))};
  sent = {path,options};
  if (JSON.parse(options.body).expected_revision === 0) return {ok:true,json:async()=>({ok:true,scene:{revision:1}})};
  return {ok:false,status:409,json:async()=>({ok:false,error:{code:'revision_conflict',message:'Read scene again'}})};
};
adapter = await load('supported');
assert.equal((await adapter.registerWebMCP()).registered, 3);
await adapter.registerWebMCP();
assert.equal(registered.length, 3);
assert.deepEqual(registered[0].inputSchema, schema);
// Presentation callbacks must not turn a committed edit into a tool failure.
await adapter.registerWebMCP({onScene: () => {throw Error('render failed')}, onStatus: () => {throw Error('badge failed')}});
const result = await registered[0].execute({expected_revision:0});
assert.equal(result.scene.revision, 1);
assert.equal(sent.path, '/api/tools/set_view');
assert.deepEqual(JSON.parse(sent.options.body), {expected_revision:0});
assert.equal(sent.options.headers['X-Studio-Actor'], 'webmcp');
assert.equal(events.filter(e => e.type === 'tidal:scene').length, 1);
await assert.rejects(registered[0].execute({expected_revision:99}), /Read scene again/);
assert.equal(events.filter(e => e.type === 'tidal:scene').length, 1);
// Cancellation is forwarded unchanged and does not fabricate a scene/result.
const controller = new AbortController();
controller.abort();
let calls = 0;
globalThis.fetch = async (path, options) => {
  calls++;
  assert.equal(options.signal, controller.signal);
  throw new DOMException('Aborted', 'AbortError');
};
await assert.rejects(registered[0].execute({expected_revision:1}, {signal:controller.signal}), {name:'AbortError'});
assert.equal(calls, 1);
assert.equal(events.filter(e => e.type === 'tidal:scene').length, 1);
assert.ok(warnings.length >= 2, 'Observer errors were isolated and reported');
for (const name of ['set_keyframe','delete_keyframe']) {
  const argumentsValue = {expected_revision:2,id:'island_ember',time:6};
  globalThis.fetch = async (path, options) => {
    assert.equal(path, `/api/tools/${name}`);
    assert.deepEqual(JSON.parse(options.body), argumentsValue);
    return {ok:true,json:async()=>({ok:true,scene:{revision:3}})};
  };
  assert.equal((await registered.find(tool=>tool.name===name).execute(argumentsValue)).scene.revision, 3);
}
console.log('WebMCP contract checks passed (mock browser API).');
