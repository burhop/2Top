"""
Parameter Interface for Animatable Geometry Objects

Defines the interface that geometry classes must implement to support
parameter-based animations in the SceneManager.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import copy


class ParameterInterface(ABC):
    """
    Interface for objects that support parameter animation.
    
    All geometry classes that want to be animatable should inherit from this
    interface and implement the required methods.
    """
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Return dictionary of all animatable parameters and their current values.
        
        Returns:
            Dict mapping parameter names to current values
        """
        pass
    
    @abstractmethod
    def set_parameter(self, name: str, value: Any) -> None:
        """
        Set a specific parameter value and trigger internal updates.
        
        Args:
            name: Parameter name
            value: New parameter value
            
        Raises:
            KeyError: If parameter name is not valid
            ValueError: If parameter value is invalid
        """
        pass
    
    @abstractmethod
    def get_parameter(self, name: str) -> Any:
        """
        Get the current value of a specific parameter.
        
        Args:
            name: Parameter name
            
        Returns:
            Current parameter value
            
        Raises:
            KeyError: If parameter name is not valid
        """
        pass
    
    @abstractmethod
    def list_parameters(self) -> List[str]:
        """
        Return list of all parameter names that can be animated.
        
        Returns:
            List of parameter names
        """
        pass
    
    @abstractmethod
    def clone(self) -> 'ParameterInterface':
        """
        Create a deep copy of the object for frame caching.
        
        Returns:
            Deep copy of the object
        """
        pass
    
    def refresh_from_dependencies(self) -> None:
        """
        Refresh object state when dependencies change.
        
        Default implementation does nothing. Override if object needs
        to update internal state when dependent objects change.
        """
        pass


class ParameterMixin:
    """
    Mixin class providing default parameter management functionality.
    
    Classes can inherit from this to get basic parameter support,
    then override specific methods as needed.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parameters = {}
    
    def get_parameters(self) -> Dict[str, Any]:
        """Default implementation returns copy of internal parameters dict."""
        return self._parameters.copy()
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Default implementation updates internal parameters dict."""
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        self._parameters[name] = value
        self._on_parameter_changed(name, value)
    
    def get_parameter(self, name: str) -> Any:
        """Default implementation gets from internal parameters dict."""
        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        return self._parameters[name]
    
    def list_parameters(self) -> List[str]:
        """Default implementation returns keys of internal parameters dict."""
        return list(self._parameters.keys())
    
    def clone(self):
        """Default implementation uses deepcopy."""
        return copy.deepcopy(self)
    
    def _on_parameter_changed(self, name: str, value: Any) -> None:
        """
        Hook called when parameter changes.
        
        Override this to implement custom parameter change logic.
        """
        pass


# Example implementations for common parameter types

class CircleParameters(ParameterMixin):
    """Example parameter implementation for circles."""
    
    def __init__(self, center_x: float = 0, center_y: float = 0, radius: float = 1):
        super().__init__()
        self._parameters = {
            'center_x': center_x,
            'center_y': center_y,
            'radius': radius
        }
    
    def _on_parameter_changed(self, name: str, value: Any) -> None:
        """Update internal state when parameters change."""
        if name == 'radius' and value <= 0:
            raise ValueError("Radius must be positive")
        
        # Trigger expression rebuild if this was a real geometry class
        self._rebuild_expression()
    
    def _rebuild_expression(self) -> None:
        """Rebuild the implicit expression from current parameters."""
        # In a real implementation, this would update the sympy expression
        # For example: (x - center_x)^2 + (y - center_y)^2 - radius^2 = 0
        pass


class RectangleParameters(ParameterMixin):
    """Example parameter implementation for rectangles."""
    
    def __init__(self, center_x: float = 0, center_y: float = 0, 
                 width: float = 2, height: float = 2):
        super().__init__()
        self._parameters = {
            'center_x': center_x,
            'center_y': center_y,
            'width': width,
            'height': height
        }
    
    def _on_parameter_changed(self, name: str, value: Any) -> None:
        """Update internal state when parameters change."""
        if name in ['width', 'height'] and value <= 0:
            raise ValueError(f"{name} must be positive")
        
        # Rebuild composite curve boundary
        self._rebuild_boundary()
    
    def _rebuild_boundary(self) -> None:
        """Rebuild the composite curve boundary from current parameters."""
        # In a real implementation, this would update the CompositeCurve
        # with new line segments based on current parameters
        pass


class TriangleParameters(ParameterMixin):
    """Example parameter implementation for triangles."""
    
    def __init__(self, x1: float = -1, y1: float = -1, 
                 x2: float = 1, y2: float = -1,
                 x3: float = 0, y3: float = 1):
        super().__init__()
        self._parameters = {
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2,
            'x3': x3, 'y3': y3
        }
    
    def _on_parameter_changed(self, name: str, value: Any) -> None:
        """Update internal state when parameters change."""
        # Validate triangle is not degenerate
        self._validate_triangle()
        
        # Rebuild composite curve boundary and half-space metadata
        self._rebuild_boundary()
        self._rebuild_halfspace_metadata()
    
    def _validate_triangle(self) -> None:
        """Ensure triangle vertices form a valid non-degenerate triangle."""
        p = self._parameters
        x1, y1 = p['x1'], p['y1']
        x2, y2 = p['x2'], p['y2']
        x3, y3 = p['x3'], p['y3']
        
        # Check area is non-zero (cross product)
        area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
        if area < 1e-10:
            raise ValueError("Triangle vertices are collinear (zero area)")
    
    def _rebuild_boundary(self) -> None:
        """Rebuild the composite curve boundary from current parameters."""
        # In a real implementation, this would update the CompositeCurve
        # with new line segments connecting the triangle vertices
        pass
    
    def _rebuild_halfspace_metadata(self) -> None:
        """Rebuild half-space metadata for fast containment."""
        # In a real implementation, this would recalculate the
        # _convex_edges_abc metadata using the corrected formula
        pass
