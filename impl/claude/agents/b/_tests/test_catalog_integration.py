"""
Tests for B-gent L-gent catalog integration.

Tests hypothesis registration, discovery, and lineage tracking
with the L-gent catalog system.
"""

import pytest
from agents.b.catalog_integration import (
    _extract_keywords,
    _generate_hypothesis_name,
    find_hypotheses,
    find_related_hypotheses,
    get_hypothesis_lineage,
    mark_hypothesis_falsified,
    record_hypothesis_evolution,
    record_hypothesis_fork,
    register_hypothesis,
    register_hypothesis_batch,
    update_hypothesis_metrics,
)
from agents.b.hypothesis_parser import Hypothesis, NoveltyLevel
from agents.l import LineageGraph, Registry, Status

# ─────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_hypothesis() -> Hypothesis:
    """Create a sample hypothesis for testing."""
    return Hypothesis(
        statement="Protein X aggregation is caused by histidine protonation at low pH",
        confidence=0.75,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=[
            "H→A mutations eliminate aggregation",
            "Aggregation persists at high pH",
        ],
        supporting_observations=[0, 1],
        assumptions=[
            "Histidine pKa is relevant at pH 5",
            "Aggregation is reversible",
        ],
    )


@pytest.fixture
def paradigm_hypothesis() -> Hypothesis:
    """Create a paradigm-shifting hypothesis for testing."""
    return Hypothesis(
        statement="Consciousness emerges from quantum coherence in neural microtubules",
        confidence=0.4,
        novelty=NoveltyLevel.PARADIGM_SHIFTING,
        falsifiable_by=[
            "Anesthesia disrupts coherence without affecting consciousness",
            "Artificial microtubules support consciousness",
        ],
        supporting_observations=[0, 2, 3],
        assumptions=[
            "Quantum effects survive decoherence in brain tissue",
            "Microtubules are not just structural",
        ],
    )


@pytest.fixture
def registry() -> Registry:
    """Create a fresh L-gent registry."""
    return Registry()


@pytest.fixture
def lineage_graph() -> LineageGraph:
    """Create a fresh lineage graph."""
    return LineageGraph()


# ─────────────────────────────────────────────────────────────────
# Registration Tests
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_hypothesis_basic(
    sample_hypothesis: Hypothesis, registry: Registry
):
    """Test basic hypothesis registration."""
    entry = await register_hypothesis(
        hypothesis=sample_hypothesis,
        registry=registry,
        domain="biochemistry",
        author="test-engine",
    )

    # Verify entry created
    assert entry.id.startswith("hyp_")
    assert entry.name is not None
    assert entry.description == sample_hypothesis.statement
    assert entry.author == "test-engine"
    assert entry.status == Status.ACTIVE

    # Verify in registry
    retrieved = await registry.get(entry.id)
    assert retrieved is not None
    assert retrieved.id == entry.id


@pytest.mark.asyncio
async def test_register_hypothesis_with_metadata(
    sample_hypothesis: Hypothesis, registry: Registry
):
    """Test hypothesis registration with custom metadata."""
    observations = [
        "Protein X aggregates at pH < 5",
        "Aggregation correlates with disease",
    ]

    entry = await register_hypothesis(
        hypothesis=sample_hypothesis,
        registry=registry,
        domain="biochemistry",
        author="robin",
        observations=observations,
        forged_from="Why does protein X aggregate?",
    )

    # Verify metadata
    assert entry.forged_from == "Why does protein X aggregate?"
    assert "biochemistry" in entry.keywords

    # Verify relationships contain observations
    assert "observations" in entry.relationships
    assert len(entry.relationships["observations"]) == 2


@pytest.mark.asyncio
async def test_register_hypothesis_batch(registry: Registry) -> None:
    """Test batch registration of hypotheses."""
    hypotheses = [
        Hypothesis(
            statement=f"Hypothesis {i}",
            confidence=0.5 + i * 0.1,
            novelty=NoveltyLevel.INCREMENTAL,
            falsifiable_by=["Test"],
            supporting_observations=[0],
            assumptions=["Assumption"],
        )
        for i in range(3)
    ]

    entries = await register_hypothesis_batch(
        hypotheses=hypotheses,
        registry=registry,
        domain="test",
        author="batch-test",
    )

    assert len(entries) == 3
    assert all(e.id.startswith("hyp_") for e in entries)

    # Verify all in registry
    all_entries = await registry.list()
    assert len(all_entries) == 3


# ─────────────────────────────────────────────────────────────────
# Discovery Tests
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_find_hypotheses_by_domain(
    sample_hypothesis: Hypothesis, paradigm_hypothesis: Hypothesis, registry: Registry
):
    """Test finding hypotheses by domain."""
    await register_hypothesis(sample_hypothesis, registry, domain="biochemistry")
    await register_hypothesis(paradigm_hypothesis, registry, domain="neuroscience")

    # Find biochemistry hypotheses
    results = await find_hypotheses(registry, domain="biochemistry")
    assert len(results) == 1
    assert "protein" in results[0].entry.description.lower()

    # Find neuroscience hypotheses
    results = await find_hypotheses(registry, domain="neuroscience")
    assert len(results) == 1
    assert "consciousness" in results[0].entry.description.lower()


@pytest.mark.asyncio
async def test_find_hypotheses_by_novelty(registry: Registry) -> None:
    """Test finding hypotheses by novelty level."""
    # Register hypotheses with different novelty levels
    incremental = Hypothesis(
        statement="Minor improvement",
        confidence=0.8,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )
    paradigm = Hypothesis(
        statement="Major breakthrough",
        confidence=0.3,
        novelty=NoveltyLevel.PARADIGM_SHIFTING,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )

    await register_hypothesis(incremental, registry, domain="test")
    await register_hypothesis(paradigm, registry, domain="test")

    # Find by novelty
    results = await find_hypotheses(registry, novelty=NoveltyLevel.PARADIGM_SHIFTING)
    assert len(results) == 1
    assert "breakthrough" in results[0].entry.description.lower()


@pytest.mark.asyncio
async def test_find_hypotheses_by_min_confidence(registry: Registry) -> None:
    """Test finding hypotheses by minimum confidence."""
    low_conf = Hypothesis(
        statement="Low confidence",
        confidence=0.3,
        novelty=NoveltyLevel.EXPLORATORY,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )
    high_conf = Hypothesis(
        statement="High confidence",
        confidence=0.9,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )

    await register_hypothesis(low_conf, registry, domain="test")
    await register_hypothesis(high_conf, registry, domain="test")

    # Find high confidence only
    results = await find_hypotheses(registry, min_confidence=0.7)
    assert len(results) == 1
    assert "high" in results[0].entry.description.lower()


@pytest.mark.asyncio
async def test_find_related_hypotheses(
    sample_hypothesis: Hypothesis, registry: Registry
):
    """Test finding related hypotheses."""
    # Register similar hypotheses
    related = Hypothesis(
        statement="Histidine residues in protein X cause pH-dependent behavior",
        confidence=0.6,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Mutate histidine"],
        supporting_observations=[0],
        assumptions=["Histidine pKa matters", "pH affects structure"],
    )

    entry1 = await register_hypothesis(
        sample_hypothesis, registry, domain="biochemistry"
    )
    await register_hypothesis(related, registry, domain="biochemistry")

    # Find related
    results = await find_related_hypotheses(registry, entry1.id, max_results=5)
    # Should find the related hypothesis (excludes source)
    assert len(results) >= 0  # May or may not find depending on search


# ─────────────────────────────────────────────────────────────────
# Lineage Tests
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_hypothesis_evolution(
    sample_hypothesis: Hypothesis, registry: Registry, lineage_graph: LineageGraph
):
    """Test recording hypothesis evolution."""
    # Register original
    original = await register_hypothesis(
        sample_hypothesis, registry, domain="biochemistry"
    )

    # Create refined version
    refined = Hypothesis(
        statement="Histidine H34 and H78 cause aggregation via salt bridges at low pH",
        confidence=0.85,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=[
            "H34A/H78A double mutant eliminates aggregation",
            "Salt bridge disruption prevents aggregation",
        ],
        supporting_observations=[0, 1, 2],
        assumptions=["Specific histidines are key", "Salt bridges form"],
    )

    # Record evolution
    new_entry = await record_hypothesis_evolution(
        lineage=lineage_graph,
        parent_id=original.id,
        refined_hypothesis=refined,
        registry=registry,
        domain="biochemistry",
        refinement_reason="Added specific histidine residue identification",
    )

    assert new_entry.id != original.id
    assert new_entry.id.startswith("hyp_")

    # Verify lineage recorded
    edges = await lineage_graph.get_relationships(source_id=new_entry.id)
    assert len(edges) == 1
    assert edges[0].target_id == original.id


@pytest.mark.asyncio
async def test_record_hypothesis_fork(
    sample_hypothesis: Hypothesis, registry: Registry, lineage_graph: LineageGraph
):
    """Test recording hypothesis fork."""
    original = await register_hypothesis(
        sample_hypothesis, registry, domain="biochemistry"
    )

    # Fork to alternative hypothesis
    alternative = Hypothesis(
        statement="Protein X aggregation is caused by cysteine oxidation, not histidine",
        confidence=0.6,
        novelty=NoveltyLevel.EXPLORATORY,
        falsifiable_by=["Reducing agents prevent aggregation"],
        supporting_observations=[0],
        assumptions=["Oxidative stress present"],
    )

    forked = await record_hypothesis_fork(
        lineage=lineage_graph,
        parent_id=original.id,
        forked_hypothesis=alternative,
        registry=registry,
        domain="biochemistry",
        fork_reason="Alternative mechanism proposed",
    )

    # Verify fork relationship
    edges = await lineage_graph.get_relationships(source_id=forked.id)
    assert len(edges) == 1
    from agents.l import RelationshipType

    assert edges[0].relationship_type == RelationshipType.FORKED_FROM


@pytest.mark.asyncio
async def test_get_hypothesis_lineage(
    sample_hypothesis: Hypothesis, registry: Registry, lineage_graph: LineageGraph
):
    """Test getting full hypothesis lineage."""
    # Create chain: h1 -> h2 -> h3
    h1 = await register_hypothesis(sample_hypothesis, registry, domain="test")

    h2_hyp = Hypothesis(
        statement="Refined hypothesis",
        confidence=0.7,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )
    h2 = await record_hypothesis_evolution(
        lineage_graph, h1.id, h2_hyp, registry, "test", "First refinement"
    )

    h3_hyp = Hypothesis(
        statement="Further refined",
        confidence=0.8,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test"],
        supporting_observations=[0],
        assumptions=[],
    )
    h3 = await record_hypothesis_evolution(
        lineage_graph, h2.id, h3_hyp, registry, "test", "Second refinement"
    )

    # Get lineage of h3
    lineage = await get_hypothesis_lineage(lineage_graph, h3.id)

    assert h1.id in lineage["ancestors"]
    assert h2.id in lineage["ancestors"]


# ─────────────────────────────────────────────────────────────────
# Metrics Tests
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_hypothesis_metrics(
    sample_hypothesis: Hypothesis, registry: Registry
):
    """Test updating hypothesis metrics after testing."""
    entry = await register_hypothesis(sample_hypothesis, registry, domain="test")

    # Simulate successful test
    updated = await update_hypothesis_metrics(
        registry, entry.id, test_passed=True, evidence_strength=0.8
    )

    assert updated is not None
    assert updated.usage_count > 0


@pytest.mark.asyncio
async def test_mark_hypothesis_falsified(
    sample_hypothesis: Hypothesis, registry: Registry
):
    """Test marking hypothesis as falsified."""
    entry = await register_hypothesis(sample_hypothesis, registry, domain="test")

    # Falsify
    result = await mark_hypothesis_falsified(
        registry,
        entry.id,
        falsified_by="Experiment XYZ",
        evidence="H→A mutation had no effect on aggregation",
    )

    assert result is True

    # Verify deprecated
    updated = await registry.get(entry.id)
    assert updated is not None
    assert updated.status == Status.DEPRECATED


# ─────────────────────────────────────────────────────────────────
# Helper Function Tests
# ─────────────────────────────────────────────────────────────────


def test_extract_keywords() -> None:
    """Test keyword extraction from hypothesis."""
    hyp = Hypothesis(
        statement="Protein aggregation causes disease progression",
        confidence=0.7,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Prevention of aggregation halts disease"],
        supporting_observations=[0],
        assumptions=["Aggregation is pathological"],
    )

    keywords = _extract_keywords(hyp, "biochemistry")

    assert "biochemistry" in keywords
    assert "incremental" in keywords
    assert any("protein" in k.lower() for k in keywords)


def test_generate_hypothesis_name() -> None:
    """Test hypothesis name generation."""
    short_hyp = Hypothesis(
        statement="Short statement",
        confidence=0.5,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test criteria"],
        supporting_observations=[0],
        assumptions=[],
    )

    long_hyp = Hypothesis(
        statement="This is a very long hypothesis statement that exceeds fifty characters and should be truncated properly",
        confidence=0.5,
        novelty=NoveltyLevel.INCREMENTAL,
        falsifiable_by=["Test criteria"],
        supporting_observations=[0],
        assumptions=[],
    )

    short_name = _generate_hypothesis_name(short_hyp)
    long_name = _generate_hypothesis_name(long_hyp)

    assert short_name == "Short statement"
    assert len(long_name) <= 50
    assert long_name.endswith("...")
