"""
AGENTESE Self Presence Context: Agent Cursor Visibility

CLI v7 Phase 3: Agent Presence

The self.presence context provides agent cursor visibility:
- self.presence.manifest - View active agent cursors
- self.presence.snapshot - Get current presence state
- self.presence.cursor - Get specific cursor
- self.presence.join - Join presence channel
- self.presence.leave - Leave presence channel
- self.presence.update - Update cursor state/activity
- self.presence.states - List available cursor states
- self.presence.circadian - Get circadian phase info

Agent Presence makes agents "visible" in the workspace:
- Cursors show what agents are focused on
- States indicate activity (working, exploring, suggesting)
- Circadian modulation adjusts animation by time of day

AGENTESE: self.presence.*

Industry Inspiration: sshx, Figma multiplayer

Principle Alignment:
- Joy-Inducing: Visible presence creates "inhabited" feeling
- Composable: Presence works with any projection surface
- Ethical: Users always see what agents are doing
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator

# Import from Crown Jewel (services/conductor/presence.py)
from services.conductor.presence import (
    AgentCursor,
    CircadianPhase,
    CursorState,
    PresenceChannel,
    get_presence_channel,
)

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

# Import contracts
from .presence_contracts import (
    CircadianResponse,
    CursorGetRequest,
    CursorGetResponse,
    CursorUpdateRequest,
    CursorUpdateResponse,
    DemoRequest,
    DemoResponse,
    JoinRequest,
    JoinResponse,
    LeaveRequest,
    LeaveResponse,
    PresenceManifestResponse,
    SnapshotResponse,
    StatesResponse,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    Observer = Umwelt[Any, Any]

logger = logging.getLogger(__name__)

# Presence affordances
PRESENCE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "snapshot",
    "cursor",
    "join",
    "leave",
    "update",
    "states",
    "circadian",
    "stream",
    "demo",
)

# Demo agent personalities for realistic simulation
DEMO_AGENTS = [
    {"id": "kgent-alpha", "name": "K-gent α", "personality": "explorer"},
    {"id": "kgent-beta", "name": "K-gent β", "personality": "worker"},
    {"id": "kgent-gamma", "name": "K-gent γ", "personality": "suggester"},
]

# Focus paths for demo exploration
DEMO_FOCUS_PATHS = [
    "self.memory",
    "self.soul",
    "world.town",
    "world.codebase",
    "concept.design",
    "self.garden",
    "world.morpheus",
    "self.witness",
]

# Active demo tasks (module-level to persist across instances)
_demo_tasks: dict[str, "asyncio.Task[None]"] = {}


@node(
    "self.presence",
    description="Agent presence - visible cursor states and activity indicators",
    singleton=True,
    contracts={
        # Perception aspects
        "manifest": Response(PresenceManifestResponse),
        "snapshot": Response(SnapshotResponse),
        "states": Response(StatesResponse),
        "circadian": Response(CircadianResponse),
        # Query aspects
        "cursor": Contract(CursorGetRequest, CursorGetResponse),
        # Mutation aspects
        "join": Contract(JoinRequest, JoinResponse),
        "leave": Contract(LeaveRequest, LeaveResponse),
        "update": Contract(CursorUpdateRequest, CursorUpdateResponse),
        "demo": Contract(DemoRequest, DemoResponse),
    },
    examples=[
        ("manifest", {}, "Get all active cursors"),
        ("stream", {}, "Stream cursor updates via SSE"),
        ("join", {"agent_id": "kgent", "display_name": "K-gent"}, "Join as K-gent"),
        (
            "update",
            {"agent_id": "kgent", "state": "exploring", "focus_path": "self.memory"},
            "Update cursor",
        ),
    ],
)
@dataclass
class PresenceNode(BaseLogosNode):
    """
    self.presence - Agent visibility interface.

    Makes agents visible in the workspace with:
    - Cursor states (waiting, following, exploring, working, suggesting)
    - Activity descriptions
    - Focus path (what AGENTESE path they're looking at)
    - Circadian modulation (animation speed by time of day)

    Pattern #2: CursorState has emoji, color, animation properties
    Pattern #9: Valid state transitions form directed graph
    Pattern #11: Circadian modulation adjusts animation
    """

    _handle: str = "self.presence"
    _channel: PresenceChannel | None = None

    def __post_init__(self) -> None:
        """Initialize with global channel if not injected."""
        if self._channel is None:
            self._channel = get_presence_channel()

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def channel(self) -> PresenceChannel:
        """Get the presence channel."""
        if self._channel is None:
            self._channel = get_presence_channel()
        return self._channel

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Presence is generally read-only for most archetypes.
        Only developers/operators can update cursors.
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return PRESENCE_AFFORDANCES

        # Most archetypes can view and stream presence
        if archetype_lower in ("architect", "artist", "researcher", "newcomer"):
            return ("manifest", "snapshot", "cursor", "states", "circadian", "stream")

        # Guest: manifest only
        return ("manifest",)

    async def manifest(self, observer: "Observer", **kwargs: Any) -> Renderable:
        """View active agent cursors and presence channel status."""
        try:
            cursors = self.channel.active_cursors
            phase = CircadianPhase.current()

            content_lines = [
                "Presence: Agent Visibility Layer",
                f"Active cursors: {len(cursors)}",
                f"Subscribers: {self.channel.subscriber_count}",
                f"Circadian phase: {phase.name} (tempo: {phase.tempo_modifier:.1f})",
                "",
            ]

            if cursors:
                content_lines.append("Active Agents:")
                for cursor in cursors:
                    age = (datetime.now() - cursor.last_update).total_seconds()
                    content_lines.append(
                        f"  {cursor.emoji} {cursor.display_name}: {cursor.activity}"
                    )
                    if cursor.focus_path:
                        content_lines.append(f"     └─ Focus: {cursor.focus_path}")
                    content_lines.append(f"     └─ State: {cursor.state.name} ({age:.0f}s ago)")
            else:
                content_lines.append("No agents currently active.")
                content_lines.append("")
                content_lines.append("To simulate agent presence:")
                content_lines.append(
                    "  self.presence.join[agent_id='k-gent', display_name='K-gent']"
                )

            return BasicRendering(
                summary="Presence: Agent Visibility Layer",
                content="\n".join(content_lines),
                metadata={
                    "affordances": list(PRESENCE_AFFORDANCES),
                    "active_count": len(cursors),
                    "phase": phase.name,
                    "tempo_modifier": phase.tempo_modifier,
                },
            )
        except Exception as e:
            logger.warning(f"Presence manifest failed: {e}")
            return BasicRendering(
                summary="Presence",
                content="Presence service not available.",
                metadata={"error": str(e)},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> Any:
        """Handle presence-specific aspects."""
        match aspect:
            case "snapshot":
                return await self._get_snapshot(observer, **kwargs)
            case "cursor" | "cursors":
                return await self._get_cursor(observer, **kwargs)
            case "join":
                return await self._join(observer, **kwargs)
            case "leave":
                return await self._leave(observer, **kwargs)
            case "update":
                return await self._update_cursor(observer, **kwargs)
            case "states":
                return await self._get_states(observer, **kwargs)
            case "circadian":
                return await self._get_circadian(observer, **kwargs)
            case "stream":
                return self._stream(observer, **kwargs)
            case "demo":
                return await self._demo(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("presence")],
        help="Get current presence snapshot",
        examples=["self.presence.snapshot"],
    )
    async def _get_snapshot(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current presence state snapshot."""
        snapshot = await self.channel.get_presence_snapshot()
        return snapshot

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("presence")],
        help="Get a specific agent cursor",
        examples=["self.presence.cursor[agent_id='k-gent']"],
    )
    async def _get_cursor(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get a specific agent cursor by ID."""
        agent_id = kwargs.get("agent_id")

        # If no agent_id, return all cursors
        if not agent_id:
            cursors = self.channel.active_cursors
            return {
                "cursors": [c.to_dict() for c in cursors],
                "count": len(cursors),
            }

        cursor = self.channel.get_cursor(agent_id)
        if cursor is None:
            return {"found": False, "error": f"Agent '{agent_id}' not found"}

        return {"found": True, "cursor": cursor.to_dict()}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("presence")],
        help="Join the presence channel",
        examples=["self.presence.join[agent_id='k-gent', display_name='K-gent']"],
    )
    async def _join(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Join the presence channel with a new cursor."""
        agent_id = kwargs.get("agent_id")
        display_name = kwargs.get("display_name")
        initial_state = kwargs.get("initial_state", "WAITING")
        activity = kwargs.get("activity", "Joining...")

        if not agent_id or not display_name:
            return {"success": False, "error": "agent_id and display_name required"}

        try:
            state = CursorState[initial_state.upper()]
        except KeyError:
            return {
                "success": False,
                "error": f"Invalid state '{initial_state}'. Valid states: {', '.join(s.name for s in CursorState)}",
            }

        cursor = AgentCursor(
            agent_id=agent_id,
            display_name=display_name,
            state=state,
            activity=activity,
        )

        await self.channel.join(cursor)

        return {
            "success": True,
            "cursor": cursor.to_dict(),
            "active_count": len(self.channel.active_cursors),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("presence")],
        help="Leave the presence channel",
        examples=["self.presence.leave[agent_id='k-gent']"],
    )
    async def _leave(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Leave the presence channel."""
        agent_id = kwargs.get("agent_id")
        if not agent_id:
            return {"success": False, "error": "agent_id required"}

        was_present = await self.channel.leave(agent_id)

        return {
            "success": True,
            "was_present": was_present,
            "active_count": len(self.channel.active_cursors),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("presence")],
        help="Update cursor state or activity",
        examples=[
            "self.presence.update[agent_id='k-gent', state='WORKING', activity='Processing...']"
        ],
    )
    async def _update_cursor(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update an existing cursor's state or activity."""
        agent_id = kwargs.get("agent_id")
        state = kwargs.get("state")
        activity = kwargs.get("activity")
        focus_path = kwargs.get("focus_path")

        if not agent_id:
            return {"success": False, "error": "agent_id required"}

        cursor = self.channel.get_cursor(agent_id)

        if cursor is None:
            return {"success": False, "error": f"Agent '{agent_id}' not found"}

        # Update state if provided
        if state:
            try:
                new_state = CursorState[state.upper()]
                if not cursor.transition_to(new_state):
                    return {
                        "success": False,
                        "error": f"Invalid transition: {cursor.state.name} → {state}",
                        "allowed_transitions": [s.name for s in cursor.state.can_transition_to],
                    }
            except KeyError:
                return {"success": False, "error": f"Invalid state '{state}'"}

        # Update activity/focus
        if activity is not None or focus_path is not None:
            cursor.update_activity(
                activity=activity or cursor.activity,
                focus_path=focus_path,
            )

        # Broadcast update
        await self.channel.broadcast(cursor)

        return {"success": True, "cursor": cursor.to_dict()}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("presence")],
        help="List available cursor states",
        examples=["self.presence.states"],
    )
    async def _get_states(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List all available cursor states with their properties."""
        states = []
        for state in CursorState:
            states.append(
                {
                    "name": state.name,
                    "emoji": state.emoji,
                    "color": state.color,
                    "tailwind_color": state.tailwind_color,
                    "animation_speed": state.animation_speed,
                    "description": state.description,
                    "can_transition_to": [s.name for s in state.can_transition_to],
                }
            )

        return {"states": states}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("time")],
        help="Get current circadian phase",
        examples=["self.presence.circadian"],
    )
    async def _get_circadian(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current circadian phase and modulation values."""
        phase = CircadianPhase.current()
        hour = datetime.now().hour

        return {
            "phase": phase.name,
            "tempo_modifier": phase.tempo_modifier,
            "warmth": phase.warmth,
            "hour": hour,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        streaming=True,
        help="Stream cursor updates in real-time via SSE",
        examples=["self.presence.stream"],
    )
    async def _stream(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream cursor updates in real-time via Server-Sent Events.

        Yields cursor updates as they happen, plus heartbeats.
        Initial batch yields all current cursors.
        """
        import asyncio

        poll_interval = float(kwargs.get("poll_interval", 5.0))

        # Track last seen state to detect changes
        last_seen: dict[str, str] = {}

        # Initial connection event
        yield {
            "type": "connected",
            "message": "Connected to presence stream",
            "timestamp": datetime.now().isoformat(),
        }

        # Send all current cursors as initial state
        for cursor in self.channel.active_cursors:
            yield {
                "type": "cursor_update",
                "cursor": cursor.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
            last_seen[cursor.agent_id] = cursor.last_update.isoformat()

        # Polling loop for changes
        while True:
            await asyncio.sleep(poll_interval)

            # Check for new/updated cursors
            current_cursors = self.channel.active_cursors
            current_ids = {c.agent_id for c in current_cursors}

            for cursor in current_cursors:
                cursor_time = cursor.last_update.isoformat()
                if cursor.agent_id not in last_seen or last_seen[cursor.agent_id] != cursor_time:
                    yield {
                        "type": "cursor_update",
                        "cursor": cursor.to_dict(),
                        "timestamp": datetime.now().isoformat(),
                    }
                    last_seen[cursor.agent_id] = cursor_time

            # Check for removed cursors
            for agent_id in list(last_seen.keys()):
                if agent_id not in current_ids:
                    yield {
                        "type": "cursor_removed",
                        "agent_id": agent_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                    del last_seen[agent_id]

            # Heartbeat
            yield {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
            }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("presence")],
        help="Start/stop demo mode with simulated agent cursors",
        examples=[
            "self.presence.demo",
            "self.presence.demo[action='start', agent_count=3]",
            "self.presence.demo[action='stop']",
        ],
    )
    async def _demo(
        self,
        observer: "Observer",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Start or stop demo mode with simulated agent cursors.

        Demo agents explore AGENTESE paths and transition through states,
        simulating the "coworking" feel of multiple agents present.

        Voice Anchor: "Agents pretending to be there with their cursors moving,
        kinda following my cursor, kinda doing its own thing."
        """
        import asyncio
        import random

        action = kwargs.get("action", "start")
        agent_count = min(int(kwargs.get("agent_count", 2)), 3)  # Max 3
        update_interval = float(kwargs.get("update_interval", 3.0))

        if action == "stop":
            # Stop all demo tasks
            stopped_ids = []
            for agent_id, task in list(_demo_tasks.items()):
                task.cancel()
                await self.channel.leave(agent_id)
                stopped_ids.append(agent_id)
                del _demo_tasks[agent_id]

            return {
                "success": True,
                "action": "stop",
                "message": f"Stopped {len(stopped_ids)} demo agents",
                "agent_ids": stopped_ids,
            }

        elif action == "start":
            # Stop any existing demos first
            for agent_id, task in list(_demo_tasks.items()):
                task.cancel()
                await self.channel.leave(agent_id)
            _demo_tasks.clear()

            started_ids = []

            async def demo_loop(agent_info: dict[str, str]) -> None:
                """Background task simulating agent behavior."""
                agent_id = agent_info["id"]
                display_name = agent_info["name"]
                personality = agent_info["personality"]

                # Join with initial state
                cursor = AgentCursor(
                    agent_id=agent_id,
                    display_name=display_name,
                    state=CursorState.WAITING,
                    activity="Starting up...",
                )
                await self.channel.join(cursor)

                # Personality-based behavior
                if personality == "explorer":
                    preferred_states = [
                        CursorState.EXPLORING,
                        CursorState.FOLLOWING,
                        CursorState.EXPLORING,
                    ]
                elif personality == "worker":
                    preferred_states = [
                        CursorState.WORKING,
                        CursorState.WORKING,
                        CursorState.FOLLOWING,
                    ]
                else:  # suggester
                    preferred_states = [
                        CursorState.SUGGESTING,
                        CursorState.EXPLORING,
                        CursorState.FOLLOWING,
                    ]

                try:
                    while True:
                        await asyncio.sleep(update_interval + random.random() * 2)

                        # Pick a state based on personality
                        target_state = random.choice(preferred_states)

                        # Ensure valid transition
                        if target_state not in cursor.state.can_transition_to:
                            # Find a valid intermediate state
                            for s in CursorState:
                                if s in cursor.state.can_transition_to:
                                    cursor.transition_to(s)
                                    break

                        cursor.transition_to(target_state)

                        # Update activity based on state
                        focus_path = random.choice(DEMO_FOCUS_PATHS)
                        activities = {
                            CursorState.EXPLORING: [
                                f"Exploring {focus_path}...",
                                f"Investigating {focus_path}",
                                f"Looking at {focus_path}",
                            ],
                            CursorState.WORKING: [
                                f"Processing in {focus_path}",
                                "Computing...",
                                f"Analyzing {focus_path}",
                            ],
                            CursorState.SUGGESTING: [
                                f"Found something in {focus_path}",
                                "I have an idea...",
                                f"Consider looking at {focus_path}",
                            ],
                            CursorState.FOLLOWING: [
                                "Following your lead...",
                                "Watching...",
                                "Standing by...",
                            ],
                            CursorState.WAITING: [
                                "Ready",
                                "Idle",
                                "Standing by",
                            ],
                        }
                        activity = random.choice(activities.get(cursor.state, ["Active..."]))
                        cursor.update_activity(activity, focus_path)

                        # Broadcast update
                        await self.channel.broadcast(cursor)

                except asyncio.CancelledError:
                    # Clean exit
                    pass

            # Start demo agents
            for i in range(agent_count):
                agent_info = DEMO_AGENTS[i]
                task = asyncio.create_task(demo_loop(agent_info))
                _demo_tasks[agent_info["id"]] = task
                started_ids.append(agent_info["id"])

            return {
                "success": True,
                "action": "start",
                "message": f"Started {len(started_ids)} demo agents",
                "agent_ids": started_ids,
            }

        else:
            return {
                "success": False,
                "action": action,
                "message": f"Unknown action: {action}. Use 'start' or 'stop'.",
                "agent_ids": [],
            }


# Factory function
def create_presence_node(channel: PresenceChannel | None = None) -> PresenceNode:
    """Create a PresenceNode instance."""
    node = PresenceNode()
    if channel is not None:
        node._channel = channel
    return node


__all__ = [
    "PresenceNode",
    "PRESENCE_AFFORDANCES",
    "create_presence_node",
]
