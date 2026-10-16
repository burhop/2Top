"""Exact stored-coefficient affine half-plane predicates and native mask codec."""

from dataclasses import dataclass, field
from fractions import Fraction
import math
import re

import numpy as np
import sympy as sp

from .numeric import broadcast_coordinates
from .rectangle_mask import RectangleMask, _is_native_rectangle


def _coefficient(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, float, np.integer, np.floating, Fraction, sp.Rational, sp.Float)
    ):
        raise ValueError(
            "Half-plane coefficients require finite rational/float scalars"
        )
    if isinstance(value, np.floating):
        if value.dtype.itemsize > 8:
            raise ValueError("Half-plane numpy coefficients support at most binary64")
        value = float(value)
    if isinstance(value, np.integer):
        value = int(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Half-plane coefficients must be finite")
    if isinstance(value, sp.Float):
        _, _, exponent, bits = value._mpf_
        if value._prec > 4096 or abs(exponent) + bits > 4096:
            raise ValueError("Half-plane coefficient exceeds resource limits")
    if isinstance(value, Fraction):
        value = sp.Rational(value.numerator, value.denominator)
    value = sp.Rational(value)
    if int(value.p).bit_length() > 4096 or int(value.q).bit_length() > 4096:
        raise ValueError("Half-plane coefficient exceeds resource limits")
    return value


def _float_intervals(coefficients):
    scale = max(abs(v) for v in coefficients)
    if scale == 0:
        return ((0.0, 0.0),) * 3
    intervals = []
    for coefficient in coefficients:
        exact = coefficient / scale
        nearest = float(exact)
        stored = sp.Rational(nearest)
        lower = math.nextafter(nearest, -math.inf) if stored > exact else nearest
        upper = math.nextafter(nearest, math.inf) if stored < exact else nearest
        intervals.append((lower, upper))
    return tuple(intervals)


@dataclass(frozen=True, slots=True)
class HalfPlaneMask:
    """Immutable a*x+b*y+c >= 0 (closed) or > 0 (open), with exact coefficients.

    Float coefficients mean their exact stored binary values. Finite binary64
    coordinates use outward interval arithmetic, with exact rational fallback
    for uncertain signs. Nonfinite coordinates are outside. If a=b=0 the exact
    constant/mode selects all finite points or none; zero is included only in
    closed mode. Raw coefficients and mode survive the native rational codec.
    """

    a: object
    b: object
    c: object = 0
    closed: bool = field(default=True, kw_only=True)
    _float_coefficients: tuple = field(init=False, repr=False)

    def __post_init__(self):
        if not isinstance(self.closed, (bool, np.bool_)):
            raise ValueError("closed must be an actual boolean")
        object.__setattr__(self, "closed", bool(self.closed))
        for name in ("a", "b", "c"):
            object.__setattr__(self, name, _coefficient(getattr(self, name)))
        object.__setattr__(
            self, "_float_coefficients", _float_intervals(self.coefficients)
        )

    @property
    def coefficients(self):
        return self.a, self.b, self.c

    def __call__(self, x, y):
        x, y, scalar = broadcast_coordinates(x, y)
        finite = np.isfinite(x) & np.isfinite(y)
        if self.a == self.b == 0:
            included = bool(self.c >= 0 if self.closed else self.c > 0)
            result = finite & included
            return bool(result) if scalar else result
        (al, au), (bl, bu), (cl, cu) = self._float_coefficients
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            ax_lower = np.nextafter(np.where(x >= 0, al * x, au * x), -np.inf)
            ax_upper = np.nextafter(np.where(x >= 0, au * x, al * x), np.inf)
            by_lower = np.nextafter(np.where(y >= 0, bl * y, bu * y), -np.inf)
            by_upper = np.nextafter(np.where(y >= 0, bu * y, bl * y), np.inf)
            lower = np.nextafter(
                np.nextafter(ax_lower + by_lower, -np.inf) + cl, -np.inf
            )
            upper = np.nextafter(np.nextafter(ax_upper + by_upper, np.inf) + cu, np.inf)
        bounded = np.isfinite(lower) & np.isfinite(upper)
        included = lower >= 0 if self.closed else lower > 0
        excluded = upper < 0 if self.closed else upper <= 0
        result = np.asarray(finite & bounded & included).copy()
        unresolved = finite & ~(bounded & (included | excluded))
        # A root near a boundary may be decisive far below binary64 range.
        for index in np.flatnonzero(unresolved):
            exact = (
                self.a * sp.Rational(float(x.flat[index]))
                + self.b * sp.Rational(float(y.flat[index]))
                + self.c
            )
            result.flat[index] = bool(exact >= 0 if self.closed else exact > 0)
        return bool(result) if scalar else result

    def to_dict(self):
        if not _is_native_half_plane(self):
            raise ValueError("Only unchanged native HalfPlaneMask can be serialized")
        return {
            "type": "HalfPlaneMask",
            "coefficients": [str(v) for v in self.coefficients],
            "closed": self.closed,
        }

    @classmethod
    def from_dict(cls, data):
        if (
            cls is not HalfPlaneMask
            or not isinstance(data, dict)
            or set(data) != {"type", "coefficients", "closed"}
            or data["type"] != "HalfPlaneMask"
            or type(data["closed"]) is not bool
            or not isinstance(data["coefficients"], list)
            or len(data["coefficients"]) != 3
        ):
            raise ValueError("Invalid HalfPlaneMask data")
        values = []
        for text in data["coefficients"]:
            if (
                not isinstance(text, str)
                or len(text) > 2470
                or re.fullmatch(r"-?[0-9]+(?:/[1-9][0-9]*)?", text) is None
            ):
                raise ValueError(
                    "Half-plane coefficients require bounded rational strings"
                )
            pieces = text.split("/")
            if any(len(piece.lstrip("-")) > 1234 for piece in pieces):
                raise ValueError("Half-plane coefficient exceeds resource limits")
            values.append(
                sp.Rational(int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1)
            )
        return cls(*values, closed=data["closed"])


_NATIVE_HALF_PLANE_CALL = HalfPlaneMask.__call__


def _is_native_half_plane(mask):
    if (
        type(mask) is not HalfPlaneMask
        or getattr(getattr(mask, "__call__", None), "__func__", None)
        is not _NATIVE_HALF_PLANE_CALL
    ):
        return False
    try:
        coefficients = tuple(_coefficient(v) for v in mask.coefficients)
        return (
            type(mask.closed) is bool
            and coefficients == mask.coefficients
            and mask._float_coefficients == _float_intervals(coefficients)
        )
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def _native_mask_kind(mask):
    if _is_native_rectangle(mask):
        return "RectangleMask"
    if _is_native_half_plane(mask):
        return "HalfPlaneMask"
    return None


def _native_mask_from_dict(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid native mask data")
    if data.get("type") == "RectangleMask":
        return RectangleMask.from_dict(data)
    if data.get("type") == "HalfPlaneMask":
        return HalfPlaneMask.from_dict(data)
    raise ValueError("Unsupported native mask type")
