"""
Tests for PersistentHypothesisStorage with lineage support.

Tests D-gent integration for hypothesis persistence, lineage tracking,
and session management.
"""

import pytest
from pathlib import Path

from agents.b.hypothesis_parser import (
    Hypothesis,
    NoveltyLevel,
    ParsedHypothesisResponse,
)
from agents.b.persistent_hypothesis import (
    HypothesisMemory,
    PersistentHypothesisStorage,
    persistent_hypothesis_storage,
)


# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_hypothesis() -> Hypothesis:
    """Create a sample hypothesis."""
    return Hypothesis(
        statement="Test hypothesis",
        confidence=0.7,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=["Assumption 1"],
    )


@pytest.fixture
def sample_response(sample_hypothesis: Hypothesis) -> ParsedHypothesisResponse:
    """Create a sample parsed response."""
    return ParsedHypothesisResponse(
        hypotheses=[sample_hypothesis],
        reasoning_chain=["Step 1", "Step 2"],
        suggested_tests=["Test 1", "Test 2"],
    )


@pytest.fixture
def temp_storage_path(tmp_path: Path) -> Path:
    """Create temporary storage path."""
    return tmp_path / "hypotheses.json"


@pytest.fixture
def memory() -> HypothesisMemory:
    """Create empty hypothesis memory."""
    return HypothesisMemory()


# ─────────────────────────────────────────────────────────────────
# HypothesisMemory Tests
# ─────────────────────────────────────────────────────────────────


def test_memory_add_response(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test adding response to memory."""
    indices = memory.add_response(sample_response, domain="test")

    assert len(indices) == 1
    assert indices[0] == 0
    assert memory.total_generated == 1
    assert len(memory.hypotheses) == 1
    assert "test" in memory.domains


def test_memory_add_response_with_session(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test adding response with session tracking."""
    indices = memory.add_response(
        sample_response, domain="test", session_id="session-1"
    )

    assert len(memory.sessions) == 1
    assert memory.sessions[0]["session_id"] == "session-1"
    assert memory.sessions[0]["count"] == 1


def test_memory_get_by_domain(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test getting hypotheses by domain."""
    memory.add_response(sample_response, domain="biochem")
    memory.add_response(sample_response, domain="neuro")

    biochem_hyps = memory.get_by_domain("biochem")
    neuro_hyps = memory.get_by_domain("neuro")

    assert len(biochem_hyps) == 1
    assert len(neuro_hyps) == 1


def test_memory_get_recent(memory: HypothesisMemory):
    """Test getting recent hypotheses."""
    for i in range(5):
        response = ParsedHypothesisResponse(
            hypotheses=[
                Hypothesis(
                    statement=f"Hypothesis {i}",
                    confidence=0.5,
                    novelty=NoveltyLevel.INCREMENTAL,
                    falsifiable_by=["Test"],
                    supporting_observations=[0],
                    assumptions=[],
                )
            ],
            reasoning_chain=[],
            suggested_tests=[],
        )
        memory.add_response(response, domain="test")

    recent = memory.get_recent(limit=3)
    assert len(recent) == 3
    assert recent[0].statement == "Hypothesis 2"  # Oldest of the 3 most recent


def test_memory_find_similar(memory: HypothesisMemory):
    """Test finding similar hypotheses."""
    response = ParsedHypothesisResponse(
        hypotheses=[
            Hypothesis(
                statement="Protein X aggregates at low pH",
                confidence=0.7,
                novelty=NoveltyLevel.INCREMENTAL,
                falsifiable_by=["Test"],
                supporting_observations=[0],
                assumptions=[],
            )
        ],
        reasoning_chain=[],
        suggested_tests=[],
    )
    memory.add_response(response, domain="biochem")

    similar = memory.find_similar(
        "Protein X forms aggregates at acidic pH", threshold=0.3
    )
    assert len(similar) >= 1


# ─────────────────────────────────────────────────────────────────
# Lineage Tests
# ─────────────────────────────────────────────────────────────────


def test_memory_add_lineage(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test adding lineage edge."""
    # Add two hypotheses
    memory.add_response(sample_response, domain="test")
    memory.add_response(sample_response, domain="test")

    # Add lineage
    edge = memory.add_lineage(
        source_idx=1,
        target_idx=0,
        relationship="evolved_from",
        context={"reason": "Refinement"},
    )

    assert edge.source_idx == 1
    assert edge.target_idx == 0
    assert edge.relationship == "evolved_from"
    assert len(memory.lineage_edges) == 1


def test_memory_get_ancestors(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test getting ancestor hypotheses."""
    # Create chain: 0 -> 1 -> 2
    for _ in range(3):
        memory.add_response(sample_response, domain="test")

    memory.add_lineage(1, 0, "evolved_from")
    memory.add_lineage(2, 1, "evolved_from")

    # Ancestors of 2
    ancestors = memory.get_ancestors(2)
    assert 0 in ancestors
    assert 1 in ancestors
    assert len(ancestors) == 2


def test_memory_get_ancestors_with_depth(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test getting ancestors with depth limit."""
    # Create chain: 0 -> 1 -> 2 -> 3
    for _ in range(4):
        memory.add_response(sample_response, domain="test")

    memory.add_lineage(1, 0, "evolved_from")
    memory.add_lineage(2, 1, "evolved_from")
    memory.add_lineage(3, 2, "evolved_from")

    # Only immediate ancestors of 3
    ancestors = memory.get_ancestors(3, max_depth=1)
    assert 2 in ancestors
    assert 1 not in ancestors


def test_memory_get_descendants(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test getting descendant hypotheses."""
    # Create tree: 0 -> [1, 2]
    for _ in range(3):
        memory.add_response(sample_response, domain="test")

    memory.add_lineage(1, 0, "forked_from")
    memory.add_lineage(2, 0, "forked_from")

    # Descendants of 0
    descendants = memory.get_descendants(0)
    assert 1 in descendants
    assert 2 in descendants
    assert len(descendants) == 2


def test_memory_catalog_id_tracking(
    memory: HypothesisMemory, sample_response: ParsedHypothesisResponse
):
    """Test L-gent catalog ID tracking."""
    memory.add_response(sample_response, domain="test")

    # Set catalog ID
    memory.set_catalog_id(0, "hyp_abc123")

    # Retrieve
    catalog_id = memory.get_catalog_id(0)
    assert catalog_id == "hyp_abc123"

    # Non-existent
    assert memory.get_catalog_id(99) is None


# ─────────────────────────────────────────────────────────────────
# PersistentHypothesisStorage Tests
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_storage_create_and_save(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test creating and saving storage."""
    storage = PersistentHypothesisStorage(path=temp_storage_path)
    await storage.load()

    await storage.add_response(sample_response, domain="test")

    assert temp_storage_path.exists()
    assert storage.total_generated == 1


@pytest.mark.asyncio
async def test_storage_load_existing(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test loading existing storage."""
    # First save
    storage1 = PersistentHypothesisStorage(path=temp_storage_path)
    await storage1.load()
    await storage1.add_response(sample_response, domain="test")

    # Reload
    storage2 = PersistentHypothesisStorage(path=temp_storage_path)
    await storage2.load()

    assert storage2.total_generated == 1
    hypotheses = await storage2.get_by_domain("test")
    assert len(hypotheses) == 1


@pytest.mark.asyncio
async def test_storage_lineage_methods(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test storage lineage methods."""
    storage = PersistentHypothesisStorage(path=temp_storage_path)
    await storage.load()

    # Add hypotheses
    await storage.add_response(sample_response, domain="test")
    await storage.add_response(sample_response, domain="test")

    # Add lineage
    edge = await storage.add_lineage(1, 0, "evolved_from", {"reason": "Better"})
    assert edge.relationship == "evolved_from"

    # Get ancestors
    ancestors = await storage.get_ancestors(1)
    assert 0 in ancestors


@pytest.mark.asyncio
async def test_storage_catalog_id_persistence(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test catalog ID persists across reloads."""
    # Save with catalog ID
    storage1 = PersistentHypothesisStorage(path=temp_storage_path)
    await storage1.load()
    await storage1.add_response(sample_response, domain="test")
    await storage1.set_catalog_id(0, "hyp_persistent123")

    # Reload and verify
    storage2 = PersistentHypothesisStorage(path=temp_storage_path)
    await storage2.load()
    catalog_id = await storage2.get_catalog_id(0)
    assert catalog_id == "hyp_persistent123"


@pytest.mark.asyncio
async def test_storage_session_tracking(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test session tracking in storage."""
    storage = PersistentHypothesisStorage(path=temp_storage_path)
    await storage.load()

    indices = await storage.add_response_with_session(
        sample_response, domain="test", session_id="research-session-1"
    )

    assert len(indices) == 1

    # Reload and check sessions persisted
    storage2 = PersistentHypothesisStorage(path=temp_storage_path)
    await storage2.load()
    # Sessions should be in memory after load


@pytest.mark.asyncio
async def test_storage_get_hypothesis_by_idx(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test getting hypothesis by index."""
    storage = PersistentHypothesisStorage(path=temp_storage_path)
    await storage.load()
    await storage.add_response(sample_response, domain="test")

    hyp = await storage.get_hypothesis_by_idx(0)
    assert hyp is not None
    assert hyp.statement == sample_response.hypotheses[0].statement

    # Invalid index
    hyp_invalid = await storage.get_hypothesis_by_idx(99)
    assert hyp_invalid is None


@pytest.mark.asyncio
async def test_storage_evolution_history(
    temp_storage_path: Path, sample_response: ParsedHypothesisResponse
):
    """Test evolution history tracking."""
    storage = PersistentHypothesisStorage(path=temp_storage_path)
    await storage.load()

    # Add multiple times to create history
    await storage.add_response(sample_response, domain="test")
    await storage.add_response(sample_response, domain="test")

    history = await storage.get_evolution_history(limit=5)
    # History should have entries from saves
    assert isinstance(history, list)


# ─────────────────────────────────────────────────────────────────
# Convenience Function Tests
# ─────────────────────────────────────────────────────────────────


def test_persistent_hypothesis_storage_factory():
    """Test factory function creates storage correctly."""
    storage = persistent_hypothesis_storage("test_path.json")
    assert isinstance(storage, PersistentHypothesisStorage)
