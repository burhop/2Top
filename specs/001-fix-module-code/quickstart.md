# Quickstart: Test Case Management System

## Overview
This quickstart guide shows how to set up and use the test case management system for the 2Top 2D Implicit Geometry Library. The system enforces the correct test-driven development process, where module code is fixed when test cases fail, not the test cases themselves.

## Prerequisites
- Python 3.11+ installed
- The 2Top project is installed and working
- pytest is available in the environment

## Setup
1. Install the project requirements if not already done:
   ```
   pip install -r requirements.txt
   ```

2. The test case system is part of the standard test structure, so no additional setup is required

## Basic Usage

### Running All Tests
To run all tests in the system:
```
pytest tests/
```

### Running Tests for a Specific Module
To run tests for a specific module (e.g., the "geometry" module):
```
pytest tests/ -k "geometry"
```

### Running Tests with Verbose Output
To get more detailed information about test execution:
```
pytest tests/ -v
```

## Test-Driven Development Process

### The "Red-Green-Refactor" Cycle
1. **Red**: Write a new test that fails (red) - this is the first step in TDD
2. **Green**: Write the minimum code to make the test pass (green) 
3. **Refactor**: Improve the code while keeping the test passing

Example of a TDD cycle:
```python
# Step 1: Red - Write a test that will fail
def test_conic_section_creation():
    # This test will fail initially
    x, y = sp.symbols('x y')
    circle = ConicSection(x**2 + y**2 - 1, (x, y))
    assert circle is not None

# Step 2: Green - Implement the code to make the test pass
# (The ConicSection class is already implemented in the system)

# Step 3: Refactor - Clean up the code if needed, but keep the test passing
```

## Identifying and Fixing Failing Tests

### When a Test Fails
1. When a test fails, the system will show a clear error message
2. The error message will include the test name, module, and specific failure details
3. The system will also show the module that is responsible for the test failure

### Fixing the Code
1. Use the error message to identify the specific problem
2. Modify the module code to address the root cause
3. Run the test again to confirm the fix

Example of fixing a failing test:
```python
# If a test fails, the error message will show:
# "test_conic_section_evaluate: Failed for input (0,0) - expected <0, got >0"

# The fix would be in the ConicSection class to correct the evaluation logic
# and then re-run the test
```

## Preventing Test Case Workarounds

The system enforces that:
1. Test cases are not modified to work around code issues
2. If a test case is actually correct, the code should be fixed
3. All test cases are validated to represent expected behavior

## Viewing Test Results
1. Test results are displayed in the console when running pytest
2. Detailed test results are available in the test result files
3. The system provides clear pass/fail status for each test
4. Error information is provided for failed tests, including suggested fixes

## Next Steps
1. Follow the TDD process: write a test, see it fail, write code, see it pass, refactor
2. When tests fail, always fix the module code, not the test case
3. Use the error messages to guide the code fixes
4. Validate that all test cases are valid and represent expected behavior