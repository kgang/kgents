"""
Tests for I-gent TUI Renderer.

Tests the terminal UI rendering:
- Field rendering
- Color application
- Metrics bars
- Compost heap (event log)
- Keyboard handling
"""

from agents.i.field import (
    DialecticPhase,
    Entity,
    EntityType,
    FieldState,
    create_demo_field,
)
from agents.i.tui import (
    Color,
    FieldRenderer,
    KeyHandler,
    RenderConfig,
    get_entity_color,
    get_log_color,
    get_phase_color,
    render_field_once,
)


class TestColors:
    """Tests for color functions."""

    def test_entity_colors(self) -> None:
        """Test entity color mapping."""
        # ID and Compose are cyan
        id_entity = Entity(id="i", entity_type=EntityType.ID, x=0, y=0)
        assert Color.CYAN.value in get_entity_color(id_entity)

        compose_entity = Entity(id="c", entity_type=EntityType.COMPOSE, x=0, y=0)
        assert Color.CYAN.value in get_entity_color(compose_entity)

        # Judge is yellow
        judge_entity = Entity(id="j", entity_type=EntityType.JUDGE, x=0, y=0)
        assert Color.YELLOW.value in get_entity_color(judge_entity)

        # Contradict is red
        contradict_entity = Entity(id="x", entity_type=EntityType.CONTRADICT, x=0, y=0)
        assert Color.RED.value in get_entity_color(contradict_entity)

        # Sublate is magenta
        sublate_entity = Entity(id="s", entity_type=EntityType.SUBLATE, x=0, y=0)
        assert Color.MAGENTA.value in get_entity_color(sublate_entity)

        # Fix is blue
        fix_entity = Entity(id="f", entity_type=EntityType.FIX, x=0, y=0)
        assert Color.BLUE.value in get_entity_color(fix_entity)

    def test_phase_colors(self) -> None:
        """Test dialectic phase color mapping."""
        assert Color.DIM.value in get_phase_color(DialecticPhase.DORMANT)
        assert Color.GREEN.value in get_phase_color(DialecticPhase.FLUX)
        assert Color.RED.value in get_phase_color(DialecticPhase.TENSION)
        assert Color.MAGENTA.value in get_phase_color(DialecticPhase.SUBLATE)
        assert Color.BLUE.value in get_phase_color(DialecticPhase.FIX)
        assert Color.CYAN.value in get_phase_color(DialecticPhase.COOLING)

    def test_log_colors(self) -> None:
        """Test log level color mapping."""
        assert Color.DIM.value in get_log_color("info")
        assert Color.GREEN.value in get_log_color("success")
        assert Color.YELLOW.value in get_log_color("warning")
        assert Color.RED.value in get_log_color("error")
        assert Color.CYAN.value in get_log_color("meta")


class TestRenderConfig:
    """Tests for RenderConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = RenderConfig()
        assert config.use_color is True
        assert config.show_compost is True
        assert config.show_metrics is True
        assert config.show_help is True
        assert config.compost_lines == 5
        assert config.field_padding == 2

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = RenderConfig(
            use_color=False,
            show_compost=False,
            compost_lines=10,
        )
        assert config.use_color is False
        assert config.show_compost is False
        assert config.compost_lines == 10


class TestFieldRenderer:
    """Tests for FieldRenderer."""

    def test_renderer_creation(self) -> None:
        """Test renderer creation."""
        state = FieldState(width=60, height=20)
        renderer = FieldRenderer(state)
        assert renderer.state == state
        assert renderer.config is not None

    def test_render_returns_string(self) -> None:
        """Test render returns a string."""
        state = FieldState(width=60, height=20)
        renderer = FieldRenderer(state)
        output = renderer.render()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contains_header(self) -> None:
        """Test rendered output contains header."""
        state = FieldState(width=60, height=20)
        renderer = FieldRenderer(state, RenderConfig(use_color=False))
        output = renderer.render()

        assert "KGENTS" in output
        assert "t:" in output  # Time indicator

    def test_render_contains_metrics(self) -> None:
        """Test rendered output contains metrics."""
        state = FieldState(width=60, height=20)
        state.entropy = 75
        state.heat = 40

        config = RenderConfig(use_color=False, show_metrics=True)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "ENTROPY" in output
        assert "HEAT" in output

    def test_render_contains_entities(self) -> None:
        """Test rendered output contains entities."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="test-judge", entity_type=EntityType.JUDGE, x=30, y=10))

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        # Should contain Judge symbol
        assert "J" in output

    def test_render_contains_phase(self) -> None:
        """Test rendered output contains phase."""
        state = FieldState(width=60, height=20)
        state.dialectic_phase = DialecticPhase.TENSION

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "PHASE:" in output
        assert "TENSION" in output

    def test_render_contains_focus(self) -> None:
        """Test rendered output contains focus indicator."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="focused", entity_type=EntityType.JUDGE, x=30, y=10))
        state.focus = "focused"

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "FOCUS:" in output
        assert "focused" in output

    def test_render_contains_help(self) -> None:
        """Test rendered output contains help bar."""
        state = FieldState(width=60, height=20)

        config = RenderConfig(use_color=False, show_help=True)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "[q]QUIT" in output
        assert "[o]OBSERVE" in output

    def test_render_without_help(self) -> None:
        """Test rendered output without help bar."""
        state = FieldState(width=60, height=20)

        config = RenderConfig(use_color=False, show_help=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "[q]QUIT" not in output

    def test_render_contains_compost(self) -> None:
        """Test rendered output contains compost heap."""
        state = FieldState(width=60, height=20)
        state.log_event("test", "source", "Test event message")

        config = RenderConfig(use_color=False, show_compost=True)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "Test event message" in output

    def test_render_without_compost(self) -> None:
        """Test rendered output without compost heap."""
        state = FieldState(width=60, height=20)
        state.log_event("test", "source", "Test event message")

        config = RenderConfig(use_color=False, show_compost=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        assert "Test event message" not in output

    def test_color_application(self) -> None:
        """Test colors are applied when enabled."""
        state = FieldState(width=60, height=20)
        state.dialectic_phase = DialecticPhase.FLUX

        config = RenderConfig(use_color=True)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        # Should contain ANSI escape codes
        assert "\033[" in output

    def test_no_color_application(self) -> None:
        """Test colors are not applied when disabled."""
        state = FieldState(width=60, height=20)
        state.dialectic_phase = DialecticPhase.FLUX

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        # Should not contain ANSI color codes
        # Note: May still contain box-drawing characters
        assert "\033[3" not in output  # No color codes

    def test_focused_entity_highlighted(self) -> None:
        """Test focused entity is highlighted differently."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="focused", entity_type=EntityType.JUDGE, x=30, y=10))
        state.focus = "focused"

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)
        output = renderer.render()

        # Focused entity should have brackets
        assert "[J]" in output


class TestRenderFieldOnce:
    """Tests for render_field_once function."""

    def test_renders_state(self) -> None:
        """Test render_field_once produces output."""
        state = create_demo_field()
        output = render_field_once(state)

        assert isinstance(output, str)
        assert len(output) > 0
        assert "KGENTS" in output

    def test_respects_config(self) -> None:
        """Test render_field_once respects configuration."""
        state = create_demo_field()
        config = RenderConfig(use_color=False, show_help=False)
        output = render_field_once(state, config)

        assert "[q]QUIT" not in output


class TestKeyHandler:
    """Tests for KeyHandler."""

    def test_register_handler(self) -> None:
        """Test registering a handler."""
        handler = KeyHandler()
        called = []

        handler.register("x", lambda: called.append("x"))
        handler.handle("x")

        assert called == ["x"]

    def test_unregistered_key(self) -> None:
        """Test handling unregistered key."""
        handler = KeyHandler()

        result = handler.handle("y")
        assert result is False

    def test_registered_key_returns_true(self) -> None:
        """Test registered key returns True."""
        handler = KeyHandler()
        handler.register("z", lambda: None)

        result = handler.handle("z")
        assert result is True

    def test_multiple_handlers(self) -> None:
        """Test multiple handlers."""
        handler = KeyHandler()
        called = []

        handler.register("a", lambda: called.append("a"))
        handler.register("b", lambda: called.append("b"))

        handler.handle("a")
        handler.handle("b")
        handler.handle("a")

        assert called == ["a", "b", "a"]


class TestRendererEdgeCases:
    """Tests for renderer edge cases."""

    def test_empty_field(self) -> None:
        """Test rendering empty field."""
        state = FieldState(width=60, height=20)
        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        assert isinstance(output, str)
        assert "DORMANT" in output  # Default phase

    def test_small_field(self) -> None:
        """Test rendering small field."""
        state = FieldState(width=20, height=5)
        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        assert isinstance(output, str)

    def test_large_field(self) -> None:
        """Test rendering large field."""
        state = FieldState(width=200, height=50)
        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        assert isinstance(output, str)

    def test_many_entities(self) -> None:
        """Test rendering many entities."""
        state = FieldState(width=60, height=20)

        # Add 50 entities
        for i in range(50):
            state.add_entity(
                Entity(
                    id=f"entity-{i}",
                    entity_type=EntityType.JUDGE,
                    x=i % 60,
                    y=i % 20,
                )
            )

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        assert isinstance(output, str)

    def test_entity_at_boundary(self) -> None:
        """Test entity at field boundary."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="corner", entity_type=EntityType.JUDGE, x=59, y=19))

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        assert "J" in output

    def test_overlapping_entities(self) -> None:
        """Test overlapping entities."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="e1", entity_type=EntityType.JUDGE, x=30, y=10))
        state.add_entity(Entity(id="e2", entity_type=EntityType.COMPOSE, x=30, y=10))

        config = RenderConfig(use_color=False)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        # One should be visible (last added wins)
        assert isinstance(output, str)

    def test_long_event_message(self) -> None:
        """Test truncation of long event messages."""
        state = FieldState(width=40, height=10)
        long_message = "A" * 100

        state.log_event("test", "source", long_message)

        config = RenderConfig(use_color=False, show_compost=True)
        renderer = FieldRenderer(state, config)

        output = renderer.render()
        # Should contain truncated message with ellipsis
        assert "..." in output
