# Native signed-distance gradient contract

Version 0.21.0 changes `SignedDistanceField.gradient` for native closed straight
endpoint chains. It differentiates the geometric signed distance determined by
the actual binary64 input coordinates, rather than the quantized float output
of `evaluate`. Unique nearest projections produce outward signed unit gradients.
Several segments meeting at the same nearest endpoint share one projection and
remain differentiable away from the boundary. Distinct equally nearest points
produce two NaNs, including true medial-axis points. Genuine noncollinear
boundary corners, crossings and inactive/cancelled boundaries also produce two
NaNs. Smooth straight boundaries and collinear joins use local side membership
to determine their outward normal; holes use outer-minus-union-of-holes signs.

The prior `resolution / 10` step returned `(0, -0.0001)` at the smooth point
`(2e-6, 1e-6)` in a square of side `4e-6`, and `(0, 0)` at the equivalent point
in a square of side `4e200`; both now return `(0, -1)`. The old square center and
corner produced finite vectors despite undefined derivatives; both now produce
two NaNs. An exterior corner's radial unit gradient remains valid. Resolution
still serializes with the field but no longer sets the native geometric step.

## Arithmetic and compatibility limits

The existing robust segment-distance kernel screens nearest features. A 64-eps
relative guard with a four-ULP floor sends close, rounded-zero and infinite
magnitudes to exact rational squared-distance and projection comparisons.
Projected axis distances use exact subtraction high/low parts inside the normal
arithmetic envelope. Ordinary proved projections use floating unit normals;
uncertain/extreme projections normalize exact residuals before conversion, with
a rare Decimal guard for tiny unit components. A rounded zero magnitude does
not imply a boundary point, and an overflowing magnitude can still have a
defined unit gradient. These guards do not establish universal correct rounding.

General straight boundary normals use exact incident-feature checks and rational
side probes bounded by all other normal-line intersections. Fully rectilinear
chains use exact infinitesimal strict/non-strict comparisons with the same
incidence and tangent-ray checks. Duplicate distance segments are reduced while
membership retains each original traversal. Geometry and query storage are
local to the call; repeated boundary normals are memoized only within that query.
No query arrays or persistent geometry cache are retained. Captured endpoint
chains drive sign and gradient together; simultaneous external geometry edits
have no atomicity guarantee.

Native field, region and boundary method overrides, custom callbacks and sampled
curves retain the existing four-evaluation central difference at `resolution / 10`.
Callback calling conventions and internal errors are preserved. Those paths
remain numerical approximations without a validity certificate. Existing
`SignedDistanceField.level_set` procedural normals also retain numerical
differentiation. This change does not prove polygon topology, equate sampled
chords to curved sources, or repair existing constructor scale limitations.

## Independent evidence and complete-call costs

The focused suite has 436 cases, including 81 new cases: tiny/huge/subnormal and
translated scales, holes/overlaps, corners and medial axes, next-representable
neighbors, shared endpoints, collinear joins, live edits, empty/broadcast inputs,
overflowing magnitudes, rounded-zero exact distances, oblique analytic normals,
high-precision half-subnormal normalization, callback overrides and curved
fallback compatibility. Read-only independent review checked 140 oblique signed
normals against exact projection/high-precision unit oracles, then 752 boundary
comparisons against the rational proof and 300 axis comparisons against Fraction
distances. These finite fixtures establish regression evidence, not a theorem
about every geometry.

Sequential warm full-call gradient medians on Work17 Python 3.11.14/NumPy 2.4.6:

| Geometry/grid | 0.20.0 ms | 0.21.0 ms |
|---|---:|---:|
| rectangle 97x97 | 2.434 | 11.464 |
| rectangle 257x257 | 27.539 | 23.938 |
| hole 97x97 | 4.306 | 21.608 |
| hole 257x257 | 61.903 | 40.139 |
| circle 97x97 | 242.368 | 301.837 |
| circle 257x257 | 1246.127 | 1372.739 |

| 64-query edge workload | 0.20.0 ms | 0.21.0 ms |
|---|---:|---:|
| exact_medial_ties_64 | 3.635 | 3.879 |
| near_medial_ties_64 | 9.270 | 3.047 |
| boundary_normals_64 | 2.711 | 2.311 |
| huge_smooth_64 | 3.308 | 1.365 |

Raw batches and ranges: [0.20 baseline](distance_gradient_0.20.0_work17.json),
[0.21 corrected](distance_gradient_0.21.0_work17.json). The 97x97 grids land on
exact rectangle boundaries; 257x257 grids do not. Correct nearest-feature and
boundary decisions have measurable small-grid/scalar overhead; dense grids can
avoid four repeated distance evaluations. Sampled-circle gradients use unchanged
fallback code, so their timing differences reflect workstation/batch variation,
not a new curved-gradient optimization. No measured workload retains queries.
Unit/mask diagnostics do not certify derivatives. Shared-workstation medians
are not universal throughput, latency or FPS guarantees.
