"""
Template for agent law verification tests.

Philosophy: Every agent proves its category citizenship.

This template demonstrates Phase 2 of the test evolution plan:
- Law markers for categorization
- Identity law verification
- Associativity verification

Copy this template when creating tests for new agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import pytest

from agents.poly.types import Agent
from bootstrap import ID, compose

if TYPE_CHECKING:
    from agents.o.bootstrap_witness import TestAgent


class TestAgentLawTemplate:
    """
    Template for category law verification.

    Every agent should have tests verifying:
    1. Left identity: Id >> f == f
    2. Right identity: f >> Id == f
    3. Associativity: (f >> g) >> h == f >> (g >> h)
    """

    @pytest.fixture
    def sample_agent(self) -> "TestAgent[Any, Any]":
        """
        Create the agent under test.

        Replace with your actual agent constructor.
        """
        from agents.o.bootstrap_witness import TestAgent

        return TestAgent(name="sample", transform=lambda x: x * 2)

    @pytest.fixture
    def test_inputs(self) -> Any:
        """Standard test inputs for law verification."""
        return [0, 1, -1, 42, 1000]

    # =========================================================================
    # Identity Laws
    # =========================================================================

    @pytest.mark.law("identity")
    @pytest.mark.law_identity
    @pytest.mark.asyncio
    async def test_left_identity(
        self, sample_agent: "TestAgent[Any, Any]", test_inputs: Any
    ) -> None:
        """
        Test left identity law: Id >> f == f.

        The identity agent composed before any agent should
        have no effect on the result.
        """
        for input_val in test_inputs:
            composed: Any = compose(cast(Agent[Any, Any], ID), cast(Agent[Any, Any], sample_agent))

            direct = await sample_agent.invoke(input_val)
            via_id = await composed.invoke(input_val)

            assert direct == via_id, (
                f"Left identity violated for input {input_val}: direct={direct}, via_id={via_id}"
            )

    @pytest.mark.law("identity")
    @pytest.mark.law_identity
    @pytest.mark.asyncio
    async def test_right_identity(
        self, sample_agent: "TestAgent[Any, Any]", test_inputs: Any
    ) -> None:
        """
        Test right identity law: f >> Id == f.

        The identity agent composed after any agent should
        have no effect on the result.
        """
        for input_val in test_inputs:
            composed: Any = compose(cast(Agent[Any, Any], sample_agent), cast(Agent[Any, Any], ID))

            direct = await sample_agent.invoke(input_val)
            via_id = await composed.invoke(input_val)

            assert direct == via_id, (
                f"Right identity violated for input {input_val}: direct={direct}, via_id={via_id}"
            )

    # =========================================================================
    # Associativity Law
    # =========================================================================

    @pytest.mark.law("associativity")
    @pytest.mark.law_associativity
    @pytest.mark.asyncio
    async def test_associativity(
        self, sample_agent: "TestAgent[Any, Any]", test_inputs: Any
    ) -> None:
        """
        Test associativity law: (f >> g) >> h == f >> (g >> h).

        Composition grouping should not affect the result.
        """
        from agents.o.bootstrap_witness import TestAgent

        f = sample_agent
        g: TestAgent[Any, Any] = TestAgent(name="g", transform=lambda x: x + 1)
        h: TestAgent[Any, Any] = TestAgent(name="h", transform=lambda x: x - 1)

        for input_val in test_inputs:
            left: Any = compose(
                compose(cast(Agent[Any, Any], f), cast(Agent[Any, Any], g)),
                cast(Agent[Any, Any], h),
            )
            right: Any = compose(
                cast(Agent[Any, Any], f),
                compose(cast(Agent[Any, Any], g), cast(Agent[Any, Any], h)),
            )

            left_result = await left.invoke(input_val)
            right_result = await right.invoke(input_val)

            # Create string representations without using >> operator
            left_repr = f"(({f.name} >> {g.name}) >> {h.name})"
            right_repr = f"({f.name} >> ({g.name} >> {h.name}))"

            assert left_result == right_result, (
                f"Associativity violated for input {input_val}: "
                f"left={left_repr}={left_result}, "
                f"right={right_repr}={right_result}"
            )

    # =========================================================================
    # Composition Closure
    # =========================================================================

    @pytest.mark.law("closure")
    @pytest.mark.asyncio
    async def test_composition_closure(self, sample_agent: "TestAgent[Any, Any]") -> None:
        """
        Test that composition produces a valid agent.

        The result of f >> g should have an invoke method
        and behave as an agent.
        """
        from agents.o.bootstrap_witness import TestAgent

        g: TestAgent[Any, Any] = TestAgent(name="g", transform=lambda x: x + 1)

        composed: Any = compose(cast(Agent[Any, Any], sample_agent), cast(Agent[Any, Any], g))

        # Should have invoke method
        assert hasattr(composed, "invoke"), "Composed agent missing invoke method"

        # Should be callable
        result = await composed.invoke(5)
        assert result is not None, "Composed agent returned None"


class TestIdAgent:
    """Tests specifically for the Identity agent."""

    @pytest.mark.law("identity")
    @pytest.mark.asyncio
    async def test_id_is_transparent(self) -> None:
        """ID should pass through any value unchanged."""
        test_values = [
            None,
            0,
            1,
            -1,
            3.14,
            "hello",
            [1, 2, 3],
            {"key": "value"},
        ]

        for val in test_values:
            result = await ID.invoke(val)
            assert result == val, f"ID changed {val!r} to {result!r}"

    @pytest.mark.law("identity")
    @pytest.mark.asyncio
    async def test_id_self_composition(self) -> None:
        """Id >> Id == Id."""
        composed = compose(ID, ID)

        for val in [0, 1, "test", [1, 2]]:
            result = await composed.invoke(val)
            assert result == val, f"Id >> Id changed {val!r} to {result!r}"
