"""
Test suite for T-gents Phase 1 implementation.

Tests:
- Type I Nullifiers: MockAgent, FixtureAgent
- Type II Saboteurs: FailingAgent
- Type III Observers: SpyAgent, PredicateAgent
- Composition and categorical properties
"""

import asyncio
from typing import Any

from agents.t import (
    MockAgent,
    MockConfig,
    FixtureAgent,
    FixtureConfig,
    FailingAgent,
    FailingConfig,
    FailureType,
    SpyAgent,
    PredicateAgent,
    not_empty,
    is_positive,
)


async def test_mock_agent():
    """Test MockAgent - constant morphism."""
    print("\n=== Testing MockAgent ===")

    # Create mock agent
    mock = MockAgent[str, dict](MockConfig(output={"status": "ok", "value": 42}))

    # Test: constant morphism property
    result1 = await mock.invoke("input_1")
    result2 = await mock.invoke("input_2")

    assert result1 == {"status": "ok", "value": 42}
    assert result2 == {"status": "ok", "value": 42}
    assert result1 == result2  # Constant property

    # Test: call counting
    assert mock.call_count == 2

    # Test: __is_test__ marker
    assert mock.__is_test__ is True

    print("✓ MockAgent: constant morphism verified")
    print(f"✓ MockAgent: call_count = {mock.call_count}")
    print("✓ MockAgent: __is_test__ = True")


async def test_fixture_agent():
    """Test FixtureAgent - deterministic lookup."""
    print("\n=== Testing FixtureAgent ===")

    # Create fixture agent
    fixtures = {
        "Fix auth bug": "Added OAuth validation",
        "Optimize query": "Added database index",
        "Add tests": "Created test suite",
    }
    fixture = FixtureAgent[str, str](FixtureConfig(fixtures=fixtures))

    # Test: deterministic lookup
    result = await fixture.invoke("Fix auth bug")
    assert result == "Added OAuth validation"

    result = await fixture.invoke("Optimize query")
    assert result == "Added database index"

    # Test: same input always yields same output
    result1 = await fixture.invoke("Add tests")
    result2 = await fixture.invoke("Add tests")
    assert result1 == result2 == "Created test suite"

    # Test: __is_test__ marker
    assert fixture.__is_test__ is True

    # Test: lookup count
    assert fixture.lookup_count == 4

    print("✓ FixtureAgent: deterministic lookup verified")
    print("✓ FixtureAgent: __is_test__ = True")

    # Test: strict mode (missing input)
    try:
        await fixture.invoke("Unknown task")
        assert False, "Should have raised KeyError"
    except KeyError as e:
        print(f"✓ FixtureAgent: strict mode raises KeyError: {e}")


async def test_fixture_agent_default():
    """Test FixtureAgent with default fallback."""
    print("\n=== Testing FixtureAgent (with default) ===")

    fixtures = {"known": "result"}
    fixture = FixtureAgent[str, str](
        FixtureConfig(fixtures=fixtures, default="default_value", strict=False)
    )

    # Test: known input
    result = await fixture.invoke("known")
    assert result == "result"

    # Test: unknown input falls back to default
    result = await fixture.invoke("unknown")
    assert result == "default_value"

    print("✓ FixtureAgent: default fallback works")


async def test_failing_agent():
    """Test FailingAgent - controlled failures."""
    print("\n=== Testing FailingAgent ===")

    # Test: fail N times, then recover
    failing = FailingAgent[str, str](
        FailingConfig(
            error_type=FailureType.NETWORK,
            fail_count=2,
            recovery_token="Success",
        )
    )

    # First two attempts should fail
    for i in range(2):
        try:
            await failing.invoke("test")
            assert False, f"Attempt {i+1} should have failed"
        except Exception as e:
            print(f"✓ FailingAgent: Attempt {i+1} failed as expected: {e}")

    # Third attempt should succeed
    result = await failing.invoke("test")
    assert result == "Success"
    print("✓ FailingAgent: Recovered with recovery_token after fail_count")

    # Test: __is_test__ marker
    assert failing.__is_test__ is True

    # Test: reset
    failing.reset()
    try:
        await failing.invoke("test")
        assert False, "Should fail after reset"
    except Exception:
        print("✓ FailingAgent: reset() works")


async def test_failing_agent_always_fails():
    """Test FailingAgent - always fails."""
    print("\n=== Testing FailingAgent (always fails) ===")

    failing = FailingAgent[str, str](
        FailingConfig(error_type=FailureType.TYPE, fail_count=-1)
    )

    # Should always fail
    for i in range(3):
        try:
            await failing.invoke("test")
            assert False, "Should always fail"
        except Exception:
            pass

    print("✓ FailingAgent: Always fails when fail_count=-1")


async def test_spy_agent():
    """Test SpyAgent - identity with observation."""
    print("\n=== Testing SpyAgent ===")

    spy = SpyAgent[dict](label="TestSpy")

    # Test: identity property
    input1 = {"data": "value1"}
    result1 = await spy.invoke(input1)
    assert result1 == input1  # Identity

    input2 = {"data": "value2"}
    result2 = await spy.invoke(input2)
    assert result2 == input2  # Identity

    # Test: history tracking
    assert len(spy.history) == 2
    assert spy.history[0] == input1
    assert spy.history[1] == input2

    # Test: assertions
    spy.assert_captured(input1)
    spy.assert_count(2)
    spy.assert_not_empty()

    # Test: last()
    assert spy.last() == input2

    # Test: __is_test__ marker
    assert spy.__is_test__ is True

    # Test: reset
    spy.reset()
    assert len(spy.history) == 0
    print("✓ SpyAgent: Identity + observation verified")


async def test_predicate_agent():
    """Test PredicateAgent - runtime validation gate."""
    print("\n=== Testing PredicateAgent ===")

    # Test: predicate that passes
    validator = PredicateAgent[str](not_empty, name="NonEmpty")

    result = await validator.invoke("hello")
    assert result == "hello"  # Passes through
    assert validator.pass_count == 1
    print("✓ PredicateAgent: Passes valid input")

    # Test: predicate that fails
    try:
        await validator.invoke("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert validator.fail_count == 1
        print(f"✓ PredicateAgent: Rejects invalid input: {e}")

    # Test: __is_test__ marker
    assert validator.__is_test__ is True


async def test_predicate_agent_custom():
    """Test PredicateAgent with custom predicate."""
    print("\n=== Testing PredicateAgent (custom) ===")

    def is_even(x: int) -> bool:
        return x % 2 == 0

    gate = PredicateAgent[int](is_even, name="EvenOnly")

    # Should pass even numbers
    result = await gate.invoke(4)
    assert result == 4

    # Should reject odd numbers
    try:
        await gate.invoke(3)
        assert False, "Should reject odd number"
    except ValueError:
        pass

    print("✓ PredicateAgent: Custom predicate works")


async def test_composition():
    """Test T-gent composition."""
    print("\n=== Testing T-gent Composition ===")

    # Create a pipeline: Mock >> Spy >> Predicate
    mock = MockAgent[None, str](MockConfig(output="result"))
    spy = SpyAgent[str](label="Pipeline")
    validator = PredicateAgent[str](not_empty, name="NonEmpty")

    # Compose
    pipeline = mock >> spy >> validator

    # Execute
    result = await pipeline.invoke(None)

    assert result == "result"
    assert len(spy.history) == 1
    assert spy.history[0] == "result"

    print("✓ Composition: Mock >> Spy >> Predicate works")
    print(f"  Pipeline name: {pipeline.name}")


async def test_associativity():
    """Test associativity law: (f >> g) >> h ≡ f >> (g >> h)."""
    print("\n=== Testing Associativity Law ===")

    # Create fresh instances for each pipeline
    mock1 = MockAgent[None, str](MockConfig(output="A"))
    spy1a = SpyAgent[str](label="B1")
    spy1b = SpyAgent[str](label="C1")

    mock2 = MockAgent[None, str](MockConfig(output="A"))
    spy2a = SpyAgent[str](label="B2")
    spy2b = SpyAgent[str](label="C2")

    # Two ways to compose
    pipeline1 = (mock1 >> spy1a) >> spy1b
    pipeline2 = mock2 >> (spy2a >> spy2b)

    # Execute both
    result1 = await pipeline1.invoke(None)
    result2 = await pipeline2.invoke(None)

    # Verify results are the same
    assert result1 == result2 == "A"

    # Verify side effects are equivalent
    assert len(spy1a.history) == len(spy2a.history) == 1
    assert len(spy1b.history) == len(spy2b.history) == 1
    assert spy1a.history[0] == spy2a.history[0] == "A"
    assert spy1b.history[0] == spy2b.history[0] == "A"

    print("✓ Associativity: (f >> g) >> h ≡ f >> (g >> h)")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("T-gents Phase 1 Test Suite")
    print("=" * 60)

    await test_mock_agent()
    await test_fixture_agent()
    await test_fixture_agent_default()
    await test_failing_agent()
    await test_failing_agent_always_fails()
    await test_spy_agent()
    await test_predicate_agent()
    await test_predicate_agent_custom()
    await test_composition()
    await test_associativity()

    print("\n" + "=" * 60)
    print("✅ All T-gents Phase 1 tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
