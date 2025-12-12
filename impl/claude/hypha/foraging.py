"""
Foraging - Action Selection Based on Free Energy.

The Hypha forages through semantic space, choosing actions
based on the Free Energy landscape:

- EXPLORE: High surprise -> branch out into new territory
- EXPLOIT: Low surprise, high reward -> consolidate gains
- PRUNE: Low surprise, low reward -> die back, release resources
- WAIT: Uncertain -> gather more data before acting

This implements the Active Inference loop:
1. PREDICT: Generate expected observation from model
2. SENSE: Sample the world
3. ERROR: Compute prediction error (Free Energy)
4. ACT: Choose action based on error
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

from .free_energy import FreeEnergyState


class ForageAction(Enum):
    """
    Actions the Hypha can take based on Free Energy.

    - EXPLORE: High surprise -> branch out
    - EXPLOIT: Low surprise, high reward -> consolidate
    - PRUNE: Low surprise, low reward -> die back
    - WAIT: Uncertain -> gather more data
    """

    EXPLORE = auto()
    EXPLOIT = auto()
    PRUNE = auto()
    WAIT = auto()


@dataclass
class ForagingPolicy:
    """
    Policy for choosing forage actions.

    Configurable thresholds for action selection based on
    surprise (normalized to [0, 1]) and reward.

    Attributes:
        explore_threshold: Surprise above this -> EXPLORE
        prune_threshold: Surprise below this, check reward
        exploit_reward_threshold: Reward above this -> EXPLOIT
    """

    explore_threshold: float = 0.7
    prune_threshold: float = 0.2
    exploit_reward_threshold: float = 0.5

    def select_action(
        self,
        state: FreeEnergyState,
        reward: float,
    ) -> ForageAction:
        """
        Select action based on free energy state and reward.

        Decision tree:
        1. If surprise > explore_threshold -> EXPLORE
        2. If surprise < prune_threshold:
           a. If reward > exploit_reward_threshold -> EXPLOIT
           b. Else -> PRUNE
        3. Else -> WAIT

        Args:
            state: Current free energy state
            reward: Estimated reward from current state

        Returns:
            ForageAction to take
        """
        surprise = state.normalized_surprise

        if surprise > self.explore_threshold:
            return ForageAction.EXPLORE

        if surprise < self.prune_threshold:
            if reward > self.exploit_reward_threshold:
                return ForageAction.EXPLOIT
            else:
                return ForageAction.PRUNE

        return ForageAction.WAIT


@dataclass
class ForagingResult:
    """
    Result of a foraging step.

    Captures what happened during one forage cycle.

    Attributes:
        action: The action taken
        free_energy_before: Free energy before action
        free_energy_after: Free energy after action
        surprise: Surprise that triggered action
        reward: Reward observed
        imprinted: Whether we imprinted to global field
        branched: Whether we branched (explore)
        pruned: Whether we pruned (die back)
    """

    action: ForageAction
    free_energy_before: float
    free_energy_after: float | None
    surprise: float
    reward: float
    imprinted: bool = False
    branched: bool = False
    pruned: bool = False

    @property
    def free_energy_delta(self) -> float | None:
        """Change in free energy (negative is good)."""
        if self.free_energy_after is None:
            return None
        return self.free_energy_after - self.free_energy_before

    @property
    def improved(self) -> bool:
        """Whether free energy decreased."""
        delta = self.free_energy_delta
        if delta is None:
            return False
        return delta < 0


# Default policy
DEFAULT_POLICY = ForagingPolicy()


def select_forage_action(
    state: FreeEnergyState,
    reward: float,
    policy: ForagingPolicy | None = None,
) -> ForageAction:
    """
    Select forage action given state and reward.

    Convenience function that uses default policy if none provided.

    Args:
        state: Current free energy state
        reward: Estimated reward
        policy: Optional custom policy

    Returns:
        ForageAction to take
    """
    p = policy or DEFAULT_POLICY
    return p.select_action(state, reward)
