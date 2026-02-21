# Quickstart: Fix Conic Section Code

## Overview
This quickstart guide explains how to fix the conic section implementation in the 2Top 2D Implicit Geometry Library.

## Prerequisites
- Python 3.11+ installed
- Development environment with access to the 2Top repository
- pytest installed for running tests
- Basic understanding of conic sections in mathematics

## Getting Started

1. Clone the repository and navigate to the project directory
2. Run the existing conic section tests to identify failing cases:
   ```
   python -m pytest tests/unit/test_conic_section_comprehensive.py -v
   ```

3. Review the failing test cases to understand expected behavior
4. Examine the current implementation in `geometry/conic_section.py`
5. Apply fixes to align with test expectations
6. Run tests again to verify fixes

## Testing Process

1. Run all conic section tests:
   ```
   python -m pytest tests/unit/test_conic_section_comprehensive.py -v
   ```

2. Run all tests to ensure no regressions:
   ```
   python -m pytest tests/unit/ -v
   ```

## Common Issues to Address

- Incorrect conic type classification
- Improper coefficient extraction from expressions
- Wrong bounding box calculations
- Inaccurate point containment testing
- Broken evaluation methods

## Verification

After applying fixes:
1. All conic section tests should pass
2. No existing functionality should be broken
3. The implementation should match the mathematical definitions of conic sections