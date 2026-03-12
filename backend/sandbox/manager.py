"""Docker container lifecycle management for sandbox environment."""

import time
import docker
from docker.models.containers import Container
from docker.errors import DockerException, APIError
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from .config import SandboxConfig, get_default_config


class SandboxError(Exception):
    """Base exception for sandbox-related errors."""
    pass


class ContainerNotFound(SandboxError):
    """Raised when a container cannot be found."""

    def __init__(self, container_id: str):
        self.container_id = container_id
        super().__init__(f"Container not found: {container_id}")


class ExecutionTimeout(SandboxError):
    """Raised when command execution exceeds timeout."""

    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Execution exceeded timeout of {timeout} seconds")


class ResourceExhausted(SandboxError):
    """Raised when container runs out of resources."""

    def __init__(self, message: str = "Container ran out of resources"):
        super().__init__(message)


class SandboxManager:
    """Docker container lifecycle management for sandboxed execution."""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or get_default_config()
        self._client: Optional[docker.DockerClient] = None
        self._containers: Dict[str, Container] = {}

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def create_sandbox(self, session_id: str) -> Container:
        try:
            create_kwargs = {
                "name": f"sandbox-{session_id}",
                "image": self.config.image,
                "command": "tail -f /dev/null",
                "detach": True,
                "user": self.config.user,
                "read_only": self.config.read_only,
                "network_mode": self.config.network_mode,
                "security_opt": [
                    f"no-new-privileges:{'true' if self.config.no_new_privileges else 'false'}"
                ],
                "cap_drop": self.config.drop_capabilities,
                "pids_limit": self.config.pids_limit,
                "mem_limit": self.config.memory_limit,
                "cpu_quota": int(self.config.cpu_limit * 100000),
                "cpu_period": 100000,
                "environment": self.config.environment,
                "working_dir": self.config.working_dir,
                "tmpfs": self.config.tmpfs,
            }

            if self.config.add_capabilities:
                create_kwargs["cap_add"] = self.config.add_capabilities

            if self.config.mounts:
                create_kwargs["mounts"] = self.config.mounts

            container = self.client.containers.create(**create_kwargs)
            container.start()
            self._containers[session_id] = container

            return container

        except APIError as e:
            error_msg = str(e.explanation) if hasattr(e, "explanation") else str(e)
            if "too many" in error_msg.lower() or "resources" in error_msg.lower():
                raise ResourceExhausted(f"Failed to create container: {error_msg}")
            raise DockerException(f"Docker API error: {error_msg}")

    def execute_in_sandbox(
        self, container_id: str, command: List[str], timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        if container_id not in self._containers:
            raise ContainerNotFound(container_id)

        container = self._containers[container_id]
        actual_timeout = timeout or self.config.timeout

        start_time = time.time()

        result = container.exec_run(cmd=command, demux=True)

        duration = time.time() - start_time
        while duration < actual_timeout:
            inspect = self.client.api.exec_inspect(result.output[1])
            if not inspect.get("Running", False):
                break
            time.sleep(0.1)
            duration = time.time() - start_time

        if duration >= actual_timeout:
            try:
                container.kill()
            except DockerException:
                pass
            raise ExecutionTimeout(actual_timeout)

        stdout = (
            result.output[0].decode("utf-8", errors="replace")
            if result.output[0]
            else ""
        )
        stderr = (
            result.output[1].decode("utf-8", errors="replace")
            if result.output[1]
            else ""
        )

        return {
            "exit_code": result.exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration": round(duration, 3),
        }

    def cleanup_sandbox(self, container_id: str) -> bool:
        if container_id not in self._containers:
            return False

        container = self._containers[container_id]

        try:
            container.stop(timeout=5)
        except DockerException:
            pass

        try:
            container.remove(v=True, force=True)
        except DockerException:
            pass

        if container_id in self._containers:
            del self._containers[container_id]

        return True

    def list_active_sandboxes(self) -> List[Container]:
        active = []
        for session_id, container in list(self._containers.items()):
            try:
                container.reload()
                if container.status == "running":
                    active.append(container)
                else:
                    if session_id in self._containers:
                        del self._containers[session_id]
            except DockerException:
                if session_id in self._containers:
                    del self._containers[session_id]

        return active

    def cleanup_all(self):
        for container_id in list(self._containers.keys()):
            self.cleanup_sandbox(container_id)

    def __del__(self):
        try:
            self.cleanup_all()
        except DockerException:
            pass

    @contextmanager
    def sandbox(self, session_id: str):
        container = None
        try:
            container = self.create_sandbox(session_id)
            yield container
        finally:
            if container:
                try:
                    self.cleanup_sandbox(session_id)
                except DockerException:
                    pass

    def get_container(self, session_id: str) -> Optional[Container]:
        return self._containers.get(session_id)


_default_manager: Optional[SandboxManager] = None


def get_default_manager() -> SandboxManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = SandboxManager()
    return _default_manager


def reset_default_manager():
    global _default_manager
    if _default_manager is not None:
        _default_manager.cleanup_all()
        _default_manager = None
