"""
Tests for Constitutional Node Integration with DP Bridge.

Verifies that @node(constitutional=True) nodes properly:
- Evaluate invocations against Constitution
- Emit TraceEntry with principle scores
- Integrate with DP Bridge ValueFunction
"""

from __future__ import annotations

from typing import Any

import pytest

from ..node import BaseLogosNode, BasicRendering, Observer
from ..registry import get_node_metadata, node, repopulate_registry, reset_registry
from .conftest import create_mock_umwelt


@pytest.fixture(autouse=True)
def clean_registry():
    """Clean registry before each test."""
    reset_registry()
    yield
    repopulate_registry()


# === Test Node ===


@node("test.constitutional", constitutional=True)
class ConstitutionalTestNode(BaseLogosNode):
    """Test node with constitutional evaluation enabled."""

    @property
    def handle(self) -> str:
        return "test.constitutional"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("test_action",)

    async def manifest(self, observer: Any, **kwargs: Any) -> BasicRendering:
        return BasicRendering(
            summary="Constitutional test node",
            content="A node for testing constitutional evaluation",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Any,
        **kwargs: Any,
    ) -> Any:
        if aspect == "test_action":
            return {"status": "success", "aspect": aspect}
        raise NotImplementedError(f"Aspect {aspect} not implemented")


@node("test.nonconstitutional", constitutional=False)
class NonConstitutionalTestNode(BaseLogosNode):
    """Test node without constitutional evaluation."""

    @property
    def handle(self) -> str:
        return "test.nonconstitutional"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("test_action",)

    async def manifest(self, observer: Any, **kwargs: Any) -> BasicRendering:
        return BasicRendering(
            summary="Non-constitutional test node",
            content="A node without constitutional evaluation",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Any,
        **kwargs: Any,
    ) -> Any:
        if aspect == "test_action":
            return {"status": "success", "aspect": aspect}
        raise NotImplementedError(f"Aspect {aspect} not implemented")


# === Tests ===


class TestConstitutionalMetadata:
    """Tests for constitutional flag in node metadata."""

    def test_constitutional_flag_in_metadata(self) -> None:
        """Constitutional flag is stored in node metadata."""
        meta = get_node_metadata(ConstitutionalTestNode)
        assert meta is not None
        assert meta.constitutional is True

    def test_nonconstitutional_flag_in_metadata(self) -> None:
        """Non-constitutional nodes have flag set to False."""
        meta = get_node_metadata(NonConstitutionalTestNode)
        assert meta is not None
        assert meta.constitutional is False


class TestConstitutionalInvocation:
    """Tests for constitutional node invocation."""

    @pytest.mark.asyncio
    async def test_constitutional_node_invokes_successfully(self) -> None:
        """Constitutional node can be invoked."""
        node = ConstitutionalTestNode()
        observer = create_mock_umwelt()

        result = await node.invoke("test_action", observer)

        assert result["status"] == "success"
        assert result["aspect"] == "test_action"

    @pytest.mark.asyncio
    async def test_nonconstitutional_node_invokes_successfully(self) -> None:
        """Non-constitutional node can be invoked normally."""
        node = NonConstitutionalTestNode()
        observer = create_mock_umwelt()

        result = await node.invoke("test_action", observer)

        assert result["status"] == "success"
        assert result["aspect"] == "test_action"

    @pytest.mark.asyncio
    async def test_constitutional_manifest_works(self) -> None:
        """Constitutional node manifest aspect works."""
        node = ConstitutionalTestNode()
        observer = create_mock_umwelt()

        result = await node.invoke("manifest", observer)

        assert hasattr(result, "summary")
        assert "Constitutional test node" in result.summary

    @pytest.mark.asyncio
    async def test_constitutional_evaluation_logged(self, caplog) -> None:
        """Constitutional invocation emits log entry with scores."""
        import logging

        caplog.set_level(logging.INFO, logger="kgents.agentese.constitutional")

        node = ConstitutionalTestNode()
        observer = create_mock_umwelt()

        await node.invoke("test_action", observer)

        # Check that constitutional evaluation was logged
        logs = [rec.message for rec in caplog.records]
        assert any("Constitutional invocation" in log for log in logs)
        assert any("value=" in log for log in logs)


class TestValueFunctionCustomization:
    """Tests for custom ValueFunction override."""

    def test_default_value_function_neutral(self) -> None:
        """Default ValueFunction returns neutral scores."""
        node = ConstitutionalTestNode()
        value_fn = node._get_value_function()

        score = value_fn.evaluate("test", "state:before", "action")

        # Default should be neutral (0.5) for all principles
        assert score.total_score == pytest.approx(0.5, abs=0.1)

    def test_custom_value_function_override(self) -> None:
        """Custom ValueFunction can be provided via override."""
        from services.categorical import Principle, ValueFunction

        class CustomConstitutionalNode(ConstitutionalTestNode):
            def _get_value_function(self) -> ValueFunction:
                # Custom evaluator that gives high scores to "test_action"
                def custom_eval(agent_name: str, state: Any, action: Any) -> float:
                    return 1.0 if "test_action" in agent_name else 0.5

                return ValueFunction(
                    principle_evaluators={
                        Principle.JOY_INDUCING: custom_eval,
                    }
                )

        node = CustomConstitutionalNode()
        value_fn = node._get_value_function()

        score = value_fn.evaluate("test.constitutional.test_action", "state:before", "test_action")

        # JOY_INDUCING should be 1.0, others default to 0.5
        joy_score = next(
            ps for ps in score.principle_scores if ps.principle == Principle.JOY_INDUCING
        )
        assert joy_score.score == 1.0
