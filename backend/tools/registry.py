"""
Tool registry for registering and querying tools.
"""

import json
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema import ValidationError

from backend.tools.base import BaseTool, RiskLevel


class ToolRegistry:
    """Registry for managing tool instances with validation."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool with the registry.
        
        Args:
            tool: BaseTool instance to register
        
        Raises:
            ValueError: If tool with same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name to look up
        
        Returns:
            BaseTool instance if found, None otherwise
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[BaseTool]:
        """
        List all registered tools.
        
        Returns:
            List of all registered BaseTool instances
        """
        return list(self._tools.values())
    
    def validate_args(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """
        Validate arguments against tool's parameter schema.
        
        Args:
            tool_name: Name of the tool to validate against
            args: Arguments to validate
        
        Returns:
            True if valid, raises ValidationError if invalid
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        jsonschema.validate(instance=args, schema=tool.parameters_schema)
        return True
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool metadata by name.
        
        Args:
            name: Tool name to look up
        
        Returns:
            Dict with tool metadata or None if not found
        """
        tool = self.get_tool(name)
        if tool:
            return tool.get_info()
        return None
    
    def list_tools_info(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all registered tools.
        
        Returns:
            List of tool metadata dicts
        """
        return [tool.get_info() for tool in self._tools.values()]
