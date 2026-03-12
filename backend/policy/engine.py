from typing import Dict, List, Any, Optional
from backend.policy.rules import (
    POLICY_RULES,
    check_tool_whitelist,
    check_command_safe,
    check_path_restriction,
)
from backend.database.models import PolicyViolation
from backend.database.connection import get_db


class PolicyEngine:
    def __init__(self):
        self.rules = POLICY_RULES

    def validate_tool(
        self, tool_name: str, session_id: str
    ) -> tuple[bool, Optional[str]]:
        if not check_tool_whitelist(tool_name):
            return False, f"Tool '{tool_name}' not in whitelist"
        return True, None

    def validate_command(
        self, command: str, session_id: str
    ) -> tuple[bool, Optional[str]]:
        if not check_command_safe(command):
            return False, f"Command '{command}' violates safety policy"
        return True, None

    def validate_path(self, path: str, session_id: str) -> tuple[bool, Optional[str]]:
        if not check_path_restriction(path, session_id):
            return False, f"Path '{path}' outside workspace"
        return True, None

    def validate_execution_plan(
        self, plan: Dict[str, Any], session_id: str
    ) -> tuple[bool, List[str]]:
        violations = []

        for step in plan.get("steps", []):
            tool_name = step.get("tool")
            args = step.get("arguments", {})

            valid, error = self.validate_tool(tool_name, session_id)
            if not valid:
                violations.append(error)

            if tool_name == "run_shell_safe":
                command = args.get("command", "")
                valid, error = self.validate_command(command, session_id)
                if not valid:
                    violations.append(error)

            if "path" in args:
                valid, error = self.validate_path(args["path"], session_id)
                if not valid:
                    violations.append(error)

        return len(violations) == 0, violations

    def log_violation(
        self, session_id: str, rule_name: str, details: str, severity: str = "critical"
    ):
        db = next(get_db())
        try:
            violation = PolicyViolation(
                session_id=session_id,
                rule_name=rule_name,
                violation_details=details,
                severity=severity,
            )
            db.add(violation)
            db.commit()
        finally:
            db.close()
