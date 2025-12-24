"""
Witness as MDP: Optimal Tracing Policy.

The Witness Crown Jewel formulated as a Markov Decision Process where
the optimal policy maximizes auditability while minimizing overhead.

This is delightfully self-referential: the Witness witnesses itself via DP.
Every tracing decision is itself traced through PolicyTrace.

State Space:
    WitnessState captures the witnessing process:
    - IDLE: Not actively witnessing
    - OBSERVING: Watching for significant events
    - MARKING: Recording a mark
    - CRYSTALLIZING: Promoting marks to crystals
    - QUERYING: Retrieving past marks

Action Space:
    WitnessAction defines what the Witness can do:
    - OBSERVE: Start/continue observation
    - MARK: Emit a mark
    - SKIP: Decide event not worth marking
    - CRYSTALLIZE: Promote to crystal
    - QUERY: Search past marks

Reward Function:
    Based on the 7 kgents principles:
    - GENERATIVE: compression_ratio = insight_density / mark_count
    - ETHICAL: auditability_score = can_explain_decision(mark)
    - JOY_INDUCING: discovery_potential = unexpected_patterns(marks)
    - COMPOSABLE: trace_coherence = marks_compose_well(trace)
    - TASTEFUL: signal_noise_ratio = valuable_marks / total_marks
    - CURATED: intentionality = explicit_choices / reflexive_actions
    - HETERARCHICAL: no_fixed_hierarchy = flexibility(mark_structure)

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every DP step emits a Mark. The PolicyTrace IS the solution.
    The Witness watches itself witness, creating infinite regress
    that bottoms out in the PolicyTrace monad.

Teaching:
    gotcha: WitnessFormulation is a ProblemFormulation[WitnessState, WitnessAction].
            It defines the MDP structure, NOT the solution. The solution comes
            from DPSolver.solve().
            (Evidence: dp/core/value_agent.py::ValueAgent._get_solver)

    gotcha: The reward function evaluates (state, action, next_state) triples,
            not just states. This captures the transition dynamics: did this
            action improve auditability from this state?
            (Evidence: services/categorical/dp_bridge.py::ProblemFormulation.reward)

    gotcha: create_witness_agent() returns a ValueAgent, not just a formulation.
            ValueAgent wraps the formulation and provides .value() and .policy()
            methods for optimal decision-making.
            (Evidence: dp/core/value_agent.py::ValueAgent)

See: spec/protocols/witness-primitives.md
See: dp/core/value_agent.py
See: services/categorical/dp_bridge.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle, ProblemFormulation

logger = logging.getLogger("kgents.dp.jewels.witness")


# =============================================================================
# Witness State Space
# =============================================================================


class WitnessState(Enum):
    """
    States in the witnessing process.

    The Witness moves through these states as it observes, records,
    and crystallizes decisions.

    State transitions:
    - IDLE -> OBSERVING: Something potentially significant happens
    - OBSERVING -> MARKING: Event is worth recording
    - OBSERVING -> IDLE: Event not worth recording (SKIP action)
    - MARKING -> OBSERVING: Mark recorded, continue watching
    - MARKING -> CRYSTALLIZING: Enough marks to promote
    - CRYSTALLIZING -> OBSERVING: Crystal created, continue
    - Any -> QUERYING: Retrieve past context
    - QUERYING -> OBSERVING: Results retrieved, resume
    """

    IDLE = auto()           # Not actively witnessing
    OBSERVING = auto()      # Watching for significant events
    MARKING = auto()        # Recording a mark
    CRYSTALLIZING = auto()  # Promoting marks to crystal
    QUERYING = auto()       # Retrieving past marks

    def __hash__(self) -> int:
        return hash(self.value)


# =============================================================================
# Witness Action Space
# =============================================================================


class WitnessAction(Enum):
    """
    Actions the Witness can take.

    Each action represents a decision point in the witnessing process:
    - OBSERVE: Pay attention (low cost, enables future actions)
    - MARK: Record this event (medium cost, high value if significant)
    - SKIP: Ignore this event (no cost, but might miss important signal)
    - CRYSTALLIZE: Compress marks into insight (high cost, very high value)
    - QUERY: Search for past context (medium cost, enables better decisions)
    """

    OBSERVE = auto()        # Start/continue observation
    MARK = auto()           # Emit a mark
    SKIP = auto()           # Decide event not worth marking
    CRYSTALLIZE = auto()    # Promote to crystal
    QUERY = auto()          # Search past marks

    def __hash__(self) -> int:
        return hash(self.value)


# =============================================================================
# Witness MDP Formulation
# =============================================================================


@dataclass(frozen=True)
class WitnessContext:
    """
    Context for evaluating Witness decisions.

    This carries the domain-specific information needed to compute
    rewards for witness actions.

    Attributes:
        event_significance: How important is the current event? (0.0-1.0)
        mark_count: How many marks already exist in this session?
        insight_density: Ratio of useful information to total marks
        trace_coherence: How well do marks compose? (0.0-1.0)
        query_relevance: For QUERY actions, how relevant are results?
    """

    event_significance: float = 0.5  # Default: medium significance
    mark_count: int = 0
    insight_density: float = 0.5  # Default: neutral
    trace_coherence: float = 0.8  # Default: good coherence
    query_relevance: float = 0.5  # Default: medium relevance


def witness_transition(state: WitnessState, action: WitnessAction) -> WitnessState:
    """
    Transition function for Witness MDP.

    Defines valid state transitions based on actions.

    Args:
        state: Current witnessing state
        action: Action to take

    Returns:
        Next state after action

    Teaching:
        gotcha: This is a deterministic transition function. Stochastic
                transitions would return a probability distribution over
                next states. We keep it simple for now.
                (Evidence: services/categorical/dp_bridge.py::ProblemFormulation.transition)
    """
    if state == WitnessState.IDLE:
        if action == WitnessAction.OBSERVE:
            return WitnessState.OBSERVING
        return WitnessState.IDLE

    elif state == WitnessState.OBSERVING:
        if action == WitnessAction.MARK:
            return WitnessState.MARKING
        elif action == WitnessAction.SKIP:
            return WitnessState.IDLE
        elif action == WitnessAction.QUERY:
            return WitnessState.QUERYING
        return WitnessState.OBSERVING

    elif state == WitnessState.MARKING:
        if action == WitnessAction.CRYSTALLIZE:
            return WitnessState.CRYSTALLIZING
        elif action == WitnessAction.OBSERVE:
            return WitnessState.OBSERVING
        return WitnessState.MARKING

    elif state == WitnessState.CRYSTALLIZING:
        if action == WitnessAction.OBSERVE:
            return WitnessState.OBSERVING
        return WitnessState.CRYSTALLIZING

    elif state == WitnessState.QUERYING:
        if action == WitnessAction.OBSERVE:
            return WitnessState.OBSERVING
        return WitnessState.QUERYING

    return state


def witness_available_actions(state: WitnessState) -> FrozenSet[WitnessAction]:
    """
    Available actions from each state.

    Defines which actions are valid in each witnessing state.

    Args:
        state: Current witnessing state

    Returns:
        Set of valid actions from this state
    """
    if state == WitnessState.IDLE:
        return frozenset({WitnessAction.OBSERVE})

    elif state == WitnessState.OBSERVING:
        return frozenset({
            WitnessAction.MARK,
            WitnessAction.SKIP,
            WitnessAction.QUERY,
            WitnessAction.OBSERVE,  # Continue observing
        })

    elif state == WitnessState.MARKING:
        return frozenset({
            WitnessAction.CRYSTALLIZE,
            WitnessAction.OBSERVE,  # Return to observing
        })

    elif state == WitnessState.CRYSTALLIZING:
        return frozenset({
            WitnessAction.OBSERVE,  # Return to observing after crystallization
        })

    elif state == WitnessState.QUERYING:
        return frozenset({
            WitnessAction.OBSERVE,  # Return to observing with context
        })

    return frozenset()


def witness_reward(
    state: WitnessState,
    action: WitnessAction,
    next_state: WitnessState,
    context: WitnessContext | None = None,
) -> float:
    """
    Reward function for Witness MDP.

    Evaluates actions based on the 7 kgents principles:

    GENERATIVE (compression):
        - CRYSTALLIZE gets high reward (compression achieved)
        - MARK gets medium reward if mark_count low (building compression corpus)
        - MARK gets low/negative reward if mark_count high (too verbose)

    ETHICAL (auditability):
        - MARK gets high reward for significant events (auditable trail)
        - SKIP gets negative reward for significant events (lost auditability)

    JOY_INDUCING (discovery):
        - QUERY gets reward proportional to relevance (discovery enabled)
        - CRYSTALLIZE gets high reward (emergent insight)

    COMPOSABLE (coherence):
        - Actions that maintain trace_coherence get bonus
        - Actions that break coherence get penalty

    TASTEFUL (signal/noise):
        - MARK significant events: positive
        - MARK insignificant events: negative (noise)
        - SKIP insignificant events: positive

    CURATED (intentionality):
        - Explicit decisions (MARK, CRYSTALLIZE) get bonus
        - Reflexive actions (OBSERVE without MARK) get penalty

    HETERARCHICAL (flexibility):
        - Actions that enable future flexibility get bonus
        - Actions that constrain get penalty

    Args:
        state: State before action
        action: Action taken
        next_state: State after action
        context: Domain-specific context for evaluation

    Returns:
        Reward value (higher is better)

    Teaching:
        gotcha: This is a HAND-CRAFTED reward function based on principles.
                In a full implementation, we'd use Constitution.reward() with
                principle evaluators. This is simplified for clarity.
                (Evidence: dp/core/constitution.py::Constitution.reward)

        gotcha: Rewards should be normalized to similar scales. If CRYSTALLIZE
                gives +10.0 and MARK gives +0.1, the agent will only crystallize.
                Balance is crucial for sensible policies.
    """
    ctx = context or WitnessContext()
    reward = 0.0

    # GENERATIVE: Compression ratio
    if action == WitnessAction.CRYSTALLIZE:
        # High reward for compression (scaled by insight density)
        reward += 2.0 * ctx.insight_density
    elif action == WitnessAction.MARK:
        # Diminishing returns: fewer marks is better (compression)
        if ctx.mark_count < 5:
            reward += 0.5  # Early marks are valuable (building corpus)
        elif ctx.mark_count < 20:
            reward += 0.2  # Medium mark count: okay
        else:
            reward -= 0.3  # Too many marks: penalty for verbosity

    # ETHICAL: Auditability
    if action == WitnessAction.MARK and ctx.event_significance > 0.7:
        # Significant events MUST be marked (auditability)
        reward += 1.0 * ctx.event_significance
    elif action == WitnessAction.SKIP and ctx.event_significance > 0.7:
        # Skipping significant events loses auditability
        reward -= 1.5 * ctx.event_significance

    # JOY_INDUCING: Discovery potential
    if action == WitnessAction.QUERY:
        # Reward proportional to relevance (enables discovery)
        reward += 0.5 * ctx.query_relevance
    elif action == WitnessAction.CRYSTALLIZE:
        # Crystallization creates emergent insight (joy!)
        reward += 0.8

    # COMPOSABLE: Trace coherence
    if action in {WitnessAction.MARK, WitnessAction.CRYSTALLIZE}:
        # Actions that build coherent trace get bonus
        reward += 0.3 * ctx.trace_coherence

    # TASTEFUL: Signal-to-noise ratio
    if action == WitnessAction.MARK:
        if ctx.event_significance > 0.6:
            reward += 0.4  # Signal
        else:
            reward -= 0.6  # Noise
    elif action == WitnessAction.SKIP:
        if ctx.event_significance < 0.4:
            reward += 0.3  # Correctly filtered noise

    # CURATED: Intentionality
    if action in {WitnessAction.MARK, WitnessAction.CRYSTALLIZE, WitnessAction.SKIP}:
        # Explicit decisions get small bonus (intentional curation)
        reward += 0.2

    # HETERARCHICAL: Flexibility
    if action == WitnessAction.OBSERVE:
        # Observing maintains flexibility (no commitment yet)
        reward += 0.1
    elif action == WitnessAction.QUERY:
        # Querying increases context (enables better decisions)
        reward += 0.2

    # State-specific penalties
    if state == WitnessState.IDLE and action != WitnessAction.OBSERVE:
        # Can't do much from IDLE except observe
        reward -= 1.0

    logger.debug(
        f"reward({state.name}, {action.name}, {next_state.name}) = {reward:.3f}"
    )

    return reward


class WitnessFormulation(ProblemFormulation[WitnessState, WitnessAction]):
    """
    Witness as MDP: Optimal tracing policy.

    This formulation defines the complete MDP structure for the Witness:
    - State space: WitnessState enum
    - Action space: WitnessAction enum
    - Transition function: witness_transition
    - Reward function: witness_reward (principle-based)

    Goal: Maximize auditability while minimizing trace overhead.

    The optimal policy π*(s) tells us: "In state s, what action should
    the Witness take to maximize long-term principle satisfaction?"

    Example:
        >>> formulation = WitnessFormulation()
        >>> from dp.core import DPSolver
        >>> solver = DPSolver(formulation=formulation)
        >>> value, trace = solver.solve(initial_state=WitnessState.IDLE)
        >>> print(f"Optimal value: {value:.3f}")
        >>> print(f"Policy trace: {trace}")

    Teaching:
        gotcha: WitnessFormulation is frozen (immutable). This enables safe
                composition and caching in DPSolver. To modify, create a new
                formulation with updated parameters.
                (Evidence: dataclass(frozen=True))

        gotcha: The reward function is stateless (pure function of state/action).
                If you need context (event significance, mark count), pass it
                through WitnessContext or encode it in the state.
                (Evidence: witness_reward signature)
    """

    def __init__(self, context: WitnessContext | None = None):
        """
        Create Witness MDP formulation.

        Args:
            context: Optional context for reward evaluation
        """
        self.context = context or WitnessContext()

        super().__init__(
            name="Witness",
            description="Optimal tracing policy for the Witness Crown Jewel",
            state_type=WitnessState,
            initial_states=frozenset({WitnessState.IDLE}),
            goal_states=frozenset(),  # No terminal state; witnessing is ongoing
            available_actions=witness_available_actions,
            transition=witness_transition,
            reward=lambda s, a, ns: witness_reward(s, a, ns, self.context),
        )


# =============================================================================
# ValueAgent Constructor
# =============================================================================


def create_witness_agent(
    context: WitnessContext | None = None,
    gamma: float = 0.95,
) -> ValueAgent[WitnessState, WitnessAction, str]:
    """
    Create a ValueAgent for the Witness Crown Jewel.

    This wraps the WitnessFormulation in a ValueAgent, which provides:
    - .value(state): Compute optimal value at state
    - .policy(state): Get optimal action from state
    - .invoke(state, action): Execute one step

    Args:
        context: Optional context for reward evaluation
        gamma: Discount factor (default 0.95 for near-term focus)

    Returns:
        ValueAgent configured for Witness optimization

    Example:
        >>> agent = create_witness_agent()
        >>> # What's the optimal action from OBSERVING state?
        >>> action = agent.policy(WitnessState.OBSERVING)
        >>> print(f"Optimal action: {action.name}")
        >>>
        >>> # Execute the action
        >>> next_state, output, trace = agent.invoke(
        ...     WitnessState.OBSERVING,
        ...     action
        ... )
        >>> print(f"Next state: {next_state.name}")
        >>> print(f"Policy trace: {trace}")

    Teaching:
        gotcha: The output_fn returns a string description of the action.
                In a full integration, this would return a structured output
                (e.g., the Mark object created, the Crystal ID, etc.).
                (Evidence: ValueAgent.output_fn signature)

        gotcha: gamma=0.95 is lower than the typical 0.99 because witnessing
                is a near-term task. We care more about immediate decisions
                (mark this event?) than distant future (what happens 100 steps
                from now?). Adjust based on your planning horizon.
    """
    ctx = context or WitnessContext()
    formulation = WitnessFormulation(context=ctx)

    # Create constitution with principle evaluators
    constitution = Constitution()

    # Map principles to reward components
    # GENERATIVE: compression ratio
    constitution.set_evaluator(
        Principle.GENERATIVE,
        lambda s, a, ns: 1.0 if a == WitnessAction.CRYSTALLIZE else 0.3,
    )

    # ETHICAL: auditability
    constitution.set_evaluator(
        Principle.ETHICAL,
        lambda s, a, ns: 1.0 if a == WitnessAction.MARK else 0.5,
    )

    # JOY_INDUCING: discovery
    constitution.set_evaluator(
        Principle.JOY_INDUCING,
        lambda s, a, ns: 0.8 if a in {WitnessAction.CRYSTALLIZE, WitnessAction.QUERY} else 0.4,
    )

    # COMPOSABLE: trace coherence (always good for Witness)
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 0.8,  # Witness maintains composable traces
    )

    # TASTEFUL: signal-to-noise
    constitution.set_evaluator(
        Principle.TASTEFUL,
        lambda s, a, ns: 0.7,  # Hand-tuned in witness_reward
    )

    # CURATED: intentionality
    constitution.set_evaluator(
        Principle.CURATED,
        lambda s, a, ns: 1.0 if a != WitnessAction.OBSERVE else 0.5,
    )

    # HETERARCHICAL: flexibility (Witness is inherently heterarchical)
    constitution.set_evaluator(
        Principle.HETERARCHICAL,
        lambda s, a, ns: 0.9,
    )

    # Output function: describe what the action does
    def output_fn(
        state: WitnessState,
        action: WitnessAction,
        next_state: WitnessState,
    ) -> str:
        """Generate human-readable output for action."""
        if action == WitnessAction.OBSERVE:
            return f"Observing from {state.name}"
        elif action == WitnessAction.MARK:
            return f"Marked event (now in {next_state.name})"
        elif action == WitnessAction.SKIP:
            return f"Skipped event (returning to {next_state.name})"
        elif action == WitnessAction.CRYSTALLIZE:
            return f"Crystallized marks into insight (now in {next_state.name})"
        elif action == WitnessAction.QUERY:
            return f"Querying past context (now in {next_state.name})"
        return f"Action {action.name}: {state.name} -> {next_state.name}"

    return ValueAgent(
        name="WitnessAgent",
        states=frozenset(WitnessState),
        actions=witness_available_actions,
        transition=witness_transition,
        output_fn=output_fn,
        constitution=constitution,
        gamma=gamma,
    )


__all__ = [
    "WitnessState",
    "WitnessAction",
    "WitnessContext",
    "WitnessFormulation",
    "witness_transition",
    "witness_available_actions",
    "witness_reward",
    "create_witness_agent",
]
