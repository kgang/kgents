"""
Keybinding Registry: Central registry for all editor keybindings.

The registry maps key sequences to EditorInput types, supporting:
- Mode-specific bindings (different behavior per mode)
- Multi-key sequences (like "gh", "gl", "gj", "gk")
- Leader key sequences (like "<Leader>k")

See: spec/surfaces/hypergraph-editor.md § Keybindings
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..core.types import EditorInput, EditorMode

# =============================================================================
# Types
# =============================================================================


@dataclass(frozen=True)
class KeyBinding:
    """
    A single keybinding.

    Attributes:
        keys: Key sequence (e.g., "gh", "i", "<Esc>", "<Leader>k")
        modes: Modes where this binding is active
        input_factory: Factory function that creates the EditorInput
        description: Human-readable description (for help/docs)
    """

    keys: str
    modes: frozenset[EditorMode]
    input_factory: Callable[[], EditorInput]
    description: str = ""


# Type for pending sequence state
@dataclass
class PendingSequence:
    """State for multi-key sequence in progress."""

    keys: str = ""  # Keys accumulated so far
    last_key_time: float = 0.0  # Timestamp of last key
    timeout: float = 1.0  # Seconds before sequence resets


# =============================================================================
# Registry
# =============================================================================


class KeybindingRegistry:
    """
    Central registry for all keybindings.

    Manages mode-specific keybindings and resolves key sequences to EditorInputs.
    Supports multi-key sequences with timeout-based reset.

    Example:
        >>> registry = KeybindingRegistry()
        >>> registry.register(KeyBinding(
        ...     keys="gh",
        ...     modes=frozenset([EditorMode.NORMAL]),
        ...     input_factory=lambda: NavigateInput(direction="parent"),
        ...     description="Go to parent node"
        ... ))
        >>> registry.resolve("gh", EditorMode.NORMAL)
        NavigateInput(direction='parent', metadata={})
    """

    def __init__(self) -> None:
        # Map: keys → list of bindings (multiple modes may share same keys)
        self._bindings: dict[str, list[KeyBinding]] = {}

        # Map: (mode, keys_prefix) → bool (for quick prefix checks)
        self._prefixes: set[tuple[EditorMode, str]] = set()

    def register(self, binding: KeyBinding) -> None:
        """
        Register a keybinding.

        Args:
            binding: The keybinding to register

        Example:
            >>> registry.register(KeyBinding(
            ...     keys="gl",
            ...     modes=frozenset([EditorMode.NORMAL]),
            ...     input_factory=lambda: NavigateInput(direction="child"),
            ...     description="Go to child node"
            ... ))
        """
        if binding.keys not in self._bindings:
            self._bindings[binding.keys] = []

        self._bindings[binding.keys].append(binding)

        # Register all prefixes for each mode
        # e.g., "gh" → register ("NORMAL", "g") and ("NORMAL", "gh")
        for mode in binding.modes:
            for i in range(1, len(binding.keys) + 1):
                prefix = binding.keys[:i]
                self._prefixes.add((mode, prefix))

    def resolve(self, keys: str, mode: EditorMode) -> EditorInput | None:
        """
        Resolve key sequence to EditorInput for current mode.

        Args:
            keys: The key sequence to resolve (e.g., "gh", "i", "<Esc>")
            mode: Current editor mode

        Returns:
            EditorInput if binding exists and is active in mode, else None

        Example:
            >>> input = registry.resolve("gh", EditorMode.NORMAL)
            >>> input.direction
            'parent'
        """
        bindings = self._bindings.get(keys, [])

        # Find first binding matching current mode
        for binding in bindings:
            if mode in binding.modes:
                return binding.input_factory()

        return None

    def is_prefix(self, keys: str, mode: EditorMode) -> bool:
        """
        Check if keys could be prefix of a valid binding in current mode.

        This is used to determine whether to wait for more keys or
        reject the sequence immediately.

        Args:
            keys: Partial key sequence (e.g., "g" when expecting "gh")
            mode: Current editor mode

        Returns:
            True if keys is a prefix of any binding in mode

        Example:
            >>> registry.is_prefix("g", EditorMode.NORMAL)
            True  # Could be "gh", "gl", "gj", "gk", etc.
            >>> registry.is_prefix("x", EditorMode.NORMAL)
            False  # No bindings start with "x"
        """
        return (mode, keys) in self._prefixes

    def bindings_for_mode(self, mode: EditorMode) -> list[KeyBinding]:
        """
        Get all bindings active in a specific mode.

        Useful for displaying help/cheat sheets.

        Args:
            mode: Editor mode to query

        Returns:
            List of bindings active in mode
        """
        result = []
        for bindings in self._bindings.values():
            for binding in bindings:
                if mode in binding.modes:
                    result.append(binding)
        return result

    def all_bindings(self) -> list[KeyBinding]:
        """Get all registered bindings (across all modes)."""
        result = []
        for bindings in self._bindings.values():
            result.extend(bindings)
        return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "KeyBinding",
    "KeybindingRegistry",
    "PendingSequence",
]
