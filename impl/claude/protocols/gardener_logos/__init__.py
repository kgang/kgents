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

from .garden import GardenSeason, GardenState, create_garden
from .plots import PlotState, create_plot
from .tending import TendingGesture, TendingVerb, apply_gesture
from .personality import TendingPersonality, default_personality

__all__ = [
    # Core state
    "GardenSeason",
    "GardenState",
    "create_garden",
    # Plots
    "PlotState",
    "create_plot",
    # Tending
    "TendingGesture",
    "TendingVerb",
    "apply_gesture",
    # Personality
    "TendingPersonality",
    "default_personality",
]
