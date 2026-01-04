"""
Unit tests for module assignment functionality
"""

import sys
import os
import unittest

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.utils.test_case_manager import TestCaseManager
from tests.models.module import Module
from tests.utils.result_storage_manager import ResultStorageManager


class TestModuleAssignment(unittest.TestCase):
    """Test the module assignment functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage_manager = ResultStorageManager()
        self.test_case_manager = TestCaseManager(self.storage_manager)

    def test_create_module_success(self):
        """Test creating a module successfully"""
        # Create a module
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module",
            dependencies=["dependency1", "dependency2"]
        )

        # Verify the module was created correctly
        self.assertIsNotNone(module)
        self.assertEqual(module.name, "Test Module")
        self.assertEqual(module.description, "A test module")
        self.assertEqual(module.path, "/path/to/test/module")
        self.assertEqual(module.dependencies, ["dependency1", "dependency2"])

    def test_get_module(self):
        """Test retrieving a module by ID"""
        # Create a module
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Retrieve the module
        retrieved_module = self.test_case_manager.get_module(module.id)
        self.assertIsNotNone(retrieved_module)
        self.assertEqual(retrieved_module.id, module.id)
        self.assertEqual(retrieved_module.name, "Test Module")

    def test_get_all_modules(self):
        """Test retrieving all modules"""
        # Create multiple modules
        module1 = self.test_case_manager.create_module(
            name="Test Module 1",
            description="First test module",
            path="/path/to/test/module1"
        )

        module2 = self.test_case_manager.create_module(
            name="Test Module 2",
            description="Second test module",
            path="/path/to/test/module2"
        )

        # Get all modules
        all_modules = self.test_case_manager.get_all_modules()
        self.assertEqual(len(all_modules), 2)
        self.assertIn(module1, all_modules)
        self.assertIn(module2, all_modules)

    def test_module_dependencies(self):
        """Test module dependencies"""
        # Create a module with dependencies
        module = self.test_case_manager.create_module(
            name="Module with Dependencies",
            description="A module with dependencies",
            path="/path/to/module/with/dependencies",
            dependencies=["dep1", "dep2", "dep3"]
        )

        # Verify dependencies are stored correctly
        self.assertEqual(module.dependencies, ["dep1", "dep2", "dep3"])

    def test_module_test_case_association(self):
        """Test that modules properly associate with test cases"""
        # Create a module
        module = self.test_case_manager.create_module(
            name="Test Module",
            description="A test module",
            path="/path/to/test/module"
        )

        # Create a test case for this module
        test_case = self.test_case_manager.create_test_case(
            name="Test Case 1",
            description="A simple test case",
            module_id=module.id,
            test_type="unit",
            input_data={"param1": "value1"},
            expected_result="expected_result"
        )

        # Verify the test case was added to the module
        self.assertIn(test_case.id, module.test_case_ids)
        
        # Verify the module was added to the test case
        retrieved_case = self.test_case_manager.get_test_case(test_case.id)
        self.assertEqual(retrieved_case.module_id, module.id)


if __name__ == "__main__":
    unittest.main()