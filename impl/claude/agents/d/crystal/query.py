"""
Query - Declarative query specification for crystals and datums.

NoSQL-like querying without ORM ceremony. Declarative, immutable, composable.

Spec: spec/protocols/unified-data-crystal.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Query:
    """
    Declarative query specification.

    Queries in kgents are NoSQL-like: flexible predicates, no joins,
    backend-agnostic. The Universe handles translation to SQL/memory/etc.

    Philosophy:
    - Queries are data, not strings
    - Immutable specifications enable caching
    - Backend selects optimal execution strategy
    - Degradation: if backend can't support, filters post-fetch

    Attributes:
        schema: Filter by schema name (e.g., "witness.mark")
        tags: Must have ALL these tags (intersection)
        author: Filter by author
        since: Created at or after this time
        until: Created before this time
        limit: Max results to return
        offset: Skip this many results (for pagination)
        where: Flexible predicate dict ({"field": value})
        order_by: Field to order by (default: created_at)
        order_desc: Descending order (default: True)

    Example:
        >>> # Recent witness marks with "eureka" tag by claude
        >>> q = Query(
        ...     schema="witness.mark",
        ...     tags=frozenset(["eureka"]),
        ...     author="claude",
        ...     since=datetime(2025, 12, 1),
        ...     limit=50,
        ... )

        >>> # All brain crystals, oldest first
        >>> q = Query(
        ...     schema="brain.crystal",
        ...     order_by="created_at",
        ...     order_desc=False,
        ... )

        >>> # Complex predicate
        >>> q = Query(
        ...     where={"status": "active", "priority": "high"},
        ...     tags=frozenset(["urgent"]),
        ... )
    """

    schema: str | None = None
    """Filter by schema name. None means all schemas."""

    tags: frozenset[str] = field(default_factory=frozenset)
    """Must have ALL these tags (intersection). Empty means no tag filter."""

    author: str | None = None
    """Filter by author. None means all authors."""

    since: datetime | None = None
    """Created at or after this time. None means no lower bound."""

    until: datetime | None = None
    """Created before this time. None means no upper bound."""

    limit: int = 100
    """Maximum number of results to return."""

    offset: int = 0
    """Skip this many results (for pagination)."""

    where: dict[str, Any] | None = None
    """
    Flexible predicate dictionary.

    Keys are field names, values are expected values.
    Semantics: exact match on all fields (AND conjunction).

    Example:
        where={"status": "active", "priority": 3}
        Matches: datum.data["status"] == "active" AND datum.data["priority"] == 3
    """

    order_by: str = "created_at"
    """Field to order results by. Default is created_at."""

    order_desc: bool = True
    """Order descending (newest first). False for ascending."""

    def with_limit(self, limit: int) -> "Query":
        """
        Create a new Query with different limit.

        Args:
            limit: New limit value

        Returns:
            New Query with updated limit
        """
        from dataclasses import replace
        return replace(self, limit=limit)

    def with_offset(self, offset: int) -> "Query":
        """
        Create a new Query with different offset.

        Args:
            offset: New offset value

        Returns:
            New Query with updated offset
        """
        from dataclasses import replace
        return replace(self, offset=offset)

    def next_page(self) -> "Query":
        """
        Get query for next page of results.

        Returns:
            New Query with offset += limit
        """
        from dataclasses import replace
        return replace(self, offset=self.offset + self.limit)

    def with_schema(self, schema: str) -> "Query":
        """
        Create a new Query filtering by schema.

        Args:
            schema: Schema name to filter by

        Returns:
            New Query with schema filter
        """
        from dataclasses import replace
        return replace(self, schema=schema)

    def with_tags(self, *tags: str) -> "Query":
        """
        Create a new Query with additional tags.

        Tags are intersected (AND): result must have ALL tags.

        Args:
            *tags: Tags to add to filter

        Returns:
            New Query with merged tags
        """
        from dataclasses import replace
        return replace(self, tags=self.tags | frozenset(tags))

    def with_time_range(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> "Query":
        """
        Create a new Query with time range filter.

        Args:
            since: Created at or after (None keeps existing)
            until: Created before (None keeps existing)

        Returns:
            New Query with time range
        """
        from dataclasses import replace
        return replace(
            self,
            since=since if since is not None else self.since,
            until=until if until is not None else self.until,
        )

    def matches_datum(self, datum: Any) -> bool:
        """
        Check if a datum matches this query.

        Used for in-memory filtering. Backends may optimize differently.

        Args:
            datum: Datum to check (must have created_at, data, tags, author)

        Returns:
            True if datum matches all query predicates
        """
        # Schema filter
        if self.schema is not None:
            datum_schema = datum.data.get("_schema")
            if datum_schema != self.schema:
                return False

        # Tag filter (must have ALL)
        if self.tags and not self.tags.issubset(datum.tags):
            return False

        # Author filter
        if self.author is not None and datum.author != self.author:
            return False

        # Time range filters
        if self.since is not None and datum.created_at < self.since:
            return False
        if self.until is not None and datum.created_at >= self.until:
            return False

        # Where predicates
        if self.where:
            for field, expected in self.where.items():
                if datum.data.get(field) != expected:
                    return False

        return True
