"""
Mark: The Atomic Unit of Execution Artifact.

Every action in kgents emits a Mark. Marks are:
- Immutable (frozen=True) — Law 1
- Causally linked — Law 2: target.timestamp > source.timestamp
- Complete — Law 3: Every AGENTESE invocation emits exactly one Mark

The Insight (from spec/protocols/witness-primitives.md):
    "Every action leaves a mark. Every mark joins a walk. Every walk follows a playbook."

Philosophy:
    Marks extend the Thought pattern from polynomial.py with:
    - Causal links (MarkLink) for tracing execution flow
    - N-Phase binding for workflow context
    - Umwelt snapshots for observer-dependent perception

See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)

Teaching:
    gotcha: Marks are IMMUTABLE (frozen=True). You cannot modify a Mark after
            creation. To "update" metadata, create a new Mark linked via CONTINUES
            relation to the original.
            (Evidence: test_trace_node.py::test_mark_immutability)

    gotcha: MarkLink.source can be MarkId OR PlanPath. This allows linking marks
            to Forest plan files directly. When traversing links, check the type
            before assuming you have a MarkId.
            (Evidence: test_session_walk.py::TestForestIntegration::test_walk_with_root_plan)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType
from uuid import uuid4

if TYPE_CHECKING:
    from protocols.nphase.schema import PhaseStatus
    from services.categorical.dp_bridge import TraceEntry

# =============================================================================
# Type Aliases
# =============================================================================

MarkId = NewType("MarkId", str)
PlanPath = NewType("PlanPath", str)  # e.g., "plans/witness-phase1.md"
WalkId = NewType("WalkId", str)

# Domain categorization for frontend routing and filtering
WitnessDomain = str  # Literal values: "navigation", "portal", "chat", "edit", "system"


# =============================================================================
# Constitutional Alignment (Phase 1: Witness as Constitutional Enforcement)
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalAlignment:
    """
    Constitutional metadata preserved through compression.

    Every Mark can carry constitutional alignment scores, tracking how well
    the action it represents adheres to the 7 constitutional principles.

    Philosophy:
        "Constitutional Compliance = 1 - Galois Loss"

        This is the atomic unit of constitutional tracking. When Marks are
        compressed into Crystals, constitutional metadata is preserved and
        aggregated (see ConstitutionalCrystalMeta in crystal.py).

    Integration:
        - Created by MarkConstitutionalEvaluator when a Mark is emitted
        - Preserved through Crystal compression hierarchy
        - Used by ConstitutionalTrustComputer to compute trust levels
        - Displayed in ConstitutionalDashboard on frontend

    The Seven Principles (with weights):
        - ETHICAL: 2.0 (safety first)
        - COMPOSABLE: 1.5 (architecture second)
        - JOY_INDUCING: 1.2 (Kent's aesthetic)
        - TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE: 1.0 each

    Example:
        >>> alignment = ConstitutionalAlignment.from_evaluation(eval)
        >>> print(f"Total: {alignment.weighted_total:.2f}")
        >>> print(f"Compliant: {alignment.is_compliant}")
    """

    # Per-principle scores (0.0 - 1.0)
    principle_scores: dict[str, float]

    # Weighted total (Σ(wᵢ × scoreᵢ) / Σwᵢ)
    weighted_total: float

    # Optional Galois loss for regenerability tracking
    galois_loss: float | None = None

    # Evidence tier (from Proof system)
    tier: str = "EMPIRICAL"  # CATEGORICAL, EMPIRICAL, AESTHETIC, GENEALOGICAL, SOMATIC

    # Compliance threshold (configurable, default 0.5)
    threshold: float = 0.5

    @property
    def is_compliant(self) -> bool:
        """Check if all principles meet minimum threshold."""
        return all(score >= self.threshold for score in self.principle_scores.values())

    @property
    def dominant_principle(self) -> str:
        """Return the highest-scoring principle."""
        if not self.principle_scores:
            return "unknown"
        return max(self.principle_scores.keys(), key=lambda p: self.principle_scores[p])

    @property
    def weakest_principle(self) -> str:
        """Return the lowest-scoring principle (bottleneck)."""
        if not self.principle_scores:
            return "unknown"
        return min(self.principle_scores.keys(), key=lambda p: self.principle_scores[p])

    @property
    def violation_count(self) -> int:
        """Count principles below threshold."""
        return sum(1 for score in self.principle_scores.values() if score < self.threshold)

    @classmethod
    def from_scores(
        cls,
        principle_scores: dict[str, float],
        galois_loss: float | None = None,
        tier: str = "EMPIRICAL",
        threshold: float = 0.5,
    ) -> "ConstitutionalAlignment":
        """
        Create alignment from principle scores.

        Uses PRINCIPLE_WEIGHTS from constitution.py for weighted total.
        """
        # Default weights (from constitution.py)
        weights = {
            "ETHICAL": 2.0,
            "COMPOSABLE": 1.5,
            "JOY_INDUCING": 1.2,
            "TASTEFUL": 1.0,
            "CURATED": 1.0,
            "HETERARCHICAL": 1.0,
            "GENERATIVE": 1.0,
        }

        # Compute weighted total
        total = 0.0
        weight_sum = 0.0
        for principle, score in principle_scores.items():
            w = weights.get(principle.upper(), 1.0)
            total += score * w
            weight_sum += w

        weighted_total = total / weight_sum if weight_sum > 0 else 0.0

        return cls(
            principle_scores=principle_scores,
            weighted_total=weighted_total,
            galois_loss=galois_loss,
            tier=tier,
            threshold=threshold,
        )

    @classmethod
    def neutral(cls) -> "ConstitutionalAlignment":
        """Create a neutral alignment (all 0.5, no Galois loss)."""
        return cls.from_scores(
            principle_scores={
                "TASTEFUL": 0.5,
                "CURATED": 0.5,
                "ETHICAL": 0.5,
                "JOY_INDUCING": 0.5,
                "COMPOSABLE": 0.5,
                "HETERARCHICAL": 0.5,
                "GENERATIVE": 0.5,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "principle_scores": self.principle_scores,
            "weighted_total": self.weighted_total,
            "galois_loss": self.galois_loss,
            "tier": self.tier,
            "threshold": self.threshold,
            "is_compliant": self.is_compliant,
            "dominant_principle": self.dominant_principle,
            "weakest_principle": self.weakest_principle,
            "violation_count": self.violation_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstitutionalAlignment":
        """Create from dictionary."""
        return cls(
            principle_scores=data.get("principle_scores", {}),
            weighted_total=data.get("weighted_total", 0.0),
            galois_loss=data.get("galois_loss"),
            tier=data.get("tier", "EMPIRICAL"),
            threshold=data.get("threshold", 0.5),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        status = "✓" if self.is_compliant else f"✗({self.violation_count})"
        return f"ConstitutionalAlignment(total={self.weighted_total:.2f}, {status})"

# Backwards compatibility aliases (remove after migration complete)
MarkId = MarkId


def generate_mark_id() -> MarkId:
    """Generate a unique Mark ID."""
    return MarkId(f"mark-{uuid4().hex[:12]}")


# Backwards compatibility alias
generate_mark_id = generate_mark_id


# =============================================================================
# Link Relations (Causal Edges)
# =============================================================================


class LinkRelation(Enum):
    """
    Types of causal relationships between Marks.

    The four relations:
    - CAUSES: This mark directly caused the target (stimulus → response)
    - CONTINUES: This mark continues work started by source (continuation)
    - BRANCHES: This mark branches from source (parallel exploration)
    - FULFILLS: This mark fulfills an intent declared in source (completion)
    """

    CAUSES = auto()  # Direct causation: A caused B
    CONTINUES = auto()  # Continuation: A leads to B in same thread
    BRANCHES = auto()  # Branching: B is a parallel exploration from A
    FULFILLS = auto()  # Fulfillment: B completes intent declared in A


@dataclass(frozen=True)
class MarkLink:
    """
    Causal edge between Marks or to plans.

    Laws:
    - Law 2 (Causality): If source is Mark, target.timestamp > source.timestamp
    - Links are immutable once created

    Example:
        >>> link = MarkLink(
        ...     source=MarkId("mark-abc"),
        ...     target=MarkId("mark-def"),
        ...     relation=LinkRelation.CAUSES,
        ... )
    """

    source: MarkId | PlanPath  # Can link from mark or plan
    target: MarkId
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
    def from_dict(cls, data: dict[str, Any]) -> MarkLink:
        """Create from dictionary."""
        source_str = data["source"]
        # Detect if source is a plan path (ends with .md) or mark ID
        if source_str.endswith(".md") or source_str.startswith("plans/"):
            source: MarkId | PlanPath = PlanPath(source_str)
        else:
            source = MarkId(source_str)

        return cls(
            source=source,
            target=MarkId(data["target"]),
            relation=LinkRelation[data["relation"]],
            metadata=data.get("metadata", {}),
        )


# Backwards compatibility alias
MarkLink = MarkLink


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

    Marks can reference which phase they were emitted during.
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
    Snapshot of observer capabilities at Mark emission time.

    Captures what the observer could perceive and do when this mark was created.
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
    What triggered the Mark.

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
    What the Mark produced.

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
# Evidence Tier (Hierarchy of Justification)
# =============================================================================


class EvidenceTier(Enum):
    """
    Hierarchy of evidence types for justification.

    From spec/protocols/witness-supersession.md:
        CATEGORICAL = 1     # Mathematical (laws hold)
        EMPIRICAL = 2       # Scientific (ASHC runs)
        AESTHETIC = 3       # Hardy criteria (inevitability, unexpectedness, economy)
        GENEALOGICAL = 4    # Pattern archaeology (git history)
        SOMATIC = 5         # The Mirror Test (felt sense)

    Higher tiers are more subjective but may trump lower tiers in human systems.
    """

    CATEGORICAL = 1  # Mathematical: proofs, laws, invariants
    EMPIRICAL = 2  # Scientific: tests, benchmarks, measurements
    AESTHETIC = 3  # Hardy: inevitability, unexpectedness, economy
    GENEALOGICAL = 4  # Archaeology: git history, pattern evolution
    SOMATIC = 5  # Mirror Test: "Does this feel like me on my best day?"


# =============================================================================
# Proof: Toulmin Argumentation Structure
# =============================================================================


@dataclass(frozen=True)
class Proof:
    """
    Defeasible reasoning structure based on Toulmin's argumentation model.

    From spec/protocols/witness-supersession.md:
        "The proof IS the decision. The mark IS the witness."

    Toulmin's model captures how humans actually argue, not just formal logic:
    - data: The evidence supporting the claim
    - warrant: The reasoning connecting data to claim
    - claim: The conclusion being argued for
    - backing: Support for the warrant itself
    - qualifier: Degree of certainty ("definitely", "probably", "possibly")
    - rebuttals: Conditions that would defeat the argument

    Why Toulmin?
        - Captures defeasibility (can be overridden by new evidence)
        - Models real human reasoning patterns
        - Enables AI-human dialectical fusion
        - Supports Article III: Supersession Rights

    Example:
        >>> proof = Proof(
        ...     data="3 hours, 45K tokens invested",
        ...     warrant="Infrastructure investment enables future velocity",
        ...     claim="This refactoring was worthwhile",
        ...     backing="CLAUDE.md: 'DI > mocking' pattern saves 30% test time",
        ...     qualifier="almost certainly",
        ...     rebuttals=("unless the API changes completely",),
        ...     tier=EvidenceTier.EMPIRICAL,
        ... )
    """

    # Core Toulmin structure
    data: str  # Evidence: "Tests pass", "3 hours invested", "Pattern X found in git"
    warrant: str  # Reasoning: "Passing tests indicate correctness"
    claim: str  # Conclusion: "This refactoring was worthwhile"

    # Extended Toulmin
    backing: str = ""  # Support for warrant: "CLAUDE.md says X"
    qualifier: str = "probably"  # Confidence: "definitely", "probably", "possibly"
    rebuttals: tuple[str, ...] = ()  # Defeaters: "unless API changes"

    # Evidence tier (from spec)
    tier: EvidenceTier = EvidenceTier.EMPIRICAL

    # Principles referenced (from Constitution)
    principles: tuple[str, ...] = ()  # e.g., ("composable", "generative")

    @classmethod
    def categorical(
        cls,
        data: str,
        warrant: str,
        claim: str,
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create a categorical (mathematical) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            qualifier="definitely",
            tier=EvidenceTier.CATEGORICAL,
            principles=principles,
        )

    @classmethod
    def empirical(
        cls,
        data: str,
        warrant: str,
        claim: str,
        backing: str = "",
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create an empirical (test/measurement) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            backing=backing,
            qualifier="almost certainly",
            tier=EvidenceTier.EMPIRICAL,
            principles=principles,
        )

    @classmethod
    def aesthetic(
        cls,
        data: str,
        warrant: str,
        claim: str,
        principles: tuple[str, ...] = (),
    ) -> Proof:
        """Create an aesthetic (Hardy criteria) proof."""
        return cls(
            data=data,
            warrant=warrant,
            claim=claim,
            qualifier="arguably",
            tier=EvidenceTier.AESTHETIC,
            principles=principles,
        )

    @classmethod
    def somatic(
        cls,
        claim: str,
        feeling: str = "feels right",
    ) -> Proof:
        """
        Create a somatic (Mirror Test) proof.

        The Mirror Test: "Does this feel like me on my best day?"
        This is Kent's absolute veto (Article IV: The Disgust Veto).
        """
        return cls(
            data=feeling,
            warrant="The Mirror Test: felt sense of authenticity",
            claim=claim,
            qualifier="personally",
            tier=EvidenceTier.SOMATIC,
            principles=("ethical", "joy-inducing"),
        )

    def strengthen(self, new_backing: str) -> Proof:
        """Return new Proof with added backing (immutable pattern)."""
        combined = f"{self.backing}; {new_backing}" if self.backing else new_backing
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=combined,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
        )

    def with_rebuttal(self, rebuttal: str) -> Proof:
        """Return new Proof with added rebuttal (immutable pattern)."""
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals + (rebuttal,),
            tier=self.tier,
            principles=self.principles,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.data,
            "warrant": self.warrant,
            "claim": self.claim,
            "backing": self.backing,
            "qualifier": self.qualifier,
            "rebuttals": list(self.rebuttals),
            "tier": self.tier.name,
            "principles": list(self.principles),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Proof:
        """Create from dictionary."""
        return cls(
            data=data.get("data", ""),
            warrant=data.get("warrant", ""),
            claim=data.get("claim", ""),
            backing=data.get("backing", ""),
            qualifier=data.get("qualifier", "probably"),
            rebuttals=tuple(data.get("rebuttals", [])),
            tier=EvidenceTier[data.get("tier", "EMPIRICAL")],
            principles=tuple(data.get("principles", [])),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        claim_preview = self.claim[:40] + "..." if len(self.claim) > 40 else self.claim
        return f"Proof({self.qualifier}: '{claim_preview}', tier={self.tier.name})"


# =============================================================================
# Mark: The Atomic Unit
# =============================================================================


@dataclass(frozen=True)
class Mark:
    """
    Atomic unit of execution artifact.

    Laws:
    - Law 1 (Immutability): Marks are frozen after creation
    - Law 2 (Causality): link.target.timestamp > link.source.timestamp
    - Law 3 (Completeness): Every AGENTESE invocation emits exactly one Mark

    A Mark captures:
    - WHAT triggered it (stimulus)
    - WHAT it produced (response)
    - WHO observed it (umwelt)
    - WHEN it happened (timestamp)
    - WHERE in the workflow (phase)
    - HOW it connects (links)

    Example:
        >>> mark = Mark(
        ...     origin="witness",
        ...     stimulus=Stimulus.from_event("git", "Commit abc123", "git"),
        ...     response=Response.thought("Noticed commit abc123", ("git", "commit")),
        ...     umwelt=UmweltSnapshot.witness(trust_level=1),
        ... )
        >>> mark.id  # "mark-abc123def456"
    """

    # Identity
    id: MarkId = field(default_factory=generate_mark_id)

    # Origin (what/who emitted it)
    origin: str = "unknown"  # Jewel or agent name: "witness", "brain", "gardener", etc.

    # Domain (for frontend routing and filtering)
    domain: WitnessDomain = "system"  # "navigation", "portal", "chat", "edit", "system"

    # Content
    stimulus: Stimulus = field(default_factory=lambda: Stimulus(kind="unknown", content=""))
    response: Response = field(default_factory=lambda: Response(kind="unknown", content=""))

    # Observer context
    umwelt: UmweltSnapshot = field(default_factory=UmweltSnapshot.system)

    # Causal links (to other marks or plans)
    links: tuple[MarkLink, ...] = ()

    # Temporal
    timestamp: datetime = field(default_factory=datetime.now)

    # N-Phase context (if within a workflow)
    phase: NPhase | None = None
    walk_id: WalkId | None = None  # If within a Walk

    # Justification (Phase 1: Explicit Toulmin)
    proof: Proof | None = None  # Toulmin argumentation structure

    # Constitutional alignment (Phase 1: Witness as Constitutional Enforcement)
    constitutional: ConstitutionalAlignment | None = None

    # Metadata
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate causal links (Law 2 check deferred to store)."""
        # Note: We can't fully validate Law 2 here because we don't have
        # access to source mark timestamps. The MarkStore enforces this.
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
    ) -> Mark:
        """
        Create Mark from Witness Thought pattern.

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
    ) -> Mark:
        """Create Mark from AGENTESE invocation."""
        return cls(
            origin=origin,
            stimulus=Stimulus.from_agentese(path, aspect, **kwargs),
            response=Response.projection(f"{path}.{aspect}"),
            umwelt=umwelt or UmweltSnapshot.system(),
            phase=phase,
            metadata={"agentese_path": path, "aspect": aspect, **kwargs},
        )

    @classmethod
    def from_kblock_bind(
        cls,
        from_kblock_id: str,
        to_kblock_id: str,
        from_content: str,
        to_content: str,
        operation: str,
        lineage_edge_dict: dict[str, Any],
        path: str = "anonymous",
        umwelt: UmweltSnapshot | None = None,
    ) -> Mark:
        """
        Create Mark from K-Block bind operation.

        This is the primary integration point for K-Block -> Witness.
        When KBlock.bind() executes, it can emit a mark using this factory.

        Args:
            from_kblock_id: Source K-Block ID
            to_kblock_id: Result K-Block ID
            from_content: Source content (truncated if needed)
            to_content: Result content (truncated if needed)
            operation: Name of the transformation function
            lineage_edge_dict: Serialized LineageEdge
            path: K-Block path (for context)
            umwelt: Optional observer context

        Returns:
            Mark with K-Block provenance in metadata

        Example:
            >>> mark = Mark.from_kblock_bind(
            ...     from_kblock_id="kb_abc123",
            ...     to_kblock_id="kb_def456",
            ...     from_content="Hello",
            ...     to_content="HELLO",
            ...     operation="uppercase",
            ...     lineage_edge_dict=edge.to_dict(),
            ... )
        """
        return cls(
            origin="k_block",
            domain="edit",
            stimulus=Stimulus(
                kind="kblock_bind",
                content=from_content[:500],  # Truncate for storage
                source=f"kblock:{from_kblock_id}",
                metadata={
                    "kblock_id": from_kblock_id,
                    "path": path,
                },
            ),
            response=Response(
                kind="kblock_result",
                content=to_content[:500],  # Truncate for storage
                success=True,
                metadata={
                    "kblock_id": to_kblock_id,
                    "operation": operation,
                },
            ),
            umwelt=umwelt or UmweltSnapshot.system(),
            tags=("kblock", "bind", operation),
            metadata={
                "kblock_from_id": from_kblock_id,
                "kblock_to_id": to_kblock_id,
                "kblock_operation": operation,
                "kblock_path": path,
                "lineage_edge": lineage_edge_dict,
            },
        )

    def is_kblock_mark(self) -> bool:
        """Check if this mark originated from a K-Block operation."""
        return self.origin == "k_block" and "kblock_from_id" in self.metadata

    def get_kblock_lineage(self) -> dict[str, Any] | None:
        """
        Extract K-Block lineage edge from metadata.

        Returns:
            The lineage edge dict if this is a K-Block mark, else None
        """
        if not self.is_kblock_mark():
            return None
        return self.metadata.get("lineage_edge")

    def get_kblock_ids(self) -> tuple[str, str] | None:
        """
        Get the (from_id, to_id) K-Block IDs if this is a K-Block mark.

        Returns:
            Tuple of (from_kblock_id, to_kblock_id) or None
        """
        if not self.is_kblock_mark():
            return None
        return (
            self.metadata.get("kblock_from_id", ""),
            self.metadata.get("kblock_to_id", ""),
        )

    def with_link(self, link: MarkLink) -> Mark:
        """Return new Mark with added link (immutable pattern)."""
        # Create new frozen instance with updated links
        return Mark(
            id=self.id,
            origin=self.origin,
            domain=self.domain,
            stimulus=self.stimulus,
            response=self.response,
            umwelt=self.umwelt,
            links=self.links + (link,),
            timestamp=self.timestamp,
            phase=self.phase,
            walk_id=self.walk_id,
            proof=self.proof,
            constitutional=self.constitutional,
            tags=self.tags,
            metadata=self.metadata,
        )

    def with_proof(self, proof: Proof) -> Mark:
        """Return new Mark with proof attached (immutable pattern)."""
        return Mark(
            id=self.id,
            origin=self.origin,
            domain=self.domain,
            stimulus=self.stimulus,
            response=self.response,
            umwelt=self.umwelt,
            links=self.links,
            timestamp=self.timestamp,
            phase=self.phase,
            walk_id=self.walk_id,
            proof=proof,
            constitutional=self.constitutional,
            tags=self.tags,
            metadata=self.metadata,
        )

    def with_constitutional(self, constitutional: ConstitutionalAlignment) -> Mark:
        """
        Return new Mark with constitutional alignment (immutable pattern).

        This is the primary method for enriching marks with constitutional metadata.
        Typically called by MarkConstitutionalEvaluator after mark creation.

        Example:
            >>> evaluator = MarkConstitutionalEvaluator()
            >>> alignment = await evaluator.evaluate(mark)
            >>> enriched = mark.with_constitutional(alignment)
        """
        return Mark(
            id=self.id,
            origin=self.origin,
            domain=self.domain,
            stimulus=self.stimulus,
            response=self.response,
            umwelt=self.umwelt,
            links=self.links,
            timestamp=self.timestamp,
            phase=self.phase,
            walk_id=self.walk_id,
            proof=self.proof,
            constitutional=constitutional,
            tags=self.tags,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "origin": self.origin,
            "domain": self.domain,
            "stimulus": self.stimulus.to_dict(),
            "response": self.response.to_dict(),
            "umwelt": self.umwelt.to_dict(),
            "links": [link.to_dict() for link in self.links],
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase.value if self.phase else None,
            "walk_id": str(self.walk_id) if self.walk_id else None,
            "proof": self.proof.to_dict() if self.proof else None,
            "constitutional": self.constitutional.to_dict() if self.constitutional else None,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Mark:
        """Create from dictionary."""
        phase = NPhase(data["phase"]) if data.get("phase") else None
        proof = Proof.from_dict(data["proof"]) if data.get("proof") else None
        constitutional = (
            ConstitutionalAlignment.from_dict(data["constitutional"])
            if data.get("constitutional")
            else None
        )

        return cls(
            id=MarkId(data["id"]),
            origin=data.get("origin", "unknown"),
            domain=data.get("domain", "system"),
            stimulus=Stimulus.from_dict(data.get("stimulus", {})),
            response=Response.from_dict(data.get("response", {})),
            umwelt=UmweltSnapshot.from_dict(data.get("umwelt", {})),
            links=tuple(MarkLink.from_dict(link) for link in data.get("links", [])),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            phase=phase,
            walk_id=WalkId(data["walk_id"]) if data.get("walk_id") else None,
            proof=proof,
            constitutional=constitutional,
            tags=tuple(data.get("tags", [])),
            metadata=data.get("metadata", {}),
        )

    def to_trace_entry(self) -> TraceEntry:
        """
        Convert Mark to TraceEntry for DP-native integration.

        Mapping:
        - action: response.content (what was done)
        - state_before: stimulus.content (what triggered it)
        - state_after: response.metadata["state"] or response.content
        - value: derived from proof.qualifier (if proof exists)
        - rationale: proof.warrant (if proof exists)
        - timestamp: mark timestamp
        """
        from services.categorical.dp_bridge import TraceEntry

        # Extract state_after from response metadata or fallback to content
        state_after = self.response.metadata.get("state", self.response.content)

        # Convert proof qualifier to value (0.0 to 1.0 scale)
        value = 0.5  # default neutral value
        rationale = ""

        if self.proof:
            # Map qualifiers to confidence values
            qualifier_to_value = {
                "definitely": 1.0,
                "almost certainly": 0.9,
                "probably": 0.7,
                "arguably": 0.5,
                "possibly": 0.3,
                "personally": 0.8,  # somatic proofs are high confidence
            }
            value = qualifier_to_value.get(self.proof.qualifier.lower(), 0.5)
            rationale = self.proof.warrant

        return TraceEntry(
            state_before=self.stimulus.content,
            action=self.response.content,
            state_after=state_after,
            value=value,
            rationale=rationale,
            timestamp=self.timestamp if self.timestamp.tzinfo else self.timestamp.replace(tzinfo=timezone.utc),
        )

    @classmethod
    def from_trace_entry(
        cls,
        entry: TraceEntry,
        origin: str = "dp_bridge",
        umwelt: UmweltSnapshot | None = None,
    ) -> Mark:
        """
        Create Mark from TraceEntry for DP-native integration.

        Reverse mapping from TraceEntry to Mark:
        - stimulus.content: entry.state_before
        - response.content: entry.action
        - response.metadata["state"]: entry.state_after
        - proof.qualifier: derived from entry.value
        - proof.warrant: entry.rationale
        - timestamp: entry.timestamp
        """
        # Convert value to qualifier
        value_to_qualifier = {
            (0.95, 1.01): "definitely",
            (0.85, 0.95): "almost certainly",
            (0.6, 0.85): "probably",
            (0.4, 0.6): "arguably",
            (0.0, 0.4): "possibly",
        }

        qualifier = "probably"  # default
        for (low, high), qual in value_to_qualifier.items():
            if low <= entry.value < high:
                qualifier = qual
                break

        # Determine evidence tier based on value confidence
        tier = EvidenceTier.EMPIRICAL  # default
        if entry.value >= 0.95:
            tier = EvidenceTier.CATEGORICAL
        elif entry.value >= 0.7:
            tier = EvidenceTier.EMPIRICAL
        else:
            tier = EvidenceTier.AESTHETIC

        # Create proof if rationale exists
        proof = None
        if entry.rationale:
            proof = Proof(
                data=f"DP trace: {entry.state_before} -> {entry.state_after}",
                warrant=entry.rationale,
                claim=entry.action,
                qualifier=qualifier,
                tier=tier,
            )

        # Create stimulus and response
        stimulus = Stimulus(
            kind="dp_trace",
            content=str(entry.state_before),
            source=origin,
            metadata={"trace_entry": True},
        )

        response = Response(
            kind="dp_action",
            content=entry.action,
            success=True,
            metadata={"state": entry.state_after, "value": entry.value},
        )

        return cls(
            origin=origin,
            stimulus=stimulus,
            response=response,
            umwelt=umwelt or UmweltSnapshot.system(),
            timestamp=entry.timestamp,
            proof=proof,
            tags=("dp_trace",),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        phase_str = f", phase={self.phase.value}" if self.phase else ""
        return (
            f"Mark(id={str(self.id)[:8]}..., "
            f"origin={self.origin}, "
            f"stimulus={self.stimulus.kind}{phase_str})"
        )


# Backwards compatibility alias
Mark = Mark


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases (new names)
    "MarkId",
    "PlanPath",
    "WalkId",
    "WitnessDomain",
    "generate_mark_id",
    # Backwards compatibility aliases
    "MarkId",
    "generate_mark_id",
    # Link types (new names)
    "LinkRelation",
    "MarkLink",
    # Backwards compatibility
    "MarkLink",
    # Phase
    "NPhase",
    # Umwelt
    "UmweltSnapshot",
    # Stimulus/Response
    "Stimulus",
    "Response",
    # Phase 1: Toulmin Argumentation
    "EvidenceTier",
    "Proof",
    # Phase 1: Constitutional Enforcement
    "ConstitutionalAlignment",
    # Core (new name)
    "Mark",
    # Backwards compatibility
    "Mark",
]
