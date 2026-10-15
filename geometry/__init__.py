# 2D Implicit Geometry Module

# Import all curve classes
from .implicit_curve import ImplicitCurve
from .bounds import SublevelBounds
from .intersection_diagnostics import diagnose_intersection_candidates
from .level_set_curve import LevelSetCurve
from .conic_section import ConicSection
from .polynomial_curve import PolynomialCurve
from .superellipse import Superellipse
from .procedural_curve import ProceduralCurve
from .rfunction_curve import RFunctionCurve
from .trimmed_implicit_curve import TrimmedImplicitCurve
from .composite_curve import CompositeCurve
from .area_region import AreaRegion
from .precision import (
    PrecisionPolicy,
    get_precision_policy,
    set_precision_policy,
    precision_context,
)

# Import high-level wrapper functions for constructive geometry
from .rfunction_curve import union, intersect, difference, blend

# Import utility functions for piecewise curves
from .composite_curve import create_circle_from_quarters, create_square_from_edges

# Import scalar field classes
from .base_field import BaseField, CurveField, BlendedField
from .kinetic_field import KineticIslandField, KineticIslandCurve

# Import field strategy classes
from .field_strategy import (
    FieldStrategy,
    SignedDistanceStrategy,
    OccupancyFillStrategy,
    SignedDistanceField,
    OccupancyField,
)

# Define what gets imported with "from geometry import *"
__all__ = [
    # Core curve classes
    "ImplicitCurve",
    "SublevelBounds",
    "diagnose_intersection_candidates",
    "LevelSetCurve",
    "ConicSection",
    "PolynomialCurve",
    "Superellipse",
    "ProceduralCurve",
    "RFunctionCurve",
    "TrimmedImplicitCurve",
    "CompositeCurve",
    "AreaRegion",
    "PrecisionPolicy",
    "get_precision_policy",
    "set_precision_policy",
    "precision_context",
    # Constructive geometry functions
    "union",
    "intersect",
    "difference",
    "blend",
    # Piecewise curve utilities
    "create_circle_from_quarters",
    "create_square_from_edges",
    # Scalar field classes
    "BaseField",
    "CurveField",
    "BlendedField",
    "KineticIslandField",
    "KineticIslandCurve",
    # Field strategy classes
    "FieldStrategy",
    "SignedDistanceStrategy",
    "OccupancyFillStrategy",
    "SignedDistanceField",
    "OccupancyField",
]
