"""Compare analytic compositions with the previous fixed-stencil gradient path."""

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry.base_field import BlendedField, CurveField
from geometry.implicit_curve import ImplicitCurve
from geometry.procedural_curve import ProceduralCurve

x, y = sp.symbols("x y")


def field(expression):
    return CurveField(ImplicitCurve(sp.sympify(expression), (x, y)))


def legacy_gradient(fields, operation, xx, yy):
    # Previous path computed these derivatives and discarded them.
    for child in fields:
        child.gradient(xx, yy)

    def evaluate(a, b):
        values = [child.evaluate(a, b) for child in fields]
        result = values[0]
        for value in values[1:]:
            if operation == "divide":
                result = result / value
            elif operation == "min":
                result = np.minimum(result, value)
            else:
                result = np.maximum(result, value)
        return result

    h = 1e-6
    return (
        (evaluate(xx + h, yy) - evaluate(xx - h, yy)) / (2 * h),
        (evaluate(xx, yy + h) - evaluate(xx, yy - h)) / (2 * h),
    )


def timing(function):
    function()
    samples = []
    for _ in range(7):
        start = time.perf_counter()
        for _ in range(30):
            function()
        samples.append((time.perf_counter() - start) * 1000 / 30)
    return {"median_ms": statistics.median(samples), "samples_ms": samples}


def counts(function, leaves):
    result = {"evaluate": 0, "gradient": 0}
    originals = []
    for child in leaves:
        originals.append((child, child.evaluate, child.gradient))

        def wrap(method, key):
            def call(*args):
                result[key] += 1
                return method(*args)

            return call

        child.evaluate = wrap(child.evaluate, "evaluate")
        child.gradient = wrap(child.gradient, "gradient")
    try:
        function()
    finally:
        for child, evaluate, gradient in originals:
            child.evaluate, child.gradient = evaluate, gradient
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    axis = np.linspace(-0.5, 0.5, 97)
    xx, yy = np.meshgrid(axis, axis)
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "grid": [97, 97],
        "timing": "7 warm batches of 30 queries; compilation excluded",
        "cases": {},
    }
    for operation in ["divide", "min", "max"]:
        leaves = [field(x * x + y + 3), field(y * y - x + 5)]
        blend = BlendedField(leaves, operation)

        def old():
            return legacy_gradient(leaves, operation, xx, yy)

        def new():
            return blend.gradient(xx, yy)

        baseline, current = timing(old), timing(new)
        report["cases"][operation] = {
            "previous": baseline,
            "current": current,
            "current_over_previous": current["median_ms"] / baseline["median_ms"],
            "previous_calls": counts(old, leaves),
            "current_calls": counts(new, leaves),
        }
    a, b = field(x + 2), field(y + 3)
    product = BlendedField([a, b], "multiply")
    dag = BlendedField([product, product, a], "add")
    report["shared_dag_calls"] = counts(lambda: dag.gradient(xx, yy), [a, b])
    blend = BlendedField([a, b], "add")
    previous = ProceduralCurve(blend.evaluate, (x, y))
    current = blend.level_set(0.0)
    report["level_set"] = {
        "previous": timing(lambda: previous.gradient(xx, yy)),
        "current": timing(lambda: current.gradient(xx, yy)),
        "previous_calls": counts(lambda: previous.gradient(xx, yy), [a, b]),
        "current_calls": counts(lambda: current.gradient(xx, yy), [a, b]),
    }
    translated = [field(x - sp.Integer(10) ** 12 + 2), field(y + 3)]
    report["translated_quotient"] = {
        "point": [1e12, 1.0],
        "independent_oracle": [0.25, -0.125],
        "previous": list(legacy_gradient(translated, "divide", 1e12, 1.0)),
        "current": list(BlendedField(translated, "divide").gradient(1e12, 1.0)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ratios": {
                    name: case["current_over_previous"]
                    for name, case in report["cases"].items()
                },
                "level_calls": report["level_set"]["current_calls"],
                "output": str(args.output),
            }
        )
    )


if __name__ == "__main__":
    main()
