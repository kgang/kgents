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

from dataclasses import dataclass, field as dataclass_field
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

    # Phase 1: High-Priority Emitters
    # E-gent emissions
    MUTATION = "mutation"  # Evolution/mutation signals

    # H-gent emissions
    SYNTHESIS = "synthesis"  # Dialectic synthesis signals

    # K-gent emissions
    PRIOR = "prior"  # Persona/prior signals

    # R-gent emissions
    REFINEMENT = "refinement"  # Optimization/refinement signals

    # Phase 3: Infrastructure Agents
    # D-gent emissions
    STATE = "state"  # Data state changes (created/updated/deleted/stale)

    # T-gent emissions
    TEST = "test"  # Test results, coverage changes

    # W-gent emissions
    DISPATCH = "dispatch"  # Message routing, blocking events

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
            # Phase 1 types
            SemanticPheromoneKind.MUTATION: 0.2,  # Medium persistence - mutations matter
            SemanticPheromoneKind.SYNTHESIS: 0.1,  # Slow decay - insights persist
            SemanticPheromoneKind.PRIOR: 0.05,  # Very slow - persona is stable
            SemanticPheromoneKind.REFINEMENT: 0.15,  # Medium - refinements are actionable
            # Phase 3 types
            SemanticPheromoneKind.STATE: 0.15,  # Medium - state changes matter
            SemanticPheromoneKind.TEST: 0.25,  # Fast - test results are ephemeral
            SemanticPheromoneKind.DISPATCH: 0.4,  # Very fast - operational signals
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
            # Phase 1 types
            SemanticPheromoneKind.MUTATION: 0.6,  # Wide - evolution affects ecosystem
            SemanticPheromoneKind.SYNTHESIS: 0.5,  # Wide - insights spread
            SemanticPheromoneKind.PRIOR: 1.0,  # Very wide - persona affects all agents
            SemanticPheromoneKind.REFINEMENT: 0.5,  # Medium - targeted improvements
            # Phase 3 types
            SemanticPheromoneKind.STATE: 0.6,  # Medium-wide - state affects neighbors
            SemanticPheromoneKind.TEST: 0.8,  # Wide - test results matter to many
            SemanticPheromoneKind.DISPATCH: 0.4,  # Narrow - routing is targeted
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
            sum_sq: float = sum((a - b) ** 2 for a, b in zip(self.embedding, other.embedding))
            return float(sum_sq**0.5)

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

    def on_sense(self, callback: Callable[[str, list[SemanticPheromone[Any]]], None]) -> None:
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
            if isinstance(p.payload, MemoryPayload) and p.payload.importance >= min_importance
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

        results = [p.payload for p in pheromones if isinstance(p.payload, NarrativePayload)]

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
        return {kind.value: len(self._field.get_all(kind)) for kind in SemanticPheromoneKind}


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

        return [p.payload for p in pheromones if isinstance(p.payload, CapabilityPayload)]

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
            p.payload for p in pheromones if isinstance(p.payload, CapabilityDeprecationPayload)
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

        return [p.payload for p in pheromones if isinstance(p.payload, CapabilityRequestPayload)]

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
        return len([p for p in all_capabilities if isinstance(p.payload, CapabilityPayload)])


# =============================================================================
# Phase 1: E-gent Evolution Field Interface (MUTATION signals)
# =============================================================================


@dataclass
class MutationPayload:
    """
    Payload for MUTATION pheromones.

    Represents an evolution/mutation signal from E-gent's thermodynamic cycle.
    """

    mutation_id: str
    fitness_delta: float  # Change in fitness (-1.0 to 1.0)
    generation: int
    parent_id: str | None = None
    mutation_type: str = "unknown"  # "crossover", "point", "structural"
    schema_signature: str = ""  # Mutation schema used
    gibbs_energy: float = 0.0  # Thermodynamic viability


@dataclass
class FitnessChangePayload:
    """
    Payload for fitness change signals.

    Emitted when an entity's fitness changes significantly.
    """

    entity_id: str
    old_fitness: float
    new_fitness: float
    reason: str = ""


@dataclass
class CycleCompletePayload:
    """
    Payload for evolution cycle completion.

    Emitted at the end of a thermodynamic cycle.
    """

    generation: int
    best_fitness: float
    population_size: int
    mutations_succeeded: int
    mutations_failed: int
    temperature: float = 1.0


class EvolutionFieldEmitter:
    """
    E-gent's interface for emitting evolution/mutation signals.

    Emits MUTATION pheromones during thermodynamic evolution cycles.
    Does NOT know about R-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "evolution"):
        self._field = field
        self._agent_id = agent_id

    def emit_mutation(
        self,
        mutation_id: str,
        fitness_delta: float,
        generation: int,
        position: FieldCoordinate,
        parent_id: str | None = None,
        mutation_type: str = "unknown",
        schema_signature: str = "",
        gibbs_energy: float = 0.0,
    ) -> str:
        """
        Emit a mutation signal.

        Called when E-gent discovers a successful mutation.
        """
        payload = MutationPayload(
            mutation_id=mutation_id,
            fitness_delta=fitness_delta,
            generation=generation,
            parent_id=parent_id,
            mutation_type=mutation_type,
            schema_signature=schema_signature,
            gibbs_energy=gibbs_energy,
        )

        # Intensity based on fitness improvement
        intensity = min(1.0, max(0.1, 0.5 + fitness_delta))

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.MUTATION,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "mutation_id": mutation_id,
                "generation": generation,
                "fitness_delta": fitness_delta,
            },
        )

    def emit_fitness_change(
        self,
        entity_id: str,
        old_fitness: float,
        new_fitness: float,
        position: FieldCoordinate,
        reason: str = "",
    ) -> str:
        """
        Emit a fitness change signal.

        Called when significant fitness changes occur.
        """
        payload = FitnessChangePayload(
            entity_id=entity_id,
            old_fitness=old_fitness,
            new_fitness=new_fitness,
            reason=reason,
        )

        delta = new_fitness - old_fitness
        intensity = min(1.0, max(0.1, abs(delta)))

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.MUTATION,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "entity_id": entity_id,
                "fitness_delta": delta,
                "signal_type": "fitness_change",
            },
        )

    def emit_cycle_complete(
        self,
        generation: int,
        best_fitness: float,
        population_size: int,
        position: FieldCoordinate,
        mutations_succeeded: int = 0,
        mutations_failed: int = 0,
        temperature: float = 1.0,
    ) -> str:
        """
        Emit a cycle completion signal.

        Called at the end of each thermodynamic evolution cycle.
        """
        payload = CycleCompletePayload(
            generation=generation,
            best_fitness=best_fitness,
            population_size=population_size,
            mutations_succeeded=mutations_succeeded,
            mutations_failed=mutations_failed,
            temperature=temperature,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.MUTATION,
            payload=payload,
            position=position,
            intensity=best_fitness,
            metadata={
                "generation": generation,
                "signal_type": "cycle_complete",
            },
        )


# =============================================================================
# Phase 1: H-gent Hegel Field Interface (SYNTHESIS signals)
# =============================================================================


@dataclass
class SynthesisPayload:
    """
    Payload for SYNTHESIS pheromones.

    Represents a dialectic synthesis from H-gent.
    """

    thesis: str
    antithesis: str
    synthesis: str
    confidence: float
    domain: str = ""
    resolution_type: str = ""  # "preserve", "negate", "elevate"


@dataclass
class ContradictionPayload:
    """
    Payload for contradiction detection.

    Emitted when H-gent detects unresolved contradictions.
    """

    statement_a: str
    statement_b: str
    severity: float  # 0.0 to 1.0
    tension_mode: str = ""  # "logical", "temporal", "contextual"
    description: str = ""


class HegelFieldEmitter:
    """
    H-gent's interface for emitting dialectic signals.

    Emits SYNTHESIS pheromones during dialectic operations.
    Does NOT know about Psi-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "hegel"):
        self._field = field
        self._agent_id = agent_id

    def emit_synthesis(
        self,
        thesis: str,
        antithesis: str,
        synthesis: str,
        confidence: float,
        position: FieldCoordinate,
        domain: str = "",
        resolution_type: str = "",
    ) -> str:
        """
        Emit a synthesis signal.

        Called when H-gent achieves a dialectic synthesis.
        """
        payload = SynthesisPayload(
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            confidence=confidence,
            domain=domain,
            resolution_type=resolution_type,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.SYNTHESIS,
            payload=payload,
            position=position,
            intensity=confidence,
            metadata={
                "domain": domain,
                "resolution_type": resolution_type,
                "signal_type": "synthesis",
            },
        )

    def emit_contradiction(
        self,
        statement_a: str,
        statement_b: str,
        severity: float,
        position: FieldCoordinate,
        tension_mode: str = "",
        description: str = "",
    ) -> str:
        """
        Emit a contradiction signal.

        Called when H-gent detects significant contradictions.
        This allows J-gent to sense potential safety issues.
        """
        payload = ContradictionPayload(
            statement_a=statement_a,
            statement_b=statement_b,
            severity=severity,
            tension_mode=tension_mode,
            description=description,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.SYNTHESIS,
            payload=payload,
            position=position,
            intensity=severity,
            metadata={
                "tension_mode": tension_mode,
                "signal_type": "contradiction",
            },
        )

    def emit_productive_tension(
        self,
        thesis: str,
        antithesis: str,
        why_held: str,
        position: FieldCoordinate,
    ) -> str:
        """
        Emit a productive tension signal.

        Called when H-gent decides synthesis is premature.
        """
        payload = {
            "thesis": thesis,
            "antithesis": antithesis,
            "why_held": why_held,
            "productive": True,
        }

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.SYNTHESIS,
            payload=payload,
            position=position,
            intensity=0.7,  # Productive tensions are significant
            metadata={
                "signal_type": "productive_tension",
            },
        )


# =============================================================================
# Phase 1: K-gent Persona Field Interface (PRIOR signals)
# =============================================================================


@dataclass
class PriorPayload:
    """
    Payload for PRIOR pheromones.

    Represents a persona preference/prior from K-gent.
    """

    prior_type: str  # "risk_tolerance", "time_preference", "creativity", etc.
    value: float  # 0.0 to 1.0 normalized value
    persona_id: str
    reason: str = ""
    confidence: float = 1.0


@dataclass
class PersonaShiftPayload:
    """
    Payload for persona shift signals.

    Emitted when K-gent's active persona changes.
    """

    old_persona: str | None
    new_persona: str
    trigger: str = ""  # What caused the shift


class PersonaFieldEmitter:
    """
    K-gent's interface for emitting persona/prior signals.

    Emits PRIOR pheromones to broadcast personality preferences.
    All agents can sense these to adapt their behavior.
    """

    def __init__(self, field: SemanticField, agent_id: str = "persona"):
        self._field = field
        self._agent_id = agent_id

    def emit_prior_change(
        self,
        prior_type: str,
        value: float,
        persona_id: str,
        position: FieldCoordinate,
        reason: str = "",
        confidence: float = 1.0,
    ) -> str:
        """
        Emit a prior change signal.

        Called when a persona preference is updated or asserted.
        """
        payload = PriorPayload(
            prior_type=prior_type,
            value=value,
            persona_id=persona_id,
            reason=reason,
            confidence=confidence,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.PRIOR,
            payload=payload,
            position=position,
            intensity=confidence,
            metadata={
                "prior_type": prior_type,
                "persona_id": persona_id,
            },
        )

    def emit_persona_shift(
        self,
        old_persona: str | None,
        new_persona: str,
        position: FieldCoordinate,
        trigger: str = "",
    ) -> str:
        """
        Emit a persona shift signal.

        Called when the active persona changes.
        """
        payload = PersonaShiftPayload(
            old_persona=old_persona,
            new_persona=new_persona,
            trigger=trigger,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.PRIOR,
            payload=payload,
            position=position,
            intensity=1.0,  # Persona shifts are high priority
            metadata={
                "old_persona": old_persona,
                "new_persona": new_persona,
                "signal_type": "persona_shift",
            },
        )

    def emit_preference(
        self,
        category: str,
        preference: str,
        strength: float,
        position: FieldCoordinate,
        persona_id: str = "default",
    ) -> str:
        """
        Emit a general preference signal.

        Convenience method for broadcasting preferences.
        """
        payload = {
            "category": category,
            "preference": preference,
            "strength": strength,
            "persona_id": persona_id,
        }

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.PRIOR,
            payload=payload,
            position=position,
            intensity=strength,
            metadata={
                "category": category,
                "signal_type": "preference",
            },
        )


# =============================================================================
# Phase 1: R-gent Refinery Field Interface (REFINEMENT signals)
# =============================================================================


@dataclass
class RefinementPayload:
    """
    Payload for REFINEMENT pheromones.

    Represents an optimization result from R-gent.
    """

    target_id: str
    improvement_type: str  # "compression", "optimization", "simplification"
    improvement_ratio: float  # > 1.0 means improvement
    before_metrics: dict[str, Any] = dataclass_field(default_factory=dict)
    after_metrics: dict[str, Any] = dataclass_field(default_factory=dict)


@dataclass
class RefinementOpportunityPayload:
    """
    Payload for refinement opportunity signals.

    Emitted when R-gent identifies potential improvements.
    """

    target_id: str
    potential_improvement: float  # Estimated improvement ratio
    strategy: str  # Recommended teleprompter strategy
    cost_estimate: float = 0.0  # Estimated cost in USD


class RefineryFieldEmitter:
    """
    R-gent's interface for emitting refinement signals.

    Emits REFINEMENT pheromones during optimization.
    Does NOT know about E-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "refinery"):
        self._field = field
        self._agent_id = agent_id

    def emit_refinement(
        self,
        target_id: str,
        improvement_type: str,
        improvement_ratio: float,
        position: FieldCoordinate,
        before_metrics: dict[str, Any] | None = None,
        after_metrics: dict[str, Any] | None = None,
    ) -> str:
        """
        Emit a refinement result signal.

        Called when R-gent completes an optimization.
        """
        payload = RefinementPayload(
            target_id=target_id,
            improvement_type=improvement_type,
            improvement_ratio=improvement_ratio,
            before_metrics=before_metrics or {},
            after_metrics=after_metrics or {},
        )

        # Intensity based on improvement ratio
        intensity = min(1.0, max(0.1, improvement_ratio - 0.5))

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.REFINEMENT,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "target_id": target_id,
                "improvement_type": improvement_type,
                "improvement_ratio": improvement_ratio,
            },
        )

    def emit_opportunity(
        self,
        target_id: str,
        potential_improvement: float,
        strategy: str,
        position: FieldCoordinate,
        cost_estimate: float = 0.0,
    ) -> str:
        """
        Emit a refinement opportunity signal.

        Called when R-gent identifies potential optimizations.
        """
        payload = RefinementOpportunityPayload(
            target_id=target_id,
            potential_improvement=potential_improvement,
            strategy=strategy,
            cost_estimate=cost_estimate,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.REFINEMENT,
            payload=payload,
            position=position,
            intensity=min(1.0, potential_improvement),
            metadata={
                "target_id": target_id,
                "strategy": strategy,
                "signal_type": "opportunity",
            },
        )

    def emit_optimization_trace(
        self,
        target_id: str,
        method: str,
        iterations: int,
        final_score: float,
        position: FieldCoordinate,
        converged: bool = False,
    ) -> str:
        """
        Emit an optimization trace signal.

        Called to broadcast optimization progress/results.
        """
        payload = {
            "target_id": target_id,
            "method": method,
            "iterations": iterations,
            "final_score": final_score,
            "converged": converged,
        }

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.REFINEMENT,
            payload=payload,
            position=position,
            intensity=final_score,
            metadata={
                "target_id": target_id,
                "method": method,
                "signal_type": "optimization_trace",
            },
        )


# =============================================================================
# Phase 2: Supporting Sensors
# =============================================================================


class EvolutionFieldSensor:
    """
    E-gent's sensor for detecting REFINEMENT signals from R-gent.

    E-gent senses refinement opportunities to inform evolutionary selection.
    R-gent improvements provide fitness hints for evolution.
    """

    def __init__(self, field: SemanticField, agent_id: str = "evolution_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_refinements(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[RefinementPayload]:
        """
        Sense nearby refinement signals.

        Returns refinement payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.REFINEMENT,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, RefinementPayload)]

    def sense_opportunities(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[RefinementOpportunityPayload]:
        """
        Sense refinement opportunities (not yet completed refinements).

        Returns opportunity payloads sorted by potential improvement.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.REFINEMENT,
        )

        return [
            p.payload for p in pheromones if isinstance(p.payload, RefinementOpportunityPayload)
        ]

    def sense_by_target(
        self,
        target_id: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[RefinementPayload]:
        """
        Sense refinements for a specific target.

        Useful for tracking optimization history of a specific entity.
        """
        refinements = self.sense_refinements(position, radius)
        return [r for r in refinements if r.target_id == target_id]

    def get_best_refinement(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        improvement_type: str | None = None,
    ) -> RefinementPayload | None:
        """
        Get the highest-improvement refinement.

        Optionally filter by improvement type.
        """
        refinements = self.sense_refinements(position, radius)
        if improvement_type:
            refinements = [r for r in refinements if r.improvement_type == improvement_type]
        if not refinements:
            return None
        return max(refinements, key=lambda r: r.improvement_ratio)


class RefineryFieldSensor:
    """
    R-gent's sensor for detecting MUTATION signals from E-gent.

    R-gent senses mutations to identify refinement candidates.
    E-gent discoveries trigger optimization opportunities.
    """

    def __init__(self, field: SemanticField, agent_id: str = "refinery_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_mutations(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[MutationPayload]:
        """
        Sense nearby mutation signals.

        Returns mutation payloads sorted by intensity (fitness delta).
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.MUTATION,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, MutationPayload)]

    def sense_fitness_changes(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[FitnessChangePayload]:
        """
        Sense fitness change signals.

        Returns fitness change payloads.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.MUTATION,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, FitnessChangePayload)]

    def sense_cycle_completions(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CycleCompletePayload]:
        """
        Sense evolution cycle completion signals.

        Returns cycle completion payloads.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.MUTATION,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, CycleCompletePayload)]

    def sense_positive_mutations(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        min_fitness_delta: float = 0.0,
    ) -> list[MutationPayload]:
        """
        Sense mutations with positive fitness delta.

        Useful for identifying successful mutations worth refining.
        """
        mutations = self.sense_mutations(position, radius)
        return [m for m in mutations if m.fitness_delta >= min_fitness_delta]

    def get_strongest_mutation(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> MutationPayload | None:
        """
        Get the mutation with highest fitness delta.
        """
        mutations = self.sense_mutations(position, radius)
        if not mutations:
            return None
        return max(mutations, key=lambda m: m.fitness_delta)


class PersonaFieldSensor:
    """
    K-gent's sensor for detecting SYNTHESIS signals from H-gent.

    K-gent senses dialectic syntheses to update personality priors.
    H-gent insights inform persona evolution.
    """

    def __init__(self, field: SemanticField, agent_id: str = "persona_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_syntheses(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[SynthesisPayload]:
        """
        Sense nearby synthesis signals.

        Returns synthesis payloads sorted by intensity (confidence).
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.SYNTHESIS,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, SynthesisPayload)]

    def sense_contradictions(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[ContradictionPayload]:
        """
        Sense contradiction signals.

        Returns contradiction payloads sorted by severity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.SYNTHESIS,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, ContradictionPayload)]

    def sense_by_domain(
        self,
        domain: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[SynthesisPayload]:
        """
        Sense syntheses in a specific domain.

        Useful for persona updates in specific areas.
        """
        syntheses = self.sense_syntheses(position, radius)
        return [s for s in syntheses if s.domain == domain]

    def get_high_confidence_syntheses(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        min_confidence: float = 0.7,
    ) -> list[SynthesisPayload]:
        """
        Get syntheses with confidence above threshold.

        High confidence syntheses are more likely to inform priors.
        """
        syntheses = self.sense_syntheses(position, radius)
        return [s for s in syntheses if s.confidence >= min_confidence]

    def get_strongest_synthesis(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> SynthesisPayload | None:
        """
        Get the synthesis with highest confidence.
        """
        syntheses = self.sense_syntheses(position, radius)
        if not syntheses:
            return None
        return max(syntheses, key=lambda s: s.confidence)


class HegelFieldSensor:
    """
    H-gent's sensor for detecting PRIOR signals from K-gent.

    H-gent senses persona priors to guide dialectic operations.
    K-gent preferences inform which contradictions to prioritize.
    """

    def __init__(self, field: SemanticField, agent_id: str = "hegel_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_priors(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[PriorPayload]:
        """
        Sense nearby prior signals.

        Returns prior payloads sorted by intensity (confidence).
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.PRIOR,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, PriorPayload)]

    def sense_persona_shifts(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[PersonaShiftPayload]:
        """
        Sense persona shift signals.

        Returns persona shift payloads.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.PRIOR,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, PersonaShiftPayload)]

    def sense_by_prior_type(
        self,
        prior_type: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[PriorPayload]:
        """
        Sense priors of a specific type.

        E.g., sense all "risk_tolerance" priors.
        """
        priors = self.sense_priors(position, radius)
        return [p for p in priors if p.prior_type == prior_type]

    def sense_by_persona(
        self,
        persona_id: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[PriorPayload]:
        """
        Sense priors from a specific persona.
        """
        priors = self.sense_priors(position, radius)
        return [p for p in priors if p.persona_id == persona_id]

    def get_active_persona(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> str | None:
        """
        Get the currently active persona from recent shifts.

        Returns the most recent new_persona from shift signals.
        """
        shifts = self.sense_persona_shifts(position, radius)
        if not shifts:
            return None
        # Return the most recent (highest intensity = most recent for shifts)
        return shifts[0].new_persona if shifts else None

    def get_prior_value(
        self,
        prior_type: str,
        position: FieldCoordinate,
        radius: float | None = None,
        default: float = 0.5,
    ) -> float:
        """
        Get the value of a specific prior type.

        Returns the highest confidence value, or default if not found.
        """
        priors = self.sense_by_prior_type(prior_type, position, radius)
        if not priors:
            return default
        # Return the highest confidence prior's value
        best = max(priors, key=lambda p: p.confidence)
        return best.value


# =============================================================================
# Factory Functions
# =============================================================================


def create_semantic_field() -> SemanticField:
    """Create a new semantic field."""
    return SemanticField()


def create_psi_emitter(field: SemanticField, agent_id: str = "psi") -> PsiFieldEmitter:
    """Create a Psi-gent field emitter."""
    return PsiFieldEmitter(field, agent_id)


def create_forge_sensor(field: SemanticField, agent_id: str = "forge") -> ForgeFieldSensor:
    """Create an F-gent field sensor."""
    return ForgeFieldSensor(field, agent_id)


def create_safety_emitter(field: SemanticField, agent_id: str = "judge") -> SafetyFieldEmitter:
    """Create a J-gent safety emitter."""
    return SafetyFieldEmitter(field, agent_id)


def create_economic_emitter(field: SemanticField, agent_id: str = "banker") -> EconomicFieldEmitter:
    """Create a B-gent economic emitter."""
    return EconomicFieldEmitter(field, agent_id)


def create_memory_emitter(field: SemanticField, agent_id: str = "memory") -> MemoryFieldEmitter:
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


def create_observer_sensor(field: SemanticField, agent_id: str = "observer") -> ObserverFieldSensor:
    """Create an O-gent observer sensor."""
    return ObserverFieldSensor(field, agent_id)


def create_catalog_emitter(field: SemanticField, agent_id: str = "catalog") -> CatalogFieldEmitter:
    """Create an L-gent catalog emitter."""
    return CatalogFieldEmitter(field, agent_id)


def create_catalog_sensor(
    field: SemanticField, agent_id: str = "catalog_sensor"
) -> CatalogFieldSensor:
    """Create an L-gent catalog sensor."""
    return CatalogFieldSensor(field, agent_id)


# Phase 1 Factory Functions


def create_evolution_emitter(
    field: SemanticField, agent_id: str = "evolution"
) -> EvolutionFieldEmitter:
    """Create an E-gent evolution emitter."""
    return EvolutionFieldEmitter(field, agent_id)


def create_hegel_emitter(field: SemanticField, agent_id: str = "hegel") -> HegelFieldEmitter:
    """Create an H-gent Hegel emitter."""
    return HegelFieldEmitter(field, agent_id)


def create_persona_emitter(field: SemanticField, agent_id: str = "persona") -> PersonaFieldEmitter:
    """Create a K-gent persona emitter."""
    return PersonaFieldEmitter(field, agent_id)


def create_refinery_emitter(
    field: SemanticField, agent_id: str = "refinery"
) -> RefineryFieldEmitter:
    """Create an R-gent refinery emitter."""
    return RefineryFieldEmitter(field, agent_id)


# Phase 2 Factory Functions (Supporting Sensors)


def create_evolution_sensor(
    field: SemanticField, agent_id: str = "evolution_sensor"
) -> EvolutionFieldSensor:
    """Create an E-gent evolution sensor (senses REFINEMENT)."""
    return EvolutionFieldSensor(field, agent_id)


def create_refinery_sensor(
    field: SemanticField, agent_id: str = "refinery_sensor"
) -> RefineryFieldSensor:
    """Create an R-gent refinery sensor (senses MUTATION)."""
    return RefineryFieldSensor(field, agent_id)


def create_persona_sensor(
    field: SemanticField, agent_id: str = "persona_sensor"
) -> PersonaFieldSensor:
    """Create a K-gent persona sensor (senses SYNTHESIS)."""
    return PersonaFieldSensor(field, agent_id)


def create_hegel_sensor(field: SemanticField, agent_id: str = "hegel_sensor") -> HegelFieldSensor:
    """Create an H-gent Hegel sensor (senses PRIOR)."""
    return HegelFieldSensor(field, agent_id)


# =============================================================================
# Phase 3: D-gent Data Field Interface (STATE signals)
# =============================================================================


@dataclass
class StatePayload:
    """
    Payload for STATE pheromones.

    Represents a data state change from D-gent.
    """

    entity_id: str
    state_type: str  # "created", "updated", "deleted", "stale"
    key: str
    old_value_hash: str | None = None
    new_value_hash: str | None = None
    store_id: str = ""  # Which data store


@dataclass
class StalePayload:
    """
    Payload for stale data signals.

    Emitted when D-gent detects stale or ghost data.
    """

    entity_id: str
    key: str
    last_accessed: str  # ISO timestamp
    staleness_score: float  # 0.0 (fresh) to 1.0 (very stale)
    recommended_action: str = ""  # "refresh", "delete", "archive"


class DataFieldEmitter:
    """
    D-gent's interface for emitting state change signals.

    Emits STATE pheromones for data lifecycle events.
    Does NOT know about M-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "data"):
        self._field = field
        self._agent_id = agent_id

    def emit_state_change(
        self,
        entity_id: str,
        state_type: str,
        key: str,
        position: FieldCoordinate,
        old_value_hash: str | None = None,
        new_value_hash: str | None = None,
        store_id: str = "",
    ) -> str:
        """
        Emit a state change signal.

        Called when D-gent observes data state transitions.
        """
        payload = StatePayload(
            entity_id=entity_id,
            state_type=state_type,
            key=key,
            old_value_hash=old_value_hash,
            new_value_hash=new_value_hash,
            store_id=store_id,
        )

        # Intensity based on state type (deletes are more important)
        intensity_map = {
            "created": 0.7,
            "updated": 0.5,
            "deleted": 0.9,
            "stale": 0.6,
        }
        intensity = intensity_map.get(state_type, 0.5)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.STATE,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "entity_id": entity_id,
                "state_type": state_type,
                "key": key,
            },
        )

    def emit_created(
        self,
        entity_id: str,
        key: str,
        position: FieldCoordinate,
        value_hash: str = "",
        store_id: str = "",
    ) -> str:
        """Convenience method for entity creation."""
        return self.emit_state_change(
            entity_id,
            "created",
            key,
            position,
            new_value_hash=value_hash,
            store_id=store_id,
        )

    def emit_updated(
        self,
        entity_id: str,
        key: str,
        position: FieldCoordinate,
        old_hash: str = "",
        new_hash: str = "",
        store_id: str = "",
    ) -> str:
        """Convenience method for entity updates."""
        return self.emit_state_change(
            entity_id,
            "updated",
            key,
            position,
            old_value_hash=old_hash,
            new_value_hash=new_hash,
            store_id=store_id,
        )

    def emit_deleted(
        self,
        entity_id: str,
        key: str,
        position: FieldCoordinate,
        old_hash: str = "",
        store_id: str = "",
    ) -> str:
        """Convenience method for entity deletion."""
        return self.emit_state_change(
            entity_id,
            "deleted",
            key,
            position,
            old_value_hash=old_hash,
            store_id=store_id,
        )

    def emit_stale(
        self,
        entity_id: str,
        key: str,
        last_accessed: str,
        staleness_score: float,
        position: FieldCoordinate,
        recommended_action: str = "",
    ) -> str:
        """
        Emit a stale data signal.

        Called when D-gent detects stale or ghost data.
        """
        payload = StalePayload(
            entity_id=entity_id,
            key=key,
            last_accessed=last_accessed,
            staleness_score=staleness_score,
            recommended_action=recommended_action,
        )

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.STATE,
            payload=payload,
            position=position,
            intensity=staleness_score,
            metadata={
                "entity_id": entity_id,
                "signal_type": "stale",
                "staleness_score": staleness_score,
            },
        )


class DataFieldSensor:
    """
    Sensor for STATE signals.

    Other agents can use this to react to data changes.
    """

    def __init__(self, field: SemanticField, agent_id: str = "data_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_state_changes(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[StatePayload]:
        """
        Sense nearby state change signals.

        Returns state payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.STATE,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, StatePayload)]

    def sense_by_state_type(
        self,
        state_type: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[StatePayload]:
        """
        Sense state changes of a specific type.

        E.g., sense all "deleted" events.
        """
        changes = self.sense_state_changes(position, radius)
        return [c for c in changes if c.state_type == state_type]

    def sense_by_entity(
        self,
        entity_id: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[StatePayload]:
        """
        Sense state changes for a specific entity.
        """
        changes = self.sense_state_changes(position, radius)
        return [c for c in changes if c.entity_id == entity_id]

    def sense_stale(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
        min_staleness: float = 0.0,
    ) -> list[StalePayload]:
        """
        Sense stale data signals.

        Returns stale payloads above the minimum staleness threshold.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.STATE,
        )

        return [
            p.payload
            for p in pheromones
            if isinstance(p.payload, StalePayload) and p.payload.staleness_score >= min_staleness
        ]

    def get_deletions(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[StatePayload]:
        """Get all deletion events (high priority)."""
        return self.sense_by_state_type("deleted", position, radius)


# =============================================================================
# Phase 3: T-gent Test Field Interface (TEST signals)
# =============================================================================


@dataclass
class TestResultPayload:
    """
    Payload for TEST pheromones.

    Represents a test result from T-gent.
    """

    test_id: str
    result: str  # "passed", "failed", "skipped", "error"
    duration_ms: float = 0.0
    affected_agents: tuple[str, ...] = ()
    error_message: str = ""
    test_file: str = ""


@dataclass
class CoverageChangePayload:
    """
    Payload for coverage change signals.

    Emitted when test coverage changes significantly.
    """

    old_coverage: float  # 0.0 to 1.0
    new_coverage: float
    delta: float  # Positive = improvement
    affected_files: tuple[str, ...] = ()


class TestFieldEmitter:
    """
    T-gent's interface for emitting test signals.

    Emits TEST pheromones for test results and coverage changes.
    Does NOT know about O-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "test"):
        self._field = field
        self._agent_id = agent_id

    def emit_test_result(
        self,
        test_id: str,
        result: str,
        position: FieldCoordinate,
        duration_ms: float = 0.0,
        affected_agents: tuple[str, ...] = (),
        error_message: str = "",
        test_file: str = "",
    ) -> str:
        """
        Emit a test result signal.

        Called when T-gent completes a test run.
        """
        payload = TestResultPayload(
            test_id=test_id,
            result=result,
            duration_ms=duration_ms,
            affected_agents=affected_agents,
            error_message=error_message,
            test_file=test_file,
        )

        # Intensity based on result (failures are more important)
        intensity_map = {
            "passed": 0.3,
            "skipped": 0.2,
            "failed": 0.9,
            "error": 1.0,
        }
        intensity = intensity_map.get(result, 0.5)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.TEST,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "test_id": test_id,
                "result": result,
                "test_file": test_file,
            },
        )

    def emit_coverage_change(
        self,
        old_coverage: float,
        new_coverage: float,
        position: FieldCoordinate,
        affected_files: tuple[str, ...] = (),
    ) -> str:
        """
        Emit a coverage change signal.

        Called when test coverage changes significantly.
        """
        delta = new_coverage - old_coverage
        payload = CoverageChangePayload(
            old_coverage=old_coverage,
            new_coverage=new_coverage,
            delta=delta,
            affected_files=affected_files,
        )

        # Intensity based on coverage delta magnitude
        intensity = min(1.0, max(0.1, abs(delta) * 5))

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.TEST,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "signal_type": "coverage_change",
                "delta": delta,
            },
        )

    def emit_test_suite_complete(
        self,
        suite_id: str,
        passed: int,
        failed: int,
        skipped: int,
        total_duration_ms: float,
        position: FieldCoordinate,
    ) -> str:
        """
        Emit a test suite completion signal.

        Called when a full test suite completes.
        """
        total = passed + failed + skipped
        pass_rate = passed / total if total > 0 else 0.0

        payload = {
            "suite_id": suite_id,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": total,
            "pass_rate": pass_rate,
            "total_duration_ms": total_duration_ms,
        }

        # Intensity based on failure rate (more failures = higher intensity)
        failure_rate = failed / total if total > 0 else 0.0
        intensity = max(0.3, failure_rate)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.TEST,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "signal_type": "suite_complete",
                "suite_id": suite_id,
                "pass_rate": pass_rate,
            },
        )


class TestFieldSensor:
    """
    Sensor for TEST signals.

    Other agents can use this to react to test results.
    """

    def __init__(self, field: SemanticField, agent_id: str = "test_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_test_results(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[TestResultPayload]:
        """
        Sense nearby test result signals.

        Returns test result payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.TEST,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, TestResultPayload)]

    def sense_failures(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[TestResultPayload]:
        """
        Sense test failures specifically.

        Returns failed and error test results.
        """
        results = self.sense_test_results(position, radius)
        return [r for r in results if r.result in ("failed", "error")]

    def sense_by_affected_agent(
        self,
        agent_id: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[TestResultPayload]:
        """
        Sense test results affecting a specific agent.
        """
        results = self.sense_test_results(position, radius)
        return [r for r in results if agent_id in r.affected_agents]

    def sense_coverage_changes(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CoverageChangePayload]:
        """
        Sense coverage change signals.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.TEST,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, CoverageChangePayload)]

    def get_coverage_regressions(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[CoverageChangePayload]:
        """
        Get coverage changes where coverage decreased.
        """
        changes = self.sense_coverage_changes(position, radius)
        return [c for c in changes if c.delta < 0]

    def has_failures(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> bool:
        """Check if there are any test failures in the field."""
        return len(self.sense_failures(position, radius)) > 0


# =============================================================================
# Phase 3: W-gent Wire Field Interface (DISPATCH signals)
# =============================================================================


@dataclass
class DispatchPayload:
    """
    Payload for DISPATCH pheromones.

    Represents a message routing event from W-gent.
    """

    message_id: str
    source: str
    target: str
    intercepted_by: tuple[str, ...] = ()
    latency_ms: float = 0.0
    message_type: str = ""


@dataclass
class BlockedPayload:
    """
    Payload for blocked message signals.

    Emitted when W-gent blocks a message.
    """

    message_id: str
    blocker: str
    reason: str
    source: str = ""
    target: str = ""
    severity: str = "warning"  # "info", "warning", "error"


class WireFieldEmitter:
    """
    W-gent's interface for emitting dispatch signals.

    Emits DISPATCH pheromones for message routing events.
    Does NOT know about J-gent or any consumer.
    """

    def __init__(self, field: SemanticField, agent_id: str = "wire"):
        self._field = field
        self._agent_id = agent_id

    def emit_dispatch(
        self,
        message_id: str,
        source: str,
        target: str,
        position: FieldCoordinate,
        intercepted_by: tuple[str, ...] = (),
        latency_ms: float = 0.0,
        message_type: str = "",
    ) -> str:
        """
        Emit a dispatch signal.

        Called when W-gent routes a message.
        """
        payload = DispatchPayload(
            message_id=message_id,
            source=source,
            target=target,
            intercepted_by=intercepted_by,
            latency_ms=latency_ms,
            message_type=message_type,
        )

        # Intensity based on number of interceptors (more = more interesting)
        base_intensity = 0.3
        interceptor_boost = len(intercepted_by) * 0.1
        intensity = min(1.0, base_intensity + interceptor_boost)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.DISPATCH,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "message_id": message_id,
                "source": source,
                "target": target,
            },
        )

    def emit_blocked(
        self,
        message_id: str,
        blocker: str,
        reason: str,
        position: FieldCoordinate,
        source: str = "",
        target: str = "",
        severity: str = "warning",
    ) -> str:
        """
        Emit a blocked message signal.

        Called when W-gent blocks a message.
        """
        payload = BlockedPayload(
            message_id=message_id,
            blocker=blocker,
            reason=reason,
            source=source,
            target=target,
            severity=severity,
        )

        # Intensity based on severity
        severity_intensity = {
            "info": 0.4,
            "warning": 0.7,
            "error": 1.0,
        }
        intensity = severity_intensity.get(severity, 0.5)

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.DISPATCH,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "message_id": message_id,
                "blocker": blocker,
                "signal_type": "blocked",
                "severity": severity,
            },
        )

    def emit_routing_latency(
        self,
        route_id: str,
        source: str,
        target: str,
        latency_ms: float,
        position: FieldCoordinate,
        is_slow: bool = False,
    ) -> str:
        """
        Emit a routing latency signal.

        Called to report message routing performance.
        """
        payload = {
            "route_id": route_id,
            "source": source,
            "target": target,
            "latency_ms": latency_ms,
            "is_slow": is_slow,
        }

        # Higher intensity for slow routes
        intensity = 0.8 if is_slow else 0.3

        return self._field.emit(
            emitter=self._agent_id,
            kind=SemanticPheromoneKind.DISPATCH,
            payload=payload,
            position=position,
            intensity=intensity,
            metadata={
                "signal_type": "latency",
                "is_slow": is_slow,
            },
        )


class WireFieldSensor:
    """
    Sensor for DISPATCH signals.

    Other agents can use this to monitor message routing.
    """

    def __init__(self, field: SemanticField, agent_id: str = "wire_sensor"):
        self._field = field
        self._agent_id = agent_id

    def sense_dispatches(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[DispatchPayload]:
        """
        Sense nearby dispatch signals.

        Returns dispatch payloads sorted by intensity.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.DISPATCH,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, DispatchPayload)]

    def sense_blocked(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[BlockedPayload]:
        """
        Sense blocked message signals.
        """
        pheromones = self._field.sense(
            position=position,
            radius=radius,
            kind=SemanticPheromoneKind.DISPATCH,
        )

        return [p.payload for p in pheromones if isinstance(p.payload, BlockedPayload)]

    def sense_by_source(
        self,
        source: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[DispatchPayload]:
        """
        Sense dispatches from a specific source.
        """
        dispatches = self.sense_dispatches(position, radius)
        return [d for d in dispatches if d.source == source]

    def sense_by_target(
        self,
        target: str,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[DispatchPayload]:
        """
        Sense dispatches to a specific target.
        """
        dispatches = self.sense_dispatches(position, radius)
        return [d for d in dispatches if d.target == target]

    def sense_intercepted(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> list[DispatchPayload]:
        """
        Sense dispatches that were intercepted.
        """
        dispatches = self.sense_dispatches(position, radius)
        return [d for d in dispatches if d.intercepted_by]

    def get_blockers(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> set[str]:
        """
        Get unique set of blockers in the field.
        """
        blocked = self.sense_blocked(position, radius)
        return {b.blocker for b in blocked}

    def has_blocks(
        self,
        position: FieldCoordinate,
        radius: float | None = None,
    ) -> bool:
        """Check if there are any blocked messages in the field."""
        return len(self.sense_blocked(position, radius)) > 0


# Phase 3 Factory Functions


def create_data_emitter(field: SemanticField, agent_id: str = "data") -> DataFieldEmitter:
    """Create a D-gent data emitter."""
    return DataFieldEmitter(field, agent_id)


def create_data_sensor(field: SemanticField, agent_id: str = "data_sensor") -> DataFieldSensor:
    """Create a D-gent data sensor."""
    return DataFieldSensor(field, agent_id)


def create_test_emitter(field: SemanticField, agent_id: str = "test") -> TestFieldEmitter:
    """Create a T-gent test emitter."""
    return TestFieldEmitter(field, agent_id)


def create_test_sensor(field: SemanticField, agent_id: str = "test_sensor") -> TestFieldSensor:
    """Create a T-gent test sensor."""
    return TestFieldSensor(field, agent_id)


def create_wire_emitter(field: SemanticField, agent_id: str = "wire") -> WireFieldEmitter:
    """Create a W-gent wire emitter."""
    return WireFieldEmitter(field, agent_id)


def create_wire_sensor(field: SemanticField, agent_id: str = "wire_sensor") -> WireFieldSensor:
    """Create a W-gent wire sensor."""
    return WireFieldSensor(field, agent_id)
