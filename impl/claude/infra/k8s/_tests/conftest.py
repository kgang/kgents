"""Shared fixtures for K8s tests."""

from __future__ import annotations

from typing import Any, Generator
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_docker_available() -> Generator[Any, None, None]:
    """Mock Docker as available."""
    with patch("infra.k8s.detection._check_docker", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_docker_unavailable() -> Generator[Any, None, None]:
    """Mock Docker as unavailable."""
    with patch("infra.k8s.detection._check_docker", return_value=False) as mock:
        yield mock


@pytest.fixture
def mock_kind_installed() -> Any:
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
def mock_kind_not_installed() -> Any:
    """Mock Kind as not installed."""

    def which_side_effect(cmd: str) -> str | None:
        return {
            "kubectl": "/usr/local/bin/kubectl",
            "docker": "/usr/local/bin/docker",
        }.get(cmd)  # kind returns None

    with patch("shutil.which", side_effect=which_side_effect) as mock:
        yield mock


@pytest.fixture
def mock_cluster_exists() -> Generator[Any, None, None]:
    """Mock cluster as existing."""
    with patch("infra.k8s.detection._check_cluster_exists", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_cluster_not_exists() -> Generator[Any, None, None]:
    """Mock cluster as not existing."""
    with patch("infra.k8s.detection._check_cluster_exists", return_value=False) as mock:
        yield mock


@pytest.fixture
def test_cluster_name() -> Any:
    """Unique cluster name for testing."""
    return "kgents-test-cluster"
