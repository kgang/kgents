"""
Tests for Semantic Stigmergic Field.

Phase 2 of Cross-Pollination: Agents coordinate via environmental signals.

Tests:
- Pheromone emission and decay
- Sensing by radius and kind
- Psi × F decoupled integration
- Safety and economic signals
"""

from typing import Any

import pytest

from agents.i.semantic_field import (
    FieldCoordinate,
    IntentPayload,
    MetaphorPayload,
    OpportunityPayload,
    SemanticPheromone,
    SemanticPheromoneKind,
    WarningPayload,
    # Phase 3 imports (Infrastructure Agents)
    create_data_emitter,
    create_data_sensor,
    create_economic_emitter,
    # Phase 1 imports
    create_evolution_emitter,
    # Phase 2 imports (Supporting Sensors)
    create_evolution_sensor,
    create_forge_sensor,
    create_hegel_emitter,
    create_hegel_sensor,
    create_memory_emitter,
    create_memory_sensor,
    create_narrative_emitter,
    create_narrative_sensor,
    create_observer_sensor,
    create_persona_emitter,
    create_persona_sensor,
    create_psi_emitter,
    create_refinery_emitter,
    create_refinery_sensor,
    create_safety_emitter,
    create_semantic_field,
    create_test_emitter,
    create_test_sensor,
    create_wire_emitter,
    create_wire_sensor,
)


class TestFieldCoordinate:
    """Tests for FieldCoordinate."""

    def test_embedding_distance(self) -> None:
        """Test distance in embedding space."""
        c1 = FieldCoordinate(embedding=(0.0, 0.0, 0.0))
        c2 = FieldCoordinate(embedding=(3.0, 4.0, 0.0))

        # 3-4-5 triangle
        assert c1.distance_to(c2) == pytest.approx(5.0)

    def test_embedding_distance_mismatched_dims(self) -> None:
        """Test distance returns inf for mismatched dimensions."""
        c1 = FieldCoordinate(embedding=(0.0, 0.0))
        c2 = FieldCoordinate(embedding=(1.0, 1.0, 1.0))

        assert c1.distance_to(c2) == float("inf")

    def test_domain_distance_same(self) -> None:
        """Test domain distance for same domain."""
        c1 = FieldCoordinate(domain="software")
        c2 = FieldCoordinate(domain="software")

        assert c1.distance_to(c2) == 0.0

    def test_domain_distance_different(self) -> None:
        """Test domain distance for different domains."""
        c1 = FieldCoordinate(domain="software")
        c2 = FieldCoordinate(domain="biology")

        assert c1.distance_to(c2) == 1.0

    def test_tag_distance(self) -> None:
        """Test tag-based distance."""
        c1 = FieldCoordinate(tags=("python", "async", "api"))
        c2 = FieldCoordinate(tags=("python", "sync", "cli"))

        # Jaccard: 1 common / 5 total = 0.2, distance = 0.8
        assert c1.distance_to(c2) == pytest.approx(0.8)

    def test_tag_distance_identical(self) -> None:
        """Test tag distance for identical tags."""
        c1 = FieldCoordinate(tags=("a", "b", "c"))
        c2 = FieldCoordinate(tags=("a", "b", "c"))

        assert c1.distance_to(c2) == 0.0

    def test_default_distance(self) -> None:
        """Test default distance when no coords available."""
        c1 = FieldCoordinate()
        c2 = FieldCoordinate()

        assert c1.distance_to(c2) == 1.0


class TestSemanticPheromone:
    """Tests for SemanticPheromone."""

    def test_pheromone_creation(self) -> None:
        """Test basic pheromone creation."""
        payload = MetaphorPayload(
            source_domain="database",
            target_domain="graph",
            confidence=0.8,
        )
        pheromone: SemanticPheromone[MetaphorPayload] = SemanticPheromone(
            id="test-1",
            emitter="psi",
            kind=SemanticPheromoneKind.METAPHOR,
            payload=payload,
            intensity=0.8,
            position=FieldCoordinate(domain="software"),
        )

        assert pheromone.id == "test-1"
        assert pheromone.emitter == "psi"
        assert pheromone.kind == SemanticPheromoneKind.METAPHOR
        assert pheromone.intensity == 0.8
        assert pheromone.is_active

    def test_pheromone_decay(self) -> None:
        """Test pheromone decay over time."""
        pheromone: SemanticPheromone[dict[str, Any]] = SemanticPheromone(
            id="test-1",
            emitter="psi",
            kind=SemanticPheromoneKind.METAPHOR,
            payload={},
            intensity=1.0,
            position=FieldCoordinate(),
        )

        # Decay
        new_intensity: float = pheromone.decay(1.0)
        assert new_intensity < 1.0
        assert pheromone.intensity == new_intensity

    def test_pheromone_expires(self) -> None:
        """Test pheromone expiration after many decays."""
        pheromone: SemanticPheromone[dict[str, Any]] = SemanticPheromone(
            id="test-1",
            emitter="psi",
            kind=SemanticPheromoneKind.WARNING,  # Fast decay
            payload={},
            intensity=0.5,
            position=FieldCoordinate(),
        )

        # Many decays should bring intensity below threshold
        for _ in range(100):
            pheromone.decay(1.0)

        assert not pheromone.is_active


class TestSemanticField:
    """Tests for SemanticField."""

    def test_field_creation(self) -> None:
        """Test field creation."""
        field = create_semantic_field()
        assert field.pheromone_count == 0
        assert field.current_tick == 0

    def test_emit_and_count(self) -> None:
        """Test emitting pheromones."""
        field = create_semantic_field()

        phero_id = field.emit(
            emitter="psi",
            kind=SemanticPheromoneKind.METAPHOR,
            payload={"test": "data"},
            position=FieldCoordinate(domain="software"),
        )

        assert phero_id.startswith("phero-")
        assert field.pheromone_count == 1

    def test_sense_by_kind(self) -> None:
        """Test sensing pheromones by kind."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="software")

        # Emit different kinds
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, position)
        field.emit("forge", SemanticPheromoneKind.INTENT, {}, position)
        field.emit("judge", SemanticPheromoneKind.WARNING, {}, position)

        # Sense only metaphors
        metaphors = field.sense(position, kind=SemanticPheromoneKind.METAPHOR)
        assert len(metaphors) == 1
        assert metaphors[0].kind == SemanticPheromoneKind.METAPHOR

    def test_sense_by_radius(self) -> None:
        """Test sensing by radius."""
        field = create_semantic_field()

        # Emit at different positions
        field.emit(
            "psi",
            SemanticPheromoneKind.METAPHOR,
            {},
            FieldCoordinate(embedding=(0.0, 0.0)),
        )
        field.emit(
            "psi",
            SemanticPheromoneKind.METAPHOR,
            {},
            FieldCoordinate(embedding=(0.1, 0.1)),
        )
        field.emit(
            "psi",
            SemanticPheromoneKind.METAPHOR,
            {},
            FieldCoordinate(embedding=(10.0, 10.0)),  # Far away
        )

        # Sense from origin with small radius
        results = field.sense(
            FieldCoordinate(embedding=(0.0, 0.0)),
            radius=0.5,
            kind=SemanticPheromoneKind.METAPHOR,
        )

        assert len(results) == 2  # Only nearby ones

    def test_sense_sorted_by_intensity(self) -> None:
        """Test sensing returns results sorted by intensity."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="software")

        # Emit with different intensities
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, position, intensity=0.3)
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, position, intensity=0.9)
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, position, intensity=0.5)

        results = field.sense(position, kind=SemanticPheromoneKind.METAPHOR)

        assert len(results) == 3
        assert results[0].intensity == 0.9
        assert results[1].intensity == 0.5
        assert results[2].intensity == 0.3

    def test_sense_strongest(self) -> None:
        """Test sensing strongest pheromone."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="software")

        field.emit(
            "psi",
            SemanticPheromoneKind.METAPHOR,
            {"id": "weak"},
            position,
            intensity=0.3,
        )
        field.emit(
            "psi",
            SemanticPheromoneKind.METAPHOR,
            {"id": "strong"},
            position,
            intensity=0.9,
        )

        strongest = field.sense_strongest(position, SemanticPheromoneKind.METAPHOR)

        assert strongest is not None
        assert strongest.payload["id"] == "strong"

    def test_tick_decay(self) -> None:
        """Test tick advances time and decays pheromones."""
        field = create_semantic_field()

        # Emit a low-intensity pheromone with fast decay
        field.emit(
            "judge",
            SemanticPheromoneKind.WARNING,
            {},
            FieldCoordinate(),
            intensity=0.05,  # Very low
        )

        assert field.pheromone_count == 1

        # Many ticks should expire it
        for _ in range(50):
            field.tick(1.0)

        assert field.pheromone_count == 0

    def test_clear(self) -> None:
        """Test clearing the field."""
        field = create_semantic_field()

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())

        assert field.pheromone_count == 2

        count = field.clear()
        assert count == 2
        assert field.pheromone_count == 0

    def test_get_all(self) -> None:
        """Test getting all pheromones."""
        field = create_semantic_field()

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())
        field.emit("forge", SemanticPheromoneKind.INTENT, {}, FieldCoordinate())

        all_pheromones = field.get_all()
        assert len(all_pheromones) == 2

        metaphors_only = field.get_all(SemanticPheromoneKind.METAPHOR)
        assert len(metaphors_only) == 1

    def test_deposit_callback(self) -> None:
        """Test deposit callback is called."""
        field = create_semantic_field()
        deposits = []

        field.on_deposit(lambda p: deposits.append(p))

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())

        assert len(deposits) == 1
        assert deposits[0].emitter == "psi"


class TestPsiFieldEmitter:
    """Tests for PsiFieldEmitter."""

    def test_emit_metaphor(self) -> None:
        """Test emitting a metaphor."""
        field = create_semantic_field()
        emitter = create_psi_emitter(field)

        emitter.emit_metaphor(
            source_domain="database",
            target_domain="graph",
            confidence=0.85,
            position=FieldCoordinate(domain="software"),
            object_map={"table": "node", "foreign_key": "edge"},
            description="Database as graph",
        )

        assert field.pheromone_count == 1

        pheromones = field.get_all(SemanticPheromoneKind.METAPHOR)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, MetaphorPayload)
        assert payload.source_domain == "database"
        assert payload.target_domain == "graph"
        assert payload.confidence == 0.85


class TestForgeFieldSensor:
    """Tests for ForgeFieldSensor."""

    def test_sense_metaphors(self) -> None:
        """Test sensing metaphors."""
        field = create_semantic_field()
        emitter = create_psi_emitter(field)
        sensor = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        # Emit some metaphors
        emitter.emit_metaphor(
            source_domain="api",
            target_domain="contract",
            confidence=0.7,
            position=position,
        )
        emitter.emit_metaphor(
            source_domain="cache",
            target_domain="memory",
            confidence=0.9,
            position=position,
        )

        # Sense them
        metaphors = sensor.sense_metaphors(position)

        assert len(metaphors) == 2
        # Should be sorted by intensity (confidence)
        assert metaphors[0].confidence == 0.9
        assert metaphors[1].confidence == 0.7

    def test_get_strongest_metaphor(self) -> None:
        """Test getting strongest metaphor."""
        field = create_semantic_field()
        emitter = create_psi_emitter(field)
        sensor = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        emitter.emit_metaphor("api", "contract", 0.5, position)
        emitter.emit_metaphor("cache", "memory", 0.95, position)

        strongest = sensor.get_strongest_metaphor(position)

        assert strongest is not None
        assert strongest.target_domain == "memory"

    def test_emit_intent(self) -> None:
        """Test emitting intent from F-gent."""
        field = create_semantic_field()
        sensor = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        sensor.emit_intent(
            purpose="Create API client",
            position=position,
            behaviors=("fetch", "parse"),
            constraints=("timeout < 5s",),
        )

        assert field.pheromone_count == 1

        pheromones = field.get_all(SemanticPheromoneKind.INTENT)
        payload = pheromones[0].payload

        assert isinstance(payload, IntentPayload)
        assert payload.purpose == "Create API client"


class TestPsiForgeIntegration:
    """
    Integration tests for Psi × F decoupled coordination.

    The key insight: Psi and F never know about each other.
    They coordinate through the shared field.
    """

    def test_psi_emits_forge_senses(self) -> None:
        """Test Psi emitting metaphor, F sensing it."""
        field = create_semantic_field()
        psi_emitter = create_psi_emitter(field)
        forge_sensor = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        # Psi discovers a metaphor (doesn't know about F)
        psi_emitter.emit_metaphor(
            source_domain="query_optimization",
            target_domain="topological_sort",
            confidence=0.88,
            position=position,
            object_map={"table": "node", "join": "edge"},
            description="Query ordering is topological sorting",
            transferable_operations=("kahns_algorithm",),
        )

        # F senses the environment (doesn't know about Psi)
        metaphors = forge_sensor.sense_metaphors(position)

        assert len(metaphors) == 1
        assert metaphors[0].target_domain == "topological_sort"
        assert metaphors[0].transferable_operations == ("kahns_algorithm",)

    def test_multiple_metaphors_strongest_wins(self) -> None:
        """Test that F-gent can select strongest metaphor."""
        field = create_semantic_field()
        psi = create_psi_emitter(field)
        forge = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        # Multiple metaphors emitted
        psi.emit_metaphor("problem", "plumbing", 0.3, position)
        psi.emit_metaphor("problem", "architecture", 0.7, position)
        psi.emit_metaphor("problem", "gardening", 0.5, position)

        # F-gent uses strongest
        best = forge.get_strongest_metaphor(position)

        assert best is not None
        assert best.target_domain == "architecture"

    def test_metaphor_decay_affects_sensing(self) -> None:
        """Test that metaphor decay affects what F senses."""
        field = create_semantic_field()
        psi = create_psi_emitter(field)
        forge = create_forge_sensor(field)

        position = FieldCoordinate(domain="software")

        # Emit low-confidence metaphor
        psi.emit_metaphor("problem", "weak_metaphor", 0.05, position)

        # Initially sensed
        assert len(forge.sense_metaphors(position)) == 1

        # Many ticks of decay
        for _ in range(100):
            field.tick(1.0)

        # Now gone
        assert len(forge.sense_metaphors(position)) == 0


class TestSafetyFieldEmitter:
    """Tests for SafetyFieldEmitter."""

    def test_emit_warning(self) -> None:
        """Test emitting a safety warning."""
        field = create_semantic_field()
        emitter = create_safety_emitter(field)

        position = FieldCoordinate(domain="software")

        emitter.emit_warning(
            severity="error",
            message="Hallucination risk detected",
            position=position,
            affected_agents=("psi", "forge"),
            trigger="Low reality grounding",
            recommendation="Reduce entropy",
        )

        pheromones = field.get_all(SemanticPheromoneKind.WARNING)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, WarningPayload)
        assert payload.severity == "error"
        assert "psi" in payload.affected_agents

    def test_warning_intensity_by_severity(self) -> None:
        """Test warning intensity varies by severity."""
        field = create_semantic_field()
        emitter = create_safety_emitter(field)

        position = FieldCoordinate()

        emitter.emit_warning("info", "Low priority", position)
        emitter.emit_warning("critical", "High priority", position)

        pheromones = field.get_all(SemanticPheromoneKind.WARNING)

        # Sort by intensity to find critical
        pheromones.sort(key=lambda p: p.intensity, reverse=True)

        assert pheromones[0].intensity == 1.0  # Critical
        assert pheromones[1].intensity == 0.3  # Info


class TestEconomicFieldEmitter:
    """Tests for EconomicFieldEmitter."""

    def test_emit_opportunity(self) -> None:
        """Test emitting an economic opportunity."""
        field = create_semantic_field()
        emitter = create_economic_emitter(field)

        position = FieldCoordinate(domain="software")

        emitter.emit_opportunity(
            signal_type="surplus",
            value=50.0,
            resource="tokens",
            position=position,
            expires_in_ticks=10,
        )

        pheromones = field.get_all(SemanticPheromoneKind.OPPORTUNITY)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, OpportunityPayload)
        assert payload.signal_type == "surplus"
        assert payload.value == 50.0

    def test_emit_scarcity(self) -> None:
        """Test emitting a scarcity signal."""
        field = create_semantic_field()
        emitter = create_economic_emitter(field)

        position = FieldCoordinate()

        emitter.emit_scarcity(
            resource="compute",
            severity=0.8,
            position=position,
        )

        pheromones = field.get_all(SemanticPheromoneKind.SCARCITY)
        assert len(pheromones) == 1
        assert pheromones[0].intensity == 0.8


class TestMemoryFieldEmitterSensor:
    """Tests for MemoryFieldEmitter and MemoryFieldSensor."""

    def test_emit_consolidation(self) -> None:
        """Test emitting a memory consolidation signal."""
        field = create_semantic_field()
        emitter = create_memory_emitter(field)

        position = FieldCoordinate(domain="conversation")

        emitter.emit_consolidation(
            memory_id="mem_001",
            importance=0.8,
            position=position,
            decay_urgency=0.6,
            context_tags=("user_preference", "topic:weather"),
            summary="User prefers detailed explanations",
        )

        pheromones = field.get_all(SemanticPheromoneKind.MEMORY)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.memory_id == "mem_001"
        assert payload.importance == 0.8
        assert "user_preference" in payload.context_tags

    def test_sense_memories_by_importance(self) -> None:
        """Test sensing memories with importance threshold."""
        field = create_semantic_field()
        emitter = create_memory_emitter(field)
        sensor = create_memory_sensor(field)

        position = FieldCoordinate(domain="conversation")

        # Emit two memories with different importance
        emitter.emit_consolidation("mem_high", 0.9, position)
        emitter.emit_consolidation("mem_low", 0.3, position)

        # Sense all
        all_memories = sensor.sense_memories(position)
        assert len(all_memories) == 2

        # Sense only high importance
        high_memories = sensor.sense_memories(position, min_importance=0.5)
        assert len(high_memories) == 1
        assert high_memories[0].memory_id == "mem_high"


class TestNarrativeFieldEmitterSensor:
    """Tests for NarrativeFieldEmitter and NarrativeFieldSensor."""

    def test_emit_story_event(self) -> None:
        """Test emitting a narrative event."""
        field = create_semantic_field()
        emitter = create_narrative_emitter(field)

        position = FieldCoordinate(domain="session")

        emitter.emit_story_event(
            thread_id="session_story",
            event_type="beginning",
            summary="User starts a new coding project",
            position=position,
            actors=("user", "claude"),
            emotional_valence=0.7,
        )

        pheromones = field.get_all(SemanticPheromoneKind.NARRATIVE)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.thread_id == "session_story"
        assert payload.event_type == "beginning"
        assert "user" in payload.actors

    def test_climax_has_highest_intensity(self) -> None:
        """Test climax events have highest intensity."""
        field = create_semantic_field()
        emitter = create_narrative_emitter(field)

        position = FieldCoordinate()

        emitter.emit_story_event("t1", "beginning", "Start", position)
        emitter.emit_story_event("t1", "climax", "Peak", position)
        emitter.emit_story_event("t1", "resolution", "End", position)

        pheromones = field.get_all(SemanticPheromoneKind.NARRATIVE)

        intensities = {p.payload.event_type: p.intensity for p in pheromones}
        assert intensities["climax"] == 1.0
        assert intensities["beginning"] < intensities["climax"]

    def test_sense_narratives_by_thread(self) -> None:
        """Test filtering narratives by thread ID."""
        field = create_semantic_field()
        emitter = create_narrative_emitter(field)
        sensor = create_narrative_sensor(field)

        # Use domain-based coordinate to ensure distance=0
        position = FieldCoordinate(domain="session")

        emitter.emit_story_event("thread_a", "beginning", "A starts", position)
        emitter.emit_story_event("thread_b", "beginning", "B starts", position)

        thread_a = sensor.sense_narratives(position, thread_id="thread_a")
        assert len(thread_a) == 1
        assert thread_a[0].thread_id == "thread_a"


class TestObserverFieldSensor:
    """Tests for ObserverFieldSensor."""

    def test_observe_all_kinds(self) -> None:
        """Test observer can see all pheromone types."""
        field = create_semantic_field()
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # Emit different pheromone types
        create_psi_emitter(field).emit_metaphor("source", "target", 0.8, position)
        create_safety_emitter(field).emit_warning("info", "test", position)
        create_memory_emitter(field).emit_consolidation("m1", 0.5, position)

        observed = observer.observe_all(position)

        assert SemanticPheromoneKind.METAPHOR.value in observed
        assert SemanticPheromoneKind.WARNING.value in observed
        assert SemanticPheromoneKind.MEMORY.value in observed

    def test_observe_warnings_by_severity(self) -> None:
        """Test filtering warnings by severity."""
        field = create_semantic_field()
        observer = create_observer_sensor(field)
        safety = create_safety_emitter(field)
        position = FieldCoordinate()

        safety.emit_warning("info", "low priority", position)
        safety.emit_warning("error", "high priority", position)

        # Get only error+ warnings
        warnings = observer.observe_warnings(position, min_severity="error")
        assert len(warnings) == 1
        assert warnings[0].severity == "error"

    def test_field_summary(self) -> None:
        """Test field summary counts pheromones by type."""
        field = create_semantic_field()
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # Emit various pheromones
        create_psi_emitter(field).emit_metaphor("src_a", "tgt_a", 0.8, position)
        create_psi_emitter(field).emit_metaphor("src_b", "tgt_b", 0.7, position)
        create_safety_emitter(field).emit_warning("info", "test", position)

        summary = observer.field_summary()

        assert summary[SemanticPheromoneKind.METAPHOR.value] == 2
        assert summary[SemanticPheromoneKind.WARNING.value] == 1


class TestPheromoneKindProperties:
    """Tests for SemanticPheromoneKind properties."""

    def test_all_kinds_have_decay_rate(self) -> None:
        """Test all kinds have a decay rate."""
        for kind in SemanticPheromoneKind:
            assert 0.0 < kind.decay_rate <= 1.0

    def test_all_kinds_have_default_radius(self) -> None:
        """Test all kinds have a default radius."""
        for kind in SemanticPheromoneKind:
            assert kind.default_radius > 0

    def test_warning_decays_fast(self) -> None:
        """Warnings should decay faster than metaphors."""
        assert SemanticPheromoneKind.WARNING.decay_rate > SemanticPheromoneKind.METAPHOR.decay_rate

    def test_warning_has_wide_radius(self) -> None:
        """Warnings should broadcast widely."""
        assert SemanticPheromoneKind.WARNING.default_radius >= 1.0

    def test_phase1_kinds_have_properties(self) -> None:
        """Test Phase 1 pheromone kinds have decay and radius."""
        phase1_kinds = [
            SemanticPheromoneKind.MUTATION,
            SemanticPheromoneKind.SYNTHESIS,
            SemanticPheromoneKind.PRIOR,
            SemanticPheromoneKind.REFINEMENT,
        ]
        for kind in phase1_kinds:
            assert 0.0 < kind.decay_rate <= 1.0
            assert kind.default_radius > 0

    def test_prior_decays_slowly(self) -> None:
        """Priors should decay slowly (persona is stable)."""
        assert SemanticPheromoneKind.PRIOR.decay_rate < SemanticPheromoneKind.MUTATION.decay_rate

    def test_prior_has_wide_radius(self) -> None:
        """Priors should broadcast widely to affect all agents."""
        assert SemanticPheromoneKind.PRIOR.default_radius >= 1.0


# =============================================================================
# Phase 1: E-gent Evolution Field Emitter Tests
# =============================================================================


class TestEvolutionFieldEmitter:
    """Tests for E-gent EvolutionFieldEmitter (MUTATION signals)."""

    def test_emit_mutation(self) -> None:
        """Test emitting a mutation signal."""
        field = create_semantic_field()
        emitter = create_evolution_emitter(field)
        position = FieldCoordinate(domain="evolution")

        phero_id = emitter.emit_mutation(
            mutation_id="mut_001",
            fitness_delta=0.3,
            generation=5,
            position=position,
            parent_id="mut_000",
            mutation_type="point",
            schema_signature="AddFunction",
            gibbs_energy=-0.5,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.MUTATION)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.mutation_id == "mut_001"
        assert payload.fitness_delta == 0.3
        assert payload.generation == 5
        assert payload.parent_id == "mut_000"
        assert payload.mutation_type == "point"
        assert payload.gibbs_energy == -0.5

    def test_mutation_intensity_scales_with_fitness(self) -> None:
        """Higher fitness delta should produce higher intensity."""
        field = create_semantic_field()
        emitter = create_evolution_emitter(field)
        position = FieldCoordinate()

        # Low fitness delta
        emitter.emit_mutation("mut_low", -0.2, 1, position)
        # High fitness delta
        emitter.emit_mutation("mut_high", 0.4, 1, position)

        pheromones = field.get_all(SemanticPheromoneKind.MUTATION)
        intensities = sorted([p.intensity for p in pheromones])

        # Higher fitness delta should have higher intensity
        assert intensities[0] < intensities[1]

    def test_emit_fitness_change(self) -> None:
        """Test emitting a fitness change signal."""
        field = create_semantic_field()
        emitter = create_evolution_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_fitness_change(
            entity_id="agent_001",
            old_fitness=0.5,
            new_fitness=0.8,
            position=position,
            reason="optimization",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.MUTATION)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.entity_id == "agent_001"
        assert payload.old_fitness == 0.5
        assert payload.new_fitness == 0.8

    def test_emit_cycle_complete(self) -> None:
        """Test emitting cycle completion signal."""
        field = create_semantic_field()
        emitter = create_evolution_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_cycle_complete(
            generation=10,
            best_fitness=0.95,
            population_size=100,
            position=position,
            mutations_succeeded=8,
            mutations_failed=2,
            temperature=0.8,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.MUTATION)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.generation == 10
        assert payload.best_fitness == 0.95
        assert payload.population_size == 100
        assert payload.mutations_succeeded == 8
        assert payload.mutations_failed == 2


# =============================================================================
# Phase 1: H-gent Hegel Field Emitter Tests
# =============================================================================


class TestHegelFieldEmitter:
    """Tests for H-gent HegelFieldEmitter (SYNTHESIS signals)."""

    def test_emit_synthesis(self) -> None:
        """Test emitting a synthesis signal."""
        field = create_semantic_field()
        emitter = create_hegel_emitter(field)
        position = FieldCoordinate(domain="philosophy")

        phero_id = emitter.emit_synthesis(
            thesis="Individual freedom",
            antithesis="Social order",
            synthesis="Liberal democracy",
            confidence=0.85,
            position=position,
            domain="political_theory",
            resolution_type="elevate",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.thesis == "Individual freedom"
        assert payload.antithesis == "Social order"
        assert payload.synthesis == "Liberal democracy"
        assert payload.confidence == 0.85
        assert payload.resolution_type == "elevate"

    def test_synthesis_intensity_matches_confidence(self) -> None:
        """Synthesis intensity should match confidence."""
        field = create_semantic_field()
        emitter = create_hegel_emitter(field)
        position = FieldCoordinate()

        emitter.emit_synthesis("A", "B", "C", 0.9, position)

        pheromones = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        assert pheromones[0].intensity == 0.9

    def test_emit_contradiction(self) -> None:
        """Test emitting a contradiction signal."""
        field = create_semantic_field()
        emitter = create_hegel_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_contradiction(
            statement_a="X is true",
            statement_b="X is false",
            severity=0.8,
            position=position,
            tension_mode="logical",
            description="Direct contradiction detected",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.statement_a == "X is true"
        assert payload.statement_b == "X is false"
        assert payload.severity == 0.8
        assert payload.tension_mode == "logical"

    def test_emit_productive_tension(self) -> None:
        """Test emitting productive tension signal."""
        field = create_semantic_field()
        emitter = create_hegel_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_productive_tension(
            thesis="Speed",
            antithesis="Accuracy",
            why_held="Trade-off depends on context",
            position=position,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        assert len(pheromones) == 1
        assert pheromones[0].metadata.get("signal_type") == "productive_tension"


# =============================================================================
# Phase 1: K-gent Persona Field Emitter Tests
# =============================================================================


class TestPersonaFieldEmitter:
    """Tests for K-gent PersonaFieldEmitter (PRIOR signals)."""

    def test_emit_prior_change(self) -> None:
        """Test emitting a prior change signal."""
        field = create_semantic_field()
        emitter = create_persona_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_prior_change(
            prior_type="risk_tolerance",
            value=0.7,
            persona_id="kent",
            position=position,
            reason="User expressed preference for bold choices",
            confidence=0.9,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.PRIOR)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.prior_type == "risk_tolerance"
        assert payload.value == 0.7
        assert payload.persona_id == "kent"
        assert payload.confidence == 0.9

    def test_prior_intensity_matches_confidence(self) -> None:
        """Prior intensity should match confidence."""
        field = create_semantic_field()
        emitter = create_persona_emitter(field)
        position = FieldCoordinate()

        emitter.emit_prior_change("creativity", 0.8, "kent", position, confidence=0.75)

        pheromones = field.get_all(SemanticPheromoneKind.PRIOR)
        assert pheromones[0].intensity == 0.75

    def test_emit_persona_shift(self) -> None:
        """Test emitting a persona shift signal."""
        field = create_semantic_field()
        emitter = create_persona_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_persona_shift(
            old_persona="researcher",
            new_persona="creator",
            position=position,
            trigger="Project phase change",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.PRIOR)
        assert len(pheromones) == 1
        # Persona shifts have high intensity
        assert pheromones[0].intensity == 1.0

        payload = pheromones[0].payload
        assert payload.old_persona == "researcher"
        assert payload.new_persona == "creator"

    def test_emit_preference(self) -> None:
        """Test emitting a general preference signal."""
        field = create_semantic_field()
        emitter = create_persona_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_preference(
            category="communication",
            preference="concise",
            strength=0.85,
            position=position,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.PRIOR)
        assert len(pheromones) == 1
        assert pheromones[0].intensity == 0.85


# =============================================================================
# Phase 1: R-gent Refinery Field Emitter Tests
# =============================================================================


class TestRefineryFieldEmitter:
    """Tests for R-gent RefineryFieldEmitter (REFINEMENT signals)."""

    def test_emit_refinement(self) -> None:
        """Test emitting a refinement signal."""
        field = create_semantic_field()
        emitter = create_refinery_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_refinement(
            target_id="agent_summarizer",
            improvement_type="optimization",
            improvement_ratio=1.3,
            position=position,
            before_metrics={"score": 0.7, "cost": 100},
            after_metrics={"score": 0.91, "cost": 80},
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.REFINEMENT)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.target_id == "agent_summarizer"
        assert payload.improvement_type == "optimization"
        assert payload.improvement_ratio == 1.3
        assert payload.before_metrics["score"] == 0.7
        assert payload.after_metrics["score"] == 0.91

    def test_refinement_intensity_scales_with_improvement(self) -> None:
        """Higher improvement ratio should produce higher intensity."""
        field = create_semantic_field()
        emitter = create_refinery_emitter(field)
        position = FieldCoordinate()

        # Small improvement
        emitter.emit_refinement("target_a", "optimization", 1.1, position)
        # Large improvement
        emitter.emit_refinement("target_b", "optimization", 1.5, position)

        pheromones = field.get_all(SemanticPheromoneKind.REFINEMENT)
        intensities = sorted([p.intensity for p in pheromones])

        # Higher improvement should have higher intensity
        assert intensities[0] < intensities[1]

    def test_emit_opportunity(self) -> None:
        """Test emitting a refinement opportunity signal."""
        field = create_semantic_field()
        emitter = create_refinery_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_opportunity(
            target_id="agent_classifier",
            potential_improvement=1.4,
            strategy="mipro_v2",
            position=position,
            cost_estimate=5.0,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.REFINEMENT)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.target_id == "agent_classifier"
        assert payload.potential_improvement == 1.4
        assert payload.strategy == "mipro_v2"
        assert payload.cost_estimate == 5.0

    def test_emit_optimization_trace(self) -> None:
        """Test emitting optimization trace signal."""
        field = create_semantic_field()
        emitter = create_refinery_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_optimization_trace(
            target_id="agent_qa",
            method="textgrad",
            iterations=15,
            final_score=0.88,
            position=position,
            converged=True,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.REFINEMENT)
        assert len(pheromones) == 1
        assert pheromones[0].metadata.get("signal_type") == "optimization_trace"


# =============================================================================
# Phase 1 Integration Tests
# =============================================================================


class TestPhase1Integration:
    """Integration tests for Phase 1 emitters working together."""

    def test_evolution_and_refinement_coordination(self) -> None:
        """Test E-gent and R-gent can coordinate via field."""
        field = create_semantic_field()
        evolution = create_evolution_emitter(field)
        refinery = create_refinery_emitter(field)
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # E-gent discovers a mutation
        evolution.emit_mutation("mut_001", 0.25, 1, position, mutation_type="point")

        # R-gent identifies refinement opportunity
        refinery.emit_opportunity("mut_001", 1.3, "bootstrap_fewshot", position)

        # Observer can see both signals
        observed = observer.observe_all(position)

        assert SemanticPheromoneKind.MUTATION.value in observed
        assert SemanticPheromoneKind.REFINEMENT.value in observed

    def test_persona_affects_all_agents(self) -> None:
        """Test K-gent priors are visible to observer."""
        field = create_semantic_field()
        persona = create_persona_emitter(field)
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # K-gent broadcasts a preference
        persona.emit_prior_change(
            "verbosity", 0.3, "kent", position, reason="User prefers concise output"
        )

        # Observer can see the prior
        observed = observer.observe_all(position)
        assert SemanticPheromoneKind.PRIOR.value in observed

        # Prior has wide radius so it reaches everywhere
        priors = observed[SemanticPheromoneKind.PRIOR.value]
        assert len(priors) == 1

    def test_hegel_synthesis_visible_to_psi(self) -> None:
        """Test H-gent synthesis can be observed by other agents."""
        field = create_semantic_field()
        hegel = create_hegel_emitter(field)
        psi = create_psi_emitter(field)
        position = FieldCoordinate()

        # H-gent achieves a synthesis
        hegel.emit_synthesis("Efficiency", "Reliability", "Robust efficiency", 0.85, position)

        # Psi-gent (metaphor solver) emits a related metaphor
        psi.emit_metaphor("robust_efficiency", "bridge_engineering", 0.75, position)

        # Both signals coexist in the field
        synthesis_signals = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        metaphor_signals = field.get_all(SemanticPheromoneKind.METAPHOR)

        assert len(synthesis_signals) == 1
        assert len(metaphor_signals) == 1

    def test_field_summary_includes_phase1(self) -> None:
        """Test field summary counts Phase 1 pheromones."""
        field = create_semantic_field()
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # Emit one of each Phase 1 type
        create_evolution_emitter(field).emit_mutation("m1", 0.2, 1, position)
        create_hegel_emitter(field).emit_synthesis("A", "B", "C", 0.8, position)
        create_persona_emitter(field).emit_prior_change("x", 0.5, "k", position)
        create_refinery_emitter(field).emit_refinement("t", "opt", 1.2, position)

        summary = observer.field_summary()

        assert summary[SemanticPheromoneKind.MUTATION.value] == 1
        assert summary[SemanticPheromoneKind.SYNTHESIS.value] == 1
        assert summary[SemanticPheromoneKind.PRIOR.value] == 1
        assert summary[SemanticPheromoneKind.REFINEMENT.value] == 1


# =============================================================================
# Phase 2: Supporting Sensors Tests
# =============================================================================


class TestEvolutionFieldSensor:
    """Tests for E-gent EvolutionFieldSensor (senses REFINEMENT)."""

    def test_sense_refinements(self) -> None:
        """Test sensing refinement signals."""
        field = create_semantic_field()
        refinery_emitter = create_refinery_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        # R-gent emits refinement
        refinery_emitter.emit_refinement(
            "target_001",
            "optimization",
            1.3,
            position,
            before_metrics={"score": 0.7},
            after_metrics={"score": 0.91},
        )

        # E-gent senses it
        refinements = evolution_sensor.sense_refinements(position)

        assert len(refinements) == 1
        assert refinements[0].target_id == "target_001"
        assert refinements[0].improvement_ratio == 1.3

    def test_sense_opportunities(self) -> None:
        """Test sensing refinement opportunity signals."""
        field = create_semantic_field()
        refinery_emitter = create_refinery_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        # R-gent emits opportunity
        refinery_emitter.emit_opportunity(
            "target_002",
            potential_improvement=1.5,
            strategy="mipro_v2",
            position=position,
        )

        # E-gent senses opportunities
        opportunities = evolution_sensor.sense_opportunities(position)

        assert len(opportunities) == 1
        assert opportunities[0].target_id == "target_002"
        assert opportunities[0].strategy == "mipro_v2"

    def test_sense_by_target(self) -> None:
        """Test filtering refinements by target ID."""
        field = create_semantic_field()
        refinery_emitter = create_refinery_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        # Emit refinements for different targets
        refinery_emitter.emit_refinement("agent_a", "opt", 1.2, position)
        refinery_emitter.emit_refinement("agent_b", "opt", 1.4, position)
        refinery_emitter.emit_refinement("agent_a", "compress", 1.1, position)

        # Sense only agent_a refinements
        agent_a_refinements = evolution_sensor.sense_by_target("agent_a", position)

        assert len(agent_a_refinements) == 2
        assert all(r.target_id == "agent_a" for r in agent_a_refinements)

    def test_get_best_refinement(self) -> None:
        """Test getting the highest-improvement refinement."""
        field = create_semantic_field()
        refinery_emitter = create_refinery_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        # Emit refinements with different improvement ratios
        refinery_emitter.emit_refinement("a", "opt", 1.2, position)
        refinery_emitter.emit_refinement("b", "opt", 1.8, position)
        refinery_emitter.emit_refinement("c", "opt", 1.5, position)

        best = evolution_sensor.get_best_refinement(position)

        assert best is not None
        assert best.target_id == "b"
        assert best.improvement_ratio == 1.8

    def test_get_best_refinement_by_type(self) -> None:
        """Test getting best refinement filtered by type."""
        field = create_semantic_field()
        refinery_emitter = create_refinery_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        refinery_emitter.emit_refinement("a", "optimization", 1.5, position)
        refinery_emitter.emit_refinement("b", "compression", 2.0, position)
        refinery_emitter.emit_refinement("c", "optimization", 1.3, position)

        best_opt = evolution_sensor.get_best_refinement(position, improvement_type="optimization")

        assert best_opt is not None
        assert best_opt.target_id == "a"
        assert best_opt.improvement_ratio == 1.5

    def test_sense_empty_field(self) -> None:
        """Test sensing when no refinements exist."""
        field = create_semantic_field()
        evolution_sensor = create_evolution_sensor(field)
        position = FieldCoordinate(domain="evolution")

        refinements = evolution_sensor.sense_refinements(position)
        best = evolution_sensor.get_best_refinement(position)

        assert refinements == []
        assert best is None


class TestRefineryFieldSensor:
    """Tests for R-gent RefineryFieldSensor (senses MUTATION)."""

    def test_sense_mutations(self) -> None:
        """Test sensing mutation signals."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="refinery")

        # E-gent emits mutation
        evolution_emitter.emit_mutation(
            "mut_001",
            fitness_delta=0.25,
            generation=5,
            position=position,
            mutation_type="point",
        )

        # R-gent senses it
        mutations = refinery_sensor.sense_mutations(position)

        assert len(mutations) == 1
        assert mutations[0].mutation_id == "mut_001"
        assert mutations[0].fitness_delta == 0.25

    def test_sense_fitness_changes(self) -> None:
        """Test sensing fitness change signals."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="refinery")

        # E-gent emits fitness change
        evolution_emitter.emit_fitness_change(
            "entity_001",
            old_fitness=0.5,
            new_fitness=0.8,
            position=position,
            reason="optimization",
        )

        # R-gent senses fitness changes
        fitness_changes = refinery_sensor.sense_fitness_changes(position)

        assert len(fitness_changes) == 1
        assert fitness_changes[0].entity_id == "entity_001"
        assert fitness_changes[0].new_fitness == 0.8

    def test_sense_cycle_completions(self) -> None:
        """Test sensing cycle completion signals."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="refinery")

        # E-gent emits cycle completion
        evolution_emitter.emit_cycle_complete(
            generation=10,
            best_fitness=0.95,
            population_size=50,
            position=position,
            mutations_succeeded=8,
            mutations_failed=2,
        )

        # R-gent senses cycle completions
        cycles = refinery_sensor.sense_cycle_completions(position)

        assert len(cycles) == 1
        assert cycles[0].generation == 10
        assert cycles[0].best_fitness == 0.95

    def test_sense_positive_mutations(self) -> None:
        """Test filtering for positive fitness delta mutations."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="refinery")

        # Emit mutations with different fitness deltas
        evolution_emitter.emit_mutation("m1", -0.2, 1, position)
        evolution_emitter.emit_mutation("m2", 0.3, 2, position)
        evolution_emitter.emit_mutation("m3", 0.1, 3, position)

        # Sense only positive mutations
        positive = refinery_sensor.sense_positive_mutations(position, min_fitness_delta=0.1)

        assert len(positive) == 2
        assert all(m.fitness_delta >= 0.1 for m in positive)

    def test_get_strongest_mutation(self) -> None:
        """Test getting mutation with highest fitness delta."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="refinery")

        evolution_emitter.emit_mutation("m1", 0.1, 1, position)
        evolution_emitter.emit_mutation("m2", 0.4, 2, position)
        evolution_emitter.emit_mutation("m3", 0.2, 3, position)

        strongest = refinery_sensor.get_strongest_mutation(position)

        assert strongest is not None
        assert strongest.mutation_id == "m2"
        assert strongest.fitness_delta == 0.4


class TestPersonaFieldSensor:
    """Tests for K-gent PersonaFieldSensor (senses SYNTHESIS)."""

    def test_sense_syntheses(self) -> None:
        """Test sensing synthesis signals."""
        field = create_semantic_field()
        hegel_emitter = create_hegel_emitter(field)
        persona_sensor = create_persona_sensor(field)
        position = FieldCoordinate(domain="persona")

        # H-gent emits synthesis
        hegel_emitter.emit_synthesis(
            "Individual freedom",
            "Social order",
            "Liberal democracy",
            confidence=0.85,
            position=position,
            domain="politics",
        )

        # K-gent senses it
        syntheses = persona_sensor.sense_syntheses(position)

        assert len(syntheses) == 1
        assert syntheses[0].synthesis == "Liberal democracy"
        assert syntheses[0].confidence == 0.85

    def test_sense_contradictions(self) -> None:
        """Test sensing contradiction signals."""
        field = create_semantic_field()
        hegel_emitter = create_hegel_emitter(field)
        persona_sensor = create_persona_sensor(field)
        position = FieldCoordinate(domain="persona")

        # H-gent emits contradiction
        hegel_emitter.emit_contradiction(
            "X is true",
            "X is false",
            severity=0.9,
            position=position,
            tension_mode="logical",
        )

        # K-gent senses contradictions
        contradictions = persona_sensor.sense_contradictions(position)

        assert len(contradictions) == 1
        assert contradictions[0].severity == 0.9
        assert contradictions[0].tension_mode == "logical"

    def test_sense_by_domain(self) -> None:
        """Test filtering syntheses by domain."""
        field = create_semantic_field()
        hegel_emitter = create_hegel_emitter(field)
        persona_sensor = create_persona_sensor(field)
        position = FieldCoordinate(domain="persona")

        hegel_emitter.emit_synthesis("A", "B", "C", 0.8, position, domain="ethics")
        hegel_emitter.emit_synthesis("D", "E", "F", 0.7, position, domain="politics")
        hegel_emitter.emit_synthesis("G", "H", "I", 0.9, position, domain="ethics")

        ethics_syntheses = persona_sensor.sense_by_domain("ethics", position)

        assert len(ethics_syntheses) == 2
        assert all(s.domain == "ethics" for s in ethics_syntheses)

    def test_get_high_confidence_syntheses(self) -> None:
        """Test filtering syntheses by confidence threshold."""
        field = create_semantic_field()
        hegel_emitter = create_hegel_emitter(field)
        persona_sensor = create_persona_sensor(field)
        position = FieldCoordinate(domain="persona")

        hegel_emitter.emit_synthesis("A", "B", "C1", 0.5, position)
        hegel_emitter.emit_synthesis("D", "E", "C2", 0.8, position)
        hegel_emitter.emit_synthesis("G", "H", "C3", 0.9, position)

        high_conf = persona_sensor.get_high_confidence_syntheses(position, min_confidence=0.7)

        assert len(high_conf) == 2
        assert all(s.confidence >= 0.7 for s in high_conf)

    def test_get_strongest_synthesis(self) -> None:
        """Test getting synthesis with highest confidence."""
        field = create_semantic_field()
        hegel_emitter = create_hegel_emitter(field)
        persona_sensor = create_persona_sensor(field)
        position = FieldCoordinate(domain="persona")

        hegel_emitter.emit_synthesis("A", "B", "low", 0.5, position)
        hegel_emitter.emit_synthesis("C", "D", "high", 0.95, position)
        hegel_emitter.emit_synthesis("E", "F", "mid", 0.7, position)

        strongest = persona_sensor.get_strongest_synthesis(position)

        assert strongest is not None
        assert strongest.synthesis == "high"
        assert strongest.confidence == 0.95


class TestHegelFieldSensor:
    """Tests for H-gent HegelFieldSensor (senses PRIOR)."""

    def test_sense_priors(self) -> None:
        """Test sensing prior signals."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        # K-gent emits prior
        persona_emitter.emit_prior_change(
            "risk_tolerance",
            0.7,
            "kent",
            position,
            reason="User prefers bold choices",
        )

        # H-gent senses it
        priors = hegel_sensor.sense_priors(position)

        assert len(priors) == 1
        assert priors[0].prior_type == "risk_tolerance"
        assert priors[0].value == 0.7

    def test_sense_persona_shifts(self) -> None:
        """Test sensing persona shift signals."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        # K-gent emits persona shift
        persona_emitter.emit_persona_shift(
            "researcher",
            "creator",
            position,
            trigger="Project phase change",
        )

        # H-gent senses shifts
        shifts = hegel_sensor.sense_persona_shifts(position)

        assert len(shifts) == 1
        assert shifts[0].old_persona == "researcher"
        assert shifts[0].new_persona == "creator"

    def test_sense_by_prior_type(self) -> None:
        """Test filtering priors by type."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        persona_emitter.emit_prior_change("risk_tolerance", 0.7, "kent", position)
        persona_emitter.emit_prior_change("creativity", 0.9, "kent", position)
        persona_emitter.emit_prior_change("risk_tolerance", 0.8, "kent", position)

        risk_priors = hegel_sensor.sense_by_prior_type("risk_tolerance", position)

        assert len(risk_priors) == 2
        assert all(p.prior_type == "risk_tolerance" for p in risk_priors)

    def test_sense_by_persona(self) -> None:
        """Test filtering priors by persona ID."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        persona_emitter.emit_prior_change("risk", 0.7, "kent", position)
        persona_emitter.emit_prior_change("risk", 0.3, "other", position)
        persona_emitter.emit_prior_change("speed", 0.8, "kent", position)

        kent_priors = hegel_sensor.sense_by_persona("kent", position)

        assert len(kent_priors) == 2
        assert all(p.persona_id == "kent" for p in kent_priors)

    def test_get_active_persona(self) -> None:
        """Test getting the active persona from shifts."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        persona_emitter.emit_persona_shift("mode1", "mode2", position)

        active = hegel_sensor.get_active_persona(position)

        assert active == "mode2"

    def test_get_active_persona_none(self) -> None:
        """Test getting active persona when no shifts exist."""
        field = create_semantic_field()
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        active = hegel_sensor.get_active_persona(position)

        assert active is None

    def test_get_prior_value(self) -> None:
        """Test getting specific prior value."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        persona_emitter.emit_prior_change("risk_tolerance", 0.75, "kent", position, confidence=0.9)

        value = hegel_sensor.get_prior_value("risk_tolerance", position)

        assert value == 0.75

    def test_get_prior_value_default(self) -> None:
        """Test getting prior value returns default when not found."""
        field = create_semantic_field()
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate()

        value = hegel_sensor.get_prior_value("nonexistent", position, default=0.5)

        assert value == 0.5


# =============================================================================
# Phase 2 Integration Tests
# =============================================================================


class TestPhase2Integration:
    """Integration tests for Phase 2 sensor bidirectional coordination."""

    def test_evolution_refinement_bidirectional(self) -> None:
        """Test E-gent ↔ R-gent bidirectional coordination."""
        field = create_semantic_field()
        evolution_emitter = create_evolution_emitter(field)
        evolution_sensor = create_evolution_sensor(field)
        refinery_emitter = create_refinery_emitter(field)
        refinery_sensor = create_refinery_sensor(field)
        position = FieldCoordinate(domain="shared")

        # E-gent discovers mutation → R-gent senses it
        evolution_emitter.emit_mutation("mut_001", 0.3, 5, position)
        mutations = refinery_sensor.sense_mutations(position)
        assert len(mutations) == 1

        # R-gent refines it → E-gent senses the improvement
        refinery_emitter.emit_refinement("mut_001", "optimization", 1.4, position)
        refinements = evolution_sensor.sense_refinements(position)
        assert len(refinements) == 1
        assert refinements[0].target_id == "mut_001"

    def test_persona_hegel_bidirectional(self) -> None:
        """Test K-gent ↔ H-gent bidirectional coordination."""
        field = create_semantic_field()
        persona_emitter = create_persona_emitter(field)
        persona_sensor = create_persona_sensor(field)
        hegel_emitter = create_hegel_emitter(field)
        hegel_sensor = create_hegel_sensor(field)
        position = FieldCoordinate(domain="shared")

        # K-gent broadcasts prior → H-gent senses it
        persona_emitter.emit_prior_change("risk_tolerance", 0.8, "kent", position)
        priors = hegel_sensor.sense_priors(position)
        assert len(priors) == 1
        assert priors[0].value == 0.8

        # H-gent achieves synthesis → K-gent senses it
        hegel_emitter.emit_synthesis(
            "Caution",
            "Boldness",
            "Calculated risk-taking",
            confidence=0.9,
            position=position,
        )
        syntheses = persona_sensor.sense_syntheses(position)
        assert len(syntheses) == 1
        assert syntheses[0].synthesis == "Calculated risk-taking"

    def test_full_stigmergic_loop(self) -> None:
        """Test complete stigmergic coordination loop."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="shared")

        # Create all Phase 1 emitters and Phase 2 sensors
        evolution_emitter = create_evolution_emitter(field)
        hegel_emitter = create_hegel_emitter(field)
        persona_emitter = create_persona_emitter(field)
        refinery_emitter = create_refinery_emitter(field)

        evolution_sensor = create_evolution_sensor(field)
        hegel_sensor = create_hegel_sensor(field)
        persona_sensor = create_persona_sensor(field)
        refinery_sensor = create_refinery_sensor(field)

        # 1. K-gent sets preference (high risk tolerance)
        persona_emitter.emit_prior_change("risk_tolerance", 0.9, "kent", position)

        # 2. H-gent senses prior, performs dialectic
        risk_value = hegel_sensor.get_prior_value("risk_tolerance", position)
        assert risk_value == 0.9

        # 3. H-gent emits synthesis based on high risk tolerance
        hegel_emitter.emit_synthesis(
            "Safety",
            "Speed",
            "Aggressive optimization",
            confidence=0.85,
            position=position,
        )

        # 4. K-gent senses synthesis, updates priors
        syntheses = persona_sensor.sense_syntheses(position)
        assert len(syntheses) == 1

        # 5. E-gent discovers bold mutation
        evolution_emitter.emit_mutation("bold_mut", 0.4, 1, position, mutation_type="structural")

        # 6. R-gent senses mutation, identifies refinement opportunity
        mutations = refinery_sensor.sense_mutations(position)
        assert len(mutations) == 1

        # 7. R-gent completes refinement
        refinery_emitter.emit_refinement("bold_mut", "optimization", 1.5, position)

        # 8. E-gent senses refinement for next evolution cycle
        refinements = evolution_sensor.sense_refinements(position)
        assert len(refinements) == 1
        assert refinements[0].improvement_ratio == 1.5

    def test_sensors_do_not_cross_contaminate(self) -> None:
        """Test that sensors only sense their designated signal types."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="shared")

        # Emit all signal types
        create_evolution_emitter(field).emit_mutation("m1", 0.3, 1, position)
        create_hegel_emitter(field).emit_synthesis("A", "B", "C", 0.8, position)
        create_persona_emitter(field).emit_prior_change("x", 0.5, "k", position)
        create_refinery_emitter(field).emit_refinement("t", "opt", 1.2, position)

        # Each sensor should only see its designated type
        evolution_sensor = create_evolution_sensor(field)
        refinery_sensor = create_refinery_sensor(field)
        persona_sensor = create_persona_sensor(field)
        hegel_sensor = create_hegel_sensor(field)

        # Evolution sensor sees REFINEMENT only
        assert len(evolution_sensor.sense_refinements(position)) == 1
        # Refinery sensor sees MUTATION only
        assert len(refinery_sensor.sense_mutations(position)) == 1
        # Persona sensor sees SYNTHESIS only
        assert len(persona_sensor.sense_syntheses(position)) == 1
        # Hegel sensor sees PRIOR only
        assert len(hegel_sensor.sense_priors(position)) == 1


# =============================================================================
# Phase 3: D-gent Data Field Emitter/Sensor Tests
# =============================================================================


class TestDataFieldEmitter:
    """Tests for D-gent DataFieldEmitter (STATE signals)."""

    def test_emit_state_change(self) -> None:
        """Test emitting a state change signal."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate(domain="data")

        phero_id = emitter.emit_state_change(
            entity_id="entity_001",
            state_type="created",
            key="users/kent",
            position=position,
            new_value_hash="abc123",
            store_id="main_db",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.entity_id == "entity_001"
        assert payload.state_type == "created"
        assert payload.key == "users/kent"
        assert payload.new_value_hash == "abc123"

    def test_emit_created_convenience(self) -> None:
        """Test convenience method for entity creation."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_created("e1", "key/path", position, value_hash="hash1")

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        payload = pheromones[0].payload
        assert payload.state_type == "created"

    def test_emit_updated_convenience(self) -> None:
        """Test convenience method for entity updates."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_updated("e1", "key/path", position, old_hash="old", new_hash="new")

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        payload = pheromones[0].payload
        assert payload.state_type == "updated"
        assert payload.old_value_hash == "old"
        assert payload.new_value_hash == "new"

    def test_emit_deleted_convenience(self) -> None:
        """Test convenience method for entity deletion."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_deleted("e1", "key/path", position)

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        payload = pheromones[0].payload
        assert payload.state_type == "deleted"

    def test_delete_has_highest_intensity(self) -> None:
        """Test that delete events have higher intensity than creates."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate()

        emitter.emit_created("e1", "k1", position)
        emitter.emit_deleted("e2", "k2", position)

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        intensities = {p.payload.state_type: p.intensity for p in pheromones}

        assert intensities["deleted"] > intensities["created"]

    def test_emit_stale(self) -> None:
        """Test emitting a stale data signal."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_stale(
            entity_id="e1",
            key="old/key",
            last_accessed="2024-01-01T00:00:00Z",
            staleness_score=0.8,
            position=position,
            recommended_action="archive",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.STATE)
        assert len(pheromones) == 1
        assert pheromones[0].intensity == 0.8


class TestDataFieldSensor:
    """Tests for D-gent DataFieldSensor."""

    def test_sense_state_changes(self) -> None:
        """Test sensing state change signals."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        sensor = create_data_sensor(field)
        position = FieldCoordinate(domain="data")

        emitter.emit_created("e1", "k1", position)
        emitter.emit_updated("e2", "k2", position)

        changes = sensor.sense_state_changes(position)

        assert len(changes) == 2

    def test_sense_by_state_type(self) -> None:
        """Test filtering by state type."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        sensor = create_data_sensor(field)
        position = FieldCoordinate(domain="data")

        emitter.emit_created("e1", "k1", position)
        emitter.emit_deleted("e2", "k2", position)
        emitter.emit_created("e3", "k3", position)

        creates = sensor.sense_by_state_type("created", position)
        deletes = sensor.sense_by_state_type("deleted", position)

        assert len(creates) == 2
        assert len(deletes) == 1

    def test_sense_by_entity(self) -> None:
        """Test filtering by entity ID."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        sensor = create_data_sensor(field)
        position = FieldCoordinate(domain="data")

        emitter.emit_created("entity_a", "k1", position)
        emitter.emit_updated("entity_a", "k2", position)
        emitter.emit_created("entity_b", "k3", position)

        entity_a_changes = sensor.sense_by_entity("entity_a", position)

        assert len(entity_a_changes) == 2
        assert all(c.entity_id == "entity_a" for c in entity_a_changes)

    def test_sense_stale(self) -> None:
        """Test sensing stale data signals."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        sensor = create_data_sensor(field)
        position = FieldCoordinate(domain="data")

        emitter.emit_stale("e1", "k1", "2024-01-01", 0.3, position)
        emitter.emit_stale("e2", "k2", "2024-01-01", 0.8, position)

        all_stale = sensor.sense_stale(position)
        high_stale = sensor.sense_stale(position, min_staleness=0.5)

        assert len(all_stale) == 2
        assert len(high_stale) == 1
        assert high_stale[0].staleness_score == 0.8

    def test_get_deletions(self) -> None:
        """Test getting deletion events."""
        field = create_semantic_field()
        emitter = create_data_emitter(field)
        sensor = create_data_sensor(field)
        position = FieldCoordinate(domain="data")

        emitter.emit_created("e1", "k1", position)
        emitter.emit_deleted("e2", "k2", position)
        emitter.emit_updated("e3", "k3", position)

        deletions = sensor.get_deletions(position)

        assert len(deletions) == 1
        assert deletions[0].entity_id == "e2"


# =============================================================================
# Phase 3: T-gent Test Field Emitter/Sensor Tests
# =============================================================================


class TestTestFieldEmitter:
    """Tests for T-gent TestFieldEmitter (TEST signals)."""

    def test_emit_test_result(self) -> None:
        """Test emitting a test result signal."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        position = FieldCoordinate(domain="test")

        phero_id = emitter.emit_test_result(
            test_id="test_foo",
            result="passed",
            position=position,
            duration_ms=150.5,
            affected_agents=("d", "m"),
            test_file="test_module.py",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.TEST)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.test_id == "test_foo"
        assert payload.result == "passed"
        assert payload.duration_ms == 150.5
        assert "d" in payload.affected_agents

    def test_failure_has_higher_intensity(self) -> None:
        """Test that failures have higher intensity than passes."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        position = FieldCoordinate()

        emitter.emit_test_result("t1", "passed", position)
        emitter.emit_test_result("t2", "failed", position)
        emitter.emit_test_result("t3", "error", position)

        pheromones = field.get_all(SemanticPheromoneKind.TEST)
        intensities = {p.payload.test_id: p.intensity for p in pheromones}

        assert intensities["t3"] > intensities["t2"] > intensities["t1"]

    def test_emit_coverage_change(self) -> None:
        """Test emitting coverage change signal."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_coverage_change(
            old_coverage=0.75,
            new_coverage=0.82,
            position=position,
            affected_files=("module_a.py", "module_b.py"),
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.TEST)
        assert len(pheromones) == 1
        assert pheromones[0].payload.delta == pytest.approx(0.07)

    def test_emit_test_suite_complete(self) -> None:
        """Test emitting test suite completion signal."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_test_suite_complete(
            suite_id="full_suite",
            passed=95,
            failed=3,
            skipped=2,
            total_duration_ms=5000.0,
            position=position,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.TEST)
        assert len(pheromones) == 1
        assert pheromones[0].metadata.get("signal_type") == "suite_complete"


class TestTestFieldSensor:
    """Tests for T-gent TestFieldSensor."""

    def test_sense_test_results(self) -> None:
        """Test sensing test result signals."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        emitter.emit_test_result("t1", "passed", position)
        emitter.emit_test_result("t2", "failed", position)

        results = sensor.sense_test_results(position)

        assert len(results) == 2

    def test_sense_failures(self) -> None:
        """Test sensing failure signals specifically."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        emitter.emit_test_result("t1", "passed", position)
        emitter.emit_test_result("t2", "failed", position)
        emitter.emit_test_result("t3", "error", position)
        emitter.emit_test_result("t4", "skipped", position)

        failures = sensor.sense_failures(position)

        assert len(failures) == 2
        assert all(f.result in ("failed", "error") for f in failures)

    def test_sense_by_affected_agent(self) -> None:
        """Test filtering by affected agent."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        emitter.emit_test_result("t1", "failed", position, affected_agents=("d", "m"))
        emitter.emit_test_result("t2", "failed", position, affected_agents=("w",))
        emitter.emit_test_result("t3", "passed", position, affected_agents=("d",))

        d_tests = sensor.sense_by_affected_agent("d", position)

        assert len(d_tests) == 2
        assert all("d" in t.affected_agents for t in d_tests)

    def test_sense_coverage_changes(self) -> None:
        """Test sensing coverage change signals."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        emitter.emit_coverage_change(0.75, 0.80, position)
        emitter.emit_coverage_change(0.80, 0.78, position)  # Regression

        changes = sensor.sense_coverage_changes(position)

        assert len(changes) == 2

    def test_get_coverage_regressions(self) -> None:
        """Test getting coverage regressions."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        emitter.emit_coverage_change(0.75, 0.80, position)  # Improvement
        emitter.emit_coverage_change(0.80, 0.78, position)  # Regression
        emitter.emit_coverage_change(0.78, 0.70, position)  # Regression

        regressions = sensor.get_coverage_regressions(position)

        assert len(regressions) == 2
        assert all(r.delta < 0 for r in regressions)

    def test_has_failures(self) -> None:
        """Test checking for failures."""
        field = create_semantic_field()
        emitter = create_test_emitter(field)
        sensor = create_test_sensor(field)
        position = FieldCoordinate(domain="test")

        # No failures initially
        assert not sensor.has_failures(position)

        emitter.emit_test_result("t1", "passed", position)
        assert not sensor.has_failures(position)

        emitter.emit_test_result("t2", "failed", position)
        assert sensor.has_failures(position)


# =============================================================================
# Phase 3: W-gent Wire Field Emitter/Sensor Tests
# =============================================================================


class TestWireFieldEmitter:
    """Tests for W-gent WireFieldEmitter (DISPATCH signals)."""

    def test_emit_dispatch(self) -> None:
        """Test emitting a dispatch signal."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        position = FieldCoordinate(domain="wire")

        phero_id = emitter.emit_dispatch(
            message_id="msg_001",
            source="agent_a",
            target="agent_b",
            position=position,
            intercepted_by=("safety", "meter"),
            latency_ms=25.5,
            message_type="request",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.DISPATCH)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert payload.message_id == "msg_001"
        assert payload.source == "agent_a"
        assert payload.target == "agent_b"
        assert "safety" in payload.intercepted_by

    def test_interceptors_increase_intensity(self) -> None:
        """Test that more interceptors increase intensity."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        position = FieldCoordinate()

        emitter.emit_dispatch("m1", "a", "b", position, intercepted_by=())
        emitter.emit_dispatch("m2", "a", "b", position, intercepted_by=("i1", "i2", "i3"))

        pheromones = field.get_all(SemanticPheromoneKind.DISPATCH)
        intensities = {p.payload.message_id: p.intensity for p in pheromones}

        assert intensities["m2"] > intensities["m1"]

    def test_emit_blocked(self) -> None:
        """Test emitting a blocked message signal."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_blocked(
            message_id="msg_002",
            blocker="safety_interceptor",
            reason="Content policy violation",
            position=position,
            source="agent_x",
            target="agent_y",
            severity="error",
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.DISPATCH)
        assert len(pheromones) == 1
        assert pheromones[0].metadata.get("signal_type") == "blocked"

    def test_blocked_severity_affects_intensity(self) -> None:
        """Test that block severity affects intensity."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        position = FieldCoordinate()

        emitter.emit_blocked("m1", "b1", "info level", position, severity="info")
        emitter.emit_blocked("m2", "b2", "error level", position, severity="error")

        pheromones = field.get_all(SemanticPheromoneKind.DISPATCH)
        intensities = {p.payload.message_id: p.intensity for p in pheromones}

        assert intensities["m2"] > intensities["m1"]

    def test_emit_routing_latency(self) -> None:
        """Test emitting routing latency signal."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        position = FieldCoordinate()

        phero_id = emitter.emit_routing_latency(
            route_id="route_001",
            source="a",
            target="b",
            latency_ms=500.0,
            position=position,
            is_slow=True,
        )

        assert phero_id.startswith("phero-")

        pheromones = field.get_all(SemanticPheromoneKind.DISPATCH)
        assert len(pheromones) == 1
        assert pheromones[0].metadata.get("signal_type") == "latency"


class TestWireFieldSensor:
    """Tests for W-gent WireFieldSensor."""

    def test_sense_dispatches(self) -> None:
        """Test sensing dispatch signals."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_dispatch("m1", "a", "b", position)
        emitter.emit_dispatch("m2", "c", "d", position)

        dispatches = sensor.sense_dispatches(position)

        assert len(dispatches) == 2

    def test_sense_blocked(self) -> None:
        """Test sensing blocked message signals."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_dispatch("m1", "a", "b", position)
        emitter.emit_blocked("m2", "blocker", "reason", position)

        blocked = sensor.sense_blocked(position)

        assert len(blocked) == 1
        assert blocked[0].blocker == "blocker"

    def test_sense_by_source(self) -> None:
        """Test filtering dispatches by source."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_dispatch("m1", "agent_a", "x", position)
        emitter.emit_dispatch("m2", "agent_b", "x", position)
        emitter.emit_dispatch("m3", "agent_a", "y", position)

        from_a = sensor.sense_by_source("agent_a", position)

        assert len(from_a) == 2
        assert all(d.source == "agent_a" for d in from_a)

    def test_sense_by_target(self) -> None:
        """Test filtering dispatches by target."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_dispatch("m1", "x", "target_a", position)
        emitter.emit_dispatch("m2", "x", "target_b", position)
        emitter.emit_dispatch("m3", "y", "target_a", position)

        to_a = sensor.sense_by_target("target_a", position)

        assert len(to_a) == 2
        assert all(d.target == "target_a" for d in to_a)

    def test_sense_intercepted(self) -> None:
        """Test sensing intercepted messages."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_dispatch("m1", "a", "b", position, intercepted_by=())
        emitter.emit_dispatch("m2", "a", "b", position, intercepted_by=("i1",))
        emitter.emit_dispatch("m3", "a", "b", position, intercepted_by=("i1", "i2"))

        intercepted = sensor.sense_intercepted(position)

        assert len(intercepted) == 2
        assert all(d.intercepted_by for d in intercepted)

    def test_get_blockers(self) -> None:
        """Test getting unique blockers."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        emitter.emit_blocked("m1", "safety", "r1", position)
        emitter.emit_blocked("m2", "meter", "r2", position)
        emitter.emit_blocked("m3", "safety", "r3", position)

        blockers = sensor.get_blockers(position)

        assert blockers == {"safety", "meter"}

    def test_has_blocks(self) -> None:
        """Test checking for blocked messages."""
        field = create_semantic_field()
        emitter = create_wire_emitter(field)
        sensor = create_wire_sensor(field)
        position = FieldCoordinate(domain="wire")

        assert not sensor.has_blocks(position)

        emitter.emit_dispatch("m1", "a", "b", position)
        assert not sensor.has_blocks(position)

        emitter.emit_blocked("m2", "blocker", "reason", position)
        assert sensor.has_blocks(position)


# =============================================================================
# Phase 3 Pheromone Kind Properties Tests
# =============================================================================


class TestPhase3PheromoneKindProperties:
    """Tests for Phase 3 pheromone kind properties."""

    def test_phase3_kinds_have_decay_rate(self) -> None:
        """Test Phase 3 pheromone kinds have decay rates."""
        phase3_kinds = [
            SemanticPheromoneKind.STATE,
            SemanticPheromoneKind.TEST,
            SemanticPheromoneKind.DISPATCH,
        ]
        for kind in phase3_kinds:
            assert 0.0 < kind.decay_rate <= 1.0

    def test_phase3_kinds_have_default_radius(self) -> None:
        """Test Phase 3 pheromone kinds have default radii."""
        phase3_kinds = [
            SemanticPheromoneKind.STATE,
            SemanticPheromoneKind.TEST,
            SemanticPheromoneKind.DISPATCH,
        ]
        for kind in phase3_kinds:
            assert kind.default_radius > 0

    def test_dispatch_decays_fastest(self) -> None:
        """Test DISPATCH decays fastest (operational signals)."""
        assert SemanticPheromoneKind.DISPATCH.decay_rate > SemanticPheromoneKind.STATE.decay_rate
        assert SemanticPheromoneKind.DISPATCH.decay_rate > SemanticPheromoneKind.TEST.decay_rate

    def test_test_has_wide_radius(self) -> None:
        """Test TEST signals have wide radius (many care about test results)."""
        assert SemanticPheromoneKind.TEST.default_radius >= 0.8


# =============================================================================
# Phase 3 Integration Tests
# =============================================================================


class TestPhase3Integration:
    """Integration tests for Phase 3 infrastructure agents."""

    def test_data_test_coordination(self) -> None:
        """Test D-gent and T-gent can coordinate via field."""
        field = create_semantic_field()
        data = create_data_emitter(field)
        test = create_test_emitter(field)
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # D-gent creates some data
        data.emit_created("entity_001", "users/kent", position)

        # T-gent runs tests on it
        test.emit_test_result("test_user_creation", "passed", position, affected_agents=("d",))

        # Observer sees both
        observed = observer.observe_all(position)

        assert SemanticPheromoneKind.STATE.value in observed
        assert SemanticPheromoneKind.TEST.value in observed

    def test_wire_safety_coordination(self) -> None:
        """Test W-gent blocking triggers safety awareness."""
        field = create_semantic_field()
        wire = create_wire_emitter(field)
        safety = create_safety_emitter(field)
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # W-gent blocks a message
        wire.emit_blocked(
            "msg_001",
            "safety_interceptor",
            "Policy violation",
            position,
            severity="error",
        )

        # J-gent emits corresponding warning
        safety.emit_warning("error", "Message blocked due to policy", position)

        # Observer sees both
        observed = observer.observe_all(position)

        assert SemanticPheromoneKind.DISPATCH.value in observed
        assert SemanticPheromoneKind.WARNING.value in observed

    def test_field_summary_includes_phase3(self) -> None:
        """Test field summary counts Phase 3 pheromones."""
        field = create_semantic_field()
        observer = create_observer_sensor(field)
        position = FieldCoordinate()

        # Emit one of each Phase 3 type
        create_data_emitter(field).emit_created("e1", "k1", position)
        create_test_emitter(field).emit_test_result("t1", "passed", position)
        create_wire_emitter(field).emit_dispatch("m1", "a", "b", position)

        summary = observer.field_summary()

        assert summary[SemanticPheromoneKind.STATE.value] == 1
        assert summary[SemanticPheromoneKind.TEST.value] == 1
        assert summary[SemanticPheromoneKind.DISPATCH.value] == 1

    def test_full_infrastructure_loop(self) -> None:
        """Test complete infrastructure coordination loop."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="infra")

        # Create all Phase 3 emitters and sensors
        data_emitter = create_data_emitter(field)
        data_sensor = create_data_sensor(field)
        test_emitter = create_test_emitter(field)
        test_sensor = create_test_sensor(field)
        wire_emitter = create_wire_emitter(field)
        wire_sensor = create_wire_sensor(field)

        # 1. D-gent creates data
        data_emitter.emit_created("entity_001", "users/kent", position)

        # 2. W-gent routes message about it
        wire_emitter.emit_dispatch("msg_001", "d", "t", position, message_type="data_created")

        # 3. T-gent runs tests
        test_emitter.emit_test_result(
            "test_data_integrity", "passed", position, affected_agents=("d",)
        )

        # 4. D-gent updates based on test success
        data_emitter.emit_updated("entity_001", "users/kent", position)

        # 5. Sensors can see everything
        state_changes = data_sensor.sense_state_changes(position)
        test_results = test_sensor.sense_test_results(position)
        dispatches = wire_sensor.sense_dispatches(position)

        assert len(state_changes) == 2  # created + updated
        assert len(test_results) == 1
        assert len(dispatches) == 1
