#!/usr/bin/env python3
"""
Test to verify the test system is set up correctly
"""

import sys
import os

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_test_system_setup():
    """Test that the test system is properly set up"""
    # This is a simple test to make sure the test system is working
    assert True, "Test system is working correctly"
    print("Test system is properly set up!")

if __name__ == "__main__":
    test_test_system_setup()
    print("All tests passed!")