"""
Tests for Kubernetes Collector Configuration.

@see impl/claude/agents/infra/collectors/config.py
@see plans/_continuations/gestalt-live-real-k8s.md
"""

from __future__ import annotations

import os
from unittest import mock

import pytest

from ..config import (
    DevelopmentK8sConfig,
    ProductionK8sConfig,
    StagingK8sConfig,
    filter_namespaces,
    get_collector_config,
    get_environment,
    get_excluded_namespaces,
    should_use_mock,
)
from ..kubernetes import KubernetesConfig


class TestGetEnvironment:
    """Tests for environment detection."""

    def test_default_is_development(self) -> None:
        """Without KGENTS_ENV, defaults to development."""
        with mock.patch.dict(os.environ, {}, clear=True):
            # Clear KGENTS_ENV if present
            os.environ.pop("KGENTS_ENV", None)
            assert get_environment() == "development"

    def test_development(self) -> None:
        """KGENTS_ENV=development."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "development"}):
            assert get_environment() == "development"

    def test_staging(self) -> None:
        """KGENTS_ENV=staging."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "staging"}):
            assert get_environment() == "staging"

    def test_production(self) -> None:
        """KGENTS_ENV=production."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "production"}):
            assert get_environment() == "production"

    def test_test(self) -> None:
        """KGENTS_ENV=test."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "test"}):
            assert get_environment() == "test"

    def test_invalid_falls_back_to_development(self) -> None:
        """Invalid environment falls back to development."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "invalid"}):
            assert get_environment() == "development"


class TestShouldUseMock:
    """Tests for mock mode detection."""

    def test_explicit_mock_true(self) -> None:
        """GESTALT_USE_MOCK=true enables mock mode."""
        with mock.patch.dict(os.environ, {"GESTALT_USE_MOCK": "true"}):
            assert should_use_mock() is True

    def test_explicit_mock_false(self) -> None:
        """GESTALT_USE_MOCK=false disables mock mode."""
        with mock.patch.dict(
            os.environ, {"GESTALT_USE_MOCK": "false", "KGENTS_ENV": "production"}
        ):
            assert should_use_mock() is False

    def test_test_env_enables_mock(self) -> None:
        """KGENTS_ENV=test enables mock mode."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "test"}, clear=True):
            os.environ.pop("GESTALT_USE_MOCK", None)
            assert should_use_mock() is True

    def test_production_env_disables_mock(self) -> None:
        """KGENTS_ENV=production disables mock mode (unless explicit)."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "production"}, clear=True):
            os.environ.pop("GESTALT_USE_MOCK", None)
            assert should_use_mock() is False


class TestGetCollectorConfig:
    """Tests for config factory."""

    def test_production_config(self) -> None:
        """Production environment returns ProductionK8sConfig."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "production"}):
            config = get_collector_config()
            assert isinstance(config, ProductionK8sConfig)

    def test_staging_config(self) -> None:
        """Staging environment returns StagingK8sConfig."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "staging"}):
            config = get_collector_config()
            assert isinstance(config, StagingK8sConfig)

    def test_development_config(self) -> None:
        """Development environment returns DevelopmentK8sConfig."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "development"}):
            config = get_collector_config()
            assert isinstance(config, DevelopmentK8sConfig)

    def test_test_config(self) -> None:
        """Test environment returns minimal KubernetesConfig."""
        with mock.patch.dict(os.environ, {"KGENTS_ENV": "test"}):
            config = get_collector_config()
            assert isinstance(config, KubernetesConfig)
            assert config.namespaces == ["test-namespace"]
            assert config.collect_metrics is False


class TestProductionK8sConfig:
    """Tests for production configuration."""

    def test_defaults(self) -> None:
        """Production config has sensible defaults."""
        config = ProductionK8sConfig()

        # Default namespaces - kgents cluster namespaces
        assert "kgents-triad" in config.namespaces
        assert "kgents-agents" in config.namespaces
        assert "default" in config.namespaces

        # Resource collection
        assert config.collect_pods is True
        assert config.collect_services is True
        assert config.collect_deployments is True
        assert config.collect_configmaps is False  # Too noisy
        assert config.collect_secrets is False  # Security risk

        # Metrics
        assert config.collect_metrics is True

        # Polling
        assert config.poll_interval == 5.0

    def test_no_kubeconfig_for_in_cluster(self) -> None:
        """Production should use in-cluster config by default."""
        config = ProductionK8sConfig()
        assert config.kubeconfig is None


class TestDevelopmentK8sConfig:
    """Tests for development configuration."""

    def test_defaults(self) -> None:
        """Development config has dev-friendly defaults."""
        config = DevelopmentK8sConfig()

        # Default namespaces - kgents cluster namespaces
        assert "kgents-triad" in config.namespaces
        assert "kgents-agents" in config.namespaces
        assert "default" in config.namespaces

        # Resource collection (more permissive for debugging)
        assert config.collect_pods is True
        assert config.collect_services is True
        assert config.collect_deployments is True
        assert config.collect_configmaps is True  # Useful for debugging
        assert config.collect_secrets is False  # Still dangerous

        # Faster polling for dev
        assert config.poll_interval == 3.0

    def test_uses_kubeconfig(self) -> None:
        """Development should use kubeconfig file."""
        config = DevelopmentK8sConfig()
        assert config.kubeconfig is not None

    def test_respects_env_vars(self) -> None:
        """Development config respects KUBECONFIG and KUBE_CONTEXT."""
        with mock.patch.dict(
            os.environ,
            {
                "KUBECONFIG": "/custom/kubeconfig",
                "KUBE_CONTEXT": "my-context",
            },
        ):
            config = DevelopmentK8sConfig()
            assert config.kubeconfig == "/custom/kubeconfig"
            assert config.context == "my-context"


class TestNamespaceUtilities:
    """Tests for namespace filtering utilities."""

    def test_excluded_namespaces(self) -> None:
        """Excluded namespaces include system namespaces."""
        excluded = get_excluded_namespaces()

        assert "kube-system" in excluded
        assert "kube-public" in excluded
        assert "kube-node-lease" in excluded

    def test_filter_excludes_system(self) -> None:
        """filter_namespaces removes system namespaces by default."""
        namespaces = ["default", "kgents", "kube-system", "kube-public"]
        filtered = filter_namespaces(namespaces)

        assert "default" in filtered
        assert "kgents" in filtered
        assert "kube-system" not in filtered
        assert "kube-public" not in filtered

    def test_filter_can_include_system(self) -> None:
        """filter_namespaces can include system namespaces."""
        namespaces = ["default", "kube-system"]
        filtered = filter_namespaces(namespaces, exclude_system=False)

        assert "default" in filtered
        assert "kube-system" in filtered
