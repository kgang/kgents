"""
Storage Provider: Unified Access to All Storage Backends.

The StorageProvider is the single entry point for all persistence.
It abstracts over different backend configurations (local SQLite,
PostgreSQL, cloud services) via infrastructure.yaml.

XDG Compliance:
- ~/.config/kgents/ - Configuration
- ~/.local/share/kgents/ - Data
- ~/.cache/kgents/ - Cache/Logs
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# yaml is optional - we can use JSON fallback
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None

from .interfaces import (
    IBlobStore,
    IRelationalStore,
    ITelemetryStore,
    IVectorStore,
)
from .providers.sqlite import (
    FilesystemBlobStore,
    InMemoryBlobStore,
    InMemoryRelationalStore,
    InMemoryTelemetryStore,
    InMemoryVectorStore,
    NumpyVectorStore,
    SQLiteRelationalStore,
    SQLiteTelemetryStore,
)


@dataclass
class XDGPaths:
    """
    XDG Base Directory paths for kgents.

    Respects XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_CACHE_HOME
    environment variables, with sensible defaults.
    """

    config: Path
    data: Path
    cache: Path

    @classmethod
    def resolve(cls) -> "XDGPaths":
        """Resolve XDG paths from environment or defaults."""
        home = Path.home()

        config_home = os.environ.get("XDG_CONFIG_HOME")
        data_home = os.environ.get("XDG_DATA_HOME")
        cache_home = os.environ.get("XDG_CACHE_HOME")

        return cls(
            config=Path(config_home) / "kgents"
            if config_home
            else home / ".config" / "kgents",
            data=Path(data_home) / "kgents"
            if data_home
            else home / ".local" / "share" / "kgents",
            cache=Path(cache_home) / "kgents"
            if cache_home
            else home / ".cache" / "kgents",
        )

    def ensure_dirs(self) -> None:
        """Create all directories if they don't exist."""
        self.config.mkdir(parents=True, exist_ok=True)
        self.data.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)


@dataclass
class RetentionConfig:
    """Retention configuration for telemetry tiers."""

    hot_days: int = 30
    warm_days: int = 365
    cold_days: int | None = None  # None = indefinite


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""

    type: str
    connection: str | None = None
    path: str | None = None
    wal_mode: bool = True
    dimensions: int = 384
    fallback: str | None = None
    threshold: int = 1000
    retention: RetentionConfig | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderConfig":
        """Create from dict."""
        retention_data = data.get("retention")
        retention = None
        if retention_data:
            retention = RetentionConfig(
                hot_days=retention_data.get("hot_days", 30),
                warm_days=retention_data.get("warm_days", 365),
                cold_days=retention_data.get("cold_days"),
            )

        return cls(
            type=data.get("type", "sqlite"),
            connection=data.get("connection"),
            path=data.get("path"),
            wal_mode=data.get("wal_mode", True),
            dimensions=data.get("dimensions", 384),
            fallback=data.get("fallback"),
            threshold=data.get("threshold", 1000),
            retention=retention,
        )


@dataclass
class InfrastructureConfig:
    """Full infrastructure configuration."""

    profile: str
    relational: ProviderConfig
    vector: ProviderConfig
    blob: ProviderConfig
    telemetry: ProviderConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InfrastructureConfig":
        """Create from dict (parsed YAML)."""
        providers = data.get("providers", {})
        return cls(
            profile=data.get("profile", "local-canonical"),
            relational=ProviderConfig.from_dict(providers.get("relational", {})),
            vector=ProviderConfig.from_dict(providers.get("vector", {})),
            blob=ProviderConfig.from_dict(providers.get("blob", {})),
            telemetry=ProviderConfig.from_dict(providers.get("telemetry", {})),
        )

    @classmethod
    def default(cls, paths: XDGPaths) -> "InfrastructureConfig":
        """Create default local-first configuration."""
        return cls(
            profile="local-canonical",
            relational=ProviderConfig(
                type="sqlite",
                connection=str(paths.data / "membrane.db"),
                wal_mode=True,
            ),
            vector=ProviderConfig(
                type="numpy",
                path=str(paths.data / "vectors.json"),
                dimensions=384,
                fallback="numpy-cosine",
                threshold=1000,
            ),
            blob=ProviderConfig(
                type="filesystem",
                path=str(paths.data / "blobs"),
            ),
            telemetry=ProviderConfig(
                type="sqlite",
                connection=str(paths.data / "telemetry.db"),
                retention=RetentionConfig(hot_days=30, warm_days=365),
            ),
        )


class EnvVarNotSetError(ValueError):
    """Raised when a required environment variable is not set."""

    pass


def _expand_env_vars(value: str, strict: bool = True) -> str:
    """
    Expand ${env:VAR} and ${VAR} patterns in strings.

    Args:
        value: String potentially containing env var references
        strict: If True, raise EnvVarNotSetError for unset vars.
                If False, use XDG defaults for known vars, fail on others.

    Raises:
        EnvVarNotSetError: If strict=True and an env var is not set,
                          or if strict=False and an unknown var is not set.
    """
    if not isinstance(value, str):
        return value

    import re

    # XDG defaults for non-strict mode
    xdg_defaults = {
        "XDG_DATA_HOME": str(Path.home() / ".local" / "share"),
        "XDG_CONFIG_HOME": str(Path.home() / ".config"),
        "XDG_CACHE_HOME": str(Path.home() / ".cache"),
    }

    # Handle ${env:VAR} pattern
    def replace_env(match):
        var_name = match.group(1)
        env_value = os.environ.get(var_name)
        if env_value is None:
            if strict:
                raise EnvVarNotSetError(
                    f"Environment variable '{var_name}' is not set. "
                    f"Set it in your shell config (e.g., export {var_name}=...)"
                )
            # For non-strict, check XDG defaults
            if var_name in xdg_defaults:
                return xdg_defaults[var_name]
            raise EnvVarNotSetError(
                f"Environment variable '{var_name}' is not set and has no default."
            )
        return env_value

    value = re.sub(r"\$\{env:(\w+)\}", replace_env, value)

    # Handle ${VAR} pattern (XDG vars)
    def replace_xdg(match):
        var_name = match.group(1)
        env_value = os.environ.get(var_name)
        if env_value is None:
            if strict:
                raise EnvVarNotSetError(
                    f"Environment variable '{var_name}' is not set. "
                    f"Set it in your shell config (e.g., export {var_name}=...)"
                )
            # For non-strict, check XDG defaults
            if var_name in xdg_defaults:
                return xdg_defaults[var_name]
            raise EnvVarNotSetError(
                f"Environment variable '{var_name}' is not set and has no default."
            )
        return env_value

    value = re.sub(r"\$\{(\w+)\}", replace_xdg, value)

    return value


@dataclass
class StorageProvider:
    """
    Unified access to all storage backends.

    Instantiated from infrastructure.yaml at startup.
    Injected into LifecycleManager, MembraneAgent, etc.

    Usage:
        storage = await StorageProvider.from_config()
        await storage.relational.execute("SELECT ...")
        results = await storage.vector.search(query_vec)
    """

    relational: IRelationalStore
    vector: IVectorStore
    blob: IBlobStore
    telemetry: ITelemetryStore
    config: InfrastructureConfig
    paths: XDGPaths

    @classmethod
    async def from_config(
        cls,
        config_path: Path | None = None,
        paths: XDGPaths | None = None,
    ) -> "StorageProvider":
        """
        Load infrastructure.yaml and instantiate providers.

        Falls back to local SQLite if no config exists.

        Args:
            config_path: Path to infrastructure.yaml (default: ~/.config/kgents/infrastructure.yaml)
            paths: XDG paths (default: auto-resolved)
        """
        paths = paths or XDGPaths.resolve()
        config_path = config_path or (paths.config / "infrastructure.yaml")

        if config_path.exists():
            try:
                with open(config_path) as f:
                    content = f.read()
                    # Try YAML first, fall back to JSON
                    if HAS_YAML:
                        raw_config = yaml.safe_load(content)
                    else:
                        raw_config = json.loads(content)
                config = InfrastructureConfig.from_dict(raw_config)
            except Exception:
                # Fall back to defaults on any config error
                config = InfrastructureConfig.default(paths)
        else:
            config = InfrastructureConfig.default(paths)

        return await cls._create_from_config(config, paths)

    @classmethod
    async def from_config_dict(
        cls,
        config_dict: dict[str, Any],
        paths: XDGPaths | None = None,
    ) -> "StorageProvider":
        """Create from config dict (useful for testing)."""
        paths = paths or XDGPaths.resolve()
        config = InfrastructureConfig.from_dict(config_dict)
        return await cls._create_from_config(config, paths)

    @classmethod
    async def _create_from_config(
        cls,
        config: InfrastructureConfig,
        paths: XDGPaths,
    ) -> "StorageProvider":
        """Create providers from config."""
        relational = await cls._create_relational(config.relational)
        vector = await cls._create_vector(config.vector)
        blob = await cls._create_blob(config.blob)
        telemetry = await cls._create_telemetry(config.telemetry)

        return cls(
            relational=relational,
            vector=vector,
            blob=blob,
            telemetry=telemetry,
            config=config,
            paths=paths,
        )

    @classmethod
    async def _create_relational(cls, config: ProviderConfig) -> IRelationalStore:
        """Create relational store from config."""
        if config.type == "sqlite":
            # Use strict=False to gracefully use XDG defaults if env vars unset
            connection = _expand_env_vars(config.connection or "", strict=False)
            store = SQLiteRelationalStore(connection, wal_mode=config.wal_mode)
            # Ensure connection is established
            await store._ensure_connection()
            return store
        elif config.type == "memory":
            return InMemoryRelationalStore()
        else:
            raise ValueError(f"Unknown relational provider type: {config.type}")

    @classmethod
    async def _create_vector(cls, config: ProviderConfig) -> IVectorStore:
        """Create vector store from config."""
        if config.type in ("numpy", "numpy-cosine"):
            path = _expand_env_vars(config.path or "", strict=False)
            store = NumpyVectorStore(path, dimensions=config.dimensions)
            await store.initialize()
            return store
        elif config.type == "memory":
            return InMemoryVectorStore(dimensions=config.dimensions)
        else:
            # Default to numpy for unknown types
            path = _expand_env_vars(config.path or "", strict=False)
            store = NumpyVectorStore(path, dimensions=config.dimensions)
            await store.initialize()
            return store

    @classmethod
    async def _create_blob(cls, config: ProviderConfig) -> IBlobStore:
        """Create blob store from config."""
        if config.type == "filesystem":
            path = _expand_env_vars(config.path or "", strict=False)
            return FilesystemBlobStore(path)
        elif config.type == "memory":
            return InMemoryBlobStore()
        else:
            raise ValueError(f"Unknown blob provider type: {config.type}")

    @classmethod
    async def _create_telemetry(cls, config: ProviderConfig) -> ITelemetryStore:
        """Create telemetry store from config."""
        if config.type == "sqlite":
            connection = _expand_env_vars(config.connection or "", strict=False)
            return SQLiteTelemetryStore(connection)
        elif config.type == "memory":
            return InMemoryTelemetryStore()
        else:
            raise ValueError(f"Unknown telemetry provider type: {config.type}")

    @classmethod
    async def create_minimal(cls) -> "StorageProvider":
        """
        Create minimal in-memory provider for error recovery.

        Used when normal initialization fails.
        """
        paths = XDGPaths.resolve()
        config = InfrastructureConfig(
            profile="minimal-fallback",
            relational=ProviderConfig(type="memory"),
            vector=ProviderConfig(type="memory"),
            blob=ProviderConfig(type="memory"),
            telemetry=ProviderConfig(type="memory"),
        )

        return cls(
            relational=InMemoryRelationalStore(),
            vector=InMemoryVectorStore(),
            blob=InMemoryBlobStore(),
            telemetry=InMemoryTelemetryStore(),
            config=config,
            paths=paths,
        )

    async def close(self) -> None:
        """Close all providers."""
        await self.relational.close()
        await self.vector.close()
        await self.blob.close()
        await self.telemetry.close()

    async def run_migrations(self) -> None:
        """
        Run database migrations.

        Creates tables if they don't exist.
        Future: Alembic migrations for schema changes.
        """
        # Core schema for membrane.db
        membrane_schema = """
        -- Instances table: tracks active kgent instances
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            hostname TEXT NOT NULL,
            pid INTEGER NOT NULL,
            project_path TEXT,
            project_hash TEXT,
            started_at TEXT NOT NULL,
            last_heartbeat TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE INDEX IF NOT EXISTS idx_instances_status ON instances(status);
        CREATE INDEX IF NOT EXISTS idx_instances_project ON instances(project_hash);

        -- Shapes table: observed patterns
        CREATE TABLE IF NOT EXISTS shapes (
            id TEXT PRIMARY KEY,
            shape_type TEXT NOT NULL,
            intensity REAL NOT NULL DEFAULT 1.0,
            persistence REAL NOT NULL DEFAULT 1.0,
            interpretation TEXT,
            project_hash TEXT,
            instance_id TEXT,
            observed_at TEXT NOT NULL,
            embedding_status TEXT DEFAULT 'none'
        );

        CREATE INDEX IF NOT EXISTS idx_shapes_type ON shapes(shape_type);
        CREATE INDEX IF NOT EXISTS idx_shapes_project ON shapes(project_hash);
        CREATE INDEX IF NOT EXISTS idx_shapes_observed ON shapes(observed_at DESC);

        -- Dreams table: consolidated insights
        CREATE TABLE IF NOT EXISTS dreams (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source_shapes TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            dreamed_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_dreams_dreamed ON dreams(dreamed_at DESC);

        -- Embedding metadata: tracks model versions
        CREATE TABLE IF NOT EXISTS embedding_metadata (
            source_id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            dimensions INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            needs_reembed INTEGER DEFAULT 0,
            content TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_embedding_reembed ON embedding_metadata(needs_reembed);

        -- Schema version
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        INSERT OR IGNORE INTO schema_version (version, applied_at)
        VALUES (1, datetime('now'));
        """

        await self.relational.execute(membrane_schema)
