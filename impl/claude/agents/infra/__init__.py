"""
Infrastructure Monitoring Agent

Live infrastructure visualization for Kubernetes, Docker, NATS, and more.

This module provides:
- Data models for infrastructure entities (pods, containers, subjects)
- Collectors for various infrastructure sources
- Health scoring algorithms
- Real-time topology streaming

@see plans/gestalt-live-infrastructure.md
"""

from .health import (
    HealthThresholds,
    calculate_entity_health,
    calculate_topology_health,
)
from .models import (
    InfraConnection,
    InfraConnectionKind,
    InfraEntity,
    InfraEntityKind,
    InfraEntityStatus,
    InfraEvent,
    InfraEventSeverity,
    InfraTopology,
)

__all__ = [
    # Entity types
    "InfraEntityKind",
    "InfraEntityStatus",
    "InfraEntity",
    # Connection types
    "InfraConnectionKind",
    "InfraConnection",
    # Topology
    "InfraTopology",
    # Events
    "InfraEvent",
    "InfraEventSeverity",
    # Health
    "calculate_entity_health",
    "calculate_topology_health",
    "HealthThresholds",
]
