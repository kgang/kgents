"""
F-gents: Forge Agents

Permanent artifact synthesis from natural language intent.

Motto: "Intent crystallizes into artifact; contracts enable composition"
"""

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
]
