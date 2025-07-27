**An Agile Development Blueprint for the 2D Implicit Sketching System**

**Introduction: An Agile Blueprint for the Implicit Sketching System**

This document presents a comprehensive, structured sprint plan for the
development of the 2D Implicit Sketching System. It is designed to be
executed by a team of AI coders, translating the high-level Software
Design Specification and QA and Testing Strategy into an actionable,
iterative development roadmap. This plan is not merely a sequence of
tasks; it represents a deliberate engineering strategy designed to
manage complexity and mitigate risk throughout the project lifecycle.

The development philosophy is founded on three core principles derived
from the project\'s foundational documents. First, it follows a
**bottom-up, dependency-aware implementation order**. The project begins
with the mathematically pure, stateless Implicit Geometry Module.^1^ By
building and stabilizing this core engine first, we isolate the
system\'s algorithmic complexity from the complexities of state
management, persistence, and user interaction. This creates a robust
foundation upon which all subsequent application layers can be built
with confidence.

Second, the plan rigorously integrates a **Test-Driven Development (TDD)
methodology**. The provided QA strategy is not treated as a separate,
post-development validation phase but as an integral part of the
implementation contract for every feature.^1^ Each development task is
preceded by a corresponding test-creation task, ensuring that the
acceptance criteria are codified and verifiable before a single line of
feature code is written. This approach is paramount for a system with
high mathematical and algorithmic complexity, as it guarantees
correctness and prevents regressions at the most granular level.

Finally, the **task granularity is optimized for AI-driven code
generation**. Each user story is broken down into atomic, unambiguous
tasks with clearly defined inputs, outputs, dependencies, and acceptance
criteria. This structure is intended to maximize the effectiveness of AI
coding agents by providing them with precise, self-contained work units,
thereby accelerating development while maintaining the highest standards
of quality and adherence to the design specification.

The plan is structured into three major parts, systematically building
the system from its core logic outwards:

1.  **Part I: Foundational Sprints -- The Implicit Geometry Module:**
    Building the mathematical engine.

2.  **Part II: System Integration Sprints -- Scene and Data
    Management:** Implementing state management, persistence, and
    querying.

3.  **Part III: Application Interface Sprints:** Exposing the backend
    functionality through well-defined APIs for consumption by front-end
    and agent-based clients.

By following this structured blueprint, the development team will
progressively construct a powerful, reliable, and maintainable implicit
sketching system, delivering value incrementally while ensuring
architectural integrity at every stage.

**Part I: Foundational Sprints -- The Implicit Geometry Module**

This initial phase of development focuses on constructing the
mathematical core of the application: the Implicit Geometry Module. The
functionality of the entire system---from rendering paths via
get_curve_paths to scene persistence with save_scene and interactive
updates through update_parameters---is fundamentally predicated on the
correctness and stability of this module.^1^ The design of the geometry
module emphasizes pure functions and immutability, which are key to
creating a predictable and testable system.^1^

Any flaw or instability in a geometry object\'s fundamental methods,
such as evaluate, gradient, or to_dict, would inevitably cascade
upwards, manifesting as critical bugs in rendering, data persistence,
and user interaction. Consequently, these foundational sprints are the
most critical phase of the project. Significant effort is dedicated here
to building a robust, thoroughly tested mathematical engine before any
application-level or stateful logic is introduced. This front-loading of
algorithmic complexity is a deliberate risk-reduction strategy, ensuring
that the upper layers of the application are built upon a solid and
reliable foundation.

**Sprint 1: Core Infrastructure & The** ImplicitCurve **Abstract Base**

**Sprint Goal:** To establish the project\'s foundational code
structure, dependencies, and the core ImplicitCurve interface. This
sprint delivers the abstract contract that all subsequent geometric
objects will adhere to, including the critical serialization and
evaluation methods that form the backbone of the entire system.

Key Features & Implementation Tasks:

This sprint focuses on setting up the development environment and
implementing the ImplicitCurve base class. This class is not intended
for direct instantiation but serves as the abstract parent for all curve
types, defining their common interface. The implementation of its
methods, particularly evaluate and the serialization contract
(to_dict/from_dict), will set the pattern for the rest of the module.

The implementation of a robust serialization contract in this initial
sprint is of paramount importance. The entire persistence mechanism,
managed by the SceneManager, relies exclusively on the to_dict and
from_dict methods of each geometric object.^1^ A failure in this
contract within a single object would compromise the integrity of the
entire saved scene, leading to potential data loss and system
instability upon loading.^1^ Therefore, establishing and validating this
pattern from the outset is a critical risk-mitigation strategy. Any new
geometry class created in subsequent sprints must pass a similar
round-trip serialization test to be considered \"done.\"

**Sprint 1 Backlog**

| User Story/Feature                                                                  | Task ID   | Task Description                                                                                                                                                                                                                                                                                                               | Dependencies | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                                     | Estimated Complexity |
|-------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a developer, I need a configured project environment to begin development.       | GEO-S1-T1 | Initialize a new Python project repository. Configure dependency management (e.g., using pip with requirements.txt or Poetry). Add core dependencies: sympy, numpy, and pytest. Configure the pytest runner.                                                                                                                   | None         | Project can be cloned and dependencies installed successfully. pytest runs and finds tests. ^1^                                                                                                                                                        | 1                    |
| As a system, I need a base representation for any 2D implicit curve.                | GEO-S1-T2 | **Test Creation:** Write pytest unit tests for the ImplicitCurve class constructor and its evaluate method.                                                                                                                                                                                                                    | GEO-S1-T1    | Tests should cover successful instantiation with a valid sympy.Expr, and failure (raising TypeError/ValueError) with invalid inputs. Tests for evaluate must check scalar and numpy array inputs for points inside, on, and outside a known curve. ^1^ | 3                    |
|                                                                                     | GEO-S1-T3 | **Implementation:** Implement the ImplicitCurve class structure. The constructor (\_\_init\_\_) must accept a sympy.Expr and a tuple of variables ((x, y)). It must validate that the expression is a valid sympy object. Implement the evaluate method, caching a lambdify-ed function for performance with numpy arrays. ^1^ | GEO-S1-T1    | Passes tests from GEO-S1-T2. The class correctly stores the expression. The evaluate method handles both single float and numpy array inputs correctly and efficiently. ^1^                                                                            | 5                    |
| As a system, I need to compute the gradient and normal vector of an implicit curve. | GEO-S1-T4 | **Test Creation:** Write pytest unit tests for the gradient and normal methods of ImplicitCurve.                                                                                                                                                                                                                               | GEO-S1-T1    | Tests must verify that gradient returns the analytically correct vector at several points. Tests for normal must verify the result is a unit-length vector of the gradient and that a ValueError is raised for zero-magnitude gradients. ^1^           | 2                    |
|                                                                                     | GEO-S1-T5 | **Implementation:** Implement the gradient and normal methods. Use sympy.diff to pre-compute symbolic derivatives in the constructor and lambdify them for fast evaluation. The normal method should call gradient and handle the normalization, including the zero-vector case. ^1^                                           | GEO-S1-T3    | Passes tests from GEO-S1-T4. Gradient and normal vectors are computed correctly and efficiently. ^1^                                                                                                                                                   | 3                    |
| As a system, I need all geometric objects to be serializable for scene persistence. | GEO-S1-T6 | **Test Creation:** Write a pytest unit test for a to_dict/from_dict round-trip.                                                                                                                                                                                                                                                | GEO-S1-T1    | The test will create a curve, serialize it, reconstruct it, and assert that the new object is functionally identical to the original (e.g., evaluate produces the same values at test points). ^1^                                                     | 3                    |
|                                                                                     | GEO-S1-T7 | **Implementation:** Implement the to_dict and from_dict methods on ImplicitCurve. to_dict will convert the sympy expression to a string. from_dict will be a classmethod that reconstructs the object by parsing the string back into an expression using sympy.sympify. ^1^                                                   | GEO-S1-T3    | Passes the round-trip test from GEO-S1-T6. The object\'s state can be fully saved to and restored from a dictionary. ^1^                                                                                                                               | 5                    |
| As a developer, I need a way to visualize implicit curves for debugging.            | GEO-S1-T8 | **Implementation:** Implement the plot method on ImplicitCurve. It should accept xlim, ylim, and resolution parameters. The implementation will use numpy to create a grid, call the vectorized evaluate method, and use matplotlib.pyplot.contour to draw the zero-level set. ^1^                                             | GEO-S1-T3    | (Manual Verification) Calling plot() on a known curve (e.g., a circle) generates and displays a correct contour plot. The method does not crash.                                                                                                       | 2                    |

**Sprint 2: Foundational Curve Primitives**

**Sprint Goal:** To implement the foundational algebraic curve types:
ConicSection and PolynomialCurve. This sprint delivers the system\'s
ability to work with the most common and mathematically well-behaved
families of implicit curves, building upon the abstract contract
established in Sprint 1.

Key Features & Implementation Tasks:

This sprint introduces the first concrete subclasses of ImplicitCurve.
The ConicSection class will not only represent second-degree polynomials
but also provide specialized methods for geometric analysis, such as
identifying the type of conic. The PolynomialCurve will serve as a
general-purpose container for implicit curves defined by any polynomial
degree. The key focus is on implementing their specialized methods while
ensuring they correctly inherit and conform to the base class interface.

**Sprint 2 Backlog**

| User Story/Feature                                                                         | Task ID   | Task Description                                                                                                                                                                                                                                                                                   | Dependencies         | Acceptance Criteria (from QA Spec)                                                                                                                                                                                           | Estimated Complexity |
|--------------------------------------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need to represent and analyze conic sections.                               | GEO-S2-T1 | **Test Creation:** Write pytest unit tests for the ConicSection class, specifically for the conic_type and degree methods.                                                                                                                                                                         | GEO-S1-T3            | Tests must create ConicSection instances for a known circle, ellipse, parabola, and hyperbola. Assert that conic_type() returns the correct string (\"circle\", \"ellipse\", etc.) and degree() consistently returns 2. ^1^  | 2                    |
|                                                                                            | GEO-S2-T2 | **Implementation:** Implement the ConicSection class, inheriting from ImplicitCurve. The constructor accepts a general second-degree polynomial expression. Implement the conic_type method using the discriminant (B2−4AC) and coefficient analysis. Implement the degree method to return 2. ^1^ | GEO-S1-T3            | Passes tests from GEO-S2-T1. The class correctly identifies different types of conic sections based on their implicit equations. ^1^                                                                                         | 3                    |
| As a system, I need to represent general polynomial curves.                                | GEO-S2-T3 | **Test Creation:** Write pytest unit tests for the PolynomialCurve class, specifically for the degree method.                                                                                                                                                                                      | GEO-S1-T3            | Tests must create PolynomialCurve instances of varying degrees (e.g., a line, a conic, a quartic curve) and assert that the degree() method returns the correct integer value for each. ^1^                                  | 2                    |
|                                                                                            | GEO-S2-T4 | **Implementation:** Implement the PolynomialCurve class, inheriting from ImplicitCurve. Implement the degree method to compute the total degree of the polynomial expression, using sympy\'s built-in polynomial tools. ^1^                                                                        | GEO-S1-T3            | Passes tests from GEO-S2-T3. The class correctly computes the degree of arbitrary polynomial expressions. ^1^                                                                                                                | 3                    |
| As a system, I need to ensure all curve subclasses are consistent with the base interface. | GEO-S2-T5 | **Test Creation & Execution:** Create and run a regression test suite for ConicSection and PolynomialCurve that re-uses the tests for evaluate, gradient, normal, and to_dict/from_dict from Sprint 1.                                                                                             | GEO-S2-T2, GEO-S2-T4 | Both ConicSection and PolynomialCurve must pass all inherited interface tests, ensuring their behavior is consistent with the ImplicitCurve contract. Serialization round-trip must work flawlessly for both subclasses. ^1^ | 3                    |

**Sprint 3: Specialized and Procedural Curves**

**Sprint Goal:** To expand the geometry library to include
non-polynomial and procedurally-defined curves by implementing
Superellipse and ProceduralCurve. This sprint tackles the challenges of
curves defined by piecewise functions (due to absolute values) and those
without any available symbolic representation, significantly increasing
the expressive power of the module.

Key Features & Implementation Tasks:

This sprint introduces two important classes that move beyond simple
polynomials. The Superellipse class, defined by an equation involving
absolute values and variable exponents, requires careful handling of
differentiation, as its gradient is not smooth across the axes.1 The

ProceduralCurve class is a generic wrapper for curves defined by an
arbitrary Python function. This presents unique challenges, as symbolic
operations like differentiation are impossible. The implementation must
provide a numerical fallback for the gradient and a clear strategy for
serialization, acknowledging that arbitrary code cannot be persisted.^1^

**Sprint 3 Backlog**

| User Story/Feature                                                               | Task ID   | Task Description                                                                                                                                                                                                                                                                                                                                   | Dependencies | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                                                                                              | Estimated Complexity |
|----------------------------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need to represent superellipse shapes.                            | GEO-S3-T1 | **Test Creation:** Write pytest unit tests for the Superellipse class.                                                                                                                                                                                                                                                                             | GEO-S1-T3    | Tests should create a squarish superellipse (n\>2) and a diamond-like one (n\<2). Tests for evaluate must confirm points inside/outside the shape. The gradient test must verify the correct vector at a non-axis point. ^1^                                                                                    | 2                    |
|                                                                                  | GEO-S3-T2 | **Implementation:** Implement the Superellipse class, inheriting from ImplicitCurve. Provide a constructor that takes parameters a, b, and n to construct the expression using sympy.Abs. The gradient method must correctly handle the piecewise nature of the derivative. ^1^                                                                    | GEO-S1-T3    | Passes tests from GEO-S3-T1. The class correctly represents superellipses and handles their non-smooth gradients. ^1^                                                                                                                                                                                           | 3                    |
| As a system, I need to represent curves defined by arbitrary code.               | GEO-S3-T3 | **Test Creation:** Write pytest unit tests for the ProceduralCurve class.                                                                                                                                                                                                                                                                          | GEO-S1-T3    | Tests must create a ProceduralCurve from a Python lambda function. The evaluate test must confirm correct return values. The gradient test must confirm that the numerical finite-difference approximation is reasonably close to the true analytical gradient. ^1^                                             | 3                    |
|                                                                                  | GEO-S3-T4 | **Implementation:** Implement the ProceduralCurve class, inheriting from ImplicitCurve. The constructor will accept a Python callable. Override evaluate to call the stored function. Override gradient to provide a numerical approximation using finite differences. ^1^                                                                         | GEO-S1-T3    | Passes tests from GEO-S3-T3. The class can wrap arbitrary Python functions and provide core interface methods. ^1^                                                                                                                                                                                              | 5                    |
| As a system, I need a defined behavior for serializing non-serializable objects. | GEO-S3-T5 | **Test Creation:** Write a pytest unit test for the serialization behavior of ProceduralCurve.                                                                                                                                                                                                                                                     | GEO-S3-T4    | The test will call to_dict on a ProceduralCurve and assert that the output dictionary contains a placeholder or descriptive string, but not the function\'s code. The from_dict test will assert that it reconstructs a placeholder object that may not be functional, codifying the documented limitation. ^1^ | 2                    |
|                                                                                  | GEO-S3-T6 | **Implementation:** Implement to_dict and from_dict for ProceduralCurve. The implementation will not attempt to serialize the Python callable. Instead, it will store a descriptive string (e.g., \"type\": \"ProceduralCurve\", \"function\": \"custom\") to indicate its nature. Document this limitation clearly in the class\'s docstring. ^1^ | GEO-S3-T4    | Passes tests from GEO-S3-T5. The serialization behavior is predictable and well-documented. ^1^                                                                                                                                                                                                                 | 2                    |

**Sprint 4: Constructive Geometry via R-Functions**

**Sprint Goal:** To implement the RFunctionCurve to enable constructive
solid geometry (CSG-like) operations on implicit curves. This sprint
delivers the capability to perform smooth and sharp union, intersection,
and difference operations, which is a cornerstone of advanced,
procedural shape creation within the system.

Key Features & Implementation Tasks:

This sprint introduces the RFunctionCurve, a composite object that
combines two or more child curves into a single new implicit curve. The
core of this work lies in the evaluate method, which must implement the
mathematical formulas for R-functions. These functions translate logical
operations (AND, OR) into continuous algebraic expressions. The
implementation will support both sharp combinations (using min and max)
and smooth blends, where a parameter (alpha) controls the radius of the
blending effect at the seams of the shapes.1 To simplify usage,
high-level wrapper functions (

union, intersect, blend) will be created to abstract away the direct
instantiation of RFunctionCurve.^1^

**Sprint 4 Backlog**

| User Story/Feature                                                            | Task ID   | Task Description                                                                                                                                                                                                                                                                                                         | Dependencies | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                                                                   | Estimated Complexity |
|-------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need to combine implicit curves using boolean-like operations. | GEO-S4-T1 | **Test Creation:** Write pytest unit tests for sharp union and intersection operations.                                                                                                                                                                                                                                  | GEO-S2-T2    | **Union:** Test that for a union of two overlapping circles, a point inside one but not the other evaluates as \"inside\" (\<0). **Intersection:** Test that a point in the overlap evaluates as \"inside,\" while a point in only one circle evaluates as \"outside\" (\>0). ^1^    | 3                    |
|                                                                               | GEO-S4-T2 | **Implementation:** Implement the RFunctionCurve class, inheriting from ImplicitCurve. The constructor will take two child ImplicitCurve objects and an operation type. The evaluate method will call evaluate on its children and combine the results using min(f1, f2) for union and max(f1, f2) for intersection. ^1^ | GEO-S2-T2    | Passes tests from GEO-S4-T1. The class correctly performs sharp boolean-like combinations. ^1^                                                                                                                                                                                       | 5                    |
| As a system, I need to blend implicit curves smoothly.                        | GEO-S4-T3 | **Test Creation:** Write pytest unit tests for smooth blending operations.                                                                                                                                                                                                                                               | GEO-S2-T2    | Create a blend of two shapes with a non-zero alpha. The test will verify that the gradient of the resulting curve is continuous across the blend region (unlike the sharp min/max versions). A qualitative plot can be used for visual verification. ^1^                             | 3                    |
|                                                                               | GEO-S4-T4 | **Implementation:** Extend RFunctionCurve\'s evaluate method to handle smooth blending. Implement a smooth min/max approximation formula, such as the quadratic blend: F(f1​,f2​)=(f1​+f2​−(f1​−f2​)2+α2​)/2. The alpha parameter will be passed during construction. ^1^                                                       | GEO-S4-T2    | Passes tests from GEO-S4-T3. The class produces a continuous field for blended shapes. ^1^                                                                                                                                                                                           | 5                    |
| As a developer, I need convenient functions for creating blended curves.      | GEO-S4-T5 | **Implementation:** Create high-level wrapper functions: union(c1, c2), intersect(c1, c2), difference(c1, c2), and blend(c1, c2, alpha). These functions will instantiate and return the appropriate RFunctionCurve object, hiding the underlying class from the user. ^1^                                               | GEO-S4-T4    | The functions are available and correctly create RFunctionCurve instances with the specified operations and parameters.                                                                                                                                                              | 2                    |
| As a system, I need to serialize and deserialize composite R-Function curves. | GEO-S4-T6 | **Test Creation & Execution:** Write a pytest unit test for a to_dict/from_dict round-trip of an RFunctionCurve.                                                                                                                                                                                                         | GEO-S4-T4    | The test will create a blended curve, serialize it, reconstruct it, and assert that the new object is functionally identical to the original. The serialized dictionary must correctly capture the operation type, smoothing parameter, and the definitions of its child curves. ^1^ | 3                    |

**Sprint 5: Curve Segmentation and Piecewise Composition**

**Sprint Goal:** To implement TrimmedImplicitCurve and CompositeCurve,
enabling the creation of complex shapes from segments of other curves.
This sprint is essential for representing boundaries that are not
defined by a single global equation, such as architectural profiles or
custom-drawn paths.

Key Features & Implementation Tasks:

This sprint introduces two classes for piecewise geometry.
TrimmedImplicitCurve represents a portion of a base curve, defined by a
\"mask\" function that determines which points are included.1 A key
feature of this class is the

contains method, which must verify that a point lies on the base curve
*and* satisfies the mask condition. CompositeCurve assembles an ordered
sequence of these trimmed segments into a single, continuous path.^1^
Its implementation must handle connectivity checks (

is_closed) and define a consistent evaluate method for the entire
piecewise curve, likely based on a pseudo-distance metric.

**Sprint 5 Backlog**

| User Story/Feature                                                                    | Task ID   | Task Description                                                                                                                                                                                                                                                                                                                                       | Dependencies         | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                       | Estimated Complexity |
|---------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need to represent a segment of an implicit curve.                      | GEO-S5-T1 | **Test Creation:** Write pytest unit tests for TrimmedImplicitCurve, focusing on the contains method.                                                                                                                                                                                                                                                  | GEO-S2-T2            | Create a full circle and trim it to its right half (using a mask lambda x, y: x \>= 0). Assert that contains() is True for a point on the right arc and False for a point on the left arc. ^1^                                           | 3                    |
|                                                                                       | GEO-S5-T2 | **Implementation:** Implement the TrimmedImplicitCurve class, inheriting from ImplicitCurve. It will wrap a base_curve and a mask callable. Implement the contains(x, y) method to check both base_curve.evaluate(x, y) ≈ 0 and mask(x, y) == True. ^1^                                                                                                | GEO-S2-T2            | Passes tests from GEO-S5-T1. The contains method correctly identifies points on the specified segment. ^1^                                                                                                                               | 5                    |
| As a system, I need to combine multiple curve segments into a single composite curve. | GEO-S5-T3 | **Test Creation:** Write pytest unit tests for CompositeCurve, focusing on connectivity (is_closed) and containment (contains).                                                                                                                                                                                                                        | GEO-S5-T2            | Create a CompositeCurve from four quarter-circle arcs trimmed from a base circle. Assert that is_closed() returns True. Assert that contains() returns True for test points on each of the four component arcs. ^1^                      | 3                    |
|                                                                                       | GEO-S5-T4 | **Implementation:** Implement the CompositeCurve class, inheriting from ImplicitCurve. It will store an ordered list of TrimmedImplicitCurve segments. Implement is_closed() to check if the end of the last segment connects to the start of the first. Implement contains(x, y) to return true if the point is contained in any of its segments. ^1^ | GEO-S5-T2            | Passes tests from GEO-S5-T3. The class correctly represents connected, piecewise curves. ^1^                                                                                                                                             | 5                    |
| As a developer, I need to visualize trimmed and composite curves correctly.           | GEO-S5-T5 | **Implementation:** Override the plot method for both TrimmedImplicitCurve and CompositeCurve. The TrimmedImplicitCurve.plot method must only render the masked portion. The CompositeCurve.plot method should iterate and plot each of its component segments. ^1^                                                                                    | GEO-S5-T2, GEO-S5-T4 | (Manual Verification) Plotting a trimmed half-circle shows only the arc. Plotting a closed composite curve shows a continuous, closed loop. The bounding box of the plotted points for the half-circle should have min_x ≈ 0. ^1^        | 3                    |
| As a system, I need to serialize and deserialize these piecewise structures.          | GEO-S5-T6 | **Test Creation & Execution:** Write pytest unit tests for to_dict/from_dict round-trips for both TrimmedImplicitCurve and CompositeCurve.                                                                                                                                                                                                             | GEO-S5-T2, GEO-S5-T4 | The tests must verify that a reconstructed TrimmedImplicitCurve has an equivalent base curve and mask behavior. A reconstructed CompositeCurve must have the correct number of functionally identical segments in the correct order. ^1^ | 5                    |

**Sprint 6: Area Regions and Boundary Representation**

**Sprint Goal:** To implement the AreaRegion class, which represents 2D
filled areas with optional holes. This sprint marks a significant step,
moving the system\'s capabilities from representing one-dimensional
curves to representing and querying two-dimensional shapes, enabling
area-based calculations and containment tests.

Key Features & Implementation Tasks:

The central component of this sprint is the AreaRegion class. It is
defined by a closed CompositeCurve for its outer boundary and an
optional list of closed curves for its holes.1 The two most critical
methods to implement are

contains(x, y) and area(). The contains method requires a robust
point-in-polygon algorithm (e.g., ray-casting) that can handle complex,
multi-part boundaries, including holes.^1^ The

area method will likely be implemented by discretizing the curved
boundaries into polygons and using a standard formula like the Shoelace
algorithm, correctly accounting for the subtracted area of any holes.^1^

**Sprint 6 Backlog**

| User Story/Feature                                                 | Task ID   | Task Description                                                                                                                                                                                                                                                                                                                                                                                      | Dependencies | Acceptance Criteria (from QA Spec)                                                                                                                                                                                        | Estimated Complexity |
|--------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need to represent a 2D filled area with boundaries. | GEO-S6-T1 | **Implementation:** Implement the AreaRegion class. The constructor will take a closed CompositeCurve as the outer_boundary and an optional list of closed CompositeCurves as holes. The constructor must validate that all boundary curves are closed by calling their is_closed() method, raising a ValueError if not. ^1^                                                                          | GEO-S5-T4    | An AreaRegion can be instantiated with valid closed boundaries. Instantiation fails with an informative error if an open boundary is provided. ^1^                                                                        | 3                    |
| As a system, I need to test if a point is inside a complex region. | GEO-S6-T2 | **Test Creation:** Write pytest unit tests for the AreaRegion.contains method.                                                                                                                                                                                                                                                                                                                        | GEO-S6-T1    | Create a square AreaRegion with a circular hole. Assert contains() is True for a point inside the square but outside the hole. Assert False for a point inside the hole. Assert False for a point outside the square. ^1^ | 3                    |
|                                                                    | GEO-S6-T3 | **Implementation:** Implement the AreaRegion.contains(x, y) method. This implementation should use a robust point-in-polygon algorithm (e.g., ray-casting or winding number) on a polygonal approximation of the boundaries. It must correctly handle holes (a point is not contained if it falls within a hole). The use of a stable geometry library like shapely is recommended as a fallback. ^1^ | GEO-S6-T1    | Passes tests from GEO-S6-T2. The method correctly determines point containment for regions with holes. ^1^                                                                                                                | 8                    |
| As a system, I need to calculate the area of a complex region.     | GEO-S6-T4 | **Test Creation:** Write a pytest unit test for the AreaRegion.area method.                                                                                                                                                                                                                                                                                                                           | GEO-S6-T1    | Create an AreaRegion for a 10x10 square with a radius-1 circular hole. Assert that area() returns a value approximately equal to 100−π, within a reasonable tolerance for numerical approximation. ^1^                    | 2                    |
|                                                                    | GEO-S6-T5 | **Implementation:** Implement the AreaRegion.area() method. The implementation should approximate the curved boundaries as high-resolution polygons and use the Shoelace formula to calculate the area. The calculated area of all holes must be subtracted from the area of the outer boundary. ^1^                                                                                                  | GEO-S6-T1    | Passes the test from GEO-S6-T4. The method correctly calculates the area of regions with holes. ^1^                                                                                                                       | 5                    |
| As a system, I need to serialize and deserialize area regions.     | GEO-S6-T6 | **Test Creation & Execution:** Write a pytest unit test for a to_dict/from_dict round-trip of an AreaRegion.                                                                                                                                                                                                                                                                                          | GEO-S6-T1    | The test will create a region with an outer boundary and a hole, serialize it, reconstruct it, and assert that the new object is functionally identical (passes the same contains and area tests). ^1^                    | 3                    |

**Sprint 7: Advanced Scalar Fields and Pluggable Strategies**

**Sprint Goal:** To implement the BaseField hierarchy and the
FieldStrategy pattern. This sprint delivers a powerful and extensible
system for generating, combining, and manipulating scalar fields, which
are crucial for advanced visualization, procedural texturing, and
physical simulations.

Key Features & Implementation Tasks:

This sprint introduces scalar fields as first-class citizens in the
geometry module. The BaseField abstract class will define a common
interface for all field types, including methods like evaluate,
gradient, and level_set.1 Concrete implementations will include

CurveField (a field derived from an ImplicitCurve), BlendedField (a
combination of other fields), and SampledField (a field backed by a grid
of data).

Crucially, this sprint also implements the FieldStrategy design
pattern.^1^ This decouples the algorithm for generating a field from the

AreaRegion itself. Concrete strategies like SignedDistanceStrategy and
OccupancyFillStrategy will be implemented, allowing an AreaRegion to
produce different kinds of field representations on demand. This makes
the system highly extensible, as new field generation techniques can be
added simply by creating new strategy classes.

**Sprint 7 Backlog**

| User Story/Feature                                                                    | Task ID   | Task Description                                                                                                                                                                                                                                                                                                                                            | Dependencies                  | Acceptance Criteria (from QA Spec)                                                                                                                                                                                    | Estimated Complexity |
|---------------------------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need a unified interface for all scalar fields.                        | GEO-S7-T1 | **Implementation:** Implement the abstract BaseField class with abstract methods evaluate, gradient, and level_set. Implement the CurveField subclass, which wraps an ImplicitCurve. Its evaluate method delegates to the curve\'s evaluate. Its level_set(0) should return an equivalent of the original curve. ^1^                                        | GEO-S1-T3                     | A CurveField can be created from any ImplicitCurve. Its methods behave as specified. level_set(0) on a CurveField created from a circle returns a curve that is functionally a circle. ^1^                            | 3                    |
| As a system, I need to combine scalar fields algebraically.                           | GEO-S7-T2 | **Implementation:** Implement the BlendedField subclass of BaseField. It should take two child BaseFields and an operation method (\"add\", \"multiply\", \"min\", etc.). Its evaluate method will perform the specified operation on the results from its children. ^1^                                                                                    | GEO-S7-T1                     | Create two CurveFields. Create a BlendedField to add them. Assert that the evaluate method of the resulting field at a sample point is the sum of the evaluations of the child fields. ^1^                            | 5                    |
| As a system, I need to generate a signed distance field from an area.                 | GEO-S7-T3 | **Test Creation:** Write a pytest unit test for the SignedDistanceStrategy.                                                                                                                                                                                                                                                                                 | GEO-S6-T3                     | Apply the strategy to an AreaRegion. Test that the resulting field\'s evaluate returns a small negative value just inside the boundary, a small positive value just outside, and approximately 0 on the boundary. ^1^ | 3                    |
|                                                                                       | GEO-S7-T4 | **Implementation:** Implement the SignedDistanceStrategy. Its generate_field method will take an AreaRegion and return a BaseField object whose evaluate(x, y) method computes the signed distance to the region\'s boundary. This involves finding the minimum distance to any boundary segment and using region.contains(x, y) to determine the sign. ^1^ | GEO-S6-T3, GEO-S7-T1          | Passes tests from GEO-S7-T3. The strategy generates a field that correctly represents the signed distance. ^1^                                                                                                        | 8                    |
| As a system, I need to generate a binary occupancy field from an area.                | GEO-S7-T5 | **Implementation:** Implement the OccupancyFillStrategy. Its generate_field method will return a BaseField whose evaluate(x, y) method returns a configured inside_value (e.g., 1.0) if region.contains(x, y) is true, and an outside_value (e.g., 0.0) otherwise. ^1^                                                                                      | GEO-S6-T3, GEO-S7-T1          | Apply the strategy to an AreaRegion. Assert that the resulting field evaluates to 1.0 for points inside and 0.0 for points outside. ^1^                                                                               | 2                    |
| As a system, I need to generate fields from an AreaRegion using pluggable strategies. | GEO-S7-T6 | **Implementation:** Add a method to the AreaRegion class, such as get_field(strategy: FieldStrategy) -\> BaseField. This method will take a strategy instance, call its generate_field method with self, and return the resulting BaseField. ^1^                                                                                                            | GEO-S6-T1, GEO-S7-4, GEO-S7-5 | Calling region.get_field with an instance of SignedDistanceStrategy returns a valid signed distance field. Calling it with OccupancyFillStrategy returns a valid occupancy field. ^1^                                 | 2                    |

**Part II: System Integration Sprints -- Scene and Data Management**

With the Implicit Geometry Module now complete and thoroughly tested,
the project transitions to building the application\'s state management
and persistence layers. This phase introduces the SceneManager, the
single stateful component in the core backend architecture. While the
geometry module is pure and stateless, and the graphics and MCP layers
are merely interfaces, the SceneManager is the central orchestrator
responsible for maintaining a consistent and coherent world state.^1^

All object creation, deletion, and modification must be channeled
through the SceneManager. It is solely responsible for assigning and
managing unique object IDs, applying visual styles, and defining group
relationships---metadata that exists outside the pure geometry of the
objects themselves.^1^ Furthermore, the critical functions of
persistence,

save_scene and load_scene, are orchestrated by the SceneManager, which
directs the to_dict and from_dict calls on the objects it contains.^1^

The testing focus for this phase must therefore shift to state
consistency. Following any operation (add, remove, group, set_style),
tests must rigorously verify not only the direct outcome of the
operation but also the integrity of the entire scene. This includes
checking for dangling references, ensuring correct object counts, and
validating that group memberships and style associations remain
consistent and correct.

**Sprint 8: The Scene Manager Core**

**Sprint Goal:** To implement the core SceneManager class, focusing on
object lifecycle management (add, remove, get) and the association of
visual styles. This sprint delivers the central registry that will
manage the application\'s entire runtime state.

Key Features & Implementation Tasks:

This sprint lays the groundwork for all state management. The
SceneManager class will be created with internal data structures (e.g.,
Python dictionaries) to store geometric objects, their styles, and
later, their group affiliations. The core object management methods
(add_object, remove_object, get_object, list_objects) will be
implemented. A critical feature is the enforcement of unique object IDs;
the add_object method must reject any attempt to add an object with a
pre-existing ID to prevent state corruption.1 Concurrently, the basic
style management methods (

set_style, get_style) will be implemented to associate arbitrary style
dictionaries with object IDs.

**Sprint 8 Backlog**

| User Story/Feature                                                           | Task ID   | Task Description                                                                                                                                                                                                                             | Dependencies | Acceptance Criteria (from QA Spec)                                                                                                                                                                           | Estimated Complexity |
|------------------------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a system, I need a central manager for all scene objects and their state. | SCM-S8-T1 | **Implementation:** Implement the SceneManager class structure. It will contain internal dictionaries to store objects (mapping ID to object instance) and styles (mapping ID to style dictionary). ^1^                                      | GEO-S1-T7    | The class can be instantiated. Internal registries are initialized and empty.                                                                                                                                | 2                    |
| As a system, I need to add and retrieve objects from the scene.              | SCM-S8-T2 | **Test Creation:** Write pytest unit tests for add_object, get_object, and list_objects. Include a test case for adding an object with a duplicate ID.                                                                                       | SCM-S8-T1    | Tests must verify that after adding, an object can be retrieved via get_object and its ID appears in list_objects. The duplicate ID test must assert that a ValueError or KeyError is raised. ^1^            | 3                    |
|                                                                              | SCM-S8-T3 | **Implementation:** Implement add_object(obj_id, obj, style), get_object(obj_id), and list_objects(). The add_object method must check for pre-existing IDs and raise an error if a conflict is found. ^1^                                   | SCM-S8-T1    | Passes tests from SCM-S8-T2. Object lifecycle is correctly managed. ^1^                                                                                                                                      | 3                    |
| As a system, I need to remove objects from the scene.                        | SCM-S8-T4 | **Test Creation:** Write pytest unit tests for remove_object. Include a test for removing a non-existent object.                                                                                                                             | SCM-S8-T3    | The test will add an object, then remove it, and verify it is no longer retrievable via get_object or present in list_objects. The non-existent ID test must assert that an appropriate error is raised. ^1^ | 2                    |
|                                                                              | SCM-S8-T5 | **Implementation:** Implement remove_object(obj_id). This method must remove the object from the object registry and also remove its associated style from the style registry. It should raise an error if the ID does not exist. ^1^        | SCM-S8-T1    | Passes tests from SCM-S8-T4. Removing an object correctly cleans up all its associated state. ^1^                                                                                                            | 3                    |
| As a system, I need to manage the visual style of each object.               | SCM-S8-T6 | **Test Creation:** Write pytest unit tests for set_style and get_style.                                                                                                                                                                      | SCM-S8-T3    | The test will add an object, set its style, and use get_style to verify the style was stored correctly. It will then update the style and verify the changes. ^1^                                            | 2                    |
|                                                                              | SCM-S8-T7 | **Implementation:** Implement set_style(obj_id, style) and get_style(obj_id). These methods will operate on the internal style dictionary. set_style should handle both creating a new style entry and merging/updating an existing one. ^1^ | SCM-S8-T1    | Passes tests from SCM-S8-T6. Object styles can be reliably set, updated, and retrieved. ^1^                                                                                                                  | 3                    |

**Sprint 9: Scene Persistence, Grouping, and Queries**

**Sprint Goal:** To extend the SceneManager with persistence
(save/load), object grouping, and spatial querying capabilities. This
sprint makes the scene state durable, enables more powerful organization
of objects, and provides essential functionality for interactive
selection tools.

Key Features & Implementation Tasks:

This sprint completes the SceneManager\'s core functionality. The most
critical features are save_scene and load_scene. The save_scene method
will orchestrate the serialization process, iterating through all
managed objects, calling their to_dict methods, and writing the
collected data into a structured JSON file. load_scene will perform the
reverse operation, dynamically reconstructing objects from the file
using their \"type\" identifier and the from_dict classmethod.1

Grouping functionality (set_group, update_group_style) will be added to
allow multiple objects to be controlled as a single unit. Finally, the
objects_in_bbox method will be implemented to enable spatial queries, a
necessary component for area-based selection in a UI.^1^

**Sprint 9 Backlog**

| User Story/Feature                                                           | Task ID   | Task Description                                                                                                                                                                                                                                                                                               | Dependencies               | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                                                                                 | Estimated Complexity |
|------------------------------------------------------------------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a user, I want to save my scene to a file and load it back later.         | SCM-S9-T1 | **Test Creation:** Write a pytest unit test for a full save/load round-trip.                                                                                                                                                                                                                                   | SCM-S8-T3, All GEO Sprints | Create a scene with multiple object types (e.g., ConicSection, CompositeCurve), styles, and groups. Save it, then load it into a new SceneManager. Assert that the new scene is functionally identical to the original (object count, types, styles, and group memberships are all preserved). ^1^ | 5                    |
|                                                                              | SCM-S9-T2 | **Implementation:** Implement save_scene(filename). This method will iterate through the object, style, and group registries and serialize the entire scene state to a JSON file, using the objects\' to_dict methods. ^1^                                                                                     | SCM-S8-T3                  | Passes the save portion of the test from SCM-S9-T1. A valid, structured JSON file is created. ^1^                                                                                                                                                                                                  | 5                    |
|                                                                              | SCM-S9-T3 | **Implementation:** Implement load_scene(filename). This method will parse the JSON file, iterate through the object definitions, dynamically find the correct geometry class based on the \"type\" field, and use the class\'s from_dict method to reconstruct each object before adding it to the scene. ^1^ | SCM-S9-T2                  | Passes the full round-trip test from SCM-S9-T1. The scene state is perfectly restored from a file. ^1^                                                                                                                                                                                             | 8                    |
| As a user, I want to group objects together to manipulate them as one.       | SCM-S9-T4 | **Test Creation:** Write pytest unit tests for set_group and update_group_style.                                                                                                                                                                                                                               | SCM-S8-T3                  | Create a group of two objects. Call update_group_style to set a new color. Assert via get_style that both objects in the group have the new color, while a non-grouped object remains unchanged. ^1^                                                                                               | 3                    |
|                                                                              | SCM-S9-T5 | **Implementation:** Implement set_group(group_id, object_ids) to manage a group registry (dict mapping group ID to a list of object IDs). Implement update_group_style(group_id, style) to iterate through a group\'s members and call set_style on each. ^1^                                                  | SCM-S8-T7                  | Passes tests from SCM-S9-T4. Grouping and group-based style propagation work correctly. ^1^                                                                                                                                                                                                        | 3                    |
| As a system, I need to find all objects within a specific area of the scene. | SCM-S9-T6 | **Test Creation:** Write a pytest unit test for objects_in_bbox.                                                                                                                                                                                                                                               | SCM-S8-T3                  | Populate a scene with objects at known locations. Perform a query with a bounding box that encloses only a subset of them. Assert that the returned list of object IDs is correct and complete. Test an empty intersection case. ^1^                                                               | 2                    |
|                                                                              | SCM-S9-T7 | **Implementation:** Implement objects_in_bbox(bbox). This will require iterating through all objects in the scene, obtaining a bounding box for each geometric object (this may require adding a bounding_box method to the ImplicitCurve base class), and checking for intersection with the query bbox. ^1^  | SCM-S8-T3                  | Passes tests from SCM-S9-T6. The method correctly identifies all objects intersecting the given bounding box. ^1^                                                                                                                                                                                  | 5                    |

**Part III: Application Interface Sprints**

With a feature-complete and robust backend engine and state manager, the
final phase of development focuses on exposing this power to the outside
world. These sprints construct the well-defined API layers that will be
consumed by a front-end UI, an AI agent, or other external services.
This involves building the Graphics Backend Interface, which translates
the internal scene representation into renderable data, and the Model
Context Protocol (MCP) layer, which provides a command-based interface
for inspection and manipulation of the scene.

**Sprint 10: The Graphics Backend and MCP Layer**

**Sprint Goal:** To implement the Graphics Backend Interface for
rendering data extraction and the initial layer of the Model Context
Protocol (MCP) for external control. This sprint builds the primary APIs
that a front-end application will consume to visualize the scene and
perform basic modifications.

Key Features & Implementation Tasks:

This sprint focuses on creating the two main \"façades\" for the
backend. The Graphics Backend Interface will be a module or class whose
methods (get_curve_paths, get_field_data, etc.) query the SceneManager
and the underlying geometry objects to produce structured, render-ready
data.1 For example,

get_curve_paths will need to get a curve object, generate a polyline
approximation of its shape, and then combine that with the style
information stored in the SceneManager.

Simultaneously, the initial MCP handling logic will be implemented
within the SceneManager via the handle_mcp_command method. This method
will act as a central dispatcher, parsing incoming command dictionaries
and routing them to the appropriate internal functions. This sprint will
cover the foundational commands: create_object, delete_object, and
describe_object.^1^

**Sprint 10 Backlog**

| User Story/Feature                                                                 | Task ID    | Task Description                                                                                                                                                                                                                                                                                                                              | Dependencies         | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                   | Estimated Complexity |
|------------------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As a renderer, I need to get approximate polylines for all curves in the scene.    | API-S10-T1 | **Test Creation:** Write pytest integration tests for get_curve_paths.                                                                                                                                                                                                                                                                        | SCM-S9-T2            | Create a scene with a simple curve and a specific style. Call get_curve_paths and assert that the output contains a polyline whose points lie on the curve and whose style dictionary matches the one in the SceneManager. ^1^       | 3                    |
|                                                                                    | API-S10-T2 | **Implementation:** Implement the get_curve_paths method in the Graphics Backend Interface. This method will query the SceneManager for all curve objects, call a method on each to get a polyline approximation (e.g., by sampling or using a contouring algorithm), and combine the points with style data from SceneManager.get_style. ^1^ | SCM-S9-T2            | Passes tests from API-S10-T1. The method returns correctly structured data for rendering curves. ^1^                                                                                                                                 | 5                    |
| As a renderer, I need to get sampled grid data for all scalar fields in the scene. | API-S10-T3 | **Implementation:** Implement the get_field_data method in the Graphics Backend Interface. This method will query the SceneManager for all field objects, call the evaluate method for each on a grid defined by the resolution and bounds parameters, and return the resulting numpy array along with style metadata (e.g., colormap). ^1^   | SCM-S9-T2, GEO-S7-T1 | (Manual Verification) Calling get_field_data for a scene with a field object returns a dictionary with a correctly shaped numpy array and associated metadata. ^1^                                                                   | 3                    |
| As an external agent, I need a protocol to control the scene.                      | API-S10-T4 | **Implementation:** In SceneManager, implement the handle_mcp_command(command_dict) method. This will be a dispatcher that inspects the \"command\" field of the input dictionary and routes to the appropriate internal function. Initially, it will be a skeleton for future commands. ^1^                                                  | SCM-S9-T2            | The method exists and can parse a command dictionary. It fails gracefully for unknown commands.                                                                                                                                      | 2                    |
| As an agent, I need to create and delete objects via MCP.                          | API-S10-T5 | **Test Creation:** Write pytest tests for the create_object and delete_object MCP commands.                                                                                                                                                                                                                                                   | API-S10-T4           | Send a create_object command via handle_mcp_command and verify the object is added to the SceneManager. Send a delete_object command and verify it is removed. Assert that command responses indicate success/failure correctly. ^1^ | 3                    |
|                                                                                    | API-S10-T6 | **Implementation:** Implement the logic within handle_mcp_command to handle the create_object and delete_object commands. This will involve parsing the command arguments and calling the SceneManager\'s own add_object and remove_object methods. ^1^                                                                                       | API-S10-T4           | Passes tests from API-S10-T5. The MCP layer can successfully manage the object lifecycle. ^1^                                                                                                                                        | 5                    |
| As an agent, I need to query the properties of an object via MCP.                  | API-S10-T7 | **Implementation:** Implement the logic for the describe_object MCP command. This handler will call SceneManager.get_object and then the object\'s to_dict method to return a serializable description. ^1^                                                                                                                                   | API-S10-T4           | Send a describe_object command for an existing object. Assert that the returned JSON contains the correct type and data for that object. ^1^                                                                                         | 2                    |

**Sprint 11: Full MCP Command Implementation and Rendering Services**

**Sprint Goal:** To complete the implementation of all specified MCP
commands and the offline rendering services (render_image,
render_animation). This sprint finalizes the entire backend feature set,
delivering a fully controllable and observable system ready for UI
integration.

Key Features & Implementation Tasks:

This final backend sprint focuses on implementing the remaining, more
complex MCP commands within the handle_mcp_command dispatcher. This
includes commands that modify the state of existing objects, such as
update_parameters, set_style, and set_field_strategy, as well as the
command for managing groups, group_objects.1

In parallel, the offline rendering services will be implemented in the
SceneManager. The render_image method will leverage the already-built
Graphics Backend Interface to fetch all renderable data and use a
headless library like matplotlib to generate a static image file. The
render_animation method will build upon this, creating a sequence of
frames by repeatedly calling a user-provided animation function (which
modifies the scene) and rendering each state to an image, finally
compiling the frames into a GIF or video file.^1^

**Sprint 11 Backlog**

| User Story/Feature                                                               | Task ID    | Task Description                                                                                             | Dependencies          | Acceptance Criteria (from QA Spec)                                                                                                                                                                                                | Estimated Complexity |
|----------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| As an agent, I need to modify the parameters of an object via MCP.               | API-S11-T1 | **Test Creation & Implementation:** Implement and test the update_parameters MCP command handler.            | API-S10-T4            | Send an update_parameters command for a curve (e.g., changing a circle\'s radius). Verify by retrieving the object and calling its evaluate method that its geometry has changed as expected. ^1^                                 | 5                    |
| As an agent, I need to manage styles and groups via MCP.                         | API-S11-T2 | **Test Creation & Implementation:** Implement and test the set_style and group_objects MCP command handlers. | API-S10-T4            | Test group_objects by sending the command, then verify the grouping by sending a set_style command for the new group ID and asserting that the style propagates to all members. ^1^                                               | 5                    |
| As an agent, I need to control the field generation strategy of an area via MCP. | API-S11-T3 | **Test Creation & Implementation:** Implement and test the set_field_strategy MCP command handler.           | API-S10-T4, GEO-S7-T6 | Send the command to an AreaRegion object. Verify the change by retrieving the object and checking its field generation behavior (e.g., it now produces signed distance values). ^1^                                               | 3                    |
| As a user, I want to render a static image of the current scene.                 | API-S11-T4 | **Test Creation & Implementation:** Implement and test the SceneManager.render_image method.                 | API-S10-T2            | Call render_image for a simple scene. Assert that an image file (e.g., PNG) is created and is not empty. ^1^                                                                                                                      | 5                    |
| As a user, I want to render an animation of the scene over time.                 | API-S11-T5 | **Test Creation & Implementation:** Implement and test the SceneManager.render_animation method.             | API-S11-T4            | Call render_animation with a trivial animate_fn that changes an object\'s color over 5 frames. Assert that an animated GIF file is created. Using an image library, assert that the resulting file contains exactly 5 frames. ^1^ | 8                    |

**Conclusion: Backend Completion and Path to UI Development**

The successful completion of this eleven-sprint plan results in a
feature-complete, robust, and rigorously tested backend system for 2D
implicit sketching. Through a methodical, bottom-up approach, the
project has systematically built from a foundation of pure mathematical
constructs to a full-featured, stateful scene management engine. Every
component, from the ImplicitCurve base class to the SceneManager and its
external APIs, has been developed and validated against a comprehensive,
test-first quality assurance strategy.

The Implicit Geometry Module provides a powerful and extensible library
for representing a vast range of 2D shapes, supporting advanced
operations like smooth blending, segmentation, and field generation. The
SceneManager offers a stable, centralized system for managing scene
state, persistence, and object metadata. Finally, the Graphics Backend
Interface and the Model Context Protocol (MCP) provide clean,
well-defined APIs that decouple the backend logic from any specific
client implementation.

With these components in place and validated, the backend is now fully
prepared to serve as a stable foundation for a parallel front-end
development effort. A UI team can proceed with high confidence,
consuming the well-documented and tested APIs to build a rich,
interactive user experience. The system is ready to be integrated with a
rendering engine, an AI agent, or any other service that can communicate
via the Model Context Protocol, marking the successful conclusion of the
backend development phase.
