#!/usr/bin/env python3
"""
Script to fix CompositeCurve by adding continuity validation
"""

import re

# Read the current file
with open('geometry/composite_curve.py', 'r') as f:
    content = f.read()

print("🔧 FIXING COMPOSITE CURVE")
print("=" * 40)

# Check current __init__ signature
init_match = re.search(r'def __init__\(self, segments: List\[TrimmedImplicitCurve\],\s*\n\s*variables: Tuple\[sp\.Symbol, sp\.Symbol\] = None\):', content)

if init_match:
    print("✅ Found current __init__ method signature")
    
    # Replace the signature
    old_signature = init_match.group(0)
    new_signature = """def __init__(self, segments: List[TrimmedImplicitCurve], 
                 variables: Tuple[sp.Symbol, sp.Symbol] = None,
                 validate_continuity: bool = True,
                 continuity_tolerance: float = 1e-6):"""
    
    content = content.replace(old_signature, new_signature)
    print("✅ Updated method signature")
    
    # Update the docstring
    old_docstring = '''        """
        Initialize CompositeCurve with ordered list of segments.
        
        Args:
            segments: List of TrimmedImplicitCurve objects in order
            variables: Tuple of (x, y) symbols, defaults to first segment's variables
        
        Raises:
            ValueError: If segments list is empty
            TypeError: If any segment is not a TrimmedImplicitCurve
        """'''
    
    new_docstring = '''        """
        Initialize CompositeCurve with ordered list of segments.
        
        Args:
            segments: List of TrimmedImplicitCurve objects in order
            variables: Tuple of (x, y) symbols, defaults to first segment's variables
            validate_continuity: If True, validate that segments form a continuous path
            continuity_tolerance: Maximum gap allowed between consecutive segments
            
        Raises:
            ValueError: If segments list is empty or continuity validation fails
            TypeError: If any segment is not a TrimmedImplicitCurve
        """'''
    
    content = content.replace(old_docstring, new_docstring)
    print("✅ Updated docstring")
    
    # Add continuity validation code after the type checking
    old_validation = '''        if not all(isinstance(seg, TrimmedImplicitCurve) for seg in segments):
            raise TypeError("All segments must be TrimmedImplicitCurve instances")
        
        # Store segments'''
    
    new_validation = '''        if not all(isinstance(seg, TrimmedImplicitCurve) for seg in segments):
            raise TypeError("All segments must be TrimmedImplicitCurve instances")
        
        # Validate continuity if requested
        if validate_continuity and len(segments) > 1:
            self._validate_continuity(segments, continuity_tolerance)
        
        # Store segments'''
    
    content = content.replace(old_validation, new_validation)
    print("✅ Added continuity validation code")
    
    # Add the _validate_continuity method if it doesn't exist
    if '_validate_continuity' not in content:
        # Find where to insert the method (after __init__)
        init_end = content.find('        super().__init__(composite_expr, variables)')
        if init_end != -1:
            # Find the end of the __init__ method
            method_end = content.find('\n    def ', init_end)
            if method_end != -1:
                validation_method = '''
    def _validate_continuity(self, segments: List[TrimmedImplicitCurve], tolerance: float):
        """
        Validate that segments form a continuous path.
        
        Args:
            segments: List of segments to validate
            tolerance: Maximum allowed gap between consecutive segments
            
        Raises:
            ValueError: If segments are not continuous
        """
        for i in range(len(segments) - 1):
            current_seg = segments[i]
            next_seg = segments[i + 1]
            
            # Get endpoints
            current_endpoints = current_seg.get_endpoints()
            next_endpoints = next_seg.get_endpoints()
            
            if not current_endpoints or not next_endpoints:
                raise ValueError(f"Segment {i} or {i+1} missing endpoint information for continuity validation")
            
            # Find minimum gap between end of current segment and start of next segment
            min_gap = float('inf')
            for curr_end in current_endpoints:
                for next_start in next_endpoints:
                    gap = np.sqrt((curr_end[0] - next_start[0])**2 + (curr_end[1] - next_start[1])**2)
                    min_gap = min(min_gap, gap)
            
            if min_gap > tolerance:
                raise ValueError(f"Gap of {min_gap:.6f} between segments {i} and {i+1} exceeds tolerance {tolerance}. "
                               f"CompositeCurve requires continuous segments.")
'''
                content = content[:method_end] + validation_method + content[method_end:]
                print("✅ Added _validate_continuity method")
    
    # Write the updated content
    with open('geometry/composite_curve.py', 'w') as f:
        f.write(content)
    
    print("✅ File updated successfully!")
    
else:
    print("❌ Could not find __init__ method signature to replace")

print("\n🧪 Testing the fix...")

# Test the fix
try:
    import sys
    # Clear any cached imports
    modules_to_remove = [k for k in sys.modules.keys() if 'geometry' in k or 'composite' in k]
    for module in modules_to_remove:
        del sys.modules[module]
    
    from geometry.composite_curve import CompositeCurve
    import inspect
    
    print(f"New signature: {inspect.signature(CompositeCurve.__init__)}")
    
except Exception as e:
    print(f"❌ Error testing fix: {e}")