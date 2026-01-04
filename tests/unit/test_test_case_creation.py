"""
Unit tests for test case creation functionality
"""

import sys
import os
import unittest
from datetime import datetime

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.utils.test_case_manager import TestCaseManager
from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.utils.result_storage_manager import ResultStorageManager


class TestTestCaseCreation(unittest.TestCase):
    """Test the test case creation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage_manager = ResultStorageManager()
        self.test_case_manager = TestCaseManager(self.storage_manager)

    def test_create_test_case_success(self):
        """Test creating a test case successfully"""
        # Create a module first
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Create a test case
        test_case = self.test_case_manager.create_test_case(
            name="Test Case 1",
            description="A simple test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param1": "value1"},
            expected_result="expected_result"
        )

        # Verify the test case was created correctly
        self.assertIsNotNone(test_case)
        self.assertEqual(test_case.name, "Test Case 1")
        self.assertEqual(test_case.description, "A simple test case")
        self.assertEqual(test_case.module_id, module.id)
        self.assertEqual(test_case.test_type, "unit")
        self.assertEqual(test_case.input_data, {"param1": "value1"})
        self.assertEqual(test_case.expected_result, "expected_result")
        self.assertEqual(test_case.status, "pending")
        self.assertTrue(test_case.valid)
        self.assertIsNone(test_case.validation_reason)

    def test_create_test_case_with_validation(self):
        """Test creating a test case with validation"""
        # Create a module first
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Create an invalid test case
        test_case = self.test_case_manager.create_test_case(
            name="Invalid Test Case",
            description="An invalid test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param1": "value1"},
            expected_result="expected_result",
            valid=False,
            validation_reason="Invalid test case due to missing parameters"
        )

        # Verify the test case was created correctly
        self.assertIsNotNone(test_case)
        self.assertFalse(test_case.valid)
        self.assertEqual(test_case.validation_reason, "Invalid test case due to missing parameters")

    def test_get_test_case(self):
        """Test retrieving a test case by ID"""
        # Create a module first
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Create a test case
        test_case = self.test_case_manager.create_test_case(
            name="Test Case 1",
            description="A simple test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param1": "value1"},
            expected_result="expected_result"
        )

        # Retrieve the test case
        retrieved_case = self.test_case_manager.get_test_case(test_case.id)
        self.assertIsNotNone(retrieved_case)
        self.assertEqual(retrieved_case.id, test_case.id)
        self.assertEqual(retrieved_case.name, "Test Case 1")

    def test_get_test_cases_by_module(self):
        """Test retrieving test cases by module"""
        # Create a module
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Create multiple test cases for the same module
        test_case1 = self.test_case_manager.create_test_case(
            name="Test Case 1",
            description="First test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param1": "value1"},
            expected_result="expected_result1"
        )

        test_case2 = self.test_case_manager.create_test_case(
            name="Test Case 2",
            description="Second test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param2": "value2"},
            expected_result="expected_result2"
        )

        # Create a test case for a different module
        module2 = self.test_case_manager.create_module(
            name="Another Module",
            description="Another test module",
            path="/path/to/another/module"
        )
        
        test_case3 = self.test_case_manager.create_test_case(
            name="Test Case 3",
            description="Third test case",
            module_id=module2.id,
            test_type="unit",
            input_data={"param3": "value3"},
            expected_result="expected_result3"
        )

        # Get test cases for the first module
        module_test_cases = self.test_case_manager.get_test_cases_by_module(module.id)
        self.assertEqual(len(module_test_cases), 2)
        self.assertIn(test_case1, module_test_cases)
        self.assertIn(test_case2, module_test_cases)
        self.assertNotIn(test_case3, module_test_cases)

        # Get test cases for the second module
        module2_test_cases = self.test_case_manager.get_test_cases_by_module(module2.id)
        self.assertEqual(len(module2_test_cases), 1)
        self.assertIn(test_case3, module2_test_cases)


if __name__ == "__main__":
    unittest.main()