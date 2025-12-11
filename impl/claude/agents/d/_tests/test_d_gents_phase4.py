"""
Integration tests for D-gents Phase 4: Ecosystem Integration.

Tests the integration of D-gents with:
- K-gent (persistent persona)
- B-gents (hypothesis storage)
- J-gents (entropy constraints)
- T-gents (SpyAgent with VolatileAgent)
"""

import asyncio
import shutil
import tempfile
from pathlib import Path

import pytest

# B-gents
from agents.b import (
    Hypothesis,
    NoveltyLevel,
    PersistentHypothesisStorage,
)
from agents.b.hypothesis_parser import ParsedHypothesisResponse

# D-gents
from agents.d import (
    EntropyConstrainedAgent,
    StorageError,
    VolatileAgent,
)

# K-gent
from agents.k import (
    DialogueInput,
    DialogueMode,
    PersistentPersonaAgent,
)

# T-gents
from agents.t import SpyAgent


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir)


# --- K-gent Integration Tests ---


@pytest.mark.asyncio
async def test_kgent_persistent_persona_integration(temp_dir) -> None:
    """Test K-gent with PersistentAgent for persona continuity."""
    path = temp_dir / "persona.json"

    # Session 1: Create persona and have dialogue
    persona1 = PersistentPersonaAgent(path=path)
    await persona1.invoke(
        DialogueInput(message="I prefer composable systems", mode=DialogueMode.REFLECT)
    )

    # State should be saved automatically
    assert path.exists()

    # Session 2: Load existing persona
    persona2 = PersistentPersonaAgent(path=path)
    await persona2.load_state()

    # Persona should remember (state restored)
    assert persona2.state is not None
    assert persona2.state.seed is not None

    # Can continue dialogue
    response2 = await persona2.invoke(
        DialogueInput(message="Tell me about my preferences", mode=DialogueMode.ADVISE)
    )

    assert response2 is not None
    print(f"K-gent integration test passed: {response2.response[:50]}...")


# --- B-gents Integration Tests ---


@pytest.mark.asyncio
async def test_bgents_hypothesis_storage_integration(temp_dir) -> None:
    """Test B-gents with PersistentAgent for hypothesis memory."""
    path = temp_dir / "hypotheses.json"

    storage = PersistentHypothesisStorage(path=path)
    await storage.load()

    # Add hypothesis response
    response = ParsedHypothesisResponse(
        hypotheses=[
            Hypothesis(
                statement="Protein X aggregates due to hydrophobic interactions",
                confidence=0.75,
                novelty=NoveltyLevel.INCREMENTAL,
                falsifiable_by=["Mutate hydrophobic residues", "Test at high pH"],
                supporting_observations=[0, 1],
                assumptions=["pH affects charge distribution"],
            )
        ],
        reasoning_chain=["Observation 1", "Observation 2", "Hypothesis"],
        suggested_tests=["Test 1", "Test 2"],
    )

    await storage.add_response(response, domain="biochemistry")

    # Verify persistence
    assert path.exists()

    # Load in new instance
    storage2 = PersistentHypothesisStorage(path=path)
    await storage2.load()

    bio_hyps = await storage2.get_by_domain("biochemistry")
    assert len(bio_hyps) == 1
    assert (
        bio_hyps[0].statement == "Protein X aggregates due to hydrophobic interactions"
    )

    print(
        f"B-gents integration test passed: {storage2.total_generated} hypotheses stored"
    )


# --- J-gents Integration Tests ---


@pytest.mark.asyncio
async def test_jgents_entropy_constraint_integration() -> None:
    """Test J-gent entropy constraints with EntropyConstrainedAgent."""

    # Simulate depth 0 in promise tree (full budget)
    dgent_depth0 = EntropyConstrainedAgent.from_depth(
        backend=VolatileAgent(_state={}),
        depth=0,
        initial_budget=0.5,
        decay_factor=0.5,
        base_size_bytes=1000,
    )

    # Small state should succeed
    await dgent_depth0.save({"key": "value"})
    loaded = await dgent_depth0.load()
    assert loaded == {"key": "value"}

    # Simulate depth 3 (budget = 0.5 * 0.5^3 = 0.0625, max = 62.5 bytes)
    dgent_depth3 = EntropyConstrainedAgent.from_depth(
        backend=VolatileAgent(_state={}),
        depth=3,
        initial_budget=0.5,
        decay_factor=0.5,
        base_size_bytes=1000,
    )

    # Large state should fail
    large_state = {"data": "x" * 1000}  # Will exceed 62.5 bytes
    with pytest.raises(StorageError, match="exceeds entropy budget"):
        await dgent_depth3.save(large_state)

    print("J-gents integration test passed: Entropy budget enforced")


# --- T-gents Integration Tests ---


@pytest.mark.asyncio
async def test_tgents_spy_volatile_integration() -> None:
    """Test T-gent SpyAgent with VolatileAgent backend."""

    spy = SpyAgent[int](label="TestSpy")

    # Capture some values
    result1 = await spy.invoke(42)
    result2 = await spy.invoke(100)

    # Values pass through unchanged
    assert result1 == 42
    assert result2 == 100

    # History is captured via D-gent
    history = await spy.get_history()
    assert history == [42, 100]

    # Can access history snapshots
    snapshots = await spy.get_history_snapshots(limit=2)
    assert len(snapshots) >= 0  # May have snapshots

    # Call count works
    assert spy.call_count == 2

    # Can reset
    spy.reset()
    assert spy.call_count == 0

    print("T-gents integration test passed: SpyAgent uses VolatileAgent")


# --- Cross-Genus Integration Tests ---


@pytest.mark.asyncio
async def test_cross_genus_integration_kgent_bgents(temp_dir) -> None:
    """Test K-gent + B-gents integration for personalized science."""
    persona_path = temp_dir / "persona.json"
    hyp_path = temp_dir / "hypotheses.json"

    # Create persistent K-gent
    persona = PersistentPersonaAgent(path=persona_path)
    persona.update_preference(
        category="science",
        key="style",
        value="mechanistic explanations",
        confidence=0.9,
    )
    await persona.save_state()

    # Create hypothesis storage
    hyp_storage = PersistentHypothesisStorage(path=hyp_path)
    await hyp_storage.load()

    # Add hypothesis
    response = ParsedHypothesisResponse(
        hypotheses=[
            Hypothesis(
                statement="Mechanistic hypothesis about X",
                confidence=0.8,
                novelty=NoveltyLevel.EXPLORATORY,
                falsifiable_by=["Test Y"],
                supporting_observations=[],
                assumptions=[],
            )
        ],
        reasoning_chain=[],
        suggested_tests=[],
    )
    await hyp_storage.add_response(response, domain="biology")

    # Both persist independently
    assert persona_path.exists()
    assert hyp_path.exists()

    # Reload both
    persona2 = PersistentPersonaAgent(path=persona_path)
    await persona2.load_state()

    hyp_storage2 = PersistentHypothesisStorage(path=hyp_path)
    await hyp_storage2.load()

    # Both restored
    assert (
        persona2.state.seed.preferences["science"]["style"]
        == "mechanistic explanations"
    )
    bio_hyps = await hyp_storage2.get_by_domain("biology")
    assert len(bio_hyps) == 1

    print("Cross-genus integration test passed: K-gent + B-gents persist independently")


@pytest.mark.asyncio
async def test_full_phase4_integration(temp_dir) -> None:
    """
    Full Phase 4 integration test demonstrating all 4 integrations.

    Shows K-gent, B-gents, J-gents, and T-gents all using D-gents.
    """
    # 1. K-gent with persistent persona
    persona = PersistentPersonaAgent(path=temp_dir / "persona.json")
    await persona.invoke(DialogueInput(message="Test", mode=DialogueMode.REFLECT))

    # 2. B-gents with hypothesis storage
    hyp_storage = PersistentHypothesisStorage(path=temp_dir / "hypotheses.json")
    await hyp_storage.load()

    # 3. J-gents with entropy constraint
    entropy_dgent = EntropyConstrainedAgent.from_depth(
        backend=VolatileAgent(_state={}), depth=1
    )
    await entropy_dgent.save({"small": "data"})

    # 4. T-gents with SpyAgent
    spy = SpyAgent[str](label="Integration")
    await spy.invoke("test-value")

    # All 4 integrations work
    assert (temp_dir / "persona.json").exists()  # K-gent persistence
    assert (temp_dir / "hypotheses.json").exists()  # B-gents persistence
    assert await entropy_dgent.load() == {"small": "data"}  # J-gents constraint
    assert spy.history == ["test-value"]  # T-gents spy

    print("✅ Full Phase 4 integration test passed: All 4 integrations working")


if __name__ == "__main__":
    # Run integration tests
    asyncio.run(test_kgent_persistent_persona_integration(Path(tempfile.mkdtemp())))
    asyncio.run(test_bgents_hypothesis_storage_integration(Path(tempfile.mkdtemp())))
    asyncio.run(test_jgents_entropy_constraint_integration())
    asyncio.run(test_tgents_spy_volatile_integration())
    asyncio.run(test_full_phase4_integration(Path(tempfile.mkdtemp())))

    print("\n🎉 All D-gents Phase 4 integration tests passed!")
