"""
Hypha - The Agent as Growing Tip.

A hypha is a thread of a fungal mycelium. It:
- Grows towards nutrients (reward)
- Grows towards information (uncertainty reduction)
- Dies back when exploration yields nothing
- Connects to other hyphae at nodes (synchronization)

This replaces the traditional "Agent" abstraction entirely
with a biologically-inspired, Active Inference-driven entity.

Mathematical Foundation:
- Active Inference: minimize F = Complexity + Inaccuracy
- Exploration driven by surprise
- Exploitation driven by reward under low surprise
- Pruning when neither exploration nor exploitation yields value
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from ..field.hdc_ops import DIMENSIONS
from ..field.holographic import HolographicField
from ..weave.event import Event
from ..weave.weave import TheWeave
from .foraging import DEFAULT_POLICY, ForageAction, ForagingPolicy, ForagingResult
from .free_energy import FreeEnergyState, GenerativeModel, Vector


@dataclass
class HyphaConfig:
    """
    Configuration for a Hypha.

    Attributes:
        exploration_rate: Base probability of exploring vs exploiting
        pruning_threshold: Free energy below which to prune
        learning_rate: Rate for generative model updates
        imprint_strength: Strength for holographic field imprints
    """

    exploration_rate: float = 0.3
    pruning_threshold: float = 0.1
    learning_rate: float = 0.1
    imprint_strength: float = 1.0
    dimensions: int = DIMENSIONS


@dataclass
class Hypha:
    """
    The Agent as a Growing Tip (Hyphal Network Metaphor).

    A hypha is a thread of a fungal mycelium. It:
    - Grows towards nutrients (reward)
    - Grows towards information (uncertainty reduction)
    - Dies back when exploration yields nothing
    - Connects to other hyphae at nodes (synchronization)

    This replaces the "Agent" abstraction entirely.

    Attributes:
        id: Unique identifier
        name: Human-readable name
        weave: The concurrent history (Trace Monoid)
        hologram: The shared holographic field
        generative_model: Internal predictive model
        config: Configuration parameters
    """

    id: str
    name: str

    # State
    weave: TheWeave = field(default_factory=TheWeave)
    hologram: HolographicField | None = None

    # Active Inference
    generative_model: GenerativeModel = field(init=False)
    free_energy_state: FreeEnergyState | None = None

    # Configuration
    config: HyphaConfig = field(default_factory=HyphaConfig)

    # Foraging policy
    policy: ForagingPolicy = field(default_factory=lambda: DEFAULT_POLICY)

    # Lifecycle state
    is_active: bool = True
    forage_count: int = 0
    explore_count: int = 0
    exploit_count: int = 0
    prune_count: int = 0

    def __post_init__(self) -> None:
        """Initialize generative model."""
        self.generative_model = GenerativeModel(dimensions=self.config.dimensions)

    async def forage(
        self,
        observation: Vector | None = None,
        context: Vector | None = None,
        reward_estimator: Callable[[Any], float] | None = None,
    ) -> ForagingResult:
        """
        Active Inference Loop.

        1. PREDICT: Generate expected observation from model
        2. SENSE: Use provided observation (or zeros)
        3. ERROR: Compute prediction error (Free Energy)
        4. ACT: Choose action based on error

        This is the core "heartbeat" of the Hypha.

        Args:
            observation: The actual observation (optional)
            context: Context for prediction (optional)
            reward_estimator: Function to estimate reward (optional)

        Returns:
            ForagingResult describing what happened
        """
        if not self.is_active:
            # Pruned hyphae don't forage
            return ForagingResult(
                action=ForageAction.PRUNE,
                free_energy_before=0.0,
                free_energy_after=None,
                surprise=0.0,
                reward=0.0,
                pruned=True,
            )

        # 1. PREDICT
        ctx = context if context is not None else self._encode_context()
        expected = self.generative_model.predict(ctx)

        # 2. SENSE
        actual = (
            observation if observation is not None else np.zeros(self.config.dimensions)
        )

        # 3. ERROR
        self.free_energy_state = FreeEnergyState(
            expected_observation=expected,
            actual_observation=actual,
            complexity=self.generative_model.complexity,
        )

        fe_before = self.free_energy_state.free_energy
        surprise = self.free_energy_state.normalized_surprise

        # 4. ACT
        reward = 0.0
        if reward_estimator is not None:
            reward = reward_estimator(actual)

        action = self.policy.select_action(self.free_energy_state, reward)

        self.forage_count += 1

        # Execute action
        result = ForagingResult(
            action=action,
            free_energy_before=fe_before,
            free_energy_after=None,
            surprise=surprise,
            reward=reward,
        )

        if action == ForageAction.EXPLORE:
            await self._explore(ctx, actual)
            result.branched = True
            self.explore_count += 1

        elif action == ForageAction.EXPLOIT:
            await self._exploit(ctx, actual)
            result.imprinted = True
            self.exploit_count += 1

        elif action == ForageAction.PRUNE:
            await self._prune()
            result.pruned = True
            self.prune_count += 1

        # Compute free energy after action (if still active)
        if self.is_active and self.free_energy_state is not None:
            result = ForagingResult(
                action=result.action,
                free_energy_before=result.free_energy_before,
                free_energy_after=self.free_energy_state.free_energy,
                surprise=result.surprise,
                reward=result.reward,
                imprinted=result.imprinted,
                branched=result.branched,
                pruned=result.pruned,
            )

        return result

    async def _explore(self, context: Vector, actual: Vector) -> None:
        """
        Branch the Weave (create new exploration thread).

        This is void.entropy.sip in the new ontology-
        drawing from the accursed share to explore.
        """
        # Record branch event in Weave
        await self.weave.record(
            content={
                "action": "explore",
                "surprise": self.free_energy_state.surprise
                if self.free_energy_state
                else 0,
            },
            source=self.id,
        )

        # Update generative model with surprise
        self.generative_model.update(
            context,
            actual,
            learning_rate=self.config.learning_rate,
        )

    async def _exploit(self, context: Vector, actual: Vector) -> None:
        """
        Consolidate learning (imprint to global field).

        This is void.entropy.pour in the new ontology-
        returning information to the collective.
        """
        # Imprint successful pattern to global hologram
        if self.hologram is not None:
            success_pattern = self.hologram.encode_structure(
                {
                    "hypha": self.id,
                    "action": "success",
                }
            )
            self.hologram.imprint(
                success_pattern, strength=self.config.imprint_strength
            )

        # Record in Weave
        await self.weave.record(
            content={"action": "exploit", "imprinted": self.hologram is not None},
            source=self.id,
        )

        # Update model (reinforce)
        self.generative_model.update(
            context,
            actual,
            learning_rate=self.config.learning_rate * 0.5,  # Slower for exploitation
        )

    async def _prune(self) -> None:
        """
        Die back (release resources).

        This is the Accursed Share in action-information
        that yields no reduction in Free Energy must be
        discharged.
        """
        # Record pruning in Weave
        await self.weave.record(
            content={"action": "prune", "reason": "no_nutrients"},
            source=self.id,
        )

        # Mark as inactive
        self.is_active = False

    def _encode_context(self) -> Vector:
        """
        Encode current context as holographic vector.

        Uses recent events from the Weave.
        """
        recent_events = list(self.weave.monoid.events[-10:])  # Last 10 events

        if not recent_events:
            return np.zeros(self.config.dimensions)

        if self.hologram is None:
            # Without hologram, just return random vector
            return np.random.randn(self.config.dimensions)

        event_vectors: list[Vector] = []
        for e in recent_events:
            vec = self.hologram.encode_structure(
                {
                    "event": e.id,
                    "source": e.source,
                }
            )
            event_vectors.append(vec)

        # Permute by position for sequence encoding
        positioned = [self.hologram.permute(v, i) for i, v in enumerate(event_vectors)]

        result: Vector = self.hologram.bundle(positioned)
        return result

    def resonate(self, pattern: Vector) -> float:
        """
        Measure resonance with the global field.

        This is "Morphic Resonance"-how familiar is this
        pattern to the collective memory?

        Args:
            pattern: Pattern to check resonance for

        Returns:
            Similarity score in [-1, 1]
        """
        if self.hologram is None:
            return 0.0
        result: float = self.hologram.resonate(pattern)
        return result

    @property
    def vitality(self) -> float:
        """
        Measure of the Hypha's vitality.

        Based on forage success rate.
        """
        if self.forage_count == 0:
            return 1.0

        success_rate = (self.explore_count + self.exploit_count) / self.forage_count
        return success_rate

    def reset(self) -> None:
        """Reset the Hypha to initial state."""
        self.generative_model.reset()
        self.free_energy_state = None
        self.is_active = True
        self.forage_count = 0
        self.explore_count = 0
        self.exploit_count = 0
        self.prune_count = 0


# Factory functions


def create_hypha(
    hypha_id: str,
    name: str,
    hologram: HolographicField | None = None,
    config: HyphaConfig | None = None,
) -> Hypha:
    """
    Create a new Hypha.

    Args:
        hypha_id: Unique identifier
        name: Human-readable name
        hologram: Optional shared holographic field
        config: Optional configuration

    Returns:
        New Hypha instance
    """
    return Hypha(
        id=hypha_id,
        name=name,
        hologram=hologram,
        config=config or HyphaConfig(),
    )


def create_hypha_colony(
    names: list[str],
    shared_hologram: HolographicField | None = None,
    config: HyphaConfig | None = None,
) -> list[Hypha]:
    """
    Create a colony of Hyphae sharing a holographic field.

    Args:
        names: Names for each hypha
        shared_hologram: Shared holographic field
        config: Configuration for all hyphae

    Returns:
        List of Hypha instances
    """
    return [
        create_hypha(
            hypha_id=f"hypha-{i}",
            name=name,
            hologram=shared_hologram,
            config=config,
        )
        for i, name in enumerate(names)
    ]
