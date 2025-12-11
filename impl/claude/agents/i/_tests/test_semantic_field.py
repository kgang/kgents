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
    SemanticPheromone,
    SemanticPheromoneKind,
    FieldCoordinate,
    MetaphorPayload,
    IntentPayload,
    WarningPayload,
    OpportunityPayload,
    CapabilityPayload,
    CapabilityDeprecationPayload,
    CapabilityRequestPayload,
    create_semantic_field,
    create_psi_emitter,
    create_forge_sensor,
    create_safety_emitter,
    create_economic_emitter,
    create_memory_emitter,
    create_memory_sensor,
    create_narrative_emitter,
    create_narrative_sensor,
    create_observer_sensor,
    create_catalog_emitter,
    create_catalog_sensor,
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

    def test_capability_has_wide_radius(self):
        """Capabilities should broadcast widely for discovery."""
        assert SemanticPheromoneKind.CAPABILITY.default_radius >= 1.0

    def test_capability_decays_slowly(self):
        """Capabilities should decay very slowly (stable)."""
        assert SemanticPheromoneKind.CAPABILITY.decay_rate <= 0.05


# =============================================================================
# L-gent Catalog Field Tests (Phase 4)
# =============================================================================


class TestCapabilityPayloads:
    """Tests for capability payload dataclasses."""

    def test_capability_payload_creation(self):
        """Test creating a CapabilityPayload."""
        payload = CapabilityPayload(
            agent_id="l-gent",
            capability_name="embed_text",
            input_type="str",
            output_type="list[float]",
            cost_estimate=0.001,
            tags=("embedding", "semantic"),
            description="Embed text into vector space",
            version="2.0",
        )

        assert payload.agent_id == "l-gent"
        assert payload.capability_name == "embed_text"
        assert payload.input_type == "str"
        assert payload.output_type == "list[float]"
        assert payload.cost_estimate == 0.001
        assert "embedding" in payload.tags
        assert payload.version == "2.0"

    def test_capability_payload_defaults(self):
        """Test CapabilityPayload default values."""
        payload = CapabilityPayload(
            agent_id="test",
            capability_name="test_cap",
            input_type="str",
            output_type="str",
        )

        assert payload.cost_estimate == 0.0
        assert payload.tags == ()
        assert payload.description == ""
        assert payload.version == "1.0"

    def test_deprecation_payload_creation(self):
        """Test creating a CapabilityDeprecationPayload."""
        payload = CapabilityDeprecationPayload(
            agent_id="l-gent",
            capability_name="old_embed",
            reason="Superseded by embed_v2",
            replacement="embed_v2",
            deprecation_date="2025-01-15",
        )

        assert payload.agent_id == "l-gent"
        assert payload.capability_name == "old_embed"
        assert payload.reason == "Superseded by embed_v2"
        assert payload.replacement == "embed_v2"

    def test_request_payload_creation(self):
        """Test creating a CapabilityRequestPayload."""
        payload = CapabilityRequestPayload(
            requester_id="f-gent",
            capability_pattern="embed*",
            urgency=0.8,
            input_type="str",
            output_type="list[float]",
            tags=("semantic",),
        )

        assert payload.requester_id == "f-gent"
        assert payload.capability_pattern == "embed*"
        assert payload.urgency == 0.8
        assert payload.input_type == "str"


class TestCatalogFieldEmitter:
    """Tests for CatalogFieldEmitter."""

    def test_emit_capability_registered(self):
        """Test emitting a capability registration."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)

        position = FieldCoordinate(domain="semantic")

        phero_id = emitter.emit_capability_registered(
            agent_id="psi-gent",
            capability_name="discover_metaphor",
            input_type="ProblemSpace",
            output_type="Functor[P,K]",
            position=position,
            cost_estimate=0.05,
            tags=("metaphor", "discovery"),
            description="Discover metaphors for problem spaces",
            version="1.2",
        )

        assert phero_id.startswith("phero-")
        assert field.pheromone_count == 1

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, CapabilityPayload)
        assert payload.agent_id == "psi-gent"
        assert payload.capability_name == "discover_metaphor"

    def test_emit_capability_full_intensity(self):
        """Test capability registration has full intensity."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate()

        emitter.emit_capability_registered(
            agent_id="test",
            capability_name="test_cap",
            input_type="str",
            output_type="str",
            position=position,
        )

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        assert pheromones[0].intensity == 1.0

    def test_emit_capability_deprecated(self):
        """Test emitting a capability deprecation."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_deprecated(
            agent_id="l-gent",
            capability_name="old_embed",
            reason="Use embed_v2 instead",
            position=position,
            replacement="embed_v2",
            deprecation_date="2025-01-15",
        )

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, CapabilityDeprecationPayload)
        assert payload.capability_name == "old_embed"
        assert payload.replacement == "embed_v2"

    def test_deprecation_has_lower_intensity(self):
        """Test deprecations have lower intensity than registrations."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate()

        emitter.emit_capability_registered("test", "cap1", "str", "str", position)
        emitter.emit_capability_deprecated("test", "cap2", "reason", position)

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        intensities = [p.intensity for p in pheromones]

        assert 1.0 in intensities  # Registration
        assert 0.8 in intensities  # Deprecation

    def test_emit_capability_updated(self):
        """Test emitting a capability update."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate()

        emitter.emit_capability_updated(
            agent_id="test",
            capability_name="test_cap",
            changes={"cost_estimate": 0.02, "version": "1.1"},
            position=position,
            new_version="1.1",
        )

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        assert len(pheromones) == 1

        # Update has dict payload, not CapabilityPayload
        payload = pheromones[0].payload
        assert payload["update_type"] == "modification"
        assert payload["new_version"] == "1.1"

    def test_emit_capability_request(self):
        """Test emitting a capability request."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_request(
            requester_id="f-gent",
            capability_pattern="embed*",
            urgency=0.9,
            position=position,
            input_type="str",
            tags=("semantic", "vector"),
        )

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        assert len(pheromones) == 1

        payload = pheromones[0].payload
        assert isinstance(payload, CapabilityRequestPayload)
        assert payload.requester_id == "f-gent"
        assert payload.capability_pattern == "embed*"

    def test_request_urgency_determines_intensity(self):
        """Test request urgency determines signal intensity."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        position = FieldCoordinate()

        emitter.emit_capability_request("req1", "cap*", 0.3, position)
        emitter.emit_capability_request("req2", "cap*", 0.9, position)

        pheromones = field.get_all(SemanticPheromoneKind.CAPABILITY)
        intensities = sorted([p.intensity for p in pheromones])

        assert intensities == [0.3, 0.9]


class TestCatalogFieldSensor:
    """Tests for CatalogFieldSensor."""

    def test_sense_capabilities(self):
        """Test sensing capabilities."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("agent_a", "cap_a", "str", "str", position)
        emitter.emit_capability_registered("agent_b", "cap_b", "int", "int", position)

        capabilities = sensor.sense_capabilities(position)

        assert len(capabilities) == 2
        names = {c.capability_name for c in capabilities}
        assert names == {"cap_a", "cap_b"}

    def test_sense_by_tags(self):
        """Test sensing capabilities by tags."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered(
            "agent_a",
            "embed",
            "str",
            "list[float]",
            position,
            tags=("embedding", "semantic"),
        )
        emitter.emit_capability_registered(
            "agent_b",
            "parse",
            "str",
            "dict",
            position,
            tags=("parsing", "json"),
        )

        # Sense by embedding tag
        results = sensor.sense_by_tags(position, ("embedding",))
        assert len(results) == 1
        assert results[0].capability_name == "embed"

        # Sense by non-matching tag
        empty = sensor.sense_by_tags(position, ("nonexistent",))
        assert len(empty) == 0

    def test_sense_by_tags_partial_match(self):
        """Test sensing by tags with partial matches."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered(
            "a", "cap_a", "str", "str", position, tags=("x", "y")
        )
        emitter.emit_capability_registered(
            "b", "cap_b", "str", "str", position, tags=("y", "z")
        )

        # Tag "y" matches both
        results = sensor.sense_by_tags(position, ("y",))
        assert len(results) == 2

    def test_sense_deprecations(self):
        """Test sensing deprecation notices."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("a", "new_cap", "str", "str", position)
        emitter.emit_capability_deprecated("a", "old_cap", "Retired", position)

        deprecations = sensor.sense_deprecations(position)

        assert len(deprecations) == 1
        assert deprecations[0].capability_name == "old_cap"

    def test_sense_capability_requests(self):
        """Test sensing capability requests."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("a", "cap", "str", "str", position)
        emitter.emit_capability_request("requester", "need_*", 0.8, position)

        requests = sensor.sense_capability_requests(position)

        assert len(requests) == 1
        assert requests[0].requester_id == "requester"
        assert requests[0].capability_pattern == "need_*"

    def test_find_capability(self):
        """Test finding a specific capability by name."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("a", "cap_a", "str", "str", position)
        emitter.emit_capability_registered("b", "cap_b", "int", "int", position)

        found = sensor.find_capability("cap_b", position)
        assert found is not None
        assert found.capability_name == "cap_b"
        assert found.agent_id == "b"

        not_found = sensor.find_capability("nonexistent", position)
        assert not_found is None

    def test_get_agent_capabilities(self):
        """Test getting all capabilities from a specific agent."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("psi", "cap1", "str", "str", position)
        emitter.emit_capability_registered("psi", "cap2", "int", "int", position)
        emitter.emit_capability_registered("forge", "cap3", "str", "dict", position)

        psi_caps = sensor.get_agent_capabilities("psi", position)

        assert len(psi_caps) == 2
        names = {c.capability_name for c in psi_caps}
        assert names == {"cap1", "cap2"}

    def test_has_capability(self):
        """Test checking if a capability exists."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("a", "exists", "str", "str", position)

        assert sensor.has_capability("exists", position) is True
        assert sensor.has_capability("not_exists", position) is False

    def test_get_capability_count(self):
        """Test getting total capability count."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        assert sensor.get_capability_count() == 0

        emitter.emit_capability_registered("a", "cap1", "str", "str", position)
        emitter.emit_capability_registered("b", "cap2", "int", "int", position)

        assert sensor.get_capability_count() == 2

    def test_capability_count_excludes_non_capabilities(self):
        """Test capability count only counts CapabilityPayload."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        # Mix of payload types
        emitter.emit_capability_registered("a", "cap", "str", "str", position)
        emitter.emit_capability_deprecated("a", "old", "reason", position)
        emitter.emit_capability_request("req", "pattern", 0.5, position)

        # Only counts CapabilityPayload, not deprecations or requests
        assert sensor.get_capability_count() == 1


class TestCatalogIntegration:
    """Integration tests for L-gent catalog field coordination."""

    def test_emitter_sensor_roundtrip(self):
        """Test complete emitter→sensor roundtrip."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field, agent_id="l-gent")
        sensor = create_catalog_sensor(field, agent_id="discovery")

        position = FieldCoordinate(domain="semantic")

        # L-gent registers capabilities
        emitter.emit_capability_registered(
            agent_id="psi-gent",
            capability_name="metaphor_discovery",
            input_type="ProblemSpace",
            output_type="Functor[P,K]",
            position=position,
            tags=("metaphor", "category-theory"),
            description="Discover metaphorical mappings",
        )

        # Other agent discovers it
        capabilities = sensor.sense_capabilities(position)
        assert len(capabilities) == 1
        assert capabilities[0].capability_name == "metaphor_discovery"
        assert "metaphor" in capabilities[0].tags

    def test_capability_discovery_workflow(self):
        """Test full capability discovery workflow."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        # 1. Agent requests a capability
        emitter.emit_capability_request(
            requester_id="f-gent",
            capability_pattern="embed*",
            urgency=0.9,
            position=position,
            tags=("semantic",),
        )

        # 2. Check unfulfilled requests
        requests = sensor.sense_capability_requests(position)
        assert len(requests) == 1

        # 3. L-gent registers matching capability
        emitter.emit_capability_registered(
            agent_id="l-gent",
            capability_name="embed_text",
            input_type="str",
            output_type="list[float]",
            position=position,
            tags=("semantic", "embedding"),
        )

        # 4. Requester can now find it
        found = sensor.find_capability("embed_text", position)
        assert found is not None
        assert found.agent_id == "l-gent"

    def test_capability_lifecycle(self):
        """Test capability registration → update → deprecation."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        # 1. Register
        emitter.emit_capability_registered(
            "agent",
            "capability_v1",
            "str",
            "str",
            position,
            version="1.0",
        )
        assert sensor.get_capability_count() == 1

        # 2. Update (new emission, doesn't replace old)
        emitter.emit_capability_updated(
            "agent",
            "capability_v1",
            changes={"version": "1.1"},
            position=position,
            new_version="1.1",
        )

        # 3. Deprecate
        emitter.emit_capability_deprecated(
            "agent",
            "capability_v1",
            reason="Replaced by v2",
            position=position,
            replacement="capability_v2",
        )

        deprecations = sensor.sense_deprecations(position)
        assert len(deprecations) == 1
        assert deprecations[0].replacement == "capability_v2"

    def test_decoupled_agents_via_field(self):
        """Test agents discover each other via field without direct coupling."""
        field = create_semantic_field()
        position = FieldCoordinate(domain="semantic")

        # Agent A registers capability (doesn't know B)
        emitter_a = create_catalog_emitter(field, agent_id="agent_a")
        emitter_a.emit_capability_registered(
            agent_id="agent_a",
            capability_name="transform_data",
            input_type="RawData",
            output_type="CleanData",
            position=position,
            tags=("data", "transformation"),
        )

        # Agent B senses capability (doesn't know A)
        sensor_b = create_catalog_sensor(field, agent_id="agent_b")
        capabilities = sensor_b.sense_by_tags(position, ("transformation",))

        assert len(capabilities) == 1
        assert capabilities[0].agent_id == "agent_a"

    def test_capability_decay_affects_discovery(self):
        """Test capability decay affects discoverability."""
        field = create_semantic_field()
        emitter = create_catalog_emitter(field)
        sensor = create_catalog_sensor(field)

        position = FieldCoordinate(domain="semantic")

        emitter.emit_capability_registered("agent", "test_cap", "str", "str", position)

        # Initially discoverable
        assert sensor.has_capability("test_cap", position)

        # CAPABILITY has very slow decay (0.02), needs many ticks
        # Decay formula: intensity *= exp(-0.02 * dt)
        # Need intensity < 0.01 to expire
        # 1.0 * exp(-0.02 * t) < 0.01
        # exp(-0.02 * t) < 0.01
        # -0.02 * t < ln(0.01) ≈ -4.6
        # t > 230
        for _ in range(300):
            field.tick(1.0)

        assert not sensor.has_capability("test_cap", position)
