"""Shared fixtures for K8s tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture
def mock_docker_available():
    """Mock Docker as available."""
    with patch("infra.k8s.detection._check_docker", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_docker_unavailable():
    """Mock Docker as unavailable."""
    with patch("infra.k8s.detection._check_docker", return_value=False) as mock:
        yield mock


@pytest.fixture
def mock_kind_installed():
    """Mock Kind as installed at a path."""

    def which_side_effect(cmd: str) -> str | None:
        return {
            "kind": "/usr/local/bin/kind",
            "kubectl": "/usr/local/bin/kubectl",
            "docker": "/usr/local/bin/docker",
        }.get(cmd)

    with patch("shutil.which", side_effect=which_side_effect) as mock:
        yield mock


@pytest.fixture
def mock_kind_not_installed():
    """Mock Kind as not installed."""

    def which_side_effect(cmd: str) -> str | None:
        return {
            "kubectl": "/usr/local/bin/kubectl",
            "docker": "/usr/local/bin/docker",
        }.get(cmd)  # kind returns None

    with patch("shutil.which", side_effect=which_side_effect) as mock:
        yield mock


@pytest.fixture
def mock_cluster_exists():
    """Mock cluster as existing."""
    with patch("infra.k8s.detection._check_cluster_exists", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_cluster_not_exists():
    """Mock cluster as not existing."""
    with patch("infra.k8s.detection._check_cluster_exists", return_value=False) as mock:
        yield mock


@pytest.fixture
def test_cluster_name() -> None:
    """Unique cluster name for testing."""
    return "kgents-test-cluster"
