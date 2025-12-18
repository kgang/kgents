"""
Town Event Definitions: DataEvent subclasses for Agent Town.

Events flow through the three-bus architecture:
1. DataBus: Persistence events (CitizenCreated, ConversationTurn, etc.)
2. SynergyBus: Cross-jewel events (town.gossip → K-gent narrative)
3. EventBus: Fan-out to UI (SSE stream, WebSocket, CLI)

All events are immutable dataclasses for safe concurrent handling.

See: plans/town-rebuild.md Part II (Event Architecture)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, FrozenSet
from uuid import uuid4


class TownEventType(Enum):
    """Types of town events."""

    # Citizen lifecycle
    CITIZEN_CREATED = auto()
    CITIZEN_UPDATED = auto()
    CITIZEN_DEACTIVATED = auto()

    # Conversation
    CONVERSATION_STARTED = auto()
    CONVERSATION_TURN = auto()
    CONVERSATION_ENDED = auto()

    # Relationships
    RELATIONSHIP_CREATED = auto()
    RELATIONSHIP_CHANGED = auto()

    # Social dynamics
    GOSSIP_SPREAD = auto()
    COALITION_FORMED = auto()
    COALITION_DISSOLVED = auto()

    # Inhabit
    INHABIT_STARTED = auto()
    INHABIT_ENDED = auto()
    FORCE_APPLIED = auto()

    # Simulation
    SIMULATION_STEP = auto()
    REGION_ACTIVITY = auto()


@dataclass(frozen=True, slots=True)
class TownEvent:
    """
    Base class for all town events.

    All town events are immutable and carry:
    - event_id: Unique identifier
    - event_type: Type of event
    - timestamp: When the event occurred
    - source: What generated this event
    - causal_parent: For event chaining
    """

    event_id: str
    event_type: TownEventType
    timestamp: float
    source: str = "town"
    causal_parent: str | None = None

    @classmethod
    def _create_id(cls) -> str:
        return uuid4().hex[:16]


# =============================================================================
# Citizen Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class CitizenCreated(TownEvent):
    """Emitted when a new citizen is created."""

    citizen_id: str = ""
    name: str = ""
    archetype: str = ""
    region: str = ""
    traits: tuple[tuple[str, Any], ...] = ()

    @classmethod
    def create(
        cls,
        citizen_id: str,
        name: str,
        archetype: str,
        region: str = "inn",
        traits: dict[str, Any] | None = None,
        causal_parent: str | None = None,
    ) -> CitizenCreated:
        """Factory for creating CitizenCreated events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CITIZEN_CREATED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            citizen_id=citizen_id,
            name=name,
            archetype=archetype,
            region=region,
            traits=tuple(traits.items()) if traits else (),
        )


@dataclass(frozen=True, slots=True)
class CitizenUpdated(TownEvent):
    """Emitted when a citizen's attributes change."""

    citizen_id: str = ""
    changes: tuple[tuple[str, Any], ...] = ()

    @classmethod
    def create(
        cls,
        citizen_id: str,
        changes: dict[str, Any],
        causal_parent: str | None = None,
    ) -> CitizenUpdated:
        """Factory for creating CitizenUpdated events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CITIZEN_UPDATED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            citizen_id=citizen_id,
            changes=tuple(changes.items()),
        )


@dataclass(frozen=True, slots=True)
class CitizenDeactivated(TownEvent):
    """Emitted when a citizen is deactivated."""

    citizen_id: str = ""
    reason: str = ""

    @classmethod
    def create(
        cls,
        citizen_id: str,
        reason: str = "manual",
        causal_parent: str | None = None,
    ) -> CitizenDeactivated:
        """Factory for creating CitizenDeactivated events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CITIZEN_DEACTIVATED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            citizen_id=citizen_id,
            reason=reason,
        )


# =============================================================================
# Conversation Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class ConversationStarted(TownEvent):
    """Emitted when a conversation begins."""

    conversation_id: str = ""
    citizen_id: str = ""
    topic: str = ""

    @classmethod
    def create(
        cls,
        conversation_id: str,
        citizen_id: str,
        topic: str = "",
        causal_parent: str | None = None,
    ) -> ConversationStarted:
        """Factory for creating ConversationStarted events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CONVERSATION_STARTED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            conversation_id=conversation_id,
            citizen_id=citizen_id,
            topic=topic,
        )


@dataclass(frozen=True, slots=True)
class ConversationTurn(TownEvent):
    """Emitted when a turn is added to a conversation."""

    conversation_id: str = ""
    citizen_id: str = ""
    turn_number: int = 0
    role: str = ""  # "user" | "citizen" | "system"
    content: str = ""
    sentiment: str | None = None
    emotion: str | None = None

    @classmethod
    def create(
        cls,
        conversation_id: str,
        citizen_id: str,
        turn_number: int,
        role: str,
        content: str,
        sentiment: str | None = None,
        emotion: str | None = None,
        causal_parent: str | None = None,
    ) -> ConversationTurn:
        """Factory for creating ConversationTurn events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CONVERSATION_TURN,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            conversation_id=conversation_id,
            citizen_id=citizen_id,
            turn_number=turn_number,
            role=role,
            content=content,
            sentiment=sentiment,
            emotion=emotion,
        )


@dataclass(frozen=True, slots=True)
class ConversationEnded(TownEvent):
    """Emitted when a conversation ends."""

    conversation_id: str = ""
    citizen_id: str = ""
    turn_count: int = 0
    summary: str = ""

    @classmethod
    def create(
        cls,
        conversation_id: str,
        citizen_id: str,
        turn_count: int,
        summary: str = "",
        causal_parent: str | None = None,
    ) -> ConversationEnded:
        """Factory for creating ConversationEnded events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.CONVERSATION_ENDED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            conversation_id=conversation_id,
            citizen_id=citizen_id,
            turn_count=turn_count,
            summary=summary,
        )


# =============================================================================
# Relationship Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class RelationshipCreated(TownEvent):
    """Emitted when a new relationship forms."""

    relationship_id: str = ""
    citizen_a: str = ""
    citizen_b: str = ""
    relationship_type: str = ""
    initial_strength: float = 0.5

    @classmethod
    def create(
        cls,
        relationship_id: str,
        citizen_a: str,
        citizen_b: str,
        relationship_type: str,
        initial_strength: float = 0.5,
        causal_parent: str | None = None,
    ) -> RelationshipCreated:
        """Factory for creating RelationshipCreated events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.RELATIONSHIP_CREATED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            relationship_id=relationship_id,
            citizen_a=citizen_a,
            citizen_b=citizen_b,
            relationship_type=relationship_type,
            initial_strength=initial_strength,
        )


@dataclass(frozen=True, slots=True)
class RelationshipChanged(TownEvent):
    """Emitted when a relationship strength changes."""

    relationship_id: str = ""
    citizen_a: str = ""
    citizen_b: str = ""
    old_strength: float = 0.0
    new_strength: float = 0.0
    reason: str = ""  # What caused the change

    @classmethod
    def create(
        cls,
        relationship_id: str,
        citizen_a: str,
        citizen_b: str,
        old_strength: float,
        new_strength: float,
        reason: str = "interaction",
        causal_parent: str | None = None,
    ) -> RelationshipChanged:
        """Factory for creating RelationshipChanged events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.RELATIONSHIP_CHANGED,
            timestamp=time.time(),
            source="town.persistence",
            causal_parent=causal_parent,
            relationship_id=relationship_id,
            citizen_a=citizen_a,
            citizen_b=citizen_b,
            old_strength=old_strength,
            new_strength=new_strength,
            reason=reason,
        )


# =============================================================================
# Social Dynamics Events (Cross-Jewel)
# =============================================================================


@dataclass(frozen=True, slots=True)
class GossipSpread(TownEvent):
    """
    Emitted when gossip spreads between citizens.

    This event triggers K-gent narrative generation via SynergyBus.
    """

    source_citizen: str = ""
    target_citizen: str = ""
    rumor_content: str = ""
    accuracy: float = 1.0  # 0.0 = false rumor, 1.0 = accurate
    source_region: str = ""
    target_region: str = ""

    @classmethod
    def create(
        cls,
        source_citizen: str,
        target_citizen: str,
        rumor_content: str,
        accuracy: float = 1.0,
        source_region: str = "",
        target_region: str = "",
        causal_parent: str | None = None,
    ) -> GossipSpread:
        """Factory for creating GossipSpread events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.GOSSIP_SPREAD,
            timestamp=time.time(),
            source="town.simulation",
            causal_parent=causal_parent,
            source_citizen=source_citizen,
            target_citizen=target_citizen,
            rumor_content=rumor_content,
            accuracy=accuracy,
            source_region=source_region,
            target_region=target_region,
        )


@dataclass(frozen=True, slots=True)
class CoalitionFormed(TownEvent):
    """
    Emitted when a coalition is detected/formed.

    This event triggers Atelier creative prompts via SynergyBus.
    """

    coalition_id: str = ""
    members: FrozenSet[str] = frozenset()
    purpose: str = ""
    strength: float = 1.0

    @classmethod
    def create(
        cls,
        coalition_id: str,
        members: set[str] | frozenset[str],
        purpose: str = "",
        strength: float = 1.0,
        causal_parent: str | None = None,
    ) -> CoalitionFormed:
        """Factory for creating CoalitionFormed events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.COALITION_FORMED,
            timestamp=time.time(),
            source="town.coalition",
            causal_parent=causal_parent,
            coalition_id=coalition_id,
            members=frozenset(members),
            purpose=purpose,
            strength=strength,
        )


@dataclass(frozen=True, slots=True)
class CoalitionDissolved(TownEvent):
    """Emitted when a coalition dissolves."""

    coalition_id: str = ""
    members: FrozenSet[str] = frozenset()
    reason: str = ""

    @classmethod
    def create(
        cls,
        coalition_id: str,
        members: set[str] | frozenset[str],
        reason: str = "decay",
        causal_parent: str | None = None,
    ) -> CoalitionDissolved:
        """Factory for creating CoalitionDissolved events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.COALITION_DISSOLVED,
            timestamp=time.time(),
            source="town.coalition",
            causal_parent=causal_parent,
            coalition_id=coalition_id,
            members=frozenset(members),
            reason=reason,
        )


# =============================================================================
# Inhabit Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class InhabitStarted(TownEvent):
    """Emitted when a user starts inhabiting a citizen."""

    user_id: str = ""
    citizen_id: str = ""
    inhabit_mode: str = ""  # "basic" | "full" | "unlimited"

    @classmethod
    def create(
        cls,
        user_id: str,
        citizen_id: str,
        inhabit_mode: str = "basic",
        causal_parent: str | None = None,
    ) -> InhabitStarted:
        """Factory for creating InhabitStarted events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.INHABIT_STARTED,
            timestamp=time.time(),
            source="town.inhabit",
            causal_parent=causal_parent,
            user_id=user_id,
            citizen_id=citizen_id,
            inhabit_mode=inhabit_mode,
        )


@dataclass(frozen=True, slots=True)
class InhabitEnded(TownEvent):
    """Emitted when a user stops inhabiting a citizen."""

    user_id: str = ""
    citizen_id: str = ""
    duration_seconds: float = 0.0
    actions_taken: int = 0

    @classmethod
    def create(
        cls,
        user_id: str,
        citizen_id: str,
        duration_seconds: float,
        actions_taken: int = 0,
        causal_parent: str | None = None,
    ) -> InhabitEnded:
        """Factory for creating InhabitEnded events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.INHABIT_ENDED,
            timestamp=time.time(),
            source="town.inhabit",
            causal_parent=causal_parent,
            user_id=user_id,
            citizen_id=citizen_id,
            duration_seconds=duration_seconds,
            actions_taken=actions_taken,
        )


@dataclass(frozen=True, slots=True)
class ForceApplied(TownEvent):
    """
    Emitted when a user forces a citizen action.

    This is an ethical guardrail event - tracks consent debt.
    """

    user_id: str = ""
    citizen_id: str = ""
    action: str = ""
    severity: float = 0.2
    debt_after: float = 0.0

    @classmethod
    def create(
        cls,
        user_id: str,
        citizen_id: str,
        action: str,
        severity: float = 0.2,
        debt_after: float = 0.0,
        causal_parent: str | None = None,
    ) -> ForceApplied:
        """Factory for creating ForceApplied events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.FORCE_APPLIED,
            timestamp=time.time(),
            source="town.inhabit",
            causal_parent=causal_parent,
            user_id=user_id,
            citizen_id=citizen_id,
            action=action,
            severity=severity,
            debt_after=debt_after,
        )


# =============================================================================
# Simulation Events
# =============================================================================


@dataclass(frozen=True, slots=True)
class SimulationStep(TownEvent):
    """Emitted when a simulation step completes."""

    step_number: int = 0
    active_citizens: int = 0
    interactions: int = 0
    coalitions_changed: int = 0

    @classmethod
    def create(
        cls,
        step_number: int,
        active_citizens: int,
        interactions: int = 0,
        coalitions_changed: int = 0,
        causal_parent: str | None = None,
    ) -> SimulationStep:
        """Factory for creating SimulationStep events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.SIMULATION_STEP,
            timestamp=time.time(),
            source="town.simulation",
            causal_parent=causal_parent,
            step_number=step_number,
            active_citizens=active_citizens,
            interactions=interactions,
            coalitions_changed=coalitions_changed,
        )


@dataclass(frozen=True, slots=True)
class RegionActivity(TownEvent):
    """Emitted when significant activity happens in a region."""

    region: str = ""
    citizen_count: int = 0
    activity_type: str = ""  # "gathering", "dispersing", "event"
    details: str = ""

    @classmethod
    def create(
        cls,
        region: str,
        citizen_count: int,
        activity_type: str,
        details: str = "",
        causal_parent: str | None = None,
    ) -> RegionActivity:
        """Factory for creating RegionActivity events."""
        return cls(
            event_id=cls._create_id(),
            event_type=TownEventType.REGION_ACTIVITY,
            timestamp=time.time(),
            source="town.simulation",
            causal_parent=causal_parent,
            region=region,
            citizen_count=citizen_count,
            activity_type=activity_type,
            details=details,
        )


# =============================================================================
# Event Topic Constants (for SynergyBus)
# =============================================================================


class TownTopics:
    """
    SynergyBus topic constants for town events.

    Topics are hierarchical:
    - town.citizen.* - Citizen lifecycle
    - town.conversation.* - Conversation events
    - town.relationship.* - Relationship changes
    - town.social.* - Social dynamics (gossip, coalitions)
    - town.inhabit.* - Inhabit/force events
    - town.simulation.* - Simulation events
    """

    # Citizen lifecycle
    CITIZEN_CREATED = "town.citizen.created"
    CITIZEN_UPDATED = "town.citizen.updated"
    CITIZEN_DEACTIVATED = "town.citizen.deactivated"

    # Conversation
    CONVERSATION_STARTED = "town.conversation.started"
    CONVERSATION_TURN = "town.conversation.turn"
    CONVERSATION_ENDED = "town.conversation.ended"

    # Relationships
    RELATIONSHIP_CREATED = "town.relationship.created"
    RELATIONSHIP_CHANGED = "town.relationship.changed"

    # Social dynamics (cross-jewel)
    GOSSIP_SPREAD = "town.social.gossip"
    COALITION_FORMED = "town.social.coalition.formed"
    COALITION_DISSOLVED = "town.social.coalition.dissolved"

    # Inhabit
    INHABIT_STARTED = "town.inhabit.started"
    INHABIT_ENDED = "town.inhabit.ended"
    FORCE_APPLIED = "town.inhabit.force"

    # Simulation
    SIMULATION_STEP = "town.simulation.step"
    REGION_ACTIVITY = "town.simulation.region"

    # Wildcards for subscription
    ALL = "town.*"
    CITIZEN_ALL = "town.citizen.*"
    CONVERSATION_ALL = "town.conversation.*"
    SOCIAL_ALL = "town.social.*"


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Base
    "TownEventType",
    "TownEvent",
    # Citizen events
    "CitizenCreated",
    "CitizenUpdated",
    "CitizenDeactivated",
    # Conversation events
    "ConversationStarted",
    "ConversationTurn",
    "ConversationEnded",
    # Relationship events
    "RelationshipCreated",
    "RelationshipChanged",
    # Social events
    "GossipSpread",
    "CoalitionFormed",
    "CoalitionDissolved",
    # Inhabit events
    "InhabitStarted",
    "InhabitEnded",
    "ForceApplied",
    # Simulation events
    "SimulationStep",
    "RegionActivity",
    # Topics
    "TownTopics",
]
