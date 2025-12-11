"""
Tests for K-Terrarium environment detection.

These tests use mocks to avoid requiring Docker/Kind to be installed.
"""

from __future__ import annotations

import pytest
from infra.k8s.detection import (
    TerrariumCapability,
    TerrariumDetection,
    detect_terrarium_mode,
    get_cluster_container_name,
)


class TestTerrariumDetection:
    """Tests for the TerrariumDetection dataclass."""

    def test_can_create_cluster_when_kind_available(self):
        """KIND_AVAILABLE capability allows cluster creation."""
        detection = TerrariumDetection(
            capability=TerrariumCapability.KIND_AVAILABLE,
            kind_path="/usr/local/bin/kind",
            docker_available=True,
        )
        assert detection.can_create_cluster is True
        assert detection.has_running_cluster is False

    def test_can_create_cluster_when_running(self):
        """CLUSTER_RUNNING capability allows cluster creation (idempotent)."""
        detection = TerrariumDetection(
            capability=TerrariumCapability.CLUSTER_RUNNING,
            kind_path="/usr/local/bin/kind",
            docker_available=True,
            cluster_name="kgents-local",
        )
        assert detection.can_create_cluster is True
        assert detection.has_running_cluster is True

    def test_cannot_create_cluster_when_none(self):
        """NONE capability prevents cluster creation."""
        detection = TerrariumDetection(
            capability=TerrariumCapability.NONE,
            docker_available=False,
            error="Docker not running",
        )
        assert detection.can_create_cluster is False
        assert detection.has_running_cluster is False


class TestDetectTerrariumMode:
    """Tests for the detect_terrarium_mode function."""

    def test_no_docker_returns_none_capability(self, mock_docker_unavailable):
        """When Docker is not running, capability is NONE."""
        result = detect_terrarium_mode()

        assert result.capability == TerrariumCapability.NONE
        assert result.docker_available is False
        assert result.error is not None
        assert "Docker" in result.error

    def test_docker_but_no_kind_returns_none(
        self, mock_docker_available, mock_kind_not_installed
    ):
        """When Kind is not installed, capability is NONE."""
        result = detect_terrarium_mode()

        assert result.capability == TerrariumCapability.NONE
        assert result.docker_available is True
        assert result.kind_path is None
        assert result.error is not None
        assert "Kind" in result.error

    def test_kind_available_no_cluster(
        self, mock_docker_available, mock_kind_installed, mock_cluster_not_exists
    ):
        """When Kind is installed but no cluster, capability is KIND_AVAILABLE."""
        result = detect_terrarium_mode()

        assert result.capability == TerrariumCapability.KIND_AVAILABLE
        assert result.docker_available is True
        assert result.kind_path == "/usr/local/bin/kind"
        assert result.cluster_name is None
        assert result.error is None

    def test_cluster_running(
        self, mock_docker_available, mock_kind_installed, mock_cluster_exists
    ):
        """When cluster exists, capability is CLUSTER_RUNNING."""
        result = detect_terrarium_mode("kgents-local")

        assert result.capability == TerrariumCapability.CLUSTER_RUNNING
        assert result.docker_available is True
        assert result.kind_path == "/usr/local/bin/kind"
        assert result.cluster_name == "kgents-local"
        assert result.error is None

    def test_custom_cluster_name(
        self, mock_docker_available, mock_kind_installed, mock_cluster_exists
    ):
        """Custom cluster name is passed through."""
        result = detect_terrarium_mode("my-custom-cluster")

        assert result.cluster_name == "my-custom-cluster"


class TestGetClusterContainerName:
    """Tests for container name generation."""

    def test_default_cluster_name(self):
        """Default cluster generates expected container name."""
        assert get_cluster_container_name() == "kgents-local-control-plane"

    def test_custom_cluster_name(self):
        """Custom cluster name generates expected container name."""
        assert get_cluster_container_name("my-cluster") == "my-cluster-control-plane"


class TestTerrariumCapabilityEnum:
    """Tests for the capability enum values."""

    def test_enum_values_exist(self):
        """All expected capability values exist."""
        assert TerrariumCapability.NONE is not None
        assert TerrariumCapability.KIND_AVAILABLE is not None
        assert TerrariumCapability.CLUSTER_RUNNING is not None

    def test_enum_ordering(self):
        """Capabilities can be compared (for upgrade paths)."""
        # NONE < KIND_AVAILABLE < CLUSTER_RUNNING
        assert TerrariumCapability.NONE.value < TerrariumCapability.KIND_AVAILABLE.value
        assert (
            TerrariumCapability.KIND_AVAILABLE.value
            < TerrariumCapability.CLUSTER_RUNNING.value
        )
