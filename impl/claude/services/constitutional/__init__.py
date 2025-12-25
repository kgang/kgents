"""
Constitutional Reward System (Generalized).

Implements the 7-Principle Constitutional reward function for evaluating
actions across all domains: chat, navigation, portal, edit.

Philosophy:
    "Every action is evaluated. Every domain is witnessed. Every score is principled."

See: spec/protocols/chat-unified.md §1.2, §4.2
See: spec/principles/CONSTITUTION.md
"""

from __future__ import annotations

from services.constitutional.reward import (
    Domain,
    Principle,
    PrincipleScore,
    constitutional_reward,
)

__all__ = [
    "Domain",
    "Principle",
    "PrincipleScore",
    "constitutional_reward",
]
