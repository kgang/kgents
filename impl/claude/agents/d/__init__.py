"""
D-gents: Data Agents for stateful computation.

This package provides the core abstractions for data persistence in kgents.

Architecture (data-architecture-rewrite):
- DgentProtocol: 5 core methods (put, get, delete, list, causal_chain)
- Datum: Frozen dataclass for all data storage
- Backends: Memory, JSONL, SQLite, Postgres (projection lattice)
- DgentRouter: Automatic backend selection with graceful degradation
- DataBus: Reactive event propagation
- AutoUpgrader: Data promotion across tiers
- Universe: Higher-level schema-aware data management

Use DgentRouter for low-level Datum storage.
Use Universe for typed objects (Crystal, Mark, etc.) with schema awareness.
"""

# Adapters (Dual-Track Architecture)
# AGENTESE Node (self.data.*)
from . import node  # noqa: F401 - imported for @node registration side-effect
from .adapters import TableAdapter

# Backends
from .backends import (
    JSONLBackend,
    MemoryBackend,
    PostgresBackend,
    SQLiteBackend,
)
from .bus import BusEnabledDgent, DataBus, DataEvent, DataEventType
from .datum import Datum

# Errors
from .errors import (
    StateCorruptionError,
    StateError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
)

# Optics (schema-at-read)
from .lens import (
    Lens,
    LensValidation,
    Prism,
    Traversal,
    attr_lens,
    dict_items_traversal,
    dict_keys_traversal,
    dict_values_traversal,
    field_lens,
    identity_lens,
    index_lens,
    key_lens,
    list_traversal,
    optional_field_prism,
    optional_index_prism,
    optional_key_prism,
    validate_composed_lens,
    verify_get_put_law,
    verify_lens_laws,
    verify_prism_laws,
    verify_put_get_law,
    verify_put_put_law,
    verify_traversal_laws,
)
from .lens_agent import LensAgent, focused
from .persistent import PersistentAgent

# Protocols (dual interface - see protocol.py)
from .protocol import BaseDgent, DataAgent, DgentProtocol

# Router and Bus
from .router import Backend, BackendStatus, DgentRouter
from .state_monad import StateMonadFunctor
from .symbiont import Symbiont

# Universe (schema-aware data management)
from .universe import (
    Backend as UniverseBackend,
    DataclassSchema,
    Query,
    Schema,
    Universe,
    UniverseStats,
    get_universe,
    init_universe,
)

# Auto-Upgrader
from .upgrader import (
    AutoUpgrader,
    DatumStats,
    UpgradePolicy,
    migrate_data,
    verify_migration,
)

# Core stateful agents (NOT deprecated - actively used)
from .volatile import VolatileAgent

# Legacy stubs removed - deprecated classes deleted:
# - UnifiedMemory, MemoryConfig, MemoryLoadResponse
# - MemoryPolynomialAgent, WitnessReport
# Use DgentProtocol, DataBus, PolyAgent instead.

__all__ = [
    # Core Types
    "Datum",
    # Protocols (dual interface)
    "DgentProtocol",
    "DataAgent",
    "BaseDgent",
    # Backends
    "MemoryBackend",
    "JSONLBackend",
    "SQLiteBackend",
    "PostgresBackend",
    # Router
    "Backend",
    "BackendStatus",
    "DgentRouter",
    # Universe (schema-aware)
    "Universe",
    "UniverseBackend",
    "Schema",
    "DataclassSchema",
    "Query",
    "UniverseStats",
    "get_universe",
    "init_universe",
    # Bus
    "DataBus",
    "DataEvent",
    "DataEventType",
    "BusEnabledDgent",
    # Upgrader
    "AutoUpgrader",
    "UpgradePolicy",
    "DatumStats",
    "migrate_data",
    "verify_migration",
    # Errors
    "StateError",
    "StateNotFoundError",
    "StateCorruptionError",
    "StateSerializationError",
    "StorageError",
    # Optics
    "Lens",
    "Prism",
    "Traversal",
    "LensValidation",
    "key_lens",
    "field_lens",
    "index_lens",
    "identity_lens",
    "attr_lens",
    "optional_key_prism",
    "optional_field_prism",
    "optional_index_prism",
    "list_traversal",
    "dict_values_traversal",
    "dict_keys_traversal",
    "dict_items_traversal",
    "verify_lens_laws",
    "verify_get_put_law",
    "verify_put_get_law",
    "verify_put_put_law",
    "verify_prism_laws",
    "verify_traversal_laws",
    "validate_composed_lens",
    "LensAgent",
    "focused",
    # Adapters
    "TableAdapter",
    # Core stateful agents (not deprecated)
    "VolatileAgent",
    "PersistentAgent",
    "Symbiont",
    "StateMonadFunctor",
]
