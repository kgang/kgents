"""
K8s Database Projector: Emits manifests for standard database operators.

Principle: "Managed, Not Built"
- We emit CloudNativePG Cluster CRs, not StatefulSets
- We emit HelmReleases for Redis and Qdrant
- The operators handle Day 2 operations
- Our Projector is a thin configuration layer

The Database Triad as Functor Stack:
    Postgres (ANCHOR)  -- Source of truth
        |
        | CDC/Outbox
        v
    Synapse FluxAgent
        |          |
        v          v
    Qdrant     Redis
  (ASSOCIATOR)  (SPARK)

Benefits:
- Free HA: CloudNativePG handles leader election, failover
- Free Backups: Barman integration when configured
- Free Metrics: Prometheus exporters included
- Free Upgrades: Operators handle rolling updates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatabaseProjection:
    """
    Projection from spec to operator manifests.

    Contains the K8s manifests for the Database Triad:
    - postgres: CloudNativePG Cluster CR
    - redis: HelmRelease for Bitnami Redis
    - qdrant: HelmRelease for Qdrant
    """

    postgres: dict[str, Any] | None = None
    redis: dict[str, Any] | None = None
    qdrant: dict[str, Any] | None = None

    def to_manifests(self) -> list[dict[str, Any]]:
        """Return all non-None manifests as a list."""
        return [m for m in [self.postgres, self.redis, self.qdrant] if m is not None]


@dataclass
class CNPGClusterConfig:
    """
    Configuration for CloudNativePG Cluster.

    Sensible defaults with override capability.
    """

    instances: int = 1
    storage: str = "1Gi"
    storage_class: str | None = None
    pg_version: int = 16
    shared_preload_libraries: list[str] = field(default_factory=lambda: ["pg_stat_statements"])
    enable_monitoring: bool = True
    backup_enabled: bool = False


@dataclass
class RedisConfig:
    """
    Configuration for Redis HelmRelease.
    """

    memory: str = "128Mi"
    architecture: str = "standalone"  # or "replication"
    enable_metrics: bool = True


@dataclass
class QdrantConfig:
    """
    Configuration for Qdrant HelmRelease.
    """

    storage: str = "1Gi"
    enable_metrics: bool = True


def to_cnpg_cluster(
    name: str,
    database: str = "kgents",
    config: CNPGClusterConfig | None = None,
) -> dict[str, Any]:
    """
    Generate CloudNativePG Cluster manifest.

    This is NOT a StatefulSet--it's a high-level intent that CNPG
    reconciles into StatefulSets, Services, Secrets, etc.

    Args:
        name: Cluster name (K8s resource name)
        database: Database name to create
        config: Optional configuration overrides

    Returns:
        CloudNativePG Cluster CR manifest

    Example:
        >>> manifest = to_cnpg_cluster("my-db", "myapp")
        >>> manifest["kind"]
        'Cluster'
        >>> manifest["apiVersion"]
        'postgresql.cnpg.io/v1'
    """
    cfg = config or CNPGClusterConfig()

    spec: dict[str, Any] = {
        "instances": cfg.instances,
        "storage": {
            "size": cfg.storage,
        },
        "postgresql": {
            "shared_preload_libraries": cfg.shared_preload_libraries,
        },
        "bootstrap": {
            "initdb": {
                "database": database,
                "owner": database,
            },
        },
    }

    # Add storage class if specified
    if cfg.storage_class:
        spec["storage"]["storageClass"] = cfg.storage_class

    # Add monitoring if enabled
    if cfg.enable_monitoring:
        spec["monitoring"] = {
            "enablePodMonitor": True,
        }

    # Add backup configuration if enabled
    if cfg.backup_enabled:
        spec["backup"] = {
            "barmanObjectStore": {
                "destinationPath": f"s3://backups/{name}",
                "s3Credentials": {
                    "accessKeyId": {
                        "name": f"{name}-backup-creds",
                        "key": "ACCESS_KEY_ID",
                    },
                    "secretAccessKey": {
                        "name": f"{name}-backup-creds",
                        "key": "SECRET_ACCESS_KEY",
                    },
                },
            },
            "retentionPolicy": "7d",
        }

    return {
        "apiVersion": "postgresql.cnpg.io/v1",
        "kind": "Cluster",
        "metadata": {
            "name": name,
            "labels": {
                "kgents.io/component": "database",
                "kgents.io/role": "anchor",
            },
        },
        "spec": spec,
    }


def to_redis_release(
    name: str,
    config: RedisConfig | None = None,
    namespace: str = "default",
) -> dict[str, Any]:
    """
    Generate Helm Release for Redis (Bitnami).

    Uses FluxCD HelmRelease for GitOps-native deployment.

    Args:
        name: Release name (K8s resource name)
        config: Optional configuration overrides
        namespace: Target namespace

    Returns:
        HelmRelease manifest for Bitnami Redis

    Example:
        >>> manifest = to_redis_release("cache")
        >>> manifest["kind"]
        'HelmRelease'
    """
    cfg = config or RedisConfig()

    values: dict[str, Any] = {
        "architecture": cfg.architecture,
        "auth": {
            "enabled": True,
            "sentinel": False,
        },
        "master": {
            "resources": {
                "requests": {"memory": cfg.memory},
                "limits": {"memory": cfg.memory},
            },
        },
    }

    if cfg.enable_metrics:
        values["metrics"] = {
            "enabled": True,
            "serviceMonitor": {
                "enabled": True,
            },
        }

    return {
        "apiVersion": "helm.toolkit.fluxcd.io/v2beta1",
        "kind": "HelmRelease",
        "metadata": {
            "name": f"{name}-redis",
            "namespace": namespace,
            "labels": {
                "kgents.io/component": "cache",
                "kgents.io/role": "spark",
            },
        },
        "spec": {
            "interval": "10m",
            "chart": {
                "spec": {
                    "chart": "redis",
                    "version": "18.x",
                    "sourceRef": {
                        "kind": "HelmRepository",
                        "name": "bitnami",
                    },
                },
            },
            "values": values,
        },
    }


def to_qdrant_release(
    name: str,
    config: QdrantConfig | None = None,
    namespace: str = "default",
) -> dict[str, Any]:
    """
    Generate Helm Release for Qdrant.

    Uses FluxCD HelmRelease for GitOps-native deployment.

    Args:
        name: Release name (K8s resource name)
        config: Optional configuration overrides
        namespace: Target namespace

    Returns:
        HelmRelease manifest for Qdrant

    Example:
        >>> manifest = to_qdrant_release("vectors")
        >>> manifest["kind"]
        'HelmRelease'
    """
    cfg = config or QdrantConfig()

    values: dict[str, Any] = {
        "persistence": {
            "size": cfg.storage,
        },
        "resources": {
            "requests": {
                "memory": "256Mi",
                "cpu": "100m",
            },
            "limits": {
                "memory": "512Mi",
                "cpu": "500m",
            },
        },
    }

    if cfg.enable_metrics:
        values["metrics"] = {
            "serviceMonitor": {
                "enabled": True,
            },
        }

    return {
        "apiVersion": "helm.toolkit.fluxcd.io/v2beta1",
        "kind": "HelmRelease",
        "metadata": {
            "name": f"{name}-qdrant",
            "namespace": namespace,
            "labels": {
                "kgents.io/component": "vector",
                "kgents.io/role": "associator",
            },
        },
        "spec": {
            "interval": "10m",
            "chart": {
                "spec": {
                    "chart": "qdrant",
                    "version": "0.9.x",
                    "sourceRef": {
                        "kind": "HelmRepository",
                        "name": "qdrant",
                    },
                },
            },
            "values": values,
        },
    }


def project_database_triad(
    name: str,
    database: str = "kgents",
    namespace: str = "default",
    pg_config: CNPGClusterConfig | None = None,
    redis_config: RedisConfig | None = None,
    qdrant_config: QdrantConfig | None = None,
) -> DatabaseProjection:
    """
    Project the complete Database Triad.

    Returns manifests for:
    - CloudNativePG Cluster (Anchor - source of truth)
    - Redis HelmRelease (Spark - fast cache)
    - Qdrant HelmRelease (Associator - semantic search)

    The Functor Stack guarantee:
    - Postgres is the Anchor (source of truth)
    - Redis and Qdrant are derived views
    - Synapse CDC agent maintains consistency

    Args:
        name: Base name for all resources
        database: Database name for Postgres
        namespace: Target namespace
        pg_config: Optional Postgres configuration
        redis_config: Optional Redis configuration
        qdrant_config: Optional Qdrant configuration

    Returns:
        DatabaseProjection with all manifests

    Example:
        >>> projection = project_database_triad("my-app")
        >>> len(projection.to_manifests())
        3
    """
    return DatabaseProjection(
        postgres=to_cnpg_cluster(name, database, pg_config),
        redis=to_redis_release(name, redis_config, namespace),
        qdrant=to_qdrant_release(name, qdrant_config, namespace),
    )


def to_yaml(projection: DatabaseProjection, separator: str = "---\n") -> str:
    """
    Convert DatabaseProjection to multi-document YAML.

    Args:
        projection: The projection to serialize
        separator: Document separator (default: ---)

    Returns:
        YAML string with all manifests
    """
    try:
        import yaml

        return separator.join(
            yaml.dump(m, default_flow_style=False) for m in projection.to_manifests()
        )
    except ImportError:
        # Fallback to JSON
        import json

        return separator.join(json.dumps(m, indent=2) for m in projection.to_manifests())
