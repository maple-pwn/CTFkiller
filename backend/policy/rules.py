from enum import Enum
from typing import Optional
from dataclasses import dataclass


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PolicyResult:
    allowed: bool
    reason: str = ""
    risk_level: RiskLevel = RiskLevel.LOW


ALLOWED_TOOLS: set = {
    "list_dir",
    "read_file",
    "write_file",
    "search_text",
    "run_python",
    "run_shell_safe",
    "extract_archive",
    "get_file_info",
}

ALLOWED_COMMANDS: set = {
    "ls",
    "cat",
    "grep",
    "head",
    "tail",
    "wc",
    "file",
    "strings",
}

FORBIDDEN_COMMANDS: set = {
    "sudo",
    "chmod",
    "chown",
    "mount",
    "iptables",
    "docker",
    "ssh",
    "nc",
    "curl",
    "wget",
}

MAX_CONCURRENT_CONTAINERS: int = 10

TOOL_WHITELIST = ALLOWED_TOOLS
COMMAND_WHITELIST = ALLOWED_COMMANDS
COMMAND_BLACKLIST = FORBIDDEN_COMMANDS

POLICY_RULES = {
    "tool_whitelist": TOOL_WHITELIST,
    "command_whitelist": COMMAND_WHITELIST,
    "command_blacklist": COMMAND_BLACKLIST,
    "max_containers": MAX_CONCURRENT_CONTAINERS,
}


def check_tool_whitelist(tool_name: str) -> bool:
    return tool_name in TOOL_WHITELIST


def check_command_safe(command: str) -> bool:
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return False

    base_cmd = cmd_parts[0]

    if base_cmd in COMMAND_BLACKLIST:
        return False

    if base_cmd not in COMMAND_WHITELIST:
        return False

    return True


def check_path_restriction(path: str, session_id: str) -> bool:
    if ".." in path:
        return False

    workspace_prefix = f"/workspace/{session_id}/"
    return path.startswith(workspace_prefix)
