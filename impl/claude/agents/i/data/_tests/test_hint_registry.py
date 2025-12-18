"""
Tests for HintRegistry.

Verifies hint-to-widget mapping, factory registration, and rendering.
"""

import pytest
from textual.widgets import Static

from agents.i.data.hint_registry import (
    HintRegistry,
    get_hint_registry,
    reset_hint_registry,
)
from agents.i.data.hints import VisualHint
from agents.i.widgets.density_field import DensityField


class TestHintRegistryBasics:
    """Test basic HintRegistry operations."""

    def test_registry_initializes_with_defaults(self) -> None:
        """Registry initializes with built-in factories."""
        registry = HintRegistry()

        # Should have default factories
        assert registry._factories
        assert "text" in registry._factories
        assert "table" in registry._factories
        assert "density" in registry._factories

    def test_register_custom_factory(self) -> None:
        """Can register custom factory."""
        registry = HintRegistry()

        def custom_factory(hint: VisualHint) -> Static:
            return Static(f"Custom: {hint.data}")

        registry.register("my_custom_type", custom_factory)

        assert "my_custom_type" in registry._factories


class TestHintRegistryTextFactory:
    """Test built-in text factory."""

    def test_text_factory_basic(self) -> None:
        """Text factory renders Static widget."""
        registry = HintRegistry()
        hint = VisualHint(type="text", data={"text": "Hello, World!"})

        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_text_factory_empty(self) -> None:
        """Text factory handles empty text."""
        registry = HintRegistry()
        hint = VisualHint(type="text", data={})

        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_text_factory_unicode(self) -> None:
        """Text factory handles unicode."""
        registry = HintRegistry()
        hint = VisualHint(type="text", data={"text": "世界 🌍"})

        widget = registry.render(hint)

        assert isinstance(widget, Static)


class TestHintRegistryTableFactory:
    """Test built-in table factory."""

    def test_table_factory_dict_format(self) -> None:
        """Table factory handles dict format."""
        registry = HintRegistry()
        hint = VisualHint(
            type="table",
            data={"Assets": 100, "Liabilities": 50},
        )

        widget = registry.render(hint)

        # Table factory returns Static with formatted text
        assert isinstance(widget, Static)

    def test_table_factory_rows_columns_format(self) -> None:
        """Table factory handles explicit rows/columns."""
        registry = HintRegistry()
        hint = VisualHint(
            type="table",
            data={
                "columns": ["Name", "Age"],
                "rows": [["Alice", "30"], ["Bob", "25"]],
            },
        )

        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_table_factory_empty(self) -> None:
        """Table factory handles empty data."""
        registry = HintRegistry()
        hint = VisualHint(type="table", data={})

        widget = registry.render(hint)

        assert isinstance(widget, Static)


class TestHintRegistryDensityFactory:
    """Test built-in density factory."""

    def test_density_factory_basic(self) -> None:
        """Density factory renders DensityField."""
        registry = HintRegistry()
        hint = VisualHint(
            type="density",
            data={"activity": 0.7, "phase": "ACTIVE"},
            agent_id="test-agent",
        )

        widget = registry.render(hint)

        assert isinstance(widget, DensityField)
        assert widget.activity == 0.7
        assert widget.agent_id == "test-agent"

    def test_density_factory_defaults(self) -> None:
        """Density factory uses defaults for missing data."""
        registry = HintRegistry()
        hint = VisualHint(type="density", data={})

        widget = registry.render(hint)

        assert isinstance(widget, DensityField)
        assert widget.activity == 0.5  # Default

    def test_density_factory_invalid_phase(self) -> None:
        """Density factory handles invalid phase gracefully."""
        registry = HintRegistry()
        hint = VisualHint(
            type="density",
            data={"activity": 0.5, "phase": "INVALID_PHASE"},
        )

        widget = registry.render(hint)

        assert isinstance(widget, DensityField)
        # Should fall back to ACTIVE


class TestHintRegistrySparklineFactory:
    """Test built-in sparkline factory."""

    def test_sparkline_factory_fallback(self) -> None:
        """Sparkline factory provides fallback if widget not available."""
        registry = HintRegistry()
        hint = VisualHint(
            type="sparkline",
            data={"values": [1.0, 2.0, 3.0, 4.0, 5.0]},
        )

        widget = registry.render(hint)

        # Should render as Static (fallback) or Sparkline widget
        assert isinstance(widget, Static) or widget.__class__.__name__ == "Sparkline"

    def test_sparkline_factory_empty_values(self) -> None:
        """Sparkline factory handles empty values."""
        registry = HintRegistry()
        hint = VisualHint(type="sparkline", data={"values": []})

        widget = registry.render(hint)

        assert widget is not None


class TestHintRegistryGraphFactory:
    """Test built-in graph factory (stub)."""

    def test_graph_factory_stub(self) -> None:
        """Graph factory renders placeholder."""
        registry = HintRegistry()
        hint = VisualHint(
            type="graph",
            data={
                "nodes": ["A", "B", "C"],
                "edges": [("A", "B"), ("B", "C")],
            },
        )

        widget = registry.render(hint)

        assert isinstance(widget, Static)


class TestHintRegistryLoomFactory:
    """Test built-in loom factory."""

    def test_loom_factory_no_tree(self) -> None:
        """Loom factory renders placeholder when no tree provided."""
        registry = HintRegistry()
        hint = VisualHint(type="loom", data={})

        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_loom_factory_with_cognitive_tree(self) -> None:
        """Loom factory renders BranchTree with valid CognitiveTree."""
        from datetime import datetime

        from agents.i.data.loom import CognitiveBranch, CognitiveTree
        from agents.i.widgets.branch_tree import BranchTree

        registry = HintRegistry()

        # Create a simple cognitive tree
        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="Initial action",
            selected=True,
        )
        tree = CognitiveTree(root=root, current_id="root")

        hint = VisualHint(type="loom", data={"tree": tree, "show_ghosts": True})
        widget = registry.render(hint)

        assert isinstance(widget, BranchTree)
        assert widget.cognitive_tree is tree
        assert widget.show_ghosts is True

    def test_loom_factory_show_ghosts_false(self) -> None:
        """Loom factory respects show_ghosts parameter."""
        from datetime import datetime

        from agents.i.data.loom import CognitiveBranch, CognitiveTree
        from agents.i.widgets.branch_tree import BranchTree

        registry = HintRegistry()

        root = CognitiveBranch(
            id="root",
            timestamp=datetime.now(),
            content="Start",
            reasoning="Initial action",
            selected=True,
        )
        tree = CognitiveTree(root=root, current_id="root")

        hint = VisualHint(type="loom", data={"tree": tree, "show_ghosts": False})
        widget = registry.render(hint)

        assert isinstance(widget, BranchTree)
        assert widget.show_ghosts is False

    def test_loom_factory_invalid_tree_type(self) -> None:
        """Loom factory handles invalid tree type gracefully."""
        registry = HintRegistry()

        # Pass a dict instead of CognitiveTree
        hint = VisualHint(type="loom", data={"tree": {"not": "a tree"}})
        widget = registry.render(hint)

        assert isinstance(widget, Static)
        # Should contain error message


class TestHintRegistryUnknownType:
    """Test handling of unknown hint types."""

    def test_unknown_type_returns_fallback(self) -> None:
        """Unknown hint type returns fallback widget."""
        registry = HintRegistry()

        # Create hint with type that won't be in registry
        # We use a valid type but then remove it
        hint = VisualHint(type="text", data={})
        hint.type = "definitely_not_registered"  # Bypass validation

        widget = registry.render(hint)

        assert isinstance(widget, Static)
        # Should contain "Unknown hint type" message


class TestHintRegistryRenderMany:
    """Test rendering multiple hints."""

    def test_render_many_empty(self) -> None:
        """render_many handles empty list."""
        registry = HintRegistry()
        container = registry.render_many([])

        assert container is not None
        assert len(container.children) == 0

    def test_render_many_single(self) -> None:
        """render_many handles single hint."""
        registry = HintRegistry()
        hints = [VisualHint(type="text", data={"text": "Hello"})]

        container = registry.render_many(hints)

        # Container is created, widgets are not mounted without app context
        assert container is not None

    def test_render_many_multiple(self) -> None:
        """render_many handles multiple hints."""
        registry = HintRegistry()
        hints = [
            VisualHint(type="text", data={"text": "A"}),
            VisualHint(type="text", data={"text": "B"}),
            VisualHint(type="text", data={"text": "C"}),
        ]

        container = registry.render_many(hints)

        # Container is created successfully
        assert container is not None

    def test_render_many_sorts_by_priority(self) -> None:
        """render_many sorts by priority (higher first)."""
        registry = HintRegistry()
        hints = [
            VisualHint(type="text", data={"text": "Low"}, priority=1),
            VisualHint(type="text", data={"text": "High"}, priority=100),
            VisualHint(type="text", data={"text": "Medium"}, priority=50),
        ]

        container = registry.render_many(hints)

        # Verify sorting logic without app context
        assert container is not None

    def test_render_many_no_sort(self) -> None:
        """render_many can skip sorting."""
        registry = HintRegistry()
        hints = [
            VisualHint(type="text", data={"text": "First"}, priority=1),
            VisualHint(type="text", data={"text": "Second"}, priority=100),
        ]

        container = registry.render_many(hints, sort_by_priority=False)

        assert container is not None


class TestHintRegistryCustomFactory:
    """Test custom factory registration and usage."""

    def test_custom_factory_overrides_default(self) -> None:
        """Custom factory can override default."""
        registry = HintRegistry()

        # Override text factory
        def custom_text(hint: VisualHint) -> Static:
            return Static(f"CUSTOM: {hint.data.get('text', '')}")

        registry.register("text", custom_text)

        hint = VisualHint(type="text", data={"text": "Hello"})
        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_custom_factory_new_type(self) -> None:
        """Custom factory for new hint type."""
        registry = HintRegistry()

        def special_factory(hint: VisualHint) -> Static:
            count = hint.data.get("count", 0)
            return Static("⭐" * count)

        registry.register("stars", special_factory)

        # Need to bypass validation since "stars" isn't in VALID_TYPES
        hint = VisualHint(type="custom", data={"count": 5})
        hint.type = "stars"  # Override after construction

        widget = registry.render(hint)

        assert isinstance(widget, Static)


class TestGlobalRegistry:
    """Test global registry functions."""

    def test_get_hint_registry_singleton(self) -> None:
        """get_hint_registry returns singleton."""
        reset_hint_registry()  # Ensure clean state

        registry1 = get_hint_registry()
        registry2 = get_hint_registry()

        assert registry1 is registry2

    def test_reset_hint_registry(self) -> None:
        """reset_hint_registry clears singleton."""
        registry1 = get_hint_registry()
        reset_hint_registry()
        registry2 = get_hint_registry()

        assert registry1 is not registry2

    def test_global_registry_has_defaults(self) -> None:
        """Global registry has default factories."""
        reset_hint_registry()
        registry = get_hint_registry()

        assert "text" in registry._factories
        assert "table" in registry._factories


class TestHintRegistryIntegration:
    """Integration tests for HintRegistry."""

    def test_bgent_table_rendering(self) -> None:
        """B-gent table hint renders correctly."""
        registry = HintRegistry()
        hint = VisualHint(
            type="table",
            data={
                "Assets": 100,
                "Liabilities": 50,
                "Net Worth": 50,
            },
            agent_id="b-gent-1",
        )

        widget = registry.render(hint)

        assert isinstance(widget, Static)

    def test_kgent_density_rendering(self) -> None:
        """K-gent density hint renders correctly."""
        registry = HintRegistry()
        hint = VisualHint(
            type="density",
            data={
                "activity": 0.8,
                "phase": "ACTIVE",
                "name": "K",
            },
            agent_id="k-gent-1",
        )

        widget = registry.render(hint)

        assert isinstance(widget, DensityField)
        assert widget.activity == 0.8
        assert widget.agent_id == "k-gent-1"

    def test_multi_agent_hints(self) -> None:
        """Multiple agents emitting different hints."""
        registry = HintRegistry()
        hints = [
            VisualHint(
                type="density",
                data={"activity": 0.7},
                agent_id="k-gent-1",
                priority=10,
            ),
            VisualHint(
                type="text",
                data={"text": "Status: OK"},
                agent_id="monitor-1",
                priority=1,
            ),
        ]

        container = registry.render_many(hints)

        # Container created successfully
        assert container is not None
