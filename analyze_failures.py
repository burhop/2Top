#!/usr/bin/env python3
"""
Script to analyze test failures and extract detailed information
"""

import subprocess
import sys
import re

def run_tests_and_capture():
    """Run pytest and capture all output"""
    print("Running pytest to capture all test results...")
    
    # Run pytest with detailed output
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/', 
        '--tb=short', '-v', '--no-header'
    ], capture_output=True, text=True, cwd='.')
    
    return result

def extract_failures(output):
    """Extract failing test names from pytest output"""
    failures = []
    lines = output.split('\n')
    
    for line in lines:
        if 'FAILED' in line and '::' in line:
            # Extract test name from lines like:
            # tests/test_file.py::TestClass::test_method FAILED [XX%]
            test_match = re.search(r'(tests/[^:]+::[^:]+::[^\s]+)', line)
            if test_match:
                failures.append(test_match.group(1))
    
    return failures

def main():
    # Run tests
    result = run_tests_and_capture()
    
    # Write full output to file for reference
    with open('full_test_output.txt', 'w') as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)
        f.write(f"\n\nReturn code: {result.returncode}")
    
    # Extract failures
    failures = extract_failures(result.stdout)
    
    print(f"\nFound {len(failures)} failing tests:")
    for i, failure in enumerate(failures, 1):
        print(f"{i:2d}. {failure}")
    
    # Write failures to file
    with open('failing_tests.txt', 'w') as f:
        for failure in failures:
            f.write(f"{failure}\n")
    
    print(f"\nFull output written to: full_test_output.txt")
    print(f"Failing tests written to: failing_tests.txt")
    
    # Show summary from end of output
    lines = result.stdout.split('\n')
    summary_lines = [line for line in lines[-10:] if line.strip()]
    if summary_lines:
        print(f"\nTest summary:")
        for line in summary_lines:
            if 'failed' in line.lower() or 'passed' in line.lower():
                print(f"  {line}")

if __name__ == "__main__":
    main()
