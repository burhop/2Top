"""
RFunctionCurve - Constructive Geometry via R-Functions

This module implements the RFunctionCurve class for Sprint 4, enabling
constructive solid geometry (CSG-like) operations on implicit curves.

The RFunctionCurve combines two child curves using R-function operations:
- Union: min(f1, f2) for sharp union, smooth approximation for blended union
- Intersection: max(f1, f2) for sharp intersection, smooth approximation for blended
- Difference: max(f1, -f2) for sharp difference (A - B)
- Blend: Smooth approximation using quadratic blending formula

Key Features:
- Sharp operations using min/max functions
- Smooth blending with configurable alpha parameter
- Full inheritance from ImplicitCurve interface
- Serialization support for composite curves
- Gradient computation for all operation types
"""

import sympy as sp
import numpy as np
from typing import Tuple, Union, Dict, Any
from .implicit_curve import ImplicitCurve


class RFunctionCurve(ImplicitCurve):
    """
    RFunctionCurve implements constructive geometry operations on implicit curves.

    This class combines two ImplicitCurve objects using R-function operations
    to create new composite curves. Supports both sharp operations (using min/max)
    and smooth blending operations with configurable smoothness parameter.

    Attributes:
        curve1 (ImplicitCurve): First child curve
        curve2 (ImplicitCurve): Second child curve
        operation (str): Operation type ("union", "intersection", "difference", "blend")
        alpha (float): Smoothness parameter for blend operations (0 for sharp)
    """

    def __init__(
        self,
        curve1: ImplicitCurve,
        curve2: ImplicitCurve,
        operation: str,
        alpha: float = 0.0,
        variables: Tuple[sp.Symbol, sp.Symbol] = None,
    ):
        """
        Initialize RFunctionCurve with two child curves and operation type.

        Args:
            curve1: First ImplicitCurve object
            curve2: Second ImplicitCurve object
            operation: Operation type - "union", "intersection", "difference", or "blend"
            alpha: Smoothness parameter for blend operations (must be > 0 for blend)
            variables: Tuple of (x, y) symbols, defaults to curve1.variables

        Raises:
            TypeError: If curve1 or curve2 are not ImplicitCurve instances
            ValueError: If operation is invalid or alpha parameter is incorrect
        """
        # Validate input curves
        if not isinstance(curve1, ImplicitCurve):
            raise TypeError("curve1 must be ImplicitCurve instance")
        if not isinstance(curve2, ImplicitCurve):
            raise TypeError("curve2 must be ImplicitCurve instance")

        # Validate operation type
        valid_operations = {"union", "intersection", "difference", "blend"}
        if operation not in valid_operations:
            raise ValueError(
                f"Invalid operation '{operation}'. Must be one of {valid_operations}"
            )

        # Validate alpha parameter
        if operation == "blend":
            if alpha <= 0:
                raise ValueError("alpha must be positive for blend operations")
        else:
            if alpha != 0.0:
                raise ValueError(f"alpha must be 0 for {operation} operations")

        # Use variables from first curve if not specified
        if variables is None:
            variables = curve1.variables

        # Store child curves and operation parameters
        self.curve1 = curve1
        self.curve2 = curve2
        self.operation = operation
        self.alpha = alpha

        # Create composite expression for parent class if both children have symbolic expressions
        # Otherwise, set expression to None and bypass parent symbolic initialization
        if curve1.expression is None or curve2.expression is None:
            self.expression = None
            self.variables = tuple(variables)
            from .precision import get_precision_policy

            self._precision_policy = get_precision_policy()
            self._eval_func = None
            self._grad_funcs = None
        else:
            x, y = variables
            if operation == "union":
                expression = sp.Min(curve1.expression, curve2.expression)
            elif operation == "intersection":
                expression = sp.Max(curve1.expression, curve2.expression)
            elif operation == "difference":
                expression = sp.Max(curve1.expression, -curve2.expression)
            else:  # blend
                # Symbolic representation of smooth blend (approximation)
                f1, f2 = curve1.expression, curve2.expression
                expression = (f1 + f2 - sp.sqrt((f1 - f2) ** 2 + alpha**2)) / 2

            # Initialize parent class
            super().__init__(expression, variables)

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the R-function curve at given point(s).

        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)

        Returns:
            Function value(s) at the given point(s)
        """
        # Evaluate child curves
        f1 = self.curve1.evaluate(x, y)
        f2 = self.curve2.evaluate(x, y)

        # Apply R-function operation
        if self.operation == "union":
            return self._sharp_union(f1, f2)
        elif self.operation == "intersection":
            return self._sharp_intersection(f1, f2)
        elif self.operation == "difference":
            return self._sharp_difference(f1, f2)
        else:  # blend
            return self._smooth_blend(f1, f2, self.alpha)

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """
        Compute gradient of the R-function curve.

        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)

        Returns:
            Tuple of (grad_x, grad_y) components
        """
        # Get child curve values and gradients
        f1 = self.curve1.evaluate(x, y)
        f2 = self.curve2.evaluate(x, y)
        grad1_x, grad1_y = self.curve1.gradient(x, y)
        grad2_x, grad2_y = self.curve2.gradient(x, y)

        # Compute gradient based on operation type
        if self.operation == "union":
            return self._gradient_sharp_union(
                f1, f2, grad1_x, grad1_y, grad2_x, grad2_y
            )
        elif self.operation == "intersection":
            return self._gradient_sharp_intersection(
                f1, f2, grad1_x, grad1_y, grad2_x, grad2_y
            )
        elif self.operation == "difference":
            return self._gradient_sharp_difference(
                f1, f2, grad1_x, grad1_y, grad2_x, grad2_y
            )
        else:  # blend
            return self._gradient_smooth_blend(
                f1, f2, grad1_x, grad1_y, grad2_x, grad2_y, self.alpha
            )

    def _sharp_union(
        self, f1: Union[float, np.ndarray], f2: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """Sharp union using min(f1, f2)"""
        return np.minimum(f1, f2)

    def _sharp_intersection(
        self, f1: Union[float, np.ndarray], f2: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """Sharp intersection using max(f1, f2)"""
        return np.maximum(f1, f2)

    def _sharp_difference(
        self, f1: Union[float, np.ndarray], f2: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """Sharp difference using max(f1, -f2)"""
        return np.maximum(f1, -f2)

    def _smooth_blend(
        self, f1: Union[float, np.ndarray], f2: Union[float, np.ndarray], alpha: float
    ) -> Union[float, np.ndarray]:
        """
        Smooth blend using quadratic approximation.

        Formula: (f1 + f2 - sqrt((f1-f2)^2 + alpha^2)) / 2
        This approximates min(f1, f2) but with smooth transitions.
        """
        diff = f1 - f2
        return (f1 + f2 - np.sqrt(diff**2 + alpha**2)) / 2

    def _gradient_sharp_union(self, f1, f2, grad1_x, grad1_y, grad2_x, grad2_y):
        """Gradient for sharp union operation"""
        # Use gradient of whichever function is smaller
        if np.isscalar(f1):
            if f1 <= f2:
                return grad1_x, grad1_y
            else:
                return grad2_x, grad2_y
        else:
            # Vectorized case
            mask = f1 <= f2
            grad_x = np.where(mask, grad1_x, grad2_x)
            grad_y = np.where(mask, grad1_y, grad2_y)
            return grad_x, grad_y

    def _gradient_sharp_intersection(self, f1, f2, grad1_x, grad1_y, grad2_x, grad2_y):
        """Gradient for sharp intersection operation"""
        # Use gradient of whichever function is larger
        if np.isscalar(f1):
            if f1 >= f2:
                return grad1_x, grad1_y
            else:
                return grad2_x, grad2_y
        else:
            # Vectorized case
            mask = f1 >= f2
            grad_x = np.where(mask, grad1_x, grad2_x)
            grad_y = np.where(mask, grad1_y, grad2_y)
            return grad_x, grad_y

    def _gradient_sharp_difference(self, f1, f2, grad1_x, grad1_y, grad2_x, grad2_y):
        """Gradient for sharp difference operation"""
        # Difference is max(f1, -f2), so gradient depends on which is larger
        neg_f2 = -f2
        if np.isscalar(f1):
            if f1 >= neg_f2:
                return grad1_x, grad1_y
            else:
                return -grad2_x, -grad2_y
        else:
            # Vectorized case
            mask = f1 >= neg_f2
            grad_x = np.where(mask, grad1_x, -grad2_x)
            grad_y = np.where(mask, grad1_y, -grad2_y)
            return grad_x, grad_y

    def _gradient_smooth_blend(self, f1, f2, grad1_x, grad1_y, grad2_x, grad2_y, alpha):
        """Gradient for smooth blend operation"""
        # Derivative of smooth blend formula
        diff = f1 - f2
        sqrt_term = np.sqrt(diff**2 + alpha**2)

        # Avoid division by zero
        safe_sqrt = np.where(sqrt_term > 1e-12, sqrt_term, 1e-12)

        # Blend weights
        w1 = 0.5 * (1 - diff / safe_sqrt)
        w2 = 0.5 * (1 + diff / safe_sqrt)

        grad_x = w1 * grad1_x + w2 * grad2_x
        grad_y = w1 * grad1_y + w2 * grad2_y

        return grad_x, grad_y

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize RFunctionCurve to dictionary.

        Returns:
            Dictionary containing curve type, operation, alpha, and child curves
        """
        return {
            "type": "RFunctionCurve",
            "operation": self.operation,
            "alpha": self.alpha,
            "curve1": self.curve1.to_dict(),
            "curve2": self.curve2.to_dict(),
            "variables": [str(var) for var in self.variables],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RFunctionCurve":
        """
        Deserialize RFunctionCurve from dictionary.

        Args:
            data: Dictionary containing serialized curve data

        Returns:
            Reconstructed RFunctionCurve instance
        """
        # Reconstruct variables
        var_names = data["variables"]
        variables = tuple(sp.Symbol(name) for name in var_names)

        # Reconstruct child curves
        curve1 = ImplicitCurve.from_dict(data["curve1"])
        curve2 = ImplicitCurve.from_dict(data["curve2"])

        # Create RFunctionCurve
        return cls(
            curve1=curve1,
            curve2=curve2,
            operation=data["operation"],
            alpha=data["alpha"],
            variables=variables,
        )

    def bounding_box(self):
        """
        Return bounding box depending on the R-function operation.

        - union / blend  → union of both child bounding boxes (the result can fill both)
        - intersection   → intersection of both child bounding boxes (result is bounded by both)
        - difference     → bounding box of curve1 (we subtract from it, so it can't grow)

        Returns:
            (xmin, xmax, ymin, ymax) or None if child boxes are unavailable.
        """
        bb1 = getattr(self.curve1, "bounding_box", lambda: None)()
        bb2 = getattr(self.curve2, "bounding_box", lambda: None)()

        if bb1 is None and bb2 is None:
            return None
        # If one is missing, fall back to the other
        if bb1 is None:
            return bb2
        if bb2 is None:
            return bb1

        x1min, x1max, y1min, y1max = bb1
        x2min, x2max, y2min, y2max = bb2

        if self.operation in ("union", "blend"):
            return (
                min(x1min, x2min),
                max(x1max, x2max),
                min(y1min, y2min),
                max(y1max, y2max),
            )
        elif self.operation == "intersection":
            xmin = max(x1min, x2min)
            xmax = min(x1max, x2max)
            ymin = max(y1min, y2min)
            ymax = min(y1max, y2max)
            # If no overlap, fall back to union box
            if xmin >= xmax or ymin >= ymax:
                return (
                    min(x1min, x2min),
                    max(x1max, x2max),
                    min(y1min, y2min),
                    max(y1max, y2max),
                )
            return (xmin, xmax, ymin, ymax)
        else:  # difference: curve1 - curve2
            return bb1

    def get_child_curves(self):
        """
        Return the two child curves as a list for UI tree display.

        Returns:
            [curve1, curve2]
        """
        return [self.curve1, self.curve2]

    def __str__(self) -> str:
        """String representation of RFunctionCurve"""
        if self.operation == "blend":
            return f"RFunctionCurve({self.operation}, alpha={self.alpha})"
        else:
            return f"RFunctionCurve({self.operation})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"RFunctionCurve(curve1={repr(self.curve1)}, "
            f"curve2={repr(self.curve2)}, operation='{self.operation}', "
            f"alpha={self.alpha})"
        )


# High-level wrapper functions for convenient curve construction


def union(curve1: ImplicitCurve, curve2: ImplicitCurve) -> RFunctionCurve:
    """
    Create sharp union of two curves using min(f1, f2).

    Args:
        curve1: First curve
        curve2: Second curve

    Returns:
        RFunctionCurve representing the union
    """
    return RFunctionCurve(curve1, curve2, operation="union")


def intersect(curve1: ImplicitCurve, curve2: ImplicitCurve) -> RFunctionCurve:
    """
    Create sharp intersection of two curves using max(f1, f2).

    Args:
        curve1: First curve
        curve2: Second curve

    Returns:
        RFunctionCurve representing the intersection
    """
    return RFunctionCurve(curve1, curve2, operation="intersection")


def difference(curve1: ImplicitCurve, curve2: ImplicitCurve) -> RFunctionCurve:
    """
    Create sharp difference of two curves (curve1 - curve2) using max(f1, -f2).

    Args:
        curve1: First curve (base)
        curve2: Second curve (to subtract)

    Returns:
        RFunctionCurve representing the difference
    """
    return RFunctionCurve(curve1, curve2, operation="difference")


def blend(curve1: ImplicitCurve, curve2: ImplicitCurve, alpha: float) -> RFunctionCurve:
    """
    Create smooth blend of two curves with configurable smoothness.

    Args:
        curve1: First curve
        curve2: Second curve
        alpha: Smoothness parameter (larger = smoother transitions)

    Returns:
        RFunctionCurve representing the smooth blend
    """
    return RFunctionCurve(curve1, curve2, operation="blend", alpha=alpha)
