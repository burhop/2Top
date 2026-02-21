# Conic Section Contract

## Overview
This contract defines the expected behavior for the ConicSection class implementation.

## Interface Contract

### Constructor
- **Input**: `expression: sp.Expr`, `variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None`
- **Output**: ConicSection instance
- **Behavior**: Creates a conic section from a symbolic expression

### Methods

#### conic_type()
- **Input**: None
- **Output**: String indicating conic type ("circle", "ellipse", "parabola", "hyperbola", "degenerate")
- **Behavior**: Classifies the conic section using discriminant analysis

#### evaluate(x_val, y_val)
- **Input**: x coordinate(s), y coordinate(s)
- **Output**: Function value(s) at the given point(s)
- **Behavior**: Evaluates the conic equation at given point(s)

#### on_curve(x_val, y_val, tolerance=1e-3)
- **Input**: x coordinate(s), y coordinate(s), tolerance
- **Output**: Boolean or array of booleans indicating if points are on the curve
- **Behavior**: Tests if point(s) are on the conic section with specified tolerance

#### bounding_box()
- **Input**: None
- **Output**: Tuple (xmin, xmax, ymin, ymax) representing the bounding box
- **Behavior**: Calculates the bounding box for the conic section

## Mathematical Expectations

### Discriminant Analysis
For a conic section in general form Ax² + Bxy + Cy² + Dx + Ey + F = 0:
- Discriminant = B² - 4AC
- If discriminant < 0: ellipse (circle if A = C and B = 0)
- If discriminant = 0: parabola
- If discriminant > 0: hyperbola

### Evaluation Convention
- Returns 0 for points on the curve
- Returns negative values for points inside closed curves
- Returns positive values for points outside closed curves