/** Real raster alpha/order checks, distinct from mocked DOM and browser QA. */
import assert from 'node:assert/strict';
import {createCanvas} from '@napi-rs/canvas';
import {compositeLayer,visibleLayers,sourceBlends,orderedLayers} from '../../studio/static/layers.js';
import {layeredDemoRecipe as demo} from '../../studio/static/layered-demo.js';
const canvas=createCanvas(8,8),buffer=createCanvas(8,8),context=canvas.getContext('2d');
function fill(color){return c=>{c.fillStyle=color;c.fillRect(0,0,8,8);c.fillRect(0,0,8,8);};}
function pixel(){return [...context.getImageData(4,4,1,1).data];}
context.fillStyle='#0000ff';context.fillRect(0,0,8,8);
compositeLayer(context,buffer,.5,fill('#ff0000'));
assert.deepEqual(pixel(),[128,0,127,255], 'nested fills get alpha once');
compositeLayer(context,buffer,1,fill('#0000ff'));assert.deepEqual(pixel(),[0,0,255,255]);
compositeLayer(context,buffer,1,fill('#ff0000'));assert.deepEqual(pixel(),[255,0,0,255]);
context.setTransform(2,0,0,2,0,0);compositeLayer(context,buffer,.05,c=>{c.fillStyle='#ffffff';c.fillRect(0,0,4,4);});
assert.ok(pixel()[1]>=12&&pixel()[1]<=13,'bounded opacity remains a single compositing operation');
assert.equal(context.getTransform().a,2,'compositor preserves target transform');
assert.deepEqual(visibleLayers(demo).map(o=>o.id),['island_lowtide','blend_confluence','island_glass']);
assert.equal(sourceBlends(demo,'island_ember')[0].id,'blend_confluence');
const hidden=structuredClone(demo);hidden.blends[0].style.visible=false;hidden.objects[0].style.visible=false;
assert.deepEqual(visibleLayers(hidden).map(o=>o.id),['island_lagoon','island_lowtide','island_glass']);
hidden.layer_order.reverse();assert.equal(orderedLayers(hidden)[0].id,'island_glass');
assert.deepEqual(demo.layer_order,['island_ember','island_lagoon','island_lowtide','blend_confluence','island_glass']);
console.log('10 real-raster and layer-policy checks passed.');
