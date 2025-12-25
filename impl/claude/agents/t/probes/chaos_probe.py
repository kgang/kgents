"""
ChaosProbe: Dialectical Mode Probe for Resilience Testing

Mode: DIALECTICAL
Purpose: Inject controlled chaos to test agent survival under perturbation.
Reward: Joy (surprising behavior) - Ethical (if breaks safety)

The ChaosProbe is a dialectical tension testing morphism. It injects
four types of controlled chaos to verify agents can handle:
- FAILURE: Controlled exceptions (legacy FailingAgent)
- NOISE: Semantic perturbation (legacy NoiseAgent)
- LATENCY: Temporal delays (legacy LatencyAgent)
- FLAKINESS: Probabilistic failures (legacy FlakyAgent)

DP Semantics:
- States: {READY, INJECTING, OBSERVING, SYNTHESIZING}
- Actions: {inject_chaos, observe_survival, synthesize_verdict}
- Transition: READY -> INJECTING -> OBSERVING -> SYNTHESIZING
- Reward: High if agent survives chaos, low if breaks

Philosophy:
    "Dialectical tension reveals truth. An agent that survives
    contradiction is more truthful than one that only works in
    ideal conditions."

Example:
    >>> # Test with failure chaos
    >>> probe = ChaosProbe(ChaosConfig(
    ...     chaos_type=ChaosType.FAILURE,
    ...     intensity=0.3,
    ...     seed=42
    ... ))
    >>> trace = await probe.verify(my_agent, test_input)
    >>> trace.value.passed  # True if agent survived

    >>> # Compose probes
    >>> full_test = chaos_probe | null_probe  # Parallel testing
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timezone
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


class ChaosType(Enum):
    """Types of chaos to inject."""

    FAILURE = auto()     # Controlled exceptions
    NOISE = auto()       # Semantic perturbation
    LATENCY = auto()     # Temporal delays
    FLAKINESS = auto()   # Probabilistic failures


class ChaosState(Enum):
    """States for ChaosProbe DP formulation."""

    READY = auto()
    INJECTING = auto()
    OBSERVING = auto()
    SYNTHESIZING = auto()


@dataclass(frozen=True)
class ChaosConfig:
    """
    Configuration for chaos injection.

    Fields:
        chaos_type: Type of chaos to inject
        intensity: Severity [0.0, 1.0] (higher = more chaotic)
        seed: Random seed for determinism (None = non-deterministic)
        fail_count: For FAILURE type, how many failures before recovery (-1 = always fail)
        variance: For LATENCY type, variance in delay
    """
    chaos_type: ChaosType = ChaosType.FAILURE
    intensity: float = 0.3
    seed: int | None = None
    fail_count: int = -1  # For FAILURE: -1 = always fail, N = fail N times
    variance: float = 0.0  # For LATENCY: delay variance


class ChaosProbe(TruthFunctor[ChaosState, A, B], Generic[A, B]):
    """
    ChaosProbe: Dialectical mode probe for resilience testing.

    Injects controlled chaos to test agent survival under perturbation.
    Consolidates legacy chaos agents (Failing/Noise/Latency/Flaky) into
    a single DP-native probe with TruthFunctor interface.

    Category Theory: C_ε: Agent[A,B] → Agent[A,B ∪ {⊥}]
    The morphism that adds chaos while observing survival.

    DP Formulation:
    - State space: {READY, INJECTING, OBSERVING, SYNTHESIZING}
    - Action space: {inject, observe, synthesize}
    - Reward: R = Joy(surprise) - Ethical(if breaks)

    Constitutional Alignment:
    - Ethical: Penalize if chaos breaks agent safety
    - Joy-inducing: Reward surprising resilience
    - Heterarchical: Test adaptation under stress
    - Composable: Chaos probes can chain via >>
    """

    def __init__(self, config: ChaosConfig):
        """
        Initialize ChaosProbe with configuration.

        Args:
            config: Chaos configuration (type, intensity, seed)
        """
        self.config = config
        self.rng = random.Random(config.seed)
        self._current_state = ChaosState.READY
        self._attempt_count = 0
        self._survived = False

        # TruthFunctor required attributes
        self.name = f"ChaosProbe({config.chaos_type.name}, ε={config.intensity})"
        self.mode = AnalysisMode.DIALECTICAL
        self.gamma = 0.99

    # === TruthFunctor Interface ===

    @property
    def states(self) -> FrozenSet[ChaosState]:
        """Return DP state space."""
        return frozenset([
            ChaosState.READY,
            ChaosState.INJECTING,
            ChaosState.OBSERVING,
            ChaosState.SYNTHESIZING,
        ])

    def actions(self, state: ChaosState) -> FrozenSet[ProbeAction]:
        """Return available actions from state."""
        if state == ChaosState.READY:
            return frozenset([ProbeAction("inject_chaos")])
        elif state == ChaosState.INJECTING:
            return frozenset([ProbeAction("observe_survival")])
        elif state == ChaosState.OBSERVING:
            return frozenset([ProbeAction("synthesize_verdict")])
        return frozenset()

    def transition(self, state: ChaosState, action: ProbeAction) -> ChaosState:
        """Return next state after action."""
        if state == ChaosState.READY and action.name == "inject_chaos":
            return ChaosState.INJECTING
        elif state == ChaosState.INJECTING and action.name == "observe_survival":
            return ChaosState.OBSERVING
        elif state == ChaosState.OBSERVING and action.name == "synthesize_verdict":
            return ChaosState.SYNTHESIZING
        return state

    def reward(
        self,
        state: ChaosState,
        action: ProbeAction,
        next_state: ChaosState
    ) -> ConstitutionalScore:
        """
        Constitutional reward for chaos injection.

        Reward structure:
        - Ethical: 0.5 baseline, +0.5 if agent survived (no safety breaks)
        - Joy-inducing: 0.3 * intensity (chaos provides interesting data)
        - Heterarchical: 0.8 (tests adaptation)
        - Composable: 0.7 (can chain with other probes)
        """
        base_score = ConstitutionalScore(
            ethical=0.5,
            joy_inducing=0.3 * self.config.intensity,
            heterarchical=0.8,
            composable=0.7,
        )

        # Bonus if agent survived chaos
        if self._survived and next_state == ChaosState.SYNTHESIZING:
            return ConstitutionalScore(
                ethical=1.0,  # Full ethical credit for survival
                joy_inducing=0.5 * self.config.intensity,
                heterarchical=0.9,
                composable=0.8,
            )

        return base_score

    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]:
        """
        Verify agent behavior under chaos injection.

        Process:
        1. READY -> INJECTING: Apply chaos wrapper
        2. INJECTING -> OBSERVING: Invoke agent with chaotic input/behavior
        3. OBSERVING -> SYNTHESIZING: Determine if agent survived
        4. SYNTHESIZING: Produce verdict

        Args:
            agent: Agent under test (must have .invoke(input) method)
            input: Input to feed to agent

        Returns:
            PolicyTrace[TruthVerdict[B]]: Trace with survival verdict
        """
        trace_entries: list[TraceEntry] = []

        # State 1: READY -> INJECTING (inject chaos)
        probe_state = ProbeState(
            phase="ready",
            observations=(),
        )

        action = ProbeAction("inject_chaos", (self.config.chaos_type,))
        next_state = self.transition(self._current_state, action)

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to("injecting"),
            reward=self.reward(self._current_state, action, next_state),
            reasoning=f"Injecting {self.config.chaos_type.name} chaos with intensity {self.config.intensity}",
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = next_state
        probe_state = probe_state.transition_to("injecting")

        # State 2: INJECTING -> OBSERVING (apply chaos and observe)
        action = ProbeAction("observe_survival")
        next_state = self.transition(self._current_state, action)

        try:
            # Apply chaos based on type
            chaotic_result = await self._apply_chaos(agent, input)
            self._survived = True
            observation = f"Agent survived {self.config.chaos_type.name} chaos"

        except Exception as e:
            self._survived = False
            chaotic_result = None
            observation = f"Agent failed under {self.config.chaos_type.name}: {str(e)}"

        probe_state = probe_state.with_observation(observation)

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to("observing"),
            reward=self.reward(self._current_state, action, next_state),
            reasoning=observation,
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = next_state
        probe_state = probe_state.transition_to("observing")

        # State 3: OBSERVING -> SYNTHESIZING (compute verdict)
        action = ProbeAction("synthesize_verdict")
        next_state = self.transition(self._current_state, action)

        verdict: TruthVerdict[B] = TruthVerdict(
            value=chaotic_result,  # type: ignore[arg-type]
            passed=self._survived,
            confidence=0.95 if self._survived else 0.8,
            reasoning=observation,
            timestamp=datetime.now(timezone.utc),
        )

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to("synthesizing"),
            reward=self.reward(self._current_state, action, next_state),
            reasoning=f"Verdict: {'PASSED' if self._survived else 'FAILED'}",
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = ChaosState.READY  # Reset for next run

        # Return PolicyTrace with verdict and accumulated entries
        policy_trace: PolicyTrace[TruthVerdict[B]] = PolicyTrace(
            value=verdict,
            entries=trace_entries,
        )

        return policy_trace

    # === Chaos Injection Methods ===

    async def _apply_chaos(self, agent: Any, input: A) -> B:
        """
        Apply chaos based on configured type.

        Returns agent output if successful, raises exception if failed.
        """
        if self.config.chaos_type == ChaosType.FAILURE:
            return await self._apply_failure(agent, input)
        elif self.config.chaos_type == ChaosType.NOISE:
            return await self._apply_noise(agent, input)
        elif self.config.chaos_type == ChaosType.LATENCY:
            return await self._apply_latency(agent, input)
        elif self.config.chaos_type == ChaosType.FLAKINESS:
            return await self._apply_flakiness(agent, input)
        else:
            raise ValueError(f"Unknown chaos type: {self.config.chaos_type}")

    async def _apply_failure(self, agent: Any, input: A) -> B:
        """
        Apply FAILURE chaos: controlled exceptions.

        Simulates FailingAgent behavior.
        """
        self._attempt_count += 1

        # Check if we should fail this time
        if self.config.fail_count == -1 or self._attempt_count <= self.config.fail_count:
            # Inject failure
            error_msg = f"ChaosProbe: Injected failure (attempt {self._attempt_count})"

            # Choose exception type based on intensity
            if self.config.intensity < 0.3:
                raise RuntimeError(error_msg)
            elif self.config.intensity < 0.6:
                raise ValueError(error_msg)
            else:
                raise Exception(error_msg)

        # Recovery: invoke agent normally
        return await agent.invoke(input)  # type: ignore[no-any-return]

    async def _apply_noise(self, agent: Any, input: A) -> B:
        """
        Apply NOISE chaos: semantic perturbation.

        Simulates NoiseAgent behavior.
        """
        # Decide whether to inject noise
        if self.rng.random() > self.config.intensity:
            # No noise this time
            return await agent.invoke(input)  # type: ignore[no-any-return]

        # Perturb input if it's a string
        if isinstance(input, str):
            perturbed = self._perturb_string(input)
            return await agent.invoke(perturbed)  # type: ignore[no-any-return]

        # For non-string inputs, pass through
        return await agent.invoke(input)  # type: ignore[no-any-return]

    def _perturb_string(self, s: str) -> str:
        """Apply string perturbation based on intensity."""
        if not s:
            return s

        # Choose perturbation based on intensity
        if self.config.intensity < 0.3:
            # Mild: case change
            return s.upper() if self.rng.random() > 0.5 else s.lower()
        elif self.config.intensity < 0.6:
            # Medium: typo (swap characters)
            if len(s) < 2:
                return s
            idx = self.rng.randint(0, len(s) - 2)
            chars = list(s)
            chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
            return "".join(chars)
        else:
            # High: add noise characters
            noise_chars = "!@#$%^&*()"
            noise = self.rng.choice(noise_chars)
            idx = self.rng.randint(0, len(s))
            return s[:idx] + noise + s[idx:]

    async def _apply_latency(self, agent: Any, input: A) -> B:
        """
        Apply LATENCY chaos: temporal delays.

        Simulates LatencyAgent behavior.
        """
        # Calculate delay based on intensity
        base_delay = self.config.intensity  # intensity maps to seconds
        actual_delay = base_delay

        # Add variance if configured
        if self.config.variance > 0:
            actual_delay += self.rng.uniform(-self.config.variance, self.config.variance)

        # Never negative
        actual_delay = max(0, actual_delay)

        # Inject delay
        await asyncio.sleep(actual_delay)

        # Invoke agent
        return await agent.invoke(input)  # type: ignore[no-any-return]

    async def _apply_flakiness(self, agent: Any, input: A) -> B:
        """
        Apply FLAKINESS chaos: probabilistic failures.

        Simulates FlakyAgent behavior.
        """
        # Fail with probability = intensity
        if self.rng.random() < self.config.intensity:
            raise RuntimeError(f"ChaosProbe: Flaky failure (p={self.config.intensity})")

        # Otherwise invoke normally
        return await agent.invoke(input)  # type: ignore[no-any-return]

    def reset(self) -> None:
        """Reset probe state for test isolation."""
        self._current_state = ChaosState.READY
        self._attempt_count = 0
        self._survived = False


# === Convenience Functions ===


def chaos_probe(
    chaos_type: ChaosType = ChaosType.FAILURE,
    intensity: float = 0.3,
    seed: int | None = None,
    **kwargs: Any,
) -> ChaosProbe[Any, Any]:
    """
    Create a ChaosProbe with given configuration.

    Args:
        chaos_type: Type of chaos (FAILURE/NOISE/LATENCY/FLAKINESS)
        intensity: Severity [0.0, 1.0]
        seed: Random seed for determinism
        **kwargs: Additional config parameters (fail_count, variance)

    Returns:
        Configured ChaosProbe

    Example:
        >>> probe = chaos_probe(ChaosType.NOISE, intensity=0.5, seed=42)
        >>> trace = await probe.verify(agent, input)
    """
    config = ChaosConfig(
        chaos_type=chaos_type,
        intensity=intensity,
        seed=seed,
        fail_count=kwargs.get("fail_count", -1),
        variance=kwargs.get("variance", 0.0),
    )
    return ChaosProbe(config)


__all__ = [
    "ChaosType",
    "ChaosState",
    "ChaosConfig",
    "ChaosProbe",
    "chaos_probe",
]
