"""
ValueAgent[S, A, B]: DP-native agent primitive.

Every ValueAgent IS a value function. This is the core insight of the DP-native
approach: agents don't just transform inputs to outputs—they carry value functions
that justify their choices.

The Bellman Equation as Agent Semantics:

    V(s) = max_a [R(s, a) + γ · V(T(s, a))]

Where:
- V(s) is the value of being in state s
- R(s, a) is the immediate reward (from Constitution)
- γ is the discount factor (how much we care about the future)
- T(s, a) is the transition function to next state

The value function encodes optimality: V*(s) tells us the best we can do from s.
The policy π(s) = argmax_a Q(s, a) is DERIVED from the value function.

Teaching:
    gotcha: ValueAgent doesn't inherit from PolyAgent. It's a parallel primitive
            with a fundamentally different semantics: PolyAgent is operational
            (how to transform), ValueAgent is declarative (what's optimal).
            (Evidence: The value function V(s) replaces the transition function)

    gotcha: The reward function comes from Constitution, not arbitrary scoring.
            This ensures all agents optimize for the 7 kgents principles.
            (Evidence: constitution.py::Constitution.reward)

    gotcha: composition via >> uses value function composition, not just
            sequential execution. The composed value function must satisfy
            the Bellman equation for the combined MDP.
            (Evidence: dp_bridge.py::BellmanMorphism.lift_composition)

See: services/categorical/dp_bridge.py
See: dp/core/constitution.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, FrozenSet, Generic, Hashable, TypeVar

from dp.core.constitution import Constitution
from services.categorical.dp_bridge import (
    DPSolver,
    PolicyTrace,
    ProblemFormulation,
    TraceEntry,
)

logger = logging.getLogger("kgents.dp.value_agent")

# Type variables for ValueAgent structure
S = TypeVar("S", bound=Hashable)  # State (must be hashable for value function caching)
A = TypeVar("A")  # Input/Action
B = TypeVar("B")  # Output


@dataclass(frozen=True)
class ValueAgent(Generic[S, A, B]):
    """
    DP-Native Agent: Every agent IS a value function.

    V(s) = max_a [ R(s, a) + γ · V(T(s, a)) ]

    The key insight: agents don't just transform inputs to outputs.
    They carry value functions that justify their choices.

    ValueAgent is IMMUTABLE (frozen=True) for safe composition.

    Attributes:
        name: Agent identifier
        states: Valid state space (frozenset for immutability)
        actions: Function mapping state -> available actions
        transition: State transition function (s, a) -> s'
        output_fn: Function mapping (s, a, s') -> output B
        constitution: Reward function (7 principles)
        gamma: Discount factor for future value (default 0.99)

    Example:
        >>> from dp.core import Constitution
        >>> from services.categorical.dp_bridge import Principle
        >>>
        >>> # Define simple navigation agent
        >>> constitution = Constitution()
        >>> constitution.set_evaluator(
        ...     Principle.COMPOSABLE,
        ...     lambda s, a, ns: 1.0 if ns == "goal" else 0.3,
        ... )
        >>>
        >>> navigator = ValueAgent(
        ...     name="Navigator",
        ...     states=frozenset({"start", "middle", "goal"}),
        ...     actions=lambda s: frozenset({"forward", "back"}),
        ...     transition=lambda s, a: "middle" if s == "start" and a == "forward" else s,
        ...     output_fn=lambda s, a, ns: f"moved {a}",
        ...     constitution=constitution,
        ... )
        >>>
        >>> # Compute value of being in "start" state
        >>> trace = navigator.value("start")
        >>> print(f"Value: {trace.total_value():.3f}")
        >>> print(f"Optimal action: {navigator.policy('start')}")

    Teaching:
        gotcha: The output_fn is separate from transition. Transition defines
                state evolution (the MDP), output_fn defines what the agent
                returns. This separation is crucial for composition.
                (Evidence: Sequential composition needs to thread state
                 through the chain while transforming outputs)

        gotcha: Value computation uses DPSolver, which implements value iteration.
                This means the value function is computed lazily on first call,
                then cached. For large state spaces, this could be expensive.
                (Evidence: DPSolver._extract_policy_trace builds the full table)

        gotcha: The constitution is part of the agent's definition. Different
                agents can have different principle weights or evaluators,
                allowing heterogeneous optimization criteria while maintaining
                the 7-principle structure.
    """

    name: str
    states: FrozenSet[S]
    actions: Callable[[S], FrozenSet[A]]
    transition: Callable[[S, A], S]
    output_fn: Callable[[S, A, S], B]
    constitution: Constitution
    gamma: float = 0.99

    # Cached value table (computed lazily)
    _value_table: dict[S, float] = field(
        default_factory=dict, repr=False, hash=False, compare=False
    )

    # Cached solver (created lazily)
    _solver: DPSolver[S, A] | None = field(default=None, repr=False, hash=False, compare=False)

    def __post_init__(self) -> None:
        """Validate the agent's structure."""
        if not self.states:
            raise ValueError(f"ValueAgent '{self.name}' has empty state space")
        if self.gamma < 0 or self.gamma > 1:
            raise ValueError(f"Discount factor gamma must be in [0, 1], got {self.gamma}")

    def _get_solver(self) -> DPSolver[S, A]:
        """
        Get or create the DP solver for this agent.

        The solver is created lazily and cached.
        """
        cached_solver: DPSolver[S, A] | None = object.__getattribute__(self, "_solver")
        if cached_solver is not None:
            return cached_solver

        # Create problem formulation from agent structure
        formulation = ProblemFormulation(
            name=self.name,
            description=f"Value function for {self.name}",
            state_type=type(next(iter(self.states))),
            initial_states=self.states,  # All states are potential starting points
            goal_states=frozenset(),  # No explicit goal; value is relative
            available_actions=self.actions,
            transition=self.transition,
            reward=lambda s, a, ns: self.constitution.reward(s, a, ns),
        )

        solver = DPSolver(
            formulation=formulation,
            gamma=self.gamma,
        )

        # Cache the solver (mutating frozen dataclass field carefully)
        object.__setattr__(self, "_solver", solver)
        return solver

    def value(self, state: S) -> PolicyTrace[S]:
        """
        Compute optimal value at state.

        V(s) = max_a [ R(s, a) + γ · V(T(s, a)) ]

        Returns a PolicyTrace containing:
        - The final state value
        - The trace of optimal actions leading to maximum cumulative reward

        Args:
            state: The state to evaluate

        Returns:
            PolicyTrace with the optimal value and action trace

        Raises:
            ValueError: If state is not in the agent's state space
        """
        if state not in self.states:
            raise ValueError(f"State {state} not in {self.name}'s state space: {self.states}")

        # Get or compute value using solver
        solver = self._get_solver()
        optimal_value, trace = solver.solve(initial_state=state)

        # Cache the computed value
        value_table = object.__getattribute__(self, "_value_table")
        value_table[state] = optimal_value

        logger.debug(
            f"{self.name}.value({state}) = {optimal_value:.3f} with {len(trace.log)} steps"
        )

        return trace

    def policy(self, state: S) -> A | None:
        """
        Return optimal action from state.

        π(s) = argmax_a [ R(s, a) + γ · V(T(s, a)) ]

        This is the DERIVED policy from the value function.
        The policy is what we actually execute.

        Args:
            state: The state to choose an action for

        Returns:
            The optimal action, or None if no actions available

        Raises:
            ValueError: If state is not in the agent's state space
        """
        if state not in self.states:
            raise ValueError(f"State {state} not in {self.name}'s state space: {self.states}")

        available_actions = self.actions(state)
        if not available_actions:
            return None

        # Get value table (compute if needed)
        if state not in object.__getattribute__(self, "_value_table"):
            self.value(state)  # Compute and cache

        value_table = object.__getattribute__(self, "_value_table")

        # Find action that maximizes Q(s, a) = R(s, a) + γ · V(s')
        best_action: A | None = None
        best_q_value = -float("inf")

        for action in available_actions:
            next_state = self.transition(state, action)
            reward = self.constitution.reward(state, action, next_state)

            # Get or compute next state value
            if next_state not in value_table:
                self.value(next_state)

            q_value = reward + self.gamma * value_table[next_state]

            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action

        logger.debug(f"{self.name}.policy({state}) = {best_action} (Q={best_q_value:.3f})")

        return best_action

    def invoke(self, state: S, action: A | None = None) -> tuple[S, B, PolicyTrace[S]]:
        """
        Execute one step of the agent.

        If action is None, use the optimal policy π(s).
        Returns (next_state, output, trace).

        This is the operational semantics: how to actually RUN the agent.

        Args:
            state: Current state
            action: Action to take (if None, use optimal policy)

        Returns:
            Tuple of (next_state, output, trace)
                - next_state: The state after taking the action
                - output: The output produced (type B)
                - trace: PolicyTrace recording this step

        Raises:
            ValueError: If state not in state space or action not valid
        """
        if state not in self.states:
            raise ValueError(f"State {state} not in {self.name}'s state space")

        # Use policy if no action provided
        if action is None:
            action = self.policy(state)
            if action is None:
                raise ValueError(f"No valid actions from state {state}")

        # Validate action
        if action not in self.actions(state):
            raise ValueError(
                f"Action {action} not valid in state {state}. Valid actions: {self.actions(state)}"
            )

        # Execute transition
        next_state = self.transition(state, action)
        output = self.output_fn(state, action, next_state)

        # Compute reward for trace
        reward = self.constitution.reward(state, action, next_state)

        # Create trace entry
        entry = TraceEntry(
            state_before=state,
            action=str(action),
            state_after=next_state,
            value=reward,
            rationale=f"{self.name} policy execution",
        )

        trace = PolicyTrace(value=next_state, log=(entry,))

        logger.debug(
            f"{self.name}.invoke({state}, {action}) -> "
            f"({next_state}, {output}, reward={reward:.3f})"
        )

        return next_state, output, trace

    def __rshift__(self, other: ValueAgent[S, A, B]) -> ValueAgent[S, A, B]:
        """
        Sequential composition: self >> other

        The composed value function satisfies the Bellman equation:

        V_{f >> g}(s) = max_a [R_f(s,a) + γ * V_g(f(s,a))]

        Key insight: Sequential composition creates a NEW ValueAgent whose:
        - States = states of first agent (self)
        - Actions = actions of first agent (self)
        - Transition = first agent's transition
        - Reward = first agent's reward + discounted second agent's value

        The second agent's value function is incorporated into the reward,
        creating a new MDP where future value comes from the continuation.

        Args:
            other: The agent to compose with (continuation)

        Returns:
            A new ValueAgent representing the composition

        Teaching:
            gotcha: State space comes from FIRST agent only. We evaluate other's
                    value at self's next state. This requires that self's state
                    space is compatible with other's.
                    (Evidence: V_g(f(s,a)) requires f(s,a) ∈ states_g)

            gotcha: The composed reward combines R_f with V_g, not R_g.
                    This is because other's optimal value already incorporates
                    its rewards through the Bellman equation.
                    (Evidence: V_g(s') = max_a' [R_g(s',a') + γ * V_g(s'')])

            gotcha: We use self.constitution for the immediate reward, but
                    other's value function provides the future reward. This
                    maintains the compositional structure while respecting
                    each agent's optimization criteria.

            gotcha: Composition is NOT strictly associative: (f >> g) >> h ≠ f >> (g >> h).
                    This is because we capture other's value at composition time.
                    (f >> g) creates an agent with V_g baked in, then (f >> g) >> h
                    adds V_h to that. But f >> (g >> h) first creates (g >> h) with
                    V_h baked into g's continuation, giving different semantics.
                    For strict associativity, we'd need lazy evaluation chains.
                    The current design prioritizes clarity and direct Bellman semantics.
                    (Evidence: See test_composition_chains_correctly for explanation)
        """
        # Store reference to other for value computation
        # We need to capture other in the closure
        other_agent = other

        # Create a new constitution that combines self's immediate reward
        # with other's value as the future component
        def composed_reward(state: S, action: A, next_state: S) -> float:
            """
            Combined reward: R_self(s,a) + γ * V_other(next_state)

            This implements the composition formula:
            V_composed(s) = max_a [R_f(s,a) + γ * V_g(f(s,a))]
            """
            # Immediate reward from first agent
            immediate = self.constitution.reward(state, action, next_state)

            # Future value from second agent (if next_state is in other's space)
            if next_state in other_agent.states:
                future_trace = other_agent.value(next_state)
                future = future_trace.total_value()
            else:
                # If next_state not in other's space, no future value
                logger.debug(
                    f"State {next_state} not in {other_agent.name}'s space, using zero future value"
                )
                future = 0.0

            # Combine with discounting
            combined = immediate + self.gamma * future

            logger.debug(
                f"Composed reward at {state} -> {next_state}: "
                f"immediate={immediate:.3f}, future={future:.3f}, "
                f"combined={combined:.3f}"
            )

            return combined

        # Create a wrapper Constitution that returns composed reward
        class ComposedConstitution(Constitution):
            """Constitution that returns composed reward R_f + γ * V_g."""

            def reward(
                self,
                state_before: S,
                action: A,
                state_after: S,
            ) -> float:
                """Return composed reward R_f + γ * V_g."""
                return composed_reward(state_before, action, state_after)

        # Create instance and copy weights from self's constitution
        final_constitution = ComposedConstitution()
        final_constitution.principle_weights = self.constitution.principle_weights.copy()
        final_constitution.evaluators = self.constitution.evaluators.copy()
        final_constitution.evidence_generators = self.constitution.evidence_generators.copy()

        return ValueAgent(
            name=f"({self.name} >> {other.name})",
            states=self.states,  # Use first agent's state space
            actions=self.actions,  # Use first agent's actions
            transition=self.transition,  # Use first agent's transition
            output_fn=self.output_fn,  # Use first agent's output
            constitution=final_constitution,
            gamma=self.gamma,  # Keep first agent's discount
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"ValueAgent(name='{self.name}', |states|={len(self.states)}, gamma={self.gamma})"


__all__ = ["ValueAgent"]
