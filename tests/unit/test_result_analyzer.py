"""
Unit tests for the test result analyzer
"""

import unittest
from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.models.test_result import TestResult
from tests.utils.test_result_analyzer import TestResultAnalyzer
from tests.utils.result_storage_manager import ResultStorageManager
from tests.utils.test_case_manager import TestCaseManager


class TestResultAnalyzer(unittest.TestCase):
    """
    Unit tests for the TestResultAnalyzer
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.storage_manager = ResultStorageManager()
        self.case_manager = TestCaseManager(self.storage_manager)
        self.analyzer = TestResultAnalyzer(self.case_manager, self.storage_manager)

    def test_get_test_results_summary(self):
        """Test getting test results summary"""
        # Test with no results
        summary = self.analyzer.get_test_results_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["pass_rate"], 0.0)

    def test_get_module_test_summary(self):
        """Test getting module test summary"""
        # Create a module
        module = Module(
            id="module_001",
            name="Test Module 1",
            description="A test module for integration",
            path="/path/to/test_module_1"
        )

        # Get the summary (will be empty since no results)
        summary = self.analyzer.get_module_test_summary(module.id)
        self.assertEqual(summary["module_id"], "module_001")
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["pass_rate"], 0.0)

    def test_get_detailed_test_results(self):
        """Test getting detailed test results"""
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

        # Get detailed results (will be empty since no results)
        detailed = self.analyzer.get_detailed_test_results(test_case.id)
        self.assertIn("error", detailed)  # Should return error since test case doesn't exist

    def tearDown(self):
        """Clean up after each test method."""
        pass


if __name__ == '__main__':
    unittest.main()