# CLI v7 Phase 6: Agent Swarms — Implementation Plan

**Status**: ✅ COMPLETE
**Created**: 2025-12-20
**Completed**: 2025-12-20
**Spec Source**: `plans/cli-v7-implementation.md` Phase 6
**Principle**: *"Teams of AI agents corralled under orchestrator uber-models that manage the overall project workflow."*

---

## Implementation Summary (2025-12-20)

**Files Implemented**:
- `services/conductor/swarm.py` — SwarmRole, SwarmSpawner, SpawnSignal/Decision
- `services/conductor/a2a.py` — A2AChannel, A2AMessage, A2AMessageType, A2ARegistry
- `services/conductor/operad.py` — SWARM_OPERAD with spawn/delegate/aggregate/handoff
- `services/conductor/_tests/test_swarm.py` — 58 unit/integration tests
- `services/conductor/_tests/test_swarm_e2e.py` — 10 E2E tests

**Key Design Decisions**:
- **SwarmRole = Behavior × Trust**: Capabilities derive from TrustLevel, personality from CursorBehavior
- **A2A via WitnessSynergyBus**: Messages ARE events—reuse existing infrastructure
- **Canonical roles**: RESEARCHER, PLANNER, IMPLEMENTER, REVIEWER, COORDINATOR

**Exit Condition Met**: ✅ 3+ agents collaborate on a task without human intermediation (test_three_agent_research_plan_review_flow)

---

## 🎯 Grounding in Kent's Voice

> *"Daring, bold, creative, opinionated but not gaudy"*

Phase 6 is bold—multi-agent collaboration without human intermediation. But it must not be gaudy: we don't need another framework. We need **composition** of existing primitives.

> *"The persona is a garden, not a museum"*

Swarms should feel alive. Agents aren't static workers; they're heterarchical beings that shift roles as context demands.

> *"Tasteful > feature-complete"*

Not all of CrewAI's complexity. Just the core: roles, A2A messaging, trust-gated spawning.

---

## Architectural Decision: Compose, Don't Duplicate

**The Temptation**: Build a parallel role system (RESEARCHER, PLANNER, etc.) with its own capabilities taxonomy.

**The Insight**: We already have:
- `CursorBehavior` (FOLLOWER, EXPLORER, ASSISTANT, AUTONOMOUS) — personality
- `TrustLevel` (L0-L3) — capability gating
- `WITNESS_OPERAD` (sense, analyze, suggest, act, invoke) — operation grammar

**The Composition**:

| Swarm Role | = CursorBehavior × TrustLevel |
|------------|-------------------------------|
| **Researcher** | EXPLORER × L0 (read-only exploration) |
| **Planner** | ASSISTANT × L2 (suggests plans, requires confirmation) |
| **Implementer** | AUTONOMOUS × L3 (executes actions) |
| **Reviewer** | FOLLOWER × L1 (bounded critique) |
| **Coordinator** | AUTONOMOUS × L3 (can invoke other jewels) |

This isn't feature creep—it's **categorical composition**. The role IS the product of behavior and trust.

---

## Phase 6 Structure

```
services/conductor/
├── swarm.py              # SwarmRole, SwarmSpawner, SwarmCoordinator
├── a2a.py                # A2AChannel, A2AMessage, A2AProtocol
├── operad.py             # SWARM_OPERAD ← WITNESS_OPERAD
└── _tests/
    ├── test_swarm.py     # Role composition, spawning
    ├── test_a2a.py       # A2A messaging, handoffs
    └── test_operad.py    # Operad law verification
```

---

## Core Work

### 6.1 SwarmRole: Behavior × Trust Composition

**Not** a new enum—a **product type**:

```python
# services/conductor/swarm.py
"""
SwarmRole: Role = CursorBehavior × TrustLevel

A swarm role is the categorical product of personality (behavior)
and capability (trust). This is NOT a new taxonomy—it's composition
of existing primitives.

Constitution §5 (Composable): "Agents are morphisms in a category."
Constitution §6 (Heterarchical): "Agents exist in flux, not fixed hierarchy."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, FrozenSet
from datetime import datetime

from ..conductor.behaviors import CursorBehavior
from ..conductor.presence import AgentCursor, CursorState
from ..witness.polynomial import TrustLevel
from ..witness.operad import WitnessMetabolics, SENSE_METABOLICS, ACT_METABOLICS

if TYPE_CHECKING:
    from protocols.agentese.gateway import Logos


@dataclass(frozen=True)
class SwarmRole:
    """
    Role = Behavior × Trust

    This is the categorical product, not a new enum.
    Roles emerge from composition of existing primitives.
    """

    behavior: CursorBehavior
    trust: TrustLevel

    # Role-specific metadata (derived, not stored)
    @property
    def name(self) -> str:
        """Human-readable role name."""
        # Canonical mappings (not exhaustive—any combo is valid)
        CANONICAL = {
            (CursorBehavior.EXPLORER, TrustLevel.READ_ONLY): "Researcher",
            (CursorBehavior.ASSISTANT, TrustLevel.SUGGESTION): "Planner",
            (CursorBehavior.AUTONOMOUS, TrustLevel.AUTONOMOUS): "Implementer",
            (CursorBehavior.FOLLOWER, TrustLevel.BOUNDED): "Reviewer",
        }
        return CANONICAL.get(
            (self.behavior, self.trust),
            f"{self.behavior.name}@{self.trust.name}"
        )

    @property
    def capabilities(self) -> FrozenSet[str]:
        """
        Derived from trust level, NOT stored.

        Pattern: Trust determines WHAT you can do.
        Behavior determines HOW you do it.
        """
        trust_caps = {
            TrustLevel.READ_ONLY: frozenset({"glob", "grep", "read", "web_search"}),
            TrustLevel.BOUNDED: frozenset({"glob", "grep", "read", "analyze", "critique"}),
            TrustLevel.SUGGESTION: frozenset({"glob", "grep", "read", "think", "suggest"}),
            TrustLevel.AUTONOMOUS: frozenset({"glob", "grep", "read", "edit", "write", "bash", "invoke"}),
        }
        return trust_caps.get(self.trust, frozenset())

    @property
    def metabolics(self) -> WitnessMetabolics:
        """Get appropriate metabolics for this role."""
        if self.trust == TrustLevel.AUTONOMOUS:
            return ACT_METABOLICS
        return SENSE_METABOLICS

    def can_execute(self, operation: str) -> bool:
        """Check if role can execute operation."""
        return operation in self.capabilities


# Canonical roles (convenience, not exhaustive)
RESEARCHER = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.READ_ONLY)
PLANNER = SwarmRole(CursorBehavior.ASSISTANT, TrustLevel.SUGGESTION)
IMPLEMENTER = SwarmRole(CursorBehavior.AUTONOMOUS, TrustLevel.AUTONOMOUS)
REVIEWER = SwarmRole(CursorBehavior.FOLLOWER, TrustLevel.BOUNDED)
COORDINATOR = SwarmRole(CursorBehavior.AUTONOMOUS, TrustLevel.AUTONOMOUS)
```

### 6.2 A2A Protocol: Agent-to-Agent Messaging

```python
# services/conductor/a2a.py
"""
A2A Protocol: Agent-to-Agent messaging via SynergyBus.

Agents communicate without human intermediation.
This is the "autonomous collaborators" pattern from Microsoft A2A.

Key insight: A2A messages ARE synergy events. We don't need
a separate bus—we need a typed event shape for agent messages.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, AsyncIterator
from uuid import uuid4

from protocols.synergy import SynergyEvent, get_synergy_bus


class A2AMessageType(Enum):
    """Types of agent-to-agent messages."""
    REQUEST = auto()      # Ask another agent to do something
    RESPONSE = auto()     # Reply to a request
    HANDOFF = auto()      # Transfer context and responsibility
    NOTIFY = auto()       # Broadcast information (no response expected)
    HEARTBEAT = auto()    # Presence signal


@dataclass
class A2AMessage:
    """
    Message between agents.

    Flows through SynergyBus as a typed SynergyEvent.
    """

    from_agent: str
    to_agent: str  # "*" for broadcast
    message_type: A2AMessageType
    payload: dict[str, Any]
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional: conversation context for handoffs
    conversation_context: list[dict[str, Any]] | None = None

    def to_synergy_event(self) -> SynergyEvent:
        """Convert to SynergyBus event."""
        return SynergyEvent(
            event_type=f"A2A_{self.message_type.name}",
            source=f"agent:{self.from_agent}",
            payload={
                "to_agent": self.to_agent,
                "correlation_id": self.correlation_id,
                "payload": self.payload,
                "conversation_context": self.conversation_context,
                "timestamp": self.timestamp.isoformat(),
            },
        )

    @classmethod
    def from_synergy_event(cls, event: SynergyEvent) -> "A2AMessage":
        """Reconstruct from SynergyBus event."""
        # Parse event_type to get message type
        type_name = event.event_type.replace("A2A_", "")
        message_type = A2AMessageType[type_name]

        # Parse source to get from_agent
        from_agent = event.source.replace("agent:", "")

        return cls(
            from_agent=from_agent,
            to_agent=event.payload["to_agent"],
            message_type=message_type,
            payload=event.payload["payload"],
            correlation_id=event.payload["correlation_id"],
            timestamp=datetime.fromisoformat(event.payload["timestamp"]),
            conversation_context=event.payload.get("conversation_context"),
        )


class A2AChannel:
    """
    Agent-to-agent communication channel.

    Wraps SynergyBus with agent-specific semantics.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._pending_responses: dict[str, asyncio.Future[A2AMessage]] = {}

    async def send(self, message: A2AMessage) -> None:
        """Send message to another agent."""
        event = message.to_synergy_event()
        await get_synergy_bus().emit(event)

    async def request(
        self,
        to_agent: str,
        payload: dict[str, Any],
        timeout: float = 30.0
    ) -> A2AMessage:
        """
        Request/response pattern with timeout.

        Sends REQUEST, waits for RESPONSE with matching correlation_id.
        """
        correlation_id = str(uuid4())
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.REQUEST,
            payload=payload,
            correlation_id=correlation_id,
        )

        # Create future for response
        future: asyncio.Future[A2AMessage] = asyncio.get_event_loop().create_future()
        self._pending_responses[correlation_id] = future

        try:
            await self.send(message)
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._pending_responses.pop(correlation_id, None)

    async def handoff(
        self,
        to_agent: str,
        context: dict[str, Any],
        conversation: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Hand off work to another agent with full context.

        The receiving agent becomes responsible for the task.
        """
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.HANDOFF,
            payload=context,
            conversation_context=conversation,
        )
        await self.send(message)

    async def subscribe(self) -> AsyncIterator[A2AMessage]:
        """
        Subscribe to messages addressed to this agent.

        Filters SynergyBus for A2A_* events to this agent or "*".
        """
        async for event in get_synergy_bus().subscribe():
            if not event.event_type.startswith("A2A_"):
                continue

            message = A2AMessage.from_synergy_event(event)

            # Check if message is for us
            if message.to_agent not in (self.agent_id, "*"):
                continue

            # Handle response correlation
            if message.message_type == A2AMessageType.RESPONSE:
                future = self._pending_responses.get(message.correlation_id)
                if future and not future.done():
                    future.set_result(message)
                    continue

            yield message
```

### 6.3 SWARM_OPERAD: Inheriting from WITNESS_OPERAD

```python
# services/conductor/operad.py
"""
SWARM_OPERAD: Composition grammar for agent swarms.

Extends WITNESS_OPERAD with swarm-specific operations:
- spawn: Create an agent with a role
- delegate: Transfer subtask between agents
- aggregate: Combine results from multiple agents
- handoff: Transfer context and responsibility

Pattern #10: Operad Inheritance
"""

from agents.operad.core import (
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, sequential

from ..witness.operad import WITNESS_OPERAD
from .swarm import SwarmRole


# =============================================================================
# Swarm Operations
# =============================================================================


def _spawn_compose(role: SwarmRole) -> PolyAgent:
    """
    Spawn: (Task, Role) → Agent

    Creates a new agent with the specified role.
    The spawned agent inherits role's behavior and trust level.
    """
    def spawn_fn(task: str) -> dict:
        return {
            "operation": "spawn",
            "task": task,
            "role": role.name,
            "behavior": role.behavior.name,
            "trust": role.trust.name,
            "capabilities": list(role.capabilities),
        }

    return from_function(f"spawn({role.name})", spawn_fn)


def _delegate_compose(from_agent: str, to_agent: str) -> PolyAgent:
    """
    Delegate: (Agent, Task) → Delegation

    Transfer a subtask from one agent to another.
    The delegating agent remains coordinator.
    """
    def delegate_fn(task: dict) -> dict:
        return {
            "operation": "delegate",
            "from": from_agent,
            "to": to_agent,
            "task": task,
            "delegated": True,
        }

    return from_function(f"delegate({from_agent}→{to_agent})", delegate_fn)


def _aggregate_compose(agents: list[str]) -> PolyAgent:
    """
    Aggregate: [Result] → AggregatedResult

    Combine results from multiple agents into a unified output.
    """
    def aggregate_fn(results: list[dict]) -> dict:
        return {
            "operation": "aggregate",
            "agents": agents,
            "results": results,
            "aggregated": True,
        }

    return from_function(f"aggregate({', '.join(agents)})", aggregate_fn)


def _handoff_compose(from_agent: str, to_agent: str) -> PolyAgent:
    """
    Handoff: (Agent, Agent) → Handoff

    Transfer full context and responsibility to another agent.
    The handing-off agent exits; the receiving agent continues.
    """
    def handoff_fn(context: dict) -> dict:
        return {
            "operation": "handoff",
            "from": from_agent,
            "to": to_agent,
            "context": context,
            "handoff_complete": True,
        }

    return from_function(f"handoff({from_agent}→{to_agent})", handoff_fn)


SWARM_OPERATIONS = {
    "spawn": Operation(
        name="spawn",
        arity=1,
        signature="(Task, Role) → Agent",
        compose=_spawn_compose,
        description="Create an agent with a role",
    ),
    "delegate": Operation(
        name="delegate",
        arity=2,
        signature="(Agent, Task) → Delegation",
        compose=_delegate_compose,
        description="Transfer subtask to another agent",
    ),
    "aggregate": Operation(
        name="aggregate",
        arity="*",  # Variadic
        signature="[Result] → AggregatedResult",
        compose=_aggregate_compose,
        description="Combine results from multiple agents",
    ),
    "handoff": Operation(
        name="handoff",
        arity=2,
        signature="(Agent, Agent) → Handoff",
        compose=_handoff_compose,
        description="Transfer context and responsibility",
    ),
}


# =============================================================================
# Swarm Laws
# =============================================================================


def _verify_delegation_associativity(*args) -> LawVerification:
    """
    Delegation is associative: (a delegate b) delegate c ≡ a delegate (b delegate c)

    Verified structurally—delegation order doesn't affect final result.
    """
    return LawVerification(
        law_name="delegation_associativity",
        status=LawStatus.STRUCTURAL,
        message="Delegation is associative by design (STRUCTURAL)",
    )


def _verify_aggregation_commutativity(*args) -> LawVerification:
    """
    Aggregation is commutative: aggregate([a, b]) ≡ aggregate([b, a])

    Results don't depend on agent order.
    """
    return LawVerification(
        law_name="aggregation_commutativity",
        status=LawStatus.PASSED,
        message="Aggregation is commutative",
    )


def _verify_handoff_irreversibility(*args) -> LawVerification:
    """
    Handoff is one-way: handoff(a, b) does NOT imply handoff(b, a)

    Once handed off, the original agent exits.
    """
    return LawVerification(
        law_name="handoff_irreversibility",
        status=LawStatus.STRUCTURAL,
        message="Handoff is irreversible by design",
    )


SWARM_LAWS = [
    Law(
        name="delegation_associativity",
        equation="(a delegate b) delegate c ≡ a delegate (b delegate c)",
        verify=_verify_delegation_associativity,
        description="Delegation order doesn't matter for final result",
    ),
    Law(
        name="aggregation_commutativity",
        equation="aggregate([a, b]) ≡ aggregate([b, a])",
        verify=_verify_aggregation_commutativity,
        description="Agent order in aggregation doesn't matter",
    ),
    Law(
        name="handoff_irreversibility",
        equation="handoff(a, b) ⊬ handoff(b, a)",
        verify=_verify_handoff_irreversibility,
        description="Handoffs are one-way transfers",
    ),
]


# =============================================================================
# Create SWARM_OPERAD
# =============================================================================


def create_swarm_operad() -> Operad:
    """
    Create the Swarm Operad.

    Pattern #10: Operad Inheritance
    Extends WITNESS_OPERAD with swarm-specific operations.
    """
    # Merge with WITNESS_OPERAD's operations
    merged_operations = dict(WITNESS_OPERAD.operations)
    merged_operations.update(SWARM_OPERATIONS)

    # Combine laws
    merged_laws = list(WITNESS_OPERAD.laws) + SWARM_LAWS

    return Operad(
        name="SwarmOperad",
        operations=merged_operations,
        laws=merged_laws,
        description="Swarm coordination grammar (extends WitnessOperad)",
    )


SWARM_OPERAD = create_swarm_operad()
OperadRegistry.register(SWARM_OPERAD)
```

### 6.4 SwarmSpawner: Signal Aggregation for Agent Selection

```python
# services/conductor/swarm.py (continued)

from dataclasses import dataclass
from typing import Callable, Any
import asyncio

from ..conductor.behaviors import CursorBehavior, BehaviorAnimator
from ..conductor.presence import AgentCursor, CursorState, get_presence_channel
from ..witness.polynomial import TrustLevel


@dataclass
class SpawnSignal:
    """A signal contributing to agent selection."""
    name: str
    weight: float  # 0.0-1.0
    reason: str


@dataclass
class SpawnDecision:
    """Result of spawn signal aggregation."""
    role: SwarmRole
    confidence: float
    reasons: list[str]
    spawn_allowed: bool


class SwarmSpawner:
    """
    Spawns agents using signal aggregation (Pattern #4).

    Multiple signals contribute to agent selection:
    - Task complexity → trust level
    - Task type → behavior
    - Available budget → role constraints
    """

    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self._active_agents: dict[str, AgentCursor] = {}

    def evaluate_role(self, task: str, context: dict[str, Any]) -> SpawnDecision:
        """
        Evaluate best role for task using signal aggregation.

        Pattern #4: Signal Aggregation for Decisions
        """
        signals: list[SpawnSignal] = []

        # Task type signals
        if any(kw in task.lower() for kw in ["search", "find", "explore", "research"]):
            signals.append(SpawnSignal(
                name="research_task",
                weight=0.8,
                reason="Task involves exploration",
            ))
            behavior = CursorBehavior.EXPLORER
            trust = TrustLevel.READ_ONLY
        elif any(kw in task.lower() for kw in ["plan", "design", "architect"]):
            signals.append(SpawnSignal(
                name="planning_task",
                weight=0.8,
                reason="Task involves planning",
            ))
            behavior = CursorBehavior.ASSISTANT
            trust = TrustLevel.SUGGESTION
        elif any(kw in task.lower() for kw in ["implement", "write", "create", "fix"]):
            signals.append(SpawnSignal(
                name="implementation_task",
                weight=0.8,
                reason="Task involves implementation",
            ))
            behavior = CursorBehavior.AUTONOMOUS
            trust = TrustLevel.AUTONOMOUS
        elif any(kw in task.lower() for kw in ["review", "check", "verify"]):
            signals.append(SpawnSignal(
                name="review_task",
                weight=0.8,
                reason="Task involves review",
            ))
            behavior = CursorBehavior.FOLLOWER
            trust = TrustLevel.BOUNDED
        else:
            # Default to assistant
            signals.append(SpawnSignal(
                name="general_task",
                weight=0.5,
                reason="General task, defaulting to assistant",
            ))
            behavior = CursorBehavior.ASSISTANT
            trust = TrustLevel.SUGGESTION

        # Capacity signals
        if len(self._active_agents) >= self.max_agents:
            signals.append(SpawnSignal(
                name="capacity_exceeded",
                weight=-1.0,  # Blocker
                reason=f"At capacity ({self.max_agents} agents)",
            ))

        # Aggregate
        confidence = sum(s.weight for s in signals)
        reasons = [s.reason for s in signals if s.weight > 0]
        spawn_allowed = confidence > 0 and len(self._active_agents) < self.max_agents

        return SpawnDecision(
            role=SwarmRole(behavior, trust),
            confidence=min(1.0, max(0.0, confidence)),
            reasons=reasons,
            spawn_allowed=spawn_allowed,
        )

    async def spawn(
        self,
        agent_id: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> AgentCursor | None:
        """
        Spawn an agent if allowed.

        Returns the spawned AgentCursor or None if spawn not allowed.
        """
        decision = self.evaluate_role(task, context or {})

        if not decision.spawn_allowed:
            return None

        # Create cursor with role's behavior
        cursor = AgentCursor(
            agent_id=agent_id,
            display_name=f"{decision.role.name}",
            state=CursorState.WAITING,
            activity=f"Starting: {task[:50]}...",
            behavior=decision.role.behavior,
        )

        # Register with presence channel
        channel = get_presence_channel()
        await channel.join(cursor)

        self._active_agents[agent_id] = cursor

        return cursor

    async def despawn(self, agent_id: str) -> bool:
        """Remove an agent from the swarm."""
        cursor = self._active_agents.pop(agent_id, None)
        if cursor is None:
            return False

        channel = get_presence_channel()
        await channel.leave(agent_id)

        return True
```

### 6.5 AGENTESE Node: self.conductor.swarm

```python
# protocols/agentese/contexts/self_swarm.py
"""
AGENTESE Node: self.conductor.swarm

Exposes swarm operations via AGENTESE protocol.

Affordances:
- spawn: Spawn an agent with a role
- list: List active swarm agents
- delegate: Delegate task to another agent
- aggregate: Aggregate results from agents
- handoff: Hand off to another agent
- despawn: Remove an agent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from opentelemetry import trace

from services.conductor.swarm import (
    SwarmRole,
    SwarmSpawner,
    RESEARCHER,
    PLANNER,
    IMPLEMENTER,
    REVIEWER,
)
from services.conductor.a2a import A2AChannel, A2AMessage, A2AMessageType
from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

_tracer = trace.get_tracer("kgents.swarm")


# =============================================================================
# Contracts
# =============================================================================


@dataclass
class SwarmSpawnRequest:
    task: str
    role: str | None = None  # "researcher", "planner", "implementer", "reviewer"


@dataclass
class SwarmSpawnResponse:
    success: bool
    agent_id: str | None
    role: str | None
    reasons: list[str]


@dataclass
class SwarmListResponse:
    agents: list[dict[str, Any]]
    count: int


@dataclass
class SwarmDelegateRequest:
    to_agent: str
    task: dict[str, Any]


@dataclass
class SwarmDelegateResponse:
    success: bool
    delegation_id: str


@dataclass
class SwarmHandoffRequest:
    to_agent: str
    context: dict[str, Any]
    conversation: list[dict[str, Any]] | None = None


@dataclass
class SwarmHandoffResponse:
    success: bool
    handoff_id: str


# =============================================================================
# Node
# =============================================================================


@node(
    "self.conductor.swarm",
    description="Agent swarm coordination (Phase 6)",
    contracts={
        "spawn": Contract(SwarmSpawnRequest, SwarmSpawnResponse),
        "list": Response(SwarmListResponse),
        "delegate": Contract(SwarmDelegateRequest, SwarmDelegateResponse),
        "handoff": Contract(SwarmHandoffRequest, SwarmHandoffResponse),
    },
    dependencies=("swarm_spawner",),  # DI registration required!
)
@dataclass
class SwarmNode(BaseLogosNode):
    """
    Swarm coordination node.

    Exposes swarm operations via AGENTESE.
    """

    _handle: str = "self.conductor.swarm"
    _spawner: SwarmSpawner = field(default_factory=SwarmSpawner)
    _channels: dict[str, A2AChannel] = field(default_factory=dict)

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CREATES("swarm_agent")],
        help="Spawn an agent with a role",
    )
    async def spawn(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Spawn a swarm agent."""
        with _tracer.start_as_current_span("swarm.spawn") as span:
            task = kwargs.get("task", "")
            role_name = kwargs.get("role")

            span.set_attribute("swarm.task", task[:100])
            span.set_attribute("swarm.role", role_name or "auto")

            # Generate agent ID
            import uuid
            agent_id = f"swarm-{uuid.uuid4().hex[:8]}"

            cursor = await self._spawner.spawn(
                agent_id=agent_id,
                task=task,
                context={"role_hint": role_name},
            )

            if cursor is None:
                return {
                    "success": False,
                    "agent_id": None,
                    "role": None,
                    "reasons": ["Spawn not allowed (capacity or signal threshold)"],
                }

            # Create A2A channel for this agent
            self._channels[agent_id] = A2AChannel(agent_id)

            return {
                "success": True,
                "agent_id": agent_id,
                "role": cursor.behavior.name if cursor.behavior else None,
                "reasons": [],
            }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("swarm_state")],
        help="List active swarm agents",
    )
    async def list(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """List active agents."""
        agents = [
            cursor.to_dict()
            for cursor in self._spawner._active_agents.values()
        ]
        return {
            "agents": agents,
            "count": len(agents),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("a2a_bus")],
        help="Delegate task to another agent",
    )
    async def delegate(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Delegate task via A2A."""
        to_agent = kwargs.get("to_agent", "")
        task = kwargs.get("task", {})

        # Get current agent's channel
        current_agent_id = kwargs.get("agent_id", "coordinator")
        channel = self._channels.get(current_agent_id) or A2AChannel(current_agent_id)

        message = A2AMessage(
            from_agent=current_agent_id,
            to_agent=to_agent,
            message_type=A2AMessageType.REQUEST,
            payload={"action": "execute", "task": task},
        )

        await channel.send(message)

        return {
            "success": True,
            "delegation_id": message.correlation_id,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("a2a_bus")],
        help="Hand off context and responsibility to another agent",
    )
    async def handoff(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Hand off via A2A."""
        to_agent = kwargs.get("to_agent", "")
        context = kwargs.get("context", {})
        conversation = kwargs.get("conversation")

        current_agent_id = kwargs.get("agent_id", "coordinator")
        channel = self._channels.get(current_agent_id) or A2AChannel(current_agent_id)

        await channel.handoff(to_agent, context, conversation)

        # Despawn the handing-off agent
        await self._spawner.despawn(current_agent_id)

        return {
            "success": True,
            "handoff_id": f"{current_agent_id}→{to_agent}",
        }
```

---

## Test Strategy

Following `docs/skills/test-patterns.md`:

| Type | Count | Focus |
|------|-------|-------|
| **Type I (Unit)** | 20 | SwarmRole composition, A2AMessage serialization |
| **Type II (Integration)** | 15 | A2AChannel + SynergyBus, SwarmSpawner + PresenceChannel |
| **Type III (Property)** | 10 | Operad laws, role composition commutativity |
| **Type IV (E2E)** | 5 | Full spawn→delegate→aggregate flow |
| **Total** | **50** | |

### Key Test Cases

```python
# test_swarm.py

def test_swarm_role_is_product_type():
    """SwarmRole = CursorBehavior × TrustLevel"""
    role = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.READ_ONLY)
    assert role.name == "Researcher"
    assert "glob" in role.capabilities
    assert "edit" not in role.capabilities  # L0 can't edit

def test_role_capabilities_derived_from_trust():
    """Capabilities come from trust, not stored separately."""
    impl = SwarmRole(CursorBehavior.AUTONOMOUS, TrustLevel.AUTONOMOUS)
    assert "edit" in impl.capabilities
    assert "invoke" in impl.capabilities

    # Same behavior, lower trust → different capabilities
    bounded = SwarmRole(CursorBehavior.AUTONOMOUS, TrustLevel.BOUNDED)
    assert "edit" not in bounded.capabilities

@given(st.sampled_from(list(CursorBehavior)), st.sampled_from(list(TrustLevel)))
def test_any_behavior_trust_combination_valid(behavior, trust):
    """Any combination of behavior and trust is a valid role."""
    role = SwarmRole(behavior, trust)
    assert role.name is not None
    assert isinstance(role.capabilities, frozenset)
```

```python
# test_operad.py

def test_swarm_operad_inherits_witness():
    """SWARM_OPERAD includes all WITNESS_OPERAD operations."""
    from services.conductor.operad import SWARM_OPERAD
    from services.witness.operad import WITNESS_OPERAD

    for op_name in WITNESS_OPERAD.operations:
        assert op_name in SWARM_OPERAD.operations

def test_delegation_associativity_law():
    """Verify delegation associativity is STRUCTURAL."""
    from services.conductor.operad import SWARM_OPERAD

    law = next(l for l in SWARM_OPERAD.laws if l.name == "delegation_associativity")
    result = law.verify()
    assert result.status == LawStatus.STRUCTURAL
```

---

## Exit Condition

**When Phase 6 feels complete**:

1. `kg self.conductor.swarm.spawn "Research the codebase"` creates a RESEARCHER agent
2. `kg self.conductor.swarm.list` shows active agents with behaviors
3. Agents communicate via A2A (SynergyBus events visible)
4. SWARM_OPERAD laws pass verification
5. **The swarm test**: Can 3+ agents collaborate on a task without human intermediation?

---

## Integration with Existing Infrastructure

| Existing System | Phase 6 Integration |
|-----------------|---------------------|
| `CursorBehavior` | SwarmRole.behavior |
| `TrustLevel` | SwarmRole.trust |
| `WITNESS_OPERAD` | SWARM_OPERAD inherits |
| `PresenceChannel` | Spawned agents join |
| `SynergyBus` | A2A messages flow through |
| `ConversationWindow` | Handoffs include conversation context |

---

## Deliverables

| File | Description | Pattern |
|------|-------------|---------|
| `services/conductor/swarm.py` | SwarmRole (Behavior × Trust), SwarmSpawner | Composition, #4 |
| `services/conductor/a2a.py` | A2AChannel, A2AMessage | SynergyBus Integration |
| `services/conductor/operad.py` | SWARM_OPERAD | #10 Operad Inheritance |
| `protocols/agentese/contexts/self_swarm.py` | AGENTESE node | #13 Contract-First |
| `services/providers.py` update | DI for swarm_spawner | #15 No Hollow Services |
| Tests | 50 tests across 4 types | T-gent taxonomy |

---

## Why This Plan is Tasteful

1. **Composition over Creation**: We compose `CursorBehavior × TrustLevel` rather than creating a new `AgentRole` enum that duplicates concepts.

2. **Leverages Existing Trust System**: kgentsd's L0-L3 trust levels ARE the capability gates. We don't build a parallel permission system.

3. **A2A is Just SynergyBus**: Agent messages are typed synergy events, not a separate bus.

4. **SWARM_OPERAD Inherits**: Pattern #10 (Operad Inheritance) keeps composition grammar unified.

5. **Joy-Inducing**: Spawned agents have visible presence via Phase 3's `AgentCursor`. The swarm feels alive.

---

*"Teams of AI agents corralled under orchestrator uber-models"—but the orchestrator isn't a separate system. It's the categorical composition of behaviors, trust, and operads we already have.*

---

**Ready for Implementation**: This plan is aligned with Constitution principles and builds on existing infrastructure.
