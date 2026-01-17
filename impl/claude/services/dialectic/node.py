"""
Dialectic AGENTESE Nodes: @node("self.dialectic") and @node("concept.fusion")

Exposes the Dialectical Fusion system via AGENTESE for Kent+Claude synthesis.

AGENTESE Paths:
- self.dialectic.manifest   - Current dialectic state
- self.dialectic.thesis     - Propose a thesis (Kent's position)
- self.dialectic.antithesis - Generate antithesis (Claude's challenge)
- self.dialectic.sublate    - Synthesize fusion (Aufhebung)
- self.dialectic.history    - View fusion history

- concept.fusion.manifest   - Fusion ontology (categorical structure)
- concept.fusion.cocone     - The cocone structure (what synthesis achieves)

Theory Basis (Ch 17: Dialectical Fusion):
    thesis: Kent's position
    antithesis: Claude's position (or vice versa)
    synthesis: A fusion better than either alone (categorical cocone)

The Emerging Constitution (7 articles) governs the fusion:
    I.   Symmetric Agency
    II.  Adversarial Cooperation
    III. Supersession Rights
    IV.  The Disgust Veto (Kent's absolute)
    V.   Trust Accumulation
    VI.  Fusion as Goal
    VII. Amendment

Philosophy:
    "The goal is not Kent's decisions or AI's decisions.
     The goal is fused decisions better than either alone.
     Individual ego is dissolved into shared purpose."

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/theory/17-dialectic.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .fusion import (
    DialecticalFusionService,
    Fusion,
    FusionResult,
    Position,
    create_position,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Contract Dataclasses
# =============================================================================


@dataclass(frozen=True)
class DialecticManifestResponse:
    """Response for dialectic manifest."""

    total_fusions: int
    recent_topic: str | None
    trust_trajectory: str
    cumulative_trust_delta: float
    fusion_counts: dict[str, int]


@dataclass(frozen=True)
class ThesisRequest:
    """Request to propose a thesis (Kent's position)."""

    topic: str
    content: str
    reasoning: str
    confidence: float | None = None
    evidence: list[str] | None = None


@dataclass(frozen=True)
class ThesisResponse:
    """Response after thesis proposal."""

    topic: str
    position: dict[str, Any]
    holder: str


@dataclass(frozen=True)
class AntithesisRequest:
    """Request to generate antithesis (Claude's challenge)."""

    topic: str
    thesis_content: str
    thesis_reasoning: str
    content: str
    reasoning: str
    confidence: float | None = None
    evidence: list[str] | None = None


@dataclass(frozen=True)
class AntithesisResponse:
    """Response after antithesis generation."""

    topic: str
    thesis: dict[str, Any]
    antithesis: dict[str, Any]


@dataclass(frozen=True)
class SublateRequest:
    """Request to synthesize (sublate/Aufheben) thesis and antithesis."""

    topic: str
    kent_view: str
    kent_reasoning: str
    claude_view: str
    claude_reasoning: str


@dataclass(frozen=True)
class SublateResponse:
    """Response after sublation (synthesis)."""

    fusion_id: str
    topic: str
    result: str
    reasoning: str
    synthesis: dict[str, Any] | None
    trust_delta: float
    mark_id: str | None


@dataclass(frozen=True)
class HistoryRequest:
    """Request for fusion history."""

    topic: str | None = None
    limit: int = 10


@dataclass(frozen=True)
class HistoryResponse:
    """Response with fusion history."""

    fusions: list[dict[str, Any]]
    count: int


@dataclass(frozen=True)
class FusionOntologyResponse:
    """Response for concept.fusion.manifest - the fusion ontology."""

    constitution_articles: list[dict[str, str]]
    fusion_results: list[dict[str, str]]
    trust_deltas: dict[str, float]
    principle_weights: dict[str, float]


@dataclass(frozen=True)
class CoconeStructureResponse:
    """Response for concept.fusion.cocone - the categorical cocone."""

    description: str
    formula: str
    components: dict[str, str]
    philosophy: str


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class DialecticManifestRendering:
    """Rendering for dialectic status manifest."""

    total_fusions: int
    recent_topic: str | None
    trust_trajectory: str
    cumulative_trust_delta: float
    fusion_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "dialectic_manifest",
            "total_fusions": self.total_fusions,
            "recent_topic": self.recent_topic,
            "trust_trajectory": self.trust_trajectory,
            "cumulative_trust_delta": self.cumulative_trust_delta,
            "fusion_counts": self.fusion_counts,
        }

    def to_text(self) -> str:
        lines = [
            "Dialectic Status (Thesis-Antithesis-Synthesis)",
            "==============================================",
            f"Total Fusions: {self.total_fusions}",
            f"Trust Trajectory: {self.trust_trajectory}",
            f"Cumulative Trust Delta: {self.cumulative_trust_delta:+.2f}",
            "",
            "Fusion Results:",
        ]
        for result, count in self.fusion_counts.items():
            lines.append(f"  {result}: {count}")
        if self.recent_topic:
            lines.extend(["", f"Most Recent: {self.recent_topic}"])
        return "\n".join(lines)


@dataclass(frozen=True)
class FusionOntologyRendering:
    """Rendering for fusion ontology."""

    constitution_articles: list[dict[str, str]]
    fusion_results: list[dict[str, str]]
    trust_deltas: dict[str, float]
    principle_weights: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "fusion_ontology",
            "constitution_articles": self.constitution_articles,
            "fusion_results": self.fusion_results,
            "trust_deltas": self.trust_deltas,
            "principle_weights": self.principle_weights,
        }

    def to_text(self) -> str:
        lines = [
            "Fusion Ontology",
            "===============",
            "",
            "The Emerging Constitution:",
        ]
        for article in self.constitution_articles:
            lines.append(f"  {article['number']}. {article['name']}: {article['description']}")
        lines.extend(["", "Fusion Results (with trust deltas):"])
        for result in self.fusion_results:
            delta = self.trust_deltas.get(result["value"], 0.0)
            lines.append(f"  {result['name']}: {result['description']} (delta: {delta:+.2f})")
        return "\n".join(lines)


# =============================================================================
# DialecticNode - self.dialectic.*
# =============================================================================


@node(
    "self.dialectic",
    description="Self-reflective dialectical reasoning: thesis + antithesis = synthesis",
    dependencies=("dialectic_service",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(DialecticManifestResponse),
        # Mutation aspects (Contract with request + response)
        "thesis": Contract(ThesisRequest, ThesisResponse),
        "antithesis": Contract(AntithesisRequest, AntithesisResponse),
        "sublate": Contract(SublateRequest, SublateResponse),
        "history": Contract(HistoryRequest, HistoryResponse),
    },
    examples=[
        ("manifest", {}, "View dialectic status"),
        (
            "thesis",
            {
                "topic": "Database choice",
                "content": "Use PostgreSQL",
                "reasoning": "Familiar, reliable, ACID-compliant",
            },
            "Propose Kent's thesis",
        ),
        (
            "sublate",
            {
                "topic": "Framework choice",
                "kent_view": "Use existing framework",
                "kent_reasoning": "Scale, resources, production-ready",
                "claude_view": "Build novel system",
                "claude_reasoning": "Joy-inducing, novel contribution",
            },
            "Synthesize a decision",
        ),
        ("history", {"topic": "architecture", "limit": 5}, "View recent architecture decisions"),
    ],
)
class DialecticNode(BaseLogosNode):
    """
    AGENTESE node for Dialectical Reasoning (self.dialectic.*).

    Exposes DialecticalFusionService through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    The dialectical process:
        1. thesis: Propose Kent's position
        2. antithesis: Challenge with Claude's position
        3. sublate: Synthesize into a fusion better than either

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/dialectic/sublate
        {"topic": "...", "kent_view": "...", "claude_view": "..."}

        # Via Logos directly
        await logos.invoke("self.dialectic.sublate", observer, topic="...", ...)

        # Via CLI
        kg decide --kent "..." --claude "..." --topic "..."
    """

    # Aspect hints for Ghost Integration
    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "thesis": "Propose Kent's position - the initial claim",
        "antithesis": "Challenge with Claude's counter-position",
        "sublate": "Synthesize thesis and antithesis into fusion (Aufhebung)",
        "history": "View past dialectical fusions and their outcomes",
    }

    def __init__(
        self,
        dialectic_service: DialecticalFusionService | None = None,
    ) -> None:
        """
        Initialize DialecticNode.

        Args:
            dialectic_service: The DialecticalFusionService (injected by container)
        """
        self._service = dialectic_service or DialecticalFusionService()

    @property
    def handle(self) -> str:
        return "self.dialectic"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Dialectic is open to all agents (symmetric agency), but
        synthesis requires deeper trust.

        - developer/operator: Full access
        - architect: Can propose and synthesize
        - newcomer: Can view history and manifest
        - guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators (Kent's trusted proxies)
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return ("manifest", "thesis", "antithesis", "sublate", "history")

        # Architects: can propose and synthesize
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "thesis", "antithesis", "sublate", "history")

        # Newcomers/reviewers: read-only observation
        if archetype_lower in ("newcomer", "casual", "reviewer", "security"):
            return ("manifest", "history")

        # Guest (default): manifest only
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest dialectic status to observer.

        AGENTESE: self.dialectic.manifest
        """
        trajectory = self._service.get_trust_trajectory()
        history = self._service.get_history(limit=10)

        # Count results
        fusion_counts: dict[str, int] = {}
        for fusion in history:
            result_name = fusion.result.value
            fusion_counts[result_name] = fusion_counts.get(result_name, 0) + 1

        recent_topic = history[0].topic if history else None

        return DialecticManifestRendering(
            total_fusions=self._service.store.count(),
            recent_topic=recent_topic,
            trust_trajectory=trajectory["trend"],
            cumulative_trust_delta=trajectory["cumulative_delta"],
            fusion_counts=fusion_counts,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "thesis":
            # Propose Kent's thesis
            topic = kwargs.get("topic", "")
            content = kwargs.get("content", "")
            reasoning = kwargs.get("reasoning", "")
            confidence = kwargs.get("confidence", 0.5)
            evidence = kwargs.get("evidence", [])

            if not topic or not content:
                return {"error": "topic and content required"}

            position = create_position(
                content=content,
                reasoning=reasoning,
                holder="kent",
                confidence=float(confidence),
                evidence=evidence,
            )

            return {
                "topic": topic,
                "position": position.to_dict(),
                "holder": "kent",
            }

        elif aspect == "antithesis":
            # Generate Claude's antithesis
            topic = kwargs.get("topic", "")
            thesis_content = kwargs.get("thesis_content", "")
            thesis_reasoning = kwargs.get("thesis_reasoning", "")
            content = kwargs.get("content", "")
            reasoning = kwargs.get("reasoning", "")
            confidence = kwargs.get("confidence", 0.5)
            evidence = kwargs.get("evidence", [])

            if not topic or not content:
                return {"error": "topic and content required"}

            thesis = create_position(
                content=thesis_content,
                reasoning=thesis_reasoning,
                holder="kent",
            )

            antithesis = create_position(
                content=content,
                reasoning=reasoning,
                holder="claude",
                confidence=float(confidence),
                evidence=evidence,
            )

            return {
                "topic": topic,
                "thesis": thesis.to_dict(),
                "antithesis": antithesis.to_dict(),
            }

        elif aspect == "sublate":
            # Synthesize (sublate) thesis and antithesis
            topic = kwargs.get("topic", "")
            kent_view = kwargs.get("kent_view", "")
            kent_reasoning = kwargs.get("kent_reasoning", "")
            claude_view = kwargs.get("claude_view", "")
            claude_reasoning = kwargs.get("claude_reasoning", "")

            if not topic:
                return {"error": "topic required"}
            if not kent_view or not claude_view:
                return {"error": "kent_view and claude_view required"}

            # Perform dialectical fusion
            witnessed = await self._service.propose_fusion(
                topic=topic,
                kent_view=kent_view,
                kent_reasoning=kent_reasoning,
                claude_view=claude_view,
                claude_reasoning=claude_reasoning,
            )

            fusion = witnessed.value

            return {
                "fusion_id": fusion.id,
                "topic": fusion.topic,
                "result": fusion.result.value,
                "reasoning": fusion.reasoning,
                "synthesis": fusion.synthesis.to_dict() if fusion.synthesis else None,
                "trust_delta": fusion.trust_delta,
                "mark_id": fusion.mark_id,
            }

        elif aspect == "history":
            # Get fusion history
            topic = kwargs.get("topic")
            limit = int(kwargs.get("limit", 10))

            fusions = self._service.get_history(topic=topic, limit=limit)

            return {
                "fusions": [f.to_dict() for f in fusions],
                "count": len(fusions),
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# FusionConceptNode - concept.fusion.*
# =============================================================================


@node(
    "concept.fusion",
    description="Abstract fusion concepts: the categorical cocone structure",
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(FusionOntologyResponse),
        "cocone": Response(CoconeStructureResponse),
    },
    examples=[
        ("manifest", {}, "View fusion ontology"),
        ("cocone", {}, "View the categorical cocone structure"),
    ],
)
class FusionConceptNode(BaseLogosNode):
    """
    AGENTESE node for Fusion Concepts (concept.fusion.*).

    Provides the abstract/theoretical view of dialectical fusion:
    - The Emerging Constitution (7 articles)
    - Fusion results and their trust implications
    - The categorical cocone structure

    This is the Platonic/conceptual complement to self.dialectic
    which handles concrete fusions.

    Example:
        # View the ontology
        await logos.invoke("concept.fusion.manifest", observer)

        # View the cocone structure
        await logos.invoke("concept.fusion.cocone", observer)
    """

    # Aspect hints for Ghost Integration
    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "cocone": "The categorical cocone - what synthesis achieves mathematically",
    }

    # The Emerging Constitution
    CONSTITUTION_ARTICLES: ClassVar[list[dict[str, str]]] = [
        {
            "number": "I",
            "name": "Symmetric Agency",
            "description": "All agents are modeled identically",
        },
        {
            "number": "II",
            "name": "Adversarial Cooperation",
            "description": "Challenge is structural, not hostile",
        },
        {
            "number": "III",
            "name": "Supersession Rights",
            "description": "Any agent may be superseded (with justification)",
        },
        {
            "number": "IV",
            "name": "The Disgust Veto",
            "description": "Kent's somatic disgust is absolute veto",
        },
        {
            "number": "V",
            "name": "Trust Accumulation",
            "description": "Earned through demonstrated alignment",
        },
        {
            "number": "VI",
            "name": "Fusion as Goal",
            "description": "Fused decisions > individual decisions",
        },
        {
            "number": "VII",
            "name": "Amendment",
            "description": "Constitution evolves through dialectical process",
        },
    ]

    # Fusion results
    FUSION_RESULTS: ClassVar[list[dict[str, str]]] = [
        {"name": "CONSENSUS", "value": "consensus", "description": "Agreement reached"},
        {
            "name": "SYNTHESIS",
            "value": "synthesis",
            "description": "New position that sublates both",
        },
        {
            "name": "KENT_PREVAILS",
            "value": "kent",
            "description": "Kent's position wins",
        },
        {
            "name": "CLAUDE_PREVAILS",
            "value": "claude",
            "description": "Claude's position wins",
        },
        {"name": "DEFERRED", "value": "deferred", "description": "Decision deferred"},
        {"name": "VETO", "value": "veto", "description": "Kent's disgust veto"},
    ]

    def __init__(self) -> None:
        """Initialize FusionConceptNode."""
        # Create a service just to get the constants
        self._service = DialecticalFusionService()

    @property
    def handle(self) -> str:
        return "concept.fusion"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Concepts are available to all archetypes (pure observation).
        """
        return ("manifest", "cocone")

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest fusion ontology to observer.

        AGENTESE: concept.fusion.manifest
        """
        return FusionOntologyRendering(
            constitution_articles=list(self.CONSTITUTION_ARTICLES),
            fusion_results=list(self.FUSION_RESULTS),
            trust_deltas={
                result.value: self._service.TRUST_DELTAS[result] for result in FusionResult
            },
            principle_weights=dict(self._service.PRINCIPLE_WEIGHTS),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "cocone":
            return {
                "description": (
                    "The categorical cocone represents synthesis as a universal construction. "
                    "Given two positions (thesis and antithesis), the cocone is the minimal "
                    "structure that 'contains' both while adding no unnecessary information."
                ),
                "formula": "cocone(thesis, antithesis) = minimal fusion preserving both",
                "components": {
                    "apex": "The synthesis - the tip of the cocone",
                    "legs": "The morphisms from thesis/antithesis to synthesis",
                    "universality": "Any other synthesis factors through this one",
                },
                "philosophy": (
                    "The cocone is not a compromise (which loses information). "
                    "It is an Aufhebung - a lifting up that preserves and transcends. "
                    "What was valid in thesis and antithesis is preserved; "
                    "what was contradictory is resolved at a higher level."
                ),
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Nodes
    "DialecticNode",
    "FusionConceptNode",
    # Contracts
    "DialecticManifestResponse",
    "ThesisRequest",
    "ThesisResponse",
    "AntithesisRequest",
    "AntithesisResponse",
    "SublateRequest",
    "SublateResponse",
    "HistoryRequest",
    "HistoryResponse",
    "FusionOntologyResponse",
    "CoconeStructureResponse",
]
