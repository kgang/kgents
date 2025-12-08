"""
Unit tests for Symbiont pattern.

Tests cover:
- Stateful computation (state threading)
- Composition with bootstrap agents (f >> g)
- Sync and async logic functions
- Pure logic testability
"""

import asyncio
import pytest
from agents.d import VolatileAgent, Symbiont


@pytest.mark.asyncio
async def test_basic_stateful_computation():
    """Symbiont threads state through invocations."""

    def counter_logic(increment: int, count: int) -> tuple[int, int]:
        """Pure function: (input, state) → (output, new_state)"""
        new_count = count + increment
        return new_count, new_count

    memory = VolatileAgent[int](_state=0)
    counter = Symbiont(logic=counter_logic, memory=memory)

    # First invocation
    result1 = await counter.invoke(1)
    assert result1 == 1

    # Second invocation - remembers previous state
    result2 = await counter.invoke(5)
    assert result2 == 6  # 1 + 5

    # Third invocation
    result3 = await counter.invoke(3)
    assert result3 == 9  # 6 + 3


@pytest.mark.asyncio
async def test_conversational_context():
    """Symbiont maintains conversation history."""
    from dataclasses import dataclass, field
    from typing import List

    @dataclass
    class ConversationState:
        messages: List[tuple[str, str]] = field(default_factory=list)

    def chat_logic(
        user_input: str, state: ConversationState
    ) -> tuple[str, ConversationState]:
        state.messages.append(("user", user_input))
        response = f"Echo: {user_input}"
        state.messages.append(("bot", response))
        return response, state

    memory = VolatileAgent[ConversationState](_state=ConversationState())
    chatbot = Symbiont(logic=chat_logic, memory=memory)

    # First message
    resp1 = await chatbot.invoke("Hello")
    assert resp1 == "Echo: Hello"

    # Second message - history persists
    resp2 = await chatbot.invoke("How are you?")
    assert resp2 == "Echo: How are you?"

    # Check history
    final_state = await memory.load()
    assert len(final_state.messages) == 4  # 2 exchanges
    assert final_state.messages[0] == ("user", "Hello")
    assert final_state.messages[1] == ("bot", "Echo: Hello")


@pytest.mark.asyncio
async def test_async_logic():
    """Symbiont supports async logic functions."""

    async def async_logic(value: int, state: int) -> tuple[int, int]:
        """Async version of stateful computation."""
        # Simulate async work
        await asyncio.sleep(0.001)
        new_state = state + value
        return new_state, new_state

    memory = VolatileAgent[int](_state=0)
    agent = Symbiont(logic=async_logic, memory=memory)

    result1 = await agent.invoke(10)
    assert result1 == 10

    result2 = await agent.invoke(5)
    assert result2 == 15


@pytest.mark.asyncio
async def test_composition_with_bootstrap():
    """Symbiont is a valid Agent - composes via >>."""
    from bootstrap.id import Id

    def logic(x: int, state: int) -> tuple[int, int]:
        return x + state, state + 1

    memory = VolatileAgent[int](_state=0)
    symbiont = Symbiont(logic=logic, memory=memory)

    # Compose with Identity (bootstrap agent)
    pipeline = Id() >> symbiont >> Id()

    result1 = await pipeline.invoke(5)
    assert result1 == 5  # 5 + 0

    result2 = await pipeline.invoke(10)
    assert result2 == 11  # 10 + 1 (state incremented)


@pytest.mark.asyncio
async def test_pure_logic_testability():
    """Logic function can be tested independently."""

    def accumulator_logic(value: int, total: int) -> tuple[int, int]:
        new_total = total + value
        return new_total, new_total

    # Test logic in isolation (no D-gent needed)
    output, new_state = accumulator_logic(5, 10)
    assert output == 15
    assert new_state == 15

    output2, new_state2 = accumulator_logic(3, new_state)
    assert output2 == 18

    # Now test with Symbiont
    memory = VolatileAgent[int](_state=10)
    agent = Symbiont(logic=accumulator_logic, memory=memory)

    result = await agent.invoke(5)
    assert result == 15


@pytest.mark.asyncio
async def test_symbiont_chain():
    """Multiple symbionts can compose."""

    def doubler(x: int, state: int) -> tuple[int, int]:
        return x * 2, state + 1

    def adder(x: int, state: int) -> tuple[int, int]:
        return x + state, state + 10

    memory1 = VolatileAgent[int](_state=0)
    memory2 = VolatileAgent[int](_state=100)

    agent1 = Symbiont(logic=doubler, memory=memory1)
    agent2 = Symbiont(logic=adder, memory=memory2)

    # Compose
    pipeline = agent1 >> agent2

    # First invocation: 5 → 10 (double) → 110 (add 100)
    result1 = await pipeline.invoke(5)
    assert result1 == 110

    # Second invocation: 3 → 6 (double) → 116 (add 110, state incremented)
    result2 = await pipeline.invoke(3)
    assert result2 == 116


@pytest.mark.asyncio
async def test_state_independence():
    """Each Symbiont maintains independent state."""

    def incrementer(x: int, state: int) -> tuple[int, int]:
        return x + state, state + 1

    memory1 = VolatileAgent[int](_state=0)
    memory2 = VolatileAgent[int](_state=100)

    agent1 = Symbiont(logic=incrementer, memory=memory1)
    agent2 = Symbiont(logic=incrementer, memory=memory2)

    # Invoke both
    result1 = await agent1.invoke(5)
    result2 = await agent2.invoke(5)

    assert result1 == 5  # 5 + 0
    assert result2 == 105  # 5 + 100

    # States are independent
    result3 = await agent1.invoke(10)
    result4 = await agent2.invoke(10)

    assert result3 == 11  # 10 + 1 (agent1 state incremented)
    assert result4 == 111  # 10 + 101 (agent2 state incremented)


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        """Run all tests manually."""
        print("Running Symbiont tests...")

        print("\n1. Basic stateful computation")
        await test_basic_stateful_computation()
        print("✓ Passed")

        print("\n2. Conversational context")
        await test_conversational_context()
        print("✓ Passed")

        print("\n3. Async logic")
        await test_async_logic()
        print("✓ Passed")

        print("\n4. Composition with bootstrap")
        await test_composition_with_bootstrap()
        print("✓ Passed")

        print("\n5. Pure logic testability")
        await test_pure_logic_testability()
        print("✓ Passed")

        print("\n6. Symbiont chain")
        await test_symbiont_chain()
        print("✓ Passed")

        print("\n7. State independence")
        await test_state_independence()
        print("✓ Passed")

        print("\n✓ All Symbiont tests passed!")

    asyncio.run(run_tests())
