"""
Production Kubernetes Configuration

Environment-aware configuration for Gestalt Live infrastructure collectors.

Supports:
- Local development (kubeconfig file)
- Production (in-cluster config via ServiceAccount)
- Test (mock collector)

@see plans/_continuations/gestalt-live-real-k8s.md
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

from .kubernetes import KubernetesConfig

# =============================================================================
# Environment Detection
# =============================================================================


KgentsEnv = Literal["development", "staging", "production", "test"]


def get_environment() -> KgentsEnv:
    """Detect current environment from KGENTS_ENV."""
    env = os.getenv("KGENTS_ENV", "development")
    if env in ("development", "staging", "production", "test"):
        return env  # type: ignore[return-value]
    return "development"


# =============================================================================
# Production Configuration
# =============================================================================


@dataclass
class ProductionK8sConfig(KubernetesConfig):
    """
    Production Kubernetes configuration for kgents cluster.

    This config is used when KGENTS_ENV=production or when running
    in-cluster with a ServiceAccount.

    Usage:
        config = ProductionK8sConfig()
        collector = KubernetesCollector(config)
    """

    # Connection - use in-cluster config when deployed, kubeconfig locally
    kubeconfig: str | None = None  # Set via env var for local dev
    context: str | None = None  # Set via env var for multi-cluster

    # Namespaces to monitor
    # Empty list = all namespaces (dangerous in production!)
    # Explicit list = only these namespaces
    namespaces: list[str] = field(
        default_factory=lambda: [
            "kgents-triad",  # Main application services
            "kgents-agents",  # NATS cluster
            "kgents-gateway",  # Kong gateway
            "kgents-observability",  # Monitoring stack
            "default",  # Default namespace
        ]
    )

    # Resource collection flags - what to collect
    collect_pods: bool = True
    collect_services: bool = True
    collect_deployments: bool = True
    collect_configmaps: bool = False  # Usually too noisy
    collect_secrets: bool = False  # Security risk - never enable in prod

    # Metrics collection (requires metrics-server)
    collect_metrics: bool = True

    # Polling configuration
    poll_interval: float = 5.0  # 5 seconds for real-time feel

    # Layout configuration
    calculate_positions: bool = True
    layout_iterations: int = 50

    # Watch-based updates (more efficient than polling)
    use_watches: bool = False  # Enable when ready for event-driven updates


@dataclass
class DevelopmentK8sConfig(KubernetesConfig):
    """
    Development Kubernetes configuration.

    Uses kubeconfig file and supports context switching for
    multi-cluster local development (e.g., Kind, minikube, Docker Desktop).
    """

    kubeconfig: str | None = field(
        default_factory=lambda: os.getenv("KUBECONFIG", "~/.kube/config")
    )
    context: str | None = field(default_factory=lambda: os.getenv("KUBE_CONTEXT"))

    # Development namespaces - monitor main kgents namespaces
    namespaces: list[str] = field(
        default_factory=lambda: [
            "kgents-triad",  # Main application services
            "kgents-agents",  # NATS cluster
            "kgents-gateway",  # Kong gateway
            "kgents-observability",  # Monitoring stack
            "default",  # Default namespace
        ]
    )

    # Enable all collection for debugging
    collect_pods: bool = True
    collect_services: bool = True
    collect_deployments: bool = True
    collect_configmaps: bool = True  # Useful for debugging
    collect_secrets: bool = False  # Still dangerous

    # Metrics if available
    collect_metrics: bool = True

    # Faster polling for development
    poll_interval: float = 3.0


@dataclass
class StagingK8sConfig(KubernetesConfig):
    """
    Staging Kubernetes configuration.

    Similar to production but may monitor additional namespaces
    for pre-release testing.
    """

    namespaces: list[str] = field(
        default_factory=lambda: [
            "kgents-staging",
            "default",
        ]
    )

    collect_pods: bool = True
    collect_services: bool = True
    collect_deployments: bool = True
    collect_configmaps: bool = False
    collect_secrets: bool = False
    collect_metrics: bool = True

    poll_interval: float = 5.0


# =============================================================================
# Configuration Factory
# =============================================================================


def get_collector_config() -> KubernetesConfig:
    """
    Get collector configuration based on environment.

    Environment detection order:
    1. KGENTS_ENV environment variable
    2. GESTALT_USE_MOCK for explicit mock mode
    3. Default to development

    Returns:
        KubernetesConfig appropriate for the detected environment.

    Example:
        # In production (container with ServiceAccount)
        export KGENTS_ENV=production
        config = get_collector_config()  # Returns ProductionK8sConfig

        # Local development
        export KGENTS_ENV=development
        export KUBECONFIG=~/.kube/config
        export KUBE_CONTEXT=kind-kgents-triad
        config = get_collector_config()  # Returns DevelopmentK8sConfig
    """
    env = get_environment()

    if env == "production":
        return ProductionK8sConfig()
    elif env == "staging":
        return StagingK8sConfig()
    elif env == "test":
        # For tests, return a minimal config
        return KubernetesConfig(
            namespaces=["test-namespace"],
            collect_pods=True,
            collect_services=True,
            collect_deployments=True,
            collect_configmaps=False,
            collect_secrets=False,
            collect_metrics=False,
        )
    else:
        # Development
        return DevelopmentK8sConfig()


def should_use_mock() -> bool:
    """
    Determine if mock collector should be used.

    Mock is used when:
    1. GESTALT_USE_MOCK=true (explicit)
    2. KGENTS_ENV=test

    Returns:
        True if mock collector should be used.
    """
    if os.getenv("GESTALT_USE_MOCK", "").lower() == "true":
        return True
    if get_environment() == "test":
        return True
    return False


# =============================================================================
# Namespace Utilities
# =============================================================================


def get_excluded_namespaces() -> set[str]:
    """
    Namespaces that should typically be excluded from monitoring.

    These are Kubernetes system namespaces that are usually noisy
    and not relevant to application monitoring.
    """
    return {
        "kube-system",
        "kube-public",
        "kube-node-lease",
        "local-path-storage",  # Kind storage
        "ingress-nginx",  # Ingress controller
    }


def filter_namespaces(
    namespaces: list[str],
    exclude_system: bool = True,
) -> list[str]:
    """
    Filter namespace list, optionally excluding system namespaces.

    Args:
        namespaces: List of namespaces to filter.
        exclude_system: Whether to exclude Kubernetes system namespaces.

    Returns:
        Filtered list of namespaces.
    """
    if not exclude_system:
        return namespaces

    excluded = get_excluded_namespaces()
    return [ns for ns in namespaces if ns not in excluded]
