"""
Utility to manage test result storage and retrieval
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from tests.models.test_result import TestResult
from tests.models.error_message import ErrorMessage


class ResultStorageManager:
    """
    Manager for storing and retrieving test results
    """
    
    def __init__(self, storage_path: str = "./test_results"):
        self.storage_path = storage_path
        # Create the storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
    
    def store_test_result(self, test_result: TestResult) -> bool:
        """
        Store a test result to persistent storage
        
        Args:
            test_result: The test result to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Create a filename based on the result ID
            filename = f"{test_result.id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            # Convert the test result to a dictionary
            data = test_result.to_dict()
            
            # Add a timestamp to the data
            data["stored_at"] = datetime.now().isoformat()
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error storing test result: {e}")
            return False
    
    def load_test_result(self, result_id: str) -> Optional[TestResult]:
        """
        Load a test result from persistent storage
        
        Args:
            result_id: The ID of the test result to load
            
        Returns:
            The loaded test result, or None if not found
        """
        try:
            filename = f"{result_id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return TestResult.from_dict(data)
        except Exception as e:
            print(f"Error loading test result: {e}")
            return None
    
    def store_error_message(self, error_message: ErrorMessage) -> bool:
        """
        Store an error message to persistent storage
        
        Args:
            error_message: The error message to store
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Create a filename based on the error message ID
            filename = f"{error_message.id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            # Convert the error message to a dictionary
            data = error_message.to_dict()
            
            # Add a timestamp to the data
            data["stored_at"] = datetime.now().isoformat()
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error storing error message: {e}")
            return False
    
    def get_all_test_results(self) -> List[TestResult]:
        """
        Get all stored test results
        
        Returns:
            List of all stored test results
        """
        results = []
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_path, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    # Check if this is a test result (has the right fields)
                    if "test_case_id" in data:
                        result = TestResult.from_dict(data)
                        results.append(result)
        except Exception as e:
            print(f"Error getting all test results: {e}")
        
        return results
    
    def get_test_results_by_module(self, module_id: str) -> List[TestResult]:
        """
        Get all test results for a specific module
        
        Args:
            module_id: The ID of the module to get results for
            
        Returns:
            List of test results for the module
        """
        all_results = self.get_all_test_results()
        return [r for r in all_results if r.module_id == module_id]