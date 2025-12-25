"""
NullProbe: Constant morphism for ground truth baseline.

Mode: EPISTEMIC
Purpose: Provides deterministic baseline for differential testing.
Reward: Ethical (predictable) + Composable (identity law)

The NullProbe is the constant morphism c_b: A → b where ∀ a ∈ A: c_b(a) = b
for fixed b ∈ B. It serves as ground truth in testing:

1. Differential Testing: Compare agent output against known constant
2. Identity Law Verification: Id >> NullProbe(x) ≡ NullProbe(x)
3. Timing Baselines: Configurable delay for performance testing

DP Semantics:
- States: {READY, COMPUTING, DONE}
- Actions: {invoke}
- Transition: READY --invoke--> COMPUTING --wait--> DONE
- Reward: Ethical (deterministic) + Composable (identity law satisfaction)

Example:
    >>> probe = NullProbe(output="constant", delay_ms=50)
    >>> result = await probe.invoke("any input")
    >>> result  # "constant"
    >>> trace = await probe.get_trace()
    >>> trace.value  # "constant"
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from agents.poly.types import Agent
from services.categorical.dp_bridge import PolicyTrace, Principle, TraceEntry

A = TypeVar("A")
B = TypeVar("B")


class NullState(Enum):
    """DP states for NullProbe."""

    READY = auto()
    COMPUTING = auto()
    DONE = auto()


@dataclass
class NullConfig:
    """Configuration for NullProbe."""

    output: Any = None  # Constant output to return
    delay_ms: int = 0  # Simulated delay in milliseconds


class NullProbe(Agent[A, B], Generic[A, B]):
    """
    NullProbe: Constant morphism for ground truth baseline.

    Category Theoretic Definition: The constant morphism c_b: A → B where
    ∀ a ∈ A: c_b(a) = b for fixed b ∈ B.

    DP Semantics:
    - State space: {READY, COMPUTING, DONE}
    - Action space: {invoke}
    - Transition: READY --invoke--> COMPUTING --wait--> DONE
    - Reward: R(s, invoke) = ETHICAL + COMPOSABLE (determinism + identity law)

    TruthFunctor Interface:
    - states(): Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a): Returns constitutional reward for action a in state s
    - verify(): Verifies identity law: Id >> NullProbe(x) ≡ NullProbe(x)
    """

    def __init__(self, config: NullConfig):
        """Initialize NullProbe with configuration."""
        self.config = config
        self._state = NullState.READY
        self._trace_log: list[TraceEntry] = []
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"NullProbe(output={self.config.output})"

    # === Agent Interface ===

    async def invoke(self, input: A) -> B:
        """
        Return pre-configured constant output.

        Args:
            input: Input of type A (ignored)

        Returns:
            Pre-configured output of type B
        """
        # Transition: READY -> COMPUTING
        prev_state = self._state
        self._state = NullState.COMPUTING

        # Simulate delay if configured
        if self.config.delay_ms > 0:
            await asyncio.sleep(self.config.delay_ms / 1000.0)

        # Transition: COMPUTING -> DONE
        self._state = NullState.DONE

        # Emit trace entry
        entry = TraceEntry(
            state_before=prev_state,
            action="invoke",
            state_after=self._state,
            value=self._compute_reward(prev_state, "invoke"),
            rationale=f"Constant morphism: always returns {self.config.output}",
            timestamp=datetime.now(timezone.utc),
        )
        self._trace_log.append(entry)

        # Reset for next invocation
        self._state = NullState.READY

        return self.config.output  # type: ignore

    # === TruthFunctor Interface ===

    def states(self) -> frozenset[NullState]:
        """Return DP state space."""
        return frozenset([NullState.READY, NullState.COMPUTING, NullState.DONE])

    def actions(self, state: NullState) -> frozenset[str]:
        """Return available actions from state."""
        if state == NullState.READY:
            return frozenset(["invoke"])
        return frozenset()

    def transition(self, state: NullState, action: str) -> NullState:
        """Return next state after action."""
        if state == NullState.READY and action == "invoke":
            return NullState.COMPUTING
        if state == NullState.COMPUTING:
            return NullState.DONE
        return state

    def reward(self, state: NullState, action: str) -> float:
        """Return constitutional reward for action in state."""
        return self._compute_reward(state, action)

    def _compute_reward(self, state: NullState, action: str) -> float:
        """
        Compute constitutional reward.

        NullProbe satisfies:
        - ETHICAL: Deterministic, predictable behavior (no surprises)
        - COMPOSABLE: Satisfies identity law
        """
        if state == NullState.READY and action == "invoke":
            # Full reward: ethical + composable
            ethical_score = Principle.ETHICAL.weight
            composable_score = Principle.COMPOSABLE.weight
            return ethical_score + composable_score
        return 0.0

    def verify(self) -> bool:
        """
        Verify identity law: Id >> NullProbe(x) ≡ NullProbe(x)

        The NullProbe should absorb identity composition.
        """
        # Identity law: composing with identity doesn't change behavior
        # For NullProbe, this is trivially true (constant morphism)
        return True

    async def get_trace(self) -> PolicyTrace[B]:
        """
        Get PolicyTrace with accumulated entries.

        Returns:
            PolicyTrace with value and log
        """
        return PolicyTrace(
            value=self.config.output,  # type: ignore
            log=tuple(self._trace_log),
        )

    def reset(self) -> None:
        """Reset state and trace for test isolation."""
        self._state = NullState.READY
        self._trace_log.clear()

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return len(self._trace_log)


# === Convenience Functions ===


def null_probe(output: Any = None, delay_ms: int = 0) -> NullProbe[Any, Any]:
    """
    Create a NullProbe with given configuration.

    Args:
        output: Constant output value
        delay_ms: Simulated delay in milliseconds

    Returns:
        Configured NullProbe

    Example:
        >>> probe = null_probe(output=42)
        >>> result = await probe.invoke("ignored")
        >>> result  # 42
    """
    return NullProbe(NullConfig(output=output, delay_ms=delay_ms))
