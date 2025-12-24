"""
GaloisLoss: Specialized Galois losses for constitutional principles.

The key insight from spec/protocols/zero-seed1/dp.md:
    "Constitutional reward IS inverse Galois loss."

Each of the 7 kgents principles maps to a specific Galois loss computation:
- TASTEFUL: bloat_loss (unnecessary structure that doesn't compress)
- COMPOSABLE: composition_loss (edges that break explicit interfaces)
- GENERATIVE: regeneration_loss (failure to reconstruct from compression)
- ETHICAL: safety_loss (implicit assumptions that hide risks)
- JOY_INDUCING: aesthetic_loss (deviation from personality attractor)
- HETERARCHICAL: rigidity_loss (imposed hierarchy that prevents flux)
- CURATED: arbitrariness_loss (changes without explicit justification)

The Total Loss Equation:
    R_constitutional(s, a, s') = 1.0 - L_galois(s -> s' via a)

Philosophy:
    High Galois loss = significant implicit structure lost in abstraction
    Lost structure = violation of constitutional principles
    Therefore: Low loss <-> High constitutional adherence

Teaching:
    gotcha: GaloisLoss requires an LLM client for semantic operations.
            If no LLM is available, losses default to 0.5 (moderate/unknown).
            (Evidence: All loss methods have try/except with 0.5 fallback)

    gotcha: The metric function determines semantic distance. Default is
            a simple embedding similarity, but can be replaced with more
            sophisticated measures like BERTScore.
            (Evidence: __init__ accepts metric parameter)

See: spec/protocols/zero-seed1/dp.md (Part II: GaloisConstitution Implementation)
See: spec/theory/galois-modularization.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Protocol

if TYPE_CHECKING:
    from services.witness.mark import Proof

logger = logging.getLogger("kgents.zero_seed.dp.galois_loss")


# =============================================================================
# LLM Client Protocol
# =============================================================================


class LLMClientProtocol(Protocol):
    """Protocol for LLM clients used in Galois loss computation."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate text from the LLM."""
        ...


@dataclass(frozen=True)
class LLMResponse:
    """Response from an LLM client."""

    text: str
    usage: dict[str, int] = field(default_factory=dict)


# =============================================================================
# Default Metric: Simple text similarity
# =============================================================================


def default_text_similarity(text_a: str, text_b: str) -> float:
    """
    Simple text similarity metric (0.0 = identical, 1.0 = completely different).

    Uses Jaccard similarity on word sets as a baseline.
    For production, replace with embedding cosine distance or BERTScore.
    """
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if not words_a and not words_b:
        return 0.0
    if not words_a or not words_b:
        return 1.0

    intersection = len(words_a & words_b)
    union = len(words_a | words_b)

    jaccard = intersection / union if union > 0 else 0.0

    # Convert similarity to distance
    return 1.0 - jaccard


# =============================================================================
# Zero Seed Node Type (for type hints)
# =============================================================================


@dataclass
class ZeroNode:
    """
    A node in the Zero Seed hypergraph.

    This is a simplified representation for Galois loss computation.
    The full ZeroNode is defined in the Zero Seed graph module.
    """

    title: str
    content: str
    layer: int  # 1-7 epistemic layers
    kind: str  # node kind (axiom, value, goal, etc.)
    tags: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()  # parent node IDs
    proof: Any | None = None  # Toulmin proof if present
    outgoing_edges: tuple[Any, ...] = ()

    @property
    def id(self) -> str:
        """Generate a simple ID from title."""
        return f"zero-{hash(self.title) % 10000:04d}"


# =============================================================================
# GaloisLoss: The Core Class
# =============================================================================


@dataclass
class GaloisLoss:
    """
    Specialized Galois losses for constitutional principles.

    Each principle maps to a specific loss computation.
    All losses return values in [0.0, 1.0]:
    - 0.0 = perfect (no loss, full structural coherence)
    - 1.0 = complete loss (structure entirely lost)

    The unified constitutional reward is: R = 1.0 - L_galois

    Example:
        >>> from services.llm import create_llm_client
        >>> llm = create_llm_client()
        >>> galois = GaloisLoss(llm)
        >>> loss = await galois.bloat_loss(node)
        >>> reward = 1.0 - loss  # Constitutional reward for TASTEFUL
    """

    llm: LLMClientProtocol | None = None
    metric: Callable[[str, str], float] = default_text_similarity

    # Loss penalty weight (lambda in the spec)
    loss_weight: float = 1.0

    # Numerical stability epsilon
    epsilon: float = 1e-8

    async def compute(self, transition_desc: str) -> float:
        """
        Compute unified Galois loss for a transition description.

        This is the main entry point for loss computation.
        Returns a single loss value summarizing structural coherence.

        Args:
            transition_desc: Text describing the state transition

        Returns:
            Loss value in [0.0, 1.0]
        """
        if not self.llm:
            logger.debug("No LLM client, returning moderate loss")
            return 0.5

        try:
            # Ask LLM to evaluate structural coherence
            response = await self.llm.generate(
                system="""You are evaluating structural coherence of transitions.
Analyze whether the transition preserves important implicit structure.
Reply with ONLY a number between 0.0 (perfect coherence) and 1.0 (no coherence).""",
                user=f"""Evaluate the structural coherence of this transition:

{transition_desc}

What is the Galois loss (0.0 = perfect structure preservation, 1.0 = complete loss)?
Reply with just a number:""",
                temperature=0.1,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Galois loss computation failed: {e}")
            return 0.5

    async def bloat_loss(self, node: ZeroNode) -> float:
        """
        TASTEFUL principle: Measure bloat.

        Bloat = content that doesn't compress (redundant structure).
        Low bloat = content is already at optimal compression.

        Method:
        1. Compress the node content
        2. Reconstruct from compressed version
        3. Loss = semantic distance after round-trip

        High loss -> couldn't compress well -> bloated content.
        """
        if not self.llm:
            return 0.5

        try:
            # Compress the content
            compressed = await self.llm.generate(
                system="Compress this to essential information only. Be extremely concise.",
                user=node.content,
                temperature=0.2,
                max_tokens=len(node.content.split()) // 2 + 10,
            )

            # Reconstruct from compressed
            reconstructed = await self.llm.generate(
                system="Expand this compressed content back to full form.",
                user=compressed.text,
                temperature=0.2,
            )

            # Loss = semantic distance after round-trip
            loss = self.metric(node.content, reconstructed.text)

            logger.debug(
                f"Bloat loss for '{node.title}': {loss:.3f} "
                f"(compressed {len(node.content)} -> {len(compressed.text)} chars)"
            )

            return self._clamp(loss)

        except Exception as e:
            logger.warning(f"Bloat loss failed: {e}")
            return 0.5

    async def composition_loss(self, node: ZeroNode) -> float:
        """
        COMPOSABLE principle: Measure composition violations.

        Composition violations = edges that require hidden state.
        A composable node has explicit interfaces; hidden dependencies
        indicate poor composability.
        """
        if not self.llm:
            return 0.5

        try:
            # Format edges for analysis
            edges_desc = "\n".join(
                f"  - {getattr(e, 'kind', 'edge')} -> {getattr(e, 'target', 'unknown')}"
                for e in node.outgoing_edges
            ) or "  (no outgoing edges)"

            prompt = f"""Analyze this node for composition violations:

Node: {node.title} (Layer {node.layer})
{node.content[:500]}

Edges:
{edges_desc}

Are there hidden dependencies? Rate composability:
- 0.0 = fully composable (all interfaces explicit)
- 1.0 = tightly coupled (many hidden dependencies)

Reply with just a number:"""

            response = await self.llm.generate(
                system="You analyze composability of graph nodes.",
                user=prompt,
                temperature=0.1,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Composition loss failed: {e}")
            return 0.5

    async def regeneration_loss(self, node: ZeroNode) -> float:
        """
        GENERATIVE principle: Measure regeneration failure.

        Regeneration failure = can't derive from lineage.
        A generative node can be regenerated from its parents.
        """
        if not self.llm:
            return 0.5

        if not node.lineage:
            # Axioms have no lineage -> perfect regeneration (they ARE the source)
            return 0.0

        try:
            # We don't have access to parent nodes here,
            # so we ask the LLM to evaluate derivability
            prompt = f"""Analyze whether this node could be derived from its lineage:

Node: {node.title}
Content: {node.content[:300]}
Lineage (parent count): {len(node.lineage)}

Can this content be logically derived from parent nodes?
Rate regeneration ability:
- 0.0 = perfectly derivable from lineage
- 1.0 = not derivable at all

Reply with just a number:"""

            response = await self.llm.generate(
                system="You evaluate logical derivability.",
                user=prompt,
                temperature=0.1,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Regeneration loss failed: {e}")
            return 0.5

    async def safety_loss(self, node: ZeroNode, action: str = "") -> float:
        """
        ETHICAL principle: Measure hidden safety risks.

        Safety risks = implicit assumptions that could cause harm.
        This is the highest-weighted principle (safety first).
        """
        if not self.llm:
            # Fail-safe: when we can't evaluate, assume moderate risk
            return 0.5

        try:
            prompt = f"""Analyze this operation for hidden safety risks:

Node: {node.title}
Action: {action or 'examine'}
Content: {node.content[:400]}
Layer: {node.layer}

Hidden safety risks (implicit assumptions, unexamined side effects):
- 0.0 = completely safe (all risks explicit)
- 1.0 = dangerous (hidden assumptions that could cause harm)

Reply with just a number:"""

            response = await self.llm.generate(
                system="You identify implicit assumptions that could cause harm.",
                user=prompt,
                temperature=0.1,
                max_tokens=10,
            )

            loss = self._parse_loss(response.text)

            # Safety has high weight, so we're conservative
            # Unknown safety -> higher default loss
            if response.text.strip() == "":
                loss = 0.7

            return loss

        except Exception as e:
            logger.warning(f"Safety loss failed: {e}")
            return 0.7  # Fail-safe: assume higher risk

    async def aesthetic_loss(self, node: ZeroNode) -> float:
        """
        JOY_INDUCING principle: Measure aesthetic coherence.

        Aesthetic coherence = alignment with personality attractor.
        Kent's kgents personality has specific eigenvectors.
        """
        if not self.llm:
            return 0.5

        try:
            # Personality eigenvectors (from DP-Native spec)
            personality = """
Personality eigenvectors for kgents:
- warmth: 0.7 (warm, not distant)
- playfulness: 0.6 (playful, not entirely serious)
- formality: 0.3 (casual, not formal)
- challenge: 0.5 (balanced support/challenge)
- depth: 0.8 (philosophical, not surface)

"Daring, bold, creative, opinionated but not gaudy"
"""

            prompt = f"""Rate aesthetic alignment with this personality:

{personality}

Content to evaluate:
{node.content[:400]}

Alignment score:
- 0.0 = perfect aesthetic match
- 1.0 = completely off (wrong voice)

Reply with just a number:"""

            response = await self.llm.generate(
                system="You rate aesthetic coherence with a defined personality.",
                user=prompt,
                temperature=0.2,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Aesthetic loss failed: {e}")
            return 0.5

    async def rigidity_loss(self, node: ZeroNode) -> float:
        """
        HETERARCHICAL principle: Measure imposed rigidity.

        Rigidity = fixed hierarchy that prevents flux.
        Heterarchical structures allow dynamic reorganization.
        """
        if not self.llm:
            return 0.5

        try:
            prompt = f"""Analyze for rigid hierarchy:

Node: {node.title}
Layer: {node.layer}
Content: {node.content[:400]}

Does this impose rigid top-down structure?
- 0.0 = fluid, allows reorganization
- 1.0 = rigid, enforces fixed hierarchy

Reply with just a number:"""

            response = await self.llm.generate(
                system="You analyze organizational structure.",
                user=prompt,
                temperature=0.1,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Rigidity loss failed: {e}")
            return 0.5

    async def arbitrariness_loss(self, node: ZeroNode) -> float:
        """
        CURATED principle: Measure arbitrary changes.

        Arbitrariness = changes without explicit justification.
        A curated node has clear reasoning for its existence.
        """
        # No proof -> high arbitrariness
        if node.proof is None:
            logger.debug(f"Node '{node.title}' has no proof -> high arbitrariness")
            return 0.8

        if not self.llm:
            # Has proof, no LLM -> assume moderate quality
            return 0.4

        try:
            # Evaluate proof quality
            quality = await self.evaluate_proof_quality(node.proof)

            # Loss = inverse quality
            return self._clamp(1.0 - quality)

        except Exception as e:
            logger.warning(f"Arbitrariness loss failed: {e}")
            return 0.5

    async def evaluate_proof_quality(self, proof: Any) -> float:
        """
        Helper: Evaluate Toulmin proof quality.

        Returns quality score in [0.0, 1.0] where 1.0 is excellent.
        """
        if not self.llm:
            return 0.5

        try:
            # Extract proof components (handle both dict and object forms)
            if isinstance(proof, dict):
                data = proof.get("data", "")
                warrant = proof.get("warrant", "")
                claim = proof.get("claim", "")
                backing = proof.get("backing", "")
            else:
                data = getattr(proof, "data", "")
                warrant = getattr(proof, "warrant", "")
                claim = getattr(proof, "claim", "")
                backing = getattr(proof, "backing", "")

            prompt = f"""Rate proof quality (0.0-1.0):

Data: {data}
Warrant: {warrant}
Claim: {claim}
Backing: {backing}

A high-quality proof has:
- Clear evidence (data)
- Sound reasoning (warrant)
- Justified conclusion (claim)
- Supporting context (backing)

Quality score (0.0 = poor, 1.0 = excellent):"""

            response = await self.llm.generate(
                system="You evaluate argument quality using Toulmin schema.",
                user=prompt,
                temperature=0.1,
                max_tokens=10,
            )

            return self._parse_loss(response.text)

        except Exception as e:
            logger.warning(f"Proof quality evaluation failed: {e}")
            return 0.5

    def _parse_loss(self, text: str) -> float:
        """Parse loss value from LLM response text."""
        try:
            # Extract first number from text
            import re
            match = re.search(r"[\d.]+", text.strip())
            if match:
                value = float(match.group())
                return self._clamp(value)
            return 0.5
        except ValueError:
            return 0.5

    def _clamp(self, value: float) -> float:
        """Clamp value to [0.0, 1.0] with numerical stability."""
        return max(self.epsilon, min(1.0 - self.epsilon, value))


# =============================================================================
# Convenience Functions
# =============================================================================


async def compute_transition_loss(
    galois: GaloisLoss,
    source: ZeroNode,
    action: str,
    target: ZeroNode,
) -> float:
    """
    Compute Galois loss for a state transition.

    This constructs the transition description and computes unified loss.
    """
    transition_desc = f"""
Layer: {source.layer} -> {target.layer}
Kind: {source.kind} -> {target.kind}
Action: {action}

From: "{source.title}"
{source.content[:300]}

To: "{target.title}"
{target.content[:300]}

Lineage: {len(source.lineage)} -> {len(target.lineage)} ancestors
Tags: {source.tags} -> {target.tags}
"""
    return await galois.compute(transition_desc)


async def compute_principle_losses(
    galois: GaloisLoss,
    node: ZeroNode,
    action: str = "",
) -> dict[str, float]:
    """
    Compute losses for all 7 constitutional principles.

    Returns a dictionary mapping principle names to loss values.
    """
    return {
        "TASTEFUL": await galois.bloat_loss(node),
        "COMPOSABLE": await galois.composition_loss(node),
        "GENERATIVE": await galois.regeneration_loss(node),
        "ETHICAL": await galois.safety_loss(node, action),
        "JOY_INDUCING": await galois.aesthetic_loss(node),
        "HETERARCHICAL": await galois.rigidity_loss(node),
        "CURATED": await galois.arbitrariness_loss(node),
    }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core class
    "GaloisLoss",
    # Types
    "ZeroNode",
    "LLMClientProtocol",
    "LLMResponse",
    # Functions
    "compute_transition_loss",
    "compute_principle_losses",
    "default_text_similarity",
]
