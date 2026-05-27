"""
Error message generation system for the 2Top test system
"""

import uuid
from typing import Optional
from tests.models.error_message import ErrorMessage
from tests.models.test_result import TestResult
from tests.utils.result_storage_manager import ResultStorageManager


class ErrorMessageGenerator:
    """
    Generates error messages for the 2Top test system
    """

    def __init__(self, storage_manager: ResultStorageManager = None):
        self.storage_manager = storage_manager or ResultStorageManager()

    def generate_error_message(self, test_result: TestResult) -> str:
        """
        Generate a human-readable error message string for a test result.

        Args:
            test_result: The TestResult to generate a message for

        Returns:
            A formatted error message string
        """
        if test_result.status != "failed":
            return "Test passed - no error to report"

        module_name = f"Module {test_result.module_id}"
        msg = f"Test '{test_result.test_case_id}' in module '{module_name}' failed\n"
        msg += f"Error details: {test_result.error_details or 'Unknown error'}\n"
        msg += "Suggested actions:\n"
        msg += "  - Review the error details above\n"
        msg += "  - Check the test case implementation\n"
        if test_result.diagnosis:
            msg += f"  - Diagnosis: {test_result.diagnosis}\n"
        return msg

    def generate_detailed_error_message(self, test_result: TestResult) -> str:
        """
        Generate a detailed error report string for a test result.

        Args:
            test_result: The TestResult to generate a report for

        Returns:
            A detailed formatted error report string
        """
        lines = ["Test Failure Report", "=" * 40]
        lines.append(f"Test Case ID: {test_result.test_case_id}")
        lines.append(f"Module: Module {test_result.module_id}")
        lines.append(f"Status: {test_result.status}")
        lines.append(f"Execution time: {test_result.execution_time:.3f}s")
        if test_result.error_details:
            lines.append(f"Error type: {test_result.error_details}")
        if test_result.diagnosis:
            lines.append(f"Root cause analysis: {test_result.diagnosis}")
        lines.append("Recommended actions:")
        lines.append("  - Review the error details above")
        lines.append("  - Check the test case implementation")
        return "\n".join(lines)

    def generate_error_for_test_result(
        self,
        test_result: TestResult,
        error_type: str,
        error_details: str,
        suggested_fix: Optional[str] = None,
    ) -> ErrorMessage:
        """
        Generate an error message for a test result

        Args:
            test_result: The test result to generate an error for
            error_type: Type of error
            error_details: Details about the error
            suggested_fix: Suggested fix for the error

        Returns:
            The created error message
        """
        message = f"[{error_type}] {error_details}"
        error_message = ErrorMessage(
            id=f"em_{uuid.uuid4().hex[:12]}",
            test_result_id=test_result.id,
            message=message,
            severity="error",
            suggested_fix=suggested_fix,
        )
        self.storage_manager.store_error_message(error_message)
        return error_message

    def get_error_messages_by_test_result(self, test_result_id: str) -> list:
        """
        Get all error messages for a specific test result

        Args:
            test_result_id: The ID of the test result

        Returns:
            List of error messages for the test result
        """
        # In a real system, this would be more complex, but for now
        # we're just returning a list of all error messages
        # (this is a simplification)
        return []  # Placeholder

    def get_error_messages_by_severity(self, severity: str) -> list:
        """
        Get all error messages of a specific severity

        Args:
            severity: The severity level to filter by

        Returns:
            List of error messages with the specified severity
        """
        # In a real system, this would be more complex, but for now
        # we're just returning an empty list
        # (this is a simplification)
        return []  # Placeholder
