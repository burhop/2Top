#!/usr/bin/env python3
"""
Fix tolerance issues in composite curve factory functions
"""

import re

def fix_tolerances_in_file(filename):
    """Fix tolerance issues in the geometry factories file"""
    print(f"🔧 Fixing tolerances in {filename}")
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Patterns to fix - these are too restrictive for plotting
    fixes = [
        # Fix narrow line tolerances like (-0.6 <= x <= -0.4) to be wider
        (r'(-?\d+\.?\d*) <= x_val <= (-?\d+\.?\d*)\) and \((-?\d+\.?\d*) <= y_val <= (-?\d+\.?\d*)', 
         lambda m: f'{float(m.group(1)) - 0.05:.2f} <= x_val <= {float(m.group(2)) + 0.05:.2f}) and ({float(m.group(3)) - 0.05:.2f} <= y_val <= {float(m.group(4)) + 0.05:.2f}'),
        
        # Fix patterns like (0.4 <= y_val <= 0.6) to be wider
        (r'(\d+\.?\d*) <= y_val <= (\d+\.?\d*)', 
         lambda m: f'{float(m.group(1)) - 0.05:.2f} <= y_val <= {float(m.group(2)) + 0.05:.2f}'),
        
        # Fix patterns like (-0.1 <= x_val <= 0.1) to be wider  
        (r'(-?\d+\.?\d*) <= x_val <= (\d+\.?\d*)', 
         lambda m: f'{float(m.group(1)) - 0.05:.2f} <= x_val <= {float(m.group(2)) + 0.05:.2f}'),
    ]
    
    original_content = content
    
    # Apply fixes
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if content != original_content:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Updated tolerances in {filename}")
        return True
    else:
        print(f"ℹ️ No tolerance changes needed in {filename}")
        return False

if __name__ == "__main__":
    fix_tolerances_in_file("geometry/factories.py")