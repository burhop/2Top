"""Analytic parabola contact, nearby two-root crossing and disjoint controls."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from geometry import ImplicitCurve
from geometry.curve_intersections import find_curve_intersections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("parabola-contact-demo"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    x, y = sp.symbols("x y")
    parabola = ImplicitCurve(y - x * x, (x, y))
    cases = []
    for name, height, expected in [
        ("tangent", sp.Integer(0), [(0.0, 0.0)]),
        (
            "two_crossings",
            sp.Rational(1, 1000),
            [(-np.sqrt(0.001), 0.001), (np.sqrt(0.001), 0.001)],
        ),
        ("disjoint", -sp.Rational(1, 1000), []),
    ]:
        line = ImplicitCurve(y - height, (x, y))
        points = sorted(
            find_curve_intersections(
                parabola, line, search_range=2.0, grid_resolution=64, tolerance=1e-8
            )
        )
        if len(points) != len(expected):
            raise RuntimeError(f"{name}: expected {len(expected)} points, got {points}")
        if expected:
            np.testing.assert_allclose(points, expected, atol=1e-7, rtol=0)
        cases.append(
            dict(
                case=name,
                points=points,
                analytic_reference=expected,
                maximum_coordinate_error=float(
                    np.max(np.abs(np.array(points) - expected))
                )
                if expected
                else None,
                residual_pairs=[
                    [parabola.evaluate(*point), line.evaluate(*point)]
                    for point in points
                ],
            )
        )
    data = dict(
        result_kind="approximate_numerical_intersections",
        cases=cases,
        benefit="Preserve one contact and two distinct nearby crossings while reducing per-evaluation overhead.",
        limits="Same solver starts, budgets and final residual checks. No general tangency, positional-accuracy or completeness guarantee.",
    )
    (args.output / "intersections.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    xx = np.linspace(-0.08, 0.08, 500)
    ax.plot(xx, xx * xx, color="#245782", label="Parabola y=x²")
    ax.axhline(0.0, color="#963c87", label="Tangent y=0")
    ax.axhline(0.001, color="#b9770e", label="Two crossings y=0.001")
    ax.axhline(-0.001, color="#ba4a3a", label="Disjoint y=-0.001")
    ax.scatter([0.0], [0.0], color="#963c87", s=70, zorder=5)
    ax.scatter(
        [-np.sqrt(0.001), np.sqrt(0.001)],
        [0.001, 0.001],
        color="#07834a",
        s=70,
        zorder=5,
    )
    ax.set(
        title="General numerical path: preserved contact and nearby roots",
        xlabel="x",
        ylabel="y",
        ylim=(-0.002, 0.007),
    )
    ax.grid(alpha=0.2)
    ax.legend(loc="upper center")
    fig.tight_layout()
    fig.savefig(args.output / "intersections.png", dpi=140)
    plt.close(fig)
    print(json.dumps(data))


if __name__ == "__main__":
    main()
