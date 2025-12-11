"""
Kind cluster management for K-Terrarium.

Provides create, destroy, start, stop operations for the local K8s cluster.
All operations are idempotent where possible.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from .detection import (
    TerrariumCapability,
    detect_terrarium_mode,
    get_cluster_container_name,
    is_cluster_container_paused,
    is_cluster_container_running,
)
from .exceptions import (
    ClusterNotFoundError,
    ClusterOperationError,
    DockerNotFoundError,
    KindNotFoundError,
)


class ClusterStatus(Enum):
    """Current state of the Kind cluster."""

    NOT_FOUND = auto()  # Cluster doesn't exist
    RUNNING = auto()  # Cluster running and ready
    PAUSED = auto()  # Cluster container paused (can resume)
    STOPPED = auto()  # Cluster container stopped
    ERROR = auto()  # Unknown error state


@dataclass
class ClusterConfig:
    """Configuration for the Kind cluster."""

    name: str = "kgents-local"
    image: str = "kindest/node:v1.29.0"  # Pinned for reproducibility
    wait_timeout: int = 120  # seconds to wait for cluster ready
    namespaces: list[str] = field(
        default_factory=lambda: [
            "kgents-agents",
            "kgents-ephemeral",
        ]
    )


@dataclass
class ClusterResult:
    """Result of a cluster operation."""

    success: bool
    status: ClusterStatus
    message: str
    elapsed_seconds: float = 0.0


class KindCluster:
    """
    Manages a Kind cluster for K-Terrarium.

    Provides lifecycle operations with graceful error handling.
    All operations are idempotent where possible.

    Example:
        cluster = KindCluster()
        result = cluster.create()
        if result.success:
            print(f"Cluster ready in {result.elapsed_seconds:.1f}s")
    """

    def __init__(
        self,
        config: ClusterConfig | None = None,
        on_progress: Callable[[str], None] | None = None,
    ):
        """
        Initialize cluster manager.

        Args:
            config: Cluster configuration. Uses defaults if None.
            on_progress: Callback for progress messages.
        """
        self.config = config or ClusterConfig()
        self._on_progress = on_progress or (lambda msg: None)
        self._manifests_dir = Path(__file__).parent / "manifests"

    def create(self) -> ClusterResult:
        """
        Create and configure the Kind cluster.

        Idempotent: if cluster exists, returns success without changes.

        Steps:
        1. Verify prerequisites (Docker, Kind)
        2. Create cluster with config
        3. Apply base manifests (namespaces)
        4. Wait for readiness

        Returns:
            ClusterResult with success status and timing.
        """
        start = time.perf_counter()

        # Check prerequisites
        detection = detect_terrarium_mode(self.config.name)

        if not detection.docker_available:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Docker not available. Please start Docker Desktop.",
            )

        if detection.kind_path is None:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Kind not installed. See: https://kind.sigs.k8s.io/docs/user/quick-start/",
            )

        # Check if already exists
        if detection.capability == TerrariumCapability.CLUSTER_RUNNING:
            self._on_progress(f"Cluster '{self.config.name}' already exists")
            return ClusterResult(
                success=True,
                status=ClusterStatus.RUNNING,
                message=f"Cluster '{self.config.name}' already running",
                elapsed_seconds=time.perf_counter() - start,
            )

        # Create cluster
        self._on_progress(f"Creating cluster '{self.config.name}'...")
        try:
            result = subprocess.run(
                [
                    "kind",
                    "create",
                    "cluster",
                    "--name",
                    self.config.name,
                    "--image",
                    self.config.image,
                    "--wait",
                    f"{self.config.wait_timeout}s",
                ],
                capture_output=True,
                text=True,
                timeout=self.config.wait_timeout + 30,
            )

            if result.returncode != 0:
                return ClusterResult(
                    success=False,
                    status=ClusterStatus.ERROR,
                    message=f"Failed to create cluster: {result.stderr.strip()}",
                    elapsed_seconds=time.perf_counter() - start,
                )
        except subprocess.TimeoutExpired:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Cluster creation timed out",
                elapsed_seconds=time.perf_counter() - start,
            )

        # Apply namespaces
        self._on_progress("Applying base manifests...")
        self._apply_namespaces()

        elapsed = time.perf_counter() - start
        self._on_progress(f"Cluster ready in {elapsed:.1f}s")

        return ClusterResult(
            success=True,
            status=ClusterStatus.RUNNING,
            message=f"Cluster '{self.config.name}' created and ready",
            elapsed_seconds=elapsed,
        )

    def destroy(self) -> ClusterResult:
        """
        Destroy the Kind cluster completely.

        Idempotent: if cluster doesn't exist, returns success.

        Returns:
            ClusterResult with operation status.
        """
        start = time.perf_counter()

        detection = detect_terrarium_mode(self.config.name)

        if detection.capability != TerrariumCapability.CLUSTER_RUNNING:
            return ClusterResult(
                success=True,
                status=ClusterStatus.NOT_FOUND,
                message=f"Cluster '{self.config.name}' not found (nothing to destroy)",
            )

        self._on_progress(f"Destroying cluster '{self.config.name}'...")

        try:
            result = subprocess.run(
                ["kind", "delete", "cluster", "--name", self.config.name],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                return ClusterResult(
                    success=False,
                    status=ClusterStatus.ERROR,
                    message=f"Failed to destroy cluster: {result.stderr.strip()}",
                    elapsed_seconds=time.perf_counter() - start,
                )
        except subprocess.TimeoutExpired:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Cluster destruction timed out",
                elapsed_seconds=time.perf_counter() - start,
            )

        return ClusterResult(
            success=True,
            status=ClusterStatus.NOT_FOUND,
            message=f"Cluster '{self.config.name}' destroyed",
            elapsed_seconds=time.perf_counter() - start,
        )

    def pause(self) -> ClusterResult:
        """
        Pause the cluster (docker pause).

        The cluster state is preserved and can be resumed with unpause().

        Returns:
            ClusterResult with operation status.
        """
        start = time.perf_counter()
        container_name = get_cluster_container_name(self.config.name)

        # Check if already paused
        if is_cluster_container_paused(self.config.name):
            return ClusterResult(
                success=True,
                status=ClusterStatus.PAUSED,
                message=f"Cluster '{self.config.name}' already paused",
            )

        # Check if running
        if not is_cluster_container_running(self.config.name):
            return ClusterResult(
                success=False,
                status=ClusterStatus.NOT_FOUND,
                message=f"Cluster '{self.config.name}' not running",
            )

        self._on_progress(f"Pausing cluster '{self.config.name}'...")

        try:
            result = subprocess.run(
                ["docker", "pause", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return ClusterResult(
                    success=False,
                    status=ClusterStatus.ERROR,
                    message=f"Failed to pause: {result.stderr.strip()}",
                    elapsed_seconds=time.perf_counter() - start,
                )
        except subprocess.TimeoutExpired:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Pause operation timed out",
                elapsed_seconds=time.perf_counter() - start,
            )

        return ClusterResult(
            success=True,
            status=ClusterStatus.PAUSED,
            message=f"Cluster '{self.config.name}' paused",
            elapsed_seconds=time.perf_counter() - start,
        )

    def unpause(self) -> ClusterResult:
        """
        Unpause a paused cluster (docker unpause).

        Returns:
            ClusterResult with operation status.
        """
        start = time.perf_counter()
        container_name = get_cluster_container_name(self.config.name)

        # Check if already running
        if is_cluster_container_running(self.config.name):
            return ClusterResult(
                success=True,
                status=ClusterStatus.RUNNING,
                message=f"Cluster '{self.config.name}' already running",
            )

        self._on_progress(f"Resuming cluster '{self.config.name}'...")

        try:
            result = subprocess.run(
                ["docker", "unpause", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return ClusterResult(
                    success=False,
                    status=ClusterStatus.ERROR,
                    message=f"Failed to unpause: {result.stderr.strip()}",
                    elapsed_seconds=time.perf_counter() - start,
                )
        except subprocess.TimeoutExpired:
            return ClusterResult(
                success=False,
                status=ClusterStatus.ERROR,
                message="Unpause operation timed out",
                elapsed_seconds=time.perf_counter() - start,
            )

        return ClusterResult(
            success=True,
            status=ClusterStatus.RUNNING,
            message=f"Cluster '{self.config.name}' resumed",
            elapsed_seconds=time.perf_counter() - start,
        )

    def status(self) -> ClusterStatus:
        """
        Get current cluster status.

        Returns:
            ClusterStatus enum value.
        """
        detection = detect_terrarium_mode(self.config.name)

        if detection.capability != TerrariumCapability.CLUSTER_RUNNING:
            return ClusterStatus.NOT_FOUND

        if is_cluster_container_paused(self.config.name):
            return ClusterStatus.PAUSED

        if is_cluster_container_running(self.config.name):
            return ClusterStatus.RUNNING

        return ClusterStatus.STOPPED

    def _apply_namespaces(self) -> bool:
        """
        Apply namespace manifests using kubectl.

        Returns:
            True if successful, False otherwise.
        """
        namespace_yaml = self._manifests_dir / "namespace.yaml"
        if not namespace_yaml.exists():
            self._on_progress("No namespace manifest found, skipping...")
            return True

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(namespace_yaml)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False
