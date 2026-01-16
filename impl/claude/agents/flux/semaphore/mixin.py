"""
Semaphore mixin utilities.

Type checking utilities for SemaphoreToken detection.
"""

from typing import Any

from .token import SemaphoreToken


def is_semaphore_token(result: Any) -> bool:
    """
    Check if a result is a SemaphoreToken.

    Args:
        result: Any result from agent.invoke()

    Returns:
        True if result is a SemaphoreToken, False otherwise
    """
    return isinstance(result, SemaphoreToken)
