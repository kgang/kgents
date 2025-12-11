"""
Tests for K-Terrarium cluster management.

Unit tests use mocks to avoid requiring Docker/Kind.
Integration tests (marked with @pytest.mark.external) require actual K8s tooling.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from infra.k8s.cluster import (
    ClusterConfig,
    ClusterResult,
    ClusterStatus,
    KindCluster,
)
from infra.k8s.detection import TerrariumCapability, TerrariumDetection


class TestClusterConfig:
    """Tests for ClusterConfig defaults."""

    def test_default_values(self):
        """Default config has expected values."""
        config = ClusterConfig()

        assert config.name == "kgents-local"
        assert "kindest/node" in config.image
        assert config.wait_timeout == 120
        assert "kgents-agents" in config.namespaces
        assert "kgents-ephemeral" in config.namespaces

    def test_custom_values(self):
        """Custom config overrides defaults."""
        config = ClusterConfig(
            name="my-cluster",
            image="kindest/node:v1.28.0",
            wait_timeout=60,
            namespaces=["my-namespace"],
        )

        assert config.name == "my-cluster"
        assert config.image == "kindest/node:v1.28.0"
        assert config.wait_timeout == 60
        assert config.namespaces == ["my-namespace"]


class TestClusterResult:
    """Tests for ClusterResult structure."""

    def test_success_result(self):
        """Success result has expected fields."""
        result = ClusterResult(
            success=True,
            status=ClusterStatus.RUNNING,
            message="Cluster created",
            elapsed_seconds=45.2,
        )

        assert result.success is True
        assert result.status == ClusterStatus.RUNNING
        assert result.message == "Cluster created"
        assert result.elapsed_seconds == 45.2

    def test_failure_result(self):
        """Failure result has expected fields."""
        result = ClusterResult(
            success=False,
            status=ClusterStatus.ERROR,
            message="Docker not available",
        )

        assert result.success is False
        assert result.status == ClusterStatus.ERROR
        assert result.elapsed_seconds == 0.0  # Default


class TestKindClusterCreate:
    """Tests for KindCluster.create()."""

    def test_create_fails_without_docker(self):
        """Create fails gracefully when Docker unavailable."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.NONE,
            docker_available=False,
            error="Docker not running",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster()
            result = cluster.create()

        assert result.success is False
        assert result.status == ClusterStatus.ERROR
        assert "Docker" in result.message

    def test_create_fails_without_kind(self):
        """Create fails gracefully when Kind not installed."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.NONE,
            docker_available=True,
            kind_path=None,
            error="Kind not installed",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster()
            result = cluster.create()

        assert result.success is False
        assert result.status == ClusterStatus.ERROR
        assert "Kind" in result.message

    def test_create_idempotent_when_exists(self):
        """Create returns success if cluster already exists."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
            cluster_name="kgents-local",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster()
            result = cluster.create()

        assert result.success is True
        assert result.status == ClusterStatus.RUNNING
        assert "already" in result.message.lower()

    def test_create_calls_kind_with_config(self):
        """Create invokes kind CLI with correct arguments."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.KIND_AVAILABLE,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
        )

        mock_subprocess = MagicMock()
        mock_subprocess.returncode = 0
        mock_subprocess.stdout = ""
        mock_subprocess.stderr = ""

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            with patch("subprocess.run", return_value=mock_subprocess) as mock_run:
                config = ClusterConfig(
                    name="test-cluster", image="kindest/node:v1.29.0"
                )
                cluster = KindCluster(config=config)
                cluster.create()

                # Verify kind create was called
                calls = [c for c in mock_run.call_args_list if "create" in str(c)]
                assert len(calls) >= 1

                # Check arguments
                create_call = calls[0]
                args = create_call[0][0]
                assert "kind" in args
                assert "create" in args
                assert "cluster" in args
                assert "--name" in args
                assert "test-cluster" in args

    def test_progress_callback_called(self):
        """Progress callback is invoked during create."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
            cluster_name="kgents-local",
        )

        progress_messages: list[str] = []

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster(on_progress=progress_messages.append)
            cluster.create()

        assert len(progress_messages) > 0


class TestKindClusterDestroy:
    """Tests for KindCluster.destroy()."""

    def test_destroy_idempotent_when_not_exists(self):
        """Destroy returns success if cluster doesn't exist."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.KIND_AVAILABLE,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster()
            result = cluster.destroy()

        assert result.success is True
        assert result.status == ClusterStatus.NOT_FOUND
        assert "not found" in result.message.lower()

    def test_destroy_calls_kind_delete(self):
        """Destroy invokes kind delete cluster."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
            cluster_name="kgents-local",
        )

        mock_subprocess = MagicMock()
        mock_subprocess.returncode = 0

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            with patch("subprocess.run", return_value=mock_subprocess) as mock_run:
                cluster = KindCluster()
                cluster.destroy()

                # Verify kind delete was called
                calls = [c for c in mock_run.call_args_list if "delete" in str(c)]
                assert len(calls) >= 1


class TestKindClusterPauseUnpause:
    """Tests for pause/unpause operations."""

    def test_pause_when_already_paused(self):
        """Pause returns success if already paused."""
        with patch("infra.k8s.cluster.is_cluster_container_paused", return_value=True):
            cluster = KindCluster()
            result = cluster.pause()

        assert result.success is True
        assert result.status == ClusterStatus.PAUSED

    def test_pause_fails_when_not_running(self):
        """Pause fails if cluster not running."""
        with patch("infra.k8s.cluster.is_cluster_container_paused", return_value=False):
            with patch(
                "infra.k8s.cluster.is_cluster_container_running", return_value=False
            ):
                cluster = KindCluster()
                result = cluster.pause()

        assert result.success is False

    def test_unpause_when_already_running(self):
        """Unpause returns success if already running."""
        with patch("infra.k8s.cluster.is_cluster_container_running", return_value=True):
            cluster = KindCluster()
            result = cluster.unpause()

        assert result.success is True
        assert result.status == ClusterStatus.RUNNING


class TestKindClusterStatus:
    """Tests for status() method."""

    def test_status_not_found(self):
        """Status returns NOT_FOUND when cluster doesn't exist."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.KIND_AVAILABLE,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            cluster = KindCluster()
            status = cluster.status()

        assert status == ClusterStatus.NOT_FOUND

    def test_status_running(self):
        """Status returns RUNNING when cluster is active."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
            cluster_name="kgents-local",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            with patch(
                "infra.k8s.cluster.is_cluster_container_paused", return_value=False
            ):
                with patch(
                    "infra.k8s.cluster.is_cluster_container_running", return_value=True
                ):
                    cluster = KindCluster()
                    status = cluster.status()

        assert status == ClusterStatus.RUNNING

    def test_status_paused(self):
        """Status returns PAUSED when cluster container is paused."""
        mock_detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            docker_available=True,
            kind_path="/usr/local/bin/kind",
            cluster_name="kgents-local",
        )

        with patch(
            "infra.k8s.cluster.detect_terrarium_mode", return_value=mock_detection
        ):
            with patch(
                "infra.k8s.cluster.is_cluster_container_paused", return_value=True
            ):
                cluster = KindCluster()
                status = cluster.status()

        assert status == ClusterStatus.PAUSED


class TestClusterStatusEnum:
    """Tests for ClusterStatus enum."""

    def test_all_statuses_exist(self):
        """All expected status values exist."""
        assert ClusterStatus.NOT_FOUND is not None
        assert ClusterStatus.RUNNING is not None
        assert ClusterStatus.PAUSED is not None
        assert ClusterStatus.STOPPED is not None
        assert ClusterStatus.ERROR is not None
