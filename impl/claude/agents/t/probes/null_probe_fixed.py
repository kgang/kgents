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
    >>> config = NullConfig(output="constant", delay_ms=50)
    >>> probe = NullProbe(config)
    >>> trace = await probe.verify(agent, "any input")
    >>> trace.value.value  # "constant"
    >>> trace.value.passed  # True
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, FrozenSet, Generic, TypeVar

from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthFunctor,
    TruthVerdict,
)

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


class NullProbe(TruthFunctor[NullState, A, B], Generic[A, B]):
    """
    NullProbe: Constant morphism for ground truth baseline.

    Category Theoretic Definition: The constant morphism c_b: A → B where
    ∀ a ∈ A: c_b(a) = b for fixed b ∈ B.

    DP Semantics:
    - State space: {READY, COMPUTING, DONE}
    - Action space: {invoke}
    - Transition: READY --invoke--> COMPUTING --wait--> DONE
    - Reward: R(s, invoke, s') = ETHICAL + COMPOSABLE (determinism + identity law)

    TruthFunctor Interface:
    - states: Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a, s'): Returns constitutional reward for transition
    - verify(agent, input): Returns PolicyTrace[TruthVerdict[B]]
    """

    def __init__(self, config: NullConfig):
        """Initialize NullProbe with configuration."""
        self.config = config
        self.__is_test__ = True  # T-gent marker

        # TruthFunctor required attributes
        self.name = f"NullProbe(output={self.config.output})"
        self.mode = AnalysisMode.EPISTEMIC
        self.gamma = 0.99

    # === TruthFunctor Interface ===

    @property
    def states(self) -> FrozenSet[NullState]:
        """Return DP state space."""
        return frozenset([NullState.READY, NullState.COMPUTING, NullState.DONE])

    def actions(self, state: NullState) -> FrozenSet[ProbeAction]:
        """Return available actions from state."""
        if state == NullState.READY:
            return frozenset([ProbeAction("invoke")])
        return frozenset()

    def transition(self, state: NullState, action: ProbeAction) -> NullState:
        """Return next state after action."""
        if state == NullState.READY and action.name == "invoke":
            return NullState.COMPUTING
        if state == NullState.COMPUTING:
            return NullState.DONE
        return state

    def reward(
        self, state: NullState, action: ProbeAction, next_state: NullState
    ) -> ConstitutionalScore:
        """
        Return constitutional reward for transition.

        NullProbe satisfies:
        - ETHICAL: Deterministic, predictable behavior (no surprises)
        - COMPOSABLE: Satisfies identity law
        - TASTEFUL: Simple, minimal design
        """
        if state == NullState.READY and action.name == "invoke":
            return ConstitutionalScore(
                ethical=2.0,       # Fully deterministic (max weight)
                composable=1.5,    # Satisfies identity law
                tasteful=0.5,      # Simple, clean design
            )
        return ConstitutionalScore()

    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]:
        """
        Verify agent behavior, returning constant output.

        This is the main entry point. The NullProbe ignores the agent
        and input, always returning the pre-configured constant value.

        Args:
            agent: Agent under test (ignored for NullProbe)
            input: Input to feed to agent (ignored for NullProbe)

        Returns:
            PolicyTrace[TruthVerdict[B]]: Trace with constant verdict
        """
        # Build initial probe state
        probe_state = ProbeState(
            phase="ready",
            observations=(),
        )

        # Transition: READY -> COMPUTING
        action = ProbeAction("invoke", (input,))
        next_probe_state = probe_state.transition_to("computing")

        # Simulate delay if configured
        if self.config.delay_ms > 0:
            await asyncio.sleep(self.config.delay_ms / 1000.0)

        # Compute reward for this transition
        state_before = NullState.READY
        state_after = NullState.COMPUTING
        reward_score = self.reward(state_before, action, state_after)

        # Create trace entry for READY -> COMPUTING
        entry1 = TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=next_probe_state.with_observation("invoked"),
            reward=reward_score,
            reasoning=f"Constant morphism invoked: will return {self.config.output}",
        )

        # Transition: COMPUTING -> DONE
        final_probe_state = next_probe_state.transition_to("done").with_observation(self.config.output)

        entry2 = TraceEntry(
            state_before=next_probe_state,
            action=ProbeAction("complete"),
            state_after=final_probe_state,
            reward=ConstitutionalScore(),  # No reward for automatic transition
            reasoning=f"Constant morphism completed: returned {self.config.output}",
        )

        # Create verdict
        verdict = TruthVerdict(
            value=self.config.output,  # type: ignore
            passed=True,  # NullProbe always passes (deterministic constant)
            confidence=1.0,  # Maximum confidence (no uncertainty)
            reasoning=f"NullProbe: constant morphism c_b where ∀ a: c_b(a) = {self.config.output}",
        )

        # Build trace
        trace = PolicyTrace(value=verdict)
        trace.append(entry1)
        trace.append(entry2)

        return trace


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
        >>> trace = await probe.verify(lambda x: x, "ignored")
        >>> trace.value.value  # 42
        >>> trace.value.passed  # True
    """
    return NullProbe(NullConfig(output=output, delay_ms=delay_ms))
