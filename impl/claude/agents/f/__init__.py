"""
F-gents: Forge Agents

Permanent artifact synthesis from natural language intent.

Motto: "Intent crystallizes into artifact; contracts enable composition"
"""

from agents.f.contract import (
    CompositionRule,
    Contract,
    Invariant,
    synthesize_contract,
)
from agents.f.intent import (
    Dependency,
    DependencyType,
    Example,
    Intent,
    parse_intent,
)

__all__ = [
    # Intent parsing (Phase 1)
    "Dependency",
    "DependencyType",
    "Example",
    "Intent",
    "parse_intent",
    # Contract synthesis (Phase 2)
    "CompositionRule",
    "Contract",
    "Invariant",
    "synthesize_contract",
]
