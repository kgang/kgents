"""
Semantic Stigmergic Field: Agent coordination via environmental signals.

Phase 2 of Cross-Pollination Proposal: Agents don't call each other directly.
They emit signals to the field; others sense them.

Key pheromone types:
- METAPHOR: Psi-gent emits Functor[P,K] for F/R/E to sense
- INTENT: F-gent emits ArtifactIntent for G/P to sense
- WARNING: J-gent emits SafetyAlert for all agents
- OPPORTUNITY: B-gent emits EconomicSignal for E/R

Integration Example (Psi × F decoupled):
- Psi-gent: Leaves metaphor pheromone, doesn't know F exists
- F-gent: Senses metaphor pheromones, doesn't know Psi exists
- Result: Complete decoupling via shared field

See: docs/agent-cross-pollination-final-proposal.md (Phase 2)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime
from enum import Enum
from math import exp
from typing import Any, Callable, Generic, TypeVar
from uuid import uuid4

A = TypeVar("A")  # Source type
B = TypeVar("B")  # Target type


class SemanticPheromoneKind(Enum):
    """
    Types of semantic pheromones for agent coordination.

    Each kind carries specific payload types and decay characteristics.
    """

    # Psi-gent emissions
    METAPHOR = "metaphor"  # Functor[ProblemSpace, KnownDomain]

    # F-gent emissions
    INTENT = "intent"  # ArtifactIntent
    ARTIFACT = "artifact"  # Created artifact reference

    # J-gent emissions
    WARNING = "warning"  # SafetyAlert

    # B-gent emissions
    OPPORTUNITY = "opportunity"  # EconomicSignal
    SCARCITY = "scarcity"  # Resource constraint

    # M-gent emissions
    MEMORY = "memory"  # Memory reference for consolidation

    # N-gent emissions
    NARRATIVE = "narrative"  # Story thread/crystal

    # L-gent emissions (Phase 4)
    CAPABILITY = "capability"  # Agent capability advertisement

    @property
    def decay_rate(self) -> float:
        """Decay rate per tick (0.0 to 1.0)."""
        return {
            SemanticPheromoneKind.METAPHOR: 0.1,  # Slow decay - metaphors persist
            SemanticPheromoneKind.INTENT: 0.2,  # Moderate decay
            SemanticPheromoneKind.ARTIFACT: 0.05,  # Very slow - artifacts persist
            SemanticPheromoneKind.WARNING: 0.3,  # Fast decay - warnings are urgent
            SemanticPheromoneKind.OPPORTUNITY: 0.15,  # Moderate decay
            SemanticPheromoneKind.SCARCITY: 0.25,  # Faster decay
            SemanticPheromoneKind.MEMORY: 0.08,  # Slow decay - memories persist
            SemanticPheromoneKind.NARRATIVE: 0.12,  # Moderate decay
            SemanticPheromoneKind.CAPABILITY: 0.02,  # Very slow - capabilities are stable
        }[self]

    @property
    def default_radius(self) -> float:
        """Default sensing radius in embedding space."""
        return {
            SemanticPheromoneKind.METAPHOR: 0.5,  # Wide radius for metaphors
            SemanticPheromoneKind.INTENT: 0.3,  # Narrow for specific intents
            SemanticPheromoneKind.ARTIFACT: 0.4,
            SemanticPheromoneKind.WARNING: 1.0,  # Broadcast warnings widely
            SemanticPheromoneKind.OPPORTUNITY: 0.6,
            SemanticPheromoneKind.SCARCITY: 0.8,  # Wide awareness of scarcity
            SemanticPheromoneKind.MEMORY: 0.3,
            SemanticPheromoneKind.NARRATIVE: 0.4,
            SemanticPheromoneKind.CAPABILITY: 1.0,  # Wide broadcast for discovery
        }[self]


@dataclass
class FieldCoordinate:
    """
    Position in the semantic field.

    Can be either:
    - Embedding-based: tuple of floats from L-gent
    - Domain-based: categorical position in problem taxonomy
    """

    embedding: tuple[float, ...] | None = None
    domain: str | None = None
    tags: tuple[str, ...] = ()

    def distance_to(self, other: FieldCoordinate) -> float:
        """Calculate distance to another coordinate."""
        if self.embedding and other.embedding:
            # Euclidean distance in embedding space
            if len(self.embedding) != len(other.embedding):
                return float("inf")
            sum_sq = sum((a - b) ** 2 for a, b in zip(self.embedding, other.embedding))
            return sum_sq**0.5

        if self.domain and other.domain:
            # Domain matching: 0.0 if same, 1.0 if different
            return 0.0 if self.domain == other.domain else 1.0

        # Tag-based similarity
        if self.tags and other.tags:
            intersection = len(set(self.tags) & set(other.tags))
            union = len(set(self.tags) | set(other.tags))
            return 1.0 - (intersection / union) if union > 0 else 1.0

        return 1.0  # Default: maximum distance


@dataclass
class SemanticPheromone(Generic[A]):
    """
    A semantic signal left in the field.

    Agents emit pheromones; others sense them without direct coupling.
    """

    id: str
    emitter: str  # Agent ID that emitted
    kind: SemanticPheromoneKind
    payload: A  # Type-specific payload (Functor, Intent, etc.)
    intensity: float  # Current intensity (decays over time)
    position: FieldCoordinate
    timestamp: datetime = dataclass_field(default_factory=datetime.now)
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    def decay(self, dt: float) -> float:
        """
        Apply time decay to intensity.

        Uses exponential decay: I(t) = I_0 * e^(-λt)
        """
        decay_rate = self.kind.decay_rate
        self.intensity *= exp(-decay_rate * dt)
        return self.intensity

    @property
    def is_active(self) -> bool:
        """Is this pheromone still active (above threshold)?"""
        return self.intensity > 0.01


@dataclass
class MetaphorPayload:
    """
    Payload for METAPHOR pheromones.

    Represents a functor from problem space to known domain.
    """

    source_domain: str  # Problem domain
    target_domain: str  # Known domain (the metaphor)
    confidence: float  # How good is this metaphor?

    # The mapping (simplified - full version would be Functor[P,K])
    object_map: dict[str, str] = dataclass_field(default_factory=dict)

    # Example: "database query" -> "topological sort"
    description: str = ""

    # Operations that can be transferred
    transferable_operations: tuple[str, ...] = ()


@dataclass
class IntentPayload:
    """
    Payload for INTENT pheromones.

    Represents a forging intent from F-gent.
    """

    purpose: str
    behaviors: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    domain: str | None = None


@dataclass
class WarningPayload:
    """
    Payload for WARNING pheromones.

    Safety alerts from J-gent.
    """

    severity: str  # "info", "warning", "error", "critical"
    message: str
    affected_agents: tuple[str, ...] = ()

    # What triggered the warning
    trigger: str = ""

    # Recommended action
    recommendation: str = ""


@dataclass
class OpportunityPayload:
    """
    Payload for OPPORTUNITY pheromones.

    Economic signals from B-gent.
    """

    signal_type: str  # "surplus", "demand", "arbitrage"
    value: float
    resource: str  # What resource

    # Time sensitivity
    expires_in_ticks: int = 10


# =============================================================================
# L-gent Capability Payloads (Phase 4)
# =============================================================================


@dataclass
class CapabilityPayload:
    """
    Payload for CAPABILITY pheromones.

    Represents an agent's advertised capability.
    L-gent uses this for semantic service discovery.
    """

    agent_id: str
    capability_name: str
    input_type: str  # Expected input type (e.g., "str", "Functor[A,B]")
    output_type: str  # Output type
    cost_estimate: float = 0.0  # Estimated token/compute cost
    tags: tuple[str, ...] = ()  # For tag-based filtering
    description: str = ""  # Human-readable description
    version: str = "1.0"  # Capability version


@dataclass
class CapabilityDeprecationPayload:
    """
    Payload for capability deprecation notices.

    Emitted when an agent is retiring a capability.
    """

    agent_id: str
    capability_name: str
    reason: str
    replacement: str | None = None  # Suggested replacement capability
    deprecation_date: str = ""  # ISO format date


@dataclass
class CapabilityRequestPayload:
    """
    Payload for capability requests.

    Emitted when an agent is looking for a capability.
    """

    requester_id: str
    capability_pattern: str  # Pattern to match (e.g., "embed*", "parse_json")
    urgency: float = 0.5  # 0.0 (low) to 1.0 (high)
    input_type: str | None = None  # Required input type
    output_type: str | None = None  # Required output type
    tags: tuple[str, ...] = ()  # Required tags


class SemanticField:
    """
    The shared environment all agents inhabit.

    Agents don't know each other. They know:
    1. How to emit signals (deposit)
    2. How to sense signals (sense)
    3. Signals decay over time

    Everything else emerges.
    """

    def __init__(
        self,
        decay_tick_interval: float = 1.0,
        intensity_threshold: float = 0.01,
    ):
        self._pheromones: dict[str, SemanticPheromone[Any]] = {}
        self._decay_tick_interval = decay_tick_interval
        self._intensity_threshold = intensity_threshold
        self._current_tick = 0

        # Event hooks for observation
        self._on_deposit: list[Callable[[SemanticPheromone[Any]], None]] = []
        self._on_sense: list[Callable[[str, list[SemanticPheromone[Any]]], None]] = []

    def deposit(self, pheromone: SemanticPheromone[Any]) -> str:
        """
        Agent leaves a signal in the field.

        Returns the pheromone ID.
        """
        self._pheromones[pheromone.id] = pheromone

        # Notify observers
        for callback in self._on_deposit:
            callback(pheromone)

        return pheromone.id

    def emit(
        self,
        emitter: str,
        kind: SemanticPheromoneKind,
        payload: Any,
        position: FieldCoordinate,
        intensity: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Convenience method to create and deposit a pheromone.
        """
        pheromone: SemanticPheromone[Any] = SemanticPheromone(
            id=f"phero-{uuid4().hex[:8]}",
            emitter=emitter,
            kind=kind,
            payload=payload,
            intensity=intensity,
            position=position,
            metadata=metadata or {},
        )
        return self.deposit(pheromone)

    def sense(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        kind: SemanticPheromoneKind | None = None,
    ) -> list[SemanticPheromone[Any]]:
        """
        Agent senses nearby signals.

        Args:
            position: Where to sense from
            radius: Maximum distance to sense (default: kind's default or 0.5)
            kind: Filter by pheromone kind (optional)

        Returns:
            List of pheromones within radius, sorted by intensity (strongest first)
        """
        if radius is None:
            radius = kind.default_radius if kind else 0.5

        results: list[SemanticPheromone[Any]] = []

        for pheromone in self._pheromones.values():
            if not pheromone.is_active:
                continue

            if kind is not None and pheromone.kind != kind:
                continue

            distance = position.distance_to(pheromone.position)
            if distance <= radius:
                results.append(pheromone)

        # Sort by intensity (strongest first)
        results.sort(key=lambda p: p.intensity, reverse=True)

        # Notify observers
        for callback in self._on_sense:
            callback(kind.value if kind else "any", results)

        return results

    def sense_strongest(
        self,
        position: FieldCoordinate,
        kind: SemanticPheromoneKind,
        radius: float | None = None,
    ) -> SemanticPheromone[Any] | None:
        """
        Sense the strongest pheromone of a given kind.
        """
        results = self.sense(position, radius, kind)
        return results[0] if results else None

    def tick(self, dt: float = 1.0) -> int:
        """
        Advance time, decaying all pheromones.

        Returns the number of pheromones that expired.
        """
        self._current_tick += 1
        expired = 0

        to_remove = []
        for phero_id, pheromone in self._pheromones.items():
            pheromone.decay(dt)
            if not pheromone.is_active:
                to_remove.append(phero_id)
                expired += 1

        for phero_id in to_remove:
            del self._pheromones[phero_id]

        return expired

    def get_all(
        self,
        kind: SemanticPheromoneKind | None = None,
    ) -> list[SemanticPheromone[Any]]:
        """Get all active pheromones, optionally filtered by kind."""
        results = [p for p in self._pheromones.values() if p.is_active]
        if kind:
            results = [p for p in results if p.kind == kind]
        return results

    def clear(self) -> int:
        """Clear all pheromones. Returns count cleared."""
        count = len(self._pheromones)
        self._pheromones.clear()
        return count

    def on_deposit(self, callback: Callable[[SemanticPheromone[Any]], None]) -> None:
        """Register a callback for pheromone deposits."""
        self._on_deposit.append(callback)

    def on_sense(
        self, callback: Callable[[str, list[SemanticPheromone[Any]]], None]
    ) -> None:
        """Register a callback for sense operations."""
        self._on_sense.append(callback)

    @property
    def pheromone_count(self) -> int:
        """Number of active pheromones."""
        return len(self._pheromones)

    @property
    def current_tick(self) -> int:
        """Current simulation tick."""
        return self._current_tick


# =============================================================================
# Psi-gent Field Interface (Emitter)
# =============================================================================


class PsiFieldEmitter:
    """
    Psi-gent's interface to the semantic field.

    Emits METAPHOR pheromones when metaphors are discovered.
    Does NOT know about F-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "psi"):
        self._field = field
        self._agent_id = agent_id

    def emit_metaphor(
        self,
        source_domain: str,
        target_domain: str,
        confidence: float,
        position: FieldCoordinate,
        object_map: dict[str, str] | None = None,
        description: str = "",
        transferable_operations: tuple[str, ...] = (),
    ) -> str:
        """
        Emit a metaphor pheromone.

        Called when Psi-gent discovers a useful metaphor.
        """
        payload = MetaphorPayload(
            source_domain=source_domain,
            target_domain=target_domain,
            confidence=confidence,
            object_map=object_map or {},
            description=description,
            transferable_operations=transferable_operations,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.METAPHOR,
            payload=payload,
            position=position,
            intensity=confidence,  # Use confidence as intensity
            metadata={"source_domain": source_domain, "target_domain": target_domain},
        )


# =============================================================================
# F-gent Field Interface (Consumer)
# =============================================================================


class ForgeFieldSensor:
    """
    F-gent's interface to the semantic field.

    Senses METAPHOR pheromones to enhance forging.
    Does NOT know about Psi-gent or any emitter.
    """

    def __init__(self, field: SemanticField, agent_id: str = "forge"):
        self._field = field
        self._agent_id = agent_id

    def sense_metaphors(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[MetaphorPayload]:
        """
        Sense nearby metaphor pheromones.

        Returns metaphor payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.METAPHOR,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, MetaphorPayload)]

    def get_strongest_metaphor(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> MetaphorPayload | None:
        """
        Get the strongest metaphor near this position.
        """
        metaphors = self.sense_metaphors(position, radius)
        return metaphors[0] if metaphors else None

    def emit_intent(
        self,
        purpose: str,
        position: FieldCoordinate,
        behaviors: tuple[str, ...] = (),
        constraints: tuple[str, ...] = (),
        domain: str | None = None,
    ) -> str:
        """
        Emit an intent pheromone (for G-gent/P-gent to sense).
        """
        payload = IntentPayload(
            purpose=purpose,
            behaviors=behaviors,
            constraints=constraints,
            domain=domain,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.INTENT,
            payload=payload,
            position=position,
            intensity=1.0,
            metadata={"purpose": purpose},
        )


# =============================================================================
# J-gent Field Interface (Warning Emitter)
# =============================================================================


class SafetyFieldEmitter:
    """
    J-gent's interface for emitting safety warnings.
    """

    def __init__(self, field: SemanticField, agent_id: str = "judge"):
        self._field = field
        self._agent_id = agent_id

    def emit_warning(
        self,
        severity: str,
        message: str,
        position: FieldCoordinate,
        affected_agents: tuple[str, ...] = (),
        trigger: str = "",
        recommendation: str = "",
    ) -> str:
        """
        Emit a safety warning.

        Warnings have high intensity and broadcast widely.
        """
        payload = WarningPayload(
            severity=severity,
            message=message,
            affected_agents=affected_agents,
            trigger=trigger,
            recommendation=recommendation,
        )

        # Intensity based on severity
        intensity_map = {
            "info": 0.3,
            "warning": 0.6,
            "error": 0.8,
            "critical": 1.0,
        }
        intensity = intensity_map.get(severity, 0.5)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.WARNING,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={"severity": severity},
        )


# =============================================================================
# B-gent Field Interface (Economic Signals)
# =============================================================================


class EconomicFieldEmitter:
    """
    B-gent's interface for emitting economic signals.
    """

    def __init__(self, field: SemanticField, agent_id: str = "banker"):
        self._field = field
        self._agent_id = agent_id

    def emit_opportunity(
        self,
        signal_type: str,
        value: float,
        resource: str,
        position: FieldCoordinate,
        expires_in_ticks: int = 10,
    ) -> str:
        """
        Emit an economic opportunity signal.
        """
        payload = OpportunityPayload(
            signal_type=signal_type,
            value=value,
            resource=resource,
            expires_in_ticks=expires_in_ticks,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.OPPORTUNITY,
            payload=payload,
            position=position,
            intensity=min(1.0, value / 100),  # Normalize value to intensity
            metadata={"signal_type": signal_type, "resource": resource},
        )

    def emit_scarcity(
        self,
        resource: str,
        severity: float,
        position: FieldCoordinate,
    ) -> str:
        """
        Emit a scarcity signal.
        """
        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.SCARCITY,
            payload={"resource": resource, "severity": severity},
            position=position,
            intensity=severity,
            metadata={"resource": resource},
        )


# =============================================================================
# M-gent Field Interface (Memory Signals)
# =============================================================================


@dataclass
class MemoryPayload:
    """
    Payload for MEMORY pheromones.

    Represents a memory signal for consolidation.
    """

    memory_id: str
    importance: float  # How important is this memory?
    decay_urgency: float  # How soon should this be consolidated?
    context_tags: tuple[str, ...] = ()
    summary: str = ""


class MemoryFieldEmitter:
    """
    M-gent's interface for emitting memory signals.

    Emits when memories should be consolidated or when important
    context should be shared with other agents.
    """

    def __init__(self, field: SemanticField, agent_id: str = "memory"):
        self._field = field
        self._agent_id = agent_id

    def emit_consolidation(
        self,
        memory_id: str,
        importance: float,
        position: FieldCoordinate,
        decay_urgency: float = 0.5,
        context_tags: tuple[str, ...] = (),
        summary: str = "",
    ) -> str:
        """
        Emit a memory consolidation signal.

        Called when M-gent detects a memory worth persisting.
        """
        payload = MemoryPayload(
            memory_id=memory_id,
            importance=importance,
            decay_urgency=decay_urgency,
            context_tags=context_tags,
            summary=summary,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.MEMORY,
            payload=payload,
            position=position,
            intensity=importance,
            metadata={"memory_id": memory_id, "urgency": decay_urgency},
        )


class MemoryFieldSensor:
    """
    Sensor for memory signals.

    Other agents can use this to detect when important context
    is available in the field.
    """

    def __init__(self, field: SemanticField, agent_id: str = "memory_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_memories(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        min_importance: float = 0.0,
    ) -> list[MemoryPayload]:
        """
        Sense nearby memory signals.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.MEMORY,
        )

        return [
            p.payload
            for p in pheromones
            if isinstance(p.payload, MemoryPayload)
            and p.payload.importance >= min_importance
        ]


# =============================================================================
# N-gent Field Interface (Narrative Signals)
# =============================================================================


@dataclass
class NarrativePayload:
    """
    Payload for NARRATIVE pheromones.

    Represents a narrative thread or chronicle entry.
    """

    thread_id: str
    event_type: str  # "beginning", "development", "climax", "resolution"
    summary: str
    actors: tuple[str, ...] = ()
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)


class NarrativeFieldEmitter:
    """
    N-gent's interface for emitting narrative signals.

    Emits story events that other agents can incorporate into
    their context or decision-making.
    """

    def __init__(self, field: SemanticField, agent_id: str = "narrator"):
        self._field = field
        self._agent_id = agent_id

    def emit_story_event(
        self,
        thread_id: str,
        event_type: str,
        summary: str,
        position: FieldCoordinate,
        actors: tuple[str, ...] = (),
        emotional_valence: float = 0.0,
    ) -> str:
        """
        Emit a narrative event signal.

        Called when N-gent chronicles a significant event.
        """
        payload = NarrativePayload(
            thread_id=thread_id,
            event_type=event_type,
            summary=summary,
            actors=actors,
            emotional_valence=emotional_valence,
        )

        # Intensity based on event type (climax = highest)
        intensity_map = {
            "beginning": 0.5,
            "development": 0.6,
            "climax": 1.0,
            "resolution": 0.7,
        }
        intensity = intensity_map.get(event_type, 0.5)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.NARRATIVE,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={"thread_id": thread_id, "event_type": event_type},
        )


class NarrativeFieldSensor:
    """
    Sensor for narrative signals.

    Allows agents to incorporate story context into their operations.
    """

    def __init__(self, field: SemanticField, agent_id: str = "narrative_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_narratives(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        thread_id: str | None = None,
    ) -> list[NarrativePayload]:
        """
        Sense nearby narrative signals.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.NARRATIVE,
        )

        results = [
            p.payload for p in pheromones if isinstance(p.payload, NarrativePayload)
        ]

        if thread_id:
            results = [n for n in results if n.thread_id == thread_id]

        return results


# =============================================================================
# O-gent Field Interface (Observer - senses all signals)
# =============================================================================


class ObserverFieldSensor:
    """
    O-gent's interface for observing the semantic field.

    Can sense ALL pheromone types for monitoring and telemetry.
    """

    def __init__(self, field: SemanticField, agent_id: str = "observer"):
        self._field = field
        self._agent_id = agent_id

    def observe_all(
        self,
        position: FieldCoordinate,
        radius: float = 1.0,
    ) -> dict[str, list[SemanticPheromone[Any]]]:
        """
        Observe all signals in the field.

        Returns signals grouped by pheromone kind.
        """
        result: dict[str, list[SemanticPheromone[Any]]] = {}

        for kind in SemanticPheromoneKind:
            signals = self._field.sense(position=position, radius=radius, kind=kind)
            if signals:
                result[kind.value] = signals

        return result

    def observe_warnings(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        min_severity: str = "info",
    ) -> list[WarningPayload]:
        """
        Specifically observe warning signals.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.WARNING,
        )

        severity_levels = {"info": 0, "warning": 1, "error": 2, "critical": 3}
        min_level = severity_levels.get(min_severity, 0)

        return [
            p.payload
            for p in pheromones
            if isinstance(p.payload, WarningPayload)
            and severity_levels.get(p.payload.severity, 0) >= min_level
        ]

    def field_summary(self) -> dict[str, int]:
        """
        Get a summary of field activity by pheromone type.
        """
        return {
            kind.value: len(self._field.get_all(kind)) for kind in SemanticPheromoneKind
        }


# =============================================================================
# L-gent Field Interface (Catalog - Emitter + Sensor)
# =============================================================================


class CatalogFieldEmitter:
    """
    L-gent's interface for emitting capability signals.

    Advertises agent capabilities to the semantic field for discovery.
    Does NOT know about specific consumers of capabilities.
    """

    def __init__(self, field: SemanticField, agent_id: str = "catalog"):
        self._field = field
        self._agent_id = agent_id

    def emit_capability_registered(
        self,
        agent_id: str,
        capability_name: str,
        input_type: str,
        output_type: str,
        position: FieldCoordinate,
        cost_estimate: float = 0.0,
        tags: tuple[str, ...] = (),
        description: str = "",
        version: str = "1.0",
    ) -> str:
        """
        Emit a capability registration signal.

        Called when an agent registers a new capability with the catalog.
        """
        payload = CapabilityPayload(
            agent_id=agent_id,
            capability_name=capability_name,
            input_type=input_type,
            output_type=output_type,
            cost_estimate=cost_estimate,
            tags=tags,
            description=description,
            version=version,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.CAPABILITY,
            payload=payload,
            position=position,
            intensity=1.0,  # Capabilities are full strength
            metadata={
                "agent_id": agent_id,
                "capability_name": capability_name,
                "tags": list(tags),
            },
        )

    def emit_capability_deprecated(
        self,
        agent_id: str,
        capability_name: str,
        reason: str,
        position: FieldCoordinate,
        replacement: str | None = None,
        deprecation_date: str = "",
    ) -> str:
        """
        Emit a capability deprecation notice.

        Called when an agent is retiring a capability.
        """
        payload = CapabilityDeprecationPayload(
            agent_id=agent_id,
            capability_name=capability_name,
            reason=reason,
            replacement=replacement,
            deprecation_date=deprecation_date,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.CAPABILITY,
            payload=payload,
            position=position,
            intensity=0.8,  # Deprecations are important but not primary
            metadata={
                "agent_id": agent_id,
                "capability_name": capability_name,
                "deprecated": True,
            },
        )

    def emit_capability_updated(
        self,
        agent_id: str,
        capability_name: str,
        changes: dict[str, Any],
        position: FieldCoordinate,
        new_version: str = "",
    ) -> str:
        """
        Emit a capability update signal.

        Called when a capability's metadata changes.
        """
        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.CAPABILITY,
            payload={
                "agent_id": agent_id,
                "capability_name": capability_name,
                "changes": changes,
                "new_version": new_version,
                "update_type": "modification",
            },
            position=position,
            intensity=0.7,
            metadata={
                "agent_id": agent_id,
                "capability_name": capability_name,
                "update": True,
            },
        )

    def emit_capability_request(
        self,
        requester_id: str,
        capability_pattern: str,
        urgency: float,
        position: FieldCoordinate,
        input_type: str | None = None,
        output_type: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> str:
        """
        Emit a capability request signal.

        Called when an agent is looking for a capability.
        """
        payload = CapabilityRequestPayload(
            requester_id=requester_id,
            capability_pattern=capability_pattern,
            urgency=urgency,
            input_type=input_type,
            output_type=output_type,
            tags=tags,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.CAPABILITY,
            payload=payload,
            position=position,
            intensity=urgency,  # Urgency determines signal strength
            metadata={
                "requester_id": requester_id,
                "pattern": capability_pattern,
                "request": True,
            },
        )


class CatalogFieldSensor:
    """
    L-gent's interface for sensing capability signals.

    Discovers available capabilities in the semantic field.
    Does NOT know about specific emitters of capabilities.
    """

    def __init__(self, field: SemanticField, agent_id: str = "catalog_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_capabilities(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CapabilityPayload]:
        """
        Sense nearby capability signals.

        Returns capability payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.CAPABILITY,
        )

        return [
            p.payload for p in pheromones if isinstance(p.payload, CapabilityPayload)
        ]

    def sense_by_tags(
        self,
        position: FieldCoordinate,
        tags: tuple[str, ...],
        radius: float | None = None,
    ) -> list[CapabilityPayload]:
        """
        Sense capabilities filtered by tags.

        Returns capabilities that have at least one matching tag.
        """
        capabilities = self.sense_capabilities(position, radius)
        tag_set = set(tags)

        return [cap for cap in capabilities if set(cap.tags) & tag_set]

    def sense_deprecations(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CapabilityDeprecationPayload]:
        """
        Sense deprecation notices.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.CAPABILITY,
        )

        return [
            p.payload
            for p in pheromones
            if isinstance(p.payload, CapabilityDeprecationPayload)
        ]

    def sense_capability_requests(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CapabilityRequestPayload]:
        """
        Sense unfulfilled capability requests.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.CAPABILITY,
        )

        return [
            p.payload
            for p in pheromones
            if isinstance(p.payload, CapabilityRequestPayload)
        ]

    def find_capability(
        self,
        capability_name: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> CapabilityPayload | None:
        """
        Find a specific capability by name.
        """
        capabilities = self.sense_capabilities(position, radius)
        for cap in capabilities:
            if cap.capability_name == capability_name:
                return cap
        return None

    def get_agent_capabilities(
        self,
        agent_id: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CapabilityPayload]:
        """
        Get all capabilities from a specific agent.
        """
        capabilities = self.sense_capabilities(position, radius)
        return [cap for cap in capabilities if cap.agent_id == agent_id]

    def has_capability(
        self,
        capability_name: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> bool:
        """
        Check if a capability exists in the field.
        """
        return self.find_capability(capability_name, position, radius) is not None

    def get_capability_count(self) -> int:
        """
        Get total number of registered capabilities.
        """
        all_capabilities = self._field.get_all(SemanticPheromoneKind.CAPABILITY)
        return len(
            [p for p in all_capabilities if isinstance(p.payload, CapabilityPayload)]
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_semantic_field() -> SemanticField:
    """Create a new semantic field."""
    return SemanticField()


def create_psi_emitter(field: SemanticField, agent_id: str = "psi") -> PsiFieldEmitter:
    """Create a Psi-gent field emitter."""
    return PsiFieldEmitter(field, agent_id)


def create_forge_sensor(
    field: SemanticField, agent_id: str = "forge"
) -> ForgeFieldSensor:
    """Create an F-gent field sensor."""
    return ForgeFieldSensor(field, agent_id)


def create_safety_emitter(
    field: SemanticField, agent_id: str = "judge"
) -> SafetyFieldEmitter:
    """Create a J-gent safety emitter."""
    return SafetyFieldEmitter(field, agent_id)


def create_economic_emitter(
    field: SemanticField, agent_id: str = "banker"
) -> EconomicFieldEmitter:
    """Create a B-gent economic emitter."""
    return EconomicFieldEmitter(field, agent_id)


def create_memory_emitter(
    field: SemanticField, agent_id: str = "memory"
) -> MemoryFieldEmitter:
    """Create an M-gent memory emitter."""
    return MemoryFieldEmitter(field, agent_id)


def create_memory_sensor(
    field: SemanticField, agent_id: str = "memory_sensor"
) -> MemoryFieldSensor:
    """Create a memory field sensor."""
    return MemoryFieldSensor(field, agent_id)


def create_narrative_emitter(
    field: SemanticField, agent_id: str = "narrator"
) -> NarrativeFieldEmitter:
    """Create an N-gent narrative emitter."""
    return NarrativeFieldEmitter(field, agent_id)


def create_narrative_sensor(
    field: SemanticField, agent_id: str = "narrative_sensor"
) -> NarrativeFieldSensor:
    """Create a narrative field sensor."""
    return NarrativeFieldSensor(field, agent_id)


def create_observer_sensor(
    field: SemanticField, agent_id: str = "observer"
) -> ObserverFieldSensor:
    """Create an O-gent observer sensor."""
    return ObserverFieldSensor(field, agent_id)


def create_catalog_emitter(
    field: SemanticField, agent_id: str = "catalog"
) -> CatalogFieldEmitter:
    """Create an L-gent catalog emitter."""
    return CatalogFieldEmitter(field, agent_id)


def create_catalog_sensor(
    field: SemanticField, agent_id: str = "catalog_sensor"
) -> CatalogFieldSensor:
    """Create an L-gent catalog sensor."""
    return CatalogFieldSensor(field, agent_id)
