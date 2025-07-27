#!/usr/bin/env python3
"""
Script to run a single test and capture its output
"""

import subprocess
import sys
import os

def run_single_test(test_name):
    """Run a single test and return the result"""
    print(f"Running test: {test_name}")
    
    # Run the specific test
    result = subprocess.run([
        sys.executable, '-m', 'pytest', test_name,
        '-v', '--tb=short', '--no-header'
    ], capture_output=True, text=True, cwd='.')
    
    print(f"Return code: {result.returncode}")
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result

if __name__ == "__main__":
    # Test a specific failing test
    test_name = "tests/test_area_region.py::TestAreaRegionConstructor::test_constructor_validates_outer_boundary_closed"
    run_single_test(test_name)
