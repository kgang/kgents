"""
Schema - Versioned data contracts.

Schemas define the shape of data, version evolution, and migration paths.
They are code, not database DDL. Frozen dataclasses are the contracts.

Spec: spec/protocols/unified-data-crystal.md
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Schema(Generic[T]):
    """
    A versioned data contract.

    Schemas in kgents are not database migrations - they're code.
    Each version is a frozen dataclass. Migrations are pure functions.

    Philosophy:
    - Schemas version like code, not like databases
    - Migration functions are declarative, composable
    - Unknown schemas degrade gracefully to raw Datum
    - Old data auto-upgrades lazily on read

    Attributes:
        name: Qualified schema name (e.g., "witness.mark", "brain.crystal")
        version: Monotonic version number (1, 2, 3...)
        contract: The frozen dataclass type defining structure
        migrations: Dict mapping version -> upgrade function

    Example:
        >>> @dataclass(frozen=True)
        ... class MarkV1:
        ...     action: str
        ...     reasoning: str
        ...
        >>> @dataclass(frozen=True)
        ... class MarkV2:
        ...     action: str
        ...     reasoning: str
        ...     tags: tuple[str, ...] = ()
        ...
        >>> schema = Schema(
        ...     name="witness.mark",
        ...     version=2,
        ...     contract=MarkV2,
        ...     migrations={
        ...         1: lambda d: {**d, "tags": ()},  # v1 -> v2
        ...     },
        ... )
    """

    name: str
    """Qualified schema name. Use dot notation: 'domain.type'."""

    version: int
    """Current schema version. Must be monotonic (1, 2, 3...)."""

    contract: type[T]
    """The frozen dataclass type defining the structure."""

    migrations: dict[int, Callable[[dict[str, Any]], dict[str, Any]]] = field(
        default_factory=dict
    )
    """Migration functions. Key is source version (v1->v2 is keyed by 1)."""

    def parse(self, data: dict[str, Any]) -> T:
        """
        Parse raw data into typed contract.

        This assumes data is already at the current schema version.
        Use upgrade() first if dealing with old data.

        Args:
            data: Raw dictionary matching contract structure

        Returns:
            Typed instance of contract

        Raises:
            TypeError: If data doesn't match contract signature
        """
        # Filter out metadata fields that aren't part of the contract
        filtered = {
            k: v for k, v in data.items()
            if not k.startswith("_")
        }
        return self.contract(**filtered)

    def upgrade(self, old_version: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        Upgrade data from old version to current.

        Applies migration functions sequentially:
        v1 -> v2 -> v3 -> ... -> current

        Args:
            old_version: The version of the input data
            data: The raw data at old_version

        Returns:
            Data upgraded to current version

        Raises:
            ValueError: If old_version > current version
        """
        if old_version > self.version:
            raise ValueError(
                f"Cannot downgrade from v{old_version} to v{self.version}"
            )

        if old_version == self.version:
            return data

        # Apply migrations sequentially
        current_data = data.copy()
        for v in range(old_version, self.version):
            if v in self.migrations:
                current_data = self.migrations[v](current_data)

        return current_data

    def to_dict(self, value: T) -> dict[str, Any]:
        """
        Convert typed value to raw dictionary.

        Includes schema metadata (_schema, _version) for persistence.

        Args:
            value: Typed instance of contract

        Returns:
            Dictionary with data + metadata
        """
        data = asdict(value) if hasattr(value, "__dataclass_fields__") else dict(value)  # type: ignore
        return {
            **data,
            "_schema": self.name,
            "_version": self.version,
        }

    def can_upgrade(self, old_version: int) -> bool:
        """
        Check if we can upgrade from old_version to current.

        Returns True if:
        - old_version == current (no upgrade needed)
        - All migration functions exist for the path

        Args:
            old_version: Version to check upgrade path from

        Returns:
            True if upgrade is possible
        """
        if old_version == self.version:
            return True

        if old_version > self.version:
            return False

        # Check all migrations exist
        for v in range(old_version, self.version):
            if v not in self.migrations:
                return False

        return True
