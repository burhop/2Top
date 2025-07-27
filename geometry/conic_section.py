"""
ConicSection class - Sprint 2 Task GEO-S2-T2

Implementation of ConicSection subclass of ImplicitCurve for degree-2 polynomial curves.
Represents conic sections: circles, ellipses, parabolas, hyperbolas, and degenerate cases.

General form: Ax² + Bxy + Cy² + Dx + Ey + F = 0
"""

import sympy as sp
import numpy as np
from typing import Tuple, Optional
from .implicit_curve import ImplicitCurve


class ConicSection(ImplicitCurve):
    """
    Represents conic sections (degree-2 implicit curves).
    
    This class handles circles, ellipses, parabolas, hyperbolas, and degenerate cases.
    It provides specialized methods for geometric analysis such as conic type classification.
    """
    
    def __init__(self, expression: sp.Expr, variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None):
        """
        Initialize a ConicSection with a symbolic expression.
        
        Args:
            expression: A sympy.Expr defining the conic section (typically degree 2)
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.
            
        Note:
            While this class is designed for degree-2 polynomials, it can handle other
            expressions but the conic_type() method may give unexpected results.
        """
        # Initialize using parent class
        super().__init__(expression, variables)
        
        # Cache for conic coefficients (performance optimization)
        self._coefficients = None
    
    def _extract_coefficients(self) -> dict:
        """
        Extract coefficients from the general conic form Ax² + Bxy + Cy² + Dx + Ey + F = 0.
        
        Returns:
            Dictionary with keys 'A', 'B', 'C', 'D', 'E', 'F' containing the coefficients
        """
        if self._coefficients is not None:
            return self._coefficients
        
        x, y = self.variables
        
        # Expand the expression to ensure we can extract coefficients
        expanded_expr = sp.expand(self.expression)
        
        # Extract coefficients for each term
        # Use sympy's coeff method to get coefficients of specific terms
        A = expanded_expr.coeff(x, 2).coeff(y, 0) if expanded_expr.coeff(x, 2) else 0
        B = expanded_expr.coeff(x, 1).coeff(y, 1) if expanded_expr.coeff(x, 1) else 0
        C = expanded_expr.coeff(x, 0).coeff(y, 2) if expanded_expr.coeff(x, 0) else 0
        D = expanded_expr.coeff(x, 1).coeff(y, 0) if expanded_expr.coeff(x, 1) else 0
        E = expanded_expr.coeff(x, 0).coeff(y, 1) if expanded_expr.coeff(x, 0) else 0
        F = expanded_expr.coeff(x, 0).coeff(y, 0) if expanded_expr.coeff(x, 0) else 0
        
        # Handle cases where coeff returns None
        A = A if A is not None else 0
        B = B if B is not None else 0
        C = C if C is not None else 0
        D = D if D is not None else 0
        E = E if E is not None else 0
        F = F if F is not None else 0
        
        self._coefficients = {
            'A': float(A),
            'B': float(B), 
            'C': float(C),
            'D': float(D),
            'E': float(E),
            'F': float(F)
        }
        
        return self._coefficients
    
    def conic_type(self) -> str:
        """
        Determine the type of conic section using discriminant analysis.
        
        Returns:
            String indicating conic type: "circle", "ellipse", "parabola", "hyperbola", or "degenerate"
            
        Note:
            Uses the discriminant B² - 4AC to classify the conic:
            - B² - 4AC < 0: ellipse (circle if A = C and B = 0)
            - B² - 4AC = 0: parabola
            - B² - 4AC > 0: hyperbola
        """
        coeffs = self._extract_coefficients()
        A, B, C = coeffs['A'], coeffs['B'], coeffs['C']
        
        # Calculate discriminant
        discriminant = B**2 - 4*A*C
        
        # Handle degenerate cases first
        if abs(A) < 1e-12 and abs(B) < 1e-12 and abs(C) < 1e-12:
            return "degenerate"  # Not a quadratic
        
        # Classify based on discriminant
        if abs(discriminant) < 1e-12:  # discriminant ≈ 0
            return "parabola"
        elif discriminant < 0:  # discriminant < 0
            # Check if it's a circle (A = C and B = 0)
            if abs(A - C) < 1e-12 and abs(B) < 1e-12:
                return "circle"
            else:
                return "ellipse"
        else:  # discriminant > 0
            return "hyperbola"
    
    def degree(self) -> int:
        """
        Return the degree of the conic section.
        
        Returns:
            Always returns 2 for conic sections
            
        Note:
            This method always returns 2 as conic sections are by definition degree-2 curves.
        """
        return 2
    
    def canonical_form(self) -> 'ConicSection':
        """
        Return an equivalent ConicSection in canonical (simplified) coordinate frame.
        
        Returns:
            New ConicSection with simplified expression (translation and rotation applied)
            
        Note:
            This is a simplified implementation. A full implementation would involve
            completing the square and handling rotation to eliminate xy terms.
        """
        # For now, return a copy of self
        # A full implementation would involve complex coordinate transformations
        return ConicSection(self.expression, self.variables)
    
    def to_dict(self) -> dict:
        """
        Serialize the conic section to a dictionary.
        
        Returns:
            Dictionary with type "ConicSection" and all necessary reconstruction data
        """
        # Get base serialization
        base_dict = super().to_dict()
        
        # Override type to be more specific
        base_dict["type"] = "ConicSection"
        
        # Could add additional conic-specific information
        base_dict["conic_type"] = self.conic_type()
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConicSection':
        """
        Reconstruct a ConicSection from a dictionary.
        
        Args:
            data: Dictionary from to_dict() method
            
        Returns:
            New ConicSection instance
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Handle both "ConicSection" and "ImplicitCurve" types for compatibility
        if data.get("type") not in ["ConicSection", "ImplicitCurve"]:
            raise ValueError(f"Invalid type: expected 'ConicSection' or 'ImplicitCurve', got {data.get('type')}")
        
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
        conic_type = self.conic_type()
        return f"<ConicSection ({conic_type}): {self.expression} = 0>"
