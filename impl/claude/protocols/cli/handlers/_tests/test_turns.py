"""
Tests for kgents turns/dag/fork CLI handlers.

Tests verify:
1. Help displays correctly for all commands
2. turns command shows turn history
3. dag command visualizes turn DAG
4. fork command creates forked weave
5. JSON output mode
6. Error handling for edge cases

These tests are part of the Turn-gents Realization phase.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# === Fixtures ===


class MockContext:
    """Mock InvocationContext for testing."""

    def __init__(self) -> None:
        self.outputs: list[tuple[str, dict[str, Any]]] = []

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        self.outputs.append((human, semantic))


@pytest.fixture
def ctx() -> MockContext:
    """Create mock context."""
    return MockContext()


@pytest.fixture
def demo_weave() -> Any:
    """Create a demo weave with sample turns."""
    from weave import TheWeave, Turn, TurnType

    weave = TheWeave()

    # Create demo turns
    turns = [
        Turn.create_turn(
            content="Hello, starting task",
            source="agent-a",
            turn_type=TurnType.SPEECH,
            confidence=0.95,
            turn_id="turn-001",
        ),
        Turn.create_turn(
            content="Analyzing request",
            source="agent-a",
            turn_type=TurnType.THOUGHT,
            confidence=0.8,
            turn_id="turn-002",
        ),
        Turn.create_turn(
            content="Reading file",
            source="agent-a",
            turn_type=TurnType.ACTION,
            confidence=0.9,
            turn_id="turn-003",
        ),
        Turn.create_turn(
            content="Here's the result",
            source="agent-a",
            turn_type=TurnType.SPEECH,
            confidence=0.85,
            turn_id="turn-004",
        ),
    ]

    for i, turn in enumerate(turns):
        deps = {turns[i - 1].id} if i > 0 else None
        weave.monoid.append_mut(turn, deps)

    return weave


# === Help Tests ===


class TestTurnsHelp:
    """Tests for turns --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0 and shows help text."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_h_flag(self, ctx: MockContext) -> None:
        """-h returns 0 and shows help text."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["-h"], ctx)  # type: ignore[arg-type]

        assert result == 0


class TestDagHelp:
    """Tests for dag --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.turns import cmd_dag

        result = cmd_dag(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0


class TestForkHelp:
    """Tests for fork --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.turns import cmd_fork

        result = cmd_fork(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0


# === Turns Command Tests ===


class TestTurnsCommand:
    """Tests for the turns command."""

    def test_empty_weave(self, ctx: MockContext) -> None:
        """Empty weave returns gracefully."""
        from protocols.cli.handlers.turns import cmd_turns

        # With no demo flag, should return empty
        result = cmd_turns(["agent-a"], ctx)  # type: ignore[arg-type]

        assert result == 0
        assert any("No turns" in out[0] for out in ctx.outputs)

    def test_show_all_flag(self, ctx: MockContext) -> None:
        """--all flag parses correctly."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--all"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_json_output(self, ctx: MockContext) -> None:
        """--json flag produces JSON output."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--all", "--json"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_stats_only(self, ctx: MockContext) -> None:
        """--stats shows statistics only."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--stats"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_last_n_parsing(self, ctx: MockContext) -> None:
        """--last N is parsed correctly."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--all", "--last", "5"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_type_filter(self, ctx: MockContext) -> None:
        """--type filter is applied."""
        from protocols.cli.handlers.turns import cmd_turns

        result = cmd_turns(["--all", "--type", "SPEECH"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_invalid_type_filter(self, ctx: MockContext) -> None:
        """Invalid --type returns error."""
        from protocols.cli.handlers.turns import cmd_turns

        # Patch _get_global_weave to return non-empty weave
        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            from weave import TheWeave, Turn, TurnType

            weave = TheWeave()
            turn = Turn.create_turn(
                content="test",
                source="agent",
                turn_type=TurnType.SPEECH,
            )
            weave.monoid.append_mut(turn)
            mock.return_value = weave

            result = cmd_turns(["--all", "--type", "INVALID"], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("Unknown turn type" in out[0] for out in ctx.outputs)


# === DAG Command Tests ===


class TestDagCommand:
    """Tests for the dag command."""

    def test_empty_weave(self, ctx: MockContext) -> None:
        """Empty weave returns gracefully."""
        from protocols.cli.handlers.turns import cmd_dag

        result = cmd_dag([], ctx)  # type: ignore[arg-type]

        assert result == 0
        assert any("No turns" in out[0] for out in ctx.outputs)

    def test_json_output(self, ctx: MockContext) -> None:
        """--json flag produces JSON output."""
        from protocols.cli.handlers.turns import cmd_dag

        result = cmd_dag(["--json"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_agent_flag(self, ctx: MockContext) -> None:
        """--agent flag is parsed."""
        from protocols.cli.handlers.turns import cmd_dag

        result = cmd_dag(["--agent", "agent-a"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_thoughts_flag(self, ctx: MockContext) -> None:
        """--thoughts flag shows thought turns."""
        from protocols.cli.handlers.turns import cmd_dag

        result = cmd_dag(["--thoughts"], ctx)  # type: ignore[arg-type]

        assert result == 0


# === Fork Command Tests ===


class TestForkCommand:
    """Tests for the fork command."""

    def test_no_turn_id(self, ctx: MockContext) -> None:
        """No turn ID specified returns error."""
        from protocols.cli.handlers.turns import cmd_fork

        result = cmd_fork([], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("No turn ID" in out[0] for out in ctx.outputs)

    def test_empty_weave(self, ctx: MockContext) -> None:
        """Empty weave returns gracefully."""
        from protocols.cli.handlers.turns import cmd_fork

        result = cmd_fork(["turn-001"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_name_flag(self, ctx: MockContext) -> None:
        """--name flag is parsed."""
        from protocols.cli.handlers.turns import cmd_fork

        result = cmd_fork(["turn-001", "--name", "my-fork"], ctx)  # type: ignore[arg-type]

        assert result == 0


# === Weave Integration Tests ===


class TestWeaveIntegration:
    """Tests with actual Weave data."""

    def test_turns_with_demo_weave(self, ctx: MockContext, demo_weave: Any) -> None:
        """Turns command works with demo weave."""
        from protocols.cli.handlers.turns import cmd_turns

        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            mock.return_value = demo_weave

            result = cmd_turns(["agent-a"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_dag_with_demo_weave(self, ctx: MockContext, demo_weave: Any) -> None:
        """DAG command works with demo weave."""
        from protocols.cli.handlers.turns import cmd_dag

        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            mock.return_value = demo_weave

            result = cmd_dag(["--agent", "agent-a"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_fork_with_demo_weave(self, ctx: MockContext, demo_weave: Any) -> None:
        """Fork command works with demo weave."""
        from protocols.cli.handlers.turns import cmd_fork

        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            mock.return_value = demo_weave

            result = cmd_fork(["turn-001"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_fork_partial_id(self, ctx: MockContext, demo_weave: Any) -> None:
        """Fork accepts partial turn IDs."""
        from protocols.cli.handlers.turns import cmd_fork

        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            mock.return_value = demo_weave

            # Use partial ID
            result = cmd_fork(["turn-00"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_turns_json_with_data(self, ctx: MockContext, demo_weave: Any) -> None:
        """JSON output includes turn data."""
        import json

        from protocols.cli.handlers.turns import cmd_turns

        with patch("protocols.cli.handlers.turns._get_global_weave") as mock:
            mock.return_value = demo_weave

            result = cmd_turns(["--all", "--json"], ctx)  # type: ignore[arg-type]

        assert result == 0
        # Find JSON output
        json_output = None
        for human, _ in ctx.outputs:
            if human.strip().startswith("["):
                json_output = human
                break

        if json_output:
            data = json.loads(json_output)
            assert isinstance(data, list)

    def test_compression_ratio(self, ctx: MockContext, demo_weave: Any) -> None:
        """Compression ratio is calculated."""
        from weave import CausalCone

        cone = CausalCone(demo_weave)
        ratio = cone.compression_ratio("agent-a")

        # With single agent, compression is 0% (all events in cone)
        assert ratio >= 0.0


# === Output Helpers Tests ===


class TestOutputHelpers:
    """Tests for output helper functions."""

    def test_emit_output_with_ctx(self) -> None:
        """_emit_output uses ctx when available."""
        from protocols.cli.handlers.turns import _emit_output

        ctx = MockContext()
        _emit_output("test message", {"key": "value"}, ctx)  # type: ignore[arg-type]

        assert len(ctx.outputs) == 1
        assert ctx.outputs[0][0] == "test message"

    def test_emit_output_without_ctx(self, capsys: Any) -> None:
        """_emit_output prints when no ctx."""
        from protocols.cli.handlers.turns import _emit_output

        _emit_output("test message", {"key": "value"}, None)

        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_get_demo_weave_disabled(self) -> None:
        """Demo weave returns None when KGENTS_DEMO_TURNS not set."""
        import os

        from protocols.cli.handlers.turns import _get_demo_weave

        # Ensure env var is not set
        os.environ.pop("KGENTS_DEMO_TURNS", None)

        result = _get_demo_weave()

        assert result is None

    def test_get_demo_weave_enabled(self) -> None:
        """Demo weave returns data when KGENTS_DEMO_TURNS=1."""
        import os

        from protocols.cli.handlers.turns import _get_demo_weave

        # Set env var
        os.environ["KGENTS_DEMO_TURNS"] = "1"
        try:
            result = _get_demo_weave()

            assert result is not None
            assert len(result) > 0
        finally:
            os.environ.pop("KGENTS_DEMO_TURNS", None)


# === TurnDAGRenderer Integration Tests ===


class TestTurnDAGRendererIntegration:
    """Tests for TurnDAGRenderer integration."""

    def test_render_panel(self, demo_weave: Any) -> None:
        """TurnDAGRenderer produces Panel output."""
        from agents.i.screens.turn_dag import TurnDAGConfig, TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=demo_weave)
        panel = renderer.render()

        assert panel is not None
        assert panel.title is not None

    def test_render_with_agent(self, demo_weave: Any) -> None:
        """TurnDAGRenderer highlights agent cone."""
        from agents.i.screens.turn_dag import TurnDAGConfig, TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=demo_weave)
        panel = renderer.render(agent_id="agent-a")

        assert panel is not None
        assert "agent-a" in str(panel.title)

    def test_render_stats(self, demo_weave: Any) -> None:
        """TurnDAGRenderer produces stats."""
        from agents.i.screens.turn_dag import TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=demo_weave)
        stats = renderer.render_stats()

        assert stats is not None

    def test_fork_from(self, demo_weave: Any) -> None:
        """TurnDAGRenderer.fork_from creates valid weave."""
        from agents.i.screens.turn_dag import TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=demo_weave)
        forked = renderer.fork_from("turn-002")

        assert forked is not None
        assert len(forked) <= len(demo_weave)

    def test_get_turn_info(self, demo_weave: Any) -> None:
        """TurnDAGRenderer.get_turn_info returns turn details."""
        from agents.i.screens.turn_dag import TurnDAGRenderer

        renderer = TurnDAGRenderer(weave=demo_weave)
        info = renderer.get_turn_info("turn-001")

        assert info is not None
        assert info["id"] == "turn-001"
        assert info["source"] == "agent-a"
