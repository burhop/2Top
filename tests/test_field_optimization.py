import numpy as np
import sympy as sp
from geometry import ConicSection, AreaRegion, CompositeCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.field_strategy import SignedDistanceField, OccupancyField


def test_trimmed_implicit_curve_approximation_no_mask_filter():
    x, y = sp.symbols("x y")
    # Simple circle (x^2 + y^2 - 4 = 0)
    circle = ConicSection(x**2 + y**2 - 4, (x, y))

    # Trimmed curve segment with endpoints at (2, 0) and (0, 2)
    # The mask checks if x >= 0 and y >= 0
    mask = lambda px, py: px >= -1e-9 and py >= -1e-9
    trimmed = TrimmedImplicitCurve(
        base_curve=circle,
        mask=mask,
        variables=(x, y),
        endpoints=[(2.0, 0.0), (0.0, 2.0)],
    )

    # Even if endpoints are exactly on the boundary, they should not be filtered out
    pts = trimmed.get_polyline_approximation(resolution=10)
    assert len(pts) == 10
    # Endpoints must be preserved exactly
    assert np.allclose(pts[0], (2.0, 0.0))
    assert np.allclose(pts[-1], (0.0, 2.0))


def test_field_grid_caching():
    x, y = sp.symbols("x y")
    circle = ConicSection(x**2 + y**2 - 4, (x, y))
    trimmed = TrimmedImplicitCurve(circle, lambda px, py: True)
    composite = CompositeCurve([trimmed])
    region = AreaRegion(composite)

    sdf = SignedDistanceField(region, resolution=0.1)
    occupancy = OccupancyField(region, 1.0, 0.0)

    # Generate grids
    grid_x, grid_y = np.meshgrid(np.linspace(-3, 3, 50), np.linspace(-3, 3, 50))

    # First evaluation (cache miss)
    res_sdf_1 = sdf.evaluate(grid_x, grid_y)
    res_occ_1 = occupancy.evaluate(grid_x, grid_y)

    assert sdf._cache is not None
    assert occupancy._cache is not None

    # Second evaluation (cache hit)
    # Verify reference equality works
    res_sdf_2 = sdf.evaluate(grid_x, grid_y)
    res_occ_2 = occupancy.evaluate(grid_x, grid_y)

    assert res_sdf_2 is res_sdf_1
    assert res_occ_2 is res_occ_1

    # Evaluate with new identical grid (numerical equality check)
    grid_x_new, grid_y_new = np.meshgrid(np.linspace(-3, 3, 50), np.linspace(-3, 3, 50))
    res_sdf_3 = sdf.evaluate(grid_x_new, grid_y_new)
    res_occ_3 = occupancy.evaluate(grid_x_new, grid_y_new)

    # Numerical identity matches should hit cache and return the cached object
    assert res_sdf_3 is res_sdf_1
    assert res_occ_3 is res_occ_1

    # Clear cache
    sdf.clear_cache()
    occupancy.clear_cache()

    assert sdf._cache is None
    assert occupancy._cache is None

    # Evaluate after clearing
    res_sdf_4 = sdf.evaluate(grid_x, grid_y)
    res_occ_4 = occupancy.evaluate(grid_x, grid_y)
    assert res_sdf_4 is not res_sdf_1
