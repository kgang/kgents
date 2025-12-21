"""
MarkStore: Append-Only Ledger for Marks.

The store enforces the three Mark laws:
- Law 1 (Immutability): Marks cannot be modified after creation
- Law 2 (Causality): link.target.timestamp > link.source.timestamp
- Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark

Pattern 7 from crown-jewel-patterns.md: Append-Only History
"History is a ledger. Modifications are new entries, not edits."

Philosophy:
    The MarkStore is an append-only ledger. You can add traces,
    but you cannot modify or delete them. This provides:
    - Complete audit trail
    - Causal integrity verification
    - Replay capability

See: spec/protocols/warp-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .mark import (
    LinkRelation,
    Mark,
    MarkId,
    MarkLink,
    NPhase,
    PlanPath,
    WalkId,
)

logger = logging.getLogger("kgents.witness.trace_store")


# =============================================================================
# Exceptions
# =============================================================================


class MarkStoreError(Exception):
    """Base exception for trace store errors."""

    pass


class CausalityViolation(MarkStoreError):
    """Raised when a MarkLink violates causality (Law 2)."""

    def __init__(self, source_id: str, target_id: str, source_ts: datetime, target_ts: datetime):
        self.source_id = source_id
        self.target_id = target_id
        self.source_ts = source_ts
        self.target_ts = target_ts
        super().__init__(
            f"Causality violation: target {target_id} ({target_ts}) "
            f"must be after source {source_id} ({source_ts})"
        )


class DuplicateMarkError(MarkStoreError):
    """Raised when attempting to add a trace with an existing ID."""

    def __init__(self, trace_id: MarkId):
        self.trace_id = trace_id
        super().__init__(f"Trace with ID {trace_id} already exists")


class MarkNotFoundError(MarkStoreError):
    """Raised when a referenced trace is not found."""

    def __init__(self, trace_id: MarkId):
        self.trace_id = trace_id
        super().__init__(f"Trace with ID {trace_id} not found")


# =============================================================================
# Query Types
# =============================================================================


@dataclass(frozen=True)
class MarkQuery:
    """
    Query parameters for trace retrieval.

    All parameters are optional. Multiple parameters combine with AND logic.
    """

    # Time range
    after: datetime | None = None
    before: datetime | None = None

    # Origin filter
    origins: tuple[str, ...] | None = None

    # Phase filter
    phases: tuple[NPhase, ...] | None = None

    # Walk filter
    walk_id: WalkId | None = None

    # Tag filter (any match)
    tags: tuple[str, ...] | None = None

    # Link filter (traces with links to/from this ID)
    links_to: MarkId | None = None
    links_from: MarkId | None = None

    # Limit and offset for pagination
    limit: int | None = None
    offset: int = 0

    def matches(self, node: Mark, store: MarkStore) -> bool:
        """Check if a trace node matches this query."""
        # Time range
        if self.after and node.timestamp <= self.after:
            return False
        if self.before and node.timestamp >= self.before:
            return False

        # Origin
        if self.origins and node.origin not in self.origins:
            return False

        # Phase
        if self.phases and node.phase not in self.phases:
            return False

        # Walk
        if self.walk_id and node.walk_id != self.walk_id:
            return False

        # Tags (any match)
        if self.tags:
            if not any(tag in node.tags for tag in self.tags):
                return False

        # Links to (this node has a link TO the specified target)
        if self.links_to:
            if not any(link.target == self.links_to for link in node.links):
                return False

        # Links from (this node has a link FROM the specified source)
        if self.links_from:
            if not any(
                link.source == self.links_from
                or (isinstance(link.source, str) and link.source == str(self.links_from))
                for link in node.links
            ):
                return False

        return True


# =============================================================================
# MarkStore: Append-Only Ledger
# =============================================================================


@dataclass
class MarkStore:
    """
    Append-only ledger for Marks.

    Enforces all three Mark laws:
    - Law 1: Immutability (Marks are frozen dataclasses)
    - Law 2: Causality (append validates timestamp ordering)
    - Law 3: Completeness (no external enforcement, but tracked)

    The store maintains:
    - Primary index by ID
    - Secondary index by timestamp (for range queries)
    - Backlink index (target → sources) for causality traversal

    Example:
        >>> store = MarkStore()
        >>> node = Mark.from_thought("Test", "git", ("test",))
        >>> store.append(node)
        >>> retrieved = store.get(node.id)
        >>> assert retrieved == node
    """

    # Primary storage: ID → Mark
    _nodes: dict[MarkId, Mark] = field(default_factory=dict)

    # Timestamp-ordered list of IDs (for range queries)
    _timeline: list[MarkId] = field(default_factory=list)

    # Backlink index: target_id → list of (source_id, relation)
    _backlinks: dict[MarkId, list[tuple[MarkId | PlanPath, LinkRelation]]] = field(
        default_factory=dict
    )

    # Walk index: walk_id → list of trace_ids
    _walk_index: dict[WalkId, list[MarkId]] = field(default_factory=dict)

    # Persistence path (if any)
    _persistence_path: Path | None = None

    def __post_init__(self) -> None:
        """Initialize secondary indices."""
        # Ensure backlinks dict exists for all nodes
        for node in self._nodes.values():
            for link in node.links:
                if link.target not in self._backlinks:
                    self._backlinks[link.target] = []

    # =========================================================================
    # Core Operations
    # =========================================================================

    def append(self, node: Mark) -> None:
        """
        Append a Mark to the ledger.

        Validates:
        - No duplicate IDs
        - Causality (Law 2) for all links

        Raises:
            DuplicateMarkError: If a trace with this ID exists
            CausalityViolation: If any link violates causality
            MarkNotFoundError: If a link references a non-existent trace
        """
        # Check for duplicate
        if node.id in self._nodes:
            raise DuplicateMarkError(node.id)

        # Validate links (Law 2: causality)
        for link in node.links:
            self._validate_link(node, link)

        # Append to primary storage
        self._nodes[node.id] = node

        # Update timeline (maintain sorted order by timestamp)
        # Simple append since we assume chronological order in practice
        self._timeline.append(node.id)

        # Update backlinks
        for link in node.links:
            if link.target not in self._backlinks:
                self._backlinks[link.target] = []
            self._backlinks[link.target].append((link.source, link.relation))

        # Update walk index
        if node.walk_id:
            if node.walk_id not in self._walk_index:
                self._walk_index[node.walk_id] = []
            self._walk_index[node.walk_id].append(node.id)

        logger.debug(f"Appended trace {node.id}: {node.origin} / {node.stimulus.kind}")

    def get(self, trace_id: MarkId) -> Mark | None:
        """Get a Mark by ID."""
        return self._nodes.get(trace_id)

    def get_or_raise(self, trace_id: MarkId) -> Mark:
        """Get a Mark by ID, raising if not found."""
        node = self.get(trace_id)
        if node is None:
            raise MarkNotFoundError(trace_id)
        return node

    def query(self, query: MarkQuery) -> Iterator[Mark]:
        """
        Query traces matching the given criteria.

        Returns an iterator over matching traces in timestamp order.
        """
        count = 0
        skipped = 0

        for trace_id in self._timeline:
            node = self._nodes[trace_id]

            if not query.matches(node, self):
                continue

            # Handle offset
            if skipped < query.offset:
                skipped += 1
                continue

            # Handle limit
            if query.limit and count >= query.limit:
                return

            yield node
            count += 1

    def count(self, query: MarkQuery | None = None) -> int:
        """Count traces matching the query (or all traces if no query)."""
        if query is None:
            return len(self._nodes)
        return sum(1 for _ in self.query(query))

    def all(self) -> Iterator[Mark]:
        """Iterate over all traces in timestamp order."""
        for trace_id in self._timeline:
            yield self._nodes[trace_id]

    def recent(self, limit: int = 10) -> list[Mark]:
        """Get the most recent traces."""
        return [self._nodes[tid] for tid in self._timeline[-limit:]]

    # =========================================================================
    # Causal Graph Navigation
    # =========================================================================

    def get_causes(self, trace_id: MarkId) -> list[Mark]:
        """Get all traces that caused this trace (incoming CAUSES links)."""
        backlinks = self._backlinks.get(trace_id, [])
        causes = []
        for source, relation in backlinks:
            if relation == LinkRelation.CAUSES:
                # Skip plan paths (they're not mark IDs)
                if isinstance(source, str) and not source.startswith("mark-"):
                    continue
                source_node = self.get(MarkId(str(source)))
                if source_node:
                    causes.append(source_node)
        return causes

    def get_effects(self, trace_id: MarkId) -> list[Mark]:
        """Get all traces caused by this trace (outgoing CAUSES links)."""
        effects = []
        for node in self.all():
            for link in node.links:
                if link.source == trace_id and link.relation == LinkRelation.CAUSES:
                    effects.append(node)
        return effects

    def get_continuation(self, trace_id: MarkId) -> list[Mark]:
        """Get traces that continue this trace (CONTINUES relation)."""
        continuations = []
        for node in self.all():
            for link in node.links:
                if link.source == trace_id and link.relation == LinkRelation.CONTINUES:
                    continuations.append(node)
        return continuations

    def get_branches(self, trace_id: MarkId) -> list[Mark]:
        """Get traces that branch from this trace (BRANCHES relation)."""
        branches = []
        for node in self.all():
            for link in node.links:
                if link.source == trace_id and link.relation == LinkRelation.BRANCHES:
                    branches.append(node)
        return branches

    def get_fulfillments(self, trace_id: MarkId) -> list[Mark]:
        """Get traces that fulfill intents in this trace (FULFILLS relation)."""
        fulfillments = []
        for node in self.all():
            for link in node.links:
                if link.source == trace_id and link.relation == LinkRelation.FULFILLS:
                    fulfillments.append(node)
        return fulfillments

    def get_walk_traces(self, walk_id: WalkId) -> list[Mark]:
        """Get all traces in a specific Walk."""
        trace_ids = self._walk_index.get(walk_id, [])
        return [self._nodes[tid] for tid in trace_ids]

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_link(self, node: Mark, link: MarkLink) -> None:
        """
        Validate a MarkLink for causality (Law 2).

        Raises:
            CausalityViolation: If target.timestamp <= source.timestamp
            MarkNotFoundError: If source trace doesn't exist (for trace links)
        """
        # Plan links don't need timestamp validation
        if isinstance(link.source, str) and (
            link.source.endswith(".md") or link.source.startswith("plans/")
        ):
            return

        # Get source trace
        source_id = MarkId(str(link.source))
        source_node = self.get(source_id)

        if source_node is None:
            raise MarkNotFoundError(source_id)

        # Law 2: target.timestamp > source.timestamp
        if node.timestamp <= source_node.timestamp:
            raise CausalityViolation(
                source_id=str(source_id),
                target_id=str(node.id),
                source_ts=source_node.timestamp,
                target_ts=node.timestamp,
            )

    # =========================================================================
    # Persistence
    # =========================================================================

    def save(self, path: Path | str) -> None:
        """Save the store to a JSON file."""
        path = Path(path)
        data = {
            "version": 1,
            "nodes": [node.to_dict() for node in self.all()],
        }
        path.write_text(json.dumps(data, indent=2, default=str))
        self._persistence_path = path
        logger.info(f"Saved {len(self._nodes)} traces to {path}")

    @classmethod
    def load(cls, path: Path | str) -> MarkStore:
        """Load a store from a JSON file."""
        path = Path(path)
        data = json.loads(path.read_text())

        store = cls()
        store._persistence_path = path

        for node_data in data.get("nodes", []):
            node = Mark.from_dict(node_data)
            # Skip validation on load (data was validated on append)
            store._nodes[node.id] = node
            store._timeline.append(node.id)

            for link in node.links:
                if link.target not in store._backlinks:
                    store._backlinks[link.target] = []
                store._backlinks[link.target].append((link.source, link.relation))

            if node.walk_id:
                if node.walk_id not in store._walk_index:
                    store._walk_index[node.walk_id] = []
                store._walk_index[node.walk_id].append(node.id)

        logger.info(f"Loaded {len(store._nodes)} traces from {path}")
        return store

    def sync(self) -> None:
        """Sync to persistence path if set."""
        if self._persistence_path:
            self.save(self._persistence_path)

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, Any]:
        """Get store statistics."""
        origin_counts: dict[str, int] = {}
        phase_counts: dict[str, int] = {}
        walk_counts: dict[str, int] = {}

        for node in self.all():
            origin_counts[node.origin] = origin_counts.get(node.origin, 0) + 1
            if node.phase:
                phase_counts[node.phase.value] = phase_counts.get(node.phase.value, 0) + 1
            if node.walk_id:
                walk_counts[str(node.walk_id)] = walk_counts.get(str(node.walk_id), 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_links": sum(len(node.links) for node in self.all()),
            "by_origin": origin_counts,
            "by_phase": phase_counts,
            "walks": len(self._walk_index),
            "walk_counts": walk_counts,
        }

    def __len__(self) -> int:
        """Return the number of traces in the store."""
        return len(self._nodes)

    def __contains__(self, trace_id: MarkId) -> bool:
        """Check if a trace ID exists in the store."""
        return trace_id in self._nodes


# =============================================================================
# Global Store Factory
# =============================================================================

_global_store: MarkStore | None = None


def get_mark_store() -> MarkStore:
    """Get the global trace store (singleton)."""
    global _global_store
    if _global_store is None:
        _global_store = MarkStore()
    return _global_store


def set_mark_store(store: MarkStore) -> None:
    """Set the global trace store (for testing)."""
    global _global_store
    _global_store = store


def reset_mark_store() -> None:
    """Reset the global trace store (for testing)."""
    global _global_store
    _global_store = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Exceptions
    "MarkStoreError",
    "CausalityViolation",
    "DuplicateMarkError",
    "MarkNotFoundError",
    # Query
    "MarkQuery",
    # Store
    "MarkStore",
    # Global factory
    "get_mark_store",
    "set_mark_store",
    "reset_mark_store",
]
