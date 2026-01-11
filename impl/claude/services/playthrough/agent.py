"""
PlaythroughAgent: A polynomial functor for AI gameplay.

Categorical Structure:
    PlayAgent[S, A, B] = Σ(s:S) B^(A_s)

Where:
    S = Agent modes: {Strategic, Tactical, Reflexive, Observing}
    A_s = Mode-dependent inputs
    B = Unified output: (Action, DecisionTrace, WitnessData)
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

if TYPE_CHECKING:
    from .perception import UnifiedPercept
    from .reaction import HumanReactionModel
    from .witness import PlaythroughEvidence, WitnessAccumulator


class AgentMode(Enum):
    """
    Modes of the polynomial functor.

    Each mode has different input types and decision processes:
    - STRATEGIC: Long-term planning via LLM
    - TACTICAL: Short-term decisions via heuristics + small LLM
    - REFLEXIVE: Immediate reactions via pure functions
    - OBSERVING: State tracking via state machine
    """

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    REFLEXIVE = "reflexive"
    OBSERVING = "observing"


@dataclass
class AgentPersona:
    """
    A persona defines a morphism variation through the PlayAgent functor.

    Different personas explore different regions of the possibility space.
    """

    name: str
    strategic_bias: str  # "maximize_dps", "maximize_survival", "try_everything", etc.
    risk_tolerance: float  # 0.0 = very cautious, 1.0 = very aggressive
    reaction_skill: float  # 0.0 = novice, 1.0 = pro
    exploration_rate: float  # 0.0 = follows meta, 1.0 = tries everything

    def __post_init__(self) -> None:
        """Validate persona parameters."""
        assert 0.0 <= self.risk_tolerance <= 1.0
        assert 0.0 <= self.reaction_skill <= 1.0
        assert 0.0 <= self.exploration_rate <= 1.0


@dataclass
class Action:
    """
    An action in the game.

    Actions are the output type B of the polynomial functor.
    """

    type: str
    target: str | None = None
    direction: tuple[float, float] | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    # Common action types (class-level, not instance attributes)
    NONE: ClassVar["Action"]
    RETREAT: ClassVar["Action"]

    @property
    def is_attack(self) -> bool:
        return self.type in ("attack", "ability")

    @property
    def is_defensive(self) -> bool:
        return self.type in ("retreat", "dodge", "heal")

    @property
    def requires_aim(self) -> bool:
        return self.type in ("attack", "ability") and self.target is not None

    def with_noise(self, noise: float) -> Action:
        """Apply aim noise to the action."""
        if self.direction:
            dx, dy = self.direction
            return Action(
                type=self.type,
                target=self.target,
                direction=(dx + noise, dy + noise),
                parameters=self.parameters,
            )
        return self

    @classmethod
    def move(cls, direction: tuple[float, float]) -> Action:
        return cls(type="move", direction=direction)

    @classmethod
    def attack(cls, target: str) -> Action:
        return cls(type="attack", target=target)

    @classmethod
    def use_ability(cls, ability: str, target: str | None = None) -> Action:
        return cls(type="ability", target=target, parameters={"ability": ability})


# Set class-level constants
Action.NONE = Action(type="none")
Action.RETREAT = Action(type="retreat")


class LLMClient(Protocol):
    """Protocol for LLM client used in strategic decisions."""

    async def complete(self, prompt: str, max_tokens: int = 200) -> str:
        """Complete a prompt."""
        ...


class GameInterface(Protocol):
    """Protocol for game interface."""

    async def capture_screen(self) -> bytes:
        """Capture current screen."""
        ...

    async def get_debug_state(self) -> dict[str, Any]:
        """Get debug API state."""
        ...

    async def get_audio_cues(self) -> list[dict[str, Any]]:
        """Get recent audio cues."""
        ...

    async def send_action(self, action: Action) -> None:
        """Send action to game."""
        ...


@dataclass
class DecisionResult:
    """Result of a decision, including witness data."""

    action: Action
    mode: AgentMode
    reasoning: str
    confidence: float
    alternatives: list[str]
    reaction_time_ms: float


class PlaythroughAgent:
    """
    Polynomial functor: PlayAgent[Mode, Percept] → (Action, Witness)

    Implements the categorical playthrough structure for AI-driven gameplay.
    """

    def __init__(
        self,
        persona: AgentPersona,
        llm_client: LLMClient | None = None,
    ):
        self.persona = persona
        self.llm = llm_client
        self.mode = AgentMode.OBSERVING

        # Import here to avoid circular imports
        from .reaction import HumanReactionModel
        from .witness import WitnessAccumulator

        self.reaction_model = HumanReactionModel(persona.reaction_skill)
        self.witness = WitnessAccumulator()

        # Internal state for learning
        self._enemy_patterns: dict[str, list[float]] = {}
        self._last_strategic_decision: float = 0.0

    async def perceive(self, game: GameInterface) -> UnifiedPercept:
        """
        Sheaf gluing: Local observations → Global percept.

        Combines visual, API, and audio sections into unified perception.
        """
        from .perception import PerceptionSheaf

        sheaf = PerceptionSheaf()
        return await sheaf.perceive(game)

    async def decide(self, percept: UnifiedPercept) -> DecisionResult:
        """
        Polynomial application: (Mode, Percept) → (Action, Trace).

        The core decision function that selects mode and generates action.
        """
        # Select mode based on situation
        self.mode = self._select_mode(percept)

        # Apply mode-specific decision process
        match self.mode:
            case AgentMode.STRATEGIC:
                action, reasoning = await self._strategic_decision(percept)
            case AgentMode.TACTICAL:
                action, reasoning = await self._tactical_decision(percept)
            case AgentMode.REFLEXIVE:
                action, reasoning = self._reflexive_decision(percept)
            case AgentMode.OBSERVING:
                action, reasoning = Action.NONE, "Observing game state"

        # Apply human reaction model
        humanized_action = self.reaction_model.humanize(action, percept)

        # Compute confidence and alternatives
        confidence = self._compute_confidence(percept, action)
        alternatives = self._get_alternatives(percept)

        result = DecisionResult(
            action=humanized_action,
            mode=self.mode,
            reasoning=reasoning,
            confidence=confidence,
            alternatives=alternatives,
            reaction_time_ms=self.reaction_model.last_reaction_time,
        )

        # Witness the decision
        self.witness.mark_decision(result, percept)

        return result

    def _select_mode(self, percept: UnifiedPercept) -> AgentMode:
        """Select the appropriate decision mode based on situation."""
        # Reflexive: Immediate threats
        if self._has_immediate_threat(percept):
            return AgentMode.REFLEXIVE

        # Strategic: Time-based (every 30 seconds) or at upgrade opportunities
        now = time.time()
        if now - self._last_strategic_decision > 30 or percept.has_upgrade_available:
            return AgentMode.STRATEGIC

        # Tactical: Default for combat situations
        if percept.enemies:
            return AgentMode.TACTICAL

        # Observing: Nothing to do
        return AgentMode.OBSERVING

    def _has_immediate_threat(self, percept: UnifiedPercept) -> bool:
        """Check for threats requiring reflexive response."""
        # Check projectiles
        for proj in percept.projectiles:
            if proj.get("time_to_impact_ms", 1000) < 500:
                return True

        # Check very close enemies
        for enemy in percept.enemies:
            if enemy.get("distance", 1000) < 100:
                return True

        return False

    async def _strategic_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """LLM-driven strategic planning."""
        self._last_strategic_decision = time.time()

        if not self.llm:
            # Fallback to heuristic strategy
            return self._heuristic_strategy(percept)

        prompt = f"""
Game State: Wave {percept.wave.get("number", 1)}, Health {percept.player.get("health", 100)}%
Current Upgrades: {percept.player.get("upgrades", [])}
Available Upgrades: {[u.get("name") for u in percept.upgrades]}

As a {self.persona.strategic_bias} player with risk tolerance {self.persona.risk_tolerance}:
What upgrade should I pick? Respond in format: UPGRADE:<name> REASON:<brief reason>
"""

        try:
            response = await asyncio.wait_for(
                self.llm.complete(prompt, max_tokens=100),
                timeout=2.0,
            )
            return self._parse_strategic_response(response, percept)
        except (TimeoutError, Exception):
            return self._heuristic_strategy(percept)

    def _heuristic_strategy(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """Fallback heuristic strategy when LLM unavailable."""
        upgrades = percept.upgrades

        if not upgrades:
            return Action.NONE, "No upgrades available"

        # Score upgrades based on persona
        scored = []
        for upgrade in upgrades:
            score = self._score_upgrade(upgrade, percept)
            scored.append((upgrade, score))

        best = max(scored, key=lambda x: x[1])
        return (
            Action(type="select_upgrade", parameters={"upgrade": best[0].get("name")}),
            f"Selected {best[0].get('name')} (score: {best[1]:.2f})",
        )

    def _score_upgrade(self, upgrade: dict[str, Any], percept: UnifiedPercept) -> float:
        """Score an upgrade based on persona preferences."""
        name = upgrade.get("name", "").lower()
        score = 50.0  # Base score

        # Bias by persona
        if self.persona.strategic_bias == "maximize_dps":
            if any(kw in name for kw in ["damage", "attack", "pierce", "multishot"]):
                score += 30
        elif self.persona.strategic_bias == "maximize_survival":
            if any(kw in name for kw in ["health", "regen", "shield", "armor"]):
                score += 30
        elif self.persona.strategic_bias == "try_everything":
            # Prefer upgrades we haven't tried
            if name not in percept.player.get("upgrades", []):
                score += 20

        # Exploration bonus
        if random.random() < self.persona.exploration_rate:
            score += random.uniform(-20, 20)

        return float(score)

    def _parse_strategic_response(
        self, response: str, percept: UnifiedPercept
    ) -> tuple[Action, str]:
        """Parse LLM response into action."""
        # Simple parsing - look for UPGRADE: pattern
        if "UPGRADE:" in response:
            parts = response.split("UPGRADE:")
            if len(parts) > 1:
                upgrade_part = parts[1].strip()
                upgrade_name = upgrade_part.split()[0] if upgrade_part else None
                if upgrade_name:
                    return (
                        Action(type="select_upgrade", parameters={"upgrade": upgrade_name}),
                        f"LLM selected: {upgrade_name}",
                    )

        return self._heuristic_strategy(percept)

    async def _tactical_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """Heuristic-driven tactical decisions."""
        if not percept.enemies:
            return Action.NONE, "No enemies to engage"

        # Score all enemies as targets
        scored_targets = []
        for enemy in percept.enemies:
            threat = self._compute_threat(enemy, percept.player)
            value = self._compute_target_value(enemy)
            score = threat * 0.6 + value * 0.4

            # Adjust by persona
            if self.persona.strategic_bias == "maximize_dps":
                score *= 1.2 if value > threat else 0.8
            elif self.persona.strategic_bias == "maximize_survival":
                score *= 1.2 if threat > value else 0.8

            scored_targets.append((enemy, score))

        # Consider defensive action if low health
        if percept.player.get("health", 100) < 30 * (1 - self.persona.risk_tolerance):
            return Action.RETREAT, "Low health, retreating"

        # Attack highest scored target
        if scored_targets:
            best_target = max(scored_targets, key=lambda x: x[1])
            return (
                Action.attack(best_target[0].get("id", "unknown")),
                f"Attacking {best_target[0].get('type', 'enemy')} (score: {best_target[1]:.2f})",
            )

        return Action.NONE, "No valid targets"

    def _compute_threat(self, enemy: dict[str, Any], player: dict[str, Any]) -> float:
        """Compute threat level of an enemy."""
        distance = enemy.get("distance", 500)
        damage = enemy.get("damage", 10)
        health = enemy.get("health", 100)

        # Closer = more threatening
        distance_factor = max(0, 1 - distance / 500)
        # Higher damage = more threatening
        damage_factor = damage / 50
        # Higher health = harder to eliminate quickly
        health_factor = health / 200

        return float(distance_factor * 0.5 + damage_factor * 0.3 + health_factor * 0.2)

    def _compute_target_value(self, enemy: dict[str, Any]) -> float:
        """Compute value of killing an enemy."""
        xp = enemy.get("xp_value", 10)
        health = enemy.get("health", 100)

        # Higher XP = more valuable
        xp_factor = xp / 100
        # Lower health = easier kill
        ease_factor = 1 - health / 200

        return float(xp_factor * 0.6 + ease_factor * 0.4)

    def _reflexive_decision(self, percept: UnifiedPercept) -> tuple[Action, str]:
        """Pure function reflexes - no LLM needed."""
        # Check projectiles
        for proj in percept.projectiles:
            time_to_impact = proj.get("time_to_impact_ms", 1000)
            if time_to_impact < 500:
                # Compute dodge direction (perpendicular to projectile vector)
                vel = proj.get("velocity", {"x": 0, "y": 1})
                dodge_x = -vel.get("y", 0)
                dodge_y = vel.get("x", 0)
                return Action.move((dodge_x, dodge_y)), "Reflexive dodge"

        # Check very close enemies
        for enemy in percept.enemies:
            if enemy.get("distance", 1000) < 100:
                # Run away from enemy
                pos = enemy.get("position", {"x": 0, "y": 0})
                player_pos = percept.player.get("position", {"x": 0, "y": 0})
                dx = player_pos.get("x", 0) - pos.get("x", 0)
                dy = player_pos.get("y", 0) - pos.get("y", 0)
                return Action.move((dx, dy)), "Reflexive retreat from close enemy"

        return Action.NONE, "No reflex triggered"

    def _compute_confidence(self, percept: UnifiedPercept, action: Action) -> float:
        """Compute confidence in the chosen action."""
        # Base confidence from persona skill
        base = self.persona.reaction_skill * 0.5 + 0.5

        # Reduce confidence under stress
        stress = self.reaction_model.stress
        confidence = base * (1 - stress * 0.3)

        # Reduce confidence for complex decisions
        if self.mode == AgentMode.STRATEGIC:
            confidence *= 0.9

        return float(max(0.1, min(1.0, confidence)))

    def _get_alternatives(self, percept: UnifiedPercept) -> list[str]:
        """Get alternative actions that were considered."""
        alternatives = []

        if self.mode == AgentMode.TACTICAL:
            alternatives.append("retreat")
            alternatives.append("focus_weakest_enemy")
            alternatives.append("focus_strongest_enemy")

        if self.mode == AgentMode.STRATEGIC:
            for upgrade in percept.upgrades[:3]:
                alternatives.append(f"upgrade:{upgrade.get('name', 'unknown')}")

        return alternatives[:5]

    async def run_playthrough(
        self,
        game: GameInterface,
        max_waves: int = 10,
        max_duration_ms: float = 300_000,  # 5 minutes
    ) -> PlaythroughEvidence:
        """
        Run a complete playthrough and generate evidence.

        This is the main entry point for using the agent.
        """
        from .witness import PlaythroughEvidence

        start_time = time.time()
        decisions: list[DecisionResult] = []

        while True:
            # Check termination conditions
            elapsed = (time.time() - start_time) * 1000
            if elapsed > max_duration_ms:
                break

            # Perceive
            percept = await self.perceive(game)

            # Check if game over
            if percept.player.get("health", 0) <= 0:
                break

            if percept.wave.get("number", 0) > max_waves:
                break

            # Decide
            result = await self.decide(percept)
            decisions.append(result)

            # Act
            await game.send_action(result.action)

            # Small delay to match game tick rate
            await asyncio.sleep(0.016)  # ~60fps

        return self.witness.generate_evidence(
            persona=self.persona,
            decisions=decisions,
            duration_ms=(time.time() - start_time) * 1000,
        )
