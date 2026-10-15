"""Reusable segment/circle intersections; JSON coordinates and a standalone plot."""

import argparse
import json
from pathlib import Path
import sys

# Run from a checkout without relying on another editable installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from geometry import ImplicitCurve, TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("trimmed-intersection-demo")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    x, y = sp.symbols("x y")
    segment = TrimmedImplicitCurve(
        ImplicitCurve(y - sp.Rational(3, 4), (x, y)),
        lambda px, py: -1.5 <= px <= 1.5,
        xmin=-1.5,
        xmax=1.5,
        ymin=0.75,
        ymax=0.75,
        endpoints=[(-1.5, 0.75), (1.5, 0.75)],
    )
    circle = ImplicitCurve(x * x + y * y - sp.Rational(25, 16), (x, y))
    points = sorted(
        find_curve_intersections(
            segment, circle, search_range=2.0, grid_resolution=100, tolerance=1e-8
        )
    )
    references = [(-1.0, 0.75), (1.0, 0.75)]
    if len(points) != 2:
        raise RuntimeError(f"Expected two segment/circle crossings, got {points}")
    np.testing.assert_allclose(points, references, atol=1e-7, rtol=0)
    data = dict(
        operation="trimmed_segment_intersects_circle",
        result_kind="approximate_numerical_coordinates",
        points=points,
        analytic_reference=references,
        maximum_coordinate_error=float(np.max(np.abs(np.array(points) - references))),
        accepted_by_final_trim=[segment.contains(px, py, 1e-7) for px, py in points],
        grid_resolution=100,
        search_range=2.0,
        residual_tolerance=1e-8,
        benefit="Returned crossings can become cutting or anchor coordinates in reusable geometry workflows.",
        limits="Grid-seeded numerical search is not exact or complete. Arbitrary trim masks remain authoritative.",
    )
    (args.output / "intersections.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    theta = np.linspace(0.0, 2 * np.pi, 500)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(
        1.25 * np.cos(theta),
        1.25 * np.sin(theta),
        color="#245782",
        label="Circle radius 1.25",
    )
    ax.plot([-2.0, 2.0], [0.75, 0.75], "--", color="#aaaaaa", label="Untrimmed line")
    ax.plot([-1.5, 1.5], [0.75, 0.75], color="#963c87", lw=3, label="Bounded segment")
    ax.scatter([-1.5, 1.5], [0.75, 0.75], color="#963c87", marker="s", zorder=4)
    ax.scatter(
        *np.array(points).T,
        color="#07834a",
        s=80,
        zorder=5,
        label="Numerical intersections",
    )
    for px, py in points:
        ax.annotate(
            f"({px:.6g}, {py:.6g})",
            (px, py),
            xytext=(8, 12),
            textcoords="offset points",
        )
    ax.set(
        xlim=(-2.0, 2.0),
        ylim=(-1.6, 1.6),
        xlabel="x",
        ylabel="y",
        title="A thin trimmed segment recovers both circle crossings",
    )
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(args.output / "intersections.png", dpi=150)
    plt.close(fig)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
