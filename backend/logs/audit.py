"""
Audit logging service for tracking all system actions.

This module provides the AuditLogger class for recording and retrieving
audit trails of actions performed within the system.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class AuditLogger:
    """
    In-memory audit logger for tracking system actions.

    Currently stores logs in memory. Future versions may add database persistence.
    """

    def __init__(self):
        """Initialize the audit logger with an empty log list."""
        self._logs: List[Dict[str, Any]] = []

    def log_action(
        self,
        session_id: str,
        action: str,
        actor: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an action to the audit trail.

        Args:
            session_id: The session identifier
            action: The action type (e.g., 'session_created', 'message_sent')
            actor: The user ID or actor performing the action
            details: Additional JSON details about the action
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "action": action,
            "actor": actor,
            "details": details or {},
        }
        self._logs.append(log_entry)

    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all logs for a specific session.

        Args:
            session_id: The session identifier to filter by

        Returns:
            List of log entries for the session, sorted by timestamp
        """
        return [log for log in self._logs if log["session_id"] == session_id]

    def get_audit_trail(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filters.

        Args:
            filters: Dictionary of filter criteria. Supported filters:
                - session_id: Filter by session
                - action: Filter by action type
                - actor: Filter by actor
                - start_time: Filter logs after this timestamp (ISO 8601)
                - end_time: Filter logs before this timestamp (ISO 8601)

        Returns:
            List of log entries matching the filters
        """
        if not filters:
            return list(self._logs)

        filtered_logs = []

        for log in self._logs:
            match = True

            # Check session_id filter
            if "session_id" in filters:
                if log["session_id"] != filters["session_id"]:
                    match = False

            # Check action filter
            if match and "action" in filters:
                if log["action"] != filters["action"]:
                    match = False

            # Check actor filter
            if match and "actor" in filters:
                if log["actor"] != filters["actor"]:
                    match = False

            # Check start_time filter
            if match and "start_time" in filters:
                try:
                    start_time = datetime.fromisoformat(
                        filters["start_time"].replace("Z", "+00:00")
                    )
                    log_time = datetime.fromisoformat(
                        log["timestamp"].replace("Z", "+00:00")
                    )
                    if log_time < start_time:
                        match = False
                except (ValueError, TypeError):
                    pass

            # Check end_time filter
            if match and "end_time" in filters:
                try:
                    end_time = datetime.fromisoformat(
                        filters["end_time"].replace("Z", "+00:00")
                    )
                    log_time = datetime.fromisoformat(
                        log["timestamp"].replace("Z", "+00:00")
                    )
                    if log_time > end_time:
                        match = False
                except (ValueError, TypeError):
                    pass

            if match:
                filtered_logs.append(log)

        return filtered_logs

    def clear_logs(self) -> None:
        """Clear all logs from the audit trail."""
        self._logs.clear()


# Global instance for easy access
audit_logger = AuditLogger()
