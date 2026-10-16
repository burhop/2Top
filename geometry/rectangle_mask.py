"""Immutable closed rational rectangle predicate for native trim proofs."""

from dataclasses import dataclass, field
import math
import re

import numpy as np
import sympy as sp

from .numeric import broadcast_coordinates


def _bound(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, float, np.integer, np.floating, sp.Rational, sp.Float)
    ):
        raise ValueError("Rectangle bounds must be finite rational or float scalars")
    if isinstance(value, np.floating):
        if value.dtype.itemsize > 8:
            raise ValueError("Rectangle bounds support at most binary64 numpy floats")
        value = float(value)
    if isinstance(value, np.integer):
        value = int(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Rectangle bounds must be finite")
    if isinstance(value, sp.Float):
        _, _, exponent, bits = value._mpf_
        if value._prec > 4096 or abs(exponent) + bits > 4096:
            raise ValueError("Rectangle bound exceeds coefficient limits")
    try:
        rational = sp.Rational(value)
        nearest = float(rational)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Rectangle bounds require finite float conversion") from error
    if (
        not math.isfinite(nearest)
        or int(rational.p).bit_length() > 4096
        or int(rational.q).bit_length() > 4096
    ):
        raise ValueError("Rectangle bound exceeds finite coefficient limits")
    return rational


def _directed(value, lower):
    nearest = float(value)
    exact = sp.Rational(nearest)
    if lower and exact < value:
        return math.nextafter(nearest, math.inf)
    if not lower and exact > value:
        return math.nextafter(nearest, -math.inf)
    return nearest


@dataclass(frozen=True, slots=True)
class RectangleMask:
    """Closed [xmin,xmax] x [ymin,ymax] with exact stored rational bounds.

    Use as ``TrimmedImplicitCurve(base, RectangleMask(...))``. Float bounds mean
    their exact stored binary values. Directed float thresholds make scalar and
    broadcast array comparisons agree with those rational inequalities for
    finite binary64 coordinates. Degenerate boxes are valid. Nonfinite,
    unsupported or excessively large bounds raise ValueError.
    """

    xmin: object
    xmax: object
    ymin: object
    ymax: object
    _float_bounds: tuple = field(init=False, repr=False)

    def __post_init__(self):
        for name in ("xmin", "xmax", "ymin", "ymax"):
            object.__setattr__(self, name, _bound(getattr(self, name)))
        if self.xmin > self.xmax or self.ymin > self.ymax:
            raise ValueError("Rectangle lower bounds must not exceed upper bounds")
        object.__setattr__(
            self,
            "_float_bounds",
            tuple(_directed(value, i % 2 == 0) for i, value in enumerate(self.bounds)),
        )

    @property
    def bounds(self):
        return self.xmin, self.xmax, self.ymin, self.ymax

    def __call__(self, x, y):
        x, y, scalar = broadcast_coordinates(x, y)
        xmin, xmax, ymin, ymax = self._float_bounds
        result = (
            np.isfinite(x)
            & np.isfinite(y)
            & (x >= xmin)
            & (x <= xmax)
            & (y >= ymin)
            & (y <= ymax)
        )
        return bool(result) if scalar else result

    def to_dict(self):
        """Serialize exact rational bounds without executable expressions."""
        if not _is_native_rectangle(self):
            raise ValueError("Only unchanged native RectangleMask can be serialized")
        return {"type": "RectangleMask", "bounds": [str(v) for v in self.bounds]}

    @classmethod
    def from_dict(cls, data):
        """Read four bounded integer/fraction strings, never symbolic code."""
        if (
            cls is not RectangleMask
            or not isinstance(data, dict)
            or set(data) != {"type", "bounds"}
            or data["type"] != "RectangleMask"
            or not isinstance(data["bounds"], list)
            or len(data["bounds"]) != 4
        ):
            raise ValueError("Invalid RectangleMask data")
        values = []
        for text in data["bounds"]:
            if (
                not isinstance(text, str)
                or len(text) > 2470
                or re.fullmatch(r"-?[0-9]+(?:/[1-9][0-9]*)?", text) is None
            ):
                raise ValueError("Rectangle bounds require bounded rational strings")
            pieces = text.split("/")
            if any(len(piece.lstrip("-")) > 1234 for piece in pieces):
                raise ValueError("Rectangle bound exceeds coefficient limits")
            values.append(
                sp.Rational(int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1)
            )
        return cls(*values)


_NATIVE_RECTANGLE_CALL = RectangleMask.__call__


def _is_native_rectangle(mask):
    if (
        type(mask) is not RectangleMask
        or getattr(getattr(mask, "__call__", None), "__func__", None)
        is not _NATIVE_RECTANGLE_CALL
    ):
        return False
    try:
        bounds = tuple(_bound(v) for v in mask.bounds)
        return (
            bounds == mask.bounds
            and bounds[0] <= bounds[1]
            and bounds[2] <= bounds[3]
            and mask._float_bounds
            == tuple(_directed(v, i % 2 == 0) for i, v in enumerate(bounds))
        )
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False
