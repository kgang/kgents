"""
Infrastructure Collectors

Data collectors for various infrastructure sources:
- Kubernetes: Pods, services, deployments, events
- Docker: Containers, networks, volumes
- NATS: Subjects, streams, consumers
- OTEL: Metrics and traces

Each collector implements the BaseCollector interface for consistent
topology generation and event streaming.

@see plans/gestalt-live-infrastructure.md
@see plans/_continuations/gestalt-live-real-k8s.md
"""

from .base import BaseCollector, CollectorConfig
from .config import (
    DevelopmentK8sConfig,
    ProductionK8sConfig,
    StagingK8sConfig,
    get_collector_config,
    get_environment,
    should_use_mock,
)

__all__ = [
    # Base
    "BaseCollector",
    "CollectorConfig",
    # Config
    "ProductionK8sConfig",
    "DevelopmentK8sConfig",
    "StagingK8sConfig",
    "get_collector_config",
    "get_environment",
    "should_use_mock",
]

# Collectors are imported lazily to avoid dependency issues
# Use: from agents.infra.collectors.kubernetes import KubernetesCollector
