"""
Tests for VisualHint protocol.

Verifies hint validation, type checking, and edge cases.
"""

import pytest
from agents.i.data.hints import VisualHint, validate_hint


class TestVisualHintValidation:
    """Test VisualHint validation."""

    def test_valid_hint_minimal(self) -> None:
        """Minimal valid hint with just type."""
        hint = VisualHint(type="text")

        assert hint.type == "text"
        assert hint.data == {}
        assert hint.position == "main"
        assert hint.priority == 0
        assert hint.agent_id == ""

    def test_valid_hint_full(self) -> None:
        """Fully specified valid hint."""
        hint = VisualHint(
            type="table",
            data={"key": "value"},
            position="sidebar",
            priority=10,
            agent_id="b-gent-1",
        )

        assert hint.type == "table"
        assert hint.data == {"key": "value"}
        assert hint.position == "sidebar"
        assert hint.priority == 10
        assert hint.agent_id == "b-gent-1"

    def test_invalid_hint_type(self) -> None:
        """Invalid hint type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown hint type"):
            VisualHint(type="invalid_type")

    def test_invalid_position(self) -> None:
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError, match="Unknown position"):
            VisualHint(type="text", position="invalid_position")

    def test_data_must_be_dict(self) -> None:
        """data parameter must be dict."""
        with pytest.raises(TypeError, match="data must be dict"):
            VisualHint(type="text", data="not a dict")  # type: ignore

    def test_priority_must_be_int(self) -> None:
        """priority parameter must be int."""
        with pytest.raises(TypeError, match="priority must be int"):
            VisualHint(type="text", priority=3.5)  # type: ignore

    def test_all_valid_types(self) -> None:
        """All declared valid types should work."""
        valid_types = [
            "density",
            "table",
            "graph",
            "sparkline",
            "text",
            "loom",
            "custom",
        ]

        for hint_type in valid_types:
            hint = VisualHint(type=hint_type)
            assert hint.type == hint_type

    def test_all_valid_positions(self) -> None:
        """All declared valid positions should work."""
        valid_positions = ["main", "sidebar", "overlay", "footer"]

        for position in valid_positions:
            hint = VisualHint(type="text", position=position)
            assert hint.position == position


class TestVisualHintData:
    """Test VisualHint data handling."""

    def test_empty_data_default(self) -> None:
        """Default data is empty dict."""
        hint = VisualHint(type="text")
        assert hint.data == {}

    def test_data_preserves_structure(self) -> None:
        """Data structure is preserved."""
        data = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 42,
        }

        hint = VisualHint(type="custom", data=data)

        assert hint.data == data
        assert hint.data["nested"]["key"] == "value"
        assert hint.data["list"] == [1, 2, 3]

    def test_data_not_shared_between_hints(self) -> None:
        """Each hint gets its own data dict."""
        hint1 = VisualHint(type="text")
        hint2 = VisualHint(type="text")

        hint1.data["key"] = "value"

        assert "key" not in hint2.data


class TestVisualHintPriority:
    """Test priority handling."""

    def test_default_priority_zero(self) -> None:
        """Default priority is 0."""
        hint = VisualHint(type="text")
        assert hint.priority == 0

    def test_negative_priority(self) -> None:
        """Negative priorities are valid."""
        hint = VisualHint(type="text", priority=-10)
        assert hint.priority == -10

    def test_large_priority(self) -> None:
        """Large priorities are valid."""
        hint = VisualHint(type="text", priority=999999)
        assert hint.priority == 999999


class TestValidateHint:
    """Test validate_hint function."""

    def test_validate_valid_hint(self) -> None:
        """Valid hint passes validation."""
        hint = VisualHint(type="text")
        validate_hint(hint)  # Should not raise

    def test_validate_not_hint(self) -> None:
        """Non-hint object fails validation."""
        with pytest.raises(TypeError, match="Expected VisualHint"):
            validate_hint("not a hint")  # type: ignore

    def test_validate_none(self) -> None:
        """None fails validation."""
        with pytest.raises(TypeError, match="Expected VisualHint"):
            validate_hint(None)  # type: ignore


class TestVisualHintUseCases:
    """Test real-world use cases for VisualHint."""

    def test_bgent_table_hint(self) -> None:
        """B-gent (Banker) emits table hint."""
        hint = VisualHint(
            type="table",
            data={
                "Assets": 100,
                "Liabilities": 50,
                "Net Worth": 50,
            },
            position="sidebar",
            agent_id="b-gent-1",
        )

        assert hint.type == "table"
        assert hint.data["Assets"] == 100

    def test_ygent_graph_hint(self) -> None:
        """Y-gent (Topology) emits graph hint."""
        hint = VisualHint(
            type="graph",
            data={
                "nodes": ["A", "B", "C"],
                "edges": [("A", "B"), ("B", "C")],
            },
            position="main",
            priority=10,
            agent_id="y-gent-1",
        )

        assert hint.type == "graph"
        assert len(hint.data["nodes"]) == 3

    def test_kgent_density_hint(self) -> None:
        """K-gent emits density hint."""
        hint = VisualHint(
            type="density",
            data={
                "activity": 0.7,
                "phase": "ACTIVE",
                "name": "K",
            },
            position="main",
            agent_id="k-gent-1",
        )

        assert hint.type == "density"
        assert hint.data["activity"] == 0.7

    def test_sparkline_hint(self) -> None:
        """Agent emits sparkline hint."""
        hint = VisualHint(
            type="sparkline",
            data={
                "values": [1.0, 2.0, 3.0, 4.0, 5.0],
                "width": 20,
            },
            position="footer",
            agent_id="monitor-1",
        )

        assert hint.type == "sparkline"
        assert len(hint.data["values"]) == 5

    def test_text_hint(self) -> None:
        """Agent emits simple text hint."""
        hint = VisualHint(
            type="text",
            data={"text": "Hello from agent"},
            position="overlay",
            priority=100,
            agent_id="notifier-1",
        )

        assert hint.type == "text"
        assert hint.position == "overlay"
        assert hint.priority == 100

    def test_custom_hint(self) -> None:
        """Agent emits custom hint type."""
        hint = VisualHint(
            type="custom",
            data={
                "widget_class": "MyCustomWidget",
                "params": {"color": "blue"},
            },
            position="main",
            agent_id="custom-agent-1",
        )

        assert hint.type == "custom"
        assert hint.data["widget_class"] == "MyCustomWidget"
