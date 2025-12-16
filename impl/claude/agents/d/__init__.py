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

Use DgentRouter for all persistence needs - it auto-selects the best backend.
"""

from .datum import Datum

# Errors
from .errors import (
    StateCorruptionError,
    StateError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
)

# Protocols
from .protocol import BaseDgent, DgentProtocol

# Router and Bus
from .router import DgentRouter
from .bus import BusEnabledDgent, DataBus, DataEvent, DataEventType

# Auto-Upgrader
from .upgrader import AutoUpgrader, DatumStats, UpgradePolicy, migrate_data, verify_migration

# Backends
from .backends import (
    JSONLBackend,
    MemoryBackend,
    PostgresBackend,
    SQLiteBackend,
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

# Legacy support (DEPRECATED - kept for backward compatibility)
from .volatile import VolatileAgent
from .persistent import PersistentAgent
from .symbiont import Symbiont
from .legacy import (
    MemoryConfig,
    MemoryLoadResponse,
    MemoryPolynomialAgent,
    UnifiedMemory,
    WitnessReport,
)
from .state_monad import StateMonadFunctor

__all__ = [
    # Core Types
    "Datum",
    # Protocols
    "DgentProtocol",
    "BaseDgent",
    # Backends
    "MemoryBackend",
    "JSONLBackend",
    "SQLiteBackend",
    "PostgresBackend",
    # Router
    "DgentRouter",
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
    # Legacy (DEPRECATED)
    "VolatileAgent",
    "PersistentAgent",
    "Symbiont",
    "MemoryConfig",
    "MemoryLoadResponse",
    "MemoryPolynomialAgent",
    "UnifiedMemory",
    "WitnessReport",
    "StateMonadFunctor",
]
