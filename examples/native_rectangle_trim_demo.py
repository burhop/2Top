"""Exact native trim proof for an irrational fourth-order contact; JSON only."""

import json
from pathlib import Path
import sys
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import ImplicitCurve, RectangleMask, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections

x, y = sp.symbols("x y")
field = TrimmedImplicitCurve(
    ImplicitCurve((x * x - 2) ** 4, (x, y)), RectangleMask(0, 2, -1, 1)
)
report = find_polynomial_line_intersections(field, ImplicitCurve(y, (x, y)))
assert len(report["points"]) == 1
assert report["roots"][1]["multiplicity"] == 4
assert report["roots"][1]["root_trim_membership"] == "model_root_included"
print(json.dumps(report, indent=2, allow_nan=False))
