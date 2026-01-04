"""
Test result analysis system for the 2Top test system
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from tests.models.test_result import TestResult
from tests.models.test_case import TestCase
from tests.utils.test_case_manager import TestCaseManager
from tests.utils.result_storage_manager import ResultStorageManager


class TestResultAnalyzer:
    """
    Analyzes test results in the 2Top test system
    """

    def __init__(self, 
                 test_case_manager: TestCaseManager = None,
                 storage_manager: ResultStorageManager = None):
        self.test_case_manager = test_case_manager or TestCaseManager()
        self.storage_manager = storage_manager or ResultStorageManager()

    def get_test_results_summary(self, test_case_ids: List[str] = None) -> Dict[str, Any]:
        """
        Get a summary of test results

        Args:
            test_case_ids: Optional list of test case IDs to analyze. If None, analyze all.

        Returns:
            Dictionary with test results summary
        """
        # Get all test results
        all_results = self.storage_manager.get_all_test_results()
        
        # If specific test case IDs are provided, filter results
        if test_case_ids:
            all_results = [r for r in all_results if r.test_case_id in test_case_ids]
        
        # Count results by status
        status_counts = Counter(r.status for r in all_results)
        
        # Get the total number of test results
        total_count = len(all_results)
        
        # Calculate pass rate
        pass_rate = 0.0
        if total_count > 0:
            pass_rate = (status_counts.get("passed", 0) / total_count) * 100
        
        return {
            "total": total_count,
            "passed": status_counts.get("passed", 0),
            "failed": status_counts.get("failed", 0),
            "pass_rate": pass_rate,
            "by_status": dict(status_counts)
        }

    def get_test_results_by_module(self, module_id: str) -> List[TestResult]:
        """
        Get all test results for a specific module

        Args:
            module_id: The ID of the module

        Returns:
            List of test results for the module
        """
        return self.storage_manager.get_test_results_by_module(module_id)

    def get_test_results_by_test_case(self, test_case_id: str) -> List[TestResult]:
        """
        Get all test results for a specific test case

        Args:
            test_case_id: The ID of the test case

        Returns:
            List of test results for the test case
        """
        # This is a bit tricky as the result doesn't store the test case id directly
        # but we can get it from the storage manager
        all_results = self.storage_manager.get_all_test_results()
        return [r for r in all_results if r.test_case_id == test_case_id]

    def get_test_case_history(self, test_case_id: str) -> List[TestResult]:
        """
        Get the history of a test case (all test results for this test case)

        Args:
            test_case_id: The ID of the test case

        Returns:
            List of test results for the test case, sorted by timestamp
        """
        results = self.get_test_results_by_test_case(test_case_id)
        return sorted(results, key=lambda r: r.timestamp)

    def get_module_test_summary(self, module_id: str) -> Dict[str, Any]:
        """
        Get a test summary for a specific module

        Args:
            module_id: The ID of the module

        Returns:
            Dictionary with test results summary for the module
        """
        # Get all test results for the module
        results = self.get_test_results_by_module(module_id)
        
        # Count results by status
        status_counts = Counter(r.status for r in results)
        
        # Get the total number of test results
        total_count = len(results)
        
        # Calculate pass rate
        pass_rate = 0.0
        if total_count > 0:
            pass_rate = (status_counts.get("passed", 0) / total_count) * 100
        
        return {
            "module_id": module_id,
            "total": total_count,
            "passed": status_counts.get("passed", 0),
            "failed": status_counts.get("failed", 0),
            "pass_rate": pass_rate,
            "by_status": dict(status_counts)
        }

    def get_test_case_status(self, test_case_id: str) -> str:
        """
        Get the current status of a test case (based on the most recent result)

        Args:
            test_case_id: The ID of the test case

        Returns:
            The status of the test case ("passed", "failed", "pending", or "unknown")
        """
        # Get the most recent result for the test case
        history = self.get_test_case_history(test_case_id)
        if not history:
            return "pending"
        
        # Return the status of the most recent result
        return history[-1].status

    def get_detailed_test_results(self, test_case_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a test case and its results

        Args:
            test_case_id: The ID of the test case

        Returns:
            Dictionary with detailed test case and result information
        """
        # Get the test case
        test_case = self.test_case_manager.get_test_case(test_case_id)
        if not test_case:
            return {"error": "Test case not found"}
        
        # Get the test case history
        history = self.get_test_case_history(test_case_id)
        
        # Get the most recent result
        most_recent = None
        if history:
            most_recent = history[-1]
        
        return {
            "test_case": test_case.to_dict(),
            "history": [r.to_dict() for r in history],
            "most_recent": most_recent.to_dict() if most_recent else None
        }