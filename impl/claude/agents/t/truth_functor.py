"""
TruthFunctor: DP-Native Verification Probes

A TruthFunctor is a morphism that verifies truthfulness of agents.
Every TruthFunctor emits PolicyTrace and has constitutional reward.

F: Agent[A, B] → PolicyTrace[TruthVerdict[B]]

The key insight: Verification IS a decision process. The probe navigates
a state space of observations, taking actions (tests), accumulating reward
(constitutional alignment), and producing a trace that IS the proof.

Architecture:
    TruthFunctor[S, A, B] = DP problem formulation
        S: Probe state space (phases of verification)
        A: Agent input type
        B: Agent output type

    PolicyTrace[B] = Writer monad for accumulation
        value: Final verdict
        entries: Trace of state transitions

    ConstitutionalScore = Reward function
        7 principles weighted by importance
        ethical > composable > joy > others

Integration:
    - Maps to AnalysisMode (CATEGORICAL/EPISTEMIC/DIALECTICAL/GENERATIVE)
    - Replaces T-gent abstraction with DP-native semantics
    - Emits PolicyTrace for witness integration
    - Supports sequential (>>) and parallel (|) composition
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, FrozenSet, Generic, TypeVar

# Type variables
S = TypeVar("S")  # State space of probe
A = TypeVar("A")  # Input to agent under test
B = TypeVar("B")  # Output from agent under test


class AnalysisMode(Enum):
    """
    Four modes of analysis from the Analysis Operad.

    Each mode corresponds to a different verification strategy:
    - CATEGORICAL: Verify composition laws (associativity, identity, etc.)
    - EPISTEMIC: Verify axiom grounding and knowledge foundations
    - DIALECTICAL: Inject contradictions to test robustness
    - GENERATIVE: Test regenerability and compression
    """

    CATEGORICAL = auto()
    EPISTEMIC = auto()
    DIALECTICAL = auto()
    GENERATIVE = auto()


@dataclass(frozen=True)
class ConstitutionalScore:
    """
    Score based on the 7 constitutional principles.

    This is the reward function for verification. Each principle maps
    to a dimension of constitutional alignment:

    - tasteful: Clear purpose, justified design
    - curated: Intentional, not exhaustive
    - ethical: Augments humans, never replaces judgment
    - joy_inducing: Delightful interaction
    - composable: Morphism in category (>> composition)
    - heterarchical: Exists in flux, not fixed hierarchy
    - generative: Spec is compression

    The weighted_total gives ethical highest importance (2.0x weight).
    """

    tasteful: float = 0.0
    curated: float = 0.0
    ethical: float = 0.0
    joy_inducing: float = 0.0
    composable: float = 0.0
    heterarchical: float = 0.0
    generative: float = 0.0

    @property
    def weighted_total(self) -> float:
        """
        Weighted sum with ethical having highest weight.

        Returns normalized score in [0, 1] range.
        """
        weights = {
            "ethical": 2.0,
            "composable": 1.5,
            "joy_inducing": 1.2,
            "tasteful": 1.0,
            "curated": 1.0,
            "heterarchical": 1.0,
            "generative": 1.0,
        }
        total = 0.0
        for name, weight in weights.items():
            total += getattr(self, name) * weight
        return total / sum(weights.values())

    def __add__(self, other: ConstitutionalScore) -> ConstitutionalScore:
        """Add two scores component-wise."""
        return ConstitutionalScore(
            tasteful=self.tasteful + other.tasteful,
            curated=self.curated + other.curated,
            ethical=self.ethical + other.ethical,
            joy_inducing=self.joy_inducing + other.joy_inducing,
            composable=self.composable + other.composable,
            heterarchical=self.heterarchical + other.heterarchical,
            generative=self.generative + other.generative,
        )

    def __mul__(self, scalar: float) -> ConstitutionalScore:
        """Scale score by scalar."""
        return ConstitutionalScore(
            tasteful=self.tasteful * scalar,
            curated=self.curated * scalar,
            ethical=self.ethical * scalar,
            joy_inducing=self.joy_inducing * scalar,
            composable=self.composable * scalar,
            heterarchical=self.heterarchical * scalar,
            generative=self.generative * scalar,
        )


@dataclass(frozen=True)
class TruthVerdict(Generic[B]):
    """
    Result of truth verification.

    This is the final value in PolicyTrace[TruthVerdict[B]].

    Fields:
        value: The actual output from agent
        passed: Whether verification succeeded
        confidence: Confidence in verdict [0, 1]
        reasoning: Human-readable explanation
        galois_loss: Optional Galois connection loss
        timestamp: When verdict was reached
    """

    value: B
    passed: bool
    confidence: float
    reasoning: str
    galois_loss: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ProbeState:
    """
    State of a probe during verification.

    The probe navigates through phases (e.g., "init", "testing", "synthesizing"),
    accumulating observations and verifying laws.

    Fields:
        phase: Current verification phase
        observations: Immutable tuple of observations made
        laws_verified: Set of law names successfully verified
        compression_ratio: Measure of generative compression
    """

    phase: str
    observations: tuple[Any, ...]
    laws_verified: FrozenSet[str] = frozenset()
    compression_ratio: float = 1.0

    def with_observation(self, obs: Any) -> ProbeState:
        """Add observation, returning new state."""
        return ProbeState(
            phase=self.phase,
            observations=self.observations + (obs,),
            laws_verified=self.laws_verified,
            compression_ratio=self.compression_ratio,
        )

    def with_law(self, law_name: str) -> ProbeState:
        """Mark law as verified, returning new state."""
        return ProbeState(
            phase=self.phase,
            observations=self.observations,
            laws_verified=self.laws_verified | {law_name},
            compression_ratio=self.compression_ratio,
        )

    def transition_to(self, new_phase: str) -> ProbeState:
        """Transition to new phase, returning new state."""
        return ProbeState(
            phase=new_phase,
            observations=self.observations,
            laws_verified=self.laws_verified,
            compression_ratio=self.compression_ratio,
        )


@dataclass(frozen=True)
class ProbeAction:
    """
    Action a probe can take.

    Examples:
        ProbeAction("test_associativity", (f, g, h))
        ProbeAction("inject_contradiction", ("axiom_1", "axiom_2"))
        ProbeAction("measure_compression", ())
    """

    name: str
    parameters: tuple[Any, ...] = ()


@dataclass(frozen=True)
class TraceEntry:
    """
    Single entry in a PolicyTrace.

    Records the (s, a, s', r) tuple from DP formulation, plus reasoning.
    This is the atomic unit of proof.
    """

    state_before: ProbeState
    action: ProbeAction
    state_after: ProbeState
    reward: ConstitutionalScore
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyTrace(Generic[B]):
    """
    Accumulated trace of verification.

    This is the Writer monad for probes. As verification proceeds,
    the probe builds up a trace of state transitions. The trace IS
    the proof—each entry shows what was tested, why, and what reward
    was earned.

    Usage:
        trace = PolicyTrace(verdict)
        trace.append(TraceEntry(...))
        trace.append(TraceEntry(...))
        total = trace.total_reward  # Sum of constitutional scores
    """

    value: B
    entries: list[TraceEntry] = field(default_factory=list)

    def append(self, entry: TraceEntry) -> PolicyTrace[B]:
        """Add entry to trace."""
        self.entries.append(entry)
        return self

    @property
    def total_reward(self) -> float:
        """Sum of weighted rewards across trace."""
        return sum(e.reward.weighted_total for e in self.entries)

    @property
    def max_reward(self) -> float:
        """Maximum reward achieved in any single step."""
        if not self.entries:
            return 0.0
        return max(e.reward.weighted_total for e in self.entries)

    @property
    def avg_reward(self) -> float:
        """Average reward per step."""
        if not self.entries:
            return 0.0
        return self.total_reward / len(self.entries)


class TruthFunctor(ABC, Generic[S, A, B]):
    """
    Abstract base for all verification probes.

    Every TruthFunctor is a DP problem formulation:
    - states: Valid probe states (phases of verification)
    - actions(s): Valid actions from state s
    - transition(s, a): State evolution s → s'
    - reward(s, a, s'): Constitutional scoring
    - gamma: Discount factor (default 0.99)

    The verify() method runs the probe, producing PolicyTrace[TruthVerdict[B]].
    The trace IS the proof. The verdict IS the mark.

    Composition:
        probe1 >> probe2  # Sequential: run probe1, then probe2
        probe1 | probe2   # Parallel: run both, combine results

    Integration:
        - Each probe has an AnalysisMode (CATEGORICAL/EPISTEMIC/etc.)
        - PolicyTrace entries can be witnessed via W-gent
        - ConstitutionalScore integrates with Director's merit function
    """

    name: str
    mode: AnalysisMode
    gamma: float = 0.99

    @property
    @abstractmethod
    def states(self) -> FrozenSet[S]:
        """
        Valid probe states.

        Example: frozenset(["init", "testing", "synthesizing", "complete"])
        """
        ...

    @abstractmethod
    def actions(self, state: S) -> FrozenSet[ProbeAction]:
        """
        Valid actions for given state.

        State-dependent action space. For example:
        - "init" → [ProbeAction("start_test")]
        - "testing" → [ProbeAction("test_law", (law,)) for law in laws]
        - "synthesizing" → [ProbeAction("compute_verdict")]
        """
        ...

    @abstractmethod
    def transition(self, state: S, action: ProbeAction) -> S:
        """
        State transition function.

        Deterministic: (s, a) → s'
        """
        ...

    @abstractmethod
    def reward(self, state: S, action: ProbeAction, next_state: S) -> ConstitutionalScore:
        """
        Constitutional reward for transition.

        Higher reward when:
        - Ethical: probe respects agent autonomy
        - Composable: probe can be chained with others
        - Joy-inducing: probe provides helpful feedback
        - etc.
        """
        ...

    @abstractmethod
    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]:
        """
        Verify agent behavior, returning traced verdict.

        This is the main entry point. The probe runs the agent,
        observes behavior, verifies laws, and produces a trace.

        Args:
            agent: Agent under test (any callable A → B)
            input: Input to feed to agent

        Returns:
            PolicyTrace[TruthVerdict[B]]: Trace with final verdict

        The trace contains:
        - entries: List of (s, a, s', r) tuples
        - value: TruthVerdict with passed/failed and reasoning
        """
        ...

    def __rshift__(self, other: TruthFunctor) -> ComposedProbe:
        """
        Sequential composition: self >> other

        Run self, then run other on the result.
        """
        return ComposedProbe(self, other, "seq")

    def __or__(self, other: TruthFunctor) -> ComposedProbe:
        """
        Parallel composition: self | other

        Run both probes, combine traces.
        """
        return ComposedProbe(self, other, "par")


@dataclass
class ComposedProbe(TruthFunctor):
    """
    Composition of two probes.

    Supports two composition modes:
    - "seq": Sequential (left >> right) — run left, feed to right
    - "par": Parallel (left | right) — run both, merge traces

    This is a product type in the category of probes.
    """

    left: TruthFunctor
    right: TruthFunctor
    op: str  # "seq" | "par"

    @property
    def name(self) -> str:
        symbol = ">>" if self.op == "seq" else "|"
        return f"({self.left.name} {symbol} {self.right.name})"

    @property
    def mode(self) -> AnalysisMode:
        """Use left's mode for composed probe."""
        return self.left.mode

    @property
    def states(self) -> FrozenSet[Any]:
        """
        Product state space: left.states × right.states

        Represented as tuples (left_state, right_state).
        """
        return frozenset((ls, rs) for ls in self.left.states for rs in self.right.states)

    def actions(self, state: Any) -> FrozenSet[ProbeAction]:
        """
        Actions depend on composition mode.

        - seq: Only left actions until left completes
        - par: Union of left and right actions
        """
        if self.op == "seq":
            # Sequential: only left's actions initially
            left_state, right_state = state
            return self.left.actions(left_state)
        else:
            # Parallel: union of actions
            left_state, right_state = state
            left_actions = self.left.actions(left_state)
            right_actions = self.right.actions(right_state)
            return left_actions | right_actions

    def transition(self, state: Any, action: ProbeAction) -> Any:
        """
        Product transition: advance appropriate component.
        """
        left_state, right_state = state

        if self.op == "seq":
            # Sequential: transition left, keep right unchanged
            new_left = self.left.transition(left_state, action)
            return (new_left, right_state)
        else:
            # Parallel: determine which component to advance
            if action in self.left.actions(left_state):
                new_left = self.left.transition(left_state, action)
                return (new_left, right_state)
            else:
                new_right = self.right.transition(right_state, action)
                return (left_state, new_right)

    def reward(self, state: Any, action: ProbeAction, next_state: Any) -> ConstitutionalScore:
        """
        Combined reward: sum of component rewards.
        """
        left_before, right_before = state
        left_after, right_after = next_state

        # Get reward from whichever component transitioned
        if left_before != left_after:
            left_reward = self.left.reward(left_before, action, left_after)
        else:
            left_reward = ConstitutionalScore()

        if right_before != right_after:
            right_reward = self.right.reward(right_before, action, right_after)
        else:
            right_reward = ConstitutionalScore()

        return left_reward + right_reward

    async def verify(self, agent: Any, input: Any) -> PolicyTrace[TruthVerdict]:
        """
        Run composed verification.

        - seq: Run left, then feed result to right
        - par: Run both, merge traces
        """
        if self.op == "seq":
            # Sequential composition
            left_trace = await self.left.verify(agent, input)
            right_trace = await self.right.verify(agent, input)

            # Merge traces
            combined = PolicyTrace(right_trace.value)
            combined.entries.extend(left_trace.entries)
            combined.entries.extend(right_trace.entries)
            return combined
        else:
            # Parallel composition
            left_trace = await self.left.verify(agent, input)
            right_trace = await self.right.verify(agent, input)

            # Merge traces, combine verdicts
            combined_verdict = TruthVerdict(
                value=(left_trace.value.value, right_trace.value.value),
                passed=left_trace.value.passed and right_trace.value.passed,
                confidence=min(left_trace.value.confidence, right_trace.value.confidence),
                reasoning=f"Left: {left_trace.value.reasoning}\nRight: {right_trace.value.reasoning}",
            )

            combined = PolicyTrace(combined_verdict)
            combined.entries.extend(left_trace.entries)
            combined.entries.extend(right_trace.entries)
            return combined


# Export all types
__all__ = [
    "AnalysisMode",
    "ConstitutionalScore",
    "TruthVerdict",
    "ProbeState",
    "ProbeAction",
    "TraceEntry",
    "PolicyTrace",
    "TruthFunctor",
    "ComposedProbe",
]
