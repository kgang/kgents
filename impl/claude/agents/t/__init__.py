"""
T-gents: Test Agents for kgents

Lightweight testing utilities and mock agents for development and testing.

Philosophy:
- Test-gents are agents designed explicitly for testing other agents
- They follow the same morphism principles (A → B types)
- They can simulate failures, delays, edge cases
- Composable with other agents via >> operator

Core T-gents:
- FailingAgent: Always fails with configurable error types
- MockAgent: Returns configurable mock outputs
- DelayAgent: Adds artificial delays for testing async behavior
- CounterAgent: Tracks invocation counts for verification

Usage:
    from agents.t import FailingAgent, MockAgent

    # Test retry logic
    failing = FailingAgent(error_type="type", fail_count=2)
    result = await failing.invoke(test_input)

    # Mock responses
    mock = MockAgent(output={"status": "ok"})
    result = await mock.invoke(anything)
"""

from .failing import (
    FailingAgent,
    FailingConfig,
    FailureType,
    failing_agent,
)

from .mock import (
    MockAgent,
    MockConfig,
    mock_agent,
)

__all__ = [
    "FailingAgent",
    "FailingConfig",
    "FailureType",
    "failing_agent",
    "MockAgent",
    "MockConfig",
    "mock_agent",
]
