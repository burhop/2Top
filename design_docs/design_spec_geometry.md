# Software Design Specification: 2D Implicit Geometry Module

## Overview and Purpose

The **2D Implicit Geometry Module** provides a comprehensive framework
for representing and manipulating planar curves defined implicitly by
equations $f(x,y) = 0$ . It supports exact *symbolic* computations
whenever possible (via Sympy) and falls back to efficient *numerical*
methods (via NumPy/SciPy) as needed. This module enables advanced
geometric operations such as intersection finding, smooth blending of
shapes, curve trimming, set operations (union, intersection,
difference), and conversion to scalar **fields** (e.g. signed distance
fields). The module is designed for integration into an interactive
sketching system, working in tandem with a **Scene Manager**,
**Dependency & Update Graph**, **UI**, and **Graphics Backend** to
provide real-time feedback and persistent scene management.

**Key Integration Points:** The geometry module defines core data
structures (implicit curves, composites, fields) that integrate with
other subsystems:  
- **Scene Manager:** All geometry objects can be created, referenced,
saved, and loaded through the scene manager. Every geometric object must
be serializable to a dictionary form and reconstructible (via
`to_dict()` / `from_dict()` methods) for scene
persistence[\[1\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,from_dict).  
- **Dependency & Update Graph:** Derived geometry (e.g., an offset curve
based on another curve) registers parent-child relationships in a
dependency graph. If an upstream curve changes, downstream objects are
either recomputed or marked as "broken" for user/AI
resolution[\[2\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,get_subtree).
For example, an offset curve holds a reference to its base curve and can
recalc its expression if the base is modified, or else the dependency
graph flags it for updates. The geometry module may implement helper
methods like `recompute()` on complex objects to facilitate this update
process[\[2\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,get_subtree).  
- **Graphics Backend:** The geometry module supplies the data needed for
rendering. The backend uses methods like `evaluate()` and `plot()` or
specialized interfaces to extract renderable content (curve points,
contour paths, field heatmaps,
etc.)[\[3\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=2). For
instance, a `get_curve_paths()` function in the graphics layer can
utilize `ImplicitCurve.evaluate` over a grid or param range to generate
an approximate polyline of the curve for drawing. Scalar fields (e.g.
from AreaRegion) provide `get_field_data()` for visualizing
heatmaps[\[3\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=2).  
- **User Interface:** The web-based UI communicates via high-level
commands (through a Model Context Protocol, MCP) to create and
manipulate geometry. The UI may use quick client-side approximations
(e.g. evaluating the implicit equation in JavaScript via math.js for a
**real-time
preview**[\[4\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,marching%20squares%29%2C%20WebSocket%20events))
and relies on the module's data for accurate geometry. The implicit
geometry module can provide expressions or sampled data for the UI's
preview (e.g. a string formula for math.js, or using `fill()` to get a
coarse bitmap for a curve's interior). The module's operations (e.g.,
offsetting a curve) are exposed as MCP commands (`offset_object`, etc.),
which internally call the module's functions and then notify the
dependency graph and scene manager of changes.

Overall, the module emphasizes **pure functions** and **immutability**
for ease of reasoning and AI agent coding. Methods do not cause side
effects on global state or other objects (unless explicitly noted), and
geometric objects are treated as value-like (any operation producing a
new geometry returns a new object rather than modifying inputs). All
public interfaces perform rigorous input validation and raise clear
exceptions on errors (never silent failures). The following sections
fully specify the public classes, functions, and behaviors, with
detailed method signatures, expected behavior, usage examples, and
integration notes.

## Core Concepts and Data Representation

### Implicit Curve Representation

An **implicit curve** is defined by an equation $f(x,y) = 0$ in the 2D
plane. The function $f(x,y)$ is typically a continuous scalar field:
points $(x,y)$ satisfying $f(x,y) = 0$ lie on the curve. By convention
in this module, for closed curves we treat **inside** of the shape as
$f(x,y) < 0$ and outside as $f(x,y) > 0$ . This sign convention ensures
that the gradient $\nabla f$ points outward from a filled shape (since
it points in the direction of increasing $f$ ). The module uses
**Sympy** expressions to represent $f(x,y)$ symbolically when possible,
enabling exact calculations (derivatives, solving intersections,
simplification). For numerical tasks and large-scale evaluation, the
module relies on **NumPy** arrays and vectorized functions (often via
Sympy's lambdify) to compute values efficiently.

### Class Hierarchy of Curves

Implicit curves are organized into a class hierarchy to accommodate
different families of equations and exploit their properties:

- `ImplicitCurve` -- Base class for any 2D implicit curve. Stores a
  Sympy expression and provides general methods like evaluation,
  differentiation, and plotting. This class is largely abstract;
  specific curve types derive from it.
- `ConicSection` -- Represents conic sections (ellipse, circle,
  parabola, hyperbola), i.e. implicit polynomials of degree 2. Provides
  specialized methods to classify the conic (e.g., identify ellipse vs
  hyperbola) and possibly closed-form intersection solutions.
- `PolynomialCurve` -- General implicit polynomial of any degree. Could
  provide a `degree()` method and possibly factorization or root-finding
  optimizations for polynomial systems.
- `Superellipse` -- Represents shapes defined by an equation like
  $|x/a|^{n} + |y/b|^{n} = 1$ (the superellipse family). These curves
  involve exponents and absolute values, and require careful handling of
  piecewise differentiation. They illustrate a **procedural implicit**
  shape that isn't a simple polynomial.
- `RFunctionCurve` -- Represents combinations of implicit curves via
  R-functions or smooth blending operations. This class can model
  *constructive solid geometry (CSG)* operations like union,
  intersection, and difference in a *single continuous implicit
  formula*, with optional smoothing. Internally it may hold references
  to child curves and an operation type.
- `ProceduralCurve` -- A generic wrapper for curves defined by a
  user-provided function or algorithm rather than a closed-form
  expression. For example, a curve defined by an arbitrary computation
  or imported shape. It stores a Python callable (evaluation function)
  or other description rather than a Sympy expression.

Each subclass inherits the interface of `ImplicitCurve` and may override
certain methods to provide more efficient or analytically precise
behavior. For instance, a `ConicSection` can solve its intersection with
a line via quadratic formula rather than a general numeric method. All
curve objects, regardless of type, can be used interchangeably in the
module's operations (e.g., you can blend a `Superellipse` with a
`ConicSection`, or find intersections between a `PolynomialCurve` and a
`ProceduralCurve`). Internally, the module will choose appropriate
methods (symbolic or numeric) based on the curve types.

### Scalar Fields and Regions

In addition to one-dimensional curves (the 0-level sets of $f(x,y)$ ),
the module handles **scalar fields** over the plane derived from these
implicit functions. A scalar field is just $g(x,y)$ mapping points to a
scalar value (which could be a signed distance, occupancy (0/1), or
other texture). Fields are useful for visualization (heatmaps,
contours), for offsetting and blending shapes (treating $f$ values as
continuous "density"), and for defining filled regions.

The concept of an **AreaRegion** is used to represent 2D areas bounded
by implicit curves. An AreaRegion has an outer boundary (and possibly
inner boundaries for holes) and can answer point containment queries,
compute area, and generate fields (like a signed distance field or fill
pattern) covering the region.

The module also includes **Composite Curves** made by joining multiple
curve segments end-to-end. This is useful when a complex shape's
boundary is composed of pieces of different implicit curves (for
example, an egg shape might combine part of a circle and part of an
ellipse). Composite curves and trimmed curves (partial segments of a
base curve) allow piecewise construction of shapes while still using the
implicit representation for each segment.

All numeric data in computations is handled using Python's float (double
precision) or NumPy's float arrays. Symbolic parameters (Sympy Symbols)
are used for representing expressions and can be substituted with
numeric values for evaluation or specialized (e.g., you could keep a
circle's radius as a symbol and substitute different values). Where
performance is critical (e.g., evaluating a field on a large grid, or
repeatedly computing a complex formula), the code should use vectorized
NumPy operations or even compile routines with **Numba** (if enabled)
for speed. The design prioritizes correctness and clarity, but
highlights opportunities for optimization (e.g., caching lambdify
results, using SciPy's solvers for intersections, or using Shapely for
heavy geometric computations as a fallback).

## Class Specifications and Interfaces

Below we detail each major class in the module, including all public
methods with signatures, types, and behaviors. For each method, we
specify its purpose, input parameters, return value, and any exceptions
or special cases. Example usage scenarios are provided for complex
methods to illustrate their use.

### 1. Base Class: `ImplicitCurve` {#base-class-implicitcurve}

The `ImplicitCurve` class defines the core interface for all implicit
curves. It is primarily a container for the symbolic expression and
provides methods to evaluate the expression, query its derivatives, and
produce basic visualizations. All specific curve types derive from this
class.

    import sympy as sp
    import numpy as np

    class ImplicitCurve:
        def __init__(self, expression: sp.Expr, variables: tuple=(sp.Symbol('x'), sp.Symbol('y'))):
            # Initialize with a Sympy expression defining f(x, y) = 0.
            ...
        def evaluate(self, x_val: float | np.ndarray, y_val: float | np.ndarray) -> float | np.ndarray:
            ...
        def gradient(self, x_val: float, y_val: float) -> tuple[float, float]:
            ...
        def normal(self, x_val: float, y_val) -> tuple[float, float]:
            ...
        def field(self, x_val: float, y_val) -> float:
            ...
        def plot(self, xlim: tuple[float,float], ylim: tuple[float,float], resolution: int=400):
            ...
        def to_dict(self) -> dict:
            ...
        @classmethod
        def from_dict(cls, data: dict) -> 'ImplicitCurve':
            ...
        def __str__(self):
            ...
        def __repr__(self):
            ...

**Fields/Attributes:**  
- `expression: sympy.Expr` -- The symbolic expression $f(x,y)$ whose
zero contour defines the curve. Typically in expanded or simplified form
for ease of use. This can represent any implicit equation (polynomial,
transcendental, piecewise, etc.).  
- `variables: tuple(sympy.Symbol)` -- A tuple of two Sympy symbols,
typically `(x, y)`, that are the independent variables in `expression`.
By default, the class uses global symbols `x, y = sympy.symbols('x y')`.
If a curve is defined in different coordinates (e.g., polar r, theta),
the expression can be in those symbols, but for consistency most curves
use `x` and `y`. This attribute is mainly to keep track of the symbolic
variables for substitution or serialization.

**Constructor:** `__init__(expression, variables=(x,y))`  
Initializes an ImplicitCurve with a given Sympy expression. It should
verify that `expression` is a valid Sympy `Expr` involving exactly two
symbols (the ones in `variables`). If not, it should raise a `TypeError`
or `ValueError` (e.g., if you pass a non-sympy expression or an
expression in the wrong number of variables). The expression is stored
internally. The constructor may also pre-compute certain useful values
for performance: for example, it may calculate the symbolic gradients
$\partial f/\partial x$ and $\partial f/\partial y$ and store them (or
store a lambdified numeric function) to speed up repeated evaluation.
However, such caching is an implementation detail; from the outside, the
object behaves the same.

- **Example:** Creating a simple circle curve

<!-- -->

- x, y = sp.symbols('x y')
      circle_expr = x**2 + y**2 - 1  # unit circle: x^2 + y^2 = 1
      circle = ImplicitCurve(circle_expr, variables=(x, y))

  This defines a circle of radius 1 centered at the origin, as
  $f(x,y) = x^{2} + y^{2} - 1$ . Now `circle.evaluate(0,1)` should
  return approximately 0 (on the curve), `circle.evaluate(0,0)` returns
  `-1` (inside the circle, negative as per convention), and
  `circle.evaluate(2,0)` returns `3` (outside).

`evaluate(x_val, y_val) -> float or np.ndarray`**:**  
Evaluate the implicit function $f(x,y)$ at the given point(s). This
method returns the scalar field value
$f\left( x_{\text{val}},y_{\text{val}} \right)$ . It accepts either
single floats or NumPy arrays for `x_val` and `y_val`: - If `x_val` and
`y_val` are floats (or Python numeric types), the return is a float
result. - If they are NumPy arrays of equal shape, the result is a NumPy
array of that shape, computed elementwise. Broadcasting rules should be
similar to NumPy's: e.g., a scalar `x_val` with an array `y_val` yields
an array.

**Behavior:** The method should be side-effect free and purely compute
the value. Internally, it can use Sympy's subs for single values
(slower) or use a **lambdified** function for better performance,
especially if evaluating many points. For example, the implementation
might do:

    if not hasattr(self, "_eval_func"):
        # create a fast vectorized function on first use
        self._eval_func = sp.lambdify(self.variables, self.expression, "numpy")
    return self._eval_func(x_val, y_val)

This would allow efficient array processing. If the expression involves
operations not supported by NumPy (e.g., a conditional or special
function), a piecewise evaluation or fallback to sympy's `.subs` might
be needed. The method must handle points anywhere in $\mathbb{R}^{2}$ ;
there is no domain restriction beyond those inherent to the expression
(e.g., if the expression has a square root, evaluating outside its
domain yields a complex or NaN -- such cases can either be left as NaN
or raise an error if critical). Usually, it's acceptable to propagate
NaNs or infinities from underlying math operations.

**Edge cases:** If the expression is extremely complex or evaluation
fails (Sympy could throw for certain operations), the method should
raise an exception or return numpy NaNs rather than an incorrect value.
No exceptions are typically raised for regular valid points.  
- **Example:** Using `evaluate` on different inputs

    circle.evaluate(0.5, 0.5)    # 0.5^2 + 0.5^2 - 1 = -0.5 (inside the circle)
    import numpy as np
    xs = np.linspace(-2, 2, 5)
    ys = np.linspace(-2, 2, 5)
    Z = circle.evaluate(xs[:,None], ys[None,:])  
    # Z is a 5x5 array of values of x^2+y^2-1 on a grid

In the above, `Z[i,j]` will be negative for points inside the circle,
positive outside, and zero near the boundary (within numerical
tolerance).

`gradient(x_val, y_val) -> Tuple[float, float]`**:**  
Return the gradient vector
$\nabla f(x,y) = \left( \frac{\partial f}{\partial x},\mspace{6mu}\frac{\partial f}{\partial y} \right)$
evaluated at the given point. This gives the direction normal to the
curve at that point. This method expects `x_val, y_val` as floats (we
typically do not vectorize gradient for arrays; if needed one could loop
or use vectorized derivatives).

Internally, the partial derivatives can be obtained symbolically via
Sympy: e.g., compute
`df_dx = sp.diff(self.expression, self.variables[0])` and similarly for
`df_dy` at initialization. These can then be lambdified for fast
evaluation. The method returns a tuple `(df_dx_val, df_dy_val)` of
floats. If the point $\left( x_{v}al,y_{v}al \right)$ lies exactly on
the curve, this is the normal vector (not normalized) pointing outward
(assuming the implicit is oriented with negative inside). If the point
is off the curve, the gradient is still computed (useful for distance
approximation or field analysis) -- it's just the gradient of the field
at that point.

**Special cases:** At points where the gradient is zero (e.g., a
singular point on the curve, such as the center of a lemniscate or a
cusp), the method returns `(0.0, 0.0)` or extremely small values. We
might raise a warning or handle it if needed, but typically such cases
are rare and would be handled at a higher level if at all. The user of
this method should be aware that a zero gradient means the implicit
function has a stationary point there (which on a curve indicates a
singular or non-manifold point).  
- **Example:** For the circle above, `circle.gradient(1, 0)` returns
approximately `(2, 0)` -- since
$\partial f/\partial x = 2x,\partial f/\partial y = 2y$ , at (1,0) it's
(2,0). At (0.707, 0.707) on the circle, the gradient would be roughly
`(1.414, 1.414)` (pointing outward at 45°). At the center (0,0),
gradient is (0,0) because that's a singular point for the implicit
function (though not on the curve, since f(0,0)≠0 in this case).

`normal(x_val, y_val) -> Tuple[float, float]`**:**  
Compute the **unit normal vector** to the curve at a given point. This
method first obtains the gradient at (x_val, y_val) and then normalizes
it to length 1. Specifically, it returns
$\mathbf{n} = \frac{\nabla f}{\parallel \nabla f \parallel}$ . This
vector points in the direction of increasing $f$ (outwards for closed
shapes where inside is f\<0).

If the gradient magnitude is extremely small or zero, a `ValueError` may
be raised (indicating the normal direction is undefined at that point,
e.g., at a singular point or if the point is not exactly on the curve).
Another approach is to return a zero vector (0,0) or a best-effort
direction, but raising an exception is often clearer for an undefined
normal. In general, callers should provide points on the curve if they
expect a meaningful normal; if the point is off the curve, the gradient
can be normalized anyway (giving a direction of steepest ascent of f),
but it wouldn't be exactly a curve normal unless that point is on the
level set. We can document that the user should pass a point on the
curve (i.e., f(x,y)=0) for the intended normal usage; otherwise they are
just getting a normalized gradient of the field.

**Example:** Continuing the circle example,
`circle.normal(0.707, 0.707)` (where $x^{2} + y^{2} \approx 1$ ) would
yield approximately `(0.707, 0.707)`. In fact for a circle the normal at
a point on the circle is just the radial direction. If we accidentally
call `circle.normal(0,0)`, the gradient is (0,0) so this method would
likely raise an error about zero vector normalization.

`field(x_val, y_val) -> float`**:**  
Return the scalar field value at a point. For a basic implicit curve,
this can be identical to `evaluate(x_val, y_val)`. The distinction
between `field` and `evaluate` is subtle: by convention, `evaluate`
typically refers to checking the equation (often to see if it's zero),
whereas `field` emphasizes interpreting $f(x,y)$ as a continuous scalar
field (e.g., for use in blending or distance computations). In practice,
**for** `ImplicitCurve`**,** `field(x,y)` **will just call**
`evaluate(x,y)`. This method exists to provide a uniform interface with
other scalar field objects (see the `BaseField` interface later). For
example, both an `ImplicitCurve` and a more general `Field` (like a
sampled grid) might have a `field()` method to get a scalar.

One could imagine overriding `field()` in certain subclasses: e.g., a
`Superellipse` might implement `field` to return a *signed distance
approximation* rather than the raw equation, if that were useful.
However, by default, `field = evaluate`. The return is a float (this
method is not vectorized; it expects single coordinate inputs, since
it's primarily used in contexts like point containment or distance
queries where we handle one point at a time).

`plot(xlim, ylim, resolution)`**:**  
Generate a plot or visualization of the implicit curve over a given
region. This is primarily a debugging or illustration tool, since the
actual UI rendering is handled by the graphics backend. However,
implementing `plot` is useful for quick checks and for any automated
tests that might generate images.

Parameters: - `xlim: (float, float)` -- The range
$\left\lbrack x_{\min},x_{\max} \right\rbrack$ in the plot. -
`ylim: (float, float)` -- The range
$\left\lbrack y_{\min},y_{\max} \right\rbrack$ . - `resolution: int` --
The number of sample points per axis (or per unit) to use. For example,
if `resolution=400`, the method might sample a 400x400 grid across the
specified ranges.

**Behavior:** The method should produce a visual representation of the
curve $f(x,y) = 0$ . A typical implementation would: - Create a grid of
x and y values within the limits. - Evaluate $f(x,y)$ on the grid (using
the vectorized `evaluate()`). - Use a contour-finding method to extract
the zero contour. For instance, using `matplotlib.pyplot.contour` at
level 0, or a marching squares algorithm (from `skimage.measure` or
custom). - Plot this contour on a matplotlib Axes, and perhaps fill or
color it.

If using matplotlib, one could do:

    X = np.linspace(xlim[0], xlim[1], resolution)
    Y = np.linspace(ylim[0], ylim[1], resolution)
    XX, YY = np.meshgrid(X, Y)
    ZZ = self.evaluate(XX, YY)
    plt.contour(XX, YY, ZZ, levels=[0], colors=('blue'))

This would draw the curve in blue. Alternatively, a simpler approach is
to plot a set of points satisfying $f = 0$ by scanning, but contour is
more accurate for smooth curves.

The `plot()` method might either **display** the plot directly (using
`matplotlib.pyplot.show()`), or return a matplotlib Figure/Axes for
further customization. In a headless or automated environment, returning
the Axes object is preferable so calling code can decide what to do
(e.g., save to file). We avoid heavy UI integration in this method -- it
should not depend on the system's UI.

**Note:** This method does not permanently attach the plot anywhere;
it\'s a one-time rendering. It has no side effects on the curve data. In
integration, the actual interactive UI preview might not use this
method; instead, the UI or graphics backend would sample the curve via
`evaluate` or a specialized call. But having `plot` is useful for
internal testing or documentation.

- **Example:** `circle.plot(xlim=(-2,2), ylim=(-2,2), resolution=500)`
  would create a matplotlib contour of the circle in the specified
  range. The resolution of 500 ensures a reasonably smooth circle. If
  one wanted a quick field image instead of a contour, one could modify
  `plot` to use `plt.imshow(ZZ, ...)` to show the field intensity (where
  the zero level is the boundary between positive and negative values).

`to_dict() -> dict` **and**
`from_dict(cls, data: dict) -> ImplicitCurve`**:**  
These methods handle **serialization** of the geometry object, allowing
it to be saved to disk (e.g. as part of a scene JSON) and reconstructed
later. They are critical for integration with the Scene Manager, which
saves and loads scenes by serializing
objects[\[1\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,from_dict).
The exact format can be designed for clarity and versioning. A
recommended scheme:

- `to_dict()` should produce a JSON-serializable dictionary capturing
  all information needed to reconstruct the object. Common fields might
  include:

- `"type"`: a string identifier for the class (e.g., `"ImplicitCurve"`
  or a more specific type name like `"ConicSection"`).

- `"expression"`: a representation of the Sympy expression. We cannot
  directly serialize Sympy objects, so we have options:
  - Use `str(self.expression)` which gives a string like
    `"x**2 + y**2 - 1"`. Later, `from_dict` can parse this string back
    into a Sympy expression (using `sympy.sympify` with proper symbols).
  - Or store a structured form (like polynomial coefficients), but that
    quickly gets complex for general expressions.

- `"variables"`: It might be sufficient to assume `x` and `y` (so not
  store them), but to be safe, we can store a list of variable names
  like `["x", "y"]` to reconstruct symbols.

- If the object is a subclass, include any additional parameters:
  - For `ConicSection`, maybe `"conic_type"` or parameters like center
    coordinates, etc., if easily derivable.
  - For `Superellipse`, store exponent `n` and radii `a, b` if
    available.
  - For `ProceduralCurve`, it might store a reference to a function name
    or a formula (if available) -- though arbitrary code can\'t be fully
    serialized, perhaps just an identifier.
  - For `RFunctionCurve`, store info about operands and operation (see
    below for composite structures).

- Possibly an `"id"` if the object is part of a larger structure and
  referenced by others. The Scene Manager typically assigns unique IDs
  to objects and might handle mapping, so the geometry module\'s
  `to_dict` might not include an ID by itself unless needed for internal
  references (like within a composite).

- `from_dict(data)` should be a classmethod that reads the dictionary
  and returns a new object. It will:

- Look at `data["type"]` and decide which subclass to instantiate. Often
  we implement this at the base class to dispatch: e.g., if
  `type == "ConicSection"`, call `ConicSection.from_dict(data)`, etc.
  Alternatively, each subclass registers itself in a registry.

- Reconstruct the Sympy expression: e.g.,
  `expr_str = data["expression"]`; do something like
  `x,y = sympy.symbols(tuple(data["variables"]))`; then
  `expr = sympy.sympify(expr_str, {x.name: x, y.name: y})`. This yields
  back the expression.

- Call the constructor of that class with the expression. If there were
  additional parameters stored (like `conic_type` just for info or
  special hints), use them as needed.

**Note on composite references:** For standalone curves, embedding all
data is straightforward. However, if a curve *references another curve*
(e.g., a TrimmedImplicitCurve references a base curve, or an offset
curve referencing original), we have two approaches: - *By Value:* Embed
the full definition of the referenced curve within the dictionary. This
makes `from_dict` self-contained (no external dependency) but can lead
to duplication if the base curve is also saved separately as its own
object. - *By Reference:* Store a reference (like an object ID) to the
base curve. E.g.,
`{"type": "TrimmedImplicitCurve", "base_id": 42, ...}`. This requires
that the Scene Manager or loader resolve the reference by looking up an
object with ID 42 (which must have been loaded previously). This avoids
duplicating data and preserves the identity that the trimmed curve's
base is the same object as some top-level curve.

The design should support **both** modes. Typically, when saving a
*scene*, each top-level object is saved once with an ID, and any
dependent objects store references. For example, if we have a curve
object with id 1 and an offset of that curve with id 2, the offset's
`to_dict` might be
`{"type": "OffsetCurve", "base_id": 1, "distance": 5.0, ...}`. However,
if we are serializing just that offset curve alone (outside the context
of a full scene), we might embed the base expression to make it
standalone. The implementation can check if the base has an `id`
attribute or a flag indicating external management.

For simplicity, initial implementations might embed everything (making
each object fully self-describing), and rely on higher-level scene logic
to eliminate duplicates. But the **recommended approach** for
integration is to use references for shared
objects[\[2\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,get_subtree).
In this spec, we note that: - `ImplicitCurve.to_dict()` for base curves
(Conic, etc.) will output a full definition. - For composite objects
(trims, composites, regions) that contain other curves, the `to_dict`
may include nested dicts or references. We will detail those in their
respective sections.

`__str__()` **and** `__repr__()`**:**  
Provide human-readable descriptions of the curve. For `ImplicitCurve`,
`__str__` might return the equation string (e.g., `"x^2 + y^2 - 1 = 0"`
for the circle), and `__repr__` could include the class name and id
(e.g., `"<ConicSection: x^2 + y^2 - 1 = 0>"`). These are mainly for
debugging and logging. They are public but not heavily used in
computations.

### 2. ConicSection (Subclass of ImplicitCurve) {#conicsection-subclass-of-implicitcurve}

**Class** `ConicSection(ImplicitCurve)`**:** This subclass represents
any degree-2 implicit curve, i.e., equations of the form
$Ax^{2} + Bxy + Cy^{2} + Dx + Ey + F = 0$ . It covers circles, ellipses,
parabolas, hyperbolas, and degenerate cases (line pairs, etc., though
degenerate conics might be better handled by simpler classes).

Additional methods and behaviors:

    class ConicSection(ImplicitCurve):
        def conic_type(self) -> str: ...
        def canonical_form(self) -> 'ConicSection': ...
        def focus_directrix(self): ...  # optional, for parabolas
        def degree(self) -> int: ...
        # (inherits evaluate, gradient, etc., possibly overridden)

\- `conic_type() -> str`: Analyze the coefficients of the quadratic form
to determine the type of conic. For example, using the discriminant
$B^{2} - 4AC$ : - If discriminant \< 0 and A and C have same sign:
ellipse (if A=C and B=0 and centered at origin, a special ellipse -\>
circle). - If discriminant = 0: parabola (or degenerate). - If
discriminant \> 0: hyperbola. - Also check if it factors into lines
(degenerate case: if the equation can be factored). This method returns
a string like `"ellipse"`, `"circle"`, `"parabola"`, `"hyperbola"`, or
`"degenerate"` (with subcases perhaps). It should also consider
translation: if the equation has linear terms, the curve is not centered
at the origin. A robust implementation might complete the square to find
the center and axes. Example: For `x^2 + y^2 - 1 = 0`, `conic_type()`
would return `"circle"`. For `x^2 - y^2 - 1 = 0`, it returns
`"hyperbola"`. For `x^2 + 2x + y^2 = 0`, that's an ellipse (circle)
shifted left; still `"ellipse"` type.

- `canonical_form() -> ConicSection`: Return an equivalent ConicSection
  in a simplified or canonical coordinate frame. This might involve:
  translating the conic to center it (removing linear terms) and
  rotating if there\'s an $xy$ term, so that the result is axis-aligned.
  The method could compute the translation vector and rotation angle
  that simplify the quadratic form, then return a **new** ConicSection
  with equation in those coordinates. It can also return the
  transformation parameters (maybe as part of the object's fields or as
  separate methods to get center coordinates, rotation angle, etc.). For
  instance, the canonical form of $x^{2} + 2x + y^{2} = 0$ would be
  $(x + 1)^{2} + y^{2} - 1 = 0$ , i.e., centered at (-1,0) making it
  clear it's a circle radius 1 at (-1,0).

- `focus_directrix()`: (Optional) For parabolas, one might provide a
  method to get the focus point and directrix line equation. This is a
  specialized feature not required for other conics; it could raise
  NotImplemented for non-parabolas. For example, $y^{2} = 4ax$ has focus
  (a,0) and directrix x = -a. The general quadratic can be analyzed to
  extract these if needed.

- `degree() -> int`: Overrides the base or provides the polynomial
  degree of the curve. For ConicSection, this always returns 2. The base
  class might not have a concrete degree property (since not all
  implicits are polynomials), but for polynomial-based subclasses it's
  useful. Similarly, `PolynomialCurve.degree()` returns its degree.

**Performance and overrides:** ConicSection might override intersection
methods or others. For example, intersecting a ConicSection with a line
(another implicit of degree 1) can be solved by substituting the line's
equation into the conic's and solving the resulting quadratic exactly.
The module's high-level `intersect(curve1, curve2)` function will check
types and use such special-case logic (see function specs below). But
ConicSection itself could have helper methods or at least internal logic
to facilitate this.

**Serialization:** `ConicSection.to_dict()` would likely set
`"type": "ConicSection"` and then rely on the base implementation to
store the expression. We might also store a simpler description, like
center and radii for ellipse, but since those can be derived from the
expression, it's not strictly necessary. On load, seeing type
ConicSection, we could call `ConicSection(expr, vars)`.

### 3. PolynomialCurve (Subclass of ImplicitCurve) {#polynomialcurve-subclass-of-implicitcurve}

**Class** `PolynomialCurve(ImplicitCurve)`**:** Represents a general
polynomial implicit equation of degree *n* (could be 2 as well, but
typically if it's specifically degree 2 we use ConicSection for more
features).

- `degree() -> int`: Return the total degree of the polynomial. This can
  be computed by examining the Sympy expression -- e.g., for each
  monomial term $x^{i}y^{j}$ , check max(i+j). Sympy might have a
  `.total_degree()` function for polynomials we can use.
- We might include methods like `coefficients()` to retrieve polynomial
  coefficients in some structured way (like a dictionary mapping power
  tuples to coefficients, or a 2D array if we limit degree).
- If needed, a `factor()` method could attempt to factor the polynomial
  (e.g., $(x - 1)^{2} + y^{2} = 0$ factors over complex or such -- but
  for geometry, real factorization can find multiple components).
- Otherwise, it uses all base class methods. Intersection of two
  PolynomialCurves can be very computationally heavy (solving two
  polynomial equations). We would rely on Sympy's algebraic solvers or
  resultants for small degrees, and fallback to numeric methods for
  higher degrees.

**Example:** A lemniscate of Bernoulli could be given by
$\left( x^{2} + y^{2} \right)^{2} = a^{2}\left( x^{2} - y^{2} \right)$ .
Expanding that yields a 4th-degree polynomial implicit. That would be a
PolynomialCurve of degree 4. `degree()` would return 4, `evaluate` can
compute it, etc.

**Serialization:** `PolynomialCurve.to_dict()` uses type
\"PolynomialCurve\" and stores the expression string. No special
parameters beyond what ImplicitCurve does.

### 4. Superellipse (Subclass of ImplicitCurve) {#superellipse-subclass-of-implicitcurve}

**Class** `Superellipse(ImplicitCurve)`**:** Represents curves of the
form
$\left| \frac{x}{a} \right|^{n} + \left| \frac{y}{b} \right|^{n} = 1$
(or similar shapes). These are not polynomials for most n (except n=2
which reduces to an ellipse). They are a type of *procedural implicit
curve* defined by an exponent that affects curvature (n\<2 gives a more
rectangular shape, n\>2 more diamond-like shape). The implicit function
could be expressed as
$f(x,y) = \left( \left| \frac{x}{a} \right|^{n} + \left| \frac{y}{b} \right|^{n} \right)^{1/n} - 1$
. Alternatively, without the 1/n power:
$\left| \frac{x}{a} \right|^{n} + \left| \frac{y}{b} \right|^{n} - 1 = 0$
defines the same boundary.

**Special considerations:** Because of the absolute values, the
expression is piecewise-defined in quadrants. Sympy can handle `Abs(x)`
symbolically, but the gradient will involve signum functions. A
Superellipse might override `evaluate` or `gradient` to implement them
piecewise: - `evaluate(x,y)` can compute
$\left( |x/a|^{n} + |y/b|^{n} \right) - 1$ . If using numpy, we can do
`np.abs(x_val/a)**n + np.abs(y_val/b)**n - 1`. - `gradient(x,y)` will
have components:
$\partial f/\partial x = \frac{n}{a}*\text{sign}(x)*\left| \frac{x}{a} \right|^{n - 1}$
(and similarly for y). At $x = 0$ or $y = 0$ , the gradient is not
differentiable in the classical sense, but we can define subgradient or
set it to 0 in implementation.

**Fields:** likely store `a`, `b`, `n` as attributes or be constructed
from those. The Sympy expression could incorporate `Abs` and fractional
powers but that's fine.

**Methods:** We may provide: - `exponent() -> float`: returns n. -
Possibly getters for `a` and `b`. - We might not allow arbitrary
exponents for gradient (especially if not integer, derivative is
fractional power which Sympy can handle formally but numeric evaluation
might need caution around 0). - For simplicity, we expect `n` to be a
positive real. If it\'s rational, sympy might rationalize it; if it\'s
not, sympy might keep it symbolic.

**Usage example:** `Superellipse` might have an alternative constructor
for convenience: `Superellipse(a, b, n)` that sets up the expression
automatically as above. E.g.:

    class Superellipse(ImplicitCurve):
        def __init__(self, a: float, b: float, n: float):
            x,y = sp.symbols('x y')
            expr = ((sp.Abs(x)/a)**n + (sp.Abs(y)/b)**n) - 1
            super().__init__(expr, (x,y))
            self.a, self.b, self.n = a, b, n

This saves `a,b,n`. Then `to_dict` could store them separately for
clarity (so the type is \"Superellipse\", and data contains a,b,n, or
just the expression as well).

**Note:** A Superellipse is a closed shape (for n \>= 1). The inside
region is $f(x,y) < 0$ which corresponds to $|x/a|^{n} + |y/b|^{n} < 1$
.

### 5. RFunctionCurve (Subclass of ImplicitCurve) {#rfunctioncurve-subclass-of-implicitcurve}

**Class** `RFunctionCurve(ImplicitCurve)`**:** This class enables
*composite implicit operations* -- smooth unions, intersections, and
differences using R-functions or other blending techniques. It
essentially represents an implicit function that is a combination
$F\left( f_{1}(x,y),f_{2}(x,y) \right) = 0$ where $f_{1},f_{2}$ are
implicit functions of child curves and $F$ is some binary operation that
yields a new implicit. Examples of $F$ : - For a **union** (OR)
operation: a *sharp* union could be $\min\left( f_{1},f_{2} \right) = 0$
(meaning points are on the boundary if they are on either boundary that
is the outermost). But $\min$ is not smooth; an R-function smooth union
might use
$F\left( f_{1},f_{2} \right) = f_{1} + f_{2} + \sqrt{f_{1}^{2} + f_{2}^{2}}$
. The zero level of that gives a rounded merge of the two shapes. - For
**intersection** (AND): sharp intersection is
$\max\left( f_{1},f_{2} \right) = 0$ ; a smooth version might use
$F\left( f_{1},f_{2} \right) = f_{1} + f_{2} - \sqrt{f_{1}^{2} + f_{2}^{2}}$
for a smooth intersection (or other formulations). - For **difference**
(A - B): one can use something like
$F\left( f_{1},f_{2} \right) = \max\left( f_{1}, - f_{2} \right)$ for a
sharp difference (point is on boundary if it's on f1's boundary and
inside f2 or vice versa). Smooth difference can be constructed similarly
with R-functions.

Because these formulas can vary, `RFunctionCurve` likely stores: -
`curve1: ImplicitCurve` - `curve2: ImplicitCurve` - `operation: str`
(e.g., \"union\", \"intersection\", \"difference\", \"smooth_union\",
etc.) - `blend_param: float` (optional smoothing parameter, like radius
or alpha controlling smoothness)

The `expression` for RFunctionCurve can be a Sympy expression if we
choose a formula. Sympy has `Min` and `Max` functions, so we could
represent sharp union as `Min(f1_expr, f2_expr)` -- but note, `Min` is a
piecewise construct (non-differentiable where f1=f2). For smooth blends,
we might represent it as a formula using sqrt or other smooth
approximations. Or we keep it procedural (i.e., `evaluate` calls the
child evaluates and then combines values in Python). The decision
depends on needed symbolic capabilities: - If we want to allow further
symbolic operations on the result, representing it as a Sympy expression
is useful (Sympy can handle sqrt and even min to some extent). - If not,
it's simpler to not attempt a single expression and just override
`evaluate`/`gradient` to do combined numeric work.

**Behavior:**  
- `evaluate(x,y)` for RFunctionCurve will evaluate f1 =
curve1.evaluate(x,y), f2 = curve2.evaluate(x,y), then combine: - If
operation is `"union"` (sharp union), return `min(f1, f2)`. The
zero-level of that is effectively the union of the zero-level sets.
(Inside (negative) region of union has f_new \< 0 if either f1\<0 or
f2\<0.) - If `"intersection"` (sharp), return `max(f1, f2)`. - If
`"difference"` (A minus B), return `max(f1, -f2)` (since inside
difference means inside A and outside B). - If `"smooth_union"` or
method `"smooth"` with parameter, use a smoothing formula. A common
smooth-min approximation is:  
\$ \text{smooth\\min}(f1,f2; \alpha) = f1 + f2 - \sqrt{(f1 - f2)\^2 +
\alpha\^2} \over 2 \$ (this actually gives something like a soft
transition between min and average -- there are multiple formulae;
another is using logistic or exponentials). The parameter $\alpha$
controls the blend radius: when $|f1 - f2| \gg \alpha$ , this
approximates `min`, and when they are close, it rounds the corner. We
can choose one formula (perhaps referencing known techniques by Quilez
or Rvachev). For simplicity in coding, one formula is:  
$F_{union}(f1,f2) = f1 + f2 - \sqrt{f1^{2} + f2^{2}}$ .  
If f1 and f2 are both negative (inside both shapes, union region), this
yields a negative value larger in magnitude than each (which still
indicates inside). If one is negative and other positive, the sqrt term
ensures continuity. This formula smooths the intersection area of the
shapes. (Note: The chosen formula should be verified; there are known
R-function formulas in literature). - Smooth intersection similarly. -
Smooth difference might apply smoothness on the subtraction boundary. -
The exact formula or method could be parameterized by `method` and
`blend_param`. The module might include preset methods like
`"quadratic"` (meaning use a particular polynomial smoothing of degree 2
around the boundary), `"smooth_min"` (exponential smoothing), etc. The
initial design suggests `method="quadratic"` as default -- implying a
quadratic smooth blend.

- `gradient(x,y)`: If the operation is smooth and expressed as a
  formula, we can derive the gradient by combining gradients of f1 and
  f2 appropriately. If operation is sharp (min/max), the gradient is not
  well-defined exactly where f1 = f2, but away from that:

- If f1 \< f2, then min is f1, so gradient = grad(f1).

- If f2 \< f1, gradient = grad(f2).

- If equal, any gradient between them could apply; practically, we might
  choose one or the other or define it zero. Because of this
  nondifferentiability, it might be acceptable that at the exact seam,
  gradient has a discontinuity. For numeric purposes, maybe just pick
  one.

- For smooth formulas, we differentiate the formula. E.g., for
  $f1 + f2 - \sqrt{f1^{2} + f2^{2}}$ , the gradient = grad(f1) +
  grad(f2) - (1/(2*sqrt(\...)))*(2*f1*grad(f1) + 2*f2*grad(f2)) by chain
  rule. This simplifies to a weighted combination of grad(f1) and
  grad(f2). If implementers find this complex, they could also do
  numeric gradient (two small perturbations) for a smooth field if
  needed.

- `to_dict()`: The RFunctionCurve should serialize its operation and
  children. Example:

<!-- -->

- {
        "type": "RFunctionCurve",
        "operation": "union",
        "smooth": False,
        "curve1": curve1.to_dict() if standalone else {"ref": id1},
        "curve2": curve2.to_dict() if standalone else {"ref": id2}
      }

  If the curves are standalone or not part of scene, embed them. If they
  have their own IDs in scene, use references. The `operation` field
  distinguishes union/intersection/difference and whether it\'s smooth
  (or a separate param field for smoothness like `"alpha": 0.5`).
  `from_dict` will need to reconstruct by retrieving or rebuilding the
  child curves and then creating a new RFunctionCurve combining them.

**Note:** In some designs, we might not expose \"RFunctionCurve\"
directly to users; instead, users call high-level functions
`union(curve1, curve2)` which internally create an appropriate
RFunctionCurve or Composite. But we include it here for completeness
since it was listed as a class in the concept hierarchy.

**Example usage:**

    # Smooth union of circle and square
    circle = ConicSection(x**2 + y**2 - 1)
    square = Superellipse(a=1, b=1, n=10)  # n=10 approximates a square shape boundary
    blended = blend(circle, square, method="smooth", alpha=0.5) 
    # 'blend' might create an RFunctionCurve under the hood

Here `blended` is an ImplicitCurve (perhaps specifically an
RFunctionCurve). Its `evaluate(x,y)` will yield a field that is \~
negative inside either shape, with a smooth transition around where the
two shapes meet. If `alpha` is small, the union is almost sharp; if
large, they blend more gradually.

### 6. ProceduralCurve (Subclass of ImplicitCurve) {#proceduralcurve-subclass-of-implicitcurve}

**Class** `ProceduralCurve(ImplicitCurve)`**:** This class encapsulates
curves defined by a procedure or external code rather than an analytic
expression. For example, maybe the curve's shape comes from a dataset or
a complex algorithm (noise-based contour, etc.). It might not have a
closed-form expression.

In practice, we can implement `ProceduralCurve` by allowing the user to
pass a Python function `(x: float, y: float) -> float` that computes
$f(x,y)$ . Internally, we could still attempt to symbolically represent
it (maybe not), but typically we'd set `expression = None` or a
placeholder and just override `evaluate` to call the function.

**Fields:** - `func: Callable[[float,float], float]` -- the
user-supplied function. - Perhaps `grad_func: Optional[Callable]` if the
user can supply a gradient function as well (for better accuracy than
finite difference). - Possibly `description: str` -- a text description
of this procedure (for logging or serialization).

**Methods:** - `evaluate(x,y)` -- simply calls `func(x,y)`. If array
input is given, either vectorize the function or loop. We might use
NumPy's `vectorize` or `frompyfunc` to handle array inputs if
performance is needed. - `gradient(x,y)` -- if `grad_func` provided, use
it. If not, a fallback is to approximate by finite differences: e.g.,
take a small epsilon and compute
$\left( f(x + \varepsilon,y) - f(x - \varepsilon,y) \right)/(2\varepsilon)$
etc. This is less precise and can be slow, but at least provides a
result. The `ProceduralCurve` could raise `NotImplementedError` for
gradient if we choose to enforce requiring a grad function for certain
operations. But better to have a fallback numeric approximation. -
`normal(x,y)` -- same approach: compute gradient then normalize. -
`field(x,y)` -- call evaluate, similar to base. - `plot` -- can reuse
ImplicitCurve's logic since evaluate is available. - `to_dict()` -- here
we have a challenge: how to serialize an arbitrary function? We
generally cannot serialize code easily. We might just not support full
serialization for ProceduralCurve, or require that the function
corresponds to a known named function. Perhaps we allow a
`"formula_str"` if user actually gave one. Or we label it as
non-serializable. For simplicity, we might do:

    {"type": "ProceduralCurve", "function": "custom", "description": "user-defined curve"}

and then it's on the user to reattach the function after loading
(meaning `from_dict` might create a placeholder or require injection).
In an AI coding context, it might skip serialization for these, or treat
it as error.

Given this complexity, ProceduralCurve is likely used only at runtime,
not saved as part of scene (or if saved, it's a loss of information). We
mention this limitation in docs: **Note**: If using ProceduralCurve,
saving and loading the scene may not fully preserve the curve unless the
procedural definition is known to the system.

**Example usage:**

    import math
    f = lambda x,y: math.sin(x) + math.cos(y) - 0.5  # some wavy curve
    wave_curve = ProceduralCurve(f, description="sin(x)+cos(y)=0.5 curve")
    val = wave_curve.evaluate(1.0, 2.0)  # calls f(1.0, 2.0)

Now `wave_curve` is an ImplicitCurve albeit without a symbolic
expression. We can still find its intersection with another curve by
using numeric methods (since symbolic won't work). The intersection
routine would detect if one or both curves are procedural and choose a
numeric strategy (like a 2D root finder or sampling grid).

ProceduralCurve's presence ensures the module can be extended with
custom shapes not anticipated in the original design.

## Trimmed Curves and Curve Segments

In interactive design, it\'s often useful to take a portion of a curve
(between two endpoints or within a certain region) rather than the whole
infinite curve. The **TrimmedImplicitCurve** class represents a segment
of an implicit curve defined by a *mask* (a boolean condition in the
plane that selects part of the curve).

### Class: `TrimmedImplicitCurve(ImplicitCurve)`

A `TrimmedImplicitCurve` wraps a "base" implicit curve and restricts it
to a subset of its points. It still behaves like an ImplicitCurve (you
can evaluate it, plot it, use it in unions, etc.), but conceptually it
represents only those points of the base curve satisfying some
condition.

    class TrimmedImplicitCurve(ImplicitCurve):
        def __init__(self, base_curve: ImplicitCurve, mask: Callable[[float,float], bool]):
            ...
        def evaluate(self, x_val, y_val) -> float:
            ...
        def contains(self, x_val, y_val) -> bool:
            ...
        def to_dict(self) -> dict:
            ...
        @classmethod
        def from_dict(cls, data: dict, base_lookup: Callable[[int], ImplicitCurve] = None) -> TrimmedImplicitCurve:
            ...
        # Note: Other ImplicitCurve methods like gradient, normal, plot are inherited or overridden as needed

**Fields:** - `base_curve: ImplicitCurve` -- the underlying full curve
from which we are taking a portion. -
`mask: Callable[[float,float], bool]` -- a function or callable that
returns True if the point (x,y) *should be part of the trimmed curve*
(i.e., lies within the desired segment), and False if not. This mask
defines the trimming region or criteria. Commonly, the mask might be
based on: - A bounding box or angle range. - Parametric t-values if
known. - For an open curve segment between two endpoints, the mask can
be defined as "the point is between the endpoints along the curve" --
but implementing that is tricky without parameterization.

**Behavior:** - The trimmed curve is considered to consist only of those
points on the base curve where `mask(x,y)` is True. For any point not on
the base curve, we generally consider it not part of the trimmed curve
anyway (so mask only matters on the curve). - `evaluate(x,y)`: Usually,
the implicit function for a trimmed curve can be taken the same as the
base's $f(x,y)$ . Because trimmed or not, the underlying equation
doesn't change -- what changes is which points we consider "valid".
Thus, `TrimmedImplicitCurve.evaluate(x,y)` can simply delegate to
`base_curve.evaluate(x,y)` (returning the same scalar value). It does
**not**, for example, make points outside the trimmed segment have some
different value; if you evaluate the base's equation anywhere, you get
something. So trimmed's `evaluate` isn't restricted to mask--- it gives
you the field value of the base curve's function even for points outside
the trimmed segment. This is okay because typically one uses `contains`
or other means to know if a point is on the segment. Another approach
would be to modify evaluate such that if mask is False, maybe it returns
something else (like a positive value indicating "not on curve"). But
since off-curve points are anyway indicated by non-zero field, we rely
on `contains` to differentiate segment membership. -
`contains(x,y) -> bool`: This method is crucial for trimmed curves. It
should return True if the point (x,y) lies **on the trimmed curve
segment**. That implies two conditions: 1. The point lies on the base
curve (i.e. base_curve.evaluate(x,y) is approximately 0 within
tolerance). 2. The mask condition holds at that point
(`mask(x,y) == True`). So an implementation might check
`abs(base_curve.evaluate(x,y)) < tol` (some small tolerance, since
floating equals zero is tough) and `mask(x,y) is True`. For strict
symbolic checking, if one had exact coords, we could check f=0 exactly,
but usually this is numeric. - If either condition fails, contains is
False. This method allows functions like intersection or composite
assembly to know if an intersection point lies on the trimmed portion or
was on the base outside the trimmed range. - `gradient` and `normal`: by
default, these can use the base curve's gradient/normal (since trimming
doesn't change local geometry). If needed, TrimmedImplicitCurve can
override them simply to use base's methods (which they inherit
anyway). - `plot()`: should draw only the trimmed portion of the curve.
This is one area where we can't just use base's plot on the whole range,
we must restrict it. Implementation approach: - We can sample points on
the base curve (for example by solving for one variable or
parameterizing locally) that satisfy the mask, or sample many points on
base curve and filter by mask. - A generic method: use base.plot at high
resolution to get the full curve contour, then filter the resulting
points by mask and only draw those segments. However, base.plot might
give you a continuous contour (like a list of line segments). You'd need
to cut that polyline where mask condition fails. Possibly simpler is to
manually do a parameter walk: \* If the base curve can be parameterized
(some shapes can, like circles or known curves, but not general ones
easily). \* Alternatively, pick a grid, evaluate base f, find near-zero
points, and test mask -- not very precise though. - Another approach: if
mask is something simple like x \> 0 (right half of curve), one can
solve the base's equation with that constraint explicitly. - The
implementation might thus depend on the nature of mask. In general, a
safe fallback is to use base.plot to get an approximate polyline for
f=0, then discard portions where the midpoint of a line segment violates
mask. - `to_dict()`: Must serialize the trimmed curve. Key elements: -
`"type": "TrimmedImplicitCurve"` - Represent `base_curve`: either by
reference ID or by a nested dict. Likely by reference if base is a
separate object in scene, or nested if not. - Represent `mask`: This is
tricky because a mask is an arbitrary function. We might restrict mask
to certain known types (for serialization) or not support serializing
complex mask. Perhaps we allow a mask that is defined by a geometric
region or simple analytic condition, and we store that. For example, if
mask corresponds to a bounding box, store that. If mask corresponds to
two endpoints on the curve, store those endpoints. - One approach: If
this trimmed segment was created by
`curve_segment(curve, start_point, end_point)`, then we know the mask
basically \"between start and end along curve\". We could store the
start and end coordinates. That gives enough to roughly reconstruct
(we'd need to find the segment between them, possibly by re-tracing). -
If mask is a user-provided lambda, we cannot serialize that. In such
cases, either prohibit such complex masks from being saved or define
mask in terms of base curve parameters (like store param t-range if base
was parameterized). - Perhaps easier: only allow mask that can be
encoded as a shape or region: e.g., a polygon or angle range. Could
store polygon vertices for clipping region, etc. - For simplicity in
initial spec, we'll assume typical masks come from either specifying
endpoints or a rectangular region. - So possible fields in dict:
`"base_curve": {...}, "mask_type": "endpoints", "start": [x0,y0], "end": [x1,y1]`.
Or `"mask_type": "region", "polygon": [...]` for arbitrary region. -
Then `from_dict` would reconstruct base (resolving reference if needed)
and if mask_type is endpoints, call `curve_segment(base, start, end)`
internally to recreate. - Another scenario: a user trims by half-plane,
e.g., \"x \> 0\". Mask = lambda x,y: x\>0. We can detect that and store
it as `"mask_type": "halfplane", "condition": "x>0"` or something. That
again requires parsing on load (not trivial but doable).

Given the complexity, the specification can outline that serialization
of masks is limited: **if the mask is defined by simple geometric
criteria (endpoints or a rectangular region), it will be serialized;
otherwise, the trimmed curve might not be fully serializable without
custom handling**.

**Supporting Functions for Trim:**  
The module provides convenience functions to create trimmed curves: -
`trim_curve(curve, region_mask) -> TrimmedImplicitCurve`: a generic
function to trim a curve by an arbitrary region mask. For example,
`region_mask` could be a function `lambda x,y: (x >= 0 and y >= 0)` to
take the first quadrant portion of the curve. Internally this just does
`TrimmedImplicitCurve(curve, region_mask)`. If the mask is not callable
but perhaps a shape (like if we allowed passing an AreaRegion or
polygon), we might adapt it (e.g., create a function that tests point
inside that region). -
`curve_segment(curve, start_point, end_point) -> TrimmedImplicitCurve`:
trims the curve to the segment between two specified points on that
curve. The inputs `start_point` and `end_point` are tuples (x,y) that
**must lie on the curve**. This function will: 1. Validate that
start_point and end_point indeed satisfy `curve.evaluate` ≈ 0 (within
tolerance). If not, raise ValueError. 2. Define a mask that selects the
appropriate portion of the curve between these points. How to do this
algorithmically: - If the base curve is closed (like a circle) or has
multiple branches, there are two possible segments connecting the
points. The function might choose the shorter path by default, or need
an extra parameter (like direction or preference). - One approach: do a
continuation from the start point along the curve until the end point is
reached, and mark all visited points as the segment. This requires a
curve tracing algorithm: \* Starting at start_point, use the gradient
(normal direction) to locally step along the curve (perpendicular to
gradient, i.e., tangent direction), or use a param if known, until you
get to end_point. Keep track of path. \* This is complex to implement
generally; but for common shapes we can do easier: e.g., if curve is
differentiable and not self-intersecting between those points, this
works. For something like a circle, we can compute polar angles for the
points and take the smaller arc. - In simpler terms, the mask could be
defined implicitly as "not having passed through any cut that excludes
the end." Some simpler solution: if the curve can be implicitly turned
into a function y(x) or x(y) in some range, and start and end give a
range on that function. - As an approximation, one might use the line
segment between start and end as a dividing line: e.g., assume the
desired segment is the one that lies near that line segment. That's not
robust though. - For now, the spec can say: the implementation may
approximate the segment by sampling the curve and selecting the arc
connecting start to end that doesn't wrap around the other way. For
closed shapes, default to the shorter arc unless specified.

     Once the set of segment points is determined (even approximately), the mask can be encoded as the set of those points or the param range. But for a continuous mask function: we might define mask for segment as follows: *the mask returns True if and only if the point is closer (in along-curve sense) to the start-end path than the alternative.* This is hard to formulate simply.

     Another idea: if the curve is defined by wzxhzdk:94, we can have another function wzxhzdk:95 that increases monotonically along the curve (like an arclength parameter or an angle for circles). If we find one for base (maybe by picking an initial point and integrating curvature), we could then mark points between two parameter values. But designing that for arbitrary curve is advanced.

- In practice, initial implementation might just assume the curve is
  reasonably simple and do:

  - If curve is closed: convert to param (like polar angle if center
    known, or find a param by solving).
  - If open (like a parabola or line), then the "segment" is just
    between those two along the only path.
  - Possibly use shapely: shapely can approximate curves as polylines
    and then we could cut that polyline between points.
  - The function can indeed use shapely: if we can turn the implicit
    into a shapely geometry (approximate it via many segments), shapely
    can split a LineString at given points and give the segment.

- Ultimately, `curve_segment` returns
  `TrimmedImplicitCurve(curve, mask)` with that mask capturing the
  segment.

- `contains(x,y) -> bool`: as described, check if on base (f≈0) and mask
  true.

**Example:**

    # Trim the right half of a circle (x >= 0 side)
    half_circle = trim_curve(circle, lambda x,y: x >= 0)
    half_circle.contains(0.707, 0.707)  # True (point on right upper quadrant)
    half_circle.contains(-0.707, 0.707) # False (point on left side not included)

Here the mask is a simple half-plane. Plotting `half_circle.plot(...)`
should show only the right half of the circle.

**Integration considerations:** TrimmedImplicitCurve can be used
anywhere an ImplicitCurve is expected (it inherits). E.g., you can find
intersections between a trimmed curve and another curve -- the
intersection solver should check `contains()` on results to filter any
intersection points that lie outside the trimmed portion. Also, when
trimming an existing scene curve, one would create a new
TrimmedImplicitCurve object (with a new ID) and possibly keep the
original curve intact. The dependency graph might not necessarily link
the trimmed to the base as a dependency, because trimming is often a
one-time derivation (the segment doesn't automatically update if the
base is changed in shape -- although one could consider it should, but
the mask might no longer apply if shape changed drastically). If the
base curve's parameters change slightly (like radius), arguably the
segment endpoints move; the system could attempt to update them if it
knows how (maybe recompute the intersection of new base with the mask
region or recompute param positions). This is complex, so a trimmed
curve might be treated as *broken* if base changes (the user might need
to re-trim). The dependency graph can still register the base as a
parent of trimmed, and if base changes, mark trimmed as broken (since
there's no automatic re-trim logic provided unless
trivial)[\[2\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,get_subtree).

**Serialization:** Given the complexity, an example serialized trimmed
curve might look like:

    {
      "type": "TrimmedImplicitCurve",
      "base": {"ref": 5},               // reference to base curve object ID 5
      "mask": {
          "type": "halfplane",
          "expression": "x >= 0"
      }
    }

or for an endpoint-defined segment:

    {
      "type": "TrimmedImplicitCurve",
      "base": {...},                    // possibly inlined base definition if no id
      "mask": {
          "type": "segment",
          "start": [x0, y0],
          "end": [x1, y1]
      }
    }

`from_dict` would then need context (like a lookup function to resolve
`"ref":5` to an actual object, which the scene manager would supply). If
base is embedded, it loads that first. Then if mask type is \"segment\",
it might call `curve_segment` on the base with those endpoints (which
will recompute the mask function as needed). If mask is \"halfplane\",
it reconstructs a lambda or a small function from the expression string
(like using Python's `eval` with safe context or a small parser). That's
doable for simple conditions (e.g., parse \"x\>=0\" to a lambda x,y:
x\>=0). We'll note that only certain simple mask types are supported by
serialization.

### Operations Associated with Trimming

We already described `trim_curve` and `curve_segment` functions:

    def trim_curve(curve: ImplicitCurve, region_mask: Callable[[float,float], bool]) -> TrimmedImplicitCurve: ...
    def curve_segment(curve: ImplicitCurve, start: (float,float), end: (float,float)) -> TrimmedImplicitCurve: ...

\- `trim_curve`: general trimming. Example use:
`trim_curve(circle, lambda x,y: y >= 0)` would return the top half of
the circle (all points on circle with y\>=0). - `curve_segment`:
specifically for between two points. Example: If you have an ellipse and
you want the arc from angle 30° to 60°, you could find those endpoint
coordinates and call `curve_segment(ellipse, pt30, pt60)`.

Both functions ensure the result is a `TrimmedImplicitCurve` that is a
valid ImplicitCurve in itself (so it can be used in unions, etc. --
though note, if you union two trimmed curves that were originally parts
of the same base, you effectively could reconstruct the original shape
or a subset). Trimmed curves should implement everything needed so that,
for example, if you do `union(trimmedCurve, anotherCurve)`, inside the
union\'s evaluate it will call each's evaluate -- trimmed's evaluate
works fine (just base eval), but union\'s logic should also check if the
point is in the trimmed part or not? Actually, union's implicit
combination doesn't inherently know about mask. If trimmed's field
returns a value for a point not in the segment, it's because base gave
it. If that point is not on the base curve, the field will be nonzero
(positive outside or negative inside if base had interior concept). So
it\'s fine -- trimmed curve doesn't have an inside region notion beyond
the curve itself, it\'s a 1D set. Typically for union and intersection
operations, we might mostly use closed shapes (areas). Using an open
curve in a union is a bit unusual, but the method doesn't forbid it:
union of a curve and another yields presumably an implicit whose zero
set includes both (which might be disjoint sets). It's okay.

## Composite Curves and Area Regions

### Class: `CompositeCurve(ImplicitCurve)`

A `CompositeCurve` represents a connected sequence of curve **segments**
joined end-to-end, forming a continuous piecewise curve. This is useful
for modeling a complex boundary that consists of different pieces (e.g.,
an architectural profile composed of arc and line segments). In our
design, each segment is a `TrimmedImplicitCurve` (or could be a whole
ImplicitCurve if it naturally ends at join points, but typically trimmed
to those join endpoints). The composite itself is considered an
ImplicitCurve so that it can be used in further operations like any
other curve.

    class CompositeCurve(ImplicitCurve):
        def __init__(self, segments: list[TrimmedImplicitCurve]):
            ...
        def segments(self) -> list[TrimmedImplicitCurve]:
            ...
        def is_closed(self) -> bool:
            ...
        def evaluate(self, x_val, y_val) -> float:
            ...
        def contains(self, x_val, y_val) -> bool:
            ...
        def plot(self, **kwargs):
            ...
        def to_dict(self) -> dict:
            ...
        @classmethod
        def from_dict(cls, data: dict, curve_lookup: Callable = None) -> CompositeCurve:
            ...

**Fields:** - `segments: List[TrimmedImplicitCurve]` -- the ordered list
of segments composing the curve. The end of each segment should coincide
with the start of the next, so the whole list forms a continuous path.
The segments may come from different base curves (e.g., segment 1 is
part of a circle, segment 2 is part of a line, etc.). - We assume the
segments are oriented consistently. Ideally, the end of `segments[i]`
exactly matches the start of `segments[i+1]` in coordinates. The code
may enforce this by adjusting or warning if not.

**Behavior:** - `is_closed() -> bool`: Returns True if the composite
curve forms a closed loop. That typically means the end of the last
segment connects back to the start of the first segment (within some
tolerance). If true, the composite can be used as a boundary for an
AreaRegion. If false, it's an open polycurve. - `evaluate(x,y)`: We need
to define an implicit function for the composite curve. Since the
composite is not a single analytic equation in general, we can't have a
simple Sympy expression that yields 0 exactly on all segments. However,
we still want to treat CompositeCurve as an ImplicitCurve for interface
consistency. Options: 1. **Pseudo-distance approach:** We could define
evaluate as the *minimum* of the absolute field values of all segments
(with a sign convention perhaps irrelevant since segments themselves
might not define an inside/outside). For a purely 1D curve like this,
inside/outside is not defined (there's no filled area). So perhaps we
treat the composite as a curve that doesn't partition the plane. If we
just want an implicit field for it, one common trick is to use a
**signed distance** or approximate distance to the curve: i.e.,
`evaluate(x,y)` returns a positive value equal to distance from the
nearest segment minus zero (so it's zero on the curve, positive off the
curve). This would treat all segments collectively. - We could
approximate this by returning `min_i f_i(x,y)` if each segment's base f
provides a signed distance or at least a function that's zero on that
segment. However, if segments overlap or if base functions have
different sign conventions, careful: but trimmed segments of the same
base share that base's f which is zero on segment and either positive or
negative off (with no consistent "inside" concept). - A simpler
approach: return the **minimum absolute value** of all segment
evaluations: `min(|f1(x,y)|, |f2(x,y)|, ...)` and perhaps give it a sign
of something if needed (not particularly meaningful here since
composite's inside concept is not used; we might just always return
non-negative as a pseudo-distance). - This would yield 0 on the entire
polycurve. Off the curve, it yields some positive value measuring
closeness to one of the segments. If two segments are far apart, in the
gap the value is nonzero reflecting distance to nearest piece. This
effectively treats composite like a multi-curve set, not as one
continuous function. But it's okay for evaluating and plotting (contour
at 0 will draw all pieces). - The drawback is differentiability at
segment joins or at equidistant points from two segments (but that's
fine, it's an implicit for disjoint union of segments). 2. **Piecewise
definition:** We could try to define a piecewise sympy expression for
each segment region, but determining which piece's equation to use at a
given (x,y) requires checking if point projects onto that segment, which
is complex symbolically. So likely not. 3. **Not implementing evaluate
at all?** But we promised to fully implement ImplicitCurve interface. So
we should have something.

The simplest robust path: implement `evaluate` to return the minimum of
absolute base evaluations. For sign, perhaps always non-negative
(distance style). We might just define it as distance. But computing
actual Euclidean distance to an implicit curve is an iterative process;
using \|f\| as a proxy is not actual distance unless f is a distance
field. But for small distances it's a decent heuristic, and if each base
is reasonably scaled (like for conic f, not exactly distance but scaled
by gradient lengths).

It\'s acceptable for our usage because the main use of `evaluate` for
composite might be in plotting or passing to field generator. Field
generation (like a sign distance field from composite) could refine this
anyway.

Therefore: - For each segment $s_{i}$ with base function $f_{i}$ ,
compute $v_{i} = f_{i}(x,y)$ . Since the segment only is defined where
$f_{i} = 0$ and mask holds, away from that segment, $f_{i}$ won't be
zero but has some value. We take $d_{i} = \left| v_{i} \right|$ as a
pseudo-distance to segment i (not exactly distance but 0 at segment, \>0
off). - Let $d = \min_{i}d_{i}$ . Then we can return d (or even keep the
sign as + always or decide a sign if composite is closed to define an
interior). - If composite is closed, perhaps we might want a sign:
inside that closed loop vs outside. But since composite by itself
doesn\'t know an inside (unless it's closed, in which case an area
region should be used for interior queries). If someone tries
`contains(x,y)` on a closed CompositeCurve, maybe we return True if x,y
lies *on* one of the segments (since \"contains\" concept for a curve
usually means on the curve, not inside area). - So likely we treat
composite curve as just a set of curves, not an area. So we won\'t
define negative/positive for inside/outside in composite\'s evaluate. We
simply treat outside as not on curve.

Summing up, `evaluate` for composite returns a float where 0 indicates
the point is on one of the segments (and satisfying that segment's
mask), and a nonzero value otherwise (with no particular sign meaning
beyond that). Possibly always positive unless the base functions produce
negative in some region, but since segments are just 1D, we might as
well output absolute value.

- `contains(x,y) -> bool`: True if the point lies on **any** of the
  component segments (again within tolerance). We implement by iterating
  segments: if any `seg.contains(x,y)` is True, then True. Otherwise
  False. This is the proper geometric \"point on this composite curve?\"
  query.

- `segments()`: returns the list of TrimmedImplicitCurve segments
  (perhaps to allow external iteration or inspection).

- `plot()`: Plot all segments in sequence. This can simply loop through
  segments and call each segment's plot onto the same axes (ensuring to
  use same scale and not show intermediate). Alternatively, since each
  segment's `plot` might create a full figure, better to manually gather
  their points:

- For each segment: we can attempt to sample points along it (the
  segment likely being simpler than the base's full curve).

- Possibly the CompositeCurve could store not just segments but also the
  coordinates of endpoints for easy plotting, but the segments
  themselves have endpoints (the mask likely determined by them).

- The composite can join the points from segment1 and segment2 if they
  share an endpoint to make a continuous plot, though drawing separately
  yields same visual if done sequentially.

- The composite inherits ImplicitCurve interface, but methods like
  `gradient` or `normal` might not be well-defined globally. Perhaps we
  won't implement `gradient` for composite (or if needed, we could
  approximate by whichever segment's gradient is relevant if point is on
  a segment, but if point is not on any segment, gradient of distance
  field concept can be computed by whichever segment is closest).

- Possibly just leave `gradient` not explicitly overridden; if
  `evaluate` returns a min of absolute values, we could differentiate
  that piecewise. But not worth complicating; probably not needed in
  normal usage except maybe field generation. If needed, one could
  approximate gradient by finite diff on composite's evaluate. That's
  fine.

- `to_dict()`:

- `"type": "CompositeCurve"`

- Need to serialize segments. Since segments might be unique to this
  composite, likely we embed them.

- We can store segments as a list under a key, e.g.
  `"segments": [dict(seg1), dict(seg2), ...]`.

- Each segment is a TrimmedImplicitCurve, so we use its `to_dict`. If
  those trimmed segments reference base curves that are not used
  elsewhere, we can embed fully. If some segment's base is also a
  top-level object or used by another composite, it might be referenced.
  However, typically if a composite is built, those base curves might
  have been created solely for it or duplicates. But consider: If the
  user trims an existing curve for segment, the base might be an
  existing object. In such case, the segment's to_dict would likely use
  base's id reference. Then when loading, to avoid duplicating the base
  geometry, we must ensure to reuse. A straightforward strategy:

  - Save each segment with possibly references if base has id.
  - Save composite as containing those segments.
  - In from_dict, when reconstructing segments, we provide a
    `base_lookup` that can resolve references by id to actual curve
    objects already loaded or currently being loaded. The composite
    from_dict might accept a `curve_lookup` parameter to fetch base
    references from the scene.
  - If base curves were not separate (like user created them on the
    fly), they\'d be embedded, so then it\'s fine.

- `from_dict`: Reconstruct the segments list:

- For each segment dict in data, call `TrimmedImplicitCurve.from_dict`.
  That may need a way to resolve base references; so likely the
  composite's from_dict gets passed a function or context that knows all
  loaded objects by id (the scene manager would orchestrate this).

- After getting segment objects, just do
  `CompositeCurve(segments_list)`.

- We might also verify connectivity (matching end-points) upon loading,
  possibly warn if mismatched (floating precision differences can be
  tolerated within epsilon).

**Example usage:**

    # Suppose we have a circle and a line and we want a shape composed of a quarter-circle and a line tangent.
    arc = curve_segment(circle, start=(0,1), end=(1,0))  # quarter circle from top to right
    line = ConicSection(y - 0)  # x-axis line
    seg_line = trim_curve(line, lambda x,y: (0 <= x <= 1 and y==0))  # line segment from (0,0) to (1,0)
    composite = CompositeCurve([arc, seg_line])
    composite.is_closed()  # False, it's an open shape
    composite.plot(xlim=(-0.1,1.1), ylim=(-0.1,1.1))

This would produce an L-shaped curve (quarter of a circle and then a
line). `CompositeCurve.evaluate(x,y)` near those segments yields small
values; on the drawn segments yields 0; `contains` would identify points
exactly on those pieces.

### Class: `AreaRegion`

An `AreaRegion` represents a 2D area bounded by one or more closed
curves. It essentially defines a set of points in the plane (an
interior), somewhat analogous to a filled shape or polygon. This class
is useful for operations like calculating area, doing point-in-region
tests, and generating fields like occupancy grids or distance fields for
the area.

    class AreaRegion:
        def __init__(self, outer_boundary: CompositeCurve, holes: list[CompositeCurve] = []):
            ...
        def contains(self, x_val: float, y_val: float) -> bool:
            ...
        def area(self) -> float:
            ...
        def perimeter(self) -> float:
            ...
        def plot(self, **kwargs):
            ...
        def field(self, x_val: float, y_val) -> float:
            ...
        def fill(self, resolution: int = 100) -> np.ndarray:
            ...
        def to_dict(self) -> dict:
            ...
        @classmethod
        def from_dict(cls, data: dict, curve_lookup: Callable = None) -> AreaRegion:
            ...

**Fields:** - `outer_boundary: CompositeCurve` -- a closed composite
curve defining the outer boundary (outline) of the region.
**Precondition:** `outer_boundary.is_closed()` should be True, or else
the region is not well-defined. We assume a consistent orientation
(clockwise or counterclockwise) for the boundary, typically
counterclockwise for the outer boundary (with interior on the left side
as you traverse). - `holes: List[CompositeCurve]` -- optional list of
closed composite curves that define holes (interior boundaries) within
the region. Each hole curve should also be closed. Ideally, they should
lie entirely inside the outer boundary and not intersect each other or
the outer boundary (like disjoint holes in a shape). - Optionally, we
might also store a field strategy or a cached field (see FieldStrategy
below), but that can be generated on the fly.

**Behavior:** - `contains(x,y) -> bool`: Return True if the point (x,y)
lies inside the area region (i.e., in the filled part), and False if it
lies outside or on a hole. We consider points exactly on the boundary as
inside or not? Typically, for a region, being on the boundary might be
considered inside for containment test (depending on convention). We can
define contains such that: - If (x,y) is exactly on outer_boundary,
return True (or maybe allow inclusive). - If on a hole boundary, return
False (point is not in the filled area if it\'s on the hole's edge). -
Otherwise, do a standard point-in-polygon test using the boundaries.

Implementation: We cannot easily rely on implicit function signs for
composite boundaries because CompositeCurve doesn't give a well-defined
inside field. Instead: - We can sample the sign of one of the base
curve's implicit functions if that base extends to define an inside. For
example, if outer_boundary is one closed loop, perhaps one of its
segment's base curves (like if it's all arcs and lines) might not have a
global f that's negative inside entire shape. Possibly not -- if
segments come from different formulas, no single f covers all. -
Instead, use a ray-casting or winding rule algorithm: \* Cast a ray from
(x,y) to infinity and count how many times it crosses the outer boundary
segments. If an odd number, point is inside outer boundary. Then check
holes: if inside any hole (odd crossings on a hole boundary), then it's
actually outside of that hole (so not contained in region). \* The
composite segments give a piecewise linear/curved boundary. We can
sample or param equations to find intersections with a ray. This is
doable numerically. For robust implementation, might convert each
segment to a polyline approximation with fine resolution and then do a
typical point-in-polygon (like winding number). \* Using a library: If
shapely is available, we could convert boundaries to shapely polygons
and use its `contains` function, which is reliable. E.g., polygon =
shapely.Polygon(exterior, \[hole1, hole2, \...\]); then contains =
polygon.contains(Point(x,y)). That requires approximating each composite
to a series of points (since shapely deals with straight line segments,
not true curves, but fine with a high enough fidelity). \* Without
shapely, do manual algorithm with enough sampling or analytic segment
intersection checks. - Efficiency: contains will often be called for
single points, could be fine to use shapely or manual crossing test with
moderately fine segmentation of curves.

- `area() -> float`: Compute the area of the region (outer area minus
  holes). If the outer_boundary and holes were simple polygons, one
  would sum polygon areas. For curved boundaries, we can still compute
  area via calculus (line integrals) or approximate via sampling.

- For many shapes, area can be computed by integrating the implicit
  function or using Green's theorem. But a general approach:
  - If shape is composed of known segments (circular arcs, lines, etc.),
    possibly derive formula for area segment (e.g., area under an arc
    can be computed).
  - Or sample the region with a fine grid or Monte Carlo to approximate
    area. That could be slow if done repeatedly.
  - Possibly convert to shapely geometry (as above) and use
    shapely.area.

- Given performance considerations, an initial implementation might
  approximate:
  - Rasterize region at high resolution and count pixels (approx area).
  - Or break the boundary into many short linear segments (like polyline
    approximation) and use standard polygon area calculation (Shoelace
    formula) on that polyline. That's likely the most straightforward:
    sample each curved segment at high resolution to a series of points,
    then sum cross-products for area.

- We should clarify tolerance: area result might have a small error
  depending on resolution of approximation, which might be acceptable
  for interactive use. If exact area is needed for simple shapes,
  specialized code can be added (like formula for circle area etc if
  shapes known, but that defeats generality).

- `perimeter() -> float`: (Not listed in original doc, but often useful)
  -- sum of lengths of outer boundary and holes (with holes subtracted
  if needed). Could similarly approximate by summing lengths of segments
  or formulas for each (line length easy, arc length maybe known or
  numerical integration).

- If not required, we can omit this, but it\'s a common metric.

- `plot()`: Visualize the region. This could:

- Draw the outer boundary (maybe filled) and hole boundaries (maybe
  unfilled).

- If using matplotlib, one can use `plt.fill` to fill the polygon. But
  since boundaries are curved, need to approximate them with points.

- Or sample a grid and color inside vs outside (like a filled contour).

- Simpler: use the fill() method (described next) to get a raster of
  inside/outside and display that as an image or contour.

- Or if shapely is used, get polygon and use its plotting or transform
  to points for fill.

- For a crisp look, a combination: draw outer boundary curve and holes
  with lines, and fill the interior with translucent color.

- The specifics can vary; the key is to communicate that it should show
  the area clearly.

- `field(x,y) -> float`: Evaluate a scalar field associated with this
  region at (x,y). The region itself can produce different kinds of
  fields depending on context:

- If the idea is a *signed distance field*, then `field(x,y)` would
  return the signed distance to the region's boundary (negative inside,
  positive outside). If `field_strategy` is set to
  SignedDistanceStrategy (discussed under Field strategies),
  `AreaRegion.field()` might use that.

- If the field strategy is occupancy (binary), `field(x,y)` could return
  1.0 if inside, 0.0 if outside (or vice versa).

- Or a gradient fill might return a value between 0 and 1 depending on
  distance or other pattern.

- Implementation approach: `AreaRegion` may hold an attribute
  `field_strategy: FieldStrategy` or similar. In the constructor, we
  might allow an optional param to pick a default strategy (e.g.,
  default to SignedDistanceStrategy for field queries).

- If `field_strategy` is set, `field(x,y)` simply calls that strategy's
  generate/evaluate. If not, we define a default:

  - Possibly default to occupancy (inside -\> 1.0, outside -\> 0.0).
  - But occupancy is a bit trivial (it's like contains as float). Signed
    distance is more informative for modeling.
  - The design suggests an interface where you can ask for a specific
    field representation via
    `field_representation(method="signed_distance")`, returning e.g. a
    `BaseField`. They list in the original doc:
  - `field(x,y)`
  - `fill(resolution)`
  - `field_representation(method="signed_distance") -> BaseField`.
  - They also show a `field_strategy` attribute in class definitions,
    though not explicitly in the earlier skeleton but in narrative.
  - Possibly, `AreaRegion.field(x,y)` is meant to always give a default
    field value (like signed distance by default), and the strategy can
    be changed.
  - We can implement: if field_strategy is None, assume occupancy or a
    basic distance guess.

- For now, we will say: by default, `field(x,y)` returns a signed
  distance approximation: if inside, value negative (with magnitude
  equal to min distance to boundary), if outside, positive = distance to
  boundary. Actually computing exact distance to a complex boundary is
  involved:

  - If boundaries were lines and arcs, we can compute distance from
    point to each segment (distance to line segment formula, distance to
    arc (center and angle) etc.) and take the smallest distance to any
    boundary segment, then apply sign (negative if point is inside
    region, which we can check via contains).
  - That yields a signed distance (with some error if shape corners
    cause discontinuities, but that\'s real).
  - So an implementation:
    `dist = min(min_distance_to_outer_boundary, min_distance_to_any_hole)`.
    If point is outside outer (contains False), result positive distance
    to outer. If inside outer and not in any hole (contains True),
    result = negative of distance to nearest boundary (which could be
    either outer boundary or a hole boundary, whichever is closer).
  - If inside a hole (shouldn\'t happen if we define region such that
    inside hole is outside region), but if point is exactly inside hole
    area, `contains` is False, so treat as outside region, and distance
    to hole boundary is maybe the distance but we consider sign positive
    because it\'s outside region (the region\'s interior excludes that
    point).
  - If on boundary, distance 0.
  - This gives a continuous signed distance field except at boundary
    (which is fine, that's where it's zero anyway).
  - Implementing min distance to a CompositeCurve: for each segment,
    compute distance from point to that segment's underlying curve.
  - For line segment or arc segments, there are straightforward formula:
    distance to infinite line or circle, then clamp to segment.
  - For general implicit segment: we could use the base curve's implicit
    function as a pseudo-distance if gradient \~1. But that\'s not exact
    distance, could do a quick numeric projection to find actual foot.
  - Perhaps better to sample some points on segment and pick nearest, or
    more precisely:
    - If base is differentiable, set up a distance minimization problem:
      minimize (x - X(t))\^2+(y-Y(t))\^2 subject to f(X,Y)=0. Could
      solve via Lagrange multipliers or numeric root find. That's heavy
      to do for each query but maybe okay if needed.
    - Simpler fallback: approximate each segment by many small line
      segments, then distance is min distance to those lines (like
      polyline approximation).
  - For initial approach, approximate distance via polyline
    discretization of boundaries (that\'s easier and still accurate if
    resolution is fine).
  - Alternatively use shapely: shapely can compute distance from a point
    to a geometry. If we have polygon for outer and holes,
    shapely.distance will give distance to boundary (holes considered
    part of boundary, I think shapely polygon distance gives 0 if
    inside, \>0 if outside, or if inside hole, distance to that hole\'s
    boundary which might be less than to outer boundary).
  - Actually if point inside polygon, shapely.distance = 0 (distance to
    the polygon's interior is 0 by definition because it contains it).
    That's not helpful for signed distance magnitude; we want distance
    to boundary.
  - Could instead extract boundary lines and compute distance to those
    using shapely, which can consider interior points distance to edges
    (should be positive).
  - Or easier: if inside region, distance = min(distance to outer
    boundary, distance to any hole boundary). If outside region,
    distance = distance to outer boundary (holes irrelevant because
    you\'re outside already).
  - Shapely can give distance to a polygon for outside points (that's
    distance to boundary effectively), and for inside points we can
    compute distance to boundary by looking at distance to interior
    holes or outer edges directly (like shapely has polygon.exterior and
    polygon.interiors).
  - We\'ll specify conceptually and leave exact method open.

- `fill(resolution: int) -> np.ndarray`: Generate a rasterized fill of
  the region or its field on a grid. This method creates a 2D array
  representing either a binary mask of inside/outside or a field sampled
  over the area's bounding box. The meaning could be:

- If we interpret \"fill\" as an occupancy grid (since the name suggests
  filling an area), likely it returns a NumPy array of shape
  (resolution_y, resolution_x) where each cell is 1 if the corresponding
  point is inside the region, or 0 if outside (if occupancy
  interpretation). Or it could be a float field value if using a
  different strategy.

- The original doc hints: `fill(self, resolution) -> np.ndarray` likely
  for a rasterized fill or field sample. Possibly default to occupancy
  fill (which is essentially a mask image).

- We should define how resolution translates to grid size:
  - It could be interpreted as number of pixels across the width (with
    height scaled accordingly to aspect ratio of region's bounding box).
  - Or resolution is total number of samples in each dimension (like
    resolution x resolution grid covering bounding box).
  - For simplicity: assume a square grid of size
    `resolution x resolution` covering the bounding box of the outer
    boundary (minX, maxX, minY, maxY).
  - Or possibly resolution is DPI or similar, but likely number of
    points.

- Implementation:

  - Determine bounding box of outer_boundary (by scanning all segments
    or using their extents).
  - Create linspace for x and y of given length = resolution.
  - Use `contains` or `field` to assign values.
  - If using occupancy:
    `data[i,j] = 1.0 if contains(x_j, y_i) else 0.0`. (We have to be
    careful with array indexing vs coordinates).
  - If using field values: we could output the signed distance field
    sampled at each grid point (that\'s like generating a heightmap for
    the shape).
  - Perhaps the name `fill` leans toward occupancy. Meanwhile,
    generating a full signed distance field might be expensive for high
    resolution (but resolution might be moderate like 100 or 200 by
    default).
  - Possibly we could allow an argument to choose what to fill with
    (like occupancy vs distance), but not mentioned in signature, likely
    they assume a default.
  - If a field strategy is set, maybe fill uses that field: e.g., if
    field_strategy is occupancy, fill returns occupancy grid; if sign
    distance strategy, fill returns a float grid of distances.
  - But the design suggests separate `FieldStrategy` classes for
    generating BaseField objects rather than arrays; still, fill could
    just use field() at each sample.

- We will define: `fill(resolution)` returns a NumPy array of floats of
  shape (resolution, resolution). If the region has a field strategy:

  - If it\'s occupancy, values will be 1.0 inside, 0.0 outside (like a
    monochrome bitmap).
  - If it\'s signed distance, the array contains the signed distance
    values (clamped perhaps if resolution is coarse).
  - If BoundedGradient, it might produce intermediate values between 0
    and 1 across boundary.
  - For generality, implement fill by: for each pixel center coordinate,
    compute `val = self.field(x,y)` and store it. So it\'s consistent
    with what `field(x,y)` does (which in turn depends on chosen
    strategy).
  - That covers all cases: just grid-sample the region's field.

<!-- -->

- This approach means if no special strategy was set, it defaults to
  some basic field (we decide what in field()).

<!-- -->

- `to_dict()`:

- `"type": "AreaRegion"`

- Should include a representation of outer_boundary and holes:
  - Could do `"outer": outer_boundary.to_dict()`, and
    `"holes": [dict(h) for h in holes]`.
  - Because CompositeCurve can be nested, that might be heavy but okay.
  - We might instead store references if those composite curves are also
    standalone objects (not usual; likely composite is only used as part
    of area).
  - Perhaps treat outer and holes as sub-objects always embedded, since
    an AreaRegion usually is a unique combination.
  - But maybe not: user could create an AreaRegion from an existing
    CompositeCurve (like define boundary composite as an object, then
    create region referencing it). If so, we can do reference by id for
    outer and holes. It\'s analogous to trimmed reference.
  - We\'ll allow referencing by id if present.

- Possibly store an indicator of field strategy, e.g.,
  `"field_strategy": "signed_distance"` if one is set (and any
  parameters for it).

- If area has material or fill patterns, could be additional fields (not
  in current scope, but extension point).

- `from_dict()`:

- Reconstruct outer via CompositeCurve.from_dict (resolving references
  if needed).

- Reconstruct holes list similarly.

- Create AreaRegion with those.

- If field_strategy info present, instantiate the corresponding
  FieldStrategy and attach it.

**Example usage:**

    # Create a filled region from a closed composite (like a rectangle and one circular hole)
    rect = CompositeCurve([...])  # assume segments forming a rectangle
    circle = ConicSection(x**2+y**2-0.5) 
    hole_curve = CompositeCurve([ curve_segment(circle, start=(0.5,0), end=(-0.5,0)) , ...])  # actually for a circle, better approach: treat conic itself as one closed segment if you allow that
    # Simpler: maybe an AreaRegion can accept an ImplicitCurve as boundary if it's closed.
    # But per design, they specifically said CompositeCurve for boundaries.
    outer_boundary = rect
    holes = [hole_curve]
    region = AreaRegion(outer_boundary, holes)
    print(region.contains(0,0))  # True if (0,0) inside rect and outside hole
    print(region.area())        # ~ area of rect minus area of hole (should compute accordingly)
    field_val = region.field(0,0)  # maybe negative (inside)
    grid = region.fill(resolution=100)  # a 100x100 grid of values
    region.plot()

One nuance: if the outer boundary or holes are given as CompositeCurve,
they might in turn have references to base curves etc. Typically, one
constructs those first. The above pseudocode for hole is incomplete (one
would need to build a closed curve for hole).

### Field Strategies and Field Objects

The design includes a notion of different **FieldStrategy** classes that
can generate field representations from an AreaRegion. Also, a hierarchy
of `BaseField` classes to represent scalar fields in a more general way
than just using ImplicitCurve or AreaRegion. This separation allows
treating fields as first-class objects that can be combined (added,
blended) and queried similarly to implicit curves.

#### FieldStrategy Interface

A `FieldStrategy` encapsulates an algorithm for creating a field (some
subclass of BaseField) from a given AreaRegion. This decouples the *type
of field* (distance, occupancy, etc.) from the region itself.

    class FieldStrategy:
        def generate_field(self, area: 'AreaRegion') -> BaseField:
            """Given an AreaRegion, return a field representation (BaseField) for it."""
            ...

Concrete strategies:  
- **SignedDistanceStrategy(FieldStrategy):**  
`generate_field(area)` produces a `BaseField` that approximates the
*signed distance field* of the region. The resulting BaseField's
`evaluate(x,y)` will give negative values inside the region (with
magnitude equal to distance to nearest boundary), positive outside
(distance to boundary), and 0 on the boundary. Implementation might
internally compute a distance function: - Possibly sample the boundary
densely (or rely on area.field method if it was implemented to do sign
distance) and create a `SampledField` (like an image) representing
distance. But a sampled field might lose accuracy if used outside the
sampled range. - Or implement BaseField with an analytic evaluation:
e.g., `evaluate(x,y)` uses the logic described in AreaRegion.field
earlier (min distance to boundaries). - Could even use Sympy if region
is simple (like if boundaries are implicit curves themselves, one could
try to combine them piecewise, but that's complicated). - Likely easier:
create a new class, say `SignedDistanceField`, that holds reference to
AreaRegion (or its boundary segments) and implements evaluate by
computing distances as needed. - Or simply have `generate_field` return
a `Field` object (the Field class described later) that wraps a function
using area.contains and area's distance logic. Possibly the simplest:
return a `Field` (which is our high-level Field interface) with a custom
lambda for evaluate and gradient, etc. - For now, we state that it
returns a BaseField (we'll detail BaseField soon).

- **OccupancyFillStrategy(FieldStrategy):**  
  This might be used for a quick inside/outside mask. It likely has
  parameters like `inside_value=1.0, outside_value=0.0` (the code
  snippet shows these in **init**). `generate_field(area)` would return
  a field that is basically the characteristic function of the region:

- `evaluate(x,y)` returns `inside_value` if area.contains(x,y) is True,
  else `outside_value`.

- `gradient(x,y)` would be zero almost everywhere (since it's constant
  inside and outside except at boundary where it\'s
  undefined/discontinuous). Possibly the gradient can be defined as zero
  vector for all non-boundary points and not worry about the
  discontinuity.

- This Field is effectively a binary image of the region.

- It could be implemented as a subclass of BaseField or via Field class
  combining things. But conceptually simple.

- **BoundedGradientStrategy(FieldStrategy):**  
  It has a `falloff: float` parameter. This likely creates a field that
  smoothly transitions from one value inside to another outside over
  some band of width = falloff around the boundary. For example, maybe
  inside_value=1, outside_value=0, and instead of a hard step, you get a
  gradient in a boundary layer:

- Possibly implemented by taking signed distance and applying a clamped
  linear or smoothstep function: e.g., if `d = signed_distance(x,y)`,
  then the field value could be:
  - 1 if d \<= 0 (inside fully).
  - 0 if d \>= falloff (fully outside).
  - A linear interpolation or smooth curve if 0 \< d \< falloff: for
    instance $value = max\left( 0,min(1,1 - d/falloff) \right)$ , which
    goes from 1 at boundary (d=0) down to 0 at d=falloff.
  - Or maybe reversed (maybe they want value 1 at boundary and 0 deep
    inside? But likely inside=1).

- `falloff` defines how thick the transition region is.

- This could be used for rendering a soft edge or for simulation (like a
  fuzzy region).

- Implementation: likely generate a BaseField that wraps the signed
  distance field of the area and applies the above formula in evaluate.

- E.g., it can create a `BlendedField` combining a constant field and
  the distance field with a smooth function. But simpler: just implement
  an evaluate that calls area.field (with distance) and then applies
  math to that result.

These strategies can be utilized by
`AreaRegion.field_representation(method)` or by setting
area.field_strategy and then using area.field / fill. The design
hints: -
`AreaRegion.field_representation(method="signed_distance") -> BaseField`
likely uses these strategies. Possibly implemented by mapping method
string to a FieldStrategy (e.g., \"signed_distance\" -\>
SignedDistanceStrategy). - The `AreaRegion.field_strategy` attribute (if
present in design) can be set (like
`region.field_strategy = SignedDistanceStrategy()`), and then maybe
`region.field(x,y)` calls that.

In our spec, we can describe that: - `AreaRegion` can have an optional
`field_strategy: FieldStrategy`. If not None, its `field` and `fill`
will use the field generated by that strategy. If None, a default (like
occupancy) is used. - Provide a method
`set_field_strategy(strategy: FieldStrategy)` or just assign attribute.

#### BaseField and Field Classes

`BaseField` is an abstract interface for a scalar field. It defines what
you can do with a field: evaluate it, get gradient, extract level sets
(contours) as implicit curves, combine with other fields, etc. Different
subclasses might store the field in different ways (analytically, as a
combination of other fields, or as a sampled grid).

    class BaseField:
        def evaluate(self, x_val: float, y_val: float) -> float: ...
        def gradient(self, x_val: float, y_val: float) -> tuple[float,float]: ...
        def level_set(self, value: float = 0.0) -> ImplicitCurve: ...
        def plot(self, xlim, ylim, resolution): ...
        def normalize(self) -> BaseField: ...
        def combine(self, other: BaseField, method: str) -> BaseField: ...

**Intended behavior of BaseField methods:** - `evaluate(x,y)`: returns
the scalar field value at (x,y). - `gradient(x,y)`: returns
$\nabla g(x,y)$ for the field $g(x,y)$ . By default, if we don't have an
analytic form, gradient can be approximated by finite difference (small
delta \~1e-6). - `level_set(value) -> ImplicitCurve`: produce an
ImplicitCurve corresponding to the contour where field = value.
Essentially, treat $g(x,y) - \text{value} = 0$ as an implicit curve. -
For fields that come directly from an implicit curve, level_set(0) would
return that curve (e.g., if Field was created from ImplicitCurve via
CurveField). - If the field is a combination or sampled, this may
involve numeric contour extraction. For analytic combinations, we can
attempt to form a sympy expression for $g(x,y)$ and subtract value, but
often g might not be a simple expression. - Possibly best done by
sampling and constructing a CompositeCurve approximation via marching
squares. - Or if field is e.g. an RFunction combination of two implicit
fields, maybe we could derive an expression as in RFunctionCurve and
return an ImplicitCurve of that expression. - At minimum, we can provide
a general approach: sample the field on a grid and run a contour
extraction (like `skimage.measure.find_contours` or similar) to get
lines for that level, then approximate those lines as CompositeCurve or
list of points. - Or utilize the `marching_squares` algorithm from SciPy
to get a polygon for value=level. - The output could be one
ImplicitCurve if the level set is a single closed curve, or multiple (if
the level set breaks into multiple components). The spec says return
ImplicitCurve -- perhaps in case of multiple components, return a
CompositeCurve containing them? Or just one and user has to know if
there are multiple. - We can define: if multiple disjoint contours at
that level, combine them into a CompositeCurve if they are closed, or
maybe return one and ignore others (not ideal). Better to return
CompositeCurve with possibly multiple sub-composites? Or a custom
MultiCurve container. - This corner case can be advanced; we might note
it as a limitation or possible future extension (multi-return).

- `plot(xlim, ylim, resolution)`: Plot the field as a heatmap or contour
  map. Could use matplotlib's `imshow` or `contourf`. For discrete
  fields like occupancy, this would show a binary image. For distance
  fields, a smooth gradient. For combined fields, something maybe more
  complex. The default could be to sample a resolution grid and use
  `imshow` with a color map (jet, etc.) for continuous values, or
  black/white for occupancy.

- Possibly allow specifying a colormap or levels, but not in interface
  signature here, keep it simple.

- `normalize() -> BaseField`: Return a new Field where the values are
  normalized to a standard range (e.g., 0 to 1). Typically:

- If original field values range from `min_val` to `max_val`, normalized
  = (field - min_val)/(max_val - min_val). But global min/max might be
  infinite if field unbounded (like distance fields go to infinity far
  away).

- Usually normalization would consider a particular domain or bounding
  box. Perhaps they intend to call `normalize()` after sampling some
  region to scale the values.

- But from design: They likely want to easily combine fields that might
  have different magnitude scales. E.g., if you have one field range
  0-100 and another 0-1, combining them directly might be uneven;
  normalizing ensures both have comparable scale.

- Implementation: If field is a simple analytic one with known range
  (like occupancy has 0/1 known, sign distance not bounded unless domain
  bound given), maybe not easy globally. Possibly do local
  normalization: maybe as needed by user with context.

- Could implement by sampling the field on a region of interest (like
  xlim/ylim if known or from last plot range) to estimate min/max, then
  create a new Field that uses those constants to scale.

- Or if we assume fields often limited (like result of some combination
  or inside finite region), we can attempt generic:
  - Evaluate field on a coarse grid within some auto-chosen bounds (like
    bounding box from any associated geometry or \[-1,1\]\^2 if unknown)
    to guess min/max, then define normalized field accordingly.
  - Or require user to specify normalization bounds optionally (not in
    interface currently).

- We can specify that `normalize()` will typically map the field values
  into \[0,1\] or \[-1,1\] depending on context. Perhaps \[0,1\] is
  safer as default. If field has negative (like sign distance has
  negative inside), do we want to preserve sign? Possibly not, maybe
  they\'d shift it to 0 for inside? Or treat negative/positive
  separately?

- Might choose: if field can take negative and positive, normalize
  separate by absolute max or something to keep sign info.

- The design didn't detail that. Possibly they consider fields can be
  both.

- Maybe define two modes: one to normalize absolute values (for sign
  distance, so inside = -1, outside = +1 at far distance?), or to clamp
  negative to 0 for inside occupancy?

- But given not specified, we\'ll say:
  - If field spans positive and negative, we can normalize such that 0
    =\> 0.5? That would distort sign meaning. Perhaps better: maintain
    sign, just divide by max(\|min\|, \|max\|) so that the extreme
    magnitude becomes 1 or -1.
  - Or produce two fields (one for sign).

- Simplicity: For now, if the field has both positive and negative,
  we\'ll normalize by absolute max (so that the largest magnitude
  becomes ±1). If it's all positive or 0-1 already, we might leave it or
  ensure 0-1.

- `combine(other, method) -> BaseField`: Combine two fields to produce a
  new one. This is a high-level method that can cover various
  operations:

- `method` could be:
  - `"add"`: new field = f1 + f2.
  - `"subtract"`: = f1 - f2.
  - `"multiply"`: = f1 \* f2.
  - `"min"` / `"maximum"`: pointwise min or max of the two field values.
  - `"smooth_min"` or `"smooth_max"`: like R-function blending with
    smoothing parameter. Possibly if method string includes a number or
    is pre-configured with some global smoothing param.
  - It could also cover blending like an average or more exotic combos.

- Implementation:
  - We might implement this by returning a `BlendedField` instance that
    stores references to field1 and field2 and the method.
    `BlendedField.evaluate` will call field1.evaluate and
    field2.evaluate and then combine results accordingly.
  - `BlendedField.gradient` similarly combines the gradients
    appropriately if differentiable:
  - For add/subtract: gradient is sum/difference of gradients.
  - For multiply: product rule: grad(f\*g) = f \* grad(g) + g \*
    grad(f).
  - For min/max: choose grad of whichever is lesser/greater. If
    smooth_min, differentiate the smooth formula.
  - Alternatively, incorporate into Field class logic: e.g.,
    `Field.combine` might produce a generic Field that knows how to
    evaluate both, but separate class is cleaner.

- We will detail `BlendedField` below as they gave it in design.

**Subclasses of BaseField (from design):**  
- `CurveField(BaseField)`: A field defined directly from an
ImplicitCurve. Essentially, it wraps an implicit curve's function as a
field (likely the simplest field where evaluate = curve.evaluate (the f
value), gradient = curve.gradient, level_set(0) returns the curve
back). - This might be exactly what the `Field` class (the high-level
wrapper) does when you pass an ImplicitCurve. The design text shows:

    class CurveField(BaseField):
        def __init__(self, curve: ImplicitCurve): ...

It likely stores the curve internally. - `evaluate(x,y)` -\>
curve.evaluate(x,y). - `gradient(x,y)` -\> curve.gradient(x,y). -
`level_set(v)` -\> ImplicitCurve of `curve.expression = v`, if v not 0,
that\'s basically shifting the constant: If original curve f(x,y)=0, the
level set f(x,y)=c would be a parallel curve (like offset, but not
exactly offset if f is not distance). \* Actually f(x,y)=c is *some*
offset-like curve but not actual constant distance; still, one can
return an ImplicitCurve with expression `curve.expression - c = 0`. \*
That ImplicitCurve might just be returned as a new ImplicitCurve object
(since `curve.expression` is sympy, do
`new_expr = self.curve.expression - value` and create
ImplicitCurve(new_expr) maybe). \* This would be correct mathematically
(the set of solutions to f=c). \* If c is 0, it\'s the original curve
(could even return self.curve or copy). \* If c is small, it might
approximate a slight offset (for small c, if f is like a signed distance
or linear, then yes; if not sign distance, then f=c yields a different
shape not exactly offset at distance c but some isosurface). \* It\'s
fine as level set definition though. - `plot` could call curve.plot (if
we want field's plot to maybe show something else? But since field is
basically the curve's scalar function, plotting it as heatmap might be
more appropriate? Possibly not needed if user just wanted to treat it as
field). \* But if someone specifically constructed Field from a curve to
then maybe combine it with another, they might not call Field.plot
often. \* We can still implement it to show, e.g., a contour or colormap
of that scalar function (which is the same as plotting the implicit's
field). - So `CurveField` is straightforward.

- `BlendedField(BaseField)`: Combines two fields with some method, as
  discussed.

- Fields: `field1: BaseField`, `field2: BaseField`, `method: str` (like
  \"add\", \"min\", etc), possibly `param` like alpha if method needs
  smoothing factor.

- Evaluate:
  - if method \"add\": return f1+f2,
  - \"subtract\": f1 - f2,
  - \"multiply\": f1 \* f2,
  - \"min\": min(f1, f2),
  - \"max\": max(f1, f2),
  - \"smooth_min\": implement formula like
    $\text{smooth\_min}(a,b) = \left( a + b - |a - b|*smoothing_{f}actor \right)/2$
    or another. Actually, since this is fields, maybe they\'d reuse the
    RFunction formulas (like one of Rfunction formulas).
  - If we allowed an alpha param, maybe the BlendedField was created
    with that. The design shows `blend_smooth(field1, field2, alpha)` as
    a standalone function. Perhaps that function creates a BlendedField
    with method \"smooth_min\" and stores alpha internally.
  - Could also incorporate alpha in method name or as an attribute of
    BlendedField.
  - \"smooth_max\": similarly for intersection blending.
  - \"average\": possibly (not listed but could).

- Gradient:

  - For differentiable combos (add, subtract, multiply), we can compute
    analytic combos of gradients:
  - add/sub: grad = grad1 + grad2,
  - multiply: grad = f2 \* grad1 + f1 \* grad2,
  - If we implement min: not differentiable at tie, but away from tie:
    gradient = grad of whichever smaller field; possibly we just pick
    one (like a propagation of gradient from the controlling field).
  - For smooth_min: differentiate the smoothing formula.
  - If implementer not comfortable deriving formula, they can always do
    a numeric gradient approach by small deltas on field.evaluate (since
    we can evaluate combined easily).
  - But likely we should specify known formulas for smooth:
  - One common smooth min formula:
    $\text{smooth\_min}_{\alpha}(a,b) = - \alpha\log\left( \exp( - a/\alpha) + \exp( - b/\alpha) \right)$
    (smooth union via softmax with negative sign).
    - This yields something approximating min with smoothness controlled
      by α. Harder to differentiate directly, but doable (it's basically
      weighted average of grads).
  - Another: polynomial smoothing: e.g., if we want C\^1 continuous min,
    one formula:
    $\text{smooth\_min}_{k}(a,b) = \frac{a + b - \sqrt{(a - b)^{2} + k^{2}}}{2}$
    . This is like R-function, where k is like alpha. If k=0, it\'s
    exact min (with cusp), if k\>0, smoothens around where a ≈ b.
    - Different literature have different forms; above is commonly used,
      derivative exists except where a=b exactly then gradient = average
      of grads.
    - If implement, gradient = 0.5\*(grad(a) + grad(b) - (
      (a-b)/sqrt((a-b)\^2+k\^2) \* (grad(a) - grad(b)) )), at points
      where sqrt is defined (a != b).
  - Actually, the given formula is smooth and differentiable for all
    a!=b. At a=b, gradient from formula yields average of grad(a) and
    grad(b) (because symmetrical).
  - That works fine, giving a smooth transition.
  - We can mention such formula or reference it as one approach.

- `level_set(value)`: If blended field is something like add or
  subtract, then f1 + f2 = c becomes an ImplicitCurve maybe representing
  some new shape. One could attempt to produce a sympy expression if
  both fields originate from sympy expressions:

  - If field1 is a CurveField from an implicit f1(x,y), and field2
    likewise f2(x,y), then f1+f2=c yields a new implicit f1+f2-c=0,
    which we can make into an ImplicitCurve easily (especially if they
    are sympy).
  - If one or both are SampledFields or something non-analytic, we
    cannot get an exact expression; might fallback to numeric contour
    extraction.
  - Possibly, `level_set` method of fields could attempt: if both fields
    are actually analytic (maybe they have an internal sympy expression
    attribute or are composition of analytic ones), derive an
    expression. If not, numeric approach.

- `plot`: for a combination field, can sample and plot like any field.

- `SampledField(BaseField)`: Represents a field from discretized data
  (e.g., an image or grid of values with known spatial bounds).

- Fields: `data: np.ndarray` (2D array of samples),
  `bounds: (x_min, x_max, y_min, y_max)` specifying what area the array
  covers in the plane.

- Evaluate: need to map (x,y) to array indices and interpolate:
  - If (x,y) within bounds, find relative position:
    `u = (x - x_min) / (x_max - x_min) * (width-1)` and similarly for v
    for y (taking care y might be inversed in array indexing).
  - Then either round to nearest indices for a piecewise constant field,
    or do bilinear interpolation of the four surrounding pixels for
    smoother result.
  - If outside bounds, decide: possibly return outside_value if an
    occupancy or perhaps extrapolate as constant (maybe assume outside
    region field decays to some constant like 0).
  - Could also treat outside as undefined and raise or return 0
    depending on context. Usually for distance fields, outside bounds
    maybe approximate as far (value beyond known region).

- Gradient: approximate by finite differences on the grid (e.g., central
  difference using neighboring cells).

- level_set(value): we can run a contour algorithm on the grid data at
  that value, returning a CompositeCurve or list of polyline
  approximations.

- combine: possible to combine SampledFields by aligning grids or
  resampling one onto another\'s grid. But easier is to upsample
  everything to an analytical combination by reading values (inefficient
  for every eval).
  - Perhaps any combine involving a SampledField should produce another
    SampledField by performing the operation on overlapping region of
    arrays. That requires interpolation of one onto the other's grid or
    define a new grid covering both extents.
  - Alternatively, define a new Field that for eval calls eval on both
    fields (with interpolation) and combines results. That dynamic
    approach might be simpler and avoids creating big arrays
    prematurely. Essentially that is like a BlendedField but underlying
    one or both are Sampled.
  - So we can just rely on our BaseField combine which doesn\'t care if
    underlying is sampled, just calls their evaluate.
  - Only if performance is needed might we implement combine
    specifically to produce a new SampledField by combining arrays (like
    adding two images pixel by pixel if they align).

**Class Field (High-level):**  
The design also shows a `Field` class with similar methods:

    class Field:
        def __init__(self, source: ImplicitCurve): ...
        def evaluate(...): ...
        def level_set(...): ...
        def gradient(...): ...
        def combine(other, method="add"): ...
        def normalize(): ...
        def plot(...): ...

This seems to mirror BaseField, possibly as a user-friendly interface.
It might either: - Inherit BaseField (making Field a concrete subclass
of BaseField, like we might do instead of using BaseField directly). -
Or wrap a BaseField instance internally. For example, `Field(curve)`
might create a `CurveField(curve)` internally and store it, and then
each method of Field calls the underlying BaseField's method. - Given
they explicitly wrote Field and also listed BaseField & subclasses,
perhaps they meant Field as a simpler façade: the user deals with Field
objects, not BaseField/CurveField classes directly. The
behind-the-scenes could be hidden.

For implementing, one might choose not to separate, but for spec: We can
describe `Field` as the main class you use to generate fields from
curves and combine them: - `Field(source)` can accept either an
ImplicitCurve or another BaseField or even an AreaRegion: \* If source
is ImplicitCurve, it initializes a CurveField internally. \* If source
is AreaRegion, maybe it uses SignedDistanceStrategy by default to create
a field (or occupancy). \* If source is already BaseField, maybe wrap it
or just store as is (like Field just holds a BaseField). \* Possibly,
`Field` itself inherits BaseField, so it could just implement evaluate
by delegating to its underlying (like composition). - The methods on
Field simply call the underlying field\'s methods and return Field or
ImplicitCurve or so accordingly, making it more convenient.

Given the possible confusion, we might simplify: treat `Field` as
synonymous with `BaseField` for usage, or as a thin wrapper. We will
specify that constructing a Field from a curve yields a CurveField
behind scenes, and combining Fields yields new Field objects (wrapping
BlendedField), etc.

**Field Operations (Standalone Functions):**  
They listed a bunch of functions: add, subtract, multiply, minimum,
maximum, blend_smooth, blur, laplacian, threshold, invert, compose.
These essentially do what Field.combine could do or other
transformations: - `add(f1,f2)` returns f1+f2 field (same as
f1.combine(f2,\"add\")). - `subtract(f1,f2)` etc. - `minimum, maximum`:
likely create a new Field that is pointwise min or max (could be
implemented via BlendedField with method \"min\"/\"max\"). -
`blend_smooth(f1,f2, alpha)`: create a smoothly blended union field.
Implementation akin to smooth_min but likely not exactly min: - It could
be like a weighted sum that near boundaries yields a smooth mix.
Possibly same formula as RFunctionCurve union earlier:
$f_{\text{smooth union}} = f1 + f2 + \sqrt{f1^{2} + f2^{2}}$ if we treat
negative inside. Actually, in field context: \* If we interpret f1 and
f2 as *signed distance fields* of shapes, a common smooth union formula
is
$\text{smooth\_min}(f1,f2;\alpha) = - \alpha\ln\left( \exp( - f1/\alpha) + \exp( - f2/\alpha) \right)$
. \* Or polynomial: $\frac{f1 + f2 - \sqrt{(f1 - f2)^{2}}}{2}$ yields
exact min (with no smoothing parameter, it's still sharp at equality).
\* To add smoothing, one might do
$\frac{f1 + f2 - \sqrt{(f1 - f2)^{2} + \alpha^{2}}}{2}$ . That is a
smooth approximation of min. \* That's likely what\'s intended by
\"quadratic blend\" etc. For union shapes, f negative inside, min
selects the more negative (the deeper inside either shape). \* The given
in code parted: They might not expect user to manually implement
formula, these high-level functions do it. \* So
`blend_smooth(field1, field2, alpha)` returns a Field (maybe type
BlendedField with method \"smooth_min\" and param alpha stored). -
`blur(field, kernel_size)`: Apply a blur (like Gaussian) to the field.
If field is sampled (like image), one could convolve the array with a
Gaussian of given kernel size (which might be sigma or kernel
half-width). - If field is analytic, maybe sample it to a grid, blur,
and return a SampledField. So blur likely results in a SampledField
output (since continuous blur of an analytic is not trivial to express
unless we have convolution formula). - Most straightforward: define an
output resolution (maybe based on some default or user-provided maybe
missing param?), then do convolution. - But since not specified, perhaps
`blur` is mainly for SampledFields or after we discretize things like
images. - Could do: if field is not sampled, first produce a sampled
representation at some resolution (like 256x256 or user-specified
environment param), then blur that. - It\'s an expensive operation in
continuous space otherwise. - `laplacian(field)`: Compute Laplacian of a
field (∇\^2 f). This is a field representing the second derivative
sum. - Could implement analytically if possible (if we have sympy
expression, we can differentiate twice). - Or if field is sampled, apply
Laplacian filter (like finite difference). - It\'s like an edge detector
on images, or for distance fields yields curvature info. - Possibly
needed for advanced analysis (maybe not high priority but included). -
`threshold(field, value)`: Create a new field that is 1 in regions where
`field(x,y) >= value` (or maybe \> or \<, need to decide) and 0
otherwise. Essentially a binary mask field derived from a continuous
field. - For example, threshold a distance field at 0 yields occupancy
of shape, or threshold a noise field at 0.5 to get a pattern. - Should
specify which side is inside: if original field was something like
intensity, threshold at e.g. 0.5 means all points where f\>=0.5 get 1,
else 0. - If original was signed distance, threshold at 0 basically
yields the inside/outside step function (similar to occupancy but from a
field). - Implementation: This yields a BaseField, possibly of type
BlendedField with a piecewise definition or a special subclass that just
stores the original field and threshold and in evaluate returns
inside/outside_value. Could implement as a custom FieldStrategy applied
to field (like occupancy but for that specific field). - For gradient:
threshold field is basically step function, gradient \~ 0 (except at
boundary where undefined). We could just return zero gradient for all
points or maybe attempt a delta at boundary which we can\'t do
discretely. But anyway, once thresholded it's not differentiable so
gradient can be considered zero (maybe not used). - `level_set` of a
thresholded field at say 0.5 might actually yield the original field's
level set at the threshold boundary, which is basically the contour we
thresholded on -- interesting relationship: thresholding and then
level_set isn\'t meaningful unless thresholding yields 0/1 and then
looking for 0.5 level to find the boundary again, kind of identity. But
threshold likely to produce occupancy-like field where boundaries are
lost or not well-defined (they become jumps). - Actually if threshold
returns exactly 0 or 1, any intermediate level in between has no volume
except maybe a fuzzy region where original exactly equal threshold. - In
effect, thresholding is a way to generate region from field. One might
more directly get region by doing field.level_set(value). But threshold
provides a field output.

- `invert(field)`: Invert the field's values:

- If field was occupancy 0/1, invert gives 1/0 (swap inside/outside).
  That effectively corresponds to complement region.

- If field is numeric, invert might mean `new_field(x,y) = -field(x,y)`
  (i.e., negate). Or if original field\'s range is \[0,1\], invert could
  also mean 1 - field.

- The design is ambiguous:
  - Possibly they mean invert intensities (for occupancy it\'s
    complement, for general perhaps 1-value if normalized).
  - But since they separate threshold (which deals with occupancy),
    invert likely means just numerical negation (which is sign inversion
    for distance fields).

- We\'ll define invert as *negation* (field with same magnitude but
  opposite sign or difference from unity? It\'s safer to do negative).

- For occupancy, that yields 1-\>-1 and 0-\>0? Actually if occupancy was
  0/1 and we do negative, get 0/-1 which isn\'t exactly the complement
  in same scale; better to treat occupancy as a special case: complement
  occupancy yield inside_value = 0, outside=1 effectively (which one
  could achieve by invert then normalize maybe).

- Alternatively, we can treat invert differently depending on if the
  field is signed (distance or other): if symmetrical around 0, invert =
  negative; if it\'s 0-1 occupancy, invert should probably yield 1 -
  val.

- But since field might not carry metadata of being occupancy or not, we
  either unify to negative (which for occupancy yields negative values
  which might not be expected).

- Could do: if field appears binary (only returns 0 or 1 exactly, maybe
  we can check type if it\'s occupancy field class), then invert returns
  occupancy with swapped values.

- For continuous \[0,1\], invert as 1 - val yields a field also \[0,1\]
  but reversed.

- Possibly the design intended invert for binary fields mostly. Or as a
  general tool to invert distance sign (i.e., treat outside as inside).

- We\'ll mention both interpretations:

  - For binary fields, invert flips 0 and 1.
  - Otherwise, invert returns a field computing `-field(x,y)`.

- `compose(fields: list[BaseField], method="sum")`: Combine multiple
  fields at once. If method=\"sum\", it sums all fields (which is like a
  reduce operation of pairwise add). If \"min\", does a pointwise
  minimum of all. If \"max\", likewise maximum of all.

- This is basically a convenience to avoid chaining combine repeatedly.
  It can be implemented by reducing via the binary combine operations:
  - sum: start with zero field or first field then add others.
  - min: use iterative min: min(f1, f2, f3) = min(f1, min(f2, f3)), etc.

- Or we could create a new class maybe CompositeField, but likely not
  necessary. Simpler to implement in one function if performance isn\'t
  an issue. Or create successive BlendedField objects.

- If large list, a balanced tree combination might be more efficient
  than left-fold if some operations heavy, but that\'s micro-optimizing.

All these operations are high-level and should produce new Field objects
(which might be underlying BlendedField or such).

**Summary of usage:**  
A typical workflow with fields: - Create fields from implicit shapes:
`field1 = Field(curve1)`, `field2 = Field(curve2)`. Under the hood they
are CurveField. - Combine fields:
`union_field = field1.combine(field2, method="smooth_min")` (or using
provided functions:
`union_field = blend_smooth(field1, field2, alpha=...)`). This yields a
new Field representing a smooth union. - Query or visualize:
`union_field.level_set(0)` to get an ImplicitCurve of the combined shape
boundary. Or `union_field.plot(...)` to see the scalar field
distribution. - Possibly convert back to region: if union_field was sign
distance, one could threshold or level_set to create AreaRegion. But
likely one would directly take level_set(0) to get shape.

### Dependencies and Performance Considerations

**Dependencies:** This module relies on: - `sympy` for symbolic math
(expressions, solving equations, differentiation). - `numpy` for
efficient numerical computations (vectorized evaluate, array
operations). - `matplotlib` for plotting if needed. - Optionally: -
`scipy.optimize` for numeric root-finding (could be used in intersection
solving when symbolic fails, e.g., using `nsolve` or `fsolve` for
equations). - `shapely` for robust geometric operations (union,
intersection, buffering (offsets), polygonization). - `scipy.ndimage` or
`opencv` for blur operations on arrays. - `numba` to JIT compile
performance-critical loops (like scanning a curve or evaluating many
points). For example, a numba-accelerated routine could speed up
computing distance to a complex boundary by parallelizing or optimizing
low-level math.

**Performance Strategies:** - Cache results of symbolic computations.
For example, store lambdified functions for evaluate and gradient after
first creation to avoid sympy overhead each time. - Use vectorized NumPy
wherever possible instead of Python loops (evaluation of a grid,
combining fields, etc.). - Use appropriate data structures: e.g., use
`numpy.float64` for arrays to interface well with sympy lambdify outputs
(which often produce numpy functions). - For intersection of curves: -
If both curves are low-degree polynomials, use sympy's `solve` or
`groebner` to get solutions exactly or parameterically. - If symbolic
fails (e.g., non-polynomial intersection or too high degree), use a
numeric approach: \* One way: pick one variable to eliminate. For
instance, solve curve1's equation for y in terms of x (Sympy `solve` can
give a formula or a list of potential solutions, or use `nsolve` for
specific guesses), then plug into curve2's equation and solve for x. \*
Or use `nsolve` on the system \[f1(x,y)=0, f2(x,y)=0\] with initial
guesses. Possibly try multiple initial guesses (maybe by scanning
bounding box for sign changes). \* Or sample one curve's points and plug
into other's function to check sign changes, then refine using bisection
or Newton. \* Another numeric strategy: treat it as optimization:
minimize f1\^2+f2\^2 using SciPy's optimize to find where both near
zero. - The function `intersect(curve1, curve2)` should output a list of
intersection coordinates. If symbolic solutions exist, get exact
rationals or algebraic numbers (Sympy might give those) and convert to
floats for output (keeping them in the dict or maybe as Sympy objects?
But likely floats are fine for use, though losing exactness). - For each
found solution, verify it is a valid real solution (no imaginary part,
within any domain restrictions). - Also filter duplicates (the same
intersection might come from solving in two ways). - If infinite
intersections (e.g., two identical curves), sympy might return param
solution or implicit set. We could handle by detecting if f1 and f2 are
multiples or so; in such case, maybe raise an exception or return an
empty list and a note that curves coincide. - If no intersection, return
an empty list.

- For offset computation:

- If using shapely: `shapely.buffer(distance)` on a polygon
  approximating the curve can give offset polygon.

- For analytic approach: If base curve is given by f(x,y)=0, the offset
  at distance d (outer) ideally is f(x,y)=d if f was sign distance. If f
  is not sign distance, you can approximate small offsets by taking
  `f(x,y) = d * ||∇f(x,y)||` or something? Actually, one known approach:
  offsetting an implicit defined by f is given by solution of f(x,y) = c
  sometimes works if c is small and f is somewhat normalized.

  - A better approximation: new implicit for offset outward:
    $f_{\text{offset}}(x,y) = f(x,y) - d = 0$ . If f\<0 inside shape,
    then f-d=0 gives f(x,y)=d, which for a sign distance f would indeed
    be the offset at distance d outside.

  - If f isn\'t normalized, f(x,y)=d yields a curve at places where
    original f equals some constant. For a general curve, this constant
    offset curve is not exactly at a fixed Euclidean distance but a
    scaled one depending on local gradient magnitude. However, if d is
    small relative to curvature radius, it\'s a first-order
    approximation.

  - The module can do that as a quick method: just return ImplicitCurve
    with expression `base.expression - d`.

  - For example, for circle f = x\^2+y\^2-1, f-0.1=0 gives x\^2+y\^2 -
    1.1 = 0, which indeed is a circle radius sqrt(1.1) \~ 1.048, which
    is an offset of \~0.048, not exactly 0.1. Actually, circle\'s sign
    distance is sqrt(x\^2+y\^2) -1, which is f\' = sqrt(x\^2+y\^2) -1.
    Setting f\'=0.1 yields sqrt(x\^2+y\^2) = 1.1, or x\^2+y\^2 = 1.21.
    The original f approach gave 1.1 (which corresponds to radius
    \~1.048). The correct radius for offset 0.1 is 1.1; our got 1.048.

  - That's an error because original f isn\'t normalized to distance.
    The difference is significant enough to matter in precise contexts.

  - So better:

  - If base is a circle x\^2+y\^2-1, gradient norm at boundary = 2r = 2
    typically (at r=1, grad(1,0)=(2,0) magnitude 2). So f(x,y)-0.1=0
    yields radius \~ sqrt(1.1) which is \~1.048, offset \~0.048. If we
    divide the offset by grad magnitude (2) we\'d get \~0.05 which
    matches that.

  - So a heuristic: for offset outward by d, one could do
    `base.expression - d * L = 0`, where L is an estimate of gradient
    length for typical points. But gradient varies along curve.

  - You could instead attempt to solve f(x,y) = t for each point where f
    was originally 0, such that the actual distance from original curve
    is d. That's complicated pointwise. Instead, perhaps:

  - Use approximate sign distance field: either compute one by sampling
    or by solving Eikonal equation (not trivial to do exactly).

  - Or offset via Minkowski sum concept: if shape is convex and nice,
    f(x,y) = 0 offset by d outward is f(x,y)=d \* \|\|∇f(x,y)\|\| maybe.
    But not globally correct.

  - The design said \"approximate offset curve\", so they likely accept
    that a method might be approximate:

  - Could indeed implement `ImplicitCurve(expr_offset)` with
    `expr_offset = sympy.expand(base.expression + C)` adjusting constant
    such that shape expands. If base has constant term (like F in
    polynomial), subtracting distance times grad magnitude might be done
    at points (not an expression though).

  - Another route: convert to polygon with many points, offset polygon
    outwards by d (like parallel curve), then fit an implicit to that.
    Fitting implicit is hard in general, but maybe one could generate a
    CompositeCurve by offsetting each segment:

  - e.g., for circle, offset is another circle easily found (increase
    radius).

  - For a general curve piece, offset curves can be significantly
    different shape (especially at corners, where you get arcs).

  - A robust approach is beyond this spec. But at least mention using
    shapely for an approximate polygon offset, then maybe converting
    that to CompositeCurve (the result of shapely.buffer for a curve
    will be a polygon, maybe approximate that with arcs/segments).

  - Considering an AI implementer, a possible compromise: if shapely is
    available, do:

  <!-- -->

  - poly = shapely.LineString(sampled_points_on_curve).buffer(distance)
        # then poly.boundary is shapely LineString(s) approximating offset boundary.
        # We can extract those coordinates and create a CompositeCurve or at least points.

    This yields an approximation. If shapely not, maybe sample, then
    manually offset points by normal vector approximations. That can
    fail around tight curvature or corners. But as \"approximate\",
    maybe okay visually.

  <!-- -->

  - For now, we specify: offset uses either a simple expression
    adjustment for known shapes or numeric approximation for general:

  - If base is a ConicSection (circle): we can compute exactly: circle:
    new radius = old radius ± d. Ellipse offset is not an ellipse (it\'s
    an \"offset curve\" which in general is a parallel curve of an
    ellipse, which is not an ellipse, but can be approximated by a
    high-degree polynomial or closed form not trivial).

  - So maybe only circle and line can offset exactly easily. Parabola
    offset is not a parabola, etc.

  - Could implement special-case: if base is circle (detect B=0, A=C in
    conic), then do new ConicSection with adjusted constant.

  - Otherwise, use shapely or sampling.

**Conclusion**: The above provides enough detail for an AI to implement
the module. The specification has enumerated all interfaces, described
integration points (to_dict/from_dict for scene, dependency usage,
etc.), given example usages, and discussed how to handle key operations
mathematically with relevant libraries. The design is comprehensive and
avoids diagrams, focusing on textual explanation.

[\[1\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,from_dict)
[\[2\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,get_subtree)
[\[3\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=2)
[\[4\]](file://file-FT3iuJbMmBAgRPmRe3Lcd4#:~:text=,marching%20squares%29%2C%20WebSocket%20events)
system_integration_v_2.md

<file://file-FT3iuJbMmBAgRPmRe3Lcd4>
