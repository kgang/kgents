"""
Flux-Semaphore integration utilities.

Functions for processing semaphore tokens and reentry contexts
within the FluxAgent stream processing loop.
"""

from typing import TYPE_CHECKING, Any

from .reentry import ReentryContext
from .token import SemaphoreToken

if TYPE_CHECKING:
    from agents.poly.types import Agent

    from .purgatory import Purgatory


def is_reentry_context(event: Any) -> bool:
    """
    Check if an event is a ReentryContext.

    Args:
        event: Any event from the merged source

    Returns:
        True if event is a ReentryContext, False otherwise
    """
    return isinstance(event, ReentryContext)


async def process_semaphore_result(
    token: SemaphoreToken[Any],
    purgatory: "Purgatory",
    original_event: Any,
) -> None:
    """
    Process a SemaphoreToken result by saving to Purgatory.

    This is called when agent.invoke() returns a SemaphoreToken,
    signaling that the agent needs human input before proceeding.

    Args:
        token: The SemaphoreToken returned by the agent
        purgatory: The Purgatory instance to save to
        original_event: The original event that triggered this
    """
    await purgatory.save(token)


async def process_reentry_event(
    reentry: ReentryContext[Any],
    agent: "Agent[Any, Any]",
) -> Any:
    """
    Process a ReentryContext by resuming the agent.

    This is called when a human has resolved a semaphore and
    a ReentryContext is injected back into the stream.

    Args:
        reentry: The ReentryContext with frozen state and human input
        agent: The inner agent to resume

    Returns:
        The result of agent.resume() if available, or re-invoke result
    """
    # Check if agent has resume method (Semaphore mixin)
    if hasattr(agent, "resume"):
        return await agent.resume(reentry.frozen_state, reentry.human_input)

    # Fallback: re-invoke with human input
    # This handles agents that don't implement the semaphore protocol
    return await agent.invoke(reentry.human_input)
