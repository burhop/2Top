"""
Test to verify the data models are working correctly
"""

import sys
import os
import unittest
from datetime import datetime

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.models.test_result import TestResult
from tests.models.error_message import ErrorMessage


class TestDataModels(unittest.TestCase):
    """Test the data models for the 2Top test system"""
    
    def test_test_case_model(self):
        """Test the test case data model"""
        test_case = TestCase(
            id="test-001",
            name="Test Case 1",
            description="A simple test case",
            module_id="module-001",
            test_type="unit",
            input_data={"x": 1, "y": 2},
            expected_result=3
        )
        
        self.assertEqual(test_case.id, "test-001")
        self.assertEqual(test_case.name, "Test Case 1")
        self.assertEqual(test_case.description, "A simple test case")
        self.assertEqual(test_case.module_id, "module-001")
        self.assertEqual(test_case.test_type, "unit")
        self.assertEqual(test_case.input_data, {"x": 1, "y": 2})
        self.assertEqual(test_case.expected_result, 3)
        self.assertEqual(test_case.status, "pending")
        self.assertTrue(test_case.valid)
        
        # Test to_dict and from_dict
        data = test_case.to_dict()
        restored = TestCase.from_dict(data)
        self.assertEqual(restored.id, "test-001")
        self.assertEqual(restored.name, "Test Case 1")
    
    def test_module_model(self):
        """Test the module data model"""
        module = Module(
            id="module-001",
            name="Test Module",
            description="A test module",
            path="/path/to/module"
        )
        
        self.assertEqual(module.id, "module-001")
        self.assertEqual(module.name, "Test Module")
        self.assertEqual(module.description, "A test module")
        self.assertEqual(module.path, "/path/to/module")
        self.assertEqual(module.dependencies, [])
        self.assertEqual(module.test_case_ids, [])
        
        # Test to_dict and from_dict
        data = module.to_dict()
        restored = Module.from_dict(data)
        self.assertEqual(restored.id, "module-001")
        self.assertEqual(restored.name, "Test Module")
    
    def test_test_result_model(self):
        """Test the test result data model"""
        test_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.01
        )
        
        self.assertEqual(test_result.id, "result-001")
        self.assertEqual(test_result.test_case_id, "test-001")
        self.assertEqual(test_result.module_id, "module-001")
        self.assertEqual(test_result.status, "passed")
        self.assertEqual(test_result.execution_time, 0.01)
        
        # Test to_dict and from_dict
        data = test_result.to_dict()
        restored = TestResult.from_dict(data)
        self.assertEqual(restored.id, "result-001")
        self.assertEqual(restored.test_case_id, "test-001")
    
    def test_error_message_model(self):
        """Test the error message data model"""
        error_message = ErrorMessage(
            id="error-001",
            test_result_id="result-001",
            message="Test error message",
            severity="error"
        )
        
        self.assertEqual(error_message.id, "error-001")
        self.assertEqual(error_message.test_result_id, "result-001")
        self.assertEqual(error_message.message, "Test error message")
        self.assertEqual(error_message.severity, "error")
        self.assertIsNone(error_message.suggested_fix)
        
        # Test to_dict and from_dict
        data = error_message.to_dict()
        restored = ErrorMessage.from_dict(data)
        self.assertEqual(restored.id, "error-001")
        self.assertEqual(restored.test_result_id, "result-001")


if __name__ == "__main__":
    unittest.main()