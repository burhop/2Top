"""
Utility to identify which module a test case belongs to
"""

from typing import Optional
from tests.models.test_case import TestCase
from tests.models.module import Module


class ModuleIdentifier:
    """
    Utility to identify and work with modules
    """
    
    def __init__(self):
        self.modules = {}  # In a real system, this would be a database or registry
    
    def get_module_by_id(self, module_id: str) -> Optional[Module]:
        """
        Get a module by its ID
        
        Args:
            module_id: The ID of the module to retrieve
            
        Returns:
            The module if found, None otherwise
        """
        # In a real system, this would look up the module in a database or registry
        # For this implementation, we'll return a basic module for demonstration
        if module_id in self.modules:
            return self.modules[module_id]
        return None
    
    def get_module_by_test_case(self, test_case: TestCase) -> Optional[Module]:
        """
        Get the module that a test case belongs to
        
        Args:
            test_case: The test case to find the module for
            
        Returns:
            The module that the test case belongs to, or None if not found
        """
        # In a real system, this would look up the module in a database or registry
        # For this implementation, we'll return a basic module for demonstration
        return Module(
            id=test_case.module_id,
            name=f"Module {test_case.module_id}",
            description="Module that contains the test case",
            path=f"/path/to/{test_case.module_id}"
        )
    
    def add_module(self, module: Module) -> None:
        """
        Add a module to the identifier
        
        Args:
            module: The module to add
        """
        self.modules[module.id] = module
    
    def get_all_modules(self) -> list:
        """
        Get all registered modules
        
        Returns:
            List of all registered modules
        """
        return list(self.modules.values())