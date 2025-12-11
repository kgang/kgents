"""
Storage providers for the infrastructure layer.

This module provides concrete implementations of the storage protocols:
- SQLiteRelationalStore: SQLite-based relational storage
- NumpyVectorStore: Numpy-based vector storage (local-first)
- FilesystemBlobStore: Filesystem-based blob storage
- SQLiteTelemetryStore: SQLite-based telemetry storage

From the critique (Mycelium Protocol):
    "Instead of relying on a central Instance DB to lock state,
    D-gents should use Conflict-free Replicated Data Types (CRDTs)."

Future providers will implement CRDT-based backends for local-first
multi-instance coordination without central locking.

Provider Selection:
    Providers are selected based on InfrastructureConfig.
    The factory function create_providers() handles instantiation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import from existing protocols/cli/instance_db/providers
# This bridges the gap during migration
from protocols.cli.instance_db.providers.sqlite import (
    FilesystemBlobStore,
    InMemoryBlobStore,
    InMemoryRelationalStore,
    InMemoryTelemetryStore,
    InMemoryVectorStore,
    NumpyVectorStore,
    SQLiteRelationalStore,
    SQLiteTelemetryStore,
)

from ..ground import InfrastructureConfig, XDGPaths
from ..storage import (
    IBlobStore,
    IRelationalStore,
    ITelemetryStore,
    IVectorStore,
)

__all__ = [
    # Concrete implementations
    "SQLiteRelationalStore",
    "NumpyVectorStore",
    "FilesystemBlobStore",
    "SQLiteTelemetryStore",
    # In-memory implementations (for testing/fallback)
    "InMemoryRelationalStore",
    "InMemoryVectorStore",
    "InMemoryBlobStore",
    "InMemoryTelemetryStore",
    # Factory
    "create_providers",
]


async def create_providers(
    config: InfrastructureConfig,
    paths: XDGPaths,
) -> tuple[IRelationalStore, IVectorStore, IBlobStore, ITelemetryStore]:
    """
    Create storage providers from configuration.

    This factory implements Infrastructure-as-Code:
    - Configuration declares WHAT providers to use
    - This function creates HOW they are instantiated

    From spec/principles.md (Generative):
        "Spec captures judgment; implementation follows mechanically."

    The config is the spec; this function is the mechanical derivation.
    """
    # Relational provider
    relational: IRelationalStore
    if config.relational.type == "sqlite":
        connection = config.relational.connection or str(paths.data / "membrane.db")
        relational = SQLiteRelationalStore(
            db_path=Path(connection),
            wal_mode=config.relational.wal_mode,
        )
    elif config.relational.type == "memory":
        relational = InMemoryRelationalStore()
    else:
        raise ValueError(f"Unknown relational provider: {config.relational.type}")

    # Vector provider
    vector: IVectorStore
    if config.vector.type == "numpy":
        vector_path = config.vector.path or str(paths.data / "vectors.json")
        vector = NumpyVectorStore(
            dimension=config.vector.dimensions,
            persistence_path=Path(vector_path),
        )
    elif config.vector.type == "memory":
        vector = InMemoryVectorStore(dimension=config.vector.dimensions)
    else:
        raise ValueError(f"Unknown vector provider: {config.vector.type}")

    # Blob provider
    blob: IBlobStore
    if config.blob.type == "filesystem":
        blob_path = config.blob.path or str(paths.data / "blobs")
        blob = FilesystemBlobStore(base_path=Path(blob_path))
    elif config.blob.type == "memory":
        blob = InMemoryBlobStore()
    else:
        raise ValueError(f"Unknown blob provider: {config.blob.type}")

    # Telemetry provider
    telemetry: ITelemetryStore
    if config.telemetry.type == "sqlite":
        telemetry_connection = config.telemetry.connection or str(
            paths.data / "telemetry.db"
        )
        telemetry = SQLiteTelemetryStore(db_path=Path(telemetry_connection))
    elif config.telemetry.type == "memory":
        telemetry = InMemoryTelemetryStore()
    else:
        raise ValueError(f"Unknown telemetry provider: {config.telemetry.type}")

    return relational, vector, blob, telemetry
