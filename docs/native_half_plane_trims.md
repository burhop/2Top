# Native affine half-plane root membership

Version 0.30.0 resolves the demonstrated x+y>=0 callback limitation through an
explicit native predicate. It does not infer a certificate from arbitrary code.

```python
import sympy as sp
from geometry import HalfPlaneMask, ImplicitCurve, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections

x, y = sp.symbols("x y")
trimmed = TrimmedImplicitCurve(
    ImplicitCurve((x * x - 2) ** 4, (x, y)), HalfPlaneMask(1, 1, 0)
)
report = find_polynomial_line_intersections(trimmed, ImplicitCurve(y - x, (x, y)))
assert len(report["points"]) == 1
assert report["roots"][1]["multiplicity"] == 4
assert report["roots"][1]["root_trim_membership"] == "model_root_included"
```

The model roots are (+/-sqrt(2),+/-sqrt(2)), each multiplicity four; the positive
root belongs to x+y>=0. The native solver proves that membership, while the same
opaque callback remains unverified. The public JSON example is
`python examples/native_half_plane_demo.py`.

## Coefficients, boundaries and degeneracy

HalfPlaneMask(a,b,c=0,closed=True) means a*x+b*y+c>=0. With closed=False it means
strictly >0. Mode must be an actual boolean. Rational coefficients are exact;
Python/NumPy floats mean their stored binary values, and SymPy Float/Fraction
values retain their exact rational value. Numerator/denominator sizes are limited
to 4096 bits; SymPy Float precision/exponents are checked before exact conversion.
Nonfinite/complex/symbolic/string coefficients are rejected. Large/tiny rational
coefficients need not have a representable raw binary64 value.

Positive exact scaling preserves the predicate. Negative scaling reverses its
side; boundary equality is still included only in closed mode. If a=b=0, the
constant/mode selects all finite points or none. In particular (0,0,0) includes
all finite points when closed and none when open. Nonfinite coordinates are
always outside, including constant predicates.

## Exact sign at binary64 coordinates

The immutable native predicate retains raw coefficients. A positive exact
max-coefficient normalization supplies bounded float coefficient enclosures.
Every product and interval addition rounds outward using nextafter. Only a
strictly decisive enclosure, with the appropriate closed/open inequalities,
selects a sign. Uncertain signs, nonfinite intermediates and equality use exact
rational arithmetic on the stored coefficients and actual finite binary64
coordinates. A tiny positive term remains positive even below the subnormal
product range; cancelling 1e308 terms cannot erase a decisive tiny constant.
Normal IEEE binary64 arithmetic is assumed for the conservative float filter.

The callable supports scalar and broadcast array coordinates. Mixed batches
usually use the interval filter; boundary-heavy batches may need exact work at
every point and can be slower. No hard exact-arithmetic runtime or universal
latency guarantee is claimed. Frozen attributes plus native type/call/cache
validation prevent replacements from gaining an unearned symbolic proof.

## Root proof and independent representative checks

The polynomial/line solver substitutes the captured affine line exactly, giving
d*t+e. A zero d uses the constant and boundary mode directly. Otherwise the
existing exact isolated-root comparison decides the side of rational -e/d,
reversing the comparison for negative d. Derived slope, intercept and threshold
limits are checked; unsupported growth remains unverified, never excluded by a
numeric guess. This does not use residual size or a nearby point as a proof.

Per-wrapper root_trim_checks now includes native_half_plane, alongside rectangle
and opaque callback evidence. Nested predicates all apply. One proved exclusion
is definitive; inclusion requires every wrapper. Actual representative contains,
finite field residual and exact model position-bound checks remain independent
acceptance gates. A mathematically included boundary root can have a rounded
representative outside the predicate and remain unaccepted. Global trimmed
completeness remains conservative, with the existing untrimmed coefficient-model
scope. Degree-at-most-eight polynomial/line model limits are unchanged.

Only default trim containment and unchanged native predicates without extra
explicit wrapper bbox constraints gain native proof. Overridden methods,
subclasses, resource limits and arbitrary callbacks remain opaque. Observed
coefficient/mode/cache/mask/method/bbox edits invalidate all trim proofs and
accepted points; the existing stable-hidden-state assumption remains for
arbitrary callbacks. No proof of hostile metaprogramming is claimed.

## Serialization and evidence

The native codec preserves all three raw rational coefficient strings and the
actual boolean boundary mode, including positive/negative scaling. It never
serializes only rounded normalized coefficients. Strict bounded rational parsing,
marker/payload agreement, known-type dispatch and evaluator authority guards
retain the previous rectangle protections. Missing/malformed/unknown native
data raises; it does not become a pass-through mask. Native RectangleMask data
keeps its existing format. Arbitrary callback serialization remains explicitly
lossy under the existing contract.

94 regression cases use independent analytic, Fraction and 160-digit Decimal
oracles. These include 160 seeded extreme-cancellation signs, subnormal products,
irrational/flat contacts, open/closed equality, constant-on-line predicates,
scale/sign changes, nested masks, mutation and codec rejection. Independent
review separately passed 4,032 exact sign comparisons and 30 oblique root cases.

The next evidenced opportunity is native projection/chord masks for from_anchors.
Its current opaque callback on the chord (-2,-2)..(2,2) leaves both irrational
roots on y=x unresolved, while three equivalent nested native half-planes prove
both included. That factory also retains its existing lossy callback codec.
Integrating a bounded native chord predicate could remove the manual assembly
while explicitly preserving endpoint, side and tolerance semantics.


## Work17 measurements

The same exact inequalities are opaque callbacks in the 0.29 baseline and
declared HalfPlaneMask objects in 0.30. These are five warm calls on a shared
Work17 workstation, measured while full regression was running. They compare
the explicit API choice; no speedup or universal latency guarantee is claimed.

| Workload | 0.29 points | 0.30 points | 0.30 ms |
|---|---:|---:|---:|
| oblique_irrational_contact | 0 | 1 | 20.705 |
| closed_flat_boundary | 1 | 1 | 8.588 |
| open_flat_boundary | 0 | 0 | 12.457 |
| negative_scaled_side | 0 | 1 | 46.693 |
| constant_on_line_closed | 0 | 1 | 32.416 |
| constant_on_line_open | 0 | 0 | 33.172 |
| nested_rectangle | 0 | 1 | 36.687 |
| degenerate_all | 0 | 2 | 20.820 |
| opaque_callback | 0 | 0 | 32.030 |
| anchor_factory_chord | 0 | 0 | 24.395 |

The mixed_signs batch took **83.681 ms for 100,000 coordinates**.
The exact_boundary batch took **109.710 ms for 1,000 coordinates**.

Boundary batches intentionally exercise exact fallback. The constant-on-line
closed control proves both roots included but accepts only one representative;
its other rounded point fails actual predicate containment. Raw [baseline data](half_plane_0.29_baseline_work17.json)
and [current data](half_plane_0.30_work17.json) retain every root, proof, float
gate and timing sample. The anchor_factory_chord control retains zero accepted
points, while the independent equivalent native-conjunction regression returns
two; this is the evidence for the next bounded factory improvement.
