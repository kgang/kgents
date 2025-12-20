"""
SwarmRole: Role = CursorBehavior x TrustLevel

CLI v7 Phase 6: Agent Swarms

A swarm role is the categorical product of personality (behavior)
and capability (trust). This is NOT a new taxonomy--it's composition
of existing primitives.

The insight: We don't need a new AgentRole enum. The role IS the
composition of behavior (how you act) and trust (what you can do).

Constitution Alignment:
- 5 (Composable): "Agents are morphisms in a category; composition is primary."
- 6 (Heterarchical): "Agents exist in flux, not fixed hierarchy."

Industry Innovation:
- CrewAI role-based orchestration (Researcher, Planner, Implementer, Reviewer)
- Microsoft A2A (Agent-to-Agent) protocol

Usage:
    # Canonical roles
    from services.conductor.swarm import RESEARCHER, PLANNER, IMPLEMENTER

    # Or compose your own
    custom = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.BOUNDED)

    # Check capabilities
    if role.can_execute("edit"):
        ...
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, FrozenSet

from .behaviors import CursorBehavior
from .presence import AgentCursor, CursorState, get_presence_channel

if TYPE_CHECKING:
    from services.witness.polynomial import TrustLevel


logger = logging.getLogger(__name__)


# =============================================================================
# TrustLevel Import (deferred to avoid circular imports)
# =============================================================================


def _get_trust_level_class() -> type:
    """Lazy import of TrustLevel to avoid circular dependency."""
    from services.witness.polynomial import TrustLevel as TL
    return TL


def _get_trust_levels() -> dict[str, Any]:
    """Get trust level enum values."""
    TL = _get_trust_level_class()
    return {
        "READ_ONLY": TL.READ_ONLY,
        "BOUNDED": TL.BOUNDED,
        "SUGGESTION": TL.SUGGESTION,
        "AUTONOMOUS": TL.AUTONOMOUS,
    }


# =============================================================================
# SwarmRole: Behavior x Trust Composition
# =============================================================================


@dataclass(frozen=True)
class SwarmRole:
    """
    Role = Behavior x Trust

    This is the categorical product, not a new enum.
    Roles emerge from composition of existing primitives.

    The role determines:
    - HOW the agent behaves (CursorBehavior: FOLLOWER, EXPLORER, etc.)
    - WHAT the agent can do (TrustLevel: L0-L3 capabilities)

    Example:
        RESEARCHER = SwarmRole(CursorBehavior.EXPLORER, TrustLevel.READ_ONLY)
        - Behavior: Curious wanderer, independent discovery
        - Trust: Can only read, not modify

    Pattern: Composition over creation (Constitution S5)
    """

    behavior: CursorBehavior
    trust_level_name: str  # Store as string to avoid import issues

    @property
    def trust(self) -> Any:
        """Get the actual TrustLevel enum value."""
        levels = _get_trust_levels()
        return levels.get(self.trust_level_name)

    @property
    def name(self) -> str:
        """
        Human-readable role name.

        Canonical mappings for common combinations.
        Non-canonical combos get descriptive names.
        """
        CANONICAL = {
            (CursorBehavior.EXPLORER, "READ_ONLY"): "Researcher",
            (CursorBehavior.ASSISTANT, "SUGGESTION"): "Planner",
            (CursorBehavior.AUTONOMOUS, "AUTONOMOUS"): "Implementer",
            (CursorBehavior.FOLLOWER, "BOUNDED"): "Reviewer",
            (CursorBehavior.AUTONOMOUS, "BOUNDED"): "Coordinator",
        }
        canonical_name = CANONICAL.get((self.behavior, self.trust_level_name))
        if canonical_name:
            return canonical_name

        # Non-canonical: descriptive name
        return f"{self.behavior.name}@{self.trust_level_name}"

    @property
    def emoji(self) -> str:
        """Combined emoji showing behavior + trust."""
        trust_emoji = {
            "READ_ONLY": "L0",
            "BOUNDED": "L1",
            "SUGGESTION": "L2",
            "AUTONOMOUS": "L3",
        }
        return f"{self.behavior.emoji}{trust_emoji.get(self.trust_level_name, '??')}"

    @property
    def capabilities(self) -> FrozenSet[str]:
        """
        Derived from trust level, NOT stored.

        Pattern: Trust determines WHAT you can do.
        Behavior determines HOW you do it.

        L0 (READ_ONLY): glob, grep, read, web_search
        L1 (BOUNDED): + analyze, critique
        L2 (SUGGESTION): + think, suggest
        L3 (AUTONOMOUS): + edit, write, bash, invoke
        """
        TRUST_CAPS = {
            "READ_ONLY": frozenset({"glob", "grep", "read", "web_search"}),
            "BOUNDED": frozenset({"glob", "grep", "read", "web_search", "analyze", "critique"}),
            "SUGGESTION": frozenset({"glob", "grep", "read", "web_search", "think", "suggest"}),
            "AUTONOMOUS": frozenset({
                "glob", "grep", "read", "web_search",
                "edit", "write", "bash", "invoke"
            }),
        }
        return TRUST_CAPS.get(self.trust_level_name, frozenset())

    @property
    def description(self) -> str:
        """Human-readable description."""
        return f"{self.behavior.description} (Trust: {self.trust_level_name})"

    def can_execute(self, operation: str) -> bool:
        """Check if role can execute an operation."""
        return operation in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/persistence."""
        return {
            "name": self.name,
            "emoji": self.emoji,
            "behavior": self.behavior.name,
            "trust_level": self.trust_level_name,
            "capabilities": sorted(self.capabilities),
        }


# =============================================================================
# Canonical Roles (Convenience)
# =============================================================================


# These are the most common role compositions.
# Any behavior x trust combination is valid--these are just defaults.

RESEARCHER = SwarmRole(CursorBehavior.EXPLORER, "READ_ONLY")
"""Read-only exploration, information gathering. L0 trust."""

PLANNER = SwarmRole(CursorBehavior.ASSISTANT, "SUGGESTION")
"""Architecture design, strategy. L2 trust (requires confirmation)."""

IMPLEMENTER = SwarmRole(CursorBehavior.AUTONOMOUS, "AUTONOMOUS")
"""Code writing, file edits. L3 trust (full autonomy)."""

REVIEWER = SwarmRole(CursorBehavior.FOLLOWER, "BOUNDED")
"""Quality assurance, critique. L1 trust (bounded operations)."""

COORDINATOR = SwarmRole(CursorBehavior.AUTONOMOUS, "AUTONOMOUS")
"""Orchestration, cross-jewel invocation. L3 trust."""


# =============================================================================
# SpawnSignal: Signal Aggregation for Agent Selection
# =============================================================================


@dataclass
class SpawnSignal:
    """
    A signal contributing to agent selection.

    Pattern #4: Signal Aggregation for Decisions
    Multiple signals contribute to agent selection:
    - Task type -> behavior selection
    - Complexity -> trust level
    - Capacity -> spawn allowance
    """

    name: str
    weight: float  # -1.0 to 1.0 (negative = blocker)
    reason: str


@dataclass
class SpawnDecision:
    """Result of spawn signal aggregation."""

    role: SwarmRole
    confidence: float  # 0.0-1.0
    reasons: list[str]
    spawn_allowed: bool


# =============================================================================
# SwarmSpawner: Creates and Manages Swarm Agents
# =============================================================================


@dataclass
class SwarmSpawner:
    """
    Spawns agents using signal aggregation (Pattern #4).

    The spawner:
    1. Evaluates task type -> suggests role
    2. Aggregates signals -> confidence score
    3. Spawns agent with presence cursor if allowed
    4. Manages active agent lifecycle

    Integrations:
    - PresenceChannel: Spawned agents get visible cursors
    - A2AChannel: Spawned agents can communicate (see a2a.py)
    """

    max_agents: int = 5
    _active_agents: dict[str, AgentCursor] = field(default_factory=dict)

    def evaluate_role(self, task: str, context: dict[str, Any] | None = None) -> SpawnDecision:
        """
        Evaluate best role for task using signal aggregation.

        Pattern #4: Signal Aggregation for Decisions

        Signals considered:
        - Task keywords -> behavior/trust
        - Current capacity -> spawn permission
        - Context hints -> role override
        """
        context = context or {}
        signals: list[SpawnSignal] = []

        # Default role
        behavior = CursorBehavior.ASSISTANT
        trust_level = "SUGGESTION"

        # Check for role hint in context
        role_hint = context.get("role_hint", "").lower()
        if role_hint:
            if role_hint == "researcher":
                behavior = CursorBehavior.EXPLORER
                trust_level = "READ_ONLY"
                signals.append(SpawnSignal("role_hint", 0.9, f"Role hint: {role_hint}"))
            elif role_hint == "planner":
                behavior = CursorBehavior.ASSISTANT
                trust_level = "SUGGESTION"
                signals.append(SpawnSignal("role_hint", 0.9, f"Role hint: {role_hint}"))
            elif role_hint == "implementer":
                behavior = CursorBehavior.AUTONOMOUS
                trust_level = "AUTONOMOUS"
                signals.append(SpawnSignal("role_hint", 0.9, f"Role hint: {role_hint}"))
            elif role_hint == "reviewer":
                behavior = CursorBehavior.FOLLOWER
                trust_level = "BOUNDED"
                signals.append(SpawnSignal("role_hint", 0.9, f"Role hint: {role_hint}"))

        # Task keyword signals (if no role hint)
        if not role_hint:
            task_lower = task.lower()

            if any(kw in task_lower for kw in ["search", "find", "explore", "research", "look"]):
                signals.append(SpawnSignal(
                    "research_keywords",
                    0.8,
                    "Task involves exploration/research",
                ))
                behavior = CursorBehavior.EXPLORER
                trust_level = "READ_ONLY"

            elif any(kw in task_lower for kw in ["plan", "design", "architect", "strategy"]):
                signals.append(SpawnSignal(
                    "planning_keywords",
                    0.8,
                    "Task involves planning/design",
                ))
                behavior = CursorBehavior.ASSISTANT
                trust_level = "SUGGESTION"

            elif any(kw in task_lower for kw in ["implement", "write", "create", "fix", "build"]):
                signals.append(SpawnSignal(
                    "implementation_keywords",
                    0.8,
                    "Task involves implementation",
                ))
                behavior = CursorBehavior.AUTONOMOUS
                trust_level = "AUTONOMOUS"

            elif any(kw in task_lower for kw in ["review", "check", "verify", "test", "validate"]):
                signals.append(SpawnSignal(
                    "review_keywords",
                    0.8,
                    "Task involves review/verification",
                ))
                behavior = CursorBehavior.FOLLOWER
                trust_level = "BOUNDED"

            else:
                # Default: assistant with suggestion trust
                signals.append(SpawnSignal(
                    "general_task",
                    0.5,
                    "General task, defaulting to Planner role",
                ))

        # Capacity signal
        if len(self._active_agents) >= self.max_agents:
            signals.append(SpawnSignal(
                "capacity_exceeded",
                -1.0,  # Blocker
                f"At capacity ({len(self._active_agents)}/{self.max_agents} agents)",
            ))

        # Aggregate confidence
        confidence = sum(s.weight for s in signals)
        positive_reasons = [s.reason for s in signals if s.weight > 0]
        spawn_allowed = confidence > 0 and len(self._active_agents) < self.max_agents

        return SpawnDecision(
            role=SwarmRole(behavior, trust_level),
            confidence=min(1.0, max(0.0, confidence)),
            reasons=positive_reasons,
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

        Creates an AgentCursor with the role's behavior and
        registers it with the PresenceChannel for visibility.

        Returns the spawned AgentCursor or None if spawn not allowed.
        """
        decision = self.evaluate_role(task, context)

        if not decision.spawn_allowed:
            logger.warning(
                f"Spawn denied for {agent_id}: {decision.reasons}"
            )
            return None

        # Create cursor with role's behavior
        cursor = AgentCursor(
            agent_id=agent_id,
            display_name=f"{decision.role.name}",
            state=CursorState.WAITING,
            activity=f"Starting: {task[:50]}...",
            behavior=decision.role.behavior,
            metadata={
                "role": decision.role.to_dict(),
                "task": task,
                "spawn_confidence": decision.confidence,
            },
        )

        # Register with presence channel
        try:
            channel = get_presence_channel()
            await channel.join(cursor)
        except Exception as e:
            logger.warning(f"Could not register cursor with presence: {e}")

        self._active_agents[agent_id] = cursor
        logger.info(
            f"Spawned {decision.role.name} agent: {agent_id} "
            f"(confidence: {decision.confidence:.2f})"
        )

        return cursor

    async def despawn(self, agent_id: str) -> bool:
        """
        Remove an agent from the swarm.

        Unregisters from PresenceChannel and cleans up.
        Returns True if agent was present and removed.
        """
        cursor = self._active_agents.pop(agent_id, None)
        if cursor is None:
            return False

        # Unregister from presence channel
        try:
            channel = get_presence_channel()
            await channel.leave(agent_id)
        except Exception as e:
            logger.warning(f"Could not unregister cursor from presence: {e}")

        logger.info(f"Despawned agent: {agent_id}")
        return True

    def get_agent(self, agent_id: str) -> AgentCursor | None:
        """Get an active agent by ID."""
        return self._active_agents.get(agent_id)

    def list_agents(self) -> list[AgentCursor]:
        """List all active agents."""
        return list(self._active_agents.values())

    @property
    def active_count(self) -> int:
        """Number of active agents."""
        return len(self._active_agents)

    @property
    def at_capacity(self) -> bool:
        """Whether the swarm is at max capacity."""
        return len(self._active_agents) >= self.max_agents


# =============================================================================
# Factory Function
# =============================================================================


def create_swarm_role(
    behavior: CursorBehavior | str,
    trust: str,
) -> SwarmRole:
    """
    Factory for creating SwarmRole with string inputs.

    Convenience for CLI/API usage where enum values aren't available.

    Args:
        behavior: CursorBehavior enum or string name
        trust: Trust level name (READ_ONLY, BOUNDED, SUGGESTION, AUTONOMOUS)

    Returns:
        SwarmRole composition
    """
    if isinstance(behavior, str):
        behavior = CursorBehavior[behavior.upper()]

    return SwarmRole(behavior, trust.upper())


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Core type
    "SwarmRole",
    # Canonical roles
    "RESEARCHER",
    "PLANNER",
    "IMPLEMENTER",
    "REVIEWER",
    "COORDINATOR",
    # Signal aggregation
    "SpawnSignal",
    "SpawnDecision",
    # Spawner
    "SwarmSpawner",
    # Factory
    "create_swarm_role",
]
