"""
Test case management system for the 2Top test system
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from tests.models.test_case import TestCase
from tests.models.module import Module
from tests.utils.result_storage_manager import ResultStorageManager


class TestCaseManager:
    """
    Manages test cases in the 2Top test system
    """

    def __init__(self, storage_manager: ResultStorageManager = None):
        self.storage_manager = storage_manager or ResultStorageManager()
        self.test_cases: Dict[str, TestCase] = {}
        self.modules: Dict[str, Module] = {}

    def create_test_case(self,
                         name: str,
                         description: str,
                         module_id: str,
                         test_type: str,
                         input_data: Dict[str, Any],
                         expected_result: Any,
                         valid: bool = True,
                         validation_reason: Optional[str] = None) -> TestCase:
        """
        Create a new test case

        Args:
            name: Name of the test case
            description: Description of the test case
            module_id: ID of the module this test case belongs to
            test_type: Type of test (e.g., "unit", "integration", "regression")
            input_data: Data to be used in the test
            expected_result: Expected result of the test
            valid: Whether the test case is valid
            validation_reason: Reason if the test case is invalid

        Returns:
            The created test case
        """
        # Generate a unique ID for the test case
        test_case_id = f"tc_{uuid.uuid4().hex[:12]}"

        # Create the test case
        test_case = TestCase(
            id=test_case_id,
            name=name,
            description=description,
            module_id=module_id,
            test_type=test_type,
            input_data=input_data,
            expected_result=expected_result,
            valid=valid,
            validation_reason=validation_reason
        )

        # Store the test case
        self.test_cases[test_case_id] = test_case

        # Add the test case to the module
        if module_id in self.modules:
            self.modules[module_id].test_case_ids.append(test_case_id)

        return test_case

    def get_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """
        Get a test case by its ID

        Args:
            test_case_id: The ID of the test case to retrieve

        Returns:
            The test case, or None if not found
        """
        return self.test_cases.get(test_case_id)

    def get_test_cases_by_module(self, module_id: str) -> List[TestCase]:
        """
        Get all test cases for a specific module

        Args:
            module_id: The ID of the module

        Returns:
            List of test cases for the module
        """
        return [tc for tc in self.test_cases.values() if tc.module_id == module_id]

    def update_test_case(self, test_case_id: str, **kwargs) -> bool:
        """
        Update a test case

        Args:
            test_case_id: The ID of the test case to update
            **kwargs: Fields to update

        Returns:
            True if the update was successful, False otherwise
        """
        if test_case_id not in self.test_cases:
            return False

        test_case = self.test_cases[test_case_id]
        
        # Update the fields
        for key, value in kwargs.items():
            if hasattr(test_case, key):
                setattr(test_case, key, value)
        
        # Update the last modified timestamp
        test_case.last_modified = datetime.now()
        
        return True

    def delete_test_case(self, test_case_id: str) -> bool:
        """
        Delete a test case

        Args:
            test_case_id: The ID of the test case to delete

        Returns:
            True if the deletion was successful, False otherwise
        """
        if test_case_id not in self.test_cases:
            return False

        # Remove the test case from the module
        test_case = self.test_cases[test_case_id]
        if test_case.module_id in self.modules:
            self.modules[test_case.module_id].test_case_ids.remove(test_case_id)
        
        # Delete the test case
        del self.test_cases[test_case_id]
        return True

    def create_module(self,
                      name: str,
                      description: str,
                      path: str,
                      dependencies: List[str] = None) -> Module:
        """
        Create a new module

        Args:
            name: Name of the module
            description: Description of the module
            path: Path to the module
            dependencies: List of module dependencies

        Returns:
            The created module
        """
        # Generate a unique ID for the module
        module_id = f"mod_{uuid.uuid4().hex[:12]}"

        # Create the module
        module = Module(
            id=module_id,
            name=name,
            description=description,
            path=path,
            dependencies=dependencies or []
        )

        # Store the module
        self.modules[module_id] = module

        return module

    def get_module(self, module_id: str) -> Optional[Module]:
        """
        Get a module by its ID

        Args:
            module_id: The ID of the module to retrieve

        Returns:
            The module, or None if not found
        """
        return self.modules.get(module_id)

    def get_all_test_cases(self) -> List[TestCase]:
        """
        Get all test cases

        Returns:
            List of all test cases
        """
        return list(self.test_cases.values())

    def get_all_modules(self) -> List[Module]:
        """
        Get all modules

        Returns:
            List of all modules
        """
        return list(self.modules.values())