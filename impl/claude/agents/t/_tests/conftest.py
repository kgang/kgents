"""
Shared pytest fixtures for TruthFunctor test suite.

Provides common fixtures for testing probes:
- Mock agents for testing probe behavior
- Sample probe states and actions
- Helper functions for verification
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from agents.t.probes.null_probe import NullConfig, NullProbe
from agents.t.truth_functor import (
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthVerdict,
)

# =============================================================================
# Mock Agents for Testing
# =============================================================================


@pytest.fixture
def identity_agent() -> Callable[[Any], Any]:
    """
    Identity agent: returns input unchanged.

    Useful for testing probes in isolation without agent complexity.
    """

    def agent(input: Any) -> Any:
        return input

    return agent


@pytest.fixture
def constant_agent() -> Callable[[Any], str]:
    """
    Constant agent: always returns "constant".

    Useful for predictable agent behavior in probe tests.
    """

    def agent(input: Any) -> str:
        return "constant"

    return agent


@pytest.fixture
def doubling_agent() -> Callable[[int], int]:
    """
    Doubling agent: returns input * 2.

    Useful for testing probe behavior with transformations.
    """

    def agent(input: int) -> int:
        return input * 2

    return agent


@pytest.fixture
async def async_identity_agent() -> Callable[[Any], Any]:
    """
    Async identity agent: async version of identity.

    Useful for testing async probe invocations.
    """

    async def agent(input: Any) -> Any:
        return input

    return agent


# =============================================================================
# Sample Probe States
# =============================================================================


@pytest.fixture
def initial_probe_state() -> ProbeState:
    """
    Initial probe state: ready to start verification.
    """
    return ProbeState(
        phase="init",
        observations=(),
        laws_verified=frozenset(),
        compression_ratio=1.0,
    )


@pytest.fixture
def testing_probe_state() -> ProbeState:
    """
    Probe state during testing phase with some observations.
    """
    return ProbeState(
        phase="testing",
        observations=("obs1", "obs2"),
        laws_verified=frozenset({"identity"}),
        compression_ratio=0.95,
    )


@pytest.fixture
def complete_probe_state() -> ProbeState:
    """
    Complete probe state with all laws verified.
    """
    return ProbeState(
        phase="complete",
        observations=("obs1", "obs2", "obs3"),
        laws_verified=frozenset({"identity", "associativity", "composability"}),
        compression_ratio=0.85,
    )


# =============================================================================
# Sample Probe Actions
# =============================================================================


@pytest.fixture
def invoke_action() -> ProbeAction:
    """Standard invoke action."""
    return ProbeAction("invoke")


@pytest.fixture
def test_identity_action() -> ProbeAction:
    """Action for testing identity law."""
    return ProbeAction("test_identity")


@pytest.fixture
def test_associativity_action() -> ProbeAction:
    """Action for testing associativity law."""
    return ProbeAction("test_associativity", parameters=("f", "g", "h"))


# =============================================================================
# Sample Constitutional Scores
# =============================================================================


@pytest.fixture
def perfect_score() -> ConstitutionalScore:
    """Perfect score: all principles at 1.0."""
    return ConstitutionalScore(
        tasteful=1.0,
        curated=1.0,
        ethical=1.0,
        joy_inducing=1.0,
        composable=1.0,
        heterarchical=1.0,
        generative=1.0,
    )


@pytest.fixture
def ethical_score() -> ConstitutionalScore:
    """Score emphasizing ethical principle."""
    return ConstitutionalScore(
        ethical=1.0,
        composable=0.5,
    )


@pytest.fixture
def zero_score() -> ConstitutionalScore:
    """Zero score: no principles satisfied."""
    return ConstitutionalScore()


# =============================================================================
# Sample Trace Entries
# =============================================================================


@pytest.fixture
def sample_trace_entry(
    initial_probe_state: ProbeState,
    testing_probe_state: ProbeState,
    invoke_action: ProbeAction,
    ethical_score: ConstitutionalScore,
) -> TraceEntry:
    """
    Sample trace entry: init → testing via invoke.
    """
    return TraceEntry(
        state_before=initial_probe_state,
        action=invoke_action,
        state_after=testing_probe_state,
        reward=ethical_score,
        reasoning="Transitioned to testing phase",
    )


# =============================================================================
# Sample Policy Traces
# =============================================================================


@pytest.fixture
def empty_policy_trace() -> PolicyTrace[TruthVerdict[str]]:
    """
    Empty policy trace with just a verdict, no entries.
    """
    verdict = TruthVerdict(
        value="test",
        passed=True,
        confidence=1.0,
        reasoning="No verification needed",
    )
    return PolicyTrace(value=verdict, entries=[])


@pytest.fixture
def single_entry_trace(
    sample_trace_entry: TraceEntry,
) -> PolicyTrace[TruthVerdict[str]]:
    """
    Policy trace with one entry.
    """
    verdict = TruthVerdict(
        value="test",
        passed=True,
        confidence=0.9,
        reasoning="Single step verification",
    )
    trace = PolicyTrace(value=verdict, entries=[])
    trace.append(sample_trace_entry)
    return trace


# =============================================================================
# Sample Probes
# =============================================================================


@pytest.fixture
def null_probe_42() -> NullProbe:
    """
    NullProbe that always returns 42.
    """
    return NullProbe(NullConfig(output=42, delay_ms=0))


@pytest.fixture
def null_probe_string() -> NullProbe:
    """
    NullProbe that always returns "constant".
    """
    return NullProbe(NullConfig(output="constant", delay_ms=0))


@pytest.fixture
def null_probe_none() -> NullProbe:
    """
    NullProbe that always returns None.
    """
    return NullProbe(NullConfig(output=None, delay_ms=0))


@pytest.fixture
def null_probe_slow() -> NullProbe:
    """
    NullProbe with 50ms delay.
    """
    return NullProbe(NullConfig(output="slow", delay_ms=50))


# =============================================================================
# Helper Functions
# =============================================================================


@pytest.fixture
def assert_valid_trace():
    """
    Helper to assert a PolicyTrace is valid.
    """

    def validator(trace: PolicyTrace[Any]) -> None:
        """Validate that trace has required properties."""
        assert trace.value is not None, "Trace must have a value"
        assert isinstance(trace.entries, list), "Trace entries must be a list"
        assert all(isinstance(e, TraceEntry) for e in trace.entries), (
            "All entries must be TraceEntry instances"
        )

        # Check that entries form a valid chain
        for i in range(len(trace.entries) - 1):
            current = trace.entries[i]
            next_entry = trace.entries[i + 1]
            # Could add more chain validation here if needed

    return validator


@pytest.fixture
def assert_constitutional_score_valid():
    """
    Helper to assert a ConstitutionalScore is valid.
    """

    def validator(score: ConstitutionalScore) -> None:
        """Validate that score has valid ranges."""
        # All scores should be >= 0
        assert score.tasteful >= 0, "tasteful score must be non-negative"
        assert score.curated >= 0, "curated score must be non-negative"
        assert score.ethical >= 0, "ethical score must be non-negative"
        assert score.joy_inducing >= 0, "joy_inducing score must be non-negative"
        assert score.composable >= 0, "composable score must be non-negative"
        assert score.heterarchical >= 0, "heterarchical score must be non-negative"
        assert score.generative >= 0, "generative score must be non-negative"

        # Weighted total should be in [0, 1] for normalized scores
        # (though scores can be > 1.0 individually, weighted_total normalizes)
        assert 0 <= score.weighted_total, "weighted_total must be non-negative"

    return validator


@pytest.fixture
def measure_probe_performance():
    """
    Helper to measure probe execution performance.
    """
    import time

    async def measure(probe: Any, agent: Callable, input: Any) -> tuple[Any, float]:
        """
        Execute probe and measure elapsed time.

        Returns:
            Tuple of (result, elapsed_seconds)
        """
        start = time.time()
        result = await probe.verify(agent, input)
        elapsed = time.time() - start
        return result, elapsed

    return measure


# =============================================================================
# Pytest Configuration
# =============================================================================


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "property: marks tests as property-based tests")
