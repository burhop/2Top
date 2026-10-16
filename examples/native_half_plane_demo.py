"""Native x+y>=0 proves the positive irrational contact; JSON, no scene edits."""

import json
from pathlib import Path
import sys
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry import HalfPlaneMask, ImplicitCurve, TrimmedImplicitCurve
from geometry import find_polynomial_line_intersections

x, y = sp.symbols("x y")
field = TrimmedImplicitCurve(
    ImplicitCurve((x * x - 2) ** 4, (x, y)), HalfPlaneMask(1, 1, 0)
)
report = find_polynomial_line_intersections(field, ImplicitCurve(y - x, (x, y)))
assert len(report["points"]) == 1 and report["points"][0][0] > 0
assert report["roots"][1]["root_trim_membership"] == "model_root_included"
print(json.dumps(report, indent=2, allow_nan=False))
