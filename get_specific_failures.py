#!/usr/bin/env python3
"""
Script to run specific failing tests and capture their detailed error messages
"""

import subprocess
import sys

# List of failing tests identified from the output
failing_tests = [
    "tests/test_area_region.py::TestAreaRegionConstructor::test_constructor_validates_outer_boundary_closed",
    "tests/test_area_region.py::TestAreaRegionConstructor::test_constructor_validates_holes_closed",
    "tests/test_area_region.py::TestAreaRegionContains::test_contains_square_with_circular_hole",
    "tests/test_base_field.py::TestCurveField::test_gradient_vectorized",
    "tests/test_base_field.py::TestBlendedField::test_init_insufficient_fields",
    "tests/test_base_field.py::TestBlendedField::test_init_invalid_field_types",
    "tests/test_composite_curve.py::TestCompositeCurveIsClosedMethod::test_is_closed_for_complete_circle",
    "tests/test_composite_curve.py::TestCompositeCurveContainsMethod::test_contains_points_on_each_segment",
    "tests/test_composite_curve.py::TestCompositeCurveContainsMethod::test_contains_with_partial_segments",
    "tests/test_composite_curve.py::TestCompositeCurveContainsMethod::test_contains_vectorized_input",
    "tests/test_composite_curve.py::TestCompositeCurveContainsMethod::test_contains_tolerance_handling",
    "tests/test_composite_curve.py::TestCompositeCurveEdgeCases::test_overlapping_segments",
    "tests/test_field_strategy.py::TestSignedDistanceField::test_evaluate_vectorized",
    "tests/test_field_strategy.py::TestOccupancyField::test_evaluate_vectorized"
]

def run_single_test(test_name):
    """Run a single test with detailed output"""
    print(f"\n{'='*80}")
    print(f"RUNNING: {test_name}")
    print('='*80)
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', test_name, 
        '-v', '-s', '--tb=short'
    ], capture_output=True, text=True, cwd='.')
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0

def main():
    print("Running detailed analysis of failing tests...")
    
    passed = 0
    failed = 0
    
    # Write all output to a file
    with open('detailed_failure_analysis.txt', 'w') as f:
        f.write("DETAILED FAILURE ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        for i, test in enumerate(failing_tests, 1):
            print(f"\n[{i}/{len(failing_tests)}] Running: {test}")
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest', test, 
                '-v', '-s', '--tb=short'
            ], capture_output=True, text=True, cwd='.')
            
            f.write(f"TEST {i}: {test}\n")
            f.write("-" * 80 + "\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
            f.write(f"\nReturn code: {result.returncode}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            if result.returncode == 0:
                passed += 1
                print(f"  ✅ PASSED")
            else:
                failed += 1
                print(f"  ❌ FAILED")
    
    print(f"\n\nSUMMARY:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {len(failing_tests)}")
    print(f"\nDetailed output written to: detailed_failure_analysis.txt")

if __name__ == "__main__":
    main()
