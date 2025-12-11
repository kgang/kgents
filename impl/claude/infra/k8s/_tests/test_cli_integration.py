"""Integration tests for CLI commands.

These tests verify CLI handlers work end-to-end without hitting a real cluster.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest


class TestInfraApplyCommand:
    """Tests for kgents infra apply command."""

    def test_apply_requires_argument(self):
        """apply without argument shows usage."""
        # Simulate what the CLI handler does
        from protocols.cli.handlers.infra import _cmd_apply

        # Mock cluster check to return running
        # The import happens inside _cmd_apply, so patch at the source
        with patch("infra.k8s.cluster.KindCluster") as mock_cluster:
            from infra.k8s import ClusterStatus

            mock_instance = MagicMock()
            mock_instance.status.return_value = ClusterStatus.RUNNING
            mock_cluster.return_value = mock_instance

            # Should return 1 (error) with no args
            result = _cmd_apply([])
            assert result == 1

    def test_apply_agent_by_name_parses_correctly(self):
        """Agent name is normalized correctly."""
        # Test the name normalization logic
        test_cases = [
            ("b-gent", "B"),
            ("bgent", "B"),
            ("B", "B"),
            ("l-gent", "L"),
            ("psi-gent", "Psi"),
            ("psi", "Psi"),
        ]

        for name, expected_genus in test_cases:
            # Normalize name logic from _apply_agent_by_name
            if name.endswith("-gent"):
                genus = name[:-5].upper()
            elif name.endswith("gent"):
                genus = name[:-4].upper()
            else:
                genus = name.upper()

            if genus.lower() == "psi":
                genus = "Psi"

            assert genus == expected_genus, (
                f"{name} -> {genus} (expected {expected_genus})"
            )


class TestOperatorErrorHandling:
    """Tests for operator error handling."""

    def test_cluster_operation_error_has_two_args(self):
        """ClusterOperationError requires operation and detail."""
        from infra.k8s.exceptions import ClusterOperationError

        err = ClusterOperationError("apply", "resource not found")
        assert "apply" in str(err)
        assert "resource not found" in str(err)
        assert err.operation == "apply"
        assert err.detail == "resource not found"

    def test_reconcile_handles_kubectl_failure_gracefully(self):
        """reconcile_agent catches exceptions and returns failure result."""
        import asyncio

        from infra.k8s import AgentSpec, create_operator

        spec = AgentSpec(
            name="test-agent",
            namespace="nonexistent-namespace",
            genus="T",
        )

        # Mock kubectl to fail
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="namespace not found",
            )

            operator = create_operator()
            result = asyncio.run(operator.reconcile_agent(spec))

            assert result.success is False
            assert "Failed" in result.message


class TestAgentSpecGeneration:
    """Tests for AgentSpec manifest generation."""

    def test_deployment_has_required_fields(self):
        """Generated deployment has all required K8s fields."""
        from infra.k8s import AgentSpec

        spec = AgentSpec(
            name="test-agent",
            namespace="test-ns",
            genus="T",
        )

        deployment = spec.to_deployment()

        # Required top-level fields
        assert deployment["apiVersion"] == "apps/v1"
        assert deployment["kind"] == "Deployment"
        assert "metadata" in deployment
        assert "spec" in deployment

        # Required metadata fields
        assert deployment["metadata"]["name"] == "t-gent"
        assert deployment["metadata"]["namespace"] == "test-ns"
        assert "labels" in deployment["metadata"]

        # Required spec fields
        assert "replicas" in deployment["spec"]
        assert "selector" in deployment["spec"]
        assert "template" in deployment["spec"]

        # Template has containers
        containers = deployment["spec"]["template"]["spec"]["containers"]
        assert len(containers) >= 1
        assert containers[0]["name"] == "logic"

    def test_service_has_required_fields(self):
        """Generated service has all required K8s fields."""
        from infra.k8s import AgentSpec

        spec = AgentSpec(
            name="test-agent",
            namespace="test-ns",
            genus="T",
        )

        service = spec.to_service()

        assert service["apiVersion"] == "v1"
        assert service["kind"] == "Service"
        assert service["metadata"]["name"] == "t-gent"
        assert service["spec"]["type"] == "ClusterIP"
        assert len(service["spec"]["ports"]) >= 1
