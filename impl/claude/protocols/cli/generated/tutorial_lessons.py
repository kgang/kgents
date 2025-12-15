"""
Auto-generated tutorial lessons.

Generated: 2025-12-15T00:04:09.831950+00:00
Source: protocols/cli/repl_tutorial.py:generate_lessons()

DO NOT EDIT - regenerate with: kg tutorial generate
"""

from __future__ import annotations

from typing import Any

# Auto-generated lesson data
CACHED_LESSONS: list[dict[str, Any]] = [
    {
        "name": "discover_self",
        "context": "root",
        "prompt": "Type 'self' to explore your agent's internal world (status, memory, soul):",
        "expected": ["self"],
        "hint": "Try typing: self",
        "celebration": "You've entered the self context. Type '?' to see what's here.",
    },
    {
        "name": "introspection",
        "context": "any",
        "prompt": "Type '?' to see available affordances in this context:",
        "expected": ["?"],
        "hint": "The question mark (?) shows what you can do here.",
        "celebration": "Introspection reveals affordances - the actions available to you.",
    },
    {
        "name": "navigate_up",
        "context": "any",
        "prompt": "Type '..' to go back up one level:",
        "expected": [".."],
        "hint": "Two dots (..) moves you up in the hierarchy.",
        "celebration": "Navigation is simple: enter a context, explore, go back with '..'",
    },
    {
        "name": "discover_world",
        "context": "root",
        "prompt": "Type 'world' to explore external entities (agents, infrastructure, daemons):",
        "expected": ["world"],
        "hint": "Try typing: world",
        "celebration": "You've entered the world context. Type '?' to see what's here.",
    },
    {
        "name": "discover_concept",
        "context": "root",
        "prompt": "Type 'concept' to explore abstract ideas (laws, principles, dialectics):",
        "expected": ["concept"],
        "hint": "Try typing: concept",
        "celebration": "You've entered the concept context. Type '?' to see what's here.",
    },
    {
        "name": "discover_void",
        "context": "root",
        "prompt": "Type 'void' to explore entropy and the Accursed Share (serendipity, shadow):",
        "expected": ["void"],
        "hint": "Try typing: void",
        "celebration": "You've entered the void context. Type '?' to see what's here.",
    },
    {
        "name": "discover_time",
        "context": "root",
        "prompt": "Type 'time' to explore temporal traces (past, future, schedules):",
        "expected": ["time"],
        "hint": "Try typing: time",
        "celebration": "You've entered the time context. Type '?' to see what's here.",
    },
    {
        "name": "composition",
        "context": "root",
        "prompt": "Type 'self.status >> concept.count' to compose a pipeline:",
        "expected": [
            "self.status >> concept.count",
            "self status >> concept count",
            "self.status>>concept.count",
        ],
        "hint": "The >> operator composes paths into pipelines.",
        "celebration": "Pipelines compose actions - the heart of AGENTESE. Composition over construction!",
    },
]
