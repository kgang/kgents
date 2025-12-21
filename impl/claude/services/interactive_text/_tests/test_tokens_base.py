"""
Tests for MeaningToken base class implementation.

Tests the BaseMeaningToken class including:
- Affordance retrieval
- Interaction handling with trace witness capture
- Token serialization

Feature: meaning-token-frontend
Requirements: 1.2, 6.3, 12.1
"""

from __future__ import annotations

from typing import Any

import pytest

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    InteractionResult,
    Observer,
    ObserverDensity,
    ObserverRole,
)
from services.interactive_text.tokens.base import (
    BaseMeaningToken,
    ExecutionTrace,
    TraceWitness,
    filter_affordances_by_observer,
)

# =============================================================================
# Test Token Implementation
# =============================================================================


class TestToken(BaseMeaningToken[str]):
    """Concrete test implementation of BaseMeaningToken."""

    def __init__(
        self,
        text: str,
        position: tuple[int, int],
        affordances: tuple[Affordance, ...] | None = None,
    ) -> None:
        self._text = text
        self._position = position
        self._affordances = affordances or (
            Affordance(
                name="click",
                action=AffordanceAction.CLICK,
                handler="test.click",
                enabled=True,
            ),
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="test.hover",
                enabled=True,
            ),
        )
        self._action_results: dict[AffordanceAction, Any] = {}

    @property
    def token_type(self) -> str:
        return "test_token"

    @property
    def source_text(self) -> str:
        return self._text

    @property
    def source_position(self) -> tuple[int, int]:
        return self._position

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        return list(self._affordances)

    async def project(self, target: str, observer: Observer) -> str:
        return f"[{target}] {self._text}"

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        # Return pre-configured result or default
        return self._action_results.get(action, {"action": action.value, "success": True})

    def set_action_result(self, action: AffordanceAction, result: Any) -> None:
        """Set the result for a specific action (for testing)."""
        self._action_results[action] = result


# =============================================================================
# ExecutionTrace Tests
# =============================================================================


class TestExecutionTrace:
    """Tests for ExecutionTrace dataclass."""

    def test_create_trace(self) -> None:
        """ExecutionTrace can be created with required fields."""
        trace = ExecutionTrace(
            agent_path="self.document.task.toggle",
            operation="toggle",
        )
        assert trace.agent_path == "self.document.task.toggle"
        assert trace.operation == "toggle"
        assert trace.input_data == {}
        assert trace.output_data is None

    def test_trace_with_data(self) -> None:
        """ExecutionTrace can include input and output data."""
        trace = ExecutionTrace(
            agent_path="self.document.task.toggle",
            operation="toggle",
            input_data={"task_id": "123", "new_state": True},
            output_data={"success": True},
            observer_id="obs-456",
        )
        assert trace.input_data["task_id"] == "123"
        assert trace.output_data["success"] is True
        assert trace.observer_id == "obs-456"

    def test_trace_to_dict(self) -> None:
        """ExecutionTrace can be serialized to dict."""
        trace = ExecutionTrace(
            agent_path="test.path",
            operation="test_op",
            input_data={"key": "value"},
        )
        result = trace.to_dict()

        assert result["agent_path"] == "test.path"
        assert result["operation"] == "test_op"
        assert result["input_data"] == {"key": "value"}
        assert "timestamp" in result


# =============================================================================
# TraceWitness Tests
# =============================================================================


class TestTraceWitness:
    """Tests for TraceWitness dataclass."""

    def test_create_witness(self) -> None:
        """TraceWitness can be created with trace."""
        trace = ExecutionTrace(
            agent_path="test.path",
            operation="test_op",
        )
        witness = TraceWitness(
            id="witness-123",
            trace=trace,
        )
        assert witness.id == "witness-123"
        assert witness.trace == trace
        assert witness.verified is False

    def test_witness_to_dict(self) -> None:
        """TraceWitness can be serialized to dict."""
        trace = ExecutionTrace(
            agent_path="test.path",
            operation="test_op",
        )
        witness = TraceWitness(
            id="witness-123",
            trace=trace,
            verified=True,
            verification_result={"passed": True},
        )
        result = witness.to_dict()

        assert result["id"] == "witness-123"
        assert result["verified"] is True
        assert result["verification_result"]["passed"] is True
        assert "trace" in result


# =============================================================================
# BaseMeaningToken Tests
# =============================================================================


class TestBaseMeaningToken:
    """Tests for BaseMeaningToken base class."""

    @pytest.fixture
    def observer(self) -> Observer:
        """Create a test observer."""
        return Observer.create(
            capabilities=frozenset(["llm", "network"]),
            density=ObserverDensity.COMFORTABLE,
            role=ObserverRole.EDITOR,
        )

    @pytest.fixture
    def token(self) -> TestToken:
        """Create a test token."""
        return TestToken(
            text="test content",
            position=(0, 12),
        )

    def test_token_properties(self, token: TestToken) -> None:
        """Token has correct properties."""
        assert token.token_type == "test_token"
        assert token.source_text == "test content"
        assert token.source_position == (0, 12)
        assert token.token_id == "test_token:0:12"

    def test_token_to_dict(self, token: TestToken) -> None:
        """Token can be serialized to dict."""
        result = token.to_dict()

        assert result["token_type"] == "test_token"
        assert result["source_text"] == "test content"
        assert result["source_position"] == (0, 12)
        assert result["token_id"] == "test_token:0:12"

    @pytest.mark.asyncio
    async def test_get_affordances(self, token: TestToken, observer: Observer) -> None:
        """Token returns affordances for observer."""
        affordances = await token.get_affordances(observer)

        assert len(affordances) == 2
        assert any(a.action == AffordanceAction.CLICK for a in affordances)
        assert any(a.action == AffordanceAction.HOVER for a in affordances)

    @pytest.mark.asyncio
    async def test_project(self, token: TestToken, observer: Observer) -> None:
        """Token can project to target."""
        result = await token.project("cli", observer)
        assert result == "[cli] test content"

    @pytest.mark.asyncio
    async def test_on_interact_success(self, token: TestToken, observer: Observer) -> None:
        """on_interact returns success for valid action."""
        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert result.data is not None
        assert result.witness_id is not None  # Trace captured

    @pytest.mark.asyncio
    async def test_on_interact_unavailable_action(
        self, token: TestToken, observer: Observer
    ) -> None:
        """on_interact returns not_available for unavailable action."""
        result = await token.on_interact(AffordanceAction.DRAG, observer)

        assert result.success is False
        assert "not available" in result.error.lower()

    @pytest.mark.asyncio
    async def test_on_interact_disabled_affordance(self, observer: Observer) -> None:
        """on_interact returns not_available for disabled affordance."""
        token = TestToken(
            text="test",
            position=(0, 4),
            affordances=(
                Affordance(
                    name="click",
                    action=AffordanceAction.CLICK,
                    handler="test.click",
                    enabled=False,  # Disabled
                ),
            ),
        )

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is False
        assert "not available" in result.error.lower()

    @pytest.mark.asyncio
    async def test_on_interact_captures_trace(self, token: TestToken, observer: Observer) -> None:
        """on_interact captures trace witness when enabled."""
        result = await token.on_interact(
            AffordanceAction.CLICK,
            observer,
            capture_trace=True,
        )

        assert result.success is True
        assert result.witness_id is not None

    @pytest.mark.asyncio
    async def test_on_interact_no_trace(self, token: TestToken, observer: Observer) -> None:
        """on_interact skips trace when disabled."""
        result = await token.on_interact(
            AffordanceAction.CLICK,
            observer,
            capture_trace=False,
        )

        assert result.success is True
        assert result.witness_id is None

    @pytest.mark.asyncio
    async def test_on_interact_with_kwargs(self, token: TestToken, observer: Observer) -> None:
        """on_interact passes kwargs to action handler."""
        token.set_action_result(
            AffordanceAction.CLICK,
            {"received_kwargs": True},
        )

        result = await token.on_interact(
            AffordanceAction.CLICK,
            observer,
            extra_param="value",
        )

        assert result.success is True


# =============================================================================
# filter_affordances_by_observer Tests
# =============================================================================


class TestFilterAffordancesByObserver:
    """Tests for filter_affordances_by_observer utility."""

    def test_no_requirements(self) -> None:
        """All affordances returned when no requirements specified."""
        affordances = (
            Affordance(name="a", action=AffordanceAction.CLICK, handler="h1"),
            Affordance(name="b", action=AffordanceAction.HOVER, handler="h2"),
        )
        observer = Observer.create()

        result = filter_affordances_by_observer(affordances, observer)

        assert len(result) == 2

    def test_filter_by_capability(self) -> None:
        """Affordances filtered by observer capabilities."""
        affordances = (
            Affordance(name="llm_action", action=AffordanceAction.CLICK, handler="h1"),
            Affordance(name="basic_action", action=AffordanceAction.HOVER, handler="h2"),
        )
        observer = Observer.create(capabilities=frozenset(["network"]))

        required = {
            "llm_action": frozenset(["llm"]),
            "basic_action": frozenset(),
        }

        result = filter_affordances_by_observer(affordances, observer, required)

        # llm_action should be disabled, basic_action enabled
        llm_affordance = next(a for a in result if a.name == "llm_action")
        basic_affordance = next(a for a in result if a.name == "basic_action")

        assert llm_affordance.enabled is False
        assert basic_affordance.enabled is True

    def test_observer_with_all_capabilities(self) -> None:
        """All affordances enabled when observer has all capabilities."""
        affordances = (
            Affordance(name="llm_action", action=AffordanceAction.CLICK, handler="h1"),
            Affordance(name="network_action", action=AffordanceAction.HOVER, handler="h2"),
        )
        observer = Observer.create(capabilities=frozenset(["llm", "network", "verification"]))

        required = {
            "llm_action": frozenset(["llm"]),
            "network_action": frozenset(["network"]),
        }

        result = filter_affordances_by_observer(affordances, observer, required)

        assert all(a.enabled for a in result)
