"""
Data model for test cases in the 2Top test system
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


class TestCase:
    """
    Represents a test case in the 2Top test system
    """
    
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 module_id: str,
                 test_type: str,
                 input_data: Dict[str, Any],
                 expected_result: Any,
                 valid: bool = True,
                 validation_reason: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.module_id = module_id
        self.test_type = test_type
        self.input_data = input_data
        self.expected_result = expected_result
        self.status = "pending"  # Can be "pending", "passed", "failed", "invalid"
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
        self.valid = valid
        self.validation_reason = validation_reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the test case to a dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "module_id": self.module_id,
            "test_type": self.test_type,
            "input_data": self.input_data,
            "expected_result": self.expected_result,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "valid": self.valid,
            "validation_reason": self.validation_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """Create a test case from a dictionary"""
        # Convert datetime strings back to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        last_modified = datetime.fromisoformat(data["last_modified"]) if isinstance(data["last_modified"], str) else data["last_modified"]
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            module_id=data["module_id"],
            test_type=data["test_type"],
            input_data=data["input_data"],
            expected_result=data["expected_result"],
            valid=data.get("valid", True),
            validation_reason=data.get("validation_reason")
        )