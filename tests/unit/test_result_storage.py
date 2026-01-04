"""
Test to verify the result storage manager is working correctly
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
from tests.models.error_message import ErrorMessage


class TestResultStorageManager(unittest.TestCase):
    """Test the result storage manager for the 2Top test system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_manager = ResultStorageManager(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_store_and_load_test_result(self):
        """Test storing and loading a test result"""
        # Create a test result
        test_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="failed",
            timestamp=datetime.now(),
            execution_time=0.01,
            error_details="Test failed with unexpected result"
        )
        
        # Store the test result
        success = self.storage_manager.store_test_result(test_result)
        self.assertTrue(success)
        
        # Load the test result
        loaded_result = self.storage_manager.load_test_result("result-001")
        self.assertIsNotNone(loaded_result)
        self.assertEqual(loaded_result.id, "result-001")
        self.assertEqual(loaded_result.test_case_id, "test-001")
        self.assertEqual(loaded_result.module_id, "module-001")
        self.assertEqual(loaded_result.status, "failed")
        self.assertEqual(loaded_result.error_details, "Test failed with unexpected result")
    
    def test_store_and_load_error_message(self):
        """Test storing and loading an error message"""
        # Create an error message
        error_message = ErrorMessage(
            id="error-001",
            test_result_id="result-001",
            message="Test error message",
            severity="error"
        )
        
        # Store the error message
        success = self.storage_manager.store_error_message(error_message)
        self.assertTrue(success)
        
        # In a real system, we would also test loading, but the current implementation
        # doesn't have a direct method to load error messages, so we just test storage
    
    def test_get_all_test_results(self):
        """Test getting all test results"""
        # Create a test result
        test_result = TestResult(
            id="result-001",
            test_case_id="test-001",
            module_id="module-001",
            status="failed",
            timestamp=datetime.now(),
            execution_time=0.01
        )
        
        # Store the test result
        self.storage_manager.store_test_result(test_result)
        
        # Get all test results
        all_results = self.storage_manager.get_all_test_results()
        self.assertEqual(len(all_results), 1)
        self.assertEqual(all_results[0].id, "result-001")
    
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


if __name__ == "__main__":
    unittest.main()