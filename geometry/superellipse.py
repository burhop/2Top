"""
Superellipse class - Sprint 3 Task GEO-S3-T2

Implementation of Superellipse subclass of ImplicitCurve for superellipse shapes.
Represents curves of the form |x/a|^n + |y/b|^n = 1, which includes:
- Circles (n=2, a=b)
- Ellipses (n=2, a≠b)  
- Squares (n→∞)
- Diamonds (n=1)
- Various intermediate shapes

The class handles the piecewise nature of absolute value derivatives.
"""

import sympy as sp
import numpy as np
from typing import Tuple, Optional, Union
from .implicit_curve import ImplicitCurve


class Superellipse(ImplicitCurve):
    """
    Represents superellipse curves defined by |x/a|^n + |y/b|^n = 1.
    
    This class handles the family of curves that interpolate between diamonds (n=1),
    circles/ellipses (n=2), and squares (n→∞). The absolute value terms create
    piecewise functions that require special handling for gradient computation.
    """
    
    def __init__(self, a: float, b: float, n: float, 
                 variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None):
        """
        Initialize a Superellipse with shape parameters.
        
        Args:
            a: Semi-axis length in x-direction (must be positive)
            b: Semi-axis length in y-direction (must be positive)
            n: Shape exponent (n=1: diamond, n=2: ellipse, n>2: square-like)
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.
            
        Raises:
            ValueError: If a, b, or n are not positive
        """
        # Validate parameters
        if a <= 0:
            raise ValueError(f"Parameter 'a' must be positive, got {a}")
        if b <= 0:
            raise ValueError(f"Parameter 'b' must be positive, got {b}")
        if n <= 0:
            raise ValueError(f"Parameter 'n' must be positive, got {n}")
        
        # Store parameters
        self.a = float(a)
        self.b = float(b)
        self.n = float(n)
        
        # Set up variables
        if variables is None:
            x, y = sp.symbols('x y', real=True)
            variables = (x, y)
        else:
            x, y = variables
        
        # Construct the superellipse expression: |x/a|^n + |y/b|^n - 1 = 0
        # This represents the implicit equation |x/a|^n + |y/b|^n = 1
        expression = sp.Abs(x/a)**n + sp.Abs(y/b)**n - 1
        
        # Initialize parent class
        super().__init__(expression, variables)
        
        # Cache for gradient computation optimization
        self._gradient_cache = {}
    
    def gradient(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """
        Compute the gradient of the superellipse, handling piecewise nature of absolute values.
        
        Args:
            x: x-coordinate(s) for gradient evaluation
            y: y-coordinate(s) for gradient evaluation
            
        Returns:
            Tuple of (grad_x, grad_y) components
            
        Note:
            The gradient is not defined at points where x=0 or y=0 for n<2.
            This implementation provides a numerical approximation in such cases.
        """
        # Handle scalar inputs
        if np.isscalar(x) and np.isscalar(y):
            return self._gradient_scalar(float(x), float(y))
        
        # Handle array inputs
        x_arr = np.asarray(x)
        y_arr = np.asarray(y)
        
        if x_arr.shape != y_arr.shape:
            raise ValueError("x and y arrays must have the same shape")
        
        # Vectorized gradient computation
        grad_x = np.zeros_like(x_arr, dtype=float)
        grad_y = np.zeros_like(y_arr, dtype=float)
        
        flat_x = x_arr.ravel()
        flat_y = y_arr.ravel()
        flat_grad_x = grad_x.ravel()
        flat_grad_y = grad_y.ravel()
        
        for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
            gx, gy = self._gradient_scalar(float(xi), float(yi))
            flat_grad_x[i] = gx
            flat_grad_y[i] = gy
        
        return grad_x, grad_y
    
    def _gradient_scalar(self, x: float, y: float) -> Tuple[float, float]:
        """
        Compute gradient at a single point, handling absolute value derivatives.
        
        Args:
            x: x-coordinate
            y: y-coordinate
            
        Returns:
            Tuple of (grad_x, grad_y)
        """
        # For superellipse |x/a|^n + |y/b|^n - 1 = 0
        # ∂f/∂x = n * |x/a|^(n-1) * sign(x) / a
        # ∂f/∂y = n * |y/b|^(n-1) * sign(y) / b
        
        # Handle potential singularities at x=0 or y=0
        epsilon = 1e-12
        
        # Compute x-component of gradient
        if abs(x) < epsilon:
            if self.n >= 1.0:
                grad_x = 0.0  # Gradient is zero at x=0 for n>=1
            else:
                # For n<1, gradient is undefined at x=0
                # Use numerical approximation
                grad_x = self._numerical_gradient_x(x, y)
        else:
            # Standard analytical gradient
            abs_x_over_a = abs(x / self.a)
            if abs_x_over_a > 0:
                grad_x = self.n * (abs_x_over_a**(self.n - 1)) * np.sign(x) / self.a
            else:
                grad_x = 0.0
        
        # Compute y-component of gradient
        if abs(y) < epsilon:
            if self.n >= 1.0:
                grad_y = 0.0  # Gradient is zero at y=0 for n>=1
            else:
                # For n<1, gradient is undefined at y=0
                # Use numerical approximation
                grad_y = self._numerical_gradient_y(x, y)
        else:
            # Standard analytical gradient
            abs_y_over_b = abs(y / self.b)
            if abs_y_over_b > 0:
                grad_y = self.n * (abs_y_over_b**(self.n - 1)) * np.sign(y) / self.b
            else:
                grad_y = 0.0
        
        return grad_x, grad_y
    
    def _numerical_gradient_x(self, x: float, y: float, h: float = 1e-8) -> float:
        """Compute numerical gradient in x-direction using finite differences."""
        f_plus = self.evaluate(x + h, y)
        f_minus = self.evaluate(x - h, y)
        return (f_plus - f_minus) / (2 * h)
    
    def _numerical_gradient_y(self, x: float, y: float, h: float = 1e-8) -> float:
        """Compute numerical gradient in y-direction using finite differences."""
        f_plus = self.evaluate(x, y + h)
        f_minus = self.evaluate(x, y - h)
        return (f_plus - f_minus) / (2 * h)
    
    def shape_type(self) -> str:
        """
        Classify the superellipse shape based on the exponent n.
        
        Returns:
            String describing the shape type
        """
        if abs(self.n - 1.0) < 1e-10:
            return "diamond"
        elif abs(self.n - 2.0) < 1e-10:
            if abs(self.a - self.b) < 1e-10:
                return "circle"
            else:
                return "ellipse"
        elif self.n > 2.0:
            return "square-like"
        else:  # 1 < n < 2
            return "rounded-diamond"
    
    def to_dict(self) -> dict:
        """
        Serialize the superellipse to a dictionary.
        
        Returns:
            Dictionary with type "Superellipse" and all necessary reconstruction data
        """
        # Get base serialization
        base_dict = super().to_dict()
        
        # Override type to be more specific
        base_dict["type"] = "Superellipse"
        
        # Add superellipse-specific parameters
        base_dict["a"] = self.a
        base_dict["b"] = self.b
        base_dict["n"] = self.n
        base_dict["shape_type"] = self.shape_type()
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Superellipse':
        """
        Reconstruct a Superellipse from a dictionary.
        
        Args:
            data: Dictionary from to_dict() method
            
        Returns:
            New Superellipse instance
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if data.get("type") != "Superellipse":
            raise ValueError(f"Invalid type: expected 'Superellipse', got {data.get('type')}")
        
        # Extract required parameters
        required_fields = ["a", "b", "n"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        try:
            a = float(data["a"])
            b = float(data["b"])
            n = float(data["n"])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid parameter values: {e}")
        
        # Parse variables if provided
        variables = None
        if "variables" in data:
            try:
                variables = tuple(sp.Symbol(var_str) for var_str in data["variables"])
            except Exception as e:
                raise ValueError(f"Failed to parse variables {data['variables']}: {e}")
        
        return cls(a=a, b=b, n=n, variables=variables)
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"|x/{self.a}|^{self.n} + |y/{self.b}|^{self.n} = 1"
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        shape_type = self.shape_type()
        return f"<Superellipse ({shape_type}): a={self.a}, b={self.b}, n={self.n}>"
