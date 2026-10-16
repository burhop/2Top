# Native closed-rectangle root membership

Version 0.29.0 makes the polynomial/line solver useful with a declarative trim
predicate. In 0.28 every non-binary root under an arbitrary callback remains
membership-unverified, even when a simple box obviously includes it. The new
public immutable RectangleMask supplies a bounded exact predicate the solver can
reason about. Existing arbitrary callbacks keep their conservative contract.

```python
import sympy as sp
from geometry import ImplicitCurve, RectangleMask, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections

x, y = sp.symbols("x y")
trimmed = TrimmedImplicitCurve(
    ImplicitCurve((x * x - 2) ** 4, (x, y)),
    RectangleMask(0, 2, -1, 1),
)
report = find_polynomial_line_intersections(trimmed, ImplicitCurve(y, (x, y)))
assert len(report["points"]) == 1
positive = report["roots"][1]
assert positive["multiplicity"] == 4
assert positive["root_trim_membership"] == "model_root_included"
```

The analytic roots are +/-sqrt(2), each multiplicity four; only the positive
root belongs to this closed box. Its accepted float has a separate exact
L-infinity enclosure bound and actual residual/containment checks. Negative-root
exclusion is proved for the captured model, rather than guessed from a nearby
sample. `python examples/native_rectangle_trim_demo.py` prints the JSON evidence.

## Predicate and proof scope

RectangleMask(xmin,xmax,ymin,ymax) stores exact rational bounds. Python/NumPy
float values mean their stored binary values; SymPy Float precision and rational
coefficients are preserved within a 4096-bit limit. Bounds require finite nearest
binary64 conversion, correct ordering and supported scalar types. Closed
zero-width/height boxes are valid. Scalar and broadcast binary64 coordinates use
directed thresholds: the first float at/above each lower bound and last float
at/below each upper bound. Finite float comparisons therefore match the exact
rational inequalities, including 1/3, 1/10 and subnormal limits. Nonfinite
coordinates are outside. The mask is immutable through ordinary attribute edits.

The solver trusts only the unchanged native mask/cached thresholds and default
TrimmedImplicitCurve.contains, with no extra explicit wrapper bbox fields.
Overridden methods, subclasses, replacement caches and additional bbox
constraints remain opaque. Rectangle bounds map exactly to a closed interval
on the affine line; constant coordinates and negative slopes are handled
directly. Each isolated parameter root is compared with those rational bounds.
When a threshold lies inside its isolating interval, endpoint/equality tests
and a square-free exact root count decide its side. No residual, tolerance or
representative mask result is used to prove root membership. Existing input,
coefficient and interval limits remain, with 4096-bit derived thresholds. SymPy
exact operations have no hard wall-clock guarantee.

`root_trim_checks` separates each wrapper's `native_rectangle` proof from
`callback` evidence, with included/excluded/unverified status. Nonexact roots
can gain `model_root_included` or `model_root_excluded`; existing exact binary
roots retain `exact_point_accepted`/`exact_point_excluded`. Every nested wrapper
applies. One proved exclusion is decisive even if another wrapper is unresolved;
inclusion requires all wrappers. Arbitrary masks still require an exactly
representable model root and actual scalar boolean containment. Global
`trimmed_root_completeness` remains false conservatively; untrimmed model-root
completeness has its existing stored-coefficient scope.

## A root can be included while its float is unusable

Root proof never waives the independent position, finite residual or actual
representative contains gates. A zero-width box at exact x=1/3 contains that
model root but no binary64 x coordinate; membership is included, while points
stays empty with `representative_trim_not_accepted`. Likewise the rational
threshold float(sqrt(2)) lies above the exact root. A lower bound at that float
provably excludes the root even if a nearby representative is included.
Independent Fraction and 160-digit Decimal tests cover these distinctions.

Observed mask, contains, bbox or native predicate edits during callback
validation clear every accepted point and trim proof. Scalar-like numeric bbox
arrays are snapshotted by value. Deleted fields report invalidation instead of
crashing. A base model edit also invalidates untrimmed model completeness;
trim-only edits retain that unchanged model evidence. Arbitrary hidden closure
state must remain stable during the call; this is not a proof about arbitrary
mutable code or hostile metaprogramming.

## Native serialization

RectangleMask.to_dict/from_dict preserve four rational strings without symbolic
evaluation. The decoder accepts only bounded signed integers or fractions;
malformed native data raises rather than becoming a pass-through mask.
TrimmedImplicitCurve serializes this predicate in native_mask and restores it
through the normal nested curve codec. Overridden trim methods, replaced/stale
base evaluators and unsupported native evaluation chains are rejected for this
native codec. Standalone mask serialization remains available. Other mask
functions retain the existing explicit lossy reconstruction warning. Existing
base-curve serialization still governs unrelated curve-specific data.

The [polynomial/line model limits](polynomial_line_intersections.md) still apply.
The general numerical finder and default geometry behavior are unchanged. The
next supported-predicate opportunity is native affine half-planes for oblique
cuts, which arbitrary callbacks still leave unresolved at irrational roots.


## Work17 measurements

The same stated boxes are explicit opaque rational predicates in the0.28baseline
and native RectangleMask objects in0.29. This measures the declared API choice;
it does not infer a proof from an arbitrary callback. Each timing is the median
of five warm complete calls, with no cross-machine or latency guarantee.

| Workload | 0.28 points | 0.29 points | 0.29 ms |
|---|---:|---:|---:|
| irrational_flat_contact | 0 | 1 | 16.379 |
| nonbinary_rational | 0 | 1 | 4.321 |
| exact_closed_endpoint | 1 | 1 | 6.000 |
| sqrt2_threshold_excluded | 0 | 0 | 10.773 |
| nonbinary_zero_width | 0 | 0 | 5.274 |
| oblique_irrational | 0 | 1 | 11.584 |
| nested_rectangles | 0 | 1 | 10.831 |
| opaque_callback | 0 | 0 | 9.452 |
| opaque_oblique_halfplane | 0 | 0 | 10.438 |

The native broadcast mask takes 0.691 ms for
100,000 coordinates here. [Baseline reports](native_trims_0.28_baseline_work17.json)
and [current reports](native_trims_0.29_work17.json) retain every root, bound,
trim evidence and timing sample. 71 new regression cases use independent
Fraction/Decimal oracles and adversarial authority/serialization controls.

The opaque_oblique_halfplane control includes the positive analytic root under
x+y>=0 on y=x, yet its membership remains unverified. This is the measured
reason to add a native affine half-plane predicate next, with closed/open
boundary rules and exact rational root-side oracles.
