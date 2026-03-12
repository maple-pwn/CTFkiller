"""
Test script to verify tool registry implementation.
"""

from backend.tools.base import BaseTool, RiskLevel
from backend.tools.registry import ToolRegistry
from backend.tools.file_tools import ListDirTool, ReadFileTool, WriteFileTool
from backend.tools.search_tools import SearchTextTool
from backend.tools.execution_tools import RunPythonTool, RunShellSafeTool
from backend.tools.archive_tools import ExtractArchiveTool, GetFileInfoTool


def test_tool_registry():
    """Test the tool registry with all 8 tools."""
    registry = ToolRegistry()
    
    # Register all 8 tools
    tools = [
        ListDirTool(),
        ReadFileTool(),
        WriteFileTool(),
        SearchTextTool(),
        RunPythonTool(),
        RunShellSafeTool(),
        ExtractArchiveTool(),
        GetFileInfoTool(),
    ]
    
    print("=== Testing Tool Registration ===")
    for tool in tools:
        try:
            registry.register(tool)
            print(f"✓ Registered: {tool.name}")
        except ValueError as e:
            print(f"✗ Failed to register {tool.name}: {e}")
            return False
    
    print("\n=== Testing Tool Retrieval ===")
    for tool in tools:
        retrieved = registry.get_tool(tool.name)
        if retrieved and isinstance(retrieved, BaseTool):
            print(f"✓ Retrieved: {retrieved.name}")
        else:
            print(f"✗ Failed to retrieve: {tool.name}")
            return False
    
    print("\n=== Testing List Tools ===")
    all_tools = registry.list_tools()
    if len(all_tools) == 8:
        print(f"✓ All {len(all_tools)} tools listed")
    else:
        print(f"✗ Expected 8 tools, got {len(all_tools)}")
        return False
    
    print("\n=== Testing Parameter Schema Validation ===")
    # Test valid args
    valid_list_dir_args = {"path": "/tmp"}
    try:
        registry.validate_args("list_dir", valid_list_dir_args)
        print("✓ list_dir validation passed for valid args")
    except Exception as e:
        print(f"✗ list_dir validation failed: {e}")
        return False
    
    # Test invalid args
    invalid_list_dir_args = {"invalid_key": "/tmp"}
    try:
        registry.validate_args("list_dir", invalid_list_dir_args)
        print("✗ list_dir should have failed for invalid args")
        return False
    except Exception:
        print("✓ list_dir validation correctly rejected invalid args")
    
    print("\n=== Testing Tool Info ===")
    tool_info = registry.get_tool_info("write_file")
    if tool_info:
        print(f"✓ write_file info: name={tool_info['name']}, risk={tool_info['risk_level']}")
    else:
        print("✗ Failed to get tool info")
        return False
    
    print("\n=== Verifying Results Format ===")
    # Check that all tools return the expected structure
    test_context = {"user": "test"}
    
    for tool in tools:
        result = tool.execute({}, test_context)
        if all(key in result for key in ["success", "result", "error"]):
            print(f"✓ {tool.name} returns standardized format")
        else:
            print(f"✗ {tool.name} missing required result keys")
            return False
    
    print("\n=== All Tests Passed ===")
    return True


if __name__ == "__main__":
    success = test_tool_registry()
    exit(0 if success else 1)
