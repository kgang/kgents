---
path: plans/architecture/live-infrastructure
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Live Infrastructure Plan: The Database Triad

> *"YAML is generated, not written. The spec is the source of truth."* — Spec-Driven Infrastructure Principle

**Status**: Implementation Plan
**Date**: 2025-12-12
**Kent's Choices**: PostgreSQL + Redis + Qdrant | OTel + Custom | Deep Integration | Visual Dashboards

---

## Overview

This plan instantiates live infrastructure in Terrarium following the categorical principles. The Database Triad is a **coproduct**:

```
DB = Postgres ⊕ Redis ⊕ Qdrant
```

Each database is a specialized functor:
- **Postgres**: Relations → State (ACID, source of truth)
- **Redis**: Keys → State (cache, pub/sub, sessions)
- **Qdrant**: Vectors → State (embeddings, semantic search)

---

## Phase 1: CRDs and Operators

### 1.1 PostgreSQL CRD

```yaml
# impl/claude/infra/k8s/crds/postgres-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.kgents.io
spec:
  group: kgents.io
  names:
    kind: PostgresCluster
    listKind: PostgresClusterList
    plural: postgresclusters
    singular: postgrescluster
    shortNames:
      - pg
  scope: Namespaced
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              required:
                - database
              properties:
                database:
                  type: string
                  description: Database name
                replicas:
                  type: integer
                  default: 1
                  minimum: 1
                  maximum: 3
                storage:
                  type: object
                  properties:
                    size:
                      type: string
                      default: "1Gi"
                    storageClassName:
                      type: string
                resources:
                  type: object
                  properties:
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          default: "500m"
                        memory:
                          type: string
                          default: "512Mi"
                    requests:
                      type: object
                      properties:
                        cpu:
                          type: string
                          default: "100m"
                        memory:
                          type: string
                          default: "256Mi"
                pooler:
                  type: object
                  description: PgBouncer connection pooler
                  properties:
                    enabled:
                      type: boolean
                      default: true
                    poolMode:
                      type: string
                      enum: ["session", "transaction", "statement"]
                      default: "transaction"
                    maxConnections:
                      type: integer
                      default: 100
                backup:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: false
                    schedule:
                      type: string
                      description: Cron schedule for backups
                metrics:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: true
                    port:
                      type: integer
                      default: 9187
            status:
              type: object
              properties:
                phase:
                  type: string
                  enum: ["Pending", "Initializing", "Running", "Failed", "Degraded"]
                ready:
                  type: boolean
                endpoint:
                  type: string
                poolerEndpoint:
                  type: string
                connections:
                  type: object
                  properties:
                    active:
                      type: integer
                    idle:
                      type: integer
                    waiting:
                      type: integer
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Phase
          type: string
          jsonPath: .status.phase
        - name: Ready
          type: boolean
          jsonPath: .status.ready
        - name: Endpoint
          type: string
          jsonPath: .status.endpoint
        - name: Active
          type: integer
          jsonPath: .status.connections.active
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
```

### 1.2 Redis CRD

```yaml
# impl/claude/infra/k8s/crds/redis-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: redisclusters.kgents.io
spec:
  group: kgents.io
  names:
    kind: RedisCluster
    listKind: RedisClusterList
    plural: redisclusters
    singular: rediscluster
    shortNames:
      - redis
  scope: Namespaced
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              properties:
                image:
                  type: string
                  default: "valkey/valkey:8"
                  description: Use Valkey (open source Redis fork)
                replicas:
                  type: integer
                  default: 1
                maxMemory:
                  type: string
                  default: "128mb"
                evictionPolicy:
                  type: string
                  enum: ["noeviction", "allkeys-lru", "volatile-lru", "allkeys-random"]
                  default: "allkeys-lru"
                resources:
                  type: object
                  properties:
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          default: "200m"
                        memory:
                          type: string
                          default: "256Mi"
                persistence:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: false
                    storageSize:
                      type: string
                      default: "1Gi"
                pubsub:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: true
                    maxChannels:
                      type: integer
                      default: 100
                metrics:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: true
                    port:
                      type: integer
                      default: 9121
            status:
              type: object
              properties:
                phase:
                  type: string
                ready:
                  type: boolean
                endpoint:
                  type: string
                memoryUsage:
                  type: string
                hitRate:
                  type: string
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Phase
          type: string
          jsonPath: .status.phase
        - name: Memory
          type: string
          jsonPath: .status.memoryUsage
        - name: Hit Rate
          type: string
          jsonPath: .status.hitRate
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
```

### 1.3 Qdrant CRD

```yaml
# impl/claude/infra/k8s/crds/qdrant-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: qdrantclusters.kgents.io
spec:
  group: kgents.io
  names:
    kind: QdrantCluster
    listKind: QdrantClusterList
    plural: qdrantclusters
    singular: qdrantcluster
    shortNames:
      - qdrant
  scope: Namespaced
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  default: 1
                storage:
                  type: object
                  properties:
                    size:
                      type: string
                      default: "1Gi"
                resources:
                  type: object
                  properties:
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          default: "500m"
                        memory:
                          type: string
                          default: "512Mi"
                collections:
                  type: array
                  description: Pre-create collections on startup
                  items:
                    type: object
                    required:
                      - name
                      - dimensions
                    properties:
                      name:
                        type: string
                      dimensions:
                        type: integer
                      distance:
                        type: string
                        enum: ["Cosine", "Euclid", "Dot"]
                        default: "Cosine"
                metrics:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: true
            status:
              type: object
              properties:
                phase:
                  type: string
                ready:
                  type: boolean
                endpoint:
                  type: string
                collections:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      vectors:
                        type: integer
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Phase
          type: string
          jsonPath: .status.phase
        - name: Endpoint
          type: string
          jsonPath: .status.endpoint
        - name: Collections
          type: integer
          jsonPath: .status.collections
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
```

---

## Phase 2: Operators

### 2.1 PostgreSQL Operator

```python
# impl/claude/infra/k8s/operators/postgres_operator.py
"""
PostgreSQL Operator: Manages PostgresCluster CRDs.

Creates:
- StatefulSet for PostgreSQL
- Service for internal access
- PgBouncer Deployment (if pooler.enabled)
- PVC for data persistence
- ConfigMap for postgresql.conf
- Secret for credentials
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Any

import kopf


@dataclass
class PostgresSpec:
    """Parsed PostgresCluster spec."""

    database: str
    replicas: int = 1
    storage_size: str = "1Gi"
    storage_class: str | None = None
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    cpu_request: str = "100m"
    memory_request: str = "256Mi"
    pooler_enabled: bool = True
    pooler_mode: str = "transaction"
    pooler_max_connections: int = 100
    metrics_enabled: bool = True
    metrics_port: int = 9187


def parse_postgres_spec(spec: dict[str, Any]) -> PostgresSpec:
    """Parse CRD spec into typed dataclass."""
    resources = spec.get("resources", {})
    limits = resources.get("limits", {})
    requests = resources.get("requests", {})
    storage = spec.get("storage", {})
    pooler = spec.get("pooler", {})
    metrics = spec.get("metrics", {})

    return PostgresSpec(
        database=spec["database"],
        replicas=spec.get("replicas", 1),
        storage_size=storage.get("size", "1Gi"),
        storage_class=storage.get("storageClassName"),
        cpu_limit=limits.get("cpu", "500m"),
        memory_limit=limits.get("memory", "512Mi"),
        cpu_request=requests.get("cpu", "100m"),
        memory_request=requests.get("memory", "256Mi"),
        pooler_enabled=pooler.get("enabled", True),
        pooler_mode=pooler.get("poolMode", "transaction"),
        pooler_max_connections=pooler.get("maxConnections", 100),
        metrics_enabled=metrics.get("enabled", True),
        metrics_port=metrics.get("port", 9187),
    )


def generate_password() -> str:
    """Generate secure random password."""
    return secrets.token_urlsafe(24)


def to_secret(name: str, namespace: str, database: str) -> dict[str, Any]:
    """Generate Secret manifest for PostgreSQL credentials."""
    password = generate_password()
    return {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": f"{name}-credentials",
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "postgres",
                "app.kubernetes.io/instance": name,
                "kgents.io/component": "database",
            },
        },
        "type": "Opaque",
        "data": {
            "username": base64.b64encode(b"postgres").decode(),
            "password": base64.b64encode(password.encode()).decode(),
            "database": base64.b64encode(database.encode()).decode(),
            "connection-string": base64.b64encode(
                f"postgresql://postgres:{password}@{name}:5432/{database}".encode()
            ).decode(),
        },
    }


def to_configmap(name: str, namespace: str, spec: PostgresSpec) -> dict[str, Any]:
    """Generate ConfigMap for postgresql.conf."""
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"{name}-config",
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "postgres",
                "app.kubernetes.io/instance": name,
            },
        },
        "data": {
            "postgresql.conf": f"""
# kgents PostgreSQL configuration
listen_addresses = '*'
max_connections = 200
shared_buffers = 128MB
work_mem = 4MB

# Logging for observability
log_statement = 'all'
log_duration = on
log_min_duration_statement = 100

# pg_stat_statements for metrics
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
""",
            "pg_hba.conf": """
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             0.0.0.0/0               md5
host    all             all             ::/0                    md5
""",
        },
    }


def to_statefulset(
    name: str, namespace: str, spec: PostgresSpec, secret_name: str
) -> dict[str, Any]:
    """Generate StatefulSet manifest for PostgreSQL."""
    return {
        "apiVersion": "apps/v1",
        "kind": "StatefulSet",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "postgres",
                "app.kubernetes.io/instance": name,
                "kgents.io/component": "database",
            },
        },
        "spec": {
            "serviceName": name,
            "replicas": spec.replicas,
            "selector": {
                "matchLabels": {
                    "app.kubernetes.io/name": "postgres",
                    "app.kubernetes.io/instance": name,
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app.kubernetes.io/name": "postgres",
                        "app.kubernetes.io/instance": name,
                    },
                    "annotations": {
                        "prometheus.io/scrape": "true" if spec.metrics_enabled else "false",
                        "prometheus.io/port": str(spec.metrics_port),
                    },
                },
                "spec": {
                    "containers": [
                        {
                            "name": "postgres",
                            "image": "postgres:16-alpine",
                            "ports": [{"containerPort": 5432, "name": "postgres"}],
                            "env": [
                                {
                                    "name": "POSTGRES_DB",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": secret_name,
                                            "key": "database",
                                        }
                                    },
                                },
                                {
                                    "name": "POSTGRES_PASSWORD",
                                    "valueFrom": {
                                        "secretKeyRef": {
                                            "name": secret_name,
                                            "key": "password",
                                        }
                                    },
                                },
                            ],
                            "resources": {
                                "limits": {
                                    "cpu": spec.cpu_limit,
                                    "memory": spec.memory_limit,
                                },
                                "requests": {
                                    "cpu": spec.cpu_request,
                                    "memory": spec.memory_request,
                                },
                            },
                            "volumeMounts": [
                                {"name": "data", "mountPath": "/var/lib/postgresql/data"},
                                {"name": "config", "mountPath": "/etc/postgresql"},
                            ],
                            "livenessProbe": {
                                "exec": {
                                    "command": ["pg_isready", "-U", "postgres"]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                            },
                            "readinessProbe": {
                                "exec": {
                                    "command": ["pg_isready", "-U", "postgres"]
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5,
                            },
                        },
                    ]
                    + (
                        [
                            {
                                "name": "exporter",
                                "image": "prometheuscommunity/postgres-exporter:v0.15.0",
                                "ports": [
                                    {"containerPort": spec.metrics_port, "name": "metrics"}
                                ],
                                "env": [
                                    {
                                        "name": "DATA_SOURCE_URI",
                                        "value": "localhost:5432/postgres?sslmode=disable",
                                    },
                                    {
                                        "name": "DATA_SOURCE_USER",
                                        "value": "postgres",
                                    },
                                    {
                                        "name": "DATA_SOURCE_PASS",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": secret_name,
                                                "key": "password",
                                            }
                                        },
                                    },
                                ],
                                "resources": {
                                    "limits": {"cpu": "100m", "memory": "128Mi"},
                                    "requests": {"cpu": "50m", "memory": "64Mi"},
                                },
                            }
                        ]
                        if spec.metrics_enabled
                        else []
                    ),
                    "volumes": [
                        {
                            "name": "config",
                            "configMap": {"name": f"{name}-config"},
                        }
                    ],
                },
            },
            "volumeClaimTemplates": [
                {
                    "metadata": {"name": "data"},
                    "spec": {
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {"requests": {"storage": spec.storage_size}},
                        **(
                            {"storageClassName": spec.storage_class}
                            if spec.storage_class
                            else {}
                        ),
                    },
                }
            ],
        },
    }


def to_service(name: str, namespace: str) -> dict[str, Any]:
    """Generate Service manifest for PostgreSQL."""
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "postgres",
                "app.kubernetes.io/instance": name,
            },
        },
        "spec": {
            "type": "ClusterIP",
            "ports": [
                {"port": 5432, "targetPort": 5432, "name": "postgres"},
                {"port": 9187, "targetPort": 9187, "name": "metrics"},
            ],
            "selector": {
                "app.kubernetes.io/name": "postgres",
                "app.kubernetes.io/instance": name,
            },
        },
    }


# Kopf handlers (for real operator deployment)
@kopf.on.create("kgents.io", "v1alpha1", "postgresclusters")
async def create_postgres(spec: dict, name: str, namespace: str, **kwargs):
    """Handle PostgresCluster creation."""
    parsed = parse_postgres_spec(spec)

    # Generate manifests
    secret = to_secret(name, namespace, parsed.database)
    configmap = to_configmap(name, namespace, parsed)
    statefulset = to_statefulset(name, namespace, parsed, f"{name}-credentials")
    service = to_service(name, namespace)

    # Create resources (kopf.adopt for ownership)
    # In real implementation, use kubernetes client
    return {
        "phase": "Initializing",
        "ready": False,
        "endpoint": f"{name}.{namespace}.svc.cluster.local:5432",
    }


@kopf.on.delete("kgents.io", "v1alpha1", "postgresclusters")
async def delete_postgres(name: str, namespace: str, **kwargs):
    """Handle PostgresCluster deletion."""
    # Kubernetes garbage collection handles owned resources
    pass
```

---

## Phase 3: Database Metrics

### 3.1 DBPulse Dataclass

```python
# impl/claude/protocols/terrarium/db_metrics.py
"""
Database Metrics: Emit DB health to Terrarium HolographicBuffer.

Extends the Pulse pattern from agents/d/pulse.py to databases.
Each backend (Postgres, Redis, Qdrant) has specialized metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal


class DBPhase(Enum):
    """Database operational phase."""

    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    FAILING = "failing"


@dataclass(frozen=True)
class PostgresPulse:
    """Vitality signal for PostgreSQL."""

    timestamp: str
    phase: DBPhase

    # Connection pool
    pool_active: int
    pool_idle: int
    pool_waiting: int
    pool_max: int

    # Query metrics
    queries_per_second: float
    avg_latency_ms: float
    slow_queries: int  # Queries > 100ms

    # Resource usage
    connections_used: int
    connections_max: int
    cache_hit_ratio: float  # From pg_stat_statements

    # Categorical metric
    morphisms_executed: int  # Total queries since startup

    def to_event(self) -> dict[str, Any]:
        """Convert to Terrarium event format."""
        return {
            "type": "DB_PULSE",
            "backend": "postgres",
            "timestamp": self.timestamp,
            "phase": self.phase.value,
            "pool": {
                "active": self.pool_active,
                "idle": self.pool_idle,
                "waiting": self.pool_waiting,
                "max": self.pool_max,
                "utilization": self.pool_active / self.pool_max if self.pool_max > 0 else 0,
            },
            "performance": {
                "qps": self.queries_per_second,
                "latency_ms": self.avg_latency_ms,
                "slow_queries": self.slow_queries,
                "cache_hit_ratio": self.cache_hit_ratio,
            },
            "morphisms": self.morphisms_executed,
        }

    @classmethod
    def create(
        cls,
        pool_active: int = 0,
        pool_idle: int = 0,
        pool_waiting: int = 0,
        pool_max: int = 100,
        qps: float = 0.0,
        latency_ms: float = 0.0,
        slow_queries: int = 0,
        cache_hit_ratio: float = 0.0,
        morphisms: int = 0,
    ) -> PostgresPulse:
        """Factory with sensible defaults."""
        # Determine phase based on metrics
        utilization = pool_active / pool_max if pool_max > 0 else 0
        if utilization > 0.9 or latency_ms > 100:
            phase = DBPhase.OVERLOADED
        elif utilization > 0.7 or latency_ms > 50:
            phase = DBPhase.DEGRADED
        elif pool_active == 0:
            phase = DBPhase.STARTING
        else:
            phase = DBPhase.HEALTHY

        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            phase=phase,
            pool_active=pool_active,
            pool_idle=pool_idle,
            pool_waiting=pool_waiting,
            pool_max=pool_max,
            queries_per_second=qps,
            avg_latency_ms=latency_ms,
            slow_queries=slow_queries,
            connections_used=pool_active,
            connections_max=pool_max,
            cache_hit_ratio=cache_hit_ratio,
            morphisms_executed=morphisms,
        )


@dataclass(frozen=True)
class RedisPulse:
    """Vitality signal for Redis/Valkey."""

    timestamp: str
    phase: DBPhase

    # Memory
    memory_used_mb: float
    memory_max_mb: float
    memory_fragmentation_ratio: float

    # Performance
    commands_per_second: float
    hit_rate: float  # Cache hit ratio
    keyspace_hits: int
    keyspace_misses: int

    # Pub/Sub
    pubsub_channels: int
    pubsub_patterns: int

    # Categorical metric
    morphisms_executed: int

    def to_event(self) -> dict[str, Any]:
        return {
            "type": "DB_PULSE",
            "backend": "redis",
            "timestamp": self.timestamp,
            "phase": self.phase.value,
            "memory": {
                "used_mb": self.memory_used_mb,
                "max_mb": self.memory_max_mb,
                "utilization": self.memory_used_mb / self.memory_max_mb
                if self.memory_max_mb > 0
                else 0,
                "fragmentation": self.memory_fragmentation_ratio,
            },
            "performance": {
                "ops_per_second": self.commands_per_second,
                "hit_rate": self.hit_rate,
            },
            "pubsub": {
                "channels": self.pubsub_channels,
                "patterns": self.pubsub_patterns,
            },
            "morphisms": self.morphisms_executed,
        }


@dataclass(frozen=True)
class QdrantPulse:
    """Vitality signal for Qdrant."""

    timestamp: str
    phase: DBPhase

    # Collections
    collections_count: int
    total_vectors: int

    # Performance
    searches_per_second: float
    avg_search_latency_ms: float
    index_size_mb: float

    # Resource
    memory_mb: float
    disk_mb: float

    # Categorical metric
    morphisms_executed: int

    def to_event(self) -> dict[str, Any]:
        return {
            "type": "DB_PULSE",
            "backend": "qdrant",
            "timestamp": self.timestamp,
            "phase": self.phase.value,
            "collections": {
                "count": self.collections_count,
                "vectors": self.total_vectors,
            },
            "performance": {
                "searches_per_second": self.searches_per_second,
                "latency_ms": self.avg_search_latency_ms,
            },
            "storage": {
                "index_mb": self.index_size_mb,
                "memory_mb": self.memory_mb,
                "disk_mb": self.disk_mb,
            },
            "morphisms": self.morphisms_executed,
        }


@dataclass
class DBMetricsCollector:
    """Collects metrics from all database backends."""

    postgres_endpoint: str | None = None
    redis_endpoint: str | None = None
    qdrant_endpoint: str | None = None

    _postgres_client: Any = field(default=None, repr=False)
    _redis_client: Any = field(default=None, repr=False)
    _qdrant_client: Any = field(default=None, repr=False)

    async def collect_postgres(self) -> PostgresPulse | None:
        """Collect PostgreSQL metrics via pg_stat_statements."""
        if not self._postgres_client:
            return None

        # Query pg_stat_statements
        stats = await self._postgres_client.fetchrow(
            """
            SELECT
                sum(calls) as total_calls,
                sum(total_exec_time) / sum(calls) as avg_time_ms,
                sum(calls) / EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time())) as qps
            FROM pg_stat_statements
            WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
            """
        )

        pool = self._postgres_client.get_pool()

        return PostgresPulse.create(
            pool_active=pool.get_size() - pool.get_idle_size(),
            pool_idle=pool.get_idle_size(),
            pool_waiting=0,  # Would need pg_stat_activity query
            pool_max=pool.get_max_size(),
            qps=float(stats["qps"] or 0),
            latency_ms=float(stats["avg_time_ms"] or 0),
            morphisms=int(stats["total_calls"] or 0),
        )

    async def collect_redis(self) -> RedisPulse | None:
        """Collect Redis metrics via INFO command."""
        if not self._redis_client:
            return None

        info = await self._redis_client.info()

        memory_used = info.get("used_memory", 0) / (1024 * 1024)
        memory_max = info.get("maxmemory", 0) / (1024 * 1024) or 128  # Default 128MB

        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0

        # Determine phase
        utilization = memory_used / memory_max if memory_max > 0 else 0
        if utilization > 0.9:
            phase = DBPhase.OVERLOADED
        elif utilization > 0.7:
            phase = DBPhase.DEGRADED
        else:
            phase = DBPhase.HEALTHY

        return RedisPulse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            phase=phase,
            memory_used_mb=memory_used,
            memory_max_mb=memory_max,
            memory_fragmentation_ratio=info.get("mem_fragmentation_ratio", 1.0),
            commands_per_second=info.get("instantaneous_ops_per_sec", 0),
            hit_rate=hit_rate,
            keyspace_hits=hits,
            keyspace_misses=misses,
            pubsub_channels=info.get("pubsub_channels", 0),
            pubsub_patterns=info.get("pubsub_patterns", 0),
            morphisms_executed=info.get("total_commands_processed", 0),
        )

    async def collect_qdrant(self) -> QdrantPulse | None:
        """Collect Qdrant metrics via REST API."""
        if not self._qdrant_client:
            return None

        # Get collections info
        collections = await self._qdrant_client.get_collections()
        total_vectors = sum(c.vectors_count for c in collections.collections)

        # Get telemetry
        telemetry = await self._qdrant_client.get_telemetry()

        return QdrantPulse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            phase=DBPhase.HEALTHY,
            collections_count=len(collections.collections),
            total_vectors=total_vectors,
            searches_per_second=telemetry.get("requests", {}).get("avg_per_second", 0),
            avg_search_latency_ms=telemetry.get("requests", {}).get("avg_duration_ms", 0),
            index_size_mb=telemetry.get("storage", {}).get("index_size_mb", 0),
            memory_mb=telemetry.get("storage", {}).get("memory_mb", 0),
            disk_mb=telemetry.get("storage", {}).get("disk_mb", 0),
            morphisms_executed=telemetry.get("requests", {}).get("total", 0),
        )
```

---

## Phase 4: Visual Dashboard Widget

### 4.1 DB Metrics Panel

```python
# impl/claude/agents/i/widgets/db_panel.py
"""
Database Metrics Panel: Textual widget for live DB visualization.

Displays:
- PostgreSQL pool utilization, QPS, latency
- Redis memory usage, hit rate
- Qdrant vector count, search latency
- Bicameral coherency status
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, ProgressBar, Label
from textual.reactive import reactive

from protocols.terrarium.db_metrics import PostgresPulse, RedisPulse, QdrantPulse


class DBGauge(Static):
    """Base gauge widget for database metrics."""

    value = reactive(0.0)
    label_text = reactive("DB")

    def compose(self) -> ComposeResult:
        yield Label(self.label_text, id="gauge-label")
        yield ProgressBar(total=100, show_eta=False, id="gauge-bar")
        yield Label("0%", id="gauge-value")

    def watch_value(self, value: float) -> None:
        bar = self.query_one("#gauge-bar", ProgressBar)
        bar.update(progress=value * 100)
        self.query_one("#gauge-value", Label).update(f"{value:.1%}")


class PostgresGauge(Vertical):
    """PostgreSQL metrics widget."""

    DEFAULT_CSS = """
    PostgresGauge {
        border: solid green;
        height: auto;
        padding: 1;
    }

    PostgresGauge .header {
        text-style: bold;
        color: $success;
    }

    PostgresGauge .metric {
        margin-left: 2;
    }
    """

    pulse: PostgresPulse | None = reactive(None)

    def compose(self) -> ComposeResult:
        yield Label("POSTGRES", classes="header")
        yield Horizontal(
            Label("Pool:", classes="label"),
            ProgressBar(total=100, show_eta=False, id="pool-bar"),
            Label("0/0", id="pool-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("QPS:", classes="label"),
            Label("0.0", id="qps-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Lat:", classes="label"),
            Label("0ms", id="latency-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Phase:", classes="label"),
            Label("unknown", id="phase-text"),
            classes="metric",
        )

    def watch_pulse(self, pulse: PostgresPulse | None) -> None:
        if not pulse:
            return

        # Update pool bar
        bar = self.query_one("#pool-bar", ProgressBar)
        utilization = pulse.pool_active / pulse.pool_max if pulse.pool_max > 0 else 0
        bar.update(progress=utilization * 100)
        self.query_one("#pool-text", Label).update(
            f"{pulse.pool_active}/{pulse.pool_max}"
        )

        # Update QPS
        self.query_one("#qps-text", Label).update(f"{pulse.queries_per_second:.1f}")

        # Update latency
        self.query_one("#latency-text", Label).update(f"{pulse.avg_latency_ms:.1f}ms")

        # Update phase with color
        phase_label = self.query_one("#phase-text", Label)
        phase_label.update(pulse.phase.value)
        phase_label.styles.color = {
            "healthy": "green",
            "degraded": "yellow",
            "overloaded": "red",
            "failing": "red",
            "starting": "blue",
        }.get(pulse.phase.value, "white")


class RedisGauge(Vertical):
    """Redis metrics widget."""

    DEFAULT_CSS = """
    RedisGauge {
        border: solid red;
        height: auto;
        padding: 1;
    }

    RedisGauge .header {
        text-style: bold;
        color: $error;
    }
    """

    pulse: RedisPulse | None = reactive(None)

    def compose(self) -> ComposeResult:
        yield Label("REDIS", classes="header")
        yield Horizontal(
            Label("Mem:", classes="label"),
            ProgressBar(total=100, show_eta=False, id="mem-bar"),
            Label("0/0 MB", id="mem-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Hit:", classes="label"),
            Label("0%", id="hit-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Ops:", classes="label"),
            Label("0/s", id="ops-text"),
            classes="metric",
        )

    def watch_pulse(self, pulse: RedisPulse | None) -> None:
        if not pulse:
            return

        # Update memory bar
        bar = self.query_one("#mem-bar", ProgressBar)
        utilization = (
            pulse.memory_used_mb / pulse.memory_max_mb if pulse.memory_max_mb > 0 else 0
        )
        bar.update(progress=utilization * 100)
        self.query_one("#mem-text", Label).update(
            f"{pulse.memory_used_mb:.0f}/{pulse.memory_max_mb:.0f} MB"
        )

        # Update hit rate
        self.query_one("#hit-text", Label).update(f"{pulse.hit_rate:.1%}")

        # Update ops
        self.query_one("#ops-text", Label).update(f"{pulse.commands_per_second:.0f}/s")


class QdrantGauge(Vertical):
    """Qdrant metrics widget."""

    DEFAULT_CSS = """
    QdrantGauge {
        border: solid blue;
        height: auto;
        padding: 1;
    }

    QdrantGauge .header {
        text-style: bold;
        color: $primary;
    }
    """

    pulse: QdrantPulse | None = reactive(None)

    def compose(self) -> ComposeResult:
        yield Label("QDRANT", classes="header")
        yield Horizontal(
            Label("Vectors:", classes="label"),
            Label("0", id="vectors-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Search:", classes="label"),
            Label("0/s", id="search-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Lat:", classes="label"),
            Label("0ms", id="latency-text"),
            classes="metric",
        )

    def watch_pulse(self, pulse: QdrantPulse | None) -> None:
        if not pulse:
            return

        self.query_one("#vectors-text", Label).update(f"{pulse.total_vectors:,}")
        self.query_one("#search-text", Label).update(
            f"{pulse.searches_per_second:.1f}/s"
        )
        self.query_one("#latency-text", Label).update(
            f"{pulse.avg_search_latency_ms:.1f}ms"
        )


class BicameralCoherencyBar(Vertical):
    """Bicameral Memory coherency status widget."""

    DEFAULT_CSS = """
    BicameralCoherencyBar {
        border: solid magenta;
        height: auto;
        padding: 1;
    }

    BicameralCoherencyBar .header {
        text-style: bold;
        color: $secondary;
    }
    """

    coherency_rate = reactive(1.0)
    ghosts_healed = reactive(0)
    stale_flagged = reactive(0)

    def compose(self) -> ComposeResult:
        yield Label("BICAMERAL COHERENCY", classes="header")
        yield Horizontal(
            Label("Left (PG) ←→ Right (Qdrant)", classes="label"),
            classes="metric",
        )
        yield Horizontal(
            Label("Coherency:", classes="label"),
            ProgressBar(total=100, show_eta=False, id="coherency-bar"),
            Label("100%", id="coherency-text"),
            classes="metric",
        )
        yield Horizontal(
            Label("Ghosts healed:", classes="label"),
            Label("0", id="ghosts-text"),
            Label(" | Stale:", classes="label"),
            Label("0", id="stale-text"),
            classes="metric",
        )

    def watch_coherency_rate(self, rate: float) -> None:
        bar = self.query_one("#coherency-bar", ProgressBar)
        bar.update(progress=rate * 100)
        text = self.query_one("#coherency-text", Label)
        text.update(f"{rate:.1%}")
        text.styles.color = "green" if rate > 0.95 else "yellow" if rate > 0.8 else "red"

    def watch_ghosts_healed(self, count: int) -> None:
        self.query_one("#ghosts-text", Label).update(str(count))

    def watch_stale_flagged(self, count: int) -> None:
        self.query_one("#stale-text", Label).update(str(count))


class DBMetricsPanel(Vertical):
    """Complete database metrics panel."""

    DEFAULT_CSS = """
    DBMetricsPanel {
        height: auto;
        padding: 1;
    }

    DBMetricsPanel > Horizontal {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            PostgresGauge(id="postgres-gauge"),
            RedisGauge(id="redis-gauge"),
            QdrantGauge(id="qdrant-gauge"),
        )
        yield BicameralCoherencyBar(id="bicameral-bar")

    def update_postgres(self, pulse: PostgresPulse) -> None:
        self.query_one("#postgres-gauge", PostgresGauge).pulse = pulse

    def update_redis(self, pulse: RedisPulse) -> None:
        self.query_one("#redis-gauge", RedisGauge).pulse = pulse

    def update_qdrant(self, pulse: QdrantPulse) -> None:
        self.query_one("#qdrant-gauge", QdrantGauge).pulse = pulse

    def update_coherency(
        self, rate: float, ghosts: int = 0, stale: int = 0
    ) -> None:
        bar = self.query_one("#bicameral-bar", BicameralCoherencyBar)
        bar.coherency_rate = rate
        bar.ghosts_healed = ghosts
        bar.stale_flagged = stale
```

---

## Phase 5: Terrarium Integration

### 5.1 Terrarium Endpoint

```python
# Addition to impl/claude/protocols/terrarium/gateway.py

@app.get("/api/db/metrics")
async def get_db_metrics():
    """Get aggregated database metrics for I-gent DensityField."""
    collector = app.state.db_collector

    postgres_pulse = await collector.collect_postgres()
    redis_pulse = await collector.collect_redis()
    qdrant_pulse = await collector.collect_qdrant()

    return {
        "postgres": postgres_pulse.to_event() if postgres_pulse else None,
        "redis": redis_pulse.to_event() if redis_pulse else None,
        "qdrant": qdrant_pulse.to_event() if qdrant_pulse else None,
        "bicameral": {
            "coherency_rate": app.state.bicameral.stats().get("coherency_rate", 1.0)
            if hasattr(app.state, "bicameral")
            else 1.0,
        },
    }
```

---

## Categorical Summary

```
┌─────────────────────────────────────────────────────────────┐
│              THE DATABASE TRIAD AS COPRODUCT                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      DB = Pg ⊕ Redis ⊕ Qdrant               │
│                                                             │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Postgres │      │  Redis   │      │  Qdrant  │          │
│  │ (ACID)   │      │ (Cache)  │      │ (Vector) │          │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘          │
│       │                 │                 │                 │
│       └────────────┬────┴─────────────────┘                 │
│                    │                                        │
│                    ▼                                        │
│            ┌──────────────┐                                 │
│            │  DBFunctor   │                                 │
│            │  lift/unlift │                                 │
│            └──────┬───────┘                                 │
│                   │                                         │
│                   ▼                                         │
│            ┌──────────────┐                                 │
│            │ State[DB, A] │                                 │
│            └──────────────┘                                 │
│                                                             │
│  Universal Property:                                        │
│  For any X and f: Pg→X, g: Redis→X, h: Qdrant→X            │
│  ∃! [f,g,h]: DB → X                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Deliverables Checklist

### Phase 1: CRDs
- [ ] PostgresCluster CRD
- [ ] RedisCluster CRD
- [ ] QdrantCluster CRD
- [ ] Apply to Kind cluster

### Phase 2: Operators
- [ ] postgres_operator.py
- [ ] redis_operator.py
- [ ] qdrant_operator.py
- [ ] Integration tests

### Phase 3: Metrics
- [ ] DBPulse dataclasses
- [ ] DBMetricsCollector
- [ ] Terrarium `/api/db/metrics`

### Phase 4: Widgets
- [ ] PostgresGauge
- [ ] RedisGauge
- [ ] QdrantGauge
- [ ] BicameralCoherencyBar
- [ ] DBMetricsPanel

### Phase 5: Integration
- [ ] Kind cluster with DB pods
- [ ] Terrarium wired to collectors
- [ ] I-gent dashboard consuming metrics

---

*"The stream finds a way around the boulder."* — Graceful Degradation Principle
