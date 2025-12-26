"""
Feed Defaults: The five canonical feeds.

These feeds demonstrate the power of the Feed primitive:
1. cosmos: Everything, chronological (the raw truth stream)
2. coherent: Lowest loss first (your most solid beliefs)
3. contradictions: Has contradiction edges (synthesis opportunities)
4. axioms: L1-L2 only (the bedrock you stand on)
5. handwavy: L3 with loss > 0.5 (goals waiting to cohere)

Philosophy:
    "A feed without filters is the raw cosmos.
     A feed with filters is a perspective.
     Multiple feeds = multiple selves."
"""

from __future__ import annotations

from services.feed.core import Feed, FeedFilter, FeedRanking, FeedSource


# =============================================================================
# Default Feeds
# =============================================================================


COSMOS_FEED = Feed(
    id="cosmos",
    name="The Cosmos",
    description="Everything, in order of creation. The raw truth stream.",
    sources=(FeedSource(type="all"),),
    filters=(),
    ranking=FeedRanking(
        recency_weight=1.0,
        attention_weight=0.0,
        principles_weight=0.0,
        coherence_weight=0.0,
    ),
)


COHERENT_FEED = Feed(
    id="coherent",
    name="Most Coherent",
    description="Lowest loss first — your most solid beliefs.",
    sources=(FeedSource(type="all"),),
    filters=(),
    ranking=FeedRanking(
        coherence_weight=1.0,  # Primary: low loss = high rank
        recency_weight=0.1,  # Secondary: slight recency bias
        attention_weight=0.0,
        principles_weight=0.0,
    ),
)


CONTRADICTIONS_FEED = Feed(
    id="contradictions",
    name="Contradictions",
    description="Where your beliefs conflict — opportunity for synthesis.",
    sources=(FeedSource(type="all"),),
    filters=(
        # Custom filter: has contradiction edges
        FeedFilter(
            field="custom",
            operator="eq",
            value=lambda kb: _has_contradiction_edge(kb),
        ),
    ),
    ranking=FeedRanking(
        coherence_weight=-1.0,  # Inverted: highest loss first
        recency_weight=0.1,
        attention_weight=0.0,
        principles_weight=0.0,
    ),
)


AXIOMS_FEED = Feed(
    id="axioms",
    name="Your Axioms",
    description="L1-L2 — the bedrock you stand on.",
    sources=(
        FeedSource(type="layer", value=(1, 2)),  # Assumptions and Values
    ),
    filters=(),
    ranking=FeedRanking(
        coherence_weight=1.0,  # Most coherent axioms first
        recency_weight=0.0,  # Time doesn't matter for axioms
        attention_weight=0.0,
        principles_weight=0.0,
    ),
)


HANDWAVY_FEED = Feed(
    id="handwavy",
    name="Hand-Wavy Goals",
    description="High loss declarations waiting to cohere. Dreams need structure.",
    sources=(
        FeedSource(type="layer", value=3),  # Layer 3: Goals
    ),
    filters=(
        FeedFilter(
            field="loss",
            operator="gt",
            value=0.5,  # High loss threshold
        ),
    ),
    ranking=FeedRanking(
        recency_weight=1.0,  # Most recent first
        coherence_weight=0.0,  # Don't rank by coherence (all are incoherent)
        attention_weight=0.0,
        principles_weight=0.0,
    ),
)


# Tuple of all default feeds
DEFAULT_FEEDS = (
    COSMOS_FEED,
    COHERENT_FEED,
    CONTRADICTIONS_FEED,
    AXIOMS_FEED,
    HANDWAVY_FEED,
)


# =============================================================================
# Helper Functions
# =============================================================================


def _has_contradiction_edge(kblock) -> bool:
    """
    Check if K-Block has a contradiction edge.

    NOTE: This is a placeholder. The actual implementation depends on
    how K-Blocks store edge information. This should be updated when
    K-Block's edge storage is finalized.
    """
    # Check if kblock has edges attribute
    if not hasattr(kblock, "edges"):
        return False

    # Check if any edge is a contradiction
    from services.zero_seed import EdgeKind

    for edge in kblock.edges:
        if edge.kind == EdgeKind.CONTRADICTS:
            return True

    return False


def get_default_feed(feed_id: str) -> Feed | None:
    """
    Get a default feed by ID.

    Args:
        feed_id: One of 'cosmos', 'coherent', 'contradictions', 'axioms', 'handwavy'

    Returns:
        Feed if found, None otherwise
    """
    for feed in DEFAULT_FEEDS:
        if feed.id == feed_id:
            return feed
    return None


__all__ = [
    "COSMOS_FEED",
    "COHERENT_FEED",
    "CONTRADICTIONS_FEED",
    "AXIOMS_FEED",
    "HANDWAVY_FEED",
    "DEFAULT_FEEDS",
    "get_default_feed",
]
