"""
A-gents: Abstract + Art

The letter A represents two intertwined concepts:
- Abstract: The foundational skeletons and patterns all agents inherit
- Art: Creativity coaching and ideation support

A is the first letter—the beginning. A-gents define:
1. What all agents have in common (the abstract skeleton)
2. How agents support human creativity (the art of collaboration)

The Identity agent (abstract skeleton) is in bootstrap as Id.
"""

from .creativity_coach import (
    CreativityCoach,
    creativity_coach,
    expand,
    connect,
    constrain,
    question,
)

from ..types import (
    CreativityInput,
    CreativityOutput,
    CreativityMode,
    CreativityPersona,
)

# Re-export Id from bootstrap as the abstract skeleton
from bootstrap import Id, id_agent

__all__ = [
    # Abstract (from bootstrap)
    'Id',
    'id_agent',

    # Art - Creativity Coach
    'CreativityCoach',
    'creativity_coach',
    'expand',
    'connect',
    'constrain',
    'question',

    # Types
    'CreativityInput',
    'CreativityOutput',
    'CreativityMode',
    'CreativityPersona',
]

# A-gents genus marker
GENUS = 'a'
