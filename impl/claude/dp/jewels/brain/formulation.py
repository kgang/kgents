"""
Brain Crown Jewel as DP formulation.

Brain is the spatial cathedral of memory. As a DP problem: optimal capture/recall policies.

The MDP:
    State: (memory_load, relevance_decay, query_pending)
    Actions: {CAPTURE, RECALL, FORGET, CONSOLIDATE, WAIT}
    Reward: Weighted sum of principle satisfaction
        - COMPOSABLE: memory coherence (do memories compose?)
        - GENERATIVE: compression ratio (efficient storage)
        - JOY_INDUCING: serendipity score (unexpected connections)

The Bellman Equation:
    V(s) = max_a [ R(s, a) + γ · V(T(s, a)) ]

Where:
    - V(s) is the value of being in memory state s
    - R(s, a) is the immediate reward (from Constitution)
    - γ is the discount factor (how much we care about future memory quality)
    - T(s, a) is the state transition (how memory evolves)

Teaching:
    gotcha: BrainState is frozen (immutable) for hashability. This is required
            for DP caching. All state transitions must create NEW states.
            (Evidence: ValueAgent requires S: TypeVar("S", bound=Hashable))

    gotcha: The reward function comes from Constitution, not custom scoring.
            This ensures Brain optimizes for the 7 kgents principles.
            (Evidence: dp/core/constitution.py)

    gotcha: This is a FORMULATION, not a full implementation. To use this as
            a ValueAgent, call create_brain_agent() which wires everything together.
            (Evidence: The pattern from dp/core/examples/simple_navigation.py)

See: services/brain/ (Crown Jewel implementation)
See: dp/core/value_agent.py (ValueAgent primitive)
See: dp/core/constitution.py (7 principles as reward)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle

# =============================================================================
# State Definition
# =============================================================================


@dataclass(frozen=True)
class BrainState:
    """
    State of the memory system.

    Attributes:
        memory_load: How full is memory (0.0-1.0)
        relevance_decay: How stale is recent context (0.0-1.0)
        query_pending: Is there an active query waiting?

    Teaching:
        gotcha: frozen=True makes this hashable, which is REQUIRED for DP.
                The value function needs to cache V(s), which requires s
                to be hashable for dict keys.
                (Evidence: ValueAgent._value_table is dict[S, float])

        gotcha: All fields are simple types (float, bool). Complex objects
                would need custom __hash__. Keep it simple.
    """

    memory_load: float  # 0.0 (empty) to 1.0 (full)
    relevance_decay: float  # 0.0 (fresh) to 1.0 (stale)
    query_pending: bool  # True if waiting for recall

    def __post_init__(self) -> None:
        """Validate state invariants."""
        if not (0.0 <= self.memory_load <= 1.0):
            raise ValueError(f"memory_load must be in [0, 1], got {self.memory_load}")
        if not (0.0 <= self.relevance_decay <= 1.0):
            raise ValueError(f"relevance_decay must be in [0, 1], got {self.relevance_decay}")


# =============================================================================
# Action Definition
# =============================================================================


class BrainAction(Enum):
    """
    Actions Brain can take.

    - CAPTURE: Store new memory (increases load, resets decay)
    - RECALL: Retrieve memory (rewards accuracy if query pending)
    - FORGET: Prune low-value memories (reduces load)
    - CONSOLIDATE: Compress/crystallize memories (improves coherence)
    - WAIT: Do nothing (decay increases)

    Teaching:
        gotcha: These are the ATOMIC actions. Composite strategies (like
                "capture then consolidate") are handled by policy execution,
                not by defining new action types.
    """

    CAPTURE = auto()
    RECALL = auto()
    FORGET = auto()
    CONSOLIDATE = auto()
    WAIT = auto()


# =============================================================================
# Problem Formulation
# =============================================================================


class BrainFormulation:
    """
    Brain as MDP: Optimal memory management.

    Goal: Maximize recall accuracy while managing capacity.

    Reward function:
    - COMPOSABLE: memory coherence (do memories compose?)
    - GENERATIVE: compression ratio (efficient storage)
    - JOY_INDUCING: serendipity score (unexpected connections)

    This class provides:
    1. State space enumeration (discrete grid)
    2. Action availability (state-dependent)
    3. Transition function (state evolution)
    4. Output function (what Brain returns)
    5. Constitution (principle-based rewards)

    Teaching:
        gotcha: This is not a ValueAgent itself. It's a factory for creating
                ValueAgents with Brain-specific structure. Separation of concerns:
                formulation (problem definition) vs agent (DP solver).
    """

    @staticmethod
    def generate_states(granularity: int = 5) -> FrozenSet[BrainState]:
        """
        Generate discrete state space.

        For continuous state variables, we discretize into a grid.
        Granularity controls the resolution: higher = more states = more accuracy.

        Args:
            granularity: Number of discrete values per dimension (default 5)

        Returns:
            Frozen set of all possible BrainStates

        Teaching:
            gotcha: DP requires FINITE state spaces for exact solutions.
                    With granularity=5, we get 5×5×2 = 50 states. Increasing
                    granularity improves fidelity but increases computation.
                    (Evidence: ValueAgent.value() iterates over all states)
        """
        states = set()
        step = 1.0 / (granularity - 1) if granularity > 1 else 1.0

        for i in range(granularity):
            memory_load = i * step
            for j in range(granularity):
                relevance_decay = j * step
                for query_pending in [False, True]:
                    states.add(
                        BrainState(
                            memory_load=memory_load,
                            relevance_decay=relevance_decay,
                            query_pending=query_pending,
                        )
                    )

        return frozenset(states)

    @staticmethod
    def available_actions(state: BrainState) -> FrozenSet[BrainAction]:
        """
        State-dependent action availability.

        Some actions are only valid in certain states:
        - RECALL only makes sense if query_pending
        - FORGET only makes sense if memory_load > 0
        - CONSOLIDATE only makes sense if memory_load > threshold

        Args:
            state: Current BrainState

        Returns:
            Frozen set of available actions

        Teaching:
            gotcha: This encodes domain constraints. A full memory can't CAPTURE.
                    A query-free state shouldn't RECALL. This prevents nonsensical
                    policies and guides the DP solver toward valid strategies.
        """
        actions = set()

        # WAIT is always available
        actions.add(BrainAction.WAIT)

        # CAPTURE only if not full
        if state.memory_load < 1.0:
            actions.add(BrainAction.CAPTURE)

        # RECALL only if query pending
        if state.query_pending:
            actions.add(BrainAction.RECALL)

        # FORGET only if there's something to forget
        if state.memory_load > 0.0:
            actions.add(BrainAction.FORGET)

        # CONSOLIDATE only if enough memories to consolidate
        if state.memory_load > 0.3:
            actions.add(BrainAction.CONSOLIDATE)

        return frozenset(actions)

    @staticmethod
    def transition(state: BrainState, action: BrainAction) -> BrainState:
        """
        State transition function: T(s, a) -> s'

        Defines how Brain's state evolves under each action.

        Args:
            state: Current state
            action: Action taken

        Returns:
            Next state

        Teaching:
            gotcha: Must return a NEW BrainState (frozen dataclass). Cannot
                    mutate the input state. This is enforced by frozen=True.
                    (Evidence: dataclass(frozen=True) raises FrozenInstanceError
                     on mutation attempts)

            gotcha: Transitions are deterministic (no randomness). For stochastic
                    environments, we'd need transition probabilities P(s'|s,a).
                    This is a simplification for clarity.
        """
        memory_load = state.memory_load
        relevance_decay = state.relevance_decay
        query_pending = state.query_pending

        if action == BrainAction.CAPTURE:
            # Increase load, reset decay
            memory_load = min(1.0, memory_load + 0.2)
            relevance_decay = 0.0

        elif action == BrainAction.RECALL:
            # Fulfill query, increase decay slightly
            query_pending = False
            relevance_decay = min(1.0, relevance_decay + 0.1)

        elif action == BrainAction.FORGET:
            # Reduce load, increase decay
            memory_load = max(0.0, memory_load - 0.3)
            relevance_decay = min(1.0, relevance_decay + 0.2)

        elif action == BrainAction.CONSOLIDATE:
            # Reduce load (compression), reset decay (coherence)
            memory_load = max(0.0, memory_load - 0.1)
            relevance_decay = max(0.0, relevance_decay - 0.3)

        elif action == BrainAction.WAIT:
            # Decay increases, load unchanged
            relevance_decay = min(1.0, relevance_decay + 0.15)

        # Quantize to valid state space (discretized grid)
        # This ensures transitions stay within the finite state space
        def quantize(val: float, granularity: int = 2) -> float:
            """Snap to nearest grid point."""
            if granularity <= 1:
                return max(0.0, min(1.0, val))
            step = 1.0 / (granularity - 1)
            return round(val / step) * step

        return BrainState(
            memory_load=quantize(memory_load),
            relevance_decay=quantize(relevance_decay),
            query_pending=query_pending,
        )

    @staticmethod
    def output_fn(state: BrainState, action: BrainAction, next_state: BrainState) -> str:
        """
        Output function: what Brain returns.

        This is separate from transition. Transition defines state evolution,
        output defines what the agent communicates.

        Args:
            state: State before action
            action: Action taken
            next_state: State after action

        Returns:
            Human-readable output string

        Teaching:
            gotcha: Output type can be anything (we use str for simplicity).
                    For a real Brain agent, this might return memory objects,
                    crystal IDs, or projection data.
        """
        return f"Brain: {action.name} (load {next_state.memory_load:.1f}, decay {next_state.relevance_decay:.1f})"

    @staticmethod
    def create_constitution() -> Constitution:
        """
        Create Brain-specific Constitution.

        Maps Brain actions to the 7 principles:

        - COMPOSABLE: Do memories compose coherently?
          → Reward CONSOLIDATE (builds structure)
          → Reward low decay (fresh context composes better)

        - GENERATIVE: Is storage efficient (compression)?
          → Reward CONSOLIDATE (compression)
          → Reward low load (efficient use of space)

        - JOY_INDUCING: Are unexpected connections made?
          → Reward RECALL when decay is moderate (serendipity zone)
          → Penalty FORGET (kills serendipity potential)

        Returns:
            Configured Constitution

        Teaching:
            gotcha: These evaluators are DOMAIN-SPECIFIC. Different Crown Jewels
                    would have different evaluators, but the same 7-principle
                    structure. This is the power of Constitution as abstraction.
        """
        constitution = Constitution()

        # COMPOSABLE: Coherent memory structure
        def composable_score(s: BrainState, a: BrainAction, ns: BrainState) -> float:
            score = 0.5  # neutral base
            if a == BrainAction.CONSOLIDATE:
                score = 0.9  # consolidation builds coherence
            elif a == BrainAction.CAPTURE:
                score = 0.7  # adding structured memory is good
            # Reward low decay (fresh context composes better)
            score += 0.3 * (1.0 - ns.relevance_decay)
            return min(1.0, score)

        constitution.set_evaluator(
            Principle.COMPOSABLE,
            composable_score,
            lambda s, a, ns: f"Coherence: {composable_score(s, a, ns):.2f}",
        )

        # GENERATIVE: Efficient compression
        def generative_score(s: BrainState, a: BrainAction, ns: BrainState) -> float:
            score = 0.5
            if a == BrainAction.CONSOLIDATE:
                score = 1.0  # consolidation IS compression
            elif a == BrainAction.FORGET:
                score = 0.6  # pruning helps efficiency
            # Reward low load (efficient use of space)
            score += 0.4 * (1.0 - ns.memory_load)
            return min(1.0, score)

        constitution.set_evaluator(
            Principle.GENERATIVE,
            generative_score,
            lambda s, a, ns: f"Compression: {generative_score(s, a, ns):.2f}",
        )

        # JOY_INDUCING: Serendipity from unexpected connections
        def joy_score(s: BrainState, a: BrainAction, ns: BrainState) -> float:
            score = 0.5
            if a == BrainAction.RECALL:
                # Serendipity zone: moderate decay (not too fresh, not too stale)
                if 0.3 <= s.relevance_decay <= 0.7:
                    score = 0.9  # sweet spot for unexpected connections
                else:
                    score = 0.6
            elif a == BrainAction.FORGET:
                score = 0.2  # forgetting kills serendipity potential
            elif a == BrainAction.CONSOLIDATE:
                score = 0.7  # consolidation can surface connections
            return score

        constitution.set_evaluator(
            Principle.JOY_INDUCING,
            joy_score,
            lambda s, a, ns: f"Serendipity: {joy_score(s, a, ns):.2f}",
        )

        return constitution


# =============================================================================
# Agent Factory
# =============================================================================


def create_brain_agent(
    granularity: int = 5, gamma: float = 0.95
) -> ValueAgent[BrainState, BrainAction, str]:
    """
    Create a Brain ValueAgent from the formulation.

    This is the main entry point for using Brain as a DP agent.

    Args:
        granularity: State space resolution (default 5 → 50 states)
        gamma: Discount factor for future value (default 0.95)

    Returns:
        ValueAgent configured for Brain memory management

    Example:
        >>> brain = create_brain_agent(granularity=5)
        >>> initial_state = BrainState(0.5, 0.3, True)
        >>> trace = brain.value(initial_state)
        >>> print(f"Optimal value: {trace.total_value():.3f}")
        >>> optimal_action = brain.policy(initial_state)
        >>> print(f"Optimal action: {optimal_action}")

    Teaching:
        gotcha: This wires together all the pieces: states, actions, transitions,
                outputs, and constitution. The ValueAgent handles the DP solving.
                This is the "batteries included" constructor.
    """
    formulation = BrainFormulation()

    return ValueAgent(
        name="Brain",
        states=formulation.generate_states(granularity),
        actions=formulation.available_actions,
        transition=formulation.transition,
        output_fn=formulation.output_fn,
        constitution=formulation.create_constitution(),
        gamma=gamma,
    )


__all__ = [
    "BrainState",
    "BrainAction",
    "BrainFormulation",
    "create_brain_agent",
]
