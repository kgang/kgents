"""
Voice Crystal: Compressive Proof of Voice Evolution.

This module implements voice-aware crystal compression for the rap-coach pilot.

From PROTO_SPEC:
    "Crystals must state what changed in voice and why, with evidence anchors.
    The crystal is warm - it sees the artist."

Key Laws Implemented:
    L3 Voice Continuity: Crystal summaries identify through-line of voice
    L4 Courage Preservation: High-risk takes protected in crystal
    L5 Repair Path: If loss high, propose repair path - not verdict

Philosophy:
    "Generate crystals that capture the change in voice, not performance metrics.
    The crystal answers: 'Who are you becoming?'"

See: pilots/rap-coach-flow-lab/PROTO_SPEC.md
See: services/witness/crystal.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from services.witness.crystal import (
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from services.witness.honesty import CompressionHonesty, CrystalHonestyCalculator

from .courage_preservation import CourageMoment, CourageProtectionEngine
from .joy_functor import CourageAwareJoyObservation, SessionJoyProfile

if TYPE_CHECKING:
    from services.witness.mark import Mark, MarkId


# =============================================================================
# Voice Delta: What Changed
# =============================================================================


@dataclass(frozen=True)
class VoiceDelta:
    """
    Captures what changed in voice during a session.

    This is the core insight of the VoiceCrystal.
    It answers: "Who are you becoming?"

    Example:
        "Started defensive, but by take 5 was owning the aggressive register."
    """

    description: str  # What changed
    evidence_anchors: tuple[str, ...]  # Take IDs that show the change
    registers_explored: tuple[str, ...]  # Registers touched
    dominant_register: str | None  # Most present register

    @classmethod
    def from_takes(
        cls,
        takes: list[dict[str, Any]],
        descriptions: list[str],
    ) -> "VoiceDelta":
        """
        Create VoiceDelta from a list of takes.

        Args:
            takes: List of take dicts with intent info
            descriptions: Human-readable descriptions of key moments

        Returns:
            VoiceDelta summarizing voice evolution
        """
        # Extract registers
        registers = [
            t.get("intent", {}).get("register", "unknown") for t in takes
        ]
        unique_registers = tuple(sorted(set(registers)))

        # Find dominant register (most frequent)
        if registers:
            from collections import Counter
            register_counts = Counter(registers)
            dominant = register_counts.most_common(1)[0][0]
        else:
            dominant = None

        # Get take IDs for evidence
        evidence = tuple(t.get("take_id", "") for t in takes if t.get("take_id"))

        # Combine descriptions
        description = " ".join(descriptions) if descriptions else "Voice explored new territory."

        return cls(
            description=description,
            evidence_anchors=evidence,
            registers_explored=unique_registers,
            dominant_register=dominant,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "evidence_anchors": list(self.evidence_anchors),
            "registers_explored": list(self.registers_explored),
            "dominant_register": self.dominant_register,
        }


# =============================================================================
# Voice Through-Line (L3)
# =============================================================================


@dataclass(frozen=True)
class VoiceThroughline:
    """
    The through-line of voice across a session (L3 Voice Continuity).

    L3 Law: "Crystal summaries must identify the through-line of voice
    across a session. The artist's thread is never lost."

    The through-line is what stays consistent even as the artist explores.
    It's their unique signature that emerges across takes.
    """

    description: str  # What tied the session together
    core_energy: str  # The persistent quality (e.g., "intensity", "introspection")
    evolution_arc: str  # How it developed (e.g., "built", "deepened", "shifted")

    @classmethod
    def from_session(
        cls,
        takes: list[dict[str, Any]],
        joy_profile: SessionJoyProfile,
    ) -> "VoiceThroughline":
        """
        Identify through-line from session data.

        Args:
            takes: List of takes with intent and content
            joy_profile: Joy observations across session

        Returns:
            VoiceThroughline capturing the artist's thread
        """
        if not takes:
            return cls(
                description="The session awaits.",
                core_energy="potential",
                evolution_arc="beginning",
            )

        # Analyze registers
        registers = [
            t.get("intent", {}).get("register", "unknown") for t in takes
        ]

        # Identify core energy from dominant mode
        if joy_profile.dominant_mode.value == "warmth":
            core_energy = "connection"
        elif joy_profile.dominant_mode.value == "flow":
            core_energy = "momentum"
        else:
            core_energy = "exploration"

        # Analyze evolution
        if len(takes) < 3:
            evolution_arc = "emerging"
        elif joy_profile.flow_trajectory and joy_profile.flow_trajectory[-1] > joy_profile.flow_trajectory[0]:
            evolution_arc = "building"
        else:
            evolution_arc = "deepening"

        # Synthesize description
        unique_registers = set(registers)
        if len(unique_registers) == 1:
            description = f"Stayed in {registers[0]} territory, {evolution_arc} across takes."
        else:
            description = f"Moved through {', '.join(sorted(unique_registers))}, with {core_energy} as the thread."

        return cls(
            description=description,
            core_energy=core_energy,
            evolution_arc=evolution_arc,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "core_energy": self.core_energy,
            "evolution_arc": self.evolution_arc,
        }


# =============================================================================
# Repair Path (L5)
# =============================================================================


@dataclass(frozen=True)
class RepairPath:
    """
    Navigable path forward when loss is high (L5 Repair Path Law).

    L5 Law: "If loss is high, the system proposes a repair path - not a verdict.
    Failure is navigable, not final."

    A repair path is:
    - Specific and actionable
    - Non-judgmental (observation, not evaluation)
    - Referenced to a specific take
    - Possibly paired with a positive example
    """

    observation: str  # What we noticed (not "what you did wrong")
    suggestion: str  # What might be worth trying
    reference_take_id: str  # The take this relates to
    difficulty: str  # "quick_fix", "practice_focus", "longer_journey"
    positive_example_take_id: str | None = None  # Example that worked

    @classmethod
    def from_high_loss_take(
        cls,
        take_id: str,
        galois_loss: float,
        intent_register: str,
        positive_take_id: str | None = None,
    ) -> "RepairPath":
        """
        Create a repair path for a high-loss take.

        Args:
            take_id: The take with high loss
            galois_loss: The loss value (> 0.5 triggers repair)
            intent_register: What register was being attempted
            positive_take_id: Optional take that showed the register working

        Returns:
            RepairPath with navigable suggestion
        """
        # Determine difficulty based on loss
        if galois_loss > 0.7:
            difficulty = "longer_journey"
        elif galois_loss > 0.5:
            difficulty = "practice_focus"
        else:
            difficulty = "quick_fix"

        # Generate observation (non-judgmental)
        observation = f"The {intent_register} register took some time to land there."

        # Generate suggestion
        suggestions_by_register = {
            "aggressive": "Try grounding the energy in breath before pushing intensity.",
            "vulnerable": "Consider starting smaller - vulnerability builds.",
            "experimental": "What if you tried the experiment in smaller chunks?",
            "playful": "Sometimes playfulness needs momentum - try building up to it.",
            "introspective": "Introspection often deepens with repetition of the same phrase.",
            "storytelling": "The story might land clearer with stronger connective words.",
            "technical": "Technical runs sometimes need slower practice first.",
        }

        suggestion = suggestions_by_register.get(
            intent_register,
            "What would it feel like to try that again with fresh ears?",
        )

        return cls(
            observation=observation,
            suggestion=suggestion,
            reference_take_id=take_id,
            difficulty=difficulty,
            positive_example_take_id=positive_take_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "observation": self.observation,
            "suggestion": self.suggestion,
            "reference_take_id": self.reference_take_id,
            "difficulty": self.difficulty,
            "positive_example_take_id": self.positive_example_take_id,
        }


# =============================================================================
# VoiceCrystal: The Complete Crystal
# =============================================================================


@dataclass(frozen=True)
class VoiceCrystal:
    """
    Compressive proof of voice evolution.

    This extends the base Crystal with:
    - Voice delta (what changed)
    - Voice through-line (L3)
    - Courage moments (L4)
    - Repair paths (L5)
    - Warmth disclosure (never cold)

    The VoiceCrystal answers: "Who are you becoming?"
    """

    crystal_id: CrystalId
    session_id: str
    voice_delta: VoiceDelta
    voice_throughline: VoiceThroughline
    courage_moments: tuple[CourageMoment, ...]
    repair_paths: tuple[RepairPath, ...]
    mood: MoodVector
    warmth_disclosure: str
    compression_honesty: CompressionHonesty
    galois_loss: float
    source_take_ids: tuple[str, ...]
    crystallized_at: datetime = field(default_factory=datetime.now)

    @classmethod
    async def from_session(
        cls,
        session_id: str,
        takes: list[dict[str, Any]],
        joy_profile: SessionJoyProfile,
        courage_engine: CourageProtectionEngine,
        marks: list["Mark"],
    ) -> "VoiceCrystal":
        """
        Create a VoiceCrystal from a completed session.

        This is the main crystallization method that:
        1. Computes voice delta
        2. Identifies through-line (L3)
        3. Preserves courage moments (L4)
        4. Generates repair paths for high-loss takes (L5)
        5. Creates warm disclosure

        Args:
            session_id: Session identifier
            takes: List of takes with intent and content
            joy_profile: Aggregated joy observations
            courage_engine: Engine with captured courage moments
            marks: Witness marks for the session

        Returns:
            VoiceCrystal capturing the session's voice evolution
        """
        # Generate voice descriptions from takes
        descriptions = []
        if takes:
            first_register = takes[0].get("intent", {}).get("register", "unknown")
            last_register = takes[-1].get("intent", {}).get("register", "unknown")
            if first_register != last_register:
                descriptions.append(
                    f"Started in {first_register}, moved to {last_register}."
                )
            else:
                descriptions.append(f"Committed to {first_register} throughout.")

        # Create voice delta
        voice_delta = VoiceDelta.from_takes(takes, descriptions)

        # Create through-line (L3)
        voice_throughline = VoiceThroughline.from_session(takes, joy_profile)

        # Get courage moments (L4)
        courage_moments = tuple(courage_engine.get_session_moments())

        # Generate repair paths for high-loss takes (L5)
        repair_paths: list[RepairPath] = []
        # For now, we'd need actual Galois loss per take
        # This would be computed from intent vs delivery
        # Placeholder: no repair paths in this generation

        # Compute mood from marks
        mood = MoodVector.from_marks(marks)

        # Generate warmth disclosure
        warmth_disclosure = cls._generate_warmth_disclosure(
            takes=takes,
            courage_count=len(courage_moments),
            joy_intensity=joy_profile.average_intensity,
        )

        # Compute compression honesty
        honesty_calc = CrystalHonestyCalculator()
        # Create a placeholder base crystal for honesty computation
        base_crystal = Crystal.from_crystallization(
            insight=voice_delta.description,
            significance=voice_throughline.description,
            principles=["courage", "voice"],
            source_marks=[m.id for m in marks],
            time_range=(
                marks[0].timestamp if marks else datetime.now(),
                marks[-1].timestamp if marks else datetime.now(),
            ),
        )
        compression_honesty = await honesty_calc.compute_honesty(
            original_marks=marks,
            crystal=base_crystal,
        )

        # Take IDs
        source_take_ids = tuple(t.get("take_id", "") for t in takes if t.get("take_id"))

        return cls(
            crystal_id=generate_crystal_id(),
            session_id=session_id,
            voice_delta=voice_delta,
            voice_throughline=voice_throughline,
            courage_moments=courage_moments,
            repair_paths=tuple(repair_paths),
            mood=mood,
            warmth_disclosure=warmth_disclosure,
            compression_honesty=compression_honesty,
            galois_loss=compression_honesty.galois_loss,
            source_take_ids=source_take_ids,
        )

    @staticmethod
    def _generate_warmth_disclosure(
        takes: list[dict[str, Any]],
        courage_count: int,
        joy_intensity: float,
    ) -> str:
        """
        Generate warmth disclosure for the crystal.

        The crystal is warm - it sees the artist.
        This disclosure should never read like a report.
        """
        if not takes:
            return "The session awaits your voice."

        take_count = len(takes)

        if courage_count > 0 and joy_intensity > 0.6:
            return (
                f"You brought {take_count} takes and {courage_count} moments of courage. "
                "The voice was alive. Keep that energy."
            )
        elif courage_count > 0:
            return (
                f"{take_count} takes, {courage_count} risks taken. "
                "The courage is the practice. Everything else follows."
            )
        elif joy_intensity > 0.7:
            return (
                f"{take_count} takes and flow was present. "
                "You found something in there."
            )
        elif joy_intensity > 0.5:
            return (
                f"{take_count} takes, building blocks laid. "
                "The work is happening."
            )
        else:
            return (
                f"You showed up for {take_count} takes. "
                "That's the practice. See you next time."
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "crystal_id": str(self.crystal_id),
            "session_id": self.session_id,
            "voice_delta": self.voice_delta.to_dict(),
            "voice_throughline": self.voice_throughline.to_dict(),
            "courage_moments": [m.to_dict() for m in self.courage_moments],
            "repair_paths": [p.to_dict() for p in self.repair_paths],
            "mood": self.mood.to_dict(),
            "warmth_disclosure": self.warmth_disclosure,
            "compression_honesty": self.compression_honesty.to_dict(),
            "galois_loss": self.galois_loss,
            "source_take_ids": list(self.source_take_ids),
            "crystallized_at": self.crystallized_at.isoformat(),
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "VoiceDelta",
    "VoiceThroughline",
    "RepairPath",
    "VoiceCrystal",
]
