"""
Data model for test results in the 2Top test system
"""

from datetime import datetime
from typing import Optional, Any, Dict


class TestResultModel:
    """
    Represents a test result in the 2Top test system
    """
    
    def __init__(self, 
                 id: str,
                 test_case_id: str,
                 module_id: str,
                 status: str,
                 timestamp: datetime,
                 execution_time: float,
                 error_details: Optional[str] = None,
                 output: Optional[str] = None,
                 diagnosis: Optional[str] = None):
        self.id = id
        self.test_case_id = test_case_id
        self.module_id = module_id
        self.status = status  # Can be "passed", "failed"
        self.timestamp = timestamp
        self.execution_time = execution_time
        self.error_details = error_details
        self.output = output
        self.diagnosis = diagnosis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the test result to a dictionary for storage"""
        return {
            "id": self.id,
            "test_case_id": self.test_case_id,
            "module_id": self.module_id,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "execution_time": self.execution_time,
            "error_details": self.error_details,
            "output": self.output,
            "diagnosis": self.diagnosis
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create a test result from a dictionary"""
        # Convert datetime strings back to datetime objects
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        
        return cls(
            id=data["id"],
            test_case_id=data["test_case_id"],
            module_id=data["module_id"],
            status=data["status"],
            timestamp=timestamp,
            execution_time=data["execution_time"],
            error_details=data.get("error_details"),
            output=data.get("output"),
            diagnosis=data.get("diagnosis")
        )