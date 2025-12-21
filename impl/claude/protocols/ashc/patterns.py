"""
L0 Kernel Pattern Matching

Structural-only pattern matching. No regex, no destructuring.
Per design decision: minimal kernel, fail-fast on errors.
"""

from __future__ import annotations

from typing import Any

from .ast import (
    DictPattern,
    L0Pattern,
    ListPattern,
    LiteralPattern,
    WildcardPattern,
)


class L0MatchError(Exception):
    """Error during pattern matching. Fail-fast."""

    def __init__(self, message: str, pattern: L0Pattern, value: Any):
        self.pattern = pattern
        self.value = value
        super().__init__(message)


def match(pattern: L0Pattern, value: Any) -> dict[str, Any] | None:
    """
    Structural pattern matching.

    Returns bindings dict if match succeeds, None if fails.
    Structural only: no regex, no guards, no destructuring.

    Args:
        pattern: The pattern to match against
        value: The value to match

    Returns:
        Dict of bindings if match succeeds, None if match fails
    """
    if isinstance(pattern, LiteralPattern):
        return _match_literal(pattern, value)
    elif isinstance(pattern, WildcardPattern):
        return _match_wildcard(pattern, value)
    elif isinstance(pattern, DictPattern):
        return _match_dict(pattern, value)
    elif isinstance(pattern, ListPattern):
        return _match_list(pattern, value)
    else:
        raise L0MatchError(
            f"Unknown pattern type: {type(pattern).__name__}",
            pattern,
            value,
        )


def _match_literal(pattern: LiteralPattern, value: Any) -> dict[str, Any] | None:
    """Match exact value."""
    if value == pattern.value:
        return {}
    return None


def _match_wildcard(pattern: WildcardPattern, value: Any) -> dict[str, Any] | None:
    """Match anything, bind to name."""
    return {pattern.name: value}


def _match_dict(pattern: DictPattern, value: Any) -> dict[str, Any] | None:
    """Match dictionary structure."""
    if not isinstance(value, dict):
        return None

    # Convert tuple keys to dict for easier lookup
    pattern_keys = dict(pattern.keys)

    # Check for exact key match (unless allow_extra)
    if not pattern.allow_extra and set(value.keys()) != set(pattern_keys.keys()):
        return None

    # Check that all pattern keys exist in value
    if not pattern.allow_extra:
        for key in pattern_keys:
            if key not in value:
                return None

    # Match each key's pattern
    bindings: dict[str, Any] = {}
    for key, subpattern in pattern_keys.items():
        if key not in value:
            return None
        sub_bindings = match(subpattern, value[key])
        if sub_bindings is None:
            return None
        bindings.update(sub_bindings)

    return bindings


def _match_list(pattern: ListPattern, value: Any) -> dict[str, Any] | None:
    """Match list structure."""
    if not isinstance(value, (list, tuple)):
        return None

    # Check length (unless allow_extra)
    if not pattern.allow_extra and len(value) != len(pattern.elements):
        return None

    # Must have at least as many elements as pattern
    if len(value) < len(pattern.elements):
        return None

    # Match each element's pattern
    bindings: dict[str, Any] = {}
    for i, subpattern in enumerate(pattern.elements):
        sub_bindings = match(subpattern, value[i])
        if sub_bindings is None:
            return None
        bindings.update(sub_bindings)

    return bindings


# =============================================================================
# Convenience constructors
# =============================================================================


def literal(value: Any) -> LiteralPattern:
    """Create a literal pattern."""
    return LiteralPattern(value)


def wildcard(name: str) -> WildcardPattern:
    """Create a wildcard pattern that binds to name."""
    return WildcardPattern(name)


def dict_pattern(keys: dict[str, L0Pattern], allow_extra: bool = False) -> DictPattern:
    """Create a dict pattern from a regular dict."""
    return DictPattern.from_dict(keys, allow_extra)


def list_pattern(*elements: L0Pattern, allow_extra: bool = False) -> ListPattern:
    """Create a list pattern from elements."""
    return ListPattern(elements=elements, allow_extra=allow_extra)
