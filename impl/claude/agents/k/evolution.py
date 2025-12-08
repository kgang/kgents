"""
K-gent Evolution: How the persona changes over time.

The persona is a garden, not a museum. It grows, changes seasons,
and occasionally needs pruning.

Sources of change:
1. Explicit updates (Kent directly states changes)
2. Observed patterns (K-gent notices regularities)
3. Contradiction resolution (behavior vs stated preferences)
4. Temporal decay (confidence degrades without reinforcement)
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime
import logging

from bootstrap.types import Agent
from .persona import PersonaState, PersonaSeed
from typing import Protocol


# Configure structured logging
logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for preferences."""
    HIGH = "high"        # 0.8-1.0: Recently confirmed, explicit
    MEDIUM = "medium"    # 0.5-0.8: Inferred or older
    LOW = "low"          # 0.2-0.5: Stale, needs confirmation
    UNCERTAIN = "uncertain"  # <0.2: Contradictory evidence


class ChangeSource(Enum):
    """Source of preference/pattern changes."""
    EXPLICIT = "explicit"    # Kent directly stated this
    INFERRED = "inferred"    # K-gent observed this pattern
    INHERITED = "inherited"  # From initial bootstrap
    DECAYED = "decayed"      # Lost confidence over time


@dataclass
class EvolutionInput:
    """Input for persona evolution."""
    # What triggered this evolution
    trigger: str  # "explicit", "observation", "contradiction", "review", "forget"

    # The content of the change
    aspect: str  # "preference", "pattern", "context"
    operation: str  # "add", "modify", "remove", "confirm", "archive"
    content: Any
    reason: Optional[str] = None

    # For contradiction resolution
    conflicting_evidence: Optional[list[str]] = None


@dataclass
class EvolutionOutput:
    """Output from persona evolution."""
    accepted: bool
    new_state: PersonaState
    change_summary: str

    # If not accepted, why?
    rejection_reason: Optional[str] = None

    # If change needs confirmation
    needs_confirmation: bool = False
    confirmation_prompt: Optional[str] = None


# Protocol for evolution handlers
class EvolutionHandler(Protocol):
    """
    Protocol for handlers that process specific evolution triggers.

    Enables decomposition of EvolutionAgent into composable morphisms.

    Example:
        explicit_handler = ExplicitUpdateHandler(state, trackers)
        observation_handler = ObservationHandler(state, trackers)

        # Compose via routing
        evolution = TriggerRouter({
            "explicit": explicit_handler,
            "observation": observation_handler,
        })
    """

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle evolution input and return output."""
        ...


@dataclass
class ConfidenceTracker:
    """Track confidence for a single preference/pattern."""
    value: float = 1.0
    last_confirmed: Optional[datetime] = None
    source: ChangeSource = ChangeSource.INHERITED
    evidence_count: int = 0

    def reinforce(self) -> None:
        """Increase confidence from new evidence."""
        old_value = self.value
        old_level = self.level

        self.evidence_count += 1
        self.value = min(1.0, self.value + 0.1)
        self.last_confirmed = datetime.now()

        logger.info(
            "Confidence reinforced",
            extra={
                "event": "confidence_reinforced",
                "old_value": old_value,
                "new_value": self.value,
                "old_level": old_level.value,
                "new_level": self.level.value,
                "evidence_count": self.evidence_count,
                "source": self.source.value,
            }
        )

    def decay(self, months: float) -> None:
        """Decrease confidence over time."""
        old_value = self.value
        old_level = self.level

        decay_rate = 0.1  # per month
        self.value = max(0.1, self.value - (decay_rate * months))

        logger.warning(
            "Confidence decayed",
            extra={
                "event": "confidence_decayed",
                "old_value": old_value,
                "new_value": self.value,
                "old_level": old_level.value,
                "new_level": self.level.value,
                "months_elapsed": months,
                "decay_rate": decay_rate,
            }
        )

    def contradict(self) -> None:
        """Decrease confidence from contradictory evidence."""
        old_value = self.value
        old_level = self.level
        old_source = self.source

        self.value = max(0.2, self.value - 0.2)
        self.source = ChangeSource.DECAYED

        logger.warning(
            "Confidence contradicted",
            extra={
                "event": "confidence_contradicted",
                "old_value": old_value,
                "new_value": self.value,
                "old_level": old_level.value,
                "new_level": self.level.value,
                "old_source": old_source.value,
                "new_source": self.source.value,
            }
        )

    @property
    def level(self) -> ConfidenceLevel:
        if self.value >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.value >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif self.value >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN


# Concrete handler implementations

class ExplicitUpdateHandler:
    """
    Handler for explicit user updates.

    Immediate acceptance with high confidence.
    Implements EvolutionHandler protocol.
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle explicit user updates - immediate, high confidence."""
        logger.info(
            "Handling explicit update",
            extra={
                "event": "explicit_update",
                "aspect": input.aspect,
                "operation": input.operation,
            }
        )

        new_state = self._apply_change(input)

        # Track with high confidence
        key = f"{input.aspect}.{input.content}"
        self._trackers[key] = ConfidenceTracker(
            value=1.0,
            last_confirmed=datetime.now(),
            source=ChangeSource.EXPLICIT,
            evidence_count=1,
        )

        return EvolutionOutput(
            accepted=True,
            new_state=new_state,
            change_summary=f"Explicit {input.operation}: {input.content}",
        )

    def _apply_change(self, input: EvolutionInput) -> PersonaState:
        """Apply a change to the persona state."""
        logger.debug(
            "Applying change to persona state",
            extra={
                "event": "apply_change",
                "aspect": input.aspect,
                "operation": input.operation,
            }
        )

        # Create a copy of the state
        new_seed = PersonaSeed(
            name=self._state.seed.name,
            roles=list(self._state.seed.roles),
            preferences=dict(self._state.seed.preferences),
            patterns=dict(self._state.seed.patterns),
        )

        new_state = PersonaState(
            seed=new_seed,
            current_focus=self._state.current_focus,
            recent_interests=list(self._state.recent_interests),
            active_projects=list(self._state.active_projects),
            confidence=dict(self._state.confidence),
            sources=dict(self._state.sources),
        )

        # Apply the change
        if input.aspect == "preference":
            if input.operation == "add":
                values = new_state.seed.preferences.get("values", [])
                if isinstance(values, list):
                    values.append(input.content)
                    logger.debug("Added preference value", extra={"value": input.content})
            elif input.operation == "remove":
                values = new_state.seed.preferences.get("values", [])
                if isinstance(values, list) and input.content in values:
                    values.remove(input.content)
                    logger.debug("Removed preference value", extra={"value": input.content})

        elif input.aspect == "pattern":
            if input.operation == "add":
                # Add to thinking patterns by default
                patterns = new_state.seed.patterns.get("thinking", [])
                patterns.append(input.content)
                logger.debug("Added thinking pattern", extra={"pattern": input.content})

        elif input.aspect == "context":
            if input.operation == "modify":
                if isinstance(input.content, dict):
                    if "current_focus" in input.content:
                        new_state.current_focus = input.content["current_focus"]
                        logger.debug("Modified current_focus", extra={"focus": input.content["current_focus"]})
                    if "recent_interests" in input.content:
                        new_state.recent_interests = input.content["recent_interests"]
                        logger.debug("Modified recent_interests", extra={"count": len(input.content["recent_interests"])})

        self._state = new_state
        return new_state


class ObservationHandler:
    """
    Handler for observed patterns.

    Proposes changes with medium confidence after repeated evidence.
    Implements EvolutionHandler protocol.
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle inferred changes - propose, medium confidence."""
        key = f"{input.aspect}.{input.content}"

        # Check if we've seen this pattern before
        if key in self._trackers:
            tracker = self._trackers[key]
            tracker.reinforce()

            if tracker.evidence_count >= 3 and tracker.level == ConfidenceLevel.HIGH:
                # Enough evidence to add without confirmation
                logger.info(
                    "Pattern confirmed through observation",
                    extra={
                        "event": "pattern_confirmed",
                        "key": key,
                        "evidence_count": tracker.evidence_count,
                        "confidence": tracker.value,
                    }
                )

                new_state = self._apply_change(input)
                return EvolutionOutput(
                    accepted=True,
                    new_state=new_state,
                    change_summary=f"Inferred pattern confirmed: {input.content}",
                )

        # Not enough evidence - propose change
        if key not in self._trackers:
            logger.info(
                "New pattern observed",
                extra={
                    "event": "pattern_observed",
                    "key": key,
                    "initial_confidence": 0.4,
                }
            )

            self._trackers[key] = ConfidenceTracker(
                value=0.4,
                last_confirmed=datetime.now(),
                source=ChangeSource.INFERRED,
                evidence_count=1,
            )

        return EvolutionOutput(
            accepted=False,
            new_state=self._state,
            change_summary=f"Observing pattern: {input.content}",
            needs_confirmation=True,
            confirmation_prompt=(
                f"I've noticed you often {input.content}. "
                f"Should I add this as a pattern, or is this situational?"
            ),
        )

    def _apply_change(self, input: EvolutionInput) -> PersonaState:
        """Apply a change to the persona state (same as ExplicitUpdateHandler)."""
        # Create a copy of the state
        new_seed = PersonaSeed(
            name=self._state.seed.name,
            roles=list(self._state.seed.roles),
            preferences=dict(self._state.seed.preferences),
            patterns=dict(self._state.seed.patterns),
        )

        new_state = PersonaState(
            seed=new_seed,
            current_focus=self._state.current_focus,
            recent_interests=list(self._state.recent_interests),
            active_projects=list(self._state.active_projects),
            confidence=dict(self._state.confidence),
            sources=dict(self._state.sources),
        )

        # Apply the change
        if input.aspect == "pattern":
            if input.operation == "add":
                patterns = new_state.seed.patterns.get("thinking", [])
                patterns.append(input.content)

        self._state = new_state
        return new_state


class ContradictionHandler:
    """
    Handler for contradictions between behavior and stated preferences.

    Asks for user clarification with resolution options:
    - Ask: Request clarification on when each preference applies
    - Contextualize: Both valid but context-specific
    - Supersede: More recent evidence takes precedence
    Implements EvolutionHandler protocol.
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers
        self._detector = ConflictDetector(trackers)

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle contradictions between behavior and stated preferences."""
        logger.warning(
            "Contradiction detected",
            extra={
                "event": "contradiction_detected",
                "aspect": input.aspect,
                "content": str(input.content),
                "conflicting_evidence": input.conflicting_evidence,
            }
        )

        # Check for automatically detected conflicts
        conflicts = self._detector.detect_conflicts()

        if conflicts:
            # Format multiple conflicts for presentation
            conflict_details = "\n".join(
                f"  - {c.preference_a} vs {c.preference_b}"
                for c in conflicts[:3]  # Show first 3
            )

            prompt = (
                f"Your recent behavior seems to contradict stated preferences:\n"
                f"{conflict_details}\n\n"
                f"Resolution options:\n"
                f"1. Clarify when each applies (context-specific)\n"
                f"2. Update to current preference (supersede old)\n"
                f"3. Keep both as valid alternatives\n\n"
                f"How should I resolve this?"
            )
        else:
            # Single contradiction from input
            prompt = (
                f"Your recent behavior seems to contradict a stated preference. "
                f"{input.content}\n"
                f"Has your preference shifted, or is this context-specific?"
            )

        return EvolutionOutput(
            accepted=False,
            new_state=self._state,
            change_summary=f"Contradiction detected: {input.content}",
            needs_confirmation=True,
            confirmation_prompt=prompt,
        )


class ForgetHandler:
    """
    Handler for intentional and natural forgetting.

    Supports:
    - Intentional forgetting (user requests removal)
    - Natural decay (automatic archiving of stale data)
    Implements EvolutionHandler protocol.
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle forgetting - intentional removal or archival."""
        logger.info(
            "Handling forget request",
            extra={
                "event": "forget_request",
                "aspect": input.aspect,
                "content": str(input.content),
                "reason": input.reason,
            }
        )

        key = f"{input.aspect}.{input.content}"

        # Remove from trackers
        if key in self._trackers:
            del self._trackers[key]
            logger.info(
                "Removed from confidence tracking",
                extra={"event": "tracker_removed", "key": key}
            )

        # Remove from state
        new_state = self._remove_from_state(input)

        return EvolutionOutput(
            accepted=True,
            new_state=new_state,
            change_summary=f"Forgot: {input.content}",
        )

    def _remove_from_state(self, input: EvolutionInput) -> PersonaState:
        """Remove item from persona state."""
        # Create a copy of the state
        new_seed = PersonaSeed(
            name=self._state.seed.name,
            roles=list(self._state.seed.roles),
            preferences=dict(self._state.seed.preferences),
            patterns=dict(self._state.seed.patterns),
        )

        new_state = PersonaState(
            seed=new_seed,
            current_focus=self._state.current_focus,
            recent_interests=list(self._state.recent_interests),
            active_projects=list(self._state.active_projects),
            confidence=dict(self._state.confidence),
            sources=dict(self._state.sources),
        )

        # Remove the content
        if input.aspect == "preference":
            values = new_state.seed.preferences.get("values", [])
            if isinstance(values, list) and input.content in values:
                values.remove(input.content)
                logger.debug("Removed preference value", extra={"value": input.content})

        elif input.aspect == "pattern":
            # Remove from all pattern categories
            for category, patterns in new_state.seed.patterns.items():
                if input.content in patterns:
                    patterns.remove(input.content)
                    logger.debug(
                        "Removed pattern",
                        extra={"category": category, "pattern": input.content}
                    )

        elif input.aspect == "context":
            if "recent_interests" in str(input.content):
                interest = str(input.content).replace("recent_interests.", "")
                if interest in new_state.recent_interests:
                    new_state.recent_interests.remove(interest)

        self._state = new_state
        return new_state


@dataclass
class ConflictData:
    """Data about conflicting preferences."""
    preference_a: str
    preference_b: str
    evidence_a: list[str]
    evidence_b: list[str]
    suggested_resolution: str


class ConflictDetector:
    """
    Detects conflicts between preferences and patterns.

    Analyzes evidence for contradictory preferences and suggests resolutions.
    Not a full handler - used by ContradictionHandler for analysis.
    """

    def __init__(self, trackers: dict[str, ConfidenceTracker]):
        self._trackers = trackers

    def detect_conflicts(self) -> list[ConflictData]:
        """
        Detect conflicting preferences based on evidence.

        Returns list of conflicts found.
        """
        conflicts = []

        # Group trackers by aspect (simplified conflict detection)
        aspect_groups: dict[str, list[tuple[str, ConfidenceTracker]]] = {}

        for key, tracker in self._trackers.items():
            if "." in key:
                aspect = key.split(".")[0]
                if aspect not in aspect_groups:
                    aspect_groups[aspect] = []
                aspect_groups[aspect].append((key, tracker))

        # Look for contradictory evidence within each aspect
        for aspect, items in aspect_groups.items():
            # Simple heuristic: if multiple items in same aspect have contradicting sources
            for i, (key_a, tracker_a) in enumerate(items):
                for key_b, tracker_b in items[i + 1:]:
                    # Check if both have high evidence but different sources
                    if (
                        tracker_a.evidence_count >= 3
                        and tracker_b.evidence_count >= 3
                        and tracker_a.source != tracker_b.source
                    ):
                        # Potential conflict
                        conflicts.append(
                            ConflictData(
                                preference_a=key_a,
                                preference_b=key_b,
                                evidence_a=[f"count:{tracker_a.evidence_count}"],
                                evidence_b=[f"count:{tracker_b.evidence_count}"],
                                suggested_resolution=(
                                    f"Ask: Help me understand when you prefer "
                                    f"{key_a.split('.')[-1]} vs {key_b.split('.')[-1]}"
                                ),
                            )
                        )

        return conflicts


class ReviewHandler:
    """
    Handler for periodic reviews of stale preferences.

    Identifies low-confidence items needing reconfirmation.
    Implements EvolutionHandler protocol.
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers

    async def handle(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle periodic reviews of stale preferences."""
        stale_items = []
        very_stale_items = []  # For automatic archival

        now = datetime.now()

        for key, tracker in self._trackers.items():
            # Check for very old items (>1 year without confirmation)
            if tracker.last_confirmed:
                months_old = (now - tracker.last_confirmed).days / 30.0

                # Natural decay: archive very old, low-confidence items
                if months_old > 12 and tracker.value < 0.3:
                    very_stale_items.append(key)
                # Seasonal review: flag items >6 months old
                elif months_old > 6 and tracker.level in (ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN):
                    stale_items.append(key)
            elif tracker.level in (ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN):
                stale_items.append(key)

        # Automatically archive very stale items
        if very_stale_items:
            logger.info(
                "Archiving very stale items",
                extra={
                    "event": "auto_archive",
                    "count": len(very_stale_items),
                    "items": very_stale_items,
                }
            )
            for key in very_stale_items:
                del self._trackers[key]

        if stale_items:
            logger.info(
                "Review identified stale items",
                extra={
                    "event": "stale_items_found",
                    "count": len(stale_items),
                    "items": stale_items[:5],  # Log first 5
                }
            )

            return EvolutionOutput(
                accepted=False,
                new_state=self._state,
                change_summary=f"Review needed for {len(stale_items)} items",
                needs_confirmation=True,
                confirmation_prompt=(
                    f"It's been a while since we talked about some preferences:\n"
                    f"{', '.join(stale_items[:3])}\n"
                    f"Are these still relevant to who you are?"
                ),
            )

        logger.info(
            "Review completed - all current",
            extra={
                "event": "review_completed",
                "stale_count": 0,
                "archived_count": len(very_stale_items),
            }
        )

        return EvolutionOutput(
            accepted=True,
            new_state=self._state,
            change_summary=f"All preferences current - archived {len(very_stale_items)} very old items",
        )


class TriggerRouter(Agent[EvolutionInput, EvolutionOutput]):
    """
    Routes evolution inputs to appropriate handlers based on trigger type.

    Implements composable routing pattern from IMPLEMENTATION_PLAN.md Issue #5.
    Uses switch-like composition to delegate to specialized handlers.

    Example:
        router = TriggerRouter(state, trackers)
        result = await router.invoke(EvolutionInput(
            trigger="explicit",
            aspect="preference",
            operation="add",
            content="Direct communication"
        ))
    """

    def __init__(self, state: PersonaState, trackers: dict[str, ConfidenceTracker]):
        self._state = state
        self._trackers = trackers

        # Create handlers
        self._handlers: dict[str, EvolutionHandler] = {
            "explicit": ExplicitUpdateHandler(state, trackers),
            "observation": ObservationHandler(state, trackers),
            "contradiction": ContradictionHandler(state, trackers),
            "review": ReviewHandler(state, trackers),
            "forget": ForgetHandler(state, trackers),
        }

    @property
    def name(self) -> str:
        return "TriggerRouter"

    async def invoke(self, input: EvolutionInput) -> EvolutionOutput:
        """Route input to appropriate handler based on trigger."""
        logger.info(
            "Routing evolution input",
            extra={
                "event": "routing_evolution",
                "trigger": input.trigger,
                "aspect": input.aspect,
                "operation": input.operation,
            }
        )

        # Get handler for trigger
        handler = self._handlers.get(input.trigger)

        if handler is None:
            logger.error(
                "Unknown evolution trigger",
                extra={
                    "event": "unknown_trigger",
                    "trigger": input.trigger,
                }
            )
            return EvolutionOutput(
                accepted=False,
                new_state=self._state,
                change_summary="Unknown trigger type",
                rejection_reason=f"Unknown trigger: {input.trigger}",
            )

        # Delegate to handler
        result = await handler.handle(input)

        logger.info(
            "Evolution routing completed",
            extra={
                "event": "routing_completed",
                "trigger": input.trigger,
                "accepted": result.accepted,
                "needs_confirmation": result.needs_confirmation,
            }
        )

        return result


class EvolutionAgent(Agent[EvolutionInput, EvolutionOutput]):
    """
    Evolve K-gent's persona over time.

    REFACTORED (Issue #5): Now uses composable TriggerRouter pattern
    instead of internal orchestration.

    Delegates to specialized handlers via TriggerRouter:
    - ExplicitUpdateHandler (immediate, high confidence)
    - ObservationHandler (proposed, medium confidence)
    - ContradictionHandler (ask for clarification)
    - ReviewHandler (archive stale data)
    """

    def __init__(self, state: PersonaState):
        self._state = state
        self._trackers: dict[str, ConfidenceTracker] = {}

        # Composition: delegate to TriggerRouter
        self._router = TriggerRouter(state, self._trackers)

        logger.info(
            "EvolutionAgent initialized",
            extra={
                "event": "agent_initialized",
                "agent_name": self.name,
                "persona_name": state.seed.name,
            }
        )

    @property
    def name(self) -> str:
        return "Evolution"

    async def invoke(self, input: EvolutionInput) -> EvolutionOutput:
        """
        Evolve the persona based on input.

        Delegates to TriggerRouter for composable handling.
        Returns new state and summary of changes.
        """
        logger.info(
            "Evolution invoked",
            extra={
                "event": "evolution_invoked",
                "trigger": input.trigger,
                "aspect": input.aspect,
                "operation": input.operation,
                "reason": input.reason,
            }
        )

        # Delegate to router (composition, not orchestration)
        result = await self._router.invoke(input)

        logger.info(
            "Evolution completed",
            extra={
                "event": "evolution_completed",
                "accepted": result.accepted,
                "needs_confirmation": result.needs_confirmation,
                "change_summary": result.change_summary,
            }
        )

        return result


# Bootstrap functionality

class BootstrapMode(Enum):
    """Bootstrap modes for initial persona population."""
    CLEAN_SLATE = "clean_slate"      # Start empty, build through interaction
    INTERVIEW = "interview"           # Structured onboarding conversation
    DOCUMENT_IMPORT = "document"      # Import from existing writings
    HYBRID = "hybrid"                 # Recommended: interview + observation


@dataclass
class BootstrapConfig:
    """Configuration for persona bootstrapping."""
    mode: BootstrapMode = BootstrapMode.HYBRID

    # For INTERVIEW mode
    core_questions: list[str] = field(default_factory=lambda: [
        "What are your core values?",
        "What's your current focus?",
        "What matters most to you in how others communicate with you?",
    ])

    # For DOCUMENT_IMPORT mode
    import_sources: list[str] = field(default_factory=list)

    # For HYBRID mode
    skip_patterns: bool = True  # Patterns must be observed, not imported


async def bootstrap_persona(
    config: BootstrapConfig,
    existing_state: Optional[PersonaState] = None
) -> PersonaState:
    """
    Bootstrap a persona state based on configuration.

    Implements the bootstrap problem solutions from spec:
    - CLEAN_SLATE: Start with minimal seed
    - INTERVIEW: Guided questions (requires interaction - returns prompts)
    - DOCUMENT_IMPORT: Parse from existing data
    - HYBRID: Light interview + clean patterns + optional docs

    Args:
        config: Bootstrap configuration
        existing_state: Optional existing state to enhance

    Returns:
        Initialized PersonaState ready for evolution
    """
    logger.info(
        "Bootstrapping persona",
        extra={
            "event": "bootstrap_start",
            "mode": config.mode.value,
        }
    )

    if config.mode == BootstrapMode.CLEAN_SLATE:
        # Minimal seed - everything learned through interaction
        seed = PersonaSeed(
            name="Kent",
            roles=[],
            preferences={},
            patterns={},
        )

        state = PersonaState(
            seed=seed,
            current_focus="",
            recent_interests=[],
            active_projects=[],
        )

        logger.info("Created clean slate persona", extra={"event": "bootstrap_clean"})
        return state

    elif config.mode == BootstrapMode.INTERVIEW:
        # Start with existing or minimal state
        state = existing_state or PersonaState(seed=PersonaSeed())

        # Interview mode requires interaction - log questions for caller
        logger.info(
            "Interview mode - questions ready",
            extra={
                "event": "bootstrap_interview",
                "questions": config.core_questions,
            }
        )

        # Return state with metadata about needed questions
        # Caller should present questions and update via explicit triggers
        return state

    elif config.mode == BootstrapMode.DOCUMENT_IMPORT:
        # Import from documents (simplified - would need actual parser)
        state = existing_state or PersonaState(seed=PersonaSeed())

        logger.info(
            "Document import mode",
            extra={
                "event": "bootstrap_import",
                "source_count": len(config.import_sources),
            }
        )

        # TODO: Actual document parsing would go here
        # For now, use existing state or default
        return state

    elif config.mode == BootstrapMode.HYBRID:
        # Recommended: Light interview + clean patterns + optional docs
        state = existing_state or PersonaState(seed=PersonaSeed())

        if config.skip_patterns:
            # Clear patterns - must be observed
            state.seed.patterns = {}
            logger.info(
                "Hybrid mode - cleared patterns for observation",
                extra={"event": "bootstrap_hybrid"}
            )

        # Keep core preferences from seed/import
        # Interview questions ready for caller
        logger.info(
            "Hybrid bootstrap ready",
            extra={
                "event": "bootstrap_hybrid_ready",
                "questions": config.core_questions[:2],  # Fewer questions in hybrid
            }
        )

        return state

    # Fallback
    return existing_state or PersonaState(seed=PersonaSeed())


# Convenience functions

def evolve_persona(state: PersonaState) -> EvolutionAgent:
    """Create an evolution agent for the given persona state."""
    return EvolutionAgent(state)


async def bootstrap_clean_slate() -> PersonaState:
    """Quick bootstrap with clean slate mode."""
    return await bootstrap_persona(BootstrapConfig(mode=BootstrapMode.CLEAN_SLATE))


async def bootstrap_hybrid(existing_state: Optional[PersonaState] = None) -> PersonaState:
    """Quick bootstrap with recommended hybrid mode."""
    return await bootstrap_persona(
        BootstrapConfig(mode=BootstrapMode.HYBRID),
        existing_state=existing_state
    )
