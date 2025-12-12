"""
ReentryContext: The Green Card.

Injected back into Flux as high-priority Perturbation.
Carries all context needed to resume agent processing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

R = TypeVar("R")  # Human input type


@dataclass
class ReentryContext(Generic[R]):
    """
    The Green Card. Injected back into Flux as high-priority Perturbation.

    When a human resolves a semaphore, this carries:
    1. The frozen state from before ejection
    2. The human's input/decision
    3. Reference back to original event

    The agent's resume() method receives this to complete processing.

    The Reentry Flow:
    1. Human flips card green (resolves semaphore)
    2. Purgatory creates ReentryContext
    3. ReentryContext injected as Perturbation (priority=200)
    4. Agent.resume(frozen_state, human_input) completes work

    Example:
        >>> reentry = ReentryContext(
        ...     token_id="sem-abc12345",
        ...     frozen_state=token.frozen_state,
        ...     human_input="Approve",
        ...     original_event=token.original_event,
        ... )
        >>> # Inject as perturbation
        >>> perturbation = create_perturbation(reentry, priority=200)
        >>> await flux_agent._perturbation_queue.put(perturbation)
    """

    token_id: str
    """ID of the resolved SemaphoreToken."""

    frozen_state: bytes
    """
    Pickled state from before ejection.

    Agent unpickles to restore context for resume().
    """

    human_input: R
    """
    What the human provided.

    Type should match token.required_type if specified.
    """

    original_event: Any
    """
    The event that triggered the semaphore.

    For audit trail and debugging.
    """

    def __post_init__(self) -> None:
        """Validate reentry context."""
        if not self.token_id:
            raise ValueError("ReentryContext requires token_id")
