"""
The Accursed Share: Chaos and exploratory tests.

Philosophy: We cherish and express gratitude for slop.
10% of test budget goes to unpredictable exploration.

This demonstrates Phase 5 of the test evolution plan.
These tests are designed to discover unexpected behaviors.
"""

import pytest
import random
from pathlib import Path
from tempfile import TemporaryDirectory

from testing.accursed_share import (
    Discovery,
    DiscoveryLog,
    generate_weird_inputs,
)


class TestDiscoveryLog:
    """Tests for the discovery log system."""

    @pytest.fixture
    def temp_log(self):
        """Create a temporary discovery log."""
        with TemporaryDirectory() as tmpdir:
            yield DiscoveryLog(Path(tmpdir) / "discoveries.json")

    def test_record_discovery(self, temp_log):
        """Test recording a discovery."""
        discovery = Discovery(
            test_name="test_example",
            discovery_type="boundary_case",
            description="Empty string handling",
        )
        temp_log.record(discovery)

        assert len(temp_log.discoveries) == 1
        assert temp_log.discoveries[0].test_name == "test_example"

    def test_composition_success_recording(self, temp_log):
        """Test recording a composition success."""
        discovery = temp_log.record_composition_success(
            test_name="test_compose",
            agents=["AgentA", "AgentB", "AgentC"],
            input_val=42,
            output_val=84,
        )

        assert discovery.discovery_type == "composition_success"
        assert "AgentA >> AgentB >> AgentC" in discovery.description

    def test_boundary_case_recording(self, temp_log):
        """Test recording a boundary case."""
        discovery = temp_log.record_boundary_case(
            test_name="test_boundary",
            description="Large input",
            input_val="a" * 10000,
            behavior="Handled gracefully",
        )

        assert discovery.discovery_type == "boundary_case"
        assert discovery.actionable is True

    def test_persistence(self, temp_log):
        """Test that discoveries persist across instances."""
        temp_log.record(
            Discovery(
                test_name="test_persist",
                discovery_type="unexpected_behavior",
                description="Test persistence",
            )
        )

        # Create new log at same path
        new_log = DiscoveryLog(temp_log.log_path)

        assert len(new_log.discoveries) == 1
        assert new_log.discoveries[0].test_name == "test_persist"

    def test_get_actionable(self, temp_log):
        """Test filtering actionable discoveries."""
        temp_log.record(
            Discovery(
                test_name="actionable",
                discovery_type="boundary_case",
                description="Actionable",
                actionable=True,
            )
        )
        temp_log.record(
            Discovery(
                test_name="not_actionable",
                discovery_type="composition_success",
                description="Not actionable",
                actionable=False,
            )
        )

        actionable = temp_log.get_actionable()
        assert len(actionable) == 1
        assert actionable[0].test_name == "actionable"

    def test_summary(self, temp_log):
        """Test summary statistics."""
        temp_log.record(
            Discovery(
                test_name="a",
                discovery_type="boundary_case",
                description="A",
                actionable=True,
            )
        )
        temp_log.record(
            Discovery(
                test_name="b",
                discovery_type="composition_success",
                description="B",
            )
        )
        temp_log.record(
            Discovery(
                test_name="c",
                discovery_type="boundary_case",
                description="C",
            )
        )

        summary = temp_log.summary()
        assert summary["total"] == 3
        assert summary["actionable"] == 1
        assert summary["by_type"]["boundary_case"] == 2
        assert summary["by_type"]["composition_success"] == 1


class TestWeirdInputs:
    """Tests using weird inputs for boundary exploration."""

    def test_weird_inputs_not_empty(self):
        """Verify weird inputs generator works."""
        inputs = generate_weird_inputs()
        assert len(inputs) > 0

    @pytest.mark.accursed_share
    @pytest.mark.asyncio
    async def test_id_handles_weird_inputs(self):
        """
        Test that ID agent handles weird inputs.

        This is a chaos test - we're exploring, not asserting.
        """
        from bootstrap import ID

        inputs = generate_weird_inputs()
        handled = 0
        failed = 0

        for inp in inputs:
            try:
                await ID.invoke(inp)
                # ID should return input unchanged
                # (but comparison might fail for some types)
                handled += 1
            except Exception as e:
                failed += 1
                print(f"ID failed on {type(inp).__name__}: {e}")

        # Just report, don't assert
        print(f"Handled: {handled}/{len(inputs)}, Failed: {failed}")


@pytest.mark.accursed_share
class TestChaoticComposition:
    """Chaotic composition tests for discovery."""

    @pytest.mark.asyncio
    async def test_random_agent_composition(self):
        """
        Pick random agents, compose, observe.

        This test doesn't assert - it discovers.
        """
        from agents.o.bootstrap_witness import TestAgent
        from functools import reduce
        from bootstrap import compose

        # Create a pool of test agents
        agent_pool = [TestAgent(f"add_{i}", lambda x, i=i: x + i) for i in range(5)] + [
            TestAgent(f"mul_{i}", lambda x, i=i: x * (i + 1)) for i in range(3)
        ]

        # Random selection
        n_agents = random.randint(2, 5)
        selected = random.sample(agent_pool, n_agents)

        try:
            composed = reduce(compose, selected)
            result = await composed.invoke(1)

            names = [a.name for a in selected]
            print(f"SUCCESS: {' >> '.join(names)} on 1 = {result}")

        except Exception as e:
            names = [a.name for a in selected]
            print(f"FAILURE: {' >> '.join(names)}: {e}")

    @pytest.mark.asyncio
    async def test_deep_composition_chain(self):
        """Test very deep composition chains."""
        from bootstrap import compose, ID
        from functools import reduce

        # Chain 100 identity agents
        agents = [ID for _ in range(100)]

        deep_chain = reduce(compose, agents)

        result = await deep_chain.invoke(42)
        assert result == 42, f"Deep chain changed value: {result}"

        print("Deep chain (n=100) succeeded")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_composition(self):
        """Test concurrent agent invocations."""
        import asyncio
        from agents.o.bootstrap_witness import TestAgent

        agent = TestAgent("counter", lambda x: x + 1)

        # Many concurrent invocations
        tasks = [agent.invoke(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 100
        print("Concurrent invocations: 100/100 succeeded")


@pytest.mark.accursed_share
class TestSerendipitousDiscovery:
    """Tests designed for serendipitous discoveries."""

    @pytest.mark.asyncio
    async def test_type_coercion_chain(self):
        """
        Test chains with type-changing transforms.

        Discovers how composition handles type changes.
        """
        from agents.o.bootstrap_witness import TestAgent
        from bootstrap import compose

        # int -> str -> list -> dict
        to_str = TestAgent("to_str", lambda x: str(x))
        to_list = TestAgent("to_list", lambda x: [x])
        to_dict = TestAgent("to_dict", lambda x: {"value": x})

        chain = compose(compose(to_str, to_list), to_dict)

        result = await chain.invoke(42)

        # Document the discovery
        print(f"Type chain: 42 -> {result}")
        assert result == {"value": ["42"]}

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """
        Test how errors propagate through composition.

        Discovers error handling behavior.
        """
        from agents.o.bootstrap_witness import TestAgent
        from bootstrap import compose

        def failing_transform(x):
            if x == 0:
                raise ValueError("Cannot handle zero")
            return x * 2

        safe = TestAgent("safe", lambda x: x + 1)
        risky = TestAgent("risky", failing_transform)

        # Safe before risky: 0 -> 1 -> 2 (succeeds)
        chain1 = compose(safe, risky)
        result1 = await chain1.invoke(0)
        print(f"safe >> risky on 0: {result1}")
        assert result1 == 2

        # Risky before safe: 0 -> error
        chain2 = compose(risky, safe)
        try:
            await chain2.invoke(0)
            print("risky >> safe on 0: succeeded (unexpected)")
        except ValueError as e:
            print(f"risky >> safe on 0: {e} (expected)")
