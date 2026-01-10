"""
AGENTESE Derivation Nodes.

Provides AGENTESE paths for Constitutional derivation operations:
- self.derivation.* - Query own derivation context
- concept.constitution.* - Constitutional operations
- world.kblock.derivation.* - K-Block derivation operations

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    "Every artifact justifies itself by tracing back to axioms."

Integration:
- services/derivation/service.py: DerivationService
- protocols/ashc/paths/types.py: DerivationPath types
- agents/d/galois.py: GaloisLossComputer

Teaching:
    gotcha: DerivationPath is generic over Source/Target but in practice
            we use Any since we're working with string IDs.
            (Evidence: protocols/ashc/paths/types.py::DerivationPath[Any, Any])

    gotcha: Galois loss accumulation: L(p;q) = 1 - (1-L(p))*(1-L(q))
            This ensures loss never decreases under composition.
            (Evidence: protocols/ashc/paths/types.py::DerivationPath.compose)

See: spec/protocols/zero-seed1/ashc.md
See: spec/k-block/derivation-context.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
from protocols.ashc.paths import DerivationPath

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# Constants
# =============================================================================

# The 7 Constitutional Principles (L2 layer)
CONSTITUTIONAL_PRINCIPLES: tuple[str, ...] = (
    "TASTEFUL",
    "CURATED",
    "ETHICAL",
    "JOY_INDUCING",
    "COMPOSABLE",
    "HETERARCHICAL",
    "GENERATIVE",
)

# Affordances for each node
SELF_DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "path",
    "grounded",
    "loss",
)

CONSTITUTION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "principles",
    "score",
    "ground",
)

KBLOCK_DERIVATION_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "compute",
    "suggest",
    "downstream",
)


# =============================================================================
# Contracts
# =============================================================================


@dataclass(frozen=True)
class DerivationPathResponse:
    """Response for derivation path query."""

    path_id: str | None
    source_id: str
    target_id: str
    galois_loss: float
    is_grounded: bool
    witnesses: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GroundedResponse:
    """Response for grounded check."""

    is_grounded: bool
    grounding_principle: str | None = None
    galois_loss: float = 0.0
    reasoning: str | None = None


@dataclass(frozen=True)
class LossResponse:
    """Response for Galois loss query."""

    galois_loss: float
    coherence: float
    tier: str  # "categorical", "empirical", "aesthetic", "somatic", "chaotic"


@dataclass(frozen=True)
class PrinciplesResponse:
    """Response listing constitutional principles."""

    principles: list[str]
    count: int


@dataclass(frozen=True)
class ScoreRequest:
    """Request to score content against principles."""

    content: str


@dataclass(frozen=True)
class ScoreResponse:
    """Response with principle scores."""

    scores: dict[str, float]
    overall_coherence: float
    dominant_principle: str | None = None


@dataclass(frozen=True)
class GroundRequest:
    """Request to ground an artifact to a principle."""

    artifact_id: str
    principle: str
    reasoning: str | None = None


@dataclass(frozen=True)
class GroundResponse:
    """Response from grounding operation."""

    success: bool
    path_id: str | None = None
    galois_loss: float = 0.0
    error: str | None = None


@dataclass(frozen=True)
class ComputeRequest:
    """Request to compute derivation for a K-Block."""

    kblock_id: str


@dataclass(frozen=True)
class ComputeResponse:
    """Response with K-Block derivation context."""

    kblock_id: str
    is_grounded: bool
    galois_loss: float
    principle_scores: dict[str, float]
    ancestors: list[str]
    created_by: str | None = None


@dataclass(frozen=True)
class SuggestRequest:
    """Request to suggest grounding for content."""

    content: str
    top_k: int = 5


@dataclass(frozen=True)
class SuggestResponse:
    """Response with suggested groundings."""

    suggestions: list[dict[str, Any]]


@dataclass(frozen=True)
class DownstreamRequest:
    """Request to get downstream K-Blocks."""

    kblock_id: str


@dataclass(frozen=True)
class DownstreamResponse:
    """Response with downstream K-Block IDs."""

    kblock_id: str
    downstream_ids: list[str]
    count: int


# =============================================================================
# self.derivation.* Node
# =============================================================================


@node(
    "self.derivation",
    description="Query own derivation context and grounding",
    contracts={
        "manifest": Response(DerivationPathResponse),
        "path": Response(DerivationPathResponse),
        "grounded": Response(GroundedResponse),
        "loss": Response(LossResponse),
    },
    examples=[
        ("manifest", {}, "Show current derivation context"),
        ("path", {}, "Get derivation path to current context"),
        ("grounded", {}, "Check if current context is grounded"),
        ("loss", {}, "Get accumulated Galois loss"),
    ],
)
@dataclass
class SelfDerivationNode(BaseLogosNode):
    """
    self.derivation - Query own derivation context.

    Enables agents to query their own derivation structure:
    - Am I grounded in Constitutional principles?
    - What is my Galois loss (semantic distance from axioms)?
    - What is the derivation path to my current context?

    Philosophy:
        "The observer asks 'Am I grounded?' not out of doubt,
         but as a categorical query against the derivation graph."
    """

    _handle: str = "self.derivation"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can query their own derivation."""
        return SELF_DERIVATION_AFFORDANCES

    def _get_derivation_service(self) -> Any:
        """Import DerivationService lazily to avoid circular imports."""
        from agents.d.universe import get_universe
        from services.derivation.service import DerivationService

        universe = get_universe()
        return DerivationService(universe)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS],
        help="Get derivation path for current context",
    )
    async def path(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Return the derivation path to the observer's current context.

        This queries the derivation graph for the path connecting
        the current context to its nearest grounded principle.
        """
        # Get observer context (session or agent ID)
        context_id = self._extract_context_id(observer)

        try:
            service = self._get_derivation_service()
            chain = await service.trace_to_axiom(context_id)

            content = f"""## Derivation Path: {context_id}

### Chain to Axioms

| Step | Crystal Type | Layer | Edge | Loss |
|------|--------------|-------|------|------|
"""
            for i, ref in enumerate(chain.chain):
                content += f"| {i + 1} | {ref.crystal_type} | L{ref.layer} | {ref.edge_kind} | {ref.galois_loss:.3f} |\n"

            if not chain.chain:
                content += "| (no derivation chain found) | — | — | — | — |\n"

            content += f"""
### Summary

- **Grounded**: {chain.is_grounded}
- **Total Loss**: {chain.total_galois_loss:.3f}
- **Coherence**: {chain.coherence():.1%}
"""

            return BasicRendering(
                summary=f"Derivation path: {'grounded' if chain.is_grounded else 'ungrounded'} (loss: {chain.total_galois_loss:.3f})",
                content=content,
                metadata={
                    "path_id": None,  # chain doesn't have a single ID
                    "source_id": context_id,
                    "target_id": chain.chain[-1].id if chain.chain else context_id,
                    "galois_loss": chain.total_galois_loss,
                    "is_grounded": chain.is_grounded,
                    "witnesses": [],
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error getting derivation path: {e}",
                content=f"Could not retrieve derivation path for {context_id}.\n\nError: {e}",
                metadata={
                    "path_id": None,
                    "source_id": context_id,
                    "target_id": context_id,
                    "galois_loss": 1.0,
                    "is_grounded": False,
                    "witnesses": [],
                },
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS],
        help="Check if current context is grounded in principles",
    )
    async def grounded(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Return whether the current context has principled grounding.

        Grounded = has a derivation path to L1/L2 axioms with acceptable loss.
        """
        context_id = self._extract_context_id(observer)

        try:
            service = self._get_derivation_service()
            chain = await service.trace_to_axiom(context_id)

            # Find the grounding principle if any
            grounding_principle = None
            for ref in reversed(chain.chain):
                if ref.layer in {1, 2}:
                    grounding_principle = ref.crystal_type.upper()
                    break

            status_emoji = "yes" if chain.is_grounded else "no"

            content = f"""## Grounding Check: {context_id}

### Is Grounded: {status_emoji}

| Metric | Value |
|--------|-------|
| **Grounded** | {chain.is_grounded} |
| **Grounding Principle** | {grounding_principle or "None"} |
| **Galois Loss** | {chain.total_galois_loss:.3f} |
| **Coherence** | {chain.coherence():.1%} |

### Interpretation

{
                f"This context is grounded in the **{grounding_principle}** principle with {chain.coherence():.0%} coherence."
                if chain.is_grounded
                else "This context lacks principled grounding. Consider adding derivation edges to Constitutional principles."
            }
"""

            return BasicRendering(
                summary=f"{'Grounded' if chain.is_grounded else 'Ungrounded'} ({chain.coherence():.0%} coherence)",
                content=content,
                metadata={
                    "is_grounded": chain.is_grounded,
                    "grounding_principle": grounding_principle,
                    "galois_loss": chain.total_galois_loss,
                    "reasoning": None,
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error checking grounding: {e}",
                content=f"Could not check grounding for {context_id}.\n\nError: {e}",
                metadata={
                    "is_grounded": False,
                    "grounding_principle": None,
                    "galois_loss": 1.0,
                    "reasoning": str(e),
                },
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS],
        help="Get Galois loss for current derivation context",
    )
    async def loss(self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Return the accumulated Galois loss to current context.

        Galois loss measures semantic distance from axioms.
        Lower loss = closer to grounded truth.
        """
        context_id = self._extract_context_id(observer)

        try:
            service = self._get_derivation_service()
            coherence_score = await service.coherence_check(context_id)
            galois_loss = 1.0 - coherence_score

            # Classify tier based on loss thresholds
            tier = self._classify_tier(galois_loss)

            content = f"""## Galois Loss: {context_id}

### Metrics

| Metric | Value |
|--------|-------|
| **Galois Loss** | {galois_loss:.3f} |
| **Coherence** | {coherence_score:.1%} |
| **Evidence Tier** | {tier.upper()} |

### Evidence Tier Interpretation

| Tier | Loss Range | Meaning |
|------|------------|---------|
| Categorical | < 0.10 | Near-lossless, deductive |
| Empirical | < 0.38 | Moderate loss, inductive |
| Aesthetic | < 0.45 | Taste-based judgment |
| Somatic | < 0.65 | Intuitive, embodied |
| Chaotic | >= 0.65 | High entropy, unreliable |

Current tier: **{tier.upper()}** ({galois_loss:.3f})
"""

            return BasicRendering(
                summary=f"Galois loss: {galois_loss:.3f} ({tier})",
                content=content,
                metadata={
                    "galois_loss": galois_loss,
                    "coherence": coherence_score,
                    "tier": tier,
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error getting Galois loss: {e}",
                content=f"Could not compute Galois loss for {context_id}.\n\nError: {e}",
                metadata={
                    "galois_loss": 1.0,
                    "coherence": 0.0,
                    "tier": "chaotic",
                },
            )

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Default manifest: show derivation path."""
        return await self.path(observer, **kwargs)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "path": self.path,
            "grounded": self.grounded,
            "loss": self.loss,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")

    def _extract_context_id(self, observer: Any) -> str:
        """Extract a context ID from the observer."""
        if hasattr(observer, "dna"):
            return getattr(observer.dna, "name", "observer")
        return "observer"

    def _classify_tier(self, loss: float) -> str:
        """Classify Galois loss into evidence tier."""
        if loss < 0.10:
            return "categorical"
        elif loss < 0.38:
            return "empirical"
        elif loss < 0.45:
            return "aesthetic"
        elif loss < 0.65:
            return "somatic"
        else:
            return "chaotic"


# =============================================================================
# concept.constitution.* Node
# =============================================================================


@node(
    "concept.constitution",
    description="Constitutional principles and grounding operations",
    contracts={
        "manifest": Response(PrinciplesResponse),
        "principles": Response(PrinciplesResponse),
        "score": Contract(ScoreRequest, ScoreResponse),
        "ground": Contract(GroundRequest, GroundResponse),
    },
    examples=[
        ("manifest", {}, "List constitutional principles"),
        ("principles", {}, "Show all 7 principles"),
        ("score", {"content": "tasteful design"}, "Score content against principles"),
        (
            "ground",
            {"artifact_id": "kb_123", "principle": "COMPOSABLE"},
            "Ground artifact to principle",
        ),
    ],
)
@dataclass
class ConstitutionNode(BaseLogosNode):
    """
    concept.constitution - Constitutional principles and grounding.

    Provides access to the 7 Constitutional principles (L2 layer)
    and operations for grounding artifacts to principles.

    The 7 Principles:
    1. TASTEFUL - Each agent serves a clear, justified purpose
    2. CURATED - Intentional selection over exhaustive cataloging
    3. ETHICAL - Agents augment human capability, never replace judgment
    4. JOY_INDUCING - Delight in interaction
    5. COMPOSABLE - Agents are morphisms in a category
    6. HETERARCHICAL - Agents exist in flux, not fixed hierarchy
    7. GENERATIVE - Spec is compression

    Philosophy:
        "The Constitution is not a set of rules.
         It's the axioms from which everything derives."
    """

    _handle: str = "concept.constitution"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can query constitution; grounding requires architect+."""
        if archetype.lower() in ("architect", "developer", "admin", "system"):
            return CONSTITUTION_AFFORDANCES
        return ("manifest", "principles", "score")

    def _get_galois_service(self) -> Any:
        """Import GaloisLossComputer lazily."""
        try:
            from services.zero_seed.galois import GaloisLossComputer

            return GaloisLossComputer()
        except ImportError:
            return None

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List the 7 Constitutional principles",
    )
    async def principles(
        self, observer: Observer | "Umwelt[Any, Any]", **kwargs: Any
    ) -> Renderable:
        """Return the 7 principles: TASTEFUL, CURATED, ETHICAL, etc."""
        content = """## Constitutional Principles (L2)

> *"The Constitution is not a set of rules. It's the axioms from which everything derives."*

### The 7 Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **TASTEFUL** | Each agent serves a clear, justified purpose |
| 2 | **CURATED** | Intentional selection over exhaustive cataloging |
| 3 | **ETHICAL** | Agents augment human capability, never replace judgment |
| 4 | **JOY_INDUCING** | Delight in interaction |
| 5 | **COMPOSABLE** | Agents are morphisms in a category |
| 6 | **HETERARCHICAL** | Agents exist in flux, not fixed hierarchy |
| 7 | **GENERATIVE** | Spec is compression |

### Usage

- `concept.constitution.score content="..."` - Score content against principles
- `concept.constitution.ground artifact_id=... principle=...` - Ground artifact
"""

        return BasicRendering(
            summary="7 Constitutional principles",
            content=content,
            metadata={
                "principles": list(CONSTITUTIONAL_PRINCIPLES),
                "count": len(CONSTITUTIONAL_PRINCIPLES),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS, Effect.CALLS],
        help="Score content against Constitutional principles",
        budget_estimate="~100 tokens",
    )
    async def score(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        content: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Return principle scores for the given content."""
        if not content:
            return BasicRendering(
                summary="score requires content parameter",
                content='Usage: `kg concept.constitution.score content="your content here"`',
                metadata={"scores": {}, "overall_coherence": 0.0, "dominant_principle": None},
            )

        galois = self._get_galois_service()

        # Score against each principle
        scores: dict[str, float] = {}
        for principle in CONSTITUTIONAL_PRINCIPLES:
            if galois:
                try:
                    loss = await galois.compute_loss(content, principle.lower())
                    scores[principle] = 1.0 - loss
                except Exception:
                    scores[principle] = 0.5  # Default if computation fails
            else:
                # Heuristic scoring without LLM
                scores[principle] = self._heuristic_score(content, principle)

        overall = sum(scores.values()) / len(scores) if scores else 0.0
        dominant = max(scores, key=lambda x: scores.get(x, 0.0)) if scores else None

        # Format score bars
        score_lines = []
        for principle in CONSTITUTIONAL_PRINCIPLES:
            score = scores.get(principle, 0.0)
            bar_length = int(score * 20)
            bar = "#" * bar_length + "-" * (20 - bar_length)
            score_lines.append(f"| {principle} | [{bar}] | {score:.2f} |")

        result_content = f"""## Constitutional Score

**Content**: "{content[:100]}{"..." if len(content) > 100 else ""}"

### Principle Scores

| Principle | Score Bar | Value |
|-----------|-----------|-------|
{chr(10).join(score_lines)}

### Summary

- **Overall Coherence**: {overall:.1%}
- **Dominant Principle**: {dominant}
- **Interpretation**: {"Content aligns well with Constitutional principles." if overall > 0.7 else "Content may need refinement for better alignment."}
"""

        return BasicRendering(
            summary=f"Overall coherence: {overall:.1%} (dominant: {dominant})",
            content=result_content,
            metadata={
                "scores": scores,
                "overall_coherence": overall,
                "dominant_principle": dominant,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES],
        help="Ground an artifact to a Constitutional principle",
        required_capability="write",
    )
    async def ground(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        artifact_id: str | None = None,
        principle: str | None = None,
        reasoning: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Create derivation edge from principle to artifact."""
        if not artifact_id or not principle:
            return BasicRendering(
                summary="ground requires artifact_id and principle",
                content="Usage: `kg concept.constitution.ground artifact_id=<id> principle=<name>`\n\n"
                f"Valid principles: {', '.join(CONSTITUTIONAL_PRINCIPLES)}",
                metadata={"success": False, "error": "missing_params"},
            )

        # Validate principle
        principle_upper = principle.upper()
        if principle_upper not in CONSTITUTIONAL_PRINCIPLES:
            return BasicRendering(
                summary=f"Invalid principle: {principle}",
                content=f"'{principle}' is not a valid Constitutional principle.\n\n"
                f"Valid principles: {', '.join(CONSTITUTIONAL_PRINCIPLES)}",
                metadata={"success": False, "error": "invalid_principle"},
            )

        try:
            from agents.d.universe import get_universe
            from services.derivation.service import DerivationService

            universe = get_universe()
            service = DerivationService(universe)

            edge_id = await service.link_derivation(
                source_id=artifact_id,
                target_id=f"principle:{principle_upper}",
                edge_kind="GROUNDS",
                context=reasoning,
            )

            # Compute resulting loss
            coherence = await service.coherence_check(artifact_id)
            loss = 1.0 - coherence

            return BasicRendering(
                summary=f"Grounded {artifact_id} to {principle_upper}",
                content=f"""## Grounding Created

**Artifact**: {artifact_id}
**Principle**: {principle_upper}
**Edge ID**: {edge_id}
**Galois Loss**: {loss:.3f}

### Interpretation

Artifact '{artifact_id}' is now derivationally grounded in the **{principle_upper}** principle.
{f"Reasoning: {reasoning}" if reasoning else ""}
""",
                metadata={
                    "success": True,
                    "path_id": edge_id,
                    "galois_loss": loss,
                    "error": None,
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error creating grounding: {e}",
                content=f"Could not ground {artifact_id} to {principle}.\n\nError: {e}",
                metadata={
                    "success": False,
                    "path_id": None,
                    "galois_loss": 1.0,
                    "error": str(e),
                },
            )

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Default manifest: show principles."""
        return await self.principles(observer, **kwargs)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "principles": self.principles,
            "score": self.score,
            "ground": self.ground,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")

    def _heuristic_score(self, content: str, principle: str) -> float:
        """Heuristic scoring without LLM."""
        content_lower = content.lower()
        principle_lower = principle.lower()

        # Simple keyword matching as fallback
        keywords: dict[str, list[str]] = {
            "tasteful": ["tasteful", "elegant", "refined", "purposeful", "justified"],
            "curated": ["curated", "intentional", "selected", "chosen", "specific"],
            "ethical": ["ethical", "augment", "human", "judgment", "responsible"],
            "joy_inducing": ["joy", "delight", "pleasant", "enjoyable", "satisfying"],
            "composable": ["compose", "morphism", "category", "combine", "modular"],
            "heterarchical": ["flux", "dynamic", "evolving", "adaptive", "non-fixed"],
            "generative": ["generative", "compression", "minimal", "concise", "essential"],
        }

        principle_keywords = keywords.get(principle_lower, [])
        matches = sum(1 for kw in principle_keywords if kw in content_lower)
        return min(0.3 + (matches * 0.15), 1.0)


# =============================================================================
# world.kblock.derivation.* Node
# =============================================================================


@node(
    "world.kblock.derivation",
    description="K-Block derivation operations",
    contracts={
        "manifest": Response(ComputeResponse),
        "compute": Contract(ComputeRequest, ComputeResponse),
        "suggest": Contract(SuggestRequest, SuggestResponse),
        "downstream": Contract(DownstreamRequest, DownstreamResponse),
    },
    examples=[
        ("manifest", {}, "Show derivation overview"),
        ("compute", {"kblock_id": "kb_123"}, "Compute derivation for K-Block"),
        ("suggest", {"content": "new feature spec"}, "Suggest groundings for content"),
        ("downstream", {"kblock_id": "kb_123"}, "Get downstream K-Blocks"),
    ],
)
@dataclass
class KBlockDerivationNode(BaseLogosNode):
    """
    world.kblock.derivation - K-Block derivation operations.

    Provides derivation context for K-Blocks:
    - Compute derivation status and Galois loss
    - Suggest groundings for orphan K-Blocks
    - Find downstream dependents

    Philosophy:
        "The K-Block is not where you edit a document.
         It's where you edit a possible world—with derivational guarantees."
    """

    _handle: str = "world.kblock.derivation"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can query derivation; suggest requires architect+."""
        if archetype.lower() in ("architect", "developer", "admin", "system"):
            return KBLOCK_DERIVATION_AFFORDANCES
        return ("manifest", "compute", "downstream")

    def _get_derivation_service(self) -> Any:
        """Import DerivationService lazily."""
        from agents.d.universe import get_universe
        from services.derivation.service import DerivationService

        universe = get_universe()
        return DerivationService(universe)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS],
        help="Compute derivation context for a K-Block",
    )
    async def compute(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kblock_id: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Compute and return derivation context for the K-Block."""
        if not kblock_id:
            return BasicRendering(
                summary="compute requires kblock_id parameter",
                content="Usage: `kg world.kblock.derivation.compute kblock_id=<id>`",
                metadata={
                    "kblock_id": "",
                    "is_grounded": False,
                    "galois_loss": 1.0,
                    "principle_scores": {},
                    "ancestors": [],
                    "created_by": None,
                },
            )

        try:
            service = self._get_derivation_service()
            tree = await service.get_derivation_tree(kblock_id)

            # Extract principle scores from ancestors
            principle_scores: dict[str, float] = {}
            for ancestor in tree.ancestors:
                if ancestor.layer in {1, 2}:
                    principle_scores[ancestor.crystal_type] = 1.0 - ancestor.galois_loss

            ancestor_ids = [a.id for a in tree.ancestors[:10]]

            content = f"""## K-Block Derivation: {kblock_id}

### Status

| Metric | Value |
|--------|-------|
| **Grounded** | {tree.is_grounded} |
| **Total Loss** | {tree.total_loss_to_axioms:.3f} |
| **Ancestors** | {len(tree.ancestors)} |
| **Descendants** | {len(tree.descendants)} |

### Ancestor Chain (to axioms)

| # | ID | Type | Layer | Loss |
|---|-----|------|-------|------|
"""
            for i, ancestor in enumerate(tree.ancestors[:10]):
                content += f"| {i + 1} | {ancestor.id[:12]}... | {ancestor.crystal_type} | L{ancestor.layer} | {ancestor.galois_loss:.3f} |\n"

            if not tree.ancestors:
                content += "| (no ancestors found) | — | — | — | — |\n"

            content += """
### Principle Alignment

"""
            for principle, score in principle_scores.items():
                content += f"- **{principle.upper()}**: {score:.1%}\n"

            if not principle_scores:
                content += "(No principle alignment detected)\n"

            return BasicRendering(
                summary=f"K-Block {kblock_id[:12]}... {'grounded' if tree.is_grounded else 'orphan'} (loss: {tree.total_loss_to_axioms:.3f})",
                content=content,
                metadata={
                    "kblock_id": kblock_id,
                    "is_grounded": tree.is_grounded,
                    "galois_loss": tree.total_loss_to_axioms,
                    "principle_scores": principle_scores,
                    "ancestors": ancestor_ids,
                    "created_by": None,
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error computing derivation: {e}",
                content=f"Could not compute derivation for {kblock_id}.\n\nError: {e}",
                metadata={
                    "kblock_id": kblock_id,
                    "is_grounded": False,
                    "galois_loss": 1.0,
                    "principle_scores": {},
                    "ancestors": [],
                    "created_by": None,
                },
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS, Effect.CALLS],
        help="Suggest grounding for orphan content",
        budget_estimate="~200 tokens",
    )
    async def suggest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        content: str | None = None,
        top_k: int = 5,
        **kwargs: Any,
    ) -> Renderable:
        """Return suggested groundings sorted by Galois loss."""
        if not content:
            return BasicRendering(
                summary="suggest requires content parameter",
                content='Usage: `kg world.kblock.derivation.suggest content="your content"`',
                metadata={"suggestions": []},
            )

        suggestions: list[dict[str, Any]] = []

        # Score content against each principle
        for principle in CONSTITUTIONAL_PRINCIPLES:
            # Compute affinity using heuristic or Galois
            galois = None
            try:
                from services.zero_seed.galois import GaloisLossComputer

                galois = GaloisLossComputer()
            except ImportError:
                pass

            if galois:
                try:
                    loss = await galois.compute_loss(content)
                except Exception:
                    loss = 0.5
            else:
                loss = 0.5

            suggestions.append(
                {
                    "principle": principle,
                    "galois_loss": loss,
                    "coherence": 1.0 - loss,
                    "reasoning": f"Align with {principle} principle",
                }
            )

        # Sort by loss (lower is better)
        suggestions.sort(key=lambda s: s["galois_loss"])
        suggestions = suggestions[:top_k]

        content_text = f"""## Grounding Suggestions

**Content**: "{content[:100]}{"..." if len(content) > 100 else ""}"

### Top {len(suggestions)} Suggestions (by Galois Loss)

| Rank | Principle | Loss | Coherence |
|------|-----------|------|-----------|
"""
        for i, sug in enumerate(suggestions, 1):
            content_text += f"| {i} | {sug['principle']} | {sug['galois_loss']:.3f} | {sug['coherence']:.1%} |\n"

        content_text += f"""
### Recommendation

Best grounding: **{suggestions[0]["principle"]}** (loss: {suggestions[0]["galois_loss"]:.3f})

To ground this content:
```
kg concept.constitution.ground artifact_id=<your_id> principle={suggestions[0]["principle"]}
```
"""

        return BasicRendering(
            summary=f"Best grounding: {suggestions[0]['principle']} (loss: {suggestions[0]['galois_loss']:.3f})",
            content=content_text,
            metadata={"suggestions": suggestions},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS],
        help="Get K-Blocks that derive from this one",
    )
    async def downstream(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        kblock_id: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """Return IDs of K-Blocks that derive from this one."""
        if not kblock_id:
            return BasicRendering(
                summary="downstream requires kblock_id parameter",
                content="Usage: `kg world.kblock.derivation.downstream kblock_id=<id>`",
                metadata={"kblock_id": "", "downstream_ids": [], "count": 0},
            )

        try:
            service = self._get_derivation_service()
            tree = await service.get_derivation_tree(kblock_id)

            downstream_ids = [d.id for d in tree.descendants]

            content = f"""## Downstream K-Blocks: {kblock_id}

### Dependents ({len(downstream_ids)} total)

| # | K-Block ID | Type | Layer |
|---|------------|------|-------|
"""
            for i, desc in enumerate(tree.descendants[:20]):
                content += (
                    f"| {i + 1} | {desc.id[:12]}... | {desc.crystal_type} | L{desc.layer} |\n"
                )

            if not tree.descendants:
                content += "| (no downstream K-Blocks) | — | — | — |\n"

            if len(tree.descendants) > 20:
                content += f"\n... and {len(tree.descendants) - 20} more\n"

            content += f"""
### Impact Analysis

Changes to **{kblock_id}** will affect **{len(downstream_ids)}** downstream K-Blocks.
"""

            return BasicRendering(
                summary=f"{len(downstream_ids)} downstream K-Blocks",
                content=content,
                metadata={
                    "kblock_id": kblock_id,
                    "downstream_ids": downstream_ids[:100],
                    "count": len(downstream_ids),
                },
            )
        except Exception as e:
            return BasicRendering(
                summary=f"Error getting downstream: {e}",
                content=f"Could not get downstream for {kblock_id}.\n\nError: {e}",
                metadata={"kblock_id": kblock_id, "downstream_ids": [], "count": 0},
            )

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Default manifest: show overview."""
        content = """## K-Block Derivation Overview

> *"Every K-Block justifies itself by tracing back to axioms."*

### Available Operations

| Aspect | Description |
|--------|-------------|
| `compute` | Compute derivation context for a K-Block |
| `suggest` | Suggest groundings for orphan content |
| `downstream` | Find K-Blocks that derive from this one |

### Usage Examples

```bash
# Compute derivation for a K-Block
kg world.kblock.derivation.compute kblock_id=kb_123

# Get grounding suggestions for new content
kg world.kblock.derivation.suggest content="new feature spec"

# Find downstream dependents
kg world.kblock.derivation.downstream kblock_id=kb_123
```

### Philosophy

The K-Block derivation system ensures that every piece of content
has a traceable lineage back to Constitutional principles.

Orphan K-Blocks (without grounding) are valid but represent
"unproven assertions"—they exist without principled justification.
"""

        return BasicRendering(
            summary="K-Block derivation operations",
            content=content,
            metadata={
                "kblock_id": "",
                "is_grounded": False,
                "galois_loss": 0.0,
                "principle_scores": {},
                "ancestors": [],
                "created_by": None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        methods: dict[str, Any] = {
            "compute": self.compute,
            "suggest": self.suggest,
            "downstream": self.downstream,
        }

        if aspect in methods:
            return await methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Factory Functions
# =============================================================================

_self_derivation_node: SelfDerivationNode | None = None
_constitution_node: ConstitutionNode | None = None
_kblock_derivation_node: KBlockDerivationNode | None = None


def get_self_derivation_node() -> SelfDerivationNode:
    """Get or create the singleton SelfDerivationNode."""
    global _self_derivation_node
    if _self_derivation_node is None:
        _self_derivation_node = SelfDerivationNode()
    return _self_derivation_node


def get_constitution_node() -> ConstitutionNode:
    """Get or create the singleton ConstitutionNode."""
    global _constitution_node
    if _constitution_node is None:
        _constitution_node = ConstitutionNode()
    return _constitution_node


def get_kblock_derivation_node() -> KBlockDerivationNode:
    """Get or create the singleton KBlockDerivationNode."""
    global _kblock_derivation_node
    if _kblock_derivation_node is None:
        _kblock_derivation_node = KBlockDerivationNode()
    return _kblock_derivation_node


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Nodes
    "SelfDerivationNode",
    "ConstitutionNode",
    "KBlockDerivationNode",
    # Factory functions
    "get_self_derivation_node",
    "get_constitution_node",
    "get_kblock_derivation_node",
    # Affordances
    "SELF_DERIVATION_AFFORDANCES",
    "CONSTITUTION_AFFORDANCES",
    "KBLOCK_DERIVATION_AFFORDANCES",
    # Constants
    "CONSTITUTIONAL_PRINCIPLES",
    # Contracts
    "DerivationPathResponse",
    "GroundedResponse",
    "LossResponse",
    "PrinciplesResponse",
    "ScoreRequest",
    "ScoreResponse",
    "GroundRequest",
    "GroundResponse",
    "ComputeRequest",
    "ComputeResponse",
    "SuggestRequest",
    "SuggestResponse",
    "DownstreamRequest",
    "DownstreamResponse",
]
