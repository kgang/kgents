"""
Datum - The irreducible atom of data.

The Datum is ground truth. Schema-free, always works, immutable.
Every piece of data in kgents starts as a Datum before crystallization.

Spec: spec/protocols/unified-data-crystal.md
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Datum:
    """
    The irreducible atom of data.

    A Datum is:
    - Schema-free: No contract enforcement, just raw dict
    - Immutable: Frozen dataclass ensures no mutation
    - Timestamped: Created at is set once, never changes
    - Provenanced: Tracks author, source, and lineage
    - Taggable: Classification via frozenset (immutable)

    Philosophy:
    The Datum is the fallback. When schemas fail, when versions mismatch,
    when the world is uncertain - the Datum persists. It is the bedrock
    upon which all Crystals are built.

    Example:
        >>> datum = Datum(
        ...     id=str(uuid4()),
        ...     created_at=datetime.now(UTC),
        ...     data={"action": "implemented datum", "reasoning": "foundation"},
        ...     tags=frozenset(["witness", "foundation"]),
        ...     author="claude",
        ... )
    """

    id: str
    """Unique identifier (typically UUID)."""

    created_at: datetime
    """Immutable timestamp. When this datum came into existence."""

    data: dict[str, Any]
    """The raw payload. Schema-free, just data."""

    tags: frozenset[str] = field(default_factory=frozenset)
    """Classification tags. Immutable set for categorization."""

    author: str = "system"
    """Who created this datum. Defaults to 'system'."""

    source: str | None = None
    """Where this datum came from. Could be a service, file, URL, etc."""

    parent_id: str | None = None
    """Causal lineage. If this datum was derived from another, track it."""

    @classmethod
    def create(
        cls,
        data: dict[str, Any],
        *,
        tags: frozenset[str] | set[str] | None = None,
        author: str = "system",
        source: str | None = None,
        parent_id: str | None = None,
    ) -> "Datum":
        """
        Convenient factory for creating a Datum with auto-generated ID and timestamp.

        Args:
            data: The raw payload
            tags: Classification tags (converted to frozenset)
            author: Who created this
            source: Where it came from
            parent_id: Parent datum ID if derived

        Returns:
            A new Datum with generated ID and current timestamp
        """
        return cls(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            data=data,
            tags=frozenset(tags) if tags else frozenset(),
            author=author,
            source=source,
            parent_id=parent_id,
        )

    def with_tags(self, *new_tags: str) -> "Datum":
        """
        Create a new Datum with additional tags.

        Since Datum is frozen, this returns a new instance.

        Args:
            *new_tags: Tags to add

        Returns:
            New Datum with merged tags
        """
        return Datum(
            id=self.id,
            created_at=self.created_at,
            data=self.data,
            tags=self.tags | frozenset(new_tags),
            author=self.author,
            source=self.source,
            parent_id=self.parent_id,
        )

    def replace(self, **changes: Any) -> "Datum":
        """
        Create a new Datum with specified fields replaced.

        Uses dataclass replace semantics.

        Args:
            **changes: Fields to replace

        Returns:
            New Datum with changes applied
        """
        from dataclasses import replace
        return replace(self, **changes)
