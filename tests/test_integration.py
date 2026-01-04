"""
Integration tests to verify the test case management system works correctly
"""

import unittest
from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.models.test_result import TestResult
from tests.utils.test_case_failure_detector import TestCaseFailureDetector
from tests.utils.module_identifier import ModuleIdentifier
from tests.utils.result_storage_manager import ResultStorageManager
from tests.utils.test_result_analyzer import TestResultAnalyzer
from tests.utils.error_message_generator import ErrorMessageGenerator
from tests.utils.test_case_manager import TestCaseManager
from tests.utils.test_case_executor import TestCaseExecutor


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the test case management system
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.failure_detector = TestCaseFailureDetector()
        self.module_identifier = ModuleIdentifier()
        self.storage_manager = ResultStorageManager("./test_results_integration")
        self.analyzer = TestResultAnalyzer()
        self.error_generator = ErrorMessageGenerator()

    def test_full_workflow(self):
        """Test the full workflow of test case management system"""
        # Create a test case
        test_case = TestCase(
            id="test_001",
            name="Test case 1",
            description="A simple test case",
            module_id="module_001",
            test_type="unit",
            input_data={"param1": 1, "param2": 2},
            expected_result=3
        )
        
        # Create a module
        module = Module(
            id="module_001",
            name="Test Module 1",
            description="A test module for integration",
            path="/path/to/test_module_1"
        )
        
        # Add the module to the identifier
        self.module_identifier.add_module(module)
        
        # Create a test result
        test_result = TestResult(
            id="result_001",
            test_case_id="test_001",
            module_id="module_001",
            status="failed",
            timestamp="2026-01-03T10:00:00Z",
            execution_time=0.012,
            error_details="AssertionError: 1 != 3",
            output="Test output",
            diagnosis="The function returned 1 instead of 3, indicating a bug in the implementation"
        )
        
        # Test failure detection
        failure_details = self.failure_detector.detect_failure(test_result)
        self.assertIsNotNone(failure_details)
        self.assertEqual(failure_details["test_result_id"], "result_001")
        
        # Test module identification
        identified_module = self.failure_detector.get_module_for_failure(test_result)
        self.assertIsNotNone(identified_module)
        self.assertEqual(identified_module.id, "module_001")
        
        # Test result analysis
        analysis = self.analyzer.analyze_test_result(test_result)
        self.assertIn("result_id", analysis)
        self.assertEqual(analysis["result_id"], "result_001")
        self.assertIn("status", analysis)
        self.assertEqual(analysis["status"], "failed")
        
        # Test error message generation
        error_message = self.error_generator.generate_error_message(test_result)
        self.assertIn("Test 'result_001' in module 'Test Module 1' failed", error_message)
        self.assertIn("Error details: AssertionError: 1 != 3", error_message)
        
        # Test detailed error message
        detailed_error = self.error_generator.generate_detailed_error_message(test_result)
        self.assertIn("Test Failure Report", detailed_error)
        self.assertIn("Test Case ID: result_001", detailed_error)
        self.assertIn("Module: Test Module 1", detailed_error)
        
        # Test storage
        success = self.storage_manager.store_test_result(test_result)
        self.assertTrue(success)
        
        # Test loading
        loaded_result = self.storage_manager.load_test_result("result_001")
        self.assertIsNotNone(loaded_result)
        self.assertEqual(loaded_result.id, "result_001")
        self.assertEqual(loaded_result.status, "failed")
        
        # Test error message storage
        error_message_obj = self.error_generator.generate_detailed_error_message(test_result)
        self.assertIsInstance(error_message_obj, str)
        
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test results directory
        import shutil
        import os
        if os.path.exists("./test_results_integration"):
            shutil.rmtree("./test_results_integration")


if __name__ == '__main__':
    unittest.main()