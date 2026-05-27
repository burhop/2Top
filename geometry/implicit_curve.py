"""
ImplicitCurve class - Sprint 1 Task GEO-S1-T3

Core implementation of the ImplicitCurve abstract base class for 2D implicit geometry.
Represents curves defined by equations f(x,y) = 0.

Sign convention: f(x,y) < 0 inside, f(x,y) > 0 outside for closed curves.
"""

import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Union, Optional
from abc import abstractmethod

from .precision import PrecisionPolicy, get_precision_policy


class ImplicitCurve:
    """
    Base class for 2D implicit curves defined by equations f(x,y) = 0.

    This class provides the core interface for all implicit curves, storing
    a symbolic expression and providing methods to evaluate, differentiate,
    and visualize the curve.
    """

    def __init__(
        self,
        expression: sp.Expr,
        variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
        precision_policy: Optional[PrecisionPolicy] = None,
    ):
        """
        Initialize an ImplicitCurve with a symbolic expression.

        Args:
            expression: A sympy.Expr defining f(x,y) whose zero contour defines the curve
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.

        Raises:
            TypeError: If expression is not a sympy.Expr
            ValueError: If variables tuple doesn't contain exactly 2 symbols
        """
        # Validate expression type
        if not isinstance(expression, sp.Expr):
            raise TypeError(f"Expression must be a sympy.Expr, got {type(expression)}")

        # Set default variables if not provided
        if variables is None:
            variables = (sp.Symbol("x"), sp.Symbol("y"))

        # Validate variables
        if not isinstance(variables, (tuple, list)) or len(variables) != 2:
            raise ValueError(
                "Variables must be a tuple/list of exactly 2 sympy symbols"
            )

        if not all(isinstance(var, sp.Symbol) for var in variables):
            raise ValueError("All variables must be sympy.Symbol instances")

        self.expression = expression
        self.variables = tuple(variables)
        self._precision_policy = precision_policy or get_precision_policy()

        # Cache for lambdified function (performance optimization)
        self._eval_func = None
        self._grad_funcs = None

    def evaluate(
        self, x_val: Union[float, np.ndarray], y_val: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the implicit function f(x,y) at given point(s).

        Args:
            x_val: x coordinate(s) - can be scalar or numpy array
            y_val: y coordinate(s) - can be scalar or numpy array

        Returns:
            Function value(s) at the given point(s). Returns numpy array if any input is array.

        Note:
            - Returns 0 for points on the curve
            - Returns negative values for points inside closed curves
            - Returns positive values for points outside closed curves
        """
        # Create lambdified function on first use for performance
        if self._eval_func is None:
            self._eval_func = sp.lambdify(self.variables, self.expression, "numpy")

        try:
            result = self._eval_func(x_val, y_val)
            if np.isscalar(result):
                if np.isnan(result):
                    return np.nan
                return float(result)
            else:
                return np.asarray(result, dtype=float)
        except OverflowError:
            if np.isscalar(x_val) and np.isscalar(y_val):
                return float("inf")
            else:
                x_arr = np.asarray(x_val)
                return np.full_like(x_arr, float("inf"), dtype=float)

    @property
    def is_curved(self) -> bool:
        """Return True if the curve is curved (non-linear)."""
        if hasattr(self, "degree"):
            try:
                deg = self.degree()
                return deg > 1
            except Exception:
                pass
        return True

    def get_endpoints(
        self, xmin: Optional[float] = None, xmax: Optional[float] = None
    ) -> list:
        """
        Dynamically calculate and return endpoints (zero-crossings) for periodic curves.

        Args:
            xmin: Optional lower limit to find crossings. If None, uses object/default bounds.
            xmax: Optional upper limit to find crossings. If None, uses object/default bounds.

        Returns:
            List of (x, y) tuples.
        """
        import sympy as sp
        import math

        expr = self.expression
        if expr is None:
            return []
        free = expr.free_symbols
        x_sym = next((s for s in free if s.name == "x"), None)
        y_sym = next((s for s in free if s.name == "y"), None)

        if not x_sym or not y_sym:
            return []

        has_trig = len(expr.atoms(sp.sin)) > 0 or len(expr.atoms(sp.cos)) > 0
        if not has_trig:
            return []

        try:
            df_dy = sp.diff(expr, y_sym)
            df2_dy2 = sp.diff(expr, y_sym, 2)
            df3_dy3 = sp.diff(expr, y_sym, 3)
            df_dx_dy = sp.diff(expr, x_sym, y_sym)

            # Check if quadratic in y and no mixed term
            if df3_dy3 == 0 and df_dx_dy == 0 and df2_dy2 != 0:
                E = df_dy.subs(y_sym, 0)
                D = df2_dy2
                cy_val = float(-E / D)

                # Retrieve bounds if defined
                xmin_val = xmin if xmin is not None else getattr(self, "xmin", -10.0)
                xmax_val = xmax if xmax is not None else getattr(self, "xmax", 10.0)

                # Clean up None bounds
                if xmin_val is None:
                    xmin_val = -10.0
                if xmax_val is None:
                    xmax_val = 10.0

                sin_terms = expr.atoms(sp.sin)
                cos_terms = expr.atoms(sp.cos)

                is_sin = True
                trig_term = None
                if sin_terms:
                    trig_term = list(sin_terms)[0]
                    is_sin = True
                elif cos_terms:
                    trig_term = list(cos_terms)[0]
                    is_sin = False

                if trig_term is not None:
                    arg = trig_term.args[0]
                    B = float(arg.coeff(x_sym))
                    C = float(arg.subs(x_sym, 0))
                    endpoints = []
                    if B != 0:
                        if is_sin:
                            k_min = int(
                                math.floor(((xmin_val - 1.0) * B + C) / math.pi)
                            )
                            k_max = int(math.ceil(((xmax_val + 1.0) * B + C) / math.pi))
                            for k in range(k_min - 2, k_max + 3):
                                x_val = (k * math.pi - C) / B
                                if xmin_val - 0.2 <= x_val <= xmax_val + 0.2:
                                    endpoints.append((x_val, cy_val))
                        else:
                            k_min = int(
                                math.floor(((xmin_val - 1.0) * B + C) / math.pi - 0.5)
                            )
                            k_max = int(
                                math.ceil(((xmax_val + 1.0) * B + C) / math.pi - 0.5)
                            )
                            for k in range(k_min - 2, k_max + 3):
                                x_val = ((k + 0.5) * math.pi - C) / B
                                if xmin_val - 0.2 <= x_val <= xmax_val + 0.2:
                                    endpoints.append((x_val, cy_val))
                    return endpoints
        except Exception:
            pass

        return []

    def gradient(
        self, x_val: Union[float, np.ndarray], y_val: Union[float, np.ndarray]
    ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
        """
        Compute the gradient vector ∇f(x,y) = (∂f/∂x, ∂f/∂y) at given point(s).

        Args:
            x_val: x coordinate(s) - scalar or numpy array
            y_val: y coordinate(s) - scalar or numpy array

        Returns:
            Tuple of (df/dx, df/dy) at the given point(s)
            For scalar inputs: returns (float, float)
            For array inputs: returns (np.ndarray, np.ndarray)

        Note:
            The gradient points in the direction of steepest increase of f.
            For points on the curve, this gives the outward normal direction.
        """
        # Compute symbolic gradients on first use
        if self._grad_funcs is None:
            grad_x = sp.diff(self.expression, self.variables[0])
            grad_y = sp.diff(self.expression, self.variables[1])

            # Create lambdified functions for fast evaluation
            self._grad_funcs = (
                sp.lambdify(self.variables, grad_x, "numpy"),
                sp.lambdify(self.variables, grad_y, "numpy"),
            )

        # Evaluate gradients
        grad_x_val = self._grad_funcs[0](x_val, y_val)
        grad_y_val = self._grad_funcs[1](x_val, y_val)

        # Handle scalar vs array outputs
        if np.isscalar(x_val) and np.isscalar(y_val):
            return (float(grad_x_val), float(grad_y_val))
        else:
            return (np.asarray(grad_x_val), np.asarray(grad_y_val))

    def normal(self, x_val: float, y_val: float) -> Tuple[float, float]:
        """
        Compute the unit normal vector at given point.

        Args:
            x_val: x coordinate
            y_val: y coordinate

        Returns:
            Tuple of (nx, ny) representing the unit normal vector

        Raises:
            ValueError: If gradient magnitude is zero (undefined normal)

        Note:
            The normal vector points outward from the curve (in direction of increasing f).
        """
        grad_x, grad_y = self.gradient(x_val, y_val)

        # Compute magnitude
        magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Handle zero gradient case
        if magnitude < 1e-12:
            raise ValueError(
                f"Normal undefined at point ({x_val}, {y_val}) - zero gradient"
            )

        # Return unit normal
        return (grad_x / magnitude, grad_y / magnitude)

    def field(self, x_val: float, y_val: float) -> float:
        """
        Return the scalar field value at a point.

        For basic ImplicitCurve, this is identical to evaluate().
        The distinction is conceptual - field emphasizes the continuous scalar field interpretation.

        Args:
            x_val: x coordinate
            y_val: y coordinate

        Returns:
            Scalar field value at the point
        """
        return float(self.evaluate(x_val, y_val))

    def plot(
        self,
        xlim: Tuple[float, float] = (-2, 2),
        ylim: Tuple[float, float] = (-2, 2),
        resolution: int = 400,
    ):
        """
        Plot the implicit curve using matplotlib contour.

        Args:
            xlim: x-axis limits as (min, max)
            ylim: y-axis limits as (min, max)
            resolution: Grid resolution for contour plot

        Note:
            This creates a contour plot showing the zero level set of the function.
            Useful for debugging and visualization.
        """
        # Create coordinate grid
        x_vals = np.linspace(xlim[0], xlim[1], resolution)
        y_vals = np.linspace(ylim[0], ylim[1], resolution)
        X, Y = np.meshgrid(x_vals, y_vals)

        # Evaluate function over grid
        Z = self.evaluate(X, Y)

        # Create contour plot
        plt.figure(figsize=(8, 8))
        plt.contour(X, Y, Z, levels=[0], colors="blue", linewidths=2)
        plt.contourf(X, Y, Z, levels=50, alpha=0.3, cmap="RdBu")
        plt.colorbar(label="f(x,y)")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Implicit Curve: f(x,y) = 0")
        plt.grid(True, alpha=0.3)
        plt.axis("equal")
        plt.show()

    def precision_policy(self) -> PrecisionPolicy:
        """Return the precision policy for this curve."""

        return self._precision_policy

    def scale_hint(self) -> float:
        """Return a scale hint (subclasses can override with better estimates)."""

        # Default to unit scale; curve subclasses should provide tighter bounds.
        return 1.0

    def _resolve_tolerance(self, tolerance: Optional[float] = None) -> float:
        """Resolve a caller-provided tolerance against the policy defaults."""

        if tolerance is not None:
            return tolerance
        return self.precision_policy().blended_tolerance(self.scale_hint())

    def on_curve(
        self,
        x_val: Union[float, np.ndarray],
        y_val: Union[float, np.ndarray],
        tolerance: Optional[float] = None,
    ) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are on the curve.

        Base implementation returns False. Subclasses should override this method
        to provide proper curve membership testing.

        Args:
            x_val: x coordinate(s) - can be scalar or numpy array
            y_val: y coordinate(s) - can be scalar or numpy array
            tolerance: Tolerance for curve membership test

        Returns:
            Boolean or array of booleans indicating if points are on the curve
        """
        tol = self._resolve_tolerance(tolerance)
        values = self.evaluate(x_val, y_val)
        if np.isscalar(values):
            return abs(float(values)) <= tol
        values_array = np.asarray(values)
        return np.abs(values_array) <= tol

    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Returns a bounding box (xmin, xmax, ymin, ymax) for the implicit curve.
        This is a placeholder and should be implemented more robustly in subclasses.
        """
        # For now, return a large default bounding box
        return (-1000.0, 1000.0, -1000.0, 1000.0)

    @abstractmethod
    def coefficients(self) -> dict:
        """
        Returns a dictionary of coefficients for the implicit curve expression.
        Keys are sympy symbols or 1 for the constant term, values are coefficients.
        Subclasses must implement this method.
        """
        pass

    def to_dict(self) -> dict:
        """
        Serialize the curve to a dictionary for persistence.

        Returns:
            Dictionary containing all information needed to reconstruct the curve

        Note:
            Critical for scene persistence - must be able to round-trip through from_dict.
        """
        return {
            "type": "ImplicitCurve",
            "expression": str(self.expression),
            "variables": [str(var) for var in self.variables],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ImplicitCurve":
        """
        Reconstruct a curve from a dictionary.

        This method dispatches to the appropriate subclass based on the 'type' field.

        Args:
            data: Dictionary from to_dict() method

        Returns:
            New ImplicitCurve instance of the appropriate subclass

        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        curve_type = data.get("type")
        if not curve_type:
            raise ValueError("Missing required field: type")

        # Dispatch to appropriate subclass
        if curve_type == "ImplicitCurve":
            return cls._from_dict_base(data)
        elif curve_type == "ConicSection":
            from .conic_section import ConicSection

            return ConicSection.from_dict(data)
        elif curve_type == "PolynomialCurve":
            from .polynomial_curve import PolynomialCurve

            return PolynomialCurve.from_dict(data)
        elif curve_type == "Superellipse":
            from .superellipse import Superellipse

            return Superellipse.from_dict(data)
        elif curve_type == "ProceduralCurve":
            from .procedural_curve import ProceduralCurve

            return ProceduralCurve.from_dict(data)
        elif curve_type == "RFunctionCurve":
            from .rfunction_curve import RFunctionCurve

            return RFunctionCurve.from_dict(data)
        elif curve_type == "TrimmedImplicitCurve":
            from .trimmed_implicit_curve import TrimmedImplicitCurve

            return TrimmedImplicitCurve.from_dict(data)
        elif curve_type == "CompositeCurve":
            from .composite_curve import CompositeCurve

            return CompositeCurve.from_dict(data)
        else:
            raise ValueError(f"Unknown curve type: {curve_type}")

    @classmethod
    def _from_dict_base(cls, data: dict) -> "ImplicitCurve":
        """
        Reconstruct base ImplicitCurve from dictionary.

        Args:
            data: Dictionary from to_dict() method

        Returns:
            New ImplicitCurve instance
        """
        if "expression" not in data:
            raise ValueError("Missing required field: expression")

        # Parse expression string back to sympy
        try:
            expression = sp.sympify(data["expression"])
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{data['expression']}': {e}")

        # Parse variables if provided
        variables = None
        if "variables" in data:
            try:
                variables = tuple(sp.Symbol(var_str) for var_str in data["variables"])
            except Exception as e:
                raise ValueError(f"Failed to parse variables {data['variables']}: {e}")

        return cls(expression, variables)

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.expression} = 0"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"<ImplicitCurve: {self.expression} = 0>"
