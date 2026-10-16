"""Write the exact-model x8 contact report as JSON; no server or scene changes."""

import json
from pathlib import Path
import sys

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import ImplicitCurve, find_polynomial_line_intersections

x, y = sp.symbols("x y")
report = find_polynomial_line_intersections(
    ImplicitCurve(y - x**8, (x, y)), ImplicitCurve(y, (x, y))
)
print(json.dumps(report, indent=2, allow_nan=False))
