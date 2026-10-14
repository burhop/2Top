"""Warm occupancy costs and concrete mutable-cache/boundary before-after evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import types

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import AreaRegion, OccupancyField, create_square_from_edges
from geometry.base_field import BlendedField, CurveField
from geometry.implicit_curve import ImplicitCurve


def timing(function):
    function()
    samples = []
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(30):
            function()
        samples.append((time.perf_counter() - start) * 1000 / 30)
    return {"median_ms": statistics.median(samples), "samples_ms": samples}


def evidence(cls):
    x, y = sp.symbols("x y")
    field = cls(AreaRegion(create_square_from_edges((0, 0), (4, 4))))
    composite = BlendedField([field, CurveField(ImplicitCurve(y, (x, y)))])
    try:
        normal = list(composite.level_set(2.0).normal(0.0, 2.0))
    except ValueError:
        normal = "rejected"
    try:
        field.level_set(0.5)
        level = "returned discontinuous procedural curve"
    except ValueError as error:
        level = str(error)
    xx, yy = np.ones(5), np.full(5, 2.0)
    field.evaluate(xx, yy)
    xx[1] = -1.0
    values = field.evaluate(xx, yy).tolist()
    axis = np.linspace(-1.0, 5.0, 97)
    gx, gy = np.meshgrid(axis, axis)
    constant = cls(field.region, 2.0, 2.0)

    def uncached():
        field.clear_cache()
        return field.evaluate(gx, gy)

    return {
        "edge_normal": normal,
        "one_sided_values": [
            composite.evaluate(-1e-6, 2.0),
            composite.evaluate(1e-6, 2.0),
        ],
        "intermediate_level": level,
        "mutated_grid": values,
        "independent_grid_oracle": [1.0, 0.0, 1.0, 1.0, 1.0],
        "warm_repeated_grid": timing(lambda: field.evaluate(gx, gy)),
        "warm_fresh_grid": timing(lambda: field.evaluate(gx.copy(), gy.copy())),
        "warm_uncached_grid": timing(uncached),
        "warm_gradient": timing(lambda: field.gradient(gx, gy)),
        "equal_value_gradient": timing(lambda: constant.gradient(gx, gy)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "grid": [97, 97],
        "timing": "7 warm batches of 30 queries; compilation excluded; fresh-grid timing includes array copies",
        "current": evidence(OccupancyField),
    }
    if args.baseline_file:
        source = args.baseline_file.read_bytes()
        module = types.ModuleType("geometry._occupancy_baseline")
        module.__package__ = "geometry"
        exec(compile(source, str(args.baseline_file), "exec"), module.__dict__)
        result["baseline_commit"] = "1345e6bd7492ad9b1fe78b0832b7f56983855270"
        result["baseline_sha256"] = hashlib.sha256(source).hexdigest()
        result["previous"] = evidence(module.OccupancyField)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "current_ms": {
                    name: result["current"][name]["median_ms"]
                    for name in [
                        "warm_repeated_grid",
                        "warm_fresh_grid",
                        "warm_gradient",
                    ]
                },
                "edge_normal": result["current"]["edge_normal"],
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
