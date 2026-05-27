"""
Utilities package for visual tests.

Contains common functionality for plotting, creating test objects,
and evaluating grids of points.
"""

from .plotting import PlotManager, register_embed_viewer
from .test_objects import CurveFactory, RegionFactory
from .grid_evaluation import GridEvaluator
from .baseline_manager import VisualBaselineManager, get_baseline_manager

__all__ = [
    "PlotManager",
    "register_embed_viewer",
    "CurveFactory",
    "RegionFactory",
    "GridEvaluator",
    "VisualBaselineManager",
    "get_baseline_manager",
]
