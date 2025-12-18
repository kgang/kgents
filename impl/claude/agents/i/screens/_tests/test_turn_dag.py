"""
Tests for TurnDAGRenderer - Phase 6 of Turn-gents Protocol.

Tests cover:
1. TurnDAGConfig options
2. TurnNode creation
3. DAG rendering
4. Thought collapse
5. Cone highlighting
6. Fork/rewind capability
7. Statistics rendering
"""

import pytest

from weave import TheWeave, Turn, TurnType


class TestTurnDAGConfig:
    """Tests for TurnDAGConfig defaults."""

    def test_default_config_hides_thoughts(self) -> None:
        """Thoughts are collapsed by default."""
        from ..turn_dag import TurnDAGConfig

        config = TurnDAGConfig()
        assert config.show_thoughts is False

    def test_default_config_shows_confidence(self) -> None:
        """Confidence is shown by default."""
        from ..turn_dag import TurnDAGConfig

        config = TurnDAGConfig()
        assert config.show_confidence is True

    def test_default_config_highlights_cone(self) -> None:
        """Cone highlighting is on by default."""
        from ..turn_dag import TurnDAGConfig

        config = TurnDAGConfig()
        assert config.highlight_cone is True


class TestTurnNode:
    """Tests for TurnNode dataclass."""

    def test_turn_node_creation(self) -> None:
        """Can create a TurnNode."""
        from ..turn_dag import TurnNode

        node = TurnNode(
            turn_id="test-123",
            source="agent-a",
            turn_type="SPEECH",
            content_preview="Hello world",
            confidence=0.95,
            entropy_cost=0.01,
            timestamp=1234567890.0,
            is_yield=False,
            is_approved=False,
            dependencies=set(),
        )

        assert node.turn_id == "test-123"
        assert node.source == "agent-a"
        assert node.turn_type == "SPEECH"
        assert not node.in_cone  # Default

    def test_turn_node_in_cone(self) -> None:
        """Can set in_cone flag."""
        from ..turn_dag import TurnNode

        node = TurnNode(
            turn_id="test",
            source="agent",
            turn_type="SPEECH",
            content_preview="",
            confidence=1.0,
            entropy_cost=0.0,
            timestamp=0.0,
            is_yield=False,
            is_approved=False,
            dependencies=set(),
            in_cone=True,
        )

        assert node.in_cone is True


class TestTurnDAGRenderer:
    """Tests for TurnDAGRenderer core functionality."""

    def test_render_empty_weave(self) -> None:
        """Can render empty weave."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)
        panel = renderer.render()

        assert panel is not None
        assert "Turn DAG" in str(panel.title)

    def test_render_with_turns(self) -> None:
        """Can render weave with turns."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        turn = Turn.create_turn(
            content="Hello",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn, None)

        renderer = TurnDAGRenderer(weave=weave)
        panel = renderer.render()

        assert panel is not None

    def test_render_with_agent_cone(self) -> None:
        """Can render with agent cone highlighted."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        turn = Turn.create_turn(
            content="Hello",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn, None)

        renderer = TurnDAGRenderer(weave=weave)
        panel = renderer.render(agent_id="agent-a")

        assert "agent-a" in str(panel.title)

    def test_thought_collapse(self) -> None:
        """Thoughts are collapsed when config says so."""
        from ..turn_dag import TurnDAGConfig, TurnDAGRenderer

        weave = TheWeave()

        # Add speech and thought
        speech = Turn.create_turn(
            content="Speech",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        thought = Turn.create_turn(
            content="Thinking...",
            source="agent",
            turn_type=TurnType.THOUGHT,
        )
        weave.monoid.append_mut(speech, None)
        weave.monoid.append_mut(thought, {speech.id})

        # With thoughts collapsed (default)
        config = TurnDAGConfig(show_thoughts=False)
        renderer = TurnDAGRenderer(weave=weave, config=config)
        renderer._build_nodes(None)

        # Only speech should be in nodes
        assert len(renderer._nodes) == 1
        assert renderer._nodes[0].turn_type == "SPEECH"

    def test_thought_visible(self) -> None:
        """Thoughts visible when enabled."""
        from ..turn_dag import TurnDAGConfig, TurnDAGRenderer

        weave = TheWeave()

        speech = Turn.create_turn(
            content="Speech",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        thought = Turn.create_turn(
            content="Thinking...",
            source="agent",
            turn_type=TurnType.THOUGHT,
        )
        weave.monoid.append_mut(speech, None)
        weave.monoid.append_mut(thought, {speech.id})

        # With thoughts visible
        config = TurnDAGConfig(show_thoughts=True)
        renderer = TurnDAGRenderer(weave=weave, config=config)
        renderer._build_nodes(None)

        # Both should be in nodes
        assert len(renderer._nodes) == 2


class TestRenderCone:
    """Tests for cone rendering."""

    def test_render_cone_tree(self) -> None:
        """Can render causal cone as tree."""
        from weave import CausalCone

        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        turn = Turn.create_turn(
            content="Hello",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn, None)

        cone = CausalCone(weave)
        renderer = TurnDAGRenderer(weave=weave)
        tree = renderer.render_cone(cone, "agent-a")

        assert tree is not None
        assert "agent-a" in str(tree.label)


class TestRenderStats:
    """Tests for statistics rendering."""

    def test_empty_stats(self) -> None:
        """Stats for empty weave."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)
        stats = renderer.render_stats()

        assert "No turns recorded" in str(stats)

    def test_stats_with_turns(self) -> None:
        """Stats include turn counts."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        for i in range(3):
            turn = Turn.create_turn(
                content=f"Turn {i}",
                source="agent",
                turn_type=TurnType.SPEECH,
            )
            weave.monoid.append_mut(turn, None)

        renderer = TurnDAGRenderer(weave=weave)
        stats = renderer.render_stats()

        assert "Total Turns: 3" in str(stats)
        assert "SPEECH" in str(stats)


class TestGetTurnInfo:
    """Tests for get_turn_info method."""

    def test_get_existing_turn(self) -> None:
        """Can get info for existing turn."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        turn = Turn.create_turn(
            content="Hello",
            source="agent-a",
            turn_type=TurnType.SPEECH,
            confidence=0.9,
        )
        weave.monoid.append_mut(turn, None)

        renderer = TurnDAGRenderer(weave=weave)
        info = renderer.get_turn_info(turn.id)

        assert info is not None
        assert info["id"] == turn.id
        assert info["source"] == "agent-a"
        assert info["content"] == "Hello"
        assert info["confidence"] == 0.9

    def test_get_nonexistent_turn(self) -> None:
        """Returns None for nonexistent turn."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)
        info = renderer.get_turn_info("nonexistent")

        assert info is None


class TestForkFrom:
    """Tests for fork/rewind functionality."""

    def test_fork_creates_new_weave(self) -> None:
        """Fork creates a new weave."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()

        turn1 = Turn.create_turn(
            content="First",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        turn2 = Turn.create_turn(
            content="Second",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn1, None)
        weave.monoid.append_mut(turn2, {turn1.id})

        renderer = TurnDAGRenderer(weave=weave)

        # Fork from first turn
        forked = renderer.fork_from(turn1.id)

        # Forked weave should only have turn1
        assert len(forked) == 1

    def test_fork_preserves_history(self) -> None:
        """Fork preserves history up to fork point."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()

        turn1 = Turn.create_turn(
            content="First",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        turn2 = Turn.create_turn(
            content="Second",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        turn3 = Turn.create_turn(
            content="Third",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn1, None)
        weave.monoid.append_mut(turn2, {turn1.id})
        weave.monoid.append_mut(turn3, {turn2.id})

        renderer = TurnDAGRenderer(weave=weave)

        # Fork from second turn
        forked = renderer.fork_from(turn2.id)

        # Forked weave should have turn1 and turn2
        assert len(forked) == 2

    def test_fork_includes_dependencies(self) -> None:
        """Fork includes all dependencies."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()

        turn1 = Turn.create_turn(
            content="First",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )
        turn2 = Turn.create_turn(
            content="Second",
            source="agent-b",
            turn_type=TurnType.SPEECH,
        )
        turn3 = Turn.create_turn(
            content="Third",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn1, None)
        weave.monoid.append_mut(turn2, None)
        # Turn3 depends on both turn1 and turn2
        weave.monoid.append_mut(turn3, {turn1.id, turn2.id})

        renderer = TurnDAGRenderer(weave=weave)

        # Fork from turn3
        forked = renderer.fork_from(turn3.id)

        # Forked weave should have all three turns
        assert len(forked) == 3


class TestConvenienceFunction:
    """Tests for render_turn_dag convenience function."""

    def test_render_turn_dag_basic(self) -> None:
        """Can use convenience function."""
        from ..turn_dag import render_turn_dag

        weave = TheWeave()
        panel = render_turn_dag(weave)

        assert panel is not None

    def test_render_turn_dag_with_agent(self) -> None:
        """Convenience function accepts agent_id."""
        from ..turn_dag import render_turn_dag

        weave = TheWeave()
        turn = Turn.create_turn(
            content="Hello",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        weave.monoid.append_mut(turn, None)

        panel = render_turn_dag(weave, agent_id="agent")

        assert "agent" in str(panel.title)

    def test_render_turn_dag_show_thoughts(self) -> None:
        """Convenience function accepts show_thoughts."""
        from ..turn_dag import render_turn_dag

        weave = TheWeave()
        panel = render_turn_dag(weave, show_thoughts=True)

        assert panel is not None


class TestTypeColors:
    """Tests for turn type color mapping."""

    def test_speech_is_green(self) -> None:
        """SPEECH turns are green."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)

        assert renderer._type_color("SPEECH") == "green"

    def test_action_is_blue(self) -> None:
        """ACTION turns are blue."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)

        assert renderer._type_color("ACTION") == "blue"

    def test_yield_is_yellow(self) -> None:
        """YIELD turns are yellow."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)

        assert renderer._type_color("YIELD") == "yellow"

    def test_thought_is_dim(self) -> None:
        """THOUGHT turns are dim."""
        from ..turn_dag import TurnDAGRenderer

        weave = TheWeave()
        renderer = TurnDAGRenderer(weave=weave)

        assert renderer._type_color("THOUGHT") == "dim"
