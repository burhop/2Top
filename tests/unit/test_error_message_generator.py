"""
Unit tests for the error message generator
"""

import unittest
from tests.models.test_result import TestResult
from tests.utils.error_message_generator import ErrorMessageGenerator


class TestErrorMessageGenerator(unittest.TestCase):
    """
    Unit tests for the ErrorMessageGenerator
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.error_generator = ErrorMessageGenerator()

    def test_generate_error_message_passed(self):
        """Test generating an error message for a passed test"""
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
        
        # Generate the error message
        error_message = self.error_generator.generate_error_message(test_result)
        
        # Check the error message
        self.assertEqual(error_message, "Test passed - no error to report")

    def test_generate_error_message_failed(self):
        """Test generating an error message for a failed test"""
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

        # Generate the error message
        error_message = self.error_generator.generate_error_message(test_result)

        # Check the error message
        self.assertIn("Test 'test_002' in module 'Module module_001' failed", error_message)
        self.assertIn("Error details: AssertionError: 1 != 3", error_message)
        self.assertIn("Suggested actions:", error_message)

    def test_generate_detailed_error_message(self):
        """Test generating a detailed error message"""
        # Create a test result
        test_result = TestResult(
            id="result_003",
            test_case_id="test_003",
            module_id="module_001",
            status="failed",
            timestamp="2026-01-03T10:00:00Z",
            execution_time=0.015,
            error_details="AssertionError: 1 != 3",
            output="Test output",
            diagnosis="The function returned 1 instead of 3, indicating a bug in the implementation"
        )

        # Generate the detailed error message
        detailed_error = self.error_generator.generate_detailed_error_message(test_result)

        # Check the detailed error message
        self.assertIn("Test Failure Report", detailed_error)
        self.assertIn("Test Case ID: test_003", detailed_error)  # Note: it's the test case id, not result id
        self.assertIn("Error type: AssertionError: 1 != 3", detailed_error)
        self.assertIn("Root cause analysis: The function returned 1 instead of 3, indicating a bug in the implementation", detailed_error)
        self.assertIn("Recommended actions:", detailed_error)

    def tearDown(self):
        """Clean up after each test method."""
        pass


if __name__ == '__main__':
    unittest.main()