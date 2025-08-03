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


class ImplicitCurve:
    """
    Base class for 2D implicit curves defined by equations f(x,y) = 0.
    
    This class provides the core interface for all implicit curves, storing
    a symbolic expression and providing methods to evaluate, differentiate,
    and visualize the curve.
    """
    
    def __init__(self, expression: sp.Expr, variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None):
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
            variables = (sp.Symbol('x'), sp.Symbol('y'))
        
        # Validate variables
        if not isinstance(variables, (tuple, list)) or len(variables) != 2:
            raise ValueError("Variables must be a tuple/list of exactly 2 sympy symbols")
        
        if not all(isinstance(var, sp.Symbol) for var in variables):
            raise ValueError("All variables must be sympy.Symbol instances")
        
        self.expression = expression
        self.variables = tuple(variables)
        
        # Cache for lambdified function (performance optimization)
        self._eval_func = None
        self._grad_funcs = None
    
    def evaluate(self, x_val: Union[float, np.ndarray], y_val: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
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
        
        # Evaluate using the cached lambdified function with overflow protection
        try:
            result = self._eval_func(x_val, y_val)
            # Check for overflow/underflow in the result
            if np.isscalar(result):
                if np.isnan(result):
                    # Treat NaN as "outside" - use large finite value
                    return 1e100
                elif np.isinf(result):
                    # Check if infinity is mathematically correct by checking inputs
                    if np.isinf(x_val) or np.isinf(y_val):
                        # Infinity in inputs should produce infinity in result for polynomial expressions
                        return result  # Preserve the infinity
                    else:
                        # Infinity from numerical overflow - replace with large finite value
                        return 1e100 if result > 0 else -1e100
            else:
                # Handle array results
                result = np.asarray(result)
                # Handle NaN values
                result = np.where(np.isnan(result), 1e100, result)  # Treat NaN as "outside"
                # Handle infinity values - preserve if inputs contain infinity
                if np.any(np.isinf(x_val)) or np.any(np.isinf(y_val)):
                    # Some inputs are infinite, so infinite results may be mathematically correct
                    # Only replace infinity where inputs are finite (indicating numerical overflow)
                    x_finite = np.isfinite(x_val) if hasattr(x_val, '__len__') else np.isfinite(x_val)
                    y_finite = np.isfinite(y_val) if hasattr(y_val, '__len__') else np.isfinite(y_val)
                    inputs_finite = x_finite & y_finite if hasattr(x_finite, '__len__') else (x_finite and y_finite)
                    # Replace infinity only where inputs are finite (numerical overflow)
                    result = np.where(inputs_finite & np.isposinf(result), 1e100, result)
                    result = np.where(inputs_finite & np.isneginf(result), -1e100, result)
                else:
                    # No infinite inputs, so any infinite results are from numerical overflow
                    result = np.where(np.isposinf(result), 1e100, result)
                    result = np.where(np.isneginf(result), -1e100, result)
                return result
            return result
        except OverflowError:
            # Handle overflow during computation
            if np.isscalar(x_val) and np.isscalar(y_val):
                return 1e100  # Large positive value indicates "very far outside"
            else:
                # For array inputs, return array of large values
                x_arr = np.asarray(x_val)
                return np.full_like(x_arr, 1e100, dtype=float)
    
    def gradient(self, x_val: Union[float, np.ndarray], y_val: Union[float, np.ndarray]) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:
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
                sp.lambdify(self.variables, grad_y, "numpy")
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
            raise ValueError(f"Normal undefined at point ({x_val}, {y_val}) - zero gradient")
        
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
    
    def plot(self, xlim: Tuple[float, float] = (-2, 2), ylim: Tuple[float, float] = (-2, 2), 
             resolution: int = 400):
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
        plt.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)
        plt.contourf(X, Y, Z, levels=50, alpha=0.3, cmap='RdBu')
        plt.colorbar(label='f(x,y)')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Implicit Curve: f(x,y) = 0')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
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
            "variables": [str(var) for var in self.variables]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ImplicitCurve':
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
    def _from_dict_base(cls, data: dict) -> 'ImplicitCurve':
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
