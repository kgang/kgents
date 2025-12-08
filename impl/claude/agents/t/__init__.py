"""
T-gents: Test Agents for kgents

Category Theory-based testing agents for verification, perturbation, and observation.

Philosophy:
- Testing is algebraic verification, not just examples
- T-gents prove categorical properties: associativity, identity, resilience
- All T-gents marked with __is_test__ = True
- Composable with other agents via >> operator

Phase 1 T-gents (Implemented):

Type I - Nullifiers (Constants & Fixtures):
- MockAgent: Constant morphism c_b: A → b
- FixtureAgent: Deterministic lookup f: A → B

Type II - Saboteurs (Chaos & Perturbation):
- FailingAgent: Bottom morphism ⊥: A → Error

Type III - Observers (Identity with Side Effects):
- SpyAgent: Writer Monad S: A → (A, [A])
- PredicateAgent: Gate P: A → A ∪ {⊥}

Usage:
    from agents.t import MockAgent, FailingAgent, SpyAgent

    # Mock expensive operations
    mock = MockAgent(MockConfig(output="result"))

    # Test retry logic
    failing = FailingAgent(FailingConfig(
        error_type=FailureType.NETWORK,
        fail_count=2,
        recovery_token="Success"
    ))

    # Observe pipeline data
    spy = SpyAgent(label="Hypotheses")
    pipeline = generate >> spy >> validate
"""

from .failing import (
    FailingAgent,
    FailingConfig,
    FailureType,
    failing_agent,
    syntax_failing,
    import_failing,
)

from .mock import (
    MockAgent,
    MockConfig,
    mock_agent,
)

from .fixture import (
    FixtureAgent,
    FixtureConfig,
    fixture_agent,
)

from .spy import (
    SpyAgent,
    spy_agent,
)

from .predicate import (
    PredicateAgent,
    predicate_agent,
    not_none,
    not_empty,
    is_positive,
    is_non_negative,
)

__all__ = [
    # Type I - Nullifiers
    "MockAgent",
    "MockConfig",
    "mock_agent",
    "FixtureAgent",
    "FixtureConfig",
    "fixture_agent",
    # Type II - Saboteurs
    "FailingAgent",
    "FailingConfig",
    "FailureType",
    "failing_agent",
    "syntax_failing",
    "import_failing",
    # Type III - Observers
    "SpyAgent",
    "spy_agent",
    "PredicateAgent",
    "predicate_agent",
    # Predicate helpers
    "not_none",
    "not_empty",
    "is_positive",
    "is_non_negative",
]
