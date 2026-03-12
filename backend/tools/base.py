"""
Base classes for tool registry system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(Enum):
    """Risk level classification for tools."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any], risk_level: RiskLevel):
        """
        Initialize a tool.
        
        Args:
            name: Unique identifier for the tool
            description: Human-readable description of what the tool does
            parameters_schema: JSON Schema defining the expected parameters
            risk_level: Risk classification for the tool
        """
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
        self.risk_level = risk_level
    
    @abstractmethod
    def execute(self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            args: Tool arguments matching the parameters schema
            context: Optional execution context (user info, session data, etc.)
        
        Returns:
            Dict with keys: success, result, error
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters_schema": self.parameters_schema,
            "risk_level": self.risk_level.value
        }
