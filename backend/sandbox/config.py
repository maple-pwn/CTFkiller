"""Security configuration for Docker sandbox environment."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SandboxConfig:
    """Security hardening configuration for sandbox containers."""

    # Container base image
    image: str = "python:3.11-slim"

    # Resource limits
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    pids_limit: int = 100
    timeout: int = 300  # seconds

    # Security hardening
    read_only: bool = True
    network_mode: str = "none"
    drop_capabilities: List[str] = None
    add_capabilities: List[str] = None
    no_new_privileges: bool = True

    # User/Group (non-root: 10001:10001)
    user: str = "10001:10001"

    # Mount configuration (read-only by default)
    mounts: List[Dict] = None

    # Environment variables
    environment: Dict[str, str] = None

    # Working directory
    working_dir: str = "/workspace"

    # Temporary directory (tmpfs)
    tmpfs: Dict[str, str] = None

    def __post_init__(self):
        """Initialize default values."""
        # Security: Drop ALL capabilities by default
        if self.drop_capabilities is None:
            self.drop_capabilities = ["ALL"]

        # Add only necessary capabilities
        if self.add_capabilities is None:
            self.add_capabilities = []

        # Custom mounts (read-only)
        if self.mounts is None:
            self.mounts = []

        # Environment variables
        if self.environment is None:
            self.environment = {
                "PATH": "/usr/local/bin:/usr/bin:/bin",
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
                "HOME": "/workspace",
                "LANG": "C.UTF-8",
            }

        # Tmpfs for /tmp and /workspace (needed for non-root write access)
        if self.tmpfs is None:
            self.tmpfs = {
                "/tmp": "rw,noexec,nosuid,size=64m",
                "/workspace": "rw,noexec,nosuid,size=128m",
            }


# Global default configuration
_default_config: Optional[SandboxConfig] = None


def get_default_config() -> SandboxConfig:
    """Get or create the default sandbox configuration."""
    global _default_config
    if _default_config is None:
        _default_config = SandboxConfig()
    return _default_config


def reset_default_config():
    """Reset the default configuration (useful for testing)."""
    global _default_config
    _default_config = None
