"""
Utilities package for visual tests.

Contains common functionality for plotting, creating test objects,
and evaluating grids of points.
"""

from .plotting import PlotManager
from .test_objects import CurveFactory, RegionFactory
from .grid_evaluation import GridEvaluator

__all__ = [
    'PlotManager',
    'CurveFactory',
    'RegionFactory', 
    'GridEvaluator'
]
