# Algebraic field derivatives (0.16.0)

`BlendedField` now uses child derivatives for every native algebraic operation.
Previously divide/min/max computed child gradients, discarded them and sampled
the entire composition four more times with a fixed `1e-6` displacement. For
`(x-1e12+2)/(y+3)` at `(1e12,1)`, that displacement rounded away in x: the old
derivative was `(0,-0.1249999999897)` rather than the independent analytic
`(0.25,-0.125)`. The new result matches the analytic pair.

## Contracts

- Quotients fold left. Derivative terms are combined using binary exponent
  scaling for extreme magnitudes, avoiding a squared denominator and overflowing
  intermediate products/ratios. A conservatively bounded ordinary-magnitude path
  avoids exponent work. Regression scales extend from `1e-300` to `1e300`,
  including a value that underflows while its derivative remains representable.
- Zero denominators retain the legacy zero-filled value policy. Both derivative
  components are NaN there, including after a later division. The legacy scalar
  zero-denominator early return remains; arrays continue their elementwise fold.
- Min/max use the exact winning child derivative. Tied winning children must
  have identical finite gradient components; otherwise both components are NaN.
  A strict winner ignores inactive undefined derivatives. Globally inactive
  children are not differentiated; a child winning some array points is evaluated
  on the full coordinate batch and its invalid entries are masked afterwards.
- Finite valid scalar, zero-dimensional, list, broadcast-grid and empty-array
  shapes agree. Scalar min/max retain Python's legacy NaN ordering; array min/max
  retain NumPy propagation. Domain exceptions from callbacks still propagate.
- Values/gradients reuse native graph nodes by identity within a single query.
  No result or expression snapshot persists between queries. Existing native
  symbolic kernels retain their expression/variable invalidation. Child,
  operation and method edits remain visible. Native cycles, including generated
  contour edges, raise `ValueError`. Evaluation callbacks are assumed pointwise
  and free of observable side effects; identity reuse changes callback counts.
- Custom evaluation/gradient overrides remain callable. A custom value-only
  `BlendedField` keeps its existing numerical fallback; this change does not
  certify arbitrary overrides or remove every numerical derivative in the engine.

Blended contours keep child derivatives rather than resampling the whole field.
Their internal procedural wrapper retains honest placeholder serialization.
Known native procedural heuristic errors propagate by absolute chain-rule
weights, including existing level shifts and nested blended contours. Unresolved
children are masked; final normals reject directions no larger than propagated
uncertainty. A smooth stationary child can still contribute a valid zero
derivative to a regular composition. No new public field or compiled API is added.

## Evidence and limits

Run `python -m pytest tests/test_field_algebra.py tests/test_base_field.py` and
`python benchmarks/field_algebra.py --output algebra.json`. The independent
oracles use symbolic differentiation and closed-form derivatives, covering
translations, extreme rescaling, singular domains, ties, mutable shared graphs,
custom overrides and procedural cusp/quantization guards.

[Raw Work17 measurements](field_algebra_work17.json) use a 97×97 grid and seven
warm batches of 30 queries; compilation is excluded. Compared with the previous
fixed-stencil path, direct cheap polynomial grids cost approximately 2.06× for
division, 1.20× for minimum and 1.10× for maximum. Leaf evaluations fall from
eight to two; a globally inactive min/max leaf also avoids its derivative.
The affine blended contour replaces 34 leaf evaluations with two evaluations
and two gradients. Shared `p=a*b; p+p+a` queries call each leaf value/gradient once.
Timings are measurements on this machine, not universal speed guarantees.

Float64 values can overflow, underflow or lose cancellation accuracy, and a
child's own derivative may already be inaccurate. Binary scaling does not
recover rounded-away information or make every algebraic expression stable.
Heuristic procedural errors remain sampled estimates, not differentiability or
accuracy certificates; the previously documented hidden-feature counterexample
still applies. No symbolic flattening crosses custom evaluator boundaries.

Next useful work includes denominator-sensitive domain-aware procedural sampling
and error diagnostics for distance/occupancy fields, which retain numerical
derivatives. Arbitrary smooth-field bounds remain unknown where no proof exists.
