"""
Environment detection for K-Terrarium.

Determines whether K8s tooling is available and what mode to operate in.
Enables graceful degradation when Docker/Kind are not present.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum, auto


class TerrariumCapability(Enum):
    """What K8s capabilities are available."""

    NONE = auto()  # No K8s tooling (Docker or Kind missing)
    KIND_AVAILABLE = auto()  # Kind installed, no cluster running
    CLUSTER_RUNNING = auto()  # Kind cluster active and ready


@dataclass
class TerrariumDetection:
    """Result of environment detection."""

    capability: TerrariumCapability
    kind_path: str | None = None
    kubectl_path: str | None = None
    docker_available: bool = False
    cluster_name: str | None = None
    error: str | None = None

    @property
    def can_create_cluster(self) -> bool:
        """Whether we can create a new cluster."""
        return self.capability in (
            TerrariumCapability.KIND_AVAILABLE,
            TerrariumCapability.CLUSTER_RUNNING,
        )

    @property
    def has_running_cluster(self) -> bool:
        """Whether a cluster is currently running."""
        return self.capability == TerrariumCapability.CLUSTER_RUNNING


def detect_terrarium_mode(cluster_name: str = "kgents-local") -> TerrariumDetection:
    """
    Detect what K-Terrarium capabilities are available.

    Order of checks:
    1. Docker running?
    2. Kind installed?
    3. Cluster exists?

    Args:
        cluster_name: Name of the Kind cluster to check for.

    Returns:
        TerrariumDetection with capability level and details.
    """
    # Check Docker first
    docker_available = _check_docker()
    if not docker_available:
        return TerrariumDetection(
            capability=TerrariumCapability.NONE,
            docker_available=False,
            error="Docker not running or not installed",
        )

    # Check Kind
    kind_path = shutil.which("kind")
    kubectl_path = shutil.which("kubectl")

    if kind_path is None:
        return TerrariumDetection(
            capability=TerrariumCapability.NONE,
            docker_available=True,
            kubectl_path=kubectl_path,
            error="Kind not installed",
        )

    # Check if cluster exists
    cluster_exists = _check_cluster_exists(cluster_name)
    if cluster_exists:
        return TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            kind_path=kind_path,
            kubectl_path=kubectl_path,
            docker_available=True,
            cluster_name=cluster_name,
        )

    # Kind available but no cluster
    return TerrariumDetection(
        capability=TerrariumCapability.KIND_AVAILABLE,
        kind_path=kind_path,
        kubectl_path=kubectl_path,
        docker_available=True,
    )


def _check_docker() -> bool:
    """
    Check if Docker daemon is running.

    Uses 'docker info' which requires the daemon to be responsive.
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # Docker CLI not installed
        return False
    except subprocess.TimeoutExpired:
        # Docker daemon not responding
        return False
    except Exception:
        return False


def _check_cluster_exists(name: str) -> bool:
    """
    Check if a Kind cluster with the given name exists.

    Args:
        name: Cluster name to check for.

    Returns:
        True if cluster exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["kind", "get", "clusters"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False

        # Parse cluster list (one per line)
        clusters = result.stdout.strip().split("\n")
        return name in clusters
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def get_cluster_container_name(cluster_name: str = "kgents-local") -> str:
    """
    Get the Docker container name for a Kind cluster's control plane.

    Kind uses a naming convention: {cluster_name}-control-plane
    """
    return f"{cluster_name}-control-plane"


def is_cluster_container_running(cluster_name: str = "kgents-local") -> bool:
    """
    Check if the cluster's Docker container is running (not paused).

    Returns:
        True if running, False if paused/stopped/missing.
    """
    container_name = get_cluster_container_name(cluster_name)
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False
        status = result.stdout.strip()
        return status == "running"
    except Exception:
        return False


def is_cluster_container_paused(cluster_name: str = "kgents-local") -> bool:
    """
    Check if the cluster's Docker container is paused.

    Returns:
        True if paused, False otherwise.
    """
    container_name = get_cluster_container_name(cluster_name)
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Paused}}", container_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False
