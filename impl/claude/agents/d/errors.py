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
