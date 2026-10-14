# Signed-distance gradient diagnostics

Version 0.22.0 extends the existing `gradient_diagnostics(x, y)` protocol to
`SignedDistanceField`. It is opt-in: existing `gradient()` behavior, saved
resolution/schema, composition derivatives and procedural level-set normals
retain their current contract, except that native dispatch now respects an
authoritative `_evaluate_vectorized` override.

## Reproduced problem and derivative target

At a smooth unit-circle source point `(0.9981243961, 0.06121837872)`, the current
sampled magnitude is about `0.001875603892`. Source containment changes sign
across the circle while that chord magnitude remains nonzero: `evaluate()` has
a jump. With resolution `1e-6`, legacy gradient returns approximately
`(18756.04, 18756.04)`, although the analytic source-circle normal is the point
itself. The diagnostic estimator cannot resolve that evaluated discontinuity
and returns two NaNs, infinite heuristic errors and budget-exhausted statuses.
It does not replace the field with an exact circle signed distance.

For an overridden analytic circle-distance callback of radius `1e-6`, the
legacy default step returns components below `0.001` at `(1.6e-6, 1.2e-6)`.
Adaptive diagnostics recover `(0.8, 0.6)` within the tested tolerance. At
`(2e-6, 0)`, x resolves but the smooth zero y derivative remains unresolved
within the fixed budget, so the returned diagnostic vector has two NaNs.
At the true callback-circle medial center, zero central differences do not
establish a normal; the diagnostic vector is unavailable.

Outside the sampled circle near an interior chord projection, diagnostics can
consistently recover a chord normal that differs from the source-circle radial
normal. `derivative_target="evaluate"` explicitly identifies this evaluated
hybrid field. `distance_model="boundary_magnitude_and_containment_sign"` means
straight or sampled boundary magnitudes combined with authoritative source or
callback containment; `custom_evaluation` identifies overridden field methods.
No sampled-polyline derivative is represented as a source-curve derivative.

## Return contract and compatibility

- `gradient`: two components. Numerical vectors have two NaNs if any component
  is unresolved/nonfinite or a coordinate is nonfinite; `raw_gradient` retains
  the candidate for investigation, even when it is explosive or misleading.
- `available`: one bool per point; finite errors and candidates mean sampled
  consistency only. `certified` is false, including supplied gradients and the
  native route: no universal accuracy/rounding certificate is advertised.
- Numerical `status`, `error_estimate`, actual `steps`, `nominal_step`,
  `selection`, `candidates` and `field_evaluations` reuse the unchanged adaptive
  estimator. Error estimates are heuristic; unresolved errors are infinite.
- Native straight geometry delegates to the 0.21 nearest-feature gradient and
  retains corner/medial unavailable masks. It reports `nearest_feature`,
  `native_endpoint_distance` and no fabricated numerical error estimate.
- A supplied gradient override is authoritative, including super delegation.
  Its internal evaluation count and error are unknown (`None`). A finite supplied
  vector is not independently validated by these diagnostics.

Numerical diagnostics make at most 321 vector `evaluate` calls, not 321 calls per
point. Scalar callbacks receive Python floats; NumPy 0d and broadcast shapes are
preserved. Callback exceptions propagate without retries or vectorization.
The full array shape is probed to preserve callback semantics, including already
resolved points. All-nonfinite numerical queries can still spend 161 evaluations
before masking; user callbacks may perform unbounded internal work.
Results and geometry remain query-local with no retained input buffers/cache.

Finite sampling cannot rule out hidden features, aliasing, noise or domain
boundaries between probes. Flat sample statuses do not prove a zero derivative.
Near-medial decimal coordinates need not lie exactly on the intended radius;
rounded callback values may look flat differently across platforms and escape
detection. The annulus medial regression uses the exact binary64 point
`(0.75, 0)` on radius `0.75` and keeps the unavailable-vector assertion.
Smooth points can remain unresolved; this bounded pass adds no scale/domain
solver, source closest-point solver or exact curved-distance claim. Legacy
`gradient()`, algebra and level-set normal consumers do not automatically use
the opt-in diagnostic vector. Those integrations remain explicit future work.

## Evidence and complete-call costs

The affected suite has 504 tests, including 32 new cases. Analytic callback
circles at scales `1e-6`, `1` and `1e6`, annulus smooth/medial radii, square-root
domain/derivative boundaries and the distinct circle/chord normal cover numerical
behavior. Contract cases cover scalar, NumPy 0d, broadcast, empty and nonfinite
inputs; constant/wrong-shaped outputs; provided gradients; custom containment;
vectorized overrides; internal errors and defensive outputs.

Sequential warm complete-call medians on Work17 Python 3.11.14/NumPy 2.4.6:

| Workload | 0.21 gradient ms | 0.22 gradient ms | Opt-in diagnostics ms | Evaluate calls | Available vectors |
|---|---:|---:|---:|---:|---:|
| sampled_source_boundary | 13.088 | 11.206 | 1720.463 | 161 | 0/1 |
| sampled_smooth_chord | 12.944 | 50.023 | 221.589 | 17 | 1/1 |
| sampled_17x17 | 47.921 | 122.676 | 5571.328 | 125 | 284/289 |
| tiny_circle_callback | 0.018 | 0.056 | 11.009 | 89 | 1/1 |
| circle_medial_callback | 0.018 | 0.113 | 22.173 | 161 | 0/1 |
| affine_callback_64 | 0.030 | 0.157 | 3.441 | 17 | 64/64 |
| nonfinite_callback_64 | 0.025 | 0.097 | 21.775 | 161 | 0/64 |

Raw batches/ranges: [0.21 baseline](distance_gradient_diagnostics_0.21.0_work17.json),
[0.22 current](distance_gradient_diagnostics_0.22.0_work17.json). Legacy gradients
remain cheap; diagnostics deliberately spend additional probes for uncertainty
information. Counts and availability describe these fixtures, not universal
source-gradient accuracy. Shared-workstation medians do not guarantee latency,
FPS or speedups. An affine-callback weakref probe retained no query arrays.
