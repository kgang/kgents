"""
K8s-specific exceptions for K-Terrarium.

These exceptions enable graceful degradation when K8s tooling is unavailable.
"""

from __future__ import annotations


class TerrariumError(Exception):
    """Base exception for K-Terrarium operations."""

    pass


class KindNotFoundError(TerrariumError):
    """Kind CLI not found in PATH."""

    def __init__(self) -> None:
        super().__init__(
            "Kind not found. Install from https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
        )


class DockerNotFoundError(TerrariumError):
    """Docker not running or not found."""

    def __init__(self, detail: str = "") -> None:
        msg = "Docker not available"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class ClusterNotFoundError(TerrariumError):
    """Expected cluster does not exist."""

    def __init__(self, name: str) -> None:
        self.cluster_name = name
        super().__init__(f"Cluster '{name}' not found. Run 'kgents infra init' first.")


class ClusterOperationError(TerrariumError):
    """A cluster operation failed."""

    def __init__(self, operation: str, detail: str) -> None:
        self.operation = operation
        self.detail = detail
        super().__init__(f"Cluster {operation} failed: {detail}")


class KubectlNotFoundError(TerrariumError):
    """kubectl CLI not found in PATH."""

    def __init__(self) -> None:
        super().__init__(
            "kubectl not found. Kind should install it, or install manually from https://kubernetes.io/docs/tasks/tools/"
        )


class ImageNotFoundError(TerrariumError):
    """Container image not found locally or in Kind cluster."""

    def __init__(self, image: str, suggestion: str = "") -> None:
        self.image = image
        msg = f"Image '{image}' not found"
        if suggestion:
            msg += f". {suggestion}"
        super().__init__(msg)


class EntrypointInvalidError(TerrariumError):
    """Entrypoint module or file does not exist."""

    def __init__(self, entrypoint: str, reason: str = "") -> None:
        self.entrypoint = entrypoint
        msg = f"Entrypoint '{entrypoint}' is invalid"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
