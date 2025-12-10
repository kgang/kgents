"""
Instance DB: The Bicameral Engine

Persistent, local-first memory for kgents instances.

This module implements the canonical instance database at ~/.kgents/,
providing storage abstraction, lifecycle management, and cross-project
memory with git-worktree-like semantics.

Key Components:
- LifecycleManager: Bootstrap, shutdown, mode detection
- StorageProvider: Unified access to all storage backends
- NervousSystem: Fast-path signal routing (Spinal Cord)
- Synapse: Active Inference event bus (surprise-based routing)
- Hippocampus: Short-term memory consolidation
- Repository interfaces: IRelationalStore, IVectorStore, IBlobStore, ITelemetryStore
- SQLite providers: Default local-first implementation

Design Principles:
- Local-first: Works offline, no network by default
- XDG-compliant: Proper directory structure
- Provider abstraction: Backend-agnostic persistence
- Lazy construction: DB created on first shape
- Two-tier routing: Reflexes bypass cortex for O(1) latency
- Active Inference: Signal routing based on surprise
"""

from .interfaces import (
    IRelationalStore,
    IVectorStore,
    IBlobStore,
    ITelemetryStore,
)
from .storage import StorageProvider, XDGPaths, EnvVarNotSetError
from .lifecycle import LifecycleManager, OperationMode, LifecycleState
from .nervous import (
    NervousSystem,
    NervousSystemConfig,
    Signal,
    SignalPriority,
    create_nervous_system,
)
from .synapse import (
    Synapse,
    SynapseConfig,
    PredictiveModel,
    create_synapse,
)
from .hippocampus import (
    Hippocampus,
    HippocampusConfig,
    LetheEpoch,
    create_hippocampus,
)

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
    # Nervous System (Spinal Cord)
    "NervousSystem",
    "NervousSystemConfig",
    "Signal",
    "SignalPriority",
    "create_nervous_system",
    # Synapse (Active Inference)
    "Synapse",
    "SynapseConfig",
    "PredictiveModel",
    "create_synapse",
    # Hippocampus (Short-Term Memory)
    "Hippocampus",
    "HippocampusConfig",
    "LetheEpoch",
    "create_hippocampus",
]
