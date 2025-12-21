"""
AGENTESE Self Swarm Context: Agent Swarm Coordination

CLI v7 Phase 6: Agent Swarms

The self.conductor.swarm context provides swarm coordination:
- self.conductor.swarm.manifest - View swarm status
- self.conductor.swarm.spawn - Spawn an agent with a role
- self.conductor.swarm.list - List active swarm agents
- self.conductor.swarm.delegate - Delegate task to another agent
- self.conductor.swarm.handoff - Hand off context to another agent
- self.conductor.swarm.despawn - Remove an agent from swarm
- self.conductor.swarm.roles - List available canonical roles

Agent Swarms enable multi-agent collaboration:
- Agents have roles = Behavior x Trust (composition, not new enum)
- A2A protocol enables agent-to-agent messaging
- SWARM_OPERAD provides composition grammar

AGENTESE: self.conductor.swarm.*

Industry Innovation: CrewAI roles, Microsoft A2A

Constitution Alignment:
- S5 (Composable): "Agents are morphisms in a category"
- S6 (Heterarchical): "Agents exist in flux, not fixed hierarchy"
- S7 (Generative): Role = Behavior x Trust (composition)
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from services.conductor.a2a import (
    A2AChannel,
    A2AMessage,
    A2AMessageType,
    get_a2a_registry,
)
from services.conductor.swarm import (
    COORDINATOR,
    IMPLEMENTER,
    PLANNER,
    RESEARCHER,
    REVIEWER,
    SwarmRole,
    SwarmSpawner,
)

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Contracts (Pattern #13: Contract-First Types)
# =============================================================================


@dataclass
class SwarmManifestResponse:
    """Response for manifest aspect."""
    active_count: int
    max_agents: int
    agents: list[dict[str, Any]]
    at_capacity: bool


@dataclass
class SwarmSpawnRequest:
    """Request to spawn an agent."""
    task: str
    role: str | None = None  # "researcher", "planner", "implementer", "reviewer"


@dataclass
class SwarmSpawnResponse:
    """Response from spawn."""
    success: bool
    agent_id: str | None
    role: str | None
    reasons: list[str]


@dataclass
class SwarmListResponse:
    """Response from list."""
    agents: list[dict[str, Any]]
    count: int


@dataclass
class SwarmDelegateRequest:
    """Request to delegate task."""
    from_agent: str
    to_agent: str
    task: dict[str, Any]


@dataclass
class SwarmDelegateResponse:
    """Response from delegate."""
    success: bool
    delegation_id: str
    from_agent: str
    to_agent: str


@dataclass
class SwarmHandoffRequest:
    """Request to hand off context."""
    from_agent: str
    to_agent: str
    context: dict[str, Any]
    conversation: list[dict[str, Any]] | None = None


@dataclass
class SwarmHandoffResponse:
    """Response from handoff."""
    success: bool
    handoff_id: str
    from_despawned: bool


@dataclass
class SwarmDespawnRequest:
    """Request to despawn an agent."""
    agent_id: str


@dataclass
class SwarmDespawnResponse:
    """Response from despawn."""
    success: bool
    agent_id: str


@dataclass
class SwarmRolesResponse:
    """Response from roles."""
    roles: list[dict[str, Any]]
    count: int


# =============================================================================
# Affordances
# =============================================================================


SWARM_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "spawn",
    "list",
    "delegate",
    "handoff",
    "despawn",
    "roles",
)


# =============================================================================
# SwarmNode
# =============================================================================


@node(
    "self.conductor.swarm",
    description="Agent swarm coordination - multi-agent collaboration (Phase 6)",
    singleton=True,
    contracts={
        # Perception
        "manifest": Response(SwarmManifestResponse),
        "list": Response(SwarmListResponse),
        "roles": Response(SwarmRolesResponse),
        # Mutations
        "spawn": Contract(SwarmSpawnRequest, SwarmSpawnResponse),
        "delegate": Contract(SwarmDelegateRequest, SwarmDelegateResponse),
        "handoff": Contract(SwarmHandoffRequest, SwarmHandoffResponse),
        "despawn": Contract(SwarmDespawnRequest, SwarmDespawnResponse),
    },
)
@dataclass
class SwarmNode(BaseLogosNode):
    """
    self.conductor.swarm - Agent swarm coordination interface.

    Enables multi-agent collaboration:
    - Spawn agents with roles (Behavior x Trust composition)
    - Delegate tasks between agents
    - Hand off context with conversation history
    - Manage swarm lifecycle

    Roles are NOT a new enum - they compose existing primitives:
    - CursorBehavior: EXPLORER, FOLLOWER, ASSISTANT, AUTONOMOUS
    - TrustLevel: L0 (READ_ONLY) to L3 (AUTONOMOUS)

    Example:
        # Spawn a researcher
        kg self.conductor.swarm.spawn[task="Research authentication patterns"]

        # List active agents
        kg self.conductor.swarm.list

        # Delegate to another agent
        kg self.conductor.swarm.delegate[from_agent="coord-1", to_agent="impl-2", ...]
    """

    _handle: str = "self.conductor.swarm"
    _spawner: SwarmSpawner = field(default_factory=SwarmSpawner)
    _channels: dict[str, A2AChannel] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Swarm affordances available to all archetypes."""
        return SWARM_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View swarm status and active agents."""
        agents = self._spawner.list_agents()
        agent_data = [cursor.to_dict() for cursor in agents]

        content_lines = [
            "Swarm: Agent Coordination",
            f"Active agents: {self._spawner.active_count}/{self._spawner.max_agents}",
            f"At capacity: {self._spawner.at_capacity}",
            "",
            "Canonical Roles (Behavior x Trust):",
            "  - Researcher: EXPLORER x L0 (read-only exploration)",
            "  - Planner: ASSISTANT x L2 (suggests, requires confirmation)",
            "  - Implementer: AUTONOMOUS x L3 (full autonomy)",
            "  - Reviewer: FOLLOWER x L1 (bounded critique)",
            "  - Coordinator: AUTONOMOUS x L3 (cross-jewel invoke)",
            "",
        ]

        if agents:
            content_lines.append("Active Agents:")
            for cursor in agents:
                role_info = cursor.metadata.get("role", {})
                content_lines.append(
                    f"  [{cursor.agent_id}] {cursor.display_name} "
                    f"({role_info.get('emoji', '?')}) - {cursor.activity}"
                )
        else:
            content_lines.append("No active agents. Use spawn to create one.")

        return BasicRendering(
            summary=f"Swarm: {self._spawner.active_count} agents",
            content="\n".join(content_lines),
            metadata={
                "affordances": list(SWARM_AFFORDANCES),
                "active_count": self._spawner.active_count,
                "max_agents": self._spawner.max_agents,
                "at_capacity": self._spawner.at_capacity,
                "agents": agent_data,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle swarm-specific aspects."""
        match aspect:
            case "spawn":
                return await self._spawn_agent(observer, **kwargs)
            case "list":
                return await self._list_agents(observer, **kwargs)
            case "delegate":
                return await self._delegate_task(observer, **kwargs)
            case "handoff":
                return await self._handoff_context(observer, **kwargs)
            case "despawn":
                return await self._despawn_agent(observer, **kwargs)
            case "roles":
                return await self._list_roles(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("swarm_agent")],
        help="Spawn an agent with a role",
        examples=[
            'self.conductor.swarm.spawn[task="Research the codebase"]',
            'self.conductor.swarm.spawn[task="Implement feature", role="implementer"]',
        ],
    )
    async def _spawn_agent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Spawn a swarm agent.

        Signal aggregation determines role if not specified:
        - Research keywords -> RESEARCHER (EXPLORER x L0)
        - Planning keywords -> PLANNER (ASSISTANT x L2)
        - Implementation keywords -> IMPLEMENTER (AUTONOMOUS x L3)
        - Review keywords -> REVIEWER (FOLLOWER x L1)

        Args:
            task: What the agent should work on
            role: Optional role hint ("researcher", "planner", etc.)

        Returns:
            agent_id, role name, spawn reasons
        """
        task = kwargs.get("task", "")
        role_hint = kwargs.get("role")

        if not task:
            return {
                "success": False,
                "agent_id": None,
                "role": None,
                "reasons": ["task is required"],
            }

        # Generate agent ID
        agent_id = f"swarm-{uuid.uuid4().hex[:8]}"

        # Spawn with optional role hint
        cursor = await self._spawner.spawn(
            agent_id=agent_id,
            task=task,
            context={"role_hint": role_hint} if role_hint else None,
        )

        if cursor is None:
            return {
                "success": False,
                "agent_id": None,
                "role": None,
                "reasons": ["Spawn not allowed (capacity or signal threshold)"],
            }

        # Create A2A channel for this agent
        channel = A2AChannel(agent_id)
        channel.start_subscription()
        self._channels[agent_id] = channel
        get_a2a_registry().register(channel)

        role_info = cursor.metadata.get("role", {})
        return {
            "success": True,
            "agent_id": agent_id,
            "role": role_info.get("name"),
            "reasons": [f"Spawned as {role_info.get('name', 'agent')}"],
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("swarm_state")],
        help="List active swarm agents",
        examples=["self.conductor.swarm.list"],
    )
    async def _list_agents(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List active agents in the swarm.

        Returns agent cursors with role and state information.
        """
        agents = self._spawner.list_agents()
        return {
            "agents": [cursor.to_dict() for cursor in agents],
            "count": len(agents),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("a2a_bus")],
        help="Delegate task to another agent",
        examples=['self.conductor.swarm.delegate[from_agent="coord", to_agent="impl", task={...}]'],
    )
    async def _delegate_task(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Delegate task via A2A protocol.

        Sends a REQUEST message from one agent to another.
        The delegating agent remains coordinator.

        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            task: Task payload (dict)

        Returns:
            delegation_id for tracking
        """
        from_agent = kwargs.get("from_agent", "")
        to_agent = kwargs.get("to_agent", "")
        task = kwargs.get("task", {})

        if not from_agent or not to_agent:
            return {
                "success": False,
                "delegation_id": "",
                "from_agent": from_agent,
                "to_agent": to_agent,
            }

        # Get or create channel for from_agent
        channel = self._channels.get(from_agent)
        if channel is None:
            channel = A2AChannel(from_agent)
            self._channels[from_agent] = channel

        # Create and send delegation message
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=A2AMessageType.REQUEST,
            payload={"action": "execute", "task": task},
        )

        await channel.send(message)

        return {
            "success": True,
            "delegation_id": message.correlation_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("a2a_bus"), Effect.WRITES("swarm_agent")],
        help="Hand off context and responsibility to another agent",
        examples=['self.conductor.swarm.handoff[from_agent="a", to_agent="b", context={...}]'],
    )
    async def _handoff_context(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Hand off work to another agent.

        The receiving agent gets full context and responsibility.
        The handing-off agent is despawned after handoff.

        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            context: Context payload (dict)
            conversation: Optional conversation history

        Returns:
            handoff_id, whether from_agent was despawned
        """
        from_agent = kwargs.get("from_agent", "")
        to_agent = kwargs.get("to_agent", "")
        context = kwargs.get("context", {})
        conversation = kwargs.get("conversation")

        if not from_agent or not to_agent:
            return {
                "success": False,
                "handoff_id": "",
                "from_despawned": False,
            }

        # Get or create channel
        channel = self._channels.get(from_agent)
        if channel is None:
            channel = A2AChannel(from_agent)

        # Send handoff message
        await channel.handoff(to_agent, context, conversation)

        # Despawn the handing-off agent
        despawned = await self._spawner.despawn(from_agent)

        # Cleanup channel
        if from_agent in self._channels:
            self._channels[from_agent].stop_subscription()
            del self._channels[from_agent]
            get_a2a_registry().unregister(from_agent)

        return {
            "success": True,
            "handoff_id": f"{from_agent}->{to_agent}",
            "from_despawned": despawned,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("swarm_agent")],
        help="Remove an agent from the swarm",
        examples=['self.conductor.swarm.despawn[agent_id="swarm-abc123"]'],
    )
    async def _despawn_agent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Despawn an agent.

        Removes from swarm and cleans up A2A channel.

        Args:
            agent_id: Agent to despawn

        Returns:
            success status
        """
        agent_id = kwargs.get("agent_id", "")

        if not agent_id:
            return {"success": False, "agent_id": ""}

        # Despawn from spawner
        success = await self._spawner.despawn(agent_id)

        # Cleanup channel
        if agent_id in self._channels:
            self._channels[agent_id].stop_subscription()
            del self._channels[agent_id]
            get_a2a_registry().unregister(agent_id)

        return {"success": success, "agent_id": agent_id}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("role_registry")],
        help="List available canonical roles",
        examples=["self.conductor.swarm.roles"],
    )
    async def _list_roles(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List canonical roles.

        Shows the standard role compositions (Behavior x Trust).
        Any combination is valid - these are just convenience defaults.
        """
        canonical_roles = [
            RESEARCHER.to_dict(),
            PLANNER.to_dict(),
            IMPLEMENTER.to_dict(),
            REVIEWER.to_dict(),
            COORDINATOR.to_dict(),
        ]

        return {
            "roles": canonical_roles,
            "count": len(canonical_roles),
        }


# =============================================================================
# Factory
# =============================================================================


def create_swarm_node(spawner: SwarmSpawner | None = None) -> SwarmNode:
    """
    Create a SwarmNode instance.

    Args:
        spawner: Optional SwarmSpawner (uses default if not provided)

    Returns:
        Configured SwarmNode
    """
    node = SwarmNode()
    if spawner is not None:
        node._spawner = spawner
    return node


__all__ = [
    # Node
    "SwarmNode",
    "create_swarm_node",
    # Affordances
    "SWARM_AFFORDANCES",
    # Contracts
    "SwarmManifestResponse",
    "SwarmSpawnRequest",
    "SwarmSpawnResponse",
    "SwarmListResponse",
    "SwarmDelegateRequest",
    "SwarmDelegateResponse",
    "SwarmHandoffRequest",
    "SwarmHandoffResponse",
    "SwarmDespawnRequest",
    "SwarmDespawnResponse",
    "SwarmRolesResponse",
]
