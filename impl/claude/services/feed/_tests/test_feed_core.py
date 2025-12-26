"""
Tests for Feed core primitives.

Verifies:
- Feed, FeedSource, FeedFilter, FeedRanking
- Source matching logic
- Filter matching logic
- Feed inclusion logic
"""

from datetime import datetime, timezone

import pytest

from services.feed.core import Feed, FeedFilter, FeedRanking, FeedSource
from services.k_block.core.kblock import KBlock, generate_kblock_id


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_kblock():
    """Create a sample K-Block for testing."""
    return KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Test Content",
        base_content="# Test Content",
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        zero_seed_layer=3,  # Layer 3: Goals
        toulmin_proof={
            "claim": "Test claim",
            "warrant": "Test warrant",
            "principles": ["tasteful", "composable"],
        },
    )


# =============================================================================
# FeedSource Tests
# =============================================================================


def test_feed_source_all_matches_everything(sample_kblock):
    """FeedSource with type='all' matches all K-Blocks."""
    source = FeedSource(type="all")
    assert source.matches(sample_kblock)


def test_feed_source_layer_matches_single_layer(sample_kblock):
    """FeedSource with type='layer' matches K-Blocks by layer."""
    source = FeedSource(type="layer", value=3)
    assert source.matches(sample_kblock)

    source_wrong = FeedSource(type="layer", value=2)
    assert not source_wrong.matches(sample_kblock)


def test_feed_source_layer_matches_tuple_layers(sample_kblock):
    """FeedSource with type='layer' and tuple value matches multiple layers."""
    source = FeedSource(type="layer", value=(1, 2, 3))
    assert source.matches(sample_kblock)

    source_wrong = FeedSource(type="layer", value=(1, 2))
    assert not source_wrong.matches(sample_kblock)


def test_feed_source_custom_predicate(sample_kblock):
    """FeedSource with type='custom' uses predicate function."""
    source = FeedSource(type="custom", value=lambda kb: kb.zero_seed_layer == 3)
    assert source.matches(sample_kblock)

    source_wrong = FeedSource(type="custom", value=lambda kb: kb.zero_seed_layer == 1)
    assert not source_wrong.matches(sample_kblock)


# =============================================================================
# FeedFilter Tests
# =============================================================================


def test_feed_filter_layer_eq(sample_kblock):
    """FeedFilter with field='layer' and operator='eq' filters by layer."""
    filter_pass = FeedFilter(field="layer", operator="eq", value=3)
    assert filter_pass.matches(sample_kblock)

    filter_fail = FeedFilter(field="layer", operator="eq", value=2)
    assert not filter_fail.matches(sample_kblock)


def test_feed_filter_layer_lt_gt(sample_kblock):
    """FeedFilter with field='layer' supports lt/gt operators."""
    filter_lt = FeedFilter(field="layer", operator="lt", value=4)
    assert filter_lt.matches(sample_kblock)

    filter_gt = FeedFilter(field="layer", operator="gt", value=2)
    assert filter_gt.matches(sample_kblock)

    filter_gt_fail = FeedFilter(field="layer", operator="gt", value=3)
    assert not filter_gt_fail.matches(sample_kblock)


def test_feed_filter_layer_between(sample_kblock):
    """FeedFilter with field='layer' supports between operator."""
    filter_pass = FeedFilter(field="layer", operator="between", value=(2, 4))
    assert filter_pass.matches(sample_kblock)

    filter_fail = FeedFilter(field="layer", operator="between", value=(1, 2))
    assert not filter_fail.matches(sample_kblock)


def test_feed_filter_time_comparison(sample_kblock):
    """FeedFilter with field='time' filters by creation time."""
    filter_lt = FeedFilter(
        field="time",
        operator="lt",
        value=datetime(2025, 2, 1, tzinfo=timezone.utc),
    )
    assert filter_lt.matches(sample_kblock)

    filter_gt = FeedFilter(
        field="time",
        operator="gt",
        value=datetime(2024, 12, 1, tzinfo=timezone.utc),
    )
    assert filter_gt.matches(sample_kblock)


def test_feed_filter_principle_contains(sample_kblock):
    """FeedFilter with field='principle' checks proof principles."""
    filter_pass = FeedFilter(field="principle", operator="contains", value="tasteful")
    assert filter_pass.matches(sample_kblock)

    filter_fail = FeedFilter(field="principle", operator="contains", value="ethical")
    assert not filter_fail.matches(sample_kblock)


def test_feed_filter_custom_predicate(sample_kblock):
    """FeedFilter with field='custom' uses predicate function."""
    filter_pass = FeedFilter(
        field="custom",
        operator="eq",
        value=lambda kb: kb.zero_seed_layer == 3,
    )
    assert filter_pass.matches(sample_kblock)


# =============================================================================
# Feed Tests
# =============================================================================


def test_feed_matches_source():
    """Feed.matches_source checks if K-Block passes source criteria."""
    feed = Feed(
        id="test",
        name="Test Feed",
        sources=(FeedSource(type="layer", value=3),),
    )

    kb_pass = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )
    assert feed.matches_source(kb_pass)

    kb_fail = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )
    assert not feed.matches_source(kb_fail)


def test_feed_passes_filters():
    """Feed.passes_filters checks if K-Block passes all filters."""
    feed = Feed(
        id="test",
        name="Test Feed",
        filters=(
            FeedFilter(field="layer", operator="gt", value=2),
            FeedFilter(field="layer", operator="lt", value=5),
        ),
    )

    kb_pass = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )
    assert feed.passes_filters(kb_pass)

    kb_fail = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )
    assert not feed.passes_filters(kb_fail)


def test_feed_should_include():
    """Feed.should_include combines source and filter checks."""
    feed = Feed(
        id="test",
        name="Test Feed",
        sources=(FeedSource(type="layer", value=(3, 4)),),
        filters=(FeedFilter(field="layer", operator="eq", value=3),),
    )

    kb_pass = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=3,
    )
    assert feed.should_include(kb_pass)

    # Fails source
    kb_fail_source = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=1,
    )
    assert not feed.should_include(kb_fail_source)

    # Fails filter (even though it passes source)
    kb_fail_filter = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="",
        base_content="",
        zero_seed_layer=4,
    )
    assert not feed.should_include(kb_fail_filter)


def test_feed_serialization():
    """Feed.to_dict serializes feed configuration."""
    feed = Feed(
        id="test",
        name="Test Feed",
        description="A test feed",
        sources=(FeedSource(type="layer", value=3),),
        filters=(FeedFilter(field="layer", operator="gt", value=2),),
        ranking=FeedRanking(recency_weight=1.0),
    )

    data = feed.to_dict()
    assert data["id"] == "test"
    assert data["name"] == "Test Feed"
    assert data["description"] == "A test feed"
    assert len(data["sources"]) == 1
    assert len(data["filters"]) == 1
    assert data["ranking"]["recency_weight"] == 1.0
