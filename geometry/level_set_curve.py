"""Field-unit level shifts preserving the original numeric implementation."""

import math

import sympy as sp

from .bounds import SublevelBounds, rational_level
from .implicit_curve import ImplicitCurve
from .numeric import broadcast_coordinates, field_result


class LevelSetCurve(ImplicitCurve):
    """f(x,y)-level, delegating evaluation/gradient and sublevel envelopes.

    This is not a Euclidean distance offset. Arbitrary callback serialization
    retains the source curve's honest unavailable-code placeholder.
    """

    def __init__(self, curve, level):
        if not isinstance(curve, ImplicitCurve):
            raise TypeError("curve must be an ImplicitCurve")
        exact = rational_level(level)
        try:
            self.level = float(exact)
        except OverflowError as error:
            raise ValueError("Level shift must fit a finite float") from error
        if not math.isfinite(self.level):
            raise ValueError("Level shift must fit a finite float")
        self.curve = curve
        self.variables = curve.variables
        self.expression = (
            None
            if curve.expression is None
            else curve.expression - sp.Float(self.level)
        )
        self._precision_policy = curve.precision_policy()
        self._eval_func = self._grad_funcs = None

    def evaluate(self, x, y):
        xx, yy, scalar = broadcast_coordinates(x, y)
        return field_result(self.curve.evaluate(xx, yy) - self.level, xx.shape, scalar)

    def gradient(self, x, y):
        return self.curve.gradient(x, y)

    def normal(self, x, y):
        from .field_algebra import _method_is

        if not _method_is(self, "gradient", LevelSetCurve.gradient):
            return ImplicitCurve.normal(self, x, y)
        if not _method_is(self, "evaluate", LevelSetCurve.evaluate) or not _method_is(
            self, "gradient_diagnostics", LevelSetCurve.gradient_diagnostics
        ):
            raise ValueError("Normal undefined - unresolved numerical derivative")
        if not math.isfinite(self.evaluate(x, y)):
            raise ValueError("Normal undefined outside the shifted field domain")
        # A constant shift preserves regularity, including numerical cusp guards.
        return self.curve.normal(x, y)

    def gradient_diagnostics(self, x, y):
        """Propagate source diagnostics through a finite constant level shift."""
        from .field_algebra import _method_is, callback_diagnostics, shifted_diagnostics

        if not _method_is(self, "gradient", LevelSetCurve.gradient):
            result = callback_diagnostics(self.evaluate, self.gradient, x, y)
        elif not _method_is(self, "evaluate", LevelSetCurve.evaluate):
            result = callback_diagnostics(self.evaluate, None, x, y)
        elif callable(getattr(self.curve, "gradient_diagnostics", None)):
            result = self.curve.gradient_diagnostics(x, y)
        else:
            result = callback_diagnostics(
                self.curve.evaluate, self.curve.gradient, x, y
            )
        return shifted_diagnostics(result, self.evaluate(x, y))

    def sublevel_bounds(self, level=0):
        level = rational_level(level)
        if getattr(self.evaluate, "__func__", None) is not LevelSetCurve.evaluate:
            return SublevelBounds("unknown", reason="Custom level-set evaluator")
        return self.curve.sublevel_bounds(level + sp.Rational(self.level))

    def bounding_box(self):
        return self.sublevel_bounds().box

    def coefficients(self):
        if self.expression is None:
            return {}
        return sp.Poly(self.expression, *self.variables).as_dict()

    def scale_hint(self):
        return self.curve.scale_hint()

    def to_dict(self):
        return dict(type="LevelSetCurve", curve=self.curve.to_dict(), level=self.level)

    @classmethod
    def from_dict(cls, data):
        if (
            not isinstance(data, dict)
            or set(data) != {"type", "curve", "level"}
            or data["type"] != "LevelSetCurve"
        ):
            raise ValueError("Invalid LevelSetCurve envelope")
        return cls(ImplicitCurve.from_dict(data["curve"]), data["level"])
