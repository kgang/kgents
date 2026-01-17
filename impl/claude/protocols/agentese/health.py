"""
AGENTESE Health Check Module.

Provides comprehensive health checking for all AGENTESE nodes and services.
Used by the gateway to monitor system health and detect issues early.

Philosophy:
    "A healthy system is a system that knows its own state."
    "Fail fast, surface early, fix immediately."

AGENTESE Paths:
- self.health.manifest   - Overall system health
- self.health.nodes      - Node-specific health
- self.health.services   - Service-specific health

See: docs/skills/unified-agentese-nodes.md
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .node import AgentMeta, Observer
from .registry import get_registry

logger = logging.getLogger(__name__)


# =============================================================================
# Health Status Enum
# =============================================================================


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class NodeHealth:
    """Health status of a single AGENTESE node."""

    path: str
    status: HealthStatus
    can_resolve: bool
    can_manifest: bool
    error: str | None = None
    latency_ms: float = 0.0
    aspects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path": self.path,
            "status": self.status.value,
            "can_resolve": self.can_resolve,
            "can_manifest": self.can_manifest,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "aspects": self.aspects,
        }


@dataclass
class ServiceHealth:
    """Health status of a service provider."""

    name: str
    status: HealthStatus
    available: bool
    error: str | None = None
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "available": self.available,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


@dataclass
class HealthReport:
    """Complete health report for AGENTESE system."""

    timestamp: datetime
    overall_status: HealthStatus
    total_nodes: int
    healthy_nodes: int
    degraded_nodes: int
    unhealthy_nodes: int
    failed_nodes: list[str]
    warnings: list[str]
    node_details: list[NodeHealth] = field(default_factory=list)
    service_details: list[ServiceHealth] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status.value,
            "total_nodes": self.total_nodes,
            "healthy_nodes": self.healthy_nodes,
            "degraded_nodes": self.degraded_nodes,
            "unhealthy_nodes": self.unhealthy_nodes,
            "failed_nodes": self.failed_nodes,
            "warnings": self.warnings,
            "node_details": [n.to_dict() for n in self.node_details],
            "service_details": [s.to_dict() for s in self.service_details],
            "duration_ms": self.duration_ms,
        }

    def to_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            "AGENTESE Health Report",
            "=" * 50,
            f"Timestamp: {self.timestamp.isoformat()}",
            f"Overall Status: {self.overall_status.value.upper()}",
            "",
            f"Total Nodes: {self.total_nodes}",
            f"  Healthy: {self.healthy_nodes}",
            f"  Degraded: {self.degraded_nodes}",
            f"  Unhealthy: {self.unhealthy_nodes}",
            "",
        ]

        if self.failed_nodes:
            lines.append("Failed Nodes:")
            for node in self.failed_nodes:
                lines.append(f"  - {node}")
            lines.append("")

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        lines.append(f"[Completed in {self.duration_ms:.1f}ms]")

        return "\n".join(lines)


# =============================================================================
# Health Check Functions
# =============================================================================


async def check_node_health(
    path: str,
    container: Any | None = None,
    observer: Observer | None = None,
) -> NodeHealth:
    """
    Check health of a single AGENTESE node.

    Args:
        path: AGENTESE path (e.g., "self.axiom")
        container: Optional service container for DI
        observer: Optional observer (uses guest if not provided)

    Returns:
        NodeHealth with status and details
    """
    if observer is None:
        observer = Observer.guest()

    registry = get_registry()
    start = time.monotonic()

    try:
        # Check if path is registered
        if not registry.has(path):
            return NodeHealth(
                path=path,
                status=HealthStatus.UNHEALTHY,
                can_resolve=False,
                can_manifest=False,
                error=f"Path not registered: {path}",
            )

        # Try to resolve the node
        node = await registry.resolve(path, container)
        if node is None:
            return NodeHealth(
                path=path,
                status=HealthStatus.UNHEALTHY,
                can_resolve=False,
                can_manifest=False,
                error=f"Node resolution returned None: {path}",
            )

        # Try to invoke manifest
        manifest_error: str | None = None
        try:
            # Use manifest method directly with AgentMeta for v1 compatibility
            meta = AgentMeta.from_observer(observer)
            result = await node.manifest(meta)  # type: ignore[arg-type]
            can_manifest = result is not None
        except Exception as e:
            can_manifest = False
            manifest_error = f"Manifest failed: {e}"

        # Get affordances
        try:
            meta = AgentMeta.from_observer(observer)
            aspects = list(node.affordances(meta))
        except Exception:
            aspects = []

        latency = (time.monotonic() - start) * 1000

        # Determine status
        if can_manifest:
            status = HealthStatus.HEALTHY
            final_error: str | None = None
        else:
            status = HealthStatus.DEGRADED
            final_error = manifest_error if manifest_error else "Cannot manifest"

        return NodeHealth(
            path=path,
            status=status,
            can_resolve=True,
            can_manifest=can_manifest,
            error=final_error,
            latency_ms=latency,
            aspects=aspects,
        )

    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return NodeHealth(
            path=path,
            status=HealthStatus.UNHEALTHY,
            can_resolve=False,
            can_manifest=False,
            error=str(e),
            latency_ms=latency,
        )


async def check_service_health(
    name: str,
    provider_fn: Any,
) -> ServiceHealth:
    """
    Check health of a service provider.

    Args:
        name: Service name (e.g., "skill_registry")
        provider_fn: Async function that returns the service

    Returns:
        ServiceHealth with status and details
    """
    start = time.monotonic()

    try:
        service = await provider_fn()
        latency = (time.monotonic() - start) * 1000

        if service is None:
            return ServiceHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                available=False,
                error="Provider returned None",
                latency_ms=latency,
            )

        return ServiceHealth(
            name=name,
            status=HealthStatus.HEALTHY,
            available=True,
            latency_ms=latency,
        )

    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return ServiceHealth(
            name=name,
            status=HealthStatus.UNHEALTHY,
            available=False,
            error=str(e),
            latency_ms=latency,
        )


async def check_agentese_health(
    paths: list[str] | None = None,
    container: Any | None = None,
    include_services: bool = True,
) -> HealthReport:
    """
    Check health of all AGENTESE nodes.

    This is the main entry point for health checking.

    Args:
        paths: Specific paths to check (all if None)
        container: Optional service container for DI
        include_services: Whether to check service providers

    Returns:
        HealthReport with comprehensive health status
    """
    start = time.monotonic()

    # Import gateway to ensure all nodes are registered
    from . import gateway

    gateway._import_node_modules()

    registry = get_registry()
    observer = Observer(archetype="developer", capabilities=frozenset({"read", "write"}))

    # Determine paths to check
    if paths is None:
        paths = registry.list_paths()

    # Check all nodes in parallel
    node_tasks = [check_node_health(path, container, observer) for path in paths]
    node_results = await asyncio.gather(*node_tasks)

    # Analyze results
    node_details = list(node_results)
    healthy_count = sum(1 for n in node_details if n.status == HealthStatus.HEALTHY)
    degraded_count = sum(1 for n in node_details if n.status == HealthStatus.DEGRADED)
    unhealthy_count = sum(1 for n in node_details if n.status == HealthStatus.UNHEALTHY)
    failed_nodes = [n.path for n in node_details if n.status == HealthStatus.UNHEALTHY]

    # Collect warnings
    warnings: list[str] = []
    for n in node_details:
        if n.status == HealthStatus.DEGRADED:
            warnings.append(f"{n.path}: {n.error}")

    # Check services if requested
    service_details: list[ServiceHealth] = []
    if include_services:
        from services import providers

        # Key services to check
        services_to_check = [
            ("skill_registry", providers.get_skill_registry),
            ("jit_injector", providers.get_jit_injector),
            ("dialectic_service", providers.get_dialectic_service),
            ("ashc_self_awareness", providers.get_ashc_self_awareness),
            ("axiom_discovery_pipeline", providers.get_axiom_discovery_pipeline),
            ("galois_service", providers.get_galois_service),
            ("fusion_service", providers.get_fusion_service),
        ]

        service_tasks = [check_service_health(name, fn) for name, fn in services_to_check]
        service_results = await asyncio.gather(*service_tasks)
        service_details = list(service_results)

        # Add service failures to warnings
        for s in service_details:
            if s.status == HealthStatus.UNHEALTHY:
                warnings.append(f"Service {s.name}: {s.error}")

    # Determine overall status
    if unhealthy_count > 0 or any(s.status == HealthStatus.UNHEALTHY for s in service_details):
        overall_status = HealthStatus.UNHEALTHY
    elif degraded_count > 0 or any(s.status == HealthStatus.DEGRADED for s in service_details):
        overall_status = HealthStatus.DEGRADED
    elif healthy_count == len(paths):
        overall_status = HealthStatus.HEALTHY
    else:
        overall_status = HealthStatus.UNKNOWN

    duration = (time.monotonic() - start) * 1000

    return HealthReport(
        timestamp=datetime.now(timezone.utc),
        overall_status=overall_status,
        total_nodes=len(paths),
        healthy_nodes=healthy_count,
        degraded_nodes=degraded_count,
        unhealthy_nodes=unhealthy_count,
        failed_nodes=failed_nodes,
        warnings=warnings,
        node_details=node_details,
        service_details=service_details,
        duration_ms=duration,
    )


async def check_unified_nodes_health(
    container: Any | None = None,
) -> HealthReport:
    """
    Check health of all new unified AGENTESE nodes.

    Specifically checks:
    - self.axiom
    - self.dialectic
    - self.skill
    - concept.fusion

    Returns:
        HealthReport for unified nodes only
    """
    unified_paths = [
        "self.axiom",
        "self.dialectic",
        "self.skill",
        "concept.fusion",
    ]

    return await check_agentese_health(
        paths=unified_paths,
        container=container,
        include_services=True,
    )


# =============================================================================
# Quick Health Check
# =============================================================================


async def quick_health() -> dict[str, Any]:
    """
    Quick health check returning essential metrics.

    Returns:
        Dict with status, node_count, healthy_count
    """
    report = await check_unified_nodes_health()

    return {
        "status": report.overall_status.value,
        "total_nodes": report.total_nodes,
        "healthy_nodes": report.healthy_nodes,
        "failed_nodes": report.failed_nodes,
        "duration_ms": report.duration_ms,
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "HealthStatus",
    # Data Classes
    "NodeHealth",
    "ServiceHealth",
    "HealthReport",
    # Functions
    "check_node_health",
    "check_service_health",
    "check_agentese_health",
    "check_unified_nodes_health",
    "quick_health",
]
