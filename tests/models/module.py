"""
Data model for modules in the 2Top test system
"""

from datetime import datetime
from typing import List, Optional


class Module:
    """
    Represents a module in the 2Top test system
    """
    
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 path: str,
                 dependencies: List[str] = None,
                 test_case_ids: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.path = path
        self.dependencies = dependencies or []
        self.test_case_ids = test_case_ids or []
        self.last_updated = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert the module to a dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "dependencies": self.dependencies,
            "test_case_ids": self.test_case_ids,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Module':
        """Create a module from a dictionary"""
        # Convert datetime strings back to datetime objects
        last_updated = datetime.fromisoformat(data["last_updated"]) if isinstance(data["last_updated"], str) else data["last_updated"]
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            path=data["path"],
            dependencies=data.get("dependencies", []),
            test_case_ids=data.get("test_case_ids", [])
        )