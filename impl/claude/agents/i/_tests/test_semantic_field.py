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
    create_forge_sensor,
    create_memory_emitter,
    create_memory_sensor,
    create_narrative_emitter,
    create_narrative_sensor,
    create_observer_sensor,
    create_psi_emitter,
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
