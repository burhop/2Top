"""
ProceduralCurve class - Sprint 3 Task GEO-S3-T4

Implementation of ProceduralCurve subclass of ImplicitCurve for curves defined by arbitrary Python functions.
This class wraps Python callables to provide the ImplicitCurve interface, using numerical methods
for operations that require symbolic computation (like gradients).

Key limitations:
- Gradient computation uses finite differences (numerical approximation)
- Serialization cannot preserve the actual function code
- Functions must accept two numeric arguments (x, y) and return a numeric value
"""

import sympy as sp
import numpy as np
from typing import Tuple, Optional, Union, Callable
from .implicit_curve import ImplicitCurve
from .numeric import broadcast_coordinates, field_result, real_array
from .differentiation import estimate_gradient


from .precision import PrecisionPolicy, get_precision_policy


class ProceduralCurve(ImplicitCurve):
    """
    Represents implicit curves defined by arbitrary Python functions.

    This class allows wrapping any Python callable that takes (x, y) coordinates
    and returns a numeric value representing the implicit function f(x,y).
    Since the function is not symbolic, gradients are computed numerically.
    """

    def __init__(
        self,
        function: Callable[[float, float], float],
        variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
        name: str = "custom",
        precision_policy: Optional[PrecisionPolicy] = None,
        is_periodic: bool = False,
        *,
        gradient_function=None,
        derivative_scale=None,
    ):
        """
        Initialize a ProceduralCurve with a Python function.

        Args:
            function: Python callable that takes (x, y) and returns f(x, y)
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.
            name: Descriptive name for the function (used in serialization and display)
            precision_policy: Optional precision policy. If None, uses active default policy.
            is_periodic: Set to True for functions involving sin/cos so the graphics
                         backend uses its high-resolution periodic sampling path instead
                         of relying on the fragile name-string heuristic.

        Raises:
            ValueError: If function is not callable
        """
        # Validate function
        if not callable(function):
            raise ValueError("function must be callable")
        if gradient_function is not None and not callable(gradient_function):
            raise ValueError("gradient_function must be callable or None")
        scales = None
        if derivative_scale is not None:
            scales = real_array(derivative_scale)
            if np.asarray(derivative_scale).dtype.kind == "b":
                raise ValueError("derivative_scale must be positive and finite")
            if scales.shape == ():
                scales = np.repeat(scales, 2)
            if (
                scales.shape != (2,)
                or not np.isfinite(scales).all()
                or np.any(scales <= 0)
            ):
                raise ValueError(
                    "derivative_scale must be a positive finite scalar or pair"
                )
            scales = tuple(float(v) for v in scales)
        self._gradient_function = gradient_function
        self._derivative_scale = scales

        # Store the function and metadata
        self.function = function
        self.name = name
        self.is_periodic = is_periodic

        # Set up variables
        if variables is None:
            x, y = sp.symbols("x y", real=True)
            variables = (x, y)

        # Set up variables
        self._variables = variables

        # ProceduralCurve doesn't have a symbolic expression
        # We set expression to None and handle it specially
        self.expression = None
        self.variables = variables

        # Set up precision policy
        self._precision_policy = precision_policy or get_precision_policy()

        # Don't call super().__init__ since we don't have a symbolic expression
        # Instead, manually set up what we need
        self._eval_func = None  # We'll use our own function
        self._grad_funcs = None  # We'll compute gradients numerically

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the procedural curve at given coordinates.

        Args:
            x: x-coordinate(s) for evaluation
            y: y-coordinate(s) for evaluation

        Returns:
            Function value(s) at the given coordinates
        """
        x_arr, y_arr, scalar = broadcast_coordinates(x, y)
        if scalar:
            return field_result(self.function(float(x_arr), float(y_arr)), (), True)

        # Vectorized evaluation path
        try:
            # Try evaluating directly (if the function supports vectorization)
            result = self.function(x_arr, y_arr)
        except Exception:
            # Fallback to numpy's vectorize wrapper
            vfunc = np.vectorize(self.function, otypes=[float])
            result = vfunc(x_arr, y_arr)
        return field_result(result, x_arr.shape, False)

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """Return the analytic callback or representable numerical estimate."""
        if self._gradient_function is not None:
            return self.gradient_diagnostics(x, y)["gradient"]
        xx, yy, scalar = broadcast_coordinates(x, y)
        result = estimate_gradient(
            self.evaluate, xx, yy, self._derivative_scale, diagnostics=False
        )
        return tuple(field_result(v, xx.shape, scalar) for v in result["gradient"])

    def gradient_diagnostics(self, x, y):
        """Gradient, heuristic error estimate and actual coarse/fine displacements.

        Analytic callbacks have no claimed numerical error bound (None). The
        default numerical scale is max(1, |coordinate|) per axis; explicit
        derivative_scale supplies local coordinate units for small features.
        """
        xx, yy, scalar = broadcast_coordinates(x, y)
        if self._gradient_function is not None:
            if scalar:
                result = self._gradient_function(float(xx), float(yy))
            else:
                try:
                    result = self._gradient_function(xx, yy)
                except (TypeError, ValueError):
                    result = np.vectorize(
                        self._gradient_function, otypes=[float, float]
                    )(xx, yy)
            try:
                gx, gy = result
            except (TypeError, ValueError) as error:
                raise ValueError(
                    "gradient_function must return two real components"
                ) from error
            return dict(
                gradient=(
                    field_result(gx, xx.shape, scalar),
                    field_result(gy, xx.shape, scalar),
                ),
                error_estimate=None,
                steps=None,
                method="analytic",
            )
        result = estimate_gradient(self.evaluate, xx, yy, self._derivative_scale)
        for key in ("gradient", "error_estimate"):
            result[key] = tuple(field_result(v, xx.shape, scalar) for v in result[key])
        result["steps"] = tuple(
            tuple(
                tuple(field_result(v, xx.shape, scalar) for v in stencil)
                for stencil in axis
            )
            for axis in result["steps"]
        )
        return result

    def normal(self, x_val: float, y_val: float) -> Tuple[float, float]:
        """Reject singular, nonfinite or numerically unresolved directions."""
        if (
            self._gradient_function is not None
            or type(self).gradient is not ProceduralCurve.gradient
        ):
            return super().normal(x_val, y_val)
        try:
            diagnostics = self.gradient_diagnostics(x_val, y_val)
            gx, gy = diagnostics["gradient"]
            value = self.evaluate(x_val, y_val)
            finite = np.isfinite([value, gx, gy]).all()
        except (ArithmeticError, ValueError) as error:
            raise ValueError("Normal undefined outside the field domain") from error
        scale = max(abs(gx), abs(gy))
        uncertainty = max(diagnostics["error_estimate"])
        if not finite or not np.isfinite(uncertainty) or scale <= uncertainty:
            raise ValueError(
                "Normal undefined - zero gradient or unresolved numerical derivative"
            )
        nx, ny = gx / scale, gy / scale
        magnitude = np.hypot(nx, ny)
        return (nx / magnitude, ny / magnitude)

    def to_dict(self) -> dict:
        """
        Serialize the procedural curve to a dictionary.

        Returns:
            Dictionary with type "ProceduralCurve" and placeholder information

        Note:
            Cannot serialize the actual function code. Returns descriptive placeholder.
        """
        # Create base dictionary structure
        data = {
            "type": "ProceduralCurve",
            "function": "custom",  # Always use "custom" as placeholder indicator
            "variables": [str(var) for var in self.variables],
            "name": self.name,
        }

        # Add warning about serialization limitations
        data["_serialization_note"] = (
            "Function and analytic gradient callbacks cannot be serialized. This is a placeholder."
        )
        if self._derivative_scale is not None:
            data["derivative_scale"] = list(self._derivative_scale)

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ProceduralCurve":
        """
        Reconstruct a ProceduralCurve from a dictionary.

        Args:
            data: Dictionary from to_dict() method

        Returns:
            New ProceduralCurve instance with placeholder function

        Raises:
            ValueError: If data is invalid or missing required fields

        Note:
            The reconstructed curve will have a placeholder function that raises
            NotImplementedError when called, since the original function cannot be serialized.
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if data.get("type") != "ProceduralCurve":
            raise ValueError(
                f"Invalid type: expected 'ProceduralCurve', got {data.get('type')}"
            )

        # Extract function name/description
        if "function" not in data:
            raise ValueError("Missing required field: function")

        function_name = data["function"]
        if not isinstance(function_name, str):
            raise ValueError("Function field must be a string description")

        # Extract name
        name = data.get("name", function_name)

        # Parse variables if provided
        variables = None
        if "variables" in data:
            try:
                variables = tuple(sp.Symbol(var_str) for var_str in data["variables"])
            except Exception as e:
                raise ValueError(f"Failed to parse variables {data['variables']}: {e}")

        # Create placeholder function that raises error
        def placeholder_function(x, y):
            raise NotImplementedError(
                f"This is a placeholder for a serialized ProceduralCurve '{name}'. "
                "The original function cannot be reconstructed from serialized data."
            )

        return cls(
            placeholder_function,
            variables=variables,
            name=name,
            derivative_scale=data.get("derivative_scale"),
        )

    def bounding_box(self):
        """
        Return bounding box hint for the graphics backend.

        ProceduralCurve has no analytical bounds; returns None so the backend
        falls back to its grid-probe heuristic. Callers that know the domain
        should set ``obj.xmin``, ``obj.xmax``, ``obj.ymin``, ``obj.ymax``
        directly after construction.

        Returns:
            None
        """
        return None

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"ProceduralCurve({self.name})"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"<ProceduralCurve: {self.name}>"
