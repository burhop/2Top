#!/usr/bin/env python3
"""
Systematic test fixing script to identify and analyze remaining failures
"""

import subprocess
import sys
import re

def run_all_tests():
    """Run all tests and capture results"""
    print("Running all tests to get current status...")
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/', 
        '--tb=line', '-v', '--disable-warnings'
    ], capture_output=True, text=True, cwd='.')
    
    return result

def extract_failed_tests(output):
    """Extract failed test names from pytest output"""
    failed_tests = []
    lines = output.split('\n')
    
    for line in lines:
        if 'FAILED' in line and '::' in line:
            # Extract test name
            match = re.search(r'(tests/[^:]+::[^:]+::[^\s]+)', line)
            if match:
                failed_tests.append(match.group(1))
    
    return failed_tests

def run_specific_test(test_name):
    """Run a specific test and return detailed output"""
    result = subprocess.run([
        sys.executable, '-m', 'pytest', test_name, 
        '-v', '-s', '--tb=short'
    ], capture_output=True, text=True, cwd='.')
    
    return result

def main():
    # Get current test status
    result = run_all_tests()
    
    # Extract summary info
    lines = result.stdout.split('\n')
    summary_line = None
    for line in lines:
        if 'failed' in line.lower() and ('passed' in line.lower() or 'error' in line.lower()):
            summary_line = line.strip()
            break
    
    print(f"Current test status: {summary_line}")
    
    # Extract failed tests
    failed_tests = extract_failed_tests(result.stdout)
    
    print(f"\nFound {len(failed_tests)} failing tests:")
    for i, test in enumerate(failed_tests, 1):
        print(f"{i:2d}. {test}")
    
    # Write results to files
    with open('current_test_status.txt', 'w') as f:
        f.write(f"Test Status: {summary_line}\n\n")
        f.write("Failed Tests:\n")
        for test in failed_tests:
            f.write(f"  {test}\n")
        f.write(f"\nFull Output:\n{result.stdout}")
    
    # Analyze first few failures in detail
    if failed_tests:
        print(f"\nAnalyzing first 3 failures in detail...")
        with open('detailed_failures.txt', 'w') as f:
            f.write("DETAILED FAILURE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            for i, test in enumerate(failed_tests[:3], 1):
                print(f"  Analyzing: {test}")
                test_result = run_specific_test(test)
                
                f.write(f"FAILURE {i}: {test}\n")
                f.write("-" * 50 + "\n")
                f.write(test_result.stdout)
                f.write("\n" + "=" * 50 + "\n\n")
    
    print(f"\nFiles created:")
    print(f"  - current_test_status.txt (summary)")
    print(f"  - detailed_failures.txt (first 3 failures)")
    
    return failed_tests

if __name__ == "__main__":
    main()
