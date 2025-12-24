"""
Agent Semaphores: Pause/Resume Pattern (Simplified).

Minimal semaphore system for DP-native transformation.
Only Pause (SemaphoreToken) and Resume (ReentryContext) primitives.

The spec says: "DP state can encode continuation. Only need 2 files."

Core Components:
    - SemaphoreToken: The Red Card. Return this to pause.
    - ReentryContext: The Green Card. Injected to resume.
    - Purgatory: The waiting room. Tokens wait here until human resolves.
    - SemaphoreReason: Why paused (taxonomy).

Example:
    >>> from agents.flux.semaphore import (
    ...     SemaphoreToken,
    ...     SemaphoreReason,
    ...     Purgatory,
    ... )
    >>>
    >>> # Agent pauses for human input
    >>> token = SemaphoreToken(
    ...     reason=SemaphoreReason.APPROVAL_NEEDED,
    ...     frozen_state=pickle.dumps(my_state),
    ...     prompt="Delete 47 records?",
    ...     options=["Approve", "Reject"],
    ... )
    >>> return token  # Pause
    >>>
    >>> # Save to Purgatory
    >>> await purgatory.save(token)
    >>>
    >>> # Human resolves, Resume
    >>> reentry = await purgatory.resolve(token.id, "Approve")

Simplified (2025-12-24): Removed mixin, flux_integration, durable.
DP state will encode continuation. See _archive/dp-transformation-2024-12-24/.
"""

from .purgatory import Purgatory
from .reason import SemaphoreReason
from .reentry import ReentryContext
from .token import SemaphoreToken

__all__ = [
    "Purgatory",
    "ReentryContext",
    "SemaphoreReason",
    "SemaphoreToken",
]
