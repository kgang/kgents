"""
Galois Loss Computation for Zero Seed.

Core formula: L(P) = d(P, C(R(P)))

Where:
- R: Prompt -> ModularPrompt (restructure via LLM)
- C: ModularPrompt -> Prompt (reconstitute via LLM)
- d: Prompt x Prompt -> [0,1] (semantic distance)

Philosophy:
    "The loss IS the layer. The fixed point IS the axiom.
     The contradiction IS the super-additive signal."

The Galois adjunction R -| C defines:
- Axioms as zero-loss fixed points: L(axiom) < epsilon_1
- Layers via convergence depth: layer(P) = argmin_n L(R^n(P)) < epsilon
- Contradictions via super-additivity: L(A U B) > L(A) + L(B) + tau

See: spec/protocols/zero-seed1/galois.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .distance import (
    BERTScoreDistance,
    SemanticDistanceMetric,
    get_default_metric,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from agents.k.llm import LLMClient as AgentLLMClient


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Fixed-point threshold for axiom detection
FIXED_POINT_THRESHOLD: float = 0.05  # epsilon_1

# Contradiction detection tolerance
CONTRADICTION_TOLERANCE: float = 0.1  # tau

# Explosion prevention threshold
EXPLOSION_THRESHOLD: float = 0.6

# Layer loss bounds (from spec Part I)
LAYER_LOSS_BOUNDS: dict[int, tuple[float, float]] = {
    1: (0.00, 0.05),  # Axioms: near-zero loss
    2: (0.05, 0.15),  # Values: low loss
    3: (0.15, 0.30),  # Goals: moderate loss
    4: (0.30, 0.45),  # Specs: medium loss
    5: (0.45, 0.60),  # Execution: higher loss
    6: (0.60, 0.75),  # Reflection: high loss
    7: (0.75, 1.00),  # Representation: maximum loss
}

LAYER_NAMES: dict[int, str] = {
    1: "Axiom",
    2: "Value",
    3: "Goal",
    4: "Spec",
    5: "Execution",
    6: "Reflection",
    7: "Representation",
}


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class ContradictionType(Enum):
    """Classification of contradiction by strength."""

    NONE = auto()  # Compatible or synergistic
    WEAK = auto()  # Surface tension only (strength 0.1-0.2)
    MODERATE = auto()  # Resolvable via synthesis (0.2-0.5)
    STRONG = auto()  # Irreconcilable (>0.5)


class EvidenceTier(Enum):
    """
    Evidence tier based on Galois loss.

    Kent calibration (2025-12-28):
    - CATEGORICAL: L < 0.10 (near-lossless, deductive)
    - EMPIRICAL: L < 0.38 (moderate loss, inductive)
    - AESTHETIC: L < 0.45 (taste-based judgment)
    - SOMATIC: L < 0.65 (intuitive, embodied)
    - CHAOTIC: L >= 0.65 (high entropy, unreliable)
    """

    CATEGORICAL = auto()  # Near-lossless (deductive), L < 0.10
    EMPIRICAL = auto()  # Moderate loss (inductive), L < 0.38
    AESTHETIC = auto()  # Taste-based judgment, L < 0.45
    SOMATIC = auto()  # Intuitive/embodied, L < 0.65
    CHAOTIC = auto()  # High entropy/unreliable, L >= 0.65


# -----------------------------------------------------------------------------
# LLM Client Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Protocol for LLM client used in restructure/reconstitute."""

    async def restructure(self, content: str) -> ModularPrompt:
        """
        R: Prompt -> ModularPrompt

        Decompose prompt into modular components.
        """
        ...

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """
        C: ModularPrompt -> Prompt

        Reconstitute prompt from modular representation.
        """
        ...


# -----------------------------------------------------------------------------
# Modular Prompt Representation
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ModularComponent:
    """A single component in a modular prompt."""

    name: str
    content: str
    weight: float = 1.0  # Importance in reconstitution
    dependencies: tuple[str, ...] = ()  # Other components this depends on


@dataclass(frozen=True)
class GhostAlternative:
    """
    A deferred restructuring alternative.

    Represents paths not taken during restructuring.
    Used for synthesis hints in contradiction resolution.
    """

    content: str
    rationale: str
    deferral_cost: float  # Cost of not choosing this path


@dataclass
class ModularPrompt:
    """
    The output of restructuring R(P).

    Represents a prompt decomposed into modular components.
    May include ghost alternatives (paths not taken).
    """

    components: list[ModularComponent]
    ghosts: list[GhostAlternative] = field(default_factory=list)
    structure_notes: str = ""  # How components relate

    def to_text(self) -> str:
        """Serialize for reconstitution."""
        parts = []
        for comp in self.components:
            parts.append(f"[{comp.name}]\n{comp.content}")
        return "\n\n".join(parts)


# -----------------------------------------------------------------------------
# Loss Cache
# -----------------------------------------------------------------------------


@dataclass
class LossCacheEntry:
    """A cached loss computation result."""

    loss: float
    computed_at: datetime
    metric_name: str


class LossCache:
    """
    Cache for Galois loss computations.

    Loss computation is expensive (LLM calls). This cache
    stores results keyed by content hash.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: dict[str, dict[str, LossCacheEntry]] = {}
        self._max_size = max_size

    def _content_hash(self, content: str) -> str:
        """Hash content for cache key."""
        import hashlib

        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, content: str, loss_type: str) -> float | None:
        """
        Get cached loss if available.

        Args:
            content: The content that was analyzed
            loss_type: Type of loss (node_loss, edge_loss, etc.)

        Returns:
            Cached loss value or None
        """
        key = self._content_hash(content)
        if key in self._cache and loss_type in self._cache[key]:
            return self._cache[key][loss_type].loss
        return None

    def set(
        self,
        content: str,
        loss_type: str,
        loss: float,
        metric_name: str = "default",
    ) -> None:
        """
        Store computed loss in cache.

        Args:
            content: The content that was analyzed
            loss_type: Type of loss
            loss: Computed loss value
            metric_name: Metric used for computation
        """
        key = self._content_hash(content)

        # Evict oldest if at capacity
        if len(self._cache) >= self._max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        if key not in self._cache:
            self._cache[key] = {}

        self._cache[key][loss_type] = LossCacheEntry(
            loss=loss,
            computed_at=datetime.now(timezone.utc),
            metric_name=metric_name,
        )

    def invalidate(self, content: str) -> None:
        """Remove all cached losses for content."""
        key = self._content_hash(content)
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()


# -----------------------------------------------------------------------------
# Default LLM Implementation
# -----------------------------------------------------------------------------


class SimpleLLMClient:
    """
    Simple LLM client implementation using kgents LLM abstraction.

    Uses the kgents LLM abstraction from agents/k/llm.py which routes
    through ClaudeCLIRuntime or MorpheusLLMClient.

    For production, use a proper DI-injected client.
    This is a reference implementation.
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514") -> None:
        self.model = model
        self._client: AgentLLMClient | None = None

    def _get_client(self) -> AgentLLMClient:
        """Get or create kgents LLM client."""
        if self._client is None:
            from agents.k.llm import create_llm_client

            self._client = create_llm_client(model=self.model)
        return self._client

    async def restructure(self, content: str) -> ModularPrompt:
        """
        Restructure content into modular components.

        Uses LLM to identify distinct conceptual units.
        """
        prompt = f"""Analyze this text and break it into distinct conceptual components.

For each component, identify:
1. A short name (2-3 words)
2. The core content
3. Dependencies on other components

Text to analyze:
{content}

Respond in this format:
COMPONENT: <name>
CONTENT: <content>
DEPENDS: <comma-separated component names, or NONE>

---

List all components, separated by ---.
If there are alternative ways to structure this, note them at the end as GHOST alternatives."""

        try:
            client = self._get_client()
            response = await client.generate(
                system="You are a text analysis assistant that breaks text into modular components.",
                user=prompt,
                max_tokens=2000,
            )

            text = response.text
            return self._parse_restructure_response(text)

        except Exception:
            # Fallback: treat entire content as single component
            return ModularPrompt(
                components=[
                    ModularComponent(
                        name="main",
                        content=content,
                        weight=1.0,
                        dependencies=(),
                    )
                ]
            )

    def _parse_restructure_response(self, text: str) -> ModularPrompt:
        """Parse LLM response into ModularPrompt."""
        components: list[ModularComponent] = []
        ghosts: list[GhostAlternative] = []

        # Split by separator
        parts = text.split("---")

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check for ghost
            if part.startswith("GHOST"):
                lines = part.split("\n", 1)
                if len(lines) > 1:
                    ghosts.append(
                        GhostAlternative(
                            content=lines[1].strip(),
                            rationale="Alternative restructuring",
                            deferral_cost=0.1,
                        )
                    )
                continue

            # Parse component
            name = "unnamed"
            content = ""
            depends: tuple[str, ...] = ()

            for line in part.split("\n"):
                line = line.strip()
                if line.startswith("COMPONENT:"):
                    name = line[10:].strip()
                elif line.startswith("CONTENT:"):
                    content = line[8:].strip()
                elif line.startswith("DEPENDS:"):
                    deps_str = line[8:].strip()
                    if deps_str.upper() != "NONE":
                        depends = tuple(d.strip() for d in deps_str.split(","))

            if content:
                components.append(
                    ModularComponent(
                        name=name,
                        content=content,
                        weight=1.0,
                        dependencies=depends,
                    )
                )

        # Ensure at least one component
        if not components:
            components.append(
                ModularComponent(
                    name="main",
                    content=text,
                    weight=1.0,
                    dependencies=(),
                )
            )

        return ModularPrompt(components=components, ghosts=ghosts)

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """
        Reconstitute modular components back into coherent text.

        Uses LLM to blend components while preserving meaning.
        """
        prompt = f"""Reconstitute these components into coherent, natural text.

Preserve the semantic content of each component while making the
whole text flow naturally.

Components:
{modular.to_text()}

{f"Structure notes: {modular.structure_notes}" if modular.structure_notes else ""}

Write the reconstituted text. Do not add any commentary, just the text itself."""

        try:
            client = self._get_client()
            response = await client.generate(
                system="You are a text synthesis assistant that combines components into coherent text.",
                user=prompt,
                max_tokens=2000,
            )

            return response.text.strip()

        except Exception:
            # Fallback: concatenate components
            return modular.to_text()


# -----------------------------------------------------------------------------
# Core Galois Loss Computer
# -----------------------------------------------------------------------------


@dataclass
class GaloisLossComputer:
    """
    Core Galois loss computation.

    Implements L(P) = d(P, C(R(P))) for various content types.

    From spec Part II: "Galois Loss as THE Fundamental Metric"
    """

    llm: LLMClientProtocol = field(default_factory=SimpleLLMClient)
    metric: SemanticDistanceMetric = field(default_factory=get_default_metric)
    cache: LossCache = field(default_factory=LossCache)

    async def compute_loss(self, content: str, use_cache: bool = True) -> float:
        """
        Compute L(content) = d(content, C(R(content))).

        This is the core Galois loss formula.

        Args:
            content: Any textual content
            use_cache: Whether to use cached results (default: True)

        Returns:
            Loss in [0, 1] where 0 = perfect preservation
        """
        # Check cache
        if use_cache:
            cached = self.cache.get(content, "raw_loss")
            if cached is not None:
                return cached

        # Restructure
        modular = await self.llm.restructure(content)

        # Reconstitute
        reconstituted = await self.llm.reconstitute(modular)

        # Measure distance
        loss = self.metric.distance(content, reconstituted)

        # Cache result
        if use_cache:
            self.cache.set(content, "raw_loss", loss, self.metric.name)

        return loss

    async def node_loss(self, content: str, node_id: str | None = None) -> float:
        """
        Compute loss for a node's content.

        Wrapper around compute_loss with node-specific caching.
        """
        cache_key = f"node:{node_id}" if node_id else "node_anonymous"
        cached = self.cache.get(content, cache_key)
        if cached is not None:
            return cached

        loss = await self.compute_loss(content)
        self.cache.set(content, cache_key, loss, self.metric.name)
        return loss

    async def edge_loss(
        self,
        source_content: str,
        edge_kind: str,
        target_content: str,
        source_layer: int = 0,
        target_layer: int = 0,
    ) -> float:
        """
        Compute loss for an edge transition.

        Measures semantic coherence lost when traversing edge.

        Args:
            source_content: Source node content
            edge_kind: Type of edge (justifies, specifies, etc.)
            target_content: Target node content
            source_layer: Source node layer (optional)
            target_layer: Target node layer (optional)

        Returns:
            Edge transition loss
        """
        # Construct transition description
        transition = f"""
From: L{source_layer} node
{source_content[:500]}

Via: {edge_kind}

To: L{target_layer} node
{target_content[:500]}
"""

        cached = self.cache.get(transition, "edge_loss")
        if cached is not None:
            return cached

        loss = await self.compute_loss(transition)
        self.cache.set(transition, "edge_loss", loss, self.metric.name)
        return loss

    async def proof_loss(self, proof_text: str) -> float:
        """
        Compute loss for a Toulmin proof.

        Coherence = 1 - loss.

        Args:
            proof_text: Serialized proof (Toulmin format)

        Returns:
            Proof loss (lower = more coherent)
        """
        cached = self.cache.get(proof_text, "proof_loss")
        if cached is not None:
            return cached

        loss = await self.compute_loss(proof_text)
        self.cache.set(proof_text, "proof_loss", loss, self.metric.name)
        return loss

    def coherence_from_loss(self, loss: float) -> float:
        """
        Convert loss to coherence.

        coherence = 1 - loss

        Args:
            loss: Galois loss value

        Returns:
            Coherence in [0, 1]
        """
        return 1.0 - loss


# -----------------------------------------------------------------------------
# Layer Assignment
# -----------------------------------------------------------------------------


@dataclass
class LayerAssignment:
    """Result of automatic layer assignment."""

    layer: int
    loss: float
    loss_by_layer: dict[int, float]
    confidence: float
    insight: str
    rationale: str


async def assign_layer_via_galois(
    content: str,
    computer: GaloisLossComputer,
) -> LayerAssignment:
    """
    Assign content to the layer where it has minimal loss.

    This DERIVES layer assignment rather than requiring manual choice.

    From spec Part VI: "Layer Assignment via Loss Minimization"
    """
    losses: dict[int, float] = {}

    # Compute loss at each layer (simulate layer context)
    for layer in range(1, 8):
        # Add layer context to content
        layer_context = f"[Layer {layer}: {LAYER_NAMES[layer]}]\n{content}"
        loss = await computer.compute_loss(layer_context)
        losses[layer] = loss

    # Find minimum-loss layer
    best_layer = min(losses, key=lambda k: losses[k])
    best_loss = losses[best_layer]
    confidence = 1.0 - best_loss

    # Generate rationale
    rationale = _explain_layer_choice(best_layer, losses)

    return LayerAssignment(
        layer=best_layer,
        loss=best_loss,
        loss_by_layer=losses,
        confidence=confidence,
        insight=f"Content naturally lives at L{best_layer} ({LAYER_NAMES[best_layer]})",
        rationale=rationale,
    )


def _explain_layer_choice(best_layer: int, losses: dict[int, float]) -> str:
    """Explain why a layer was chosen."""
    explanations = {
        1: "Content is a zero-loss fixed point (axiom)",
        2: "Content grounds higher layers with minimal abstraction loss",
        3: "Content expresses intent with moderate abstraction",
        4: "Content specifies implementation with acceptable detail loss",
        5: "Content describes concrete execution",
        6: "Content synthesizes experience with expected reflection loss",
        7: "Content represents meta-structure (high abstraction)",
    }

    loss_summary = ", ".join(f"L{layer}: {loss:.2f}" for layer, loss in sorted(losses.items()))

    return f"{explanations[best_layer]}. Loss by layer: {loss_summary}"


def compute_layer_from_convergence(
    losses_by_iteration: list[float],
    threshold: float = FIXED_POINT_THRESHOLD,
) -> int:
    """
    Derive layer from restructuring convergence depth.

    layer(node) = argmin_n L(R^n(node)) < epsilon

    Args:
        losses_by_iteration: Losses at each R^n iteration
        threshold: Fixed-point threshold (epsilon)

    Returns:
        Layer (1-7) based on convergence depth
    """
    for depth, loss in enumerate(losses_by_iteration):
        if loss < threshold:
            return min(depth + 1, 7)  # L1 = depth 0, etc.
    return 7  # L7 if doesn't converge


# -----------------------------------------------------------------------------
# Contradiction Detection
# -----------------------------------------------------------------------------


@dataclass
class ContradictionAnalysis:
    """
    Analysis of potential contradiction between two nodes.

    From spec Part III: "Contradiction Detection via Super-Additive Loss"
    """

    content_a: str
    content_b: str
    loss_a: float
    loss_b: float
    loss_combined: float
    ghost_alternatives: list[GhostAlternative] = field(default_factory=list)

    @property
    def strength(self) -> float:
        """
        Contradiction strength = super-additive excess.

        > 0: Contradiction (super-additive)
        = 0: Independent (additive)
        < 0: Synergistic (sub-additive)
        """
        return self.loss_combined - (self.loss_a + self.loss_b)

    @property
    def is_contradiction(self) -> bool:
        """Contradiction if strength exceeds tolerance."""
        return self.strength > CONTRADICTION_TOLERANCE

    @property
    def type(self) -> ContradictionType:
        """Classify contradiction by strength."""
        if self.strength > 0.5:
            return ContradictionType.STRONG
        elif self.strength > 0.2:
            return ContradictionType.MODERATE
        elif self.strength > 0.1:
            return ContradictionType.WEAK
        else:
            return ContradictionType.NONE

    @property
    def synthesis_hint(self) -> GhostAlternative | None:
        """Best ghost alternative for synthesis."""
        if not self.ghost_alternatives:
            return None

        # Return ghost with lowest deferral cost
        return min(self.ghost_alternatives, key=lambda g: g.deferral_cost)


async def detect_contradiction(
    content_a: str,
    content_b: str,
    computer: GaloisLossComputer,
) -> ContradictionAnalysis:
    """
    Detect contradiction using super-additive loss.

    contradicts(A, B) iff L(A U B) > L(A) + L(B) + tau

    Args:
        content_a: First content
        content_b: Second content
        computer: Galois loss computer

    Returns:
        ContradictionAnalysis with strength and type
    """
    # Compute individual losses
    loss_a = await computer.compute_loss(content_a)
    loss_b = await computer.compute_loss(content_b)

    # Compute combined loss
    combined = f"{content_a}\n\n---\n\n{content_b}"

    # Get restructuring with ghosts for synthesis hints
    modular = await computer.llm.restructure(combined)
    reconstituted = await computer.llm.reconstitute(modular)
    loss_combined = computer.metric.distance(combined, reconstituted)

    return ContradictionAnalysis(
        content_a=content_a,
        content_b=content_b,
        loss_a=loss_a,
        loss_b=loss_b,
        loss_combined=loss_combined,
        ghost_alternatives=list(modular.ghosts),
    )


def prevents_explosion(
    loss_a: float,
    loss_not_a: float,
    loss_conjunction: float,
) -> bool:
    """
    Check if paraconsistent explosion is prevented.

    From A and not-A, you CAN'T derive anything if:
    L(A) + L(not-A) + L(A ^ not-A) > EXPLOSION_THRESHOLD

    Args:
        loss_a: Loss of A
        loss_not_a: Loss of not-A
        loss_conjunction: Loss of A ^ not-A

    Returns:
        True if explosion is prevented (safe)
    """
    total_loss = loss_a + loss_not_a + loss_conjunction
    return total_loss > EXPLOSION_THRESHOLD


# -----------------------------------------------------------------------------
# Fixed Point (Axiom) Detection
# -----------------------------------------------------------------------------


@dataclass
class FixedPointResult:
    """Result of fixed-point analysis."""

    content: str
    loss: float
    is_fixed_point: bool
    iterations_to_converge: int
    loss_history: list[float]

    @property
    def is_axiom(self) -> bool:
        """Axioms are zero-loss fixed points."""
        return self.is_fixed_point and self.loss < FIXED_POINT_THRESHOLD


async def find_fixed_point(
    content: str,
    computer: GaloisLossComputer,
    max_iterations: int = 7,
) -> FixedPointResult:
    """
    Find if content converges to a fixed point under R o C.

    A fixed point satisfies: L(R^n(content)) < epsilon for some n.

    Args:
        content: Content to analyze
        computer: Galois loss computer
        max_iterations: Maximum iterations to try

    Returns:
        FixedPointResult with convergence info
    """
    current = content
    loss_history: list[float] = []
    iterations = 0

    for i in range(max_iterations):
        # Apply R o C
        modular = await computer.llm.restructure(current)
        reconstituted = await computer.llm.reconstitute(modular)

        # Measure loss
        loss = computer.metric.distance(current, reconstituted)
        loss_history.append(loss)

        # Check convergence
        if loss < FIXED_POINT_THRESHOLD:
            iterations = i + 1
            return FixedPointResult(
                content=content,
                loss=loss,
                is_fixed_point=True,
                iterations_to_converge=iterations,
                loss_history=loss_history,
            )

        # Continue with reconstituted
        current = reconstituted

    # Did not converge
    return FixedPointResult(
        content=content,
        loss=loss_history[-1] if loss_history else 1.0,
        is_fixed_point=False,
        iterations_to_converge=-1,
        loss_history=loss_history,
    )


# -----------------------------------------------------------------------------
# Evidence Tier Classification
# -----------------------------------------------------------------------------


def classify_evidence_tier(loss: float) -> EvidenceTier:
    """
    Map Galois loss to evidence tier.

    Kent calibration (2025-12-28):
    - CATEGORICAL: L < 0.10 (near-lossless, deductive)
    - EMPIRICAL: L < 0.38 (moderate loss, inductive)
    - AESTHETIC: L < 0.45 (taste-based judgment)
    - SOMATIC: L < 0.65 (intuitive, embodied)
    - CHAOTIC: L >= 0.65 (high entropy, unreliable)
    """
    if loss < 0.10:
        return EvidenceTier.CATEGORICAL
    elif loss < 0.38:
        return EvidenceTier.EMPIRICAL
    elif loss < 0.45:
        return EvidenceTier.AESTHETIC
    elif loss < 0.65:
        return EvidenceTier.SOMATIC
    else:
        return EvidenceTier.CHAOTIC


# -----------------------------------------------------------------------------
# Production Async Loss Computation with Fallback
# -----------------------------------------------------------------------------


@dataclass
class GaloisLoss:
    """
    Result of Galois loss computation.

    Contains the loss value and metadata about computation method.
    """

    loss: float
    method: str  # "llm" or "fallback"
    metric_name: str
    cached: bool = False


async def compute_galois_loss_async(
    content: str,
    llm_client: LLMClientProtocol | None = None,
    use_cache: bool = True,
    cache: LossCache | None = None,
) -> GaloisLoss:
    """
    Compute Galois loss with async LLM support and fallback.

    This is the production-ready async loss computation function that:
    1. Uses LLM for restructure (R) and reconstitute (C) operations
    2. Computes semantic distance d(P, C(R(P)))
    3. Falls back to fast metrics (BERTScore, cosine) when LLM unavailable
    4. Uses caching to avoid redundant LLM calls

    The Galois loss formula:
        L(P) = d(P, C(R(P)))
    where:
        - R: Prompt -> ModularPrompt (restructure via LLM)
        - C: ModularPrompt -> Prompt (reconstitute via LLM)
        - d: Prompt x Prompt -> [0,1] (semantic distance)

    Args:
        content: The content to analyze
        llm_client: Optional LLM client (if None, uses SimpleLLMClient or falls back)
        use_cache: Whether to use cached results (default: True)
        cache: Optional cache instance (if None, creates new one)

    Returns:
        GaloisLoss with loss value and computation metadata

    Example:
        >>> from agents.k.llm import create_llm_client
        >>> llm = create_llm_client()
        >>> result = await compute_galois_loss_async(
        ...     "This is test content",
        ...     llm_client=llm,
        ...     use_cache=True,
        ... )
        >>> assert 0.0 <= result.loss <= 1.0
        >>> assert result.method in ("llm", "fallback")
    """
    # Initialize cache if needed
    if cache is None:
        cache = LossCache()

    # Check cache first
    cached_loss = None
    if use_cache:
        cached_loss = cache.get(content, "galois_loss_async")
        if cached_loss is not None:
            # Need to determine metric name from cache
            # For now, return with generic name
            return GaloisLoss(
                loss=cached_loss,
                method="llm",  # Assume cached value was from LLM
                metric_name="cached",
                cached=True,
            )

    # Try LLM-based computation
    try:
        # Use provided client or create one
        if llm_client is None:
            llm_client = SimpleLLMClient()

        # Create computer with LLM
        metric = get_default_metric()
        computer = GaloisLossComputer(
            llm=llm_client,
            metric=metric,
            cache=cache if use_cache else LossCache(),
        )

        # Compute loss via R o C
        loss = await computer.compute_loss(content, use_cache=use_cache)

        # Cache result
        if use_cache:
            cache.set(content, "galois_loss_async", loss, metric.name)

        return GaloisLoss(
            loss=loss,
            method="llm",
            metric_name=metric.name,
            cached=False,
        )

    except Exception as e:
        # Fall back to fast metrics without LLM
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"LLM-based loss computation failed, using fallback: {e}")

        # Try BERTScore first (most accurate fallback)
        try:
            metric = BERTScoreDistance()
            # For fallback, we can't do R o C, so we approximate
            # by comparing content to a simplified version
            simplified = _simplify_content(content)
            loss = metric.distance(content, simplified)

            if use_cache:
                cache.set(content, "galois_loss_async", loss, "bertscore_fallback")

            return GaloisLoss(
                loss=loss,
                method="fallback",
                metric_name="bertscore",
                cached=False,
            )
        except Exception:
            pass

        # Final fallback: cosine embedding
        try:
            from .distance import CosineEmbeddingDistance

            metric = CosineEmbeddingDistance()
            simplified = _simplify_content(content)
            loss = metric.distance(content, simplified)

            if use_cache:
                cache.set(content, "galois_loss_async", loss, "cosine_fallback")

            return GaloisLoss(
                loss=loss,
                method="fallback",
                metric_name="cosine",
                cached=False,
            )
        except Exception:
            # Ultimate fallback: moderate loss estimate
            return GaloisLoss(
                loss=0.5,
                method="fallback",
                metric_name="default",
                cached=False,
            )


def _simplify_content(content: str) -> str:
    """
    Simplify content for fallback loss computation.

    This is a heuristic approximation of restructure-reconstitute
    when no LLM is available.

    Strategy:
    - Extract first and last sentences (compression)
    - This approximates what R o C might produce
    """
    sentences = content.split(". ")
    if len(sentences) <= 2:
        return content

    # Take first and last sentences as compressed representation
    return f"{sentences[0]}. {sentences[-1]}"


# -----------------------------------------------------------------------------
# Bootstrap Fixed Point Verification
# -----------------------------------------------------------------------------


@dataclass
class BootstrapVerification:
    """Result of verifying Zero Seed as a fixed point."""

    spec_loss: float
    is_fixed_point: bool
    regenerability: float
    interpretation: str


async def verify_bootstrap_fixed_point(
    zero_seed_spec: str,
    computer: GaloisLossComputer,
) -> BootstrapVerification:
    """
    Verify Zero Seed is approximately a fixed point.

    From spec Part IX: "Bootstrap Strange Loop as Lawvere Fixed Point"

    The spec should survive its own modularization with minimal loss.
    Target: L < 0.15 (85% regenerability)
    """
    # Apply restructure-reconstitute
    loss = await computer.compute_loss(zero_seed_spec)

    # Check against threshold
    is_fixed_point = loss < 0.15
    regenerability = 1.0 - loss

    # Interpret result
    if loss < 0.1:
        interpretation = "Strong fixed point: spec is highly self-similar"
    elif loss < 0.2:
        interpretation = "Approximate fixed point: spec is mostly self-describing"
    elif loss < 0.3:
        interpretation = "Weak fixed point: spec has significant compression"
    else:
        interpretation = "Not a fixed point: spec loses coherence under restructuring"

    return BootstrapVerification(
        spec_loss=loss,
        is_fixed_point=is_fixed_point,
        regenerability=regenerability,
        interpretation=interpretation,
    )


__all__ = [
    # Constants
    "FIXED_POINT_THRESHOLD",
    "CONTRADICTION_TOLERANCE",
    "EXPLOSION_THRESHOLD",
    "LAYER_LOSS_BOUNDS",
    "LAYER_NAMES",
    # Enums
    "ContradictionType",
    "EvidenceTier",
    # Protocols
    "LLMClientProtocol",
    # Modular representation
    "ModularComponent",
    "GhostAlternative",
    "ModularPrompt",
    # Cache
    "LossCache",
    "LossCacheEntry",
    # LLM client
    "SimpleLLMClient",
    # Core computer
    "GaloisLossComputer",
    # Layer assignment
    "LayerAssignment",
    "assign_layer_via_galois",
    "compute_layer_from_convergence",
    # Contradiction
    "ContradictionAnalysis",
    "detect_contradiction",
    "prevents_explosion",
    # Fixed point
    "FixedPointResult",
    "find_fixed_point",
    # Classification
    "classify_evidence_tier",
    # Production async loss
    "GaloisLoss",
    "compute_galois_loss_async",
    # Bootstrap
    "BootstrapVerification",
    "verify_bootstrap_fixed_point",
]
