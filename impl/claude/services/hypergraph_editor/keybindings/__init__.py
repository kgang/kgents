"""
Keybindings: Keybinding registry and default configurations.

This package provides the keybinding system for the Hypergraph Editor:
- KeybindingRegistry: Central registry mapping keys → EditorInputs
- create_default_registry(): Factory for standard vim-like bindings

See: spec/surfaces/hypergraph-editor.md § Keybindings
"""

from .defaults import create_default_registry
from .registry import KeyBinding, KeybindingRegistry, PendingSequence

__all__ = [
    # Registry
    "KeyBinding",
    "KeybindingRegistry",
    "PendingSequence",
    # Defaults
    "create_default_registry",
]
