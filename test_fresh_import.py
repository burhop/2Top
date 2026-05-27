#!/usr/bin/env python3
"""
Test fresh import of CompositeCurve to check if continuity validation is working
"""

import sys
import os

# Clear any existing imports
modules_to_remove = [
    k for k in sys.modules.keys() if "geometry" in k or "composite" in k
]
for module in modules_to_remove:
    del sys.modules[module]

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Now import fresh
from geometry.composite_curve import CompositeCurve
from geometry.trimmed_implicit_curve import TrimmedImplicitCurve
from geometry.polynomial_curve import PolynomialCurve
import sympy as sp
import inspect

print("🔄 FRESH IMPORT TEST")
print("=" * 40)

# Check the signature
print("CompositeCurve.__init__ signature:")
print(f"  {inspect.signature(CompositeCurve.__init__)}")

# Test creating discontinuous segments
print("\n🧪 Testing discontinuous segments...")

x, y = sp.symbols("x y")

try:
    # Segment 1: Line from (0, 0) to (1, 0)
    seg1_line = PolynomialCurve(y, (x, y))
    seg1_mask = lambda x_val, y_val: (0 <= x_val <= 1) and (-0.1 <= y_val <= 0.1)
    seg1 = TrimmedImplicitCurve(seg1_line, seg1_mask, endpoints=[(0, 0), (1, 0)])

    # Segment 2: Line from (2, 1) to (3, 1) - BIG GAP!
    seg2_line = PolynomialCurve(y - 1, (x, y))
    seg2_mask = lambda x_val, y_val: (2 <= x_val <= 3) and (0.9 <= y_val <= 1.1)
    seg2 = TrimmedImplicitCurve(seg2_line, seg2_mask, endpoints=[(2, 1), (3, 1)])

    # Try to create composite - should fail if validation is working
    composite = CompositeCurve([seg1, seg2])
    print("  ❌ ERROR: Discontinuous curve was created! Validation not working.")

except ValueError as e:
    print(f"  ✅ SUCCESS: Validation working - {e}")
except TypeError as e:
    print(f"  ❓ Signature issue: {e}")
except Exception as e:
    print(f"  ❓ Unexpected error: {e}")

print("\n📋 Module info:")
print(f"  CompositeCurve module: {CompositeCurve.__module__}")
print(f"  File location: {inspect.getfile(CompositeCurve)}")
