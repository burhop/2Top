"""Small residuals versus actual position in the reproduced x**8 contact case."""

import argparse
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sympy as sp

from geometry import ImplicitCurve, diagnose_intersection_candidates
from geometry.curve_intersections import find_curve_intersections


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("intersection-uncertainty-demo")
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    x, y = sp.symbols("x y")
    first, second = ImplicitCurve(y - x**8, (x, y)), ImplicitCurve(y, (x, y))
    points = find_curve_intersections(
        first, second, search_range=2, grid_resolution=50, tolerance=1e-8
    )
    report = diagnose_intersection_candidates(first, second, points)
    assert len(points) == 4 and all(
        not row["position_verified"] for row in report["candidate_reports"]
    )
    oracles = []
    with localcontext() as context:
        context.prec = 160
        for point in points:
            px, py = map(Decimal.from_float, point)
            oracles.append(
                dict(
                    point=point,
                    decimal_residuals=[str(py - px**8), str(py)],
                    decimal_distance_to_only_root=str((px * px + py * py).sqrt()),
                )
            )
    data = dict(
        analytic_isolated_roots=[(0.0, 0.0)],
        oracle="y=0 implies x**8=0;160digitDecimal evaluates exactbinaryfloatinput coordinates",
        candidate_report=report,
        independent_oracles=oracles,
        limits="The legacy residual-filtered candidates remain compatible. All diagnostic positions are unverified; the linearized displacement is not a root error/bound. No root is removed or newly certified.",
    )
    (args.output / "uncertainty.json").write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    labels = [f"Candidate {i + 1}" for i in range(len(points))]
    actual = [float(row["decimal_distance_to_only_root"]) for row in oracles]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].bar(labels, actual, color=["#85929e", "#b9770e", "#b9770e", "#b9770e"])
    axes[0].set(
        title="Independent distance to the only root",
        ylabel="Distance (coordinate units)",
    )
    magnitudes = [
        max(abs(float(v)) for v in row["decimal_residuals"]) for row in oracles
    ]
    axes[1].bar(labels, magnitudes, color="#245782")
    axes[1].axhline(
        1e-8, color="#ba4a3a", linestyle="--", label="Legacy residual tolerance"
    )
    axes[1].set_yscale("log")
    axes[1].set_ylim(1e-195, 1e-6)
    axes[1].set(
        title="Small residual does not bound position", ylabel="Maximum field residual"
    )
    axes[1].legend()
    for ax in axes:
        ax.tick_params(axis="x", labelrotation=20)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("All four diagnostic positions remain unverified")
    fig.tight_layout()
    fig.savefig(args.output / "uncertainty.png", dpi=140)
    plt.close(fig)
    print(
        json.dumps(
            dict(candidates=len(points), position_verified=0, actual_errors=actual)
        )
    )


if __name__ == "__main__":
    main()
