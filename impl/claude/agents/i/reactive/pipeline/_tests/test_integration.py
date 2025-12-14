"""Integration tests for Widget Integration Pipeline (Wave 9)."""

import pytest
from agents.i.reactive.pipeline.focus import (
    AnimatedFocus,
    FocusTransitionStyle,
    create_animated_focus,
)
from agents.i.reactive.pipeline.layout import (
    Constraints,
    FlexAlign,
    FlexDirection,
    FlexLayout,
    GridLayout,
    LayoutNode,
)
from agents.i.reactive.pipeline.render import (
    RenderNode,
    RenderPipeline,
    RenderPriority,
    create_render_pipeline,
)
from agents.i.reactive.pipeline.theme import (
    Theme,
    ThemeMode,
    ThemeProvider,
    create_dark_theme,
    create_theme_provider,
    styled_text,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.clock import create_clock
from agents.i.reactive.wiring.interactions import FocusDirection


class SimpleWidget:
    """Simple widget for testing integration."""

    def __init__(self, name: str, content: str = ""):
        self.name = name
        self.content = content
        self.focused = False
        self.theme: Theme | None = None

    def render(self) -> str:
        if self.theme:
            if self.focused:
                fg = self.theme.primary
                return styled_text(f"[*] {self.content}", fg=fg, bold=True)
            else:
                fg = self.theme.text
                return styled_text(f"[ ] {self.content}", fg=fg)
        else:
            prefix = "[*]" if self.focused else "[ ]"
            return f"{prefix} {self.content}"


class TestRenderPipelineWithLayout:
    """Test RenderPipeline with layout system."""

    def test_render_with_layout_positions(self) -> None:
        """RenderPipeline can render widgets at layout positions."""
        # Create layout
        flex = FlexLayout(direction=FlexDirection.ROW, gap=2)
        flex.add_child(LayoutNode("item-1", Constraints.fixed(10, 1)))
        flex.add_child(LayoutNode("item-2", Constraints.fixed(10, 1)))
        flex.add_child(LayoutNode("item-3", Constraints.fixed(10, 1)))
        flex.compute(available_width=40, available_height=10)

        # Create pipeline
        pipeline = create_render_pipeline()

        # Register widgets at layout positions
        for node in flex.children:
            widget = SimpleWidget(node.id, f"Widget {node.id}")
            pipeline.register(
                node.id,
                widget,
                render_fn=lambda w: w.render(),
            )

        # Process frame
        outputs = pipeline.process_frame()

        assert len(outputs) == 3
        assert "Widget item-1" in outputs["item-1"]

    def test_layout_with_grid(self) -> None:
        """RenderPipeline works with grid layout."""
        grid = GridLayout(columns=2, column_gap=2, row_gap=1)

        for i in range(4):
            grid.add_child(LayoutNode(f"cell-{i}", Constraints.fill_both()))

        grid.compute(available_width=42, available_height=10)

        pipeline = create_render_pipeline()

        for node in grid.children:
            widget = SimpleWidget(node.id, f"Cell {node.id}")
            pipeline.register(node.id, widget)

        outputs = pipeline.process_frame()

        assert len(outputs) == 4
        # Check grid positions
        assert grid.children[0].rect.x == 0
        assert grid.children[1].rect.x == 22  # 20 + 2 gap


class TestRenderPipelineWithFocus:
    """Test RenderPipeline with animated focus."""

    def test_focus_invalidates_widgets(self) -> None:
        """Focus changes invalidate affected widgets."""
        pipeline = create_render_pipeline()
        focus = create_animated_focus(transition_style=FocusTransitionStyle.NONE)

        widgets = {}
        for i in range(3):
            widget = SimpleWidget(f"w-{i}", f"Widget {i}")
            widgets[f"w-{i}"] = widget
            pipeline.register(f"w-{i}", widget)
            focus.register(f"w-{i}", tab_index=i)

        # Connect focus signal to invalidate
        def on_focus_change(old_id: str | None, new_id: str | None) -> None:
            if old_id:
                widgets[old_id].focused = False
                pipeline.invalidate(old_id)
            if new_id:
                widgets[new_id].focused = True
                pipeline.invalidate(new_id)

        focus._on_focus_change = on_focus_change

        # Initial render
        pipeline.process_frame()

        # Focus first widget
        focus.focus("w-0")
        outputs = pipeline.process_frame()

        assert "[*]" in outputs["w-0"]

        # Move focus
        focus.move(FocusDirection.FORWARD)
        outputs = pipeline.process_frame()

        assert "[ ]" in outputs["w-0"]
        assert "[*]" in outputs["w-1"]

    def test_focus_with_spring_animation(self) -> None:
        """Focus transitions animate with springs."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)

        focus.register("a", tab_index=0, position=(0, 0))
        focus.register("b", tab_index=1, position=(50, 0))

        focus.focus("a")
        focus.focus("b")

        # Animation should be in progress
        assert focus.is_transitioning is True

        # Run animation
        positions: list[float] = []
        for _ in range(50):
            focus.update(16.67)
            positions.append(focus.visual_state.ring_x)
            if not focus.is_transitioning:
                break

        # Position should have moved toward target
        assert positions[-1] > positions[0]
        assert focus.is_transitioning is False


class TestRenderPipelineWithTheme:
    """Test RenderPipeline with theme system."""

    def test_theme_affects_rendering(self) -> None:
        """Theme changes affect widget rendering."""
        pipeline = create_render_pipeline()
        provider = create_theme_provider(mode=ThemeMode.DARK)

        widget = SimpleWidget("themed", "Themed Widget")
        widget.theme = provider.theme

        pipeline.register("themed", widget)

        # Render in dark mode
        outputs = pipeline.process_frame()
        assert "Themed Widget" in outputs["themed"]

        # Switch to light mode
        provider.toggle_mode()
        widget.theme = provider.theme
        pipeline.invalidate("themed")

        outputs = pipeline.process_frame()
        assert "Themed Widget" in outputs["themed"]

    def test_theme_provider_signal(self) -> None:
        """Theme provider signal can invalidate widgets."""
        pipeline = create_render_pipeline()
        provider = create_theme_provider(mode=ThemeMode.DARK)

        widget = SimpleWidget("reactive", "Reactive Widget")
        widget.theme = provider.theme

        node = pipeline.register("reactive", widget)

        # Connect theme changes to invalidation
        def on_theme_change(theme: Theme) -> None:
            widget.theme = theme
            pipeline.invalidate("reactive")

        provider.subscribe(on_theme_change)

        # Change theme
        provider.toggle_mode()

        # Widget should be invalidated
        assert node.dirty is True


class TestFullIntegration:
    """Full integration tests combining all Wave 9 features."""

    def test_dashboard_simulation(self) -> None:
        """Simulate a dashboard with layout, focus, and theme."""
        # Clock for timing
        clock = create_clock(use_wall_time=False)

        # Theme
        provider = create_theme_provider(mode=ThemeMode.DARK)

        # Layout
        layout = FlexLayout(direction=FlexDirection.COLUMN, gap=1)
        layout.add_child(LayoutNode("header", Constraints.fill_width(height=1)))
        layout.add_child(LayoutNode("content", Constraints.fill_both()))
        layout.add_child(LayoutNode("footer", Constraints.fill_width(height=1)))
        layout.compute(available_width=80, available_height=24)

        # Pipeline
        pipeline = create_render_pipeline()
        pipeline.connect_clock(clock)

        # Focus
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)

        # Widgets
        widgets: dict[str, SimpleWidget] = {}
        for node in layout.children:
            widget = SimpleWidget(node.id, f"Section: {node.id}")
            widget.theme = provider.theme
            widgets[node.id] = widget
            pipeline.register(node.id, widget)
            focus.register(
                node.id,
                tab_index=layout.children.index(node),
                position=(node.rect.x, node.rect.y),
            )

        # Theme change handler
        def on_theme_change(theme: Theme) -> None:
            for w in widgets.values():
                w.theme = theme
            pipeline.invalidate_all()

        provider.subscribe(on_theme_change)

        # Focus change handler
        def on_focus_change(old_id: str | None, new_id: str | None) -> None:
            if old_id and old_id in widgets:
                widgets[old_id].focused = False
                pipeline.invalidate(old_id)
            if new_id and new_id in widgets:
                widgets[new_id].focused = True
                pipeline.invalidate(new_id)

        focus._on_focus_change = on_focus_change

        # Simulate several frames
        focus.focus("header")
        clock.tick(override_delta=16.67)

        state = pipeline.state.value
        assert state.frame_count > 0

        # Move focus
        focus.move(FocusDirection.FORWARD)
        clock.tick(override_delta=16.67)

        assert focus.focused_id == "content"

        # Toggle theme
        provider.toggle_mode()
        clock.tick(override_delta=16.67)

        # All widgets should have been re-rendered
        assert all(
            not node.dirty for node in [pipeline.get_node(n) for n in widgets] if node
        )

    def test_animated_focus_with_clock(self) -> None:
        """AnimatedFocus integrates with Clock for automatic updates."""
        clock = create_clock(use_wall_time=False)
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)
        focus.connect_clock(clock)

        focus.register("a", tab_index=0, position=(0, 0))
        focus.register("b", tab_index=1, position=(100, 0))

        focus.focus("a")
        focus.focus("b")

        initial_x = focus.visual_state.ring_x

        # Tick clock to advance animation
        for _ in range(20):
            clock.tick(override_delta=16.67)

        # Animation should have progressed
        assert focus.visual_state.ring_x != initial_x

    def test_signal_driven_updates(self) -> None:
        """Signal changes drive widget updates through pipeline."""
        pipeline = create_render_pipeline()
        count: Signal[int] = Signal.of(0)

        class CounterWidget:
            def __init__(self, signal: Signal[int]):
                self._signal = signal

            def render(self) -> str:
                return f"Count: {self._signal.value}"

        widget = CounterWidget(count)
        pipeline.register("counter", widget)
        pipeline.connect_signal(count, ["counter"])

        # Initial render
        outputs = pipeline.process_frame()
        assert outputs["counter"] == "Count: 0"

        # Update signal
        count.set(42)
        outputs = pipeline.process_frame()

        assert outputs["counter"] == "Count: 42"

    def test_priority_rendering_with_focus(self) -> None:
        """Focused widgets render with higher priority."""
        pipeline = create_render_pipeline()

        render_order: list[str] = []

        class OrderTrackingWidget:
            def __init__(self, name: str):
                self.name = name

            def render(self) -> str:
                render_order.append(self.name)
                return self.name

        # Register with different priorities
        pipeline.register(
            "background",
            OrderTrackingWidget("background"),
            RenderPriority.LOW,
        )
        pipeline.register(
            "focused",
            OrderTrackingWidget("focused"),
            RenderPriority.HIGH,  # Focused items get high priority
        )
        pipeline.register(
            "normal",
            OrderTrackingWidget("normal"),
            RenderPriority.NORMAL,
        )

        pipeline.process_frame()

        # High priority should render first
        assert render_order[0] == "focused"
        assert render_order[1] == "normal"
        assert render_order[2] == "background"


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_pipeline(self) -> None:
        """Empty pipeline processes without error."""
        pipeline = create_render_pipeline()
        outputs = pipeline.process_frame()

        assert outputs == {}
        assert pipeline.state.value.frame_count == 1

    def test_empty_layout(self) -> None:
        """Empty layouts compute without error."""
        flex = FlexLayout(direction=FlexDirection.ROW)
        rect = flex.compute(available_width=80, available_height=24)

        assert rect.width == 80
        assert rect.height == 24

    def test_focus_with_no_elements(self) -> None:
        """Focus manager handles no registered elements."""
        focus = create_animated_focus()

        result = focus.move(FocusDirection.FORWARD)

        assert result is None
        assert focus.focused_id is None

    def test_rapid_focus_changes(self) -> None:
        """Rapid focus changes don't break animation."""
        focus = create_animated_focus(transition_style=FocusTransitionStyle.SPRING)

        for i in range(10):
            focus.register(f"elem-{i}", tab_index=i, position=(i * 10, 0))

        # Rapidly change focus
        for i in range(10):
            focus.focus(f"elem-{i}")
            focus.update(1.0)  # Very short update

        # Should end on last focused element
        assert focus.focused_id == "elem-9"

    def test_theme_system_mode(self) -> None:
        """SYSTEM mode uses default."""
        provider = create_theme_provider(mode=ThemeMode.DARK)
        provider.set_system_mode(ThemeMode.LIGHT)
        provider.set_mode(ThemeMode.SYSTEM)

        # Should follow system mode (which we set to LIGHT)
        assert provider.mode == ThemeMode.LIGHT
