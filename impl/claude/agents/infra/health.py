"""
Infrastructure Health Scoring

Algorithms for calculating health scores for infrastructure entities
and aggregate topology health.

Health scores range from 0.0 (critical) to 1.0 (healthy).

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    InfraEntity,
    InfraEntityKind,
    InfraEntityStatus,
    InfraTopology,
)

# =============================================================================
# Health Thresholds
# =============================================================================


@dataclass
class HealthThresholds:
    """Configurable thresholds for health scoring."""

    # CPU thresholds (as percentage 0-100)
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0

    # Memory thresholds (as percentage 0-100)
    memory_warning: float = 80.0
    memory_critical: float = 95.0

    # Error rate thresholds (as percentage 0-100)
    error_rate_warning: float = 1.0
    error_rate_critical: float = 5.0

    # Latency thresholds (p99 in ms)
    latency_warning: float = 500.0
    latency_critical: float = 2000.0

    # NATS queue depth thresholds
    queue_depth_warning: int = 1000
    queue_depth_critical: int = 10000

    # Restart thresholds (restarts in last hour)
    restart_warning: int = 3
    restart_critical: int = 10


DEFAULT_THRESHOLDS = HealthThresholds()


# =============================================================================
# Entity Health Calculation
# =============================================================================


def calculate_entity_health(
    entity: InfraEntity,
    thresholds: HealthThresholds | None = None,
) -> float:
    """
    Calculate health score (0.0 - 1.0) for an infrastructure entity.

    The health score is a weighted average of multiple factors:
    - Status score: Is the entity in a healthy state?
    - CPU score: Is CPU utilization within acceptable limits?
    - Memory score: Is memory utilization within acceptable limits?
    - Custom metric scores: Entity-specific metrics (error rate, latency, etc.)

    Returns:
        float: Health score from 0.0 (critical) to 1.0 (healthy)
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    scores: list[tuple[float, float]] = []  # (score, weight) pairs

    # Status score (weight: 3.0 - status is very important)
    status_score = _calculate_status_score(entity.status)
    scores.append((status_score, 3.0))

    # CPU score (weight: 1.0)
    cpu_score = _calculate_resource_score(
        entity.cpu_percent,
        thresholds.cpu_warning,
        thresholds.cpu_critical,
    )
    scores.append((cpu_score, 1.0))

    # Memory score (weight: 1.5 - memory issues can be more critical)
    if entity.memory_percent is not None:
        memory_score = _calculate_resource_score(
            entity.memory_percent,
            thresholds.memory_warning,
            thresholds.memory_critical,
        )
        scores.append((memory_score, 1.5))

    # Error rate score (weight: 2.0)
    if "error_rate" in entity.custom_metrics:
        error_rate = entity.custom_metrics["error_rate"] * 100  # Convert to percentage
        error_score = _calculate_resource_score(
            error_rate,
            thresholds.error_rate_warning,
            thresholds.error_rate_critical,
        )
        scores.append((error_score, 2.0))

    # Latency score (weight: 1.0)
    if "latency_p99" in entity.custom_metrics:
        latency_score = _calculate_resource_score(
            entity.custom_metrics["latency_p99"],
            thresholds.latency_warning,
            thresholds.latency_critical,
        )
        scores.append((latency_score, 1.0))

    # Queue depth score for NATS (weight: 1.5)
    if entity.kind in (InfraEntityKind.NATS_SUBJECT, InfraEntityKind.NATS_STREAM):
        if "queue_depth" in entity.custom_metrics:
            queue_score = _calculate_resource_score(
                entity.custom_metrics["queue_depth"],
                float(thresholds.queue_depth_warning),
                float(thresholds.queue_depth_critical),
            )
            scores.append((queue_score, 1.5))

    # Restart count score for pods/containers (weight: 1.5)
    if entity.kind in (InfraEntityKind.POD, InfraEntityKind.CONTAINER):
        if "restart_count" in entity.custom_metrics:
            restart_score = _calculate_resource_score(
                entity.custom_metrics["restart_count"],
                float(thresholds.restart_warning),
                float(thresholds.restart_critical),
            )
            scores.append((restart_score, 1.5))

    # Calculate weighted average
    if not scores:
        return 1.0

    total_weight = sum(weight for _, weight in scores)
    weighted_sum = sum(score * weight for score, weight in scores)

    return weighted_sum / total_weight


def _calculate_status_score(status: InfraEntityStatus) -> float:
    """Calculate health score contribution from entity status."""
    status_scores = {
        # Healthy states
        InfraEntityStatus.RUNNING: 1.0,
        InfraEntityStatus.SUCCEEDED: 1.0,
        InfraEntityStatus.ACTIVE: 1.0,
        # Pending/transitional states
        InfraEntityStatus.PENDING: 0.7,
        InfraEntityStatus.CREATED: 0.7,
        InfraEntityStatus.RESTARTING: 0.5,
        InfraEntityStatus.TERMINATING: 0.5,
        InfraEntityStatus.PAUSED: 0.6,
        InfraEntityStatus.INACTIVE: 0.6,
        # Unhealthy states
        InfraEntityStatus.FAILED: 0.0,
        InfraEntityStatus.EXITED: 0.3,
        InfraEntityStatus.DEAD: 0.0,
        InfraEntityStatus.UNKNOWN: 0.5,
    }
    return status_scores.get(status, 0.5)


def _calculate_resource_score(
    value: float,
    warning_threshold: float,
    critical_threshold: float,
) -> float:
    """
    Calculate health score for a resource metric.

    Returns 1.0 if below warning, scales to 0.5 at warning,
    and 0.0 at or above critical.
    """
    if value >= critical_threshold:
        return 0.0
    elif value >= warning_threshold:
        # Linear interpolation from 0.5 (at warning) to 0.0 (at critical)
        ratio = (value - warning_threshold) / (critical_threshold - warning_threshold)
        return 0.5 * (1 - ratio)
    else:
        # Linear interpolation from 1.0 (at 0) to 0.5 (at warning)
        ratio = value / warning_threshold
        return 1.0 - 0.5 * ratio


# =============================================================================
# Topology Health Calculation
# =============================================================================


def calculate_topology_health(
    topology: InfraTopology,
    thresholds: HealthThresholds | None = None,
) -> dict:
    """
    Calculate aggregate health metrics for an infrastructure topology.

    Returns a dictionary with:
    - overall: Average health score across all entities
    - healthy: Count of entities with health >= 0.8
    - warning: Count of entities with 0.5 <= health < 0.8
    - critical: Count of entities with health < 0.5
    - by_kind: Health breakdown by entity kind
    - by_namespace: Health breakdown by namespace
    - worst_entities: List of lowest-health entities
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    # Recalculate health for all entities (in case thresholds changed)
    healths = []
    for entity in topology.entities:
        health = calculate_entity_health(entity, thresholds)
        healths.append((entity, health))

    # Calculate counts
    healthy_count = sum(1 for _, h in healths if h >= 0.8)
    warning_count = sum(1 for _, h in healths if 0.5 <= h < 0.8)
    critical_count = sum(1 for _, h in healths if h < 0.5)

    # Calculate by-kind breakdown
    by_kind: dict[str, dict] = {}
    for entity, health in healths:
        kind = entity.kind.value
        if kind not in by_kind:
            by_kind[kind] = {"count": 0, "total_health": 0.0}
        by_kind[kind]["count"] += 1
        by_kind[kind]["total_health"] += health

    for kind in by_kind:
        count = by_kind[kind]["count"]
        by_kind[kind]["average_health"] = (
            by_kind[kind]["total_health"] / count if count > 0 else 1.0
        )
        del by_kind[kind]["total_health"]

    # Calculate by-namespace breakdown
    by_namespace: dict[str, dict] = {}
    for entity, health in healths:
        ns = entity.namespace or "(none)"
        if ns not in by_namespace:
            by_namespace[ns] = {"count": 0, "total_health": 0.0}
        by_namespace[ns]["count"] += 1
        by_namespace[ns]["total_health"] += health

    for ns in by_namespace:
        count = by_namespace[ns]["count"]
        by_namespace[ns]["average_health"] = (
            by_namespace[ns]["total_health"] / count if count > 0 else 1.0
        )
        del by_namespace[ns]["total_health"]

    # Find worst entities
    worst_entities = sorted(healths, key=lambda x: x[1])[:10]

    return {
        "overall": sum(h for _, h in healths) / len(healths) if healths else 1.0,
        "healthy": healthy_count,
        "warning": warning_count,
        "critical": critical_count,
        "total": len(healths),
        "by_kind": by_kind,
        "by_namespace": by_namespace,
        "worst_entities": [
            {
                "id": e.id,
                "name": e.display_name,
                "kind": e.kind.value,
                "health": h,
                "status": e.status.value,
            }
            for e, h in worst_entities
        ],
    }


# =============================================================================
# Health Grade Utilities
# =============================================================================


def health_to_grade(health: float) -> str:
    """Convert health score to letter grade."""
    if health >= 0.95:
        return "A+"
    elif health >= 0.9:
        return "A"
    elif health >= 0.85:
        return "B+"
    elif health >= 0.8:
        return "B"
    elif health >= 0.7:
        return "C+"
    elif health >= 0.6:
        return "C"
    elif health >= 0.4:
        return "D"
    else:
        return "F"


def grade_to_color(grade: str) -> str:
    """Get color for health grade (hex)."""
    colors = {
        "A+": "#22c55e",  # Green
        "A": "#4ade80",
        "B+": "#86efac",
        "B": "#fde047",  # Yellow
        "C+": "#facc15",
        "C": "#f97316",  # Orange
        "D": "#ef4444",  # Red
        "F": "#dc2626",
    }
    return colors.get(grade, "#6b7280")
