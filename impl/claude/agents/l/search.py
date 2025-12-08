"""
L-gent Search: Three-Brain Architecture

Combines three search strategies:
1. Keyword (BM25): Exact/fuzzy text matching
2. Semantic (Embeddings): Intent-based similarity
3. Graph (Traversal): Relationship-aware discovery

This file implements the basic keyword search. Semantic and graph search
will be added in future phases.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .catalog import CatalogEntry, Registry, EntityType, Status


class SearchStrategy(Enum):
    """Available search strategies."""
    KEYWORD = "keyword"       # Text matching (BM25-like)
    SEMANTIC = "semantic"     # Embedding similarity (future)
    GRAPH = "graph"           # Relationship traversal (future)
    FUSION = "fusion"         # Combined multi-strategy (future)


@dataclass
class SearchResult:
    """A single search result with relevance score."""
    entry: CatalogEntry
    score: float              # 0.0 to 1.0 (higher = more relevant)
    strategy: SearchStrategy  # Which search found this
    explanation: str          # Why this was returned


class Search:
    """Three-brain search system for L-gent catalog.

    Phase 1 (MVP): Keyword search only
    Phase 2: Add semantic search with embeddings
    Phase 3: Add graph traversal
    Phase 4: Fusion layer combining all strategies
    """

    def __init__(self, registry: Registry):
        """Initialize search with a registry."""
        self.registry = registry

    async def find(
        self,
        query: str,
        strategy: SearchStrategy = SearchStrategy.KEYWORD,
        limit: int = 10,
        filters: dict[str, any] | None = None
    ) -> list[SearchResult]:
        """Search the catalog.

        Args:
            query: Search query string
            strategy: Which search strategy to use
            limit: Maximum number of results
            filters: Optional filters (entity_type, status, author, etc.)

        Returns:
            List of SearchResults, sorted by relevance (descending)
        """
        if strategy == SearchStrategy.KEYWORD:
            return await self._keyword_search(query, limit, filters)
        elif strategy == SearchStrategy.SEMANTIC:
            raise NotImplementedError("Semantic search coming in Phase 2")
        elif strategy == SearchStrategy.GRAPH:
            raise NotImplementedError("Graph search coming in Phase 3")
        elif strategy == SearchStrategy.FUSION:
            raise NotImplementedError("Fusion search coming in Phase 4")
        else:
            raise ValueError(f"Unknown search strategy: {strategy}")

    async def _keyword_search(
        self,
        query: str,
        limit: int,
        filters: dict[str, any] | None = None
    ) -> list[SearchResult]:
        """Simple keyword-based search.

        Searches in:
        - name
        - description
        - keywords
        - contracts_implemented
        - contracts_required

        Scoring:
        - Exact match in name: +1.0
        - Partial match in name: +0.5
        - Match in keywords: +0.3
        - Match in description: +0.2
        - Match in contracts: +0.1
        """
        all_entries = await self.registry.list_all()

        # Apply filters
        if filters:
            all_entries = self._apply_filters(all_entries, filters)

        # Score each entry
        results: list[SearchResult] = []
        query_lower = query.lower()
        query_terms = query_lower.split()

        for entry in all_entries:
            score = 0.0
            explanations = []

            # Check name
            if query_lower == entry.name.lower():
                score += 1.0
                explanations.append(f"Exact name match: {entry.name}")
            elif query_lower in entry.name.lower():
                score += 0.5
                explanations.append(f"Partial name match: {entry.name}")

            # Check keywords
            entry_keywords_lower = [kw.lower() for kw in entry.keywords]
            for term in query_terms:
                if term in entry_keywords_lower:
                    score += 0.3
                    explanations.append(f"Keyword match: {term}")

            # Check description
            description_lower = entry.description.lower()
            for term in query_terms:
                if term in description_lower:
                    score += 0.2
                    explanations.append(f"Description contains: {term}")
                    break  # Only count once per entry

            # Check contracts
            all_contracts = entry.contracts_implemented + entry.contracts_required
            contracts_lower = [c.lower() for c in all_contracts]
            for term in query_terms:
                if any(term in contract for contract in contracts_lower):
                    score += 0.1
                    explanations.append(f"Contract match: {term}")
                    break  # Only count once per entry

            # Only include if score > 0
            if score > 0:
                results.append(SearchResult(
                    entry=entry,
                    score=score,
                    strategy=SearchStrategy.KEYWORD,
                    explanation="; ".join(explanations[:3])  # Top 3 reasons
                ))

        # Sort by score (descending) and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def _apply_filters(
        self,
        entries: list[CatalogEntry],
        filters: dict[str, any]
    ) -> list[CatalogEntry]:
        """Apply filters to entry list.

        Supported filters:
        - entity_type: EntityType
        - status: Status
        - author: str
        - min_success_rate: float
        """
        filtered = entries

        if "entity_type" in filters:
            entity_type = filters["entity_type"]
            if isinstance(entity_type, str):
                entity_type = EntityType(entity_type)
            filtered = [e for e in filtered if e.entity_type == entity_type]

        if "status" in filters:
            status = filters["status"]
            if isinstance(status, str):
                status = Status(status)
            filtered = [e for e in filtered if e.status == status]

        if "author" in filters:
            author = filters["author"]
            filtered = [e for e in filtered if e.author == author]

        if "min_success_rate" in filters:
            min_rate = filters["min_success_rate"]
            filtered = [e for e in filtered if e.success_rate >= min_rate]

        return filtered

    async def find_by_type_signature(
        self,
        input_type: str | None = None,
        output_type: str | None = None,
        limit: int = 10
    ) -> list[SearchResult]:
        """Find agents by type signature.

        This is a specialized search for composition planning.

        Args:
            input_type: Required input type (or None for any)
            output_type: Required output type (or None for any)
            limit: Maximum results

        Returns:
            Agents matching the type signature
        """
        all_entries = await self.registry.list_by_type(EntityType.AGENT)

        results: list[SearchResult] = []

        for entry in all_entries:
            matches = True
            score = 1.0

            if input_type and entry.input_type != input_type:
                matches = False

            if output_type and entry.output_type != output_type:
                matches = False

            if matches:
                explanation = f"Type signature: {entry.input_type} → {entry.output_type}"

                # Boost score for high success rate
                score *= entry.success_rate

                results.append(SearchResult(
                    entry=entry,
                    score=score,
                    strategy=SearchStrategy.KEYWORD,  # For now
                    explanation=explanation
                ))

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def find_similar(
        self,
        entry_id: str,
        limit: int = 5
    ) -> list[SearchResult]:
        """Find entries similar to a given entry.

        Phase 1 (MVP): Uses keyword overlap
        Phase 2: Will use semantic similarity

        Args:
            entry_id: ID of entry to find similar to
            limit: Maximum results

        Returns:
            Similar entries
        """
        entry = await self.registry.get(entry_id)
        if not entry:
            raise ValueError(f"Entry {entry_id} not found")

        # Build query from keywords and name
        query = " ".join(entry.keywords + [entry.name])

        # Search and exclude the original entry
        results = await self._keyword_search(query, limit + 1, None)
        return [r for r in results if r.entry.id != entry_id][:limit]
