"""
Flux Integration for Agent Semaphores.

This module provides the integration between FluxAgent and the Semaphore system:
1. Detection of SemaphoreToken returns from inner.invoke()
2. Ejection to Purgatory with state preservation
3. Injection of ReentryContext as high-priority Perturbation
4. Resume handling for semaphore-capable agents

The Purgatory Pattern:
    Instead of blocking the flux stream, we EJECT the event to Purgatory
    and continue processing. When human resolves, we inject ReentryContext
    as a Perturbation.

Integration Points:
    - FluxAgent._process_event(): Detect SemaphoreToken, eject to Purgatory
    - Purgatory.resolve(): Returns ReentryContext
    - create_reentry_perturbation(): Wraps ReentryContext as Perturbation

Usage:
    >>> from agents.flux.semaphore import Purgatory, SemaphoreToken
    >>> from agents.flux.semaphore.flux_integration import (
    ...     SemaphoreAwareFlux,
    ...     create_reentry_perturbation,
    ... )
    >>>
    >>> # Wrap FluxAgent with semaphore awareness
    >>> flux = SemaphoreAwareFlux(inner=my_agent, purgatory=Purgatory())
    >>>
    >>> # Or use the factory
    >>> flux = create_semaphore_flux(my_agent)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

from ..perturbation import Perturbation, create_perturbation
from .mixin import is_semaphore_capable, is_semaphore_token
from .purgatory import Purgatory
from .reentry import ReentryContext
from .token import SemaphoreToken

if TYPE_CHECKING:
    from agents.poly.types import Agent

    from ..agent import FluxAgent

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type

# Priority for reentry perturbations (higher than normal perturbations)
REENTRY_PRIORITY = 200


def create_reentry_perturbation(
    reentry: ReentryContext[Any],
    loop: asyncio.AbstractEventLoop | None = None,
) -> Perturbation:
    """
    Create a Perturbation from a ReentryContext.

    The ReentryContext is injected into the flux stream as a high-priority
    Perturbation. The flux will detect this and route to agent.resume().

    Args:
        reentry: The ReentryContext from Purgatory.resolve()
        loop: Optional event loop for the Future

    Returns:
        Perturbation wrapping the ReentryContext
    """
    return create_perturbation(
        data=reentry,
        priority=REENTRY_PRIORITY,
        loop=loop,
    )


def is_reentry_context(event: Any) -> bool:
    """
    Check if an event is a ReentryContext.

    Used by FluxAgent to detect reentry perturbations.

    Args:
        event: The event to check

    Returns:
        True if event is a ReentryContext
    """
    return isinstance(event, ReentryContext)


@dataclass
class SemaphoreFluxConfig:
    """
    Configuration for semaphore-aware flux processing.

    Attributes:
        purgatory: The Purgatory instance for ejected events
        reentry_priority: Priority for reentry perturbations
        auto_void_on_start: Check for expired deadlines on flux start
    """

    purgatory: Purgatory = field(default_factory=Purgatory)
    reentry_priority: int = REENTRY_PRIORITY
    auto_void_on_start: bool = True


async def process_semaphore_result(
    token: SemaphoreToken[Any],
    purgatory: Purgatory,
    original_event: Any,
) -> None:
    """
    Process a SemaphoreToken result from inner.invoke().

    Called when FluxAgent detects that inner.invoke() returned a
    SemaphoreToken instead of a normal result.

    The Purgatory Pattern:
    1. Enrich token with original_event if not set
    2. Save to Purgatory
    3. (Caller should skip output emission and continue stream)

    Args:
        token: The SemaphoreToken returned by the agent
        purgatory: The Purgatory to eject to
        original_event: The event that triggered the semaphore

    Note:
        The flux stream continues after this. The blocked event waits
        in Purgatory, not in the flux.
    """
    # Enrich token with original event if not already set
    if token.original_event is None:
        token.original_event = original_event

    # Eject to Purgatory
    await purgatory.save(token)


async def process_reentry_event(
    reentry: ReentryContext[Any],
    agent: "Agent[Any, Any]",
) -> Any:
    """
    Process a ReentryContext by calling agent.resume().

    Called when FluxAgent detects a ReentryContext perturbation.

    Args:
        reentry: The ReentryContext from Purgatory.resolve()
        agent: The agent that yielded the semaphore (must be SemaphoreCapable)

    Returns:
        Result from agent.resume()

    Raises:
        RuntimeError: If agent does not implement resume()
    """
    if not is_semaphore_capable(agent):
        raise RuntimeError(
            f"Agent {agent.name} received ReentryContext but does not implement resume(). "
            "Agents that yield semaphores must implement SemaphoreCapable protocol."
        )

    # Call resume on the agent
    # Type safety: we've checked is_semaphore_capable, which verifies resume() exists
    resume_fn = getattr(agent, "resume")
    return await resume_fn(reentry.frozen_state, reentry.human_input)


async def inject_reentry(
    purgatory: Purgatory,
    flux: "FluxAgent[Any, Any]",
    token_id: str,
    human_input: Any,
) -> bool:
    """
    Resolve a semaphore and inject ReentryContext into flux.

    This is the "flip the card green" operation. Called by external
    code (CLI, API, etc.) when human provides context.

    Args:
        purgatory: The Purgatory containing the token
        flux: The FluxAgent to inject into
        token_id: ID of the token to resolve
        human_input: What the human provided

    Returns:
        True if successfully resolved and injected, False otherwise
    """
    reentry = await purgatory.resolve(token_id, human_input)
    if reentry is None:
        return False

    # Create perturbation and inject
    perturbation = create_reentry_perturbation(reentry)
    await flux._perturbation_queue.put(perturbation)
    return True


class SemaphoreFluxMixin:
    """
    Mixin that adds semaphore awareness to FluxAgent.

    This mixin provides the integration between FluxAgent's event processing
    and the Semaphore system. It should be mixed into FluxAgent or used
    via composition.

    Key behaviors:
    1. Detects SemaphoreToken returns from inner.invoke()
    2. Ejects to Purgatory instead of blocking
    3. Detects ReentryContext perturbations
    4. Routes to agent.resume() for completion

    Example:
        >>> class SemaphoreAwareFluxAgent(SemaphoreFluxMixin, FluxAgent):
        ...     pass  # Inherits semaphore-aware processing
    """

    _semaphore_config: SemaphoreFluxConfig

    def configure_semaphores(self, config: SemaphoreFluxConfig) -> None:
        """Configure semaphore handling."""
        self._semaphore_config = config

    @property
    def purgatory(self) -> Purgatory:
        """Get the Purgatory instance."""
        if not hasattr(self, "_semaphore_config"):
            self._semaphore_config = SemaphoreFluxConfig()
        return self._semaphore_config.purgatory

    async def _handle_semaphore_result(
        self,
        result: Any,
        original_event: Any,
    ) -> bool:
        """
        Check if result is SemaphoreToken and handle if so.

        Args:
            result: Return value from inner.invoke()
            original_event: The input event

        Returns:
            True if result was a SemaphoreToken (handled), False otherwise
        """
        if not is_semaphore_token(result):
            return False

        await process_semaphore_result(
            token=result,
            purgatory=self.purgatory,
            original_event=original_event,
        )
        return True

    async def _handle_reentry_event(
        self,
        event: Any,
    ) -> tuple[bool, Any]:
        """
        Check if event is ReentryContext and handle if so.

        Args:
            event: The event to check

        Returns:
            (True, result) if was ReentryContext, (False, None) otherwise
        """
        if not is_reentry_context(event):
            return False, None

        reentry: ReentryContext[Any] = event
        result = await process_reentry_event(
            reentry=reentry,
            agent=self.inner,  # type: ignore[attr-defined]
        )
        return True, result


# Factory function for creating semaphore-aware flux
def create_semaphore_flux(
    agent: "Agent[A, B]",
    purgatory: Purgatory | None = None,
    **flux_config: Any,
) -> "FluxAgent[A, B]":
    """
    Create a FluxAgent with semaphore awareness.

    This is a convenience factory that wraps a FluxAgent with
    semaphore integration. The returned flux will:
    1. Detect SemaphoreToken returns and eject to Purgatory
    2. Detect ReentryContext perturbations and route to resume()

    Args:
        agent: The inner agent to wrap
        purgatory: Optional Purgatory instance (creates one if not provided)
        **flux_config: Additional FluxConfig parameters

    Returns:
        Configured FluxAgent with semaphore support

    Note:
        This function patches the flux's processing to add semaphore
        detection. For full integration, consider using SemaphoreAwareFlux.
    """
    from ..agent import FluxAgent
    from ..config import FluxConfig

    flux: FluxAgent[A, B] = FluxAgent(
        inner=agent,
        config=FluxConfig(**flux_config),
    )

    # Attach purgatory
    semaphore_config = SemaphoreFluxConfig(
        purgatory=purgatory or Purgatory(),
    )
    setattr(flux, "_semaphore_config", semaphore_config)

    return flux
