# Geometric SDF signs and guarded endpoint performance

Version 0.20.0 fixes the tiny-hole sign defect and reduces the material 0.19
sampled-curve cost while preserving that version's robust arithmetic.

## Sign and boundary contract

For native straight boundaries with finite endpoint pairs, SDF membership is
odd/even membership of the live, exactly closed, ordered endpoint chain. The
outer interior minus each hole interior has negative distance; exterior/hole
interiors have positive distance. The magnitude is the minimum distance to all
outer/hole edges. Exactly zero computed distance returns canonical positive
zero, including edge interiors and vertices. No source expression tolerance or
trim plotting padding expands the sign band or makes a nonzero magnitude zero.

The `[0,6e-6]` square with a `[2e-6,4e-6]` hole now gives `-5e-7` at
`(1.5e-6,3e-6)` under the default region policy. Its public `contains` still
returns false there: that API deliberately retains its existing fuzzy tolerance
semantics. Generic and concave endpoint extensions accepted by trim padding
now have positive SDF values. Public tolerance defaults and explicit arguments,
region precision objects, serialization and non-SDF field behavior are unchanged.

Half-open ray crossings ignore horizontal edges. Ordinary interpolation uses a
conservative roundoff guard; overflowing differences, erased/subnormal ratios
or terms and near-boundary comparisons use exact `Fraction.from_float`
crossings. These compare the actual binary64 coordinates, including translated
ones. Reversal does not change membership. Native endpoint chains with exact
gaps now raise `ValueError` in the SDF path, even if fuzzy public closure accepts
them. This requirement is intentionally stricter than public containment.

Curved boundaries use their source `contains` with explicit zero tolerance;
their magnitude still uses the existing 50-point chord approximation. A smooth
source boundary is not necessarily zero distance to those chords, and source
membership can disagree with chord geometry. No exact curved SDF or topology
certificate is claimed. Native region/boundary containment overrides remain
authoritative. Region callbacks accepting `tolerance` receive zero; existing
two-argument and uninspectable callbacks retain their calling conventions.
Internal callback errors propagate without retry. Callback correctness remains
the callback author's responsibility.

## Performance path and arithmetic limits

Axis-aligned edges retain direct clamping/hypot. An oblique edge can settle an
ordinary query at endpoint A or B without compensated determinant arithmetic
only when every nonzero endpoint/query coordinate is within `[2^-200,2^200]`.
Within this envelope representable nonzero subtraction differences and products
stay normal and finite. A's projection must be below minus
`64*eps*(abs(dot_x)+abs(dot_y))`; B's projection-minus-squared-norm must exceed
`64*eps*(abs(dot_x)+abs(dot_y)+length_sq)`. These conservative absolute guards
bound the rounded subtractions, products, sums and B comparison. Endpoint
distance uses hypot. The limits restrict this optimization, not accepted input.

Every interior, uncertain or extreme query delegates to the unchanged 0.19
robust kernel: separately scaled differences, compensated determinant and
bounded Decimal fallback (`80 + 2*exponent spread`, capped at 1600 digits).
All existing exact-rational/high-precision, tiny/huge/subnormal, cancellation,
endpoint reversal and half-subnormal tie regressions remain. There is no new
cache, retained query buffer, dependency or source-curve shortcut. Memory stays
query-local and linear in the number of points per segment.

For more than eight segments and at least 32 query points, an additional
query-local reduction computes point-to-segment-box lower bounds. Within the
same ordinary coordinate envelope, a segment is skipped only when its box
distance exceeds the current minimum inflated by `1 + 64*eps`. A segment lies
inside its box, and the margin bounds normal subtraction/hypot rounding.
Near ties, zero bounds, unavailable minima and points/edges outside the envelope
use the full kernel. Every endpoint pair is validated even if its segment is
skipped. Small workloads avoid this extra bounding cost. Samples and nearest
hole contributions are unchanged; the reduction introduces no cache or source
geometry approximation. Exact-rational minimum regressions cover reversed,
translated, ordinary/extreme and adjacent-point cases across these paths.

## Independent correctness evidence

`tests/test_distance_sign.py` covers default-policy tiny/ordinary/large squares
and holes, exact edges/vertices and adjacent representable neighbors, translated
coordinates, concavity/reversal, multiple holes, generic endpoint extensions,
positive rescalings of circle expressions, unchanged containment behavior,
live mutation, broadcast/zero-dimensional/scalar forms and callback contracts.
Exact rational ray crossings cover overflowing differences, ratio underflow,
near-line neighbors and huge translated coordinates.

`tests/test_distance_numerics.py` retains the 135 previous cases and adds 47
guard/envelope/minimum fixtures, each with several endpoint/interior/neighbor queries
compared to independent exact rational projection plus a 1500-digit square root.
Normal values use at most `8e-15` relative tolerance; the prior named exact
zero/subnormal/infinite assertions remain exact. Independent read-only review
also checked 220 mixed-exponent triangles, 1,200 projection constructions and
150 ordinary distance/reversal cases against exact/robust oracles. Aggregate local and CI evidence is recorded
in the verification page and milestone PR.

## Work17 measurements

Run the same script against each preserved checkout, sequentially, using the
same Python/NumPy environment:

```powershell
python benchmarks/distance_sign_performance.py --repository PATH --label VERSION --output timings.json
```

Five warm evaluation/edge batches and three gradient/scalar batches use one
complete call each. Full sampled-circle evaluations include source sign,
50-point boundary sampling, segment kernels and reduction; gradients invoke
four complete field evaluations. Raw arrays retain every batch and environment.
Medians below are milliseconds on Work17 Python 3.11.14/NumPy 2.4.6:

| Complete workload | 0.18.0 | 0.19.0 | 0.20.0 |
|---|---:|---:|---:|
| rectangle 97x97, evaluate | 0.407 | 0.799 | 0.507 |
| rectangle 257x257, evaluate | 4.832 | 7.959 | 5.339 |
| hole 97x97, evaluate | 5.121 | 1.150 | 0.878 |
| hole 257x257, evaluate | 24.204 | 13.989 | 9.128 |
| circle 97x97, evaluate | 16.377 | 46.110 | 19.621 |
| circle 257x257, evaluate | 136.455 | 936.417 | 100.856 |
| circle 97x97, gradient | 85.799 | 480.158 | 78.174 |
| circle 257x257, gradient | 521.826 | 3734.171 | 799.173 |
| circle 97x97, scalar | 2.584 | 25.938 | 2.980 |
| circle 257x257, scalar | 3.474 | 21.401 | 11.898 |
| overflow_64 | 0.054 | 41.450 | 41.410 |
| collinear_64 | 0.051 | 1.869 | 1.801 |
| near_line_64 | 0.051 | 0.501 | 0.598 |
| endpoint_257 | 1.045 | 20.290 | 4.207 |

Raw evidence: [0.18](distance_sign_performance_0.18.0_work17.json),
[0.19](distance_sign_performance_0.19.0_work17.json),
[0.20](distance_sign_performance_0.20.0_work17.json).
The two circle evaluations improve about 2.35x and 9.28x versus 0.19.
Against 0.18, 97x97 remains about 20% slower and 257x257 is about 26% faster.
Gradient costs improve versus 0.19 but the 257x257 gradient remains about 53%
slower than 0.18; scalar and small/fallback workloads are not universally faster.
The old overflow workload returns unavailable results and is not a correct
alternative to precision fallback. No tested workload retains query arrays.
Small batches vary on a shared workstation, visibly including scalar calls
that are geometrically identical across the two grid rows. These are measured
medians with raw ranges, not a guaranteed throughput, latency or FPS budget.

## Remaining limits and next opportunity

The fixed-step SDF numerical gradient still crosses corners, medial axes and
small features and does not carry a derivative validity certificate. Curved
sampling has no adaptive distance-error bound. Existing polygon construction
can reject extremely tiny areas or overflow legacy closure checks at huge
scales; this change does not redefine constructor validity. Exact endpoint
membership remains odd/even rather than a self-intersection/topology validator.
Nonfinite query points stay NaN; invalid endpoint geometry raises. Binary64
distances can legitimately overflow their representable range. Native WebMCP
host verification remains a separate unverified capability.

A concrete next geometry task is a bounded validity contract for the existing
SDF numerical derivative at corners/medial axes and features smaller than its
fixed step. Any such work needs its own oracle and scope; this milestone does
not imply authorization for unrelated geometry or host changes.
