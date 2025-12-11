"""
L-gent Fusion: Three-Brain Hybrid Search combining keyword + semantic + graph.

This module implements the fusion layer that combines results from all three
search strategies (keyword, semantic, graph) into a unified query interface.

Phase 7 Implementation:
- QueryFusion: Unified search across all three brains
- Query type classification (exact name, semantic intent, type query, relationship)
- Weighted result combination using reciprocal rank fusion
- Serendipity suggestions (unexpected but useful connections)

Design Philosophy:
- Adaptive weighting: Different queries need different brain emphasis
- Parallelized search: All three brains run concurrently
- Explain everything: Results include interpretation and reasoning
- Joy-inducing: Surface serendipitous discoveries
"""

import asyncio
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .graph_search import GraphBrain, GraphResult
from .search import Search
from .search import SearchResult as KeywordResult
from .semantic import SemanticBrain, SemanticResult
from .types import CatalogEntry


class QueryType(Enum):
    """Classification of query intent."""

    EXACT_NAME = "exact_name"  # "NewsParser_v2"
    SEMANTIC_INTENT = "semantic_intent"  # "summarize financial documents"
    TYPE_QUERY = "type_query"  # "RawHTML -> Summary"
    RELATIONSHIP = "relationship"  # "depends on X", "compatible with Y"


@dataclass
class FusedResult:
    """Unified result from fusion search."""

    id: str
    entry: CatalogEntry
    score: float  # Final fused score (0.0 to 1.0)
    sources: dict[str, float]  # Which brains found this + their scores
    explanation: str  # Why this was returned
    rank: int  # Position in final results (1-indexed)


@dataclass
class QueryResponse:
    """Complete response to a query."""

    results: list[FusedResult]
    serendipity: list[FusedResult]  # Unexpected but potentially useful
    query_interpretation: str  # How the query was understood
    query_type: QueryType
    total_found: int  # Total before limit


class QueryFusion:
    """Unified search combining keyword, semantic, and graph strategies.

    This is the top-level search interface for L-gent. It:
    1. Classifies the query to determine appropriate brain weighting
    2. Runs all three searches in parallel
    3. Fuses results using reciprocal rank fusion
    4. Generates serendipity suggestions
    5. Explains the interpretation and results

    Example:
        fusion = QueryFusion(keyword_brain, semantic_brain, graph_brain)
        response = await fusion.search("process PDF documents")
        # Returns: agents that process PDFs, plus serendipitous suggestions
    """

    def __init__(
        self,
        keyword_brain: Search,
        semantic_brain: SemanticBrain,
        graph_brain: GraphBrain,
    ):
        """Initialize query fusion.

        Args:
            keyword_brain: Keyword search (Brain 1)
            semantic_brain: Semantic search (Brain 2)
            graph_brain: Graph search (Brain 3)
        """
        self.keyword = keyword_brain
        self.semantic = semantic_brain
        self.graph = graph_brain

    async def search(
        self, query: str, constraints: Optional[dict[str, Any]] = None, limit: int = 10
    ) -> QueryResponse:
        """Unified search across all three brains.

        Args:
            query: Search query (can be keywords, intent, or relationship)
            constraints: Optional filters (entity_type, status, etc.)
            limit: Maximum number of results

        Returns:
            QueryResponse with fused results and serendipity
        """
        # Classify query type
        query_type = self._classify_query(query)

        # Get appropriate weights
        weights = self._get_weights(query_type)

        # Run all three searches in parallel
        keyword_task = self._safe_keyword_search(query, constraints, limit * 2)
        semantic_task = self._safe_semantic_search(query, constraints, limit * 2)
        graph_task = self._safe_graph_search(query, query_type, limit * 2)

        keyword_results, semantic_results, graph_results = await asyncio.gather(
            keyword_task, semantic_task, graph_task
        )

        # Fuse results
        fused = self._reciprocal_rank_fusion(
            keyword_results, semantic_results, graph_results, weights
        )

        # Generate serendipity
        serendipity = self._generate_serendipity(
            query, fused, keyword_results, semantic_results, graph_results
        )

        # Explain interpretation
        interpretation = self._explain_interpretation(query, query_type)

        return QueryResponse(
            results=fused[:limit],
            serendipity=serendipity,
            query_interpretation=interpretation,
            query_type=query_type,
            total_found=len(fused),
        )

    # Query classification

    def _classify_query(self, query: str) -> QueryType:
        """Determine which brain should be weighted highest.

        Args:
            query: User query string

        Returns:
            QueryType classification
        """
        # Exact name pattern (e.g., "NewsParser", "Summarizer_v2")
        if re.match(r"^[A-Z][a-zA-Z]*(_v?\d+)?$", query):
            return QueryType.EXACT_NAME

        # Type signature pattern (e.g., "RawHTML -> Summary", "input:JSON")
        if "->" in query or "input:" in query or "output:" in query:
            return QueryType.TYPE_QUERY

        # Relationship pattern (e.g., "depends on", "compatible with", "implements")
        relationship_keywords = [
            "depends",
            "compatible",
            "implements",
            "successor",
            "ancestor",
        ]
        if any(kw in query.lower() for kw in relationship_keywords):
            return QueryType.RELATIONSHIP

        # Default to semantic intent
        return QueryType.SEMANTIC_INTENT

    def _get_weights(self, query_type: QueryType) -> tuple[float, float, float]:
        """Get (keyword, semantic, graph) weights for query type.

        Args:
            query_type: Classified query type

        Returns:
            Tuple of weights (keyword, semantic, graph) summing to 1.0
        """
        weights_map = {
            QueryType.EXACT_NAME: (0.8, 0.1, 0.1),  # Keyword dominates
            QueryType.SEMANTIC_INTENT: (0.2, 0.7, 0.1),  # Semantic dominates
            QueryType.TYPE_QUERY: (0.1, 0.2, 0.7),  # Graph dominates
            QueryType.RELATIONSHIP: (0.1, 0.1, 0.8),  # Graph dominates
        }
        return weights_map[query_type]

    # Safe search wrappers (handle empty results gracefully)

    async def _safe_keyword_search(
        self, query: str, constraints: Optional[dict[str, Any]], limit: int
    ) -> list[KeywordResult]:
        """Keyword search with error handling."""
        try:
            return await self.keyword.find(query, filters=constraints, limit=limit)
        except Exception:
            return []

    async def _safe_semantic_search(
        self, query: str, constraints: Optional[dict[str, Any]], limit: int
    ) -> list[SemanticResult]:
        """Semantic search with error handling."""
        try:
            return await self.semantic.search(query, filters=constraints, limit=limit)
        except Exception:
            return []

    async def _safe_graph_search(
        self, query: str, query_type: QueryType, limit: int
    ) -> list[GraphResult]:
        """Graph search with error handling.

        For non-relationship queries, graph search returns empty.
        """
        if query_type != QueryType.RELATIONSHIP:
            return []

        try:
            # Extract artifact ID from query if possible
            # For now, return empty - full implementation would parse relationship queries
            return []
        except Exception:
            return []

    # Result fusion

    def _reciprocal_rank_fusion(
        self,
        keyword_results: list[KeywordResult],
        semantic_results: list[SemanticResult],
        graph_results: list[GraphResult],
        weights: tuple[float, float, float],
    ) -> list[FusedResult]:
        """Combine results using reciprocal rank fusion.

        RRF formula: score = Σ(weight / (k + rank))
        where k=60 is a constant smoothing parameter.

        Args:
            keyword_results: Results from Brain 1
            semantic_results: Results from Brain 2
            graph_results: Results from Brain 3
            weights: Weighting (keyword, semantic, graph)

        Returns:
            Fused and ranked results
        """
        k = 60  # RRF smoothing constant
        keyword_weight, semantic_weight, graph_weight = weights

        # Build score accumulator
        scores: dict[str, dict[str, Any]] = {}

        # Add keyword scores
        for rank, result in enumerate(keyword_results, start=1):
            entry_id = result.entry.id
            if entry_id not in scores:
                scores[entry_id] = {
                    "entry": result.entry,
                    "score": 0.0,
                    "sources": {},
                    "explanations": [],
                }
            rrf_score = keyword_weight / (k + rank)
            scores[entry_id]["score"] += rrf_score
            scores[entry_id]["sources"]["keyword"] = result.score
            scores[entry_id]["explanations"].append(f"Keyword: {result.explanation}")

        # Add semantic scores
        for rank, sem_result in enumerate(semantic_results, start=1):
            entry_id = sem_result.id
            if entry_id not in scores:
                scores[entry_id] = {
                    "entry": sem_result.entry,
                    "score": 0.0,
                    "sources": {},
                    "explanations": [],
                }
            rrf_score = semantic_weight / (k + rank)
            scores[entry_id]["score"] += rrf_score
            scores[entry_id]["sources"]["semantic"] = sem_result.similarity
            scores[entry_id]["explanations"].append(
                f"Semantic: {sem_result.explanation}"
            )

        # Add graph scores
        for rank, graph_result in enumerate(graph_results, start=1):
            entry_id = graph_result.id
            if entry_id not in scores:
                scores[entry_id] = {
                    "entry": graph_result.entry,
                    "score": 0.0,
                    "sources": {},
                    "explanations": [],
                }
            rrf_score = graph_weight / (k + rank)
            scores[entry_id]["score"] += rrf_score
            scores[entry_id]["sources"]["graph"] = 1.0 / graph_result.path_length
            scores[entry_id]["explanations"].append(
                f"Graph: {graph_result.explanation}"
            )

        # Convert to FusedResult and sort
        fused: list[FusedResult] = []
        for entry_id, data in scores.items():
            explanation = "; ".join(data["explanations"][:2])  # Top 2 reasons
            fused.append(
                FusedResult(
                    id=entry_id,
                    entry=data["entry"],
                    score=data["score"],
                    sources=data["sources"],
                    explanation=explanation,
                    rank=0,  # Will be set below
                )
            )

        # Sort by score (descending)
        fused.sort(key=lambda r: r.score, reverse=True)

        # Assign ranks
        for rank, fused_result in enumerate(fused, start=1):
            fused_result.rank = rank

        return fused

    # Serendipity generation

    def _generate_serendipity(
        self,
        query: str,
        fused: list[FusedResult],
        keyword_results: list[KeywordResult],
        semantic_results: list[SemanticResult],
        graph_results: list[GraphResult],
    ) -> list[FusedResult]:
        """Generate serendipitous suggestions (unexpected but useful).

        Serendipity criteria:
        - Found by only one brain (not consensus)
        - Not in top results (rank > 5)
        - Has high score from the brain that found it

        Args:
            query: Original query
            fused: Fused results
            keyword_results: Keyword brain results
            semantic_results: Semantic brain results
            graph_results: Graph brain results

        Returns:
            List of serendipitous results (max 3)
        """
        serendipity: list[FusedResult] = []

        # Look for results found by only semantic brain (unexpected connections)
        for result in fused:
            if result.rank > 5:  # Not in top results
                sources_count = len(result.sources)
                if sources_count == 1 and "semantic" in result.sources:
                    if result.sources["semantic"] > 0.6:  # High semantic similarity
                        serendipity.append(result)

        return serendipity[:3]

    def _explain_interpretation(self, query: str, query_type: QueryType) -> str:
        """Explain how the query was interpreted.

        Args:
            query: Original query
            query_type: Classified query type

        Returns:
            Human-readable interpretation
        """
        explanations = {
            QueryType.EXACT_NAME: f"Looking for artifact with exact name '{query}'",
            QueryType.SEMANTIC_INTENT: f"Finding artifacts that semantically match '{query}'",
            QueryType.TYPE_QUERY: f"Searching for type signature: {query}",
            QueryType.RELATIONSHIP: f"Finding artifacts with relationship: {query}",
        }
        return explanations[query_type]


# Convenience function


async def create_query_fusion(
    keyword_brain: Search, semantic_brain: SemanticBrain, graph_brain: GraphBrain
) -> QueryFusion:
    """Create a query fusion instance.

    Args:
        keyword_brain: Keyword search
        semantic_brain: Semantic search
        graph_brain: Graph search

    Returns:
        QueryFusion instance
    """
    return QueryFusion(keyword_brain, semantic_brain, graph_brain)
