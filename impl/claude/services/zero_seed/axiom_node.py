"""
Axiom AGENTESE Node: @node("self.axiom")

Exposes the Axiom Discovery Pipeline through AGENTESE for universal gateway access.

AGENTESE Paths:
- self.axiom.manifest       - Axiom system status
- self.axiom.discover       - Discover personal axioms from decision history
- self.axiom.validate       - Validate if content qualifies as an axiom
- self.axiom.contradictions - Check for contradictions between axioms

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "Kent discovers his personal axioms. The system shows him:
     'You've made 147 decisions this month. Here are the 3 principles
      you never violated — your L0 axioms.'"

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/zero-seed.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .axiom_discovery_pipeline import (
    DEFAULT_TIME_WINDOW_DAYS,
    AxiomCandidate,
    AxiomDiscoveryPipeline,
    AxiomDiscoveryResult,
    ContradictionPair,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Request/Response Contracts
# =============================================================================


@dataclass(frozen=True)
class AxiomManifestResponse:
    """Response for self.axiom.manifest."""

    status: str
    default_time_window: int
    axiom_threshold: float
    stability_threshold: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "default_time_window": self.default_time_window,
            "axiom_threshold": self.axiom_threshold,
            "stability_threshold": self.stability_threshold,
        }


@dataclass(frozen=True)
class DiscoverRequest:
    """Request for self.axiom.discover."""

    days: int = DEFAULT_TIME_WINDOW_DAYS
    max_candidates: int = 5
    user_id: str | None = None


@dataclass(frozen=True)
class DiscoverResponse:
    """Response for self.axiom.discover."""

    candidates: list[dict[str, Any]]
    total_decisions: int
    axioms_discovered: int
    contradictions: list[dict[str, Any]]
    duration_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": self.candidates,
            "total_decisions": self.total_decisions,
            "axioms_discovered": self.axioms_discovered,
            "contradictions": self.contradictions,
            "duration_ms": self.duration_ms,
        }


@dataclass(frozen=True)
class ValidateRequest:
    """Request for self.axiom.validate."""

    content: str


@dataclass(frozen=True)
class ValidateResponse:
    """Response for self.axiom.validate."""

    content: str
    is_axiom: bool
    loss: float
    stability: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "is_axiom": self.is_axiom,
            "loss": self.loss,
            "stability": self.stability,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ContradictionsRequest:
    """Request for self.axiom.contradictions."""

    axiom_a: str
    axiom_b: str


@dataclass(frozen=True)
class ContradictionsResponse:
    """Response for self.axiom.contradictions."""

    is_contradiction: bool
    strength: float
    type_label: str
    synthesis_hint: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_contradiction": self.is_contradiction,
            "strength": self.strength,
            "type": self.type_label,
            "synthesis_hint": self.synthesis_hint,
        }


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class AxiomManifestRendering:
    """Rendering for axiom system manifest."""

    status: str
    default_time_window: int
    axiom_threshold: float
    stability_threshold: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "axiom_manifest",
            "status": self.status,
            "default_time_window": self.default_time_window,
            "axiom_threshold": self.axiom_threshold,
            "stability_threshold": self.stability_threshold,
        }

    def to_text(self) -> str:
        return f"""Axiom Discovery System
======================
Status: {self.status}
Default Time Window: {self.default_time_window} days
Axiom Threshold: L < {self.axiom_threshold}
Stability Threshold: {self.stability_threshold}

Philosophy:
  "Axioms are not stipulated but discovered.
   They are the fixed points of your decision landscape."
"""


@dataclass(frozen=True)
class AxiomDiscoveryRendering:
    """Rendering for axiom discovery results."""

    result: AxiomDiscoveryResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "axiom_discovery",
            **self.result.to_dict(),
        }

    def to_text(self) -> str:
        lines = [
            "Personal Axiom Discovery",
            "========================",
            f"Analyzed {self.result.total_decisions_analyzed} decisions from past {self.result.time_window_days} days",
            f"Found {self.result.patterns_found} recurring patterns",
            f"Discovered {self.result.axioms_discovered} axioms (L < 0.05)",
            "",
        ]

        if self.result.top_axioms:
            lines.append("Your Personal Axioms:")
            lines.append("-" * 40)
            for i, axiom in enumerate(self.result.top_axioms, 1):
                lines.append(f"{i}. {axiom.content}")
                lines.append(f"   Loss: {axiom.loss:.3f} | Confidence: {axiom.confidence:.2f}")
                lines.append(f"   Seen {axiom.frequency} times")
                lines.append("")
        else:
            lines.append("No axioms discovered yet.")
            lines.append("Keep making decisions - patterns will emerge!")
            lines.append("")

        if self.result.has_contradictions:
            lines.append("Contradictions Detected:")
            lines.append("-" * 40)
            for c in self.result.contradictions_detected:
                lines.append(f"  - {c.axiom_a}")
                lines.append(f"    vs {c.axiom_b}")
                lines.append(f"    Strength: {c.strength:.2f} ({c.type_label})")
                if c.synthesis_hint:
                    lines.append(f"    Hint: {c.synthesis_hint}")
                lines.append("")

        lines.append(f"[Completed in {self.result.duration_ms:.0f}ms]")
        return "\n".join(lines)


# =============================================================================
# Affordances
# =============================================================================

AXIOM_AFFORDANCES: tuple[str, ...] = (
    "discover",  # Discover personal axioms
    "validate",  # Validate axiom candidate
)

AXIOM_ADMIN_AFFORDANCES: tuple[str, ...] = AXIOM_AFFORDANCES + (
    "contradictions",  # Check contradictions between axioms
)


# =============================================================================
# AxiomNode
# =============================================================================


@node(
    "self.axiom",
    description="Personal axiom discovery - find the principles you never violate",
    dependencies=(),  # No required dependencies - pipeline creates its own
    contracts={
        "manifest": Response(AxiomManifestResponse),
        "discover": Contract(DiscoverRequest, DiscoverResponse),
        "validate": Contract(ValidateRequest, ValidateResponse),
        "contradictions": Contract(ContradictionsRequest, ContradictionsResponse),
    },
    examples=[
        ("discover", {"days": 30, "max_candidates": 5}, "Discover axioms from past 30 days"),
        ("validate", {"content": "Simplicity over complexity"}, "Validate potential axiom"),
    ],
)
class AxiomNode(BaseLogosNode):
    """
    AGENTESE node for personal axiom discovery.

    Exposes the Axiom Discovery Pipeline through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/axiom/discover
        {"days": 30, "max_candidates": 5}

        # Via Logos directly
        await logos.invoke("self.axiom.discover", observer, days=30)

        # Via CLI
        kg axiom discover --days 30

    Philosophy:
        "You've made 147 decisions this month.
         Here are the 3 principles you never violated — your L0 axioms."
    """

    def __init__(self) -> None:
        """Initialize AxiomNode with pipeline."""
        self._pipeline = AxiomDiscoveryPipeline()

    @property
    def handle(self) -> str:
        return "self.axiom"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        if archetype_lower in ("developer", "operator", "admin", "system"):
            return AXIOM_ADMIN_AFFORDANCES

        return AXIOM_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Display axiom discovery system status",
        examples=["kg axiom", "kg axiom manifest"],
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest axiom system status.

        AGENTESE: self.axiom.manifest
        """
        from .galois import FIXED_POINT_THRESHOLD, STABILITY_THRESHOLD

        return AxiomManifestRendering(
            status="active",
            default_time_window=DEFAULT_TIME_WINDOW_DAYS,
            axiom_threshold=FIXED_POINT_THRESHOLD,
            stability_threshold=STABILITY_THRESHOLD,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,  # Analysis is a form of read-only perception
        effects=[Effect.READS("marks")],  # Reads marks and computes derived metrics
        help="Discover personal axioms from decision history",
        examples=["kg axiom discover", "kg axiom discover --days 60"],
    )
    async def discover(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Discover personal axioms from decision history.

        AGENTESE: self.axiom.discover

        Args:
            days: Time window in days (default: 30)
            max_candidates: Max candidates to return (default: 5)
            user_id: Optional user ID for filtering
        """
        days = kwargs.get("days", DEFAULT_TIME_WINDOW_DAYS)
        max_candidates = kwargs.get("max_candidates", 5)
        user_id = kwargs.get("user_id")

        result = await self._pipeline.discover_axioms(
            user_id=user_id,
            days=days,
            max_candidates=max_candidates,
        )

        return AxiomDiscoveryRendering(result=result)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate methods."""

        if aspect == "discover":
            days = kwargs.get("days", DEFAULT_TIME_WINDOW_DAYS)
            max_candidates = kwargs.get("max_candidates", 5)
            user_id = kwargs.get("user_id")

            result = await self._pipeline.discover_axioms(
                user_id=user_id,
                days=days,
                max_candidates=max_candidates,
            )

            return {
                "candidates": [c.to_dict() for c in result.candidates],
                "total_decisions": result.total_decisions_analyzed,
                "axioms_discovered": result.axioms_discovered,
                "contradictions": [c.to_dict() for c in result.contradictions_detected],
                "duration_ms": result.duration_ms,
            }

        elif aspect == "validate":
            content = kwargs.get("content")
            if not content:
                return {"error": "content required"}

            candidate = await self._pipeline.validate_potential_axiom(content)

            return {
                "content": candidate.content,
                "is_axiom": candidate.is_axiom,
                "loss": candidate.loss,
                "stability": candidate.stability,
                "confidence": candidate.confidence,
            }

        elif aspect == "contradictions":
            axiom_a = kwargs.get("axiom_a")
            axiom_b = kwargs.get("axiom_b")

            if not axiom_a or not axiom_b:
                return {"error": "axiom_a and axiom_b required"}

            from .galois.galois_loss import detect_contradiction

            analysis = await detect_contradiction(
                content_a=axiom_a,
                content_b=axiom_b,
                computer=self._pipeline._computer,
            )

            return {
                "is_contradiction": analysis.is_contradiction,
                "strength": analysis.strength,
                "type": analysis.type.name,
                "synthesis_hint": analysis.synthesis_hint.content
                if analysis.synthesis_hint
                else None,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AxiomNode",
    "AxiomManifestRendering",
    "AxiomDiscoveryRendering",
    "AxiomManifestResponse",
    "DiscoverRequest",
    "DiscoverResponse",
    "ValidateRequest",
    "ValidateResponse",
    "ContradictionsRequest",
    "ContradictionsResponse",
]
