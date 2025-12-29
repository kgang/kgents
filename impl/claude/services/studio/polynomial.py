"""
StudioPolynomial -- State Machine for Creative Production Studio.

The Studio polynomial models the creative production pipeline as a
mode-dependent state machine following AD-002 (Polynomial Generalization).

States:
- ARCHAEOLOGY: Excavating raw materials, extracting patterns
- SYNTHESIS: Generating creative vision, style guide
- PRODUCTION: Creating assets (sprites, audio, etc.)
- REVIEW: Quality assurance, iteration
- DELIVERY: Export, handoff, gallery placement

The Two-Functor Pipeline:
    f(Principles, Archaeology) -> (Vision, Strategy)
    f(Vision | Strategy) -> (Creative Assets | Art Assets)

Teaching:
    gotcha: The polynomial defines DIRECTION SETS (valid inputs per state).
            studio_directions(phase) returns FrozenSet[InputType] -- the
            inputs that are legal to receive in each phase. This is the
            type-safe way to enforce state machine invariants.

    gotcha: PRODUCTION is only reachable from SYNTHESIS after vision is
            established. You cannot produce assets without a creative vision.
            This is encoded in VALID_TRANSITIONS.

    gotcha: REVIEW phase can loop back to PRODUCTION (via iterate) or
            advance to DELIVERY. This enables the create-review-refine cycle.

Example:
    >>> fsm = StudioStateMachine()
    >>> fsm.state
    StudioPhase.ARCHAEOLOGY
    >>> fsm.transition(StudioPhase.SYNTHESIS, StudioEvent.FINDINGS_COMPLETE)
    True
    >>> STUDIO_POLYNOMIAL.valid_inputs(StudioPhase.PRODUCTION)
    frozenset({ProduceInput, AssetTypeInput, StyleInput, type, Any})

See: spec/s-gents/studio.md, spec/principles.md (AD-002)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Studio Phase (Positions in the Polynomial)
# =============================================================================


class StudioPhase(Enum):
    """
    Positions in the studio polynomial.

    These phases represent the creative production pipeline:
    - ARCHAEOLOGY: Excavating raw materials, extracting patterns
    - SYNTHESIS: Generating creative vision, style guide
    - PRODUCTION: Creating assets (sprites, audio, etc.)
    - REVIEW: Quality assurance, iteration
    - DELIVERY: Export, handoff, gallery placement

    From the spec: The studio is a two-functor pipeline.
    Archaeology extracts vision, Production synthesizes assets.
    """

    ARCHAEOLOGY = auto()  # Excavating raw materials, extracting patterns
    SYNTHESIS = auto()  # Generating creative vision, style guide
    PRODUCTION = auto()  # Creating assets (sprites, audio, etc.)
    REVIEW = auto()  # Quality assurance, iteration
    DELIVERY = auto()  # Export, handoff, gallery placement

    @property
    def is_terminal(self) -> bool:
        """True if this phase can end a production cycle."""
        return self == StudioPhase.DELIVERY

    @property
    def is_creative(self) -> bool:
        """True if this phase involves creative decision-making."""
        return self in (StudioPhase.ARCHAEOLOGY, StudioPhase.SYNTHESIS)

    @property
    def is_production(self) -> bool:
        """True if this phase produces concrete artifacts."""
        return self in (StudioPhase.PRODUCTION, StudioPhase.DELIVERY)


# =============================================================================
# Event Types (Triggers for State Transitions)
# =============================================================================


class StudioEvent(Enum):
    """Events that trigger state transitions in the Studio."""

    # Archaeology events
    START_EXCAVATION = auto()  # Begin archaeology phase
    FINDINGS_COMPLETE = auto()  # Archaeological findings ready

    # Synthesis events
    START_SYNTHESIS = auto()  # Begin vision synthesis
    VISION_SYNTHESIZED = auto()  # Creative vision established
    STYLE_CODIFIED = auto()  # Style guide created

    # Production events
    START_PRODUCTION = auto()  # Begin asset production
    ASSET_PRODUCED = auto()  # Asset created
    ASSET_REFINED = auto()  # Asset improved with feedback

    # Review events
    START_REVIEW = auto()  # Begin quality review
    REVIEW_PASSED = auto()  # Quality check passed
    REVIEW_FAILED = auto()  # Quality check failed, needs iteration

    # Delivery events
    START_DELIVERY = auto()  # Begin delivery phase
    ASSET_EXPORTED = auto()  # Asset exported to format
    GALLERY_PLACED = auto()  # Asset placed in gallery
    HANDOFF_COMPLETE = auto()  # Handoff to consumer complete

    # Control events
    RESET = auto()  # Return to ARCHAEOLOGY
    ERROR = auto()  # Error occurred


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class ExcavateInput:
    """Input for excavation operation."""

    sources: tuple[str, ...]  # Source paths or identifiers
    focus: str = "visual"  # VISUAL, AUDIO, NARRATIVE, MECHANICAL, EMOTIONAL


@dataclass(frozen=True)
class SourceInput:
    """Input for adding a source to excavation."""

    path: str
    source_type: str = "file"  # file, url, reference


@dataclass(frozen=True)
class FocusInput:
    """Input for setting archaeology focus."""

    focus_type: str  # VISUAL, AUDIO, NARRATIVE, MECHANICAL, EMOTIONAL
    priority: float = 1.0


@dataclass(frozen=True)
class SynthesizeInput:
    """Input for vision synthesis."""

    findings_id: str  # Reference to archaeological findings
    principles: tuple[str, ...] = ()  # Design principles to apply


@dataclass(frozen=True)
class PrincipleInput:
    """Input for adding a design principle."""

    name: str
    description: str
    priority: float = 1.0


@dataclass(frozen=True)
class VisionInput:
    """Input referencing an existing vision."""

    vision_id: str


@dataclass(frozen=True)
class ProduceInput:
    """Input for asset production."""

    vision_id: str
    requirement: str
    asset_type: str  # sprite, animation, audio, graphic, video, writing


@dataclass(frozen=True)
class AssetTypeInput:
    """Input for specifying asset type."""

    asset_type: str
    specs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StyleInput:
    """Input for applying style constraints."""

    style_guide_id: str
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReviewInput:
    """Input for quality review."""

    asset_id: str
    criteria: tuple[str, ...] = ()  # Quality criteria to check


@dataclass(frozen=True)
class FeedbackInput:
    """Input for providing feedback on an asset."""

    asset_id: str
    feedback: str
    severity: str = "minor"  # minor, major, critical


@dataclass(frozen=True)
class IterateInput:
    """Input for iterating on an asset after review."""

    asset_id: str
    changes_requested: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExportInput:
    """Input for exporting an asset."""

    asset_id: str
    format: str  # png, ogg, mp4, json, etc.
    optimization: str = "balanced"  # none, balanced, aggressive


@dataclass(frozen=True)
class GalleryInput:
    """Input for gallery placement."""

    asset_id: str
    placement: str = "showcase"  # showcase, archive, work-in-progress


@dataclass(frozen=True)
class HandoffInput:
    """Input for handoff to consumer."""

    asset_ids: tuple[str, ...]
    destination: str
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class StudioOutput:
    """Output from studio transitions."""

    phase: StudioPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    artifact_id: str | None = None  # ID of produced artifact, if any


@dataclass
class DeliveryOutput(StudioOutput):
    """Output from delivery phase."""

    exported_path: str | None = None
    gallery_placement: str | None = None
    handoff_destination: str | None = None


# =============================================================================
# Valid State Transitions
# =============================================================================


VALID_TRANSITIONS: dict[StudioPhase, set[StudioPhase]] = {
    StudioPhase.ARCHAEOLOGY: {
        StudioPhase.SYNTHESIS,  # Findings complete, synthesize vision
        StudioPhase.ARCHAEOLOGY,  # Continue excavating (add more sources)
    },
    StudioPhase.SYNTHESIS: {
        StudioPhase.PRODUCTION,  # Vision established, start producing
        StudioPhase.ARCHAEOLOGY,  # Need more findings, go back
        StudioPhase.SYNTHESIS,  # Refine vision
    },
    StudioPhase.PRODUCTION: {
        StudioPhase.REVIEW,  # Asset ready for review
        StudioPhase.PRODUCTION,  # Continue producing (more assets)
        StudioPhase.SYNTHESIS,  # Vision needs adjustment
    },
    StudioPhase.REVIEW: {
        StudioPhase.DELIVERY,  # Review passed, deliver
        StudioPhase.PRODUCTION,  # Review failed, iterate
        StudioPhase.REVIEW,  # Continue reviewing (more assets)
    },
    StudioPhase.DELIVERY: {
        StudioPhase.ARCHAEOLOGY,  # Start new production cycle
        StudioPhase.DELIVERY,  # Continue delivering (more exports)
    },
}


def can_transition(from_phase: StudioPhase, to_phase: StudioPhase) -> bool:
    """Check if a phase transition is valid."""
    return to_phase in VALID_TRANSITIONS.get(from_phase, set())


def get_valid_next_phases(phase: StudioPhase) -> set[StudioPhase]:
    """Get all valid next phases from current phase."""
    return VALID_TRANSITIONS.get(phase, set())


# Alias for consistency with spec
get_valid_next_states = get_valid_next_phases


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def studio_directions(phase: StudioPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each studio phase.

    This encodes the mode-dependent behavior:
    - ARCHAEOLOGY: Excavation-related inputs
    - SYNTHESIS: Vision and principle inputs
    - PRODUCTION: Asset creation inputs
    - REVIEW: Quality and feedback inputs
    - DELIVERY: Export and handoff inputs

    The direction function is the core polynomial insight:
    different phases accept different inputs.
    """
    match phase:
        case StudioPhase.ARCHAEOLOGY:
            return frozenset({ExcavateInput, SourceInput, FocusInput, type, Any})
        case StudioPhase.SYNTHESIS:
            return frozenset({SynthesizeInput, PrincipleInput, VisionInput, type, Any})
        case StudioPhase.PRODUCTION:
            return frozenset({ProduceInput, AssetTypeInput, StyleInput, type, Any})
        case StudioPhase.REVIEW:
            return frozenset({ReviewInput, FeedbackInput, IterateInput, type, Any})
        case StudioPhase.DELIVERY:
            return frozenset({ExportInput, GalleryInput, HandoffInput, type, Any})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def studio_transition(phase: StudioPhase, input: Any) -> tuple[StudioPhase, StudioOutput]:
    """
    Studio state transition function.

    This is the polynomial core:
    transition: Phase x Input -> (NewPhase, Output)

    From the spec: The studio is a two-functor pipeline.
    Phase transitions move between the pipeline stages.
    """
    match phase:
        case StudioPhase.ARCHAEOLOGY:
            if isinstance(input, ExcavateInput):
                return StudioPhase.ARCHAEOLOGY, StudioOutput(
                    phase=StudioPhase.ARCHAEOLOGY,
                    success=True,
                    message=f"Excavating {len(input.sources)} sources with {input.focus} focus",
                    metadata={
                        "sources": input.sources,
                        "focus": input.focus,
                    },
                )
            elif isinstance(input, SourceInput):
                return StudioPhase.ARCHAEOLOGY, StudioOutput(
                    phase=StudioPhase.ARCHAEOLOGY,
                    success=True,
                    message=f"Added source: {input.path}",
                    metadata={"source": input.path, "type": input.source_type},
                )
            elif isinstance(input, FocusInput):
                return StudioPhase.ARCHAEOLOGY, StudioOutput(
                    phase=StudioPhase.ARCHAEOLOGY,
                    success=True,
                    message=f"Set focus to {input.focus_type}",
                    metadata={"focus": input.focus_type, "priority": input.priority},
                )
            elif isinstance(input, SynthesizeInput):
                # Ready to synthesize, transition to SYNTHESIS
                return StudioPhase.SYNTHESIS, StudioOutput(
                    phase=StudioPhase.SYNTHESIS,
                    success=True,
                    message="Archaeology complete, beginning synthesis",
                    metadata={"findings_id": input.findings_id},
                )
            else:
                return StudioPhase.ARCHAEOLOGY, StudioOutput(
                    phase=StudioPhase.ARCHAEOLOGY,
                    success=False,
                    message=f"Invalid input for ARCHAEOLOGY: {type(input).__name__}",
                )

        case StudioPhase.SYNTHESIS:
            if isinstance(input, SynthesizeInput):
                return StudioPhase.SYNTHESIS, StudioOutput(
                    phase=StudioPhase.SYNTHESIS,
                    success=True,
                    message="Synthesizing vision from findings",
                    metadata={
                        "findings_id": input.findings_id,
                        "principles": input.principles,
                    },
                )
            elif isinstance(input, PrincipleInput):
                return StudioPhase.SYNTHESIS, StudioOutput(
                    phase=StudioPhase.SYNTHESIS,
                    success=True,
                    message=f"Added principle: {input.name}",
                    metadata={"principle": input.name, "priority": input.priority},
                )
            elif isinstance(input, VisionInput):
                return StudioPhase.SYNTHESIS, StudioOutput(
                    phase=StudioPhase.SYNTHESIS,
                    success=True,
                    message=f"Using existing vision: {input.vision_id}",
                    metadata={"vision_id": input.vision_id},
                )
            elif isinstance(input, ProduceInput):
                # Vision established, transition to PRODUCTION
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=True,
                    message="Vision synthesized, beginning production",
                    metadata={"vision_id": input.vision_id},
                )
            else:
                return StudioPhase.SYNTHESIS, StudioOutput(
                    phase=StudioPhase.SYNTHESIS,
                    success=False,
                    message=f"Invalid input for SYNTHESIS: {type(input).__name__}",
                )

        case StudioPhase.PRODUCTION:
            if isinstance(input, ProduceInput):
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=True,
                    message=f"Producing {input.asset_type}: {input.requirement}",
                    metadata={
                        "vision_id": input.vision_id,
                        "asset_type": input.asset_type,
                        "requirement": input.requirement,
                    },
                )
            elif isinstance(input, AssetTypeInput):
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=True,
                    message=f"Set asset type: {input.asset_type}",
                    metadata={"asset_type": input.asset_type, "specs": input.specs},
                )
            elif isinstance(input, StyleInput):
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=True,
                    message=f"Applied style guide: {input.style_guide_id}",
                    metadata={
                        "style_guide_id": input.style_guide_id,
                        "overrides": input.overrides,
                    },
                )
            elif isinstance(input, ReviewInput):
                # Asset ready, transition to REVIEW
                return StudioPhase.REVIEW, StudioOutput(
                    phase=StudioPhase.REVIEW,
                    success=True,
                    message="Asset produced, beginning review",
                    metadata={"asset_id": input.asset_id},
                )
            else:
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=False,
                    message=f"Invalid input for PRODUCTION: {type(input).__name__}",
                )

        case StudioPhase.REVIEW:
            if isinstance(input, ReviewInput):
                return StudioPhase.REVIEW, StudioOutput(
                    phase=StudioPhase.REVIEW,
                    success=True,
                    message=f"Reviewing asset: {input.asset_id}",
                    metadata={"asset_id": input.asset_id, "criteria": input.criteria},
                )
            elif isinstance(input, FeedbackInput):
                return StudioPhase.REVIEW, StudioOutput(
                    phase=StudioPhase.REVIEW,
                    success=True,
                    message=f"Feedback recorded: {input.severity}",
                    metadata={
                        "asset_id": input.asset_id,
                        "feedback": input.feedback,
                        "severity": input.severity,
                    },
                )
            elif isinstance(input, IterateInput):
                # Review failed, go back to PRODUCTION
                return StudioPhase.PRODUCTION, StudioOutput(
                    phase=StudioPhase.PRODUCTION,
                    success=True,
                    message="Iterating on asset",
                    metadata={
                        "asset_id": input.asset_id,
                        "changes": input.changes_requested,
                    },
                )
            elif isinstance(input, ExportInput):
                # Review passed, transition to DELIVERY
                return StudioPhase.DELIVERY, DeliveryOutput(
                    phase=StudioPhase.DELIVERY,
                    success=True,
                    message="Review passed, beginning delivery",
                    metadata={"asset_id": input.asset_id},
                )
            else:
                return StudioPhase.REVIEW, StudioOutput(
                    phase=StudioPhase.REVIEW,
                    success=False,
                    message=f"Invalid input for REVIEW: {type(input).__name__}",
                )

        case StudioPhase.DELIVERY:
            if isinstance(input, ExportInput):
                return StudioPhase.DELIVERY, DeliveryOutput(
                    phase=StudioPhase.DELIVERY,
                    success=True,
                    message=f"Exported to {input.format}",
                    metadata={
                        "asset_id": input.asset_id,
                        "format": input.format,
                        "optimization": input.optimization,
                    },
                    exported_path=f"{input.asset_id}.{input.format}",
                )
            elif isinstance(input, GalleryInput):
                return StudioPhase.DELIVERY, DeliveryOutput(
                    phase=StudioPhase.DELIVERY,
                    success=True,
                    message=f"Placed in gallery: {input.placement}",
                    metadata={"asset_id": input.asset_id, "placement": input.placement},
                    gallery_placement=input.placement,
                )
            elif isinstance(input, HandoffInput):
                return StudioPhase.DELIVERY, DeliveryOutput(
                    phase=StudioPhase.DELIVERY,
                    success=True,
                    message=f"Handed off to {input.destination}",
                    metadata={
                        "asset_ids": input.asset_ids,
                        "destination": input.destination,
                    },
                    handoff_destination=input.destination,
                )
            elif isinstance(input, ExcavateInput):
                # Start new cycle, transition to ARCHAEOLOGY
                return StudioPhase.ARCHAEOLOGY, StudioOutput(
                    phase=StudioPhase.ARCHAEOLOGY,
                    success=True,
                    message="Starting new production cycle",
                    metadata={"sources": input.sources},
                )
            else:
                return StudioPhase.DELIVERY, StudioOutput(
                    phase=StudioPhase.DELIVERY,
                    success=False,
                    message=f"Invalid input for DELIVERY: {type(input).__name__}",
                )

        case _:
            return phase, StudioOutput(
                phase=phase,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# Transition Record
# =============================================================================


@dataclass(frozen=True)
class StudioTransition:
    """Record of a phase transition."""

    from_phase: StudioPhase
    to_phase: StudioPhase
    event: StudioEvent
    payload: dict[str, Any] | None = None


# =============================================================================
# State Machine (Convenience Wrapper)
# =============================================================================


class StudioStateMachine:
    """
    State machine for tracking Studio pipeline progress.

    This is a simple state machine that tracks the current phase
    and validates transitions. The actual work is done by the
    CreativeStudioService orchestrator.
    """

    def __init__(self, initial_phase: StudioPhase = StudioPhase.ARCHAEOLOGY) -> None:
        self._phase = initial_phase
        self._history: list[StudioTransition] = []

    @property
    def phase(self) -> StudioPhase:
        """Current phase."""
        return self._phase

    # Alias for compatibility
    @property
    def state(self) -> StudioPhase:
        """Current state (alias for phase)."""
        return self._phase

    @property
    def history(self) -> list[StudioTransition]:
        """Transition history."""
        return self._history.copy()

    def transition(
        self,
        to_phase: StudioPhase,
        event: StudioEvent,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        """
        Attempt to transition to a new phase.

        Returns True if transition was successful, False if invalid.
        """
        if not can_transition(self._phase, to_phase):
            return False

        transition = StudioTransition(
            from_phase=self._phase,
            to_phase=to_phase,
            event=event,
            payload=payload,
        )
        self._history.append(transition)
        self._phase = to_phase
        return True

    def reset(self) -> None:
        """Reset to ARCHAEOLOGY phase."""
        if self._phase != StudioPhase.ARCHAEOLOGY:
            self._history.append(
                StudioTransition(
                    from_phase=self._phase,
                    to_phase=StudioPhase.ARCHAEOLOGY,
                    event=StudioEvent.RESET,
                )
            )
        self._phase = StudioPhase.ARCHAEOLOGY

    def fail(self, error: str) -> None:
        """Record an error (stays in current phase)."""
        self._history.append(
            StudioTransition(
                from_phase=self._phase,
                to_phase=self._phase,
                event=StudioEvent.ERROR,
                payload={"error": error},
            )
        )


# =============================================================================
# Polynomial Definition (AD-002 Pattern)
# =============================================================================


@dataclass(frozen=True)
class StudioPolynomial:
    """
    Polynomial functor for the Studio.

    P(y) = sum_{s in positions} y^{directions(s)}

    This captures the mode-dependent behavior of the Studio:
    different phases accept different inputs (inputs).
    """

    positions: FrozenSet[StudioPhase]
    directions: Callable[[StudioPhase], FrozenSet[Any]]

    def valid_inputs(self, phase: StudioPhase) -> FrozenSet[Any]:
        """Get valid inputs for a phase."""
        if phase not in self.positions:
            return frozenset()
        return self.directions(phase)


# The singleton polynomial for Studio
STUDIO_POLYNOMIAL = StudioPolynomial(
    positions=frozenset(StudioPhase),
    directions=studio_directions,
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Phase/State
    "StudioPhase",
    "StudioEvent",
    "StudioTransition",
    "StudioStateMachine",
    # Polynomial
    "StudioPolynomial",
    "STUDIO_POLYNOMIAL",
    # Direction/Transition Functions
    "studio_directions",
    "studio_transition",
    # Transition Helpers
    "can_transition",
    "get_valid_next_states",
    "get_valid_next_phases",
    "VALID_TRANSITIONS",
    # Input Types
    "ExcavateInput",
    "SourceInput",
    "FocusInput",
    "SynthesizeInput",
    "PrincipleInput",
    "VisionInput",
    "ProduceInput",
    "AssetTypeInput",
    "StyleInput",
    "ReviewInput",
    "FeedbackInput",
    "IterateInput",
    "ExportInput",
    "GalleryInput",
    "HandoffInput",
    # Output Types
    "StudioOutput",
    "DeliveryOutput",
]
