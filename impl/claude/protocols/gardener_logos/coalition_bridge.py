"""
Coalition Bridge: Gardener ↔ Coalition Forge integration.

Wave 2: Extensions - Coalition → Gardener synergy.

This module bridges the Gardener tending calculus with Coalition Forge:
- Gardener can spawn coalitions via GRAFT gesture
- Coalition completions feed back to Gardener as observations
- Coalition context queries Brain for relevant Gardener memories

Usage:
    from protocols.gardener_logos.coalition_bridge import (
        graft_coalition,
        spawn_coalition_from_garden,
        record_coalition_completion,
    )

    # From a Gardener session, spawn a coalition
    gesture, coalition_id = await spawn_coalition_from_garden(
        garden=garden_state,
        task_template="research_report",
        task_description="Research competitors",
    )

    # Record coalition completion in garden
    await record_coalition_completion(
        garden=garden_state,
        task_id="task-123",
        output_summary="Found 5 competitors...",
        credits_spent=50,
    )
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .tending import TendingGesture, TendingResult, TendingVerb

if TYPE_CHECKING:
    from .garden import GardenState


@dataclass
class CoalitionSpawnRequest:
    """
    Request to spawn a coalition from Gardener.

    This captures the intent before the coalition is formed.
    """

    task_template: str
    task_description: str
    context_from_garden: list[str]  # Relevant crystals/memories
    estimated_credits: int
    garden_session_id: str


@dataclass
class CoalitionSpawnResult:
    """
    Result of spawning a coalition from Gardener.
    """

    success: bool
    coalition_id: str | None
    gesture: TendingGesture
    error: str | None = None


def graft_coalition(
    task_template: str,
    task_description: str,
    reasoning: str = "",
    garden_session_id: str | None = None,
    tone: float = 0.7,
) -> TendingGesture:
    """
    Create a GRAFT gesture for spawning a coalition.

    This is a specialized graft that targets the Coalition Forge
    and includes task information in the gesture metadata.

    Args:
        task_template: The coalition task template to use
        task_description: Natural language description
        reasoning: Why this coalition is being spawned
        garden_session_id: The originating Gardener session
        tone: How definitive (0.0=tentative, 1.0=definitive)

    Returns:
        TendingGesture for grafting a coalition
    """
    return TendingGesture(
        verb=TendingVerb.GRAFT,
        target=f"world.coalition.form:{task_template}",
        tone=tone,
        reasoning=reasoning or f"Spawning coalition for: {task_description[:50]}",
        entropy_cost=TendingVerb.GRAFT.base_entropy_cost
        * 1.5,  # Extra cost for coalition
        session_id=garden_session_id,
        result_summary=task_description[:100],
    )


async def spawn_coalition_from_garden(
    garden: "GardenState",
    task_template: str,
    task_description: str,
    reasoning: str = "",
) -> tuple[TendingGesture, str | None]:
    """
    Spawn a coalition from within a Gardener session.

    This:
    1. Creates a GRAFT gesture for the coalition
    2. Queries Brain for relevant context
    3. Emits the coalition formation event
    4. Returns the gesture and coalition ID

    Args:
        garden: The current garden state
        task_template: Which task template to use
        task_description: What the coalition should do
        reasoning: Why we're spawning this

    Returns:
        (TendingGesture, coalition_id or None on failure)
    """
    from agents.forge.synergy import emit_coalition_formed, query_context_for_coalition

    # Create the graft gesture
    gesture = graft_coalition(
        task_template=task_template,
        task_description=task_description,
        reasoning=reasoning,
        garden_session_id=garden.session_id,
    )

    # Query for relevant context from Brain (result used for logging/tracing)
    _ = await query_context_for_coalition(
        task_template=task_template,
        task_description=task_description,
    )

    # Generate coalition ID
    coalition_id = f"garden-coal-{uuid.uuid4().hex[:8]}"

    # Determine archetypes based on template
    archetypes = _suggest_archetypes_for_template(task_template)

    # Emit coalition formed event
    await emit_coalition_formed(
        coalition_id=coalition_id,
        task_template=task_template,
        archetypes=archetypes,
        eigenvector_compatibility=0.85,  # Would calculate from garden context
        estimated_credits=_estimate_credits_for_template(task_template),
    )

    # Record gesture in garden
    garden.add_gesture(gesture)

    return gesture, coalition_id


async def record_coalition_completion(
    garden: "GardenState",
    task_id: str,
    coalition_id: str,
    output_summary: str,
    credits_spent: int,
    handoffs: int = 0,
    success: bool = True,
) -> TendingGesture:
    """
    Record a coalition completion in the Gardener's garden.

    This creates an OBSERVE gesture that captures the coalition
    result as part of the garden's momentum.

    Args:
        garden: The garden state to update
        task_id: The completed task ID
        coalition_id: The coalition that completed
        output_summary: Summary of the output
        credits_spent: Credits used
        handoffs: Number of handoffs
        success: Whether task succeeded

    Returns:
        The OBSERVE gesture recorded
    """
    # Create observation gesture
    gesture = TendingGesture(
        verb=TendingVerb.OBSERVE,
        target=f"world.coalition.{coalition_id}.complete",
        tone=1.0 if success else 0.3,
        reasoning=f"Coalition completed: {output_summary[:50]}...",
        entropy_cost=0.01,  # Observation is nearly free
        session_id=garden.session_id,
        result_summary=f"Task {task_id}: {credits_spent} credits, {handoffs} handoffs",
    )

    # Record in garden
    garden.add_gesture(gesture)

    return gesture


def _suggest_archetypes_for_template(task_template: str) -> list[str]:
    """
    Suggest coalition archetypes based on task template.

    This maps task templates to typical coalition compositions.
    """
    archetype_map = {
        "research_report": ["Scout", "Sage", "Scribe"],
        "code_review": ["Steady", "Sync", "Scout"],
        "content_creation": ["Spark", "Sage", "Scribe"],
        "decision_analysis": ["Sage", "Scout", "Spark", "Steady", "Sync"],
        "competitive_intel": ["Scout", "Scout", "Sage", "Scribe"],
    }
    return archetype_map.get(task_template, ["Scout", "Sage"])


def _estimate_credits_for_template(task_template: str) -> int:
    """
    Estimate credits for a task template.

    This should eventually be more sophisticated, but for now
    uses simple heuristics.
    """
    credit_map = {
        "research_report": 50,
        "code_review": 30,
        "content_creation": 40,
        "decision_analysis": 75,
        "competitive_intel": 100,
    }
    return credit_map.get(task_template, 50)


class GardenerCoalitionIntegration:
    """
    Integration helper for Gardener → Coalition → Brain synergies.

    This class coordinates the full lifecycle:
    1. Gardener spawns coalition
    2. Coalition queries Brain for context
    3. Coalition executes
    4. Results feed back to Gardener and Brain

    Usage:
        integration = GardenerCoalitionIntegration(garden)
        result = await integration.spawn_and_track(
            "research_report",
            "Analyze competitor pricing strategies",
        )
    """

    def __init__(self, garden: "GardenState") -> None:
        self._garden = garden
        self._active_coalitions: dict[str, dict[str, Any]] = {}

    async def spawn_and_track(
        self,
        task_template: str,
        task_description: str,
        reasoning: str = "",
    ) -> CoalitionSpawnResult:
        """
        Spawn a coalition and track its progress.

        Args:
            task_template: Task template to use
            task_description: What the task should accomplish
            reasoning: Why we're spawning this

        Returns:
            CoalitionSpawnResult with status and IDs
        """
        try:
            gesture, coalition_id = await spawn_coalition_from_garden(
                garden=self._garden,
                task_template=task_template,
                task_description=task_description,
                reasoning=reasoning,
            )

            if coalition_id:
                self._active_coalitions[coalition_id] = {
                    "task_template": task_template,
                    "task_description": task_description,
                    "spawned_at": datetime.now(),
                    "gesture": gesture,
                }

            return CoalitionSpawnResult(
                success=True,
                coalition_id=coalition_id,
                gesture=gesture,
            )

        except Exception as e:
            # Create failure gesture
            failure_gesture = TendingGesture(
                verb=TendingVerb.OBSERVE,
                target=f"world.coalition.form:{task_template}",
                tone=0.0,
                reasoning=f"Coalition spawn failed: {e}",
                entropy_cost=0.01,
                session_id=self._garden.session_id,
            )
            self._garden.add_gesture(failure_gesture)

            return CoalitionSpawnResult(
                success=False,
                coalition_id=None,
                gesture=failure_gesture,
                error=str(e),
            )

    async def record_completion(
        self,
        coalition_id: str,
        task_id: str,
        output_summary: str,
        credits_spent: int,
        handoffs: int = 0,
    ) -> None:
        """
        Record coalition completion in garden.

        This is called when a coalition finishes its task.
        """
        success = coalition_id in self._active_coalitions

        # Record completion (result stored but not currently used)
        _ = await record_coalition_completion(
            garden=self._garden,
            task_id=task_id,
            coalition_id=coalition_id,
            output_summary=output_summary,
            credits_spent=credits_spent,
            handoffs=handoffs,
            success=success,
        )

        # Remove from active tracking
        if coalition_id in self._active_coalitions:
            del self._active_coalitions[coalition_id]

    @property
    def active_count(self) -> int:
        """Number of active coalitions from this garden."""
        return len(self._active_coalitions)


__all__ = [
    "CoalitionSpawnRequest",
    "CoalitionSpawnResult",
    "graft_coalition",
    "spawn_coalition_from_garden",
    "record_coalition_completion",
    "GardenerCoalitionIntegration",
]
