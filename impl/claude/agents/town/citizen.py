"""
Citizen: The Metaphysical Agent Entity.

A citizen is not a known entity but an archaeological site.
Like Porras-Kim's undeciphered texts, citizens contain:
- Fragments that may never cohere
- Meanings that shift with interpretation
- An intended destiny distinct from what we impose

The simulation excavates. It does not create.

Six Metaphysical Properties (from spec/town/metaphysics.md):
- Archaeological (Porras-Kim): Meaning is excavated, not assigned
- Hyperobjectival (Morton): Distributed in time and relation
- Intra-active (Barad): Emerge through relation, not before
- Opaque (Glissant): Irreducibly unknowable core
- Cosmotechnical (Hui): Unique moral-cosmic-technical unity
- Accursed (Bataille): Must spend excess gloriously

See: spec/town/metaphysics.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from agents.d.polynomial import MemoryPolynomialAgent
from agents.town.polynomial import (
    CITIZEN_POLYNOMIAL,
    CitizenInput,
    CitizenOutput,
    CitizenPhase,
)

# =============================================================================
# Eigenvectors (Soul Fingerprint)
# =============================================================================


@dataclass
class Eigenvectors:
    """
    The citizen's soul eigenvectors.

    These are not fixed traits but shifting interpretations.
    Like the "meaning" of a museum artifact, they change
    with observation context.

    From Hui: Each citizen embodies a different cosmotechnics—
    a different relationship between cosmos (meaning) and technics (action).
    """

    warmth: float = 0.5  # 0 = cold, 1 = warm
    curiosity: float = 0.5  # 0 = incurious, 1 = intensely curious
    trust: float = 0.5  # 0 = suspicious, 1 = trusting
    creativity: float = 0.5  # 0 = conventional, 1 = inventive
    patience: float = 0.5  # 0 = impatient, 1 = patient

    def __post_init__(self) -> None:
        """Clamp values to [0, 1]."""
        self.warmth = max(0.0, min(1.0, self.warmth))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.trust = max(0.0, min(1.0, self.trust))
        self.creativity = max(0.0, min(1.0, self.creativity))
        self.patience = max(0.0, min(1.0, self.patience))

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "warmth": self.warmth,
            "curiosity": self.curiosity,
            "trust": self.trust,
            "creativity": self.creativity,
            "patience": self.patience,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Eigenvectors:
        """Create from dictionary."""
        return cls(
            warmth=data.get("warmth", 0.5),
            curiosity=data.get("curiosity", 0.5),
            trust=data.get("trust", 0.5),
            creativity=data.get("creativity", 0.5),
            patience=data.get("patience", 0.5),
        )


# =============================================================================
# Cosmotechnics (Meaning-Making Frame)
# =============================================================================


@dataclass(frozen=True)
class Cosmotechnics:
    """
    A citizen's cosmotechnics—their unique moral-cosmic-technical unity.

    From Hui: There is not one technology but multiple cosmotechnics.
    Each citizen lives in a different technological world.

    These are INCOMMENSURABLE. They cannot be translated into each other.
    When cosmotechnics meet, they create friction, not synthesis.
    """

    name: str
    description: str
    metaphor: str  # e.g., "Life is a gathering"

    # The opacity statement (Glissant): what cannot be shared
    opacity_statement: str = ""


# Default cosmotechnics for the MPP citizens
GATHERING = Cosmotechnics(
    name="gathering",
    description="Meaning arises through congregation",
    metaphor="Life is a gathering",
    opacity_statement="There are gatherings I cannot share with you.",
)

CONSTRUCTION = Cosmotechnics(
    name="construction",
    description="Meaning arises through building",
    metaphor="Life is construction",
    opacity_statement="There are structures I build only in silence.",
)

EXPLORATION = Cosmotechnics(
    name="exploration",
    description="Meaning arises through discovery",
    metaphor="Life is exploration",
    opacity_statement="There are frontiers I will not map for you.",
)

# Phase 2 cosmotechnics
HEALING = Cosmotechnics(
    name="healing",
    description="Meaning arises through restoration",
    metaphor="Life is restoration",
    opacity_statement="There are wounds I heal only in solitude.",
)

MEMORY = Cosmotechnics(
    name="memory",
    description="Meaning arises through remembering",
    metaphor="Life is remembering",
    opacity_statement="There are memories I guard alone.",
)

EXCHANGE = Cosmotechnics(
    name="exchange",
    description="Meaning arises through trade",
    metaphor="Life is trade",
    opacity_statement="There are bargains I make only with myself.",
)

CULTIVATION = Cosmotechnics(
    name="cultivation",
    description="Meaning arises through tending",
    metaphor="Life is tending",
    opacity_statement="There are gardens I tend in secret.",
)


# =============================================================================
# Citizen Entity
# =============================================================================


@dataclass
class Citizen:
    """
    A citizen of Agent Town.

    This is an archaeological site, not a created entity.
    The simulation excavates meaning; it does not assign it.

    Core Components:
    - polynomial: The state machine (CitizenPolynomial)
    - eigenvectors: Soul fingerprint
    - cosmotechnics: Meaning-making frame
    - memory: Holographic memory (MemoryPolynomialAgent)
    - opacity: Irreducible unknowable core

    From Morton: The citizen is a hyperobject—distributed in time/relation.
    They are not "in" a region; they are a local thickening of the mesh.
    """

    name: str
    archetype: str
    region: str  # Current location (region name)
    eigenvectors: Eigenvectors = field(default_factory=Eigenvectors)
    cosmotechnics: Cosmotechnics = field(default_factory=lambda: GATHERING)

    # Internal state (managed by polynomial)
    _phase: CitizenPhase = field(default=CitizenPhase.IDLE, repr=False)
    _memory: MemoryPolynomialAgent | None = field(default=None, repr=False)

    # Identity
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)

    # Relationships (citizen_id -> weight)
    relationships: dict[str, float] = field(default_factory=dict)

    # Accursed share: accumulated surplus that must be spent
    accursed_surplus: float = 0.0

    def __post_init__(self) -> None:
        """Initialize memory if not provided."""
        if self._memory is None:
            self._memory = MemoryPolynomialAgent()

    @property
    def phase(self) -> CitizenPhase:
        """Current phase in the polynomial."""
        return self._phase

    @property
    def memory(self) -> MemoryPolynomialAgent:
        """The citizen's memory agent."""
        if self._memory is None:
            self._memory = MemoryPolynomialAgent()
        return self._memory

    @property
    def is_resting(self) -> bool:
        """Check if citizen is resting (Right to Rest)."""
        return self._phase == CitizenPhase.RESTING

    @property
    def is_available(self) -> bool:
        """Check if citizen is available for interaction."""
        return self._phase != CitizenPhase.RESTING

    def transition(self, input: Any) -> CitizenOutput:
        """
        Perform a state transition.

        From Barad: The transition reconfigures the phenomenon.
        The citizen doesn't change—our cut on them changes.
        """
        new_phase, output = CITIZEN_POLYNOMIAL.transition(self._phase, input)
        self._phase = new_phase
        return output

    def greet(self, partner_id: str) -> CitizenOutput:
        """Initiate a greeting with another citizen."""
        return self.transition(CitizenInput.greet(partner_id))

    def work(self, activity: str, duration_minutes: int = 60) -> CitizenOutput:
        """Start working on an activity."""
        return self.transition(CitizenInput.work(activity, duration_minutes))

    def reflect(self, topic: str | None = None) -> CitizenOutput:
        """Enter reflection."""
        return self.transition(CitizenInput.reflect(topic))

    def rest(self) -> CitizenOutput:
        """Go to rest (Right to Rest)."""
        return self.transition(CitizenInput.rest())

    def wake(self) -> CitizenOutput:
        """Wake from rest."""
        return self.transition(CitizenInput.wake())

    def move_to(self, region: str) -> None:
        """Move to a different region."""
        self.region = region

    def update_relationship(self, citizen_id: str, delta: float) -> None:
        """Update relationship with another citizen."""
        current = self.relationships.get(citizen_id, 0.0)
        self.relationships[citizen_id] = max(-1.0, min(1.0, current + delta))

    def get_relationship(self, citizen_id: str) -> float:
        """Get relationship weight with another citizen."""
        return self.relationships.get(citizen_id, 0.0)

    def accumulate_surplus(self, amount: float) -> None:
        """
        Accumulate surplus (Bataille).

        The surplus must eventually be spent gloriously or catastrophically.
        """
        self.accursed_surplus += amount

    def spend_surplus(self, amount: float) -> float:
        """
        Spend surplus (glorious expenditure).

        Returns the amount actually spent.
        """
        spent = min(amount, self.accursed_surplus)
        self.accursed_surplus -= spent
        return spent

    async def remember(self, content: Any, key: str | None = None) -> None:
        """Store something in memory."""
        await self.memory.store(content, key=key)

    async def recall(self, key: str | None = None) -> Any:
        """Recall something from memory."""
        response = await self.memory.load(key=key)
        return response.state

    def manifest(self, lod: int = 0) -> dict[str, Any]:
        """
        Manifest the citizen at a given Level of Detail.

        From Glissant: Higher LOD does not mean more transparency.
        It means encountering the opacity more directly.

        LOD 0: Silhouette (name, location, emoji)
        LOD 1: Posture (current action, mood)
        LOD 2: Dialogue (speech, inner monologue)
        LOD 3: Memory (active memories, goals)
        LOD 4: Psyche (eigenvectors, tensions)
        LOD 5: Abyss (irreducible mystery)
        """
        base: dict[str, Any] = {
            "name": self.name,
            "region": self.region,
            "phase": self._phase.name,
        }

        if lod >= 1:
            base["archetype"] = self.archetype
            base["mood"] = self._infer_mood()

        if lod >= 2:
            base["cosmotechnics"] = self.cosmotechnics.name
            base["metaphor"] = self.cosmotechnics.metaphor

        if lod >= 3:
            base["eigenvectors"] = self.eigenvectors.to_dict()
            base["relationships"] = dict(self.relationships)

        if lod >= 4:
            base["accursed_surplus"] = self.accursed_surplus
            base["id"] = self.id

        if lod >= 5:
            # The abyss: reveal the opacity
            base["opacity"] = {
                "statement": self.cosmotechnics.opacity_statement,
                "message": (
                    f"You have reached the edge of what can be known about {self.name}. "
                    "Beyond this lies irreducible mystery. This is not concealment; "
                    "this is their right to remain opaque."
                ),
            }

        return base

    def _infer_mood(self) -> str:
        """Infer mood from eigenvectors and phase."""
        if self._phase == CitizenPhase.RESTING:
            return "resting"
        if self._phase == CitizenPhase.REFLECTING:
            return "contemplative"
        if self._phase == CitizenPhase.WORKING:
            return "focused"
        if self._phase == CitizenPhase.SOCIALIZING:
            if self.eigenvectors.warmth > 0.7:
                return "warm"
            return "engaged"
        # IDLE
        if self.eigenvectors.curiosity > 0.7:
            return "curious"
        return "calm"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "archetype": self.archetype,
            "region": self.region,
            "eigenvectors": self.eigenvectors.to_dict(),
            "cosmotechnics": self.cosmotechnics.name,
            "phase": self._phase.name,
            "relationships": dict(self.relationships),
            "accursed_surplus": self.accursed_surplus,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Citizen:
        """Deserialize from dictionary."""
        # Map cosmotechnics name to instance
        cosmo_map = {
            "gathering": GATHERING,
            "construction": CONSTRUCTION,
            "exploration": EXPLORATION,
            # Phase 2 cosmotechnics
            "healing": HEALING,
            "memory": MEMORY,
            "exchange": EXCHANGE,
            "cultivation": CULTIVATION,
        }
        cosmo = cosmo_map.get(data.get("cosmotechnics", "gathering"), GATHERING)

        # Map phase name to enum
        phase_name = data.get("phase", "IDLE")
        phase = CitizenPhase[phase_name]

        citizen = cls(
            name=data["name"],
            archetype=data["archetype"],
            region=data["region"],
            eigenvectors=Eigenvectors.from_dict(data.get("eigenvectors", {})),
            cosmotechnics=cosmo,
            _phase=phase,
        )

        if "id" in data:
            citizen.id = data["id"]
        if "relationships" in data:
            citizen.relationships = dict(data["relationships"])
        if "accursed_surplus" in data:
            citizen.accursed_surplus = data["accursed_surplus"]

        return citizen

    def __repr__(self) -> str:
        return (
            f"Citizen({self.name}, {self.archetype}, {self.region}, {self._phase.name})"
        )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "Eigenvectors",
    "Cosmotechnics",
    # MPP cosmotechnics
    "GATHERING",
    "CONSTRUCTION",
    "EXPLORATION",
    # Phase 2 cosmotechnics
    "HEALING",
    "MEMORY",
    "EXCHANGE",
    "CULTIVATION",
    "Citizen",
]
