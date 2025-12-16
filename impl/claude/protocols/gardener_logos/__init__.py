"""
Gardener-Logos: The Meta-Tending Substrate.

Unifies the Gardener Crown Jewel with Prompt Logos into a single
coherent system for tending the garden of prompts.

See: spec/protocols/gardener-logos.md

Core Concepts:
- Garden: The unified state (session + prompts + memory + season)
- Plot: A focused region of the garden with its own prompts
- Tending Gesture: A verb-oriented operation (observe, prune, graft, water, rotate, wait)
- Season: The garden's relationship to change

AGENTESE Paths:
- concept.gardener.manifest → Garden overview
- concept.gardener.tend → Apply tending gesture
- concept.gardener.season.* → Season operations
- concept.gardener.plot.* → Plot management
- concept.gardener.session.* → Session operations (existing)
- concept.prompt.* → Prompt Logos (delegated)
"""

from .coalition_bridge import (
    CoalitionSpawnRequest,
    CoalitionSpawnResult,
    GardenerCoalitionIntegration,
    graft_coalition,
    record_coalition_completion,
    spawn_coalition_from_garden,
)
from .garden import GardenSeason, GardenState, create_garden
from .persistence import (
    GardenStore,
    create_garden_store,
    get_garden_store,
    reset_garden_store,
)
from .personality import TendingPersonality, default_personality
from .plots import PlotState, create_crown_jewel_plots, create_plot
from .tending import TendingGesture, TendingVerb, apply_gesture

__all__ = [
    # Core state
    "GardenSeason",
    "GardenState",
    "create_garden",
    # Plots
    "PlotState",
    "create_plot",
    "create_crown_jewel_plots",
    # Tending
    "TendingGesture",
    "TendingVerb",
    "apply_gesture",
    # Personality
    "TendingPersonality",
    "default_personality",
    # Persistence (Phase 3)
    "GardenStore",
    "create_garden_store",
    "get_garden_store",
    "reset_garden_store",
    # Coalition Bridge (Wave 2)
    "CoalitionSpawnRequest",
    "CoalitionSpawnResult",
    "graft_coalition",
    "spawn_coalition_from_garden",
    "record_coalition_completion",
    "GardenerCoalitionIntegration",
]
