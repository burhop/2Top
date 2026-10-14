# Occupancy validity (0.17.0)

Binary occupancy is a mask, not a continuous implicit field. Previously its
gradient returned zero at every point. Adding the coordinate field `y` to a
unit-valued square mask then produced normal `(0,1)` at `(0,2)`, although values
on either side jumped from 2 to 3. A direct occupancy `level_set(0.5)` similarly
returned a sign-changing procedural curve despite the mask never equaling 0.5:
the measured 31×31 plot interpolated 77 contour vertices with no actual zeros.

## Bounded correction and compatibility

- Finite strict-interior/exterior values retain the existing classification:
  `region.contains(tolerance=1e-8)` excluding
  `region.contains_boundary(tolerance=1e-8)`. Serialization keys stay unchanged.
  Finite real scalar outputs, including accepted live NumPy scalars, export as
  ordinary JSON numbers. Invalid output configuration raises `ValueError`.
- Derivatives are zero on accepted constant pieces. Both components are NaN in
  the declared `2e-8` boundary guard, in known invalid source domains, or where
  bounded membership probes observe a different/nonfinite value. This includes
  tested outer edges, corners, holes, singular sources and polygon trim transitions.
- Boundary predicates use existing curve/trim units, which may depend on field
  rescaling. They do not define a Euclidean offset. Polygon trim rectangles can
  suppress a boundary predicate at a real containment transition; four axis
  probes supplement that guard. Probe displacements are `±2e-8`, using `nextafter`
  when an addition rounds away. Scalar callbacks still receive scalar coordinates.
- Equal finite inside/outside outputs define a constant field: finite-coordinate
  values and zero derivatives need no region queries. Nonfinite coordinates
  return NaN, including on constant fields. Numerical inputs broadcast consistently
  for scalars, zero-dimensional arrays, lists, grids and empty arrays.
- Known nonfinite source boundary evaluations are masked. Unavailable/malformed
  predicates and callback exceptions remain explicit errors. Closure is queried
  with the existing resolved tolerance to avoid reusing its default cached result;
  an observed open or empty boundary is rejected.
- Occupancy's cross-query cache is removed. Array identity or matching a few grid
  samples cannot safely establish unchanged coordinates, values or geometry.
  Returned arrays are fresh; coordinate/result edits and current region/value
  replacements take effect without `clear_cache`. The common cache API remains,
  and algebraic queries still reuse shared fields within one query.

**Intentional level-set change:** direct `OccupancyField.level_set` raises
`ValueError` for finite levels. Levels absent from the stored outputs have empty
zero sets; endpoint levels can describe plateaus or empty sets, not regular
implicit curves. Equal-value fields likewise have an empty set or whole-plane
plateau. Return types for successful regular continuous fields are unchanged.
Use the existing `region.outer_boundary` and `region.holes` for boundary geometry.
Choose the existing distance strategy explicitly when a sampled distance field
is appropriate; it is not automatically an exact Euclidean offset.

## Evidence and measured tradeoffs

Independent reference cases cover rectangles, circles under field rescaling,
convex/concave polygons, holes, translated/tiny/large geometry, finite output
rescaling, domains, singularity, scalar callbacks, serialization and mutations.
The correction makes the reproduced composed normal fail explicitly, rejects
the nonexistent direct half-level curve, and fixes the stale edited-grid result.

Run `python -m pytest tests/test_occupancy_validity.py` and
`python benchmarks/occupancy_validity.py --output occupancy.json`. For comparison,
save `geometry/field_strategy.py` from commit
`1345e6bd7492ad9b1fe78b0832b7f56983855270` and pass it as `--baseline-file`.
[Raw Work17 timings](occupancy_validity_work17.json) record seven warm batches of
30 queries on a 97×97 square grid. Current evaluation is approximately **0.34 ms**,
versus **0.22 ms** for the previous uncached path and **0.00071 ms** for its unsafe
repeated-grid cache hit. Guarded gradients cost approximately **1.40 ms**, versus
**0.0047 ms** for unconditional zeros; constant-field gradients cost **0.019 ms**.
Fresh-grid timings include copies. Compilation is excluded. These measurements
show a correctness cost, not a speed improvement or an application FPS claim.

## Limits and next work

Finite membership samples cannot prove continuity or detect every hidden custom
predicate jump. The guard is conservative and may reject regular near-boundary
points. Region topology/containment and source callbacks remain their existing
oracles, including separate conic classification and factory metadata caches.
Removing the occupancy cache does not certify arbitrary in-place geometry edits.

Generic discontinuous compositions can still be wrapped and interpolated by
plotters: NaN boundary derivatives reject normals, not every fabricated rendered
contour. This increment closes the dedicated occupancy level-set path without
redesigning the global contour solver. Signed-distance cache/derivative validity
and domain/noise contracts remain separate useful geometry work.

A narrow [signed-distance cache reproduction](occupancy_next_sdf_cache.json)
already shows the next concrete gap: editing one cached grid coordinate from
`(1,2)` to `(-1,2)` for the `[0,4]` square leaves the reported distance at `-1`;
clearing that unchanged field's cache returns the analytic `+1`. This increment
leaves the distance implementation intact.
