"""
License gate decorator and utilities.

Provides @requires_tier decorator for feature gating and runtime license checking.
"""

from __future__ import annotations

import contextvars
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from protocols.licensing.tiers import LicenseTier

if TYPE_CHECKING:
    pass

# Context variable to track current license tier
_current_tier: contextvars.ContextVar[LicenseTier] = contextvars.ContextVar(
    "license_tier",
    default=LicenseTier.FREE,
)

P = ParamSpec("P")
T = TypeVar("T")


class LicenseError(Exception):
    """Raised when feature requires higher tier."""

    def __init__(self, feature: str, required: LicenseTier, current: LicenseTier):
        self.feature = feature
        self.required = required
        self.current = current
        super().__init__(
            f"Feature '{feature}' requires {required.name} tier. "
            f"Current tier: {current.name}. "
            f"Upgrade at https://kgents.io/pricing"
        )


def get_current_tier() -> LicenseTier:
    """Get the current license tier from context."""
    return _current_tier.get()


def set_current_tier(tier: LicenseTier) -> None:
    """Set the current license tier in context."""
    _current_tier.set(tier)


def check_tier(required: LicenseTier, current: LicenseTier | None = None) -> bool:
    """
    Check if current tier meets requirement.

    Args:
        required: Required license tier
        current: Current tier (defaults to context tier)

    Returns:
        True if current >= required
    """
    if current is None:
        current = get_current_tier()
    result: bool = current >= required
    return result


def requires_tier(tier: LicenseTier) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to gate features by license tier.

    Usage:
        @requires_tier(LicenseTier.PRO)
        def soul_advise(prompt: str) -> str:
            ...

    Args:
        tier: Minimum required license tier

    Raises:
        LicenseError: If current tier is insufficient
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get current tier from context
            current_tier = _extract_tier_from_context(args, kwargs)

            if current_tier < tier:
                raise LicenseError(func.__name__, tier, current_tier)

            return func(*args, **kwargs)

        # Store metadata on wrapper for introspection
        wrapper.__license_tier__ = tier  # type: ignore[attr-defined]
        return wrapper

    return decorator


def requires_tier_async(
    tier: LicenseTier,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Async version of requires_tier decorator.

    Usage:
        @requires_tier_async(LicenseTier.PRO)
        async def soul_advise_async(prompt: str) -> str:
            ...

    Args:
        tier: Minimum required license tier

    Raises:
        LicenseError: If current tier is insufficient
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get current tier from context
            current_tier = _extract_tier_from_context(args, kwargs)

            if current_tier < tier:
                raise LicenseError(func.__name__, tier, current_tier)

            # Call async function
            result: T = await func(*args, **kwargs)  # type: ignore[misc]
            return result

        # Store metadata on wrapper for introspection
        wrapper.__license_tier__ = tier  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def _extract_tier_from_context(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> LicenseTier:
    """
    Extract license tier from function arguments or context.

    Priority:
    1. Explicit 'license_tier' kwarg
    2. Context object with 'license_tier' attribute
    3. Global context variable
    4. Default to FREE

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Extracted license tier
    """
    # Check kwargs for explicit tier
    if "license_tier" in kwargs:
        tier = kwargs["license_tier"]
        if isinstance(tier, LicenseTier):
            return tier

    # Check first arg for context object with tier
    if args:
        first_arg = args[0]
        if hasattr(first_arg, "license_tier"):
            tier = getattr(first_arg, "license_tier")
            if isinstance(tier, LicenseTier):
                return tier

    # Fall back to context variable
    return get_current_tier()


def get_tier_requirement(func: Callable[..., Any]) -> LicenseTier | None:
    """
    Get the tier requirement for a decorated function.

    Args:
        func: Function to inspect

    Returns:
        Required tier or None if not gated
    """
    return getattr(func, "__license_tier__", None)
