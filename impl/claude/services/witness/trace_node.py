"""
TraceNode: The Atomic Unit of Execution Artifact.

Every action in kgents emits a TraceNode. TraceNodes are:
- Immutable (frozen=True) — Law 1
- Causally linked — Law 2: target.timestamp > source.timestamp
- Complete — Law 3: Every AGENTESE invocation emits exactly one TraceNode

The Insight (from spec/protocols/warp-primitives.md):
    "Every action is a TraceNode. Every session is a Walk. Every workflow is a Ritual."

Philosophy:
    TraceNodes extend the Thought pattern from polynomial.py with:
    - Causal links (TraceLink) for tracing execution flow
    - N-Phase binding for workflow context
    - Umwelt snapshots for observer-dependent perception

See: spec/protocols/warp-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType
from uuid import uuid4

if TYPE_CHECKING:
    from protocols.nphase.schema import PhaseStatus

# =============================================================================
# Type Aliases
# =============================================================================

TraceNodeId = NewType("TraceNodeId", str)
PlanPath = NewType("PlanPath", str)  # e.g., "plans/warp-servo-phase1.md"
WalkId = NewType("WalkId", str)


def generate_trace_id() -> TraceNodeId:
    """Generate a unique TraceNode ID."""
    return TraceNodeId(f"trace-{uuid4().hex[:12]}")


# =============================================================================
# Link Relations (Causal Edges)
# =============================================================================


class LinkRelation(Enum):
    """
    Types of causal relationships between TraceNodes.

    The four relations:
    - CAUSES: This node directly caused the target (stimulus → response)
    - CONTINUES: This node continues work started by source (continuation)
    - BRANCHES: This node branches from source (parallel exploration)
    - FULFILLS: This node fulfills an intent declared in source (completion)
    """

    CAUSES = auto()  # Direct causation: A caused B
    CONTINUES = auto()  # Continuation: A leads to B in same thread
    BRANCHES = auto()  # Branching: B is a parallel exploration from A
    FULFILLS = auto()  # Fulfillment: B completes intent declared in A


@dataclass(frozen=True)
class TraceLink:
    """
    Causal edge between TraceNodes or to plans.

    Laws:
    - Law 2 (Causality): If source is TraceNode, target.timestamp > source.timestamp
    - Links are immutable once created

    Example:
        >>> link = TraceLink(
        ...     source=TraceNodeId("trace-abc"),
        ...     target=TraceNodeId("trace-def"),
        ...     relation=LinkRelation.CAUSES,
        ... )
    """

    source: TraceNodeId | PlanPath  # Can link from node or plan
    target: TraceNodeId
    relation: LinkRelation
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source": str(self.source),
            "target": str(self.target),
            "relation": self.relation.name,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraceLink:
        """Create from dictionary."""
        source_str = data["source"]
        # Detect if source is a plan path (ends with .md) or trace ID
        if source_str.endswith(".md") or source_str.startswith("plans/"):
            source: TraceNodeId | PlanPath = PlanPath(source_str)
        else:
            source = TraceNodeId(source_str)

        return cls(
            source=source,
            target=TraceNodeId(data["target"]),
            relation=LinkRelation[data["relation"]],
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# N-Phase Reference
# =============================================================================


class NPhase(Enum):
    """
    N-Phase workflow phases.

    Three-phase (compressed):
        SENSE → ACT → REFLECT

    Eleven-phase (full ceremony):
        PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS_SYNERGIZE
        → IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT

    TraceNodes can reference which phase they were emitted during.
    """

    # Compressed (3-phase)
    SENSE = "SENSE"
    ACT = "ACT"
    REFLECT = "REFLECT"

    # Full ceremony (11-phase)
    PLAN = "PLAN"
    RESEARCH = "RESEARCH"
    DEVELOP = "DEVELOP"
    STRATEGIZE = "STRATEGIZE"
    CROSS_SYNERGIZE = "CROSS-SYNERGIZE"
    IMPLEMENT = "IMPLEMENT"
    QA = "QA"
    TEST = "TEST"
    EDUCATE = "EDUCATE"
    MEASURE = "MEASURE"
    # REFLECT is shared with compressed

    @property
    def family(self) -> str:
        """Return the 3-phase family this phase belongs to."""
        sense_phases = {
            NPhase.SENSE,
            NPhase.PLAN,
            NPhase.RESEARCH,
            NPhase.DEVELOP,
            NPhase.STRATEGIZE,
            NPhase.CROSS_SYNERGIZE,
        }
        act_phases = {NPhase.ACT, NPhase.IMPLEMENT, NPhase.QA, NPhase.TEST, NPhase.EDUCATE}
        reflect_phases = {NPhase.REFLECT, NPhase.MEASURE}

        if self in sense_phases:
            return "SENSE"
        elif self in act_phases:
            return "ACT"
        elif self in reflect_phases:
            return "REFLECT"
        return "UNKNOWN"


# =============================================================================
# Umwelt Snapshot
# =============================================================================


@dataclass(frozen=True)
class UmweltSnapshot:
    """
    Snapshot of observer capabilities at TraceNode emission time.

    Captures what the observer could perceive and do when this trace was created.
    This enables replay with context: "What did the agent know at this moment?"

    Fields:
    - observer_id: Who was observing (agent, human, jewel)
    - role: Observer role (from GestaltUmwelt or trust level)
    - capabilities: What actions were permitted
    - perceptions: What was visible to the observer
    - trust_level: Trust level at emission (L0-L3 from Witness)
    """

    observer_id: str
    role: str = "developer"  # tech_lead, developer, reviewer, etc.
    capabilities: frozenset[str] = field(default_factory=frozenset)
    perceptions: frozenset[str] = field(default_factory=frozenset)
    trust_level: int = 0  # 0=READ_ONLY, 1=BOUNDED, 2=SUGGESTION, 3=AUTONOMOUS

    @classmethod
    def system(cls) -> UmweltSnapshot:
        """Create a system-level umwelt (full capabilities)."""
        return cls(
            observer_id="system",
            role="system",
            capabilities=frozenset({"read", "write", "execute", "observe"}),
            perceptions=frozenset({"all"}),
            trust_level=3,
        )

    @classmethod
    def witness(cls, trust_level: int = 0) -> UmweltSnapshot:
        """Create a Witness umwelt with specified trust level."""
        caps = frozenset({"observe"})
        if trust_level >= 1:
            caps = caps | frozenset({"write_kgents"})
        if trust_level >= 2:
            caps = caps | frozenset({"suggest"})
        if trust_level >= 3:
            caps = caps | frozenset({"execute"})

        return cls(
            observer_id="witness",
            role="witness",
            capabilities=caps,
            perceptions=frozenset({"git", "filesystem", "tests", "agentese", "ci"}),
            trust_level=trust_level,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "observer_id": self.observer_id,
            "role": self.role,
            "capabilities": list(self.capabilities),
            "perceptions": list(self.perceptions),
            "trust_level": self.trust_level,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UmweltSnapshot:
        """Create from dictionary."""
        return cls(
            observer_id=data.get("observer_id", "unknown"),
            role=data.get("role", "developer"),
            capabilities=frozenset(data.get("capabilities", [])),
            perceptions=frozenset(data.get("perceptions", [])),
            trust_level=data.get("trust_level", 0),
        )


# =============================================================================
# Stimulus and Response
# =============================================================================


@dataclass(frozen=True)
class Stimulus:
    """
    What triggered the TraceNode.

    Can be:
    - User prompt
    - AGENTESE invocation
    - Event from watcher (git, file, test, CI)
    - Timer or schedule
    """

    kind: str  # "prompt", "agentese", "git", "file", "test", "ci", "timer"
    content: str  # The actual stimulus content
    source: str = ""  # Where it came from
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_agentese(cls, path: str, aspect: str, **kwargs: Any) -> Stimulus:
        """Create stimulus from AGENTESE invocation."""
        return cls(
            kind="agentese",
            content=f"{path}.{aspect}",
            source="agentese",
            metadata={"path": path, "aspect": aspect, **kwargs},
        )

    @classmethod
    def from_prompt(cls, prompt: str, source: str = "user") -> Stimulus:
        """Create stimulus from user prompt."""
        return cls(kind="prompt", content=prompt, source=source)

    @classmethod
    def from_event(cls, event_type: str, content: str, source: str) -> Stimulus:
        """Create stimulus from watcher event."""
        return cls(kind=event_type, content=content, source=source)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "kind": self.kind,
            "content": self.content,
            "source": self.source,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Stimulus:
        """Create from dictionary."""
        return cls(
            kind=data.get("kind", "unknown"),
            content=data.get("content", ""),
            source=data.get("source", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class Response:
    """
    What the TraceNode produced.

    Can be:
    - Text output
    - State transition
    - File modification
    - AGENTESE projection
    """

    kind: str  # "text", "state", "file", "projection", "thought"
    content: str
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def thought(cls, content: str, tags: tuple[str, ...] = ()) -> Response:
        """Create response from Witness thought."""
        return cls(
            kind="thought",
            content=content,
            success=True,
            metadata={"tags": list(tags)},
        )

    @classmethod
    def projection(cls, path: str, target: str = "cli") -> Response:
        """Create response from AGENTESE projection."""
        return cls(
            kind="projection",
            content=f"Projected {path} to {target}",
            success=True,
            metadata={"path": path, "target": target},
        )

    @classmethod
    def error(cls, message: str) -> Response:
        """Create error response."""
        return cls(kind="error", content=message, success=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "kind": self.kind,
            "content": self.content,
            "success": self.success,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        """Create from dictionary."""
        return cls(
            kind=data.get("kind", "unknown"),
            content=data.get("content", ""),
            success=data.get("success", True),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# TraceNode: The Atomic Unit
# =============================================================================


@dataclass(frozen=True)
class TraceNode:
    """
    Atomic unit of execution artifact.

    Laws:
    - Law 1 (Immutability): TraceNodes are frozen after creation
    - Law 2 (Causality): link.target.timestamp > link.source.timestamp
    - Law 3 (Completeness): Every AGENTESE invocation emits exactly one TraceNode

    A TraceNode captures:
    - WHAT triggered it (stimulus)
    - WHAT it produced (response)
    - WHO observed it (umwelt)
    - WHEN it happened (timestamp)
    - WHERE in the workflow (phase)
    - HOW it connects (links)

    Example:
        >>> node = TraceNode(
        ...     origin="witness",
        ...     stimulus=Stimulus.from_event("git", "Commit abc123", "git"),
        ...     response=Response.thought("Noticed commit abc123", ("git", "commit")),
        ...     umwelt=UmweltSnapshot.witness(trust_level=1),
        ... )
        >>> node.id  # "trace-abc123def456"
    """

    # Identity
    id: TraceNodeId = field(default_factory=generate_trace_id)

    # Origin (what/who emitted it)
    origin: str = "unknown"  # Jewel or agent name: "witness", "brain", "gardener", etc.

    # Content
    stimulus: Stimulus = field(default_factory=lambda: Stimulus(kind="unknown", content=""))
    response: Response = field(default_factory=lambda: Response(kind="unknown", content=""))

    # Observer context
    umwelt: UmweltSnapshot = field(default_factory=UmweltSnapshot.system)

    # Causal links (to other nodes or plans)
    links: tuple[TraceLink, ...] = ()

    # Temporal
    timestamp: datetime = field(default_factory=datetime.now)

    # N-Phase context (if within a workflow)
    phase: NPhase | None = None
    walk_id: WalkId | None = None  # If within a Walk

    # Metadata
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate causal links (Law 2 check deferred to store)."""
        # Note: We can't fully validate Law 2 here because we don't have
        # access to source node timestamps. The TraceNodeStore enforces this.
        pass

    @classmethod
    def from_thought(
        cls,
        content: str,
        source: str,
        tags: tuple[str, ...] = (),
        origin: str = "witness",
        trust_level: int = 0,
        phase: NPhase | None = None,
    ) -> TraceNode:
        """
        Create TraceNode from Witness Thought pattern.

        This is the primary upgrade path from the existing Thought type.
        """
        return cls(
            origin=origin,
            stimulus=Stimulus.from_event(source, f"Event from {source}", source),
            response=Response.thought(content, tags),
            umwelt=UmweltSnapshot.witness(trust_level),
            phase=phase,
            tags=tags,
        )

    @classmethod
    def from_agentese(
        cls,
        path: str,
        aspect: str,
        response_content: str,
        origin: str = "logos",
        umwelt: UmweltSnapshot | None = None,
        phase: NPhase | None = None,
        **kwargs: Any,
    ) -> TraceNode:
        """Create TraceNode from AGENTESE invocation."""
        return cls(
            origin=origin,
            stimulus=Stimulus.from_agentese(path, aspect, **kwargs),
            response=Response.projection(f"{path}.{aspect}"),
            umwelt=umwelt or UmweltSnapshot.system(),
            phase=phase,
            metadata={"agentese_path": path, "aspect": aspect, **kwargs},
        )

    def with_link(self, link: TraceLink) -> TraceNode:
        """Return new TraceNode with added link (immutable pattern)."""
        # Create new frozen instance with updated links
        return TraceNode(
            id=self.id,
            origin=self.origin,
            stimulus=self.stimulus,
            response=self.response,
            umwelt=self.umwelt,
            links=self.links + (link,),
            timestamp=self.timestamp,
            phase=self.phase,
            walk_id=self.walk_id,
            tags=self.tags,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "origin": self.origin,
            "stimulus": self.stimulus.to_dict(),
            "response": self.response.to_dict(),
            "umwelt": self.umwelt.to_dict(),
            "links": [link.to_dict() for link in self.links],
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase.value if self.phase else None,
            "walk_id": str(self.walk_id) if self.walk_id else None,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraceNode:
        """Create from dictionary."""
        phase = NPhase(data["phase"]) if data.get("phase") else None

        return cls(
            id=TraceNodeId(data["id"]),
            origin=data.get("origin", "unknown"),
            stimulus=Stimulus.from_dict(data.get("stimulus", {})),
            response=Response.from_dict(data.get("response", {})),
            umwelt=UmweltSnapshot.from_dict(data.get("umwelt", {})),
            links=tuple(TraceLink.from_dict(link) for link in data.get("links", [])),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            phase=phase,
            walk_id=WalkId(data["walk_id"]) if data.get("walk_id") else None,
            tags=tuple(data.get("tags", [])),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        phase_str = f", phase={self.phase.value}" if self.phase else ""
        return (
            f"TraceNode(id={str(self.id)[:8]}..., "
            f"origin={self.origin}, "
            f"stimulus={self.stimulus.kind}{phase_str})"
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "TraceNodeId",
    "PlanPath",
    "WalkId",
    "generate_trace_id",
    # Link types
    "LinkRelation",
    "TraceLink",
    # Phase
    "NPhase",
    # Umwelt
    "UmweltSnapshot",
    # Stimulus/Response
    "Stimulus",
    "Response",
    # Core
    "TraceNode",
]
