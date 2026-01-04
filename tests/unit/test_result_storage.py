"""
Unit tests for test result storage functionality
"""

import sys
import os
import unittest
import tempfile
import shutil
from datetime import datetime

# Add the current directory to the path to import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.utils.result_storage_manager import ResultStorageManager
from tests.models.test_result import TestResult
from tests.models.test_case import TestCase
from tests.utils.test_case_manager import TestCaseManager
from tests.utils.test_case_executor import TestCaseExecutor


class TestResultStorage(unittest.TestCase):
    """Test the test result storage functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_manager = ResultStorageManager(self.temp_dir)
        self.test_case_manager = TestCaseManager(self.storage_manager)
        self.test_case_executor = TestCaseExecutor(self.test_case_manager, self.storage_manager)

    def tearDown(self):
        """Tear down test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_store_test_result_success(self):
        """Test storing a test result successfully"""
        # Create a test result
        test_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.01,
            output="test output"
        )

        # Store the test result
        success = self.storage_manager.store_test_result(test_result)
        self.assertTrue(success)

        # Verify the file was created
        import os
        filename = f"{test_result.id}.json"
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))

    def test_load_test_result_success(self):
        """Test loading a test result successfully"""
        # Create a test result
        test_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.01,
            output="test output"
        )

        # Store the test result
        self.storage_manager.store_test_result(test_result)

        # Load the test result
        loaded_result = self.storage_manager.load_test_result("result-001")
        self.assertIsNotNone(loaded_result)
        self.assertEqual(loaded_result.id, "result-001")
        self.assertEqual(loaded_result.test_case_id, "test-001")
        self.assertEqual(loaded_result.module_id, "module-001")
        self.assertEqual(loaded_result.status, "passed")
        self.assertEqual(loaded_result.output, "test output")

    def test_load_nonexistent_test_result(self):
        """Test loading a non-existent test result"""
        # Try to load a non-existent test result
        loaded_result = self.storage_manager.load_test_result("nonexistent")
        self.assertIsNone(loaded_result)

    def test_get_all_test_results(self):
        """Test getting all test results"""
        # Create test results
        test_result1 = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="failed",
            timestamp=datetime.now(),
            execution_time=0.01
        )

        test_result2 = TestResult(
            id="result-002",
            test_case_id="test-002",
            module_id="module-002",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.02
        )

        # Store the test results
        self.storage_manager.store_test_result(test_result1)
        self.storage_manager.store_test_result(test_result2)

        # Get all test results
        all_results = self.storage_manager.get_all_test_results()
        self.assertEqual(len(all_results), 2)
        result_ids = [r.id for r in all_results]
        self.assertIn("result-001", result_ids)
        self.assertIn("result-002", result_ids)

    def test_get_test_results_by_module(self):
        """Test getting test results by module"""
        # Create test results
        test_result1 = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="failed",
            timestamp=datetime.now(),
            execution_time=0.01
        )

        test_result2 = TestResult(
            id="result-002",
            test_case_id="test-002",
            module_id="module-002",
            status="passed",
            timestamp=datetime.now(),
            execution_time=0.02
        )

        # Store the test results
        self.storage_manager.store_test_result(test_result1)
        self.storage_manager.store_test_result(test_result2)

        # Get test results for module-001
        module_results = self.storage_manager.get_test_results_by_module("module-001")
        self.assertEqual(len(module_results), 1)
        self.assertEqual(module_results[0].id, "result-001")

        # Get test results for module-002
        module_results = self.storage_manager.get_test_results_by_module("module-002")
        self.assertEqual(len(module_results), 1)
        self.assertEqual(module_results[0].id, "result-002")

    def test_store_error_message(self):
        """Test storing an error message"""
        # Create an error message
        from tests.models.error_message import ErrorMessage
        
        error_message = ErrorMessage(
            id="error-001",
            test_result_id="result-001",
            message="Test error message",
            severity="error"
        )

        # Store the error message
        success = self.storage_manager.store_error_message(error_message)
        self.assertTrue(success)

        # Verify the file was created
        import os
        filename = f"{error_message.id}.json"
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))


if __name__ == "__main__":
    unittest.main()