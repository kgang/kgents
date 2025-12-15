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
from protocols.nphase.operad import (
    NPhase,
    NPhaseState,
    is_valid_transition,
)
from protocols.nphase.operad import (
    next_phase as nphase_next,
)

# =============================================================================
# Eigenvectors (Soul Fingerprint)
# =============================================================================


@dataclass
class Eigenvectors:
    """
    The citizen's soul eigenvectors (7D personality space).

    These are not fixed traits but shifting interpretations.
    Like the "meaning" of a museum artifact, they change
    with observation context.

    From Hui: Each citizen embodies a different cosmotechnics—
    a different relationship between cosmos (meaning) and technics (action).

    Phase 4: Extended from 5D to 7D (added resilience, ambition).
    """

    warmth: float = 0.5  # 0 = cold, 1 = warm
    curiosity: float = 0.5  # 0 = incurious, 1 = intensely curious
    trust: float = 0.5  # 0 = suspicious, 1 = trusting
    creativity: float = 0.5  # 0 = conventional, 1 = inventive
    patience: float = 0.5  # 0 = impatient, 1 = patient
    # Phase 4 additions
    resilience: float = 0.5  # 0 = fragile, 1 = antifragile
    ambition: float = 0.5  # 0 = content, 1 = driven

    def __post_init__(self) -> None:
        """Clamp values to [0, 1]."""
        self.warmth = max(0.0, min(1.0, self.warmth))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.trust = max(0.0, min(1.0, self.trust))
        self.creativity = max(0.0, min(1.0, self.creativity))
        self.patience = max(0.0, min(1.0, self.patience))
        self.resilience = max(0.0, min(1.0, self.resilience))
        self.ambition = max(0.0, min(1.0, self.ambition))

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "warmth": self.warmth,
            "curiosity": self.curiosity,
            "trust": self.trust,
            "creativity": self.creativity,
            "patience": self.patience,
            "resilience": self.resilience,
            "ambition": self.ambition,
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
            resilience=data.get("resilience", 0.5),
            ambition=data.get("ambition", 0.5),
        )

    def drift(self, other: "Eigenvectors") -> float:
        """
        Calculate L2 distance (drift) between eigenvector spaces.

        Metric space laws preserved:
        - L1: drift(x, x) = 0 (identity)
        - L2: drift(x, y) = drift(y, x) (symmetry)
        - L3: drift(x, z) <= drift(x, y) + drift(y, z) (triangle)
        """
        sum_squares = (
            (self.warmth - other.warmth) ** 2
            + (self.curiosity - other.curiosity) ** 2
            + (self.trust - other.trust) ** 2
            + (self.creativity - other.creativity) ** 2
            + (self.patience - other.patience) ** 2
            + (self.resilience - other.resilience) ** 2
            + (self.ambition - other.ambition) ** 2
        )
        return float(sum_squares**0.5)

    def similarity(self, other: "Eigenvectors") -> float:
        """
        Cosine similarity for coalition formation.

        Returns value in [-1, 1] where 1 = identical direction.
        """
        # Convert to vectors
        v1 = [
            self.warmth,
            self.curiosity,
            self.trust,
            self.creativity,
            self.patience,
            self.resilience,
            self.ambition,
        ]
        v2 = [
            other.warmth,
            other.curiosity,
            other.trust,
            other.creativity,
            other.patience,
            other.resilience,
            other.ambition,
        ]

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    def apply_bounded_drift(
        self, deltas: dict[str, float], max_drift: float = 0.1
    ) -> "Eigenvectors":
        """
        Apply bounded drift to create new eigenvectors.

        Ensures no dimension changes more than max_drift.
        """
        new_values = {}
        for key in [
            "warmth",
            "curiosity",
            "trust",
            "creativity",
            "patience",
            "resilience",
            "ambition",
        ]:
            current = getattr(self, key)
            delta = deltas.get(key, 0.0)
            bounded_delta = max(-max_drift, min(max_drift, delta))
            new_values[key] = max(0.0, min(1.0, current + bounded_delta))
        return Eigenvectors(**new_values)


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

# Phase 4 cosmotechnics (5 new archetypes)
CONSTRUCTION_V2 = Cosmotechnics(
    name="construction_v2",
    description="Meaning arises through structured creation",
    metaphor="Life is architecture",
    opacity_statement="There are blueprints I draft in solitude.",
)

EXCHANGE_V2 = Cosmotechnics(
    name="exchange_v2",
    description="Meaning arises through fair value exchange",
    metaphor="Life is negotiation",
    opacity_statement="There are bargains I make with myself alone.",
)

RESTORATION = Cosmotechnics(
    name="restoration",
    description="Meaning arises through healing and repair",
    metaphor="Life is mending",
    opacity_statement="There are wounds I bind in darkness.",
)

SYNTHESIS_V2 = Cosmotechnics(
    name="synthesis_v2",
    description="Meaning arises through knowledge integration",
    metaphor="Life is discovery",
    opacity_statement="There are connections I perceive that I cannot share.",
)

MEMORY_V2 = Cosmotechnics(
    name="memory_v2",
    description="Meaning arises through witnessing and recording",
    metaphor="Life is testimony",
    opacity_statement="There are histories I carry alone.",
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

    # N-Phase compressed state (SENSE/ACT/REFLECT)
    nphase_state: NPhaseState = field(default_factory=NPhaseState)
    nphase_history: list[dict[str, Any]] = field(default_factory=list, repr=False)

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

    @property
    def nphase_phase(self) -> NPhase:
        """Current compressed N-Phase state (SENSE/ACT/REFLECT)."""
        return self.nphase_state.current_phase

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

    def advance_nphase(
        self,
        target: NPhase | str | None = None,
        payload: Any | None = None,
    ) -> dict[str, Any]:
        """
        Advance the citizen's compressed N-Phase state.

        If target is None, advances to the next phase in SENSE→ACT→REFLECT.
        Validates transitions via operad law (SENSE->ACT->REFLECT->SENSE).
        """
        from_phase = self.nphase_state.current_phase
        if target is None:
            to_phase = nphase_next(from_phase)
        elif isinstance(target, NPhase):
            to_phase = target
        else:
            to_phase = NPhase[target.upper()]

        if not is_valid_transition(from_phase, to_phase):
            raise ValueError(
                f"Invalid N-Phase transition: {from_phase.name} -> {to_phase.name}"
            )

        # Track cycles when closing REFLECT → SENSE
        if from_phase == NPhase.REFLECT and to_phase == NPhase.SENSE:
            self.nphase_state.cycle_count += 1

        self.nphase_state.current_phase = to_phase
        self.nphase_state.phase_outputs[to_phase].append(payload)

        record = {
            "citizen_id": self.id,
            "from": from_phase.name,
            "to": to_phase.name,
            "cycle": self.nphase_state.cycle_count,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
        }
        self.nphase_history.append(record)
        return record

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
            "nphase": {
                "current": self.nphase_state.current_phase.name,
                "cycle_count": self.nphase_state.cycle_count,
            },
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
            base["nphase"]["phase_outputs"] = {
                phase.name: list(outputs)
                for phase, outputs in self.nphase_state.phase_outputs.items()
            }

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
            "nphase": {
                "current": self.nphase_state.current_phase.name,
                "cycle_count": self.nphase_state.cycle_count,
                "phase_outputs": {
                    phase.name: list(outputs)
                    for phase, outputs in self.nphase_state.phase_outputs.items()
                },
            },
        }

    def nphase_ledger(self) -> dict[str, Any]:
        """Return a JSON-serializable ledger of N-Phase transitions."""
        return {
            "current": self.nphase_state.current_phase.name,
            "cycle_count": self.nphase_state.cycle_count,
            "history": list(self.nphase_history),
            "phase_outputs": {
                phase.name: list(outputs)
                for phase, outputs in self.nphase_state.phase_outputs.items()
            },
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
            # Phase 4 cosmotechnics
            "construction_v2": CONSTRUCTION_V2,
            "exchange_v2": EXCHANGE_V2,
            "restoration": RESTORATION,
            "synthesis_v2": SYNTHESIS_V2,
            "memory_v2": MEMORY_V2,
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
        if "nphase" in data:
            nphase_data = data.get("nphase", {})
            outputs = nphase_data.get("phase_outputs", {})
            phase_outputs = {
                phase: list(outputs.get(phase.name, [])) for phase in NPhase
            }
            citizen.nphase_state = NPhaseState(
                current_phase=NPhase[nphase_data.get("current", "SENSE")],
                cycle_count=int(nphase_data.get("cycle_count", 0)),
                phase_outputs=phase_outputs,
            )
            citizen.nphase_history = list(nphase_data.get("history", []))

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
    # Phase 4 cosmotechnics
    "CONSTRUCTION_V2",
    "EXCHANGE_V2",
    "RESTORATION",
    "SYNTHESIS_V2",
    "MEMORY_V2",
    "Citizen",
]
