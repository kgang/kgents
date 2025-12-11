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

from .compost import (
    CompostBin,
    CompostConfig,
    CompostingStrategy,
    CountMinSketch,
    HyperLogLog,
    NutrientBlock,
    TDigestSimplified,
    create_compost_bin,
    create_nutrient_block,
)
from .dreamer import (
    DreamerConfig,
    DreamPhase,
    DreamReport,
    LucidDreamer,
    MaintenanceChunk,
    MaintenanceTaskType,
    NightWatch,
    Question,
    create_lucid_dreamer,
)
from .hippocampus import (
    Hippocampus,
    HippocampusConfig,
    LetheEpoch,
    create_hippocampus,
)
from .interfaces import (
    IBlobStore,
    IRelationalStore,
    ITelemetryStore,
    IVectorStore,
)
from .lethe import (
    ForgetProof,
    LetheGardener,
    LetheGardenerConfig,
    LetheRecord,
    LetheStore,
    RetentionConfig,
    RetentionPolicy,
    create_lethe_gardener,
    create_lethe_store,
)
from .lifecycle import LifecycleManager, LifecycleState, OperationMode
from .nervous import (
    NervousSystem,
    NervousSystemConfig,
    Signal,
    SignalPriority,
    create_nervous_system,
)
from .neurogenesis import (
    ColumnType,
    ISchemaIntrospector,
    MigrationAction,
    MigrationProposal,
    MockSchemaIntrospector,
    NeurogenesisConfig,
    PatternCluster,
    SchemaNeurogenesis,
    TypeInferrer,
    create_schema_neurogenesis,
)
from .storage import EnvVarNotSetError, StorageProvider, XDGPaths
from .synapse import (
    PredictiveModel,
    Synapse,
    SynapseConfig,
    create_synapse,
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
    # Compost (Memory Compression)
    "CompostBin",
    "CompostConfig",
    "CompostingStrategy",
    "NutrientBlock",
    "CountMinSketch",
    "HyperLogLog",
    "TDigestSimplified",
    "create_compost_bin",
    "create_nutrient_block",
    # Lethe (Cryptographic Amnesia)
    "LetheStore",
    "LetheGardener",
    "LetheGardenerConfig",
    "LetheRecord",
    "ForgetProof",
    "RetentionPolicy",
    "RetentionConfig",
    "create_lethe_store",
    "create_lethe_gardener",
    # Lucid Dreamer (Phase 5)
    "LucidDreamer",
    "DreamerConfig",
    "DreamPhase",
    "DreamReport",
    "NightWatch",
    "Question",
    "MaintenanceChunk",
    "MaintenanceTaskType",
    "create_lucid_dreamer",
    # Schema Neurogenesis (Phase 5)
    "SchemaNeurogenesis",
    "NeurogenesisConfig",
    "MigrationProposal",
    "MigrationAction",
    "ColumnType",
    "PatternCluster",
    "TypeInferrer",
    "MockSchemaIntrospector",
    "ISchemaIntrospector",
    "create_schema_neurogenesis",
]
