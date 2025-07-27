# 2D Implicit Geometry Module

# Import all curve classes
from .implicit_curve import ImplicitCurve
from .conic_section import ConicSection
from .polynomial_curve import PolynomialCurve
from .superellipse import Superellipse
from .procedural_curve import ProceduralCurve
from .rfunction_curve import RFunctionCurve

# Import high-level wrapper functions for constructive geometry
from .rfunction_curve import union, intersect, difference, blend

# Define what gets imported with "from geometry import *"
__all__ = [
    # Core curve classes
    'ImplicitCurve',
    'ConicSection', 
    'PolynomialCurve',
    'Superellipse',
    'ProceduralCurve',
    'RFunctionCurve',
    
    # Constructive geometry functions
    'union',
    'intersect', 
    'difference',
    'blend'
]
