"""
Muse Orchestrator: The Co-Creative Engine.

From muse.md:
    "The co-creative engine coordinates amplification, selection,
    contradiction, and crystallization into a coherent workflow."

The orchestrator manages:
1. Session lifecycle (ground → spark → spiral → crystallize → witness)
2. Agent coordination (taste, contradictor, ghost, checkpoint)
3. Iteration tracking (30-50 principle)
4. Escape velocity detection

See: spec/c-gent/muse.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Generic, TypeVar, Union

from ..agents import (
    CheckpointAgent,
    ContradictorAgent,
    GhostAnalysis,
    GhostAnalyzerAgent,
    MirrorTestResult,
    ResurrectionCandidate,
    TasteVectorAgent,
)
from ..checkpoints import (
    Checkpoint,
    CheckpointResult,
    CoCreativeMode,
)
from ..models import (
    ITERATION_MILESTONES,
    KENT_TASTE_DEFAULT,
    VOLUME_TARGETS,
    Contradiction,
    CreativeOption,
    DefenseResponse,
    Ghost,
    ResonanceLevel,
    SessionPhase,
    SessionState,
    TasteVector,
)

T = TypeVar("T")


# =============================================================================
# Orchestrator Configuration
# =============================================================================


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""

    # Iteration targets
    min_iterations: int = 30
    target_iterations: int = 50
    max_iterations: int = 100

    # Volume targets
    default_volume: int = 50
    volume_targets: dict[str, int] = field(default_factory=lambda: VOLUME_TARGETS.copy())

    # Resonance thresholds
    escape_velocity_threshold: ResonanceLevel = ResonanceLevel.PROFOUND
    minimum_ship_resonance: ResonanceLevel = ResonanceLevel.RESONANT

    # Contradiction settings
    contradict_every_selection: bool = True
    max_consecutive_defenses: int = 5  # Force pivot after this many

    # Checkpoint enforcement
    enforce_checkpoints: bool = True
    allow_checkpoint_skip: bool = False


# =============================================================================
# Session Events (for callbacks/hooks)
# =============================================================================


@dataclass
class SessionEvent:
    """Base class for session events."""

    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IterationEvent:
    """Event fired after each iteration."""

    session_id: str
    iteration: int
    milestone: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SelectionEvent:
    """Event fired when Kent makes a selection."""

    session_id: str
    iteration: int
    selected_id: str
    ghost_count: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContradictionEvent:
    """Event fired when AI contradicts."""

    session_id: str
    iteration: int
    move: str
    challenge: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BreakthroughEvent:
    """Event fired when escape velocity is reached."""

    session_id: str
    iteration: int
    resonance: ResonanceLevel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CheckpointEvent:
    """Event fired at checkpoint completion."""

    session_id: str
    checkpoint_number: int
    checkpoint_name: str
    passed: bool
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Muse Orchestrator
# =============================================================================


class MuseOrchestrator(Generic[T]):
    """
    The Co-Creative Engine Orchestrator.

    Coordinates the full creative workflow:
    1. GROUND: Establish constraints and context
    2. SPARK: Kent provides initial direction
    3. SPIRAL: Iterative diverge-converge cycles
    4. CRYSTALLIZE: Lock in the breakthrough
    5. WITNESS: Record what worked

    The orchestrator manages all cross-cutting agents and ensures
    the 30-50 iteration principle is enforced.
    """

    def __init__(
        self,
        domain: str,
        config: OrchestratorConfig | None = None,
        taste: TasteVector | None = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            domain: The domain ("youtube", "little_kant")
            config: Configuration options
            taste: Initial taste vector
        """
        self.domain = domain
        self.config = config or OrchestratorConfig()

        # Initialize agents
        self.taste_agent = TasteVectorAgent(taste=taste or KENT_TASTE_DEFAULT)
        self.contradictor = ContradictorAgent()
        self.ghost_analyzer = GhostAnalyzerAgent()
        self.checkpoint_agent = CheckpointAgent(domain)

        # Session state
        self.session: SessionState[T] | None = None

        # Event callbacks
        self._event_handlers: dict[type, list[Callable[..., Any]]] = {}

        # Consecutive defense counter
        self._consecutive_defenses = 0

    # -------------------------------------------------------------------------
    # Session Lifecycle
    # -------------------------------------------------------------------------

    def start_session(self, spark: str) -> SessionState[T]:
        """
        Start a new co-creative session.

        Args:
            spark: The initial creative direction

        Returns:
            New session state
        """
        self.session = SessionState[T](
            id=f"session_{uuid.uuid4().hex[:8]}",
            phase=SessionPhase.SPARK,
            spark=spark,
            target_iterations=self.config.target_iterations,
            taste=self.taste_agent.taste,
        )

        self._consecutive_defenses = 0
        return self.session

    def ground(self, constraints: dict[str, Any]) -> None:
        """
        Establish session constraints.

        Args:
            constraints: Dictionary of constraints to apply
        """
        if self.session is None:
            raise ValueError("No active session")

        self.session.phase = SessionPhase.GROUND
        # Apply constraints to session (could extend SessionState)

    def enter_spiral(self) -> None:
        """Enter the spiral phase (iterative diverge-converge)."""
        if self.session is None:
            raise ValueError("No active session")

        self.session.phase = SessionPhase.SPIRAL

    # -------------------------------------------------------------------------
    # Core Loop Operations
    # -------------------------------------------------------------------------

    def amplify(
        self,
        element: str,
        generator: Callable[[int], list[CreativeOption[T]]],
    ) -> list[CreativeOption[T]]:
        """
        Generate options using the volume principle.

        Args:
            element: What type of element to generate
            generator: Function that generates N options

        Returns:
            List of creative options
        """
        volume = self.config.volume_targets.get(element, self.config.default_volume)
        return generator(volume)

    def select(
        self,
        options: list[CreativeOption[T]],
        selected_id: str,
        reason: str = "",
    ) -> tuple[CreativeOption[T], list[Ghost[T]]]:
        """
        Record a selection and create ghosts.

        Args:
            options: All options that were available
            selected_id: ID of the selected option
            reason: Why this was selected

        Returns:
            Tuple of (selected option, list of ghosts)
        """
        if self.session is None:
            raise ValueError("No active session")

        # Find selected
        selected = None
        ghosts: list[Ghost[T]] = []

        for option in options:
            if option.id == selected_id:
                selected = option
            else:
                # Create ghost
                ghost = self.ghost_analyzer.record_rejection(
                    option=option,
                    rejection_reason=f"Not selected; {reason}" if reason else "Not selected",
                    rejection_strength=0.5,
                    ai_championed=option.novelty_score > 0.7,
                    ai_surprise=option.novelty_score,
                    iteration=self.session.iteration,
                )
                ghosts.append(ghost)
                self.session.add_ghost(ghost)

        if selected is None:
            raise ValueError(f"No option found with id {selected_id}")

        # Record selection
        self.session.selections.append((self.session.iteration, selected_id))

        # Fire event
        self._fire_event(
            SelectionEvent(
                session_id=self.session.id,
                iteration=self.session.iteration,
                selected_id=selected_id,
                ghost_count=len(ghosts),
            )
        )

        return selected, ghosts

    def contradict(
        self,
        selection: T,
    ) -> Contradiction:
        """
        Generate a contradiction for the selection.

        Args:
            selection: What Kent selected

        Returns:
            Contradiction challenge
        """
        if self.session is None:
            raise ValueError("No active session")

        contradiction = self.contradictor.contradict(
            selection=selection,
            session=self.session,
        )

        self.session.contradictions.append(contradiction)

        # Fire event
        self._fire_event(
            ContradictionEvent(
                session_id=self.session.id,
                iteration=self.session.iteration,
                move=contradiction.move.name,
                challenge=contradiction.challenge,
            )
        )

        return contradiction

    def respond_to_contradiction(
        self,
        contradiction: Contradiction,
        defended: bool,
        reasoning: str,
        conviction: float = 0.5,
        new_direction: str | None = None,
    ) -> DefenseResponse:
        """
        Record Kent's response to a contradiction.

        Args:
            contradiction: The contradiction being responded to
            defended: True if defending, False if pivoting
            reasoning: Why defend or pivot
            conviction: Strength of conviction (0-1)
            new_direction: If pivoting, what's the new direction

        Returns:
            DefenseResponse
        """
        if self.session is None:
            raise ValueError("No active session")

        response = DefenseResponse(
            defended=defended,
            reasoning=reasoning,
            conviction_strength=conviction,
            new_direction=new_direction,
        )

        self.session.defenses.append(response)

        # Track consecutive defenses
        if defended:
            self._consecutive_defenses += 1
            if self._consecutive_defenses >= self.config.max_consecutive_defenses:
                # Force consideration of pivot
                pass  # Could trigger a stronger contradiction
        else:
            self._consecutive_defenses = 0

        # Record outcome in contradictor
        self.contradictor.record_outcome(contradiction, response)

        return response

    def mirror_test(self, work: T) -> MirrorTestResult:
        """
        Apply the Mirror Test to current work.

        Args:
            work: The creative work to evaluate

        Returns:
            MirrorTestResult
        """
        if self.session is None:
            raise ValueError("No active session")

        result = self.taste_agent.mirror_test(work)
        self.session.add_resonance(result.level)

        # Check for escape velocity
        if result.level >= self.config.escape_velocity_threshold:
            self._fire_event(
                BreakthroughEvent(
                    session_id=self.session.id,
                    iteration=self.session.iteration,
                    resonance=result.level,
                )
            )

        return result

    def advance_iteration(self) -> str:
        """
        Advance to the next iteration.

        Returns:
            Milestone description if at a milestone, empty string otherwise
        """
        if self.session is None:
            raise ValueError("No active session")

        milestone = self.session.advance_iteration()

        self._fire_event(
            IterationEvent(
                session_id=self.session.id,
                iteration=self.session.iteration,
                milestone=milestone,
            )
        )

        return milestone

    # -------------------------------------------------------------------------
    # Checkpoint Integration
    # -------------------------------------------------------------------------

    def execute_checkpoint(
        self,
        work: T,
    ) -> tuple[CheckpointResult, CoCreativeMode]:
        """
        Execute the current checkpoint.

        Args:
            work: The creative work

        Returns:
            Tuple of (result, recommended mode)
        """
        if self.session is None:
            raise ValueError("No active session")

        # Get current resonance
        resonance = None
        if self.session.resonance_history:
            _, resonance = self.session.resonance_history[-1]

        result, mode = self.checkpoint_agent.execute_checkpoint(work, resonance)

        if result.passed:
            self.checkpoint_agent.pass_checkpoint(result.checkpoint, work)

        self._fire_event(
            CheckpointEvent(
                session_id=self.session.id,
                checkpoint_number=result.checkpoint.number,
                checkpoint_name=result.checkpoint.name,
                passed=result.passed,
            )
        )

        return result, mode

    def get_current_checkpoint(self) -> Checkpoint | None:
        """Get the current checkpoint."""
        return self.checkpoint_agent.get_current_checkpoint()

    def get_co_creative_mode(self) -> CoCreativeMode:
        """Get the co-creative mode for current checkpoint."""
        return self.checkpoint_agent.get_co_creative_mode()

    # -------------------------------------------------------------------------
    # Session State Queries
    # -------------------------------------------------------------------------

    def can_ship(self) -> tuple[bool, list[str]]:
        """
        Check if the work can be shipped.

        Returns:
            Tuple of (can_ship, blocking_reasons)
        """
        if self.session is None:
            return False, ["No active session"]

        blockers = []

        # Check minimum iterations
        if not self.session.minimum_iterations_met:
            blockers.append(
                f"Only {self.session.iteration}/{self.config.min_iterations} iterations completed"
            )

        # Check escape velocity
        if not self.session.escape_velocity_reached:
            blockers.append("Escape velocity not reached (need PROFOUND resonance)")

        # Check checkpoints
        checkpoint_can_ship, checkpoint_blockers = self.checkpoint_agent.can_ship()
        if not checkpoint_can_ship:
            blockers.extend(checkpoint_blockers)

        return len(blockers) == 0, blockers

    def get_session_state(self) -> SessionState[T] | None:
        """Get current session state."""
        return self.session

    def get_iteration_milestone(self) -> str:
        """Get current iteration milestone description."""
        if self.session is None:
            return ""
        return ITERATION_MILESTONES.get(self.session.iteration, "")

    def get_ghost_analysis(self) -> GhostAnalysis:
        """Get analysis of session ghosts."""
        return self.ghost_analyzer.analyze(self.session)

    def get_resurrection_candidates(self, limit: int = 5) -> list[ResurrectionCandidate]:
        """Get ghosts worth resurrecting."""
        return self.ghost_analyzer.find_worth_resurrecting(self.session, limit)

    # -------------------------------------------------------------------------
    # Crystallization and Witnessing
    # -------------------------------------------------------------------------

    def crystallize(self, final_work: T) -> None:
        """
        Lock in the final work.

        Args:
            final_work: The completed creative work
        """
        if self.session is None:
            raise ValueError("No active session")

        self.session.phase = SessionPhase.CRYSTALLIZE
        self.session.current = final_work

    def witness(self) -> dict[str, Any]:
        """
        Generate witness record for the session.

        Returns:
            Dictionary with session record
        """
        if self.session is None:
            raise ValueError("No active session")

        self.session.phase = SessionPhase.WITNESS

        # Evolve taste based on selections
        selection_records: list[tuple[CreativeOption[Any], str]] = []
        for iteration, option_id in self.session.selections:
            # Find the option in ghosts (the ones NOT selected would be ghosts)
            # This is a simplified representation
            selection_records.append(
                (CreativeOption(id=option_id), f"Selected at iteration {iteration}")
            )

        self.taste_agent.evolve(selection_records, self.session.id)

        # Build witness record
        return {
            "session_id": self.session.id,
            "domain": self.domain,
            "iterations": self.session.iteration,
            "ghosts_created": len(self.session.ghosts),
            "contradictions": len(self.session.contradictions),
            "defenses": len([d for d in self.session.defenses if d.defended]),
            "pivots": len([d for d in self.session.defenses if not d.defended]),
            "final_resonance": self.session.resonance_history[-1][1].name
            if self.session.resonance_history
            else None,
            "escape_velocity_reached": self.session.escape_velocity_reached,
            "timestamp": datetime.now().isoformat(),
        }

    # -------------------------------------------------------------------------
    # Event System
    # -------------------------------------------------------------------------

    def on(self, event_type: type, handler: Callable[..., Any]) -> None:
        """Register an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def _fire_event(
        self,
        event: Union[
            SessionEvent,
            IterationEvent,
            SelectionEvent,
            ContradictionEvent,
            BreakthroughEvent,
            CheckpointEvent,
        ],
    ) -> None:
        """Fire an event to all registered handlers."""
        event_type = type(event)
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                handler(event)


# =============================================================================
# Factory Functions
# =============================================================================


def create_orchestrator(
    domain: str,
    config: OrchestratorConfig | None = None,
    taste: TasteVector | None = None,
) -> MuseOrchestrator[Any]:
    """Create a new orchestrator for a domain."""
    return MuseOrchestrator(domain, config, taste)


def create_youtube_orchestrator(
    config: OrchestratorConfig | None = None,
) -> MuseOrchestrator[Any]:
    """Create an orchestrator for YouTube content."""
    return MuseOrchestrator("youtube", config)


def create_little_kant_orchestrator(
    config: OrchestratorConfig | None = None,
) -> MuseOrchestrator[Any]:
    """Create an orchestrator for Little Kant episodes."""
    return MuseOrchestrator("little_kant", config)


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Configuration
    "OrchestratorConfig",
    # Events
    "SessionEvent",
    "IterationEvent",
    "SelectionEvent",
    "ContradictionEvent",
    "BreakthroughEvent",
    "CheckpointEvent",
    # Orchestrator
    "MuseOrchestrator",
    # Factory functions
    "create_orchestrator",
    "create_youtube_orchestrator",
    "create_little_kant_orchestrator",
]
