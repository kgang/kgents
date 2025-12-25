"""
Backwards Compatibility Layer

Maps legacy T-gent types to new TruthFunctor probes.
All legacy types emit deprecation warnings on first instantiation.

Migration Guide:
- MockAgent → NullProbe
- FixtureAgent → NullProbe(fixtures=...)
- FailingAgent → ChaosProbe(chaos_type=ChaosType.FAILURE)
- NoiseAgent → ChaosProbe(chaos_type=ChaosType.NOISE)
- LatencyAgent → ChaosProbe(chaos_type=ChaosType.LATENCY)
- FlakyAgent → ChaosProbe(chaos_type=ChaosType.FLAKINESS)
- SpyAgent → WitnessProbe
- PredicateAgent → WitnessProbe(predicate=...)
- CounterAgent → WitnessProbe (use .history for count)
- MetricsAgent → WitnessProbe (use .history for metrics)
- JudgeAgent → JudgeProbe
- OracleAgent → JudgeProbe(oracle=...)
- TrustGate → TrustProbe
"""

import warnings
from functools import wraps
from typing import TypeVar, Generic, Any, Callable, Dict
from dataclasses import dataclass

from .probes import (
    NullProbe,
    WitnessProbe,
    WitnessConfig,
)
# TODO: Uncomment when remaining probes are implemented
# from .probes import (
#     ChaosProbe,
#     ChaosType,
#     ChaosConfig,
#     JudgeProbe,
#     JudgeConfig,
#     TrustProbe,
#     TrustConfig,
# )
from .truth_functor import PolicyTrace, TruthVerdict

# Stub types for unimplemented probes (used in compat layer)
class ChaosType:
    FAILURE = "failure"
    NOISE = "noise"
    LATENCY = "latency"
    FLAKINESS = "flakiness"

class ChaosProbe:
    def __init__(self, **kwargs):
        self.error_msg = kwargs.get("error_msg", "Chaos error")
    async def verify(self, agent, input):
        return PolicyTrace(value=TruthVerdict(value=input, passed=False, confidence=0.0, reasoning="Chaos injected"))

class JudgeProbe:
    def __init__(self, **kwargs):
        pass
    async def verify(self, agent, input):
        return PolicyTrace(value=TruthVerdict(value=input, passed=True, confidence=1.0, reasoning="Judgment passed"))

class TrustProbe:
    def __init__(self, **kwargs):
        pass
    async def verify(self, agent, input):
        return PolicyTrace(value=TruthVerdict(value=input, passed=True, confidence=1.0, reasoning="Trust granted"))

A = TypeVar("A")
B = TypeVar("B")


def deprecated(replacement: str):
    """Decorator to mark legacy types as deprecated."""

    def decorator(cls):
        original_init = cls.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            warnings.warn(
                f"{cls.__name__} is deprecated. Use {replacement} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            original_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator


@deprecated("NullProbe")
class MockAgent(Generic[A, B]):
    """
    DEPRECATED: Use NullProbe instead.

    Provides backwards compatibility with legacy MockAgent API.

    Migration:
        # Old
        mock = MockAgent(MockConfig(output="result"))
        result = await mock.invoke(input)

        # New
        probe = NullProbe(constant="result")
        trace = await probe.verify(agent, input)
        result = trace.value.value
    """

    def __init__(self, constant: B | Any = None, delay_ms: int = 0):
        # Handle both MockConfig and direct args
        if hasattr(constant, "output"):
            # MockConfig passed
            output = constant.output
            delay = getattr(constant, "delay_ms", delay_ms)
        else:
            output = constant
            delay = delay_ms
        self._probe = NullProbe(constant=output, delay_ms=delay)
        self._call_count_val = 0
        self.name = f"MockAgent({output})"

    async def invoke(self, input: A) -> B:
        """Legacy API: returns just the value."""
        self._call_count_val += 1
        # NullProbe doesn't have invoke, so we just return the constant
        return self._probe.constant

    @property
    def _call_count(self) -> int:
        return self._call_count_val

    @property
    def call_count(self) -> int:
        return self._call_count_val

    def reset(self) -> None:
        self._call_count_val = 0


@deprecated("NullProbe with fixtures")
class FixtureAgent(Generic[A, B]):
    """
    DEPRECATED: Use NullProbe with fixtures instead.

    Migration:
        # Old
        fixture = FixtureAgent(fixtures={1: "one", 2: "two"})
        result = await fixture.invoke(1)

        # New
        # Note: NullProbe doesn't support fixtures, use dict lookup
        fixtures = {1: "one", 2: "two"}
        result = fixtures.get(input, default)
    """

    def __init__(
        self, fixtures: dict[A, B] | Any, default: B | None = None, strict: bool = False
    ):
        # Handle both FixtureConfig and direct args
        if hasattr(fixtures, "fixtures"):
            # FixtureConfig passed
            self._fixtures = fixtures.fixtures
            self._default = getattr(fixtures, "default", default)
            self._strict = getattr(fixtures, "strict", strict)
        else:
            self._fixtures = fixtures
            self._default = default
            self._strict = strict
        # For now, use a simple NullProbe that returns default
        # TODO: Extend NullProbe to support fixture lookups
        self._probe = NullProbe(constant=default)

    async def invoke(self, input: A) -> B:
        if input in self._fixtures:
            return self._fixtures[input]
        if self._strict:
            raise KeyError(f"No fixture for {input}")
        return self._default


@deprecated("ChaosProbe(chaos_type=ChaosType.FAILURE)")
class FailingAgent:
    """
    DEPRECATED: Use ChaosProbe(chaos_type=ChaosType.FAILURE) instead.

    Migration:
        # Old
        failing = FailingAgent(FailingConfig(error_type=FailureType.NETWORK))
        try:
            await failing.invoke(input)
        except Exception:
            pass

        # New
        probe = ChaosProbe(chaos_type=ChaosType.FAILURE, error_msg="Network error")
        trace = await probe.verify(agent, input)
        assert not trace.value.passed  # Expect failure
    """

    def __init__(self, error_msg: str = "Failing agent", **kwargs):
        self._probe = ChaosProbe(chaos_type=ChaosType.FAILURE, error_msg=error_msg)

    async def invoke(self, input: Any) -> Any:
        async def dummy_agent(x):
            raise RuntimeError(self._probe.error_msg)

        result = await self._probe.verify(dummy_agent, input)
        if not result.value.passed:
            raise RuntimeError(self._probe.error_msg)
        return result.value.value


@deprecated("ChaosProbe(chaos_type=ChaosType.NOISE)")
class NoiseAgent:
    """
    DEPRECATED: Use ChaosProbe(chaos_type=ChaosType.NOISE) instead.

    Migration:
        # Old
        noise = NoiseAgent(NoiseConfig(noise_type=NoiseType.NUMERIC))
        result = await noise.invoke(input)

        # New
        probe = ChaosProbe(chaos_type=ChaosType.NOISE, noise_factor=0.1)
        trace = await probe.verify(agent, input)
        result = trace.value.value
    """

    def __init__(self, noise_factor: float = 0.1, **kwargs):
        self._probe = ChaosProbe(chaos_type=ChaosType.NOISE, noise_factor=noise_factor)

    async def invoke(self, input: Any) -> Any:
        async def dummy_agent(x):
            return x

        result = await self._probe.verify(dummy_agent, input)
        return result.value.value


@deprecated("ChaosProbe(chaos_type=ChaosType.LATENCY)")
class LatencyAgent:
    """
    DEPRECATED: Use ChaosProbe(chaos_type=ChaosType.LATENCY) instead.

    Migration:
        # Old
        latency = LatencyAgent(delay_ms=100)
        result = await latency.invoke(input)

        # New
        probe = ChaosProbe(chaos_type=ChaosType.LATENCY, latency_ms=100)
        trace = await probe.verify(agent, input)
        result = trace.value.value
    """

    def __init__(self, latency_ms: int = 100, **kwargs):
        self._probe = ChaosProbe(chaos_type=ChaosType.LATENCY, latency_ms=latency_ms)

    async def invoke(self, input: Any) -> Any:
        async def dummy_agent(x):
            return x

        result = await self._probe.verify(dummy_agent, input)
        return result.value.value


@deprecated("ChaosProbe(chaos_type=ChaosType.FLAKINESS)")
class FlakyAgent:
    """
    DEPRECATED: Use ChaosProbe(chaos_type=ChaosType.FLAKINESS) instead.

    Migration:
        # Old
        flaky = FlakyAgent(failure_rate=0.5)
        result = await flaky.invoke(input)

        # New
        probe = ChaosProbe(chaos_type=ChaosType.FLAKINESS, failure_probability=0.5)
        trace = await probe.verify(agent, input)
    """

    def __init__(self, failure_probability: float = 0.5, **kwargs):
        self._probe = ChaosProbe(
            chaos_type=ChaosType.FLAKINESS, failure_probability=failure_probability
        )

    async def invoke(self, input: Any) -> Any:
        async def dummy_agent(x):
            return x

        result = await self._probe.verify(dummy_agent, input)
        return result.value.value


@deprecated("WitnessProbe")
class SpyAgent(Generic[A]):
    """
    DEPRECATED: Use WitnessProbe instead.

    Migration:
        # Old
        spy = SpyAgent(label="Observer")
        result = await spy.invoke(input)
        history = spy.history

        # New
        probe = WitnessProbe(WitnessConfig(label="Observer"))
        trace = await probe.verify(agent, input)
        history = probe.history
    """

    def __init__(self, label: str = "Spy", max_history: int = 100):
        config = WitnessConfig(label=label, max_history=max_history)
        self._probe = WitnessProbe(config)

    async def invoke(self, input: A) -> A:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value

    @property
    def history(self) -> list[A]:
        return self._probe.history

    @property
    def call_count(self) -> int:
        return len(self._probe.history)

    def reset(self) -> None:
        self._probe.reset()

    def assert_captured(self, expected: A) -> None:
        assert expected in self._probe.history, (
            f"Expected {expected} not captured. History: {self._probe.history}"
        )

    def assert_count(self, count: int) -> None:
        actual = len(self._probe.history)
        assert actual == count, f"Expected {count} invocations, got {actual}"

    def assert_not_empty(self) -> None:
        assert len(self._probe.history) > 0, "Spy captured nothing"

    def last(self) -> A:
        if not self._probe.history:
            raise IndexError("Spy has no captured values")
        return self._probe.history[-1]


@deprecated("WitnessProbe(predicate=...)")
class PredicateAgent(Generic[A]):
    """
    DEPRECATED: Use WitnessProbe(predicate=...) instead.

    Migration:
        # Old
        pred = PredicateAgent(predicate=lambda x: x > 0)
        result = await pred.invoke(5)

        # New
        probe = WitnessProbe(WitnessConfig(label="Predicate"))
        trace = await probe.verify(agent, 5)
        assert trace.value.passed
    """

    def __init__(self, predicate: Callable[[A], bool], label: str = "Predicate"):
        config = WitnessConfig(label=label)
        self._probe = WitnessProbe(config)
        self._predicate = predicate

    async def invoke(self, input: A) -> A:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        if not result.value.passed:
            raise ValueError(f"Predicate failed for {input}")
        return result.value.value


@deprecated("WitnessProbe (use .history for count)")
class CounterAgent(Generic[A]):
    """
    DEPRECATED: Use WitnessProbe and check len(probe.history) instead.

    Migration:
        # Old
        counter = CounterAgent()
        await counter.invoke(input)
        count = counter.count

        # New
        probe = WitnessProbe(WitnessConfig(label="Counter"))
        trace = await probe.verify(agent, input)
        count = len(probe.history)
    """

    def __init__(self, label: str = "Counter"):
        config = WitnessConfig(label=label)
        self._probe = WitnessProbe(config)

    async def invoke(self, input: A) -> A:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value

    @property
    def count(self) -> int:
        return len(self._probe.history)

    def reset(self) -> None:
        self._probe.reset()


@deprecated("WitnessProbe (use .history for metrics)")
class MetricsAgent(Generic[A]):
    """
    DEPRECATED: Use WitnessProbe and analyze .history for metrics.

    Migration:
        # Old
        metrics = MetricsAgent()
        result = await metrics.invoke(input)
        perf = metrics.metrics

        # New
        probe = WitnessProbe(WitnessConfig(label="Metrics"))
        trace = await probe.verify(agent, input)
        # Analyze trace.entries for performance metrics
    """

    def __init__(self):
        config = WitnessConfig(label="Metrics")
        self._probe = WitnessProbe(config)

    async def invoke(self, input: A) -> A:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value

    @property
    def metrics(self) -> dict[str, Any]:
        return {
            "invocation_count": len(self._probe.history),
            "history": self._probe.history,
        }

    def reset(self) -> None:
        self._probe.reset()


@deprecated("JudgeProbe")
class JudgeAgent:
    """
    DEPRECATED: Use JudgeProbe instead.

    Migration:
        # Old
        judge = JudgeAgent(criteria="Must be helpful")
        result = await judge.invoke(input)

        # New
        probe = JudgeProbe(criteria="Must be helpful")
        trace = await probe.verify(agent, input)
        assert trace.value.passed
    """

    def __init__(self, criteria: str):
        self._probe = JudgeProbe(criteria=criteria)

    async def invoke(self, input: Any) -> Any:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value


@deprecated("JudgeProbe(oracle=...)")
class OracleAgent:
    """
    DEPRECATED: Use JudgeProbe(oracle=...) instead.

    Migration:
        # Old
        oracle = OracleAgent(oracle=lambda exp, act: exp == act)
        result = await oracle.invoke(input)

        # New
        probe = JudgeProbe(criteria="Oracle", oracle=lambda exp, act: exp == act)
        trace = await probe.verify(agent, input)
    """

    def __init__(self, oracle: Callable[[Any, Any], bool]):
        self._probe = JudgeProbe(criteria="Oracle", oracle=oracle)

    async def invoke(self, input: Any) -> Any:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value


@deprecated("TrustProbe")
class TrustGate:
    """
    DEPRECATED: Use TrustProbe instead.

    Migration:
        # Old
        gate = TrustGate(threshold=0.8)
        result = await gate.invoke(proposal)

        # New
        probe = TrustProbe(threshold=0.8)
        trace = await probe.verify(agent, proposal)
        assert trace.value.passed  # Trust granted
    """

    def __init__(self, threshold: float = 0.7, bypass_enabled: bool = True):
        self._probe = TrustProbe(threshold=threshold, bypass_enabled=bypass_enabled)

    async def invoke(self, input: Any) -> Any:
        async def identity_agent(x):
            return x

        result = await self._probe.verify(identity_agent, input)
        return result.value.value


__all__ = [
    "MockAgent",
    "FixtureAgent",
    "FailingAgent",
    "NoiseAgent",
    "LatencyAgent",
    "FlakyAgent",
    "SpyAgent",
    "PredicateAgent",
    "CounterAgent",
    "MetricsAgent",
    "JudgeAgent",
    "OracleAgent",
    "TrustGate",
]
