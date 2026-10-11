/**
 * Tidal Atlas: declarative radial-twist island geometry, independent of the UI.
 * Keep formulas and numeric bounds paired with geometry/kinetic.py.
 * evaluate() is an implicit field, NOT an exact signed-distance function.
 * All contours are sampled closed polylines, ordered outermost to innermost.
 */
const TAU = Math.PI * 2;
export const LOOP_DURATION = 12;
export const DEFAULT_PARAMETERS = Object.freeze({
  x: 500, y: 350, radius: 230, elongation: 1.2,
  rotation: -24, lobes: 3, warp: 0.7, phase: 0.4,
});
export const PARAMETER_BOUNDS = Object.freeze({
  x: Object.freeze([-1000, 2000]), y: Object.freeze([-700, 1400]),
  radius: Object.freeze([80, 400]), elongation: Object.freeze([0.4, 2.5]),
  rotation: Object.freeze([-360, 360]), lobes: Object.freeze([2, 9]),
  warp: Object.freeze([0, 1]), phase: Object.freeze([0, TAU]),
});
export const MAX_CONTOURS = 80;
export const MAX_SAMPLES = 720;
export const MAX_COORDINATE = 1e9;

function finiteNumber(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new TypeError(`${name} must be a finite number`);
  }
  return value;
}

function plainObject(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

export function normalizeParameters(parameters = {}) {
  if (parameters === null) parameters = {};
  if (!plainObject(parameters)) throw new TypeError('parameters must be a plain numeric mapping');
  if (Object.keys(parameters).some(name => !Object.hasOwn(DEFAULT_PARAMETERS, name))) {
    throw new TypeError('unknown island parameter');
  }
  const result = {};
  for (const [name, fallback] of Object.entries(DEFAULT_PARAMETERS)) {
    const value = finiteNumber(Object.hasOwn(parameters, name) ? parameters[name] : fallback, name);
    const [lower, upper] = PARAMETER_BOUNDS[name];
    const bounded = Math.min(upper, Math.max(lower, value));
    result[name] = name === 'lobes' ? Math.floor(bounded + 0.5) : bounded;
  }
  return result;
}

function boundedInteger(value, name, lower, upper) {
  finiteNumber(value, name);
  if (!Number.isInteger(value)) throw new TypeError(`${name} must be an integer`);
  return Math.min(upper, Math.max(lower, value));
}

function motionState(parameters, time, motion) {
  finiteNumber(time, 'time');
  motion = Math.min(1, Math.max(0, finiteNumber(motion, 'motion')));
  const period = LOOP_DURATION;
  // JS remainder differs from Python modulo for negatives; normalize it once.
  const remainder = time % period;
  const t = (remainder < 0 ? remainder + period : remainder) * TAU / LOOP_DURATION;
  const phase = parameters.phase;
  const breath = 1 + motion * (
    0.032 * Math.sin(t + phase) + 0.012 * Math.sin(3 * t + 0.7 * phase)
  );
  return {
    x: parameters.x + parameters.radius * 0.012 * motion * (Math.sin(t + phase) - Math.sin(phase)),
    y: parameters.y + parameters.radius * 0.016 * motion * (Math.cos(2 * t + phase) - Math.cos(phase)),
    scale: parameters.radius * breath,
    stretch: Math.sqrt(parameters.elongation),
    rotation: parameters.rotation * Math.PI / 180 + 0.026 * motion * Math.sin(t + phase),
    phase: phase + 0.075 * motion * Math.sin(t + 0.5 * phase),
    twistMotion: 0.09 * motion * Math.sin(2 * t + phase),
  };
}

function profile(theta, parameters, state) {
  const { warp, lobes } = parameters;
  const phase = state.phase;
  return 1
    + (0.052 + 0.085 * warp) * Math.cos(lobes * theta + phase)
    + (0.026 + 0.026 * warp) * Math.sin((lobes + 1) * theta - 0.7 * phase)
    + 0.07 * Math.cos(theta - 0.6)
    - (0.15 + 0.49 * warp) * Math.exp(3.6 * (Math.cos(theta - 1.1 - 0.4 * phase) - 1));
}

function twist(rho, parameters, state) {
  return parameters.warp * (2.35 / (1 + 2.7 * rho * rho) - 0.62)
    + state.twistMotion / (1 + rho * rho);
}

export function contourLevels(count = 24) {
  count = boundedInteger(count, 'count', 2, MAX_CONTOURS);
  return Array.from({ length: count }, (_, i) => 1 - 0.82 * (i / (count - 1)) ** 0.86);
}

/** Numeric count/samples API; each ring includes its repeated final point. */
export function generateContours(parameters = {}, time = 0, motion = 0.45, count = 24, samples = 180) {
  parameters = normalizeParameters(parameters);
  const state = motionState(parameters, time, motion);
  const levels = contourLevels(count);
  samples = boundedInteger(samples, 'samples', 24, MAX_SAMPLES);
  const cosine = Math.cos(state.rotation);
  const sine = Math.sin(state.rotation);
  const angles = new Float64Array(samples);
  const profiles = new Float64Array(samples);
  for (let i = 0; i < samples; i++) {
    angles[i] = i * TAU / samples;
    profiles[i] = profile(angles[i], parameters, state);
  }
  return levels.map(level => {
    const ring = new Array(samples + 1);
    for (let i = 0; i < samples; i++) {
      const rho = level * profiles[i];
      const angle = angles[i] + twist(rho, parameters, state);
      const x = rho * Math.cos(angle) * state.stretch * state.scale;
      const y = rho * Math.sin(angle) / state.stretch * state.scale;
      ring[i] = [state.x + x * cosine - y * sine, state.y + x * sine + y * cosine];
    }
    ring[samples] = [...ring[0]];
    return ring;
  });
}

/** Scalar field; zero on the outer shore and negative inside. */
export function evaluate(x, y, parameters = {}, time = 0, motion = 0.45) {
  finiteNumber(x, 'x');
  finiteNumber(y, 'y');
  if (Math.abs(x) > MAX_COORDINATE || Math.abs(y) > MAX_COORDINATE) {
    throw new RangeError('coordinates must be finite and within ±1e9');
  }
  return createEvaluator(parameters, time, motion)(x, y);
}

/** Reuse normalized parameters/motion state for bounded grid evaluation. */
export function createEvaluator(parameters = {}, time = 0, motion = 0.45) {
  parameters = normalizeParameters(parameters);
  const state = motionState(parameters, time, motion);
  const cosine = Math.cos(state.rotation), sine = Math.sin(state.rotation);
  return (x, y) => {
  finiteNumber(x, 'x'); finiteNumber(y, 'y');
  if (Math.abs(x) > MAX_COORDINATE || Math.abs(y) > MAX_COORDINATE) throw new RangeError('Coordinates exceed the finite grid bounds');
  const dx = x - state.x;
  const dy = y - state.y;
  const localX = (dx * cosine + dy * sine) / state.scale / state.stretch;
  const localY = (-dx * sine + dy * cosine) / state.scale * state.stretch;
  const rho = Math.hypot(localX, localY);
  const theta = Math.atan2(localY, localX) - twist(rho, parameters, state);
  return rho / profile(theta, parameters, state) - 1;
  };
}

export function toRecipe(parameters = {}) {
  return { type: 'tidal_island', version: 1, parameters: normalizeParameters(parameters) };
}

export function fromRecipe(recipe) {
  if (!plainObject(recipe) || Object.keys(recipe).sort().join(',') !== 'parameters,type,version') {
    throw new TypeError('invalid island recipe envelope');
  }
  if (recipe.type !== 'tidal_island' || recipe.version !== 1 || !plainObject(recipe.parameters)) {
    throw new TypeError('unsupported island recipe');
  }
  return normalizeParameters(recipe.parameters);
}
