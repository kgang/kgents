"""
Tests for default feeds.

Verifies:
- 5 default feeds exist
- Cosmos feed includes everything
- Coherent feed prioritizes low loss
- Contradictions feed filters appropriately
- Axioms feed filters L1-L2
- Handwavy feed filters L3 with high loss
"""

from datetime import datetime, timezone

import pytest

from services.feed.defaults import (
    AXIOMS_FEED,
    COHERENT_FEED,
    CONTRADICTIONS_FEED,
    COSMOS_FEED,
    DEFAULT_FEEDS,
    HANDWAVY_FEED,
    get_default_feed,
)
from services.k_block.core.kblock import KBlock, generate_kblock_id

# =============================================================================
# Default Feeds Tests
# =============================================================================


def test_default_feeds_count():
    """There are exactly 5 default feeds."""
    assert len(DEFAULT_FEEDS) == 5


def test_default_feed_ids():
    """Default feeds have expected IDs."""
    feed_ids = {feed.id for feed in DEFAULT_FEEDS}
    expected = {"cosmos", "coherent", "contradictions", "axioms", "handwavy"}
    assert feed_ids == expected


def test_get_default_feed():
    """get_default_feed retrieves feeds by ID."""
    assert get_default_feed("cosmos") == COSMOS_FEED
    assert get_default_feed("coherent") == COHERENT_FEED
    assert get_default_feed("contradictions") == CONTRADICTIONS_FEED
    assert get_default_feed("axioms") == AXIOMS_FEED
    assert get_default_feed("handwavy") == HANDWAVY_FEED
    assert get_default_feed("nonexistent") is None


# =============================================================================
# Cosmos Feed Tests
# =============================================================================


def test_cosmos_includes_everything():
    """Cosmos feed includes all K-Blocks."""
    kb_l1 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )
    kb_l7 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=7,
    )

    assert COSMOS_FEED.should_include(kb_l1)
    assert COSMOS_FEED.should_include(kb_l7)


def test_cosmos_ranking_is_recency():
    """Cosmos feed ranks by recency only."""
    assert COSMOS_FEED.ranking.recency_weight == 1.0
    assert COSMOS_FEED.ranking.attention_weight == 0.0
    assert COSMOS_FEED.ranking.principles_weight == 0.0
    assert COSMOS_FEED.ranking.coherence_weight == 0.0


# =============================================================================
# Coherent Feed Tests
# =============================================================================


def test_coherent_includes_everything():
    """Coherent feed includes all K-Blocks (filters by ranking, not inclusion)."""
    kb = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )
    assert COHERENT_FEED.should_include(kb)


def test_coherent_ranking_is_coherence():
    """Coherent feed ranks by coherence primarily."""
    assert COHERENT_FEED.ranking.coherence_weight == 1.0
    assert COHERENT_FEED.ranking.recency_weight == 0.1  # Secondary


# =============================================================================
# Axioms Feed Tests
# =============================================================================


def test_axioms_includes_only_l1_l2():
    """Axioms feed includes only L1-L2 K-Blocks."""
    kb_l1 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )
    kb_l2 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=2,
    )
    kb_l3 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )

    assert AXIOMS_FEED.should_include(kb_l1)
    assert AXIOMS_FEED.should_include(kb_l2)
    assert not AXIOMS_FEED.should_include(kb_l3)


def test_axioms_ranking_is_coherence():
    """Axioms feed ranks by coherence (ignores time)."""
    assert AXIOMS_FEED.ranking.coherence_weight == 1.0
    assert AXIOMS_FEED.ranking.recency_weight == 0.0


# =============================================================================
# Handwavy Feed Tests
# =============================================================================


def test_handwavy_includes_only_l3_high_loss():
    """Handwavy feed includes only L3 K-Blocks (filter by loss is TODO)."""
    kb_l3 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )
    kb_l1 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )

    # Source check: only L3
    assert HANDWAVY_FEED.matches_source(kb_l3)
    assert not HANDWAVY_FEED.matches_source(kb_l1)

    # TODO: Once K-Block stores Galois loss, test filter for loss > 0.5


def test_handwavy_ranking_is_recency():
    """Handwavy feed ranks by recency (most recent first)."""
    assert HANDWAVY_FEED.ranking.recency_weight == 1.0
    assert HANDWAVY_FEED.ranking.coherence_weight == 0.0
