"""
Builder: A Workshop Builder Extending Citizen.

A builder is a specialized citizen with development expertise.
They inherit all citizen capabilities (memory, relationships, N-Phase)
while adding builder-specific behavior:
- Specialty phase in BUILDER_POLYNOMIAL
- Voice patterns for characteristic speech
- Builder state machine (parallel to citizen state)

The Insight:
    Builders are not just workers—they are interpretive frames.
    Sage sees architecture where Spark sees possibility.
    Each builder's cosmotechnics shapes how they perceive problems.

Example:
    >>> sage = create_sage("Ada")
    >>> sage.speak("we need authentication")
    "Have we considered... we need authentication"
    >>> sage.is_in_specialty  # True when DESIGNING
    False

See: plans/agent-town/builders-workshop.md
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from agents.town.builders.polynomial import (
    BUILDER_POLYNOMIAL,
    BuilderInput,
    BuilderOutput,
    BuilderPhase,
)
from agents.town.citizen import Citizen, Cosmotechnics, Eigenvectors

# =============================================================================
# Builder Class
# =============================================================================


@dataclass
class Builder(Citizen):
    """
    A workshop builder—a specialized citizen with development expertise.

    Builders extend Citizen with:
    - specialty: Their preferred BuilderPhase (where they excel)
    - voice_patterns: Characteristic speech patterns
    - _builder_phase: Current phase in the builder polynomial
    - _nphase_context: Optional N-Phase context (Wave 4)

    The builder has two state machines:
    1. CitizenPolynomial: Life phases (IDLE, WORKING, SOCIALIZING, etc.)
    2. BuilderPolynomial: Work phases (EXPLORING, DESIGNING, etc.)

    These operate in parallel—a builder can be SOCIALIZING (citizen)
    while in DESIGNING (builder) phase.

    Wave 4 Enhancement:
        Builders can receive N-Phase context from their containing WorkshopFlux.
        This allows builders to adapt behavior based on whether we're in
        UNDERSTAND, ACT, or REFLECT phase.
    """

    specialty: BuilderPhase = field(default=BuilderPhase.IDLE)
    voice_patterns: tuple[str, ...] = field(default_factory=tuple)
    _builder_phase: BuilderPhase = field(default=BuilderPhase.IDLE, repr=False)
    _nphase_context: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def builder_phase(self) -> BuilderPhase:
        """Current phase in the builder polynomial."""
        return self._builder_phase

    @property
    def is_in_specialty(self) -> bool:
        """Check if builder is working in their specialty phase."""
        return self._builder_phase == self.specialty

    @property
    def specialty_name(self) -> str:
        """Human-readable specialty name."""
        return self.specialty.name.lower().capitalize()

    @property
    def nphase_context(self) -> dict[str, Any]:
        """
        Current N-Phase context (Wave 4).

        Returns dict with keys:
        - phase: Current N-Phase name (UNDERSTAND, ACT, REFLECT) or None
        - cycle_count: How many U→A→R cycles completed
        - session_id: Session ID if available

        Empty dict if no context set.
        """
        return self._nphase_context

    def set_nphase_context(
        self,
        phase: str | None = None,
        cycle_count: int = 0,
        session_id: str | None = None,
    ) -> None:
        """
        Set N-Phase context for this builder (Wave 4).

        Called by WorkshopFlux to inject N-Phase state.

        Args:
            phase: Current N-Phase name (UNDERSTAND, ACT, REFLECT)
            cycle_count: How many U→A→R cycles completed
            session_id: Session ID for tracking
        """
        self._nphase_context = {
            "phase": phase,
            "cycle_count": cycle_count,
            "session_id": session_id,
        }

    def clear_nphase_context(self) -> None:
        """Clear N-Phase context."""
        self._nphase_context = {}

    @property
    def is_understanding(self) -> bool:
        """Check if currently in UNDERSTAND phase (gathering context)."""
        return self._nphase_context.get("phase") == "UNDERSTAND"

    @property
    def is_acting(self) -> bool:
        """Check if currently in ACT phase (doing work)."""
        return self._nphase_context.get("phase") == "ACT"

    @property
    def is_reflecting(self) -> bool:
        """Check if currently in REFLECT phase (synthesizing)."""
        return self._nphase_context.get("phase") == "REFLECT"

    def builder_transition(self, input: Any) -> BuilderOutput:
        """
        Perform a builder state transition.

        This uses BUILDER_POLYNOMIAL for development work transitions,
        separate from citizen life transitions.
        """
        new_phase, output = BUILDER_POLYNOMIAL.transition(self._builder_phase, input)
        self._builder_phase = new_phase
        return output

    def speak(self, content: str) -> str:
        """
        Generate speech with characteristic voice pattern.

        If voice_patterns is empty, returns content unchanged.
        Otherwise, prepends a random voice pattern.
        """
        if self.voice_patterns:
            pattern = random.choice(self.voice_patterns)
            return f"{pattern} {content}"
        return content

    def handoff_to(
        self,
        target: Builder,
        artifact: Any = None,
        message: str = "",
    ) -> BuilderOutput:
        """
        Hand off work to another builder.

        This transitions self to IDLE and signals target's specialty.
        """
        return self.builder_transition(
            BuilderInput.handoff(
                from_builder=self.archetype,
                to_builder=target.archetype,
                artifact=artifact,
                message=message,
            )
        )

    def start_task(self, task: str, priority: int = 1, **context: Any) -> BuilderOutput:
        """Start working on a new task."""
        return self.builder_transition(BuilderInput.assign(task, priority, **context))

    def continue_work(self, note: str | None = None) -> BuilderOutput:
        """Continue current work."""
        return self.builder_transition(BuilderInput.continue_work(note))

    def complete_work(self, artifact: Any = None, summary: str = "") -> BuilderOutput:
        """Complete current work and return to IDLE."""
        return self.builder_transition(BuilderInput.complete(artifact, summary))

    def query_user(self, question: str) -> BuilderOutput:
        """Query the user for clarification."""
        return self.builder_transition(BuilderInput.query_user(question))

    def receive_response(self, response: str) -> BuilderOutput:
        """Receive a user response."""
        return self.builder_transition(BuilderInput.user_response(response))

    def builder_rest(self) -> BuilderOutput:
        """Step back from builder work (returns to IDLE builder phase)."""
        return self.builder_transition(BuilderInput.rest())

    def manifest(self, lod: int = 0) -> dict[str, Any]:
        """
        Manifest builder at a given Level of Detail.

        Extends Citizen.manifest() with builder-specific data.
        """
        base = super().manifest(lod)

        # Add builder data at LOD 1+
        if lod >= 1:
            base["builder"] = {
                "phase": self._builder_phase.name,
                "specialty": self.specialty.name,
                "is_in_specialty": self.is_in_specialty,
            }
            # Add N-Phase context if set (Wave 4)
            if self._nphase_context:
                base["builder"]["nphase"] = self._nphase_context

        if lod >= 2:
            base["builder"]["voice_patterns"] = list(self.voice_patterns[:3])

        return base

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base["builder"] = {
            "phase": self._builder_phase.name,
            "specialty": self.specialty.name,
            "voice_patterns": list(self.voice_patterns),
        }
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Builder:
        """Deserialize from dictionary."""
        # Use parent method for base Citizen fields
        from agents.town.builders.cosmotechnics import (
            ARCHITECTURE,
            CRAFTSMANSHIP,
            DISCOVERY,
            EXPERIMENTATION,
            ORCHESTRATION,
        )

        cosmo_map = {
            "architecture": ARCHITECTURE,
            "experimentation": EXPERIMENTATION,
            "craftsmanship": CRAFTSMANSHIP,
            "discovery": DISCOVERY,
            "orchestration": ORCHESTRATION,
        }

        # Get builder-specific data
        builder_data = data.get("builder", {})
        builder_phase = BuilderPhase[builder_data.get("phase", "IDLE")]
        specialty = BuilderPhase[builder_data.get("specialty", "IDLE")]
        voice_patterns = tuple(builder_data.get("voice_patterns", []))

        # Get cosmotechnics
        cosmo_name = data.get("cosmotechnics", "architecture")
        cosmo = cosmo_map.get(cosmo_name)
        if cosmo is None:
            # Fall back to parent cosmotechnics lookup
            from agents.town.citizen import GATHERING

            cosmo = GATHERING

        builder = cls(
            name=data["name"],
            archetype=data["archetype"],
            region=data["region"],
            eigenvectors=Eigenvectors.from_dict(data.get("eigenvectors", {})),
            cosmotechnics=cosmo,
            specialty=specialty,
            voice_patterns=voice_patterns,
            _builder_phase=builder_phase,
        )

        if "id" in data:
            builder.id = data["id"]
        if "relationships" in data:
            builder.relationships = dict(data["relationships"])
        if "accursed_surplus" in data:
            builder.accursed_surplus = data["accursed_surplus"]

        return builder

    def __repr__(self) -> str:
        return f"Builder({self.name}, {self.archetype}, {self._builder_phase.name})"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Builder",
]
