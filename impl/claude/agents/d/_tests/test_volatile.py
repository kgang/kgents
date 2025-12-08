"""
Unit tests for VolatileAgent.

Tests cover:
- Protocol compliance (DataAgent interface)
- Round-trip integrity (isomorphism)
- Isolation (deep copy semantics)
- History ordering and limits
"""

import pytest
from agents.d import VolatileAgent


@pytest.mark.asyncio
async def test_round_trip():
    """State survives save/load cycle without corruption."""
    dgent = VolatileAgent[dict](_state={"initial": "state"})

    test_state = {"value": 42, "nested": {"key": "data"}}
    await dgent.save(test_state)

    loaded = await dgent.load()
    assert loaded == test_state
    assert loaded == {"value": 42, "nested": {"key": "data"}}


@pytest.mark.asyncio
async def test_isolation():
    """Loaded state is independent copy, not reference."""
    dgent = VolatileAgent[dict](_state={"value": 1})

    # Load and mutate
    state1 = await dgent.load()
    state1["value"] = 2
    state1["new_key"] = "added"

    # Load again - should be unaffected
    state2 = await dgent.load()
    assert state2["value"] == 1
    assert "new_key" not in state2


@pytest.mark.asyncio
async def test_history_ordering():
    """History returns states newest-first, excluding current."""
    dgent = VolatileAgent[int](_state=0)

    await dgent.save(1)
    await dgent.save(2)
    await dgent.save(3)

    history = await dgent.history(limit=5)
    # Current state is 3, history should be [2, 1, 0] (newest first)
    assert history == [2, 1, 0]


@pytest.mark.asyncio
async def test_history_limit():
    """History respects limit parameter."""
    dgent = VolatileAgent[int](_state=0)

    await dgent.save(1)
    await dgent.save(2)
    await dgent.save(3)
    await dgent.save(4)
    await dgent.save(5)

    # Request only last 2 historical states
    history = await dgent.history(limit=2)
    assert len(history) == 2
    assert history == [4, 3]  # Newest 2 (excluding current 5)


@pytest.mark.asyncio
async def test_bounded_history():
    """History is bounded to prevent unbounded growth."""
    dgent = VolatileAgent[int](_state=0, _max_history=3)

    # Save many states
    for i in range(1, 10):
        await dgent.save(i)

    # History should only contain last 3
    history = await dgent.history()
    assert len(history) == 3
    assert history == [8, 7, 6]  # Current is 9, history keeps [8,7,6]


@pytest.mark.asyncio
async def test_snapshot_non_async():
    """Snapshot provides non-async access for testing."""
    dgent = VolatileAgent[str](_state="initial")

    await dgent.save("updated")

    # Snapshot doesn't require await
    current = dgent.snapshot()
    assert current == "updated"


@pytest.mark.asyncio
async def test_complex_state():
    """Works with complex nested structures."""
    dgent = VolatileAgent[dict](_state={})

    complex_state = {
        "users": {"alice": {"age": 30}, "bob": {"age": 25}},
        "sessions": [{"id": 1, "active": True}, {"id": 2, "active": False}],
        "metadata": {"version": "1.0", "timestamp": 123456789},
    }

    await dgent.save(complex_state)
    loaded = await dgent.load()

    assert loaded == complex_state
    assert loaded["users"]["alice"]["age"] == 30

    # Mutate loaded copy
    loaded["users"]["alice"]["age"] = 31

    # Original should be unchanged
    loaded2 = await dgent.load()
    assert loaded2["users"]["alice"]["age"] == 30


@pytest.mark.asyncio
async def test_dataclass_state():
    """Works with dataclass state types."""
    from dataclasses import dataclass

    @dataclass
    class UserProfile:
        name: str
        age: int

    initial = UserProfile(name="Alice", age=30)
    dgent = VolatileAgent[UserProfile](_state=initial)

    # Update
    updated = UserProfile(name="Alice", age=31)
    await dgent.save(updated)

    loaded = await dgent.load()
    assert loaded.name == "Alice"
    assert loaded.age == 31

    # History contains initial
    history = await dgent.history()
    assert len(history) == 1
    assert history[0].age == 30


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        """Run all tests manually."""
        print("Running VolatileAgent tests...")

        print("\n1. Round-trip test")
        await test_round_trip()
        print("✓ Passed")

        print("\n2. Isolation test")
        await test_isolation()
        print("✓ Passed")

        print("\n3. History ordering test")
        await test_history_ordering()
        print("✓ Passed")

        print("\n4. History limit test")
        await test_history_limit()
        print("✓ Passed")

        print("\n5. Bounded history test")
        await test_bounded_history()
        print("✓ Passed")

        print("\n6. Snapshot test")
        await test_snapshot_non_async()
        print("✓ Passed")

        print("\n7. Complex state test")
        await test_complex_state()
        print("✓ Passed")

        print("\n8. Dataclass state test")
        await test_dataclass_state()
        print("✓ Passed")

        print("\n✓ All VolatileAgent tests passed!")

    asyncio.run(run_tests())
