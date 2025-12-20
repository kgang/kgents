"""
JSON Projection for Gardener-Logos.

API-friendly JSON representation of the garden state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..garden import GardenState


def project_garden_to_json(
    garden: "GardenState",
    include_gestures: bool = True,
    gesture_limit: int = 10,
) -> dict[str, Any]:
    """
    Project garden state to JSON for API responses.

    This is the canonical JSON representation used by:
    - REST API endpoints
    - WebSocket streaming
    - React frontend consumption

    Args:
        garden: Garden state to project
        include_gestures: Whether to include gesture history
        gesture_limit: Max gestures to include

    Returns:
        JSON-serializable dict
    """
    result = garden.to_dict()

    # Add computed fields
    result["computed"] = {
        "health_score": garden.metrics.health_score,
        "entropy_remaining": max(0, garden.metrics.entropy_budget - garden.metrics.entropy_spent),
        "entropy_percentage": (
            (garden.metrics.entropy_budget - garden.metrics.entropy_spent)
            / garden.metrics.entropy_budget
            if garden.metrics.entropy_budget > 0
            else 0
        ),
        "active_plot_count": len([p for p in garden.plots.values() if p.is_active]),
        "total_plot_count": len(garden.plots),
        "season_plasticity": garden.season.plasticity,
        "season_entropy_multiplier": garden.season.entropy_multiplier,
    }

    # Optionally limit gestures
    if include_gestures:
        result["recent_gestures"] = [g.to_dict() for g in garden.recent_gestures[-gesture_limit:]]
    else:
        result.pop("recent_gestures", None)

    return result


__all__ = ["project_garden_to_json"]
