"""Enclosures of mathematical sublevel sets, separate from display hints."""

from dataclasses import dataclass
from functools import lru_cache
import math
from numbers import Real

import numpy as np
import sympy as sp


@dataclass(frozen=True)
class SublevelBounds:
    """A finite enclosing box, a proved empty set, or unavailable information."""

    kind: str
    box: tuple | None = None
    reason: str = ""

    def __post_init__(self):
        if self.kind not in {"bounded", "empty", "unknown"}:
            raise ValueError("Invalid sublevel bounds kind")
        if self.kind == "bounded":
            if (
                not isinstance(self.box, tuple)
                or len(self.box) != 4
                or not all(math.isfinite(v) for v in self.box)
                or self.box[0] > self.box[1]
                or self.box[2] > self.box[3]
            ):
                raise ValueError("A bounded result requires a finite ordered box")
        elif self.box is not None:
            raise ValueError("Empty and unknown bounds have no box")


def rational_level(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (Real, sp.Rational, sp.Float)
    ):
        raise ValueError("Level must be a finite real number")
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        raise ValueError("Level must be a finite real number")
    if isinstance(value, sp.Float) and value.is_finite is not True:
        raise ValueError("Level must be a finite real number")
    try:
        result = sp.Rational(value)
        if not isinstance(result, sp.Rational):
            raise ValueError("Level must be a finite real number")
        return result
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Level must be a finite real number") from error


def _outward_endpoint(center, square, direction):
    """Check a float endpoint against an exact rational squared-distance test."""
    try:
        candidate = float((center + direction * sp.sqrt(square)).evalf(50))
    except (TypeError, ValueError, OverflowError):
        return None
    for _ in range(8):
        if not math.isfinite(candidate):
            return None
        delta = sp.Rational(candidate) - center
        if direction * delta >= 0 and delta**2 >= square:
            return candidate
        candidate = math.nextafter(candidate, math.copysign(math.inf, direction))
    return None


@lru_cache(maxsize=256)
def quadratic_sublevel_bounds(expression, variables, level):
    """Exact rational quadratic completion with checked float enclosures.

    Rationalize stored Float atoms before expansion, so translated factored
    expressions do not lose their small constant terms during extraction.
    Other symbolic coefficients and unsupported fields remain unknown.
    """
    if not isinstance(expression, sp.Expr) or len(variables) != 2:
        return SublevelBounds("unknown", reason="No symbolic quadratic field")
    try:
        exact = expression.xreplace(
            {v: sp.Rational(v) for v in expression.atoms(sp.Float)}
        )
        polynomial = sp.Poly(exact, *variables)
        if polynomial.total_degree() > 2 or any(
            not isinstance(c, sp.Rational) for c in polynomial.coeffs()
        ):
            return SublevelBounds(
                "unknown", reason="Only real rational/Float quadratics are supported"
            )
        coefficients = polynomial.as_dict()
        a, b, c, d, e, f = (
            coefficients.get(power, sp.Integer(0))
            for power in [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]
        )
        if a == b == c == d == e == 0:
            return (
                SublevelBounds("empty")
                if f > level
                else SublevelBounds(
                    "unknown", reason="Constant sublevel is the whole plane"
                )
            )
        determinant = a * c - b * b / 4
        if a <= 0 or determinant <= 0:
            return SublevelBounds(
                "unknown", reason="Quadratic is not positive definite"
            )
        cx, cy = (
            (b * e / 2 - c * d) / (2 * determinant),
            (b * d / 2 - a * e) / (2 * determinant),
        )
        minimum = f + (d * cx + e * cy) / 2
        radius_squared = level - minimum
        if radius_squared < 0:
            return SublevelBounds("empty")
        sx, sy = radius_squared * c / determinant, radius_squared * a / determinant
        box = tuple(
            _outward_endpoint(center, square, direction)
            for center, square in [(cx, sx), (cy, sy)]
            for direction in (-1, 1)
        )
        if any(v is None for v in box):
            return SublevelBounds("unknown", reason="No checked finite float enclosure")
        return SublevelBounds("bounded", box)
    except (TypeError, ValueError, OverflowError, sp.PolynomialError):
        return SublevelBounds(
            "unknown", reason="Unsupported symbolic quadratic coefficients"
        )


def union_bounds(first, second):
    if first.kind == "unknown" or second.kind == "unknown":
        return SublevelBounds("unknown", reason="A union operand has unknown bounds")
    if first.kind == "empty":
        return second
    if second.kind == "empty":
        return first
    a, b = first.box, second.box
    return SublevelBounds(
        "bounded", (min(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), max(a[3], b[3]))
    )


def intersection_bounds(first, second):
    if first.kind == "empty" or second.kind == "empty":
        return SublevelBounds("empty")
    if first.kind == "unknown":
        return second
    if second.kind == "unknown":
        return first
    a, b = first.box, second.box
    box = (max(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]))
    if box[0] > box[1] or box[2] > box[3]:
        return SublevelBounds("empty")
    return SublevelBounds("bounded", box)
