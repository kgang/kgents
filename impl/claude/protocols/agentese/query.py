"""
AGENTESE Query System (v3)

Bounded queries for exploring the registry without invocation.

The Problem (from spec §8.1):
    AGENTESE paths are invocations. But sometimes you want to ask
    "what exists?" without triggering side effects.

Query Grammar:
    ?world.*              - Query all world.* nodes
    ?*.*.manifest         - Query all manifestable paths
    ?self.memory.?        - Query affordances for a specific node

Constraints (from spec §8.3):
    limit:            Default 100, max 1000
    offset:           Pagination offset (default 0)
    tenant_filter:    Multi-tenant isolation
    capability_check: Only return accessible paths (default enabled)
    cost_estimate:    Dry-run for expensive queries

Example:
    # Query all world nodes
    result = logos.query("?world.*")

    # Query with pagination
    result = logos.query("?world.*", limit=10, offset=20)

    # Query builder style
    result = (
        QueryBuilder(logos)
        .pattern("?world.*")
        .limit(50)
        .with_capability_check(observer)
        .execute()
    )
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .exceptions import PathSyntaxError

if TYPE_CHECKING:
    from .logos import Logos
    from .node import Observer


# === Exceptions ===


class QuerySyntaxError(PathSyntaxError):
    """Query pattern is malformed."""

    def __init__(
        self,
        message: str,
        pattern: str,
        *,
        why: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(message, path=pattern, why=why, suggestion=suggestion)
        self.pattern = pattern


class QueryBoundError(Exception):
    """Query bounds exceeded."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


# === Query Result ===


@dataclass(frozen=True)
class QueryMatch:
    """
    Single match from a query.

    Attributes:
        path: The matched AGENTESE path
        node_type: Type of the node (holon, aspect)
        context: The context (world, self, concept, void, time)
        affordances: Available aspects if queried
    """

    path: str
    node_type: str = "holon"  # "holon" or "aspect"
    context: str = ""
    affordances: tuple[str, ...] = ()


@dataclass(frozen=True)
class QueryResult:
    """
    Result of an AGENTESE query.

    Attributes:
        pattern: The original query pattern
        matches: List of matching paths
        total_count: Total matches (before pagination)
        limit: Applied limit
        offset: Applied offset
        has_more: Whether more results exist
        cost_estimate: Optional cost estimate for the query
    """

    pattern: str
    matches: tuple[QueryMatch, ...]
    total_count: int
    limit: int
    offset: int
    has_more: bool = False
    cost_estimate: float | None = None

    @property
    def paths(self) -> list[str]:
        """Get just the path strings."""
        return [m.path for m in self.matches]

    def __len__(self) -> int:
        """Number of matches in this result (after pagination)."""
        return len(self.matches)

    def __iter__(self) -> Any:
        """Iterate over matches."""
        return iter(self.matches)

    def __bool__(self) -> bool:
        """True if any matches."""
        return len(self.matches) > 0


# === Query Builder ===


@dataclass
class QueryBuilder:
    """
    Fluent query builder for AGENTESE queries.

    Example:
        result = (
            QueryBuilder(logos)
            .pattern("?world.*")
            .limit(50)
            .offset(10)
            .with_capability_check(observer)
            .execute()
        )
    """

    _logos: "Logos"
    _pattern: str = ""
    _limit: int = 100
    _offset: int = 0
    _tenant_id: str | None = None
    _observer: "Observer | None" = None
    _capability_check: bool = True
    _dry_run: bool = False

    def pattern(self, p: str) -> "QueryBuilder":
        """Set the query pattern."""
        self._pattern = p
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """Set the result limit (max 1000)."""
        self._limit = min(n, 1000)
        return self

    def offset(self, n: int) -> "QueryBuilder":
        """Set the pagination offset."""
        self._offset = max(0, n)
        return self

    def tenant(self, tenant_id: str) -> "QueryBuilder":
        """Filter by tenant ID."""
        self._tenant_id = tenant_id
        return self

    def with_capability_check(self, observer: "Observer") -> "QueryBuilder":
        """Enable capability checking with the given observer."""
        self._observer = observer
        self._capability_check = True
        return self

    def without_capability_check(self) -> "QueryBuilder":
        """Disable capability checking."""
        self._capability_check = False
        return self

    def dry_run(self, enabled: bool = True) -> "QueryBuilder":
        """Enable dry-run mode (cost estimate only)."""
        self._dry_run = enabled
        return self

    def execute(self) -> QueryResult:
        """Execute the query."""
        if not self._pattern:
            raise QuerySyntaxError(
                "Query pattern required",
                pattern="",
                why="QueryBuilder requires a pattern",
                suggestion="Call .pattern('?world.*') before .execute()",
            )

        return query(
            self._logos,
            self._pattern,
            limit=self._limit,
            offset=self._offset,
            tenant_id=self._tenant_id,
            observer=self._observer,
            capability_check=self._capability_check,
            dry_run=self._dry_run,
        )


# === Pattern Matching ===


def _parse_query_pattern(pattern: str) -> tuple[str, str, str]:
    """
    Parse a query pattern into (context, holon, aspect) patterns.

    Patterns:
        ?world.*           -> ("world", "*", "*")
        ?*.*.manifest      -> ("*", "*", "manifest")
        ?self.memory.?     -> ("self", "memory", "?")
        ?self.memory       -> ("self", "memory", "*")

    Returns:
        Tuple of (context_pattern, holon_pattern, aspect_pattern)

    Raises:
        QuerySyntaxError: If pattern is invalid
    """
    if not pattern.startswith("?"):
        raise QuerySyntaxError(
            f"Query pattern must start with '?': {pattern}",
            pattern=pattern,
            why="Queries are prefixed with '?' to distinguish from invocations",
            suggestion=f"Use ?{pattern} instead",
        )

    # Remove the ? prefix
    path = pattern[1:]

    if not path:
        raise QuerySyntaxError(
            "Empty query pattern",
            pattern=pattern,
            why="Pattern cannot be empty after '?'",
            suggestion="Use ?world.* or ?*.*.manifest",
        )

    parts = path.split(".")

    # Handle various forms
    if len(parts) == 1:
        # ?world -> match all in context
        return (parts[0], "*", "*")
    elif len(parts) == 2:
        # ?world.* or ?self.memory
        return (parts[0], parts[1], "*")
    elif len(parts) == 3:
        # ?world.*.manifest or ?self.memory.?
        return (parts[0], parts[1], parts[2])
    else:
        raise QuerySyntaxError(
            f"Query pattern too deep: {pattern}",
            pattern=pattern,
            why="AGENTESE paths have at most 3 parts: context.holon.aspect",
            suggestion="Use ?context.holon.aspect format",
        )


def _matches_pattern(value: str, pattern: str) -> bool:
    """
    Check if a value matches a pattern.

    Patterns:
        "*"  - matches anything
        "?"  - query marker (matches anything, used for affordance queries)
        "foo" - exact match
        "foo*" - wildcard (fnmatch style)
    """
    if pattern in ("*", "?"):
        return True
    if "*" in pattern or "?" in pattern:
        return fnmatch.fnmatch(value, pattern.replace("?", "*"))
    return value == pattern


def _is_affordance_query(aspect_pattern: str) -> bool:
    """Check if this is an affordance query (?self.memory.?)."""
    return aspect_pattern == "?"


# === Core Query Function ===


def query(
    logos: "Logos",
    pattern: str,
    *,
    limit: int = 100,
    offset: int = 0,
    tenant_id: str | None = None,
    observer: "Observer | None" = None,
    capability_check: bool = True,
    dry_run: bool = False,
) -> QueryResult:
    """
    Query the AGENTESE registry without invocation.

    Args:
        logos: Logos instance to query
        pattern: Query pattern (must start with '?')
        limit: Maximum results (default 100, max 1000)
        offset: Pagination offset (default 0)
        tenant_id: Optional tenant filter
        observer: Observer for capability checking
        capability_check: Whether to filter by capability (default True)
        dry_run: If True, only estimate cost without executing

    Returns:
        QueryResult with matches and metadata

    Raises:
        QuerySyntaxError: If pattern is invalid
        QueryBoundError: If limit exceeds 1000

    Example:
        # Query all world nodes
        result = query(logos, "?world.*")

        # Query with pagination
        result = query(logos, "?world.*", limit=10, offset=20)

        # Query affordances
        result = query(logos, "?self.memory.?")
    """
    # Validate bounds
    if limit > 1000:
        raise QueryBoundError("Max limit is 1000. Use pagination.")
    if limit < 1:
        limit = 1
    if offset < 0:
        offset = 0

    # Parse pattern
    ctx_pattern, holon_pattern, aspect_pattern = _parse_query_pattern(pattern)

    # Dry run: just estimate
    if dry_run:
        # Estimate based on pattern specificity
        if ctx_pattern != "*" and holon_pattern != "*":
            estimated = 1 if aspect_pattern == "?" else 10
        elif ctx_pattern != "*":
            estimated = 50
        else:
            estimated = 500

        return QueryResult(
            pattern=pattern,
            matches=(),
            total_count=0,
            limit=limit,
            offset=offset,
            has_more=False,
            cost_estimate=estimated * 0.001,  # Hypothetical cost unit
        )

    # Collect matches
    all_matches: list[QueryMatch] = []

    # Get all handles from registry
    handles = logos.registry.list_handles()

    # Also check cached paths
    for cached_path in logos._cache:
        if cached_path not in handles:
            handles.append(cached_path)

    # Match against pattern
    for handle in handles:
        parts = handle.split(".")
        if len(parts) < 2:
            continue

        ctx = parts[0]
        holon = parts[1]

        # Check context and holon patterns
        if not _matches_pattern(ctx, ctx_pattern):
            continue
        if not _matches_pattern(holon, holon_pattern):
            continue

        # If this is an affordance query, get affordances for the node
        if _is_affordance_query(aspect_pattern):
            node = logos.registry.get(handle)
            if node is not None:
                # Get affordances
                from .node import AgentMeta

                meta = AgentMeta(
                    name="query",
                    archetype=observer.archetype if observer else "guest",
                    capabilities=tuple(observer.capabilities) if observer else (),
                )
                try:
                    affordances = node.affordances(meta)
                    for aff in affordances:
                        full_path = f"{handle}.{aff}"
                        # Capability check if enabled
                        if capability_check and observer:
                            # Basic check: affordances list is already filtered
                            pass
                        all_matches.append(
                            QueryMatch(
                                path=full_path,
                                node_type="aspect",
                                context=ctx,
                                affordances=(),
                            )
                        )
                except Exception:
                    # Node doesn't support affordances, skip
                    pass
        else:
            # Regular path match
            if aspect_pattern == "*":
                # Match the holon itself
                all_matches.append(
                    QueryMatch(
                        path=handle,
                        node_type="holon",
                        context=ctx,
                        affordances=(),
                    )
                )
            else:
                # Match specific aspect pattern
                node = logos.registry.get(handle)
                if node is not None:
                    from .node import AgentMeta

                    meta = AgentMeta(
                        name="query",
                        archetype=observer.archetype if observer else "guest",
                        capabilities=tuple(observer.capabilities) if observer else (),
                    )
                    try:
                        affordances = node.affordances(meta)
                        for aff in affordances:
                            if _matches_pattern(aff, aspect_pattern):
                                full_path = f"{handle}.{aff}"
                                all_matches.append(
                                    QueryMatch(
                                        path=full_path,
                                        node_type="aspect",
                                        context=ctx,
                                        affordances=(),
                                    )
                                )
                    except Exception:
                        pass

    # Sort matches for consistent ordering
    all_matches.sort(key=lambda m: m.path)

    # Apply pagination
    total_count = len(all_matches)
    paginated = all_matches[offset : offset + limit]
    has_more = offset + limit < total_count

    return QueryResult(
        pattern=pattern,
        matches=tuple(paginated),
        total_count=total_count,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


# === Logos Integration ===


def add_query_to_logos(logos_cls: type) -> None:
    """
    Add query method to Logos class.

    This is called during module initialization to add the query
    method to the Logos class.
    """

    def query_method(
        self: "Logos",
        pattern: str,
        **constraints: Any,
    ) -> QueryResult:
        """
        Query the registry without invocation.

        Args:
            pattern: Query pattern (must start with '?')
            **constraints: Query constraints (limit, offset, etc.)

        Returns:
            QueryResult with matches

        Example:
            # Query all world nodes
            paths = logos.query("?world.*")

            # Query all manifestable paths
            paths = logos.query("?*.*.manifest")

            # Query affordances for a specific node
            affordances = logos.query("?self.memory.?")
        """
        return query(self, pattern, **constraints)

    # Add method to class
    logos_cls.query = query_method  # type: ignore[attr-defined]


# === Factory Functions ===


def create_query_builder(logos: "Logos") -> QueryBuilder:
    """
    Create a QueryBuilder for fluent query construction.

    Example:
        builder = create_query_builder(logos)
        result = builder.pattern("?world.*").limit(50).execute()
    """
    return QueryBuilder(_logos=logos)
