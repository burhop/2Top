"""Property-based regression tests for geometry scenarios."""

from __future__ import annotations


import pytest

from geometry import PrecisionPolicy

from tests.factories.curve_scenarios import sample_scenarios


@pytest.mark.parametrize("seed", [101, 202, 303])
def test_scenario_closure_and_containment(seed: int):
    policy = PrecisionPolicy()
    scenarios = sample_scenarios(seed, max_scenarios=30, precision_policy=policy)
    for scenario in scenarios:
        if scenario.composite is None:
            continue
        composite = scenario.composite
        # Numeric invariant: closed composites should contain centroid
        if composite.is_closed():
            bbox = composite.bounding_box()
            cx = 0.5 * (bbox[0] + bbox[1])
            cy = 0.5 * (bbox[2] + bbox[3])
            assert composite.contains(cx, cy, region_containment=True)
        # All scenarios should mark boundary points as on-curve
        for curve in scenario.curves:
            endpoints = getattr(curve, "get_endpoints", lambda: [])()
            for point in endpoints:
                assert composite.contains(*point)
