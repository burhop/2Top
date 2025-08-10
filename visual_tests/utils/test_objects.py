"""
Factory classes for creating test objects.

Provides standardized methods for creating various types of curves and regions
for visual testing, with consistent parameters and error handling.
"""

import sympy as sp
import numpy as np
from typing import Tuple, List, Callable, Optional
from geometry import (
    ImplicitCurve, ConicSection, PolynomialCurve, TrimmedImplicitCurve,
    CompositeCurve, AreaRegion
)


class CurveFactory:
    """
    Factory for creating various types of implicit curves for testing.
    """
    
    @staticmethod
    def create_circle(center: Tuple[float, float] = (0, 0), 
                     radius: float = 2) -> ConicSection:
        """
        Create a circle curve.
        
        Args:
            center: Circle center (x, y)
            radius: Circle radius
            
        Returns:
            ConicSection representing the circle
        """
        x, y = sp.symbols('x y')
        cx, cy = center
        circle_expr = (x - cx)**2 + (y - cy)**2 - radius**2
        return ConicSection(circle_expr, (x, y))
    
    @staticmethod
    def create_ellipse(center: Tuple[float, float] = (0, 0),
                      a: float = 2, b: float = 1) -> ConicSection:
        """
        Create an ellipse curve.
        
        Args:
            center: Ellipse center (x, y)
            a: Semi-major axis length
            b: Semi-minor axis length
            
        Returns:
            ConicSection representing the ellipse
        """
        x, y = sp.symbols('x y')
        cx, cy = center
        ellipse_expr = (x - cx)**2/a**2 + (y - cy)**2/b**2 - 1
        return ConicSection(ellipse_expr, (x, y))
    
    @staticmethod
    def create_hyperbola(center: Tuple[float, float] = (0, 0),
                        a: float = 1, b: float = 1) -> ConicSection:
        """
        Create a hyperbola curve.
        
        Args:
            center: Hyperbola center (x, y)
            a: Parameter a
            b: Parameter b
            
        Returns:
            ConicSection representing the hyperbola
        """
        x, y = sp.symbols('x y')
        cx, cy = center
        hyperbola_expr = (x - cx)**2/a**2 - (y - cy)**2/b**2 - 1
        return ConicSection(hyperbola_expr, (x, y))
    
    @staticmethod
    def create_parabola(vertex: Tuple[float, float] = (0, 0),
                       direction: str = 'up', scale: float = 1) -> ConicSection:
        """
        Create a parabola curve.
        
        Args:
            vertex: Parabola vertex (x, y)
            direction: Direction ('up', 'down', 'left', 'right')
            scale: Scaling factor
            
        Returns:
            ConicSection representing the parabola
        """
        x, y = sp.symbols('x y')
        vx, vy = vertex
        
        if direction == 'up':
            parabola_expr = (y - vy) - scale * (x - vx)**2
        elif direction == 'down':
            parabola_expr = (y - vy) + scale * (x - vx)**2
        elif direction == 'right':
            parabola_expr = (x - vx) - scale * (y - vy)**2
        elif direction == 'left':
            parabola_expr = (x - vx) + scale * (y - vy)**2
        else:
            raise ValueError(f"Invalid direction: {direction}")
            
        return ConicSection(parabola_expr, (x, y))
    
    @staticmethod
    def create_line(point1: Tuple[float, float], 
                   point2: Tuple[float, float]) -> PolynomialCurve:
        """
        Create a line through two points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            PolynomialCurve representing the line
        """
        x, y = sp.symbols('x y')
        x1, y1 = point1
        x2, y2 = point2
        
        # Line equation: (y2-y1)x - (x2-x1)y + (x2-x1)y1 - (y2-y1)x1 = 0
        line_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
        return PolynomialCurve(line_expr, (x, y))
    
    @staticmethod
    def create_cubic_curve(expression: Optional[str] = None) -> PolynomialCurve:
        """
        Create a cubic curve.
        
        Args:
            expression: Optional custom expression. If None, uses default.
            
        Returns:
            PolynomialCurve representing the cubic
        """
        x, y = sp.symbols('x y')
        
        if expression is None:
            # Default: y^2 = x^3 - x (cubic with interesting shape)
            cubic_expr = y**2 - x**3 + x
        else:
            cubic_expr = sp.sympify(expression)
            
        return PolynomialCurve(cubic_expr, (x, y))
    
    @staticmethod
    def create_trimmed_circle(center: Tuple[float, float] = (0, 0),
                             radius: float = 1,
                             mask_function: Optional[Callable] = None) -> TrimmedImplicitCurve:
        """
        Create a trimmed circle.
        
        Args:
            center: Circle center (x, y)
            radius: Circle radius
            mask_function: Optional custom mask. If None, uses upper half.
            
        Returns:
            TrimmedImplicitCurve representing the trimmed circle
        """
        circle = CurveFactory.create_circle(center, radius)
        
        if mask_function is None:
            # Default: upper half
            mask_function = lambda px, py: py >= center[1]
            
        return TrimmedImplicitCurve(circle, mask_function)
    
    @staticmethod
    def create_composite_circle_quarters(center: Tuple[float, float] = (0, 0),
                                       radius: float = 1.5) -> CompositeCurve:
        """
        Create a composite curve from circle quarters.
        
        Args:
            center: Circle center (x, y)
            radius: Circle radius
            
        Returns:
            CompositeCurve with two quarter-circle segments
        """
        x, y = sp.symbols('x y')
        cx, cy = center
        
        circle_base = CurveFactory.create_circle(center, radius)
        
        # First quarter (upper right): x >= cx, y >= cy
        quarter1_mask = lambda px, py: px >= cx and py >= cy
        quarter1 = TrimmedImplicitCurve(circle_base, quarter1_mask)
        
        # Third quarter (lower left): x <= cx, y <= cy
        quarter3_mask = lambda px, py: px <= cx and py <= cy
        quarter3 = TrimmedImplicitCurve(circle_base, quarter3_mask)
        
        return CompositeCurve([quarter1, quarter3], (x, y))


class RegionFactory:
    """
    Factory for creating various types of area regions for testing.
    """
    
    @staticmethod
    def create_circle_region(center: Tuple[float, float] = (0, 0),
                           radius: float = 2) -> AreaRegion:
        """
        Create a circular area region.
        
        Args:
            center: Circle center (x, y)
            radius: Circle radius
            
        Returns:
            AreaRegion representing the filled circle
        """
        x, y = sp.symbols('x y')
        
        # Create circle curve
        circle_curve = CurveFactory.create_circle(center, radius)
        
        # First try direct creation from the implicit circle (preferred)
        try:
            return AreaRegion(circle_curve)
        except Exception:
            # Fallback: build a closed composite from four quarter-circle segments
            cx, cy = center
            q1_mask = lambda px, py: (px >= cx) and (py >= cy)   # NE
            q2_mask = lambda px, py: (px <= cx) and (py >= cy)   # NW
            q3_mask = lambda px, py: (px <= cx) and (py <= cy)   # SW
            q4_mask = lambda px, py: (px >= cx) and (py <= cy)   # SE

            q1 = TrimmedImplicitCurve(circle_curve, q1_mask)
            q2 = TrimmedImplicitCurve(circle_curve, q2_mask)
            q3 = TrimmedImplicitCurve(circle_curve, q3_mask)
            q4 = TrimmedImplicitCurve(circle_curve, q4_mask)

            circle_composite = CompositeCurve([q1, q2, q3, q4], (x, y))
            return AreaRegion(circle_composite)
    
    @staticmethod
    def create_triangle_region(vertices: List[Tuple[float, float]]) -> AreaRegion:
        """
        Create a triangular area region from three vertices using the proven working method.
        
        Args:
            vertices: List of three (x, y) vertex coordinates
            
        Returns:
            AreaRegion representing the filled triangle
        """
        if len(vertices) != 3:
            raise ValueError("Triangle requires exactly 3 vertices")
            
        x, y = sp.symbols('x y')
        v1, v2, v3 = vertices
        
        # Create 3 line segments for the triangle edges using the working original method
        segments = []
        
        # Edge 1: v1 to v2
        x1, y1 = v1
        x2, y2 = v2
        edge1_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
        edge1_curve = ImplicitCurve(edge1_expr, (x, y))
        
        def edge1_mask(px, py):
            # Use parametric form: point = v1 + t*(v2-v1) where 0 <= t <= 1
            dx = x2 - x1
            dy = y2 - y1
            if abs(dx) > abs(dy):
                if dx == 0:
                    return False
                t = (px - x1) / dx
            else:
                if dy == 0:
                    return False
                t = (py - y1) / dy
            return 0 <= t <= 1
        
        edge1_segment = TrimmedImplicitCurve(edge1_curve, edge1_mask, endpoints=[v1, v2])
        segments.append(edge1_segment)
        
        # Edge 2: v2 to v3
        x1, y1 = v2
        x2, y2 = v3
        edge2_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
        edge2_curve = ImplicitCurve(edge2_expr, (x, y))
        
        def edge2_mask(px, py):
            dx = x2 - x1
            dy = y2 - y1
            if abs(dx) > abs(dy):
                if dx == 0:
                    return False
                t = (px - x1) / dx
            else:
                if dy == 0:
                    return False
                t = (py - y1) / dy
            return 0 <= t <= 1
        
        edge2_segment = TrimmedImplicitCurve(edge2_curve, edge2_mask, endpoints=[v2, v3])
        segments.append(edge2_segment)
        
        # Edge 3: v3 to v1
        x1, y1 = v3
        x2, y2 = v1
        edge3_expr = (y2 - y1) * x - (x2 - x1) * y + (x2 - x1) * y1 - (y2 - y1) * x1
        edge3_curve = ImplicitCurve(edge3_expr, (x, y))
        
        def edge3_mask(px, py):
            dx = x2 - x1
            dy = y2 - y1
            if abs(dx) > abs(dy):
                if dx == 0:
                    return False
                t = (px - x1) / dx
            else:
                if dy == 0:
                    return False
                t = (py - y1) / dy
            return 0 <= t <= 1
        
        edge3_segment = TrimmedImplicitCurve(edge3_curve, edge3_mask, endpoints=[v3, v1])
        segments.append(edge3_segment)
        
        # Create composite curve with the 3 line segments
        triangle_composite = CompositeCurve(segments, (x, y))

        # Annotate as convex polygon for fast, correct region containment.
        # For CCW-ordered vertices, a point is inside if it's on the left side of each directed edge.
        # For edge from (x1,y1) to (x2,y2), the half-space is: (x2-x1)*(y-y1) - (y2-y1)*(x-x1) >= 0
        # Rearranging: -(y2-y1)*x + (x2-x1)*y + (y2-y1)*x1 - (x2-x1)*y1 >= 0
        # CompositeCurve expects Ax+By+C <= tol, so we negate: (y2-y1)*x - (x2-x1)*y - (y2-y1)*x1 + (x2-x1)*y1 <= 0
        edges_abc = []
        ordered = [v1, v2, v3]
        for i in range(3):
            (x1, y1) = ordered[i]
            (x2, y2) = ordered[(i + 1) % 3]
            A = (y2 - y1)
            B = -(x2 - x1)
            C = -(y2 - y1) * x1 + (x2 - x1) * y1
            edges_abc.append((A, B, C))
        triangle_composite._is_convex_polygon = True
        triangle_composite._convex_edges_abc = edges_abc
        
        # Create the area region
        return AreaRegion(triangle_composite)
    
    @staticmethod
    def create_rectangle_region(corner1: Tuple[float, float],
                              corner2: Tuple[float, float]) -> AreaRegion:
        """
        Create a rectangular area region.
        
        Args:
            corner1: First corner (x, y)
            corner2: Opposite corner (x, y)
            
        Returns:
            AreaRegion representing the filled rectangle
        """
        x1, y1 = corner1
        x2, y2 = corner2
        
        # Ensure proper ordering
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        # Create rectangle from four vertices
        vertices = [
            (min_x, min_y),  # Bottom left
            (max_x, min_y),  # Bottom right
            (max_x, max_y),  # Top right
            (min_x, max_y)   # Top left
        ]
        
        x, y = sp.symbols('x y')
        segments = []
        
        for i in range(4):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 4]
            
            # Create line for this edge
            line_curve = CurveFactory.create_line(v1, v2)
            
            # Create mask for the edge segment
            def create_edge_mask(vertex1, vertex2):
                def mask(px, py):
                    # More tolerant line check
                    line_val = abs(line_curve.evaluate(px, py))
                    if line_val > 0.1:
                        return False
                    
                    # Check bounds with small tolerance
                    min_x_seg = min(vertex1[0], vertex2[0]) - 0.01
                    max_x_seg = max(vertex1[0], vertex2[0]) + 0.01
                    min_y_seg = min(vertex1[1], vertex2[1]) - 0.01
                    max_y_seg = max(vertex1[1], vertex2[1]) + 0.01
                    
                    return min_x_seg <= px <= max_x_seg and min_y_seg <= py <= max_y_seg
                
                return mask
            
            edge_mask = create_edge_mask(v1, v2)
            trimmed_edge = TrimmedImplicitCurve(line_curve, edge_mask)
            segments.append(trimmed_edge)
        
        # Create composite curve from the four edges
        rectangle_boundary = CompositeCurve(segments, (x, y))

        # Tag as axis-aligned square/rectangle for fast path in CompositeCurve.contains/evaluate
        rectangle_boundary._is_square = True
        rectangle_boundary._square_bounds = (min_x, max_x, min_y, max_y)

        # Also provide convex polygon half-space representation
        verts = vertices  # CCW order: BL -> BR -> TR -> TL
        edges_abc = []
        for i in range(4):
            (x1e, y1e) = verts[i]
            (x2e, y2e) = verts[(i + 1) % 4]
            A = (y2e - y1e)
            B = -(x2e - x1e)
            C = (x2e - x1e) * y1e - (y2e - y1e) * x1e
            edges_abc.append((-A, -B, -C))
        rectangle_boundary._is_convex_polygon = True
        rectangle_boundary._convex_edges_abc = edges_abc
        
        # Create the area region
        return AreaRegion(rectangle_boundary)
    
    @staticmethod
    def create_region_with_hole(outer_region: AreaRegion,
                              hole_region: AreaRegion) -> AreaRegion:
        """
        Create a region with a hole (conceptual - actual implementation may vary).
        
        Args:
            outer_region: The outer boundary region
            hole_region: The hole region to subtract
            
        Returns:
            AreaRegion with hole (simplified implementation)
        """
        # Note: This is a simplified implementation
        # Full boolean operations would require more complex geometry
        print("Warning: Region with hole is a simplified implementation")
        return outer_region  # For now, just return the outer region
    
    @staticmethod
    def get_standard_test_regions() -> List[Tuple[str, AreaRegion]]:
        """
        Get a list of standard test regions for comprehensive testing.
        
        Returns:
            List of (name, region) tuples
        """
        regions = []
        
        # Circle
        circle = RegionFactory.create_circle_region((0, 0), 2)
        regions.append(("Circle", circle))
        
        # Triangle
        triangle_vertices = [(-2, -1.5), (2, -1.5), (0, 2)]
        triangle = RegionFactory.create_triangle_region(triangle_vertices)
        regions.append(("Triangle", triangle))
        
        # Rectangle
        rectangle = RegionFactory.create_rectangle_region((-1.5, -1), (1.5, 1))
        regions.append(("Rectangle", rectangle))
        
        return regions
