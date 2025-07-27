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


class ProceduralCurve(ImplicitCurve):
    """
    Represents implicit curves defined by arbitrary Python functions.
    
    This class allows wrapping any Python callable that takes (x, y) coordinates
    and returns a numeric value representing the implicit function f(x,y).
    Since the function is not symbolic, gradients are computed numerically.
    """
    
    def __init__(self, function: Callable[[float, float], float], 
                 variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None,
                 name: str = "custom"):
        """
        Initialize a ProceduralCurve with a Python function.
        
        Args:
            function: Python callable that takes (x, y) and returns f(x, y)
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.
            name: Descriptive name for the function (used in serialization and display)
            
        Raises:
            ValueError: If function is not callable
        """
        # Validate function
        if not callable(function):
            raise ValueError("function must be callable")
        
        # Store the function and metadata
        self.function = function
        self.name = name
        
        # Set up variables
        if variables is None:
            x, y = sp.symbols('x y', real=True)
            variables = (x, y)
        
        # Set up variables
        self._variables = variables
        
        # ProceduralCurve doesn't have a symbolic expression
        # We set expression to None and handle it specially
        self.expression = None
        self.variables = variables
        
        # Don't call super().__init__ since we don't have a symbolic expression
        # Instead, manually set up what we need
        self._eval_func = None  # We'll use our own function
        self._grad_funcs = None  # We'll compute gradients numerically
        
        # Finite difference step size for numerical gradient
        self._gradient_h = 1e-8
    
    def evaluate(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Evaluate the procedural curve at given coordinates.
        
        Args:
            x: x-coordinate(s) for evaluation
            y: y-coordinate(s) for evaluation
            
        Returns:
            Function value(s) at the given coordinates
        """
        # Handle scalar inputs
        if np.isscalar(x) and np.isscalar(y):
            return self.function(float(x), float(y))
        
        # Handle array inputs
        x_arr = np.asarray(x)
        y_arr = np.asarray(y)
        
        if x_arr.shape != y_arr.shape:
            raise ValueError("x and y arrays must have the same shape")
        
        # Vectorized evaluation
        result = np.zeros_like(x_arr, dtype=float)
        flat_x = x_arr.flatten()
        flat_y = y_arr.flatten()
        flat_result = result.flatten()
        
        for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
            flat_result[i] = self.function(float(xi), float(yi))
        
        return result
    
    def gradient(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
        """
        Compute the gradient using finite differences.
        
        Args:
            x: x-coordinate(s) for gradient evaluation
            y: y-coordinate(s) for gradient evaluation
            
        Returns:
            Tuple of (grad_x, grad_y) components computed numerically
            
        Note:
            Uses central finite differences for numerical gradient approximation.
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
        
        flat_x = x_arr.flatten()
        flat_y = y_arr.flatten()
        flat_grad_x = grad_x.flatten()
        flat_grad_y = grad_y.flatten()
        
        for i, (xi, yi) in enumerate(zip(flat_x, flat_y)):
            gx, gy = self._gradient_scalar(float(xi), float(yi))
            flat_grad_x[i] = gx
            flat_grad_y[i] = gy
        
        return grad_x, grad_y
    
    def _gradient_scalar(self, x: float, y: float) -> Tuple[float, float]:
        """
        Compute numerical gradient at a single point using finite differences.
        
        Args:
            x: x-coordinate
            y: y-coordinate
            
        Returns:
            Tuple of (grad_x, grad_y)
        """
        h = self._gradient_h
        
        # Central finite difference for x-component
        f_x_plus = self.function(x + h, y)
        f_x_minus = self.function(x - h, y)
        grad_x = (f_x_plus - f_x_minus) / (2 * h)
        
        # Central finite difference for y-component
        f_y_plus = self.function(x, y + h)
        f_y_minus = self.function(x, y - h)
        grad_y = (f_y_plus - f_y_minus) / (2 * h)
        
        return grad_x, grad_y
    
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
            "function": self.name,  # Use name as placeholder
            "variables": [str(var) for var in self.variables],
            "name": self.name
        }
        
        # Add warning about serialization limitations
        data["_serialization_note"] = "Function code cannot be serialized. This is a placeholder."
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProceduralCurve':
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
            raise ValueError(f"Invalid type: expected 'ProceduralCurve', got {data.get('type')}")
        
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
        
        return cls(placeholder_function, variables=variables, name=name)
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"ProceduralCurve({self.name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return f"<ProceduralCurve: {self.name}>"
