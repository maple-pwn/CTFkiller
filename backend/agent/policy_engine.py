"""
Policy Engine for validating steps against policy rules.
"""

from typing import Dict, Any, List, Optional

from backend.agent.models import Step, PolicyResult, RiskLevel
from backend.policy.rules import ALLOWED_TOOLS, ALLOWED_COMMANDS, FORBIDDEN_COMMANDS


class PolicyEngine:
    """Engine for policy validation of steps."""

    MAX_STEPS = 10
    ALLOWED_TOOLS = ALLOWED_TOOLS

    def __init__(self, allowed_tools: Optional[set] = None):
        """
        Initialize policy engine.

        Args:
            allowed_tools: Set of allowed tool names. If None, uses defaults.
        """
        self.allowed_tools = allowed_tools or self.ALLOWED_TOOLS

    def validate_step(self, step: Step) -> PolicyResult:
        """
        Validate a single step against policy rules.

        Args:
            step: Step to validate

        Returns:
            PolicyResult with validation outcome
        """
        tool = step.tool
        args = step.args

        # Check if tool is in allowed list
        if tool not in self.allowed_tools:
            return PolicyResult(
                allowed=False,
                reason=f"Tool '{tool}' is not in allowed tools list",
                risk_level=RiskLevel.HIGH,
            )

        # Check for forbidden commands in args (string arguments)
        if self._contains_forbidden_args(args):
            return PolicyResult(
                allowed=False,
                reason="Step contains forbidden commands or dangerous arguments",
                risk_level=RiskLevel.HIGH,
            )

        # Check for high-risk operations
        if self._is_high_risk(step):
            return PolicyResult(
                allowed=True,
                reason="Step approved with high risk level",
                risk_level=RiskLevel.HIGH,
            )

        return PolicyResult(
            allowed=True,
            reason="Step passed policy validation",
            risk_level=RiskLevel.LOW,
        )

    def validate_plan(self, steps: List[Step]) -> List[PolicyResult]:
        """
        Validate all steps in a plan.

        Args:
            steps: List of steps to validate

        Returns:
            List of PolicyResult for each step
        """
        return [self.validate_step(step) for step in steps]

    def check_max_steps(self, step_count: int) -> bool:
        """
        Check if step count exceeds maximum.

        Args:
            step_count: Current number of steps

        Returns:
            True if count is within limit
        """
        return step_count <= self.MAX_STEPS

    def _contains_forbidden_args(self, args: Dict[str, Any]) -> bool:
        """Check if args contain forbidden commands."""
        if not isinstance(args, dict):
            return False

        for value in args.values():
            if isinstance(value, str):
                # Check for forbidden command names
                if value.strip() in FORBIDDEN_COMMANDS:
                    return True
                # Check for dangerous patterns
                dangerous_patterns = [
                    "; rm -rf",
                    "&& rm -rf",
                    "| chmod",
                    "> /etc/",
                    "< /etc/",
                ]
                for pattern in dangerous_patterns:
                    if pattern in value:
                        return True

        return False

    def _is_high_risk(self, step: Step) -> bool:
        """Check if step is high risk."""
        tool = step.tool
        args = step.args

        # High-risk tools
        high_risk_tools = {"run_python", "run_shell_safe", "write_file"}

        if tool in high_risk_tools:
            # Check for dangerous file paths
            if "path" in args or "file" in args:
                path = args.get("path") or args.get("file") or ""
                dangerous_paths = ["/etc/", "/var/", "/sys/", "/proc/"]
                if any(dangerous in path for dangerous in dangerous_paths):
                    return True

        return False
