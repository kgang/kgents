"""
L-gent Registry Implementation

Layer 1: What exists in the ecosystem?

The Registry is a simplified in-memory catalog for Phase 1.
Future phases will add:
- Persistent storage (D-gent integration)
- Semantic search (embeddings + vector DB)
- Graph traversal (lineage + lattice)
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .types import (
    Catalog,
    CatalogEntry,
    EntityType,
    SearchResult,
    Status,
)


class Registry:
    """
    Layer 1: Registry - What exists in the ecosystem?

    Simplified implementation for Phase 1 G-gent integration.
    Provides in-memory storage and basic search functionality.
    """

    def __init__(self, catalog: Catalog | None = None):
        """Initialize registry with optional existing catalog."""
        self.catalog = catalog or Catalog()

    async def register(self, entry: CatalogEntry) -> str:
        """
        Add or update an artifact in the registry.

        Steps:
        1. Validate entry (required fields)
        2. Update timestamp
        3. Store in catalog
        4. Return entry ID

        Idempotent: Re-registering same ID updates existing entry.
        """
        # Validate required fields
        if not entry.id:
            raise ValueError("CatalogEntry.id is required")
        if not entry.name:
            raise ValueError("CatalogEntry.name is required")
        if not entry.description:
            raise ValueError("CatalogEntry.description is required")

        # Update timestamp
        entry_updated = replace(entry, updated_at=datetime.now())

        # Store
        self.catalog.entries[entry.id] = entry_updated
        self.catalog.last_updated = datetime.now()

        return entry.id

    async def get(self, id: str) -> CatalogEntry | None:
        """Retrieve entry by ID. O(1) lookup."""
        return self.catalog.entries.get(id)

    async def exists(self, id: str) -> bool:
        """Check existence without retrieving."""
        return id in self.catalog.entries

    async def list(
        self,
        entity_type: EntityType | None = None,
        status: Status | None = None,
        author: str | None = None,
        limit: int | None = None,
    ) -> list[CatalogEntry]:
        """
        List entries with optional filters.

        Args:
            entity_type: Filter by entity type
            status: Filter by status
            author: Filter by author
            limit: Maximum number of results

        Returns:
            List of matching entries, sorted by updated_at descending
        """
        entries = list(self.catalog.entries.values())

        # Apply filters
        if entity_type is not None:
            entries = [e for e in entries if e.entity_type == entity_type]
        if status is not None:
            entries = [e for e in entries if e.status == status]
        if author is not None:
            entries = [e for e in entries if e.author == author]

        # Sort by updated_at descending (most recent first)
        entries.sort(key=lambda e: e.updated_at, reverse=True)

        # Apply limit
        if limit is not None:
            entries = entries[:limit]

        return entries

    async def find(
        self,
        query: str | None = None,
        entity_type: EntityType | None = None,
        keywords: list[str] | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search for entries.

        Phase 1 Implementation:
        - Keyword matching on description and keywords
        - No semantic search (embeddings) yet
        - No graph traversal yet

        Args:
            query: Free-text search query
            entity_type: Filter by entity type
            keywords: Filter by exact keyword matches
            limit: Maximum number of results

        Returns:
            List of SearchResult with relevance scores
        """
        results: list[SearchResult] = []

        for entry in self.catalog.entries.values():
            # Apply entity_type filter
            if entity_type is not None and entry.entity_type != entity_type:
                continue

            # Calculate relevance score
            score = 0.0
            match_type = "none"
            explanation = ""

            # Exact keyword matching
            if keywords:
                matched_keywords = [
                    kw
                    for kw in keywords
                    if kw.lower() in [k.lower() for k in entry.keywords]
                ]
                if matched_keywords:
                    score += len(matched_keywords) / len(keywords) * 0.5
                    match_type = "keyword"
                    explanation = f"Matched keywords: {', '.join(matched_keywords)}"

            # Text query matching (simple substring search)
            if query:
                query_lower = query.lower()
                if query_lower in entry.name.lower():
                    score += 0.3
                    match_type = "exact" if score == 0.3 else "hybrid"
                    explanation += f" | Name match: '{query}'"
                if query_lower in entry.description.lower():
                    score += 0.2
                    match_type = "exact" if match_type == "none" else "hybrid"
                    explanation += f" | Description match: '{query}'"

                # Check tongue-specific fields for TONGUE entities
                if entry.entity_type == EntityType.TONGUE:
                    if (
                        entry.tongue_domain
                        and query_lower in entry.tongue_domain.lower()
                    ):
                        score += 0.3
                        match_type = "hybrid"
                        explanation += f" | Domain match: '{query}'"

            # If only entity_type filter was provided (no query/keywords), give default score
            if (
                score == 0.0
                and entity_type is not None
                and query is None
                and not keywords
            ):
                score = 1.0
                match_type = "exact"
                explanation = f"Entity type: {entity_type.value}"

            # Skip entries with zero score
            if score > 0:
                results.append(
                    SearchResult(
                        entry=entry,
                        score=min(score, 1.0),  # Cap at 1.0
                        match_type=match_type,
                        explanation=explanation.strip(" |"),
                    )
                )

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        # Apply limit
        return results[:limit]

    async def delete(self, id: str) -> bool:
        """
        Remove entry from registry.

        Returns:
            True if deleted, False if not found
        """
        if id in self.catalog.entries:
            del self.catalog.entries[id]
            self.catalog.last_updated = datetime.now()
            return True
        return False

    async def update_usage(
        self, id: str, success: bool = True, error: str | None = None
    ) -> None:
        """
        Update usage metrics for an entry.

        Args:
            id: Entry ID to update
            success: Whether the invocation was successful
            error: Optional error message if failed
        """
        entry = self.catalog.entries.get(id)
        if not entry:
            return

        # Update usage count
        entry.usage_count += 1
        entry.last_used = datetime.now()

        # Update success rate
        total_invocations = entry.usage_count
        if success:
            # Incrementally update success rate
            entry.success_rate = (
                entry.success_rate * (total_invocations - 1) + 1.0
            ) / total_invocations
        else:
            # Record failure
            entry.success_rate = (
                entry.success_rate * (total_invocations - 1) + 0.0
            ) / total_invocations
            entry.last_error = error

        entry.updated_at = datetime.now()
        self.catalog.last_updated = datetime.now()

    async def deprecate(
        self,
        id: str,
        reason: str,
        successor_id: str | None = None,
    ) -> bool:
        """
        Mark an entry as deprecated.

        Args:
            id: Entry to deprecate
            reason: Why it's deprecated
            successor_id: Optional ID of replacement

        Returns:
            True if deprecated, False if not found
        """
        entry = self.catalog.entries.get(id)
        if not entry:
            return False

        entry.status = Status.DEPRECATED
        entry.deprecation_reason = reason
        entry.deprecated_in_favor_of = successor_id
        entry.updated_at = datetime.now()
        self.catalog.last_updated = datetime.now()

        # Add successor relationship if provided
        if successor_id:
            if "successor_to" not in entry.relationships:
                entry.relationships["successor_to"] = []
            entry.relationships["successor_to"].append(successor_id)

        return True

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
    ) -> bool:
        """
        Add a relationship between two entries.

        Args:
            source_id: Source entry ID
            target_id: Target entry ID
            relationship_type: Type of relationship (e.g., "depends_on", "forked_from")

        Returns:
            True if added, False if source not found
        """
        source = self.catalog.entries.get(source_id)
        if not source:
            return False

        if relationship_type not in source.relationships:
            source.relationships[relationship_type] = []

        # Avoid duplicates
        if target_id not in source.relationships[relationship_type]:
            source.relationships[relationship_type].append(target_id)
            source.updated_at = datetime.now()
            self.catalog.last_updated = datetime.now()

        return True

    async def find_related(
        self,
        id: str,
        relationship_type: str,
    ) -> list[CatalogEntry]:
        """
        Find entries related to a given entry.

        Args:
            id: Source entry ID
            relationship_type: Type of relationship to traverse

        Returns:
            List of related entries
        """
        source = self.catalog.entries.get(id)
        if not source:
            return []

        related_ids = source.relationships.get(relationship_type, [])
        return [
            e
            for e in [self.catalog.entries.get(rid) for rid in related_ids]
            if e is not None
        ]

    def to_dict(self) -> dict:
        """Export catalog as dictionary."""
        return self.catalog.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "Registry":
        """Import catalog from dictionary."""
        catalog = Catalog.from_dict(data)
        return cls(catalog=catalog)
