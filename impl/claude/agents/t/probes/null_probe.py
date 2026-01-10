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
    >>> probe = NullProbe(constant="constant", delay_ms=50)
    >>> trace = await probe.verify(agent, "any input")
    >>> trace.value.value  # "constant"
    >>> trace.value.passed  # True
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, FrozenSet, Generic, TypeVar

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


@dataclass
class NullConfig:
    """Configuration for NullProbe."""

    output: Any = None  # Constant output to return
    delay_ms: int = 0  # Simulated delay in milliseconds


class NullState(str, Enum):
    """DP states for NullProbe."""

    READY = "ready"
    COMPUTING = "computing"
    DONE = "done"


@dataclass(frozen=True)
class NullProbe(TruthFunctor[NullState, A, B], Generic[A, B]):
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
    - states: Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a, s'): Returns constitutional reward for transition
    - verify(agent, input): Returns PolicyTrace[TruthVerdict[B]]
    """

    constant: B
    delay_ms: int = 0
    name: str = ""

    def __post_init__(self) -> None:
        """Set default name if not provided."""
        if not self.name:
            object.__setattr__(self, "name", f"NullProbe(output={self.constant})")

    @property
    def mode(self) -> AnalysisMode:  # type: ignore[override]
        """Analysis mode for this probe."""
        return AnalysisMode.EPISTEMIC

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
        - GENERATIVE: Minimal but present (constant is a form of compression)
        """
        if state == NullState.READY and action.name == "invoke":
            return ConstitutionalScore(
                ethical=1.0,  # Fully predictable
                composable=1.0,  # Satisfies identity
                generative=0.5,  # Minimal but present
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
        action = ProbeAction("invoke")
        next_probe_state = probe_state.transition_to("computing")

        # Simulate delay if configured
        if self.delay_ms > 0:
            await asyncio.sleep(self.delay_ms / 1000.0)

        # Compute reward for this transition
        state_before = NullState.READY
        state_after = NullState.COMPUTING
        reward_score = self.reward(state_before, action, state_after)

        # Create trace entry for READY -> COMPUTING
        entry1 = TraceEntry(
            state_before=next_probe_state,
            action=action,
            state_after=next_probe_state.with_observation("invoked"),
            reward=reward_score,
            reasoning=f"Constant morphism invoked: will return {self.constant}",
        )

        # Transition: COMPUTING -> DONE
        final_probe_state = next_probe_state.transition_to("done")

        entry2 = TraceEntry(
            state_before=next_probe_state,
            action=ProbeAction("complete"),
            state_after=final_probe_state.with_observation(self.constant),
            reward=ConstitutionalScore(),
            reasoning=f"Constant morphism completed: returned {self.constant}",
        )

        # Create verdict
        verdict = TruthVerdict(
            value=self.constant,
            passed=True,  # NullProbe always passes (deterministic constant)
            confidence=1.0,  # Maximum confidence (no uncertainty)
            reasoning=f"NullProbe: constant morphism c_b where ∀ a: c_b(a) = {self.constant}",
        )

        # Build trace
        trace = PolicyTrace(value=verdict)
        trace.append(entry1)
        trace.append(entry2)

        return trace


# === Convenience Functions ===


def null_probe(constant: Any = None, delay_ms: int = 0) -> NullProbe[Any, Any]:
    """
    Create a NullProbe with given configuration.

    Args:
        constant: Constant output value
        delay_ms: Simulated delay in milliseconds

    Returns:
        Configured NullProbe

    Example:
        >>> probe = null_probe(constant=42)
        >>> trace = await probe.verify(agent, "ignored")
        >>> trace.value.value  # 42
        >>> trace.value.passed  # True
    """
    return NullProbe(constant=constant, delay_ms=delay_ms)
