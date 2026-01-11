"""
Axiom Discovery Service: Guided dialogue to discover endeavor axioms.

Implements a 5-turn structured dialogue that extracts:
- A1: Success Definition - What does success look like?
- A2: Feeling Target - What do you want to feel?
- A3: Constraints - What's non-negotiable?
- A4: Verification - How will you know it's working?

The discovery process follows the Zero Seed pattern:
- Ground decisions in axioms
- Construct witnessed proofs
- Detect contradictions

Example:
    discovery = AxiomDiscoveryService()

    # Start with raw endeavor
    session = await discovery.start_discovery(
        "I want to build better daily habits"
    )

    # Turn 1: Success definition
    turn1 = await discovery.process_turn(
        session.session_id,
        "I want to end each day feeling accomplished"
    )

    # Continue through all phases...
    axioms = await discovery.complete_discovery(session.session_id)

Teaching:
    gotcha: Sessions are stored in memory by default. For persistence,
            wire to WitnessPersistence after bootstrap is complete.

    gotcha: The dialogue is structured but not rigid. If a user's response
            covers multiple axioms, the service extracts what it can and
            may skip or combine phases.

    gotcha: AI agents should use this service through AGENTESE:
            self.tangibility.endeavor.discover

See: spec/protocols/zero-seed1/genesis.md
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================


class DiscoveryPhase(str, Enum):
    """
    Phases of the axiom discovery dialogue.

    Each phase targets a specific axiom:
    - GREETING: Introduction and raw endeavor capture
    - SUCCESS: A1 - What does success look like?
    - FEELING: A2 - What do you want to feel?
    - CONSTRAINTS: A3 - What's non-negotiable?
    - VERIFICATION: A4 - How will you know it's working?
    - COMPLETE: All axioms discovered
    """

    GREETING = "greeting"
    SUCCESS = "success"
    FEELING = "feeling"
    CONSTRAINTS = "constraints"
    VERIFICATION = "verification"
    COMPLETE = "complete"


@dataclass(frozen=True)
class EndeavorAxioms:
    """
    Discovered axioms from the 5-turn dialogue.

    These axioms ground the endeavor in verifiable success criteria.
    They are used by PilotBootstrapService to match or create a pilot.

    Attributes:
        success_definition: A1 - What does success look like?
        feeling_target: A2 - What do you want to feel?
        constraints: A3 - What's non-negotiable?
        verification: A4 - How will you know it's working?
        raw_endeavor: Original user input
        discovered_at: Timestamp of completion
        session_id: The discovery session ID

    Example:
        axioms = EndeavorAxioms(
            success_definition="End each day with a written reflection",
            feeling_target="Present, grounded, aware of my growth",
            constraints=["Must take less than 10 minutes", "No pressure to be 'productive'"],
            verification="I can look back at a week of entries and see patterns",
            raw_endeavor="I want to build a daily journaling habit"
        )
    """

    success_definition: str
    feeling_target: str
    constraints: tuple[str, ...]
    verification: str
    raw_endeavor: str
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    session_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success_definition": self.success_definition,
            "feeling_target": self.feeling_target,
            "constraints": list(self.constraints),
            "verification": self.verification,
            "raw_endeavor": self.raw_endeavor,
            "discovered_at": self.discovered_at.isoformat(),
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EndeavorAxioms":
        """Create from dictionary."""
        return cls(
            success_definition=data.get("success_definition", ""),
            feeling_target=data.get("feeling_target", ""),
            constraints=tuple(data.get("constraints", [])),
            verification=data.get("verification", ""),
            raw_endeavor=data.get("raw_endeavor", ""),
            discovered_at=datetime.fromisoformat(data["discovered_at"])
            if "discovered_at" in data
            else datetime.utcnow(),
            session_id=data.get("session_id", ""),
        )

    def is_complete(self) -> bool:
        """Check if all axioms are discovered."""
        return bool(
            self.success_definition
            and self.feeling_target
            and self.constraints
            and self.verification
        )

    def completeness_score(self) -> float:
        """Calculate how complete the axioms are (0.0 to 1.0)."""
        score = 0.0
        if self.success_definition:
            score += 0.25
        if self.feeling_target:
            score += 0.25
        if self.constraints:
            score += 0.25
        if self.verification:
            score += 0.25
        return score


@dataclass
class DiscoveryTurn:
    """
    A single turn in the discovery dialogue.

    Attributes:
        turn_number: 1-indexed turn number
        phase: Current phase of discovery
        prompt: The question asked
        response: User's response (empty until provided)
        extracted: What was extracted from the response
        next_phase: Phase after processing this turn
    """

    turn_number: int
    phase: DiscoveryPhase
    prompt: str
    response: str = ""
    extracted: dict[str, Any] = field(default_factory=dict)
    next_phase: DiscoveryPhase = DiscoveryPhase.GREETING

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "turn_number": self.turn_number,
            "phase": self.phase.value,
            "prompt": self.prompt,
            "response": self.response,
            "extracted": self.extracted,
            "next_phase": self.next_phase.value,
        }


@dataclass
class DiscoverySession:
    """
    A discovery session tracking the axiom dialogue.

    Attributes:
        session_id: Unique session identifier
        raw_endeavor: Original user endeavor
        current_phase: Current phase of discovery
        turns: List of dialogue turns
        axioms: Partially discovered axioms
        started_at: Session start time
        completed_at: Session completion time (if complete)
    """

    session_id: str
    raw_endeavor: str
    current_phase: DiscoveryPhase
    turns: list[DiscoveryTurn] = field(default_factory=list)
    axioms: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "raw_endeavor": self.raw_endeavor,
            "current_phase": self.current_phase.value,
            "turns": [t.to_dict() for t in self.turns],
            "axioms": self.axioms,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# =============================================================================
# Prompts
# =============================================================================


PHASE_PROMPTS = {
    DiscoveryPhase.SUCCESS: (
        "Let's ground this endeavor in something tangible.\n\n"
        "**A1: Success Definition**\n"
        "What does success look like for '{endeavor}'?\n\n"
        "Describe a specific, observable outcome. Not 'be happier' but "
        "'end each day with a written reflection' or 'complete one focused work block'."
    ),
    DiscoveryPhase.FEELING: (
        "Now let's connect this to how you want to feel.\n\n"
        "**A2: Feeling Target**\n"
        "When this endeavor is working, what do you want to feel?\n\n"
        "Be specific: 'present and grounded', 'accomplished without exhaustion', "
        "'curious and engaged'."
    ),
    DiscoveryPhase.CONSTRAINTS: (
        "Every endeavor has non-negotiables.\n\n"
        "**A3: Constraints**\n"
        "What's non-negotiable for this endeavor?\n\n"
        "Think about time ('must take less than 10 minutes'), values "
        "('no hustle culture'), or conditions ('works offline')."
    ),
    DiscoveryPhase.VERIFICATION: (
        "Finally, let's define how you'll know it's working.\n\n"
        "**A4: Verification**\n"
        "How will you know this endeavor is succeeding?\n\n"
        "What evidence would convince you? 'I can look back at a week of entries', "
        "'my energy improves over time', 'I actually want to do it'."
    ),
    DiscoveryPhase.COMPLETE: (
        "Your endeavor axioms are complete.\n\n"
        "**Summary**\n"
        "- **Success**: {success}\n"
        "- **Feeling**: {feeling}\n"
        "- **Constraints**: {constraints}\n"
        "- **Verification**: {verification}\n\n"
        "Ready to find or create a pilot for this endeavor."
    ),
}


# =============================================================================
# Service
# =============================================================================


class AxiomDiscoveryService:
    """
    Service for guided axiom discovery dialogue.

    Implements a 5-turn structured dialogue to extract endeavor axioms.
    These axioms are then used by PilotBootstrapService to match or
    create a pilot.

    Example:
        discovery = AxiomDiscoveryService()

        # Start discovery
        session = await discovery.start_discovery(
            "I want to build a daily journaling habit"
        )
        print(session.session_id)  # Use for subsequent turns

        # Process turns
        turn = await discovery.process_turn(
            session.session_id,
            "I want to end each day with a written reflection"
        )
        print(turn.prompt)  # Next question

        # Complete when all axioms discovered
        axioms = await discovery.complete_discovery(session.session_id)

    AI Agent Usage:
        Via AGENTESE:
            await logos.invoke(
                "self.tangibility.endeavor",
                observer,
                aspect="discover",
                endeavor="I want to build a daily habit"
            )
    """

    def __init__(self) -> None:
        """Initialize the discovery service."""
        self._sessions: dict[str, DiscoverySession] = {}

    async def start_discovery(self, endeavor: str) -> DiscoverySession:
        """
        Start a new axiom discovery session.

        Args:
            endeavor: Raw endeavor description from user

        Returns:
            DiscoverySession with first turn ready

        Example:
            session = await discovery.start_discovery(
                "I want to build better daily habits"
            )
            # session.turns[0].prompt contains the first question
        """
        session_id = str(uuid.uuid4())

        # Create session
        session = DiscoverySession(
            session_id=session_id,
            raw_endeavor=endeavor,
            current_phase=DiscoveryPhase.SUCCESS,
        )

        # Create first turn
        prompt = PHASE_PROMPTS[DiscoveryPhase.SUCCESS].format(endeavor=endeavor)
        first_turn = DiscoveryTurn(
            turn_number=1,
            phase=DiscoveryPhase.SUCCESS,
            prompt=prompt,
        )
        session.turns.append(first_turn)

        # Store session
        self._sessions[session_id] = session

        logger.info(f"Started discovery session {session_id} for: {endeavor[:50]}...")
        return session

    async def process_turn(
        self,
        session_id: str,
        response: str,
    ) -> DiscoveryTurn:
        """
        Process a user response and advance to next phase.

        Args:
            session_id: Session ID from start_discovery
            response: User's response to current prompt

        Returns:
            DiscoveryTurn for next phase (or final summary if complete)

        Raises:
            ValueError: If session not found or already complete

        Example:
            turn = await discovery.process_turn(
                session.session_id,
                "I want to feel present and grounded"
            )
            if turn.phase == DiscoveryPhase.COMPLETE:
                print("Discovery complete!")
            else:
                print(turn.prompt)  # Next question
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.current_phase == DiscoveryPhase.COMPLETE:
            raise ValueError("Session already complete")

        # Get current turn and record response
        current_turn = session.turns[-1]
        current_turn.response = response

        # Extract axiom from response based on phase
        extracted = self._extract_axiom(session.current_phase, response)
        current_turn.extracted = extracted

        # Update axioms
        session.axioms.update(extracted)

        # Determine next phase
        next_phase = self._get_next_phase(session.current_phase)
        current_turn.next_phase = next_phase
        session.current_phase = next_phase

        # Create next turn
        if next_phase == DiscoveryPhase.COMPLETE:
            # Generate completion summary
            prompt = PHASE_PROMPTS[DiscoveryPhase.COMPLETE].format(
                success=session.axioms.get("success_definition", "Not defined"),
                feeling=session.axioms.get("feeling_target", "Not defined"),
                constraints=", ".join(session.axioms.get("constraints", ["None"])),
                verification=session.axioms.get("verification", "Not defined"),
            )
            session.completed_at = datetime.utcnow()
        else:
            prompt = PHASE_PROMPTS[next_phase].format(endeavor=session.raw_endeavor)

        next_turn = DiscoveryTurn(
            turn_number=len(session.turns) + 1,
            phase=next_phase,
            prompt=prompt,
        )
        session.turns.append(next_turn)

        logger.debug(f"Session {session_id} advanced to {next_phase.value}")
        return next_turn

    async def complete_discovery(self, session_id: str) -> EndeavorAxioms:
        """
        Complete discovery and return structured axioms.

        Args:
            session_id: Session ID

        Returns:
            EndeavorAxioms with all discovered axioms

        Raises:
            ValueError: If session not found

        Example:
            axioms = await discovery.complete_discovery(session.session_id)
            print(axioms.success_definition)
            print(axioms.is_complete())
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Build axioms from session
        axioms = EndeavorAxioms(
            success_definition=session.axioms.get("success_definition", ""),
            feeling_target=session.axioms.get("feeling_target", ""),
            constraints=tuple(session.axioms.get("constraints", [])),
            verification=session.axioms.get("verification", ""),
            raw_endeavor=session.raw_endeavor,
            discovered_at=session.completed_at or datetime.utcnow(),
            session_id=session_id,
        )

        logger.info(
            f"Completed discovery {session_id}: completeness={axioms.completeness_score():.0%}"
        )
        return axioms

    async def get_session(self, session_id: str) -> DiscoverySession | None:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            DiscoverySession or None if not found
        """
        return self._sessions.get(session_id)

    async def fast_discover(
        self,
        endeavor: str,
        success: str,
        feeling: str,
        constraints: list[str],
        verification: str,
    ) -> EndeavorAxioms:
        """
        Skip dialogue and create axioms directly.

        For programmatic use when axioms are already known.

        Args:
            endeavor: Raw endeavor description
            success: A1 - Success definition
            feeling: A2 - Feeling target
            constraints: A3 - Constraints list
            verification: A4 - Verification criteria

        Returns:
            EndeavorAxioms with provided values

        Example:
            axioms = await discovery.fast_discover(
                endeavor="Daily journaling",
                success="Write one entry per day",
                feeling="Present and reflective",
                constraints=["Under 10 minutes", "No pressure"],
                verification="Week of entries visible"
            )
        """
        session_id = str(uuid.uuid4())

        return EndeavorAxioms(
            success_definition=success,
            feeling_target=feeling,
            constraints=tuple(constraints),
            verification=verification,
            raw_endeavor=endeavor,
            session_id=session_id,
        )

    def _extract_axiom(
        self,
        phase: DiscoveryPhase,
        response: str,
    ) -> dict[str, Any]:
        """Extract axiom from response based on phase."""
        response = response.strip()

        match phase:
            case DiscoveryPhase.SUCCESS:
                return {"success_definition": response}

            case DiscoveryPhase.FEELING:
                return {"feeling_target": response}

            case DiscoveryPhase.CONSTRAINTS:
                # Parse constraints - split on newlines, commas, or "and"
                constraints = []
                for part in response.replace("\n", ",").split(","):
                    part = part.strip()
                    if part and part.lower() not in ("and", "or", "also"):
                        constraints.append(part)
                return {"constraints": constraints or [response]}

            case DiscoveryPhase.VERIFICATION:
                return {"verification": response}

            case _:
                return {}

    def _get_next_phase(self, current: DiscoveryPhase) -> DiscoveryPhase:
        """Get the next phase in the discovery sequence."""
        sequence = [
            DiscoveryPhase.SUCCESS,
            DiscoveryPhase.FEELING,
            DiscoveryPhase.CONSTRAINTS,
            DiscoveryPhase.VERIFICATION,
            DiscoveryPhase.COMPLETE,
        ]
        try:
            idx = sequence.index(current)
            return sequence[idx + 1]
        except (ValueError, IndexError):
            return DiscoveryPhase.COMPLETE

    def stats(self) -> dict[str, Any]:
        """Get service statistics."""
        active = sum(
            1 for s in self._sessions.values() if s.current_phase != DiscoveryPhase.COMPLETE
        )
        completed = len(self._sessions) - active

        return {
            "total_sessions": len(self._sessions),
            "active_sessions": active,
            "completed_sessions": completed,
        }


# =============================================================================
# Singleton Factory
# =============================================================================


_service: AxiomDiscoveryService | None = None


def get_axiom_discovery_service() -> AxiomDiscoveryService:
    """
    Get the global AxiomDiscoveryService singleton.

    Returns:
        The singleton AxiomDiscoveryService instance

    Example:
        discovery = get_axiom_discovery_service()
        session = await discovery.start_discovery("My endeavor")
    """
    global _service
    if _service is None:
        _service = AxiomDiscoveryService()
    return _service


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "AxiomDiscoveryService",
    "DiscoverySession",
    "DiscoveryTurn",
    "DiscoveryPhase",
    "EndeavorAxioms",
    "get_axiom_discovery_service",
]
