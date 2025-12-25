"""
ChaosProbe: Perturbation morphism for dialectical testing.

Mode: DIALECTICAL
Purpose: Inject controlled chaos to test agent resilience.
Reward: Joy (surprising) - Ethical (if breaks safety)

The ChaosProbe applies controlled perturbations to test robustness:
- FAILURE: Probabilistic exceptions (test retry logic)
- NOISE: Semantic perturbations (test input tolerance)
- LATENCY: Delays (test timeout handling)
- FLAKINESS: Intermittent failures (test resilience)

All chaos is deterministic via seed (reproducible chaos engineering).

DP Semantics:
- States: {READY, PERTURBING, FAILED, SUCCEEDED}
- Actions: {inject_chaos}
- Transition: READY --inject--> PERTURBING --{fail|succeed}--> {FAILED|SUCCEEDED}
- Reward: Joy (chaos) - Ethical (safety violations)

Example:
    >>> probe = ChaosProbe(chaos_type=ChaosType.FAILURE, probability=0.3, seed=42)
    >>> try:
    ...     result = await probe.invoke("test")
    ... except RuntimeError:
    ...     print("Chaos injected!")
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from agents.poly.types import Agent
from services.categorical.dp_bridge import PolicyTrace, Principle, TraceEntry

A = TypeVar("A")


class ChaosType(Enum):
    """Types of chaos to inject."""

    FAILURE = "failure"  # Raise exceptions
    NOISE = "noise"  # Perturb output
    LATENCY = "latency"  # Add delays
    FLAKINESS = "flakiness"  # Intermittent failures


class ChaosState(Enum):
    """DP states for ChaosProbe."""

    READY = auto()
    PERTURBING = auto()
    FAILED = auto()
    SUCCEEDED = auto()


@dataclass
class ChaosConfig:
    """Configuration for ChaosProbe."""

    chaos_type: ChaosType = ChaosType.FAILURE
    probability: float = 0.5  # Probability of chaos (0.0-1.0)
    seed: int | None = None  # For reproducibility
    latency_ms: int = 100  # Latency in milliseconds (for LATENCY type)
    noise_level: float = 0.1  # Noise level (for NOISE type)


class ChaosProbe(Agent[A, A], Generic[A]):
    """
    ChaosProbe: Perturbation morphism for dialectical testing.

    Category Theory: C_p: A → A | Error where p is probability
    The morphism that probabilistically perturbs or fails.

    Algebraic Laws:
    - C_0 ≡ id (zero probability is identity)
    - C_1 ≡ bottom (probability 1 always fails)
    - C_p ∘ C_p ≈ C_{p²} (chaos compounds)

    DP Semantics:
    - State space: {READY, PERTURBING, FAILED, SUCCEEDED}
    - Action space: {inject_chaos}
    - Transition: READY --inject--> PERTURBING --{fail|succeed}--> {FAILED|SUCCEEDED}
    - Reward: R(s, inject) = JOY - ETHICAL * (safety_violations)

    TruthFunctor Interface:
    - states(): Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a): Returns constitutional reward for action a in state s
    - verify(): Verifies chaos laws (C_0 ≡ id, C_1 ≡ bottom)
    """

    def __init__(self, config: ChaosConfig):
        """Initialize ChaosProbe with configuration."""
        self.config = config
        self._rng = random.Random(config.seed)
        self._state = ChaosState.READY
        self._trace_log: list[TraceEntry] = []
        self._injection_count = 0
        self._failure_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"ChaosProbe({self.config.chaos_type.value}, p={self.config.probability})"

    # === Agent Interface ===

    async def invoke(self, input: A) -> A:
        """
        Apply chaos to input.

        Args:
            input: Input of type A

        Returns:
            Perturbed input or raises exception

        Raises:
            RuntimeError: If FAILURE chaos is injected
        """
        prev_state = self._state
        self._state = ChaosState.PERTURBING
        self._injection_count += 1

        # Decide whether to inject chaos
        inject = self._rng.random() < self.config.probability

        try:
            if inject:
                result = await self._inject_chaos(input)
                self._state = ChaosState.SUCCEEDED
            else:
                result = input
                self._state = ChaosState.SUCCEEDED

            # Emit trace entry (success)
            entry = TraceEntry(
                state_before=prev_state,
                action="inject_chaos",
                state_after=self._state,
                value=self._compute_reward(prev_state, "inject_chaos", injected=inject),
                rationale=f"Chaos: {self.config.chaos_type.value}, injected={inject}",
                timestamp=datetime.now(timezone.utc),
            )
            self._trace_log.append(entry)

            # Reset for next invocation
            self._state = ChaosState.READY
            return result

        except Exception as e:
            # Chaos caused failure
            self._state = ChaosState.FAILED
            self._failure_count += 1

            # Emit trace entry (failure)
            entry = TraceEntry(
                state_before=prev_state,
                action="inject_chaos",
                state_after=self._state,
                value=self._compute_reward(prev_state, "inject_chaos", injected=True, failed=True),
                rationale=f"Chaos failed: {e}",
                timestamp=datetime.now(timezone.utc),
            )
            self._trace_log.append(entry)

            # Reset for next invocation
            self._state = ChaosState.READY
            raise

    async def _inject_chaos(self, input: A) -> A:
        """
        Inject chaos based on configured type.

        Args:
            input: Input to perturb

        Returns:
            Perturbed input

        Raises:
            RuntimeError: For FAILURE and FLAKINESS types
        """
        if self.config.chaos_type == ChaosType.FAILURE:
            raise RuntimeError("ChaosProbe: Injected failure")

        elif self.config.chaos_type == ChaosType.NOISE:
            return self._inject_noise(input)

        elif self.config.chaos_type == ChaosType.LATENCY:
            await asyncio.sleep(self.config.latency_ms / 1000.0)
            return input

        elif self.config.chaos_type == ChaosType.FLAKINESS:
            # Flakiness: sometimes fails, sometimes succeeds
            if self._rng.random() < 0.5:
                raise RuntimeError("ChaosProbe: Flaky failure")
            return input

        return input

    def _inject_noise(self, input: A) -> A:
        """
        Inject semantic noise into input.

        Args:
            input: Input to perturb

        Returns:
            Perturbed input
        """
        if isinstance(input, str):
            # String noise: randomly modify characters
            chars = list(input)
            num_changes = max(1, int(len(chars) * self.config.noise_level))
            for _ in range(num_changes):
                if chars:
                    idx = self._rng.randint(0, len(chars) - 1)
                    chars[idx] = chr(ord(chars[idx]) + self._rng.choice([-1, 1]))
            return "".join(chars)  # type: ignore

        elif isinstance(input, (int, float)):
            # Numeric noise: add small perturbation
            noise = self._rng.gauss(0, self.config.noise_level)
            return input + noise  # type: ignore

        # For other types, return unchanged
        return input

    # === TruthFunctor Interface ===

    def states(self) -> frozenset[ChaosState]:
        """Return DP state space."""
        return frozenset([
            ChaosState.READY,
            ChaosState.PERTURBING,
            ChaosState.FAILED,
            ChaosState.SUCCEEDED,
        ])

    def actions(self, state: ChaosState) -> frozenset[str]:
        """Return available actions from state."""
        if state == ChaosState.READY:
            return frozenset(["inject_chaos"])
        return frozenset()

    def transition(self, state: ChaosState, action: str) -> ChaosState:
        """Return next state after action."""
        if state == ChaosState.READY and action == "inject_chaos":
            return ChaosState.PERTURBING
        # Non-deterministic: could go to FAILED or SUCCEEDED
        # This is captured in the probability
        return state

    def reward(self, state: ChaosState, action: str, injected: bool = False, failed: bool = False) -> float:
        """Return constitutional reward for action in state."""
        return self._compute_reward(state, action, injected, failed)

    def _compute_reward(self, state: ChaosState, action: str, injected: bool = False, failed: bool = False) -> float:
        """
        Compute constitutional reward.

        ChaosProbe satisfies:
        - JOY: Surprising behavior (chaos is delightful in test)
        - ETHICAL: Penalized if causes safety violations
        """
        if state == ChaosState.READY and action == "inject_chaos":
            reward = 0.0

            # Joy from injecting chaos (testing is good)
            if injected:
                reward += Principle.JOY_INDUCING.weight

            # Ethical penalty if caused failure
            if failed:
                reward -= Principle.ETHICAL.weight

            return reward

        return 0.0

    def verify(self) -> bool:
        """
        Verify chaos laws:
        - C_0 ≡ id (zero probability is identity)
        - C_1 ≡ bottom (probability 1 always fails for FAILURE type)
        """
        # Law 1: C_0 should never inject chaos
        if self.config.probability == 0.0:
            return self._injection_count == 0 or self._failure_count == 0

        # Law 2: C_1 with FAILURE should always fail
        if self.config.probability == 1.0 and self.config.chaos_type == ChaosType.FAILURE:
            return self._failure_count == self._injection_count

        # For intermediate probabilities, laws are probabilistic
        return True

    async def get_trace(self) -> PolicyTrace[A]:
        """
        Get PolicyTrace with accumulated entries.

        Returns:
            PolicyTrace with value and log
        """
        # For ChaosProbe, the "value" is the chaos statistics
        value = {
            "injection_count": self._injection_count,
            "failure_count": self._failure_count,
            "success_rate": 1.0 - (self._failure_count / max(1, self._injection_count)),
        }

        return PolicyTrace(
            value=value,  # type: ignore
            log=tuple(self._trace_log),
        )

    def reset(self) -> None:
        """Reset state and trace for test isolation."""
        self._state = ChaosState.READY
        self._trace_log.clear()
        self._injection_count = 0
        self._failure_count = 0

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return self._injection_count

    @property
    def failure_rate(self) -> float:
        """Proportion of invocations that failed."""
        if self._injection_count == 0:
            return 0.0
        return self._failure_count / self._injection_count


# === Convenience Functions ===


def chaos_probe(
    chaos_type: ChaosType = ChaosType.FAILURE,
    probability: float = 0.5,
    seed: int | None = None,
) -> ChaosProbe[Any]:
    """
    Create a ChaosProbe with given configuration.

    Args:
        chaos_type: Type of chaos to inject
        probability: Probability of injection (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        Configured ChaosProbe

    Example:
        >>> probe = chaos_probe(ChaosType.NOISE, probability=0.3, seed=42)
        >>> result = await probe.invoke("test input")
    """
    return ChaosProbe(ChaosConfig(
        chaos_type=chaos_type,
        probability=probability,
        seed=seed,
    ))
