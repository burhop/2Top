#!/usr/bin/env python3
"""
Script to add the _validate_continuity method to CompositeCurve
"""

# Read the current file
with open('geometry/composite_curve.py', 'r') as f:
    lines = f.readlines()

print("🔧 ADDING _validate_continuity METHOD")
print("=" * 50)

# Find the line with super().__init__
insert_line = -1
for i, line in enumerate(lines):
    if 'super().__init__(composite_expr, variables)' in line:
        insert_line = i + 1  # Insert after this line
        break

if insert_line == -1:
    print("❌ Could not find super().__init__ line")
    exit(1)

print(f"✅ Found super().__init__ at line {insert_line}")

# The method to insert
method_lines = [
    "    \n",
    "    def _validate_continuity(self, segments: List[TrimmedImplicitCurve], tolerance: float):\n",
    "        \"\"\"\n",
    "        Validate that segments form a continuous path.\n",
    "        \n",
    "        Args:\n",
    "            segments: List of segments to validate\n",
    "            tolerance: Maximum allowed gap between consecutive segments\n",
    "            \n",
    "        Raises:\n",
    "            ValueError: If segments are not continuous\n",
    "        \"\"\"\n",
    "        for i in range(len(segments) - 1):\n",
    "            current_seg = segments[i]\n",
    "            next_seg = segments[i + 1]\n",
    "            \n",
    "            # Get endpoints\n",
    "            current_endpoints = current_seg.get_endpoints()\n",
    "            next_endpoints = next_seg.get_endpoints()\n",
    "            \n",
    "            if not current_endpoints or not next_endpoints:\n",
    "                raise ValueError(f\"Segment {i} or {i+1} missing endpoint information for continuity validation\")\n",
    "            \n",
    "            # Find minimum gap between end of current segment and start of next segment\n",
    "            min_gap = float('inf')\n",
    "            for curr_end in current_endpoints:\n",
    "                for next_start in next_endpoints:\n",
    "                    gap = np.sqrt((curr_end[0] - next_start[0])**2 + (curr_end[1] - next_start[1])**2)\n",
    "                    min_gap = min(min_gap, gap)\n",
    "            \n",
    "            if min_gap > tolerance:\n",
    "                raise ValueError(f\"Gap of {min_gap:.6f} between segments {i} and {i+1} exceeds tolerance {tolerance}. \"\n",
    "                               f\"CompositeCurve requires continuous segments.\")\n",
]

# Insert the method
new_lines = lines[:insert_line] + method_lines + lines[insert_line:]

# Write the updated file
with open('geometry/composite_curve.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Method added successfully!")

# Verify
with open('geometry/composite_curve.py', 'r') as f:
    content = f.read()
    
if 'def _validate_continuity' in content:
    print("✅ Verification: Method found in file")
else:
    print("❌ Verification: Method not found in file")