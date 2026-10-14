# Bounded automatic procedural steps (0.15.0)

ProceduralCurve now selects numerical steps automatically when no
`derivative_scale` or `gradient_function` is supplied. This reduces manual hints
for the measured translated and small-feature fields. It is a sample-based
heuristic with a fixed budget, not a black-box accuracy or differentiability
certificate. Explicit scalar/pair scales retain the nine-evaluation fixed path;
analytic callbacks still avoid numerical field probes.

## Selection and diagnostics

Each axis starts at `max(eps**0.2, 8*abs(spacing(coordinate)))`: a unit-scale
local stencil with a representability floor, rather than a large step caused
solely by the coordinate's translation. Coarse/fine nonuniform central slopes
use actual float displacements and Richardson correction. Candidates compare
the correction, output roundoff/subnormal spacing and derivative float spacing.
Relative selection thresholds are `1e-6` for truncation and `1e-9` for roundoff;
they are heuristics, not promised tolerances on the true derivative.

Candidates shrink by four when truncation dominates and expand by four when
roundoff dominates. Expansion stops when visible truncation overtakes roundoff,
instead of searching indefinitely for a stable nonlocal secant. Acceptance uses
coarse/fine one-sided disagreement, neighboring candidate agreement and a second
pair at `0.7*step` off the dyadic ladder. Reported uncertainty includes observed
off-ladder disagreement and its roundoff estimate. This reduces demonstrated
aliases and cusp failures; it cannot exclude every unsampled oscillation.

`gradient_diagnostics()` retains gradient/error/actual-step/method entries and
adds per-axis/per-point status, selection (`local`, `refined`, `expanded`),
candidate count and nominal selected step. `field_evaluations` counts calls to
the curve evaluator over the full broadcast shape. There are at most **20
candidates per axis and 321 vector evaluations per gradient**. Scalar-only
callback fallback may invoke the Python function once per element in each call.
Broadcast shapes and inputs are preserved; settled points retain their steps
while other points continue. Empty inputs require only the center evaluation.

| Status | Meaning |
| --- | --- |
| `sample_consistent` | The tested neighboring/off-ladder estimates met the selection checks |
| `sampled_stationary` | Tested variation is compatible with a zero derivative at this point |
| `flat_samples` | Tested values stayed flat; constancy is unproved and quantization uncertainty remains |
| `budget_exhausted` | No accepted candidate within the hard limit |
| `roundoff_limited` | Expansion reached a visible truncation/roundoff tradeoff |
| `stencil_collapsed` | Refinement no longer supplied distinct representable stencils |
| `nonfinite` | No finite candidate derivative was available |

Unresolved candidates return a finite sampled approximation where possible,
with **infinite uncertainty**. This approximation is not a trustworthy direction.
Numerical normals reject infinite uncertainty, nonfinite values and directions
dominated by uncertainty. Flat components retain finite quantization estimates
so regular affine fields such as `1+y` retain their normals; global constants
still have no normal. Neither a flat status nor a successful normal proves that
hidden features are absent.

## Limits demonstrated rather than hidden

The smooth compact-support bump in the saved fixtures has derivative `(1,1)` at
the origin, yet every sampled x neighbor lies outside its `1e-100` support. Both
old and new estimators return the wrong x derivative and can accept the wrong
normal. The new status says **flat samples**, not certified zero. No finite
unconstrained probing scheme can exclude such a function. An explicit local
scale or analytic callback resolves this known example.

The tested `1e-18` sine remains budget-limited, and subnormal output derivatives
remain precision-limited even when their returned approximation happens to match
the analytic value. Quantized output can erase a local signal before sampling.
Noise, nondeterministic callbacks, incorrect explicit scales and untested
oscillations remain limitations. Callbacks should be pure pointwise functions;
automatic mode makes more evaluations and does not reuse samples across calls.

Numpy callbacks returning nonfinite coarse neighbors can shrink toward valid
samples (the `log(x)` near-boundary fixture). Python callback exceptions,
malformed outputs and unavailable-code placeholders propagate. The method does
not infer a domain, silently swallow programmer errors, add one-sided
derivatives or recover an exact-boundary derivative that does not exist.

## Reproduction and measured cost

```bash
python -m pytest tests/test_automatic_derivatives.py tests/test_procedural_derivatives.py
python benchmarks/automatic_derivatives.py --output automatic.json
python benchmarks/automatic_derivatives.py --implementation-root ../previous-checkout --output before.json
```

Saved [0.14 baseline](benchmarks/automatic-0.15.0-before.json) and
[0.15 results](benchmarks/automatic-0.15.0-after.json) retain analytic expected
derivatives, observed values/errors, actual steps, statuses and call counts.
Translated sines at `1e9`/`1e12` improve from normalized errors around 0.955 to
around `1e-13`; sines at scales `1e-6`, `1e-9` and `1e-12` improve from errors
around one to around `1e-13` without hints. The tested dyadic alias is corrected,
while abs/sign/cube-root and differentiable-cusp directions stay unresolved.

Easy scalar fixtures use 17 evaluations instead of nine. Difficult fixtures
take more; a single difficult array point can keep the whole broadcast callback
running. On Work17, seven warm 97x97 grid medians are **4.65 ms automatic versus
1.07 ms for the previous default** (about 4.35x). Current explicit-scale and
analytic paths measure 1.07 ms and 0.033 ms. Ordinary gradients skip constructing
unused diagnostics, but adaptation still costs more computation and samples.
These are local fixture timings, not universal ratios or application FPS.

The measured accuracy/diagnostic benefit justifies a bounded default for unknown
procedural fields. Known analytic derivatives or explicit scales remain the
appropriate performance path. General algebraic-field derivatives, domain-aware
sampling and user-defined noise/locality contracts remain separate increments.
