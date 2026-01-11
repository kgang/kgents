"""
Human Reaction Model: Transforms ideal AI actions into human-like actions.

Categorical Interpretation:
    A natural transformation: IdealAction → HumanizedAction

This model adds human-like imperfections:
- Reaction time delays (150-400ms typical)
- Aim precision noise
- Stress-induced degradation
- Fatigue over time
- Attention tunneling under pressure
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Action
    from .perception import UnifiedPercept


@dataclass
class HumanReactionModel:
    """
    Transforms ideal AI actions into human-like actions.

    Categorical interpretation: A natural transformation
        IdealAction → HumanizedAction

    The transformation preserves action type but adds realistic imperfections.
    """

    skill_level: float  # 0.0 = novice, 1.0 = pro

    # Derived parameters (set in __post_init__)
    base_reaction_ms: float = field(init=False)
    variance: float = field(init=False)

    # Dynamic state
    stress: float = field(default=0.0, init=False)
    fatigue: float = field(default=0.0, init=False)
    last_reaction_time: float = field(default=0.0, init=False)
    _action_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Initialize derived parameters from skill level."""
        # Skill affects base reaction time: 250ms (novice) to 150ms (pro)
        self.base_reaction_ms = 250 - (self.skill_level * 100)

        # Skill affects consistency: higher skill = lower variance
        self.variance = 50 * (1 - self.skill_level * 0.5)

    def humanize(self, action: Action, percept: UnifiedPercept) -> Action:
        """
        Apply human-like imperfections to ideal action.

        This is the core natural transformation:
            humanize: IdealAction × Percept → HumanizedAction
        """
        from .agent import Action as ActionClass

        # Update internal state
        self._update_stress(percept)
        self._update_fatigue()
        self._action_count += 1

        # Sample reaction time
        self.last_reaction_time = self._sample_reaction_time()

        # Apply precision noise if action requires aiming
        if action.requires_aim:
            noise = self._sample_aim_noise()
            action = action.with_noise(noise)

        # Attention filtering under high stress
        if self._attention_failure():
            return ActionClass.NONE

        return action

    def _update_stress(self, percept: UnifiedPercept) -> None:
        """Update stress level based on game situation."""
        # Stress factors
        threat_stress = percept.threat_level * 0.5
        health_stress = (100 - percept.player.get("health", 100)) / 100 * 0.3
        wave_stress = percept.wave.get("number", 1) / 20 * 0.2

        target_stress = min(1.0, threat_stress + health_stress + wave_stress)

        # Smooth stress changes (exponential moving average)
        self.stress = self.stress * 0.9 + target_stress * 0.1

    def _update_fatigue(self) -> None:
        """Update fatigue based on time played."""
        # Fatigue increases logarithmically with action count
        # Roughly: 30 minutes = 0.3 fatigue, 60 minutes = 0.5 fatigue
        import math

        actions_per_minute = 60 * 60  # Assuming ~60fps and ~1 action per second
        minutes_equivalent = self._action_count / actions_per_minute
        self.fatigue = min(0.8, 0.1 * math.log(1 + minutes_equivalent))

    def _sample_reaction_time(self) -> float:
        """
        Sample a human-like reaction time.

        Base reaction times by skill:
        - Novice: ~250ms (σ=50ms)
        - Average: ~200ms (σ=37ms)
        - Pro: ~150ms (σ=25ms)

        Modifiers:
        - Stress: +30% max
        - Fatigue: +20% max
        """
        # Sample from Gaussian
        base = max(50, random.gauss(self.base_reaction_ms, self.variance))

        # Apply stress modifier
        stress_factor = 1 + self.stress * 0.3

        # Apply fatigue modifier
        fatigue_factor = 1 + self.fatigue * 0.2

        return base * stress_factor * fatigue_factor

    def _sample_aim_noise(self) -> float:
        """
        Sample aim precision noise.

        Higher stress and fatigue = worse aim.
        Higher skill = better baseline aim.
        """
        # Base noise: 20 pixels for novice, 0 for pro
        base_noise = 20 * (1 - self.skill_level)

        # Stress increases noise
        stress_factor = 1 + self.stress * 0.5

        # Fatigue increases noise
        fatigue_factor = 1 + self.fatigue * 0.3

        noise_std = base_noise * stress_factor * fatigue_factor
        return random.gauss(0, noise_std)

    def _attention_failure(self) -> bool:
        """
        Check if attention failure occurs (tunnel vision).

        Under high stress, humans sometimes miss things entirely.
        """
        if self.stress > 0.7:
            # 10% chance of missing action under extreme stress
            failure_chance = (self.stress - 0.7) / 0.3 * 0.1
            return random.random() < failure_chance
        return False

    def humanness_score(self, action: Action) -> float:
        """
        Compute how human-like this action was.

        Used for Galois loss computation.
        """
        # Check if reaction time is in human range
        if self.last_reaction_time < 100:
            return 0.3  # Too fast - inhuman

        if self.last_reaction_time > 1000:
            return 0.5  # Too slow - inattentive

        # Ideal human range: 150-400ms
        if 150 <= self.last_reaction_time <= 400:
            return 1.0

        # Slightly outside ideal range
        if 100 <= self.last_reaction_time < 150:
            return 0.8  # Fast but possible

        if 400 < self.last_reaction_time <= 600:
            return 0.9  # Slow but normal

        return 0.7

    def reset(self) -> None:
        """Reset dynamic state for new playthrough."""
        self.stress = 0.0
        self.fatigue = 0.0
        self.last_reaction_time = 0.0
        self._action_count = 0


# Preset reaction models for different skill levels
NOVICE_REACTION = HumanReactionModel(skill_level=0.3)
AVERAGE_REACTION = HumanReactionModel(skill_level=0.5)
SKILLED_REACTION = HumanReactionModel(skill_level=0.7)
PRO_REACTION = HumanReactionModel(skill_level=0.9)
