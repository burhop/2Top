"""
Visual Tests Package for 2D Implicit Geometry Library

This package contains organized visual tests for the geometry library,
including utilities, curve tests, region tests, and comprehensive demonstrations.
"""

from .utils.plotting import PlotManager
from .utils.test_objects import CurveFactory, RegionFactory
from .utils.grid_evaluation import GridEvaluator

__all__ = [
    'PlotManager',
    'CurveFactory', 
    'RegionFactory',
    'GridEvaluator'
]
