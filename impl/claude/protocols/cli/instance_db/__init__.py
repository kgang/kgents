"""
Instance DB: The Pocket Cortex

Persistent, local-first memory for kgents instances.

This module implements the canonical instance database at ~/.kgents/,
providing storage abstraction, lifecycle management, and cross-project
memory with git-worktree-like semantics.

Key Components:
- LifecycleManager: Bootstrap, shutdown, mode detection
- StorageProvider: Unified access to all storage backends
- Repository interfaces: IRelationalStore, IVectorStore, IBlobStore, ITelemetryStore
- SQLite providers: Default local-first implementation

Design Principles:
- Local-first: Works offline, no network by default
- XDG-compliant: Proper directory structure
- Provider abstraction: Backend-agnostic persistence
- Lazy construction: DB created on first shape
"""

from .interfaces import (
    IRelationalStore,
    IVectorStore,
    IBlobStore,
    ITelemetryStore,
)
from .storage import StorageProvider, XDGPaths, EnvVarNotSetError
from .lifecycle import LifecycleManager, OperationMode, LifecycleState

__all__ = [
    # Interfaces
    "IRelationalStore",
    "IVectorStore",
    "IBlobStore",
    "ITelemetryStore",
    # Storage
    "StorageProvider",
    "XDGPaths",
    "EnvVarNotSetError",
    # Lifecycle
    "LifecycleManager",
    "OperationMode",
    "LifecycleState",
]
