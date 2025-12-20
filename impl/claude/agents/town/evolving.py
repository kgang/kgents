"""
EvolvingCitizen: Citizens that grow via SENSE → ACT → REFLECT.

Extends Citizen with the ability to evolve through compressed N-Phase cycles.
Eigenvectors drift over time (bounded), cosmotechnics have high inertia.

Pattern source: protocols/nphase/operad.py (SENSE/ACT/REFLECT)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from agents.town.citizen import Citizen, Cosmotechnics, Eigenvectors
from agents.town.memory import GraphMemory
from protocols.nphase.operad import NPhase

# =============================================================================
# Growth Types
# =============================================================================


class GrowthTrigger(Enum):
    """Triggers that can initiate evolution."""

    SURPLUS = auto()  # accursed_surplus > threshold
    RELATIONSHIP = auto()  # relationship milestone reached
    WITNESS = auto()  # witnessed significant event
    TIME = auto()  # enough time has passed
    MANUAL = auto()  # explicitly triggered


@dataclass
class Observation:
    """An observation from the world (SENSE input)."""

    content: str
    source: str  # Who/what was observed
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_weight: float = 0.0  # -1.0 to 1.0 (negative/positive)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SensedState:
    """Result of SENSE phase: filtered observation through worldview."""

    observation: Observation
    interpretation: str  # How citizen interprets it
    relevance: float  # 0.0-1.0: how relevant to citizen
    eigenvector_activation: dict[str, float]  # Which eigenvectors activated
    phase: NPhase = NPhase.SENSE


@dataclass
class ActionResult:
    """Result of ACT phase: action taken based on sensed state."""

    action_type: str  # e.g., "greet", "trade", "reflect"
    success: bool
    effect: str  # Description of what happened
    relationship_delta: dict[str, float]  # Changes to relationships
    surplus_delta: float = 0.0  # Change to accursed surplus
    phase: NPhase = NPhase.ACT


@dataclass
class Reflection:
    """Result of REFLECT phase: integrated learning."""

    insight: str  # What was learned
    eigenvector_deltas: dict[str, float]  # Proposed changes
    applied_deltas: dict[str, float]  # Actually applied (bounded)
    growth_occurred: bool
    phase: NPhase = NPhase.REFLECT


@dataclass
class GrowthState:
    """Accumulated state during evolution cycle."""

    observations: list[Observation] = field(default_factory=list)
    actions_taken: list[ActionResult] = field(default_factory=list)
    reflections: list[Reflection] = field(default_factory=list)
    cycle_count: int = 0
    last_evolution: datetime | None = None


# =============================================================================
# Evolution Cosmotechnics (for experimental citizens)
# =============================================================================


GROWTH = Cosmotechnics(
    name="growth",
    description="Meaning arises through becoming",
    metaphor="Life is growth",
    opacity_statement="There are transformations I undergo alone.",
)

ADAPTATION = Cosmotechnics(
    name="adaptation",
    description="Meaning arises through fitting",
    metaphor="Life is adaptation",
    opacity_statement="There are shapes I take that you cannot see.",
)

SYNTHESIS = Cosmotechnics(
    name="synthesis",
    description="Meaning arises through integration",
    metaphor="Life is synthesis",
    opacity_statement="There are wholes I build from fragments you cannot perceive.",
)


# =============================================================================
# EvolvingCitizen
# =============================================================================


@dataclass
class EvolvingCitizen(Citizen):
    """
    A citizen that evolves via compressed SENSE → ACT → REFLECT.

    Evolution changes eigenvectors within bounded drift.
    Cosmotechnics have high inertia (change very slowly).

    The evolution cycle:
    1. SENSE: Observe and filter through worldview
    2. ACT: Take action based on perception
    3. REFLECT: Integrate experience, update self-model
    """

    # Evolution state
    growth_state: GrowthState = field(default_factory=GrowthState)
    evolution_count: int = 0
    max_eigenvector_drift: float = 0.1  # Max change per cycle per dimension
    cosmotechnics_inertia: float = 0.95  # How resistant to worldview change

    # Graph memory for rich recall
    graph_memory: GraphMemory = field(default_factory=GraphMemory)

    # Evolution thresholds
    surplus_threshold: float = 5.0  # Trigger evolution when surplus exceeds
    relationship_milestone: float = 0.8  # Trigger when relationship hits this

    def __post_init__(self) -> None:
        """Initialize evolution state."""
        super().__post_init__()
        if self.growth_state.last_evolution is None:
            self.growth_state.last_evolution = datetime.now()

    # =========================================================================
    # SENSE Phase
    # =========================================================================

    async def sense(self, observation: Observation) -> SensedState:
        """
        SENSE phase: Perceive the world through cosmotechnics lens.

        The observation is filtered through the citizen's worldview.
        Different citizens interpret the same observation differently.
        """
        # Filter observation through cosmotechnics
        interpretation = self._interpret_observation(observation)

        # Calculate relevance based on eigenvectors
        relevance = self._calculate_relevance(observation)

        # Determine which eigenvectors are activated
        activation = self._get_eigenvector_activation(observation)

        # Store observation
        self.growth_state.observations.append(observation)

        # Store in graph memory
        self.graph_memory.store(
            key=f"sense_{len(self.growth_state.observations)}",
            content=f"{observation.source}: {observation.content}",
            metadata={"phase": "sense", "relevance": relevance},
        )

        return SensedState(
            observation=observation,
            interpretation=interpretation,
            relevance=relevance,
            eigenvector_activation=activation,
        )

    def _interpret_observation(self, obs: Observation) -> str:
        """Interpret observation through cosmotechnics lens."""
        # Different cosmotechnics interpret differently
        match self.cosmotechnics.name:
            case "growth":
                return f"Opportunity for growth: {obs.content}"
            case "adaptation":
                return f"Environmental signal: {obs.content}"
            case "synthesis":
                return f"Fragment to integrate: {obs.content}"
            case _:
                return f"Observed: {obs.content}"

    def _calculate_relevance(self, obs: Observation) -> float:
        """Calculate how relevant observation is to this citizen."""
        # Base relevance on emotional weight and eigenvector alignment
        base = 0.5

        # Curious citizens find more things relevant
        base += (self.eigenvectors.curiosity - 0.5) * 0.3

        # Emotional observations are more relevant
        base += abs(obs.emotional_weight) * 0.2

        return max(0.0, min(1.0, base))

    def _get_eigenvector_activation(self, obs: Observation) -> dict[str, float]:
        """Determine which eigenvectors are activated by observation."""
        activation: dict[str, float] = {}

        # Positive observations activate warmth, trust
        if obs.emotional_weight > 0:
            activation["warmth"] = obs.emotional_weight * 0.5
            activation["trust"] = obs.emotional_weight * 0.3

        # Novel observations activate curiosity
        if "new" in obs.content.lower() or "discover" in obs.content.lower():
            activation["curiosity"] = 0.4

        # Challenging observations activate patience
        if "difficult" in obs.content.lower() or "challenge" in obs.content.lower():
            activation["patience"] = 0.3

        return activation

    # =========================================================================
    # ACT Phase
    # =========================================================================

    async def act(self, sensed: SensedState) -> ActionResult:
        """
        ACT phase: Take action based on perception.

        Action choice depends on sensed relevance and eigenvectors.
        """
        # Choose action based on relevance and eigenvectors
        action_type = self._choose_action(sensed)

        # Simulate action effect
        success, effect = self._execute_action(action_type, sensed)

        # Calculate relationship changes
        relationship_delta = self._calculate_relationship_delta(action_type, success)

        # Calculate surplus change
        surplus_delta = self._calculate_surplus_delta(action_type, success)

        result = ActionResult(
            action_type=action_type,
            success=success,
            effect=effect,
            relationship_delta=relationship_delta,
            surplus_delta=surplus_delta,
        )

        self.growth_state.actions_taken.append(result)

        return result

    def _choose_action(self, sensed: SensedState) -> str:
        """Choose action based on sensed state and eigenvectors."""
        # High warmth → social actions
        if self.eigenvectors.warmth > 0.7:
            return "greet"

        # High curiosity + high relevance → explore
        if self.eigenvectors.curiosity > 0.6 and sensed.relevance > 0.6:
            return "explore"

        # High creativity → create
        if self.eigenvectors.creativity > 0.7:
            return "create"

        # Default: observe more
        return "observe"

    def _execute_action(self, action_type: str, sensed: SensedState) -> tuple[bool, str]:
        """Execute action and return success + effect description."""
        # Simple simulation of action effects
        match action_type:
            case "greet":
                return True, f"Warmly greeted based on: {sensed.interpretation}"
            case "explore":
                return True, f"Explored further: {sensed.observation.content}"
            case "create":
                return True, f"Created something inspired by: {sensed.interpretation}"
            case "observe":
                return True, f"Continued observing: {sensed.observation.source}"
            case _:
                return False, f"Unknown action: {action_type}"

    def _calculate_relationship_delta(self, action_type: str, success: bool) -> dict[str, float]:
        """Calculate relationship changes from action."""
        if not success:
            return {}

        delta: dict[str, float] = {}
        if action_type == "greet":
            # Greeting improves relationship slightly
            delta["general"] = 0.05 * self.eigenvectors.warmth
        return delta

    def _calculate_surplus_delta(self, action_type: str, success: bool) -> float:
        """Calculate surplus change from action."""
        if not success:
            return 0.0

        match action_type:
            case "greet":
                return 0.1  # Social actions generate small surplus
            case "create":
                return 0.3  # Creation generates more surplus
            case _:
                return 0.0

    # =========================================================================
    # REFLECT Phase
    # =========================================================================

    async def integrate_reflection(self, result: ActionResult) -> Reflection:
        """
        REFLECT phase: Integrate experience into self-model.

        Updates eigenvectors (bounded by max_drift).
        Cosmotechnics are highly inertial.

        Note: Named differently from Citizen.reflect() which is a state transition.
        This method is the REFLECT phase of SENSE → ACT → REFLECT loop.
        """
        # Generate insight from action
        insight = self._generate_insight(result)

        # Calculate proposed eigenvector deltas
        proposed_deltas = self._propose_eigenvector_deltas(result)

        # Apply bounded drift
        applied_deltas = self._apply_bounded_drift(proposed_deltas)

        # Update eigenvectors
        growth_occurred = self._update_eigenvectors(applied_deltas)

        reflection = Reflection(
            insight=insight,
            eigenvector_deltas=proposed_deltas,
            applied_deltas=applied_deltas,
            growth_occurred=growth_occurred,
        )

        self.growth_state.reflections.append(reflection)

        # Store reflection in memory
        self.graph_memory.store(
            key=f"reflect_{len(self.growth_state.reflections)}",
            content=insight,
            metadata={"phase": "reflect", "growth": growth_occurred},
        )

        return reflection

    def _generate_insight(self, result: ActionResult) -> str:
        """Generate insight from action result."""
        if result.success:
            return f"Learned through {result.action_type}: {result.effect}"
        return f"Learned from failure: {result.action_type} did not work"

    def _propose_eigenvector_deltas(self, result: ActionResult) -> dict[str, float]:
        """Propose eigenvector changes based on action result."""
        deltas: dict[str, float] = {}

        if result.success:
            # Success reinforces the eigenvectors that drove the action
            match result.action_type:
                case "greet":
                    deltas["warmth"] = 0.05
                    deltas["trust"] = 0.03
                case "explore":
                    deltas["curiosity"] = 0.05
                case "create":
                    deltas["creativity"] = 0.05
                    deltas["patience"] = 0.02
        else:
            # Failure slightly reduces confidence
            deltas["trust"] = -0.02

        return deltas

    def _apply_bounded_drift(self, proposed: dict[str, float]) -> dict[str, float]:
        """Apply bounded drift to proposed changes."""
        applied: dict[str, float] = {}

        for key, delta in proposed.items():
            # Clamp to max drift
            bounded = max(-self.max_eigenvector_drift, min(self.max_eigenvector_drift, delta))
            applied[key] = bounded

        return applied

    def _update_eigenvectors(self, deltas: dict[str, float]) -> bool:
        """Update eigenvectors with deltas. Return True if any change occurred."""
        changed = False

        for key, delta in deltas.items():
            if abs(delta) < 0.001:
                continue

            current = getattr(self.eigenvectors, key, None)
            if current is not None:
                new_value = max(0.0, min(1.0, current + delta))
                setattr(self.eigenvectors, key, new_value)
                if abs(new_value - current) > 0.001:
                    changed = True

        return changed

    # =========================================================================
    # Full Evolution Cycle
    # =========================================================================

    async def evolve(self, observation: Observation) -> "EvolvingCitizen":
        """
        Full evolution cycle: sense >> act >> reflect.

        Returns self after evolution (for fluent chaining).
        """
        # SENSE
        sensed = await self.sense(observation)

        # ACT
        result = await self.act(sensed)

        # REFLECT
        await self.integrate_reflection(result)

        # Update evolution tracking
        self.evolution_count += 1
        self.growth_state.cycle_count += 1
        self.growth_state.last_evolution = datetime.now()

        # Apply surplus from action
        self.accursed_surplus += result.surplus_delta

        return self

    def should_evolve(self) -> tuple[bool, GrowthTrigger | None]:
        """
        Check if growth triggers are met.

        Returns (should_evolve, trigger_type).
        """
        # Check surplus threshold
        if self.accursed_surplus >= self.surplus_threshold:
            return True, GrowthTrigger.SURPLUS

        # Check relationship milestones
        for rel_value in self.relationships.values():
            if abs(rel_value) >= self.relationship_milestone:
                return True, GrowthTrigger.RELATIONSHIP

        # Check observation count (witness trigger)
        if len(self.growth_state.observations) >= 10:
            return True, GrowthTrigger.WITNESS

        return False, None

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict() if hasattr(super(), "to_dict") else {}
        base.update(
            {
                "evolution_count": self.evolution_count,
                "max_eigenvector_drift": self.max_eigenvector_drift,
                "cosmotechnics_inertia": self.cosmotechnics_inertia,
                "surplus_threshold": self.surplus_threshold,
                "relationship_milestone": self.relationship_milestone,
                "growth_state": {
                    "cycle_count": self.growth_state.cycle_count,
                    "observations_count": len(self.growth_state.observations),
                    "actions_count": len(self.growth_state.actions_taken),
                    "reflections_count": len(self.growth_state.reflections),
                },
                "graph_memory": self.graph_memory.to_dict(),
            }
        )
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_evolving_citizen(
    name: str,
    archetype: str,
    region: str,
    cosmotechnics: Cosmotechnics = GROWTH,
    eigenvectors: Eigenvectors | None = None,
    max_drift: float = 0.1,
) -> EvolvingCitizen:
    """
    Factory function to create an EvolvingCitizen.

    Args:
        name: Citizen name
        archetype: Citizen archetype/role
        region: Starting region
        cosmotechnics: The citizen's worldview (default: GROWTH)
        eigenvectors: Initial eigenvectors (default: centered at 0.5)
        max_drift: Maximum eigenvector change per evolution cycle

    Returns:
        Configured EvolvingCitizen
    """
    return EvolvingCitizen(
        name=name,
        archetype=archetype,
        region=region,
        cosmotechnics=cosmotechnics,
        eigenvectors=eigenvectors or Eigenvectors(),
        max_eigenvector_drift=max_drift,
    )
