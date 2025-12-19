"""
PersistentAgent: File-backed state with atomic writes.

Provides durable state storage using JSON serialization,
atomic file operations, and append-only history (JSONL).
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Generic,
    List,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from .errors import (
    StateCorruptionError,
    StateNotFoundError,
    StateSerializationError,
    StorageError,
)

S = TypeVar("S")


class PersistentAgent(Generic[S]):
    """
    File-backed D-gent with atomic writes and JSONL history.

    Features:
    - JSON serialization (dataclasses and primitives)
    - Atomic writes (temp file + rename)
    - JSONL history (append-only, survives crash)
    - Crash recovery (survives process restart)

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class UserProfile:
        ...     name: str
        ...     age: int
        ...
        >>> dgent = PersistentAgent(
        ...     path=Path("user.json"),
        ...     schema=UserProfile
        ... )
        >>> await dgent.save(UserProfile(name="Alice", age=30))
        >>> profile = await dgent.load()
        >>> profile.name
        'Alice'
    """

    def __init__(
        self,
        path: Path | str,
        schema: Type[S],
        max_history: int = 100,
    ) -> None:
        """
        Initialize persistent D-gent.

        Args:
            path: Path to JSON file for current state
            schema: Type of state (for deserialization)
            max_history: Max history entries in JSONL file
        """
        self.path = Path(path)
        self.schema = schema
        self.max_history = max_history

        # History stored in .jsonl file alongside main state
        self.history_path = self.path.with_suffix(self.path.suffix + ".jsonl")

    async def load(self) -> S:
        """
        Load state from file.

        Returns:
            Deserialized state

        Raises:
            StateNotFoundError: If file doesn't exist
            StateCorruptionError: If JSON is invalid
        """
        if not self.path.exists():
            raise StateNotFoundError(f"No state at {self.path}")

        try:
            with open(self.path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Invalid JSON in {self.path}: {e}")
        except Exception as e:
            raise StorageError(f"Failed to read {self.path}: {e}")

        # Deserialize based on schema
        return self._deserialize(data)

    async def save(self, state: S) -> None:
        """
        Atomically save state to file + append to history.

        Args:
            state: State to persist

        Raises:
            StateSerializationError: If state can't be serialized
            StorageError: If write fails
        """
        # Serialize state
        serialized = self._serialize(state)

        try:
            # Ensure parent directory exists
            self.path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write: temp file + rename
            temp_path = self.path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(serialized, f, indent=2)

            # Atomic rename (POSIX guarantees)
            temp_path.replace(self.path)

            # Append to history (JSONL)
            await self._append_history(serialized)

        except Exception as e:
            raise StorageError(f"Failed to save state to {self.path}: {e}")

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Load historical states from JSONL file.

        Args:
            limit: Max entries to return (newest first)

        Returns:
            List of historical states (excludes current)
        """
        if not self.history_path.exists():
            return []

        try:
            entries = []
            with open(self.history_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entries.append(self._deserialize(data))

            # Return newest first, apply limit
            entries.reverse()
            return entries[:limit] if limit else entries

        except Exception:
            # History corruption shouldn't crash - just return empty
            return []

    async def _append_history(self, serialized: Any) -> None:
        """
        Append serialized state to JSONL history file.

        Implements bounded history: keeps max_history entries.
        """
        try:
            # Read existing history
            entries = []
            if self.history_path.exists():
                with open(self.history_path, "r") as f:
                    entries = [line.strip() for line in f if line.strip()]

            # Add new entry
            entries.append(json.dumps(serialized))

            # Enforce max_history (keep newest)
            if len(entries) > self.max_history:
                entries = entries[-self.max_history :]

            # Write back
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w") as f:
                f.write("\n".join(entries) + "\n")

        except Exception:
            # History failure shouldn't crash save operation
            pass

    def _serialize(self, state: S) -> Any:
        """
        Serialize state to JSON-compatible structure.

        Supports:
        - Primitives (str, int, float, bool, None)
        - Collections (list, dict)
        - Dataclasses (converted to dict)
        - Enums (converted to their value)

        Raises:
            StateSerializationError: If state contains non-serializable types
        """

        def enum_serializer(obj: Any) -> Any:
            """Convert enums to their values for JSON serialization."""
            if isinstance(obj, Enum):
                return obj.value
            return obj

        try:
            if is_dataclass(state):
                return asdict(
                    state,  # type: ignore[arg-type]
                    dict_factory=lambda x: {k: enum_serializer(v) for k, v in x},
                )
            return state
        except Exception as e:
            raise StateSerializationError(f"Cannot serialize state: {e}")

    def _deserialize(self, data: Any) -> S:
        """
        Deserialize JSON data to state type.

        Recursively handles nested dataclasses.

        Args:
            data: JSON-compatible data structure

        Returns:
            State instance of type S

        Raises:
            StateCorruptionError: If data doesn't match schema
        """
        try:
            if is_dataclass(self.schema):
                return self._deserialize_dataclass(self.schema, data)  # type: ignore
            return data  # type: ignore
        except Exception as e:
            raise StateCorruptionError(f"Cannot deserialize to {self.schema}: {e}")

    def _deserialize_dataclass(self, cls: Type[Any], data: dict[str, Any]) -> Any:
        """
        Recursively deserialize a dataclass and its nested dataclass fields.

        Handles:
        - Nested dataclasses (recursively reconstructed)
        - Enums (reconstructed from string values)
        - Lists of dataclasses or enums
        - Primitives and collections (passed through)

        Args:
            cls: The dataclass type to instantiate
            data: Dict of field values (may contain nested dicts)

        Returns:
            Instance of cls with all nested dataclasses properly constructed
        """
        if not isinstance(data, dict):
            return data

        # Get type hints for this dataclass
        try:
            type_hints = get_type_hints(cls)
        except Exception:
            # Fallback if type hints fail
            type_hints = {}

        # Build kwargs with recursively deserialized fields
        kwargs: dict[str, Any] = {}
        for field_name, field_value in data.items():
            field_type = type_hints.get(field_name)

            # Handle None values
            if field_value is None:
                kwargs[field_name] = None
            elif field_type and is_dataclass(field_type):
                # Recursively deserialize nested dataclass
                kwargs[field_name] = self._deserialize_dataclass(field_type, field_value)
            elif field_type:
                # Try to handle enums (check if it's an Enum class)
                try:
                    if isinstance(field_type, type) and issubclass(field_type, Enum):
                        # Reconstruct enum from its value
                        kwargs[field_name] = field_type(field_value)
                        continue
                except TypeError:
                    # Not a simple type, might be a generic like list[X]
                    pass

                # Handle lists of complex types
                if isinstance(field_value, list) and field_value:
                    # Get the generic type if available (e.g., list[Hypothesis])
                    origin = get_origin(field_type)
                    if origin is list:
                        args = get_args(field_type)
                        if args and is_dataclass(args[0]):
                            # List of dataclasses
                            # args[0] from get_args is always a type, not an instance
                            item_type = cast(Type[Any], args[0])
                            kwargs[field_name] = [
                                self._deserialize_dataclass(item_type, item)
                                if isinstance(item, dict)
                                else item
                                for item in field_value
                            ]
                            continue

                # Default: use as-is
                kwargs[field_name] = field_value
            else:
                # No type hint - use as-is
                kwargs[field_name] = field_value

        return cls(**kwargs)
