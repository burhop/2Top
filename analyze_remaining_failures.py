#!/usr/bin/env python3
"""
Enhanced script to analyze remaining test failures and extract detailed information
"""

import subprocess
import sys
import re
import json

def run_tests_and_capture():
    """Run pytest and capture all output"""
    print("Running pytest to capture all test results...")
    
    # Run pytest with detailed output
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 'tests/', 
        '--tb=short', '-v', '--no-header'
    ], capture_output=True, text=True, cwd='.')
    
    return result

def extract_failures_and_errors(output):
    """Extract failing test names and error details from pytest output"""
    failures = []
    errors = []
    lines = output.split('\n')
    
    in_failure_section = False
    in_error_section = False
    current_test = None
    current_details = []
    
    for line in lines:
        # Check for FAILED tests
        if 'FAILED' in line and '::' in line:
            test_match = re.search(r'(tests/[^:]+::[^:]+::[^\s]+)', line)
            if test_match:
                failures.append({
                    'test_name': test_match.group(1),
                    'line': line.strip()
                })
        
        # Check for ERROR tests
        elif 'ERROR' in line and '::' in line:
            test_match = re.search(r'(tests/[^:]+::[^:]+::[^\s]+)', line)
            if test_match:
                errors.append({
                    'test_name': test_match.group(1),
                    'line': line.strip()
                })
        
        # Look for failure details sections
        elif line.startswith('=') and 'FAILURES' in line:
            in_failure_section = True
        elif line.startswith('=') and 'ERRORS' in line:
            in_error_section = True
        elif line.startswith('=') and ('short test summary' in line or 'failed' in line.lower()):
            in_failure_section = False
            in_error_section = False
    
    return failures, errors

def extract_summary_info(output):
    """Extract test summary information"""
    lines = output.split('\n')
    summary_line = None
    
    for line in lines:
        if 'failed' in line.lower() and 'passed' in line.lower():
            summary_line = line.strip()
            break
    
    return summary_line

def main():
    # Run tests
    result = run_tests_and_capture()
    
    # Write full output to file for reference
    with open('full_test_output_detailed.txt', 'w') as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)
        f.write(f"\n\nReturn code: {result.returncode}")
    
    # Extract failures and errors
    failures, errors = extract_failures_and_errors(result.stdout)
    summary = extract_summary_info(result.stdout)
    
    print(f"\n=== TEST ANALYSIS RESULTS ===")
    print(f"Summary: {summary}")
    print(f"\nFound {len(failures)} failing tests:")
    for i, failure in enumerate(failures, 1):
        print(f"{i:2d}. {failure['test_name']}")
    
    if errors:
        print(f"\nFound {len(errors)} error tests:")
        for i, error in enumerate(errors, 1):
            print(f"{i:2d}. {error['test_name']}")
    
    # Write structured data to files
    with open('failing_tests_detailed.json', 'w') as f:
        json.dump({
            'summary': summary,
            'failures': failures,
            'errors': errors,
            'total_failures': len(failures),
            'total_errors': len(errors)
        }, f, indent=2)
    
    # Write simple list for easy reference
    with open('failing_tests_list.txt', 'w') as f:
        f.write("FAILING TESTS:\n")
        for failure in failures:
            f.write(f"{failure['test_name']}\n")
        if errors:
            f.write("\nERROR TESTS:\n")
            for error in errors:
                f.write(f"{error['test_name']}\n")
    
    print(f"\nFiles created:")
    print(f"  - full_test_output_detailed.txt (complete output)")
    print(f"  - failing_tests_detailed.json (structured data)")
    print(f"  - failing_tests_list.txt (simple list)")
    
    # Return first few failures for immediate analysis
    if failures:
        print(f"\nFirst 5 failing tests for immediate analysis:")
        for i, failure in enumerate(failures[:5], 1):
            print(f"{i}. {failure['test_name']}")
    
    return failures[:5] if failures else []

if __name__ == "__main__":
    main()
