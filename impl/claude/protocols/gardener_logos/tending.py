"""
Tending Calculus: The gesture-based operations of Gardener-Logos.

Traditional programming: f(x) = y — function transforms input to output
Tending calculus: tend(garden, gesture) ~ garden' — gesture tends garden toward new state

The tending relation is *approximate*, not exact. Gardens respond to gestures
but have their own momentum. The gardener proposes; the garden disposes.

See: spec/protocols/gardener-logos.md Part I
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .garden import GardenState
    from .persistence import GardenStore
    from .seasons import SeasonTransition


class TendingVerb(Enum):
    """
    The six primitive gestures of tending.

    These are the verbs of the tending calculus—the fundamental
    operations a gardener can perform on a garden.

    Unlike CRUD operations, tending verbs have *meaning*:
    - They suggest relationship rather than manipulation
    - They imply patience rather than immediacy
    - They acknowledge the garden's own momentum
    """

    OBSERVE = auto()  # Perceive without changing
    PRUNE = auto()  # Remove what no longer serves
    GRAFT = auto()  # Add something new
    WATER = auto()  # Nurture what exists (TextGRAD)
    ROTATE = auto()  # Change perspective
    WAIT = auto()  # Allow time to pass

    @property
    def emoji(self) -> str:
        """Verb emoji for display."""
        return {
            TendingVerb.OBSERVE: "👁️",
            TendingVerb.PRUNE: "✂️",
            TendingVerb.GRAFT: "🌿",
            TendingVerb.WATER: "💧",
            TendingVerb.ROTATE: "🔄",
            TendingVerb.WAIT: "⏳",
        }[self]

    @property
    def base_entropy_cost(self) -> float:
        """Base entropy cost for this verb type."""
        return {
            TendingVerb.OBSERVE: 0.01,  # Nearly free
            TendingVerb.PRUNE: 0.15,  # Moderate - removing is careful work
            TendingVerb.GRAFT: 0.20,  # Expensive - adding is creative
            TendingVerb.WATER: 0.10,  # Moderate - nurturing takes energy
            TendingVerb.ROTATE: 0.05,  # Cheap - perspective shift
            TendingVerb.WAIT: 0.00,  # Free - time costs nothing
        }[self]

    @property
    def affects_state(self) -> bool:
        """Whether this verb typically changes garden state."""
        return self in {
            TendingVerb.PRUNE,
            TendingVerb.GRAFT,
            TendingVerb.WATER,
            TendingVerb.ROTATE,
        }


@dataclass(frozen=True)
class TendingGesture:
    """
    A gesture in the tending calculus.

    Gestures are immutable records of tending operations.
    They capture not just WHAT was done, but WHY and HOW:

    - verb: The type of operation
    - target: What was tended (AGENTESE path)
    - tone: How definitive (0.0=tentative, 1.0=definitive)
    - reasoning: Why this gesture?
    - entropy_cost: Cost from the Accursed Share

    Gestures accumulate in the garden's momentum, providing
    a trace of how the garden has been tended over time.
    """

    verb: TendingVerb
    target: str  # AGENTESE path
    tone: float  # 0.0 = tentative, 1.0 = definitive
    reasoning: str
    entropy_cost: float
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional context
    observer: str = "default"  # Umwelt archetype
    session_id: str | None = None
    result_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "verb": self.verb.name,
            "target": self.target,
            "tone": self.tone,
            "reasoning": self.reasoning,
            "entropy_cost": self.entropy_cost,
            "timestamp": self.timestamp.isoformat(),
            "observer": self.observer,
            "session_id": self.session_id,
            "result_summary": self.result_summary,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TendingGesture":
        """Deserialize from persistence."""
        return cls(
            verb=TendingVerb[data["verb"]],
            target=data["target"],
            tone=data.get("tone", 0.5),
            reasoning=data.get("reasoning", ""),
            entropy_cost=data.get("entropy_cost", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else datetime.now(),
            observer=data.get("observer", "default"),
            session_id=data.get("session_id"),
            result_summary=data.get("result_summary", ""),
        )

    def is_recent(self, hours: int = 24) -> bool:
        """Check if gesture is recent (within hours)."""
        return datetime.now() - self.timestamp < timedelta(hours=hours)

    def display(self) -> str:
        """Human-readable display string."""
        time_str = self.timestamp.strftime("%H:%M")
        return f"{time_str} {self.verb.emoji} {self.verb.name.lower()} {self.target}"


@dataclass
class TendingResult:
    """
    Result of applying a tending gesture.

    Captures:
    - Whether the gesture was accepted by the garden
    - What changed (if anything)
    - The new garden state
    - Any side effects (synergies triggered, etc.)
    - Suggested season transition (Phase 8: Auto-Inducer)
    """

    gesture: TendingGesture
    accepted: bool
    state_changed: bool
    changes: list[str]  # What changed
    synergies_triggered: list[str]  # Cross-jewel effects
    reasoning_trace: tuple[str, ...]
    error: str | None = None

    # Phase 8: Auto-Inducer - suggested season transition
    suggested_transition: "SeasonTransition | None" = None

    @property
    def success(self) -> bool:
        """Whether the gesture succeeded."""
        return self.accepted and self.error is None


async def apply_gesture(
    garden: "GardenState",
    gesture: TendingGesture,
    *,
    store: "GardenStore | None" = None,
    auto_save: bool = True,
    emit_event: bool = True,
    evaluate_transition: bool = True,
) -> TendingResult:
    """
    Apply a tending gesture to the garden.

    This is the core operation of the tending calculus.
    It routes the gesture to the appropriate handler based on verb.

    Args:
        garden: The garden to tend
        gesture: The gesture to apply
        store: Optional GardenStore for persistence
        auto_save: Whether to auto-save after successful gesture (requires store)
        emit_event: Whether to emit synergy events for significant gestures
        evaluate_transition: Whether to evaluate for season transition (Phase 8)

    Returns:
        TendingResult with outcome (including suggested_transition if any)
    """
    handlers = {
        TendingVerb.OBSERVE: _handle_observe,
        TendingVerb.PRUNE: _handle_prune,
        TendingVerb.GRAFT: _handle_graft,
        TendingVerb.WATER: _handle_water,
        TendingVerb.ROTATE: _handle_rotate,
        TendingVerb.WAIT: _handle_wait,
    }

    handler = handlers.get(gesture.verb)
    if handler is None:
        return TendingResult(
            gesture=gesture,
            accepted=False,
            state_changed=False,
            changes=[],
            synergies_triggered=[],
            reasoning_trace=("Unknown verb",),
            error=f"Unknown tending verb: {gesture.verb}",
        )

    try:
        result = await handler(garden, gesture)

        # Record gesture in garden momentum
        recorded_gesture = TendingGesture(
            verb=gesture.verb,
            target=gesture.target,
            tone=gesture.tone,
            reasoning=gesture.reasoning,
            entropy_cost=gesture.entropy_cost,
            observer=gesture.observer,
            session_id=gesture.session_id,
            result_summary="success" if result.success else "failed",
        )
        garden.add_gesture(recorded_gesture)

        # Auto-save if store provided and gesture succeeded
        if store is not None and auto_save and result.accepted:
            await store.save_gesture(garden.garden_id, recorded_gesture)
            await store.save(garden)

        # Emit synergy event for significant gestures (Phase 6)
        # Only emit for state-changing gestures (not OBSERVE or WAIT)
        if emit_event and result.accepted and gesture.verb.affects_state:
            await _emit_gesture_applied_event(garden, gesture, result)

        # Phase 8: Auto-Inducer - evaluate for season transition
        if evaluate_transition and result.accepted:
            result = _evaluate_and_add_transition_suggestion(garden, result)

        return result

    except Exception as e:
        return TendingResult(
            gesture=gesture,
            accepted=False,
            state_changed=False,
            changes=[],
            synergies_triggered=[],
            reasoning_trace=(f"Error: {e}",),
            error=str(e),
        )


def _evaluate_and_add_transition_suggestion(
    garden: "GardenState",
    result: TendingResult,
) -> TendingResult:
    """
    Evaluate garden state for season transition suggestion.

    Phase 8: Auto-Inducer
    Called after successful gesture application to check if the garden
    should transition to a new season based on activity patterns.

    Args:
        garden: The garden that was just tended
        result: The tending result to augment

    Returns:
        TendingResult with suggested_transition if applicable
    """
    try:
        from .seasons import suggest_season_transition

        suggestion = suggest_season_transition(garden)

        if suggestion is not None:
            # Create a new result with the suggestion
            return TendingResult(
                gesture=result.gesture,
                accepted=result.accepted,
                state_changed=result.state_changed,
                changes=result.changes,
                synergies_triggered=result.synergies_triggered,
                reasoning_trace=result.reasoning_trace,
                error=result.error,
                suggested_transition=suggestion,
            )

    except ImportError:
        # seasons module not available - skip silently
        pass
    except Exception as e:
        # Log but don't fail the gesture
        import logging
        logger = logging.getLogger("kgents.gardener.auto_inducer")
        logger.warning(f"Failed to evaluate season transition: {e}")

    return result


# =============================================================================
# Verb Handlers
# =============================================================================


async def _handle_observe(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle OBSERVE gesture: perceive without changing.

    Observation is nearly free (low entropy cost) and never
    changes state. It gathers information about the target.
    """
    # Parse target path
    target = gesture.target
    observations: list[str] = []

    if target.startswith("concept.gardener"):
        # Observing the garden itself
        observations.append(f"Garden: {garden.name}")
        observations.append(f"Season: {garden.season.name} ({garden.season.emoji})")
        observations.append(f"Plots: {len(garden.plots)}")
        observations.append(f"Health: {garden.metrics.health_score:.0%}")

    elif target.startswith("concept.prompt"):
        # Observing prompts (would delegate to Prompt Logos)
        observations.append(f"Prompt count: {garden.prompt_count}")
        observations.append(f"Types: {garden.prompt_types}")

    else:
        # Generic observation
        observations.append(f"Observed: {target}")

    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=False,
        changes=[],
        synergies_triggered=[],
        reasoning_trace=tuple(observations),
    )


async def _handle_prune(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle PRUNE gesture: remove what no longer serves.

    Pruning marks things for deprecation or removal.
    It requires appropriate season (HARVEST or COMPOSTING best).
    """
    # Check season appropriateness
    good_seasons = {
        garden.season.HARVEST,
        garden.season.COMPOSTING,
    }
    season_warning = None
    if garden.season not in good_seasons:
        season_warning = f"Pruning in {garden.season.name} season may be premature"

    changes: list[str] = []
    target = gesture.target

    # For now, record intent (actual pruning would delegate)
    changes.append(f"Marked for pruning: {target}")

    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=True,
        changes=changes,
        synergies_triggered=[],
        reasoning_trace=(
            season_warning or "Pruning accepted",
            f"Target: {target}",
        ),
    )


async def _handle_graft(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle GRAFT gesture: add something new.

    Grafting adds new prompts, plots, or patterns.
    Best in SPROUTING season.
    """
    # Check season appropriateness
    if garden.season == garden.season.SPROUTING:
        season_bonus = "Perfect season for new growth!"
    elif garden.season.plasticity > 0.5:
        season_bonus = "Season is receptive to new additions"
    else:
        season_bonus = f"Low plasticity in {garden.season.name} - graft may not take"

    changes: list[str] = []
    target = gesture.target

    # Record graft intent
    changes.append(f"Grafted: {target}")

    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=True,
        changes=changes,
        synergies_triggered=[],
        reasoning_trace=(
            season_bonus,
            f"Target: {target}",
            f"Reasoning: {gesture.reasoning}",
        ),
    )


async def _handle_water(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle WATER gesture: nurture what exists via TextGRAD.

    Watering applies textual gradients to improve prompts.
    The tone determines base learning rate, adjusted by season plasticity.

    Phase 5: Season-aware TextGRAD
    - learning_rate = tone × season.plasticity
    - SPROUTING (0.9) → Aggressive improvements
    - DORMANT (0.1) → Conservative/stable
    - BLOOMING (0.3) → Crystallizing, less change
    """
    target = gesture.target
    synergies: list[str] = []
    changes: list[str] = []
    reasoning_trace: list[str] = []

    # Calculate garden-aware learning rate
    # Tone (0-1) × Plasticity (0.1-0.9) gives effective rate
    learning_rate = gesture.tone * garden.season.plasticity
    reasoning_trace.append(f"Base tone: {gesture.tone:.2f}")
    reasoning_trace.append(f"Season plasticity: {garden.season.plasticity:.2f}")
    reasoning_trace.append(f"Effective learning_rate: {learning_rate:.3f}")

    # Watering triggers TextGRAD if target is a prompt
    if target.startswith("concept.prompt"):
        synergies.append("textgrad:improvement_proposed")

        # Phase 5: Actually invoke TextGRAD with garden-aware parameters
        try:
            textgrad_result = await _invoke_textgrad_improvement(
                target=target,
                feedback=gesture.reasoning,
                learning_rate=learning_rate,
                garden_context={
                    "season": garden.season.name,
                    "plasticity": garden.season.plasticity,
                    "active_plot": garden.active_plot,
                },
            )

            if textgrad_result.content_changed:
                changes.append(f"TextGRAD improved: {target}")
                changes.extend(
                    f"  Modified: {s}" for s in textgrad_result.sections_modified
                )
                synergies.append("textgrad:improvement_applied")
            else:
                changes.append(f"TextGRAD analyzed (no changes): {target}")

            reasoning_trace.extend(textgrad_result.reasoning_trace)

        except Exception as e:
            # TextGRAD invocation failed - still record the watering attempt
            reasoning_trace.append(f"TextGRAD error: {e}")
            changes.append(f"Watered (TextGRAD unavailable): {target}")

    else:
        # Non-prompt target - record nurturing intent
        changes.append(f"Nurtured: {target}")
        reasoning_trace.append("Target is not a prompt, recorded nurturing intent")

    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=len(changes) > 0,
        changes=changes,
        synergies_triggered=synergies,
        reasoning_trace=tuple(reasoning_trace),
    )


async def _invoke_textgrad_improvement(
    target: str,
    feedback: str,
    learning_rate: float,
    garden_context: dict[str, Any],
) -> Any:
    """
    Invoke TextGRAD improvement with garden-aware parameters.

    Phase 5: This bridges the tending calculus with the Evergreen Prompt System.

    Args:
        target: The AGENTESE path to improve (e.g., "concept.prompt.task.X")
        feedback: Natural language feedback for improvement
        learning_rate: Garden-adjusted learning rate (tone × plasticity)
        garden_context: Garden context dict (season, plasticity, active_plot)

    Returns:
        ImprovementResult from TextGRAD
    """
    from dataclasses import dataclass

    # Import TextGRAD improver
    try:
        from protocols.prompt.textgrad import TextGRADImprover

        # Create improver with garden-adjusted learning rate
        improver = TextGRADImprover(learning_rate=learning_rate)

        # For now, we create a minimal sections dict based on target
        # In production, this would load the actual prompt sections
        section_name = target.replace("concept.prompt.", "").replace(".", "_")
        sections = {section_name: f"# {section_name}\n\nTarget for improvement."}

        # Apply improvement
        result = improver.improve(sections, feedback)
        return result

    except ImportError:
        # TextGRAD not available - return stub result
        @dataclass
        class StubResult:
            content_changed: bool = False
            sections_modified: tuple[str, ...] = ()
            reasoning_trace: tuple[str, ...] = ("TextGRAD import failed",)

        return StubResult()


async def _handle_rotate(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle ROTATE gesture: change perspective.

    Rotation changes how we observe the garden (observer switch)
    or transitions seasons.
    """
    target = gesture.target

    if target == "concept.gardener.season":
        # Season rotation is handled by garden.transition_season()
        return TendingResult(
            gesture=gesture,
            accepted=True,
            state_changed=True,
            changes=["Season rotation requested"],
            synergies_triggered=[],
            reasoning_trace=(
                f"Current season: {garden.season.name}",
                "Use concept.gardener.season.transition for full rotation",
            ),
        )

    # Perspective rotation (observer change)
    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=False,
        changes=[],
        synergies_triggered=[],
        reasoning_trace=(
            f"Rotated perspective on: {target}",
            f"Observer: {gesture.observer}",
        ),
    )


async def _handle_wait(
    garden: "GardenState",
    gesture: TendingGesture,
) -> TendingResult:
    """
    Handle WAIT gesture: allow time to pass.

    Waiting is free and doesn't change state.
    It's an intentional non-action—acknowledging that
    sometimes the best tending is no tending.
    """
    return TendingResult(
        gesture=gesture,
        accepted=True,
        state_changed=False,
        changes=[],
        synergies_triggered=[],
        reasoning_trace=(
            "Waiting...",
            f"The garden rests at {garden.season.name}",
            "Sometimes the best gesture is patience",
        ),
    )


# =============================================================================
# Gesture Builders (Ergonomic Factories)
# =============================================================================


def observe(target: str, reasoning: str = "") -> TendingGesture:
    """Create an OBSERVE gesture."""
    return TendingGesture(
        verb=TendingVerb.OBSERVE,
        target=target,
        tone=0.5,
        reasoning=reasoning or f"Observing {target}",
        entropy_cost=TendingVerb.OBSERVE.base_entropy_cost,
    )


def prune(target: str, reasoning: str, tone: float = 0.5) -> TendingGesture:
    """Create a PRUNE gesture."""
    return TendingGesture(
        verb=TendingVerb.PRUNE,
        target=target,
        tone=tone,
        reasoning=reasoning,
        entropy_cost=TendingVerb.PRUNE.base_entropy_cost,
    )


def graft(target: str, reasoning: str, tone: float = 0.7) -> TendingGesture:
    """Create a GRAFT gesture."""
    return TendingGesture(
        verb=TendingVerb.GRAFT,
        target=target,
        tone=tone,
        reasoning=reasoning,
        entropy_cost=TendingVerb.GRAFT.base_entropy_cost,
    )


def water(target: str, feedback: str, tone: float = 0.5) -> TendingGesture:
    """Create a WATER gesture (TextGRAD nurturing)."""
    return TendingGesture(
        verb=TendingVerb.WATER,
        target=target,
        tone=tone,
        reasoning=feedback,
        entropy_cost=TendingVerb.WATER.base_entropy_cost,
    )


def rotate(target: str, reasoning: str = "") -> TendingGesture:
    """Create a ROTATE gesture."""
    return TendingGesture(
        verb=TendingVerb.ROTATE,
        target=target,
        tone=0.5,
        reasoning=reasoning or f"Rotating perspective on {target}",
        entropy_cost=TendingVerb.ROTATE.base_entropy_cost,
    )


def wait(reasoning: str = "") -> TendingGesture:
    """Create a WAIT gesture."""
    return TendingGesture(
        verb=TendingVerb.WAIT,
        target="",
        tone=0.0,
        reasoning=reasoning or "Allowing time to pass",
        entropy_cost=0.0,
    )


# =============================================================================
# Synergy Event Emission (Phase 6)
# =============================================================================


async def _emit_gesture_applied_event(
    garden: "GardenState",
    gesture: TendingGesture,
    result: TendingResult,
) -> None:
    """
    Emit a GESTURE_APPLIED synergy event.

    Only called for significant (state-changing) gestures.
    This allows Brain to auto-capture garden state changes.
    """
    try:
        from protocols.synergy import get_synergy_bus
        from protocols.synergy.events import create_gesture_applied_event

        event = create_gesture_applied_event(
            garden_id=garden.garden_id,
            gesture_verb=gesture.verb.name,
            target=gesture.target,
            success=result.success,
            state_changed=result.state_changed,
            synergies_triggered=result.synergies_triggered,
            tone=gesture.tone,
            reasoning=gesture.reasoning,
        )

        # Emit event (fire-and-forget via bus)
        await get_synergy_bus().emit(event)

    except ImportError:
        # Synergy module not available - skip silently
        pass
    except Exception as e:
        # Log but don't fail the gesture
        import logging

        logger = logging.getLogger("kgents.gardener.synergy")
        logger.warning(f"Failed to emit gesture event: {e}")


__all__ = [
    "TendingVerb",
    "TendingGesture",
    "TendingResult",
    "apply_gesture",
    # Builders
    "observe",
    "prune",
    "graft",
    "water",
    "rotate",
    "wait",
]
