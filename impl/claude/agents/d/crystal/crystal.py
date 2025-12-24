"""
Crystal - A typed, versioned datum.

Crystals are Datums that have been validated against a Schema.
They carry both the raw data (always accessible) and the typed value (contract-enforced).

Spec: spec/protocols/unified-data-crystal.md
"""

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Generic, TypeVar

from .datum import Datum
from .schema import Schema

T = TypeVar("T")


@dataclass(frozen=True)
class CrystalMeta:
    """
    Crystal metadata - the schema envelope.

    Tracks which schema contract was applied, when, and provenance.

    Attributes:
        schema_name: Qualified schema name (e.g., "witness.mark")
        schema_version: Version number of schema applied
        created_at: When this crystal was formed (not datum creation time)
        crystallized_from: Source datum ID if this was an upgrade
    """

    schema_name: str
    """The schema contract applied (e.g., 'witness.mark')."""

    schema_version: int
    """Version of schema at crystallization time."""

    created_at: datetime
    """When this crystal was formed (may differ from datum.created_at)."""

    crystallized_from: str | None = None
    """If upgraded from older schema, the source datum ID."""


@dataclass(frozen=True)
class Crystal(Generic[T]):
    """
    A typed, versioned datum.

    A Crystal wraps a Datum with a typed Schema contract. It provides:
    - Type safety via generic parameter T
    - Schema versioning and upgrade tracking
    - Dual access: raw datum (always works) + typed value (contract-enforced)

    Philosophy:
    Crystals are formed by applying pressure (schema) to raw matter (datum).
    The datum persists unchanged. The crystal is a lens through which we
    view it with structure and meaning.

    When schemas change, old crystals don't break - they're re-crystallized
    lazily through migration functions.

    Example:
        >>> @dataclass(frozen=True)
        ... class Mark:
        ...     action: str
        ...     reasoning: str
        ...
        >>> schema = Schema(name="witness.mark", version=1, contract=Mark)
        >>> datum = Datum.create({"action": "test", "reasoning": "example"})
        >>> crystal = Crystal.from_datum(datum, schema)
        >>> crystal.value.action  # Type-safe access
        'test'
        >>> crystal.datum.data    # Raw access always available
        {'action': 'test', 'reasoning': 'example'}
    """

    meta: CrystalMeta
    """Schema metadata - which contract, which version."""

    datum: Datum
    """The underlying raw datum. Always accessible."""

    value: T
    """The typed, validated value per schema contract."""

    @classmethod
    def from_datum(cls, datum: Datum, schema: Schema[T]) -> "Crystal[T]":
        """
        Crystallize a datum into a typed crystal.

        This is the primary factory method. It:
        1. Extracts version from datum if present
        2. Upgrades data if needed
        3. Parses into typed contract
        4. Wraps in Crystal with metadata

        Args:
            datum: Raw datum to crystallize
            schema: Schema contract to apply

        Returns:
            A new Crystal[T] with typed value

        Raises:
            TypeError: If datum.data doesn't match schema contract
        """
        # Extract schema metadata if present
        data = datum.data.copy()
        old_version = data.get("_version", 1)

        # Upgrade if needed
        if old_version < schema.version:
            data = schema.upgrade(old_version, data)
            upgraded_datum = datum.replace(data=data)
        else:
            upgraded_datum = datum

        # Parse into typed contract
        value = schema.parse(data)

        # Form the crystal
        return cls(
            meta=CrystalMeta(
                schema_name=schema.name,
                schema_version=schema.version,
                created_at=datetime.now(UTC),
                crystallized_from=datum.id if old_version < schema.version else None,
            ),
            datum=upgraded_datum,
            value=value,
        )

    @classmethod
    def create(cls, value: T, schema: Schema[T], **datum_kwargs: Any) -> "Crystal[T]":
        """
        Create a new Crystal from a typed value.

        Convenience method that:
        1. Converts typed value to dict
        2. Creates a Datum
        3. Forms Crystal

        Args:
            value: Typed instance matching schema contract
            schema: Schema contract
            **datum_kwargs: Additional Datum fields (tags, author, etc.)

        Returns:
            A new Crystal[T]
        """
        data = schema.to_dict(value)
        datum = Datum.create(data, **datum_kwargs)
        return cls.from_datum(datum, schema)

    def was_upgraded(self) -> bool:
        """
        Check if this crystal was formed by upgrading an older schema version.

        Returns:
            True if crystallized_from is set
        """
        return self.meta.crystallized_from is not None

    def with_tags(self, *tags: str) -> "Crystal[T]":
        """
        Create a new Crystal with additional datum tags.

        Preserves typed value, updates underlying datum.

        Args:
            *tags: Tags to add

        Returns:
            New Crystal with merged tags
        """
        new_datum = self.datum.with_tags(*tags)
        return Crystal(
            meta=self.meta,
            datum=new_datum,
            value=self.value,
        )
