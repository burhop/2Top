# 2D Implicit Geometry Module

A comprehensive framework for representing and manipulating planar curves defined implicitly by equations f(x,y) = 0.

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

## Sprint 1 Implementation

This implements the foundational ImplicitCurve abstract base class with:

- Core evaluation methods (evaluate, gradient, normal)
- Serialization support (to_dict, from_dict)
- Visualization capabilities (plot)
- Comprehensive test coverage

## Usage

```python
import sympy as sp
from geometry.implicit_curve import ImplicitCurve

# Create symbols
x, y = sp.symbols('x y')

# Define a circle: x^2 + y^2 - 1 = 0
circle_expr = x**2 + y**2 - 1
circle = ImplicitCurve(circle_expr, variables=(x, y))

# Evaluate at a point
value = circle.evaluate(0.5, 0.5)  # Should be negative (inside)

# Get gradient
grad = circle.gradient(1.0, 0.0)  # Should be (2, 0)

# Plot the curve
circle.plot(xlim=(-2, 2), ylim=(-2, 2))
```
