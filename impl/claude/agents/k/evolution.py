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
    trigger: str  # "explicit", "observation", "contradiction", "review"

    # The content of the change
    aspect: str  # "preference", "pattern", "context"
    operation: str  # "add", "modify", "remove", "confirm"
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


class EvolutionAgent(Agent[EvolutionInput, EvolutionOutput]):
    """
    Evolve K-gent's persona over time.

    Handles:
    - Explicit updates (immediate, high confidence)
    - Inferred changes (proposed, medium confidence)
    - Contradiction resolution (ask for clarification)
    - Temporal decay (archive stale data)
    """

    def __init__(self, state: PersonaState):
        self._state = state
        self._trackers: dict[str, ConfidenceTracker] = {}
        
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
        
        if input.trigger == "explicit":
            result = await self._handle_explicit(input)
        elif input.trigger == "observation":
            result = await self._handle_observation(input)
        elif input.trigger == "contradiction":
            result = await self._handle_contradiction(input)
        elif input.trigger == "review":
            result = await self._handle_review(input)
        else:
            logger.error(
                "Unknown evolution trigger",
                extra={
                    "event": "unknown_trigger",
                    "trigger": input.trigger,
                }
            )
            result = EvolutionOutput(
                accepted=False,
                new_state=self._state,
                change_summary="Unknown trigger type",
                rejection_reason=f"Unknown trigger: {input.trigger}",
            )
        
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

    async def _handle_explicit(self, input: EvolutionInput) -> EvolutionOutput:
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

    async def _handle_observation(self, input: EvolutionInput) -> EvolutionOutput:
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

    async def _handle_contradiction(self, input: EvolutionInput) -> EvolutionOutput:
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
        
        return EvolutionOutput(
            accepted=False,
            new_state=self._state,
            change_summary=f"Contradiction detected: {input.content}",
            needs_confirmation=True,
            confirmation_prompt=(
                f"Your recent behavior seems to contradict a stated preference. "
                f"{input.content}\n"
                f"Has your preference shifted, or is this context-specific?"
            ),
        )

    async def _handle_review(self, input: EvolutionInput) -> EvolutionOutput:
        """Handle periodic reviews of stale preferences."""
        stale_items = []

        for key, tracker in self._trackers.items():
            if tracker.level in (ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN):
                stale_items.append(key)

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
                    f"Some preferences haven't been confirmed in a while:\n"
                    f"{', '.join(stale_items[:3])}\n"
                    f"Are these still accurate?"
                ),
            )

        logger.info(
            "Review completed - all current",
            extra={
                "event": "review_completed",
                "stale_count": 0,
            }
        )
        
        return EvolutionOutput(
            accepted=True,
            new_state=self._state,
            change_summary="All preferences current - no review needed",
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


# Convenience function

def evolve_persona(state: PersonaState) -> EvolutionAgent:
    """Create an evolution agent for the given persona state."""
    return EvolutionAgent(state)
