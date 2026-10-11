/** Deterministic numeric mirror of geometry/choreography.py. No clocks or UI. */
import { LOOP_DURATION, PARAMETER_BOUNDS, normalizeParameters } from './geometry.js';
export const POSE_FIELDS = Object.freeze(['x', 'y', 'radius', 'elongation', 'rotation', 'warp']);
export const MAX_KEYFRAMES = 24;

export function sampleParameters(parameters, keys = [], time = 0) {
  if (typeof time !== 'number' || !Number.isFinite(time)) throw new TypeError('Time must be finite');
  if (!Array.isArray(keys) || keys.length > MAX_KEYFRAMES) throw new TypeError('At most 24 keyframes');
  let previous = -1;
  for (const key of keys) {
    if (!key || Object.keys(key).sort().join(',') !== 'easing,parameters,time' ||
        typeof key.time !== 'number' || !Number.isFinite(key.time) || key.time < 0 || key.time > LOOP_DURATION || key.time <= previous ||
        !['linear', 'smooth'].includes(key.easing)) throw new TypeError('Invalid keyframe');
    if (!key.parameters || Object.keys(key.parameters).sort().join(',') !== [...POSE_FIELDS].sort().join(',')) throw new TypeError('Incomplete pose');
    for (const name of POSE_FIELDS) {
      const value = key.parameters[name], [low, high] = PARAMETER_BOUNDS[name];
      if (typeof value !== 'number' || !Number.isFinite(value) || value < low || value > high) throw new TypeError('Invalid pose value');
    }
    previous = key.time;
  }
  const result = normalizeParameters(parameters);
  if (!keys.length) return result;
  const phase = time >= 0 && time <= LOOP_DURATION ? time : ((time % LOOP_DURATION) + LOOP_DURATION) % LOOP_DURATION;
  let left = keys[0], right = left;
  if (phase >= keys.at(-1).time) left = right = keys.at(-1);
  else if (phase > left.time) {
    for (let i = 1; i < keys.length; i++) {
      left = keys[i - 1]; right = keys[i];
      if (phase <= right.time) break;
    }
  }
  let f = right.time === left.time ? 0 : (phase - left.time) / (right.time - left.time);
  if (left.easing === 'smooth') f = f * f * (3 - 2 * f);
  for (const name of POSE_FIELDS) result[name] = left.parameters[name] + f * (right.parameters[name] - left.parameters[name]);
  return result;
}
