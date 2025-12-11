"""
Tests for Semantic Stigmergic Field.

Phase 2 of Cross-Pollination: Agents coordinate via environmental signals.

Tests:
- Pheromone emission and decay
- Sensing by radius and kind
- Psi × F decoupled integration
- Safety and economic signals
"""

import pytest
from agents.i.semantic_field import (
    FieldCoordinate,
    IntentPayload,
    MetaphorPayload,
    OpportunityPayload,
    SemanticPheromone,
    SemanticPheromoneKind,
    WarningPayload,
    create_economic_emitter,
    # Phase 1 imports
    create_evolution_emitter,
    create_forge_sensor,
    create_hegel_emitter,
    create_memory_emitter,
    create_memory_sensor,
    create_narrative_emitter,
    create_narrative_sensor,
    create_observer_sensor,
    create_persona_emitter,
    create_psi_emitter,
    create_refinery_emitter,
    create_safety_emitter,
    create_semantic_field,
)


class TestFieldCoordinate:
    """Tests for FieldCoordinate."""

    def test_embedding_distance(self):
        """Test distance in embedding space."""
        c1 = FieldCoordinate(embedding=(0.0, 0.0, 0.0))
        c2 = FieldCoordinate(embedding=(3.0, 4.0, 0.0))

        # 3-4-5 triangle
        assert c1.distance_to(c2) == pytest.approx(5.0)

    def test_embedding_distance_mismatched_dims(self):
        """Test distance returns inf for mismatched dimensions."""
        c1 = FieldCoordinate(embedding=(0.0, 0.0))
        c2 = FieldCoordinate(embedding=(1.0, 1.0, 1.0))

        assert c1.distance_to(c2) == float("inf")

    def test_domain_distance_same(self):
        """Test domain distance for same domain."""
        c1 = FieldCoordinate(domain="software")
        c2 = FieldCoordinate(domain="software")

        assert c1.distance_to(c2) == 0.0

    def test_domain_distance_different(self):
        """Test domain distance for different domains."""
        c1 = FieldCoordinate(domain="software")
        c2 = FieldCoordinate(domain="biology")

        assert c1.distance_to(c2) == 1.0

    def test_tag_distance(self):
        """Test tag-based distance."""
        c1 = FieldCoordinate(tags=("python", "async", "api"))
        c2 = FieldCoordinate(tags=("python", "sync", "cli"))

        # Jaccard: 1 common / 5 total = 0.2, distance = 0.8
        assert c1.distance_to(c2) == pytest.approx(0.8)

    def test_tag_distance_identical(self):
        """Test tag distance for identical tags."""
        c1 = FieldCoordinate(tags=("a", "b", "c"))
        c2 = FieldCoordinate(tags=("a", "b", "c"))

        assert c1.distance_to(c2) == 0.0

    def test_default_distance(self):
        """Test default distance when no coords available."""
        c1 = FieldCoordinate()
        c2 = FieldCoordinate()

        assert c1.distance_to(c2) == 1.0


class TestSemanticPheromone:
    """Tests for SemanticPheromone."""

    def test_pheromone_creation(self):
        """Test basic pheromone creation."""
        payload = MetaphorPayload(
            source_domain="database",
            target_domain="graph",
            confidence=0.8,
        )
        pheromone = SemanticPheromone(
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

    def test_pheromone_decay(self):
        """Test pheromone decay over time."""
        pheromone = SemanticPheromone(
            id="test-1",
            emitter="psi",
            kind=SemanticPheromoneKind.METAPHOR,
            payload={},
            intensity=1.0,
            position=FieldCoordinate(),
        )

        # Decay
        new_intensity = pheromone.decay(1.0)
        assert new_intensity < 1.0
        assert pheromone.intensity == new_intensity

    def test_pheromone_expires(self):
        """Test pheromone expiration after many decays."""
        pheromone = SemanticPheromone(
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

    def test_field_creation(self):
        """Test field creation."""
        field = create_semantic_field()
        assert field.pheromone_count == 0
        assert field.current_tick == 0

    def test_emit_and_count(self):
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

    def test_sense_by_kind(self):
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

    def test_sense_by_radius(self):
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

    def test_sense_sorted_by_intensity(self):
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

    def test_sense_strongest(self):
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

    def test_tick_decay(self):
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

    def test_clear(self):
        """Test clearing the field."""
        field = create_semantic_field()

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())
        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())

        assert field.pheromone_count == 2

        count = field.clear()
        assert count == 2
        assert field.pheromone_count == 0

    def test_get_all(self):
        """Test getting all pheromones."""
        field = create_semantic_field()

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())
        field.emit("forge", SemanticPheromoneKind.INTENT, {}, FieldCoordinate())

        all_pheromones = field.get_all()
        assert len(all_pheromones) == 2

        metaphors_only = field.get_all(SemanticPheromoneKind.METAPHOR)
        assert len(metaphors_only) == 1

    def test_deposit_callback(self):
        """Test deposit callback is called."""
        field = create_semantic_field()
        deposits = []

        field.on_deposit(lambda p: deposits.append(p))

        field.emit("psi", SemanticPheromoneKind.METAPHOR, {}, FieldCoordinate())

        assert len(deposits) == 1
        assert deposits[0].emitter == "psi"


class TestPsiFieldEmitter:
    """Tests for PsiFieldEmitter."""

    def test_emit_metaphor(self):
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

    def test_sense_metaphors(self):
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

    def test_get_strongest_metaphor(self):
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

    def test_emit_intent(self):
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

    def test_psi_emits_forge_senses(self):
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

    def test_multiple_metaphors_strongest_wins(self):
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

    def test_metaphor_decay_affects_sensing(self):
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

    def test_emit_warning(self):
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

    def test_warning_intensity_by_severity(self):
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

    def test_emit_opportunity(self):
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

    def test_emit_scarcity(self):
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

    def test_emit_consolidation(self):
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

    def test_sense_memories_by_importance(self):
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

    def test_emit_story_event(self):
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

    def test_climax_has_highest_intensity(self):
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

    def test_sense_narratives_by_thread(self):
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

    def test_observe_all_kinds(self):
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

    def test_observe_warnings_by_severity(self):
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

    def test_field_summary(self):
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

    def test_all_kinds_have_decay_rate(self):
        """Test all kinds have a decay rate."""
        for kind in SemanticPheromoneKind:
            assert 0.0 < kind.decay_rate <= 1.0

    def test_all_kinds_have_default_radius(self):
        """Test all kinds have a default radius."""
        for kind in SemanticPheromoneKind:
            assert kind.default_radius > 0

    def test_warning_decays_fast(self):
        """Warnings should decay faster than metaphors."""
        assert (
            SemanticPheromoneKind.WARNING.decay_rate
            > SemanticPheromoneKind.METAPHOR.decay_rate
        )

    def test_warning_has_wide_radius(self):
        """Warnings should broadcast widely."""
        assert SemanticPheromoneKind.WARNING.default_radius >= 1.0

    def test_phase1_kinds_have_properties(self):
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

    def test_prior_decays_slowly(self):
        """Priors should decay slowly (persona is stable)."""
        assert (
            SemanticPheromoneKind.PRIOR.decay_rate
            < SemanticPheromoneKind.MUTATION.decay_rate
        )

    def test_prior_has_wide_radius(self):
        """Priors should broadcast widely to affect all agents."""
        assert SemanticPheromoneKind.PRIOR.default_radius >= 1.0


# =============================================================================
# Phase 1: E-gent Evolution Field Emitter Tests
# =============================================================================


class TestEvolutionFieldEmitter:
    """Tests for E-gent EvolutionFieldEmitter (MUTATION signals)."""

    def test_emit_mutation(self):
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

    def test_mutation_intensity_scales_with_fitness(self):
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

    def test_emit_fitness_change(self):
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

    def test_emit_cycle_complete(self):
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

    def test_emit_synthesis(self):
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

    def test_synthesis_intensity_matches_confidence(self):
        """Synthesis intensity should match confidence."""
        field = create_semantic_field()
        emitter = create_hegel_emitter(field)
        position = FieldCoordinate()

        emitter.emit_synthesis("A", "B", "C", 0.9, position)

        pheromones = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        assert pheromones[0].intensity == 0.9

    def test_emit_contradiction(self):
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

    def test_emit_productive_tension(self):
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

    def test_emit_prior_change(self):
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

    def test_prior_intensity_matches_confidence(self):
        """Prior intensity should match confidence."""
        field = create_semantic_field()
        emitter = create_persona_emitter(field)
        position = FieldCoordinate()

        emitter.emit_prior_change("creativity", 0.8, "kent", position, confidence=0.75)

        pheromones = field.get_all(SemanticPheromoneKind.PRIOR)
        assert pheromones[0].intensity == 0.75

    def test_emit_persona_shift(self):
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

    def test_emit_preference(self):
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

    def test_emit_refinement(self):
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

    def test_refinement_intensity_scales_with_improvement(self):
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

    def test_emit_opportunity(self):
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

    def test_emit_optimization_trace(self):
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

    def test_evolution_and_refinement_coordination(self):
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

    def test_persona_affects_all_agents(self):
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

    def test_hegel_synthesis_visible_to_psi(self):
        """Test H-gent synthesis can be observed by other agents."""
        field = create_semantic_field()
        hegel = create_hegel_emitter(field)
        psi = create_psi_emitter(field)
        position = FieldCoordinate()

        # H-gent achieves a synthesis
        hegel.emit_synthesis(
            "Efficiency", "Reliability", "Robust efficiency", 0.85, position
        )

        # Psi-gent (metaphor solver) emits a related metaphor
        psi.emit_metaphor("robust_efficiency", "bridge_engineering", 0.75, position)

        # Both signals coexist in the field
        synthesis_signals = field.get_all(SemanticPheromoneKind.SYNTHESIS)
        metaphor_signals = field.get_all(SemanticPheromoneKind.METAPHOR)

        assert len(synthesis_signals) == 1
        assert len(metaphor_signals) == 1

    def test_field_summary_includes_phase1(self):
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
