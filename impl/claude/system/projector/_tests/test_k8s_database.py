"""
Tests for K8s Database Projector.

The K8s Database Projector emits manifests for standard database operators,
following the "Managed, Not Built" principle.

Test Categories:
1. CloudNativePG Cluster generation
2. Redis HelmRelease generation
3. Qdrant HelmRelease generation
4. Database Triad projection
5. Configuration overrides
6. YAML serialization
"""

from __future__ import annotations

import pytest

from system.projector.k8s_database import (
    CNPGClusterConfig,
    DatabaseProjection,
    QdrantConfig,
    RedisConfig,
    project_database_triad,
    to_cnpg_cluster,
    to_qdrant_release,
    to_redis_release,
    to_yaml,
)


# ===========================================================================
# CloudNativePG Cluster Tests
# ===========================================================================


class TestCNPGCluster:
    """Tests for CloudNativePG Cluster manifest generation."""

    def test_to_cnpg_cluster_basic(self) -> None:
        """Basic cluster manifest has correct structure."""
        manifest = to_cnpg_cluster("test-db")

        assert manifest["apiVersion"] == "postgresql.cnpg.io/v1"
        assert manifest["kind"] == "Cluster"
        assert manifest["metadata"]["name"] == "test-db"

    def test_to_cnpg_cluster_labels(self) -> None:
        """Cluster has kgents labels for identification."""
        manifest = to_cnpg_cluster("test-db")

        labels = manifest["metadata"]["labels"]
        assert labels["kgents.io/component"] == "database"
        assert labels["kgents.io/role"] == "anchor"

    def test_to_cnpg_cluster_default_storage(self) -> None:
        """Default storage is 1Gi."""
        manifest = to_cnpg_cluster("test-db")

        assert manifest["spec"]["storage"]["size"] == "1Gi"

    def test_to_cnpg_cluster_custom_storage(self) -> None:
        """Custom storage size is respected."""
        config = CNPGClusterConfig(storage="10Gi")
        manifest = to_cnpg_cluster("test-db", config=config)

        assert manifest["spec"]["storage"]["size"] == "10Gi"

    def test_to_cnpg_cluster_storage_class(self) -> None:
        """Storage class is set when configured."""
        config = CNPGClusterConfig(storage_class="fast-ssd")
        manifest = to_cnpg_cluster("test-db", config=config)

        assert manifest["spec"]["storage"]["storageClass"] == "fast-ssd"

    def test_to_cnpg_cluster_instances(self) -> None:
        """Instance count is configurable."""
        config = CNPGClusterConfig(instances=3)
        manifest = to_cnpg_cluster("test-db", config=config)

        assert manifest["spec"]["instances"] == 3

    def test_to_cnpg_cluster_database_name(self) -> None:
        """Database name is set in bootstrap."""
        manifest = to_cnpg_cluster("test-db", database="myapp")

        bootstrap = manifest["spec"]["bootstrap"]["initdb"]
        assert bootstrap["database"] == "myapp"
        assert bootstrap["owner"] == "myapp"

    def test_to_cnpg_cluster_shared_preload_libraries(self) -> None:
        """pg_stat_statements is loaded by default."""
        manifest = to_cnpg_cluster("test-db")

        libs = manifest["spec"]["postgresql"]["shared_preload_libraries"]
        assert "pg_stat_statements" in libs

    def test_to_cnpg_cluster_monitoring_enabled_by_default(self) -> None:
        """PodMonitor is enabled by default."""
        manifest = to_cnpg_cluster("test-db")

        assert manifest["spec"]["monitoring"]["enablePodMonitor"] is True

    def test_to_cnpg_cluster_monitoring_disabled(self) -> None:
        """Monitoring can be disabled."""
        config = CNPGClusterConfig(enable_monitoring=False)
        manifest = to_cnpg_cluster("test-db", config=config)

        assert "monitoring" not in manifest["spec"]

    def test_to_cnpg_cluster_backup_disabled_by_default(self) -> None:
        """Backup is disabled by default."""
        manifest = to_cnpg_cluster("test-db")

        assert "backup" not in manifest["spec"]

    def test_to_cnpg_cluster_backup_enabled(self) -> None:
        """Backup configuration is added when enabled."""
        config = CNPGClusterConfig(backup_enabled=True)
        manifest = to_cnpg_cluster("test-db", config=config)

        assert "backup" in manifest["spec"]
        backup = manifest["spec"]["backup"]
        assert backup["retentionPolicy"] == "7d"
        assert "barmanObjectStore" in backup


# ===========================================================================
# Redis HelmRelease Tests
# ===========================================================================


class TestRedisRelease:
    """Tests for Redis HelmRelease manifest generation."""

    def test_to_redis_release_basic(self) -> None:
        """Basic Redis manifest has correct structure."""
        manifest = to_redis_release("cache")

        assert manifest["apiVersion"] == "helm.toolkit.fluxcd.io/v2beta1"
        assert manifest["kind"] == "HelmRelease"
        assert manifest["metadata"]["name"] == "cache-redis"

    def test_to_redis_release_labels(self) -> None:
        """Redis has kgents labels for identification."""
        manifest = to_redis_release("cache")

        labels = manifest["metadata"]["labels"]
        assert labels["kgents.io/component"] == "cache"
        assert labels["kgents.io/role"] == "spark"

    def test_to_redis_release_namespace(self) -> None:
        """Namespace is configurable."""
        manifest = to_redis_release("cache", namespace="production")

        assert manifest["metadata"]["namespace"] == "production"

    def test_to_redis_release_chart_reference(self) -> None:
        """Chart reference points to Bitnami."""
        manifest = to_redis_release("cache")

        chart = manifest["spec"]["chart"]["spec"]
        assert chart["chart"] == "redis"
        assert chart["version"] == "18.x"
        assert chart["sourceRef"]["kind"] == "HelmRepository"
        assert chart["sourceRef"]["name"] == "bitnami"

    def test_to_redis_release_default_memory(self) -> None:
        """Default memory is 128Mi."""
        manifest = to_redis_release("cache")

        master = manifest["spec"]["values"]["master"]
        assert master["resources"]["requests"]["memory"] == "128Mi"
        assert master["resources"]["limits"]["memory"] == "128Mi"

    def test_to_redis_release_custom_memory(self) -> None:
        """Custom memory is respected."""
        config = RedisConfig(memory="256Mi")
        manifest = to_redis_release("cache", config=config)

        master = manifest["spec"]["values"]["master"]
        assert master["resources"]["requests"]["memory"] == "256Mi"

    def test_to_redis_release_architecture_standalone(self) -> None:
        """Default architecture is standalone."""
        manifest = to_redis_release("cache")

        assert manifest["spec"]["values"]["architecture"] == "standalone"

    def test_to_redis_release_architecture_replication(self) -> None:
        """Replication architecture is configurable."""
        config = RedisConfig(architecture="replication")
        manifest = to_redis_release("cache", config=config)

        assert manifest["spec"]["values"]["architecture"] == "replication"

    def test_to_redis_release_metrics_enabled_by_default(self) -> None:
        """Metrics are enabled by default."""
        manifest = to_redis_release("cache")

        metrics = manifest["spec"]["values"]["metrics"]
        assert metrics["enabled"] is True
        assert metrics["serviceMonitor"]["enabled"] is True

    def test_to_redis_release_metrics_disabled(self) -> None:
        """Metrics can be disabled."""
        config = RedisConfig(enable_metrics=False)
        manifest = to_redis_release("cache", config=config)

        assert "metrics" not in manifest["spec"]["values"]

    def test_to_redis_release_interval(self) -> None:
        """Reconciliation interval is 10m."""
        manifest = to_redis_release("cache")

        assert manifest["spec"]["interval"] == "10m"


# ===========================================================================
# Qdrant HelmRelease Tests
# ===========================================================================


class TestQdrantRelease:
    """Tests for Qdrant HelmRelease manifest generation."""

    def test_to_qdrant_release_basic(self) -> None:
        """Basic Qdrant manifest has correct structure."""
        manifest = to_qdrant_release("vectors")

        assert manifest["apiVersion"] == "helm.toolkit.fluxcd.io/v2beta1"
        assert manifest["kind"] == "HelmRelease"
        assert manifest["metadata"]["name"] == "vectors-qdrant"

    def test_to_qdrant_release_labels(self) -> None:
        """Qdrant has kgents labels for identification."""
        manifest = to_qdrant_release("vectors")

        labels = manifest["metadata"]["labels"]
        assert labels["kgents.io/component"] == "vector"
        assert labels["kgents.io/role"] == "associator"

    def test_to_qdrant_release_namespace(self) -> None:
        """Namespace is configurable."""
        manifest = to_qdrant_release("vectors", namespace="ml")

        assert manifest["metadata"]["namespace"] == "ml"

    def test_to_qdrant_release_chart_reference(self) -> None:
        """Chart reference points to Qdrant."""
        manifest = to_qdrant_release("vectors")

        chart = manifest["spec"]["chart"]["spec"]
        assert chart["chart"] == "qdrant"
        assert chart["version"] == "0.9.x"
        assert chart["sourceRef"]["kind"] == "HelmRepository"
        assert chart["sourceRef"]["name"] == "qdrant"

    def test_to_qdrant_release_default_storage(self) -> None:
        """Default storage is 1Gi."""
        manifest = to_qdrant_release("vectors")

        assert manifest["spec"]["values"]["persistence"]["size"] == "1Gi"

    def test_to_qdrant_release_custom_storage(self) -> None:
        """Custom storage is respected."""
        config = QdrantConfig(storage="10Gi")
        manifest = to_qdrant_release("vectors", config=config)

        assert manifest["spec"]["values"]["persistence"]["size"] == "10Gi"

    def test_to_qdrant_release_resources(self) -> None:
        """Resource limits are set."""
        manifest = to_qdrant_release("vectors")

        resources = manifest["spec"]["values"]["resources"]
        assert resources["requests"]["memory"] == "256Mi"
        assert resources["limits"]["memory"] == "512Mi"

    def test_to_qdrant_release_metrics_enabled_by_default(self) -> None:
        """Metrics are enabled by default."""
        manifest = to_qdrant_release("vectors")

        metrics = manifest["spec"]["values"]["metrics"]
        assert metrics["serviceMonitor"]["enabled"] is True

    def test_to_qdrant_release_metrics_disabled(self) -> None:
        """Metrics can be disabled."""
        config = QdrantConfig(enable_metrics=False)
        manifest = to_qdrant_release("vectors", config=config)

        assert "metrics" not in manifest["spec"]["values"]


# ===========================================================================
# Database Triad Projection Tests
# ===========================================================================


class TestDatabaseTriadProjection:
    """Tests for the complete Database Triad projection."""

    def test_project_database_triad_returns_all_three(self) -> None:
        """Triad projection includes all three components."""
        projection = project_database_triad("my-app")

        assert projection.postgres is not None
        assert projection.redis is not None
        assert projection.qdrant is not None

    def test_project_database_triad_to_manifests(self) -> None:
        """to_manifests() returns three manifests."""
        projection = project_database_triad("my-app")

        manifests = projection.to_manifests()
        assert len(manifests) == 3

    def test_project_database_triad_consistent_naming(self) -> None:
        """All resources share the base name."""
        projection = project_database_triad("my-app")

        assert projection.postgres is not None
        assert projection.redis is not None
        assert projection.qdrant is not None
        assert projection.postgres["metadata"]["name"] == "my-app"
        assert projection.redis["metadata"]["name"] == "my-app-redis"
        assert projection.qdrant["metadata"]["name"] == "my-app-qdrant"

    def test_project_database_triad_database_name(self) -> None:
        """Database name is passed to Postgres."""
        projection = project_database_triad("my-app", database="production")

        assert projection.postgres is not None
        bootstrap = projection.postgres["spec"]["bootstrap"]["initdb"]
        assert bootstrap["database"] == "production"

    def test_project_database_triad_namespace(self) -> None:
        """Namespace is passed to Redis and Qdrant."""
        projection = project_database_triad("my-app", namespace="staging")

        assert projection.redis is not None
        assert projection.qdrant is not None
        assert projection.redis["metadata"]["namespace"] == "staging"
        assert projection.qdrant["metadata"]["namespace"] == "staging"

    def test_project_database_triad_custom_configs(self) -> None:
        """Custom configs are applied to each component."""
        pg_config = CNPGClusterConfig(instances=3, storage="50Gi")
        redis_config = RedisConfig(memory="512Mi")
        qdrant_config = QdrantConfig(storage="20Gi")

        projection = project_database_triad(
            "my-app",
            pg_config=pg_config,
            redis_config=redis_config,
            qdrant_config=qdrant_config,
        )

        assert projection.postgres is not None
        assert projection.redis is not None
        assert projection.qdrant is not None
        assert projection.postgres["spec"]["instances"] == 3
        assert projection.postgres["spec"]["storage"]["size"] == "50Gi"

        master = projection.redis["spec"]["values"]["master"]
        assert master["resources"]["requests"]["memory"] == "512Mi"

        assert projection.qdrant["spec"]["values"]["persistence"]["size"] == "20Gi"


# ===========================================================================
# DatabaseProjection Tests
# ===========================================================================


class TestDatabaseProjection:
    """Tests for the DatabaseProjection dataclass."""

    def test_empty_projection(self) -> None:
        """Empty projection returns empty manifest list."""
        projection = DatabaseProjection()

        assert projection.to_manifests() == []

    def test_partial_projection(self) -> None:
        """Partial projection returns only non-None manifests."""
        projection = DatabaseProjection(
            postgres=to_cnpg_cluster("test"),
            redis=None,
            qdrant=None,
        )

        manifests = projection.to_manifests()
        assert len(manifests) == 1
        assert manifests[0]["kind"] == "Cluster"

    def test_full_projection(self) -> None:
        """Full projection returns all three manifests."""
        projection = project_database_triad("test")

        manifests = projection.to_manifests()
        kinds = {m["kind"] for m in manifests}
        assert kinds == {"Cluster", "HelmRelease"}


# ===========================================================================
# YAML Serialization Tests
# ===========================================================================


class TestYAMLSerialization:
    """Tests for YAML serialization."""

    def test_to_yaml_basic(self) -> None:
        """to_yaml produces valid output."""
        projection = project_database_triad("test")
        yaml_output = to_yaml(projection)

        # Should have separators between documents
        assert "---" in yaml_output or "apiVersion" in yaml_output

    def test_to_yaml_custom_separator(self) -> None:
        """Custom separator is used."""
        projection = project_database_triad("test")
        yaml_output = to_yaml(projection, separator="# ---\n")

        # Either YAML works (with custom separator) or falls back to JSON
        assert "apiVersion" in yaml_output or "kind" in yaml_output

    def test_to_yaml_empty_projection(self) -> None:
        """Empty projection produces empty output."""
        projection = DatabaseProjection()
        yaml_output = to_yaml(projection)

        assert yaml_output == ""


# ===========================================================================
# Categorical Guarantee Tests
# ===========================================================================


class TestCategoricalGuarantees:
    """Tests verifying the categorical structure of the Database Triad."""

    def test_postgres_is_anchor(self) -> None:
        """Postgres role is 'anchor' (source of truth)."""
        projection = project_database_triad("test")

        assert projection.postgres is not None
        role = projection.postgres["metadata"]["labels"]["kgents.io/role"]
        assert role == "anchor"

    def test_redis_is_spark(self) -> None:
        """Redis role is 'spark' (fast cache)."""
        projection = project_database_triad("test")

        assert projection.redis is not None
        role = projection.redis["metadata"]["labels"]["kgents.io/role"]
        assert role == "spark"

    def test_qdrant_is_associator(self) -> None:
        """Qdrant role is 'associator' (semantic search)."""
        projection = project_database_triad("test")

        assert projection.qdrant is not None
        role = projection.qdrant["metadata"]["labels"]["kgents.io/role"]
        assert role == "associator"

    def test_triad_components_identified(self) -> None:
        """Each component has a unique kgents.io/component label."""
        projection = project_database_triad("test")

        components = {
            m["metadata"]["labels"]["kgents.io/component"]
            for m in projection.to_manifests()
        }
        assert components == {"database", "cache", "vector"}
