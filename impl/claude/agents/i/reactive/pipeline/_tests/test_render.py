"""Tests for RenderPipeline."""

import pytest

from agents.i.reactive.pipeline.render import (
    RenderNode,
    RenderPipeline,
    RenderPriority,
    RenderState,
    create_render_pipeline,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.clock import ClockConfig, create_clock


class MockWidget:
    """Mock widget for testing."""

    def __init__(self, content: str = "default"):
        self.content = content
        self.render_count = 0

    def render(self) -> str:
        self.render_count += 1
        return self.content


class TestRenderNode:
    """Tests for RenderNode."""

    def test_create_node(self) -> None:
        """RenderNode can be created with widget."""
        widget = MockWidget("test")
        node = RenderNode(id="test-1", widget=widget)

        assert node.id == "test-1"
        assert node.widget == widget
        assert node.priority == RenderPriority.NORMAL
        assert node.dirty is True

    def test_render_calls_widget(self) -> None:
        """RenderNode.render() calls widget.render()."""
        widget = MockWidget("hello")
        node = RenderNode(id="test", widget=widget)

        output = node.render()

        assert output == "hello"
        assert widget.render_count == 1
        assert node.dirty is False
        assert node.last_output == "hello"

    def test_render_with_custom_fn(self) -> None:
        """RenderNode can use custom render function."""
        widget = {"value": 42}

        def custom_render(w: dict[str, int]) -> str:
            return f"value={w['value']}"

        node: RenderNode[dict[str, int]] = RenderNode(
            id="test", widget=widget, _render_fn=custom_render
        )

        output = node.render()

        assert output == "value=42"

    def test_invalidate_marks_dirty(self) -> None:
        """RenderNode.invalidate() marks node as dirty."""
        widget = MockWidget()
        node = RenderNode(id="test", widget=widget)

        node.render()  # Clear dirty
        assert node.dirty is False

        node.invalidate()
        assert node.dirty is True

    def test_priority_levels(self) -> None:
        """RenderPriority levels order correctly."""
        assert RenderPriority.CRITICAL < RenderPriority.HIGH
        assert RenderPriority.HIGH < RenderPriority.NORMAL
        assert RenderPriority.NORMAL < RenderPriority.LOW
        assert RenderPriority.LOW < RenderPriority.IDLE


class TestRenderPipeline:
    """Tests for RenderPipeline."""

    def test_create_pipeline(self) -> None:
        """RenderPipeline can be created."""
        pipeline = create_render_pipeline()

        assert pipeline.node_count == 0
        assert pipeline.state.value.running is True

    def test_register_widget(self) -> None:
        """Can register widgets in pipeline."""
        pipeline = create_render_pipeline()
        widget = MockWidget("content")

        node = pipeline.register("widget-1", widget)

        assert node.id == "widget-1"
        assert pipeline.node_count == 1
        assert pipeline.state.value.total_nodes == 1

    def test_unregister_widget(self) -> None:
        """Can unregister widgets from pipeline."""
        pipeline = create_render_pipeline()
        widget = MockWidget("content")

        pipeline.register("widget-1", widget)
        assert pipeline.node_count == 1

        result = pipeline.unregister("widget-1")

        assert result is True
        assert pipeline.node_count == 0

    def test_process_frame_renders_dirty(self) -> None:
        """process_frame renders dirty nodes."""
        pipeline = create_render_pipeline()
        widget1 = MockWidget("one")
        widget2 = MockWidget("two")

        pipeline.register("w1", widget1)
        pipeline.register("w2", widget2)

        outputs = pipeline.process_frame()

        assert outputs["w1"] == "one"
        assert outputs["w2"] == "two"
        assert widget1.render_count == 1
        assert widget2.render_count == 1

    def test_process_frame_skips_clean(self) -> None:
        """process_frame skips clean nodes."""
        pipeline = create_render_pipeline()
        widget = MockWidget("content")

        pipeline.register("w1", widget)
        pipeline.process_frame()  # First render

        assert widget.render_count == 1

        # Second frame - should skip (not dirty)
        outputs = pipeline.process_frame()

        # Node is clean, so it won't be re-rendered
        assert widget.render_count == 1

    def test_invalidate_triggers_rerender(self) -> None:
        """Invalidating a node causes re-render."""
        pipeline = create_render_pipeline()
        widget = MockWidget("v1")

        pipeline.register("w1", widget)
        pipeline.process_frame()
        assert widget.render_count == 1

        widget.content = "v2"
        pipeline.invalidate("w1")
        outputs = pipeline.process_frame()

        assert outputs["w1"] == "v2"
        assert widget.render_count == 2

    def test_priority_order(self) -> None:
        """Higher priority nodes render first."""
        pipeline = create_render_pipeline()
        render_order: list[str] = []

        def make_widget(name: str) -> MockWidget:
            class OrderWidget(MockWidget):
                def render(self) -> str:
                    render_order.append(name)
                    return name

            return OrderWidget(name)

        pipeline.register("low", make_widget("low"), RenderPriority.LOW)
        pipeline.register("high", make_widget("high"), RenderPriority.HIGH)
        pipeline.register("normal", make_widget("normal"), RenderPriority.NORMAL)

        pipeline.process_frame()

        # HIGH < NORMAL < LOW
        assert render_order == ["high", "normal", "low"]

    def test_connect_signal(self) -> None:
        """Signal changes invalidate connected nodes."""
        pipeline = create_render_pipeline()
        widget = MockWidget("initial")
        signal: Signal[int] = Signal.of(0)

        pipeline.register("w1", widget)
        pipeline.connect_signal(signal, ["w1"])
        pipeline.process_frame()  # Initial render

        assert widget.render_count == 1

        # Change signal
        signal.set(1)

        # Node should be dirty
        assert pipeline.dirty_count == 1

    def test_pause_resume(self) -> None:
        """Pipeline can be paused and resumed."""
        pipeline = create_render_pipeline()

        pipeline.pause()
        assert pipeline.state.value.running is False

        pipeline.resume()
        assert pipeline.state.value.running is True

    def test_parent_child_relationship(self) -> None:
        """Parent-child nodes work correctly."""
        pipeline = create_render_pipeline()
        parent_widget = MockWidget("parent")
        child_widget = MockWidget("child")

        pipeline.register("parent", parent_widget)
        pipeline.register("child", child_widget, parent="parent")

        parent_node = pipeline.get_node("parent")
        child_node = pipeline.get_node("child")

        assert parent_node is not None
        assert child_node is not None
        assert "child" in parent_node._children
        assert child_node._parent == "parent"

    def test_cascade_invalidation(self) -> None:
        """Invalidating parent cascades to children."""
        pipeline = create_render_pipeline()
        parent_widget = MockWidget("parent")
        child_widget = MockWidget("child")

        pipeline.register("parent", parent_widget)
        pipeline.register("child", child_widget, parent="parent")
        pipeline.process_frame()  # Clear dirty

        pipeline.invalidate("parent", cascade=True)

        parent_node = pipeline.get_node("parent")
        child_node = pipeline.get_node("child")

        assert parent_node is not None
        assert child_node is not None
        assert parent_node.dirty is True
        assert child_node.dirty is True

    def test_render_stats(self) -> None:
        """Pipeline tracks render statistics."""
        pipeline = create_render_pipeline()
        pipeline.register("w1", MockWidget("a"))
        pipeline.register("w2", MockWidget("b"))

        pipeline.process_frame()

        state = pipeline.state.value
        assert state.frame_count == 1
        assert state.nodes_rendered == 2
        assert state.total_nodes == 2

    def test_connect_clock(self) -> None:
        """Pipeline can connect to Clock for automatic updates."""
        clock = create_clock(use_wall_time=False)
        pipeline = create_render_pipeline()
        widget = MockWidget("test")

        pipeline.register("w1", widget)
        pipeline.connect_clock(clock)

        # Tick the clock
        clock.tick(override_delta=16.67)

        # Widget should have been rendered
        assert widget.render_count == 1


class TestRenderState:
    """Tests for RenderState."""

    def test_default_state(self) -> None:
        """RenderState has correct defaults."""
        state = RenderState()

        assert state.frame_count == 0
        assert state.nodes_rendered == 0
        assert state.nodes_skipped == 0
        assert state.running is True

    def test_immutable(self) -> None:
        """RenderState is immutable."""
        state = RenderState()

        with pytest.raises(Exception):  # FrozenInstanceError
            state.frame_count = 1  # type: ignore[misc]
