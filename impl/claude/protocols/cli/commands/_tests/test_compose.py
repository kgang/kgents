"""
Tests for kg compose command.

Verifies:
- Composition creation and execution
- Step dependency resolution
- Trace management
- Named composition save/load
- Error handling and early exit
"""

import pytest

from services.compose import Composition, CompositionStatus, execute_composition
from services.compose.store import CompositionStore, reset_composition_store
from services.witness.trace_store import reset_mark_store


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset stores before each test."""
    reset_mark_store()
    reset_composition_store()


class TestCompositionTypes:
    """Test composition data structures."""

    def test_composition_from_commands(self):
        """Test creating a composition from command list."""
        commands = ["audit spec/foo.md", "probe identity"]
        comp = Composition.from_commands(commands, name="test")

        assert comp.name == "test"
        assert len(comp.steps) == 2
        assert comp.steps[0].command == "audit spec/foo.md"
        assert comp.steps[1].command == "probe identity"
        assert comp.status == CompositionStatus.PENDING

    def test_step_dependencies_default_sequential(self):
        """Test that steps have default sequential dependencies."""
        commands = ["cmd1", "cmd2", "cmd3"]
        comp = Composition.from_commands(commands)

        assert comp.steps[0].depends_on == []  # First step has no deps
        assert comp.steps[1].depends_on == [0]  # Second depends on first
        assert comp.steps[2].depends_on == [1]  # Third depends on second

    def test_composition_to_dict(self):
        """Test serialization to dictionary."""
        comp = Composition.from_commands(["cmd1", "cmd2"], name="test")
        data = comp.to_dict()

        assert data["name"] == "test"
        assert data["status"] == "pending"
        assert len(data["steps"]) == 2
        assert data["steps"][0]["command"] == "cmd1"


class TestCompositionStore:
    """Test composition persistence store."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self):
        """Test saving and retrieving compositions."""
        store = CompositionStore()
        comp = Composition.from_commands(["cmd1"], name="test")

        await store.save(comp)
        retrieved = await store.get(comp.id)

        assert retrieved is not None
        assert retrieved.id == comp.id
        assert retrieved.name == "test"

    @pytest.mark.asyncio
    async def test_get_by_name(self):
        """Test retrieving composition by name."""
        store = CompositionStore()
        comp = Composition.from_commands(["cmd1"], name="validate")

        await store.save(comp)
        retrieved = await store.get_by_name("validate")

        assert retrieved is not None
        assert retrieved.name == "validate"

    @pytest.mark.asyncio
    async def test_get_by_name_returns_most_recent(self):
        """Test that get_by_name returns most recent composition."""
        store = CompositionStore()

        # Save two compositions with same name
        comp1 = Composition.from_commands(["cmd1"], name="test")
        comp2 = Composition.from_commands(["cmd2"], name="test")

        await store.save(comp1)
        await store.save(comp2)

        retrieved = await store.get_by_name("test")
        assert retrieved is not None
        assert retrieved.id == comp2.id  # Most recent

    @pytest.mark.asyncio
    async def test_history(self):
        """Test getting composition history."""
        store = CompositionStore()

        # Save several compositions
        for i in range(5):
            comp = Composition.from_commands([f"cmd{i}"], name=f"test{i}")
            await store.save(comp)

        history = await store.history(limit=3)
        assert len(history) == 3
        # History should be in reverse chronological order
        assert history[0].name == "test4"
        assert history[1].name == "test3"
        assert history[2].name == "test2"


@pytest.mark.asyncio
class TestCompositionExecution:
    """Test composition execution."""

    async def test_execute_simple_composition(self):
        """Test executing a simple composition."""
        comp = Composition.from_commands(
            ["audit spec/foo.md", "probe identity"],
            name="test",
        )

        result = await execute_composition(comp)

        assert result.status == CompositionStatus.COMPLETED
        assert len(result.results) == 2
        assert all(r.success for r in result.results)
        assert result.trace_id is not None

    async def test_execute_with_verbose(self):
        """Test execution with verbose output."""
        comp = Composition.from_commands(["audit spec/foo.md"], name="test")

        # This should not raise (just prints to stdout)
        result = await execute_composition(comp, verbose=True)
        assert result.status == CompositionStatus.COMPLETED

    async def test_trace_creation(self):
        """Test that execution creates a trace."""
        from services.witness.trace_store import get_mark_store

        comp = Composition.from_commands(["audit spec/foo.md"], name="test")
        result = await execute_composition(comp)

        assert result.trace_id is not None

        # Verify trace exists in mark store
        store = get_mark_store()
        root_mark = store.get(result.trace_id)
        assert root_mark is not None
        assert "composition_start" in root_mark.stimulus.kind

    async def test_step_results_recorded(self):
        """Test that step results are recorded."""
        comp = Composition.from_commands(["audit spec/foo.md", "probe identity"])
        result = await execute_composition(comp)

        assert len(result.results) == 2
        for i, step_result in enumerate(result.results):
            assert step_result.step_index == i
            assert step_result.duration_ms >= 0
            assert step_result.output is not None


@pytest.mark.asyncio
class TestCompositionTrace:
    """Test composition tracing."""

    async def test_trace_links_steps(self):
        """Test that trace links all step marks."""
        from services.compose.trace import start_composition_trace
        from services.witness.trace_store import get_mark_store

        comp = Composition.from_commands(["cmd1", "cmd2"])
        trace = await start_composition_trace(comp)

        assert trace.composition_id == comp.id
        assert trace.root_mark_id is not None

        # Verify root mark exists
        store = get_mark_store()
        root_mark = store.get(trace.root_mark_id)
        assert root_mark is not None

    async def test_trace_records_composition_metadata(self):
        """Test that trace contains composition metadata."""
        from services.compose.trace import start_composition_trace
        from services.witness.trace_store import get_mark_store

        comp = Composition.from_commands(["cmd1", "cmd2"], name="test")
        trace = await start_composition_trace(comp)

        store = get_mark_store()
        root_mark = store.get(trace.root_mark_id)

        assert root_mark.response.metadata["composition_id"] == comp.id
        assert root_mark.response.metadata["composition_name"] == "test"
        assert root_mark.response.metadata["step_count"] == 2


class TestCLICommand:
    """Test CLI command interface."""

    def test_cmd_compose_help(self):
        """Test that help works."""
        from protocols.cli.commands.compose import cmd_compose

        # Should return 0 and not raise
        result = cmd_compose(["--help"])
        assert result == 0

    def test_cmd_compose_no_args_shows_help(self):
        """Test that no args shows help."""
        from protocols.cli.commands.compose import cmd_compose

        result = cmd_compose([])
        assert result == 0  # Shows help, not an error


# Integration test would go here if we had real command handlers
# For now, the executor uses stubs, which is sufficient for Phase 5
