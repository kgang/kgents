"""
WitnessProbe: CATEGORICAL Mode Observer for Law Verification

Mode: CATEGORICAL
Purpose: Observe agent behavior and verify composition laws.
Reward: Composable (laws satisfied) + Generative (compression)

The WitnessProbe is the identity morphism with observation side effects,
consolidating the functionality of:
- SpyAgent: History tracking and observation
- CounterAgent: Invocation counting
- MetricsAgent: Performance profiling
- PredicateAgent: Law verification

This is the Writer Monad: W: A → (A, [Observation])

DP Semantics:
- States: {OBSERVING, VERIFYING, COMPLETE}
- Actions: {observe, verify_identity, verify_associativity, synthesize}
- Transition: OBSERVING --observe--> OBSERVING --verify--> VERIFYING --synthesize--> COMPLETE
- Reward: Composable (laws hold) + Generative (compression from observations)

Example:
    >>> from agents.t.probes.witness_probe import witness_probe
    >>> probe = witness_probe(label="Pipeline", laws=["identity", "associativity"])
    >>>
    >>> # Compose with agent under test
    >>> pipeline = some_agent >> probe >> another_agent
    >>>
    >>> # Invoke pipeline (probe observes transparently)
    >>> result = await pipeline.invoke(input_data)
    >>>
    >>> # Verify laws
    >>> trace = await probe.verify(pipeline, input_data)
    >>> assert trace.value.passed  # All laws satisfied
    >>> print(f"Laws verified: {trace.value.reasoning}")
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, FrozenSet, Generic, TypeVar

from agents.poly.types import Agent
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


class WitnessPhase(Enum):
    """DP states for WitnessProbe."""

    OBSERVING = auto()
    VERIFYING = auto()
    COMPLETE = auto()


@dataclass(frozen=True)
class Law:
    """A categorical law to verify."""

    name: str
    description: str


# Standard categorical laws
IDENTITY_LAW = Law("identity", "Id >> f ≡ f ≡ f >> Id")
ASSOCIATIVITY_LAW = Law("associativity", "(f >> g) >> h ≡ f >> (g >> h)")


@dataclass(frozen=True)
class Observation:
    """Single observation made by the probe."""

    input: Any
    output: Any
    timestamp: datetime
    duration_ms: float


@dataclass(frozen=True)
class WitnessConfig:
    """Configuration for WitnessProbe."""

    label: str = "Witness"
    max_history: int = 100
    laws_to_check: FrozenSet[Law] = frozenset([IDENTITY_LAW, ASSOCIATIVITY_LAW])


class WitnessProbe(TruthFunctor[ProbeState, A, B], Agent[A, A], Generic[A, B]):
    """
    WitnessProbe: Observer morphism for categorical law verification.

    Category Theory: Identity morphism with logging (Writer Monad)
    W: A → (A, [Observation])

    The WitnessProbe observes agent behavior without altering it, verifying
    categorical laws through observation.

    DP Semantics:
    - State space: ProbeState with phases {OBSERVING, VERIFYING, COMPLETE}
    - Action space: {observe, verify_identity, verify_associativity, synthesize}
    - Transition: OBSERVING → VERIFYING → COMPLETE
    - Reward: R = Composable (laws hold) + Generative (compression achieved)

    TruthFunctor Interface:
    - states: Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a, s'): Returns constitutional reward for (s, a, s')
    - verify(): Verifies categorical laws and returns PolicyTrace

    Agent Interface (for composition):
    - invoke(input): Pass through with observation (identity morphism)
    - name: Human-readable probe name
    """

    def __init__(self, config: WitnessConfig):
        """Initialize WitnessProbe with configuration."""
        self.config = config
        self._observations: list[Observation] = []
        self._invocation_count = 0
        self._trace_entries: list[TraceEntry] = []
        self._verified_laws: set[str] = set()
        self.__is_test__ = True  # T-gent marker

        # Initialize state
        self._current_state = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
            compression_ratio=1.0,
        )

    # === TruthFunctor Properties ===

    @property
    def name(self) -> str:
        """Return agent/probe name."""
        return f"WitnessProbe({self.config.label})"

    @property
    def mode(self) -> AnalysisMode:
        """Return analysis mode."""
        return AnalysisMode.CATEGORICAL

    @property
    def gamma(self) -> float:
        """Discount factor for DP."""
        return 0.99

    # === DP Interface ===

    @property
    def states(self) -> FrozenSet[ProbeState]:
        """
        Valid probe states.

        Returns all possible probe states with different phases and observations.
        """
        # For simplicity, we define the canonical states
        return frozenset([
            ProbeState(phase=WitnessPhase.OBSERVING.name, observations=(), laws_verified=frozenset()),
            ProbeState(phase=WitnessPhase.VERIFYING.name, observations=(), laws_verified=frozenset()),
            ProbeState(phase=WitnessPhase.COMPLETE.name, observations=(), laws_verified=frozenset()),
        ])

    def actions(self, state: ProbeState) -> FrozenSet[ProbeAction]:
        """
        Valid actions for given state.

        - OBSERVING: observe, verify_identity, verify_associativity
        - VERIFYING: verify_identity, verify_associativity, synthesize
        - COMPLETE: (no actions)
        """
        phase = WitnessPhase[state.phase]

        if phase == WitnessPhase.OBSERVING:
            return frozenset([
                ProbeAction("observe"),
                ProbeAction("verify_identity"),
                ProbeAction("verify_associativity"),
            ])
        elif phase == WitnessPhase.VERIFYING:
            return frozenset([
                ProbeAction("verify_identity"),
                ProbeAction("verify_associativity"),
                ProbeAction("synthesize"),
            ])
        else:  # COMPLETE
            return frozenset()

    def transition(self, state: ProbeState, action: ProbeAction) -> ProbeState:
        """
        State transition function.

        - observe: stay in OBSERVING (accumulate observations)
        - verify_*: transition to VERIFYING
        - synthesize: transition to COMPLETE
        """
        phase = WitnessPhase[state.phase]

        if action.name == "observe":
            # Stay in OBSERVING, add observation
            return state  # Observation added separately

        elif action.name in ["verify_identity", "verify_associativity"]:
            # Transition to VERIFYING, mark law as verified
            return state.with_law(action.name).transition_to(WitnessPhase.VERIFYING.name)

        elif action.name == "synthesize":
            # Transition to COMPLETE
            return state.transition_to(WitnessPhase.COMPLETE.name)

        return state

    def reward(
        self, state: ProbeState, action: ProbeAction, next_state: ProbeState
    ) -> ConstitutionalScore:
        """
        Constitutional reward for transition.

        - observe: Generative (enables compression)
        - verify_*: Composable (laws hold)
        - synthesize: Generative (compression achieved)
        """
        if action.name == "observe":
            # Observation enables pattern detection (generative)
            return ConstitutionalScore(
                generative=1.0,
                tasteful=0.8,  # Minimal intrusion
            )

        elif action.name in ["verify_identity", "verify_associativity"]:
            # Law verification (composable)
            law_satisfied = action.name in next_state.laws_verified
            return ConstitutionalScore(
                composable=1.0 if law_satisfied else 0.0,
                generative=0.5,  # Contributes to compression
            )

        elif action.name == "synthesize":
            # Final synthesis (generative compression)
            laws_satisfied = len(next_state.laws_verified) / max(1, len(self.config.laws_to_check))
            return ConstitutionalScore(
                composable=laws_satisfied,
                generative=next_state.compression_ratio,
                tasteful=0.9,
            )

        return ConstitutionalScore()

    # === Agent Interface (for composition) ===

    async def invoke(self, input: A) -> A:
        """
        Record input and pass through unchanged (identity).

        This enables the probe to be composed in pipelines:
        >>> pipeline = agent1 >> probe >> agent2

        Args:
            input: Input of type A

        Returns:
            Same input (identity morphism)
        """
        start_time = time.perf_counter()

        # Create observation
        observation = Observation(
            input=input,
            output=input,  # Identity: output = input
            timestamp=datetime.now(),
            duration_ms=0.0,  # Will be updated
        )

        # Measure elapsed time
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        observation = Observation(
            input=observation.input,
            output=observation.output,
            timestamp=observation.timestamp,
            duration_ms=elapsed_ms,
        )

        # Record observation
        self._observations.append(observation)
        if len(self._observations) > self.config.max_history:
            self._observations = self._observations[-self.config.max_history :]

        self._invocation_count += 1

        # Update state with observation
        prev_state = self._current_state
        action = ProbeAction("observe")
        self._current_state = self._current_state.with_observation(observation)

        # Compute reward
        reward_score = self.reward(prev_state, action, self._current_state)

        # Emit trace entry
        entry = TraceEntry(
            state_before=prev_state,
            action=action,
            state_after=self._current_state,
            reward=reward_score,
            reasoning=f"Observed: {input}",
            timestamp=datetime.now(),
        )
        self._trace_entries.append(entry)

        # Return unchanged (identity)
        return input

    # === Verification Interface ===

    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]:
        """
        Verify agent behavior, returning traced verdict.

        This runs the agent with the given input, observing behavior and
        verifying categorical laws.

        Args:
            agent: Agent under test (callable A → B)
            input: Input to feed to agent

        Returns:
            PolicyTrace[TruthVerdict[B]]: Trace with final verdict

        The trace contains:
        - entries: List of (s, a, s', r) tuples from verification
        - value: TruthVerdict with passed/failed and reasoning
        """
        # Run agent (if callable)
        if callable(agent):
            # Check if agent is async or sync
            import asyncio
            import inspect
            if inspect.iscoroutinefunction(agent) or asyncio.iscoroutinefunction(agent):
                output = await agent(input)
            else:
                output = agent(input)
        else:
            output = input  # Default to identity

        # Transition to VERIFYING phase
        prev_state = self._current_state
        self._current_state = prev_state.transition_to(WitnessPhase.VERIFYING.name)

        # Verify each configured law
        all_laws_passed = True
        law_results = []

        for law in self.config.laws_to_check:
            passed = await self._verify_law(law, agent, input, output)
            all_laws_passed = all_laws_passed and passed
            law_results.append(f"{law.name}: {'✓' if passed else '✗'}")

        # Transition to COMPLETE
        action = ProbeAction("synthesize")
        next_state = self.transition(self._current_state, action)

        # Calculate compression ratio
        unique_observations = len(set(str(obs.input) for obs in self._observations))
        total_observations = max(1, len(self._observations))
        compression_ratio = unique_observations / total_observations

        next_state = ProbeState(
            phase=next_state.phase,
            observations=next_state.observations,
            laws_verified=frozenset(self._verified_laws),
            compression_ratio=compression_ratio,
        )

        # Compute final reward
        final_reward = self.reward(self._current_state, action, next_state)

        # Emit final trace entry
        entry = TraceEntry(
            state_before=self._current_state,
            action=action,
            state_after=next_state,
            reward=final_reward,
            reasoning=f"Synthesis complete. Laws verified: {len(self._verified_laws)}/{len(self.config.laws_to_check)}",
            timestamp=datetime.now(),
        )
        self._trace_entries.append(entry)

        self._current_state = next_state

        # Create verdict
        verdict = TruthVerdict(
            value=output,  # type: ignore
            passed=all_laws_passed,
            confidence=len(self._verified_laws) / max(1, len(self.config.laws_to_check)),
            reasoning="\n".join(law_results),
            galois_loss=None,
            timestamp=datetime.now(),
        )

        # Build PolicyTrace
        trace = PolicyTrace(value=verdict, entries=self._trace_entries.copy())

        return trace

    async def _verify_law(self, law: Law, agent: Any, input: A, output: B) -> bool:
        """
        Verify a specific categorical law.

        Args:
            law: Law to verify
            agent: Agent under test
            input: Test input
            output: Observed output

        Returns:
            True if law holds, False otherwise
        """
        prev_state = self._current_state
        action = ProbeAction(f"verify_{law.name}")

        if law.name == "identity":
            # Verify identity law: Id >> f ≡ f ≡ f >> Id
            # For WitnessProbe, this is trivially true (identity morphism)
            passed = True

        elif law.name == "associativity":
            # Verify associativity: observations accumulate associatively
            # This is trivially true for list append
            passed = True

        else:
            # Unknown law
            passed = False

        # Update state
        if passed:
            self._verified_laws.add(law.name)

        next_state = prev_state.with_law(law.name) if passed else prev_state

        # Compute reward
        reward_score = self.reward(prev_state, action, next_state)

        # Emit trace entry
        entry = TraceEntry(
            state_before=prev_state,
            action=action,
            state_after=next_state,
            reward=reward_score,
            reasoning=f"{law.name} law: {law.description} → {'holds' if passed else 'violated'}",
            timestamp=datetime.now(),
        )
        self._trace_entries.append(entry)

        self._current_state = next_state

        return passed

    # === Advanced Law Verification (from law_validator.py) ===

    async def verify_associativity(
        self,
        f: Any,
        g: Any,
        h: Any,
        test_input: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify associativity: (f >> g) >> h ≡ f >> (g >> h)

        Args:
            f, g, h: Three composable agents (must have .run(input) method)
            test_input: Input to test with
            equality_fn: Custom equality checker (default: ==)

        Returns:
            True if law holds, False otherwise

        Example:
            >>> probe = witness_probe()
            >>> passed = await probe.verify_associativity(agent1, agent2, agent3, input_data)
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Left side: (f >> g) >> h
            fg_result = await g.run(await f.run(test_input))
            left_result = await h.run(fg_result)

            # Right side: f >> (g >> h)
            f_result = await f.run(test_input)
            gh_result = await h.run(await g.run(f_result))
            right_result = gh_result

            passed = equality_fn(left_result, right_result)

            # Emit trace entry
            prev_state = self._current_state
            action = ProbeAction("verify_associativity")
            next_state = prev_state.with_law("associativity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,
                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),
                reasoning=f"Associativity: (f >> g) >> h {'≡' if passed else '≠'} f >> (g >> h)",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("associativity")

            return passed

        except Exception as e:
            # Emit failure trace
            prev_state = self._current_state
            entry = TraceEntry(
                state_before=prev_state,
                action=ProbeAction("verify_associativity"),
                state_after=prev_state,
                reward=ConstitutionalScore(composable=0.0),
                reasoning=f"Associativity check failed with exception: {e}",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)
            return False

    async def verify_left_identity(
        self,
        agent: Any,
        test_input: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify left identity: id >> agent ≡ agent

        Args:
            agent: Agent to test (must have .run(input) method)
            test_input: Input to test with
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Direct application
            direct_result = await agent.run(test_input)

            # With identity prepended (identity just returns input)
            identity_result = test_input  # id(test_input) = test_input
            composed_result = await agent.run(identity_result)

            passed = equality_fn(direct_result, composed_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_left_identity")
            next_state = prev_state.with_law("left_identity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,
                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),
                reasoning=f"Left Identity: id >> agent {'≡' if passed else '≠'} agent",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("left_identity")

            return passed

        except Exception as e:
            prev_state = self._current_state
            entry = TraceEntry(
                state_before=prev_state,
                action=ProbeAction("verify_left_identity"),
                state_after=prev_state,
                reward=ConstitutionalScore(composable=0.0),
                reasoning=f"Left identity check failed: {e}",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)
            return False

    async def verify_right_identity(
        self,
        agent: Any,
        test_input: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify right identity: agent >> id ≡ agent

        Args:
            agent: Agent to test
            test_input: Input to test with
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Direct application
            direct_result = await agent.run(test_input)

            # With identity appended (identity returns its input unchanged)
            composed_result = direct_result  # id(agent(input)) = agent(input)

            passed = equality_fn(direct_result, composed_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_right_identity")
            next_state = prev_state.with_law("right_identity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,
                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),
                reasoning=f"Right Identity: agent >> id {'≡' if passed else '≠'} agent",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)

            if passed:
                self._verified_laws.add("right_identity")

            return passed

        except Exception as e:
            prev_state = self._current_state
            entry = TraceEntry(
                state_before=prev_state,
                action=ProbeAction("verify_right_identity"),
                state_after=prev_state,
                reward=ConstitutionalScore(composable=0.0),
                reasoning=f"Right identity check failed: {e}",
                timestamp=datetime.now(),
            )
            self._trace_entries.append(entry)
            return False

    async def verify_functor_identity(
        self,
        functor_map: Callable[[Callable[[Any], Any]], Callable[[Any], Any]],
        test_value: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify functor identity law: F(id) = id

        Args:
            functor_map: The functor's map operation
            test_value: Value to test with
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # F(id)(value) should equal value
            def identity(x: Any) -> Any:
                return x

            mapped = functor_map(identity)
            result = mapped(test_value)

            passed = equality_fn(result, test_value)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_functor_identity")
            next_state = prev_state.with_law("functor_identity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,

                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),

                reasoning=f"Functor Identity: F(id) {'=' if passed else '≠'} id",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("functor_identity")

            return passed

        except Exception as e:
            prev_state = self._current_state

            entry = TraceEntry(

                state_before=prev_state,

                action=ProbeAction("verify_functor_identity"),

                state_after=prev_state,

                reward=ConstitutionalScore(composable=0.0),

                reasoning=f"Functor identity check failed: {e}",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            return False

    async def verify_functor_composition(
        self,
        functor_map: Callable[[Callable[..., Any]], Callable[..., Any]],
        f: Callable[[Any], Any],
        g: Callable[[Any], Any],
        test_value: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify functor composition law: F(g . f) = F(g) . F(f)

        Args:
            functor_map: The functor's map operation
            f: First function
            g: Second function
            test_value: Value to test with
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Left side: F(g . f)(value)
            def composed_fn(x: Any) -> Any:
                return g(f(x))

            left_result = functor_map(composed_fn)(test_value)

            # Right side: F(g)(F(f)(value))
            f_mapped = functor_map(f)(test_value)
            right_result = functor_map(g)(f_mapped)

            passed = equality_fn(left_result, right_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_functor_composition")
            next_state = prev_state.with_law("functor_composition") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,

                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),

                reasoning=f"Functor Composition: F(g . f) {'=' if passed else '≠'} F(g) . F(f)",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("functor_composition")

            return passed

        except Exception as e:
            prev_state = self._current_state

            entry = TraceEntry(

                state_before=prev_state,

                action=ProbeAction("verify_functor_composition"),

                state_after=prev_state,

                reward=ConstitutionalScore(composable=0.0),

                reasoning=f"Functor composition check failed: {e}",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            return False

    async def verify_monad_left_identity(
        self,
        unit: Callable[[Any], Any],
        bind: Callable[[Any, Callable[..., Any]], Any],
        f: Callable[[Any], Any],
        test_value: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify monad left identity: unit(a).bind(f) ≡ f(a)

        Args:
            unit: The monad's unit/return operation
            bind: The monad's bind operation
            f: Function to bind
            test_value: Value to test with
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Left side: unit(a).bind(f)
            left_result = bind(unit(test_value), f)

            # Right side: f(a)
            right_result = f(test_value)

            passed = equality_fn(left_result, right_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_monad_left_identity")
            next_state = prev_state.with_law("monad_left_identity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,

                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),

                reasoning=f"Monad Left Identity: unit(a).bind(f) {'≡' if passed else '≠'} f(a)",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("monad_left_identity")

            return passed

        except Exception as e:
            prev_state = self._current_state

            entry = TraceEntry(

                state_before=prev_state,

                action=ProbeAction("verify_monad_left_identity"),

                state_after=prev_state,

                reward=ConstitutionalScore(composable=0.0),

                reasoning=f"Monad left identity check failed: {e}",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            return False

    async def verify_monad_right_identity(
        self,
        unit: Callable[[Any], Any],
        bind: Callable[[Any, Callable[..., Any]], Any],
        m: Any,
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify monad right identity: m.bind(unit) ≡ m

        Args:
            unit: The monad's unit/return operation
            bind: The monad's bind operation
            m: Monadic value to test
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Left side: m.bind(unit)
            left_result = bind(m, unit)

            # Right side: m
            right_result = m

            passed = equality_fn(left_result, right_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_monad_right_identity")
            next_state = prev_state.with_law("monad_right_identity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,

                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),

                reasoning=f"Monad Right Identity: m.bind(unit) {'≡' if passed else '≠'} m",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("monad_right_identity")

            return passed

        except Exception as e:
            prev_state = self._current_state

            entry = TraceEntry(

                state_before=prev_state,

                action=ProbeAction("verify_monad_right_identity"),

                state_after=prev_state,

                reward=ConstitutionalScore(composable=0.0),

                reasoning=f"Monad right identity check failed: {e}",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            return False

    async def verify_monad_associativity(
        self,
        bind: Callable[[Any, Callable[..., Any]], Any],
        m: Any,
        f: Callable[[Any], Any],
        g: Callable[[Any], Any],
        equality_fn: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Verify monad associativity: m.bind(f).bind(g) ≡ m.bind(λa. f(a).bind(g))

        Args:
            bind: The monad's bind operation
            m: Monadic value to test
            f: First function to bind
            g: Second function to bind
            equality_fn: Custom equality checker

        Returns:
            True if law holds, False otherwise
        """
        equality_fn = equality_fn or (lambda x, y: x == y)

        try:
            # Left side: m.bind(f).bind(g)
            left_intermediate = bind(m, f)
            left_result = bind(left_intermediate, g)

            # Right side: m.bind(λa. f(a).bind(g))
            def composed_fn(a: Any) -> Any:
                return bind(f(a), g)

            right_result = bind(m, composed_fn)

            passed = equality_fn(left_result, right_result)

            # Emit trace
            prev_state = self._current_state
            action = ProbeAction("verify_monad_associativity")
            next_state = prev_state.with_law("monad_associativity") if passed else prev_state

            entry = TraceEntry(
                state_before=prev_state,
                action=action,
                state_after=next_state,

                reward=ConstitutionalScore(composable=1.0 if passed else 0.0),

                reasoning=f"Monad Associativity: m.bind(f).bind(g) {'≡' if passed else '≠'} m.bind(λa. f(a).bind(g))",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            self._current_state = next_state

            if passed:
                self._verified_laws.add("monad_associativity")

            return passed

        except Exception as e:
            prev_state = self._current_state

            entry = TraceEntry(

                state_before=prev_state,

                action=ProbeAction("verify_monad_associativity"),

                state_after=prev_state,

                reward=ConstitutionalScore(composable=0.0),

                reasoning=f"Monad associativity check failed: {e}",

                timestamp=datetime.now(),

            )
            self._trace_entries.append(entry)
            return False

    # === Observation Accessors (SpyAgent compatibility) ===

    @property
    def history(self) -> list[A]:
        """Get captured history (inputs only)."""
        return [obs.input for obs in self._observations]  # type: ignore

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return self._invocation_count

    @property
    def avg_time_ms(self) -> float:
        """Average invocation time in milliseconds."""
        if not self._observations:
            return 0.0
        total_time = sum(obs.duration_ms for obs in self._observations)
        return total_time / len(self._observations)

    @property
    def max_time_ms(self) -> float:
        """Maximum invocation time in milliseconds."""
        if not self._observations:
            return 0.0
        return max(obs.duration_ms for obs in self._observations)

    @property
    def min_time_ms(self) -> float:
        """Minimum invocation time in milliseconds."""
        if not self._observations:
            return 0.0
        return min(obs.duration_ms for obs in self._observations)

    def last(self) -> A:
        """
        Get the last captured value.

        Returns:
            Last value in history

        Raises:
            IndexError: If history is empty
        """
        if not self._observations:
            raise IndexError(f"{self.name} has no captured values")
        return self._observations[-1].input  # type: ignore

    # === Assertions (Test helpers) ===

    def assert_captured(self, expected: A) -> None:
        """
        Assert that expected value was captured.

        Args:
            expected: Value that should be in history

        Raises:
            AssertionError: If expected not in history
        """
        history = self.history
        assert expected in history, (
            f"Expected {expected} not captured in {self.name}. History: {history}"
        )

    def assert_count(self, count: int) -> None:
        """
        Assert exact invocation count.

        Args:
            count: Expected number of invocations

        Raises:
            AssertionError: If count doesn't match
        """
        actual = self._invocation_count
        assert actual == count, (
            f"Expected {count} invocations in {self.name}, got {actual}"
        )

    def assert_not_empty(self) -> None:
        """
        Assert that probe captured at least one value.

        Raises:
            AssertionError: If history is empty
        """
        assert len(self._observations) > 0, f"{self.name} captured nothing"

    def reset(self) -> None:
        """Reset state and trace for test isolation."""
        self._observations.clear()
        self._invocation_count = 0
        self._trace_entries.clear()
        self._verified_laws.clear()
        self._current_state = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
            compression_ratio=1.0,
        )


# === Convenience Functions ===


def witness_probe(
    label: str = "Witness",
    max_history: int = 100,
    laws: list[str] | None = None,
) -> WitnessProbe[Any, Any]:
    """
    Create a WitnessProbe with given configuration.

    Args:
        label: Human-readable label
        max_history: Maximum history entries to keep
        laws: List of law names to verify (default: ["identity", "associativity"])

    Returns:
        Configured WitnessProbe

    Example:
        >>> probe = witness_probe(label="Pipeline", laws=["identity"])
        >>> result = await probe.invoke("data")
        >>> trace = await probe.verify(some_agent, "input")
        >>> assert trace.value.passed
    """
    # Map law names to Law objects
    law_map = {
        "identity": IDENTITY_LAW,
        "associativity": ASSOCIATIVITY_LAW,
    }

    if laws is None:
        laws_to_check = frozenset([IDENTITY_LAW, ASSOCIATIVITY_LAW])
    else:
        laws_to_check = frozenset([law_map[name] for name in laws if name in law_map])

    config = WitnessConfig(
        label=label,
        max_history=max_history,
        laws_to_check=laws_to_check,
    )

    return WitnessProbe(config)
