"""
Shared types for I-gent data layer.

This module contains types that need to be shared across data and widget modules
to avoid circular imports.
"""

from __future__ import annotations

from enum import Enum


class Phase(Enum):
    """
    Agent lifecycle phase.

    The phase determines visual density and color mapping.
    """

    ACTIVE = "ACTIVE"  # Full activity, high density
    WAKING = "WAKING"  # Spinning up, medium-high density
    WANING = "WANING"  # Spinning down, medium-low density
    DORMANT = "DORMANT"  # Minimal activity, low density
    VOID = "VOID"  # Special state - glitch territory
