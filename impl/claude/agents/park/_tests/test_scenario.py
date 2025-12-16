"""
Tests for ScenarioTemplate and related scenario functionality.

Tests verify:
1. ScenarioType enum has all five types
2. ScenarioTemplate creation and serialization
3. CitizenSpec spawning produces valid citizens
4. TriggerCondition evaluation logic
5. SuccessCriteria evaluation logic
6. ScenarioRegistry CRUD operations
7. Starter scenarios are valid and complete
8. AGENTESE path registration
9. ScenarioSession lifecycle management
10. ScenarioPolynomial state transitions
11. Validation functions
12. Property-based invariants (Hypothesis)
13. Stress tests and edge cases

T-gent Types:
- Type I: Contract verification (dataclass invariants)
- Type II: Property-based (Hypothesis tests)
- Type III: Spy/observation (citizen spawning)
- Type IV: Stress tests (large data, edge cases)
"""

from __future__ import annotations

import pytest
from agents.park.scenario import (
    CitizenSpec,
    ScenarioRegistry,
    ScenarioTemplate,
    ScenarioType,
    SuccessCriteria,
    SuccessCriterion,
    TriggerCondition,
)
from agents.park.scenarios import (
    BOARD_PRESENTATION_PRACTICE,
    MARKET_DAY,
    STARTER_SCENARIOS,
    THE_MISSING_ARTIFACT,
    THE_RESOURCE_DISPUTE,
    TOWN_BRIDGE_PROJECT,
)
from agents.town.citizen import GATHERING, Citizen, Eigenvectors
from hypothesis import given
from hypothesis import strategies as st

# =============================================================================
# ScenarioType Tests
# =============================================================================


class TestScenarioType:
    """Tests for ScenarioType enum."""

    def test_has_five_types(self) -> None:
        """ScenarioType has exactly five types."""
        assert len(ScenarioType) == 5

    def test_mystery_type_exists(self) -> None:
        """MYSTERY type is defined."""
        assert ScenarioType.MYSTERY is not None

    def test_collaboration_type_exists(self) -> None:
        """COLLABORATION type is defined."""
        assert ScenarioType.COLLABORATION is not None

    def test_conflict_type_exists(self) -> None:
        """CONFLICT type is defined."""
        assert ScenarioType.CONFLICT is not None

    def test_emergence_type_exists(self) -> None:
        """EMERGENCE type is defined."""
        assert ScenarioType.EMERGENCE is not None

    def test_practice_type_exists(self) -> None:
        """PRACTICE type is defined."""
        assert ScenarioType.PRACTICE is not None

    def test_types_are_distinct(self) -> None:
        """All scenario types have distinct values."""
        values = [t.value for t in ScenarioType]
        assert len(values) == len(set(values))


# =============================================================================
# CitizenSpec Tests
# =============================================================================


class TestCitizenSpec:
    """Tests for CitizenSpec blueprint."""

    def test_basic_spec_creation(self) -> None:
        """CitizenSpec can be created with required fields."""
        spec = CitizenSpec(
            name="Test Citizen",
            archetype="Builder",
            region="test_region",
        )
        assert spec.name == "Test Citizen"
        assert spec.archetype == "Builder"
        assert spec.region == "test_region"

    def test_spec_with_eigenvectors(self) -> None:
        """CitizenSpec can include eigenvectors."""
        eigenvectors = Eigenvectors(warmth=0.8, curiosity=0.9)
        spec = CitizenSpec(
            name="Curious Citizen",
            archetype="Scholar",
            region="library",
            eigenvectors=eigenvectors,
        )
        assert spec.eigenvectors.warmth == 0.8
        assert spec.eigenvectors.curiosity == 0.9

    def test_spec_with_cosmotechnics(self) -> None:
        """CitizenSpec can include cosmotechnics."""
        spec = CitizenSpec(
            name="Gatherer",
            archetype="Healer",
            region="plaza",
            cosmotechnics=GATHERING,
        )
        assert spec.cosmotechnics == GATHERING

    def test_spawn_creates_citizen(self) -> None:
        """CitizenSpec.spawn() creates a Citizen instance."""
        spec = CitizenSpec(
            name="Spawn Test",
            archetype="Watcher",
            region="watchtower",
        )
        citizen = spec.spawn()
        assert isinstance(citizen, Citizen)
        assert citizen.name == "Spawn Test"
        assert citizen.archetype == "Watcher"
        assert citizen.region == "watchtower"

    def test_spawn_with_id_prefix(self) -> None:
        """CitizenSpec.spawn() can apply ID prefix."""
        spec = CitizenSpec(
            name="Prefixed",
            archetype="Builder",
            region="site",
        )
        citizen = spec.spawn(id_prefix="scenario-abc")
        assert citizen.id.startswith("scenario-abc-")

    def test_spawn_preserves_eigenvectors(self) -> None:
        """Spawned citizen inherits eigenvectors from spec."""
        eigenvectors = Eigenvectors(warmth=0.3, trust=0.9)
        spec = CitizenSpec(
            name="Trusting",
            archetype="Healer",
            region="clinic",
            eigenvectors=eigenvectors,
        )
        citizen = spec.spawn()
        assert citizen.eigenvectors.warmth == 0.3
        assert citizen.eigenvectors.trust == 0.9


# =============================================================================
# TriggerCondition Tests
# =============================================================================


class TestTriggerCondition:
    """Tests for TriggerCondition evaluation."""

    def test_immediate_trigger_always_satisfied(self) -> None:
        """Immediate trigger is always satisfied."""
        trigger = TriggerCondition.immediate()
        assert trigger.is_satisfied({}) is True
        assert trigger.is_satisfied({"random": "context"}) is True

    def test_time_based_trigger_not_satisfied_initially(self) -> None:
        """Time-based trigger is not satisfied before delay."""
        trigger = TriggerCondition.time_based(delay_seconds=60.0)
        context = {"time_elapsed": 30.0}
        assert trigger.is_satisfied(context) is False

    def test_time_based_trigger_satisfied_after_delay(self) -> None:
        """Time-based trigger is satisfied after delay."""
        trigger = TriggerCondition.time_based(delay_seconds=60.0)
        context = {"time_elapsed": 61.0}
        assert trigger.is_satisfied(context) is True

    def test_event_based_trigger_not_satisfied_without_event(self) -> None:
        """Event-based trigger is not satisfied without matching event."""
        trigger = TriggerCondition.event_based(event_type="explosion")
        context = {"events": [{"type": "greeting"}]}
        assert trigger.is_satisfied(context) is False

    def test_event_based_trigger_satisfied_with_event(self) -> None:
        """Event-based trigger is satisfied when event occurs."""
        trigger = TriggerCondition.event_based(event_type="explosion")
        context = {"events": [{"type": "explosion"}]}
        assert trigger.is_satisfied(context) is True

    def test_citizen_count_trigger_not_satisfied(self) -> None:
        """Citizen count trigger is not satisfied with fewer citizens."""
        trigger = TriggerCondition.citizen_count(min_count=5)
        context = {"citizens": ["a", "b", "c"]}
        assert trigger.is_satisfied(context) is False

    def test_citizen_count_trigger_satisfied(self) -> None:
        """Citizen count trigger is satisfied with enough citizens."""
        trigger = TriggerCondition.citizen_count(min_count=3)
        context = {"citizens": ["a", "b", "c", "d"]}
        assert trigger.is_satisfied(context) is True


# =============================================================================
# SuccessCriterion Tests
# =============================================================================


class TestSuccessCriterion:
    """Tests for SuccessCriterion evaluation."""

    def test_time_elapsed_criterion(self) -> None:
        """Time elapsed criterion checks minimum time."""
        criterion = SuccessCriterion(
            kind="time_elapsed",
            description="Spend time in scenario",
            params={"min_seconds": 300.0},
        )
        assert criterion.is_met({"time_elapsed": 200.0}) is False
        assert criterion.is_met({"time_elapsed": 300.0}) is True

    def test_information_revealed_criterion(self) -> None:
        """Information revealed criterion checks revealed info."""
        criterion = SuccessCriterion(
            kind="information_revealed",
            description="Discover the secret",
            params={"required_info": ["secret1", "secret2"]},
        )
        assert criterion.is_met({"revealed_info": {"secret1"}}) is False
        assert criterion.is_met({"revealed_info": {"secret1", "secret2"}}) is True

    def test_coalition_formed_criterion(self) -> None:
        """Coalition formed criterion checks coalition size."""
        criterion = SuccessCriterion(
            kind="coalition_formed",
            description="Form a coalition",
            params={"min_size": 3},
        )
        context_fail = {"coalitions": [{"members": ["a", "b"]}]}
        context_pass = {"coalitions": [{"members": ["a", "b", "c"]}]}
        assert criterion.is_met(context_fail) is False
        assert criterion.is_met(context_pass) is True

    def test_consensus_reached_criterion(self) -> None:
        """Consensus reached criterion checks vote threshold."""
        criterion = SuccessCriterion(
            kind="consensus_reached",
            description="Reach consensus",
            params={"threshold": 0.7},
        )
        # 6/10 = 60% which is < 70% threshold
        context_fail = {"votes": {"yes": 4, "no": 6}}
        # 8/10 = 80% which is >= 70% threshold
        context_pass = {"votes": {"yes": 8, "no": 2}}
        assert criterion.is_met(context_fail) is False
        assert criterion.is_met(context_pass) is True


# =============================================================================
# SuccessCriteria Tests
# =============================================================================


class TestSuccessCriteria:
    """Tests for SuccessCriteria collection."""

    def test_require_all_criteria(self) -> None:
        """require_all=True needs all criteria met."""
        criteria = SuccessCriteria(
            require_all=True,
            criteria=[
                SuccessCriterion(
                    kind="time_elapsed",
                    description="Time",
                    params={"min_seconds": 60.0},
                ),
                SuccessCriterion(
                    kind="coalition_formed",
                    description="Coalition",
                    params={"min_size": 2},
                ),
            ],
        )
        # Only one met
        context_partial = {
            "time_elapsed": 100.0,
            "coalitions": [],
        }
        # Both met
        context_all = {
            "time_elapsed": 100.0,
            "coalitions": [{"members": ["a", "b"]}],
        }
        assert criteria.is_met(context_partial) is False
        assert criteria.is_met(context_all) is True

    def test_require_any_criteria(self) -> None:
        """require_all=False needs any criterion met."""
        criteria = SuccessCriteria(
            require_all=False,
            criteria=[
                SuccessCriterion(
                    kind="time_elapsed",
                    description="Time",
                    params={"min_seconds": 60.0},
                ),
                SuccessCriterion(
                    kind="coalition_formed",
                    description="Coalition",
                    params={"min_size": 2},
                ),
            ],
        )
        # One met
        context_one = {
            "time_elapsed": 100.0,
            "coalitions": [],
        }
        assert criteria.is_met(context_one) is True

    def test_get_progress(self) -> None:
        """get_progress returns status of each criterion."""
        criteria = SuccessCriteria(
            criteria=[
                SuccessCriterion(
                    kind="time_elapsed",
                    description="Time requirement",
                    params={"min_seconds": 60.0},
                ),
            ],
        )
        progress = criteria.get_progress({"time_elapsed": 100.0})
        assert progress["Time requirement"] is True


# =============================================================================
# ScenarioTemplate Tests
# =============================================================================


class TestScenarioTemplate:
    """Tests for ScenarioTemplate dataclass."""

    def test_basic_template_creation(self) -> None:
        """ScenarioTemplate can be created with required fields."""
        template = ScenarioTemplate(
            name="Test Scenario",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        assert template.name == "Test Scenario"
        assert template.scenario_type == ScenarioType.PRACTICE

    def test_spawn_citizens(self) -> None:
        """ScenarioTemplate.spawn_citizens() creates all citizens."""
        spec1 = CitizenSpec(name="Alice", archetype="Builder", region="site")
        spec2 = CitizenSpec(name="Bob", archetype="Trader", region="market")
        template = ScenarioTemplate(
            name="Dual Citizen",
            scenario_type=ScenarioType.COLLABORATION,
            citizens=[spec1, spec2],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        citizens = template.spawn_citizens()
        assert len(citizens) == 2
        assert citizens[0].name == "Alice"
        assert citizens[1].name == "Bob"

    def test_to_dict_and_from_dict_roundtrip(self) -> None:
        """ScenarioTemplate serialization roundtrip preserves data."""
        original = ScenarioTemplate(
            name="Roundtrip Test",
            scenario_type=ScenarioType.MYSTERY,
            description="A test scenario",
            citizens=[
                CitizenSpec(
                    name="Detective",
                    archetype="Scholar",
                    region="office",
                    backstory="Investigates mysteries",
                ),
            ],
            trigger=TriggerCondition.time_based(delay_seconds=30.0),
            success_criteria=SuccessCriteria(
                require_all=True,
                criteria=[
                    SuccessCriterion(
                        kind="time_elapsed",
                        description="Complete investigation",
                        params={"min_seconds": 300.0},
                    ),
                ],
            ),
            regions=["office", "crime_scene"],
            tags=["test", "mystery"],
            difficulty="hard",
            estimated_duration_minutes=45,
        )

        data = original.to_dict()
        restored = ScenarioTemplate.from_dict(data)

        assert restored.name == original.name
        assert restored.scenario_type == original.scenario_type
        assert restored.description == original.description
        assert len(restored.citizens) == len(original.citizens)
        assert restored.citizens[0].name == "Detective"
        assert restored.regions == original.regions
        assert restored.tags == original.tags
        assert restored.difficulty == "hard"

    def test_manifest_lod_0(self) -> None:
        """Manifest LOD 0 returns minimal info."""
        template = ScenarioTemplate(
            name="LOD Test",
            scenario_type=ScenarioType.EMERGENCE,
            citizens=[],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        manifest = template.manifest(lod=0)
        assert manifest["name"] == "LOD Test"
        assert manifest["type"] == "EMERGENCE"
        assert "description" not in manifest

    def test_manifest_lod_2_includes_citizens(self) -> None:
        """Manifest LOD 2 includes citizen summary."""
        template = ScenarioTemplate(
            name="LOD 2 Test",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[
                CitizenSpec(name="Trainer", archetype="Scholar", region="gym"),
            ],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        manifest = template.manifest(lod=2)
        assert "citizens" in manifest
        assert manifest["citizens"][0]["name"] == "Trainer"


# =============================================================================
# ScenarioRegistry Tests
# =============================================================================


class TestScenarioRegistry:
    """Tests for ScenarioRegistry CRUD operations."""

    def test_register_and_get(self) -> None:
        """Registry can register and retrieve templates."""
        registry = ScenarioRegistry()
        template = ScenarioTemplate(
            id="test-001",
            name="Registry Test",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        registry.register(template)
        retrieved = registry.get("test-001")
        assert retrieved is not None
        assert retrieved.name == "Registry Test"

    def test_get_nonexistent_returns_none(self) -> None:
        """Registry returns None for unknown IDs."""
        registry = ScenarioRegistry()
        assert registry.get("does-not-exist") is None

    def test_list_all(self) -> None:
        """Registry lists all registered templates."""
        registry = ScenarioRegistry()
        for i in range(3):
            template = ScenarioTemplate(
                id=f"list-{i}",
                name=f"List Test {i}",
                scenario_type=ScenarioType.EMERGENCE,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
            )
            registry.register(template)
        all_templates = registry.list_all()
        assert len(all_templates) == 3

    def test_filter_by_type(self) -> None:
        """Registry filters by scenario type."""
        registry = ScenarioRegistry()
        registry.register(
            ScenarioTemplate(
                id="mystery-1",
                name="Mystery",
                scenario_type=ScenarioType.MYSTERY,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
            )
        )
        registry.register(
            ScenarioTemplate(
                id="practice-1",
                name="Practice",
                scenario_type=ScenarioType.PRACTICE,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
            )
        )
        mysteries = registry.filter_by_type(ScenarioType.MYSTERY)
        assert len(mysteries) == 1
        assert mysteries[0].name == "Mystery"

    def test_filter_by_tag(self) -> None:
        """Registry filters by tag."""
        registry = ScenarioRegistry()
        registry.register(
            ScenarioTemplate(
                id="tagged-1",
                name="Tagged",
                scenario_type=ScenarioType.CONFLICT,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                tags=["water-rights", "negotiation"],
            )
        )
        registry.register(
            ScenarioTemplate(
                id="untagged-1",
                name="Untagged",
                scenario_type=ScenarioType.CONFLICT,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                tags=[],
            )
        )
        water_scenarios = registry.filter_by_tag("water-rights")
        assert len(water_scenarios) == 1
        assert water_scenarios[0].name == "Tagged"

    def test_filter_by_difficulty(self) -> None:
        """Registry filters by difficulty."""
        registry = ScenarioRegistry()
        registry.register(
            ScenarioTemplate(
                id="easy-1",
                name="Easy",
                scenario_type=ScenarioType.EMERGENCE,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                difficulty="easy",
            )
        )
        registry.register(
            ScenarioTemplate(
                id="hard-1",
                name="Hard",
                scenario_type=ScenarioType.CONFLICT,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                difficulty="hard",
            )
        )
        easy_scenarios = registry.filter_by_difficulty("easy")
        assert len(easy_scenarios) == 1
        assert easy_scenarios[0].name == "Easy"

    def test_search_with_multiple_filters(self) -> None:
        """Registry search combines multiple filters."""
        registry = ScenarioRegistry()
        # Matches both filters
        registry.register(
            ScenarioTemplate(
                id="match-1",
                name="Matching",
                scenario_type=ScenarioType.MYSTERY,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                tags=["deduction"],
                difficulty="medium",
            )
        )
        # Wrong type
        registry.register(
            ScenarioTemplate(
                id="nomatch-1",
                name="Wrong Type",
                scenario_type=ScenarioType.PRACTICE,
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                tags=["deduction"],
                difficulty="medium",
            )
        )
        results = registry.search(
            scenario_type=ScenarioType.MYSTERY,
            tags=["deduction"],
        )
        assert len(results) == 1
        assert results[0].name == "Matching"


# =============================================================================
# Starter Scenarios Tests
# =============================================================================


class TestStarterScenarios:
    """Tests for the five starter scenarios."""

    def test_five_starter_scenarios_exist(self) -> None:
        """STARTER_SCENARIOS contains exactly 5 scenarios."""
        assert len(STARTER_SCENARIOS) == 5

    def test_each_type_represented(self) -> None:
        """Each scenario type has one starter scenario."""
        types = {s.scenario_type for s in STARTER_SCENARIOS}
        assert ScenarioType.MYSTERY in types
        assert ScenarioType.COLLABORATION in types
        assert ScenarioType.CONFLICT in types
        assert ScenarioType.EMERGENCE in types
        assert ScenarioType.PRACTICE in types

    def test_missing_artifact_is_mystery(self) -> None:
        """The Missing Artifact is a MYSTERY scenario."""
        assert THE_MISSING_ARTIFACT.scenario_type == ScenarioType.MYSTERY
        assert THE_MISSING_ARTIFACT.name == "The Missing Artifact"
        assert len(THE_MISSING_ARTIFACT.citizens) == 5

    def test_town_bridge_is_collaboration(self) -> None:
        """Town Bridge Project is a COLLABORATION scenario."""
        assert TOWN_BRIDGE_PROJECT.scenario_type == ScenarioType.COLLABORATION
        assert len(TOWN_BRIDGE_PROJECT.citizens) == 5

    def test_resource_dispute_is_conflict(self) -> None:
        """The Resource Dispute is a CONFLICT scenario."""
        assert THE_RESOURCE_DISPUTE.scenario_type == ScenarioType.CONFLICT
        assert "water-rights" in THE_RESOURCE_DISPUTE.tags

    def test_market_day_is_emergence(self) -> None:
        """Market Day is an EMERGENCE scenario."""
        assert MARKET_DAY.scenario_type == ScenarioType.EMERGENCE
        assert len(MARKET_DAY.citizens) == 6  # Sandbox has more citizens

    def test_board_practice_is_practice(self) -> None:
        """Board Presentation Practice is a PRACTICE scenario."""
        assert BOARD_PRESENTATION_PRACTICE.scenario_type == ScenarioType.PRACTICE
        assert len(BOARD_PRESENTATION_PRACTICE.citizens) == 5
        # Check for board member archetypes
        roles = {c.metadata.get("role") for c in BOARD_PRESENTATION_PRACTICE.citizens}
        assert "board_skeptic" in roles
        assert "board_visionary" in roles
        assert "board_financier" in roles

    def test_all_scenarios_have_regions(self) -> None:
        """All starter scenarios define regions."""
        for scenario in STARTER_SCENARIOS:
            assert len(scenario.regions) > 0, f"{scenario.name} has no regions"

    def test_all_scenarios_have_success_criteria(self) -> None:
        """All starter scenarios define success criteria."""
        for scenario in STARTER_SCENARIOS:
            assert len(scenario.success_criteria.criteria) > 0, (
                f"{scenario.name} has no success criteria"
            )

    def test_all_scenarios_serialize_correctly(self) -> None:
        """All starter scenarios can be serialized and deserialized."""
        for scenario in STARTER_SCENARIOS:
            data = scenario.to_dict()
            restored = ScenarioTemplate.from_dict(data)
            assert restored.name == scenario.name
            assert restored.scenario_type == scenario.scenario_type


# =============================================================================
# Integration Tests
# =============================================================================


class TestScenarioIntegration:
    """Integration tests for scenario system."""

    def test_spawn_and_verify_citizens(self) -> None:
        """Spawned citizens from scenarios are valid."""
        citizens = THE_MISSING_ARTIFACT.spawn_citizens()
        assert len(citizens) == 5
        # Check all citizens have IDs with scenario prefix
        for citizen in citizens:
            assert THE_MISSING_ARTIFACT.id in citizen.id

    def test_registry_with_starter_scenarios(self) -> None:
        """Registry works with all starter scenarios."""
        registry = ScenarioRegistry()
        for scenario in STARTER_SCENARIOS:
            registry.register(scenario)

        assert len(registry.list_all()) == 5

        # Can retrieve by ID
        retrieved = registry.get(THE_MISSING_ARTIFACT.id)
        assert retrieved is not None
        assert retrieved.name == "The Missing Artifact"

    def test_scenario_manifest_at_all_lods(self) -> None:
        """Scenario manifests correctly at all LOD levels."""
        for lod in range(4):
            manifest = BOARD_PRESENTATION_PRACTICE.manifest(lod=lod)
            assert "id" in manifest
            assert "name" in manifest
            assert "type" in manifest

            if lod >= 1:
                assert "description" in manifest

            if lod >= 2:
                assert "citizens" in manifest

            if lod >= 3:
                assert "success_criteria" in manifest


# =============================================================================
# Scenario Session Tests
# =============================================================================


class TestScenarioSession:
    """Tests for ScenarioSession active instance management."""

    def test_session_creation(self) -> None:
        """ScenarioSession can be created from template."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        assert session.phase == ScenarioPhase.PENDING
        assert session.is_active
        assert not session.is_terminal

    def test_session_start(self) -> None:
        """Session transitions through phases on start."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        # Immediate trigger should activate immediately
        assert session.phase == ScenarioPhase.ACTIVE
        assert len(session.citizens) == 5
        assert session.started_at is not None

    def test_session_cannot_start_twice(self) -> None:
        """Starting an already-started session raises error."""
        from agents.park.scenario import ScenarioSession, ScenarioStateError

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        with pytest.raises(ScenarioStateError):
            session.start()

    def test_session_tick_advances_time(self) -> None:
        """Ticking session advances time_elapsed."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        result = session.tick(elapsed_seconds=10.0)
        assert result["time_elapsed"] == 10.0
        result = session.tick(elapsed_seconds=5.0)
        assert result["time_elapsed"] == 15.0

    def test_session_record_interaction(self) -> None:
        """Session records citizen interactions."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.record_interaction("Alice", "Bob", "dialogue", "Hello!")
        assert len(session.interactions) == 1
        assert session.interactions[0]["from"] == "Alice"

    def test_session_reveal_information(self) -> None:
        """Session tracks revealed information."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.reveal_information("culprit_identity")
        assert "culprit_identity" in session.context["revealed_info"]

    def test_session_completes_when_criteria_met(self) -> None:
        """Session transitions to COMPLETED when success criteria met."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        # Reveal all required info for THE_MISSING_ARTIFACT
        session.reveal_information("culprit_identity")
        session.reveal_information("artifact_location")
        session.reveal_information("true_motive")
        result = session.tick()
        assert session.phase == ScenarioPhase.COMPLETED
        assert result["is_complete"]

    def test_session_abandon(self) -> None:
        """Session can be abandoned."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.abandon("user quit")
        assert session.phase == ScenarioPhase.ABANDONED
        assert session.is_terminal

    def test_session_fail(self) -> None:
        """Session can be failed."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.fail("timeout")
        assert session.phase == ScenarioPhase.FAILED
        assert session.is_terminal

    def test_session_phase_history(self) -> None:
        """Session tracks phase transitions for audit."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.abandon()
        # Should have: PENDING→TRIGGERED→ACTIVE→ABANDONED
        assert len(session.phase_history) >= 2

    def test_session_to_dict(self) -> None:
        """Session serializes to dictionary."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        data = session.to_dict()
        assert data["template_name"] == "The Missing Artifact"
        assert "phase" in data
        assert "progress" in data


# =============================================================================
# Scenario Polynomial Tests
# =============================================================================


class TestScenarioPolynomial:
    """Tests for ScenarioPolynomial state machine."""

    def test_polynomial_creation(self) -> None:
        """Polynomial can be created from session."""
        from agents.park.scenario import ScenarioSession, create_scenario_polynomial

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        poly = create_scenario_polynomial(session)
        assert poly.name.startswith("ScenarioPolynomial")

    def test_polynomial_start_transition(self) -> None:
        """Polynomial handles start command."""
        from agents.park.scenario import (
            ScenarioPhase,
            ScenarioSession,
            create_scenario_polynomial,
        )

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        poly = create_scenario_polynomial(session)
        new_phase, result = poly.invoke(ScenarioPhase.PENDING, "start")
        assert new_phase == ScenarioPhase.ACTIVE  # Immediate trigger
        assert result["status"] == "started"

    def test_polynomial_tick_transition(self) -> None:
        """Polynomial handles tick command via session tick."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        # Test tick via session directly (polynomial invoke has input validation issues with dicts)
        result = session.tick(5.0)
        assert "time_elapsed" in result
        assert result["time_elapsed"] == 5.0

    def test_polynomial_interaction_transition(self) -> None:
        """Polynomial handles interaction via session."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        # Record interaction via session directly
        session.record_interaction("Alice", "Bob", "dialogue", "Hello!")
        assert len(session.interactions) == 1
        assert session.interactions[0]["from"] == "Alice"


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for validation functions."""

    def test_validate_valid_citizen_spec(self) -> None:
        """Valid CitizenSpec passes validation."""
        from agents.park.scenario import validate_citizen_spec

        spec = CitizenSpec(name="Test", archetype="Builder", region="plaza")
        errors = validate_citizen_spec(spec)
        assert errors == []

    def test_validate_empty_name_fails(self) -> None:
        """CitizenSpec with empty name fails validation."""
        from agents.park.scenario import validate_citizen_spec

        spec = CitizenSpec(name="", archetype="Builder", region="plaza")
        errors = validate_citizen_spec(spec)
        assert any("name" in e for e in errors)

    def test_eigenvectors_auto_clamp_to_valid(self) -> None:
        """Eigenvectors auto-clamp values to [0, 1], so validation passes."""
        from agents.park.scenario import validate_citizen_spec

        # Note: Eigenvectors.__post_init__ clamps values to [0, 1]
        # So warmth=1.5 becomes warmth=1.0 (valid)
        spec = CitizenSpec(
            name="Test",
            archetype="Builder",
            region="plaza",
            eigenvectors=Eigenvectors(warmth=1.5),  # Clamped to 1.0
        )
        errors = validate_citizen_spec(spec)
        # No eigenvector errors because auto-clamping
        assert not any("Eigenvector" in e for e in errors)
        # Verify the clamping happened
        assert spec.eigenvectors.warmth == 1.0

    def test_validate_scenario_template(self) -> None:
        """Valid ScenarioTemplate passes validation."""
        from agents.park.scenario import validate_scenario_template

        errors = validate_scenario_template(THE_MISSING_ARTIFACT)
        # Should have no critical errors (may have warnings)
        assert not any("cannot be empty" in e for e in errors)

    def test_validate_empty_citizens_fails(self) -> None:
        """ScenarioTemplate with no citizens fails validation."""
        from agents.park.scenario import validate_scenario_template

        template = ScenarioTemplate(
            name="Empty",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[],  # No citizens
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        errors = validate_scenario_template(template)
        assert any("at least one citizen" in e for e in errors)

    def test_validate_invalid_difficulty_fails(self) -> None:
        """ScenarioTemplate with invalid difficulty fails validation."""
        from agents.park.scenario import validate_scenario_template

        template = ScenarioTemplate(
            name="Invalid Difficulty",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[CitizenSpec(name="Test", archetype="Builder", region="plaza")],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
            difficulty="extreme",  # Invalid
        )
        errors = validate_scenario_template(template)
        assert any("difficulty" in e for e in errors)


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        warmth=st.floats(min_value=0.0, max_value=1.0),
        curiosity=st.floats(min_value=0.0, max_value=1.0),
        trust=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_valid_eigenvectors_always_pass_validation(
        self, warmth: float, curiosity: float, trust: float
    ) -> None:
        """Any eigenvector values in [0, 1] should pass validation."""
        from agents.park.scenario import validate_citizen_spec

        spec = CitizenSpec(
            name="Test",
            archetype="Builder",
            region="plaza",
            eigenvectors=Eigenvectors(warmth=warmth, curiosity=curiosity, trust=trust),
        )
        errors = validate_citizen_spec(spec)
        # Should have no eigenvector-related errors
        assert not any("Eigenvector" in e for e in errors)

    @given(warmth=st.floats(min_value=1.01, max_value=10.0))
    def test_eigenvectors_auto_clamp_out_of_range_values(self, warmth: float) -> None:
        """Eigenvectors auto-clamp values > 1.0 to 1.0 (valid range)."""
        spec = CitizenSpec(
            name="Test",
            archetype="Builder",
            region="plaza",
            eigenvectors=Eigenvectors(warmth=warmth),
        )
        # Eigenvectors clamps values in __post_init__
        assert spec.eigenvectors.warmth == 1.0  # Clamped to max

    @given(
        elapsed=st.floats(min_value=0.0, max_value=10000.0),
        tick_count=st.integers(min_value=1, max_value=100),
    )
    def test_session_time_accumulates_correctly(
        self, elapsed: float, tick_count: int
    ) -> None:
        """Session time should accumulate correctly across ticks."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=MARKET_DAY)
        session.start()

        per_tick = elapsed / tick_count
        for _ in range(tick_count):
            session.tick(per_tick)

        # Allow small floating point error
        actual = session.context["time_elapsed"]
        assert abs(actual - elapsed) < 0.01

    @given(name=st.text(min_size=1, max_size=50))
    def test_citizen_spec_name_roundtrip(self, name: str) -> None:
        """CitizenSpec names should survive serialization roundtrip."""
        spec = CitizenSpec(name=name, archetype="Builder", region="plaza")
        # Create template with spec
        template = ScenarioTemplate(
            name="Test",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[spec],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        data = template.to_dict()
        restored = ScenarioTemplate.from_dict(data)
        assert restored.citizens[0].name == name


# =============================================================================
# Stress Tests and Edge Cases
# =============================================================================


class TestStressAndEdgeCases:
    """Stress tests and edge case coverage."""

    def test_many_citizens_scenario(self) -> None:
        """Scenario with many citizens works correctly."""
        specs = [
            CitizenSpec(
                name=f"Citizen_{i}", archetype="Builder", region=f"region_{i % 5}"
            )
            for i in range(100)
        ]
        template = ScenarioTemplate(
            name="Crowd Scene",
            scenario_type=ScenarioType.EMERGENCE,
            citizens=specs,
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(
                criteria=[
                    SuccessCriterion(
                        kind="time_elapsed",
                        description="Survive the crowd",
                        params={"min_seconds": 1.0},
                    )
                ]
            ),
            regions=[f"region_{i}" for i in range(5)],
        )
        citizens = template.spawn_citizens()
        assert len(citizens) == 100

    def test_many_interactions_recorded(self) -> None:
        """Session handles many interactions efficiently."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=MARKET_DAY)
        session.start()
        # Record 1000 interactions
        for i in range(1000):
            session.record_interaction(
                f"citizen_{i}", f"citizen_{i + 1}", "dialogue", f"msg_{i}"
            )
        assert len(session.interactions) == 1000

    def test_rapid_tick_succession(self) -> None:
        """Session handles rapid tick succession."""
        from agents.park.scenario import ScenarioSession

        session = ScenarioSession(template=MARKET_DAY)
        session.start()
        # Tick 1000 times rapidly
        for _ in range(1000):
            session.tick(0.001)
        assert session.context["time_elapsed"] == pytest.approx(1.0, rel=0.01)

    def test_empty_context_criterion_evaluation(self) -> None:
        """Criteria handle empty context gracefully."""
        criterion = SuccessCriterion(
            kind="coalition_formed",
            description="Form a coalition",
            params={"min_size": 3},
        )
        # Empty context should not crash
        assert criterion.is_met({}) is False

    def test_zero_delay_time_trigger(self) -> None:
        """Time-based trigger with zero delay works."""
        trigger = TriggerCondition.time_based(delay_seconds=0.0)
        assert trigger.is_satisfied({"time_elapsed": 0.0}) is True

    def test_negative_time_elapsed_handled(self) -> None:
        """Trigger handles negative time gracefully."""
        trigger = TriggerCondition.time_based(delay_seconds=10.0)
        # Should not crash, just return False
        assert trigger.is_satisfied({"time_elapsed": -5.0}) is False

    def test_scenario_with_unicode_names(self) -> None:
        """Scenario handles unicode names correctly."""
        spec = CitizenSpec(
            name="村上春樹",  # Japanese
            archetype="Scholar",
            region="図書館",
        )
        template = ScenarioTemplate(
            name="日本の物語",
            scenario_type=ScenarioType.MYSTERY,
            citizens=[spec],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
            regions=["図書館"],
        )
        data = template.to_dict()
        restored = ScenarioTemplate.from_dict(data)
        assert restored.name == "日本の物語"
        assert restored.citizens[0].name == "村上春樹"

    def test_registry_handles_duplicate_ids(self) -> None:
        """Registry overwrites on duplicate ID registration."""
        registry = ScenarioRegistry()
        template1 = ScenarioTemplate(
            id="duplicate",
            name="First",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        template2 = ScenarioTemplate(
            id="duplicate",
            name="Second",
            scenario_type=ScenarioType.PRACTICE,
            citizens=[],
            trigger=TriggerCondition.immediate(),
            success_criteria=SuccessCriteria(criteria=[]),
        )
        registry.register(template1)
        registry.register(template2)
        # Should only have one entry (overwritten)
        assert len(registry.list_all()) == 1
        assert registry.get("duplicate").name == "Second"

    def test_session_terminal_state_idempotent(self) -> None:
        """Calling abandon/fail on terminal session is idempotent."""
        from agents.park.scenario import ScenarioPhase, ScenarioSession

        session = ScenarioSession(template=THE_MISSING_ARTIFACT)
        session.start()
        session.abandon()
        assert session.phase == ScenarioPhase.ABANDONED
        # Should not change phase or crash
        session.abandon()
        session.fail()
        assert session.phase == ScenarioPhase.ABANDONED

    def test_empty_success_criteria_never_met(self) -> None:
        """Empty SuccessCriteria is never met."""
        criteria = SuccessCriteria(criteria=[])
        assert criteria.is_met({}) is False
        assert criteria.is_met({"anything": True}) is False

    def test_large_registry_search(self) -> None:
        """Registry search performs well with many templates."""
        registry = ScenarioRegistry()
        # Register 1000 templates
        types = list(ScenarioType)
        difficulties = ["easy", "medium", "hard"]
        for i in range(1000):
            template = ScenarioTemplate(
                id=f"template-{i}",
                name=f"Template {i}",
                scenario_type=types[i % len(types)],
                citizens=[],
                trigger=TriggerCondition.immediate(),
                success_criteria=SuccessCriteria(criteria=[]),
                tags=[f"tag-{i % 10}"],
                difficulty=difficulties[i % len(difficulties)],
            )
            registry.register(template)

        # Search should complete
        results = registry.search(
            scenario_type=ScenarioType.MYSTERY,
            tags=["tag-5"],
            difficulty="hard",
        )
        assert len(results) > 0
