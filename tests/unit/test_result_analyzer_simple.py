"""
Unit tests for the test result analyzer - Simplified version
"""

import unittest
from tests.utils.test_result_analyzer import TestResultAnalyzer
from tests.utils.result_storage_manager import ResultStorageManager


class TestResultAnalyzer(unittest.TestCase):
    """
    Unit tests for the TestResultAnalyzer
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.storage_manager = ResultStorageManager()
        # Create analyzer with minimal dependencies
        self.analyzer = TestResultAnalyzer()

    def test_analyzer_initialization(self):
        """Test that the analyzer can be initialized"""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'get_test_results_summary'))
        self.assertTrue(hasattr(self.analyzer, 'get_module_test_summary'))

    def test_get_test_results_summary_empty(self):
        """Test getting test results summary with no data"""
        # Test with no results
        summary = self.analyzer.get_test_results_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["pass_rate"], 0.0)

    def tearDown(self):
        """Clean up after each test method."""
        pass


if __name__ == '__main__':
    unittest.main()