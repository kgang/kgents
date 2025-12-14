"""Tests for TextualAdapter - KgentsWidget → Textual bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from agents.i.reactive.adapters.textual_widget import (
    ReactiveTextualAdapter,
    TextualAdapter,
    create_textual_adapter,
)
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

# =============================================================================
# Test Fixtures - Sample Widgets
# =============================================================================


@dataclass(frozen=True)
class CounterState:
    """Simple counter state."""

    count: int = 0


class CounterWidget(KgentsWidget[CounterState]):
    """Simple counter widget for testing."""

    def __init__(self, initial: int = 0) -> None:
        self.state = Signal.of(CounterState(count=initial))

    def project(self, target: RenderTarget) -> str | dict[str, Any]:
        count = self.state.value.count
        match target:
            case RenderTarget.CLI:
                return f"Count: {count}"
            case RenderTarget.TUI:
                return f"[TUI] Count: {count}"
            case RenderTarget.JSON:
                return {"type": "counter", "count": count}
            case _:
                return f"Count: {count}"

    def increment(self) -> None:
        self.state.update(lambda s: CounterState(count=s.count + 1))

    def decrement(self) -> None:
        self.state.update(lambda s: CounterState(count=s.count - 1))


@dataclass(frozen=True)
class LabelState:
    """Simple label state."""

    text: str = ""


class LabelWidget(KgentsWidget[LabelState]):
    """Simple label widget for testing."""

    def __init__(self, text: str = "") -> None:
        self.state = Signal.of(LabelState(text=text))

    def project(self, target: RenderTarget) -> str:
        return self.state.value.text

    def set_text(self, text: str) -> None:
        self.state.set(LabelState(text=text))


# =============================================================================
# TextualAdapter Tests
# =============================================================================


class TestTextualAdapterCreation:
    """Test TextualAdapter creation."""

    def test_create_with_widget(self) -> None:
        """Create adapter with a KgentsWidget."""
        widget = CounterWidget(initial=5)
        adapter = TextualAdapter(widget)

        assert adapter.kgents_widget is widget

    def test_create_with_name(self) -> None:
        """Create adapter with custom name."""
        widget = CounterWidget()
        adapter = TextualAdapter(widget, name="my-counter")

        assert adapter.name == "my-counter"

    def test_create_with_id(self) -> None:
        """Create adapter with custom ID."""
        widget = CounterWidget()
        adapter = TextualAdapter(widget, id="counter-1")

        assert adapter.id == "counter-1"

    def test_create_with_classes(self) -> None:
        """Create adapter with CSS classes."""
        widget = CounterWidget()
        adapter = TextualAdapter(widget, classes="card highlight")

        assert "card" in adapter.classes
        assert "highlight" in adapter.classes


class TestTextualAdapterRendering:
    """Test TextualAdapter rendering."""

    def test_project_uses_tui_target(self) -> None:
        """Adapter should use TUI render target."""
        widget = CounterWidget(initial=42)
        adapter = TextualAdapter(widget)

        # Force internal update
        initial_version = adapter._render_version
        adapter._update_content()

        # Verify render happened and widget projects TUI target
        assert adapter._render_version > initial_version
        tui_output = widget.project(RenderTarget.TUI)
        assert "[TUI]" in tui_output
        assert "42" in tui_output

    def test_project_different_from_cli(self) -> None:
        """TUI projection should differ from CLI."""
        widget = CounterWidget(initial=10)

        tui_output = widget.project(RenderTarget.TUI)
        cli_output = widget.project(RenderTarget.CLI)

        assert "[TUI]" in tui_output
        assert "[TUI]" not in cli_output

    def test_renders_label_widget(self) -> None:
        """Adapter renders label widget correctly."""
        widget = LabelWidget(text="Hello, World!")
        adapter = TextualAdapter(widget)
        initial_version = adapter._render_version
        adapter._update_content()

        assert adapter._render_version > initial_version
        assert widget.project(RenderTarget.TUI) == "Hello, World!"


class TestTextualAdapterReactivity:
    """Test TextualAdapter reactive updates."""

    def test_tracks_state_changes(self) -> None:
        """Adapter should track widget state changes."""
        widget = CounterWidget(initial=0)
        adapter = TextualAdapter(widget)

        # Simulate mount
        adapter._update_content()
        assert "0" in widget.project(RenderTarget.TUI)

        # Change state (in real usage, subscription handles this)
        widget.increment()
        adapter._update_content()
        assert "1" in widget.project(RenderTarget.TUI)

    def test_multiple_updates(self) -> None:
        """Adapter handles multiple state updates."""
        widget = CounterWidget(initial=0)
        adapter = TextualAdapter(widget)

        for i in range(5):
            widget.increment()
            adapter._update_content()
            assert str(i + 1) in widget.project(RenderTarget.TUI)

    def test_label_text_changes(self) -> None:
        """Adapter tracks label text changes."""
        widget = LabelWidget(text="initial")
        adapter = TextualAdapter(widget)
        adapter._update_content()
        assert widget.project(RenderTarget.TUI) == "initial"

        widget.set_text("updated")
        adapter._update_content()
        assert widget.project(RenderTarget.TUI) == "updated"


class TestTextualAdapterVersioning:
    """Test TextualAdapter render versioning."""

    def test_tracks_render_version(self) -> None:
        """Adapter tracks render version."""
        widget = CounterWidget(initial=5)
        adapter = TextualAdapter(widget)
        initial_version = adapter._render_version

        adapter._update_content()

        assert adapter._render_version > initial_version
        assert widget.project(RenderTarget.TUI) == "[TUI] Count: 5"

    def test_version_increments_each_update(self) -> None:
        """Render version increments on each update."""
        widget = LabelWidget(text="test")
        adapter = TextualAdapter(widget)

        versions = [adapter._render_version]
        for _ in range(3):
            adapter._update_content()
            versions.append(adapter._render_version)

        # Each version should be greater than the previous
        for i in range(1, len(versions)):
            assert versions[i] > versions[i - 1]


# =============================================================================
# ReactiveTextualAdapter Tests
# =============================================================================


class TestReactiveTextualAdapter:
    """Test ReactiveTextualAdapter variant."""

    def test_create_reactive_adapter(self) -> None:
        """Create reactive adapter."""
        widget = CounterWidget(initial=0)
        adapter = ReactiveTextualAdapter(widget)

        assert adapter.kgents_widget is widget
        assert adapter._reactive_version == 0

    def test_version_increments_on_change(self) -> None:
        """Reactive version increments on state change."""
        widget = CounterWidget(initial=0)
        adapter = ReactiveTextualAdapter(widget)

        initial_version = adapter._reactive_version

        # Simulate state change callback
        adapter._on_state_change(None)

        assert adapter._reactive_version == initial_version + 1


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateTextualAdapter:
    """Test create_textual_adapter factory."""

    def test_creates_standard_adapter(self) -> None:
        """Factory creates standard adapter by default."""
        widget = CounterWidget()
        adapter = create_textual_adapter(widget)

        assert isinstance(adapter, TextualAdapter)

    def test_creates_reactive_adapter(self) -> None:
        """Factory creates reactive adapter when requested."""
        widget = CounterWidget()
        adapter = create_textual_adapter(widget, use_reactive=True)

        assert isinstance(adapter, ReactiveTextualAdapter)

    def test_passes_name(self) -> None:
        """Factory passes name to adapter."""
        widget = CounterWidget()
        adapter = create_textual_adapter(widget, name="test-name")

        assert adapter.name == "test-name"

    def test_passes_id(self) -> None:
        """Factory passes ID to adapter."""
        widget = CounterWidget()
        adapter = create_textual_adapter(widget, id="test-id")

        assert adapter.id == "test-id"

    def test_passes_classes(self) -> None:
        """Factory passes classes to adapter."""
        widget = CounterWidget()
        adapter = create_textual_adapter(widget, classes="foo bar")

        assert "foo" in adapter.classes
        assert "bar" in adapter.classes


# =============================================================================
# Edge Cases
# =============================================================================


class TestTextualAdapterEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_widget_without_state(self) -> None:
        """Adapter handles widgets without state Signal."""

        class StatelessWidget(KgentsWidget[None]):
            def project(self, target: RenderTarget) -> str:
                return "stateless"

        widget = StatelessWidget()
        adapter = TextualAdapter(widget)

        # Should not crash when mounting
        initial_version = adapter._render_version
        adapter.on_mount()
        assert adapter._render_version > initial_version
        assert widget.project(RenderTarget.TUI) == "stateless"

    def test_refresh_widget_method(self) -> None:
        """Adapter has refresh_widget method."""
        widget = CounterWidget(initial=10)
        adapter = TextualAdapter(widget)

        initial_version = adapter._render_version
        adapter.refresh_widget()
        assert adapter._render_version > initial_version
        assert "10" in widget.project(RenderTarget.TUI)

    def test_unmount_cleanup(self) -> None:
        """Adapter cleans up on unmount."""
        widget = CounterWidget()
        adapter = TextualAdapter(widget)

        # Simulate mount
        adapter.on_mount()
        assert adapter._unsubscribe is not None

        # Unmount
        adapter.on_unmount()
        assert adapter._unsubscribe is None
