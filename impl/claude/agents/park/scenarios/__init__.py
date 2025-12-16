"""
Starter Scenarios for Punchdrunk Park.

Five canonical scenarios, one per ScenarioType:
1. MYSTERY: The Missing Artifact
2. COLLABORATION: Town Bridge Project
3. CONFLICT: The Resource Dispute
4. EMERGENCE: Market Day
5. PRACTICE: Board Presentation Practice

These serve as examples and starting points for custom scenarios.
"""

from __future__ import annotations

from .board_practice import BOARD_PRESENTATION_PRACTICE
from .market_day import MARKET_DAY
from .missing_artifact import THE_MISSING_ARTIFACT
from .resource_dispute import THE_RESOURCE_DISPUTE
from .town_bridge import TOWN_BRIDGE_PROJECT

# All starter scenarios
STARTER_SCENARIOS = [
    THE_MISSING_ARTIFACT,
    TOWN_BRIDGE_PROJECT,
    THE_RESOURCE_DISPUTE,
    MARKET_DAY,
    BOARD_PRESENTATION_PRACTICE,
]

__all__ = [
    # Individual scenarios
    "THE_MISSING_ARTIFACT",
    "TOWN_BRIDGE_PROJECT",
    "THE_RESOURCE_DISPUTE",
    "MARKET_DAY",
    "BOARD_PRESENTATION_PRACTICE",
    # Collection
    "STARTER_SCENARIOS",
]
