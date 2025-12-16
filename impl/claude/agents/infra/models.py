"""
Infrastructure Data Models

Core data models for live infrastructure monitoring in Gestalt.

These models represent:
- Infrastructure entities (pods, containers, services, etc.)
- Connections between entities (network, messaging, storage)
- Topology snapshots with aggregated metrics
- Real-time events from infrastructure sources

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# =============================================================================
# Entity Types
# =============================================================================


class InfraEntityKind(str, Enum):
    """Types of infrastructure entities we can visualize."""

    # Kubernetes resources
    NAMESPACE = "namespace"
    NODE = "node"
    POD = "pod"
    SERVICE = "service"
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    DAEMONSET = "daemonset"
    INGRESS = "ingress"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    PVC = "pvc"  # Persistent Volume Claim

    # Docker resources
    CONTAINER = "container"
    NETWORK = "network"
    VOLUME = "volume"
    IMAGE = "image"

    # NATS resources
    NATS_SERVER = "nats_server"
    NATS_SUBJECT = "nats_subject"
    NATS_STREAM = "nats_stream"
    NATS_CONSUMER = "nats_consumer"

    # Databases
    DATABASE = "database"
    DATABASE_CONNECTION = "database_connection"

    # Generic
    CUSTOM = "custom"


class InfraEntityStatus(str, Enum):
    """Runtime status of an infrastructure entity."""

    RUNNING = "running"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TERMINATING = "terminating"
    UNKNOWN = "unknown"

    # Docker specific
    CREATED = "created"
    RESTARTING = "restarting"
    PAUSED = "paused"
    EXITED = "exited"
    DEAD = "dead"

    # NATS specific
    ACTIVE = "active"
    INACTIVE = "inactive"


# =============================================================================
# Infrastructure Entity
# =============================================================================


@dataclass
class InfraEntity:
    """
    A single infrastructure entity (pod, container, subject, etc.).

    This is the node in our infrastructure graph. Each entity has:
    - Identity: id, kind, name, namespace
    - State: status, health score
    - Metrics: CPU, memory, network, custom
    - Position: x, y, z (calculated by layout algorithm)
    """

    # Identity
    id: str
    kind: InfraEntityKind
    name: str
    namespace: str | None = None

    # Metadata
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    # State
    status: InfraEntityStatus = InfraEntityStatus.UNKNOWN
    status_message: str | None = None
    health: float = 1.0  # 0.0 (critical) to 1.0 (healthy)

    # Resource metrics
    cpu_percent: float = 0.0
    cpu_limit: float | None = None  # millicores
    memory_bytes: int = 0
    memory_limit: int | None = None  # bytes
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0
    network_rx_rate: float = 0.0  # bytes/sec
    network_tx_rate: float = 0.0  # bytes/sec

    # Custom metrics (entity-specific)
    custom_metrics: dict[str, float] = field(default_factory=dict)

    # Relationships (for hierarchy display)
    parent_id: str | None = None
    owner_kind: str | None = None
    owner_name: str | None = None

    # Position (set by layout algorithm)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Source metadata
    source: str = "unknown"  # kubernetes, docker, nats, etc.
    source_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure id is properly formatted."""
        if not self.id:
            # Generate id from kind/namespace/name
            parts = [self.kind.value]
            if self.namespace:
                parts.append(self.namespace)
            parts.append(self.name)
            self.id = "/".join(parts)

    @property
    def display_name(self) -> str:
        """Human-readable name for display."""
        if self.namespace:
            return f"{self.namespace}/{self.name}"
        return self.name

    @property
    def health_grade(self) -> str:
        """Convert health score to letter grade."""
        if self.health >= 0.95:
            return "A+"
        elif self.health >= 0.9:
            return "A"
        elif self.health >= 0.85:
            return "B+"
        elif self.health >= 0.8:
            return "B"
        elif self.health >= 0.7:
            return "C+"
        elif self.health >= 0.6:
            return "C"
        elif self.health >= 0.4:
            return "D"
        else:
            return "F"

    @property
    def memory_percent(self) -> float | None:
        """Memory utilization as percentage."""
        if self.memory_limit and self.memory_limit > 0:
            return (self.memory_bytes / self.memory_limit) * 100
        return None


# =============================================================================
# Connection Types
# =============================================================================


class InfraConnectionKind(str, Enum):
    """Types of connections between infrastructure entities."""

    # Network connections
    NETWORK = "network"  # Generic network connectivity
    HTTP = "http"  # HTTP/REST traffic
    GRPC = "grpc"  # gRPC calls
    TCP = "tcp"  # Raw TCP
    UDP = "udp"  # Raw UDP

    # Messaging
    NATS = "nats"  # NATS pub/sub
    NATS_REQUEST = "nats_request"  # NATS request/reply

    # Storage
    VOLUME = "volume"  # Volume mount
    DATABASE = "database"  # Database connection

    # Kubernetes relationships
    OWNS = "owns"  # Ownership (deployment → pod)
    SELECTS = "selects"  # Label selector (service → pod)
    CONFIGURES = "configures"  # ConfigMap/Secret mount

    # Dependencies
    DEPENDS = "depends"  # Generic dependency


@dataclass
class InfraConnection:
    """
    A connection between two infrastructure entities.

    This is the edge in our infrastructure graph. Connections have:
    - Endpoints: source and target entity IDs
    - Type: what kind of connection (network, messaging, storage)
    - Metrics: throughput, latency, error rate
    """

    source_id: str
    target_id: str
    kind: InfraConnectionKind

    # Metrics (for animated edges)
    requests_per_sec: float = 0.0
    bytes_per_sec: float = 0.0
    error_rate: float = 0.0  # 0.0 to 1.0
    latency_p50_ms: float = 0.0
    latency_p99_ms: float = 0.0

    # For NATS connections
    pending_messages: int = 0
    delivered_messages: int = 0

    # Connection state
    is_healthy: bool = True
    last_activity: datetime | None = None

    # Display hints
    bidirectional: bool = False
    animated: bool = False

    @property
    def id(self) -> str:
        """Unique identifier for this connection."""
        return f"{self.source_id}->{self.target_id}:{self.kind.value}"


# =============================================================================
# Topology Snapshot
# =============================================================================


@dataclass
class InfraTopology:
    """
    Complete infrastructure topology snapshot.

    This is what we send to the frontend for visualization. It contains:
    - All entities (nodes)
    - All connections (edges)
    - Aggregate statistics
    - Timestamp for freshness
    """

    entities: list[InfraEntity]
    connections: list[InfraConnection]
    timestamp: datetime

    # Aggregate statistics
    total_entities: int = 0
    healthy_count: int = 0
    warning_count: int = 0
    critical_count: int = 0

    # By-kind breakdowns
    entities_by_kind: dict[str, int] = field(default_factory=dict)
    entities_by_namespace: dict[str, int] = field(default_factory=dict)

    # Overall health (0.0 to 1.0)
    overall_health: float = 1.0

    def __post_init__(self) -> None:
        """Calculate aggregate statistics."""
        self.total_entities = len(self.entities)

        # Count by health level
        for entity in self.entities:
            if entity.health >= 0.8:
                self.healthy_count += 1
            elif entity.health >= 0.5:
                self.warning_count += 1
            else:
                self.critical_count += 1

        # Count by kind
        for entity in self.entities:
            kind = entity.kind.value
            self.entities_by_kind[kind] = self.entities_by_kind.get(kind, 0) + 1

        # Count by namespace
        for entity in self.entities:
            ns = entity.namespace or "(none)"
            self.entities_by_namespace[ns] = self.entities_by_namespace.get(ns, 0) + 1

        # Calculate overall health
        if self.entities:
            self.overall_health = sum(e.health for e in self.entities) / len(
                self.entities
            )


# =============================================================================
# Events
# =============================================================================


class InfraEventSeverity(str, Enum):
    """Severity levels for infrastructure events."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class InfraEvent:
    """
    An infrastructure event (pod restart, deployment update, etc.).

    Events are streamed to the frontend for the event feed.
    """

    id: str
    type: str  # "Normal", "Warning", etc. (K8s) or custom
    reason: str  # "Started", "Killed", "FailedScheduling", etc.
    message: str
    severity: InfraEventSeverity

    # Associated entity
    entity_id: str
    entity_kind: InfraEntityKind
    entity_name: str
    entity_namespace: str | None = None

    # Timestamps
    timestamp: datetime = field(default_factory=datetime.utcnow)
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    count: int = 1

    # Source
    source: str = "unknown"
    source_component: str | None = None
    source_host: str | None = None

    @classmethod
    def from_kubernetes_event(cls, k8s_event: dict) -> InfraEvent:
        """Create from a Kubernetes event object."""
        involved = k8s_event.get("involvedObject", {})

        severity = InfraEventSeverity.INFO
        if k8s_event.get("type") == "Warning":
            severity = InfraEventSeverity.WARNING
        if "fail" in k8s_event.get("reason", "").lower():
            severity = InfraEventSeverity.ERROR

        return cls(
            id=k8s_event.get("metadata", {}).get("uid", ""),
            type=k8s_event.get("type", "Normal"),
            reason=k8s_event.get("reason", "Unknown"),
            message=k8s_event.get("message", ""),
            severity=severity,
            entity_id=f"{involved.get('kind', 'Unknown').lower()}/{involved.get('namespace', 'default')}/{involved.get('name', 'unknown')}",
            entity_kind=InfraEntityKind(involved.get("kind", "custom").lower()),
            entity_name=involved.get("name", "unknown"),
            entity_namespace=involved.get("namespace"),
            timestamp=datetime.fromisoformat(
                k8s_event.get("lastTimestamp", datetime.utcnow().isoformat()).replace(
                    "Z", "+00:00"
                )
            ),
            count=k8s_event.get("count", 1),
            source="kubernetes",
            source_component=k8s_event.get("source", {}).get("component"),
            source_host=k8s_event.get("source", {}).get("host"),
        )


# =============================================================================
# Topology Updates (for streaming)
# =============================================================================


class TopologyUpdateKind(str, Enum):
    """Types of topology updates."""

    FULL = "full"  # Complete topology replacement
    ENTITY_ADDED = "entity_added"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_REMOVED = "entity_removed"
    CONNECTION_ADDED = "connection_added"
    CONNECTION_UPDATED = "connection_updated"
    CONNECTION_REMOVED = "connection_removed"
    METRICS = "metrics"  # Metrics-only update


@dataclass
class TopologyUpdate:
    """
    An incremental topology update.

    Sent via SSE to update the frontend without full refresh.
    """

    kind: TopologyUpdateKind
    timestamp: datetime

    # For entity updates
    entity: InfraEntity | None = None

    # For connection updates
    connection: InfraConnection | None = None

    # For full updates
    topology: InfraTopology | None = None

    # For metrics updates (entity_id → metrics dict)
    metrics: dict[str, dict[str, float]] | None = None
