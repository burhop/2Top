# Sublevel envelopes and preserved level-set kernels (0.14.0)

`curve.sublevel_bounds(level=0)` and `field.sublevel_bounds(level=0)` return an
immutable `SublevelBounds` with one of three `kind` values:

| Kind | Meaning | `box` |
| --- | --- | --- |
| `bounded` | Finite enclosure of the mathematical set `f <= level` | `(xmin, xmax, ymin, ymax)` |
| `empty` | Mathematical sublevel set proved empty | `None` |
| `unknown` | No supported finite enclosure proof available | `None` |

A bounded result may contain an empty set; boxes are enclosures, not proofs that
every enclosed point belongs to the field. Equal endpoints are valid. Unknown
does not mean empty. Levels must be finite real numbers; booleans, complex values
and strings are rejected.

## Supported proof

Native symbolic fields support constant emptiness and positive-definite
quadratics with rational or stored SymPy Float coefficients. Float atoms are
rationalized exactly **before expansion**, preserving the expression's stored
bits. Completion of the square, positive definiteness, the minimum and squared
axis extents use exact rational arithmetic. Each resulting float endpoint is
checked against the exact squared extent; adjacent outward floats are tried up
to eight times. Failure to obtain a finite checked enclosure returns unknown.
A 256-entry cache keys the immutable expression, variable tuple and level.
Expression or variable assignment invalidates compiled evaluation/gradient caches, so the
kernel and enclosure cannot silently describe different native fields.

These enclosures describe the underlying real mathematical field. They do not
enclose every artifact of floating evaluation near cancellation, reconstruct
constants already lost when an expression was built, or certify arbitrary
callbacks from display expressions. Custom evaluators require their own proof.
Higher-degree, nonrational, indefinite and semidefinite cases conservatively
return unknown. A negative-definite circle can have a bounded zero contour and
an unbounded sublevel set: the two contracts must remain distinct.

## Constructive composition

Union encloses both child sublevels. Intersection uses the intersection of two
known boxes, or either known child when the other is unknown. Disjoint known
intersection boxes prove emptiness. Difference uses the first operand only.
An unknown union operand makes the union unknown.

For the existing smooth minimum, `min(f1,f2)-alpha/2 <= S <= min(f1,f2)`.
Consequently `S <= L` is enclosed by the union of child sublevels at
`L + alpha/2`. Nested blends propagate this field-level expansion recursively
using exact rational sums, without float overflow. **Alpha is a field-unit
parameter**, so rescaling a field changes its geometry unless alpha is scaled
too. It is not a spatial distance or a generic Euclidean offset.

`RFunctionCurve.bounding_box()` retains the tuple/None API, now returning the
zero-sublevel enclosure. Empty and unknown both map to None in this legacy API;
use the new method to distinguish them. Other legacy display boxes retain their
existing behavior. Intersection exclusion uses supported sublevel enclosures
and complete finite trim rectangles, never unknown fields' heuristic boxes.
Trim rectangles constrain curve membership, not the untrimmed field sublevels.
Numerical intersection search still depends on a finite domain, grid and
tolerance; this change does not prove that every intersection is discovered.

## CurveField level sets

`CurveField(curve).level_set(L)` returns `LevelSetCurve`, preserving original
numeric evaluation, gradient and normal regularity checks while subtracting a
constant field value. Procedural callbacks work without a symbolic expression;
stable R-function evaluation is no longer replaced by an overflowing symbolic
square root. Scalar, broadcast, empty and zero-dimensional array contracts are
retained. Kinetic island curves keep their specialized recipe path. General
algebraic-field and sampled-field enclosure proofs remain unavailable.

`LevelSetCurve` serializes its source curve and finite shift, with round-trip
dispatch in `ImplicitCurve.from_dict`. Older libraries cannot read this new
curve type. Existing curve types and studio recipe schema 4 remain compatible.
Procedural functions and gradient callbacks remain honest unavailable code
placeholders on serialization; a wrapper does not save executable code.

## Reproduce the counterexamples

```bash
python -m pytest tests/test_sublevel_bounds.py tests/test_graphics_rfunction.py tests/test_base_field.py
python benchmarks/sublevel_bounds.py --output bounds.json
python benchmarks/sublevel_bounds.py --implementation-root ../previous-checkout --output before.json
```

Saved [0.13 results](benchmarks/sublevel-0.14.0-before.json) and
[0.14 results](benchmarks/sublevel-0.14.0-after.json) use 1,024 analytic contour
points per fixture. Identical unit-circle blends with alpha 2 have radius sqrt(2)
and nested radius sqrt(3): old child boxes missed 1,020 and 1,024 sampled points;
new boxes miss zero. The remote-pocket search changes from zero to two analytic
intersections. Procedural level sets no longer raise TypeError, and a shifted
extreme blend preserves its finite value around -1.118e200.

Warm box queries on Work17 cost about 0.0065 ms versus 0.0035 ms for one blend,
and 0.0158 ms versus 0.0059 ms for the nested fixture. These local means exclude
the initial exact quadratic proof, depend on cache/workload and are not universal
performance promises. The correctness tradeoff is explicit.

Remaining work includes higher-degree or domain-bound envelopes, floating
interval evaluation, local-scale derivative selection and general algebraic-field
derivatives. None is implied by an unknown result.
