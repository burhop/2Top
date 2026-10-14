# Reusable implicit backend: 0.12.0

This milestone fixes measured failures in existing field evaluation, smooth
composition and sampled contour extraction. Public constructors, recipe schema
4, serialization dispatch and the 23 studio tools remain compatible. No new
dependencies are required.

## Field evaluation and normals

`ImplicitCurve` and `ProceduralCurve` accept real scalar or NumPy-broadcastable
coordinates. Two scalar inputs return a float; array inputs, including zero-
dimensional arrays, return the broadcast shape. Constant fields and constant
gradient components fill that shape. Empty arrays are supported. Complex,
object and string coordinates/results fail explicitly. Scalar-only procedural
callbacks still use the existing vectorized fallback.

NumPy domain/overflow values remain observable during evaluation. Sampling
rejects nonfinite values. A scalar normal requires a finite field value and a
finite nonzero gradient. Max-component scaling prevents normalization overflow
and underflow; positive rescaling of a finite field preserves its direction.
Procedural gradients still use the existing fixed central-difference step of
`1e-8`; this does not establish accurate differentiation at arbitrary scales.
Procedural normals also compare that central derivative with a half-step estimate
and reject directions dominated by the estimated second-order truncation error.
This preserves cusp rejection without an absolute field-magnitude cutoff. It is
a conservative convergence heuristic, not a proof of differentiability; arbitrary
nonsmooth callbacks can evade a two-step check.

Smooth union retains the mathematical expression
`(f1 + f2 - hypot(f1 - f2, alpha)) / 2`, with finite positive `alpha`. Numeric
evaluation uses a scaled, rationalized correction to `min(f1, f2)` and matching
gradient weights, avoiding squared magnitudes and cancellation of small weights.
Tests compare extreme finite inputs to a 650-digit Decimal oracle. A result
outside float64 range can still overflow, and undefined nonfinite operands
propagate NaN. The blend parameter and contour levels are field units, not
Euclidean distances; rescaling operands changes blending geometry.

## Contour contract

`sample_field_contours` accepts resolution 24..192, finite ordered bounds with
finite extents, and 1..16 finite levels. A scalar or broadcastable sampled field
fills the square grid. `contours_from_grid` accepts row-major flat or square
finite grids and resolution 1..192 for reusable small-grid fixtures.

The fixed diagonal and original triangle order remain deterministic. Vectorized
triangle selection skips cells without crossings before Python edge stitching.
Exact-level vertices are outside; shared zero-edge segments are deduplicated.
Only connected components whose vertices all have degree two can form a closed
cycle. Open/clipped, branched/touching or numerically zero-area components are
omitted and counted once per component. The browser mirror follows this policy.
This changes omission counts for ambiguous inputs previously split into arbitrary
fragments; it avoids inventing a connection at a touching vertex.

Area checks use centered normalized representable output coordinates and a relative rounding
bound. Tiny world scales and large translations therefore retain representable
loops. World coordinates still have float64 resolution: no sampler can recover
distinct coordinates already rounded to the same floating-point value. The
sampler omits loops that collapse to zero area during world-coordinate mapping.
The results describe the sampled piecewise-linear triangulation, not exact topology,
smoothness, continuity or holes of an unsampled continuous field.

## Reproducible measurements

Run `python benchmarks/implicit_backend.py --output backend-timing.json` from
the checkout. It warms each fixture once, then records five sequential wall-clock
samples without a speed assertion. Grid jobs exclude field sampling and include
validation, selection and stitching. The retained [before](benchmarks/implicit-0.12.0-before.json)
and [after](benchmarks/implicit-0.12.0-after.json) records contain all samples,
versions, fixture hash and output signatures. Work17, Python 3.11.14, NumPy 2.4.6:

| Fixture | 0.11.1 median | 0.12.0 median |
| --- | ---: | ---: |
| Ellipse, grid 192, 16 levels | 439.13 ms | 106.45 ms |
| Static blend, grid 128, 12 levels | 151.24 ms | 44.64 ms |
| Symbolic evaluation, 193 squared | 0.226 ms | 0.211 ms |
| Smooth blend evaluation, 193 squared | 0.106 ms | 0.536 ms |

Both grid output signatures match their baselines. These fixtures show roughly
4.13x and 3.39x faster extraction on this host. Stable smooth evaluation costs
more than the unsafe formula (about 5.0x here); symbolic timing is close to timer
and system noise. These are host-specific measurements, not renderer/FPS,
memory, cold-start or universal performance guarantees.

## Verification and remaining work

The baseline new regressions reproduced 24 failures out of 30 cases before
implementation. Expanded tests cover broadcast/empty/domain contracts, analytic
normals, independent high-precision blend values and weights, holes, scale and
translation, exact touching vertices, shared zero edges, extreme interpolation,
input immutability and Python/browser agreement.

Generic `RFunctionCurve.bounding_box()` remains a heuristic for arbitrary smooth
fields and can underestimate exterior expansion. Provide explicit sampling
bounds; specialized `StaticBlendField` retains its conservative bounds. Adaptive
procedural derivatives, generic level-set wrappers, distance-field strategies
and cache redesign need separate contracts and are outside this milestone.
Native WebMCP host verification remains pending.
