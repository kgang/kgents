"""
Coalition Forge Synergy: Cross-jewel integration for Wave 2.

This module provides the integration between Coalition Forge and other Crown Jewels:
- Coalition → Brain: Auto-capture task completions to memory
- Brain → Coalition: Query relevant context before formation
- Coalition → Gardener: Bridge to session orchestration

Usage:
    from agents.forge.synergy import (
        emit_task_complete,
        emit_coalition_formed,
        query_relevant_context,
    )

    # When a coalition forms
    await emit_coalition_formed(coalition)

    # Query Brain for relevant past tasks
    crystals = await query_relevant_context("research_report")

    # After task completes
    await emit_task_complete(task_instance, output)

The synergy bus will automatically:
1. Capture task results to Brain
2. Query relevant past tasks for context
3. Notify Gardener of task completions
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.forge.task import ForgeTaskInstance, TaskOutput


async def emit_coalition_formed(
    coalition_id: str,
    task_template: str,
    archetypes: list[str],
    eigenvector_compatibility: float = 0.0,
    estimated_credits: int = 0,
) -> None:
    """
    Emit a synergy event when a coalition forms.

    This triggers handlers that may want to:
    - Enrich the coalition with Brain context
    - Notify Gardener of the formation
    - Log for analytics

    Args:
        coalition_id: Unique coalition identifier
        task_template: The task template being executed
        archetypes: List of archetype names in the coalition
        eigenvector_compatibility: Compatibility score (0-1)
        estimated_credits: Estimated credit cost
    """
    from protocols.synergy import create_coalition_formed_event, get_synergy_bus

    event = create_coalition_formed_event(
        coalition_id=coalition_id,
        task_template=task_template,
        archetypes=archetypes,
        eigenvector_compatibility=eigenvector_compatibility,
        estimated_credits=estimated_credits,
    )

    bus = get_synergy_bus()
    await bus.emit(event)


async def emit_task_complete(
    task_instance: "ForgeTaskInstance",
    output: "TaskOutput",
) -> None:
    """
    Emit a synergy event when a coalition completes a task.

    This triggers the Coalition → Brain synergy handler which
    automatically captures the task result to memory.

    Args:
        task_instance: The completed ForgeTaskInstance
        output: The TaskOutput with deliverable
    """
    from protocols.synergy import create_task_complete_event, get_synergy_bus

    event = create_task_complete_event(
        task_id=task_instance.id,
        coalition_id=task_instance.coalition_id or "",
        task_template=task_instance.template_id,
        output_format=output.format.name if hasattr(output.format, 'name') else str(output.format),
        output_summary=output.summary[:200] if output.summary else "",
        credits_spent=output.credits_spent,
        handoffs=output.handoffs,
        duration_seconds=output.duration_seconds,
    )

    bus = get_synergy_bus()
    await bus.emit(event)


async def query_relevant_context(
    task_template: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Query Brain for relevant past task results.

    Before a coalition forms, this can be called to surface
    relevant context from past executions of similar tasks.

    Args:
        task_template: The task template to find context for
        limit: Maximum number of results

    Returns:
        List of relevant crystal summaries from Brain
    """
    try:
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Query for similar task results
        query = f"forge-{task_template} task coalition"
        result = await logos.invoke(
            "self.memory.query",
            observer,
            query=query,
            limit=limit,
        )

        crystals: list[dict[str, Any]] = result.get("crystals", [])
        return crystals
    except Exception:
        # Graceful degradation - return empty if Brain unavailable
        return []


async def query_context_for_coalition(
    task_template: str,
    task_description: str,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Query Brain for comprehensive context before coalition formation.

    This enriches the coalition with:
    - Past similar task results
    - Relevant domain knowledge
    - User preferences/history

    Args:
        task_template: The task template
        task_description: Natural language description of the task
        limit: Maximum crystals to surface

    Returns:
        Context dictionary with categorized crystals
    """
    context: dict[str, Any] = {
        "past_tasks": [],
        "domain_knowledge": [],
        "total_crystals": 0,
    }

    try:
        from protocols.agentese import create_brain_logos
        from protocols.agentese.node import Observer

        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        # Query for past tasks with same template
        past_result = await logos.invoke(
            "self.memory.query",
            observer,
            query=f"forge-{task_template}",
            limit=limit // 2,
        )
        context["past_tasks"] = past_result.get("crystals", [])

        # Query for domain knowledge based on description
        if task_description:
            domain_result = await logos.invoke(
                "self.memory.query",
                observer,
                query=task_description[:100],
                limit=limit // 2,
            )
            context["domain_knowledge"] = domain_result.get("crystals", [])

        context["total_crystals"] = (
            len(context["past_tasks"]) + len(context["domain_knowledge"])
        )

    except Exception:
        # Graceful degradation
        pass

    return context


class SynergyAwareForge:
    """
    Mixin that adds synergy capabilities to Coalition Forge.

    Usage:
        class MyForge(Forge, SynergyAwareForge):
            async def on_coalition_form(self, coalition):
                await self.emit_formation_synergy(coalition)
    """

    async def emit_formation_synergy(
        self,
        coalition_id: str,
        task_template: str,
        archetypes: list[str],
        eigenvector_compatibility: float = 0.0,
        estimated_credits: int = 0,
    ) -> None:
        """Emit synergy event for coalition formation."""
        await emit_coalition_formed(
            coalition_id=coalition_id,
            task_template=task_template,
            archetypes=archetypes,
            eigenvector_compatibility=eigenvector_compatibility,
            estimated_credits=estimated_credits,
        )

    async def emit_completion_synergy(
        self,
        task_instance: "ForgeTaskInstance",
        output: "TaskOutput",
    ) -> None:
        """Emit synergy event for task completion."""
        await emit_task_complete(task_instance, output)

    async def get_context_synergy(
        self,
        task_template: str,
        task_description: str = "",
    ) -> dict[str, Any]:
        """Get context from Brain for this task."""
        return await query_context_for_coalition(
            task_template=task_template,
            task_description=task_description,
        )


__all__ = [
    "emit_coalition_formed",
    "emit_task_complete",
    "query_relevant_context",
    "query_context_for_coalition",
    "SynergyAwareForge",
]
