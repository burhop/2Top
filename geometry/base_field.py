"""
BaseField abstract class and field implementations for scalar field operations.

This module implements the BaseField hierarchy for representing and manipulating
scalar fields in 2D space. Scalar fields are functions that map (x, y) coordinates
to scalar values, useful for visualization, procedural texturing, and physical
simulations.

Key Features:
- BaseField abstract class with unified interface (evaluate, gradient, level_set)
- CurveField wraps ImplicitCurve objects as scalar fields
- BlendedField combines multiple fields using algebraic operations
- SampledField provides grid-backed field representation
- Full serialization support for persistence
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Tuple, List
from .implicit_curve import ImplicitCurve
from .bounds import SublevelBounds, rational_level


class BaseField(ABC):
    """
    Abstract base class for all scalar fields.

    A scalar field is a function that maps 2D coordinates (x, y) to scalar values.
    This class defines the common interface that all field types must implement,
    including evaluation, gradient computation, and level set extraction.

    The BaseField class enables:
    - Unified interface for all field types
    - Consistent evaluation and gradient computation
    - Level set extraction for creating implicit curves
    - Serialization support for persistence
    """

    @abstractmethod
    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the scalar field at given coordinates.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Scalar value(s) of the field at the given coordinates
        """
        pass

    @abstractmethod
    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
        """
        Compute the gradient of the scalar field at given coordinates.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Tuple of (grad_x, grad_y) representing the gradient vector(s)
        """
        pass

    @abstractmethod
    def level_set(self, level: float) -> ImplicitCurve:
        """
        Extract a level set (contour) from the scalar field.

        A level set is the set of all points where the field equals a specific value.
        This method returns an ImplicitCurve representing that contour.

        Args:
            level: The level value to extract as a contour

        Returns:
            ImplicitCurve representing the level set
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the field to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseField":
        """
        Reconstruct a field from a dictionary.

        Args:
            data: Dictionary representation of the field

        Returns:
            Reconstructed BaseField instance
        """
        pass

    def sublevel_bounds(self, level=0):
        """Unknown unless a field implementation supplies an enclosure proof."""
        rational_level(level)
        return SublevelBounds(
            "unknown", reason="Field has no certified sublevel envelope"
        )

    def clear_cache(self) -> None:
        """Clear any cached evaluation results."""
        pass

    def __str__(self) -> str:
        """String representation of the field."""
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        """Detailed string representation of the field."""
        return f"{self.__class__.__name__}()"


class CurveField(BaseField):
    """
    Scalar field derived from an ImplicitCurve.

    CurveField wraps an ImplicitCurve and exposes it as a scalar field.
    The field value at any point is simply the curve's evaluation at that point,
    following the implicit curve convention (negative inside, positive outside).

    This allows implicit curves to be used in field operations and provides
    a bridge between the curve and field representations.

    Attributes:
        curve (ImplicitCurve): The underlying implicit curve
    """

    def __init__(self, curve: ImplicitCurve):
        """
        Initialize a CurveField from an ImplicitCurve.

        Args:
            curve: The ImplicitCurve to wrap as a scalar field

        Raises:
            TypeError: If curve is not an ImplicitCurve instance
        """
        if not isinstance(curve, ImplicitCurve):
            raise TypeError("curve must be an ImplicitCurve instance")

        self.curve = curve

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the field by delegating to the underlying curve.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Field value(s) at the given coordinates
        """
        return self.curve.evaluate(x, y)

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
        """
        Compute the gradient by delegating to the underlying curve.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Gradient vector(s) at the given coordinates
        """
        return self.curve.gradient(x, y)

    def gradient_diagnostics(self, x, y):
        """Opt-in diagnostics preserving wrapped uncertainty and callbacks."""
        from .field_algebra import (
            _method_is,
            algebraic_diagnostics,
            callback_diagnostics,
        )

        if not _method_is(self, "gradient", CurveField.gradient):
            return callback_diagnostics(self.evaluate, self.gradient, x, y)
        if not _method_is(self, "evaluate", CurveField.evaluate):
            return callback_diagnostics(self.evaluate, None, x, y)
        return algebraic_diagnostics(self, x, y)

    def level_set(self, level: float) -> ImplicitCurve:
        """
        Extract a level set from the field.

        For a CurveField, the level set is created by shifting the original curve
        by the specified level value.

        Args:
            level: The level value to extract

        Returns:
            ImplicitCurve representing the level set
        """
        # Keep the kinetic recipe specialization and its serialized identity.
        from .kinetic_field import KineticIslandCurve

        if isinstance(self.curve, KineticIslandCurve):
            from .kinetic import _finite_number

            shift = _finite_number(level, "level")
            return self.curve.field.level_set(self.curve.level + shift)

        from .level_set_curve import LevelSetCurve

        return LevelSetCurve(self.curve, level)

    def sublevel_bounds(self, level=0):
        if getattr(self.evaluate, "__func__", None) is not CurveField.evaluate:
            rational_level(level)
            return SublevelBounds("unknown", reason="Custom CurveField evaluator")
        return self.curve.sublevel_bounds(level)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the CurveField to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        return {"type": "CurveField", "curve": self.curve.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurveField":
        """
        Reconstruct a CurveField from a dictionary.

        Args:
            data: Dictionary representation of the field

        Returns:
            Reconstructed CurveField instance

        Raises:
            ValueError: If the dictionary format is invalid
        """
        if data.get("type") != "CurveField":
            raise ValueError("Dictionary does not represent a CurveField")

        # Reconstruct the underlying curve
        curve = ImplicitCurve.from_dict(data["curve"])

        return cls(curve)

    def __str__(self) -> str:
        """String representation of the CurveField."""
        return f"CurveField({self.curve})"

    def __repr__(self) -> str:
        """Detailed string representation of the CurveField."""
        return f"CurveField(curve={repr(self.curve)})"


class BlendedField(BaseField):
    """
    Scalar field that combines two or more fields using algebraic operations.

    BlendedField takes multiple BaseField objects and combines them using
    operations like addition, multiplication, minimum, maximum, etc. This
    enables complex field compositions and procedural field generation.

    Supported operations:
    - "add": f1 + f2
    - "subtract": f1 - f2
    - "multiply": f1 * f2
    - "divide": f1 / f2
    - "min": min(f1, f2)
    - "max": max(f1, f2)
    - "average": (f1 + f2) / 2

    Attributes:
        fields (List[BaseField]): The fields to combine
        operation (str): The operation to apply
    """

    SUPPORTED_OPERATIONS = {
        "add",
        "subtract",
        "multiply",
        "divide",
        "min",
        "max",
        "average",
    }

    def __init__(self, fields: List[BaseField], operation: str = "add"):
        """
        Initialize a BlendedField from multiple fields and an operation.

        Args:
            fields: List of BaseField objects to combine
            operation: The operation to apply ("add", "multiply", "min", etc.)

        Raises:
            TypeError: If fields contains non-BaseField objects
            ValueError: If operation is not supported or fields list is empty
        """
        if not fields:
            raise ValueError("At least two fields are required")

        if len(fields) < 2:
            raise ValueError("At least two fields are required")

        for i, field in enumerate(fields):
            if not isinstance(field, BaseField):
                raise TypeError("All fields must be BaseField instances")

        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(
                f"Unsupported operation '{operation}'. Supported: {self.SUPPORTED_OPERATIONS}"
            )

        self.fields = fields.copy()  # Create a copy to avoid external modification
        self.operation = operation

    def evaluate(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        Evaluate the blended field by combining child field evaluations.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Combined field value(s) at the given coordinates
        """
        from .field_algebra import algebraic_query

        return algebraic_query(self, x, y)

    def gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]
    ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
        """
        Compute the gradient of the blended field.

        The gradient is computed using the chain rule and the operation type.
        For most operations, this involves combining the gradients of the child fields.

        Args:
            x: x-coordinate(s) to evaluate
            y: y-coordinate(s) to evaluate

        Returns:
            Gradient vector(s) at the given coordinates
        """
        from .field_algebra import algebraic_query, _method_is
        from .numeric import broadcast_coordinates, field_result

        if not _method_is(self, "evaluate", BlendedField.evaluate):
            xx, yy, scalar = broadcast_coordinates(x, y)
            return tuple(
                field_result(v, xx.shape, scalar)
                for v in self._numerical_gradient(xx, yy)
            )
        return algebraic_query(self, x, y, gradient=True)

    def gradient_diagnostics(self, x, y):
        """Explicit graph diagnostics; hot gradient() adds no adaptive probes."""
        from .field_algebra import (
            _method_is,
            algebraic_diagnostics,
            callback_diagnostics,
        )

        if not _method_is(self, "gradient", BlendedField.gradient):
            return callback_diagnostics(self.evaluate, self.gradient, x, y)
        if not _method_is(self, "evaluate", BlendedField.evaluate):
            return callback_diagnostics(self.evaluate, None, x, y)
        return algebraic_diagnostics(self, x, y)

    def _numerical_gradient(
        self, x: Union[float, np.ndarray], y: Union[float, np.ndarray], h: float = 1e-6
    ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
        """
        Compute numerical gradient using finite differences.

        Args:
            x: x-coordinate(s)
            y: y-coordinate(s)
            h: Step size for finite differences

        Returns:
            Numerical gradient vector(s)
        """
        # Compute partial derivatives using central differences
        grad_x = (self.evaluate(x + h, y) - self.evaluate(x - h, y)) / (2 * h)
        grad_y = (self.evaluate(x, y + h) - self.evaluate(x, y - h)) / (2 * h)

        return (grad_x, grad_y)

    def level_set(self, level: float) -> ImplicitCurve:
        """
        Extract a level set from the blended field.

        This creates an ImplicitCurve representing the contour where the
        blended field equals the specified level value.

        Args:
            level: The level value to extract

        Returns:
            ImplicitCurve representing the level set
        """
        import sympy as sp

        # Create symbolic variables
        x, y = sp.symbols("x y")

        from .field_algebra import _AlgebraicLevelSet

        try:
            level = float(rational_level(level))
        except OverflowError as error:
            raise ValueError("Level shift must fit a finite float") from error
        if not np.isfinite(level):
            raise ValueError("Level shift must fit a finite float")
        return _AlgebraicLevelSet(self, level, (x, y))

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the BlendedField to a dictionary.

        Returns:
            Dictionary representation of the field
        """
        return {
            "type": "BlendedField",
            "fields": [field.to_dict() for field in self.fields],
            "operation": self.operation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlendedField":
        """
        Reconstruct a BlendedField from a dictionary.

        Args:
            data: Dictionary representation of the field

        Returns:
            Reconstructed BlendedField instance

        Raises:
            ValueError: If the dictionary format is invalid
        """
        if data.get("type") != "BlendedField":
            raise ValueError("Dictionary does not represent a BlendedField")

        # Reconstruct child fields
        fields = []
        for field_data in data["fields"]:
            field_type = field_data.get("type")
            if field_type == "CurveField":
                fields.append(CurveField.from_dict(field_data))
            elif field_type == "BlendedField":
                fields.append(BlendedField.from_dict(field_data))
            elif field_type == "KineticIslandField":
                from .kinetic_field import KineticIslandField

                fields.append(KineticIslandField.from_dict(field_data))
            elif field_type == "SignedDistanceField":
                from geometry.field_strategy import SignedDistanceField

                fields.append(SignedDistanceField.from_dict(field_data))
            elif field_type == "OccupancyField":
                from geometry.field_strategy import OccupancyField

                fields.append(OccupancyField.from_dict(field_data))
            else:
                raise ValueError(f"Unknown field type: {field_type}")

        operation = data["operation"]

        return cls(fields, operation)

    def __str__(self) -> str:
        """String representation of the BlendedField."""
        return f"BlendedField({len(self.fields)} fields, operation='{self.operation}')"

    def __repr__(self) -> str:
        """Detailed string representation of the BlendedField."""
        return f"BlendedField(fields={repr(self.fields)}, operation='{self.operation}')"
