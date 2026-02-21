"""
Utility to detect when test cases fail and identify the responsible module
"""

from datetime import datetime
from typing import Optional, Dict, Any
from tests.models.test_case import TestCase
from tests.models.test_result import TestResult
from tests.models.module import Module


class TestCaseFailureDetector:
    """
    Utility to detect test case failures and identify the responsible module
    """
    
    def __init__(self):
        self.failure_log = []  # Log of failures for analysis
    
    def detect_failure(self, test_result: TestResult) -> Optional[Dict[str, Any]]:
        """
        Detect if a test result represents a failure and return details
        
        Args:
            test_result: The test result to analyze
            
        Returns:
            Dictionary with failure details if a failure is detected, None otherwise
        """
        if test_result.status != "failed":
            return None
        
        # Create failure details
        failure_details = {
            "test_result_id": test_result.id,
            "test_case_id": test_result.test_case_id,
            "module_id": test_result.module_id,
            "timestamp": test_result.timestamp,
            "error_details": test_result.error_details,
            "diagnosis": test_result.diagnosis
        }
        
        # Add to failure log
        self.failure_log.append(failure_details)
        
        return failure_details
    
    def get_module_for_failure(self, test_result: TestResult) -> Optional[Module]:
        """
        Get the module that is responsible for a test failure
        
        Args:
            test_result: The test result to analyze
            
        Returns:
            The module that is responsible for the test failure, or None if not found
        """
        # In a real system, this would look up the module in a database or registry
        # For this implementation, we'll return a basic module for demonstration
        if test_result.status == "failed":
            return Module(
                id=test_result.module_id,
                name=f"Module {test_result.module_id}",
                description="Module that had a test failure",
                path=f"/path/to/{test_result.module_id}"
            )
        return None
    
    def generate_error_message(self, test_result: TestResult) -> str:
        """
        Generate a clear error message for a test failure
        
        Args:
            test_result: The test result to generate an error message for
            
        Returns:
            A clear, informative error message
        """
        if test_result.status != "failed":
            return "Test passed - no error to report"
        
        error_msg = f"Test '{test_result.test_case_id}' failed in module '{test_result.module_id}'\n"
        error_msg += f"Error: {test_result.error_details or 'Unknown error'}\n"
        error_msg += f"Execution time: {test_result.execution_time:.3f}s\n"
        error_msg += f"Timestamp: {test_result.timestamp}\n"
        
        if test_result.diagnosis:
            error_msg += f"Diagnosis: {test_result.diagnosis}\n"
        
        return error_msg