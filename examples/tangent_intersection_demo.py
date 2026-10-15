"""One circle contact, two nearby crossings, and a disjoint line."""

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

from geometry import ImplicitCurve, TrimmedImplicitCurve
from geometry.curve_intersections import find_curve_intersections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("tangent-intersection-demo")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    x, y = sp.symbols("x y")
    r = sp.Integer(1000)
    a = ImplicitCurve(x * x + y * y - r * r, (x, y))
    cases = [
        ("circle_line_tangent", ImplicitCurve(y - r, (x, y)), [(0.0, 1000.0)]),
        (
            "external_circle_tangent",
            ImplicitCurve((x - 2 * r) ** 2 + y * y - r * r, (x, y)),
            [(1000.0, 0.0)],
        ),
        (
            "near_crossing",
            ImplicitCurve(y - 999, (x, y)),
            [(-float(sp.sqrt(1999)), 999.0), (float(sp.sqrt(1999)), 999.0)],
        ),
        ("near_disjoint", ImplicitCurve(y - 1001, (x, y)), []),
        ("coincident", ImplicitCurve(-7 * (x * x + y * y - r * r), (x, y)), []),
        (
            "trim_endpoint",
            TrimmedImplicitCurve(
                ImplicitCurve(y - r, (x, y)),
                lambda x, y: 0 <= x <= 1,
                xmin=0.0,
                xmax=1.0,
                ymin=1000.0,
                ymax=1000.0,
                endpoints=[(0.0, 1000.0), (1.0, 1000.0)],
            ),
            [(0.0, 1000.0)],
        ),
    ]
    results = []
    for label, b, expected in cases:
        points = sorted(
            find_curve_intersections(
                a, b, search_range=3000.0, grid_resolution=64, tolerance=1e-8
            )
        )
        if len(points) != len(expected):
            raise RuntimeError(f"{label}: expected{len(expected)}, got{points}")
        if expected:
            np.testing.assert_allclose(points, expected, atol=1e-6, rtol=0)
        results.append(
            dict(
                case=label,
                points=points,
                analytic_reference=expected,
                interpretation="coincident circles have no isolated tangent roots"
                if label == "coincident"
                else "validated float intersection coordinates",
                maximum_coordinate_error=float(
                    np.max(np.abs(np.array(points) - expected))
                )
                if expected
                else None,
            )
        )
    data = dict(
        result_kind="float_coordinates_after_native_classification_or_numerical_refinement",
        cases=results,
        benefit="A single tangent contact can become one anchor; nearby two-root crossings remain distinct.",
        limits="Exact recognition is limited to eligible native rational/Float circle fields and lines. Returned coordinates are floats validated by residual and final masks. Nonzero discriminants retain the existing numerical path.",
    )
    (args.output / "intersections.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    theta = np.linspace(0.0, 2 * np.pi, 500)
    axes[0].plot(
        1000 * np.cos(theta),
        1000 * np.sin(theta),
        color="#245782",
        label="Circle radius 1,000",
    )
    axes[0].axhline(1000, color="#963c87", label="Tangent line")
    axes[0].scatter(
        [0.0], [1000.0], color="#07834a", s=70, zorder=5, label="One contact"
    )
    axes[0].annotate(
        "(0, 1000)", (0, 1000), xytext=(10, 10), textcoords="offset points"
    )
    axes[0].set(
        title="One isolated tangent contact", xlim=(-1200, 1200), ylim=(-1200, 1250)
    )
    axes[0].set_aspect("equal")
    xx = np.linspace(-90.0, 90.0, 500)
    axes[1].plot(
        xx, np.sqrt(1000**2 - xx**2), color="#245782", label="Circle near contact"
    )
    axes[1].axhline(999, color="#963c87", label="Crossing line y=999")
    axes[1].axhline(1001, color="#ba4a3a", label="Disjoint line y=1001")
    roots = [-float(sp.sqrt(1999)), float(sp.sqrt(1999))]
    axes[1].scatter(
        roots, [999.0, 999.0], color="#07834a", s=70, zorder=5, label="Two crossings"
    )
    axes[1].set(
        title="Nearby crossing and disjoint cases", xlim=(-90, 90), ylim=(996, 1002)
    )
    for ax in axes:
        ax.set(xlabel="x", ylabel="y")
        ax.grid(alpha=0.2)
        ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(args.output / "intersections.png", dpi=140)
    plt.close(fig)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
