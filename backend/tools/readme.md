# Tool Registry

Dynamic tool registration and lookup system for the CTFkiller backend.

## Structure

```
backend/tools/
├── __init__.py         # Package exports
├── base.py             # BaseTool abstract class and RiskLevel enum
├── registry.py         # ToolRegistry for registration/lookup
├── file_tools.py       # list_dir, read_file, write_file
├── search_tools.py     # search_text
├── execution_tools.py  # run_python, run_shell_safe
├── archive_tools.py    # extract_archive, get_file_info
└── test_registry.py    # Verification test script
```

## Components

### BaseTool (base.py)
Abstract base class for all tools with:
- `name`: Unique identifier
- `description`: Human-readable description
- `parameters_schema`: JSON Schema for argument validation
- `risk_level`: Risk classification (low, medium, high)
- `execute(args, context) -> dict`: Abstract execution method

### ToolRegistry (registry.py)
Registry manager with methods:
- `register(tool)`: Register a tool
- `get_tool(name)`: Retrieve a tool by name
- `list_tools()`: List all registered tools
- `validate_args(tool_name, args)`: Validate arguments against schema

### Tools

| Tool | File | Risk Level | Description |
|------|------|------------|-------------|
| list_dir | file_tools.py | low | List directory contents |
| read_file | file_tools.py | medium | Read file content |
| write_file | file_tools.py | medium | Write file content |
| search_text | search_tools.py | low | Search text patterns |
| run_python | execution_tools.py | high | Execute Python in sandbox |
| run_shell_safe | execution_tools.py | high | Execute whitelisted shell |
| extract_archive | archive_tools.py | medium | Extract zip/tar archives |
| get_file_info | archive_tools.py | low | Get file metadata |

## Testing

```bash
cd /home/pwn/sth/CTFkiller
python3 backend/tools/test_registry.py
```

## Result Format

All tools return standardized format:
```python
{
    "success": bool,
    "result": any,
    "error": str
}
```
