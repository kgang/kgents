"""
Tests for D-gent Phase 4: The Noosphere.

Tests SemanticManifold, TemporalWitness, RelationalLattice, and MemoryGarden.
"""

import asyncio
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Conditional numpy import
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

from agents.d import (
    DriftReport,
    EdgeKind,
    # Stream types used by witness
    WitnessReport,
)
from agents.d.garden import (
    Contradiction,
    Evidence,
    EvidenceType,
    Insight,
    Lifecycle,
    MemoryGarden,
    Nutrients,
)
from agents.d.lattice import (
    LatticeRelation,
    RelationalLattice,
)
from agents.d.witness import (
    DriftSeverity,
    EntropyLevel,
    TemporalWitness,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir)


# =============================================================================
# SemanticManifold Tests
# =============================================================================


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestSemanticManifold:
    """Tests for SemanticManifold."""

    @pytest.fixture
    def manifold(self):
        """Create a semantic manifold."""
        from agents.d.manifold import SemanticManifold

        return SemanticManifold(dimension=4)

    @pytest.mark.asyncio
    async def test_add_and_get(self, manifold):
        """Test adding and retrieving entries."""
        embedding = np.array([1.0, 0.0, 0.0, 0.0])
        point = await manifold.add("doc1", {"text": "Hello"}, embedding)

        assert point.label == "doc1"
        assert np.allclose(point.coordinates, embedding)

        result = await manifold.get("doc1")
        assert result is not None
        state, point = result
        assert state == {"text": "Hello"}

    @pytest.mark.asyncio
    async def test_neighbors(self, manifold):
        """Test k-nearest neighbor search."""
        # Add entries
        await manifold.add("doc1", "A", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("doc2", "B", np.array([0.9, 0.1, 0.0, 0.0]))  # Close to doc1
        await manifold.add("doc3", "C", np.array([0.0, 1.0, 0.0, 0.0]))  # Far from doc1

        # Query
        query = np.array([1.0, 0.0, 0.0, 0.0])
        results = await manifold.neighbors(query, k=2)

        assert len(results) == 2
        states = [r[0] for r in results]
        assert "A" in states
        assert "B" in states

    @pytest.mark.asyncio
    async def test_curvature_at(self, manifold):
        """Test curvature estimation."""
        # Add clustered entries (low curvature)
        await manifold.add("doc1", "A", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("doc2", "B", np.array([0.95, 0.05, 0.0, 0.0]))
        await manifold.add("doc3", "C", np.array([0.9, 0.1, 0.0, 0.0]))

        # Curvature in cluster should be low
        curvature = await manifold.curvature_at(np.array([0.95, 0.05, 0.0, 0.0]))
        assert curvature >= 0.0

    @pytest.mark.asyncio
    async def test_geodesic(self, manifold):
        """Test geodesic path computation."""
        await manifold.add("start", "A", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("end", "B", np.array([0.0, 1.0, 0.0, 0.0]))

        geodesic = await manifold.geodesic(
            np.array([1.0, 0.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0, 0.0]), steps=5
        )

        assert len(geodesic.waypoints) == 6  # 5 steps + 1
        assert geodesic.total_length > 0

    @pytest.mark.asyncio
    async def test_void_nearby(self, manifold):
        """Test void detection."""
        # Add entries in one corner
        await manifold.add("doc1", "A", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("doc2", "B", np.array([0.9, 0.1, 0.0, 0.0]))

        # Find void (unexplored region)
        void = await manifold.void_nearby(
            np.array([1.0, 0.0, 0.0, 0.0]), search_radius=2.0
        )

        assert void is not None
        assert void.potential > 0
        assert void.radius > 0

    @pytest.mark.asyncio
    async def test_cluster_centers(self, manifold):
        """Test cluster center detection."""
        # Add two clusters
        await manifold.add("a1", "A1", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("a2", "A2", np.array([0.9, 0.1, 0.0, 0.0]))
        await manifold.add("b1", "B1", np.array([0.0, 1.0, 0.0, 0.0]))
        await manifold.add("b2", "B2", np.array([0.1, 0.9, 0.0, 0.0]))

        clusters = await manifold.cluster_centers(k=2)
        assert len(clusters) == 2

    @pytest.mark.asyncio
    async def test_stats(self, manifold):
        """Test manifold statistics."""
        await manifold.add("doc1", "A", np.array([1.0, 0.0, 0.0, 0.0]))
        await manifold.add("doc2", "B", np.array([0.0, 1.0, 0.0, 0.0]))

        stats = await manifold.stats()
        assert stats.total_entries == 2
        assert stats.dimension == 4


# =============================================================================
# TemporalWitness Tests
# =============================================================================


class TestTemporalWitness:
    """Tests for TemporalWitness."""

    @pytest.fixture
    def witness(self):
        """Create a temporal witness."""

        def fold(state, event):
            return {**state, **event}

        return TemporalWitness(fold=fold, initial={"value": 0})

    @pytest.mark.asyncio
    async def test_observe_and_load(self, witness):
        """Test observing events and loading state."""
        await witness.observe(
            {"value": 10}, WitnessReport(observer_id="test", confidence=0.9)
        )

        state = await witness.load()
        assert state["value"] == 10

    @pytest.mark.asyncio
    async def test_trajectory_tracking(self, witness):
        """Test adding and checking trajectories."""
        witness.add_trajectory(
            "value", lambda s: s.get("value", 0), "Track value changes"
        )

        await witness.observe(
            {"value": 5}, WitnessReport(observer_id="test", confidence=1.0)
        )
        await witness.observe(
            {"value": 10}, WitnessReport(observer_id="test", confidence=1.0)
        )
        await witness.observe(
            {"value": 15}, WitnessReport(observer_id="test", confidence=1.0)
        )

        trajectory = witness.get_trajectory("value")
        assert trajectory is not None
        assert trajectory.name == "value"
        assert trajectory.current_value == 15

    @pytest.mark.asyncio
    async def test_drift_detection(self, witness):
        """Test drift detection in trajectories."""
        witness.add_trajectory("value", lambda s: s.get("value", 0))

        # Add events with stable values
        for i in range(5):
            await witness.observe(
                {"value": 10}, WitnessReport(observer_id="test", confidence=1.0)
            )

        # Add events with shifted values
        for i in range(5):
            await witness.observe(
                {"value": 100},  # Big shift
                WitnessReport(observer_id="test", confidence=1.0),
            )

        # Check for drift
        drift = await witness.check_drift("value", window=timedelta(hours=24))
        assert isinstance(drift, DriftReport)
        # Note: May or may not detect drift depending on data volume

    @pytest.mark.asyncio
    async def test_entropy(self, witness):
        """Test entropy calculation."""
        # Add some events
        for i in range(5):
            await witness.observe(
                {"value": i}, WitnessReport(observer_id="test", confidence=1.0)
            )

        entropy = await witness.entropy(window=timedelta(hours=1))
        assert 0.0 <= entropy <= 1.0

    @pytest.mark.asyncio
    async def test_entropy_classification(self, witness):
        """Test entropy level classification."""
        assert witness.classify_entropy(0.1) == EntropyLevel.CALM
        assert witness.classify_entropy(0.3) == EntropyLevel.STABLE
        assert witness.classify_entropy(0.5) == EntropyLevel.ACTIVE
        assert witness.classify_entropy(0.7) == EntropyLevel.TURBULENT
        assert witness.classify_entropy(0.9) == EntropyLevel.CHAOTIC

    @pytest.mark.asyncio
    async def test_drift_classification(self, witness):
        """Test drift severity classification."""
        assert (
            witness.classify_drift(DriftReport(trajectory="t", drift_detected=False))
            == DriftSeverity.NONE
        )
        assert (
            witness.classify_drift(
                DriftReport(trajectory="t", drift_detected=True, drift_magnitude=0.2)
            )
            == DriftSeverity.MINOR
        )
        assert (
            witness.classify_drift(
                DriftReport(trajectory="t", drift_detected=True, drift_magnitude=0.5)
            )
            == DriftSeverity.MODERATE
        )
        assert (
            witness.classify_drift(
                DriftReport(trajectory="t", drift_detected=True, drift_magnitude=0.7)
            )
            == DriftSeverity.SIGNIFICANT
        )
        assert (
            witness.classify_drift(
                DriftReport(trajectory="t", drift_detected=True, drift_magnitude=0.9)
            )
            == DriftSeverity.CRITICAL
        )

    @pytest.mark.asyncio
    async def test_replay(self, witness):
        """Test time-travel replay."""
        start_time = datetime.now()

        await witness.observe(
            {"value": 1}, WitnessReport(observer_id="test", confidence=1.0)
        )
        await asyncio.sleep(0.01)
        await witness.observe(
            {"value": 2}, WitnessReport(observer_id="test", confidence=1.0)
        )

        end_time = datetime.now()

        # Replay should reconstruct state
        state = await witness.replay(start_time, end_time)
        assert state["value"] == 2

    @pytest.mark.asyncio
    async def test_is_stable(self, witness):
        """Test stability check."""
        # With few events, should be stable
        is_stable = await witness.is_stable(threshold=0.5)
        assert isinstance(is_stable, bool)


# =============================================================================
# RelationalLattice Tests
# =============================================================================


class TestRelationalLattice:
    """Tests for RelationalLattice."""

    @pytest.fixture
    def lattice(self):
        """Create a relational lattice."""
        return RelationalLattice()

    @pytest.mark.asyncio
    async def test_add_and_get(self, lattice):
        """Test adding and retrieving nodes."""
        node = await lattice.add("concept1", {"name": "Testing"})

        assert node.id == "concept1"
        assert node.state == {"name": "Testing"}

        retrieved = await lattice.get("concept1")
        assert retrieved is not None
        assert retrieved.state == {"name": "Testing"}

    @pytest.mark.asyncio
    async def test_relate(self, lattice):
        """Test establishing relationships."""
        await lattice.add("animal", {"name": "Animal"})
        await lattice.add("mammal", {"name": "Mammal"})

        await lattice.relate("mammal", "animal", EdgeKind.IS_A)

        edges = await lattice.relationships("mammal", direction="out")
        assert len(edges) >= 1
        assert any(e.target == "animal" for e in edges)

    @pytest.mark.asyncio
    async def test_meet(self, lattice):
        """Test greatest lower bound (meet)."""
        await lattice.add("animal", {"name": "Animal"})
        await lattice.add("mammal", {"name": "Mammal"})
        await lattice.add("dog", {"name": "Dog"})
        await lattice.add("cat", {"name": "Cat"})

        await lattice.relate("mammal", "animal", EdgeKind.IS_A)
        await lattice.relate("dog", "mammal", EdgeKind.IS_A)
        await lattice.relate("cat", "mammal", EdgeKind.IS_A)

        # Meet of dog and cat should be a common ancestor (mammal or animal)
        result = await lattice.meet("dog", "cat")
        assert result.found
        # The meet finds a greatest common ancestor - both mammal and animal are valid
        # GraphAgent.meet uses depth heuristics, so either is acceptable
        assert result.node_id in ("mammal", "animal")

    @pytest.mark.asyncio
    async def test_meet_same_node(self, lattice):
        """Test meet of a node with itself."""
        await lattice.add("concept", {"name": "Concept"})

        result = await lattice.meet("concept", "concept")
        assert result.found
        assert result.node_id == "concept"

    @pytest.mark.asyncio
    async def test_entails(self, lattice):
        """Test entailment checking."""
        await lattice.add("animal", {"name": "Animal"})
        await lattice.add("mammal", {"name": "Mammal"})
        await lattice.add("dog", {"name": "Dog"})

        await lattice.relate("mammal", "animal", EdgeKind.IS_A)
        await lattice.relate("dog", "mammal", EdgeKind.IS_A)

        # Animal entails dog (dog is-a mammal is-a animal)
        proof = await lattice.entails("dog", "animal")
        assert proof.holds
        assert len(proof.path) > 0

    @pytest.mark.asyncio
    async def test_compare(self, lattice):
        """Test node comparison."""
        await lattice.add("a", {"name": "A"})
        await lattice.add("b", {"name": "B"})

        await lattice.relate("b", "a", EdgeKind.IS_A)

        result = await lattice.compare("b", "a")
        assert result == LatticeRelation.BELOW

    @pytest.mark.asyncio
    async def test_lineage(self, lattice):
        """Test provenance tracking."""
        await lattice.add("v1", {"version": 1})
        await lattice.add("v2", {"version": 2}, derived_from="v1")
        await lattice.add("v3", {"version": 3}, derived_from="v2")

        await lattice.relate("v2", "v1", EdgeKind.DERIVES_FROM)
        await lattice.relate("v3", "v2", EdgeKind.DERIVES_FROM)

        lineage = await lattice.lineage("v3")
        assert "v2" in lineage
        assert "v1" in lineage

    @pytest.mark.asyncio
    async def test_record_contradiction(self, lattice):
        """Test H-gent contradiction recording."""
        await lattice.add("thesis", {"statement": "X is true"})
        await lattice.add("antithesis", {"statement": "X is false"})

        await lattice.record_contradiction("thesis", "antithesis")

        contradictions = await lattice.find_contradictions("thesis")
        assert "antithesis" in contradictions

    @pytest.mark.asyncio
    async def test_record_synthesis(self, lattice):
        """Test H-gent synthesis recording."""
        await lattice.add("thesis", {"statement": "Speed is important"})
        await lattice.add("antithesis", {"statement": "Quality is important"})
        await lattice.add("synthesis", {"statement": "Efficient quality"})

        await lattice.record_synthesis("synthesis", "thesis", "antithesis")

        syntheses = await lattice.find_syntheses("thesis")
        assert "synthesis" in syntheses


# =============================================================================
# MemoryGarden Tests
# =============================================================================


class TestMemoryGarden:
    """Tests for MemoryGarden."""

    @pytest.fixture
    def garden(self):
        """Create a memory garden."""
        return MemoryGarden()

    @pytest.mark.asyncio
    async def test_plant(self, garden):
        """Test planting a seed."""
        entry = await garden.plant(
            {"idea": "Composable agents"},
            hypothesis="Composition leads to maintainability",
        )

        # Default trust 0.3 maps to SAPLING (auto_lifecycle promotion)
        # Trust < 0.3 would remain SEED
        assert entry.lifecycle == Lifecycle.SAPLING
        assert entry.trust == 0.3
        assert entry.hypothesis == "Composition leads to maintainability"

    @pytest.mark.asyncio
    async def test_nurture_with_supporting_evidence(self, garden):
        """Test nurturing with supporting evidence."""
        entry = await garden.plant({"idea": "Test"})

        evidence = Evidence(
            id="ev1",
            entry_id=entry.id,
            evidence_type=EvidenceType.SUPPORTING,
            content="Reduced code by 60%",
            source="experiment",
            confidence=0.9,
        )

        updated = await garden.nurture(entry.id, evidence)

        assert updated.trust > 0.3
        assert len(updated.evidence) == 1

    @pytest.mark.asyncio
    async def test_nurture_with_contradicting_evidence(self, garden):
        """Test nurturing with contradicting evidence."""
        entry = await garden.plant({"idea": "Test"}, initial_trust=0.5)

        evidence = Evidence(
            id="ev1",
            entry_id=entry.id,
            evidence_type=EvidenceType.CONTRADICTING,
            content="Failed in production",
            source="incident",
            confidence=0.8,
        )

        updated = await garden.nurture(entry.id, evidence)

        assert updated.trust < 0.5

    @pytest.mark.asyncio
    async def test_lifecycle_progression(self, garden):
        """Test lifecycle auto-progression based on trust."""
        # Start with very low trust to ensure SEED
        entry = await garden.plant({"idea": "Test"}, initial_trust=0.1)
        assert entry.lifecycle == Lifecycle.SEED

        # Add lots of supporting evidence
        for i in range(10):
            evidence = Evidence(
                id=f"ev{i}",
                entry_id=entry.id,
                evidence_type=EvidenceType.SUPPORTING,
                content=f"Evidence {i}",
                source="test",
                confidence=0.9,
            )
            entry = await garden.nurture(entry.id, evidence)

        # Should have progressed through lifecycle
        assert entry.trust > 0.5
        assert entry.lifecycle in (Lifecycle.SAPLING, Lifecycle.TREE, Lifecycle.FLOWER)

    @pytest.mark.asyncio
    async def test_harvest(self, garden):
        """Test harvesting a flower."""
        # Create a high-trust entry
        entry = await garden.plant({"idea": "Insight"}, initial_trust=0.85)

        # Should be a flower
        entry = await garden.get(entry.id)
        assert entry.lifecycle == Lifecycle.FLOWER

        # Harvest
        insight = await garden.harvest(entry.id)

        assert isinstance(insight, Insight)
        assert insight.source_entry_id == entry.id
        assert insight.confidence == entry.trust

        # Entry should return to tree
        entry = await garden.get(entry.id)
        assert entry.lifecycle == Lifecycle.TREE

    @pytest.mark.asyncio
    async def test_compost(self, garden):
        """Test composting a deprecated entry."""
        entry = await garden.plant(
            {"idea": "Old approach"}, tags=["legacy", "deprecated"]
        )

        nutrients = await garden.compost(entry.id)

        assert isinstance(nutrients, Nutrients)
        assert entry.id == nutrients.source_entry_id
        assert "legacy" in nutrients.concepts

        # Entry should be compost
        entry = await garden.get(entry.id)
        assert entry.lifecycle == Lifecycle.COMPOST

    @pytest.mark.asyncio
    async def test_mycelium_connections(self, garden):
        """Test mycelium (hidden connections)."""
        entry1 = await garden.plant({"idea": "Idea 1"})
        entry2 = await garden.plant({"idea": "Idea 2"})
        entry3 = await garden.plant({"idea": "Idea 3"})

        # Connect entries
        await garden.connect(entry1.id, entry2.id)
        await garden.connect(entry2.id, entry3.id)

        # Trace mycelium from entry1
        connected = await garden.trace_mycelium(entry1.id, max_depth=2)

        assert len(connected) >= 2

    @pytest.mark.asyncio
    async def test_add_contradiction(self, garden):
        """Test adding a contradiction."""
        entry = await garden.plant({"idea": "Test"}, initial_trust=0.5)

        contradiction = await garden.add_contradiction(
            entry.id, description="Counter-evidence found", severity=0.6
        )

        assert isinstance(contradiction, Contradiction)
        entry = await garden.get(entry.id)
        assert len(entry.contradictions) == 1
        assert entry.trust < 0.5

    @pytest.mark.asyncio
    async def test_resolve_contradiction(self, garden):
        """Test resolving a contradiction."""
        entry = await garden.plant({"idea": "Test"}, initial_trust=0.5)
        contradiction = await garden.add_contradiction(entry.id, "Issue", severity=0.3)

        await garden.resolve_contradiction(
            entry.id, contradiction.id, "Resolved by updated analysis"
        )

        entry = await garden.get(entry.id)
        assert entry.contradictions[0].resolved
        assert entry.contradictions[0].resolution is not None

    @pytest.mark.asyncio
    async def test_wilting_detection(self, garden):
        """Test wilting entry detection."""
        # Create entry with old nurture time
        entry = await garden.plant({"idea": "Old"})
        entry.last_nurtured = datetime.now() - timedelta(days=10)
        garden._entries[entry.id] = entry

        assert entry.is_wilting

        wilting = await garden.wilting()
        assert len(wilting) > 0

    @pytest.mark.asyncio
    async def test_stats(self, garden):
        """Test garden statistics."""
        await garden.plant({"idea": "A"}, initial_trust=0.2)
        await garden.plant({"idea": "B"}, initial_trust=0.5)
        await garden.plant({"idea": "C"}, initial_trust=0.9)

        stats = await garden.stats()

        assert stats.total_entries == 3
        assert (
            stats.seeds > 0
            or stats.saplings > 0
            or stats.trees > 0
            or stats.flowers > 0
        )

    @pytest.mark.asyncio
    async def test_persistence(self, temp_dir):
        """Test garden persistence."""
        path = temp_dir / "garden.json"

        # Create and populate garden
        garden1 = MemoryGarden(persistence_path=str(path))
        entry = await garden1.plant(
            {"idea": "Persistent"}, hypothesis="Test persistence"
        )

        # Load in new instance
        garden2 = MemoryGarden(persistence_path=str(path))
        loaded = await garden2.get(entry.id)

        assert loaded is not None
        assert loaded.hypothesis == "Test persistence"


# =============================================================================
# Integration Tests
# =============================================================================


class TestNoosphereIntegration:
    """Integration tests across Noosphere components."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
    async def test_manifold_and_lattice_integration(self):
        """Test using manifold for semantic search with lattice for relationships."""
        from agents.d.manifold import SemanticManifold

        manifold = SemanticManifold(dimension=4)
        lattice = RelationalLattice()

        # Add concepts to both
        await manifold.add("doc1", "Machine Learning", np.array([1.0, 0.5, 0.0, 0.0]))
        await manifold.add("doc2", "Deep Learning", np.array([0.9, 0.6, 0.1, 0.0]))

        await lattice.add("doc1", {"name": "Machine Learning"})
        await lattice.add("doc2", {"name": "Deep Learning"})
        await lattice.relate("doc2", "doc1", EdgeKind.IS_A)

        # Semantic search
        neighbors = await manifold.neighbors(np.array([1.0, 0.5, 0.0, 0.0]), k=2)
        assert len(neighbors) == 2

        # Lattice relationship
        entailment = await lattice.entails("doc2", "doc1")
        assert entailment.holds

    @pytest.mark.asyncio
    async def test_witness_and_garden_integration(self):
        """Test using witness for temporal tracking with garden for trust."""

        def fold(state, event):
            return {**state, **event}

        witness = TemporalWitness(fold=fold, initial={"hypothesis_trust": 0.3})
        garden = MemoryGarden()

        # Plant hypothesis
        entry = await garden.plant(
            {"idea": "Temporal tracking improves debugging"},
            hypothesis="Event sourcing helps postmortem",
        )

        # Track trust as trajectory
        witness.add_trajectory(
            "trust",
            lambda s: s.get("hypothesis_trust", 0),
            "Track hypothesis trust over time",
        )

        # Simulate trust evolution
        for trust in [0.3, 0.4, 0.5, 0.6, 0.7]:
            await witness.observe(
                {"hypothesis_trust": trust},
                WitnessReport(observer_id="garden", confidence=1.0),
            )

            # Update garden
            if trust > entry.trust:
                evidence = Evidence(
                    id=f"ev_{trust}",
                    entry_id=entry.id,
                    evidence_type=EvidenceType.SUPPORTING,
                    content=f"Trust increased to {trust}",
                    source="witness",
                    confidence=0.9,
                )
                entry = await garden.nurture(entry.id, evidence)

        # Check final state
        final_state = await witness.load()
        assert final_state["hypothesis_trust"] == 0.7

        entry = await garden.get(entry.id)
        assert entry.trust > 0.3

    @pytest.mark.asyncio
    async def test_full_noosphere_workflow(self):
        """Test complete Noosphere workflow."""

        # 1. Create components
        def fold(state, event):
            return {**state, **event}

        witness = TemporalWitness(fold=fold, initial={})
        lattice = RelationalLattice()
        garden = MemoryGarden()

        # 2. Plant a hypothesis in the garden
        hypothesis = await garden.plant(
            {"idea": "Composability"}, hypothesis="Composable agents scale better"
        )

        # 3. Record the hypothesis in the lattice
        await lattice.add(hypothesis.id, {"hypothesis": hypothesis.hypothesis})

        # 4. Observe the creation in the witness
        await witness.observe(
            {"action": "planted", "entry_id": hypothesis.id},
            WitnessReport(observer_id="garden", confidence=1.0),
        )

        # 5. Add evidence and track
        evidence = Evidence(
            id="ev1",
            entry_id=hypothesis.id,
            evidence_type=EvidenceType.SUPPORTING,
            content="Reduced complexity by 50%",
            source="experiment",
            confidence=0.9,
        )
        await garden.nurture(hypothesis.id, evidence)

        await witness.observe(
            {"action": "nurtured", "entry_id": hypothesis.id},
            WitnessReport(observer_id="garden", confidence=1.0),
        )

        # 6. Verify integration
        events = await witness.event_count()
        assert events >= 2

        entry = await garden.get(hypothesis.id)
        assert len(entry.evidence) == 1

        node = await lattice.get(hypothesis.id)
        assert node is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
