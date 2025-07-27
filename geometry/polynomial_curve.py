"""
PolynomialCurve class - Sprint 2 Task GEO-S2-T4

Implementation of PolynomialCurve subclass of ImplicitCurve for general polynomial curves.
Represents implicit curves defined by polynomial equations of any degree.

General form: P(x,y) = 0 where P is a polynomial in x and y
"""

import sympy as sp
import numpy as np
from typing import Tuple, Optional
from .implicit_curve import ImplicitCurve


class PolynomialCurve(ImplicitCurve):
    """
    Represents general polynomial implicit curves of any degree.
    
    This class handles polynomial equations P(x,y) = 0 where P is a polynomial
    in two variables. It provides specialized methods for polynomial analysis
    such as degree computation.
    """
    
    def __init__(self, expression: sp.Expr, variables: Optional[Tuple[sp.Symbol, sp.Symbol]] = None):
        """
        Initialize a PolynomialCurve with a symbolic expression.
        
        Args:
            expression: A sympy.Expr defining the polynomial curve
            variables: Tuple of two sympy symbols (x, y). If None, uses default x, y symbols.
            
        Note:
            While this class is designed for polynomial expressions, it can handle
            non-polynomial expressions but the degree() method may give unexpected results.
        """
        # Initialize using parent class
        super().__init__(expression, variables)
        
        # Cache for degree computation (performance optimization)
        self._degree_cache = None
    
    def degree(self) -> int:
        """
        Compute the total degree of the polynomial.
        
        Returns:
            Integer representing the highest total degree of any term in the polynomial
            
        Note:
            The degree is the maximum sum of exponents in any term. For example:
            - x² + y² has degree 2
            - x³y + xy³ has degree 4 (both terms have degree 4)
            - x⁵ + x²y² + y has degree 5 (x⁵ term has highest degree)
            
        Raises:
            ValueError: If the expression is not a polynomial or degree cannot be computed
        """
        if self._degree_cache is not None:
            return self._degree_cache
        
        try:
            # Convert expression to polynomial form
            x, y = self.variables
            
            # Use sympy's polynomial tools to compute degree
            # First, try to convert to a polynomial
            poly = sp.poly(self.expression, x, y)
            
            # Get the total degree using sympy's total_degree method
            degree = poly.total_degree()
            
            self._degree_cache = degree
            return degree
            
        except (sp.PolynomialError, ValueError, AttributeError) as e:
            # If expression is not a polynomial, try alternative approach
            try:
                # Expand the expression and find maximum degree manually
                expanded = sp.expand(self.expression)
                
                # If it's a single term, compute its degree
                if expanded.is_Add:
                    terms = expanded.args
                else:
                    terms = [expanded]
                
                max_degree = 0
                x, y = self.variables
                
                for term in terms:
                    # Get degree of this term
                    term_degree = 0
                    
                    # Extract powers of x and y
                    if term.has(x):
                        x_power = sp.degree(term, x)
                        term_degree += x_power
                    
                    if term.has(y):
                        y_power = sp.degree(term, y)
                        term_degree += y_power
                    
                    max_degree = max(max_degree, term_degree)
                
                self._degree_cache = max_degree
                return max_degree
                
            except Exception:
                # Last resort: if we can't compute degree, raise error
                raise ValueError(f"Cannot compute degree of expression: {self.expression}")
    
    def to_dict(self) -> dict:
        """
        Serialize the polynomial curve to a dictionary.
        
        Returns:
            Dictionary with type "PolynomialCurve" and all necessary reconstruction data
        """
        # Get base serialization
        base_dict = super().to_dict()
        
        # Override type to be more specific
        base_dict["type"] = "PolynomialCurve"
        
        # Add polynomial-specific information
        try:
            base_dict["degree"] = self.degree()
        except ValueError:
            # If degree cannot be computed, don't include it
            pass
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PolynomialCurve':
        """
        Reconstruct a PolynomialCurve from a dictionary.
        
        Args:
            data: Dictionary from to_dict() method
            
        Returns:
            New PolynomialCurve instance
            
        Raises:
            ValueError: If data is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        # Handle both "PolynomialCurve" and "ImplicitCurve" types for compatibility
        if data.get("type") not in ["PolynomialCurve", "ImplicitCurve"]:
            raise ValueError(f"Invalid type: expected 'PolynomialCurve' or 'ImplicitCurve', got {data.get('type')}")
        
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
        try:
            degree = self.degree()
            return f"<PolynomialCurve (degree {degree}): {self.expression} = 0>"
        except ValueError:
            return f"<PolynomialCurve: {self.expression} = 0>"
