"""Query-local algebraic evaluation; no persistent graph or expression snapshots.

Callbacks are assumed pure and pointwise: shared-node reuse changes call counts.
Unknown custom derivative implementations retain responsibility for their validity.
"""

import numpy as np

from .numeric import broadcast_coordinates, field_result


def _method_is(obj, name, implementation):
    return getattr(getattr(obj, name), "__func__", None) is implementation


def _quotient_derivative(a, b, da, db):
    """Scale derivative terms by binary exponent before subtraction.

    Avoid forming b*b, a*db or overflowing intermediate derivative ratios.
    This remains float64 arithmetic, with its usual cancellation limits.
    """
    # These conservative binary limits keep ordinary ratios/products normal.
    if all(
        np.all((v == 0) | ((np.abs(v) >= 2.0**-200) & (np.abs(v) <= 2.0**200)))
        for v in (a, b, da, db)
    ) and np.all(b != 0):
        return da / b - (a / b) * (db / b)
    ma, ea = np.frexp(a)
    mb, eb = np.frexp(b)
    mda, eda = np.frexp(da)
    mdb, edb = np.frexp(db)
    first, second = mda / mb, ma * mdb / (mb * mb)
    efirst, esecond = eda - eb, ea + edb - 2 * eb
    # Zero terms must not choose an exponent that underflows the other term.
    exponent = np.maximum(
        np.where(first != 0, efirst, -10000),
        np.where(second != 0, esecond, -10000),
    )
    exponent = np.where((first == 0) & (second == 0), 0, exponent)
    difference = np.ldexp(first, efirst - exponent) - np.ldexp(
        second, esecond - exponent
    )
    return np.ldexp(difference, exponent)


class _Query:
    def __init__(self, root, x, y):
        self.root = root
        self.x, self.y, self.scalar = broadcast_coordinates(x, y)
        self.shape = self.x.shape
        self.coordinates = (
            (float(self.x), float(self.y)) if self.scalar else (self.x, self.y)
        )
        self.values, self.gradients, self.active = {}, {}, set()
        self.errors = {}

    def array(self, value):
        return np.asarray(field_result(value, self.shape, False))

    def native(self, field):
        from .base_field import BlendedField

        return field is self.root or (
            isinstance(field, BlendedField)
            and _method_is(field, "evaluate", BlendedField.evaluate)
            and _method_is(field, "gradient", BlendedField.gradient)
        )

    def children(self, field):
        from .base_field import BaseField

        if len(field.fields) < 2 or field.operation not in field.SUPPORTED_OPERATIONS:
            raise ValueError("Invalid mutable algebraic field configuration")
        if not all(isinstance(child, BaseField) for child in field.fields):
            raise TypeError("All fields must be BaseField instances")
        return field.fields

    def get(self, field, gradient=False):
        cache = self.gradients if gradient else self.values
        key = id(field)
        if key in cache:
            return cache[key]
        active_key = (key, gradient)
        if active_key in self.active:
            raise ValueError("Cyclic algebraic field graph")
        self.active.add(active_key)
        try:
            result = (
                self.compose(field, gradient)
                if self.native(field)
                else self.leaf(field, gradient)
            )
            cache[key] = result
            return result
        finally:
            self.active.remove(active_key)

    def leaf(self, field, gradient):
        from .base_field import CurveField
        from .procedural_curve import ProceduralCurve
        from .level_set_curve import LevelSetCurve

        curve = getattr(field, "curve", None)
        if not gradient:
            shifts = []
            if isinstance(field, CurveField) and _method_is(
                field, "evaluate", CurveField.evaluate
            ):
                while isinstance(curve, LevelSetCurve) and _method_is(
                    curve, "evaluate", LevelSetCurve.evaluate
                ):
                    shifts.append(curve.level)
                    curve = curve.curve
                if (
                    isinstance(curve, _AlgebraicLevelSet)
                    and _method_is(curve, "evaluate", ProceduralCurve.evaluate)
                    and curve.function is curve._algebraic_function
                ):
                    value = self.get(curve.field) - curve.level
                    for shift in reversed(shifts):
                        value = value - shift
                    return value
            return self.array(field.evaluate(*self.coordinates))
        while isinstance(curve, LevelSetCurve) and _method_is(
            curve, "gradient", LevelSetCurve.gradient
        ):
            curve = curve.curve
        error = (0.0, 0.0)
        if (
            isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and isinstance(curve, _AlgebraicLevelSet)
            and _method_is(curve, "gradient", ProceduralCurve.gradient)
            and curve._gradient_function is curve._algebraic_gradient
        ):
            result = self.get(curve.field, True)
            error = self.errors[id(curve.field)]
        elif (
            isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and isinstance(curve, ProceduralCurve)
            and _method_is(curve, "gradient", ProceduralCurve.gradient)
        ):
            diagnostics = curve.gradient_diagnostics(*self.coordinates)
            result = tuple(self.array(v) for v in diagnostics["gradient"])
            if diagnostics["error_estimate"] is not None:
                error = tuple(self.array(v) for v in diagnostics["error_estimate"])
                valid = np.isfinite(error[0]) & np.isfinite(error[1])
                result = tuple(np.where(valid, v, np.nan) for v in result)
        else:
            result = tuple(self.array(v) for v in field.gradient(*self.coordinates))
        valid = (
            np.isfinite(self.get(field))
            & np.isfinite(result[0])
            & np.isfinite(result[1])
        )
        self.errors[id(field)] = error
        return tuple(np.where(valid, v, np.nan) for v in result)

    def compose(self, field, gradient):
        children = self.children(field)
        values = [self.get(child) for child in children]
        operation = field.operation
        if operation in ("min", "max"):
            value = values[0]
            for other in values[1:]:
                if self.scalar:
                    value = self.array(
                        (min if operation == "min" else max)(float(value), float(other))
                    )
                else:
                    value = (np.minimum if operation == "min" else np.maximum)(
                        value, other
                    )
            if not gradient:
                return value
            result = [np.full(self.shape, np.nan), np.full(self.shape, np.nan)]
            seen = np.zeros(self.shape, dtype=bool)
            disagreement = np.zeros(self.shape, dtype=bool)
            error = (self.array(0.0), self.array(0.0))
            for child, child_value in zip(children, values):
                winner = (child_value == value) & np.isfinite(value)
                if not np.any(winner):
                    continue
                child_gradient = self.get(child, True)
                error = tuple(
                    np.where(winner, np.maximum(e, ce), e)
                    for e, ce in zip(error, self.errors[id(child)])
                )
                agreement = (result[0] == child_gradient[0]) & (
                    result[1] == child_gradient[1]
                )
                disagreement |= winner & seen & ~agreement
                result = [
                    np.where(winner & ~seen, g, r)
                    for g, r in zip(child_gradient, result)
                ]
                seen |= winner
            valid = (
                seen & ~disagreement & np.isfinite(result[0]) & np.isfinite(result[1])
            )
            self.errors[id(field)] = error
            return tuple(np.where(valid, v, np.nan) for v in result)

        value = values[0]
        result = self.get(children[0], True) if gradient else None
        error = self.errors[id(children[0])] if gradient else None
        valid = np.isfinite(value)
        for child, other in zip(children[1:], values[1:]):
            if not gradient and operation == "divide" and self.scalar and other == 0:
                return self.array(0.0)  # Legacy scalar zero-denominator short circuit.
            other_gradient = self.get(child, True) if gradient else None
            other_error = self.errors[id(child)] if gradient else None
            valid = valid & np.isfinite(other)
            if operation in ("add", "average", "subtract"):
                sign = -1 if operation == "subtract" else 1
                if gradient:
                    result = tuple(a + sign * b for a, b in zip(result, other_gradient))
                    error = tuple(a + b for a, b in zip(error, other_error))
                value = value + sign * other
            elif operation == "multiply":
                if gradient:
                    result = tuple(
                        a * other + value * b for a, b in zip(result, other_gradient)
                    )
                    error = tuple(
                        a * np.abs(other) + np.abs(value) * b
                        for a, b in zip(error, other_error)
                    )
                value = value * other
            elif operation == "divide":
                valid = valid & (other != 0)
                if gradient:
                    result = tuple(
                        _quotient_derivative(value, other, a, b)
                        for a, b in zip(result, other_gradient)
                    )
                    if any(np.any(e) for e in (*error, *other_error)):
                        error = tuple(
                            _quotient_derivative(np.abs(value), np.abs(other), a, -b)
                            for a, b in zip(error, other_error)
                        )
                    else:
                        error = (0.0, 0.0)
                value = np.divide(
                    value, other, out=np.zeros(self.shape), where=other != 0
                )
            valid = valid & np.isfinite(value)
        if operation == "average":
            value = value / len(children)
            if gradient:
                result = tuple(v / len(children) for v in result)
                error = tuple(v / len(children) for v in error)
        if not gradient:
            return value
        valid = valid & np.isfinite(result[0]) & np.isfinite(result[1])
        self.errors[id(field)] = error
        return tuple(np.where(valid, v, np.nan) for v in result)


def algebraic_query(field, x, y, *, gradient=False):
    query = _Query(field, x, y)
    with np.errstate(all="ignore"):
        result = query.get(field, gradient)
    if gradient:
        return tuple(field_result(v, query.shape, query.scalar) for v in result)
    return field_result(result, query.shape, query.scalar)


from .procedural_curve import ProceduralCurve


class _AlgebraicLevelSet(ProceduralCurve):
    """Internal procedural contour retaining child derivative uncertainty."""

    def __init__(self, field, level, variables):
        self.field = field
        self.level = level
        super().__init__(
            lambda x, y: self.field.evaluate(x, y) - self.level,
            variables,
            gradient_function=lambda x, y: self.field.gradient(x, y),
        )
        self._algebraic_function = self.function
        self._algebraic_gradient = self._gradient_function

    def normal(self, x, y):
        from .base_field import BlendedField

        if (
            self._gradient_function is not self._algebraic_gradient
            or self.function is not self._algebraic_function
            or not _method_is(self, "gradient", ProceduralCurve.gradient)
            or not _method_is(self, "evaluate", ProceduralCurve.evaluate)
            or not _method_is(self.field, "gradient", BlendedField.gradient)
            or not _method_is(self.field, "evaluate", BlendedField.evaluate)
        ):
            return super().normal(x, y)
        query = _Query(self.field, x, y)
        with np.errstate(all="ignore"):
            gx, gy = query.get(self.field, True)
        uncertainty = max(query.errors[id(self.field)])
        scale = max(abs(gx), abs(gy))
        if (
            not np.isfinite([self.evaluate(x, y), gx, gy, uncertainty]).all()
            or scale <= uncertainty
        ):
            raise ValueError(
                "Normal undefined - zero gradient or unresolved numerical derivative"
            )
        nx, ny = gx / scale, gy / scale
        magnitude = np.hypot(nx, ny)
        return float(nx / magnitude), float(ny / magnitude)
