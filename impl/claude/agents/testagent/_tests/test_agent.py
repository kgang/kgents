"""
Tests for TestagentAgent.

Generated with `kgents new testagent`.
"""

from __future__ import annotations

import pytest

from ..agent import TestagentAgent


class TestTestagentAgent:
    """Tests for TestagentAgent."""

    def test_agent_name(self) -> None:
        """Agent has correct name."""
        agent = TestagentAgent()
        assert agent.name == "testagent"

    @pytest.mark.asyncio
    async def test_invoke_raises_not_implemented(self) -> None:
        """invoke() raises NotImplementedError until implemented."""
        agent = TestagentAgent()
        with pytest.raises(NotImplementedError, match="Implement me"):
            await agent.invoke("test")

    @pytest.mark.asyncio
    async def test_invoke_with_sample_input(self) -> None:
        """invoke() processes sample input correctly.

        TODO: Uncomment and modify after implementing invoke().
        """
        # agent = TestagentAgent()
        # result = await agent.invoke("test")
        # assert result is not None
        pass