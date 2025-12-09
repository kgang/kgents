"""Error types for D-gents (Data Agents)."""


class StateError(Exception):
    """Base exception for D-gent errors."""


class StateNotFoundError(StateError):
    """State does not exist (e.g., first access to persistent store)."""


class StateCorruptionError(StateError):
    """Stored state is invalid or corrupted."""


class StateSerializationError(StateError):
    """State cannot be encoded for storage."""


class StorageError(StateError):
    """Backend storage operation failed."""


# Noosphere Layer Errors


class NoosphereError(StateError):
    """Base for Noosphere layer errors."""


class SemanticError(NoosphereError):
    """Semantic manifold operation failed."""


class TemporalError(NoosphereError):
    """Temporal witness operation failed."""


class LatticeError(NoosphereError):
    """Relational lattice operation failed."""


class VoidNotFoundError(SemanticError):
    """No unexplored regions detected."""


class DriftDetectionError(TemporalError):
    """Could not analyze drift (insufficient data)."""


class NodeNotFoundError(LatticeError):
    """Node does not exist in lattice."""


class EdgeNotFoundError(LatticeError):
    """Edge does not exist in lattice."""
