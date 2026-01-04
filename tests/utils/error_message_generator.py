"""
Error message generation system for the 2Top test system
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from tests.models.error_message import ErrorMessage
from tests.models.test_result import TestResult
from tests.utils.result_storage_manager import ResultStorageManager


class ErrorMessageGenerator:
    """
    Generates error messages for the 2Top test system
    """

    def __init__(self, storage_manager: ResultStorageManager = None):
        self.storage_manager = storage_manager or ResultStorageManager()

    def generate_error_message(self,
                              test_result_id: str,
                              message: str,
                              severity: str = "error",
                              suggested_fix: Optional[str] = None) -> ErrorMessage:
        """
        Generate and store an error message

        Args:
            test_result_id: The ID of the test result this error is associated with
            message: The error message
            severity: Severity level (info, warning, error)
            suggested_fix: Suggested fix for the error

        Returns:
            The created error message
        """
        # Generate a unique ID for the error message
        error_id = f"em_{uuid.uuid4().hex[:12]}"

        # Create the error message
        error_message = ErrorMessage(
            id=error_id,
            test_result_id=test_result_id,
            message=message,
            severity=severity,
            suggested_fix=suggested_fix
        )

        # Store the error message
        self.storage_manager.store_error_message(error_message)

        return error_message

    def generate_error_for_test_result(self,
                                      test_result: TestResult,
                                      error_type: str,
                                      error_details: str,
                                      suggested_fix: Optional[str] = None) -> ErrorMessage:
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
        # Create a combined error message
        message = f"[{error_type}] {error_details}"
        
        return self.generate_error_message(
            test_result_id=test_result.id,
            message=message,
            severity="error",
            suggested_fix=suggested_fix
        )

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