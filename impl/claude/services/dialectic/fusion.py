"""
Dialectical Fusion Service: Kent + Claude -> Synthesis via Cocone Construction.

This module implements E3 from the theory-operationalization plan (Chapter 17 of the
kgents monograph). It provides the categorical machinery for transforming disagreement
into constructive synthesis through dialectical fusion.

Theory Basis (Ch 17: Dialectical Fusion):
    Dialectical fusion operationalizes co-engineering between human (Kent) and AI (Claude):

    - **Kent and Claude each bring a Position**: Structured views with evidence and
      principle alignment scores
    - **Positions are evaluated**: Against the 7 Constitutional principles
    - **Synthesis attempts cocone construction**: Finding a position that preserves
      what's valid in both (though this is HEURISTIC, not categorical—see note below)
    - **Trust accumulates**: Through successful fusion, per Article V

Categorical Structure (Pushout/Cocone):
    In category theory, a cocone over a diagram is an object with morphisms from each
    diagram object that commute appropriately. For dialectical fusion:

    ::

        Kent's Position ──→ Synthesis ←── Claude's Position
              ↑                               ↑
              └──────── Common Ground ────────┘

    The synthesis is the "apex" of the cocone, and the projections from each position
    preserve the essential content of each view. A true categorical cocone would satisfy
    a universal property (uniqueness), but our LLM-based synthesis is a HEURISTIC
    approximation of this ideal.

    **IMPORTANT**: This implementation uses "heuristic synthesis" NOT a formal cocone.
    The type-level honesty principle (see Approximate[T] in 05-co-engineering.md) means
    we do not claim categorical optimality—we acknowledge the approximation explicitly.

The Emerging Constitution Articles:
    This service implements the Emerging Constitution's governance framework:

    I.   **Symmetric Agency**: All agents modeled identically (Kent ≅ Claude structurally)
    II.  **Adversarial Cooperation**: Challenge is structural, not hostile
    III. **Supersession Rights**: Any agent may be superseded (with justification)
    IV.  **The Disgust Veto**: Kent's somatic disgust is absolute veto (ETHICAL floor)
    V.   **Trust Accumulation**: Earned through demonstrated alignment
    VI.  **Fusion as Goal**: Fused decisions > individual decisions
    VII. **Amendment**: Constitution evolves through dialectical process

How Kent-Claude Tensions Fuse into Synthesis:
    1. **Position Structuring**: Raw views become Position objects with evidence,
       reasoning, confidence, and principle alignment scores
    2. **Consensus Check**: If positions fundamentally agree, immediate CONSENSUS result
    3. **Synthesis Attempt**: LLM generates a position that preserves both views' insights
    4. **Result Determination**: Apply Constitution rules (Article IV veto, Article VI
       fusion preference, Article III supersession)
    5. **Trust Delta**: Update trust based on outcome (synthesis builds most trust)
    6. **Witness Mark**: Record the fusion decision via Kleisli composition

Fusion Outcomes (FusionResult):
    - **CONSENSUS**: Article VI — Both agree, no synthesis needed
    - **SYNTHESIS**: Article VI — New position sublates both (best outcome)
    - **KENT_PREVAILS**: Article IV — Kent's position wins (may be veto)
    - **CLAUDE_PREVAILS**: Article III — Claude's position wins (with justification)
    - **DEFERRED**: Article II — More adversarial cooperation needed
    - **VETO**: Article IV — Kent's disgust veto (absolute, non-negotiable)

Philosophy:
    "Authority derives from quality of justification."
    "Challenge is nominative (structural) not substantive (hostile)."
    "Fusion is the goal; autonomy is earned."

Integration:
    - Uses Witness for recording fusion marks (via Kleisli composition from E1)
    - Uses TrustState from trust/gradient.py for trust tracking
    - Emits Witnessed[Fusion] containing both the result and its evidence trail

Zero Seed Grounding:
    This module derives from Constitution axioms:

    ::

        Article VI (Fusion as Goal) → Dialectical Fusion (E3)
          └─ "Fusion is the goal; autonomy is earned"
          └─ DialecticalFusionService implements Kent+Claude synthesis
          └─ Trust delta tracking honors Article V (Trust Gradient)

See: docs/theory/17-dialectic.md
See: plans/theory-operationalization/05-co-engineering.md (E3)
See: spec/protocols/constitution.md
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

    Each outcome maps to a specific Article of the Emerging Constitution and
    carries different trust implications. The outcomes form a hierarchy from
    most collaborative (SYNTHESIS) to most adversarial (VETO).

    Constitutional Mapping:
        - **CONSENSUS** (Article VI): Fusion achieved, both agree from the start.
          Trust delta: +0.10. This is agreement without conflict.

        - **SYNTHESIS** (Article VI): New position that sublates (preserves and
          transcends) both original positions. Trust delta: +0.15 (highest).
          This is the GOAL of dialectical fusion—constructive disagreement.

        - **KENT_PREVAILS** (Article IV): Kent's position wins, typically due to
          higher confidence or principle alignment. Trust delta: +0.05.
          Claude defers but learns from the decision.

        - **CLAUDE_PREVAILS** (Article III): Claude's position wins with
          justification. Trust delta: +0.08. Demonstrates Claude's reasoning
          capability and builds trust through successful challenge.

        - **DEFERRED** (Article II): Positions are too close to decide; more
          adversarial cooperation needed. Trust delta: 0.0. Neither position
          supersedes; the question remains open.

        - **VETO** (Article IV): Kent's disgust veto—absolute and non-negotiable.
          Trust delta: -0.10. This indicates significant misalignment and
          triggers trust erosion. The ETHICAL floor was violated.

    Trust Dynamics:
        The trust deltas reflect the Constitution's values:
        - Synthesis builds most trust (productive disagreement)
        - Veto erodes trust (indicates Claude misread Kent's values)
        - Prevailing builds moderate trust (successful competition)
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
    A structured position in the dialectic.

    In category theory terms, a Position is an object in the diagram that the
    cocone (synthesis) must span. Each position is a fully structured view with:

    - **Content**: The actual view/claim being advanced
    - **Reasoning**: The justification for holding this position
    - **Confidence**: Bayesian confidence in the position (0.0 - 1.0)
    - **Evidence**: Supporting evidence for the claim
    - **Principle Alignment**: Scores against the 7 Constitutional principles

    Constitutional Grounding:
        Positions are evaluated against the 7 principles:
        - TASTEFUL, CURATED, ETHICAL, JOY_INDUCING
        - COMPOSABLE, HETERARCHICAL, GENERATIVE

        The ETHICAL score is particularly important: if it falls below 0.3,
        this triggers potential veto consideration (Article IV).

    Categorical Role:
        In the cocone construction, each Position is a source object:

        ::

            Position_Kent ──projection──→ Synthesis
            Position_Claude ──projection──→ Synthesis

        The synthesis must "receive" both positions through projections that
        preserve their essential content.

    Attributes:
        content: The actual claim or view being advanced
        reasoning: Justification for the position
        confidence: Bayesian confidence level (0.0-1.0, clamped in post_init)
        evidence: List of supporting evidence strings
        principle_alignment: Dict mapping principle names to alignment scores (0.0-1.0)
        holder: Who holds this position ("kent", "claude", or "synthesis")
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
    A complete dialectical fusion record.

    This is the primary output of the DialecticalFusionService. It captures the
    entire dialectical process: both original positions, the attempted synthesis,
    the outcome, and the trust implications.

    Categorical Interpretation:
        A Fusion record represents a completed cocone construction attempt:

        ::

            Kent_Position ──→ Synthesis ←── Claude_Position
                   ↑                              ↑
                   └──── reasoning (witness) ─────┘

        The synthesis (if successful) is the apex of the cocone. The reasoning
        field documents HOW the synthesis was reached (the witness of the process).

    Constitutional Record:
        Every Fusion is a decision that affects the Kent-Claude relationship:

        - **Trust delta** changes cumulative trust (Article V)
        - **Result** records which Constitutional article governed the outcome
        - **Mark ID** links to the witness system for audit trail

    Relationship to Chapter 17:
        The theory describes dialectical fusion as the mechanism for resolving
        human-AI tensions constructively. This dataclass IS that mechanism's
        output—a complete record of how disagreement was transformed into
        decision (or deferred for further discussion).

    Attributes:
        id: Unique fusion identifier (fusion-{hex})
        topic: What's being decided
        timestamp: When the fusion occurred
        kent_position: Kent's structured view
        claude_position: Claude's structured view
        synthesis: The fused position (if CONSENSUS or SYNTHESIS achieved)
        result: The FusionResult outcome
        reasoning: Human-readable explanation of why this outcome was reached
        trust_delta: How much trust changed from this fusion
        mark_id: Link to witness mark for audit trail (set by _witness_fusion)
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

    This is the core E3 implementation from the theory-operationalization plan.
    It transforms disagreement into constructive synthesis by applying the
    Emerging Constitution's governance framework.

    The Fusion Pipeline:
        1. **Structure Positions**: Raw views become Position objects with evidence,
           reasoning, confidence, and principle alignment scores
        2. **Check Consensus**: If positions fundamentally agree, return CONSENSUS
        3. **Attempt Synthesis**: Use LLM to generate a position that sublates both
           (IMPORTANT: This is HEURISTIC synthesis, not a categorical cocone)
        4. **Determine Result**: Apply Constitution rules in order:
           - Article IV: Check ETHICAL floor (veto if violated)
           - Article VI: Prefer synthesis if confidence exceeds both positions
           - Article III: Higher confidence supersedes
           - Article II: Defer if positions are equal
        5. **Compute Trust Delta**: Update trust based on outcome
        6. **Record Witness**: Create mark via Kleisli composition

    Constitutional Governance:
        The service implements the Constitution's decision-making framework:

        - **Article IV** (Disgust Veto): If ETHICAL score < 0.3, VETO result
        - **Article VI** (Fusion as Goal): Synthesis preferred when viable
        - **Article III** (Supersession): Confidence > 0.1 difference decides
        - **Article II** (Adversarial Cooperation): Defer when equal

    Relationship to Chapter 17:
        Chapter 17 of the monograph establishes that dialectical fusion is how
        human-AI collaboration produces decisions superior to either party alone.
        This service IS that fusion mechanism—it's where Kent's taste and Claude's
        rigor meet to produce something neither would reach independently.

    Honest Naming (Type-Level Honesty):
        The _attempt_synthesis method produces HEURISTIC synthesis, NOT a
        categorical cocone. We explicitly acknowledge this limitation rather
        than claiming mathematical optimality. Future versions may wrap the
        result in Approximate[Cocone] to encode this at the type level.

    Attributes:
        llm: Optional LLM provider for synthesis and scoring
        store: FusionStore for persistence (default: global store)
        PRINCIPLE_WEIGHTS: Constitutional principle weights (ETHICAL highest)
        TRUST_DELTAS: Trust changes per outcome (SYNTHESIS highest positive)

    Example:
        >>> service = DialecticalFusionService(llm=my_llm)
        >>> witnessed_fusion = await service.propose_fusion(
        ...     topic="Database choice",
        ...     kent_view="Use Postgres",
        ...     kent_reasoning="Familiar, reliable",
        ...     claude_view="Use SQLite",
        ...     claude_reasoning="Simpler for prototyping",
        ... )
        >>> print(witnessed_fusion.value.result)  # FusionResult.SYNTHESIS
        >>> print(witnessed_fusion.marks)  # Witness mark for the fusion
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
        Attempt to synthesize a new position from Kent's and Claude's views.

        This implements the "heuristic cocone" construction from Chapter 17. The
        goal is to find a position that:

        1. Acknowledges the valid points in both positions
        2. Resolves the tension between them
        3. Preserves what's essential from each (sublation)
        4. Explains what each side contributes

        Type-Level Honesty Note:
            This is HEURISTIC synthesis, NOT a categorical cocone. A true cocone
            would satisfy the universal property: for any other cone over the same
            diagram, there exists a unique morphism to this cocone.

            We use LLM-based synthesis which is a practical approximation. The
            theory document 05-co-engineering.md proposes Approximate[Cocone] to
            encode this limitation at the type level. For now, we document it here.

        Categorical Aspiration:
            ::

                Kent ──projection_k──→ Synthesis ←──projection_c── Claude
                                          ↑
                                    (apex of cocone)

            The synthesis should "receive" both positions through projections
            that preserve their essential content.

        Args:
            topic: The decision topic
            kent: Kent's structured position
            claude: Claude's structured position

        Returns:
            Position representing the synthesis, or None if synthesis fails
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
