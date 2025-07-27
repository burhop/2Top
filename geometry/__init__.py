# 2D Implicit Geometry Module

# Import all curve classes
from .implicit_curve import ImplicitCurve
from .conic_section import ConicSection
from .polynomial_curve import PolynomialCurve
from .superellipse import Superellipse
from .procedural_curve import ProceduralCurve
from .rfunction_curve import RFunctionCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from .composite_curve import CompositeCurve
from .area_region import AreaRegion

# Import high-level wrapper functions for constructive geometry
from .rfunction_curve import union, intersect, difference, blend

# Import utility functions for piecewise curves
from .composite_curve import create_circle_from_quarters, create_square_from_edges

# Define what gets imported with "from geometry import *"
__all__ = [
    # Core curve classes
    'ImplicitCurve',
    'ConicSection', 
    'PolynomialCurve',
    'Superellipse',
    'ProceduralCurve',
    'RFunctionCurve',
    'TrimmedImplicitCurve',
    'CompositeCurve',
    'AreaRegion',
    
    # Constructive geometry functions
    'union',
    'intersect', 
    'difference',
    'blend',
    
    # Piecewise curve utilities
    'create_circle_from_quarters',
    'create_square_from_edges'
]
