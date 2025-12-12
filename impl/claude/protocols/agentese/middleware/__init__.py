"""
AGENTESE Middleware

Middleware components that wrap Logos invocations for:
- Aesthetic filtering (WundtCurator)
- Future: Rate limiting, caching, logging
"""

from .curator import (
    SemanticDistance,
    TasteScore,
    WundtCurator,
    structural_surprise,
    wundt_score,
)

__all__ = [
    "WundtCurator",
    "TasteScore",
    "SemanticDistance",
    "wundt_score",
    "structural_surprise",
]
