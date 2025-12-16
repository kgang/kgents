"""
Status Chrome: Error, Refusal, and Cache badge rendering.

Chrome components wrap widget content with status indicators:
- ErrorPanel: Technical error display with retry affordance
- RefusalPanel: Semantic refusal display (distinct from errors)
- CachedBadge: Prominent [CACHED] indicator for stale data

Usage:
    from protocols.projection.chrome import ErrorPanel, RefusalPanel, CachedBadge

    # Render error
    error_info = ErrorInfo(category="network", code="CONN", message="Failed")
    panel = ErrorPanel(error_info)
    print(panel.to_cli())

    # Render cache badge
    badge = CachedBadge(age_seconds=120)
    print(badge.to_cli())  # "[CACHED 2m ago]"
"""

from protocols.projection.chrome.cache import CachedBadge
from protocols.projection.chrome.error import ErrorPanel
from protocols.projection.chrome.refusal import RefusalPanel

__all__ = [
    "ErrorPanel",
    "RefusalPanel",
    "CachedBadge",
]
