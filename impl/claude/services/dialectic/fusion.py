"""
Dialectical Fusion Service: Kent + Claude → Synthesis.

Theory Basis (Ch 17: Dialectical Fusion):
    Dialectical fusion operationalizes co-engineering:
    - Kent and Claude each bring a position
    - Positions are structured with evidence and principle alignment
    - Synthesis attempts to preserve what's valid in both
    - Trust accumulates through successful fusion

The Emerging Constitution Articles:
    I.   Symmetric Agency: All agents modeled identically
    II.  Adversarial Cooperation: Challenge is structural, not hostile
    III. Supersession Rights: Any agent may be superseded (with justification)
    IV.  The Disgust Veto: Kent's somatic disgust is absolute veto
    V.   Trust Accumulation: Earned through demonstrated alignment
    VI.  Fusion as Goal: Fused decisions > individual decisions
    VII. Amendment: Constitution evolves through dialectical process

Philosophy:
    "Authority derives from quality of justification."
    "Challenge is nominative (structural) not substantive (hostile)."

Integration:
    - Uses Witness for recording fusion marks
    - Uses TrustState from trust/gradient.py for trust tracking
    - Emits Witnessed traces via Kleisli composition

See: docs/theory/17-dialectic.md
See: plans/theory-operationalization/05-co-engineering.md (E3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol
from uuid import uuid4

from ..witness.kleisli import Witnessed, witness_value
from ..witness.mark import (
    EvidenceTier,
    Mark,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)

# =============================================================================
# Type Aliases
# =============================================================================


FusionId = str


def generate_fusion_id() -> FusionId:
    """Generate a unique Fusion ID."""
    return f"fusion-{uuid4().hex[:12]}"


# =============================================================================
# Fusion Outcomes
# =============================================================================


class FusionResult(Enum):
    """
    Outcomes of dialectical fusion.

    These map to the Constitution's governance modes:
    - CONSENSUS: Article VI — Fusion achieved, both agree
    - SYNTHESIS: Article VI — New position that sublates both
    - KENT_PREVAILS: Article IV — Kent's position wins (may be veto)
    - CLAUDE_PREVAILS: Article III — Claude's position wins (with justification)
    - DEFERRED: Article II — More adversarial cooperation needed
    - VETO: Article IV — Kent's disgust veto (absolute)
    """

    CONSENSUS = "consensus"  # Agreement reached
    SYNTHESIS = "synthesis"  # New position that sublates both
    KENT_PREVAILS = "kent"  # Kent's position wins
    CLAUDE_PREVAILS = "claude"  # Claude's position wins
    DEFERRED = "deferred"  # Decision deferred
    VETO = "veto"  # Kent's disgust veto


# =============================================================================
# Position: A Structured View
# =============================================================================


@dataclass
class Position:
    """
    A position in the dialectic.

    Each position captures:
    - content: The actual view/claim
    - reasoning: Why this position is held
    - confidence: How confident the holder is (0.0 - 1.0)
    - evidence: Supporting evidence
    - principle_alignment: How well it aligns with constitutional principles
    """

    content: str
    reasoning: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    principle_alignment: dict[str, float] = field(default_factory=dict)
    holder: str = "unknown"  # "kent" or "claude"

    def __post_init__(self) -> None:
        """Validate confidence range."""
        self.confidence = max(0.0, min(1.0, self.confidence))

    @property
    def ethical_score(self) -> float:
        """Get ethical principle score (for veto detection)."""
        return self.principle_alignment.get("ETHICAL", 0.5)

    @property
    def is_ethically_concerning(self) -> bool:
        """Check if position has concerning ethical score (potential veto)."""
        return self.ethical_score < 0.3

    @property
    def dominant_principle(self) -> str:
        """Get the highest-scoring principle."""
        if not self.principle_alignment:
            return "unknown"
        return max(self.principle_alignment.keys(), key=lambda p: self.principle_alignment[p])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "principle_alignment": self.principle_alignment,
            "holder": self.holder,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        """Create from dictionary."""
        return cls(
            content=data.get("content", ""),
            reasoning=data.get("reasoning", ""),
            confidence=data.get("confidence", 0.5),
            evidence=data.get("evidence", []),
            principle_alignment=data.get("principle_alignment", {}),
            holder=data.get("holder", "unknown"),
        )


def create_position(
    content: str,
    reasoning: str,
    holder: str = "unknown",
    confidence: float = 0.5,
    evidence: list[str] | None = None,
) -> Position:
    """
    Factory for creating positions with default principle alignment.

    Args:
        content: The position content
        reasoning: The reasoning behind the position
        holder: "kent" or "claude"
        confidence: Initial confidence (0.0 - 1.0)
        evidence: Optional list of evidence

    Returns:
        A new Position with neutral principle alignment
    """
    return Position(
        content=content,
        reasoning=reasoning,
        confidence=confidence,
        evidence=evidence or [],
        principle_alignment={
            "TASTEFUL": 0.5,
            "CURATED": 0.5,
            "ETHICAL": 0.5,
            "JOY_INDUCING": 0.5,
            "COMPOSABLE": 0.5,
            "HETERARCHICAL": 0.5,
            "GENERATIVE": 0.5,
        },
        holder=holder,
    )


# =============================================================================
# Fusion: The Dialectical Record
# =============================================================================


@dataclass
class Fusion:
    """
    A dialectical fusion record.

    Captures the complete dialectic:
    - topic: What's being decided
    - kent_position: Kent's view
    - claude_position: Claude's view
    - synthesis: The fused position (if achieved)
    - result: The outcome type
    - reasoning: Why this outcome was reached
    - trust_delta: How trust changed from this fusion
    """

    id: FusionId
    topic: str
    timestamp: datetime
    kent_position: Position
    claude_position: Position
    synthesis: Position | None
    result: FusionResult
    reasoning: str
    trust_delta: float = 0.0
    mark_id: str | None = None  # Link to witness mark

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "topic": self.topic,
            "timestamp": self.timestamp.isoformat(),
            "kent_position": self.kent_position.to_dict(),
            "claude_position": self.claude_position.to_dict(),
            "synthesis": self.synthesis.to_dict() if self.synthesis else None,
            "result": self.result.value,
            "reasoning": self.reasoning,
            "trust_delta": self.trust_delta,
            "mark_id": self.mark_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Fusion":
        """Create from dictionary."""
        synthesis = None
        if data.get("synthesis"):
            synthesis = Position.from_dict(data["synthesis"])

        return cls(
            id=data["id"],
            topic=data["topic"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            kent_position=Position.from_dict(data["kent_position"]),
            claude_position=Position.from_dict(data["claude_position"]),
            synthesis=synthesis,
            result=FusionResult(data["result"]),
            reasoning=data["reasoning"],
            trust_delta=data.get("trust_delta", 0.0),
            mark_id=data.get("mark_id"),
        )


# =============================================================================
# Fusion Store
# =============================================================================


class FusionStore:
    """
    In-memory store for fusion records.

    In production, this would be backed by a database.
    """

    def __init__(self) -> None:
        self._fusions: dict[FusionId, Fusion] = {}

    def add(self, fusion: Fusion) -> None:
        """Add a fusion to the store."""
        self._fusions[fusion.id] = fusion

    def get(self, fusion_id: FusionId) -> Fusion | None:
        """Get a fusion by ID."""
        return self._fusions.get(fusion_id)

    def get_by_topic(self, topic: str, limit: int = 10) -> list[Fusion]:
        """Get fusions by topic."""
        matches = [f for f in self._fusions.values() if topic.lower() in f.topic.lower()]
        return sorted(matches, key=lambda f: f.timestamp, reverse=True)[:limit]

    def get_recent(self, limit: int = 10) -> list[Fusion]:
        """Get most recent fusions."""
        sorted_fusions = sorted(self._fusions.values(), key=lambda f: f.timestamp, reverse=True)
        return sorted_fusions[:limit]

    def count(self) -> int:
        """Get total number of fusions."""
        return len(self._fusions)

    def clear(self) -> None:
        """Clear all fusions."""
        self._fusions.clear()


# Global fusion store
_fusion_store: FusionStore | None = None


def get_fusion_store() -> FusionStore:
    """Get the global fusion store."""
    global _fusion_store
    if _fusion_store is None:
        _fusion_store = FusionStore()
    return _fusion_store


def reset_fusion_store() -> None:
    """Reset the global fusion store."""
    global _fusion_store
    _fusion_store = None


# =============================================================================
# LLM Provider Protocol
# =============================================================================


class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    async def complete(self, prompt: str) -> str:
        """Complete a prompt."""
        ...


# =============================================================================
# Dialectical Fusion Service
# =============================================================================


@dataclass
class DialecticalFusionService:
    """
    Manages dialectical fusion between Kent and Claude.

    This is the core E3 implementation. It:
    1. Structures positions with principle alignment
    2. Checks for immediate consensus
    3. Attempts synthesis (NOT cocone — honest naming)
    4. Determines outcome according to Constitution
    5. Updates trust based on outcome
    6. Records in witness

    Usage:
        >>> service = DialecticalFusionService(llm=my_llm)
        >>> fusion = await service.propose_fusion(
        ...     topic="Database choice",
        ...     kent_view="Use Postgres",
        ...     kent_reasoning="Familiar, reliable",
        ...     claude_view="Use SQLite",
        ...     claude_reasoning="Simpler for prototyping",
        ... )
        >>> print(fusion.result)  # FusionResult.SYNTHESIS
    """

    llm: LLMProvider | None = None
    store: FusionStore = field(default_factory=get_fusion_store)

    # Constitutional principles with weights
    PRINCIPLE_WEIGHTS: dict[str, float] = field(
        default_factory=lambda: {
            "ETHICAL": 2.0,  # Safety first
            "COMPOSABLE": 1.5,  # Architecture second
            "JOY_INDUCING": 1.2,  # Kent's aesthetic
            "TASTEFUL": 1.0,
            "CURATED": 1.0,
            "HETERARCHICAL": 1.0,
            "GENERATIVE": 1.0,
        }
    )

    # Trust deltas for outcomes
    TRUST_DELTAS: dict[FusionResult, float] = field(
        default_factory=lambda: {
            FusionResult.CONSENSUS: 0.10,  # Strong trust building
            FusionResult.SYNTHESIS: 0.15,  # Best outcome for trust
            FusionResult.KENT_PREVAILS: 0.05,  # Mild trust building
            FusionResult.CLAUDE_PREVAILS: 0.08,  # Good trust building
            FusionResult.DEFERRED: 0.0,  # Neutral
            FusionResult.VETO: -0.10,  # Trust loss (misalignment)
        }
    )

    async def propose_fusion(
        self,
        topic: str,
        kent_view: str,
        kent_reasoning: str,
        claude_view: str,
        claude_reasoning: str,
    ) -> Witnessed[Fusion]:
        """
        Propose and execute a dialectical fusion.

        This is the main entry point for dialectical fusion.

        Args:
            topic: The topic being decided
            kent_view: Kent's position content
            kent_reasoning: Kent's reasoning
            claude_view: Claude's position content
            claude_reasoning: Claude's reasoning

        Returns:
            Witnessed[Fusion] containing the fusion and witness marks
        """
        # 1. Structure positions
        kent_position = await self._structure_position(kent_view, kent_reasoning, "kent")
        claude_position = await self._structure_position(claude_view, claude_reasoning, "claude")

        # 2. Check for immediate consensus
        is_consensus = await self._check_consensus(kent_position, claude_position)

        if is_consensus:
            return await self._create_consensus_fusion(topic, kent_position, claude_position)

        # 3. Attempt synthesis
        synthesis = await self._attempt_synthesis(topic, kent_position, claude_position)

        # 4. Determine result
        result, reasoning = await self._determine_result(kent_position, claude_position, synthesis)

        # 5. Compute trust delta
        trust_delta = self._compute_trust_delta(result)

        # 6. Create fusion record
        fusion = Fusion(
            id=generate_fusion_id(),
            topic=topic,
            timestamp=datetime.now(timezone.utc),
            kent_position=kent_position,
            claude_position=claude_position,
            synthesis=synthesis,
            result=result,
            reasoning=reasoning,
            trust_delta=trust_delta,
        )

        # 7. Store fusion
        self.store.add(fusion)

        # 8. Create witnessed result with mark
        return self._witness_fusion(fusion)

    async def _structure_position(
        self,
        view: str,
        reasoning: str,
        holder: str,
    ) -> Position:
        """
        Structure a raw view into a Position.

        If an LLM is available, use it to extract evidence and score principles.
        Otherwise, use defaults.
        """
        evidence: list[str] = []
        alignment: dict[str, float] = {}

        if self.llm:
            # Extract evidence using LLM
            evidence = await self._extract_evidence(view, reasoning)

            # Score principle alignment
            for principle in self.PRINCIPLE_WEIGHTS.keys():
                score = await self._score_principle(view, principle)
                alignment[principle] = score

            # Estimate confidence from principle alignment
            if alignment:
                confidence = sum(alignment.values()) / len(alignment)
            else:
                confidence = 0.5
        else:
            # Default: neutral alignment
            alignment = {p: 0.5 for p in self.PRINCIPLE_WEIGHTS.keys()}
            confidence = 0.5

        return Position(
            content=view,
            reasoning=reasoning,
            confidence=confidence,
            evidence=evidence,
            principle_alignment=alignment,
            holder=holder,
        )

    async def _extract_evidence(self, view: str, reasoning: str) -> list[str]:
        """Extract evidence from view and reasoning using LLM."""
        if not self.llm:
            return []

        prompt = f"""List 2-4 key pieces of evidence supporting this position.
Return each on its own line.

Position: {view}
Reasoning: {reasoning}

Evidence:"""

        try:
            response = await self.llm.complete(prompt)
            lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
            # Clean up numbering/bullets
            cleaned = []
            for line in lines[:4]:
                # Remove common prefixes like "1.", "-", "*"
                if line and line[0].isdigit() and len(line) > 2 and line[1] in ".):":
                    line = line[2:].strip()
                elif line and line[0] in "-*•":
                    line = line[1:].strip()
                if line:
                    cleaned.append(line)
            return cleaned
        except Exception:
            return []

    async def _score_principle(self, view: str, principle: str) -> float:
        """Score a view against a principle using LLM."""
        if not self.llm:
            return 0.5

        prompt = f"""On a scale of 0.0 to 1.0, how well does this position align with the principle "{principle}"?

Position: {view}

Answer with just a number between 0.0 and 1.0:"""

        try:
            response = await self.llm.complete(prompt)
            # Extract float from response
            for word in response.strip().split():
                try:
                    score = float(word.strip(".,"))
                    return max(0.0, min(1.0, score))
                except ValueError:
                    continue
            return 0.5
        except Exception:
            return 0.5

    async def _check_consensus(
        self,
        kent: Position,
        claude: Position,
    ) -> bool:
        """Check if positions are already in consensus."""
        if not self.llm:
            # Simple heuristic: high confidence and similar content
            if kent.confidence > 0.8 and claude.confidence > 0.8:
                # Check for word overlap
                kent_words = set(kent.content.lower().split())
                claude_words = set(claude.content.lower().split())
                overlap = len(kent_words & claude_words)
                total = len(kent_words | claude_words)
                if total > 0 and overlap / total > 0.5:
                    return True
            return False

        prompt = f"""Do these two positions fundamentally agree or disagree?

Position 1 (Kent): {kent.content}
Position 2 (Claude): {claude.content}

Answer only "AGREE" or "DISAGREE":"""

        try:
            response = await self.llm.complete(prompt)
            return "AGREE" in response.upper()
        except Exception:
            return False

    async def _attempt_synthesis(
        self,
        topic: str,
        kent: Position,
        claude: Position,
    ) -> Position | None:
        """
        Attempt to synthesize a new position.

        IMPORTANT: This is HEURISTIC synthesis, NOT a categorical cocone.
        We make no claims of universality or optimality.
        """
        if not self.llm:
            # Without LLM, can't synthesize
            return None

        prompt = f"""Topic: {topic}

Kent's position: {kent.content}
Kent's reasoning: {kent.reasoning}

Claude's position: {claude.content}
Claude's reasoning: {claude.reasoning}

Generate a synthesis that:
1. Acknowledges the valid points in both positions
2. Resolves the tension between them
3. Creates a new position that preserves what's essential from both
4. Explains what each side contributes to the synthesis

Keep the synthesis concise (2-3 sentences).

Synthesis:"""

        try:
            synthesis_content = await self.llm.complete(prompt)

            # Structure the synthesis as a position
            synthesis = await self._structure_position(
                synthesis_content.strip(),
                f"Synthesis of Kent's and Claude's views on {topic}",
                "synthesis",
            )

            return synthesis
        except Exception:
            return None

    async def _determine_result(
        self,
        kent: Position,
        claude: Position,
        synthesis: Position | None,
    ) -> tuple[FusionResult, str]:
        """
        Determine the fusion result.

        Applies the Emerging Constitution:
        - Article IV (Disgust Veto): Kent's ethical concerns are absolute
        - Article VI (Fusion as Goal): Prefer synthesis when possible
        - Article III (Supersession): Higher confidence can supersede
        """
        # Article IV: Check Kent's ETHICAL floor (disgust veto)
        if kent.is_ethically_concerning:
            return FusionResult.VETO, (
                "Kent's disgust veto (ETHICAL floor violation). "
                f"Ethical score: {kent.ethical_score:.2f}"
            )

        # Article VI: If synthesis is strong, use it
        if synthesis is not None:
            # Synthesis wins if it's more confident than both
            if synthesis.confidence > max(kent.confidence, claude.confidence):
                return FusionResult.SYNTHESIS, (
                    f"Synthesis achieves higher confidence ({synthesis.confidence:.2f}) "
                    f"than Kent ({kent.confidence:.2f}) or Claude ({claude.confidence:.2f})"
                )
            # Synthesis also wins if it preserves ethical concerns
            if synthesis.ethical_score > max(kent.ethical_score, claude.ethical_score) * 0.9:
                return FusionResult.SYNTHESIS, (
                    f"Synthesis preserves ethical alignment ({synthesis.ethical_score:.2f})"
                )

        # Article III: Higher confidence wins (with justification)
        confidence_diff = abs(kent.confidence - claude.confidence)
        if confidence_diff > 0.1:  # Meaningful difference
            if kent.confidence > claude.confidence:
                return FusionResult.KENT_PREVAILS, (
                    f"Kent's position has higher confidence "
                    f"({kent.confidence:.2f} vs {claude.confidence:.2f})"
                )
            else:
                return FusionResult.CLAUDE_PREVAILS, (
                    f"Claude's position has higher confidence "
                    f"({claude.confidence:.2f} vs {kent.confidence:.2f})"
                )

        # Article II: Need more adversarial cooperation
        return FusionResult.DEFERRED, (
            f"Positions equally confident ({kent.confidence:.2f} ≈ {claude.confidence:.2f}), "
            "deferring decision for further discussion"
        )

    def _compute_trust_delta(self, result: FusionResult) -> float:
        """Compute how much trust changes from this fusion."""
        return self.TRUST_DELTAS.get(result, 0.0)

    def _witness_fusion(self, fusion: Fusion) -> Witnessed[Fusion]:
        """Create a witnessed fusion with mark."""
        # Create proof for the fusion decision
        proof = Proof(
            data=f"Fusion: {fusion.kent_position.content[:50]}... vs {fusion.claude_position.content[:50]}...",
            warrant=fusion.reasoning,
            claim=f"Fusion result: {fusion.result.value}",
            qualifier="probably"
            if fusion.result in [FusionResult.SYNTHESIS, FusionResult.CONSENSUS]
            else "arguably",
            tier=EvidenceTier.EMPIRICAL,
            principles=("composable", "heterarchical"),
        )

        # Create mark for the fusion
        mark = Mark(
            id=generate_mark_id(),
            origin="dialectic",
            domain="system",
            stimulus=Stimulus(
                kind="fusion",
                content=fusion.topic,
                source="dialectic",
                metadata={
                    "kent_view": fusion.kent_position.content[:100],
                    "claude_view": fusion.claude_position.content[:100],
                },
            ),
            response=Response(
                kind="fusion_result",
                content=fusion.result.value,
                success=True,
                metadata={
                    "reasoning": fusion.reasoning,
                    "trust_delta": fusion.trust_delta,
                },
            ),
            umwelt=UmweltSnapshot.system(),
            timestamp=fusion.timestamp,
            proof=proof,
            tags=("dialectic", "fusion", fusion.result.value),
        )

        # Link mark to fusion
        fusion.mark_id = str(mark.id)

        # Return witnessed fusion
        return Witnessed(value=fusion, marks=[mark])

    async def _create_consensus_fusion(
        self,
        topic: str,
        kent: Position,
        claude: Position,
    ) -> Witnessed[Fusion]:
        """Create a fusion for consensus case."""
        # Use Kent's position as the synthesis (or could merge)
        synthesis = Position(
            content=kent.content,
            reasoning=f"Consensus: Both Kent and Claude agree. {kent.reasoning}",
            confidence=max(kent.confidence, claude.confidence),
            evidence=kent.evidence + claude.evidence,
            principle_alignment={
                p: max(kent.principle_alignment.get(p, 0.5), claude.principle_alignment.get(p, 0.5))
                for p in self.PRINCIPLE_WEIGHTS.keys()
            },
            holder="consensus",
        )

        fusion = Fusion(
            id=generate_fusion_id(),
            topic=topic,
            timestamp=datetime.now(timezone.utc),
            kent_position=kent,
            claude_position=claude,
            synthesis=synthesis,
            result=FusionResult.CONSENSUS,
            reasoning="Positions are in fundamental agreement",
            trust_delta=self.TRUST_DELTAS[FusionResult.CONSENSUS],
        )

        self.store.add(fusion)
        return self._witness_fusion(fusion)

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_history(self, topic: str | None = None, limit: int = 10) -> list[Fusion]:
        """Get fusion history, optionally filtered by topic."""
        if topic:
            return self.store.get_by_topic(topic, limit)
        return self.store.get_recent(limit)

    def get_trust_trajectory(self) -> dict[str, Any]:
        """
        Analyze trust trajectory from fusion history.

        Returns:
            Dict with trajectory, trend, and current cumulative trust delta
        """
        fusions = self.store.get_recent(100)
        if not fusions:
            return {"trajectory": [], "trend": "neutral", "cumulative_delta": 0.0}

        # Reverse to get chronological order
        fusions = list(reversed(fusions))

        trajectory = []
        cumulative = 0.0

        for fusion in fusions:
            cumulative += fusion.trust_delta
            trajectory.append(
                {
                    "fusion_id": fusion.id,
                    "topic": fusion.topic,
                    "result": fusion.result.value,
                    "delta": fusion.trust_delta,
                    "cumulative": cumulative,
                    "timestamp": fusion.timestamp.isoformat(),
                }
            )

        # Compute trend from last 5 fusions
        if len(trajectory) >= 2:
            recent = trajectory[-5:]
            deltas: list[float] = [t["delta"] for t in recent]  # type: ignore[misc]
            avg_delta = sum(deltas) / len(deltas)

            if avg_delta > 0.02:
                trend = "increasing"
            elif avg_delta < -0.02:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trajectory": trajectory,
            "trend": trend,
            "cumulative_delta": cumulative,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "FusionId",
    "FusionResult",
    "Position",
    "Fusion",
    # Store
    "FusionStore",
    # Service
    "DialecticalFusionService",
    # Factories
    "generate_fusion_id",
    "create_position",
    # Global store access
    "get_fusion_store",
    "reset_fusion_store",
    # Protocol
    "LLMProvider",
]
