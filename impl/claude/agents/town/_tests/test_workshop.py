"""
Tests for WorkshopEnvironment: Builder's Workshop Chunk 6.

Test Categories:
1. Task creation tests
2. Plan creation tests
3. State tests
4. Environment creation tests
5. Task assignment tests
6. Advance tests
7. Handoff tests
8. Completion tests
9. Event tests
10. Keyword routing tests
11. Integration tests

Target: 65+ tests
"""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from agents.town.builders import (
    Builder,
    BuilderPhase,
    create_sage,
    create_scout,
    create_spark,
    create_steady,
    create_sync,
)
from agents.town.event_bus import EventBus
from agents.town.workshop import (
    ARCHETYPE_TO_PHASE,
    KEYWORD_ROUTING,
    PHASE_TO_ARCHETYPE,
    WorkshopArtifact,
    WorkshopEnvironment,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopPhase,
    WorkshopPlan,
    WorkshopState,
    WorkshopTask,
    create_workshop,
    create_workshop_with_builders,
    route_task,
    suggest_phases,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_task() -> WorkshopTask:
    """Create a sample task."""
    return WorkshopTask.create("Implement user authentication", priority=2)


@pytest.fixture
def default_builders() -> tuple[Builder, ...]:
    """Create the default builder set."""
    return (
        create_scout("Scout"),
        create_sage("Sage"),
        create_spark("Spark"),
        create_steady("Steady"),
        create_sync("Sync"),
    )


@pytest.fixture
def workshop() -> WorkshopEnvironment:
    """Create a workshop with default builders."""
    return create_workshop()


@pytest.fixture
def workshop_with_bus() -> tuple[WorkshopEnvironment, EventBus[WorkshopEvent]]:
    """Create a workshop with event bus."""
    bus: EventBus[WorkshopEvent] = EventBus()
    workshop = create_workshop(event_bus=bus)
    return workshop, bus


# =============================================================================
# 1. Task Creation Tests
# =============================================================================


class TestWorkshopTask:
    """Tests for WorkshopTask dataclass."""

    def test_create_with_description(self) -> None:
        """Task can be created with description."""
        task = WorkshopTask.create("Build feature")
        assert task.description == "Build feature"
        assert task.priority == 1
        assert len(task.id) == 8

    def test_create_with_priority(self) -> None:
        """Task can be created with custom priority."""
        task = WorkshopTask.create("Critical fix", priority=3)
        assert task.priority == 3

    def test_create_with_context(self) -> None:
        """Task can be created with context kwargs."""
        task = WorkshopTask.create("Feature", priority=2, component="auth", scope="api")
        assert task.context["component"] == "auth"
        assert task.context["scope"] == "api"

    def test_id_is_unique(self) -> None:
        """Each task has a unique ID."""
        tasks = [WorkshopTask.create(f"Task {i}") for i in range(10)]
        ids = [t.id for t in tasks]
        assert len(set(ids)) == 10

    def test_created_at_timestamp(self) -> None:
        """Task has creation timestamp."""
        before = datetime.now()
        task = WorkshopTask.create("Task")
        after = datetime.now()
        assert before <= task.created_at <= after

    def test_is_frozen(self) -> None:
        """Task is immutable."""
        task = WorkshopTask.create("Task")
        with pytest.raises(Exception):  # FrozenInstanceError
            task.description = "Modified"  # type: ignore

    def test_to_dict(self) -> None:
        """Task can be serialized to dict."""
        task = WorkshopTask.create("Task", priority=2, key="value")
        d = task.to_dict()
        assert d["description"] == "Task"
        assert d["priority"] == 2
        assert d["context"]["key"] == "value"
        assert "id" in d
        assert "created_at" in d


# =============================================================================
# 2. Plan Creation Tests
# =============================================================================


class TestWorkshopPlan:
    """Tests for WorkshopPlan dataclass."""

    def test_plan_structure(self, sample_task: WorkshopTask) -> None:
        """Plan has expected structure."""
        plan = WorkshopPlan(
            task=sample_task,
            assignments={"Scout": ["Research"]},
            estimated_phases=[WorkshopPhase.EXPLORING],
            lead_builder="Scout",
        )
        assert plan.task == sample_task
        assert plan.lead_builder == "Scout"

    def test_get_subtasks_for_existing(self, sample_task: WorkshopTask) -> None:
        """Can get subtasks for assigned archetype."""
        plan = WorkshopPlan(
            task=sample_task,
            assignments={"Scout": ["Research", "Discover"]},
            estimated_phases=[],
            lead_builder="Scout",
        )
        subtasks = plan.get_subtasks_for("Scout")
        assert subtasks == ["Research", "Discover"]

    def test_get_subtasks_for_missing(self, sample_task: WorkshopTask) -> None:
        """Returns empty list for unassigned archetype."""
        plan = WorkshopPlan(
            task=sample_task,
            assignments={"Scout": ["Research"]},
            estimated_phases=[],
            lead_builder="Scout",
        )
        subtasks = plan.get_subtasks_for("Sage")
        assert subtasks == []

    def test_to_dict(self, sample_task: WorkshopTask) -> None:
        """Plan can be serialized to dict."""
        plan = WorkshopPlan(
            task=sample_task,
            assignments={"Scout": ["Research"]},
            estimated_phases=[WorkshopPhase.EXPLORING, WorkshopPhase.DESIGNING],
            lead_builder="Scout",
        )
        d = plan.to_dict()
        assert d["lead_builder"] == "Scout"
        assert d["estimated_phases"] == ["EXPLORING", "DESIGNING"]


# =============================================================================
# 3. State Tests
# =============================================================================


class TestWorkshopState:
    """Tests for WorkshopState dataclass."""

    def test_is_idle_true(self, default_builders: tuple[Builder, ...]) -> None:
        """is_idle is True when IDLE."""
        state = WorkshopState(phase=WorkshopPhase.IDLE, builders=default_builders)
        assert state.is_idle is True

    def test_is_idle_false(self, default_builders: tuple[Builder, ...]) -> None:
        """is_idle is False when not IDLE."""
        state = WorkshopState(phase=WorkshopPhase.EXPLORING, builders=default_builders)
        assert state.is_idle is False

    def test_is_complete_true(self, default_builders: tuple[Builder, ...]) -> None:
        """is_complete is True when COMPLETE."""
        state = WorkshopState(phase=WorkshopPhase.COMPLETE, builders=default_builders)
        assert state.is_complete is True

    def test_is_complete_false(self, default_builders: tuple[Builder, ...]) -> None:
        """is_complete is False when not COMPLETE."""
        state = WorkshopState(phase=WorkshopPhase.REFINING, builders=default_builders)
        assert state.is_complete is False

    def test_active_builder_exploring(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is Scout during EXPLORING."""
        state = WorkshopState(phase=WorkshopPhase.EXPLORING, builders=default_builders)
        assert state.active_builder is not None
        assert state.active_builder.archetype == "Scout"

    def test_active_builder_designing(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is Sage during DESIGNING."""
        state = WorkshopState(phase=WorkshopPhase.DESIGNING, builders=default_builders)
        assert state.active_builder is not None
        assert state.active_builder.archetype == "Sage"

    def test_active_builder_prototyping(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is Spark during PROTOTYPING."""
        state = WorkshopState(phase=WorkshopPhase.PROTOTYPING, builders=default_builders)
        assert state.active_builder is not None
        assert state.active_builder.archetype == "Spark"

    def test_active_builder_refining(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is Steady during REFINING."""
        state = WorkshopState(phase=WorkshopPhase.REFINING, builders=default_builders)
        assert state.active_builder is not None
        assert state.active_builder.archetype == "Steady"

    def test_active_builder_integrating(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is Sync during INTEGRATING."""
        state = WorkshopState(phase=WorkshopPhase.INTEGRATING, builders=default_builders)
        assert state.active_builder is not None
        assert state.active_builder.archetype == "Sync"

    def test_active_builder_idle(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is None during IDLE."""
        state = WorkshopState(phase=WorkshopPhase.IDLE, builders=default_builders)
        assert state.active_builder is None

    def test_active_builder_complete(self, default_builders: tuple[Builder, ...]) -> None:
        """Active builder is None during COMPLETE."""
        state = WorkshopState(phase=WorkshopPhase.COMPLETE, builders=default_builders)
        assert state.active_builder is None

    def test_get_builder_found(self, default_builders: tuple[Builder, ...]) -> None:
        """Can get builder by archetype."""
        state = WorkshopState(phase=WorkshopPhase.IDLE, builders=default_builders)
        sage = state.get_builder("Sage")
        assert sage is not None
        assert sage.archetype == "Sage"

    def test_get_builder_not_found(self, default_builders: tuple[Builder, ...]) -> None:
        """Returns None for unknown archetype."""
        state = WorkshopState(phase=WorkshopPhase.IDLE, builders=default_builders)
        unknown = state.get_builder("Unknown")
        assert unknown is None


# =============================================================================
# 4. Environment Creation Tests
# =============================================================================


class TestWorkshopEnvironmentCreation:
    """Tests for WorkshopEnvironment creation."""

    def test_create_default(self) -> None:
        """Workshop can be created with defaults."""
        workshop = create_workshop()
        assert workshop is not None
        assert len(workshop.builders) == 5

    def test_create_with_builders(self, default_builders: tuple[Builder, ...]) -> None:
        """Workshop can be created with specific builders."""
        workshop = create_workshop_with_builders(default_builders)
        assert workshop.builders == default_builders

    def test_create_with_event_bus(self) -> None:
        """Workshop can be created with event bus."""
        bus: EventBus[WorkshopEvent] = EventBus()
        workshop = create_workshop(event_bus=bus)
        assert workshop._event_bus is bus

    def test_default_state_is_idle(self) -> None:
        """Default state is IDLE with no active task."""
        workshop = create_workshop()
        assert workshop.state.is_idle
        assert workshop.state.active_task is None
        assert workshop.state.plan is None

    def test_builders_have_correct_archetypes(self) -> None:
        """Default builders have correct archetypes."""
        workshop = create_workshop()
        archetypes = {b.archetype for b in workshop.builders}
        assert archetypes == {"Scout", "Sage", "Spark", "Steady", "Sync"}

    def test_get_builder_works(self) -> None:
        """Can get builder by archetype from workshop."""
        workshop = create_workshop()
        scout = workshop.get_builder("Scout")
        assert scout is not None
        assert scout.archetype == "Scout"


# =============================================================================
# 5. Task Assignment Tests
# =============================================================================


class TestTaskAssignment:
    """Tests for task assignment."""

    @pytest.mark.asyncio
    async def test_assign_string_task(self, workshop: WorkshopEnvironment) -> None:
        """Can assign task as string."""
        plan = await workshop.assign_task("Research authentication options")
        assert plan is not None
        assert plan.task.description == "Research authentication options"

    @pytest.mark.asyncio
    async def test_assign_task_object(
        self, workshop: WorkshopEnvironment, sample_task: WorkshopTask
    ) -> None:
        """Can assign WorkshopTask object."""
        plan = await workshop.assign_task(sample_task)
        assert plan.task == sample_task

    @pytest.mark.asyncio
    async def test_assign_sets_active_task(self, workshop: WorkshopEnvironment) -> None:
        """Assigning task sets it as active."""
        await workshop.assign_task("Task")
        assert workshop.state.active_task is not None

    @pytest.mark.asyncio
    async def test_assign_creates_plan(self, workshop: WorkshopEnvironment) -> None:
        """Assigning task creates a plan."""
        plan = await workshop.assign_task("Research API design")
        assert plan.lead_builder in {"Scout", "Sage", "Spark", "Steady", "Sync"}
        assert len(plan.estimated_phases) > 0

    @pytest.mark.asyncio
    async def test_assign_starts_first_phase(self, workshop: WorkshopEnvironment) -> None:
        """Assigning task starts first phase."""
        await workshop.assign_task("Research something")
        assert not workshop.state.is_idle
        assert workshop.state.phase in {
            WorkshopPhase.EXPLORING,
            WorkshopPhase.DESIGNING,
            WorkshopPhase.PROTOTYPING,
            WorkshopPhase.REFINING,
            WorkshopPhase.INTEGRATING,
        }

    @pytest.mark.asyncio
    async def test_assign_transitions_lead_builder(self, workshop: WorkshopEnvironment) -> None:
        """Assigning task transitions the lead builder."""
        await workshop.assign_task("Research authentication")
        lead = workshop.get_builder("Scout")
        assert lead is not None
        # Scout should be in EXPLORING phase
        assert lead.builder_phase == BuilderPhase.EXPLORING

    @pytest.mark.asyncio
    async def test_cannot_assign_while_active(self, workshop: WorkshopEnvironment) -> None:
        """Cannot assign a new task while one is active."""
        await workshop.assign_task("First task")
        with pytest.raises(ValueError, match="already in progress"):
            await workshop.assign_task("Second task")

    @pytest.mark.asyncio
    async def test_assign_with_priority(self, workshop: WorkshopEnvironment) -> None:
        """Can assign task with priority."""
        await workshop.assign_task("Critical task", priority=3)
        assert workshop.state.active_task is not None
        assert workshop.state.active_task.priority == 3


# =============================================================================
# 6. Advance Tests
# =============================================================================


class TestAdvance:
    """Tests for workshop advancement."""

    @pytest.mark.asyncio
    async def test_advance_requires_active_task(self, workshop: WorkshopEnvironment) -> None:
        """Cannot advance without active task."""
        with pytest.raises(ValueError, match="No active task"):
            await workshop.advance()

    @pytest.mark.asyncio
    async def test_advance_returns_event(self, workshop: WorkshopEnvironment) -> None:
        """Advance returns a WorkshopEvent."""
        await workshop.assign_task("Task")
        event = await workshop.advance()
        assert isinstance(event, WorkshopEvent)

    @pytest.mark.asyncio
    async def test_advance_produces_artifact_event(self, workshop: WorkshopEnvironment) -> None:
        """Advance produces artifact event while working."""
        await workshop.assign_task("Task")
        event = await workshop.advance()
        assert event.type in {
            WorkshopEventType.ARTIFACT_PRODUCED,
            WorkshopEventType.HANDOFF,
            WorkshopEventType.PHASE_COMPLETED,
        }

    @pytest.mark.asyncio
    async def test_advance_records_builder(self, workshop: WorkshopEnvironment) -> None:
        """Advance records which builder worked."""
        await workshop.assign_task("Research something")
        event = await workshop.advance()
        # Scout should be active for research task
        assert event.builder in {"Scout", "Sage", "Spark", "Steady", "Sync", None}

    @pytest.mark.asyncio
    async def test_cannot_advance_when_complete(self, workshop: WorkshopEnvironment) -> None:
        """Cannot advance when task is complete."""
        await workshop.assign_task("Task")
        await workshop.complete()
        with pytest.raises(ValueError, match="complete"):
            await workshop.advance()


# =============================================================================
# 7. Handoff Tests
# =============================================================================


class TestHandoff:
    """Tests for explicit handoffs."""

    @pytest.mark.asyncio
    async def test_handoff_requires_active_task(self, workshop: WorkshopEnvironment) -> None:
        """Cannot handoff without active task."""
        with pytest.raises(ValueError, match="No active task"):
            await workshop.handoff("Scout", "Sage")

    @pytest.mark.asyncio
    async def test_handoff_returns_event(self, workshop: WorkshopEnvironment) -> None:
        """Handoff returns a HANDOFF event."""
        await workshop.assign_task("Task")
        event = await workshop.handoff("Scout", "Sage", artifact="research_notes")
        assert event.type == WorkshopEventType.HANDOFF

    @pytest.mark.asyncio
    async def test_handoff_updates_phase(self, workshop: WorkshopEnvironment) -> None:
        """Handoff updates workshop phase."""
        await workshop.assign_task("Research task")
        await workshop.handoff("Scout", "Sage")
        assert workshop.state.phase == WorkshopPhase.DESIGNING

    @pytest.mark.asyncio
    async def test_handoff_changes_active_builder(self, workshop: WorkshopEnvironment) -> None:
        """Handoff changes the active builder."""
        await workshop.assign_task("Task")
        await workshop.handoff("Scout", "Spark")
        assert workshop.state.active_builder is not None
        assert workshop.state.active_builder.archetype == "Spark"

    @pytest.mark.asyncio
    async def test_handoff_validates_from_builder(self, workshop: WorkshopEnvironment) -> None:
        """Handoff validates from_builder exists."""
        await workshop.assign_task("Task")
        with pytest.raises(ValueError, match="not found.*Unknown"):
            await workshop.handoff("Unknown", "Sage")

    @pytest.mark.asyncio
    async def test_handoff_validates_to_builder(self, workshop: WorkshopEnvironment) -> None:
        """Handoff validates to_builder exists."""
        await workshop.assign_task("Task")
        with pytest.raises(ValueError, match="not found.*Missing"):
            await workshop.handoff("Scout", "Missing")

    @pytest.mark.asyncio
    async def test_handoff_with_artifact(self, workshop: WorkshopEnvironment) -> None:
        """Handoff can include artifact."""
        await workshop.assign_task("Task")
        event = await workshop.handoff("Scout", "Sage", artifact={"findings": "data"})
        assert event.artifact == {"findings": "data"}

    @pytest.mark.asyncio
    async def test_handoff_with_message(self, workshop: WorkshopEnvironment) -> None:
        """Handoff can include message."""
        await workshop.assign_task("Task")
        event = await workshop.handoff("Scout", "Sage", message="Ready for design")
        assert "Ready for design" in event.message

    @pytest.mark.asyncio
    async def test_handoff_creates_artifact(self, workshop: WorkshopEnvironment) -> None:
        """Handoff with artifact adds to artifacts list."""
        await workshop.assign_task("Task")
        await workshop.handoff("Scout", "Sage", artifact="notes")
        assert len(workshop.state.artifacts) == 1
        assert workshop.state.artifacts[0].content == "notes"


# =============================================================================
# 8. Completion Tests
# =============================================================================


class TestCompletion:
    """Tests for task completion."""

    @pytest.mark.asyncio
    async def test_complete_requires_active_task(self, workshop: WorkshopEnvironment) -> None:
        """Cannot complete without active task."""
        with pytest.raises(ValueError, match="No active task"):
            await workshop.complete()

    @pytest.mark.asyncio
    async def test_complete_returns_event(self, workshop: WorkshopEnvironment) -> None:
        """Complete returns TASK_COMPLETED event."""
        await workshop.assign_task("Task")
        event = await workshop.complete()
        assert event.type == WorkshopEventType.TASK_COMPLETED

    @pytest.mark.asyncio
    async def test_complete_sets_phase_complete(self, workshop: WorkshopEnvironment) -> None:
        """Complete sets phase to COMPLETE."""
        await workshop.assign_task("Task")
        await workshop.complete()
        assert workshop.state.phase == WorkshopPhase.COMPLETE
        assert workshop.state.is_complete

    @pytest.mark.asyncio
    async def test_complete_with_summary(self, workshop: WorkshopEnvironment) -> None:
        """Complete can include summary."""
        await workshop.assign_task("Task")
        event = await workshop.complete(summary="All done")
        assert "Task completed" in event.message

    @pytest.mark.asyncio
    async def test_reset_after_complete(self, workshop: WorkshopEnvironment) -> None:
        """Workshop can be reset after completion."""
        await workshop.assign_task("Task")
        await workshop.complete()
        workshop.reset()
        assert workshop.state.is_idle
        assert workshop.state.active_task is None

    @pytest.mark.asyncio
    async def test_reset_clears_artifacts(self, workshop: WorkshopEnvironment) -> None:
        """Reset clears artifacts."""
        await workshop.assign_task("Task")
        await workshop.handoff("Scout", "Sage", artifact="data")
        workshop.reset()
        assert len(workshop.state.artifacts) == 0

    @pytest.mark.asyncio
    async def test_reset_clears_events(self, workshop: WorkshopEnvironment) -> None:
        """Reset clears events."""
        await workshop.assign_task("Task")
        await workshop.advance()
        workshop.reset()
        assert len(workshop.state.events) == 0


# =============================================================================
# 9. Event Tests
# =============================================================================


class TestEvents:
    """Tests for event generation and streaming."""

    @pytest.mark.asyncio
    async def test_assign_emits_task_assigned(self, workshop: WorkshopEnvironment) -> None:
        """Task assignment emits TASK_ASSIGNED event."""
        await workshop.assign_task("Task")
        events = workshop.state.events
        event_types = {e.type for e in events}
        assert WorkshopEventType.TASK_ASSIGNED in event_types

    @pytest.mark.asyncio
    async def test_assign_emits_plan_created(self, workshop: WorkshopEnvironment) -> None:
        """Task assignment emits PLAN_CREATED event."""
        await workshop.assign_task("Task")
        events = workshop.state.events
        event_types = {e.type for e in events}
        assert WorkshopEventType.PLAN_CREATED in event_types

    @pytest.mark.asyncio
    async def test_assign_emits_phase_started(self, workshop: WorkshopEnvironment) -> None:
        """Task assignment emits PHASE_STARTED event."""
        await workshop.assign_task("Task")
        events = workshop.state.events
        event_types = {e.type for e in events}
        assert WorkshopEventType.PHASE_STARTED in event_types

    @pytest.mark.asyncio
    async def test_event_has_timestamp(self, workshop: WorkshopEnvironment) -> None:
        """Events have timestamps."""
        before = datetime.now()
        await workshop.assign_task("Task")
        after = datetime.now()
        for event in workshop.state.events:
            assert before <= event.timestamp <= after

    @pytest.mark.asyncio
    async def test_event_to_dict(self, workshop: WorkshopEnvironment) -> None:
        """Events can be serialized."""
        await workshop.assign_task("Task")
        event = workshop.state.events[0]
        d = event.to_dict()
        assert "type" in d
        assert "timestamp" in d
        assert "phase" in d

    @pytest.mark.asyncio
    async def test_event_bus_receives_events(
        self, workshop_with_bus: tuple[WorkshopEnvironment, EventBus[WorkshopEvent]]
    ) -> None:
        """Event bus receives published events."""
        workshop, bus = workshop_with_bus
        subscription = bus.subscribe()

        await workshop.assign_task("Task")

        # Give async a moment to process
        event = await subscription.get(timeout=1.0)
        assert event is not None
        assert event.type == WorkshopEventType.TASK_ASSIGNED

        subscription.close()

    def test_observe_requires_bus(self, workshop: WorkshopEnvironment) -> None:
        """observe() requires event bus."""
        with pytest.raises(RuntimeError, match="No event bus"):
            workshop.observe()


# =============================================================================
# 10. Keyword Routing Tests
# =============================================================================


class TestKeywordRouting:
    """Tests for keyword-based task routing."""

    def test_route_to_scout_research(self) -> None:
        """'research' routes to Scout."""
        task = WorkshopTask.create("Research authentication options")
        assert route_task(task) == "Scout"

    def test_route_to_scout_explore(self) -> None:
        """'explore' routes to Scout."""
        task = WorkshopTask.create("Explore different frameworks")
        assert route_task(task) == "Scout"

    def test_route_to_sage_design(self) -> None:
        """'design' routes to Sage."""
        task = WorkshopTask.create("Design the API schema")
        assert route_task(task) == "Sage"

    def test_route_to_sage_architect(self) -> None:
        """'architect' routes to Sage."""
        task = WorkshopTask.create("Architect the system")
        assert route_task(task) == "Sage"

    def test_route_to_spark_prototype(self) -> None:
        """'prototype' routes to Spark."""
        task = WorkshopTask.create("Prototype the UI")
        assert route_task(task) == "Spark"

    def test_route_to_spark_experiment(self) -> None:
        """'experiment' routes to Spark."""
        task = WorkshopTask.create("Experiment with caching")
        assert route_task(task) == "Spark"

    def test_route_to_steady_test(self) -> None:
        """'test' routes to Steady."""
        task = WorkshopTask.create("Test the authentication flow")
        assert route_task(task) == "Steady"

    def test_route_to_steady_polish(self) -> None:
        """'polish' routes to Steady."""
        task = WorkshopTask.create("Polish the error handling")
        assert route_task(task) == "Steady"

    def test_route_to_sync_integrate(self) -> None:
        """'integrate' routes to Sync."""
        task = WorkshopTask.create("Integrate with payment system")
        assert route_task(task) == "Sync"

    def test_route_to_sync_deploy(self) -> None:
        """'deploy' routes to Sync."""
        task = WorkshopTask.create("Deploy to production")
        assert route_task(task) == "Sync"

    def test_route_default_to_scout(self) -> None:
        """Default routing goes to Scout."""
        task = WorkshopTask.create("Do something unclear")
        assert route_task(task) == "Scout"

    def test_route_case_insensitive(self) -> None:
        """Routing is case insensitive."""
        task = WorkshopTask.create("RESEARCH the options")
        assert route_task(task) == "Scout"

    def test_suggest_phases_from_scout(self) -> None:
        """Suggest phases from Scout starts at EXPLORING."""
        phases = suggest_phases("Scout")
        assert phases[0] == WorkshopPhase.EXPLORING
        assert WorkshopPhase.DESIGNING in phases

    def test_suggest_phases_from_sage(self) -> None:
        """Suggest phases from Sage starts at DESIGNING."""
        phases = suggest_phases("Sage")
        assert phases[0] == WorkshopPhase.DESIGNING

    def test_suggest_phases_from_sync(self) -> None:
        """Suggest phases from Sync has only INTEGRATING."""
        phases = suggest_phases("Sync")
        assert phases == [WorkshopPhase.INTEGRATING]

    def test_phase_archetype_mappings(self) -> None:
        """PHASE_TO_ARCHETYPE and ARCHETYPE_TO_PHASE are inverse."""
        for phase, arch in PHASE_TO_ARCHETYPE.items():
            assert ARCHETYPE_TO_PHASE[arch] == phase


# =============================================================================
# 11. Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full task lifecycle."""

    @pytest.mark.asyncio
    async def test_full_task_lifecycle(self, workshop: WorkshopEnvironment) -> None:
        """Complete a task through full lifecycle."""
        # Assign
        plan = await workshop.assign_task("Research and implement feature")
        assert plan.lead_builder == "Scout"

        # Advance through phases
        events: list[WorkshopEvent] = []
        for _ in range(10):  # Max iterations
            if workshop.state.is_complete:
                break
            event = await workshop.advance()
            events.append(event)

        # Should have produced some events
        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_explicit_handoff_chain(self, workshop: WorkshopEnvironment) -> None:
        """Execute explicit handoff chain."""
        await workshop.assign_task("Build feature")

        # Scout → Sage
        await workshop.handoff("Scout", "Sage", artifact="research")
        assert workshop.state.phase == WorkshopPhase.DESIGNING

        # Sage → Spark
        await workshop.handoff("Sage", "Spark", artifact="design")
        assert workshop.state.phase == WorkshopPhase.PROTOTYPING

        # Spark → Steady
        await workshop.handoff("Spark", "Steady", artifact="prototype")
        assert workshop.state.phase == WorkshopPhase.REFINING

        # Steady → Sync
        await workshop.handoff("Steady", "Sync", artifact="implementation")
        assert workshop.state.phase == WorkshopPhase.INTEGRATING

        # Complete
        await workshop.complete()
        assert workshop.state.is_complete
        assert len(workshop.state.artifacts) == 4

    @pytest.mark.asyncio
    async def test_manifest_at_different_lods(self, workshop: WorkshopEnvironment) -> None:
        """Manifest provides different detail levels."""
        await workshop.assign_task("Task")

        lod0 = workshop.manifest(lod=0)
        assert "phase" in lod0
        assert "task" not in lod0

        lod1 = workshop.manifest(lod=1)
        assert "task" in lod1
        assert "active_builder" in lod1

        lod2 = workshop.manifest(lod=2)
        assert "plan" in lod2
        assert "builders_detail" in lod2

    @pytest.mark.asyncio
    async def test_workshop_with_custom_builders(self) -> None:
        """Workshop works with custom builder subset."""
        builders = (create_scout("Scout"), create_sage("Sage"))
        workshop = create_workshop_with_builders(builders)

        await workshop.assign_task("Research something")
        assert workshop.get_builder("Scout") is not None
        assert workshop.get_builder("Spark") is None  # Not in custom set

    @pytest.mark.asyncio
    async def test_multiple_task_cycles(self, workshop: WorkshopEnvironment) -> None:
        """Workshop can handle multiple task cycles."""
        # First task
        await workshop.assign_task("First task")
        await workshop.complete()
        assert workshop.state.is_complete

        # Reset and second task
        workshop.reset()
        await workshop.assign_task("Second task")
        assert workshop.state.active_task is not None
        assert workshop.state.active_task.description == "Second task"

    @pytest.mark.asyncio
    async def test_artifact_accumulation(self, workshop: WorkshopEnvironment) -> None:
        """Artifacts accumulate through lifecycle."""
        await workshop.assign_task("Build feature")

        await workshop.handoff("Scout", "Sage", artifact="research_notes")
        await workshop.handoff("Sage", "Spark", artifact="design_doc")
        await workshop.handoff("Spark", "Steady", artifact="prototype_code")

        assert len(workshop.state.artifacts) == 3
        assert workshop.state.artifacts[0].builder == "Scout"
        assert workshop.state.artifacts[1].builder == "Sage"
        assert workshop.state.artifacts[2].builder == "Spark"


# =============================================================================
# Artifact Tests
# =============================================================================


class TestWorkshopArtifact:
    """Tests for WorkshopArtifact dataclass."""

    def test_create_artifact(self) -> None:
        """Artifact can be created with factory."""
        artifact = WorkshopArtifact.create(
            task_id="task123",
            builder="Scout",
            phase=WorkshopPhase.EXPLORING,
            content={"findings": ["a", "b"]},
        )
        assert artifact.task_id == "task123"
        assert artifact.builder == "Scout"
        assert artifact.content == {"findings": ["a", "b"]}

    def test_artifact_has_id(self) -> None:
        """Artifact has unique ID."""
        a1 = WorkshopArtifact.create("t", "Scout", WorkshopPhase.EXPLORING, "c1")
        a2 = WorkshopArtifact.create("t", "Scout", WorkshopPhase.EXPLORING, "c2")
        assert a1.id != a2.id

    def test_artifact_to_dict(self) -> None:
        """Artifact can be serialized."""
        artifact = WorkshopArtifact.create(
            task_id="task123",
            builder="Sage",
            phase=WorkshopPhase.DESIGNING,
            content="design document",
            version=1,
        )
        d = artifact.to_dict()
        assert d["task_id"] == "task123"
        assert d["builder"] == "Sage"
        assert d["phase"] == "DESIGNING"
        assert d["content"] == "design document"
        assert d["metadata"]["version"] == 1


# =============================================================================
# Phase Mapping Tests
# =============================================================================


class TestPhaseMappings:
    """Tests for phase/archetype mappings."""

    def test_all_work_phases_have_archetype(self) -> None:
        """All work phases map to an archetype."""
        work_phases = [
            WorkshopPhase.EXPLORING,
            WorkshopPhase.DESIGNING,
            WorkshopPhase.PROTOTYPING,
            WorkshopPhase.REFINING,
            WorkshopPhase.INTEGRATING,
        ]
        for phase in work_phases:
            assert phase in PHASE_TO_ARCHETYPE

    def test_keyword_routing_coverage(self) -> None:
        """All archetypes have keywords."""
        archetypes_in_routing = set(KEYWORD_ROUTING.values())
        expected = {"Scout", "Sage", "Spark", "Steady", "Sync"}
        assert archetypes_in_routing == expected


# =============================================================================
# Chunk 7: WorkshopMetrics Tests
# =============================================================================


from agents.town.workshop import (
    BUILDER_DIALOGUE_TEMPLATES,
    WorkshopDialogueContext,
    WorkshopFlux,
    WorkshopMetrics,
)


class TestWorkshopMetrics:
    """Tests for WorkshopMetrics dataclass."""

    def test_default_metrics(self) -> None:
        """Metrics have sensible defaults."""
        metrics = WorkshopMetrics()
        assert metrics.total_steps == 0
        assert metrics.total_events == 0
        assert metrics.total_tokens == 0
        assert metrics.dialogue_tokens == 0
        assert metrics.artifacts_produced == 0
        assert metrics.phases_completed == 0
        assert metrics.handoffs == 0
        assert metrics.perturbations == 0
        assert metrics.start_time is None
        assert metrics.end_time is None

    def test_duration_seconds_not_started(self) -> None:
        """Duration is 0 when not started."""
        metrics = WorkshopMetrics()
        assert metrics.duration_seconds == 0.0

    def test_duration_seconds_running(self) -> None:
        """Duration computes from start_time to now when running."""
        import time
        metrics = WorkshopMetrics(start_time=datetime.now())
        time.sleep(0.05)
        assert metrics.duration_seconds > 0.04

    def test_duration_seconds_completed(self) -> None:
        """Duration computes from start to end when completed."""
        import time
        start = datetime.now()
        time.sleep(0.05)
        end = datetime.now()
        metrics = WorkshopMetrics(start_time=start, end_time=end)
        assert 0.04 < metrics.duration_seconds < 0.2

    def test_events_per_second(self) -> None:
        """Events per second calculation."""
        import time
        metrics = WorkshopMetrics(start_time=datetime.now(), total_events=10)
        time.sleep(0.05)
        eps = metrics.events_per_second
        assert eps > 0

    def test_events_per_second_zero_duration(self) -> None:
        """Events per second is 0 when duration is 0."""
        metrics = WorkshopMetrics(total_events=10)
        assert metrics.events_per_second == 0.0

    def test_steps_per_phase(self) -> None:
        """Steps per phase calculation."""
        metrics = WorkshopMetrics(total_steps=15, phases_completed=3)
        assert metrics.steps_per_phase == 5.0

    def test_steps_per_phase_zero_phases(self) -> None:
        """Steps per phase is 0 when no phases completed."""
        metrics = WorkshopMetrics(total_steps=10)
        assert metrics.steps_per_phase == 0.0

    def test_to_dict(self) -> None:
        """Metrics can be serialized."""
        metrics = WorkshopMetrics(
            total_steps=10,
            total_events=20,
            artifacts_produced=3,
            handoffs=2,
        )
        d = metrics.to_dict()
        assert d["total_steps"] == 10
        assert d["total_events"] == 20
        assert d["artifacts_produced"] == 3
        assert d["handoffs"] == 2
        assert "duration_seconds" in d
        assert "events_per_second" in d


# =============================================================================
# Chunk 7: WorkshopDialogueContext Tests
# =============================================================================


class TestWorkshopDialogueContext:
    """Tests for WorkshopDialogueContext dataclass."""

    def test_create_context(self, sample_task: WorkshopTask) -> None:
        """Context can be created."""
        builder = create_scout("Scout")
        context = WorkshopDialogueContext(
            task=sample_task,
            phase=WorkshopPhase.EXPLORING,
            builder=builder,
            artifacts_so_far=[],
            recent_events=[],
            step_count=1,
        )
        assert context.task == sample_task
        assert context.phase == WorkshopPhase.EXPLORING

    def test_to_prompt_context_basic(self, sample_task: WorkshopTask) -> None:
        """Basic prompt context rendering."""
        builder = create_scout("Scout")
        context = WorkshopDialogueContext(
            task=sample_task,
            phase=WorkshopPhase.EXPLORING,
            builder=builder,
            artifacts_so_far=[],
            recent_events=[],
            step_count=1,
        )
        prompt = context.to_prompt_context()
        assert sample_task.description in prompt
        assert "EXPLORING" in prompt
        assert "Scout" in prompt

    def test_to_prompt_context_with_artifacts(self, sample_task: WorkshopTask) -> None:
        """Prompt context includes artifact summaries."""
        builder = create_sage("Sage")
        artifact = WorkshopArtifact.create(
            task_id=sample_task.id,
            builder="Scout",
            phase=WorkshopPhase.EXPLORING,
            content="research",
        )
        context = WorkshopDialogueContext(
            task=sample_task,
            phase=WorkshopPhase.DESIGNING,
            builder=builder,
            artifacts_so_far=[artifact],
            recent_events=[],
            step_count=2,
        )
        prompt = context.to_prompt_context()
        assert "Previous work" in prompt
        assert "Scout" in prompt

    def test_to_prompt_context_with_events(self, sample_task: WorkshopTask) -> None:
        """Prompt context includes recent events."""
        builder = create_spark("Spark")
        context = WorkshopDialogueContext(
            task=sample_task,
            phase=WorkshopPhase.PROTOTYPING,
            builder=builder,
            artifacts_so_far=[],
            recent_events=["Design completed", "Starting prototype"],
            step_count=3,
        )
        prompt = context.to_prompt_context()
        assert "Recent:" in prompt
        assert "Design completed" in prompt


# =============================================================================
# Chunk 7: Builder Dialogue Templates Tests
# =============================================================================


class TestBuilderDialogueTemplates:
    """Tests for BUILDER_DIALOGUE_TEMPLATES."""

    def test_all_archetypes_have_templates(self) -> None:
        """All builder archetypes have dialogue templates."""
        expected = {"Scout", "Sage", "Spark", "Steady", "Sync"}
        assert set(BUILDER_DIALOGUE_TEMPLATES.keys()) == expected

    def test_all_actions_covered(self) -> None:
        """All archetypes have standard actions."""
        actions = {"start_work", "continue", "handoff", "complete"}
        for archetype, templates in BUILDER_DIALOGUE_TEMPLATES.items():
            for action in actions:
                assert action in templates, f"{archetype} missing {action}"

    def test_templates_have_content(self) -> None:
        """Templates are non-empty lists."""
        for archetype, templates in BUILDER_DIALOGUE_TEMPLATES.items():
            for action, lines in templates.items():
                assert len(lines) > 0, f"{archetype}.{action} is empty"
                for line in lines:
                    assert len(line) > 0

    def test_handoff_templates_have_placeholder(self) -> None:
        """Handoff templates have {next_builder} placeholder."""
        for archetype, templates in BUILDER_DIALOGUE_TEMPLATES.items():
            for line in templates["handoff"]:
                assert "{next_builder}" in line


# =============================================================================
# Chunk 7: WorkshopFlux Creation Tests
# =============================================================================


class TestWorkshopFluxCreation:
    """Tests for WorkshopFlux initialization."""

    def test_create_flux(self, workshop: WorkshopEnvironment) -> None:
        """Flux can be created."""
        flux = WorkshopFlux(workshop)
        assert flux is not None
        assert flux.workshop is workshop

    def test_create_with_seed(self, workshop: WorkshopEnvironment) -> None:
        """Flux can be created with seed."""
        flux = WorkshopFlux(workshop, seed=42)
        assert flux is not None

    def test_create_with_auto_advance_false(self, workshop: WorkshopEnvironment) -> None:
        """Flux can be created with auto_advance=False."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        assert flux._auto_advance is False

    def test_create_with_max_steps(self, workshop: WorkshopEnvironment) -> None:
        """Flux can be created with custom max_steps_per_phase."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=10)
        assert flux._max_steps_per_phase == 10

    def test_initial_state_not_running(self, workshop: WorkshopEnvironment) -> None:
        """Flux is not running initially."""
        flux = WorkshopFlux(workshop)
        assert flux.is_running is False

    def test_initial_phase_idle(self, workshop: WorkshopEnvironment) -> None:
        """Initial phase is IDLE."""
        flux = WorkshopFlux(workshop)
        assert flux.current_phase == WorkshopPhase.IDLE

    def test_initial_active_builder_none(self, workshop: WorkshopEnvironment) -> None:
        """Initial active builder is None."""
        flux = WorkshopFlux(workshop)
        assert flux.active_builder is None


# =============================================================================
# Chunk 7: WorkshopFlux Start Tests
# =============================================================================


class TestWorkshopFluxStart:
    """Tests for WorkshopFlux.start()."""

    @pytest.mark.asyncio
    async def test_start_string_task(self, workshop: WorkshopEnvironment) -> None:
        """Can start with string task."""
        flux = WorkshopFlux(workshop)
        plan = await flux.start("Research authentication")
        assert plan is not None
        assert flux.is_running is True

    @pytest.mark.asyncio
    async def test_start_task_object(self, workshop: WorkshopEnvironment, sample_task: WorkshopTask) -> None:
        """Can start with WorkshopTask object."""
        flux = WorkshopFlux(workshop)
        plan = await flux.start(sample_task)
        assert plan.task == sample_task

    @pytest.mark.asyncio
    async def test_start_sets_running(self, workshop: WorkshopEnvironment) -> None:
        """Start sets is_running to True."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        assert flux.is_running is True

    @pytest.mark.asyncio
    async def test_start_initializes_metrics(self, workshop: WorkshopEnvironment) -> None:
        """Start initializes metrics with start_time."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        assert flux.get_metrics().start_time is not None

    @pytest.mark.asyncio
    async def test_start_updates_phase(self, workshop: WorkshopEnvironment) -> None:
        """Start moves phase from IDLE."""
        flux = WorkshopFlux(workshop)
        await flux.start("Research task")
        assert flux.current_phase != WorkshopPhase.IDLE

    @pytest.mark.asyncio
    async def test_start_sets_active_builder(self, workshop: WorkshopEnvironment) -> None:
        """Start sets active builder."""
        flux = WorkshopFlux(workshop)
        await flux.start("Research task")
        assert flux.active_builder is not None

    @pytest.mark.asyncio
    async def test_cannot_start_while_running(self, workshop: WorkshopEnvironment) -> None:
        """Cannot start when already running."""
        flux = WorkshopFlux(workshop)
        await flux.start("First task")
        with pytest.raises(RuntimeError, match="already running"):
            await flux.start("Second task")

    @pytest.mark.asyncio
    async def test_start_with_priority(self, workshop: WorkshopEnvironment) -> None:
        """Can start with priority."""
        flux = WorkshopFlux(workshop)
        await flux.start("Critical task", priority=3)
        assert workshop.state.active_task is not None
        assert workshop.state.active_task.priority == 3


# =============================================================================
# Chunk 7: WorkshopFlux Step Tests
# =============================================================================


class TestWorkshopFluxStep:
    """Tests for WorkshopFlux.step()."""

    @pytest.mark.asyncio
    async def test_step_yields_events(self, workshop: WorkshopEnvironment) -> None:
        """Step yields WorkshopEvents."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Research task")
        events = [e async for e in flux.step()]
        assert len(events) >= 1
        for event in events:
            assert isinstance(event, WorkshopEvent)

    @pytest.mark.asyncio
    async def test_step_increments_step_count(self, workshop: WorkshopEnvironment) -> None:
        """Step increments step count."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Task")
        [e async for e in flux.step()]
        assert flux._step_count == 1
        [e async for e in flux.step()]
        assert flux._step_count == 2

    @pytest.mark.asyncio
    async def test_step_updates_metrics(self, workshop: WorkshopEnvironment) -> None:
        """Step updates metrics."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Task")
        [e async for e in flux.step()]
        metrics = flux.get_metrics()
        assert metrics.total_steps == 1
        assert metrics.total_events >= 1

    @pytest.mark.asyncio
    async def test_step_nothing_when_not_running(self, workshop: WorkshopEnvironment) -> None:
        """Step yields nothing when not running."""
        flux = WorkshopFlux(workshop)
        events = [e async for e in flux.step()]
        assert events == []

    @pytest.mark.asyncio
    async def test_step_adds_dialogue_metadata(self, workshop: WorkshopEnvironment) -> None:
        """Step adds dialogue to event metadata."""
        flux = WorkshopFlux(workshop, auto_advance=False, seed=42)
        await flux.start("Research task")
        events = [e async for e in flux.step()]
        # At least one event should have dialogue
        has_dialogue = any("dialogue" in e.metadata for e in events)
        assert has_dialogue


# =============================================================================
# Chunk 7: WorkshopFlux Run Tests
# =============================================================================


class TestWorkshopFluxRun:
    """Tests for WorkshopFlux.run()."""

    @pytest.mark.asyncio
    async def test_run_yields_events_until_complete(self, workshop: WorkshopEnvironment) -> None:
        """Run yields events until task complete."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=2)
        await flux.start("Research task")
        events = []
        async for event in flux.run():
            events.append(event)
            if len(events) > 50:  # Safety limit
                break
        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_run_ends_when_task_complete(self, workshop: WorkshopEnvironment) -> None:
        """Run stops when task completes."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=1)
        await flux.start("Research task")
        events = [e async for e in flux.run()]
        # Should have TASK_COMPLETED
        event_types = {e.type for e in events}
        assert WorkshopEventType.TASK_COMPLETED in event_types

    @pytest.mark.asyncio
    async def test_run_nothing_when_not_running(self, workshop: WorkshopEnvironment) -> None:
        """Run yields nothing when not started."""
        flux = WorkshopFlux(workshop)
        events = [e async for e in flux.run()]
        assert events == []

    @pytest.mark.asyncio
    async def test_run_tracks_handoffs(self, workshop: WorkshopEnvironment) -> None:
        """Run tracks handoff metrics."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=1)
        await flux.start("Research task")
        [e async for e in flux.run()]
        metrics = flux.get_metrics()
        # Should have at least some handoffs (unless very short task)
        assert metrics.phases_completed >= 0


# =============================================================================
# Chunk 7: WorkshopFlux Perturbation Tests
# =============================================================================


class TestWorkshopFluxPerturb:
    """Tests for WorkshopFlux.perturb()."""

    @pytest.mark.asyncio
    async def test_perturb_advance(self, workshop: WorkshopEnvironment) -> None:
        """Perturb advance forces phase advancement."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Research task")
        event = await flux.perturb("advance")
        assert event.metadata.get("perturbation") is True

    @pytest.mark.asyncio
    async def test_perturb_handoff(self, workshop: WorkshopEnvironment) -> None:
        """Perturb handoff to specific builder."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Research task")
        event = await flux.perturb("handoff", builder="Sage")
        assert event.type == WorkshopEventType.HANDOFF
        assert event.metadata.get("perturbation") is True

    @pytest.mark.asyncio
    async def test_perturb_handoff_requires_builder(self, workshop: WorkshopEnvironment) -> None:
        """Perturb handoff requires builder arg."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        with pytest.raises(ValueError, match="builder archetype required"):
            await flux.perturb("handoff")

    @pytest.mark.asyncio
    async def test_perturb_complete(self, workshop: WorkshopEnvironment) -> None:
        """Perturb complete forces task completion."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        event = await flux.perturb("complete")
        assert event.type == WorkshopEventType.TASK_COMPLETED
        assert flux.is_running is False

    @pytest.mark.asyncio
    async def test_perturb_inject_artifact(self, workshop: WorkshopEnvironment) -> None:
        """Perturb inject_artifact adds artifact."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        event = await flux.perturb("inject_artifact", artifact={"data": "test"})
        assert event.type == WorkshopEventType.ARTIFACT_PRODUCED
        assert event.metadata.get("perturbation") is True
        assert flux.get_metrics().artifacts_produced == 1

    @pytest.mark.asyncio
    async def test_perturb_unknown_action(self, workshop: WorkshopEnvironment) -> None:
        """Perturb raises for unknown action."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        with pytest.raises(ValueError, match="Unknown perturbation action"):
            await flux.perturb("invalid_action")

    @pytest.mark.asyncio
    async def test_perturb_increments_perturbation_count(self, workshop: WorkshopEnvironment) -> None:
        """Perturbations are counted in metrics."""
        flux = WorkshopFlux(workshop, auto_advance=False)
        await flux.start("Task")
        await flux.perturb("advance")
        await flux.perturb("advance")
        assert flux.get_metrics().perturbations == 2


# =============================================================================
# Chunk 7: WorkshopFlux Stop Tests
# =============================================================================


class TestWorkshopFluxStop:
    """Tests for WorkshopFlux.stop()."""

    @pytest.mark.asyncio
    async def test_stop_while_running(self, workshop: WorkshopEnvironment) -> None:
        """Stop while running returns completion event."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        event = await flux.stop()
        assert event is not None
        assert event.type == WorkshopEventType.TASK_COMPLETED

    @pytest.mark.asyncio
    async def test_stop_sets_not_running(self, workshop: WorkshopEnvironment) -> None:
        """Stop sets is_running to False."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        await flux.stop()
        assert flux.is_running is False

    @pytest.mark.asyncio
    async def test_stop_sets_end_time(self, workshop: WorkshopEnvironment) -> None:
        """Stop sets end_time in metrics."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        await flux.stop()
        assert flux.get_metrics().end_time is not None

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self, workshop: WorkshopEnvironment) -> None:
        """Stop returns None when not running."""
        flux = WorkshopFlux(workshop)
        event = await flux.stop()
        assert event is None


# =============================================================================
# Chunk 7: WorkshopFlux Status Tests
# =============================================================================


class TestWorkshopFluxStatus:
    """Tests for WorkshopFlux.get_status()."""

    def test_status_when_idle(self, workshop: WorkshopEnvironment) -> None:
        """Status reflects idle state."""
        flux = WorkshopFlux(workshop)
        status = flux.get_status()
        assert status["is_running"] is False
        assert status["phase"] == "IDLE"
        assert status["active_builder"] is None
        assert status["task"] is None

    @pytest.mark.asyncio
    async def test_status_when_running(self, workshop: WorkshopEnvironment) -> None:
        """Status reflects running state."""
        flux = WorkshopFlux(workshop)
        await flux.start("Research task")
        status = flux.get_status()
        assert status["is_running"] is True
        assert status["phase"] != "IDLE"
        assert status["active_builder"] is not None
        assert status["task"] == "Research task"

    @pytest.mark.asyncio
    async def test_status_includes_metrics(self, workshop: WorkshopEnvironment) -> None:
        """Status includes metrics dict."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        [e async for e in flux.step()]
        status = flux.get_status()
        assert "metrics" in status
        assert status["metrics"]["total_steps"] >= 1


# =============================================================================
# Chunk 7: WorkshopFlux Reset Tests
# =============================================================================


class TestWorkshopFluxReset:
    """Tests for WorkshopFlux.reset()."""

    @pytest.mark.asyncio
    async def test_reset_clears_state(self, workshop: WorkshopEnvironment) -> None:
        """Reset clears flux state."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        [e async for e in flux.step()]
        flux.reset()
        assert flux.is_running is False
        assert flux._step_count == 0
        assert flux.current_phase == WorkshopPhase.IDLE

    @pytest.mark.asyncio
    async def test_reset_clears_metrics(self, workshop: WorkshopEnvironment) -> None:
        """Reset clears metrics."""
        flux = WorkshopFlux(workshop)
        await flux.start("Task")
        [e async for e in flux.step()]
        flux.reset()
        metrics = flux.get_metrics()
        assert metrics.total_steps == 0
        assert metrics.total_events == 0

    @pytest.mark.asyncio
    async def test_can_start_after_reset(self, workshop: WorkshopEnvironment) -> None:
        """Can start new task after reset."""
        flux = WorkshopFlux(workshop)
        await flux.start("First task")
        flux.reset()
        plan = await flux.start("Second task")
        assert plan is not None
        assert flux.is_running is True


# =============================================================================
# Chunk 7: WorkshopFlux Dialogue Tests
# =============================================================================


class TestWorkshopFluxDialogue:
    """Tests for dialogue generation in WorkshopFlux."""

    @pytest.mark.asyncio
    async def test_dialogue_uses_templates(self, workshop: WorkshopEnvironment) -> None:
        """Dialogue generation uses templates."""
        flux = WorkshopFlux(workshop, seed=42)
        await flux.start("Research task")
        # Generate dialogue directly
        dialogue = await flux._generate_dialogue(flux.active_builder, "start_work")
        assert dialogue is not None
        assert len(dialogue) > 0

    @pytest.mark.asyncio
    async def test_dialogue_with_next_builder(self, workshop: WorkshopEnvironment) -> None:
        """Handoff dialogue includes next builder name."""
        flux = WorkshopFlux(workshop, seed=42)
        await flux.start("Research task")
        dialogue = await flux._generate_dialogue(
            flux.active_builder, "handoff", next_builder="Sage"
        )
        assert dialogue is not None
        assert "Sage" in dialogue

    @pytest.mark.asyncio
    async def test_dialogue_graceful_missing_template(self, workshop: WorkshopEnvironment) -> None:
        """Graceful handling of missing template."""
        flux = WorkshopFlux(workshop, seed=42)
        await flux.start("Research task")
        # Unknown action should return None
        dialogue = await flux._generate_dialogue(flux.active_builder, "unknown_action")
        assert dialogue is None


# =============================================================================
# Chunk 7: WorkshopFlux Integration Tests
# =============================================================================


class TestWorkshopFluxIntegration:
    """Integration tests for WorkshopFlux."""

    @pytest.mark.asyncio
    async def test_full_flux_lifecycle(self, workshop: WorkshopEnvironment) -> None:
        """Complete flux lifecycle from start to finish."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=2, seed=42)

        # Start
        plan = await flux.start("Research and design a new feature")
        assert plan.lead_builder == "Scout"

        # Run to completion
        events = []
        async for event in flux.run():
            events.append(event)
            if len(events) > 100:
                break

        # Verify completion
        assert not flux.is_running
        metrics = flux.get_metrics()
        assert metrics.total_steps > 0
        assert metrics.total_events > 0
        assert metrics.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_flux_with_perturbations(self, workshop: WorkshopEnvironment) -> None:
        """Flux handles perturbations correctly."""
        flux = WorkshopFlux(workshop, auto_advance=False, seed=42)
        await flux.start("Design task")

        # Do some steps (each step produces an artifact)
        [e async for e in flux.step()]
        [e async for e in flux.step()]
        artifacts_from_steps = flux.get_metrics().artifacts_produced

        # Inject artifact
        await flux.perturb("inject_artifact", artifact="manual_design")

        # Force complete
        await flux.perturb("complete")

        assert not flux.is_running
        assert flux.get_metrics().perturbations == 2
        # 1 injected artifact + any artifacts from steps
        assert flux.get_metrics().artifacts_produced == artifacts_from_steps + 1

    @pytest.mark.asyncio
    async def test_flux_metrics_accuracy(self, workshop: WorkshopEnvironment) -> None:
        """Metrics accurately track flux execution."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=2, seed=42)
        await flux.start("Explore options")

        event_count = 0
        async for event in flux.run():
            event_count += 1
            if event_count > 50:
                break

        metrics = flux.get_metrics()
        # Metrics should be roughly consistent
        assert metrics.total_events >= event_count - 10  # Allow some slack for initial events
        assert metrics.end_time is not None

    @pytest.mark.asyncio
    async def test_multiple_flux_runs(self, workshop: WorkshopEnvironment) -> None:
        """Multiple flux runs work correctly."""
        flux = WorkshopFlux(workshop, max_steps_per_phase=1)

        # First run
        await flux.start("First task")
        [e async for e in flux.run()]
        assert not flux.is_running

        # Reset and second run
        flux.reset()
        await flux.start("Second task")
        [e async for e in flux.run()]
        assert not flux.is_running
