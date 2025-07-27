#!/usr/bin/env python3
"""
Simple script to check current test status and identify remaining failures
"""

import subprocess
import sys

def check_test_status():
    """Check current test status"""
    print("Checking current test status...")
    
    # Run all tests with brief output
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/', 
        '--tb=no', '-q'
    ], capture_output=True, text=True, cwd='.')
    
    print("Test Results:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

def check_specific_tests():
    """Check specific tests that were previously failing"""
    tests = [
        'tests/test_area_region.py::TestAreaRegionConstructor::test_constructor_validates_outer_boundary_closed',
        'tests/test_area_region.py::TestAreaRegionConstructor::test_constructor_validates_holes_closed',
        'tests/test_base_field.py::TestBlendedField::test_init_insufficient_fields'
    ]
    
    print("\nChecking specific previously failing tests:")
    for test in tests:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', test, '-v'
        ], capture_output=True, text=True, cwd='.')
        
        status = "PASSED" if result.returncode == 0 else "FAILED"
        test_name = test.split("::")[-1]
        print(f"  {status}: {test_name}")

if __name__ == "__main__":
    all_passed = check_test_status()
    check_specific_tests()
    
    if all_passed:
        print("\n✅ All tests are now passing!")
    else:
        print("\n❌ Some tests are still failing.")
