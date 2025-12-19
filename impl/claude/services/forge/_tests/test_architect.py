"""
Tests for ArchitectArtisan.

Tests categorical design generation with both LLM-powered and stub modes.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ..artisans.architect import AgentDesign, ArchitectArtisan
from ..commission import Commission, CommissionStatus

# === AgentDesign Tests ===


class TestAgentDesign:
    """Tests for the AgentDesign dataclass."""

    def test_from_dict_basic(self) -> None:
        """Test creating AgentDesign from dictionary."""
        data = {
            "name": "TestAgent",
            "description": "A test agent",
            "states": ["IDLE", "ACTIVE"],
            "initial_state": "IDLE",
            "transitions": {"IDLE": ["ACTIVE"], "ACTIVE": ["IDLE"]},
            "operations": [{"name": "run", "input": "str", "output": "bool"}],
            "laws": ["identity"],
            "rationale": "For testing",
        }

        design = AgentDesign.from_dict(data)

        assert design.name == "TestAgent"
        assert design.states == ["IDLE", "ACTIVE"]
        assert design.initial_state == "IDLE"
        assert len(design.operations) == 1

    def test_from_dict_defaults(self) -> None:
        """Test AgentDesign uses sensible defaults for missing fields."""
        design = AgentDesign.from_dict({})

        assert design.name == "UnnamedAgent"
        assert "IDLE" in design.states
        assert "ACTIVE" in design.states
        assert design.initial_state == "IDLE"

    def test_to_dict_roundtrip(self) -> None:
        """Test that to_dict and from_dict are inverses."""
        original = AgentDesign(
            name="RoundtripAgent",
            description="Tests roundtrip",
            states=["A", "B", "C"],
            initial_state="A",
            transitions={"A": ["B"], "B": ["C"]},
            operations=[{"name": "op1", "input": "X", "output": "Y"}],
            laws=["law1", "law2"],
            rationale="Testing",
        )

        data = original.to_dict()
        restored = AgentDesign.from_dict(data)

        assert restored.name == original.name
        assert restored.states == original.states
        assert restored.transitions == original.transitions

    def test_validate_empty_name(self) -> None:
        """Test validation catches empty name."""
        design = AgentDesign(
            name="",
            description="",
            states=["A"],
            initial_state="A",
            transitions={},
            operations=[],
            laws=[],
            rationale="",
        )

        errors = design.validate()
        assert "Agent name is required" in errors

    def test_validate_invalid_initial_state(self) -> None:
        """Test validation catches initial state not in states list."""
        design = AgentDesign(
            name="Test",
            description="",
            states=["A", "B"],
            initial_state="C",  # Not in states
            transitions={},
            operations=[],
            laws=[],
            rationale="",
        )

        errors = design.validate()
        assert any("initial state" in e.lower() for e in errors)

    def test_validate_invalid_transition_from(self) -> None:
        """Test validation catches transitions from unknown state."""
        design = AgentDesign(
            name="Test",
            description="",
            states=["A", "B"],
            initial_state="A",
            transitions={"C": ["A"]},  # C is not a valid state
            operations=[],
            laws=[],
            rationale="",
        )

        errors = design.validate()
        assert any("unknown state" in e.lower() for e in errors)

    def test_validate_invalid_transition_to(self) -> None:
        """Test validation catches transitions to unknown state."""
        design = AgentDesign(
            name="Test",
            description="",
            states=["A", "B"],
            initial_state="A",
            transitions={"A": ["C"]},  # C is not a valid state
            operations=[],
            laws=[],
            rationale="",
        )

        errors = design.validate()
        assert any("unknown state" in e.lower() for e in errors)

    def test_validate_valid_design(self) -> None:
        """Test validation passes for valid design."""
        design = AgentDesign(
            name="ValidAgent",
            description="A valid agent",
            states=["IDLE", "ACTIVE", "ERROR"],
            initial_state="IDLE",
            transitions={
                "IDLE": ["ACTIVE"],
                "ACTIVE": ["IDLE", "ERROR"],
                "ERROR": ["IDLE"],
            },
            operations=[{"name": "process", "input": "str", "output": "str"}],
            laws=["identity", "associativity"],
            rationale="Valid design for testing",
        )

        errors = design.validate()
        assert errors == []


# === ArchitectArtisan Tests ===


class TestArchitectArtisan:
    """Tests for the ArchitectArtisan."""

    @pytest.fixture
    def commission(self) -> Commission:
        """Create a test commission."""
        return Commission(
            id="test-commission-001",
            intent="Build a simple counter agent that can increment and decrement",
            name="CounterAgent",
            status=CommissionStatus.DESIGNING,
        )

    def test_init_without_soul(self) -> None:
        """Test creating architect without K-gent soul."""
        architect = ArchitectArtisan(soul=None)
        assert architect.soul is None

    @pytest.mark.asyncio
    async def test_design_stub_mode(self, commission: Commission) -> None:
        """Test design generation in stub mode (no soul)."""
        architect = ArchitectArtisan(soul=None)

        output = await architect.design(commission)

        assert output.status == "complete"
        assert output.artisan.value == "architect"
        assert output.output is not None
        assert "states" in output.output
        assert "transitions" in output.output
        assert output.annotation is not None

    @pytest.mark.asyncio
    async def test_design_stub_uses_commission_name(self, commission: Commission) -> None:
        """Test that stub design uses commission name."""
        architect = ArchitectArtisan(soul=None)

        output = await architect.design(commission)

        # Name should be derived from commission
        assert output.output is not None
        # The stub may modify the name, but should contain something
        assert output.output.get("name")

    @pytest.mark.asyncio
    async def test_design_stub_without_name(self) -> None:
        """Test stub design derives name from intent."""
        commission = Commission(
            id="test-002",
            intent="Track user preferences across sessions",
            name=None,  # No explicit name
            status=CommissionStatus.DESIGNING,
        )
        architect = ArchitectArtisan(soul=None)

        output = await architect.design(commission)

        assert output.status == "complete"
        assert output.output is not None
        # Should derive name from intent
        assert output.output.get("name")

    @pytest.mark.asyncio
    async def test_design_with_mock_soul(self, commission: Commission) -> None:
        """Test design generation with mocked K-gent soul."""
        # Create a mock soul
        mock_soul = MagicMock()
        mock_dialogue_output = MagicMock()
        mock_dialogue_output.response = """{
            "name": "CounterAgent",
            "description": "A counter that can increment and decrement",
            "states": ["IDLE", "COUNTING"],
            "initial_state": "IDLE",
            "transitions": {"IDLE": ["COUNTING"], "COUNTING": ["IDLE"]},
            "operations": [
                {"name": "increment", "input": "void", "output": "int", "description": "Add one"},
                {"name": "decrement", "input": "void", "output": "int", "description": "Subtract one"}
            ],
            "laws": ["Identity: counter >> identity = counter"],
            "rationale": "Simple state machine for counting operations"
        }"""
        mock_soul.dialogue = AsyncMock(return_value=mock_dialogue_output)

        architect = ArchitectArtisan(soul=mock_soul)
        output = await architect.design(commission)

        assert output.status == "complete"
        assert output.output is not None
        assert output.output["name"] == "CounterAgent"
        assert "IDLE" in output.output["states"]
        assert "COUNTING" in output.output["states"]
        assert len(output.output["operations"]) == 2

    @pytest.mark.asyncio
    async def test_design_handles_invalid_json(self, commission: Commission) -> None:
        """Test design handles invalid JSON from LLM gracefully."""
        mock_soul = MagicMock()
        mock_dialogue_output = MagicMock()
        mock_dialogue_output.response = "This is not valid JSON at all"
        mock_soul.dialogue = AsyncMock(return_value=mock_dialogue_output)

        architect = ArchitectArtisan(soul=mock_soul)
        output = await architect.design(commission)

        # Should fail gracefully
        assert output.status == "failed"
        assert output.error is not None
        assert "JSON" in output.error or "parse" in output.error.lower()

    @pytest.mark.asyncio
    async def test_design_handles_json_in_markdown(self, commission: Commission) -> None:
        """Test design handles JSON wrapped in markdown code fences."""
        mock_soul = MagicMock()
        mock_dialogue_output = MagicMock()
        mock_dialogue_output.response = """```json
{
    "name": "MarkdownAgent",
    "description": "Wrapped in markdown",
    "states": ["A", "B"],
    "initial_state": "A",
    "transitions": {"A": ["B"]},
    "operations": [],
    "laws": [],
    "rationale": "Test"
}
```"""
        mock_soul.dialogue = AsyncMock(return_value=mock_dialogue_output)

        architect = ArchitectArtisan(soul=mock_soul)
        output = await architect.design(commission)

        assert output.status == "complete"
        assert output.output is not None
        assert output.output["name"] == "MarkdownAgent"

    @pytest.mark.asyncio
    async def test_design_sets_timestamps(self, commission: Commission) -> None:
        """Test that design sets started_at and completed_at."""
        architect = ArchitectArtisan(soul=None)

        output = await architect.design(commission)

        assert output.started_at is not None
        assert output.completed_at is not None
        assert output.completed_at >= output.started_at

    def test_derive_name_from_intent(self) -> None:
        """Test name derivation from intent."""
        architect = ArchitectArtisan(soul=None)

        # Simple case
        name = architect._derive_name("Build a counter")
        assert "Agent" in name

        # Empty words case
        name = architect._derive_name("   ")
        assert name == "UnnamedAgent"


# === Integration Tests ===


class TestArchitectIntegration:
    """Integration tests for Architect in commission flow."""

    @pytest.mark.asyncio
    async def test_design_produces_smith_compatible_output(self) -> None:
        """Test that Architect output can be consumed by Smith."""
        commission = Commission(
            id="integration-test",
            intent="Manage session state for web application",
            name="SessionManager",
            status=CommissionStatus.DESIGNING,
        )

        architect = ArchitectArtisan(soul=None)
        output = await architect.design(commission)

        # Verify output has all fields Smith needs
        assert output.status == "complete"
        design = output.output
        assert design is not None

        # These are required by SmithArtisan.implement()
        assert "name" in design
        assert "states" in design
        assert "transitions" in design
        assert "operations" in design

        # Can be converted back to AgentDesign
        agent_design = AgentDesign.from_dict(design)
        assert agent_design.validate() == []
