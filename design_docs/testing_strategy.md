# QA and Testing Strategy for Implicit 2D Sketching System

**Test-First Approach:** We will use a **test-driven development (TDD)**
strategy for each module: defining test cases up front (for expected
behavior and edge conditions) before implementation. All core features
will have accompanying tests, ensuring correctness and preventing
regressions. We organize the QA plan by module (Graphics Backend,
Implicit Geometry, Scene Manager, UI) and also cover **MCP command
processing** and UI integration testing. Each module's section
summarizes its functionality and outlines test suites (functional tests,
edge cases, persistence, regression) with recommended frameworks.

## Graphics Backend Interface

**Summary of Core Interfaces:** The Graphics Backend Interface provides
a neutral API for retrieving all data needed to render the scene's
objects and fields, regardless of the rendering
library[\[1\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=This%20document%20defines%20a%20neutral,rendering%20library%20or%20transport%20mechanism).
Key methods include: - `get_bounding_box()` -- returns the global scene
bounds as (min_point,
max_point)[\[2\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
`get_curve_paths(resolution, tolerance)` -- returns a list of polyline
paths approximating each implicit curve's geometry, with styling info
(points, color, width, label,
etc.)[\[3\]\[4\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
`get_field_data(resolution, bounds)` -- returns sampled scalar field
data (grid values within given bounds), plus metadata like colormap and
opacity[\[5\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
`get_intersections()` -- returns intersection point locations and
related curve IDs[\[6\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
`get_text_annotations()` -- returns any textual labels or debug
annotations to
render[\[7\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
`get_metadata()` -- returns global metadata (background color, units,
default styling hints,
etc.)[\[8\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=).

These outputs feed the frontend renderer (e.g. ThreeJS) to draw curves,
fields, and annotations. The interface must be implemented consistently
in the backend so that the UI can query it to refresh visuals.

**Suggested Testing Framework:** We will implement this interface in
Python (as part of the backend controller). **Pytest** is recommended
for unit testing these interface methods. Pytest's fixture mechanism can
initialize a test scene (with a few objects) for repeated use. If parts
are in TypeScript (for a web client-side implementation), we'll use a
lightweight JS testing tool (like **Jest** with Node/jsdom) for any
client-side portions (e.g. math.js evaluation), but primary validation
occurs on the Python side which is authoritative for data.

**Functional Test Cases:** *(Ensure each interface method returns
correct and complete data.)* - **Test get_bounding_box -- Basic Scene:**
Add a couple of objects with known coordinates (e.g. a curve spanning x
in \[0,10\] and y in \[5,15\]). Verify `get_bounding_box()` returns
`(min_x, min_y)` = (0,5) and `(max_x, max_y)` =
(10,15)[\[2\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). Include a
case with a single object to ensure it returns that object's bounds
exactly.  
- **Test get_bounding_box -- No Objects:** If the scene is empty, ensure
it returns a sensible default or empty bounds (e.g. `(0,0)-(0,0)` or
raises a clear exception). The expected behavior will be defined in
implementation; the test asserts that it does *not* return an undefined
value or crash (fail-fast with a message if undefined input).  
- **Test get_curve_paths -- Simple Curve:** Insert a simple implicit
curve (e.g. a unit circle defined by `x^2 + y^2 - 1 = 0`). Verify
`get_curve_paths(resolution=256)` returns a list with one path dict.
Assert that the polyline points lie roughly on the circle (e.g. the
point with minimum x has x ≈ -1, y ≈ 0). Check that color and line_width
match the object's style settings or defaults, and that the `label` (if
any) and `style` keys are
present[\[4\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=).  
- **Test get_curve_paths -- Tolerance and Resolution:** For a given
complex curve, call `get_curve_paths` with a coarse resolution (e.g. 50)
and a fine resolution (500). The test ensures the returned point list is
longer (more detailed) for the finer resolution. Similarly, test that
varying the `tolerance` parameter influences the simplification of the
path (smaller tolerance yields more points). This ensures the interface
respects these parameters and does not default silently.  
- **Test get_field_data -- Default and Custom Bounds:** Create a scalar
field object (e.g. a distance field or noise field) in the scene. Call
`get_field_data()` with default parameters and verify the result
includes: - An `extent` matching either the object's bounds or the scene
bounds[\[9\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=,%27heatmap%27%2C%20%27contours). -
A 2D array `values` of shape equal to the requested resolution (256×256
by default)[\[5\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). -
Proper metadata: a `colormap` string (e.g. default "viridis"), an
`opacity` value (e.g. 1.0 by default), and optional `level_sets` if
defined. - All values in the grid correspond to evaluating the field's
function on the grid (we can sample a few points manually via the
field's known equation to cross-check). Next, call
`get_field_data(resolution=(128,128), bounds=((x0,y0),(x1,y1)))` with a
specific sub-region. Verify the output `extent` equals the provided
bounds and the `values` array shape is 128×128. Check that extreme
values or edge behavior (like if the bounds only partially cover the
field) are handled (no crashes, possibly values outside the field
default to 0 or some background).  
- **Test get_intersections -- Two Curves:** Add two curves known to
intersect (e.g. two lines or a line and a circle). Verify
`get_intersections()` returns a list of intersection
dicts[\[6\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=) with correct
coordinates. For example, two perpendicular lines crossing at (2,3)
should yield one entry with `position ≈ (2,3)` and `curve_ids`
containing both line IDs. If curves do not intersect, verify it returns
an empty list (and not `None`).  
- **Test get_intersections -- Edge Case (Tangency):** Use two curves
that touch tangentially (e.g. a circle of radius 5 and another circle of
radius 3 that just touch at one point). Ensure either a single
intersection point is returned (with both curve IDs) or, if the method
defines tangency differently, that it's handled consistently (the
expected result should be defined---likely still one intersection). This
test ensures the method doesn't double-count or miss borderline cases.  
- **Test get_text_annotations:** If the system adds text annotations
(like labels or debug info), add a known annotation via the scene (or
ensure one exists, e.g. object name labels). Call
`get_text_annotations()` and verify it returns entries with the expected
`text` content, `position` coordinates, and styling (size, color,
alignment)[\[10\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=). For
example, if an object "Circle1" should have a label at its center,
ensure the returned list contains \"Circle1\" at the correct
coordinates. Also test with no annotations present (should return an
empty list without error).  
- **Test get_metadata:** Set some global metadata in the scene (e.g.
background color = black, units = \"cm\"). Verify `get_metadata()`
returns a dict with those keys and
values[\[11\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=%2A%2APurpose%3A%2A%2A%20Passes%20general,guide%20rendering).
If certain metadata keys have defaults (like `default_line_width`), test
that they appear with the expected default. Also ensure that adding a
new metadata (e.g. setting zoom level) is reflected. The test confirms
that the metadata is up-to-date and consistent with scene state.

**Edge Case & Failure Mode Tests:** *(Validate robust handling of
invalid or extreme inputs.)* - **Invalid Parameters:** Call each method
with out-of-bounds or invalid inputs to confirm graceful failure. For
example, call `get_curve_paths(resolution=-5)` or
`get_field_data(resolution=(0,0))`. The expected outcome is that the
interface **fails fast** with a clear error (likely raising a
`ValueError` due to invalid resolution) rather than producing
nonsense[\[12\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Exception%20and%20Error%20Handling).
A test will assert that a `ValueError` or custom exception is raised for
negative/zero resolution or tolerance values, matching the design's
emphasis on failing on invalid input.  
- **Missing Data Cases:** Test behavior when the scene is in a minimal
state. For instance, if `get_field_data` is called but no field objects
exist, the interface might return an empty grid or raise a "No field"
exception. We verify the chosen behavior (e.g. an empty result with
perhaps default extent) and ensure it's handled predictably (no silent
wrong data, and documented to developers). Similar tests for
`get_curve_paths` with no curves (expect empty list).  
- **Extreme Scene Sizes:** Populate a scene with a very large coordinate
range (e.g. an object at (1e6,1e6)). Test that `get_bounding_box`
correctly handles large values without overflow and that
`get_field_data` can handle a large bounding box (possibly by
downsampling). If performance might be an issue, this could be marked as
a performance test, but at minimum ensure no crash or precision error.  
- **Performance Consideration (Informational):** Although not a strict
unit test, we will include a **profiling** step to ensure that repeated
calls (e.g. many successive `get_curve_paths` calls for animation)
perform within acceptable time. This isn't a pass/fail unit test but
helps QA the "real-time update" use
case[\[13\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=To%20support%20sliders%2C%20parameter%20drags%2C,We%20support%20this%20by%20allowing).
If needed, we can create a benchmark test (PyTest can mark performance
tests) that generates an implicit curve, updates a parameter in a loop,
and calls `get_curve_paths` 100 times, asserting it stays within a time
threshold.

**Persistence Testing:** The Graphics Backend Interface itself does not
manage file persistence (that is handled by the Scene Manager), but we
will still perform **round-trip tests** in integration with scene
saving: - Save a scene with several objects to a file (JSON or
`.scene.py` via the Scene Manager) and then load it back. After loading,
call the Graphics interface methods (`get_curve_paths`, etc.) and
compare their outputs to those from before saving. They should match
exactly (the scene is restored fully). For example, ensure the bounding
box and number of curves returned after load are identical to pre-save.
This effectively tests that no data is lost or altered through the
save/load process, indirectly verifying that the interface's data is
persistent via Scene Manager.  
- If the interface is used over an API (e.g. via Flask endpoints
returning
JSON[\[14\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Required%20Backend%20Calls%3A)),
consider an integration test where we start a test server and call the
endpoints (`/object`, `/scene/save`, etc. as
listed[\[15\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)) to retrieve
data. Validate that the JSON matches expectations (e.g. `/object/:id`
returns the correct object state). This ensures the interface works in
the deployed context and that JSON serialization is correct. (These
would be higher-level tests perhaps using **pytest+requests** or
similar.)

**Regression Test Mechanism:** Each time a bug is reported (for example,
a case where `get_curve_paths` returned an incorrectly ordered point
list, or `get_field_data` mis-scaled the field values), we will **write
a new test** that reproduces that scenario. For instance, if a specific
implicit curve equation caused a crash in marching squares extraction,
we add a test case with that equation to ensure `get_curve_paths` now
handles it properly. All such regression tests will be collected
(possibly in a `test_graphics_backend_regressions.py` module). We also
maintain a library of sample scenes that previously caused issues (like
very close intersection points, extremely thin curves, etc.), and for
each we have an automated test to load the scene and call the interface
to verify the output is now correct. This practice guarantees that once
a bug is fixed, it stays fixed (the test will fail if it ever
regresses). Additionally, as part of test-first practice, whenever
adding a new interface feature we attempt to think of potential failure
modes upfront and write those tests so that even latent bugs can surface
early.

## Implicit Geometry Module

**Summary of Core Interfaces and Functionality:** The Implicit Geometry
module is a Python library for creating and manipulating 2D implicit
curves and derived shapes. All geometric objects are defined by implicit
equations $f(x,y) = 0$ and support operations like intersection
computation, blending, offsets, boolean combinations, and conversion to
fields[\[16\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Implicit%20Curves)[\[17\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=2).
Key components include: - **Base class** `ImplicitCurve`**:** provides
methods like `evaluate(x,y)` (compute $f(x,y)$ ), `gradient(x,y)`,
`normal(x,y)`, and
others[\[18\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=1.%20Base%20Class%3A%20).
These should be pure functions with no side-effects, returning numeric
results for a given point. - **Specific curve subclasses:** e.g.
`ConicSection`, `PolynomialCurve`, `Superellipse`, `RFunctionCurve` (for
smooth
unions/intersections)[\[19\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Different%20types%20of%20implicit%20curves,supported%20via%20a%20class%20hierarchy).
These may have additional methods like `degree()` for polynomials or
`canonical_form()`, but importantly they inherit the base interface. -
**Curve operations:** functions for geometric operations such as
`intersect(curve1, curve2)` to find intersection
points[\[17\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=2),
`blend(curve1, curve2, method)` to combine
shapes[\[20\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=3),
`offset(curve, distance)` to create an offset
curve[\[21\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,), and boolean
set ops `union()/intersection()/difference()` that produce new implicit
curves representing those
combinations[\[22\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=5). -
**Trimmed and composite curves:** classes like `TrimmedImplicitCurve` (a
curve restricted to a segment or region) and `CompositeCurve` (sequence
of curve segments) implement the same `ImplicitCurve` interface so they
can be used
interchangeably[\[23\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=3.%20)[\[24\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=4.%20).
For example, a `CompositeCurve` might have `is_closed()` to check if end
joins start, and uses multiple `TrimmedImplicitCurve` segments. -
**AreaRegion:** represents a filled 2D area bounded by curves (with
potential holes), supporting methods like `contains(x,y)` and
`area()`[\[25\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=5.%20). It
can generate associated fields (distance fields, occupancy grids, etc.)
via a pluggable
`FieldStrategy`[\[26\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Field%20Objects)[\[27\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=%23%20Built). -
**Field objects:** The module also defines `BaseField` and concrete
field classes (like `CurveField`, `BlendedField`, `SampledField`) that
map positions to scalar
values[\[28\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%27BaseField%27%3A%20...)[\[29\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=).
These allow converting curves to scalar fields, blending fields,
sampling to grids, etc., often used for visualization or further
computation.

The implicit geometry module is at the core of correctness for geometric
calculations, so we plan extensive unit tests for mathematical accuracy,
robustness of operations, and compliance with expected interface
contracts (like throwing exceptions on invalid inputs).

**Suggested Testing Framework:** We will use **Pytest** for all geometry
module tests. We may also leverage scientific libraries for verification
-- for example, using **Sympy** to obtain expected intersection
solutions for comparison, or **NumPy** for vectorized testing of field
evaluations. Pytest parameterization will help test multiple shapes and
scenarios succinctly. Where needed, property-based testing (with
Hypothesis or similar) can generate random curves to ensure invariants
(but initially we focus on deterministic cases).

**Functional Test Cases:** *(Validating correct results for each major
operation and class method.)* - **Test evaluate/gradient/normal -- Basic
Curve:** Construct a simple implicit curve, e.g.
`Circle: x^2 + y^2 - 4 = 0` (radius 2). Test that: - `evaluate(2,0) ≈ 0`
(point on the circle) and `evaluate(0,0) < 0` (inside the circle if we
define negative as inside) and `evaluate(3,0) > 0` (outside). This
checks the sign convention and basic evaluation correctness. -
`gradient(x,y)` returns $(\partial f/\partial x,\partial f/\partial y)$
. For the circle, at (2,0) we expect gradient ≈ (4, 0) (since ∂/∂x of
$x^{2} + y^{2} - 4$ is 2x, giving 4). The test will compare the returned
gradient to the expected analytical gradient. We do this at a couple of
points (including a non-axis-aligned point). - `normal(x,y)` should be a
normalized version of the gradient (or otherwise perpendicular to the
curve). For (2,0) on the circle, the normal should point outward
(approximately (1,0) unit vector). We verify that `normal` is indeed the
unit-length version of the gradient (within a tolerance).  
- **Test ImplicitCurve consistency:** Ensure that any subclass of
`ImplicitCurve` still produces consistent evaluate/gradient. For
example, create a `ConicSection` representing the same circle and verify
it yields the same results as the base `ImplicitCurve` test above. If
the subclass overrides methods (e.g. an optimized `evaluate`), the
outputs should remain mathematically consistent.  
- **Test intersection points (curve-curve):** Use known scenarios: - Two
lines: e.g. $f_{1}:y - 1 = 0$ (horizontal line at y=1) and
$f_{2}:x - 2 = 0$ (vertical line at x=2). The intersection is
analytically (2,1). Confirm `intersect(f1, f2)` returns a list with one
solution approx (x=2,
y=1)[\[17\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=2). No
extraneous intersections should appear. - Line and circle: line $y = 0$
and circle $x^{2} + y^{2} - 1 = 0$ . Expect two intersection points at
(-1,0) and (1,0). Test that we get two solutions and they match those
coordinates (within a tolerance if numeric). Also verify the solutions
are returned as dictionaries or tuples as specified (e.g. maybe
`{"x": ..., "y": ...}` or similar structure) and that the function
handles both symbolic (if possible) or numeric fallback correctly.  
- Parallel lines (no intersection): e.g. $y - 1 = 0$ and $y - 2 = 0$ .
`intersect` should return an empty list. Test that it does so and does
not throw an error for non-intersecting inputs; this covers the expected
behavior for disjoint geometry. - **Test blending curves:** Take two
simple curves and blend them: - For example, blend two implicit
half-planes or a circle and a square's implicit function, using method
`"quadratic"` (if defined). The result is a new `ImplicitCurve`. We
might not have an easy closed-form expected equation, but we can test
properties: e.g. the blended curve's `evaluate` should be negative in
regions where either original was negative (if blending is like a
union). If we blend identical curves, the result should essentially
equal the original shape's equation (idempotence test). A specific test:
blend two distant circles -- the output might have two lobes; verify at
a point near the center of one circle, `evaluate` is negative (inside),
and far outside both circles it's positive. Essentially, check that
blending doesn't erroneously exclude regions that should be included
(for union-like blend) or vice versa.  
- Additionally, if the blend method supports different strategies
(smooth union vs intersection), test each if applicable: e.g. a smooth
intersection of two overlapping shapes yields an object that only covers
the overlap -- test a point in overlap vs outside overlap. - **Test
offset curve:** Create a known shape and offset it: - Use a circle of
radius 1. Call `offset(circle, 0.5)` which should produce a new curve
(approximately radius 1.5 if outward). Test that for the new curve,
`evaluate(1.5, 0) ≈ 0` (on the offset boundary) whereas the original
circle at (1.5,0) had `evaluate > 0` (outside). Also test an inner
offset (negative distance) e.g. -0.2 yields radius \~0.8, and check a
point at radius 0.8 is on the new curve. This verifies the offset
distance is correctly applied.  
- Test edge case: offset by 0 (should return an equivalent curve,
perhaps the same instance or a copy). And offset by a very large number
relative to shape size -- maybe result becomes very large and possibly
less accurate; ensure no crash and result still behaves (maybe largely
flat function far away).  
- **Test boolean operations (union, intersection, difference):** Use
simple shapes for which we can predict results: - **Union:** Take two
overlapping circles. The `union(curve1, curve2)` returns an
ImplicitCurve that should represent the area covered by either circle.
Test a point that lies inside one circle but outside the other -- the
union's `evaluate` at that point should indicate "inside" (depending on
convention, likely negative if inside either). Conversely, a point
outside both should be "outside" (positive). Also test a point deep
inside both (should definitely be inside union). This ensures the union
operation is properly combining regions (likely via an `RFunctionCurve`
using max or min
operations)[\[22\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=5).  
- **Intersection (Boolean):** Using the same two circles,
`intersection(curve1, curve2)` should yield the overlapping region. Test
a point inside both original circles (should be inside intersection =\>
negative value) versus a point inside one but not the other (should be
outside =\> positive value).  
- **Difference:** e.g. `difference(circleA, circleB)` where circleB is
smaller and inside circleA. Choose a point inside circleA but also
inside circleB -- it should be outside the difference (since that region
was removed), so the resulting implicit function should be positive
there. A point inside circleA but outside circleB should remain inside
(negative). This checks that subtraction removes the specified area.  
- Additionally, ensure these operations return valid `ImplicitCurve`
objects that can be further used (e.g. you can call `evaluate` or even
do a second union with a third shape). The test can chain an operation:
`union(circleA, intersection(curveB, curveC))` for instance, and just
verify it produces an object without error. - **Test utilities
(simplify, substitute, etc.):** - **simplify:** If implemented, feed it
a known redundant expression (e.g.
$\left( x^{2} + y^{2} - 1 \right)^{2} = 0$ which is equivalent to
$x^{2} + y^{2} - 1 = 0$ ). `simplify` should return an ImplicitCurve
with an expression $x^{2} + y^{2} - 1$ (i.e. simplified). Verify the
simplified curve's evaluate matches the original for several points. If
exact symbolic simplification isn't fully implemented, this test might
just assert that `simplify` returns an equivalent curve (perhaps the
same in this simple case).  
- **substitute:** Create a parameterized curve, e.g.
$f(x,y) = x^{2} + y^{2} - r^{2}$ with parameter $r$ . Use
`substitute(curve, {"r": 3})` to get a new curve where $r = 3$ . Test
that the new curve's evaluate is zero at radius 3 (e.g. at (3,0))
whereas the original with default r (say 1) was not. Also ensure the
original curve is unchanged (if the design is to return a new object).  
- **to_numpy_function:** For a given curve, call `to_numpy_function()`
which should return a vectorized function (callable) for NumPy
arrays[\[30\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=def%20substitute,np.ndarray%2C%20np.ndarray%5D%2C%20np.ndarray%5D%3A%20...).
Test it by providing an array of points: e.g. X = \[0, 1\], Y = \[0, 0\]
(two points along x-axis) and ensure it returns an array of the same
shape with the correct evaluations (for the example circle, results
would be \[-1, 0\] if r=1). Compare these to manually computing or using
the scalar evaluate in a loop. This verifies the vectorization produces
correct results and shapes.

- **Test TrimmedImplicitCurve:** Take a base curve (say a full circle)
  and trim it to a half-circle arc. For example, define a `mask`
  function that is true for x \>= 0 to keep only the right half of the
  circle. Create `TrimmedImplicitCurve(base_curve=circle, mask=mask)`.
  Test that:
- `evaluate(x,y)` on a point that was originally on the left half
  returns something that indicates it's no longer part of the curve
  (possibly still 0 from the equation, since trimming doesn't change
  equation, but maybe `contains(x,y)` will be false). So use
  `contains(x,y)` -- for a point on the left side of the original
  circle, `contains` should be
  false[\[31\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%28optional%20future%20method),
  while for a point on the right side arc `contains` is true. This
  checks the mask is applied.
- The `plot()` or path extraction for the trimmed curve only yields the
  half-arc. If `get_curve_paths` is used on a trimmed curve, it should
  output only that segment. We can indirectly verify by checking that
  the bounding box of the trimmed curve's polyline is smaller than the
  full circle's (e.g. for right-half, min_x \~0 instead of -1).
- If `trim_curve` utility is available, test it produces the same result
  as manually constructing a TrimmedImplicitCurve. Also test
  `curve_segment(curve, start, end)` where start/end are two
  intersection points on a curve -- the returned trimmed curve's
  contains() is true between those and false outside.
- **Test CompositeCurve:** Construct a `CompositeCurve` from multiple
  `TrimmedImplicitCurve` segments, e.g. approximating a polyline or a
  closed loop piecewise. For a simple test, split a circle into four
  quarter arcs (trim the circle into quadrants) and combine them into a
  `CompositeCurve`. Then:
- `is_closed()` should return True (since the end of the last arc meets
  the start of the
  first)[\[24\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=4.%20).
- `evaluate(x,y)` on points along the circle should be ≈0 (the composite
  behaves like the full circle). Test a few quadrant boundary points.
- Ensure each segment is accessible (if `segments()` returns the list)
  and that the segments retain their trim masks.
- Test that composite curves can be used in operations too: e.g. take a
  composite (closed loop) and an independent curve, perform an
  `intersect` operation. It should handle the composite by checking each
  segment -- our test can verify that the intersection points found
  include those on the appropriate segment.
- **Test AreaRegion and FieldStrategies:** Create a simple closed area
  (e.g. an AreaRegion from a circular composite curve as outer boundary,
  no holes). Then:
- `contains(x,y)`: Test a point clearly inside (should return True) and
  a point outside
  (False)[\[32\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%60contains%28x%2C%20y).
  Also test a point exactly on the boundary -- depending on design it
  might count as inside or not; define expected behavior (commonly
  boundary might count as inside for contains). Our test will assert the
  documented behavior.
- `area()`: For a circle of radius 2, area should be \~12.5664. Allow a
  small tolerance if the area is computed numerically (or if exact
  integration is implemented for circle, it might match πr\^2 exactly).
  Create an AreaRegion and verify `area()` returns the expected value
  (this also indirectly tests that the composite curve was recognized as
  closed for integration).
- Assign a `FieldStrategy` to the area, e.g. `SignedDistanceStrategy`.
  Call `area_region.field(x,y)` at a point just inside and just outside
  the boundary. Just inside should yield a small negative value (if
  signed distance where inside is negative) and outside a small
  positive[\[33\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,signed%20distance).
  At the boundary, approximately 0. This tests that the signed distance
  field is generated correctly.
- Switch to an `OccupancyFillStrategy` (inside=1,
  outside=0)[\[27\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=%23%20Built)
  and regenerate field. Now inside points should return 1.0, outside 0.
  Test a few points to confirm the binary fill behavior. Similarly, test
  `BoundedGradientStrategy` with a given falloff -- e.g. inside might be
  0, just outside starts increasing up to a max. We verify at least
  qualitatively that `field(x,y)` changes as expected when strategy is
  changed (and ensure no caching issue keeps old values).
- `fill(resolution)`: Test that generating a raster fill returns an
  array of the right size and content. For occupancy strategy on a
  simple shape, the returned numpy array should have interior points set
  (we can sum the array and expect roughly area \* pixel_density). For
  distance, we might just check the shape and that values range from
  -distance to +distance.
- **Field-level operations:** If `Field` class and global operations
  (`add, subtract, multiply fields`) are
  implemented[\[34\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=The%20following%20high,fields%20derived%20from%20implicit%20geometry),
  we would include tests for those as well. For example, create two
  simple fields (like two Gaussian-type fields or distance fields), add
  them, and verify at sample points that the sum is correct. Similarly
  test min/max (if implemented for e.g. union of fields) yields the
  lesser/greater of inputs at test points. This ensures the field
  combination logic is correct.

**Edge Case & Error Handling Tests:** *(Ensure the module correctly
handles invalid inputs and edge conditions as per design
guidelines[\[12\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Exception%20and%20Error%20Handling).)* -
**Domain Errors:** Many methods should raise exceptions for invalid
input. We test for these explicitly: - Calling
`curve_segment(curve, start, end)` where `start` or `end` is not
actually on the curve should raise a `ValueError`. We can choose a line
$y = 0$ and take start=(0,1) (not on the line) -- expect an error
indicating points not on curve. Likewise for `trim_curve` with a mask
that doesn't select any part (maybe it should still return a valid curve
of zero length or raise; likely just returns nothing meaningful, but we
decide to treat it as error or empty). - `intersect(curve1, curve2)`
where one or both are not valid curves (e.g. passing `None` or an
unsupported type) -- should raise `TypeError`. We simulate by calling
intersect with one argument not an `ImplicitCurve`. The test asserts a
clear exception message occurs (no silent failure). - Extremely complex
curves or high-degree polynomials: ensure functions either handle them
or raise `NotImplementedError` if not supported. For example, if
`PolynomialCurve` of degree 10 is beyond current solving ability for
intersections, the code might raise NotImplemented -- test that this
occurs rather than an incorrect result.  
- Test numeric stability: e.g. intersect nearly parallel lines (small
angle between) -- solution is far out or ill-conditioned. The algorithm
might struggle; ensure if it fails, it raises a well-described exception
or returns an empty list (if considered no robust intersection). The
test will assert no crash and that the outcome aligns with documentation
(could be an empty list if lines nearly parallel beyond tolerance). -
**Precision and Tolerance:** If the module allows a `strict` mode or
tolerance
parameter[\[35\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,to%20control%20tolerance%20vs%20exactness),
test its effect. For example, for an intersection of a line and circle
that just touch, in strict mode maybe it returns one intersection; in
non-strict maybe two very close points? Or vice versa. If `strict=True`
means exact math, test that with exact shapes (like rational
coefficients) it finds symbolic solutions. If `strict=False` allows
numerical approximations, test a scenario where symbolic might not solve
but numeric does (and verify an approximate answer is returned).  
- **Performance of Critical Ops:** Not a unit test, but we will include
some performance checks for operations like `intersect` or `blend` on
large objects. For instance, blending two fields repeatedly or
offsetting a very detailed curve many times. We may include a test that
runs offset on an intricate shape and completes within a time bound.
While not a strict QA pass/fail, it helps catch any extreme
inefficiencies (like an offset algorithm that unexpectedly goes
quadratic in complexity). - **Memory leaks:** This is harder to test via
unit tests, but as part of QA we will monitor long sequences of
operations (like creating and discarding many curves in a loop) to
ensure memory usage stabilizes. We can wrap such a loop in a test and
assert that memory (as measured via Python's gc or tracemalloc) does not
grow beyond a threshold, indicating no major leaks.

**Persistence Testing:** Persistence is mainly handled via the Scene
Manager, but the geometry module supports it by providing `to_dict()` /
`from_dict()` on each
object[\[36\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%60get_bounds%28%29%20,bounding%20box%20for%20the%20object).
We will test round-trip serialization for all geometry types: -
**to_dict/from_dict -- Curve Objects:** For each concrete curve class
(`Circle` (if a convenience class wrapping `ImplicitCurve`),
`PolynomialCurve`, `CompositeCurve`, etc.), create a sample instance
with known parameters. Call `to_dict()` and inspect the output dict: it
should include all necessary data (type identifier, equation or
coefficients, parameters, etc.). Then call the class's `from_dict()` on
that dict to reconstruct an object. Verify that the reconstructed object
is equivalent to the original: - For curves, compare evaluate results at
a couple of points. - For composites or trimmed, ensure the
sub-components were restored (e.g. the number of segments in a
CompositeCurve is the same). - Styles are handled by Scene Manager, but
if any style info is included in dict (some design store style
separately), ensure either it's excluded or handled appropriately.  
- **to_dict/from_dict -- Fields and Areas:** Similarly, test
serialization of a Field (for instance a Field created from a curve).
The `to_dict` might need to store the source curve or data array. After
round-trip, test that evaluating the field at points yields the same
results. For an AreaRegion, the dict should capture outer boundary and
holes; after `from_dict`, test that `contains` and `area` still return
the same as before.  
- **Scene Save Integration:** As an integration test, when the Scene
Manager uses these methods to save a scene, we want to ensure each
object's dict is correct. We can indirectly verify by saving a scene and
checking the JSON: it should have entries like
`"type": "CompositeCurve", "data": {...}` as per
spec[\[37\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=JSON%20Scene%20Format%20%60%60%60json%20,c2).
The test can parse the JSON and verify that for each object type,
required fields are present. Then use our module's `from_dict` to
rebuild objects and cross-check geometry as above.  
- **Python .scene.py round-trip:** If `.scene.py` files are supported
(executable scripts to recreate the
scene[\[38\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Python%20,0ff%22%7D%29%20scene.save%28%22scene.json%22%29)),
this is harder to fully automate (it involves running the script). But
we can write a test that generates a `.scene.py`, then uses Python's
import or exec to run it in a sandbox, obtaining a SceneManager, and
then verify that `scene.list_objects()` and objects' details match the
original. This ensures our geometry classes and Scene Manager
collectively produce a correct script. (Mark this test as integration;
it might be skipped in CI if running arbitrary exec is undesired, but it
will be part of release QA.)

**Regression Testing Mechanism:** For the geometry module, any time a
geometric algorithm bug is found (which can be subtle), we will add a
focused test case: - For example, if an intersection routine failed to
find a solution for two curves at a specific angle, we add a test with
those curve equations and assert the correct intersection
count/coordinates. If a blending operation had a bug where the resulting
surface was not continuous, we add a test evaluating the blend at many
points to ensure continuity (perhaps by checking gradient
consistency). - We maintain a `test_implicit_geometry_regressions.py`
where each test is typically named after the issue (e.g.
`test_intersect_tangential_lines_issue47()` with a comment referencing
the bug). The test-first approach means if a bug is known, we actually
write the regression test **before** fixing the code to see it fail,
then ensure it passes after the fix. - Additionally, to guard against
future numerical issues, we might incorporate randomized testing: e.g.
generate random pairs of lines and ensure intersect either finds a valid
point or correctly identifies parallel lines. If any random case fails,
that could indicate an edge case to fix; we then turn it into a
deterministic regression test. - The regression tests are run as part of
the normal test suite so any re-introduction of a bug (or related error)
will be caught immediately in CI.

## Scene Manager Interface

**Summary of Core Interfaces:** The `SceneManager` is the central
coordinator for all objects and the scene
state[\[39\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=The%20,with%20the%20MCP%20agent%20protocol).
It manages creation/deletion of objects, grouping, styling, persistence,
and acts as the bridge to external control (MCP commands and rendering
queries). Key interface methods (Python API) include: -
`add_object(obj_id, obj, style)` -- Add a new geometric or field object
to the scene
registry[\[40\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,named%20object%20to%20the%20scene). -
`remove_object(obj_id)` -- Remove an object by its
ID[\[41\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60remove_object%28obj_id%3A%20str%29%20,from%20the%20scene%20by%20ID). -
`get_object(obj_id)` -- Retrieve the object instance for an
ID[\[42\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60get_object%28obj_id%3A%20str%29%20,object%20associated%20with%20the%20ID). -
`list_objects()` -- Return all object IDs in the
scene[\[43\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60list_objects%28%29%20,IDs%20currently%20in%20the%20scene). -
`objects_in_bbox(bbox)` -- Query objects that intersect a given bounding
box (useful for selecting objects in an
area)[\[44\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Returns%20a%20list%20of%20all,IDs%20currently%20in%20the%20scene). -
`set_style(obj_id, style)` / `get_style(obj_id)` -- Apply or retrieve a
visual style (color, line width, etc.) for an
object[\[45\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,style%20dictionary%20for%20an%20object). -
`set_group(group_id, object_ids)` -- Create or update a group with given
objects[\[46\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Returns%20the%20style%20dictionary%20associated,with%20an%20object). -
`update_group_style(group_id, style)` -- Apply a style to all objects in
a group (possibly by iterating
set_style)[\[47\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,IDs%20to%20a%20named%20group). -
`render_image(filename, resolution, bbox)` -- Render the current scene
to an image file (e.g.
PNG)[\[48\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,png). -
`render_animation(filename, frames, animate_fn, resolution)` -- Produce
an animation (like a GIF) by applying `animate_fn` over multiple
frames[\[49\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Renders%20the%20current%20scene%20to,png). -
`handle_mcp_command(command_dict)` -- Parse and execute a Model Context
Protocol command, altering the scene or querying it, and return the
result[\[50\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60handle_mcp_command%28command%3A%20Dict%29%20,command%20and%20returns%20the%20result). -
**Persistence:** `save_scene(filename)` and `load_scene(filename)` --
Save the scene (all objects, groups, styles) to disk in a JSON or script
format, and load it
back[\[51\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60save_scene%28filename%3A%20str%29%20,format).

The SceneManager ties together the geometry module (storing those
objects, calling their methods) and the graphics interface (by providing
data to draw). It must ensure consistency (e.g. unique IDs, group
membership valid) and enforce policies (no duplicate adds, etc.).

**Suggested Testing Framework:** **Pytest** will be used for the
SceneManager as well. We'll create fixtures for an empty SceneManager
and for a pre-populated scene to reuse across tests. Some tests may
benefit from using temporary directories or files (for save/load);
Pytest's tmp_path fixture can help manage that. If the UI or frontend
needs to be simulated, we may use stub callbacks (for example, a dummy
`animate_fn` for render_animation tests). The tests here are largely
unit tests, but a few will verge on integration (like actually writing
files or using the geometry classes in concert). For any asynchronous
behavior (if, say, rendering spawns threads or MCP uses async events),
we will use either synchronous modes or Pytest's support for async
tests.

**Functional Test Cases:** *(Each SceneManager API method's expected
behavior.)* - **Test add_object and get_object:** Start with a fresh
SceneManager. Create a sample ImplicitCurve (e.g. a line or circle).
Call `scene.add_object("obj1", curve_obj, style={"color": "#ff0000"})`.
Then: - Use `scene.get_object("obj1")` to retrieve it and verify it's
the same object (the test can check that the returned object equals the
one we added, or at least that it's the same type and has same defining
parameters). - Call `scene.list_objects()` and ensure \"obj1\" is in the
list[\[43\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60list_objects%28%29%20,IDs%20currently%20in%20the%20scene).
The list length should be 1 if it was empty before. - Call
`scene.get_style("obj1")` and verify it returns the style dict we
provided (color
\#ff0000)[\[45\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,style%20dictionary%20for%20an%20object).
If style was optional and we provided one, it should store it. If we add
another object without specifying style, `get_style` for that should
perhaps return an empty dict or a default (test both situations). -
Adding a second object with a different ID should succeed similarly.
Test that adding with an **existing ID** either raises an error or
overwrites (the design doesn't explicitly say, but we likely enforce
unique IDs). If our policy is to throw on duplicate, attempt
`add_object("obj1", other_obj)` should raise an Exception -- test for
that. If the policy is to overwrite, test that it indeed replaces the
object (and maybe log a warning). We will define the intended behavior
and test accordingly. - **Test remove_object:** Using a SceneManager
with a few objects, call
`scene.remove_object("obj1")`[\[41\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60remove_object%28obj_id%3A%20str%29%20,from%20the%20scene%20by%20ID).
After removal: - `get_object("obj1")` should return None or raise
(depending on implementation; likely None or KeyError). The test expects
that \"obj1\" is no longer present (we can check `list_objects()` and
see that \"obj1\" is gone). - If the object was part of a group, ensure
the group's membership updates. For example, if \"obj1\" was in group
\"G1\", after removal, maybe `objects_in_group("G1")` (if such exists)
or an internal group map no longer contains \"obj1\". If no direct
method, we might need to call `update_group_style("G1", style)` and
ensure it doesn't try to update a removed object (no error thrown). -
Removing a non-existent object ID should be handled gracefully -- the
method might throw a KeyError or simply ignore. The test will call
remove on a dummy ID and expect an exception of a specific type if
that's the design, or no change if ignoring is intended (but we should
lean towards raising an error to alert mistakes). We assert the chosen
behavior. - **Test list_objects and objects_in_bbox:** Add multiple
objects (e.g. a line, a circle, a field) with known positions. - Verify
`list_objects()` returns all their
IDs[\[43\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60list_objects%28%29%20,IDs%20currently%20in%20the%20scene);
the order is not crucial (could sort in test if needed), but the content
should match exactly the added IDs. - Use
`objects_in_bbox(((x_min,y_min),(x_max,y_max)))` to query a subset. For
example, if we have objects scattered, choose a box that covers only one
of them. Verify the returned list contains the ID of that object and not
others[\[44\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Returns%20a%20list%20of%20all,IDs%20currently%20in%20the%20scene).
Test a bounding box that encompasses all objects (should return all
IDs), and one that misses all objects (should return empty list). - Test
edge conditions: if a bounding box exactly touches an object's boundary.
For example, if a circle extends to x=5 as its far right, a bbox with
min_x=5, max_x=6 should likely count the circle as intersecting (since
at x=5 it has a point). The implementation likely treats any overlap as
inclusion -- our test will assume inclusive overlap and check that. If
not, adjust expectation accordingly. - **Test set_style and get_style:**
After adding an object, call
`scene.set_style("obj1", {"color": "#00ff00", "width": 2.0})`[\[45\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,style%20dictionary%20for%20an%20object).
Then: - `get_style("obj1")` should return a dict containing those keys
and values. If there was a previous style, ensure that updated keys
changed and unspecified keys remain or are default. For example,
initially style had only color, then we update width too; get_style
should now show both color and width (color unchanged if we didn't
override it, unless set_style replaces entirely). We need to define
whether set_style does a full replace or merges; likely it sets/merges.
Our test can verify that behavior: e.g., after set_style, color is
\"#00ff00\" (if we changed it) or remains old value if we only set
width. - Setting style on a non-existent object ID should raise an
error. Test that calling set_style with an invalid ID triggers a
KeyError or similar. - Test that styles don't affect geometry: e.g.
changing color or line width should not alter object's shape. We can
indirectly check that by calling geometry evaluate or bounding box
before and after style change -- they should remain the same. - **Test
grouping and group style:** - Use `set_group("group1", ["obj1","obj2"])`
to group two
objects[\[52\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,IDs%20to%20a%20named%20group).
Then immediately call something (if available) to retrieve group
membership. The spec provides `update_group_style` but no direct
`get_group` method; however, we can infer group existence by applying a
style. So: - Call
`update_group_style("group1", {"color": "#123456"})`[\[47\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,IDs%20to%20a%20named%20group).
Then check `get_style("obj1")` and `get_style("obj2")` -- both should
now have color \"#123456\". This confirms the grouping was recorded and
the style update propagated. - Add a third object not in the group,
ensure its style remains unchanged to verify isolation. - Test updating
a group that doesn't exist: either
`update_group_style("badgroup", {...})` does nothing or raises. Likely
should raise an error (we test for that). - Test re-grouping: call
`set_group("group1", ["obj2","obj3"])` again with a partially
overlapping or new set. Likely this replaces the old membership
entirely. After this, \"obj1\" should no longer be associated with
\"group1\" (so updating group1 style now shouldn't affect obj1). We
verify by changing group style and ensuring obj1's style stays as last
set. - If nested or overlapping groups are allowed (not specified,
probably not), we would test that scenario; but we assume groups are
flat and disjoint sets identified by name. - **Test render_image
(integration light test):** This function will produce a file (image) of
the scene[\[48\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,png). We
will test it in a controlled way: - Create a simple scene (one or two
objects) and call
`scene.render_image("test.png", resolution=(400,300))`. After execution,
verify that: - A file \"test.png\" was created in the working directory
or specified path (use tmp directory in tests to avoid clutter). - The
file size is \> 0, meaning something was written. Optionally, open the
file (if we have an image library) to ensure it's a valid PNG (e.g.
check the header bytes or attempt to load it with PIL -- not strictly
necessary for QA, but a sanity check). - We won't deeply validate the
image content in an automated test (visual correctness is hard to assert
automatically without a reference image). However, we could do a weak
check: render an image with known background color (e.g. white) and one
black circle, then sample a few pixels in the center of where the circle
should be (if we have an image diff tool or PIL) to see if they are
black. This would verify that at least the object drew. But such
pixel-level tests might be brittle and rely on external libs, so we keep
them optional. - If rendering depends on external headless modes (like
matplotlib or ThreeJS via an offscreen canvas), ensure the test
environment is configured for it (e.g. use Agg backend for matplotlib).
The test should not hang or crash if no display is present. - Also test
the optional bbox parameter: if we pass a bbox to `render_image`,
ideally the image should zoom into that region. We can verify
indirectly: render the full scene vs render with a tight bbox around an
object -- if the object appears larger in the second image (we could
compare file sizes or histograms as a rough proxy), it suggests zooming
worked. This is a stretch goal for automation; basic existence and
no-error is primary. - **Test render_animation (integration):** This is
more complex, but we can still test the mechanism: - Define a trivial
`animate_fn(frame:int)` that, say, rotates a parameter or toggles a
style. For a simple test, let `animate_fn(i)` for frame i just set
object1's color to a gradient (different each frame) or moves an
object's center slightly. Use `frames=5`. - Call
`scene.render_animation("test.gif", frames=5, animate_fn=animate_fn, resolution=(200,200))`.
After execution, verify \"test.gif\" is created and has a non-zero size.
If possible, use an animated image reader to ensure it has 5 frames
(this might be done by reading the GIF header, which contains number of
frames). We could use PIL's imageio or similar in tests to verify frame
count matches. - Ensure that animate_fn was called the correct number of
times (5 times, once per frame). We can instrument animate_fn to
increment a counter or log calls. The test can assert the counter ==
frames count, confirming that the SceneManager correctly iterated the
frames. - If the animation generation uses a lot of time or resources,
mark the test as slow. We can generate a very low-res GIF to speed it up
(e.g. 100x100). - As with images, we won't verify visual content deeply,
just existence and frame count. This test ensures that the integration
of animating and rendering doesn't throw exceptions and produces
output. - **Test save_scene and load_scene (Persistence):** This is
critical for round-trip reliability: - Populate a scene with a variety
of objects: a primitive curve, a composite, an area region with a field,
some custom style on one, a group linking two of them. Call
`scene.save_scene("scene.json")`[\[51\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60save_scene%28filename%3A%20str%29%20,format).
Verify that a file \"scene.json\" is created. Open and parse the JSON:
\* It should have a top-level \"objects\" dictionary, with each object
ID as
keys[\[37\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=JSON%20Scene%20Format%20%60%60%60json%20,c2).
Check that all added object IDs appear. For each object, verify the
\"type\" is correct (e.g. \"ImplicitCurve\" or specific subclass name),
and \"data\" and \"style\" keys exist. The data should correspond to the
object's definition (we might not deeply assert all numbers, but ensure
it's not empty and keys like equation or points are present). Style
should match what was set for that object (or default if none). \* If
groups exist, there should be a \"groups\" dictionary mapping group
names to lists of
IDs[\[53\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%7D%2C%20,%7D).
Check that our group \"group1\" is listed with the correct members. -
Now instantiate a new SceneManager, call
`load_scene("scene.json")`[\[54\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60load_scene%28filename%3A%20str%29%20,disk%20and%20restore%20all%20objects).
After loading: \* Check that `list_objects()` on the new scene returns
the same IDs as the original scene. For each, verify the object type is
preserved (e.g. get_object returns an object of the correct class, or at
least one with the same to_dict as original). \* Verify critical
attributes: for a curve, evaluate it at a point and ensure it matches
original's evaluation; for a field, perhaps compare a few sample values;
for styles, use get_style to ensure the color/width persisted; for
groups, re-run `update_group_style` on the loaded scene and ensure it
affects the same members, confirming group info was restored. - Test
`.scene.py` save if implemented. `save_scene("scene.scene.py")` should
produce a Python script. We can `exec` it in a sandbox where we
pre-import the necessary classes (as indicated in the file header). The
script is expected to recreate a scene object named e.g.
`scene`[\[38\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Python%20,0ff%22%7D%29%20scene.save%28%22scene.json%22%29).
After `exec`, we retrieve that `scene` and perform similar checks:
object list, types, sample geometry tests. This ensures the script is
valid and effective. - Error handling: try loading from a nonexistent
file (should raise IOError or similar, test for that). Try loading a
malformed file (e.g. pass a path to a text that isn't proper JSON/scene)
and ensure it raises a clear exception, not a silent fail.

**Edge Case & Failure Mode Tests:** *(Robustness of SceneManager in edge
conditions.)* - **Duplicate IDs and Naming Conflicts:** As mentioned,
adding an object with an existing ID should be handled. We test the
policy: likely raising an error to prevent accidental overrides.
Similarly, test adding a group name that already exists -- does it
replace the old group or error? We define expected behavior (probably it
replaces or updates membership, which is essentially what set_group
does). If there\'s a possibility of ID collision with group names
(shouldn't be, separate namespaces), ensure no mix-ups (probably not an
issue). - **Removal Side Effects:** Remove an object that doesn't exist
(already tested) and remove an object that is part of a group. We expect
it to be removed from the scene's object registry; we should also
consider if group references remain. Ideally, SceneManager should
internally clean up group memberships by removing that ID. We can test
by grouping objects, removing one, then doing a group style update and
confirming no error and that the removed object didn't somehow still get
updated or leave a dangling reference. - **Invalid Operations:**
Instruct the SceneManager to do something invalid and ensure graceful
handling: - E.g., `update_group_style("groupX", style)` where \"groupX\"
doesn't exist -- should raise a KeyError or internally ignore with a
log. Our test expects a KeyError (to signal misuse). -
`handle_mcp_command` with an unknown command or malformed data (we will
cover MCP testing separately, but at the SceneManager level, handle_mcp
should ideally validate commands). Test by calling
`handle_mcp_command({"command": "nonexistent"})` and expect a result
indicating failure (could be an exception or a returned dict like
`{"error": "Unknown command"}`). This ensures the system is robust to
bad input via that interface. - **Concurrency Considerations:** If the
design anticipates multiple agents or threads, we might simulate
simultaneous modifications. This is complex to do reliably in unit
tests, but we can add a test using Python threads: e.g. start two
threads that both add different objects to the scene at the same time.
After they join, verify both objects are present and nothing got
corrupted. If the SceneManager is not thread-safe by design (likely
single-thread in Python), this test might be more of a theoretical check
-- so we could instead enforce that it should not be called from
multiple threads by design. For now, likely skip actual concurrency but
mention that if multi-agent collaboration (with WebSockets) is
introduced, we'd add tests for consistency under concurrent events
(perhaps using locks and events in tests). - **Large Scene Handling:**
Populate a scene with a large number of objects (say 1000 simple curves)
programmatically and then call save_scene to ensure performance and that
file is written. This test would assert that the operation completes
within some time and that load_scene can handle reading it back. Not a
typical unit test, but a stress test we can include offline to validate
scaling. If any specific limits (like max objects) exist, tests should
cover approaching those limits and ensure graceful degradation or
documented failure.

**Persistence Testing:** (Already covered in functional tests for
save/load, but summarizing) - **Round-trip integrity:** We extensively
test that saving and loading yields an identical scene (object geometry,
styles, groups all preserved) using both JSON and Python
formats[\[37\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=JSON%20Scene%20Format%20%60%60%60json%20,c2)[\[38\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Python%20,0ff%22%7D%29%20scene.save%28%22scene.json%22%29). -
**Versioning and Compatibility:** If the scene format evolves, include
tests for backward compatibility. For example, keep a known older JSON
scene file (as a static test resource) and test that `load_scene` can
still import it correctly. Similarly, if `.scene.py` format changes
(unlikely except adding new object types), have tests to ensure old
scripts run or produce a meaningful error. - **Partial Load:**
Intentionally manipulate a saved JSON (in a copy) to remove or corrupt
one object entry, then test that load_scene either skips the broken
entry with a warning or raises a descriptive error. This verifies that
the system doesn't crash mid-load and handles file errors. We will
assert the expected behavior (perhaps an exception that indicates which
object failed to load, or a return value indicating failure).

**Regression Test Mechanism:** We will add specific tests for any bugs
discovered in the scene management: - For instance, if there was a bug
that `objects_in_bbox` missed objects on the boundary, we'd write a test
case with such a scenario to ensure it now includes boundary
intersections. - If saving a scene with certain complex objects (like
nested composite) previously lost data, after fixing we add a test that
creates that scenario and asserts the JSON contains the expected data
and reloads correctly. - If an MCP command caused an incorrect internal
state (say a create followed by delete left a dangling reference in
group), we craft a sequence of calls in a test to reproduce the issue
and then verify the state is consistent (like group membership cleaned
up). - We maintain these as part of the SceneManager test suite or a
separate regression suite. Each test will cite the context of the bug in
comments (for maintainers) and ensure that the particular edge condition
is now covered in future runs.

By adopting test-first, many potential regressions will be prevented,
but if any slip through, the act of writing a new test for each ensures
our test coverage continually grows alongside bug fixes.

## MCP Command Processing Testing

**Overview:** The Model Context Protocol (MCP) is a JSON-based command
interface that allows an external agent (AI or other frontend component)
to inspect and modify the
scene[\[55\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=To%20support%20an%20intelligent%20agent,create%2C%20or%20modify%20scene%20objects).
Supported commands include creating objects, updating parameters,
setting styles, deleting objects, grouping,
etc.[\[56\]](file://file-L1NAzSR2zK6jK7kTr4wjku). The frontend will call
a dispatcher (e.g. `dispatchMCP(command)`) which in turn invokes
`SceneManager.handle_mcp_command` or equivalent to perform the
action[\[57\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=,). Our test
strategy for MCP focuses on verifying that each command is parsed
correctly, the appropriate SceneManager methods are called, and the
intended side effects occur both in the backend and (where applicable)
in the UI. We treat MCP handling as a layer above the core API, so tests
here ensure the **mapping and integration** works as expected,
independent of whether the command came from an AI or UI.

**Testing Framework:** We will treat MCP command tests as integration
tests between the command parser/dispatcher and the SceneManager. In
Python, we can write tests that directly call `handle_mcp_command` with
a dict (simulating a parsed JSON). If there is a separate parser (e.g.
if commands were text or needed validation via Pydantic), we'd test that
as well -- possibly using the **pydantic models** if defined (the
CAD-MCP reference suggests using a library for model validation). Pytest
will be used; fixtures can provide a fresh SceneManager with a couple of
default objects to operate on for certain tests. We may also include
tests on the front-end side by simulating the dispatch, but those will
be mentioned in UI testing -- here we focus on the backend command
handling results.

**MCP Command Functional Tests:** *(Verify each supported command's
effect.)* The mapping from MCP command to SceneManager action is defined
in the
specification[\[58\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=These%20commands%20map%20to%20,methods);
we will create test cases for each:

- **create_object command:** Prepare a command dict, for example:

<!-- -->

- {"command": "create_object", "id": "curve1", "type": "Circle", "args": [0,0,5], "style": {"color":"#0f0"}}

  (Exact schema may vary; assuming it includes an id or type and any
  needed parameters to instantiate.) Invoke `handle_mcp_command(cmd)`.
  Verify:

<!-- -->

- The result returned is correct. Possibly `handle_mcp_command` returns
  a confirmation or the created object's data. If the design is to
  return the object's description (like its to_dict or ID), test that
  the response contains expected fields (e.g.
  `{"status":"ok","id":"curve1"}` or perhaps the full object dict if
  designed so).
- The scene now contains the new object: `scene.get_object("curve1")`
  returns a valid object of type Circle with radius 5 (for instance).
  Also check that if a style was provided, `scene.get_style("curve1")`
  reflects it.
- If the command omitted the `"id"` (meaning the system should
  auto-generate an ID), then verify that the response includes the
  generated ID (and it appears in scene). The UI spec's naming strategy
  suggests the UI usually generates
  names[\[59\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=Every%20newly%20created%20object%20%E2%80%93,being%20unique%20in%20the%20scene)[\[60\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,to%20produce%20a%20unique%20variant),
  but if MCP allows creation without specifying ID, our test would
  ensure an ID was assigned (perhaps the SceneManager could ask UI or
  use a default scheme). This is an integration detail; likely, for
  simplicity, the agent will provide an ID. Our tests will cover both:
  providing an ID vs not providing (if supported).
- Error cases: try a create_object with a duplicate ID (should fail with
  an error response indicating ID conflict), and with an invalid type
  name (should fail, e.g. unknown object type). We assert that the
  returned result contains an error message or code, and that no new
  object is added to the scene in those cases.
- **delete_object command:** First, ensure an object exists (we can
  reuse the object from above or create one). Form command:
  `{"command": "delete_object", "id": "curve1"}`. After
  `handle_mcp_command`, verify:
- The object is removed from the scene (`scene.get_object("curve1")` now
  yields None or not found).
- The response indicates success (maybe `{"status":"ok"}` or similar).
- If that object was part of a group or had other dependencies, ensure
  those are handled. For example, if \"curve1\" was in a group, the
  SceneManager might implicitly update the group. There\'s no explicit
  mention of that, but our test can check that after deletion, calling
  `update_group_style` on the group doesn't try to update the deleted
  object (no error occurs). Essentially, deletion should leave the scene
  in a clean state.
- Test deletion of non-existent ID: expect an error response (e.g.
  `{"error": "Object not found"}`) and no change in scene. The test will
  call handle_mcp_command on an unknown ID and assert the error.
- **describe_object command:** Assume an object \"curve1\" exists.
  Command: `{"command": "describe_object", "id": "curve1"}`. The
  expected result would be a description of the object. According to
  mapping, it likely uses `get_object()`
  internally[\[61\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,curve%2Ffield).
  Since `get_object` returns the object instance, the MCP handler
  probably converts it to a serializable form (perhaps via `to_dict()`).
- Our test will check that the response contains the key details of the
  object: e.g.
  `{"id":"curve1", "type":"Circle", "parameters": {...}, "style": {...}}`
  or something similar. If the design is to send the full object
  metadata, we verify fields like equation or radius appear.
- Also test describing an unknown ID: should return an error or empty
  result. Confirm that it does not crash.
- **update_parameters command:** This one is critical for dynamic
  editing. Create an object (e.g. a curve with a parameter) or use an
  existing one with known parameters. For example, if \"curve1\" is a
  circle with radius 5, command:

<!-- -->

- {"command": "update_parameters", "id": "curve1", "parameters": {"r": 3.5}}

  Call `handle_mcp_command(cmd)`. Verify:

<!-- -->

- The object's parameters have indeed updated. In this case,
  `scene.get_object("curve1")` (which might return an ImplicitCurve)
  should now reflect r = 3.5. How to check? If the object stores the
  expression, evaluate at a point that was on the old circle's boundary:
  (5,0) was on the old boundary (f≈0), now with r=3.5, evaluate(5,0)
  should be \>0 (outside), whereas (3.5, 0) should now be ≈0. We perform
  such an evaluation in the test to confirm the parameter took effect.
- Alternatively, if the object has an attribute or method to get
  parameters (not defined, but some objects might), use it to inspect r
  directly.
- The response should indicate success, possibly returning the updated
  object description or a confirmation. We verify that no error is
  present in the response.
- Edge: Update with a parameter that doesn't exist for that object (e.g.
  {\"foo\": 1.0} on a circle). The system should likely ignore unknown
  parameters or error. Ideally, it errors to signal misuse. Test that an
  appropriate error or rejection occurs and that the object remains
  unchanged.
- Update parameters on an object type that can't be parameterized (say a
  fixed shape with no params). This should probably just do nothing or
  error. If a Field object had no "r" parameter, updating "r" might not
  apply; ensure the system responds gracefully (maybe "unrecognized
  parameter").
- **set_style command:** Use an existing object. Command:
  `{"command": "set_style", "id": "curve1", "style": {"color": "#0000ff", "dash": [5,5]}}`.
  After handling:
- Check that `scene.get_style("curve1")` reflects the updated style
  (color now blue, dash pattern
  set)[\[45\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,style%20dictionary%20for%20an%20object).
- Possibly the SceneManager's handle might just call its own
  `set_style`, which we already test works, so this is verifying the
  glue. Ensure the response indicates success (maybe returns the new
  style or just ok).
- If the object ID is invalid, test that an error is returned (and style
  of no object isn't created or anything).
- If style keys are invalid (suppose we pass a key the system doesn't
  use), likely it just stores it anyway since style is a free dict. Not
  much to test unless we have validation on styles.
- **group_objects command:** Example command:
  `{"command": "group_objects", "group_id": "grp1", "objects": ["curve1","curve2"]}`.
  (We assume the agent provides both group_id and list; if not, maybe it
  could just group currently selected objects, but given the mapping,
  likely explicit.)
- After handling, check via SceneManager internals that group \"grp1\"
  exists. We can indirectly verify by using
  `update_group_style("grp1", {...})` and seeing it affects those
  objects as tested before. Or if handle_mcp_command for group creation
  returns something, maybe it returns group id.
- Ensure both objects are now associated with the group. If we had a way
  to query group membership (perhaps via `describe_object` which might
  list group membership, but not specified), we could check that.
  Alternatively, apply a style to one and see if group style overrides
  it later -- but that's already above. So main check is that no error,
  and future ops on that group work.
- If the command omitted a group_id, maybe the system auto-generates one
  (less likely; group id should probably be specified). If auto-naming
  groups is a feature, test it by calling group_objects without
  specifying group_id and expect a returned generated name (like
  \"Group1\"). If not supported, our test ensures the command fails
  gracefully if required fields are missing.
- Test grouping with some invalid object IDs in the list -- should
  either ignore those or error. We'd likely want it to error to avoid
  silent partial grouping. Confirm the chosen behavior.
- **set_field_strategy command:** This would apply to an `AreaRegion`
  object to change how its field is
  generated[\[62\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,not%20handled%20by%20SceneManager).
  To test:
- Ensure we have an AreaRegion in the scene (maybe created earlier or
  via create_object if type supports \"AreaRegion\"). Then command:
  `{"command": "set_field_strategy", "id": "region1", "strategy": "SignedDistance"}`
  (or some identifier of strategy and parameters if needed).
- After `handle_mcp_command`, verify the target object's field strategy
  changed. For example, call areaRegion.field(x,y) at a point and see
  that it now behaves as a signed distance (continuous values) whereas
  previously it might have been occupancy. If we had a direct way to get
  the strategy class, even better: e.g. check
  `isinstance(region.field_strategy, SignedDistanceStrategy)`.
- Try another: set_field_strategy to \"OccupancyFill\" with certain
  inside/outside values. Then maybe immediately sample the field or call
  region.fill() and inspect results (1s and 0s as expected).
- Invalid uses: calling set_field_strategy on an object that is not an
  AreaRegion (like a simple curve) -- the system should respond with an
  error ("cannot set field strategy on non-region"). Test that scenario
  to ensure it doesn't silently succeed.
- **set_view command:** The spec says `set_view` (for changing viewport)
  is *not handled by
  SceneManager*[\[63\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,not%20handled%20by%20SceneManager).
  If an MCP command `set_view` is received, it might be handled entirely
  on the front-end. Our strategy:
- The SceneManager's `handle_mcp_command` might either ignore it or
  return a "not handled" response. We test that calling
  `handle_mcp_command({"command":"set_view", ...})` results in either a
  no-op response or a specific error like "unsupported command" (unless
  by the time of implementation they decided to handle view
  differently).
- This test is to ensure unimplemented commands are acknowledged and do
  not cause crashes.

In addition to individual commands: - **Sequence and stateful
scenarios:** Test a realistic sequence of commands to ensure state
transitions are consistent: - Example scenario: 1. create_object
(curve1). 2. create_object (curve2). 3. group_objects (grp1 with
\[curve1, curve2\]). 4. update_parameters on curve1. 5. set_style on
grp1 (change color for both). 6. describe_object on curve1 (to verify it
reflects updated param and new style). 7. delete_object curve2. 8.
describe_object on curve2 (should error or indicate not found). 9.
group_objects (grp2 with \[curve1, curve2\]) perhaps, to see how
deletion was handled (curve2 was deleted, so maybe grp2 ends up just
with curve1 or error). - Write a test executing this sequence via
multiple handle_mcp_command calls. Verify after each step the expected
outcome (we've mostly covered each individually). This end-to-end use
case ensures that a chain of MCP operations leaves the SceneManager in a
valid state. It's essentially simulating an agent doing tasks and making
sure nothing breaks in between (like trying to group including a deleted
object). - **Error and Validation Testing:** Ensure the MCP interface is
robust to bad input: - Commands with missing fields (e.g. an
update_parameters with no \"parameters\" key, or create_object missing
\"type\") should be validated. If using Pydantic or schema, such a
command might be rejected before handle_mcp_command logic. We simulate
this by calling handle_mcp_command with incomplete dict and expecting an
error response or exception. - Commands with wrong data types (e.g.
parameters expecting a number but a string given) should also be caught.
If our implementation uses data classes or manual checks, confirm that
an informative error is returned. - Security: Although not primary here,
since MCP could come from external, ensure that malicious or extremely
large inputs are handled (e.g. a command with a million points in an
object definition should be refused or handled within memory safely --
this might be more of a limit test). - **MCP Response Format:** Our
tests will also enforce that all MCP responses follow a consistent
format. If we define that every response has either a `"status": "ok"`
or `"error": "message"` field, tests will check for those. For query
commands like describe, the response may include data; test that it's
structured (e.g. under a `"object": {...}` field). By verifying response
format, we ensure the agent (or UI) can reliably parse results.

**Validating UI State Changes via MCP:** Since MCP ultimately drives UI
updates, we include tests that bridge to the UI (these are integration
tests across backend and frontend): - We simulate an MCP command coming
in and then verify that the UI layer reflects it. One approach is to
have a **mock UI listener** or use the optional WebSocket mechanism. For
example, after a `handle_mcp_command(update_parameters)` on the server,
if a WebSocket message like
`{"event": "object_updated", "id": "curve1", "object": {...}}` is
supposed to be sent to
clients[\[64\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=), we test
that our server indeed produces this message. We can instrument the
SceneManager or a stub WebSocket to capture outgoing events. In a test,
after issuing the command, check that the captured event matches the
updated object data (e.g. new parameters and
style)[\[65\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=%60%60%60json%20%7B%20,ff0000%22%7D).
This ensures the backend notifies the UI properly. - On the UI side
(which we will detail in the next section), we would test that given
such an event or by directly calling the UI's dispatch function, the
visible state changes. For MCP testing, we can at least confirm the
backend's role: that every state change (create, update, delete) yields
the correct effect that the UI can observe (either through query or push
event). - For instance, after a create_object command, the backend might
not push anything if the UI itself initiated it (UI already knows). But
if an agent on backend did, and WebSocket is used, a `object_updated` or
`object_created` event might be sent. We verify that as part of our MCP
test suite. - Similarly, test that if multiple commands are issued
rapidly (like 10 create_object commands), the system can handle them
sequentially and each results in correct state and event outputs. This
is more of a stress test on command processing reliability.

By treating MCP as an independent layer, our tests double-check that the
**contract between an AI/UI and our system** is solid. We verify that
for every documented
command[\[66\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Supported%20MCP%20Commands),
the system performs the right internal calls (as we tested in
SceneManager) and returns or broadcasts the expected results, thus
ensuring any MCP-based control (like an intelligent agent or a script)
will work reliably.

## UI (Front-End) Testing Strategy

**Summary of UI Functionality:** The front-end UI for the 2D implicit
sketching application is a rich interactive interface (likely a web
interface using ThreeJS, etc.) that allows users to create and
manipulate objects, and also reflects changes driven by the backend or
an AI
agent[\[67\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=This%20document%20outlines%20a%20comprehensive,scene%20management%2C%20MCP%20agent%20control).
Key UI features include: - A **graphics canvas** where implicit curves
and fields are rendered and can be
panned/zoomed[\[68\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.1%20Graphics%20Canvas%20,field%20values%20under%20cursor%2C%20etc).
Users can select objects, use context menus for editing, and see visual
annotations (grid, handles, etc.). - **Panels and menus:** for listing
objects by category, adjusting parameters, editing equations, and
applying
styles[\[69\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.2%20Object%20Category%20Panels%20,Visibility%20toggle)[\[70\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=3).
There are controls for global actions like save/load, undo/redo,
animation,
etc.[\[71\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.4%20Global%20Controls%20,Help%2Fdocs%20access)[\[72\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=5.1%20Animation%20Panel%20,Manual%20frame%20stepping). -
**Naming and identification:** New objects get unique fun names (like
\"WobbleLoop\") by
default[\[59\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=Every%20newly%20created%20object%20%E2%80%93,being%20unique%20in%20the%20scene),
and users can rename them with uniqueness
enforced[\[60\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,to%20produce%20a%20unique%20variant). -
**MCP integration:** The UI listens for or dispatches MCP commands. It
has an internal dispatcher to handle incoming commands (e.g., from an
AI) and update the UI state
accordingly[\[73\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6.2%20MCP%20Support%20,Optional%20command%20console%20for%20developers).
It may also provide a developer console to manually input
commands[\[74\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6.2%20MCP%20Support%20,Optional%20command%20console%20for%20developers). -
**Persistence in UI:** The UI triggers save/load (likely by invoking
backend, then updating UI), and possibly autosaves to local
storage[\[75\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6). - **No
heavy logic in UI:** Many computations (curve extraction, etc.) are done
client-side as per
design[\[76\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Client), so
the UI includes a math engine and maybe a marching squares for real-time
curve updates. This implies some pure functions in UI (like evaluate
expressions or generate polyline) that can be unit-tested in isolation.

Testing the UI is inherently more challenging than backend because it's
event-driven and visual. We aim for a **lightweight strategy** focusing
on unit testing key logic (without needing a browser UI automation for
every feature), and integration testing via simulated events and state
inspection. We avoid complex UI automation tools (like Selenium) due to
maintenance overhead; instead we will use instrumented code and targeted
checks:

**Suggested Testing Framework (Front-End):** Use **Jest** (for a
React/TypeScript app or even plain TS modules) to run unit tests in a
Node environment with jsdom as needed for DOM interactions. Jest is
lightweight and can simulate DOM events. If the UI is not using a
framework with virtual DOM, we might use **Playwright or Cypress** for a
small number of end-to-end tests on actual browser contexts, but the
core approach is to attach test hooks and use logging to verify
behavior. The UI code should be written in a testable way: e.g.,
separating the rendering logic (ThreeJS scene graph updates) from
higher-level state management, so we can call state management functions
in tests and assert outcomes.

**Unit Test Cases for UI Logic:** *(Test non-visual logic in
isolation.)* - **Test object name generation:** There should be a
function or module responsible for generating unique
names[\[59\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=Every%20newly%20created%20object%20%E2%80%93,being%20unique%20in%20the%20scene).
We will unit test this: - Call the name generator when no names exist;
ensure it produces a string that matches the pattern (e.g. adjective +
type hint, like \"WobbleLoop\"). Since it\'s somewhat random or from a
list, we can at least assert it's a non-empty string and maybe that it
contains a type keyword (\"Loop\", \"Field\", etc. as per
spec[\[77\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=or%20descriptors%20with%20object%20type,being%20unique%20in%20the%20scene)). -
Simulate a scenario where that generated name already exists in the
registry. The next call should tweak the name (like append a number or
choose a different
descriptor)[\[60\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,to%20produce%20a%20unique%20variant).
We can preload the registry with \"WobbleLoop\" and see that the next
name is \"WobbleLoop2\" or a variation. Assert that the new name is
unique and still respectful of format. - Test user renaming: if there's
a function `renameObject(id, newName)`, call it with a duplicate name
(that another object has) and ensure the UI rejects it or alters it
(likely the UI will warn and not accept until
unique[\[60\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,to%20produce%20a%20unique%20variant)).
In a test, we might simulate the rename event and check that the
object's name did not change to a duplicate (and maybe that an error
message was set in state). If the UI offers suggestions for uniqueness,
test that behavior if it's implemented. - **Test UI parameter binding:**
The UI includes parameter sliders and live updates of curves when
parameters
change[\[78\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=3.1%20Object%20Inspector%20Panel%20,Area%20boundary%20listing%20and%20editing).
Likely, the UI has a function that handles parameter slider input for an
object. - We test that adjusting a parameter control calls the
appropriate update function. For instance, simulate a slider change
event for "r = 5 -\> 6" on a circle. The UI should update the internal
parameter state *and* trigger a re-computation of the curve geometry in
the client (since math.js in browser can re-evaluate
equations[\[76\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Client)). -
To test that, we can stub the math evaluator or marching squares: e.g.,
have the test inject a fake `math.evaluate` and verify it was called
with the new expression and parameter. Or if the UI calls
`dispatchMCP({"command":"update_parameters", ...})` to backend for such
changes, we verify that function was called with correct JSON (ensuring
UI properly formats outgoing MCP messages). - If UI does local updates
without roundtrip for speed, then test that after slider change, the
in-memory representation of the curve's points is updated. Possibly the
UI stores the polyline in a state -- we simulate input and then read
that state to ensure it's changed. (This may require the UI code to be
structured to allow inspection of state outside the DOM, e.g., using a
model class or a state store). - **Test object creation flow
(UI-side):** When a user creates a new object via the UI (e.g. clicking
\"Add circle\" in the canvas
menu[\[79\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,view%2C%20show%20grid%2C%20frame%20all)): -
Verify that the UI triggers the correct action: This might be an MCP
command to the backend (`create_object` with specified type). We can
intercept the function that sends commands (say `sendMCPCommand`) by
mocking it in a test. When the user action is simulated, we expect
`sendMCPCommand` to be called with, for example,
`{"command":"create_object","type":"Circle","id":someId,...}`. The
someId might be generated by UI's naming logic; we ensure it\'s included
and unique. - After sending, the UI likely will optimistically add the
object to its local list with a temporary state (or wait for
confirmation). We test that the UI's object list (the state that drives
the Object
Panels[\[69\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.2%20Object%20Category%20Panels%20,Visibility%20toggle))
increases by one and contains an entry with the new name/type. We can
simulate the backend response as well: pretend `handle_mcp_command`
returned success; our UI code might then finalize adding the object (if
it wasn't already). We verify that the object appears in the appropriate
category panel in the state (e.g., a new entry under \"Conic Curves\" if
it's a circle). - If the UI draws the object immediately using local
math (which design suggests it can for
responsiveness[\[76\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Client)),
test that the ThreeJS drawing function was called. This can be done by
mocking ThreeJS methods: e.g., stub `THREE.Line` or the rendering
routine to record that it was invoked with certain geometry points. For
instance, after adding a circle, the UI might call something like
`scene.add(new THREE.Line(curveGeometry, material))`. We can intercept
this by injecting a fake `scene.add` or `THREE.Line` in test and verify
it\'s called. This ensures the UI attempted to visualize the new
object. - **Test UI actions via context menu:** The UI spec lists
context menu options like edit, delete,
duplicate[\[80\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.3%20Contextual%20Menus%20,view%2C%20show%20grid%2C%20frame%20all).
We can test a few critical ones: - Simulate a user right-clicking an
object and choosing \"Delete\". The UI should then call the deletion
logic, which likely goes through MCP (`delete_object`). As with
creation, we intercept that the correct command is sent to backend with
the right ID. Also verify the UI immediately removes the object from its
list (maybe only after backend confirms? Depending on implementation;
some UIs optimistically remove, others wait for ack. We assume immediate
removal for responsiveness). - If available, simulate \"Duplicate\":
that might internally create a new object with a similar shape. It could
either copy locally and then send a create command or ask backend to
duplicate. Test that a create command for a new object (with a new
id/name) is issued when duplicate is invoked, and that the UI shows the
new object. - Simulate \"Rename\" via context or double-click: call the
UI function that sets a new name for an object. If the UI interacts with
backend for renaming (maybe not, name might be just UI-side until
saved), ensure uniqueness check as earlier tested. Verify that the
object list reflects the new name after the action. - **Test Undo/Redo
(if implemented):** If the UI has undo/redo in the
toolbar[\[71\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.4%20Global%20Controls%20,Help%2Fdocs%20access),
this likely ties into command history. A lightweight test: perform a
couple of actions (create object, change parameter), then call the undo
function in UI. Verify that the UI state reverts: the last change is
undone (the object removed or parameter back to old value). This might
involve simulating multiple MCP commands and then triggering an \"undo\"
command -- possibly an MCP command itself or an internal state rollback.
Check that after undo, the scene state in UI matches expected (and
possibly that an \"undo\" MCP or internal event was sent to backend if
needed). Redo similarly. - **Test Save/Load from UI:** This might not be
fully automatic, but we can simulate clicking \"Save Scene\" (which
probably triggers `scene.save_scene` via an API call or MCP). If
there\'s a function like `saveScene()`, we mock the backend call it
would make (e.g. an HTTP POST or MCP command). Test that it calls it and
perhaps that UI provides feedback (like maybe a downloaded file or a
toast message \"saved\"). Similarly, simulate \"Load Scene\" by
providing a dummy scene JSON (if UI has file input, we might call the
handler with a known JSON object). The UI should create objects from
that data (likely by calling backend load or directly constructing local
objects). Verify that after loading, the UI's object panels show all
loaded items with correct names and properties, and the canvas has them
drawn. This is a complex integration test -- we might not fully automate
it, but at least test the UI's ability to iterate through a loaded scene
data structure and update state. - **Test MCP incoming commands (UI
side):** The UI should handle incoming commands or events from the agent
or backend (for example, if an AI agent running in the frontend calls
`dispatchMCP`, or if a remote command comes via WebSocket). We will
simulate calls to the UI's MCP dispatcher: - For instance, call
`dispatchMCP({"command": "update_parameters", "id": "curve1", "parameters": {"r": 4.0}})`
on the front-end. This should result in the UI updating the object's
display. In our test environment, after calling dispatchMCP, we check
that: \* The underlying data model for \"curve1\" (perhaps an entry in a
state store) now has the new parameter value (r=4.0). If the UI stores
the equation or parameters in state (like in a form), that should
update. \* The canvas representation of \"curve1\" should be updated --
likely the UI will recompute the curve's polyline with the new radius.
We can intercept the drawing function or check that the data driving the
ThreeJS object has changed. For example, if the UI code updates the
geometry of the existing ThreeJS line, we could check that the bounding
box of that geometry expanded from radius 3.5 to 4.0. If direct
inspection of ThreeJS objects is hard, we again rely on logging or an
event: maybe the UI logs \"Updated curve1 parameter r to 4.0\". We can
capture logs or emitted events for verification. - Simulate an incoming
`create_object` command (as if the agent told the UI to add something).
In test, call
`dispatchMCP({"command":"create_object","id":"agentCurve","type":"Circle","args":[...],"style":{...}})`.
The UI should then add this new object to its state (similar to
user-initiated create). Check that it appears in object list. Also,
because this is from an agent, the UI might treat it differently (maybe
highlight it or something, but not specified). We primarily ensure it\'s
added and drawn. If the UI needs to confirm with backend, presumably the
agent is the source, so maybe dispatchMCP directly calls SceneManager in
an embedded scenario. In any case, our test ensures UI can handle
externally triggered addition. - Simulate a `set_style` command from
external (change color of an object). After dispatchMCP, verify the UI
updated the object's color swatch in the panel and the object's material
color on the canvas. We can test the panel by checking the state (e.g.
an object's style color field updated). For the canvas, we might check
that the ThreeJS material color property was set to the new value. If
the UI code calls something like
`objectMesh.material.color.set(newColor)`, we could spy on that or check
the objectMesh properties after. - **Logging and Test Hooks:** As part
of the testing strategy, we will incorporate *test hooks* in the UI
code: for example, the UI's internal model or state store could be
exposed in a non-production mode for testing. We might have something
like `window.DEBUG_UI_STATE = uiState` that tests can read. Or we design
the UI MVC such that we can instantiate the state management in a test
and call events on it without a DOM. This would let us assert state
changes directly without needing to scrape the DOM. - We will also use
logging. For critical actions (object created, parameter updated, etc.),
the UI could log to console or a custom logger. In tests, we can capture
these logs and verify expected messages appear. For example, after an
agent triggers a color change, the UI might log \"Color of curve1
changed to \#f00\". Our test can assert that this log appears,
confirming the UI responded to the command. - We avoid pixel-by-pixel
visual testing due to complexity, but if feasible, we might include a
very basic screenshot test for the canvas: e.g., after rendering a known
scene, take a canvas screenshot and compare it to a stored image.
However, given the difficulty (rendering differences across systems),
we'll rely on state verification and trust that if the data and states
are correct, the rendering is correct (plus manual QA for visuals). -
**Manual and Exploratory Testing:** As a complement to automated tests,
we note that certain UI aspects (like user experience of dragging
handles, the feel of zoom/pan, proper layering of context menus) need
manual verification. Our strategy includes creating a **UI testing
checklist** for QA engineers to go through major scenarios: - e.g.
\"Create 5 objects, group them, delete one, ensure UI doesn't show
deleted object and group count updates.\" - \"Try renaming objects to
same name, verify error message.\" - \"Drag parameter slider to extreme
ends, ensure app doesn't freeze and curve updates smoothly.\" - This is
outside the automated test code, but we mention it to have a holistic QA
strategy.

**Lightweight Integration Testing (UI+Backend):** Without full
end-to-end tools, we simulate integration via the MCP and logging: - We
can run a headless instance of the application in a test (for example,
instantiate the SceneManager and a minimal UI controller class). Then
script a sequence: create an object via UI call, verify backend has it;
then send an MCP command via backend to update it, verify UI changed.
Essentially a ping-pong test to see that UI and backend remain in sync.
This can be done by tying our earlier tests together -- for example, use
a real SceneManager but a fake networking where UI calls
handle_mcp_command directly, then UI reads result or gets event. -
Another integration approach is to use the **optional developer
console**[\[74\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6.2%20MCP%20Support%20,Optional%20command%20console%20for%20developers).
In a test environment, if we can programmatically feed commands into
this console (or directly call the functions it would call), we can
simulate a user or agent issuing commands at runtime and verify UI
updates. The console likely just calls dispatchMCP internally. We
covered calling dispatchMCP directly, which is essentially the same
effect.

**Regression Testing in UI:** We'll adopt a practice similar to
backend: - If a UI bug is found (e.g. a case where updating a parameter
did not refresh the curve until a second action, or a certain sequence
of actions caused the object list to not update), we will write a
targeted test replicating that interaction. For example, if selecting an
object then loading a scene caused a glitch, we simulate those steps in
a test and assert the UI state is correct after the fix. - We maintain a
separate set of UI regression tests, possibly tagged, so that we can
easily run them. Over time, this builds up coverage on tricky UI state
transitions. - Visual regressions (layout or rendering differences) are
harder to catch automatically. If the project allows, we might
incorporate a visual regression tool (which takes screenshots of key UI
states and compares to baseline images). This can catch if a CSS change
breaks the layout or if the canvas fails to draw something. Given our
\"lightweight\" mandate, we might not integrate a full tool, but as a
compromise, we could use a headless browser (Puppeteer) to take
screenshots of a few known scenes. This would run maybe in nightly
builds rather than each commit. If large diffs are detected, QA can
investigate. This is optional but worth mentioning as a practice.

In summary, for the UI we prioritize **deterministic testing of logic
and state** (with Jest and functional core methods), and we lean on
**simulate-and-verify approaches** for interactive behavior using
injected test hooks and logs rather than full UI automation. This keeps
tests maintainable while still providing confidence that user actions
and MCP-driven changes will produce the correct UI state. Any critical
UI flows not covered by automation will be documented for manual
testing. By combining these strategies, we ensure the UI remains stable
and in sync with the backend as features evolve, all while avoiding the
brittleness of end-to-end GUI tests.

[\[1\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=This%20document%20defines%20a%20neutral,rendering%20library%20or%20transport%20mechanism)
[\[2\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[3\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[4\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[5\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[6\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[7\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[8\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[9\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=,%27heatmap%27%2C%20%27contours)
[\[10\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[11\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=%2A%2APurpose%3A%2A%2A%20Passes%20general,guide%20rendering)
[\[13\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=To%20support%20sliders%2C%20parameter%20drags%2C,We%20support%20this%20by%20allowing)
[\[14\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Required%20Backend%20Calls%3A)
[\[15\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[55\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=To%20support%20an%20intelligent%20agent,create%2C%20or%20modify%20scene%20objects)
[\[56\]](file://file-L1NAzSR2zK6jK7kTr4wjku)
[\[57\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=,)
[\[64\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=)
[\[65\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=%60%60%60json%20%7B%20,ff0000%22%7D)
[\[66\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Supported%20MCP%20Commands)
[\[76\]](file://file-L1NAzSR2zK6jK7kTr4wjku#:~:text=Client)
graphics_backend_interface.md

<file://file-L1NAzSR2zK6jK7kTr4wjku>

[\[12\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Exception%20and%20Error%20Handling)
[\[16\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Implicit%20Curves)
[\[17\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=2)
[\[18\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=1.%20Base%20Class%3A%20)
[\[19\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Different%20types%20of%20implicit%20curves,supported%20via%20a%20class%20hierarchy)
[\[20\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=3)
[\[21\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,)
[\[22\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=5)
[\[23\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=3.%20)
[\[24\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=4.%20)
[\[25\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=5.%20)
[\[26\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=Field%20Objects)
[\[27\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=%23%20Built)
[\[28\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%27BaseField%27%3A%20...)
[\[29\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=)
[\[30\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=def%20substitute,np.ndarray%2C%20np.ndarray%5D%2C%20np.ndarray%5D%3A%20...)
[\[31\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%28optional%20future%20method)
[\[32\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,%60contains%28x%2C%20y)
[\[33\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,signed%20distance)
[\[34\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=The%20following%20high,fields%20derived%20from%20implicit%20geometry)
[\[35\]](file://file-WWKCJr2odq5EHFrGs1fouS#:~:text=,to%20control%20tolerance%20vs%20exactness)
implicit_geometry_design.md

<file://file-WWKCJr2odq5EHFrGs1fouS>

[\[36\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%60get_bounds%28%29%20,bounding%20box%20for%20the%20object)
[\[37\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=JSON%20Scene%20Format%20%60%60%60json%20,c2)
[\[38\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Python%20,0ff%22%7D%29%20scene.save%28%22scene.json%22%29)
[\[39\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=The%20,with%20the%20MCP%20agent%20protocol)
[\[40\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,named%20object%20to%20the%20scene)
[\[41\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60remove_object%28obj_id%3A%20str%29%20,from%20the%20scene%20by%20ID)
[\[42\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60get_object%28obj_id%3A%20str%29%20,object%20associated%20with%20the%20ID)
[\[43\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60list_objects%28%29%20,IDs%20currently%20in%20the%20scene)
[\[44\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Returns%20a%20list%20of%20all,IDs%20currently%20in%20the%20scene)
[\[45\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,style%20dictionary%20for%20an%20object)
[\[46\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Returns%20the%20style%20dictionary%20associated,with%20an%20object)
[\[47\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,IDs%20to%20a%20named%20group)
[\[48\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,png)
[\[49\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=Renders%20the%20current%20scene%20to,png)
[\[50\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60handle_mcp_command%28command%3A%20Dict%29%20,command%20and%20returns%20the%20result)
[\[51\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60save_scene%28filename%3A%20str%29%20,format)
[\[52\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,IDs%20to%20a%20named%20group)
[\[53\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%7D%2C%20,%7D)
[\[54\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=%23%20%60load_scene%28filename%3A%20str%29%20,disk%20and%20restore%20all%20objects)
[\[58\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=These%20commands%20map%20to%20,methods)
[\[61\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,curve%2Ffield)
[\[62\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,not%20handled%20by%20SceneManager)
[\[63\]](file://file-3cN2y1C8W3W1RLgsqtZD2z#:~:text=,not%20handled%20by%20SceneManager)
scene_manager_interfaces.md

<file://file-3cN2y1C8W3W1RLgsqtZD2z>

[\[59\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=Every%20newly%20created%20object%20%E2%80%93,being%20unique%20in%20the%20scene)
[\[60\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,to%20produce%20a%20unique%20variant)
[\[67\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=This%20document%20outlines%20a%20comprehensive,scene%20management%2C%20MCP%20agent%20control)
[\[68\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.1%20Graphics%20Canvas%20,field%20values%20under%20cursor%2C%20etc)
[\[69\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.2%20Object%20Category%20Panels%20,Visibility%20toggle)
[\[70\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=3)
[\[71\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.4%20Global%20Controls%20,Help%2Fdocs%20access)
[\[72\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=5.1%20Animation%20Panel%20,Manual%20frame%20stepping)
[\[73\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6.2%20MCP%20Support%20,Optional%20command%20console%20for%20developers)
[\[74\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6.2%20MCP%20Support%20,Optional%20command%20console%20for%20developers)
[\[75\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=6)
[\[77\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=or%20descriptors%20with%20object%20type,being%20unique%20in%20the%20scene)
[\[78\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=3.1%20Object%20Inspector%20Panel%20,Area%20boundary%20listing%20and%20editing)
[\[79\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=,view%2C%20show%20grid%2C%20frame%20all)
[\[80\]](file://file-TZXjGHKvPJeJBfuHTZJM9E#:~:text=2.3%20Contextual%20Menus%20,view%2C%20show%20grid%2C%20frame%20all)
ui_spec_implicit_sketcher.md

<file://file-TZXjGHKvPJeJBfuHTZJM9E>
