"""
A-gents: Abstract Architectures + Art/Creativity

A-gents provide:
- The agent skeleton (what every agent MUST be)
- Creativity-focused agents for idea expansion

The key insight of A-gents: Agent[A, B] from bootstrap IS the skeleton.
AbstractAgent is just an alias for semantic clarity.

For richer metadata, use AgentMeta (optional).
"""

from .skeleton import (
    # The skeleton (re-exported from bootstrap)
    AbstractAgent,
    # Optional metadata
    AgentMeta,
    AgentIdentity,
    AgentInterface,
    AgentBehavior,
    # Utilities
    has_meta,
    get_meta,
)

from .creativity import (
    # Types
    CreativityMode,
    CreativityInput,
    CreativityResponse,
    Persona,
    # Agent
    CreativityCoach,
    # Convenience functions
    creativity_coach,
    playful_coach,
    philosophical_coach,
    provocative_coach,
)

__all__ = [
    # Core skeleton
    "AbstractAgent",
    # Metadata (optional)
    "AgentMeta",
    "AgentIdentity",
    "AgentInterface",
    "AgentBehavior",
    # Utilities
    "has_meta",
    "get_meta",
    # Creativity Coach
    "CreativityMode",
    "CreativityInput",
    "CreativityResponse",
    "Persona",
    "CreativityCoach",
    "creativity_coach",
    "playful_coach",
    "philosophical_coach",
    "provocative_coach",
]
