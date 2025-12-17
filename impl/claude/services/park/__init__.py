"""
Park Crown Jewel: Punchdrunk Westworld Where Hosts Can Say No.

The Park provides immersive, consent-first agent experiences inspired by
Punchdrunk's Sleep No More and Westworld's narrative loops.

AGENTESE Paths:
- world.park.manifest      - Show park status
- world.park.host.list     - List park hosts
- world.park.host.get      - Get a host by ID or name
- world.park.host.create   - Create a new host
- world.park.host.interact - Interact with a host
- world.park.host.witness  - View host memories
- world.park.episode.start - Start a visitor episode
- world.park.episode.end   - End an episode
- world.park.scenario.list - List available scenarios
- world.park.scenario.get  - Get scenario by ID
- world.park.scenario.start - Start a scenario session

Services (Metaphysical Fullstack AD-009):
- persistence.py        - TableAdapter + D-gent for hosts, episodes, memories
- node.py               - AGENTESE node for Park (@node decorator)
- scenario_service.py   - Structured scenario management

Design DNA:
- Consent-first: Hosts can refuse uncomfortable interactions
- Observer-dependent: What you see depends on who you are
- Visible process: State machines are legible

See: docs/skills/metaphysical-fullstack.md
"""

from .persistence import (
    ParkPersistence,
    HostView,
    MemoryView,
    EpisodeView,
    InteractionView,
    LocationView,
    ParkStatus,
)
from .node import (
    ParkNode,
    ParkManifestRendering,
    HostRendering,
    HostListRendering,
    EpisodeRendering,
    InteractionRendering,
    MemoryListRendering,
    LocationListRendering,
)
from .scenario_service import (
    ScenarioService,
    create_scenario_service,
    ScenarioView,
    ScenarioDetailView,
    SessionView,
    TickResultView,
)

__all__ = [
    # Persistence
    "ParkPersistence",
    "HostView",
    "MemoryView",
    "EpisodeView",
    "InteractionView",
    "LocationView",
    "ParkStatus",
    # AGENTESE Node
    "ParkNode",
    "ParkManifestRendering",
    "HostRendering",
    "HostListRendering",
    "EpisodeRendering",
    "InteractionRendering",
    "MemoryListRendering",
    "LocationListRendering",
    # Scenario Service
    "ScenarioService",
    "create_scenario_service",
    "ScenarioView",
    "ScenarioDetailView",
    "SessionView",
    "TickResultView",
]
