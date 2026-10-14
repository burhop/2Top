"""Measure complete SDF segment kernels, including deliberate precision fallbacks."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--label", default="current")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from geometry.field_strategy import SignedDistanceField

    def kernel(start, end, x, y):
        field = SignedDistanceField.__new__(SignedDistanceField)
        field._boundary_segments = lambda: [(start, end)]
        return field._compute_distance_to_boundary_vectorized(x, y)

    results = []
    cases = []
    for size in (97, 257):
        x, y = np.meshgrid(np.linspace(-1.0, 5.0, size), np.linspace(-1.0, 6.0, size))
        cases += [
            (f"axis_{size}", (0.0, 0.0), (4.0, 0.0), x, y),
            (f"oblique_{size}", (0.0, 0.0), (3.0, 4.0), x, y),
        ]
    cases += [
        (
            "overflow_fallback_64",
            (-1e308, -1e308),
            (1e308, 1e308),
            np.linspace(-1.0, 1.0, 64),
            np.ones(64),
        ),
        (
            "collinear_fallback_64",
            (0.0, 0.0),
            (7.0, 11.0),
            np.full(64, 3.5),
            np.full(64, 5.5),
        ),
        (
            "near_line_64",
            (0.0, 0.0),
            (7.0, 11.0),
            np.full(64, 3.5),
            5.5 + np.linspace(1e-13, 1e-8, 64),
        ),
    ]
    for label, start, end, x, y in cases:
        with np.errstate(all="ignore"):
            result = kernel(start, end, x, y)
            batches = []
            for _ in range(5):
                start_time = time.perf_counter_ns()
                for _ in range(3):
                    kernel(start, end, x, y)
                batches.append((time.perf_counter_ns() - start_time) / 3 / 1e6)
        results.append(
            {
                "workload": label,
                "shape": list(x.shape),
                "median_ms": statistics.median(batches),
                "batches_ms": batches,
                "nonfinite_results": int((~np.isfinite(result)).sum()),
            }
        )
    from geometry import AreaRegion, create_square_from_edges

    reproductions = []
    for size, point, expected in [
        (4e-6, (2e-6, 1e-6), -1e-6),
        (4.0, (1e200, 2.0), 1e200),
    ]:
        with np.errstate(all="ignore"):
            observed = SignedDistanceField(
                AreaRegion(create_square_from_edges((0.0, 0.0), (size, size)))
            ).evaluate(*point)
        reproductions.append(
            {
                "side": size,
                "point": point,
                "analytic": expected,
                "observed": observed if np.isfinite(observed) else str(observed),
            }
        )
    data = {
        "label": args.label,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "workloads": results,
        "reproductions": reproductions,
        "limits": "Warm full one-segment distance calls, five batches. Baseline may return invalid values. Fallback-heavy queries are deliberately pathological; sampled-curve accuracy and application FPS are not measured here.",
    }
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "label": args.label,
                "reproductions": reproductions,
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
