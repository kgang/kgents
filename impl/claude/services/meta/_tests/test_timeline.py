"""
Tests for TimelineService.

Verifies coherence tracking, breakthrough detection, and narrative generation.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.k_block.core.kblock import KBlock, generate_kblock_id
from services.k_block.zero_seed_storage import ZeroSeedStorage
from services.meta.timeline import TimelineService


@pytest.fixture
def storage() -> ZeroSeedStorage:
    """Create empty storage."""
    return ZeroSeedStorage()


@pytest.fixture
def storage_with_kblocks(storage: ZeroSeedStorage) -> ZeroSeedStorage:
    """Create storage with sample K-Blocks (using mock with layer/loss attributes)."""
    from unittest.mock import MagicMock

    # Create mock K-Blocks with layer and layer_loss attributes
    # (Real K-Blocks use zero_seed_layer and confidence, but for testing coherence logic we use these)
    mock_kblocks = []
    layer_data = [
        (1, 0.05),  # Axiom
        (2, 0.12),  # Value
        (3, 0.28),  # Goal
        (4, 0.42),  # Spec
        (5, 0.58),  # Action
    ]

    for layer, loss in layer_data:
        mock_kb = MagicMock()
        mock_kb.id = generate_kblock_id()
        mock_kb.layer = layer
        mock_kb.layer_loss = loss
        mock_kb.edges = []
        storage._kblocks[mock_kb.id] = mock_kb
        mock_kblocks.append(mock_kb)

    return storage


# =============================================================================
# Timeline Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_timeline_empty(storage: ZeroSeedStorage):
    """Test timeline with no K-Blocks."""
    service = TimelineService(storage)
    timeline = await service.get_timeline()

    assert timeline.current_score == 0.0
    assert timeline.average_score == 0.0
    assert len(timeline.points) == 1  # Always has current snapshot
    assert len(timeline.breakthroughs) == 0
    assert timeline.total_nodes == 0
    assert timeline.total_edges == 0


@pytest.mark.asyncio
async def test_get_timeline_with_kblocks(storage_with_kblocks: ZeroSeedStorage):
    """Test timeline with sample K-Blocks."""
    service = TimelineService(storage_with_kblocks)
    timeline = await service.get_timeline()

    # Should have coherence data
    assert timeline.current_score > 0.0
    assert timeline.current_score < 1.0
    assert timeline.total_nodes == 5
    assert len(timeline.points) == 1

    # Check layer distribution
    assert 1 in timeline.layer_distribution
    assert 2 in timeline.layer_distribution
    assert 3 in timeline.layer_distribution
    assert 4 in timeline.layer_distribution
    assert 5 in timeline.layer_distribution


@pytest.mark.asyncio
async def test_coherence_calculation(storage_with_kblocks: ZeroSeedStorage):
    """Test coherence score calculation."""
    service = TimelineService(storage_with_kblocks)
    timeline = await service.get_timeline()

    # Coherence = 1 - avg_loss
    # avg_loss = (0.05 + 0.12 + 0.28 + 0.42 + 0.58) / 5 = 0.29
    # coherence = 1 - 0.29 = 0.71
    expected_coherence = 1.0 - (0.05 + 0.12 + 0.28 + 0.42 + 0.58) / 5
    assert abs(timeline.current_score - expected_coherence) < 0.01


@pytest.mark.asyncio
async def test_layer_distribution(storage_with_kblocks: ZeroSeedStorage):
    """Test layer distribution calculation."""
    service = TimelineService(storage_with_kblocks)
    timeline = await service.get_timeline()

    # Should have one K-Block per layer
    assert timeline.layer_distribution[1] == 1
    assert timeline.layer_distribution[2] == 1
    assert timeline.layer_distribution[3] == 1
    assert timeline.layer_distribution[4] == 1
    assert timeline.layer_distribution[5] == 1


# =============================================================================
# Story Tests
# =============================================================================


@pytest.mark.asyncio
async def test_tell_story_empty(storage: ZeroSeedStorage):
    """Test story generation with no K-Blocks."""
    service = TimelineService(storage)
    timeline = await service.get_timeline()
    story = await service.tell_story(timeline)

    # Story should acknowledge beginning or emergence
    assert ("journey" in story.lower() or "garden" in story.lower())
    assert len(story) > 0


@pytest.mark.asyncio
async def test_tell_story_with_data(storage_with_kblocks: ZeroSeedStorage):
    """Test story generation with K-Blocks."""
    service = TimelineService(storage_with_kblocks)
    timeline = await service.get_timeline()
    story = await service.tell_story(timeline)

    # Story should mention coherence
    assert "coherent" in story.lower() or "coherence" in story.lower()

    # Story should mention nodes
    assert "node" in story.lower()

    # Story should have philosophical closing
    assert "garden" in story.lower() or "proof" in story.lower()


# =============================================================================
# Breakthrough Detection Tests
# =============================================================================


def test_detect_breakthroughs_empty(storage: ZeroSeedStorage):
    """Test breakthrough detection with empty timeline."""
    service = TimelineService(storage)
    breakthroughs = service._detect_breakthroughs([])

    assert len(breakthroughs) == 0


def test_detect_breakthroughs_single_point(storage: ZeroSeedStorage):
    """Test breakthrough detection with single point."""
    from services.meta.timeline import CoherencePoint

    service = TimelineService(storage)
    points = [
        CoherencePoint(
            timestamp=datetime.now(timezone.utc),
            score=0.5,
        )
    ]
    breakthroughs = service._detect_breakthroughs(points)

    assert len(breakthroughs) == 0


def test_detect_breakthroughs_with_jump(storage: ZeroSeedStorage):
    """Test breakthrough detection with significant jump."""
    from services.meta.timeline import CoherencePoint

    service = TimelineService(storage)

    # Create points with a significant jump
    now = datetime.now(timezone.utc)
    points = [
        CoherencePoint(timestamp=now, score=0.5),
        CoherencePoint(timestamp=now, score=0.51),  # Small change
        CoherencePoint(timestamp=now, score=0.52),  # Small change
        CoherencePoint(timestamp=now, score=0.75),  # BIG JUMP (+0.23)
        CoherencePoint(timestamp=now, score=0.76),  # Small change
    ]

    breakthroughs = service._detect_breakthroughs(points)

    # Should detect the jump from 0.52 → 0.75
    assert len(breakthroughs) >= 1
    assert breakthroughs[0].delta > 0.1  # Significant jump
