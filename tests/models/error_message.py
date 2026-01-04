"""
Data model for error messages in the 2Top test system
"""

from datetime import datetime
from typing import Optional, Dict, Any


class ErrorMessage:
    """
    Represents an error message in the 2Top test system
    """
    
    def __init__(self, 
                 id: str,
                 test_result_id: str,
                 message: str,
                 severity: str,
                 suggested_fix: Optional[str] = None):
        self.id = id
        self.test_result_id = test_result_id
        self.message = message
        self.severity = severity  # Can be "info", "warning", "error"
        self.suggested_fix = suggested_fix
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error message to a dictionary for storage"""
        return {
            "id": self.id,
            "test_result_id": self.test_result_id,
            "message": self.message,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorMessage':
        """Create an error message from a dictionary"""
        # Convert datetime strings back to datetime objects
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        
        return cls(
            id=data["id"],
            test_result_id=data["test_result_id"],
            message=data["message"],
            severity=data["severity"],
            suggested_fix=data.get("suggested_fix")
        )