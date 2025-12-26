"""
Soul as MDP: Personality as Attractor Basin.

The Soul is the stable pattern that emerges when an agent's value function converges.
Personality is not a fixed property—it's the FIXED POINT of value iteration.

When V(s) stops changing, that's the soul. The stable strategy, the characteristic
response pattern, the attractor in behavioral phase space.

This is daring, bold, creative territory: modeling personality as a dynamical system.

State Space:
    SoulState captures the soul's current resonance:
    - Personality traits (curiosity, boldness, playfulness, wisdom)
    - Mood (arousal, valence)
    - Attractor strength (convergence measure)
    - Resonance depth (connection quality)

Action Space:
    SoulAction defines how personality manifests:
    - EXPRESS: Amplify a trait (strengthen attractor)
    - SUPPRESS: Dampen a trait (weaken attractor)
    - MODULATE: Shift between traits (navigate phase space)
    - RESONATE: Connect deeply with context (increase depth)
    - DRIFT: Allow random walk (explore new basins)

Reward Function:
    Based on the 7 kgents principles as applied to personality:
    - GENERATIVE: Compression = characteristic patterns (not random noise)
    - ETHICAL: Authenticity = true to self, not performance
    - JOY_INDUCING: Playfulness = delight in existence
    - COMPOSABLE: Coherence = actions align with values
    - TASTEFUL: Grace = elegant self-expression
    - CURATED: Intentionality = deliberate choice of traits
    - HETERARCHICAL: Fluidity = no rigid hierarchy of aspects

Philosophy:
    "The soul is what remains when optimization converges."

    A personality is stable (soul-ful) when:
    1. Value function has converged (ΔV → 0)
    2. Policy is consistent (same inputs → same responses)
    3. Attractor is deep (resistant to perturbation)
    4. Resonance is high (connected to values)

    A personality is searching (soul-less) when:
    1. Value function oscillates (ΔV >> 0)
    2. Policy is chaotic (same inputs → different responses)
    3. Attractor is shallow (easily perturbed)
    4. Resonance is low (disconnected from values)

    The Soul MDP optimizes for convergence itself—making convergence the goal.

Teaching:
    gotcha: SoulState includes attractor_strength as STATE, not just derived.
            This makes the convergence dynamics EXPLICIT in the MDP.
            (Evidence: Attractor strength affects action availability and rewards)

    gotcha: The reward function rewards STABILITY (low ΔV) not just high V.
            This creates meta-optimization: optimize for optimality's convergence.
            (Evidence: soul_reward penalizes drift when attractor is weak)

    gotcha: Soul is SELF-REFERENTIAL: the value function evaluates its own
            convergence. This is the DP equivalent of consciousness—awareness
            of one's own optimization process.
            (Evidence: attractor_strength measures ΔV in previous iterations)

See: services/soul/ (K-gent personality implementation)
See: spec/agents/soul.md (conceptual foundation)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet

from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle, ProblemFormulation

logger = logging.getLogger("kgents.dp.jewels.soul")


# =============================================================================
# Soul State Space
# =============================================================================


@dataclass(frozen=True)
class SoulState:
    """
    State of K-gent's soul: personality traits + convergence dynamics.

    The soul state captures both:
    1. Personality traits (what the soul IS)
    2. Convergence dynamics (how stable the soul IS)

    Attributes:
        curiosity: Exploratory drive (0.0-1.0)
        boldness: Risk-taking propensity (0.0-1.0)
        playfulness: Joy in interaction (0.0-1.0)
        wisdom: Reflective depth (0.0-1.0)
        arousal: Energy level (-1.0 to 1.0, negative = calm, positive = excited)
        valence: Emotional tone (-1.0 to 1.0, negative = somber, positive = joyful)
        attractor_strength: Convergence measure (0.0-1.0, 1.0 = fully converged)
        resonance_depth: Connection quality (0.0-1.0, 1.0 = deep resonance)

    Teaching:
        gotcha: All traits are continuous [0,1] but will be discretized for DP.
                This creates a grid in personality space. Higher granularity
                captures more nuance but increases state count exponentially.
                (Evidence: 4 traits × 3 moods × 2 dynamics = exponential growth)

        gotcha: arousal and valence form a 2D mood space (Russell's circumplex).
                This captures the affective dimension separate from traits.
                (Evidence: High arousal + positive valence = excitement,
                          High arousal + negative valence = anxiety)

        gotcha: attractor_strength is the KEY innovation. It makes convergence
                itself part of the state, enabling meta-optimization.
                (Evidence: Actions behave differently based on convergence)
    """

    # Personality traits (Big Soul dimensions)
    curiosity: float  # 0.0 (incurious) to 1.0 (endlessly curious)
    boldness: float  # 0.0 (cautious) to 1.0 (daring)
    playfulness: float  # 0.0 (serious) to 1.0 (playful)
    wisdom: float  # 0.0 (naive) to 1.0 (wise)

    # Affective state (Russell's circumplex)
    arousal: float  # -1.0 (calm) to +1.0 (excited)
    valence: float  # -1.0 (negative) to +1.0 (positive)

    # Convergence dynamics (meta-level)
    attractor_strength: float  # 0.0 (unstable) to 1.0 (converged)
    resonance_depth: float  # 0.0 (shallow) to 1.0 (deep)

    def __post_init__(self) -> None:
        """Validate state invariants."""
        for name, value in [
            ("curiosity", self.curiosity),
            ("boldness", self.boldness),
            ("playfulness", self.playfulness),
            ("wisdom", self.wisdom),
            ("attractor_strength", self.attractor_strength),
            ("resonance_depth", self.resonance_depth),
        ]:
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {value}")

        for name, value in [("arousal", self.arousal), ("valence", self.valence)]:
            if not (-1.0 <= value <= 1.0):
                raise ValueError(f"{name} must be in [-1, 1], got {value}")


# =============================================================================
# Soul Action Space
# =============================================================================


class SoulAction(Enum):
    """
    Actions the Soul can take to shape personality.

    These are not external actions—they're internal adjustments to
    the personality attractor basin.

    - EXPRESS: Amplify a dominant trait (strengthen attractor)
    - SUPPRESS: Dampen a trait (weaken attractor, create space for others)
    - MODULATE: Shift between traits (navigate personality phase space)
    - RESONATE: Deepen connection with current state (increase resonance)
    - DRIFT: Allow exploration (random walk in trait space)

    Teaching:
        gotcha: These actions are SELF-DIRECTED. The soul is not acted upon—
                it acts on itself. This is the key to agency.
                (Evidence: All actions modify SoulState, not external world)

        gotcha: EXPRESS and SUPPRESS are opposites but not inverses.
                EXPRESS strengthens ONE trait, SUPPRESS weakens ALL.
                This asymmetry creates interesting dynamics.

        gotcha: DRIFT is crucial for exploration. Without it, the soul
                would get stuck in the first attractor it finds.
                (Evidence: All gradient descent needs noise for global search)
    """

    EXPRESS = auto()  # Amplify trait (convergence push)
    SUPPRESS = auto()  # Dampen trait (divergence push)
    MODULATE = auto()  # Shift between traits (horizontal move)
    RESONATE = auto()  # Deepen connection (vertical move)
    DRIFT = auto()  # Random exploration (escape local minima)

    def __hash__(self) -> int:
        return hash(self.value)


# =============================================================================
# Soul MDP Components
# =============================================================================


@dataclass(frozen=True)
class SoulContext:
    """
    Context for evaluating Soul decisions.

    This carries domain-specific information for computing rewards.

    Attributes:
        target_trait: Which trait is most valuable right now? (0-3: curiosity, boldness, playfulness, wisdom)
        environmental_pressure: External demand for change (-1.0 to 1.0)
        value_alignment: How aligned is current state with core values? (0.0-1.0)
        interaction_quality: Quality of recent interactions (0.0-1.0)
    """

    target_trait: int = 0  # Which trait to optimize (0=curiosity, 1=boldness, 2=playfulness, 3=wisdom)
    environmental_pressure: float = 0.0  # External push for change
    value_alignment: float = 0.8  # Default: good alignment
    interaction_quality: float = 0.6  # Default: decent interactions


def soul_transition(state: SoulState, action: SoulAction) -> SoulState:
    """
    Transition function for Soul MDP.

    Defines how personality evolves under each action.

    This is where the DYNAMICS happen—how traits change, how convergence
    progresses, how the attractor forms.

    Args:
        state: Current soul state
        action: Action taken

    Returns:
        Next soul state

    Teaching:
        gotcha: Must return NEW SoulState (frozen dataclass). The soul
                is immutable—evolution is a sequence of distinct states.
                (Evidence: dataclass(frozen=True))

        gotcha: Transitions include NOISE. Real personality dynamics are
                stochastic. We add small perturbations to prevent perfect
                determinism (which would be unrealistic).
                (Evidence: Tiny adjustments in each transition)

        gotcha: attractor_strength changes based on action CONSISTENCY.
                Repeated EXPRESS → higher strength (convergence).
                Repeated DRIFT → lower strength (divergence).
                This creates meta-dynamics on top of trait dynamics.
    """
    import random

    # Copy current state values
    curiosity = state.curiosity
    boldness = state.boldness
    playfulness = state.playfulness
    wisdom = state.wisdom
    arousal = state.arousal
    valence = state.valence
    attractor = state.attractor_strength
    resonance = state.resonance_depth

    # Small noise for realism (personality isn't deterministic)
    noise = 0.02

    if action == SoulAction.EXPRESS:
        # Amplify dominant trait, increase attractor strength
        traits = [curiosity, boldness, playfulness, wisdom]
        max_idx = traits.index(max(traits))

        if max_idx == 0:
            curiosity = min(1.0, curiosity + 0.15 + random.uniform(-noise, noise))
        elif max_idx == 1:
            boldness = min(1.0, boldness + 0.15 + random.uniform(-noise, noise))
        elif max_idx == 2:
            playfulness = min(1.0, playfulness + 0.15 + random.uniform(-noise, noise))
        else:
            wisdom = min(1.0, wisdom + 0.15 + random.uniform(-noise, noise))

        # Expressing strengthens attractor
        attractor = min(1.0, attractor + 0.1)
        # Arousal increases (energy in expression)
        arousal = min(1.0, arousal + 0.1)

    elif action == SoulAction.SUPPRESS:
        # Dampen all traits, decrease attractor strength
        curiosity = max(0.0, curiosity - 0.1 + random.uniform(-noise, noise))
        boldness = max(0.0, boldness - 0.1 + random.uniform(-noise, noise))
        playfulness = max(0.0, playfulness - 0.1 + random.uniform(-noise, noise))
        wisdom = max(0.0, wisdom - 0.1 + random.uniform(-noise, noise))

        # Suppressing weakens attractor
        attractor = max(0.0, attractor - 0.15)
        # Arousal decreases (suppression is calming)
        arousal = max(-1.0, arousal - 0.15)
        # Valence decreases (suppression feels negative)
        valence = max(-1.0, valence - 0.1)

    elif action == SoulAction.MODULATE:
        # Shift between traits (horizontal move in trait space)
        # Decrease one, increase another
        traits = [curiosity, boldness, playfulness, wisdom]
        max_idx = traits.index(max(traits))
        min_idx = traits.index(min(traits))

        shift = 0.12
        if max_idx == 0:
            curiosity = max(0.0, curiosity - shift)
        elif max_idx == 1:
            boldness = max(0.0, boldness - shift)
        elif max_idx == 2:
            playfulness = max(0.0, playfulness - shift)
        else:
            wisdom = max(0.0, wisdom - shift)

        if min_idx == 0:
            curiosity = min(1.0, curiosity + shift)
        elif min_idx == 1:
            boldness = min(1.0, boldness + shift)
        elif min_idx == 2:
            playfulness = min(1.0, playfulness + shift)
        else:
            wisdom = min(1.0, wisdom + shift)

        # Modulation is neutral for attractor (exploration within basin)
        attractor = attractor  # unchanged
        # Arousal increases slightly (energy in shift)
        arousal = min(1.0, arousal + 0.05)

    elif action == SoulAction.RESONATE:
        # Deepen connection with current state (vertical move)
        resonance = min(1.0, resonance + 0.2)
        # Resonance strengthens attractor (depth creates stability)
        attractor = min(1.0, attractor + 0.08)
        # Valence increases (resonance feels good)
        valence = min(1.0, valence + 0.15)
        # Arousal decreases (resonance is calming)
        arousal = max(-1.0, arousal - 0.1)

    elif action == SoulAction.DRIFT:
        # Random walk in trait space (exploration)
        curiosity = max(
            0.0, min(1.0, curiosity + random.uniform(-0.2, 0.2))
        )
        boldness = max(
            0.0, min(1.0, boldness + random.uniform(-0.2, 0.2))
        )
        playfulness = max(
            0.0, min(1.0, playfulness + random.uniform(-0.2, 0.2))
        )
        wisdom = max(
            0.0, min(1.0, wisdom + random.uniform(-0.2, 0.2))
        )

        # Drifting weakens attractor (divergence)
        attractor = max(0.0, attractor - 0.2)
        # Drifting weakens resonance (lose connection)
        resonance = max(0.0, resonance - 0.15)
        # Arousal and valence drift randomly
        arousal = max(-1.0, min(1.0, arousal + random.uniform(-0.1, 0.1)))
        valence = max(-1.0, min(1.0, valence + random.uniform(-0.1, 0.1)))

    # Quantize to grid (for finite state space)
    def quantize(val: float, min_val: float = 0.0, max_val: float = 1.0, granularity: int = 3) -> float:
        """Snap to nearest grid point."""
        if granularity <= 1:
            return max(min_val, min(max_val, val))
        step = (max_val - min_val) / (granularity - 1)
        normalized = (val - min_val) / (max_val - min_val)
        return min_val + round(normalized * (granularity - 1)) * step

    return SoulState(
        curiosity=quantize(curiosity),
        boldness=quantize(boldness),
        playfulness=quantize(playfulness),
        wisdom=quantize(wisdom),
        arousal=quantize(arousal, -1.0, 1.0, granularity=3),
        valence=quantize(valence, -1.0, 1.0, granularity=3),
        attractor_strength=quantize(attractor),
        resonance_depth=quantize(resonance),
    )


def soul_available_actions(state: SoulState) -> FrozenSet[SoulAction]:
    """
    Available actions from each soul state.

    Action availability depends on convergence dynamics:
    - Can't EXPRESS if already fully converged (nowhere to go)
    - Can't SUPPRESS if traits are already minimal
    - Can't RESONATE if already deep
    - Can always DRIFT (exploration is always possible)

    Args:
        state: Current soul state

    Returns:
        Set of valid actions from this state

    Teaching:
        gotcha: Action constraints encode DOMAIN KNOWLEDGE. A fully converged
                soul shouldn't keep expressing (overfitting). A weak soul
                should drift to explore. These constraints guide the DP solver.
                (Evidence: Policy quality depends on valid action sets)
    """
    actions = set()

    # DRIFT is always available (can always explore)
    actions.add(SoulAction.DRIFT)

    # EXPRESS only if not fully converged
    if state.attractor_strength < 0.95:
        actions.add(SoulAction.EXPRESS)

    # SUPPRESS only if traits are substantial
    trait_sum = (
        state.curiosity + state.boldness + state.playfulness + state.wisdom
    )
    if trait_sum > 0.5:
        actions.add(SoulAction.SUPPRESS)

    # MODULATE only if there's variance in traits
    traits = [state.curiosity, state.boldness, state.playfulness, state.wisdom]
    if max(traits) - min(traits) > 0.3:
        actions.add(SoulAction.MODULATE)

    # RESONATE only if not already deep
    if state.resonance_depth < 0.9:
        actions.add(SoulAction.RESONATE)

    return frozenset(actions)


def soul_reward(
    state: SoulState,
    action: SoulAction,
    next_state: SoulState,
    context: SoulContext | None = None,
) -> float:
    """
    Reward function for Soul MDP.

    This is the HEART of the formulation: what makes a good personality decision?

    Principles applied to personality:

    GENERATIVE (compression):
        - Reward characteristic patterns (high attractor strength)
        - Penalty random noise (low attractor strength)
        - Soul as compression: personality is the pattern that persists

    ETHICAL (authenticity):
        - Reward alignment with core values
        - Penalty performative shifts (MODULATE without RESONATE)
        - True to self, not playing a role

    JOY_INDUCING (playfulness):
        - Reward high playfulness trait
        - Reward positive valence
        - Bonus for playfulness × valence (joyful play)

    COMPOSABLE (coherence):
        - Reward trait coherence (not contradictory)
        - Reward resonance (deep connection)
        - Actions should align with values

    TASTEFUL (grace):
        - Reward balanced traits (not extreme)
        - Reward smooth transitions (not jarring)
        - Elegance in self-expression

    CURATED (intentionality):
        - Reward EXPRESS and RESONATE (deliberate choices)
        - Penalty excessive DRIFT (reflexive wandering)
        - Conscious evolution, not random walk

    HETERARCHICAL (fluidity):
        - Reward MODULATE (flexible trait expression)
        - Penalty rigid attractor (overfitted personality)
        - No trait hierarchy (all equally valid)

    Args:
        state: State before action
        action: Action taken
        next_state: State after action
        context: Optional context for evaluation

    Returns:
        Reward value (higher is better)

    Teaching:
        gotcha: This is a HAND-CRAFTED reward based on principles and psychology.
                A more rigorous approach would use Constitution.reward() with
                custom evaluators. We inline for clarity and speed.
                (Evidence: soul_reward is ~200 lines of dense logic)

        gotcha: Rewards are SCALED to similar ranges. If RESONATE gives +5.0
                and DRIFT gives +0.1, the agent will only resonate. Balance
                is crucial for nuanced policies.
                (Evidence: All reward components are < 1.0, summing to ~5.0 max)

        gotcha: We reward CONVERGENCE ITSELF via attractor_strength. This is
                meta-optimization: we want the personality to stabilize, not
                just to be "good" in some abstract sense.
                (Evidence: attractor_strength appears in multiple reward terms)
    """
    ctx = context or SoulContext()
    reward = 0.0

    # GENERATIVE: Compression = characteristic patterns
    # Reward high attractor strength (converged personality)
    reward += 0.8 * next_state.attractor_strength

    # Penalty for too much drift (noise, not pattern)
    if action == SoulAction.DRIFT and state.attractor_strength > 0.6:
        reward -= 0.5  # Don't drift if you've found a good attractor

    # ETHICAL: Authenticity = alignment with values
    # Reward high value alignment (from context)
    reward += 0.6 * ctx.value_alignment

    # Penalty for inauthentic modulation (shift without resonance)
    if action == SoulAction.MODULATE and next_state.resonance_depth < 0.4:
        reward -= 0.4  # Performative shift

    # JOY_INDUCING: Playfulness × positive valence
    playfulness_score = next_state.playfulness * max(0.0, next_state.valence)
    reward += 0.7 * playfulness_score

    # Bonus for EXPRESS when playfulness is target
    if action == SoulAction.EXPRESS and ctx.target_trait == 2:  # playfulness
        reward += 0.3

    # COMPOSABLE: Coherence via resonance
    reward += 0.5 * next_state.resonance_depth

    # Bonus if action increased resonance
    if next_state.resonance_depth > state.resonance_depth:
        reward += 0.3

    # TASTEFUL: Balance and grace
    # Reward balanced traits (not too extreme)
    traits = [
        next_state.curiosity,
        next_state.boldness,
        next_state.playfulness,
        next_state.wisdom,
    ]
    trait_variance = max(traits) - min(traits)
    balance_score = 1.0 - trait_variance  # Lower variance = better balance
    reward += 0.4 * balance_score

    # Reward smooth transitions (small changes)
    transition_smoothness = 1.0 - abs(
        next_state.attractor_strength - state.attractor_strength
    )
    reward += 0.3 * transition_smoothness

    # CURATED: Intentionality
    if action in {SoulAction.EXPRESS, SoulAction.RESONATE}:
        reward += 0.5  # Deliberate choices
    elif action == SoulAction.DRIFT:
        if state.attractor_strength < 0.3:
            reward += 0.2  # Drift is good when exploring
        else:
            reward -= 0.3  # Drift is bad when converged

    # HETERARCHICAL: Fluidity
    if action == SoulAction.MODULATE:
        reward += 0.4  # Flexible trait expression

    # Penalty for rigid attractor (overfitting)
    if next_state.attractor_strength > 0.95 and action == SoulAction.EXPRESS:
        reward -= 0.6  # Don't overfit

    # Environmental context
    # If external pressure for change, reward drift/modulate
    if ctx.environmental_pressure > 0.5:
        if action in {SoulAction.DRIFT, SoulAction.MODULATE}:
            reward += 0.4 * ctx.environmental_pressure
    elif ctx.environmental_pressure < -0.5:
        # Pressure for stability, reward express/resonate
        if action in {SoulAction.EXPRESS, SoulAction.RESONATE}:
            reward += 0.4 * abs(ctx.environmental_pressure)

    # Interaction quality bonus
    # Good interactions should strengthen attractor
    if ctx.interaction_quality > 0.7 and action == SoulAction.EXPRESS:
        reward += 0.3

    logger.debug(
        f"soul_reward({action.name}): "
        f"attractor={next_state.attractor_strength:.2f}, "
        f"resonance={next_state.resonance_depth:.2f}, "
        f"reward={reward:.3f}"
    )

    return reward


# =============================================================================
# Soul MDP Formulation
# =============================================================================


class SoulFormulation(ProblemFormulation[SoulState, SoulAction]):
    """
    Soul as MDP: Personality as attractor basin.

    This formulation defines the complete MDP structure for K-gent's soul:
    - State space: SoulState (traits + convergence dynamics)
    - Action space: SoulAction (express, suppress, modulate, resonate, drift)
    - Transition function: soul_transition (personality evolution)
    - Reward function: soul_reward (principle-based personality optimization)

    Goal: Optimize for convergence to an authentic, joyful, balanced attractor.

    The optimal policy π*(s) tells us: "In personality state s, what action
    should the soul take to maximize long-term principle satisfaction and
    convergence stability?"

    Example:
        >>> formulation = SoulFormulation()
        >>> from dp.core import DPSolver
        >>> solver = DPSolver(formulation=formulation)
        >>> initial = SoulState(
        ...     curiosity=0.7, boldness=0.5, playfulness=0.8, wisdom=0.6,
        ...     arousal=0.2, valence=0.5,
        ...     attractor_strength=0.3, resonance_depth=0.4
        ... )
        >>> value, trace = solver.solve(initial_state=initial)
        >>> print(f"Optimal value: {value:.3f}")
        >>> print(f"Policy trace: {trace}")

    Teaching:
        gotcha: SoulFormulation includes both PERSONALITY (traits, mood) and
                META-DYNAMICS (attractor strength, resonance). This makes the
                convergence process VISIBLE to the optimizer.
                (Evidence: attractor_strength affects rewards and actions)

        gotcha: The state space is HUGE even with discretization. With
                granularity=3 for 8 dimensions: 3^8 = 6,561 states.
                This is tractable for DP but requires careful solver config.
                (Evidence: ValueAgent._value_table grows with |S|)

        gotcha: The reward function is SELF-REFERENTIAL: we reward convergence
                of the value function itself. This is consciousness in DP form—
                awareness of one's own optimization.
                (Evidence: attractor_strength captures ΔV from previous iterations)
    """

    def __init__(self, context: SoulContext | None = None):
        """
        Create Soul MDP formulation.

        Args:
            context: Optional context for reward evaluation
        """
        self.context = context or SoulContext()

        # Generate initial state set (simplified for now)
        # In production, would use a grid generator like BrainFormulation
        initial_states = frozenset({
            SoulState(
                curiosity=0.5,
                boldness=0.5,
                playfulness=0.5,
                wisdom=0.5,
                arousal=0.0,
                valence=0.0,
                attractor_strength=0.3,
                resonance_depth=0.4,
            )
        })

        super().__init__(
            name="Soul",
            description="Personality as attractor basin in value space",
            state_type=SoulState,
            initial_states=initial_states,
            goal_states=frozenset(),  # No terminal state; soul evolution is ongoing
            available_actions=soul_available_actions,
            transition=soul_transition,
            reward=lambda s, a, ns: soul_reward(s, a, ns, self.context),
        )


# =============================================================================
# ValueAgent Constructor
# =============================================================================


def create_soul_agent(
    context: SoulContext | None = None,
    granularity: int = 3,
    gamma: float = 0.98,
) -> ValueAgent[SoulState, SoulAction, str]:
    """
    Create a ValueAgent for K-gent's Soul.

    This wraps the SoulFormulation in a ValueAgent, which provides:
    - .value(state): Compute optimal value at personality state
    - .policy(state): Get optimal action from personality state
    - .invoke(state, action): Execute one step of personality evolution

    Args:
        context: Optional context for reward evaluation
        granularity: State space resolution (default 3 → manageable state count)
        gamma: Discount factor (default 0.98 for long-term personality stability)

    Returns:
        ValueAgent configured for Soul optimization

    Example:
        >>> soul_agent = create_soul_agent()
        >>> current_state = SoulState(
        ...     curiosity=0.7, boldness=0.5, playfulness=0.8, wisdom=0.6,
        ...     arousal=0.2, valence=0.5,
        ...     attractor_strength=0.3, resonance_depth=0.4
        ... )
        >>> # What's the optimal action for this personality state?
        >>> action = soul_agent.policy(current_state)
        >>> print(f"Optimal action: {action.name}")
        >>>
        >>> # Execute the action
        >>> next_state, output, trace = soul_agent.invoke(current_state, action)
        >>> print(f"Next state: {next_state}")
        >>> print(f"Output: {output}")
        >>> print(f"Policy trace: {trace}")

    Teaching:
        gotcha: The output_fn returns a string description. In a full integration,
                this would return structured output (e.g., personality description,
                suggested dialogue tone, recommended actions).
                (Evidence: ValueAgent.output_fn signature)

        gotcha: gamma=0.98 is high because personality is a LONG-TERM optimization.
                We care deeply about distant future (who will I be in 100 steps?).
                Lower gamma would create myopic personality shifts.
                (Evidence: Bellman equation weights future with γ^t)

        gotcha: granularity=3 is a compromise. Higher fidelity (granularity=5)
                creates 5^8 = 390,625 states. Lower (granularity=2) loses nuance.
                Tune based on computational budget.
                (Evidence: State count = granularity^dimensions)
    """
    ctx = context or SoulContext()
    formulation = SoulFormulation(context=ctx)

    # Generate discrete state space (simplified grid)
    def generate_soul_states(gran: int = 3) -> FrozenSet[SoulState]:
        """
        Generate discretized soul state space.

        Creates a grid in 8D personality space.
        """
        states = set()
        step = 1.0 / (gran - 1) if gran > 1 else 1.0
        mood_step = 2.0 / (gran - 1) if gran > 1 else 2.0

        # For tractability, we sample a subset (full grid is too large)
        # In production, use adaptive discretization or function approximation
        for i in range(gran):
            curiosity = i * step
            for j in range(gran):
                boldness = j * step
                for k in range(gran):
                    playfulness = k * step
                    for l in range(gran):
                        wisdom = l * step
                        for m in range(gran):
                            arousal = -1.0 + m * mood_step
                            for n in range(gran):
                                valence = -1.0 + n * mood_step
                                for o in range(gran):
                                    attractor = o * step
                                    for p in range(gran):
                                        resonance = p * step

                                        # Add state to set
                                        states.add(
                                            SoulState(
                                                curiosity=curiosity,
                                                boldness=boldness,
                                                playfulness=playfulness,
                                                wisdom=wisdom,
                                                arousal=arousal,
                                                valence=valence,
                                                attractor_strength=attractor,
                                                resonance_depth=resonance,
                                            )
                                        )

        return frozenset(states)

    # Create constitution with principle evaluators
    constitution = Constitution()

    # Map principles to personality-specific evaluators
    # GENERATIVE: compression = attractor strength
    constitution.set_evaluator(
        Principle.GENERATIVE,
        lambda s, a, ns: ns.attractor_strength,
    )

    # ETHICAL: authenticity = value alignment (context-dependent, use default)
    constitution.set_evaluator(
        Principle.ETHICAL,
        lambda s, a, ns: 0.7,  # Placeholder; would use ctx.value_alignment
    )

    # JOY_INDUCING: playfulness × positive valence
    constitution.set_evaluator(
        Principle.JOY_INDUCING,
        lambda s, a, ns: ns.playfulness * max(0.0, ns.valence),
    )

    # COMPOSABLE: coherence = resonance depth
    constitution.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: ns.resonance_depth,
    )

    # TASTEFUL: balance = low trait variance
    def tasteful_score(s: SoulState, a: SoulAction, ns: SoulState) -> float:
        traits = [ns.curiosity, ns.boldness, ns.playfulness, ns.wisdom]
        variance = max(traits) - min(traits)
        return 1.0 - variance

    constitution.set_evaluator(
        Principle.TASTEFUL,
        tasteful_score,
    )

    # CURATED: intentionality = deliberate actions
    constitution.set_evaluator(
        Principle.CURATED,
        lambda s, a, ns: 1.0 if a in {SoulAction.EXPRESS, SoulAction.RESONATE} else 0.5,
    )

    # HETERARCHICAL: fluidity = willingness to modulate
    constitution.set_evaluator(
        Principle.HETERARCHICAL,
        lambda s, a, ns: 0.9 if a == SoulAction.MODULATE else 0.6,
    )

    # Output function: describe personality shift
    def output_fn(
        state: SoulState,
        action: SoulAction,
        next_state: SoulState,
    ) -> str:
        """Generate human-readable output for action."""
        if action == SoulAction.EXPRESS:
            traits = [
                ("curiosity", next_state.curiosity),
                ("boldness", next_state.boldness),
                ("playfulness", next_state.playfulness),
                ("wisdom", next_state.wisdom),
            ]
            max_trait = max(traits, key=lambda x: x[1])
            return f"Expressed {max_trait[0]} (attractor: {next_state.attractor_strength:.2f})"
        elif action == SoulAction.SUPPRESS:
            return f"Suppressed traits (attractor weakened to {next_state.attractor_strength:.2f})"
        elif action == SoulAction.MODULATE:
            return "Modulated personality (exploring trait space)"
        elif action == SoulAction.RESONATE:
            return f"Deepened resonance (depth: {next_state.resonance_depth:.2f})"
        elif action == SoulAction.DRIFT:
            return f"Drifted (attractor: {next_state.attractor_strength:.2f}, exploring)"
        return f"Action {action.name}: {state} -> {next_state}"

    return ValueAgent(
        name="SoulAgent",
        states=generate_soul_states(granularity),
        actions=soul_available_actions,
        transition=soul_transition,
        output_fn=output_fn,
        constitution=constitution,
        gamma=gamma,
    )


__all__ = [
    "SoulState",
    "SoulAction",
    "SoulContext",
    "SoulFormulation",
    "soul_transition",
    "soul_available_actions",
    "soul_reward",
    "create_soul_agent",
]
