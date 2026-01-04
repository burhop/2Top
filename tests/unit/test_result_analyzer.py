"""
Unit tests for the test result analyzer
"""

import unittest
from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.models.test_result import TestResult
from tests.utils.test_result_analyzer import TestResultAnalyzer


class TestResultAnalyzer(unittest.TestCase):
    """
    Unit tests for the TestResultAnalyzer
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analyzer = TestResultAnalyzer()

    def test_analyze_test_result_passed(self):
        """Test analyzing a passed test result"""
        # Create a test result
        test_result = TestResult(
            id="result_001",
            test_case_id="test_001",
            module_id="module_001",
            status="passed",
            timestamp="2026-01-03T10:00:00Z",
            execution_time=0.012,
            error_details=None,
            output="Test output",
            diagnosis=None
        )
        
        # Analyze the result
        analysis = self.analyzer.analyze_test_result(test_result)
        
        # Check the analysis
        self.assertEqual(analysis["result_id"], "result_001")
        self.assertEqual(analysis["status"], "passed")
        self.assertEqual(analysis["execution_time"], 0.012)
        self.assertIsNone(analysis.get("module_name"))  # No module information in this case

    def test_analyze_test_result_failed(self):
        """Test analyzing a failed test result"""
        # Create a test result
        test_result = TestResult(
            id="result_002",
            test_case_id="test_002",
            module_id="module_001",
            status="failed",
            timestamp="2026-01-03T10:00:00Z",
            execution_time=0.015,
            error_details="AssertionError: 1 != 3",
            output="Test output",
            diagnosis="The function returned 1 instead of 3, indicating a bug in the implementation"
        )
        
        # Analyze the result
        analysis = self.analyzer.analyze_test_result(test_result)
        
        # Check the analysis
        self.assertEqual(analysis["result_id"], "result_002")
        self.assertEqual(analysis["status"], "failed")
        self.assertEqual(analysis["execution_time"], 0.015)
        self.assertEqual(analysis["error_details"], "AssertionError: 1 != 3")
        self.assertEqual(analysis["diagnosis"], "The function returned 1 instead of 3, indicating a bug in the implementation")

    def test_get_test_case_summary(self):
        """Test getting a test case summary"""
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
        
        # Get the summary
        summary = self.analyzer.get_test_case_summary(test_case)
        
        # Check the summary
        self.assertEqual(summary["id"], "test_001")
        self.assertEqual(summary["name"], "Test case 1")
        self.assertEqual(summary["test_type"], "unit")
        self.assertEqual(summary["valid"], True)

    def test_get_module_summary(self):
        """Test getting a module summary"""
        # Create a module
        module = Module(
            id="module_001",
            name="Test Module 1",
            description="A test module for integration",
            path="/path/to/test_module_1"
        )
        
        # Get the summary
        summary = self.analyzer.get_module_summary(module)
        
        # Check the summary
        self.assertEqual(summary["id"], "module_001")
        self.assertEqual(summary["name"], "Test Module 1")
        self.assertEqual(summary["path"], "/path/to/test_module_1")
        self.assertEqual(summary["test_case_count"], 0)  # No test cases added

    def tearDown(self):
        """Clean up after each test method."""
        pass


if __name__ == '__main__':
    unittest.main()