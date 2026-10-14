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
    def __init__(self, root, x, y, *, diagnostics=False):
        self.root = root
        self.x, self.y, self.scalar = broadcast_coordinates(x, y)
        self.shape = self.x.shape
        self.coordinates = (
            (float(self.x), float(self.y)) if self.scalar else (self.x, self.y)
        )
        self.values, self.gradients, self.active = {}, {}, set()
        self.errors = {}
        self.diagnostics = diagnostics
        self.sources = []
        self.has_error_estimate = False

    def array(self, value):
        return np.asarray(field_result(value, self.shape, False))

    def native(self, field):
        from .base_field import BlendedField

        return isinstance(field, BlendedField) and (
            field is self.root
            or (
                _method_is(field, "evaluate", BlendedField.evaluate)
                and _method_is(field, "gradient", BlendedField.gradient)
                and (
                    not self.diagnostics
                    or _method_is(
                        field, "gradient_diagnostics", BlendedField.gradient_diagnostics
                    )
                )
            )
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
            if gradient and not self.diagnostics:
                from .base_field import BlendedField

                if (
                    isinstance(field, BlendedField)
                    and _method_is(field, "gradient", BlendedField.gradient)
                    and not _method_is(
                        field, "gradient_diagnostics", BlendedField.gradient_diagnostics
                    )
                ):
                    self.errors[key] = (self.array(np.inf), self.array(np.inf))
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
            seen_wrappers = set()
            if isinstance(field, CurveField) and _method_is(
                field, "evaluate", CurveField.evaluate
            ):
                while isinstance(curve, LevelSetCurve) and _method_is(
                    curve, "evaluate", LevelSetCurve.evaluate
                ):
                    if id(curve) in seen_wrappers:
                        raise ValueError("Cyclic algebraic field graph")
                    seen_wrappers.add(id(curve))
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
        seen_wrappers = set()
        while (
            isinstance(curve, LevelSetCurve)
            and _method_is(curve, "gradient", LevelSetCurve.gradient)
            and _method_is(curve, "evaluate", LevelSetCurve.evaluate)
            and _method_is(
                curve, "gradient_diagnostics", LevelSetCurve.gradient_diagnostics
            )
        ):
            if id(curve) in seen_wrappers:
                raise ValueError("Cyclic algebraic field graph")
            seen_wrappers.add(id(curve))
            curve = curve.curve
        error = (0.0, 0.0)
        if (
            isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and _method_is(field, "evaluate", CurveField.evaluate)
            and (
                field is self.root
                or _method_is(
                    field, "gradient_diagnostics", CurveField.gradient_diagnostics
                )
            )
            and isinstance(curve, _AlgebraicLevelSet)
            and _method_is(curve, "gradient", _AlgebraicLevelSet.gradient)
            and curve._gradient_function is curve._algebraic_gradient
            and curve.native()
            and _method_is(
                curve, "gradient_diagnostics", _AlgebraicLevelSet.gradient_diagnostics
            )
        ):
            result = self.get(curve.field, True)
            error = self.errors[id(curve.field)]
        elif (
            self.diagnostics
            and isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and _method_is(field, "evaluate", CurveField.evaluate)
            and (
                field is self.root
                or _method_is(
                    field, "gradient_diagnostics", CurveField.gradient_diagnostics
                )
            )
        ):
            callback = getattr(curve, "gradient_diagnostics", None)
            if callable(callback):
                result, error = self.consume(callback(*self.coordinates))
            else:
                result = tuple(self.array(v) for v in field.gradient(*self.coordinates))
        elif self.diagnostics and callable(
            getattr(field, "gradient_diagnostics", None)
        ):
            result, error = self.consume(field.gradient_diagnostics(*self.coordinates))
        elif (
            not self.diagnostics
            and isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and isinstance(curve, _AlgebraicLevelSet)
            and _method_is(curve, "gradient", _AlgebraicLevelSet.gradient)
            and curve._gradient_function is curve._algebraic_gradient
        ):
            result = tuple(self.array(v) for v in field.gradient(*self.coordinates))
            error = (self.array(np.inf), self.array(np.inf))
        elif (
            isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and _method_is(field, "evaluate", CurveField.evaluate)
            and isinstance(curve, ProceduralCurve)
            and _method_is(curve, "gradient", ProceduralCurve.gradient)
        ):
            diagnostics = curve.gradient_diagnostics(*self.coordinates)
            result, error = self.consume(diagnostics)
        else:
            result = tuple(self.array(v) for v in field.gradient(*self.coordinates))
            from .field_strategy import SignedDistanceField
            from .distance_gradient import native_boundaries

            if (
                isinstance(field, SignedDistanceField)
                and _method_is(field, "gradient", SignedDistanceField.gradient)
                and not (
                    field._has_native_distance_methods()
                    and _method_is(
                        field,
                        "gradient_diagnostics",
                        SignedDistanceField.gradient_diagnostics,
                    )
                    and np.any(np.isfinite(self.x) & np.isfinite(self.y))
                    and native_boundaries(field.region) is not None
                )
            ):
                # No new adaptive probes in the cheap path. Its fixed-step
                # derivative has no claimed error; normals must not trust it.
                error = (self.array(np.inf), self.array(np.inf))
            elif (
                isinstance(field, CurveField)
                and _method_is(field, "gradient", CurveField.gradient)
                and (
                    not _method_is(field, "evaluate", CurveField.evaluate)
                    or (
                        isinstance(curve, LevelSetCurve)
                        and _method_is(curve, "gradient", LevelSetCurve.gradient)
                        and (
                            not _method_is(curve, "evaluate", LevelSetCurve.evaluate)
                            or not _method_is(
                                curve,
                                "gradient_diagnostics",
                                LevelSetCurve.gradient_diagnostics,
                            )
                        )
                    )
                )
            ):
                error = (self.array(np.inf), self.array(np.inf))
        if (
            not self.diagnostics
            and isinstance(field, CurveField)
            and _method_is(field, "gradient", CurveField.gradient)
            and not _method_is(
                field, "gradient_diagnostics", CurveField.gradient_diagnostics
            )
        ):
            error = (self.array(np.inf), self.array(np.inf))
        valid = (
            np.isfinite(self.get(field))
            & np.isfinite(result[0])
            & np.isfinite(result[1])
        )
        self.errors[id(field)] = error
        return tuple(np.where(valid, v, np.nan) for v in result)

    def consume(self, diagnostics):
        gx, gy = diagnostics["gradient"]
        result = tuple(self.array(v) for v in (gx, gy))
        error = (self.array(0.0), self.array(0.0))
        if diagnostics.get("error_estimate") is not None:
            ex, ey = diagnostics["error_estimate"]
            error = tuple(self.array(v) for v in (ex, ey))
            if any(np.any(v < 0) for v in error):
                raise ValueError("Diagnostic error estimates must be nonnegative")
            self.has_error_estimate = True
        available = np.broadcast_to(
            np.asarray(diagnostics.get("available", True)), self.shape
        )
        if available.dtype.kind != "b":
            raise ValueError("Diagnostic availability must be boolean")
        available = (
            available
            & np.isfinite(error[0])
            & np.isfinite(error[1])
            & np.isfinite(result[0])
            & np.isfinite(result[1])
            & np.isfinite(self.x)
            & np.isfinite(self.y)
        )
        if not self.diagnostics:
            return tuple(np.where(available, v, np.nan) for v in result), error
        source = {
            key: diagnostics[key]
            for key in (
                "method",
                "status",
                "field_evaluations",
                "derivative_target",
                "distance_model",
            )
            if key in diagnostics
        }
        source["error_estimate"] = (
            None
            if diagnostics.get("error_estimate") is None
            else tuple(field_result(v, self.shape, self.scalar) for v in error)
        )
        source["available"] = (
            available.item() if self.scalar else np.asarray(available).copy()
        )
        if "raw_gradient" in diagnostics:
            source["raw_gradient"] = tuple(
                field_result(v, self.shape, self.scalar)
                for v in diagnostics["raw_gradient"]
            )
        self.sources.append(source)
        return tuple(np.where(available, v, np.nan) for v in result), error

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


def algebraic_diagnostics(field, x, y):
    """Explicit diagnostic graph walk; repeated leaves share this query only."""
    query = _Query(field, x, y, diagnostics=True)
    with np.errstate(all="ignore"):
        raw = query.get(field, True)
        error = query.errors[id(field)]
        available = (
            np.isfinite(query.get(field)) & np.isfinite(query.x) & np.isfinite(query.y)
        )
        for value, uncertainty in zip(raw, error):
            available &= np.isfinite(value) & np.isfinite(uncertainty)
    result = tuple(
        field_result(np.where(available, v, np.nan), query.shape, query.scalar)
        for v in raw
    )
    return dict(
        gradient=result,
        raw_gradient=tuple(field_result(v, query.shape, query.scalar) for v in raw),
        available=available.item() if query.scalar else np.asarray(available).copy(),
        error_estimate=tuple(field_result(v, query.shape, query.scalar) for v in error)
        if query.has_error_estimate
        else None,
        method="algebraic",
        derivative_target="composed_field",
        certified=False,
        sources=query.sources,
        field_evaluations=None,
    )


def callback_diagnostics(evaluate, gradient, x, y):
    """Respect an explicit gradient; otherwise reuse bounded numerical probes."""
    from .adaptive_differentiation import automatic_gradient

    xx, yy, scalar = broadcast_coordinates(x, y)
    coordinates = (float(xx), float(yy)) if scalar else (xx, yy)
    if gradient is not None:
        gx, gy = gradient(*coordinates)
        raw = tuple(np.asarray(field_result(v, xx.shape, False)) for v in (gx, gy))
        available = (
            np.isfinite(evaluate(*coordinates))
            & np.isfinite(xx)
            & np.isfinite(yy)
            & np.isfinite(raw[0])
            & np.isfinite(raw[1])
        )
        return dict(
            gradient=tuple(
                field_result(np.where(available, v, np.nan), xx.shape, scalar)
                for v in raw
            ),
            raw_gradient=tuple(field_result(v, xx.shape, scalar) for v in raw),
            available=available.item() if scalar else np.asarray(available).copy(),
            error_estimate=None,
            method="provided_gradient",
            certified=False,
            field_evaluations=None,
        )

    def sample(a, b):
        return evaluate(float(a), float(b)) if scalar else evaluate(a, b)

    result = automatic_gradient(sample, xx, yy)
    raw = result["gradient"]
    available = np.isfinite(xx) & np.isfinite(yy)
    for value, error in zip(raw, result["error_estimate"]):
        available &= np.isfinite(value) & np.isfinite(error)
    result["raw_gradient"] = tuple(field_result(v, xx.shape, scalar) for v in raw)
    result["gradient"] = tuple(
        field_result(np.where(available, v, np.nan), xx.shape, scalar) for v in raw
    )
    result["error_estimate"] = tuple(
        field_result(v, xx.shape, scalar) for v in result["error_estimate"]
    )
    result["steps"] = tuple(
        tuple(
            tuple(field_result(v, xx.shape, scalar) for v in stencil)
            for stencil in axis
        )
        for axis in result["steps"]
    )
    for key in ("status", "selection", "candidates"):
        result[key] = tuple(v.item() if scalar else v for v in result[key])
    finite = np.isfinite(xx) & np.isfinite(yy)
    result["status"] = tuple(
        (v.item() if scalar else v)
        for v in (
            np.where(finite, status, "nonfinite_coordinate")
            for status in result["status"]
        )
    )
    result["nominal_step"] = tuple(
        field_result(v, xx.shape, scalar) for v in result["nominal_step"]
    )
    result.update(
        available=available.item() if scalar else np.asarray(available).copy(),
        derivative_target="evaluate",
        certified=False,
    )
    return result


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

    def native(self):
        return (
            self.function is self._algebraic_function
            and self._gradient_function is self._algebraic_gradient
            and _method_is(self, "gradient", _AlgebraicLevelSet.gradient)
            and _method_is(self, "evaluate", ProceduralCurve.evaluate)
        )

    def gradient(self, x, y):
        # Bypass virtual diagnostic dispatch: this callback retains the cheap
        # field gradient, even though explicit diagnostics can be expensive.
        return ProceduralCurve.gradient_diagnostics(self, x, y)["gradient"]

    def gradient_diagnostics(self, x, y):
        if not self.native():
            provided = (
                self.gradient
                if not _method_is(self, "gradient", _AlgebraicLevelSet.gradient)
                or self._gradient_function is not self._algebraic_gradient
                else None
            )
            return callback_diagnostics(self.evaluate, provided, x, y)
        result = self.field.gradient_diagnostics(x, y)
        return shifted_diagnostics(result, self.evaluate(x, y))

    def normal(self, x, y):
        from .base_field import BlendedField
        from .field_strategy import SignedDistanceField

        if (
            self._gradient_function is not self._algebraic_gradient
            or self.function is not self._algebraic_function
            or not _method_is(self, "gradient", _AlgebraicLevelSet.gradient)
            or not _method_is(self, "evaluate", ProceduralCurve.evaluate)
        ):
            if self._gradient_function is self._algebraic_gradient and _method_is(
                self, "gradient", _AlgebraicLevelSet.gradient
            ):
                raise ValueError("Normal undefined - unresolved numerical derivative")
            return super().normal(x, y)
        if not _method_is(
            self, "gradient_diagnostics", _AlgebraicLevelSet.gradient_diagnostics
        ):
            raise ValueError("Normal undefined - unresolved numerical derivative")
        implementation = (
            BlendedField.gradient
            if isinstance(self.field, BlendedField)
            else SignedDistanceField.gradient
        )
        if not _method_is(self.field, "gradient", implementation):
            return super().normal(x, y)
        if isinstance(self.field, BlendedField) and not _method_is(
            self.field, "evaluate", BlendedField.evaluate
        ):
            raise ValueError("Normal undefined - unresolved numerical derivative")
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


def shifted_diagnostics(diagnostics, value):
    """A constant shift preserves derivatives but can invalidate finite domain."""
    result = dict(diagnostics)
    gx, gy = result["gradient"]
    shape = np.shape(gx)
    scalar = np.isscalar(gx)
    available = np.broadcast_to(np.asarray(result.get("available", True)), shape)
    if available.dtype.kind != "b":
        raise ValueError("Diagnostic availability must be boolean")
    available = available & np.isfinite(value) & np.isfinite(gx) & np.isfinite(gy)
    if result.get("error_estimate") is not None:
        for error in result["error_estimate"]:
            error = np.asarray(error)
            if np.any(error < 0):
                raise ValueError("Diagnostic error estimates must be nonnegative")
            available = available & np.isfinite(error)
    result["gradient"] = tuple(
        field_result(np.where(available, v, np.nan), shape, scalar) for v in (gx, gy)
    )
    result["available"] = available.item() if scalar else np.asarray(available).copy()
    result["certified"] = False
    return result
