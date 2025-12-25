"""
Tests for Bootstrap Witness.

Minimal tests for law verification.
"""

import pytest

from agents.o import (
    BootstrapWitness,
    IdentityAgent,
    TestAgent,
    Verdict,
)


@pytest.mark.asyncio
async def test_bootstrap_witness_verification():
    """Test that BootstrapWitness runs verification."""
    witness = BootstrapWitness(test_iterations=3)

    result = await witness.invoke()

    # Should have checked all agents
    assert len(result.agent_results) == 7

    # Should have run law verification
    assert result.identity_result is not None
    assert result.composition_result is not None
    assert result.identity_result.test_cases_run == 3
    assert result.composition_result.test_cases_run == 3


@pytest.mark.asyncio
async def test_identity_agent():
    """Test that IdentityAgent returns its input."""
    id_agent = IdentityAgent[int]()

    result = await id_agent.invoke(42)
    assert result == 42


@pytest.mark.asyncio
async def test_test_agent():
    """Test that TestAgent applies its transform."""
    agent = TestAgent[int, int]("doubler", lambda x: x * 2)

    result = await agent.invoke(21)
    assert result == 42
