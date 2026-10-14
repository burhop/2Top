# Procedural derivative contracts: 0.13.0

`ProceduralCurve.gradient()` retains its scalar/broadcast array interface. Its
default no longer uses a universal `1e-8` step: that step can round away at large
coordinates or skip an entire small feature. No new dependencies are required.

## Analytic callbacks and local scales

```python
curve = ProceduralCurve(
    lambda x, y: np.sin(x / 1e-9) + y,
    gradient_function=lambda x, y: (np.cos(x / 1e-9) / 1e-9, 1),
)
numeric = ProceduralCurve(
    lambda x, y: np.sin(x / 1e-9) + y,
    derivative_scale=(1e-9, 1),
)
```

These options are keyword-only. An analytic callback must return two real
components, scalar or broadcastable to the coordinates. Scalar-only math and
branching callbacks retain a vectorized fallback; invalid output types/shapes
fail explicitly. The callback is trusted mathematical information, not checked
against numerical differentiation, and computing its gradient does not probe
the field. Normals still require a finite field and finite nonzero gradient.

`derivative_scale` is a positive finite scalar or pair of local coordinate scales.
It is independent of field amplitude and means the spatial scale over which the
function changes smoothly. The default uses `max(1, abs(coordinate))` separately
per axis. A large unrelated coordinate cannot enlarge the other axis's stencil.
Supply a local scale for translated small features or high-frequency functions.
Large constant field offsets may hide changes smaller than one output ULP;
enlarging a valid smooth stencil or providing analytic derivatives can help.

Serialization retains the scale but honestly leaves both function and gradient
callbacks as unavailable placeholders. It cannot serialize arbitrary Python code.
Existing subclasses that supply their own gradients retain that normal path.

## Numerical diagnostics

`gradient_diagnostics(x, y)` returns `gradient`, `method`, `error_estimate` and
`steps`. The numerical method is `central_richardson`. Each axis records coarse
and fine `(positive_displacement, negative_displacement)` pairs, with the same
scalar/array shape as its output. Analytic callbacks return method `analytic`
and `None` for uncertainty/steps, rather than claiming a zero error bound.

The numerical path samples the center and actual representable coordinates at
two central steps. Nonuniform three-point slopes cancel the quadratic term;
Richardson correction uses the actual displacement ratio rather than assumed
`2h`. The nominal coarse step is `eps**(1/5) * scale`. A rounded-away perturbation
uses an adjacent float. Refinement that repeats the same stencil reports infinite
uncertainty. Nonfinite/domain-limited stencils are unresolved; this milestone
does not introduce a one-sided derivative or infer an unknown domain.

Uncertainty combines the coarse/fine correction with a roundoff heuristic,
including the minimum subnormal output spacing. Numerical normals reject a
direction dominated by that uncertainty, while retaining cusp rejection and
positive field-rescaling behavior where the samples remain resolvable.

These are estimates, not certified error bounds or differentiability proofs.
Aliasing, nonsmooth functions, noise, incorrect scale hints, callback mistakes
and rounded input/output values can defeat finite sampling. No general black-box
algorithm can discover every hidden oscillation or restore lost float precision.
Field derivatives and contour levels remain distinct from Euclidean distance
offsets.

## Reproduction and measured accuracy

Run `python benchmarks/procedural_accuracy.py --output accuracy.json` on current
dev. The retained [0.12 baseline](benchmarks/procedural-0.13.0-before.json) and
[0.13 results](benchmarks/procedural-0.13.0-after.json) use the same ten analytic
functions/points. The new API supplies explicit local scales where recorded;
the baseline constructor has no such option. Absolute and normalized errors,
expected derivatives, coordinates and scale choices are all retained.

Examples on Work17, NumPy 2.4.6: the large-coordinate linear fixtures move from
zero derivatives to normalized errors around `2e-13` with explicit scales;
the translated sines and tiny-scale sine improve to around `1e-13`. These are
fixture results, not universal accuracy guarantees. A numerical gradient now
uses nine field evaluations instead of four; analytic callbacks use one gradient
invocation and no field probes. No general speed improvement is claimed.

The same script also records five warm timings on a 97-squared sine/quadratic
grid. Work17 medians were 0.146 ms for the old numerical gradient, 1.055 ms for
the corrected numerical gradient, and 0.030 ms with the analytic callback.
Ordinary gradient calls skip constructing unused uncertainty arrays, but the
more robust stencils still cost about 7.25x on this simple fixture. These are
host/fixture timings, not application FPS or universal ratios.
