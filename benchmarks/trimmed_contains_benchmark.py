import time
import os
import sys
import numpy as np
import sympy as sp

# Ensure local package imports work when running this script directly
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.implicit_curve import ImplicitCurve


def make_line_through_origin():
    x, y = sp.symbols('x y')
    # Line: y = 0
    expr = y
    return ImplicitCurve(expr, (x, y))


def rect_mask_factory(xmin, xmax, ymin, ymax):
    def mask(px, py):
        return (xmin <= px <= xmax) and (ymin <= py <= ymax)
    return mask


def run_benchmark(n_points: int = 200_000):
    rng = np.random.default_rng(123)
    xs = rng.uniform(-2.0, 2.0, size=n_points)
    ys = rng.uniform(-0.01, 0.01, size=n_points)  # near the line y=0 to hit on-curve more often

    base = make_line_through_origin()
    xmin, xmax, ymin, ymax = -1.0, 1.0, -0.5, 0.5
    mask = rect_mask_factory(xmin, xmax, ymin, ymax)

    # With explicit bounds (vectorized fast-path)
    trimmed_fast = TrimmedImplicitCurve(base, mask, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    # Without explicit bounds (forces per-point mask loop)
    trimmed_slow = TrimmedImplicitCurve(base, mask)

    # Warmup
    trimmed_fast.contains(xs[:1000], ys[:1000])
    trimmed_slow.contains(xs[:1000], ys[:1000])

    t0 = time.perf_counter()
    res_fast = trimmed_fast.contains(xs, ys)
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    res_slow = trimmed_slow.contains(xs, ys)
    t3 = time.perf_counter()

    # Sanity: they should be equal
    assert np.array_equal(res_fast, res_slow)

    print(f"Points: {n_points}")
    print(f"Fast-path (bounds) time: {t1 - t0:.4f} s")
    print(f"Fallback (per-point mask) time: {t3 - t2:.4f} s")
    print(f"Speedup: {(t3 - t2) / max(t1 - t0, 1e-12):.2f}x")


if __name__ == "__main__":
    run_benchmark()
