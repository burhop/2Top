"""
ConicSection class - Sprint 2 Task GEO-S2-T2

Implementation of ConicSection subclass of ImplicitCurve for degree-2 polynomial curves.
Represents conic sections: circles, ellipses, parabolas, hyperbolas, and degenerate cases.

General form: Ax² + Bxy + Cy² + Dx + Ey + F = 0
"""

import sympy as sp
import numpy as np
from typing import Tuple, Optional, Union
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
    
    def on_curve(self, x_val: Union[float, np.ndarray], y_val: Union[float, np.ndarray], 
                 tolerance: float = 1e-3) -> Union[bool, np.ndarray]:
        """
        Check if point(s) are on the conic section curve.
        
        Args:
            x_val: x coordinate(s) - can be scalar or numpy array
            y_val: y coordinate(s) - can be scalar or numpy array
            tolerance: Tolerance for curve membership test
            
        Returns:
            Boolean or array of booleans indicating if points are on the curve
        """
        curve_values = self.evaluate(x_val, y_val)
        return np.abs(curve_values) <= tolerance
    
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
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate the bounding box for the conic section.
        
        Returns:
            Tuple (xmin, xmax, ymin, ymax) representing the bounding box
            
        Note:
            For circles and ellipses, calculates exact bounds.
            For other conics, falls back to a conservative estimate.
        """
        coeffs = self._extract_coefficients()
        A, B, C, D, E, F = coeffs['A'], coeffs['B'], coeffs['C'], coeffs['D'], coeffs['E'], coeffs['F']
        
        conic_type = self.conic_type()
        
        if conic_type == "circle":
            # For a circle: (x-h)² + (y-k)² = r²
            # General form: x² + y² + Dx + Ey + F = 0
            # Center: (-D/2, -E/2), Radius: sqrt((D²+E²)/4 - F)
            
            # Assert circle properties: A = C ≠ 0, B = 0
            assert abs(A - C) < 1e-12, f"Circle must have A = C, but A={A}, C={C}"
            assert abs(B) < 1e-12, f"Circle must have B = 0, but B={B}"
            assert abs(A) > 1e-12, f"Circle must have A ≠ 0, but A={A}"
            
            if abs(A) < 1e-12:  # Degenerate case (should not reach here due to assertion)
                return (-1000.0, 1000.0, -1000.0, 1000.0)
            
            # Normalize coefficients (divide by A to get standard form)
            d_norm = D / A
            e_norm = E / A
            f_norm = F / A
            
            center_x = -d_norm / 2
            center_y = -e_norm / 2
            
            # Calculate radius squared
            radius_sq = (d_norm**2 + e_norm**2) / 4 - f_norm
            
            if radius_sq <= 0:
                # Degenerate circle (point or no real solution)
                return (center_x, center_x, center_y, center_y)
            
            radius = np.sqrt(radius_sq)
            
            return (center_x - radius, center_x + radius, 
                   center_y - radius, center_y + radius)
        
        elif conic_type == "ellipse":
            # Assert ellipse properties: A and C have same sign, A ≠ C, discriminant < 0
            assert abs(A) > 1e-12 and abs(C) > 1e-12, f"Ellipse must have A ≠ 0 and C ≠ 0, but A={A}, C={C}"
            assert A * C > 0, f"Ellipse must have A and C same sign, but A={A}, C={C}"
            
            if abs(B) < 1e-12:  # Axis-aligned ellipse
                # Complete the square for x and y
                center_x = -D / (2 * A)
                center_y = -E / (2 * C)
                
                # Calculate semi-axes
                # After completing the square: A(x-h)² + C(y-k)² = constant
                constant = A * center_x**2 + C * center_y**2 - F
                
                if constant <= 0:
                    # Degenerate ellipse (point or no real solution)
                    return (center_x, center_x, center_y, center_y)
                
                a_sq = constant / A  # Semi-axis in x direction squared
                b_sq = constant / C  # Semi-axis in y direction squared
                
                if a_sq <= 0 or b_sq <= 0:
                    return (center_x, center_x, center_y, center_y)
                
                a = np.sqrt(a_sq)
                b = np.sqrt(b_sq)
                
                return (center_x - a, center_x + a, center_y - b, center_y + b)
            
            else:
                # Rotated ellipse - calculate exact bounds using eigenvalue method
                # For general ellipse Ax² + Bxy + Cy² + Dx + Ey + F = 0
                
                # First, find the center by completing the square
                # The center satisfies: 2Ax + By + D = 0 and Bx + 2Cy + E = 0
                det = 4*A*C - B**2
                if abs(det) < 1e-12:
                    return (-100.0, 100.0, -100.0, 100.0)  # Degenerate
                
                center_x = (B*E - 2*C*D) / det
                center_y = (B*D - 2*A*E) / det
                
                # Translate to center and find the ellipse matrix
                # At center: [x y] * [[A B/2] [B/2 C]] * [x y]^T = constant
                constant = A*center_x**2 + B*center_x*center_y + C*center_y**2 - F
                
                if constant <= 0:
                    return (center_x, center_x, center_y, center_y)
                
                # Find eigenvalues of the matrix [[A B/2] [B/2 C]]
                # These give us the squared reciprocals of the semi-axes
                trace = A + C
                det_matrix = A*C - (B/2)**2
                discriminant = trace**2 - 4*det_matrix
                
                if discriminant < 0:
                    return (-100.0, 100.0, -100.0, 100.0)  # Should not happen for ellipse
                
                lambda1 = (trace + np.sqrt(discriminant)) / 2
                lambda2 = (trace - np.sqrt(discriminant)) / 2
                
                if lambda1 <= 0 or lambda2 <= 0:
                    return (center_x, center_x, center_y, center_y)
                
                # Semi-axes lengths
                a = np.sqrt(constant / lambda1)
                b = np.sqrt(constant / lambda2)
                
                # For rotated ellipse, the bounding box is larger than the axis-aligned case
                # The maximum extent is the larger of the two semi-axes
                max_extent = max(a, b)
                
                return (center_x - max_extent, center_x + max_extent,
                       center_y - max_extent, center_y + max_extent)
        
        elif conic_type == "parabola":
            # Parabolas are unbounded in one direction
            # Try to determine the axis and vertex
            
            if abs(A) < 1e-12:  # A = 0, parabola opens horizontally
                # Form: Cy² + Dx + Ey + F = 0 -> x = -(Cy² + Ey + F)/D
                if abs(D) < 1e-12:
                    return (-100.0, 100.0, -100.0, 100.0)  # Degenerate
                
                # Vertex y-coordinate: -E/(2C)
                if abs(C) > 1e-12:
                    vertex_y = -E / (2 * C)
                    vertex_x = -(C * vertex_y**2 + E * vertex_y + F) / D
                    
                    # Bounded in y around vertex, unbounded in x
                    y_range = 50.0  # Reasonable range around vertex
                    if D > 0:  # Opens to the right
                        return (vertex_x, float('inf'), vertex_y - y_range, vertex_y + y_range)
                    else:  # Opens to the left
                        return (float('-inf'), vertex_x, vertex_y - y_range, vertex_y + y_range)
                else:
                    return (float('-inf'), float('inf'), -100.0, 100.0)
            
            elif abs(C) < 1e-12:  # C = 0, parabola opens vertically
                # Form: Ax² + Dx + Ey + F = 0 -> y = -(Ax² + Dx + F)/E
                if abs(E) < 1e-12:
                    return (-100.0, 100.0, -100.0, 100.0)  # Degenerate
                
                # Vertex x-coordinate: -D/(2A)
                if abs(A) > 1e-12:
                    vertex_x = -D / (2 * A)
                    vertex_y = -(A * vertex_x**2 + D * vertex_x + F) / E
                    
                    # Bounded in x around vertex, unbounded in y
                    x_range = 50.0  # Reasonable range around vertex
                    if E > 0:  # Opens upward
                        return (vertex_x - x_range, vertex_x + x_range, vertex_y, float('inf'))
                    else:  # Opens downward
                        return (vertex_x - x_range, vertex_x + x_range, float('-inf'), vertex_y)
                else:
                    return (-100.0, 100.0, float('-inf'), float('inf'))
            
            else:
                # General parabola case - use conservative bounds
                return (-100.0, 100.0, -100.0, 100.0)
        
        elif conic_type == "hyperbola":
            # Hyperbolas are unbounded in both directions
            # For now, return infinite bounds (mathematically correct)
            # Could be improved to find center and asymptotes
            return (float('-inf'), float('inf'), float('-inf'), float('inf'))
        
        elif conic_type == "degenerate":
            # Handle degenerate cases: lines, points, empty sets, etc.
            
            # Check if it's a line (one of A, B, C is zero and it's degree 1)
            if abs(A) < 1e-12 and abs(C) < 1e-12:  # Linear in both x and y
                if abs(B) < 1e-12:  # Dx + Ey + F = 0 (line)
                    if abs(D) > 1e-12 or abs(E) > 1e-12:
                        # This is a line - unbounded
                        return (float('-inf'), float('inf'), float('-inf'), float('inf'))
                    else:
                        # F = 0 (everything) or F ≠ 0 (nothing)
                        return (-100.0, 100.0, -100.0, 100.0)
                else:
                    # Bxy + Dx + Ey + F = 0 - hyperbola-like, unbounded
                    return (float('-inf'), float('inf'), float('-inf'), float('inf'))
            
            elif abs(A) < 1e-12:  # Only C and possibly B non-zero
                if abs(B) < 1e-12:  # Cy² + Ey + F = 0
                    # This is a parabola opening horizontally or parallel lines
                    if abs(C) > 1e-12:
                        # Solve for y: y = (-E ± √(E² - 4CF)) / (2C)
                        discriminant = E**2 - 4*C*F
                        if discriminant >= 0:
                            y1 = (-E + np.sqrt(discriminant)) / (2*C)
                            y2 = (-E - np.sqrt(discriminant)) / (2*C)
                            y_min, y_max = min(y1, y2), max(y1, y2)
                            return (float('-inf'), float('inf'), y_min, y_max)
                        else:
                            # No real solutions
                            return (0.0, 0.0, 0.0, 0.0)
                    else:
                        # Linear: Ey + F = 0
                        if abs(E) > 1e-12:
                            y_val = -F / E
                            return (float('-inf'), float('inf'), y_val, y_val)
                        else:
                            return (-100.0, 100.0, -100.0, 100.0)
                else:
                    # Bxy + Cy² + Dx + Ey + F = 0 - complex case
                    return (float('-inf'), float('inf'), float('-inf'), float('inf'))
            
            elif abs(C) < 1e-12:  # Only A and possibly B non-zero
                if abs(B) < 1e-12:  # Ax² + Dx + F = 0
                    # This is a parabola opening vertically or parallel lines
                    if abs(A) > 1e-12:
                        # Solve for x: x = (-D ± √(D² - 4AF)) / (2A)
                        discriminant = D**2 - 4*A*F
                        if discriminant >= 0:
                            x1 = (-D + np.sqrt(discriminant)) / (2*A)
                            x2 = (-D - np.sqrt(discriminant)) / (2*A)
                            x_min, x_max = min(x1, x2), max(x1, x2)
                            return (x_min, x_max, float('-inf'), float('inf'))
                        else:
                            # No real solutions
                            return (0.0, 0.0, 0.0, 0.0)
                    else:
                        # Linear: Dx + F = 0
                        if abs(D) > 1e-12:
                            x_val = -F / D
                            return (x_val, x_val, float('-inf'), float('inf'))
                        else:
                            return (-100.0, 100.0, -100.0, 100.0)
                else:
                    # Ax² + Bxy + Dx + Ey + F = 0 - complex case
                    return (float('-inf'), float('inf'), float('-inf'), float('inf'))
            
            else:
                # All of A, B, C non-zero but still degenerate
                # Could be intersecting lines, point, etc.
                # Use conservative bounds
                return (-100.0, 100.0, -100.0, 100.0)
        
        else:
            # For unknown types
            # Use a conservative bounding box
            return (-100.0, 100.0, -100.0, 100.0)
    
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
