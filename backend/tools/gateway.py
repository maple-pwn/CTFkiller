import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.workspace.fs import WorkspaceManager
from backend.policy.engine import PolicyEngine


class ToolGateway:
    def __init__(self):
        self.workspace_manager = WorkspaceManager()
        self.policy_engine = PolicyEngine()

    def execute_tool(
        self, session_id: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        valid, error = self.policy_engine.validate_tool(tool_name, session_id)
        if not valid:
            return {"success": False, "error": error}

        handler = getattr(self, f"_handle_{tool_name}", None)
        if not handler:
            return {"success": False, "error": f"Tool '{tool_name}' not implemented"}

        try:
            result = handler(session_id, arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_list_dir(self, session_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        path = args.get("path", "")
        workspace_path = self.workspace_manager.get_workspace_path(session_id)
        full_path = os.path.join(workspace_path, path.lstrip("/"))

        valid, error = self.policy_engine.validate_path(full_path, session_id)
        if not valid:
            raise ValueError(error)

        return self.workspace_manager.list_files(session_id, path)

    def _handle_read_file(self, session_id: str, args: Dict[str, Any]) -> str:
        path = args.get("path", "")
        workspace_path = self.workspace_manager.get_workspace_path(session_id)
        full_path = os.path.join(workspace_path, path.lstrip("/"))

        valid, error = self.policy_engine.validate_path(full_path, session_id)
        if not valid:
            raise ValueError(error)

        with open(full_path, "r") as f:
            return f.read()

    def _handle_write_file(
        self, session_id: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = args.get("path", "")
        content = args.get("content", "")
        workspace_path = self.workspace_manager.get_workspace_path(session_id)
        full_path = os.path.join(workspace_path, path.lstrip("/"))

        valid, error = self.policy_engine.validate_path(full_path, session_id)
        if not valid:
            raise ValueError(error)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

        return {"path": path, "bytes_written": len(content)}

    def _handle_search_text(
        self, session_id: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        pattern = args.get("pattern", "")
        path = args.get("path", "")
        workspace_path = self.workspace_manager.get_workspace_path(session_id)
        search_path = os.path.join(workspace_path, path.lstrip("/"))

        valid, error = self.policy_engine.validate_path(search_path, session_id)
        if not valid:
            raise ValueError(error)

        results = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                results.append(
                                    {
                                        "file": os.path.relpath(
                                            file_path, workspace_path
                                        ),
                                        "line": line_num,
                                        "content": line.strip(),
                                    }
                                )
                except:
                    pass

        return {"matches": results, "count": len(results)}

    def _handle_run_shell_safe(
        self, session_id: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        command = args.get("command", "")

        valid, error = self.policy_engine.validate_command(command, session_id)
        if not valid:
            raise ValueError(error)

        workspace_path = self.workspace_manager.get_workspace_path(session_id)

        result = subprocess.run(
            command,
            shell=True,
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def _handle_get_file_info(
        self, session_id: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        path = args.get("path", "")
        workspace_path = self.workspace_manager.get_workspace_path(session_id)
        full_path = os.path.join(workspace_path, path.lstrip("/"))

        valid, error = self.policy_engine.validate_path(full_path, session_id)
        if not valid:
            raise ValueError(error)

        stat = os.stat(full_path)
        return {
            "path": path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": os.path.isfile(full_path),
            "is_dir": os.path.isdir(full_path),
        }
