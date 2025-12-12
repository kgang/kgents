"""
Agent Semaphores: The Rodizio Pattern.

Human-in-the-loop coordination that allows FluxAgents to yield control
until humans provide context. Named after Brazilian steakhouse service.

The Core Insight:
    Traditional human-in-the-loop: ask question → block → wait → continue.
    Agent Semaphores: yield token → eject to Purgatory → stream continues →
                      human resolves → re-inject as Perturbation.

Key Components:
    - SemaphoreToken: The Red Card. Return this to flip red.
    - ReentryContext: The Green Card. Injected back as Perturbation.
    - Purgatory: The waiting room. Tokens wait here until human resolves.
    - SemaphoreReason: Why the agent yielded (taxonomy).
    - SemaphoreCapable: Protocol for agents that can yield semaphores.
    - SemaphoreMixin: Mixin with helpers for creating semaphores.

Example:
    >>> from agents.flux.semaphore import (
    ...     SemaphoreToken,
    ...     SemaphoreReason,
    ...     Purgatory,
    ... )
    >>>
    >>> # Agent encounters situation needing human input
    >>> token = SemaphoreToken(
    ...     reason=SemaphoreReason.APPROVAL_NEEDED,
    ...     frozen_state=pickle.dumps(my_state),
    ...     prompt="Delete 47 records?",
    ...     options=["Approve", "Reject"],
    ... )
    >>> return token  # NOT yield!
    >>>
    >>> # FluxAgent detects token, ejects to Purgatory
    >>> await purgatory.save(token)
    >>>
    >>> # Human resolves
    >>> reentry = await purgatory.resolve(token.id, "Approve")
    >>>
    >>> # ReentryContext injected as Perturbation
    >>> # Agent resumes with context

The Purgatory Pattern:
    We RETURN tokens (not YIELD), eject state to Purgatory, and re-inject
    via existing Perturbation mechanism. This solves:
    1. Python generators cannot be pickled (server restart loses stack frame)
    2. Head-of-line blocking (one semaphore blocks entire Flux stream)

Pheromone Signals:
    - purgatory.ejected: Token ejected to purgatory
    - purgatory.resolved: Token resolved by human
    - purgatory.cancelled: Token cancelled
    - purgatory.voided: Token deadline expired (defaulted on promise)
"""

from .durable import (
    DEFAULT_STATE,
    DurablePurgatory,
    PurgatoryState,
    create_and_recover_purgatory,
    create_durable_purgatory,
)
from .flux_integration import (
    SemaphoreFluxConfig,
    SemaphoreFluxMixin,
    create_reentry_perturbation,
    create_semaphore_flux,
    inject_reentry,
    is_reentry_context,
)
from .mixin import (
    SemaphoreCapable,
    SemaphoreMixin,
    is_semaphore_capable,
    is_semaphore_token,
)
from .purgatory import Purgatory
from .reason import SemaphoreReason
from .reentry import ReentryContext
from .token import SemaphoreToken

__all__ = [
    # Core types
    "Purgatory",
    "ReentryContext",
    "SemaphoreReason",
    "SemaphoreToken",
    # Durable (D-gent backed)
    "DEFAULT_STATE",
    "DurablePurgatory",
    "PurgatoryState",
    "create_and_recover_purgatory",
    "create_durable_purgatory",
    # Mixin and protocol
    "SemaphoreCapable",
    "SemaphoreMixin",
    "is_semaphore_capable",
    "is_semaphore_token",
    # Flux integration
    "SemaphoreFluxConfig",
    "SemaphoreFluxMixin",
    "create_reentry_perturbation",
    "create_semaphore_flux",
    "inject_reentry",
    "is_reentry_context",
]
