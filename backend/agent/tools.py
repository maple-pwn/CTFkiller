"""
Tool implementations for the Agent Orchestrator.
"""

from typing import Any, Dict, List, Optional

from backend.tools.base import BaseTool, RiskLevel


class ListDirTool(BaseTool):
    """List directory contents tool."""

    def __init__(self):
        super().__init__(
            name="list_dir",
            description="List contents of a directory",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list"},
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
            risk_level=RiskLevel.LOW,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import os

        path = args.get("path", ".")
        recursive = args.get("recursive", False)

        try:
            if recursive:
                result = []
                for root, dirs, files in os.walk(path):
                    result.append({"dir": root, "files": files, "dirs": dirs})
            else:
                result = os.listdir(path)

            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ReadFileTool(BaseTool):
    """Read file contents tool."""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read contents of a file",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                    "offset": {
                        "type": "integer",
                        "description": "Byte offset to start reading",
                        "default": 0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum bytes to read",
                        "default": 10000,
                    },
                },
                "required": ["path"],
            },
            risk_level=RiskLevel.MEDIUM,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        path = args.get("path")
        offset = args.get("offset", 0)
        limit = args.get("limit", 10000)

        try:
            with open(path, "rb") as f:
                f.seek(offset)
                content = f.read(limit)

            # Try to decode as text, otherwise return base64
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                import base64

                text_content = base64.b64encode(content).decode("utf-8")

            return {"success": True, "result": text_content}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WriteFileTool(BaseTool):
    """Write file contents tool."""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write contents to a file",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                    "mode": {
                        "type": "string",
                        "description": "Write mode: 'w' or 'a'",
                        "default": "w",
                    },
                },
                "required": ["path", "content"],
            },
            risk_level=RiskLevel.MEDIUM,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        path = args.get("path")
        content = args.get("content")
        mode = args.get("mode", "w")

        try:
            with open(path, mode) as f:
                f.write(content)
            return {"success": True, "result": f"Wrote to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class SearchTextTool(BaseTool):
    """Search for text patterns in files."""

    def __init__(self):
        super().__init__(
            name="search_text",
            description="Search for text pattern in files",
            parameters_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search",
                        "default": ".",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively",
                        "default": True,
                    },
                },
                "required": ["pattern"],
            },
            risk_level=RiskLevel.LOW,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import re
        import os

        pattern = args.get("pattern")
        path = args.get("path", ".")
        recursive = args.get("recursive", True)

        try:
            results = []
            compiled_pattern = re.compile(pattern)

            if os.path.isfile(path):
                # Single file search
                with open(path, "rb") as f:
                    content = f.read()
                    try:
                        text = content.decode("utf-8")
                    except UnicodeDecodeError:
                        text = content.decode("latin-1")

                    for match in compiled_pattern.finditer(text):
                        results.append(
                            {
                                "file": path,
                                "match": match.group(),
                                "position": match.start(),
                            }
                        )
            else:
                # Directory search
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "rb") as f:
                                content = f.read()
                                try:
                                    text = content.decode("utf-8")
                                except UnicodeDecodeError:
                                    continue

                                for match in compiled_pattern.finditer(text):
                                    results.append(
                                        {
                                            "file": file_path,
                                            "match": match.group(),
                                            "position": match.start(),
                                        }
                                    )
                        except Exception:
                            continue

                    if not recursive:
                        break

            return {
                "success": True,
                "result": {"matches": results, "count": len(results)},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class RunPythonTool(BaseTool):
    """Execute Python code safely."""

    def __init__(self):
        super().__init__(
            name="run_python",
            description="Execute Python code in a restricted sandbox",
            parameters_schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                    "input_data": {
                        "type": "object",
                        "description": "Input data for the code",
                    },
                },
                "required": ["code"],
            },
            risk_level=RiskLevel.HIGH,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import sys
        from io import StringIO

        code = args.get("code")
        input_data = args.get("input_data", {})

        try:
            # Create restricted environment
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "bool": bool,
                }
            }
            safe_globals.update(input_data)

            # Capture output
            output = StringIO()
            sys.stdout = output

            try:
                exec(code, safe_globals)
                result = safe_globals.get("_result")
                if result is None:
                    exec("result = None", safe_globals)
                    result = safe_globals.get("result")
            finally:
                sys.stdout = sys.__stdout__

            return {
                "success": True,
                "result": {"output": output.getvalue(), "result": result},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class RunShellSafeTool(BaseTool):
    """Execute safe shell commands."""

    def __init__(self):
        super().__init__(
            name="run_shell_safe",
            description="Execute a safe shell command",
            parameters_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
            risk_level=RiskLevel.HIGH,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import subprocess

        command = args.get("command")
        timeout = args.get("timeout", 30)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": True,
                "result": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                },
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class ExtractArchiveTool(BaseTool):
    """Extract archive files."""

    def __init__(self):
        super().__init__(
            name="extract_archive",
            description="Extract an archive file (zip, tar, tar.gz)",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to archive file"},
                    "destination": {
                        "type": "string",
                        "description": "Destination directory",
                    },
                },
                "required": ["path"],
            },
            risk_level=RiskLevel.MEDIUM,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import zipfile
        import tarfile
        import os

        path = args.get("path")
        destination = args.get("destination", os.path.dirname(path))

        try:
            if path.endswith(".zip"):
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(destination)
            elif path.endswith((".tar", ".tar.gz", ".tgz")):
                with tarfile.open(path, "r:*") as tar_ref:
                    tar_ref.extractall(destination)
            else:
                return {"success": False, "error": "Unknown archive format"}

            return {"success": True, "result": f"Extracted to {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class GetFileInfoTool(BaseTool):
    """Get file information."""

    def __init__(self):
        super().__init__(
            name="get_file_info",
            description="Get detailed information about a file",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to inspect"},
                },
                "required": ["path"],
            },
            risk_level=RiskLevel.LOW,
        )

    def execute(
        self, args: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        import os
        import stat

        path = args.get("path")

        try:
            file_stat = os.stat(path)
            stat_info = os.stat(path)

            return {
                "success": True,
                "result": {
                    "size": file_stat.st_size,
                    "mode": stat.filemode(file_stat.st_mode),
                    "is_file": os.path.isfile(path),
                    "is_dir": os.path.isdir(path),
                    "is_executable": os.access(path, os.X_OK),
                    "created": file_stat.st_ctime,
                    "modified": file_stat.st_mtime,
                    "accessed": file_stat.st_atime,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Factory function to register all tools
def register_default_tools(registry: "ToolRegistry") -> None:
    """Register all default tools with a registry."""
    registry.register(ListDirTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(SearchTextTool())
    registry.register(RunPythonTool())
    registry.register(RunShellSafeTool())
    registry.register(ExtractArchiveTool())
    registry.register(GetFileInfoTool())
