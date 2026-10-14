# Signed-distance query freshness

The subsequent [0.19.0 numerical milestone](distance_numerics.md) fixes the
short-edge and squared-overflow reproductions recorded at the end of this page.
The [0.20.0 milestone](distance_sign_performance.md) adds strict native endpoint
signs and guarded ordinary-query performance; this page records the 0.18 state.

Version 0.18.0 repairs stale signed-distance values and the corresponding generic
polygon sign dependency. It retains the existing distance strategy, schema and
level-set wrapper; it does not reinterpret arbitrary implicit values as distance.

## Reproduction and cause

For the `[0,4]` square, changing a cached grid point from `(1,2)` to `(-1,2)`
previously returned `-1` instead of the analytic `+1`. A new same-shape array could
fail identically: the key compared only a few coordinates with `np.isclose`,
including its default relative tolerance. Array identity skipped even those checks.
The cache borrowed coordinates and returned its stored result directly, so a
caller could overwrite future answers by editing that result. It also preceded
invalid-coordinate handling. At `(1e6,2)` close finite-difference probes collided
and the vector gradient became `(0,0)` instead of `(1,0)`.

A separate SDF chord cache ignored region and boundary edits. Replacing `[0,4]`
with `[10,14]` left a scalar distance at `+1` instead of `+9`. Even clearing the
SDF caches did not repair a generic composite's vector sign after segment edits:
its cached containment polygon could still produce `-9` while scalars gave `+9`.
These are independent analytic box-distance comparisons, not cache-identity tests.

## Bounded correction and compatibility

SDF queries retain no coordinate, result or boundary-sample cache across calls.
They read current inputs and prepare current outer and hole boundary chords.
Generic composite polygon extraction also reads current segments/endpoints.
Native straight edges use their endpoints directly instead of 100 redundant
collinear samples. Returned arrays/lists are fresh; `clear_cache()` remains a
compatible no-op hook and the old private cache slots remain `None`. Existing
query-local field-algebra reuse remains available within a single query.

Hole boundaries were previously omitted from unsigned distance, despite their
contribution to sign. A `[2,4]` square hole in `[0,6]` now gives `+1` at `(3,3)`
instead of `+3`, and its nearest edges/corners contribute from either side.
Known unavailable boundaries raise `ValueError` instead of fabricating distance
`1`. This is an intentional invalid-geometry behavior change.

Scalar callbacks continue receiving floats. Lists, broadcast arrays, zero-dimensional
arrays, higher-dimensional and empty arrays use the shared numeric shape contract.
Nonfinite coordinates yield NaN at those points; finite points still evaluate.
Both numerical gradient probes and existing level wrappers read live state.
The schema, sign convention (negative inside, positive outside) and existing
gradient step remain compatible.

## Independent evidence and measured cost

Run `python -m pytest tests/test_distance_cache.py` and
`python benchmarks/distance_cache.py --output distance.json`. To compare the
complete previous implementation, use `--repository` with a clean checkout of
`c45000e18e263aa9e1013982577ccf1de45cf7cc`. The benchmark runs full queries over
97x97 and 257x257 grids for factory/generic rectangles, circles and a hole,
including repeated/copy/edited grids, explicit cache clearing, gradients and
scalars. Five warm batches exclude compilation. Old cache hits can be incorrect.

[Sequential Work17 baseline](distance_baseline_work17.json) and
[current measurements](distance_current_work17.json) show the tradeoff:

| Workload, 97x97 | Old repeated cache hit | Old cleared SDF cache | Current repeated query |
|---|---:|---:|---:|
| Factory rectangle | 0.00084 ms | 0.231 ms | 0.217 ms |
| Generic rectangle | 0.00086 ms | 41.9 ms | 1.38 ms |
| Sampled circle | 0.00250 ms | 14.6 ms | 11.5 ms |
| Rectangle with hole | 0.00224 ms | 1.01 ms (hole omitted) | 4.56 ms |

Safe repeated evaluation costs more than an unsafe cache hit. Straight-edge
polygon preparation greatly reduces measured generic recomputation cost; hole
work increases because all boundaries now contribute. At 257x257, current
factory/generic/circle/hole queries measure approximately 2.46/11.3/74.4/29.5 ms.
Scalar circle queries increase from about 1.43 to 2.42 ms. No hashing or immutable
snapshot cache is introduced without evidence of a net benefit.

After ten 257x257 queries, weak references show **zero retained query arrays**,
versus three arrays in the old field cache (roughly 1.59 MB of grid/result storage).
Traced current peak allocation is about 6.05 MB, versus 6.47 MB old. Tracemalloc
does not certify every native allocation. Working memory depends on current
points and sampled segments, rather than query history; this is not a new spatial
index or application FPS claim.

## Distance and remaining limits

Within supported finite arithmetic, straight segments use Euclidean projection.
Curved sources retain existing sampled-chord approximations: circle fixtures use
the independent `hypot(x,y)-radius` oracle with an explicit 0.01 error budget,
not a claim of uniform-angle samples or exact Euclidean offsets. Generic implicit
levels and Boolean field blends are not automatically signed distance.

This corrects SDF and generic polygon cache lifetime, not every mutable source
representation. Factory bounds/vertices/half-spaces must remain coherent with
edges; conic coefficients, closure caches and arbitrary stateful callbacks remain
separate oracles. Sampling can miss unavailable portions or yield inaccurate
chords. Concurrent source edits are not an atomic scene snapshot. Nondifferentiable
medial axes, finite-difference uncertainty and resolution-controlled gradient
validity remain separate work.

The [next concrete numerical reproduction](distance_next_numerics.json) records
two untouched gaps: a `4e-6` square gives `-2.236e-6` at `(2e-6,1e-6)` instead of
`-1e-6` because the absolute short-segment cutoff treats an edge as its start
point; querying `(1e200,2)` gives infinity instead of finite `1e200` because the
kernel squares large distances. Scale-stable segment distance is the next bounded
geometry opportunity.
