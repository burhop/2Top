"""
Test to verify the utility classes are working correctly
"""

import sys
import os
import unittest
from datetime import datetime

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.utils.test_case_failure_detector import TestCaseFailureDetector
from tests.utils.module_identifier import ModuleIdentifier
from tests.models.test_case import TestCase
from tests.models.test_result import TestResult
from tests.models.module import Module


class TestUtilities(unittest.TestCase):
    """Test the utility classes for the 2Top test system"""
    
    def test_test_case_failure_detector(self):
        """Test the test case failure detector"""
        detector = TestCaseFailureDetector()
        
        # Test with a passing result
        passing_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.01
        )
        
        # Should return None for a passing result
        self.assertIsNone(detector.detect_failure(passing_result))
        
        # Test with a failing result
        failing_result = TestResult(
            id="result-002",
            test_case_id="test-002",
            module_id="module-002",
            status="failed",
            timestamp=datetime.now(),
            execution_time=0.02,
            error_details="Test failed with unexpected result",
            diagnosis="Input value was out of expected range"
        )
        
        # Should detect the failure
        failure_details = detector.detect_failure(failing_result)
        self.assertIsNotNone(failure_details)
        self.assertEqual(failure_details["test_result_id"], "result-002")
        self.assertEqual(failure_details["test_case_id"], "test-002")
        self.assertEqual(failure_details["module_id"], "module-002")
        self.assertEqual(failure_details["error_details"], "Test failed with unexpected result")
        self.assertEqual(failure_details["diagnosis"], "Input value was out of expected range")
        
        # Test error message generation
        error_msg = detector.generate_error_message(failing_result)
        self.assertIn("Test 'test-002' failed in module 'module-002'", error_msg)
        self.assertIn("Error: Test failed with unexpected result", error_msg)
        self.assertIn("Execution time: 0.020s", error_msg)
        self.assertIn("Diagnosis: Input value was out of expected range", error_msg)
    
    def test_module_identifier(self):
        """Test the module identifier"""
        identifier = ModuleIdentifier()
        
        # Test with a test case
        test_case = TestCase(
            id="test-001",
            name="Test Case 1",
            description="A simple test case",
            module_id="module-001",
            test_type="unit",
            input_data={"x": 1, "y": 2},
            expected_result=3
        )
        
        # Get module for test case
        module = identifier.get_module_by_test_case(test_case)
        self.assertIsNotNone(module)
        self.assertEqual(module.id, "module-001")
        self.assertEqual(module.name, "Module module-001")
        self.assertEqual(module.path, "/path/to/module-001")
        
        # Add a module to the identifier
        new_module = Module(
            id="module-002",
            name="Test Module 2",
            description="Another test module",
            path="/path/to/module-002"
        )
        identifier.add_module(new_module)
        
        # Get the added module
        retrieved_module = identifier.get_module_by_id("module-002")
        self.assertIsNotNone(retrieved_module)
        self.assertEqual(retrieved_module.id, "module-002")
        self.assertEqual(retrieved_module.name, "Test Module 2")
        self.assertEqual(retrieved_module.path, "/path/to/module-002")
        
        # Get all modules
        all_modules = identifier.get_all_modules()
        self.assertEqual(len(all_modules), 1)  # Only the one we added
        self.assertEqual(all_modules[0].id, "module-002")


if __name__ == "__main__":
    unittest.main()