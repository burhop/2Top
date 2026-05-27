"""
Performance benchmark tests for graphics backend operations.

Uses pytest-benchmark (when installed) for detailed timing analysis,
plus hard time-gate tests that always run to catch regressions.

Run benchmarks:       pytest tests/test_graphics_performance.py --benchmark-only
Run gate tests only:  pytest tests/test_graphics_performance.py -k TestPerformanceGates
"""

import sys
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest
import sympy as sp

from graphics_backend.graphics_interface import GraphicsBackendInterface
from scene_management.scene_manager import SceneManager
from visual_tests.utils.test_objects import RegionFactory
from geometry.conic_section import ConicSection

_x, _y = sp.symbols("x y")


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _circle(cx=0, cy=0, r=1):
    """Create a ConicSection circle centred at (cx, cy) with radius r."""
    return ConicSection((_x - cx) ** 2 + (_y - cy) ** 2 - r**2, (_x, _y))


def _build_single_circle_scene():
    """Return a SceneManager containing one circle."""
    sm = SceneManager()
    factory = RegionFactory()
    circle = factory.create_circle_region((0, 0), 1.0)
    sm.add_object("circle", circle)
    sm.set_style("circle", {"color": "blue", "linewidth": 2})
    return sm


def _build_three_object_scene():
    """Return a SceneManager containing three distinct objects."""
    sm = SceneManager()
    factory = RegionFactory()

    circle = factory.create_circle_region((0, 0), 1.0)
    sm.add_object("circle", circle)
    sm.set_style("circle", {"color": "blue", "linewidth": 2})

    circle2 = factory.create_circle_region((3, 0), 1.5)
    sm.add_object("circle2", circle2)
    sm.set_style("circle2", {"color": "red", "linewidth": 1})

    circle3 = factory.create_circle_region((-3, 2), 1.0)
    sm.add_object("circle3", circle3)
    sm.set_style("circle3", {"color": "green", "linewidth": 1})

    return sm


# ---------------------------------------------------------------------------
# Benchmark tests (require pytest-benchmark)
# ---------------------------------------------------------------------------

try:
    import pytest_benchmark

    has_benchmark = True
except ImportError:
    has_benchmark = False


@pytest.mark.skipif(not has_benchmark, reason="pytest-benchmark is not installed")
class TestCurvePathPerformance:
    """Benchmark key graphics operations using pytest-benchmark."""

    def test_single_circle_curve_paths(self, benchmark):
        """Benchmark get_curve_paths for a single circle."""
        sm = _build_single_circle_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(
            backend.get_curve_paths, bounds=(-5, 5, -5, 5), resolution=200
        )
        assert result is not None

    def test_three_object_scene_curve_paths(self, benchmark):
        """Benchmark get_curve_paths for a three-object scene."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(
            backend.get_curve_paths, bounds=(-10, 10, -10, 10), resolution=200
        )
        assert result is not None

    def test_high_resolution_curve_paths(self, benchmark):
        """Benchmark get_curve_paths at high resolution (500)."""
        sm = _build_single_circle_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(
            backend.get_curve_paths, bounds=(-5, 5, -5, 5), resolution=500
        )
        assert result is not None

    def test_field_data_extraction(self, benchmark):
        """Benchmark get_field_data at 50×50 resolution."""
        sm = _build_single_circle_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(
            backend.get_field_data, bounds=(-5, 5, -5, 5), resolution=(50, 50)
        )
        assert result is not None

    def test_region_data_extraction(self, benchmark):
        """Benchmark get_region_data at 50×50 resolution."""
        sm = _build_single_circle_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(
            backend.get_region_data, bounds=(-5, 5, -5, 5), resolution=(50, 50)
        )
        assert result is not None

    def test_scene_bounds_calculation(self, benchmark):
        """Benchmark get_scene_bounds computation."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(backend.get_scene_bounds, padding=0.2)
        assert result is not None
        assert len(result) == 4

    def test_geometry_scene_data(self, benchmark):
        """Benchmark full get_geometry_scene_data at resolution=100."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)
        result = benchmark(backend.get_geometry_scene_data, resolution=100)
        assert result is not None


# ---------------------------------------------------------------------------
# Hard time-gate tests (always run, no pytest-benchmark required)
# ---------------------------------------------------------------------------


class TestPerformanceGates:
    """Hard time-limit tests that fail if an operation is too slow.

    These act as a safety net even when pytest-benchmark is not installed.
    """

    def test_curve_paths_under_5_seconds(self):
        """get_curve_paths for a 3-object scene must complete in <5 s."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)

        start = time.perf_counter()
        result = backend.get_curve_paths(bounds=(-10, 10, -10, 10), resolution=200)
        elapsed = time.perf_counter() - start

        # Validate result is non-empty
        assert result is not None, "get_curve_paths returned None"
        assert isinstance(result, dict), "get_curve_paths should return a dict"
        assert len(result) > 0, "get_curve_paths returned an empty dict"

        # Enforce time limit
        assert elapsed < 5.0, f"get_curve_paths took {elapsed:.2f}s, limit is 5.0s"

    def test_field_data_under_10_seconds(self):
        """get_field_data at 100×100 must complete in <10 s."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)

        start = time.perf_counter()
        result = backend.get_field_data(
            bounds=(-10, 10, -10, 10), resolution=(100, 100)
        )
        elapsed = time.perf_counter() - start

        # Validate result is non-empty
        assert result is not None, "get_field_data returned None"
        assert isinstance(result, dict), "get_field_data should return a dict"

        # Enforce time limit
        assert elapsed < 10.0, f"get_field_data took {elapsed:.2f}s, limit is 10.0s"

    def test_scene_bounds_under_2_seconds(self):
        """get_scene_bounds must complete in <2 s."""
        sm = _build_three_object_scene()
        backend = GraphicsBackendInterface(sm)

        start = time.perf_counter()
        result = backend.get_scene_bounds(padding=0.2)
        elapsed = time.perf_counter() - start

        # Validate result
        assert result is not None, "get_scene_bounds returned None"
        assert len(result) == 4, "get_scene_bounds should return a 4-tuple"
        xmin, xmax, ymin, ymax = result
        assert xmin < xmax, "xmin should be less than xmax"
        assert ymin < ymax, "ymin should be less than ymax"

        # Enforce time limit
        assert elapsed < 2.0, f"get_scene_bounds took {elapsed:.2f}s, limit is 2.0s"
