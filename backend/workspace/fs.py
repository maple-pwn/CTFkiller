"""
Workspace file system management for session isolation.
"""

import shutil
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class WorkspaceManager:
    """Manages workspace file system for isolated sessions."""

    BASE_PATH = Path("/tmp/workspace")

    def __init__(self, base_path: Optional[str] = None):
        """Initialize workspace manager with optional custom base path."""
        resolved_base_path = base_path or os.getenv("WORKSPACE_BASE_PATH")
        if resolved_base_path:
            self.BASE_PATH = Path(resolved_base_path)
        self.BASE_PATH.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, session_id: str, path: str) -> Path:
        """
        Validate that the given path is within the session workspace.

        Args:
            session_id: The session identifier
            path: The path to validate (relative to session workspace)

        Returns:
            Absolute Path object if valid

        Raises:
            ValueError: If path contains traversal or is outside workspace
        """
        # Block path traversal attempts
        if "../" in path or "..\\" in path:
            raise ValueError("Path traversal detected")

        # Resolve to absolute path
        session_dir = self.BASE_PATH / session_id
        target_path = (session_dir / path).resolve()

        # Ensure the resolved path is still within session workspace
        if not str(target_path).startswith(str(session_dir.resolve())):
            raise ValueError("Path is outside workspace")

        return target_path

    def create_session_workspace(self, session_id: str) -> str:
        """
        Create a workspace directory for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path to the created workspace directory
        """
        workspace_path = self.BASE_PATH / session_id

        # Create directory if it doesn't exist
        workspace_path.mkdir(parents=True, exist_ok=True)

        return str(workspace_path)

    def get_workspace_path(self, session_id: str) -> str:
        """
        Get the workspace path for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path to the session workspace directory
        """
        return str(self.BASE_PATH / session_id)

    def list_files(self, session_id: str, path: str = "") -> List[dict]:
        """
        List files in the workspace with metadata.

        Args:
            session_id: Unique session identifier
            path: Optional relative path (default: root of workspace)

        Returns:
            List of file metadata dicts with:
                - name: File/directory name
                - size: File size in bytes (0 for directories)
                - type: 'file' or 'directory'
                - modified_time: ISO format modification timestamp
        """
        # Validate and resolve path
        base_path = self._validate_path(session_id, path)

        files = []

        for entry in base_path.iterdir():
            try:
                stat = entry.stat()
                files.append(
                    {
                        "name": entry.name,
                        "size": stat.st_size if entry.is_file() else 0,
                        "type": "directory" if entry.is_dir() else "file",
                        "modified_time": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                    }
                )
            except (OSError, PermissionError):
                # Skip entries we can't access
                continue

        return files

    def cleanup_workspace(self, session_id: str) -> None:
        """
        Clean up a session's workspace directory.

        Args:
            session_id: Unique session identifier
        """
        workspace_path = self.BASE_PATH / session_id

        if workspace_path.exists():
            shutil.rmtree(workspace_path)
