# Scale-robust segment distances

The subsequent [0.20.0 sign/performance milestone](distance_sign_performance.md)
replaces the default-tolerance SDF sign policy and adds guarded ordinary endpoint
and nearest-segment reduction paths. Measurements below remain the 0.19 record.

Version 0.19.0 corrects distance arithmetic inside the existing SDF strategy.
It retains query-local boundary preparation, sign policy, serialization and the
gradient/level-set APIs. Arbitrary implicit values are not Euclidean distances.

## Reproductions and correction

For a square of side `4e-6`, the distance at `(2e-6,1e-6)` was `-2.236e-6`
instead of analytic `-1e-6`: the absolute `length_sq < 1e-9` cutoff treated
nonzero edges as points. Querying `(1e200,2)` near the ordinary `[0,4]` square
returned infinity instead of finite `1e200` because the kernel squared distances.
Both recorded reproductions now match their analytic values.

Exactly identical finite endpoints define a point. Every other representable
edge remains a segment, including subnormal edges. Axis-aligned segments use
coordinate clamping and `hypot`. Oblique segments separately scale edge/query
differences by powers of two, classify projection and compute perpendicular
distance from a compensated determinant. TwoDiff and Dekker residuals retain
low parts lost in coordinate subtraction and multiplication. The start-side
classification uses the projection sign, even if its positive ratio underflows.
No huge nearest point is reconstructed and subtracted from a small query.

Observed overflowing differences, erased/subnormal components, severe
cancellation and rounded endpoint projections use a Decimal fallback. Precision
is bounded: `80 + 2 * coordinate exponent spread`, capped at 1600 decimal digits.
The doubled spread accounts for product cancellation and tiny squared-norm
corrections that can decide half-subnormal rounding ties. Exactly zero fallback
determinants avoid unnecessary square roots. This is a guarded arithmetic path,
not a universal correct-rounding or domain certificate.

Nonfinite/complex endpoint geometry raises `ValueError`; an invalid edge is not
silently omitted from the minimum. Nonfinite query coordinates retain their NaN
contract. A mathematically unrepresentable binary64 distance may legitimately
be positive infinity; overflowing intermediate arithmetic alone should not
force a representable tested result to infinity or NaN.

## Independent evidence

`tests/test_distance_numerics.py` uses exact `Fraction.from_float` coordinates,
rational projection/clamping and exact squared residuals, followed by a
1500-digit Decimal square root. This oracle differs from the production scaled
determinant algorithm. Tested normal values match within `4e-15` to `8e-15`
relative tolerance; named zero/subnormal/infinite cases require exact results.

Fixtures cover tiny/huge and short/zero-length segments, translated actual float
coordinates, endpoint reversal, severe ordinary near-line cancellation, mixed
exponents, half-subnormal ties and cancellation of large/mixed products down to
a tiny determinant. Native square/hole integrations cover scalar, array and
zero-dimensional paths. Small-hole sign fixtures explicitly configure the
existing precision policy to isolate kernel arithmetic. Independent review
also checks additional mixed/translated and structured cancellation probes.

Run `python -m pytest tests/test_distance_numerics.py` and
`python benchmarks/distance_numerics.py --output kernel.json`. Compare the
complete previous kernel using `--repository` with a clean checkout of
`52ac01d4fc502890705dea4c9a2b4417f859363d`. Full field/query memory workloads are
available through `benchmarks/distance_cache.py` with the same repository option.

## Measured cost

Five sequential warm batches on Work17 exclude compilation. Raw
[baseline kernel](distance_kernel_baseline_work17.json) and
[current kernel](distance_kernel_current_work17.json) measurements include the
complete one-segment SDF distance call:

| Workload | 0.18.0 | 0.19.0 |
|---|---:|---:|
| Axis segment, 97x97 | 0.0695 ms | 0.133 ms |
| Oblique segment, 97x97 | 0.0642 ms | 1.53 ms |
| Axis segment, 257x257 | 0.687 ms | 1.87 ms |
| Oblique segment, 257x257 | 0.694 ms | 15.5 ms |
| Collinear fallback, 64 points | 0.0138 ms | 0.676 ms |
| Near-line, 64 points | 0.0138 ms | 0.186 ms |
| Overflow fallback, 64 points | 0.0142 ms (NaN results) | 26.7 ms |

Robustness adds cost, especially for oblique and precision-heavy queries. The
overflow row deliberately stresses the fallback and is not a typical scene
workload. No speed, FPS or exact curved-distance claim follows from these data.
The fixed-precision prototype was replaced before publication after its ordinary
collinear cost was measured; the committed measurements use the final
product-spread precision formula.

The [complete field baseline](distance_field_baseline_work17.json) and
[current field workloads](distance_field_current_work17.json) include sign and
sampling, not just the segment kernel. At 97x97, factory rectangle queries cost
0.549 ms versus 0.381 ms old; sampled circles cost **126 ms versus 13.4 ms**,
and circle gradients cost **543 ms versus 62.1 ms**. At 257x257, current sampled
circle queries cost **1.39 s**, and gradients cost **5.58 s**. These are material
regressions for dense sampled-curve workloads; this correctness increment does
not promise interactive performance at those sizes. Native straight-edge and
fallback-sensitive workload costs are separated in the raw measurements.

After ten 257x257 rectangle queries, weak references show no retained query
arrays. That rectangle workload's traced peak is 6.64 MB versus 6.05 MB old;
it does not bound every curved/source/native allocation. Kernel temporary
storage scales with the current point batch, processing one segment at a time,
and fallback precision is bounded. No point-by-segment matrix or persistent
distance cache is introduced. Avoiding unnecessary compensated work for proven
endpoint projections is a concrete future performance opportunity.

## Limits and next opportunity

Curved boundaries retain sampled-chord approximations. This kernel does not
certify source samples, topology, factory/conic metadata or atomic concurrent
edits. Default region tolerance still supplies sign, and the existing fixed-step
numerical gradient remains approximate, especially near medial axes or when
coordinate spacing exceeds its step. Query buffers remain unretained; working
memory depends on the current point batch and sample count.

The [next concrete sign-policy reproduction](distance_next_sign.json) is a tiny
square with a hole. At `(1.5e-6,3e-6)`, outside the hole but inside the region,
the default `1e-4` containment band produces `+5e-7` instead of `-5e-7`.
The existing zero-tolerance policy gives the analytic sign with the same correct
magnitude. The remaining gap is sign/tolerance semantics, not segment distance.
